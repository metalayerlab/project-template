# Release Process

## How it works

[release-please](https://github.com/googleapis/release-please) keeps one open **Release PR** per repository, updated on every push to `main`:

1. Conventional Commit PR titles (squash-merged) decide the bump: `fix:` → patch, `feat:` → minor, `!` or `BREAKING CHANGE:` → major. Before 1.0, each of these is one level lower. The first release is `0.1.0` (`initial-version`; without it release-please starts at 1.0.0).
2. The Release PR bumps `pyproject.toml` and `.release-please-manifest.json`, writes the `CHANGELOG.md` entry (✨ Features, 🐛 Bug Fixes, ⚡ Performance, ♻️ Refactoring, 📚 Documentation; chore/ci/test/build are hidden), and moves the image tag in `contrib/k8s` and `contrib/docker`. A follow-up job refreshes `uv.lock` on the same branch.
3. A human reviews it. The wiki check runs in strict mode, so any page still holding skeleton guidance blocks the release.
4. Merging it tags `vX.Y.Z`, publishes the GitHub Release, and calls `docker-build.yml` for `:X.Y.Z`, `:X.Y`, `:X` and `:latest`.

The full user-facing description is each project's own Release-Process wiki page (template-owned).

Versus the old process: nobody runs `bump-version.sh` or pushes tags, the version lives in one file, and the changelog can't duplicate entries or pick up merge commits.

## The release GitHub App

Workflows can't trigger other workflows through `GITHUB_TOKEN`. With the default token, a Release PR gets no CI run, and the uv.lock refresh commit doesn't either. The image build doesn't depend on this: it's called directly. The fix, once for the organisation:

1. Create a GitHub App in metalayerlab (no webhook) with repository permissions **Contents: read & write**, **Pull requests: read & write** and **Issues: read & write**. Install it on all repositories (and on project-template, so `template-update.yml` can read it if it's private).
2. Organisation **variable** `RELEASE_APP_CLIENT_ID` = the App's client ID. Organisation **secret** `RELEASE_APP_PRIVATE_KEY` = a private key.

`release-please.yml` and `template-update.yml` use the App when the variable is set, and fall back to `GITHUB_TOKEN` otherwise.

## Releasing the template itself

project-template is released the same way (release-type `simple`), tagged `vX.Y.Z` with no component prefix, because Copier ignores tags that aren't PEP 440 versions. Its tags matter: `copier update` moves projects to the newest tag, so **every template change reaches projects only through a reviewed release**. Mark breaking changes (a new required wiki heading, a renamed question, a removed file) with `!`.
