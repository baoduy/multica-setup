# Policy 03 — Source Control & Branching

| | |
|---|---|
| **Policy ID** | DRK-POL-03 |
| **Version** | 1.3 |
| **Status** | Active |
| **Owner** | release-manager (`dev`→`main`) · dev-leader (cycle git-flow) |
| **Applies to** | Every agent that branches, commits, pushes, or opens a PR in a drunk repo |
| **Related skills** | [`sdlc-gitflow`](../../skills/sdlc-gitflow/SKILL.md) · [`leader-gitops`](../../skills/leader-gitops/SKILL.md) |
| **Enforced at** | `pr-review-gate` (base-branch check) · dev-leader · release-manager |

> **Authority.** This policy is the source of truth for branch topology and PR discipline
> in the drunk factory. `sdlc-gitflow` (mechanics) and `leader-gitops` (leader procedure)
> **implement** it; `pr-review-gate`'s base-branch check derives from it. Amend this policy
> first, then cascade — see [change control](00-policies-index.md#change-control). Where a
> skill and this policy disagree, this policy wins and the skill is corrected.

## Branch topology at a glance

```
   feature/<key>  ──PR──▶  dev  ──ONE release PR──▶  main
        ▲                (INTEGRATION)              (RELEASE)
        │                     ▲                          ▲
   cut from fresh          every cycle PR           release-manager
   origin/dev              lands here                ONLY, per cycle
   (dev-leader only)       (pr-reviewer merges)      (product-owner authorizes)

   Rules: never `git checkout` a shared branch (locks it) · push by refspec ·
          every PR carries explicit --head AND --base · a PR based on main = defect ·
          merging main triggers CI publish (NuGet/npm/image) — there is no deploy step.
```

## Purpose

drunk-workspace has **no deployed environment** — merging `main` is the release act
itself (CI publishes the package or image straight off it). A careless checkout or a
mis-targeted PR does not just risk a bad merge, it risks accidentally shipping. This
policy fixes a branch/PR discipline that is safe under multi-agent concurrency and keeps
`main` reserved for exactly one custodian.

## Scope

Every drunk repo in scope of the factory: the `DKNet` family, `DKNet.Templates`, the
`drunk-pulumi-*` packages, and any repo under `drunk-others` (Python MCP services, Docker
images, Helm charts). All of them follow the same `feature → dev → main` model — there is
no separate branch strategy for a different repo class.

## Policy statements

1. **Topology.** `feature/<issue-key> ──PR──> dev ──PR──> main`. `dev` = INTEGRATION; `main` = RELEASE (merging it triggers the CI publish). Every feature branch is cut from freshly fetched `origin/dev`; every squad/feature PR targets `dev`.
2. **`main` has exactly one custodian.** `release-manager` is the **only** agent permitted to target or merge `main`, in every repo, via the single `dev`→`main` release PR (`[P<num>-2]`), authorized by product-owner. A feature or CI/CD PR based on `main` is a defect — fix the base to `dev`.
3. **Only dev-leader cuts branches and opens the cycle PR into `dev`** — inline, per [`leader-gitops`](../../skills/leader-gitops/SKILL.md), never as separate Branch/PR sub-tasks. Exactly one PR per cycle: head = the feature branch, base = `dev`. No QC squad and no separate git custodian exist in drunk — the squad leader is both.
3b. **Squad members never create a branch, and never push one of their own.** The `agent/...` branch the runtime puts a member on is a scratch worktree, not a delivery target. A member delivers only by refspec onto the leader's feature branch, and **never runs a bare `git push`** — with no refspec git pushes the current branch to origin under its own name, which delivers nothing and leaves a stray `agent/...` branch behind. A member whose sub-task names no branch, or whose named branch is absent from origin (`git ls-remote origin <branch>` empty), stops and asks the leader for it (`blocked` + the leader's mention on its OWN sub-task); it never cuts the branch itself, not even when the code is finished and correct.
3c. **A push is proved against the remote.** `git rev-parse HEAD` must equal the SHA `git ls-remote origin <feature-branch>` prints, and that SHA goes in the completion report. The local `origin/<feature-branch>` tracking ref is not proof: after a bare push it still points where it did before, so the usual `git rev-parse origin/<branch>` check passes while the remote never moved (DRK-1353, 2026-09-16 — the fix sat on `agent/dev-backend/1b37847e15ca` and dev-leader had to fast-forward the feature branch by hand).
4. **Never `git checkout` a shared branch** (`dev`, `main`, or any feature branch). A checkout locks it in one worktree until the task ends, stalling every other agent. Stay on the auto-generated `agent/...` branch and operate on the remote.
5. **Branch and push by refspec, without checking out:**
   ```bash
   git push origin origin/dev:refs/heads/<feature-branch>      # create from fresh origin/dev
   git push origin HEAD:refs/heads/<feature-branch>             # deliver commits
   ```
   Always branch from freshly fetched `origin/dev`, never a stale local ref. Verify local HEAD SHA == remote branch SHA before reporting done.
