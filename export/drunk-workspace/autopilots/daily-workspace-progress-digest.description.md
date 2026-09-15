# Goal

Daily stall sweep for drunk-workspace: find tickets that stopped moving, re-wake the agent that already owns them when the fix is mechanical, and post ONE digest to the workspace owner for everything else. The issue this run creates is the audit record; its final comment is the deliverable.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, role `owner`; never a hardcoded UUID).
- **Scope** — every open issue in this workspace, all projects. `multica issue list` caps at 100 rows: paginate `--limit 100 --offset N` until a page returns fewer than 100. Read comments bounded (`--roots-only --summary --compact`).
- **Read-only except nudges.** You never change a status, never create or cancel tickets, never assign anything. The only write besides the digest is a nudge comment.

# Stall rules

A ticket is stalled when one of these holds and it has had no run in the last 24 hours (`multica issue runs <id> --active --output json` empty, latest run older than 24h):

1. **Parked gate** — a `Review:` or `Spec review:` sub-task `blocked` with `Gate verdict` = REWORK or POLISH for more than 24h. Nudge: comment on the IMPLEMENTER's sub-task the findings went to (the `Build:`/`Docs:`/`Update:` sibling) with that implementer's agent mention: "pr-reviewer's findings of <date> are unanswered; fix, push, and report here ending with pr-reviewer's mention."
2. **Unpromoted stage** — a parent whose lowest unfinished stage is entirely `done`/`cancelled` while the next stage sits in `backlog` for more than 6h. Nudge: comment on the PARENT with the parent assignee's mention (agent, or squad mention for a squad-assigned parent): "Stage <n> is complete; promote stage <n+1>."
3. **Finished but open** — a root or phase ticket whose children are all terminal, whose release PR (if any) is merged, and which still sits `in_progress` or `blocked` for more than 12h. Nudge: comment on it with its assignee's mention: "Every child is terminal; finalize."
4. **Parked with a human** — a ticket assigned to a member at `todo` for more than 48h (gate handoff, escalation, unassigned defect). No nudge; digest only.
5. **Unassigned** — an open ticket with no assignee for more than 24h. No nudge; digest only.
6. **Silent in_progress** — `in_progress` with no active run and no comment for more than 24h, not covered above. Nudge: comment with the assignee's mention: "No run for 24h; resume or set `blocked` with a `## BLOCKER`."

Exempt: issues titled `^\[A\d+-\d+\]` (architecture findings), autopilot run issues, and anything `done`/`cancelled`.

# Nudge discipline

- One nudge per stalled ticket per day; before posting, scan its roots for a nudge from you in the last 24h and skip if found.
- A nudge carries exactly ONE agent (or squad) mention, the current assignee or leader of that ticket, and states the observed stall in one line. Never mention a human; never mention an agent that is not the ticket's owner.
- The mention is the wake. Do not change statuses.

# Digest

Post ONE comment on this run's issue: a table `ticket · rule · stalled since · owner · action taken (nudged / digest only)`, then the tickets parked with humans or unassigned (rule 4 and 5) as a short list with the decision each one waits on. Mention the workspace owner (member mention) once, at the end. If nothing is stalled, say so in one line. Then flip this issue `done`.
