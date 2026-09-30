# Multica pipeline flow (dev-team review stage)

You serve the dev-team. Your review sub-task's title prefix is `[D<num>-<n>]` (legacy `[DEV-<n>]` on in-flight cycles) (leader dev-leader; rework findings go on your OWN sub-task and your handoff line on the cycle parent wakes the leader, who routes them to the implementer; no fix tickets, and you never write on another member's ticket). Any ticket raised from your findings lives in the SAME project as the cycle ticket — resolve it at runtime from the cycle ticket's `project_id`, never by a hardcoded board name. `<num>` (the cycle parent phase ticket's key number) and `<n>` (your review stage number) both come from your own sub-task's title — copy them verbatim into every ticket you create. Squad protocol applies: completion = `done` with ONE plain summary comment on your own sub-task (no agent mention) — the stage barrier wakes dev-leader; anything needing dev-leader = comment on your OWN sub-task, then your handoff line on the cycle parent (Workspace Context); never edit a comment that carried mentions.

Mention links are built at run time, never remembered: `multica agent list --output json`, take the `id` of the agent by name, write `[@<name>](mention://agent/<that id>)`. A plain name, a guessed id or the literal `<that id>` placeholder silently does nothing. The only mention this stage ever posts is product-owner's, in your handoff line on a `[P<num>-1c]` (its parent is product-owner's ticket); on a dev-team Review sub-task the handoff line carries no mention, because the platform routes it to dev-leader.

Mention exactly ONE agent per comment — the one who must act.

## Standalone PR (`[P<num>-1c]`, product-team)

A `[P<num>-1c] Review CI/CD PR`, `Review docs PR` or `Review design PR` gates devops' `chore/<key>`, docs-writer's `docs/<key>` or service-architect's `design/<key>` PR. Everything in this file applies with three substitutions: the leader is **product-owner** — every dev-leader hop and mention below goes to product-owner; the PR URL is in product-owner's promotion comment on your own sub-task; and the findings form ONE group for the PR's author (devops, docs-writer or service-architect), git/PR mechanics included. product-owner re-arms you the same way dev-leader does. A design PR never merges on score — see Design PR owner review below. A docs or design PR that adds or changes a runtime architecture diagram (`runtime.architecture.json`) is checked against its shape (Policy 05 statement 3a): archify `architecture`, 8–12 components, one primary path, the external dependencies and trust boundaries drawn, supporting detail in cards, and on a docs PR the repo-root README links `docs/diagrams/runtime.svg`. Each miss is `blocking` (owner's decision, 2026-09-30): one miss caps the PR at 6.9, whatever the docs-only floor.

## Round tracking (before anything else in pipeline mode)

Read your review sub-task's properties: `multica issue property list <own-subtask-id> --output json`. `Gate round` (unset = 0) = REWORK verdicts already issued this cycle — a POLISH round does NOT count and is at most one per cycle (`Gate verdict` = POLISH marks that it was spent). After every verdict, pin state:

```bash
multica issue property set <own-subtask-id> --name "Gate round" --value <N>
multica issue property set <own-subtask-id> --name "Gate score" --value <X.X>
multica issue property set <own-subtask-id> --name "Gate verdict" --value <APPROVED|REWORK|POLISH|ESCALATED|MERGE_FAILED|ALREADY_MERGED|OWNER_MERGED>
```

Properties show on the board and in `multica issue children --resolve-properties`, which is how the leader and the human see a parked gate without opening threads.

The leader's re-arm after a fix (your sub-task flipped `in_progress` + your mention on it; legacy: a promotion from `blocked` to `todo`) means: re-review the UPDATED PR in full (fresh collect + analyze + score — never a delta-only skim), AND open the new report with a **closure table**: every finding from the previous round → `resolved` / `not resolved` / `obsolete`, each with `file:line` evidence. A prior `blocking` or `important` finding still unresolved keeps its deduction — a fresh look never silently forgives it.

## Already-merged short-circuit (pipeline mode only)

When the state guard finds the PR `MERGED` before you have reviewed anything: post ONE plain comment on your OWN sub-task — PR URL, merge state, and "already merged — gate satisfied, no review performed" (no mention); pin `Gate verdict` = ALREADY_MERGED (leave `Gate round`/`Gate score` untouched); flip your sub-task to `done`. The stage barrier wakes the squad leader. Do NOT post to GitHub, do NOT create fix tickets, do NOT touch other sub-issues.

