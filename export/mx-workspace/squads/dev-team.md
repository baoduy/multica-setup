# DEV Team Squad — Briefing

**Goal.** Implement approved specs and confirmed bug fixes for the Monxa platform (.NET backends) and deliver each request cycle as exactly ONE merged PR into `dev`. Generic leader machinery: `sdlc-flow-squad-leader-playbook`. Shared flow, conventions, branch/environment strategy: `sdlc-flow-delivery-pipeline`.

- **Home project**: `mx-code` (all `[D<num>-n]` sub-tasks; resolve the project ID at runtime).
- **Repo**: exactly ONE per cycle, from the four Monxa service repos (email-service, auth-api, payment-gateway, web-hook-deliverer, org `the-wixo`) — the single repo the phase ticket's Scope names. A phase ticket naming two repos is rejected `blocked` to product-owner for a split, before any decomposition or branch cut. One repo, one feature branch cut by dev-leader, every member committing directly to it, ONE PR opened by dev-leader after the last implementation stage for the final Review gate.
- **Upstream owner**: `product-team` (leader product-owner) creates the `[P<num>-1]` phase ticket this squad works from and consumes its result.

## Flow

```
ENTRY   product-team → [P<num>-1] Implementation (dev-team, todo)
        description carries the FULL approved spec — never open the main ticket
        OR a docs/config request filed directly to the squad

  ROUTE A · CODE (full cycle) — anything that touches application or test code
  ⚙ ── branch cut (inline)  dev-leader     feature branch off the latest `dev` — no sub-task (leader-gitops)
  1 ── [D<num>-1] Acceptance tests  dev-backend   §7 Gherkin → executable, RED acceptance tests + §5 stubs,
                                                  pushed; report RED SHA + per-scenario table (impl brief)
  ⚙ ── AT approval (inline) dev-leader     read ATs against the spec; pin `at_sha` + AT paths into Build
  2 ── [D<num>-2] Build     dev-backend    implement against FROZEN ATs → green; ≥80% + mutation report
                                           per touched class, full suite green, drift check empty
  ⚙ ── PR open (inline)     dev-leader     ONE PR, head = feature branch, base = `dev` — no sub-task (leader-gitops)
  3 ── [D<num>-3] Review    pr-reviewer    score 1–10; AT drift = blocking → APPROVED merges into `dev`

        REWORK at 3 ─→ Fix (dev-backend) ─→ re-arm 3                   ⟲ max 2

  ROUTE B · DOCS/CONFIG-ONLY (light cycle) — no code, no test surface
  ⚙ ── branch cut (inline)  dev-leader     feature branch off the latest `dev` — no sub-task (leader-gitops)
  1 ── [D<num>-1] Update    dev-backend    the docs/config change, committed + pushed
  ⚙ ── PR open (inline)     dev-leader     ONE PR, opened on a verified push (leader-gitops)
  2 ── [D<num>-2] Review    pr-reviewer    score 1–10 → APPROVED merges into `dev`

        REWORK at 2 ─→ Fix (dev-backend) ─→ re-arm 2                   ⟲ max 2
        (no coverage bar on this route)

EXIT ✅  PR MERGED into `dev` → [P<num>-1] done + plain report (no mention)
         → product-owner verifies score + merge, promotes the release
EXIT ⚠   2 failed rounds on one root cause, or outside squad control
         → escalate to product-owner on the PHASE ticket, never a third loop
```

The leader cuts the feature branch inline (per `leader-gitops`) BEFORE creating stage 1, and names the branch + base SHA in every implementing sub-task's description. Stage 1 is created `todo`; later stages are created `backlog` and promoted by the leader as each barrier fires and its deliverable verifies. Between stages 1 and 2 the leader runs the **AT approval** inline: reads the pushed acceptance tests against the spec's §5 / brief's §7 (every scenario present, none softened, expected values literal from the spec, business-readable — reading, never executing), then writes `at_sha` (the RED commit) and the AT file paths into the Build sub-task before promoting it. A rejected AT set re-arms stage 1 with the scenario named; it never reaches Build. The PR is likewise opened inline by the leader — after the Build gate passes, before promoting Review. Nothing else advances the cycle.

**Why two runs.** The run that writes the acceptance tests never sees the implementation, and the run that writes the implementation cannot change the acceptance tests (`at_sha` freezes them; a modified or deleted approved scenario is a `blocking` review finding). That split, plus the leader's read between them, is the checkpoint that makes "the tests went red then green" mean something — a single run attesting its own RED is not.

