# Troubleshooting

## Common problems

### Copier: "Task 'sh scripts/bootstrap.sh' returned non-zero exit status"

Usually uv is missing or can't reach the package index. Copier removes the half-made project on a failed task, so re-run with `--skip-tasks`, then run `sh scripts/bootstrap.sh` and read its error.

### The wiki publish job fails with "No wiki repository yet"

The GitHub wiki's git repository exists only after its first page is created in the web UI. Enable the wiki, create any page, and re-run the job: it replaces that page.

### Template update opened an issue, not a PR

The update changes `.github/workflows/`, and without the release GitHub App the workflow can't push those files ("refusing to allow a GitHub App to create or update workflow"). Run `uvx copier update --trust --conflict inline` locally, push a branch and open the PR. Set up the App ([Release Process](Release-Process#the-release-github-app)) to stop this.

### Checks on a bot PR say "action required"

Runs on a PR opened by `github-actions[bot]` wait for a maintainer's approval, after every push to it. Approve them on the PR's Checks tab, or with `gh api -X POST repos/<owner>/<repo>/actions/runs/<id>/approve`. The release GitHub App avoids it.

### No CI run on the Release PR, or on the template-update PR

Those PRs were opened with `GITHUB_TOKEN`, which can't trigger workflows. Set up the release GitHub App ([Release Process](Release-Process#the-release-github-app)). Meanwhile, closing and reopening the PR by hand triggers CI.

### `uv lock --check` fails on the Release PR

The lock-refresh job didn't run, or was overwritten when release-please force-pushed the branch. Push to `main` again or re-run the *Release* workflow: it refreshes `uv.lock` after every Release PR update.

### "Docs updated with the code" fails, but the change is internal

A reviewer adds the `no-docs-needed` label, and the check is skipped, which counts as passed. If it fires on a path that is never user-facing, change `[docs_touched] watch` in project-template, not locally.

### `generated section is stale`

Code changed the settings, CLI or API: run `uv run scripts/gen-wiki.py` and commit. Never edit between the markers.

### Branch-image cleanup fails with a permissions error

Grant the repository's Actions **Admin** access in the package settings, or add a `PACKAGES_DELETE_TOKEN` secret (`delete:packages`).

### mypy or ruff fail on Python 3.14 only

ruff's output depends on `target-version` (from `python_version`). For example, 3.14 formats `except A, B:` without parentheses. Template-owned scripts avoid version-dependent syntax; in project code, follow what ruff says for your minimum version.
