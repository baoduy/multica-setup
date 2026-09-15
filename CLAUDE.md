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
