# Pre-review — a mini PR gate before you report done

Policy 01 statement 15. Run it on every `build`, `bug-build`, `build-ui` and `build-excluded` sub-task, and on a Build's rework fix, once your code is pushed and the mechanical checks (1–3, 6, 7, 9) are green. It exists to remove the findings the PR gate would raise. It does not repeat the gate: no score, no `report.md`, no GitHub calls, one pass.

## How

1. Start ONE subagent with fresh context: the Agent tool, `general-purpose`. Give it the prompt below with the placeholders filled in. Your own context has seen the code being written, and a fresh reader catches what you no longer see. No subagent tool in this run → run the passes yourself and say so in the row.
2. Fix every `blocking` and `important` finding inside §3. Re-run only the tests and checks the fix touches, then push.
3. Do not start a second pre-review. A finding you cannot fix inside §3 (it needs §4 code, or the brief is wrong) goes in LEFT OPEN with `file:line`. A `nit` is fixed only when it costs one line.
4. Report one row: `Pre-review | <b> blocking, <i> important, <n> nit found · fixed <n> · LEFT OPEN <n> · subagent | inline (<why>)`. The subagent's answers also fill the `Brief re-read`, `Comments` and `Standards` rows (checks 4, 5, 8). You do not run those checks a second time.

## Prompt (fill in, pass verbatim)

```
You review a diff before its PR exists. Read-only: never edit, commit or push.
Repo checkout: <path>. Diff: `git diff origin/dev...HEAD` (a rework fix: `git diff <SHA before the fix>..HEAD` only, plus the findings comment <Review key + timestamp> — check each finding is closed and the fix broke nothing nearby; do not re-review the rest of the PR). Brief: <sub-task key> (`multica issue get <key> --output json`, field description). Spec scenarios: <spec key> §5.
Stack skill(s): <from the brief's Standards row>. At-risk rule-ids: <from the brief>.

Report findings only, one line each: `[blocking|important|nit] file:line — what is wrong — what fixes it`.
blocking = wrong behaviour, does not compile, data or secret exposure, a published API break, a contradiction of the brief's §5 contract or §3b placement.
important = a missing or weak test, a broken standards rule-id, an unhandled input in the brief's §6a, a stale comment.
nit = anything else worth one line. Never report style that the analyzers or the linter already enforce.
Proof: a blocking or important correctness or security finding names the input or state that triggers it, the wrong outcome, and why existing guards do not stop it; a rule finding cites its rule. Neither → report it as nit or drop it. No findings is a valid answer; never add one to look thorough.

Passes, in this order. Use `codegraph explore` for callers and existing helpers, not grep.
1. Brief: every §3 row is done, §6 rules hold, every §6a input row has its proof, every §9 default is applied. Nothing changed outside §3, and nothing in §4 changed.
2. Correctness: each changed guard, default, mapping and external call is checked against the empty, null, unknown and boundary values and every enum member. Each exception the changed call can raise is handled. Callers of every changed public symbol still hold. No silent failure: no empty or log-only catch that carries on, no empty list, null or default returned from a failed call, no rethrow that drops the original exception (`throw ex;`).
3. Security: no secret or PII in logs, outputs or state. Pulumi: every key-, secret-, password- or token-shaped value that reaches a Resource argument is wrapped in `pulumi.secret()` (`PULUMI-SEC-009`); grep the diff for them. No new trust-boundary input is left unvalidated.
4. Tests: each test fails if its subject is removed. Assertions pin exact values, never fragments. A destructive operation asserts the state before and after. Every added branch is hit. No setup block of 10 or more lines is copied from another test file (Policy 01 statement 7a).
5. Standards: the at-risk rule-ids first, then reuse (an existing helper does the job), less code, SRP sizes, layering direction. No new suppression (`#pragma warning disable`, `NoWarn`, `eslint-disable`, `@ts-ignore`, `# noqa`, `[ExcludeFromCodeCoverage]` and the like) without a reason on its line or the line above. No analyzer, lint, coverage or mutation setting lowered and no CI step removed, skipped or made non-failing unless the brief asks for it (blocking, Policy 04 statement 5a). Every new file under `Migrations/` is checked against `EFC-013..018`.
6. Comments and doc comments in the diff match the code beside them.

End with three lines: `Brief re-read: <n> edge cases named, each a fact or "no fact, <reason>">`, `Comments: <n> re-read, <n> wrong`, `Standards: rule-ids checked <ids> · reuse <result> · SRP <largest class/method/ctor> · DRY <result>`.
```

## What the gate does with it

pr-reviewer still reviews the whole PR on its own. Findings you declared in LEFT OPEN are not deductions. A `Pre-review` row that says `blocking` or `important` were fixed while the diff still holds them is `important` at the gate.
