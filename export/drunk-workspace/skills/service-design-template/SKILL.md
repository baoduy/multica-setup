---
name: service-design-template
description: House template for a NEW SERVICE's architecture design — the docs/architect/ file set service-architect writes before the service's first code (identity card, scope and responsibilities, domain model, integration, data, quality attributes, ADRs). The approved design binds every later spec and implementation in that repo. Not for documenting code that exists — that is library-doc-template or api-feature-doc-template.
---

# Service design template

The house shape for one new service's design (Policy 06 statement 14). It is
written before any code exists, lands as ONE `design/<issue-key>` PR on the new
repo's `dev`, and merges only when the owner approves it. After that it is the
contract every spec, impl-brief and PR in the repo is checked against (Policy 06
statement 5c) — write it so an agent that has never seen the ticket can build
from it.

## The file set

```
docs/architect/
├── README.md            identity card + index + delivery slices
├── 01-scope.md          purpose, users, responsibilities, non-goals
├── 02-domain.md         bounded context, language, aggregates, invariants, events, lifecycles
├── 03-integration.md    context map, APIs and events in and out, dependencies, main flows
├── 04-data.md           data ownership, storage, entity tables
├── 05-quality.md        security, observability, performance, packaging and deployment
├── adr/
│   └── 0001-why-a-new-service.md   one file per decision, numbered, never renumbered
└── diagrams/
    └── <name>.<type>.json + <name>.svg   archify IR and its render, side by side
```

Every file is required. A section whose trigger is absent says so in one line
(`None — the service publishes no events.`), never an empty heading and never a
placeholder.

## What a design may name

A design is the agreed architecture, so unlike a spec it names: repos, packages,
the bounded context, aggregates, entities, value objects, fields, domain events,
endpoints (verb + path), message topics and external systems. It never names
code layout: no project folders, layers, handlers, classes outside the domain
names, method signatures or file paths — how the code is laid out is dev-leader's
at decomposition. No code blocks except the file-set tree above and endpoint or
event examples in 03.

Writing rules are the spec's (Policy 06 statement 3a): one idea per sentence,
under 20 words, everyday words, bullets over paragraphs, numbers as digits.

## README.md — identity card

```markdown
# <Service name>

<One sentence: what the service does, for whom.>

| | |
|---|---|
| **Repo** | <repo name> — <github url> |
| **Service name** | <name as it appears in logs, images and config> |
| **Bounded context** | <context name> |
| **Stack** | <runtime + main framework, e.g. .NET 10 / DKNet, from DKNet.Templates> |
| **Status** | Active |
| **Design revision** | <n> |
| **Owner** | <human owner> |
| **Root ticket** | <KEY> |

## Documents
<one line per file above: link + what question it answers>

## Delivery slices
<Ordered list. Each slice = one future Workflow B ticket: a name, one line of
what it delivers, and the design sections it realises. Slice 1 is the scaffold
(repo layout per Policy 01 statement 1, CI, the empty host). No estimates.>
```

`Design revision` starts at 1 and goes up by one on every later Workflow F
ticket. `Status` is `Active`, or `Retired — <why, which repo took over>`.

## 01-scope.md — purpose and boundaries

- **Purpose** — the problem the service solves and who has it today.
- **Users and consumers** — every human role and every calling system.
- **Responsibilities** — what the service owns and decides, one bullet each.
- **Non-goals** — what it deliberately never does, and which repo does it
  instead. Never empty: the non-goals are how the next spec is stopped from
  growing the service into its neighbours.
- **Boundaries** — for each neighbouring repo, the one line that splits the
  work between them.

## 02-domain.md — the model

- **Bounded context** — its name and the one sentence that defines it.
- **Ubiquitous language** — table: term | meaning | not to be confused with.
- **Aggregates** — per aggregate: its root, the entities and value objects
  inside it, its invariants (as properties that must always hold), and which
  other aggregates it references — by id only. .NET/DKNet: open
  `dknet-ddd-conventions` and name things its way.
- **Domain events** — table: event | raised when | carries | consumed by.
- **Lifecycles** — per aggregate with states: every state and every
  transition with its trigger.

