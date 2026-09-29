# Policy 08 — Container, Build & Release

| | |
|---|---|
| **Policy ID** | DRK-POL-08 |
| **Version** | 1.2 |
| **Status** | Active |
| **Owner** | devops (build/publish automation) · release-manager (the `dev`→`main` release) |
| **Applies to** | Every drunk repo that publishes a NuGet/npm package, a container image, or a Helm chart |
| **Related skills** | [`docker-image-standards`](../../skills/docker-image-standards/SKILL.md) · [`helm-k8s-conventions`](../../skills/helm-k8s-conventions/SKILL.md) · the package-publish CI workflows `devops` configures (no dedicated skill file — see `agents/devops.md`) |
| **Enforced at** | PR review gate ([`pr-review-gate`](../../skills/pr-review-gate/SKILL.md)) · devops · release-manager |

> **Authority.** This policy is the source of truth for how drunk builds, packages, and
> releases. `docker-image-standards` and `helm-k8s-conventions` **implement** it; `devops`
> and `release-manager` act inside the limits it sets. Amend this policy first, then cascade
> the change into the skills and the CI workflows — see
> [change control](00-policies-index.md#change-control).

## Release model at a glance

```
   drunk has NO deployed environment. Publishing the artifact IS the release. There is no
   SANDBOX, no PRD, no k8s promotion to gate on top of what's below.

   (a) LIBRARY REPOS (DKNet, DKNet.Templates, drunk-pulumi-*)
       dev ──[devops CI: build+test]──▶ PR to dev, reviewed by pr-reviewer, merged
        │
        └──[release-manager: ONE PR, dev──▶main]── merge triggers CI ──▶ NuGet `dotnet pack`/
           `nuget push`  OR  npm `npm pack`/`npm publish`.  No deploy step after this.

   (b) CONTAINER-IMAGE REPOS (drunk-mcp-proxy, dev-environments, drunk-action-runners,
       HBD.YarpProxy, per-service Dockerfiles)
       CI builds + publishes a MULTI-ARCH image (linux/amd64 + linux/arm64) off `main`.
       Publishing the manifest IS the release — no environment to promote it to.

   (c) HELM CHART REPOS (drunk.charts)
       Chart version bump ──▶ CI publishes to OCI registry + npm, per helm-k8s-conventions.
       No app-repo `dev`→`main` model applies — see that skill's own chart-repo conventions.

   Guardrail: devops owns the CI workflow, never app code, never `main`.
   release-manager is the ONLY agent that opens/merges the dev──▶main PR.
```

## Purpose

drunk's repos are open-source libraries, images, and charts with no environment to deploy
to — the moment CI publishes the artifact, it is live for every downstream consumer. This
policy fixes who is allowed to trigger that moment (single-owner `main` merge), what CI must
guarantee before it does (multi-arch, build quality), and keeps `devops`'s CI-automation role
cleanly separated from `release-manager`'s one-PR release act.

## Scope

Every drunk repo across the three release shapes above. Feature delivery up to the merge into
`dev` is governed by the SDLC/branching policies; this policy starts at `dev`→`main` and
covers everything CI does to produce a published artifact.

## Policy statements

1. **`main` triggers the publish; there is no deploy after it.** Merging into `main` runs CI,
   which publishes the NuGet/npm package (library repos) or the container image (image repos).
   No agent tags production and no agent deploys anything — for library and image repos alike,
   publishing the artifact off `main` **is** the release.
2. **`release-manager` is the only agent that opens or merges the `dev`→`main` PR.** Exactly
   one open release PR per cycle, `--base main --head dev`, verified on both refs before merge,
   merged with a merge commit (never squash/rebase, to preserve `dev` history on the release
   line). No other agent ever targets or merges into `main`.
2a. **A critical release waits for the owner; every other release merges on its own.** Before
   merging, release-manager checks the commits the release PR ships (`origin/main..origin/dev`).
   The release is **critical** when it carries (1) a breaking change — a `(MINOR)` marker in any
   commit subject or body — or (2) any PR the PR gate labelled `release-review`: a
   security-sensitive change (authentication or authorization, cryptography, secret handling), a
   build or publish supply-chain change (`.github/workflows/**`, a new package source, a lockfile
   source line), commits a pr-reviewer run pushed, or a PR the owner asked to review personally
   ([Policy 04](04-code-and-spec-review.md) statement 11c). A critical release is not merged:
   release-manager reassigns its release ticket to the resolved owner
   ([Policy 10](10-ticket-ownership-and-owner-pickup.md)) at `todo` with a `## BLOCKER` +
   `## OPTIONS` comment listing every trigger with its commit or PR link — **A** merge now,
   **B** hold until a fix lands — and merges only when the owner replies A with
   release-manager's mention, re-checking first if `dev` moved since the handoff. Large diffs,
   unknown coverage and CI exceptions do not make a release critical.
3. **`devops` owns CI, never app code, and never `main`.** `devops` writes and maintains
   pipeline configs (GitHub Actions), build/test workflows, and the package-publish automation
   that runs off `main` — it does not touch application/library code, tests, or documentation,
   and it never commits to or merges `dev` or `main` directly. Its own changes land via a
   `chore/<issue-key>` branch and ONE PR to `dev`, scored by `pr-reviewer`, merged by
   `pr-reviewer` — `devops` never merges its own PR.
4. **Library repos: publishing IS the release, no deploy step exists.** `dotnet pack`/
   `nuget push` for .NET, `npm pack`/`npm publish` for TypeScript, both triggered by the
   `main` merge. `devops` configures and maintains this workflow; it never triggers, watches,
   or verifies the publish run beyond one non-blocking status snapshot — the run itself is
   CI's job.
5. **Container-image repos: publish a multi-arch manifest, not a deploy.** Same "merge to
   `main` triggers CI" shape as library repos, except the published artifact is the image
   manifest covered by statement 10 below, not a package.
6. **Helm chart repos follow `helm-k8s-conventions`'s own delivery rules, not the app-repo
   `dev` model.** A chart publishes to the OCI registry and npm via the repo's own workflows
   (`publish-oci.yml` / `npm-publish.yaml`), never a manual `helm push` (`HELM-DEL-003`). Any
   template/values change bumps the chart's `Chart.yaml` `version`; `appVersion` tracks the
   shipped image separately (`HELM-DEL-002`). New conditional rendering in a template ships
   with a `helm-unittest` assertion, and `helm lint`/`helm template` must run clean
   (`HELM-DEL-001`).
7. **Multi-stage builds — no build tooling in the runtime layer.** A Dockerfile uses a
   `builder` stage (compiles/packages: wheel, `dotnet publish`, `npm run build`) and a minimal
   `runtime` stage that `COPY --from=builder` only the artifact; build-essential/SDK never
   reaches the runtime layer (`DOCKER-BLD-001`).
8. **Non-root runtime.** Every image creates and switches to a non-root user before the
   entrypoint; a container without a `USER` line below root is a finding (`DOCKER-RUN-001`).
   Long-running service images additionally set a `securityContext` in the chart consuming
   them where applicable (`HELM-K8S-003`).
9. **No secrets in any layer.** No token/secret in `ARG`/`ENV`/`COPY` — a secret baked into a
   layer is permanent even after a later layer removes it; pass secrets at runtime or via
   `--mount=type=secret` (`DOCKER-SEC-001`). Every repo ships a `.dockerignore` excluding
   `.git`, `node_modules`, local envs, and caches (`DOCKER-SEC-002`). Dependency manifests are
   copied and installed **before** the source (`COPY . .` last), so a source-only change
   doesn't bust the dependency cache layer (`DOCKER-SEC-003`). Base images are pinned by
   explicit tag via `ARG`, never `:latest`; digest-pinning is preferred for release images
   (`DOCKER-SEC-004`).
10. **Multi-arch images — every published image covers both architectures.** Every container
    image a repo builds and publishes MUST be a multi-arch manifest covering **both
    `linux/amd64` and `linux/arm64`**, via `docker buildx build --platform
    linux/amd64,linux/arm64 --push` or `docker/build-push-action` with both platforms in
    `platforms:`; on amd64 GitHub-hosted runners this requires `docker/setup-qemu-action` +
    `docker/setup-buildx-action` so the arm64 leg emulates, and any arch-specific build step
    stays cross-build-safe via `ARG TARGETPLATFORM`/`TARGETARCH` (`DOCKER-DEL-001`). A **new**
    repo's docker/publish workflow is wired multi-arch from its first build, not added later.
    A single-architecture published image is a release defect the PR review gate flags on any
    `Dockerfile`/build-workflow diff.
11. **Long-running service images declare a `HEALTHCHECK` and OCI labels.** Source and version
    provenance (`org.opencontainers.image.source`, `.version`) so orchestration and
    provenance tooling can identify the running artifact (`DOCKER-DEL-002`).
12. **The pipeline owns the release number, and the MAJOR number is frozen.** For every
    published drunk artifact — NuGet package, npm package, container image tag, Helm chart —
    the release number is computed by the publish pipeline from the last `v`-prefixed tag
    (DKNet: `paulhatch/semantic-version` in `.github/workflows/dotnet-publish.yml`, with
    `major_pattern: "(MAJOR)"`, `minor_pattern: "(MINOR)"`), never typed by an agent. A
    normal release is a **patch** bump and needs no marker at all: `v1.2.3` → `v1.2.4`. A
    **breaking change bumps the MINOR only**: `v1.2.3` → `v1.3.0`, signalled by putting
    `(MINOR)` in the commit title that lands the break on `main` (`VER-REL-001`). No agent
    ever writes `(MAJOR)` in a commit title, PR title, or merge-commit subject, and no agent
    hand-edits a version literal (`Directory.Build.props`, `package.json`, `Chart.yaml`
    `version`, a release tag) or creates a tag or GitHub Release by hand (`VER-REL-002`).
    **A major bump is the owner's decision alone**, taken deliberately outside a delivery
    cycle — a breaking change is never reason enough for one. If a publish run emits a major
    bump nobody asked for, that is a release defect: report it on the ticket under Policy 07
    and stop; never publish again to "correct" a number (`VER-REL-003`).
13. **Image build/publish always goes through CI, never a manual local push.** Builds run via
    the repo's own GitHub Actions workflow (`.github/workflows/docker.yml` or its publish
    equivalent) — this is the same workflow statement 10's multi-arch requirement applies to
    (`DOCKER-DEL-001`).

