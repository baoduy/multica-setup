# Goal

Find what the drunk agents got wrong in the last 7 days, more than once, and file one fix issue per recurring problem for setup-steward. File one issue per upstream change too: a new archify release, new Multica releases. Report the setup's health counts. The issue this run creates is the record, and its final comment is the report. **You change nothing in the repo or the live workspace in this run.**

# Context

- **Audience**: the workspace owner (resolved per the Workspace Context, **Tickets**).
- **Project**: every issue you file goes to `drunk-setup` (id from `multica project list --output json`, matched by title), assigned to `setup-steward` (id from `multica agent list --output json`).
- **Setup repo**: `gh repo clone baoduy/multica-setup setup -- --branch dev` into your working directory. Read `setup/CLAUDE.md`. You read the bundle at `setup/export/drunk-workspace/` to name the file a fix belongs in; you never edit it here.

# Step 1: Gate digest

Extract the Part 2 script from the monthly insights autopilot, exactly as written there, and run it for 7 days:

```bash
awk '/^# Part 2/{p=1} p&&/^```bash$/{f=1;next} f&&/^```$/{exit} f' \
  setup/export/drunk-workspace/autopilots/monthly-claude-code-insights.description.md > gate-digest.sh
DAYS=7 bash ./gate-digest.sh > digest.json
```

Never rewrite or re-implement it. `digest.json` gives, per gate, the reworked keys, mean rounds, escalations and `top_findings` (rule ids and severities named in rework comments).

# Step 2: Failed and stranded runs

For every agent in `multica agent list --output json`, read `multica agent tasks <id> --output json` and keep tasks created in the last 7 days with status `failed`. Group them by agent and by the first line of the error. Also list the issues titled `Run recovery needs attention` created in the last 7 days (`multica issue list --output json`, paginate by 100).

# Step 3: Pick the problems

A problem qualifies only when the same cause shows up **at least twice** in the window: the same rule id in two reworked reviews, the same agent failing the same way twice, the same handoff stalling twice. One-offs go in the report, not in an issue. A transient infrastructure error (rate limit, runtime offline) is run-medic's, never a setup problem.

For each qualifying problem, read the agent instructions, skill or policy in the bundle that should have prevented it, and say what text is missing or wrong. If you cannot point at a file, it is not a setup problem: report it, file nothing.

Dedupe: list the open issues in `drunk-setup` first. A problem already covered by an open issue gets a comment there with the new evidence, not a second issue.

File at most **3** issues per run in this step, most frequent first. Step 7's upstream issues are outside this cap and need no recurrence. Never file one that changes a gate bar, cap, weight or severity deduction: report it to the owner instead.

# Step 4: File each issue

`multica issue create --title "[Enhance] <agent or skill>: <problem>" --project <drunk-setup id> --assignee-id <setup-steward id> --description-file ./issue-<n>.md`. The description has four parts:

- **Problem**: one sentence.
- **Evidence**: issue keys, counts, rule ids, quoted error lines. Never UUIDs.
- **Where**: the bundle file(s) and section that should change, and what the text should say.
- **Watch**: the metric that should move if the fix works (for example `pr` mean rounds, or the count of a rule id in `top_findings`).

# Step 5: Check last weeks' fixes

List `drunk-setup` issues set `done` in the last 28 days. For each, compare its **Watch** metric now with the value its Evidence quoted. Say in the report whether it moved, did not move, or cannot be measured yet. A fix that did not move after 3 weeks gets one line asking the owner whether to revert it.

# Step 6: Setup health (report only)

Run the lens script, exactly as written in the repo. Never rewrite or re-implement it:

```bash
(cd setup && python3 scripts/setup-health.py --digest ../digest.json) > health.json
```

It prints one count per lens. A lens is a standing check of the setup itself, not a recorded mistake:

| Lens | Counts |
|---|---|
| 1 Duplication | 10-word runs shared with the Workspace Context, identical agent instructions, dangling `references/` paths |
| 2 Wording | agents over the 24,000-byte always-loaded budget, lines over 600 characters, ticket keys in always-loaded text |
| 3 Structure | SKILL.md over 10 KB with no `references/`, skills with no frontmatter |
| 4 Practices | agents with no Goal line or Never list, skill descriptions with no "Use when", bundle descriptions that differ from live |
| 5 Built-ins | Multica releases since the last release review |
| 6 Performance | per gate: first-pass %, mean rounds, escalations |

Find the previous `Weekly Setup Retro` issue in `drunk-setup` and read the `health.json` block in its report comment. Compare each count with it. No previous retro, or its report has no `health.json` block: report the counts with "no baseline"; that is not a failure. A lens never files an issue and never comments on one: lens findings are for the owner. Step 7 reads lens 5 for its own check. If the script fails, write its error line under `## Setup health` and go on: a lens failure is not a `## BLOCKER`.

# Step 7: Upstream releases

Two checks. Each files at most one issue in `drunk-setup`, assigned to `setup-steward`, the way step 4 does. Before filing, list the open issues in `drunk-setup`: an open issue with the same title prefix gets a comment with the new tag instead.

- **archify.** Compare the `version` in `setup/export/drunk-workspace/skills/archify/skill-release.json` with `gh api repos/tt-a1i/archify/releases/latest --jq .tag_name`, ignoring a leading `v`. Behind: file `[Enhance] archify: sync to <tag>`. The description names both versions and the release URL.
- **Multica.** Read `5_builtins` in `health.json`. A non-empty `releases_since`: file `[Enhance] multica: adopt releases after <last_reviewed_tag>`. The description lists the tags. `releases_since` null (the script or `gh` failed): no issue, one line in the report.

These issues need no Evidence or Watch part: setup-steward runs the release review on the issue. A `gh` failure here is one report line, not a `## BLOCKER`.

# Report

Post ONE comment on this issue with `multica issue comment add --content-stdin`:

- `## Filed`: each issue key and title, step 7's included, or "none".
- `## One-offs`: problems seen once, one line each.
- `## Previous fixes`: step 5, one line each.
- `## Setup health`: step 6. One line per lens: the count now, last week's, and the change. For a count that got worse, name up to 3 files from the output. Then the full `health.json` in a fenced `json` block, which next week's retro reads. Releases listed under lens 5 are step 7's issue.
- `## For the owner`: gate-change proposals and anything you could not place, or omit the section.
- `## BLOCKER`: only if a step failed. Name the step and quote its output line.
- End with one member mention of the workspace owner.

Then set this issue `done`, or `blocked` if a step failed.
