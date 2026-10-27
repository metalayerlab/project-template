# Project Wiki Standard

Every project keeps a thorough wiki, and CI holds it to one standard.

## Why in the repository

Before, each wiki was a separate `<name>.wiki` clone, edited and pushed by hand, and nothing checked it. Pages went missing, and docs drifted from the code. Now:

- **`docs/wiki/` is the source.** It is reviewed in the same PR as the code it describes.
- `wiki.yml` mirrors it **one way** to the GitHub wiki on every push to `main`. The GitHub wiki is a read-only view, and a footer on every page says so.
- AI assistants read `docs/wiki/` as context, and update it as part of every change.

## Required pages

Defined by `docs/wiki/.standard.toml` (template-owned), with the headings each page must keep:

| Page | Required headings | When |
|---|---|---|
| Home | Table of Contents | always |
| Introduction | What it is · How it works · When not to use it | always |
| Quick-Start | Prerequisites · Install · First run · Next steps | always |
| In-Depth-Configuration | Where configuration comes from · Settings · Secrets · Examples | service, cli |
| CLI-Reference | Commands · Exit codes | service, cli |
| HTTP-API-Reference | Endpoints · Authentication · Errors | service |
| API-Reference | Public API · Stability | library |
| Deployment | one per contrib target (Docker Compose · Kubernetes · systemd) · Upgrading | any contrib |
| Architecture-Internals | Overview · Components · Data flow · Design decisions | always |
| Security | Threat model · Secrets · Hardening · Reporting a vulnerability | always |
| Testing-Guide | Running the tests · Test layout · Writing tests | always |
| Release-Process | Versioning · How a release happens · Pre-releases and hotfixes | always (template-owned content) |
| Contributing | Development setup · Workflow · Code style · Working with AI assistants · Documentation | always |
| Troubleshooting | Diagnostics · Common problems | always |
| Frequently-Asked-Questions, `_Sidebar`, `_Footer` | (none) | always |

Headings are matched ignoring case, emoji and punctuation. Projects add their own pages freely: each just has to be linked from `_Sidebar.md`, under 📖 Core Concepts. The sidebar and footer keep the existing emoji layout: 📚 Getting Started, 📖 Core Concepts, 🔧 Configuration, 🔒 Security, 🆘 Help & Support, 🧑‍💻 For Developers, 🔑 Key Features.

Each page starts from a skeleton: the fixed headings, prefilled text where it is the same for every project (config precedence, hardening, release, contributing), and `<!-- guidance: ... -->` comments telling the author or the AI what belongs in each section.

## Checks

`scripts/check-wiki.py` (stdlib Python, template-owned), run by CI, by pre-commit, and as `python3 scripts/check-wiki.py` locally:

| Error (blocks the PR) | Warning (blocks a Release PR, via `--strict`) |
|---|---|
| A required page is missing, or a required heading was removed or renamed | An `<!-- guidance: -->` comment or `TODO(wiki)` marker remains |
| A page is not linked from `_Sidebar.md` | |
| A link to a missing page or `#anchor` | |
| A relative link to a repo path, which breaks once published (use a full URL) | |
| Unbalanced `generated:start`/`end` markers | |
| A `docs/design/NNNN-*.md` record missing from the index (`docs/design/README.md`) | |
| An always-loaded AI instruction file over `[context_budget]` (AGENTS.md 8,000 characters, pointer files 300–700) | |

markdownlint runs too, with line length, inline HTML and first-line-heading turned off.

## Generated sections

Reference tables come from the code, so they can't drift:

| Block | Page | Source |
|---|---|---|
| `settings` | In-Depth-Configuration | `config.SETTINGS`: key, env var, default, help, 🔒 for secrets |
| `cli` | CLI-Reference | the Typer app: commands, options, env vars, help |
| `http-api` | HTTP-API-Reference | the FastAPI OpenAPI schema: method, path, summary |

`uv run scripts/gen-wiki.py` rewrites them; CI runs it with `--check` and fails on any difference. Prose goes around the markers, never inside them.

## Keeping docs current

- **Docs touched:** a PR that changes a watched path (`config.py`, `cli.py`, `api.py`, `Dockerfile`, `contrib/**`) without changing `docs/wiki/` fails. When nothing user-visible changed, a **reviewer** adds the `no-docs-needed` label. The decision stays visible in review, and AI assistants are told never to add it.
- **Docs map:** each project's `AGENTS.md` maps code areas to the pages they affect, so the assistant knows what to update.
- **Release gate:** strict mode on the Release PR means nothing ships while skeleton guidance remains.
- **Changing the standard:** edit `template/docs/wiki/.standard.toml` and its skeleton page in project-template. Projects get it through `copier update`, and a new required heading fails their wiki check until they write it, which is the point.
