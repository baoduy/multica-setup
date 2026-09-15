# Goal

Every hour, find issues sitting in `todo` or `in_progress` whose agent run died on a transient infrastructure error with nothing having picked them up since, and wake the crashed agent back up on that issue. Failures that are NOT safe to retry get reported, never retried.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, entry with role `owner`; use its `user_id` and name, NEVER a hardcoded UUID). This autopilot runs in `run_only` mode and creates NO run issue: the wake comment on the affected issue IS the audit record. A run that finds nothing stranded must leave no trace at all.
- **Scope** — every agent in workspace `ed38be16-b92f-48cc-9611-89bf09102d84`. Read the agent list at run time with `multica agent list --output json`; never hardcode it, so newly created agents are covered automatically. Only issues whose status is `todo` or `in_progress` are eligible for a wake — see step 4.
- **Detection signal — read this before you write any filter.** The issue's status tells you nothing about whether a run CRASHED. A crashed run leaves the issue exactly as it was (`todo`, `in_progress`); there is no error status, so an `multica issue list --status ...` sweep cannot find these. The signal lives on the AGENT TASK: `multica agent tasks <agent-id> --output json` returns rows carrying `status`, `error`, `issue_id`, `created_at`, `attempt`. `status == "failed"` with a non-empty `issue_id` is a crashed run on an issue. Issue status is used only to decide whether that crash is still worth reviving (step 4).
- **Constraints**
  - Waking an agent costs a real agent run. Only wake TRANSIENT errors (step 5). A permanent error re-crashes identically and burns credits doing it — report it, never retry it.
  - Never wake the same issue more than twice. The counter lives in issue metadata `stuck_wake_count`.
  - Lookback is 6 hours. Ignore failures older than that: a stale failure with still no follow-up has already been handled by other means (verified at setup — MXW-347 and MXW-488 sat failed-and-stranded for weeks and are both `done` today). Six hours tolerates six consecutive missed runs.
  - **Blast-radius guard**: more than 3 eligible stranded issues in one run means the detection logic is wrong, not that the platform melted. Wake nothing and escalate instead. Steady state is zero or one.
  - No self-wake loop is possible from this autopilot's own failures: `run_only` tasks carry an empty `issue_id`, so they can never appear as stranded work.
  - The wake comment itself creates a task on the issue, so the next run sees a later task and the issue stops being stranded. That is the intended self-limiting behaviour — do not add extra bookkeeping for it.
  - **NEVER author a thread root on someone else's issue.** When a human later replies inside a thread, the backend's implicit routing wakes the agent that authored that thread's ROOT. If that root is yours, every subsequent human reply in the conversation is delivered to you instead of to the agent doing the work. This is not hypothetical: on MXW-885 the wake comment created a new root, and drunkcoding's reply at `2026-07-31T00:17:24Z` enqueued an issue-janitor run two seconds later. Step 7 exists in the shape it does to prevent exactly this — do not "simplify" the `--parent` away.
  - Subscription is NOT the cause of that mis-routing and unsubscribing alone does NOT prevent it (on MXW-885 issue-janitor was never a subscriber and was still triggered). The unsubscribe in step 7 is cheap defence-in-depth for the notification list, not the fix.
- **Inputs** — none; hourly schedule.

# Steps

1. **Fetch the agents.** `multica agent list --output json`. Keep both `id` and `name` for each — the name becomes the mention label, the id becomes the mention target.

2. **Fetch every agent's task history.** For each agent id: `multica agent tasks <agent-id> --output json`. This returns the agent's FULL history in one call, not a page — no pagination needed. Concatenate all agents' rows into one list before analysing anything; recovery is cross-agent and a per-agent view will produce false positives.

3. **Find the stranded runs.** A task is STRANDED when ALL of these hold:
   - `status == "failed"`
   - `issue_id` is non-empty (an empty `issue_id` is a chat or `run_only` task — not issue work, skip it)
   - `created_at` is within the last 6 hours
   - NO other task in the combined list has the same `issue_id` and a later `created_at` — any agent counts, because a different agent picking the issue up means it recovered
   - NO task on that `issue_id` is currently `running` or `pending` (a mention at an agent that already has a pending task on the issue is silently dropped by the backend, so waking one is a wasted no-op)

