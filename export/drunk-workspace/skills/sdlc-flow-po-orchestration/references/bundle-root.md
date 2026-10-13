# Bundle root — same-repo changes, specs pipelined, builds one at a time

Open this when you are about to create two or more tickets that change the same repo, or when a bundle root you built wakes you (Policy 05 statement 1c). A service is the repo that holds it. Changes to different repos stay separate roots.

## Build it

1. **Plan in the clarification round.** The round that settles scope carries the stage plan as the guess on its scope question: one piece per stage, a piece another builds on first, a docs piece the requester asked for last. The requester's written reply approves it; there is no extra gate.
2. **Root.** The requester's ticket that holds the asks is the bundle root. With no such ticket (a chat request, after the requester said yes to creating one), create ONE root in the repo's project with a plain title, `Owner` set, assigned to yourself, `in_progress`. Either way, label and prefix it by the type of its main change, as at intake.
3. **Sub-issues.** For each piece: `multica issue create --parent <root-id> --stage <n> --status <todo on stage 1, backlog after> --assignee-id <your agent id>`, same project, plain title, no labels, `Owner` copied from the root. Description: the piece as the requester stated it, the repo, the decisions already settled on the root, and `Stage <n> of <root key>; a sub-issue: no release. Build barrier: [P<num>-1] Implementation starts only after stage <n-1> (<key>) is done with its PR merged into dev.` (stage 1 carries no barrier line). A piece's own run then asks only what is still open.
4. **Stage table.** Append `## Stages` (stage · sub-issue · workflow) to the root description, after the `Original request` comment (`multica-brainstorming`). Re-list children: exactly one sub-issue per stage.

## Run it

Stages pipeline with a depth of one (Policy 05 statement 1c): the next slice's clarification, design and spec run while this slice builds; builds merge in stage order. Two wakes do the promoting.

**From a sub-issue's own run**, at Workflow C step 1 (the moment you create its `[P<num>-1] Implementation`):

- Check the stage before yours (`multica issue children <root-id> --output json`): every sub-issue `done` (or `cancelled`) and, for each, `multica issue pull-requests <child-id> --output json` shows a PR into `dev` with `state: merged` (a `cancelled` one, or a question with no change, needs none). Closed, or you are stage 1 → create `[P<num>-1]` at `todo` as usual. Not closed → create it at `backlog`, post ONE comment on your sub-issue (`[P<num>-1] <key> created at backlog: build barrier, stage <n-1> (<key>) not merged yet. <root key> promotes it.`), and end the run; the root promotes it. Your sub-issue stays `in_progress`.
- Only when you created `[P<num>-1]` at `todo`: promote the next stage, `multica issue update <next-id> --status todo`. The promotion is the wake; post no mention. Post ONE comment on the root: `Stage <n> building: [P<num>-1] <key> handed to dev-team. Stage <n+1> promoted: <key>.` Never promote more than one stage ahead: a stage whose `[P<num>-1]` waits at `backlog` promotes nothing.

**From a wake on the bundle root**: `multica issue children <root-id> --output json`.

- **`[P<num>-2]` exists.** Leave it out of the stage scan below. Not `done` yet: nothing to do; end the run with no comment. `done`: verify the `dev`→`main` PR is merged, then flip the root `done` with the final summary (Workflow C step 2).

Otherwise find the lowest stage with a sub-issue that is not `done`/`cancelled`:

- **Its sub-issues are running** (`todo`, `in_progress`, `blocked`) and none holds a `[P<num>-1]` at `backlog`. A `blocked` one is handled on its own ticket; never promote past it. Nothing else to do: end the run with no comment.
- **A sub-issue of it is `in_progress` with its `[P<num>-1]` at `backlog`** (`multica issue children <child-id> --output json`). The stage before it closed. Verify each sub-issue of that stage: `done`, and `multica issue pull-requests <child-id> --output json` shows a PR into `dev` with `state: merged`. Then promote the waiting phase, `multica issue update <phase-id> --status todo`, and the stage after it (its sub-issue `backlog` → `todo`) when one exists. Both promotions are wakes; post no mention. Post ONE comment on the root: `Stage <n> closed (<keys>, PR links). Stage <n+1> building: [P<num>-1] <key> promoted. Stage <n+2> promoted: <key>.` Not verified → resolve on that sub-issue; promote nothing.
- **Its sub-issues wait in `backlog`.** The stage before it closed without promoting (its sub-issue was cancelled, or a question with no change). Verify that stage the same way, then promote: `multica issue update <next-id> --status todo`. Post ONE comment on the root: `Stage <n> closed (<keys>, PR links). Stage <n+1> promoted: <key>.`
- **No such stage.** The last stage closed. Verify it the same way, then release per the bundle-root shape in `SKILL.md`: ONE `[P<num>-2]` at stage `<last + 1>`, `todo`. When no package consumer can observe the change, stage none: flip the root `done` with `no republish: <reason>` in the final summary.
- **A further change for the same repo.** Found while the bundle is open and before `[P<num>-2]` exists: add it as a new last stage at `backlog` and add its row to `## Stages`; it is promoted when the stage before it hands its `[P<num>-1]` to dev-team. Never re-stage a sub-issue that has already started. Once `[P<num>-2]` exists, the change starts a new root.
