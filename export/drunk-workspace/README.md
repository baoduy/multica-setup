# drunk-workspace export

Full-workspace bundle: 31 skills, 18 agents, 3 squads, 6 projects, 10 autopilots (`autopilots/`, prompt in `*.description.md`), 19 labels, 9 properties, plus `workspace/workspace.context.md` — the workspace system prompt (Workspace Context) that Multica injects into every agent run. Push text byte-exact: pass the file content as a raw argv element (e.g. from Python `subprocess`) to `multica workspace update <id> --context`, `multica agent update <id> --instructions`, `multica squad update <id> --instructions` and `multica autopilot update <id> --description`; use `--content-stdin` for `multica skill update` and `multica skill files upsert`. Shell `"$(cat f)"` and `--context-stdin` drop the trailing newline, and `--context` decodes backslash escapes. Read every pushed resource back and diff it against the file.

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
autopilot through `.github/workflows/drunk-live-sync.yml`; `claude_ultra` runs `scripts/drunk-live-sync.py`, which pushes
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
`default` and `claude_ultra` are platform assistants outside the factory roster.
Generated from `agents/*.json` (`model` / `thinking_level` / runtime) — keep in lock-step.


| Agent            | Runtime | Model               | Thinking |
| ---------------- | ------- | ------------------- | -------- |
| arch-reviewer    | claude  | claude-opus-5-5[1m] | xhigh    |
| setup-steward    | claude  | claude-opus-5-5[1m] | xhigh    |
| product-owner    | claude  | claude-opus-5-5[1m] | xhigh    |
| service-architect | claude | claude-opus-5-5[1m] | high     |
| spec-reviewer    | claude  | claude-opus-5-5[1m] | high     |
| dev-leader       | claude  | claude-opus-5-5[1m] | high     |
| pr-reviewer      | claude  | claude-opus-5-5[1m] | xhigh    |
| blog-writer      | claude  | claude-sonnet-5     | high     |
| claude_ultra     | claude  | claude-opus-5-5[1m] | xhigh    |
| dev-backend      | claude  | claude-opus-5-5     | high     |
| release-manager  | claude  | claude-sonnet-5     | high     |
| medium-publisher | claude  | (runtime default)   | —        |
| docs-writer      | codex   | gpt-6.1-sol         | high     |
| devops           | codex   | gpt-6.1-sol         | high     |
| default          | codex   | gpt-6-sol           | high     |
| run-medic        | codex   | gpt-6-luna          | low      |
| issue-janitor    | codex   | gpt-6-luna          | medium   |
| Mika             | codex   | gpt-6-luna          | medium   |


Main development stays on Claude; the work around it rides Codex. Reasoning/judgment roles (orchestration, gates, review) ride opus on the 1M-context tier (`claude-opus-5-5[1m]`) — arch-reviewer, product-owner, pr-reviewer, setup-steward and the `claude_ultra` assistant at `xhigh`, dev-leader, spec-reviewer and service-architect at `high`; `dev-backend` rides opus on the standard tier (`claude-opus-5-5`) at `high`; release-manager and blog-writer ride sonnet. These run on the `Claude (Stevens-Mac-mini.local)` runtime.
the `default` assistant rides `gpt-6-sol` at `high`; devops and docs-writer ride `gpt-6.1-sol` at `high` (devops moved off `gpt-6-sol` after OpenAI returned "Selected model is at capacity" mid-run, and docs-writer was moved live later, recorded here 2026-10-07); `run-medic`, `issue-janitor` and `Mika` ride `gpt-6-luna` (`low` for run-medic — hourly run recovery is pattern-matching over agent task rows, not judgment — `medium` for the other two). These run on the `Codex (Stevens-Mac-mini.local)` runtime: the same host as Claude, because `default`'s monthly insights autopilot shells out to `claude -p "/insights"` and docs-writer renders archify diagrams with the host's Chrome. Thinking is always set explicitly on a Codex agent; left empty, it inherits the host's `~/.codex/config.toml`.