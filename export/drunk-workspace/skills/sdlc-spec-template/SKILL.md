# SDLC Spec Template — shared spec contract

**Single source of truth for what a drunk-workspace feature spec contains.** `product-owner` writes against it; `spec-reviewer` scores against it. If a role skill and this file disagree, this file wins.

**Role boundary.** product-owner states the problem and the required behaviour. dev-leader designs the solution and decomposes it (`sdlc-impl-brief`). A spec that reads like a recipe is defective even when the recipe is right: it hides the problem, blocks better designs, and a code snippet can contradict the prose. Whether a change is minimal or reuses the right helper is judged in code, at decomposition and at the PR gate, never in the spec.

## Who reads a spec

The requester, the workspace owner, the spec gate, the dev-leader, and the implementer. The humans may have intermediate English and no context. Write for them:

1. One idea per sentence. Under 20 words. Active voice.
2. Everyday words. No metaphors or idioms ("pay a tax", "double down", "cheapest moment").
3. Bullets over paragraphs. A paragraph is at most 3 sentences.
4. Numbers as digits (16 routes, 80%). Dates as `2026-09-15`.
5. Name a thing the same way every time. Define an acronym once, in brackets.
6. No code words: no class names, file paths, flags or `file:line`. Product and package names and error codes in backticks are fine.
7. Lead with the answer. Reasoning comes after, short.

## Template

Written into the root ticket description, in this order. Length follows the size of the requirement; a small change collapses §2 and §4 to one bullet each. Every section keeps its heading.

```markdown
# <Plain title: what changes, for whom>

**Summary.** <Two sentences. What changes. Who benefits.>

## 1. Why
- **Problem:** <who has the problem, and what it costs them>
- **Affected:** <the user, role or team>
- **Why now:** <one sentence>
- **Done means:** <the result a person can observe when the change works>

## 2. Today
- <one behaviour per bullet, plain words>

## 3. After the change
- <"The system must …" — one requirement per bullet, observable from outside>

**Must stay true:**
- <an invariant, written as a property, never as the code that holds it>

**Security:** <one sentence: the new trust boundary, or "No new attack surface, because …">

## 4. Scope
- **Repos / packages:** <names only>
- **Not in this change:** <one per bullet>
- **Decisions:** `2026-09-15 · <who> · <decision in one sentence>`
- **Open questions:** none

## 5. Acceptance criteria
```gherkin
Feature: <name>

  @integration
  Scenario: <happy path, one rule>
    Given <real names and values>
    When <one action>
    Then <one observable result>
```
```

Section tests: §1 is done when a non-engineer could act on it. §2 is done when it describes today's behaviour without saying how it is built. §3 is done when every requirement can be checked from outside and every invariant is a property. §4 is done when it holds zero open questions. §5 is done when every requirement in §3 has at least one scenario and every scenario traces to §1.

## Gherkin — BRIEF

Business language · Real data ("treasury-ops", 100.00 SGD, never "a user") · Intention revealing · Essential · Focused (one rule per scenario, one Given-When-Then) · Brief.

- Primary test: would this wording change if the implementation changed? If yes, fix it.
- At most 6 steps per scenario. Happy path first, then refusals and edges. Use a Scenario Outline for variants of one rule instead of copies. No hard scenario count; around 10 is a warning sign to look for Outlines.
- Third-person named actors, never "I". No UI mechanics, config keys, or member names.
- Tag every scenario `@integration` (crosses a real boundary: database, HTTP, package) or `@unit`. The tags are the test-scope statement; there is no separate section.
- When the deliverable is a sample or demo, at least one scenario is observable from the running artefact, not only from its tests.
- The Gherkin block is the only code block in the spec.

## Verification

Testing is never optional and never negotiated at spec time. dev-team writes the §5 scenarios as acceptance tests first, implements against them frozen, and self-verifies at ≥80% coverage per touched class plus a clean pack (`test-driven-development`). §5 says what the suite covers and which kind each scenario is, never whether it runs.

## Quality bar

1. **Clear** — a non-engineer can act on §1 and read §2–§4 without a dictionary.
2. **Correct** — every scenario traces to §1.
3. **Complete** — every requirement in §3 has a scenario.
4. **Secure** — the Security line is concrete.

If the requester asks for an over-built or insecure outcome, push back with evidence at the clarification gate instead of writing it down.
