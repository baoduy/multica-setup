---
name: leader-gitops
description: Defines dev-leader's own hands-on git-flow: cutting the feature branch and opening the cycle's one PR. Use when dev-leader reaches branch cut at decomposition or PR creation after its gate passes.
---

# leader-gitops — squad leader's git-flow

Git mechanics you (dev-leader) run YOURSELF, inline, at two git points of every cycle: feature-branch cut at decomposition and ONE PR after your gate passes. There are no Branch or PR sub-tasks and no git custodian — do these steps directly in same wake, then keep orchestrating. Git-flow is your ONLY hands-on work: you still never write, edit, or run application or test code, builds, linters, or suites.

## Branch cut — always from latest `dev`, never checked out locally

Your checkout is a linked worktree of ONE shared repo per runtime, and git allows a branch to be checked out in only one worktree at a time — a branch you `git checkout` stays locked against every other agent even after your task ends. Create and update branches you manage on the REMOTE, staying on your auto-generated `agent/dev-leader/<hash>` branch the whole time.

Cut the branch per `sdlc-gitflow` **Creating branch**; the leader-specific rules below apply on top.

- If branch ALREADY exists on origin for this issue key (earlier run, cancelled duplicate cycle): reuse it — never cut a second branch for the same cycle; run conflict procedure below if its tip is behind `origin/dev`.
- Write branch name AND base commit SHA into first implementing sub-task's description so member knows where to work.

## PR creation — you ARE the gate; verify it, then open

**Timing — after everything, before the final gate.** The PR is opened exactly once, when the LAST implementation stage has closed (every Build/Update sub-task `done` or explicitly dropped on the parent) and immediately before you promote Review, which is always the cycle's final stage. Never at branch cut, never on first push, never as a draft to "get CI running" — a PR that exists before the work is finished is reviewed twice and merged once. Everything below is the check you run at that one moment.

Opening PR is the authorization that used to be a separate handoff — so check gate FIRST, every time: every developer's Build is `done` with green suite + ≥80% per-touched-class coverage in its report (or, on a config-only cycle, you verified pushed change via `ls-remote`; on a UI presentation Build, green build, typecheck, lint and existing suites with every skipped test listed, and your follow-up issue filed; on a `build-excluded` Build, green build, existing suites and CI parity with a `Stack evidence` row for every `@stack` scenario; on a `build-waived` Build, green build, existing suites and CI parity), the Review sub-task (if already created) is not `blocked` mid-rework, and feature branch tip matches verified commit (`git ls-remote`). If any of these fail, do NOT open PR — run fix loop instead.

Open and verify the PR per `sdlc-gitflow` **Opening PR** and **PR body**; the leader-specific rules below apply on top.

- **Exactly ONE PR per request cycle** — beyond `sdlc-gitflow`'s "don't open a second," you never open more than one for the whole cycle regardless of how much rework happens.
- **PR title starts with the ROOT main ticket's key** in `[<KEY>]` form (e.g. `[DRN-123]`) so Multica autolinks it, even when the cycle spans sub-tickets.
- **Conflict check** (`gh pr view <PR#> --json mergeable -q .mergeable`): `CONFLICTING` or `UNKNOWN` → run conflict procedure below; only proceed on `MERGEABLE`.
- **Post PR URL as a plain comment on CYCLE PARENT** (pr-reviewer reads it there), then create/promote Review stage. You never merge PR — pr-reviewer owns merge.

## Conflicts — mechanical yourself, substantive to implementer

Run the merge/detect/resolve mechanics per `sdlc-gitflow` **Conflict protocol**; the leader-specific ownership rules below apply on top.

1. **Mechanical conflicts** (whitespace, import reorder, rebase noise, trivial renames): resolve yourself — you run the protocol, not an implementer.
2. **Substantive conflicts** (overlapping logic, deleted code): that is feature code — not yours. Post ONE comment on the Build sub-task whose §3 owns the conflicted paths, with its developer's mention (dev-backend or dev-frontend) and the instruction to report on that sub-task and post its handoff line when pushed; when the fix lands, re-verify mergeability. No fix sub-task. **Exception:** the conflict is an older duplicate root's fix already merged into `dev` → resolve nothing; close the cycle per `sdlc-flow-squad-leader-playbook` `references/recovery.md` (**Duplicate roots**).
3. `MERGEABLE` must show before you promote the Review stage — not just before "reporting done."

## Worktree-lock release — you own this recovery

`fatal: '<branch>' is already checked out at '<path>'` means a worktree of shared repo still holds that branch (worktrees of finished tasks linger):

1. `git worktree list` — find every path parked on branch.
2. Release each: `git -C <path> switch --detach` (frees branch; keeps that worktree's files intact). If a listed path no longer exists on disk, `git worktree prune`.
3. Confirm with `git worktree list` that no worktree shows branch, then continue.

Prevention is branch-cut rule: branches you manage are never checked out locally, so a lock should only ever come from a legacy worktree.