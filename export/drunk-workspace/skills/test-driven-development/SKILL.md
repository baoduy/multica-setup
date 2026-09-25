---
name: test-driven-development
description: Acceptance-test-first delivery for agent-run builds. Use when implementing any logic, fixing any bug, or changing any behavior. The acceptance tests are the spec made executable — authored in their own run, approved and frozen before implementation starts, and verified by outcome (frozen ATs green, mutation score, coverage) rather than by a narrated red/green.
---

# Test-Driven Development — agent edition

Two loops. The **outer loop** is the contract: acceptance tests (ATs) derived from the spec's Gherkin, written in their own run, approved and frozen BEFORE implementation exists, green when the work is done. The **inner loop** — unit-level red/green/refactor while you implement — is yours to run however helps you; nobody grades how you reached green. What is graded is the outcome: frozen ATs green, full suite green, mutation score and coverage on the classes you touched.

Why this shape and not "write the test first, watch it fail": when one run writes a test and its implementation, "I confirmed it fails" proves only that the run executed it — not that it failed for the right reason, and not that the expected value was not derived from the implementation it checks. The checkpoint that gives a test meaning is a different reader approving it before the implementation exists, and a lock on it afterwards. Prescribing the ceremony inside a single run produces theatre; separating authorship from implementation and measuring the result does not.

**When NOT to use:** pure configuration, documentation, or static-content changes with no behavioral impact.

## Reading the brief

Your sub-task description is an `sdlc-impl-brief`. Its header row **Mode** tells you which run this is. Section numbers below refer to it: §2 current code, §3 change set, §4 do-not-touch, §5 contract, §6 rules, §7 scenarios in this slice, §8 extra done checks, §9 questions. The spec's Gherkin is NOT in the brief: §7 names the scenarios; read them from the ticket the header's **Spec** row names (`multica issue get <key> --output json`).

**Change-set markers (§3 Op):** `KEEP` exists and is correct, do not modify, behaviour must still hold · `MODIFY` exists, change as described, preserve everything else · `EXTEND` exists, add without altering current behaviour · `NEW` does not exist, create it · `REMOVE` exists, delete it with its tests and dead references.

**Before either mode:** verify every §2 row against the repo and run the `@existing` scenarios; on any mismatch flip `blocked` and report — do not proceed.

## Outer loop — acceptance tests

1. **Author** (`Mode: acceptance-tests`, fresh run, no implementation in context). Read the §7 scenario names, fetch their Gherkin from the Spec ticket, and read §5 and §6. One executable AT per scenario: the feature file is the spec's Gherkin verbatim for the §7 scenarios (library repos without a BDD harness: one public-API test per scenario, named after it). Step definitions drive the application through its inbound port; outbound ports are replaced by hand-written in-memory fakes (see Ports-and-adapters below). **Expected values are literals copied from the spec — never computed by calling production code.** The only production code allowed is the signatures §5 names, with bodies that `throw new NotImplementedException()` (or the stack's equivalent), so the suite compiles. Run it: every `@existing` scenario green, every `@new` scenario red with a reason you can name (not-implemented, assertion), one row per scenario — a `@new` scenario that is already green means the scenario is wrong or the brief's §2 is. Commit tests + stubs, push. Report the RED commit SHA, the AT file paths, and the per-scenario table (`scenario | status | failure reason`), then `done`. Do not implement anything.
2. **Approve** (leader, no execution). Reads the ATs against the spec: every scenario present, none softened, expected values literal and traceable to the spec, business-readable. Pins `at_sha` and the AT paths into the Build sub-task. A rejected AT set goes back to the author with the scenario named — never to the Build run.
3. **Implement** (`Mode: build`, fresh run; `at_sha` and AT paths are in the brief header). The approved ATs are **frozen**: at done, `git diff <at_sha>..HEAD -- <AT paths>` shows no modified or deleted scenario. You may ADD tests — list every addition in the report. An approved AT that is wrong, or unreachable without changing §4 code → `blocked` with the leader's mention. Never edit, skip, tag out, or weaken one to reach green. Implement until the ATs are green, with whatever inner loop you like.
4. **Verify by outcome.** ATs green, full suite green (zero errors, zero warnings, nothing skipped), coverage per touched class ≥80%, mutation report on touched classes, AT-drift check empty. These artefacts are the evidence; a sentence saying you did TDD is not.

