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
    "service": {
        "kind": "service",
        "puid_pgid": True,
        "dependabot_automerge": "minor",
        "extra_ports": [3128],
    },
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
    "none": {"language": "none", "license": "MIT"},
    "ts-service": {
        "language": "typescript",
        "kind": "service",
        "puid_pgid": True,
        "extra_ports": [3128],
    },
    "ts-cli": {"language": "typescript", "kind": "cli", "license": "MIT", "node_version": "26"},
    "ts-library": {"language": "typescript", "kind": "library", "license": "Proprietary"},
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
        if {".git", ".venv", "node_modules"} & set(path.parts) or not path.is_file():
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


def test_template_problems_are_reported(project: Path) -> None:
    """A project that finds a template bug reports it, not only works around it (#23)."""
    agents = (project / "AGENTS.md").read_text()
    assert "gh issue list -R metalayerlab/project-template --state all" in agents
    assert "Template problem found?" in (project / ".github/pull_request_template.md").read_text()


def test_extra_ports(project: Path) -> None:
    """Each extra port is exposed and published; none means no trace of them (0005)."""
    extra = VARIANTS[project.name.removeprefix("demo-")].get("extra_ports", [])
    files = {
        "Dockerfile": [f"EXPOSE {' '.join(map(str, [8080, *extra]))}\n"],
        "contrib/docker/compose.yml": [f'"127.0.0.1:{p}:{p}"' for p in extra],
        "contrib/k8s/deployment.yaml": [f"{{name: tcp-{p}, containerPort: {p}}}" for p in extra],
        "contrib/k8s/service.yaml": [f"targetPort: tcp-{p}}}" for p in extra],
        "contrib/k8s/networkpolicy.yaml": [f"#     - {{port: {p}, protocol: TCP}}" for p in extra],
    }
    if "service" not in project.name:
        pytest.skip("no listener")
    for name, expected in files.items():
        if (path := project / name).exists():
            text = path.read_text()
            assert all(e in text for e in expected), name
            assert extra or ("tcp-" not in text and "extra_ports" not in text), name


