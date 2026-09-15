# Policy 01 — .NET Coding Standards

| | |
|---|---|
| **Policy ID** | MX-POL-01 |
| **Version** | 1.1 |
| **Status** | Active |
| **Owner** | dev-leader (dev-team) |
| **Applies to** | Every engineer and agent writing or modifying C#/.NET in Monxa repos |
| **Related skills** | [`dotnet10-efcore10-standards`](../../skills/dotnet10-efcore10-standards/SKILL.md) · [`dknet-ddd-conventions`](../../skills/dknet-ddd-conventions/SKILL.md) |
| **Enforced at** | PR review gate ([`pr-review-gate`](../../skills/pr-review-gate/SKILL.md)) · architecture review sweep ([`architecture-review-sweep`](../../skills/architecture-review-sweep/SKILL.md)) |

> **Authority.** This policy is the source of truth for .NET coding standards. The two
> skills above **implement** it and must conform to it; the review gates derive their
> rule catalog from it. Amend this policy first, then cascade the change into the skills
> and the analyzer config — see [change control](00-policies-index.md#change-control).
> The one legitimate downward override is a repo's own `CLAUDE.md` (statement 14).

## Standards at a glance

```
   THIS POLICY (rules & rule-ids: NET10-* EFC-* DKNET-* DOC-* CLEAN-*)
        │ implemented by
        ├── dotnet10-efcore10-standards ──┐
        └── dknet-ddd-conventions ────────┤ loaded by dev-backend / arch-reviewer / pr-reviewer
                                          ▼
   Layer & dependency model the code MUST follow:

        Api ─────▶ AppServices ─────▶ Domains          Domains has NO infra deps
        (HTTP,        (all business      (aggregates,        (DKNET-LAYER-001)
         CLI jobs)     logic; injects     value objects,
                       IRepositorySpec)   domain events)
                            │
                            ▼
                         Infra  (DbContext, migrations, repositories, Service Bus)
        Share  ── cross-cutting, referenced by all layers

   Aggregate contract:  private ctor + static factory → private set; → IReadOnlyCollection
                        → reference-by-id → raise events inside the transition → return IResultBase
```

## Purpose

Monxa is a payment gateway: correctness on money and identity paths dominates every
other cost. This policy fixes the language, framework, and domain-design rules so the
code is consistent, reviewable against stable rule-ids, and safe to change. The rule-ids
(`NET10-*`, `EFC-*`, `DKNET-*`, `DOC-*`, `CLEAN-*`) are finding fingerprints: a reviewer
files under an id, a developer fixes under the same id, no translation needed.

## Scope

All production C# targeting **.NET 10 / C# 14 / EF Core 10** in solutions that reference
`DKNet.*` (all Monxa services). Test code follows [Policy 02](02-testing-and-quality.md).
Solution-local `CLAUDE.md` conventions **override** these generic rules where they differ.

## Policy statements

1. **Target the right version.** Never flag a feature as missing that shipped earlier. C# 14/.NET 10 adds: extension members, the `field` keyword, null-conditional assignment (`x?.Prop = v`), `nameof` on unbound generics, partial constructors/events. Collection expressions `[..]` and primary constructors are **C# 12**; `params` collections and `System.Threading.Lock` are **C# 13**. Cite the correct version in any modernization note. (`NET10-LANG-001..005`)
2. **Layering is non-negotiable.** `Api` → `AppServices` → `Domains` (no infra deps); `Infra` holds DbContexts/migrations/repos; `Share` is cross-cutting. Domain must never reference EF provider types, HTTP clients, or `Infra` (`DKNET-LAYER-001`). Business logic never lives in the API layer (`DKNET-LAYER-002`).
3. **Rich aggregates, never anaemic ones.** State transitions live on the aggregate as intention-revealing methods, not in handlers (`DKNET-AGG-001`). Properties use `private set;` (`-002`); collections are exposed as `IReadOnlyCollection<T>` over a private backing field (`-003`); cross-aggregate links are **by id**, not object reference (`-004`); a private ctor + static factory guards validity (`-007`); keys are `Guid` UUIDv7 via the configured generator, never set manually (`-008`).
4. **Value objects over primitives.** Money, currency, email, phone, code are records/value objects — not `decimal`/`string` (`DKNET-AGG-006`).
5. **Domain events are raised inside the transition** that causes them, carry **ids + changed values** (never the tracked entity), and are never raised on someone else's aggregate (`DKNET-EVT-001..003`).
6. **Repositories & specifications.** Inject `IReadRepository<T>` where only reads happen, never the read+write `IRepository<T>` (`DKNET-REPO-001`). Predicates live in a `Specification<T>`, not as ad-hoc `Query().Where(...)` in handlers (`DKNET-REPO-002`). `DbContext` is never injected into `AppServices` (`DKNET-REPO-004`).
7. **Do not double-save, do not redundantly update.** `EfAutoSavePostInterceptor` calls `SaveChangesAsync` after command handlers — no manual save in a handler (`DKNET-REPO-005`). **`UpdateAsync` on a *tracked* entity is delete-on-sight** (`DKNET-REPO-006`): the tracker already holds it, `Update` marks every column `Modified` and clobbers concurrent writers. `UpdateAsync` is **only** for a detached entity (read with `AsNoTracking()`, loaded on a different `DbContext`, or rebuilt from a DTO/payload).
8. **FluentResults, not exceptions, for expected business failure** (`DKNET-RES-001`); a returned `IResultBase` is never discarded unchecked (`DKNET-RES-002`).
9. **Tenant ownership is enforced by the marker.** A merchant/tenant-owned entity carries `IOwnedBy`/`IMerchantOwnedEntity` or the row filter silently does not apply (`DKNET-AUTH-001`); an `IgnoreQueryFilters()` needs a justifying comment (`DKNET-AUTH-002`).
10. **Async discipline.** Forward `CancellationToken` on I/O; `Async` suffix; no `async void` (outside event handlers); no sync-over-async (`.Result`/`.Wait()`/`.GetAwaiter().GetResult()`); `ConfigureAwait(false)` in **library** projects only, never ASP.NET Core app code (`ASYNC-001..006`).
11. **EF Core correctness.** No N+1; `AsNoTracking()` on read-only queries; project to DTOs rather than materialising graphs; prefer complex types over owned types; use translated `LeftJoin`/`RightJoin`; watch the EF Core 10 parameterized-collection and `ExecuteUpdateAsync` changes. (`EFC-*`)
12. **XML docs carry the WHY.** Every `public`/`protected` member in `Domains`, `AppServices`, `Share` has an XML doc that states the business rule / caller constraint — not a restatement of the signature (`DOC-001..007`). Enforce *missing* mechanically via `<GenerateDocumentationFile>` + CS1591; the rest is author + reviewer judgment. Hard cap 500 chars/block; `<inheritdoc/>` on implementations.
13. **Less code.** No dead code, no speculative abstraction (interface with one impl and no test-double need), no redundant wrappers, no reinvented BCL (`CLEAN-LESS-001..004`). SRP thresholds are triggers for a look: class > ~300 lines, method > ~50 lines / complexity > 10, ctor with 7+ deps (`CLEAN-SRP-001..003`). DRY at 3 occurrences (2 if already drifted) (`CLEAN-DRY-001/002`). Never solve one concern two ways — name the newer/tested winner and flag the other, don't average (`CLEAN-ORG-003`).
14. **Monxa solution-local rules.** Handlers inject `IRepositorySpec`; feature folders `AppServices/Features/<Feature>/{Actions,Queries,Services,EventHandlers,Specs}`; schemas via `InfraConsts.*` constants; `[GenerateDto(...)]` must `Exclude` **every** navigation property; amount rounding is global via `AmountRoundingInterceptor<>` (never round in a handler); every state-changing `POST` has `.RequiredIdempotentKey()`.
15. **No secrets or PII in logs** (`LOG-002`); use `[LoggerMessage]` source-gen logging on hot paths (`LOG-001`).
16. **Repository layout.** A new repo puts all source under `src/` (`src/<Project>/<Project>.csproj`), tests under `tests/`, and the single solution file at the repo root (`NET10-STR-001`). New top-level projects follow this; pre-existing repos migrate on their next restructure, not retroactively.

## Best practices for .NET developers

Copy the canonical shapes — the violations then cannot happen. Full worked examples in
[`dknet-ddd-conventions`](../../skills/dknet-ddd-conventions/SKILL.md) ("Authoring reference").

- **Aggregate:** private ctor + `static Open(...)` factory; `IReadOnlyCollection<T> Lines => _lines;`; mutate + `AddEvent(...)` inside the transition; return `IResultBase`; reference other aggregates by `Guid`.
- **Query handler:** `IPageHandler<,>` injecting `IRepositorySpec`, predicate in a `Spec`, project to `Dto`, forward `ct`, no save.
- **Command handler:** `FindAsync` the aggregate (tracked) → call its method → **return the result, no `UpdateAsync`, no `SaveChangesAsync`.** The detached counter-example (`AsNoTracking()` → mutate → `UpdateAsync`) is the *only* place the call belongs.
- **Before writing a predicate/mapping/guard:** grep the slice's `Specs/` and `Share/` first — the three recurring duplications are the same `Where` in two handlers (→ one spec), the same guard in every handler (→ an aggregate invariant or a `BeforeSaveHook`), and a hand-written projection twice (→ `[GenerateDto]`).
- **Docs:** delete a doc and if no information is lost, it was `DOC-002` noise — say *why* a property has no setter, *when* a method fails, *what* an expiry rule is.

## Definition of Done / compliance

- Build clean, **zero new warnings**.
- No `blocking` finding under any `NET10-*`, `EFC-*`, `DKNET-*`, `DOC-*`, `CLEAN-*` id on the diff.
- The change conforms to the impl-brief's Change set (see [Policy 06](06-requirements-and-spec.md)).
- Public/protected members in the three documented layers carry meaningful XML docs.

## Enforcement

- **`pr-review-gate`** scores every squad PR against these ids (security → correctness → testing → maintainability → AI-slop); a `DKNET-REPO-006` on a concurrent money path without `RowVersion` is `blocking`.
- **`architecture-review-sweep`** runs on a schedule, files ≤10 ranked findings, and converts mechanically-checkable rules into permanent architecture tests.

## Exceptions & waivers

- A solution-local `CLAUDE.md` convention overrides a generic rule here — follow the repo, and flag a *harmful* convention rather than forking around it.
- Deviating from a REUSE row or exceeding an ADD-NEW ceiling requires a comment on the main ticket **before** the PR opens (see [Policy 06](06-requirements-and-spec.md)).
- No waiver exists for missing tests on touched logic or for secrets/PII in logs.

## References

- [`dotnet10-efcore10-standards`](../../skills/dotnet10-efcore10-standards/SKILL.md) — full rule catalog + doc shapes + verified version attribution.
- [`dknet-ddd-conventions`](../../skills/dknet-ddd-conventions/SKILL.md) — DKNet contract signatures, `DKNET-*` rules, canonical aggregate/handler/spec shapes.
- Microsoft Learn: [C# 14](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14) · [CA2007](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007) · [CA1848](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1848)
