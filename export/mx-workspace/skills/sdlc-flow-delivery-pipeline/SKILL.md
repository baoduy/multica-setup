# SDLC Delivery Pipeline — Shared Contract

Single source of truth for staged delivery flow. Every pipeline agent loads this skill. Role PROCEDURE lives in role skills — `sdlc-flow-po-orchestration` (product-owner), `sdlc-flow-squad-leader-playbook` (squad leaders), `spec-review-gate` (spec-reviewer), `pr-review-gate` (pr-reviewer) — and squad-specific detail lives in each squad's briefing. If a detail here ever conflicts with a role skill, role skill wins for its owner; flag mismatch to workspace owner.

## Actors

- **product-team** (squad; leader **product-owner**; members spec-reviewer, release-manager, devops, pr-reviewer, and requester as a human member) — owns main ticket end to end: requirement → spec → gated delivery → SANDBOX verification. Read-only on code.
- **product-owner** — product-team leader: research, spec, architecture, all delegation and phase promotion.
- **spec-reviewer** — automated spec review gate (Workflow B only).
- **release-manager** — owns `dev`→`main` release PR and its merge (SANDBOX line). Only agent permitted to target/merge `main` **in application repos**. CI builds image on merge; human runs argoCD.
- **dev-team** (squad; leader **dev-leader**; members dev-backend, pr-reviewer; leader runs cycle git-flow itself per `leader-gitops`) — implementation delivery. **No devops member.**
- **qc-team** (squad; leader **qc-leader**; members qc-tester, qc-runner, pr-reviewer; leader runs cycle git-flow itself per `leader-gitops`) — SANDBOX BDD integration testing. **No devops member.**
- **pr-reviewer** — automated PR review + merge gate for both squads' PRs **and for devops' standalone PRs**. It merges app-repo PRs into `dev`; it NEVER merges a helm PR, because merging a chart IS deploy.
- **devops** — CI/CD pipelines, build/release automation, and helm chart configuration. Never a member of dev-team or qc-team and never a stage in their cycles. Reached two ways: requester assigns it directly (Workflow D), or product-team delegates it a `[P<num>-1b]` phase when a feature needs a pipeline/chart change.
- **Humans**: requester (ticket creator) and workspace owner (escalation valve, production releases). Escalation targets the *resolved owner* — see "Who the human owner is" under **Human touch points & escalation map** (`Owner` property first, then root member-creator, then workspace owner).

Portability rule: never trust a hardcoded UUID from documentation — resolve IDs at runtime (`multica agent list` / `multica squad list` / `multica project list` / `multica workspace member list`, all `--output json`). Squad briefings carry a verified per-squad mention directory.

## Two different things are called "BDD" — never conflate them

| | Owner & stage | Where it lives | Waivable |
|---|---|---|---|
| **BDD unit tests** (in-repo) | dev-team, inside `[P#-1]` | application repo's own BDD test project (Reqnroll/SpecFlow for .NET, Cucumber/playwright-bdd for React) — **not every repo has one** | **Never.** It is part of code change's definition of done (`testing-standards`). |
| **BDD integration tests** (SANDBOX) | qc-team, in `[P#-3]` | `monxa.bdd-integration`, executed against a deployed SANDBOX | Yes — product-owner sets `bdd_required` by judgment (requester overrides); a money/identity-path waiver is requester-only. |

Two orthogonal metadata keys on main ticket decide which phases exist, both set by product-owner's judgment before phase creation (see `sdlc-flow-po-orchestration`): **`ship_required`** — does change reach an environment at all (`false` = test-only/docs/pure-refactor → terminal at `[P#-1]`, rides next release) — and **`bdd_required`** — does shipped change need SANDBOX suite. `ship_required=false` forces `bdd_required=false`.

**A narrowed scope never relieves dev-team of in-repo BDD coverage of change.** Whichever key is `false`, say so explicitly in `[P#-1]`: *"The SANDBOX suite [and the dev→main release] is dropped this cycle (basis: …); the in-repo BDD/unit coverage in your PR is the only automated coverage, so the acceptance criteria stand as written."*

Where application repo has no BDD test project, dev-team covers behaviour in repo's existing unit-test suite and states that in report. Nobody adds a BDD harness to a repo as a side quest of a delivery ticket.

## Feature flow (Workflow B)

