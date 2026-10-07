# CI red — who caused it

- **CI red.** First re-run the failed jobs once (`references/github.md`) and wait for them the same way. Still red → decide who caused it:
  - **Not caused by this PR** — you can show the same check red on `dev`'s head, the failure in a project or test the diff does not touch and does not reach (CodeGraph), or an infrastructure error (runner, checkout, network, cancelled run, a restore advisory on a package the diff does not change). No CI cap; merge on score; state `CI: red, not caused by this PR (<check>, <evidence>)`.
  - **Coverage ratchet** — every red check is a coverage-ratchet check and the diff's own bar is met: no cap, no round spent, merge on score (rubric, coverage-ratchet exception).
  - **Workflow fix** — the PR changes the workflow file(s) that produce the red check (a Workflow D CI/CD PR): state `CI: red by design (<check>)` and merge on score plus devops' `gh run` evidence on the branch.
  - **Caused by this PR** — anything else: the rubric's CI cap applies and the verdict is REWORK. No evidence either way counts as caused.
