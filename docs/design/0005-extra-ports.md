# 0005: Extra listener ports

Status: Implemented
Date: 2026-10-29
Authors: Stephen Cox; drafted by Claude (Opus 5.5)

## Context

A `service` has one port, the Copier answer `port` (default 8080), rendered into five template-owned files:

| File | Today |
|---|---|
| `Dockerfile` | `EXPOSE [[ port ]]` |
| `contrib/docker/compose.yml` | `"127.0.0.1:[[ port ]]:[[ port ]]"` |
| `contrib/k8s/deployment.yaml` | `containerPort: [[ port ]]`, named `http` (the probes use the name) |
| `contrib/k8s/service.yaml` | `port: [[ port ]]`, `targetPort: http` |
| `contrib/k8s/networkpolicy.yaml` | ingress on `[[ port ]]` from the `traefik` namespace only |

metalayerlab/mitm-proxy also listens on 3128 (the proxy itself). It can't declare that without editing
those files, and every template update would then conflict with or drop the edit (#20). Image metadata and
`docker run -P` miss the port.

Constraints: projects with a single listener must see **no diff** on update. The answers file is a public
interface: once a project has answered, a renamed or reshaped question breaks its `copier update`.

## Decision

- **Copier question `extra_ports`**, asked only when `kind == 'service'`:
  - `type: yaml`, default `[]`: a list of TCP port numbers, e.g. `[3128]`.
  - Validator: every entry is an int in 1–65535, none repeats, and none equals `port`.
  - Help: "Other TCP ports the service listens on, besides `port` (for example `[3128]`). Each is exposed by
    the image and published by the contrib manifests."
- **Rendering**, for each extra port `P`, in order:
  - Dockerfile: `EXPOSE [[ port ]] P …` on the existing line.
  - compose: `"127.0.0.1:P:P"`, loopback like `port`.
  - Deployment and Service: a port named `tcp-P` (at most 9 characters, inside k8s' 15-character limit),
    with `targetPort: tcp-P`.
  - NetworkPolicy: a **second** ingress rule for the extra ports, with no `from`, commented out, and a
    comment explaining why. Extra listeners usually serve in-cluster clients, not the ingress controller, and
    the template can't know which: the default stays deny, and the project uncomments and fills `from`.
- **With `extra_ports: []`** every file renders byte-for-byte as before (checked against v0.1.6 when this
  was built). `test_extra_ports` guards it: a variant without extra ports has no `tcp-` port and no
  `extra_ports` comment in any of the five files. `EXPOSE` is an expression
  (`[[ ([port] + extra_ports) | join(' ') ]]`), not a `for` block, because `trim_blocks` would eat its newline.
- **Not covered:** the listen address of an extra listener. Its setting belongs to the project's own config
  (`config.py` is project-owned), so the #19 `<PREFIX>_LISTEN_HOST=0.0.0.0` default doesn't apply to it. The
  wiki says to bind `0.0.0.0` in the image, the same way.
- **Tests**: the `service` variant sets `extra_ports: [3128]`, and `check-manifests.sh` passes on it.
  `test_extra_ports` checks each file, `test_extra_ports_rejected` each kind of invalid answer, and under
  `-m docker` `test_image_runs` checks that `docker inspect` lists `3128/tcp`.

## Alternatives considered

- **A list of `{name, port}` pairs**: readable k8s port names (`proxy` rather than `tcp-3128`), but a
  longer answer to type, and a name answer that k8s can reject (15 characters, lower-case DNS label).
  `tcp-P` is always valid. A later `extra_port_names` can add names without breaking existing answers.
- **A project-owned include file** (e.g. `contrib/ports.yaml`) that the template files read: no new
  question, but Copier renders templates at update time, not from project files, so the template can't
  include it.
- **Allow the extra ports from `traefik` too**: wrong for most second listeners, and quietly opens them.
- **UDP ports**: no project needs them yet. A later `protocol` would need the pair form.

## Consequences

- A second listener is one answer: `copier update -d extra_ports='[3128]'`, then it shows in the image,
  compose and k8s, and survives every update.
- The question is permanent once projects answer it. Changing its shape later needs a migration
  (`_migrations` in `copier.yml`).
- Wiki: Answering-the-Questions (the question), Docker-Images (`EXPOSE`), Contrib-Manifests (where the
  ports appear, and the commented NetworkPolicy rule), Updating-from-the-Template (adding the answer
  to an existing project).

## Resolved questions

1. **Ints or `{name, port}` pairs?** Ints. The shortest answer, and it can't produce an invalid k8s name.
   Names only matter inside the template's own manifests, and a later optional `extra_port_names` can add
   them without breaking an existing answer. Pairs, once answered, would need a migration to undo.
2. **NetworkPolicy?** Commented out, so the default stays deny. Allowing `traefik` would usually be wrong
   for a second listener (too open to the ingress controller, closed to the real clients). The commented
   rule leaves the exposure decision with the project, in place.
3. **compose: loopback or all interfaces?** Loopback, like `port`. The template never decides exposure,
   and binding every interface would quietly publish each extra listener on the host.
