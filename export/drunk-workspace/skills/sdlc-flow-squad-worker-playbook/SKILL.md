# SDLC Flow — Squad Worker Playbook

For squad member agents (dev-backend, docs-writer, service-architect, pr-reviewer, release-manager, devops) working staged sub-tasks under a leader. Your own instructions define your role and your quality gates; the Workspace Context defines statuses, wakes and ticket conventions. Your sub-task description is your brief: squad instructions go to the leader only, so everything you need is in the sub-task or in your skills.

## Handoff contract

Exactly one wake per handoff. A plain `done` needs nothing more: when your stage closes, the platform's sub-issue rule wakes the leader. Your handoff line (Workspace Context) is the wake only where that rule stays silent — you go `blocked`, or you go `done` while a sibling at your stage or below sits `blocked`. Then, after your report on your own sub-task and your status flip, post ONE line on the cycle parent — `<KEY> blocked — BLOCKER on <KEY>` or `<KEY> done — report on <KEY>` — with no mention of any kind when the parent is squad-assigned (on an agent-assigned parent, such as product-owner's ticket, it ends with that agent's mention). The platform routes an agent's plain comment on the squad-assigned parent to the leader, in leader role; a mention, `@all` or a `/note` prefix in that line stops it. In those two cases a turn without the line leaves your work unseen. Apart from that one case you never mention an agent, and you never comment on or change another member's sub-task: whatever another member must hear (findings, a fix request, a question) goes on YOUR sub-task, your handoff line wakes the leader, and the leader routes it.

**Rework.** After your sub-task is `done`, a review REWORK reaches you from the LEADER: the leader flips your sub-task `in_progress` and posts one comment on it with your mention, pointing at pr-reviewer's findings on the Review sub-task. Read the findings there, fix, push, and post your report on your own sub-task (completion shape, closure row per finding), flip `done`, then run Finishing step 5: a re-armed Build below the Review stage closes its stage and the barrier wakes the leader; a Fix sub-task filed at or above the `blocked` gate closes nothing, so post your handoff line. Either way the leader re-arms the review gate. Never post on the Review sub-task and never mention pr-reviewer. First command on a rework wake: `multica issue runs <your sub-task> --siblings`; another run of yours already in flight on this cycle means this wake is a duplicate — end the turn with no action, no push, no comment and no handoff line. One fix run per round; two runs pushing the same fix to one branch cost the cycle a rework round.

## Research before you edit

Every sub-task runs on a fresh checkout, so the repo folder may hold `.codegraph/` with no index in it. From the repo root, in the foreground (never `&` — a backgrounded init dies with the run and leaves a half-resolved index): `codegraph status . 2>/dev/null | grep -q "Nodes:" || codegraph init --yes .`. Then `codegraph explore "<every symbol the brief's §3 names, or your question>"` before you grep, find or open a file: it returns line-numbered source plus the callers, callees and existing helpers or fakes a file view hides — the thing you must reuse instead of writing anew. Treat its output as read. Grep/find/Read only for what the index does not hold (YAML, build scripts, `.csproj`, docs). Index missing or `init` failing: say so and fall back, never silently. EVIDENCE carries one row: `CodeGraph: <n> explore calls` or `CodeGraph: unavailable — <why>`.

## Self-review before you report done

Once the code is pushed and the suite is green, read `git diff origin/<base-branch>...HEAD` end to end as if someone else wrote it, then carry the results into the completion report. Eight checks, all of which the review gate will run anyway:

1. **Mutation report on every touched class.** Stryker scoped to the lines the cycle changed (`dotnet stryker --since:origin/dev` / `npx stryker run --mutate "<file>:<start>-<end>,…"`, `test-driven-development`), reported per touched class; every survivor dispositioned (`killed — added <test>` / `equivalent` / `accepted — <why>`). Tool unavailable → manual: invert each guard you added, run, confirm RED, restore, and say the tool was unavailable.
2. **Grep your new assertions** for fragment matches (`ShouldContain`, `Contains`, substring asserts); each pins exact expected text or is anchored to its member. Every test of a delete, overwrite, move or purge asserts the state before the act and the change after it, and a storage or queue adapter change also runs against the repo's emulator fixture (Policy 02 statement 5a). The `Assertions` row counts both.
3. **Branch coverage on every branch you added**: per-branch hits, not the class percentage. A 1-of-2 arm is covered or proven unreachable.
4. **Re-read the brief's prose**, not just §3: contract, rules, §9, every note. Each named edge case has a fact or an explicit "no fact, reason".
5. **Re-read every comment and doc comment you wrote or touched** against the code beside it.
6. **Scope.** `git diff --stat` shows nothing outside §3 and nothing in §4.
7. **Acceptance-test drift** (Build and rework): `git diff <at_sha>..HEAD -- <AT paths>` shows no modified or deleted approved scenario; every test you added is listed by file. A frozen AT you had to change is a `blocked` with your handoff line, before any of this.

