# SDLC Spec Template — shared spec contract

**Single source of truth for what a drunk-workspace feature spec contains.** `product-owner` writes against it; `spec-reviewer` scores against it. If a role skill and this file disagree, this file wins.

**Role boundary.** product-owner states the problem and the required behaviour. dev-leader designs the solution and decomposes it (`sdlc-impl-brief`). A spec that reads like a recipe is defective even when the recipe is right: it hides the problem, blocks better designs, and a code snippet can contradict the prose. Whether a change is minimal or reuses the right helper is judged in code, at decomposition and at the PR gate, never in the spec.

**The contract is the exception.** The data and API surface a change adds is what the whole team must agree on before code starts, so it belongs in the spec: §3a carries the new fields with their types and attributes, and the endpoints with their verbs and paths. Everything below that surface stays dev-leader's: which class holds the field, which handler serves the route, what gets reused. dev-leader may add rows to the contract in its impl-brief and must say so there; it may never contradict a §3a row.

**Placement is the second exception.** Where the change sits between repos and packages is agreed before code too, so §3b states it: which repo or bounded context owns the change, which repo or package starts depending on which, and whether a published package's public surface breaks. Only repos, packages and bounded contexts appear there — never a class, folder, layer or file. Which layer inside a repo holds the logic stays dev-leader's, and the PR gate checks the code against §3b. A repo with an approved service design (`docs/architect/` on `dev`) fixes placement already: §3b opens with `Fits <service> design revision <n>` and must not contradict that design — a spec that needs it changed waits for a Workflow F ticket.

## Who reads a spec

The requester, the workspace owner, the spec gate, the dev-leader, and the implementer. The humans may have intermediate English and no context. Write for them:

1. One idea per sentence. Under 20 words. Active voice.
2. Everyday words. No metaphors or idioms ("pay a tax", "double down", "cheapest moment").
3. Bullets over paragraphs. A paragraph is at most 3 sentences.
4. Numbers as digits (16 routes, 80%). Dates as `2026-09-15`.
5. Name a thing the same way every time. Define an acronym once, in brackets. When a Scope repo has an approved service design, use the terms of its ubiquitous-language table (`docs/architect/02-domain.md`) with the meaning given there; a term the table lacks is defined once, in the spec.
6. No code words: no class names, method signatures, file paths, flags or `file:line` — in any section, §3a and §3b included. Product and package names and error codes in backticks are fine. §3a is the only place entity, field and endpoint names appear.
7. Lead with the answer. Reasoning comes after, short.

## Template

Written into the root ticket description, in this order. Length follows the size of the requirement; a small change collapses §2 and §4 to one bullet each. Every section keeps its heading.

Policy 06 and the gate cite three of these sections by their older names — §1 Why is **Goals**, §2 Today is **Current State**, §3 After the change is **Expected State**. Same sections; the headings below are the ones to write.

```markdown
# <Plain title: what changes, for whom — no type prefix; the `[Feature]`/`[Enhance]`/… prefix belongs on the TICKET title, not this heading>

**Summary.** <Two sentences. What changes. Who benefits.>

## 1. Why
- **Problem:** <who has the problem, and what it costs them>
- **Affected:** <the user, role or team>
- **Why now:** <one sentence>
- **Done means:** <the result a person can observe when the change works>

## 2. Today
- <one behaviour per bullet, plain words>

## 3. After the change
- <"The system must …" — one requirement per bullet, observable from outside>

**Must stay true:**
- <an invariant, written as a property, never as the code that holds it>

**Security:** <one sentence: the new trust boundary, or "No new attack surface, because …">

## 3a. Contract changes

Fill only the tables the change touches. For the other, write one line: `None — no data contract change.` or `None — no API change.` These are markdown tables, not code blocks.

**New or changed data fields**

| Entity | Field | Type | Length / precision | Required | Unique / indexed | Default | Notes |
|---|---|---|---|---|---|---|---|
| `<entity or table>` | `<field>` | `<string, decimal, uuid, timestamp, bool, enum name>` | `<20 · 18,2 · n/a>` | yes / no | unique / indexed / no | `<value or none>` | `<allowed values, unit, currency, personal data>` |

One row per field. Length is required for text and decimal types. Say `n/a` where the type carries no length. Note anything a developer must know to create the field: allowed enum values, unit, currency, whether it holds personal data, and whether existing rows need a value.

**Endpoints**

| Change | Verb | Path | Purpose | Auth |
|---|---|---|---|---|
| new / changed / removed | `GET` | `/v1/<path>` | `<one clause>` | `<role, scope, or anonymous>` |

One row per endpoint. A changed endpoint says what changes in Purpose. A removed endpoint names what replaces it.

## 3b. Architecture impact

A change that stays inside one repo, adds no dependency and changes no public surface writes one line: `None — stays inside <repo>; no new dependency; no public-surface change.` Otherwise, all four lines:

<When a Scope repo has an approved service design, open with: `Fits <service> design revision <n>.`>

- **Owner:** <the repo — and inside a service, the bounded context — that owns the new behaviour and each new entity>
- **Dependencies:** <each new or changed dependency, one per bullet, with its direction: "`<package A>` starts using `<package B>`" — or `none`>
- **Public surface:** <each published package touched: `additive`, `breaking` or `none`. For `breaking`: what callers must change, and "the release carries `(MINOR)`">
- **Integration:** <each new interaction between repos: package reference, HTTP call or event — or `none`>

## 4. Scope
- **Repos / packages:** <every repo the change touches — one per bullet, each with what changes in one clause. Include consumers that must be updated and repos that only need a version bump. Names only, never a file or class.>
- **Not in this change:** <one per bullet>
- **Decisions:** `2026-09-15 · <who> · <decision in one sentence>`
- **Open questions:** none

## 5. Acceptance criteria
```gherkin
Feature: <name>

  @integration
  Scenario: <happy path, one rule>
    Given <real names and values>
    When <one action>
    Then <one observable result>
