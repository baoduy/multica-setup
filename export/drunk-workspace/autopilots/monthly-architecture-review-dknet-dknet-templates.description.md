# Goal

Each month, run a full architecture review of the DKNet framework repository AND the DKNet.Templates repository, filing the highest-value findings into the `drunk-net` backlog for human triage. This run issue IS the review — two repos, one agent task, no fan-out.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, role `owner`; never a hardcoded UUID). The enhancement issues you file are the deliverable for triage; the report on this issue is the index.
- **Scope** — TWO repos, each swept with the full procedure:
  1. `DKNet` — https://github.com/baoduy/DKNet.git. The framework library every DKNet-based service depends on (`DKNet.EfCore.*`, `DKNet.Svc.*`, `DKNet.Fw.*`) — a defect here compounds into every consumer.
  2. `DKNet.Templates` — https://github.com/baoduy/DKNet.Templates.git. The project templates new services are scaffolded from — a defect here is baked into every new service at day zero. The scaffolded template content (projects, config files) is in scope, not just the packaging code.
  Do NOT review any other repo in this run.
- **Project** — this run issue and every filed finding live in `drunk-net` (id from `multica project list --output json`). Never cross-file into another project.
- **How** — your agent instructions already define the procedure: invoke the `architecture-review-sweep` skill and follow it end to end PER REPO (checkout, CodeGraph index, scope/exclusions, shard, rank, dedupe, enforcement PR against that repo's `dev`, report). Read each repo's own `CLAUDE.md` / `AGENTS.md` FIRST — solution-local conventions override the generic rules.
- **Constraints**
  - Findings are filed at `backlog`, children of this run issue (`--parent`), `--assignee-id <triager user_id>` resolved at runtime as the workspace owner (`multica workspace member list --output json`, role `owner`; never a hardcoded UUID, never `--assignee` by name), titled `[A<N>-<n>] [<RULE-ID>] <what and where>` where `N` is this run issue's number — one `[A<N>-<n>]` sequence shared across both repos — with the `Arch fingerprint`, `Arch severity`, `Arch repo` and `Owner` properties set (`Arch repo` is `DKNet` or `DKNet.Templates`).
  - Cap: at most 10 findings filed TOTAL across both repos — rank globally after both sweeps, not 10 per repo.
  - Dedupe fingerprint: `<repo>:<rule-id>:<relative/path/File.cs>:<SymbolName>` where `<repo>` is `DKNet` or `DKNet.Templates`. Never re-file a finding with an open issue.
  - Enforcement PRs are test-only, target `dev`, both `--head` and `--base` explicit, ONE PR per repo and only where that repo has enforcement-worthy findings; build and tests green locally before pushing.
- **Inputs** — none; monthly schedule.

# Review dimensions

The review covers three dimensions, each with its rule catalogue, and every finding cites a catalogue rule-id:

1. **.NET coding best practices** — the `dotnet10-efcore10-standards` skill (`NET10-LANG-*`, `EFC-*`, `ASP-*`, `ASYNC-*`, `LOG-*`); attribute language features to the correct C# version.
2. **Conventions** — `dotnet10-efcore10-standards` `CLEAN-*`/`DOC-*` plus the `dknet-ddd-conventions` skill (`DKNET-*` rules — the DKNet repo DEFINES those contracts, so hold it to them hardest; DKNet.Templates must scaffold them correctly); solution-local conventions win on conflict.
3. **Security** — the dedicated pass below. DKNet ships encryption, data-authorization, and blob-storage packages that downstream services trust blindly, and DKNet.Templates stamps its defaults into every new service, so security findings rank `critical`/`high`, never below.

## Security pass — stable rule-ids

Run over every public API surface and trust boundary of each repo, using these stable rule-ids:

- `SEC-001` data-authorization gap — a row-level filter that can silently not apply (`IOwnedBy` marker missed, filter defined on a non-root type), or `IgnoreQueryFilters()` reachable without an explicit justification;
- `SEC-002` secret in source or committed config — connection strings, API keys, test credentials in `appsettings*.json` or test fixtures; secrets must come from environment/key vault. In DKNet.Templates, a real-looking secret stamped into scaffolded template content counts; an obvious placeholder does not;
- `SEC-003` unvalidated input at a public API boundary — public library entry points that pass caller input through to SQL, file paths, or blob keys without validation;
- `SEC-004` SQL or command built by concatenating input — `FromSqlRaw`/`ExecuteSqlRaw` (extends `EFC-005`), string-built SQL in `Relational.Helpers`, `Process.Start`;
- `SEC-005` sensitive-data exposure — keys, plaintext of encrypted fields, or full payloads in logs or exception messages (extends `LOG-002`); the `.Encryption` packages must never log what they protect;
- `SEC-006` crypto misuse — homemade crypto, MD5/SHA1 in a security context, ECB mode, static/reused IVs, keys held in strings, or non-constant-time comparison of MACs/tokens (use `CryptographicOperations.FixedTimeEquals`) — audit `DKNet.EfCore.Encryption` and `DKNet.Svc.Encryption` end to end;
- `SEC-007` insecure default — a public API whose default configuration is the unsafe option (encryption opt-in where it should be opt-out, authorization filter disabled unless configured, permissive fallback on missing config); in DKNet.Templates this includes unsafe defaults scaffolded into new services;
- `SEC-008` known-vulnerable dependencies — run `dotnet list package --vulnerable --include-transitive` and file one finding per critical/high advisory (fingerprint anchor: the `.csproj` path and package name).

# Steps

1. **Set this issue to `in_progress`.** `multica issue status <this-issue-id> in_progress`.
2. **Review both repos** per your instructions and `architecture-review-sweep`, applying the three dimensions above to each.
3. **Report and close.** Post the run report on this issue, broken down per repo (scope counts, findings by severity, the ≤10 filed with links and the `[A<N>-<n>]` range consumed, deferred findings, enforcement PR links, anything skipped — a partial run is reported as partial, never as clean), then set this issue to `done` (never `in_review`). Do not wait on CI.