"""Render the template with representative answers and run each result's own checks.

    uv run pytest                    # every variant: lint, types, tests, wiki, manifests
    uv run pytest -m docker          # also build each image and probe its health endpoint
    uv run pytest -k service         # one variant

Each variant is a project as `copier copy` would create it, and must pass its own
Definition of done (AGENTS.md) unchanged. That is the template's contract.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
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

import yaml  # noqa: E402  (Copier's own dependency)
from copier import run_copy  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

VARIANTS: dict[str, dict[str, object]] = {
    "service": {
        "kind": "service",
        # Long, quoted and with a backslash: it lands in Python strings and docstrings (#52).
        "description": 'A demo service: a long, "quoted" description with a back\\slash and a'
        " well-known hyphenated-word, long enough to wrap in every generated file that holds it",
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
    "obsidian": {"language": "obsidian", "brain_pull": True},
    "ts-service": {
        "language": "typescript",
        "kind": "service",
        "puid_pgid": True,
        "extra_ports": [3128],
    },
    "ts-cli": {"language": "typescript", "kind": "cli", "license": "MIT", "node_version": "26"},
    "ts-library": {"language": "typescript", "kind": "library", "license": "Proprietary"},
    "ts-web": {"language": "typescript", "kind": "web", "dependabot_automerge": "patch"},
}


def brain(project: Path) -> bool:
    """A notes repository, an Obsidian vault: no releases, wiki or image (0015, 0016)."""
    return project.name.endswith("-obsidian")


def wiki_only(project: Path) -> None:
    if brain(project):
        pytest.skip("a brain's vault is its wiki")


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
    """The budget is in the rendered docs/wiki/.standard.toml, enforced by check-wiki.py, or in
    scripts/check-vault.py for a brain (0016)."""
    budget = context_budget(project)
    over = {
        name: (size, int(limit * HEADROOM))
        for name, limit in budget.items()
        if (size := len((project / name).read_text(encoding="utf-8"))) > limit * HEADROOM
    }
    assert not over, f"skeleton uses too much of the context budget (chars, allowed): {over}"


def context_budget(project: Path) -> dict[str, int]:
    import importlib.util
    import tomllib

    if not brain(project):
        return tomllib.loads((project / "docs/wiki/.standard.toml").read_text())["context_budget"]
    script = project / "scripts/check-vault.py"
    spec = importlib.util.spec_from_file_location("check_vault", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.BUDGET  # type: ignore[no-any-return]


def test_budget_is_the_same_without_a_wiki(project: Path) -> None:
    """A brain's vault check and every wiki's standard agree on the budget (0016)."""
    import ast
    import tomllib

    if brain(project):
        pytest.skip("compared from the projects with a wiki")
    standard = tomllib.loads((project / "docs/wiki/.standard.toml").read_text())["context_budget"]
    name = "[% if language == 'obsidian' %]check-vault.py[% endif %].jinja"
    script = ROOT / "template/scripts" / name
    budget = re.search(r"BUDGET = (\{.*?\})", script.read_text(), re.S)
    assert budget and ast.literal_eval(budget.group(1)) == standard


def test_template_problems_are_reported(project: Path) -> None:
    """A project that finds a template bug reports it, not only works around it (#23, 0013)."""
    agents = (project / "AGENTS.md").read_text()
    assert "goes to `metalayerlab/project-template`" in agents
    assert "gh issue list -R <owner/repo> --state all" in agents
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


@pytest.mark.parametrize(
    ("extras", "flags"),
    [([], ""), (["fuse", "gpu"], " --extra fuse --extra gpu"), (["*"], " --all-extras")],
)
def test_image_extras(extras: list[str], flags: str, tmp_path: Path) -> None:
    """`image_extras` (#63) reaches both of the builder's `uv sync` lines; none adds nothing."""
    data = {"project_name": "demo", "description": "demo", "kind": "cli", "image_extras": extras}
    run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
             vcs_ref="HEAD", skip_tasks=True)  # fmt: skip
    syncs = [ln for ln in (tmp_path / "p/Dockerfile").read_text().splitlines() if "uv sync" in ln]
    assert syncs == [
        f"RUN uv sync --frozen --no-dev --no-install-project{flags}",
        f"RUN uv sync --frozen --no-dev --no-editable{flags}",
    ]
    assert ("image_extras" in (tmp_path / "p/Dockerfile").read_text()) == bool(extras)


