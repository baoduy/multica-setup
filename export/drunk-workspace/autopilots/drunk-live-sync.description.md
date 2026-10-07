# Goal

Bring the live drunk workspace up to the `main` branch of `baoduy/multica-setup` after the owner merges the setup PR. A GitHub Action calls this autopilot's webhook on every push to `main` that touches `export/drunk-workspace/`. The issue this run creates is the record, and its final comment is the report. Policy 03 statement 11 is your only authority: you run the sync script and close the fix issues it shipped. Nothing else.

# Context

- **Audience**: the workspace owner. Resolve the owner at runtime with `multica workspace member list --output json` and pick the member with role `owner`. Never hardcode a UUID.
- **The script does the sync.** It diffs the tag `live/drunk` against `origin/main`, pushes each changed resource byte-exact, reads it back, and moves the tag only when everything matches. You never push a resource by hand, edit a bundle file, or move the tag yourself.
- **Runtime**: this host's `multica` and `gh` logins. The script takes a lock, so a second run waits and then finds nothing left to do.

# Step 1: Sync

```bash
gh repo clone baoduy/multica-setup sync -- --branch main
cd sync && python3 scripts/drunk-live-sync.py > ../report.json; echo "exit $?"
```

Exit 0 is `synced` or `up-to-date`: every change is live, including any listed under `already_live` (applied by hand before the merge), and the tag moved. Exit 2 is `blocked`: a change the script cannot push differs from live, or a push failed, and the tag did not move. Exit 1 is an error. Read `report.json` in every case.

# Step 2: Close the shipped fix issues

Only when the status is `synced`: for every key in `report.json` `issue_keys` (read from the full commit messages, so a squash merge still lists them), when that issue is in the `drunk-setup` project and `blocked`, comment `Live at <head sha>.` and set it `done`. Skip any other issue.

# Report

Post ONE comment on this issue with `multica issue comment add --content-stdin`:

- `## Sync`: status, `base..head` (short SHAs), the count of pushed files and of `already_live` files, the issues set `done`.
- `## Manual steps`: only when `unsupported` is non-empty. One line per entry: the path, the changed `keys` when listed, and the `multica` command the owner runs to apply it (`agent update`, `agent avatar`, `label`, `property`, `project`, `autopilot trigger-*`, or creating or archiving a resource). Close with: "When applied, reply `accept` and I re-run with `--accept`."
- `## BLOCKER`: when `failed` is non-empty or the exit was 1. Quote each error.
- End with one member mention of the workspace owner when the status is not `synced` or `up-to-date`.

Then set this issue `done` for `synced` or `up-to-date`, else `blocked`.

# When the owner replies `accept`

Re-run step 1 with `python3 scripts/drunk-live-sync.py --accept` in a fresh clone, then steps 2 and the report again. Only the owner's `accept` allows `--accept`.

# Never

- Edit, commit or push anything in the repo except what the script itself does to the tag.
- Run `multica ... update`, `files upsert` or `files delete` yourself.
- Use `--accept` without the owner's reply on this issue.