### Cycle routing (decide FIRST, every request)

**Route B (docs/config-only)** applies when EVERY file the change touches is documentation (README, `docs/`, comments, changelogs) or a configuration value with no test surface. The moment the change touches a `.cs`/`.ts`/test file, or a config change alters behaviour that existing tests assert (a connection string format, a feature flag with coverage, a validation limit), it is Route A — **when unsure, take Route A**. The pr-reviewer gate runs on both routes and its coverage precondition is satisfied vacuously on a no-coverable-lines diff, so Route B still ends in a scored, gated merge — it only drops the coverage bar that has nothing to measure.

## Members

| Agent | Role | Responsibility |
|---|---|---|
| **dev-leader** | Leader | Triage, clarify, decompose, review, gate, status/stage management, **and the cycle's git-flow** — cuts the feature branch and opens the ONE PR itself, inline, per `leader-gitops`. Never writes code or runs builds/tests. |
| **dev-backend** | Developer | Owns implementation AND the cycle's in-repo tests, in two separate runs (`test-driven-development`): **Acceptance tests** — the brief's §7 Gherkin as executable Reqnroll scenarios through the inbound port with in-memory fakes, plus §5 signature stubs, RED, pushed; **Build** — implementation against the frozen approved ATs → green, own unit tests as needed → **coverage review** (every touched class ≥80%) → **mutation report** (`dotnet stryker --since:origin/dev`, scoped to the lines changed in each touched class, survivors dispositioned) → sign-off run (full suite green, zero errors/warnings) → **CI parity** (every `pull_request` workflow step run locally, nothing skipped) → AT drift check empty. Commits AND pushes to the feature branch. No branches, no PRs. |
| **pr-reviewer** | PR review gate | Per its `pr-review-gate` skill (authoritative): scores the PR 1–10, independently re-checks tests and coverage, and on APPROVED **merges it into `dev` itself**; on REWORK reports filable findings to dev-leader (it creates no tickets — only the leader does); hands off when the gate cannot merge. |

There is no separate QC member in this squad: dev-backend writes the cycle's in-repo acceptance tests in their own stage, implements against them frozen in Build, and pr-reviewer is the independent second pass (including the mechanical AT-drift and mutation-report checks). The **SANDBOX BDD integration suite belongs to `qc-team`**, on its own `[T<num>-n]` cycle — never a `[D<num>-n]` stage and never gated here.

**No devops in this squad.** Pipeline, build/release-automation and helm work is never a `[D<num>-n]` stage and never gates this cycle. If a sub-task turns out to need one, the leader does NOT create it — post it on the `[P<num>-1]` phase ticket, then your handoff line on the main ticket; `product-team` owns routing it to devops.

## Mention directory (verified)

| Agent | Mention link |
|---|---|
| dev-leader | `[@dev-leader](mention://agent/9ec725c6-a4d7-4d08-bbbb-8034b29e307f)` |
| dev-backend | `[@dev-backend](mention://agent/52973d4e-b4cf-4b29-b5ad-6f120403c857)` |
| pr-reviewer | `[@pr-reviewer](mention://agent/74c810b2-ead5-4198-a141-eb4bc4409939)` |
| product-owner (upstream) | `[@product-owner](mention://agent/b1546eca-c984-4b7a-99a6-25bc5e1c12b0)` |

Re-verify with `multica agent list --output json` if a mention does not wake its target.

## Stages — the contract behind the Flow diagram

### Route A · code (full cycle)

