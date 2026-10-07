# Scoring Rubric

## Category weights

| Category | Weight | What 10 looks like | What 3 looks like |
| --- | --- | --- | --- |
| Correctness & logic | 25% | No logic defects; concurrency and error paths sound; idempotent where required | A defect producing wrong results or data loss in a realistic path |
| Security | 20% | No findings; sensitive paths follow established patterns; no new attack surface | Any exploitable issue, secret in diff, or authz bypass |
| Testing & coverage | 20% | Changed behavior fully covered incl. edge cases; coverage on changed lines ≥ threshold; tests assert behavior | New logic with no tests, or tests that assert nothing |
| Architecture & design | 15% | Matches the spec's §3b placement; no new layering or boundary violation from the stack skill; no duplication; clear naming; small cohesive units | Contradicts §3b (wrong owner, reversed or cyclic dependency, undeclared public break), domain reaching into infrastructure, copy-paste duplication, god-methods |
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

## Proof before severity

Policy 04 statement 1a. Before a finding is kept as `blocking` or `important`, answer:

1. Can I cite the exact `file:line`?
2. **Correctness or security finding:** can I name the input or state that triggers it, the wrong outcome, and why existing guards (a caller's validation, the framework, the type system, an existing test) do not stop it? **Rule finding** (a cap, a stack rule-id, a §3b line, a test-strength rule, statement 5a): can I cite the rule?
3. Have I read the surrounding code, and walked the callers with CodeGraph?

A "no" demotes the finding to `nit` or drops it. A review with no finding above `nit` is a valid result: never raise a finding, or inflate a severity, to make the review look thorough.

**False positives — do not raise these:**

- "Add error handling" where a caller, middleware or the framework already handles the failure. Trace the caller first.
- "Missing validation" on input already validated at the trust boundary (model binding, a validator, a guard in the caller). Cite the boundary, or drop it.
- A null dereference after a null check, on a `required` member, or on a non-nullable reference the compiler already checks.
- HTTP status codes, well-known ports and framework-named timeouts called magic numbers.
- "Method too long" on a switch or mapping table, a test data table or generated code.
- N+1 on a loop over a small fixed set (enum members, configuration entries).
- Fire-and-forget that a comment says is intentional and that has its own catch-all (`ASYNC-007`).
- A style point the repo's analyzers or linter already enforce.
- A pattern the repo does not use elsewhere, offered as "better". Match the repo.
- Anything a senior engineer on this repo would not change in review.

These never lower a real defect: a finding that passes the proof check keeps its severity, pre-existing or not (Severity is impact, never novelty).

**Self-review rows** (Policy 04 statement 5): a Build EVIDENCE row that is missing or carries no measured value is a `nit` — measure the point yourself and score what you find. A row the diff or CI contradicts is `important`. No mutation evidence at all is the cap below, not a row finding.

## Hard caps (applied AFTER the weighted average)

`critical` is not a fifth severity — it is the subtype of `blocking` that is security-exploitable (exploitable issue, secret in diff, authz bypass). Label such findings `blocking (critical)`; they trigger the 3.0 cap below.

| Condition | Cap |
| --- | --- |
| Any `blocking` finding anywhere | 6.9 max (forces REWORK) |
| Any `blocking (critical)` security finding (exploitable, secret, authz bypass) | 3.0 max |
| ≥ 2 open `important` findings anywhere (any category, any mix) | 8.4 max (forces REWORK — per-category weights must not dilute repeated importants) |
| Spec-conformance category score ≤ 5, or no traceable spec/cycle-ticket link | 6.9 max (a wrong-thing PR never merges on "built right" points) |
| No tests for new/changed behavior | 6.5 max |
| A check loosened without the ticket asking for it: a repo-wide analyzer, lint, type-check, coverage or mutation setting lowered, or a CI step deleted, skipped or made non-failing (Policy 04 statement 5a) | 6.9 max (`blocking`) |
| Approved acceptance test modified or deleted after `at_sha` (drift check non-empty) without a leader re-pin | 6.9 max (`blocking`; forces REWORK — the fix is to restore the scenario and make it pass, or take it to the leader) |
| Any `@new` scenario red, skipped or tagged out at HEAD | 6.9 max (`blocking`) |
| `bug-build` cycle: `at_sha` holds implementation code or follows an implementation commit, or the reproduction is green at `at_sha` (Policy 02 statement 1b) | 6.9 max (`blocking`) |
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

**Coverage-excluded exception to the test caps** (Policy 02 statement 1e). Files the repo's coverage config on `dev` leaves out — `coverage.runsettings` `<Exclude>`/`<ExcludeByFile>` or no match in `<Include>`, jest `collectCoverageFrom`/`coveragePathIgnorePatterns`, coverage.py `omit`, `codecov.yml` `ignore` — or that the spec's §4 `Test scope` decision names when that config is silent, carry no coverage or mutation requirement. The `No mutation evidence` and `Coverage below threshold` caps do not fire on them, and they are left out of the changed-line coverage figure. The Testing & coverage category checks the exception's own duties instead: the Build's `Stack evidence` row quotes literal output for every `@stack` scenario, and the scenario's `@unit`/`@integration` ATs follow the AT contract. A `@stack` scenario with no literal output is `important`; new branching or decision logic in an excluded file is `important` (it belongs in a covered project); an excluded file the config on `dev` does not exclude and no `Test scope` decision names is judged as covered. The exclusion itself added or widened by this PR is the loosened-check `blocking`. The `CI failing` cap still applies.

**Helm chart exception to the test caps** (Policy 02 statement 1d). A devops chart PR (any `Chart.yaml`) has no coverage figure, mutation report, `at_sha` or acceptance tests: the `No mutation evidence` and `Coverage below threshold` caps do not fire, and their absence is not a finding. The Testing & coverage category checks the chart's own duties instead: a `helm-unittest` assertion for every new or changed conditional render (`HELM-DEL-001`) where the repo has a `helm-unittest` suite, else the `helm template` output before and after in the PR body; `helm lint`, `helm template` and the repo's verify scripts, where it has them, clean; and every consumer chart rendering unchanged unless it opts in. A new or changed conditional render with no assertion (or, in a repo without a suite, no before-and-after render) is the `No tests` cap; a red lint, template or verify run, or a consumer chart whose render changed without opting in, is `important`. The `CI failing` cap still applies.

## Binary gate mapping (this workspace)

There is no human-review middle band and no deferred verdict: **≥ 8.5 → APPROVED and merged** (a `design/<key>` PR: APPROVED and handed to the owner, merged on their reply A — Policy 04 statement 9a); **< 8.5 → REWORK** (then ESCALATED after 3 rounds). The caps guarantee that anything ≥ 8.5 already has: no blocking findings, at most one open `important` finding, spec conformance intact, tests present, CI green or a stated CI exception, coverage not measured below threshold. Two or more `important` findings loop back to dev-team via the 8.4 cap — the weighted average alone would not catch them (one `important` in a 25% category only costs 0.5), which is exactly why the cap exists.

## Calibration anchors

Worked from the weights above: one `important` costs 2 × weight (0.1–0.5 points), one `blocking` costs 4 × weight (0.2–1.0 points) before its cap.

- **9.5–10** — Small, focused, spec-linked change; tests included; zero findings above `nit`. Its open `nit`s merge with it, named under `Merged with:` (there is no polish round, Policy 04 statement 13).
- **8.5–9.9** — Correct, safe, covered; exactly one `important` finding. Alone it scores 9.5–9.9; `nit`s can pull it lower, and below 8.5 it is REWORK.
- **8.4** — Two or more `important` findings and no `blocking`: the cap sets the score. The arithmetic alone would give 9.0–9.8.
- **6.9 / 6.5** — Any `blocking` finding, or CI failing because of this PR: 6.9. New logic with no tests: 6.5. The cap sets the score; one `blocking` alone would compute to 9.0–9.8.
- **≤ 6.0** — Several categories collapsed, e.g. Correctness 2 (−2.0), Security 2 (−1.6), Testing 8 (−0.4) → 6.0.
- **3.0** — A `blocking (critical)` security finding (the 3.0 cap), or a fundamentally wrong approach that leaves most categories near their floor.

Report the final score to one decimal. Never inflate a score to reach a gate; when torn between two scores, pick the lower one and say why.
