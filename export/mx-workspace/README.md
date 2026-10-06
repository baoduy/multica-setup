# Monxa Software Factory — how our AI delivery pipeline works

A team of AI agents takes a request — a new feature or a bug — and carries it all the
way to tested, deployed software, with people stepping in only at a few key decision
points. This page explains how that works, written for **everyone on the team**, not
just engineers.

**How to read this**

- **New here, or non-technical?** Read **Part 1** and **Part 2**. They're plain-English
and cover the whole story at a high level — no code, no jargon.
- **Working inside the pipeline?** **Parts 3–4** have the exact stages, branch rules,
skills, and definitions.
- **Stuck on a word?** Every term in *italics-on-first-use* is explained in the
**Glossary** at the very end (PR, SANDBOX, spec, gate, coverage, …).

*Reflects the live `mx-workspace` platform · last reconciled 2026-08-02.*

---

## Contents

- **Part 1 — Start here (for everyone)**
  - The factory line · The cast of characters · Where people come in
- **Part 2 — The teams**
  - 🦊 product-team · 🦍 dev-team · 🐸 qc-team
- **Part 3 — The pipeline in detail (technical)**
  - Feature flow · Bug flow · Branch &amp; environment strategy · The specialists · Human touch points
- **Part 4 — Reference &amp; maintenance (technical)**
  - Project boards · Skills · Agent models &amp; budget · Glossary · Change log

---

# Part 1 — Start here (for everyone)

*The whole system in three short reads: the assembly line, who does the work, and
where a human is needed.*

## The software factory — plain-English overview

*New here? Read this first. It's the very same pipeline documented below, told
without jargon. 🦊 the "foreman" always knows which step you're on.*

```
                    THE SOFTWARE FACTORY

  YOUR IDEA ──▶ "an app that studies reels and remixes them"
     │
     ▼
  ┌──────────────────────┐  asks numbered questions,       ──▶ the ticket SPEC
  │ 1. THE INTERVIEW     │  each with a guessed answer          (5 sections)
  │    (product-owner)   │
  └──────────────────────┘
     │
     ▼
  ┌──────────────────────┐  a fresh reader scores the spec ──▶ ✅ ≥ 9.0
  │ 2. THE PLAN CHECK    │  no build starts until it passes     or ⟲ rework
  │    (spec-reviewer)   │
  └──────────────────────┘
     │
     ▼
  ┌──────────────────────┐  the spec becomes 4 job tickets ──▶ [P#-1] build
  │ 3. THE WORK ORDERS   │  in order                            [P#-2a] release
  │    (product-owner)   │                                      [P#-2b] deploy
  └──────────────────────┘                                      [P#-3] QC
     │
     ▼
  ┌──────────────────────┐  nobody watching: build → test  ──▶ merged PR
  │ 4. THE NIGHT SHIFT   │  → PR → review, loops til green ⟲    into dev
  │    (dev squad)       │
  └──────────────────────┘
     │
     ▼
  ┌──────────────────────┐  merges dev → main;             ──▶ image built by CI
  │ 5a. THE RELEASE      │  CI builds the image                 (SANDBOX line)
  │    (release-manager) │  (automated — no human)
  └──────────────────────┘
     │
     ▼
  ┌──────────────────────┐  you push main → SANDBOX        ──▶ live on SANDBOX
  │ 5b. THE DELIVERY     │  (the one hands-on human step)
  │    (you, by hand)    │
  └──────────────────────┘
     │
     ▼
  ┌──────────────────────┐  fresh eyes who never met the   ──▶ test report
  │ 6. THE INSPECTOR     │  builders try to BREAK it            + any bugs filed
  │    (qc squad)        │
  └──────────────────────┘
     │
     ▼
  ┌──────────────────────┐  summary: spec → PR → deploy    ──▶ main ticket
  │ 7. THE SIGN-OFF      │  → QC, then the ticket closes        done ✅
  │    (product-owner)   │
  └──────────────────────┘
```

---

**Legend** — 👤 human · 🦊 product-owner · 🦉 spec-reviewer · 🐺 dev-leader · 🔨 dev-backend · 🐳 release-manager · 🦅 pr-reviewer · 🐝 qc-leader · 🐜 qc-tester · 🐞 qc-runner

**Trigger mechanics** — assignment at `todo` starts the assignee · `backlog→todo` promotion starts the assignee · child `done` fires the stage barrier that wakes the parent's owner · a child's handoff line on its parent (a `blocked`, or a `done` beside a `blocked` sibling) wakes the parent's owner — an agent's plain comment on a squad-assigned ticket or any sub-task under one wakes that squad's leader (the leader's wake guard ends a run this double-fires) · agent mention triggers a run (NOT deduped — one mention, one run, even when the target is already running) · member (human) mention notifies only. A stage barrier re-fires on every re-entry into `done`, so members never flip their own sub-task out of `done`; the LEADER re-triggers fix work by flipping the sub-task `in_progress --no-start` (adding the blocked gate's key to `Retrigger on done`, comma-separated when there are several) and then posting the ONE mention — the re-fired barrier (or the member's handoff line) is the expected "fix is back" signal. Every mention link in a posted comment is a wake, quoted or not. Members write only on their own ticket plus their handoff line, and mention nobody.

---

### The cast of characters

Every worker in the factory is an AI agent with one job and a nickname. You'll see these
icons throughout. **You don't need to memorise them** — this table is here to glance back at.


| Icon | Agent               | In plain English — what they do                                                                                |
| ---- | ------------------- | -------------------------------------------------------------------------------------------------------------- |
| 👤   | **you / requester** | File the request, answer business questions, and press the button to deploy to the test environment.           |
| 🦊   | product-owner       | The **project manager**. Turns your request into a clear written plan and drives it to done.                   |
| 🦉   | spec-reviewer       | The **plan checker**. Scores the plan before any building starts.                                              |
| 🐺   | dev-leader          | The **build foreman**. Splits the work into steps, checks each one, and owns the branch + pull request itself. |
| 🔨   | dev-backend         | The **builder**. Writes the tests first, then the product code, and won't sign off below the coverage bar.     |
| 🦅   | pr-reviewer         | The **code reviewer**. Scores the change and merges it once it passes.                                         |
| 🐳   | release-manager     | **Ships** approved code to the SANDBOX line.                                                                   |
| 🐝   | qc-leader           | The **QA foreman**. Plans the end-to-end integration tests, and owns the branch + pull request itself.         |
| 🐜   | qc-tester           | The **scenario writer**. Writes real end-to-end test scenarios.                                                |
| 🐞   | qc-runner           | The **test runner**. Runs the scenarios against the live test environment.                                     |
| 🐙   | devops              | The **pipeline &amp; infrastructure** specialist (CI/CD, helm charts).                                         |
| 🌙   | prd-release         | Promotes a tested SANDBOX release to **production**.                                                           |
| 🏛️  | arch-reviewer       | Monthly **architecture health check** of the .NET code.                                                        |
| 🧹   | issue-janitor       | Nightly **ticket cleanup**.                                                                                    |


*(🐲 claude_ultra and 🐼 default are general-purpose helpers, not part of the delivery line.)*

### Where people come in

