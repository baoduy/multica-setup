# Goal

Monthly Claude Code insights report for the workspace owner: run Claude Code's built-in `/insights` command on this runtime, then post its findings and the HTML report on this run's issue. The issue this run creates is the record; its final comment is the deliverable.

# Context

- **Audience**: the workspace owner. Resolve the owner at runtime with `multica workspace member list --output json` and pick the member with role `owner`. Never hardcode a UUID.
- **Runtime**: `/insights` reads the Claude Code session history in `~/.claude` on the machine it runs on. The report covers every Claude Code session on that machine, including Multica agent runs.
- **Read-only.** You never act on the report's suggestions. You never create, assign or change any other ticket.

# Steps

1. Run `claude -p "/insights"` from your working directory, with a timeout of at least 15 minutes. It usually takes about a minute. On success it prints `file:///…/.claude/usage-data/report-<YYYY-MM-DD-HHMMSS>.html`.
2. Take that path, minus the `file://` prefix. Confirm the file exists and was written during this run. If the command fails, prints no path, or the file is missing or old, set this issue `blocked`. Add a `## BLOCKER` comment that quotes the shortest decisive output line, then stop.
3. Read the report HTML and extract its text. Write a summary of at most 25 lines: one line for the period and volume it covers, then each section's two or three key findings in the report's own words, then its top suggestions. Do not invent numbers that the report does not show.
4. Post ONE comment on this issue with `multica issue comment add`. Put the summary in `--content-stdin`. Attach the report with `--attachment <path> --allow-external-file`. End with the report's absolute path on its own line and one member mention of the workspace owner.
5. Set this issue `done`.
