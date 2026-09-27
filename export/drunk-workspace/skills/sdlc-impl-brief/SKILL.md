# SDLC Implementation Brief — sub-task contract

What dev-leader writes into a coding sub-task's description. Reader: an agent that can read the repo but not your mind. Content: what exists, what changes, what must not change, how "done" is proven. Target 6–8 KB; **over 10 KB the surface is too large — split it into sequenced stages.**

This is not the spec. The business spec lives on the root or phase ticket (`sdlc-spec-template`). The brief is your translation of it into a task list against real code, from CodeGraph research. Never paste the spec into the brief.

**You own the reuse/modify/add decision.** A `KEEP` / `MODIFY` / `EXTEND` / `REMOVE` row names a symbol that exists today; a `NEW` row is valid only after you searched for something to reuse and found nothing. A new entity, table or migration needs its own `NEW` row. Only a `REMOVE` row authorises deleting a public member, endpoint, config key, column or table.

**The spec's §3a contract is binding input.** Every field and endpoint §3a declares has a Change set row covering it. A field or endpoint you need beyond §3a is your design call and gets its own row; one that changes what §3a agreed — a different type, length, verb or path — goes back to product-owner on the ticket instead of landing quietly in the brief.

**The spec's §3b placement is binding too.** Put the change in the repo and bounded context §3b names as Owner, and add only the dependencies it declares, in the direction it declares. A design that needs a different owner, a new dependency or a public-surface break §3b did not declare goes back to product-owner on the ticket — pr-reviewer blocks a diff that contradicts §3b.

## Writing rules (agent reader)

1. Tables over prose. One row per unit of work. One line per cell.
2. Every code reference is `path:line` or a symbol. Never describe code the agent can read.
3. Delta and guards only. Repeat nothing that lives in a skill the implementer loads: the marker legend, the acceptance-tests and Build procedures, the standard done-list and the report shape are in `test-driven-development` and `blocker-report`.
4. Reference, do not copy: §7 lists scenario names; the Gherkin stays on the phase ticket.
5. Amend by editing rows and adding one changelog line. Never append a narrative section.
6. Every edge case you name anywhere binds as a §3 row with a `Proof` cell, or an explicit `no test — <reason>`. Prose is not binding.
7. Never dictate a test's shape; name the mutation it must catch (`Proof` column). Never order a change that fails CI by arithmetic (coverage ratchet, moved assemblies) without the config change that absorbs it, as its own row.

## Template

Copy from `# <KEY>` down and write it with `--description-file`. The same brief is the description of both the `Acceptance tests:` and the `Build:` sub-task for a surface; only the `Mode` row differs. A UI presentation surface has only the Build sub-task: `Mode: build-ui`, `at_sha` row `n/a — UI presentation`, and §7 still names the spec's scenarios for the later UI test pass.

```markdown
# <KEY> — <imperative title>

| | |
|---|---|
| **Mode** | `acceptance-tests` \| `build` \| `build-ui` (UI presentation, Policy 02 §1a: no tests) |
| **Repo · branch · base** | `<url.git>` → `feature/<key>-<slug>` @ `<base sha>` |
| **Spec** | <phase or root key> §5, revision <n> (frozen) |
| **at_sha · AT paths** | — until approved · `<tests/…/X.feature>, <tests/…/Steps.cs>` |
| **Projects in scope** | `<src/A>, <src/B>, <tests/C>` |
| **Standards** | `<stack skill(s)>` · at risk: `<3–5 rule-ids, e.g. DKNET-LAYER-001, CLEAN-SRP-001>` |

## 1. Goal
<one sentence: what works after this change that did not before>

## 2. Current code
Only symbols §3 touches or the tests drive. Verify every row with CodeGraph before writing it.

| Symbol | Where | Now |
|---|---|---|
| `<Type.Member>` | `<path:line>` | <one clause> |

Mirror: `<path:line>` · Test seam: inbound `<symbol>` · fakes `<symbol, symbol>`
(New capability: `None — new`, then the nearest pattern to mirror. No seam: add the smallest one as a §3 row.)

## 3. Change set
Ordered; each row compiles on the previous. Op ∈ KEEP · MODIFY · EXTEND · NEW · REMOVE.

| # | Op | Symbol | Where | Change | Proof — deleting this turns red |
|---|---|---|---|---|---|
| 1 | NEW | `<Type>` | `<path>` | <what, key members> | `<scenario or test name>` |

## 4. Do not touch
- `<path or symbol>` — <why>
- No renames of public members, endpoints, config keys or columns. No package changes beyond §5. No reformatting outside §3 rows. No weakening or deleting an existing test.

## 5. Contract (diffs only; delete if none)
| Kind | Before | After |
|---|---|---|
| API `<METHOD> <path>` / type / error `<HTTP CODE>` / config key / package | | |

## 6. Rules
| ID | Rule |
|---|---|
| R1 | if <condition> then <result> |

## 7. Scenarios in this slice
- `@new`: <scenario names from the spec §5, or `all`>
- `@existing`: <feature files or names that form the regression baseline>
- Slice notes (≤ 3 bullets): <narrowing, discriminating Given, seam detail>

## 8. Extra done checks
<Only what the standard list in `test-driven-development` does not cover. Delete if none.>

## 9. Ask, do not assume
| Q | Question | Default if unanswered |
|---|---|---|
| Q1 | <question> | `None — must ask` \| <default> |

## Changelog
- `<date> <who>` — <one line: rows changed, or "at_sha pinned">
```

## Leader notes

- **Three failure modes this shape prevents:** rebuilding what exists (§2 + KEEP rows), changing more than asked (§4 + `git diff --stat`), breaking working behaviour (`@existing` baseline).
- **First comment on each sub-task** carries the assignee's mention and one line: `Mode: acceptance-tests — write the tests per test-driven-development, then done.` or `Mode: build — implement per test-driven-development against at_sha <sha>, then done.` or `Mode: build-ui — implement per test-driven-development (UI presentation: no tests; skip and list what you break), then done.` The procedure itself is in that skill; do not restate it.
- **Approving the acceptance tests:** read the pushed test files against the spec (every scenario present, none softened, literal expected values, readable), then fill the `at_sha · AT paths` header row of the Build description and add one changelog line. Never a new section.
- **A scope change** from product-owner becomes new §3 rows (and §7 names) in a new brief for the new stage, plus a changelog line on the parent's plan comment. Never re-arm a finished Acceptance-tests stage for spec drift.
- **Gate sub-tasks** (Review) get a pointer table, not a brief: repo · branch · base · `at_sha` + AT paths · Build sub-task(s) for rework · root ticket, plus a cycle-specific emphasis section of at most 5 bullets.
