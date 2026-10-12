# Goal

Weekly issue hygiene (Sunday and Monday 09:00 SGT), for every issue in this workspace across all projects:

- **Rule A** — an open sub-issue under a `done` or `cancelled` parent takes the parent's status.
- **Rule B** — an issue `cancelled` for 7+ days is permanently deleted, children before parents.

The report comment on this run's issue is the only record of what was deleted.

# Constraints

- **Paginate.** `multica issue list` caps at 100 rows regardless of `--limit`. Never trust one call. If the snapshot total is exactly 100, abort the whole run and report a pagination failure. Delete nothing from a partial snapshot.
- **Open statuses only.** Rule A rewrites only `todo`, `in_progress`, `in_review`, `blocked` and `backlog`. Never rewrite an issue that is already `done` or `cancelled`.
- **Architecture findings are exempt from Rule A.** Never rewrite an issue whose title matches `^\[A[0-9]+-[0-9]+\]`, and do not propagate through it to its descendants. The monthly architecture-review autopilot files these `backlog` findings under a run issue that it closes `done` at once; inheriting `done` would close the whole architecture backlog. Match on the title only. Exempt silently.
- **Deletion is permanent.** Rule B deletes only issues with `status == cancelled` AND `updated_at` at least 7 days old. Delete deepest-first. If any descendant is not eligible, skip the parent silently. Never delete an issue that is not eligible to unblock a parent.
- **Blast-radius guard.** If the deletion set exceeds 150 issues, delete nothing and report the count. A set that large means the eligibility logic is wrong. Steady state is single digits.
- **REST for deletion only.** Deletion has no CLI command. `drunkcoding` authorized `DELETE /api/issues/<id>` on 2026-07-27, for this job only; everything else goes through the `multica` CLI. Take the base URL from `multica config show` (`server_url`) or `$MULTICA_SERVER_URL`; never hardcode a host (the runtime's URL is typically `http://127.0.0.1:8080`, not the public one). Authenticate with `$MULTICA_TOKEN`. Never print the token.

# Steps

1. **Snapshot.** Loop `multica issue list --limit 100 --offset N --output json`, adding 100 to N, until a page returns fewer than 100 rows (`has_more` is false). The response is an envelope `{issues, total, limit, offset, has_more}`; read rows from `.issues`. Check the row count against `total`. Build a map `id -> {identifier, title, status, parent_issue_id, updated_at}`.
2. **Rule A.** Walk parents top-down, so a parent made terminal in this run passes its status to its own children. For each open, non-exempt issue whose parent is `done` or `cancelled`, run `multica issue status <id> <parent status>`. Record each change as `identifier | title | old -> new`.
3. **Re-snapshot** with the same loop, because step 2 changed statuses and `updated_at`.
4. **Rule B plan.** For each eligible issue, collect its descendants from the snapshot. It is deletable when every descendant is also eligible. Order the deletable set deepest-first. Apply the blast-radius guard.
5. **Delete** each deletable issue in that order:
   ```
   curl -sS -X DELETE -o /dev/null -w '%{http_code}' \
     -H "Authorization: Bearer $MULTICA_TOKEN" "<server_url>/api/issues/<id>"
   ```
   Any 2xx or 404 is success. On any other code, stop deleting at once and report the failing issue and code; do not continue down the list.
6. **Report.** Post one comment on this run's issue via `--content-file`, then set the run issue to `done`. List only what this run changed, and omit empty sections:
   - Rule A: every status change (`identifier | title | old -> new`).
   - Rule B: the count and the full list of deleted issues, in order, with identifier and title. Never summarize it to a count alone.
   - Errors, aborts, guard trips and steps not completed. Report a partial sweep as partial, never as clean. An aborted run includes its snapshot totals as evidence.

   Leave out everything scanned, exempted or skipped. A run that changed nothing posts one line: `No changes (N issues scanned).`
