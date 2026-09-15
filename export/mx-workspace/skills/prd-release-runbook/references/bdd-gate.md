## Step 9 — Run the FULL BDD suite against SANDBOX

The PR now exists. Verify the images you are promoting by exercising SANDBOX, which is where those exact tags are already deployed.

**First, choose the ref.** New BDD tests land on `dev` and reach `main` at release time, so which ref you run decides whether the release is verified against current tests.

```
gh api "repos/the-wixo/monxa.bdd-integration/compare/main...dev" --jq '"ahead=\(.ahead_by) behind=\(.behind_by) \(.status)"'
```

- `ahead_by > 0` → **test `dev`**. It carries tests `main` lacks, and it is the head of the BDD PR you will open in step 10 — so the ref you test is the ref that gets merged.
- `ahead_by == 0` → **test `main`**. `dev` holds nothing new; there is nothing to promote and you will open no BDD PR. Say so; never record a no-op merge in a release trail.
- A `bdd-ref:` line on the ticket overrides all of this. Use it verbatim and skip the comparison.

**Report the coverage gap rather than fixing it.** When `dev` is also *behind* `main` (`behind_by > 0`), main holds test commits that `dev` — and therefore this run — did not exercise; they can arrive on main from branches that never pass through `dev`. Do NOT merge `main` into `dev` to close this. State it in the PR: the ref tested, its short SHA, and "N test commits present in `main` were not exercised by this run."

**Then dispatch** — do NOT run Playwright in this runtime. The workflow pins node 20 while this runtime has node 26, and it needs credentials this runtime should not carry.

**This gate is the FULL BDD suite, unfiltered.** It is the only point in the whole SDLC where the entire suite runs: qc-team's cycle gate runs an impacted subset by design, so a PRD release is the last chance to catch a regression outside the neighbourhood of any one change. Dispatch the on-demand SANDBOX BDD workflow with no tag filter:

```
gh workflow list --repo the-wixo/monxa.bdd-integration
gh workflow run <workflow-file> --repo the-wixo/monxa.bdd-integration --ref <chosen-ref>
gh run list --workflow <workflow-file> --repo the-wixo/monxa.bdd-integration --limit 1 --json databaseId,url,headBranch
```

Resolve `<workflow-file>` from `gh workflow list` rather than hardcoding it — the workflow that serves this gate may be renamed. Pass whatever input that workflow exposes for running everything (no `--grep`, no tag filter, `suite=full` or equivalent). If it exposes no such input, dispatch it as-is and follow the subset rule below.

Confirm the run you picked up reports the ref you dispatched before trusting it as this release's evidence.