```
👤 files main ticket (mx-main, assignee product-owner, todo)
 → 🦊 intake (labels main+feature) → research (CodeGraph, file:line evidence)
 → 🦊 clarify ⟲ with 👤 until ZERO open questions (never ask what the code answers)
       incl. delivery scope: 🦊 judges ship_required + bdd_required from requirement
       (test-only/docs → ship_required=false; no SANDBOX surface / repo note → bdd_required=false),
       asks only when unsure; 👤's explicit word overrides → metadata ship_required/bdd_required
 → 🦊 writes 7-section BUSINESS spec into main ticket description (sized to
       requirement; no code blocks; no file:line anywhere — code-level detail lives in the impl-brief)
       🦊 states problem + required behaviour; 🐺 dev-leader designs and decomposes
 → 🦊 creates [S#] Spec review sub-task (mx-main, spec-reviewer, todo)
 → 🦉 gate: APPROVED (≥9.0, no blockers) | REVIEW REQUESTED (8.0–8.9 or a reviewer trigger →
       👤 requester holds [S#] sub-task; their done flip releases delegation)
       | REWORK ⟲ (<8.0 or a blocker, max 5 rounds) | round >5 → 👤 requester manual review
 → 🦊 Workflow C: [P#-1] Implementation (dev-team, todo — always incl. in-repo BDD/unit coverage)
                   · [P#-2a] Release to SANDBOX (dev→main) (release-manager, backlog)  ── only if ship_required ≠ false
                   · [P#-2b] SANDBOX deploy (argoCD) (👤 requester, backlog)   ─┐ BOTH only if
                   · [P#-3] BDD integration tests (qc-team, backlog)           ─┘ bdd_required ≠ false
                   — plus FYI to 👤 with score
 → 🐺 dev cycle (mx-code): Branch → Build (TDD: tests first, then code, ≥80% touched classes) → PR → 🦅 review gate (merges into dev)
       REWORK from 🦅 re-enters at Build; the fix report carries suite + coverage evidence before gate is re-armed
       (docs/config-only requests take light route — Branch → Update → PR → 🦅 review gate,
        no coverage bar; routing rules in dev-team briefing)
 → ship_required=false → [P#-1] IS TERMINAL: 🦊 verifies merged dev PR + score, flips main ticket
                         done + final summary ("Not shipped this cycle: <reason>; in-repo coverage:
                         <tests>; rides next release"). No [P#-2a]/[P#-2b]/[P#-3] exist to promote
 → 🦊 verifies merged PR + score → promotes [P#-2a] → 🐳 release-manager PRs dev→main + merges (CI builds image)
 → bdd_required=false → [P#-2a] IS TERMINAL: 🦊 flips main ticket done + final summary
                         (spec → merged PR + score → released to main
                          → "BDD integration tests waived: <reason>; in-repo coverage: <tests>")
                         No [P#-2b] and no [P#-3] exist to promote — SANDBOX deploy is 👤's call, when 👤 wants it
 → otherwise 🦊 promotes [P#-2b] → 👤 argoCD-deploys main→SANDBOX, flips done
 → 🦊 refreshes [P#-3] with PR/branch/deploy facts → promotes it → 🐝 qc cycle (mx-qc-board):
       development cycle (Branch → Scenarios → Verify → PR → 🦅 gate) or run-only (Run, no branch/PR)
       Verify = qc-runner reviews scenarios against OpenAPI endpoint matrix AND
       executes IMPACTED SCOPE against SANDBOX (new/changed scenarios + regression
       neighbourhood of touched endpoints — not full suite, which belongs to
       PRD release path); REWORK from 🦅 re-runs Verify before gate
 → 🦊 verifies QC report + merged QC PR → main ticket done + final summary (no mentions)
```

## Bug flow (Workflow A)

```
intake: 👤 files bug ticket → product-owner (mx-main, todo, labels main+bug)
        OR qc-team auto-files ONE consolidated, deduped defect ticket → product-owner (todo)
 → 🦊 research → clarify ⟲ → root-cause report comment (evidence, repro, fix direction,
       targeting layer all callers route through) + a calibrated CONFIDENCE (0–100%)
       that this is a genuine platform defect with identified root cause
 → gate: pure question, no change wanted            → END (report is deliverable)
         confidence ≥ 90% (confirmed bug)           → AUTO-DELEGATE: Workflow C immediately,
                                                       FYI to 👤 (member mention: root cause,
                                                       confidence, "fix delegated — reply to halt")
         confidence < 90% (possibly by-design, config, user error)
                                                     → 👤 requester reviews and explicitly
                                                       confirms before any delegation
 → Workflow C (root-cause report = implementation basis; spec only if 👤 asks — then 🦉 gates it)
       [P#-3] is typically a run-only re-verification cycle
       delivery scope: 🦊 judges ship_required/bdd_required (a test-only fix → ship_required=false);
       when unsure auto-delegate does NOT wait — safe defaults (both true), full flow created,
       question rides FYI comment, and a later narrowing reply cancels now-unauthorized
       stages ("no BDD" → [P#-2b]+[P#-3]; "no ship" → also [P#-2a]) and never touches [P#-1]
```


