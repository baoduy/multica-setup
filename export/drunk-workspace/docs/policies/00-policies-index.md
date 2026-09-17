# drunk-workspace SDLC Policies — Source of Truth

**These policies are the authoritative source of truth for the `drunk-workspace` software
factory.** Every skill, agent instruction, squad briefing, and line of implementation code
**derives downward** from a policy here. When any lower layer diverges from a policy, the
policy is correct by definition — reconcile the lower layer *up* to it. Changes are made
**top-down**: amend the policy first, then cascade the change into the skill(s), agent
instructions, and code, in that order.

> **What drunk builds.** drunk-workspace maintains the open-source `github.com/baoduy`
> repos across **all stacks**: .NET/DDD NuGet libraries, Pulumi/TypeScript npm packages,
> Python MCP services, Docker images, and Helm charts. **There is no deployed
> environment** — for the library repos, *publishing the package IS the release*
> (NuGet/npm, off `main`); for the container-image repos, *publishing a multi-arch image
> IS the release*. No SANDBOX, no PRD, no k8s promotion. Do not import that model from a
> sibling workspace.

## Authority hierarchy — change flows downward

```
                        ┌───────────────────────────────┐
                        │   POLICY  (docs/policies/**)  │  ← source of truth: WHAT & WHY
                        │   intent · rules · precedence │     amend HERE first
                        └───────────────┬───────────────┘
                                        │ derives / must conform
                                        ▼
                        ┌────────────────────────────────┐
                        │   SKILL   (skills/**/SKILL.md) │  ← the HOW: detailed procedure
                        │   commands · rubrics · shapes  │     conforms to the policy
                        └───────────────┬────────────────┘
                                        │ derives / must conform
                                        ▼
                        ┌───────────────────────────────┐
                        │   AGENT / SQUAD  (agents/**,  │  ← identity, scope, hard limits
                        │   squads/**)  instructions    │     loads the skills
                        └───────────────┬───────────────┘
                                        │ derives / must conform
                                        ▼
                        ┌────────────────────────────────┐
                        │   IMPLEMENTATION (repos: code, │  ← the built thing
                        │   PRs, tests, images, charts)  │     verified against the policy
                        └────────────────────────────────┘

   Conflict rule:  the HIGHER layer always wins.  A skill that contradicts a policy is a
                   defect in the skill, not the policy.  Fix upward, in the same change.
```

- **Policy = intent, rules, and precedence** (WHAT must hold and WHY). Authoritative.
- **Skill = the detailed procedure** (HOW — exact commands, scoring rubrics, code shapes).
It must conform to the governing policy; if they conflict, the policy's intent wins and the
skill is corrected — never the reverse.
- **Agent/squad = who acts, with what limits**, loading the skills.
- **Implementation = the built thing**, verified against the policy at the gates.

## Change control

Any change to how the factory works starts at the policy layer:

```
  proposed change
        │
        ▼
  1. AMEND THE POLICY  ── state the new rule/intent here; bump Version; note it in this index
        │
        ▼
  2. CASCADE TO SKILL(S)  ── update every skill the policy's "Related skills" row names
        │                     so its procedure matches the amended rule
        ▼
  3. CASCADE TO AGENTS/SQUADS  ── update instructions/briefings only if scope or limits moved
        │
        ▼
  4. CASCADE TO CODE  ── implementation and its verification follow the updated skill
```

**Never patch a skill or code to introduce a rule that is not in a policy.** If the rule
belongs in the factory, it belongs in a policy first. A rule that exists only in a skill is
a policy gap — file it upward.

## Catalog

