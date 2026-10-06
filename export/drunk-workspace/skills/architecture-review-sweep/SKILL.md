---
name: architecture-review-sweep
description: End-to-end workflow for recurring architecture review of .NET solution — shard codebase across parallel analyzers, rank findings by severity, dedupe against already-filed issues, file survivors into project backlog, and convert mechanically-checkable rules into permanent architecture tests. Use when running scheduled or on-demand architecture/code-quality review that outputs Multica issues.
---

# Architecture Review Sweep

One run = **analyse → rank → dedupe → file ≤10 issues → enforce what can be enforced → report**.

This runs on schedule. Single thing that makes it useful rather than spam is **step 4, dedupe**. Never skip it.

## 0. Preconditions

```bash
multica repo checkout <repo-url>          # creates agent/<name>/<runtime> branch
```

Read repo's own `CLAUDE.md` / `AGENTS.md` first — solution-local conventions **override** generic rules in reference skills. Consult `dknet-ddd-conventions` and `dotnet10-efcore10-standards` for rule catalogue.

### Build CodeGraph index first

Per `codegraph` skill: fresh checkout never has usable index — run `codegraph init --yes .` once per run per repo, in the foreground, confirm nodes/edges > 0 via `codegraph status .`, then prefer `codegraph explore`/`callers`/`node` over grep/Read for anything structural. `explore`'s per-symbol "no covering tests found" weights severity: untested symbol with real defect ranks above tested one. If `codegraph init` fails, say so in report and fall back to Grep/Read — never silently degrade; layering and dead-code findings are much weaker without call-graph data.

## 1. Scope file set

Production source for the repo's stack only. Exclude tests, build output, generated and vendored code:

| Stack | Include | Exclude |
|---|---|---|
| .NET | `.cs` under the solution | test projects (`*.UnitTests`, `*.BDDTests`, `*Tests.csproj`), `obj/`, `bin/`, `Migrations/`, `GeneratedDtos/`, `*.g.cs`, `*.Designer.cs` |
| TypeScript / Pulumi | `src/**/*.ts` | `node_modules/`, `bin/`, `*.d.ts`, `*.test.ts`, `*.spec.ts`, `*.ts.ignore`, sample files |
| Python | `src/**/*.py` | `tests/`, `.venv/`, generated stubs |
| Docker | `Dockerfile`(s), `.dockerignore`, compose files | — |
| Helm | `Chart.yaml`, `values.yaml`, `templates/**` | `tests/` — read for coverage, never scanned for findings |

Record counts in report — reviewers need to know what was and wasn't covered.

## 2. Shard and analyse in parallel

Shard **by feature slice**, not by file count — slice keeps aggregate, its handlers, its specs and its EF config together, which is what most rules need to see at once.

Give every analyzer same rule catalogue and require it to return, per finding:

```
rule_id | severity | file:line | symbol | evidence (2-4 lines of real code) | why it matters | suggested fix | enforceable?
```

Reject findings with no `file:line` or no code evidence. Finding you cannot point at is guess.

Also run these whole-codebase passes, which sharding cannot see:
- **Duplication (DRY)** — near-identical method bodies across slices
- **Dead code** — public types/members with no inbound reference
- **Layering** — project reference graph vs. intended onion
- **Consistency** — same concept solved two ways in different slices (name newer/more-tested one as winner and flag other for cleanup; do not average them)
- **Reinvented wheel** — hand-rolled code a mature, actively-maintained package for that stack (NuGet / npm / PyPI) — or the stdlib — already provides. Only file when the hand-rolled block is non-trivial (retry/backoff, date/time math, validation, crypto, parsing) AND the package is well-established and license-compatible — adopting it must cut code **and** risk. Never recommend adding a dependency to save a few lines: that trades a supply-chain surface for nothing. Name the exact package and why it is a net win. Use the stack rule where one exists (.NET `CLEAN-LESS-004` for the in-box case, TS `TS-PKG-002/003`, Pulumi `PULUMI-TYPE-003`); else `REUSE-001`.
- **Modernization** — code that a language/framework/runtime feature *already available in the repo's current target* would collapse to less code. Cite the version (flagging a feature the target predates is the fastest way to lose credibility). Use that stack's feature catalogue (.NET `NET10-LANG-*` + EF/ASP rules) where a rule fits; else `MODERNIZE-001`. A framework/runtime **version bump is itself NOT a finding here** — flag only what an already-available feature simplifies. Mostly Tier 3 (judgement) — backlog, no faked test.

## 3. Rank

