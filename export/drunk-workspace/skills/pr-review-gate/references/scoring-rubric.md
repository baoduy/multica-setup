# Scoring Rubric

## Category weights

| Category | Weight | What 10 looks like | What 3 looks like |
| --- | --- | --- | --- |
| Correctness & logic | 25% | No logic defects; concurrency and error paths sound; idempotent where required | A defect producing wrong results or data loss in a realistic path |
| Security | 20% | No findings; sensitive paths follow established patterns; no new attack surface | Any exploitable issue, secret in diff, or authz bypass |
| Testing & coverage | 20% | Changed behavior fully covered incl. edge cases; coverage on changed lines ≥ threshold; tests assert behavior | New logic with no tests, or tests that assert nothing |
| Maintainability & design | 15% | Fits existing architecture; no duplication; clear naming; small cohesive units | Copy-paste duplication, god-methods, leaky abstractions |
| Spec conformance | 10% | Diff does exactly what the cycle ticket spec / acceptance criteria describe; no scope creep | Solves a different problem, or large unrelated changes bundled in |
| Style & conventions | 5% | Matches repo `.editorconfig`/conventions; analyzers clean | Fights the codebase's established style throughout |
| AI-slop gate | 5% | No LLM anti-patterns | Pervasive redundant comments, defensive wrapping, dead code, reinvented BCL helpers |

Weighted average = Σ(category score × weight).

## Scoring a category

Start each category at 10 and deduct:

- `blocking` finding: −4 (and triggers a hard cap below)
- `important` finding: −2
- `nit`: −0.5 (max −1.5 total from nits)
- `suggestion` / `praise`: 0

Floor each category at 1.

## Severity is impact, never novelty

Severity comes from what a finding DOES, not from whether this PR introduced it. Emitted source that does not compile, wrong behaviour, data exposure or a published-API break is `blocking` — `important` only when it is provably unreachable today — even when it is pre-existing and even when the diff merely walks past it. "Not introduced by this PR" decides WHOSE cycle fixes it (the scope rule in `references/multica-flow.md`), never whether it is a defect. A 9.5 that ships with a known non-compiling emission path in a file the diff touched is a mis-scored review, not a clean one.

## Hard caps (applied AFTER the weighted average)

`critical` is not a fifth severity — it is the subtype of `blocking` that is security-exploitable (exploitable issue, secret in diff, authz bypass). Label such findings `blocking (critical)`; they trigger the 3.0 cap below.