| #                                        | Policy                              | Audience        | Skills it governs (derive from it)                                                                                             | Enforced at                       |
| ---------------------------------------- | ----------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------ | --------------------------------- |
| [01](01-coding-standards.md)             | Coding Standards & Repository Layout | every dev ⭐     | `nodejs-typescript-standards`, `python-mcp-standards`, `dotnet10-efcore10-standards`, `dknet-ddd-conventions`, `pulumi-azure-iac-standards`, `helm-k8s-conventions` | PR review gate, arch review sweep |
| [02](02-testing-and-quality.md)          | Testing & Quality                   | every dev ⭐     | `test-driven-development` (+ each stack's `*-TEST-*` rules)                                                                     | PR review gate                    |
| [03](03-source-control-branching.md)     | Source Control & Branching          | all             | `sdlc-gitflow`, `leader-gitops`                                                                                                 | PR review gate, leaders, release-manager |
| [04](04-code-and-spec-review.md)         | Code, Spec & Architecture Review    | reviewers       | `pr-review-gate`, `spec-review-gate`, `architecture-review-sweep`                                                              | the gates themselves              |
| [05](05-sdlc-delivery-lifecycle.md)      | SDLC Delivery Lifecycle             | all             | `sdlc-flow-delivery-pipeline`, `sdlc-flow-po-orchestration`, `sdlc-flow-squad-leader-playbook`, `sdlc-flow-squad-worker-playbook` | product-owner + gates             |
| [06](06-requirements-and-spec.md)        | Requirements & Specification        | product         | `sdlc-spec-template`, `sdlc-impl-brief`                                                                                         | spec review gate                  |
| [07](07-bug-and-defect-management.md)    | Bug & Defect Management             | all             | `bug-report`, `blocker-report`                                                                                                  | product-owner, dev-team           |
| [08](08-container-build-and-release.md)  | Container, Build & Release          | devops/release  | `docker-image-standards`, `helm-k8s-conventions`, package-publish workflows                                                    | PR review gate, devops, release-manager |
| [09](09-agent-roles-and-responsibilities.md) | Agent Roles & Responsibilities  | every agent ⭐  | none — governs `agents/**` instructions and `squads/**` briefings (each charter names its agent's skills)                      | agent instructions + every gate   |
| [10](10-ticket-ownership-and-owner-pickup.md) | Ticket Ownership & Owner Pickup     | every agent     | `sdlc-flow-delivery-pipeline`, `sdlc-flow-po-orchestration`, `sdlc-flow-squad-leader-playbook`, `spec-review-gate`, `pr-review-gate` | product-owner, leaders, gates     |

## Policy map

```
                          ┌─────────────────────────────────────┐
                          │  05  SDLC DELIVERY LIFECYCLE        │
                          │  the spine: intake → deliver → ship │
                          └───┬─────────────┬──────────────┬────┘
             requirements     │             │ engineering  │  build/release
                              ▼             ▼              ▼
                  ┌─────────────────┐  ┌───────────────┐  ┌──────────────────────┐
                  │ 06 REQUIREMENTS │  │  ENGINEERING  │  │ 08 CONTAINER, BUILD  │
                  │    & SPEC       │  │   (01–04)     │  │    & RELEASE         │
                  └─────────────────┘  └──────┬────────┘  └──────────────────────┘
                                             │
                    ┌──────────────┬─────────┼──────────┬──────────────┐
                    ▼              ▼         ▼          ▼
             ┌───────────┐  ┌───────────┐ ┌─────────┐ ┌───────────┐
             │ 01 CODING │  │02 TESTING │ │03 SOURCE│ │04 REVIEW  │
             │ STANDARDS │  │ & QUALITY │ │ CONTROL │ │ (gates)   │
             └───────────┘  └───────────┘ └─────────┘ └───────────┘

             ┌────────────────────────────────────────────────────────┐
             │  07 BUG & DEFECT MGMT — cross-cuts: any policy's rule  │
             │  can trigger a defect that re-enters via 05            │
             └────────────────────────────────────────────────────────┘
```

## Change log

- 2026-09-17 — Policy 04 v1.5 (statement 2: the CodeGraph index is verified with `codegraph status`, never by the `.codegraph/` folder, and `init` runs in the foreground), Policy 09 v1.5 (dev-leader grounds every brief row in CodeGraph; dev-backend runs CodeGraph before its first grep or file read, with an EVIDENCE row). Cause, measured over 937 runs: dev-backend used CodeGraph in 1, docs-writer and dev-team in 0, pr-reviewer in 91 of 154 — agent text either checked the folder (a fresh checkout has it without an index) or said nothing. Cascaded to `codegraph`, `pr-review-gate`, `spec-review-gate`, `sdlc-flow-po-orchestration`, `sdlc-flow-squad-worker-playbook`, `sdlc-flow-squad-leader-playbook`, and agents dev-leader, dev-backend, docs-writer, pr-reviewer, spec-reviewer, arch-reviewer.

- 2026-09-16 (c) — Policy 04 v1.4 (statement 3: a gate's own review sub-task is pipeline mode however it was woken, including a re-arm mention in any status; statement 10: a spec REWORK is re-armed by product-owner in two mandatory parts, `in_progress --no-start` + spec-reviewer's mention, never by a flip to `todo`), Policy 06 v2.2 (statement 11 carries the same re-arm mechanics and drops the retired `spec_review_round` metadata key for the `Gate round` property). DRK-1364 stalled twice on a `blocked`→`todo` re-arm that woke nobody — the second time until the owner asked for the round by hand. Cascaded to `sdlc-flow-po-orchestration` (two-part re-arm plus an end-of-turn actuation check), `spec-review-gate`, `product-team` briefing and `workspace.context.md`, which now says plainly that a ticket which has already run is never re-woken by its status.

- 2026-09-16 (b) — Policy 03 v1.1 (statements 3b/3c: members never create or push a branch, no bare `git push`, a push is proved with `git ls-remote`). Workspace context also bans backgrounding a long command — a run cannot resume around an orphaned process. Cascaded to `workspace.context.md`, `sdlc-gitflow` and `sdlc-flow-squad-worker-playbook`.

- 2026-09-16 — Policy 05 v1.4 (statement 1b: a ticket assigned to product-owner with a parent is a sub-issue — same gates, no `[P<num>-2]`, terminates at the verified `[P<num>-1]`; the parent's owner releases its children together). Cascaded to `sdlc-flow-po-orchestration`, `sdlc-flow-delivery-pipeline`, `squads/product-team.md` and `agents/product-owner.md`.

- 2026-09-15 (b) — Policy 06 v2.1: plain-English writing rules for every human-facing document. Templates rewritten: `sdlc-spec-template` (Summary, sub-labels, bullets), `blocker-report` (fixed EVIDENCE keys, DEVIATIONS table, 25/40-line caps, root-cause shape), `sdlc-impl-brief` (Mode header, `Proof` column, scenario names instead of copied Gherkin, changelog instead of appended sections, 10 KB cap); marker legend, mode procedures and the standard done-list moved into `test-driven-development`; leader plan comment capped at 2 KB.

- 2026-09-15 — Policy 05 v1.3 (bugs and docs handed to dev-team as the root ticket, phases for specs only, spec frozen at delegation, gate never parks, daily stall sweep), Policy 04 v1.3 (re-review always ends in a verdict, Workflow D CI exception, CI-first verification), Policy 07 v1.2, Policy 09 v1.4 (release-manager in dev-team for root cycles; Mika runs the stall sweep). Cascaded to `pr-review-gate`, `sdlc-flow-*`, `sdlc-gitflow`, `leader-gitops`, both squads, agents, and the `Daily Stall Sweep` autopilot.

- 2026-09-14 — Policy 05 v1.2 (Workflow E direct door, gate properties, Workspace Context layer), Policy 04 v1.2 (gate state on properties, resolved-owner handoff), Policy 07 v1.1 (member-found defects filed to product-owner), Policy 09 v1.3 (statement 1b: leader-filed defects assigned to product-owner; Workspace Context; assistants' routing scope). Cascaded to `workspace/context.md`, the `sdlc-flow-*` skills (leader and product-owner playbooks split into core + `references/`), both gate skills, `bug-report`, both squad briefings and every agent instruction.

## How policies relate to skills, agents and squads

- **Skills** are the executable contracts agents load at runtime — they *implement* these policies.
- **Policies** (this folder) are the governance and the source of truth — intent, scope, responsibilities, compliance bar, waiver rules.
- **Agents / squads** (`agents/`, `squads/`) are the actors these policies assign responsibility to: `product-owner`, `spec-reviewer`, `arch-reviewer`, `dev-leader`/`dev-team`, `dev-backend`, `pr-reviewer`, `devops`, `release-manager`, `issue-janitor`, `Mika` — each chartered (goal, responsibilities, boundaries) in [Policy 09](09-agent-roles-and-responsibilities.md); `default` and `claude_ultra` are platform assistants outside the factory.

## Reading order for a new drunk developer

01 → 02 → 03 → 04 first (what you do every day), then 05 for the big picture, then 06–08 as
they become relevant to your role.

## Document structure

Every policy uses the same shape: front-matter block · **Authority note** · Purpose · Scope ·
Policy statements (numbered, testable, citing the governing skills' `rule-id`s) · Roles &
responsibilities · Definition of Done / compliance · Enforcement · Exceptions & waivers ·
References.