4. **Keep only actively-open issues.** For each stranded issue: `multica issue get <issue-id> --output json`. An issue is eligible ONLY when its status is `todo` or `in_progress`. Skip every other status and record the reason in the tally:
   - `done` / `cancelled` — the work landed or was dropped; the crash no longer matters.
   - `in_review` — the deliverable is awaiting a human; waking an agent would talk over the reviewer.
   - `blocked` — reviving the CRASHED run will not unblock it. But a `blocked` issue whose blocker thread already has a newer reply is waiting on ACTUATION, not on an answer — Pass B below owns that case; this crash sweep still skips it.
   - `backlog` — not active work; it will be picked up when scheduled.

5. **Classify the error** from the failed task's `error` string.
   - **TRANSIENT — safe to wake**: `529`, `Overloaded`, `500`, `502`, `504`, `timeout`, `The operation was aborted`, `task expired in queue`, `runtime went offline`, `daemon restarted while task was in flight`, `task cancelled by server`, `terminated`, `hermes process exited`, `connection reset by peer`, `agent produced no new messages for`.
   - **PERMANENT — never wake**: `maximum context length`, `monthly spend limit`, `requires more credits`, `fewer max_tokens`, `Key limit exceeded`, `Payment required`, `is not supported`, `executable not found`, `no such file or directory`, `No endpoints available matching your guardrail restrictions`, `AF_UNIX path too long`, `InvalidParam`.
   - Anything you cannot match confidently is PERMANENT. Defaulting to "don't retry" costs a delay; defaulting to "retry" costs a credit-burning crash loop.

6. **Apply the guard and the cap.** If the wake list exceeds 3 issues, wake NOTHING and go to step 9. Otherwise, for each issue on the wake list run `multica issue metadata list <issue-id> --output json`; when `stuck_wake_count` is already `>= 2`, move that issue off the wake list onto the escalation list.

7. **Wake each surviving issue — as a REPLY, never as a new thread root.** First find where to attach: `multica issue comment list <issue-id> --roots-only --output json`, and take the NEWEST root comment that issue-janitor did not author. Post the wake as a reply to it: `multica issue comment add <issue-id> --content-file <path> --parent <that-root-comment-id>` (write the content file inside your working directory, never `/tmp`). Only when the issue has no such root — no comments at all, or every root is one of your own — post without `--parent`. The body MUST open with both mentions, in this exact shape:

   ```
   [@all](mention://all/all) [@<agent-name>](mention://agent/<agent-id>)

   Your run on this issue failed at <failed task created_at> with a transient error and nothing has picked it up since. Retrying now — re-read the issue and its comments before you resume, because the previous run may have completed part of the work.

   Error: `<first 200 chars of the error>`

   Woken by the stuck-run recovery autopilot (attempt <n> of 2).
   ```

   Neither mention is decoration and neither is optional. `@all` suppresses the issue assignee's implicit on-comment trigger; the explicit `@agent` still fires regardless. Together they wake exactly the agent that crashed and nobody else — which matters because a stranded issue frequently has NO assignee at all, or an assignee that is not the agent that died. Mention the agent whose task failed, never the assignee.

   Then bump the counter: `multica issue metadata set <issue-id> --key stuck_wake_count --value <n> --type number`.

   Then hand the issue back completely — you are a recovery mechanism, not a participant in the work:
   `multica issue subscriber remove <issue-id> --user-id c525df5b-88bb-4772-9102-0d17a22eaad5`
   Commenting can add you to the notification list; this takes you back off it. It is idempotent — if you were never subscribed the command reports nothing to remove, which is a success, not an error. Run it after EVERY comment you post on an issue that is not your own, including the reports in step 8. Never fail a wake because the unsubscribe failed: record it and continue.

