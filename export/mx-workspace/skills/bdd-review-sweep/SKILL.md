---
name: bdd-review-sweep
description: End-to-end workflow for the recurring BDD integration review — extract the business rules from the payment-gateway solution (read-only), map every rule to the Gherkin scenarios in monxa.bdd-integration, classify the gaps, dedupe against findings already filed, and file a capped set of improvement issues for human triage. Use on every BDD Integration Review run; never work from memory.
---

# BDD Review Sweep

The workflow for a business-rule coverage review of `monxa.bdd-integration`.

**What this review answers:** does the BDD integration suite actually assert the business behaviour the payment-gateway code implements — not "do the tests pass".

## 0. Boundaries — read before anything else

| Repo | Access | Why |
|---|---|---|
| `https://github.com/the-wixo/monxa.payment-gateway.git` | **read-only** | Source of truth for business rules. Never branch, never edit, never push. |
| `https://github.com/the-wixo/monxa.bdd-integration.git` | **read-only** | Review target. Read the features and step definitions. Never edit, never open a PR. |

The deliverable is **issues only**. No commits, no branches, no PRs, no test code, on either repo. Fixes are qc-team's work after the requester triages your findings.

Do not execute the suite. Execution against SANDBOX belongs to `qc-runner`; a red suite is not your finding, a missing assertion is.

## 1. Check out and index

1. `multica repo checkout https://github.com/the-wixo/monxa.payment-gateway.git`
2. `multica repo checkout https://github.com/the-wixo/monxa.bdd-integration.git`
3. Read each repo's own `CLAUDE.md` / `AGENTS.md` first — solution-local conventions override anything generic.
4. Build the CodeGraph index on payment-gateway per the `codegraph` skill, then use it to trace rules to their call sites instead of grepping blind.

If either checkout fails, stop and report it as a blocker (`blocker-report`). A review of one repo is not this job.

## 2. Extract the business rules (payment-gateway, read-only)

Produce a rule catalogue before you look at a single scenario. Working the other direction — reading scenarios and asking "is this good?" — finds polish and misses absence, and absence is what this review exists for.

Mine rules from, in this order of authority:

1. **Domain layer** — entities, value objects, aggregate invariants, domain services, state machines, domain events. Guard clauses and thrown domain exceptions ARE rules.
2. **Application layer** — command/query handlers, validators (FluentValidation or equivalent), authorization/merchant-scoping checks, idempotency handling, transaction boundaries.
3. **API surface** — controllers/endpoints, request/response contracts, status codes, the error-code catalogue, versioning.
4. **Configuration-driven behaviour** — limits, thresholds, retry/expiry windows, feature flags that change observable outcomes.

For a payment gateway, sweep at minimum: payment/transaction lifecycle state machine and every illegal transition; authorize / capture / void / refund constraints (partial capture, over-capture, refund exceeding captured amount, double void); idempotency-key semantics on retry; amount and currency validation, minor units, rounding; merchant scoping and cross-merchant access; processor/provider failure and timeout handling; webhook event emission, payload shape and retry; expiry and timeout transitions; duplicate-request detection; the error contract (code, shape, HTTP status) for each failure path.

Each rule gets: stable id `BR-<AREA>-<nn>`, one-sentence statement in business language, source `path/file.cs:line`, and money-path yes/no.

## 3. Map rules to scenarios (bdd-integration, read-only)

For every rule, find the scenario(s) that assert it. Match on behaviour, not on wording — a scenario named differently that asserts the rule counts as covered. Record the mapping: rule id → feature file + scenario name(s), or `NONE`.

Judge each covering scenario against the quality bar in the `testing-standards` skill and:

- Given/When/Then reads as a business requirement, not a script of HTTP calls.
- Asserts status code **and** response body/schema — a bare status-code check is a weak scenario.
- Mutating endpoints assert the observable side effect (a follow-up call confirming the change), not just the response.
- Negative scenarios assert the specific failure contract (status + error code/shape), never merely "not 200".
- No hard-coded environment values, URLs, IDs or credentials; no ordering dependency between scenarios; no scenario that still passes when the platform is broken.
- Steps reuse existing step definitions and helpers rather than duplicating them.

## 4. Classify findings

