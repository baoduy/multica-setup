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

- 2026-09-22 (b) — Policy 05 v1.5: **every root main ticket title carries one type prefix** — `[Feature]` (new capability) · `[Enhance]` (change to behaviour that exists) · `[Bug]` · `[Question]` · `[CICD]` · `[Docs]` — matching its type label, which stays the source of truth (`[Feature]` and `[Enhance]` share the `feature` label; the prefix is the finer split the labels do not make). product-owner sets or corrects it at intake, in the same step it labels the root and posts the spec, with `--no-start` on the rename so the title update does not wake a second run of itself; where product-owner never touches the ticket, the first agent to pick it up sets it. Root-only: no child ever carries a type prefix, and `[S<num>]`/`[P<num>-n]`/`[D<num>-n]` keying is off the root's key NUMBER, so the rename changes no numbering (new statements 7a, 7b). Requesters and Mika still create with a plain title. Owner-approved. Cascaded to Policy 09 (Mika), `workspace.context.md`, `sdlc-flow-po-orchestration` (new step 2a), `sdlc-spec-template` (the spec's H1 stays unprefixed), and agents `mika`, `claude-ultra`, `default`.

- 2026-09-22 — Policy 06 v2.5: the spec gains **§3a Contract changes**. A change that adds or alters a domain entity states every new or changed field with its type, length, required, unique/indexed, default and notes; a change that touches an endpoint states every one of them with HTTP verb, path, purpose and auth; §4 Scope names every repo touched, one per bullet. §3a is the one section where entity, field and endpoint names are allowed — class names, method signatures, file paths and `file:line` stay banned everywhere. Cause: the spec was business-only above the contract, so the data and API surface the whole team must agree on before code reached them only in the dev-leader's impl-brief, one layer too late to review. Owner-approved amendment to statements 2, 3, 6, 7 and 12 (new 5a, 7a). Cascaded to `sdlc-spec-template` (§3a template, section tests, quality bar), `spec-review-gate` (contract gates, Scope completeness, Completeness dimension — weights unchanged), `sdlc-impl-brief` (§3a binding, divergence goes back to product-owner), `sdlc-flow-po-orchestration` and `agents/product-owner.md`.

- 2026-09-18 — Policy 06 v2.4 and Policy 09 v1.6: the clarification gate is run with `interview-me` and `multica-brainstorming` — the requester is interviewed one question at a time and the design is presented back before any spec work. Cause: both skills were attached to `product-owner` but named nowhere in its instructions or `sdlc-flow-po-orchestration`, and an agent follows its inline text, not its attached skill list (same failure mode as CodeGraph, 2026-09-17). Cascaded to `sdlc-flow-po-orchestration` (Clarification gate) and `agents/product-owner.md`.

- 2026-09-17 (b) — Policy 08 v1.1 (new statement 12: the publish pipeline owns the release number; a normal release is a patch, a breaking change bumps the MINOR only with a `(MINOR)` commit-title marker, and the MAJOR number is frozen — no agent writes `(MAJOR)`, hand-edits a version literal, or creates a tag/release; an unasked-for major bump is a release defect to report, never to re-publish over: `VER-REL-001..003`), Policy 01 v1.1 and Policy 06 v2.3 (statement 12 and the invariant example no longer promise a SemVer major on a break). Cause: DKNet went v10.1.29 → v11.0.0 → v12.0.0 in one day across delivery cycles nobody scoped as a major release. Cascaded to `nodejs-typescript-standards` (TS-PUB-002), `pulumi-azure-iac-standards` (PULUMI-TEST-003, PULUMI-DEP-003), `helm-k8s-conventions` (HELM-DEL-002), `pr-review-gate` (dimension 1, blocking), `spec-review-gate`, `workspace.context.md`, and agents release-manager and devops.

- 2026-09-17 — Policy 04 v1.5 (statement 2: the CodeGraph index is verified with `codegraph status`, never by the `.codegraph/` folder, and `init` runs in the foreground), Policy 09 v1.5 (dev-leader grounds every brief row in CodeGraph; dev-backend runs CodeGraph before its first grep or file read, with an EVIDENCE row). Cause, measured over 937 runs: dev-backend used CodeGraph in 1, docs-writer and dev-team in 0, pr-reviewer in 91 of 154 — agent text either checked the folder (a fresh checkout has it without an index) or said nothing. Cascaded to `codegraph`, `pr-review-gate`, `spec-review-gate`, `sdlc-flow-po-orchestration`, `sdlc-flow-squad-worker-playbook`, `sdlc-flow-squad-leader-playbook`, and agents dev-leader, dev-backend, docs-writer, pr-reviewer, spec-reviewer, arch-reviewer.

