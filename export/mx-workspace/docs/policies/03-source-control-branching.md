# Policy 03 — Source Control & Branching

| | |
|---|---|
| **Policy ID** | MX-POL-03 |
| **Version** | 1.2 |
| **Status** | Active |
| **Owner** | dev-leader / qc-leader (cycle git-flow) · release-manager (`dev`→`main`) |
| **Applies to** | Every agent or engineer that branches, commits, pushes, or opens a PR |
| **Related skills** | [`sdlc-gitflow`](../../skills/sdlc-gitflow/SKILL.md) · [`leader-gitops`](../../skills/leader-gitops/SKILL.md) |
| **Enforced at** | PR review gate (base-branch check) · squad leaders |

> **Authority.** This policy is the source of truth for branching & PR discipline.
> `sdlc-gitflow` and `leader-gitops` **implement** it; the PR gate derives its base-branch
> check from it. Amend this policy first, then cascade — see
> [change control](00-policies-index.md#change-control).

## Branch topology at a glance

```
   feature/<key> ──PR──▶  dev  ──release PR──▶  main
        ▲                (INTEGRATION)          (SANDBOX)
        │                     ▲                     ▲
   cut from fresh         all feature/          release-manager
   origin/dev             squad PRs land        ONLY  ([P#-2a])
   (leaders only)         here (gate merges)

   Rules: never `git checkout` a shared branch (locks it) · push by refspec ·
          every PR carries explicit --head AND --base · a PR based on main = defect.

   Helm/GitOps repos DO NOT follow this — chore/<key> ▶ PR to tracked branch ▶ human merges
   (merge = deploy). See Policy 08.
```

## Purpose

Multiple agents share repos through linked worktrees; a careless checkout or a
mis-targeted PR can lock a branch against everyone or push feature work straight at
production. This policy fixes a branch/PR discipline that is safe under concurrency and
leaves a reviewable, bisectable history.

## Scope

All application repos. **Helm chart repos are different** — see statement 8 and
[Policy 08](08-release-management.md).

## Policy statements

1. **Topology:** `feature/* ──PR──> dev ──PR──> main`. `dev` = INTEGRATION, `main` = SANDBOX. Every feature branch is cut from freshly fetched `origin/dev`; every squad/feature PR targets `dev`.
2. **Only two roles touch `main` in app repos.** `release-manager` is the **only** agent that opens/merges the single `dev`→`main` release PR (`[P#-2a]`), authorized by product-owner. A feature PR based on `main` is a defect — fix the base to `dev`.
3. **Only squad leaders cut branches and open PRs into `dev`** — inline, per [`leader-gitops`](../../skills/leader-gitops/SKILL.md), never as Branch/PR sub-tasks. One PR per squad cycle: head = the feature branch, base = `dev`.
3b. **Squad members never create a branch, and never push one of their own.** The `agent/...` branch the runtime puts a member on is a scratch worktree, not a delivery target. A member delivers only by refspec onto the leader's feature branch, and **never runs a bare `git push`** — with no refspec git pushes the current branch to origin under its own name, which delivers nothing and leaves a stray `agent/...` branch behind. A member whose sub-task names no branch, or whose named branch is absent from origin (`git ls-remote origin <branch>` empty), stops and asks the leader for it (`blocked` on its OWN sub-task + its handoff line on the parent, [Policy 05](05-sdlc-delivery-lifecycle.md) statement 5); it never cuts the branch itself, not even when the code is finished and correct.
3c. **A push is proved against the remote.** `git rev-parse HEAD` must equal the SHA `git ls-remote origin <feature-branch>` prints, and that SHA goes in the completion report. The local `origin/<feature-branch>` tracking ref is not proof: after a bare push it still points where it did before, so the usual `git rev-parse origin/<branch>` check passes while the remote never moved (drunk-workspace DRK-1353, 2026-09-16 — the fix sat on the member's `agent/...` branch and the leader had to fast-forward the feature branch by hand).
4. **Never `git checkout` a shared branch** (integration, production, or a feature branch). A checkout locks the branch in one worktree until *after* your task ends, stalling other agents. Stay on your own auto-generated `agent/...` branch and operate on the remote.
5. **Branch and push by refspec, without checking out:**
   ```bash
   git push origin origin/dev:refs/heads/<feature-branch>      # create from fresh origin/dev
   git push origin HEAD:refs/heads/<feature-branch>            # deliver commits
   ```
   Always branch from freshly fetched `origin/dev`, never a stale local ref. Verify local HEAD SHA == remote branch SHA.
6. **Every PR carries explicit `--head` AND `--base`.** `gh pr create` without `--base` silently targets the repo default (production); without `--head` it produces an empty/wrong diff that still reports success. After creating, verify `baseRefName`, `headRefName`, a **non-empty** `--stat` diff, and `mergeable == MERGEABLE`. A wrong head is not editable — close and recreate.
7. **PR bodies never contain `Closes`/`Fixes`/`Resolves` next to an issue key** — that auto-completes the issue and kills the remaining pipeline phases. PR titles carry the issue-key prefix. Check for an existing open PR before opening a second.
8. **Helm/GitOps repos do not follow the `dev` rule.** `devops` branches `chore/<issue-key>` from `origin/<tracked-branch>`, opens a PR to that branch, and **stops** — merging a chart PR *is* the deploy and only a human does it. Never commit to a `dev` branch that nothing promotes (inert), never merge `main`. See [Policy 08](08-release-management.md) and [`helm-chart-delivery`](../../skills/helm-chart-delivery/SKILL.md).
9. **Merge conflicts:** resolve mechanical ones (whitespace, imports) on a *detached* checkout of the feature branch (`git checkout --detach origin/<branch>` takes no lock), commit, push by refspec, re-check `mergeable`. Escalate **substantive** conflicts (overlapping logic, deleted code) to the code's owner — never guess.

## Best practices for .NET developers

- Prefer a branch + PR even for a small direct request — one extra command buys a reviewable record and a bisectable `dev` history.
- Report the branch name **and** its base commit SHA so whoever implements knows exactly where they are.
- A direct-commit exception (CI/CD agents) covers *what you commit to*, never *whether you check out* — every mode uses `git push origin HEAD:refs/heads/<target>`.

## Definition of Done / compliance

- [ ] Branch cut from freshly fetched `origin/dev`; no shared branch ever checked out.
- [ ] Push verified (local SHA == remote SHA).
- [ ] PR created with both `--head` and `--base`; refs verified; `--stat` non-empty.
- [ ] `mergeable == MERGEABLE`; title carries the issue-key prefix; no `Closes/Fixes/Resolves`.

## Enforcement

`pr-review-gate` treats a PR based on `main` as an automatic `blocking` finding and
verifies the base is `dev`. Squad leaders own the cycle git-flow per `leader-gitops`;
`release-manager` owns the `dev`→`main` line.

## Exceptions & waivers

- A **direct-commit-to-integration** exception exists only when stated explicitly in an agent's own instructions (typically CI/CD). No exception ever permits committing directly to the production branch.
- Dual-mode agents pick the target from how the task arrived (named feature branch → that branch, PR owned by the squad leader; direct request → own `chore/<key>` branch + PR).

## References

- [`sdlc-gitflow`](../../skills/sdlc-gitflow/SKILL.md) — mechanics: branch/commit/PR/conflict, the three failure modes, verification checklist.
- [`leader-gitops`](../../skills/leader-gitops/SKILL.md) — how squad leaders run cycle git-flow inline.
- Branch & environment strategy in [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md).
