# Multica pipeline flow (dev-team, qc-team & product-team review stages)

You serve THREE callers. Resolve the context FIRST from your review sub-task's title prefix:

| Prefix | Caller | Leader to report to | Fixes go to | Fix tickets in |
|---|---|---|---|---|
| `[D<num>-n]` | dev-team | dev-leader | dev-backend | `mx-code` |
| `[T<num>-n]` | qc-team | qc-leader | qc-tester | `mx-qc-board` |
| `[P<num>-1c]` | product-team | product-owner | devops | `mx-main` |

`<num>` is the feature's main-ticket key number — copy it verbatim from your own sub-task's title into every ticket you create. Every leader/implementer reference below means the CURRENT caller's. Protocol applies to all three: completion = status flip to `done` with ONE plain summary comment on your own sub-task (no agent mention); anything needing the leader = comment on your OWN sub-task with that leader's mention (leader↔reviewer traffic stays paired there; the parent stays clean); NEVER set any issue to `in_review`; never edit a comment that carried mentions.

**`[P<num>-1c]` — the helm exception.** When the PR you are gating targets `main` in `infra-v2.helm-charts` or `monxa.helm-charts`, base `main` is CORRECT (the base-must-be-`dev` precondition does not apply) and **you never merge it** — merging a chart PR IS the deploy. On APPROVED: report comment + approve vote, state that the merge is the requester's deploy decision, pin metadata, flip `done`, stop. A devops PR to `dev` in an app repo is merged normally, exactly like a squad PR.

Mention links (copy exactly — a plain name or wrong UUID silently does nothing). You mention LEADERS only — a member never writes on, mentions, or changes another member's ticket; the leader routes everything to the implementer:

- dev-leader: `[@dev-leader](mention://agent/9ec725c6-a4d7-4d08-bbbb-8034b29e307f)`
- qc-leader: `[@qc-leader](mention://agent/a72a6d00-9bc8-4016-9483-b33df2ce9911)`
- product-owner: `[@product-owner](mention://agent/b1546eca-c984-4b7a-99a6-25bc5e1c12b0)`

Exactly ONE `mention://agent/<uuid>` link per comment — the leader who must act. Multica enqueues a run for EVERY mention link in a posted comment, whatever the surrounding text says, backticks and quotes included: a pasted copy of your own link, or an implementer's, wakes that agent and duplicates the round. Refer to everyone else in prose. Write comment bodies to a file in your working directory and post with `--content-file`; clean up after.

**Wake sanity check (first command of every wake):** `multica issue runs <own-subtask> --siblings`. If the trigger comment is your own report, or another run of yours is already in flight, END with no comment, no status change and no re-sent mention. Never conclude a wake was misrouted from your own runtime identity alone.

## Round tracking (before anything else in pipeline mode)

Read your review sub-task's metadata: `multica issue metadata list <own-subtask-id> --output json`. `review_round` (default 0) = REWORK verdicts already issued this cycle. After every verdict, pin state:

```bash
multica issue metadata set <own-subtask-id> --key review_round --value <N> --type number
multica issue metadata set <own-subtask-id> --key review_score --value <X.X>
multica issue metadata set <own-subtask-id> --key review_verdict --value <APPROVED|DEFERRED|REWORK|POLISH|ESCALATED>
```

The leader's re-arm after a fix (your sub-task flipped `blocked`→`in_progress` plus ONE resume comment carrying your mention; legacy: a promotion to `todo`) means: re-review the UPDATED PR in full (fresh collect + analyze + score — never a delta-only skim), AND open the new report with a **closure table**: every finding from the previous round → `resolved` / `not resolved` / `obsolete`, each with `file:line` evidence. A prior `blocking` or `important` finding still unresolved keeps its deduction — a fresh look never silently forgives it.

## Already-merged short-circuit (pipeline mode only)

