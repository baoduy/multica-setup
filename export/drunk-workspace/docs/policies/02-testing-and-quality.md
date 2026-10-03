# Policy 02 — Testing & Quality

| | |
|---|---|
| **Policy ID** | DRK-POL-02 |
| **Version** | 1.7 |
| **Status** | Active |
| **Owner** | dev-backend |
| **Applies to** | Every code or behaviour change in a drunk repo, across every stack |
| **Related skills** | [`test-driven-development`](../../skills/test-driven-development/SKILL.md) · testing rules embedded in [`nodejs-typescript-standards`](../../skills/nodejs-typescript-standards/SKILL.md) (`TS-TEST-*`) · [`python-mcp-standards`](../../skills/python-mcp-standards/SKILL.md) (`MCP-TEST-*`) · [`pulumi-azure-iac-standards`](../../skills/pulumi-azure-iac-standards/SKILL.md) (`PULUMI-TEST-*`) |
| **Enforced at** | PR review gate ([`pr-review-gate`](../../skills/pr-review-gate/SKILL.md)) |

> **Authority.** This policy is the source of truth for testing and quality across every
> drunk stack. `test-driven-development` and the per-stack `*-TEST-*` rules **implement** it;
> `pr-review-gate`'s testing dimension derives its bar from it. Amend this policy first, then
> cascade — see [change control](00-policies-index.md#change-control).

## Testing at a glance

```
   Every change:   [Acceptance tests run] spec §7 ──▶ executable ATs, RED, pushed
                   [leader, inline]       read ATs vs spec ──▶ pin at_sha (frozen)
                   [Build run]            implement ──▶ ATs GREEN · suite green · ≥80% · mutation report · drift check empty
   Bug fix (Prove-It):  reproduction AT authored RED and frozen ──▶ fix in Build ──▶ green ──▶ full suite
   UI presentation (1a): no AT stage, no new tests ──▶ Build done on build · typecheck · lint · existing suites green
                         a test the change breaks ──▶ skipped with a note ──▶ ONE follow-up issue (dev-leader)

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
   opens — except a UI presentation change (statement 1a). dev-backend owns both halves, in separate runs except for a confirmed bug fix (statement 1b): the **`Acceptance tests:` stage**
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
1b. **A confirmed bug fix proves itself in one run.** A root cycle carrying product-owner's
   root-cause report (Workflow A), whose acceptance tests are only the Prove-It reproductions
   of the reported defect on one surface and whose brief adds no public signature, gets ONE
   `Build:` sub-task with `Mode: bug-build` instead of the Acceptance-tests + Build pair. In
   that run dev-backend first commits and pushes the reproduction tests alone (plus any §5
   stub), each `@new` scenario red for the reason the report names; that commit is `at_sha`,
   reported with its per-scenario RED table. Only then does it implement, in the same run,
   against those frozen tests. dev-leader approves nothing in between. The independent read
   moves to the PR gate, which checks that `at_sha` holds only tests and stubs, predates every
   implementation commit, reproduces the defect (red at `at_sha`, from CI or a local run of the
   AT paths), and matches the root's Gherkin with literal expected values. A failure of any of
   these is `blocking`. Why: a bug's acceptance test is one reproduction whose expected value
   the root-cause report already fixes, so the separate run and the leader's read cost a full
   fresh checkout and a stage hop for little extra assurance; features keep the pair.
1a. **UI presentation ships without new tests, for now.** A UI presentation change — the screens
   and layouts, components, styling and copy of a front-end app (in DKNet.Accounts.Api:
   `ui/components/**` and the `page`, `layout` and `.css` files under `ui/app/**`) — has no
   Acceptance-tests stage, no `at_sha`, no new tests, no coverage figure and no mutation report.
   Its Build is done when the app's build, typecheck and lint pass and its existing test suites
   pass. The rest of a front-end app keeps the full bar in the same cycle: server route handlers
   (`ui/app/**/route.ts`), data access, auth, session and contract code (`ui/lib/**`,
   `ui/contract/**`), middleware and build config. An existing test the change breaks is skipped
   with the runner's own skip and a one-line note naming the ticket — never deleted, never
   rewritten to pass — and dev-leader files ONE follow-up issue per cycle naming the change's §5
   scenarios and every skipped test: the scope of the later UI test pass. The §5 scenarios are
   still written in the spec. A bug fix and a PR-gate rework finding keep their reproduction test
   ([Policy 07](07-bug-and-defect-management.md)). Why: drunk has no UI test standard yet, and the
   owner chose to build the console's presentation first and test it in its own pass (DRK-1745,
   2026-09-25).
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
   closed with behaviour tests before sign-off, never left for review to find. UI presentation
   files are exempt under statement 1a.
5. **Test behaviour and contracts, not implementation.** Tests survive behaviour-preserving
   refactors: no asserting on private members, internal call order, or brittle selectors.
   Assert on state/outcome. Pulumi tests mock the SDK/cloud-provider calls, never real cloud
   APIs, and cover resource/property mapping, input validation, and error paths — no snapshot
   tests as a behavioural substitute.
5a. **A side effect is proven by its effect, through the real adapter.** A test of an
   operation that deletes, overwrites, moves or purges stored state first arranges the state
   the operation must change and asserts that state is present before the act, so the test
   cannot pass on an empty store. After the act it asserts the change itself: the items gone,
   the count changed, the old content replaced. A returned success flag or "no exception
   thrown" is never that proof. When the change touches an outbound storage or queue adapter
   (blob, object storage, queue), that test also runs the adapter against the repo's emulator
   fixture, not only against the in-memory fake: the fake proves the port, the emulator proves
   the adapter's paths, prefixes and request mapping. In DKNet the fixtures are the
   Testcontainers ones in `src/Services/Svc.BlobStorage.Tests/Fixtures` (Azurite, MinIO). A
   repo with no emulator fixture for that vendor says so in the report's LEFT OPEN, and
   dev-leader decides whether a later cycle adds one. Database adapters stay under statement 2
   (InMemory, `TEST_DB_PROVIDER` unset). Why: on DKNet PR #495 (DRK-1898) the Azure folder
   delete matched no blob because of a leading-slash prefix, and the test meant to prove it
   passed on a store it never filled. The PR gate found the defect by reproducing it against
   Azurite, which cost a rework round.
6. **Coverage gate — scoped to the change, both conditions required.** All existing tests
   pass — full suite green, zero errors, zero warnings, and a clean `dotnet pack` (.NET) or
   `npm pack` (TS). Combined unit + BDD-unit coverage of every class/module **touched** in the
   cycle reaches **≥80%**, measured only over files the feature branch changed
   (`git diff --name-only origin/dev...origin/<feature-branch>`, excluding test files) — never
   a repo-wide figure. UI presentation files (statement 1a) are outside this gate.
6a. **Mutation report per touched class — coverage's honesty check.** Coverage says a line ran; only mutation says an assertion would have caught it changing. Every Build except a UI presentation one (statement 1a) reports a mutation run scoped to the lines the cycle changed in the classes it touched — `dotnet stryker --since:origin/dev` on .NET, `npx stryker run --mutate "<file>:<start>-<end>,…"` over the diff's hunks on TypeScript — never the whole class, whose unchanged code the cycle does not own; reported per touched class, with **every survivor dispositioned** — `killed — added <test>` / `equivalent` / `accepted — <why>`. Tool genuinely unavailable → the manual equivalent: invert each guard the change added, run, confirm RED, restore, and say in the report that the tool was unavailable. A Build reported `done` without a mutation report and its dispositions is incomplete the same way a missing coverage row is; dev-leader sends it back and never promotes past it.
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
  independent re-check. On a UI presentation Build (statement 1a) there is no coverage evidence
  to read; dev-leader files the follow-up issue (§5 scenarios and skipped tests) before the PR opens.
- **pr-reviewer** — re-checks coverage and behaviour-vs-implementation assertions at the PR
  gate as an independent pass over the same diff — the only pair of eyes on the tests that did
  not write the code, so a coverage miss or an implementation-shaped test here is REWORK.

## Definition of Done / compliance

- New/changed logic has a test (UI presentation: statement 1a); every bug fix carries a
  reproduction test that failed before the fix and passes after.
- Full suite green — pre-existing tests plus new ones — zero errors, zero warnings.
- ≥80% combined coverage on every touched class/module, reported per file, never repo-wide.
- A mutation report per touched class, every survivor dispositioned (statement 6a).
- Every test of a destructive operation asserts the state before and the change after; a
  storage or queue adapter change is also tested against the repo's emulator fixture
  (statement 5a).
- No skipped/disabled test introduced to make the suite pass — except a test a UI presentation
  change broke, skipped under statement 1a with its note and listed in its follow-up issue.
- Clean `dotnet pack` / `npm pack` (or the Python package's equivalent build check).

## Enforcement

`pr-review-gate`'s testing dimension verifies tests exist for changed logic, assert behaviour
not implementation, cover edge cases, and that changed-line coverage meets the gate (override
per repo via `.pr-review.json`). A coverage miss or missing tests on touched logic is a
`blocking`/`important` finding that forces REWORK regardless of the weighted score. A test of
a destructive operation without its before and after assertions, or a storage or queue adapter
change tested only against a fake while the repo has an emulator fixture, is an `important`
finding (statement 5a). UI
presentation files carry no test requirement (statement 1a); a test skipped without its note,
or a UI presentation cycle without its follow-up issue, is an `important` finding.

## Exceptions & waivers

- The in-repo coverage gate (statement 6) has **no** waiver beyond statement 1a's UI
  presentation exception — there is no deployed
  environment or later integration stage to catch what it would have found; this is the
  only proof a published package works.
- A coverage override lives in a repo's `.pr-review.json`, never granted ad hoc per PR.
- No waiver exists for a bug fix shipped without its reproduction test.

## References

- [`test-driven-development`](../../skills/test-driven-development/SKILL.md) — RED/GREEN/REFACTOR, Prove-It, pyramid, anti-patterns.
- [`nodejs-typescript-standards`](../../skills/nodejs-typescript-standards/SKILL.md) — `TS-TEST-001..003` jest/ts-jest conventions.
- [`python-mcp-standards`](../../skills/python-mcp-standards/SKILL.md) — `MCP-TEST-001..002` pytest conventions.
- [`pulumi-azure-iac-standards`](../../skills/pulumi-azure-iac-standards/SKILL.md) — `PULUMI-TEST-001..003` builder/mock testing and publish-shape checks.
