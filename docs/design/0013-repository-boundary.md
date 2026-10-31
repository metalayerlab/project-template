# 0013: Repository boundary for agents

Status: Implemented
Date: 2026-10-31
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

An assistant working in a generated project can reach any file the user can: a sibling checkout, a
library's source, a submodule, the installed dependencies in the project's own environment. A fix made
there is invisible to that codebase's owners and reviewers, is lost on its next update, and was never
reviewed where it lands. The template already handles one case: `AGENTS.md` sends bugs in template-owned
files to a project-template issue, with a minimal, linked workaround. Every other codebase had no rule.

Constraints:

- Claude Code permission rules can't say "outside this repository": deny is checked before allow, so
  `Edit(//**)` can't have the project carved back out of it.
- Users often run in `bypassPermissions` mode, where nothing prompts. Only deny rules and `PreToolUse`
  hooks still apply.
- Bash can write anywhere, and parsing shell commands for paths is unreliable.
- The rule binds every assistant, but only Claude Code reads `.claude/settings.json`.

## Decision

1. **The rule, in `AGENTS.md` "Never":** don't change another codebase from here (other repositories,
   submodules, installed dependencies), even when asked: the user opens a session there. Search its issues,
   comment your case or draft a new one for the user to confirm, and keep any workaround minimal, linked
   and temporary. The template-owned line in the Repository map now points at this rule instead of carrying
   its own steps. Net **+227 characters** (6,240 to 6,467 of the 6,750 skeleton ceiling): category 8, an
   unenforced rule about behaviour, backed by the hook for one tool.
2. **A `PreToolUse` hook** in `.claude/settings.json` runs `scripts/repo-boundary.py` (template-owned,
   stdlib Python plus git) on `Edit|MultiEdit|Write|NotebookEdit`. It exits 2, which blocks the call in any
   permission mode, when the path belongs to another git repository (compared by `git rev-parse
   --git-common-dir`, so this repository's worktrees pass and submodules and nested clones don't) or lies
   outside the project. The temp directory and `~/.claude` (Claude Code's memory and plans) stay writable.
   Before `git init`, the project directory is the boundary.
3. **Installed dependencies:** each layer denies `Edit` on its environment (`./.venv/**`, `./node_modules/**`).
4. **Pull requests to other repositories:** `gh pr create -R`/`--repo` is denied. `gh issue create -R` is
   not pre-allowed, so it asks, except in `bypassPermissions`, where `AGENTS.md` asks for the user's
   confirmation instead.
5. **The receiving side:** a *Change request from another repository* issue form (requesting repository,
   the need, proposed change, workaround in place, done when), so requests between generated projects
   arrive in one shape.

Like 0011, the settings catch mistakes early. They are not a security boundary.

## Alternatives considered

- **Claude Code's sandbox, on by default**, to confine Bash writes too. Tested with Claude Code 2.1.289 on
  Linux (bubblewrap): it did block writes outside the project, but also `uv sync` and `uv run` (the cache in
  `~/.cache/uv` is read-only), Docker (`check-docs-secrets.sh`, the image tests) and `gh` (its login wasn't
  readable). Every layer would need cache paths and exclusions, and it doesn't run on native Windows.
  Rejected as a default; users can turn it on in `.claude/settings.local.json`.
- **Deny rules only:** can't express "outside the project" (see Context). Rejected.
- **Refusing even the user:** the user owns the machine and can always edit by hand. The rule keeps a
  session to one repository and names the way out (a session there) instead. Rejected.
- **A hook on Bash that parses commands for paths:** `cd`, variables and scripts defeat it, and a check that
  misses most cases reads as stronger than it is. Rejected.

## Consequences

- Claude Code can't edit outside the repository by mistake in any mode. Other assistants have the rule only.
- Bash is unguarded (`sed -i ../x`, `cd ../other && git commit`): the rule covers it, nothing enforces it.
- A project under the temp directory can edit its siblings there: the temp directory has to stay writable.
- Project hooks run only in a workspace the user has trusted, as Claude Code requires.
- Projects get the hook, the denies and the issue form on their next `copier update` (all template-owned).
- Wiki: Working-with-AI (settings row, guard rails), Updating-from-the-Template (reporting a problem),
  Project-Layout (the script).

## Open questions

None.
