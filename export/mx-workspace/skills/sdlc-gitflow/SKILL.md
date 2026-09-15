---
name: sdlc-gitflow
description: >-
  Git branching and pull-request discipline for multi-agent SDLC workflows —
  feature → integration → production topology, remote-only branch operations
  that avoid worktree locks, mandatory explicit --head/--base on every PR, and
  post-create verification. Use whenever an agent creates a branch, commits,
  pushes, or opens/updates a pull request. Covers mechanics of a correct git
  operation; each agent's own instructions govern whether it is authorised to
  perform one.
category: software-development
triggers:
  - gitflow
  - git flow
  - branch
  - pull request
  - pr create
  - merge conflict
---

# SDLC Gitflow

**This skill defines what a correct git operation looks like. Your agent instructions define whether you are allowed to perform it.** If two ever disagree on authority, your instructions win. If they disagree on mechanics, this skill wins.

## Workspace configuration

Values a workspace fills in once. Defaults shown; if your instructions or repo's `CLAUDE.md` state otherwise, those override.

| Setting | Default | Notes |
|---|---|---|
| Integration branch | `dev` | Where feature work merges. Every PR targets this. |
| Production branch | `main` | Release-only. Never a PR target for feature work. |
| Feature branch pattern | `feature/<issue-key-lowercase>-<short-slug>` | Follow repo's existing convention if it differs. |
| Issue key in PR title | `[ABC-123]` prefix | Enables issue↔PR autolinking. |
| Commit style | Conventional Commits (`feat:`, `fix:`, `refactor:`) | |

## Topology

```
feature/*  ──PR──>  dev  ──PR──>  main
                    ▲              ▲
              all feature work   release only
```

Feature work **never** PRs to production branch. Only designated release role opens `dev → main`.

## Three failure modes this prevents

These are not hypothetical — each has broken a real delivery.

### 1. `gh pr create` without `--base` silently targets production

`gh` defaults `--base` to repo's default branch. On a repo whose default is `main`, a PR you meant for `dev` goes straight at production, and it looks normal in CLI output.

### 2. `gh pr create` without `--head` produces a wrong or empty diff

`gh` uses whatever branch is currently checked out — often an agent's own scratch branch. Result is a PR with an empty or unrelated diff that still reports success.

**Therefore: never omit either flag. Always both, always explicit.**

```bash
gh pr create --head <feature-branch> --base dev --title "[ABC-123] ..." --body "..."
```

### 3. `git checkout` of a shared branch locks it against every other agent

When agents share one repo via linked worktrees, git allows a branch to be checked out in only one worktree at a time. A branch you check out stays locked **even after your task ends**, stalling every agent that needs it next.

**Therefore: never `git checkout` integration branch, production branch, or a feature branch.** Stay on your own auto-generated working branch and operate on remote.

## Creating a branch — without checking anything out

```bash
multica repo checkout <repo-url>          # stay on auto-generated agent/... branch
git fetch origin --prune

git ls-remote origin dev                  # ensure integration branch exists
# if missing:
git push origin origin/main:refs/heads/dev

# create feature branch from freshly fetched origin/dev
git push origin origin/dev:refs/heads/<feature-branch>
git ls-remote origin <feature-branch>     # verify non-empty
```

Always branch from freshly fetched `origin/dev`, never from a stale local copy. Report branch name **and** its base commit SHA so whoever implements knows exactly where they are working.

## Committing and pushing

Commit on your own working branch, then deliver with an explicit refspec push:

```bash
git push origin HEAD:refs/heads/<feature-branch>
```

Verify it landed:

```bash
git rev-parse HEAD                              # matches...
git rev-parse origin/<feature-branch>           # ...this
```

Never check feature branch out to push to it.

## Opening a PR

1. **Know exact head branch.** Never infer or guess it. If you were not told which branch, or `git ls-remote origin <branch>` is empty, stop and ask — do **not** fall back to `dev`, `main`, or your own `agent/...` branch.
2. **Check for an existing PR first.** `gh pr list --head <branch> --base dev --state open`. If one exists, update its title/body instead of opening a second.
3. **Create with both refs explicit** (see above).
4. **Verify both refs afterwards:**

