# Reports — completion and blocker

Every report an agent posts uses one of the two shapes below. The shape is fixed; only the EVIDENCE table grows with the work. Humans scan headings and tables, so the headings are literal and the prose is short.

**Writing rules for both shapes:** one idea per sentence, under 20 words, everyday words, no metaphors. One line per table cell. Commands and error text go in code blocks, never inside a sentence. Numbers as digits. Lead with the result.

## Completion report — any finished work

ONE comment in this shape when work is finished: sub-task done, stage promoted, fix verified, cycle delivered.

```markdown
## RESULT

✅ done — <what changed, one line> · <repo> · `<branch>` · `<commit>`
Deviations from the brief: none | <n>, see below

## DEVIATIONS

| # | Brief said | Done instead | Why (`file:line`) |
|---|---|---|---|

## EVIDENCE

| Check | Result |
|---|---|
| Build | 0 errors, 0 warnings |
| Tests | <n> passed, 0 failed, 0 skipped |
| @existing / @new | green / green |
| AT drift | `git diff <at_sha>..HEAD -- <paths>` empty; added tests: <file>, … |
| Repro RED | `bug-build` only: `at_sha <sha>` (tests + stubs only, pushed before any fix commit); <scenario> red at `at_sha` — <reason>, … |
| Coverage (touched classes) | min <n>% (<class>); all ≥ 80% |
| Branch hits | <n>/<n> new branches hit — or `none added` |
| Mutation | Stryker <score>%, <n> survivors dispositioned — or — manual: <n> guards, each went red |
| Assertions | fragment grep over added asserts: <n> matches, each anchored — or `0 matches` |
| Brief re-read | <n> edge cases named, each a fact or "no fact, <reason>" |
| Comments | <n> comments re-read against the code; <n> fixed |
| Standards | <skills opened> · rule-ids: <ids> · reuse: <result> · SRP: <numbers> · DRY: <result> · docs: <n/a / url> |
| CodeGraph | <n> explore calls — or `unavailable — <why>` |
| Pack | clean |
| CI parity | `<workflow>: <step>` ✓, … · not local: <steps> · jscpd <n> clones · on a throwaway merge with `origin/dev` `<sha>` — nothing skipped; a running sibling's `@new` red named by key (Policy 02 statements 6b, 1c) |
| Pre-review | <b> blocking, <i> important, <n> nit found · fixed <n> · LEFT OPEN <n> · subagent \| inline (<why>) |
| Diff | <n> files, +<a>/−<b>, inside §3 |
| Push | `HEAD` == `origin/<branch>` |

## LEFT OPEN

- <one line each> — or `none`
```

A `build-ui` Build (UI presentation, Policy 02 §1a) writes `n/a — UI presentation` in the @existing / @new, AT drift, Coverage, Branch hits, Mutation and Assertions rows, puts typecheck and lint in the Build row, counts its skips in the Tests row, and adds one row: `Skipped tests | <n>: <file> · <test> · <control it drove>, …` — or `none`.

Rules:

- **RESULT is one line plus the deviation count.** A deviation is anything the brief said that you did differently. It goes in the DEVIATIONS table with its reason, never in prose. Delete the DEVIATIONS section when there are none.
- **EVIDENCE rows are the checks your brief's "done when" names**, using the keys above so the leader and the gate read the same row every time. A skipped check is a row that says `skipped — <why>`, never a missing row. Roles without code (docs, release, review) keep only the rows that apply.
- **No other sections.** A large table (routes, endpoints, per-file numbers) goes into the PR description or a file in the repo, and EVIDENCE links to it.
- **Under 40 lines.** One comment per event: a stage promotion is ONE comment in this shape (RESULT = what closed and what is now `todo` with whom).
- Status and mention rules are unchanged and owned by your role skill.

## Blocker report — work cannot proceed

Whenever you flip an issue to `blocked`, escalate, or hand back a stuck cycle, the comment opens with these sections, in this order, before anything else.

```markdown
## BLOCKER

**Ticket:** <KEY> · <title>
**Stuck on:** <one sentence: what cannot happen>
**Because:** <one sentence>
```
<the exact error line or command output, if any>
```
**I tried:** <1–3 bullets, one line each>
**I need:** <one action or one decision>
**From:** [@name](mention://agent/<uuid>)

## OPTIONS

**A ✅ Recommended — <action>.** Effort: <low / medium / high>. Risk: <one phrase>. Trade-off: <one phrase>.
**B — <action>.** Effort: … Risk: … Trade-off: …
**C — <park it / ship without X>.** Effort: … Risk: … Trade-off: …

Reply with the letter.

## QUESTIONS

1. <Question>? My guess: <answer>.
```

Rules:

- Headings are literally `## BLOCKER`, `## OPTIONS`, `## QUESTIONS` so they stay greppable. One blocker comment per event.
- Every field filled, each at most 2 short sentences. **I need** names a decision or action, never "please advise".
- 2 or 3 options. Exactly one `✅ Recommended`, first. Each option is decidable from its line alone. Include "park it" or "ship without" whenever it is a real choice. Options are things YOU can do once approved, unless the blocker is access, credentials or a business decision.
- `## QUESTIONS` only when a real question remains beyond choosing an option. Delete the section otherwise.
- Under 25 lines. Evidence, logs and links go below the three sections.
- The report is additive, not the delivery: an agent hop still needs `blocked` plus the handoff line on the parent (Workspace Context); a human hop still needs the ticket reassigned to the human at `todo`, asked to reply with the next agent's mention.
- When it clears, reply in the same thread with what unblocked it, one line.

## Root-cause report (product-owner, Workflow A)

Same discipline. Open with the answer and the confidence, then the evidence table, then what is affected, then LEFT OPEN:

```markdown
## RESULT
<Confirmed defect | Not a defect | Question answered> — confidence <n>%. <One sentence: what is wrong and where.> <Next step: fix handed to dev-team | waiting for your confirmation | none needed.>

## EVIDENCE
| Claim | Evidence (`file:line`) |
|---|---|

## AFFECTED
- <component or user, one line each>

## LEFT OPEN
- <one line each> — or `none`
```
