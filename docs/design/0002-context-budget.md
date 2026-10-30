# 0002: Context budget for AI-facing files

Status: Implemented (the AGENTS.md budget was raised to 9,000 by [0006](0006-context-budget-review.md))
Date: 2026-10-27
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Generated projects are written mostly by AI assistants, and every assistant session pays for what it
reads. A measurement of a rendered service project (about 4 characters per token):

| Source | When read | Before |
|---|---|---|
| `CLAUDE.md` + `AGENTS.md` | every session | ~1,950 tokens |
| `README.md` (its AI section restated AGENTS.md) | often, for orientation | ~1,040 (AI section ~450) |
| `uv.lock` | by accident, "to check versions" | ~37,000 |
| `CHANGELOG.md`, `docs/design/*` | grow without limit | unbounded |

Cursor and Copilot's coding agent read AGENTS.md natively *and* through their pointer files, so they paid
for parts of it twice. Nothing told assistants what not to read, and design records had no index.

## Decision

1. **A "Don't read" section** in AGENTS.md: the lock file (with the command to use instead), CHANGELOG
   (`git log`), tool caches, `.graphify/`, generated wiki blocks, and design records the index doesn't
   name. `.claude/settings.json` also denies `Read` on the lock file and caches. The layer supplies its own
   list (`layer.lock_file`, `layer.noread`, `claude/deny.json`). CHANGELOG is discouraged but not denied,
   because people do ask about it.
2. **A design index:** `docs/design/README.md` has one line per record. AGENTS.md says to read it first.
   `check-wiki.py` fails if a record isn't listed.
3. **A terse AGENTS.md:** imperative rules and tables, with the reasons left to the wiki. It went from
   ~1,800 to ~1,400 tokens with no rule removed.
4. **Pointer files are pointers:** the Cursor rule no longer `@`-imports AGENTS.md (Cursor loads it
   natively), Copilot's file keeps only the critical rules, and the README's AI section is a table of
   entry points.
5. **Template-owned wiki pages say whether assistants need them** (Release-Process, Contributing), in an
   HTML comment that published readers don't see.
6. **A budget enforced in every project:** `[context_budget]` in each project's template-owned
   `docs/wiki/.standard.toml` (AGENTS.md 8,000 characters; CLAUDE.md 600; Copilot 700; Cursor and Gemini 300),
   checked by `check-wiki.py` in project CI. The template's tests require the rendered skeleton to use at
   most 75% of each budget, leaving the rest for the project. The template repo has a budget of its own.
7. **The method is passed on:** each project's AGENTS.md says to add large or generated paths to "Don't
   read" (and the Claude denies) and to keep rules terse; its Contributing page explains why;
   `0000-template.md` points to the index; and the review checklist has an "AI instruction files" section.

## Alternatives considered

- *Denying `Read(CHANGELOG.md)`*: blocks legitimate questions like "what changed since 1.2?". Guidance is enough.
- *Splitting AGENTS.md into per-area files loaded on demand*: fewer tokens per session, but tools differ in
  how they load nested files, and one file is easier to review. Revisit if the budget is outgrown.
- *Dropping the reasons entirely*: they remain in the wiki for humans, and for assistants asked to explain a rule.

## Consequences

- Raising a budget in `template/docs/wiki/.standard.toml` needs a new design record: the cost recurs in
  every session of every project. Projects can't raise it locally: the file is template-owned.
- New layers must define `lock_file`, `deps_query` and `noread`, and provide `claude/deny.json`
  (`tests/test_layers.py` checks).
- Each new design record needs an index line, or the wiki check fails.