```bash
gh pr view <PR#> --json baseRefName,headRefName
```

- Wrong base → fixable: `gh pr edit <PR#> --base dev`
- Wrong head → **not editable on GitHub.** Close it (`gh pr close <PR#>`) and re-create with correct `--head`. Note close-and-recreate when you report.

5. **Diff sanity check:** `gh pr diff <PR#> --stat` must be non-empty and contain work you expect. An empty diff means head is wrong. Never report done on an empty PR.

## Conflict protocol

Run after every PR create/edit, before reporting done:

```bash
gh pr view <PR#> --json mergeable -q .mergeable
```

- `MERGEABLE` → done.
- `CONFLICTING` or `UNKNOWN`:

```bash
git fetch origin
git checkout --detach origin/<feature-branch>   # detached: takes no branch lock
git merge origin/dev
```

- **Mechanical conflicts** (whitespace, import order, trivial renames): resolve, `git commit -m "fix: resolve merge conflicts with dev"`, push via refspec.
- **Substantive conflicts** (overlapping logic, deleted code): do not guess. Leave them, and escalate to whoever owns that code.

Re-check `mergeable` until it prints `MERGEABLE` before reporting done.

## Role boundaries

Workspaces differ in how git authority is distributed. Two common shapes:

- **Dedicated custodian** — one agent owns all branch/PR operations; implementers only commit and push to a branch prepared for them.
- **Self-service** — each agent manages its own branch and PR.

Either way mechanics above are identical. What changes is *who* may act and *when* — that lives in agent instructions, not here. If your instructions say a leader must authorise PR, this skill does not override that.

## Exceptions

An agent may be authorised to commit directly to integration branch — CI/CD and infrastructure agents commonly are, because their changes sit outside application's test surface. That exception must be **stated explicitly in that agent's own instructions**. Absent such a statement, assume feature-branch flow.

No exception ever permits committing directly to production branch.

### Dual-mode agents

An agent with a direct-commit exception often still participates in squad work, where a feature branch already exists. Select target from **how task arrived**, not from a fixed rule:

| Task arrived as | Target | Who opens PR |
|---|---|---|
| Squad sub-task, or names a feature branch | that feature branch | squad's PR owner — not you |
| Direct request, no branch named | your own `chore/<issue-key>` branch → PR to integration branch | you |
| Neither is clear | ask; never guess a target branch | — |

Committing straight to integration branch is **not** default for second row. Prefer a branch and a PR: it costs one command, leaves a reviewable record, and keeps integration branch's history bisectable. Only an agent with an explicit direct-commit exception in its instructions skips it.

**Exception covers *what you commit to*, never *whether you check out*.** These are independent. A direct-commit exception is granted because agent's changes are low-risk; worktree lock has nothing to do with risk — it is a mechanical consequence of `git checkout` that outlives task and blocks other agents regardless of how safe change was. Every mode uses same refspec push:

```bash
git push origin HEAD:refs/heads/<target>
```

One mechanic, several destinations. There is never a reason to check out a shared branch.

## Anti-patterns

1. `gh pr create` without `--base` — silently targets production.
2. `gh pr create` without `--head` — silently produces an empty or wrong diff.
3. `git checkout dev` / `main` / a feature branch — locks it against other agents, potentially past end of your task.
4. Branching from a stale local ref instead of freshly fetched `origin/dev`.
5. Guessing a head branch when task did not name one.
6. Reporting done without verifying `baseRefName`, `headRefName`, a non-empty diff, and `MERGEABLE`.
7. Opening a second PR for a branch that already has an open one.
8. Resolving a substantive logic conflict yourself rather than escalating to code's owner.
9. Feature work PR'd straight to production branch.

## Verification checklist

- [ ] Branch created from freshly fetched `origin/<integration>`
- [ ] No shared branch was ever `git checkout`-ed
- [ ] Push verified: local HEAD SHA == remote branch SHA
- [ ] PR created with **both** `--head` and `--base` explicit
- [ ] `baseRefName` == integration branch, `headRefName` == intended feature branch
- [ ] `gh pr diff --stat` non-empty and contains expected work
- [ ] `mergeable` == `MERGEABLE`
- [ ] PR title carries issue key prefix