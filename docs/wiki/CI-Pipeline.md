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
| `brain-pull.yml` | daily; manual (brains with `brain_pull` only) | See [Brain pull](#brain-pull) |

Locally, `pre-commit` runs the same lint, type, wiki and secret checks before each commit, and checks the commit message format. `scripts/check-docs-secrets.sh` runs CI's markdownlint and gitleaks steps exactly, with the same images, arguments and config. It needs Docker: without it, it skips locally and fails in CI.

## Brain pull

A brain that answers `brain_pull` ([design 0017](https://github.com/metalayerlab/project-template/blob/main/docs/design/0017-brain-pull.md)) gets `brain-pull.yml`: daily at 05:00 UTC, or by hand (`gh workflow run brain-pull.yml`, with an optional `since` date and a `debug` switch that logs every Claude message and tool call, which is how you see the calls it refused).

1. **Update notes** (read-only token). Without the `CLAUDE_CODE_OAUTH_TOKEN` secret it stops there, green. Otherwise `scripts/followed-repos.py` lists the `repos:` values in the vault, and a shell step asks GitHub which of them have commits or releases since the start of this workflow's last *successful* run. Only if one changed does Claude Code run, with read-only tools and edits limited to the vault's notes, and write a patch, a PR body and optional issues.
2. **Open or update the PR** (`contents`, `pull-requests`, `issues` and `actions: write`). It rejects a patch that touches anything but existing `.md` notes in the vault (`.obsidian/`, `_templates/`, `Decisions.base`, new or deleted files), re-runs `check-vault.py`, commits to the open `brain-pull` PR's branch or a new `brain-pull/<date>`, and opens or comments on the PR. A closed PR's branch is never reused.

A failed run moves no date, so the next one reads the same changes again. After the push nothing fails the run: dispatching CI and opening issues (3 at most) are warnings. A push by `GITHUB_TOKEN` starts no workflows, so the job dispatches `ci.yml` on the branch; that run isn't shown on the PR, and the PR's own CI run waits for you to approve it. Repositories it can't read (private ones) are skipped with a warning. Nothing is merged without you.

## Required checks

Make these required in the `main` ruleset ([Quick Start](Quick-Start#create-the-github-repository)): `Secret scan`, every `Test (Python …)` or `Test (Node.js …)`, `Version and lock file`, `Dockerfile and contrib manifests`, `Workflow lint`, `Wiki standard`, `Docs updated with the code`, and `conventional-commit`. A check that is skipped (for example docs-touched with the `no-docs-needed` label) counts as passed.

Nothing in CI is `continue-on-error`. A red check means the PR waits.
