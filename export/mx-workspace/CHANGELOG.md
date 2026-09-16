# mx-workspace — Change log & review notes

*Moved out of `README.md` 2026-08-04. Dated, newest-relevant notes on definition changes,
live incidents, and review findings. The README stays the living description of the CURRENT
system; this file is its history.*

## 2026-09-16 — product-owner reads ticket shape: sub-issues stop at implementation (live)

Port of the drunk-workspace change made the same day. product-owner now reads `parent_issue_id` on its first
wake and runs one of three shapes. A **root** main ticket is unchanged: full chain to `[P#-3]` per the scope keys.
A **sub-issue** (it has a parent) keeps every gate and both scope keys but is terminal at `[P#-1]` — no `[P#-2a]`,
no `[P#-2b]`, no `[P#-3]`, no project move and no labels — because the parent's owner ships all of its children in
ONE `dev`→`main` release; a per-child release would ship siblings still mid-cycle. A **bundle root** (no parent,
but children that already carry the work) is never re-spec'd: it waits for every child to reach `done` with its PR
merged into `dev`, then runs the release tail alone over all of them.

Cascaded to `sdlc-flow-po-orchestration` (new “Shape first” section, Workflow C creation + wake handling, hard rules),
`sdlc-flow-delivery-pipeline` (scope-key list, stage-ownership table), `squads/product-team.md`,
`agents/product-owner.md`, and Policy 05 v1.1 (statement 1b).

## 2026-09-15 — mx-workspace: mention hygiene, re-trigger flips in_progress, leader-routed rework, `Retrigger on done` (dev-team + qc-team; live)

Port of the three drunk-workspace changes made earlier today (see the entries below), applied to
both squads and to the shared skills. mx already had "the gate creates nothing, the leader files
the Fix"; what changed is the wake mechanics around it.

- **Mention hygiene.** Every `mention://agent/<uuid>` link in a posted comment is a wake, quoted or
  in backticks alike. pr-reviewer's `multica-flow.md` now lists LEADER links only (dev-leader,
  qc-leader, product-owner) — it never mentions dev-backend / qc-tester / devops; one link per
  comment. Wake sanity check first (`multica issue runs <own> --siblings`; own comment or own run
  in flight → end). Leader fix-loop checks `--siblings` before filing or re-mentioning.
- **Re-trigger flips `in_progress` first.** Every leader re-arm (`blocked` Build/Scenarios/
  Verify/Review, a `done` sub-task sent back, answered blocker, spec-review re-arm, `[P-1c]`
  re-arm) is `multica issue status <id> in_progress --no-start` THEN the one mention. Replaces every
  `blocked→todo`. "done is one-way" now reads: members never flip their own sub-task out of `done`;
  the leader does, to `in_progress`, only to re-trigger; the re-fired barrier is the expected
  "fix is back" signal.
- **No member-to-member traffic.** Stated in the delivery pipeline wake contract and the member
  protocol: a member writes only on its own ticket and mentions only its leader; the leader routes.
  Removed: polish-round "implementer mentions you back", "mention whoever raised the findings",
  product-team's pr-reviewer→devops direct loop (now via product-owner), blocker-report's
  any-agent re-arm (leader's move; a member reports on its own ticket).
- **`Retrigger on done`** (text property, id `23673c24-9f49-4584-a228-48d315c3e3cd` in
  mx-workspace). Leader sets it on every re-triggered sub-task / Fix it files with the key of the
  blocked issue to re-arm — dev-team: the Review; qc-team: the stage-2 Verify (stage 2 first, its
  `done` then wakes the leader to re-arm Review 3); product-team: `[P-1c]`. Wake-up checklist item 1:
  a `done` child carrying it → verify, flip the named issue `in_progress --no-start`, ONE comment
  with its assignee's mention, unset. Members never set or clear it. mx has no workspace context,
  so the rule lives in `sdlc-flow-delivery-pipeline` + the leader playbook + the briefings.
- **Files.** `pr-review-gate` (SKILL.md, references/multica-flow.md), `sdlc-flow-delivery-pipeline`,
  `sdlc-flow-squad-leader-playbook`, `sdlc-flow-squad-member-protocol`, `sdlc-flow-po-orchestration`,
  `spec-review-gate`, `blocker-report`, squads dev-team / qc-team / product-team, agents dev-leader /
  qc-leader / pr-reviewer / dev-backend, policies 04 / 09, `README.md`, `CLAUDE.md`. 15 live resources
  pushed and verified by hash/text against the bundle.

## 2026-09-15 — `Retrigger on done` property: leader bookkeeping for which blocked gate a fix re-arms (drunk-workspace live; mx-workspace NOT yet updated)

Owner recommendation. A fix that lands above a parked gate's stage (a `[D#-5] Fix:` sub-task while
`[D#-4] Review` sits `blocked`) fires no barrier when it goes `done`, and the leader had no durable
record of which issue to re-arm. New workspace custom property `Retrigger on done` (text, issue
key; id `12f1ef46-e5df-42ec-a5d4-ae6d66f384d9` in drunk-workspace).

