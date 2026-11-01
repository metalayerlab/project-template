# Quick Start

## Prerequisites

- [uv](https://docs.astral.sh/uv/). `uvx copier` runs Copier without installing it.
- `git`, and `gh` (authenticated) to create the repository.
- Docker, optional: for running the image and the manifest checks locally.

## Generate the project

```sh
uvx copier copy --trust gh:metalayerlab/project-template my-project
cd my-project
git add -A && git commit -m "chore: initial commit from project-template"
```

`--trust` lets Copier run `scripts/bootstrap.sh`. That script runs `git init`, `uv lock`, fills the generated wiki sections and installs pre-commit hooks if available. Without `--trust`, run `sh scripts/bootstrap.sh` yourself. The questions are explained in [Answering the Questions](Answering-the-Questions).

## Create the GitHub repository

```sh
gh repo create metalayerlab/my-project --private --source . --push
```

The push runs `wiki.yml`, which creates the `no-docs-needed` label; `template-update.yml` creates `template-update` before it uses it.

Then, once per repository, in the GitHub settings:

1. **General → Pull Requests:** allow **squash merging only**, set the default commit message to **"Pull request title"**, and turn on "Automatically delete head branches". The PR title becomes the commit release-please reads. If you set `dependabot_automerge`, also tick **Allow auto-merge** (`gh repo edit --enable-auto-merge`).
2. **Wiki:** enable it and **create the first page** in the web UI (any text). GitHub only creates the wiki's git repository then. From now on `wiki.yml` overwrites it from `docs/wiki/` on every push to `main`.
3. **About box:** `python3 scripts/repo-metadata.py` sets the description, the website (the wiki) and the topics from `.github/repository.toml`, using your `gh` login. Edit the file first if you want other topics. Until you run it, `wiki.yml` warns on every push to `main`.
4. **Rules → Rulesets** for `main`: require a pull request with 1 approval and **review from Code Owners**, block force pushes, and make these checks required: `Secret scan`, `Test (...)`, `Version and lock file`, `Dockerfile and contrib manifests`, `Workflow lint`, `Wiki standard`, `Docs updated with the code`, `conventional-commit`.
   A brain (`language: obsidian`) has no wiki, releases or PR-title check: require `Secret scan`, `Project checks`, `Vault check`, `Repository metadata` and `Workflow lint`, and skip steps 2 and 5. If a scheduled job commits to `main` (a nightly commit of a notes vault), add the repository admin role to the ruleset's bypass list; agents stay denied by `.claude/settings.json`.
5. **Packages:** after the first image is pushed, give the repository's Actions **Admin** access to the package (package settings → Manage Actions access), so branch-image cleanup can delete versions.

The organisation's release GitHub App is set up once for all repositories: see [Release Process](Release-Process#the-release-github-app).

## First build-out with AI

1. Open the project with your assistant. It finds its instructions on its own (see [Working with AI](Working-with-AI#instruction-files)).
2. Paste prompt 1 from `docs/ai/prompts.md`, filling in what the project must do. The assistant writes `docs/design/0001-initial-design.md` and stops.
3. Review the design, then give the second half of prompt 1. The assistant implements in small commits and fills in the wiki.
4. Open PRs from a `feat/...` branch. CI, the wiki checks and a human review ([Human Review Checklist](Human-Review-Checklist)) gate each one.
5. The first `feat:` merged to `main` opens a Release PR for 0.1.0. It is blocked until no wiki page still holds skeleton guidance.
