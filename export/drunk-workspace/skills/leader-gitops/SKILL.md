# leader-gitops — squad leader's git-flow

Git mechanics you (dev-leader) run YOURSELF, inline, at two git points of every cycle: feature-branch cut at decomposition and ONE PR after your gate passes. There are no Branch or PR sub-tasks and no git custodian — do these steps directly in same wake, then keep orchestrating. Git-flow is your ONLY hands-on work: you still never write, edit, or run application or test code, builds, linters, or suites.

## Branch cut — always from latest `dev`, never checked out locally

Your checkout is a linked worktree of ONE shared repo per runtime, and git allows a branch to be checked out in only one worktree at a time — a branch you `git checkout` stays locked against every other agent even after your task ends. Create and update branches you manage on the REMOTE, staying on your auto-generated `agent/dev-leader/<hash>` branch the whole time:

1. Check out target repo (`multica repo checkout <url>` with the URL exactly as `multica repo list --output json` prints it, `.git` suffix included) and stay on auto-generated branch.
2. `git fetch origin --prune`.
3. Ensure `dev` exists on remote (`git ls-remote origin dev`); if missing, create it from default branch without a local checkout: `git push origin origin/main:refs/heads/dev`.
4. Create feature branch from up-to-date `dev`, again without a local checkout: `git push origin origin/dev:refs/heads/<feature-branch>` — name it `feature/<issue-key-lowercase>-<short-slug>` (repo's existing convention). If branch ALREADY exists on origin for this issue key (earlier run, cancelled duplicate cycle): reuse it — never cut a second branch for the same cycle; run conflict procedure below if its tip is behind `origin/dev`.
5. Verify with `git ls-remote origin <feature-branch>`, then write branch name AND base commit SHA into first implementing sub-task's description so member knows where to work.

Never branch from a stale local copy — always from freshly fetched `origin/dev`. Never `git checkout` `dev`, `main`, or any feature branch, and never leave a worktree parked on a branch another agent will need.

## PR creation — you ARE the gate; verify it, then open

**Timing — after everything, before the final gate.** The PR is opened exactly once, when the LAST implementation stage has closed (every Build/Docs/Update sub-task `done` or explicitly dropped on the parent) and immediately before you promote Review, which is always the cycle's final stage. Never at branch cut, never on first push, never as a draft to "get CI running" — a PR that exists before the work is finished is reviewed twice and merged once. Everything below is the check you run at that one moment.

Opening PR is the authorization that used to be a separate handoff — so check gate FIRST, every time: dev-backend's Build is `done` with green suite + ≥80% per-touched-class coverage in its report (or, on a docs/config-only cycle, you verified pushed change via `ls-remote`; on a UI presentation Build, green build, typecheck, lint and existing suites with every skipped test listed, and your follow-up issue filed), the Review sub-task (if already created) is not `blocked` mid-rework, and feature branch tip matches verified commit (`git ls-remote`). If any of these fail, do NOT open PR — run fix loop instead.

- **Exactly ONE PR per request cycle.** Before creating, run `gh pr list --head <feature-branch> --base dev --state open`. If one exists, update its title/description to current scope and reuse it — never open a second.
- **Never omit `--head` or `--base`:** `gh pr create --head <feature-branch> --base dev --title "..." --body "..."` — without `--base`, gh defaults to `main`, silently targeting release line; without `--head`, gh uses whatever branch happens to be checked out, silently producing a wrong or empty diff.
- **PR title starts with ROOT main ticket's key in `[<KEY>]` form** (e.g. `[DRN-123]`) so Multica autolinks it. NEVER put `Closes`/`Fixes`/`Resolves` + an issue key in title or body — it auto-completes ticket and kills later phases.
- **Verify BOTH refs:** `gh pr view <PR#> --json baseRefName,headRefName` — base MUST be `dev`, head MUST be exact feature branch. A wrong base is fixable (`gh pr edit --base dev`); a wrong head is NOT editable — `gh pr close <PR#>` and recreate with correct `--head`.
- **Diff sanity:** `gh pr diff <PR#> --stat` must be non-empty and contain cycle's pushed work. An empty or unrelated diff means head is wrong — fix it before moving on.
- **Conflict check:** `gh pr view <PR#> --json mergeable -q .mergeable`. `CONFLICTING` or `UNKNOWN` → run conflict procedure below; only proceed on `MERGEABLE`.
- **Post PR URL as a plain comment on CYCLE PARENT** (pr-reviewer reads it there), then create/promote Review stage. You never merge PR — pr-reviewer owns merge.

## Conflicts — mechanical yourself, substantive to implementer

1. `git fetch origin && git checkout --detach origin/<feature-branch> && git merge origin/dev` — detached HEAD, so no worktree takes branch lock.
2. **Mechanical conflicts** (whitespace, import reorder, rebase noise, trivial renames): resolve yourself, `git add .`, `git commit -m "fix: resolve merge conflicts with dev"`, `git push origin HEAD:refs/heads/<feature-branch>`.
3. **Substantive conflicts** (overlapping logic, deleted code): that is feature code — not yours. Post ONE comment on dev-backend's Build sub-task listing conflicted paths, with dev-backend's mention and the instruction to report back on that sub-task with your mention when pushed; when the fix lands, re-verify mergeability. No fix sub-task.
4. Re-run mergeable check — it must print `MERGEABLE` before Review stage is promoted.

## Worktree-lock release — you own this recovery

`fatal: '<branch>' is already checked out at '<path>'` means a worktree of shared repo still holds that branch (worktrees of finished tasks linger):

1. `git worktree list` — find every path parked on branch.
2. Release each: `git -C <path> switch --detach` (frees branch; keeps that worktree's files intact). If a listed path no longer exists on disk, `git worktree prune`.
3. Confirm with `git worktree list` that no worktree shows branch, then continue.

Prevention is branch-cut rule: branches you manage are never checked out locally, so a lock should only ever come from a legacy worktree.