- Leader sets it on every sub-task it re-triggers for fix work (re-armed Build, or a Fix sub-task
  it files — leader may file one when the fix deserves its own brief; pr-reviewer still never
  files). Wake-up checklist item 1: any `done` child carrying it → verify, flip the named issue
  `in_progress --no-start`, ONE comment there with its assignee's mention pointing at the fix
  report, unset the property. Several children naming one issue → re-arm once, when all are `done`.
- Worker: a Fix sub-task above a blocked stage ends its report with the leader's mention (rule 5,
  already there); members never set or clear the property.
- Recovery: a `done` child still carrying the property while its target is `blocked` = lost re-arm.
- Files: `workspace/context.md`, delivery-pipeline, leader playbook + `recovery.md`, worker
  playbook, `squads/dev-team.md`.

## 2026-09-15 — no member-to-member traffic: review rework routed through the squad leader (drunk-workspace live; mx-workspace bundle NOT yet updated)

Owner policy: a member writes only on its own ticket (comments, status, properties) and mentions
only its leader; anything for another member goes on the member's own ticket with the leader's
mention, and the leader routes it. Only the leader writes on tickets it does not own.

- **Review round, new shape.** pr-reviewer: ONE findings comment on its OWN Review sub-task
  (grouped per implementer, `file:line`, acceptance criteria, `round N of 2`), Review `blocked`,
  ends with dev-leader's mention — the only mention link. dev-leader: per implementer, flip that
  sub-task `in_progress --no-start` + ONE comment with its mention pointing at the findings.
  Implementer: fix, push, report on own sub-task with a closure row per finding, flip `done`, no
  mention — the re-fired barrier wakes the leader (confirmed live on DRK-1280, 08:01Z). dev-leader:
  verify, then re-arm Review `in_progress --no-start` + ONE comment with pr-reviewer's mention.
  pr-reviewer re-reviews in full; a re-arm with unchanged PR head is not a round.
- **Removed.** "Rework runs member to member, leader stays out", the implementer's
  `@pr-reviewer` mention-back, pr-reviewer flipping/commenting on the implementer's sub-task,
  the stall-sweep autopilot nudging implementers directly (now nudges the leader on the phase
  ticket).
- **Files.** `workspace/context.md`, delivery-pipeline, leader playbook (Rework section rewritten
  as three steps) + `recovery.md`, worker playbook, `pr-review-gate` (SKILL.md, multica-flow.md,
  github.md), `squads/dev-team.md`, agents dev-backend / docs-writer / pr-reviewer / dev-leader
  description, autopilot daily digest, policies 04 / 05 / 07 / 09.

## 2026-09-15 — rework wake hygiene + re-trigger flips `in_progress` (drunk-workspace live; mx-workspace bundle NOT yet updated)