@pytest.mark.parametrize(
    "bad", ["fuse", [1], [""], ["*", "fuse"], ["a b"], ["fuse;rm"], ["-x"], ["fuse", "fuse"]]
)
def test_image_extras_rejected(bad: object, tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "kind": "cli", "image_extras": bad}
    with pytest.raises(ValueError, match="image_extras"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


def test_first_release_is_0_1_0(project: Path) -> None:
    """With the manifest at 0.0.0, release-please would otherwise propose 1.0.0."""
    import json

    if brain(project):
        pytest.skip("a brain has no releases")
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
    ):
        sh(*cmd, cwd=project)
    if (project / "vite.config.ts").exists():
        sh("npm", "run", "build", cwd=project)
        assert '<div id="root">' in (project / "dist/index.html").read_text()
        assert "[]" not in (project / "docs/wiki/In-Depth-Configuration.md").read_text()
        return
    sh("node", "--input-type=module", "-e", f'import {{ VERSION }} from "{project.name}";', cwd=project)
    if (project / "src/cli.ts").exists():
        sh("node", "dist/cli.js", "--help", cwd=project)
        assert sh("npm", "start", "--silent", "--", "version", cwd=project).strip() == "0.0.0"


def test_none_checks(project: Path) -> None:
    """No layer: the project's checks are its own scripts/check.sh, and version.txt (0008)."""
    if not (project / "scripts/check.sh").exists():
        pytest.skip("has a language layer")
    assert quiet(["sh", "scripts/check.sh"], project) == ["scripts/check.sh: no checks defined yet"]
    assert brain(project) or (project / "version.txt").read_text() == "0.0.0\n"
    assert not (project / "pyproject.toml").exists() and not (project / "src").exists()
    agents = (project / "AGENTS.md").read_text()
    assert "sh scripts/check.sh" in agents and "``" not in agents.replace("```", "")


