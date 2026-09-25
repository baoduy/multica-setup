---
name: helm-k8s-conventions
description: Conventions for drunk Helm charts (drunk.charts — drunk-app application chart and drunk-lib library chart) and their Kubernetes manifests — app/library chart split, reusable named templates, values contracts, helm-unittest tests, and OCI/npm chart publishing. Use when writing or reviewing Helm charts or K8s templates in baoduy repos.
---

# Helm & Kubernetes Conventions (drunk.charts)

Derived from `github.com/baoduy/drunk.charts` — an application chart (`drunk-app`) plus a
library chart (`drunk-lib`, `type: library`) of reusable templates. Helm 3.0+. Every rule
carries a stable `rule-id`.

## Chart structure

- `HELM-STR-001` **Reusable logic duplicated instead of living in library chart.** Shared template partials belong in `drunk-lib/templates/` (a `type: library` chart with no rendered resources of its own); `drunk-app` consumes them. Copy-pasting a `_helpers`-style block into an app chart is a violation.
- `HELM-STR-002` **Chart metadata incomplete.** Every chart has a `Chart.yaml` with `name`, `version` (chart SemVer), `appVersion`, and `type` (`application` vs `library`). A library chart MUST set `type: library`.
- `HELM-STR-003` **Value referenced but not declared/documented.** Every `.Values.*` a template reads is declared with a sane default in `values.yaml` and documented in chart README. No undocumented magic keys.
- `HELM-STR-004` **Layout drift.** Keep standard layout: `Chart.yaml`, `values.yaml`, `templates/`, `tests/`, `README.md` per chart.

## Templating

- `HELM-TPL-001` **Ad-hoc name/label instead of shared helpers.** Resource names, `metadata.labels`, and selector labels come from library's named templates (`{{ include "drunk-lib.fullname" . }}`, standard label helper) — not hand-written per manifest. Match Kubernetes recommended labels (`app.kubernetes.io/*`).
- `HELM-TPL-002` **Unquoted/uncoerced value.** String values from `.Values` are `quote`d; numbers/booleans coerced deliberately. Rely on `include` + `toYaml | nindent` for nested blocks rather than manual indentation.
- `HELM-TPL-003` **Selector labels not immutable.** `spec.selector.matchLabels` must be a stable subset that never changes across upgrades (changing it is a breaking, in-place-update-blocking change); keep it separate from full label set.
- `HELM-TPL-004` **Namespace hard-coded.** Never bake a namespace into a template; let release/`-n` decide.

## Kubernetes manifest hygiene

- `HELM-K8S-001` **No resource requests/limits.** Workloads set `resources.requests`/`limits` (values-driven); flag a container without them.
- `HELM-K8S-002` **Missing probes.** Long-running workloads declare `livenessProbe` and `readinessProbe`.
- `HELM-K8S-003` **Runs privileged / as root.** Set a `securityContext` (non-root `runAsUser`, `readOnlyRootFilesystem`, dropped capabilities) — mirrors non-root container images.
- `HELM-K8S-004` **Secrets as plain values.** Sensitive config flows through `Secret`/external-secret references, never checked into `values.yaml` in clear text.

## Test & publish

- `HELM-DEL-001` **Template change without a helm-unittest test.** Chart logic is covered by `helm-unittest` under chart's `tests/`; new conditional rendering ships with an assertion. Run `helm lint` + `helm template` clean.
- `HELM-DEL-002` **Chart version not bumped.** Any template/values change bumps `Chart.yaml` `version` (chart SemVer) — patch normally, minor for a breaking template/values change, **never major** (major is frozen and owner-only, Policy 08 statement 12); `appVersion` tracks shipped app image separately.
- `HELM-DEL-003` **Manual publish.** Charts publish via repo workflows (OCI registry and npm) — `.github/workflows/publish-oci.yml` / `npm-publish.yaml` — not a manual `helm push`.

