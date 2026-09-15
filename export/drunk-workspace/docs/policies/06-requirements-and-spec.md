# Policy 06 — Requirements & Specification

| | |
|---|---|
| **Policy ID** | DRK-POL-06 |
| **Version** | 2.1 |
| **Status** | Active |
| **Owner** | product-owner (spec author) · spec-reviewer (gate) |
| **Applies to** | Every Workflow B feature/enhancement spec and every dev-team implementation brief |
| **Related skills** | [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) · [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) |
| **Enforced at** | spec review gate ([`spec-review-gate`](../../skills/spec-review-gate/SKILL.md)) |

> **Authority.** This policy is the source of truth for what a spec/brief contains.
> `sdlc-spec-template` and `sdlc-impl-brief` **implement** it — the five sections,
> the format rules, and the tagged Gherkin derive from it. Amend this policy first, then
> cascade — see [change control](00-policies-index.md#change-control).

## Requirement cascade at a glance

```
   product-owner (WHAT & WHY)                              dev-leader (HOW)
   ┌──────────────────────────────┐                       ┌──────────────────────────┐
   │ SPEC (main ticket) — 5 §§     │                       │ IMPL BRIEF (dev sub-task)│
   │ §1 Goals   §2 Current State   │   business-level,      │ Goal · Current state ·   │
   │ §3 Expected State (+Security) │   NO file:line ──────▶ │ Change set (KEEP/MODIFY/ │
   │ §4 Scope   §5 Gherkin (@unit/ │   code detail is the   │ EXTEND/NEW/REMOVE)       │
   │   @integration, only code)    │   dev-leader's job     └────────────┬─────────────┘
   └──────────────────────────────┘                                     ▼
                                                                 IMPLEMENTATION (code)
                                                       verified at the PR gate (Policy 04)

   §1–§4 = business prose, NO code/class/paths/line-numbers.  §5 Gherkin is the only fenced block.
```

## Purpose

A spec exists to convey the **problem and the required behaviour** so dev-team builds the
right thing, correctly, minimally, and securely — without dev-team ever needing to open
the main ticket's comment thread. This policy fixes what a spec contains and where the
boundary between "what" (product-owner) and "how" (dev-leader) sits: a spec that reads
like a recipe buries the problem, forecloses a better design, and — since prose cannot
contradict a code snippet that disagrees with it — risks shipping the contradiction
silently.

## Scope

Feature/enhancement specs on main tickets for drunk library and infra repos (`DKNet`
family, `drunk-pulumi-*`, `drunk-others`) — the requester-facing, gate-scored artifact —
and the implementation briefs dev-leader writes into `[D<num>-n]` coding sub-tasks. Bugs
use a root-cause report instead of a spec unless the requester explicitly asks for one
(see [Policy 07](07-bug-and-defect-management.md)); a requested bug spec then passes this
same gate.

## Policy statements

1. **The clarification gate comes before any spec work.** No deliverable while any open question remains. Resolve what the code can answer via CodeGraph-first research; ask the requester ONLY what it cannot (business rules, scope, priorities). Post remaining questions as ONE numbered comment, then STOP and wait — repeat until zero open questions. §4 Scope must carry zero open questions.
2. **Role boundary.** product-owner states the problem, the required behaviour, and the constraints. **dev-leader designs the implementation and decomposes it** into an impl-brief. Judging whether a change is minimal, reuses the right helper, or mirrors the right pattern in code is dev-leader's call at decomposition and pr-reviewer's at the merge gate — never spec content, never spec-review content.
3. **The five sections, in order:** 1 Goals · 2 Current State · 3 Expected State (ending in one Security line) · 4 Scope · 5 Acceptance Criteria (Gherkin, each scenario tagged `@integration` or `@unit`). No word budgets — length scales with the requirement; a section is too long the moment it answers another section's question or explains mechanism.
3a. **Specs are written for a reader with intermediate English and no context.** One idea per sentence, under 20 words, everyday words, no metaphors or idioms, bullets over paragraphs, numbers as digits, a two-sentence Summary before §1, fixed sub-labels in §1 (Problem · Affected · Why now · Done means) and §4 (Repos/packages · Not in this change · Decisions · Open questions). The spec gate scores readability inside Business clarity (`sdlc-spec-template` writing rules). The same rules bind the root-cause report, the blocker report and the final summary — everything a human reads.
4. **Goals (§1) is the section the spec exists for** — name who is hurt, what it costs, why now, the affected role, and the observable signal the change worked, in language a non-engineer could act on. A thin or missing §1 is a spec-gate **blocker**.
5. **Invariants live in Expected State (§3)**, stated as the property that must hold ("an existing consumer's dependency-injection registration must never break across a minor version bump"), never as the code that holds it. §3 ends with one **Security line**: the trust boundary the change introduces, or "No new attack surface" with one clause of reasoning. This is where a design mandate becomes a legitimate requirement.
6. **Zero code blocks anywhere except the §5 Gherkin.** No C#, JSON, YAML, or mock-ups. No class names, method signatures, or file paths in any section; naming a repo or package is fine, naming a class or file is not.
7. **No `file:line` anywhere in the spec.** The spec is business-level. CodeGraph-verified code-level detail — paths, symbols, current implementation, reuse-vs-new — is the dev-leader's and lives in the impl-brief, never in the spec.
8. **Research with CodeGraph before writing the business claims.** §2 Current State and every §3 invariant claiming a property of the code today must be grounded by `codegraph explore` before the spec is posted — a §2/§3 claim the code plainly contradicts, or a §4 Scope naming a repo/package that does not exist, is a spec-gate blocker.
9. **§5 Acceptance Criteria follows the BRIEF Gherkin standard** (Business language, Real data, Intention-revealing, Essential, Focused, Brief) and must be automatable as tests in the repo — drunk has no deployed system to run BDD scenarios against, so every scenario targets the test suite, never an environment.
10. **§5 scenario tags are the test scope, never a waiver.** Every scenario carries `@integration` or `@unit`; that tagging tells dev-team which suite each criterion belongs to and replaces the old separate Test Scope section. Testing is never optional: dev-team self-verifies every change at ≥80% per-touched-class coverage (tests authored by dev-backend, test-first) as part of Implementation regardless of what the spec says, so there is no `required`/`waived` toggle here (contrast a deployed-service factory's BDD-integration waiver, which does not exist in drunk). Any statement proposing to waive, defer, or skip testing is itself a blocker.
11. **The spec-review gate loop:** score 1–10 on a weighted rubric (coverage & traceability 30%, Gherkin quality 25%, business clarity & problem framing 20%, security 10%, completeness & unambiguity 15%). **APPROVED** requires score ≥ 8.5 AND zero blocker findings. **REWORK** (score < 8.5 or any blocker) loops back to product-owner, capped at **5 rounds** (tracked via the `spec_review_round` metadata key); round 6 triggers **MANUAL HANDOFF** to the requester (or workspace-owner fallback) instead of a sixth rework.
12. **Implementation brief (`sdlc-impl-brief`) is the layer below the spec** — dev-leader's translation into a task list against real code (Goal · Current state · Change set · delta markers KEEP/MODIFY/EXTEND/NEW/REMOVE). It carries the code-level detail the spec deliberately omits, never restates the business spec, and never contradicts the spirit of §3's invariants; anything the brief needs beyond the spec (a new entity, table, or migration) is dev-leader's design call, made explicit in the brief's Change set rather than assumed from the spec.
13. **Bugs (Workflow A) are NOT spec-gated.** Root-cause reports carry their own calibrated confidence gate (see [Policy 05](05-sdlc-delivery-lifecycle.md) and [Policy 07](07-bug-and-defect-management.md)) and only enter this policy's scope if the requester explicitly asks for a spec.

## Roles & responsibilities

- **product-owner** — authors the spec, runs the clarification gate to zero open questions, grounds §2/§3 claims with CodeGraph before posting, creates the `[S#]` sub-task, revises on REWORK, never edits the spec after a human handoff takes it.
- **spec-reviewer** — scores conformance to this contract, confirms Scope repos are real and Current State/invariants are not contradicted by the code, posts the verdict, gates APPROVED/REWORK/MANUAL HANDOFF, never edits the spec or designs the fix.
- **dev-leader** — reads the approved spec once, then works from the implementation brief it writes; owns every design decision the spec deliberately leaves open, including all code-level detail.

## Definition of Done / compliance

- All five sections present, in order, zero TBD/TODO/placeholders, no contradictions.
- Every §5 acceptance criterion traces to a §1 Goal and vice versa; every scenario tagged `@integration` or `@unit`.
- Zero code/class-names/paths/line-numbers anywhere outside §5's Gherkin.
- §5 tags agree with §4 Scope; no waiver language present.
- Spec-gate score ≥ 8.5, zero blockers, before any Workflow C delegation.

## Enforcement

`spec-reviewer` scores conformance to this policy's contract (see
[Policy 04](04-code-and-spec-review.md)), confirming §4 Scope names real repos and that
§2/§3 claims hold against real code with CodeGraph before scoring. Format violations — a
code block outside §5, a symbol or path in any section, any `file:line` citation, a
missing/thin §1, an untagged §5 scenario, a testing waiver — are each a blocker regardless
of the overall score.

## Exceptions & waivers

- There is no BDD-integration waiver in drunk — unlike a deployed-service factory, there is
  no SANDBOX stage to waive; dev-team's in-repo verification is never optional and costs no
  points either way.
- A finding that exposes a genuine business question during REWORK reopens the
  clarification gate (statement 1) before the spec is revised again.
- Bugs skip this policy's gate unless the requester requests a spec, at which point every
  statement above applies to it exactly as to a feature.

## References

- [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) — the five sections, format rules, BRIEF Gherkin standard, tagged Gherkin (source of truth).
- [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) — the dev sub-task brief template and the Change set / delta-marker model.
- [`agents/product-owner.md`](../../agents/product-owner.md), [`agents/spec-reviewer.md`](../../agents/spec-reviewer.md).
