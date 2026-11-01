# 0017: An opt-in integration test job in CI

Status: Implemented
Date: 2026-11-01
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

Generated Python projects split their tests: `tests/integration/` is marked `integration` and skipped unless
`RUN_INTEGRATION=1`, so `pytest` stays fast and offline. Nothing in CI runs them. metalayerlab/sluice's need a
real FUSE mount: the `fuse` extra (pyfuse3), the `build:` packages in `contrib/system-packages.txt` to compile
it, and `fuse3` (a `runtime:` package) for `fusermount3`. `ubuntu-latest` has `/dev/fuse`, so they can run
on hosted runners, but `ci.yml` is template-owned and has no place for the job. sluice carries a
project-owned `integration.yml` until the template has one (#81).

The job must fail, never pass vacuously: when it is on and no test runs, or a test skips because a package
or device is missing.

Constraints: a project that doesn't use it sees **no diff** on update, and the answers file is a public
interface (design records [0005](0005-extra-ports.md), [0012](0012-image-extras.md)).

## Decision

- **Copier question `integration_ci`**: `type: bool`, default `false`, asked only when
  `language == 'python'`. Its validator rejects `true` for any other language, so a `-d integration_ci=true`
  for TypeScript fails instead of rendering nothing.
- **Copier question `integration_extras`**: `type: yaml`, default `[]`, asked only when `integration_ci`. A
  list of extra names, or `["*"]` for all, with `image_extras`'s validator (names start with a letter or
  digit and use only letters, digits, `.`, `_` and `-`; `"*"` stands alone; no repeats), plus: not without
  `integration_ci`. A separate answer from `image_extras`: the image and the tests can need different extras.
- **Rendering**, in the Python layer's `ci/jobs.yml` fragment (the core's `ci.yml` is unchanged): a job
  `integration`, named **Integration tests**, on the minimum Python version:
  1. installs both lists in `contrib/system-packages.txt`, `build:` and `runtime:`, by the same `sed` as the
     Test job (none listed: nothing installed);
  2. `uv sync --locked`, with `--extra <name>` per name or `--all-extras` (an undefined extra fails `uv`);
  3. `RUN_INTEGRATION=1 uv run pytest -m integration --no-cov --junitxml=$RUNNER_TEMP/integration.xml`:
     pytest exits 5 when no test is selected, which fails the step. `--no-cov`, because the coverage floor
     belongs to the unit tests: a subset of tests can't meet it;
  4. a step that reads the JUnit report and fails, naming each one, if any test was skipped (an `xfail`
     is not a skip).
- **Other layers**: no question, no job. TypeScript has `npm run test:integration`, but vitest passes with no
  tests in that mode (`passWithNoTests`), so its job needs its own "fail when empty" design; a TypeScript
  project that needs it opens an issue.
- **Wiki for new projects**: the Python layer's Testing-Guide fragment says the job runs, when it is on.
- **Tests**: `test_integration_ci` (off, on, two extras, `"*"`), `test_integration_ci_rejected` (another
  language, extras without the job, and `image_extras`'s bad values), and
  `test_integration_job_fails_rather_than_skips`, which runs the rendered steps against no tests, passing
  tests with an `xfail`, and a skipped test. The `service-min` variant turns it on, so actionlint and the
  wiki checks see the job.

## Alternatives considered

- **Only the `build:` packages, as the Test job installs**: `fusermount3` is a `runtime:` package, so the
  tests couldn't mount. A third list (`test:`) in `contrib/system-packages.txt` would make every project's
  file and the image's parser change for one job; the runtime list is what the installed project needs, and
  the tests run the installed project.
- **A project-owned `.github/workflows/integration.yml`** seeded by the template: it would never receive
  fixes (pins, the skip check), which is why `ci.yml` is template-owned.
- **One answer, `integration_ci: [fuse]`** (a list meaning on): `[]` would have to mean "on, no extras",
  so "off" needs another value of another type. Two answers each have one type.
- **Reusing `image_extras` for the job**: the image and the tests can need different extras, and a project
  without an image (a library) has no `image_extras`.
- **Running integration tests inside the Test job** (one matrix entry with `RUN_INTEGRATION=1`): the
  integration tests would count towards the coverage floor and slow every matrix entry's feedback, and a
  failure would not say which kind of test failed.
- **Failing on skips with a project-side hook** (the integration `conftest.py`): `tests/**` is
  project-owned, so existing projects would never receive it.

## Consequences

- Turning the job on is one answer: `copier update -d integration_ci=true -d integration_extras='[fuse]'`.
  The project lists the packages in `contrib/system-packages.txt` and makes `Integration tests` a required
  check.
- Both answers are permanent once given; changing their shape needs a migration.
- A test that skips on a missing precondition fails the job: projects that want a test skipped in CI mark
  it `xfail`, or leave it unmarked by `integration`.
- Wiki: Answering-the-Questions (both questions), CI-Pipeline (the job and the required check),
  Updating-from-the-Template (the command).

## Resolved questions

1. **Which Python versions?** The minimum only: the integration tests check the system around the code,
   and the Test job already checks every version.
2. **Python only?** Yes, until a TypeScript project asks: it needs a "fail when empty" of its own.
