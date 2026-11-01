# Migrating Existing Projects

Projects that predate the template can adopt it. Moving each onto it gives it the shared CI, release and wiki machinery, and future fixes through `copier update`. Do one project at a time, on a branch, as one reviewed PR.

## Steps

1. **Branch and render over the repo.** `_skip_if_exists` keeps existing `src/`, `tests/`, `CHANGELOG.md` and wiki pages. Everything else is offered for overwrite:

   ```sh
   git switch -c chore/adopt-project-template
   uvx copier copy --trust --overwrite -d github_owner=<current-owner> \
       gh:metalayerlab/project-template .
   ```

   Use the repository's current owner while it lives there. Moving it to metalayerlab later is `gh repo transfer` plus another `copier update -d github_owner=metalayerlab`, and the image path changes, so update every consumer (Flux, Compose).
2. **Merge back what is project-specific**, with `git diff` and `git add -p`: dependencies and entry points in `pyproject.toml`, extra Dockerfile stages, extra manifests, README content.
3. **Bring the wiki in with its history,** then let the checker list the gaps:

   ```sh
   git remote add wiki ../<name>.wiki && git fetch wiki
   mv docs/wiki/.standard.toml "$TMPDIR/standard.toml"          # keep the standard
   git rm -rq docs/wiki && git commit -qm "chore: make room for the wiki"
   git subtree add --prefix=docs/wiki wiki master              # the wiki, with its history
   mv "$TMPDIR/standard.toml" docs/wiki/.standard.toml
   python3 scripts/check-wiki.py                             # missing pages and headings
   ```

   Copy missing skeleton pages from a fresh render, and rename headings to the standard's.
4. **Retire the old machinery:** `scripts/bump-version.sh`, `.github/release-template.md`, `src/<pkg>/__version__.py` (change its imports to `from <pkg> import __version__`), `requirements*.txt`, and repo-root compose files (moved to `contrib/docker/`).
5. **Seed release-please** with the current release: set `.release-please-manifest.json` and the `pyproject.toml` version to the latest `vX.Y.Z` tag. The existing `CHANGELOG.md` stays, and new entries go on top.
6. **Make the checks pass:** `uv sync`, then the Definition of done. A backlog of lint, type or coverage failures is fixed in follow-up PRs. Don't relax the template's settings. Where you must, add a temporary per-module mypy override, tracked in `TODO.md`.
7. **GitHub settings,** as in [Quick Start](Quick-Start#create-the-github-repository): squash merge on the PR title, and the ruleset with the new required checks (the workflows create their labels). Put the repository's current topics in `.github/repository.toml` before running `python3 scripts/repo-metadata.py`: it removes topics the file doesn't list (`--check` shows them). Once `wiki.yml` publishes, archive the old `<name>.wiki` clone.

## Common situations

| Situation | What to do |
|---|---|
| Already uv + hatchling, version only in pyproject | Steps 1–2 are mostly merging workflows; keep extra build stages and entrypoints |
| setuptools / pip / `requirements*.txt` | Move to hatchling + uv (`uv add` each runtime dependency, `uv add --dev` the tools), then delete the requirements files |
| black | Replace with `ruff format`; expect one large formatting commit |
| Non-blocking or loose lint and types | Expect a ruff and mypy-strict backlog: temporary per-module overrides, tracked in `TODO.md` |
| An old `requires-python` floor | Raise it to the template's minimum, or answer `python_version` accordingly |
| Several compose files at the repo root | Move them to `contrib/docker/`; extra variants stay as extra files there |
| Privileged workloads (FUSE, DaemonSets) | Keep them as extra manifests; their namespace can't use the *restricted* Pod Security level, so say why in a comment |
| Fixtures captured from real systems | Answer `personal_data_guard=true`. Keep project-specific rules in a script of their own with its own CI step, because the template's guard is template-owned |
| A long-lived integration branch (e.g. `next`) | Replace it with `feat/*` branches into `main`. Merge the wiki clone's branches into `master` (the branch GitHub publishes) before step 3 |
| A notes repository (an Obsidian vault) | `copier copy --trust -d language=obsidian -d vault_dir=<the vault's folder, or .>` into it. An existing `🏠 Home.md` or `📐 Conventions.md` is kept; the vault gains `decisions/`, the base and the record template. Your `README.md` is kept; `.gitignore` comes back as a conflict once: keep your ignore entries. Put your note conventions in `📐 Conventions`; `AGENTS.md` tells assistants to follow them |
| Missing wiki pages or LICENSE | The checker lists missing pages; choose a licence with `license` |
