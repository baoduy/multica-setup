# Goal

Each month, fan the architecture review out into ONE review sub-issue per Monxa .NET backend repo, let each repo review run as its own independent agent task, and roll the four results up into a single consolidated report on this run issue.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, entry with role `owner`; use its `user_id`, NEVER a hardcoded UUID). This run issue is the index and the roll-up. The per-repo `[RP#]` sub-issues carry the actual reviews; the enhancement issues they file are the deliverable for triage.
- **Scope** — four .NET 10 / EF Core 10 services on DKNet-based DDD. The `RP` number is FIXED per repo and must never be renumbered, so `[RP3]` always means payment-gateway:
  1. `RP1` — Auth API — https://github.com/the-wixo/monxa.auth-api.git
  2. `RP2` — Email Service — https://github.com/the-wixo/monxa.email-service.git
  3. `RP3` — Payment Gateway — https://github.com/the-wixo/monxa.payment-gateway.git
  4. `RP4` — Webhook Deliverer — https://github.com/the-wixo/monxa.web-hook-deliverer.git
- **Projects** — this run issue and the four `[RP#]` review sub-issues live in `mx-jobs` (`e301fbc6-2ee9-48bd-8587-d5626b6176f2`). Enhancement issues are filed into `mx-main` (`8008ea4e-76ce-4035-9824-8041e82d1b68`).
- **Constraints**
  - **This run reviews NO code.** It dispatches, then stops. Every checkout, every analysis, every filed finding happens inside the `[RP#]` sub-issue runs.
  - **`--status todo` is what starts a review.** An agent-assigned sub-issue created at `todo` enqueues its assignee immediately; `backlog` sets the assignee and fires nothing, which would park the whole review forever.
  - **Do NOT pass `--stage`.** All four sub-issues must sit in one implicit stage. The server then wakes the parent assignee EXACTLY ONCE — when the LAST sub-issue reaches a terminal status. That single wake is the only trigger for the roll-up in step 5; four separate stages would fragment it and park three of the four reviews.
  - **Do NOT close this run issue at dispatch.** It stays `in_progress` until all four reviews are terminal. The nightly issue-hygiene autopilot propagates a terminal parent status onto open children: closing this issue early flips all four `[RP#]` sub-issues to `done` overnight and the review silently never happens. `[RP#]` is NOT on the hygiene exemption list — an open parent is the only thing protecting the sub-issues.
  - **The `[A<N>-<n>]` prefix on filed findings is still mandatory** — it is the hygiene autopilot's exemption marker, and a finding without it WILL be flipped to `done` the next night. `N` is now the numeric part of the `[RP#]` REVIEW SUB-ISSUE's identifier (not this run issue's), and `n` restarts at 1 within each repo. Each repo review is its own run, so a counter continuing across repos is no longer possible.
  - A repo review that fails no longer costs the other three — each is a separate task. Report the failure in the roll-up anyway. If a sub-issue's run dies, the hourly stuck-run recovery autopilot revives it; do not build your own retry.
- **Inputs** — none; monthly schedule.

# Steps

1. **Set this issue to `in_progress`.** `multica issue status <this-issue-id> in_progress`.

2. **Write one description file per repo** inside your working directory (never `/tmp`, never a shared path). Each file is the ONLY context that repo's run receives, so it must be complete on its own and state:
   - the `RP` number, the repo URL, and that the review is scoped to THAT ONE repo;
   - invoke the `architecture-review-sweep` skill and follow it end to end; read that repo's own `CLAUDE.md` / `AGENTS.md` FIRST, because solution-local conventions override the generic ones and these services do not share conventions;
   - the review covers three dimensions, each with its rule catalogue, and every finding cites a catalogue rule-id:
     1. **.NET coding best practices** — the `dotnet10-efcore10-standards` skill (`NET10-LANG-*`, `EFC-*`, `ASP-*`, `ASYNC-*`, `LOG-*`); attribute language features to the correct C# version;
     2. **Conventions** — `dotnet10-efcore10-standards` `CLEAN-*`/`DOC-*` plus the `dknet-ddd-conventions` skill (`DKNET-*` aggregate, repository, event, and data-authorization rules); solution-local conventions win on conflict;
     3. **Security** — the dedicated pass below; these are payment-adjacent services, so security findings rank `critical`/`high`, never below;
   - run a security pass over every trust boundary (HTTP endpoints, message-bus handlers, webhook receivers, config), using these stable rule-ids:
     - `SEC-001` endpoint or handler reachable without authentication/authorization (`[Authorize]`/`RequireAuthorization` missing, or `AllowAnonymous` without a stated reason);
     - `SEC-002` secret in source or committed config — connection strings, API keys, signing keys in `appsettings*.json`; secrets must come from environment/key vault;
     - `SEC-003` unvalidated input at a trust boundary — request DTOs without validation, or over-posting (entities/domain types bound directly from requests);
     - `SEC-004` SQL or command built by concatenating user input — `FromSqlRaw`/`ExecuteSqlRaw` (extends `EFC-005`), Dapper, `Process.Start`;
     - `SEC-005` sensitive-data exposure — PAN, tokens, secrets, or full request bodies in logs, exception messages, or API responses (extends `LOG-002`);
     - `SEC-006` crypto misuse — homemade crypto, MD5/SHA1 in a security context, or non-constant-time comparison of signatures/tokens (use `CryptographicOperations.FixedTimeEquals`);
     - `SEC-007` inbound webhook accepted without signature verification, or a state-changing payment endpoint without idempotency protection;
     - `SEC-008` known-vulnerable dependencies — run `dotnet list package --vulnerable --include-transitive` and file one finding per critical/high advisory;
   - build the CodeGraph index (`codegraph init .`, then `codegraph status .` to confirm nodes/edges > 0) before analysing; fall back to Grep/Read and say so if indexing fails;
   - analyse every production `.cs` file; exclude all unit/BDD test projects, `obj/`, `bin/`, `Migrations/`, `GeneratedDtos/`, `*.g.cs`, `*.Designer.cs`;
   - dedupe against already-filed findings on the per-repo fingerprint `<repo-short-name>:<rule-id>:<relative/path/File.cs>:<SymbolName>` and never re-file something with an open issue;
   - file at most 10 enhancement issues, highest severity first, **as children of that `[RP#]` sub-issue** (`--parent <that-sub-issue-id>`) into `mx-main` at `backlog`, `--assignee-id <owner-user_id>` (the workspace owner resolved at runtime, per Audience — never `--assignee`, name matching is fuzzy, and never a hardcoded UUID), each titled `[A<sub-issue-number>-<n>] [<RULE-ID>] <what and where>`, with `arch_finding`, `arch_severity` and `arch_repo` metadata set. Everything above the cap goes in the report body only;
   - add architecture tests for mechanically-checkable rules (Tier 1 clean / Tier 2 baseline allow-list) and open ONE test-only PR against `dev` with both `--head` and `--base` explicit; never modify production code; build and tests green locally before pushing; leave `TEST_DB_PROVIDER` unset;
   - post the per-repo report on that sub-issue and set THAT SUB-ISSUE to `done` (never `in_review`);
   - do not touch this run issue and do not review any other repo.

3. **Create the four review sub-issues**, one `multica issue create` each, in `RP` order:
   ```
   multica issue create \
     --title "[RP1] Architecture Review — Auth API (<YYYY-MM>)" \
     --parent <this-issue-id> \
     --project e301fbc6-2ee9-48bd-8587-d5626b6176f2 \
     --assignee-id b10219fb-a1d5-417f-abe9-2f3fb486bb1b \
     --status todo \
     --priority medium \
     --description-file ./rp1.md
   ```
   Repeat for `RP2` Email Service, `RP3` Payment Gateway, `RP4` Webhook Deliverer. `<YYYY-MM>` is this run's month. No `--stage` on any of them. A create that fails is a repo not reviewed — retry it once, and if it still fails record it and carry on with the rest.

3a. **Label each review sub-issue `arch.review`.** `issue create` takes no label flag, so this is a second call per sub-issue, straight after its create returns:
   ```
   multica issue label add <sub-issue-id> e8412c72-f304-4a34-99e0-86987fd00a8e
   ```
   The command takes the label's UUID, NOT its name — `arch.review` is `e8412c72-f304-4a34-99e0-86987fd00a8e` and already exists workspace-wide, so never create it. If the id is ever rejected, resolve it with `multica label list --output json` and use the id for `arch.review`; never label a review issue with anything else. A missing label is a reporting gap, not a failed review — record it and carry on.

4. **Publish the index and stop.** Set metadata `arch_dispatch` on this issue to the four sub-issue identifiers, comma-separated (`multica issue metadata set <this-issue-id> --key arch_dispatch --value "MXW-xxx,MXW-xxx,MXW-xxx,MXW-xxx"`), then post ONE comment listing `RP number | repo | sub-issue link | status`. End the run here. Do not review code, do not wait for the sub-issues, and do NOT set this issue to `done`.

5. **Roll up — LATER, on the stage-complete wake.** When the server wakes you on this issue because all four sub-issues are terminal — the wake itself is the signal and may carry no comment; confirm with `multica issue children <this-issue-id> --output json` that every `[RP#]` is `done`/`cancelled` — read each sub-issue and the children it filed, then post ONE consolidated report:
   - per-repo scope counts and findings by severity;
   - issues filed, with links and the `[A<N>-<n>]` prefix range each repo consumed, so a gap or duplicate is visible at a glance;
   - findings deferred above the cap, PR links, tests added;
   - cross-service patterns called out ONCE rather than four times;
   - every repo whose review failed, filed nothing, or was skipped — stated explicitly. A partial run is reported as partial, never as clean.

   Then set this issue to `done`. Do not wait on CI.