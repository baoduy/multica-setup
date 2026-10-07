# Goal

Every hour, find issues whose agent run stopped without finishing and wake that agent back onto them. Two classes, both covered:

- **A — the run was killed.** A transient infrastructure error: API rate limit / overload, or a background-process failure such as the runtime going offline or the daemon restarting mid-task.
- **B — the run abandoned its turn.** The task ended `completed` with no error, but the ticket never reached `done` or `blocked` — typically the agent ended its turn waiting on something it backgrounded, which never notifies because the run is already over (DRK-1673 ended on "I'll stop issuing calls now and wait for the background run notification" and sat `in_progress` with nobody coming).

Failures that are not safe to retry are never retried, and an issue already woken 3 times is left for a human member to review.

# Context

- **Audience** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, entry with role `owner`; use its `user_id` and name, never a hardcoded UUID). This autopilot runs in `run_only` mode and creates NO run issue: the wake comment on the affected issue is the audit record. A run that finds nothing stranded must leave no trace at all.
- **Scope** — every agent in this workspace (the one the run is in). Read the agent list at run time with `multica agent list --output json`; never hardcode it, so a newly created agent is covered automatically. Only a LEAF issue (no sub-issues) that is ASSIGNED TO AN AGENT and sits at `todo` or `in_progress` is eligible for a wake (step 4). An issue assigned to a member is waiting on that person — a release approval, a design review — not on a run; one assigned to a squad or to nobody has no agent run to resume. None of them is ever woken.
- **Detection signal — read this before writing any filter.** Issue status alone tells you nothing: a run that dies or gives up leaves the issue exactly as it was (`todo`, `in_progress`), so no `multica issue list --status ...` sweep can find either class. The signal is the AGENT TASK joined against the issue. `multica agent tasks <agent-id> --output json` returns rows carrying `status`, `error`, `result`, `issue_id`, `created_at`, `completed_at`, `attempt`. A non-empty `issue_id` means the task was issue work.
  - Class A is `status == "failed"` — the run was killed, and `error` says by what.
  - Class B is `status == "completed"` with `error` null — the run ended cleanly, so nothing looks wrong at the task level; what is wrong is that its ISSUE never reached a terminal state. Class B is the common case by far: in drunk-workspace only 14 of 597 dev-backend tasks ever carried `failed`, while an abandoned turn leaves no failure record at all. **Never filter class B on the wording of `result.output`** — the phrasing varies per run; the structural fact (task completed, leaf issue still open, no newer task) is the signal.
- **Constraints**
  - Waking an agent costs a real agent run. Only wake TRANSIENT errors (step 5). A permanent error re-crashes identically and burns credits doing it — report it, never retry it.
  - **Wake cap is 3 per issue.** The counter is the `Wake count` custom property (number) on the issue. At `>= 3`, never wake again: hand the issue to its human owner (step 7) and leave the judgment to them.
  - Lookback is 6 hours. Ignore failures older than that — six hours tolerates six consecutive missed runs, and an older stranded run has already been handled by other means.
  - **Blast-radius guard**: more than 3 eligible stranded issues in one run means the detection logic is wrong, not that the platform melted. Wake nothing and escalate instead (step 9). Steady state is zero or one.
  - No self-wake loop is possible from this autopilot's own failures: `run_only` tasks carry an empty `issue_id`, so they can never appear as stranded work.
  - The wake comment itself creates a task on the issue, so the next run sees a later task and the issue stops being stranded. That is the intended self-limiting behaviour — do not add extra bookkeeping for it.
  - **Never author a thread root on someone else's issue.** When a human later replies inside a thread, the backend wakes the agent that authored that thread's ROOT. If that root is yours, every later human reply in the conversation is delivered to you instead of to the agent doing the work. Step 7's `--parent` exists for exactly that — do not simplify it away.
  - You are an infrastructure recovery mechanism, not a participant in the work. You never change a status, never create or cancel a ticket, never assign anything, never take part in the cycle. Your only writes are the wake comment, the hand-off comment, the `Wake count` property, and the escalation issue of step 9.
- **Inputs** — none; hourly schedule.

# Steps

