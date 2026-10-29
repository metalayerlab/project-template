# Design records

Why the template is the way it is. Copy [0000-template.md](../../template/docs/design/0000-template.md) to
`NNNN-short-title.md` and add a line below. **Read this index first**, then only the records you need.

| # | Title | Status | Decision in one line |
|---|---|---|---|
| [0001](0001-template-architecture.md) | Template architecture | Approved | Copier, release-please, an agnostic core plus language layers, the wiki in each repo, one AGENTS.md |
| [0002](0002-context-budget.md) | Context budget for AI-facing files | Implemented | "Don't read" list, a design index, terse AGENTS.md, pointer-only tool files, a size budget enforced in every project's CI |
| [0003](0003-dependabot-automerge.md) | Dependabot auto-merge | Implemented | Opt-in: queue auto-merge on patch/minor Dependabot PRs; a code owner's approval still merges them, and no bot ever approves |
| [0004](0004-local-lint.md) | Run CI's markdownlint and gitleaks locally | Implemented | `scripts/check-docs-secrets.sh` runs both through Docker with CI's pins, and CI calls the same script so they can't drift |
