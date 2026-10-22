---
name: api-feature-doc-template
description: House template for an APPLICATION's docs — features of a running application that callers reach over HTTP, a webhook or an MCP tool. One folder per feature (index.md with overview, business domain and end-to-end flow, plus endpoints, data model, integration and configuration pages), the app's service README with its runtime architecture, its configuration reference and its deployment guide. Not for an installable package — that is library-doc-template. Use when docs-writer writes or updates an application's docs.
---

# API feature doc template

The house shape for the features of a running application: an accounts
resource, a webhook receiver, an approval flow. The reader calls it over the
wire or runs the service; they never reference its code. They need the routes,
who may call them, what to send, what comes back, what can go wrong — and, for
the maintainer and the partner team, which business rules it enforces, what it
stores, and which other systems it depends on.

Not this template: a package, component or client SDK the reader installs and
calls in their own code → `library-doc-template`, even when the package helps
build APIs (middleware, endpoint-mapping extensions). A UI — screens,
components, a console guide — has no house template yet. This layout wins over
a repo's own feature-doc template (today: the `dknet-docs` set in
DKNet.Templates `plugin/skills/dknet-docs/` and any repo that copied it in);
take the repo template's wording and voice only where it does not conflict.

Fill sections in the order shown. Omit a section or page when its trigger below
is absent; never reorder, never invent a new top-level section, never leave a
heading with placeholder text under it.

## Facts come from the code

- **Routes:** the endpoint mapping, generated routes included (build once and
  read the generated file), minus excluded ones, plus hand-mapped ones. This
  list is the spine of `endpoints.md` and its completeness check.
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
- **Configuration:** the options classes and their validation, the
  `appsettings*.json` files, and the Helm values or compose files that set
  them. Where a value comes from (settings file, environment variable, secret
  store) and when it is read (startup, per request, on reload) come from the
  binding code, never from the key's name.
- **Concurrency:** the concurrency token, ETag or row version the entity
  mapping declares, and the status a stale write gets — or the lock the
  handler takes. Neither means last write wins; say so.
- **Deployment:** the Dockerfile, the Helm chart (values, probes, resources,
  identity), the pipeline YAML, and how migrations reach the database (startup
  migrate, migration bundle, a job). A file that exists is not proof that
  production uses it: say "the chart sets", never "production runs".
- **What the repo cannot tell:** production values, backup and restore,
  recovery time and data-loss window, service objectives, the owning team.
  Never inferred, never invented: each goes in ❓ Open questions.

Code-naming rule (point at code by name, never by line): `library-doc-template`
`references/page-rules.md` (open it before writing and again before pushing).

## The layout

```text
README.md                         the service README: the application's main page
docs/
├── index.md                      GitHub Pages home: the README, links rebased to docs/
├── configuration.md              keys the whole application reads
├── deployment.md                 the deployment guide
├── diagrams/                     runtime architecture + release path (IR + .svg)
└── features/<feature>/
    ├── index.md                  the feature: overview, domain, Quick Start, end-to-end flow, pages
    ├── endpoints.md              every route, errors and limits
    ├── data-model.md             what it stores
    ├── integration.md            events and downstream systems
    ├── configuration.md          keys this feature alone reads
    └── diagrams/                 this feature's diagrams (IR + .svg)
```

- `docs/` is the repo's existing docs root.
- `<feature>` follows the repo's existing doc folder naming; kebab-case of the
  feature name where the repo has none (`accounts`, `approval-flow`).
- Every feature page except `index.md` opens with
  `# <Feature> — <Page>` and the line `Part of [<Feature>](index.md).`

## Feature index.md

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

## 📚 Pages

- [Endpoints](endpoints.md) — <one line: what the reader finds there>
- <one bullet per other page in the folder>

## 🔗 Related features

<Sibling features and the client SDK, if one exists, each with one line on when
to reach for it instead.>

## ❓ Open questions

| Question | Why it matters | Checked | Who can answer |
|---|---|---|---|

<One table for the whole feature folder. What goes in each row:
`library-doc-template` `references/page-rules.md`.>
```

## endpoints.md

```markdown
## 🔌 Endpoints

| Verb | Path | Purpose | Auth |
|---|---|---|---|

### `<VERB> <path>`

<One sentence.>

- **Auth:** <role or scope, and where it is declared — or "anonymous">
- **Idempotency** (write routes): <the header and what a replay returns — or
  "not idempotent: a retry creates a second <thing>">
- **Concurrency** (write routes that change an existing entity): <what the
  caller sends (`If-Match`, a version field) and the status a stale write gets
  — or "none: the last write wins">
- **Request:** a table — Field | Type | Required | Rules | From (body, route,
  query, header, claim)