1. **Build the candidate list with the fixed script — never your own pipeline.** Write this script to `./detect.sh` in your working directory exactly as given, and run `bash ./detect.sh`. Do not rewrite, "simplify" or re-implement it in Python, and never keep its files in `/tmp`: on 2026-09-25 a hand-rolled pipeline appended pretty-printed JSON to a `/tmp` file shared across runs, parsed it line by line, silently dropped the rows it could not parse — among them dev-backend's RUNNING task on DRK-1726 — and woke an agent that was still working.

   ```bash
   multica agent list --output json > ./agents.json || echo "SWEEP PARTIAL: agent list failed" >&2
   jq -r '.[].id' ./agents.json | while read -r a; do
     multica agent tasks "$a" --output json || echo "SWEEP PARTIAL: agent tasks failed for $a" >&2
   done > ./tasks.json
   jq -s --slurpfile agents ./agents.json --argjson now "$(date -u +%s)" '
     def ts: sub("\\.[0-9]+"; "") | fromdateiso8601;
     ($agents[0] | map({(.id): .name}) | add) as $names
     | [.[][] | select((.issue_id // "") != "")]
     | group_by(.issue_id)
     | map((sort_by(.created_at) | last) as $n
         | select(all(.[]; .status | IN("running", "pending", "dispatched", "queued") | not))
         | select(($n.created_at | ts) >= $now - 6*3600)
         | (if $n.status == "failed" then "A"
            elif $n.status == "completed" and ($n.completed_at | ts) <= $now - 1800 then "B"
            else empty end) as $class
         | {class: $class, issue_id: $n.issue_id, agent_id: $n.agent_id, agent_name: $names[$n.agent_id],
            task_id: $n.id, created_at: $n.created_at, completed_at: $n.completed_at,
            error: ($n.error // "" | .[0:200]), output: ($n.result.output // "" | tostring | .[0:200])})
   ' ./tasks.json > ./raw.json || echo "SWEEP PARTIAL: candidate join failed" >&2
   jq -c '.[]' ./raw.json | while read -r row; do
     i=$(jq -r .issue_id <<<"$row")
     issue=$(multica issue get "$i" --output json </dev/null) && kids=$(multica issue children "$i" --output json </dev/null) \
       || { echo "SWEEP PARTIAL: issue lookup failed for $i" >&2; continue; }
     jq -c --argjson issue "$issue" --argjson kids "$kids" '
       select($issue.assignee_type == "agent" and ($issue.status | IN("todo", "in_progress")) and $kids.total == 0)
       | . + {identifier: $issue.identifier, title: $issue.title, status: $issue.status}' <<<"$row" \
       || echo "SWEEP PARTIAL: issue filter failed for $i" >&2
   done | jq -s . > ./candidates.json
   ```

   Any `SWEEP PARTIAL` line on stderr, or a non-zero exit, means the sweep is partial: wake nothing and go to step 9. `./candidates.json` is the ONLY source of stranded issues for the rest of the run; `agent_id` / `agent_name` in each row are the agent to mention, and `identifier` / `title` name the ticket. An issue missing from the file is not stranded — never look it up, count it, comment on it or report it.

2. **What the script already decided — do not re-filter it.** It concatenates every agent's recent task history (the first page `multica agent tasks` returns reaches back days, well past the 6-hour lookback; the "More runs available" note on stderr is expected, not a failure) and reduces it to the NEWEST task per `issue_id` across all agents — recovery is cross-agent, and any agent's later task on the issue means it recovered. It keeps an issue only when the `issue_id` is non-empty (empty is a chat or `run_only` task), the newest task was created within the last 6 hours, and NO task on that issue is `running`, `pending`, `dispatched` or `queued` — a mention at an agent that already has a task in flight is either dropped or queues a duplicate run behind the live one. It then reads every remaining issue and its children and keeps it only when it is a LEAF (`total == 0`), ASSIGNED TO AN AGENT (`assignee_type == "agent"`) and at `todo` or `in_progress` (step 4).

