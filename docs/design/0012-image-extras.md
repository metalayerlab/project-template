# 0012: Optional extras in the image

Status: Implemented
Date: 2026-10-31
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

metalayerlab/sluice keeps `pyfuse3` as an optional extra (`sluice[fuse]`): it compiles against libfuse3,
and the core, its unit tests and lint shouldn't need a C toolchain. The image needs the extra, so the
template-owned Dockerfile carried a local edit, `--extra fuse` on both of the builder's `uv sync` lines. That
edit conflicts with every template change to those lines (#63).

Constraints: projects without extras must see **no diff** on update, and the answers file is a public
interface (design [0005](0005-extra-ports.md)).

## Decision

- **Copier question `image_extras`**, asked only when `container_image and language == 'python'`:
  - `type: yaml`, default `[]`: a list of extra names, e.g. `[fuse]`, or `["*"]` for all of them.
  - Validator: a list of non-empty strings, no repeats; each starts with a letter or digit and uses only
    letters, digits, `.`, `_` and `-` (so nothing reaches the `RUN` line as a flag or shell syntax); `"*"`
    stands alone.
  - Help: what an extra is, the `["*"]` form, and that CI's tests don't install them.
- **Rendering**, in `layers/python/docker/builder.Dockerfile.jinja`: both `uv sync` lines get
  `--extra <name>` for each name, or `--all-extras` for `["*"]`, plus a one-line comment naming the answer.
  With `[]` the rendered Dockerfile is byte-for-byte unchanged.
- **CI is unchanged**: `uv sync --locked` in the test job installs no extras, which is the point of an extra.
  A project that wants its extra tested adds a job of its own.
- **Tests**: `test_image_extras` (none, two names, `"*"`), `test_image_extras_rejected`, and under
  `-m docker` `test_image_installs_extras`, which adds an extra to a rendered project, locks it and imports it
  in the image.

## Alternatives considered

- **A project-owned `contrib/image-extras.txt`**, read in the Dockerfile like `contrib/system-packages.txt`
  (#53): a `--mount=type=bind` and shell parsing on two `RUN` lines, and a new file and AGENTS.md row in every
  project. The apt lists are project data the template never touches; which extras the image installs is a
  build fact, like `extra_ports`, and a Copier answer renders it with no parsing.
- **A build arg** (`ARG EXTRAS`): `docker-build.yml` is template-owned, so the value would have nowhere to live.
- **Reading extras from `pyproject.toml`** (a `[tool.<project>]` table): non-standard, and needs a TOML parse
  in the build.

## Consequences

- Installing an extra in the image is one answer: `copier update -d image_extras='[fuse]'`.
- The question is permanent once answered; changing its shape later needs a migration.
- The extra's apt packages still go in `contrib/system-packages.txt`.
- Wiki: Answering-the-Questions (the question), Docker-Images (*Optional extras*), Updating-from-the-Template
  (the command).

## Resolved questions

1. **File or answer?** An answer: no parsing, no new project file, no AGENTS.md characters.
2. **`--all-extras`?** Yes, as `["*"]`: one form for "everything", and the validator keeps it alone.