Incident on DRK-1282 (DKNet.Accounts.Api PR #4): pr-reviewer's round-1 findings comment quoted
its own mention link inside the "closing instruction verbatim", Multica woke pr-reviewer on its
own comment, it declared the wake "misrouted" and re-mentioned dev-backend; the owner then had
dev-leader file a fix sub-task. Result: three dev-backend fix runs on one branch for a two-line
fix. Two duplicates were cancelled by hand.

- **Mention links are wakes, wherever they sit.** `workspace/context.md`: every
  `mention://agent/<uuid>` link in a comment or description enqueues a run, backticks and quotes
  included; write instructions about mentioning in prose. `pr-review-gate/references/multica-flow.md`
  closing instruction no longer carries pr-reviewer's own link; a findings comment carries exactly
  ONE mention link, the implementer's.
- **Check for a live run before re-sending or filing.** pr-reviewer: first command on a wake on an
  implementer's sub-task is `multica issue runs <id> --active`; own findings comment or implementer
  run in flight → end with nothing. An implementer mention with an unchanged PR head is not a new
  round. Worker playbook: `--siblings` first on a rework wake; another own run in flight → no push,
  no mention. Leader `recovery.md` stall detection: `--siblings` before re-mentioning or filing.
- **Re-triggering a `done`/`blocked` sub-task flips it `in_progress` first, mention last.**
  Owner request. Leader (any re-arm, corrective comment, failed-report send-back, AT reject,
  product-owner spec re-arm) and pr-reviewer (REWORK/POLISH round) run
  `multica issue status <id> in_progress --no-start`, then the ONE mention comment. Worker ends the
  turn at `done`/`blocked` as always; the re-fired barrier is expected and the leader treats it as
  a report to verify (Review still `blocked` → no promotion, no new sub-task). Replaces
  `blocked`→`todo` re-arms and "never flip out of `done`" (now: nobody flips their OWN sub-task
  out of `done`). Files: delivery-pipeline, leader playbook + recovery.md, worker playbook,
  po-orchestration, `squads/dev-team.md`, `agents/dev-backend.md`, `agents/pr-reviewer.md`.

## 2026-09-11 — acceptance-test-first: Build split into `Acceptance tests` → `Build`, frozen at `at_sha` (bundle; both workspaces)

Reshaped dev-backend's testing flow after Böckeler's "TDD inside the agent loop — theater or
actual value?" and Vaccari's "Acceptance Tests for AI-assisted development". Two findings drove
it: a single run that writes a test and attests its own RED proves only that it ran (and agents
skip or fake the step, or derive the expected value from the implementation); and executable
acceptance tests approved before implementation, frozen after, are the guardrail that actually
constrains an agent. Prescribing the ceremony is replaced by measuring the outcome.

- **Stage split.** Route A is now `[D#-1] Acceptance tests` → leader's inline **AT approval**
  (read against the spec, pin `at_sha` + AT paths into Build) → `[D#-2] Build` → `[D#-3] Review`.
  Same brief for both dev-backend sub-tasks; two opening instructions in `sdlc-impl-brief`.
  Multi-surface: all Acceptance-tests sub-tasks at one stage, all Builds at the next.
- **Frozen ATs.** `git diff <at_sha>..HEAD -- <AT paths>` must be empty at Build done and is
  re-run by pr-reviewer; a modified/deleted approved scenario is `blocking` (6.9 cap). Wrong AT →
  `blocked` to the leader, re-arm stage 1, re-pin — never edited in Build. Additions allowed, listed.
- **Inner loop unprescribed.** `test-driven-development` rewritten: outer loop (ATs) is the
  contract; unit red/green/refactor is dev-backend's own and is not reported. Anti-tautology rule:
  expected values are spec literals, never computed by calling production code.
- **Mutation report replaces narrated mutation checks.** Stryker scoped to touched classes,
  survivors dispositioned (`killed`/`equivalent`/`accepted`); manual fallback must say the tool
  was unavailable. Missing evidence caps at 7.9. Self-review check 1 updated, check 7 (AT drift) added.
- **Ports-and-adapters harness** in `testing-standards`: ATs drive the inbound port with
  hand-written in-memory fakes; `WebApplicationFactory`/Testcontainers only for `@integration`.
  Brief §2 gains a **Test seam** line; a missing seam is a §3 row, never an ad-hoc refactor.
- Touched: `agents/dev-backend.md`, `agents/dev-leader.md`, `squads/dev-team.md`,
  `skills/test-driven-development`, `skills/testing-standards`, `skills/sdlc-impl-brief`,
  `skills/sdlc-flow-squad-member-protocol`, `skills/sdlc-flow-squad-leader-playbook`,
  `skills/pr-review-gate` (+ rubric), `docs/policies/02`/`05`/`09`, README §④. Skills, agents and squad pushed live to both workspaces 2026-09-11 (hash-verified); policies, README and CHANGELOG are bundle-only (no CLI).

## 2026-09-10 — dev-qc merged into dev-backend (ported from drunk-workspace, live)

Ported the dev-team cooperation change already running in `drunk-workspace`: the in-repo QC
role is gone and `dev-backend` owns implementation AND the cycle's in-repo tests, test-first.
Pushed live to mx-workspace, not bundle-only.

- **`dev-qc` archived** and removed from `dev-team`. `qc-team` (qc-leader · qc-tester ·
  qc-runner, SANDBOX BDD integration on `mx-qc-board`) is untouched — it was never the same
  role and stays the separate `[P#-3]` phase.
- **Route A lost its Verify stage**: `1 Build → 2 Review` (was `1 Build → 2 Verify →
  3 Review`). `dev-backend`'s Build is `done` only on a green full suite with ≥80% combined
  BDD+unit coverage per touched class, measured and reported per class; a red suite or a
  coverage gap ends `blocked`, never `done`. Route B unchanged apart from wording (no
  coverage bar rather than "no Verify stage").
- **One gate, one loop**: pr-reviewer at Review is the only gate, and the consolidated
  `Fix (review):` sub-task now carries the whole round — implementation defects, missing or
  thin tests, and coverage gaps alike, since one owner holds code and tests. The "re-arm
  Verify FIRST" rule is gone with the stage; the fix report carries the suite + coverage
  evidence instead. Fix-ticket routing itself is unchanged (drunk's no-ticket rework model
  was deliberately NOT ported).
- **`test-driven-development` assigned to `dev-backend`** (now 8 skills) alongside
  `testing-standards`; its instructions carry the explicit RED → GREEN → REFACTOR →
  coverage review → sign-off run flow.
- Definitions touched: `agents/dev-backend.{md,description.md,json}`, `agents/dev-leader.md`,
  `squads/dev-team.{md,json,description.md}`, `skills/leader-gitops`,
  `skills/sdlc-flow-delivery-pipeline`, `skills/pr-review-gate` (SKILL + `references/github.md`
  + `references/scoring-rubric.md`), `skills/sdlc-flow-squad-leader-playbook`,
  `skills/sdlc-flow-squad-member-protocol`, Policies 00 / 02 (v1.2) / 05 / 09 (v1.1),
  `README.md`, `CLAUDE.md`, `manifest.json`.
- Coverage evidence moved with the role: `pr-review-gate`'s coverage source is now
  dev-backend's per-touched-class report on the **Build** sub-task, and `leader-gitops`'
  PR gate reads that report instead of a verifier verdict.

## 2026-09-10 — Spec-review double-wake fixed; reviewer-created tickets now unassigned (live)

Two changes pushed live alongside the dev-qc merge above.

**Spec-review gate no longer double-wakes product-owner** (ported from drunk-workspace).
The APPROVED verdict both mentioned product-owner AND flipped the staged `[S<num>]` sub-task
to `done`, firing two enqueues for one event. Two product-owner sessions then raced in
Workflow C step 2, both saw no `[P…]` children, and both created a phase set — two live
`[P<num>-1]` tickets, two dev-team cycles, two branches, two PRs.

- `spec-review-gate`: APPROVED now emits **exactly one** wake, chosen by staging — staged
  sub-task (the normal case) gets the verdict with NO mention, because the `done` flip fires
  the parent barrier; only an unstaged sub-task carries the product-owner mention. REWORK
  always mentions (`blocked` fires no barrier). Pipeline mode now also triggers on a mention
  on the gate's OWN sub-task at any status, and on-demand mode is narrowed so it can never
  apply there and strand the ticket.
- `sdlc-flow-po-orchestration`: REWORK is acted on by **verdict**, not status, and the re-arm
  is explicitly two mandatory parts (status → `todo`, plus the mention). New hard rules: one
  phase set per main ticket with an after-write children re-list and **oldest-wins** duplicate
  resolution by `created_at`; and an explicit warning that a second session may be running the
  same event with a stale view. The reply-without-mention rule is narrowed to mid-run replies
  only — re-waking an agent whose turn ended always needs the mention.
- `product-owner`: `max_concurrent_tasks` 6 → 1, so a duplicate enqueue queues instead of
  racing.

**Reviewer-created tickets are created UNASSIGNED**, for owner review before work starts
(workspace-owner decision, applied in both workspaces). pr-reviewer no longer assigns work to
an agent it does not already own:

- `Fix (review):` sub-issues and `Review follow-ups:` issues are created with no assignee,
  name the intended owner as `Suggested owner:` in the body, get their `Owner` property set,
  and are handed to the resolved human owner by ONE member mention on the new ticket.
- **The cycle intentionally waits on that assignment.** dev-team's briefing tells the leader to
  read an unassigned fix ticket as awaiting-owner, not as a stalled member.
- Definitions touched: `skills/pr-review-gate` (SKILL + `references/multica-flow.md`),
  `agents/pr-reviewer.md`, `squads/dev-team.md`, Policies 04 and 09.

## 2026-09-10 — Only squad leaders create issues; members report (live, both workspaces)

Workspace-owner rule, replacing the "reviewer files it unassigned" step from earlier today.
`multica issue create` now belongs to `product-owner`, `dev-leader` and `qc-leader` alone.

- **Members create nothing.** `pr-reviewer` (was filing `Fix (review):` and `Review follow-ups:`)
  and `qc-runner` (was filing `[T<num>-n] Fix:` to qc-tester) now only report — one consolidated
  report per round on their OWN gate sub-issue with the leader's mention. Their reports must be
  written **filable as-is**: findings with `file:line`, a recommendation per finding, verifiable
  acceptance criteria, `Suggested owner:`, and the stage the fix must carry (their own stage — a
  fix on a fresh stage orphans the gate that raised it).
- **Leaders file, and consolidate for real.** Findings from two members in the same round, or
  successive rounds sharing one root cause, become ONE issue rather than several. A member-filed
  issue is a defect: fold it into the leader's issue and cancel it.
- **A leader-filed issue raised from a report is created UNASSIGNED**, `Owner` set, handed to the
  resolved human owner by ONE member mention. The owner's assignment is the wake and the cycle
  pauses there by design — briefings say so explicitly so a leader does not read it as a stall or
  re-file it. Routine decomposition sub-issues (`[S#]`, `[P#-n]`, `[D#-n]` Build/Review,
  `[T#-n]` Scenarios/Verify/Review) are the exception and stay assigned.
- Definitions touched (mx): `skills/pr-review-gate` (SKILL + `references/multica-flow.md`),
  `skills/sdlc-flow-squad-leader-playbook`, `skills/sdlc-flow-squad-member-protocol`,
  `skills/sdlc-flow-po-orchestration`, `agents/pr-reviewer.md`, `agents/qc-runner.md`,
  `agents/dev-leader.md`, `agents/qc-leader.md`, all three squad briefings, Policies 04 and 09
  (new governing statement **1b**).
- Off-pipeline agents outside every squad (`arch-reviewer`, `Mika`, `prd-release`,
  `issue-janitor`) are unchanged — they have no leader and file under their own charters.

## 2026-08-21 — Simplification & robustness pass (bundle-only; re-import to go live)

- **Skills trimmed, functionality preserved**: `codegraph` (setup/internals cut, gotcha kept), `test-driven-development` (382→~55 lines; stack detail lives in `testing-standards`), `interview-me` (dead cross-references removed), `multica-brainstorming` (decorative graphviz diagram removed), `architecture-review-sweep` (CodeGraph setup → pointer to `codegraph`).
- **Duplication collapsed to canonical homes**: wake contract → `sdlc-flow-delivery-pipeline` (playbooks/member-protocol/blocker-report now point); owner resolution → delivery-pipeline "Who the human owner is" — all escalation texts (leader playbook, po-orchestration, squad briefings, spec-review-gate ×2, pr-review-gate) now use the same `Owner`-property-first order (previously three inconsistent orders).
- **Stale README thresholds fixed**: spec gate is ≥9.0 / 8.0–8.9 REVIEW REQUESTED / <8.0 REWORK everywhere; the "live contradiction" footnote was stale (skill and briefing already agreed) and is removed; §2 weight list corrected (business clarity 20% + completeness 15%, not "architecture 25%").
- **Scoring hardened**: both gates now require a per-finding **closure table** on every re-review round — a prior blocking/major finding still unresolved keeps its deduction.
- **Wake-signal defects fixed**: po-orchestration no longer pairs a promotion with an agent mention (double wake); "plain comment wakes leader" claims replaced with mention-required (MXW-454); pr-review-gate leader reports now on reviewer's OWN sub-task, not parent.
- **`leader-gitops`**: reuse rule added for a feature branch that already exists on origin (cancelled-duplicate case).
- **spec-reviewer description**: "architecture" dimension mislabel → "business clarity" (rubric forbids scoring architecture at the spec gate).


**Git-flow consolidation 2026-08-04 — the dedicated git-custodian agent is retired.** Its
branch-cut and cycle-PR duties moved to the two squad leaders (dev-leader, qc-leader), who now
run git inline — no Branch or PR sub-tasks exist in either squad's cycle anymore. Its old
gitops runbook was replaced by a new skill, `leader-gitops`, bound to both leaders (manifest
count unchanged — a rename, not an addition). New cycle shapes: dev-team Route A is now leader
branch (inline) → `[D#-1] Build` → `[D#-2] Verify` → leader PR (inline) → `[D#-3] Review`;
Route B drops to `[D#-1] Update` → `[D#-2] Review`; qc-team's development cycle is leader
branch (inline) → `[T#-1] Scenarios` → `[T#-2] Verify` → leader PR (inline) → `[T#-3] Review`.
The monthly branch-cleanup autopilot moved to dev-leader. release-manager (`dev`→`main`) is
unaffected. Changed: `agents/dev-leader.md`, `agents/qc-leader.md`, `squads/dev-team.md`,
`squads/qc-team.md`, `skills/leader-gitops` (new), the retired agent + its old skill deleted,
`manifest.json`.

**Simplification pass 2026-08-04 — squads self-manage end to end.** Findings from a full
audit of the bundle against Multica's native built-ins:

- **Escalation to humans now delivers by ASSIGNMENT, not member mention** — verified against
the platform source: a `mention://member/...` link renders but enqueues/notifies nothing, so
every "escalate to the creator" path silently waked nobody. Squad briefings, the leader
playbook, `sdlc-flow-delivery-pipeline`, `sdlc-flow-po-orchestration` and
`sdlc-flow-squad-member-protocol` now reassign the stuck ticket to the human at `todo`
(the pattern spec-reviewer/pr-reviewer handoffs already used).
- **`sdlc-impl-brief` registered and bound** to dev-leader + qc-leader — the leader playbook
required it but no agent loaded it (phantom reference).
- **Aggressive skill trim**: the generic `addyosmani/agent-skills` pack was unbound from squad
agents (dev-backend 15→7, dev-qc 9→6, dev-leader 9→6, product-owner 9→7) and the 12 resulting
orphans deleted; `doubt-driven-development` removed from dev-leader (its own text forbids
persona binding). 5 stale never-manifested dirs (`brainstorming`, `code-simplification`,
`idea-refine`, `spec-driven-development`, `using-agent-skills`) deleted. 36→25 manifest skills.
- **Consistency fixes**: spec gate is APPROVED ≥9.0 with a REVIEW REQUESTED tier at 8.0–8.9
(delivery-pipeline previously said ≥8.0); devops phase naming aligned to `[P#-1b]` (Workflow C)
vs `[P#-1]` (Workflow D); squad briefings' duplicated `--stage` mechanics collapsed into the
leader playbook (single canonical copy, incident refs preserved).

**Dev-team light route 2026-08-04.** Docs/config-only requests no longer run the full
five-stage cycle: a new Route B (`Branch → Update → PR → Review`, no Verify stage) skips the
dev-qc test gate that has nothing to verify. Routing is the leader's FIRST decision per
request, defaulting to the full cycle when unsure; the pr-reviewer gate runs on both routes
(its coverage precondition is vacuous on a no-coverable-lines diff). Changed:
`squads/dev-team.md`, `agents/dev-leader.md`, `agents/dev-backend.md`,
`skills/sdlc-flow-delivery-pipeline`, `skills/leader-gitops`.

**Status-discipline hardening 2026-08-04.** The wake chain runs entirely on status writes,
so a forgotten flip strands a cycle. Two rules added: members — *"the LAST action of every
run on a sub-task is a status write"* (re-read your own status before ending a run and
confirm it matches the report; `sdlc-flow-squad-member-protocol`); leaders — *flip the cycle
parent `todo` → `in_progress` yourself on first pickup* (`sdlc-flow-squad-leader-playbook`).
Both skills now point explicitly at the platform's built-in `multica-working-on-issues`
skill (auto-injected in every agent workdir) as the source of native status semantics.
`blocker-report` gained an optional `## QUESTIONS` section (numbered, best-guess attached)
and its delivery rule now matches the reassign-to-human escalation pattern.