```
```

Section tests: §1 is done when a non-engineer could act on it. §2 is done when it describes today's behaviour without saying how it is built. §3 is done when every requirement can be checked from outside and every invariant is a property. §3a is done when a developer can create every field and call every endpoint without asking a question. §3b is done when a reviewer can tell, without opening the code, which repo owns the change, which way every new dependency points, and whether any published package breaks. §4 is done when it names every repo the change touches and holds zero open questions. §5 is done when every requirement in §3 has at least one scenario and every scenario traces to §1.

## Gherkin — BRIEF

Business language · Real data ("treasury-ops", 100.00 SGD, never "a user") · Intention revealing · Essential · Focused (one rule per scenario, one Given-When-Then) · Brief.

- Primary test: would this wording change if the implementation changed? If yes, fix it.
- At most 6 steps per scenario. Happy path first, then refusals and edges. Use a Scenario Outline for variants of one rule instead of copies. No hard scenario count; around 10 is a warning sign to look for Outlines.
- Third-person named actors, never "I". No UI mechanics, config keys, or member names.
- Tag every scenario `@integration` (crosses a real boundary: database, HTTP, package) or `@unit`. The tags are the test-scope statement; there is no separate section. The third tag, `@stack`, marks a scenario only the running stack can show, on coverage-excluded wiring (Policy 02 §1e): the repo's coverage config on `dev` leaves the surface out, or a §4 `Test scope` decision names it. dev-team quotes its literal output instead of automating it. `@stack` on anything else is a waiver.
- When the deliverable is a sample or demo, at least one scenario is observable from the running artefact, not only from its tests.
- The Gherkin block is the only code block in the spec. The §3a tables are tables, not code blocks.
- §5 still carries no field or endpoint names — scenarios stay in business language. The contract lives in §3a.

## Verification

Testing is never optional and never negotiated at spec time, except by the ticket's owner (below). dev-team writes the §5 scenarios as acceptance tests first, implements against them frozen, and self-verifies at ≥80% coverage per touched class plus a clean pack (`test-driven-development`). §5 says what the suite covers and which kind each scenario is, never whether it runs. The exceptions are set by policy, not by the spec: a UI presentation change (screens, layouts, components, styling, copy — Policy 02 §1a) is built without tests, and its §5 scenarios are still written and tagged — they scope the later UI test pass. Coverage-excluded wiring (an Aspire AppHost, container, compose or realm definitions, config data, demo or load tools — Policy 02 §1e) has no coverage or mutation bar: its automatable scenarios keep `@unit`/`@integration`, and the rest are `@stack`. When the repo's coverage config on `dev` does not settle a wiring surface, §4 carries the requester's answer as `<date> · <who> · Test scope: <surface> — proven on the running stack`. Code no shipped artifact uses (an Aspire AppHost and the apps only it starts, test projects, test helpers) is built without tests when the ticket's resolved owner waives them in their own reply (Policy 02 §1f): §4 carries `<date> · <owner> · Test waiver: <surface> — <reason>`, and its §5 scenarios are still written and tagged. Never for code a shipped project uses, security or authorization code, a published package's public API, or a bug fix's reproduction.

## Quality bar

1. **Clear** — a non-engineer can act on §1 and read §2–§4 without a dictionary.
2. **Correct** — every scenario traces to §1.
3. **Complete** — every requirement in §3 has a scenario.
4. **Secure** — the Security line is concrete.
5. **Contract-complete** — every field and endpoint the change needs is in §3a with its type, length and attributes, and §4 names every repo touched.
6. **Well-placed** — §3b puts the change in the repo that owns it, every new dependency points the way the stack's layering allows, and every public-surface break is declared.

If the requester asks for an over-built or insecure outcome, push back with evidence at the clarification gate instead of writing it down.
