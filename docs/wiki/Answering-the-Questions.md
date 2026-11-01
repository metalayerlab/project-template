# Answering the Questions

Copier asks these when you run `copier copy`. Pass answers non-interactively with `-d key=value`, for example `-d kind=cli`. The answers are saved in `.copier-answers.yml`, and `copier update` reuses them. To change one later, run `copier update --trust --skip-tasks -d key=new-value`, or `copier update --trust --skip-tasks --vcs-ref=HEAD -A` to answer everything again.

## Questions

| Question | Default | Notes |
|---|---|---|
| `language` | `python` | The language layer: `python`, `typescript` (Node.js and npm, [design 0009](https://github.com/metalayerlab/project-template/blob/main/docs/design/0009-typescript-layer.md)), `obsidian` for a notes repository (below), or `none` for a language without a layer yet. `none` gives the core only (release-please, CI's secret scan and wiki checks, the wiki, AGENTS.md) and a project-owned `scripts/check.sh` for your own checks. `kind` is then `other`, which skips every question after it up to `code_owners` and builds no image ([design 0008](https://github.com/metalayerlab/project-template/blob/main/docs/design/0008-no-language-layer.md)). `obsidian` asks `vault_dir` instead of `kind`, which is always `brain`: an Obsidian vault with the agent guard rails (`AGENTS.md`, `.claude/settings.json`, the boundary hook, the secret scan, template updates) and no releases, wiki, image or markdownlint. The vault is its wiki, and its design records are notes in it ([design 0016](https://github.com/metalayerlab/project-template/blob/main/docs/design/0016-obsidian-layer.md)) |
| `project_name` | (none) | kebab-case. Used for the repo, image, CLI command, systemd unit and k8s namespace |
| `package_name` | from `project_name` | Python only: the import name, snake_case. A TypeScript package is named `project_name` |
| `description` | (none) | One line, any length; quotes are fine. Appears in the README, the package manifest, OCI labels and the wiki footer. The CLI's `--help` and the API's OpenAPI document read it from the manifest at run time |
| `github_owner` | `metalayerlab` | Organisation or user. Sets the image path and all links |
| `kind` | `service` | `service`: long-running HTTP app (FastAPI, or Fastify for TypeScript) with health endpoints and a `serve` command. `cli`: a command (Typer, or commander). `library`: import only, with no CLI, image or contrib. `web` (TypeScript only): a Vite + React single-page app with React Router, configured at run time by `/config.json` and served by nginx; no CLI ([design 0014](https://github.com/metalayerlab/project-template/blob/main/docs/design/0014-web-kind.md)). With `language: none`: `other` only, no generated code. Not asked for `obsidian`: always `brain` |
| `vault_dir` | `knowledge` | `obsidian` only. The vault's folder: one folder name, or `.` for the repository root. The default leaves room beside the vault for scripts and git-ignored folders; `.` suits a repository that is nothing but a vault |
| `python_version` | `3.13` | Python only. Minimum version: the Docker base image and the first CI matrix entry. CI also tests every newer supported version |
| `node_version` | `24` | TypeScript only. Minimum Node.js LTS line (`24` or `26`): the Docker base image and the first CI matrix entry. CI also tests every newer one |
| `port` | `8080` | service and web (nginx's port) |
| `extra_ports` | `[]` | service only. Other TCP ports it listens on, e.g. `[3128]`: exposed by the image and published by Compose and Kubernetes ([Contrib Manifests](Contrib-Manifests)). Each is 1–65535, listed once, and not `port` |
| `health_path` | `/healthz` | service and web (answered by nginx): the liveness route, Docker `HEALTHCHECK`, k8s liveness probe and CI smoke test |
| `container_image` | yes (no for library) | Builds and publishes to GHCR |
| `multi_arch` | yes | Adds `linux/arm64` (built with QEMU; slower) |
| `image_extras` | `[]` | Python with an image only. Optional extras (`[project.optional-dependencies]`) the image installs, e.g. `[fuse]`, or `["*"]` for all of them. CI's tests don't install them ([Docker Images](Docker-Images#optional-extras)) |
| `contrib` | all three for a service; `docker` and `k8s` for web | `docker`, `k8s`, `systemd` (service only): see [Contrib Manifests](Contrib-Manifests) |
| `puid_pgid` | no | No: the image runs as `USER 1000:1000`. Yes: the container starts as root to chown the state directory, then drops to `PUID:PGID`, for hosts where bind-mounted state must match a host user. Either way it runs as uid 1000 under Kubernetes |
| `timezone` | `Europe/London` | `TZ` in the Compose, k8s and systemd manifests |
| `code_owners` | `@<owner>/maintainers` | CODEOWNERS for every path. The team must exist and have write access |
| `dependabot_automerge` | `off` | `patch` or `minor`: Dependabot PRs up to that level get auto-merge queued, so a code owner's **Approve** merges them as soon as the required checks pass. Majors, and updates Dependabot can't classify, are merged by hand. Nothing is merged without a human approval. Needs repository settings: see [Quick Start](Quick-Start#create-the-github-repository) and [design 0003](https://github.com/metalayerlab/project-template/blob/main/docs/design/0003-dependabot-automerge.md) |
| `license` | `Unlicense` (`Proprietary` for `obsidian`) | `Unlicense`, `MIT`, `Apache-2.0`, `Proprietary` |
| `copyright_holder` | the owner | Not asked for the Unlicense |
| `personal_data_guard` | no | A CI job that fails on public IPv4 addresses or on strings from a `PERSONAL_DATA_DENYLIST` secret. Use it when tests carry fixtures captured from real systems |
| `integration_ci` | no | Python only. Adds CI's **Integration tests** job: it installs both lists in `contrib/system-packages.txt` (`build:` and `runtime:`), runs the tests marked `integration` with `RUN_INTEGRATION=1`, and fails if none runs or one is skipped ([CI Pipeline](CI-Pipeline#integration-tests), [design 0017](https://github.com/metalayerlab/project-template/blob/main/docs/design/0017-integration-ci-job.md)) |
| `integration_extras` | `[]` | With `integration_ci` only. Optional extras the job installs, e.g. `[fuse]`, or `["*"]` for all of them. Separate from `image_extras`: the image and the tests can need different extras |

## Derived values

Never asked, and computed from the answers: `env_prefix` (`MY_PROJECT_`, for every setting's environment variable), `image` (`ghcr.io/<owner>/<project_name>`), `repo_url`, `has_cli` (service or cli), and `copyright_year`.
