## Step 2 — Check out both repos and read the CURRENT main

```
multica repo checkout https://github.com/the-wixo/infra-v2.helm-charts.git --ref main
multica repo checkout https://github.com/the-wixo/monxa.helm-charts.git --ref main
```

**Critical: checkout puts you on a per-agent branch that may be stale from an earlier run.** Never read tags from the working tree. In each repo, run `git fetch origin main`, then read values with `git show origin/main:<path>`. Branch your release work from `origin/main`, not from whatever the working tree is on.

A stale read produces a wrong drift table and promotes wrong tags to production. This has already happened once during design — treat it as a live hazard, not a theoretical one.

Record `git rev-parse --short origin/main` for `infra-v2.helm-charts`. It goes in the release note as the provenance of the tags.

## Step 3 — Compute the drift table

Parse the image-tag block from `origin/main:charts/monxa-apps/values.yaml`. Every line of the form `key: &anchor "tag"`. Skip blanks and `#` comments. Locate the block by its `# UI Image tags` / `# API Image tags` comment headers, not by hardcoded line numbers — the line range shifts as the file changes.

Read the same keys from `origin/main:charts/mx-apps/values.yaml` in the PRD repo. Build a table of key / old tag / new tag for every key whose tags differ. That is the drift set.

Apply the scope override if the ticket gave one. Report every key you skipped and why.

**If the drift set is empty:** PRD is already at image parity. Do NOT close the ticket yet — check step 3b/4b first. Only when there is also no authorized config change do you comment "PRD is already at SANDBOX parity — nothing to release", set the issue to `done`, open no PR and stop. With authorized config changes, the release continues on those alone (config-only run, see `references/config-drift.md`).

## Step 3b — Config drift report

**Load `references/config-drift.md` now** and follow its Step 3b. It runs every release, right after this table: it compares the per-app `configMap` blocks of the two charts, reports what PRD is missing, and states plainly which differences are by design and must never be closed. It is a report — it authorizes nothing.

## Step 4 — Apply the image-tag edits

Read `monxa.helm-charts/.claude/agents/update-image-tags.md`. It holds the authoritative key→image mapping (which `images.json` repo path each values key corresponds to, and whether it lives in the `images` or `backup_images` array) and the exact edit rules. Follow it verbatim, **including its `helm template` verification** — step 0 installed helm for exactly this. (Earlier revisions of these instructions told you to skip that step because helm was unavailable. That no longer applies; do not skip it.)

If that file is missing, has moved, or its mapping table no longer parses, abort per the failure rule. Say plainly that the mapping source is unavailable. Do not reconstruct the mapping from memory or from the current contents of `images.json` — a wrong mapping ships a wrong image to production.

## Step 4b — Apply authorized config edits

Follow Step 4b of `references/config-drift.md`. Only keys the requester authorized on the ticket are edited, only in `charts/mx-apps/values.yaml`, and a SANDBOX value is never copied into PRD. If nothing was authorized, this step changes no file — that is the normal case.

## Step 5 — Diff gate

All of these must pass. Any failure aborts per the failure rule.

Throughout, **promoted keys** are the image-tag drift set from step 3 and **authorized config keys** are the keys step 4b was authorized to edit. On a run with no authorized config change, the authorized set is empty and the gate is exactly what it always was.

1. `jq . acr-sync/images.json` exits 0 — the JSON is still valid.
2. `git diff --name-only` lists **only** paths from `charts/mx-apps/values.yaml` and `acr-sync/images.json`. A third changed file means something went wrong; abort. On a config-only run `images.json` is untouched and `values.yaml` alone is expected.
3. Every changed line in `values.yaml` is **either** an image-tag line matching `<key>: &<key> "<tag>"` for a promoted key, with the anchor name, indentation and quoting preserved and nothing else on the line changed, **or** an added/changed line for an authorized config key. Any changed line that is neither aborts the run — that is the check that catches an accidental edit to a neighbouring key.
4. Every changed line in `images.json` has a byte-identical repo path — only the `:tag` suffix differs.
5. The number of changed image-tag lines equals the number of promoted keys, **and** the number of added/changed config lines equals the number of authorized config keys. Fewer means a key silently failed to apply; more means you edited something nobody asked for.
6. `cd charts/mx-apps && helm lint .` reports 0 failed charts.
7. `cd charts/mx-apps && helm template .` exits 0 and emits manifests, and the promoted tags appear in the rendered output (`helm template . | grep 'image:'`). A tag that renders as the OLD value means the anchor edit did not reach the templates.
8. Every authorized config key appears in the rendered output under the expected app, with the expected value. A key that renders nowhere reached no container; abort.

Items 1–5 prove *what* changed; 6–8 prove the chart still renders and that the new tags and keys actually reach the manifests. Both halves are required — a values key can be renamed out from under a template and still produce a clean two-file diff.
