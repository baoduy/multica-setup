# Pre-review — a mini PR gate before you report done

Policy 01 statement 17. Run it on every `Build:` sub-task (any mode, including
`Mode: bug-build`) and every `Fix (review):` sub-task, once code is pushed and
self-review checks 1–3, 6, 7 and 9 are green. qc-team carries no `Build`/`Fix (review)`
of this shape and never runs it. It exists to remove the findings the PR gate would
raise; it does not repeat the gate — no score, no report file, no GitHub calls, one pass.

## How

1. Start ONE subagent with fresh context: the Agent tool, `general-purpose`. Fill in the
   prompt below. No subagent tool available in this run → run the passes yourself and say
   so in the row (`inline (<why>)`).
2. Fix every `blocking` and `important` finding inside §3. Re-run only the tests and
   checks the fix touches, then push.
3. Do not start a second pre-review. A finding you cannot fix inside §3 (needs §4 code,
   or the brief is wrong) goes to LEFT OPEN with `file:line`. A `nit` is fixed only when
   it costs one line.
4. Report one row: `Pre-review | <b> blocking, <i> important, <n> nit found · fixed <n> · LEFT OPEN <n> · subagent | inline (<why>)`.
   Its answers also fill checks 4, 5 and 8 (brief re-read, comments, Standards) — do not
   run those a second time.

## Prompt (fill in, pass verbatim)

```
You review a diff before its PR exists. Read-only: never edit, commit or push.
Repo checkout: <path>. Diff: `git diff origin/dev...HEAD` (a `Fix (review):` sub-task:
`git diff <PR head SHA pr-reviewer scored>..HEAD` only — that SHA is on the Fix sub-task's
description or the findings comment it answers — check each listed finding is closed and
the fix broke nothing nearby; do not re-review the rest of the PR). Brief: <sub-task key>
(`multica issue get <key> --output json`, field description — §7 already carries the
scenarios, §6a the input domain).
Stack skill(s): `dknet-ddd-conventions`, `dotnet10-efcore10-standards`, the repo's own
`CLAUDE.md` (Policy 01 statement 14). At-risk rule-ids: <from the brief's Standards row>.

Report findings only, one line each: `[blocking|important|nit] file:line — what is wrong — what fixes it`.
blocking = wrong behaviour, does not compile, data or secret exposure, a published API
break, a contradiction of the brief's §5 contract or §3b placement.
important = a missing or weak test, a broken standards rule-id, an unhandled input in the
brief's §6a, a stale comment.
nit = anything else worth one line. Never report style the analyzers already enforce.
Proof (Policy 04 statement 1a): a blocking or important correctness or security finding
names the input or state that triggers it, the wrong outcome, and why existing guards do
not stop it; a rule finding cites its rule. Neither → nit or drop. No findings is a valid
answer; never add one to look thorough.

Passes, in order. Use `codegraph explore` for callers and existing helpers, not grep.
1. Brief: every §3 row done, §6 rules hold, every §6a input row has its proof (Policy 06
   statement 10a), every §9 default applied. Nothing changed outside §3, nothing in §4
   changed.
2. Correctness: each changed guard, default, mapping and external call checked against
   empty, null, unknown and boundary values and every enum/option member. Each failure the
   changed external call can raise or return (a thrown exception, or a failed
   `IResultBase` — `DKNET-RES-002`) is handled. Callers of every changed public symbol
   still hold. `UpdateAsync` is never called on a tracked entity (`DKNET-REPO-006`) —
   trace whether the read was tracked or detached. No silent failure (Policy 01
   statement 8): no empty/log-only `catch` that carries on, no empty collection/`null`/
   `default` from a failed call, no rethrow dropping the original exception
   (`NET10-ERR-001..003`).
3. Security: no secret or PII in logs, outputs or state (`LOG-002`). Injection, authn/authz
   gaps (new `[AllowAnonymous]`, missing policy checks, `DKNET-AUTH-001/002` tenant
   markers), unsafe deserialization, weak crypto, SSRF, path traversal, disabled cert
   validation, `IHttpClientFactory` bypass. Every new state-changing `POST` carries
   `.RequiredIdempotentKey()`. No new trust-boundary input left unvalidated.
4. Tests: each test fails if its subject is removed. Assertions pin exact values, never
   fragments; an absence assertion is paired with a presence one. Every added branch hit,
   per-branch not per-line. No setup or arrange block of ~10+ lines copied from the AT
   harness or another test file — merge it into the shared fixture at the second copy
   (Policy 02 statement 7a).
5. Standards: the at-risk rule-ids first, then reuse (`codegraph explore` — existing
   helper, extension, spec or base type), less code (`CLEAN-LESS-001..004`), SRP
   (`CLEAN-SRP-001..003`), DRY (`CLEAN-DRY-001/002`), layering (`DKNET-LAYER-001..004`,
   `DKNET-AGG-004`, `DKNET-REPO-004`). No new suppression (`#pragma warning disable`,
   `[SuppressMessage]`, `<NoWarn>`, `[ExcludeFromCodeCoverage]`) without a reason on its
   line or the one above; no analyzer, coverage or mutation setting lowered, no CI step
   removed/skipped/non-failing unless the ticket asks for it (Policy 04 statement 4a).
   Every new file under `Migrations/` checked against `EFC-013..018`. A new framework API
   or pattern checks the vendor's current official docs (Microsoft Learn, or Context7) and
   cites the page.
6. Comments and doc comments in the diff match the code beside them.

End with: `Brief re-read: <n> edge cases named, each a fact or "no fact, <reason>"`,
`Comments: <n> re-read, <n> wrong`,
`Standards: <skills opened> | rule-ids checked: <ids> | reuse: <symbol → reused X / none found> | SRP: largest class <n> lines, method <n> lines / complexity <n>, ctor <n> deps | DRY: <none / merged file:line> | docs: <n/a / url>`.
```

## What the gate does with it

pr-reviewer still reviews the whole PR on its own. Findings declared in LEFT OPEN are not
deductions. A missing `Pre-review` row is a `nit` (Policy 04 statement 4) — the gate
measures the point itself. A `Pre-review` row claiming a `blocking`/`important` finding
was fixed while the diff still holds it is `important` (pr-review-gate pass 5, Policy 01
statement 17).
