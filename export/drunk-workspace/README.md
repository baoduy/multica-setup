# drunk-workspace export

Full-workspace bundle: 29 skills, 15 agents, 3 squads, 4 projects, 6 autopilots (`autopilots/`, prompt in `*.description.md`; push with `multica autopilot update <id> --description "$(cat f)"`), plus `workspace/context.md` — the workspace system prompt (Workspace Context) that Multica injects into every agent run. Push it with `multica workspace update <id> --context-stdin < workspace/context.md`.

**Governance / source of truth:** [`docs/policies/`](docs/policies/00-policies-index.md) — the
authoritative SDLC policies (coding standards, testing, source control, review, delivery,
requirements, defects, container/build/release). Every skill and agent derives from a policy
there; amend the policy first, then cascade. See the [index](docs/policies/00-policies-index.md).

## Layering (what an agent actually receives)

- **Workspace Context** (`workspace/context.md`) — every run, every agent: statuses, wakes, ticket conventions, `Owner`, git rules, report shapes. Stated once here, cited elsewhere.
- **Agent instructions** (`agents/*.md`) — identity, triggers, hard limits, the skills to load.
- **Squad instructions** (`squads/*.md`) — injected into the squad LEADER's task only, with a platform-generated roster (mention markdown + skills per member). Members never see them.
- **Skills** (`skills/*/SKILL.md` + `references/`) — written to the run's working directory as files; a skill costs tokens only when opened. Every-wake procedure lives in `SKILL.md`; rare paths live in `references/`.
- **Gate state** — `Gate verdict` / `Gate round` / `Gate score` custom properties on review sub-tasks.

## Agent → model assignment

Role charters (goal, responsibilities, boundaries per agent) live in
[Policy 09 — Agent Roles & Responsibilities](docs/policies/09-agent-roles-and-responsibilities.md);
`default` and `claude_ultra` are platform assistants outside the factory roster.
Generated from `agents/*.json` (`model` / `thinking_level` / runtime) — keep in lock-step.

| Agent | Runtime | Model | Thinking |
|---|---|---|---|
| arch-reviewer | claude | claude-opus-5 | max |
| product-owner | claude | claude-opus-5 | high |
| spec-reviewer | claude | claude-opus-5 | high |
| dev-leader | claude | claude-opus-5 | high |
| pr-reviewer | claude | claude-opus-5 | high |
| blog-writer | claude | claude-opus-5 | high |
| claude_ultra | claude | claude-opus-5 | xhigh |
| dev-backend | claude | claude-sonnet-5 | high |
| release-manager | claude | claude-sonnet-5 | high |
| docs-writer | claude | claude-opus-5 | high |
| devops | claude | claude-opus-5[1m] | high |
| default | claude | claude-sonnet-5 | high |
| issue-janitor | hermes | (runtime default) | — |
| Mika | hermes | (runtime default) | — |
| medium-publisher | claude | (runtime default) | — |

Reasoning/judgment roles (orchestration, gates, review) ride opus; implementation and the platform assistant ride sonnet; devops rides opus on the 1M-context tier. `issue-janitor` and `Mika` are the only agents still off the claude runtime (hermes, runtime default model).
