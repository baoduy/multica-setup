# SDLC Spec Template — shared spec contract

**Single source of truth for what a Monxa feature spec contains.** `product-owner` authors against it; `spec-reviewer` scores conformance to it. Neither restates it — if a role skill disagrees with this file, **this file wins** and the mismatch goes to the workspace owner.

## Role boundary

**product-owner states the problem and required behaviour. dev-leader designs the implementation and decomposes it** into an `sdlc-impl-brief`.

A spec that reads like a recipe buries the problem and forecloses better designs the squad can see and the author cannot. It also lets the spec contradict itself: put a code snippet next to a sentence and the squad implements the snippet, silently, even where the sentence was right.

The opposite failure — a spec that never says what already exists, so a new entity and new SQL tables get built for a need existing methods already cover — is closed one layer down, in the dev-leader's `sdlc-impl-brief`: its Change set names, per class and per method, what is reused, modified, removed, and genuinely new. That class-level reuse/modify/add decision is code-level and belongs to dev-leader at decomposition, never in the spec.

**The contract is the exception.** The data and API surface a change adds is what the whole platform must agree on before code starts, so it belongs in the spec: §3a carries the new fields with their types and attributes, and the endpoints with their verbs and paths. Everything below that surface stays dev-leader's: which class holds the field, which handler serves the route, what is reused. dev-leader may add rows to the contract in its impl-brief and must say so there; it may never contradict a §3a row.

**Placement is the second exception.** Where the change sits between repos and services is agreed before code too, so §3b states it: which repo or bounded context owns the change, which repo or service starts depending on which, and whether a contract other services or external callers consume breaks. Only repos, services and bounded contexts appear there — never a class, folder, layer or file. Which layer inside a service holds the logic stays dev-leader's, and the PR gate checks the code against §3b.

## The seven sections

In this order, in the main ticket description. **No word budgets — length scales with the size of the requirement.** A section is done when it answers its question below; it is too long the moment a sentence answers another section's question or explains mechanism. Cut mechanism, never business context.

| # | Section | Must answer — stop when answered |
|---|---------|----------------------------------|
| 1 | **Goals** | Who is hurt, what it costs, why now — and the observable signal it worked. Name the affected role. Business language only; done when a non-engineer could act on it. |
| 2 | **Current State** | How the system behaves today, in business terms — the before-picture the change starts from. Behaviour, not code: no class names, no service internals. |
| 3 | **Expected State** | What the system must do after the change, observable from outside — outcomes, not mechanism — plus any invariant that must hold ("a payout must never fail because of a notification"), stated as a property, never the code that holds it. **Ends with one Security line:** the trust boundary in business terms, or "No new attack surface" with reasoning; payments idempotency/replay where relevant. |
| 3a | **Contract changes** | The data and API surface this change adds. Two markdown tables, filled only where they apply, each otherwise one line (`None — no data contract change.` / `None — no API change.`). **Fields:** `Entity · Field · Type · Length / precision · Required · Unique / indexed · Default · Notes` — one row per new or changed field; length required for text and decimal types, `n/a` otherwise; Notes carries what a developer must know (allowed enum values, unit, currency, personal data, what existing rows get). **Endpoints:** `Change (new/changed/removed) · Verb · Path · Purpose · Auth` — one row per endpoint; a changed one says what changes, a removed one names its replacement. The only section where entity, field and endpoint names appear; class names, method signatures and paths stay banned here too. |
| 3b | **Architecture impact** | Where the change sits between repos and services. A change that stays inside one repo, adds no dependency and changes no public surface writes one line: `None — stays inside <repo>; no new dependency; no public-surface change.` Otherwise four labelled lines. **Owner:** the repo — and inside a service, the bounded context — that owns the new behaviour and each new entity. **Dependencies:** each new or changed dependency between repos or services, with its direction ("`<service A>` starts calling `<service B>`"), or `none`. **Public surface:** each contract other services or external callers consume that the change touches — a service's HTTP API, a Service Bus event or message, a webhook payload, a shared package another repo references — `additive`, `breaking` or `none`; for `breaking`, which callers must change, and §4 names their repos. **Integration:** each new interaction between repos or services — HTTP call, Service Bus event or message, webhook, package reference — or `none`. Done when a reviewer can tell, without opening the code, which repo owns the change, which way every new dependency points, and whether any consumer breaks. Repos, services and bounded contexts only — never a class, project folder, layer or file. |
| 4 | **Scope** | **Every repo and service the change touches** — one per bullet, each with what changes in one clause, including consumers that must be updated and services needing only a version bump. Plus explicit no-gos, and any resolved decision with attribution and date. Zero open questions. Service granularity only — a service name is fine, a class is not. Monxa is many services in many repos: a repo the §3a contract implies but §4 never names is a gate finding, because the squads are sized off this list. |
| 5 | **Acceptance Criteria** | The QC-scope preamble (below), then BRIEF-compliant Gherkin with every scenario tagged `@integration` or `@unit`. The only fenced block in the spec. **When the deliverable is a demonstration or sample, at least one scenario must be observable from the RUNNING artefact** — a developer boots it and sees the behaviour — not only from its test suite. DRK-1188 proved role-gated properties in tests and docs while every seeded product had them null, so `dotnet run` + `GET /v1/products` showed nothing to anyone (DRK-1198 item 3). |

