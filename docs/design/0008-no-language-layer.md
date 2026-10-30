# 0008: A "None" language choice

Status: Approved
Date: 2026-10-30
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

`language` has one choice, Python. A project in a language with no layer yet (Go, Rust, shell, Terraform,
docs only) still wants the core: release-please, PR-title lint, the secret scan, the wiki standard and its
checker, `AGENTS.md` and the Claude Code guard rails, CODEOWNERS, the licence, the personal-data guard and
`template-update.yml`. Today its only route is to answer Python and delete what that adds, and that route
doesn't last:

- `pyproject.toml` and `scripts/gen-wiki.py` are template-owned (not in `_skip_if_exists`), so every
  `copier update` that touches them comes back as a conflict on a file the project deleted.
- `AGENTS.md`, CI, pre-commit and `.claude/settings.json` are template-owned too, and they name `uv`,
  `pytest` and `ruff` commands the project can't run. The project can't fix that locally.
- So the project stops updating, or never adopts the template. That is the hand-copied drift record 0001 was
  written to end.

Constraints:

- Python projects must see **no diff** on update (as in 0005): every Python variant renders byte-for-byte as
  before.
- The core stays language-neutral, and `tests/test_layers.py` keeps policing it. No `language == 'none'`
  branches in core files.
- The answers file is a public interface. A project that answers `none` must be able to move to a real layer
  later with `copier update`.

## Decision

### The question

```yaml
language:
  choices:
    Python: python
    "None: core only (no build, tests or image)": none
  default: python
```

The default stays Python. The label says what you give up.

### `layers/none/`: the contract, with empty values

A real layer directory, so `test_layers.py` checks it like any other (it globs `layers/*/layer.jinja`).

| Value | `none` | Why |
|---|---|---|
| `name`, `code_lang` | `None`, `text` | docs and code fences |
| `release_type`, `version_file` | `simple`, `version.txt` | release-please's language-free type |
| `test` | `sh scripts/check.sh` | the one command the project owns (below) |
| `lint`, `lint_fix`, `format`, `format_check`, `typecheck`, `test_integration`, `gen_wiki`, `install`, `add_dependency` | `''` | nothing to run |
| `lock_file`, `deps_query`, `noread` | `''`, `''`, `[]` | no lock file or caches |
| `run`, `install_cli`, `install_lib`, `import_snippet`, `config_file`, `cli_file`, `api_file` | `''` | never rendered: `kind` is `other` (below) |
| `container_*`, `systemd_upgrade`, `release_lock_note` | `''` | no image, no systemd, no lock to refresh |

Every required fragment exists. Most render nothing (`ci/jobs.yml`, `dependabot.yml`, `pre-commit/hooks.yaml`,
`bootstrap.sh`, `docker/*`, `ignore/*`, `systemd/*`). The rest are short generic text: `agents/*`, `copilot.md`,
`ai/stack-summary.txt`, `readme/development.md` and `wiki/*` say that the project has no language layer and
that its commands live in `scripts/check.sh`. `ci/jobs.yml` runs `sh scripts/check.sh` as the test job, and
a version job checks that `version.txt` matches `.release-please-manifest.json`.

### The core skips empty values

