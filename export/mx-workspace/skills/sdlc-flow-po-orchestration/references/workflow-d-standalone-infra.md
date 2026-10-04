# Workflow D — Standalone CI/CD & Infrastructure Procedure

`devops` owns standalone infra work end to end. You never spec it and never route it through dev-team, qc-team, release-manager, or spec-review gate. Standalone PR it opens still gets pr-reviewer gate, on same repo-class merge-authority rules as step 2b.

**Two exits. Pick by what requester actually asked for.**

### D1 — Analysis only ("look at X and tell me")

Requester wants information so THEY can decide. Research, post report — evidence at `file:line`, what would have to change, which repos and files, landing rule that applies — mention requester, and **STOP**. Create no sub-tasks, promote nothing, delegate at no confidence level. Workflow A's ≥90% auto-delegate does NOT apply to this class: pipeline or infra change is always requester's call, never yours.

### D2 — Change requested ("update the pipeline / update the chart")

Route it straight to `devops`. Clarify only what genuinely blocks change (never what files answer), then:

1. Create ONE `[P<num>-1] CI/CD change: <scope>` in `mx-main`, parent = main ticket, assignee `devops` (`--assignee-id`, resolved from `multica agent list --output json`), `todo`. Description is self-contained — `devops` must never need to read main ticket: target repo(s) and file paths, what to change and why, acceptance criteria, and **landing rule for that repo class** (app repo → commit directly to `dev`; helm repo → branch + PR to `main`, human merges).
2. **Helm repos only** — also create `[P<num>-2] Merge helm PR (deploy): <scope>`, assignee = requester's member UUID (`--assignee-id`; workspace-owner fallback when creator is agent), `backlog`. Description: review PR `devops` opened and merge it if correct — merging publishes chart, so **merge IS deploy decision** — then flip this ticket `done`.
3. **On P1 done** — re-read report. App repo: verify commit landed on `dev`. Helm repo: verify OPEN PR whose base is `main` (`multica issue pull-requests <p1-id> --output json`); no PR means there is nothing to merge — resolve it with `devops` on their ticket and never promote. Satisfied → promote P2 (`backlog`→`todo`) with ONE comment carrying PR link and requester's MEMBER mention.
4. **On P2 done** — verify PR is merged, then flip MAIN ticket `done` with plain summary: what changed, commit or PR link, and where it landed. No mentions.
5. **No other phases exist in this flow** — no `[S#]` spec review, no `[P#-2a]` release, no `[P#-2b]` argoCD ticket, no `[P#-3]` BDD phase. If change genuinely warrants integration testing afterwards, say so in final summary and let requester file it.