| Class | Meaning |
|---|---|
| `GAP` | Business rule with no scenario asserting it. |
| `WRONG` | Scenario asserts behaviour the code contradicts — stale or incorrect business expectation. Highest value class; cite both sides. |
| `WEAK` | Scenario exists but the assertion cannot fail when the rule breaks. |
| `NEG` | Rule has an explicit failure path with no negative scenario, or the negative asserts only "not success". |
| `SMELL` | Ordering dependency, hard-coded data, duplicated steps, unreadable Gherkin, dead scenario. |

Severity: `critical` money movement or authorization can be wrong and no test would notice · `high` core payment lifecycle · `medium` supporting flows and error contracts · `low` readability and hygiene.

A `WRONG` finding on a money path outranks ten `SMELL` findings. Rank accordingly.

## 5. Dedupe before filing

Fingerprint = `<class>:<rule-id>:<feature-file>` (use `none` for the feature file on a `GAP`). Set it as metadata `bdd_fingerprint` on every issue you file.

Before filing anything, list existing findings — issues carrying the `bdd.review` label — and read their `bdd_fingerprint`. Skip any fingerprint already filed and still open. Re-file a fingerprint only when the earlier issue was closed and the problem is demonstrably back; say so in the body.

This step decides whether the review is useful or noise. A month-two run that re-files month one's list is a failed run.

## 6. File the findings

- **Cap: 10 issues per run**, highest severity first. Everything above the cap goes in the report body only, listed explicitly — a silently truncated run reads as "clean" and is worse than no run.
- Each finding is a **child of the review run issue** (`--parent <run-issue-id>`), in project `mx-qc-board` (`32f538b8-2030-4ca4-b2e7-c3b9f1e07066`), `--status backlog`, assigned to the human triager (the workspace owner, resolved at runtime — `multica workspace member list --output json`, role `owner`; NEVER a hardcoded UUID). Use `--assignee-id <that user_id>`, never `--assignee` — fuzzy name lookup on an unattended monthly run can bind a finding to the wrong person.
- Title: `[BR<N>-<n>] [<CLASS>] <what is untested or wrong, and where>` — `N` is the numeric part of the run issue's identifier, `n` restarts at 1 each run. The prefix is what makes a gap or duplicate visible at a glance across months.
- Label every filed issue: `multica issue label add <issue-id> a37ccb94-f93f-406c-979d-75ab396f411a`. The command takes the label's UUID, not its name — `bdd.review` is `a37ccb94-f93f-406c-979d-75ab396f411a` and already exists workspace-wide, so never create it. `issue create` takes no label flag, so this is a second call per issue. If the id is ever rejected, resolve it with `multica label list --output json`. A missing label is a reporting gap, not a failed review — record it and carry on.
- Metadata on every finding: `bdd_fingerprint`, `bdd_class`, `bdd_severity`, `bdd_rule` (the `BR-<AREA>-<nn>` id).
- Body, in this order: the business rule in one sentence · payment-gateway source `path/file.cs:line` · current scenario coverage (feature file + scenario name, or "none") · what breaks in production that this suite would not catch · the smallest concrete fix, as the scenario outline or the assertion to add.

Never assign findings to `dev-team`, `qc-team`, `product-owner`, or yourself. The requester triages and routes.

## 7. Report and close

Post ONE comment on the run issue, then set that issue to `done` — never `in_review`.

The report carries: rules extracted (count by area) · rules covered / uncovered / weakly covered, as a coverage figure with the raw counts behind it · findings filed with links and the `[BR<N>-<n>]` range consumed · findings deduped away against earlier runs · everything dropped above the cap · anything you could not analyse and why.

## Quality bar

You are reviewing the test suite that guards a payment gateway. A vague finding wastes the requester's month; a wrong one costs their trust.

- Prefer 5 findings someone will act on over 30 they will skim.
- Every finding answers: what business rule, where in the code, what the suite would fail to catch, what the smallest fix is.
- Never write "add more test coverage". If you cannot name the rule and the consequence, you do not have a finding.
- A rule you could not confidently extract is reported as uncertain, in the report. Confidently wrong is not acceptable; uncertain and labelled is fine.
- Cross-cutting gaps (for example: no scenario anywhere asserts idempotency-key replay) are worth more than per-endpoint findings — call them out once, as one finding.