**Autopilots exported 2026-08-04.** The workspace's 4 autopilots (hourly stuck-run recovery —
currently paused; monthly branch cleanup; monthly architecture review; nightly issue hygiene) are
now versioned under `autopilots/` and registered in `manifest.json` (`--scope autopilot` exports,
importable via `--include autopilots`). Autopilot priority is not capturable via the CLI.

**Answered-blocker stall hardening 2026-08-04 (MXW-1016).** A correct blocker answer was posted
without the actuation (no `blocked`→`todo` flip, no mention) and the cycle stalled silently —
only a status transition or an agent mention enqueues a run. Four layers added: `blocker-report`
gained a Resolution Protocol (answer in-thread + actuate in the same wake); the leader playbook's
wake checklist gained an answered-blocker re-arm rule and an end-of-wake actuation check; the
member protocol gained self-service resume (a member woken with an answer in its blocker thread
flips its own sub-task back); and the hourly stuck-run recovery autopilot gained **Pass B**, an
answered-blocker sweep that nudges the blocked member when a blocker thread has a ≥30-minute-old
reply but the issue is still `blocked` (⚠️ inert while that autopilot stays paused).

⚠️ **These passes edit the export bundle only** — apply to the platform (skill bind/unbind,
squad instruction updates, edited skill contents) to make them live.

