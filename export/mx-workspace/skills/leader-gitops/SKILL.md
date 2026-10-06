# leader-gitops — squad leader's git-flow

The git mechanics you (dev-leader, qc-leader) run YOURSELF, inline, at two git points of every cycle: feature-branch cut at decomposition and ONE PR after your gate passes. There are no Branch or PR sub-tasks and no git custodian — do these steps directly in same wake, then keep orchestrating. Git-flow is your ONLY hands-on work: you still never write, edit, or run application or test code, builds, linters, or suites.

## Branch cut — always from latest `dev`, never checked out locally

Your checkout is linked worktree of ONE shared repo per runtime, and git allows branch to be checked out in only one worktree at time — branch you `git checkout` stays locked against every other agent even after your task ends (this stalled MXW-555). Create and update branches you manage on REMOTE, staying on your auto-generated `agent/<your-name>/<hash>` branch whole time:

1. Check out target repo (`multica repo checkout <url>`) and stay on auto-generated branch.
2. `git fetch origin --prune`.
3. Ensure `dev` exists on remote (`git ls-remote origin dev`); if missing, create it from default branch without local checkout: `git push origin origin/main:refs/heads/dev`.
4. Create feature branch from up-to-date `dev`, again without local checkout: `git push origin origin/dev:refs/heads/<feature-branch>` — name it `feature/<issue-key-lowercase>-<short-slug>` (repo's existing convention). If branch ALREADY exists on origin for this issue key (earlier run, cancelled duplicate cycle): reuse it — never cut second branch for same cycle; run conflict procedure below if its tip is behind `origin/dev`.
5. Verify with `git ls-remote origin <feature-branch>`, then write branch name AND base commit SHA into first implementing sub-task's description so member knows where to work.

Never branch from stale local copy — always from freshly fetched `origin/dev`. Never `git checkout` `dev`, `main`, or any feature branch, and never leave worktree parked on branch another agent will need.

## PR creation — you ARE gate; verify it, then open

**Timing — after everything, before the final gate.** The PR is opened exactly once, when the LAST implementation stage has closed (every Build/Docs/Update sub-task `done` or explicitly dropped on the parent) and immediately before you promote Review, which is always the cycle's final stage. Never at branch cut, never on first push, never as a draft to "get CI running" — a PR that exists before the work is finished is reviewed twice and merged once. Everything below is the check you run at that one moment.

Opening PR is authorization that used to be separate handoff — so check gate FIRST, every time: your squad's verifier verdict is green — for dev-team that is dev-backend's Build `done` with green suite + ≥80% per-touched-class coverage in its report (or, on docs/config-only cycle, you verified pushed change via `ls-remote`), no `Fix:`/`Fix (review):` sub-task is open, and feature branch tip matches verified commit (`git ls-remote`). If any of these fail, do NOT open PR — run fix loop instead.

- **Exactly ONE PR per request cycle.** Before creating, run `gh pr list --head <feature-branch> --base dev --state open`. If one exists, update its title/description to current scope and reuse it — never open second.
- **Never omit `--head` or `--base`:** `gh pr create --head <feature-branch> --base dev --title "..." --body-file <path>` — without `--base`, gh defaults to `main`, silently targeting production; without `--head`, gh uses whatever branch happens to be checked out, silently producing wrong or empty diff (this created zero-content PR on MXW-577).
- **The PR title starts with ROOT main ticket's key in `[MXW-XXX]` form** so Multica autolinks it. NEVER put `Closes`/`Fixes`/`Resolves` + issue key in title or body — it auto-completes ticket and kills later phases.
- **PR body: Summary · Evidence · Merge danger**, per the **PR body** section of `sdlc-gitflow`, passed with `--body-file`. You never run code, so Evidence quotes the members' reports: Before from the Acceptance-tests report (`at_sha`) or the `bug-build` `Repro RED` row, After from the Build's EVIDENCE rows. Door and blast radius come from the spec's §3a and §3b.
- **Verify BOTH refs:** `gh pr view <PR#> --json baseRefName,headRefName` — base MUST be `dev`, head MUST be exact feature branch. A wrong base is fixable (`gh pr edit --base dev`); wrong head is NOT editable — `gh pr close <PR#>` and recreate with correct `--head`.
- **Diff sanity:** `gh pr diff <PR#> --stat` must be non-empty and contain cycle's pushed work. An empty or unrelated diff means head is wrong — fix it before moving on.
- **Conflict check:** `gh pr view <PR#> --json mergeable -q.mergeable`. `CONFLICTING` or `UNKNOWN` → run conflict procedure below; only proceed on `MERGEABLE`.
- **Post PR URL as plain comment on CYCLE PARENT** (pr-reviewer reads it there), then create/promote Review stage. You never merge PR — pr-reviewer owns merge.

## Conflicts — mechanical yourself, substantive to implementer

1. `git fetch origin && git checkout --detach origin/<feature-branch> && git merge origin/dev` — detached HEAD, so no worktree takes branch lock.
2. **Mechanical conflicts** (whitespace, import reorder, rebase noise, trivial renames): resolve yourself, `git add.`, `git commit -m "fix: resolve merge conflicts with dev"`, `git push origin HEAD:refs/heads/<feature-branch>`.
3. **Substantive conflicts** (overlapping logic, deleted code): that is feature code — not yours. Dispatch ONE consolidated `Fix:` sub-task to implementing member (dev-backend / qc-tester) listing conflicted paths; when fix lands, re-verify mergeability.
4. Re-run mergeable check — it must print `MERGEABLE` before Review stage is promoted.

## Worktree-lock release — you own this recovery

`fatal: '<branch>' is already checked out at '<path>'` means worktree of shared repo still holds that branch (worktrees of finished tasks linger):

1. `git worktree list` — find every path parked on branch.
2. Release each: `git -C <path> switch --detach` (frees branch; keeps that worktree's files intact). If listed path no longer exists on disk, `git worktree prune`.
3. Confirm with `git worktree list` that no worktree shows branch, then continue.

Prevention is branch-cut rule: branches you manage are never checked out locally, so lock should only ever come from legacy worktree.
