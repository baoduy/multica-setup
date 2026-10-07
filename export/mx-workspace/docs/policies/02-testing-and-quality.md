# Policy 02 — Testing &amp; Quality


|                    |                                                                                                                                                                                                        |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Policy ID**      | MX-POL-02                                                                                                                                                                                              |
| **Version**        | 1.8                                                                                                                                                                                                    |
| **Status**         | Active                                                                                                                                                                                                 |
| **Owner**          | dev-leader (in-repo tests) · qc-leader (SANDBOX integration)                                                                                                                                           |
| **Applies to**     | Every code or behaviour change in Monxa repos                                                                                                                                                          |
| **Related skills** | [`testing-standards`](../../skills/testing-standards/SKILL.md) · [`test-driven-development`](../../skills/test-driven-development/SKILL.md) · [`playwright-bdd`](../../skills/playwright-bdd/SKILL.md) |
| **Enforced at**    | PR review gate ([`pr-review-gate`](../../skills/pr-review-gate/SKILL.md)) — testing dimension                                                                                                          |


> **Authority.** This policy is the source of truth for testing &amp; quality. `testing-standards`,
> `test-driven-development` and `playwright-bdd` **implement** it; the PR gate's testing
> dimension derives its bar from it. Amend this policy first, then cascade — see
> [change control](00-policies-index.md#change-control).

## Testing at a glance

```
   Every change:   [Acceptance tests run] spec §7 ──▶ executable ATs, RED, pushed
                   [leader, inline]       read ATs vs spec ──▶ pin at_sha (frozen)
                   [Build run]            implement ──▶ ATs GREEN · suite green · ≥80% · mutation report · drift check empty
   Bug fix (Prove-It, confirmed, Mode: bug-build):  reproduction pushed as at_sha, RED ──▶ fix same run ──▶ green ──▶ full suite

   Test pyramid              Coverage gate (BOTH required, scoped to the change)
        ╱╲  E2E ~5%          ┌─────────────────────────────────────────────┐
       ╱──╲ Integ ~15%       │ 1. full suite green — 0 errors, 0 warnings  │
      ╱────╲ Unit ~80%       │ 2. ≥80% combined BDD+unit on TOUCHED classes│
     ╱──────╲                └─────────────────────────────────────────────┘

   Two "BDD"s — never conflate:
     in-repo BDD/unit  (dev-team, [P#-1])   ── NEVER waivable, part of Build's Definition of Done
     SANDBOX integration (qc-team, [P#-3])  ── requester-only waiver → bdd_required=false
```

## Purpose

Tests are proof, not decoration — "seems right" is not done. A codebase with good
tests is an agent's superpower; without them it is a liability. This policy sets the
quality bar and the coverage gate so every change ships with the evidence that it works
and stays working.

## Scope

All behaviour changes. Two distinct things are called "BDD" and must never be conflated:


|                                     | Owner &amp; stage         | Where                                                                                           | Waivable                                                       |
| ----------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **BDD unit tests** (in-repo)        | dev-team, inside `[P#-1]` | the repo's own BDD/unit project (Reqnroll/SpecFlow for .NET, Cucumber/playwright-bdd for React) | **Never** — part of the change's Definition of Done            |
| **BDD integration tests** (SANDBOX) | qc-team, in `[P#-3]`      | `monxa.bdd-integration`, run against a deployed SANDBOX                                         | Yes — **requester-only** waiver, recorded `bdd_required=false` |


"No BDD required" **always** means the SANDBOX integration suite only. It never relieves
dev-team of in-repo coverage of the change.

## Policy statements

1. **Acceptance-test-first, authored and implemented in separate runs, verified by outcome.** Every change is proven by acceptance tests derived from the spec's Gherkin before its PR opens. Inside a dev-team cycle dev-backend owns both halves but never in one run: the **`Acceptance tests:` stage** turns the brief's §7 into executable, RED scenarios (plus the §5 signature stubs so they compile) and pushes them; dev-leader reads them against the spec and pins `at_sha`; the **`Build:` stage** implements against those frozen scenarios until green. A modified or deleted approved scenario after `at_sha` is a `blocking` review finding — a wrong scenario goes back to the leader, never gets edited to pass. How dev-backend reaches green inside Build (unit red/green/refactor) is its own business and is not reported; what IS reported and re-measured is the outcome: frozen ATs green, full suite green, ≥80% coverage and a mutation report per touched class, empty drift check. Why: a single run that writes a test and then attests "it failed first" proves only that it ran; the independent read before implementation and the lock afterwards are what make red-then-green evidence. For a defect the acceptance test is the Prove-It reproduction (see [Policy 07](07-bug-and-defect-management.md)). There is no separate in-repo QC role: **missing or thin tests and coverage gaps are dev-backend's own work**, closed inside Build, and the PR gate is the independent second pass. The writer/gate split still holds in qc-team for the SANDBOX suite: qc-tester writes scenarios, qc-runner gates and executes them ([Policy 09](09-agent-roles-and-responsibilities.md)).
1a. **A confirmed bug fix proves itself in one run.** A phase ticket whose root is a Workflow A bug carrying product-owner's root-cause report ([Policy 07](07-bug-and-defect-management.md) statement 1), whose acceptance test is only the Prove-It reproduction on one surface, and whose brief adds no public signature, gets ONE `Build:` sub-task with `Mode: bug-build` instead of the Acceptance-tests + Build pair. dev-backend commits and pushes the reproduction alone first (that commit is `at_sha`, red for the reason the root-cause report names), then fixes in the same run. dev-leader approves nothing in between; pr-reviewer checks that `at_sha` holds only the reproduction test and stubs, predates every fix commit, is red, and matches the root-cause report's reproduction conditions. A mismatch is `blocking` (`references/scoring-rubric.md`, [Policy 04](04-code-and-spec-review.md) statement 4). A second surface, a new public signature, or any doubt about the confidence gate keeps the normal pair.

1b. **Independent surfaces build in parallel against one frozen test set.** When a phase ticket's surfaces have disjoint file sets (inside this cycle's one repo), the Acceptance-tests stage writes every surface's scenarios — and any §5 stub shared between them, as one sub-task — at the SAME stage; Builds run at the next stage, **at most 3 at once**. A Build is `done` only when its own `@new` scenarios, every `@existing` scenario, every pre-existing test, and every already-`done` sibling Build's `@new` scenarios are green — a still-running sibling's may stay red. A push rejected by a sibling's push is rebased onto the updated branch and the suite re-run, so the last Build to finish is the one that proves the whole surface set green. Surfaces run in sequence only for a real file overlap or behaviour dependency, never because a brief grew large (`sdlc-impl-brief`). REWORK findings still consolidate into ONE `Fix (review):` sub-task per round regardless of how many Builds ran ([Policy 04](04-code-and-spec-review.md) statement 6) — grouping findings per Build sub-task was considered and dropped as a conflict with that statement.