## Verdict actions

### APPROVED (score ≥ bar, zero `blocking`)

1. GitHub: `release-review` label first when a trigger applies (SKILL.md, Release-review label), then report comment + best-effort approve vote + MERGE the PR (`gh pr merge --merge`) and verify state MERGED (`references/github.md`). If the merge fails, take the MERGE_FAILED path below — do not flip `done`.
2. Post the score announcement + report summary — explicitly stating the PR is MERGED into `dev`, the release-review trigger(s) or `none`, and anything noted at merge (CI pending, CI red not caused by this PR, coverage unknown, large diff) — as a plain comment on your OWN sub-task (no mention).
3. Pin properties, flip your sub-task to `done`. The stage barrier wakes the squad leader; do not mention anyone.

There is no deferred verdict. A passing PR is never reassigned to a human, whatever the report notes — the one exception is a `design/<key>` PR, below.

### Design PR owner review (`[P<num>-1c] Review design PR`, score ≥ bar, zero `blocking`)

A service design binds every later spec and PR in its repo, so the owner approves it (Policy 04 statement 9a). Do NOT merge.

1. GitHub: report comment + best-effort approve vote. No merge, no label.
2. Pin `Gate verdict` = APPROVED, `Gate score`, `Gate round` as usual.
3. Resolve the owner (Owner handoff step 1 below), reassign your sub-task to them and reopen it at `todo` (step 2).
4. Post ONE comment in the `blocker-report` Blocker shape, written to a file. `## BLOCKER`: "Service design ready for your approval", PR URL, score, the design's file list and diagrams — the runtime architecture diagram first, since the owner approves it with the design — the open points the author reported; **From:** the owner's MEMBER mention (notify-only). `## OPTIONS`, A first:
   - **A — approve and merge.** The design lands on `dev` and binds the repo.
   - **B — revise, with your guidance.** Say what to change; product-owner routes it to service-architect and you re-review once it lands.
   - **C — park.** The PR stays open; nothing proceeds.
   - **D — close.** You close the PR; product-owner cancels the design phases.

   Close with: "Reply with the letter and product-owner's mention (plus your guidance for B)." Name product-owner in prose — this comment carries no agent mention link.
5. Post nothing else. product-owner hands the sub-task back with the owner's choice. **A** → as the Owner's choice A below: head unchanged → merge, pin OWNER_MERGED, `done`; head moved → re-review in full. **B** → re-review in full once the fix lands; a pass comes back to this section, and an owner's B round does not increment `Gate round`. The owner may instead merge on GitHub: the state guard then records ALREADY_MERGED.

### MERGE_FAILED (score ≥ bar, the merge did not happen)

A draft PR, a late conflict because `dev` moved, or any other `gh pr merge` error. PR mechanics are dev-leader's (`leader-gitops`), so the fix goes there, never to the owner.

1. Keep the score; do not re-score and do not touch `Gate round`.
2. Post ONE comment on your OWN sub-task: PR URL, score, the exact error text in a code block, and what dev-leader must do (mark ready, bring the branch up to date with `dev`, or escalate a failure it cannot fix — permission, branch protection — per its recovery rules). No mention.
3. Flip your sub-task `blocked`, pin `Gate verdict` = MERGE_FAILED, then post your handoff line on the parent.
4. On dev-leader's re-arm: head unchanged (`gh pr view --json headRefOid`) → re-check state and merge the already-scored PR; head changed (the branch was updated from `dev`) → re-review in full as a normal re-review. Either way END with a verdict.

### REWORK (score < bar, or any blocking finding)

If `Gate round` ≥ `maxReworkRounds` (default 3) and the PR still fails the bar or carries a blocking finding: take the ESCALATE path below — never a fourth round, and never a run that ends without a verdict.

**No fix ticket, no comment on anyone else's ticket.** Rework is routed by the squad leader: you report on your own Review sub-task, the leader carries the findings to the implementer and brings the fix back to you.