On a normal run, **a human is needed at only three moments**: filing the request, answering
any business questions the agents can't answer from the code, and doing the final deploy to
the test environment (SANDBOX). Everything in between — building, testing, reviewing, merging
— runs on its own. The full list, including the rare "something went wrong" hand-offs, is in
[Part 3 › Human touch points](#4--human-touch-points).

---

# Part 2 — The teams

*Three squads do the work. Each has a leader who coordinates but never touches code, plus a
few specialists. This part gives each team's **goal** and a **step-by-step flow** — readable
without a technical background, though the stage codes (like `[P#-1]`) are there for the
engineers.*

## Teams (squads) — goal &amp; flow, per team

*The three squads the pipeline runs on. Each has a **leader** (its only orchestrating
member) plus gated worker roles; `pr-reviewer` is shared across squads. The two downstream
squad leaders (dev-leader, qc-leader) run their own cycle's git-flow inline, per
`leader-gitops` — no dedicated git-custodian agent.
Sourced from `squads/*.json` + each squad's briefing (`squads/<name>.md`) — the authoritative
Layer-3 definitions. Keep this in lock-step with those files.*


| Squad          | Icon | Leader        | Members (role)                                         | Home board    | Owns                                              |
| -------------- | ---- | ------------- | ------------------------------------------------------ | ------------- | ------------------------------------------------- |
| `product-team` | 🦊   | product-owner | spec-reviewer · release-manager · devops · pr-reviewer | `mx-main`     | the whole feature, requirement → SANDBOX-verified |
| `dev-team`     | 🦍   | dev-leader    | dev-backend · pr-reviewer                              | `mx-code`     | one merged `dev` PR of app code per cycle         |
| `qc-team`      | 🐸   | qc-leader     | qc-tester · qc-runner · pr-reviewer                    | `mx-qc-board` | the SANDBOX BDD integration suite                 |


`product-team` is the top of the chain: it delegates `[P#-1]` to **dev-team** and `[P#-3]`
to **qc-team** by squad assignment and consumes their results. The two downstream squads are
structurally identical — a leader that never touches code but runs its own cycle's git-flow
inline, a builder, a verify gate, and a PR-review-and-merge gate — differing only in what
they build.

### 🦊 product-team — own the feature end to end

**Goal.** Take a raw requirement to a spec that passed its review gate, then drive it through
implementation, release and SANDBOX deploy to integration-tested and verified — holding the
main ticket until the whole chain is provably complete. **Writes no product code; read-only
on code, always.** SANDBOX is the last environment it reaches (production is `prd-release`, §3.3).


| Member             | Role              | Owns                                                                                              |
| ------------------ | ----------------- | ------------------------------------------------------------------------------------------------- |
| 🦊 product-owner   | leader            | requirement analysis, research, the spec, all delegation, all phase promotion, main-ticket status |
| 🦉 spec-reviewer   | spec-review gate  | `[S#]` — scores the spec 1–10, APPROVES / REWORKS / hands to 👤                                   |
| 🐳 release-manager | release custodian | `[P#-2a]` — the ONE `dev`→`main` PR + merge in app repos                                          |
| 🐙 devops          | CI/CD &amp; helm  | `[P#-1b]` — pipelines, build/release automation, helm charts (only on the two CI/CD triggers)     |
| 🦅 pr-reviewer     | CI/CD PR gate     | `[P#-1c]` — scores devops' PR; merge authority differs by repo class                              |
| 👤 drunkcoding     | requester (human) | business clarifications, the BDD waiver, `[P#-2b]` SANDBOX deploy, helm-PR merge, escalations     |


```
👤 requirement lands — mx-main · assignee product-team · todo
  │
  ├── ①  ANALYSE   intake · labels · CodeGraph research (file:line evidence)
  │                clarification gate ⟲ → ZERO open questions · delivery scope (judged, ask if unsure)
  │                → ship_required + bdd_required metadata
  │
  ├── ②  SPEC      write the 7-section business spec into the main-ticket DESCRIPTION
  │
  ├── ③  GATE      [S#] Spec review → 🦉
  │                ✅ APPROVED (≥ 9.0) → ④   ⟲ REWORK (max 5) → revise + re-arm
  │                ⛔ > 5 rounds / unconfirmed product call → hand [S#] to 👤
  │
  ├── ④  DELEGATE  create ONLY the phases the spec calls for (conditional, not a checklist)
  │      ├─ app code             → [P#-1]  dev-team        todo   (desc = the FULL spec)
  │      ├─ pipeline/helm change → [P#-1b] devops          todo   ┐ only on a CI/CD trigger
  │      │                         [P#-1c] pr-reviewer     backlog┘ (config→chart, or 👤 asked)
  │      ├─ release to SANDBOX   → [P#-2a] release-manager backlog  ── only when ship_required ≠ false
  │      ├─ SANDBOX deploy       → [P#-2b] 👤 drunkcoding  backlog ┐ only when
  │      └─ BDD integration      → [P#-3]  qc-team         backlog ┘ bdd_required ≠ false
  │
  ├── ⑤  PROMOTE   one stage at a time — each only after the previous deliverable VERIFIES
  │                (never on `done` alone: e.g. [P#-1] needs a MERGED dev PR + reviewer score)
  │                ├─ ship_required=false → [P#-1] is TERMINAL (rides next release) → close at ⑥
  │                ├─ bdd_required=false  → [P#-2a] is TERMINAL → close at ⑥
  │                └─ ticket has a parent → [P#-1] is TERMINAL (parent releases all children) → close at ⑥
  │
  └── ⑥  CLOSE     main ticket → done + plain final summary · no mentions
```


**CI/CD lane (`[P#-1b]`/`[P#-1c]`).** Created only when a config value must reach the chart, or
👤 explicitly asked. Landing + merge authority is by repo class: app-repo feature-branch commit
(reviewed inside dev-team's PR, no `[P#-1c]`); app-repo standalone (`chore/<key>` PR → `dev`,
pr-reviewer scores **and merges**); helm repo (`chore/<key>` PR → `main`, pr-reviewer scores but
**never merges** — merging a chart PR *is* the deploy, so `[P#-2] Merge helm PR` goes to 👤).

### 🦍 dev-team — implement approved specs &amp; confirmed fixes

**Goal.** Implement the spec/fix for the Monxa .NET backends and deliver each request cycle as
**exactly ONE merged PR into `dev`**. Works `[P#-1]` from product-team; sub-tasks `[D#-n]` live
on `mx-code`; repos are the four service repos (email-service, auth-api, payment-gateway,
web-hook-deliverer). **No devops in this squad** — pipeline/helm work is never a `[D#-n]` stage.


| Member         | Role           | Owns                                                                                                                                                                                                   |
| -------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🐺 dev-leader  | leader         | triage, decompose, review, gate, stage/status, **and the cycle's git-flow** — cuts the feature branch and opens the ONE PR itself, inline, per `leader-gitops`; never writes code or runs builds/tests |
| 🔨 dev-backend | developer      | owns code AND the in-repo tests, in two separate runs: writes the spec's scenarios as RED acceptance tests first (`[D#-1]`), then — after 🐺 approves and freezes them — the implementation that turns them green (`[D#-2]`) with ≥ 80% coverage and a mutation report on every touched class · commits + pushes to the feature branch · no branches, no PRs |
| 🦅 pr-reviewer | PR-review gate | scores 1–10 · on APPROVED **merges into `dev` itself** · on REWORK dispatches ONE fix                                                                                                                  |


```
[P#-1] Implementation — cycle parent on mx-code · in_progress until the gate passes
  │   stage 1 is created `todo`; every later stage is `backlog`, promoted by 🐺 only when the
  │   previous barrier fires AND its deliverable verifies (the self-management contract)
  │
  ├── ⚙      BRANCH   🐺   leader cuts the feature branch inline from latest `dev` (no sub-task, `leader-gitops`)
  ├── D-1  BUILD    🔨   branch gate (`ls-remote`) first · implement to spec · commit + push
  ├── D-2  VERIFY   🧪   full suite green · zero errors · coverage > 80% on touched classes  ◀─┐
  ├── ⚙      PR       🐺   leader opens the ONE PR inline · head = feature branch · base = `dev` (no sub-task, `leader-gitops`) │
  └── D-3  REVIEW   🦅   PR-state guard, then score 1–10                                       │
          ├── ✅ APPROVED → 🦅 merges into `dev` → barrier wakes 🐺 (verifies merge + score)    │
          └── ⟲ REWORK / 🧪 red → ONE consolidated Fix: → 🔨, then ALWAYS re-arm D-2 first ────┘
                                   (review fix = unverified code; re-verify before re-review)
          ⛔ caps: 2 failed rounds on the same root cause → escalate (phase → 🦊; root → 👤)
```

**Docs/config-only requests take a light route** (routing decided FIRST by 🐺; when unsure,
full cycle): leader cuts the branch inline → `D-1 UPDATE 🔨` → leader opens the PR inline →
`D-2 REVIEW 🦅` — no Verify stage, because there is no test surface to verify. The 🦅 gate
still scores and merges (its coverage precondition is satisfied vacuously on a
no-coverable-lines diff); REWORK loops a fix to 🔨 via the leader and re-arms the Review stage directly,
same 3-round cap. The moment a change touches code or a config value that existing tests
assert, it is the full cycle.

### 🐸 qc-team — the SANDBOX BDD integration suite

**Goal.** Build and maintain the **BDD integration suite** — Gherkin scenarios run as real HTTP
calls against the deployed SANDBOX — and deliver each cycle as **ONE merged PR into `dev` of
`monxa.bdd-integration`**. Coverage bar: **every in-scope OpenAPI endpoint, ≥ 1 positive AND
≥ 1 negative scenario**. Works `[P#-3]` from product-team; `[T#-n]` sub-issues on `mx-qc-board`.
**WRITE only `monxa.bdd-integration`; READ the four service repos** (for contracts/edge cases).


| Member         | Role                        | Owns                                                                                                                                                                                                                           |
| -------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🐝 qc-leader   | leader                      | endpoint × (positive,negative) matrix · test plan · decompose · gate · consolidated report · auto bug-filing · **and the cycle's git-flow** — cuts the feature branch and opens the ONE PR itself, inline, per `leader-gitops` |
| 🐜 qc-tester   | scenario developer          | writes + executes NEW/changed Gherkin against SANDBOX · commits + pushes · no branches/PRs/bugs                                                                                                                                |
| 🐞 qc-runner   | review &amp; execution gate | reviews scenarios vs the matrix, runs the **impacted scope** against SANDBOX · verdict gates the PR                                                                                                                            |
| 🦅 pr-reviewer | PR-review gate              | scores 1–10 · merges into `dev` on APPROVED · loops REWORK back to 🐜                                                                                                                                                          |


```
[P#-3] BDD integration tests — cycle parent on mx-qc-board
  │
  ├── ROUTE A · RUN-ONLY   existing coverage only (regression / re-verify after a fix)
  │   └── T-1  RUN   🐞   impacted scope against SANDBOX · no branch · no PR · no matrix gate → report
  │
  └── ROUTE B · DEVELOPMENT   coverage missing or changing — three staged sub-issues + two leader-inline git steps (mirrors dev-team)
      ├── ⚙      BRANCH     🐝   leader cuts the feature branch inline from latest `dev` of monxa.bdd-integration (no sub-task, `leader-gitops`)
      ├── T-1  SCENARIOS  🐜   branch gate first · implement + execute the matrix rows in this batch
      ├── T-2  VERIFY     🐞   green ONLY when: every in-scope endpoint has +/− present ·          ◀─┐
      │                        impacted scope runs zero-fail vs SANDBOX · BDD quality bar met        │
      │                        (selection VISIBLE in the report — narrow run ≠ "suite green")        │
      ├── ⚙      PR         🐝   leader opens the ONE PR inline · head = feature branch · base = `dev` (no sub-task, `leader-gitops`) │
      └── T-3  REVIEW     🦅   score 1–10                                                             │
              ├── ✅ APPROVED → 🦅 merges into `dev` → barrier wakes 🐝                                │
              └── ⟲ REWORK / 🐞 test-code red → ONE Fix: → 🐜, then ALWAYS re-arm T-2 first ──────────┘
              ⛔ caps: 2 failed rounds same root cause → escalate

  ◆ platform defect found (not test-code)  → 🐝 AUTO-files ONE consolidated, deduped bug to mx-main → 🦊
    (a scenario proving a defect is CORRECT test code — tag it known-issue, land the PR, track on the bug)
```

**Impacted scope, not full suite.** T-2 runs a change-focused regression (everything added/changed

- the same-endpoint neighbourhood + anything sharing fixtures/data), not the whole suite — 🐝 names
it, 🐞 may only widen it. Full-suite execution belongs to the PRD release path (`prd-release`).

---

---

# Part 3 — The pipeline in detail (technical)

*The exact machinery: how a feature and a bug each move through the system, the branch and
environment rules, the specialist agents that run off to the side, and every point a human
is involved. If you're not an engineer, you can stop after Part 2 — nothing below changes the
big picture.*

## 1 · Feature flow (Workflow B)

### At a glance

```
   ①           ②           ③           ④           ⑤           ⑥           ⑦           ⑧
  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
  │  SPEC  │─▶│  GATE  │─▶│ SPLIT  │─▶│ BUILD  │─▶│RELEASE │─▶│ DEPLOY │─▶│   QC   │─▶│ CLOSE  │
  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
   🦊          🦉           🦊           🐺          🐳          👤           🐝          🦊
   intake      score       4 phase     code +      dev→main    main        verify      summary
   research    ≥ 9.0       tickets     merge       merge       SANDBOX     SANDBOX     + done
   clarify     or rework   in order    into dev     (auto)
```

### Step by step

```
┌─────────────────────────────────────────────────┐
│ The main ticket — mx-main · from filing to done │
└─┬───────────────────────────────────────────────┘
  │
  ├── ①  INTAKE & SPEC — 🦊 product-owner
  │   ├── start     👤 files the main ticket   mx-main · assignee 🦊 · todo
  │   ├── research  checkout dev · CodeGraph first · cite claims as file:line
  │   ├── clarify   ⟲ numbered questions + guesses + @👤 ─▶ STOP ─▶ repeat until zero
  │   │             (never ask what the code already answers; only a written reply answers)
  │   ├── preview   spec preview + @👤 ─▶ STOP ─▶ written approval
  │   └── spec      7 sections into the ticket DESCRIPTION · no open questions
  │
  ├── ②  SPEC-REVIEW GATE — 🦉 spec-reviewer
  │   ├── start     🦊 opens [S#] Spec review   parent = main · 🦉 · todo
  │   ├── score     verify every file:line, then weigh:  traceability 25%
  │   │            · Gherkin 20% · business clarity 20% · architecture fit 15%
  │   │            · completeness 10% · security 10%
  │   ├── pass      ✅ ≥ 9.0 and no blockers ─▶ [S#] done · verdict + @🦊 ─▶ ③
  │   ├── review    ◔ 8.0–8.9 or a trigger ─▶ REVIEW REQUESTED — 👤 holds [S#]
  │   ├── rework    ⟲ < 8.0 or any blocker ─▶ findings + @🦊 ─▶ 🦊 revises,
  │   │             re-arms [S#] ─▶ full re-review               rounds 1–5
  │   └── cap       ⛔ round > 5 ─▶ 👤 requester · their done-flip releases it
  │
  ├── ③  SPLIT INTO PHASES — 🦊 product-owner · Workflow C
  │   ├── start     [S#] done wakes 🦊 · FYIs 👤 with the score
  │   ├── create    the phases the scope authorizes, in order
  │   │   ├── [P#-1] Implementation           ─▶ dev-team         todo · desc = the spec
  │   │   ├── [P#-2a] Release to SANDBOX       ─▶ release-manager  backlog · dev→main PR + merge   ── ship_required ≠ false
  │   │   ├── [P#-2b] SANDBOX deploy (DevOps)  ─▶ 👤 requester     backlog · main→SANDBOX ┐ bdd_required
  │   │   └── [P#-3] BDD integration           ─▶ qc-team          backlog               ┘ ≠ false
  │   └── note      idempotent — existing children checked first · ship_required=false ⇒ [P#-1] only · sub-issue (has parent) ⇒ [P#-1] only
  │
  ├── ④  DEV CYCLE — 🐺 dev-leader
  │   ├── start     [P#-1] todo · sub-tasks in mx-code · questions ─▶ MAIN + @🦊
  │   ├── git-flow  🐺 cuts the feature branch and opens the ONE PR itself, inline, per `leader-gitops` — no sub-task for either
  │   ├── stages    three sub-tasks, in order (leader cuts the branch first)
  │   │   ├── [D#-1] acceptance tests 🔨   spec §7 ─▶ executable scenarios, RED · commit + push
  │   │   ├── (🐺 reads them against the spec, pins `at_sha` — frozen from here)
  │   │   ├── [D#-2] build  🔨   implement against the frozen scenarios ─▶ green · ≥ 80% · mutation report · drift check empty
  │   │   ├── (🐺 opens the ONE PR inline · feature ─▶ dev, never main)
  │   │   └── [D#-3] review 🦅   PR-state guard first, then AT drift + score 1–10
  │   ├── loops     rework, max 3 rounds
  │   │   ├── ⟲ AT rejected / wrong ─▶ re-arm [D#-1] ─▶ 🔨 (never edited in build)
  │   │   └── ⟲ [D#-3] rework    ─▶ ONE Fix ─▶ 🔨   ⛔ 3 rounds ─▶ 👤 owner
  │   ├── done      ✅ 🦅 merges into dev · in-scope leftovers ─▶ Merged with: (no ticket) ─▶ 🦊
  │   └── ═══ barrier · wakes 🦊 — verifies the merged PR + review score ═══
  │
  ├── ⑤  RELEASE — 🐳 release-manager
  │   ├── start     🦊 promotes [P#-2a] ─▶ todo + comment (PR link, score)
  │   ├── release   🐳 opens ONE dev→main PR, merges it (automated, no human)
  │   │             CI then builds the image on `main` (the SANDBOX line)
  │   └── ═══ barrier · wakes 🦊 — promotes [P#-2b] ═══
  │
  ├── ⑥  DEPLOY — 👤 requester
  │   ├── start     🦊 promotes [P#-2b] ─▶ todo + comment (release PR link)
  │   ├── deploy    👤 argoCD-deploys main ─▶ SANDBOX · flips [P#-2b] done
  │   │             the one remaining hands-on human step
  │   └── ═══ barrier · wakes 🦊 — refreshes [P#-3] with PR + deploy facts ═══
  │
  ├── ⑦  QC CYCLE — 🐝 qc-leader
  │   ├── start     [P#-3] todo · sub-issues in mx-qc-board · wake checklist
  │   ├── route A   DEVELOPMENT — new coverage is needed
  │   │   ├── (🐝 cuts the feature branch inline, per `leader-gitops` — no sub-task)
  │   │   ├── [T#-1] test   🐜   write + run against SANDBOX
  │   │   ├── [T#-2] verify 🐞   review scenarios + impacted-scope execution
  │   │   ├── (🐝 opens the ONE PR inline · feature ─▶ dev)
  │   │   └── [T#-3] review 🦅   same gate as dev · ⛔ 3 rounds ─▶ 👤
  │   ├── route B   RUN-ONLY — existing suites already cover it
  │   │   └── [T#-1] run    🐞   the suites against SANDBOX · no branch, no PR
  │   ├── defects   🐝 files ONE consolidated, deduped bug ─▶ 🦊 (todo)
  │   ├── done      consolidated test report on [P#-3] ─▶ done
  │   └── ═══ barrier · wakes 🦊 — verifies report + merged QC PR ═══
  │
  └── ⑧  CLOSE — 🦊 product-owner
      ├── done      main ticket ─▶ done · summary: spec ─▶ release ─▶ deploy ─▶ QC
      └── note      production tagging is automatic in CI/CD downstream, outside this flow
```

---

## 2 · Bug flow (Workflow A)

### At a glance

```
  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
  │    FILE    │─▶│ ROOT CAUSE │─▶│ CONFIDENCE │─▶│ WORKFLOW C │─▶│   CLOSE    │
  └────────────┘  └────────────┘  └────────────┘  └────────────┘  └────────────┘
   👤 or 🐝        🦊              ◆ gate          🐺 🐳 👤 🐝     🦊
   files a bug     evidence +      ≥ 90% auto      same as         summary
                   confidence %    < 90% ask 👤    ④ ⑤ ⑥ ⑦        + done
```

### Step by step

```
┌────────────────────────────────────────────────┐
│ The bug ticket — mx-main · from filing to done │
└─┬──────────────────────────────────────────────┘
  │
  ├── ①  INTAKE — 🦊 product-owner
  │   ├── start     two origins
  │   │   ├── (a) 👤 files a bug ticket   mx-main · 🦊 · labels main + bug
  │   │   └── (b) 🐝 auto-files from QC — ONE consolidated, deduped ticket
  │   │
  │   ├── research  checkout · CodeGraph · reproduce the conditions
  │   └── clarify   ⟲ symptoms / repro / expected vs actual + @👤
  │                 ─▶ STOP ─▶ repeat until answered
  │
  ├── ②  ROOT-CAUSE REPORT — 🦊 · a comment on the main ticket
  │   ├── report    direct answer ─▶ evidence (file:line + call paths)
  │   │             ─▶ root cause · affected components · repro conditions
  │   │             ─▶ fix direction — the layer ALL callers route through
  │   └── score     calibrated confidence 0–100% — genuine platform defect?
  │
  ├── ③  CONFIDENCE GATE — ◆ three outcomes
  │   ├── ask only  a question, no change wanted ─▶ END — report delivered
  │   ├── pass      ✅ ≥ 90% confirmed ─▶ auto-delegate Workflow C
  │   │             FYI 👤 (root cause, confidence, "reply to halt")
  │   └── hold      ⛔ < 90% — may be by-design / config / user error
  │                 ─▶ 👤 reviews and explicitly confirms first
  │
  └── ④  WORKFLOW C — same machinery as the feature flow
      ├── basis     the root-cause report · spec only if 👤 asks (then 🦉 gate)
      ├── phases    same four, in order
      │   ├── [P#-1]  🐺 dev cycle (branch/PR inline · D-1…D-3 · loops · 🦅 merge gate)
      │   ├── [P#-2a] 🐳 release-manager — dev→main PR + merge (CI builds image)
      │   ├── [P#-2b] 👤 SANDBOX deploy (DevOps)
      │   └── [P#-3]  🐝 QC — usually RUN-ONLY re-verification
      │ 
      └── close     🦊 main ticket ─▶ done + summary
```

---

## Git branch &amp; environment flow

*How the pipeline's commits move through branches and out to environments. The
mechanics live in the `sdlc-gitflow` skill; this is the shape it enforces.*

### Topology — who may open which PR

```
  ┌──────────────────────┐           ┌──────────────────────┐           ┌──────────────────────┐
  │ feature/<key>-<slug> │────PR────▶│         dev          │────PR────▶│         main         │
  └──────────────────────┘           └──────────────────────┘           └──────────────────────┘
   🐺 dev-leader / 🐝 qc-leader        INTEGRATION branch                  SANDBOX branch · release
   one branch per issue,               all feature work lands              🐳 release-manager opens
   cut from origin/dev,                here — the squad leaders open       AND merges the ONE dev→main
   inline per `leader-gitops`          each feature→dev PR, inline         PR (automated) · CI then
   commit + push, never                                                   builds the image
   checkout a shared branch
```

Feature work **never** PRs to `main`. Only 🐳 release-manager opens `dev → main`; only the
squad leaders (dev-leader / qc-leader) open `feature → dev`, inline per `leader-gitops`. 🐙
devops is the sole exception — it commits CI/CD config **directly to `dev`** (no PR) and
touches nothing else.

### Branch → environment

```
   dev   ─────────────────────────▶  INTEGRATION   feature PRs land here continuously
   main  ── CI builds the image ──▶  SANDBOX        👤 argoCD-deploys main → SANDBOX   [P#-2b]
   main  ── 🌙 prd-release      ──▶  PRD            promotes SANDBOX helm tags → PRD;
                                                     merging the release PR IS the prod deploy
```

### Rules that never bend

- **Both refs explicit, every PR** — `gh pr create --head <branch> --base dev …`. A missing
`--base` silently targets `main`; a missing `--head` yields an empty or wrong diff that
still reports success.
- **One PR body shape** — Summary (a text visual of the change) · Evidence (red before,
green after, every check that could not run) · Merge danger (one-way or two-way door, blast
radius), passed with `--body-file` (Policy 03 statement 7a, `sdlc-gitflow`). Release PRs keep
their own format.
- **Remote-only branch ops** — never `git checkout` `dev`, `main`, or a shared feature
branch; a checkout locks it against every other agent, potentially past the end of the task.
- **Branch from freshly fetched `origin/dev`** — never a stale local ref. Conventional
Commits; PR titles carry the `[<KEY>]` issue prefix for issue↔PR autolinking.
- **No one commits to `main`.** Production tagging is automatic in CI/CD downstream — no
agent does it.

---

## 3 · Standalone &amp; off-pipeline agents

Four agents run **outside** the feature/bug pipeline (§1–§2): 🏛️ arch-reviewer, 🧹
issue-janitor, 🌙 prd-release and 🐙 devops. Each does its whole job alone, belongs to no
squad, and reports by status (`done` on success, `blocked` when stuck — never
`in_review`, which fires no trigger), plus a handoff line on the parent when a ticket that has one goes `blocked`. What differs is the trigger: arch-reviewer and
issue-janitor fire on a **schedule** (a Multica autopilot); prd-release and devops fire on
**ticket assignment**. All four appear in §5 (skills) and §6 (models) like every other agent.

**Legend** — 🏛️ arch-reviewer · 🧹 issue-janitor · 🌙 prd-release · 🐙 devops · 👤 human · 🤖 CI / DevOps (no human)

### 3.1 · 🏛️ arch-reviewer — monthly .NET architecture sweep

Audits the Monxa .NET services against DKNet DDD conventions and .NET 10 / EF Core 10
standards, files the highest-value findings into the backlog for human triage, and converts
whatever is mechanically checkable into permanent architecture tests.
Skills: `architecture-review-sweep` (the workflow) · `dknet-ddd-conventions` ·
`dotnet10-efcore10-standards` · `codegraph` · `sdlc-gitflow` (enforcement PRs).

#### At a glance

```
  ┌─────────┐   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   ┌────────┐
  │ TRIGGER │──▶│ INDEX  │─▶│ANALYSE │─▶│  RANK  │─▶│ DEDUPE │─▶│  FILE  │─▶│ENFORCE │──▶│ REPORT │
  └─────────┘   └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘   └────────┘
   monthly       codegraph   prod .cs    crit →      per-repo    ≤10/repo    test-only    one run
   🤖 02:00 SGT   init        only        low         fingerprint →backlog    PR → dev     issue → done
                 └────────── repeated per repo: auth-api · email-service · payment-gateway ──────────┘
```

#### Step by step

```
┌───────────────────────────────────────────────────┐
│ The run issue — mx-jobs · 1st of month, 02:00 SGT │
└─┬─────────────────────────────────────────────────┘
  │
  ├── ①  TRIGGER   autopilot files the run issue in mx-jobs · assignee 🏛️
  │                (if it names one repo, review only that one)
  │
  ├── ②  PER REPO — auth-api ─▶ email-service ─▶ payment-gateway · each an independent sweep
  │   ├── INDEX    checkout · read the repo's own CLAUDE.md/AGENTS.md (local conventions win)
  │   │           · codegraph init . · confirm nodes/edges > 0 (else Grep/Read, and say so)
  │   │ 
  │   ├── ANALYSE  every production .cs · exclude tests, obj/, bin/, Migrations/,
  │   │            GeneratedDtos/, *.g.cs, *.Designer.cs
  │   │ 
  │   ├── RANK     findings critical → high → medium → low
  │   ├── DEDUPE   vs already-filed · fingerprint <repo>:<rule-id>:<path>:<Symbol>
  │   ├── FILE     ≤ 10 issues → mx-main · backlog · assignee drunkcoding (--assignee-id)
  │   │           · arch_finding / arch_severity / arch_repo metadata · overflow → report only
  │   │ 
  │   └── ENFORCE  architecture tests (Tier 1 clean · Tier 2 allow-list · Tier 3 backlog)
  │               · test-only PR --head <branch> --base dev · product code never touched
  │
  └── ③  REPORT    one consolidated report across all target repos on the run issue → done
                  · a failure in one repo never aborts the others · skipped work is named
```

### 3.2 · 🧹 issue-janitor — nightly issue hygiene

Keeps the workspace issue graph clean: propagates terminal parent status to forgotten
sub-issues, then deletes long-cancelled issues children-first. Self-contained — no shared
skills, its whole procedure lives in `instructions`.

#### At a glance

```
  ┌─────────┐   ┌───────────┐   ┌───────────┐   ┌────────┐   ┌────────┐
  │ TRIGGER │──▶│ PAGINATE  │──▶│ PROPAGATE │──▶│  PRUNE │──▶│ REPORT │
  └─────────┘   └───────────┘   └───────────┘   └────────┘   └────────┘
   nightly       all issues     terminal parent  delete       honest —
   🤖              100/pg        → open children  cancelled    partial is
                 (total 100      status only      ≥ 7d, kids   reported
                  → abort)                          first      partial
```

#### Step by step

```
┌────────────────────────────────────────────────────┐
│ Nightly hygiene sweep — the whole workspace graph  │
└─┬──────────────────────────────────────────────────┘
  │
  ├── ①  TRIGGER     autopilot wakes 🧹 nightly · one job only · declines anything else
  │
  ├── ②  PAGINATE    multica issue list --limit 100 --offset N · loop until a page < 100
  │                 · a total of exactly 100 = pagination failure → ABORT
  │
  ├── ③  PROPAGATE   push terminal parent status onto forgotten sub-issues
  │                 · rewrites OPEN statuses only (todo · in_progress · in_review · blocked · backlog)
  │                 · never touches a done or cancelled record (those are terminal)
  │
  ├── ④  PRUNE       delete long-dead issues, children before parents
  │                 · only status cancelled AND updated_at ≥ 7 days old
  │                 · any ineligible descendant ─▶ SKIP the parent and report it
  │                 · DELETE {server_url}/api/issues/{id} + Bearer (authorized 2026-07-27 —
  │                    no CLI delete exists) · token never printed or logged
  │
  └── ⑤  REPORT      honest run report · partial success reported as partial, never a clean
                     sweep it did not actually complete
```

### 3.3 · 🌙 prd-release — SANDBOX → PRD promotion

Promotes SANDBOX image tags into the Monxa PRD helm charts and opens the release PR — the
PRODUCTION analogue of release-manager's SANDBOX cut, but with the deploy gate held by a
human: **merging the release PR *is* the production deploy** (DevOps `mx-apps` auto-syncs
it, prune + selfHeal on), so 🌙 builds and verifies the release but never merges it on its
own judgement. Loads only `sdlc-gitflow`. Runs in two turns.

#### At a glance

```
  RUN 1 · build the release PR                              triggered: requester assigns a release issue

  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
  │  READ  │─▶│ DRIFT  │─▶│  EDIT  │─▶│  GATE  │─▶│RESEARCH│─▶│  NOTE  │─▶│   PR   │─▶│  BDD   │─▶ handoff
  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘  └────────┘
   ticket +    SANDBOX vs  values.yaml 7 checks:   gh compare  ⚠ risk +    → main      smoke vs    issue stays
   overrides   PRD tags    + images.json helm       per image   shipping    (NOT        SANDBOX ·   in_progress
               (∅ → done)               renders                            merged)     tag-window

----------------------------------------------------------------------------------------------------------------
  RUN 2 · approve or close                                  triggered: a comment on the ticket
              ◆ pick the case

  ┌──────────────┐   ┌───────────┐   ┌────────┐   ┌────────┐
  │ read comment │──▶│ RE-VERIFY │──▶│ MERGE  │──▶│ CLOSE  │
  └──────────────┘   └───────────┘   └────────┘   └────────┘
   A approve /        4 stale          release PR   done /
   B self-merged /    checks           = DEPLOY     in_progress /
   C ambiguous        (fail → stop)    🤖 DevOps   cancelled
```

#### Step by step

```
┌────────────────────────────────────────────────────────────────┐
│ The release issue — mx-prd-releases · from assignment to done  │
└─┬──────────────────────────────────────────────────────────────┘
  │  merging the release PR IS the production deploy — that decision is the requester's;
  │  executing it is 🌙's. The BDD test PR touches only the test repo, so 🌙 may merge that one.
  │
  ├── ①  RUN 1 — build the release PR · 🌙 woken by assignment
  │   ├── READ      install helm · read ticket (creator · `only:` / `bdd-ref:` overrides)
  │   │            · move into mx-prd-releases · set in_progress
  │   ├── DRIFT     read origin/main tags — SANDBOX (infra-v2.helm-charts) vs PRD
  │   │             (monxa.helm-charts) · build key/old/new table · apply `only:` scope
  │   │            · ∅ drift ─▶ "already at parity" · done · no PR · STOP
  │   ├── EDIT      write charts/mx-apps/values.yaml + acr-sync/images.json ONLY,
  │   │             per the repo's update-image-tags mapping (missing map ─▶ abort)
  │   ├── GATE      7 checks: json valid · exactly 2 files changed · anchors preserved
  │   │            · identical image paths · count = promoted keys · helm lint · helm
  │   │             template renders the NEW tags   (any fail ─▶ abort · leave uncommitted · blocked)
  │   ├── RESEARCH  per image: gh compare old…new · filter merge/junk subjects · detect
  │   │             risk mechanically (migrations · appsettings · Dockerfile · auth · reverts…)
  │   ├── NOTE      release note: header + provenance SHA · ⚠ deploy risk · what's shipping
  │   │            · "after merge = deploy" · never a result it does not yet have
  │   ├── PR        branch release/prd-<id> from origin/main · commit the 2 files · push
  │   │            · gh pr create --base main   (opened, NOT merged)
  │   ├── BDD       pick ref (dev if ahead of main, else main · `bdd-ref:` overrides)
  │   │   │        · dispatch bdd-sandbox-daily.yml · ONE blocking watch · download report
  │   │   │        · tag-window recheck — SANDBOX moved? ─▶ report is not evidence, say so loudly
  │   │   │        · red suite ─▶ draft the release PR so it can't be merged by reflex
  │   │   ├── open BDD PR (dev→main) only if tested dev AND green
  │   │   └── merge the BDD PR only (green + mergeable) · NEVER the release PR
  │   │ 
  │   └── HANDOFF   comment: promotion table · risk block · BDD result · both PR links · @creator
  │                · the release PR waits on their decision · issue stays in_progress
  │                 (in_review fires no trigger — their approval reply would strand the release)
  │
  └── ②  RUN 2 — approve or close · 🌙 woken by a ticket comment
      ├── ◆ read the comment, pick the case (can't tell ─▶ Case C · never guess a prod merge)
      ├── A approve      re-verify 4 stale checks — PR head unchanged · SANDBOX still matches
      │                 · still mergeable · still renders · any fail ─▶ don't merge, name which
      │                 · else merge BDD PR (if green+open) then the release PR · confirm · done
      ├── B self-merged  verify PR state ─▶ done (merged) / in_progress (open) / cancelled (closed)
      └── C anything else  merge nothing · answer, or ask for an explicit `approve` · in_progress
```

### 3.4 · 🐙 devops — CI/CD pipeline setup

Keeps the CI/CD pipelines, helm chart configuration and docker-compose files correct — and
nothing else. App-repo changes land via the squad's feature branch or one gated
`chore/<issue-key>` PR to `dev`, never a direct commit; every chart change is a PR a human merges.
Skills: `compose-delivery` · `helm-chart-delivery` · `sdlc-gitflow` (full list in §5).

#### At a glance

```
  ┌─────────┐   ┌───────────┐   ┌──────────┐   ┌─────────────┐   ┌────────────┐   ┌────────┐
  │ ASSIGN  │──▶│   SCOPE   │──▶│ CHECKOUT │──▶│  EDIT CI/CD │──▶│ PUSH → dev │──▶│ REPORT │
  └─────────┘   └───────────┘   └──────────┘   └─────────────┘   └────────────┘   └────────┘
   a CI/CD       CI/CD only?     the repo(s)    .github/          commit direct    one summary
   ticket · 👤   else refuse                    workflows ·       to dev only      · done
                                                azure-pipelines
```

#### Step by step

```
┌─────────────────────────────────────────────────┐
│ A CI/CD ticket — 🐙 devops · dev branch only    │
└─┬───────────────────────────────────────────────┘
  │
  ├── ①  ASSIGN      👤 assigns a pipeline task to 🐙
  ├── ②  SCOPE       CI/CD only — pipeline YAML, build scripts, deploy workflows, CI/CD IaC
  │                 · anything touching app code, tests, or docs ─▶ refuse politely, explain scope
  │
  ├── ③  CHECKOUT    multica repo checkout the target repo(s) — one of the Monxa repos
  │                  (email-service · auth-api · payment-gateway · web-hook-deliverer · bdd-integration)
  │
  ├── ④  EDIT CI/CD  create/modify .github/workflows/*.yml · azure-pipelines.yml · release automation
  │  
  ├── ⑤  PUSH → dev  commit + push directly to dev with clear messages · never another branch
  │                  (refuse a non-dev target unless the user explicitly overrides)
  │
  └── ⑥  REPORT      ONE plain summary comment · status done (never in_review) · can't proceed
                     ─▶ blocked + the blocker · no agent-mentions in comments (they enqueue runs)
```

---

## 4 · Human touch points

### Best case — happy path (every run)


| #   | Touch point                              | State         | Detail                                                                                                                    |
| --- | ---------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| 1   | File the request                         | 👤 always     | the request itself — irreducible                                                                                          |
| 2   | Business clarifications                  | 👤 always     | rules/scope the code cannot answer, then the spec preview approved in writing; agents forbidden from asking what the repo answers |
| 3   | Spec approval                            | 🤖 automated  | 🦉 gate, APPROVED at ≥9.0 with no blockers (8.0–8.9 → requester review)                                                                                |
| 4   | Bug-fix approval                         | 🤖 automated  | ≥90% confidence → auto-delegate (FYI only, reply to halt)                                                                 |
| 5   | SANDBOX deploy (P#-2b, DevOps)           | 👤 deliberate | requester deploys `main` → SANDBOX; the `dev`→`main` release (P#-2a) is automated                                         |
| 6   | QC bug filing                            | 🤖 automated  | 🐝 auto-files consolidated deduped ticket to 🦊                                                                           |
| 7   | Review follow-ups                        | 🤖 automated  | 🦅 → 🦊 triage; owner sees only genuine human decisions                                                                   |
| 8   | Release to SANDBOX (`dev`→`main`, P#-2a) | 🤖 automated  | release-manager opens + merges the PR; CI builds the image; production tagging is automatic downstream, outside this flow |


Happy path: a feature touches humans at #1, #2, #5 only; a bug at #1 (and #2 when clarification is needed).

### Worst case — escalation valves (only when a gate trips)


| #   | Touch point            | State    | Detail                                                                          |
| --- | ---------------------- | -------- | ------------------------------------------------------------------------------- |
| 9   | Bug-fix confirmation   | 👤 gate  | &lt;90% confidence — may be by-design / config / user error → 👤 confirms first |
| 10  | Spec gate escalation   | 👤 valve | &gt;5 rework loops → requester manual review                                    |
| 11  | PR gate escalation     | 👤 valve | 3 rework rounds / deferred / failed merge → workspace owner                     |
| 12  | Squad stuck escalation | 👤 valve | 2 failed fix attempts on same root cause → owner/🦊                             |


Worst case adds these on top of the happy-path touches — each is a capped loop that hands control to a human instead of spinning forever.

**How an escalation reaches you:** by ASSIGNMENT — the stuck ticket (a gate's review sub-task, a blocked child) is reassigned to the creator (else the ticket's `Owner` property, else owner) at `todo`, with a `## BLOCKER` comment on it. A member mention renders a link but delivers no notification, so it is never the delivery mechanism.

---

---

# Part 4 — Reference &amp; maintenance (technical)

*The boards work is tracked on, the skills each agent loads, the AI models behind each role
and why, a plain-English glossary, and the log of what changed. Edit these in lock-step with
the definition files (see [`CLAUDE.md`](./CLAUDE.md)).*

> **Role charters.** Each agent's goal, responsibilities, and hard boundaries are chartered in
> [Policy 09 — Agent Roles &amp; Responsibilities](docs/policies/09-agent-roles-and-responsibilities.md)
> (governance: [`docs/policies/`](docs/policies/00-policies-index.md)); every agent's
> instructions open with its charter Goal. `default` and `claude-ultra` are platform
> assistants outside the factory roster. Notably: dev-backend owns implementation AND the
> in-repo tests, but in two separate runs — acceptance tests first, approved and frozen by
> dev-leader, then the implementation against them (there is no separate in-repo QC role —
> pr-reviewer is the independent second pass), while qc-tester writes SANDBOX integration
> scenarios and qc-runner gates them.

## Projects (boards)

*The five Multica projects the pipeline runs on — every ticket, sub-task, and run
issue lives on one of these boards. The names used throughout §1–§3 (`mx-main`,
`mx-code`, …) refer to these. Generated from `projects/*.json`; keep in lock-step with
those files and the `manifest.json` `projects[]` entries.*


| Project              | Lead             | Status      | What lives here — and where the flow uses it                                                                                          | Repositories                                                                      |
| -------------------- | ---------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| ❇️ `mx-main`         | 🦊 product-owner | planned     | Feature &amp; bug intake, spec, planning, close — the pipeline's front door (§1 ①–③⑧ · §2). 🏛️ arch-reviewer files findings here too | auth-api · bdd-integration · email-service · payment-gateway · web-hook-deliverer |
| 👨‍💻 `mx-code`      | 🐺 dev-leader    | in progress | Dev-team implementation sub-tasks `[D#-1…D#-3]` (§1 ④)                                                                                | email-service · auth-api · payment-gateway · web-hook-deliverer                   |
| ❤️‍🔥 `mx-qc-board`  | 🐝 qc-leader     | in progress | QC-team integration-test sub-issues `[T#-1…T#-3]` (§1 ⑦)                                                                              | bdd-integration                                                                   |
| ♻️ `mx-jobs`         | — none —         | in progress | Scheduled autopilot run issues — 🏛️ arch-reviewer's monthly sweep (§3.1)                                                             | all 5 Monxa repos · helm-charts SANDBOX (infra-v2) + PRD (monxa)                  |
| ♻️ `mx-prd-releases` | 🌙 prd-release   | planned     | Production release issues — 🌙 prd-release's SANDBOX→PRD promotions (§3.3)                                                            | helm-charts SANDBOX (infra-v2) · helm-charts PRD (monxa)                          |


Repository names are shortened from `github.com/the-wixo/monxa.<name>` (and
`the-wixo/infra-v2.helm-charts` for the SANDBOX charts). `mx-jobs` has no board **lead** —
it holds run issues filed by the scheduled autopilot in §3, which report by status rather
than being owned on a board.

---

## 5 · Skills architecture

### Layer model


| Layer               | Artifact                                                                                                                        | Reaches                                 | Contains                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| 1 — shared contract | `sdlc-flow-delivery-pipeline` skill                                                                                             | 🦊 🦉 🐺 🐝 🦅 at every task claim      | both flows, stage ownership, conventions, branch/environment strategy, trigger + status contract, escalation map |
| 2 — role procedure  | `sdlc-flow-po-orchestration` (🦊) · `spec-review-gate` (🦉) · `pr-review-gate` (🦅) · `sdlc-flow-squad-leader-playbook` (🐺 🐝) | the owning agent(s) only                | the HOW: workflows, rubrics, gate actions, loops, wake checklists                                                |
| 3 — squad specifics | squad `instructions` (leader briefing) — product-team, dev-team &amp; qc-team                                                   | the squad leader, with every squad task | members table, stage tables, squad loops + caps, verified mention directory (UUIDs)                              |
| 4 — agent identity  | each agent's `instructions`                                                                                                     | that agent, always                      | persona · scope · hard limits · skill pointers (~2k chars each)                                                  |


Layers 1–2 above are the **flow/role skills** (the `sdlc-flow` family + the gate
skills) — they encode *this pipeline*. Agents additionally load a small set of
**capability skills** (TDD, testing standards, git, CodeGraph, stack conventions) —
only ones carrying Monxa- or stack-specific content; generic best-practice text was
deliberately trimmed (2026-08). The two inventories below are generated from the
agents' `skill_names[]` and kept in lock-step with `manifest.json` — they are the
authoritative source, superseding any prose description of "who loads what".

### Skills per agent

*Exactly the `skill_names[]` on each `agents/<name>.json`. Count in parentheses.*


| Agent                  | Skills                                                                                                                                                                                 |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🦊 product-owner (8)   | `blocker-report` · `bug-report` · `codegraph` · `interview-me` · `multica-brainstorming` · `sdlc-flow-delivery-pipeline` · `sdlc-flow-po-orchestration` · `sdlc-spec-template`         |
| 🦉 spec-reviewer (6)   | `blocker-report` · `codegraph` · `sdlc-flow-delivery-pipeline` · `sdlc-flow-squad-member-protocol` · `sdlc-spec-template` · `spec-review-gate`                                         |
| 🐺 dev-leader (7)      | `blocker-report` · `codegraph` · `leader-gitops` · `sdlc-flow-delivery-pipeline` · `sdlc-flow-squad-leader-playbook` · `sdlc-gitflow` · `sdlc-impl-brief` |
| 🔨 dev-backend (8)     | `blocker-report` · `codegraph` · `dknet-ddd-conventions` · `dotnet10-efcore10-standards` · `sdlc-flow-squad-member-protocol` · `sdlc-gitflow` · `test-driven-development` · `testing-standards` |
| 🐳 release-manager (3) | `blocker-report` · `sdlc-flow-squad-member-protocol` · `sdlc-gitflow`                                                                                                  |
| 🦅 pr-reviewer (6)     | `blocker-report` · `codegraph` · `dknet-ddd-conventions` · `pr-review-gate` · `sdlc-flow-delivery-pipeline` · `sdlc-flow-squad-member-protocol`                                        |
| 🐝 qc-leader (8)       | `bdd-report` · `blocker-report` · `bug-report` · `codegraph` · `leader-gitops` · `sdlc-flow-delivery-pipeline` · `sdlc-flow-squad-leader-playbook` · `sdlc-impl-brief` |
| 🐜 qc-tester (4)       | `bdd-report` · `blocker-report` · `codegraph` · `sdlc-flow-squad-member-protocol`                                                                   |
| 🐞 qc-runner (4)       | `bdd-report` · `blocker-report` · `codegraph` · `sdlc-flow-squad-member-protocol` |
| 🔍 bdd-reviewer (5)    | `bdd-report` · `bdd-review-sweep` · `blocker-report` · `codegraph` · `testing-standards` |
| 🤝 Mika (0)            | — (chief-of-staff assistant; no workspace skills bound) |
| 🐙 devops (7)          | `blocker-report` · `codegraph` · `compose-delivery` · `helm-chart-delivery` · `sdlc-flow-delivery-pipeline` · `sdlc-flow-squad-member-protocol` · `sdlc-gitflow`                |
| 🐲 claude_ultra (4)    | `autopilot-spec` · `blocker-report` · `interview-me` · `multica-brainstorming`                                                                                         |
| 🐼 default (4)         | `autopilot-spec` · `blocker-report` · `interview-me` · `multica-brainstorming`                                                                                         |
| 🏛️ arch-reviewer (7)  | `architecture-review-sweep` · `blocker-report` · `bug-report` · `codegraph` · `dknet-ddd-conventions` · `dotnet10-efcore10-standards` · `sdlc-gitflow`                                 |
| 🧹 issue-janitor (1)   | `blocker-report`                                                                                                                                                       |
| 🌙 prd-release (3)     | `blocker-report` · `prd-release-runbook` · `sdlc-gitflow`                                                                                                              |


arch-reviewer, issue-janitor, prd-release and devops are **standalone / off-pipeline
agents** (see §3) — they run outside the feature/bug pipeline, some on a schedule, some on
direct ticket assignment. arch-reviewer carries a full review toolkit; issue-janitor keeps
its whole procedure in `instructions`; prd-release and devops lean on
`sdlc-gitflow` for their git work.

### Full skill catalog

*All 26 skills in the workspace, grouped by family. "Bound to" is the reverse index of
the Skills-per-agent table above; every skill is now bound to at least one agent.*

`*devops` now owns the 🐙 icon outright — its former co-holder, the dedicated git-custodian
agent, was retired when the squad leaders took over its git-flow duties (see `CHANGELOG.md`).*

**A · sdlc-flow pipeline** (workspace-specific — Layers 1–2)


| Skill                             | Governs                                                                                                                                  | Bound to                |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| `sdlc-flow-delivery-pipeline`     | shared two-flow contract: stage ownership, triggers, branch strategy, escalation                                                         | 🦊 🦉 🐺 🦅 🐝 🐙       |
| `sdlc-flow-po-orchestration`      | Workflows A (confidence gate) / B (spec + gate loop) / C (phases), delegation, follow-ups triage                                         | 🦊                      |
| `sdlc-flow-squad-leader-playbook` | leader machinery: wake checklist, decomposition, mention protocol, fix-loop, recovery loop, finalize                                     | 🐺 🐝                   |
| `sdlc-flow-squad-member-protocol` | member-side protocol: branch/build/verify/PR stage discipline, status/mention rules                                                      | 🦉 🔨 🧪 🦅 🐜 🐞 🐳 🐙 |
| `sdlc-impl-brief`                 | the dev sub-task contract: nine-section implementation brief leaders write into coding sub-tasks                                         | 🐺 🐝                   |
| `blocker-report`                  | the two fixed report shapes — completion (RESULT / EVIDENCE / LEFT OPEN) and blocker (`## BLOCKER` + `## OPTIONS`)                                                                         | all agents              |
| `bug-report`                      | the standard 3-section body (Scope (Git Repo, Module/Classes) / Root cause / Suggested owner) for every separately-filed bug/defect issue | 🦊 🐝 🏛️               |
| `sdlc-spec-template`              | the 7-section business-spec contract the `[S#]` gate scores against (§3a contract, §3b architecture impact)                              | 🦊 🦉                   |
| `spec-review-gate`                | spec rubric, verdicts, 5-round cap, handoff                                                                                              | 🦉                      |
| `pr-review-gate`                  | PR rubric, merge gate, 3-round cap, handoff, follow-ups filing                                                                           | 🦅                      |
| `bdd-report`                      | BDD test-report format on qc-team sub-issues                                                                                             | 🐝 🐜 🐞 🔍             |
| `prd-release-runbook`             | 🌙 prd-release's SANDBOX→PRD promotion runbook (drift table, release PR, BDD gate) — see §3.3                                            | 🌙                      |


**B · Multica platform**


| Skill                   | Governs                                                               | Bound to                   |
| ----------------------- | --------------------------------------------------------------------- | -------------------------- |
| `multica-brainstorming` | Multica-native requester dialogue — numbered questions with guesses, spec preview approved in writing | 🦊 🐲 🐼 |
| `autopilot-spec`        | Goal → Context → Steps structure for autopilot runbooks               | 🐲 🐼                      |


**C · Discovery, spec &amp; planning**


| Skill          | Governs                                  | Bound to |
| -------------- | ---------------------------------------- | -------- |
| `interview-me` | intent extraction — numbered questions, each with a guess | 🦊 🐲 🐼 |


**D · Implementation &amp; delivery**


| Skill                 | Governs                                          | Bound to |
| --------------------- | ------------------------------------------------ | -------- |
| `helm-chart-delivery` | helm chart authoring, values wiring, deploy prep | 🐙       |
| `compose-delivery`    | docker-compose file authoring, `docker compose config` validation, PR delivery | 🐙       |


**E · Test, review &amp; debugging**


| Skill                     | Governs                                                                | Bound to                       |
| ------------------------- | ---------------------------------------------------------------------- | ------------------------------ |
| `test-driven-development` | tests first, prove the code works                                      | 🧪                             |
| `testing-standards`       | unit + BDD test standards and the coverage bar                         | 🔨 🧪 🔍                       |
| `bdd-review-sweep`        | 🔍 bdd-reviewer's recurring BDD-suite quality sweep                    | 🔍                             |
| `codegraph`               | code-graph setup (`codegraph init`) + query method for research/review | 🦊 🦉 🐺 🔨 🧪 🦅 🐝 🐜 🐞 🏛️ 🐙 🔍 |


**F · Git &amp; branching**


| Skill           | Governs                                                                                                              | Bound to              |
| --------------- | -------------------------------------------------------------------------------------------------------------------- | --------------------- |
| `sdlc-gitflow`  | feature→dev→main branch/PR discipline: remote-only ops, explicit `--head/--base`, post-create verification, PR body shape | 🐺 🔨 🧪 🐳 🏛️ 🌙 🐙 |
| `leader-gitops` | the squad leaders' inline git-flow runbook — branch cut, the ONE cycle PR, conflict handling, worktree-lock recovery | 🐺 🐝                 |


**G · .NET architecture review** (arch-reviewer's autopilot toolkit — see §3)


| Skill                         | Governs                                                              | Bound to  |
| ----------------------------- | -------------------------------------------------------------------- | --------- |
| `architecture-review-sweep`   | recurring .NET review workflow: shard, rank by severity, dedup, file | 🏛️       |
| `dknet-ddd-conventions`       | DKNet DDD conventions (entities, aggregates, events, CQRS)           | 🏛️ 🔨 🦅 |
| `dotnet10-efcore10-standards` | verified .NET 10 / C# 14 / EF Core 10 review standards               | 🏛️ 🔨    |


**Coverage:** all **25** skills listed in `manifest.json` are bound to at least one agent and
every directory under `skills/` is in the manifest — no orphans in either direction. The
generic best-practice pack imported from `addyosmani/agent-skills` was trimmed in the
2026-08 simplification pass: only skills carrying Monxa- or stack-specific content remain;
generic engineering advice lives in the agents' own Engineering Standards sections.

### Maintenance rules

- **Flow change** → edit `sdlc-flow-delivery-pipeline` only.
- **One role's procedure** → edit that role's skill.
- **Squad membership/stages** → edit that squad's briefing.
- **Add/remove/rebind a skill on an agent** → edit that agent's `skill_names[]` **and** the
two tables above (Skills per agent + Full skill catalog "Bound to") in the same change,
and register any new skill in `manifest.json`. An unlisted skill is invisible to import.
- **Never re-inflate agent instructions** — identity and hard limits only.
- Skills are portable across workspaces (the `sdlc-flow` prefix): they resolve UUIDs at runtime; only squad briefings pin workspace-specific mention directories.
- Changes apply on each agent's next task claim — no restarts.

---

## 6 · Agent runtimes &amp; models

Runtime is derived from the model name: a model whose name starts with `claude` runs on the **claude** runtime. Every agent in this workspace is now on it — the last `opencode`/`openrouter` holdouts (`default`, `devops`, `issue-janitor`) were migrated 2026-09-10.

Model choice follows **subscription coverage** (flat-fee = no per-token cost): every agent
runs on **Claude Premium**. No agent bills per-token `openrouter/*`.

| Agent              | Model               | Thinking | Covered by     |
| ------------------ | ------------------- | -------- | -------------- |
| 🦊 product-owner   | claude-opus-5-5[1m] | high     | Claude Premium |
| 🦉 spec-reviewer   | claude-opus-5-5[1m] | high     | Claude Premium |
| 🐺 dev-leader      | claude-sonnet-5     | high     | Claude Premium |
| 🔨 dev-backend     | claude-opus-5-5     | high     | Claude Premium |
| 🐳 release-manager | claude-sonnet-5     | medium   | Claude Premium |
| 🦅 pr-reviewer     | claude-sonnet-5     | high     | Claude Premium |
| 🐝 qc-leader       | claude-sonnet-5     | high     | Claude Premium |
| 🐜 qc-tester       | claude-sonnet-5     | high     | Claude Premium |
| 🐞 qc-runner       | claude-sonnet-5     | medium   | Claude Premium |
| 🐙 devops          | claude-opus-5-5[1m] | high     | Claude Premium |
| 🐲 claude_ultra    | claude-opus-5-5     | xhigh    | Claude Premium |
| 🐼 default         | claude-sonnet-5     | high     | Claude Premium |
| 🏛️ arch-reviewer  | claude-opus-5-5     | max      | Claude Premium |
| 🧪 bdd-reviewer    | claude-opus-5-5     | max      | Claude Premium |
| 🐼 Mika            | claude-opus-5-5     | high     | Claude Premium |
| 🧹 issue-janitor   | claude-sonnet-5     | -        | Claude Premium |
| 🌙 prd-release     | claude-sonnet-5     | high     | Claude Premium |


arch-reviewer, issue-janitor, prd-release and devops are **standalone / off-pipeline agents** (§3), not pipeline-flow members.

Squad git-flow (branch cut, the ONE cycle PR) is no longer a separate agent run — dev-leader
and qc-leader execute it inline, per `leader-gitops`, at their own tier above. No extra model
call is spent per branch or PR.

### Token-budget rationale

Tier is assigned by **subscription coverage first, then cheapest tier that fits the role** —
Claude Premium for the roles where reasoning quality dominates, OpenCode Go for the squad
workhorses, the $0 free tier for off-pipeline utility runs:

- **Judgment &amp; orchestration** — 🦊 product-owner on Claude Opus 5.5, 1M-context tier
(`high`); reasoning-heavy, correctness dominates. 🦉 spec-reviewer gates specs on the same
tier at `high`; 🐺 dev-leader orchestrates on Claude Sonnet (`high`) — squad
triage/decompose/gate over diffs, not prose.
- **Implementation** (🔨 dev-backend, 🐜 qc-tester) — code/test writers. dev-backend on Claude
Opus 5.5 standard tier (`high`), owning tests and code together; qc-tester on Claude Sonnet at `high`.
- **Mechanical git/ops** (🐳 release-manager, 🐞 qc-runner) — Claude Sonnet at `medium`.
Kept on a capable model (not a light one) because a lighter model dropped the
end-of-turn sub-task status flip (`done`/`blocked`), stranding the pipeline; the flip is a
correctness-critical control step (release-manager's core job is two `gh` calls — open the
`dev`→`main` PR, merge it).
- **Review gates** (🦅 pr-reviewer, 🐝 qc-leader) — Claude Sonnet at `high`/`medium`; scoped
judgment over a diff.
- **Off-pipeline / utility** (🐼 default, 🧹 issue-janitor, 🌙 prd-release) — Claude Sonnet;
adequate for ad-hoc work, nightly hygiene, and release-note drafting. 🏛️ arch-reviewer and
🧪 bdd-reviewer stay on Claude Opus (`max`) — they reason over a whole codebase, where a
cheaper tier's quality ceiling would not fit.

Keep this table and the per-agent JSON `model`/`thinking_level` in lock-step (see
[`CLAUDE.md`](./CLAUDE.md)) — re-tiering an agent without updating both makes the budget
picture wrong.

---

## Glossary — plain-English terms

*Alphabetical. If a section above used a word you didn't know, it's probably here.*


| Term                      | What it means                                                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **agent**                 | An AI worker with one specific job and a nickname (see the cast in Part 1).                                                               |
| **argoCD**                | The tool that pushes approved code out to a running environment. "argoCD-deploy to SANDBOX" = make the new version live on the test site. |
| **backlog / todo / done** | The status of a ticket. `backlog` = queued but not started, `todo` = ready to start (this is what wakes an agent), `done` = finished.     |
| **barrier**               | An automatic checkpoint: when a step finishes, it "fires the barrier" that wakes whoever was waiting on it.                               |
| **handoff line**          | The one-line comment a child posts on its parent when the barrier stays silent (`blocked`, or `done` beside a `blocked` sibling).        |
| **BDD / Gherkin**         | A way of writing tests as plain-language scenarios ("Given… When… Then…") that non-programmers can read. Gherkin is the exact format.     |
| **branch**                | A separate copy of the code to work on safely without disturbing the main copy. See `feature`, `dev`, `main`.                             |
| **CI/CD**                 | Automation that builds, tests, and ships code without a human running the steps by hand.                                                  |
| **coverage**              | How much of the changed code is exercised by tests, as a percentage. Our bar is **&gt;80%** of the classes a change touches.              |
| **dev (branch)**          | The shared **integration** copy of the code where all finished work lands first.                                                          |
| **gate**                  | A quality checkpoint that must pass before work moves on (a plan score, a code review, a test run).                                       |
| **helm chart**            | The configuration that describes how an app is deployed to a server environment.                                                          |
| **main (branch)**         | The **release** copy of the code. Merging into `main` triggers the build that goes to SANDBOX.                                            |
| **mention**               | Tagging an agent in a comment. Tagging an **agent** starts it working; tagging a **person** just notifies them.                           |
| **phase / stage**         | A numbered unit of work, e.g. `[P#-1]` (a feature phase) or `[D#-3]` (a dev step). The `#` is the ticket number.                          |
| **PR (pull request)**     | A proposal to merge one branch's changes into another, reviewed before it's accepted.                                                     |
| **PRD / production**      | The real, customer-facing environment. The last stop, handled by 🌙 prd-release.                                                          |
| **SANDBOX**               | The internal **test environment** where a change goes live for the team to try before production.                                         |
| **spec**                  | The written plan for a request — 7 sections describing what to build and why, scored before any building starts.                         |
| **squad / team**          | A group of agents with a leader that delivers one kind of work (product, dev, or QC).                                                     |
| **ticket / issue**        | A single unit of tracked work on a board (a request, a bug, a sub-task).                                                                  |


## Change log &amp; review notes

Moved to [`CHANGELOG.md`](./CHANGELOG.md) — dated notes on definition changes, live incidents, and review findings.