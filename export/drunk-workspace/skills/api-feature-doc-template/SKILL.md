---
name: api-feature-doc-template
description: House template for an API FEATURE doc page — a feature of a running application that callers reach over HTTP, a webhook or an MCP tool (overview, business domain, end-to-end flow from endpoint to database and events, endpoints, entity fields at database level, downstream systems), plus the app's service README. Not for an installable package — that is library-doc-template.
---

# API feature doc template

The house shape for one feature of a running application: an accounts resource,
a webhook receiver, an approval flow. The reader calls it over the wire or runs
the service; they never reference its code. They need the routes, who may call
them, what to send, what comes back, what can go wrong — and, for the
maintainer and the partner team, which business rules it enforces, what it
stores, and which other systems it depends on.

Not this template: a package, component or client SDK the reader installs and
calls in their own code → `library-doc-template`, even when the package helps
build APIs (middleware, endpoint-mapping extensions). A UI — screens,
components, a console guide — has no house template yet. A repo with its own
template for feature docs (today: the `dknet-docs` set in DKNet.Templates
`plugin/skills/dknet-docs/` and DKNet.Accounts.Api `.agents/skills/dknet-docs/`
— five files under `docs/features/<feature>/`) → that template for the feature
pages; the **Service README** below still shapes the repo-root README unless
that template defines one.

Fill sections in this order. Omit a section when its trigger below is absent;
never reorder, never invent a new top-level section, never leave a heading with
placeholder text under it.

## Facts come from the code

- **Routes:** the endpoint mapping, generated routes included (build once and
  read the generated file), minus excluded ones, plus hand-mapped ones. This
  list is the spine of the page and its completeness check.
- **Request and response:** the bound request type and the returned DTO;
  validation rules from the validator or annotations, and whether that route
  actually enforces them.
- **Errors:** only the statuses the handler, its filters and the pipeline can
  return on that route.
- **The spec's §3a Contract changes** lists the endpoints and fields the change
  was meant to add, in the same columns as the tables below. Where §3a and the
  code disagree, the code is what ships: document the code and raise the gap on
  your ticket.
- **Business domain:** the aggregate and entity names, the guard clauses and
  domain methods that enforce a rule, and the spec's §1–§3 for the words the
  business uses. A rule no code enforces is not a rule of the feature.
