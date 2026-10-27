# Language layers

The template is a **language-agnostic core** plus one **layer** per language. Python is the only layer so
far, and TypeScript/Node is next. `tests/test_layers.py` enforces the boundary: core files may not contain
language tooling, and every layer must provide everything the core asks for.

## Where things live

| Kind | Where | Example |
|---|---|---|
| **Core**: identical for every language | `template/` | release-please, Docker build/cleanup, PR-title lint, secret scan, the wiki standard and checker, `contrib/`, AI files, issue/PR templates |
| **Layer interface**: named values the core reads | `layers/<lang>/layer.jinja` | `layer.test` = `uv run pytest`, `layer.container_base` = `python:3.13-slim` |
| **Layer fragments**: language-specific blocks the core includes | `layers/<lang>/<area>/*.jinja` | `ci/jobs.yml.jinja` (the CI test jobs), `docker/builder.Dockerfile.jinja` |
| **Layer files**: whole files that exist only for one language | `template/`, gated in the *name*: `[% if language == 'python' %]src[% endif %]/` | `pyproject.toml`, `src/`, `tests/`, `scripts/gen-wiki.py` |

Why are whole layer files still under `template/`? Copier renders one tree, and a file's output path is its
path under `template/`. Fragments can live anywhere, because Jinja resolves `include` and `import` from the
repository root, and `layers/` itself is never rendered into a project.

### How the core uses a layer

At the top of a core file:

```jinja
[% import 'layers/' ~ language ~ '/layer.jinja' as layer with context %]
```

then values with `[[ layer.test ]]`, and blocks with:

```jinja
[% include 'layers/' ~ language ~ '/ci/jobs.yml.jinja' %]                  [#! required !#]
[% include 'layers/' ~ language ~ '/release/jobs.yml.jinja' ignore missing %]   [#! optional hook !#]
```

Fragments see the same context, `layer` included.

## The contract

A layer `layers/<lang>/` provides:

### 1. `layer.jinja`: every name below, defined with `[% set name = ... %]`

| Name | Python value | Used in |
|---|---|---|
| `name`, `code_lang` | `Python`, `python` | docs, code-fence language |
| `release_type` | `python` | release-please-config.json |
| `version_file` | `pyproject.toml` | AGENTS.md boundaries and repository map |
| `install`, `add_dependency` | `uv sync`, `` `uv add <pkg>` (dev: …) `` | AGENTS.md |
| `lint`, `lint_fix`, `format`, `format_check`, `typecheck`, `test`, `test_integration` | `uv run ruff check` … | AGENTS.md stack table and Definition of done |
| `gen_wiki` | `uv run scripts/gen-wiki.py` | AGENTS.md, wiki pages, PR template |
| `run`, `install_cli`, `install_lib`, `import_snippet` | `uv run <name>`, `uv tool install git+…`, `uv add git+…`, `import <pkg>` | README, Quick-Start |
| `config_file`, `cli_file`, `api_file` | `config.py`, `cli.py`, `api.py` | AGENTS.md docs map |
| `release_lock_note` | `. A follow-up job refreshes uv.lock…` (may be `''`) | Release-Process |
| `container_base`, `container_bin_dir`, `container_bin` | `python:3.13-slim`, `/opt/venv/bin`, … | Dockerfile, docker/entrypoint.sh |
| `systemd_upgrade` | `` `uv pip install --python /opt/<name> …` `` | Deployment |

### 2. Fragments, by area (paths relative to `layers/<lang>/`)

| Fragment | Into | Required |
|---|---|---|
| `ci/jobs.yml` | ci.yml: the test job(s) and the version/lock check | yes |
| `release/jobs.yml` | release-please.yml: extra jobs (Python: refresh `uv.lock` on the Release PR) | optional |
| `dependabot.yml` | dependabot.yml: the package ecosystem | yes |
| `pre-commit/hooks.yaml` | .pre-commit-config.yaml: lint, format, typecheck and gen-wiki hooks | yes |
| `bootstrap.sh` | scripts/bootstrap.sh: lock, then fill the generated wiki sections | yes |
| `claude/allow.json` | .claude/settings.json: allow-listed commands | yes |
| `docker/builder.Dockerfile`, `docker/runtime.Dockerfile`, `docker/healthcheck.Dockerfile` | Dockerfile stage 1, the runtime install, the HEALTHCHECK command | yes |
| `ignore/gitignore`, `ignore/dockerignore` | the language's ignore entries | yes |
| `agents/stack-intro.md`, `agents/repo-map.md`, `agents/conventions.md` | AGENTS.md | yes |
| `copilot.md`, `ai/stack-summary.txt`, `readme/development.md` | Copilot instructions, the chat prompt, README | yes |
| `systemd/install-comment`, `systemd/notes-comment` | the systemd unit's header | yes |
| `wiki/*.md`, `wiki/docs-touched.toml`, `wiki/deploy-systemd-install.sh` | wiki skeleton pages; `.standard.toml` watched paths | yes |

### 3. Whole files in `template/`, gated by `language`

- The manifest and lock (`pyproject.toml` + `uv.lock` via bootstrap), with the version field release-please bumps.
- The source skeleton with the config order `<PREFIX>_<KEY>_FILE` > env > file > default; the `version`,
  `config` and (for a service) `serve` commands; and `/healthz`, `/readyz`, `/version`.
- Tests with an 80% coverage floor: unit and integration split, integration opt-in.
- `scripts/gen-wiki.*`, filling the `settings`, `cli` and `http-api` generated blocks, with `--check`.

### 4. Questions and tests

- Its questions in `copier.yml`, each with `when: "[[ language == '<lang>' ]]"`.
- Render variants in `tests/test_render.py` and `.github/workflows/template-ci.yml` (service, cli, library).

### Core tools every layer may assume

`python3` (stdlib: `check-wiki.py`, the personal-data guard), `uv`/`uvx` (Copier, pre-commit), `git`, `docker`.

## Adding a layer (Node, say)

1. Write a design record in the template's `docs/design/` and get it approved.
2. `cp -r layers/python layers/node`, then rewrite every value and fragment for Node.
   `uv run pytest tests/test_layers.py` tells you what's missing.
3. Add `Node: node` to the `language` choices in `copier.yml`, with Node's questions (`node_version`, …).
4. Add the gated whole files: `[% if language == 'node' %]package.json[% endif %].jinja`, `src/`, `tests/`, `gen-wiki`.
5. Add Node variants to the render tests and the template CI matrix. Document the layer on the wiki
   (Answering-the-Questions, Contributing-to-the-Template).