## CI/CD & infra flow (Workflow D)

Pipelines, build/release automation, and helm charts are `devops` work. They never enter dev-team or qc-team flow and never open a spec-review gate. They DO open a PR-review gate whenever `devops` produces a standalone PR — see "PR-review gate for devops PRs" below.

**Two doors, and only one of them is product-team's:**

| Door | When | Owner |
|---|---|---|
| **direct** | requester files a pipeline/helm ticket straight to `devops` | `devops`, end to end. product-team stays out entirely — never adopts, re-parents, or wraps such a ticket. |
| **delegated** | a FEATURE needs a pipeline or chart change, surfaced by spec or by a squad | product-team creates `[P<num>-1b] CI/CD change` (devops, `todo`) + `[P<num>-1c] Review CI/CD PR` (pr-reviewer, `backlog`) as phases of that feature |

A squad that discovers pipeline/helm work mid-cycle never creates sub-task itself: it reports on its phase ticket, posts its handoff line on the main ticket, and product-team routes it.

### PR-review gate for devops PRs

| devops landed it as | pr-reviewer's action on APPROVED |
|---|---|
| commit on a named feature branch (app repo) | none — it is reviewed inside squad's cycle PR |
| PR → `dev` (app repo, standalone) | score, vote, **and merge**, exactly as for a squad PR |
| PR → `main` (either helm repo) | score and vote, **never merge** — merging a chart PR IS deploy, so a human merges it via `[P<num>-2] Merge helm PR` |

```
👤 asks for pipeline / helm work
 ├─ direct door: 👤 assigns 🔧 devops straight away (supported, not an error — 🦊 stays out)
 └─ via 🦊: intake (labels main+cicd) → classify Workflow D
       ├─ D1 "analyse and tell me"  → 🦊 report (file:line) + STOP. No sub-tasks, no delegation
       │                              at any confidence. 👤 decides what happens next.
       └─ D2 "make the change"      → 🦊 creates [P#-1] CI/CD change (devops, todo) only
 → 🔧 devops does work, landing it by REPO CLASS:
       app repo   → task names a feature branch? commit to THAT branch (squad leader owns PR).
                    otherwise → chore/<issue> branch, open PR to `dev`, report link. Never
                    commits directly to `dev` or `main`.
       helm repo  → branch chore/<issue>, push, open PR to `main`, STOP. Never merges.
 → 🦊 verifies (commit on feature branch | OPEN PR based on dev | OPEN PR based on main)
 → helm only: 🦊 promotes [P#-2] Merge helm PR (deploy) → 👤 reviews and merges = deploy decision
 → 🦊 flips main ticket done + plain summary
```

No `[P#-2a]` release, no `[P#-2b]` argoCD ticket, no `[P#-3]` BDD phase in this flow.

## Stage ownership

| Ticket | Project | Owner | Created | Starts when |
|---|---|---|---|---|---|
| main ticket | mx-main | product-team → product-owner (whole life) | requester / qc-team | assignment at `todo` |
| `[S#]` spec review | mx-main | spec-reviewer | product-owner | assignment at `todo`; re-armed `blocked`→`in_progress --no-start` + mention |
| `[P#-1]` implementation | mx-main | dev-team → dev-leader | product-owner | created `todo` |
| `[P#-1b]` CI/CD change (delegated) | mx-main | devops | product-owner — only when feature needs one | created `todo` |
| `[P#-1c]` review CI/CD PR | mx-main | pr-reviewer | product-owner — only alongside a `[P#-1b]` standalone PR | promoted once PR URL is posted |
| `[P#-2a]` release dev→main | mx-main | release-manager | product-owner — **only when `ship_required` ≠ `false`, and only on a ticket with no parent** | promoted after P#-1 verified |
| `[P#-2b]` SANDBOX deploy (argoCD) | mx-main | 👤 requester | product-owner — **only when `bdd_required` ≠ `false`** | promoted after P#-2a done |
| `[P#-3]` integration tests | mx-main | qc-team → qc-leader | product-owner — **only when `bdd_required` ≠ `false`** | promoted after P#-2b done |
| `[D#-n]` dev sub-tasks (Branch → Build → PR → Review) | mx-code | dev-team members | dev-leader | stage promotion |
| `[T#-n]` qc sub-issues (Branch → Scenarios → Verify → PR → Review) | mx-qc-board | qc-team members | qc-leader | stage promotion |
| `[P#-1]` CI/CD change (Workflow D) | mx-main | devops | product-owner, or requester directly | created `todo` |
| `[P#-2]` merge helm PR (Workflow D) | mx-main | 👤 requester | product-owner | promoted after helm PR is verified open |

