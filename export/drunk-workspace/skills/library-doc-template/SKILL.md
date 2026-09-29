---
name: library-doc-template
description: House template for a LIBRARY doc page — a package, Pulumi component or client SDK a developer installs and calls in their own code (DKNet packages, drunk-pulumi-* components), plus its package README and changelog entry. Not for a feature callers reach over HTTP — that is api-feature-doc-template.
---

# Library doc template

The house shape for one documented package or component: the reader installs it
and calls its types in their own code. Derived from the most developed page in
the fleet, `DKNet/docs/AspNetCore/DKNet.AspCore.Idempotency.md` — reader-task
order, not API order.

Not this template: a feature of a running application that callers reach over
HTTP, a webhook or an MCP tool → `api-feature-doc-template`. A repo with its own
template for library pages (today: DKNet's `docs/Package-Doc-Template.md`) →
that template, not this one.

Fill sections in this order. Omit a section when its trigger below is absent;
never reorder, never invent a new top-level section, never leave a heading with
placeholder text under it.

## The skeleton

```markdown
# <Package or component name>

<One sentence: what it does, for whom. No marketing, no history.>

## ✨ Why use it?

<2–5 bullets. Each names a concrete problem the reader has and how this removes
it. A bullet that could describe any library in the repo is a dead bullet.>

## 🚀 Quick Start

<Install line, then the smallest runnable example that produces a visible
result. Copy it from a test or run it — never hand-write it from memory.>

## 🔄 How it works

<The flow diagram: what runs when the reader's code makes the Quick Start call,
from that call to the result they see — every step in order, the branch they
hit most (hit or miss, valid or invalid, on or off) and the failure path. Then
2–4 sentences on what the diagram cannot show: defaults, ordering guarantees,
when and where each step runs.>

## 🧩 Features

### <Capability, phrased as what it does>

<What it is, the smallest code showing it, then the behaviour worth knowing
(defaults, order, what happens on the unhappy path). One `###` per capability.
A capability with a flow, states or a which-form-do-I-use choice of its own
gets its own diagram right after its example.>

## ⚙️ Configuration reference

<Table: option | type | default | effect. Every option the public surface
exposes, defaults matching the code at this commit.>

## 🧱 Where it fits

<How it sits against the other packages/components and the runtime around it —
with an `architecture` diagram when it spans more than one.>

## ⚠️ Gotchas & limits

<What bites people: thread-safety, ordering, cost, unsupported combinations,
what this deliberately does NOT do. Never empty on a non-trivial package.>

## 🔗 Related packages

<Sibling packages, with one line on when to reach for each instead.>
```

## Section rules

| Section | Required? | Fails review when |
|---|---|---|
| Title + one-liner | Always | The one-liner restates the package name, or is longer than a sentence |
| ✨ Why use it? | Always | Reads as a feature list instead of the reader's problem |
| 🚀 Quick Start | Always | The example was not run, is missing the install step, or needs unstated setup |
| 🔄 How it works | Always, unless the package is a set of independent one-call helpers with no order, branch or state | The diagram is not the Quick Start call's real path (generic boxes, invented steps), or it leaves out a failure path the code has |
| 🧩 Features | Always | Restates method signatures instead of behaviour; a `###` per method rather than per capability |
| ⚙️ Configuration reference | When the public surface has options | A default in the table disagrees with the code |
| 🧱 Where it fits | When the package works across more than one component, service, or package | Prose that a diagram would say better, or a diagram with no prose around it |
| ⚠️ Gotchas & limits | Always, unless the package is genuinely one behaviour with no edges | Empty, or only restates the happy path |
| 🔗 Related packages | When siblings exist | Bare links with no "reach for this when" line |

Emoji headings are house style on these pages — keep them, exactly as above.

## Diagrams

Every page carries at least one flow or steps diagram, in 🔄 How it works
(Section rules name the one exemption). A capability with a shape of its own —
states it moves through, a which-form-do-I-use choice, a value passing through
transforms — gets its own diagram after its example, and how the package sits
among its siblings goes in 🧱 Where it fits. One diagram per shape; never draw
the same flow twice.

Every diagram is drawn with archify, never Mermaid — even where the repo's own
template offers Mermaid as a fallback.

The archify type is your call: pick the one that best shows what that diagram
must answer, using archify's own type router (its `guide` command settles a
close call). A Pulumi component's flow is the resources it creates, in order,
each optional one behind the arg that switches it on.

Every diagram shows the real mechanism: the type, method, resource and arg
names from the code, never generic boxes ("Service → Database"). Commit both
the JSON IR and the rendered `.svg`, side by side under `docs/diagrams/` (or
the repo's existing diagram folder), and reference the `.svg` from the
Markdown with alt text that narrates the flow in one sentence.

## Two smaller shapes

**Package README** (the repo-root or package-root `README.md`): the same
skeleton truncated to Title + one-liner, Why use it?, Quick Start, then a link
table into the full `docs/` pages. No Features section — it drifts from the doc
page that owns it.

**Changelog entry**: one line per user-visible change under the version heading,
imperative mood, linking the doc page the change affects. No internal refactors.

## Keep the index in step

These repos navigate by hand-maintained index pages. A new page that no index
links to is an orphan and does not count as delivered:

- `DKNet`: the area `README.md` next to the page (e.g. `docs/AspNetCore/README.md`)
  plus `docs/README.md` where it lists areas.
- `drunk-pulumi-*`: the area `index.md` and `doc/README.md`.
- Anything else: whatever `README`/`index` sits above the page.

## API-dump pages — never a new one

`drunk-pulumi-azure-components/doc/**/*.md` use API-dump order (Purpose →
Dependencies → Classes → Interfaces → Enums → Exports). It restates the
TypeScript types the reader can already read and goes stale the moment a
signature changes. Never write a new page in that shape. Updating one: fix what
the ticket asks, in this template's shape, and flag the page's full migration
in your report so it can be scheduled as its own change.

## Self-check before pushing

1. Every code sample was run, or copied verbatim from a passing test.
2. Every default, flag, path, and version matches the code at this commit.
3. Every link resolves (relative links included).
4. Gotchas section names at least one real edge, or the package truly has none.
5. 🔄 How it works has its flow diagram, drawn from the call path you traced in
   the code; every diagram's JSON IR and rendered `.svg` are both committed, and
   the `.svg` renders in the Markdown preview.
6. `git diff --stat` shows documentation and diagram files only.