- **Response:** `<status>` and a JSON example
- **Errors:** a table — Status | Code | When
- **Example:** one runnable `curl` with every required header

## ⚠️ Errors & limits

<The error body shape; paging defaults and caps; rate limits; ordering and
consistency; retry safety; what the feature deliberately does NOT do.>
```

## data-model.md

```markdown
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

<A store that is not a table (a Redis key or list, a blob container): one `###`
per shape, headed by its key pattern or name, with the same table minus Column
and DB type, plus its lifetime and what removes it.>

<Then, each only when the code has it and it is specific to this feature:
cache entries (key, lifetime, what clears them, what a reader sees while
stale) and retention (what deletes or archives rows, and when). How the schema
changes is the same for every feature of one database: it lives once in the
deployment guide's 🗃️ Database changes; link it.>
```

## integration.md

```markdown
## 📣 Events

| Event | Raised when | Payload | Transport | Consumers | Ordering | Duplicates | On failure |
|---|---|---|---|---|---|---|---|

<Ordering: what keeps two events in order, or "none". Duplicates: what a
consumer sees on redelivery and what makes it safe (message id, idempotent
handler). On failure: retries, dead-letter queue, how to replay — with the
replay's side effects — and what happens to an event raised while its
transport is switched off.>

## 🌐 Downstream systems

| System | Direction | How | What for | When it is down |
|---|---|---|---|---|

<Direction: `we call it`, `it consumes our events`, `we consume its events`,
`it calls us`, or `registered, unused` for a client the app wires up but no
handler calls. How: HTTP, queue or topic name, SDK. When it is down: the
timeout, retry and circuit breaker the registered client sets, the fallback, or
"the request fails with <status>". Then the configuration keys that point at
each system.>
```

## configuration.md (feature and application)

```markdown
## ⚙️ Configuration reference

| Key | Type | Required | Default | Rules | Secret | Takes effect | Effect |
|---|---|---|---|---|---|---|---|
```

Rules: range, format, unit or allowed values, from the validator. Secret: `no`,
or `yes — <store>` (Key Vault, Kubernetes secret); a secret's example value is
always a placeholder. Takes effect: `startup` (restart to change), `per
request`, or `on reload`.

The feature's `configuration.md` lists only the keys that feature alone reads.
`docs/configuration.md` (title `# <Service> configuration`) lists the keys the
whole application shares, and says once how a key maps to an environment
variable (`A:B` → `A__B`). A key lives on exactly one page; the others link it.

## Section rules

| Page | Section | Required? | Fails review when |
|---|---|---|---|
| index.md | Title + one-liner | Always | Names the framework or restates the route |
| index.md | 📖 Overview | Always | Lists endpoints instead of what a caller can do; no line on who calls it |
| index.md | 🏢 Business domain | Always | A term the folder uses is missing from the table; a rule no code enforces; the "Enforced by" column names no validator, guard or constraint |
| index.md | 🚀 Quick Start | Always | Not run or copied from a test; the auth step or a required header is missing |
| index.md | 🔄 End-to-end flow | Always | The main-route diagram stops before the database or skips a raised event; not the route's real path (generic boxes, invented hops); the entity has a status whose changes are not drawn; a transition no handler performs; a diagram with no prose |
| index.md | 📚 Pages | Always | A page in the folder is missing from the list, or a link does not resolve |
| index.md | 🔗 Related features | When siblings or a client SDK exist | Bare links with no "reach for this when" line |
| index.md | ❓ Open questions | When any page in the folder needs a fact the repo cannot prove | A guess stated as fact on any page; a row with no "Checked"; a table on a page other than `index.md` |
| endpoints.md | 🔌 Endpoints | Always | A published route has no section; an error the route cannot return; a write route silent on idempotency; a write to an existing entity silent on concurrency |
| endpoints.md | ⚠️ Errors & limits | Always | Empty, or only restates the happy path |
| data-model.md | 🗃️ Data model | When the feature stores data | A column, type, length, key or default disagrees with the entity mapping; a field with no purpose or one that restates the type; a relation missing; a status value no code writes; a non-table store with no lifetime |
| integration.md | 📣 Events | When the feature publishes or consumes a message or webhook | A payload field, transport or consumer that is not in the code; ordering, duplicates or failure handling left blank |
| integration.md | 🌐 Downstream systems | When the feature calls, is called by, or exchanges events with another system | A registered client or bus endpoint missing; no "when it is down" behaviour; a partner no code calls |
| configuration.md | ⚙️ Configuration reference | When the feature (or, for `docs/configuration.md`, the application) reads settings, env vars or flags | A default or rule disagrees with the code; a secret with a real-looking value; no "Takes effect"; a key listed on two pages |

A page whose every section is absent is not written. Emoji-heading note:
`library-doc-template` `references/page-rules.md`.

