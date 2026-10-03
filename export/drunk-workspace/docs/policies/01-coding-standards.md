# Policy 01 — Coding Standards & Repository Layout

| | |
|---|---|
| **Policy ID** | DRK-POL-01 |
| **Version** | 1.5 |
| **Status** | Active |
| **Owner** | dev-leader |
| **Applies to** | Every engineer and agent writing or modifying code in any drunk stack: .NET/DDD NuGet libraries, Pulumi/TypeScript npm packages, Python MCP/FastAPI services, Docker images, Helm charts |
| **Related skills** | [`nodejs-typescript-standards`](../../skills/nodejs-typescript-standards/SKILL.md) · [`python-mcp-standards`](../../skills/python-mcp-standards/SKILL.md) · [`dotnet10-efcore10-standards`](../../skills/dotnet10-efcore10-standards/SKILL.md) · [`dknet-ddd-conventions`](../../skills/dknet-ddd-conventions/SKILL.md) · [`pulumi-azure-iac-standards`](../../skills/pulumi-azure-iac-standards/SKILL.md) · [`helm-k8s-conventions`](../../skills/helm-k8s-conventions/SKILL.md) |
| **Enforced at** | dev-backend's Standards self-review (statement 15) · PR review gate ([`pr-review-gate`](../../skills/pr-review-gate/SKILL.md)) · architecture review sweep ([`architecture-review-sweep`](../../skills/architecture-review-sweep/SKILL.md)) |

> **Authority.** This policy is the source of truth for coding standards across every drunk
> stack. The six skills above **implement** it, one per language/runtime; the review gates
> derive their rule catalogue from it. Amend this policy first, then cascade the change into
> the relevant skill(s) — see [change control](00-policies-index.md#change-control). Where
> a skill and this policy diverge, the policy's intent wins and the skill is corrected.

## Standards at a glance

drunk-workspace is **not** a single-language shop: it maintains open-source repos across five
stacks for `github.com/baoduy`, each with its own toolchain. This policy states the
language-agnostic intent once; each stack's skill is the authoritative implementer of the
letter of the rule.

| Stack | Repos (examples) | Governing skill(s) | Rule-id prefix |
|---|---|---|---|
| TypeScript / Pulumi IaC | `drunk-pulumi-azure*`, `-cloudflare-components`, `-intune-components` | `nodejs-typescript-standards` (language/tooling) + `pulumi-azure-iac-standards` (IaC domain) | `TS-*`, `PULUMI-*` |
| Python MCP/FastAPI | `drunk-mcp-proxy`, `entraid-mcp-server` | `python-mcp-standards` | `MCP-*` |
| .NET / C# DDD libraries | `DKNet`, `DKNet.Templates` | `dotnet10-efcore10-standards` (language/EF) + `dknet-ddd-conventions` (DDD domain) | `NET10-*`, `EFC-*`, `ASP-*`, `ASYNC-*`, `LOG-*`, `CLEAN-*`, `DKNET-*` |
| Helm charts | `drunk.charts` | `helm-k8s-conventions` | `HELM-*` |
| Docker images | `dev-environments`, `drunk-action-runners`, `HBD.YarpProxy`, service Dockerfiles | (build-quality intent is in [Policy 08](08-container-build-and-release.md); layout/style N/A here) | `DOCKER-*` |

## Purpose

drunk maintains public open-source packages, not a deployed product — code quality on `main`
is what downstream consumers (other `baoduy` repos, and the public) actually run. This policy
fixes the cross-stack engineering intent (layout, typing, error handling, size discipline,
secrets hygiene) so a reviewer can apply one mental model across five toolchains, while each
stack's skill carries the toolchain-specific letter of the law.

## Scope

All production source in a drunk repo, in any of the five stacks above. Test code follows
[Policy 02](02-testing-and-quality.md). A repo's own `CLAUDE.md`/`AGENTS.md` overrides a
generic rule here where they differ (see Exceptions).

## Policy statements

1. **Repository layout — source lives under `src/`.** A new repo, or a new top-level project
   inside an existing repo, puts all application/library source under `src/` with tests under
   a sibling `tests/`: `src/<Project>/<Project>.csproj` + root `.sln`/`.slnx` for .NET
   (`NET10-STR-001`), TypeScript source under `src/` with `tsc` emitting to `bin/`
   (`TS-CFG-003`), and Python packages under `src/` with `conftest.py` putting `src/` on
   `sys.path` (`MCP-STR-001`). Pre-existing repos keep their current layout until their next
   restructure — this is not retroactive.
2. **Strict typing, zero `any` (TypeScript).** `strict`, `noImplicitAny` stay on; a widening
   cast (`as any`, `as unknown as T`) needs a one-line justification comment or it is a
   violation (`TS-CFG-001`, `TS-CFG-002`).
3. **Full type hints (Python).** Every function signature is fully type-hinted (args + return);
   public functions/classes/modules carry Google-style docstrings (`MCP-STY-001`).
4. **Rich, not anaemic, aggregates (.NET DDD).** State transitions live on the aggregate as
   intention-revealing methods; `private set;` + `IReadOnlyCollection<T>`; cross-aggregate
   references by id, never by object (`DKNET-AGG-001..004`). Domain never references EF
   provider types, HTTP clients, or `Infra` (`DKNET-LAYER-001`).
5. **No swallowed errors.** A `catch` adds context and rethrows or recovers — it never
   discards silently (`TS-ERR-001`); an `IResultBase` is never discarded unchecked
   (`DKNET-RES-002`); an MCP service logs the exception **type**, never the raw message, and
   never returns a raw error to the client (`MCP-SEC-001`, `MCP-SEC-002`).
6. **No exceptions for expected control flow.** Use typed results / narrowing for expected
   business branches; throw only for exceptional/boundary failures (`TS-ERR-003`,
   `DKNET-RES-001`).
7. **DRY thresholds are a trigger to look, not an automatic defect.** Same non-trivial block
   in 3+ places, or 2 places already drifted, gets named and fixed at the newer/tested
   instance — never averaged across both (`CLEAN-DRY-001`, `CLEAN-DRY-002`, `CLEAN-ORG-003`).
7a. **Test code reuses its harness; two copies of a setup block are already too many.** A new
   test extends the acceptance-test harness or the repo's shared fixture (a builder, a
   factory taking the fakes, a parameterised case) instead of copying its setup. A copied
   setup or arrange block of ~10 lines or more is a DRY defect at the second copy, because
   the repos' CI duplication gate (SonarCloud, new-code duplication over 3%) counts test
   code and fails the PR. DAMP still holds inside a test body: the rule targets copied
   setup, not readable assertions. Where the repo runs a duplication gate, the implementer
   checks the changed test files locally before pushing (`npx jscpd --min-lines 10
   --reporters console <changed test dirs>`).
