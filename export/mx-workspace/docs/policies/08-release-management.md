# Policy 08 — Release Management

| | |
|---|---|
| **Policy ID** | MX-POL-08 |
| **Version** | 1.1 |
| **Status** | Active |
| **Owner** | release-manager (`dev`→`main` SANDBOX line) · prd-release (PRD promotion) · devops (CI/CD & charts) |
| **Applies to** | Every release to SANDBOX and every promotion to production |
| **Related skills** | [`prd-release-runbook`](../../skills/prd-release-runbook/SKILL.md) · [`helm-chart-delivery`](../../skills/helm-chart-delivery/SKILL.md) |
| **Enforced at** | release-manager · prd-release · human merge of chart PRs |

> **Authority.** This policy is the source of truth for releasing & deploying.
> `prd-release-runbook` and `helm-chart-delivery` **implement** it. Amend this policy
> first, then cascade — see [change control](00-policies-index.md#change-control).

## Release & environment flow at a glance

```
   APP REPOS                          HELM / GitOps REPOS (merge = deploy, human only)
   dev ──[P#-2a]──▶ main              chore/<key> ──PR──▶ tracked branch ──human merge──▶ controller syncs
   (release-manager)  │                 (devops opens, never merges; pr-reviewer scores, never merges)
                      │ CI builds image
                      ▼
                   SANDBOX  ◀── 👤 argoCD deploy ([P#-2b], unless BDD waived)
                      │
                      ▼  (PRD promotion, prd-release, TWO runs)
   Run 1: read tags from origin/main ▶ drift table ▶ edits ▶ diff gate (helm lint/template)
          ▶ branch release/prd-<id> from origin/main ▶ PR to main
   Run 2 (ticket comment): full SANDBOX BDD suite from pinned bdd-ref ▶ write verification ▶ human merges

   Guardrails: read values from origin, not worktree · verify render before PR · image-tag promotion = prd-release, never devops.
```

## Purpose

Ship safely across three environments — INTEGRATION (`dev`), SANDBOX (`main`), and
PRODUCTION (GitOps-synced charts) — with clear, single-owner authority at each hop and a
human hand on every production-affecting merge.

## Scope

App-repo releases (`dev`→`main`), SANDBOX deploy, and helm chart promotion to production.
Feature delivery up to the merge into `dev` is [Policy 05](05-sdlc-delivery-lifecycle.md);
branch mechanics are [Policy 03](03-source-control-branching.md).

## Policy statements

1. **Environment model.** `dev` = INTEGRATION, `main` = SANDBOX. Merging into `main` triggers CI to build the image and handle production tagging automatically downstream; a **human** then deploys `main` to SANDBOX via argoCD (`[P#-2b]`).
2. **One release owner.** `release-manager` is the **only** agent that opens/merges the single `dev`→`main` release PR (`[P#-2a]`), authorized by product-owner, in the **application** repos. No agent tags production — that is automatic in CI/CD.
3. **SANDBOX deploy is the requester's call** (`[P#-2b]`), promoted only when `bdd_required ≠ false`. Under a BDD waiver there is no SANDBOX tail: `[P#-2a] done` is terminal and the requester deploys `main` whenever they choose, outside the ticket.
4. **Helm/GitOps repos: merging the PR IS the deploy.** There is no separate release step — the controller syncs whatever lands on the tracked branch, often with prune and self-heal on. Treat the merge as a production action owned by a **human**.
5. **Chart repos do not follow the app-repo `dev` model.** Identify the tracked branch per repo first:
   - `infra-v2.helm-charts` (SANDBOX) — `main` + `release/sandbox`, **no `dev` branch**.
   - `monxa.helm-charts` (PRD) — `dev` exists but **nothing promotes it to `main`** (prd-release cuts release branches from `origin/main`), so a commit on `dev` never ships.
   Never commit to an inert `dev`; never commit or merge `main`.
6. **`devops` opens chart PRs, never merges them.** Branch `chore/<issue-key>` from `origin/<tracked-branch>`, open a PR to that branch, **stop**. `pr-reviewer` may score a helm PR but never merges it. The human merge is the deploy decision (`[P#-2]` for a delegated helm change).
7. **Read values from the remote, never the worktree** (`git show origin/<tracked-branch>:<path>`) — a stale per-agent checkout can show values never on the tracked branch. Locate blocks by comment header/key, never by hardcoded line number.
8. **Verify the render before opening any chart PR** — `helm lint .` and `helm template .`, and confirm **your change appears in the rendered output** (a value still rendering the old result means the edit did not take effect). If helm can't be installed, say so explicitly in the PR body — never let a reviewer assume a verification passed silently.
9. **PRD promotion (`prd-release`) is two runs.** Run 1 builds the release PR from `origin/main` (read tags from `origin/main`, never the working tree; compute the drift table; apply edits per the authoritative key→image mapping; pass the seven-item diff gate incl. `helm lint`/`helm template`; branch `release/prd-<issue-id>` from `origin/main`; PR to `main`). Run 2 (triggered by a ticket comment) runs the full SANDBOX BDD suite from the pinned `bdd-ref` and writes the verification section **after** the suite actually runs — never pre-announce a result.
10. **Image-tag promotion is `prd-release`'s job, never `devops`'s.** `only:` and `bdd-ref:` override lines on the release ticket are honoured; absent `only:`, promote every key that differs; absent `bdd-ref:`, use `main` (never "the most recently active branch" — release evidence must be reproducible).
11. **Multi-arch images.** Every container image a repo builds/publishes MUST be a multi-arch manifest covering **both `linux/amd64` and `linux/arm64`** (`docker buildx --platform linux/amd64,linux/arm64`, or `docker/build-push-action` with both platforms). A new repo's docker/publish workflow is wired multi-arch from the start; a single-architecture published image is a release defect the pr-review gate flags on any `Dockerfile`/build-workflow diff.

## Definition of Done / compliance

- **SANDBOX release:** `dev`→`main` PR merged by release-manager, CI image built; `[P#-2b]` deployed by the requester (unless waived).
- **Chart change:** render verified (change visible in `helm template`), PR opened to the tracked branch, human-merged; the sync confirmed.
- **PRD release:** diff gate passed, release note written from real git compares, full BDD suite green with evidence, PR merged by a human.

## Enforcement

`release-manager` owns the app-repo `main` monopoly; `prd-release` owns PRD image-tag
promotion and the drift/diff/BDD gates; `devops` opens but never merges chart PRs;
`pr-reviewer` scores but never merges a chart PR. Every production-affecting merge is a
human action.

## Exceptions & waivers

- A **BDD integration waiver** removes the SANDBOX deploy/test tail for a feature (`[P#-2a]` terminal) — see [Policy 02](02-testing-and-quality.md).
- If helm cannot be installed, the PR still opens but must state plainly that the render was **not** verified.
- Failure rule: any diff-gate/render failure aborts the release per the agent's own instructions (which outrank the runbook) — flag the mismatch on the ticket.

## References

- [`prd-release-runbook`](../../skills/prd-release-runbook/SKILL.md) — the full PRD promotion procedure (+ `references/drift-and-edit.md`, `release-note.md`, `bdd-gate.md`).
- [`helm-chart-delivery`](../../skills/helm-chart-delivery/SKILL.md) — safe GitOps chart-change procedure.
- Branch & environment strategy and Workflow D in [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md).