## Diagrams

Every feature carries at least one flow diagram, in its `index.md`
🔄 End-to-end flow: the feature's main route from the endpoint to the database
and on to the events it raises and their consumers — the write route that best
stands for the feature, or the main read route when it is read-only — with the
refusal a caller hits most as a branch. Two more shapes must be drawn there
when the feature has them: a status that changes over its life (a state
diagram with only the transitions the handlers actually perform), and several
calls a caller must make in a set order. A route whose path differs from the
main one (async hand-off, external call, compensation) gets its own diagram in
`endpoints.md` under its route; an event that travels on after it is raised
may get one in `integration.md`. A feature's diagrams live in
`docs/features/<feature>/diagrams/`.

The application's main page — the service README — carries the repo's runtime
architecture diagram in 🏗️ Runtime architecture (`docs/diagrams/runtime.svg`;
type, IR path and drawing prompt fixed in `references/page-rules.md`). A
deployment guide carries one diagram, in 🔄 Release path: the pipeline's real
stages, artifacts and target environments, under `docs/diagrams/`.

Archify diagram rules (drawn with archify not Mermaid, picking the type via
its type router, naming the real mechanism, committing IR + `.svg`):
`library-doc-template` `references/page-rules.md`. This template's own
exception: a repo template that asks for an `erDiagram` may keep it in
Mermaid — archify has no table-schema type. The flow diagram is typically a
sequence or workflow; a status diagram is typically a lifecycle; a table
schema stays a table.

## Service README

The repo-root `README.md` of an application — its main page. It gets a
newcomer from "what is this" to a working local call; every detail lives on
the page that owns it, and the README links there. Sections, in this order:

- Title + one-liner.
- 📖 Overview: one bullet per feature, each linking its
  `docs/features/<feature>/index.md`, then one line on who calls the
  application.
- 🏗️ Runtime architecture, always: `docs/diagrams/runtime.svg` (a repo that
  committed it under another name: link that file and flag the rename in your
  report), alt text narrating the primary path in one sentence. A repo that
  lacks it: draw it on this ticket (Policy 05 statement 3a; shape and drawing
  prompt in `references/page-rules.md`, archify type always `architecture`).
- 🌐 Downstream systems for the whole application.
- 🚀 Quick Start: from a fresh clone to the running app, then one call. Each
  command names its working directory and what must run first.
- ✅ Verify it works: one request, page or health check, and the exact
  result to expect. Run it, or copy it from a passing test.
- 🛠️ Common commands: restore, build, test, run, format — only commands the
  repo actually has, each with its working directory.
- ⚠️ Known limitations: what a new developer or caller hits first.
- 📚 Documentation: a table of the feature index pages, `docs/configuration.md`
  and the 🚢 deployment guide, one line each on what it answers.
- ❓ Open questions, when the README needs a fact the repo cannot prove
  (owner, support route).

No endpoint sections, no full configuration table — they drift from the page
that owns them.

## Deployment guide

`docs/deployment.md` for an application that ships as an image or a chart. The
reader is an operator with access to the cluster and the pipeline; they never
read the code. They need what ships, how it reaches an environment, how to tell
it worked, and what a rollback does not undo. Skip the guide for a library.

```markdown
# Deploying <service>

<One sentence: what ships and where it runs.>

## 📦 What ships

<The artifacts: image name and tag scheme, chart name and version, where each
is published, which pipeline builds it. Then how to trace one deployment back:
commit → image tag → chart version.>

## 🔄 Release path

<The diagram: commit → pipeline stages → artifacts → environment, drawn from
the pipeline YAML. A step a human does by hand (promote `dev` to `main`, run
`helm upgrade`) is drawn as a manual step, set apart from the automated ones.
Then: Stage | Trigger | What it does | Gate. Then the environments the repo
names, and what differs between them; a repo that names none says so and asks
in ❓ Open questions — never invent `staging` or `prod`.>

## 🧱 Runtime shape

<What the chart creates: workloads, replicas, ports, identity, resources. Each
probe and exactly what it checks. What must already exist in the cluster or
the subscription before install (stores, queues, secrets, identities, a
gateway).>

## ⚙️ Configuration and secrets

<How settings reach the pod (chart values → environment variables, a secret
store mount) and who supplies each secret. Link `docs/configuration.md`;
never copy its table.>

## 🗃️ Database changes

<The migration tool, who applies migrations, when, and whether the previous
version still runs on the new schema. Only when the application stores data;
feature pages link here instead of repeating it.>

## 🚀 Deploy

<The supported procedure: the pipeline to run or the exact commands, every
required input, and the side effects. A command that restarts, migrates or
deletes says so.>

## ✅ Verify

<The checks after a deploy: health endpoints, one smoke call and its expected
result, the logs or metrics to watch and for how long.>

## ↩️ Roll back

<When to roll back, the procedure, and what it does NOT undo: applied
migrations, sent messages, written data.>

## 🧯 When a deploy fails

| What you see | Likely cause | What to do |
|---|---|---|

<Failed rollout, failing probe, failed migration, missing secret or dependency —
only causes the chart, the startup code or the pipeline can produce.>

## ❓ Open questions
```

