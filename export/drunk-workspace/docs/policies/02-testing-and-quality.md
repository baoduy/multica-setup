# Policy 02 — Testing & Quality

| | |
|---|---|
| **Policy ID** | DRK-POL-02 |
| **Version** | 1.2 |
| **Status** | Active |
| **Owner** | dev-backend |
| **Applies to** | Every code or behaviour change in a drunk repo, across every stack |
| **Related skills** | [`test-driven-development`](../../skills/test-driven-development/SKILL.md) · testing rules embedded in [`nodejs-typescript-standards`](../../skills/nodejs-typescript-standards/SKILL.md) (`TS-TEST-*`) · [`python-mcp-standards`](../../skills/python-mcp-standards/SKILL.md) (`MCP-TEST-*`) · [`pulumi-azure-iac-standards`](../../skills/pulumi-azure-iac-standards/SKILL.md) (`PULUMI-TEST-*`) |
| **Enforced at** | PR review gate ([`pr-review-gate`](../../skills/pr-review-gate/SKILL.md)) |

> **Authority.** This policy is the source of truth for testing and quality across every
> drunk stack. `test-driven-development` and the per-stack `*-TEST-*` rules **implement** it;
> `pr-review-gate`'s testing dimension derives its bar from it. Amend this policy first, then
> cascade — see [change control](../00-policies-index.md#change-control).

## Testing at a glance

```
   Every change:   [Acceptance tests run] spec §7 ──▶ executable ATs, RED, pushed
                   [leader, inline]       read ATs vs spec ──▶ pin at_sha (frozen)
                   [Build run]            implement ──▶ ATs GREEN · suite green · ≥80% · mutation report · drift check empty
   Bug fix (Prove-It):  reproduction AT authored RED and frozen ──▶ fix in Build ──▶ green ──▶ full suite

   No deployed environment to test against — these are published packages.
   Coverage is measured on the feature branch, per TOUCHED class/module, never repo-wide:

        git diff --name-only origin/dev...origin/<feature-branch>   (production files only)

   Sign-off = FULL suite green (pre-existing + new) + ≥80% on every touched class + clean
   `dotnet pack` / `npm pack`, expressed ONLY by dev-backend flipping its Build sub-task to `done`.
```

## Purpose

drunk ships open-source packages with nothing to deploy — the test suite is the only proof
a change works before it reaches `main` and is published. This policy sets the bar (test-first,
behaviour not implementation, per-stack runner) and the coverage gate that decides whether a
cycle's verification can go green, so a red suite never silently reaches a release.

## Scope

Every behaviour change across the five drunk stacks (.NET, TypeScript/Pulumi, Python, Helm,
Docker). Test code is exempt from [Policy 01](01-coding-standards.md)'s production-code
statements but follows the runner and structure conventions below.

## Policy statements

1. **Acceptance-test-first, authored and implemented in separate runs, verified by outcome.**
   Every change is proven by acceptance tests derived from the spec's Gherkin before its PR
   opens. dev-backend owns both halves but never in one run: the **`Acceptance tests:` stage**
   turns the brief's §7 into executable, RED tests against the package's public API (plus the
   §5 signature stubs so they compile) and pushes them; dev-leader reads them against the spec
   and pins `at_sha`; the **`Build:` stage** implements against those frozen tests until green.
   A modified or deleted approved test after `at_sha` is a `blocking` review finding — a wrong
   test goes back to the leader, never gets edited to pass. How dev-backend reaches green inside
   Build (unit red/green/refactor) is its own business and is not reported; what IS reported and
   re-measured is the outcome: frozen ATs green, full suite green, ≥80% coverage and a mutation
   report per touched class, empty drift check. Why: a single run that writes a test and then
   attests "it failed first" proves only that it ran; the independent read before implementation
   and the lock afterwards are what make red-then-green evidence. For a defect the acceptance
   test is the Prove-It reproduction — see `test-driven-development`.
2. **Correct runner per stack — no substitutions.** TypeScript repos run **jest via ts-jest**
   (`jest.config.js`, `preset: ts-jest`); do not add mocha/vitest (`TS-TEST-001` — note this
   supersedes the stale `PULUMI-TEST-001` mocha reference, which is not the real runner).
   Python repos run **pytest**, patching at the import path the code under test actually uses
   (`MCP-STR-003`, `MCP-TEST-001`). .NET repos run **xUnit** (or the project's existing
   runner) with FluentAssertions and Moq/NSubstitute **on abstractions only**, `[Theory]` for
   parameterized cases, `WebApplicationFactory<T>`/Testcontainers for integration —
   `TEST_DB_PROVIDER` left unset so tests run InMemory, never `SqlServer`.
3. **Test naming and placement per stack.** TypeScript: `<unit>.test.ts` matching the
   `testMatch` glob, beside or under the source (`TS-TEST-002`). Python: `tests/` alongside
   the `src/` package it covers (`MCP-STR-001`).
4. **New logic ships with a test — authored by dev-backend, in the same Build.** New
   builder/helper/type-composition TS logic ships with a `*.test.ts` (`TS-TEST-003`); new
   Pulumi builder behaviour ships with a unit test under Pulumi mocks
   (`pulumi.runtime.setMocks`) (`PULUMI-TEST-001`); every class touched in a DEV Team cycle
   reaches the coverage gate in statement 6 before Build can go `done`. Tests are part of
   dev-backend's done: a Build reported `done` without them is a defect against this policy.
   **Coverage review is a mandatory Build step**: after the implementation is green,
   dev-backend measures coverage per touched class and reads each class against its tests —
   every public behaviour, branch, and error path the change added must be exercised; gaps are
   closed with behaviour tests before sign-off, never left for review to find.
5. **Test behaviour and contracts, not implementation.** Tests survive behaviour-preserving
   refactors: no asserting on private members, internal call order, or brittle selectors.
   Assert on state/outcome. Pulumi tests mock the SDK/cloud-provider calls, never real cloud
   APIs, and cover resource/property mapping, input validation, and error paths — no snapshot
   tests as a behavioural substitute.
6. **Coverage gate — scoped to the change, both conditions required.** All existing tests
   pass — full suite green, zero errors, zero warnings, and a clean `dotnet pack` (.NET) or
   `npm pack` (TS). Combined unit + BDD-unit coverage of every class/module **touched** in the
   cycle reaches **≥80%**, measured only over files the feature branch changed
   (`git diff --name-only origin/dev...origin/<feature-branch>`, excluding test files) — never
   a repo-wide figure.
7. **Never inflate coverage.** No trivial tests on getters or framework code. If 80% on a
   touched class is genuinely unreachable, flag the untestable paths to dev-leader instead of
   padding; if code is untestable as written, propose the smallest design change rather than
   silently rewriting production logic to suit a test.
8. **FIRST.** Fast, Isolated, Repeatable, Deterministic — no real time, network, live cloud
   API, random seeds, or order dependence; mock only at boundaries that are slow,
   non-deterministic, or have uncontrollable side effects.
9. **Arrange-Act-Assert / Given-When-Then, one behaviour per test.** Name the test for
   scenario + expected outcome. DAMP over DRY in tests — each test reads as a self-contained
   spec, not one that requires tracing shared helpers.
10. **Test doubles, cheapest that works.** Real implementation > fake > stub > mock.
    Over-mocking produces a suite that passes while production breaks.
11. **Test pyramid.** ~80% small/unit, ~15% integration, ~5% E2E-equivalent (in-process
    BDD-style). The Beyonce Rule: if you liked it, you should have put a test on it.
12. **Commit and push tests with the code before reporting, pass or fail.** A run that ends
    in `blocked` (red suite, coverage gap, untestable path) still pushes its tests — the
    failing scenario IS the evidence the leader and the next run need.
13. **Never edit a test to make it pass.** A red test against correct spec behaviour is an
    implementation defect — fix the code. A test wrong against the spec is fixed as a test,
    stated as such in the report.

## Roles & responsibilities

- **dev-backend** — the **sole author of the cycle's tests and code**, and owner of this
  policy's in-repo enforcement: writes the tests first from the spec's acceptance criteria,
  implements against them, runs the coverage review, measures and reports per-touched-class
  coverage, and is the only role whose sign-off (a `done` flip on its Build with a green suite)
  satisfies statement 6. Never flips `done` on a red suite or a coverage gap.
- **dev-leader** — gates the cycle: no PR authorization or finalize while a Build sub-task is
  `blocked`, its report lacks per-touched-class coverage evidence, or the Review sub-task is
  `blocked` mid-rework. Never runs tests itself — reads the evidence and trusts the PR gate's
  independent re-check.
- **pr-reviewer** — re-checks coverage and behaviour-vs-implementation assertions at the PR
  gate as an independent pass over the same diff — the only pair of eyes on the tests that did
  not write the code, so a coverage miss or an implementation-shaped test here is REWORK.

## Definition of Done / compliance

- New/changed logic has a test; every bug fix carries a reproduction test that failed before
  the fix and passes after.
- Full suite green — pre-existing tests plus new ones — zero errors, zero warnings.
- ≥80% combined coverage on every touched class/module, reported per file, never repo-wide.
- No skipped/disabled test introduced to make the suite pass.
- Clean `dotnet pack` / `npm pack` (or the Python package's equivalent build check).

## Enforcement

`pr-review-gate`'s testing dimension verifies tests exist for changed logic, assert behaviour
not implementation, cover edge cases, and that changed-line coverage meets the gate (override
per repo via `.pr-review.json`). A coverage miss or missing tests on touched logic is a
`blocking`/`important` finding that forces REWORK regardless of the weighted score.

## Exceptions & waivers

- The in-repo coverage gate (statement 6) has **no** waiver — there is no deployed
  environment or later integration stage to catch what it would have found; this is the
  only proof a published package works.
- A coverage override lives in a repo's `.pr-review.json`, never granted ad hoc per PR.
- No waiver exists for a bug fix shipped without its reproduction test.

## References

- [`test-driven-development`](../../skills/test-driven-development/SKILL.md) — RED/GREEN/REFACTOR, Prove-It, pyramid, anti-patterns.
- [`nodejs-typescript-standards`](../../skills/nodejs-typescript-standards/SKILL.md) — `TS-TEST-001..003` jest/ts-jest conventions.
- [`python-mcp-standards`](../../skills/python-mcp-standards/SKILL.md) — `MCP-TEST-001..002` pytest conventions.
- [`pulumi-azure-iac-standards`](../../skills/pulumi-azure-iac-standards/SKILL.md) — `PULUMI-TEST-001..003` builder/mock testing and publish-shape checks.
