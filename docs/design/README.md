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
