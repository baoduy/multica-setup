---
name: dotnet10-efcore10-standards
description: Verified .NET 10 / C# 14 / EF Core 10 / ASP.NET Core 10 review standards — language features by correct version, EF Core 10 breaking changes, EF query anti-patterns with official doc links, migration safety, error handling, and CA/Meziantou analyzer rule IDs reviewer should expect. Use when reviewing or modernizing C# code targeting .NET 10 and EF Core 10.
---

# .NET 10 / EF Core 10 Review Standards

Verified against Microsoft Learn and dotnet/efcore, 2026-07-29. Every rule carries stable `rule-id` for use as finding fingerprint.

## Repository layout

- `NET10-STR-001` **Code outside `src/`.** New repo puts all application/library projects under `src/` (`src/<Project>/<Project>.csproj`), tests under `tests/` alongside it, and single `.sln`/`.slnx` at repo root. Don't scatter `.csproj`s at root or invent bespoke top-level layout. Existing repos that predate this keep their layout until restructure; new repos and new top-level projects follow it.

## Get version attribution right

Most common way to be wrong here is to flag something as "not using C# 14 feature" when feature shipped two versions ago. Reviewers lose credibility fast doing that.

**Actually C# 14 / .NET 10:** extension members (`extension(Type x) { }` blocks — extension *properties*, static members, operators), `field` keyword, null-conditional assignment (`x?.Prop = v`), `nameof` on unbound generics, modifiers on simple lambda parameters, partial constructors and events, more implicit `Span<T>` conversions, user-defined compound assignment.
→ https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14

**NOT C# 14 — do not attribute these to it:**
- Collection expressions (`[..]`) and primary constructors → **C# 12 / .NET 8**
- `params` collections and `System.Threading.Lock` → **C# 13 / .NET 9**

They are still fine to raise in modernization pass — just cite right version.

### Language rules

- `NET10-LANG-001` **Manual backing field for trivial property.** `private T _x; public T X { get => _x; set => _x = Normalize(value); }` collapses to `field` keyword.
- `NET10-LANG-002` **Null-guard that collapses to null-conditional assignment.** `if (x is not null) x.P = v;` → `x?.P = v;`. (`++`/`--` still not allowed with `?.`.)
- `NET10-LANG-003` **Extension method that reads as property.** `IsEmpty()` where extension property fits better. Only raise when it genuinely improves call site.
- `NET10-LANG-004` **Pre-C#12 collection construction.** `new List<T> { a, b }` / `.ToArray()` chains where collection expression is clearer.
- `NET10-LANG-005` **Source-generator workaround** (factory/init methods) that partial constructors or events now replace.

## EF Core 10

### What changed that reviewer must know

- **Complex types matured** — optional complex types, complex-type→JSON mapping, struct-backed complex types. Official guidance: prefer complex types over owned entity types for table-splitting and JSON.
- **Parameterized collections** — `.Contains(array)` now emits multiple scalar parameters (`IN (@id1, @id2)`) instead of one JSON array, giving planner cardinality. Tunable via `UseParameterizedCollectionMode`, `EF.Constant`, `EF.Parameter`, `EF.MultipleParameters`.
- **`ExecuteUpdateAsync`** takes plain lambda (no longer expression tree) and supports JSON columns on `ToJson()` complex types.
- **Named query filters** — `HasQueryFilter("Name", ...)`, multiple filters per entity, selective `IgnoreQueryFilters(["Name"])`. This removes old one-filter-per-type limit.
- **`LeftJoin`/`RightJoin`** LINQ operators are translated — retire `SelectMany` + `GroupJoin` + `DefaultIfEmpty`.
- **Split-query ordering fix** — consistent `ORDER BY` across split queries, closing real data-correctness bug.
- **Security** — `EF.Constant` values redacted from logs by default; new build-time analyzer for string concatenation in raw-SQL APIs.
- **SQL Server/Azure SQL native `json` and `vector` types**; `EF.Functions.VectorDistance()`.

→ https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/whatsnew

### Breaking changes to check on upgrade

EF tools need `--framework` on multi-targeted projects · Application Name auto-injected into connection strings (can escalate distributed transactions when EF and Dapper share connection) · SQL Server `json` type by default at compat ≥170 / `UseAzureSql` · parameterized-collection default change (plan-cache impact) · `ExecuteUpdateAsync` source break · complex-type column names uniquified and nested ones use full path names · `IDiscriminatorPropertySetConvention` signature change · `IRelationalCommandDiagnosticsLogger` gained `logCommandText` · **SQL parameter names simplified** (`@city`, not `@__city_0`) — breaks any test asserting on generated SQL and can spike plan recompilation on deploy · **Microsoft.Data.Sqlite 10** has high-impact `DateTime`/`DateTimeOffset` UTC handling changes.

