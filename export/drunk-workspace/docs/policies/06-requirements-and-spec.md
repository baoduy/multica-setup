# Policy 06 — Requirements & Specification

| | |
|---|---|
| **Policy ID** | DRK-POL-06 |
| **Version** | 2.8 |
| **Status** | Active |
| **Owner** | product-owner (spec author) · spec-reviewer (gate) |
| **Applies to** | Every Workflow B feature/enhancement spec and every dev-team implementation brief |
| **Related skills** | [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) · [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) |
| **Enforced at** | spec review gate ([`spec-review-gate`](../../skills/spec-review-gate/SKILL.md)) |

> **Authority.** This policy is the source of truth for what a spec/brief contains.
> `sdlc-spec-template` and `sdlc-impl-brief` **implement** it — the seven sections,
> the format rules, and the tagged Gherkin derive from it. Amend this policy first, then
> cascade — see [change control](00-policies-index.md#change-control).

## Requirement cascade at a glance

```
   product-owner (WHAT & WHY)                              dev-leader (HOW)
   ┌──────────────────────────────┐                       ┌──────────────────────────┐
   │ SPEC (main ticket) — 7 §§     │                       │ IMPL BRIEF (dev sub-task)│
   │ §1 Goals   §2 Current State   │   business-level,      │ Goal · Current state ·   │
   │ §3 Expected State (+Security) │   NO file:line ──────▶ │ Change set (KEEP/MODIFY/ │
   │ §3a Contract (fields, routes) │   code detail is the   │ EXTEND/NEW/REMOVE) —     │
   │ §3b Architecture impact       │   dev-leader's job     │ covers every §3a row,    │
   │ §4 Scope   §5 Gherkin (@unit/ │                       │ honours every §3b line   │
   │   @integration, only code)    │                       └────────────┬─────────────┘
   └──────────────────────────────┘                                     ▼
                                                                 IMPLEMENTATION (code)
                                                       verified at the PR gate (Policy 04)

   §1–§4 = business prose, NO class names/paths/line-numbers.  §5 Gherkin is the only fenced block.
   §3a is the one place entity, field and endpoint names appear — the contract the team agrees before code.
   §3b places the change between repos and packages — never inside one; the PR gate checks the code against it.
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

1. **The clarification gate comes before any spec work.** No deliverable while any open question remains. Resolve what the code can answer via CodeGraph-first research; ask the requester ONLY what it cannot (business rules, scope, priorities). Post remaining questions as ONE numbered comment, then STOP and wait — repeat until zero open questions. §4 Scope must carry zero open questions. Run the gate with the `interview-me` and `multica-brainstorming` skills — the requester is interviewed, never guessed at; the role skill's procedure still owns the deliverable's shape and location.
2. **Role boundary.** product-owner states the problem, the required behaviour, the constraints, **the data and API contract the change adds (§3a)**, and **where the change sits between repos and packages (§3b)**. **dev-leader designs the implementation and decomposes it** into an impl-brief. Judging whether a change is minimal, reuses the right helper, or mirrors the right pattern in code is dev-leader's call at decomposition and pr-reviewer's at the merge gate — never spec content, never spec-review content. The contract surface is the exception the boundary draws on purpose: what the team must agree before code starts is a requirement, not a design. §3b is the same kind of exception: which repo or bounded context owns the change, which repo or package starts depending on which, and whether a published package's public surface breaks, is agreed before code. What sits below those surfaces — which class holds a field, which handler serves a route, which layer inside a repo holds the logic, what is reused — stays dev-leader's.
3. **The seven sections, in order,** with the headings `sdlc-spec-template` prints and the names this policy and the gate cite them by: 1 Why (Goals) · 2 Today (Current State) · 3 After the change (Expected State, ending in one Security line) · 3a Contract changes · 3b Architecture impact · 4 Scope · 5 Acceptance criteria (Gherkin, each scenario tagged `@integration` or `@unit`). The template owns the heading text; a spec that uses the cited name as its heading is not a finding. No word budgets — length scales with the requirement; a section is too long the moment it answers another section's question or explains mechanism.
3a. **Specs are written for a reader with intermediate English and no context.** One idea per sentence, under 20 words, everyday words, no metaphors or idioms, bullets over paragraphs, numbers as digits, a two-sentence Summary before §1, fixed sub-labels in §1 (Problem · Affected · Why now · Done means) and §4 (Repos/packages · Not in this change · Decisions · Open questions). The spec gate scores readability inside Business clarity (`sdlc-spec-template` writing rules). The same rules bind the root-cause report, the blocker report and the final summary — everything a human reads.
4. **Goals (§1) is the section the spec exists for** — name who is hurt, what it costs, why now, the affected role, and the observable signal the change worked, in language a non-engineer could act on. A thin or missing §1 is a spec-gate **blocker**.
5. **Invariants live in Expected State (§3)**, stated as the property that must hold ("an existing consumer's dependency-injection registration keeps working after the upgrade"), never as the code that holds it. §3 ends with one **Security line**: the trust boundary the change introduces, or "No new attack surface" with one clause of reasoning. This is where a design mandate becomes a legitimate requirement.

5a. **The contract lives in Contract changes (§3a).** Any change that adds or alters a domain entity states every new or changed field in a table: entity, field, type, length or precision, required, unique or indexed, default, and the notes a developer needs (allowed enum values, unit, currency, personal data, what existing rows get). Any change that adds, alters or removes an endpoint states every one of them in a table: change kind, HTTP verb, path, purpose, auth. A change touching neither says so in one line. §3a is the ONE section where entity, field and endpoint names are allowed; class names, method signatures, file paths and `file:line` stay banned there as everywhere else. A missing §3a where the change needs one is a spec-gate **blocker** — the team cannot review a contract it cannot see.
5b. **Architecture placement lives in Architecture impact (§3b).** Four labelled lines: **Owner** — the repo, and inside a service the bounded context, that owns the new behaviour and each new entity; **Dependencies** — every new or changed dependency between repos or packages, with its direction, or `none`; **Public surface** — for each published package the change touches, `additive`, `breaking` or `none`, and for `breaking`, what callers must change and that the release carries `(MINOR)` ([Policy 08](08-container-build-and-release.md) statement 12); **Integration** — for each new interaction between repos, how they talk (package reference, HTTP call, event), or `none`. A change that stays inside one repo, adds no dependency and changes no public surface says so in one line. §3b names repos, packages and bounded contexts only — never a class, project folder, layer or file. A placement that puts behaviour or data in a repo or context that does not own it, a dependency that creates a cycle or points against the stack's layering, or a breaking public-surface change declared `additive` or `none`, is a spec-gate **blocker**; a missing §3b where the change crosses repos or touches a published package's public surface is a **major**.
6. **Zero code blocks anywhere except the §5 Gherkin.** No C#, JSON, YAML, or mock-ups; the §3a contract is markdown tables, not fenced code. No class names, method signatures, or file paths in any section; naming a repo, package, entity, field or endpoint path is fine, naming a class or file is not.
7. **No `file:line` anywhere in the spec.** The spec is business-level above the contract. CodeGraph-verified code-level detail — paths, symbols, current implementation, reuse-vs-new — is the dev-leader's and lives in the impl-brief, never in the spec.

7a. **§4 Scope names every repo the change touches**, one per bullet, each with what changes in one clause — services, libraries, consumers that must be updated, and repos that need only a version bump. Multi-repo work is the normal case here; a repo the §3a contract or a §3 requirement plainly implies but §4 never names is a spec-gate **major**, because the squad sizes and schedules the work off this list.
8. **Research with CodeGraph before writing the business claims.** §2 Current State, every §3 invariant, and every §3b line claiming a property of the code today (a dependency that exists, a context that owns an entity) must be grounded by `codegraph explore` before the spec is posted — a §2/§3/§3b claim the code plainly contradicts, or a §4 Scope naming a repo/package that does not exist, is a spec-gate blocker.
9. **§5 Acceptance Criteria follows the BRIEF Gherkin standard** (Business language, Real data, Intention-revealing, Essential, Focused, Brief) and must be automatable as tests in the repo — drunk has no deployed system to run BDD scenarios against, so every scenario targets the test suite, never an environment.
10. **§5 scenario tags are the test scope, never a waiver.** Every scenario carries `@integration` or `@unit`; that tagging tells dev-team which suite each criterion belongs to and replaces the old separate Test Scope section. Testing is never optional: dev-team self-verifies every change at ≥80% per-touched-class coverage (tests authored by dev-backend, test-first) as part of Implementation regardless of what the spec says, so there is no `required`/`waived` toggle here (contrast a deployed-service factory's BDD-integration waiver, which does not exist in drunk). Any statement proposing to waive, defer, or skip testing is itself a blocker. The one exception is set by policy, not by the spec: a UI presentation change ([Policy 02](02-testing-and-quality.md) statement 1a) is built without tests; its §5 scenarios are still written and tagged, and they scope the later UI test pass.
11. **The spec-review gate loop:** score 1–10 on a weighted rubric (coverage & traceability 25%, Gherkin quality 20%, business clarity & problem framing 20%, architecture fit 15%, security 10%, completeness & unambiguity 10%). **APPROVED** requires score ≥ 8.5 AND zero blocker findings. **REWORK** (score < 8.5 or any blocker) loops back to product-owner, capped at **5 rounds** (tracked on the `Gate round` property, [Policy 04](04-code-and-spec-review.md) statement 11a); round 6 triggers **MANUAL HANDOFF** to the requester (or workspace-owner fallback) instead of a sixth rework. Each round is re-armed by product-owner in two mandatory parts — the sub-task flipped `in_progress --no-start`, then ONE resume comment carrying spec-reviewer's mention. A flip to `todo` re-arms nothing; the mention is the wake.
12. **Implementation brief (`sdlc-impl-brief`) is the layer below the spec** — dev-leader's translation into a task list against real code (Goal · Current state · Change set · delta markers KEEP/MODIFY/EXTEND/NEW/REMOVE). It carries the code-level detail the spec deliberately omits, never restates the business spec, and never contradicts the spirit of §3's invariants, a §3a contract row, or a §3b line. The brief's Change set covers every §3a row. A field, endpoint, table or migration the brief needs **beyond** §3a is dev-leader's design call, made explicit as its own Change set row rather than assumed from the spec — and if it changes the agreed contract or the §3b placement rather than sitting below it, dev-leader says so on the ticket instead of shipping the divergence quietly.
13. **Bugs (Workflow A) are NOT spec-gated.** Root-cause reports carry their own calibrated confidence gate (see [Policy 05](05-sdlc-delivery-lifecycle.md) and [Policy 07](07-bug-and-defect-management.md)) and only enter this policy's scope if the requester explicitly asks for a spec.

## Roles & responsibilities

- **product-owner** — authors the spec, runs the clarification gate to zero open questions, grounds §2/§3 claims with CodeGraph before posting, creates the `[S#]` sub-task, revises on REWORK, never edits the spec after a human handoff takes it.
- **spec-reviewer** — scores conformance to this contract, confirms Scope repos are real, Current State/invariants are not contradicted by the code, and the §3b placement fits the Scope repos' own conventions and stack standards, posts the verdict, gates APPROVED/REWORK/MANUAL HANDOFF, never edits the spec or designs the fix.
- **dev-leader** — reads the approved spec once, then works from the implementation brief it writes; owns every design decision the spec deliberately leaves open, including all code-level detail.

## Definition of Done / compliance

- All seven sections present, in order, zero TBD/TODO/placeholders, no contradictions.
- §3a states every new or changed field with type, length and attributes, and every new, changed or removed endpoint with verb and path — or one line saying the change touches neither.
- §3b names the owner, every new dependency with its direction, each touched published package's public-surface change, and each new integration — or one line saying the change stays inside one repo.
- §4 names every repo the change touches.
- Every §5 acceptance criterion traces to a §1 Goal and vice versa; every scenario tagged `@integration` or `@unit`.
- Zero code blocks outside §5's Gherkin; zero class names, method signatures, paths or line numbers anywhere, §3a included.
- §5 tags agree with §4 Scope; no waiver language present.
- Spec-gate score ≥ 8.5, zero blockers, before any Workflow C delegation.

## Enforcement

`spec-reviewer` scores conformance to this policy's contract (see
[Policy 04](04-code-and-spec-review.md)), confirming §4 Scope names real repos and that
§2/§3/§3b claims hold against real code with CodeGraph before scoring. Format violations — a
code block outside §5, a class name, method signature or path in any section, any
`file:line` citation, a missing/thin §1, a missing §3a where the change adds an entity or
an endpoint, an untagged §5 scenario, a testing waiver — are each a blocker regardless of
the overall score, as are the §3b placement defects of statement 5b. The PR gate then
checks the code against §3b ([Policy 04](04-code-and-spec-review.md) statement 5).

## Exceptions & waivers

- There is no BDD-integration waiver in drunk — unlike a deployed-service factory, there is
  no SANDBOX stage to waive; dev-team's in-repo verification is never optional and costs no
  points either way. UI presentation files are built without tests by policy
  ([Policy 02](02-testing-and-quality.md) statement 1a), not by the spec.
- A finding that exposes a genuine business question during REWORK reopens the
  clarification gate (statement 1) before the spec is revised again.
- Bugs skip this policy's gate unless the requester requests a spec, at which point every
  statement above applies to it exactly as to a feature.

## References

- [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) — the seven sections, the §3a contract tables, the §3b architecture lines, format rules, BRIEF Gherkin standard, tagged Gherkin (source of truth).
- [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) — the dev sub-task brief template and the Change set / delta-marker model.
- [`agents/product-owner.md`](../../agents/product-owner.md), [`agents/spec-reviewer.md`](../../agents/spec-reviewer.md).
