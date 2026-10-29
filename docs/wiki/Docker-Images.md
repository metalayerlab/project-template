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

**Visibility:** GHCR creates a new package as **private**, even for a public repository, and anonymous pulls fail with `unauthorized`. After the first push, set it once under the package's *Package settings → Change visibility* (there's no API for this). It stays linked to the repository either way.

## Smoke test

For a service, before anything is pushed, the image is built for the runner and started, and `health_path` must answer within 30 seconds. On failure the container logs are printed. Multi-arch builds (`linux/amd64,linux/arm64`) follow and reuse the cache.

**Listen address:** a service image sets `<PREFIX>_LISTEN_HOST=0.0.0.0`, so it's reachable through its published ports whatever the app's own default (a safe `127.0.0.1` default would be unreachable from outside the container). Environment variables beat the config file, so in the image `listen.host` in a mounted `config.yaml` has no effect: pass `-e <PREFIX>_LISTEN_HOST=...` instead. That matters with `--network host`, where `0.0.0.0` is every interface of the host.

## Cleanup

`docker-cleanup.yml` deletes `dev-*` and `feat-*` tags older than 7 days, daily. It never touches `latest`, `edge`, `main` or releases. It needs the package to grant the repository's Actions **Admin** access, or a `PACKAGES_DELETE_TOKEN` secret.
