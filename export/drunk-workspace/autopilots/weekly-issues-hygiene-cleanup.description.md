# Goal

Weekly issue hygiene (Sunday and Monday 09:00 SGT), for every issue in this workspace across all projects:

- **Rule A** — an open sub-issue under a `done` or `cancelled` parent takes the parent's status.
- **Rule B** — an issue `cancelled` for 7+ days is listed as a deletion candidate, children before parents. The workspace owner deletes; this job deletes nothing (the platform lets an agent delete only the issues it created).

# Constraints

- **Paginate.** `multica issue list` caps at 100 rows regardless of `--limit`. Never trust one call. If the snapshot total is exactly 100, abort the whole run and report a pagination failure. List no candidate from a partial snapshot.
- **Open statuses only.** Rule A rewrites only `todo`, `in_progress`, `in_review`, `blocked` and `backlog`. Never rewrite an issue that is already `done` or `cancelled`.
- **Architecture findings are exempt from Rule A.** Never rewrite an issue whose title matches `^\[A[0-9]+-[0-9]+\]`, and do not propagate through it to its descendants. The monthly architecture-review autopilot files these `backlog` findings under a run issue that it closes `done` at once; inheriting `done` would close the whole architecture backlog. Match on the title only. Exempt silently.
- **Deletion is permanent, so the list must be exact.** Rule B lists only issues with `status == cancelled` AND `updated_at` at least 7 days old, deepest-first. If any descendant is not eligible, leave the parent out silently.
- **Blast-radius guard.** If the candidate set exceeds 150 issues, list none and report the count. A set that large means the eligibility logic is wrong. Steady state is single digits.
- **Never delete.** No `multica issue delete`, no REST call. Everything goes through the `multica` CLI.

# Steps

1. **Snapshot.** Loop `multica issue list --limit 100 --offset N --output json`, adding 100 to N, until a page returns fewer than 100 rows (`has_more` is false). The response is an envelope `{issues, total, limit, offset, has_more}`; read rows from `.issues`. Check the row count against `total`. Build a map `id -> {identifier, title, status, parent_issue_id, updated_at}`.
2. **Rule A.** Walk parents top-down, so a parent made terminal in this run passes its status to its own children. For each open, non-exempt issue whose parent is `done` or `cancelled`, run `multica issue status <id> <parent status>`. Record each change as `identifier | title | old -> new`.
3. **Re-snapshot** with the same loop, because step 2 changed statuses and `updated_at`.
4. **Rule B candidates.** For each eligible issue, collect its descendants from the snapshot. It is a candidate when every descendant is also eligible. Order the candidates deepest-first. Apply the blast-radius guard.
5. **Report.** Post one comment on this run's issue via `--content-file`, then set the run issue to `done`. List only what this run changed, and omit empty sections:
   - Rule A: every status change (`identifier | title | old -> new`).
   - Rule B: the count and the full list of deletion candidates, in order, with identifier and title, then the one command that deletes them in that order: `multica issue delete <key> <key> ... --yes`. Never summarize the list to a count alone. When the list is not empty, end the comment with one member mention of the workspace owner.
   - Errors, aborts, guard trips and steps not completed. Report a partial sweep as partial, never as clean. An aborted run includes its snapshot totals as evidence.

   Leave out everything scanned, exempted or skipped. A run that changed nothing and lists no candidate posts one line: `No changes (N issues scanned).`
