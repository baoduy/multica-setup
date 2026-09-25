# SDLC Implementation Brief — dev sub-task contract

**What dev-leader writes into a coding sub-task's description.** One to two pages, aimed at an agent that can read repo but cannot read your mind: what already exists, what changes, what must not be touched, and how "done" is verified.

This is NOT feature spec. Business spec lives on MAIN ticket per `sdlc-spec-template` — problem, behaviour, security, and Gherkin — and is what requester approves and `spec-reviewer` scores. This file is the layer below it: dev-leader's translation of that spec into a task list against real code. Do not paste business spec into a sub-task and call it a brief; that is how a sub-task ends up building a new entity and new SQL tables for a need existing methods already covered.

**You own the reuse/modify/add decision.** The business spec no longer carries a Change Map — the class- and method-level call of what to `KEEP`, `MODIFY`, `EXTEND`, add as `NEW`, or `REMOVE` is yours, made here in §3 Change set from CodeGraph research. Research before you write each row: a `KEEP`/`MODIFY`/`REMOVE` row names a symbol that exists today, and a `NEW` row is valid only after searching for something to reuse and finding nothing. A new entity, table, or migration needs its own `NEW` row or it is out of scope. Only a `REMOVE` row authorises deleting a public member, endpoint, config key, column or table; dead private code the change orphans is yours to clean up without a row. This is the section that stops the sub-task rebuilding what already exists.

**The spec's §3a contract is binding input.** Every field and endpoint §3a declares has a Change set row covering it. A field or endpoint you need beyond §3a is your design call and gets its own row; one that changes what §3a agreed — a different type, length, verb or path — goes back to product-owner on the ticket instead of landing quietly in the brief.

---

## Template

Copy from `# <TICKET-ID>` down, fill it in, delete guidance blockquotes, and write it with `--description-file`.

# `<TICKET-ID>` — `<Short imperative title>`

| | |
|---|---|
| **Type** | New feature \| Enhancement \| Refactor \| Bug fix |
| **Repo / branch** | `<repo>` → `<the cycle's feature branch — one per cycle, never a new one per sub-task>` |
| **Projects in scope** | `<src/Foo.Api, src/Foo.Domain, tests/Foo.Specs>` |
| **Main ticket** | `<MXW-nnn>` — approved spec (business-level; no Change Map) |

**Delta markers**

| Marker | Meaning for agent |
|---|---|
| `KEEP` | Exists and is correct. Do not modify. Behaviour must still hold at end. |
| `MODIFY` | Exists. Change it as described. Preserve everything not described. |
| `EXTEND` | Exists. Add to it without altering current behaviour. |
| `NEW` | Does not exist. Create it. |
| `REMOVE` | Exists. Delete it, including its tests and any dead references. |

---

## 1. Goal

`<Two or three sentences. What user can do after this change that they could not before. No background, no business case — those are on main ticket.>`

## 2. Current state

> Anchor agent in code. Paths and type names, not prose. Resolve every row with CodeGraph before writing it.
>
> For a brand-new capability write: **None — new capability.** Then list nearest existing pattern to follow for consistency.

| Component | Path | Current behaviour |
|---|---|---|
| `<Type / method / table / endpoint>` | `<src/…/File.cs>` | `<what it does today, one line>` |

**Follow these existing patterns:** `<path to closest analogous implementation to mirror for structure, naming, error handling, and test layout>`

**Test seam (for the Acceptance-tests stage):** `<the inbound port the scenarios drive — application service / handler / public API type — and the outbound ports to fake in memory (repository, clock, bus, external client) with the existing fake or the interface to implement>`. No seam exists → add the smallest one as a §3 row; the Acceptance-tests run never refactors to create it.

**Verify before changing:** confirm each row above exists as described. On any mismatch, flip sub-task `blocked` and report it — do not proceed. A stale brief is most common cause of a duplicated implementation.

## 3. Change set

> Delta and nothing but delta. One row per unit of work, ordered so each row compiles on top of previous one. This is agent's task list, and the reuse/modify/add decision itself — made from CodeGraph research, see the delta markers above.