Where a layer value can be empty, the core guards on the **value**, not the language:
`[% if layer.gen_wiki %]…[% endif %]`. Most guards are in `AGENTS.md` (the Stack table, Definition of done,
Don't read), the PR template, `Contributing.md` and `.claude/settings.json`. For Python every value is set,
so its output doesn't change: every Python variant rendered identically to v0.1.10 when this was built
(only `_commit` in `.copier-answers.yml` differed).
`layers/README.md` documents which values may be empty.

### Gated whole files

- `scripts/[% if language == 'none' %]check.sh[% endif %].jinja`: **project-owned** (added to
  `_skip_if_exists`). It is where the project puts its own lint and test commands. The stub prints
  `scripts/check.sh: no checks defined yet` and exits 0, so the first CI run is green.
  `AGENTS.md`'s Definition of done runs it, so an assistant sees the placeholder and is told to fill it.
- `[% if language == 'none' %]version.txt[% endif %].jinja`: `0.0.0`, matching the manifest (the first
  release is still `0.1.0`, from `initial-version`). Project-owned: release-please bumps it.

### Other questions

- `kind` is not asked (`when: "[[ language != 'none' ]]"`) and its default becomes
  `"[[ 'other' if language == 'none' else 'service' ]]"`. Copier checks a hidden default against the
  choices, so `other` is a choice, disabled by a validator unless `language` is `none`. A Python
  project's interactive prompt shows it greyed out.
  It makes `has_cli` false and skips `port`, `extra_ports`, `health_path`, `contrib`, `puid_pgid` and `timezone`.
- `container_image` is not asked for `other`, and is false. An image needs a builder stage, and a builder
  stage needs a layer.
- `Quick-Start` and `README` get an `other` branch: "see `scripts/check.sh` and Contributing".
- The wiki standard needs no change: the pages for `has_cli`, `service`, `library` and `contrib` drop out, and
  every remaining page is core.

### Tests

- A `none` variant in `tests/test_render.py` and `.github/workflows/template-ci.yml`. It runs its own
  Definition of done, as the other variants do.
- `test_none_checks`: `scripts/check.sh` runs and prints its one line, `version.txt` is `0.0.0`, and
  `AGENTS.md` has no empty commands. `test_kind_other_needs_language_none`: `kind: other` with Python fails.
- `FORBIDDEN` in `test_layers.py` is unchanged: `none` has no tools to forbid.

## Alternatives considered

- **Answer Python and delete (the status quo).** Update conflicts on template-owned files, and assistants are
  told to run commands that don't exist. See Context.
- **`if language == 'none'` branches through the core.** Smaller at first, but it spreads special cases
  through every core file, and `test_layers.py` can't tell a legitimate branch from Python leaking in.
  Guarding on the value keeps the core asking "what does the layer give me?", which is the contract.
- **A separate core-only template.** Two templates drift apart, the problem 0001 exists to solve.
- **Write the missing layer first.** That's the right answer for a language we use often, and Node is still
  next. But it blocks one-off projects on a whole layer, and `none` doesn't stop a layer being written.
- **`none` as the default.** It would quietly become the usual answer, and projects would lose the tested
  skeleton. Rejected.
- **Let the project own `AGENTS.md`'s commands.** It would stop receiving template fixes for the whole file.
  `scripts/check.sh` keeps the project-owned part to one script.

## Consequences

- A project in any language gets the core, and keeps receiving its fixes.
- Its guarantees are weaker. Nothing is linted or tested until someone fills `scripts/check.sh`. The stub
  says so on every run.
- **Moving to a real layer:** `copier update --trust -d language=python -d kind=cli`. Tested from a
  scratch tag: no conflicts, and the new project passes its checks. The layer's files appear. Copier
  **deletes** `scripts/check.sh` and `version.txt`, project edits and all. Move their commands into the new
  layer's tools first; the old script is still in git history. The project-owned wiki pages keep their
  no-layer text, and `check-wiki.py` names the new pages to link from `_Sidebar.md`.
  Updating-from-the-Template documents this.
- The layer contract changes: a value may be empty, and the core must guard every value that can be.
  A future layer can rely on this too (no typechecker, say).
- This is a `feat:` change, not breaking: the default and the Python output are unchanged.
- Wiki: Answering-the-Questions (the choice and what it skips), Updating-from-the-Template (moving to a real
  layer), Contributing-to-the-Template (empty values and guards), Project-Layout (`scripts/check.sh`,
  `version.txt`). `layers/README.md` (empty values).
- `AGENTS.md.jinja` grows by the guards only. The guards are template source, so the rendered Python output
  doesn't change. A `none` render is shorter.

## Open questions

1. **The name: `none`, `generic` or `other`?** I recommend `none`. It's honest: there is no layer, and
   `generic` suggests a toolchain that isn't there.
2. **Should the `scripts/check.sh` stub exit 0 or 1?** I recommend exit 0, with the printed warning. A failing
   stub blocks the first commit's CI and teaches people to ignore red. The Definition of done and the warning
   make the gap visible.
3. **Should `kind` be hidden as `other`, or still asked?** I recommend hiding it. `service`, `cli` and `library` all
   promise generated code (FastAPI, Typer, a package) that `none` can't produce.
4. **No container image at all?** I recommend no, for now. A project-owned Dockerfile would be a stub nobody
   updates, and a project that needs an image needs a layer. A later record can add this.
