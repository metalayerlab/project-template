# 0014: A `web` kind: a single-page app in a static image

Status: Approved
Date: 2026-10-31
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Record 0009 settled that a front end is a `kind`, not a layer: it uses the TypeScript toolchain, and what
differs is the project's shape. It left `kind: web` (a Vite + React SPA served from a static image) to its own
record, because it changes the core: the image, the health check, the deployment manifests and the wiki.

The archive (`/pool/distributed/arc/code`) has seven Vite + React SPAs from 2024–26:

| App | Served by | Runtime config | API |
|---|---|---|---|
| atomics client, two Foxie frontends | Firebase Hosting, `** → /index.html`, `/api/** →` a function | `VITE_*` at build time | same-origin `/api` (one), absolute `VITE_API_URL` (one) |
| Foxie dev (2026) | Firebase Hosting | `VITE_*`, default `http://localhost:5001/…` | separate origin |
| baqup webui | embedded in the Go binary | `window.APIUrl` templated into `index.html` | same-origin `/api/` |
| funders-db | GitHub Pages | a data file fetched at run time | none |
| andronics-io-ai | only the Vite dev server, in Docker | none | mocks |

Shared: React with `@vitejs/plugin-react`, vitest with jsdom and Testing Library, `jsx: react-jsx`,
react-router, Tailwind. What went wrong: `package.json` copied between repos (with a dependency on a sibling
directory that no longer exists), unused dependencies, dev and prod cache headers that disagree and an
`index.html` that is never marked no-cache, an API URL baked in at build time that defaults to localhost, and
one app with no production serving path at all. None had accessibility linting outside the Traefik fork, and
none ran end-to-end tests.

Constraints:

- Python, `none` and the existing TypeScript variants render **byte-for-byte** as before.
- The core stays language-neutral; `tests/test_layers.py` keeps policing it.
- The skeleton stays small and inside the context budget.

## Decision

### The questions

```yaml
kind:
  choices:
    # ...service, cli, library, other as now...
    "web: single-page app (Vite + React), served by nginx":
      value: web
      validator: "[% if language != 'typescript' %]Only with language: typescript[% endif %]"
```

`has_cli` stays `kind in ['service', 'cli']`, so a web project has no CLI and no `config.yaml`.

| Question | `web` |
|---|---|
| `port`, `health_path` | asked (`when: kind in ['service', 'web']`); defaults 8080 and `/healthz` |
| `container_image` | asked, default yes (the expression already gives that). No means `dist/` only, deployed by the project |
| `contrib` | asked; choices `docker` and `k8s`, default both. `systemd` is service-only (validator): a unit for static files is nginx's job, not ours |
| `extra_ports`, `puid_pgid`, `timezone` | not asked: one port, no state, no clock |

### The skeleton

| File | Owner | What |
|---|---|---|
| `index.html` | project | the shell: `<div id="root">`, `<script type="module" src="/src/main.tsx">` |
| `src/main.tsx` | project | loads the run-time config, then renders the router |
| `src/routes.tsx` | project | the route table (below): a layout with an error element, `/`, and a catch-all |
| `src/pages/` | project | `Home.tsx` (the name, version and API base URL) and `NotFound.tsx`. No data layer |
| `src/config.ts` | project | `SETTINGS` (name, type, default, description) and `loadConfig()`: fetch `/config.json`, fall back to defaults, a `ConfigError` on a wrong type. The same table shape as the server config, so `gen-wiki.ts` documents it |
| `public/config.json` | project | the defaults, `{"apiBaseUrl": "/api"}`. The deployment mounts its own over it |
| `tests/unit/routes.test.tsx`, `tests/unit/config.test.ts`, `tests/setup.ts` | project | Testing Library on jsdom, the real route table in `createMemoryRouter`; `fetch` stubbed |
| `vite.config.ts` | template | React plugin; `define` for the name and version from `package.json`, so the bundle carries two strings, not the manifest; the dev server proxies `/api` to `http://127.0.0.1:8080`; vitest's settings, at the same 80% floor |
| `docker/nginx.conf` | template | the server (below) |
| `docker/nginx-site.conf` | project | included inside the `server` block, empty but for comments: a CSP, extra headers, a `location` |

`tsconfig.json` becomes a template with a `web` branch: `jsx: react-jsx`, `lib` with `DOM`,
`moduleResolution: bundler`, `noEmit`, `allowImportingTsExtensions`. The strict settings and
`erasableSyntaxOnly` stay, so `scripts/gen-wiki.ts` still runs under Node's type stripping and imports
`src/config.ts`. `tsconfig.build.json`, `vitest.config.ts`, `src/index.ts` and the `prepare` script are not
rendered: nothing installs a web app as a package.

