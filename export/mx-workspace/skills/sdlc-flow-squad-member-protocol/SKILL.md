# Squad member protocol — triggers, status, defect loops

You are squad MEMBER (implementer, verifier, tester, runner) working under
squad leader. This is machinery for waking right actor and closing
sub-task. Your own instructions name your leader and carry their mention token —
use that token wherever this skill says `<@leader>`. Leader-side machinery lives
in `sdlc-flow-squad-leader-playbook`; stage map lives in
`sdlc-flow-delivery-pipeline`.

## Mention rule

**One wake signal per handoff — status flip XOR mention, never both, never
neither** (full wake contract: `sdlc-flow-delivery-pipeline`). Your `done`/`blocked`
flip trips the stage barrier that wakes leader — do NOT also mention (second wake,
leader runs twice). A comment with no waking status change stalls unless it carries
the mention. Before ending turn: moved a status that wakes someone? → no mention.
No? → mention the one who must act. Agent mention (`[@name](mention://agent/<uuid>)`,
real UUID — plain name triggers nothing) enqueues a run: only in comments needing
that agent to act, never in done reports or FYIs; non-acting teammates by plain name.

- Done report on your own sub-task → **no mention**. Status is trigger.
- Comment that needs your leader to act → on your **OWN** sub-task, with `<@leader>` —
  never on parent issue: mention wakes leader wherever it is posted, and
  leader↔member communication stays paired on your sub-task while parent stays
  clean for leader's own orchestration. **Mentions are NOT deduped — one
  mention, one run, every time**, even when leader is already `running`. Post
  ONE comment per turn, last thing you do, with at most one mention in it;
  a second mention comment in same turn runs that agent twice on same event.
- Human decision required → that hop is your LEADER's, not yours: report it on
  your OWN sub-task with `<@leader>` and say human decision is needed.
  Leader escalates per pipeline escalation map (by reassigning ticket to
  human — member mention renders link but delivers nothing).

## Status discipline

Only `done` and `blocked` wake your leader — through stage barrier, with no
mention needed. Anything else strands ticket and stalls pipeline.

| Status | When | Meaning |
|---|---|---|
| `done` | your work is complete and green | YOUR work is finished — **not** that leader approved it. Leader review happens after barrier fires. |
| `blocked` | you cannot proceed, or your gate is red | cycle is visibly unfinished; leader gates it |
| `in_review` | **never** | leader-only, for PARENT issue |

Never flip `done` while gate you own is red or fix sub-issue from your own
work is still open — documenting failures in comment does not make it
green.

**LAST action of every run on sub-task is status write.** Status
flip — not your report comment — is what fires barrier and wakes next
actor; run that ends with sub-task still `todo`/`in_progress` leaves
pipeline dead until janitor sweep or human notices. Before ending ANY run:
re-read your sub-task's current status (`multica issue get <id> --output json`)
and confirm it says what your report says — finished work reads `done`, parked
work reads `blocked`. This applies to EVERY completion on a sub-task that has
not yet reached `done` (completion comment with status left at `todo` wakes
nobody — this stranded MXW-562). **Rework on a sub-task that already reached
`done` is the exception: leave it `done` and mention instead.** A re-entry into
`done` re-fires the stage barrier and wakes your leader again for a stage it
already reviewed, so the mention of whoever raised the findings is the wake —
never a re-flip. The same applies to a NEW sub-task the leader files above a
`blocked` gate (a fix round or scope change at stage 4 while Review sits
`blocked` at stage 3): the server closes a stage barrier only when every
sub-task at that stage and below is terminal, so your `done` there fires
nothing — flip `done` as usual AND end your report with the leader's mention;
the leader's brief says so when it applies.

Native status semantics (what each status does server-side, PR close-intent
auto-completion, metadata keys) are documented in platform's built-in
`multica-working-on-issues` skill, present in your workdir — this protocol
layers squad conventions on top of it and never contradicts it.

