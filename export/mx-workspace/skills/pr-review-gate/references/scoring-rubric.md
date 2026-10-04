# Scoring Rubric

## Category weights

| Category | Weight | What 10 looks like | What 3 looks like |
| --- | --- | --- | --- |
| Correctness & logic | 25% | No logic defects; concurrency and error paths sound; idempotent where required | A defect producing wrong results or data loss in a realistic path |
| Security | 20% | No findings; sensitive paths follow established patterns; no new attack surface | Any exploitable issue, secret in diff, or authz bypass |
| Testing & coverage | 20% | Changed behavior fully covered incl. edge cases; coverage on changed lines ≥ threshold; tests assert behavior | New logic with no tests, or tests that assert nothing |
| Architecture & design | 15% | Matches the spec's §3b placement; no new layering or boundary violation from `dknet-ddd-conventions`; no duplication; clear naming; small cohesive units | Contradicts §3b (wrong owner, reversed or cyclic dependency, undeclared contract break), domain reaching into infrastructure, copy-paste duplication, god-methods |
| Spec conformance | 10% | Diff does exactly what the cycle ticket spec / Gherkin scenarios describe; no scope creep | Solves a different problem, or large unrelated changes bundled in |
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

Severity comes from what a finding DOES, not from whether this PR introduced it. Emitted source that does not compile, wrong behaviour, data exposure or a published-API break is `blocking` — `important` only when provably unreachable today — even when it is pre-existing and even when the diff merely walks past it. "Not introduced by this PR" decides WHOSE cycle fixes it (the scope rule in `references/multica-flow.md`), never whether it is a defect.

## Proof before severity

Policy 04 statement 1a. Before a finding is kept as `blocking` or `important`, answer:

