# SDLC Delivery Pipeline — Shared Contract

The one-page contract every pipeline agent shares: actors, flows, stage ownership, branch strategy, escalation caps. Platform-wide constants (statuses, wakes, titles, `Owner`, git rules) are in the Workspace Context you already carry and are not repeated here. Role procedure lives in role skills — `sdlc-flow-po-orchestration` (product-owner), `sdlc-flow-squad-leader-playbook` (dev-leader), `spec-review-gate`, `pr-review-gate`; if this file and a role skill disagree, the role skill wins for its owner and the mismatch is reported to the workspace owner.

## Actors

- **product-owner** — leader of product-team. Research, spec, orchestration of the root ticket. Read-only on code.
- **spec-reviewer** — automated spec gate (Workflow B). Approve bar 8.5, max 5 rework rounds.
- **dev-team** — squad led by **dev-leader**; members dev-backend (tests and code, acceptance-test-first), docs-writer (documentation only), pr-reviewer (PR gate, merges into `dev`), release-manager (a `Release` stage on root cycles). The leader cuts the one feature branch and opens the one PR itself (`leader-gitops`).
- **pr-reviewer** — automated PR gate for every `dev`-bound PR (dev-team's cycle PR and devops' standalone PR). Approve bar 8.5, max 2 rework rounds plus one polish round.
- **release-manager** — opens and merges the single `dev`→`main` release PR, as `[P<num>-2]` on a spec cycle or `[D<num>-n] Release` on a root cycle. CI publishes the package on merge.
- **devops** — CI/CD pipelines, package-publish automation, docker-compose files. Lands as `chore/<issue-key>` PR to `dev`, gated by pr-reviewer. Never enters the squad flow, never gets a spec gate.
- **Humans** — the requester (root creator) and the resolved owner (`Owner` property). Business clarifications and escalations only.

## Workflows

| Request | Workflow | Shape |
|---|---|---|
| question or defect to root-cause | **A** | research → root-cause report + confidence → ≥90% (or requester confirmed): the ROOT is reassigned to dev-team, which runs the cycle plus a `Release` stage and finalizes it `in_review`; <90% requester confirms first; pure question ends at the report |
| feature or enhancement to a library repo | **B → C** | clarify to zero open questions → business spec in the root description → `[S<num>]` gate → C |
| delivery of an approved spec | **C** | `[P<num>-1] Implementation` (dev-team, `todo`, stage 1; description pins `Spec revision: <n>`, frozen for the cycle) → `[P<num>-2] Release` (release-manager, `backlog`, stage 2) → root `done` |
| CI/CD or build/publish automation | **D** | D1 analysis-only ends at the report; D2 `[P<num>-1] CI/CD change` (devops, stage 1) → `[P<num>-1c] Review CI/CD PR` (pr-reviewer, stage 2) → root `done`. No spec gate, no release phase |
| docs-only change to a library repo | **E** | the ROOT is reassigned to dev-team with a `## Brief` (Route B) → dev-leader finalizes `in_review`. No spec gate, no release. A docs ticket may also be assigned to dev-team directly, bypassing product-owner |

Inside dev-team a cycle is `[D<num>-1] Acceptance tests` → leader's inline AT approval (pins `at_sha`) → `[D<num>-2] Build` (+ `Docs` at the same stage) → leader opens the PR → `[D<num>-3] Review` (→ `[D<num>-4] Release` on a root cycle that republishes). Route B (docs/config only) is a single `[D<num>-1] Update` then Review. Squad specifics are in the squad briefing the leader receives.

## Stage ownership

| Ticket | Owner | Created by | Starts when |
|---|---|---|---|
| root ticket | product-owner (spec, CI/CD) or dev-team (confirmed bug, docs, direct-door ticket) | requester or Mika | assignment at `todo`; product-owner reassigns a bug/docs root to dev-team after its gate |
| `[S<num>]` | spec-reviewer | product-owner | `todo`; re-armed `blocked`→`in_progress --no-start` + mention |
| `[P<num>-1]` | dev-team → dev-leader, or devops | product-owner | created `todo` |
| `[P<num>-1c]` | pr-reviewer | product-owner | promoted once the devops PR URL is posted |
| `[P<num>-2]` | release-manager | product-owner | promoted after `[P<num>-1]` verifies |
| `[D<num>-n]` | dev-team members (incl. release-manager on a root cycle) | dev-leader | stage promotion |

## Verification before promotion

`done` says the assignee finished, not that the deliverable is correct. Before promoting the next stage: `[S<num>]` → verdict APPROVED; `[P<num>-1]` (dev-team) → pr-reviewer's score reported and `multica issue pull-requests <id> --output json` shows a PR into `dev` with `state: merged` and no close intent; `[P<num>-1]` (devops) → an open PR based on `dev`; `[P<num>-1c]` → merged; `[P<num>-2]` → the `dev`→`main` PR merged. Unsatisfied → resolve on that owner's ticket with its agent mention; never promote past it.

## Branch and release strategy

`feature/<key>-<slug>` from fresh `origin/dev` → PR to `dev` (pr-reviewer merges) → `dev`→`main` release PR (release-manager merges) → CI publishes NuGet/npm from `main`. One repo per phase ticket; a phase naming two repos is rejected `blocked` to product-owner for a split. One feature branch and one PR per cycle; members commit to the leader's branch and never open PRs. devops uses `chore/<key>` branches to `dev`. No `[P<num>-2]` for a change a package consumer cannot observe (comments, tests, tooling).

## Stage barriers

Stage N's barrier fires only when every sub-task at stage ≤ N is terminal (`done`/`cancelled`). A `blocked` gate at stage 3 keeps every higher stage's `done` silent, so a sub-task filed above a non-terminal stage must end its completion report with the leader's mention. A re-entry into `done` re-fires the barrier. Nobody flips their own sub-task out of `done`. The leader (any re-trigger) and pr-reviewer (a REWORK or POLISH round) do, only to `in_progress` (`multica issue status <id> in_progress --no-start`) and only as the first step of re-triggering fix work on a `done` or `blocked` sub-task, mention posted after; the barrier that re-fires when it returns to `done` is expected, and the leader treats it as a report to verify, not as a new stage.

## Human touch points

| Gate | Cap | Then |
|---|---|---|
| business clarification | — | requester, always |
| spec review | 5 rework rounds | `[S<num>]` reassigned to the resolved owner at `todo` |
| bug confidence | < 90% | requester confirms before delegation |
| PR review | 2 rework rounds, failed precondition, failed merge | Review sub-task reassigned to the resolved owner at `todo` |
| squad fix attempts | 2 on one root cause | phase cycle → product-owner mentioned on the phase ticket; root cycle → resolved owner by reassignment |
| defect found by a member | — | leader files ONE `bug-report` ticket assigned to product-owner at `todo`, `Owner` set; Workflow A's confidence gate decides whether a human confirms |
| review leftovers | — | in-scope: cleared by pr-reviewer in-cycle; out-of-scope: dropped unless a defect or security finding with a named reproduction |
| release | — | automated |