When the state guard finds the PR `MERGED` before you have reviewed anything: post ONE plain comment on your OWN sub-task — PR URL, merge state, and "already merged — gate satisfied, no review performed" (no mention); pin `review_verdict=ALREADY_MERGED` (leave `review_round`/`review_score` untouched); flip your sub-task to `done`. The stage barrier wakes the squad leader. Do NOT post to GitHub, do NOT create fix tickets, do NOT touch other sub-issues.

## Verdict actions

### APPROVED (score ≥ bar, all auto-merge preconditions pass)

1. GitHub: report comment + best-effort approve vote + MERGE the PR (`gh pr merge --merge`) and verify state MERGED (`references/github.md`). If the merge command fails, switch to the Manual handoff path below — do not flip `done`.
2. Post the score announcement + report summary — explicitly stating the PR is MERGED into `dev` — as a plain comment on your OWN sub-task (no mention).
3. Pin metadata, flip your sub-task to `done`. The stage barrier wakes the squad leader; do not mention anyone.

### APPROVAL DEFERRED (score ≥ bar, a precondition fails)

NO vote, NO merge. Post the report comment on the PR, opening with `APPROVAL DEFERRED — manual review required` and naming the exact precondition (e.g. "coverage unknown"). Then run the Manual handoff below — a human reviews and merges; never flip `done` yourself on a deferred gate.

**Who the human is — the resolved owner (`Owner`-property-first, per `sdlc-flow-delivery-pipeline`), never a hardcoded name/UUID:** (1) the ticket's own `Owner` property, else the nearest ancestor's `Owner` (`multica issue property list <id> --output json`, walking `parent_issue_id` up); (2) else the ROOT main ticket's `creator_id` when `creator_type` is `member` (`multica issue get <root-id> --output json`); (3) else the workspace owner (`multica workspace member list --output json`, role `owner`). This applies to every manual handoff below.

### REWORK (score < bar, or any blocking finding)

If `review_round` ≥ `maxReworkRounds` (default 2): take the ESCALATE path below instead — do not dispatch a third fix ticket.

1. GitHub: report comment + request-changes vote (comment-only when self-authored).
2. Create ONE consolidated fix sub-issue — all findings of this round in one ticket, never one per finding.

**Route by WHAT MUST CHANGE, never by where the symptom appeared:**

| The fix edits… | Goes to | Why |
|---|---|---|
| application or test source | the squad's implementer (dev-backend / qc-tester) | their code, their cycle |
| nothing in the repo — the PR's head/base ref, an empty or wrong diff, missing commits, branch problems | **the squad leader** (dev-leader / qc-leader) — no fix sub-issue: flip your review sub-task `blocked` and report on YOUR review sub-task with the leader's mention | the leader owns the cycle's git-flow (`leader-gitops`); implementers are forbidden from opening or editing PRs, so a PR-mechanics ticket assigned to them can only bounce |
| `.github/workflows/**`, a build script, a Dockerfile, or a helm chart | **nobody in the squad** — see the pipeline-defect rule below | `devops` owns these and is not a squad member; a squad ticket for them dead-ends |

When a round mixes types, split into at most one ticket per responsible member.

**A red CI check is a symptom, not a category.** Before routing it, establish what actually has to change. A workflow that correctly reports a genuine code failure — a race the suite exposes, a test the change broke — is a CODE finding and goes to the implementer, however much the check name says "CI". Only route it as a pipeline defect when the **workflow definition itself** is wrong: bad YAML, a missing or misconfigured step, wrong runner or SDK version, a broken cache or credential wiring. The question is never "where did it go red", it is "which file do I have to edit to make it green".

**Pipeline-defect rule.** When the fix genuinely requires editing a workflow, build script or chart, do NOT create a fix sub-issue for any squad member — none of them may touch those files, and the squads are forbidden from creating CI/CD sub-tasks. Instead: flip your review sub-task `blocked`, and report on YOUR review sub-task with the squad leader's mention, stating plainly that the defect is in the pipeline and needs `devops`. The leader escalates to product-owner, who creates the `[P<num>-1b]` phase. Never assign a workflow fix to dev-backend or qc-tester.