8. **Less code, no speculative abstraction.** No dead code, no interface with one
   implementation and no test-double need, no redundant forwarding wrapper, no reinvented
   BCL/framework/stdlib behaviour (`CLEAN-LESS-001..004`). SRP size triggers: class >~300
   lines, method >~50 lines or complexity >10, constructor with 7+ deps (`CLEAN-SRP-001..003`).
9. **Secrets and PII never reach logs, code, or plain config.** No secret literal or exposed
   `Output` in Pulumi code — secrets flow through Key Vault (`PULUMI-SEC-001`); no PAN,
   token, or full request body in .NET logs (`LOG-002`); Helm secrets flow through
   `Secret`/external-secret references, never plaintext `values.yaml` (`HELM-K8S-004`).
10. **House formatting per stack, not personal taste.** TypeScript: Prettier only, no ESLint
    config added (`TS-FMT-001`). Python: double-quoted strings per the repo's formatter
    (`MCP-STY-001`). .NET: `.editorconfig` + analyzer defaults. Don't reformat a file outside
    the diff to match a different convention.
11. **Package manager discipline per stack.** TypeScript repos use `pnpm` exclusively —
    `pnpm-lock.yaml` only, never `package-lock.json`/`yarn.lock` (`TS-PKG-001`); bulk upgrades
    go through `pnpm run update`, not scattered manual bumps (`TS-PKG-004`).
12. **Public API compatibility for published packages.** A renamed/removed export, changed
    signature, or dropped `.d.ts`/public C# member is a breaking change: it ships with a
    `Breaking` changelog entry naming the replacement and bumps the **MINOR** version only
    (`TS-PUB-002`, `PULUMI-TEST-003`). The major number is frozen and owner-only — no agent
    bumps it for a break, see [Policy 08](08-container-build-and-release.md) statement 12
    (`VER-REL-001`). Additive-only changes carry no version marker at all; the pipeline
    numbers them as a patch.
13. **Helm: shared logic lives in the library chart.** Reusable template partials belong in
    `drunk-lib/templates/` (`type: library`); an app chart copy-pasting a `_helpers`-style
    block instead of consuming the library chart is a violation (`HELM-STR-001`). Every
    `.Values.*` a template reads is declared with a default and documented (`HELM-STR-003`).
14. **Async discipline (.NET).** Forward `CancellationToken` on I/O calls that accept one, use
    the `Async` suffix, never `async void` outside an event handler, never sync-over-async
    (`.Result`/`.Wait()`/`.GetAwaiter().GetResult()`) (`ASYNC-001..007`). An `async void`
    event handler catches `Exception` around its whole body, logs it, and leaves the operation
    in a defined state (an intercepted request is continued or aborted, never left hanging):
    an exception that escapes `async void` is rethrown on the thread pool and crashes the host
    process, so catching only a library's own exception type is not enough (`ASYNC-007`;
    DKNet PR #499, PdfGenerator request interception). Every `Promise` in
    TypeScript is awaited or explicitly handled — no fire-and-forget in the sync path
    (`TS-ERR-002`).
