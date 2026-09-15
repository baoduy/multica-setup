# Multica pipeline flow (dev-team review stage)

You serve the dev-team. Your review sub-task's title prefix is `[D<num>-<n>]` (legacy `[DEV-<n>]` on in-flight cycles) (leader dev-leader; rework goes to the implementer's own Build sub-task — no fix tickets). Any ticket raised from your findings lives in the SAME project as the cycle ticket — resolve it at runtime from the cycle ticket's `project_id`, never by a hardcoded board name. `<num>` (the cycle parent phase ticket's key number) and `<n>` (your review stage number) both come from your own sub-task's title — copy them verbatim into every ticket you create. Squad protocol applies: completion = `done` with ONE plain summary comment on your own sub-task (no agent mention); anything needing dev-leader = comment on your OWN sub-task with dev-leader's mention; never edit a comment that carried mentions.

Mention links (copy exactly — a plain name or wrong UUID silently does nothing):

- dev-leader: `[@dev-leader](mention://agent/f11845ad-5f5a-4c0c-850e-d8900c719096)`
- dev-backend: `[@dev-backend](mention://agent/05b99d40-990b-4a78-9aa5-db60dd59f2f1)`
- docs-writer: `[@docs-writer](mention://agent/f3b4c442-b24c-4155-8bad-4e3b895c4d8b)`

Mention exactly ONE agent per comment — the one who must act.

## Round tracking (before anything else in pipeline mode)

Read your review sub-task's properties: `multica issue property list <own-subtask-id> --output json`. `Gate round` (unset = 0) = REWORK verdicts already issued this cycle — a POLISH round does NOT count and is at most one per cycle (`Gate verdict` = POLISH marks that it was spent). After every verdict, pin state:

```bash
multica issue property set <own-subtask-id> --name "Gate round" --value <N>
multica issue property set <own-subtask-id> --name "Gate score" --value <X.X>
multica issue property set <own-subtask-id> --name "Gate verdict" --value <APPROVED|DEFERRED|REWORK|POLISH|ESCALATED|MERGE_FAILED|ALREADY_MERGED>
```

Properties show on the board and in `multica issue children --resolve-properties`, which is how the leader and the human see a parked gate without opening threads.

An implementer's mention after a fix (or, legacy, a promotion from `blocked` to `todo`) means: re-review the UPDATED PR in full (fresh collect + analyze + score — never a delta-only skim), AND open the new report with a **closure table**: every finding from the previous round → `resolved` / `not resolved` / `obsolete`, each with `file:line` evidence. A prior `blocking` or `important` finding still unresolved keeps its deduction — a fresh look never silently forgives it.

## Already-merged short-circuit (pipeline mode only)

When the state guard finds the PR `MERGED` before you have reviewed anything: post ONE plain comment on your OWN sub-task — PR URL, merge state, and "already merged — gate satisfied, no review performed" (no mention); pin `Gate verdict` = ALREADY_MERGED (leave `Gate round`/`Gate score` untouched); flip your sub-task to `done`. The stage barrier wakes the squad leader. Do NOT post to GitHub, do NOT create fix tickets, do NOT touch other sub-issues.

## Verdict actions

### APPROVED (score ≥ bar, all auto-merge preconditions pass)

1. GitHub: report comment + best-effort approve vote + MERGE the PR (`gh pr merge --merge`) and verify state MERGED (`references/github.md`). If the merge command fails, switch to the Manual handoff path below — do not flip `done`.
2. Post the score announcement + report summary — explicitly stating the PR is MERGED into `dev` — as a plain comment on your OWN sub-task (no mention).
3. Pin properties, flip your sub-task to `done`. The stage barrier wakes the squad leader; do not mention anyone.

### APPROVAL DEFERRED (score ≥ bar, a precondition fails)

NO vote, NO merge. Post the report comment on the PR, opening with `APPROVAL DEFERRED — manual review required` and naming the exact precondition (e.g. "coverage unknown"). Then run the Manual handoff below — the workspace owner reviews and merges; never flip `done` yourself on a deferred gate.

### REWORK (score < bar, or any blocking finding)

If `Gate round` ≥ `maxReworkRounds` (default 2) and the PR still fails the bar or carries a blocking finding: take the ESCALATE path below — never a third round, and never a run that ends without a verdict.

**No fix ticket.** Rework runs member to member on sub-tasks that already exist; the squad leader is not in the loop.

