# Testing standards — BDD,.NET, React

Stack conventions and quality bars for tests in Monxa repos. The TDD cycle
itself (red/green/refactor, prove-it pattern, test pyramid) is in
`test-driven-development`; this skill is the *what good looks like* for this
codebase.

## BDD-first

Cover behavior with Gherkin scenarios; fall back to unit tests only where BDD is
impractical. Use project's existing tooling — Reqnroll/SpecFlow for.NET,
Cucumber.js or playwright-bdd for React/Next.js. Deliver feature files together
with their step definitions in same change.

## Coverage gate

Scope gate to what change TOUCHED — never whole solution. A repo-wide
ratio is pre-existing baseline single ticket cannot move; gating on it blocks
cleanup and hotfix work at baseline.

Both conditions must pass:

1. **All existing tests pass** — full suite green, zero errors, zero warnings.
2. **Combined BDD + unit coverage of touched classes is ≥ 80%** — measured
 over files this change added or modified, not over repo.

Report suite result and per-touched-class numbers (file + %). A repo-wide
figure is FYI only, never gate. Files change deleted carry no coverage
obligation. If 80% on touched class is genuinely unreachable, flag untestable paths to your leader — never pad with trivial tests.

**Don't inflate coverage** with trivial tests (getters, framework code). If code
is untestable as written, propose smallest design change that fixes it —
never silently rewrite production logic to suit test.

## Test behavior and contracts, not implementation

Tests must survive behavior-preserving refactors. No asserting on private
members, internal call order, or brittle DOM/CSS selectors.

- **Structure:** Given/When/Then (BDD) or Arrange–Act–Assert (unit). One
 behavior per test; name states scenario + expected outcome
 (`Should_ReturnNotFound_When_OrderDoesNotExist`).
- **FIRST:** fast, isolated, deterministic, repeatable. No real time, network,
 live databases, random seeds, or order dependence — mock external
 dependencies.

## Gherkin

Business language, not UI mechanics. One behavior per scenario.
`Scenario Outline` + `Examples` for data-driven cases. Reuse step definitions.
Tag meaningfully.

## Acceptance tests through ports

The cycle's acceptance tests (brief §7 as Reqnroll scenarios) drive the
**inbound port** — application service, command/query handler, mediator — never
a controller, HTTP or the UI. **Outbound ports** (repositories, clock, bus,
external clients, secrets) are hand-written in-memory fakes implementing the
port interface, composed through one test factory that takes the fakes the way
`Program` takes the adapters. Not an in-memory database, not a mock scripting
call order. `WebApplicationFactory<T>` / Testcontainers are reserved for
scenarios tagged `@integration`. Expected values are literals from the spec.

## Mutation report

Regression quality is measured, not narrated: `dotnet stryker` scoped to the
touched classes (`--mutate "**/<Class>.cs"`; install once with
`dotnet tool install -g dotnet-stryker`). Report per class the score and every
surviving mutant with a disposition — `killed — added <test>`, `equivalent`, or
`accepted — <why>`. Tool unavailable → manual delete/invert per guard, stated.

##.NET

xUnit (or project's runner), FluentAssertions, Moq/NSubstitute on
abstractions, `[Theory]` for parameterized cases,
`WebApplicationFactory<T>`/Testcontainers for `@integration` scenarios only.
Cover happy path, boundaries, null/invalid input, and exception paths.

## React / Next.js

Vitest or Jest + React Testing Library — query by role/label/text, test-id as last resort. `user-event` over `fireEvent`. `findBy*`/`waitFor` for async. Mock
`next/navigation`; MSW for network. Cover conditional rendering, interactions,
form validation, error/empty/loading states, and accessibility. No snapshot
tests as behavioral substitutes.
