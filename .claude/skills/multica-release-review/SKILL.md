---
name: multica-release-review
description: Review new multica-ai/multica releases since the last recorded run and propose how to use their features to improve the agents, squads, skills, autopilots and policies in the drunk and mx workspace bundles. Use when the user asks to check new Multica releases, catch up on Multica changes, or runs /multica-release-review.
argument-hint: "[--from <tag>] [--to <tag>]"
---

# Multica release review

Study the Multica releases the setup has not been reviewed against yet. Work out
which new features would improve the drunk and mx workspaces or which changes break
them, write a report, and record the run so the next one starts after the newest
release reviewed.

This skill only analyses and proposes changes. It never edits a bundle or pushes
to a live workspace. Changes the owner accepts go through the normal flow in
`CLAUDE.md`: policy first, one commit per change, and pushing live only with
approval.

## Files

- State: `release-reviews/last-run.json`
  ```json
  {"last_reviewed_tag": "v0.6.0", "published_at": "2026-09-28T07:07:30Z",
   "run_date": "2026-09-28", "report": "release-reviews/2026-09-28_v0.6.0.md"}
  ```
- Reports: `release-reviews/<run_date>_<oldest-tag>..<newest-tag>.md`, or
  `<run_date>_<tag>.md` when the run covers one release.

## 1. Pick the releases

```bash
cat release-reviews/last-run.json
gh release list -R multica-ai/multica --limit 100 --exclude-drafts --exclude-pre-releases \
  --json tagName,publishedAt
```

- Review every release published after `published_at`, oldest first. If there is
  none, report "no new releases since <tag>" and stop. Do not write a report or
  change the state.
- `--from <tag>` / `--to <tag>` override the range, with `--from` exclusive, the
  same way `last_reviewed_tag` works.
- If there is no state file and no `--from`, ask the owner where to start. Offer
  the latest release only, the release matching `multica --version`, or a named tag.

Also record the installed version (`multica --version`). A feature that needs a
newer server or daemon (for example a claim capability such as `joined-wakeups-v1`)
is marked **needs upgrade**. It does not count as available.

## 2. Triage the changelog

For each release, run `gh release view <tag> -R multica-ai/multica --json body`.
Every changelog line names a PR (`(#NNNN)`). Sort each PR into one bucket:

- **Relevant.** It touches agents, squads, skills, autopilots, wakeups, issue
  status or sub-issue flow, custom properties, labels, projects, the runtime prompt
  or daemon, the CLI (`cmd/multica`), task/run lifecycle, comments or mentions,
  PR/CI integration, deliverables or attachments agents produce, workspace
  settings, or the model catalog.
- **Skip.** Desktop or mobile chrome, i18n copy, the marketing README, editor
  cosmetics, or internal refactors with no behaviour change. List skipped PRs by
  number and title only, so the owner can overrule a skip.

When unsure, treat the PR as relevant.

## 3. Read the relevant PRs carefully

For each relevant PR:

```bash
gh pr view <N> -R multica-ai/multica --json title,body,files,mergedAt
```

Read the whole body: "Rollout and risks" and "behavior changes" sections are where
breaking changes hide. Then read every changed documentation file that agents or
operators rely on: `docs/**`, `apps/docs/**`, and any `references/*.md` under the
built-in multica skill (agents read those at runtime).

```bash
gh api repos/multica-ai/multica/contents/<path>?ref=<tag> --jq .content | base64 -d
```

If a release has more than about 15 relevant PRs, fan out. Spawn one
general-purpose agent per release, each returning per-PR notes (feature, new
CLI/API surface, behaviour changes, rollout needs). Keep the mapping in step 4 in
the main thread.

For each PR, note what an agent or operator can now do that it could not do
before, the exact CLI flags and API fields, and anything that changes existing
behaviour.

## 4. Map the features onto the setup

Read the setup before proposing anything. Proposals that ignore how the bundles
work today are useless.

- `export/{drunk,mx}-workspace/docs/policies/`. Policy is the source of truth.
- `workspace/workspace.context.md`, `agents/*.md`, `squads/*.md`, `autopilots/*.json`,
  `properties/properties.json`, and the flow skills (`sdlc-flow-*`, `leader-gitops`,
  `pr-review-gate`, `spec-review-gate`).
- The auto-memory index (`MEMORY.md`). It lists the workarounds built for missing
  platform features, such as mention-link wakes, the `Retrigger on done` property,
  run-medic and the hourly run recovery, stalled `completed` runs, and the
  in_review override. These are the first things to check against each new feature.

For each relevant feature, look for:

1. **Replace a workaround.** A native feature that makes a property, autopilot,
   prose rule or script redundant or more reliable. Example: wakeup v2
   `children_done` conditions and system `child_done` rules against the
   `Retrigger on done` property and the leader's re-arm steps.
2. **Breaks an assumption.** A setup file relies on behaviour the release changed.
   Example: v0.6.0 no longer posts a system comment when sub-issues finish. Grep
   the bundles for text that expects it.
3. **New capability.** Something the flow could use that nothing replaces yet,
   such as check-ins for quiet autopilot runs, PR `merged`/`checks_finished` waits,
   or deliverables.
4. **Not useful here.** Say why in one line.

Cite each hit as `path:line` in both bundles. Flag every proposal that contradicts
or amends a policy with the policy file and the statement it would change. Those
need the owner's explicit yes before any edit.

## 5. Write the report

`release-reviews/<run_date>_<range>.md`:

```markdown
# Multica release review — <range> (<run_date>)

Installed: multica <version>. Releases: <tag (date)>, ...

## Summary
<3–6 bullets: the changes that matter most, ranked>

## Proposals
### P1 <title> — <replace workaround | breaks assumption | new capability>
- Feature: <what it is>, from #<PR> in <tag>. Needs upgrade: yes/no
- Setup today: <how it works now, with path:line>
- Change: <what to edit, in which bundle(s)>
- Policy impact: <none | policy file + statement; needs owner approval>
- Benefit / risk / effort: <one line each>

## Breaking or behaviour changes to verify
## Not adopted (relevant but not useful here)
## Skipped PRs
<#N title, one per line, grouped by release>
```

Rank proposals by value. A breaking change the setup depends on comes first.

## 6. Record the run

Only after the report is written, overwrite `release-reviews/last-run.json` with the
newest tag reviewed, its `publishedAt`, today's date and the report path. A run cut
short leaves the state untouched, so the next run repeats the same range.

Sync with `origin/dev` (`git fetch` and fast-forward or rebase). Commit the report
and the state together with the message
`repo: multica release review <range>` and push to `dev`.

Finish by giving the owner the summary and the proposal titles, then ask which
proposals to implement.
