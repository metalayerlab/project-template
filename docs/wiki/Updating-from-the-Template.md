# Updating from the Template

Projects record the template version they were made from (`_commit` in `.copier-answers.yml`). `copier update` re-renders the template at its newest tag with the same answers, and applies the difference as a three-way merge. Your own edits survive, and project-owned files are never touched ([Project Layout](Project-Layout#who-owns-what)).

## Automatic updates

`template-update.yml` runs every Monday (or on demand: Actions → Template update → Run workflow). When the template has a new release, it opens or refreshes a PR, `chore: update from project-template vX.Y.Z`, labelled `template-update` (the workflow creates the label if it's missing). Review it like any PR, with the template's CHANGELOG open beside it. It uses the release GitHub App when one is configured, so CI runs on the PR, a private template is readable, and changes to `.github/workflows/` can be pushed ([Release Process](Release-Process#the-release-github-app)). Without the App, an update that changes workflow files opens an issue instead; run `uvx copier update --trust --conflict inline` locally and open the PR yourself.

## Manual updates

```sh
git switch -c chore/template-update
uvx copier update --trust                        # newest template tag, same answers
uvx copier update --trust -d contrib='[docker, k8s]'   # also change an answer
uvx copier update --trust -d extra_ports='[3128]'      # declare a second listener
uvx copier update --trust -d image_extras='[fuse]'     # install an optional extra in the image
uvx copier update --trust -d integration_ci=true -d integration_extras='[fuse]'   # run the integration tests in CI
uvx copier update --trust --vcs-ref=v1.4.0       # a specific template version
git diff                                          # review, test, commit, open a PR
```

The working tree must be clean first. `--trust` re-runs `scripts/bootstrap.sh`, which refreshes `uv.lock` and the generated wiki sections.

## Conflicts

When your change and the template's touch the same lines, Copier leaves `<<<<<<< before updating` / `>>>>>>> after updating` markers in the file (`--conflict inline`, the workflow's default). Search the PR diff for `<<<<<<<`, resolve each one, and commit. A file you deleted that the template still ships comes back, so delete it again if it's really unwanted, and say why in the PR.

## Fixes to project-owned files

A fix to a file the project owns, such as `src/<package>/config.py`, never arrives through an update. The release notes name it, and you apply it by hand. The config engine's type checks are one: a YAML `0.5` or `true` for an integer setting, or a list or mapping for a string setting, is now an error that names the setting instead of a silent `0`, `1` or Python repr. Copy `_coerce` and its tests from a freshly rendered project.

## Moving from `none` to a language layer

A project made with `language: none` moves to a layer when one exists:

```sh
uvx copier update --trust -d language=python -d kind=cli   # and that layer's questions
```

Copier adds the layer's files and **deletes** `scripts/check.sh` and `version.txt`, your edits included. Before you update, move the commands from `check.sh` into the new layer's tools (they are still in git history afterwards). The version moves into the layer's manifest file (`pyproject.toml` or `package.json`), and must match `.release-please-manifest.json`. Your wiki pages keep their old text, so update Quick-Start, Contributing and Testing-Guide, and link the new pages from `_Sidebar.md` (`check-wiki.py` names them).

## Between `none` and `obsidian`

`copier update --trust -d language=obsidian` turns a `language: none` project into a brain, a notes vault: Copier deletes the release files, `docs/` (your wiki pages and design records included), `contrib/`, `CONTRIBUTING.md`, `SECURITY.md`, `TODO.md` and `version.txt`, so move anything you keep into the vault first. It adds the vault in `vault_dir` and `scripts/check-vault.py`, and keeps your `README.md` and `scripts/check.sh`, which are now the project's. Going back (`-d language=none`) brings the deleted files back as skeletons and leaves the vault in place.

If you keep resolving the same conflict, the change probably belongs in the template: see [Contributing to the Template](Contributing-to-the-Template).

## Reporting a template problem

A bug in a template-owned file is every project's bug, and a fix made inside one project reaches none of the others. It can also be overwritten or conflict at the next update. So, human or AI:

1. **Search first**, open and closed: `gh issue list -R metalayerlab/project-template --state all -S "<terms>"`.
2. **If one matches**, comment with your project's case: what you saw, and the workaround. If it's closed as fixed, take the update instead of working around it.
3. **Otherwise open one** with the *Template problem* form ([Contributing to the Template](Contributing-to-the-Template)), before or alongside any workaround.
4. **A workaround** only unblocks the project. Keep it minimal, link the issue in a code comment and in `TODO.md`, and remove it when the fix arrives in the update PR.

The same applies to any other codebase a project depends on. Every project's AGENTS.md carries this rule tersely, under "Never", and the PR template asks for the linked issue.
