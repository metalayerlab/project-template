# Contrib Manifests

`contrib/` holds deployment manifests, versioned with the code. Each is hardened by default. release-please moves the image tag in Compose and kustomize to every release (`# x-release-please-version` markers). `contrib/<name>.example.yaml` documents every setting with its default.

## Docker Compose

`contrib/docker/compose.yml`, with no obsolete `version:` key:

- Pinned to the release tag, and the port bound to `127.0.0.1` only (Traefik goes in front). So is each of `extra_ports`: publishing one on other interfaces is a deliberate edit.
- `./config` mounted read-only, `./state` for state, secrets as files via `<PREFIX>_<KEY>_FILE`.
- A read-only root, `no-new-privileges`, and `cap_drop: [ALL]`. With `puid_pgid`, only the capabilities the entrypoint needs to chown and drop privileges are added back.

## Kubernetes

`contrib/k8s/`, a kustomize base (no Helm), ready to apply directly or to reference from a Flux overlay with `?ref=vX.Y.Z`:

- A Namespace with the *restricted* Pod Security Standard enforced.
- A Deployment: `runAsNonRoot`, uid 1000, `readOnlyRootFilesystem`, `capabilities: drop [ALL]`, `seccompProfile: RuntimeDefault`, `automountServiceAccountToken: false`, readiness on `/readyz`, liveness on `health_path`, requests/limits, and `Recreate` (state is single-writer).
- A Service, and a NetworkPolicy admitting only the `traefik` namespace. Each of `extra_ports` is a named port (`tcp-3128`) in the Deployment and the Service, and a commented-out NetworkPolicy rule: an extra listener usually serves in-cluster clients rather than the ingress controller, so nothing reaches it until you uncomment the rule and name those clients.
- A ConfigMap generated from `config.yaml`; its hash suffix rolls the Deployment on change. Secrets are never in the base: SOPS in the GitOps repo, mounted as files.
- For `kind: web`: both probes on `health_path`, the default rolling update (no state), `config.json` from the ConfigMap mounted by `subPath` over the image's copy, and an `emptyDir` on `/tmp` for nginx. Its Compose file mounts `./config.json` the same way, with no state volume or environment.

## systemd

`contrib/systemd/<name>.service` plus `<name>.sysusers`:

- A dedicated system user, `StateDirectory=`, `ConfigurationDirectory=`, `UMask=0077`.
- The full sandbox: `ProtectSystem=strict`, `ProtectHome`, no capabilities, `PrivateTmp`/`PrivateDevices`, the kernel protections, `RestrictAddressFamilies`, `MemoryDenyWriteExecute`, `SystemCallFilter=@system-service`.
- The install steps are in the unit's header and on the project's Deployment wiki page. The venv lives in `/opt/<name>`, outside `/home`, because of `ProtectHome`.

## Validation

`scripts/check-manifests.sh`, run by CI's manifests job (and locally, where it skips missing tools):

| Check | Tool |
|---|---|
| Dockerfile | hadolint |
| Compose | `docker compose config --quiet` |
| Kubernetes | `kubectl kustomize` piped into `kubeconform -strict` |
| systemd | `systemd-analyze verify` (on a copy whose `ExecStart` is `/bin/true`) |

Project-specific needs (a privileged DaemonSet, FUSE, a sidecar) are added in the project. Loosen hardening only with a comment saying why: the review checklist asks about it.