| Severity | Meaning |
|---|---|
| `critical` | Correctness, data-integrity, security, or money-handling defect |
| `high` | Architectural violation that will compound (layering breach, tenant filter gap) |
| `medium` | DRY/SOLID violation, oversized unit, missing abstraction |
| `low` | Naming, organisation, cosmetics |

Rank by severity, then by blast radius (how many call sites), then by fix cost ascending.

## 4. Dedupe — mandatory

Every filed issue is titled `[A<N>-<n>] [<RULE-ID>] <short target> — <one-line problem>` (see §5 for `[A<N>-<n>]` prefix) and carries the custom property `Arch fingerprint` = `<fingerprint>`, where

```
fingerprint = <repo-short-name>:<rule-id>:<relative/path/File.cs>:<SymbolName>
```

Line numbers are deliberately **not** in fingerprint — they drift on every unrelated edit and would defeat matching.

**Repo prefix is mandatory** when run covers more than one repository. Without it, same rule hitting same relative path in two services collides and you silently skip real finding. Also set the `Arch repo` property so findings can be filtered per repo.

**Cheap first pass** — build seen-set from titles, one page of 100 at a time (the CLI rejects `--limit` above 100):

```bash
multica issue list --project <project-id> --limit 100 --offset 0 --fields identifier,title,status --output json
```

Repeat with `--offset 100`, `200`, … while the response's `has_more` is `true`. Stopping at the first page misses older findings and files duplicates.

**Precise confirmation** — only for survivors that made cut:

```bash
multica issue list --project <project-id> --property "Arch fingerprint=<fingerprint>" --output json
```

Then:
- **Match on open issue** → skip. Do not comment, do not bump.
- **Match on `done`/`cancelled` issue but violation is back** → file fresh, and link old one in body as regression.
- **No match** → new finding, eligible to file.

## 5. File — hard cap 10 per run

File at most **10 new issues per run**, highest severity first. Everything that didn't make cut goes in run report body only, so nothing is lost and backlog stays readable.

### Parent link and `[A<N>-<n>]` prefix — both mandatory

Every filed finding is **child of run issue** (`--parent <run-issue-id>`) and its title starts with `[A<N>-<n>]`:

- `A` — architecture. Identifies sweep that produced finding.
- `N` — **run issue's own number**, numeric part of its identifier (`DRN-912` → `912`). Not child's number, which does not exist yet at title time.
- `n` — counter starting at **1**, incrementing in filing order (severity descending). When one run sweeps several repos counter **continues across them** — it is run-scoped, never repo-scoped, so `[A912-11]` may be first issue of repo 2.

Finding filed in run `DRN-912` therefore reads:

```
[A912-1] [DKNET-AGG-002] Merchant.Status — public setter bypasses state-transition rules
```

Keep rule-id bracket. Cheap dedupe pass in §4 builds its seen-set from titles, so dropping rule-id re-files everything next run.

Two reasons prefix is load-bearing, not decoration:

1. It makes review's whole output greppable and orderable as one batch (`A912-*`), same way delivery squads use `[D763-4]` / `[T586-2]`.
2. Weekly issue-hygiene autopilot exempts issues matching `^\[A\d+-\d+\]` from terminal-parent status inheritance. Without prefix, `backlog` finding parented to run issue that ends `done` gets flipped to `done` next night and finding is lost. **Malformed prefix silently destroys finding.** Self-check every title against `^\[A[0-9]+-[0-9]+\] ` before you move on.

```bash
multica issue create \
  --title "[A912-1] [DKNET-AGG-002] Merchant.Status — public setter bypasses state-transition rules" \
  --description-file ./finding.md \
  --project <project-id> \
  --status backlog \
  --priority <high|medium|low> \
  --assignee-id <triager-user-id> \
  --parent <run-issue-id>
multica issue property set <new-id> --name "Arch fingerprint" --value "<fingerprint>"
multica issue property set <new-id> --name "Arch severity" --value "<severity>"
multica issue property set <new-id> --name "Arch repo" --value "<repo-short-name>"
multica issue property set <new-id> --name Owner --value "<triager>"
```

Write description files **inside working directory** (`./finding.md`), never `/tmp` — CLI rejects outside paths.

Issues are filed at `backlog` **assigned to human triager** named in your agent instructions — never to delivery squad (`dev-team`), never to yourself. Triager decides what gets promoted and who does it.

Always use `--assignee-id <uuid>`, never `--assignee <name>`: name matching is fuzzy, and on unattended scheduled run near-miss would silently hand findings to wrong person.