| Condition | Cap |
| --- | --- |
| Any `blocking` finding anywhere | 6.9 max (forces REWORK) |
| Any `blocking (critical)` security finding (exploitable, secret, authz bypass) | 3.0 max |
| ≥ 2 open `important` findings anywhere (any category, any mix) | 8.4 max (forces REWORK — per-category weights must not dilute repeated importants) |
| Spec-conformance category score ≤ 5, or no traceable spec/cycle-ticket link | 6.9 max (a wrong-thing PR never merges on "built right" points) |
| No tests for new/changed behavior | 6.5 max |
| Approved acceptance test modified or deleted after `at_sha` (drift check non-empty) without a leader re-pin | 6.9 max (`blocking`; forces REWORK — the fix is to restore the scenario and make it pass, or take it to the leader) |
| Any `@new` scenario red, skipped or tagged out at HEAD | 6.9 max (`blocking`) |
| No mutation evidence on touched classes with new logic (neither tool report nor manual run stated) | 7.9 max |
| CI failing, caused by this PR | 6.9 max (three exceptions below) |
| Coverage on changed lines measured BELOW threshold (default 80%) | 7.9 max (forces REWORK: dev-backend's bar is measurable and fixable) |
| Docs-only / comment-only / typo-fix PR with green CI | floor of 9.0 (fast-path) |

**Caps beat the floor.** The docs-only 9.0 floor applies only when no cap fired: a docs-only PR carrying a `blocking` finding is 6.9 max like any other.

Coverage UNKNOWN (no artifact, no per-class numbers on the Build sub-task, tests not cheaply runnable) is NOT a cap and does not block the merge — state `Coverage: unknown (<why>)` in the report.

**Workflow-fix exception to the CI cap.** The `CI failing` cap does not fire when the PR changes the workflow file(s) that produce the red check (a Workflow D CI/CD PR whose purpose is to change what CI does). The red result is the behaviour under change; score the merit, state `CI: red by design (<check>)`, and merge on score plus devops' `gh run` evidence on the branch.

**Coverage-ratchet exception to the CI cap.** The `CI failing` cap does NOT fire when EVERY red check is a coverage-ratchet check (`codecov/patch`, `codecov/project` or equivalent), the diff's own coverage bar is met, and nothing else is red. Score the merit; merit ≥ bar ⇒ **APPROVED and merged**, never REWORK, and **never increment `Gate round`**. A rework round must never be spent on a number no rework can reach: a small diff's patch percentage is fixed by the repo's ratchet config, a branch unreachable by construction cannot be covered, and a brief that instructs removing `[ExcludeFromCodeCoverage]` lowers project coverage by arithmetic. State the check, its target and the arithmetic in the report. If the ratchet config itself is the defect, that is an out-of-scope finding against the repo, not a finding against the PR — and a brief instruction that breaks CI by arithmetic is a brief defect, reported to the leader, not a deduction from the implementer. (DRK-1204: merit 9.9 scored 6.9, both rework rounds burnt, human merge — for one line C# cannot admit.)

**Not-caused-by-this-PR exception to the CI cap.** The `CI failing` cap does NOT fire when, after ONE re-run of the failed jobs, the gate can show the red was not caused by this PR: the same check is red on `dev`'s head, the failure sits in a project or test the diff does not touch and does not reach (CodeGraph), or it is an infrastructure error (runner, checkout, network, a cancelled run, a restore advisory on a package the diff does not change). Score the merit, state `CI: red, not caused by this PR (<check>, <evidence>)`, merge on score. No evidence means caused: the cap stays. Measured over 47 deferred PRs (2026-08 to 2026-09), about 8 were red for reasons the PR did not cause — flaky tests, infrastructure, an unrelated advisory.

**UI presentation exception to the test caps** (Policy 02 statement 1a). Files that only render a front-end app — screens and layouts, components, styling, copy; never route handlers, data access, auth, session, contract code, middleware or build config — carry no test requirement. The `No tests`, `No mutation evidence` and `Coverage below threshold` caps do not fire on them, and they are left out of the Testing & coverage category, which checks the exception's own duties for them instead: every existing test the change broke is skipped with the runner's skip and a one-line note naming the ticket (never deleted, never rewritten to pass), and the Review description links dev-leader's follow-up issue naming the cycle's §5 scenarios and every skipped test. Each skipped test without its note, a deleted or rewritten test, and a missing follow-up issue is an `important` finding. A UI-presentation-only PR scores the category on those duties alone. The `CI failing` cap still applies — a skipped test is not a red one.

## Binary gate mapping (this workspace)

There is no human-review middle band and no deferred verdict: **≥ 8.5 → APPROVED and merged**; **< 8.5 → REWORK** (then ESCALATED after 3 rounds). The caps guarantee that anything ≥ 8.5 already has: no blocking findings, at most one open `important` finding, spec conformance intact, tests present, CI green or a stated CI exception, coverage not measured below threshold. Two or more `important` findings loop back to dev-team via the 8.4 cap — the weighted average alone would not catch them (one `important` in a 25% category only costs 0.5), which is exactly why the cap exists.

## Calibration anchors

- **9.5** — Small, focused, spec-linked change; tests included; zero findings above `nit`, and every in-scope `nit` already cleared by a polish round before merge (an open in-scope `nit` at merge time is not a 9.5, it is an unfinished cycle).
- **8.5–9.4** — Correct, safe, covered; exactly one `important` finding (two would trigger the 8.4 cap).
- **8.0** — Correct and safe, but 1–2 `important` maintainability/testing gaps → below the bar, REWORK with a short fix list.
- **6.0** — At least one `blocking` issue OR untested new logic; needs rework before merge.
- **3.0** — Security-relevant defect or fundamentally wrong approach.

Report the final score to one decimal. Never inflate a score to reach a gate; when torn between two scores, pick the lower one and say why.
