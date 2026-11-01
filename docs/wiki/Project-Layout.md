# Project Layout

What a generated `service` contains (a `cli` lacks `api.py` and the HTTP pages; a `library` also lacks the CLI, image and contrib). A TypeScript `web` app has no CLI or `config.yaml`: it has the files under *web* below, and `docker/nginx.conf` in place of `docker/entrypoint.sh`.

## Files

```text
.github/
  workflows/          ci, docker-build, docker-cleanup, release-please, pr-title, wiki, template-update
  ISSUE_TEMPLATE/     bug, feature, change request from another repository, links (wiki, private security reports)
  CODEOWNERS  dependabot.yml  pull_request_template.md  copilot-instructions.md
  repository.toml     GitHub's About box: description, website, topics (scripts/repo-metadata.py)
.claude/settings.json  .cursor/rules/project.mdc
AGENTS.md  CLAUDE.md  GEMINI.md          instructions for AI assistants (AGENTS.md is the source)
README.md  CONTRIBUTING.md  SECURITY.md  LICENSE  CHANGELOG.md  TODO.md
src/<pkg>/            __init__ (version)  config (settings)  cli (Typer)  api (FastAPI)  __main__      Python
src/                  index (version)  config  cli (commander)  api (Fastify)                 TypeScript
src/                  main.tsx  routes.tsx  pages/  config.ts (/config.json)  vite-env.d.ts       web
index.html  public/config.json  vite.config.ts  docker/nginx.conf  docker/nginx-site.conf     web
tests/unit/  tests/integration/  tests/conftest.py (Python) or tests/setup.ts, helpers.ts (TypeScript)
scripts/              bootstrap.sh  check-wiki.py  repo-metadata.py  repo-boundary.py  gen-wiki.py|.ts  check-manifests.sh  check-docs-secrets.sh  [check-personal-data.py]  [check.sh]
docs/wiki/            the project wiki + .standard.toml
docs/design/          design records: README.md (the index), 0000-template.md
docs/ai/              prompts.md  review-checklist.md
contrib/              <name>.example.yaml  system-packages.txt  docker/  k8s/  systemd/
Dockerfile  docker/entrypoint.sh  .dockerignore
pyproject.toml  uv.lock  (or package.json  package-lock.json  tsconfig*.json  eslint.config.js  vitest.config.ts)  [version.txt]  release-please-config.json  .release-please-manifest.json  .copier-answers.yml
.gitignore  .gitleaks.toml  .markdownlint-cli2.yaml  .pre-commit-config.yaml  .editorconfig
```

A brain (`language: obsidian`) has the guard rails and a vault: `AGENTS.md`, the tool pointers, `.claude/settings.json`, `.github/` (CI, template update, CODEOWNERS, Dependabot, the change-request form, `repository.toml`), `scripts/` (`bootstrap.sh`, `check.sh`, `check-vault.py`, `check-docs-secrets.sh` for gitleaks only, `repo-boundary.py`, `repo-metadata.py`), `README.md`, `LICENSE`, the dotfiles, and the vault in `vault_dir` (`knowledge/` by default). No `docs/`, `contrib/`, release files, `CONTRIBUTING.md`, `SECURITY.md` or `TODO.md`. `.gitignore` adds Obsidian's per-client state (`**/.obsidian/workspace*.json`, `**/.obsidian/cache`, `**/.trash/`) ([design 0016](https://github.com/metalayerlab/project-template/blob/main/docs/design/0016-obsidian-layer.md)):

```text
knowledge/
  🏠 Home.md  📐 Conventions.md       the start note; the note conventions AGENTS.md says to follow
  decisions/Decisions.base          the design index (T); records are `📝 NNNN Title.md` notes beside it
  _templates/📝 Design Record.md     the record template (T), for Obsidian's Insert template
  _attachments/                     files notes embed
  .obsidian/app.json  templates.json  the attachment and templates folders; the rest of .obsidian/ is each user's
```

`README.md`, Home, Conventions, `_attachments/` and the two `.obsidian/` files are the project's; the base and the record template are the template's (T). `scripts/check-vault.py` checks front matter, embeds, the design records' shape and the AI files' context budget; a link to a note that doesn't exist yet is fine. With `brain_pull`, a brain also gets `.github/workflows/brain-pull.yml` and `scripts/followed-repos.py` (both T; [CI Pipeline](CI-Pipeline#brain-pull)).

## Who owns what

| Owner | Files | On `copier update` |
|---|---|---|
| **Template** | `.github/workflows/`, `scripts/`, `docs/wiki/.standard.toml`, `docs/wiki/Release-Process.md`, `docs/ai/`, lint configs, `Dockerfile`, `docker/` | Updated (three-way merge; local edits survive or conflict) |
| **Project** | `src/`, `tests/`, `scripts/check.sh` and `version.txt` (`language: none`), a brain's `README.md` and notes, every other `docs/wiki/` page, `.github/repository.toml`, `CHANGELOG.md`, `TODO.md`, `contrib/*.example.yaml`, `contrib/system-packages.txt` | Never touched again after the first copy (`_skip_if_exists`) |
| **Shared** | `README.md`, `AGENTS.md`, `pyproject.toml` or `package.json`, `contrib/*/` manifests | Merged: template changes apply on top of yours, and clashes become conflict markers |
| **Machines** | `CHANGELOG.md` entries, the version, `.release-please-manifest.json` (release-please); `.copier-answers.yml` (Copier); generated wiki sections (`gen-wiki.py`) | Never edited by hand |

Change a template-owned file in project-template, not in the project. A local fix is overwritten or conflicts at the next update, and the other projects never get it.
