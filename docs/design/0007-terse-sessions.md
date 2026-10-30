# 0007: Terse sessions

Status: Implemented
Date: 2026-10-30
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

[0002](0002-context-budget.md) and [0006](0006-context-budget-review.md) limit what an assistant reads at the
start of a session. Most of a session's tokens come from what happens after it starts:

| Source | Controlled today? |
|---|---|
| Instruction files (`AGENTS.md` and the tool files) | Yes: `[context_budget]` |
| Tool results: command output, file reads | Partly: "Don't read" |
| Conversation history: each turn is sent again with every later turn | No |
| Assistant replies: output costs more than input, and each one becomes history | No |
| User messages: pasted logs and files | No |

The project's own Definition of done is a large tool result, and an assistant runs it several times per
task. On a fresh service project, one passing run prints about 6,450 characters (about 1,600 tokens):

| Command | Output when it passes |
|---|---|
| `python3 scripts/check-wiki.py` | 28 lines, 2,770 characters: one warning per unwritten placeholder |
| `uv run pytest` | 30 lines, 1,941 characters: header, per-file progress, coverage table |
| `scripts/check-docs-secrets.sh` | 16 lines: gitleaks' ASCII-art banner and colour codes |
| `scripts/check-manifests.sh` | 6 lines |
| ruff, ruff format, mypy, `gen-wiki.py --check` | 1 line each |

## Decision

1. **Quiet when they pass.** Every Definition of done command prints one line when it passes, and its
   detail only when it fails:
   - `check-wiki.py` prints a count of its warnings (`wiki OK (27 warnings; --verbose lists them)`) and
     lists them only with `--verbose`. Errors, and warnings promoted to errors by `--strict`, are always
     listed in full.
   - The Python layer's pytest options add `-q`, and change the coverage report to
     `term-missing:skip-covered`. A coverage failure still names the files and lines that are missing.
   - `check-manifests.sh` and `check-docs-secrets.sh` capture each tool's output, print it in full only if
     the tool fails, and end a pass with one summary line (what was checked, and what was skipped as not
     installed). gitleaks' banner and colour codes are turned off, so a failure stays readable.
   - The template's tests assert that each template-owned check prints one line when it passes, so new
     output can't creep back in.
2. **Two rules** in `template/AGENTS.md.jinja`, How to work:
   - item 8: "Reply tersely: the result, then what you need from the user. No preamble, recaps or restated
     plans." This cuts form, not content: recommendations, what was skipped and reasons for non-obvious
     choices stay (cut categories 5–8 in Contributing-to-the-Template).
   - item 9: "Task done and the next is unrelated? Make sure the PR, `TODO.md` or design record holds what's
     needed, then suggest a new session." An assistant can't end a session, so this advises rather than
     enforces. It's suggested once, at the boundary between tasks, never mid-task. A follow-up on the same
     work keeps its session: the context is still useful. Tool commands (`/clear`, `/compact`) go in the
     wiki, not `AGENTS.md`.

   Together they add 237 characters: the longest variant goes from 5,965 to 6,202 of 6,750.
3. **Guidance for users**, which nothing can enforce:
   - the template wiki's Working-with-AI page gains a section on keeping sessions small;
   - the project skeleton's Contributing page ("Keeping AI context small") gains two bullets:
     - point, don't paste: give a path or the failing check's name, not the log;
     - one task per session: clear or compact between tasks, so history doesn't pile up;
   - `docs/ai/prompts.md` gains a line saying the same.
4. **No tool-specific settings.** Claude Code's output styles would reach only Claude, and would duplicate
   the `AGENTS.md` rule.

## Alternatives considered

- *Only the reply rule:* the smallest change, but it leaves the largest saving (command output) untouched.
- *A `--quiet` flag on each command, used in `AGENTS.md`:* every command line in the Definition of done gets
  longer, and humans running the commands get the noisy version. Quiet by default with `--verbose` is the
  right way round.
- *Quiet output only locally, verbose in CI:* two behaviours to document and test. CI logs are read by
  people when a check fails, and a failing check prints its detail anyway.
- *A token budget per session:* nothing measures it across tools, and it would fail the wrong thing.

## Consequences

- One passing Definition of done run drops from about 6,450 characters to under 1,500 on a fresh service
  project. The saving repeats on every run, in every session, in every project.
- Projects get the scripts and the rule in their next update PR. `check-wiki.py`'s output changes, but no
  check becomes stricter, so this is a `feat:`, not a breaking change. Anyone who parses its warnings
  needs `--verbose`.
- `pyproject.toml` isn't in `_skip_if_exists`, so `copier update` merges the new pytest options into
  existing projects. A project that has changed `addopts` itself may get a merge conflict on that line.
- Wiki pages change: Working-with-AI (a new "Keeping sessions small" section), Project-Wiki-Standard
  (`--verbose`), Troubleshooting (two entries), and the project skeleton's Contributing page and kick-off
  prompts.
- **Acceptance check:** the template's tests (decision 1), plus one sample task run before and after on a
  rendered project, with the token counts the tool reports quoted in the PR.

## Resolved questions

1. **Should CI pass `--verbose` to `check-wiki.py`?** No. One behaviour everywhere. A failure lists
   everything, and the warning count tells a reviewer that placeholders remain. In CI, warnings are also
   GitHub annotations on the PR.
2. **Should the coverage table go entirely on a pass?** No: `skip-covered` shows only files with missing
   lines, which is the detail an assistant needs when coverage drops.
3. **Where does the reply rule go?** How to work, as item 8, with the other rules about how an assistant
   reports. Conventions is about the code.
4. **Should `AGENTS.md` enforce a new session per task?** It can't: only the user can end a session. It
   advises, as item 9, once the work is written down where the next session will find it.
