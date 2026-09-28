# GitHub platform reference (gh CLI)

Verify auth first: `gh auth status` and capture your identity: `SELF=$(gh api user -q .login)`. All commands use `-R baoduy/<repo>` (the checkout may be on a task-scoped branch; never rely on cwd remotes alone).

## Phase 0 — Locate the PR when only the branch is known

```bash
gh pr list -R baoduy/<repo> --head <feature-branch> --state open --json number,url,isDraft,baseRefName
```

## Phase 0.5 — State guard (pipeline mode, before any collection)

```bash
gh pr view $PR -R $R --json state -q .state   # MERGED → short-circuit done; CLOSED → blocked path; OPEN → continue
```

## Phase 1 — Collect

```bash
PR=123; R="baoduy/<repo>"
mkdir -p .pr-review/$PR
gh pr view $PR -R $R --json title,body,author,baseRefName,headRefName,url,isDraft,labels,reviewDecision > .pr-review/$PR/meta.json
gh pr diff $PR -R $R > .pr-review/$PR/diff.patch
gh pr view $PR -R $R --json files -q '.files[].path' > .pr-review/$PR/files.txt
gh pr view $PR -R $R --json comments,reviews > .pr-review/$PR/discussion.json
gh pr view $PR -R $R --json commits -q '.commits[].messageHeadline' > .pr-review/$PR/commits.txt
gh pr checks $PR -R $R > .pr-review/$PR/checks.txt || true
```

Gate-relevant fields: `isDraft` (draft ⇒ never approve), `baseRefName` (must be `dev`), `author.login` vs `$SELF` (self-authored ⇒ votes impossible), `reviewDecision` (already `APPROVED` by a human ⇒ comment only, never duplicate votes).

**Coverage on changed lines:** if CI publishes a coverage artifact (Cobertura/lcov), download it (`gh run download -R $R --name coverage`) and intersect with `files.txt`. Otherwise use the coverage numbers dev-backend measured and reported per touched class on the cycle's Build sub-task (its done gates at >=80% per touched class before the PR stage — cite that comment in your report). Otherwise, if the repo's test suite runs cheaply, run it once with coverage from the checkout (read-only; do not commit anything). Else mark coverage **unknown** — state it in the report; it neither caps the score nor blocks the merge. A config/docs-only diff has no coverable lines; say so in the report.

## CI — wait, re-run, attribute

```bash
gh pr checks $PR -R $R --json name,state,link      # poll every ~2 min, foreground, max 30 min total
RUN=$(gh run list -R $R --branch <feature-branch> --json databaseId,conclusion -q '[.[]|select(.conclusion=="failure")][0].databaseId')
gh run rerun $RUN -R $R --failed                    # ONE re-run of the failed jobs, then poll again
gh run list -R $R --branch dev --workflow "<workflow>" --limit 1 --json conclusion,headSha   # same check red on dev?
gh run view $RUN -R $R --log-failed | tail -60      # which project/test failed, or an infra error
```

Quote the evidence you used in the report. No evidence that the PR did not cause a red check means it did.

## Phase 4 — Actions

Report comment (all verdicts):

```bash
gh pr comment $PR -R $R --body-file .pr-review/$PR/report.md
```

APPROVED (score ≥ bar, zero `blocking`):

```bash
# only when a release-review trigger applies (SKILL.md, Release-review label):
gh label create release-review -R $R --color B60205 --description "Owner reviews the dev→main release that ships this PR" --force
gh pr edit $PR -R $R --add-label release-review
gh pr review $PR -R $R --approve --body "Automated review gate: score {SCORE}/10. Full report in the PR comments."   # best-effort: skipped when self-authored
gh pr merge $PR -R $R --merge
gh pr view $PR -R $R --json state -q .state   # MUST print MERGED before reporting
```

If `gh pr merge` fails (draft, late conflict, branch protection, missing permission): do NOT retry with `--admin` or enable auto-merge — take the MERGE_FAILED path in `references/multica-flow.md` (to dev-leader) and quote the exact error.

REWORK:

```bash
gh pr review $PR -R $R --request-changes --body "Automated review gate: score {SCORE}/10 — changes requested. Findings are in the PR comments and on the Review sub-task in Multica."
```

**Self-authored fallback:** when `author.login == $SELF`, GitHub rejects BOTH `--approve` and `--request-changes`. Do not treat the rejection as a run failure: post the report comment only, and note in the Multica report that the vote was skipped (self-authored) — a skipped vote does NOT block the merge. The Multica rework comment on the implementer's Build sub-task carries the enforcement. Configuring a dedicated `GH_TOKEN` on this agent gives it its own identity and enables real votes — recheck `$SELF` every run rather than caching the limitation.

## Hard limits

- The ONLY permitted merge is `gh pr merge` of the PR you scored APPROVED in this run, or the ESCALATED or design PR whose owner chose option A — never any other PR, never `--admin`, never auto-merge, never edit the PR base/branch. The only other GitHub writes are report comments, votes and the `release-review` label.
- Never create GitHub issues — findings go to Multica sub-issues only.
- Never print tokens; if auth fails, stop and report per the blocked path in `references/multica-flow.md`.
