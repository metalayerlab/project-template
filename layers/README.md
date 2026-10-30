# Language layers

The template is a **language-agnostic core** plus one **layer** per language: `python` and `typescript`
(design record 0009). `none` is the layer for a language without one: every value is defined,
most of them empty (design record 0008). `tests/test_layers.py` enforces the boundary: core files may not contain
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

| Name | Python value | TypeScript value | Used in |
|---|---|---|---|
| `name`, `code_lang` | `Python`, `python` | `TypeScript`, `typescript` | docs, code-fence language |
| `release_type` | `python` | `node` | release-please-config.json |
| `version_file` | `pyproject.toml` | `package.json` | AGENTS.md boundaries and repository map |
| `install`, `add_dependency` | `uv sync`, `` `uv add <pkg>` (dev: …) `` | `npm ci`, `` `npm install <pkg>` (dev: …) `` | AGENTS.md |
| `lint`, `lint_fix`, `format`, `format_check`, `typecheck`, `test`, `test_integration` | `uv run ruff check` … | `npm run lint` … `npm test`, `npm run test:integration` | AGENTS.md stack table and Definition of done |
| `gen_wiki` | `uv run scripts/gen-wiki.py` | `node scripts/gen-wiki.ts` | AGENTS.md, wiki pages, PR template. The core appends `--check`, so it must take arguments |
| `run`, `install_cli`, `install_lib`, `import_snippet` | `uv run <name>`, `uv tool install git+…`, `uv add git+…`, `import <pkg>` | `npm start --`, `npm install -g github:…`, `npm install github:…`, `import { VERSION } from "<name>";` | README, Quick-Start |
| `public_api`, `suppressions` | `<pkg> (its __init__)`, `` `noqa`/`type: ignore` `` | `` `<name>` (`src/index.ts`) ``, `` `eslint-disable`/`@ts-expect-error` `` | API-Reference, AGENTS.md "Never" |
| `lock_file`, `deps_query`, `noread` | `uv.lock`, `uv tree --depth 1`, `.venv/` … | `package-lock.json`, `npm ls --depth 0`, `node_modules/` … | AGENTS.md "Don't read" |
| `config_file`, `cli_file`, `api_file` | `config.py`, `cli.py`, `api.py` | `config.ts`, `cli.ts`, `api.ts` | AGENTS.md docs map |
| `release_lock_note` | `. A follow-up job refreshes uv.lock…` | `''` (release-please bumps the lock too) | Release-Process |
| `runtime`, `base_image` | `Python`, `python` | `Node.js`, `node` | dependabot.yml (the base image's held-back updates) |
| `container_base`, `container_bin_dir`, `container_bin` | `python:3.13-slim`, `/opt/venv/bin`, … | `node:24-slim`, `/app/bin`, `/app/bin/<name>` | Dockerfile, docker/entrypoint.sh |
| `systemd_upgrade` | `` `uv pip install --python /opt/<name> …` `` | `` `npm install -g --prefix /opt/<name> …` `` | Deployment |

**Empty values.** A value may be `''` (or `[]` for `noread`) when the language has no such step. The core
guards every value that can be empty on the value itself, `[% if layer.typecheck %]…[% endif %]`, never on
`language`. `name`, `code_lang`, `release_type`, `version_file` and `test` are never empty: `test` is the
one command the Definition of done always runs.

### 2. Fragments, by area (paths relative to `layers/<lang>/`)

| Fragment | Into | Required |
|---|---|---|
| `ci/jobs.yml` | ci.yml: the test job(s) and the version/lock check | yes |
| `release/jobs.yml` | release-please.yml: extra jobs (Python: refresh `uv.lock` on the Release PR) | optional |
| `editorconfig` | .editorconfig: extra sections (TypeScript: 2-space `.ts`/`.js`, which Prettier reads) | optional |
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

- The manifest and lock (`pyproject.toml` + `uv.lock`, `package.json` + `package-lock.json`, via bootstrap), with the
  version field release-please bumps.
- The source skeleton with the config order `<PREFIX>_<KEY>_FILE` > env > file > default; the `version`,
  `config` and (for a service) `serve` commands; and `/healthz`, `/readyz`, `/version`.
- Tests with an 80% coverage floor: unit and integration split, integration opt-in.
- Formatting that doesn't depend on the answers: a long `project_name` or `description` must not make the
  formatter rewrite a file (TypeScript reads both from `package.json` at run time).
- `scripts/gen-wiki.*`, filling the `settings`, `cli` and `http-api` generated blocks, with `--check`.

### 4. Questions and tests

- Its questions in `copier.yml`, each with `when: "[[ language == '<lang>' ]]"`.
- Render variants in `tests/test_render.py` and `.github/workflows/template-ci.yml` (service, cli, library), and a
  `test_<lang>_checks` that runs the layer's Definition of done.

### Core tools every layer may assume

`python3` (stdlib: `check-wiki.py`, the personal-data guard), `uv`/`uvx` (Copier, pre-commit), `git`, `docker`.
The template's own tests also need each layer's toolchain: `node` >= 24 and `npm` for TypeScript.

## Adding a layer (Go, say)

1. Write a design record in the template's `docs/design/` and get it approved.
2. `cp -r layers/typescript layers/go` (or `python`), then rewrite every value and fragment.
   `uv run pytest tests/test_layers.py` tells you what's missing. Add its tools to `FORBIDDEN` there.
3. Add `Go: go` to the `language` choices in `copier.yml`, with its questions (`go_version`, …).
4. Add the gated whole files: `[% if language == 'go' %]go.mod[% endif %].jinja`, `src/` or its equivalent, tests,
   `gen-wiki`.
5. Add variants to the render tests and the template CI matrix. Render the other layers before and after: their
   output must not change. Document the layer on the wiki (Answering-the-Questions, Contributing-to-the-Template).
