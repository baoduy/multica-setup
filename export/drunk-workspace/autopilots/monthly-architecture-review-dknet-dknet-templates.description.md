# Goal

Each month, run a full architecture review of the DKNet framework repository AND the DKNet.Templates repository, filing the highest-value findings into the `drunk-net` backlog for human triage. This run issue IS the review — two repos, one agent task, no fan-out.

The review has one purpose: make the code **smaller, newer, cleaner and safer without changing what it does**. Every finding is a concrete, behaviour-preserving change — not an observation.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, role `owner`; never a hardcoded UUID). The enhancement issues you file are the deliverable for triage; the report on this issue is the index.
- **Scope** — TWO repos, each swept with the full procedure:
  1. `DKNet` — https://github.com/baoduy/DKNet.git. The framework library every DKNet-based service depends on (`DKNet.EfCore.*`, `DKNet.Svc.*`, `DKNet.Fw.*`) — a defect here compounds into every consumer.
  2. `DKNet.Templates` — https://github.com/baoduy/DKNet.Templates.git. The project templates new services are scaffolded from — a defect here is baked into every new service at day zero. The scaffolded template content (projects, config files) is in scope, not just the packaging code.
  Do NOT review any other repo in this run.
- **Project** — this run issue and every filed finding live in `drunk-net` (id from `multica project list --output json`). Never cross-file into another project.
- **How** — your agent instructions already define the procedure: invoke the `architecture-review-sweep` skill and follow it end to end PER REPO (checkout, CodeGraph index, scope/exclusions, shard, rank, dedupe, enforcement PR against that repo's `dev`, report). Read each repo's own `CLAUDE.md` / `AGENTS.md` FIRST — solution-local conventions override the generic rules.
- **Toolchain baseline** — both repos pin SDK `10.0.0` (`src/global.json`) with `LangVersion` `latest`, so **.NET 10 / C# 14 / EF Core 10 features are already available** and a finding may assume them. Re-read `global.json` and `Directory.Build.props` at the start of each sweep instead of trusting this line — if the pin has moved, the pinned version wins. A framework or SDK **version bump is never itself a finding**.
- **Constraints**
  - Findings are filed at `backlog`, children of this run issue (`--parent`), `--assignee-id <triager user_id>` resolved at runtime as the workspace owner (`multica workspace member list --output json`, role `owner`; never a hardcoded UUID, never `--assignee` by name), titled `[A<N>-<n>] [<RULE-ID>] <what and where>` where `N` is this run issue's number — one `[A<N>-<n>]` sequence shared across both repos — with the `Arch fingerprint`, `Arch severity`, `Arch repo` and `Owner` properties set (`Arch repo` is `DKNet` or `DKNet.Templates`).
  - Cap: at most 10 findings filed TOTAL across both repos — rank globally after both sweeps, not 10 per repo.
  - Dedupe fingerprint: `<repo>:<rule-id>:<relative/path/File.cs>:<SymbolName>` where `<repo>` is `DKNet` or `DKNet.Templates`. Never re-file a finding with an open issue.
  - Enforcement PRs are test-only, target `dev`, both `--head` and `--base` explicit, ONE PR per repo and only where that repo has enforcement-worthy findings; build and tests green locally before pushing.
- **Inputs** — none; monthly schedule.

# Behaviour-preservation gate — applies to EVERY finding

These are published NuGet packages. Downstream services compile against them and a silent behaviour change surfaces in someone else's production, not here. Before a finding is filed it must pass all four:

1. **Observable behaviour unchanged** — same inputs, same outputs, same exceptions, same persisted data, same emitted SQL. A finding that "improves" behaviour is a different ticket; say so and file it as its own finding, never smuggled inside a cleanup.
2. **Public API unchanged** — no removed or renamed public/protected type, member or parameter, no changed default value, no narrowed nullability on an input, no widened nullability on an output. If the improvement genuinely requires a public surface change, file it with `breaking:` as the first word of the `## Proposed solution` section, rank it one level lower, and cap breaking findings at **1 per run** — the owner decides those, not the sweep.
3. **Covered by existing tests** — name the test(s) that would fail if the change altered behaviour (`codegraph explore` reports coverage per symbol). No covering test → the finding must include adding a characterization test for today's behaviour FIRST, as step 1 of the proposed solution.
4. **Net code reduction or net risk reduction** — state the approximate LOC delta (`~-40 lines`) or the concrete risk closed. A refactor that adds lines and closes no risk is not filed. Deleting code is a valid, welcome finding on its own.

A finding that cannot pass this gate is not softened until it fits — it is dropped and listed in the deferred section of the report.

# Review dimensions — the six focus areas

Every finding belongs to exactly one focus area and cites a catalogue rule-id. Rule catalogues come from the `dotnet10-efcore10-standards` and `dknet-ddd-conventions` skills; solution-local conventions in a repo's own `CLAUDE.md` win on conflict.

## F1 — Modernize onto current .NET/C#/EF Core features

Code that a language, runtime or framework feature **already available at the repo's pinned SDK** would collapse to less code or make safer. Rule-ids: `NET10-LANG-*`, `EFC-*`, `ASP-*`, `ASYNC-*`; else `MODERNIZE-001`.

Hunt specifically for hand-rolled code the platform now does: collection and index/range expressions over manual list building, primary constructors over field+constructor boilerplate, `required`/`init` over defensive setters, pattern matching over `if`/`as`/null chains, `System.Text.Json` source generation over reflection paths, `TimeProvider` over `DateTime.UtcNow`, `IAsyncEnumerable`/`await foreach` over materialized lists, `FrozenDictionary`/`SearchValues` over hot-path lookups, `ArgumentNullException.ThrowIfNull` and friends over hand-written guards, EF Core 10 bulk `ExecuteUpdate`/`ExecuteDelete` over load-then-save loops, `ILogger` source-generated `[LoggerMessage]` over interpolated log calls.

Cite the version that introduced the feature. Flagging a feature the pinned SDK predates is the fastest way to lose credibility — and never propose a language feature by bumping `LangVersion` or the TFM.

## F2 — Cleaner code

The same behaviour expressed with less ceremony: nested conditionals flattened to guard clauses, long methods split at their seams, primitive obsession replaced by the value object the domain already defines, comments that only restate the code deleted along with the code they defend, duplicated bodies (DRY) collapsed to one. Rule-ids: `CLEAN-*`, `DOC-*`; DDD-specific shapes use `DKNET-*`.

Clean means **fewer moving parts**, not more layers. A finding that introduces an interface with one implementation, a factory for one product, or a config knob for a value that never changes is an anti-finding — do not file it.

## F3 — Security

DKNet ships encryption, data-authorization and blob-storage packages that downstream services trust blindly, and DKNet.Templates stamps its defaults into every new service. Security findings rank `critical`/`high`, never below, and every `critical`/`high` one is filed even if that consumes the whole run's cap. Run this pass over every public API surface and trust boundary of each repo, with these stable rule-ids:

- `SEC-001` data-authorization gap — a row-level filter that can silently not apply (`IOwnedBy` marker missed, filter defined on a non-root type), or `IgnoreQueryFilters()` reachable without an explicit justification;
- `SEC-002` secret in source or committed config — connection strings, API keys, test credentials in `appsettings*.json` or test fixtures; secrets must come from environment/key vault. In DKNet.Templates, a real-looking secret stamped into scaffolded template content counts; an obvious placeholder does not;
- `SEC-003` unvalidated input at a public API boundary — public library entry points that pass caller input through to SQL, file paths, or blob keys without validation;
- `SEC-004` SQL or command built by concatenating input — `FromSqlRaw`/`ExecuteSqlRaw` (extends `EFC-005`), string-built SQL in `Relational.Helpers`, `Process.Start`;
- `SEC-005` sensitive-data exposure — keys, plaintext of encrypted fields, or full payloads in logs or exception messages (extends `LOG-002`); the `.Encryption` packages must never log what they protect;
- `SEC-006` crypto misuse — homemade crypto, MD5/SHA1 in a security context, ECB mode, static/reused IVs, keys held in strings, or non-constant-time comparison of MACs/tokens (use `CryptographicOperations.FixedTimeEquals`) — audit `DKNet.EfCore.Encryption` and `DKNet.Svc.Encryption` end to end;
- `SEC-007` insecure default — a public API whose default configuration is the unsafe option (encryption opt-in where it should be opt-out, authorization filter disabled unless configured, permissive fallback on missing config); in DKNet.Templates this includes unsafe defaults scaffolded into new services;
- `SEC-008` known-vulnerable dependencies — run `dotnet list package --vulnerable --include-transitive` and file one finding per critical/high advisory (fingerprint anchor: the `.csproj` path and package name).

Security is the one place the behaviour-preservation gate bends: closing a hole may change behaviour by design. When it does, say exactly what changes and who notices, under a `## Behaviour change` heading in the finding body — never omit it.

## F4 — Organisation: fewer types, fewer files, less code

Where the code is correct but laid out wrong: types living in the wrong project or namespace, a class doing two jobs, one job split across two classes, a folder whose name no longer matches its contents, public surface that should be `internal`, dead code with no inbound reference (`codegraph` proves this — grep cannot). Rule-ids: `CLEAN-*` for structure, `DKNET-*` for layering breaches; else `ORG-001`.

Prefer the finding that **deletes** a type over the one that adds one. Merging two anaemic classes into one, or dropping an abstraction with a single caller, is worth more than any new arrangement of the same volume of code. Layering findings (project reference graph vs. intended onion) belong here and rank `high`.

## F5 — Reuse a maintained NuGet package instead of hand-rolled code

Hand-written code that a mature, actively-maintained package — or the BCL itself — already provides. Rule-id: `CLEAN-LESS-004` for the in-box/BCL case, `REUSE-001` for a new package.

Bar for **replacing hand-rolled code with an in-box BCL type**: none beyond the gate. This is the preferred outcome — always check the BCL before naming a package.

Bar for **adding a new package dependency** — all must hold, and be stated in the finding body:
- the hand-rolled block is non-trivial (retry/backoff, date/time math, validation, crypto, parsing, resilience, rate-limiting) — never a few lines;
- the package had a release within the last 12 months and is not deprecated (`dotnet package search` / nuget.org listing; state the version and last-release date);
- license is MIT/Apache-2.0-compatible;
- `dotnet list package --vulnerable --include-transitive` is clean for it, and it drags in no heavy transitive graph;
- net code reduction is real, and the risk it removes is named.

DKNet is itself a library: every dependency it takes is forced on every consumer. When in doubt between "keep 60 hand-rolled lines" and "publish a new transitive dependency to every downstream service", keep the 60 lines and do not file. Prefer a Microsoft-published or foundation-governed package (e.g. `Microsoft.Extensions.*`, `System.*`) over a single-maintainer one at equal fit.

## F6 — Package upgrades available for the current framework (inventory, mostly report-only)

Existing package references that have a newer stable release compatible with the pinned target (`net10.0` today). Rule-id: `DEPS-001`. Run per repo, in both `src/Directory.Packages.props` and any per-project override:

```bash
dotnet list package --outdated
dotnet list package --deprecated
dotnet list package --vulnerable --include-transitive
```

**Default outcome is a table in the run report, not a filed issue.** A routine version bump is mechanical work that the `🚀 Monthly NuGet Upgrade — DKNet` autopilot already delivers as one PR; re-filing the same bumps here would double the backlog and collide on triage. Report the inventory per repo as:

| package | current | latest stable on `net10.0` | kind | action |
|---|---|---|---|---|

where `kind` is `framework-family` (`Microsoft.*` / `System.*` / EF Core / ASP.NET Core, align to latest 10.x.x) or `third-party`, and `action` is `routine bump` / `needs code change` / `deprecated` / `vulnerable`. Stable releases only — never list preview/rc/beta as an upgrade target. Never propose a TFM or SDK bump.

**File a finding only when the upgrade is NOT mechanical** — that is where this sweep adds something the upgrade autopilot cannot:
- a major-version jump whose release notes require source changes (name the breaking change and the call sites, `codegraph` proves the blast radius) — `high` if it also closes a vulnerability, else `medium`;
- a package marked **deprecated** or with no release in 24 months, where the fix is migrating to the successor package (name it) or dropping the dependency — `medium`, `high` if it is on a security path;
- an upgrade that unlocks a real code deletion (the new version ships in-box what this repo hand-rolls) — cross-reference F5 and file under `CLEAN-LESS-004`/`REUSE-001` instead, not `DEPS-001`;
- a vulnerable package stays where it already is: F3 `SEC-008`, not here. Do not file both.

`DKNet.Templates` is outside the NuGet-upgrade autopilot's scope entirely, so its inventory is the only upgrade signal anyone gets — always include it, and note that outdated pins in scaffolded template content ship stale versions into every new service.

# Ranking and the 10-issue cap

Rank globally across both repos: severity first, then blast radius (public API and consumer count), then fix cost ascending.

Balance the run so it does not return ten of the same shape:
- every F3 finding at `critical`/`high` is filed first, ahead of every other focus area, and may take the whole 10-issue cap; any beyond 10 go in the run report, never filed;
- of the remaining slots, at most **4 from any one focus area**, and at most **2 from F6** (its default output is the report table, not issues);
- at most **1** `breaking:` finding per run;
- a `low` finding is filed only if the cap is not otherwise reached.

Everything ranked but not filed goes in the run report, grouped by focus area, so nothing is lost.

# Steps

1. **Set this issue to `in_progress`.** `multica issue status <this-issue-id> in_progress`.
2. **Review both repos** per your instructions and `architecture-review-sweep`, applying the six focus areas above to each, and putting every candidate finding through the behaviour-preservation gate before it is filed.
3. **Report and close.** Post the run report on this issue, broken down per repo (scope counts, findings by severity AND by focus area F1–F6, the F6 upgrade-inventory table per repo, the ≤10 filed with links and the `[A<N>-<n>]` range consumed, deferred findings, findings dropped at the behaviour-preservation gate with the reason, enforcement PR links, anything skipped — a partial run is reported as partial, never as clean), then set this issue to `done` (never `in_review`). Do not wait on CI.