## Self-review before you report done

The review gate is not where your own defects should surface. Once the code is pushed and the suite is green, review your own diff as if someone else wrote it — read `git diff origin/<base-branch>...HEAD` end to end, not your memory of what you changed — then carry the result into the completion report.

Seven checks. All cheap, and all of them things the review gate WILL run anyway:

1. **Mutation report on every touched class.** Run Stryker (`dotnet stryker` / `npx stryker run`) scoped to the classes you touched; every surviving mutant gets a disposition (`killed — added <test>` / `equivalent` / `accepted — <why>`). Tool unavailable → manual: delete or invert each guard you added, run, confirm RED, restore — and say the tool was unavailable. A test that stays green proves nothing (`test-driven-development`).
2. **Grep your own new assertions** for fragment matches (`ShouldContain`, `Contains`, substring asserts). Each must pin the exact expected text or be anchored to the member it belongs to.
3. **Branch coverage on every branch you added** — per-branch hits, not the class percentage. A 1-of-2 arm is an untested edge case: cover it, or prove with a probe that no input reaches it and say which.
4. **Re-read the brief's prose**, not just §3 — the contract, the rules, §9, every note. Each edge case named there needs a fact or an explicit "no fact, reason".
5. **Re-read every comment and doc comment you wrote or touched** against the code beside it. A comment that overstates what the code does is a defect; so is a class remark that lists two of three cases.
6. **Scope.** `git diff --stat` shows nothing outside §3 and nothing in §4.
7. **Acceptance-test drift** (Build and Fix sub-tasks). `git diff <at_sha>..HEAD -- <AT paths>` shows no modified or deleted approved scenario; every test you ADDED is listed by file. A frozen AT you had to change is not a self-review row — it is a `blocked` with the leader's mention, before any of this.

Then report it. EVIDENCE carries one row per check with its measured result — the mutation you ran and what went red, the per-branch numbers, the grep outcome. Anything a check found that you could NOT fix inside §3 goes in LEFT OPEN with `file:line`: that is the line the reviewer reads, and a self-review finding declared there is never held against the cycle. A completion report with no self-review rows is an unfinished turn.

**Docs and config sub-tasks run checks 4–6 only; Acceptance-tests sub-tasks run 2, 4–6.** There is nothing to mutate in a README.

## Finishing task

1. Run the self-review above — all six checks — then decide verdict against acceptance criteria you were given. Never report done without self-review EVIDENCE rows.
2. On PASS: post ONE plain comment on YOUR sub-task in completion-report
   shape from `blocker-report` skill (RESULT / EVIDENCE / LEFT OPEN) —
   EVIDENCE rows are measured numbers your role owes (coverage %, suite
   status, build status). No agent mention.
3. Flip YOUR sub-task to `done`. Do not hand off to next stage yourself —
   routing is leader's job.
4. On BLOCKED: flip YOUR sub-task to `blocked` **first** — never leave it
   `in_progress` — then post blocker on YOUR sub-task including
   `<@leader>`, formatted per `blocker-report` skill (opens with
   standalone `## BLOCKER` section). Status `blocked` is not optional
   bookkeeping: `## BLOCKER` written while your sub-task still reads
   `in_progress` is invisible to leader's blocked-child scan, so their
   reliable status-driven re-arm never fires and your resume falls back to
   leader remembering to mention you mid-reply — which is exactly how MXW-1426
   stranded three times. Flipping `blocked` is what routes your resume through
   machinery that actually works.
5. **Self-service resume.** If you are woken while your own sub-task sits
   `blocked` (reply landed in your `## BLOCKER` thread) and reply
   actually answers your **Need** (option letter, decision,
   access): flip YOUR sub-task back to `todo`/`in_progress` yourself, reply
   in thread that you are resuming, and continue — do not wait for
   leader to re-arm you. If reply does NOT settle Need, say exactly
   what is still missing in same thread and stay `blocked`.

