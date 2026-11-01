# 0016: An `obsidian` language layer: the vault is the wiki, design records are notes

Status: Implemented
Date: 2026-11-01
Authors: Stephen Cox; drafted by Claude (Opus 5.5)
Supersedes: [0015](0015-knowledge-kind.md)

## Context

0015 added `kind: knowledge` under `language: none`: a notes repository that keeps the agent guard rails and
drops releases, the wiki, design records and markdownlint. Two things are wrong with it.

- **Obsidian is a toolchain, and 0015 put it in the core.** A vault has its own Markdown dialect (wikilinks,
  embeds, callouts, properties), its own config directory (`.obsidian/`), its own ignore entries, its own
  index mechanism (Bases) and its own template mechanism (`_templates/`). That is exactly what 0001 says a
  layer holds. 0015 rejected "`knowledge` as a language" because a notes repository had no toolchain; it
  then gated the Obsidian `.gitignore` entries on `kind` in the core, and had no place for an Obsidian check.
- **Dropping design records was wrong.** A notes repository makes decisions about itself (its layout, its
  conventions, what it follows) and they need the same Context / Decision / Alternatives record a code
  repository keeps. What doesn't fit is their *style*: plain Markdown in `docs/design/`, a hand-kept index
  table and relative links, outside the vault where nothing links to them.

And the wiki: a vault already *is* a wiki (linked pages, a graph, a home note). A `docs/wiki/` beside it, or
the GitHub wiki, would be a second documentation home.