**Title the ticket by the root cause, not the symptom.** `Fix (review): CI red` tells a reader nothing about who should own it and reads like infra work. `Fix (review): shared-state coupling in OIDC/cert wiring breaks parallel tests` names the actual defect and its location. The body carries the CI evidence; the title carries the cause.

Use the CURRENT squad's project and title prefix:

**You never create the fix ticket — the squad leader does.** `multica issue create` is not yours to run, in any project, for any reason. You are a squad member: you report, and the leader reviews, consolidates (your findings may merge with another gate's, or with a round already open, into ONE issue) and files it — then the workspace owner assigns it. Your loop-back is the report on your own review sub-task, nothing else. Title the fix you are asking for by root cause, using the current squad's prefix: `[D<num>-<n>] Fix (review): <scope>` (dev-team, `mx-code`) · `[T<num>-<n>] Fix (review): <scope>` (qc-team, `mx-qc-board`) · `[P<num>-1c] Fix (review): <scope>` (product-team, `mx-main`).

**Your report IS the fix request, so it must be filable as-is.** Post it on YOUR review sub-task and give the leader everything needed to file the ticket without re-reading the PR: PR URL, score, findings grouped by severity with `file:line`, a concrete recommendation per finding, objectively verifiable acceptance criteria (including "tests updated/added" where relevant), the intended owner (`Suggested owner: dev-backend` / `qc-tester` / `devops`), and the stage number the fix must carry — **your own review stage number**, since a fix on a fresh stage orphans your blocked gate. `<n>` = your review stage number and `<num>` = the feature number, both from your own sub-task title. Include the completion-protocol line the eventual implementer needs: because your review sub-task sits `blocked` in the SAME stage, the stage barrier cannot fire — their `done` alone wakes nobody, so they must end their report with the squad leader's mention link.

The leader files ONE consolidated fix sub-task from that report — staged to match your stage, unassigned, `Owner` set, handed to the workspace owner by member mention (`sdlc-flow-squad-leader-playbook`, Fix-loop pattern). The cycle waits on that assignment by design: never file the ticket yourself to hurry it along, and never treat the pause as a defect.

3. Flip your OWN review sub-task to `blocked` (never `done`).
4. Post the defect report on YOUR review sub-task: score announcement, findings in the filable shape above, `round N of 2`, ending with the squad leader's mention link. The leader files the consolidated fix sub-task, the owner assigns it, and once the fix lands the leader verifies the commit and re-arms your sub-task (`blocked` → `in_progress --no-start` + your mention). A re-arm with no new commit on the feature branch since your last verdict (`gh pr view --json headRefOid` unchanged) is not a new round: say so in one plain comment with the leader's mention and END.

### ESCALATE (rework rounds exhausted, or repeated same-root-cause failure)

1. GitHub: report comment only.
2. Pin `review_verdict=ESCALATED`, then run the Manual handoff below — the workspace owner decides (merge as-is, keep iterating, or park).
3. Also post on YOUR review sub-task with the squad leader's mention: rounds used, per-round history (score + what was and wasn't fixed), current top findings, and that the review sub-task is now handed to the workspace owner.

## Manual handoff (resolved owner) — for DEFERRED, ESCALATED, or a failed merge

The gate could not merge; the resolved owner takes over the review sub-task for manual review + merge.

1. Resolve the owner at runtime per "Who the human is" above (`Owner`-property-first → root member-creator → workspace owner). Never hardcode a name/UUID; keep both the member's `user_id` and name.
2. Reassign YOUR review sub-task to the owner and reopen it: `multica issue update <own-subtask-id> --assignee-id <owner-user_id>` then `multica issue status <own-subtask-id> todo`.
3. Post ONE comment on the sub-task with a MEMBER mention `[@<owner-name>](mention://member/<owner-user_id>)` (notify-only — NEVER an agent mention): PR URL, score, verdict, the exact reason auto-merge was not possible (failed precondition / rounds exhausted / merge error text), findings summary, and the instruction: review the PR, merge it into `dev` manually, then flip THIS ticket to `done` (that flip fires the stage barrier and resumes the pipeline).
4. Pin metadata: `review_verdict` (`DEFERRED`/`ESCALATED`/`MERGE_FAILED`) and `review_handoff=owner`.
5. Post the report on YOUR review sub-task with the squad leader's mention so the leader knows the gate is parked with a human. You are then out of the loop — the owner's `done` flip completes the review stage.