6. **Every PR carries explicit `--head` AND `--base`.** `gh pr create` without `--base` silently targets the repo default (often `main`); without `--head` it produces an empty/wrong diff that still reports success. After creating, verify `baseRefName`, `headRefName`, a **non-empty** `--stat` diff, and `mergeable == MERGEABLE`. A wrong head is not editable — close and recreate.
7. **PR titles carry the ROOT main ticket's key in `[<KEY>]` form; bodies and titles never contain `Closes`/`Fixes`/`Resolves` next to an issue key** — that auto-completes the ticket and kills the remaining pipeline phases. Check for an existing open PR (`gh pr list --head <branch> --base <base> --state open`) before opening a second.
8. **Devops CI/CD changes follow the same `dev` rule — there is no separate track.** `devops` branches `chore/<issue-key>` from freshly fetched `origin/dev`, opens exactly one PR to `dev`, and `pr-reviewer` scores and merges it on APPROVED — identical mechanics to a feature cycle. There is no Helm/GitOps exception in drunk: a Helm chart repo is just another repo in scope, released the same `dev`→`main` way (merge triggers the chart/image publish, not a deploy).
8a. **docs-writer's docs changes follow the same rule.** `docs-writer` branches `docs/<issue-key>` from freshly fetched `origin/dev` (or the repo's default branch where it has no `dev`), opens exactly one PR to it, and `pr-reviewer` scores and merges it on APPROVED. It never commits to a squad cycle's feature branch — dev-team cycles carry no docs stage ([Policy 05](05-sdlc-delivery-lifecycle.md) statement 3a).
9. **Merge conflicts:** resolve mechanical ones (whitespace, import order, trivial renames) on a *detached* checkout of the feature branch (`git checkout --detach origin/<branch>` takes no lock), commit, push by refspec, re-check `mergeable`. Escalate **substantive** conflicts (overlapping logic, deleted code) to the code's owner (dev-backend, via dev-leader) — never guess.
10. **Release-manager's three acts and nothing else:** open `gh pr create --base main --head dev`; check whether the release is critical ([Policy 08](08-container-build-and-release.md) statement 2a) from commit subjects and PR labels alone; and merge it (`--merge`, no squash/rebase, preserving `dev` history) — a critical release only after the resolved owner replies. Never run, read, or wait on application code, tests, builds, or the CI publish itself — that is CI's job, out of scope even for the custodian of the branch it publishes from.

## Roles & responsibilities

- **dev-leader** — cuts the cycle's feature branch, opens the single `feature`→`dev` PR after its own gate passes, resolves mechanical conflicts, never merges (pr-reviewer owns the merge), never targets `main`.
- **devops** — cuts `chore/<issue-key>` from `dev`, opens one PR to `dev`, never merges its own PR, never targets `main`.
- **docs-writer** — cuts `docs/<issue-key>` from `dev`, opens one PR to `dev`, never merges its own PR, never targets `main`.
- **pr-reviewer** — merges every `feature`/`chore`/`docs` PR into `dev` on APPROVED; treats a PR based on `main` as an automatic blocking finding; never touches `main`.
- **release-manager** — the sole agent that opens and merges the `dev`→`main` release PR, holding a critical one for the owner; never creates feature branches; never merges any other PR.
- **product-owner** — authorizes the release phase (`[P<num>-2]`); read-only on code and git, never branches or opens PRs.

## Definition of Done / compliance

- Branch cut from freshly fetched `origin/dev`; no shared branch ever checked out.
- Push verified (local SHA == remote SHA) before any "done" report.
- PR created with both `--head` and `--base`; refs verified; `--stat` non-empty; `mergeable == MERGEABLE`.
- PR title carries the issue-key prefix; no `Closes/Fixes/Resolves` next to an issue key.
- The `dev`→`main` release PR is the only PR in the cycle whose base is `main`, and it was opened and merged by release-manager alone.

## Enforcement

`pr-review-gate` treats a PR based on `main` as an automatic `blocking` finding and
verifies the base is `dev` before scoring or merging. `dev-leader` owns cycle git-flow per
`leader-gitops`, including the branch-gate check on every wake (verify the feature branch
exists on origin before promoting a coding sub-task). `release-manager` owns the `dev`→`main`
line exclusively and self-verifies both refs before merging.

## Exceptions & waivers

- A **direct-commit-to-`dev`** exception exists only when stated explicitly in an agent's
  own instructions (e.g., a CI/CD maintenance agent). No exception ever permits committing
  directly to `main` — there is no deployment to protect against by skipping review, but
  `main` is the publish trigger and stays single-custodian regardless.
- Docs-only and config-only changes still go through a branch and PR — there is no
  direct-to-`dev` shortcut for content, only for the narrow, explicitly-stated CI/CD case
  above.

## References

- [`sdlc-gitflow`](../../skills/sdlc-gitflow/SKILL.md) — mechanics: branch/commit/PR/conflict, the three failure modes, the verification checklist.
- [`leader-gitops`](../../skills/leader-gitops/SKILL.md) — how dev-leader runs cycle git-flow inline (branch cut, the one PR, worktree-lock recovery).
- Branch & release strategy in [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) (the "`main` monopoly" scope note).
- [`agents/release-manager.md`](../../agents/release-manager.md) — the two-acts boundary.
