---
name: helm-chart-delivery
description: >-
 Safe procedure for changing GitOps helm chart repository — read values from
 remote not worktree, verify render with helm lint/template before
 opening PR, target branch cluster syncs, and never merge.
 Use when editing chart values, templates, resource limits, env blocks, or
 adding service to chart in repo that GitOps controller (Argo CD, Flux)
 auto-syncs.
category: devops
triggers:
 - helm
 - helm chart
 - chart values
 - argocd
 - argo cd
 - gitops
---

# Helm Chart Delivery

**In GitOps repo, merging PR *is* deploy.** There is no separate release step to catch mistake — controller syncs whatever lands on tracked branch, with prune and self-heal enabled. Treat merge as production action owned by human.

## Before you touch anything: identify tracked branch

Chart repos do **not** follow app-repo `feature → dev → main` model. Establish, for specific repo:

- Which branch does GitOps controller track?
- Does a `dev` branch exist, and does anything promote it to tracked branch?

A `dev` branch that nothing promotes is **not safe staging area — it is dead end.** A commit there never ships, and change silently does nothing. Confirm this from repo and your instructions; do not assume app-repo convention applies.

## Read current values from remote, never worktree

An agent checkout may sit on stale per-agent branch from earlier run. Reading working tree can show you values that were never on tracked branch.
```bash
multica repo checkout <url> --ref <tracked-branch>
git fetch origin <tracked-branch>
git show origin/<tracked-branch>:<path/to/values.yaml>    # the real current state
```
## Make change

Locate blocks by their **comment headers or keys**, never by hardcoded line numbers — charts get reordered and line-number edit silently lands in wrong block.

## Verify render before opening PR

This is step that catches failure that matters: edit that parses fine but never reaches templates.
```bash
helm lint .
helm template .            # from the chart directory
```
Confirm **your change appears in rendered output**. A value that still renders as OLD result means your edit did not take effect — wrong file, wrong key path, or overridden downstream. Fix it before opening anything.

If `helm` is not on PATH, install it. If you cannot, **say so explicitly in PR body** — never let reviewer assume verification passed silently.

## Open PR — and stop

Create branch on remote without checking it out (see `sdlc-gitflow` for why):
```bash
git push origin origin/<tracked-branch>:refs/heads/chore/<issue-key>
git push origin HEAD:refs/heads/chore/<issue-key>
gh pr create --head chore/<issue-key> --base <tracked-branch> --title "[<ISSUE-KEY>] ..." --body-file <path>
```
Write the PR body per `sdlc-gitflow` **PR body**:

1. **Summary** — what changed and why, with a `diff` sketch of the values that change
2. **Evidence** — the `helm lint` and `helm template` results showing the NEW value, or `Not verified: helm template — <why>`
3. **Merge danger** — Blast radius `deploy — merging this deploys to <environment>`

Then **stop**. Report PR link. A human reviews and merges.

## Never

- **Never merge chart PR.** The merge is deploy decision and it belongs to requester.
- **Never commit directly to tracked branch.**
- **Never commit to a `dev` branch in chart repo** unless you have confirmed something promotes it.
- **Never wait for GitOps controller to sync.** Report PR and finish.
- **Never bump image tags for release** unless that is explicitly your role — image-tag promotion is separate release role.

## Verification checklist

- [ ] Tracked branch identified from repo, not assumed
- [ ] Current values read via `git show origin/<tracked-branch>:<path>`
- [ ] Edit located by key/comment header, not line number
- [ ] `helm lint` clean
- [ ] `helm template` shows NEW value
- [ ] PR base is tracked branch; head is `chore/<issue-key>`
- [ ] PR body states what deploys on merge, and flags any check that could not run
- [ ] PR reported, not merged
