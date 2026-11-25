# drunk-workspace export

Full-workspace bundle: 29 skills, 17 agents, 2 squads, 5 projects, 10 autopilots (`autopilots/`, prompt in `*.description.md`), 12 labels, 9 properties, plus `workspace/workspace.context.md` — the workspace system prompt (Workspace Context) that Multica injects into every agent run. Push text byte-exact: pass the file content as a raw argv element (e.g. from Python `subprocess`) to `multica workspace update <id> --context`, `multica agent update <id> --instructions`, `multica squad update <id> --instructions` and `multica autopilot update <id> --description`; use `--content-stdin` for `multica skill update` and `multica skill files upsert`. Shell `"$(cat f)"` and `--context-stdin` drop the trailing newline, and `--context` decodes backslash escapes. Read every pushed resource back and diff it against the file.

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

**Live sync ([Policy 03](docs/policies/03-source-control-branching.md) statement 11).** The tag `live/drunk` marks the
`main` commit the live workspace matches. A merge to `main` that touches this bundle wakes the `🔄 Drunk Live Sync`
autopilot through `.github/workflows/drunk-live-sync.yml`; `Mika` runs `scripts/drunk-live-sync.py`, which pushes
the changed resources byte-exact, reads them back and moves the tag. `python3 scripts/drunk-live-sync.py --check`
compares every supported file on `main` with live and pushes nothing.

## Layering (what an agent actually receives)

- **Workspace Context** (`workspace/workspace.context.md`) — every run, every agent: statuses, wakes, ticket conventions, `Owner`, git rules, report shapes. Stated once here, cited elsewhere.
- **Agent instructions** (`agents/*.md`) — identity, triggers, hard limits, the skills to load.
- **Squad instructions** (`squads/*.md`) — injected into the squad LEADER's task only, with a platform-generated roster (mention markdown + skills per member). Members never see them.
- **Skills** (`skills/*/SKILL.md` + `references/`) — written to the run's working directory as files; a skill costs tokens only when opened. Every-wake procedure lives in `SKILL.md`; rare paths live in `references/`.
- **Gate state** — `Gate verdict` / `Gate round` / `Gate score` custom properties on review sub-tasks.

## Agent → model assignment

Role charters (goal, responsibilities, boundaries per agent) live in
[Policy 09 — Agent Roles & Responsibilities](docs/policies/09-agent-roles-and-responsibilities.md);
`claude_ultra` is the platform assistant outside the factory roster.
Generated from `agents/*.json` (`model` / `thinking_level` / runtime) — keep in lock-step.


| Agent            | Runtime | Model               | Thinking |
| ---------------- | ------- | ------------------- | -------- |
| arch-reviewer    | claude  | claude-opus-5-5     | xhigh    |
| setup-steward    | claude  | claude-opus-5-5     | xhigh    |
| product-owner    | claude  | claude-opus-5-5     | high     |
| service-architect | claude | claude-opus-5-5     | high     |
| spec-reviewer    | claude  | claude-opus-5-5     | high     |
| dev-leader       | claude  | claude-opus-5-5     | high     |
| pr-reviewer      | claude  | claude-opus-5-5     | xhigh    |
| blog-writer      | claude  | claude-sonnet-5-5   | high     |
| claude_ultra     | claude  | claude-opus-5-5     | xhigh    |
| dev-backend      | claude  | claude-opus-5-5     | high     |
| dev-frontend     | claude  | claude-opus-5-5     | high     |
| release-manager  | claude  | claude-sonnet-5-5   | high     |
| docs-writer      | claude  | claude-opus-5-5     | medium   |
| devops           | codex   | gpt-6.1-sol         | high     |
| run-medic        | codex   | gpt-6-luna          | low      |
| issue-janitor    | codex   | gpt-6-luna          | medium   |
| Mika             | codex   | gpt-6-luna          | medium   |


Main development stays on Claude; the work around it rides Codex. Every Claude agent runs on the plain model ID: Claude Opus 5.5 and Sonnet 5.5 have a 1M context window by default, so there is no `[1m]` variant. Reasoning/judgment roles (orchestration, gates, review) ride opus (`claude-opus-5-5`) — arch-reviewer, pr-reviewer, setup-steward and the `claude_ultra` assistant at `xhigh`, product-owner, dev-leader, spec-reviewer and service-architect at `high`; `dev-backend` and `dev-frontend` ride opus at `high` too; release-manager and blog-writer ride sonnet (`claude-sonnet-5-5`) at `high`. These run on the `Claude (Stevens-Mac-mini.local)` runtime.
devops rides `gpt-6.1-sol` at `high` (moved off `gpt-6-sol` after OpenAI returned "Selected model is at capacity" mid-run). docs-writer was moved live to `claude-opus-5-5` at `medium` on the `Claude (Stevens-Mac-mini.local)` runtime, recorded here 2026-11-23; `run-medic`, `issue-janitor` and `Mika` ride `gpt-6-luna` (`low` for run-medic — hourly run recovery is pattern-matching over agent task rows, not judgment — `medium` for the other two). These run on the `Codex (Stevens-Mac-mini.local)` runtime: the same host as Claude, because Mika's monthly insights autopilot shells out to `claude -p "/insights"`. Thinking is always set explicitly on a Codex agent; left empty, it inherits the host's `~/.codex/config.toml`.