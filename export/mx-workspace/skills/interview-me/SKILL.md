---
name: interview-me
description: Extracts what the user actually wants instead of what they think they should want. Achieves this through one-question-at-a-time interview until ~95% confidence about underlying intent. Use when an ask is underspecified ("build me X" without "for whom" or "why now"), when user explicitly invokes ("interview me", "grill me", "are we sure?", "stress-test my thinking"), or when you catch yourself silently filling in ambiguous requirements before any plan, spec, or code exists.
---

# Interview Me

What people ask for and what they actually want are different things. The cheapest moment to find that gap is before any plan, spec, or code exists — once building starts, switching costs are real and the misfit gets rationalized into "good enough". This skill closes the gap: one question at a time, with your best guess attached, until you can predict what the user will say before they say it.

## When to Use

- Ask is missing at least one of: **who** it's for, **why** they want it, what **success** looks like, what the binding **constraint** is
- Request is conventional rather than specific ("build me X", "make it faster") and you can't unpack the convention without guessing
- Two reasonable values are in tension (simplicity vs. flexibility, cost vs. speed) and the user hasn't picked
- User explicitly invokes: "interview me", "grill me", "are we sure?", "stress-test my thinking"

**When NOT to use:** unambiguous self-contained asks, pure information requests, mechanical operations, user explicitly chose speed over verification, or you already pass the 95% stop test below.

**Needs a live user.** On a Multica ticket the thread is the live user: each wake is one turn, and the requester answers in writing on the ticket. Never invoke in CI, scheduled runs or autopilots — there, flag the underspecification as a blocker instead of guessing.

## The Process

1. **Hypothesize, with a confidence number.** Before asking anything, write your best one-sentence read of what the user wants plus an honest 0–100% confidence. Below ~70%, append what's still missing on the same line — that tells the user exactly what the interview needs to surface.

```
HYPOTHESIS: You want to answer "how are we doing?" in standup; "dashboard" was the convention that came to mind.
CONFIDENCE: ~30% — missing: who it's for, what "metrics" means here, what success looks like
```

2. **Ask ONE question at a time, each with a guess attached.**

```
Q: <one focused question>
GUESS: <your hypothesis for the answer, with the reasoning that produced it>
```

Wait for the reaction before the next question. One at a time because the third question depends on the first answer, and batches get skim-read. A guess attached because reacting to a wrong guess is faster than generating an answer from scratch, and it surfaces YOUR assumptions — which is what the interview exists to expose. Mitigate polite agreement by being visibly willing to be wrong and occasionally guessing where you expect push-back.

On a Multica ticket a round is ONE numbered comment: every question that does not depend on another's answer, each with its guess; a dependent question waits for the next round (`multica-brainstorming` step 2).

3. **Listen for "want vs. should want".** Danger answers pattern-match best-practice talk without specifics: "scalable", "clean architecture", "the standard approach", "I'm supposed to…". When you hear one, ask: *"If you didn't have to justify this to anyone, what would you actually want?"* — that question often does more work than the previous five.

4. **Restate intent in the user's own words** when confidence is high — tight, line-by-line confirmable:

```
- Outcome:      <one line>
- User:         <one line — who benefits>
- Why now:      <one line — what changed>
- Success:      <one line — how we know it worked>
- Constraint:   <one line — the binding limit>
- Out of scope: <one line — what we're explicitly NOT doing>
Yes / no / refine?
```

"Out of scope" is non-negotiable — half of misalignment is silent disagreement about what is NOT being built.

5. **Confirm — explicit yes only.** NOT yes: "whatever you think is best" (delegation — re-ask with two concrete options), "sounds good" / "sure, let's go" (ambiguous — ask "anything you'd refine?"), silence then "okay start" (gave up, not converged — ask what you missed). On a ticket, a status move, a resolved thread or silence is not a yes either. Fold corrections in, restate, loop until explicit yes.

## The 95% stop test

Done when: *can I predict the user's reaction to the next three questions I would ask?* Checkable, not a vibe. Floor: several rounds without confidence visibly rising means the questions are wrong, not the user — say so: "I've asked X questions and still can't predict your reactions; something foundational is missing. Step back?"

## Output

A **confirmed statement of intent** — the step-4 restate with an explicit yes. Specs, plans, and task lists are downstream; they consume this. Never produce them before the confirmation, and never save an intent doc the user hasn't confirmed.
