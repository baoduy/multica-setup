# Goal

Monthly report for the workspace owner, in three parts:

1. Claude Code `/insights`: the usage report for this runtime.
2. Multica release review: which new `multica-ai/multica` releases would improve the drunk and mx workspace bundles, or break them.
3. Gate digest: how the PR and spec gates did over the last 30 days, from their `Gate verdict`, `Gate round` and `Gate score` properties.

The issue this run creates is the record, and its final comment is the deliverable. **Report only.** You never apply a proposal, edit a bundle, commit, push, or change the live workspace.

# Context

- **Audience**: the workspace owner. Resolve the owner at runtime with `multica workspace member list --output json` and pick the member with role `owner`. Never hardcode a UUID.
- **Runtime**: `/insights` reads the Claude Code session history in `~/.claude` on the machine it runs on. The report covers every Claude Code session on that machine, including Multica agent runs.
- **Read-only.** The only `multica` writes you make are this issue's comment and its status. You never create, assign or change any other ticket.
- **Independent parts.** Run part 1 first. If one part fails, still run and report the others.

# Part 1: Claude Code insights

1. Run `claude -p "/insights"` from your working directory, with a timeout of at least 15 minutes. It usually takes about a minute. On success it prints `file:///…/.claude/usage-data/report-<YYYY-MM-DD-HHMMSS>.html`.
2. Take that path, minus the `file://` prefix. Confirm the file exists and was written during this run. If the command fails, prints no path, or the file is missing or old, part 1 has failed. Keep the shortest decisive output line for the BLOCKER.
3. Read the report HTML and extract its text. Write a summary of at most 25 lines: one line for the period and volume it covers, then each section's two or three key findings in the report's own words, then its top suggestions. Do not invent numbers that the report does not show.

# Part 2: Multica release review

1. Clone the setup repo into your working directory: `gh repo clone baoduy/multica-setup multica-setup -- --branch dev`. Work only inside that clone.
2. Read `multica-setup/CLAUDE.md` and `multica-setup/.claude/skills/multica-release-review/SKILL.md`. Follow the skill's steps 1 to 5, with these overrides:
   - **Skip step 6 entirely.** Do not write `release-reviews/last-run.json`. Do not commit or push. The state advances only when the owner runs the skill themselves.
   - Write the report file inside the clone (`release-reviews/<run_date>_<range>.md`). It is attached to the comment, never committed.
   - Do not ask which proposals to implement. List the proposal titles in the comment instead.
   - If the skill finds no release after `last_reviewed_tag`, part 2 is one line: "No new Multica releases since <tag>." Write no report file.
3. Check the vendored archify skill, as `CLAUDE.md` requires on every release review. Compare the `version` in `export/drunk-workspace/skills/archify/skill-release.json` with `gh api repos/tt-a1i/archify/releases/latest --jq .tag_name`, ignoring a leading `v`. Report one line: "archify up to date at <version>" or "archify <bundle version> behind upstream <tag>". Do not sync.
4. If the clone, `gh` or the skill fails, part 2 has failed. Keep the shortest decisive output line for the BLOCKER.

# Part 3: Gate digest

How the two review gates did over the last 30 days. Report only: you propose nothing and change nothing. The owner reads the numbers and decides whether a policy needs to change.

1. Write this script to `./gate-digest.sh` in your working directory exactly as given and run `DAYS=30 bash ./gate-digest.sh > digest.json`. Do not rewrite it, re-implement it, or keep its files in `/tmp`. It reads every review sub-task created in the window (the `Gate verdict`, `Gate round` and `Gate score` properties), and the comments of each one that took a rework round, and writes `rows.jsonl`, `findings.txt` and the digest.

```bash
#!/usr/bin/env bash
# Gate digest: every review sub-task created in the last DAYS days, with its current verdict.
set -euo pipefail
DAYS="${DAYS:-30}"
SINCE=$(date -u -v-"${DAYS}"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-${DAYS} days" +%Y-%m-%dT%H:%M:%SZ)
STOP=$(date -u -v-"$((DAYS + 30))"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-$((DAYS + 30)) days" +%Y-%m-%dT%H:%M:%SZ)
: > rows.jsonl
for v in APPROVED REWORK ESCALATED MERGE_FAILED ALREADY_MERGED OWNER_MERGED; do
  off=0
  while :; do
    page=$(multica issue list --property "Gate verdict=$v" --limit 100 --offset "$off" --sort created_at --direction desc \
      --output json --resolve-properties --fields id,identifier,title,created_at,updated_at,properties)
    echo "$page" | jq -c --arg s "$SINCE" '.issues[] | select(.created_at >= $s)
      | {id, key: .identifier, title, updated_at,
         gate: (if (.title|test("^\\[S[0-9]+\\]")) then "spec" else "pr" end),
         verdict: ([.properties[]|select(.name=="Gate verdict")|.display][0]),
         round: ([.properties[]|select(.name=="Gate round")|.value][0] // 0),
         score: ([.properties[]|select(.name=="Gate score")|.value][0])}' >> rows.jsonl
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

2. If the script fails or prints no JSON, part 3 has failed. Keep the shortest decisive output line for the BLOCKER.
3. From `digest.json` write the section, using only its numbers:
   - **PR gate** and **Spec gate**, one line each: reviews, first-pass rate (`first_pass` / `count`, as a percentage), reworked, mean rework rounds, escalated, median score, and the count per verdict.
   - **Most-cited in rework comments:** the `top_findings` entries as `id ×n`. The severity tags (`[blocking]`, `[major]` and the like) count every tagged finding in those comments; the rule-ids are the stack rules the gates cited most.
   - **Reworked:** up to 10 `reworked_keys` per gate, newest first.
   - If last month's run of this autopilot posted a digest, put last month's first-pass rates beside this month's. Otherwise say `no earlier digest`.

# Report

Post ONE comment on this issue with `multica issue comment add` and `--content-stdin`:

- `## Claude Code insights`: the part 1 summary and the HTML report's absolute path on its own line.
- `## Multica release review`: the installed `multica` version, the range reviewed, the skill's Summary bullets, the proposal titles in rank order with their type, every breaking change to verify, and the archify line. If nothing is new, give the one line plus the archify line.
- `## Gate digest`: the part 3 section.
- `## BLOCKER`: only if a part failed. Name the part and quote its output line.
- End with one member mention of the workspace owner.

Attach the insights HTML with `--attachment <path> --allow-external-file`, and the release review report with a second `--attachment <path>` when it exists.

Then set this issue `blocked` if any part failed, or `done` if all three succeeded.