3. **The two classes in `class`.**
   - **A — killed run**: the newest task is `failed`. Go on to step 5 to decide whether the error is safe to retry.
   - **B — abandoned turn**: the newest task is `completed` and its `completed_at` is at least **30 minutes** ago. The grace period keeps you from racing a leader who is about to promote the next stage in their own turn. Class B skips step 5 entirely — there is no error to classify.
   - Anything else (`cancelled`, in flight, too recent) is not in the file.

4. **Only agent-assigned, open LEAF issues — already filtered by the script.** Every row in `./candidates.json` has passed three checks, and you never re-check, widen or override them:

   - **No sub-issues.** A parent, phase or any other middle ticket is legitimately `todo`/`in_progress` for as long as its sub-issues work; its own run ended on purpose. Without this filter class B fires on every parent in the workspace.
   - **Assigned to an agent.** An issue assigned to a member is waiting on that human — a release approval, a design review — and waking the agent whose run last touched it only re-posts the same "waiting on you" turn; on 2026-09-30 four such leaves (DRK-1866, DRK-1872, DRK-1879, DRK-1882) were woken to the cap and handed off every hour, and tripped two escalations. An issue assigned to a squad or to nobody has no agent run to resume either.
   - **Status `todo` or `in_progress`.** `done`/`cancelled` means the work landed or was dropped; `in_review` is awaiting a human; `blocked` needs an answer, not a retry; `backlog` is not active work.

   Everything the script dropped is an expected outcome: not woken, not counted toward the blast-radius guard of step 6, not commented on, not escalated, not mentioned in any report.

5. **Classify the error — class A only.** From the failed task's `error` string.
   - **TRANSIENT — safe to wake.** API rate limit / overload: `429`, `rate limit`, `rate_limit_error`, `529`, `Overloaded`, `500`, `502`, `504`, `timeout`, `The operation was aborted`, `connection reset by peer`. Background-process / runtime failure: `runtime went offline`, `daemon restarted while task was in flight`, `task expired in queue`, `task cancelled by server`, `terminated`, `hermes process exited`, `agent produced no new messages for`.
   - **PERMANENT — never wake**: `maximum context length`, `monthly spend limit`, `requires more credits`, `fewer max_tokens`, `Key limit exceeded`, `Payment required`, `is not supported`, `executable not found`, `no such file or directory`, `No endpoints available matching your guardrail restrictions`, `AF_UNIX path too long`, `InvalidParam`.
   - Anything you cannot match confidently is PERMANENT. Defaulting to "don't retry" costs a delay; defaulting to "retry" costs a credit-burning crash loop.

6. **Apply the guard and the cap.** The wake list is the class-A transient issues plus every class-B issue **in `./candidates.json`** — an issue the script dropped (has children, not assigned to an agent, or its status is not `todo`/`in_progress`) or classified PERMANENT at step 5 is not stranded, does not count toward the guard, and never appears in a report. If the wake list exceeds 3 issues, wake NOTHING and go to step 9. Otherwise read each remaining issue's counter with `multica issue property list <issue-id> --output json` and take `Wake count` (absent means 0). A value `>= 3` moves that issue off the wake list onto the hand-off list of step 7b.

