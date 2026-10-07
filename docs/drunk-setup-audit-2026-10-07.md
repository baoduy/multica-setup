# drunk-workspace setup audit — 2026-10-07

Scope: `export/drunk-workspace/` (archify and CHANGELOG excluded), the Multica
v0.6.1 runtime brief and built-in `multica-platform` skill, and 30 days of live
run data (2026-09-07 to 2026-10-07, read-only). Each finding was checked against
the text it cites.

Tags: **[bundle]** = bundle edit, no policy change · **[owner]** = changes or
contradicts a policy, needs the owner's yes · **[live]** = needs a manual live
push (the sync script does not carry it).

## Headline

1. **Host plugins leak into every Claude agent run.** The daemon runs `claude -p`
   without `--setting-sources`, so each run inherits the Mac mini's
   `~/.claude/settings.json` plugins (caveman, ponytail, rtk hook): about 19K
   characters of skill listing plus about 10K of SessionStart hooks (measured
   2026-10-06). That is more than all dedupe savings below combined, and the
   hooks change behaviour (terse caveman prose against `blocker-report`'s
   "everyday words"; ponytail bias on code). Possible fix: agent `custom_args`
   `["--setting-sources","project,local"]`. **Owner decision (2026-10-07):
   keep.** caveman, ponytail and rtk are shared on purpose.
2. **The spec gate cannot learn.** Spec first-pass rate is 15% (8 of 52) against
   55% for PRs (77 of 139). `spec-review-gate` defines no rule ids, so its
   findings carry only `[major]`/`[blocker]`. The retro's rule "same rule id in
   two reworked reviews" can never fire for the gate that reworks most. The
   author also has no pre-submit check: dev members have
   `sdlc-flow-squad-worker-playbook/references/pre-review.md`, product-owner has
   nothing that mirrors the spec gate. [bundle]