## Inner loop — programmer tests (yours)

Write unit tests where they help you design or pin a detail the ATs do not reach. Red → green → refactor at that level is recommended, not reported. The rules that still bind every test you write: test behaviour not implementation, Arrange–Act–Assert, one behaviour per test, name states scenario + expected outcome, DAMP over DRY, cheapest test double that works (real → fake → stub → mock, mock only at slow/non-deterministic/side-effecting boundaries).

## Prove-It (bug fixes)

The outer loop at bug scale. The reproduction test IS the acceptance test: authored in the `Acceptance tests:` stage from the bug's Gherkin, red for the reason the bug report describes, approved, frozen; the fix lands in Build and turns it green; the full suite proves no regression. A fix with no frozen reproduction test is unverified. In a review REWORK round the same rule applies inside the fix run: add the reproduction test first, list it as an addition, then fix.

## Ports-and-adapters — what makes ATs fast and honest

- Drive the **inbound port** (application service, command/query handler, mediator, or the package's public API) — not HTTP, not the UI, not a controller.
- **Outbound ports** (repositories, clock, message bus, external HTTP clients, secrets) get hand-written in-memory fakes implementing the port interface. Not an in-memory database, not a mocking framework scripting call order.
- Compose the application for tests from its ports, the way production composes it from adapters — one factory taking the fakes, so the AT harness signature stays stable as handlers multiply.
- `WebApplicationFactory<T>` / Testcontainers / real adapters only for scenarios tagged `@integration`.
- No port seam where one is needed? That is a §3 row for the leader to add (smallest seam that lets the AT drive the behaviour), reported `blocked` from the `Acceptance tests:` stage — never an ad-hoc refactor made there.

## Mutation score — the regression sensor

Run mutation testing on the touched classes and report it; it replaces hand-narrated "I deleted the guard and it went red" wherever the tool runs.

- .NET: `dotnet stryker --mutate "**/<TouchedClass>.cs"` (install once: `dotnet tool install -g dotnet-stryker`). TypeScript: `npx stryker run --mutate "src/<file>.ts"` (`@stryker-mutator/core` + the repo's runner plugin).
- Report per touched class: mutation score, and **every surviving mutant** with a disposition — `killed — added <test>`, `equivalent — <why no test can tell>`, or `accepted — <reason>`. An undispositioned survivor in code you added is an open finding.
- Tool cannot run (no network, unsupported runner): fall back to the manual mutation check per guard — delete or invert it, run, confirm RED, restore — and state in the report that the tool was unavailable.

## Coverage gate

Scoped to touched classes (production files in the cycle diff, tests excluded), ≥80% each, reported per class — never the whole repo. Never pad with trivial tests on getters or framework code; if code is untestable as written, propose the smallest design change and flag it to the leader.

## Test pyramid

Most tests small and fast, progressively fewer above: **~80% unit** (pure logic, single process, no I/O — milliseconds), **~15% integration** (crosses a boundary: API, database, filesystem — localhost only, seconds), **~5% E2E** (critical flows only). ATs through the inbound port with fakes sit in the unit band. If a change breaks your code and no test caught it, that's a missing test, not bad luck.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Authoring or editing an approved AT inside the Build run | ATs come from the `Acceptance tests:` stage; a modified/deleted AT after `at_sha` is a `blocking` review finding. Wrong AT → `blocked`, leader decides |
| Expected value computed by calling production code (tautology) | Literals from the spec's Examples; the test must be able to disagree with the implementation |
| Narrated RED ("confirmed it fails for the right reason") with no artefact | RED commit SHA + per-scenario failure table from the author run |
| Testing implementation details | Test inputs and outputs, not internal structure |
| Flaky tests (timing, order-dependent) | Deterministic assertions; each test owns its state setup/teardown |
| Testing framework code | Only test YOUR code |
| Snapshot abuse | Snapshots sparingly; review every change |
| Mocking everything | Preference order above; mock only at boundaries |
| ATs through HTTP/UI for `@unit` scenarios | Drive the inbound port with in-memory fakes; keep real adapters for `@integration` |
| "Tested it manually" | Manual testing doesn't persist; tomorrow's change breaks it silently |

## A test that cannot fail is not a test

RED is not just the author stage — it is a property every finished test must still have.

- **Every guard, normalisation, format rule or ordering rule you add must kill a mutant.** The mutation report above is the proof; a surviving mutant on a guard means the guard is satisfied by the environment, not by the code (a `\r` guard asserted `ShouldNotContain("\r")` on Linux, where `Environment.NewLine` is already `\n` — deleting the normalisation it guarded left 58/58 green).
- **Assertions pin the exact expected text, never a fragment.** `ShouldContain("typeof(")` plus `ShouldContain("Marker")` passes with the fragments in unrelated positions; `ShouldContain("typeof(global::Probe.Markers.Marker)")` does not. Anchor an annotation assertion to the member it belongs to.
- **An absence assertion needs a presence sibling.** `dto.Nickname.ShouldBeNull()` for an omitted field also passes when the field is dropped end to end. Pair it with a test that sends a value and asserts it round-trips.
- **Branch coverage on every branch you added, not line coverage.** A 1-of-2 arm is an untested edge case — report per-branch hits. An arm no input can reach is not a gap: prove it with a probe and say so.
- **Every edge case the brief names anywhere — §3 row, contract, rules, §9, a prose note — needs a fact or an explicit "no fact, reason".**
- **Never mutate ambient state in a test** (`CultureInfo.CurrentCulture`, environment variables, static config). Scope and restore it, or pin it on a dedicated thread.

## UI presentation Build (`Mode: build-ui`)

Policy 02 statement 1a: a change confined to a front-end app's screens, layouts, components, styling and copy ships without new tests. No Acceptance-tests stage comes before it and there is no `at_sha`. In this mode:

- Write no test, no coverage figure and no mutation report — the outer and inner loops above do not run.
- Run the app's build, typecheck, lint and every existing suite, unit and acceptance. Each test your change broke gets the runner's own skip (`test.skip`, `it.skip`) and a one-line note — `// skipped: <KEY> — UI presentation change; restored in the UI test pass` — never deleted, never rewritten to pass.
- A §3 file outside the presentation surface (route handler, `lib/`, data access, auth, session, contract, middleware, config) is mis-routed: `blocked` to the leader.
- Done when: build, typecheck and lint clean; every existing suite passes with the skips; every skipped test listed in the report (file · test name · the control it drove); every §3 row implemented and nothing outside §3 changed; pushed; report posted; sub-task `done`.

## Done when (standard list — the EVIDENCE rows of your completion report)

- Build clean, no new warnings.
- `@existing` scenarios green (baseline intact); every `@new` scenario green.
- Full suite passes; nothing skipped or disabled.
- Coverage per touched class ≥ 80%, reported per class.
- Mutation report per touched class with every survivor dispositioned — or the manual run with the tool named unavailable.
- `git diff <at_sha>..HEAD -- <AT paths>` empty; every added test listed.
- Every §3 row implemented; nothing outside §3 changed (`git diff --stat`); every §4 constraint respected.
- Clean `dotnet pack` / `npm pack`. No `TODO`, commented-out code or placeholder left.
- Plus the brief's §8 extra checks.
- Pushed to the cycle's feature branch (`HEAD` == `origin/<branch>`), completion report posted (`blocker-report` shape, DEVIATIONS listed), sub-task `done`.

Run each test command after a change that could affect its result — never re-run an unchanged suite for reassurance.
