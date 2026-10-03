# Recovery — stuck, stalled, duplicated or mis-signalled children

Open this when the wake-up checklist finds a child that is `blocked`, failed, silent, duplicated, or reporting the wrong state. A stuck sub-task never stops the cycle: every wake that finds one ends in exactly one of a loop-back dispatched, a stage resumed or promoted, or an escalation posted.

## Loop

1. **Diagnose** the root-cause stage: the stuck sub-task itself, or an earlier stage whose deliverable is defective (missing branch, broken build, wrong artifact, wrong approved AT).
2. **Loop back**: re-arm the root-cause sub-task — flip it `in_progress` (`multica issue status <id> in_progress --no-start`) whether it sits `blocked` or `done`, then ONE corrective comment carrying the assignee's mention: the exact defect, the evidence, and what "fixed" looks like. Flip first, mention last; its return to `done` wakes you to verify — the stage barrier, or its handoff line while a sibling at its stage or below is still `blocked`. Downstream stays `blocked`/`backlog`. A wrong approved AT is fixed by re-arming Acceptance tests and re-pinning `at_sha`, never by editing it in Build.
3. **Resume forward** when it returns: verify the failure is actually resolved, then re-arm the stalled downstream sub-task (`in_progress --no-start` + assignee mention).
4. **Escalate instead of spinning** after 2 failed fix attempts on one root cause, or when the cause is outside squad control (product decision, credentials, environment, scope): phase-ticket cycle → ONE comment on your own phase ticket, then your handoff line on the root with product-owner's mention; root-ticket cycle → reassign the stuck ticket to the resolved owner at `todo` with a `## BLOCKER` comment (`blocker-report`). Never take back a ticket a human holds.

## Stall detection

A `blocked` Review whose findings you have not yet routed (no `in_progress` implementer sub-task carrying your routing comment) means your own wake was lost: route it now (playbook, Rework step 1). A `blocked` Review with `Gate verdict` = MERGE_FAILED is a merge for you to fix, not findings to route (playbook, **Failed merge and the owner's choice**). A Review held by the owner with `Gate verdict` = ESCALATED is not stalled: it waits for the owner's letter. A routed round with no implementer report for a full run window: first `multica issue runs <build-sub-task> --siblings`; an implementer run in flight means the fix is under way — do nothing, and say so if a human asked (never file a fix sub-task or re-mention next to a live run; a second run on the same branch duplicates the fix and burns a rework round). No active run: ONE corrective comment on the implementer's sub-task with its mention (it is already `in_progress`). A `done` child still carrying `Retrigger on done` while an issue it names sits `blocked` (and every child naming that issue is `done`) means your re-arm was lost: re-arm that issue now (playbook, checklist item 1) and drop its key from the property, unsetting it when none is left. Nothing else. An `in_progress` sub-task with a silent assignee for a run window: check `multica issue runs <id> --active --output json`; no active run → re-arm (it is already `in_progress`) with a corrective comment and mention.

## Barrier frontier

Stage N's barrier fires only when every sub-task at stage ≤ N is terminal. While Review sits `blocked` at stage 3, a fix or scope sub-task at stage 4 goes `done` and the barrier stays silent: that member posts its handoff line instead (Workspace Context). A member that forgot it leaves its `done` unseen until your next wake, so every wake acts on every child's state (checklist items 1–4), never only on the child the line names.

## Duplicates

Two decomposition chains, or two sub-tasks with the same purpose at the same stage: keep the older by `created_at`, cancel the rest (`multica issue cancel-task <run-id> --issue <dup-id>` for any live run first, then `multica issue update <dup-id> --status cancelled`), and pin the correct branch and artifacts on the canonical chain. Oldest wins because two concurrent sessions reach the same answer only from `created_at`.

## Duplicate roots

Two root tickets share a root cause when their root-cause reports name the same mechanism at the same `file:line`. The older one by `created_at` is canonical (Policy 07 statement 8a). A root a human holds is not yours to cancel (Loop step 4).

**Before decomposing a root:** `multica issue search "<root-cause file or symbol>" --output json` (open issues only: a closed older root is a regression, not a duplicate), then read the root-cause report of every root it returns for the same repo.
- An older duplicate exists: cut no branch. Post ONE comment on this root: "Duplicate of <older key>, filed earlier with the same root cause; its cycle carries the fix." Then `multica issue update <root-id> --status cancelled`. No mention.
- Only newer ones exist: carry on. Their own sessions cancel them.

**After a failed merge:** Review is `blocked` with `Gate verdict` = MERGE_FAILED, and pr-reviewer's comment carries a `Duplicate probe` naming the older root and its merged PR.
- The scenarios that reproduce this root's observable failure are green on `dev`:
  1. `gh pr close <PR#> -R baoduy/<repo> --comment "Superseded by #<older PR> (<older key>): same root cause, already merged into dev."`
  2. Cancel every open sub-task, Review and Release included: `multica issue cancel-task <run-id> --issue <id>` for any live run first, then `multica issue update <id> --status cancelled`.
  3. Any `@new` scenario still red on `dev` → ONE defect per `references/issue-filing.md`. It names those scenarios, the behaviour they assert, and the older fix's contract that contradicts it (its CHANGELOG line or `<remarks>`). product-owner triages whether the behaviour is wanted. None red → nothing to file.
  4. ONE completion comment on the root (`blocker-report`). RESULT: duplicate of <older key>, PR closed. EVIDENCE: the probe table. LEFT OPEN: the filed defect key, or `none`. Then `multica issue update <root-id> --status cancelled`. No mention.
- Anything else is a substantive conflict, escalated per Loop step 4: no probe, a probe that did not compile or run, failure scenarios red on `dev`, or a root cause you cannot match. Never rebase it, and never edit an approved acceptance test.

## Substantive merge conflicts

Mechanical conflicts are yours (`leader-gitops`). Overlapping logic or deleted code is feature code: ONE comment on dev-backend's Build sub-task listing the conflicted paths with dev-backend's mention, asking it to report on that sub-task and post its handoff line when pushed; re-verify `MERGEABLE` when it lands. No fix sub-task.
