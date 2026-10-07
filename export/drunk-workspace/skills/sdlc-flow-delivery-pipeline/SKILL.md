# SDLC Delivery Pipeline — Shared Contract

The one-page contract every pipeline agent shares: actors, flows, stage ownership, branch strategy, escalation caps. Platform-wide constants (statuses, wakes, titles, `Owner`, git rules) are in the Workspace Context you already carry and are not repeated here. Role procedure lives in role skills — `sdlc-flow-po-orchestration` (product-owner), `sdlc-flow-squad-leader-playbook` (dev-leader), `spec-review-gate`, `pr-review-gate`; if this file and a role skill disagree, the role skill wins for its owner and the mismatch is reported to the workspace owner.

## Constants

The numbers the whole factory quotes. Change one here and it changes everywhere it is written out — grep the bundle before calling it done.

| Constant | Value | Owned by |
|---|---|---|
| spec gate approve bar | **8.5** (zero `blocker` findings) | Policy 04 §6 · `spec-review-gate` |
| PR gate approve bar | **8.5** (zero `blocking` findings) — a passing PR always merges into `dev`, never waits for a human; the one exception is a service design PR, which merges only on the owner's reply A (Workflow F) | Policy 04 §5 · `pr-review-gate/references/scoring-rubric.md` |
| deduction math, both gates | start 10 · blocker/blocking −4 · major/important −2 · minor/nit −0.5 (max −1.5) · floor 1 · caps after the weighted sum | `scoring-rubric.md` (the full cap table lives there) |
| coverage bar | **≥80%** per class/module the cycle touched, on the feature branch only; UI presentation files (§1a) and coverage-excluded wiring (§1e) exempt | Policy 02 §6, §1a, §1e |
| rework rounds | spec **5**, PR **3** (no polish round: a passing PR merges with its leftovers; then the owner's options, and only the owner's option B adds a round) | Policy 04 §6, §11, §11b |
| CI wait before merging past a running check | **30 min** | Policy 04 §5 · `pr-review-gate` |
| bug auto-delegate | confidence **≥90%**, else the requester confirms | Policy 07 §3 |
| squad fix attempts | **2** on one root cause, then escalate | Policy 05 §9 |
| sweep findings | **≤10** new issues per repo per run | Policy 04 §19 |
| run-medic wakes | **3** per issue, then its human owner | Policy 09, `run-medic` charter |
| brief size | 6–8 KB, split into parallel surfaces over 10 KB; leader plan comment under 2 KB | `sdlc-impl-brief`, leader playbook |
| parallel Builds | at most **3** at one stage, disjoint §3 files, shared §5 stubs from the Acceptance-tests stage | Policy 02 §1c |

## Actors