**Delivery-scope narrowing (`ship_required` / `bdd_required`).** Product-owner sets both by judgment before phase creation and records them as metadata; requester's explicit word overrides either. Absent/ambiguous/unsure = both required. A money/identity-path SANDBOX waiver is requester-only. Full decision procedure in `sdlc-flow-po-orchestration`.

- `bdd_required=false` drops SANDBOX-verification tail: **`[P#-2b]` and `[P#-3]` are never created**, and `[P#-2a] done` becomes terminal. Nothing to serve a deploy that no suite will test; requester deploys `main` to SANDBOX on their own schedule.
- `ship_required=false` also drops release: **`[P#-2a]` is never created either**, and `[P#-1] done` (merged into `dev`) becomes terminal. Change rides next `dev`→`main` release. Used for work a running service never observes — test-only, docs, pure refactor.
- **A ticket with a parent drops the whole tail regardless of both keys**: a sub-issue product-owner runs is terminal at `[P#-1]`, because the parent's owner ships every child in ONE `dev`→`main` release, one SANDBOX deploy and one BDD pass. A per-child release would ship siblings still mid-cycle. The parent's own cycle creates `[P#-2a]`/`[P#-2b]`/`[P#-3]` over the finished children.

Neither key drops anything else. `[P#-1]`, its in-repo BDD/unit coverage, acceptance criteria, and pr-reviewer merge gate always run at full strength. A narrowed scope reduces coverage of deployed environment, never coverage of fix.

## Conventions

- **Projects**: main + phase tickets in `mx-main`; dev sub-tasks in `mx-code`; qc sub-issues in `mx-qc-board`.
- **Titles**: ROOT main tickets carry one type prefix — `[Feature]` · `[Enhance]` · `[Bug]` · `[Question]` · `[CICD]` — matching the type label, set by product-owner at intake (Policy 05 §7a). Children carry `[S<num>]` / `[P<num>-n]` / `[D<num>-n]` / `[T<num>-n]` where `<num>` is ROOT main ticket's key NUMBER and `n` stage — never a type prefix, and the rename never touches that keying.
- **Labels**: main tickets ONLY (`main` + `feature`/`bug`/`question`/`cicd` + one `monxa.<service>` domain label per service change touches — best-effort, so label count shows how many services ticket involves). Never on children. product-owner seeds domain labels on intake; a squad leader adds any service it missed to ROOT main ticket (not to its sub-tasks) once implementation reveals it.
- **One PR per squad cycle**, head = feature branch, base = `dev`. PR titles/bodies must NEVER contain `Closes`/`Fixes`/`Resolves` next to an issue key — close intent auto-completes issue and kills remaining phases.
- Every sub-task is parented to its cycle parent directly — never nested under another sub-task.

## Branch & environment strategy

- **`main` = SANDBOX.** Merging into `main` triggers CI, which builds image and handles production tagging automatically downstream; a human then deploys `main` to SANDBOX via argoCD. ONLY agent that targets or merges `main` is release-manager, via a single `dev`→`main` release PR authorized by product-owner (`[P#-2a]`).
- **`dev` = INTEGRATION.** Every feature branch is created from latest `dev`; every squad/feature PR targets `dev`. If `dev` does not exist, squad leader creates it from `main` first (per `leader-gitops`).
- A squad/feature PR based on `main` is a defect: fix base to `dev`. Only `[P#-2a]` release PR (release-manager) legitimately uses base `main`, head `dev`.

### Helm chart repos are `main`-based — `dev` rule does NOT apply

Two chart repos do not follow app-repo branch model, and treating them as if they did either does nothing or deploys to production by accident:

