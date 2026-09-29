# Monxa (mx) SDLC Policies — Source of Truth

**These policies are the authoritative source of truth for the `mx-workspace` software
factory.** Every skill, agent instruction, squad briefing, and line of implementation
code **derives downward** from a policy here. When any lower layer diverges from a policy,
the policy is correct by definition — reconcile the lower layer *up* to it. Changes are
made **top-down**: you amend the policy first, then cascade the change into the skill(s),
agent instructions, and code, in that order.

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
                        │   PRs, tests, charts)          │     verified against the policy
                        └────────────────────────────────┘

   Conflict rule:  the HIGHER layer always wins.  A skill that contradicts a policy is a
                   defect in the skill, not the policy.  Fix upward, in the same change.
```

- **Policy = intent, rules, and precedence** (WHAT must hold and WHY). Authoritative.
- **Skill = the detailed procedure** (HOW — exact commands, scoring rubrics, code shapes).
It must conform to the governing policy; if they conflict, the policy's intent wins and
the skill is corrected — never the reverse.
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
        │
        ▼
  5. RECONCILE README.md  ── per the README-mirror rule (CLAUDE.md)
```

**Never patch a skill or code to introduce a rule that is not in a policy.** If the rule
belongs in the factory, it belongs in a policy first. A rule that exists only in a skill is
a policy gap — file it upward.

## Catalog


| #                                     | Policy                           | Audience    | Skills it governs (derive from it)                                | Enforced at                  |
| ------------------------------------- | -------------------------------- | ----------- | ----------------------------------------------------------------- | ---------------------------- |
| [01](01-coding-standards-dotnet.md)   | .NET Coding Standards            | .NET dev ⭐  | `dotnet10-efcore10-standards`, `dknet-ddd-conventions`            | PR review gate, arch sweep   |
| [02](02-testing-and-quality.md)       | Testing &amp; Quality            | .NET dev ⭐  | `testing-standards`, `test-driven-development`, `playwright-bdd`  | PR review gate               |
| [03](03-source-control-branching.md)  | Source Control &amp; Branching   | .NET dev ⭐  | `sdlc-gitflow`, `leader-gitops`                                   | PR review gate, leaders      |
| [04](04-code-and-spec-review.md)      | Code &amp; Spec Review           | .NET dev ⭐  | `pr-review-gate`, `spec-review-gate`, `architecture-review-sweep` | the gates themselves         |
| [05](05-sdlc-delivery-lifecycle.md)   | SDLC Delivery Lifecycle          | all         | `sdlc-flow-delivery-pipeline`                                     | product-owner + gates        |
| [06](06-requirements-and-spec.md)     | Requirements &amp; Specification | product     | `sdlc-spec-template`, `sdlc-impl-brief`, `interview-me`, `multica-brainstorming` | spec review gate             |
| [07](07-bug-and-defect-management.md) | Bug &amp; Defect Management      | all         | `bug-report`, `blocker-report`                                    | product-owner, qc-team       |
| [08](08-release-management.md)        | Release Management               | ops/release | `prd-release-runbook`, `helm-chart-delivery`                      | release-manager, prd-release |
| [09](09-agent-roles-and-responsibilities.md) | Agent Roles &amp; Responsibilities | every agent ⭐ | none — governs `agents/**` instructions and `squads/**` briefings (each charter names its agent's skills) | agent instructions + every gate |


## Policy map

```
                          ┌─────────────────────────────────────┐
                          │  05  SDLC DELIVERY LIFECYCLE        │
                          │  the spine: intake → deliver → ship │
                          └───┬─────────────┬──────────────┬────┘
             requirements     │             │ engineering  │  release
                              ▼             ▼              ▼
                  ┌─────────────────┐  ┌───────────────┐  ┌────────────────┐
                  │ 06 REQUIREMENTS │  │  ENGINEERING  │  │ 08 RELEASE MGMT │
                  │    & SPEC       │  │   (01–04)     │  │  dev→main→prod  │
                  └─────────────────┘  └──────┬────────┘  └────────────────┘
                                             │
                    ┌──────────────┬─────────┼──────────┬──────────────┐
                    ▼              ▼         ▼          ▼              ▼
             ┌───────────┐  ┌───────────┐ ┌─────────┐ ┌───────────┐
             │ 01 CODING │  │02 TESTING │ │03 SOURCE│ │04 REVIEW  │
             │ STANDARDS │  │ & QUALITY │ │ CONTROL │ │ (gates)   │
             └───────────┘  └───────────┘ └─────────┘ └───────────┘

             ┌────────────────────────────────────────────────────────┐
             │  07 BUG & DEFECT MGMT — cross-cuts: any policy's rule  │
             │  can trigger a defect that re-enters via 05            │
             └────────────────────────────────────────────────────────┘
```

## How policies relate to skills, agents and squads

- **Skills** are the executable contracts agents load at runtime — they *implement* these policies.
- **Policies** (this folder) are the governance and the source of truth — intent, scope, responsibilities, compliance bar, waiver rules.
- **Agents / squads** (`agents/`, `squads/`) are the actors these policies assign responsibility to: `product-owner`, `spec-reviewer`, `dev-leader`/`dev-team` (`dev-backend`), `qc-leader`/`qc-team` (`qc-tester`, `qc-runner`), `pr-reviewer`, `release-manager`, `prd-release`, `devops`, `arch-reviewer`, `issue-janitor` — each chartered (goal, responsibilities, boundaries) in [Policy 09](09-agent-roles-and-responsibilities.md); `default` and `claude-ultra` are platform assistants outside the factory.

## Reading order for a new .NET developer

01 → 02 → 03 → 04 first (what you do every day), then 05 for the big picture,
then 06–08 as they become relevant to your role.

## Document structure

Every policy uses the same shape: front-matter block · **Authority note & governance
diagram** · Purpose · Scope · Policy statements (numbered, testable) · Roles &amp;
responsibilities · Definition of Done / compliance · Enforcement · Exceptions &amp; waivers ·
References. Policies 01–04 also carry an explicit **Best practices for .NET developers**
section.