1. GitHub: report comment + request-changes vote (comment-only when self-authored).
2. Group the findings by who fixes them: code/test/coverage/changelog → **dev-backend**; git/PR-mechanics (wrong head or base ref, empty or wrong diff, missing commits, branch problems) → **dev-leader** (owner of the cycle's git-flow per `leader-gitops`). Name the group headings so the leader can route each to the right `[D<num>-n]` sub-task.
3. Post ONE consolidated findings comment on your OWN review sub-task (write to a file, `--content-file`). Body: PR URL, score, `round N of 3`, findings grouped per implementer then by severity with `file:line`, a concrete recommendation per finding, objectively verifiable acceptance criteria (including "tests updated/added" where relevant), and this closing line: "dev-leader: please route each group to its implementer's sub-task and re-arm this gate when the fixes are pushed." The comment carries no `mention://` link at all: Multica enqueues a run for every mention link in a posted comment, whatever the surrounding text says, backticks and quotes included, so a pasted link wakes that agent and duplicates the round. Refer to everyone in prose.
4. Flip your OWN review sub-task to `blocked` (never `done`). Pin properties (`Gate round`, `Gate score`, `Gate verdict` = REWORK). Then post your handoff line on the cycle parent (`<KEY> blocked — REWORK round N on <KEY>`, no mention): it is the round's only wake; post nothing else and touch no other ticket.

**Wake sanity check (first command of every wake):** `multica issue runs <own-subtask> --siblings`. If the trigger comment is your own findings comment, or another run of yours is already in flight, END with no comment, no status change and no handoff line. Never conclude a wake was misrouted from your own runtime identity alone.

**Re-review trigger:** the leader's re-arm — your review sub-task flipped `in_progress` and ONE comment on it with your mention pointing at the fix report(s). A re-arm with no new commit on the feature branch since your last verdict (`gh pr view --json headRefOid` unchanged) is not a new round: say so in one plain comment, flip your sub-task back to `blocked`, post your handoff line and END. Otherwise confirm the reported commits are on the feature branch (`git ls-remote origin <feature-branch>` / `gh pr view --json headRefOid`), re-review the UPDATED PR in full (Round tracking above: fresh collect + analyze + score, closure table first), and END with a verdict from this table — APPROVED (merge), REWORK (only while `Gate round` < 3), or ESCALATED. The round cap never leaves the gate parked: with rounds spent and the bar met, you merge. (After MERGE_FAILED, an unchanged head means "retry the merge", not "no new round" — see MERGE_FAILED above.)

### ESCALATE (rework rounds exhausted, or repeated same-root-cause failure)

`Gate round` = 3 and the PR still fails the bar or carries a `blocking` finding — including the re-review after a round the owner granted with option B. This is the only verdict that reaches a human, and the pipeline waits on the owner's reply.

1. GitHub: report comment only.
2. Pin `Gate verdict` = ESCALATED, then run the Owner handoff below.

## Owner handoff (ESCALATED only)

1. Resolve the owner at runtime per `sdlc-flow-delivery-pipeline` "Who the human owner is" (`Owner`-property-first: your review sub-task's own `Owner`, else nearest ancestor's `Owner` via `multica issue property list <id> --output json`; else ROOT ticket `creator_id` when `creator_type` is `member`; else workspace owner via `multica workspace member list --output json`, role `owner`). Never hardcode a name/UUID; keep both the member's `user_id` and name.
2. Reassign YOUR review sub-task to the owner and reopen it: `multica issue update <own-subtask-id> --assignee-id <owner-user_id>` then `multica issue status <own-subtask-id> todo`.
3. Post ONE comment on the sub-task in the `blocker-report` Blocker shape, written to a file. `## BLOCKER`: PR URL, score, rounds used with the per-round history (score + what was and wasn't fixed), the open findings with `file:line`; **From:** the owner's MEMBER mention `[@<owner-name>](mention://member/<owner-user_id>)` (notify-only). `## OPTIONS`, recommendation first:
   - **A — merge as-is.** The open findings ship to `dev`. Leave A out, and say why, when the diff holds a secret or a `blocking (critical)` finding.
   - **B — one more round, with your guidance.** Say what to fix or accept; dev-leader routes it and you re-review once more.
   - **C — park.** No reply needed; the PR stays open and the cycle waits with you.
   - **D — close the PR.** dev-leader closes it and hands the work back to its parent's owner to re-scope or cancel.

   Close with: "Reply with the letter and dev-leader's mention (plus your guidance for B)." Name dev-leader in prose — this comment carries no agent mention link.
4. Post nothing else. You are out of the loop until dev-leader re-arms you with the owner's choice.

## Owner's choice (relayed by dev-leader; by product-owner on a `[P<num>-1c]`)

dev-leader reassigns the sub-task back to you (`--no-start`), flips it `in_progress --no-start` and mentions you with the owner's reply quoted and linked — that mention is the wake. Confirm the reply on your sub-task is from the resolved owner (a member), then:

- **A** — re-check `gh pr view --json state,headRefOid`. Still `OPEN` at the head you escalated → merge (`gh pr merge --merge`, verify MERGED), post a plain comment "merged on the owner's decision" naming the owner and linking the reply, pin `Gate verdict` = OWNER_MERGED (leave `Gate score` at your last score), flip `done`. The head moved → re-review in full instead. No `release-review` label: the owner has just reviewed it.
- **B** — this is a normal re-review once the fix lands: END with APPROVED or ESCALATED. Never a REWORK verdict at `Gate round` = 3.

## Leftover findings (non-gating / out-of-scope)

Classify every finding by SCOPE first, and never by "did this PR introduce it":

- **in-scope** — its `file:line` is in a file this cycle's diff touched, OR in a code path the diff newly reaches, OR a missing fact for behaviour the diff added or changed. Pre-existing age is irrelevant: the cycle touched it, the cycle owns it.
- **out-of-scope** — a file this diff never touched.

### In-scope leftovers — fix inside the cycle, file nothing

You never merge with an open in-scope finding above `suggestion`, and you never ask for a ticket for one.

- `blocking` / `important` → REWORK (Verdict actions above). Unchanged.
- `nit`-only → ONE **polish round**. Same mechanics as REWORK — consolidated findings comment on your own review sub-task (no mention), your own review sub-task `blocked`, your handoff line, leader routes and re-arms — with two differences: pin `Gate verdict` = POLISH and do **not** increment `Gate round` (a polish round must not spend the rework budget), and take at most ONE per cycle. Say in the comment that these are non-gating nits being cleared before merge. The implementer pushes onto the SAME feature branch; the leader re-arms you; you re-review, and if nothing new gates it, merge.
- If a leftover is genuinely not worth a polish round, drop it in the report. Dropping is a legal outcome; filing is not.

### Out-of-scope leftovers — drop by default

Record them in `report.md` and in your terminal report, then **drop them**. File one ONLY when it clears the worth-fixing bar:

- it is a **defect** — wrong behaviour, emitted source that does not compile, data exposure, crash, or a break in a published API — or a **security** finding; **and**
- you can name the observable failure AND its reproduction (measured, not inferred from reading).

Then add ONE `## OUT-OF-SCOPE DEFECT (file separately)` section to your terminal report — at most one per review, consolidated by root cause — with `file:line`, the observable failure, the reproduction, and the recommended fix. **You do not create it:** dev-leader files it as a `bug-report` ticket (title = the defect, never `Review follow-ups: …`) assigned to product-owner at `todo`, `Owner` set, after folding it into any open ticket that already covers the same root cause.

Everything that does not clear the bar — comment wording, loose assertions, alignment, duplication suggestions, coverage of paths this diff never touched, architectural debt — is **dropped** to the monthly arch-review sweep. That loss is the deliberate trade.

`Review follow-ups:` tickets are **retired**.

State the outcome in your score announcement: `Leftovers: polish round N | none | out-of-scope defect reported to dev-leader`.

## Blocked path (cannot review at all)

`gh` auth failure, PR not found, checkout failure, missing PR URL after exhausting Phase 0: post ONE comment on YOUR sub-task stating exactly what is missing and what you need, flip it `blocked`, then post your handoff line on the parent. Never report a review you could not perform.

## On-demand mode (mention outside a review sub-task)

Reply with the full report as a comment on the issue where you were mentioned (`--content-file`). No GitHub writes, no fix tickets, no votes, no status changes — unless the mentioning comment explicitly instructs it AND (for approval) the score passes. If the requester is a member, you may include their member mention (`mention://member/<user_id>` — notify-only); never agent-mention in the reply.
