# Design records

Why the template is the way it is. Copy [0000-template.md](../../template/docs/design/0000-template.md) to
`NNNN-short-title.md` and add a line below. **Read this index first**, then only the records you need.
A record that is Approved but not yet Implemented has its remaining work in the root
[`TODO.md`](../../TODO.md) or an issue.

| # | Title | Status | Decision in one line |
|---|---|---|---|
| [0001](0001-template-architecture.md) | Template architecture | Implemented | Copier, release-please, an agnostic core plus language layers, the wiki in each repo, one AGENTS.md |
| [0002](0002-context-budget.md) | Context budget for AI-facing files | Implemented | "Don't read" list, a design index, terse AGENTS.md, pointer-only tool files, a size budget enforced in every project's CI |
| [0003](0003-dependabot-automerge.md) | Dependabot auto-merge | Implemented | Opt-in: queue auto-merge on patch/minor Dependabot PRs; a code owner's approval still merges them, and no bot ever approves |
| [0004](0004-local-lint.md) | Run CI's markdownlint and gitleaks locally | Implemented | `scripts/check-docs-secrets.sh` runs both through Docker with CI's pins, and CI calls the same script so they can't drift |
| [0005](0005-extra-ports.md) | Extra listener ports | Implemented | Copier question `extra_ports` (list of ints, default `[]`): exposed by the image and published by compose and k8s; no diff when empty |
| [0006](0006-context-budget-review.md) | Context budget review | Implemented | Raise the AGENTS.md budget from 8,000 to 9,000 characters (skeleton ceiling 6,750), keep 75% headroom, and write down what a cut costs |
| [0007](0007-terse-sessions.md) | Terse sessions | Implemented | Definition of done checks print one line when they pass; `AGENTS.md` rules for terse replies and a new session per unrelated task; users point rather than paste |
| [0008](0008-no-language-layer.md) | A "None" language choice | Implemented | `language: none` renders the core only, through a `layers/none/` with empty values the core skips; one project-owned `scripts/check.sh` holds the project's checks |
| [0009](0009-typescript-layer.md) | TypeScript language layer | Implemented | One `typescript` layer (npm, Node's type stripping, ESLint + Prettier, tsc, vitest at 80%, Fastify, commander, `node:<v>-slim`); a front end is a later `kind: web`, not a layer |
| [0010](0010-repository-metadata.md) | Repository metadata | Implemented | A project-owned `.github/repository.toml` (description, homepage = the wiki, topics) applied with `scripts/repo-metadata.py` under the maintainer's `gh` login; CI warns on drift, never fails |
| [0011](0011-agent-git-permissions.md) | Agent git permissions | Implemented | The `main` ruleset protects `main`; `.claude/settings.json` lets agents push feature branches (asking each time) and denies pushes naming `main`, force pushes, tags and releases |
| [0012](0012-image-extras.md) | Optional extras in the image | Implemented | Copier question `image_extras` (Python with an image; list of names, `["*"]` for all, default `[]`): `--extra` flags on both builder `uv sync` lines; no diff when empty |
| [0013](0013-repository-boundary.md) | Repository boundary for agents | Implemented | Another codebase changes by an issue in its own repository: an `AGENTS.md` rule, a Claude Code hook that blocks edits outside the repository, dependency `Edit` denies, and a change-request issue form; no sandbox by default |
| [0014](0014-web-kind.md) | A `web` kind | Implemented | `kind: web` (TypeScript only): Vite + React 19, React Router 8 (data mode), run-time `/config.json`, same-origin `/api`, built by the Node builder and served by `nginx:1.30-trixie` as uid 1000 |
| [0015](0015-knowledge-kind.md) | A `knowledge` kind | Superseded by 0016 | `kind: knowledge` (`language: none` only): a notes repository keeps the agent guard rails and the secret scan, and drops releases, the wiki standard, design records and markdownlint; `README.md` is its project-owned map |
| [0016](0016-obsidian-layer.md) | An `obsidian` language layer | Implemented | `language: obsidian` (kind `brain`) supersedes 0015: the vault (`vault_dir`, default `knowledge`) is the wiki, design records are vault notes indexed by a Base, and Obsidian specifics move from the core to `layers/obsidian/` |
| [0017](0017-integration-ci-job.md) | An opt-in integration test job | Implemented | Copier questions `integration_ci` (Python; bool, default off) and `integration_extras` (list, `["*"]` for all): a CI job installs both package lists and the extras, runs the `integration` tests, and fails if none runs or one is skipped |
| [0018](0018-brain-pull.md) | Brain pull | Implemented | Opt-in `brain_pull` (obsidian only, default off): a daily workflow where a read-only Claude Code job updates the notes whose `repos:` changed and a separate write job enforces the vault scope and opens one PR; no secret, it skips |