## Format rules

- **Zero code blocks anywhere except the Gherkin in §5.** No C#, JSON, YAML, or mock-ups.
- **No class names, method signatures, or symbols in §1–§5, §3a and §3b included.** A service, repo, entity, field or endpoint path is fine; a class name is not. Class- and method-level reuse/modify/add decisions are code-level and live in the dev-leader's `sdlc-impl-brief` (its Change set), not here.
- **The §3a tables are tables, not code blocks** — the Gherkin in §5 stays the only fenced block.
- **No line numbers and no `file:line` anywhere in the spec.**
- **State each property once**; every later section that relies on it references it ("per §3"), never restates it.
- **Scale to size.** For a cosmetic or single-behaviour change, collapse the light sections to a line: §2 to one sentence, §3a to its two `None —` lines, §3b to its one `None —` line, §4's decisions to a bullet, the Security line to "No new attack surface — <reason>".

## §5 QC Scope — two fixed lines (preamble to the Gherkin)
```
Ships this cycle: yes
Ships this cycle: no — <reason> (basis: <requester | product-owner judgment | repo note>, <YYYY-MM-DD>)

BDD integration tests: required
BDD integration tests: waived — <reason> (basis: <requester | product-owner judgment | repo note>, <YYYY-MM-DD>)
```
State one `Ships this cycle:` line and one `BDD integration tests:` line above the scenarios. A waiver with no reason or no basis is not a waiver. The two lines must agree with the `ship_required`/`bdd_required` metadata on the main ticket, and with each other — `Ships this cycle: no` forces `BDD integration tests: waived`. If a line disagrees with metadata, fix the key.

**Product-owner sets scope by judgment; requester overrides it either way.** Two things product-owner's judgment can never waive, so their basis must read `requester`: dev-team's in-repo tests (never expressible as a waiver here at all — they are always in `[P#-1]`), and the SANDBOX-suite waiver on the money/identity path (`monxa.payment-gateway`, `monxa.auth-api`). `spec-reviewer` checks FORM and authority-of-basis, never the merit of a well-formed decision. When integration tests are **not** waived, tag the covering scenarios `@integration`; everything else is `@unit`. See `sdlc-flow-po-orchestration` for the decision procedure and `spec-review-gate` for the form check.

## Gherkin standard — BRIEF

Seb Rose / Cucumber: **B**usiness language · **R**eal data (concrete values — "Acme Pte Ltd", not "merchant") · **I**ntention revealing (actor's intent, not mechanics) · **E**ssential (cut anything not illustrating the rule) · **F**ocused (one rule, one Given-When-Then) · **B**rief.

- **Primary test, applied first — Cucumber's own:** *would this wording change if the implementation changed?* If yes, it is a finding.
- **No hard step count.** Score `Brief` qualitatively; published limits disagree and neither is official, so step count is never a finding on its own.
- Declarative preferred. Imperative is permitted where the mechanism genuinely IS the requirement — at most a `minor`, never a bar to clear.
- Third-person named actors, never "I". No UI mechanics, config keys, method or field names — the contract lives in §3a, the scenarios stay in business language.
- Every scenario automatable. Happy path before negative and edge scenarios.
- **Tag every scenario `@integration` or `@unit`.** `@integration` needs a real integration surface (database, HTTP, service boundary); everything else is `@unit`. The tag, together with the QC-scope preamble, is the whole test-scope statement — there is no separate section.

## Quality Bar

In order:

1. **Clear** — a non-engineer can act on §1; invariants in §3 are properties, not mechanisms.
2. **Correct** — acceptance criteria trace to §1.
3. **Complete** — every business requirement covered by ≥1 scenario.
4. **Secure** — the §3 Security line is concrete; payments idempotency/replay where relevant.
5. **Contract-complete** — every field and endpoint the change needs is in §3a with its type, length and attributes, and §4 names every repo and service touched.
6. **Well-placed** — §3b puts the change in the repo and bounded context that own it, every new dependency points the way the stack's layering allows with no cycle, and every public-surface break is declared.

If the requester demands an over-built or insecure outcome, push back with evidence at the clarification gate rather than specifying it.