15. **The implementer proves the standards before handoff, not the reviewer after.** Every
    Build (and `build-ui` Build) ends with a **Standards self-review**, reported as its own
    EVIDENCE row: the stack's governing skill(s) opened by name and the rule-ids checked
    against the diff; a CodeGraph reuse search for every new public symbol, with its result
    (reused `<symbol>`, or none found); the SRP triggers of statement 8 measured on every
    touched class; the DRY triggers of statement 7 checked; SOLID at the boundaries the diff
    crosses — dependency direction per the stack's layering rules, published API extend-only
    (statement 12), one reason to change per new class. A change that adopts a framework or
    library API or pattern the repo does not already use checks that vendor's current
    official documentation and cites it in the row. A violation found is fixed inside the
    brief's §3, or listed in LEFT OPEN with `file:line`. dev-leader's implementation brief
    names the governing skill(s) and the 3–5 rule-ids most at risk for its surface
    (`Standards` row). A Standards row the diff contradicts is an `important` PR-gate
    finding; a missing one is a `nit`, because the gate runs the standards check itself
    ([Policy 04](04-code-and-spec-review.md) statement 5).

## Roles & responsibilities

- **dev-leader** — owns this policy; decomposes work so it lands under the right skill per
  stack; never writes code itself.
- **dev-backend** — implements against these standards inside the domain project the ticket
  resolves to (`drunk-net` / `drunk-pulumi` / `drunk-others`); applies SOLID/KISS/YAGNI and the
  stack's own skill, and proves it in the Standards self-review row (statement 15).
- **dev-leader** also names the governing skill(s) and the rule-ids most at risk in every
  implementation brief's `Standards` row.
- **pr-reviewer** — scores every PR against these rule-ids via `pr-review-gate`; a `blocking`
  finding on any id here caps the score regardless of the weighted average.
- **arch-reviewer** — runs the monthly `architecture-review-sweep`, matching the skill to each
  repo's stack, and converts mechanically-checkable rules into permanent lint/analyzer/test
  enforcement.

## Definition of Done / compliance

- The change conforms to the rule-ids of its stack's governing skill(s); no unresolved
  `blocking`/`important` finding under any id listed above.
- New repos and new top-level projects follow the `src/` layout (statement 1); no retrofit
  required on unrelated pre-existing repos.
- No secret or PII literal introduced anywhere in the diff, including logs and IaC output.
- Build/compile is clean: `tsc --strict`, `dotnet build` with zero new warnings, or the
  Python package's own lint/type check, as applicable.

## Enforcement

- **dev-backend's Standards self-review** (statement 15) is the first check, before the PR
  exists; pr-reviewer treats a contradicted row as an `important` finding and a
  missing one as a `nit` it checks itself.
- **`pr-review-gate`** scores every PR against the governing skill's rule-ids (security →
  correctness → testing → architecture & design → AI-slop); a `blocking` finding overrides the
  weighted average.
- **`architecture-review-sweep`** runs monthly across all stacks, applies the matching skill
  per repo, files ≤10 ranked findings after dedupe, and converts checkable rules into
  permanent enforcement (analyzer, lint config, or architecture test) in the repo's native
  mechanism.

## Exceptions & waivers

- A repo's own `CLAUDE.md`/`AGENTS.md` convention overrides a generic rule here — follow the
  repo, and flag a *harmful* convention upward rather than silently forking around it.
- Pre-existing repos are not required to retrofit the `src/` layout (statement 1) outside a
  planned restructure.
- No waiver exists for a secret/PII-in-logs finding or for a swallowed-error finding.

## References

- [`nodejs-typescript-standards`](../../skills/nodejs-typescript-standards/SKILL.md) — TS toolchain, config, formatting, error handling, test runner.
- [`python-mcp-standards`](../../skills/python-mcp-standards/SKILL.md) — src-layout, config, provider pattern, security-safe logging.
- [`dotnet10-efcore10-standards`](../../skills/dotnet10-efcore10-standards/SKILL.md) — language version attribution, EF Core 10 anti-patterns, clean-code thresholds.
- [`dknet-ddd-conventions`](../../skills/dknet-ddd-conventions/SKILL.md) — DKNet contract surface and DDD violation patterns.
- [`pulumi-azure-iac-standards`](../../skills/pulumi-azure-iac-standards/SKILL.md) — Builder pattern, naming, RBAC/security-by-default, type composition.
- [`helm-k8s-conventions`](../../skills/helm-k8s-conventions/SKILL.md) — chart structure, templating, K8s manifest hygiene.