- **product-owner** — leader of product-team. Research, spec, orchestration of the ticket it is assigned. Read-only on code. A root ticket (no parent) it owns through release; a sub-issue (has a parent) it owns through development only — the parent's owner releases all its children together.
- **spec-reviewer** — automated spec gate (Workflow B). Approve bar 8.5, max 5 rework rounds.
- **dev-team** — squad led by **dev-leader**; members dev-backend (tests and code, acceptance-test-first; in-code API comments and a breaking change's `Breaking` changelog entry ship in Build), pr-reviewer (PR gate, merges into `dev`). The squad's delivery ends at the merge into `dev`: it never stages a release or opens a `dev`→`main` PR. The leader cuts the one feature branch and opens the one PR itself (`leader-gitops`). A cycle writes no docs pages; the leader's final report carries a `Docs impact:` line naming the pages the change made stale, and the repo's runtime architecture diagram when a component, external dependency or trust boundary changed.
- **pr-reviewer** — automated PR gate for every `dev`-bound PR (dev-team's cycle PR and the standalone PRs of devops, docs-writer and service-architect). Approve bar 8.5 — every passing PR merges, labelled `release-review` when a trigger applies; max 3 rework rounds, then the owner chooses.
- **release-manager** — opens and merges the single `dev`→`main` release PR, always as product-owner's `[P<num>-2]` — on a spec cycle, a bundle root, or a root dev-team handed back after its merge into `dev`. Not a dev-team member. A critical release (a `(MINOR)` commit or a `release-review` PR) waits for the owner's reply A. CI publishes the package on merge.
- **devops** — CI/CD pipelines, package-publish automation, docker-compose files, Helm charts (any `Chart.yaml`). Lands as `chore/<issue-key>` PR to `dev`, gated by pr-reviewer. Never enters the squad flow, never gets a spec gate.
- **docs-writer** — library and API feature docs with `archify` diagrams, written only when a human asks. Lands as `docs/<issue-key>` PR to `dev`, gated by pr-reviewer. Never enters the squad flow, never gets a spec gate.
- **service-architect** — designs a new service before its first code: `docs/architect/` in the new repo, with `archify` diagrams, per `service-design-template`. Delegated by product-owner only. Lands as `design/<issue-key>` PR to `dev`, scored by pr-reviewer and merged only on the owner's reply A. The merged design binds every later spec, impl-brief and PR in that repo.
- **Humans** — the requester (root creator) and the resolved owner (`Owner` property). Business clarifications and escalations only.

## Workflows

| Request | Workflow | Shape |
|---|---|---|
| question or defect to root-cause | **A** | research → root-cause report + confidence → ≥90% (or requester confirmed): the ROOT is reassigned to dev-team, which runs the cycle up to the merge into `dev`, then hands the root back to product-owner for ONE `[P<num>-2]` release (or finalizes it `in_review` with `no republish: <reason>`); <90% requester confirms first; pure question ends at the report |
| feature or enhancement to a library repo | **B → C** | clarify to zero open questions → business spec in the root description → `[S<num>]` gate → C |
| delivery of an approved spec | **C** | `[P<num>-1] Implementation` (dev-team, `todo`, stage 1; description pins `Spec revision: <n>`, frozen for the cycle) → `[P<num>-2] Release` (release-manager, `backlog`, stage 2; root tickets only) → ticket `done`. On a sub-issue the cycle ends at the verified `[P<num>-1]` — no release phase |
| CI/CD, build/publish automation, or a Helm chart change | **D** | D1 analysis-only ends at the report; D2 `[P<num>-1] CI/CD change` (devops, stage 1) → `[P<num>-1c] Review CI/CD PR` (pr-reviewer, stage 2) → root `done`. No spec gate, no release phase |
| docs a human asked for | **E** | `[P<num>-1] Docs` (docs-writer, stage 1) → `[P<num>-1c] Review docs PR` (pr-reviewer, stage 2) → root `done`. No spec gate, no release phase. A docs ticket may also be assigned to docs-writer directly, bypassing product-owner |
| a new service, or a change to an approved service design | **F** | clarify repo + service name, purpose, users, scope, neighbours → requester creates the empty repo with `dev` → `[P<num>-1] Design` (service-architect, stage 1) → `[P<num>-1c] Review design PR` (pr-reviewer, stage 2; a pass goes to the owner, merged on reply A) → root `done`. No spec gate, no release phase, delegated door only. Then the service is built through ordinary B tickets |

All traffic inside a squad is routed by its leader: members write only on their own sub-task and mention only the leader; a review REWORK travels pr-reviewer → dev-leader → implementer → dev-leader → pr-reviewer, never member to member; on a `[P<num>-1c]` it travels pr-reviewer → product-owner → devops, docs-writer or service-architect → product-owner → pr-reviewer, and the owner's reply on a design PR travels owner → product-owner → pr-reviewer (A) or service-architect (B). Inside dev-team a cycle is `[D<num>-1] Acceptance tests` → leader's inline AT approval (pins `at_sha`) → `[D<num>-2] Build` (one per independent surface, in parallel, at most 3 — Policy 02 statement 1c) → leader opens the PR → `[D<num>-3] Review`, the last stage — no Release stage; a root that republishes goes back to product-owner after the merge into `dev`. A confirmed bug fix is a single `[D<num>-1] Build` in `Mode: bug-build` (reproduction pushed first as `at_sha`, then the fix, one run; Policy 02 statement 1b) then Review. Route B (config only) is a single `[D<num>-1] Update` then Review. Squad specifics are in the squad briefing the leader receives.

## Stage ownership

| Ticket | Owner | Created by | Starts when |
|---|---|---|---|
| root ticket | product-owner (spec, CI/CD, docs, design) or dev-team (confirmed bug, direct-door ticket), or devops / docs-writer (direct-door ticket) | requester or Mika | assignment at `todo`; product-owner reassigns a bug root to dev-team after its gate |
| `[S<num>]` | spec-reviewer | product-owner | `todo`; re-armed `blocked`→`in_progress --no-start` + mention |
| `[P<num>-1]` | dev-team → dev-leader, devops, docs-writer, or service-architect | product-owner | created `todo` |
| `[P<num>-1c]` | pr-reviewer | product-owner | promoted once the devops, docs-writer or service-architect PR URL is posted |
| `[P<num>-2]` | release-manager | product-owner | promoted after `[P<num>-1]` verifies |
| `[D<num>-n]` | dev-team members | dev-leader | stage promotion |

## Verification before promotion

`done` says the assignee finished, not that the deliverable is correct. Before promoting the next stage: `[S<num>]` → verdict APPROVED; `[P<num>-1]` (dev-team) → pr-reviewer's score reported and `multica issue pull-requests <id> --output json` shows a PR into `dev` with `state: merged` and no close intent; `[P<num>-1]` (devops, docs-writer, service-architect) → an open PR based on `dev`; `[P<num>-1c]` → merged; `[P<num>-2]` → the `dev`→`main` PR merged. Unsatisfied → resolve on that owner's ticket with its agent mention; never promote past it.

## Branch and release strategy

`feature/<key>-<slug>` from fresh `origin/dev` → PR to `dev` (pr-reviewer merges) → `dev`→`main` release PR (release-manager merges) → CI publishes NuGet/npm from `main`. One repo per phase ticket; a phase naming two repos is rejected `blocked` to product-owner for a split. One feature branch and one PR per cycle; members commit to the leader's branch and never open PRs. devops uses `chore/<key>` branches to `dev`, docs-writer `docs/<key>`, service-architect `design/<key>`. No `[P<num>-2]` for a change a package consumer cannot observe (comments, tests, tooling), and none at all on a ticket that has a parent — its parent's owner releases the children together, woken by the child's `done`.

## Stage barriers

Stage N's barrier fires only when every sub-task at stage ≤ N is terminal (`done`/`cancelled`): the platform's sub-issue rule then wakes the parent's owner, who promotes stage N+1. A `blocked` gate at stage 3 keeps every higher stage's `done` silent, so there the member posts its handoff line on the parent (workspace context). A re-entry into `done` re-fires the barrier. Nobody flips their own sub-task out of `done`. The leader does, only to `in_progress` (`multica issue status <id> in_progress --no-start`) and only as the first step of re-triggering fix work on a `done` or `blocked` sub-task, mention posted after; the barrier or handoff line that follows its return to `done` is a report to verify, not a new stage. Every re-triggered sub-task carries `Retrigger on done` = the blocked issue's key, comma-separated when its `done` must re-arm several (workspace context), so a fix landing above the gate's stage still tells the leader exactly which issues to re-arm.

## Human touch points

| Gate | Cap | Then |
|---|---|---|
| business clarification | — | requester, always |
| spec review | 5 rework rounds | `[S<num>]` reassigned to the resolved owner at `todo` |
| bug confidence | < 90% | requester confirms before delegation |
| PR review | 3 rework rounds (a passing PR never reaches a human; a failed merge goes to dev-leader) | Review sub-task reassigned to the resolved owner at `todo` with options — A merge as-is · B one more round · C park · D close; the owner replies with dev-leader's mention and the pipeline waits until then |
| squad fix attempts | 2 on one root cause | phase cycle → product-owner mentioned on the phase ticket; root cycle → resolved owner by reassignment |
| defect found by a member | — | leader files ONE `bug-report` ticket assigned to product-owner at `todo`, `Owner` set; Workflow A's confidence gate decides whether a human confirms |
| review leftovers | — | in-scope: cleared by pr-reviewer in-cycle; out-of-scope: dropped unless a defect or security finding with a named reproduction |
| service design | every design PR | `[P<num>-1c]` reassigned to the resolved owner at `todo` with options (A merge · B revise with guidance · C park · D close); the owner replies with product-owner's mention, product-owner relays; pr-reviewer merges on A |
| release | critical: a `(MINOR)` commit or a `release-review` PR in `origin/main..origin/dev` | not critical → automated; critical → release ticket reassigned to the resolved owner at `todo` with options (A merge now · B hold); release-manager merges on the owner's reply A |
