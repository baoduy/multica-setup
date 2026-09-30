# CLAUDE.md — multica/export

Rules for editing workspace bundles here (in addition to `../CLAUDE.md`:
analyse first, local bundle first, ask before pushing live).

## Git

- Commit and push straight to `dev` in this repo — no feature branch, no PR.
  This overrides the default "branch first when on the default branch" rule.
- Before committing, sync with `origin/dev` (`git fetch` + rebase or
  fast-forward); never force-push `dev`.
- One commit per accepted change, message prefixed with the bundle
  (`drunk:`, `mx:`, or `drunk+mx:`).

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

## Vendored upstream skills — archify

`export/drunk-workspace/skills/archify/` mirrors the `archify/` directory of
https://github.com/tt-a1i/archify for the Multica platform. The same skill is
installed globally for Claude Code at `~/.claude/skills/archify`. mx-workspace
does not carry it yet.

- Check for a new upstream release from time to time, and on every
  `multica-release-review` run. The bundle version is in
  `skills/archify/skill-release.json`. The upstream version is
  `gh api repos/tt-a1i/archify/releases/latest --jq .tag_name`.
- Sync = replace the bundle dir with upstream `archify/` at the release tag.
  The bundle intentionally drops `test/` and the rendered `examples/*.html`.
  It keeps the bundle-only `config.json` (the Multica import origin). Diff
  first (`diff -rq <clone>/archify export/drunk-workspace/skills/archify`),
  so the only differences are those three.
- Read the upstream `CHANGELOG.md` before you sync. A major or minor bump can
  change the CLI, the schemas or the IR shape. Re-check everything in the
  bundle that quotes archify commands, types or file names. Find them with
  `grep -rli archify export/drunk-workspace --exclude-dir=archify`: agents,
  doc/design templates, both gate skills, the delivery pipeline and Policies
  05, 06 and 09.
- Never pin `ARCHIFY_CHROME` in an agent's `custom_env`. A runtime can be
  macOS or Ubuntu, and archify finds Chrome by itself only when the variable
  is unset (`findChrome` in `bin/visual-check.mjs`). On macOS it checks
  `/Applications`. On Linux it searches `PATH` for `google-chrome`,
  `google-chrome-stable`, `chromium` and `chromium-browser`, so each Ubuntu
  host needs one of those on `PATH`. If a host needs
  `ARCHIFY_CHROME_NO_SANDBOX=1`, set it in that host's daemon environment.
  Do not set it per agent. Re-check `findChrome` after every sync.
- Update the global copy in the same pass:
  `npx -y skills add tt-a1i/archify --skill archify --agent claude-code --global --copy --yes`.
- Push live like any other skill: ask first. Use `multica skill update` for
  `SKILL.md` and `multica skill files upsert` for every changed file. Use
  `multica skill files delete` for files that upstream removed. Then read the skill back and diff it against
  the bundle.
- Commit as `drunk: sync archify to vX.Y.Z`.

<!-- rtk-instructions v2 -->
# Command output

Command output here is condensed to save tokens, keeping every signal and
dropping costly noise. Treat it as the complete result: run commands
normally, and batch related commands into one call to avoid extra turns.
Truncated results state their recovery path in their own output. Re-run a
command as `rtk proxy <cmd>` only when its result is unusable: empty when
output was clearly expected, contradicting its exit code, or garbled.
<!-- /rtk-instructions -->