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
gh pr create --head <feature-branch> --base dev --title "[ABC-123] ..." --body-file <path>
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

Never run a bare `git push`: with no refspec it pushes your `agent/...` worktree branch under its own name to origin, which delivers nothing and leaves debris.

Verify it landed **against the remote**, not against a local tracking ref — a bare push makes `origin/<feature-branch>` look right while the remote never moved:

```bash
git rev-parse HEAD                              # matches...
git ls-remote origin <feature-branch>           # ...the SHA this prints
```

Report that `ls-remote` SHA in your completion comment. No `ls-remote` line, no delivery.

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
3. **Create with both refs explicit** (see above), the body from a file per **PR body** below.
4. **Verify both refs afterwards:**

```bash
gh pr view <PR#> --json baseRefName,headRefName
```

- Wrong base → fixable: `gh pr edit <PR#> --base dev`
- Wrong head → **not editable on GitHub.** Close it (`gh pr close <PR#>`) and re-create with correct `--head`. Note close-and-recreate when you report.

5. **Diff sanity check:** `gh pr diff <PR#> --stat` must be non-empty and contain work you expect. Empty diff means head is wrong. Never report done on empty PR.

## PR body

Every PR you open uses this body (Policy 03 statement 7a). The release PRs keep the format their own skill sets: release-manager's `dev`→`main` PR. Two readers use the body: a human and the review gate. Write it by the spec writing rules — one idea per sentence, everyday words, numbers as digits.

Write the body to a file inside your working directory and pass `--body-file <path>`. An inline `--body "..."` breaks on backticks and newlines. On a reused PR, run `gh pr edit <PR#> --body-file <path>`.

````markdown
## Summary

<1–2 sentences: what changes, for whom. Spec: <ROOT-KEY> revision <n>.>

<ONE visual, the smallest that shows the change — see below>

## Evidence

- **Before:** `<scenario or test>` red at `<at_sha>` — <why it failed, one line>
- **After:** green at `<head sha>` — <n> passed, 0 failed, 0 skipped · coverage min <n>% · mutation <score>
- **Not verified:** <a check that could not run, and why> — or `none`

## Merge danger

**Door:** two-way | one-way — <why>
**Blast radius:** none | repo | consumers | data | deploy — <who or what could break>
````

Rules:

- **Summary visual.** Pick the smallest view that makes the point: a call tree for runtime flow, a shallow file tree for a layout change or a broad refactor, pseudocode for logic. When the shape already exists and the point is what changes, use a `diff` block over one of those. One visual, rarely two. Keep only the calls, files and states the change touches. Text blocks only, never a ` ```mermaid ` block.

  ```diff
   submitPayout
     validateBeneficiary
  +  checkDailyLimit
     postLedgerEntry
  ```

- **Evidence quotes the stage reports.** Before comes from the Acceptance-tests report (`at_sha`) or a `bug-build`'s `Repro RED` row. After comes from the Build's EVIDENCE rows. A PR with no red-first test (docs, design, chart, CI, UI presentation, a `build-excluded` Build with no `at_sha`, a `build-waived` Build) drops Before and lists the checks that ran instead, one per line: `helm template` showing the new value, `helm-unittest`, a link check, typecheck and lint, each `@stack` scenario's literal output from the Build's `Stack evidence` row.
- **Not verified** names every check that could not run, so no reader assumes it passed. A dev-team Build never reports a check skipped, so on a cycle PR this line is `none`.
- **Door.** Two-way: reverting the merge commit undoes the change. One-way: a field is removed, renamed or changes type; data is migrated or deleted; or a published package or consumed contract breaks (the spec's §3b says `breaking`). Say which.
- **Blast radius.** One word, then who or what could break. Take it from the spec's §3b Public surface and Integration lines. Name a `release-review` trigger (security-sensitive, supply chain) when one applies.
- No `Closes`/`Fixes`/`Resolves` next to an issue key, here or in the title (statement 7).
- Summary, Evidence and Merge danger fit in about 30 lines. A large table (routes, endpoints, per-file numbers) goes after Merge danger, under `## Details`.

Shape adapted from the `pr` skill in mattpocock/skills v1.3 (MIT). The visual menu comes from Dex Horthy's `show-me` skill.

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
- [ ] PR body follows **PR body** (Summary · Evidence · Merge danger), passed with `--body-file`