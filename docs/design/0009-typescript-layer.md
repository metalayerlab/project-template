# 0009: TypeScript language layer

Status: Implemented
Date: 2026-10-30
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Record 0001 names TypeScript/Node as the layer after Python ([#47](https://github.com/metalayerlab/project-template/issues/47)).
The issue left the toolchain open, so this record settles it from what we have actually built. The archived
projects (`/pool/distributed/arc/code`) contain 28 with TypeScript. The ten from 2025–26 count most. The older
ones (2019–22: Create React App, tslint, webpack, yarn) show a toolchain we have since dropped.

| Shape | Projects | Stack |
|---|---|---|
| Library | ebay-client, charities-uk-client, lib-queue, foxie `types` | tsup ESM + `.d.ts`, vitest + v8 coverage, ESLint flat + typescript-eslint, `tsc --noEmit`, semantic-release + husky + commitlint |
| Component library | atom-ui, andronics-io-ui, foxi-systems-ui, atomics/ui | Vite library mode, React, Tailwind, Storybook, vitest + Testing Library |
| Web app (SPA) | atomics/client, foxie frontend, baqup webui, andronics-io-ai | Vite, React, react-router, TanStack Query, zod; static files deployed to Firebase Hosting |
| Service | unified-server, deluge-jrpc-proxy, Firebase functions | Express (or Koa), pino, zod, `/health/live`; a multi-stage `node:20-alpine` image as a non-root user |
| CLI | spider, audit, foxie import scripts | commander, ts-node or tsx |

What they share: npm with `package-lock.json` (yarn before 2025, and two repos had both lock files), vitest
(jest before 2025, and many repos had `"test": "echo no test specified"`), `strict: true`, ESM, ESLint with
typescript-eslint, zod. What went wrong is what the template already fixes: release and commit tooling
copied by hand into each repo, missing tests, mixed lock files and ad hoc deploy scripts.

Constraints:

- Python and `none` variants render **byte-for-byte** as before.
- The core stays language-neutral, and `tests/test_layers.py` polices it for TypeScript too.
- The skeleton stays small (AGENTS.md: a skeleton, not a framework) and inside the context budget.

## Decision

### One layer, `typescript`; a front end is a `kind`

A layer is a **toolchain**: install, lint, format, type-check, test, the lock check, the Dependabot ecosystem,
the base image. A front end uses the same toolchain as a TypeScript service, so it is not a second layer.
What differs is the project's **shape** (which source files, which wiki pages, what the image runs, the
health check), and that is what `kind` already decides.

- This record: `layers/typescript/` with `kind` `service`, `cli` and `library`.
- A later record: `kind: web` (a Vite + React SPA served from a static image), limited to `typescript` by a
  validator, as `kind: other` is limited to `none` (0008). It changes the core, not just the layer, so it
  gets its own record.

### The questions

```yaml
language:
  choices:
    Python: python
    "TypeScript: Node.js and npm": typescript
    "None: core only (no build, tests or image)": none

node_version:
  type: str
  help: Minimum Node.js version (Docker base image and the first CI matrix entry)
  choices: ["24", "26"]
  default: "24"
  when: "[[ language == 'typescript' ]]"
```

The LTS lines today are 22 (maintenance), 24 (active) and 26 (LTS since October 2026). 22 is left out: it
reaches end of life in April 2027, and Node 24 is needed for `import.meta.main`.

The npm package name is `project_name`, unscoped; `package_name` stays Python-only. The `kind` labels name
both frameworks ("FastAPI / Fastify", "Typer / commander").

### Toolchain

| Concern | Choice |
|---|---|
| Package manager | npm. `npm ci` fails when `package-lock.json` is out of step with `package.json`: the lock check |
| Running TypeScript | **Node's type stripping**, no tsx: `node src/cli.ts`, `node scripts/gen-wiki.ts`. So erasable syntax only (`erasableSyntaxOnly`, `verbatimModuleSyntax`), and imports name the `.ts` file (`rewriteRelativeImportExtensions` turns them into `.js` in `dist/`) |
| Language settings | ESM (`"type": "module"`), `module`/`moduleResolution: nodenext`, `strict`, `noUncheckedIndexedAccess`, target ES2024 |
| Compiler | TypeScript `~6.0`: typescript-eslint supports `<6.1`, so 7.x waits for it |
| Lint | ESLint flat config: `@eslint/js` recommended, typescript-eslint `strictTypeChecked`, `no-console` outside the CLI, scripts and tests, `--max-warnings 0` |
| Format | Prettier, width 100 (as ruff), `**/*.{ts,js}` only: the wiki and workflows belong to markdownlint and the template |
| Type-check | `tsc --noEmit` over `src/`, `tests/`, `scripts/` and the config files |
| Build | `tsc -p tsconfig.build.json` to `dist/` (JS, `.d.ts`, source maps), every kind; `prepare` runs it, so installs from GitHub build |
| Tests | vitest with `@vitest/coverage-v8`: 80% lines, branches, functions and statements. `tests/unit/` by default; `tests/integration/` only with `RUN_INTEGRATION=1` (`npm run test:integration`) |
| Service | Fastify 5, `fastify-type-provider-zod` and `@fastify/swagger`. One zod schema validates the request, types the handler and documents the route. The CLI's `serve` closes the server on SIGINT/SIGTERM (Node as PID 1 ignores them otherwise) |
| CLI | commander. `main()` returns the exit code: 2 for a `ConfigError`, as in Python |
| Config | `src/config.ts`: the same four sources and `SETTINGS` table as `config.py`, YAML through `yaml`. Plain TypeScript, not zod: the coercion rules are the Python ones, and a CLI needs no zod |
| Name and version | `NAME`, `VERSION` and `DESCRIPTION` in `src/index.ts`, read from `package.json` at run time |
| Release | release-please, `release_type: node`. It bumps `package.json` and `package-lock.json` together, so no lock follow-up job |
| Image | `node:<node_version>-slim`, multi-stage: `npm ci --ignore-scripts`, build, `npm prune --omit=dev`, and `/app/bin/<name>` linking to `dist/cli.js`. The base image's own uid 1000 user, `node`, is removed for the project's |

### Layer values (`layers/typescript/layer.jinja`)

| Value | TypeScript |
|---|---|
| `name`, `code_lang`, `release_type`, `version_file` | `TypeScript`, `typescript`, `node`, `package.json` |
| `install`, `add_dependency` | `npm ci`, `` `npm install <pkg>` (dev: `npm install -D <pkg>`) `` |
| `lint`, `lint_fix` | `npm run lint`, `npm run lint -- --fix` |
| `format`, `format_check` | `npm run format`, `npm run format:check` |
| `typecheck`, `test`, `test_integration` | `npm run typecheck`, `npm test`, `npm run test:integration` |
| `gen_wiki` | `node scripts/gen-wiki.ts` (the core appends `--check`, which an `npm run` script would swallow) |
| `run`, `install_cli`, `install_lib`, `import_snippet` | `npm start --`, `npm install -g github:<owner>/<name>`, `npm install github:<owner>/<name>`, `import { VERSION } from "<name>";` |
| `public_api`, `suppressions` | `` `<name>` (`src/index.ts`) ``, `` `eslint-disable`/`@ts-expect-error` `` |
| `lock_file`, `deps_query`, `noread` | `package-lock.json`, `npm ls --depth 0`, `node_modules/`, `dist/`, `coverage/` |
| `config_file`, `cli_file`, `api_file` | `config.ts`, `cli.ts`, `api.ts` |
| `release_lock_note` | `''` |
| `runtime`, `base_image` | `Node.js`, `node` |
| `container_base`, `container_bin_dir`, `container_bin` | `node:<node_version>-slim`, `/app/bin`, `/app/bin/<name>` |
| `systemd_upgrade` | `` `npm install -g --prefix /opt/<name> github:<owner>/<name>#vX.Y.Z` `` |

### Core changes, none of which changes a Python or `none` render

- Four new layer values replace Python wording in core files: `public_api` (API-Reference), `suppressions`
  (AGENTS.md "Never"), `runtime` and `base_image` (dependabot.yml's held-back base image).
- `.editorconfig` becomes a template with an optional `editorconfig` fragment. TypeScript's sets 2-space
  `.ts`/`.js`, because Prettier reads `.editorconfig` and the core says 4.

### Gated whole files

`package.json`, `tsconfig.json`, `tsconfig.build.json`, `eslint.config.js`, `.prettierrc.json`,
`vitest.config.ts`, `src/`, `tests/` and `scripts/gen-wiki.ts`, each gated on `language == 'typescript'` in
its name. `src/` mirrors Python's: `index.ts`, plus `config.ts` and `cli.ts` (`version`, `config`, and
`serve` for a service) when `has_cli`, plus `api.ts` for a service: `createApp()` with `/healthz`, `/readyz`
and `/version`. `tests/setup.ts` hides the developer's own `<PREFIX>*` variables from every test, and
`tests/helpers.ts` writes config files. Ownership matches Python: `src/**` and `tests/**` are in
`_skip_if_exists`; `package.json` and the tool configs are not, as `pyproject.toml` is not.

`gen-wiki.ts` fills the same three blocks as `gen-wiki.py`: settings from `SETTINGS`, the CLI reference from
the commander program, and the HTTP API reference from `createApp().swagger()`. The tests call
`app.inject()`, so only `serve`'s test opens a port, on loopback.

The rendered sources are Prettier-clean whatever the answers: the name and description come from
`package.json` at run time, and tests build environment names from `ENV_PREFIX`, so a long answer doesn't
change how a line wraps.

The health check runs `node -e` with the built-in `fetch`, because the slim image has no curl.

### Tests

- Variants `ts-service` (with `puid_pgid` and an extra port), `ts-cli` (`node_version: 26`) and `ts-library`
  in `tests/test_render.py` and `template-ci.yml` (which adds `actions/setup-node`).
  `test_typescript_checks` runs the layer's Definition of done, `npm ci`, the integration run, the import
  smoke test and `npm start -- version`. The existing tests cover the rest (the wiki, the context budget,
  manifests, actionlint, the sub-command reference), and `-m docker` builds each image and probes it.
- `FORBIDDEN["typescript"]` in `test_layers.py`: `npm ci/run/test/install`, `npx`, `node_modules`, `vitest`,
  `eslint`, `prettier`, `tsc`, `tsconfig`, `node:<v>-slim`.

## Alternatives considered

- **A `typescript-frontend` layer, or sub-layers.** It would copy about 25 fragments to change three or four
  values, and every core fix would need making twice. A front end differs in shape, not toolchain: `kind`.
- **Name the layer `node`** (the issue's name). The question asks for a language, and plain JavaScript is not
  offered. `node` survives as `release_type` and in `node_version`.
- **Express.** We know it best, but it has no OpenAPI, so the HTTP API reference would need a hand-kept spec
  or a second registration per route that can drift. Tests need supertest, `req.body` is `any`, and logging
  needs pino-http. Fastify does all of this with four packages.
- **Hono.** Small, and `@hono/zod-openapi` matches Fastify's single definition. But it needs an adapter on Node
  and its ecosystem is thinner. Reconsider if edge runtimes matter.
- **Biome instead of ESLint + Prettier.** One tool, like ruff. Our repos and the assistants know ESLint
  best, and typescript-eslint's type-aware rules have no full Biome equivalent yet.
- **tsx (the first draft of this record).** One more dependency to do what Node 24 does itself.
- **pnpm or yarn.** No archived project needs them, and npm ships in the image. Mixed lock files were one of
  the archive's faults.
- **tsup or another bundler.** `tsc` emits ESM and `.d.ts` files. A bundler is one more tool for no gain on Node.
- **Jest.** Every 2025–26 project moved to vitest, which runs TypeScript and ESM without configuration.
- **semantic-release, husky, commitlint.** The core already has release-please, the PR-title lint and pre-commit.
- **Alpine images.** Python uses `-slim`. One libc across layers keeps the Docker fragments alike.
- **In the skeleton: Firebase deploy, Storybook, Chrome extensions, Electron, npm workspaces.** Each is one
  project's choice, not a skeleton's.

## Consequences

- A TypeScript project gets the same guarantees as a Python one: a lock check, lint, format, type-check, an
  80% coverage floor, generated reference pages, an image and its health check.
- Its CI still needs `python3` for the core's stdlib `check-wiki.py` and the pre-commit framework. Ubuntu
  runners ship it. The template's own tests now need Node.js >= 24 and npm.
- `copier update` reaches the layer's template-owned files (`package.json`, `tsconfig*.json`, the lint and
  test configs). A project that edits them takes conflicts, as Python's do with `pyproject.toml`.
- A project can move between `python` and `typescript` only by rewriting `src/` and `tests/`. Copier does
  not translate code.
- TypeScript 7 waits for typescript-eslint. Dependabot will propose it; the PR fails until support lands.
- This is a `feat:` change, not breaking: the default and the Python and `none` output are unchanged.
- Wiki: Answering-the-Questions, CI-Pipeline, Contributing-to-the-Template, Docker-Images, FAQ, Introduction,
  Project-Layout, Release-Process, Updating-from-the-Template. `layers/README.md` gains a TypeScript column.
- `AGENTS.md.jinja` changes by one value (`suppressions`): no characters for Python. A TypeScript service's
  rendered `AGENTS.md` is 6,353 characters, under the 6,750 skeleton ceiling.

## Open questions

None. Resolved on review:

1. **Publish libraries to npm?** Not yet: install from GitHub (`prepare` builds), as Python installs from git.
   A registry needs a token and a scope decision, so it gets its own record if wanted. `package.json` is
   `"private": true` until then.
2. **The CI Node matrix:** the LTS lines from `node_version` to 26. Odd-numbered releases are short-lived.
