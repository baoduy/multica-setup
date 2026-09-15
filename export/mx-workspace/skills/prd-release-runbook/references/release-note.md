## Step 6 — Research the changes, per image

For every key in the drift set, gather what actually changed in that service's source repo.

**Resolve the source repo from the image path** you already have from step 4's mapping. An image at `ghcr.io/the-wixo/<name>` corresponds to GitHub repo `the-wixo/<name>`. An image on any other registry (e.g. `healthzUI` → `docker.io/baoduy2412/healthz-ui`) has no source repo you can read — say so explicitly in the note rather than omitting the image.

**Resolve image tag → git ref:**

| image family | image tag | git ref |
|---|---|---|
| API images (`*Api`) | `1.0.191` | prefix with `v` → `v1.0.191` |
| UI images (`*UI`) | `v2026.07.29-925e906` | used verbatim; already a tag |

**Fetch the comparison:**

```
gh api "repos/the-wixo/<name>/compare/<old-ref>...<new-ref>" --jq '{commits: .total_commits, files: (.files|length)}'
gh api --paginate "repos/the-wixo/<name>/compare/<old-ref>...<new-ref>" --jq '.commits[].commit.message | split("\n")[0]'
gh api "repos/the-wixo/<name>/compare/<old-ref>...<new-ref>" --jq '.files[].filename'
```

If either ref does not resolve, state that in the note for that image — "could not resolve `v1.0.191`; changes unknown" — and continue with the others. Never silently drop an image from a production release note; a reader must be able to see that something is unaccounted for.

**Filter commit subjects mechanically, not by judgement:**

- Drop anything matching `^Merge (pull request|branch|remote)`.
- Drop one-word junk subjects (`up`, `wip`, `temp`, bare `fix`).
- Deduplicate.

**Detect risk items mechanically.** Grep the changed file paths for:
`migration`, `.sql`, `appsettings`, `.env`, `Dockerfile`, `entrypoint`, `.csproj`, `package.json`, `Program.cs`.

Then scan the filtered subjects for these, which file paths do not reveal:

- Framework or runtime upgrades (`.NET 10`, node major bumps).
- Reverts of previously merged work.
- Removed or renamed API endpoints — breaking for callers.
- Security-sensitive changes: certificate validation, auth, log scrubbing, secret handling.
- Seed or reference-data changes that alter production data.
- New features shipping behind a disabled flag or kill switch — note that behaviour is unchanged on deploy and the feature is inert until flipped.

## Step 7 — Write the release note

Structure, in this order:

1. **Header** — `# PRD Release YYYY-MM-DD — N image tag(s)`, the `infra-v2.helm-charts` provenance SHA, a link to the Multica issue, the promotion table (key / image / PRD now / PRD after), and a one-line list of the keys already at parity and therefore untouched.
2. **`## ⚠ Deploy risk — read before merging`** — per image, only the risk items from step 6, each with enough detail to act on. Say explicitly when an image has none, and say explicitly when there are no database migrations. This block is what the approver reads first; it must not be padded with routine changes.
3. **`## What's shipping`** — per image: commit and file counts, a compare link, then the filtered subjects grouped into themed paragraphs with bold leads. Collapse churn to its net outcome: if a change was made, reverted, and remade across commits, report where it landed, not the back-and-forth. Push test-only and docs-only work to a single trailing `_Also: …_` line. Call out when two images are related and should ship together.
4. **`## After merge`** — **merging IS deploying.** Merge fires `build-push-helm.yml` (on `charts/**`) and `acr-sync.yml` (on `acr-sync/**`); the new chart is published to `prdappmxacr43o.azurecr.io`, and DevOps `mx-apps` auto-syncs it to production (`automated.enabled: true`, `targetRevision: "1.0.*"`, prune and selfHeal on). There is no human step after the merge. Also state that this repo has no PR-time CI, so the render was validated locally by this agent instead — name the helm version and that the promoted tags were confirmed in the rendered output.

A `## SANDBOX BDD verification` section is appended in step 10, after the smoke suite has actually run. Do not write that section here, and do not pre-announce a result you do not have yet.

Keep the per-service sections at the depth of the grouped summary — themes, not a transcript of every commit. The filtered subject list is your input, not your output.
