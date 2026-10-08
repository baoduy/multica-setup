# drunk setup improvement loop and live sync

How the drunk workspace improves its own agents, skills and policies from
recorded mistakes, and how a reviewed change reaches the live workspace.
The rule behind it is drunk Policy 03 statement 11
(`export/drunk-workspace/docs/policies/03-source-control-branching.md`); the
charter is in Policy 09 (**setup-steward**).

<a href="../.archify/workflow-setup-improvement-loop/setup-improvement-loop.html">
  <img alt="multica-setup improvement loop (drunk-workspace)" src="../output/improvement-loop-presentation/improvement-loop-animation.gif">
</a>

Interactive diagram: `.archify/workflow-setup-improvement-loop/setup-improvement-loop.html`
(open it in a browser).

## The flow at a glance

```
 Monitor        Improve              Develop            Release              Sync to live
 ───────        ───────              ───────            ───────              ────────────
 agent runs ─▶  🔁 Weekly Setup  ─▶  setup-steward  ─▶  dev→main PR    ─▶   GitHub Action
 record gate    Retro (Mon 09:00     commits the fix    owner reviews        (push to main,
 verdicts,      SGT) files ≤3 fix    on dev, adds an    and merges           export/drunk-workspace/**)
 rounds and     issues in            entry to the one                         │ webhook
 failed runs    drunk-setup          open PR, issue                           ▼
                                     goes blocked                       🔄 Drunk Live Sync
                                                                        claude_ultra runs
                                                                        scripts/drunk-live-sync.py
                                                                          │
                          fix issues set done, tag live/drunk moves ◀─────┘
```

`main` is what the live drunk workspace runs. The tag `live/drunk` marks the
`main` commit that live matches. Nothing reaches live without the owner
merging `main`.

<a href="../.archify/workflow-setup-gitflow/setup-gitflow.html">
  <img alt="multica-setup improvement loop git flow (drunk-workspace)" src="../output/gitflow-presentation/gitflow-archify-animation.gif">
</a>

Interactive diagram: `.archify/workflow-setup-gitflow/setup-gitflow.html`.

## Parts

| Part | Where | What it does |
|---|---|---|
| `drunk-setup` project | live workspace | Holds the retro, fix and sync issues. Led by the owner; only `baoduy/multica-setup` is attached, so the delivery pipeline never routes its issues. |
| `setup-steward` agent | `export/drunk-workspace/agents/setup-steward.*` | Runs the retro and delivers fixes. Claude Opus, `xhigh`, one run at a time (all fixes commit to `dev`). |
| `🔁 Weekly Setup Retro` autopilot | `autopilots/weekly-setup-retro.*` | Mondays 09:00 Asia/Singapore. Its description is the retro procedure. |
| `🔄 Drunk Live Sync` autopilot | `autopilots/drunk-live-sync.*` | Webhook trigger. Assigns `claude_ultra` to run the sync script and report. |
| Sync script | `scripts/drunk-live-sync.py` | Pushes the changed resources, reads them back, moves the tag. |
| Health script | `scripts/setup-health.py` | The retro's six lens counts. Read-only. |
| GitHub Action | `.github/workflows/drunk-live-sync.yml` | On a push to `main` touching `export/drunk-workspace/**`, POSTs to the webhook. |
| Webhook secret | repo secret `MULTICA_DRUNK_SYNC_WEBHOOK` | The autopilot's webhook URL on `https://multica-api.st24.live`. |
| Tag `live/drunk` | GitHub | The `main` commit live matches. Only the sync script moves it. |

## 1. Monitor: what counts as a mistake

The workspace already records them. The retro reads the last 7 days of:

- review sub-tasks: the `Gate verdict`, `Gate round` and `Gate score`
  properties, and the rule ids and severities named in rework comments
  (the gate-digest script from the monthly insights autopilot, run with
  `DAYS=7`);
- failed agent tasks, grouped by agent and error;
- `Run recovery needs attention` escalations from run-medic.

## 2. Improve: the weekly retro

`setup-steward` files an issue only when the same cause shows up at least
twice and a bundle file should have prevented it. At most 3 issues a week,
deduped against open ones, each with:

- **Problem**: one sentence.
- **Evidence**: issue keys, counts, rule ids.
- **Where**: the bundle file and section to change.
- **Watch**: the metric that should move if the fix works.