8. **Standards** (Build and `build-ui`; Policy 01 statement 15). Open the stack skill the brief's `Standards` row names — `dknet-ddd-conventions` + `dotnet10-efcore10-standards` for .NET, `nodejs-typescript-standards` + `pulumi-azure-iac-standards` for TypeScript/Pulumi, `python-mcp-standards`, `helm-k8s-conventions`, `docker-image-standards` — and check the diff against its rule-ids, the brief's at-risk ones first. Then, whatever the stack:
   - **Reuse:** `codegraph explore` for every new public symbol before keeping it — an existing helper, extension or base type that does the job replaces yours.
   - **DRY:** the same non-trivial block in 3+ places, or 2 copies that already drifted, is merged at the newer, tested copy (`CLEAN-DRY-001/002`). **Tests count** (Policy 01 statement 7a): a setup or arrange block of ~10+ lines copied from the AT harness or another test file is merged into the shared fixture at the second copy. Where the repo's CI runs a duplication gate (SonarCloud), run `npx jscpd --min-lines 10 --reporters console <changed test dirs>` before pushing and fix every clone it reports in files you touched.
   - **Less code:** no dead code, no interface with one implementation and no test-double need, no forwarding wrapper, no reinvented framework or stdlib helper (`CLEAN-LESS-001..004`).
   - **SRP:** measure every touched class — over ~300 lines, a method over ~50 lines or complexity 10, a constructor with 7+ dependencies is split (`CLEAN-SRP-001..003`).
   - **SOLID at the boundaries you crossed:** dependencies point the way the layering allows (.NET: domain never references infrastructure, EF provider types or HTTP clients, `DKNET-LAYER-001..004`; aggregates reference each other by id, `DKNET-AGG-004`); published API is extend-only (Policy 01 statement 12); each new class has one reason to change; depend on an abstraction only where a test fakes it.
   - **New framework API or pattern** the repo does not already use: check the vendor's current official docs (Context7 or the vendor site) and cite the page.
   The row: `Standards | <skills opened> | rule-ids checked: <ids> | reuse: <symbol → reused X / none found> | SRP: largest class <n> lines, method <n> lines / complexity <n>, ctor <n> deps | DRY: <none / merged file:line> | docs: <n/a / url>`.

EVIDENCE carries one row per check with its measured result. Anything a check found that you could not fix inside §3 goes in LEFT OPEN with `file:line`; a self-review finding declared there is never held against the cycle. Docs and config sub-tasks run checks 4–6, `build-ui` Builds 4–6 and 8; Acceptance-tests sub-tasks run 2 and 4–6; a `bug-build` runs all eight, like a Build.

## Finishing a task

1. Decide the verdict against your role's gates. Never report done with a known failure or without self-review EVIDENCE rows.
2. On PASS: ONE plain comment on your own sub-task in completion shape (`blocker-report`: RESULT / EVIDENCE / LEFT OPEN, measured numbers), no mention, then flip `done`. The stage barrier wakes the leader; routing is the leader's job.
3. `done` means your work is complete, not that the leader approved it. A PR being up and awaiting review is exactly `done`.
4. Flip the status in the same turn as the report. A PASS comment with the ticket still `in_progress` wakes nobody.
5. After flipping `done`, always check `multica issue children <parent-id>`: if any sibling at your stage or below is `blocked`, your `done` closed no stage and the barrier stays silent — a parked sibling never flips itself, so nothing else will fire it either. Post your handoff line (`<KEY> done — report on <KEY>`). A same-stage sibling parked on YOUR push is the common case. Your sub-task may carry `Retrigger on done`: that is the leader's bookkeeping for which issues to re-arm — never set, change or clear it.

## You never create issues

`multica issue create` is your leader's. Report what is wrong, where (`file:line`), what you recommend, verifiable acceptance criteria, the suggested owner, and for anything inside a cycle the stage number the fix must carry. The leader consolidates and files; a defect outside the cycle goes to product-owner's bug workflow.

## When you are blocked

Post the blocker on your own sub-task in `blocker-report` shape (`## BLOCKER`, then `## OPTIONS` with one ✅ Recommended, then `## QUESTIONS` when real), no mention, flip `blocked`, then your handoff line (`<KEY> blocked — BLOCKER on <KEY>`). A human decision is your leader's hop, not yours. Spec ambiguity or scope questions: no guessing, no sub-task; ask the leader the same way.

## Delivering to the feature branch

The feature branch is the leader's, cut from `dev`, shared by the whole cycle. Commit and push to it directly (refspec push per `sdlc-gitflow`), verify `git rev-parse HEAD` equals the SHA `git ls-remote origin <branch>` prints — the remote, never the local `origin/<branch>` tracking ref, which a bare `git push` leaves looking correct — and quote that SHA when you report; work left on your `agent/...` branch is lost when the run ends. Never create branches or open PRs, and never run a bare `git push`: with no refspec it pushes your `agent/...` worktree branch to origin, which delivers nothing. If the named feature branch is missing on origin (`git ls-remote` empty), do not create it: `blocked` with your handoff line.
