# Introduction

## What it is

A [Copier](https://copier.readthedocs.io/) template. Copier asks a few questions, renders `template/` into a new repository, and records the answers and the template version in `.copier-answers.yml`. Later, `copier update` replays the template's changes onto the project with a three-way merge. That last step is the reason for Copier: our earlier projects were each copied by hand from one another and drifted apart. Their action versions, lint strictness and version regexes all differ, and bugs fixed in one copy were never fixed in the others.

It has a **language-agnostic core** (release, images, manifests, wiki, AI files) and **language layers**. The layers are Python and TypeScript (Node.js), and `none` gives the core alone. A project's `kind` (service, CLI, library, or a `web` front end for TypeScript) decides its shape ([Contributing to the Template](Contributing-to-the-Template#adding-a-language-layer)).

## What was taken from existing projects

Our earlier projects each had some part done best. The template takes the best version of each, and fixes the bugs found along the way:

| Area | What was kept |
|---|---|
| Python tooling | uv + hatchling + lock file, the version only in `pyproject.toml`, strict mypy, blocking lint, a Python version matrix |
| Images | The multi-stage uv Dockerfile, the PUID/PGID `setpriv` wrapper, a container smoke test before push, tag rebuilds by dispatch, `latest` only set explicitly, a correct image digest |
| Manifests | The hardened systemd unit, the kustomize base with restricted security contexts |
| Upkeep | Dependabot (with the Python base image held to patch updates), GHCR branch-image cleanup, issue templates, the optional personal-data guard |
| Conventions | The `_FILE`/env/file config precedence, the `TODO.md` "Decided against" list, Conventional Commits, the wiki page set and its `_Sidebar`/`_Footer` layout |

Fixed while consolidating:

- CI accepted semver (`1.2.3-beta.1`) while the release required PEP 440 (`1.2.3b1`). It's PEP 440 everywhere now.
- The home-made changelog had several bugs: merge commits leaked into sections, entries could be duplicated, nothing was written for a first release, and it was edited by hand. release-please replaces it.
- The `Image digest` step printed nothing in some copies.
- Conventional Commits were never enforced. The PR title is now linted.
- Coverage had no floor anywhere. It's 80% now.
- Credential checks were grep regexes. gitleaks scans the full history now.
- Actions were pinned to major tags only. They're pinned to SHAs now, and Dependabot updates them.

## What was left out

| Left out | Why |
|---|---|
| `bump-version.sh`, the git-log/grep changelog step, `release-template.md` | Replaced by release-please; the release template was never used |
| `__version__.py` | A second copy of the version that had to be kept in sync; `importlib.metadata` reads it instead |
| `requirements*.txt`, setuptools, black | Stale or superseded: the uv lock file, hatchling and `ruff format` |
| Helm | Our clusters run Flux with kustomize. A chart would double the maintenance for no gain |
| Project-specific machinery | Extra binary build stages, privileged/FUSE workloads, DaemonSet init containers, optional backing-service compose variants, custom WSGI entrypoints: projects add these themselves |
| `PLAN.md`, `BUGS.md` | Ephemeral; design records in `docs/design/` take their place |
| `.graphify/` output | Local knowledge graphs stay git-ignored |
| CODE_OF_CONDUCT | Internal team repositories; add one if a project goes public |
| Separate `*.wiki` clones | The wiki now lives in each repository: see [Project Wiki Standard](Project-Wiki-Standard) |
