# Policy 04 — Code, Spec & Architecture Review

| | |
|---|---|
| **Policy ID** | DRK-POL-04 |
| **Version** | 1.7 |
| **Status** | Active |
| **Owner** | pr-reviewer (code) · spec-reviewer (spec) · arch-reviewer (architecture sweeps) |
| **Applies to** | Every Workflow B spec before implementation, every squad/devops PR into `dev`, every scheduled architecture sweep |
| **Related skills** | [`pr-review-gate`](../../skills/pr-review-gate/SKILL.md) · [`spec-review-gate`](../../skills/spec-review-gate/SKILL.md) · [`architecture-review-sweep`](../../skills/architecture-review-sweep/SKILL.md) |
| **Enforced at** | the gates themselves (automated) |

> **Authority.** This policy is the source of truth for the two review gates and the
> architecture sweep. `pr-review-gate`, `spec-review-gate`, and `architecture-review-sweep`
> **implement** it — their scores, thresholds, and gate actions derive from it. Amend this
> policy first, then cascade — see [change control](00-policies-index.md#change-control). A
> skill that contradicts this policy is a defect in the skill.

## Gates at a glance

```
   SPEC gate (spec-reviewer)                       PR gate (pr-reviewer)
   ┌────────────────────────────┐                 ┌─────────────────────────────┐
   │ score ≥ 8.5, 0 blockers     │──APPROVED──▶    │ score ≥ 8.5, all merge      │──APPROVED──▶ gate
   │  → Workflow C delivery      │                 │  preconditions pass         │   MERGES into dev
   │ < 8.5 / blocker → REWORK    │                 │ ≥ 8.5 but precond fails     │
   │  (max 5 rounds → requester) │                 │  → APPROVAL DEFERRED (owner)│
   └────────────────────────────┘                 │ < 8.5 / blocking → REWORK   │
                                                    │  (max 3 rounds → owner)     │
                                                    └─────────────────────────────┘

   Rule: hard caps override arithmetic · every finding cites file:line, verified with
   CodeGraph · merge only the PR just gated · non-negotiable rules beat any requester shortcut.
```

## Purpose

Front-load quality at three checkpoints — spec approval, PR merge, and a recurring
architecture sweep — so a dev cycle is never spent implementing a defective spec, broken
code never reaches `dev`, and cross-cutting drift is caught before it compounds. Reviews are
evidence-based and calibrated, so approval is a privilege, never a default, and a human is a
bottleneck only when a review genuinely needs one.

## Scope

Every product-owner Workflow B spec (spec gate), every dev-team or devops PR opened against
`dev` (PR gate — including the `architecture-review-sweep` enforcement PR), and the monthly
(or on-demand, repo-scoped) sweep across all drunk stacks: .NET/DDD, Pulumi/TS IaC, Docker
images, Helm charts, Python MCP services.

## Policy statements

1. **Evidence before opinion.** Every finding cites `file:line` from the actual diff (PR) or the spec section (spec review) or the sweep's own read (architecture). A reviewer with no `file:line` for a claim has no opinion to state.
2. **CodeGraph-first, always before judging.** Before ruling on correctness, security, or duplication, run `codegraph explore` (index verified with `codegraph status` — never by the `.codegraph/` folder's existence, which a fresh checkout has without an index; `codegraph init` in the foreground when status shows no nodes) to walk callers/callees beyond the diff and verify every "reuse X / mirror Y" claim — grep/manual reading is the fallback for what CodeGraph cannot answer, never the default.
3. **Two operating modes, decided first, every wake.** A gate's OWN review sub-task (`[D<num>-n] Review:` for PR review, `[S<num>] Spec review:` for spec review) is **pipeline mode** — fully autonomous, ending in a gate action — whether it was assigned, promoted to `todo`, or re-armed by a mention on it, in whatever status it then holds (`todo`, `in_progress` or `blocked`). A mention on any OTHER ticket is **on-demand mode** — report-only: post the findings as a comment, take no GitHub write, no status flip, no ticket, unless the mentioning comment explicitly instructs otherwise.
4. **Score, then gate — never inflate.** Both gates score 1–10 per weighted category, then apply hard caps that override the arithmetic (a great average never outranks a blocking finding). Never inflate a score to reach a gate; when torn between two values, report the lower one and say why.
5. **PR gate weights and caps** (`references/scoring-rubric.md`): Correctness & logic 25% · Security 20% · Testing & coverage 20% · Maintainability & design 15% · Spec conformance 10% · Style & conventions 5% · AI-slop gate 5%. Hard caps: any `blocking` finding → 6.9 max · any `blocking (critical)` security finding (exploitable/secret/authz bypass) → 3.0 max · ≥ 2 open `important` findings anywhere → 8.4 max · spec-conformance ≤ 5 or no traceable spec link → 6.9 max · no tests for new/changed behavior → 6.5 max · an approved acceptance test modified or deleted after `at_sha` without a leader re-pin, or any `@new` scenario red, skipped or tagged out at HEAD → 6.9 max · no mutation evidence on touched classes carrying new logic ([Policy 02](02-testing-and-quality.md) statement 6a) → 7.9 max · CI failing → 6.9 max · coverage on changed lines below threshold (default 80%) → 7.9 max · docs/comment-only PR with green CI → 9.0 floor (caps beat the floor). Two exceptions to the CI cap, both stated in the report and neither spending a rework round: a Workflow D PR that changes the workflow producing the red check (statement 11b), and a red that is only a coverage-ratchet check while the diff's own bar is met — that lands APPROVAL DEFERRED for a human, never REWORK. **APPROVED** at ≥ 8.5 with every auto-merge precondition passing; **APPROVAL DEFERRED** at ≥ 8.5 with a failed precondition; **REWORK** below 8.5 or on any blocking finding (max 3 rounds, then escalate).
6. **Spec gate weights** (`spec-review-gate`): Requirement coverage & traceability 30% · Gherkin quality 25% · Business clarity & problem framing 20% · Completeness & unambiguity 15% · Security Considerations 10%. Deduction math mirrors the PR gate (per-dimension start 10; `blocker` −4, `major` −2, `minor` −0.5) with caps: any `blocker` → 6.9 max · ≥ 2 open `major` findings → 8.4 max. **APPROVED** at ≥ 8.5 with zero `blocker` findings → the product-owner is released to delegate (Workflow C); **REWORK** below 8.5 or any blocker (max 5 rounds, then **MANUAL HANDOFF** — the sub-task is reassigned to the requester, never a 6th rework round, and never taken back while a human holds it).
7. **The spec gate verifies claims against real code, never the design.** Every `file:line` citation and every Constraint claiming a property the code holds today is spot-checked with CodeGraph; a citation to code that does not exist, or a claimed invariant the code does not hold, is a `blocker`. Whether the change reuses the right helper or mirrors the right pattern is dev-leader's call at decomposition and pr-reviewer's at the merge gate — the spec gate never re-opens that.
8. **PR-state guard runs before anything else, in pipeline mode.** `MERGED` → the gate is already satisfied: post one plain comment noting no review was performed, pin `Gate verdict` = ALREADY_MERGED, flip the sub-task `done`, and end — no collection, no analysis, no GitHub writes. `CLOSED` without merge → the blocked path. Only an `OPEN` PR is reviewed.
9. **pr-reviewer merges the PR it just approved — nothing else.** On APPROVED, the gate itself runs `gh pr merge` on the PR scored in this run and verifies the state is `MERGED`. It never enables auto-merge, never force-merges, never pushes commits, and never merges any PR it did not just gate. A helm-chart PR is never auto-merged by this gate to begin with — merging a chart is a deploy, which sits outside this policy's automated path.
10. **REWORK is routed by the squad leader, once per round, consolidated, without tickets.** A PR REWORK is ONE consolidated findings comment on pr-reviewer's OWN Review sub-task, grouped per implementer (dev-backend for code/test/coverage, docs-writer for docs, dev-leader for git/PR mechanics per `leader-gitops`) — never one comment per finding, never a fix sub-issue — citing `file:line` per finding with an objectively verifiable acceptance criterion, ending with dev-leader's mention. dev-leader flips each implementer's sub-task `in_progress`, posts the findings pointer there with that implementer's mention, and when the implementer's `done` comes back re-arms the Review sub-task (`in_progress` + pr-reviewer's mention). Members never write on each other's tickets. A spec REWORK is a verdict comment only — the spec gate never creates sub-issues or delegates; the product-owner revises and re-arms the gate sub-task itself (`in_progress --no-start` + spec-reviewer's mention, both parts). Flipping that sub-task to `todo` re-arms nothing: it has already run, so only the mention wakes the next round.
11. **Manual handoff when the gate cannot merge or cannot conclude.** A PR that is APPROVED but has a failed auto-merge precondition, has exhausted its 3 rework rounds, or hit a failed merge command is reassigned to the resolved owner ([Policy 10](10-ticket-ownership-and-owner-pickup.md); member mention, `todo`) for manual review and merge — never a retry with more force. A spec that exhausts 5 rework rounds is reassigned on the same terms. In both cases the review sub-task is never taken back while a human holds it.
11b. **A re-review always ends in a verdict.** The 3-round cap limits REWORK verdicts; a fix returning after round 3 is scored and ends APPROVED (merged), DEFERRED or ESCALATED — never a provisional comment with the gate left `blocked`. When a round's findings went to several implementers the gate re-reviews once, after the last one reports. **Workflow D exception to the CI precondition:** a PR that changes the workflow producing the red check merges on score with `CI: red by design` stated; the red is the behaviour under change. **CI first:** tests and coverage are read from CI (`checks_conclusion`, artifacts) when the repo has CI; local re-runs only when CI is absent, coverage is unknown, or a reported row is doubted.
11a. **Gate state is pinned on custom properties.** Both gates record `Gate verdict` (select: APPROVED, REWORK, POLISH, DEFERRED, ESCALATED, MERGE_FAILED, ALREADY_MERGED), `Gate round` (number of REWORK rounds spent; POLISH does not count) and `Gate score` on their own review sub-task after every verdict. Issue metadata is not used.
12. **Findings become Multica sub-issues, never GitHub issues.** All fix work generated by a review — PR or spec — is tracked in Multica; the gates do not open GitHub issues.
13. **Scope decides where a finding goes; impact decides its severity.** A finding is **in-scope** when its `file:line` is in a file the cycle's diff touched, in a path the diff newly reaches, or a missing fact for behaviour the diff changed — *who introduced it is irrelevant*. In-scope findings never leave the cycle and never become tickets: `blocking`/`important` take a rework round, `nit`-only leftovers take one polish round (same mechanics, does not spend the rework budget, at most one per cycle), and the PR is not merged until they are closed. Out-of-scope findings (a file the diff never touched) are recorded with `file:line`, never move the score, and are **dropped** unless they clear the worth-fixing bar — a defect (wrong behaviour, emitted source that does not compile, data exposure, crash, published-API break) or a security finding, with the observable failure AND its reproduction named — in which case the squad leader files ONE ordinary defect ticket (never `Review follow-ups:`), unassigned, `Owner` set, folded into any open ticket sharing the root cause. **Only a squad leader files issues; a gate is a member and files none.** Severity never softens because a defect is pre-existing: "not introduced by this PR" decides whose cycle fixes it, not whether it is a defect. Remaining debt is the monthly sweep's, not filed ad hoc.
14. **Self-authored PRs fall back gracefully.** GitHub rejects a review vote from the PR's own author; the gate attempts the vote, falls back to a plain comment on rejection, and notes the skipped vote — the Multica report is the audit record and a rejected vote never blocks an otherwise-APPROVED merge.
15. **Include at least one `praise` finding when deserved** — on both gates, review is calibration, not attrition.
16. **Reviewers do not design.** The spec gate scores what is reused/modified/new only — never how to build it. The PR gate does not re-open a spec decision the spec gate already settled.
17. **Architecture sweeps run on a schedule, per stack.** `arch-reviewer` applies each repo's own stack-specific standard skill (`dknet-ddd-conventions` + `dotnet10-efcore10-standards` for .NET, `pulumi-azure-iac-standards` for Pulumi/TS, `docker-image-standards`, `helm-k8s-conventions`, `python-mcp-standards`), reading that repo's `CLAUDE.md`/`AGENTS.md` first since solution-local conventions override the generic rules.
18. **Dedupe before filing is mandatory, not optional.** Every sweep run checks already-filed issues by title, then confirms survivors via the `Arch fingerprint` custom property (namespaced per repo) before filing anything new — this is the single step that keeps the sweep useful instead of spam.
19. **File a small, high-value set for human triage.** At most 10 new issues per repo per run, highest severity first, filed at `backlog` assigned to the human triager (the workspace owner, resolved at runtime) in that repo's own domain project — never to `dev-team`, `product-owner`, or the reviewer itself. Everything above the cap is recorded in the run report body, never silently dropped.
20. **Mechanically-checkable rules convert to permanent enforcement.** Every rule the sweep can check gets tiered: Tier 1 (clean today) → an architecture/lint/unit test added now; Tier 2 (existing violations) → the same test with an explicit, shrink-only allow-list of today's offenders; Tier 3 (judgment call) → backlog issue only, never a faked test. A Tier-1 test that fails on today's code is a defect in the enforcement PR itself. The enforcement PR is test-only or config-only — it never touches production code, and always targets `dev` with both `--head` and `--base` explicit.
21. **Non-negotiable rules override requester shortcuts.** No mentioning comment, cycle ticket, or requester instruction may waive a hard cap, a merge precondition, the CodeGraph-first requirement, or the round caps — on-demand mode's "report-only unless explicitly instructed" applies only to whether a gate *acts*, never to whether it applies the rubric honestly.

