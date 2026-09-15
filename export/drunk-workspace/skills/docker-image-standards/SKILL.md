---
name: docker-image-standards
description: Conventions for drunk container images (dev-environments, action-runners, YarpProxy, mcp-proxy, and per-service Dockerfiles) — multi-stage BuildKit builds, non-root runtime, cache mounts, ARG-driven versions, and slim reproducible runtime stages. Use when writing or reviewing a Dockerfile or image build in baoduy repos.
---

# Docker Image Standards (drunk images)

Derived from Dockerfiles across `github.com/baoduy` (e.g. `drunk-mcp-proxy`, `dev-environments`,
`drunk-action-runners`, `HBD.YarpProxy`). Every rule carries a stable `rule-id`.

## Build structure

- `DOCKER-BLD-001` **Single-stage image shipping build tools.** Use a multi-stage build: a `builder` stage that compiles/packages (wheel, `dotnet publish`, `npm run build`) and a minimal `runtime` stage that `COPY --from=builder` only artifact. Build-essential/SDK must never reach runtime layer.
- `DOCKER-BLD-002` **No BuildKit syntax directive when using BuildKit features.** Files using cache mounts start with `# syntax=docker/dockerfile:1.4` (or newer) on line 1.
- `DOCKER-BLD-003` **Package install without a cache mount.** Dependency installs use `RUN --mount=type=cache,target=<cache-dir>` (`/root/.cache/pip`, npm/nuget caches) so rebuilds are fast and layers stay lean.
- `DOCKER-BLD-004` **Versions hard-coded instead of `ARG`.** Base language/runtime versions are `ARG` (`ARG PYTHON_VERSION=3.12`, `ARG NODE_VERSION=25`) and referenced in `FROM`; re-declare `ARG` in each stage that needs it (ARGs don't cross stages).

## Runtime hardening

- `DOCKER-RUN-001` **Runs as root.** Create and switch to a non-root user (`RUN useradd -m -u 10001 appuser` … `USER appuser`) before entrypoint. A container without a `USER` line below root is a finding.
- `DOCKER-RUN-002` **Fat base image.** Prefer `-slim` / distroless / alpine runtime bases; only install runtime deps actually needed (`--no-install-recommends`), and clean apt lists in SAME `RUN` (`apt-get clean && rm -rf /var/lib/apt/lists/*`).
- `DOCKER-RUN-003` **Python deps installed into system site-packages.** Use an isolated venv (`python -m venv /opt/venv` + `ENV PATH="/opt/venv/bin:$PATH"`), install built wheel into it — don't pollute base interpreter.
- `DOCKER-RUN-004` **No entrypoint verification.** After install, a smoke line (`RUN <entrypoint> --help | head`) catches a broken package at build time rather than at deploy.

## Correctness & security

- `DOCKER-SEC-001` **Secret baked into a layer.** No secrets/tokens in `ARG`/`ENV`/`COPY`; pass them at runtime or via `--mount=type=secret`. A secret in any layer is permanent even if later removed.
- `DOCKER-SEC-002` **Missing `.dockerignore`.** Ship a `.dockerignore` excluding `.git`, `node_modules`, local envs, caches — keeps build context small and secrets out.
- `DOCKER-SEC-003` **`COPY . .` too early.** Copy dependency manifests first, install, THEN copy source, so a source-only change doesn't bust dependency layer.
- `DOCKER-SEC-004` **Unpinned mutable base with no supply-chain note.** Pin bases by explicit tag (via `ARG`); flag `:latest`. Digest-pinning is preferred for release images.

## Delivery

- `DOCKER-DEL-001` **Build not wired to CI, or single-arch.** Image builds/publishes go through repo's GitHub Actions (`.github/workflows/docker.yml` / publish workflow) — not a manual local push — and every published image MUST be a multi-arch manifest covering **both `linux/amd64` and `linux/arm64`**. Build with `docker buildx build --platform linux/amd64,linux/arm64 --push` (or `docker/build-push-action` with `platforms: linux/amd64,linux/arm64`); on amd64 runners add `docker/setup-qemu-action` + `docker/setup-buildx-action` so arm64 leg emulates. Keep any arch-specific step cross-build-safe via `ARG TARGETPLATFORM`/`TARGETARCH`. A new repo is wired multi-arch from its first build; a single-architecture published image is a finding.
- `DOCKER-DEL-002` **`HEALTHCHECK`/labels missing on a service image.** Long-running service images should declare a `HEALTHCHECK` and OCI `LABEL`s (source, version) so orchestration and provenance work.

