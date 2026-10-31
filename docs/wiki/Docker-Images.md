# Docker Images

`ghcr.io/<owner>/<project>`, built by `docker-build.yml` from a multi-stage Dockerfile: a builder installs from the lock file (Python: uv into `/opt/venv`; TypeScript: `npm ci`, then `dist/` and the runtime dependencies into `/app`), and a slim runtime runs as uid 1000 with a `HEALTHCHECK` and OCI labels (version, revision and created, passed as build args).

## System packages

A dependency that builds from source needs compilers and headers, and some projects need a library or tool at run time. List them, as Debian/Ubuntu apt package names, in the project-owned `contrib/system-packages.txt`:

```text
build: gcc pkg-config libfuse3-dev
runtime: fuse3 libfuse3-3
```

The `build:` packages are installed in the builder stage, and in CI's test job before the dependencies are installed (see [CI Pipeline](CI-Pipeline)). The `runtime:` packages are installed in the runtime stage, so they are in the image. Both lists are empty by default, and an empty list installs nothing. Repeat a line to add more. Both base images (`python:<v>-slim`, `node:<v>-slim`) are Debian, so the names are Debian's. To run from source, install the `build:` packages yourself; to deploy without the image (systemd), the `runtime:` ones.

## Optional extras

A Python dependency that only the image needs, such as one that compiles against a C library, can stay an optional extra, so the core, its tests and lint need no C toolchain. Name the extras the image installs in the Copier answer `image_extras`:

```sh
uvx copier update --trust -d image_extras='[fuse]'     # or '["*"]' for every extra
```

Both of the builder's `uv sync` lines then get `--extra fuse` (`--all-extras` for `"*"`). It is an answer, not a project file, so the Dockerfile stays template-owned and updates without conflicts ([design 0012](https://github.com/metalayerlab/project-template/blob/main/docs/design/0012-image-extras.md)). CI's test job installs no extras. List the extra's build and runtime apt packages in `contrib/system-packages.txt` as above.

## Tags

| Trigger | Tags |
|---|---|
| Release (called by release-please) | `X.Y.Z`, `X.Y`, `X` (from 1.0: a 0.x release gets no `:0`), `latest` |
| Push to `main` | `edge`, `main`, `main-<sha>` |
| Push to `dev/**`, `feat/**` | `<branch>`, `<branch>-<sha>` |
| Pull request | built and smoke-tested, not pushed |
| Manual, with `tag: vX.Y.Z` | that release's semver tags, built with today's Docker files; `latest` only if ticked |

`latest` is only ever set explicitly. An old release rebuilt by hand can't take it over.

**Visibility:** GHCR creates a new package as **private**, even for a public repository, and anonymous pulls fail with `unauthorized`. After the first push, set it once under the package's *Package settings → Change visibility* (there's no API for this). It stays linked to the repository either way.

## Smoke test

For a service, before anything is pushed, the image is built for the runner and started, and `health_path` must answer within 30 seconds. On failure the container logs are printed. Multi-arch builds (`linux/amd64,linux/arm64`) follow and reuse the cache.

**Ports:** the image `EXPOSE`s `port` and each of `extra_ports`, so `docker run -P` and `docker inspect` see every listener. The `<PREFIX>_LISTEN_HOST` default below covers `port` only: an extra listener's address is the project's own setting, so make it bind `0.0.0.0` in the image too.

**Listen address:** a service image sets `<PREFIX>_LISTEN_HOST=0.0.0.0`, so it's reachable through its published ports whatever the app's own default (a safe `127.0.0.1` default would be unreachable from outside the container). Environment variables beat the config file, so in the image `listen.host` in a mounted `config.yaml` has no effect: pass `-e <PREFIX>_LISTEN_HOST=...` instead. That matters with `--network host`, where `0.0.0.0` is every interface of the host.

## Cleanup

`docker-cleanup.yml` deletes `dev-*` and `feat-*` tags older than 7 days, daily. It never touches `latest`, `edge`, `main` or releases. It needs the package to grant the repository's Actions **Admin** access, or a `PACKAGES_DELETE_TOKEN` secret.
