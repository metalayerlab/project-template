# project-template

The starting point for every metalayerlab project. It gives AI-generated, human-reviewed codebases the same
CI/CD, release automation, deployment manifests, documentation standard and AI-assistant instructions from
their first commit, and keeps them in step afterwards.

```sh
uvx copier copy --trust gh:metalayerlab/project-template my-project
cd my-project && git add -A && git commit -m "chore: initial commit from project-template"
```

Then follow the wiki's [Quick Start](https://github.com/metalayerlab/project-template/wiki/Quick-Start):
create the GitHub repo, set up branch protection, create the first wiki page, and start the kick-off prompt.

## What a project gets

| Area | What |
|---|---|
| **Code skeleton** (Python layer) | uv + hatchling, `src/` layout, config loader (`_FILE` > env > file > default), Typer CLI, FastAPI service with `/healthz` `/readyz` `/version`, pytest with an 80% coverage floor, ruff, mypy `--strict` |
| **CI** | lint, format, types, tests on a Python matrix, gitleaks secret scan, version/lock consistency, Dockerfile + manifest validation (hadolint, kubeconform, `systemd-analyze`, `docker compose config`), actionlint |
| **Release** | release-please: a reviewed Release PR bumps the version and writes `CHANGELOG.md` from Conventional Commits; merging it tags, publishes the GitHub Release and builds the image. PR titles are linted. |
| **Images** | GHCR, multi-arch, smoke-tested on every PR; `:X.Y.Z`/`:X.Y`/`:X`/`:latest` on release, `:edge` from main, expiring branch images; OCI labels |
| **contrib/** | Docker Compose, Kubernetes (kustomize base, PSS *restricted*, NetworkPolicy, Flux-friendly), systemd (sandboxed unit + sysusers), each with the image tag kept current by release-please |
| **Wiki** | A **standardised wiki in `docs/wiki/`**: required pages and headings, CI-checked links and sidebar, sections generated from the code, "docs touched" enforcement, strict mode on Release PRs, published one way to the GitHub wiki |
| **AI layer** | `AGENTS.md` (the single source), plus `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` and `.cursor/rules/` pointers; `.claude/settings.json` guard rails; kick-off prompts; a human review checklist; a PR template that records AI involvement |
| **Upkeep** | Dependabot (actions, uv, Docker), CODEOWNERS, issue templates, and a weekly *Template update* PR via `copier update` |

What was deliberately left out, and why, is on the wiki's
[Introduction](https://github.com/metalayerlab/project-template/wiki/Introduction#what-was-left-out) page.

## For AI assistants

Two different sets of instructions live in this repository:

| You are working on | Read | Then |
|---|---|---|
| **A project generated from this template** | that project's `AGENTS.md` (rendered from [template/AGENTS.md.jinja](template/AGENTS.md.jinja)) | its `docs/ai/prompts.md` and `docs/wiki/` |
| **This template itself** | [AGENTS.md](AGENTS.md) (Claude Code: [CLAUDE.md](CLAUDE.md)) | [layers/README.md](layers/README.md) and the [wiki](https://github.com/metalayerlab/project-template/wiki) |

In a generated project, each assistant finds its instructions where it looks for them, and all of them lead
to one file:

| Assistant | Entry point | Leads to |
|---|---|---|
| Claude Code | `CLAUDE.md` (+ `.claude/settings.json`) | `@AGENTS.md` |
| OpenAI Codex / ChatGPT with repo access | `AGENTS.md` | n/a |
| ChatGPT / Claude.ai chat without repo access | `docs/ai/prompts.md` → "Context for a chat assistant" | paste AGENTS.md |
| GitHub Copilot | `.github/copilot-instructions.md` (pointer + 3 critical rules) | AGENTS.md (the coding agent reads it natively) |
| Gemini CLI | `GEMINI.md` | `@./AGENTS.md` |
| Cursor | AGENTS.md, natively (`.cursor/rules/project.mdc` is a one-line pointer) | n/a |

How to run the AI-generate → human-review loop is on the wiki's
[Working with AI](https://github.com/metalayerlab/project-template/wiki/Working-with-AI) page.

## Documentation

The [wiki](https://github.com/metalayerlab/project-template/wiki) (source: [docs/wiki/](docs/wiki/)) covers
answering the questions, the project layout, CI, releases, images, contrib manifests, the project wiki
standard, working with AI, the review checklist, updating from the template, and migrating existing
projects.

## Developing the template

```sh
uv sync
uv run pytest             # renders every variant and runs its checks
uv run pytest -m docker   # also builds and runs each image
```

See [AGENTS.md](AGENTS.md) for the Jinja delimiters (`[[ ]]` / `[% %]`) and the rules. Changes are released
with release-please, and projects receive them through `copier update`.

## License

[Unlicense](LICENSE). Generated projects choose their own licence.