## Roles & responsibilities

- **devops** — owns CI/CD pipeline configs and the package-publish/image-publish automation
  that runs off `main`; opens PRs to `dev` only, never merges them, never touches app code,
  never touches `main`.
- **release-manager** — the sole owner of the `dev`→`main` PR for library and image repos;
  three acts only (open the PR, check whether it is critical from commit subjects and PR labels,
  merge it — a critical one on the owner's reply); never runs tests/builds, never triggers or
  verifies the publish beyond one snapshot.
- **pr-reviewer** — scores every PR touching a `Dockerfile`, build workflow, or chart template
  against the rule-ids above; a missing multi-arch platform list or a secret in a layer is
  `blocking`.
- **arch-reviewer** — sweeps image and chart repos on the monthly `architecture-review-sweep`
  using `docker-image-standards`/`helm-k8s-conventions` as the rule catalogue for those stacks.

## Definition of Done / compliance

- **Library release:** `dev`→`main` PR opened and merged by release-manager only (a critical
  release after the owner's reply A); CI publish
  workflow started (one non-blocking snapshot); no deploy step exists or is expected.
- **Image release:** CI build/publish workflow is wired multi-arch (`linux/amd64` +
  `linux/arm64`) from its first build; the published manifest covers both platforms.
- **Chart release:** `helm lint`/`helm template` clean, chart version bumped (patch, or minor
  for a breaking template/values change — never major), published via the repo's own OCI/npm
  workflow — never a manual `helm push`.
- **Release numbering:** no `(MAJOR)` marker anywhere in the release's commit titles; a
  breaking change carries `(MINOR)` plus a `Breaking` changelog entry naming the replacement;
  the published tag's major equals the previous release's major; no version literal or tag
  edited by hand.
- No secret literal in any Dockerfile layer, chart value, or CI workflow file.

## Enforcement

`pr-review-gate` flags any `Dockerfile`/build-workflow diff missing the multi-arch platform
list, a missing non-root `USER`, or a secret in a layer as `blocking`. It also flags a
`(MAJOR)` marker in any commit or PR title, and a hand-edited version literal or tag, as
`blocking` (`VER-REL-001`/`VER-REL-002`). `devops` is the sole
configurer of the CI workflows enforcing this at build time. `release-manager` owns the
`main` merge monopoly for library and image repos; a PR targeting `main` opened by any other
agent is itself a policy violation.

## Exceptions & waivers

- No waiver exists for an agent-initiated major bump. The major number moves only when the
  owner says so, by hand, outside a delivery cycle — a breaking change bumps the minor.
- No waiver exists for a single-architecture published image — a new repo not yet
  multi-arch-capable stays unpublished rather than shipping single-arch.
- No waiver exists for a secret baked into a layer; the layer must be rebuilt from a clean
  base, not patched.
- A repo's own `CLAUDE.md`/`AGENTS.md` build convention overrides a generic Docker rule here
  where it differs — flag a harmful convention upward rather than forking around it silently.

## References

- [`docker-image-standards`](../../skills/docker-image-standards/SKILL.md) — full Dockerfile rule catalogue (`DOCKER-BLD-*`, `DOCKER-RUN-*`, `DOCKER-SEC-*`, `DOCKER-DEL-*`).
- [`helm-k8s-conventions`](../../skills/helm-k8s-conventions/SKILL.md) — chart structure, templating, K8s manifest hygiene, `HELM-DEL-*` publish rules.
- `agents/devops.md` — CI/CD scope and hard boundary (no app code, no `main`).
- `agents/release-manager.md` — the two-act `dev`→`main` release procedure and its absolute boundary.
