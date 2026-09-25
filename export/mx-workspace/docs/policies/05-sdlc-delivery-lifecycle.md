# Policy 05 — SDLC Delivery Lifecycle

| | |
|---|---|
| **Policy ID** | MX-POL-05 |
| **Version** | 1.3 |
| **Status** | Active |
| **Owner** | product-owner (product-team) |
| **Applies to** | Every ticket that flows through the mx software factory |
| **Related skills** | [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) · [`sdlc-flow-po-orchestration`](../../skills/sdlc-flow-po-orchestration/SKILL.md) · [`sdlc-flow-squad-leader-playbook`](../../skills/sdlc-flow-squad-leader-playbook/SKILL.md) · [`sdlc-flow-squad-member-protocol`](../../skills/sdlc-flow-squad-member-protocol/SKILL.md) |
| **Enforced at** | product-owner orchestration + the review gates |

> **Authority.** This policy is the source of truth for the delivery flow. The
> `sdlc-flow-*` and role skills **implement** it — stages, ownership and branch strategy
> derive from it. Amend this policy first, then cascade — see
> [change control](00-policies-index.md#change-control).

## Delivery lifecycle at a glance

```
   FEATURE (Workflow B)
   👤 ticket ─▶ 🦉 intake/clarify (0 open Qs) ─▶ 11-section SPEC ─▶ [S#] SPEC GATE
        │                                                              │ APPROVED
        ▼                                                              ▼
   [P#-1] DEV cycle: Branch▶Build▶Verify▶PR▶🦅PR GATE (merge to dev)
        │
        ▼
   [P#-2a] release dev▶main (release-manager, CI builds image)
        │
        ├── bdd_required=false ──▶ TERMINAL (👤 deploys main when they choose)
        │
        └── else ─▶ [P#-2b] 👤 argoCD deploy to SANDBOX ─▶ [P#-3] 🐝 qc BDD ─▶ ✅ done

   BUG (A): research ─▶ root-cause + confidence  ≥90% auto-delegate C · <90% requester confirms
   CI/CD (D): devops only — no spec gate; helm PR scored, never gate-merged (human merges = deploy)

   Barriers: done = fires the stage · blocked+mention = needs help · mentions ARE actions (assign a human a ticket)
```

## Purpose

Define the staged delivery flow — who owns what, at which stage, with which gate —
so every requirement moves from intake to verified delivery predictably and no ticket
strands. This is the map; the delivery-pipeline skill is the source of truth.

## Scope

All four workflows: **A** bug, **B** feature, **C** implementation (shared tail),
**D** CI/CD & infra. Projects: `mx-main` (main + phase tickets), `mx-code` (dev
sub-tasks), `mx-qc-board` (qc sub-issues).

## Actors

`product-team` (leader **product-owner**; spec-reviewer, release-manager, devops,
pr-reviewer + the requester) owns the main ticket end to end, read-only on code.
`dev-team` (leader **dev-leader**; dev-backend, pr-reviewer) implements acceptance-test-first in two
runs: dev-backend writes the spec's scenarios as RED acceptance tests, dev-leader reads and
freezes them (`at_sha`), dev-backend implements against them in Build at ≥80% coverage plus a
mutation report per touched class ([Policy 02](02-testing-and-quality.md) §1/§3).
`qc-team` (leader **qc-leader**; qc-tester, qc-runner, pr-reviewer) runs SANDBOX BDD.
`devops` owns CI/CD & helm, never a squad member. Humans: the requester and the
workspace owner (escalation valve).

## Policy statements

1. **Feature flow (B):** intake → clarify with the requester until **zero** open questions → 11-section business spec on the main ticket → `[S#]` spec-review gate → on approval, `[P#-1]` implementation (always incl. in-repo BDD/unit coverage) + the conditional SANDBOX tail → dev cycle (Branch → Build → Verify → PR → review gate merges to `dev`) → `[P#-2a]` release `dev`→`main` → `[P#-2b]` SANDBOX deploy → `[P#-3]` BDD integration → main ticket done.
1b. **A sub-issue stops at implementation.** The shape of the ticket assigned to product-owner decides where its cycle ends: a **root** main ticket (no parent) runs the full chain above; a **sub-issue** (it has a parent) gets the same classification, spec, gates and scope keys but **no `[P#-2a]`, `[P#-2b]` or `[P#-3]`** — it is terminal at the verified `[P#-1]` (merged into `dev`, pr-reviewer scored) and flips `done`. The parent's owner ships every child in ONE `dev`→`main` release, one SANDBOX deploy and one BDD pass, so no release ever carries a sibling that is still mid-cycle. A parent whose children already carry the work is never re-spec'd: its own cycle creates only the release tail, once every child is `done` with its PR merged.
2. **Bug flow (A):** intake → research → root-cause report with a calibrated **confidence 0–100%**. Confidence **≥ 90%** auto-delegates Workflow C immediately (FYI to requester, "reply to halt"); **< 90%** waits for the requester to confirm; a pure question with no change wanted ends with the report as the deliverable. See [Policy 07](07-bug-and-defect-management.md).
3. **CI/CD flow (D):** pipelines and helm are `devops` work — never enter dev/qc cycles, never open a spec gate. Two doors: **direct** (requester assigns devops; product-team stays out) or **delegated** `[P#-1b]`/`[P#-1c]` phases of a feature. A standalone devops PR to `dev` gets a PR gate; a helm PR to `main` is scored but **never merged by the gate**. See [Policy 08](08-release-management.md).
4. **Gates front-load quality** — spec gate before implementation, PR gate before merge (see [Policy 04](04-code-and-spec-review.md)).
5. **Stage barriers fire on `done`.** Completion = `done`. `blocked` + a mention comment = needs help — and that comment lives on the blocked agent's OWN ticket, never on its parent: a mention wakes its target wherever it is posted, so assigner↔assignee communication (questions, blockers, defect reports) stays paired on the assignee's ticket while parent comments remain the parent owner's orchestration space. `in_review` is leader-only for root parents awaiting a human; on a phase ticket it deadlocks the pipeline — use `done`.
6. **Mentions are actions.** An agent/squad mention (real UUID, resolved at runtime) enqueues a run; a member (human) mention only renders a link and delivers nothing. To make a human act, **assign them a ticket at `todo`** — never rely on a mention. Never agent-mention in FYI/ack comments.
7. **Titles, projects, labels:** **every ROOT main ticket title carries one type prefix** — `[Feature]` · `[Enhance]` · `[Bug]` · `[Question]` · `[CICD]` — followed by the plain title; children carry `[S#]`/`[P#-n]`/`[D#-n]`/`[T#-n]` keyed to the root ticket number. Labels on main tickets **only** (`main` + `feature`/`bug`/`question`/`cicd`). Every sub-task parents directly to its cycle parent.

7a. **The root prefix is product-owner's, set at intake.** The requester creates the root ticket with a plain title; product-owner adds or corrects the prefix on the root when it labels the ticket and posts the spec (`multica issue update <root-id> --title "<prefix> <plain title>" --no-start` — **always `--no-start`**, a title update on a ticket assigned to your squad otherwise wakes a second run). Where product-owner never touches the ticket, the first agent to pick it up sets the prefix the same way. Reclassifying the workflow changes the prefix with it.

7b. **The prefix is root-only.** It never appears on a child, and it changes no child's title, numbering or `#` keying: `[S#]`, `[P#-n]`, `[D#-n]` and `[T#-n]` are keyed off the root's key NUMBER, never its title. Emitting a type prefix on a sub-task is a defect.

**Root-title type prefix.** Exactly one prefix, matching the root ticket's type label:

| Prefix | Label | Use for |
|---|---|---|
| `[Feature]` | `feature` | a capability that does not exist today |
| `[Enhance]` | `feature` | a change to behaviour that already exists |
| `[Bug]` | `bug` | a reported defect |
| `[Question]` | `question` | a question with no change wanted |
| `[CICD]` | `cicd` | a pipeline or build-script change |

The label stays the source of truth — `[Feature]` and `[Enhance]` both carry the `feature` label, so the prefix is the finer split the labels do not make. A prefix that disagrees with the label is a defect: fix the pair, never argue it.
8. **Escalation is an action, not a status.** A squad that escalates still owns its cycle: post ONE standalone `## BLOCKER` + `## OPTIONS` comment (per [`blocker-report`](../../skills/blocker-report/SKILL.md)), deliver it (agent mention for an agent hop, ticket reassignment at `todo` for a human hop), park the blocked child. Ending a turn with a stuck child and no dispatched comment is a flow defect.
9. **Human touch points are capped** (see the table in the delivery pipeline): business clarifications (always the requester), spec review (5 rounds), bug confidence (< 90%), PR review (3 rounds), squad fix attempts (2 on the same root cause), SANDBOX deploy, helm merge. The human is the ROOT ticket creator when `creator_type=member`, else the workspace owner.

## Definition of Done / compliance

- Feature: spec approved → PR merged with score → released to `main` → (unless waived) SANDBOX-deployed and BDD-verified → main ticket `done` with a final summary.
- Every stage transition leaves exactly one promotion comment in the completion shape.
- No stranded children: every `blocked` child has a dispatched `## BLOCKER` comment.

## Enforcement

`product-owner` orchestrates and promotes phases; the spec and PR gates enforce quality;
squad leaders run cycles per the leader playbook; members follow the member protocol.
Branch authority is deliberate and enforced by [Policy 03](03-source-control-branching.md).

## Exceptions & waivers

- A **BDD integration waiver** (requester-only, `bdd_required=false`) drops `[P#-2b]` and `[P#-3]` and makes `[P#-2a]` terminal — nothing else changes (see [Policy 02](02-testing-and-quality.md)).
- Docs/config-only requests take the light dev route (Branch → Update → PR → gate, no Verify stage).
- Workflow D has no `[P#-2a]` release, no `[P#-2b]`, no `[P#-3]`.

## References

- [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) — the single source of truth (flow diagrams, stage ownership table, branch strategy, escalation map).
- Role procedures: [`sdlc-flow-po-orchestration`](../../skills/sdlc-flow-po-orchestration/SKILL.md), [`sdlc-flow-squad-leader-playbook`](../../skills/sdlc-flow-squad-leader-playbook/SKILL.md), [`sdlc-flow-squad-member-protocol`](../../skills/sdlc-flow-squad-member-protocol/SKILL.md), [`leader-gitops`](../../skills/leader-gitops/SKILL.md).
