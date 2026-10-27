# 0001: Template architecture

Status: Approved
Date: 2026-10-27
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Our earlier projects were each copied by hand from one another and drifted. They ended up with
three package managers, three lint strictness levels, two version regexes that disagree, and fixes
(digest output, changelog duplication guard) that landed in only one copy. The team wants one starting
point for new projects that are AI-generated and human-reviewed, with thorough documentation in every
repository.

## Decision

- **Copier**, not a GitHub template repository: `copier update` carries template fixes into existing
  projects as reviewable PRs (`template-update.yml`).
- **release-please** for versioning and CHANGELOG: a Release PR from Conventional Commit PR titles
  (squash-merged and linted). It replaces `bump-version.sh` and the git-log/grep changelog.
- **A language-agnostic core plus language layers.** Python first (uv, hatchling, ruff, mypy strict,
  pytest with an 80% floor), with TypeScript/Node next. The contract is in `layers/README.md`.
- **A standardised wiki in each repository** (`docs/wiki/`): required pages and headings in
  `.standard.toml`, checked by a stdlib script, generated reference sections, docs-touched enforcement,
  strict mode on Release PRs, and a one-way publish to the GitHub wiki.
- **One AI instruction source** (`AGENTS.md`), with thin per-tool pointers and Claude Code permission
  guard rails.
- **Jinja delimiters `[[ ]]` / `[% %]`**, so workflow `${{ }}` needs no escaping.
- **github_owner defaults to metalayerlab.**

## Alternatives considered

- GitHub template repository plus an init script: no update path, which is the drift problem again.
- git-cliff with a dispatch bump workflow: closer to the old flow, but there's no reviewed release step.
- Fixing the home-made changelog: it keeps the bugs' root cause (a regex over git log).
- Keeping the wikis as separate clones: unreviewed and unchecked, the status quo that let pages go missing.
- Helm: Flux with kustomize is the norm in our clusters.

## Consequences

- Template changes affect every project. They go through the template's own Release PR, and the breaking
  ones are marked `!`.
- Release PRs need a GitHub App token to trigger CI (`RELEASE_APP_CLIENT_ID` / `RELEASE_APP_PRIVATE_KEY`).
- Existing projects migrate one at a time (wiki: Migrating-Existing-Projects).
