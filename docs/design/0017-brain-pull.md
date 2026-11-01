# 0017: Brain pull: a scheduled workflow keeps a brain's `repos:` notes current

Status: Implemented
Date: 2026-11-01
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

A brain (`language: obsidian`, [0016](0016-obsidian-layer.md)) holds notes about code projects, and they go
stale as soon as those repositories move on. The maintainer's brain (`andronics/brain`, its design record
`📝 0001`) built a fix: `brain-pull.yml`, a daily `anthropics/claude-code-action` run that reads the
repositories named in notes' `repos:` property and opens one PR updating those notes. Issue #94 asks to ship
it in the layer, because `.github/workflows/` is template-owned and the brain keeps it there only as a
workaround.

What running it taught (#94):

- **Claude never holds a write token.** A read-only job runs the gate and Claude and uploads a patch, a PR
  body and an optional `issues.json`; a second job with write permissions applies the patch.
- **The prompt is not the control.** The write job rejects paths outside the vault and in `.obsidian/`,
  `_templates/` or `Decisions.base`, and re-runs `check-vault.py`. Emoji note names come out quoted unless
  `git -c core.quotePath=false apply --numstat`.
- **The gate:** commits or releases since the last *successful* run, never a PR's merge date. A failed run
  then retries the same window, which replaces a per-run repository cap.
- **Repository setting:** Actions must be allowed to create pull requests, and new repositories have it off.
- **CI:** a push by `GITHUB_TOKEN` triggers no workflows, so the write job dispatches `ci.yml` on the branch.
  That run is not shown as a PR check, and the PR's own CI run waits for approval (`action_required`).
- **Branches:** only an open `brain-pull` PR's branch is reused. A closed PR's branch brings back rejected
  edits.
- **Claude's allowed tools:** a first run had 8 calls refused and made 2 thin edits. Allowing read-only
  commands, giving today's date and asking for one simple command per Bash call gave a sourced update in 23
  turns. `python3` stays refused: it would bypass the path rule.
- **A `debug` input** for manual runs (`show_full_output`): the only way to see which tool calls were refused.
- **After the push nothing is fatal:** a malformed `issues.json` is dropped before it, and a failure to
  dispatch CI or open an issue is a warning.

Constraints: a project that doesn't use it sees no diff on update (its answers file aside); the core stays
language-neutral (`tests/test_layers.py`); every action is pinned; each job gets least privilege; and the
workflow must not fail every day in a brain that hasn't set it up.

## Decision

### The question

```yaml
brain_pull:
  type: bool
  help: Add the Brain pull workflow? Daily, Claude Code updates the notes whose `repos:` property names a GitHub repository that changed, in one PR for review. Needs the CLAUDE_CODE_OAUTH_TOKEN secret and a repository setting (Quick-Start in the wiki)
  default: false
  when: "[[ language == 'obsidian' ]]"
```

Opt-in, off by default:

- It spends the maintainer's Claude subscription (or API credit) on a schedule, and needs a secret and a
  repository setting. A template should not start that in a repository whose owner didn't ask.
- A brain with no `repos:` notes (a commons, a personal brain without code) gains nothing from it, and a
  daily scheduled run still costs a private repository Actions minutes.
- With `false`, every existing brain renders exactly as before; only `.copier-answers.yml` gains
  `brain_pull: false`. Other languages never see the question.

`copier update --trust -d brain_pull=true` turns it on.

### What renders

Two whole layer files, gated in their names as `layers/README.md` §3 says:

| File | Owner | What |
|---|---|---|
| `.github/workflows/[% if language == 'obsidian' and brain_pull %]brain-pull.yml[% endif %].jinja` | template | the workflow |
| `scripts/[% if language == 'obsidian' and brain_pull %]followed-repos.py[% endif %].jinja` | template | prints the `owner/name` values of the vault's `repos:` properties |

`followed-repos.py` reads notes the way `check-vault.py` does (git's file list, no dot-folders, YAML front
matter with PyYAML declared inline) and skips `_templates/`. `repos:` may be one string or a list; an entry
that isn't `owner/name` is a warning on stderr, never output. A shell `grep '^repos:'` would miss a YAML block
list and accept anything.

### The workflow

`on: schedule` (daily, 05:00 UTC) and `workflow_dispatch` with two inputs: `since` (a date overriding the
last run) and `debug` (boolean, `show_full_output`; logs are public in a public repository). Top-level
`permissions: {}`, `concurrency: brain-pull`.

**`update`** (`contents: read`, `pull-requests: read`, `actions: read`; 30 minutes):

1. The gate, plain shell. No `CLAUDE_CODE_OAUTH_TOKEN` secret: a notice, and the run ends green without
   calling any API. Otherwise `since` = the input, else the start of this workflow's last successful run, else
   one day ago; the repositories from `followed-repos.py` with commits or releases after it. A repository it
   can't read (private, renamed) is a warning. The branch: an open `brain-pull` PR's branch (checked out),
   else `brain-pull/<date>`, with the run number added if that name exists.
2. Only if a repository changed: Claude Code, with the date, the repositories and `since` in the prompt.
   Allowed tools: `Read`, `Glob`, `Grep`, `Edit` on the vault's `.md` files, `Write`/`Edit` in its output
   folder, and read-only commands (`gh api`, `gh issue/pr/release view`, `cat`, `jq`, `grep`, `git log`/`diff`/`show`,
   `uv run scripts/check-vault.py`, ...). No web tools, no `python3`. `--max-turns 40`.
3. Package: `git diff --binary -- <vault>` as `vault.patch` (untracked files can't be in it, so no new
   notes), `pr-body.md`, and `issues.json` if it is an array of `{title, body}` strings (else dropped with a
   warning), uploaded as an artifact.

**`propose`** (`contents`, `pull-requests`, `issues` and `actions: write`; 10 minutes), only if there is
something to propose:

1. Scope, from `git -c core.quotePath=false apply --numstat` and `--summary`: every path is an existing `.md`
   file in the vault, outside any dot-folder (`.obsidian/`) and `_templates/` (`Decisions.base` is not
   `.md`); with `vault_dir: .`, also not `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` or `README.md`. No file is
   created, deleted, renamed or changes mode. Anything else fails the run.
2. Apply on the branch (the open PR's, or a new one), `uv run scripts/check-vault.py`, commit
   `docs: brain pull <date>`, push.
3. Open the PR (label `brain-pull`, created with `--force`), or comment the new body on the open one. If
   GitHub refuses to create it, an error names the repository setting and the run fails, so the next run
   reads the same window again.
4. Warnings only from here: dispatch `ci.yml` on the branch, and open at most 3 issues from `issues.json`.

### The secret and the repository setting

- `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`) is the one secret. Without it the workflow skips; set it
  later and the first run reads from the last (skipped) successful run, so nothing is lost but the days before
  it.
- **Allow GitHub Actions to create and approve pull requests** (Settings, Actions, General; the API's
  `can_approve_pull_request_reviews`) must be on, and for an organisation repository the organisation must
  allow it first. Quick-Start documents it with a one-off
  `gh api -X PUT repos/<owner>/<repo>/actions/permissions/workflow -F can_approve_pull_request_reviews=true`.
  `repo-metadata.py` does not set it: that script and `repository.toml` are the About box, and CI's drift
  check runs on `GITHUB_TOKEN`, which can't read Actions settings (they need the Administration permission).
  It also lets workflows *approve* PRs, a security setting a maintainer should turn on knowingly.

### Tests

- `tests/test_render.py`: the `obsidian` variant sets `brain_pull: true`, so the workflow is linted
  (actionlint) and its label checked by `test_labels_are_created`. A default render has neither file, and no
  other language can render them. The workflow's jobs have the permissions above (`update` writes nothing),
  the secret gate and the scope rules are present, and every action in every rendered workflow is pinned to a
  commit SHA with a version comment. `followed-repos.py` finds inline and block lists, skips `_templates/` and
  bad entries, and works with `vault_dir: .`.
- `tests/test_layers.py`: no core file mentions `brain_pull`; a file gated on it is also gated on
  `language == 'obsidian'`.

## Alternatives considered

- **On by default for `kind: brain`.** Every existing brain would gain a daily scheduled workflow, a secret to
  set and a setting to change on its next update, and new brains would spend Claude usage nobody chose.
- **A project-owned workflow (`_skip_if_exists`).** The workflow is what most needs fixes (the lessons above
  were all fixes); a project-owned copy stops receiving them.
- **One job with write permissions.** Claude would hold a write token while reading untrusted content from
  other repositories; the allow-list would be the only control.
- **The gate on a PR's merge date.** Changes landing between a run and its merge would fall before the date
  and never be read.
- **A per-run repository cap.** Only successful runs move the date, so a run that runs out of turns is
  retried; a cap would also need state.
- **Set the Actions setting from `repo-metadata.py` / `repository.toml`.** See above: CI can't check it with
  `GITHUB_TOKEN`, it is a security choice, and `repository.toml` is project-owned, so existing brains wouldn't
  get the key.
- **Fail when the secret is missing.** A brain that answered yes but hasn't set the secret yet would have a
  red run every day.
- **`grep '^repos:'` in the gate instead of a script.** Misses YAML block lists and quoted values.
- **Trigger CI with a GitHub App or PAT token** instead of a dispatch. A second secret for every brain.
- **A Claude Code run per repository or per note.** More runs, more PRs to review; one run a day keeps
  review to one sitting.
- **Auto-merge.** A human reviews every change; a later record may revisit it.

## Consequences

- A brain that opts in gets at most one PR a day (none on quiet days), plus issues for changes too big for a
  note. Every other project, and every brain that doesn't opt in, renders as before.
- The brain (`andronics/brain`) replaces its project-owned copy with `copier update --trust -d brain_pull=true`,
  and its design record `📝 0001` points here.
- `repos:` becomes a property the template reads. The vault's `📐 Conventions` note is project-owned and not
  rendered from a template, so it doesn't mention it; the wiki does.
- The PR's checks need a human: approve the PR's own CI run, or rely on the dispatched run on the branch.
- Wiki: Answering-the-Questions (`brain_pull`), Quick-Start (the secret and the setting), CI-Pipeline (the
  workflow), Project-Layout (the two files), Updating-from-the-Template (turning it on).

## Open questions

None. Merging the PR approves this record:

1. **Opt-in or on by default?** Opt-in (above).
2. **Can the template set the repository setting?** No; documented with a `gh api` command (above).
