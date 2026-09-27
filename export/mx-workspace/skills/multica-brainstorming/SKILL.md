---
name: multica-brainstorming
description: "You MUST use this before specifying or designing any feature, enhancement or behaviour change. Runs the requester dialogue on the Multica ticket - numbered questions with your best guesses, approaches, and a spec preview the requester approves in writing - then hands off through the SDLC flow."
---

# Brainstorming Ideas Into Designs (Multica)

Turn an idea into an agreed design through dialogue with the requester, record it **on the Multica issue**, and hand it to the SDLC flow. On a ticket every wake is one turn: each round is ONE comment, and only the requester's written reply moves the dialogue on. The design lives in the platform — never in a local file, never in a git commit.

<HARD-GATE>
Write no spec, design or code, scaffold nothing, and take no implementation action until the requester has approved the spec preview (step 4) in writing. This applies to EVERY change regardless of perceived simplicity.
</HARD-GATE>

## Precedence

Where your role skill already defines the procedure — product-owner's Workflow B, the seven sections of `sdlc-spec-template`, and the spec-review gate in `sdlc-flow-po-orchestration` — **that procedure owns the deliverable's shape and location.** This skill governs only the dialogue that produces it and the hand-off that follows. Workflows with no spec (A, D) use step 2 only, limited to what genuinely blocks the work. Never blend two contradictory procedures: follow the role skill and flag the mismatch to the workspace owner.

`interview-me` owns the intent (who, why, success, constraint, out of scope); this skill owns what follows. Run both as ONE dialogue — one comment per round, never one per skill.

## Anti-Pattern: "This Is Too Simple To Need A Design"

"Simple" work is where unexamined assumptions waste most effort. The preview may be five lines, but you MUST present it and get approval.

## Checklist

Track these in your own todo list — never as Multica issues — and complete them in order:

1. **Read context** — ticket and thread first, then code
2. **Clarify** — numbered questions, each with your best guess, ONE comment per round
3. **Propose approaches** — only when the requester has a real choice
4. **Present the spec preview** — ONE comment, approved in writing
5. **Record the design** — where your role skill says; the original ask survives
6. **Self-review what you recorded** — placeholders, contradictions, ambiguity, scope
7. **Hand off through the SDLC flow** — never implement off the back of your own design

Steps 2–4 loop until the requester approves the preview in writing.

## 1. Read context

The ticket is context, not just the code:

- `multica issue get <id> --output json` — description, status, assignee, creator, parent, project.
- `multica issue comment list <id> --compact --output json` — decisions already made. Read this BEFORE asking anything; never ask what the thread already answered.
- `multica issue children <id> --output json` and `multica issue metadata list <id> --output json` when the ticket has structure.
- Then code: `multica repo checkout <url> --ref dev`, CodeGraph before grep (`codegraph explore "<symbols or question>"`), every conclusion citing `file:line`. No evidence → say so; never guess.
- Pipeline YAML, build scripts and chart values are NOT in the code graph — read those files directly. A claim about a document (README, `docs/` page, design file) is checked against the document itself, never against a code inventory of it.

**Assess scope before detail.** If the request is several independent subsystems, say so in the first round and help decompose it into separate tickets rather than refining a design that should be three designs. Each piece gets its own ticket → design → delivery cycle.

## 2. Clarify

Ask ONLY what research cannot answer: business rules, scope, priorities, trade-off preferences.

Each round is ONE comment, mentioning the requester — `mention://member/<id>` for a human, `mention://agent/<id>` for an agent creator (`creator_type`/`creator_id` from `multica issue get`):

- **My read:** your one-line hypothesis of what the requester wants, with a confidence number.
- **Numbered questions**, each with **Guess:** and the evidence behind it. Ask only questions that do not depend on each other's answers; a dependent question waits for the next round.
- **Reply by number** — ask for "1 yes · 2 no, because …", so every answer is traceable.

Then **STOP and wait**, ticket `in_progress`. Repeat until zero open questions remain.

**Only a written reply answers.** A status move, a resolved thread, or silence is not an answer and never confirms a guess. On such a wake, post ONE short comment listing the numbers still open, with the requester's mention, and stop.

**Cover these before the preview** — they are what the spec gate most often finds nobody asked:

- **Out of scope** — what this change does NOT do.
- **Examples** — for each business rule, 1–2 cases with real values, plus one refusal or edge case. Agreed examples become the §5 scenarios.
- **Contract** — for each new or changed field: required or optional, allowed values, default, and what existing rows get. For each refusal: which field is at fault.
- **Break or add** — must any existing caller change (a package consumer, another service, an external client)? Additive or breaking is the requester's call, never yours.
- **Prerequisites** — anything outside the team the change waits on (a consent, a secret, another ticket), and who owns it.

A decision made anywhere else — a side thread, another ticket, a chat — goes into the next round's comment, so it lands on this ticket.

## 3. Propose approaches

Only when the requester has a real choice: 2–3 lettered options in that round's comment, your recommendation first with its reason. YAGNI ruthlessly — strip speculative features out of every option before you present it.

Options differ in behaviour, scope or contract — never in classes, layers or files. For product-owner that design belongs to dev-leader (Policy 06 statement 1).

## 4. Present the spec preview

ONE comment, mentioning the requester, before any spec is written:

- **Summary** — two sentences: what changes, who benefits.
- **Done means** — the result a person can observe when the change works.
- **Rules** — each business rule, with its agreed examples.
- **Contract** — each new or changed field and endpoint, or `none`.
- **Placement** — the owning repo, each new dependency, additive or breaking, or `stays inside <repo>`.
- **Not in this change** — one per bullet.
- **Decisions** — each answer so far, with who gave it and where.

Before posting, check the rules against each other. Two rules that cannot both hold ("an empty group can be moved" and "no group is its own parent") are a question for the requester, not a spec.

End with: "Reply `approved`, or name the lines to change." Then **STOP**. A written approval releases step 5; anything else starts a new round.

## 5. Record the design on the issue

The Multica issue is the durable home of the design.

- **Keep the original ask.** Before the first description write, post the requester's original description as ONE comment headed `Original request` (no mention) unless the thread already has one.
- **product-owner** — the spec goes into the ticket description per `sdlc-flow-po-orchestration` Workflow B, built from the approved preview; every Decisions line lands in the spec.
- Write the file **inside your working directory** (e.g. `./spec.md`), then `multica issue update <id> --description-file ./spec.md`. Delete the file afterwards. Treat a failed write as fatal — never let a stale file from another run leak in.
- Diagrams, screenshots, renders: `multica attachment upload <path>`. That command is the only thing that actually delivers a file to a reader.
- **Never make a local path the deliverable** — no `docs/…/design.md` as the record, no git commit, no absolute path or `file://` link in a comment. A runtime path is dead to every reader but you. Reference code locations as inline code (`path/to/file.cs:42`), never as a link.
- **No ticket yet?** Run the dialogue in the conversation and ASK whether to create an issue for it. Never auto-create one, and never assign it to yourself.

## 6. Self-review what you recorded

Re-read it with fresh eyes and fix inline — one pass, no loop:

1. **Placeholders** — any "TBD", "TODO", empty section, or vague requirement?
2. **Consistency** — do sections contradict each other, or the approved preview?
3. **Coverage** — every preview decision is recorded; every agreed example is a scenario.
4. **Scope** — is this one deliverable, or does it need splitting into separate tickets?
5. **Ambiguity** — could a requirement be read two ways? It is a question for the requester, not your pick.

## 7. Hand off through the SDLC flow

The approved design is input to the delivery pipeline, never a licence to implement. Shared contract: `sdlc-flow-delivery-pipeline`. Your terminal step depends on your role:

- **product-owner** — the design becomes the main-ticket spec. Feature or enhancement → `[S#]` spec-review gate, then Workflow C once APPROVED. Pipeline or helm chart change → **Workflow D, straight to `devops`**; never dev-team, never qc-team. You stay read-only on code throughout.
- **platform assistants (`default`, `claude_ultra`)** — you do not spec or implement product work. Stop at the confirmed intent (`interview-me` step 4), write it into the ticket you file, and route it: product work to `product-owner` in `mx-main`, CI/CD and helm charts to `devops`, everything else per your own routing rules.

Mention only the requester in a dialogue comment. Never mention another agent there: every agent mention link enqueues a run, even a quoted one.

Status discipline on your own ticket: finished → `done` (never `in_review` — it fires no trigger and strands the ticket); waiting on answers → stay `in_progress`; genuinely stuck → `blocked` plus a plain comment for whoever must unblock you.
