# Policy 07 — Bug & Defect Management

| | |
|---|---|
| **Policy ID** | DRK-POL-07 |
| **Version** | 1.2 |
| **Status** | Active |
| **Owner** | product-owner (intake, root-cause, confidence gate, triage) |
| **Applies to** | Every reported bug, every architecture-sweep finding routed as a defect, every PR-gate REWORK finding, and every blocker escalation |
| **Related skills** | [`bug-report`](../../skills/bug-report/SKILL.md) · [`blocker-report`](../../skills/blocker-report/SKILL.md) |
| **Enforced at** | product-owner, dev-team |

> **Authority.** This policy is the source of truth for how a reported defect is routed,
> diagnosed, and fixed. `bug-report` and `blocker-report` **implement** its ticket and
> escalation shapes. Amend this policy first, then cascade — see
> [change control](00-policies-index.md#change-control).

## Bug flow at a glance

```
   👤 bug/question ─▶ 🦉 product-owner researches ─▶ ROOT-CAUSE report + CONFIDENCE (0–100%)
                                                              │
                    ┌─────────────────────────────┬──────────┴───────────────┐
                    ▼                              ▼                          ▼
             pure question             confidence ≥ 90%              confidence < 90%
             (no change wanted)        AUTO-DELEGATE Workflow C      👤 requester confirms
             → report is the           (FYI: "reply to halt")        before any delegation
                deliverable
                                              │
                                              ▼
                          Root-cause report = the implementation basis
                          (no spec needed unless the requester asks for one)

   dev-team review loop:  pr-reviewer REWORK ─▶ ONE findings comment on dev-backend's Build sub-task
                          (never one per finding, no ticket) ─▶ Prove-It test + fix ─▶ mention back ─▶ re-review ─▶ 2 rounds cap
                                                                                        │
                                                                                        ▼
                                                                    pr-reviewer escalates to the
                                                                    workspace owner instead of a 3rd round

   Escalate as an action: 2 failed attempts on the same root cause ─▶ ## BLOCKER + ## OPTIONS
```

## Purpose

Route every defect to the right owner on the first read, fix it at the layer all callers
route through — never the symptom the ticket names — and never let a fix ship without a
test proving the defect is gone. A bug ticket must let a zero-context reader pick the
handling team from the ticket alone.

## Scope

Standalone bug/question tickets worked by product-owner (Workflow A), defects `pr-reviewer`
finds while gating a dev-team cycle's PR, defects an architecture sweep routes for human
triage, and blocker escalations raised by any agent stuck on the same root cause. In-cycle
rework comments (a PR-gate REWORK on the implementer's sub-task) follow `pr-review-gate`'s
format, not this policy's three-section shape.

## Policy statements

1. **Bug flow (Workflow A): research → clarify → root-cause report → confidence gate → delegate.** product-owner reproduces the issue, finds the root cause at the layer all callers route through — never the symptom path the ticket names — and posts a root-cause report as a comment: direct answer first, then evidence (`file:line`, call paths), affected components, reproduction conditions, a proposed fix direction, and a **calibrated confidence (0–100%)** that this is a genuine platform defect with the identified root cause.
2. **When the ticket already carries structured filing sections** (a QC-consolidated defect or an architecture-sweep finding routed for triage — both use the `bug-report` three-section shape), product-owner starts from them: verifies the stated location instead of re-deriving from zero, and treats the stated Root cause as a hypothesis to confirm or refute, never as settled diagnosis.
3. **Confidence gates delegation, with no override.**
   - **≥ 90%** (confirmed) → auto-delegate straight to Workflow C **immediately** — the root-cause report itself is the implementation basis, no separate spec is written — plus ONE FYI comment to the requester (member mention) stating root cause, confidence, and that the fix is delegated ("reply to halt").
   - **< 90%** (possibly by-design, config, or user error) → post the report and require the requester to explicitly confirm before any delegation. Never inflate confidence to skip this step.
   - **Pure question, no change requested** → the report ends the workflow; nothing is delegated.
4. **A Workflow B spec is written only if the requester asks for one** — it then passes the spec-review gate ([Policy 04](04-code-and-spec-review.md)) like any other spec; a bug fix does not require one by default.
5. **A pipeline/build-script root cause is Workflow D, never dev-team.** Regardless of confidence, a fix that lives in a pipeline or build script routes to `devops`, reported and handed off explicitly — Workflow A's auto-delegate does not apply to that class.
6. **Fix at the root, once.** The fix targets the layer all callers route through; a guard in one shared function that closes every caller's path beats a guard duplicated in each caller, and it is the only way to guarantee no sibling caller is left broken.
7. **Bug ticket = three sections, in order, per `bug-report`:** **Scope (Git Repo, Module/Classes)** (the most precise VERIFIED location — git repo + module/class/file, package, or endpoint; a guessed location is worse than none, since it routes the ticket to the wrong team), **Root cause** (the mechanism that makes it fail, never the symptom, + blast radius if left unfixed; `HYPOTHESIS:` unless proven), **Suggested owner** (one team + one line of reasoning derived from Scope and Root cause, routed by what must change — never by where the symptom surfaced). Evidence and a proposed fix are the owner's to produce during diagnosis, not the reporter's.
8. **One issue per distinct root cause; de-duplicate before filing.** A review-round consolidation or an architecture-sweep triage batch files ONE ticket with a summary table (`defect · scope · severity · root cause · suggested owner`) followed by one three-section block per defect — never one ticket per symptom observed.
9. **Title names the root cause, not the symptom** — "shared-state coupling breaks parallel test isolation", never "tests are flaky".
10. **In-cycle defects are caught by dev-backend's own tests first, then by the PR gate — no separate QC loop.** dev-backend works test-first ([Policy 02](02-testing-and-quality.md) §1): a red test during Build is fixed in place, never filed as a ticket. A defect the PR gate finds is a `pr-review-gate` REWORK: ONE consolidated findings comment per round on `dev-backend`'s own Build sub-task with its mention — no fix ticket, never one comment per finding; dev-backend reproduces each finding with a failing test before fixing (Prove-It), pushes, and mentions pr-reviewer back on that sub-task; pr-reviewer's own review sub-task sits `blocked` meanwhile and the squad leader is not in the loop. Capped at 2 rounds, then pr-reviewer hands off to the workspace owner instead of starting a third.
11. **Escalate as an action, not a status.** After 2 failed attempts on the same root cause — or anything outside the acting agent's control (a product decision, missing credentials, a broken environment) — post ONE standalone comment opening with `## BLOCKER` immediately followed by `## OPTIONS`, per `blocker-report`: Blocked / Cause / Tried / Need / Owner, then 2–3 decidable options with exactly one marked `✅ Recommended`. The section is additive to delivery, not a substitute for it — an agent hop still needs `blocked` plus the receiving agent's mention; a human hop still needs the ticket reassigned to the human at `todo` (a member mention alone notifies but delivers nothing).
12. **Completion is reported in the fixed shape, one comment per event:** `## RESULT` (what changed, one line) / `## EVIDENCE` (a table row per claim — build, tests, coverage, diff shape; a skipped check is a row saying so, never a missing row) / `## LEFT OPEN` (follow-ups, deviations, waivers, or `none`). A completion comment carrying more than one short paragraph of narrative below `LEFT OPEN` belongs in a blocker report or a spec discussion instead.
13. **Defects re-enter delivery through Policy 05, not through a side channel.** A confirmed bug is handed to `dev-team` as the ROOT ticket (Policy 05 §2): dev-leader runs the cycle and its `Release` stage; there are no `[P<num>-n]` phases for a bug and no separate defect-delivery pipeline to maintain.
13a. **A defect a squad member finds outside its cycle is filed by its leader to product-owner.** pr-reviewer's `## OUT-OF-SCOPE DEFECT` section, or any member report naming a defect or security finding with a reproduction, becomes ONE `bug-report` ticket (consolidated by root cause) that dev-leader creates assigned to `product-owner` at `todo` with `Owner` set. It enters statement 1 as a bug on its own merits; the confidence gate decides whether a human confirms. It is never left unassigned and never assigned to the workspace owner.
14. **Architecture-sweep findings are never self-routed to a fix.** `arch-reviewer` files findings to the human triager (the workspace owner, resolved at runtime), never to `dev-team` or `product-owner` directly; product-owner only picks one up if the triager routes it in as a bug ticket, at which point Workflow A applies from statement 2.

## Roles & responsibilities

- **product-owner** — runs Workflow A end to end: research, root-cause report, confidence gate, delegation decision, and (per Policy 05 Workflow C) ownership of the resulting main ticket through delivery.
- **dev-backend** — catches its own defects test-first inside Build; fixes pr-reviewer's findings on its own Build sub-task with a reproduction test per finding and mentions pr-reviewer back.
- **pr-reviewer** — finds in-cycle defects at the PR gate; owns the consolidated findings comment and the re-review loop, capped at 2 rounds.
- **dev-leader** — out of the rework loop; owns the cycle's git-flow and finalizes on Review `done`.
- **devops** — owns any defect whose root cause lives in a pipeline or build script (Workflow D), regardless of confidence level.
- **Requester / workspace owner** — confirms delegation below the 90% confidence bar; receives blocker escalations that are outside squad control.

## Definition of Done / compliance

- Root cause identified — not the symptom — with `file:line` evidence and a calibrated confidence figure.
- A confirmed bug (≥ 90%) auto-delegated with the FYI comment posted; a low-confidence bug held for explicit requester confirmation before delegation.
- The fix lands at the shared layer callers route through; no sibling caller left broken.
- Every ticket follows the three-section `bug-report` shape and routes correctly on a zero-context read.
- Every PR-gate defect round is backed by a failing-then-passing reproduction test and a full green suite before `done`.

## Enforcement

`product-owner` runs Workflow A and applies the confidence gate on every bug/question main
ticket. `pr-reviewer` enforces the 2-round cap on the review loop before handing off. The PR gate ([Policy 04](04-code-and-spec-review.md)) verifies that a delivered
fix carries its proving test as part of the merge gate.

## Exceptions & waivers

- A bug needs a Workflow B spec only if the requester explicitly asks for one; the spec-review gate then applies as normal.
- A pipeline/build-script root cause is always Workflow D — the ≥ 90% auto-delegate to dev-team never applies to it.
- A `[P#-3]` phase created for a bug fix is typically a run-only re-verification cycle, not a fresh design phase.

## References

- [`bug-report`](../../skills/bug-report/SKILL.md) — the three-section body contract and consolidated multi-defect ticket format.
- [`blocker-report`](../../skills/blocker-report/SKILL.md) — the `## BLOCKER`/`## OPTIONS` escalation shape and the completion-report shape.
- Workflow A in `sdlc-flow-po-orchestration`; the dev-team review loop in `skills/pr-review-gate/references/multica-flow.md`.
- Delivery re-entry: [Policy 05](05-sdlc-delivery-lifecycle.md). Review gates a delivered fix passes through: [Policy 04](04-code-and-spec-review.md).
