# Page rules shared by api-feature-doc-template and library-doc-template

Canonical wording for the blocks both doc templates repeat near-verbatim.
Open this before writing a page and again before pushing.

## Point at code by name, never by line

**Point at code by name, never by line.** Name the class or type (`AuthConfig`),
or the folder that holds it (`ApiEndpoints/DKNet.Notification.Api/Configs/Auth/`).
A file path is fine when the file itself is the subject (`appsettings.json`,
`Program.cs`). Never a line number or line range (`AuthConfig.cs:28-29`,
`#L28`): every edit to the file moves its lines, and the page goes stale with
nobody noticing. Line-level evidence belongs in the archify IR's `evidence` and
in your completion report, never on the page.

## Diagram rules (archify)

Every diagram is drawn with archify, never Mermaid — even where the repo's own
template offers Mermaid as a fallback.

The archify type is your call: pick the one that best shows what that diagram
must answer, using archify's own type router (its `guide` command settles a
close call). One diagram per shape; never draw the same flow twice.

Every diagram shows the real mechanism — the route, handler, table, queue,
event, partner-system, type, method, resource and arg names from the code,
never generic boxes ("Service → Database"). Commit both the JSON IR and the
rendered `.svg`, side by side under the diagram folder the template names
(`library-doc-template`: `docs/<Package>/diagrams/`; `api-feature-doc-template`:
`docs/features/<feature>/diagrams/`; repo-wide diagrams: `docs/diagrams/`), and reference the `.svg` from the Markdown with alt text that
narrates the flow in one sentence.

Each template's own `## Diagrams` section still states its own triggers (which
section carries the required diagram, which capability or route gets its own)
and its own typical archify type — that part is not shared and stays there.

## Section-rules note

Emoji headings are house style on these pages — keep them, exactly as above.

## ❓ Open questions

`api-feature-doc-template` only: one table per feature, in its `index.md`,
plus the service README's and the deployment guide's own. Library pages carry
no table (Policy 09): a fact the repo cannot prove is left off the page and
raised as an open question on the ticket.

```markdown
## ❓ Open questions

| Question | Why it matters | Checked | Who can answer |
|---|---|---|---|
```

One row per fact the page needs and the repo cannot prove: a production
value, a retention or recovery target, a supported version range, an owner,
an intended behaviour the code contradicts. Checked: what you read before
giving up. The rest of the page never states a guess as fact.

Section-rules table row (`api-feature-doc-template`):
`| index.md | ❓ Open questions | When any page in the folder needs a fact the repo cannot prove | A guess stated as fact on any page; a row with no "Checked"; a table on a page other than `index.md` |`

## Self-check items (both run on every push)

- No line references on the page: `git diff origin/dev... -- '*.md' | grep -E '^\+.*\.(cs|ts|tsx|js|py|json|ya?ml|csproj|props|targets|sh|bicep|tf)(:[0-9]+|#L[0-9]+)'`
  prints nothing.
- `git diff --stat` shows documentation and diagram files only.

## GitHub Pages: docs/index.md

`docs/` must serve as a GitHub Pages site (deploy from the branch's `/docs`
folder). Pages builds with Jekyll in safe mode, which ignores symlinks, and
the repo-root `README.md` lies outside `docs/`. So every repo carries
`docs/index.md`: a real file, never a symlink, with the same text as the
repo-root `README.md` and every relative link and image path rebased to
`docs/` (`docs/features/x/index.md` → `features/x/index.md`,
`docs/diagrams/runtime.svg` → `diagrams/runtime.svg`, `LICENSE` →
`../LICENSE`). Change one, change the other in the same commit. A repo that
already has a `docs/README.md` index keeps it, linked from the README's
documentation links; `docs/index.md` is the site's home page.

Self-check: the two files match apart from link targets —
`diff <(sed -E 's/\]\([^)]*\)/]()/g' README.md) <(sed -E 's/\]\([^)]*\)/]()/g' docs/index.md)`
prints nothing — and every link in `docs/index.md` resolves.

## Which template