| Section | Required? | Fails review when |
|---|---|---|
| 📦 What ships | Always | An artifact name or tag scheme not in the pipeline; no trace from commit to deployment |
| 🔄 Release path | Always | No diagram, or one not drawn from the pipeline YAML; a stage or gate the pipeline lacks |
| 🧱 Runtime shape | Always | A probe described by name only, not by what it checks; a precondition missing that startup refuses to run without |
| ⚙️ Configuration and secrets | Always | A copied configuration table; a secret with a real-looking value |
| 🗃️ Database changes | When the application stores data | Silent on who applies migrations or on old-version compatibility |
| 🚀 Deploy | Always | A step with an unstated input or side effect |
| ✅ Verify | Always | No expected result; a check the service does not expose |
| ↩️ Roll back | Always | Silent on what a rollback leaves behind |
| 🧯 When a deploy fails | Always | A cause the code cannot produce |
| ❓ Open questions | When the guide needs a fact the repo cannot prove | Production state stated as fact from a repo file |

One authoritative place: a page that already covers part of this (an operator
guide, the chart's README) is linked or reshaped into this guide, never copied.
Describe deploy commands; never run them — a documentation ticket authorises no
deploy, migration or replay.

## Keep the index in step

A page that no index links to is an orphan and does not count as delivered:

- The service README has its GitHub Pages copy, `docs/index.md`
  (`library-doc-template` `references/page-rules.md`, **GitHub Pages**).

- Every feature page is listed in its feature's `index.md` 📚 Pages and links
  back to it.
- Every feature `index.md`, `docs/configuration.md` and the deployment guide
  are linked from the service README's 📚 Documentation table, and from the
  `docs/README.md` or `docs/index.md` when the repo has one.

## Existing pages in another shape

A single-file feature page, or a feature folder in another file set (the
`dknet-docs` five files) — never write a new one. Updating one: change only
what the ticket asks, in the file it is in, in this template's section shape,
and flag the move to `docs/features/<feature>/` in your report so it can be
scheduled as its own change. Never rewrite a whole page unasked.

## Self-check before pushing

1. The `endpoints.md` 🔌 Endpoints table matches the routes the app publishes,
   generated ones included, and each route has its own section.
2. Every request, response and `curl` was run, or copied from a passing test.
3. Every status in an Errors table is one the route can return; every default
   matches the code at this commit.
4. Every link and anchor resolves, checked by a script, not by eye: emoji
   headings make GitHub slugs easy to get wrong. Every feature page is in its
   `index.md` 📚 Pages and links back; every feature `index.md` is in the
   README's 📚 Documentation table; `docs/index.md` matches the README (the
   diff in `library-doc-template` `references/page-rules.md`, **GitHub Pages**).
5. Each feature `index.md` 🔄 End-to-end flow draws the main route from the
   endpoint through the tables it writes to the events it raises, plus the
   status changes when the entity has a status and the caller's steps when the
   feature takes several calls in order — each drawn from the code path you
   traced; every diagram's JSON IR and rendered `.svg` are both committed in
   its `diagrams/` folder, and the `.svg` renders in the Markdown preview.
6. The README's 🏗️ Runtime architecture shows `docs/diagrams/runtime.svg`,
   drawn on this ticket if the repo lacked it, and it passes the validation in
   docs-writer's procedure.
7. Every `data-model.md` row matches the entity mapping or latest migration —
   column, type, length, key, default — and carries a purpose.
8. Every term in 🏢 Business domain is used in the folder, and every rule names
   what enforces it.
9. `integration.md` 🌐 Downstream systems lists every registered client and bus
   endpoint the feature touches, each with its "when it is down" behaviour.
10. Self-check and docs-only diff proof (no line references on any page;
    `git diff --stat` touches documentation and diagram files only):
    `library-doc-template` `references/page-rules.md`.
11. Every fact the repo cannot prove is a row in the feature `index.md`
    ❓ Open questions (or the README's or deployment guide's own table), never
    a sentence elsewhere; every config row has Required, Rules, Secret and
    Takes effect; no key is on two pages; no secret has a real-looking value.
12. A deployment guide's 🔄 Release path diagram is drawn from the pipeline
    YAML, ↩️ Roll back names what it leaves behind, and no deploy command was
    run.
