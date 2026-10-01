# Goal

Monthly report for the workspace owner, in two parts:

1. Claude Code `/insights`: the usage report for this runtime.
2. Multica release review: which new `multica-ai/multica` releases would improve the drunk and mx workspace bundles, or break them.

The issue this run creates is the record, and its final comment is the deliverable. **Report only.** You never apply a proposal, edit a bundle, commit, push, or change the live workspace.

# Context

- **Audience**: the workspace owner. Resolve the owner at runtime with `multica workspace member list --output json` and pick the member with role `owner`. Never hardcode a UUID.
- **Runtime**: `/insights` reads the Claude Code session history in `~/.claude` on the machine it runs on. The report covers every Claude Code session on that machine, including Multica agent runs.
- **Read-only.** The only `multica` writes you make are this issue's comment and its status. You never create, assign or change any other ticket.
- **Independent parts.** Run part 1 first. If one part fails, still run and report the other.

# Part 1: Claude Code insights

1. Run `claude -p "/insights"` from your working directory, with a timeout of at least 15 minutes. It usually takes about a minute. On success it prints `file:///…/.claude/usage-data/report-<YYYY-MM-DD-HHMMSS>.html`.
2. Take that path, minus the `file://` prefix. Confirm the file exists and was written during this run. If the command fails, prints no path, or the file is missing or old, part 1 has failed. Keep the shortest decisive output line for the BLOCKER.
3. Read the report HTML and extract its text. Write a summary of at most 25 lines: one line for the period and volume it covers, then each section's two or three key findings in the report's own words, then its top suggestions. Do not invent numbers that the report does not show.

# Part 2: Multica release review

1. Clone the setup repo into your working directory: `gh repo clone baoduy/multica-setup multica-setup -- --branch dev`. Work only inside that clone.
2. Read `multica-setup/CLAUDE.md` and `multica-setup/.claude/skills/multica-release-review/SKILL.md`. Follow the skill's steps 1 to 5, with these overrides:
   - **Skip step 6 entirely.** Do not write `release-reviews/last-run.json`. Do not commit or push. The state advances only when the owner runs the skill themselves.
   - Write the report file inside the clone (`release-reviews/<run_date>_<range>.md`). It is attached to the comment, never committed.
   - Do not ask which proposals to implement. List the proposal titles in the comment instead.
   - If the skill finds no release after `last_reviewed_tag`, part 2 is one line: "No new Multica releases since <tag>." Write no report file.
3. Check the vendored archify skill, as `CLAUDE.md` requires on every release review. Compare the `version` in `export/drunk-workspace/skills/archify/skill-release.json` with `gh api repos/tt-a1i/archify/releases/latest --jq .tag_name`, ignoring a leading `v`. Report one line: "archify up to date at <version>" or "archify <bundle version> behind upstream <tag>". Do not sync.
4. If the clone, `gh` or the skill fails, part 2 has failed. Keep the shortest decisive output line for the BLOCKER.

# Report

Post ONE comment on this issue with `multica issue comment add` and `--content-stdin`:

- `## Claude Code insights`: the part 1 summary and the HTML report's absolute path on its own line.
- `## Multica release review`: the installed `multica` version, the range reviewed, the skill's Summary bullets, the proposal titles in rank order with their type, every breaking change to verify, and the archify line. If nothing is new, give the one line plus the archify line.
- `## BLOCKER`: only if a part failed. Name the part and quote its output line.
- End with one member mention of the workspace owner.

Attach the insights HTML with `--attachment <path> --allow-external-file`, and the release review report with a second `--attachment <path>` when it exists.

Then set this issue `blocked` if either part failed, or `done` if both succeeded.