@pytest.mark.parametrize("bad", [[0], [70000], [8080], [3128, 3128], [True], "3128"])
def test_extra_ports_rejected(bad: object, tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "extra_ports": bad}
    with pytest.raises(ValueError, match="extra_ports"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


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
    if not (project / "pyproject.toml").exists():
        pytest.skip("not a Python project")
    for cmd in (
        ["uv", "lock", "--check"],
        ["uv", "run", "ruff", "check"],
        ["uv", "run", "ruff", "format", "--check"],
        ["uv", "run", "mypy"],
        ["uv", "run", "pytest", "-q", "-p", "no:warnings"],
        ["uv", "run", "scripts/gen-wiki.py", "--check"],
    ):
        sh(*cmd, cwd=project)


def test_typescript_checks(project: Path) -> None:
    """The layer's Definition of done, plus CI's lock check and smoke test (0009)."""
    if not (project / "package.json").exists():
        pytest.skip("not a TypeScript project")
    for cmd in (
        ["npm", "ci", "--no-audit", "--no-fund"],
        ["npm", "run", "lint"],
        ["npm", "run", "format:check"],
        ["npm", "run", "typecheck"],
        ["npm", "test"],
        ["npm", "run", "test:integration"],
        ["node", "scripts/gen-wiki.ts", "--check"],
        ["node", "--input-type=module", "-e", f'import {{ VERSION }} from "{project.name}";'],
    ):
        sh(*cmd, cwd=project)
    if (project / "src/cli.ts").exists():
        sh("node", "dist/cli.js", "--help", cwd=project)
        assert sh("npm", "start", "--silent", "--", "version", cwd=project).strip() == "0.0.0"


def test_none_checks(project: Path) -> None:
    """No layer: the project's checks are its own scripts/check.sh, and version.txt (0008)."""
    if not (project / "scripts/check.sh").exists():
        pytest.skip("has a language layer")
    assert quiet(["sh", "scripts/check.sh"], project) == ["scripts/check.sh: no checks defined yet"]
    assert (project / "version.txt").read_text() == "0.0.0\n"
    assert not (project / "pyproject.toml").exists() and not (project / "src").exists()
    agents = (project / "AGENTS.md").read_text()
    assert "sh scripts/check.sh" in agents and "``" not in agents.replace("```", "")


def test_kind_other_needs_language_none(tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "kind": "other"}
    with pytest.raises(ValueError, match="language: none"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


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


SUBGROUP_TS = """
import {{ cli }} from "{root}/scripts/gen-wiki.ts";
import {{ program }} from "{root}/src/cli.ts";

const root = program();
root
  .command("grp")
  .description("Manage things.")
  .command("show")
  .description("Show a thing.")
  .argument("<name>", "The thing to show.")
  .option("--force", "Show it anyway.");
console.log(cli(root));
"""


def test_gen_wiki_documents_subcommands(project: Path, tmp_path: Path) -> None:
    """A sub-app's commands, and their positional arguments, reach CLI-Reference (#17)."""
    pkg = project.name.replace("-", "_")
    if (project / "src" / pkg / "cli.py").exists():
        script = tmp_path / "subgroup.py"
        script.write_text(SUBGROUP.format(pkg=pkg))
        out = sh("uv", "run", "python", str(script), cwd=project)
    elif (project / "src/cli.ts").exists():
        script = tmp_path / "subgroup.ts"
        script.write_text(SUBGROUP_TS.format(root=project))
        out = sh("node", str(script), cwd=project)
    else:
        pytest.skip("no CLI")
    assert f"### `{project.name} grp show`" in out
    assert "`NAME`" in out and "The thing to show." in out
    assert "`--force`" in out and "Show it anyway." in out


def test_no_double_blank_lines_in_markdown(project: Path) -> None:
    """markdownlint's MD012 fails a project's first PR (Wiki standard) on these."""
    pages = [project / "AGENTS.md", *sorted((project / "docs/wiki").glob("*.md"))]
    doubled = [p.name for p in pages if "\n\n\n" in p.read_text(encoding="utf-8")]
    assert not doubled


def test_readme_links_existing_wiki_pages(project: Path) -> None:
    """The README links the wiki by URL, which check-wiki.py doesn't follow."""
    pages = re.findall(r"/wiki/([\w-]+)\)", (project / "README.md").read_text())
    missing = [p for p in pages if not (project / "docs/wiki" / f"{p}.md").exists()]
    assert pages and not missing


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


FAKE_GH = """#!/bin/sh
# Stands in for the GitHub CLI: answers `gh api repos/{owner}/{repo}`, records everything else.
echo "$*" >> "$GH_LOG"
[ "$1 $2" = "api repos/{owner}/{repo}" ] && cat "$GH_REPO" || cat > /dev/null
"""


def test_repository_metadata(project: Path, tmp_path: Path) -> None:
    """The About box: seeded from the answers, applied by gh, drift reported (0010)."""
    import json
    import tomllib

    want = tomllib.loads((project / ".github/repository.toml").read_text())
    variant = VARIANTS[project.name.removeprefix("demo-")]
    topics = [variant.get("language", "python"), variant["kind"]] if "kind" in variant else []
    assert want == {"description": f"A demo {project.name.removeprefix('demo-')}",
                    "homepage": f"https://github.com/metalayerlab/{project.name}/wiki", "topics": topics}  # fmt: skip

    (tmp_path / "gh").write_text(FAKE_GH)
    (tmp_path / "gh").chmod(0o755)
    env = {"PATH": f"{tmp_path}:{os.environ['PATH']}", "GH_LOG": str(tmp_path / "log"),
           "GH_REPO": str(tmp_path / "repo.json")}  # fmt: skip
    script = ["python3", "scripts/repo-metadata.py"]
    (tmp_path / "repo.json").write_text(json.dumps({**want, "topics": [*topics, "stray"]}))
    drift = subprocess.run([*script, "--check"], cwd=project, env={**os.environ, **env},
                           capture_output=True, text=True)  # fmt: skip
    assert drift.returncode == 1 and "applying removes them): stray" in drift.stdout
    (tmp_path / "repo.json").write_text(json.dumps(want))
    assert sh(*script, "--check", cwd=project, env=env) == ""
    sh(*script, cwd=project, env=env)
    assert "repo edit --enable-wiki" in (tmp_path / "log").read_text()


def quiet(cmd: list[str], cwd: Path) -> list[str]:
    """A passing check's output lines, outside GitHub Actions (whose annotations are CI-only)."""
    env = {**os.environ, "GITHUB_ACTIONS": ""}
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stdout + result.stderr
    return (result.stdout + result.stderr).splitlines()


def test_checks_are_quiet_when_they_pass(project: Path) -> None:
    """Every Definition of done run is read by an assistant: one line on a pass (0007)."""
    checks = [["python3", "scripts/check-wiki.py"]]
    if (project / "scripts/check-manifests.sh").exists():
        checks.append(["scripts/check-manifests.sh"])
    noisy = {" ".join(c): lines for c in checks if len(lines := quiet(c, project)) > 1}
    assert not noisy


def test_docs_secrets_without_docker(project: Path, tmp_path: Path) -> None:
    """Optional locally, never skipped in CI (0004)."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for tool in ("bash", "dirname"):
        (bin_dir / tool).symlink_to(shutil.which(tool) or tool)
    script = str(project / "scripts/check-docs-secrets.sh")
    for ci, code in (("", 0), ("true", 1)):
        env = {"PATH": str(bin_dir), "CI": ci}
        result = subprocess.run([script], cwd=project, capture_output=True, text=True, env=env)
        assert result.returncode == code, result.stdout + result.stderr


def test_gitleaks_pins_match(project: Path) -> None:
    """pre-commit scans staged changes with the same gitleaks as CI's script."""
    script = (project / "scripts/check-docs-secrets.sh").read_text()
    hook = (project / ".pre-commit-config.yaml").read_text()
    tag = re.search(r"gitleaks/gitleaks:(v[\d.]+)", script)
    rev = re.search(r"gitleaks/gitleaks\n\s+rev: (v[\d.]+)", hook)
    assert tag and rev and tag.group(1) == rev.group(1)


@pytest.mark.docker
def test_docs_secrets_match_ci(project: Path, tmp_path: Path) -> None:
    """The skeleton passes in one line (0007), and an MD014 `$` prompt fails locally as in CI (#21)."""
    assert len(quiet(["scripts/check-docs-secrets.sh"], project)) == 1
    copy = tmp_path / project.name
    shutil.copytree(project, copy, ignore=shutil.ignore_patterns(".venv", "node_modules"))
    page = copy / "docs/wiki/Home.md"
    page.write_text(page.read_text() + "\n```sh\n$ demo --help\n```\n")
    result = subprocess.run(
        ["scripts/check-docs-secrets.sh", "docs"], cwd=copy, capture_output=True, text=True
    )
    assert result.returncode == 1 and "MD014" in result.stdout + result.stderr


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
    extra = VARIANTS[project.name.removeprefix("demo-")].get("extra_ports", [])
    exposed = sh("docker", "inspect", "-f", "{{json .Config.ExposedPorts}}", tag, cwd=project)
    assert all(f'"{p}/tcp"' in exposed for p in extra), exposed
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
    shutil.copytree(project, copy, ignore=shutil.ignore_patterns(".venv", "node_modules"))
    python = copy / "src" / project.name.replace("-", "_") / "config.py"
    config, default = (
        (python, '"listen.host", "0.0.0.0"')
        if python.exists()
        else (copy / "src/config.ts", 'key: "listen.host", default: "0.0.0.0"')
    )
    text = config.read_text()
    assert default in text
    config.write_text(text.replace(default, default.replace("0.0.0.0", "127.0.0.1")))
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