8. **Report, don't retry, the rest.** For each PERMANENT failure and each issue that hit the wake cap, post ONE comment on that issue mentioning the workspace owner `[@<owner-name>](mention://member/<owner-user_id>)` (resolved at runtime, per Audience — never a hardcoded UUID), naming the failed agent, quoting the error, and stating plainly that it was NOT retried and why. Do NOT mention the agent in these comments — that would wake it straight back into the same crash. Attach these as a reply under an existing root and unsubscribe afterwards, exactly as step 7 requires. Issues skipped at step 4 on status grounds get no comment at all.

9. **Escalate only when a human is actually needed.** If the blast-radius guard tripped, or a CLI step failed in a way that left the sweep partial, create ONE issue: `multica issue create --title "Stuck-run recovery needs attention (<UTC date>)" --description-file ./escalation.md --assignee-id <owner-user_id> --priority high --project e301fbc6-2ee9-48bd-8587-d5626b6176f2` (`<owner-user_id>` = workspace owner resolved at runtime, per Audience — never a hardcoded UUID). The description carries the full stranded list with each issue's status and error, the count that tripped the guard, and exactly which steps you could not complete. This is the ONLY circumstance in which this autopilot creates an issue.

10. **Stay silent otherwise.** If the sweep found nothing stranded, post nothing, create nothing, and end the run. A quiet hour must leave no trace — never post a "nothing to do" comment anywhere. Report a partial sweep as partial, never as clean.

# Pass B — answered-blocker sweep (same run, after the crash sweep)

The crash sweep catches runs that DIED; this pass catches decisions that died. Someone (agent or human) answers a `## BLOCKER` but forgets the actuation — no status flip, no mention — and the cycle stalls while everyone believes it is moving. Only a status transition or an agent mention enqueues a run; a correct answer left as prose moves nothing (MXW-1016 stalled exactly this way: "A. Confirmed and approved" landed 24 seconds after the blocker, and the cycle sat dead until a human noticed).

1. **Collect candidates.** `multica issue list --status blocked --output json`. Keep only issues assigned to an AGENT — a `blocked` issue assigned to a human is a legitimate escalation waiting on a person, never nudge those.
2. **Locate the blocker thread.** For each candidate, scan the comments of the issue ITSELF and of its PARENT (`parent_id`, when set) for the most recent comment containing a `## BLOCKER` heading. No such comment anywhere → skip; blocked-without-a-report is a protocol defect but not this pass's job.
3. **Detect the unactuated answer.** A candidate qualifies when BOTH hold:
   - a reply newer than the blocker comment exists in its thread (or a later root on the same issue), authored by someone OTHER than the blocker's author — i.e. somebody responded after the block;
   - that newest reply is at least **30 minutes old** and the issue is STILL `blocked`. The grace period keeps you from racing a resolver who is about to actuate in their current turn.
4. **Guards — same discipline as the crash sweep.** Per-issue metadata counter `blocker_nudge_count`: already `>= 2` → move to the escalation list (step 9), never a third nudge. More than 3 qualifying issues in one run → nudge NOTHING and escalate; steady state is zero or one.
5. **Nudge the BLOCKED issue's assignee agent — not the resolver, not the leader.** The member owns the judgment (does the reply actually settle the Need?) per the self-service-resume rule in `sdlc-flow-squad-member-protocol`; you only detect the timestamp pattern and must NEVER flip someone else's status yourself. Post a REPLY inside the blocker thread (same `--parent` rule and root-authorship rule as step 7 — never a new root):

   ```
   [@all](mention://all/all) [@<assignee-agent-name>](mention://agent/<assignee-agent-id>)

   A reply landed in this blocker thread at <reply created_at>, but <blocked-issue-identifier> is still `blocked`. If that reply settles your **Need**, flip your sub-task back and resume per your self-service-resume protocol; if it does not, state exactly what is still missing in this thread and stay blocked.

   Nudged by the stuck-run recovery autopilot (attempt <n> of 2).
   ```

   Then bump `blocker_nudge_count` (`--type number`) and unsubscribe exactly as step 7 requires.
6. **The silence rule applies to this pass too.** Nothing qualifying → no comment, no issue, no trace.