`package.json` gains `dev` (`vite`), `build` (`vite build`) and `preview` scripts, `react` and `react-dom` 19
and `react-router` 8 as dependencies, and `vite`, `@vitejs/plugin-react`, `jsdom`, `@testing-library/react`, `@types/react`,
`@types/react-dom` and `eslint-plugin-react-hooks` as dev dependencies. ESLint adds react-hooks'
recommended rules, and `no-console` applies everywhere in `src/`.

Runtime config is **a file read at run time**, not `VITE_*`: one image runs in every environment, and a
missing variable can no longer ship an app that points at localhost. The API is **same-origin `/api`**:
the ingress (Traefik, compose's reverse proxy) routes it to the service, and the dev server proxies it.

### Routing: React Router, data mode

The router is **React Router 8** (`react-router`; v8 needs React 19.2 or later), in **data mode**:

- One route table, `createBrowserRouter(routes)` in `src/main.tsx` and `<RouterProvider>` from
  `react-router/dom`. `src/routes.tsx` exports the table, so the tests render the same routes in
  `createMemoryRouter` and a page is never tested without its route.
- A root layout route with `<Outlet>` and an `errorElement`, so a thrown error or a failed loader shows a page,
  not a blank screen. A `*` route renders `NotFound`.
- History URLs (`/items/42`), not hash URLs: nginx's fallback serves `index.html` for any path that is not a
  file. `basename` is Vite's `import.meta.env.BASE_URL`, so a sub-path deployment changes one setting.
- The convention, in the layer's Code Style fragment: a route's data comes from its `loader`
  (`useLoaderData`), and a change from its `action`, not from `useEffect` + `fetch`. Loading and error states
  then belong to the router, and a project adds a cache library only when it needs one.
- Framework mode (React Router's Vite plugin, file routes, server rendering) is not used: that makes the
  project a server, which is a `service`.

### The image

The builder stage is the layer's, with a `web` branch: `npm ci`, `npm run build`, and `dist/` is the output.
The runtime stage is the official **`nginx:1.30-trixie`** (Debian, like `node:<v>-slim`; nginx 1.30.6 ships
`curl`, checked):

- A new layer value, `runtime_base`, names the runtime stage's image. It equals `container_base` for every
  layer and kind except TypeScript `web`, so other Dockerfiles render unchanged.
- The runtime fragment removes the stock site and `/docker-entrypoint.d/` scripts (they rewrite files under
  `/etc` at start, which a read-only root file system refuses), copies both nginx files and `dist/` to
  `/usr/share/nginx/html`.
- The core keeps its own steps: `runtime:` system packages, the uid 1000 user, `USER 1000:1000`. A new
  `kind == 'web'` branch at the end adds the `HEALTHCHECK` (`curl -fsS` on `health_path`), `EXPOSE`, and
  `CMD ["nginx", "-g", "daemon off;"]`.

`docker/nginx.conf`:

- `listen <port>`; the pid file and temp paths under `/tmp`, so uid 1000 and a read-only root work.
- `location = <health_path>` returns 200 without touching the file system.
- `/assets/` (Vite's hashed files): `Cache-Control: public, max-age=31536000, immutable`, and a missing one
  is a 404, never the fallback page (a stale tab would otherwise parse HTML as a script).
- `index.html`, `config.json` and the SPA fallback (`try_files $uri /index.html`): `no-cache`.
- `server_tokens off`, gzip, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`.
  No CSP by default: it depends on what the app loads, so it goes in `nginx-site.conf`.

### Deployment manifests

- compose: the port, `./config.json` mounted read-only over `/usr/share/nginx/html/config.json`; no volume.
- k8s: probes on `health_path`; `config.json` from a ConfigMap by `subPath`; an `emptyDir` on `/tmp`;
  `readOnlyRootFilesystem` stays true; no state volume.
- `docker-build.yml`'s smoke test runs for `web` too, and also checks that `/` returns the shell.

### CI and the layer

- `ci/jobs.yml`: for `web`, the import smoke test becomes `npm run build` and a check for `dist/index.html`.
- `agents/repo-map`, `wiki/components`, `wiki/docs-touched`, `wiki/dev-setup` (`npm run dev`) and the
  Quick-Start fragments gain `web` branches.
- `dependabot.yml` ignores nginx minor updates: odd minors are mainline, and moving to the next stable line
  is a template release.

### The wiki standard

A `web` project requires In-Depth-Configuration (gate: `has_cli or kind == 'web'`), with its settings
table generated from `src/config.ts`, and Deployment when `contrib` is set. No CLI or HTTP API reference.
AGENTS.md's Docs map row for a setting uses the same gate.

### Tests

- Variant `ts-web` (contrib `docker` and `k8s`) in `tests/test_render.py` and `template-ci.yml`;
  `test_typescript_checks` runs its Definition of done. `-m docker` builds the image and probes
  `health_path` and `/`.
- A test that `kind: web` is refused for `python` and `none`.

## Alternatives considered

- **Node serving `dist/` (Fastify with `@fastify/static`).** Reuses the service's config, health check and
  runtime stage. But it keeps a Node process and its dependencies in front of static files, and the image is
  several times larger. A project that needs a back end for its front end is a `service` that also serves
  files: its own change.
- **`nginxinc/nginx-unprivileged`.** Starts as uid 101, so the core's root steps (runtime packages, the
  uid 1000 user) would need `USER` switching around them. The official image with the core's user keeps the
  Dockerfile's shape.
- **Caddy, static-web-server, Alpine nginx.** Alpine or scratch images: no `apt`, so
  `contrib/system-packages.txt` can't work, and 0009 keeps one libc across layers.
- **Build-time `VITE_*` config.** What the archive did. One image per environment, and it caused the
  localhost default.
- **`window.__ENV__` written by an entrypoint (envsubst).** Needs a writable file system and a shell step at
  start. A mounted file needs neither.
- **TanStack Router.** Type-checks paths, params and search params, which React Router does only partly.
  But it is typed best with file routes and a code-generation plugin, its code-based routes are verbose, no
  archived project used it, and assistants know React Router far better. Revisit if typed search params matter.
- **React Router's declarative mode (`<BrowserRouter>`, `<Routes>`).** What the archive used (v6). No
  loaders, actions or error elements, and data mode costs the same lines.
- **wouter.** Tiny, but no loaders or error boundaries: each project would invent them.
- **Hash URLs (`HashRouter`, as baqup's webui).** For hosts with no fallback. Ours has one.
- **In the skeleton: TanStack Query, zustand, Tailwind, a component library, Storybook, msw, Playwright.** One
  project's choice, not a skeleton's. The archive listed TanStack Query and never used it.
- **`eslint-plugin-jsx-a11y`.** Its peer range stops at ESLint 9, and the layer is on 10. Add it when that
  changes.
- **`eslint-plugin-react-refresh`.** A hot-reload nicety, not a correctness check.
- **Firebase Hosting or GitHub Pages deploy.** Already decided against (0009). `container_image: false`
  leaves `dist/` for whatever the project uses.

## Consequences

- A front end gets the TypeScript guarantees (lock check, lint, format, type-check, 80% coverage) plus an
  image with a correct cache policy and run-time config. That fixes the archive's faults by construction.
- New projects only: `kind` can't be changed to `web` by `copier update` without rewriting `src/`.
- Two base images to track. Dependabot proposes nginx patch updates; a stable line change is ours.
- `tsconfig.json` becomes a template, and `layers/README.md` gains `runtime_base` for every layer.
- `feat:`, not breaking: no other variant's output changes.
- Wiki: Answering-the-Questions, CI-Pipeline, Docker-Images, Project-Layout, FAQ, Introduction.
- `AGENTS.md.jinja`: one gate changes; no characters for existing variants. The `ts-web` render is measured
  against the 6,750-character skeleton ceiling at implementation.

## Open questions

None. Resolved on review:

1. **nginx or Node to serve the files?** nginx: the job is static files, and a Node runtime is weight and
   attack surface with no work to do. Node earns its place only with a back end, which is a `service`.
2. **One `tsconfig.json` or Vite's app/node split?** One. Two files type-check browser code without Node's
   types, but at skeleton size that is more configuration than code; a project can split it later.
3. **Require In-Depth-Configuration for `web`?** Yes: `config.json` is the one thing a deployer must get
   right, and the table is generated, so the page costs a paragraph.
4. **systemd for `web`?** No: serving files on a host is the host's nginx, configured by whoever runs it.
5. **A router in the skeleton?** Yes, as a standard rather than each project's choice: React Router 8 in
   data mode (above).
