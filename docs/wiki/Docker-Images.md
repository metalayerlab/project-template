# Docker Images

`ghcr.io/<owner>/<project>`, built by `docker-build.yml` from a multi-stage Dockerfile: a uv builder installs from the lock file into `/opt/venv`, and a slim runtime runs as uid 1000 with a `HEALTHCHECK` and OCI labels (version, revision and created, passed as build args).

## Tags

| Trigger | Tags |
|---|---|
| Release (called by release-please) | `X.Y.Z`, `X.Y`, `X` (from 1.0: a 0.x release gets no `:0`), `latest` |
| Push to `main` | `edge`, `main`, `main-<sha>` |
| Push to `dev/**`, `feat/**` | `<branch>`, `<branch>-<sha>` |
| Pull request | built and smoke-tested, not pushed |
| Manual, with `tag: vX.Y.Z` | that release's semver tags, built with today's Docker files; `latest` only if ticked |

`latest` is only ever set explicitly. An old release rebuilt by hand can't take it over.

## Smoke test

For a service, before anything is pushed, the image is built for the runner and started, and `health_path` must answer within 30 seconds. On failure the container logs are printed. Multi-arch builds (`linux/amd64,linux/arm64`) follow and reuse the cache.

## Cleanup

`docker-cleanup.yml` deletes `dev-*` and `feat-*` tags older than 7 days, daily. It never touches `latest`, `edge`, `main` or releases. It needs the package to grant the repository's Actions **Admin** access, or a `PACKAGES_DELETE_TOKEN` secret.
