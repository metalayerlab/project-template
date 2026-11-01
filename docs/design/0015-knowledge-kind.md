# 0015: A `knowledge` kind: a notes repository with the agent guard rails

Status: Implemented
Date: 2026-11-01
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Notes repositories (a person's "brain", a project brain where the work has no code repository, a commons a
group shares) are worked on by AI agents as much as code is, and need the same guard rails: `AGENTS.md`,
`.claude/settings.json` with the push denies (0011), the repository boundary hook (0013), the secret scan,
and fixes arriving through `copier update`. Today the only route is `language: none` (0008), which also
brings releases, the wiki standard, design records and markdownlint. A notes repository has no use for any of
them, and deleting them brings the update conflicts 0008 was written to end.

The first such repository is the maintainer's own brain, an Obsidian vault in git:

- About 300 files: Markdown notes in `knowledge/`, the scripts they refer to in `tools/`, and evidence and key
  material in `artifacts/` and `private/`, which `.gitignore` keeps out of git.
- `README.md` is its map (what each folder is, where to start). Note format lives in a conventions note
  inside the vault, not in tooling.
- A nightly cron job commits everything and pushes straight to `main` (`auto <timestamp>`), alongside
  hand-written commits.
- `.gitignore` already carries Obsidian's per-client state (`.obsidian/workspace*.json`, `.trash/`) and
  graphify's cache.

This kind is the first step of a wider plan (brains that update themselves from the repositories they
follow, and agents that discuss in shared rooms). Those later steps build on this kind but are not part of
this record.

Constraints:

- Every existing variant renders **byte-for-byte** as before.
- The core stays language-neutral; `tests/test_layers.py` keeps policing it.
- The repository owns its notes and their conventions. The template owns only the guard rails.

## Decision

### The question

`kind` becomes asked for `language: none`, with two choices there:

```yaml
kind:
  choices:
    # ...service, cli, library, web as now...
    "other: no language layer (language: none only)":
      value: other
      validator: "[% if language != 'none' %]Only with language: none[% endif %]"
    # A notes repository: the agent guard rails, no releases or wiki (design record 0015).
    "knowledge: a notes repository, such as an Obsidian vault (language: none only)":
      value: knowledge
      validator: "[% if language != 'none' %]Only with language: none[% endif %]"
  default: "[[ 'other' if language == 'none' else 'service' ]]"
```

The `when` on `kind` is removed. `other` stays the default for `none`, so existing `none` projects render
the same files; their `.copier-answers.yml` now records `kind: other`. `service`, `cli` and `library` get a
validator ("Needs a language layer"), as `web` already had one. `knowledge` skips everything `other` skips
(`port`, `contrib`, `container_image`, ...).

### What a knowledge repository gets