**Every edge case you name anywhere in this brief must bind as a §3 row.** A `[Flags]` combination, a non-finite value, an out-of-range input, a null element, a platform difference, an ordering requirement — if you mention it in §5, §6, §9 or a prose note, then §3 carries a row requiring a fact for it, or an explicit `no fact — reason: <why>`. Prose is not binding and the implementer is not wrong to skip it: DRK-1211 §6 named the `[Flags]` combination, §3 did not require a test, it shipped untested and came back as DRK-1213.

**Never prescribe a test's shape without naming the mutation it must catch.** A §3 row that dictates how a guard is written owns that guard's defects. Write it as "assert X such that deleting Y turns the suite red", never as a literal assertion to copy: DRK-1214 §3 row 6 prescribed a `\r` guard the CI host satisfied by itself, so deleting the normalisation it guarded left the suite green — the reviewer traced that defect to the brief, not the implementer (DRK-1223).

**Never instruct a change that fails CI by arithmetic without also authorising what absorbs it.** Dropping an `[ExcludeFromCodeCoverage]`, deleting tests, or moving code between assemblies moves the coverage ratchet. If the repo's config will go red for it, the config change belongs in §3 too — otherwise the cycle burns rework rounds on a number no implementer can reach (DRK-1204: merit 9.9, scored 6.9, both rounds spent, human merge).


| # | Marker | Component | Path | Change |
|---|---|---|---|---|
| 1 | `NEW` | `<Type>` | `<path>` | `<what to create, with key members>` |
| 2 | `MODIFY` | `<Type.Method>` | `<path>` | `<current behaviour → required behaviour>` |
| 3 | `EXTEND` | `<Type>` | `<path>` | `<what to add>` |
| 4 | `NEW` | `<migration>` | `<path>` | `<schema change>` |

## 4. Out of scope — do not change

> Most valuable section in an agent brief. Without it an agent will helpfully refactor adjacent code, rename things for consistency, upgrade packages, or "fix" tests it does not understand.

- `<Component / path>` — `<why it stays as is>`
- Do not rename existing public members, endpoints, config keys, or database columns
- Do not upgrade or add package references beyond those listed in §5
- Do not reformat or refactor files other than to make changes in §3
- Do not weaken, skip, or delete an existing test to make a new one pass. If an existing test conflicts with this brief, stop and report it

## 5. Contract

> Only what changes. Omit section entirely if nothing external changes.

**API** — `<METHOD> <path>`
```json
// request
{ }
// response <status>
{ }
```

**New errors**

| HTTP | Code | Condition | Message |
|---|---|---|---|
| `<nnn>` | `<CODE>` | `<condition>` | `<user-facing text>` |

**Types / signatures**
```csharp
// NEW
<signature>
// MODIFY — before → after
<old signature>
<new signature>
```

**Config** — `<key>`: `<type, default, valid range, where it lives>`

**Packages** — `<only additions, with version, or None>`

## 6. Rules

> New or changed rules only. Existing rules that still apply belong in §2 or `@existing` scenarios. Numbered so Gherkin can reference them.

| ID | Rule |
|---|---|
| R1 | `<if … then …>` |

**Edge cases to handle explicitly:** `<null / empty / boundary / concurrent / already-in-that-state>`

## 7. Acceptance criteria

> Derived from main ticket's §7, narrowed to this sub-task's slice.
>
> `@existing` scenarios describe behaviour that already works and must still work — regression baseline. Run them first and confirm they pass before writing any code; if they do not, §2 is wrong.
>
> `@new` scenarios are target. All must pass when work is done. Nothing else counts as done.
>
> **This block IS the acceptance-test source.** The `Acceptance tests:` sub-task turns it into executable tests verbatim (feature file + steps through the test seam in §2, or one public-API test per scenario), RED, and pushes them; you read them against the spec and pin `at_sha`. From then on the scenarios are frozen for the Build run. Write every expected value as a literal the test can copy — a scenario whose outcome can only be described by running the code is not an acceptance criterion.

