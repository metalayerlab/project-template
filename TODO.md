# TODO

The template's own outstanding work. Bugs and features with discussion belong in GitHub issues; this file is
for what maintainers (and their AI assistants) should know at a glance. An Approved design record with work
left gets a line here or an issue.

## Open

- [ ] `kind: web`, a Vite + React SPA in a static image, `typescript` only: needs its own design record
  (design [0009](docs/design/0009-typescript-layer.md))

## Decided against (don't re-propose without reading this first)

<!-- One line each: the idea, why not, and a link to the issue, PR or design record. -->

- A separate front-end language layer (`typescript-frontend`): same toolchain, different shape, so it is a `kind` ([0009](docs/design/0009-typescript-layer.md))
- Express, Hono, Biome, tsx, pnpm/yarn, a bundler, Jest or semantic-release in the TypeScript layer ([0009](docs/design/0009-typescript-layer.md))
- Denying every `git push` to agents: the `main` ruleset already guards `main`, so agents push feature branches ([0011](docs/design/0011-agent-git-permissions.md))
- A project-owned `contrib/image-extras.txt` for the image's Python extras: a Copier answer renders them with no parsing and no conflicts ([0012](docs/design/0012-image-extras.md))
- Claude Code's sandbox on by default, to confine Bash to the project: it also blocks the `uv` cache, Docker and `gh` login ([0013](docs/design/0013-repository-boundary.md))
- Firebase deploy, Storybook, Chrome extensions, Electron or npm workspaces in the skeleton: one project's choice, not a skeleton's ([0009](docs/design/0009-typescript-layer.md))
