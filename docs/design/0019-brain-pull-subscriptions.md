# 0019: Brain pull subscriptions: a note chooses what a brain follows, and how much

Status: Implemented
Date: 2026-11-01
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Brain pull ([0018](0018-brain-pull.md)) follows the repositories that notes name in `repos:`, and all of each
one. That can't express:

- a source no note covers yet;
- following part of a source (its releases, its design records, one wiki page);
- reading less of a busy repository, which keeps each Claude Code run cheaper.

The maintainer's brain (`andronics/brain`) added this in its own copy of the workflow (its design record
`📝 0002`), so it can't switch to the template's workflow without losing it (#105). Its copy also fixed a
gap in 0018: the gate's `gh run list --workflow brain-pull.yml --status success` has no `--branch`, so a test
run from another branch moves the "since" date and the next scheduled run misses that window.

What the sources look like: every project-template project keeps its wiki in `docs/wiki/` (published by its
`wiki` workflow) and its design records in `docs/design/`. So the parts map onto the commits API filtered by
path: no wiki clone and no new token.

## Decision

### The note

`<vault>/🛰️ Subscriptions.md` (`kind: subscriptions`), with the list in its properties, so it stays editable
in Obsidian and links like any note:

```yaml
subscriptions:
  - source: metalayerlab/project-template
    follow: [design-records, releases]
  - source: metalayerlab/sluice
    follow: [everything]
  - source: metalayerlab/mitm-proxy
    follow: ["wiki:Security"]
```

| Part | Changed when | Gate query |
|---|---|---|
| `everything` | any commit or release | `commits?since=` and `releases` |
| `releases` | a release published | `releases` (newest first, one page) |
| `design-records` | a commit under `docs/design/` | `commits?since=&path=docs/design` |
| `wiki:<Page>` | a commit to `docs/wiki/<Page>.md` | `commits?since=&path=docs/wiki/<Page>.md` |

- **`repos:` stays:** each repository a note names is an implicit `follow: [everything]`. A subscription for
  the same repository replaces it, which is how a busy repository is narrowed. Claude still updates every
  note naming it, from the parts followed.
- **Rendered with `brain_pull`**, as a whole layer file gated in its name
  (`[% if language == 'obsidian' and brain_pull %]🛰️ Subscriptions.md[% endif %]`), with `subscriptions: []`
  and a body saying what `follow` takes. **Project-owned** (`_skip_if_exists`): the list is the brain's own
  content, edited by its maintainer, and the template only seeds it. A brain that already has the note keeps
  it.
- A missing note, or an empty list, is fine: the brain follows its `repos:` only, as under 0018.

### The gate

`scripts/brain-pull-gate.py` (template-owned) replaces `scripts/followed-repos.py` and the shell loop:

```sh
uv run scripts/brain-pull-gate.py SINCE OUT_FILE [--vault DIR]   # writes OUT_FILE, prints the changed sources
uv run scripts/brain-pull-gate.py --list [--vault DIR]           # what is followed, per source; no API calls
```

- It reads the notes as `followed-repos.py` did (git's file list, no dot-folders or `_templates/`, PyYAML).
- A malformed list (not a list, a `source` that isn't `owner/name`, a source listed twice, an empty or
  unknown `follow`) exits 2 with an `::error` naming the note, before any Claude Code run: a typo must not
  silently follow nothing.
- A source the API can't find (404: private, renamed or gone) is a warning, as under 0018. Any other API
  failure exits 1, so the run fails and the next one reads the same window.
- `brain-pull-out/changes.md` lists, per changed source, the notes naming it in `repos:` (or "none") and,
  per part, what changed: commits as `<sha7> <subject>`, releases by tag, at most 100 per part and a count of
  the rest.

### The workflow

- The gate: `gh run list --workflow brain-pull.yml --branch main --status success`. Only a successful run on
  `main` moves the date; the PR it opens targets `main` already.
- The prompt points Claude at `changes.md`: read those changes and nothing outside the parts followed; update
  the notes listed; a source with no notes, or a change too big for a note, goes to `issues.json`. It also
  asks Claude to read the `📐` note in the folder of each note it edits, if it has one, and never to edit
  `🛰️ Subscriptions.md`.
- The propose job's scope check refuses a patch touching `<vault>/🛰️ Subscriptions.md`: what the brain
  follows is the maintainer's choice, not Claude's.
- Claude's allowed tools lose `uv run scripts/followed-repos.py`; it reads `changes.md` with `Read`.

### Tests

`tests/test_render.py`: the three files are opt-in; the gate step uses `--branch main` and writes
`changes.md`; the prompt names `changes.md`, the note and the `📐` notes; the scope check refuses the note
(also with `vault_dir: .`); `--list` shows `repos:` as `everything` and a subscription replacing it; each
malformed list exits 2; and against a stand-in `gh`, each part maps onto its query, a quiet source and
part are left out, a 404 is a warning and a 502 fails. `tests/test_layers.py`: the note is gated on
`language == 'obsidian' and brain_pull`.

## Alternatives considered

- **A YAML file (`subscriptions.yml`)** outside the vault: simpler to parse, but not editable or linkable
  from Obsidian.
- **Depth in each note's properties only:** still can't follow a source no note covers, and scatters one
  source's depth across notes.
- **Cloning wikis (`<repo>.wiki.git`):** needed only for wikis edited on GitHub directly. Template projects
  publish from `docs/wiki/`; revisit if a non-template source is subscribed.
- **Let Claude add notes for an uncovered source:** every run could add notes to review, and new notes need
  naming and placement judgement. An issue first; a later record can allow it.
- **Drop `repos:`:** breaks every note that uses it and loses the link from a note to its sources.
- **Template-owned note:** every brain's list would be overwritten on update.
- **`--branch "$default_branch"` from the event payload:** a scheduled run's payload carries only the
  schedule, and the workflow already opens its PR against `main`.
- **Fail on a 404, as the brain's copy does:** a note naming a renamed or private repository would fail every
  run until edited; 0018 chose a warning.

## Consequences

- One note to keep: adding a source or narrowing one is a one-line edit, reviewed like any note.
- More API calls (one per source and part), all with `GITHUB_TOKEN`; narrower prompts, so cheaper runs on
  busy sources.
- A brain with `brain_pull` gets the note and the renamed script on its next `copier update`;
  `scripts/followed-repos.py` is removed. Nothing changes for brains without `brain_pull` or other projects.
- `andronics/brain` can set `brain_pull: true` and delete its project-owned workflow and gate; its
  `🛰️ Subscriptions.md` is kept.
- Wiki: Answering-the-Questions (`brain_pull`), CI-Pipeline (Brain pull), Project-Layout (the files).

## Open questions

None. Merging the PR approves this record.