3. **Skill descriptions are not in git.** 14 of 29 skills have no frontmatter in
   the bundle, and the live `description` (the text agents see in the skill
   listing) is never pushed: `drunk-live-sync.py` pushes SKILL.md content only,
   and `--check` compares content hashes, so it reports "clean". Example:
   bundle `multica-brainstorming` says "and whenever an ask is underspecified";
   live does not. [bundle + live; script change is repo-root, not setup-steward's]
4. **A policy contradiction.** Policy 04 statement 13 (`04-code-and-spec-review.md:73`)
   says the leader files an out-of-scope defect "unassigned, `Owner` set".
   Policy 07 statement 13a (`07-bug-and-defect-management.md:78`), Policy 09
   statement 1b and `bug-report` say "assigned to `product-owner` at `todo` …
   never left unassigned". [owner]
5. **The weekly retro has never run.** Created 2026-10-07; first fire
   2026-10-12 09:00 SGT. No baseline exists yet.

## 1. Duplication versus reuse

Rule: only Workspace Context is injected into every run. An attached skill
costs only its listing line until the agent opens it. So a copy of a Workspace
Context rule in an agent file is removable; a copy of a skill rule in an agent
file is often the only text the agent reliably reads, and stays.

Removable (always-loaded path):

- `workspace.context.md:26` `Retrigger on done`: about 700 of 1,019 bytes are
  dev-leader's re-arm procedure, already in
  `sdlc-flow-squad-leader-playbook` (SKILL.md:13, `references/review-outcomes.md`,
  `references/recovery.md`). Keep the definition and "members never set or
  clear it". Hits 100% of runs. [bundle]
- `agents/arch-reviewer.md:16,68` restate Workspace Context (`--head`/`--base`,
  flip `todo`→`in_progress`). [bundle]
- `workspace.context.md:38-39` (`--content-file`, bounded reads) repeat the
  runtime brief (`runtime_config_sections.go:262-263,402-411`) and the
  `multica-platform` invariant. Low value; keep only if agents drift without
  them. [bundle]

Keep (looks duplicated, is load-bearing):

- The `done`, never `in_review` paragraph in `docs-writer.md:53` and
  `service-architect.md:34`. The brief tells agents the opposite
  (`runtime_config_sections.go:781`); docs-writer followed the brief on 6 of 7
  tickets before this paragraph existed (CHANGELOG 2026-09-28).
- Squad roster rows that echo member charters: the leader never reads member
  instructions.
- Gate bars quoted in Policies 04/06, `sdlc-flow-delivery-pipeline` and both gate
  skills: mandated by the root `CLAUDE.md`. All numbers are in sync today.

Removable (on-demand path):

- `leader-gitops` (7.4 KB) re-derives `sdlc-gitflow` "Creating branch",
  "Opening PR" and "Conflict protocol" command for command (lines 7-15, 21-29,
  32-37). Keep its gate-check timing, one-PR rule and worktree-lock sections;
  cite the rest. About 3 KB. dev-leader opens it every cycle. [bundle]
- `api-feature-doc-template` and `library-doc-template` (both docs-writer) share
  a byte-identical self-check regex, the `--stat` check and the archify
  paragraph; `service-design-template` carries a drifted third copy. Move to one
  shared reference. [bundle]
- `sdlc-flow-squad-worker-playbook:13` repeats `codegraph:28` (foreground
  `init`). [bundle]
- Policy 03 statement 5 prints the push commands that `sdlc-gitflow` owns. [owner,
  wording only]

Drift and dead references (fix first; these are defects, not style):

- `autopilots/hourly-run-recovery.description.md:115` gives a 3-step `Owner`
  chain and drops "root creator when `creator_type` is member". [bundle]
- Three cites to a heading that no longer exists, `sdlc-flow-delivery-pipeline`
  "Who the human owner is": Policy 10:147, `pr-review-gate/references/multica-flow.md:91`,
  `spec-review-gate/SKILL.md:115`. Policy 10:53 cites "Triggers & status
  discipline", also gone. [bundle; Policy 10 cite is wording only]
- `pulumi-azure-iac-standards:52,106,108` still say mocha;
  `nodejs-typescript-standards:43` flags it as stale (jest is the runner). [bundle]
- `squads/dev-team.md:42` and `agents/release-manager.md:19` carry a
  grandfather clause for DRK-1974/DRK-1978. Both are `done`; delete it. [bundle]

## 2. Wording

Measured, not guessed: rewriting three of the worst passages in caveman/STE
style while keeping every rule id, number and command shrank them 1–11%. The
bundle is dense, not padded. The gains come from structure:

- Split one-sentence walls into bullets or tables:
  `workspace.context.md:10` (1,533 characters, wake triggers) and `:11`
  (handoff line) load on every run; `pr-review-gate/SKILL.md:46` is a
  5,232-character single paragraph (the Testing phase).
- Drop incident narratives from runtime text; keep the rule and its policy
  cite: `workspace.context.md:34` (DRK-1353), `run-medic.md:10,12`,
  `docs-writer.md:50,53` (keep the `in_review` rule itself, drop "(DRK-1785 …)").
  Incident history belongs in the CHANGELOG.
- One term per concept. Workspace Context alone uses ticket ×25, issue ×21,
  sub-task ×10, sub-issue ×5 for one CLI object. "Owner", "resolved owner",
  "human owner", "requester" and "workspace owner" overlap; define them once in
  Workspace Context. Policy cites mix "statement N" (35) and "§N" (14).
- Style rule for runtime text (agents, skills, Workspace Context, autopilots):
  imperative, one idea per sentence, 20 words or fewer, never drop
  not/never/only, numbers, rule ids or commands. Policies stay readable prose
  for humans.

## 3. Structure

Already right (keep): the four `sdlc-flow-*` skills are a clean hub and spokes
with no section overlap; stack skills are split deliberately
(`nodejs-typescript-standards` vs `pulumi-azure-iac-standards`,
`dotnet10-efcore10-standards` vs `dknet-ddd-conventions`); `blocker-report` and
`bug-report` are different artifacts.

Simplify:

- Progressive disclosure, applied evenly. `pr-review-gate` routes to four
  `references/` files; its sibling `spec-review-gate` (23 KB) has none. Same gap:
  `test-driven-development` (20 KB), `architecture-review-sweep` (14 KB). Keep
  SKILL.md as routing plus invariants; move phases to references. [bundle]
- Scripts for deterministic steps. No bundle skill has a `scripts/` directory;
  dedupe fingerprints, AT-contract checks and run-medic detection are prose that
  each run re-derives. Upload them as skill files. [bundle]
- `default` and `claude_ultra` share one instruction text by design (Policy 09
  scope). Their configs differ (codex gpt-6-sol vs Opus xhigh 1M;
  claude_ultra also carries `architecture-review-sweep` and `codegraph`, which
  its own line 1 rules out: "you never … review"). Only the live-sync autopilot
  assigns claude_ultra. Decide whether two assistants are needed. [owner, Policy 09]
- `medium-publisher` has a blank `model` and `thinking_level`, and
  `blog-writer`/`medium-publisher` had 0 runs in 30 days. Set or retire. [owner]
- `arch-reviewer` carries `nodejs-typescript-standards`, but its stack table
  names no plain Node/TS stack. [bundle]

## 4. Skill and agent management practices

Adopt as the bundle's standing rules:

1. Every SKILL.md has frontmatter `name` + `description`, and the description
   says WHAT and WHEN ("Use when …"). The bundle file is the source; the sync
   pushes the description field too. 17 of 29 descriptions lack a WHEN clause.
2. SKILL.md holds routing and invariants; detail goes to `references/` one level
   deep, each routed from SKILL.md. Target under ~10 KB per SKILL.md.
3. Deterministic procedure ships as a script file, not prose.
4. Agent instructions: Goal first (Policy 09 statement 3), one job, a scannable
   `## Never` list, no copy of Workspace Context, no procedure a skill owns.
   Missing Goal: `default`, `claude-ultra`, `medium-publisher`. No Never list:
   9 of 18 agents.
5. Attach a skill only when the charter needs it; confirm with run
   transcripts (`Skill` tool calls in the runtime host's Claude session logs).
6. Runtime text carries no ticket keys or dates except as format examples.
7. Each agent's always-loaded prompt has a budget (target 6K tokens).
   Over it today: dev-leader 7.0K, product-owner 6.2K, docs-writer 6.1K
   (13 KB instructions file), before skill listings.

## 5. Reuse Multica built-ins

- `issue create --property Name=Value` (installed) replaces the
  create-then-`property set` pair for `Owner` and `Retrigger on done`
  (`workspace.context.md:23,26`, leader playbook). A turn that dies between the
  two calls leaves an ownerless child. Release review P3, not applied. [bundle]
- Settings "After PRs merge" → **Don't change** (release review P5). Not
  verified since the v0.6 upgrade; Policy 03 statement 7's rationale still names
  the keyword ban as the only guard. [owner + live setting]
- Wakeup conditions (`--until-pr checks`, `--until-issue`) would replace the
  30-minute CI poll and the `Retrigger on done` mechanism, but the owner turned
  wakeups off on 2026-09-29 (2-second dispatch budget against a remote Postgres).
  Correctly not adopted. Re-test on each release review. [owner, later]
- Fenced `html`/`mermaid` charts in roll-up comments (release review P8): owner
  decision still open.
- Already reused well: `--resolve-properties`, `--fields` + offset paging,
  `run_only` for run-recovery, custom properties for gate state. No bundle skill
  duplicates `multica-platform`.

## 6. Agent performance and quality

Data (30 days): 3,600 runs. Every failure was infrastructure (spend limit,
credits, daemon restart, provider capacity): zero competence failures.
Cancellations are almost all the owner's.

| Gate | Reviews | First pass | Mean rounds | Escalated | Median score |
|---|---|---|---|---|---|
| PR | 139 | 55% | 0.54 | 2 | 9.8 |
| Spec | 52 | 15% | 1.06 | 1 | 9.4 |

Levers, in order of expected effect:

1. Host plugins (headline 1): kept on purpose by the owner.
2. Spec gate rule ids plus an author pre-review that mirrors the gate's
   checklist, like dev's `pre-review.md`. Watch: spec first-pass rate. [bundle]
3. Model and thinking fit. dev-leader runs Opus 1M at 1,240 runs a month with a
   92-second median: mostly routing. Trial `claude-sonnet-5` on dev-leader for
   two weeks; watch stalls and Wake count. pr-reviewer and product-owner at
   `xhigh` are justified by gate weight. [owner]
4. Shorter always-loaded prompts (sections 1-2) on the highest-volume agents:
   dev-leader and product-owner.

## Proposed retro extension: six lenses

Each lens is one command that prints a count. The count is the lens's Watch
metric, so the retro can tell whether a fix moved it.

| Lens | Command (deterministic) | Watch |
|---|---|---|
| 1 Duplication | count Workspace Context sentences repeated verbatim in `agents/`, `squads/`, `skills/`; count dangling skill-heading cites | copies, dangling cites |
| 2 Wording | bytes per agent of Workspace Context + instructions (+ squad briefing for leaders); lines over 600 characters in runtime text; ticket keys in runtime text | always-loaded bytes, long lines, incident keys |
| 3 Structure | SKILL.md over 10 KB without `references/`; skills without frontmatter | counts |
| 4 Practices | agents without Goal line or `## Never`; descriptions without "Use when"; live vs bundle description diff | counts |
| 5 Built-ins | compare `release-reviews/last-run.json` with the latest Multica tag; if behind, say "run `multica-release-review`" — never duplicate it | releases behind |
| 6 Performance | the existing gate digest plus failed tasks; spec and PR first-pass rate, mean rounds | first-pass %, rounds |

The retro's current rules (Policy 09, setup-steward charter) only allow issues
for a cause that recurred at least twice and a bundle file should have
prevented. Static lens findings do not fit that rule. Two ways to add them:

- **A. Report only.** Lenses go in a `## Setup health` section of the retro
  report with week-over-week counts. No new issues. Adds to the charter.
- **B. Lenses may file issues** inside the existing cap of 3, recurring mistakes
  first. Contradicts "fix a problem the evidence does not show" unless the
  charter says a lens count is evidence.

**Owner decision (2026-10-07): A.** Policy 09 v1.34; the lenses run as
`scripts/setup-health.py`. Lens 1 counts 10-word runs shared with the Workspace
Context instead of sentence copies, because exact sentence copies measured 0.

## Applied on 2026-10-07

CHANGELOG entries (f) to (l): Policy 04 statement 13 aligned with Policy 07
13a; the four-step owner chain in run recovery; owner-resolution cites;
jest in the Pulumi standards; the expired DRK-1974/DRK-1978 clause; the
arch-reviewer Workspace Context copies; the retro's setup health step.
Everything else above is open for the owner to pick.
