# mx-workspace — Change log & review notes

*Moved out of `README.md` 2026-08-04. Dated, newest-relevant notes on definition changes,
live incidents, and review findings. The README stays the living description of the CURRENT
system; this file is its history.*

## 2026-09-29 (c) — stage barriers are the wake again; the handoff line covers only what they miss (not live)

Owner's decision. **Policy 05 v1.6** (statement 5): Multica's built-in sub-issue rule wakes
the parent's owner when every sub-issue at a stage and below is closed, and once more when all
are closed, whoever closed them, so a plain `done` posts nothing more. The child posts its
handoff line only where the rule stays silent: it goes `blocked`, or it goes `done` while a
sibling at its stage or below sits `blocked` (a Fix at a gate's stage always does; a re-armed
sub-task below a `blocked` gate closes its own stage and does not). Reversed from the first
2026-09-29 entry: a human's `done` flip releases the next actor again, the "never create wakeup
rules" line is gone, staging is the barrier mechanism again, the Barrier frontier bullet is
back in the leader playbook, and the monthly architecture review rolls up on the all-closed
wake again (no `[RP#]` handoff lines).

**Not live yet**: the owner asked for bundle and GitHub only. The platform rule still times out
against the Azure database on this server, so the live workspace keeps the handoff-line setup
until the move.

Cascade: workspace context, `CLAUDE.md`, `README.md`, `sdlc-flow-squad-member-protocol`,
`sdlc-flow-squad-leader-playbook`, `sdlc-flow-delivery-pipeline`, `sdlc-flow-po-orchestration`,
`spec-review-gate`, `pr-review-gate` `references/multica-flow.md`, `sdlc-impl-brief`, agents
`arch-reviewer`, `dev-backend`, `devops`, `issue-janitor`, `qc-runner`, `qc-tester`,
`release-manager`, squads `dev-team`, `qc-team`, `product-team`, autopilots
`monthly-architecture-review-monxa-backend-services`, `weekly-issue-hygiene-cancelled-cleanup`.
Same change in drunk.

## 2026-09-29 (b) — workspace context names who prefixes a root product-owner never touches (live)

No policy amended: Policy 05 statement 7a already gives the root type prefix (`[Feature]` ·
`[Enhance]` · `[Bug]` · `[Question]` · `[CICD]`) to the first agent that picks up a root
product-owner never touches. The workspace context said only "set by product-owner at intake",
unlike drunk's, so an agent working a root routed straight to it read no duty to prefix it. It
now carries the same clause as drunk. The prefix rule itself has been live in mx since
2026-09-22 (b); roots filed before then keep their plain titles, as in drunk. Cascade:
`workspace/workspace.context.md`.

## 2026-09-29 — a child wakes its parent's owner with one handoff line; stage barriers wake nobody (live)

Owner-approved. **Policy 05 v1.5** (statement 5: a child keeps its report, `## BLOCKER` and
questions on its own ticket, flips `done`/`blocked`, then posts ONE line on the parent —
`<KEY> done — report on <KEY>` / `<KEY> blocked — BLOCKER on <KEY>` — with no mention of any
kind on a squad-assigned parent, which every main and phase ticket here is; the agent's mention
on an agent-assigned parent; nothing on a member-assigned one; a human who finishes a ticket
for an agent replies with that agent's mention), **Policy 03 v1.2** (3b: a missing branch is
`blocked` + the handoff line), **Policy 04 v1.4** and **Policy 09 v1.5** (gates and members wake
the leader with the handoff line, never a mention). Members no longer mention anyone; the
`<@leader>` mention tokens are gone from dev-backend, qc-runner and qc-tester.

Cause: since the Multica v0.6.0 upgrade (2026-09-28) the sub-issue-done wake is a wakeup rule
whose dispatch has a hard-coded 2 s budget. This server reaches its Postgres in Azure Singapore
at 70–400 ms a round trip and a dispatch needs about 30, so every stage-barrier wake and every
agent-created wakeup timed out (drunk DRK-1796's leader never woke after its Build closed; the
same server hosts this workspace). An agent's plain comment on a squad-assigned ticket enqueues
the leader inside the request (`routeAssignedSquadLeaderFallback`, `server/internal/handler/comment.go`)
with no dispatcher, and a busy leader gets it folded into its queued run or replayed after the
current one. The old fallback — the leader's mention on the member's own sub-task — started a
plain agent run on the child with no squad briefing. The owner switches the platform's
sub-issue-done wakeup off in Settings → Wakeups, and agents are told never to create wakeup
rules. `--stage` stays mandatory: it is now the order the leader promotes in, not a wake.

