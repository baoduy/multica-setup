# SDLC Gitflow

**This skill defines what correct git operation looks like. Your agent instructions define whether you are allowed to perform it.** If two ever disagree on authority, your instructions win. If they disagree on mechanics, this skill wins.

## Workspace configuration

Values workspace fills in once. Defaults shown; if your instructions or repo's `CLAUDE.md` state otherwise, those override.

| Setting | Default | Notes |
|---|---|---|
| Integration branch | `dev` | Where feature work merges. Every PR targets this. |
| Production branch | `main` | Release-only. Never PR target for feature work. |
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

These are not hypothetical — each has broken real delivery.

### 1. `gh pr create` without `--base` silently targets production

`gh` defaults `--base` to repo's default branch. On repo whose default is `main`, PR you meant for `dev` goes straight at production, and it looks normal in CLI output.

### 2. `gh pr create` without `--head` produces wrong or empty diff

`gh` uses whatever branch is currently checked out — often agent's own scratch branch. Result is PR with empty or unrelated diff that still reports success.

**Therefore: never omit either flag. Always both, always explicit.**

```bash
gh pr create --head <feature-branch> --base dev --title "[ABC-123] ..." --body "..."
```

### 3. `git checkout` of shared branch locks it against every other agent

When agents share one repo via linked worktrees, git allows branch to be checked out in only one worktree at time. Branch you check out stays locked **even after your task ends**, stalling every agent that needs it next.

**Therefore: never `git checkout` integration branch, production branch, or feature branch.** Stay on your own auto-generated working branch and operate on remote.

## Creating branch — without checking anything out

```bash
multica repo list --output json           # copy the URL exactly as registered (drunk registers every repo with its .git suffix)
multica repo checkout <repo-url>          # stay on auto-generated agent/... branch
git fetch origin --prune

git ls-remote origin dev                  # ensure integration branch exists
# if missing:
git push origin origin/main:refs/heads/dev

# create feature branch from freshly fetched origin/dev
git push origin origin/dev:refs/heads/<feature-branch>
git ls-remote origin <feature-branch>     # verify non-empty
```

Always branch from freshly fetched `origin/dev`, never from stale local copy. Report branch name **and** its base commit SHA so whoever implements knows exactly where they are working.

## Working on branch prepared for you

`multica repo checkout` leaves you on auto-generated `agent/...` worktree branch — stay on it (see failure mode 3). Before touching any file, sync your worktree to feature branch tip:

```bash
git fetch origin
git reset --hard origin/<feature-branch>
```

Your task runs in fresh checkout: uncommitted or unpushed work is permanently lost when run ends, and work pushed only to your `agent/...` branch counts as unpushed.

## Committing and pushing

Commit on your own working branch, then deliver with explicit refspec push:

```bash
git push origin HEAD:refs/heads/<feature-branch>
```

Verify it landed:

```bash
git rev-parse HEAD                              # matches...
git rev-parse origin/<feature-branch>           # ...this
```

If push is rejected because branch moved, rebase and push again — never force-push:

```bash
git fetch origin
git rebase origin/<feature-branch>
git push origin HEAD:refs/heads/<feature-branch>
```

Never check feature branch out to push to it, and never push your auto-generated `agent/...` branch name to origin.

## Opening PR

1. **Know exact head branch.** Never infer or guess it. If you were not told which branch, or `git ls-remote origin <branch>` is empty, stop and ask — do **not** fall back to `dev`, `main`, or your own `agent/...` branch.
2. **Check for existing PR first.** `gh pr list --head <branch> --base dev --state open`. If one exists, update its title/body instead of opening second.
3. **Create with both refs explicit** (see above).
4. **Verify both refs afterwards:**

```bash
gh pr view <PR#> --json baseRefName,headRefName
```

- Wrong base → fixable: `gh pr edit <PR#> --base dev`
- Wrong head → **not editable on GitHub.** Close it (`gh pr close <PR#>`) and re-create with correct `--head`. Note close-and-recreate when you report.

5. **Diff sanity check:** `gh pr diff <PR#> --stat` must be non-empty and contain work you expect. Empty diff means head is wrong. Never report done on empty PR.

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

- **Dedicated custodian** — one agent owns all branch/PR operations; implementers only commit and push to branch prepared for them.
- **Self-service** — each agent manages its own branch and PR.

Either way mechanics above are identical. What changes is *who* may act and *when* — that lives in agent instructions, not here. If your instructions say leader must authorise PR, this skill does not override that.

## Exceptions

Agent may be authorised to commit directly to integration branch — CI/CD maintenance agents commonly are. That exception must be **stated explicitly in that agent's own instructions**. Absent such statement, assume feature-branch flow.

No exception ever permits committing directly to production branch.

## Anti-patterns

1. `gh pr create` without `--base` — silently targets production.
2. `gh pr create` without `--head` — silently produces empty or wrong diff.
3. `git checkout dev` / `main` / feature branch — locks it against other agents, potentially past end of your task.
4. Branching from stale local ref instead of freshly fetched `origin/dev`.
5. Guessing head branch when task did not name one.
6. Reporting done without verifying `baseRefName`, `headRefName`, non-empty diff, and `MERGEABLE`.
7. Opening second PR for branch that already has open one.
8. Resolving substantive logic conflict yourself rather than escalating to code's owner.
9. Feature work PR'd straight to production branch.
10. Force-pushing to shared branch — rebase on moved tip and push again instead.
11. Pushing your auto-generated `agent/...` branch name to origin.

## Verification checklist

- [ ] Branch created from freshly fetched `origin/<integration>`
- [ ] No shared branch was ever `git checkout`-ed
- [ ] Push verified: local HEAD SHA == remote branch SHA
- [ ] PR created with **both** `--head` and `--base` explicit
- [ ] `baseRefName` == integration branch, `headRefName` == intended feature branch
- [ ] `gh pr diff --stat` non-empty and contains expected work
- [ ] `mergeable` == `MERGEABLE`
- [ ] PR title carries issue key prefix