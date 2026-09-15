# bug-report — standard bug/defect issue format

The body contract for every SEPARATE bug or defect issue filed — a new backlog/todo ticket reporting something broken. Does NOT cover in-cycle fix sub-tasks (`Fix:`/`Fix (review):` — those follow the dispatching gate's own format and routing) or blockers (`blocker-report`). Goal: a reader with ZERO context can route the ticket to the right owner, who does the real diagnosis.

## Who reports, who files

- Any teammate who finds a bug reports it to THEIR leader first — a member never opens a bug issue directly.
- Only **leaders** and the **product owner** create bug issues.
- Before filing, the leader/product-owner CONSOLIDATES: search existing open bugs, de-duplicate, and fold the report into an existing issue when it shares a root cause. Open a new separate issue only when none already covers it.

## The three sections — always, in this order

### Scope (Git Repo, Module/Classes)
The Git repo plus the most precise code location you VERIFIED — module/class/file (`src/...:line`), package, endpoint (`METHOD /path`), or workflow file. `Location unknown` is acceptable; a guessed location is not — a wrong location routes the ticket to the wrong team and costs more than no location.

### Root cause
The mechanism that makes it fail — the underlying reason, never the symptom — plus the blast radius if left unfixed (one line). Open with `HYPOTHESIS:` whenever you have not proven it (the owning team does the real diagnosis — a cause stated as fact sends work to the wrong place with false confidence); a cause you verified at code level may be stated plainly.

### Suggested owner
One team/agent + one line of reasoning derived from Scope and Root cause. You suggest; the assignee/triager decides. Route by WHAT MUST CHANGE, never by where the symptom appeared.

## Rules

- One issue per distinct root cause; de-duplicate before filing (see "Who reports, who files").
- A consolidated multi-defect ticket opens with a summary table — `defect · scope · severity · root cause · suggested owner` — then one three-section block per defect.
- Plain descriptive title naming the ROOT CAUSE, not the symptom ("shared-state coupling breaks parallel OIDC tests", never "CI red").
- Write the body with `--description-file` pointing at a file inside your working directory.
- Your caller's skill or briefing may ADD sections and metadata on top (evidence, a proposed fix, fingerprints, title prefixes, links back to a cycle); it never removes or renames the three.
