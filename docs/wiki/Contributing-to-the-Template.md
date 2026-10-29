# Contributing to the Template

The template is a shared dependency of every project. A change here reaches all of them through the weekly update PR, so it's held to a higher bar than a project change.

## Reporting a problem

Search the [open and closed issues](https://github.com/metalayerlab/project-template/issues?q=is%3Aissue) first. If one matches, add your project's case to it: what you saw, and the workaround you used. Otherwise open one with a form:

- **Template problem**: a rendered file, workflow or check that's wrong. It asks for the template version (`_commit` in `.copier-answers.yml`), the language layer and kind, the file, and whether it shows in a fresh render or only after `copier update`.
- **Feature request**: something every project should get.

Blank issues are off. Don't report a security problem in a public issue: contact a maintainer of `@metalayerlab/maintainers` directly.

## Making a change

1. Read the template's `AGENTS.md`. Most important: **Jinja uses `[[ ]]` and `[% %]`**, so GitHub Actions' `${{ }}` needs no escaping, and `[[` may never appear in a `.jinja` file except as a variable.
2. Branch and edit. Language-neutral changes go in `template/` (or `copier.yml`). Anything specific to one language goes in `layers/<lang>/`: a value in `layer.jinja`, or a fragment that core files `include` (see [Core and layers](#core-and-layers)). Conditional files are conditional in their *names*: `[% if kind == 'service' %]api.py[% endif %].jinja`.
3. Render and look at the output: `uvx copier copy --trust --defaults -r HEAD -d project_name=demo -d description=demo . /tmp/demo`. Keep `-r HEAD`: without it Copier renders the latest release tag, not your working tree.
4. Run `uv run pytest`, which renders four variants (service, a minimal service, cli, library) and runs each one's Definition of done, the wiki checks, the manifest checks and actionlint. `uv run pytest -m docker` also builds each image and probes its health endpoint.
5. Update this wiki (CI checks it with `--strict`), and open a PR whose Conventional Commit title describes the effect on *projects*. Use `!` for anything that will fail a project's CI after the update (a new required heading, a stricter check, a renamed question).
6. Release with the template's own Release PR. Projects pick it up at their next update.

`main` is protected by a ruleset: changes arrive only by PR, squash-merged, with every Template CI check, the wiki checks and the PR-title check passing, and an approval from `@metalayerlab/maintainers` (`.github/CODEOWNERS`). Organisation admins can merge a PR without the approval, for when the only maintainer is the author, but can't push to `main` directly.

When deciding whether a file is template-owned or project-owned (`_skip_if_exists`): make it project-owned only if projects must diverge from it. Project-owned files never receive another fix.

## Core and layers

| Change | Edit |
|---|---|
| Something every project gets, whatever the language (a workflow step, the wiki standard, a manifest) | `template/` |
| A language's command, tool, image or wording | `layers/<lang>/layer.jinja` (a value) or a fragment under `layers/<lang>/` |
| A whole file only one language has (`pyproject.toml`, `src/`, `tests/`) | `template/`, gated in its name by `language` |

Core files read a layer with `[% import 'layers/' ~ language ~ '/layer.jinja' as layer with context %]`, then `[[ layer.test ]]` and `[% include 'layers/' ~ language ~ '/ci/jobs.yml.jinja' %]`. The `tests/test_layers.py` checks fail if language tooling lands in a core file, or if a layer is missing a value or fragment the core uses.

## Adding a language layer

TypeScript/Node is the next planned layer. Start from a copy of `layers/python/` and rewrite each value and fragment. The full contract (every `layer.*` value, every fragment, the gated whole files, questions and test variants) is in the template's `layers/README.md`, and `uv run pytest tests/test_layers.py` lists whatever is still missing. Start with a design record in the template's `docs/design/`.
