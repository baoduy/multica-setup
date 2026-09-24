# CLAUDE.md — managing the `mx-workspace` Multica export

This folder is a **Multica Platform workspace export**: the versioned source of the
agents, squads, and skills that run the `sdlc-flow` software-factory pipeline. Editing
files here changes what the platform runs after the bundle is re-imported. Read
[`README.md`](./README.md) first for the *flow*; this file is the *maintenance contract*
for the definitions themselves.

> Golden rule: **every agent, squad, and skill must be listed in `manifest.json`.** A
> file the manifest does not reference is invisible to import. When you add or rename a
> definition, update its file **and** its manifest entry in the same change.

> README-mirror rule: **`README.md` is hand-maintained documentation, not auto-derived —
> every change to the definitions must leave it correct in the SAME change.** This applies
> whether you *modified* files directly, *imported* a bundle that changed them, or
> *exported* a fresh bundle from the live workspace (the export overwrites the JSONs, so
> the README can silently drift out of sync). After any of the three, reconcile the
> affected README sections below and re-run the validators. Treat a stale README as a
> broken build.
>
> | What changed | README section(s) to reconcile |
> |---|---|
> | Skill added/removed/rebound on an agent (`skill_names[]`) | §5 **Skills per agent** (row + count) · §5 **Full skill catalog** (`Bound to`) · §5 Coverage count |
> | New or deleted skill file | §5 **Full skill catalog** (add/remove the row under its family) · §5 Coverage count |
> | Agent added or removed | Legend (§ top) · flow diagrams (§1/§2) · §5 Skills-per-agent · §6 runtimes & models |
> | Agent re-tiered (`model`/`thinking_level`) | §6 **runtimes & models** table (+ token-budget rationale if the tier class changed) |
> | Squad membership / stage change | flow diagrams (§1/§2) · §4 human touch points if a human step moved |
> | Flow / stage / ownership change | §1/§2 diagrams · §4 human touch points · §5 layer model if a skill's authority changed |

## Layout

```
manifest.json           registry: version, scope, source_workspace_id, agents[], squads[], skills[], autopilots[]
agents/<name>.json      one agent definition  (+ <name>.avatar.png alongside it)
squads/<name>.json      one squad definition  (members reference agents by name)
skills/<name>/SKILL.md  a skill (procedure/contract); skills/<name>/config.json if present
autopilots/<slug>.json  one autopilot (title, prompt/description, mode, assignee, triggers) —
                        exported per-autopilot (--scope autopilot), never auto-bundled by `all`;
                        priority is not capturable via the CLI and must be re-set in the UI
```

Naming is uniform: the file basename IS the identity (`agents/release-manager.json` →
agent `release-manager`). Keep basename, the JSON `name`, and the manifest `name` identical.

## Agent definition (`agents/<name>.json`)

Fields that matter when authoring (copy an existing agent as the template — `release-manager`
for git/ops agents, `product-owner` for orchestration agents):

| Field | Notes |
|---|---|
| `name` | kebab-case; matches filename and manifest. |
| `description` | one line; shown in listings. |
| `instructions` | the agent's **identity + scope + hard limits** only. Persona, what it owns, what it must refuse, and pointers to its skills. Keep it tight (~2–8k chars). **Do NOT** inline flow/procedure that belongs in a skill — see Layering. |
| `model` / `thinking_level` | drive cost — see **Model & token budget**. |
| `source_runtime_provider` | `claude` for every agent in this workspace (must match the model family). |
| `visibility` | `workspace` for shared agents. |
| `permission_mode` | `public_to` + `invocation_targets` = who may invoke it. |
| `skill_names[]` | skills this agent loads; each must exist under `skills/`. |
| `avatar_file` | `agents/<name>.avatar.png` (see **Avatars**). |
| `source_id` | live-workspace UUID. Leave `""` for a **new** (not-yet-imported) agent; the platform assigns it on first import. If import rejects an empty value, generate a UUID and use the SAME value in the JSON and the manifest entry. |
| `source_runtime_id` | the runtime the agent runs on; reuse the value siblings use. |

