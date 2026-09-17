# PRD Release Runbook

Procedure `prd-release` follows to promote SANDBOX image tags to Monxa PRD helm charts, and to apply the PRD chart config changes the requester authorizes on the release ticket. Identity, scope, "Never do these" guardrails and failure rule live in agent's own instructions and OUTRANK this file; if two disagree, instructions win — flag mismatch on ticket.

Two runs. Run 1 builds release PR and stops. Run 2 is triggered by comment on ticket.

Deep detail lives in four reference files. Load each when you reach its steps, not before:

| Steps | Reference |
|---|---|
| 2–5 · read `main`, drift table, edits, diff gate | `references/drift-and-edit.md` |
| 3b, 4b · SANDBOX vs PRD config drift, authorized config edits | `references/config-drift.md` |
| 6–7 · per-image research, risk detection, note | `references/release-note.md` |
| 9–10c · full-suite dispatch, tag window, BDD PR | `references/bdd-gate.md` |

---

# Run 1 — build release PR

Triggered when someone assigns you release issue.

## Step 0 — Install helm

You merge to repo that deploys itself to production, so you must be able to render chart before you trust it. Install helm if not already on PATH:

```
command -v helm || {
  curl -fsSL https://get.helm.sh/helm-v3.16.3-linux-amd64.tar.gz -o /tmp/helm.tgz &&
  tar -xzf /tmp/helm.tgz -C /tmp && mkdir -p "$HOME/.local/bin" &&
  mv /tmp/linux-amd64/helm "$HOME/.local/bin/helm"
}
```

`mx-apps` vendors its dependencies (`charts/drunk-app-*.tgz`), so no `helm dependency update` and no registry auth needed.

If helm cannot be installed, still open PR — but say plainly in PR body and on ticket that render was **not** verified, so human merging it knows check is missing rather than assuming it passed silently.

## Step 1 — Read ticket

`multica issue get <id> --output json`, and read its comments — a config request often arrives as comment, not in description.

Note issue creator — you will @-mention them later, and they are the only person whose config instructions you may act on. Do not hardcode name; whoever filed ticket is requester.

Look for three optional override lines:

- `only: paymentGatewayApi, merchantUI` — promote only those keys. If absent, promote every key that differs.
- `bdd-ref: <branch>` — ref of `monxa.bdd-integration` to run smoke suite from in step 9. If absent, use `main`. Never auto-select "most recently active branch": release evidence has to be reproducible.
- `config: <app>.configMap.<Key> = <value or source>` — chart config change to apply in step 4b. Prose request naming app, key and value source counts too. Zero or many.

If issue is not in project `e2ffb49d-9d34-4d8a-9147-0ead4171de8c`, move it in first:
`multica issue update <id> --project e2ffb49d-9d34-4d8a-9147-0ead4171de8c`

Set issue to `in_progress`.

## Steps 2–5 — Check out, compute drift, apply edits, diff gate

**Load `references/drift-and-edit.md` now and follow it exactly.** It covers: checking out both repos and reading tags from `origin/main` (never working tree — stale read promotes wrong tags to production), computing drift table from image-tag block, the config drift report and authorized config edits (which it hands to `references/config-drift.md`), applying edits per authoritative key→image mapping, and eight-item diff gate including `helm lint` and `helm template`.

Do not proceed to Step 6 until every diff-gate item passes. Any failure aborts per failure rule.

## Steps 6–7 — Research changes and write release note

**Load `references/release-note.md` now and follow it exactly.** It covers: resolving each image to its source repo and git ref, fetching compare via `gh api`, filtering commit subjects mechanically, detecting risk items by changed-path grep and subject scan, and four-section note structure.

Add two more sections when this run carried config work: `## Config drift — SANDBOX vs PRD` (the step 3b report, every run) and `## Config changes` (what step 4b applied, only when it applied something). Both are specified in `references/config-drift.md`, including the redaction rule — never paste a webhook URL, signed URL, key or connection string into a PR body or ticket comment.

Do not write `## SANDBOX BDD verification` section here — it is added in Step 10, after suite has actually run. Never pre-announce result you do not have.

## Step 8 — Branch, commit, push, PR

Branch `release/prd-<issue-id>` from `origin/main`. Commit changed files with message naming promoted keys and any config keys applied. Push, then `gh pr create` targeting `main`, using step 7 release note as PR body (pass it with `--body-file`).

## Steps 9–10c — Full BDD suite, tag window, BDD PR

**Load `references/bdd-gate.md` now and follow it exactly.** It covers: choosing ref, coverage-gap report, dispatching FULL suite (no tag filter), single permitted blocking CI wait, subset rule, re-checking tag window, attaching verification section, and opening + merging BDD test PR on green.

**The BDD gate verifies images, never PRD config.** It runs against SANDBOX, which renders SANDBOX's own values — a PRD config key you added cannot be exercised by it, whatever the suite reports. Say that in the verification section whenever the run carried config changes: they are verified by the render check (gate item 8) and by the requester's review, not by the suite.

Two things this gate must never do: merge RELEASE PR (that is Run 2, after requester approves), and describe filtered run as full-suite verification.

## Step 11 — Hand off and stop