The monthly architecture review no longer relies on the all-closed wake: each `[RP#]` run ends
with a handoff line on the run issue carrying arch-reviewer's mention, and the roll-up runs on
the wake that finds all four terminal (earlier wakes end silently).

Cascade: workspace context (wake list, handoff line, human replies, member write rule,
staging rationale, `Retrigger on done`, Fix-stage rationale, missing branch), `CLAUDE.md`,
`README.md` (trigger mechanics, diagrams, glossary), `sdlc-flow-squad-member-protocol`
(Mention rule → Handoff rule; the barrier self-check is gone), `sdlc-flow-squad-leader-playbook`
(handoff wakes, reply-under-trigger rule, Barrier frontier removed, staging and fix-loop
rationale), `sdlc-flow-delivery-pipeline` (wake contract; Barrier poisoning → stages order
promotion), `sdlc-flow-po-orchestration`, `spec-review-gate`, `pr-review-gate` +
`references/multica-flow.md`, `blocker-report`, `test-driven-development`, `sdlc-impl-brief`,
agents `arch-reviewer`, `dev-backend`, `devops`, `issue-janitor`, `pr-reviewer`, `qc-leader`,
`qc-runner`, `qc-tester`, `release-manager`, squads `dev-team`, `qc-team`, `product-team`,
autopilots `monthly-architecture-review-monxa-backend-services`,
`weekly-issue-hygiene-cancelled-cleanup`. Same change in drunk.

## 2026-09-28 — arch-review roll-up no longer waits for a "stage complete" comment (live)

