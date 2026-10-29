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
    "service": {"kind": "service", "puid_pgid": True, "dependabot_automerge": "minor"},
    "service-min": {
        "kind": "service",
        "contrib": ["k8s"],
        "puid_pgid": False,
        "multi_arch": False,
        "python_version": "3.14",
        "personal_data_guard": True,
        "license": "Proprietary",
    },
    "cli": {"kind": "cli", "license": "MIT", "dependabot_automerge": "patch"},
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
    # vcs_ref="HEAD": render this checkout, uncommitted changes included. Without it Copier
    # renders the latest tag, and the tests would check the last release, not the change.
    run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD")
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


def test_dependabot_automerge_is_opt_in(project: Path) -> None:
    level = VARIANTS[project.name.removeprefix("demo-")].get("dependabot_automerge", "off")
    wf = project / ".github/workflows/dependabot-automerge.yml"
    assert wf.exists() == (level != "off")
    if level != "off":
        text = wf.read_text()
        assert "semver-patch" in text
        assert ("semver-minor" in text) == (level == "minor")
        assert "semver-major" not in text


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


SUBGROUP = '''
import importlib.util
from typing import Annotated

import typer

from {pkg}.cli import app

grp = typer.Typer(help="Manage things.")


@grp.command()
def show(
    name: Annotated[str, typer.Argument(help="The thing to show.")],
    force: Annotated[bool, typer.Option("--force", help="Show it anyway.")] = False,
) -> None:
    """Show a thing."""


app.add_typer(grp, name="grp")
spec = importlib.util.spec_from_file_location("gen_wiki", "scripts/gen-wiki.py")
gen_wiki = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen_wiki)
print(gen_wiki.cli())
'''


def test_gen_wiki_documents_subcommands(project: Path, tmp_path: Path) -> None:
    """A sub-app's commands, and their positional arguments, reach CLI-Reference (#17)."""
    pkg = project.name.replace("-", "_")
    if not (project / "src" / pkg / "cli.py").exists():
        pytest.skip("no CLI")
    script = tmp_path / "subgroup.py"
    script.write_text(SUBGROUP.format(pkg=pkg))
    out = sh("uv", "run", "python", str(script), cwd=project)
    assert f"### `{project.name} grp show`" in out
    assert "`NAME`" in out and "The thing to show." in out
    assert "`--force`" in out and "Show it anyway." in out


def test_no_double_blank_lines_in_markdown(project: Path) -> None:
    """markdownlint's MD012 fails a project's first PR (Wiki standard) on these."""
    pages = [project / "AGENTS.md", *sorted((project / "docs/wiki").glob("*.md"))]
    doubled = [p.name for p in pages if "\n\n\n" in p.read_text(encoding="utf-8")]
    assert not doubled


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
    _probe_healthz(project, tag)


@pytest.mark.docker
def test_image_serves_when_app_binds_loopback(project: Path, tmp_path: Path) -> None:
    """A safe 127.0.0.1 default in the app must not break the image (#17): inside a
    container, the published ports decide exposure."""
    if "service" not in project.name:
        pytest.skip("no HTTP listener")
    copy = tmp_path / project.name
    shutil.copytree(project, copy, ignore=shutil.ignore_patterns(".venv"))
    config = copy / "src" / project.name.replace("-", "_") / "config.py"
    text = config.read_text()
    assert '"listen.host", "0.0.0.0"' in text
    config.write_text(text.replace('"listen.host", "0.0.0.0"', '"listen.host", "127.0.0.1"'))
    tag = f"{project.name}:loopback"
    sh("docker", "build", "-q", "-t", tag, ".", cwd=copy)
    _probe_healthz(copy, tag)


def _probe_healthz(project: Path, tag: str) -> None:
    """Run the image as docker-build.yml's smoke test does and wait for /healthz."""
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