| Kept | Notes |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, Copilot and Cursor pointers | `AGENTS.md` gets a `knowledge` branch (below) |
| `.claude/settings.json` and `scripts/repo-boundary.py` | without the denies for files it doesn't have (`CHANGELOG.md`, `.release-please-manifest.json`) |
| Secret scan: `scripts/check-docs-secrets.sh secrets`, `.gitleaks.toml`, the CI job and the pre-commit hook | |
| CI: the secret scan, `sh scripts/check.sh` (project-owned, for the repository's own note checks) and actionlint | no version job |
| `template-update.yml`, `CODEOWNERS`, `LICENSE`, `.editorconfig`, `.gitignore` | `.gitignore` adds Obsidian's per-client state (`**/.obsidian/workspace*.json`, `**/.trash/`); `license` defaults to `Proprietary` |
| `.github/repository.toml` and `scripts/repo-metadata.py` | no homepage (there is no wiki) |
| `dependabot.yml` | the `github-actions` ecosystem only |
| The change-request issue form (0013) and a short PR template | |
| `personal_data_guard` | asked as now, default off |
| A context-budget check in CI | template-owned and independent of the wiki standard (below) |

| Dropped | Why |
|---|---|
| release-please (config, manifest, workflow), `CHANGELOG.md`, `version.txt`, `pr-title.yml`, the `conventional-pre-commit` hook | notes aren't released; the nightly commit isn't a Conventional Commit |
| `docs/wiki/`, `wiki.yml`, `scripts/check-wiki.py`, the `check-wiki` hook | the notes *are* the documentation |
| `docs/design/`, `docs/ai/`, `TODO.md` | the repository records decisions and backlog in its own notes |
| `.markdownlint-cli2.yaml` and the `docs` half of `check-docs-secrets.sh` | the repository's note conventions decide its Markdown, not ours |
| `CONTRIBUTING.md`, `SECURITY.md`, the bug and feature issue forms, `contrib/system-packages.txt` | written for software |

Dropped files are listed in a Jinja-rendered `_exclude` block in `copier.yml` that renders only for
`knowledge`, not gated one by one in their names: they are core files every other kind keeps, and twenty
renamed files would hide that. The `none` layer's system-packages step and version job are guarded on `kind`.
Files that stay but differ (`AGENTS.md`, `CLAUDE.md`, `.claude/settings.json`, CI, pre-commit, the PR
template, `template-update.yml`, `check-docs-secrets.sh`) get `knowledge` branches; `CLAUDE.md`,
`template-update.yml` and `check-docs-secrets.sh` become `.jinja` files for it.

### `README.md` is the repository's map

For `knowledge`, `README.md` is project-owned: the skeleton is a table of folders and a "start here" line,
and the repository rewrites it. `_skip_if_exists` entries are rendered with Jinja (checked in Copier's
`_main.py`), so the entry is conditional on `kind` and every other kind's `README.md` stays template-owned.

### `AGENTS.md`

A `knowledge` branch replaces the code-oriented sections with three rules: read `README.md` first and then
only the notes the task needs; follow the note conventions `README.md` names; never commit what `.gitignore`
keeps out (evidence, keys). The Definition of done is `sh scripts/check.sh` and
`scripts/check-docs-secrets.sh secrets`. It renders to 2,370 characters (the `none` one is 4,998), well
inside the skeleton's 6,750; every other variant's `AGENTS.md` is unchanged.

### The context budget and the ruleset

A `knowledge` repository's CI checks its AI-facing files against the same `[context_budget]` as every
other kind, in a `Context budget` job running the template-owned `scripts/check-context-budget.py` (also a
pre-commit hook). The budget is a literal in the script; `test_budget_is_the_same_without_a_wiki` keeps it
equal to `.standard.toml`'s. The same job validates `.github/repository.toml`, and a `GitHub's About box`
job warns on drift on `main`, as `wiki.yml` does for other kinds.

The knowledge Quick Start keeps the `main` ruleset (0011) with a bypass for the repository admin, so a
scheduled commit job can push to `main`. Agents are still denied pushes to `main` by `settings.json`.

### Tests

- A `knowledge` variant in `tests/test_render.py` and `template-ci.yml`, running its own Definition of done.
- Tests that read the wiki or release files skip `knowledge`.
- `test_knowledge_keeps_guard_rails_only`: none of the dropped files render, nothing names them, and the
  budget check passes. `test_knowledge_readme_is_project_owned`: `copier update` keeps a knowledge
  `README.md` and still updates an `other` one. `test_kind_other_needs_language_none[knowledge]` and
  `test_kind_with_code_needs_a_layer` cover the validators.

## Alternatives considered

- **`language: none, kind: other`, and delete the rest.** The deleted files are template-owned, so each update
  brings them back as conflicts. That is 0008's Context again. Rejected.
- **`knowledge` as a `language`.** A language is a toolchain (layer values, build, image); a notes repository
  is a shape with no toolchain, which is what `kind` describes (0009). Rejected.
- **A separate template for notes repositories.** The guard rails would be copied and drift, the problem 0001
  exists to solve. Rejected.
- **A `notes_dir` question in every code project** (the earlier plan): agents in each project edit the vault's
  notes directly, through a Copier question naming the vault. Dropped: the repository boundary hook (0013)
  blocks edits outside the repository, it contradicts "another codebase changes through its own
  repository", every project's `AGENTS.md` pays for it from the context budget, and the question would
  show to every public user of the template. A brain that pulls from the repositories it follows needs
  nothing from them.
- **Markdownlint with a relaxed config.** Obsidian notes use wikilinks, callouts and emoji file names, and
  each repository's conventions differ; one config would fail some and police nothing in others. A
  repository that wants it adds it to `scripts/check.sh`. Rejected.

## Consequences

- A notes repository gets the agent guard rails and keeps receiving their fixes.
- Adopting the kind over an existing repository is `copier copy` into it: the existing `README.md` and
  `.gitignore` come back as conflicts to merge once. Migrating-Existing-Projects documents this.
- Moving between `other` and `knowledge` with `copier update -d kind=...` adds or deletes the release and wiki
  files; Copier deletes `version.txt` going to `knowledge`. Updating-from-the-Template documents this.
- The core gains an `_exclude` block and `knowledge` branches in a dozen files. `test_layers.py` is
  unaffected: `kind` is not a language.
- `scripts/repo-metadata.py` still enables the (unused) GitHub wiki when it applies the About box.
- This is a `feat:` change, not breaking: the default and every existing variant's files are unchanged
  (checked byte for byte); `none` projects' answers file gains `kind: other`.
- Wiki: Answering-the-Questions (the choice and what it drops), Project-Layout (what a knowledge repository
  has), Migrating-Existing-Projects, Updating-from-the-Template, Working-with-AI (the `knowledge` rules), Quick-Start (the checks and the admin bypass),
  Contributing-to-the-Template (the `_exclude` exception).

## Open questions

None. Resolved on review:

1. **The nightly push to `main` against the `main` ruleset?** The knowledge Quick Start keeps the ruleset and
   gives the repository admin a bypass. The writer is the owner's own job, agents are still stopped by
   `settings.json`, and a nightly PR nobody reviews is review in name only.
2. **Where do the note conventions live?** Not in the template: `README.md` names the repository's conventions
   note and `AGENTS.md` says to follow it. A template-owned conventions file would impose one note format on
   every brain.
3. **The context budget without the wiki standard?** A template-owned budget check that doesn't need the wiki,
   run in CI, so a knowledge repository's AI-facing files can't grow unchecked.
4. **The licence default?** `Proprietary` for `knowledge`. A Creative Commons choice waits for a commons to
   licence.
5. **Obsidian in the template's `.gitignore`?** Yes, for `knowledge` only: `**/.obsidian/workspace*.json` and
   `**/.trash/`. The `**/` matters: a pattern with a slash in it is anchored, and a vault may be a subfolder.
   Anything more (graphify's cache, private folders) is the repository's own.
6. **`personal_data_guard` on by default for `knowledge`?** No: a homelab brain is full of addresses the guard
   would fail on, and a private repository is the right control. A public commons turns it on.