7. **Wake each surviving issue — as a REPLY, never as a new thread root.** Immediately before each wake, re-run `bash ./detect.sh` and confirm the issue is still listed: `jq -e --arg i <issue-id> 'any(.[]; .issue_id == $i)' ./candidates.json`. A non-zero exit means an agent picked it up while you worked — skip it silently, no comment and no counter bump. Then find where to attach: `multica issue comment list <issue-id> --roots-only --output json`, and take the NEWEST root comment that you did not author. Post the wake as a reply to it: `multica issue comment add <issue-id> --content-file <path> --parent <that-root-comment-id>` (write the content file inside your working directory, never `/tmp`). Only when the issue has no such root — no comments at all, or every root is one of your own — post without `--parent`. The body opens with the crashed agent's mention, written as a `mention://agent/<agent-id>` markdown link using that agent's real id, and reads:

   ```
   <mention link for the crashed agent>

   Your run on this issue failed at <failed task created_at> with a transient error and nothing has picked it up since. Retrying now — re-read the issue and its comments before you resume, because the previous run may have completed part of the work.

   Error: `<first 200 chars of the error>`

   Woken by the hourly run-recovery autopilot (wake <n> of 3).
   ```

   For a **class B** issue the body is the same shape with this text instead:

   ```
   <mention link for the agent whose run ended>

   Your run on this issue ended at <completed_at> without the ticket reaching `done` or `blocked`, and nothing has picked it up since. Per the workspace context, every reporting turn ends by reading the ticket's status back and correcting it — and a turn must never end waiting on something backgrounded, because the run is over and nothing will notify you. Re-read the issue and its comments, finish the work, and end this turn at `done` or `blocked` with a `## BLOCKER`.

   Last run output: `<first 200 chars of result.output>`

   Woken by the hourly run-recovery autopilot (wake <n> of 3).
   ```

   Mention the agent whose task failed or abandoned the turn, never the issue assignee — the assigned agent is often not the one whose run stopped (a leader's run on a member's sub-issue, a gate's run on a leader's ticket). Exactly one mention per comment.

   Then bump the counter: `multica issue property set <issue-id> --name "Wake count" --value <n>`.

   **7b. Issues at the cap get a hand-off, not a wake.** For an issue whose `Wake count` is already `>= 3`, post ONE comment — same `--parent` rule — that mentions the issue's human owner (its `Owner` property, else the nearest ancestor's, else the workspace owner) and states plainly: the run has now stopped short 4 times, it was woken 3 times, it will NOT be woken again, and the last error or last run output. Do NOT mention any agent in this comment — that would wake it straight back into the same crash. Leave the status, the assignee and the judgment to that member. Post this once and never again for that issue; on later runs it is already at the cap and already handed off, so skip it silently.

8. **Report, don't retry, the permanent failures.** For each PERMANENT failure, post ONE comment on that issue mentioning the workspace owner (resolved at runtime), naming the failed agent, quoting the error, and stating plainly that it was NOT retried and why. Do NOT mention the agent. Same `--parent` rule as step 7. Issues the script dropped at step 4 get no comment at all.

9. **Escalate only when a human is actually needed.** Escalate only when the blast-radius guard tripped at step 6, or when a CLI step failed in a way that left the sweep partial.

   **The escalation reports the wake list and nothing else.** Every issue it names is one that qualified for a wake: it is in `./candidates.json` and, for class A, passed the step-5 transient classification. Issues that were skipped — parents with children, issues assigned to a member, a squad or nobody, `done`/`cancelled`/`in_review`/`blocked`/`backlog` leaves, permanent errors, issues with a task already in flight — are expected outcomes, not findings; they are never listed, never counted, and never explained. If nothing qualified for a wake, there is nothing to escalate: create no issue at all and end the run silently, however many raw candidates the sweep started from.

   Then create ONE issue: `multica issue create --title "Run recovery needs attention (<UTC date>)" --description-file ./escalation.md --assignee-id <owner user_id> --priority high --project <this run issue's project id>` (the `project_id` of the issue this autopilot run created). The description carries exactly three things:

   - one line naming the reason — the guard tripping with its count, or which step left the sweep partial;
   - one table, one row per wake-list issue. **Identify each issue by its ticket identifier (`DRK-1673`), never by its UUID** — the script already put it in each row as `identifier`. Name the agent by its `agent_name` from step 1, never its id:

     | Ticket | Title | Class | Agent | Stopped at (UTC) | Wake count | Error / last output |
     |---|---|---|---|---|---|---|
     | DRK-1673 | Wire the accounts screen | B | dev-backend | 2026-09-23 23:09 | 1 | first 120 chars, single line |

   - exactly which steps you could not complete.

   This is the ONLY circumstance in which this autopilot creates an issue.

10. **Unsubscribe after every comment.** Commenting can add you to an issue's notification list. After each comment you post — wake, hand-off or report — run `multica issue subscriber remove <issue-id>` (it defaults to you). It is idempotent: "nothing to remove" is success, not an error. Never fail a wake because the unsubscribe failed; record it and continue.

11. **Stay silent otherwise.** If the sweep found nothing stranded, post nothing, create nothing, and end the run. A quiet hour leaves no trace — never post a "nothing to do" comment anywhere. Report a partial sweep as partial, never as clean.
