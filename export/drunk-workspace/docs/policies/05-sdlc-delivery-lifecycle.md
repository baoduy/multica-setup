# Policy 05 — SDLC Delivery Lifecycle

| | |
|---|---|
| **Policy ID** | DRK-POL-05 |
| **Version** | 1.14 |
| **Status** | Active |
| **Owner** | product-owner |
| **Applies to** | Every ticket that flows through the drunk software factory |
| **Related skills** | [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) · [`sdlc-flow-po-orchestration`](../../skills/sdlc-flow-po-orchestration/SKILL.md) · [`sdlc-flow-squad-leader-playbook`](../../skills/sdlc-flow-squad-leader-playbook/SKILL.md) · [`sdlc-flow-squad-worker-playbook`](../../skills/sdlc-flow-squad-worker-playbook/SKILL.md) |
| **Enforced at** | product-owner orchestration + the review gates |

> **Authority.** This policy is the source of truth for the delivery flow. The
> `sdlc-flow-*` skills **implement** it — stages, ownership, and branch handoffs derive
> from it. Amend this policy first, then cascade — see
> [change control](00-policies-index.md#change-control).

## Delivery lifecycle at a glance

```
   FEATURE (Workflow B)
   👤 ticket ─▶ 🦊 intake/clarify (0 open Qs) ─▶ 6-section SPEC ─▶ [S#] SPEC GATE
        │                                                              │ APPROVED
        ▼                                                              ▼
   [P#-1] DEV cycle: Branch▶Build(TDD, ≥80% cov)▶PR▶🦅 PR GATE (merges to dev)
        │
        ▼
   [P#-2] release dev▶main (release-manager opens+merges; a critical release waits for the owner) ─▶ CI publishes
        │
        ▼
   MAIN TICKET done — TERMINAL. No SANDBOX, no BDD stage, no deploy: publishing IS release.

   BUG (A): research ─▶ root-cause + confidence  ≥90% auto-delegate C · <90% requester confirms
   CI/CD (D): devops only — no spec gate, but still 🦅 PR GATE on the standalone chore/<key> PR
   DOCS (E):  docs-writer only, and only when a human asks — no spec gate, 🦅 PR GATE on the standalone docs/<key> PR
   DESIGN (F): new service only — 🦊 clarify → empty repo → service-architect's design/<key> PR → 🦅 PR GATE → 👤 owner approves → merge

   Barriers: done = fires the stage · blocked, or done beside a blocked sibling = ONE handoff line on the parent · mentions ARE actions (assign a human a ticket)
```

## Purpose

Define the staged delivery flow — who owns what, at which stage, with which gate — so
every requirement moves from intake to a published package/image predictably and no
ticket strands. drunk has no deployed environment: for library repos, publishing the
NuGet/npm package IS the release; for container-image repos, publishing the multi-arch
image IS the release. There is no SANDBOX, no PRD, no promotion beyond `main`.

## Scope

All six workflows: **A** bug/question, **B** feature/enhancement spec, **C**
orchestrated delivery (the shared implementation → release tail), **D** CI/CD & build
automation, **E** docs on request, **F** new-service design. All drunk repos: `DKNet` family, `DKNet.Templates`, `drunk-pulumi-*`,
`drunk-others` (Python MCP, Docker, Helm).

## Actors

**product-owner** — research, spec, orchestration of the main ticket end to end; read-only
on code. **spec-reviewer** — the automated spec-review gate (Workflow B only).
**dev-team** (squad; leader **dev-leader**; members dev-backend, pr-reviewer;
the leader runs cycle git-flow itself) — implementation, acceptance-test-first in two runs:
dev-backend writes the spec's scenarios as RED acceptance tests, dev-leader reads and freezes
them (`at_sha`), dev-backend implements against them in Build at ≥80% coverage plus a mutation
report per touched class with a clean pack ([Policy 02](02-testing-and-quality.md) §1/§4); a UI presentation change is built without tests (Policy 02 §1a). No QC squad or QC role exists —
dev-team self-verifies; there is no SANDBOX to deploy to and no BDD integration stage. A
dev-team cycle writes no docs pages (statement 3a).
**pr-reviewer** — the automated PR review + merge gate for every `dev`-bound PR (dev-team's
cycle PR and the standalone PRs of devops, docs-writer and service-architect). **release-manager** — owns the single
`dev`→`main` release PR and its merge; the only agent that ever targets `main`. **devops**
— CI/CD pipelines and build/publish automation, outside the squad flow, no spec gate.
**docs-writer** — library and API feature docs, written only when a human asks for them,
outside the squad flow, no spec gate.
**service-architect** — the design of a new service, before its first code (Workflow F),
delegated by product-owner only, no spec gate; its PR merges only on the owner's approval.
**Humans** — the requester (ticket creator) and the workspace owner (escalation valve).

## Policy statements

1. **Feature flow (B):** intake → clarify with the requester until **zero** open questions → seven-section business spec on the main ticket ([Policy 06](06-requirements-and-spec.md) statement 3) → `[S#]` spec-review gate → on APPROVED, Workflow C: `[P<num>-1]` implementation (dev-team, always including in-repo unit/integration verification — there is no separate QC phase) → dev cycle (Branch → Build → PR → `pr-review-gate` merges into `dev`) → `[P<num>-2]` release `dev`→`main` (release-manager opens + merges; CI publishes the package/image) → main ticket `done`. **Two phases only** — no deploy phase and no QC phase exist because there is no deployed environment.

1b. **A sub-issue stops at development.** The shape of the ticket assigned to product-owner decides where its ownership ends: a **root** ticket (no parent) runs to release as above; a **sub-issue** (it has a parent) gets the same classification, spec and gates but **no `[P<num>-2]`** — it terminates at the verified `[P<num>-1]` and flips `done`, which fires the parent's stage barrier. The parent's owner releases all of its children together in one `dev`→`main` PR, so partial releases of a decomposed feature never happen. The same shape rule already governs dev-team: it stages a `Release` only on a cycle whose ticket has no parent. A sub-issue also keeps its parent's project and carries no labels.

2. **Bug flow (A):** intake → research → root-cause report with a calibrated **confidence 0–100%** that this is a genuine platform defect with the identified root cause, targeting the layer all callers route through — never the symptom path the ticket names. Confidence **≥ 90%** (or the requester's confirmation below that) hands the ROOT ticket to `dev-team` by reassignment — no `[P<num>-n]` phases: dev-leader runs the cycle, stages `[D<num>-n] Release` (release-manager, a dev-team member for that stage) when a package consumer can observe the change, and finalizes the root `in_review` for the owner. product-owner posts one FYI to the requester ("fix delegated, reply to halt") and is out of the ticket. A pure question with no change wanted ends with the report as the deliverable. A root cause found in a pipeline or build script is reclassified to Workflow D and handed to devops, whatever the confidence. See [Policy 07](07-bug-and-defect-management.md).

3. **CI/CD flow (D):** pipelines and build/publish automation are `devops` work — never enter the dev-team cycle, never open a spec gate, and never trigger a `[P<num>-2]` release phase on their own. Two doors: **direct** (requester assigns devops; product-owner stays out) or **delegated**, classified into **D1** analysis-only (report + STOP, requester decides) or **D2** change-requested (`[P<num>-1]` to devops → `[P<num>-1c]` PR review to pr-reviewer). Unlike a sibling factory's Helm/GitOps carve-out, a **standalone devops PR to `dev` gets the same `pr-review-gate` merge, not a human-only merge** — there is no deploy act to reserve for a human here.

3a. **Docs flow (E): docs are written when a human asks, never every cycle.** A docs-only change to a library repo (README, `docs/`, guides, changelog; no source, no test surface) is `docs-writer` work — it never enters the dev-team cycle, never opens a spec gate and never triggers a release. Two doors, like Workflow D: **direct** (the requester or Mika assigns `docs-writer` straight away; product-owner stays out) or **delegated** (product-owner clarifies, then creates `[P<num>-1] Docs: <scope>` to docs-writer and `[P<num>-1c] Review docs PR: <scope>` to pr-reviewer). docs-writer lands ONE `docs/<issue-key>` PR to `dev`, which pr-reviewer scores and merges like devops' PR. The moment the change touches source or tests it is Workflow B. **A dev-team cycle writes no docs pages:** in-code API comments and, for a breaking change, the `Breaking` changelog entry naming the replacement ([Policy 01](01-coding-standards.md) statement 12) ship in dev-backend's Build; dev-leader's final report lists every doc page the change made stale under `Docs impact:` (or `Docs impact: none`), so the owner can ask for them.

3b. **Phases exist for approved specs only.** `[P<num>-1]` / `[P<num>-2]` are Workflow C, downstream of a spec gate. The one exception is the single-change pair `[P<num>-1]` + `[P<num>-1c]` of Workflows D2, E and F, which carries no spec and no release. `[P<num>-1]` pins `Spec revision: <n>` and the spec is **frozen** for the cycle: a later change is a scope comment on the phase ticket with dev-team's mention, which dev-leader turns into ONE scope stage; a finished Acceptance-tests stage is never re-armed for spec drift, and neither the root nor the phase description is edited while the cycle runs.

3c. **Service design flow (F): a new service is designed before its first code, and the owner approves the design.** A request that needs a service or repo that does not exist yet is Workflow F. **One door, delegated:** a design ticket assigned to `service-architect` directly is handed to product-owner. product-owner runs the clarification gate with the requester until the repo name, service name, purpose, users, what is in and out of scope, and the neighbouring repos are settled, and asks the requester to create the empty repo with a `dev` branch — no phase starts before it exists. Then product-owner creates `[P<num>-1] Design: <service>` to service-architect and `[P<num>-1c] Review design PR: <service>` to pr-reviewer. service-architect lands ONE `design/<issue-key>` PR to `dev` that adds `docs/architect/` ([Policy 06](06-requirements-and-spec.md) statement 14). pr-reviewer scores it like a docs PR, but a passing design PR never merges on score: it goes to the resolved owner with options, and merges only on the owner's reply A, relayed by product-owner ([Policy 04](04-code-and-spec-review.md) statement 9a). No spec gate, no release. Once merged, the design binds every later spec and implementation in that repo ([Policy 06](06-requirements-and-spec.md) statement 5c); changing it is a new Workflow F ticket, never a spec or a code PR. Building the service is ordinary Workflow B tickets after that, the first one usually the scaffold.

4. **Gates front-load quality** — the spec gate before implementation, the PR gate before every merge into `dev` (see [Policy 04](04-code-and-spec-review.md)).

5. **Stage barriers fire on `done`; a handoff line covers what they miss.** Completion = `done`; `blocked` = needs help. The report, the `## BLOCKER` and every question or defect report stay on the child's OWN ticket, so assigner↔assignee communication stays paired there. The platform's sub-issue rule wakes the parent's owner when every sub-issue at a stage and below is closed (`done`/`cancelled`) while a later stage waits, and once more when every sub-issue is closed — whoever closed them — so a plain `done` needs nothing more. It never fires for a `blocked` child, nor for a `done` while a sibling at its stage or below sits `blocked`; in those two cases the child's turn ends with ONE line on the parent — `<KEY> blocked — BLOCKER on <KEY>` or `<KEY> done — report on <KEY>` (`<KEY> — <what> on <KEY>` for anything else the parent's owner must read now) — and that line is the wake: on a squad-assigned parent it carries no mention of any kind (the platform routes an agent's plain comment there to the squad leader; any mention, `@all` or a `/note` prefix stops that), on an agent-assigned parent it ends with that agent's mention, on a member-assigned parent none is posted. The line is the only thing a child posts on the parent; the parent's other comments remain its owner's orchestration space. `in_review` is leader-only, reserved for a ROOT ticket awaiting a human; on a phase or sub-task ticket it deadlocks the pipeline — **never** report `in_review` on a phase/sub ticket, use `done`.

6. **Mentions are actions.** An agent/squad mention (real UUID, resolved at runtime) enqueues a run; a member (human) mention only renders a link and delivers nothing. To make a human act, **assign them a ticket at `todo`** — never rely on a mention. Never agent-mention in FYI/ack/done comments; the one exception is the handoff line on an agent-assigned parent (statement 5).

7. **Titles, projects, labels:** **every ROOT main ticket title carries one type prefix** — `[Feature]` · `[Enhance]` · `[Bug]` · `[Question]` · `[CICD]` · `[Docs]` · `[Design]` — followed by the plain title; children carry `[S<num>]` (spec review, keyed to the main ticket) / `[P<num>-n]` (product-owner's phase tickets, keyed to the main ticket, `n`: `-1` implementation, CI/CD change, docs or design, `-2` release) / `[D<num>-n]` (dev-team sub-tasks, keyed to the parent PHASE ticket, `n` = stage). Labels on main tickets **only** (`main` + `feature`/`bug`/`question`/`cicd`/`docs`/`design` + optional domain). Every sub-task parents directly to its cycle parent — never nested deeper. Every child stays in the SAME domain project as the main ticket.

7a. **The root prefix is product-owner's, set at intake.** The requester and Mika create root tickets with a plain title; product-owner adds or corrects the prefix on the root ticket when it labels the ticket and posts the spec (`multica issue update <root-id> --title "<prefix> <plain title>" --no-start` — **always `--no-start`**, a title update on a ticket assigned to you otherwise wakes a second run of yourself). Where product-owner never touches the ticket — a CI/CD ticket taken through the direct door by devops, a docs ticket taken through the direct door by docs-writer — the first agent to pick it up sets the prefix the same way. Reclassifying the workflow changes the prefix with it.

7b. **The prefix is root-only.** It never appears on a child, and it changes no child's title, numbering or `<num>` keying: `[S<num>]`, `[P<num>-n]` and `[D<num>-n]` are keyed off the root's key NUMBER, never its title. Emitting a type prefix on a sub-task is a defect.

**Root-title type prefix.** Exactly one prefix, matching the root ticket's type label:

| Prefix | Label | Use for |
|---|---|---|
| `[Feature]` | `feature` | a capability that does not exist today |
| `[Enhance]` | `feature` | a change to behaviour that already exists |
| `[Bug]` | `bug` | a reported defect |
| `[Question]` | `question` | a question with no change wanted |
| `[CICD]` | `cicd` | a pipeline or build-script change |
| `[Docs]` | `docs` | a docs-only change |
| `[Design]` | `design` | a new service's design, before its first code |

The label stays the source of truth — `[Feature]` and `[Enhance]` both carry the `feature` label, so the prefix is the finer split the labels do not make. A prefix that disagrees with the label is a defect: fix the pair, never argue it.

8. **Escalation is an action, not a status.** A squad that escalates still owns its cycle: post ONE standalone `## BLOCKER` + `## OPTIONS` comment (per [`blocker-report`](../../skills/blocker-report/SKILL.md)), deliver it (the handoff line for a hop to the parent's owner, statement 5; an agent mention for any other agent hop; ticket reassignment at `todo` for a human hop), park the blocked child. Ending a turn with a stuck child and no dispatched comment is a flow defect.

9. **Human touch points are capped:** business clarifications (always the requester, irreducible), spec review (5 rework rounds, then manual handoff), bug confidence (< 90% waits for requester confirmation), PR review (3 rework rounds, then the resolved owner picks an option and the pipeline waits — a PR that passes the score is never handed to a human, [Policy 04](04-code-and-spec-review.md) statements 5 and 11), service design (the owner approves every design PR, statement 3c), critical release (a `dev`→`main` release carrying a `(MINOR)` commit or a `release-review` PR waits for the owner's reply, [Policy 08](08-container-build-and-release.md) statement 2a), squad fix attempts (2 on the same root cause, then escalate). A defect a member finds outside its cycle is filed by its leader to `product-owner` at `todo` and enters the bug flow — the confidence gate is the only human hop it gets. The escalation human is the resolved owner per [Policy 10](10-ticket-ownership-and-owner-pickup.md).

9a. **Gate state lives on custom properties.** Review gates pin `Gate verdict`, `Gate round` and `Gate score` on their own sub-task (never on issue metadata), so a parked gate is visible on the board and in `multica issue children --resolve-properties` without reading threads. Leaders and product-owner read those properties on every wake.

9b. **Platform-wide constants are stated once, in the Workspace Context.** Statuses and wake rules, ticket conventions, `Owner` resolution, git and PR rules, report shapes and bounded comment reads live in the workspace system prompt (`workspace/context.md`) and are cited, not restated, by skills and instructions. Rare-path procedure lives in a skill's `references/`, opened when the case occurs.

9c. **A review gate never parks.** The rework cap limits REWORK verdicts, not re-reviews: every re-review ends APPROVED, REWORK (rounds left) or ESCALATED. A run that leaves the gate `blocked` without a verdict is a flow defect. A Workflow D PR that changes the workflow producing a red check is merged on score (CI red by design), never handed to a human for the red alone.

9d. **Stalls are swept by an autopilot, on its own schedule.** The `🌤️ Daily Stall Sweep` autopilot (Mika; daily 09:00 SGT while it is enabled — its live `status` is the source of truth for whether a sweep runs at all) re-wakes the owning agent of a parked gate, an unpromoted stage, a finished-but-open parent or a silent `in_progress`, and digests to the owner what only a human can move. The sweep changes no status and creates no work.

10. **A review's leftovers never become a delivery cycle.** In-scope leftovers — anything in a file the cycle's diff touched, regardless of who introduced it — are cleared inside that cycle by pr-reviewer before it merges (a polish round routed by dev-leader to the implementer's own Build sub-task), and produce no ticket. Out-of-scope leftovers are dropped unless they clear the worth-fixing bar — a defect or security finding with a named observable failure and reproduction — in which case dev-leader files ONE ordinary defect ticket, folded into any open ticket sharing its root cause. `Review follow-ups:` tickets are retired. Decomposing a leftovers ticket into `[P-1]`/`[P-2]` phases is a flow defect, and so is filing new backlog work from nits: the monthly `arch-reviewer` sweep owns that. The 2026-09-11 cascade (eight roots in six hours, two NuGet patches for code comments) is what this rule exists to prevent.

## Roles & responsibilities

- **product-owner** — classifies the workflow, researches with CodeGraph, runs the clarification gate, authors the spec, creates and promotes phase tickets, triages follow-ups, flips the main ticket `done`. Never touches code or git.
- **spec-reviewer** — scores Workflow B specs, gates REWORK/APPROVED/MANUAL HANDOFF.
- **dev-leader / dev-team** — decomposes `[P<num>-1]` into `[D<num>-n]` sub-tasks, self-verifies, cuts the branch, opens the one PR.
- **pr-reviewer** — scores and merges every `dev`-bound PR: dev-team's, devops', docs-writer's and service-architect's — a design PR only on the owner's reply.
- **release-manager** — opens the single `dev`→`main` release PR, checks whether it is critical, and merges it — a critical one only on the owner's reply; nothing else.
- **devops** — owns Workflow D end to end under D1/D2; lands its change via a `chore/<issue-key>` PR to `dev`.
- **docs-writer** — owns Workflow E, only on a human's request; lands its change via a `docs/<issue-key>` PR to `dev`.
- **service-architect** — owns Workflow F's design phase; lands `docs/architect/` via a `design/<issue-key>` PR to `dev`, merged on the owner's approval.

## Definition of Done / compliance

- Feature: spec approved → PR merged into `dev` with a pr-reviewer score → `dev`→`main` release PR merged → package/image published by CI → main ticket `done` with a final summary. No SANDBOX/BDD stage is ever inserted.
- Feature delivered as a sub-issue: spec approved → PR merged into `dev` with a pr-reviewer score → sub-issue `done` with a final summary naming the parent as release owner. No release PR, no publish — both belong to the parent.
- Bug: root-cause report posted with a calibrated confidence; delegation (or requester confirmation) recorded before any Workflow C work starts.
- CI/CD: devops' PR merged into `dev`; main ticket `done` with a plain summary; no `[S#]` and no `[P<num>-2]` ever created for this flow.
- Docs: docs-writer's PR merged into `dev`; main ticket `done` with a plain summary; no `[S#]`, no `[P<num>-2]`, and no Docs sub-task in any dev-team cycle.
- Service design: service-architect's PR merged into `dev` on the owner's reply A; main ticket `done` with a plain summary linking the design; no `[S#]` and no `[P<num>-2]`.
- Every stage transition leaves exactly one promotion comment in the completion shape; no stranded children (every `blocked` child has a dispatched `## BLOCKER` comment).

## Enforcement

`product-owner` orchestrates and promotes phases; the spec-review and PR-review gates
enforce quality at their checkpoints; `dev-leader` runs the cycle per the squad-leader
playbook; squad members follow the worker playbook. Branch authority is enforced by
[Policy 03](03-source-control-branching.md).

## Exceptions & waivers

- No BDD-integration waiver exists in drunk (unlike a deployed-service factory) — there is
  no SANDBOX stage to waive in the first place. dev-team's in-repo unit/integration
  verification at ≥80% per-touched-class coverage is never optional and never waived, except for
  UI presentation files ([Policy 02](02-testing-and-quality.md) statement 1a).
- Config-only requests still take the light dev route (Branch → Update → PR → gate)
  — the Update sub-task carries no coverage requirement when there is nothing to test.
  Docs-only requests are Workflow E: docs-writer's own `docs/<issue-key>` PR, same gate.
- A sub-issue never gets a `[P<num>-2]` release phase, whatever a package consumer can
  observe — the parent releases its children together.
- Workflow D never gets a `[P<num>-2]` release phase — a CI/CD change to build/publish
  workflows never triggers a package release on its own; if one is warranted, the
  requester files it separately.

## References

- [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) — the single source of truth (actors, all four flow diagrams, stage-ownership table, branch & release strategy, escalation map).
- Role procedures: [`sdlc-flow-po-orchestration`](../../skills/sdlc-flow-po-orchestration/SKILL.md), [`sdlc-flow-squad-leader-playbook`](../../skills/sdlc-flow-squad-leader-playbook/SKILL.md), [`sdlc-flow-squad-worker-playbook`](../../skills/sdlc-flow-squad-worker-playbook/SKILL.md), [`leader-gitops`](../../skills/leader-gitops/SKILL.md).
- [`agents/product-owner.md`](../../agents/product-owner.md), [`agents/dev-leader.md`](../../agents/dev-leader.md).