Comment on issue with promotion table, config drift table, config changes applied (if any), risk block, BDD result (counts + run link + ref/SHA + coverage gap + tag-window statement), and **both** PR links, plus @-mention of issue creator.

Say clearly what you did and what remains:

- Whether BDD PR was merged (with its commit SHA, confirmed — never report merge you have not verified), or why it was not.
- Any config key reported as **`value needed`** — name it and ask for the value, so the gap does not silently persist into the next release.
- That **release PR is waiting on their decision**, that merging it deploys to production via DevOps auto-sync with no further human step, and whether it is ready or in draft and why.
- Spell out their two options, explicitly:
  1. **Reply `approve` on this ticket** and you will merge release PR and close ticket for them.
  2. **Merge it themselves** and reply here, and you will verify and close.

Leave issue **`in_progress`**. Nothing has shipped to production yet, so it is not `done`.

Never set issue to `in_review`, however much "awaiting review" describes it. `in_review` fires no trigger in Multica, so their approval reply would wake nobody and release would strand. `in_progress` is what keeps this ticket listening.

Do not wait for helm CI, for DevOps, or for their reply; end your turn.


---

# Run 2 — approve, close out, or amend

You are woken by comment on ticket. Read it and pick case. If you cannot tell which case applies, use case C — never guess your way into production merge.

## Case A — requester approves; you merge and close

They replied approving release: `approve`, `approved`, `go ahead`, `ship it`, `merge it`, or unmistakably equivalent. **They have made deploy decision; you execute it.**

**Re-verify before merging.** Their approval covers what you showed them, not whatever is true now. All of these must still hold:

1. **PR head is unchanged** since BDD report — `gh pr view <pr> --json headRefOid`. If someone pushed to release branch, evidence no longer describes what would merge. Your own Case D config push moves this head too — if you amended the PR after the report, treat it as changed and re-report before merging.
2. **SANDBOX tags still match promoted set** — re-read `origin/main:charts/monxa-apps/values.yaml`. If SANDBOX has moved on, report is no longer evidence for these tags.
3. **PR is still mergeable** — no conflict with `main`.
4. **`helm template` still renders** PR head with promoted tags and any applied config keys present.

If any fails: **do not merge.** Comment saying exactly which check went stale and what it means, and that release needs fresh run. Leave issue `in_progress`. Their approval does not make stale check current.

If all hold:

1. If release PR is in draft, mark it ready: `gh pr ready <pr> --repo the-wixo/monxa.helm-charts`. Draft here means BDD suite was red — their approval covers that, since they were told.
2. If BDD PR is still open and its suite was green, merge it first.
3. Merge release PR: `gh pr merge <pr> --repo the-wixo/monxa.helm-charts --merge`.
4. **Confirm it landed** — `gh pr view <pr> --json state,mergedAt,mergeCommit`. Never report merge you have not verified.
5. Comment with merge commit SHA, that `build-push-helm.yml` and `acr-sync.yml` are now running, and that DevOps `mx-apps` will auto-sync new chart to production. Say what they should watch.
6. Set issue **`done`**.

Do not wait for workflows or for DevOps to finish — report them as in flight and end your turn.

## Case B — they merged it themselves

```
gh pr view <pr-number> --repo the-wixo/monxa.helm-charts --json state,mergedAt,mergeCommit
```

- **Merged:** comment confirming with commit SHA, note DevOps is syncing to production, set issue **`done`**.
- **Not merged:** comment that PR is still open and nothing has shipped. Leave `in_progress`.
- **Closed without merging:** comment that release was abandoned, set issue **`cancelled`**.

## Case D — requester asks for a chart config change on this release

They asked for a `charts/mx-apps/values.yaml` config change while the release PR is open — a new configMap key, a corrected value, closing a gap your step 3b report showed. **This is in scope; do not send them away.** It is the same chart, the same PR, the same approval gate.

1. Run the step 4b authorization test (`references/config-drift.md`). Requester or owner/admin, app and key named, value source named. Anything ambiguous — ask, apply nothing, stay `in_progress`.
2. Apply the edits on the existing release branch, per step 4b's edit rules. Never copy a SANDBOX value.
3. Re-run the full step 5 diff gate, including the render check for each new key.
4. Push to the same release PR and update its body: the new `## Config changes` entries, and the risk line if the change touches a live integration.
5. Comment on the ticket: what you added, where each value came from, that the PR head moved and **the earlier BDD report predates this change** — it verified images against SANDBOX and could never have covered a PRD config value.
6. Leave issue **`in_progress`**. A config change is not approval to merge; they still decide, in Case A.

Requests outside `charts/mx-apps/values.yaml` and `acr-sync/images.json` — chart refactors, new services, template edits, CI changes, other charts — remain out of scope. Say so and point them at `devops`, per your instructions.

## Case C — anything else

Questions, partial feedback, "looks good but…", request to change scope, or wording you are not certain is approval. **Merge nothing.** Answer what was asked, or say plainly that you are not treating comment as approval and ask them to reply `approve` if they want you to merge. Leave issue `in_progress`.

Reading approval into ambiguous comment deploys to production on guess. Cost of asking again is one message.

## Comment style

Write comments and PR bodies with `--content-file` / `--body-file` pointing inside your working directory, never inline and never path outside workdir. Keep issue comments short: table, risk block, link, ask. No process narration.
