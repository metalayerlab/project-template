# 0004: Run CI's markdownlint and gitleaks locally

Status: Implemented
Date: 2026-10-29
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Every project's CI runs two checks that nothing local runs (#21):

| Check | Where | How it's pinned |
|---|---|---|
| gitleaks | `ci.yml`, *Secret scan* | `docker run ghcr.io/gitleaks/gitleaks:v8.30.1 git --redact --verbose --config .gitleaks.toml .` |
| markdownlint-cli2 | `wiki.yml`, *Wiki standard* | `DavidAnson/markdownlint-cli2-action` v25.0.0 (by SHA), which bundles markdownlint-cli2 0.24.0; globs `docs/wiki/*.md`, `*.md`, `!CHANGELOG.md` |

The first project (metalayerlab/mitm-proxy) passed its whole Definition of done locally, then failed both
checks on the PR: an MD014 `$` prompt in Home.md, and a gitleaks false positive on RFC 6455's sample key.

Constraints:

- No new toolchain on the developer's machine: both tools already ship as Docker images.
- Docker is optional locally (the Definition of done must still be runnable without it), never in CI.
- Local and CI must not drift. Dependabot bumps the action's SHA in `wiki.yml`, but it would not bump a
  Docker tag written into a script.
- The rendered AGENTS.md has 73 characters left under its 75% headroom (after #26): one short line.

## Decision

- **`scripts/check-docs-secrets.sh`** (core, template-owned, POSIX `sh`), in every project:
  - `scripts/check-docs-secrets.sh` runs both; `scripts/check-docs-secrets.sh docs` or `secrets` runs one.
  - secrets: the exact `docker run` command from `ci.yml` today.
  - docs: `docker run davidanson/markdownlint-cli2:v0.24.0` with `.markdownlint-cli2.yaml` and the globs
    from `wiki.yml`.
  - Without Docker: prints `skip: docker is not installed` and exits 0. With `CI=true` it exits 1 instead,
    so CI can never pass by skipping (the convention `check-manifests.sh` already follows).
- **CI calls the script**, so it is the only place the versions and arguments live:
  - `ci.yml`'s gitleaks step becomes `run: scripts/check-docs-secrets.sh secrets`.
  - `wiki.yml`'s *Markdown lint* step becomes `run: scripts/check-docs-secrets.sh docs`, replacing the action.
- **Version bumps** are by hand in the template (one file), like gitleaks is already. The bump goes into
  Dependabot's `docker` ecosystem only if it can track a tag in a shell script, which it can't today.
- **Definition of done**: AGENTS.md gets `scripts/check-docs-secrets.sh  # if Docker is available`, and the
  Claude allow-list gets `Bash(scripts/check-docs-secrets.sh:*)`.
- **Tests** (`tests/test_render.py`): under `-m docker`, every variant passes the script, and an MD014 line
  planted in a copy fails it. Plain tests run it with no Docker on `PATH` (exit 0, and exit 1 with `CI=true`),
  and check that pre-commit's gitleaks `rev` equals the script's image tag.

## Alternatives considered

- **Script with its own pins, plus a template test that they match the workflows**: keeps the action and
  its PR annotations, but a project's Dependabot bumps the action alone, and the two drift in every project
  where the template test never runs.
- **pre-commit hooks** (gitleaks and markdownlint both have them): pre-commit is optional here (bootstrap
  only suggests it), and its hook versions are a third pin to keep in step.
- **Install the tools natively** (Homebrew, npm): a Node toolchain in every project for one linter, and
  versions that differ per machine.

## Consequences

- The local result matches CI's by construction: same image, same arguments, same config.
- `wiki.yml` loses the action's inline PR annotations: findings appear in the job log as `file:line`
  instead. markdownlint-cli2 bumps stop arriving from Dependabot and are made in the template.
- gitleaks scans commits (`git` mode), as CI does: uncommitted changes aren't scanned until committed.
- Projects get the new script and the changed workflow steps through `copier update`. Nothing in them is
  project-owned, so there's no conflict unless a project edited those steps.
- Wiki: CI-Pipeline (the local equivalents), Project-Layout (`scripts/`), Troubleshooting (a gitleaks false
  positive goes in `.gitleaks.toml`'s allow-list; MD014 and `$` prompts).

## Resolved questions

1. **Replace the markdownlint action with the script?** Yes. Local and CI match only if CI runs the same
   command. A pin-matching test would run only in template CI, while each project's Dependabot bumps the
   action alone. Annotations can come back later with a problem matcher if they're missed.
2. **The name?** `check-docs-secrets.sh`, not `check-lint.sh`: "Lint" already means ruff in AGENTS.md's
   commands table. It also follows the `check-wiki` / `check-manifests` naming.
3. **Scan the working tree too?** No. The script mirrors CI, which scans commits, and `gitleaks dir` would
   need its own exclusions. Staged changes are already scanned by pre-commit's gitleaks hook, at the same
   version (a test checks it).

Building it found a template bug, fixed in #28: a fresh `library` project's Troubleshooting page failed
MD012.
