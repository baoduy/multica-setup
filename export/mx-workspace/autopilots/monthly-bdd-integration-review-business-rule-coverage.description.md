# Goal

Each month, audit whether the `monxa.bdd-integration` suite actually asserts the business rules the payment-gateway code enforces, and file the gaps as a small, deduped set of improvement issues for triage. One run issue, one review, one report.

# Context

- **Audience** — drunkcoding (`04aadf2b-6674-4791-97e6-f8360575f317`). The findings filed under this run issue are the deliverable; this issue itself is the report.
- **Scope** — review target is `https://github.com/the-wixo/monxa.bdd-integration.git`. Business rules are extracted from `https://github.com/the-wixo/monxa.payment-gateway.git`, which is a **read-only source** in this review.
- **Projects** — this run issue lives in `mx-jobs` (`e301fbc6-2ee9-48bd-8587-d5626b6176f2`). Findings are filed into `mx-qc-board` (`32f538b8-2030-4ca4-b2e7-c3b9f1e07066`) as children of this issue.
- **Constraints**
  - **Read-only on both repos.** No branch, no commit, no push, no PR, no test code. The deliverable is issues only; qc-team implements fixes after drunkcoding triages.
  - **Do not execute the suite.** Running scenarios against SANDBOX belongs to `qc-runner`. A red suite is not a finding here; an assertion that cannot fail is.
  - **Cap 10 findings per run**, highest severity first, deduped against everything already filed under the `bdd.review` label (`a37ccb94-f93f-406c-979d-75ab396f411a`). Anything above the cap is listed in the report, never dropped silently.
  - Findings are filed at `--status backlog` with `--assignee-id 04aadf2b-6674-4791-97e6-f8360575f317`. Never `--assignee` (fuzzy name lookup on an unattended run can bind a finding to the wrong person), and never assigned to `dev-team`, `qc-team`, `product-owner`, or the agent itself.
  - A run that finds nothing new says so explicitly. A truncated run that reads as "clean" is worse than no run.
- **Inputs** — none; monthly schedule.

# Steps

1. **Set this issue to `in_progress`.** `multica issue status <this-issue-id> in_progress`.

2. **Invoke the `bdd-review-sweep` skill and follow it end to end.** It is authoritative for every step below — the rule extraction order, the scenario quality bar, the finding classes (`GAP` / `WRONG` / `WEAK` / `NEG` / `SMELL`), the severity ladder, the fingerprint format, and the issue body contract. Do not work from memory and do not restate it here.

   In outline: check out both repos and read their `CLAUDE.md` / `AGENTS.md`; build the CodeGraph index on payment-gateway; extract the business-rule catalogue (domain invariants and state machine, application validators and idempotency, API error contracts, config-driven limits); then map every rule to the scenarios that assert it.

3. **Dedupe before filing anything.** List the issues carrying the `bdd.review` label, read their `bdd_fingerprint` metadata, and skip any fingerprint already filed and still open. A run that re-files last month's list is a failed run.

4. **File the findings** as children of this issue (`--parent <this-issue-id>`), `--project 32f538b8-2030-4ca4-b2e7-c3b9f1e07066`, `--status backlog`, `--assignee-id 04aadf2b-6674-4791-97e6-f8360575f317`. Title prefix `[BR<N>-<n>] [<CLASS>] <what is untested or wrong, and where>`, where `N` is the numeric part of THIS issue's identifier and `n` restarts at 1. Then, per finding, a second call to label it — `issue create` takes no label flag:
   ```
   multica issue label add <issue-id> a37ccb94-f93f-406c-979d-75ab396f411a
   ```
   Set `bdd_fingerprint`, `bdd_class`, `bdd_severity` and `bdd_rule` metadata on each one so next month's run can dedupe against it. A missing label or metadata key is a reporting gap, not a failed review — record it and carry on.

5. **Post the report and close.** One comment on this issue via `--content-file`, then `done` — never `in_review`. The report carries: rules extracted by area · covered / uncovered / weakly covered with the raw counts behind the coverage figure · findings filed with links and the `[BR<N>-<n>]` range consumed · findings deduped away against earlier runs · everything dropped above the cap · anything that could not be analysed, and why.