Diagrams: a domain-model diagram (aggregates, what each holds, id references
between them), and a state diagram per aggregate that has a lifecycle.

## 03-integration.md — the service among its neighbours

- **Context map** — every neighbour, the direction of each dependency, and how
  they talk (package reference, HTTP, event, shared nothing).
- **Exposed API** — table: verb | path | purpose | auth.
- **Published events** — table: event | topic | payload fields | who listens.
- **Consumed APIs and events** — table: source repo | what | why | what
  happens when it is down. Every row verified in the source repo with CodeGraph.
- **Dependencies** — every package and service the new one depends on, with
  its direction. The direction must fit the stack's layering: a service may
  depend on a library, never the other way round; no cycle between repos.
- **Main flows** — each main use case from trigger to result, failure path
  included.

Diagrams: the context map (architecture), and one sequence diagram per main
flow — at least one.

## 04-data.md — what it stores

- **Ownership** — the data the service owns, and the data it never writes
  (owned elsewhere; read by API or event only).
- **Storage** — the store per aggregate, and why (link the ADR).
- **Entities** — one table per entity in the Policy 06 §3a shape: field | type |
  length or precision | required | unique or indexed | default | notes (enum
  values, unit, currency, personal data).
- **Retention** — how long each kind of record lives, and what deletes it.

Tables, no diagram: archify has no table-schema type, and a Mermaid
`erDiagram` is not used here.

## 05-quality.md — how well it must work

- **Security** — the trust boundaries, who is authenticated how, the
  authorization rule per endpoint group, personal data and where it flows,
  secrets and where they live.
- **Observability** — the health checks, the logs and metrics an operator
  needs, and the correlation id across calls.
- **Performance and scale** — the numbers that matter (requests per second,
  latency, data volume), each with its source. No invented numbers: unknown
  is an open question.
- **Packaging and deployment** — what the service ships as (NuGet package,
  multi-arch container image per Policy 08, Helm chart) and what CI publishes.
- **Testing approach** — which behaviours need integration tests against real
  infrastructure (Policy 02), and which neighbour is faked.

## adr/NNNN-<slug>.md — one per decision

```markdown
# ADR-NNNN: <decision in a few words>

- **Status:** Accepted | Superseded by ADR-NNNN
- **Context:** <the forces, in bullets>
- **Decision:** <what was chosen>
- **Alternatives:** <each option not chosen, and why not>
- **Consequences:** <what gets easier, what gets harder>
```

`ADR-0001` is always **why a new service** instead of growing an existing repo.
Every other choice with a real alternative (storage, sync vs async, a new
dependency) gets its own ADR. A later design revision adds ADRs and marks the
old one superseded; it never edits an accepted decision.

## Diagrams

Every diagram is drawn with archify, never Mermaid — no fallback, no
placeholder. Required: the context map and at least one main flow (03), the
domain model (02), and a lifecycle per stateful aggregate (02). The archify type
for each is your call, using archify's type router. Diagrams show the real names
from this design — never generic boxes ("Service → Database"). Commit the JSON
IR and the rendered `.svg` side by side under `docs/architect/diagrams/`, and
reference the `.svg` with alt text that narrates it in one sentence. archify
will not install, validate or render → `blocked` with the failing command.

## Revising an approved design

Only on a new Workflow F ticket. Bump `Design revision`, add an ADR for every
changed decision, change only the sections the ticket names, and list them in
the PR body. A spec or a code PR never edits `docs/architect/`.

## Self-check before pushing

1. Every file in the set exists; no empty heading, no TODO, no placeholder.
2. Every claim about a neighbouring repo cites the evidence in your report
   (`file:line` from CodeGraph); what you could not verify is an open question
   on your ticket, not a sentence in the design.
3. Non-goals is not empty; every consumed API names its failure behaviour.
4. Every dependency points the way the stack allows, with no cycle.
5. Every entity field has type, required and default; every endpoint has verb,
   path and auth.
6. All required diagrams exist, both IR and `.svg` committed, and
   `git diff origin/dev... | grep -c '^+```mermaid'` prints 0.
7. `git diff --stat` shows `docs/architect/` only.