@pytest.mark.parametrize("language", ["python", "none"])
def test_kind_web_needs_typescript(language: str, tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "language": language, "kind": "web"}
    with pytest.raises(ValueError, match="language: typescript"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


def test_systemd_is_service_only(tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "language": "typescript",
            "kind": "web", "contrib": ["systemd"]}  # fmt: skip
    with pytest.raises(ValueError, match="kind: service"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


def test_kind_other_needs_language_none(tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "kind": "other"}
    with pytest.raises(ValueError, match="language: none"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


@pytest.mark.parametrize(("kind", "error"), [("knowledge", "Invalid choice"), ("brain", "language: obsidian")])
def test_language_none_offers_other_only(kind: str, error: str, tmp_path: Path) -> None:
    """A notes repository is `language: obsidian`, whose kind is always `brain` (0016)."""
    data = {"project_name": "demo", "description": "demo", "language": "none", "kind": kind}
    with pytest.raises(ValueError, match=error):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip
    data = {"project_name": "demo", "description": "demo", "language": "obsidian"}
    run_copy(str(ROOT), tmp_path / "o", data=data, defaults=True, unsafe=True, quiet=True,
             vcs_ref="HEAD", skip_tasks=True)  # fmt: skip
    assert 'topics = ["obsidian", "brain"]' in (tmp_path / "o/.github/repository.toml").read_text()


@pytest.mark.parametrize("kind", ["service", "cli", "library", "web", "other"])
def test_obsidian_is_a_brain(kind: str, tmp_path: Path) -> None:
    """`kind` isn't asked for obsidian, and an answer for it can't make a vault anything else (0016)."""
    data = {"project_name": "demo", "description": "demo", "language": "obsidian", "kind": kind}
    with pytest.raises(ValueError, match="kind"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


@pytest.mark.parametrize("kind", ["service", "cli", "library"])
def test_kind_with_code_needs_a_layer(kind: str, tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "language": "none", "kind": kind}
    with pytest.raises(ValueError, match="Needs a language layer"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


BRAIN_DROPS = [
    "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md", "TODO.md", "version.txt", "contrib", "docs",
    "release-please-config.json", ".release-please-manifest.json", ".markdownlint-cli2.yaml",
    "scripts/check-wiki.py", ".github/workflows/release-please.yml", ".github/workflows/pr-title.yml",
    ".github/workflows/wiki.yml", ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
]  # fmt: skip


def test_brain_keeps_guard_rails_only(project: Path) -> None:
    """Releases, the wiki and markdownlint go; the guard rails stay, and the vault comes (0015, 0016)."""
    if not brain(project):
        assert not (project / "scripts/check-vault.py").exists() and not (project / "knowledge").exists()
        return
    assert [p for p in BRAIN_DROPS if (project / p).exists()] == []
    skip = {".git", "__pycache__"}
    files = [p for p in project.rglob("*") if p.is_file() and not skip & set(p.parts)]
    text = "\n".join(p.read_text(errors="ignore") for p in files)
    dropped = r"check-wiki|release-please|docs/wiki|docs/design|CHANGELOG|markdownlint"
    assert not re.search(dropped, text)
    sh("uv", "run", "scripts/check-vault.py", cwd=project)
    assert quiet(["uv", "run", "scripts/check-vault.py"], project) == [
        "check-vault OK: 4 files, 0 design records"
    ]
    assert "**/.obsidian/workspace*.json" in (project / ".gitignore").read_text()
    assert "proprietary" in (project / "LICENSE").read_text()


VAULT_OWNERS = {
    "README.md": True,
    "knowledge/🏠 Home.md": True,
    "knowledge/📐 Conventions.md": True,
    "knowledge/.obsidian/app.json": True,
    "knowledge/.obsidian/templates.json": True,
    "knowledge/decisions/Decisions.base": False,
    "knowledge/_templates/📝 Design Record.md": False,
}


def test_brain_ownership(tmp_path: Path) -> None:
    """copier update leaves a brain's README.md and notes alone, not other kinds' README.md,
    and still updates the design index and template (0015, 0016)."""
    for language, owned in (("obsidian", VAULT_OWNERS), ("none", {"README.md": False})):
        dst = tmp_path / language
        data = {"project_name": "demo", "description": "demo", "language": language}
        run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD",
                 skip_tasks=True)  # fmt: skip
        for name in owned:
            (dst / name).write_text("mine\n")
        run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD",
                 skip_tasks=True, overwrite=True)  # fmt: skip
        assert {n: (dst / n).read_text() == "mine\n" for n in owned} == owned, language


def test_vault_at_the_root(tmp_path: Path) -> None:
    """`vault_dir: .` puts the skeleton at the root, and the ignore and noread entries still match (0016)."""
    data = {"project_name": "demo", "description": "demo", "language": "obsidian", "vault_dir": "."}
    dst = tmp_path / "demo"
    run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD")
    for name in ["🏠 Home.md", "decisions/Decisions.base", ".obsidian/app.json", "_attachments/.gitkeep"]:
        assert (dst / name).is_file(), name
    assert not (dst / "knowledge").exists()
    agents = (dst / "AGENTS.md").read_text()
    assert "`.obsidian/`, `.trash/`, `_attachments/`" in agents and "`🏠 Home.md`" in agents
    (dst / ".obsidian/workspace.json").write_text("{}")
    (dst / ".trash").mkdir()
    (dst / ".trash/old.md").write_text("old")
    ignored = sh("git", "check-ignore", ".obsidian/workspace.json", ".trash/old.md", cwd=dst)
    assert ignored.split() == [".obsidian/workspace.json", ".trash/old.md"]
    sh("git", "add", "-A", cwd=dst)
    assert sh("uv", "run", "scripts/check-vault.py", cwd=dst).startswith("check-vault OK")


@pytest.mark.parametrize("bad", ["notes/vault", "..", "../notes", "", ".obsidian", "a/"])
def test_vault_dir_rejected(bad: str, tmp_path: Path) -> None:
    data = {"project_name": "demo", "description": "demo", "language": "obsidian", "vault_dir": bad}
    with pytest.raises(ValueError, match="vault_dir"):
        run_copy(str(ROOT), tmp_path / "p", data=data, defaults=True, unsafe=True, quiet=True,
                 vcs_ref="HEAD", skip_tasks=True)  # fmt: skip


RECORD = """---
kind: decision
number: {number}
status: {status}
date: 2026-11-01
authors: [A. Maintainer]
summary: A decision
supersedes: {supersedes}
superseded_by: {superseded_by}
tags: [decision]
---

## 🧭 Context

## ✅ Decision

## ⚖️ Alternatives considered

## 🌊 Consequences

## ❓ Open questions
"""
OLD = RECORD.format(number=1, status="superseded", supersedes="[]",
                    superseded_by='"[[📝 0002 Follow Upstream]]"')  # fmt: skip
NEW = RECORD.format(number=2, status="approved", supersedes='["[[📝 0001 Keep Notes Here]]"]',
                    superseded_by="")  # fmt: skip
VAULT_CASES = {
    "valid": ({}, ""),
    "broken embed": ({"🧭 Topic.md": "See [[🧭 Not Yet]].\n\n![[missing.png]]\n"}, "embeds a missing file"),
    "bad front matter": ({"🧭 Topic.md": "---\ntags: [a\n---\n"}, "not valid YAML"),
    "bad status": ({"decisions/📝 0002 Follow Upstream.md": NEW.replace("approved", "done")}, "status 'done'"),
    "duplicate number": ({"decisions/📝 0002 Also Two.md": NEW}, "number 2 is also"),
    "missing heading": ({"decisions/📝 0002 Follow Upstream.md": NEW.replace("## ⚖️ Alternatives considered", "")},
                        "missing headings: Alternatives considered"),
    "one-sided supersedes": ({"decisions/📝 0001 Keep Notes Here.md": OLD.replace("superseded_by: \"[[📝 0002 Follow Upstream]]\"", "superseded_by:")},
                             "doesn't link back"),
}  # fmt: skip


@pytest.mark.parametrize("case", VAULT_CASES)
def test_vault_check(case: str, project: Path, tmp_path: Path) -> None:
    """The vault check fails on what is always broken; a link to a missing note passes (0016)."""
    if not brain(project):
        pytest.skip("no vault")
    copy = tmp_path / project.name
    shutil.copytree(project, copy)
    vault = copy / "knowledge"
    notes = {"decisions/📝 0001 Keep Notes Here.md": OLD, "decisions/📝 0002 Follow Upstream.md": NEW,
             "🧭 Topic.md": "---\ntags: [topic]\n---\nSee [[🧭 Not Yet]] and ![[🏠 Home]].\n"}  # fmt: skip
    files, error = VAULT_CASES[case]
    for name, text in {**notes, **files}.items():
        (vault / name).write_text(text, encoding="utf-8")
    result = subprocess.run(["uv", "run", "scripts/check-vault.py"], cwd=copy, capture_output=True, text=True)
    if not error:
        assert result.returncode == 0, result.stdout + result.stderr
        assert result.stdout == "check-vault OK: 7 files, 2 design records\n"
    else:
        assert result.returncode == 1 and error in result.stdout, result.stdout + result.stderr


PULL = ".github/workflows/brain-pull.yml"
PULL_FILES = [PULL, "scripts/followed-repos.py"]


@pytest.mark.parametrize("data", [{"language": "obsidian"}, {"language": "python", "brain_pull": True},
                                  {"language": "none", "brain_pull": True}])  # fmt: skip
def test_brain_pull_is_opt_in(data: dict[str, object], tmp_path: Path) -> None:
    """Only a brain that answers brain_pull gets the workflow; an answer can't add it elsewhere (0017)."""
    dst = tmp_path / "p"
    run_copy(str(ROOT), dst, data={"project_name": "demo", "description": "demo", **data}, defaults=True,
             unsafe=True, quiet=True, vcs_ref="HEAD", skip_tasks=True)  # fmt: skip
    assert [f for f in PULL_FILES if (dst / f).exists()] == []


def test_brain_pull_workflow(project: Path) -> None:
    """Claude runs read-only; only propose writes, after checking the patch's scope (0017)."""
    if not brain(project):
        assert [f for f in PULL_FILES if (project / f).exists()] == []
        return
    flow = yaml.safe_load((project / PULL).read_text())
    jobs = flow["jobs"]
    assert flow["permissions"] == {} and set(jobs) == {"update", "propose"}
    assert jobs["update"]["permissions"] == {"contents": "read", "pull-requests": "read", "actions": "read"}
    assert jobs["propose"]["permissions"] == {"contents": "write", "pull-requests": "write",
                                              "issues": "write", "actions": "write"}  # fmt: skip
    steps = {s.get("name") or s["uses"].split("@")[0]: s for s in jobs["update"]["steps"]}
    assert "secrets.CLAUDE_CODE_OAUTH_TOKEN != ''" in steps["Is Claude Code set up?"]["env"]["HAS_TOKEN"]
    assert steps["Which followed repositories changed?"]["if"] == "steps.secret.outputs.ok == 'true'"
    claude = steps["Claude Code updates the notes"]
    assert claude["with"]["show_full_output"] == "${{ inputs.debug == true }}"
    assert "Edit(./knowledge/**/*.md)" in claude["with"]["claude_args"]
    assert "python3" not in claude["with"]["claude_args"]
    run = "\n".join(s.get("run", "") for s in jobs["propose"]["steps"])
    for needed in ["core.quotePath=false apply --numstat", "apply --summary", "uv run scripts/check-vault.py",
                   "gh workflow run ci.yml", "--label brain-pull"]:  # fmt: skip
        assert needed in run, needed


def test_actions_are_pinned(project: Path) -> None:
    """Every action is pinned to a commit SHA, with its version in a comment."""
    uses = [line.strip() for f in (project / ".github/workflows").glob("*.yml")
            for line in f.read_text().splitlines() if re.match(r"\s*(- )?uses: ", line)]  # fmt: skip
    pin = re.compile(r"^(- )?uses: (\./\S+|[\w.-]+/[\w./-]+@[0-9a-f]{40} # v\d\S*)$")
    assert uses and [u for u in uses if not pin.match(u)] == []


def scope_check(project: Path, out: Path, prefix: str) -> subprocess.CompletedProcess[str]:
    """Run the propose job's scope step on out/vault.patch, as the workflow does."""
    flow = yaml.safe_load((project / PULL).read_text())
    step = next(s for s in flow["jobs"]["propose"]["steps"] if s.get("name") == "The patch only edits notes")
    assert step["env"]["PREFIX"] == prefix
    return subprocess.run(["bash", "-c", step["run"]], cwd=project, capture_output=True, text=True,
                          env={**os.environ, "OUT": str(out), "PREFIX": prefix})  # fmt: skip


def patch_for(project: Path, out: Path, edits: dict[str, str]) -> None:
    """Make edits in a checkout and write them as out/vault.patch, as the update job does."""
    for name, text in edits.items():
        path = project / name
        new = not path.exists()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        if new:
            sh("git", "add", "-N", name, cwd=project)
    out.mkdir(exist_ok=True)
    (out / "vault.patch").write_text(sh("git", "diff", "--binary", cwd=project))


OUTSIDE = "outside the vault's notes"
SCOPE_CASES = {
    "a note": ({"knowledge/🏠 Home.md": "edited\n"}, ""),
    "two notes": ({"knowledge/🏠 Home.md": "x\n", "knowledge/📐 Conventions.md": "y\n"}, ""),
    "obsidian settings": ({"knowledge/.obsidian/app.json": "{}\n"}, OUTSIDE),
    "the design index": ({"knowledge/decisions/Decisions.base": "x\n"}, OUTSIDE),
    "the record template": ({"knowledge/_templates/📝 Design Record.md": "x\n"}, OUTSIDE),
    "outside the vault": ({"README.md": "x\n"}, OUTSIDE),
    "a workflow": ({".github/workflows/ci.yml": "x\n"}, OUTSIDE),
    "a new note": ({"knowledge/🧭 New.md": "x\n"}, "adds, removes or renames"),
}  # fmt: skip


@pytest.mark.parametrize("case", SCOPE_CASES)
def test_brain_pull_scope(case: str, project: Path, tmp_path: Path) -> None:
    """The propose job applies only edits to existing notes in the vault (0017)."""
    if not brain(project):
        pytest.skip("no Brain pull")
    copy = tmp_path / project.name
    shutil.copytree(project, copy)
    edits, error = SCOPE_CASES[case]
    patch_for(copy, tmp_path / "out", edits)
    result = scope_check(copy, tmp_path / "out", "knowledge/")
    if error:
        assert result.returncode == 1 and error in result.stdout, result.stdout + result.stderr
    else:
        assert result.returncode == 0, result.stdout + result.stderr


def test_brain_pull_with_the_vault_at_the_root(tmp_path: Path) -> None:
    """`vault_dir: .`: notes at the root are in scope; the AI files and README.md are not (0017)."""
    dst = tmp_path / "demo"
    data = {"project_name": "demo", "description": "demo", "language": "obsidian", "vault_dir": ".",
            "brain_pull": True}  # fmt: skip
    run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True, vcs_ref="HEAD")
    (dst / "decisions/🧭 Topic.md").write_text("---\nrepos: [a/b]\n---\n", encoding="utf-8")
    sh("git", "add", "-A", cwd=dst)
    assert sh("uv", "run", "-q", "scripts/followed-repos.py", cwd=dst) == "a/b\n"
    patch_for(dst, tmp_path / "ok", {"🏠 Home.md": "edited\n", "decisions/🧭 Topic.md": "x\n"})
    assert scope_check(dst, tmp_path / "ok", "").returncode == 0
    for name in ["AGENTS.md", "README.md", ".obsidian/app.json", "scripts/check.sh"]:
        sh("git", "checkout", "--", ".", cwd=dst)
        patch_for(dst, tmp_path / name.replace("/", "-"), {name: "x\n"})
        result = scope_check(dst, tmp_path / name.replace("/", "-"), "")
        assert result.returncode == 1 and name in result.stdout, name


FOLLOWED = {
    "🧭 Inline.md": '---\nrepos: [a/one, "b/two"]\n---\n',
    "sub/🧭 Block.md": "---\nrepos:\n  - c/three\n  - not a repo\n---\n",
    "🧭 One.md": "---\nrepos: a/one\n---\n",
    "_templates/🧭 Skipped.md": "---\nrepos: [z/skipped]\n---\n",
    "🧭 None.md": "No front matter.\n",
}


def test_followed_repos(project: Path, tmp_path: Path) -> None:
    """The gate's list: inline and block lists, distinct and sorted; templates and bad entries skipped (0017)."""
    if not brain(project):
        pytest.skip("no Brain pull")
    copy = tmp_path / project.name
    shutil.copytree(project, copy)
    for name, text in FOLLOWED.items():
        (copy / "knowledge" / name).parent.mkdir(parents=True, exist_ok=True)
        (copy / "knowledge" / name).write_text(text, encoding="utf-8")
    result = subprocess.run(["uv", "run", "-q", "scripts/followed-repos.py"], cwd=copy, capture_output=True,
                            text=True)  # fmt: skip
    assert result.returncode == 0, result.stderr
    assert result.stdout == "a/one\nb/two\nc/three\n"
    assert "repos entry 'not a repo' is not owner/name" in result.stderr


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


def test_home_toc_lines_are_separate_paragraphs(project: Path) -> None:
    """A missing blank line joins two Table of Contents lines into one paragraph (#78)."""
    wiki_only(project)
    lines = (project / "docs/wiki/Home.md").read_text(encoding="utf-8").splitlines()
    toc = re.compile(r"\*\*[^*]+\*\*:")
    joined = [b for a, b in zip(lines, lines[1:]) if toc.match(a) and toc.match(b)]
    assert not joined


def test_issue_form_offers_every_choice() -> None:
    """The Template problem form lists every language and kind copier.yml offers (#79)."""
    import yaml

    questions = yaml.safe_load((ROOT / "copier.yml").read_text())
    form = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE/template_problem.yml").read_text())
    dropdowns = {f["id"]: f["attributes"]["options"] for f in form["body"] if f["type"] == "dropdown"}
    for question in ("language", "kind"):
        choices = [c["value"] if isinstance(c, dict) else c for c in questions[question]["choices"].values()]
        assert dropdowns[question] == choices, question


def test_readme_links_existing_wiki_pages(project: Path) -> None:
    """The README links the wiki by URL, which check-wiki.py doesn't follow."""
    wiki_only(project)
    pages = re.findall(r"/wiki/([\w-]+)\)", (project / "README.md").read_text())
    missing = [p for p in pages if not (project / "docs/wiki" / f"{p}.md").exists()]
    assert pages and not missing


def test_wiki_standard(project: Path) -> None:
    wiki_only(project)
    sh("python3", "scripts/check-wiki.py", cwd=project)


def test_fresh_wiki_blocks_a_release(project: Path) -> None:
    """Skeleton guidance must fail strict mode (Release PRs) until it is written."""
    wiki_only(project)
    result = subprocess.run(
        ["python3", "scripts/check-wiki.py", "--strict"], cwd=project, capture_output=True
    )
    assert result.returncode == 1


def test_written_wiki_passes_strict(project: Path, tmp_path: Path) -> None:
    wiki_only(project)
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
    topics = ["obsidian", "brain"] if brain(project) else topics
    topics = [t for t in topics if t not in ("none", "other")]
    assert want == {"description": variant.get("description", f"A demo {project.name.removeprefix('demo-')}"),
                    "homepage": "" if brain(project) else
                                f"https://github.com/metalayerlab/{project.name}/wiki",
                    "topics": topics}  # fmt: skip

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
    checks = [["uv", "run", "scripts/check-vault.py"] if brain(project) else ["python3", "scripts/check-wiki.py"]]
    sh(*checks[0], cwd=project)  # uv's first run reports installing PyYAML
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
    wiki_only(project)
    copy = tmp_path / project.name
    shutil.copytree(project, copy, ignore=shutil.ignore_patterns(".venv", "node_modules"))
    page = copy / "docs/wiki/Home.md"
    page.write_text(page.read_text() + "\n```sh\n$ demo --help\n```\n")
    result = subprocess.run(
        ["scripts/check-docs-secrets.sh", "docs"], cwd=copy, capture_output=True, text=True
    )
    assert result.returncode == 1 and "MD014" in result.stdout + result.stderr


def test_labels_are_created(project: Path) -> None:
    """Copier copies files, not labels: a workflow creates each label the checks use (#56)."""
    files = [*(project / ".github/workflows").glob("*.yml"), project / "scripts/check-wiki.py"]
    text = "\n".join(f.read_text() for f in files if f.exists())
    use = r"--label ([\w-]+)|^\s+labels: ([\w-]+)|labels\.\*\.name, '([\w-]+)'"
    used = set(re.findall(use, text, re.M))
    used = {name for group in used for name in group if name}
    created = set(re.findall(r"gh label create ([\w-]+)", text))
    assert {"template-update"} | (set() if brain(project) else {"no-docs-needed"}) <= used
    assert used <= created, used - created


def edit_hook(project: Path, file_path: str) -> subprocess.CompletedProcess[str]:
    event = json.dumps({"cwd": str(project), "tool_input": {"file_path": file_path}})
    return subprocess.run(
        ["python3", "scripts/repo-boundary.py"], cwd=project, input=event, capture_output=True,
        text=True, env={**os.environ, "CLAUDE_PROJECT_DIR": str(project)},
    )  # fmt: skip


def test_edits_stay_in_the_repository(project: Path) -> None:
    """Another codebase is changed by an issue in its own repository (0013)."""
    settings = json.loads((project / ".claude/settings.json").read_text())
    hook = settings["hooks"]["PreToolUse"][0]
    assert "Write" in hook["matcher"] and "scripts/repo-boundary.py" in hook["hooks"][0]["command"]
    nested = project / ".boundary-test"
    try:
        sh("git", "init", "-q", str(nested), cwd=project)
        cases = {
            "src/new.txt": 0,
            str(project / "README.md"): 0,
            f"{tempfile.gettempdir()}/scratch.txt": 0,
            str(Path.home() / ".claude/memory.md"): 0,
            str(Path.home() / "elsewhere/repo/file.txt"): 2,
            ".boundary-test/file.txt": 2,
        }
        results = {p: edit_hook(project, p) for p in cases}
    finally:
        shutil.rmtree(nested)
    assert {p: r.returncode for p, r in results.items()} == cases
    assert all(r.stdout + r.stderr == "" for r in results.values() if r.returncode == 0)
    assert all("issue in its own repository" in r.stderr for r in results.values() if r.returncode)


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
    if project.name.endswith("web"):
        _probe_healthz(project, tag, shell=True)
        return
    if "service" not in project.name:
        sh("docker", "run", "--rm", tag, "version", cwd=project)
        return
    _probe_healthz(project, tag)


def test_system_packages_are_empty_by_default(project: Path) -> None:
    """contrib/system-packages.txt (#53) exists in every project with code and lists nothing."""
    if brain(project):
        pytest.skip("no code to build")
    lines = (project / "contrib/system-packages.txt").read_text().splitlines()
    assert [ln for ln in lines if not ln.startswith("#") and ln.strip()] == ["build:", "runtime:"]


@pytest.mark.docker
def test_image_installs_system_packages(project: Path, tmp_path: Path) -> None:
    """The `build:` packages reach the builder stage and the `runtime:` ones the image (#53)."""
    if not project.name.endswith("cli"):
        pytest.skip("one variant per layer is enough")
    copy = tmp_path / project.name
    shutil.copytree(project, copy, ignore=shutil.ignore_patterns(".venv", "node_modules"))
    with (copy / "contrib/system-packages.txt").open("a") as f:
        f.write("build: pkg-config\nruntime: tini\n")
    tag = f"{project.name}:packages"
    sh("docker", "build", "-q", "-t", tag, ".", cwd=copy)
    sh("docker", "run", "--rm", "--entrypoint", "tini", tag, "--version", cwd=copy)


@pytest.mark.docker
def test_image_installs_extras(tmp_path: Path) -> None:
    """An extra named in `image_extras` is in the image (#63)."""
    data = {"project_name": "demo", "description": "demo", "kind": "cli", "image_extras": ["six"]}
    dst = tmp_path / "demo"
    run_copy(str(ROOT), dst, data=data, defaults=True, unsafe=True, quiet=True,
             vcs_ref="HEAD", skip_tasks=True)  # fmt: skip
    with (dst / "pyproject.toml").open("a") as f:
        f.write('\n[project.optional-dependencies]\nsix = ["six>=1.16"]\n')
    sh("uv", "lock", "-q", cwd=dst)
    sh("docker", "build", "-q", "-t", "demo:extras", ".", cwd=dst)
    sh("docker", "run", "--rm", "--entrypoint", "python", "demo:extras", "-c", "import six",
       cwd=dst)  # fmt: skip


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


def _probe_healthz(project: Path, tag: str, shell: bool = False) -> None:
    """Run the image as docker-build.yml's smoke test does and wait for /healthz.

    shell: also check that / and any route are the app's index.html (a web app, 0014),
    with the manifests' hardening: a read-only root and no capabilities.
    """
    name = f"{project.name}-test"
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    hardening = ["--read-only", "--tmpfs", "/tmp", "--cap-drop", "ALL"] if shell else []
    sh("docker", "run", "-d", "--name", name, *hardening, "-p", "127.0.0.1::8080", tag, cwd=project)
    try:
        port = sh("docker", "port", name, "8080", cwd=project).split(":")[-1].strip()
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2) as r:
                    assert r.status == 200
                for path in ["/", "/some/route"] if shell else []:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=2) as r:
                        assert '<div id="root">' in r.read().decode(), path
                return
            except OSError:
                time.sleep(1)
        pytest.fail(sh("docker", "logs", name, cwd=project))
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)
