---
name: multica-brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation, then records the agreed design on the Multica issue and hands off through the SDLC flow."
---

# Brainstorming Ideas Into Designs (Multica)

Turn ideas into fully formed designs through collaborative dialogue, record agreed design **on Multica issue**, and hand it to SDLC flow. Design lives in platform — never in local file, never in git commit.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented design and requester has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Precedence

Where your role skill already defines spec procedure — product-owner's Workflow B section list and its spec-review gate in `sdlc-flow-po-orchestration`, for instance — **that procedure owns deliverable's shape and location.** This skill governs only dialogue that produces it and hand-off that follows. Never blend two contradictory procedures: follow role skill and flag mismatch to workspace owner.

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every change goes through this process — config tweak, one label, one-line pipeline edit. "Simple" work is where unexamined assumptions waste most effort. Design may be three sentences, but you MUST present it and get approval.

## Checklist

Create task for each item and complete them in order:

1. **Read context** — ticket first, then code
2. **Ask clarifying questions** — one per message
3. **Propose 2-3 approaches** — trade-offs plus your recommendation
4. **Present design** — in sections, approval after each
5. **Record design on issue** — into description via `--description-file`
6. **Self-review what you recorded** — placeholders, contradictions, ambiguity, scope
7. **Request review** — ONE comment mentioning requester, then STOP
8. **Hand off through SDLC flow** — never implement product code off back of your own design

Steps 4→5 and 6→7 loop on "no, revise" until the requester approves.

## 1. Read context

Ticket is context, not just code:

- `multica issue get <id> --output json` — description, status, assignee, parent, project.
- `multica issue comment list <id> --output json` — decisions already made. Read this BEFORE asking anything; never ask what thread already answered.
- `multica issue children <id> --output json` and `multica issue metadata list <id> --output json` when ticket has structure.
- Then code: `multica repo checkout <url> --ref dev`, CodeGraph before grep (`codegraph explore "<symbols or question>"`), every conclusion citing `file:line`. No evidence → say so; never guess.
- Pipeline YAML, build scripts and chart values are NOT in code graph — read those files directly.

**Assess scope before detail.** If request is several independent subsystems, say so immediately and help decompose it into separate tickets rather than refining design that should be three designs. Each piece gets its own ticket → design → delivery cycle.

## 2. Ask clarifying questions

- One question per message. Multiple choice when it fits, open-ended when it doesn't.
- Ask ONLY what research cannot answer: business rules, scope, priorities, trade-off preferences.
- Focus on purpose, constraints, success criteria.
- On ticket rather than in chat, post open questions as ONE numbered comment mentioning requester (`mention://member/<id>` for humans, resolved from ticket's creator fields), then **STOP and wait**. Repeat until zero open questions remain.

## 3. Propose approaches

2-3 options with trade-offs. Lead with your recommendation and reasoning for it. YAGNI ruthlessly — strip speculative features out of every option before you present it.

## 4. Present design

- Scale each section to its complexity: few sentences when straightforward, up to 200-300 words when nuanced.
- Ask after each section whether it reads right so far. Be ready to go back.
- Cover architecture, components, data flow, error handling, testing.
- **Design for isolation** — each unit has one clear purpose, well-defined interface, and can be understood and tested on its own. For each unit, answer: what does it do, how is it used, what does it depend on? If consumer must read unit's internals to use it, boundary is wrong.
- **In existing codebase** — follow patterns already there. Include targeted fixes for problems that genuinely block work; propose no unrelated refactoring.

## 5. Record design on issue

Multica issue is durable home of design.

- Write design to file **inside your working directory** (e.g. `./design.md`), then `multica issue update <id> --description-file ./design.md`. Delete file afterwards. Treat failed write as fatal — never let stale file from another run leak in.
- Diagrams, screenshots, renders: `multica attachment upload <path>`. That command is only thing that actually delivers file to reader.
- **Never make local path deliverable** — no `docs/…/design.md` as record, no git commit, no absolute path or `file://` link in comment. Runtime path is dead to every reader but you. Reference code locations as inline code (`path/to/file.cs:42`), never as link.
- **No ticket yet?** Present design in conversation and ASK whether to create issue for it. Never auto-create one, and never assign it to yourself.

## 6. Self-review what you recorded

Re-read it with fresh eyes and fix inline — one pass, no loop:

1. **Placeholders** — any "TBD", "TODO", empty section, or vague requirement?
2. **Consistency** — do sections contradict each other? Does architecture match described behaviour?
3. **Scope** — is this one deliverable, or does it need splitting into separate tickets?
4. **Ambiguity** — could requirement be read two ways? Pick one and state it explicitly.

## 7. Request review

ONE comment via `--content-file`: what design decides, what changed since last round, and what you need from reader. Mention requester with `mention://member/<id>`. Then **STOP and wait** — their reply is gate. If they ask for changes, revise description and re-run step 6.

Never agent-mention teammate in review request only human needs to read: agent mention enqueues run and can create loops.

## 8. Hand off through SDLC flow

Approved design is input to delivery pipeline, never licence to implement. Shared contract is `sdlc-flow-delivery-pipeline`; your terminal step depends on your role:

- **product-owner** — design becomes main-ticket spec. Feature or enhancement → `[S#]` spec-review gate, then Workflow C once APPROVED. Pipeline or helm chart change → **Workflow D, straight to `devops`**; never dev-team, never qc-team. You stay read-only on code throughout.
- **devops** — approved pipeline or chart design is yours to build. Land it by repo class: app repos commit directly to `dev`; helm repos get `chore/<issue-key>` branch from `origin/main` and PR to `main` that human merges.
- **squad members** — design feeds your leader's staged sub-tasks. Work stage you were given, PR into `dev`, and let pr-reviewer gate decide.
- **platform assistants (`default`, `claude_ultra`)** — you do not implement product work. Route it: product work to `product-owner` in `mx-main`, CI/CD and helm charts to `devops`, everything else per your own routing rules.

Status discipline on your own ticket: finished → `done` (never `in_review` — it fires no trigger and strands ticket); waiting on answers → stay `in_progress`; genuinely stuck → `blocked` plus plain comment for whoever must unblock you.