| Repo | Branches that exist | Reality |
|---|---|---|
| `infra-v2.helm-charts` (SANDBOX) | `main`, `release/sandbox` | **has no `dev` branch at all** |
| `monxa.helm-charts` (PRD) | `dev`, `main`, `release/prd-*` | `dev` exists but **nothing promotes it to `main`** — `prd-release` cuts release branches from `origin/main`, so a commit on `dev` never ships |

Therefore, in either chart repo: never commit to `dev` (inert), and never commit or merge to `main` (that IS deploy). `devops` branches `chore/<issue-key>` from `origin/main`, opens a PR to `main`, and stops; a human merges. Procedure detail lives in `helm-chart-delivery` skill. Merging `monxa.helm-charts:main` publishes chart and Argo CD `mx-apps` auto-syncs it to **production** with prune and selfHeal on — there is no human step after that merge.

**Scope of `main` monopoly:** release-manager is only agent that may target or merge `main` **in application repos** (SANDBOX line). In two helm repos, `devops` may OPEN a PR against `main` — it may never merge one — and `prd-release` owns image-tag promotion PRs there. Image-tag promotion stays `prd-release`'s job, never `devops`'s.

## Triggers & status discipline (summary — full protocol in leader playbook)

- A run is triggered by: assignment at `todo`, promotion `backlog`→`todo`, a `done` or `cancelled` that closes a stage (the platform's sub-issue rule wakes the parent's assignee), an agent/squad mention link (real UUID required), and an agent's plain comment on a squad-assigned ticket or any sub-task under one (it wakes that squad's leader: the handoff line, workspace context — the leader's wake guard ends a run this double-fires, Policy 05 statement 5a). **Mentions are not deduped** — every mention enqueues its own run even when the target is already `queued` or `running`, and a stage barrier re-fires on EVERY re-entry into `done`. Three consequences: post ONE mention comment per turn (not two); every `mention://agent/<uuid>` link in a comment or description is a wake — even inside backticks or quoted instructions — so write instructions about mentioning someone in prose and never paste the link; and nobody flips their OWN sub-task out of `done` — only the leader does, to `in_progress` (`multica issue status <id> in_progress --no-start`), as step one of re-triggering fix work on a `done` or `blocked` sub-task, mention posted after; the barrier (or handoff line) that follows its return to `done` is a report to verify, not a new stage.
- **No member-to-member traffic.** A member writes only on its own ticket (comments, status, properties) plus its handoff line on the parent. It never comments on, mentions, or changes another member's ticket. Anything meant for another member (review findings, a fix request, a question) is a comment on the member's OWN ticket, and its handoff line wakes the leader, who routes it. Only the leader writes on tickets it does not own.
- **`Retrigger on done`** (text custom property, one issue key or several comma-separated: `MXW-1703,MXW-1704`) marks a sub-task whose completion must re-trigger one or more `blocked` issues. The leader sets it on every sub-task it re-triggers for fix work (a re-armed Build/Scenarios, or the Fix sub-task it files) — `multica issue property set <id> --name "Retrigger on done" --value <blocked-key>[,<blocked-key>…]`, appending to a value already set, never overwriting — because a `done` at or above a blocked stage fires no barrier and the leader would otherwise have no record of which gates to re-arm. Leader on every wake: each `done` child carrying it → for every key it names, once every child naming that key is `done`, flip that issue `in_progress --no-start` and post ONE comment there with its assignee's mention pointing at the fix report; then set the property to the keys still waiting, or `multica issue property unset <id> --name "Retrigger on done"` when none is left. Members never set or clear it.
- Agent/squad mention = triggers a run; a MEMBER (human) mention renders a link only — server delivers nothing for it. To make a human ACT, put a ticket in their queue: assign (or reassign) relevant ticket to them at `todo`. Comments that need an agent to act MUST carry that agent's mention link (MXW-454) — except a handoff line on a squad-assigned parent, which wakes its leader without one; never agent-mention in FYI/ack comments.
- Completion = `done` (fires stage barrier). `blocked` = needs help, and a `done` beside a `blocked` sibling fires nothing: both end with the child's handoff line on its parent (workspace context). `in_review` is leader-only for ROOT parents awaiting a human; on a phase ticket it deadlocks pipeline — use `done`.
- **Barrier poisoning.** A stage's done-barrier fires only when EVERY sub-task at that stage **and every lower stage** is terminal (`done`/`cancelled`). One sibling sitting `blocked` (a gate mid-REWORK) poisons the barrier for its own stage AND for every stage above it, so NO `done` at or above that stage wakes anyone: that completion ends with the member's handoff line.
- **One wake per handoff — never neither.** Every routing move (delegation, a `blocked`/`done`→`in_progress --no-start` re-arm, phase promotion, an answer or decision another agent must act on) fires exactly ONE wake for the next actor: a status transition that enqueues a run (assignment/promotion to `todo`, a `done` that trips a barrier), a handoff line on a squad-assigned parent, OR an agent mention. A re-arm's status flip enqueues NOTHING server-side (MXW-1426) and a plain comment wakes nobody unless it lands on a squad-assigned ticket (MXW-454) — when the transition wakes nobody, the mention is the ONLY wake; omit it and the ticket sits parked with nobody woken.
- **End-of-turn actuation check — LAST thing every run.** Before ending a turn, re-scan the tickets you touched: any decision, re-arm, or promotion this turn whose executor was NOT woken by a status transition or an agent mention → fire the wake now. A turn that changed no status and enqueued no run, on work that is not finished, has stalled the pipeline.

