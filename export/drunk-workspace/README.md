# drunk-workspace export

Full-workspace bundle: 30 skills, 16 agents, 3 squads, 4 projects, 7 autopilots (`autopilots/`, prompt in `*.description.md`; push with `multica autopilot update <id> --description "$(cat f)"`), plus `workspace/context.md` — the workspace system prompt (Workspace Context) that Multica injects into every agent run. Push it with `multica workspace update <id> --context-stdin < workspace/context.md`.

**Config files.** `properties/properties.json` carries the ACTIVE property definitions only — archived ones are
dropped on purpose (the CLI has `property archive`/`unarchive` but no delete, so an archived definition lives on
server-side with its values preserved; it just never comes back into the bundle). A re-export that reintroduces one
is noise, not a change. No instruction file in this bundle pins a UUID: agent, squad and project ids are resolved at
run time (`multica agent|squad|project list --output json`), and the mention-link recipe lives once in the
Workspace Context.

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


| Agent            | Runtime | Model               | Thinking |
| ---------------- | ------- | ------------------- | -------- |
| arch-reviewer    | claude  | claude-opus-5-5[1m] | xhigh    |
| product-owner    | claude  | claude-opus-5-5[1m] | xhigh    |
| service-architect | claude | claude-opus-5-5[1m] | high     |
| spec-reviewer    | claude  | claude-opus-5-5[1m] | high     |
| dev-leader       | claude  | claude-opus-5-5[1m] | high     |
| pr-reviewer      | claude  | claude-opus-5-5[1m] | xhigh    |
| blog-writer      | claude  | claude-sonnet-5     | high     |
| claude_ultra     | claude  | claude-opus-5-5[1m] | xhigh    |
| dev-backend      | claude  | claude-opus-5-5     | high     |
| release-manager  | claude  | claude-sonnet-5     | high     |
| docs-writer      | claude  | claude-sonnet-5     | high     |
| devops           | claude  | claude-sonnet-5     | high     |
| default          | claude  | claude-sonnet-5     | high     |
| run-medic        | claude  | claude-haiku-4-5    | low      |
| issue-janitor    | claude  | claude-haiku-4-5    | (runtime default) |
| Mika             | claude  | claude-haiku-4-5    | (runtime default) |
| medium-publisher | claude  | (runtime default)   | —        |


Reasoning/judgment roles (orchestration, gates, review) ride opus on the 1M-context tier (`claude-opus-5-5[1m]`) — arch-reviewer, product-owner, pr-reviewer and the `claude_ultra` assistant at `xhigh`, dev-leader, spec-reviewer and service-architect at `high`; `dev-backend` rides opus on the standard tier (`claude-opus-5-5`) at `high`; devops, release, writing and the `default` assistant ride sonnet. `run-medic` rides haiku at `low`: hourly run recovery is pattern-matching over agent task rows, not judgment.
`issue-janitor` and `Mika` ride haiku at the runtime-default thinking level. Every agent runs on the `Claude (Stevens-Mac-mini.local)` runtime.