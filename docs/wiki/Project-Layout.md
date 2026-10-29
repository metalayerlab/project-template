# Project Layout

What a generated `service` contains (a `cli` lacks `api.py` and the HTTP pages; a `library` also lacks the CLI, image and contrib).

## Files

```text
.github/
  workflows/          ci, docker-build, docker-cleanup, release-please, pr-title, wiki, template-update
  ISSUE_TEMPLATE/     bug, feature, links (wiki, private security reports)
  CODEOWNERS  dependabot.yml  pull_request_template.md  copilot-instructions.md
.claude/settings.json  .cursor/rules/project.mdc
AGENTS.md  CLAUDE.md  GEMINI.md          instructions for AI assistants (AGENTS.md is the source)
README.md  CONTRIBUTING.md  SECURITY.md  LICENSE  CHANGELOG.md  TODO.md
src/<pkg>/            __init__ (version)  config (settings)  cli (Typer)  api (FastAPI)  __main__
tests/unit/  tests/integration/  tests/conftest.py
scripts/              bootstrap.sh  check-wiki.py  gen-wiki.py  check-manifests.sh  check-docs-secrets.sh  [check-personal-data.py]
docs/wiki/            the project wiki + .standard.toml
docs/design/          design records: README.md (the index), 0000-template.md
docs/ai/              prompts.md  review-checklist.md
contrib/              <name>.example.yaml  docker/  k8s/  systemd/
Dockerfile  docker/entrypoint.sh  .dockerignore
pyproject.toml  uv.lock  release-please-config.json  .release-please-manifest.json  .copier-answers.yml
.gitignore  .gitleaks.toml  .markdownlint-cli2.yaml  .pre-commit-config.yaml  .editorconfig
```

## Who owns what

| Owner | Files | On `copier update` |
|---|---|---|
| **Template** | `.github/workflows/`, `scripts/`, `docs/wiki/.standard.toml`, `docs/wiki/Release-Process.md`, `docs/ai/`, lint configs, `Dockerfile`, `docker/` | Updated (three-way merge; local edits survive or conflict) |
| **Project** | `src/`, `tests/`, every other `docs/wiki/` page, `CHANGELOG.md`, `TODO.md`, `contrib/*.example.yaml` | Never touched again after the first copy (`_skip_if_exists`) |
| **Shared** | `README.md`, `AGENTS.md`, `pyproject.toml`, `contrib/*/` manifests | Merged: template changes apply on top of yours, and clashes become conflict markers |
| **Machines** | `CHANGELOG.md` entries, the version, `.release-please-manifest.json` (release-please); `.copier-answers.yml` (Copier); generated wiki sections (`gen-wiki.py`) | Never edited by hand |

Change a template-owned file in project-template, not in the project. A local fix is overwritten or conflicts at the next update, and the other projects never get it.
