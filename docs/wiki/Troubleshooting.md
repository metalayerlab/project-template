# Troubleshooting

## Common problems

### Copier: "Task 'sh scripts/bootstrap.sh' returned non-zero exit status"

Usually uv is missing or can't reach the package index. Copier removes the half-made project on a failed task, so re-run with `--skip-tasks`, then run `sh scripts/bootstrap.sh` and read its error.

### The wiki publish job fails with "No wiki repository yet"

The GitHub wiki's git repository exists only after its first page is created in the web UI. Enable the wiki, create any page, and re-run the job: it replaces that page.

### Template update opened an issue, not a PR

The update changes `.github/workflows/`, and without the release GitHub App the workflow can't push those files ("refusing to allow a GitHub App to create or update workflow"). Run `uvx copier update --trust --conflict inline` locally, push a branch and open the PR. Set up the App ([Release Process](Release-Process#the-release-github-app)) to stop this.

### `unauthorized` pulling a public project's image

The GHCR package is still private, which is the default for a new package. Make it public in its package settings ([Docker Images](Docker-Images#tags)).

### Checks on a bot PR say "action required"

Runs on a PR opened by `github-actions[bot]` wait for a maintainer's approval, after every push to it. Approve them on the PR's Checks tab, or with `gh api -X POST repos/<owner>/<repo>/actions/runs/<id>/approve`. Approve only the runs for the PR's latest commit: a stale run approved later cancels the current one (`cancel-in-progress`). The release GitHub App avoids all of this.

### No CI run on the Release PR, or on the template-update PR

Those PRs were opened with `GITHUB_TOKEN`, which can't trigger workflows. Set up the release GitHub App ([Release Process](Release-Process#the-release-github-app)). Meanwhile, closing and reopening the PR by hand triggers CI.

### `uv lock --check` fails on the Release PR

The lock-refresh job didn't run, or was overwritten when release-please force-pushed the branch. Push to `main` again or re-run the *Release* workflow: it refreshes `uv.lock` after every Release PR update.

### "Docs updated with the code" fails, but the change is internal

A reviewer adds the `no-docs-needed` label, and the check is skipped, which counts as passed. If it fires on a path that is never user-facing, change `[docs_touched] watch` in project-template, not locally.

### `generated section is stale`

Code changed the settings, CLI or API: run `uv run scripts/gen-wiki.py` and commit. Never edit between the markers.

### CLI-Reference lists a sub-app but not its commands

Before 0.1.5, `gen-wiki.py` rendered only the root app's commands, without positional arguments: a sub-app (`app.add_typer(sub, name="grp")`) showed as one `grp` entry. Take the template update, run `uv run scripts/gen-wiki.py`, and delete any hand-written table of sub-commands. The update makes `generated section is stale` fail until you do.

### Smoke test: `no answer on /healthz after 30s`, but the container is healthy

The app binds `127.0.0.1`, which can't be reached through a published port. Before 0.1.5 the image used the app's default listen address. Take the template update, which sets `<PREFIX>_LISTEN_HOST=0.0.0.0` in the image, and drop any project-side `ENV` for it from the Dockerfile ([Docker Images](Docker-Images#smoke-test)).

### `listen.host` in `config.yaml` is ignored in the container

The image sets `<PREFIX>_LISTEN_HOST=0.0.0.0`, and environment variables beat the config file. Pass `-e <PREFIX>_LISTEN_HOST=...` instead. `<project> config` shows where each value came from.

### Branch-image cleanup fails with a permissions error

Grant the repository's Actions **Admin** access in the package settings, or add a `PACKAGES_DELETE_TOKEN` secret (`delete:packages`).

### mypy or ruff fail on Python 3.14 only

ruff's output depends on `target-version` (from `python_version`). For example, 3.14 formats `except A, B:` without parentheses. Template-owned scripts avoid version-dependent syntax; in project code, follow what ruff says for your minimum version.
