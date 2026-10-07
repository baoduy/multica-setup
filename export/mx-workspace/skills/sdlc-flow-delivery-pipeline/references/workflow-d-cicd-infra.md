# CI/CD & infra flow (Workflow D)

## CI/CD & infra flow (Workflow D)

Pipelines, build/release automation, and helm charts are `devops` work. They never enter dev-team or qc-team flow and never open a spec-review gate. They DO open a PR-review gate whenever `devops` produces a standalone PR — see "PR-review gate for devops PRs" below.

**Two doors, and only one of them is product-team's:**

| Door | When | Owner |
|---|---|---|
| **direct** | requester files a pipeline/helm ticket straight to `devops` | `devops`, end to end. product-team stays out entirely — never adopts, re-parents, or wraps such a ticket. |
| **delegated** | a FEATURE needs a pipeline or chart change, surfaced by spec or by a squad | product-team creates `[P<num>-1b] CI/CD change` (devops, `todo`) + `[P<num>-1c] Review CI/CD PR` (pr-reviewer, `backlog`) as phases of that feature |

A squad that discovers pipeline/helm work mid-cycle never creates sub-task itself: it reports on its phase ticket, posts its handoff line on the main ticket, and product-team routes it.

### PR-review gate for devops PRs

| devops landed it as | pr-reviewer's action on APPROVED |
|---|---|
| commit on a named feature branch (app repo) | none — it is reviewed inside squad's cycle PR |
| PR → `dev` (app repo, standalone) | score, vote, **and merge**, exactly as for a squad PR |
| PR → `main` (either helm repo) | score and vote, **never merge** — merging a chart PR IS deploy, so a human merges it via `[P<num>-2] Merge helm PR` |

```
👤 asks for pipeline / helm work
 ├─ direct door: 👤 assigns 🔧 devops straight away (supported, not an error — 🦊 stays out)
 └─ via 🦊: intake (labels main+cicd) → classify Workflow D
       ├─ D1 "analyse and tell me"  → 🦊 report (file:line) + STOP. No sub-tasks, no delegation
       │                              at any confidence. 👤 decides what happens next.
       └─ D2 "make the change"      → 🦊 creates [P#-1] CI/CD change (devops, todo) only
 → 🔧 devops does work, landing it by REPO CLASS:
       app repo   → task names a feature branch? commit to THAT branch (squad leader owns PR).
                    otherwise → chore/<issue> branch, open PR to `dev`, report link. Never
                    commits directly to `dev` or `main`.
       helm repo  → branch chore/<issue>, push, open PR to `main`, STOP. Never merges.
 → 🦊 verifies (commit on feature branch | OPEN PR based on dev | OPEN PR based on main)
 → helm only: 🦊 promotes [P#-2] Merge helm PR (deploy) → 👤 reviews and merges = deploy decision
 → 🦊 flips main ticket done + plain summary
```

No `[P#-2a]` release, no `[P#-2b]` argoCD ticket, no `[P#-3]` BDD phase in this flow.
