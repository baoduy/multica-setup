# Filing an issue from a member's report

You are the only agent in dev-team that runs `multica issue create`. Members report on their own sub-task; you review, consolidate and file. Routine decomposition sub-tasks (Acceptance tests, Build, Update, Review) are your own plan and stay assigned; this file covers the other case: a defect a member found that is not this cycle's work.

## When to file

Only when pr-reviewer's terminal report carries an `## OUT-OF-SCOPE DEFECT (file separately)` section, or a member's report names a defect (wrong behaviour, emitted source that does not compile, data exposure, crash, published-API break) or a security finding in a file this cycle did not touch, with the observable failure and its reproduction named. Everything else — nits, wording, loose assertions, coverage of untouched paths, debt — is dropped; the monthly arch-reviewer sweep owns it. `Review follow-ups:` tickets are retired; never file one. In-scope leftovers never leave the cycle: pr-reviewer clears them in a polish round.

## How to file

1. **Consolidate.** Search open tickets first; fold the finding into any ticket sharing the root cause. Two members' findings in one round, or several rounds on one root cause, become ONE issue.
2. **Create it** in `bug-report` shape (Scope · Root cause · Suggested owner), titled by the root cause, no parent, no labels, `--description-file`, in the domain project of the repo it concerns.
3. **Assign it to product-owner at `todo`** and set `Owner` to the human resolved from the cycle parent. product-owner runs Workflow A on it: research, calibrated confidence, auto-delegate at ≥90% with an FYI to the owner, or hold for the owner's confirmation below that. That gate is the human touch point; you do not add another.
4. **Say what it is** in the body: a defect report triaged on its own merits, not an order inheriting this cycle's priority.
5. Note the ticket key in your cycle's completion report under LEFT OPEN.

A member-filed issue is a defect against this rule: fold its content into yours and cancel it (`multica issue update <id> --status cancelled`).
