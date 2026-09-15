# Policy 06 — Requirements & Specification

| | |
|---|---|
| **Policy ID** | MX-POL-06 |
| **Version** | 2.0 |
| **Status** | Active |
| **Owner** | product-owner (spec) · dev-leader (implementation brief) |
| **Applies to** | Every feature spec and every dev sub-task brief |
| **Related skills** | [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) · [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) · [`interview-me`](../../skills/interview-me/SKILL.md) |
| **Enforced at** | spec review gate ([`spec-review-gate`](../../skills/spec-review-gate/SKILL.md)) |

> **Authority.** This policy is the source of truth for what a spec/brief contains.
> `sdlc-spec-template` and `sdlc-impl-brief` **implement** it — the section list, the
> format rules, and the §5 QC-Scope preamble derive from it. Amend this policy first, then
> cascade — see [change control](00-policies-index.md#change-control).

## Requirement cascade at a glance

```
   product-owner (WHAT & WHY)                              dev-leader (HOW)
   ┌──────────────────────────────┐                       ┌──────────────────────────┐
   │ SPEC (main ticket) — 5 §§     │                       │ IMPL BRIEF (dev sub-task)│
   │ §1 Goals   §2 Current State   │   business-level,      │ Goal · Current state ·   │
   │ §3 Expected State (+Security) │   NO code/paths ─────▶ │ Change set (KEEP/MODIFY/ │
   │ §4 Scope   §5 Gherkin (@unit/ │   the reuse/add call   │ EXTEND/NEW/REMOVE) —     │
   │   @integration) + QC preamble │   is the dev-leader's  │ REUSE binding, NEW ceil. │
   └──────────────────────────────┘                       └────────────┬─────────────┘
                                                                       ▼
   §1–§4 = business prose, NO code/class/paths/line-numbers.    IMPLEMENTATION (code)
   §5 Gherkin is the only fenced block.               verified vs the brief at the PR gate (Policy 04)
```

## Purpose

A spec exists to convey the **problem and the required behaviour** so a squad can build
the right thing. This policy fixes what a spec contains and where the boundary between
"what" (product-owner) and "how" (dev-leader) sits. The class-level reuse-vs-rebuild call
— what stops the squad rebuilding what already exists — is code-level and lives one layer
down, in the dev-leader's implementation brief.

## Scope

Feature specs on `mx-main` main tickets (the requester-approved, gate-scored artifact) and
the implementation briefs dev-leader writes into `mx-code` sub-tasks. Bugs use a root-cause
report instead of a spec unless the requester asks for one (see [Policy 07](07-bug-and-defect-management.md)).

## Policy statements

1. **Role boundary.** product-owner states the problem and the required behaviour. **dev-leader designs the implementation and decomposes it** into an impl-brief. A spec that reads like a recipe buries the problem and forecloses better designs. The class- and method-level reuse/modify/add decision is the dev-leader's, made in the impl-brief's Change set, never in the spec.
2. **The five sections, in order:** 1 Goals · 2 Current State · 3 Expected State (ending in one Security line) · 4 Scope · 5 Acceptance Criteria (the QC-Scope preamble, then Gherkin with every scenario tagged `@integration` or `@unit`). Each is done when it answers its question — **no word budgets**, length scales with the requirement.
3. **§1–§4 are business prose.** No code, no class names, no method signatures, no file paths, no line numbers. A code snippet next to a sentence lets the spec contradict itself — the squad implements the snippet. The **only** fenced block is the §5 Gherkin.
4. **Goals (§1) is the section the spec exists for** — name who is hurt, what it costs, why now, the affected role, and the observable signal the change worked, in language a non-engineer could act on. A thin or missing §1 is a spec-gate **blocker**.
5. **Invariants live in Expected State (§3)**, stated as the property that must hold ("a payout must never fail because of a notification"), never as the code that holds it. §3 ends with one **Security line**: the trust boundary in business terms, or "No new attack surface" with reasoning; payments idempotency/replay where relevant.
6. **No `file:line`, symbol, or Change Map in the spec.** The reuse/modify/add decision — one call per class/method touched — is the dev-leader's, made in the impl-brief's Change set (`KEEP`/`MODIFY`/`EXTEND`/`NEW`/`REMOVE`) from CodeGraph research, ordered REUSE-first so what already exists is read first. A `NEW` row is valid only after searching for something to reuse and finding nothing; a new entity/table/migration is its own `NEW` row or it is out of scope.
7. **§5 Acceptance Criteria** opens with the two-line QC-Scope preamble, then BRIEF-compliant Gherkin. Every scenario is tagged `@integration` or `@unit`; the tag plus the preamble is the whole test-scope statement.
8. **QC Scope (§5 preamble)** is exactly one `Ships this cycle:` line and one `BDD integration tests: required` / `... : waived — <reason> (basis: <requester | product-owner judgment | repo note>, <date>)` line, agreeing with the `ship_required`/`bdd_required` metadata and with each other. The BDD-integration waiver, and any SANDBOX-suite waiver on the money/identity path (`monxa.payment-gateway`, `monxa.auth-api`), is the requester's decision — product-owner may never waive those on its own judgment.
9. **Clarify to zero open questions before writing** — never ask what the code answers; use [`interview-me`](../../skills/interview-me/SKILL.md) to structure the intake. §4 Scope carries zero unresolved questions.
10. **Implementation brief (`sdlc-impl-brief`) is the layer below the spec** — dev-leader's translation into a task list against real code (Goal · Current state · Change set · delta markers KEEP/MODIFY/EXTEND/NEW/REMOVE). It carries the code-level detail the spec omits, never restates the business spec, and owns the reuse/modify/add decision end to end (`REUSE`/`KEEP` grounded in CodeGraph, `NEW` a ceiling, `REMOVE` the only authority to delete a public member, endpoint, config key, column or table).

## Definition of Done / compliance

- All five sections present, in order, zero TBD/TODO/placeholders, no contradictions.
- Every §5 acceptance criterion traces to a §1 Goal and vice versa; every scenario tagged `@integration` or `@unit`.
- §4 Scope names real repos/services; §2 Current State and §3 invariants hold against real code.
- Zero code/class-names/paths/line-numbers anywhere outside §5 Gherkin.
- Spec-gate score ≥ 9.0, zero blockers.

## Enforcement

`spec-reviewer` scores conformance to this contract (see [Policy 04](04-code-and-spec-review.md)),
confirming §4 Scope names real repos/services and that §2/§3 claims hold against real code
with CodeGraph. Format violations (code outside §5, symbols or paths in any section, any
`file:line` or line number, an untagged §5 scenario, a testing waiver of dev-team's in-repo
tests) are each blockers.

## Exceptions & waivers

- **BDD integration waiver** — requester-only, well-formed per §5 preamble; never a finding, costs zero points. Missing reason/basis or a contradiction with `bdd_required` metadata is a form defect (`major`), not a merit argument. A SANDBOX-suite waiver on `monxa.payment-gateway` or `monxa.auth-api` whose basis is not `requester` is a `major` authority defect.
- Bugs skip the spec unless the requester requests one (then the spec gate applies).

## References

- [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) — the five sections, format rules, BRIEF Gherkin standard, §5 QC-Scope preamble (source of truth).
- [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) — the dev sub-task brief template + the Change set / delta-marker model that owns the reuse/add decision.
- [`interview-me`](../../skills/interview-me/SKILL.md) — structured requirement clarification.