**Presentation pass 2026-08-02 — restructured for a mixed audience.** The document was
reorganised into four parts (Part 1–2 plain-English for everyone; Parts 3–4 technical
reference), and a **cast-of-characters** table plus a **Glossary** were added. No facts
changed in this pass — the branch-strategy and project-board sections were *moved* into the
technical parts, not edited. The old section numbers (§1–§6) were kept so existing
cross-references still resolve.

**Coverage standardised to `>80%` 2026-08-02.** The dev-team code-coverage gate on touched
classes was changed from `≥90%` to `>80%` everywhere it appears — in this README **and** in
the source definitions (`skills/testing-standards`, `agents/dev-backend.md`, `agents/dev-qc.md`,
`squads/dev-team.md`). Bug-fix *confidence* thresholds (also 90%, a different metric) were left
unchanged. ⚠️ **This edits the export bundle only — re-import / update the affected agents on
the platform to make the new gate live** (`skills/multica-cli` has the commands).

---

*The reconcile history below predates the presentation pass.*

This README was regenerated on 2026-07-26 and the workspace has since drifted. On 2026-08-02
the following were reconciled against the current JSONs (all now correct in the sections above):

- **§5 Skills per agent** — regenerated from each `agents/<name>.json` `skill_names[]`. 13 of 17
agents had changed (e.g. dev-backend 9→14, devops 2→6, product-owner's `brainstorming`→
`multica-brainstorming` and `spec-driven-development`→`sdlc-spec-template`).
- **§5 Full skill catalog** — rebuilt "Bound to" reverse index; added the five new skills
(`sdlc-flow-squad-member-protocol`, `sdlc-spec-template`, `multica-brainstorming`,
`helm-chart-delivery`, `testing-standards`); dropped five now-unmanifested ones.
- **§6 models** — dev-qc is `openrouter/openrouter/pareto-code` (was `claude-sonnet-5`);
prd-release rationale said `qwen3.7-max`, actual is `deepseek-v4-pro`.
- **New "Teams (squads)" section** — goal + detailed flow per squad, including the third squad
**product-team** (not previously documented as a squad).
- Small §1 fixes: spec is **11 sections** (was "9"); SANDBOX deploy is **argoCD** (was "DevOps-deploys").

