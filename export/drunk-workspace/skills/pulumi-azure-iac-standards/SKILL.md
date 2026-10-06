---
name: pulumi-azure-iac-standards
description: Conventions for drunk Pulumi Azure/Cloudflare TypeScript IaC libraries (@drunk-pulumi/*) — Builder pattern, convention-over-configuration naming, security-by-default (RBAC, Key Vault, private endpoints), composable type system, and how components/providers are structured and tested, plus the four monthly-review rule families (security-by-default, upstream provider drift, deprecation path, Well-Architected best practice). Use when writing, reviewing, or extending Pulumi TypeScript code in drunk-pulumi-* repos.
---

# Pulumi Azure IaC Standards (drunk-pulumi-*)

Derived from conventions of `github.com/baoduy/drunk-pulumi-azure` (`@drunk-pulumi/azure`) and its
sibling component/provider libraries (`-azure-components`, `-azure-providers`, `-cloudflare-components`,
`-intune-components`). These are opinionated, type-safe abstraction layers over Pulumi Native
providers. Every rule carries a stable `rule-id` for use as a finding fingerprint.

## Core philosophy (do not fight it)

- **Convention over configuration** — resources are named automatically and environment-aware; do not hand-name.
- **Security by default** — encryption, RBAC, private endpoints, and Key Vault integration are default path, not an opt-in.
- **Builder pattern** — infrastructure is defined through a fluent, chainable API, not raw resource constructors.
- **Type safety** — full TypeScript; compose small types rather than widening to `any`.

## Builder pattern

- `PULUMI-BLD-001` **New resource wrapper skips Builder base.** A synchronous resource extends `Builder<TResults extends ResourceInfo>` and implements `build(): TResults`; anything needing async work (secret reads, remote lookups) extends `BuilderAsync<TResults>` and returns `Promise<TResults>`. Do not invent a parallel base.
- `PULUMI-BLD-002` **Method chain is not interface-segregated.** Progressive builders expose Starter → Feature → Build interfaces (`IStorageStarterBuilder` → `IStorageBuilder` → `IBuilder<TResults>`) so illegal states are unrepresentable. A single fat interface with every optional method is a violation.
- `PULUMI-BLD-003` **Entry point bypassed.** Most infrastructure starts from `ResourceBuilder('<project>')` (`.createRoles()` → `.createRG()` → `.createVault()` → `.addSecrets()` → `.createEnvUID()` → `.build()`). New standalone resource creation that duplicates RG/roles/vault wiring should compose `ResourceBuilder` instead.
- `PULUMI-BLD-004` **`build()` does side-effectful work outside resource construction.** Keep `build()` to declaring resources and returning `*Info` result; no imperative I/O in sync path.

## Naming

- `PULUMI-NAME-001` **Hard-coded resource name.** Names come from `naming` helper (`src/Common/Naming.ts`, 90+ rules) — `naming.getStorageName('x')`, `naming.getResourceGroupName('x')`. Format `[prefix]-[name]-[region]-[suffix]-[org]`, cleaned per service constraints. Never string-concatenate an Azure resource name by hand.
- `PULUMI-NAME-002` **Length/charset rules ignored.** Strict-naming services (Storage, etc.) use `cleanName` + `maxLength`. A new resource type needs its naming rule added, not a bespoke sanitizer at call site.
- `PULUMI-NAME-003` **Naming toggled inline.** Prefix/region/suffix are controlled by env (`DPA_NAMING_DISABLE_PREFIX`, `DPA_NAMING_DISABLE_REGION`, `DPA_NAMING_DISABLE_SUFFIX`) — read `src/env.ts`, don't add ad-hoc flags.

## Security & RBAC

- `PULUMI-SEC-001` **Secret in code or plain output.** Secrets flow through Key Vault (`.createVault()` / `.addSecrets()`); never inline a literal, never expose one as a non-secret `Output`.
- `PULUMI-SEC-002` **Bypassing three-tier env roles.** Access uses `admin` / `contributor` / `readOnly` roles loaded from vault (`EnvRoleBuilder.loadFrom(vaultInfo)`, `grantEnvRolesAccess(...)`). Do not assign raw principals per resource.
- `PULUMI-SEC-003` **Public exposure by default.** Prefer private endpoints and vault-backed encryption identities (`createEnvUID`); flag any resource that is public without an explicit, justified reason.

## Type system

- `PULUMI-TYPE-001` **Widened/duplicated type instead of composition.** Compose from building blocks (`WithNamedType`, `WithOutputId`, `WithResourceGroupInfo`, `WithVaultInfo`, `OptsArgs`) — e.g. `ResourceInfo = WithNamedType & WithOutputId & WithResourceGroupInfo`. Don't redeclare fields already provided by a mixin type.
- `PULUMI-TYPE-002` **`*Info` vs `*Args` confusion.** `*Args` are inputs to a builder; `*Info` are results after creation. A function returning post-creation data must return an `Info` type, not `Args` it received.
- `PULUMI-TYPE-003` **`OptsArgs` reinvented.** `dependsOn` / `ignoreChanges` / `importUri` come from `OptsArgs`; thread them through rather than adding one-off option params.

## Components vs providers

- `PULUMI-PKG-001` **Wrong repo for change.** `-components` repos hold reusable `ComponentResource` wrappers; `-providers` repos hold dynamic/custom providers; core `azure` repo holds builders. Put change where its layer lives; don't cross-publish.
- `PULUMI-PKG-002` **`ComponentResource` without parenting.** A component registers child resources under itself (`{ parent: this }`) and calls `registerOutputs`; unparented children break resource graph.

## Testing & delivery

- `PULUMI-TEST-001` **No unit test for builder logic.** Builders/naming/type composition are unit-testable with Pulumi mocks (`pulumi.runtime.setMocks`) under repo's mocha config; new builder behaviour ships with tests.
- `PULUMI-TEST-002` **Publish shape broken.** These are npm libraries — a change must keep a clean `npm pack` / build (`.tasks/npm-package.ts`) and not leak internal `.ts.ignore`/sample files into package.
- `PULUMI-TEST-003` **Breaking public API without a minor bump.** Renamed/removed exported builders, interfaces, or `*Info` fields are breaking changes for downstream stacks — they ship with a `Breaking` changelog entry naming the replacement and a `(MINOR)` marker in the commit title (`v1.2.3` → `v1.3.0`). **Never a major bump**: the major number is frozen and owner-only (Policy 08 statement 12, `VER-REL-001`).
---

# Review dimensions (monthly architecture review)

The four rule families below are the review dimensions of the **Monthly Architecture Review — Pulumi repos** autopilot. They are additive to the convention rules above; a finding always cites one stable rule-id.

**Stance: recommend, never bump, never delete.** This catalogue produces backlog findings and test-only enforcement. Dependency version bumps belong to the npm-upgrade autopilot; removing a public export requires human approval and ships in a minor release, never a major one (see `PULUMI-DEP-003`).

## Dimension 1 — Security by default

`PULUMI-SEC-001/002/003` above still apply. Additional rules — each is a violation when the **default path** (no caller opt-in) lands on the unsafe option:

- `PULUMI-SEC-004` **Transport not hardened by default.** `minimumTlsVersion` unset or below `TLS1_2` (Storage, SQL, Redis, App Service, API Management), `httpsOnly`/`httpsTrafficOnlyEnabled` not forced, HTTP listener with no HTTPS redirect. A wrapper that passes the caller's `undefined` straight through inherits the provider default — that is a finding even when the provider default happens to be safe today.
- `PULUMI-SEC-005` **Key-based auth where managed identity is available.** `allowSharedKeyAccess` not disabled on Storage, ACR `adminUserEnabled: true`, SQL/PostgreSQL SQL-auth admin password when Entra-only admin is supported, connection strings handed out where a user-assigned identity (`createEnvUID`) would work. Identity is the default path; key auth is an explicit, justified opt-in.
- `PULUMI-SEC-006` **Public network access default-on.** `publicNetworkAccess: 'Enabled'` (or unset), Storage `allowBlobPublicAccess: true`, `networkAcls.defaultAction: 'Allow'`, AKS/AKS API server with no private-cluster or authorized-IP-range option, NSG/firewall rule with `0.0.0.0/0` or `*` source. Extends `PULUMI-SEC-003` with concrete property anchors.
- `PULUMI-SEC-007` **Data-protection defaults missing.** Key Vault without `enableSoftDelete` + `enablePurgeProtection`, Storage without blob delete-retention / versioning, SQL without TDE, no customer-managed-key path on a resource that supports CMK, no `infrastructureEncryption` where offered.
- `PULUMI-SEC-008` **No diagnostics wired by default.** A resource that emits audit/security logs (Key Vault, SQL, AKS, App Gateway, Firewall, Storage) built without a diagnostic setting to Log Analytics. Unloggable infrastructure is uninvestigable after an incident.
- `PULUMI-SEC-009` **Secret leaves as a non-secret `Output`.** A value read from Key Vault, a generated password, or a connection string returned without `pulumi.secret(...)` — it lands in plaintext in state and in `pulumi up` diffs. Extends `PULUMI-SEC-001` to the output side.
- `PULUMI-SEC-010` **AKS hardening defaults.** `disableLocalAccounts` not set, no Azure RBAC for Kubernetes authorization, no workload identity / OIDC issuer, `enableRBAC: false`, Basic-SKU load balancer or public IP, no `apiServerAccessProfile`.

Rank Dimension 1 findings `critical`/`high` — these are libraries every downstream stack trusts blindly, and an insecure default is inherited silently by every consumer that does not override it.

## Dimension 2 — Upstream provider drift

Recommend-only. Read the current pins from `package.json` and compare against the registry (`npm view <pkg> versions --json`, `npm outdated`) and the upstream changelog. **Never open a version-bump PR from a review run.**

- `PULUMI-UP-001` **Provider pin materially behind latest stable.** `@pulumi/pulumi`, `@pulumi/azure-native`, `@pulumi/azuread`, `@pulumi/cloudflare` a major (or a long-lived minor) behind latest stable. Finding names the current pin, latest stable, and the notable changes between them — not just "upgrade available".
- `PULUMI-UP-002` **New upstream property not surfaced by the wrapper.** Upstream added a security-, resiliency-, or cost-relevant argument (a hardening toggle, a zone option, a new SKU tier) that the builder/component does not expose, so no downstream stack can set it. Cite the upstream property path and the wrapper's `*Args` type that should carry it.
- `PULUMI-UP-003` **Pinned versioned API module.** Importing an explicit dated module (`@pulumi/azure-native/<service>/v20200101/...`) instead of the default latest-stable surface, with no comment justifying the pin. Dated modules freeze the resource at that API version and quietly miss every later hardening default.
- `PULUMI-UP-004` **Deprecated upstream resource or property still used.** Upstream marked a resource/property deprecated (provider release notes, `@deprecated` in the SDK's `.d.ts`) and local code still calls it. Cite the upstream replacement.
- `PULUMI-UP-005` **Hand-rolled wrapper now shipped upstream.** Upstream (or a sibling `-components` package) now provides what a local wrapper was written to work around. Recommend deleting the local wrapper under the `PULUMI-DEP-003` deprecation path — not an immediate removal.

## Dimension 3 — Deprecation path

- `PULUMI-DEP-003` **Removal without a deprecation path.** These packages are published npm libraries — deleting an exported builder, component, or `*Info` field breaks every downstream stack at install time. The removal path is two-step and spans two releases:
  1. **This release** — mark the export `@deprecated` with a JSDoc tag naming the replacement and the reason, add a migration note to the repo's changelog/README, keep the code working. Non-breaking, ships in a minor.
  2. **A later release** — delete it, per `PULUMI-TEST-003`: the removal carries `(MINOR)` and cuts a minor release, never a major one.

  A review run **never** deletes a public export and never opens a PR that does. Step 1 is filed as a finding for human approval; step 2 is a separate, human-scheduled removal ticket.

## Dimension 4 — Azure best practice (Well-Architected)

Findings here map to a Well-Architected pillar and, like Dimension 1, are about the **default** a downstream stack inherits.

- `PULUMI-WAF-001` **No availability-zone / zone-redundancy option.** Reliability. A zone-capable resource (Storage `Standard_ZRS`, SQL `zoneRedundant`, AKS `availabilityZones`, App Gateway/Firewall/Load Balancer `zones`, Key Vault region pairing) built with no way for a caller to request zone redundancy.
- `PULUMI-WAF-002` **Expensive default SKU with no tier knob.** Cost optimisation. A builder that hard-codes a premium tier, or offers no SKU/capacity argument, forces every non-production stack to pay production prices. Name the default and the cheapest safe alternative.
- `PULUMI-WAF-003` **No governance defaults.** Operational excellence. Resources created without the repo's standard tag set (environment, owner, project — sourced from config, not hand-written strings), or a component that drops tags its parent passed down.
- `PULUMI-WAF-004` **Stateful resource with no deletion guard.** Reliability. A data-bearing resource (Storage, SQL, Key Vault, Postgres, Cosmos, Redis persistence) built with no `protect` / `retainOnDelete` path via `OptsArgs`, so a stack rename or refactor destroys data silently.

## Enforcement (all four dimensions)

Tier discipline is defined by `architecture-review-sweep`; the native mechanism for these repos is an eslint rule or a mocha unit test under the repo's existing config. What is mechanically checkable here:

- Dimension 1 — a mocha test with `pulumi.runtime.setMocks` asserting the built resource's args carry the hardened default (no caller input). This is the highest-value enforcement in the catalogue: it pins the default and fails the moment someone loosens it.
- Dimension 2 — a lint rule banning dated `@pulumi/azure-native/**/v[0-9]*` imports (`PULUMI-UP-003`).
- Dimension 4 — a test asserting the tag set is applied and that a zone/SKU argument exists on the builder's `*Args` type.

Enforcement PRs stay test-only and config-only, target `dev`, and must be green locally before push. Never touch production source in a review run.