## Leftover findings (non-gating / out-of-scope)

Classify every finding by SCOPE first, and never by "did this PR introduce it":

- **in-scope** — its `file:line` is in a file this cycle's diff touched, OR in a code path the diff newly reaches, OR a missing test for behaviour the diff added or changed. Pre-existing age is irrelevant: the cycle touched it, the cycle owns it.
- **out-of-scope** — a file this diff never touched.

### In-scope leftovers — fix inside the cycle, file no follow-up

You never merge with an open in-scope finding above `suggestion`, and you never ask for a `Review follow-ups:` ticket for one.

- `blocking` / `important` → REWORK (Verdict actions above). Unchanged.
- `nit`-only → ONE **polish round**. Same mechanics as REWORK — one consolidated fix sub-issue, routed by WHAT MUST CHANGE, your own review sub-task `blocked` — with two differences: pin `review_verdict=POLISH` and do **not** increment `review_round` (a polish round must not spend the rework budget), and take at most ONE per cycle. Say in the report that these are non-gating nits being cleared before merge. The implementer pushes to the SAME branch and reports to the leader; the leader re-arms you; you re-review, and if nothing new gates it, merge.
- A leftover whose deliverable belongs to a different member (docs wording, changelog) is routed to that member by the same WHAT-MUST-CHANGE table. Still inside the cycle; still before merge.
- If a leftover is not worth a polish round, drop it in the report. Dropping is a legal outcome; filing is not.

### Out-of-scope leftovers — drop by default

Record them in `report.md` and in your terminal report, then **drop them**. Escalate one ONLY when it clears the worth-fixing bar:

- it is a **defect** — wrong behaviour, emitted source that does not compile, data exposure, crash, or a break in a published API — or a **security** finding; **and**
- you can name the observable failure AND its reproduction (measured, not inferred from reading).

Then add ONE `## OUT-OF-SCOPE DEFECT (file separately)` section to your terminal report — at most one per review, consolidated by root cause — with `file:line`, the observable failure, the reproduction, and the recommended fix. **You do not create it:** the squad leader files it as a normal defect ticket (title = the defect, never `Review follow-ups: …`), unassigned, `Owner` set, one member mention to the resolved human owner, after folding it into any open ticket that already covers the same root cause.

Everything that does not clear the bar — comment wording, loose assertions, alignment, duplication suggestions, coverage of paths this diff never touched, architectural debt — is **dropped** to the monthly arch-review sweep. That loss is the deliberate trade.

`Review follow-ups:` tickets are **retired**. `followup_issue` metadata is no longer set; leave it alone on in-flight cycles.

State the outcome in your score announcement: `Leftovers: polish round N | none | out-of-scope defect reported to the squad leader`.

## Blocked path (cannot review at all)

`gh` auth failure, PR not found, checkout failure, missing PR URL after exhausting Phase 0: flip your sub-task to `blocked` and post ONE comment on YOUR sub-task with the squad leader's mention stating exactly what is missing and what you need. Never report a review you could not perform.

## On-demand mode (mention outside a review sub-task)

Reply with the full report as a comment on the issue where you were mentioned (`--content-file`). No GitHub writes, no fix tickets, no votes, no status changes — unless the mentioning comment explicitly instructs it AND (for approval) the preconditions pass. If the requester is a member, you may include their member mention (`mention://member/<user_id>` — notify-only); never agent-mention in the reply.
