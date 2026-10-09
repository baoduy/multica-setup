# Bundle root — same-repo changes, one stage at a time

Open this when you are about to create two or more tickets that change the same repo, or when a bundle root you built wakes you (Policy 05 statement 1c). A service is the repo that holds it. Changes to different repos stay separate roots.

## Build it

1. **Plan in the clarification round.** The round that settles scope carries the stage plan as the guess on its scope question: one piece per stage, a piece another builds on first, docs last. The requester's written reply approves it; there is no extra gate.
2. **Root.** The requester's ticket that holds the asks is the bundle root. With no such ticket (a chat request, after the requester said yes to creating one), create ONE root in the repo's project with a plain title, `Owner` set, assigned to yourself, `in_progress`. Either way, label and prefix it by the type of its main change, as at intake.
3. **Sub-issues.** For each piece: `multica issue create --parent <root-id> --stage <n> --status <todo on stage 1, backlog after> --assignee-id <your agent id>`, same project, plain title, no labels, `Owner` copied from the root. Description: the piece as the requester stated it, the repo, the decisions already settled on the root, and `Stage <n> of <root key>; a sub-issue: no release.` A piece's own run then asks only what is still open.
4. **Stage table.** Append `## Stages` (stage · sub-issue · workflow) to the root description, after the `Original request` comment (`multica-brainstorming`). Re-list children: exactly one sub-issue per stage.

## Run it

Every wake on the bundle root: `multica issue children <root-id> --output json`, then find the lowest stage with a sub-issue that is not `done`/`cancelled`.

- **Its sub-issues are running** (`todo`, `in_progress`, `blocked`). A `blocked` one is handled on its own ticket; never promote past it. Nothing else to do: end the run with no comment.
- **Its sub-issues wait in `backlog`.** The stage before it closed. Verify each sub-issue of that stage: `done`, and `multica issue pull-requests <child-id> --output json` shows a PR into `dev` with `state: merged` (a `cancelled` one, or a question with no change, needs none). Then promote: `multica issue update <next-id> --status todo`. The promotion is the wake; post no mention. Post ONE comment on the root: `Stage <n> closed (<keys>, PR links). Stage <n+1> promoted: <key>.`
- **No such stage.** The last stage closed. Verify it the same way, then release per the bundle-root shape in `SKILL.md`: ONE `[P<num>-2]` at stage `<last + 1>`, `todo`, or `no republish: <reason>` in the final summary.
- **A further change for the same repo.** Found while the bundle is open and before `[P<num>-2]` exists: add it as a new last stage at `backlog` and add its row to `## Stages`; the next wake promotes it once the stages before it close. Never re-stage a sub-issue that has already started. Once `[P<num>-2]` exists, the change starts a new root.