No policy amended. Multica v0.6.0 (#8807) turns the sub-issue-done wake into a system
wakeup rule that posts **no** comment; the run carries a `[WAKEUP]` block and the timeline a
`wakeup_triggered` entry instead. `arch-reviewer` shape C and step 5 of the monthly
architecture-review autopilot told the agent it is woken "by the 'stage complete' comment",
so after the upgrade the roll-up wake would go unrecognised. Both now say the wake itself is
the signal and have the agent confirm with `multica issue children` that every `[RP#]` is
`done`/`cancelled` — correct before and after the upgrade. Cause: 2026-09-28 release review
(`release-reviews/2026-09-28_v0.4.40..v0.6.0.md` P4). Cascade: `agents/arch-reviewer.md`,
`autopilots/monthly-architecture-review-monxa-backend-services.description.md`.

## 2026-09-28 — architecture-review dedupe list paged 100 at a time (live)

No policy amended. `multica issue list` rejects `--limit` above 100 since Multica v0.4.42
(#7896); `architecture-review-sweep` §4 asked for `--limit 200`, so the cheap dedupe pass
errored on every run. It now reads `--limit 100 --offset 0 --fields identifier,title,status`
and repeats while `has_more` is true (release review P1; same change in drunk). Cascade:
`skills/architecture-review-sweep/SKILL.md`.

## 2026-09-27 — product-owner runs the clarification dialogue with `multica-brainstorming` (live)

Owner-approved. **Policy 06 v2.3** (statement 9: the dialogue runs with `interview-me` and
`multica-brainstorming`; each round is ONE numbered comment mentioning the requester, every
question with product-owner's best guess; before any spec, ONE spec-preview comment waits for
the requester's written approval; only a written reply answers — a status move, a resolved
thread or silence confirms no guess; the role skill still owns the spec's shape; Related skills
and References name `multica-brainstorming`). **Policy 09 v1.4** (product-owner runs the
clarification gate with both skills). Policy index row 06 lists both skills. Cause: the skill
was attached to product-owner but named in neither its instructions nor
`sdlc-flow-po-orchestration`, and agents follow inline text, not their attached skill list
(drunk measured this for CodeGraph on 2026-09-17). The earlier same-day entry had also put the
written-reply and spec-preview rules into the skill before any mx policy stated them. Cascaded
to `sdlc-flow-po-orchestration` (Clarification gate), `agents/product-owner.md` (Operating
contract) and README (intake flow diagram, human touch point #2, and §3.4 devops, which still listed
`brainstorming` and said devops commits straight to `dev` against `agents/devops.md`).

## 2026-09-27 — clarification dialogue runs on the ticket; only a written reply answers (live)

Ported from drunk-workspace (its 2026-09-27 (e)); no policy amended.

`multica-brainstorming` is rewritten for the ticket, where every wake is one turn: each round is
ONE numbered comment (requester's mention, a one-line read with a confidence number, every
question with a guess and its evidence, replies by number), approaches only when the requester
has a real choice and never in classes or layers, then ONE spec-preview comment (Summary, Done
means, Rules with examples, Contract, Placement, Not in this change, Decisions) approved in
writing before any spec. A status move, a resolved thread or silence confirms no guess. Before
the preview the dialogue covers out of scope, real-value examples plus one refusal or edge case
per rule, the business side of the contract, additive or breaking as the requester's call, and
outside prerequisites. The original description is kept as an `Original request` comment before
the first description write. The hand-off list drops the devops and squad-member lines and keeps
product-owner and the platform assistants, who stop at the confirmed intent and route.
`interview-me` (identical in both bundles) states that on a ticket the thread is the live user
and a round is one numbered comment of independent questions — matching the Clarification gate's
existing "ONE numbered comment".

Skill assignments: `multica-brainstorming` detached from `dev-leader`, `qc-leader` and `devops` —
named in none of their instructions, and its "every change needs an approved design" gate
contradicted Workflow D's "clarify only what genuinely blocks". README skill tables updated.

Open at the time: mx `product-owner` had `multica-brainstorming` attached but named nowhere
inline. Closed the same day — see the entry above.

## 2026-09-27 — architecture reviewed at both gates; dev-backend proves the coding standards before the PR (live)

Two owner-approved changes ported from drunk-workspace (its 2026-09-27 (c) and (d)).

**Architecture at both gates.** The spec gains **§3b Architecture impact**: Owner (the repo, and
inside a service the bounded context, that owns the change), Dependencies (each new dependency
between repos or services, with its direction), Public surface (each contract other services or
external callers consume — HTTP API, Service Bus event or message, webhook payload, shared
package — `additive`, `breaking` with the callers that must change, or `none`), Integration
(each new interaction between repos or services) — or one `None — stays inside <repo>` line.
Repos, services and bounded contexts only; which layer inside a service holds the logic stays
dev-leader's. mx ships deployed services, so there is no `(MINOR)` versioning rule on a break
(Policy 08 has none). The spec gate gains **Architecture fit 15%**: weights are now Coverage &
traceability 25 · Gherkin 20 · Business clarity 20 · Architecture fit 15 · Completeness 10 ·
Security 10. The PR category Maintainability & design becomes **Architecture & design** at the
same 15%: a diff contradicting §3b is `blocking`; a new `DKNET-LAYER-*` / `DKNET-AGG-004` /
`DKNET-REPO-004` violation in touched code, or a dependency between repos or services §3b never
declared, is `important`; the gate never re-decides §3b. Bars, bands, caps and round limits are
unchanged (spec: APPROVED ≥ 9.0, REVIEW REQUESTED 8.0–8.9, REWORK < 8.0, 5 rounds; PR: 8.5, 3
rounds). The PR rubric's calibration anchors were rewritten from the deduction math — the old
"8.5 for one `important`" and "8.0 for 1–2 `important`" disagreed with it (one alone computes
9.5–9.9, two compute 9.0–9.8; in-scope findings still take a rework round per statement 7).

**Standards self-review.** Every dev-backend `Build:` and `Fix (review):` ends with a Standards
EVIDENCE row: both .NET stack skills and the repo's `CLAUDE.md` opened, rule-ids checked, a
CodeGraph reuse search per new public symbol, `CLEAN-SRP-001..003` and `CLEAN-DRY-001/002`
measured, SOLID at the boundaries crossed (`DKNET-LAYER-001..004`, `DKNET-AGG-004`,
`DKNET-REPO-004`, `CLEAN-DIP-001`), vendor docs cited for a framework API the repo does not use
yet. dev-leader's brief names the at-risk rule-ids in a `Standards` row; a missing or
contradicted row is an `important` PR-gate finding.

Amended **MX-POL-06 v2.2** (authority line, diagram, statement 1: §3b is the second exception to
the role boundary; statement 2: seven sections; statement 3: no code words in §3b; new statement
3c: the four lines, blocker and major severities, CodeGraph grounding; statement 10: the brief
honours §3b; Definition of Done, enforcement, references), **MX-POL-04 v1.3** (diagram; statement
3: spec weights and Architecture fit; statement 4: Architecture & design with the §3b, layering
and Standards-row checks; statement 9: reviewers do not design inside a service; both
scorecards and the worked example; Definition of Done), **MX-POL-01 v1.2** (Enforced at; new
statement 17: the Standards self-review; Definition of Done; enforcement), **MX-POL-05 v1.4**
(diagram and statement 1: seven-section spec, was a stale "11-section") and **MX-POL-09 v1.3**
(product-owner authors a seven-section spec, was a stale "five-section"; spec-reviewer's Never
line allows §3b; dev-leader's brief honours §3b and names the `Standards` row; dev-backend's
Build carries the Standards row; pr-reviewer checks the diff against §3b and the layering).
Cascaded to `sdlc-spec-template` (placement exception, seven sections, §3b row, format rule,
scale-to-size, quality bar 6), `spec-review-gate` (contract line, collect step reads each repo's
`CLAUDE.md`/`AGENTS.md`, new **§3b placement** check with inline rules and severities,
code-level-design line, weights table, verdict scorecard), `pr-review-gate` (pass 5
**Architecture & design** with the checks inline, both scorecards;
`references/scoring-rubric.md` category row and anchors), `sdlc-impl-brief` (§3b binding,
`Standards` header row and paragraph, Done-when row), `sdlc-flow-squad-member-protocol`
(self-review check 8 **Standards** with the rules inline and the row shape; finishing step 1 no
longer says "six checks"), `test-driven-development` (Verification list),
`sdlc-flow-po-orchestration` (Workflow B step 2, hard rule), `sdlc-flow-delivery-pipeline`
(seven-section spec), `squads/product-team.md` (seven-section spec), `squads/dev-team.md`
(Build row), `agents/product-owner.md`, `agents/spec-reviewer.md`, `agents/dev-backend.md` (open
the stack skills before coding), `agents/dev-leader.md`, `agents/pr-reviewer.md` and `README.md`
(spec-gate weights, section counts, skill catalog row, glossary). The spec gate has no deduction
math, no count caps and no numeric calibration anchors in mx, so it got no anchors — flagged to
the owner, not added.

## 2026-09-24 — PR review round cap raised from 2 to 3 (live)

🦅 pr-reviewer may now issue 3 REWORK verdicts before ESCALATED → MANUAL HANDOFF (was 2), on
the owner's request. The spec cap (5), the squad fix-attempt cap (2 on the same root cause) and
the polish round are unchanged. Amended **Policy 04 v1.2** (diagram, statement 4, round-caps
exception), **Policy 05 v1.3** (statement 9) and **Policy 09 v1.2** (pr-reviewer
responsibilities). Cascaded to `pr-review-gate` (REWORK row, `maxReworkRounds: 3`,
`references/multica-flow.md` cap check and `round N of 3`), `sdlc-flow-delivery-pipeline`
(human touch-point table) and README (§ small-change path, dev/qc squad trees, escalation valve
table, skill table). Same change in drunk-workspace.

## 2026-09-24 — dev-backend moves to Claude Opus 5.5 (live)

🔨 dev-backend moves from `claude-sonnet-5` to `claude-opus-5-5` (standard context tier,
thinking stays `high`), on the owner's request. No policy touched. Cascaded to
`agents/dev-backend.json`, README §6 (table and tier summary) and the `CLAUDE.md` role table.
Same change in drunk-workspace.

## 2026-09-24 — `Retrigger on done` holds several issue keys (dev-team, qc-team, product-team; live)

A fix whose `done` must re-trigger more than one blocked sibling had no way to say so: the
property held one issue key (DRK-1696 in drunk-workspace hit it). The value is now one key or
several, comma-separated (`MXW-1703,MXW-1704`). The leader appends a key to a sub-task that
already carries one instead of overwriting it, re-arms each named issue once every child naming
it is `done` (one re-arm per issue however many children name it), and drops each key as it is
re-armed, unsetting the property when none is left. **MX-POL-04 v1.1**: the Fix carries
`Retrigger on done` naming every gate to re-arm. Cascaded to `properties/properties.json`,
`workspace.context.md`, `sdlc-flow-delivery-pipeline`, `sdlc-flow-squad-leader-playbook`
(checklist item 1, re-trigger rule, review-fix steps 1–2, loop-back and resume),
`sdlc-flow-squad-member-protocol`, `squads/product-team.md`, `CLAUDE.md` and `README.md`. Same
change in drunk-workspace.

## 2026-09-24 — stuck-run recovery escalates the wake list only, by ticket identifier

The hourly stuck-run recovery autopilot escalated the RAW candidate list when its
blast-radius guard tripped: parents whose run ended cleanly while their sub-issues were
still working, and issues already `done`, appeared as findings, each identified by a bare
UUID. Step 4 now skips any issue with children (`total > 0`) whose own newest task did not
fail — a parent with open sub-issues is a cycle in flight, not a strand; a parent whose task
genuinely failed stays eligible. Step 9 reports the wake list and nothing else: skipped
issues are never listed or counted, an empty wake list produces no escalation issue at all,
and every row is keyed on the ticket identifier (`MXW-1016`) and the agent NAME, never a
UUID. Same change applied to `drunk-workspace`'s hourly run-recovery autopilot and the
`run-medic` agent instructions.

## 2026-09-24 — opus agents move to Claude Opus 5.5; model table matches the JSON again

Every agent on `claude-opus-5` moves to **`claude-opus-5-5`** (same 1M context, same
`[1m]` tier marker where it was set, lower per-token price): 🦊 product-owner, 🦉 spec-reviewer
and 🐙 devops on `claude-opus-5-5[1m]`, 🐲 claude_ultra, 🏛️ arch-reviewer, 🧪 bdd-reviewer and
🐼 Mika on `claude-opus-5-5`. Thinking levels are unchanged — Opus 5.5 defaults to `medium`
effort and cannot run with thinking disabled, so every agent keeps an explicit level.

The model table had drifted from `agents/*.json` and is corrected in the same pass:
🦉 spec-reviewer and 🐺 dev-leader were listed as `claude-opus-4-8` (actual: opus on the 1M
tier, and Claude Sonnet respectively), 🦊 product-owner was missing its `[1m]` marker, and
🐼 Mika was listed as opus while its JSON said Sonnet — resolved in favour of the table, so
Mika is now opus in both, and 🦊 product-owner's thinking column is corrected from `xhigh`
to `high`, the level its JSON and the live agent already ran at. Live agents updated to match.

## 2026-09-22 (b) — root ticket titles carry a type prefix (Policy 05 v1.2)

A root ticket's type was readable only from its label, so a board or a notification showed nothing about what kind of
work a ticket was. Owner-approved amendment to MX-POL-05 §7 (new 7a, 7b): **every ROOT main ticket title carries one
type prefix** — `[Feature]` (new capability) · `[Enhance]` (change to behaviour that exists) · `[Bug]` · `[Question]` ·
`[CICD]` — matching its type label.
- The **label stays the source of truth**; `[Feature]` and `[Enhance]` both carry `feature`, so the prefix is the finer split the labels do not make. A prefix disagreeing with the label is a defect to fix, not to argue.
- **product-owner sets or corrects it at intake**, in the same step it labels the root and posts the spec: `multica issue update <root-id> --title "<prefix> <plain title>" --no-start`. `--no-start` is mandatory — the root is assigned to the squad and a title update without it wakes a second run.
- **Root-only.** No child carries a type prefix, and `[S#]`/`[P#-n]`/`[D#-n]`/`[T#-n]` keying is off the root's key NUMBER, so the rename changes no numbering.
- Requesters still create with a plain title; reclassifying the workflow re-prefixes.

Cascaded to `sdlc-flow-delivery-pipeline`, `sdlc-flow-po-orchestration` (new step 2a), `workspace/workspace.context.md`,
and agents `claude-ultra` and `default`.

## 2026-09-22 — the spec carries the contract: §3a fields and endpoints (Policy 06 v2.1)

The spec was business-only above the contract, so the data and API surface the whole platform must agree on
before code started reached the team only in the dev-leader's impl-brief — one layer too late to review, and
invisible to the other repos it binds. Owner-approved amendment to MX-POL-06 statements 1, 2, 3, 6 and 10
(new 3a, 3b): the spec now has **six sections**, with **§3a Contract changes** between Expected State and Scope.
- **Fields:** one row per new or changed field — entity, field, type, length/precision, required, unique/indexed, default, notes (allowed enum values, unit, currency, personal data, what existing rows get).
- **Endpoints:** one row per endpoint — new/changed/removed, HTTP verb, path, purpose, auth.
- **§4 Scope** names every repo and service touched, one per bullet with what changes; a repo the contract implies but Scope omits is a `major`.
- §3a is the ONE section where entity, field and endpoint names are allowed; class names, method signatures, paths and `file:line` stay blockers everywhere, §3a included. The tables are markdown, so §5 Gherkin is still the only fenced block.
- Gate: missing §3a where the change adds an entity or endpoint is a `blocker`; incomplete field or endpoint rows are `major`. Folded into the existing Completeness & unambiguity dimension — **weights and the 9.0 bar are unchanged**.
- Impl-brief: every §3a row is covered by a Change set row; a divergence from the agreed contract goes back to product-owner, not into the brief.

Cascaded to `sdlc-spec-template`, `spec-review-gate`, `sdlc-impl-brief`, `sdlc-flow-po-orchestration`,
`agents/product-owner.md` and Policy 04's Definition of Done.

## 2026-09-16 (c) — a re-arm into `todo` wakes nobody, on the spec gate too (live)

drunk-workspace DRK-1364: product-owner answered two spec-review REWORK rounds by flipping the `[S1311]`
sub-task `blocked`→`todo` with no mention. Neither flip enqueued a run — a ticket that has already run is
never re-woken by its status — so the gate sat idle for over an hour until the owner typed "pls check again".
Same shape as the dev-team fix of 2026-09-15, one layer up: product-owner ↔ spec-reviewer.

mx-workspace already carried the rule (`sdlc-flow-po-orchestration` two-part re-arm, MXW-1426, the end-of-turn
actuation check), so only the wake contract in `workspace.context.md` changed here: it now names the
`blocked`/`done`→`todo` flip as enqueuing nothing, alongside the `in_progress --no-start` re-arm and the plain
comment. drunk-workspace took the full cascade — Policy 04 v1.4, Policy 06 v2.2, `sdlc-flow-po-orchestration`,
`spec-review-gate`, the `product-team` briefing and its workspace context.

## 2026-09-16 (b) — members never cut or push a branch; no backgrounded commands (live)

drunk-workspace DRK-1353 showed the failure both workspaces were open to: dev-backend finished the fix, ran a
bare `git push`, and git pushed its runtime worktree branch `agent/dev-backend/1b37847e15ca` to origin under its
own name. The feature branch never moved, but the member's `git rev-parse origin/<branch>` check still passed — a
local tracking ref does not notice a push that went elsewhere — so it reported delivered. dev-leader caught the gap
and fast-forwarded the branch by hand.

Policy 03 v1.1 adds statements 3b (members never create or push a branch; no bare `git push`; a missing feature
branch is `blocked` + the leader's mention, never a branch the member cuts itself) and 3c (a push is proved with
`git ls-remote origin <feature-branch>`, and that SHA goes in the report). `sdlc-gitflow` and
`sdlc-flow-squad-member-protocol` carry the same check.

The same run also stalled on a backgrounded test suite and had to be resumed. A Multica run cannot resume around a
backgrounded process — the turn ends, the process is orphaned, the next run starts in a fresh checkout — so the
workspace context now bans it: long tests, builds and packs run synchronously with a longer timeout, split into
chunks that each finish inside one call.

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