## Roles & responsibilities

- **pr-reviewer** — owns the PR gate end-to-end: collect, analyze, score, gate, merge on APPROVED, post consolidated rework findings on its own Review sub-task for dev-leader to route on REWORK, hand off to the workspace owner when it cannot conclude.
- **spec-reviewer** — owns the spec gate: verifies the spec against real code, scores it, gates it, and hands off to the requester after 5 rounds. Never edits the spec, never touches PRs.
- **arch-reviewer** — owns the monthly (or on-demand, repo-scoped) sweep across all stacks: analyze, rank, dedupe, file ≤10 issues per repo for the workspace owner to triage, convert enforceable rules into tests, report what was and wasn't covered.
- **dev-backend** — receives the PR-gate findings from dev-leader on its own Build sub-task, fixes with a reproduction test per finding, reports there and flips `done`; dev-leader re-arms the gate.
- **dev-leader** — receives git/PR-mechanics findings and owns the cycle's git-flow.
- **product-owner** — receives spec REWORK verdicts to revise, and triages PR-gate follow-up tickets in place.
- **Workspace owner** — the terminal human for a manual handoff the gate could not resolve itself.

## Definition of Done / compliance

- **Spec:** score ≥ 8.5, zero blockers, all six `sdlc-spec-template` sections present (§3a carries the field and endpoint contract), §4 Scope complete, grounded against real code.
- **PR:** score ≥ 8.5, zero blocking findings, all auto-merge preconditions pass, merged into `dev` by the gate itself.
- **Sweep:** every in-scope repo's production source reviewed against its own stack skill, dedupe run before filing, ≤10 issues filed per repo, enforcement PR green locally before push, report states what was and wasn't covered.

