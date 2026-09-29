# Reports — completion & blocker

Every report you post — completion comment, stage promotion, final report
to human, or blocker — uses one of two fixed shapes in this file.
Shape is fixed; length is not: EVIDENCE table grows with size of
work, prose never does. Humans scan headings and tables — narrative is
optional and always comes last.

## Completion report — any finished work

ONE comment in this shape whenever you report work finished: sub-task done,
stage promoted, fix verified, cycle delivered.

```markdown
## RESULT

✅ done — <one line: what changed, where (repo · branch · PR/commit)>

## EVIDENCE

| Check | Outcome |
|---|---|
| Build | <clean, 0 new warnings> |
| Tests | <199 passed / 0 failed / 0 skipped> |
| Coverage | <87% on touched classes> |
| Diff | <2 files, +112, tests only — matches the brief> |
| <mutation / CI / merge / …> | <numbers, not prose> |

## LEFT OPEN

- <follow-up ticket, deviation, or waiver — one line each, or `none`>

<optional: ONE short paragraph of narrative worth recording>
```

Rules:

- **Every claim in RESULT has EVIDENCE row.** Rows are whatever your
  brief's "done when" list names (build, tests, coverage, diff shape, mutation
  check, merge SHA, …). Check you skipped is row saying `skipped — <why>`,
  never missing row.
- **At most one paragraph below LEFT OPEN.** If it needs more, it is blocker
  report (below) or spec discussion on main ticket — not completion
  comment.
- **One comment per event.** A completed stage gets ONE promotion comment in
  this shape (RESULT = what stage closed and what is now `todo`, with whom) —
  never summary comment plus separate promotion comment.
- **Final report to human:** same shape; RESULT carries PR link, score
  and merge commit. Detail lives in stage comments — link, don't repeat.
- Status, handoff and mention rules are owned by your role skill and the
  workspace context; this file only fixes comment's format.

## Blocker report — work cannot proceed

Whenever you report that work cannot proceed — flipping issue to `blocked`,
escalating to leader, product-owner or human, or handing back stuck cycle —
comment MUST open with standalone `## BLOCKER` section, immediately
followed by `## OPTIONS`. Humans scan for those headings; blocker buried in
prose is blocker nobody sees, and blocker with no options is homework.

## Format

Both sections come FIRST, before any narrative:

```markdown
## BLOCKER

- **Blocked:** <issue id + stage/task that cannot move>
- **Cause:** <root cause in one line — what actually stops you>
- **Tried:** <what you attempted and how it failed>
- **Need:** <exact decision, access, fix or approval required>
- **Owner:** <mention link of whoever must act>

## OPTIONS

**✅ Recommended — A: <the action, one line>**
- Effort / risk: <e.g. ~2h, low risk, no schema change>
- Trade-off: <what it costs or gives up>

**B: <alternative action, one line>**
- Effort / risk: <…>
- Trade-off: <…>

**C: <fallback — often "park it until X" or "ship without Y">**
- Effort / risk: <…>
- Trade-off: <…>

**Reply with a letter and I proceed.**

## QUESTIONS

1. <open question options alone cannot settle — numbered, answerable, with your best-guess answer attached>

<evidence, logs, links and narrative go below the sections>
```

`## QUESTIONS` is included only when open questions exist beyond picking
option — never pad it. Each question is numbered, independently answerable, and
carries your best guess so human can confirm with one word.

## Rules

- Exactly one `## BLOCKER` section per comment, one blocker comment per event.
- Heading is literally `## BLOCKER` — uppercase, H2 — so it stays greppable.
- Every field filled. **Need** must be answerable: name decision or action,
  never "please advise".
- Section is additive, not substitute for delivery: agent hop still
  needs `blocked` + leader's agent mention; HUMAN hop still needs
  stuck ticket reassigned to human at `todo` (member mention renders
  link but delivers nothing) — exactly as your role skill prescribes.
- Not blocker: anything you can still work around, or question that does not
  stop you — that is normal comment.
- When it clears, reply in same thread with what unblocked it.

## Resolving blocker — answer is not resolution

Any agent answering someone else's `## BLOCKER`: an answer alone moves nothing — only a status transition or agent mention enqueues a run (wake contract: `sdlc-flow-delivery-pipeline`; MXW-1016 stalled on a correct answer nobody actuated). So: (1) reply INSIDE the `## BLOCKER` thread, never as a new root comment; (2) actuate in the SAME wake — flip the blocked issue `blocked`→`in_progress` (`multica issue status <id> in_progress --no-start`) with a resume comment carrying the assignee's mention link — a leader's move; a member answering another member's blocker instead reports on its OWN ticket and posts its handoff line, or, when you lack authority over that issue, mention one agent who has it; (3) end-of-turn self-check: turn changed no status and enqueued no run → go back and actuate before ending.

## Options rules

- 2–3 options. One is not choice; four is research paper.
- Mark exactly ONE `✅ Recommended`, and put it first. You did analysis —
  say what you would do. Listing options without pick pushes work back.
- Each option is decidable from letter alone: action, its effort/risk,
  and what it trades away. No option may need follow-up question to evaluate.
- Include do-nothing / park / ship-degraded option whenever it is real —
  it is often right call and only human can make it.
- Options must be things YOU can execute on approval, except where blocker
  is access, credentials or business decision only human owns.
- Genuinely no alternative? Keep heading, write one option and one line
  saying why nothing else works — never silently drop section.