1. Can I cite the exact `file:line`?
2. **Correctness or security finding:** can I name the input or state that triggers it, the wrong outcome, and why existing guards (a caller's validation, the framework, the type system, an existing test) do not stop it? **Rule finding** (a cap, a stack rule-id, a §3b line, a test-strength rule, statement 4a): can I cite the rule?
3. Have I read the surrounding code, and walked the callers with CodeGraph?

A "no" demotes the finding to `nit` or drops it. A review with no finding above `nit` is a valid result: never raise a finding, or inflate a severity, to make the review look thorough.

**False positives — do not raise these:**

- "Add error handling" where a caller, middleware or the framework already handles the failure. Trace the caller first.
- "Missing validation" on input already validated at the trust boundary (model binding, a validator, a guard in the caller). Cite the boundary, or drop it.
- A null dereference after a null check, on a `required` member, or on a non-nullable reference the compiler already checks.
- HTTP status codes, well-known ports and framework-named timeouts called magic numbers.
- "Method too long" on a switch or mapping table, a test data table or generated code.
- N+1 on a loop over a small fixed set (enum members, configuration entries).
- Fire-and-forget that a comment says is intentional and that has its own catch-all.
- A style point the repo's analyzers already enforce.
- A pattern the repo does not use elsewhere, offered as "better". Match the repo.
- Anything a senior engineer on this repo would not change in review.

These never lower a real defect: a finding that passes the proof check keeps its severity, pre-existing or not (Severity is impact, never novelty).

**Self-review rows** (Policy 04 statement 4): a Build EVIDENCE row that is missing or carries no measured value is a `nit` — measure the point yourself and score what you find. A row the diff or CI contradicts is `important`. No mutation evidence at all is the cap below, not a row finding; the coverage number and, on `monxa.bdd-integration`, the per-scenario pass/fail table are unaffected — an unknown coverage figure is the auto-merge precondition failing (APPROVAL DEFERRED), never a nit.

## Hard caps (applied AFTER the weighted average)

| Condition | Cap |
| --- | --- |
| Any `blocking` finding anywhere | 6.9 max (forces REWORK) |
| Any `critical` security finding (exploitable, secret, authz bypass) | 3.0 max |
| Two or more open `important` findings anywhere, no `blocking` | 8.4 max |
| No tests for new/changed behavior | 6.5 max |
| A check loosened without the ticket asking for it: a repo-wide analyzer, lint, coverage or mutation setting lowered, or a CI step deleted, skipped or made non-failing (Policy 04 statement 4a) | 6.9 max (`blocking`) |
| Approved acceptance test modified or deleted after `at_sha` (drift check non-empty) without a leader re-pin | 6.9 max (`blocking`; forces REWORK — the fix is to restore the scenario and make it pass, or take it to the leader) |
| Any `@new` scenario red, skipped or tagged out at HEAD | 6.9 max (`blocking`) |
| No mutation evidence on touched classes with new logic (neither tool report nor manual run stated) | 7.9 max |
| CI failing | 6.9 max (coverage-ratchet exception below) |
| Coverage on changed lines measured BELOW threshold (default 80%) | 7.9 max (forces REWORK: dev-backend's bar is measurable and fixable) |
| Docs-only / comment-only / typo-fix PR with green CI | floor of 9.0 (fast-path; preconditions still apply; caps beat the floor) |

Coverage UNKNOWN (no artifact, tests not cheaply runnable) is NOT a cap — it fails the auto-approve precondition instead, so a ≥ 8.5 PR lands on APPROVAL DEFERRED and a human decides.

**Coverage-ratchet exception to the CI cap.** The `CI failing` cap does NOT fire when EVERY red check is a coverage-ratchet check (`codecov/patch`, `codecov/project` or equivalent), the diff's own coverage bar is met, and nothing else is red. Score the merit; merit ≥ bar ⇒ **APPROVAL DEFERRED** (a human decides), never REWORK, and **never increment `review_round`**. A rework round must never be spent on a number no rework can reach: a small diff's patch percentage is fixed by the repo's ratchet config, a branch unreachable by construction cannot be covered, and a brief that instructs removing `[ExcludeFromCodeCoverage]` lowers project coverage by arithmetic. State the check, its target and the arithmetic in the report. If the ratchet config itself is the defect, that is an out-of-scope finding against the repo, not a finding against the PR — and a brief instruction that breaks CI by arithmetic is a brief defect, reported to the leader, not a deduction from the implementer. (DRK-1204: merit 9.9 scored 6.9, both rework rounds burnt, human merge — for one line C# cannot admit.)

## Binary gate mapping (this workspace)

There is no human-review middle band: **≥ 8.5 → APPROVED** (or APPROVAL DEFERRED when a precondition fails); **< 8.5 → REWORK**. The caps guarantee that anything ≥ 8.0 already has: no blocking findings, tests present, CI green, coverage ≥ threshold. The 8.5 bar means a PR carrying several unaddressed `important` findings loops back to dev-team instead of reaching the human.

## Calibration anchors

Worked from the weights above: one `important` costs 2 × weight (0.1–0.5 points), one `blocking` costs 4 × weight (0.2–1.0 points) before its cap. Nits alone, maxed at −1.5 in every one of the seven categories at once, bottom out at exactly 8.5 — still a pass.

- **9.5–10** — Small, focused, spec-linked change; tests included; zero findings above `nit`. Its open `nit`s merge with it, named under `Merged with:` (there is no polish round, Policy 04 statement 7).
- **8.5–9.9** — Correct, safe, covered; exactly one `important` finding. Alone it scores 9.5 (Correctness) to 9.9 (Style or AI-slop); `nit`s elsewhere can pull it down, and below 8.5 it is REWORK. At or above 8.5 it merges, named under `Merged with:`.
- **8.4** — Two or more `important` findings and no `blocking`: the cap sets the score. The arithmetic alone would give 9.0 (both in Correctness) to 9.8 (one each in the two 5% categories) — above the approve bar, which is why the cap exists: without it a PR carrying two or three importants would merge on score alone.
- **7.9** — Coverage on changed lines below threshold, or no mutation evidence on touched classes with new logic: the cap sets the score.
- **6.9 / 6.5** — Any `blocking` finding, CI failing, or approved-AT drift: 6.9. No tests for new or changed behaviour: 6.5. The cap sets the score; one `blocking` alone would compute to 9.0–9.8.
- **≤ 6.0** — Several categories collapsed, e.g. Correctness 2 (−2.0), Security 2 (−1.6), Testing 8 (−0.4) → 6.0.
- **3.0** — A `critical` security finding (the 3.0 cap), or a fundamentally wrong approach that leaves most categories near their floor.

Report the final score to one decimal. Never inflate a score to reach a gate; when torn between two scores, pick the lower one and say why.