Description template — implements shared `bug-report` contract (that skill's three sections and rules apply); Problem, Why it matters, Enforcement and rule footer are sweep-specific extras:

```markdown
## Problem
<what is wrong, one paragraph>

## Where
`src/Path/To/File.cs:120` · repo `<repo-short-name>`

## Evidence
```csharp
<the actual offending code>
```

## Why it matters
<concrete consequence — bug that becomes possible, change that becomes expensive>

## Scope
- **Impacted feature**: <library capability/consumer-facing behaviour this weakens — e.g. "EF repository pattern", "Pulumi VNet component" — not class name>
- **Repo**: `<repo-short-name>` (+ any other repo/package fix touches, incl. downstream consumers of published package)
- **Blast radius**: <public API/consumers affected if left unfixed, one line>

## Proposed solution
<smallest change that resolves it — you read code, so state it plainly; prefix `HYPOTHESIS:` only when unverified>

## Suggested owner
<dev-team (library/test code, default) · devops (workflow/pipeline/publish, Helm chart) — one line of reasoning derived from Scope; triager decides, this is routing hint>

## Enforcement
<one of: architecture test added in PR #N | baseline test added, this file is on allow-list | judgement call, not mechanically checkable>

---
rule: `<RULE-ID>` · severity: `<severity>` · fingerprint: `<fingerprint>`
```

## 6. Enforce what can be enforced

Rule that stays prose gets re-violated. Rule that becomes test never does. Classify every rule into one of three tiers:

**Tier 1 — clean, auto-enforce.** Mechanically checkable and codebase *currently passes*. Add architecture test now; it locks in good state.

**Tier 2 — baseline-enforce.** Mechanically checkable but there are existing violations. Add test **with explicit `KnownViolations` allow-list containing exactly today's offenders**. Test fails moment *new* violation appears, while existing ones stay green. Every backlog issue that gets fixed deletes one entry. Allow-list must only shrink — say so in comment on field.

**Tier 3 — judgement.** Not mechanically checkable (naming quality, whether abstraction earns its keep). Backlog issue only. Do not fake test for it.

Never add Tier-1 test that fails on today's code — that turns review into broken build.

Match existing test style exactly — **discover it per repo**, never carry it over from another repo. Read that repo's own test project before writing anything. In `DKNet`, for example, that means: `Architecture/` folder under relevant `*.Tests` project, `public sealed class <Rule>ArchitectureTests`, xUnit `[Fact]`, reflection over `typeof(...).Assembly` for assemblies under test, Shouldly assertions whose failure message names offenders and explains *why* rule exists.

```csharp
failing.ShouldBeEmpty(
    "Entities must not expose public setters — state changes go through intention-revealing " +
    "methods so invariants hold. Offenders: " + string.Join(", ", failing));
```

Message must say *why*, not just *what*. Test whose failure text doesn't explain intent gets deleted by next person it blocks.

### Enforcement PR

Test-only. **Never** touch production code in this PR.

```bash
cd src && dotnet build <Solution>.slnx -c Release              # analyzers are errors
dotnet test <path/to/Project.Tests.csproj>                      # must be green
git push origin HEAD:refs/heads/<feature-branch>
gh pr create --head <feature-branch> --base dev --title "[<ISSUE-KEY>] ..." --body-file <path>   # body: sdlc-gitflow **PR body**
```

Branch and PR mechanics follow `sdlc-gitflow` skill — **always pass both `--head` and `--base dev` explicitly**; without `--base`, `gh` silently targets production branch. Verify `baseRefName`/`headRefName` and non-empty diff before reporting done.

Max ~5 new tests per run. Both build and test must pass locally before pushing — red PR is worse than no PR. Link PR from run report.

Then stop. Report PR link and fact that CI is running; do **not** wait for CI or poll it.

## 7. Report

Post to parent run-issue: scope counts (files analysed / excluded), findings by severity, ≤10 filed (with links), everything deferred, enforcement PR link, and tests added by tier. State `[A<N>-<n>]` range consumed (e.g. `A912-1 .. A912-17`) — gap or repeat in that range means title went out malformed.

**State what was skipped.** If slice failed to analyse, if cap dropped 30 findings, if shard timed out — say so explicitly. Silent truncation reads as "clean codebase" when it isn't.

## Anti-patterns

- Filing finding with no `--parent` run-issue link, or with missing/malformed `[A<N>-<n>]` prefix
- Re-filing finding that already has open issue
- Findings without `file:line` and real code evidence
- Tier-1 test that fails on existing code
- Touching production code in enforcement PR
- "Consider refactoring for clarity" — vague findings with no concrete fix
- Reporting clean run when shards errored out
- Waiting on CI after opening PR