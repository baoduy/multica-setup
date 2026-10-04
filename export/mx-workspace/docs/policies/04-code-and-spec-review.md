# Policy 04 — Code & Spec Review

| | |
|---|---|
| **Policy ID** | MX-POL-04 |
| **Version** | 1.9 |
| **Status** | Active |
| **Owner** | pr-reviewer (code) · spec-reviewer (spec) · arch-reviewer (sweeps) |
| **Applies to** | Every spec before implementation and every PR before merge |
| **Related skills** | [`pr-review-gate`](../../skills/pr-review-gate/SKILL.md) · [`spec-review-gate`](../../skills/spec-review-gate/SKILL.md) · [`architecture-review-sweep`](../../skills/architecture-review-sweep/SKILL.md) |
| **Enforced at** | the gates themselves (automated) |

> **Authority.** This policy is the source of truth for the two review gates.
> `spec-review-gate`, `pr-review-gate` and `architecture-review-sweep` **implement** it —
> their scores, thresholds and gate actions derive from it. Amend this policy first, then
> cascade — see [change control](00-policies-index.md#change-control).

## Review gates at a glance

```
   SPEC gate (spec-reviewer)                     PR gate (pr-reviewer)
   ┌───────────────────────────┐                ┌────────────────────────────┐
   │ score ≥ 9.0, 0 blockers    │──APPROVED──▶   │ score ≥ 8.5, 0 blocking,    │──APPROVED──▶ gate
   │  → implementation          │  [P#-1]        │  all merge preconds pass    │   MERGES into dev
   │ 8.0–8.9 / trigger          │                │ ≥ 8.5 but precond fails     │
   │  → requester holds [S#]    │                │  → APPROVAL DEFERRED (human)│
   │ < 8.0 / blocker → REWORK   │                │ < 8.5 / blocking → REWORK   │
   │  (max 5 rounds)            │                │  (max 3 rounds)             │
   └───────────────────────────┘                └────────────────────────────┘
        weights: coverage 25 · gherkin 20            phases: scope → security → correctness
        · clarity 20 · arch fit 15                   → testing → architecture & design
        · completeness 10 · sec 10                   → slop → style

   Rule: hard caps override arithmetic · every finding cites file:line · merge only what you gated.
```

## Purpose

Front-load quality at two gates — spec approval and PR merge — so defects are caught
before a dev cycle is wasted or before broken code reaches `dev`. Reviews are
evidence-based and scored, so approval is objective and the human is a bottleneck only
when a review genuinely needs them.

## Scope

Every Workflow B spec (spec gate) and every squad/devops PR into `dev` (PR gate). Plus
scheduled architecture sweeps that file backlog issues.

## Policy statements

1. **Evidence before opinion.** Every finding cites `file:line` from the actual diff (PR) or the spec section (spec). If you have not read the code, you may not have an opinion on it. Use CodeGraph to walk callers/callees beyond the diff before judging.
1a. **A PR-gate finding proves its failure, and a clean review is a valid review.** A correctness or security finding rated `blocking` or `important` names three things: the input or state that triggers it, the wrong outcome, and why the code's existing guards (a caller's validation, the framework, the type system, an existing test) do not stop it. A rule finding — a rubric cap, a stack rule-id, a §3b line, a test-strength rule, statement 4a — cites its rule instead. A finding that can do neither is demoted to `nit` or dropped. A review with no finding above `nit` is a valid result: a finding is never raised, and a severity never inflated, to make a review look thorough. `references/scoring-rubric.md` lists the false positives the gate does not raise.
2. **Score, then gate.** Both gates produce a 1–10 weighted score plus a verdict. **Hard caps override arithmetic** — a blocking finding never loses to a good average. **Every report renders the full scorecard table (below) — for a PASS and a BLOCKED verdict alike** (see statement 11 and the Scoring section).
3. **Spec gate (`spec-reviewer`):** weighted rubric — Requirement coverage & traceability 25% · Gherkin quality 20% · Business clarity 20% · Architecture fit 15% · Completeness & unambiguity 10% · Security 10%. **APPROVED** at score **≥ 9.0** with zero blockers and no reviewer trigger → straight to implementation; **8.0–8.9** or a trigger → the requester holds the `[S#]` sub-task; **< 8.0** or a blocker → REWORK (max 5 rounds, then manual review). The gate confirms §4 Scope names real repos/services and that §2 Current State and §3 invariants hold against real code — a Scope naming something that does not exist, or a §2/§3/§3b claim the code contradicts, is a **blocker**. The gate scores **Architecture fit** on §3b ([Policy 06](06-requirements-and-spec.md) statement 3c): whether the owner, dependency directions and public-surface calls fit each Scope repo's own `CLAUDE.md`/`AGENTS.md` and the platform's dependency rules — no cycle between services, a shared package never depending on a service — at the level of repos, services and bounded contexts. Whether the change reuses the right helper, mirrors the right pattern or puts logic in the right layer inside a service is dev-leader's call at decomposition and pr-reviewer's at the merge gate — the spec gate never re-opens that.
3a. **A spec-gate finding names its consequence, and a clean spec is a valid result.** A `blocker` or `major` finding names its section and what goes wrong downstream: what dev-team would build wrong, which §5 scenario cannot be written or checked, or which question the implementer is left to guess. A §2, §3 or §3b claim the code contradicts cites the CodeGraph `file:line` in the finding (never in the spec). A format-gate or template finding cites the rule it breaks instead. A finding that can do neither is `minor`, `nit` or dropped. The proof decides whether a finding exists, never which of two severities it takes: a proven finding torn between `major` and `blocker` is still a `blocker`. A spec with no finding above `minor` is a valid result; a finding is never raised to make a review look thorough. `spec-review-gate` lists the false positives the gate does not raise (statement 9 among them).
4. **PR gate (`pr-reviewer`):** four-phase .NET 10 analysis — Scope (built right *and* the right thing; base MUST be `dev`; walk the impl-brief's Change set row-by-row) → Security first → Correctness → Testing → Architecture & design → AI-slop → Style. **Architecture & design reviews the code's architecture, not only its tidiness:** a diff that contradicts an approved spec §3b line ([Policy 06](06-requirements-and-spec.md) statement 3c) — behaviour or data in a repo or bounded context §3b did not name as owner, a dependency that reverses the declared direction or creates a cycle between services or projects, a public-surface break §3b declared `additive` or `none` — is `blocking`; a new violation of the stack skill's layering or boundary rules ([Policy 01](01-coding-standards-dotnet.md) statement 2 — `DKNET-LAYER-001..004`, `DKNET-AGG-004`, `DKNET-REPO-004`) in code the diff touched, or a new dependency or interaction between repos or services §3b never declared, is `important`, as is a dev-backend Build whose Standards self-review row the diff contradicts ([Policy 01](01-coding-standards-dotnet.md) statement 17). **A self-review EVIDENCE row that is missing or carries no measured value is a `nit`:** the gate measures that point itself and scores what it finds; a row the diff or CI contradicts is `important`, and no mutation evidence at all keeps its own 7.9 cap. This never excuses the coverage number itself, which stays governed by the auto-merge coverage precondition and its own cap. The gate judges the diff against §3b and never re-decides §3b itself (statement 9); a Workflow A bug PR has no spec and is checked against the layering rules only. A `bug-build` Build ([Policy 02](02-testing-and-quality.md) statement 1a) has no separate Acceptance-tests sub-task to check: the gate instead confirms `at_sha` is the Build's own first commit, holds only the reproduction test and stubs, is red for the reason product-owner's root-cause report names, and predates every fix commit — a mismatch is `blocking` (`references/scoring-rubric.md`). **APPROVED** at score **≥ 8.5 AND** every auto-merge precondition passes → the gate merges into `dev` itself; **≥ 8.5 but a precondition fails** → APPROVAL DEFERRED, manual handoff; **< 8.5 or any blocking finding** → REWORK (max 3 rounds, then escalate).
4a. **A PR never loosens the checks that judge it.** The gate reads `.pr-review.json` from `dev` on GitHub, never from the PR head. In the diff, a new suppression without a reason on its own line or the line above is `important`: `#pragma warning disable`, `[SuppressMessage]`, `<NoWarn>`, `[ExcludeFromCodeCoverage]`, `eslint-disable`, `@ts-ignore`, `@ts-expect-error`, `# noqa`, `# type: ignore`. A change that loosens a repo-wide check is `blocking` unless the cycle ticket asks for that change: an analyzer, lint or formatter rule disabled or lowered in severity (`.editorconfig`, `Directory.Build.props` `TreatWarningsAsErrors` / `AnalysisLevel` / `NoWarn`, lint configs); a coverage or mutation threshold lowered (`.pr-review.json`, Stryker `thresholds`, Coverlet or Codecov targets); a CI step deleted, skipped (`if: false`) or made non-failing (`continue-on-error: true`). A devops PR whose ticket names the change is the asked-for case. Why: an agent that cannot make a check pass is tempted to change the check, and the gate scores whatever the PR head's configuration says.
5. **Merge only what you just gated.** The only permitted merge is `gh pr merge` on the PR scored APPROVED in this run. Never `--admin`/force, never enable auto-merge, never push commits, never merge a helm PR (merging a chart *is* the deploy).
6. **Findings become Multica sub-issues, never GitHub issues — and only a squad LEADER files them.** A gate is a squad member: it reports its findings on its own gate sub-issue in filable shape, wakes the leader with its handoff line on the parent ([Policy 05](05-sdlc-delivery-lifecycle.md) statement 5), and creates nothing. The leader reviews, **consolidates** (findings from several members, or several rounds sharing a root cause, become ONE issue) and files ONE fix sub-issue, cited under the same `DKNET-*` / `NET10-*` rule-ids the developer fixes under. **A leader-filed issue raised from a report is created UNASSIGNED**: `Suggested owner:` names the intended author-role (dev-backend / qc-tester / devops), its `Owner` property is set, and it is handed to the resolved human owner by member mention — the owner reviews it and assigns it, and that assignment starts the work.
7. **Scope decides where a finding goes; impact decides its severity.** A finding is **in-scope** when its `file:line` is in a file the cycle's diff touched, in a path the diff newly reaches, or a missing test for behaviour the diff changed — *who introduced it is irrelevant*. In-scope findings never leave the cycle and never become tickets, and the score alone decides what they cost: below 8.5 or any `blocking` → a rework round; at 8.5 or above the PR merges, its open in-scope `nit`s and its one permitted `important` named in the report under `Merged with:` and dropped. There is no polish round (retired): a passing PR never goes back for findings the caps already let through. Out-of-scope findings (a file the diff never touched) are recorded with `file:line`, never move the score, and are **dropped** unless they clear the worth-fixing bar — a defect (wrong behaviour, emitted source that does not compile, data exposure, crash, published-API break) or a security finding, with the observable failure AND its reproduction named — in which case the squad leader files ONE ordinary defect ticket (never `Review follow-ups:`), unassigned, `Owner` set, folded into any open ticket sharing the root cause. Severity never softens because a defect is pre-existing: "not introduced by this PR" decides whose cycle fixes it, not whether it is a defect. Remaining debt is the monthly sweep's, not filed ad hoc.
8. **Include at least one `praise` finding when deserved** — review is calibration, not attrition.
9. **Reviewers do not design.** The spec gate scores *what* is reused/modified/new and *where* the change sits between repos and services (§3b), never *how* to build it inside one (dev-leader's call). The PR gate checks the code against that placement and does not re-open settled spec decisions.
10. **Architecture sweeps** run on a schedule: analyse → rank → **dedupe against already-filed issues** (the one step that makes it useful, never skipped) → file ≤10 survivors → convert mechanically-checkable rules into permanent architecture tests → report coverage (what was and wasn't scanned).
11. **Every report displays the scorecard — always.** The category × weight × score table (see Scoring) appears in every review report and every posted verdict comment, in **both** the PASS state (APPROVED / APPROVAL DEFERRED / REVIEW REQUESTED) and the BLOCKED state (REWORK / escalated / manual handoff). A verdict posted without the full scorecard is non-compliant, regardless of outcome — the score is the audit record and must be legible whether the change advanced or was sent back.

## Scoring

Both gates score **each category 1–10**, compute the weighted average, then apply hard caps
(a blocking finding can never be averaged away). Report the final score to one decimal;
when torn between two scores, take the lower and say why. The scorecard is rendered in every
report per statement 11.

### PR review scorecard (`pr-reviewer`)

| Category | Weight | Score |
|---|---|---|
| Correctness & logic | 25% | _n.n_ |
| Security | 20% | _n.n_ |
| Testing & coverage | 20% | _n.n_ |
| Architecture & design | 15% | _n.n_ |
| Spec conformance | 10% | _n.n_ |
| Style & conventions | 5% | _n.n_ |
| AI-slop gate | 5% | _n.n_ |
| **Weighted total** | **100%** | **_X.X / 10_** |

**Worked example** — exactly how a report renders a BLOCKED verdict (the table shows on a fail, too):

| Category | Weight | Score |
|---|---|---|
| Correctness | 25% | 9.5 |
| Security | 20% | 10.0 |
| Testing | 20% | 4.5 |
| Architecture & design | 15% | 9.0 |
| Spec conformance | 10% | 8.0 |
| Style | 5% | 9.5 |
| AI-slop | 5% | 8.5 |
| **Weighted total** | **100%** | **8.3** |

Weighted average is 8.3, but the testing/coverage gap trips the **coverage-below-threshold hard cap (7.9 max)** → final **7.9 → BLOCKED (REWORK)**. The scorecard is posted with the REWORK comment regardless.

**Category scoring:** start each at 10 and deduct — `blocking` −4, `important` −2, `nit` −0.5 (max −1.5), `suggestion`/`praise` 0; floor at 1.

**Hard caps (applied after the weighted average):** any `blocking` finding → 6.9 max · any critical security finding (exploitable / secret / authz bypass) → 3.0 max · two or more open `important` findings anywhere → 8.4 max · no tests for new/changed behaviour → 6.5 max · a check loosened without the ticket asking for it (statement 4a) → 6.9 max · a `bug-build` whose `at_sha` holds more than the reproduction and stubs, is green, postdates a fix commit or misses the root-cause report's reproduction conditions ([Policy 02](02-testing-and-quality.md) statement 1a) → 6.9 max · CI failing → 6.9 max · coverage on changed lines below threshold (default 80%) → 7.9 max · docs/comment/typo-only PR with green CI → 9.0 floor (fast path; caps beat the floor).

**Gate:** **≥ 8.5 → APPROVED** (or APPROVAL DEFERRED if a merge precondition fails); **< 8.5 → REWORK**. No human-review middle band.

### Spec review scorecard (`spec-reviewer`)

| Category | Weight | Score |
|---|---|---|
| Requirement coverage & traceability | 25% | _n.n_ |
| Gherkin quality | 20% | _n.n_ |
| Business clarity & problem framing | 20% | _n.n_ |
| Architecture fit | 15% | _n.n_ |
| Completeness & unambiguity | 10% | _n.n_ |
| Security considerations | 10% | _n.n_ |
| **Weighted total** | **100%** | **_X.X / 10_** |

**Gate:** **≥ 9.0** with zero blockers → APPROVED; **8.0–8.9** or a reviewer trigger → REVIEW REQUESTED (requester holds `[S#]`); **< 8.0** or any blocker → REWORK (max 5 rounds). A well-formed BDD waiver is never a finding and costs zero points.

## Best practices for .NET developers (receiving a review)

- Read the rule-id, fix under the same id; if you disagree, reply on the finding with evidence — don't silently ignore it.
- REWORK re-enters at Build and **always re-runs Verify** before the gate is re-armed. Every hop is routed by the squad leader (gate → leader → implementer → leader → gate); a re-trigger flips the sub-task `in_progress --no-start` before the mention, and the Fix carries `Retrigger on done` naming every gate to re-arm (comma-separated keys when there are several).
- A `DKNET-REPO-006` (redundant `UpdateAsync`) is delete-on-sight, not a discussion — check the read for `AsNoTracking()` and remove the call.
- Keep PRs under ~3,000 changed lines; larger PRs are never auto-approved and get reviewed file-by-file with security-sensitive files first.

## Definition of Done / compliance

- **Spec:** score ≥ 9.0, zero blockers, all seven sections present and well-formed (§3a carries the field and endpoint contract, §3b the architecture placement), §4 Scope complete and grounded against code.
- **PR:** score ≥ 8.5, zero blocking findings, no check loosened without the ticket asking for it (statement 4a), the diff consistent with the spec's §3b placement and the stack's layering rules, all auto-merge preconditions pass, merged into `dev` by the gate.

## Enforcement

The gates are the enforcement — fully autonomous in pipeline mode. Manual handoff goes
to the ROOT ticket creator (owner as fallback) via **reassignment at `todo`**, never a
bare mention. On-demand mode (a human mention) is report-only: no GitHub writes, no
tickets, unless explicitly instructed.

## Exceptions & waivers

- A well-formed **BDD integration waiver** is never a spec-gate finding and costs zero points (see [Policy 02](02-testing-and-quality.md)) — only the requester decides it; the reviewer may add one non-scoring risk note on a money/identity path.
- Self-authored PRs: GitHub rejects the vote; the gate falls back to plain comments and notes the skipped vote — the Multica report is the audit record and the merge still proceeds.
- Round caps: spec 5, PR 3 — then the human takes over via a reassigned review sub-task.

## References

- [`spec-review-gate`](../../skills/spec-review-gate/SKILL.md) — weights, severities, calibration, gate mechanics.
- [`pr-review-gate`](../../skills/pr-review-gate/SKILL.md) — four-phase analysis, scoring rubric, gate actions, merge preconditions.
- [`architecture-review-sweep`](../../skills/architecture-review-sweep/SKILL.md) — shard/rank/dedupe/file/enforce sweep.
- Rule catalogs: [Policy 01](01-coding-standards-dotnet.md). Spec contract: [Policy 06](06-requirements-and-spec.md).