## Persisting your work

The feature branch is your leader's, cut from `dev` at decomposition, and it is the ONE branch the whole cycle shares: every member commits and pushes directly to it, nobody owns a branch of their own, and nobody opens a PR — the leader opens the single PR once the last implementation stage is done, for the final Review gate.

Any code, test, or config you produce must be committed AND pushed before you
report done — your task runs in fresh checkout and unpushed work is
permanently lost. Branch and push mechanics (worktree rules,
`git push origin HEAD:refs/heads/<feature-branch>` form, push-landed check,
never-create-a-branch rule) are in `sdlc-gitflow`. Follow it; do not
improvise. Missing feature branch on origin → `blocked` + `<@leader>` on your
OWN sub-task, asking leader to create it. Never create it yourself.

## Defect loop — verifier side

Failure caused by YOUR OWN test code is not defect: fix your test and keep
verifying. For clear IMPLEMENTATION defect (failing test, spec violation):

1. **Commit and push your tests first** — failing scenarios ARE
   reproduction.
2. **You never create an issue — your leader does.** `multica issue create` is
   not yours to run, in any project, for any reason: not a fix sub-issue, not a
   bug ticket, not a follow-up. You report; the leader reviews, consolidates
   (findings from several members, or several rounds, may become ONE issue) and
   files it. This is what keeps a verification round from turning into a
   sub-issue storm nobody can route.
3. **Flip YOUR sub-task to `blocked` — never `done`.** Post ONE consolidated
   defect report on YOUR sub-task including `<@leader>` (never on parent) —
   ONE report per round covering every defect found, never one per failing
   test. It must give the leader everything needed to file the fix without
   re-reading your run: per failing scenario, the test name, how to run it,
   expected vs actual, and the suspected code location; plus the branch and
   commit your tests are pushed on. State that you are parked pending
   re-verification. The leader files the consolidated fix issue from this
   report and re-arms you when it lands.
4. **Re-verify when re-armed.** Leader flips your sub-task back to `todo`
   with resume comment. Sync to updated branch tip, re-run FULL
   suite — never only previously failing scenarios. Green → PASS
   protocol above. Still red → NEW round (steps 1–3) with a NEW consolidated
   report to the leader. After 2 rounds on same root cause leader escalates
   instead of looping again.

## Defect loop — implementer side

Receiving `[D<num>-n] Fix:` sub-issue:

1. Reproduce listed failing tests first, then fix IMPLEMENTATION. (A fix
   sub-issue reaches you already reviewed: the leader consolidated it and the
   workspace owner assigned it. It arrives unassigned and starts only when the
   owner assigns it to you — never adopt one that is still unassigned.)
2. **Never edit verifier's tests to make them pass.** If you believe test
   itself is wrong, flip fix sub-issue to `blocked` and raise it on
   fix sub-issue itself with `<@leader>`.
3. Run listed tests locally until green, push, and post done summary
   naming which scenarios now pass.
4. Flip fix sub-issue to `done`, AND post ONE comment on fix sub-issue
   including `<@leader>` asking to re-arm re-verification — that comment needs
   leader to act, so mention is required. It never goes on parent.

## Questions that are not defects

Spec ambiguity, scope questions, legitimate coverage or environment blocker:
no sub-issue. Post comment on your OWN sub-task including `<@leader>` and let
leader decide.

## Anti-patterns

- Mentioning agent in done report → spurious wake-up, duplicated work.
- `in_review` on your own sub-task → nothing fires, ticket stranded.
- `done` with red suite or open fix sub-issue → flow falsely closes.
- One fix sub-issue per failing test → sub-issue storm, unroutable. This is why members report and only the leader files.
- A member creating ANY issue → work enters the board unreviewed and unconsolidated; the leader loses the one place duplicate findings get merged.
- Handing off to next stage yourself → two actors think they own it.
- Reporting done with unpushed work → work is gone.