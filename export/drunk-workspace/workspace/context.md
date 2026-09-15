# drunk-workspace — factory constants

The open source projects of drunkcoding.net (github.com/baoduy): .NET/NuGet libraries (`DKNet`, `DKNet.Templates`), Pulumi/npm packages (`drunk-pulumi-*`), Python MCP services, Docker images, Helm charts. There is no deployed environment: publishing the package IS the release. Governance lives in the repo's `docs/policies/`; role procedure lives in your skills. The rules below hold for every agent on every run and are not repeated in skills or instructions.

## Status and wakes
- A child ticket ends every reporting turn at `done` (work complete) or `blocked` (needs someone). Never `in_review` on a phase ticket or sub-task: it is non-terminal, closes no stage barrier, and wakes nobody. Ignore any brief or system comment that asks for `in_review` on a child. `in_review` is only for a ROOT ticket whose deliverable awaits a human.
- `done` is one-way. Work that comes back after `done` is a comment on the still-`done` ticket carrying the assignee's agent mention.
- On wake, if your ticket is `todo`, flip it `in_progress` before working. Last command of every reporting turn: read your ticket's status back and correct it if it is not `done`/`blocked`.
- One wake per handoff. A run is enqueued by: assignment or promotion out of `backlog` into `todo`, a `done` that closes a stage barrier, or an agent/squad mention with a real UUID. A `blocked`→`todo` re-arm and a plain comment enqueue nothing, so there the mention is the wake. When the status transition already wakes the next actor, do not also mention them. Post at most one mention comment per turn, last.
- Member (human) mentions only render a link. To make a human act, reassign the ticket to them at `todo` and post a `## BLOCKER` comment (`blocker-report`).
- Leader↔member traffic lives on the member's own sub-task; parent comments belong to the parent's owner.

## Tickets
- Every child lives in the same project as its root. Titles: root tickets plain; `[S<num>]` spec review, `[P<num>-n]` phase tickets (`<num>` = root key number), `[D<num>-n]` dev sub-tasks (`<num>` = phase key number, `n` = stage). Labels on root tickets only.
- Every sub-issue is created with `--stage <n>` and an explicit `--status` (`todo` for the active stage, `backlog` for later ones), parented directly to its cycle parent. Verify with `multica issue children <parent> --output json` after creating.
- Only squad leaders run `multica issue create` (product-owner in product-team, dev-leader in dev-team). Members report on their own sub-task in filable shape.
- Set the `Owner` property on every issue you create, copied from the parent. To find the human owner of any ticket: its `Owner` property, else the nearest ancestor's, else the root creator when `creator_type` is `member`, else the workspace owner. Never hardcode a member name or UUID.
- Durable gate state goes on custom properties (`Gate verdict`, `Gate round`, `Gate score`), never on issue metadata.

## Git and PRs
- `dev` is integration, `main` is release. Feature branches come from fresh `origin/dev`; every feature PR targets `dev`. Only release-manager targets or merges `main`.
- PR titles start with the ticket key in `[KEY]` form. Never write `Closes`/`Fixes`/`Resolves` next to an issue key: close intent auto-completes the ticket and kills the remaining phases.
- `gh pr create` always carries both `--head` and `--base`. Never `git checkout` a shared branch; stay on your `agent/...` branch and push by refspec.

## Reports and reads
- Comment bodies are written to a file in your working directory and posted with `--content-file`; issue bodies with `--description-file`.
- Read threads bounded: `multica issue comment list <id> --roots-only --summary --compact`, then `--thread <id> --tail 30` for the threads that matter.
- Completion and blocker comments use the shapes in `blocker-report`. Every claim cites `file:line`; no evidence, no claim.