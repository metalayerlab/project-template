# 0003: Dependabot auto-merge

Status: Implemented
Date: 2026-10-28
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Every project gets weekly Dependabot PRs, and under the `main` ruleset (1 approval, review from Code
Owners) each one needs a maintainer to approve it and then come back to merge it after CI. The team
asked for an auto-merge option for routine bumps. The template's rule is that a human reviews every change.

Tested on e2e-throwaway (2026-10-28) with a real Dependabot PR (pyyaml 6.0.2 → 6.0.3):

| Ruleset | Workflow approves + queues auto-merge | Result |
|---|---|---|
| 1 approval + code owners | yes | Blocked, `REVIEW_REQUIRED`: a `github-actions` approval never counts as a code owner's |
| 1 approval, no code owners | yes | Merged by itself once CI passed |

Without code-owner review, *any* workflow approval counts. Anyone with write access, or an AI assistant
on a branch, could add a workflow step that approves its own PR, and it would merge unreviewed.

## Decision

- Copier question `dependabot_automerge`: `off` (default), `patch`, or `minor`.
- When on, `dependabot-automerge.yml` reads the update type with `dependabot/fetch-metadata` and runs
  `gh pr merge --auto --squash` for allowed levels. It **never approves**.
- The ruleset is unchanged: a code owner's single **Approve** merges the PR as soon as the checks pass.
  Majors, and updates whose type Dependabot can't report, get no auto-merge.
- Repositories that opt in tick *Allow auto-merge*.

## Alternatives considered

- **Bot approval with code-owner review off:** fully automatic, but opens the self-approval hole above.
- **A machine user in the maintainers team** approving with a PAT kept as a *Dependabot* secret (only
  Dependabot-triggered runs can read those): fully automatic with code-owner review kept. Rejected
  for now as an extra account to own and a token to rotate; revisit if one-click proves too slow.
- **Ruleset bypass for Dependabot or GitHub Actions:** the merge is made as the actor who enabled auto-merge
  (`github-actions`), so the bypass would cover every workflow, the same hole.

## Consequences

- Routine bumps cost one click, with no second visit to merge.
- A human still approves every change, Dependabot's included.
- Dependabot's release cooldown applies first: very new releases aren't proposed for a few days.
