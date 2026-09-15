# SDLC Flow — Squad Worker Playbook

For squad member agents (dev-backend, docs-writer, pr-reviewer, release-manager, devops) working staged sub-tasks under a leader. Your own instructions define your role, your quality gates and your leader's mention markdown; the Workspace Context defines statuses, wakes and ticket conventions. Your sub-task description is your brief: squad instructions go to the leader only, so everything you need is in the sub-task or in your skills.

## Mention contract

Exactly one wake per handoff, and the only agent you ever mention is your leader. When your status flip is the wake (`done` or `blocked` closes or poisons your stage barrier and wakes the leader), post no mention. When your status does not move in a way that wakes anyone, the mention is the only wake and you post it, on your own sub-task, last thing in the turn, at most one per turn. You never comment on, mention, or change another member's sub-task: whatever another member must hear (findings, a fix request, a question) goes on YOUR sub-task with the leader's mention, and the leader routes it.

**Rework.** After your sub-task is `done`, a review REWORK reaches you from the LEADER: the leader flips your sub-task `in_progress` and posts one comment on it with your mention, pointing at pr-reviewer's findings on the Review sub-task. Read the findings there, fix, push, and post your report on your own sub-task (completion shape, closure row per finding), then flip `done` — no mention: that second `done` re-fires the barrier and wakes the leader, who re-arms the review gate. Never post on the Review sub-task and never mention pr-reviewer. First command on a rework wake: `multica issue runs <your sub-task> --siblings`; another run of yours already in flight on this cycle means this wake is a duplicate — end the turn with no action, no push and no mention. One fix run per round; two runs pushing the same fix to one branch cost the cycle a rework round. The same holds for a sub-task the leader files above a non-terminal stage: your `done` closes no barrier, so end the report with dev-leader's mention (the brief says so when it applies).

## Self-review before you report done

Once the code is pushed and the suite is green, read `git diff origin/<base-branch>...HEAD` end to end as if someone else wrote it, then carry the results into the completion report. Seven checks, all of which the review gate will run anyway:

1. **Mutation report on every touched class.** Stryker (`dotnet stryker` / `npx stryker run`) scoped to touched classes; every survivor dispositioned (`killed — added <test>` / `equivalent` / `accepted — <why>`). Tool unavailable → manual: invert each guard you added, run, confirm RED, restore, and say the tool was unavailable.
2. **Grep your new assertions** for fragment matches (`ShouldContain`, `Contains`, substring asserts); each pins exact expected text or is anchored to its member.
3. **Branch coverage on every branch you added**: per-branch hits, not the class percentage. A 1-of-2 arm is covered or proven unreachable.
4. **Re-read the brief's prose**, not just §3: contract, rules, §9, every note. Each named edge case has a fact or an explicit "no fact, reason".
5. **Re-read every comment and doc comment you wrote or touched** against the code beside it.
6. **Scope.** `git diff --stat` shows nothing outside §3 and nothing in §4.
7. **Acceptance-test drift** (Build and rework): `git diff <at_sha>..HEAD -- <AT paths>` shows no modified or deleted approved scenario; every test you added is listed by file. A frozen AT you had to change is a `blocked` with the leader's mention, before any of this.

EVIDENCE carries one row per check with its measured result. Anything a check found that you could not fix inside §3 goes in LEFT OPEN with `file:line`; a self-review finding declared there is never held against the cycle. Docs and config sub-tasks run checks 4–6; Acceptance-tests sub-tasks run 2 and 4–6.

## Finishing a task

1. Decide the verdict against your role's gates. Never report done with a known failure or without self-review EVIDENCE rows.
2. On PASS: ONE plain comment on your own sub-task in completion shape (`blocker-report`: RESULT / EVIDENCE / LEFT OPEN, measured numbers), no mention, then flip `done`. The barrier wakes the leader; routing is the leader's job.
3. `done` means your work is complete, not that the leader approved it. A PR being up and awaiting review is exactly `done`.
4. Flip the status in the same turn as the report. A PASS comment with the ticket still `in_progress` wakes nobody.
5. After flipping `done`, check `multica issue children <parent-id>`: if a sibling at your stage or below is `blocked` (a Fix sub-task above a parked gate is the usual case), your `done` fired no barrier. Post one more comment on your own sub-task with your leader's mention. Your sub-task may carry `Retrigger on done`: that is the leader's bookkeeping for which gate to re-arm — never set, change or clear it.

## You never create issues

`multica issue create` is your leader's. Report what is wrong, where (`file:line`), what you recommend, verifiable acceptance criteria, the suggested owner, and for anything inside a cycle the stage number the fix must carry. The leader consolidates and files; a defect outside the cycle goes to product-owner's bug workflow.

## When you are blocked

Flip `blocked` and post the blocker on your own sub-task with your leader's mention, in `blocker-report` shape (`## BLOCKER`, then `## OPTIONS` with one ✅ Recommended, then `## QUESTIONS` when real). A human decision is your leader's hop, not yours. Spec ambiguity or scope questions: no guessing, no sub-task; ask the leader on your own sub-task.

## Delivering to the feature branch

The feature branch is the leader's, cut from `dev`, shared by the whole cycle. Commit and push to it directly (refspec push per `sdlc-gitflow`), verify `git rev-parse HEAD` equals `git rev-parse origin/<branch>` before reporting; work left on your `agent/...` branch is lost when the run ends. Never create branches or open PRs. If the named feature branch is missing on origin (`git ls-remote` empty), do not create it: `blocked` with the leader's mention.