→ https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-10.0/breaking-changes

### EF query anti-patterns

- `EFC-001` **N+1 from lazy loading.** Navigation accessed in loop. → https://learn.microsoft.com/en-us/ef/core/querying/related-data/lazy
- `EFC-002` **Missing `AsNoTracking()` on read-only path.** Query result is projected/returned and never mutated. → https://learn.microsoft.com/en-us/ef/core/querying/tracking
- `EFC-003` **Cartesian explosion.** Multiple sibling `Include`s on collection navigations without `AsSplitQuery()`. → https://learn.microsoft.com/en-us/ef/core/querying/single-split-queries
- `EFC-004` **Client-side evaluation.** `.AsEnumerable()`/`.ToList()` mid-query, or predicate calling non-translatable method. → https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying
- `EFC-005` **Raw SQL injection risk.** Concatenated or interpolated user input into `FromSqlRaw`/`ExecuteSqlRaw`. Use `FromSql` or parameterized overloads. EF10 ships analyzer for this. → https://learn.microsoft.com/en-us/ef/core/querying/sql-queries
- `EFC-006` **`SaveChangesAsync` inside loop.** Batch into one unit of work. *(No dedicated official page — cite two performance pages.)* → https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying
- `EFC-007` **Global query filter pitfall.** Filter defined on non-root type of hierarchy, filter cycles, or reliance on filters with compiled models. → https://learn.microsoft.com/en-us/ef/core/querying/filters
- `EFC-008` **`DbContext` lifetime/pooling misuse.** Context captured by background worker or parallel task without `AddDbContextFactory`/`AddPooledDbContextFactory`. → https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/
- `EFC-009` **Over-materialisation.** Whole entity graph loaded to read two columns; project to DTO instead. → https://learn.microsoft.com/en-us/ef/core/performance/advanced-performance-topics
- `EFC-010` **Migration hygiene.** Divergent model snapshots from parallel branches, or `dotnet ef database update` against production instead of idempotent SQL scripts. → https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/teams
- `EFC-011` **Unbounded query.** List endpoint or job query with no pagination or row cap.
- `EFC-012` **Owned entity type used where complex type now fits** (table-splitting / JSON) under EF10 guidance.

### Migration safety

A migration runs against data the previous release still reads. Check every new file under `Migrations/`.

- `EFC-013` **Rename scaffolded as drop + add.** EF scaffolds a renamed property or table as `DropColumn` + `AddColumn`, which loses the data. Edit the migration to `RenameColumn` / `RenameTable`. → https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/managing
- `EFC-014` **Drop in the same release as the code that stops using it.** A column or table the previous release still reads is dropped in the migration that ships with the code change. Remove the code first; drop the column in a later release. A rename on a live table goes expand → contract: add the new column, write both, backfill, switch reads, then drop the old one.
- `EFC-015` **New required column on a populated table.** A `NOT NULL` column with no default fails on existing rows, or a default silently invents values. Add it nullable, backfill, then make it required in a later migration.
- `EFC-016` **Schema change and bulk data change in one migration.** A large `migrationBuilder.Sql` backfill beside DDL holds locks for the whole run. Put the backfill in its own migration, batched.
- `EFC-017` **Blocking index build on a large table.** PostgreSQL: create it concurrently (Npgsql `IsCreatedConcurrently()`, or `migrationBuilder.Sql(..., suppressTransaction: true)`). SQL Server: `ONLINE = ON` where the edition supports it.
- `EFC-018` **Edited migration.** A migration already merged to `dev` is never edited, renamed or deleted; a fix is a new migration. Its model snapshot stays in step.

## ASP.NET Core 10

- `ASP-001` **Hand-rolled validation** duplicating built-in Minimal API validation (`AddValidation()`, `Microsoft.Extensions.Validation`, per-endpoint `.DisableValidation()`).
- `ASP-002` **OpenAPI 3.1 assumptions.** Nullable is now `oneOf` / `type: [null, T]`, not `nullable: true`; `OpenApiAny` → `JsonNode`; `OpenApiSchema.Nullable` removed. Flag snapshot tests and consumers that assume 3.0 shape.
- `ASP-003` **Business logic in endpoint.** Endpoints map request → bus/handler → response, nothing more.
- `ASP-004` **Missing idempotency on state-changing POST** where solution has idempotency convention.
- `ASP-005` **Cookie-auth 401 behaviour change** — API endpoints now return 401/403 rather than redirecting to login. Flag code that depended on redirect.

