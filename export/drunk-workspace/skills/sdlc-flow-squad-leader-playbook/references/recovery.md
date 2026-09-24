# Recovery — stuck, stalled, duplicated or mis-signalled children

Open this when the wake-up checklist finds a child that is `blocked`, failed, silent, duplicated, or reporting the wrong state. A stuck sub-task never stops the cycle: every wake that finds one ends in exactly one of a loop-back dispatched, a stage resumed or promoted, or an escalation posted.

## Loop

1. **Diagnose** the root-cause stage: the stuck sub-task itself, or an earlier stage whose deliverable is defective (missing branch, broken build, wrong artifact, wrong approved AT).
2. **Loop back**: re-arm the root-cause sub-task — flip it `in_progress` (`multica issue status <id> in_progress --no-start`) whether it sits `blocked` or `done`, then ONE corrective comment carrying the assignee's mention: the exact defect, the evidence, and what "fixed" looks like. Flip first, mention last; its return to `done` re-fires the barrier and wakes you to verify. Downstream stays `blocked`/`backlog`. A wrong approved AT is fixed by re-arming Acceptance tests and re-pinning `at_sha`, never by editing it in Build.
3. **Resume forward** when it returns: verify the failure is actually resolved, then re-arm the stalled downstream sub-task (`in_progress --no-start` + assignee mention).
4. **Escalate instead of spinning** after 2 failed fix attempts on one root cause, or when the cause is outside squad control (product decision, credentials, environment, scope): phase-ticket cycle → ONE comment on your own phase ticket with product-owner's mention; root-ticket cycle → reassign the stuck ticket to the resolved owner at `todo` with a `## BLOCKER` comment (`blocker-report`). Never take back a ticket a human holds.

## Stall detection

A `blocked` Review whose findings you have not yet routed (no `in_progress` implementer sub-task carrying your routing comment) means your own wake was lost: route it now (playbook, Rework step 1). A routed round with no implementer report for a full run window: first `multica issue runs <build-sub-task> --siblings`; an implementer run in flight means the fix is under way — do nothing, and say so if a human asked (never file a fix sub-task or re-mention next to a live run; a second run on the same branch duplicates the fix and burns a rework round). No active run: ONE corrective comment on the implementer's sub-task with its mention (it is already `in_progress`). A `done` child still carrying `Retrigger on done` while an issue it names sits `blocked` (and every child naming that issue is `done`) means your re-arm was lost: re-arm that issue now (playbook, checklist item 1) and drop its key from the property, unsetting it when none is left. Nothing else. An `in_progress` sub-task with a silent assignee for a run window: check `multica issue runs <id> --active --output json`; no active run → re-arm (it is already `in_progress`) with a corrective comment and mention.

## Barrier frontier

Stage N's barrier fires only when every sub-task at stage ≤ N is terminal. While Review sits `blocked` at stage 3, a fix or scope sub-task at stage 4 goes `done` and wakes nobody. Treat such a sub-task's completion as a mention-driven handoff: its brief says to end the report with your mention, and you check for that report on every wake rather than waiting for a barrier.

## Duplicates

Two decomposition chains, or two sub-tasks with the same purpose at the same stage: keep the older by `created_at`, cancel the rest (`multica issue cancel-task <run-id> --issue <dup-id>` for any live run first, then `multica issue update <dup-id> --status cancelled`), and pin the correct branch and artifacts on the canonical chain. Oldest wins because two concurrent sessions reach the same answer only from `created_at`.

## Substantive merge conflicts

Mechanical conflicts are yours (`leader-gitops`). Overlapping logic or deleted code is feature code: ONE comment on dev-backend's Build sub-task listing the conflicted paths with dev-backend's mention, asking it to report back on that sub-task with your mention when pushed; re-verify `MERGEABLE` when it lands. No fix sub-task.
