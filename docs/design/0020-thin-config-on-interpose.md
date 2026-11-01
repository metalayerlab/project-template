# 0020: A thin `config.py` on interpose's settings engine

<!-- Add a line for this record to the index in docs/design/README.md (CI checks). -->

Status: Proposed
Date: 2026-11-01
Authors: Stephen Cox

## Context

Every Python `service` and `cli` project gets its own copy of the settings engine in
`src/<pkg>/config.py`: `Setting`, the lookup order, `_coerce`, `resolve`, `read_file` and `ConfigError`.
`src/**` is in `_skip_if_exists`, so the copy is project-owned from the first render, and a template fix
never reaches it. Issue #84 records the drift between the template, sluice and mitm-proxy (silent `0` for a
YAML `0.5`, a Python repr for a list given to a string setting, list settings in one project only). Part 1
of #84 fixed the template's copy and added `is_list`; existing projects still apply both by hand
([Updating from the Template](../wiki/Updating-from-the-Template.md#fixes-to-project-owned-files)).

[metalayerlab/interpose](https://github.com/metalayerlab/interpose) is the shared library for that engine.
Its design 0001 (Proposed) defines v0.1: `interpose.settings` (`Setting`, `Settings(prefix, settings,
default_path=...)`, `Settings.resolve() -> Resolved(values, sources)`, `ConfigError`, single-value checks)
and `interpose.secret` (`Secret`, `read_secret_dir`), with the template's lookup order, the same coercion
rules as Part 1, pyyaml as the only dependency, and consumers pinning a GitHub tag. No tag exists yet.

Constraints:

- The lookup order (`<PREFIX><KEY>_FILE` > `<PREFIX><KEY>` > YAML file > default), the env var names and
  the `config` command's output are the contract every project's `AGENTS.md` and wiki document. They don't
  change.
- `scripts/gen-wiki.py` is template-owned and runs in every Python project, migrated or not, so it must
  read both a project's own `Setting` and interpose's.
- `config.py` stays under `src/**`, so it stays project-owned. Only the engine moves out of it.
- The generated code stays small ([AGENTS.md](../../AGENTS.md#rules)).
- TypeScript projects have their own engine (`src/config.ts`) and no shared library. This record is Python only.

## Decision

Once interpose v0.1.0 is tagged:

1. **`config.py.jinja` shrinks** to the project's settings, its `Config` dataclass and `load_config`:

   ```python
   from interpose.settings import ConfigError, Setting, Settings, one_of

   SETTINGS = Settings(
       "[[ env_prefix ]]",
       (Setting("log_level", "INFO", "Log level: ...", check=one_of(*LOG_LEVELS)), ...),
       default_path=Path("/etc/[[ project_name ]]/config.yaml"),
   )
   CONFIG_ENV = SETTINGS.config_env

   def load_config(path=None, environ=None) -> Config:
       r = SETTINGS.resolve(path, environ)
       # cross-setting rules here
       return Config(log_level=str(r.values["log_level"]).upper(), ..., sources=dict(r.sources))
   ```

   It re-exports `ConfigError`, `SETTINGS` and `CONFIG_ENV`, so `cli.py` and its tests are unchanged.
   `test_config.py.jinja` keeps the tests of the project's own behaviour (the lookup order end to end, the
   log level and port checks) and drops the engine's (`_coerce`, list parsing), which interpose tests.

2. **The dependency.** `pyproject.toml.jinja` adds
   `"interpose @ git+https://github.com/metalayerlab/interpose@v0.1.0"` for `has_cli` kinds, beside
   `pyyaml`, which interpose then brings. `pyproject.toml` is a shared file, so an update merges the line
   into existing projects. The Python layer adds `git` to the builder stage's packages if uv needs it to
   fetch the tag (see open question 2).

3. **`gen-wiki.py` reads the public API.** The `settings` block iterates `config.SETTINGS` and reads only
   `key`, `env`, `default`, `help`, `secret` and `is_list`, the attributes interpose's `Setting` documents
   as public. A project that hasn't migrated has the same attributes, so one script serves both. It never
   reads `_coerce`, `ENV_PREFIX` or other internals.

4. **Updates.** Dependabot's `uv` ecosystem, already in every Python project, proposes interpose bumps. A
   template release bumps the pin for new projects only; existing projects follow Dependabot.

5. **Wiki.** [Project Layout](../wiki/Project-Layout.md) says `config.py` holds the project's settings
   and the engine is the interpose dependency. [Updating from the Template](../wiki/Updating-from-the-Template.md)
   says engine fixes arrive as Dependabot PRs, not template update PRs, and gives the migration below.
   The generated In-Depth-Configuration page is unchanged: users see the same settings.

### Migration for existing projects

`config.py` and `tests/**` are project-owned, so the update PR can't rewrite them. It brings the
`pyproject.toml` dependency and the `gen-wiki.py` that reads either shape. The project then:

1. replaces the engine in `config.py` with the `Settings(...)` call above, keeping its `SETTINGS` entries,
   `Config` and `load_config`'s cross-setting rules;
2. moves single-value checks it wrote by hand (ports, choices) to `check=`;
3. deletes its engine tests, keeping its own behaviour tests;
4. runs its Definition of done: config keys, env vars and `config` output are unchanged.

A project that skips this keeps working on its own copy, and loses nothing but future engine fixes.

## Alternatives considered

- **A template-owned engine file (`src/<pkg>/_settings.py`, outside `_skip_if_exists`):** fixes the drift
  with no dependency, and was weighed in interpose's 0001. It lost there because `Secret`, metrics and the
  pipeline core don't belong in every project, and it ties engine fixes to the template's release cadence.
  It also carves an exception into `src/**`.
- **Keep the engine in `config.py` and fix copies by hand:** the status quo #84 exists to end.
- **Vendor interpose's source with a sync workflow:** a second update channel beside Dependabot, for code
  that installs as a package anyway.
- **Depend on a release archive URL (`.../archive/refs/tags/v0.1.0.tar.gz`):** needs no `git` in the
  image, but Dependabot doesn't update URL dependencies. Kept as the fallback for open question 2.
- **interpose for TypeScript too:** no TypeScript consumer shares the drift yet.

## Consequences

- One coercion behaviour in every migrated project, and new projects start migrated.
- The skeleton's `config.py` and its tests get shorter; the engine's tests live in interpose, whose
  coverage now guards every consumer.
- Every Python CLI and service needs network access to GitHub to lock and build, as it already does for PyPI.
- `secret=True` values resolve to `Secret` (interpose 0001, open question 1). The skeleton has no secret
  setting, so only projects that added one change `Config` to hold `Secret` and call `.reveal()`.
- Rollback: pin the previous interpose tag, or keep a project on its own copy.
- Wiki pages: Project-Layout, Updating-from-the-Template (this repo). Generated projects' pages don't change.

## Open questions

1. **Approve before or after interpose v0.1.0 is tagged?** Recommend after: this record depends on
   interpose's `Settings` and `Setting` signatures, which its 0001 can still change.
2. **Does Dependabot's `uv` support update a `git+https` dependency pinned to a tag, and does the
   builder stage need `git`?** interpose 0001 leaves the first unverified. Recommend testing both on one
   consumer (sluice) before approval. If Dependabot can't, the fallback is a small scheduled workflow that
   opens a PR when interpose has a newer tag.
3. **Should the template update PR say when a project's `config.py` still has its own engine?** Recommend
   no check: a line in Updating-from-the-Template is enough, and a check would fail projects that chose
   to keep their copy.
