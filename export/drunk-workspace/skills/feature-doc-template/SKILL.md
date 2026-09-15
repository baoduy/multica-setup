---
name: feature-doc-template
description: The house template for a feature/package documentation page in the baoduy open-source repos (DKNet .NET packages, drunk-pulumi TypeScript components) — section order, what each section must contain, when a section is omitted, and which archify diagram belongs where. Use when writing or restructuring any feature doc, package README, or docs/ page in those repos.
---

# Feature doc template

The house shape for one documented feature or package. Derived from the most
developed page in the fleet, `DKNet/docs/AspNetCore/DKNet.AspCore.Idempotency.md`
— reader-task order, not API order.

Fill sections in this order. Omit a section when its trigger below is absent;
never reorder, never invent a new top-level section, never leave a heading with
placeholder text under it.

## The skeleton

```markdown
# <PackageName or Feature Name>

<One sentence: what it does, for whom. No marketing, no history.>

## ✨ Why use it?

<2–5 bullets. Each names a concrete problem the reader has and how this removes
it. A bullet that could describe any library in the repo is a dead bullet.>

## 🚀 Quick Start

<Install line, then the smallest runnable example that produces a visible
result. Copy it from a test or run it — never hand-write it from memory.>

## 🧩 Features

### <Capability, phrased as what it does>

<What it is, the smallest code showing it, then the behaviour worth knowing
(defaults, order, what happens on the unhappy path). One `###` per capability.>

## ⚙️ Configuration reference

<Table: option | type | default | effect. Every option the public surface
exposes, defaults matching the code at this commit.>

## 🧱 Where it fits

<How it sits against the other packages/components and the runtime around it.
This is where the archify diagram goes.>

## ⚠️ Gotchas & limits

<What bites people: thread-safety, ordering, cost, unsupported combinations,
what this deliberately does NOT do. Never empty on a non-trivial feature.>

## 🔗 Related packages

<Sibling packages, with one line on when to reach for each instead.>
```

## Section rules

| Section | Required? | Fails review when |
|---|---|---|
| Title + one-liner | Always | The one-liner restates the package name, or is longer than a sentence |
| ✨ Why use it? | Always | Reads as a feature list instead of the reader's problem |
| 🚀 Quick Start | Always | The example was not run, is missing the install step, or needs unstated setup |
| 🧩 Features | Always | Restates method signatures instead of behaviour; a `###` per method rather than per capability |
| ⚙️ Configuration reference | When the public surface has options | A default in the table disagrees with the code |
| 🧱 Where it fits | When the feature spans more than one component, service, or package | Prose that a diagram would say better, or a diagram with no prose around it |
| ⚠️ Gotchas & limits | Always, unless the feature is genuinely one behaviour with no edges | Empty, or only restates the happy path |
| 🔗 Related packages | When siblings exist | Bare links with no "reach for this when" line |

Emoji headings are house style on these pages — keep them, exactly as above.

## Which archify diagram

One diagram maximum per doc unless the reader genuinely needs two. Commit both
the JSON IR and the rendered `.svg`, side by side under `docs/diagrams/` (or the
repo's existing diagram folder), and reference the `.svg` from the Markdown.

| The doc explains | archify type |
|---|---|
| How components/services/stores wire together | `architecture` |
| A request's path across processes, with responses | `sequence` |
| Steps, decisions, retries in a pipeline or runbook | `workflow` |
| Where data moves and what transforms it | `dataflow` |
| The states a thing moves through and its terminal outcomes | `lifecycle` |

No diagram when the feature is one call with one outcome — a paragraph wins.

## Two smaller shapes

**Package README** (the repo-root or package-root `README.md`): the same
skeleton truncated to Title + one-liner, Why use it?, Quick Start, then a link
table into the full `docs/` pages. No Features section — it drifts from the doc
page that owns it.

**Changelog entry**: one line per user-visible change under the version heading,
imperative mood, linking the doc page the change affects. No internal refactors.

## Precedence — an in-repo template wins

Before writing, look for a documentation template the target repo already owns
(`.github/skills/**/templates/`, `docs/_templates/`, a `CONTRIBUTING.md` docs
section). If one exists for the kind of doc you are writing, follow it and skip
this template. Known cases:

| Repo | Doc kind | Follow |
|---|---|---|
| `DKNet` | library/package page under `docs/<Area>/<Package>.md` | this template |
| `DKNet.Templates` | application feature/vertical-slice docs | the repo's own `.github/skills/dknet-feature-documentation/templates/` set (README / api-reference / architecture / data-model / events) |
| `DKNet.Templates` | template usage and sample docs (`docs/template-usage.md`, `docs/samples/**`) | the existing page's shape |
| `drunk-pulumi-*` | component page under `doc/<area>/<Name>.md` | this template (see the conflict note below) |

Never write a fifth shape. If neither this template nor an in-repo one fits the
doc you were asked for, say so on the ticket before writing.

## Keep the index in step

These repos navigate by hand-maintained index pages. A new page that no index
links to is an orphan and does not count as delivered:

- `DKNet`: the area `README.md` next to the page (e.g. `docs/AspNetCore/README.md`)
  plus `docs/README.md` where it lists areas.
- `drunk-pulumi-*`: the area `index.md` and `doc/README.md`.
- Anything else: whatever `README`/`index` sits above the page.

## Conflict in the current fleet — resolved

Three shapes exist today:

- **This template** (`DKNet/docs/AspNetCore/*.md`) — reader-task order. Adopted.
- **API-dump order** (`drunk-pulumi-azure-components/doc/**/*.md`: Purpose →
  Dependencies → Classes → Interfaces → Enums → Exports) — restates the
  TypeScript types the reader can already read, and goes stale the moment a
  signature changes. **Do not write new pages in this shape.**
- **DKNet.Templates' own set** (`.github/skills/dknet-feature-documentation/templates/*`)
  — a good fit for application feature docs, and it already asks for the
  sequence / component / state-machine / event-flow diagrams archify renders.
  Keep it for that repo (see Precedence above). Note it currently exists in
  three copies — `.claude/skills/`, `.github/skills/dknet-feature-documentation/`,
  and a stale `.github/skills/feature-documentation/skill.md`. Read the
  `.github/skills/dknet-feature-documentation/` copy; flag the duplication on
  the ticket rather than fixing it inside a doc change.

When updating an existing API-dump page, do not silently rewrite the whole file:
add or fix what the ticket asks for in this template's shape, and flag the
page's full migration on the ticket so it can be scheduled as its own change.


## Self-check before pushing

1. Every code sample was run, or copied verbatim from a passing test.
2. Every default, flag, path, and version matches the code at this commit.
3. Every link resolves (relative links included).
4. Gotchas section names at least one real edge, or the feature truly has none.
5. Diagram: JSON IR and rendered asset both committed, and the `.svg` renders in
   the Markdown preview.
6. `git diff --stat` shows documentation and diagram files only.