→ https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0

## Async, cancellation, logging

- `ASYNC-001` **`CancellationToken` not forwarded** to call that accepts one (**CA2016**, Meziantou **MA0040**). → https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2016
- `ASYNC-002` **No `CancellationToken` parameter** on async method that performs I/O (Meziantou **MA0032**).
- `ASYNC-003` **`async void`** outside event handler.
- `ASYNC-004` **Sync-over-async** — `.Result`, `.Wait()`, `.GetAwaiter().GetResult()`.
- `ASYNC-005` **Missing `ConfigureAwait`** in *library* projects (**CA2007**, Meziantou **MA0004**). Not applicable to ASP.NET Core app code — no `SynchronizationContext`. Do not flag it there. → https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca2007
- `ASYNC-006` **Missing `Async` suffix** on async method.
- `ASYNC-007` **`async void` event handler without a catch-all** — the whole body sits in `try { … } catch (Exception ex)`, which logs and leaves the operation in a defined state (an intercepted request is continued or aborted). Catching only a library type such as `PuppeteerException` lets any other exception escape and crash the host (Policy 01 statement 14).
- `NET10-ERR-001` **Swallowed exception.** An empty `catch`, or one that only logs and continues as if the call succeeded (Policy 01 statement 5).
- `NET10-ERR-002` **Fallback that hides a failure.** A failed call returns an empty collection, `null` or `default` where the caller cannot tell failure from an empty result. Return a failed `IResult`/`Result`, or let the exception through.
- `NET10-ERR-003` **Lost stack trace.** `throw ex;` instead of `throw;`, or a new exception thrown without the caught one as its inner exception.
- `LOG-001` **Non-source-generated logging on hot path** (**CA1848**) — use `[LoggerMessage]`. → https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1848
- `LOG-002` **Sensitive data in logs** — PAN, tokens, full request bodies, secrets.

## Clean code — DRY / SOLID / less code

Thresholds are triggers for look, not automatic defects. Say why specific instance is problem, or don't file it.

- `CLEAN-DRY-001` **Duplicated logic.** Same non-trivial block in 3+ places, or 2 places in different slices.
- `CLEAN-DRY-002` **Copy-paste divergence.** Near-identical blocks that have drifted — dangerous kind, since one gets fixed and other doesn't.
- `CLEAN-SRP-001` **Class over ~300 lines** or with more than one reason to change.
- `CLEAN-SRP-002` **Method over ~50 lines** or cyclomatic complexity > 10.
- `CLEAN-SRP-003` **Constructor with 7+ dependencies** — type is doing too much.
- `CLEAN-OCP-001` **Type-switch on enum/type** repeated across files where polymorphism or keyed service fits.
- `CLEAN-LSP-001` **Override that throws `NotSupportedException`** or silently no-ops.
- `CLEAN-ISP-001` **Fat interface** — implementers forced to stub members they don't need.
- `CLEAN-DIP-001` **Concrete infrastructure dependency** where abstraction exists.
- `CLEAN-LESS-001` **Dead code** — unreferenced public types/members, commented-out blocks, unreachable branches.
- `CLEAN-LESS-002` **Speculative abstraction** — interface with exactly one implementation and no test-double or extension need.
- `CLEAN-LESS-003` **Redundant wrapper** — service that only forwards to another.
- `CLEAN-LESS-004` **Reinvented BCL/framework behaviour.**
- `CLEAN-ORG-001` **Misplaced file** — type not in feature slice it belongs to.
- `CLEAN-ORG-002` **Grab-bag `Helpers`/`Utils`/`Common` type** accumulating unrelated members.
- `CLEAN-ORG-003` **Inconsistent solution** — same concern solved two ways. Name newer / better-tested one as winner and flag other for cleanup. Do not split difference.

## Not independently verified

Flagged honestly rather than presented as fact:
- Exact verbatim wording of Meziantou **MA0032** / **MA0040** — intent above is correct; fetch `docs/Rules/MA0032.md` and `MA0040.md` from github.com/meziantou/Meziantou.Analyzer before quoting them in style guide.
- `EFC-006` has no dedicated official page; two performance pages cited are real sources.
- `EFC-017`: `IsCreatedConcurrently()` is the Npgsql provider's index-builder extension; confirm it exists in the repo's Npgsql version before citing it, else use the `suppressTransaction` SQL form.