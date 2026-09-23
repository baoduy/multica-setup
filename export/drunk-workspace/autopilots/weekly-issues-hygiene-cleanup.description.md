# Goal

Weekly issue hygiene (Sunday and Monday 09:00 SGT): propagate a terminal parent status onto forgotten open sub-issues, then permanently delete cancelled issues that have been cancelled for 7+ days, children before parents.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, entry with role `owner`; never a hardcoded UUID). The issue this run creates IS the audit record; the report comment is the deliverable and the only record of what was destroyed.
- **Scope** — every issue in workspace `4539126d-0687-4993-8852-3554b7c5fb50`, all projects.
- **Constraints**
   - `multica issue list` CAPS AT 100 ROWS regardless of `--limit`. ALWAYS paginate with `--limit 100 --offset N` until a page returns fewer than 100 rows. The workspace has \~667 issues. Never trust a single unpaginated call. If the snapshot total is exactly 100, abort the whole run and report a pagination failure — do not delete anything from a partial snapshot.
   - Rule A rewrites ONLY open statuses: `todo`, `in_progress`, `in_review`, `blocked`, `backlog`. Never rewrite an issue already `done` or `cancelled`.
   - **Rule A exemption — architecture-review findings.** NEVER rewrite an issue whose title matches `^\[A[0-9]+-[0-9]+\]` (e.g. `[A912-3] [DKNET-AGG-002] ...`). The monthly architecture-review autopilot files these `backlog` findings as children of its run issue, and it closes that run issue `done` the moment the sweep finishes — the parent being terminal says nothing about the findings, which are open work for the triager. Inheriting `done` here would silently close the entire architecture backlog on the first night. Match on the title only; do not fetch properties per issue (that is one API call per row across \~700 rows). The exemption applies to the issue itself AND stops propagation through it to its own descendants. Exempt silently — exemptions are expected behaviour, not report content.
   - Rule B deletes ONLY issues where `status == cancelled` AND `updated_at` is &gt;= 7 days old.
   - Delete strictly deepest-first. A parent may be deleted only after every descendant is already gone. If any descendant is NOT eligible, SKIP the parent silently — expected retention, not report content. NEVER delete a non-eligible issue to unblock a parent.
   - **Blast-radius guard**: if the computed deletion set exceeds 150 issues, ABORT deletion and report the count instead. A set that large means the eligibility logic is wrong, not that there is that much garbage. Steady state is single digits.
   - Deletion is PERMANENT and unrecoverable. Authorized REST exception to the CLI-only rule (drunkcoding, 2026-07-27), scoped to issue deletion only.
- **Inputs** — base URL from `multica config show` (`server_url`) or `$MULTICA_SERVER_URL`; never hardcode a host (the runtime's base URL is NOT the public one — it is typically `http://127.0.0.1:8080`). Auth via `$MULTICA_TOKEN`. Never print the token.

# Steps

1. **Snapshot every issue.** Loop `multica issue list --limit 100 --offset N --output json`, incrementing N by 100, until a page returns fewer than 100 rows. Note the response is an envelope — `{issues, total, limit, offset, has_more}` — not a bare array; read rows from `.issues` and loop until `has_more` is false. Cross-check the row count against the server-reported `total`. Build a map of `id -> {identifier, title, status, parent_issue_id, updated_at}`. Record the total count. Abort if the total is exactly 100.
2. **Rule A — inherit terminal parent status.** Process parents top-down so a newly-terminal parent propagates to its own children within the same run. For each issue whose status is open:
   - parent status `done` → `multica issue status <id> done`
   - parent status `cancelled` → `multica issue status <id> cancelled`
   - parent open or no parent → leave alone
   - title matches `^\[A[0-9]+-[0-9]+\]` → EXEMPT, leave alone and do not propagate through it (see constraints)  
     Record every change as `identifier | title | old -> new`; exemptions are applied silently.

3. **Re-snapshot** (step 2 changed both statuses and `updated_at`), using the same pagination loop.
4. **Rule B — compute the deletion plan.** Eligible = `status == cancelled` AND `updated_at` &gt;= 7 days old. For each eligible issue, compute its full descendant set from the snapshot. Classify:
   - **deletable** — every descendant is also eligible (or it has none)
   - **skipped-blocked** — at least one descendant is not eligible; record each blocker as `identifier(status)`  
     Order the deletable set deepest-first. Apply the blast-radius guard before deleting anything.
5. **Delete.** For each deletable issue, in deepest-first order:
   ```
     curl -sS -X DELETE -o /dev/null -w '%{http_code}' \
       -H "Authorization: Bearer $MULTICA_TOKEN" "<server_url>/api/issues/<id>"
   ```

     A successful delete returns `204`. Treat any 2xx and 404 as success. On ANY other status code, STOP deleting immediately, record the failing issue and code, and report — do not continue down the list, because an unexpected code may mean the ordering assumption is broken.
6. **Post the report** as a comment on this run's issue via `--content-file`, then set the run issue to `done`. **The report is CHANGES-ONLY: list what this run actually modified or destroyed, plus anything actionable — never what it merely scanned, exempted, or left alone.** Omit empty categories entirely (no "none" placeholder rows), omit exemption identifier lists, omit skipped-for-terminal-parent lists, omit Rule B skipped-blocked parents, and omit snapshot bookkeeping (totals, page counts) — all of that is re-derivable and repeats identically every night; a report that is 90% unchanged noise hides the one line that matters. Include exactly:
   - Rule A: every status change made (`identifier | title | old -> new`)
   - Rule B: count and full list of issues DELETED, in order, with identifier and title — deletion is permanent, so this is the only surviving record of them; it is NEVER summarized to a count alone
   - Rule C: every child re-staged (`identifier | title | -> stage N`)
   - **Actionable findings even though nothing was changed** — these are alerts, not noise: missed barriers (`done` + unstaged, with parent), orphaned parents, and children left unstaged because the stage was ambiguous (with the reason)
   - any errors, aborts, guard trips, or steps you could not complete — state these explicitly rather than omitting them; a partial sweep is reported as partial, never as clean, and an aborted run DOES report its snapshot totals (they are the evidence)  
     A run that changed nothing and found nothing actionable posts a single line — `No changes (N issues scanned).` — and nothing else.