One-offs, transient infrastructure errors (run-medic's job) and anything
that would change a gate bar, cap, weight or deduction go into the retro's
report for the owner instead of an issue. The retro also checks whether
earlier fixes moved their Watch metric and asks about reverting one that did
not move in 3 weeks.

Every retro also reports the setup's health. `scripts/setup-health.py`
prints one count per lens, and the report compares each with last week's:

| Lens | Counts |
|---|---|
| 1 Duplication | 10-word runs shared with the Workspace Context, identical agent instructions, dangling `references/` paths |
| 2 Wording | agents over the 24,000-byte always-loaded budget, lines over 600 characters, ticket keys in always-loaded text |
| 3 Structure | SKILL.md over 10 KB with no `references/`, skills with no frontmatter |
| 4 Practices | agents with no Goal line or Never list, skill descriptions with no "Use when", bundle descriptions that differ from live |
| 5 Built-ins | Multica releases since the last release review |
| 6 Performance | per gate: first-pass %, mean rounds, escalations (from the gate digest) |

Lens findings are report only: they file no issue (Policy 09, setup-steward
charter). The owner picks what to act on. The baseline is
[`drunk-setup-audit-2026-10-07.md`](drunk-setup-audit-2026-10-07.md).
`setup-steward` never edits the script; owner sessions maintain it
(`python3 scripts/setup-health.py --selftest` checks its parsers).

## 3. Develop: a fix

On each fix issue `setup-steward`:

1. clones the repo at `dev` and follows the root `CLAUDE.md` (policy first,
   cascade everywhere a rule is quoted, one CHANGELOG entry);
2. edits `export/drunk-workspace/` only;
3. commits `drunk: <change> [DRK-n]` onto fresh `origin/dev` by refspec and
   proves the push with `git ls-remote`;
4. opens the `dev`→`main` PR, or adds a bullet to the open one:
   `[DRK-n] <change> — evidence: … — watch: …`;
5. comments the SHA, PR and metric on the issue and sets it `blocked`
   (waiting on the owner).

Owner sessions commit to `dev` too; their commits ride the same PR.

## 4. Release: the owner's review

The owner reviews the PR and merges it. The merge is the approval to go
live.

- **Prefer a merge commit.** A squash merge leaves `dev` diverged from `main`,
  so the next PR shows old commits again. After a squash, merge `main` back
  into `dev` (`git merge origin/main` on `dev`; no content changes). Fix issues
  are closed either way, because the sync reads issue keys from the full
  commit messages.
- **Rework:** comment on the fix issue. `setup-steward` adds a commit on `dev`.
- **Reject:** say so on the fix issue. `setup-steward` reverts its commit on
  `dev`, removes its PR entry and cancels the issue.

## 5. Sync to live

The Action calls the webhook, the autopilot creates a `Drunk Live Sync (date)`
issue, and `claude_ultra` runs the script in a fresh clone of `main`. The
script holds a lock, so overlapping runs wait and then find nothing to do.

It diffs `live/drunk..origin/main` under `export/drunk-workspace/` and handles
each changed file:

| File | Result |
|---|---|
| agent instructions and description, squad instructions and description, project and autopilot descriptions, the Workspace Context | pushed byte-exact, read back |
| skill `SKILL.md`, skill files (added, changed, deleted), skill `config.json` | pushed, read back |
| agent `.json`: `model`, `thinking_level`, `max_concurrent_tasks`, `skill_names` | pushed, read back |
| any agent, project or autopilot `.json` that live already matches | `already_live`: counts as synced |
| `docs/`, `README.md`, `manifest.json` | ignored (not live) |
| anything else that differs from live: new or deleted resources, avatars, other agent keys, triggers, labels, properties | `unsupported`: a manual step |

Outcomes:

- **`synced`** (exit 0): every change is live. The tag moves, fix issues
  named `[DRK-n]` in the merged commits go `done`, the sync issue goes `done`.
- **`up-to-date`** (exit 0): nothing to do; the sync issue goes `done`.
- **`blocked`** (exit 2): something is unsupported or failed. The tag stays,
  and the sync issue lists the manual steps. Apply them, reply `accept`, and
  `claude_ultra` re-runs with `--accept`, which moves the tag.
- **error** (exit 1): the issue quotes the error.

## Owner runbook

| Task | Command |
|---|---|
| Check main vs live without pushing | `python3 scripts/drunk-live-sync.py --check` |
| Re-run the sync | `gh workflow run drunk-live-sync.yml --ref main`, or `multica autopilot trigger 701d6f5e-68dd-4d5b-b406-d1bdf6aa6cce` |
| Run the retro now | `multica autopilot trigger 2deb281e-87f0-4592-9e72-1960656e675b` |
| Pause the loop | `multica autopilot update <id> --status paused` on either autopilot |
| Rotate the webhook | `echo y \| multica autopilot trigger-rotate-url 701d6f5e-… <trigger-id>`, then `gh secret set MULTICA_DRUNK_SYNC_WEBHOOK` with `https://multica-api.st24.live` + the new `webhook_path`. Never paste the path anywhere else: it is the secret. |
| Push live by hand from `dev` | Ask first (root `CLAUDE.md`). Get it into `main` in the next PR, or the next sync puts the `main` version back. Run `--check` afterwards. |

## Guardrails

- `setup-steward` never pushes live, moves the tag, merges or approves the PR,
  or touches `export/mx-workspace/`, `scripts/`, `.github/` or the root
  `CLAUDE.md`.
- No agent changes a gate bar, cap, weight or severity deduction; those go to
  the owner.
- `claude_ultra` runs the sync from the autopilot's description only, never
  pushes a resource by hand, and uses `--accept` only on the owner's reply.
- The sync moves the tag only when every pushed file reads back equal.

## Limits

- The Mac mini must be on: the Multica backend, the runtimes and the webhook
  endpoint all run there.
- mx-workspace has no loop or live sync yet.
- New or deleted resources, avatars, triggers, labels and properties are still
  manual steps, unless they are applied live before the merge.
