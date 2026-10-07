# Goal

Each month, run an architecture review of the drunk Pulumi IaC libraries across four dimensions — security-by-default, upstream provider drift, deprecation path, and Azure Well-Architected best practice — filing the highest-value findings into the `drunk-pulumi` backlog for human triage. This run issue IS the review: one agent task, no fan-out.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, role `owner`; never a hardcoded UUID). The findings you file are the deliverable for triage; the report on this issue is the index.
- **Project** — this run issue and every filed finding live in `drunk-pulumi` (id from `multica project list --output json`). Never cross-file into another project.
- **How** — your agent instructions already define the procedure: invoke `architecture-review-sweep` and follow it end to end PER REPO (checkout, CodeGraph index, scope/exclusions, shard, rank, dedupe, enforcement PR against that repo's `dev`, report), applying `pulumi-azure-iac-standards` as the rule catalogue. Read each repo's own `CLAUDE.md` / `AGENTS.md` FIRST — repo-local conventions override anything generic.
- **Inputs** — none; monthly schedule.

# Scope — every month, plus one rotating repo

Reviewing all five repos in one run does not fit. Review the two core repos every month, plus exactly ONE rotating repo chosen deterministically from the run month:

**Every month (core — nearly all the public surface):**
1. `drunk-pulumi-azure` — https://github.com/baoduy/drunk-pulumi-azure.git — the builders (`@drunk-pulumi/azure`); a bad default here is inherited by every downstream stack.
2. `drunk-pulumi-azure-components` — https://github.com/baoduy/drunk-pulumi-azure-components.git — the reusable `ComponentResource` wrappers.

**One rotating repo — pick by `(month number mod 3)` of the run date, so each is covered every quarter:**
- remainder `0` → `drunk-pulumi-azure-providers` — https://github.com/baoduy/drunk-pulumi-azure-providers.git
- remainder `1` → `drunk-pulumi-cloudflare-components` — https://github.com/baoduy/drunk-pulumi-cloudflare-components.git
- remainder `2` → `drunk-pulumi-intune-components` — https://github.com/baoduy/drunk-pulumi-intune-components.git

State in the report which rotating repo this run took and which two it deferred to later months. `drunk-pulumi-kubx` is OUT of scope until the owner adds it. Review no other repo.

# Review dimensions

All four are defined, with stable rule-ids, in the `pulumi-azure-iac-standards` skill under "Review dimensions". Load it and cite a rule-id on every finding. Summary of what each dimension is for:

1. **Security by default** (`PULUMI-SEC-001`…`PULUMI-SEC-010`) — the unsafe option must never be the default path. Transport hardening, identity over keys, public-access defaults, data-protection defaults, diagnostics, secret outputs, AKS hardening. Rank these `critical`/`high`, never below — these libraries are trusted blindly by every consumer that does not override.
2. **Upstream provider drift** (`PULUMI-UP-001`…`PULUMI-UP-005`) — pins behind latest stable, new upstream properties the wrapper never exposes, dated API-version imports, deprecated upstream surface still in use, hand-rolled wrappers now shipped upstream.
3. **Deprecation path** (`PULUMI-DEP-003`) — a public export is removed only through the two-release deprecation path.
4. **Azure Well-Architected** (`PULUMI-WAF-001`…`PULUMI-WAF-004`) — zone redundancy, SKU/cost knobs, governance tags, deletion guards on stateful resources.

The existing convention rules (`PULUMI-BLD-*`, `PULUMI-NAME-*`, `PULUMI-TYPE-*`, `PULUMI-PKG-*`, `PULUMI-TEST-*`) stay in force; a clear violation is still a valid finding.

# Hard constraints — this run recommends, it does not change production code

- **No version bumps.** Dimension 2 findings name the current pin, the latest stable, and what changed. Opening a dependency-bump PR is the `🚀 Monthly npm Upgrade — Pulumi repos` autopilot's job, not yours — even while that autopilot is paused. If it is paused, say so in the report so the owner knows drift findings have no automated bump path.
- **No deletion of public exports.** A published npm library's exported builder, component, or `*Info` field is a downstream install-time contract. Follow `PULUMI-DEP-003`: file step 1 (mark `@deprecated` + migration note, non-breaking) as a finding for human approval; step 2 (the actual delete) is a separate human-scheduled ticket that cuts a minor release, never a major one (`PULUMI-TEST-003`). Never open a PR that deletes an export.
- **Enforcement PRs are test-only / config-only**, target `dev`, both `--head` and `--base` explicit, ONE PR per repo and only where that repo has enforcement-worthy findings. Build, `tsc`, eslint and the mocha suite must be green locally before pushing. Never touch production source.

# Filing rules

- Findings are filed at `backlog`, children of this run issue (`--parent`), assigned to the human triager — the workspace owner resolved at runtime via `multica workspace member list --output json` (the entry with role `owner`), passed as `--assignee-id <that user_id>`, never `--assignee` (fuzzy name matching could silently bind the finding to the wrong person on an unattended run).
- Title: `[A<N>-<n>] [<RULE-ID>] <what and where>` where `N` is this run issue's number — ONE `[A<N>-<n>]` sequence shared across all repos in the run.
- Properties on every finding: `Arch fingerprint`, `Arch severity`, `Arch repo` (the repo short name, e.g. `drunk-pulumi-azure-components`) and `Owner`.
- **Cap: at most 10 findings filed TOTAL across all repos in the run** — rank globally after all sweeps finish, not 10 per repo. Everything above the cap goes in the report body only.
- Dedupe fingerprint: `<repo-short-name>:<rule-id>:<relative/path/File.ts>:<SymbolName>` — e.g. `drunk-pulumi-azure:PULUMI-SEC-006:src/Storage/StorageBuilder.ts:StorageBuilder`. Never re-file a finding that already has an open issue.
- A pattern repeated across every repo is worth more as ONE cross-repo finding than as three per-repo ones — say so explicitly and fingerprint it against the repo where the fix belongs.

# Quality bar

Prefer 5 findings someone will act on over 30 they will skim. Every finding answers: what is wrong, where exactly, what breaks downstream, what is the smallest fix. Never "consider refactoring for clarity". Uncertain is fine — say so in the issue; confidently wrong is not.

# Steps

1. **Set this issue to `in_progress`.** `multica issue status <this-issue-id> in_progress`.
2. **Review the two core repos plus this month's rotating repo** per your instructions and `architecture-review-sweep`, applying the four dimensions to each.
3. **Report and close.** Post the run report on this issue, broken down per repo — repos reviewed and rotating repos deferred, scope counts, findings by severity, the ≤10 filed with links and the `[A<N>-<n>]` range consumed, findings dropped by the cap, enforcement PR links, and anything skipped. A partial run is reported as partial, never as clean. Then set this issue to `done` (never `in_review`). Do not wait on CI.