2. **BDD-first.** Cover behaviour with Gherkin scenarios in business language, one behaviour per scenario; fall back to unit tests only where BDD is impractical. Ship feature files with their step definitions in the same change. Never add a BDD harness to a repo that lacks one as a side quest — cover the behaviour in the existing unit suite and say so.
3. **Coverage gate — scoped to the change, both conditions required:**
  - All existing tests pass — full suite green, **zero errors, zero warnings**.
  - **Combined BDD + unit coverage of the touched classes ≥ 80%**, measured over files this change added/modified, never repo-wide. A repo-wide figure is FYI only.
3a. **Mutation runs are scoped to the lines the cycle changed, not the whole class.** The mutation run (statement 3's coverage "honesty check") targets the diff's hunks in each touched class — `git fetch origin dev` first (a task-scoped checkout may lack the ref), then `dotnet stryker --since:origin/dev` — never a whole-class run, which re-tests code the cycle does not own. Still reported per touched class, every surviving mutant dispositioned. Tool genuinely unavailable → the manual equivalent: invert each guard the change added, run, confirm RED, restore, and say so. The speed-up is not yet measured here: compare mutant count and wall time on the next Build; if `--since` does not narrow the run, add `-m` touched-class globs.
4. **Never inflate coverage** with trivial tests (getters, framework code). If code is untestable as written, propose the smallest design change — never silently rewrite production logic to suit a test. If 80% on a touched class is genuinely unreachable, flag the untestable paths to the leader.
5. **Test behaviour and contracts, not implementation.** Tests must survive behaviour-preserving refactors: no asserting on private members, internal call order, or brittle DOM/CSS selectors. Assert on state/outcome, not on which methods were called.
6. **FIRST** — Fast, Isolated, Repeatable, Deterministic. No real time, network, live DB, random seeds, or order dependence; mock external dependencies only.
7. **Structure &amp; naming.** Given/When/Then (BDD) or Arrange-Act-Assert (unit); one behaviour per test; the name states scenario + expected outcome (`Should_ReturnNotFound_When_OrderDoesNotExist`). **DAMP over DRY** in tests — each test reads as a self-contained spec. DAMP governs assertions and arrange-readability inside a test body — it is never licence to repaste a setup block (statement 7a).
7a. **Test code reuses its harness; a second copy of a setup block is already too many.** A new test extends the AT harness or the repo's shared fixture (a builder, a factory taking the fakes, a parameterised case) instead of copying its setup. A copied setup or arrange block of ~10 lines or more is a DRY defect at the second copy — tighter than Policy 01 statement 13's 3-occurrence threshold, because test setup drifts faster and the architecture-review sweep already flags copy-paste duplication as an Architecture finding (`references/scoring-rubric.md`). DAMP still holds inside the test body: the rule targets copied setup, not readable assertions.
8. **Test doubles, cheapest that works.** Real implementation &gt; fake &gt; stub &gt; mock. Mock only at boundaries that are slow, non-deterministic, or have uncontrollable side effects. Over-mocking makes tests pass while production breaks.
9. **Test pyramid.** ~80% small/unit, ~15% integration, ~5% E2E. The Beyonce Rule: if you liked it, you should have put a test on it.
10. **Nothing is reported skipped, and CI runs locally first.** A dev-team `Build:` or `Fix (review):` sub-task never reports `done` with a check it was asked to run marked skipped or deferred — a check that cannot run is `blocked` with the reason, or the manual fallback its own statement names (e.g. statement 3a's manual mutation check). Before its last push the implementer makes a throwaway local merge of fresh `origin/dev` into its HEAD (a scratch branch it never pushes; the shared feature branch is never rebased) and, from the repo root, runs the repo's `pull_request` workflow steps that run locally (`.github/workflows/*.yml`: restore, build, test, and — where the workflow builds a container on `pull_request` — `docker build` with no push; a step needing a Docker daemon the runtime doesn't have is `not local`, same as one needing a secret). A step needing a secret, upload, publish or deploy is listed `not local: <step>` — a declared boundary, not a skip. Reported in a `CI parity` row (member-protocol check 9). A red also present on `origin/dev` is noted with that proof; any other red is the implementer's to fix. A conflict is reported, not resolved — conflicts with `dev` are dev-leader's (`leader-gitops`). dev-leader sends back a Build or Fix whose report marks any check skipped. `qc-team`'s SANDBOX suite is unaffected: this statement binds dev-team's in-repo Build/Fix only.

## Best practices for .NET developers

- **Runner &amp; libs:** xUnit (or the project runner), FluentAssertions, Moq/NSubstitute **on abstractions**, `[Theory]` for parameterized cases, `WebApplicationFactory<T>` / Testcontainers for integration. Never `TEST_DB_PROVIDER=SqlServer` — leave it unset so tests run InMemory.
- **Cover:** happy path, boundaries, null/invalid input, and exception paths.
- **Gherkin (Reqnroll/SpecFlow):** business language, not UI mechanics; `Scenario Outline` + `Examples` for data-driven cases; reuse step definitions; tag meaningfully.
- **React/Next (where relevant):** Vitest/Jest + React Testing Library, query by role/label/text (test-id last resort), `user-event` over `fireEvent`, MSW for network; no snapshot tests as behavioural substitutes.
- **Report** the suite result and per-touched-class coverage (file + %) in the completion comment's EVIDENCE table (see [`blocker-report`](../../skills/blocker-report/SKILL.md)).

## Roles &amp; responsibilities

- **dev-backend** — the **sole author of the cycle's in-repo tests and code** (BDD unit +
  traditional unit): writes the tests first from the spec's acceptance criteria, implements
  against them, runs the coverage review, measures and reports per-touched-class coverage,
  and is the only role whose sign-off (a `done` flip on its Build with a green suite)
  satisfies the coverage gate. Never flips `done` on a red suite or a coverage gap, and
  never edits a test to force it green — a red test against correct spec behaviour is an
  implementation defect.
- **qc-tester / qc-runner** — the SANDBOX integration pair: qc-tester authors scenarios,
  qc-runner reviews and executes them and classifies failures. qc-runner never writes
  test code; qc-tester never gates its own work.
- **dev-leader / qc-leader** — gate their cycles: no PR authorization or finalize while a
  Build sub-task is `blocked`, its report lacks per-touched-class coverage evidence, the
  latest verification verdict is red, or any fix sub-task is open. Never run tests
  themselves — read the evidence and trust the PR gate's independent re-check.
- **pr-reviewer** — re-checks tests and coverage at the PR gate as an independent pass —
  the only pair of eyes on the tests that did not write the code, so a coverage miss or an
  implementation-shaped test here is REWORK
  over the same diff.

## Definition of Done / compliance

- New/changed logic has tests; edge cases covered; every bug fix carries a reproduction test that failed before the fix.
- Full suite green, zero warnings.
- ≥ 80% combined coverage on touched classes, reported per file.
- No skipped/disabled tests introduced to make the suite pass.
- Every `pull_request` workflow step green locally on a throwaway merge of `origin/dev` into HEAD, and no check reported skipped (statement 10).

## Enforcement

`pr-review-gate` Phase 2 testing dimension: verifies tests exist for changed logic,
assert behaviour not implementation, cover edge cases, and that changed-line coverage
≥ 80% (override via `.pr-review.json`). A coverage miss or missing tests on touched
logic is a `blocking`/`important` finding → REWORK.

## Exceptions &amp; waivers

- The **SANDBOX integration suite** (`[P#-3]`) is waivable by the **requester only**, recorded as `bdd_required=false`. A waiver drops `[P#-2b]` deploy and `[P#-3]` and makes `[P#-2a]` terminal — it never touches the in-repo test obligation, the acceptance criteria, or the merge gate.
- The in-repo coverage gate has **no** waiver.
- Coverage override per repo lives in `.pr-review.json` as merged on `dev`, not per PR: the
  gate reads the file from `dev` on GitHub, and a PR that lowers the threshold is a `blocking`
  finding unless its ticket asks for it ([Policy 04](04-code-and-spec-review.md) statement 4a).

## References

- [`test-driven-development`](../../skills/test-driven-development/SKILL.md) — RED/GREEN/REFACTOR, Prove-It, pyramid, anti-patterns.
- [`testing-standards`](../../skills/testing-standards/SKILL.md) — the "what good looks like" bar for this codebase.
- [`playwright-bdd`](../../skills/playwright-bdd/SKILL.md) — browser BDD tooling.