| Stage | Title | Assignee | Created | Notes |
|---|---|---|---|---|
| ⚙ | *(no sub-task — leader inline)* | dev-leader | — | cut the feature branch from latest `dev` per `leader-gitops` BEFORE creating stage 1; name branch + base SHA in the Build description |
| 1 | `[D<num>-1] Acceptance tests: <scope>` | dev-backend | `todo` | branch gate first (`ls-remote`); description is the `sdlc-impl-brief` with its Acceptance-tests opening instruction. Deliverable: §7 as executable, RED scenarios + §5 stubs, `@existing` green, pushed. `done` ONLY with RED SHA + per-scenario table; a `@new` scenario already green, or a missing seam → `blocked` |
| ⚙ | *(no sub-task — leader inline)* | dev-leader | — | **AT approval**: `ls-remote` confirms the RED SHA; read the AT files against the spec (present / not softened / literal expected values / readable) — never run them; reject → re-arm stage 1 naming the scenario; accept → append `at_sha` + AT paths to the Build description, promote stage 2 |
| 2 | `[D<num>-2] Build: <scope>` | dev-backend | `backlog` | same brief + `at_sha`. Implement against frozen ATs; `done` ONLY on green: every `@new` + `@existing` scenario, full suite, zero errors, every touched class ≥80% + mutation report, `git diff <at_sha>..HEAD -- <AT paths>` empty, Standards self-review row reported (member-protocol check 8), CI parity reported with nothing skipped (member-protocol check 9, Policy 02 statement 10). Red suite, coverage gap or modified AT → `blocked` with the gap named, never `done` |
| ⚙ | *(no sub-task — leader inline)* | dev-leader | — | after stage 2 `done` with coverage + mutation + drift evidence: confirm the pushed tip via `ls-remote`, then open + verify the ONE PR (head = feature branch, base = `dev`, no close-intent keywords) per `leader-gitops`; post the PR URL on the cycle parent |
| 3 | `[D<num>-3] Review: <scope>` | pr-reviewer | `backlog` | promoted only after the leader posted the PR URL; description names repo, feature branch, `at_sha` + AT paths, the Build sub-task(s) a fix ticket would derive from, and where the PR URL, coverage and mutation evidence are reported |

### Route B · docs/config-only (light cycle)

| Stage | Title | Assignee | Created | Notes |
|---|---|---|---|---|
| ⚙ | *(no sub-task — leader inline)* | dev-leader | — | cut the feature branch from latest `dev` per `leader-gitops` BEFORE creating stage 1 |
| 1 | `[D<num>-1] Update: <scope>` | dev-backend | `todo` | branch gate first (`ls-remote`); the exact files and content changes named in the sub-task (no impl brief needed — the description IS the change list); commit + push, verify the push landed |
| ⚙ | *(no sub-task — leader inline)* | dev-leader | — | on a verified push (`ls-remote`, no coverage evidence exists on this route): open + verify the ONE PR per `leader-gitops`; post the PR URL on the cycle parent |
| 2 | `[D<num>-2] Review: <scope>` | pr-reviewer | `backlog` | promoted only after the leader posted the PR URL; APPROVED merges into `dev` as on Route A |

Stage 1 is the only stage created in `todo`. Every later stage is created `backlog` and promoted by the leader when the previous stage's barrier fires and its deliverable verifies — that promotion is the self-management contract; nothing else moves the cycle forward. The two ⚙ rows are NOT sub-tasks: the leader runs them itself, inline, in the same wake (branch cut before dispatching Build; PR open after the gate passes) — creating a Branch or PR sub-task for them is a defect. A cycle never switches routes midway: if a Route B change turns out to need a code edit, the leader adds a Build sub-task for dev-backend at the next unused stage number and says so on the cycle parent.

The Route A table shows the single-surface default. When the spec spans independent surfaces, each surface gets its own Acceptance-tests + Build pair: all Acceptance-tests sub-tasks at the SAME stage, all Builds at the next (or sequenced when one surface depends on another, playbook decomposition rules) — same-stage sub-tasks must touch disjoint files, since they share the one feature branch. Each Build sub-task carries its own `at_sha`, coverage bar and mutation report over the classes it touched. Review follows the last Build stage, and a fix ticket goes to the owner of whichever Build sub-task holds the files a finding touches. The rework loop below re-arms the **Review** stage by role, whatever its number.

## The rework loop — one gate, one loop

There is one gate in this squad: pr-reviewer at the Review stage. It fails one way, and **it creates nothing**: its own Review sub-task goes `blocked`, it posts ONE consolidated report on that sub-task, written filable (findings with `file:line`, recommendation per finding, acceptance criteria, `Suggested owner: dev-backend`, and the stage the fix must carry), and its handoff line on the phase ticket wakes dev-leader. **dev-leader then files ONE `Fix (review):` sub-task** from that report — consolidating anything that shares a root cause with an already-open fix — staged to the Review stage, **UNASSIGNED**, `Owner` set, handed to the resolved human owner by member mention. **The human assigns it before work starts, and the cycle intentionally waits on that**: an unassigned fix sub-task is awaiting-owner, never a stalled member, and nobody re-files or escalates it. A `Fix (review):` sub-task carries the whole round's findings — implementation defects, missing or thin tests, and coverage gaps alike, since dev-backend owns code and tests together (Policy 02 §1). Run the playbook's fix-loop pattern, with this squad's re-arm order:

1. **Review gate loop** (Review REWORK) — dev-leader files the consolidated fix sub-task from pr-reviewer's report and the owner assigns it; then dev-backend adds a reproduction test per finding (an addition — approved ATs stay frozen), fixes the implementation, re-runs the full suite, the coverage review and the mutation report, confirms the drift check against `at_sha` is still empty, pushes, reports on the fix sub-task and posts its handoff line. After the fix lands and `ls-remote` confirms the commit on the feature branch, the leader re-arms the **Review** stage (`blocked`→`in_progress --no-start`, pr-reviewer mention) for a full re-review of the updated PR. The Fix sub-task carries `Retrigger on done` = the Review key from creation; its `done` fires no barrier (same stage as the parked gate), so dev-backend ends its report with your mention and your wake-up checklist re-arms the issue the property names, then clears it. dev-backend never posts on the Review sub-task or mentions pr-reviewer; pr-reviewer never posts on the Fix sub-task — every hop passes through you. There is no separate verification stage to re-run — the suite and coverage evidence come back inside the fix report, and a fix report without green suite + coverage is not a landed fix: it ends `blocked`, not `done`.
2. **Build or Acceptance-tests blocked** — dev-backend cannot reach green or ≥80% (untestable path, missing seam, spec ambiguity), or finds an approved AT wrong: it ends `blocked` with a report on its OWN sub-task and its handoff line. The leader answers on that sub-task and re-arms it (`blocked`→`in_progress --no-start` + mention). A wrong approved AT is fixed by re-arming the Acceptance-tests sub-task and re-pinning `at_sha` — never by editing it in Build. Nobody files a ticket for this.
3. The PR needs no re-open — it tracks the branch. If it goes `CONFLICTING`, the leader runs the `leader-gitops` conflict procedure itself between Build green and Review (mechanical conflicts inline; substantive ones as a `Fix:` to dev-backend).
4. Caps: 2 failed rounds on the same root cause → escalate. pr-reviewer's own caps and handoff are owned by `pr-review-gate`; track its handoff, never duplicate it.

Gates: while any fix sub-task is open, an Acceptance-tests or Build sub-task sits `blocked`, `at_sha` is not pinned, a Build report lacks green suite + ≥80% per-touched-class coverage + mutation report + empty drift check, or the latest pr-reviewer verdict is REWORK/ESCALATED — no PR authorization, no promotion past the gate, no finalize; the cycle parent stays `in_progress`.

## Escalation — creator first, owner as fallback

When the squad cannot self-resolve (2 failed fix attempts on the same root cause, a product decision, missing credentials, a broken environment, out-of-scope work, or a gate handoff), stop looping and escalate in ONE comment:

- **Phase-ticket cycle** (the cycle parent has a parent) → comment on YOUR OWN phase ticket with product-owner's agent mention (the mention wakes product-owner there; the main ticket stays clean). product-team owns the human hop from there.
- **Root-ticket cycle** (no parent) → **reassign the stuck ticket to the human at `todo`** — the resolved owner per `sdlc-flow-delivery-pipeline` "Who the human owner is" (`Owner`-property-first → root member-creator → workspace owner; resolve at runtime, never hardcode): `multica issue update <id> --assignee-id <member-uuid> --status todo`. A member mention delivers nothing — the assignment is the escalation. Never an agent mention in an escalation to a human.

State what was tried, what failed, what decision you need, and what stays blocked until it arrives, in a `## BLOCKER` comment on the reassigned ticket.

## Status & stage management (leader-owned, every wake)

The full mechanics live in `sdlc-flow-squad-leader-playbook` — `--stage <n>` on every sub-issue you create (an unstaged child fires no barrier and the cycle silently dies — MXW-1187), the create/verify commands, the staging-stops-at-your-own-children rule, parent-status discipline, wake-up checklist, and finalize. Run its wake-up checklist FIRST on every wake, before creating, promoting, or answering anything.

- Cycle parent: `in_progress` from first dispatch until the gate passes. Never `in_review` on a phase ticket — that wakes nobody.
- Finalize per the playbook: PHASE ticket → `done` + plain report (no mention — the barrier wakes product-owner, who verifies score + merge and promotes the release); ROOT ticket → `in_review` per the playbook's finalize rules.