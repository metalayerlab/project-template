# TODO

The template's own outstanding work. Bugs and features with discussion belong in GitHub issues; this file is
for what maintainers (and their AI assistants) should know at a glance. An Approved design record with work
left gets a line here or an issue.

## Open

Nothing open: new work starts as an issue or a design record.

## Decided against (don't re-propose without reading this first)

<!-- One line each: the idea, why not, and a link to the issue, PR or design record. -->

- A separate front-end language layer (`typescript-frontend`): same toolchain, different shape, so it is a `kind` ([0009](docs/design/0009-typescript-layer.md))
- Express, Hono, Biome, tsx, pnpm/yarn, a bundler, Jest or semantic-release in the TypeScript layer ([0009](docs/design/0009-typescript-layer.md))
- Denying every `git push` to agents: the `main` ruleset already guards `main`, so agents push feature branches ([0011](docs/design/0011-agent-git-permissions.md))
- A project-owned `contrib/image-extras.txt` for the image's Python extras: a Copier answer renders them with no parsing and no conflicts ([0012](docs/design/0012-image-extras.md))
- Claude Code's sandbox on by default, to confine Bash to the project: it also blocks the `uv` cache, Docker and `gh` login ([0013](docs/design/0013-repository-boundary.md))
- Firebase deploy, Storybook, Chrome extensions, Electron or npm workspaces in the skeleton: one project's choice, not a skeleton's ([0009](docs/design/0009-typescript-layer.md))
- Node (Fastify) serving a `web` app's files, or Caddy/Alpine/unprivileged nginx images: the official Debian nginx with the core's uid 1000 user ([0014](docs/design/0014-web-kind.md))
- Build-time `VITE_*` config or an entrypoint-written `window.__ENV__` for a `web` app: a mounted `/config.json` read at run time ([0014](docs/design/0014-web-kind.md))
- TanStack Router, wouter, hash URLs or React Router's declarative/framework modes: React Router in data mode ([0014](docs/design/0014-web-kind.md))
- TanStack Query, zustand, Tailwind, Storybook, msw or Playwright in the `web` skeleton: one project's choice ([0014](docs/design/0014-web-kind.md))
- systemd for `kind: web`: a host's own nginx serves static files ([0014](docs/design/0014-web-kind.md))