```gherkin
@<area>
Feature: <name>

  Background:
    Given <minimal shared context>

  # ── Existing behaviour — must remain green ──────────────────────
  @existing
  Example: <current behaviour most at risk from this change>
    Given <context>
    When <action>
    Then <outcome>

  # ── New behaviour — must be made green ─────────────────────────
  @new
  Example: <primary new capability, happy path>
    Given <context>
    When <action>
    Then <outcome>

  @new
  Scenario Outline: <rule R1 boundaries>
    Given <context with <param>>
    When <action>
    Then <outcome is <expected>>

    Examples:
      | param | expected |
      | <v>   | <e>      |

  @new
  Example: <rejection / failure case with a specific error>
    Given <context>
    When <action>
    Then <the request is refused with error "CODE">
    And <no state changed>
```

## 8. Done when

> Machine-checkable wherever possible. These rows become EVIDENCE table of your completion report (`blocker-report` skill), line by line, pass/fail.

- [ ] `dotnet build` clean, no new warnings
- [ ] `dotnet test --filter "Category=existing"` — all pass (regression intact)
- [ ] `dotnet test --filter "Category=new"` — all pass
- [ ] Coverage on changed files ≥ `<n>%`
- [ ] Mutation report per touched class (Stryker; every surviving mutant dispositioned) — or manual mutation run with the tool named unavailable
- [ ] `git diff <at_sha>..HEAD -- <AT paths>` empty (no approved scenario modified or deleted); added tests listed
- [ ] Every §3 row implemented; nothing outside §3 modified (confirm with `git diff --stat`)
- [ ] No `TODO`, commented-out code, or placeholder implementations left behind
- [ ] `<migration applied and reversible / OpenAPI regenerated / docs updated>`
- [ ] Every §4 constraint respected
- [ ] Pushed to cycle's feature branch (not an `agent/...` branch), sub-task set `done`

## 9. Ask, do not assume

> If any of following is unresolved, flip sub-task `blocked` and post a plain comment for whoever must unblock you rather than choosing. Anything absent from this brief that turns out to require a decision belongs here too.

| # | Question | Default if unanswered |
|---|---|---|
| Q1 | `<question>` | `<None — must ask>` \| `<stated default>` |

---

## Notes for dev-leader

Keep whole brief under two pages. If it grows past that, sub-task is too large — split it into sequenced stages that each compile and pass tests on their own.

Three failure modes this format exists to prevent:

- **Agent reimplements something that exists.** Cured by §2 being specific about paths and type names, and by §3 KEEP rows naming the exact symbol to call instead of rebuild.
- **Agent changes far more than asked.** Cured by §4 and `git diff --stat` check in §8.
- **Agent breaks working behaviour to satisfy a new requirement.** Cured by `@existing` tag: baseline is executable, not a promise.

**One brief, two sub-tasks.** The same brief is the description of both the `Acceptance tests:` and the `Build:` sub-task for a surface. After the Acceptance-tests run reports its RED SHA, read the pushed test files against the spec — every §7 scenario present, none softened, expected values literal, readable — then append to the Build description, before promoting it:

> **Acceptance tests approved.** `at_sha`: `<RED commit SHA>` · paths: `<tests/…/Feature.feature, tests/…/Steps.cs, …>`. Frozen: do not modify or delete; additions allowed and must be listed.

Open the **Acceptance-tests** sub-task's first comment with assignee's mention and this instruction:

> Write the acceptance tests for this brief — tests only. Verify §2 against repo and run `@existing` scenarios to confirm baseline; on any mismatch flip `blocked` and report. Turn §7 into executable tests verbatim through the §2 test seam; production code limited to the §5 signatures with not-implemented bodies. Expected values are literals from §7, never computed by calling production code. Run: `@existing` green, every `@new` red for a nameable reason. Commit, push, report the RED SHA, the test file paths and a per-scenario table, then set this sub-task `done`. Do not implement anything.

Open the **Build** sub-task's first comment with assignee's mention and this instruction:

> Implement this sub-task per its description. Before writing code: verify §2 against repo and run `@existing` scenarios to confirm baseline. On any mismatch, flip this sub-task `blocked` and report — do not proceed. Then work through §3 in order until every `@new` scenario at `at_sha` is green — the approved acceptance tests are frozen: never edit, skip or weaken one; a wrong one is a `blocked` to me. Respect §4 absolutely. For anything in §9, flip `blocked` and ask rather than deciding. Finish with a completion report per `blocker-report` skill — §8 line by line as its EVIDENCE rows — then set this sub-task `done`.