- **Stored data:** the entity mapping (EF Core configurations, migrations, or
  the ORM's schema) for table and column names, database types, lengths,
  nullability, keys, indexes and defaults — never the C# property alone.
- **Downstream systems:** registered HTTP and typed clients, SDK clients,
  message-bus publishers and consumers, and the configuration keys holding
  their addresses. A partner no code calls is not a dependency.

## The skeleton

```markdown
# <Feature name>

<One sentence: what a caller can do with it, in business words. No framework
names, no route.>

## 📖 Overview

<2–5 bullets. Each names something a caller can do or rely on, and the business
rule behind it ("A posting is never edited; a mistake is corrected by a
reversing posting"). A bullet that lists an endpoint is a dead bullet. Then one
line on who calls it (end user app, partner system, back office).>

## 🏢 Business domain

<Where the feature sits: the business area it belongs to and the one next to
it that it must not overlap. Then the terms a reader must share with the
business, and the rules the feature enforces.>

| Term | Meaning | In the code |
|---|---|---|

| Rule | Enforced by | A caller who breaks it gets |
|---|---|---|

## 🚀 Quick Start

<The most common call end to end: how to get a token (or "no auth"), one request
with every required header, the real response. Copied from an integration or
acceptance test, or run against a local instance — never written from memory.>

## 🔄 End-to-end flow

<The main route from the endpoint to the database and out again: caller →
endpoint → validation → handler → domain → the tables written → the events
raised → who consumes them, with the refusal a caller hits most as an
alternative branch. Then the entity's status changes when it has a status, and
the caller's steps when using the feature takes several calls in a set order.
Each diagram is followed by a short paragraph on what it cannot show:
transaction boundary, what happens when the event publish fails, what is
eventually consistent.>

## 🔌 Endpoints

| Verb | Path | Purpose | Auth |
|---|---|---|---|

### `<VERB> <path>`

<One sentence.>

- **Auth:** <role or scope, and where it is declared — or "anonymous">
- **Idempotency** (write routes): <the header and what a replay returns — or
  "not idempotent: a retry creates a second <thing>">
- **Request:** a table — Field | Type | Required | Rules | From (body, route,
  query, header, claim)
- **Response:** `<status>` and a JSON example
- **Errors:** a table — Status | Code | When
- **Example:** one runnable `curl` with every required header

## 🗃️ Data model

### <Entity> — `<schema.table>`

<One sentence: what one row is, in business words.>

| Field | Column | DB type | Length / precision | Required | Key / index | Default | Purpose |
|---|---|---|---|---|---|---|---|

<Key / index: `PK`, `FK → <Entity>.<Field>`, `unique`, `indexed (<name>)`.
Purpose: why the field exists — the business question it answers or the rule
it serves — never its type restated. Then the relations
(`<Entity> 1 — n <Entity>` via `<FK>`, on delete `<rule>`), the concurrency
token and soft-delete or audit columns when the entity has them, and, when the
entity has a status: Value | Meaning | Reached by | Next.>

## 📣 Events

| Event | Raised when | Payload | Transport | Consumers |
|---|---|---|---|---|

## 🌐 Downstream systems

| System | Direction | How | What for | When it is down |
|---|---|---|---|---|

<Direction: `we call it`, `it consumes our events`, `we consume its events`,
`it calls us`. How: HTTP, queue or topic name, SDK. When it is down: timeout,
retry, circuit breaker, fallback, or "the request fails with <status>". Then
the configuration keys that point at each system.>

## ⚙️ Configuration reference

| Key | Type | Default | Effect |
|---|---|---|---|

## ⚠️ Errors & limits

<The error body shape; paging defaults and caps; rate limits; ordering and
consistency; retry safety; what the feature deliberately does NOT do.>

## 🔗 Related features

<Sibling features and the client SDK, if one exists, each with one line on when
to reach for it instead.>
```

## Section rules

| Section | Required? | Fails review when |
|---|---|---|
| Title + one-liner | Always | Names the framework or restates the route |
| 📖 Overview | Always | Lists endpoints instead of what a caller can do; no line on who calls it |
| 🏢 Business domain | Always | A term the page uses is missing from the table; a rule no code enforces; the "Enforced by" column names no validator, guard or constraint |
| 🚀 Quick Start | Always | Not run or copied from a test; the auth step or a required header is missing |
| 🔄 End-to-end flow | Always | The main-route diagram stops before the database or skips a raised event; not the route's real path (generic boxes, invented hops); the entity has a status whose changes are not drawn; a transition no handler performs; a diagram with no prose |
| 🔌 Endpoints | Always | A published route has no section; an error the route cannot return; a write route silent on idempotency |
| 🗃️ Data model | When the feature stores data | A column, type, length, key or default disagrees with the entity mapping; a field with no purpose or one that restates the type; a relation missing; a status value no code writes |
| 📣 Events | When the feature publishes or consumes a message or webhook | A payload field, transport or consumer that is not in the code |
| 🌐 Downstream systems | When the feature calls, is called by, or exchanges events with another system | A registered client or bus endpoint missing; no "when it is down" behaviour; a partner no code calls |
| ⚙️ Configuration reference | When the feature reads settings, env vars or flags | A default disagrees with the code |
| ⚠️ Errors & limits | Always | Empty, or only restates the happy path |
| 🔗 Related features | When siblings or a client SDK exist | Bare links with no "reach for this when" line |

Emoji headings are house style on these pages — keep them, exactly as above.

## Diagrams

Every page carries at least one flow diagram, in 🔄 End-to-end flow: the
feature's main route from the endpoint to the database and on to the events it
raises and their consumers — the write route that best stands for the feature,
or the main read route when it is read-only — with the refusal a caller hits
most as a branch. Two more shapes must be drawn when the feature has them: a
status that changes over its life (a state diagram with only the transitions
the handlers actually perform), and several calls a caller must make in a set
order. A route whose path differs from the main one (async hand-off, external
call, compensation) gets its own diagram in its 🔌 Endpoints section; an event
that travels on after it is raised may get one in 📣 Events.

Every diagram is drawn with archify, never Mermaid — even where the repo's own
template offers Mermaid as a fallback. Only an `erDiagram` a repo template asks
for may stay Mermaid: archify has no table-schema type.

The archify type is your call: pick the one that best shows what that diagram
must answer, using archify's own type router (its `guide` command settles a
close call) — typically a sequence or workflow for the flow, a lifecycle for
the status. A table schema stays a table. One diagram per shape; never draw the
same flow twice.

Every diagram shows the real mechanism: the route, handler, table, queue,
event and partner-system names from the code, never generic boxes
("Service → Database"). Commit both the JSON IR and the rendered `.svg`, side
by side under `docs/diagrams/` (or the repo's existing diagram folder), and
reference the `.svg` from the Markdown with alt text that narrates the flow in
one sentence.

## Service README

The repo-root `README.md` of an application: Title + one-liner, 📖 Overview
(one bullet per feature, each linking its page), 🏗️ Runtime architecture (once
the repo has one: its `docs/diagrams/runtime.svg`, alt text narrating the primary path in one
sentence — Policy 05 statement 3a; shape and drawing prompt in docs-writer's
procedure, archify type always `architecture`), 🌐 Downstream systems for the
whole application, 🚀 Quick Start (run it locally,
then one call), a link to the configuration reference, then a table of the
feature pages. No endpoint sections — they drift from the feature page that
owns them.

## Keep the index in step

A new feature page that no index links to is an orphan and does not count as
delivered: link it from the service README's feature table and from the
`docs/README.md` or `docs/index.md` that sits above it.

## Self-check before pushing

1. The 🔌 Endpoints table matches the routes the app publishes, generated ones
   included, and each route has its own section.
2. Every request, response and `curl` was run, or copied from a passing test.
3. Every status in an Errors table is one the route can return; every default
   matches the code at this commit.
4. Every link resolves (relative links included).
5. 🔄 End-to-end flow draws the main route from the endpoint through the tables
   it writes to the events it raises, plus the status changes when the entity
   has a status and the caller's steps when the feature takes several calls in
   order — each drawn from the code path you traced; every diagram's JSON IR
   and rendered `.svg` are both committed, and the `.svg` renders in the
   Markdown preview.
6. Every 🗃️ Data model row matches the entity mapping or latest migration —
   column, type, length, key, default — and carries a purpose.
7. Every term in 🏢 Business domain is used on the page, and every rule names
   what enforces it.
8. 🌐 Downstream systems lists every registered client and bus endpoint the
   feature touches, each with its "when it is down" behaviour.
9. `git diff --stat` shows documentation and diagram files only.
