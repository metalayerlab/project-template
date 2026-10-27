# CI Pipeline

Every workflow is template-owned, and every action is pinned to a commit SHA (Dependabot proposes the updates).

## Workflows

| Workflow | Runs on | Does |
|---|---|---|
| `ci.yml` | push to `main`, `dev/**`, `feat/**`; PRs | **Secret scan** (gitleaks, full history) · **Test** per Python version: `uv sync --locked`, ruff check + format, mypy strict, pytest with the coverage floor, import + `--help` smoke test, generated wiki sections current · **Version and lock file**: PEP 440, pyproject = manifest, `uv lock --check` · **Dockerfile and contrib manifests**: `scripts/check-manifests.sh` · **Workflow lint**: actionlint · optional **Personal data guard** |
| `wiki.yml` | push to `main`; PRs (also on label changes) | **Wiki standard**: `check-wiki.py` (`--strict` on Release PRs) + markdownlint · **Docs updated with the code** (PRs) · **Publish** to the GitHub wiki (main) |
| `pr-title.yml` | PRs | The title is a Conventional Commit with a lower-case subject |
| `docker-build.yml` | branches, PRs, release (called), manual | See [Docker Images](Docker-Images) |
| `docker-cleanup.yml` | daily | Deletes branch images older than 7 days |
| `release-please.yml` | push to `main` | See [Release Process](Release-Process) |
| `template-update.yml` | weekly | See [Updating from the Template](Updating-from-the-Template) |

Locally, `pre-commit` runs the same lint, type, wiki and secret checks before each commit, and checks the commit message format.

## Required checks

Make these required in the `main` ruleset ([Quick Start](Quick-Start#create-the-github-repository)): `Secret scan`, every `Test (Python …)`, `Version and lock file`, `Dockerfile and contrib manifests`, `Workflow lint`, `Wiki standard`, `Docs updated with the code`, and `conventional-commit`. A check that is skipped (for example docs-touched with the `no-docs-needed` label) counts as passed.

Nothing in CI is `continue-on-error`. A red check means the PR waits.