`kind: knowledge` is unreleased (0.1.19 predates #89) and no project has adopted it, so it can be replaced
rather than migrated.

Constraints, as in 0015: every existing variant renders byte-for-byte as before; the core stays
language-neutral; the repository owns its notes and their conventions, the template owns the guard rails and
the design-record shape.

## Decision

### The question

A fourth `language` choice; `knowledge` leaves `language: none`:

```yaml
language:
  choices:
    Python: python
    "TypeScript: Node.js and npm": typescript
    # A notes repository: the vault is the wiki, design records are notes (design record 0016).
    "Obsidian: a vault of notes (no build, release or image)": obsidian
    "None: core only (no build, tests or image)": none
```

`kind` is not asked for `obsidian`; it is `brain`, the shape 0015 defined as `knowledge` (no releases, no
software docs, `README.md` project-owned, the guard rails kept), renamed for what these repositories are: a
personal brain, a project brain, a commons. So 0015's split stands with the line drawn where 0009 draws it:
**`obsidian` is the toolchain, `brain` is the shape.** The core's `kind == 'knowledge'` branches and
`_exclude` block become `kind == 'brain'`; everything Obsidian-specific in them moves to `layers/obsidian/`.
`kind: knowledge` is no longer a choice for `language: none`, which goes back to `other` only.

One new question says where the vault is:

```yaml
vault_dir:
  type: str
  help: The vault's folder, relative to the repository root ("." for the root itself)
  default: knowledge
  when: "[[ language == 'obsidian' ]]"
  validator: >-
    [% if not (vault_dir | regex_search('^(\\.|[A-Za-z0-9_][A-Za-z0-9 _-]*)$')) %]
    One folder name, or "." for the repository root
    [% endif %]
```

One folder name, not a path: the vault's directory in `template/` is named `[[ vault_dir ]]`, and a
rendered name with a `/` in it is not a nested path. The default is the brain's layout, which keeps `tools/`
and git-ignored `artifacts/` and `private/` outside the vault; `.` suits a repository that is nothing but a
vault.

### The vault

The skeleton, under `vault_dir` (`<vault>` below):

| Path | Owner | What |
|---|---|---|
| `<vault>/🏠 Home.md` | project | the vault's start note; `README.md` points at it |
| `<vault>/📐 Conventions.md` | project | the repository's note conventions (the note `AGENTS.md` says to follow) |
| `<vault>/decisions/` | project, except the base | design records (below) |
| `<vault>/decisions/Decisions.base` | template | the design index |
| `<vault>/_templates/📝 Design Record.md` | template | the record template, for Obsidian's *Insert template* |
| `<vault>/_attachments/` | project | images and files notes embed |
| `<vault>/.obsidian/app.json`, `templates.json` | project | attachment folder and templates folder only; everything else in `.obsidian/` is the user's |

There is no `docs/` at all: no wiki pages, no `wiki.yml`, no GitHub wiki, no `docs/ai/prompts.md`. Home and
Conventions are written once and are the repository's, like 0015's `README.md`. Which other notes exist is the
repository's business; the template requires none.

### Design records, in vault style

Same purpose, same five sections, same lifecycle as a code project's; different form:

- **Name**: `📝 NNNN Title In Title Case.md` in `<vault>/decisions/`, linked by name:
  `[[📝 0003 Follow Sluice Releases]]`. The number keeps commits and issues able to cite a record briefly.
- **Properties** instead of header lines:

  ```yaml
  ---
  kind: decision
  number: 3
  status: proposed        # proposed | approved | implemented | superseded | rejected
  date: 2026-11-01
  authors: [Stephen Cox]
  summary: The decision in one line
  supersedes: []          # wikilinks, quoted: ["[[📝 0001 ...]]"]
  superseded_by:
  tags: [decision]
  ---
  ```

- **Headings**: `## 🧭 Context`, `## ✅ Decision`, `## ⚖️ Alternatives considered`, `## 🌊 Consequences`,
  `## ❓ Open questions`. The check compares them with the emoji stripped.
- **Index**: `Decisions.base`, an Obsidian Base over the folder showing number, name, status, date and
  `summary`, sorted by number. It replaces `docs/design/README.md`'s table: nobody keeps an index by hand,
  and `check-wiki.py`'s design-index check isn't needed.
- **Decided against**: a record with `status: rejected`, or a line in a record's Alternatives. The base has
  a second view filtering them. There is no `TODO.md`; an Approved record with work left gets an issue.

### The layer

`layers/obsidian/` provides every name and fragment in `layers/README.md`:

| Value or fragment | Obsidian |
|---|---|
| `name`, `code_lang`, `topic` | `Obsidian`, `markdown`, `obsidian` |
| `lint` | `uv run scripts/check-vault.py` |
| `test` | `sh scripts/check.sh` (project-owned, as for `none`) |
| `noread` | `<vault>/.obsidian/`, `<vault>/.trash/`, `<vault>/_attachments/` |
| `release_type`, `version_file`, and the image, systemd and CLI values | defined, never rendered: `brain` drops releases and has no image |
| `ignore/gitignore` | `**/.obsidian/workspace*.json`, `**/.obsidian/cache`, `**/.trash/`, moved from the core |
| `ci/jobs.yml`, `pre-commit/hooks.yaml`, `claude/allow.json` | the vault check |
| `agents/*.md`, `copilot.md`, `ai/stack-summary.txt` | the vault rules (below) |
| `dependabot.yml` | nothing: the core's `github-actions` entry only |

`scripts/check-vault.py` is a whole layer file (`[% if language == 'obsidian' %]` in its name),
template-owned, rendered with `vault_dir` as its default `--vault`. Its dependency on PyYAML is declared inline (PEP 723), so `uv run` needs no project manifest.
It checks only what the template owns or what is always broken:

1. Every note's frontmatter parses.
2. Every embed (`![[...]]`) resolves. A plain `[[link]]` to a missing note is allowed: in a vault it marks the
   next note to write.
3. Every design record has the properties above, a valid `status`, a unique `number`, the five headings, and
   `supersedes`/`superseded_by` links that resolve and point at each other.
4. The context budget, as 0015's `check-context-budget.py` does, folded in.

`tests/test_layers.py` gains an `obsidian` entry in `FORBIDDEN` (`\.obsidian`, `check-vault`, `\.base\b`), so
the core can't regrow vault specifics.

### `AGENTS.md`

0015's `knowledge` branch, with the layer's fragments: read `<vault>/🏠 Home.md` first and then only the
notes the task needs; follow `📐 Conventions`; link notes by name, never by path; record a decision about the
repository as a design record from the template; never edit `.obsidian/` beyond the two shared files; never
commit what `.gitignore` keeps out. Definition of done: `uv run scripts/check-vault.py`, `sh scripts/check.sh`,
`scripts/check-docs-secrets.sh secrets`. Target: within 500 characters of 0015's 2,370.

### Kept from 0015

The guard rails, secret scan, `template-update.yml`, `repository.toml` without a homepage, `Proprietary`
licence default, the `main` ruleset with an admin bypass for a scheduled commit job, `personal_data_guard` off
by default, and no markdownlint. Its Open questions 1, 2, 4 and 6 stand as answered. Question 3 (the context
budget without the wiki) is now the vault check; question 5 (Obsidian in `.gitignore`) is now the layer's.

### Tests

- The `knowledge` variant becomes `language: obsidian` in `tests/test_render.py` and `template-ci.yml`.
- `test_kind_other_needs_language_none[knowledge]` is replaced by a test that `language: none` offers `other`
  only and `obsidian` renders `kind: brain`.
- Vault check tests: a broken embed, a bad `status`, a duplicate `number`, a missing heading and a one-sided
  `supersedes` each fail; a link to a missing note passes.
- `test_layers.py` covers the new layer like the others.
- `vault_dir`: a render with `.` puts the skeleton at the root and its `.gitignore` and `noread` entries
  still match; a name with `/` or `..` is rejected.

## Alternatives considered

- **Keep `kind: knowledge` under `language: none` (0015).** The Obsidian ignore entries already sit in the
  core gated on `kind`, a vault check and design-record style would join them, and `test_layers.py` can't see
  it. Superseded.
- **Keep the kind's name `knowledge`, or call it `vault`.** `vault` names the tool's concept, which the layer
  already carries; `knowledge` names the content. `brain` names the repository, as the roadmap already does.
- **`kind: obsidian` under `language: none`.** The same toolchain-in-the-core, under another name.
- **Both `language: obsidian` and `language: none, kind: knowledge`.** A notes repository with no Obsidian is
  plausible, but nobody has one; it can come back as a layer (`logseq`, plain Markdown) when someone does.
- **A fixed `knowledge/` vault folder, or always the repository root.** Fixed is the brain's layout but
  not every repository's; the root leaves no place outside the vault for scripts and git-ignored evidence. A
  question with the brain's layout as its default costs only `obsidian` users a prompt.
- **A nested `vault_dir` (`notes/vault`).** Copier would render the `/` into one directory name; nobody needs
  it yet.
- **Keep `docs/wiki/` and the GitHub wiki beside the vault.** Two documentation homes, one of them not
  linkable from the notes.
- **Design records in `docs/design/` in the code-project style.** Outside the vault: no wikilinks to or from
  them, not in the graph, and a hand-kept index.
- **Records named without a number, or without an emoji.** The number is what a commit message can cite; the
  emoji is the vault style every brain section already uses.
- **A stdlib-only vault check, like `check-wiki.py`.** Frontmatter is YAML; a hand parser of a YAML subset
  would reject valid notes. `uv` is a core tool (`layers/README.md`).
- **A required vault standard (pages and headings, like `.standard.toml`).** A vault's notes are the
  repository's; the template only owns the design records' shape.
- **Markdownlint.** Still rejected, for 0015's reason.

## Consequences

- A notes repository is an Obsidian vault with the agent guard rails, and its decisions are notes in it,
  linked and indexed like every other note.
- Not breaking: `kind: knowledge` was never released, and every other variant renders byte-for-byte as before.
  A `feat:` change.
- The core loses its Obsidian lines; `layers/README.md` lists `obsidian` and notes that `release_type` and
  `version_file` may be never-rendered for a layer whose only kind drops releases.
- `scripts/check-context-budget.py` goes; its check lives in `check-vault.py`, and the test keeping its budget
  equal to `.standard.toml`'s moves with it.
- The brain adopts the layer with `copier copy` into it (0015's migration note still holds). With the default `vault_dir`, its existing
  `knowledge/` is already the vault; it gains `decisions/`, the base and the template, and its `README.md`
  and `.gitignore` conflict once.
- `TODO.md`: the two 0015 "Decided against" lines are re-pointed to this record.
- Wiki: Answering-the-Questions (the `obsidian` choice, `vault_dir`; `none` back to `other` only), Project-Layout (the vault
  skeleton), Working-with-AI (the vault rules), Quick-Start, Migrating-Existing-Projects,
  Updating-from-the-Template (moving between `none` and `obsidian`), Contributing-to-the-Template (the layer).

## Open questions

None. Resolved on review:

1. **The kind's name?** `brain`, not `knowledge` or `vault`.
2. **Where the vault is?** A `vault_dir` question, default `knowledge`.
3. **`decisions/` or `design/` for the records?** `decisions/`: the brain's `homelab/design/` already means
   target-state notes.
4. **Is `Decisions.base` template-owned?** Yes: it is a view, not content, and fixes to its columns arrive
   with `copier update`. A repository wanting another view adds its own base.
