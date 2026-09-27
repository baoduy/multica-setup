# Policy 06 — Requirements & Specification

| | |
|---|---|
| **Policy ID** | MX-POL-06 |
| **Version** | 2.2 |
| **Status** | Active |
| **Owner** | product-owner (spec) · dev-leader (implementation brief) |
| **Applies to** | Every feature spec and every dev sub-task brief |
| **Related skills** | [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) · [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) · [`interview-me`](../../skills/interview-me/SKILL.md) |
| **Enforced at** | spec review gate ([`spec-review-gate`](../../skills/spec-review-gate/SKILL.md)) |

> **Authority.** This policy is the source of truth for what a spec/brief contains.
> `sdlc-spec-template` and `sdlc-impl-brief` **implement** it — the seven sections, the
> format rules, and the §5 QC-Scope preamble derive from it. Amend this policy first, then
> cascade — see [change control](00-policies-index.md#change-control).

## Requirement cascade at a glance

```
   product-owner (WHAT & WHY)                              dev-leader (HOW)
   ┌──────────────────────────────┐                       ┌──────────────────────────┐
   │ SPEC (main ticket) — 7 §§     │                       │ IMPL BRIEF (dev sub-task)│
   │ §1 Goals   §2 Current State   │   business-level,      │ Goal · Current state ·   │
   │ §3 Expected State (+Security) │   NO code/paths ─────▶ │ Change set (KEEP/MODIFY/ │
   │ §3a Contract (fields, routes) │   the reuse/add call   │ EXTEND/NEW/REMOVE) —     │
   │ §3b Architecture impact       │   is the dev-leader's  │ REUSE binding, NEW ceil., │
   │ §4 Scope   §5 Gherkin (@unit/ │                       │ covers every §3a row,    │
   │   @integration) + QC preamble │                       │ honours every §3b line   │
   └──────────────────────────────┘                       └────────────┬─────────────┘
                                                                       ▼
   §1–§4 = business prose, NO class names/paths/line-numbers.   IMPLEMENTATION (code)
   §5 Gherkin is the only fenced block.               verified vs the brief at the PR gate (Policy 04)
   §3a is the one place entity, field and endpoint names appear — the contract agreed before code.
   §3b places the change between repos and services — never inside one; the PR gate checks the code against it.
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

1. **Role boundary.** product-owner states the problem, the required behaviour, **the data and API contract the change adds (§3a)**, and **where the change sits between repos and services (§3b)**. **dev-leader designs the implementation and decomposes it** into an impl-brief. A spec that reads like a recipe buries the problem and forecloses better designs. The class- and method-level reuse/modify/add decision is the dev-leader's, made in the impl-brief's Change set, never in the spec. The contract surface is the exception the boundary draws on purpose: what the platform must agree before code starts is a requirement, not a design. §3b is the same kind of exception: which repo or bounded context owns the change, which repo or service starts depending on which, and whether a contract other services or external callers consume breaks, is agreed before code. What sits below those surfaces — which class holds a field, which handler serves a route, which layer inside a service holds the logic, what is reused — stays dev-leader's.
2. **The seven sections, in order:** 1 Goals · 2 Current State · 3 Expected State (ending in one Security line) · 3a Contract changes · 3b Architecture impact · 4 Scope · 5 Acceptance Criteria (the QC-Scope preamble, then Gherkin with every scenario tagged `@integration` or `@unit`). Each is done when it answers its question — **no word budgets**, length scales with the requirement.
3. **§1–§4 are business prose, above the contract.** No code, no class names, no method signatures, no file paths, no line numbers — §3a and §3b included. A code snippet next to a sentence lets the spec contradict itself — the squad implements the snippet. The **only** fenced block is the §5 Gherkin; the §3a contract is markdown tables.

3a. **The contract lives in Contract changes (§3a).** A change that adds or alters a domain entity states every new or changed field in a table: entity, field, type, length or precision, required, unique or indexed, default, and the notes a developer needs (allowed enum values, unit, currency, personal data, what existing rows get). A change that adds, alters or removes an endpoint states every one of them in a table: change kind, HTTP verb, path, purpose, auth. A change touching neither says so in one line each. §3a is the ONE section where entity, field and endpoint names are allowed. A missing §3a where the change needs one is a spec-gate **blocker** — the platform cannot review a contract it cannot see.

3b. **§4 Scope names every repo and service the change touches**, one per bullet with what changes in one clause — including consumers that must be updated and services needing only a version bump. Monxa runs one platform across many repos; a repo the §3a contract or a §3 requirement plainly implies but §4 never names is a spec-gate **major**, because squads are sized and sequenced off this list.

3c. **Architecture placement lives in Architecture impact (§3b).** Four labelled lines: **Owner** — the repo, and inside a service the bounded context, that owns the new behaviour and each new entity; **Dependencies** — every new or changed dependency between repos or services, with its direction, or `none`; **Public surface** — for each contract other services or external callers consume that the change touches (a service's HTTP API, a Service Bus event or message, a webhook payload, a shared package another repo references), `additive`, `breaking` or `none`, and for `breaking`, which callers must change and the repos §4 names for them; **Integration** — for each new interaction between repos or services, how they talk (HTTP call, Service Bus event or message, webhook, package reference), or `none`. A change that stays inside one repo, adds no dependency and changes no public surface says so in one line. §3b names repos, services and bounded contexts only — never a class, project folder, layer or file. A placement that puts behaviour or data in a repo or context that does not own it, a dependency that creates a cycle or points against the stack's layering, or a breaking public-surface change declared `additive` or `none`, is a spec-gate **blocker**; a missing §3b where the change crosses repos or services or touches a public surface is a **major**. Every §3b line claiming a property of the code today (a dependency that exists, a context that owns an entity) is grounded with CodeGraph before the spec is posted; one the code plainly contradicts is a **blocker**.
4. **Goals (§1) is the section the spec exists for** — name who is hurt, what it costs, why now, the affected role, and the observable signal the change worked, in language a non-engineer could act on. A thin or missing §1 is a spec-gate **blocker**.
5. **Invariants live in Expected State (§3)**, stated as the property that must hold ("a payout must never fail because of a notification"), never as the code that holds it. §3 ends with one **Security line**: the trust boundary in business terms, or "No new attack surface" with reasoning; payments idempotency/replay where relevant.
6. **No `file:line`, symbol, or Change Map in the spec.** The reuse/modify/add decision — one call per class/method touched — is the dev-leader's, made in the impl-brief's Change set (`KEEP`/`MODIFY`/`EXTEND`/`NEW`/`REMOVE`) from CodeGraph research, ordered REUSE-first so what already exists is read first. A `NEW` row is valid only after searching for something to reuse and finding nothing; a new entity/table/migration is its own `NEW` row or it is out of scope. The §3a contract is binding input to that Change set, not a substitute for it: §3a says which fields and endpoints the change owes, the Change set says which classes and migrations deliver them.
7. **§5 Acceptance Criteria** opens with the two-line QC-Scope preamble, then BRIEF-compliant Gherkin. Every scenario is tagged `@integration` or `@unit`; the tag plus the preamble is the whole test-scope statement.
8. **QC Scope (§5 preamble)** is exactly one `Ships this cycle:` line and one `BDD integration tests: required` / `... : waived — <reason> (basis: <requester | product-owner judgment | repo note>, <date>)` line, agreeing with the `ship_required`/`bdd_required` metadata and with each other. The BDD-integration waiver, and any SANDBOX-suite waiver on the money/identity path (`monxa.payment-gateway`, `monxa.auth-api`), is the requester's decision — product-owner may never waive those on its own judgment.
9. **Clarify to zero open questions before writing** — never ask what the code answers; use [`interview-me`](../../skills/interview-me/SKILL.md) to structure the intake. §4 Scope carries zero unresolved questions.
10. **Implementation brief (`sdlc-impl-brief`) is the layer below the spec** — dev-leader's translation into a task list against real code (Goal · Current state · Change set · delta markers KEEP/MODIFY/EXTEND/NEW/REMOVE). Every §3a row is covered by a Change set row, and the Change set honours every §3b line; a field or endpoint needed beyond §3a is dev-leader's own row, and one that would change what §3a agreed, or the §3b placement, goes back to product-owner on the ticket instead of landing quietly. It carries the code-level detail the spec omits, never restates the business spec, and owns the reuse/modify/add decision end to end (`REUSE`/`KEEP` grounded in CodeGraph, `NEW` a ceiling, `REMOVE` the only authority to delete a public member, endpoint, config key, column or table).

## Definition of Done / compliance

- All seven sections present, in order, zero TBD/TODO/placeholders, no contradictions.
- §3a states every new or changed field with type, length and attributes, and every new, changed or removed endpoint with verb and path — or one line saying the change touches neither.
- §3b names the owner, every new dependency with its direction, each touched public surface's change, and each new integration — or one line saying the change stays inside one repo.
- §4 names every repo and service the change touches.
- Every §5 acceptance criterion traces to a §1 Goal and vice versa; every scenario tagged `@integration` or `@unit`.
- §4 Scope names real repos/services; §2 Current State, §3 invariants and §3b claims hold against real code.
- Zero code blocks outside §5 Gherkin; zero class names, method signatures, paths or line numbers anywhere, §3a and §3b included.
- Spec-gate score ≥ 9.0, zero blockers.

## Enforcement

`spec-reviewer` scores conformance to this contract (see [Policy 04](04-code-and-spec-review.md)),
confirming §4 Scope names real repos/services, that §2/§3/§3b claims hold against real code
with CodeGraph, and that the §3b placement fits each Scope repo's own conventions and stack
standard. Format violations (code outside §5, class names, method signatures or paths in any section,
any `file:line` or line number, a missing §3a where the change adds an entity or an
endpoint, an untagged §5 scenario, a testing waiver of dev-team's in-repo tests) are each
blockers, as are the §3b placement defects of statement 3c. The PR gate then checks the code
against §3b ([Policy 04](04-code-and-spec-review.md) statement 4).

## Exceptions & waivers

- **BDD integration waiver** — requester-only, well-formed per §5 preamble; never a finding, costs zero points. Missing reason/basis or a contradiction with `bdd_required` metadata is a form defect (`major`), not a merit argument. A SANDBOX-suite waiver on `monxa.payment-gateway` or `monxa.auth-api` whose basis is not `requester` is a `major` authority defect.
- Bugs skip the spec unless the requester requests one (then the spec gate applies).

## References

- [`sdlc-spec-template`](../../skills/sdlc-spec-template/SKILL.md) — the seven sections, the §3a contract tables, the §3b architecture lines, format rules, BRIEF Gherkin standard, §5 QC-Scope preamble (source of truth).
- [`sdlc-impl-brief`](../../skills/sdlc-impl-brief/SKILL.md) — the dev sub-task brief template + the Change set / delta-marker model that owns the reuse/add decision.
- [`interview-me`](../../skills/interview-me/SKILL.md) — structured requirement clarification.
