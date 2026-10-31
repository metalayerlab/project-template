# TODO

The template's own outstanding work. Bugs and features with discussion belong in GitHub issues; this file is
for what maintainers (and their AI assistants) should know at a glance. An Approved design record with work
left gets a line here or an issue.

## Open

- [ ] `kind: web`, a Vite + React SPA in a static image, `typescript` only: needs its own design record
  (design [0009](docs/design/0009-typescript-layer.md))
- [ ] A `description` containing `"` breaks rendering: `pyproject.toml` (and probably `package.json`) puts it in a
  string unescaped. Use `| tojson` wherever it's rendered, and give one test variant a quoted description

## Decided against (don't re-propose without reading this first)

<!-- One line each: the idea, why not, and a link to the issue, PR or design record. -->

- A separate front-end language layer (`typescript-frontend`): same toolchain, different shape, so it is a `kind` ([0009](docs/design/0009-typescript-layer.md))
- Express, Hono, Biome, tsx, pnpm/yarn, a bundler, Jest or semantic-release in the TypeScript layer ([0009](docs/design/0009-typescript-layer.md))
- Denying every `git push` to agents: the `main` ruleset already guards `main`, so agents push feature branches ([0011](docs/design/0011-agent-git-permissions.md))
- Firebase deploy, Storybook, Chrome extensions, Electron or npm workspaces in the skeleton: one project's choice, not a skeleton's ([0009](docs/design/0009-typescript-layer.md))
