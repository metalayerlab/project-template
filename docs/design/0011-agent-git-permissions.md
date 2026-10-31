# 0011: Agent git permissions

Status: Implemented
Date: 2026-10-31
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Generated projects' `.claude/settings.json` has denied `Bash(git push:*)`, `Bash(git tag:*)` and
`Bash(gh release:*)` since the initial template, without a record of why ([#60]). The written rules said
something narrower: `AGENTS.md` and the Contributing page forbid pushing to **`main`** and pushing tags, but the
deny list blocked every push. An agent couldn't push its own `feat/*` or `dev/*` branch to open a PR, and
nothing told it the user was expected to.

Constraints:

- Claude Code's `Bash(...)` rules match the command text, not what git will do. A bare `git push` while on
  `main`, a push through an alias, or a script that pushes can't be told apart from a safe push.
- `main` is already protected on GitHub by its ruleset ([Quick Start]: PRs only, required checks, Code Owner
  review, no force pushes). That holds whoever or whatever pushes.
- Tags and releases belong to release-please (0001). A hand-made tag or release breaks its versioning.

## Decision

1. **The `main` ruleset is the control.** `settings.json` only catches an agent's mistakes early, before
   GitHub rejects them. Nothing in it is a security boundary.
2. **Agents may push feature branches.** `Bash(git push:*)` leaves the deny list. A push is not pre-allowed,
   so Claude Code still asks before each one unless the user allows it.
3. **Pushes that name `main`, force, or carry tags stay denied:**

   ```json
   "Bash(git push * main)",
   "Bash(git push * main *)",
   "Bash(git push *:main)",
   "Bash(git push *:main *)",
   "Bash(git push *refs/heads/main)",
   "Bash(git push *refs/heads/main *)",
   "Bash(git push *--force*)",
   "Bash(git push * -f*)",
   "Bash(git push *+*)",
   "Bash(git push *--mirror*)",
   "Bash(git push *--tags*)",
   "Bash(git push *--follow-tags*)",
   ```

   `*` matches any text, spaces included, and Claude Code checks each part of a compound command. `+` is
   a force refspec (`git push origin +feat/x`).

4. **Tags and releases stay denied:** `Bash(git tag:*)` and `Bash(gh release:*)` are unchanged.

`AGENTS.md` already says "Never push to `main`, create tags or releases", so it doesn't change (0 characters).

## Alternatives considered

- **Keep denying every push, and tell agents the user pushes.** Safe, but it stops an agent at the last step of
  every task for something the ruleset already guards. Rejected.
- **Allow `git push` outright and rely on the ruleset alone.** The ruleset stops a push to `main`, but not a
  pushed tag (release-please's) or a force push to someone's feature branch. Rejected.
- **Pre-allow pushes to `feat/*` and `dev/*`.** Prefix rules can't check what branch is current, so the allow
  would be no more precise than the denies. A prompt per push keeps a human in the loop. Rejected.

## Consequences

- Agents can finish a task with `git push -u origin feat/<topic>` and `gh pr create`.
- A bare `git push` on `main` gets past the deny list and is stopped by the ruleset. A project without the ruleset
  ([Quick Start] step 4) has no protection for `main` beyond `AGENTS.md`.
- Projects get the new `settings.json` on their next `copier update` (template-owned).
- Wiki: Working-with-AI says which pushes are denied.

## Open questions

None.

[#60]: https://github.com/metalayerlab/project-template/issues/60
[Quick Start]: ../wiki/Quick-Start.md
