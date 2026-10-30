# AGENTS.md: working on project-template

This repository is a [Copier](https://copier.readthedocs.io/) template: `template/` is rendered into new
projects. These instructions are for changing **the template**. The instructions that generated projects
get are in `template/AGENTS.md.jinja`.

## Layout

| Path | What |
|---|---|
| `copier.yml` | The questions, derived values, `_skip_if_exists` (project-owned files) and tasks |
| `template/` | Everything rendered into a project. Files ending `.jinja` are rendered; the rest are copied verbatim |
| `layers/<lang>/` | A language layer: `layer.jinja` (the values the core reads) and fragments the core includes |
| `layers/README.md` | The layer contract: what every layer must provide |
| `tests/test_render.py` | Renders each variant and runs that project's own Definition of done |
| `tests/test_layers.py` | Enforces the core/layer boundary |
| `docs/wiki/` | This template's wiki (published to the GitHub wiki), checked by the same script projects use |
| `docs/design/` | Design records for the template; `README.md` is the index (read it, not every record) |
| `TODO.md` | The template's outstanding work and rejected ideas |

## Jinja in this template

- Delimiters are **`[[ var ]]`**, **`[% block %]`** and **`[#! comment !#]`**, not `{{ }}`, so GitHub
  Actions' `${{ }}` needs no escaping.
- So **never write `[[` in a `.jinja` file** unless you mean a variable. Watch for `Callable[[str], X]`,
  TOML `[[array]]` and bash `[[ ]]`: use `Callable[..., X]`, `[table.key]` and `[ ]`.
- Conditional files and directories go in the *name*: `[% if kind == 'service' %]api.py[% endif %].jinja`.
  An empty rendered name skips the file.
- `trim_blocks` and `lstrip_blocks` are on. Put block tags on their own lines, and check the rendered
  output, not the source.

## Core vs layer

`template/` is the core. Anything specific to one language (its commands, tools, base images, ignore
entries, wording) goes in `layers/<lang>/`: a value in `layer.jinja`, or a fragment the core `include`s.
Whole files that exist for only one language (`pyproject.toml`, `src/`, `tests/`) stay in `template/`, gated
in their *name*. `uv run pytest tests/test_layers.py` fails if Python tooling appears in a core file. See
`layers/README.md`.

## Don't read

`uv.lock`, `.venv/`, `CHANGELOG.md` (use `git log`), and `.graphify/`. Rendered test output lives in
pytest's temporary directories: render a variant yourself instead.

## Rules

- Every change must keep all variants green: `uv run pytest` (add `-m docker` to build and run the images).
- A change to what projects get (workflows, scripts, the wiki standard, manifests) is a user-facing change
  for every project. Document it in `docs/wiki/`, use a `feat:`/`fix:` PR title, and mark breaking ones
  `!`: projects receive it through `copier update`.
- Template-owned vs project-owned is decided by `_skip_if_exists` in `copier.yml`. Never make a file
  project-owned without saying why in the PR: those files stop receiving fixes.
- A new required wiki page or heading in `template/docs/wiki/.standard.toml` fails every project's CI on its
  next update. Add the skeleton page and say so in the PR body.
- Pin actions to commit SHAs, with the version in a trailing comment.
- Never credit an AI in commits or PRs (`Co-authored-by` trailers, "Generated with" lines, session links).
- Asking the user something? Give your recommendation and why.
- Finished a bug or enhancement? Say what let it happen, and whether `template/`, a check or this file should
  change. Propose it, with your recommendation, or say "none".
- Reply tersely: the result, then what you need from the user. No preamble, recaps or restated plans.
- Task done and the next is unrelated? Make sure the PR, `TODO.md` or a design record holds what's needed,
  then suggest a new session.
- An Approved design record with work left gets a `TODO.md` line or an issue, not just wording in the record.
- Keep the generated code small. It's a skeleton for AI-assisted build-out, not a framework.
- AI-facing files have a budget: `[context_budget]` in `template/docs/wiki/.standard.toml`, enforced in every
  project's CI. The skeleton may use 75% of it (`tests/test_render.py`). Raising it needs a design record. A change to
  `template/AGENTS.md.jinja` states the characters it adds or frees and each cut's category (wiki: Contributing to the Template).

## Definition of done

```sh
uv run pytest                                                   # all variants
uv run pytest -m docker                                         # images build, run and are healthy
python3 template/scripts/check-wiki.py --wiki docs/wiki --strict
docker run --rm -v "$PWD:/repo" -w /repo rhysd/actionlint:1.7.12
docker run --rm -v "$PWD:/workdir" davidanson/markdownlint-cli2:v0.24.0 \
  --config template/.markdownlint-cli2.yaml "docs/wiki/*.md" "*.md" "!CHANGELOG.md"
```

plus the matching `docs/wiki/` change.
