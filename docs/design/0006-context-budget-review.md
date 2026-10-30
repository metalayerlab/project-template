# 0006: Context budget review

Status: Implemented
Date: 2026-10-30
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

[0002](0002-context-budget.md) set every project's `AGENTS.md` budget at 8,000 characters, and the template's
tests let the rendered skeleton use at most 75% of it (6,000), leaving 2,000 for the project's own rules.

The skeleton has been at that ceiling from the start. The default render (a service project) measured:

| Commit | Change | Characters |
|---|---|---|
| `be647a9` | Initial template | 5,831 |
| `caed0b8` | No AI credit in commits and PRs (#15) | 5,914 |
| `f7dcc1e` | How to report a template problem (#26) | 5,866 |
| `f2f7957` | Local markdownlint and gitleaks (#29) | 5,922 |
| `4fa07aa` | A recommendation with every question (#35) | 5,926 |

The longest test variant reaches 5,965 with #36's lessons rule. Every rule added since the first commit was
paid for with cuts, and the cuts are running out. Where the 5,904 characters of a default render go, with #36:

| Section | Characters |
|---|---|
| Title and intro | 140 |
| How to work | 856 |
| Don't read | 360 |
| Stack and commands | 642 |
| Repository map | 995 |
| Conventions | 1,085 |
| Never | 744 |
| Definition of done | 341 |
| Docs map | 741 |

### What a cut costs

A cut is free when an assistant would do nothing differently without the text. In rising order of cost:

1. **Redundancy:** text that says again what another line already says.
2. **Anything CI enforces:** if it's forgotten, the check fails and its message teaches the rule.
3. **Reasons for rules that are already intuitive:** these can live in the wiki.
4. **Pointers:** without the link, the detail exists but is never found.
5. **A reason for a counter-intuitive rule:** without it, the rule is applied too literally or talked around.
6. **Specifics that differ from an assistant's defaults:** `uv run`, `typer.echo`, the config precedence.
   Without them, the assistant does what most repositories do.
7. **Triggers:** a rule without its "when" gets misapplied.
8. **Unenforced rules about behaviour:** stop for approval, never claim an unrun check passed. Nothing
   backs these up but a careful reviewer.

Categories 1–3 were spent on #26, #35 and #36. Nearly everything left is in 4–8.

### What the budget protects

8,000 characters is about 2,000 tokens, read in every session of every project. 0002 framed the budget as a
token cost, and at this size that cost is small next to what a session reads besides. The bigger cost is
attention: each rule competes with the others, and a long file buries the ones that matter most. The
budget's main job is to keep `AGENTS.md` short enough that every rule in it is read and acted on.

## Decision

1. **Raise the `AGENTS.md` budget from 8,000 to 9,000 characters**, in
   `template/docs/wiki/.standard.toml.jinja`. The skeleton's ceiling goes from 6,000 to 6,750, and a
   project's own room from 2,000 to 2,250. About 785 characters become free for the skeleton, enough for
   five one-line rules. The other budgets (`CLAUDE.md`, `GEMINI.md`, Cursor, Copilot) stay as they are: none
   is near its limit.
2. **Keep the 75% headroom** in `tests/test_render.py`, so projects keep a quarter of every budget.
3. **Write the cut categories down** in the template wiki's Contributing-to-the-Template page, as the test
   for any change to `template/AGENTS.md.jinja`. A PR that changes it states the characters added or freed,
   and the category of each cut.
4. **Review again when the skeleton reaches 6,750**, with a new record. Don't raise the budget
   piecemeal.

## Alternatives considered

- *Keep cutting:* what's left costs quality (categories 4–8), and nothing measures the loss.
- *Raise the headroom to 85% instead of the budget:* this takes the room from projects, which have their
  own rules to add.
- *A larger raise (10,000):* fewer reviews, but it removes the pressure that keeps the file terse, and the
  attention cost grows with every line.
- *Split `AGENTS.md` into per-area files loaded on demand* (0002's "revisit if outgrown"): fewer characters
  per session, but tools differ in how they find and load nested files. Assistants would miss rules without
  any signal.
- *Move the Repository map or the Docs map to the wiki behind a pointer:* a category 4 cut. Both tables are
  read on most tasks.

## Consequences

- Projects get the higher limit in their next update PR. `.standard.toml` is template-owned, and raising a
  limit can't fail a project's CI, so this is a `feat:`, not a breaking change.
- The skeleton's growth costs at most about 190 tokens more per session, and only as rules are added:
  raising the limit adds no text.
- Wiki pages that quote 8,000 change: Working-with-AI (Context budget) and Project-Wiki-Standard. 0002
  stays as the record of the original decision, with a line pointing here.
- The template repo's own `docs/wiki/.standard.toml` (`AGENTS.md` = 6000) covers this repository's
  `AGENTS.md`, not projects', and doesn't change.

## Resolved questions

1. **How much to raise it?** 9,000. It covers about five more rules and keeps the pressure that makes each
   line earn its place. 10,000 would postpone the next review but invite filler.
2. **Should the skeleton's share change?** No, it stays at 75%. Projects need room for their own rules,
   and 2,250 characters is not generous.
3. **Measure the effect of cuts on quality?** The method is described in Contributing-to-the-Template and
   used only for cuts in categories 4–8. It wasn't run for this raise: raising the limit changes no
   existing text, so there was nothing to compare.
