# Workflow C — edge cases

Open this when a Workflow C wake meets one of the situations below.

## Duplicate phases

Two concurrent sessions can both create a phase pair (a gate that both flips `done` and mentions you fires two enqueues). After every create or promotion, re-list `multica issue children <root-id> --output json`. Per stage keep the ticket with the earliest `created_at` and cancel every later one (`multica issue cancel-task <run-id> --issue <dup-id>` for any live run first, then `multica issue update <dup-id> --status cancelled`). Never pick by title or memory: only `created_at` gives two sessions the same answer. Two live `[P<num>-1]` tickets means two dev-team cycles, two branches and two PRs on one scope.

## A human flipped the root `done` early

Their flip is a decision, not a mistake. Never move the root off `done`. Let the open phases finish (their handoff lines still wake you), post the final summary on the root when they do, and leave the status alone.

## Multi-repo scope

A phase ticket names exactly one repository. When the spec's Scope spans two (a library and its template or consumer), create one `[P<num>-n] Implementation` per repo, sequenced by dependency, with a Release stage between them when the consumer needs the published package: `[P-1]` library → `[P-2]` Release → `[P-3]` consumer → `[P-4]` Release. dev-leader rejects a multi-repo phase `blocked`, announced by its handoff line on your ticket; that is your decomposition defect to fix by splitting.

## Leftovers-shaped tickets

A review's non-gating findings never reach you as delivery work. In-scope leftovers are cleared by pr-reviewer inside its cycle; out-of-scope ones are dropped unless a defect or security finding with a named reproduction, which dev-leader files as an ordinary `bug-report` ticket assigned to you. `Review follow-ups:` tickets are retired: never file one, never accept one as a root, never decompose one into phases. If a bag of nits reaches you anyway (comment wording, assertion polish, coverage of untouched paths), triage it in place with a one-line disposition per finding and flip it `done`. Out-of-scope debt belongs to the monthly arch-reviewer sweep.

## Spec drift after delegation

The spec is frozen when `[P<num>-1]` is created (its description opens with `Spec revision: <n>`). If a requester answer or your own research changes it mid-cycle: do not edit the root or phase description. Post ONE scope comment on the phase ticket with dev-team's mention stating the change and the scenarios it adds or alters; dev-leader adds a scope stage. Amending the description under a running Acceptance-tests stage caused two rejected AT sets and seven dev-backend runs on DRK-1250.

## Legacy titles

`[PHASE-n]` / `[DEV-n]` titles on in-flight tickets are the same tickets as `[P<num>-n]` / `[D<num>-n]`. Reconcile, never duplicate.
