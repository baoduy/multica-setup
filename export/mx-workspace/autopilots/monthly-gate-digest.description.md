# Goal

Monthly gate digest for the workspace owner: how the PR and spec gates did over the last 30 days. The issue this run creates is the record, and its final comment is the deliverable. **Report only.** You never apply a proposal, edit a policy or skill, or change any other ticket.

# Context

- **Audience**: the workspace owner. Resolve the owner at runtime with `multica workspace member list --output json` and pick the member with role `owner`. Never hardcode a UUID.
- **Read-only.** The only `multica` writes you make are this issue's comment and its status.

# Part 1: Gate digest

How the two review gates did over the last 30 days. Report only: you propose nothing and change nothing. The owner reads the numbers and decides whether a policy needs to change.

1. Write this script to `./gate-digest.sh` in your working directory exactly as given and run `DAYS=30 bash ./gate-digest.sh > digest.json`. Do not rewrite it, re-implement it, or keep its files in `/tmp`. It reads every review sub-task created in the window (the `review_verdict`, `review_round` and `review_score` metadata on PR review sub-tasks, and the `spec_review_*` keys on spec review sub-tasks), and the comments of each one that took a rework round, and writes `rows.jsonl`, `findings.txt` and the digest.

```bash
#!/usr/bin/env bash
# Gate digest (mx, gate state in issue metadata): every review sub-task created in the last DAYS days, with its current verdict.
set -euo pipefail
DAYS="${DAYS:-30}"
SINCE=$(date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-${DAYS} days" +%Y-%m-%dT%H:%M:%SZ)
STOP=$(date -u -v-"$((DAYS + 30))"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-$((DAYS + 30)) days" +%Y-%m-%dT%H:%M:%SZ)
: > rows.jsonl
for kv in review_verdict={APPROVED,DEFERRED,REWORK,POLISH,ESCALATED,ALREADY_MERGED} spec_review_verdict={APPROVED,"REVIEW REQUESTED",REWORK,ESCALATED}; do
  off=0
  while :; do
    page=$(multica issue list --metadata "$kv" --limit 100 --offset "$off" --sort created_at --direction desc \
      --output json --fields id,identifier,title,created_at,updated_at,metadata)
    echo "$page" | jq -c --arg s "$SINCE" '.issues[] | select(.created_at >= $s)
      | {id, key: .identifier, title, updated_at,
         gate: (if .metadata.spec_review_verdict then "spec" else "pr" end),
         verdict: (.metadata.review_verdict // .metadata.spec_review_verdict),
         round: ((.metadata.review_round // .metadata.spec_review_round // 0) | tonumber),
         score: ((.metadata.review_score // .metadata.spec_review_score) | if . == null then null else tonumber end)}' >> rows.jsonl
    n=$(echo "$page" | jq '.issues|length'); more=$(echo "$page" | jq '.has_more')
    # Review sub-tasks live days, not months: stop paging once a page was created 30 days before the window.
    oldest=$(echo "$page" | jq -r '.issues[-1].created_at // ""')
    [ "$more" = true ] && [ "$oldest" \> "$STOP" ] || break
    off=$((off + n))
  done
done
# Rule-ids and severities named in the comments of every sub-task that took a rework round.
: > findings.txt
for id in $(jq -r 'select(.round > 0) | .id' rows.jsonl); do
  multica issue comment list "$id" --output json | jq -r '(if type == "array" then . else .comments end)[]?.content // empty' \
    | grep -oE '\b[A-Z][A-Z0-9]+(-[A-Z0-9]+)*-[0-9]{3}\b|\[(blocking|important|blocker|major)\]' >> findings.txt || true
done
jq -s --arg since "$SINCE" '
  def stats: {count: length,
    by_verdict: (group_by(.verdict) | map({key: .[0].verdict, value: length}) | from_entries),
    first_pass: ([.[]|select(.round==0 and (.verdict|test("APPROVED|MERGED")))]|length),
    reworked: ([.[]|select(.round>0)]|length),
    mean_rounds: (if length>0 then (([.[].round]|add)/length*100|round/100) else null end),
    escalated: ([.[]|select(.verdict=="ESCALATED")]|length),
    median_score: ([.[].score|select(.!=null)]|sort|if length>0 then .[length/2|floor] else null end),
    reworked_keys: [.[]|select(.round>0)|.key]};
  {since: $since, pr: ([.[]|select(.gate=="pr")]|stats), spec: ([.[]|select(.gate=="spec")]|stats)}' rows.jsonl > digest.json
sort findings.txt | uniq -c | sort -rn | head -15 | awk '{print $2" "$1}' | jq -R -s 'split("\n")|map(select(length>0)|split(" ")|{(.[0]): (.[1]|tonumber)})|add // {}' > top-findings.json
jq -s '.[0] + {top_findings: .[1]}' digest.json top-findings.json
```

2. If the script fails or prints no JSON, part 1 has failed. Keep the shortest decisive output line for the BLOCKER.
3. From `digest.json` write the section, using only its numbers:
   - **PR gate** and **Spec gate**, one line each: reviews, first-pass rate (`first_pass` / `count`, as a percentage), reworked, mean rework rounds, escalated, median score, and the count per verdict.
   - **Most-cited in rework comments:** the `top_findings` entries as `id ×n`. The severity tags (`[blocking]`, `[major]` and the like) count every tagged finding in those comments; the rule-ids are the stack rules the gates cited most.
   - **Reworked:** up to 10 `reworked_keys` per gate, newest first.
   - If last month's run of this autopilot posted a digest, put last month's first-pass rates beside this month's. Otherwise say `no earlier digest`.

# Report

Post ONE comment on this issue with `multica issue comment add` and `--content-stdin`: `## Gate digest` with the section above, `## BLOCKER` only if the script failed (quote its output line), and one member mention of the workspace owner. Attach `digest.json` with `--attachment <path> --allow-external-file`.

Then set this issue `blocked` if the script failed, or `done` if it succeeded.
