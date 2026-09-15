# Policy 07 — Bug & Defect Management

| | |
|---|---|
| **Policy ID** | MX-POL-07 |
| **Version** | 1.0 |
| **Status** | Active |
| **Owner** | product-owner (triage & root cause) · qc-team (defect discovery) |
| **Applies to** | Every reported bug, discovered defect, and escalation |
| **Related skills** | [`bug-report`](../../skills/bug-report/SKILL.md) · [`blocker-report`](../../skills/blocker-report/SKILL.md) · [`test-driven-development`](../../skills/test-driven-development/SKILL.md) |
| **Enforced at** | product-owner (Workflow A) · qc-team consolidation · squad fix cycles |

> **Authority.** This policy is the source of truth for defect handling. `bug-report` and
> `blocker-report` **implement** its ticket and escalation shapes. Amend this policy first,
> then cascade — see [change control](00-policies-index.md#change-control).

## Bug flow at a glance

```
   👤 bug / 🐝 qc-discovered defect ─▶ 🦊 research ─▶ ROOT-CAUSE report + CONFIDENCE (0–100%)
                                                              │
                    ┌─────────────────────────────┬──────────┴───────────────┐
                    ▼                              ▼                          ▼
             pure question             confidence ≥ 90%              confidence < 90%
             (no change)               AUTO-DELEGATE Workflow C      👤 requester confirms
             → report = done           (FYI: "reply to halt")        before any delegation
                                              │
                                              ▼
                    Prove-It: FAILING repro test ─▶ fix at the SHARED layer ─▶ passes ─▶ full suite

   Ticket = Scope (Git Repo, Module/Classes) · Root cause (HYPOTHESIS: unless proven) · Suggested owner
   Escalate after 2 failed attempts on the same root cause → ## BLOCKER + ## OPTIONS, deliver by assignment.
```

## Purpose

Route defects to the right team the first time and fix them at the root, not the symptom.
A bug ticket must let a zero-context reader pick the handling team from the ticket alone,
and no fix ships without a test that proves the bug is gone.

## Scope

Standalone bug/defect tickets, qc-discovered defects, and blocker escalations. In-cycle
fix sub-tasks (`Fix:` / `Fix (review):`) follow the dispatching gate's own format, not this
policy's report shape.

## Policy statements

1. **Bug flow (Workflow A):** intake → research → a root-cause report comment (evidence, repro, fix direction targeting the layer all callers route through) with a **calibrated confidence (0–100%)** that this is a genuine platform defect with the identified root cause.
2. **Confidence gates delegation:**
   - **≥ 90%** (confirmed) → auto-delegate Workflow C immediately, FYI to the requester ("fix delegated — reply to halt").
   - **< 90%** (possibly by-design/config/user error) → the requester reviews and explicitly confirms before any delegation.
   - **Pure question, no change wanted** → the report is the deliverable; END.
3. **Fix at the root, once.** Target the layer all callers route through — one guard in a shared function beats a guard in every caller and leaves no sibling caller broken.
4. **Prove-It before fixing.** Reproduce the bug with a failing test first; implement the fix; the test passes; run the full suite for regressions (see [Policy 02](02-testing-and-quality.md)).
5. **Bug ticket = three sections, in order** (per [`bug-report`](../../skills/bug-report/SKILL.md)): **Scope (Git Repo, Module/Classes)** (verified location — git repo + module/class, never guessed), **Root cause** (the mechanism, never the symptom, + blast radius; `HYPOTHESIS:` unless proven), **Suggested owner** (one team + one line, routed by *what must change*, never by where the symptom appeared). Evidence and a proposed fix are the owner's to produce during diagnosis, not the reporter's.
6. **One issue per distinct root cause; de-duplicate before filing.** A QC cycle files **ONE consolidated, deduped** defect ticket with a summary table (`defect · scope · severity · root cause · suggested owner`) then one three-section block per defect.
7. **Title names the root cause, not the symptom** ("shared-state coupling breaks parallel OIDC tests", never "CI red").
8. **Escalate as an action, not a status.** After **2 failed attempts on the same root cause** (or anything outside squad control — a product decision, missing credentials, a broken environment), post ONE standalone `## BLOCKER` + `## OPTIONS` comment (per [`blocker-report`](../../skills/blocker-report/SKILL.md)) and deliver it: agent mention for an agent hop, **ticket reassignment at `todo`** for a human hop. Never take a ticket back while a human holds it.
9. **Report completion in the fixed shape** — `## RESULT` / `## EVIDENCE` (every claim has an evidence row; a skipped check is a row saying so) / `## LEFT OPEN`, one comment per event.

## Best practices for .NET developers

- State a fix as `HYPOTHESIS:` unless you verified it at code level — a hypothesis stated as fact sends work to the wrong team with false confidence.
- Diagnose with CodeGraph: `codegraph explore`/`callers` to find every call site of the function you're about to touch before choosing where the fix lands.
- A reproduction test is the regression guard — it stays in the suite after the fix.

## Definition of Done / compliance

- Root cause identified (not the symptom) with evidence and a confidence figure.
- Reproduction test failed before the fix and passes after; full suite green.
- Fix lands at the shared layer; no sibling caller left broken.
- Ticket routes correctly on first read (Where/Scope/Suggested owner coherent).

## Enforcement

`product-owner` runs Workflow A and applies the confidence gate; qc-team consolidates and
routes discovered defects; squad fix cycles cap at 2 attempts per root cause before
escalation. The PR gate ([Policy 04](04-code-and-spec-review.md)) verifies the fix and its test.

## Exceptions & waivers

- A BDD-integration waiver already on the ticket is honoured at once; auto-delegation does not wait for a BDD answer — the full flow is created, the question rides along in the FYI, and a later "no BDD" reply cancels `[P#-2b]` and `[P#-3]` (making `[P#-2a]` terminal) without touching `[P#-1]`'s in-repo test obligation.
- Bugs need a spec only if the requester asks (then the spec gate applies).
- `[P#-3]` for a bug is typically a run-only re-verification cycle.

## References

- [`bug-report`](../../skills/bug-report/SKILL.md) — the three-section body contract + consolidated-ticket format.
- [`blocker-report`](../../skills/blocker-report/SKILL.md) — completion and blocker comment shapes.
- Bug flow (Workflow A) in [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md); Prove-It in [`test-driven-development`](../../skills/test-driven-development/SKILL.md).