**Re-export 2026-08-02 (second pull).** The platform added two agent-specific runbook skills,
extracted from those agents' `instructions`: a dedicated git-custodian runbook (later renamed
`leader-gitops` and rebound to the squad leaders — see the git-flow consolidation entry above)
and `prd-release-runbook` (→ 🌙 prd-release, now 3 skills). Manifest **33 → 35**; §5
Skills-per-agent + Full skill catalog updated. The three squad briefings also gained their own
`## Flow` diagrams — they match the "Teams (squads)" section above, so no change was needed there.
Models were unchanged.

**Still open — NOT reconciled in this pass (flagged, needs a decision / a dedicated flow-doc pass):**

1. **§1/§2 feature/bug flow diagrams are structurally stale.** The live flow (per
sdlc-flow-delivery-pipeline`+`sdlc-flow-po-orchestration`) now has a **CI/CD lane**` [P#-1b]`devops +`[P#-1c]`pr-reviewer), a`[P#-2] Merge helm PR `human step, and a bdd_required=false` waiver where `[P#-2a]` is terminal. §1/§2 still show only the old
our-phase shape. The new "Teams" section documents these; §1/§2 should be re-drawn to match.
2. ~~**Spec-gate threshold contradiction.**~~ RESOLVED 2026-08-21 — skill, briefing and README all state ≥9.0 with the 8.0–8.9 REVIEW REQUESTED tier. The shared `sdlc-flow-delivery-pipeline` skill and
1 ③ say **≥ 8.0**; the `product-team` briefing (`squads/product-team.md`) says **≥ 9.0**.
ne is wrong — pick the intended bar and fix the loser (Rule 7: don't average).
3. **Five stale skill directories** under `skills/` (`brainstorming`, `spec-driven-development`,
using-agent-skills`,` code-simplification`,` idea-refine`) are left over from a prior export nd are not in` manifest.json`. Delete them in a cleanup pass.
4. **§5 layer-model &amp; maintenance prose** still reference the old capability-library framing and
 "33 skills" world (now 35); the counts are corrected but the surrounding narrative could be tightened.