Instruction discipline (learned conventions, keep them):
- Report completion via **status only** — `done` fires the stage barrier; on a phase/sub
  ticket **never** `in_review` (wakes nobody, strands the pipeline). `blocked` + a mention
  comment = needs help.
- **Mentions are actions.** An agent mention (`[@name](mention://agent/<uuid>)`, real UUID)
  enqueues a run; a member (human) mention only notifies. Never agent-mention in FYI/done
  comments. Resolve UUIDs at runtime (`multica agent list --output json`) — don't trust a
  hardcoded UUID in prose. **Mentions are NOT deduped** — one mention, one run, even when
  the target is already `queued` or `running`; post ONE mention comment per turn.
- **Members never flip their own sub-task out of `done`.** A stage barrier re-fires on every
  re-entry into `done`; only the LEADER re-triggers fix work, by flipping the sub-task
  `in_progress --no-start` (adding the blocked gate's key to `Retrigger on done`, comma-separated when there are several) and then
  posting the ONE mention. Members write only on their own ticket and mention only their
  leader — no member-to-member traffic.
- Git boundaries are deliberate: only the squad leaders (`dev-leader`, `qc-leader`) cut
  feature branches and open PRs into `dev` — inline, per `leader-gitops`, never as
  Branch/PR sub-tasks; only `release-manager` opens/merges the `dev`→`main` release.
  `main` = SANDBOX, `dev` = INTEGRATION. Production tagging is automatic in CI/CD
  downstream — no agent does it.

## Squad definition (`squads/<name>.json`)

```
name, description, instructions (leader briefing — members table, stage tables, caps,
  and the VERIFIED per-workspace mention directory with real UUIDs),
avatar_url  ("emoji:🦍" form for squads),
leader_name (must be one of the members),
members[]   ({ agent_name, role: "leader" | "member" })
```

Every `agent_name` in `members[]` must be a real `agents/<name>.json`. The squad briefing is
Layer 3 (see README §5): squad membership, stage tables, and the mention directory live here —
NOT the shared flow.

## Avatars

- Format: **256×256 RGBA PNG**, flat **Twemoji animal** icon (the whole set is Twemoji:
  🦉 product-owner, 🐺 dev-backend, 🐳 release-manager, 🐼 default, …). Squads use an
  emoji directly via `avatar_url: "emoji:🦍"`.
- Generate a new one from the official Twemoji SVG so it matches the set exactly:
  ```sh
  python3 -m venv /tmp/tw && /tmp/tw/bin/pip install -q cairosvg
  # find the codepoint at https://emojipedia.org (whale 🐳 = 1f433)
  curl -sL -o /tmp/a.svg https://cdn.jsdelivr.net/gh/jdecked/twemoji@latest/assets/svg/<codepoint>.svg
  /tmp/tw/bin/python -c "import cairosvg;cairosvg.svg2png(url='/tmp/a.svg',write_to='agents/<name>.avatar.png',output_width=256,output_height=256)"
  file agents/<name>.avatar.png   # must say: PNG image data, 256 x 256, 8-bit/color RGBA
  ```
- Pick an unused animal; keep it semantically apt (release-manager = 🐳 whale = Docker/
  ships-images). At runtime the platform takes the PNG via `multica agent avatar <id>`.

## Model & token budget

Section 6 of `README.md` is the authoritative model/thinking table — **keep it in sync with
the agent JSONs** (it plans the token budget). Assign by role, cheapest tier that fits:

| Role class | Model / thinking | Why |
|---|---|---|
| Judgment & orchestration (product-owner, spec-reviewer, dev-leader) | `claude` opus, `high`/`xhigh` | reasoning-heavy; correctness dominates cost. |
| Implementation (dev-backend, qc-tester) | `claude` opus (dev-backend) / sonnet (qc-tester), `high`/`xhigh` | writes code/tests. |
| Mechanical git/ops (**release-manager**, qc-runner) | `claude` sonnet, `medium` | deterministic CLI steps, but the end-of-turn status flip is correctness-critical — a lighter model dropped it and stranded the pipeline. Squad git-flow (branch cut, cycle PR) is NOT a separate agent: the leaders run it inline via `leader-gitops`. |
| Review gates (pr-reviewer, qc-leader) | `claude` sonnet, `high`/`medium` | scoped judgment over a diff. |

When you add or re-tier an agent: update `model`/`thinking_level` in its JSON **and** the
README §6 row in the same change, so the budget picture stays truthful.

## Editing discipline (layering — see README §5)

- **Flow change** (stages, ownership, branch strategy) → edit `skills/sdlc-flow-delivery-pipeline` only.
- **One role's procedure** → edit that role's skill (`sdlc-flow-po-orchestration`, `pr-review-gate`, …).
- **Squad membership/stages/mentions** → edit that squad briefing.
- **Agent identity/hard limits** → edit that agent's `instructions` — never re-inflate it with flow detail.
- Surface a conflict between two definitions rather than blending them; pick the more recent/tested and flag the other.

## Adding a new agent — checklist

1. `agents/<name>.json` — copy a sibling of the right role class; set name/description/
   instructions/model/thinking/skills/avatar_file; `source_id: ""`.
2. `agents/<name>.avatar.png` — 256×256 Twemoji animal (pipeline above).
3. `manifest.json` — add the `agents[]` entry (name, file, source_id `""`, source_runtime_id,
   source_runtime_provider, skill_names, had_secrets:false).
4. If it joins a squad: add it to `squads/<squad>.json` `members[]` and the briefing's mention
   directory (real UUID after import).
5. If a pipeline stage assigns it: update `skills/sdlc-flow-delivery-pipeline` (stage table +
   diagram) and the owning role skill's promotion logic.
6. README (see the **README-mirror rule**): add it to the Legend, the flow diagrams, the
   **§5 Skills per agent** + **Full skill catalog** tables (with its `skill_names[]`), and the
   **§6 runtimes & models** table — all in this same change.
7. Validate: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('agents/*.json')+['manifest.json']+glob.glob('squads/*.json')]; print('all valid')"`.
8. Reconcile the README against the JSONs — every agent's `skill_names[]` and count must
   match §5, and the §5 coverage total must equal the number of skills under `skills/`:
   ```sh
   python3 -c "
   import json,glob,os,re
   ags={json.load(open(f))['name']:(json.load(open(f)).get('skill_names') or []) for f in glob.glob('agents/*.json')}
   sk={os.path.basename(os.path.dirname(p)) for p in glob.glob('skills/*/SKILL.md')}
   r=open('README.md').read()
   bad=[a for a,s in ags.items() if not re.search(re.escape(a)+r' \\('+str(len(s))+r'\\)',r)]
   print('agent count mismatches:',bad or 'none'); print('skills on disk:',len(sk))"
   ```

## Sync to the platform

The manifest + files mirror a live workspace (`source_workspace_id`). Apply changes with the
Multica CLI (the platform built-in skills cover all `multica` CLI commands):

- Agents: `multica agent create` / `update <id>`, `multica agent avatar <id>`,
  `multica agent skills set <id>`.
- Squads: the `multica` squad commands; members reference agents by name.
- Skills: `multica skill import` / `multica skill files`.

Re-import through the same export/import tooling that produced this bundle when applying it
wholesale. After any agent is re-created, its UUID changes — **re-verify squad mention
directories** (they pin UUIDs) and resolve IDs at runtime everywhere else.

**After every import or export, reconcile the README (README-mirror rule).** An `export`
overwrites the JSONs from the live workspace and an `import` rewrites them from a bundle —
either can change `skill_names[]`, models, or the agent roster without touching `README.md`.
Diff before/after (`git diff -- agents/ squads/ skills/ manifest.json`), then update the
README sections the mapping table lists and re-run the step-8 reconcile check above. Commit
the definition change and its README update together.