- 2026-09-23 — Policy 09 v1.7: `run-medic` chartered as the eleventh factory agent — hourly recovery of agent runs killed by a transient infrastructure failure (API rate limit / overload, runtime offline, daemon restart), with an explicit carve-out from the member write rule and a hard cap of 3 wakes per issue counted on the new `Wake count` property, after which the issue is handed to its human owner. Cascaded to `agents/run-medic.*`, the `🔁 Hourly Run Recovery` autopilot, `properties/properties.json`, `workspace/workspace.context.md` and the README model table. Same pass corrected the issue-hygiene cadence from "nightly" to weekly (it runs Sunday and Monday 09:00 SGT) everywhere it was quoted, and realigned the bundle's autopilot `status` fields with the live workspace.

- 2026-09-16 (c) — Policy 04 v1.4 (statement 3: a gate's own review sub-task is pipeline mode however it was woken, including a re-arm mention in any status; statement 10: a spec REWORK is re-armed by product-owner in two mandatory parts, `in_progress --no-start` + spec-reviewer's mention, never by a flip to `todo`), Policy 06 v2.2 (statement 11 carries the same re-arm mechanics and drops the retired `spec_review_round` metadata key for the `Gate round` property). DRK-1364 stalled twice on a `blocked`→`todo` re-arm that woke nobody — the second time until the owner asked for the round by hand. Cascaded to `sdlc-flow-po-orchestration` (two-part re-arm plus an end-of-turn actuation check), `spec-review-gate`, `product-team` briefing and `workspace.context.md`, which now says plainly that a ticket which has already run is never re-woken by its status.

- 2026-09-16 (b) — Policy 03 v1.1 (statements 3b/3c: members never create or push a branch, no bare `git push`, a push is proved with `git ls-remote`). Workspace context also bans backgrounding a long command — a run cannot resume around an orphaned process. Cascaded to `workspace.context.md`, `sdlc-gitflow` and `sdlc-flow-squad-worker-playbook`.

- 2026-09-16 — Policy 05 v1.4 (statement 1b: a ticket assigned to product-owner with a parent is a sub-issue — same gates, no `[P<num>-2]`, terminates at the verified `[P<num>-1]`; the parent's owner releases its children together). Cascaded to `sdlc-flow-po-orchestration`, `sdlc-flow-delivery-pipeline`, `squads/product-team.md` and `agents/product-owner.md`.

- 2026-09-15 (b) — Policy 06 v2.1: plain-English writing rules for every human-facing document. Templates rewritten: `sdlc-spec-template` (Summary, sub-labels, bullets), `blocker-report` (fixed EVIDENCE keys, DEVIATIONS table, 25/40-line caps, root-cause shape), `sdlc-impl-brief` (Mode header, `Proof` column, scenario names instead of copied Gherkin, changelog instead of appended sections, 10 KB cap); marker legend, mode procedures and the standard done-list moved into `test-driven-development`; leader plan comment capped at 2 KB.

- 2026-09-15 — Policy 05 v1.3 (bugs and docs handed to dev-team as the root ticket, phases for specs only, spec frozen at delegation, gate never parks, daily stall sweep), Policy 04 v1.3 (re-review always ends in a verdict, Workflow D CI exception, CI-first verification), Policy 07 v1.2, Policy 09 v1.4 (release-manager in dev-team for root cycles; Mika runs the stall sweep). Cascaded to `pr-review-gate`, `sdlc-flow-*`, `sdlc-gitflow`, `leader-gitops`, both squads, agents, and the `Daily Stall Sweep` autopilot.

- 2026-09-14 — Policy 05 v1.2 (Workflow E direct door, gate properties, Workspace Context layer), Policy 04 v1.2 (gate state on properties, resolved-owner handoff), Policy 07 v1.1 (member-found defects filed to product-owner), Policy 09 v1.3 (statement 1b: leader-filed defects assigned to product-owner; Workspace Context; assistants' routing scope). Cascaded to `workspace/context.md`, the `sdlc-flow-*` skills (leader and product-owner playbooks split into core + `references/`), both gate skills, `bug-report`, both squad briefings and every agent instruction.

## How policies relate to skills, agents and squads

- **Skills** are the executable contracts agents load at runtime — they *implement* these policies.
- **Policies** (this folder) are the governance and the source of truth — intent, scope, responsibilities, compliance bar, waiver rules.
- **Agents / squads** (`agents/`, `squads/`) are the actors these policies assign responsibility to: `product-owner`, `spec-reviewer`, `arch-reviewer`, `dev-leader`/`dev-team`, `dev-backend`, `pr-reviewer`, `devops`, `release-manager`, `issue-janitor`, `run-medic`, `Mika` — each chartered (goal, responsibilities, boundaries) in [Policy 09](09-agent-roles-and-responsibilities.md); `default` and `claude_ultra` are platform assistants outside the factory.

## Reading order for a new drunk developer

01 → 02 → 03 → 04 first (what you do every day), then 05 for the big picture, then 06–08 as
they become relevant to your role.

## Document structure

Every policy uses the same shape: front-matter block · **Authority note** · Purpose · Scope ·
Policy statements (numbered, testable, citing the governing skills' `rule-id`s) · Roles &
responsibilities · Definition of Done / compliance · Enforcement · Exceptions & waivers ·
References.
