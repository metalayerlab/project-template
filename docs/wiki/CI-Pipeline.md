# CI Pipeline

Every workflow is template-owned, and every action is pinned to a commit SHA (Dependabot proposes the updates). The gitleaks and markdownlint-cli2 images are pinned in `scripts/check-docs-secrets.sh`, which CI calls, and are bumped by hand in project-template.

## Workflows

| Workflow | Runs on | Does |
|---|---|---|
| `ci.yml` | push to `main`; PRs (branches are checked through their PR, so nothing runs twice) | Every **Test** job first installs the `build:` packages in `contrib/system-packages.txt`, if any ([Docker Images](Docker-Images#system-packages)) · **Secret scan** (gitleaks, full history: `scripts/check-docs-secrets.sh secrets`) · **Test** per Python version: `uv sync --locked`, ruff check + format, mypy strict, pytest with the coverage floor (a warning fails it), import + `--help` smoke test, generated wiki sections current · **Version and lock file**: PEP 440, pyproject = manifest, `uv lock --check` · TypeScript: **Test** per Node.js version (`npm ci`, which fails on a stale lock file; ESLint, Prettier, `tsc`, vitest with the coverage floor, the import and `--help` smoke test (for `web`: `npm run build` makes `dist/index.html`), generated wiki sections current) and **Version and lock file** (semver; `package.json` = `package-lock.json` = manifest) · **Dockerfile and contrib manifests**: `scripts/check-manifests.sh` · **Workflow lint**: actionlint · optional **Personal data guard** |
| `wiki.yml` | push to `main`; PRs (also on label changes) | **Wiki standard**: `check-wiki.py` (`--strict` on Release PRs) + markdownlint (`scripts/check-docs-secrets.sh docs`) + `.github/repository.toml` is valid · **Docs updated with the code** (PRs) · creates the `no-docs-needed` label (main) · **Publish** to the GitHub wiki (main), then a **warning**, never a failure, if GitHub's About box differs from `.github/repository.toml` (fix: `python3 scripts/repo-metadata.py`, which needs admin rights) |
| `pr-title.yml` | PRs | The title is a Conventional Commit with a lower-case subject |
| `docker-build.yml` | branches, PRs, release (called), manual | See [Docker Images](Docker-Images) |
| `docker-cleanup.yml` | daily | Deletes branch images older than 7 days |
| `release-please.yml` | push to `main` | See [Release Process](Release-Process) |
| `dependabot-automerge.yml` | Dependabot PRs (only with `dependabot_automerge`) | Queues auto-merge for patch (or patch and minor) updates; the merge waits for a code owner's approval and every required check. It never approves |
| `template-update.yml` | weekly | See [Updating from the Template](Updating-from-the-Template) |

Locally, `pre-commit` runs the same lint, type, wiki and secret checks before each commit, and checks the commit message format. `scripts/check-docs-secrets.sh` runs CI's markdownlint and gitleaks steps exactly, with the same images, arguments and config. It needs Docker: without it, it skips locally and fails in CI.

## Required checks

Make these required in the `main` ruleset ([Quick Start](Quick-Start#create-the-github-repository)): `Secret scan`, every `Test (Python …)` or `Test (Node.js …)`, `Version and lock file`, `Dockerfile and contrib manifests`, `Workflow lint`, `Wiki standard`, `Docs updated with the code`, and `conventional-commit`. A check that is skipped (for example docs-touched with the `no-docs-needed` label) counts as passed.

Nothing in CI is `continue-on-error`. A red check means the PR waits.