## Human touch points & escalation map

**Who the human owner is — resolve at runtime, NEVER hardcode a name or UUID.** In order: (1) the ticket's own `Owner` custom property, else the nearest ancestor's `Owner` (`multica issue property list <id> --output json`, walking `parent_issue_id` toward the root); (2) else the ROOT main ticket's `creator_id` when its `creator_type` is `member` (`multica issue get <root-id> --output json`); (3) else the workspace owner (`multica workspace member list --output json`, role `owner`) as final fallback. "Escalate to owner" / "resolved owner" everywhere below means this `Owner`-property-first resolution.

**Set `Owner` on every issue you create.** After creating an issue, set its `Owner` to the owner resolved from its parent: `multica issue property set <new-id> --name Owner --value "<member-name-or-id>"`. An agent filing a *root* ticket sets `Owner` to the human the work is for. This propagates ownership down the tree, so every descendant resolves the human in one lookup instead of falling through to the workspace owner — the failure mode that made agents treat the workspace owner as everyone's owner.

**Delivery is by ASSIGNMENT, never by mention.** A member mention renders a link and delivers nothing server-side, so an escalation that only member-mentions a human wakes nobody. Hand human a ticket instead: reassign ticket that needs them — gate's own review sub-task (spec-reviewer and pr-reviewer already hand off this way), or stuck child — to their member UUID at `todo` (`multica issue update <id> --assignee-id <member-uuid> --status todo`), with `## BLOCKER` comment on that ticket. Comments on requester's own MAIN ticket (clarifications, FYIs) are one exception — requester watches ticket they filed. Never an agent mention in an escalation to a human, and never take a ticket back while a human holds it.

| Gate | Cap | Then |
|---|---|---|
| Business clarifications | — | always requester (irreducible) |
| Spec review (🦉) | 5 rework rounds | review sub-task → resolved owner |
| Bug confidence (🦊) | < 90% confidence | requester confirms before delegation |
| PR review (🦅) | per `pr-review-gate` (3 rework rounds / deferred / merge failed) | review sub-task → resolved owner |
| Squad fix attempts | 2 failed attempts on same root cause | phase-ticket cycle → product-owner mentioned on squad's OWN phase ticket; root-ticket cycle → resolved owner |
| Anything outside squad control | — | same as above — a product decision, missing credentials, or a broken environment is never worth a second loop |
| SANDBOX deploy (argoCD) | — | requester runs `[P#-2b]`; dev→main release + build is automated (release-manager + CI) |
| Production tagging | — | automatic in CI/CD downstream, outside this flow |
| Helm chart merge | — | requester reviews and merges PR `devops` opened; merge IS deploy. pr-reviewer may score it, never merge it |
| Review leftovers | — | in-scope: the score decides — below 8.5 takes a rework round, at 8.5+ it merges with the PR named under `Merged with:` (no polish round, Policy 04 statement 7), no ticket either way. Out-of-scope: dropped, unless a defect/security finding with a named reproduction ⇒ the squad leader files ONE ordinary defect ticket. `Review follow-ups:` tickets retired; never decomposed into phases |

**Escalation is an action, not a status.** A squad that escalates still owns its cycle: it posts ONE comment naming what was tried, what failed, decision needed, and what stays blocked — in a standalone `## BLOCKER` section per `blocker-report` skill — and delivers it (agent mention for an agent hop; ticket reassignment at `todo` for a human hop), then parks blocked child. Ending a turn with a stuck child and no comment dispatched is a flow defect.