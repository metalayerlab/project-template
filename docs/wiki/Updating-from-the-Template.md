# Updating from the Template

Projects record the template version they were made from (`_commit` in `.copier-answers.yml`). `copier update` re-renders the template at its newest tag with the same answers, and applies the difference as a three-way merge. Your own edits survive, and project-owned files are never touched ([Project Layout](Project-Layout#who-owns-what)).

## Automatic updates

`template-update.yml` runs every Monday (or on demand: Actions → Template update → Run workflow). When the template has a new release, it opens or refreshes a PR, `chore: update from project-template vX.Y.Z`, labelled `template-update`. Review it like any PR, with the template's CHANGELOG open beside it. It uses the release GitHub App when one is configured, so CI runs on the PR and a private template is readable ([Release Process](Release-Process#the-release-github-app)).

## Manual updates

```sh
git switch -c chore/template-update
uvx copier update --trust                        # newest template tag, same answers
uvx copier update --trust -d contrib='[docker, k8s]'   # also change an answer
uvx copier update --trust --vcs-ref=v1.4.0       # a specific template version
git diff                                          # review, test, commit, open a PR
```

The working tree must be clean first. `--trust` re-runs `scripts/bootstrap.sh`, which refreshes `uv.lock` and the generated wiki sections.

## Conflicts

When your change and the template's touch the same lines, Copier leaves `<<<<<<< before updating` / `>>>>>>> after updating` markers in the file (`--conflict inline`, the workflow's default). Search the PR diff for `<<<<<<<`, resolve each one, and commit. A file you deleted that the template still ships comes back, so delete it again if it's really unwanted, and say why in the PR.

If you keep resolving the same conflict, the change probably belongs in the template: see [Contributing to the Template](Contributing-to-the-Template).