## Enforcement

The gates are the enforcement, fully autonomous in pipeline mode. A verdict a gate cannot act on itself (deferred precondition, exhausted rounds, failed merge, exhausted spec rounds) goes to a human via reassignment at `todo`, never a bare mention. On-demand mode is report-only: no GitHub writes, no tickets, unless the mentioning comment explicitly says so.

## Exceptions & waivers

- Round caps are fixed by policy, not by request: PR review 3 rounds, spec review 5 rounds — then the human takes over via a reassigned sub-task. No requester shortcut extends them.
- Self-authored PRs: a rejected vote never blocks an otherwise-APPROVED merge; the Multica report stands as the audit record.
- Coverage genuinely unknown (no CI artifact, not cheaply runnable) is not a hard cap — it fails the auto-merge precondition instead, landing on APPROVAL DEFERRED for a human decision, never a silent pass.

## References

- [`pr-review-gate`](../../skills/pr-review-gate/SKILL.md) — four-phase analysis, scoring rubric, gate actions, merge preconditions, follow-up consolidation.
- [`spec-review-gate`](../../skills/spec-review-gate/SKILL.md) — weighted rubric, format gates, round bookkeeping, gate mechanics.
- [`architecture-review-sweep`](../../skills/architecture-review-sweep/SKILL.md) — shard/rank/dedupe/file/enforce workflow, per-stack routing.
- `agents/pr-reviewer.md`, `agents/spec-reviewer.md`, `agents/arch-reviewer.md` — role identity, hard behavioral limits, status discipline.
- Delivery context: [Policy 05](05-sdlc-delivery-lifecycle.md). Spec contract: [Policy 06](06-requirements-and-spec.md).
