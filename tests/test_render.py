"""Render the template with representative answers and run each result's own checks.

    uv run pytest                    # every variant: lint, types, tests, wiki, manifests
    uv run pytest -m docker          # also build each image and probe its health endpoint
    uv run pytest -k service         # one variant

Each variant is a project as `copier copy` would create it, and must pass its own
Definition of done (AGENTS.md) unchanged. That is the template's contract.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest

# Rendered projects must pick their own interpreter and venv, as a fresh checkout would.
# CI's setup-uv exports UV_PYTHON (the template's own Python), and `uv run pytest` sets
# VIRTUAL_ENV: both would leak into every project's `uv lock` / `uv run`. Before importing
# copier: it runs tasks through plumbum, which snapshots the environment at import time.
for _var in ("UV_PYTHON", "VIRTUAL_ENV", "UV_PROJECT_ENVIRONMENT"):
    os.environ.pop(_var, None)

from copier import run_copy  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

VARIANTS: dict[str, dict[str, object]] = {
    "service": {"kind": "service", "puid_pgid": True},
    "service-min": {
        "kind": "service",
        "contrib": ["k8s"],
        "puid_pgid": False,
        "multi_arch": False,
        "python_version": "3.14",
        "personal_data_guard": True,
        "license": "Proprietary",
    },
    "cli": {"kind": "cli", "license": "MIT"},
    "library": {"kind": "library", "license": "Apache-2.0"},
}


def sh(*cmd: str, cwd: Path, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, env={**os.environ, **(env or {})}
    )
    assert result.returncode == 0, f"{' '.join(cmd)} failed:\n{result.stdout}\n{result.stderr}"
    return result.stdout


@pytest.fixture(scope="session", params=sorted(VARIANTS))
def project(request: pytest.FixtureRequest, tmp_path_factory: pytest.TempPathFactory) -> Path:
    name = f"demo-{request.param}"
    dst = tmp_path_factory.mktemp("render") / name
    data = {"project_name": name, "description": f"A demo {request.param}", **VARIANTS[request.param]}
    run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True)
    sh("git", "add", "-A", cwd=dst)
    return dst


def test_no_unrendered_jinja(project: Path) -> None:
    leftovers = []
    for path in project.rglob("*"):
        if ".git" in path.parts or ".venv" in path.parts or not path.is_file():
            continue
        if re.search(r"\[\[|\[%|\.jinja$", path.name):
            leftovers.append(str(path))
        elif path.suffix not in {".lock", ".pyc"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"\[\[ |\[% ", text):
                leftovers.append(str(path))
    assert not leftovers


HEADROOM = 0.75  # the skeleton may use at most 75% of each budget, leaving room for the project


def test_always_loaded_files_leave_headroom(project: Path) -> None:
    """The budget itself is in the rendered docs/wiki/.standard.toml, enforced by check-wiki.py."""
    import tomllib

    budget = tomllib.loads((project / "docs/wiki/.standard.toml").read_text())["context_budget"]
    over = {
        name: (size, int(limit * HEADROOM))
        for name, limit in budget.items()
        if (size := len((project / name).read_text(encoding="utf-8"))) > limit * HEADROOM
    }
    assert not over, f"skeleton uses too much of the context budget (chars, allowed): {over}"


def test_first_release_is_0_1_0(project: Path) -> None:
    """With the manifest at 0.0.0, release-please would otherwise propose 1.0.0."""
    import json

    config = json.loads((project / "release-please-config.json").read_text())
    assert config["packages"]["."]["initial-version"] == "0.1.0"


def test_python_checks(project: Path) -> None:
    for cmd in (
        ["uv", "lock", "--check"],
        ["uv", "run", "ruff", "check"],
        ["uv", "run", "ruff", "format", "--check"],
        ["uv", "run", "mypy"],
        ["uv", "run", "pytest", "-q", "-p", "no:warnings"],
        ["uv", "run", "scripts/gen-wiki.py", "--check"],
    ):
        sh(*cmd, cwd=project)


def test_wiki_standard(project: Path) -> None:
    sh("python3", "scripts/check-wiki.py", cwd=project)


def test_fresh_wiki_blocks_a_release(project: Path) -> None:
    """Skeleton guidance must fail strict mode (Release PRs) until it is written."""
    result = subprocess.run(
        ["python3", "scripts/check-wiki.py", "--strict"], cwd=project, capture_output=True
    )
    assert result.returncode == 1


def test_written_wiki_passes_strict(project: Path, tmp_path: Path) -> None:
    copy = tmp_path / "p"
    shutil.copytree(project / "docs", copy / "docs")
    shutil.copytree(project / "scripts", copy / "scripts")
    for page in (copy / "docs/wiki").glob("*.md"):
        text = page.read_text(encoding="utf-8")
        page.write_text(re.sub(r"<!-- guidance:.*?-->\n?", "", text, flags=re.S), encoding="utf-8")
    sh("python3", "scripts/check-wiki.py", "--strict", cwd=copy)


def test_manifests(project: Path) -> None:
    script = project / "scripts/check-manifests.sh"
    if script.exists():
        sh(str(script), cwd=project)


def test_workflows_lint(project: Path) -> None:
    if not shutil.which("actionlint") and not shutil.which("docker"):
        pytest.skip("neither actionlint nor docker available")
    if shutil.which("actionlint"):
        sh("actionlint", cwd=project)
    else:
        sh("docker", "run", "--rm", "-v", f"{project}:/repo", "-w", "/repo",
           "rhysd/actionlint:1.7.12", cwd=project)  # fmt: skip


@pytest.mark.docker
def test_image_runs(project: Path) -> None:
    if not (project / "Dockerfile").exists():
        pytest.skip("no container image")
    tag = f"{project.name}:test"
    sh("docker", "build", "-q", "-t", tag, ".", cwd=project)
    if "service" not in project.name:
        sh("docker", "run", "--rm", tag, "version", cwd=project)
        return
    name = f"{project.name}-test"
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    sh("docker", "run", "-d", "--name", name, "-p", "127.0.0.1::8080", tag, cwd=project)
    try:
        port = sh("docker", "port", name, "8080", cwd=project).split(":")[-1].strip()
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2) as r:
                    assert r.status == 200
                    return
            except OSError:
                time.sleep(1)
        pytest.fail(sh("docker", "logs", name, cwd=project))
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
