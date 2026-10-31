# Working with AI

The template assumes most code is written by an AI assistant and every change is approved by a human. It gives the assistant precise rails, and gives the reviewer a checklist and checks they can rely on.

## Instruction files

`AGENTS.md` is the single source of instructions: the stack and exact commands, the repository map with owners, conventions, boundaries ("never do these"), the Definition of done, and the docs map. Each tool's own file points to it, so the instructions can't diverge:

| Assistant | Entry point | How it reaches AGENTS.md |
|---|---|---|
| Claude Code | `CLAUDE.md` | `@AGENTS.md` import, plus `.claude/settings.json`: check commands pre-allowed; edits to CHANGELOG, the manifest and the answers file denied; pushes to feature branches allowed (asked each time), but pushes naming `main`, force pushes, `git tag` and `gh release` denied (the `main` ruleset is the real guard); `.env`/`secrets/` unreadable |
| OpenAI Codex, ChatGPT with repo access | `AGENTS.md` | native |
| ChatGPT / Claude.ai chat, no repo access | `docs/ai/prompts.md` | the "Context for a chat assistant" prompt, then paste AGENTS.md |
| GitHub Copilot | `.github/copilot-instructions.md` | a pointer plus three critical rules; the coding agent reads AGENTS.md natively |
| Gemini CLI | `GEMINI.md` | `@./AGENTS.md` import |
| Cursor | AGENTS.md | native; `.cursor/rules/project.mdc` is a one-line pointer (no `@` import, so nothing loads twice) |

The README's "For AI assistants" section lists the same table for humans. Personal tweaks go in git-ignored files (`CLAUDE.local.md`, `.claude/settings.local.json`), never in the shared ones.

## The loop

1. **Design:** prompt 1 in `docs/ai/prompts.md`. The assistant writes a `docs/design/` record and stops. A human approves or corrects it. Rejected ideas go into `TODO.md` "Decided against", so they aren't proposed again.
2. **Build:** in small Conventional Commits, each passing the Definition of done (`ruff`, `mypy`, `pytest`, `gen-wiki --check`, `check-wiki`, `check-manifests`, and `check-docs-secrets` where Docker is available).
3. **Document:** the same PR updates the pages the docs map names, and replaces skeleton guidance with real text (prompt 4 audits the whole wiki).
4. **Review:** the PR template records how much was generated. A code owner reviews with the [Human Review Checklist](Human-Review-Checklist). Optionally, a second assistant reviews first (prompt 5).
5. **Release:** release-please's Release PR, also reviewed, is blocked until the wiki is complete.

## Context budget

Every assistant session pays for what it reads, so the AI-facing files are kept lean (design records [0002](https://github.com/metalayerlab/project-template/blob/main/docs/design/0002-context-budget.md) and [0006](https://github.com/metalayerlab/project-template/blob/main/docs/design/0006-context-budget-review.md)):

| Measure | Effect |
|---|---|
| AGENTS.md is terse: imperative rules and tables, the reasons in the wiki | ~1,500 tokens per session, for every tool |
| A "Don't read" list (lock file, CHANGELOG, caches, generated blocks), plus `Read` denies in `.claude/settings.json` | avoids one-off reads of 10k–40k tokens (`uv.lock` alone is ~37k) |
| `docs/design/README.md` indexes every record (CI-checked) | the assistant reads the index, not every record |
| Pointer files only point; the README's AI section is a table of entry points | no double loading in Cursor or Copilot |
| Template-owned wiki pages tell assistants whether to read on | fewer whole-page reads |
| `[context_budget]` in each project's `docs/wiki/.standard.toml`, enforced by `check-wiki.py` in project CI | AGENTS.md ≤ 9,000 characters, the pointer files 300–700. The template's own tests require the skeleton to use at most 75%, leaving room for the project |
| AGENTS.md, the review checklist and the Contributing page tell assistants and reviewers to keep it that way | the method carries on after the first commit |

## Keeping sessions small

The budget covers what an assistant reads first. Most of a session's tokens come later: command output, and the conversation itself, which is sent again with every turn ([design record 0007](https://github.com/metalayerlab/project-template/blob/main/docs/design/0007-terse-sessions.md)).

- **Quiet checks:** every Definition of done command prints one line when it passes, and its detail only when it fails. `check-wiki.py --verbose` lists the warnings it counts. A passing run of a fresh project's Definition of done prints about 6,450 characters without this. The template's tests fail if a template-owned check prints more than one line on a pass.
- **Terse replies:** AGENTS.md tells the assistant to give the result, then what it needs from the user, with no preamble, recaps or restated plans. That cuts form, not content: recommendations, reasons for non-obvious choices and what was skipped stay.
- **One task per session:** when a task is done and the next is unrelated, the assistant checks that the PR, `TODO.md` or a design record holds what the next session needs, then suggests starting one. It suggests this once, at the boundary, never mid-task. In Claude Code, `/clear` starts afresh and `/compact` summarises; other tools have their own equivalents.
- **Point, don't paste:** give the assistant a path or the failing check's name, not the log. It can read the file or rerun the check, and only reads what it needs.

## Guard rails

- **Checks the assistant can't talk its way past:** blocking CI, the coverage floor, mypy strict, the wiki standard, docs-touched, and PR-title linting.
- **Boundaries in AGENTS.md:** never edit release-owned or template-owned files, never weaken a check (no unexplained `noqa` or `type: ignore`, no skipped tests, no loosened sandbox), never commit secrets, never push to main or tag.
- **Supply chain:** dependencies must be justified, and checked to exist under exactly that name (typosquatting). The lock file pins them, and Dependabot updates them.
- **Honesty:** the assistant must say what it didn't run or isn't sure of. A claimed green check must have been run.
- **A recommendation with every question:** when the assistant asks the user something, including a design record's open questions, it says what it would choose and why. The user can then answer "yes" instead of asking for a recommendation first, and a weak reason is visible before it becomes a decision. The assistant still stops for the answer.
- **Lessons from every fix:** finishing a bug or enhancement, the assistant says what let it happen and what should change so it can't again (a test, a check, AGENTS.md, the template), or "none". The PR template's Lessons section asks human authors the same. A real lesson ends as an issue or a PR, not only prose. "None" is a fine answer: the point is to ask, not to invent one.
- **Human ownership:** CODEOWNERS plus a required review. `no-docs-needed` is a reviewer's label, and the assistant never adds it.
- **No AI credit in history:** the person who opens the PR is its author. `.claude/settings.json` sets `"attribution": {"commit": "", "pr": "", "sessionUrl": false}`, so Claude Code adds no `Co-authored-by` trailer, PR byline or session link, and AGENTS.md tells every other assistant the same. Set it in your user settings (`~/.claude/settings.json`) too, for repositories not made from the template; the old `includeCoAuthoredBy` setting is deprecated and ignored.
