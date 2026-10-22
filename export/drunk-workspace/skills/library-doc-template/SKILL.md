---
name: library-doc-template
description: House template for a LIBRARY's docs — a package, Pulumi component or client SDK a developer installs and calls in their own code (DKNet packages, drunk-pulumi-* components). One folder per package — index.md plus one page per feature — and its package README and changelog entry. Not for a feature callers reach over HTTP — that is api-feature-doc-template. Use when docs-writer writes or updates a library or package's docs.
---

# Library doc template

The house shape for one documented package or component: the reader installs it
and calls its types in their own code. Derived from the most developed page in
the fleet, `DKNet/docs/AspNetCore/DKNet.AspCore.Idempotency.md` — reader-task
order, not API order — split into one folder per package so each capability
gets its own page.

Not this template: a feature of a running application that callers reach over
HTTP, a webhook or an MCP tool → `api-feature-doc-template`. This layout wins
over a repo's own library template (today: DKNet's `docs/Package-Doc-Template.md`);
take the repo template's wording and voice only where it does not conflict.

Fill sections in the order shown. Omit a section when its trigger below is
absent; never reorder, never invent a new top-level section, never leave a
heading with placeholder text under it.

## The folder

```text
docs/<Package>/
├── index.md              the package: what, why, Quick Start, architecture, how it works, feature list
├── <feature>.md          one page per capability
└── diagrams/             every diagram's JSON IR + rendered .svg
```

- `docs/` is the repo's existing docs root (`docs/`, `doc/`).
- `<Package>` is the package id exactly as published (`PackageId`, the
  `package.json` name, the Pulumi component name).
- `<feature>.md` follows the repo's existing doc file naming; kebab-case of the
  capability where the repo has none (`replays-a-cached-response.md`).
- One capability per feature page. A package with a single capability still
  gets `index.md` plus one feature page.

## index.md

```markdown
# <Package or component name>

<One sentence: what it does, for whom. No marketing, no history.>

## ✨ Why use it?

<2–5 bullets. Each names a concrete problem the reader has and how this removes
it. A bullet that could describe any library in the repo is a dead bullet.>

## 🚀 Quick Start

<Install line, then the smallest runnable example that produces a visible
result. Copy it from a test or run it — never hand-write it from memory.>

## 🏗️ Architecture

<The component diagram (archify `architecture`): the package's components as
they run inside the host app — the types the reader registers or calls, the
stores, handlers and background parts behind them, the host at the edge, every
external dependency and trust boundary. Then 2–3 sentences on what it cannot
show: lifetimes, what is shared across requests, what runs where.>

## 🔄 How it works

<The flow diagram: what runs when the reader's code makes the Quick Start call,
from that call to the result they see — every step in order, the branch they
hit most (hit or miss, valid or invalid, on or off) and the failure path. Then
2–4 sentences on what the diagram cannot show: defaults, ordering guarantees,
when and where each step runs.>

## 🧩 Features

- [<Capability, phrased as what it does>](<feature>.md) — <one line: what it
  does for the reader>

## 🔗 Related packages

<Sibling packages, with one line on when to reach for each instead.>
```

| Section | Required? | Fails review when |
|---|---|---|
| Title + one-liner | Always | The one-liner restates the package name, or is longer than a sentence |
| ✨ Why use it? | Always | Reads as a feature list instead of the reader's problem |
| 🚀 Quick Start | Always | The example was not run, is missing the install step, or needs unstated setup |
| 🏗️ Architecture | Always | Generic boxes instead of the package's real types; a component, store or external dependency the code has is missing; a single-package repo draws a second copy of `runtime.svg` instead of showing it |
| 🔄 How it works | Always, unless the package is a set of independent one-call helpers with no order, branch or state | The diagram is not the Quick Start call's real path (generic boxes, invented steps), or it leaves out a failure path the code has |
| 🧩 Features | Always | A feature page in the folder is missing from the list; a link that does not resolve; a description that restates the method signature |
| 🔗 Related packages | When siblings exist | Bare links with no "reach for this when" line |

## Feature page

```markdown
# <Capability, phrased as what it does>

Part of [<Package>](index.md). <What it is, the smallest code showing it, then
the behaviour worth knowing (defaults, order, what happens on the unhappy path).
Then this capability's diagram, right after its example, with 1–2 sentences on
what it cannot show.>

## ⚙️ Configuration reference

<Table: option | type | default | effect. Every option this capability reads,
defaults matching the code at this commit.>

## 🧱 Where it fits

<How this capability sits against the other packages/components and the
runtime around it — with an `architecture` diagram when it spans more than one.>

## ⚠️ Gotchas & limits

<What bites people: thread-safety, ordering, cost, unsupported combinations,
what this deliberately does NOT do.>
```