**Subset rule — never let a filtered run stand in for the full suite.** After the run, establish what it actually executed (the workflow's run command in its logs or definition, and the scenario count in the report). If it applied a tag filter or otherwise ran a subset:

- Say so in the risk block, verbatim: **"the full-suite gate was NOT satisfied — this run executed `<filter>` only (N scenarios)."**
- **Convert the release PR to draft** (`gh pr ready <pr> --repo the-wixo/monxa.helm-charts --undo`) and say why on the ticket.
- Do not abort the release — the requester may still choose to ship — but never describe a subset run as full-suite verification, and never quietly omit the distinction.

Then wait **once**, in a single blocking foreground call — this is the one CI wait you are permitted, because the report is part of what you were asked to deliver:

```
gh run watch <run-id> --repo the-wixo/monxa.bdd-integration
```

Do not wrap this in a retry or sleep loop, and do not split "start the run" and "collect the result" across turns.

Then pull the machine-readable result:

```
gh run download <run-id> --repo the-wixo/monxa.bdd-integration --name cucumber-json-report --dir ./bdd-report
```

Summarise from the cucumber JSON: scenarios passed, failed, skipped; and for each failure the scenario name and the step that failed. If the artifact is missing or unparseable, say exactly that — never infer a pass from a green run conclusion alone.

**If the dispatch or the run itself fails to produce a report** (workflow errored, artifact absent, ref invalid): say so plainly in the PR and on the ticket. Never describe tests as passing, and never quietly omit the section — an absent report must be visible as absent.

## Step 10 — Check the tag window, then attach the report

**This check is the point of the exercise; do not skip it.** The suite tested SANDBOX *live*, but the PR promotes a snapshot of SANDBOX tags taken earlier. SANDBOX moves often — it moved twice during this agent's design.

Re-read the SANDBOX image tags from `origin/main:charts/monxa-apps/values.yaml` (fetch again first). Compare to the set you are promoting:

- **Identical** — state in the PR that SANDBOX was unchanged for the duration of the run, so the report is evidence for exactly the promoted tags.
- **Different** — state loudly, in the risk block, which keys moved and that **the BDD report is not evidence for the promoted set**. Do not bury this in the test section. Do not silently continue as if the report were valid.

Add a `## SANDBOX BDD verification` section to the PR body (`gh pr edit <pr> --body-file`) containing: pass/fail/skip counts, each failure with its failing step, the workflow run URL, the ref and short SHA tested, the coverage-gap line from step 9, and the tag-window statement above.

**State the executed scope precisely, in the section's first line.** A full unfiltered run is **"full BDD suite (N scenarios, no tag filter)"**. Anything filtered is **"SUBSET ONLY — `<filter>`, N scenarios; the full-suite gate was NOT satisfied"**. Never write a bare "BDD integration tests passed": with no scope attached it reads as full coverage, and if the run was filtered that is a false claim on a production release note.

**On failure, convert the release PR to draft** so it cannot be merged by reflex:

```
gh pr ready <pr-number> --repo the-wixo/monxa.helm-charts --undo
```

Say on the ticket that you drafted it and why. A failing integration suite is not automatically a stop — the requester decides — but a red report on a mergeable production PR must not look ready.

## Step 10b — Open the BDD PR, but only on green

Only when BOTH hold: you tested `dev` (it was ahead of `main`), and the suite passed.

```
gh pr create --repo the-wixo/monxa.bdd-integration --base main --head dev \
  --title "BDD tests for PRD Release YYYY-MM-DD" --body-file <path>
```

Body: the tests that passed, the workflow run URL, the SHA tested, and a link to the release PR. Then link back the other way — edit the release PR to reference the BDD PR, so a reader of either finds the other.

Never open this PR when the suite failed: `main` is the PRD test baseline and the source of the published report, and it must never receive tests that did not pass against SANDBOX. Never open it when `dev` was not ahead — there is nothing to merge.

If the PR cannot be created (conflict with `main`, branch protection, a PR already open for `dev`), say so on the ticket and in the release PR, and continue without it. Do not force it. Merging it happens in step 10c, not here.

## Step 10c — Merge the BDD PR (and only the BDD PR)

Merge the BDD test PR when all three hold:

1. A BDD PR was opened — i.e. `dev` was ahead of `main`.
2. The suite reported **zero** failures, with a present and parseable report.
3. GitHub reports the PR mergeable (no conflict, no failing required check).

```
gh pr merge <bdd-pr> --repo the-wixo/monxa.bdd-integration --merge
```

`main`'s suite then holds exactly the tests that verified this release. Confirm the merge landed rather than assuming it did.

If it will not merge — conflict, branch protection, anything — say so on the ticket and in the release PR, and continue. Never force it.

**Do not merge the release PR in this run.** However clean everything looks — green suite, clean render, no risk items — the deploy decision is the requester's, and they have not made it yet. Merging publishes to the production ACR and DevOps syncs it unattended. You merge it only in run 2, after they approve on the ticket.

The BDD result does affect how you leave the release PR:

- **Suite green** → leave the release PR ready for review.
- **Suite red or no report** → convert the release PR to draft so it cannot be merged by reflex, and name the failures on the ticket:

```
gh pr ready <release-pr> --repo the-wixo/monxa.helm-charts --undo
```

Note that the tag window and the risk block do **not** gate anything mechanically here — they are reported so the human deciding the merge can weigh them. Report them accurately and let them decide.