Classify each page by what its reader does with the thing. Decide from the code, not the repo name — one repo can hold both kinds (DKNet.Accounts.Api ships an API and its client package):
- **Library** — the reader installs a package (NuGet, npm, Pulumi component, client SDK) and calls its types in their own code; a packable project (`PackageId`, a published `package.json`) → `library-doc-template`. A package that helps others build an API (middleware, endpoint-mapping extensions) is still a library.
- **API feature** — the reader calls a running application over HTTP, a webhook or an MCP tool; a host project that maps routes (`Map*`, `[Http*]`, controllers, routers) → `api-feature-doc-template`, which also owns an application's repo-root README, its `docs/configuration.md` and its `docs/deployment.md` guide.
- **Both** (an endpoint and its client SDK method) → one page each, each in its own template. **Neither** (how-to guide, ADR, migration note, a guide to the template or platform itself, changelog) → the existing page's shape; nothing to follow → ask on your ticket before writing. **UI** (screens, components, a console guide) has no template yet: follow the existing page's shape.

Then look for the repo's own template: `git ls-files | grep -iE '(^|/)docs?/_?templates?/|(^|/)[^/]*doc[^/]*template[^/]*\.md$|skills/[^/]*docs?[^/]*/templates/'`. The house folder layout wins over it for both kinds — today DKNet's `docs/Package-Doc-Template.md` (library pages) and the `dknet-docs` set in DKNet.Templates or a repo that copied it in (API features); take the repo template's wording and voice only where it does not conflict. Open the house template in full before writing — with the Skill tool, never from memory — and the repo template, if any, for its wording; the house template owns the section order, section rules, which diagrams a page carries and the index page — never the drawing tool (Diagram rules above), whatever it says about Mermaid. An existing page in another shape: change only what the ticket asks, in the chosen shape, and flag the page's migration in your report — never rewrite a whole page unasked. Place new pages where the repo already keeps docs (`docs/`, `doc/`, package-level `README`).
## Flow diagrams

Every library package (its `index.md`) and every API feature (its `index.md`) carries at least one flow or steps diagram, placed where the chosen template says (house templates: 🔄 How it works in `library-doc-template`'s `index.md`, 🔄 End-to-end flow in `api-feature-doc-template`'s feature `index.md`). Every main page also carries a component diagram — a library's `index.md` 🏗️ Architecture, an application's README 🏗️ Runtime architecture — and every library feature page its own diagram. The template says what each diagram must show; the archify type is your call — pick the one that shows it best, with archify's type router. Draw it from the path CodeGraph traced, never generic boxes: author the typed JSON IR, validate, render. Commit BOTH the IR source and the exported asset so the diagram stays regenerable — `<diagram folder>/<name>.<type>.json` plus the rendered `.svg` referenced from the Markdown (diagram folder: Diagram rules above). Static by default; motion only if asked. One diagram per idea.

## Runtime architecture diagram

**The repo's runtime architecture diagram** — one per repo (Policy 05 statement 3a). An application docs ticket draws it when the repo lacks it — the service README is the application's main page and carries it; a library docs ticket draws it only when the ticket asks. Its type is fixed, not your call: archify `architecture`, IR `docs/diagrams/runtime.architecture.json`, render `docs/diagrams/runtime.svg`, linked from the repo-root README's 🏗️ Runtime architecture section (`library-doc-template` / `api-feature-doc-template` README shapes). Brief yourself with this prompt, verbatim:

> Analyze this repository, then use archify to create a high-level runtime architecture diagram.
> Show 8–12 core components, one primary path, external dependencies, and trust boundaries.
> Put supporting detail in cards instead of adding more edges.

"Analyze" is your CodeGraph research step: every component, the primary path and every external dependency come from what CodeGraph traced, under their real names. A library runs inside its consumer's process: draw the package's components as they run in the host app, with the host at the edge. Trust boundaries are archify `boundaries`; ports, config keys, auth and failure behaviour go in `cards`, never in extra edges. A repo whose `dev` holds `docs/architect/diagrams/runtime.architecture.json` was defined at design time: read it first, draw yours from the code, and list every component, dependency or boundary that differs in your report as a design question for the owner — never redraw the code to match the design, and never edit `docs/architect/`.

**archify is the only drawing tool — never Mermaid.** Not as a repo template's fallback, not because the ticket needs many diagrams, not as a placeholder "pending an archify render". The one exception: an `erDiagram` a repo template asks for may stay Mermaid — archify has no table-schema type. archify will not install, validate or render → flip `blocked` with the failing command and its error, never fall back. A Mermaid diagram already in a section you change is redrawn in archify (archify takes the Mermaid source as input) and its block deleted; one elsewhere on the page stays and is listed in your report.