| Section | Required? | Fails review when |
|---|---|---|
| Title + body | Always | No back-link to `index.md`; restates method signatures instead of behaviour; covers more than one capability; no diagram, or one that redraws `index.md` 🔄 How it works |
| ⚙️ Configuration reference | When the capability has options | A default in the table disagrees with the code; an option shared with another feature documented twice instead of linked |
| 🧱 Where it fits | When the capability works across more than one component, service, or package | Prose that a diagram would say better, or a diagram with no prose around it |
| ⚠️ Gotchas & limits | Always, unless the capability is genuinely one behaviour with no edges | Empty, or only restates the happy path |

Emoji-heading note and code-naming rule (point at code by name, never by
line): `references/page-rules.md` (open it before writing and again before
pushing).

## What the repo cannot prove

Library pages carry no ❓ Open questions table (Policy 09). A fact the repo
cannot prove — a supported version range, an intended behaviour the code
contradicts, an owner — is left off the page and raised as an open question on
your ticket. No page states a guess as fact.

## Diagrams

Every package's `index.md` carries two diagrams: the component diagram in
🏗️ Architecture (always archify `architecture`) and the flow or steps diagram
in 🔄 How it works (its section rule names the one exemption). In a repo that
ships only this package, 🏗️ Architecture shows the repo's runtime diagram
(`docs/diagrams/runtime.svg`) when it exists, instead of drawing it twice.

Every feature page carries its own diagram after its example: what that
capability does, drawn from its call path. The archify type is your call at
the time — pick it with archify's type router for the shape the capability has
(steps or a flow, states it moves through, a which-form-do-I-use choice, a
value passing through transforms, a call between parts). How a capability sits
among its siblings goes in its 🧱 Where it fits. One diagram per shape; never
draw the same flow twice. Diagrams live in `docs/<Package>/diagrams/`.

Archify diagram rules (drawn with archify not Mermaid, picking the type via
its type router, naming the real mechanism, committing IR + `.svg`):
`references/page-rules.md`. A Pulumi component's flow is the resources it
creates, in order, each optional one behind the arg that switches it on.

## Two smaller shapes

**Package README** (the repo-root or package-root `README.md`): Title +
one-liner, Why use it?, Quick Start, then a link table into
`docs/<Package>/index.md` and its feature pages. No Features section — it
drifts from the pages that own it. The repo-root README also carries
🏗️ Runtime architecture once the repo has its runtime diagram:
`docs/diagrams/runtime.svg` with alt text that narrates the primary path in one
sentence (Policy 05 statement 3a; the shape and the drawing prompt are in
docs-writer's procedure, and its archify type is always `architecture`).

**Changelog entry**: one line per user-visible change under the version heading,
imperative mood, linking the doc page the change affects. No internal refactors.

## Keep the index in step

These repos navigate by hand-maintained index pages. A page that no index links
to is an orphan and does not count as delivered:

- Every feature page is listed in its package's `index.md` 🧩 Features.
- Every `docs/<Package>/index.md` is linked from the index above it:
  `DKNet` → `docs/README.md`; `drunk-pulumi-*` → `doc/README.md`; anything
  else → whatever `README`/`index` sits above it.

## Existing pages in another shape

A single-file library page (DKNet's `docs/<Area>/<Package>.md`) or an API-dump
page (`drunk-pulumi-azure-components/doc/**/*.md`: Purpose → Dependencies →
Classes → Interfaces → Enums → Exports) — never write a new one. Updating one:
change only what the ticket asks, in the file it is in, in this template's
section shape, and flag the move to `docs/<Package>/` in your report so it can
be scheduled as its own change. Never rewrite a whole page unasked.

## Self-check before pushing

1. Every code sample was run, or copied verbatim from a passing test.
2. Every default, flag, path, and version matches the code at this commit.
3. Every link resolves (relative links included); every feature page is listed
   in `index.md` and links back to it; `index.md` is linked from the index
   above it.
4. Each feature page's Gotchas names at least one real edge, or the capability
   truly has none.
5. `index.md` has its 🏗️ Architecture component diagram and its 🔄 How it
   works flow diagram, and every feature page has its own diagram, each drawn
   from what you traced in the code; every diagram's JSON IR and rendered `.svg` are both
   committed under `docs/<Package>/diagrams/`, and the `.svg` renders in the
   Markdown preview.
6. No guess stated as fact; every fact the repo cannot prove is an open
   question on your ticket.
7. Self-check and docs-only diff proof (no line references on any page;
   `git diff --stat` touches documentation and diagram files only):
   `references/page-rules.md`.
