# CLAUDE.md — multica/export

Rules for editing workspace bundles here (in addition to `../CLAUDE.md`:
analyse first, local bundle first, ask before pushing live).

## Scoring rubrics (review gates)

When creating or editing any scoring rubric (pr-review-gate, spec-review-gate,
or a future gate), enforce all of these — rationale in `README.md` here:

- Deduction math is explicit and shared: start each category/dimension at 10;
  blocker/blocking −4, major/important −2, minor/nit −0.5 (max −1.5 from
  minors); floor 1; weighted sum; then hard caps; one decimal.
- Hard caps exist for finding COUNTS, not just weighted arithmetic:
  ≥2 open major/important findings anywhere → cap below the approve bar.
- "Wrong thing" caps independently of "built right": spec-conformance failure
  or missing spec link → cap 6.9, regardless of code quality.
- Caps beat floors; say so in the rubric.
- Never reference a severity the severity list doesn't define.
- Calibration anchors (9.5 / 8.5 / 8.0 / 6.0 / 3.0 style) must agree with the
  deduction math — verify with arithmetic, not vibes.
- Approve bar is 8.5 on BOTH spec and PR gates. A gate replacing human approval
  is never softer than gates downstream of it.
- Changing any bar/cap/weight: grep the entire bundle for the old value —
  policies 04 and 06, sdlc-flow-delivery-pipeline, and both gate skills quote
  these numbers.

## Policy is the source of truth

`docs/policies/` in each bundle governs the flow; skills, agents, squads and
the workspace context implement it. Two rules follow from that:

- **A change that contradicts a policy needs the owner's approval first.**
  Before editing, check the policies the change touches. If the request
  conflicts with one, stop and say which policy and which statement, what the
  change would make it say, and wait for an explicit yes — never resolve the
  conflict yourself, in either direction. A change that merely adds to a
  policy still amends it: amend the policy first, then cascade.
- **Never leave the setup out of sync with the policy.** Every accepted change
  lands everywhere it is quoted in the same pass: the policy statement, the
  skills, agents, squads and workspace context that restate it, the changelog
  (drunk: `docs/policies/CHANGELOG.md`; mx: `CHANGELOG.md`), and the
  live workspace. Grep the whole bundle for the old wording or value before
  declaring it done, and after pushing live, read each updated resource back
  and diff it against the local file. Live and bundle drift is a defect, not a
  pending task.

<!-- rtk-instructions v2 -->
# Command output

Command output here is condensed to save tokens, keeping every signal and
dropping costly noise. Treat it as the complete result: run commands
normally, and batch related commands into one call to avoid extra turns.
Truncated results state their recovery path in their own output. Re-run a
command as `rtk proxy <cmd>` only when its result is unusable: empty when
output was clearly expected, contradicting its exit code, or garbled.
<!-- /rtk-instructions -->