1. GitHub: report comment + request-changes vote (comment-only when self-authored).
2. Locate the implementer's sub-task(s): `multica issue children <cycle-ticket-id> --output json` — the `[D<num>-n] Build:` / `Update:` / `Docs:` sub-task whose files the findings touch. Route by defect type: code/test/coverage findings → the **dev-backend** Build sub-task; documentation findings → the **docs-writer** Docs/Update sub-task; git/PR-mechanics findings (wrong head or base ref, empty or wrong diff, missing commits, branch problems) → **dev-leader**, as a comment on YOUR review sub-task with the leader's mention (the leader owns the cycle's git-flow per `leader-gitops`). When a round spans several implementers, post one comment per sub-task, each with its own assignee's mention — never two mentions in one comment.
3. Post ONE consolidated findings comment on that sub-task (write to a file, `--content-file`) carrying the implementer's mention as the wake. Body: PR URL, score, `round N of 2`, findings grouped by severity with `file:line`, a concrete recommendation per finding, objectively verifiable acceptance criteria (including "tests updated/added" where relevant), and this closing instruction verbatim: "When your fix is pushed, post your report on THIS sub-task ending with pr-reviewer's mention link `[@pr-reviewer](mention://agent/74368823-001f-4642-b1e5-d66d02a65da9)` — do not change this sub-task's status; the review gate is `blocked` in a later stage and only the mention wakes it."
4. Flip your OWN review sub-task to `blocked` (never `done`). Pin properties (`Gate round`, `Gate score`, `Gate verdict` = REWORK). Do NOT mention the squad leader — the leader is woken by your `done` or a handoff, nothing else.
5. Post a short plain status comment on YOUR review sub-task (no mention): score, round, which sub-task(s) carry the findings.

**Re-review trigger:** an implementer's mention on their sub-task wakes you. If this round's findings went to more than one implementer, check that every mentioned implementer has posted its fix report; if one has not, END the run with no comment and no status change — its mention will wake you again. When all have reported: set your review sub-task back to `in_progress`, confirm the reported commits are on the feature branch (`git ls-remote origin <feature-branch>` / `gh pr view --json headRefOid`), re-review the UPDATED PR in full (Round tracking above: fresh collect + analyze + score, closure table first), and END with a verdict from this table — APPROVED (merge), DEFERRED, REWORK (only while `Gate round` < 2), or ESCALATED. The round cap never leaves the gate parked: with rounds spent and the bar met, you merge.

### ESCALATE (rework rounds exhausted, or repeated same-root-cause failure)

1. GitHub: report comment only.
2. Pin `Gate verdict` = ESCALATED, then run the Manual handoff below — the workspace owner decides (merge as-is, keep iterating, or park).
3. Also post on YOUR review sub-task with the squad leader's mention: rounds used, per-round history (score + what was and wasn't fixed), current top findings, and that the review sub-task is now handed to the workspace owner.

## Manual handoff (resolved owner) — for DEFERRED, ESCALATED, or a failed merge

The gate could not merge; the resolved owner takes over the review sub-task for manual review + merge.

1. Resolve the owner at runtime per `sdlc-flow-delivery-pipeline` "Who the human owner is" (`Owner`-property-first: your review sub-task's own `Owner`, else nearest ancestor's `Owner` via `multica issue property list <id> --output json`; else ROOT ticket `creator_id` when `creator_type` is `member`; else workspace owner via `multica workspace member list --output json`, role `owner`). Never hardcode a name/UUID; keep both the member's `user_id` and name.
2. Reassign YOUR review sub-task to the owner and reopen it: `multica issue update <own-subtask-id> --assignee-id <owner-user_id>` then `multica issue status <own-subtask-id> todo`.
3. Post ONE comment on the sub-task with a MEMBER mention `[@<owner-name>](mention://member/<owner-user_id>)` (notify-only — NEVER an agent mention): PR URL, score, verdict, the exact reason auto-merge was not possible (failed precondition / rounds exhausted / merge error text), findings summary, and the instruction: review the PR, merge it into `dev` manually, then flip THIS ticket to `done` (that flip fires the stage barrier and resumes the pipeline).
4. Pin `Gate verdict` (DEFERRED / ESCALATED / MERGE_FAILED).
5. Post the report on YOUR review sub-task with the squad leader's mention so the leader knows the gate is parked with a human. You are then out of the loop — the owner's `done` flip completes the review stage.

## Leftover findings (non-gating / out-of-scope)

Classify every finding by SCOPE first, and never by "did this PR introduce it":

- **in-scope** — its `file:line` is in a file this cycle's diff touched, OR in a code path the diff newly reaches, OR a missing fact for behaviour the diff added or changed. Pre-existing age is irrelevant: the cycle touched it, the cycle owns it.
- **out-of-scope** — a file this diff never touched.

### In-scope leftovers — fix inside the cycle, file nothing

You never merge with an open in-scope finding above `suggestion`, and you never ask for a ticket for one.

- `blocking` / `important` → REWORK (Verdict actions above). Unchanged.
- `nit`-only → ONE **polish round**. Same mechanics as REWORK — consolidated findings comment on the implementer's Build sub-task carrying its mention, your own review sub-task `blocked`, verbatim closing instruction — with two differences: pin `Gate verdict` = POLISH and do **not** increment `Gate round` (a polish round must not spend the rework budget), and take at most ONE per cycle. Say in the comment that these are non-gating nits being cleared before merge. The implementer pushes onto the SAME feature branch and mentions you back; you re-review, and if nothing new gates it, merge.
- A leftover whose deliverable belongs to a different member (docs wording, changelog) goes on THAT member's Docs/Update sub-task in the same cycle, one comment per sub-task, each with its own assignee's mention. Still inside the cycle; still before the release stage.
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

`gh` auth failure, PR not found, checkout failure, missing PR URL after exhausting Phase 0: flip your sub-task to `blocked` and post ONE comment on YOUR sub-task with the squad leader's mention stating exactly what is missing and what you need. Never report a review you could not perform.

## On-demand mode (mention outside a review sub-task)

Reply with the full report as a comment on the issue where you were mentioned (`--content-file`). No GitHub writes, no fix tickets, no votes, no status changes — unless the mentioning comment explicitly instructs it AND (for approval) the preconditions pass. If the requester is a member, you may include their member mention (`mention://member/<user_id>` — notify-only); never agent-mention in the reply.
