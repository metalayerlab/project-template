# 0010: Repository metadata

Status: Implemented
Date: 2026-10-30
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

A repository's About box on GitHub has a description, a website and topics. The template sets none of them, so
generated projects end up with the defaults:

- **No website.** The project's documentation is its wiki (0001), but nothing in the About box links to it.
- **No topics.** They are how a project is found, on GitHub and across the owner's own repositories, and
  nobody remembers to add them after creating a repository.
- **Drift.** The description shown on GitHub and the Copier `description` answer (used in the README, the
  package manifest and the wiki footer) are set in two places and diverge over time.

Constraints:

- `GITHUB_TOKEN` can **read** this metadata (`GET /repos/{owner}/{repo}` needs only `metadata: read`) but cannot
  **write** it: editing it needs `administration: write`, which `GITHUB_TOKEN` can't be given. Writing from CI
  would need a personal access token or a GitHub App secret in every project.
- The template stores no secrets (0001). An admin-scoped token in every repository is a big risk to take for
  a small benefit.
- Adding this must not turn existing projects' CI red when they update.

## Decision

Keep the metadata in a file in the repository, apply it with the maintainer's own `gh` login, and have CI
**warn** when the repository on GitHub doesn't match the file.

### The file: `.github/repository.toml` (project-owned)

```toml
# The repository's About box on GitHub. Apply with: python3 scripts/repo-metadata.py
description = "<description answer>"
homepage = "<repo_url>/wiki"
topics = ["<layer.topic>", "<kind>"]
```

- It's project-owned (added to `_skip_if_exists`) because the project changes its topics as it grows.
  The template seeds the file and never touches it again.
- `homepage` defaults to the wiki. A project with a docs site or a product page changes it.
- `topics` start as the language and the `kind`, without `other`. GitHub's rules apply: lowercase letters,
  digits and hyphens, at most 50 characters each, at most 20 topics. The script rejects anything else.

### A new layer value: `topic`

| Layer | `topic` |
|---|---|
| `python` | `python` |
| `typescript` | `typescript` |
| `none` | `''` (skipped) |

This keeps language names out of core files: `test_layers.py` would flag a `language == ...` branch.
`layers/README.md` gets one more row.

### The script: `scripts/repo-metadata.py` (template-owned, Python standard library only)

The script is written in core Python, as `check-wiki.py` is, so it runs in every variant, `none` included.

- `python3 scripts/repo-metadata.py` **applies** the file with `gh`:
  `gh repo edit --description … --homepage … --enable-wiki`, then sets the topics to exactly the file's list
  (`PUT /repos/{owner}/{repo}/topics`), so topics added in the web UI and not in the file are removed.
  The CI warning lists them first.
- `--check` **compares** the file with the live repository (`gh api`, so `GITHUB_TOKEN` in CI and your login
  locally), prints each difference, and exits 1 if there are any or GitHub can't be read.
- `--validate` checks the file only, offline. The `check` job of `wiki.yml` runs it on every PR, so an invalid
  file is caught before it reaches main.
- Every mode exits 2 if the file is invalid.

### CI: a warning, not a failure

A step after "Mirror docs/wiki/" in the `publish` job of `wiki.yml`. The job already runs only on pushes to main and
already depends on the wiki existing:

```yaml
- name: Repository metadata matches .github/repository.toml?
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    rc=0; python3 scripts/repo-metadata.py --check || rc=$?
    if [ "$rc" = 1 ]; then
      echo "::warning::GitHub's About box differs from .github/repository.toml: run python3 scripts/repo-metadata.py"
    elif [ "$rc" != 0 ]; then exit "$rc"; fi
```

The step runs after the mirror, so a metadata problem can never stop the wiki being published.
An invalid file is a mistake the project makes, so it fails the step: `--check` exits 2, and the step lets
that through. Only drift (or GitHub being unreachable) is turned into a warning.

### Where it's documented, and the template itself

- The template's wiki: Quick-Start (run the script once after creating the repository and its first wiki
  page), Project-Layout (the file and script), CI-Pipeline (the warning), Migrating-Existing-Projects.
- No change to `template/AGENTS.md.jinja` (0 characters), and no new required wiki page or heading.
- This repository gets its own `.github/repository.toml`, and its own `wiki.yml` runs the same two steps with
  `template/scripts/repo-metadata.py`.
- Tests: `test_repository_metadata` renders each variant's file and runs `--check` (no drift, then drift) and
  the apply against a stand-in `gh`.

## Alternatives considered

- **CI applies it (B).** It needs a token or GitHub App with admin rights stored as a secret in every
  project. Rejected for now. The file format doesn't depend on who applies it, so a later record can add this
  as an opt-in.
- **A settings app (Probot `settings`, `.github/settings.yml`) (C).** This brings in an outside service that
  controls far more than three fields (branch protection, collaborators, labels). Rejected.
- **Fail CI on drift.** The fix needs admin rights and is outside any PR, so a red build would land on
  whoever pushed next. It would become noise people learn to ignore. Rejected.
- **Topics from the package manifest's keywords** (`pyproject.toml`, `package.json`). That would be one
  source per language, but `none` has no manifest, and the core would need a parser for each language.
  Rejected.
- **Copier answers for the topics.** They would be fixed at copy time, while topics keep changing.
  Updating them would mean `copier update -d`. Rejected.

## Consequences

- New projects get a wiki link and topics in their About box after running one command. Without that, CI
  shows a warning on every push to main until they do.
- **Existing projects** receive the file and the script on their next `copier update`, and the warning shows
  until they run the script once. CI doesn't go red.
- The file, not the web UI, decides the description, website and topics. A change made in the web UI is
  reported by the warning, and the next run of the script removes it.
- The layer contract gains `topic`.
- `feat:`, not breaking.

## Open questions

Implemented as recommended below.

1. **Should `bootstrap.sh` run the script?** I recommend **no**. Bootstrap runs at `copier copy`, before the
   GitHub repository usually exists, and again on every `copier update`. Changing GitHub settings without being
   asked during an update is a surprising side effect. Quick-Start and the CI warning are enough to prompt it.
2. **Should the script also set other repository settings** (squash-only merges, deleting merged branches,
   disabling Projects)? I recommend **not yet**. Those are a separate change to what projects get. The file can
   take a `[settings]` table later without breaking anything.
3. **Should the default topics include the license or `copier-template`?** I recommend **no**. They'd be noise
   in search; the language and `kind` are what people actually search for.
