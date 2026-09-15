# Policy 05 — SDLC Delivery Lifecycle

| | |
|---|---|
| **Policy ID** | DRK-POL-05 |
| **Version** | 1.3 |
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
   👤 ticket ─▶ 🦊 intake/clarify (0 open Qs) ─▶ 11-section SPEC ─▶ [S#] SPEC GATE
        │                                                              │ APPROVED
        ▼                                                              ▼
   [P#-1] DEV cycle: Branch▶Build(TDD, ≥80% cov)▶PR▶🦅 PR GATE (merges to dev)
        │
        ▼
   [P#-2] release dev▶main (release-manager opens+merges) ─▶ CI publishes package/image
        │
        ▼
   MAIN TICKET done — TERMINAL. No SANDBOX, no BDD stage, no deploy: publishing IS release.

   BUG (A): research ─▶ root-cause + confidence  ≥90% auto-delegate C · <90% requester confirms
   CI/CD (D): devops only — no spec gate, but still 🦅 PR GATE on the standalone chore/<key> PR

   Barriers: done = fires the stage · blocked+mention = needs help · mentions ARE actions (assign a human a ticket)
```

## Purpose

Define the staged delivery flow — who owns what, at which stage, with which gate — so
every requirement moves from intake to a published package/image predictably and no
ticket strands. drunk has no deployed environment: for library repos, publishing the
NuGet/npm package IS the release; for container-image repos, publishing the multi-arch
image IS the release. There is no SANDBOX, no PRD, no promotion beyond `main`.

## Scope

All four workflows: **A** bug/question, **B** feature/enhancement spec, **C**
orchestrated delivery (the shared implementation → release tail), **D** CI/CD & build
automation. All drunk repos: `DKNet` family, `DKNet.Templates`, `drunk-pulumi-*`,
`drunk-others` (Python MCP, Docker, Helm).

## Actors

**product-owner** — research, spec, orchestration of the main ticket end to end; read-only
on code. **spec-reviewer** — the automated spec-review gate (Workflow B only).
**dev-team** (squad; leader **dev-leader**; members dev-backend, docs-writer, pr-reviewer;
the leader runs cycle git-flow itself) — implementation, acceptance-test-first in two runs:
dev-backend writes the spec's scenarios as RED acceptance tests, dev-leader reads and freezes
them (`at_sha`), dev-backend implements against them in Build at ≥80% coverage plus a mutation
report per touched class with a clean pack ([Policy 02](02-testing-and-quality.md) §1/§4). No QC squad or QC role exists —
dev-team self-verifies; there is no SANDBOX to deploy to and no BDD integration stage.
**pr-reviewer** — the automated PR review + merge gate for every `dev`-bound PR (both
dev-team's cycle PR and devops' standalone PR). **release-manager** — owns the single
`dev`→`main` release PR and its merge; the only agent that ever targets `main`. **devops**
— CI/CD pipelines and build/publish automation, outside the squad flow, no spec gate.
**Humans** — the requester (ticket creator) and the workspace owner (escalation valve).

## Policy statements

1. **Feature flow (B):** intake → clarify with the requester until **zero** open questions → 11-section business spec on the main ticket → `[S#]` spec-review gate → on APPROVED, Workflow C: `[P<num>-1]` implementation (dev-team, always including in-repo unit/integration verification — there is no separate QC phase) → dev cycle (Branch → Build → PR → `pr-review-gate` merges into `dev`) → `[P<num>-2]` release `dev`→`main` (release-manager opens + merges; CI publishes the package/image) → main ticket `done`. **Two phases only** — no deploy phase and no QC phase exist because there is no deployed environment.
2. **Bug flow (A):** intake → research → root-cause report with a calibrated **confidence 0–100%** that this is a genuine platform defect with the identified root cause, targeting the layer all callers route through — never the symptom path the ticket names. Confidence **≥ 90%** (or the requester's confirmation below that) hands the ROOT ticket to `dev-team` by reassignment — no `[P<num>-n]` phases: dev-leader runs the cycle, stages `[D<num>-n] Release` (release-manager, a dev-team member for that stage) when a package consumer can observe the change, and finalizes the root `in_review` for the owner. product-owner posts one FYI to the requester ("fix delegated, reply to halt") and is out of the ticket. A pure question with no change wanted ends with the report as the deliverable. A root cause found in a pipeline or build script is reclassified to Workflow D and handed to devops, whatever the confidence. See [Policy 07](07-bug-and-defect-management.md).
3a. **Docs flow (E):** a docs-only change to a library repo (README, `docs/`, comments, changelog; no source, no test surface) is a dev-team Route B root cycle with no spec gate and no release. Two doors, like Workflow D: **direct** (the requester or Mika assigns `dev-team` straight away; product-owner stays out) or **delegated** (product-owner clarifies, appends a `## Brief` to the root, and reassigns the ROOT to `dev-team`). No phases. The moment the change touches source or tests it is Workflow B.
3b. **Phases exist for approved specs only.** `[P<num>-1]` / `[P<num>-2]` are Workflow C, downstream of a spec gate. `[P<num>-1]` pins `Spec revision: <n>` and the spec is **frozen** for the cycle: a later change is a scope comment on the phase ticket with dev-team's mention, which dev-leader turns into ONE scope stage; a finished Acceptance-tests stage is never re-armed for spec drift, and neither the root nor the phase description is edited while the cycle runs.
3. **CI/CD flow (D):** pipelines and build/publish automation are `devops` work — never enter the dev-team cycle, never open a spec gate, and never trigger a `[P<num>-2]` release phase on their own. Two doors: **direct** (requester assigns devops; product-owner stays out) or **delegated**, classified into **D1** analysis-only (report + STOP, requester decides) or **D2** change-requested (`[P<num>-1]` to devops → `[P<num>-1c]` PR review to pr-reviewer). Unlike a sibling factory's Helm/GitOps carve-out, a **standalone devops PR to `dev` gets the same `pr-review-gate` merge, not a human-only merge** — there is no deploy act to reserve for a human here.
4. **Gates front-load quality** — the spec gate before implementation, the PR gate before every merge into `dev` (see [Policy 04](04-code-and-spec-review.md)).
5. **Stage barriers fire on `done`.** Completion = `done`. `blocked` + a mention comment = needs help — and that comment lives on the blocked agent's OWN ticket, never on its parent: a mention wakes its target wherever it is posted, so assigner↔assignee communication (questions, blockers, defect reports) stays paired on the assignee's ticket while parent comments remain the parent owner's orchestration space. `in_review` is leader-only, reserved for a ROOT ticket awaiting a human; on a phase or sub-task ticket it deadlocks the pipeline — **never** report `in_review` on a phase/sub ticket, use `done`.
6. **Mentions are actions.** An agent/squad mention (real UUID, resolved at runtime) enqueues a run; a member (human) mention only renders a link and delivers nothing. To make a human act, **assign them a ticket at `todo`** — never rely on a mention. Never agent-mention in FYI/ack/done comments.
7. **Titles, projects, labels:** main tickets plain (no prefix); children carry `[S<num>]` (spec review, keyed to the main ticket) / `[P<num>-n]` (product-owner's phase tickets, keyed to the main ticket, `n`: `-1` implementation or CI/CD change, `-2` release) / `[D<num>-n]` (dev-team sub-tasks, keyed to the parent PHASE ticket, `n` = stage). Labels on main tickets **only** (`main` + `feature`/`bug`/`question`/`cicd` + optional domain). Every sub-task parents directly to its cycle parent — never nested deeper. Every child stays in the SAME domain project as the main ticket.
8. **Escalation is an action, not a status.** A squad that escalates still owns its cycle: post ONE standalone `## BLOCKER` + `## OPTIONS` comment (per [`blocker-report`](../../skills/blocker-report/SKILL.md)), deliver it (agent mention for an agent hop, ticket reassignment at `todo` for a human hop), park the blocked child. Ending a turn with a stuck child and no dispatched comment is a flow defect.
9. **Human touch points are capped:** business clarifications (always the requester, irreducible), spec review (5 rework rounds, then manual handoff), bug confidence (< 90% waits for requester confirmation), PR review (2 rework rounds, then manual handoff to the resolved owner), squad fix attempts (2 on the same root cause, then escalate). A defect a member finds outside its cycle is filed by its leader to `product-owner` at `todo` and enters the bug flow — the confidence gate is the only human hop it gets. The escalation human is the resolved owner per [Policy 10](10-ticket-ownership-and-owner-pickup.md).
9a. **Gate state lives on custom properties.** Review gates pin `Gate verdict`, `Gate round` and `Gate score` on their own sub-task (never on issue metadata), so a parked gate is visible on the board and in `multica issue children --resolve-properties` without reading threads. Leaders and product-owner read those properties on every wake.
9c. **A review gate never parks.** The rework cap limits REWORK verdicts, not re-reviews: every re-review ends APPROVED, DEFERRED, REWORK (rounds left) or ESCALATED. A run that leaves the gate `blocked` without a verdict is a flow defect. A Workflow D PR that changes the workflow producing a red check is merged on score (CI red by design), never handed to a human for the red alone.
9d. **Stalls are swept daily.** The `Daily Stall Sweep` autopilot (Mika) re-wakes the owning agent of a parked gate, an unpromoted stage, a finished-but-open parent or a silent `in_progress`, and digests to the owner what only a human can move. The sweep changes no status and creates no work.
9b. **Platform-wide constants are stated once, in the Workspace Context.** Statuses and wake rules, ticket conventions, `Owner` resolution, git and PR rules, report shapes and bounded comment reads live in the workspace system prompt (`workspace/context.md`) and are cited, not restated, by skills and instructions. Rare-path procedure lives in a skill's `references/`, opened when the case occurs.
10. **A review's leftovers never become a delivery cycle.** In-scope leftovers — anything in a file the cycle's diff touched, regardless of who introduced it — are cleared inside that cycle by pr-reviewer before it merges (a polish round on the implementer's own Build sub-task), and produce no ticket. Out-of-scope leftovers are dropped unless they clear the worth-fixing bar — a defect or security finding with a named observable failure and reproduction — in which case dev-leader files ONE ordinary defect ticket, folded into any open ticket sharing its root cause. `Review follow-ups:` tickets are retired. Decomposing a leftovers ticket into `[P-1]`/`[P-2]` phases is a flow defect, and so is filing new backlog work from nits: the monthly `arch-reviewer` sweep owns that. The 2026-09-11 cascade (eight roots in six hours, two NuGet patches for code comments) is what this rule exists to prevent.

## Roles & responsibilities

- **product-owner** — classifies the workflow, researches with CodeGraph, runs the clarification gate, authors the spec, creates and promotes phase tickets, triages follow-ups, flips the main ticket `done`. Never touches code or git.
- **spec-reviewer** — scores Workflow B specs, gates REWORK/APPROVED/MANUAL HANDOFF.
- **dev-leader / dev-team** — decomposes `[P<num>-1]` into `[D<num>-n]` sub-tasks, self-verifies, cuts the branch, opens the one PR.
- **pr-reviewer** — scores and merges every `dev`-bound PR, both dev-team's and devops'.
- **release-manager** — opens and merges the single `dev`→`main` release PR; nothing else.
- **devops** — owns Workflow D end to end under D1/D2; lands its change via a `chore/<issue-key>` PR to `dev`.

## Definition of Done / compliance

- Feature: spec approved → PR merged into `dev` with a pr-reviewer score → `dev`→`main` release PR merged → package/image published by CI → main ticket `done` with a final summary. No SANDBOX/BDD stage is ever inserted.
- Bug: root-cause report posted with a calibrated confidence; delegation (or requester confirmation) recorded before any Workflow C work starts.
- CI/CD: devops' PR merged into `dev`; main ticket `done` with a plain summary; no `[S#]` and no `[P<num>-2]` ever created for this flow.
- Every stage transition leaves exactly one promotion comment in the completion shape; no stranded children (every `blocked` child has a dispatched `## BLOCKER` comment).

## Enforcement

`product-owner` orchestrates and promotes phases; the spec-review and PR-review gates
enforce quality at their checkpoints; `dev-leader` runs the cycle per the squad-leader
playbook; squad members follow the worker playbook. Branch authority is enforced by
[Policy 03](03-source-control-branching.md).

## Exceptions & waivers

- No BDD-integration waiver exists in drunk (unlike a deployed-service factory) — there is
  no SANDBOX stage to waive in the first place. dev-team's in-repo unit/integration
  verification at ≥80% per-touched-class coverage is never optional and never waived.
- Docs/config-only requests still take the light dev route (Branch → Update → PR → gate)
  — the Build/Update sub-task carries no coverage requirement when there is nothing to test.
- Workflow D never gets a `[P<num>-2]` release phase — a CI/CD change to build/publish
  workflows never triggers a package release on its own; if one is warranted, the
  requester files it separately.

## References

- [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) — the single source of truth (actors, all four flow diagrams, stage-ownership table, branch & release strategy, escalation map).
- Role procedures: [`sdlc-flow-po-orchestration`](../../skills/sdlc-flow-po-orchestration/SKILL.md), [`sdlc-flow-squad-leader-playbook`](../../skills/sdlc-flow-squad-leader-playbook/SKILL.md), [`sdlc-flow-squad-worker-playbook`](../../skills/sdlc-flow-squad-worker-playbook/SKILL.md), [`leader-gitops`](../../skills/leader-gitops/SKILL.md).
- [`agents/product-owner.md`](../../agents/product-owner.md), [`agents/dev-leader.md`](../../agents/dev-leader.md).
