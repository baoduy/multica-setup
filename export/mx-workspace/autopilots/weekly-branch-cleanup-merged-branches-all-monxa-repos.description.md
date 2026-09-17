Goal: once a month, delete the remote branches in every Monxa repository that are already fully merged into `dev` or `main`, and report exactly what was deleted, what was deliberately kept, and why.

Context:
- Scope is every repo attached to the `mx-jobs` project. Read the list at run time with `multica project resource list e301fbc6-2ee9-48bd-8587-d5626b6176f2 --output json` — do NOT hardcode it, so newly attached repos are covered automatically. As of setup: monxa.auth-api, monxa.email-service, monxa.payment-gateway, monxa.web-hook-deliverer, monxa.bdd-integration, infra-v2.helm-charts, monxa.helm-charts.
- Branch model: `main` = PRD, `dev` = SANDBOX integration. Feature branches merge into `dev`; `dev` reaches `main` through the release PR.
- Deleting a remote branch is irreversible from your side. Every exclusion below is a hard rule, not a preference. When a branch is ambiguous, KEEP it and say so in the report.
- Not every repo has both bases (e.g. infra-v2.helm-charts has `main` and no `dev`). Evaluate against whichever of `origin/dev` / `origin/main` actually exist; never treat a missing base as "merged".

NEVER DELETE:
1. Any long-lived base branch, by exact name: `dev`, `main`, `develop`, `master`, `staging`, `uat`, `qa`, `prod`, `production`. Match the branch name EXACTLY, never by prefix.
2. Any branch not proven merged — it must appear in `git branch -r --merged origin/dev` or `git branch -r --merged origin/main`.
3. Any branch with an open pull request (`gh pr list --state open --json headRefName`).
4. Any branch matching `release/*`, `hotfix/*`, or `v*`.
5. Any GitHub-protected branch. The API refusal is expected — log it as "protected", do not retry, continue.
6. Any branch whose tip commit is less than 14 days old — a just-merged branch may still be needed to reopen a PR.

EXACT-MATCH FILTERING (do not get this wrong):
- When removing a base branch from the merged list, anchor the match: `grep -vE '^origin/(dev|main|develop|master|staging|uat|qa|prod|production)$'`.
- Never use an unanchored `grep -v origin/dev` — `origin/dev` is a prefix of `origin/develop`, so an unanchored filter silently mangles any branch whose name starts with `dev`.

Steps:
1. Read the repo list from the `mx-jobs` project resources.
2. For each repo: `multica repo checkout <url>`, then `git fetch --all --prune`.
3. Determine which bases exist: `git ls-remote --heads origin dev main`.
4. Build candidates: for each existing base, `git branch -r --merged <base>`, collect the `origin/*` branches, and apply the anchored filter above.
5. Apply EVERY exclusion. For the 14-day rule use the tip committer date: `git log -1 --format=%cI <ref>`.
6. Delete each surviving candidate with `git push origin --delete <branch>`. On failure, record the error and continue — never abort the sweep because one delete failed.
7. Post one comment on this issue with the results. Start with a totals line (`N branches deleted across M repos, K kept, F failed`), then one markdown table per repo: Branch | Merged into | Tip date | Age (days) | Action (deleted / kept / failed) | Reason. Close with a `Rule check` section flagging anything ambiguous or wrong about the rules above.
8. Set this issue to `done`.