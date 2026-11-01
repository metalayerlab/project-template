# TODO

The template's own outstanding work. Bugs and features with discussion belong in GitHub issues; this file is
for what maintainers (and their AI assistants) should know at a glance. An Approved design record with work
left gets a line here or an issue.

## Open

- A thin `config.py` on interpose's settings engine (#84 part 2, [0020](docs/design/0020-thin-config-on-interpose.md)): blocked on interpose v0.1.0

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
- A `notes_dir` question letting code projects edit a notes vault directly: the boundary hook blocks it and it costs every project's budget; a brain pulls instead ([0015](docs/design/0015-knowledge-kind.md), kept by [0016](docs/design/0016-obsidian-layer.md))
- Markdownlint in a brain (`language: obsidian`): each vault's conventions decide its Markdown ([0016](docs/design/0016-obsidian-layer.md), from [0015](docs/design/0015-knowledge-kind.md))
- `docs/wiki/` or the GitHub wiki beside an Obsidian vault: the vault is the wiki ([0016](docs/design/0016-obsidian-layer.md))
- A stdlib-only vault check: frontmatter is YAML, so `check-vault.py` declares PyYAML inline ([0016](docs/design/0016-obsidian-layer.md))
- systemd for `kind: web`: a host's own nginx serves static files ([0014](docs/design/0014-web-kind.md))
- A `test:` list in `contrib/system-packages.txt` for the integration job: it installs the `runtime:` list too ([0017](docs/design/0017-integration-ci-job.md))
- A seeded project-owned `integration.yml` workflow: it would never receive fixes, so the job is in the template-owned `ci.yml` ([0017](docs/design/0017-integration-ci-job.md))
- Reusing `image_extras` for the integration job, or one list-valued `integration_ci`: the image and the tests can need different extras, and "off" needs its own value ([0017](docs/design/0017-integration-ci-job.md))
- Integration tests inside the Test job's matrix: they would count towards the coverage floor ([0017](docs/design/0017-integration-ci-job.md))
- Brain pull on by default for every brain: it spends Claude usage, needs a secret and a repository setting, and a brain without `repos:` notes gains nothing ([0018](docs/design/0018-brain-pull.md))
- Setting "Allow GitHub Actions to create and approve pull requests" from `repo-metadata.py`: CI's `GITHUB_TOKEN` can't read it, and it is a security choice for the maintainer ([0018](docs/design/0018-brain-pull.md))
- One Brain pull job holding a write token while Claude reads other repositories: Claude runs read-only and a second job checks its patch ([0018](docs/design/0018-brain-pull.md))
- Cloning sources' wikis for Brain pull subscriptions: template projects publish from `docs/wiki/`, so a path-filtered commits query is enough ([0019](docs/design/0019-brain-pull-subscriptions.md))
- Brain pull adding notes for a subscribed source no note covers: it opens an issue instead, keeping review to one PR a day ([0019](docs/design/0019-brain-pull-subscriptions.md))
