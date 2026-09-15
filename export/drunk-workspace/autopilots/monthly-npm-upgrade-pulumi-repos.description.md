# Goal

Each month, upgrade every npm dependency across ALL Pulumi component repos to its latest stable version. This run issue is the COORDINATOR PARENT — you do not upgrade anything on it directly. Create one child delivery issue per repo (list below), each child running its own full squad cycle and delivering its own PR against that repo's `dev` branch. The parent finalizes only when every child is complete.

# Repos (one child issue per repo)

1. `drunk-pulumi-azure-components` — https://github.com/baoduy/drunk-pulumi-azure-components.git
2. `drunk-pulumi-azure-providers` — https://github.com/baoduy/drunk-pulumi-azure-providers.git
3. `drunk-pulumi-cloudflare-components` — https://github.com/baoduy/drunk-pulumi-cloudflare-components.git
4. `drunk-pulumi-intune-components` — https://github.com/baoduy/drunk-pulumi-intune-components.git

# Context

- **Requester** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, role `owner`; never a hardcoded UUID).
- **Project** — this parent, every child, and every sub-task live in `drunk-pulumi` (`59f7d38d-0588-44b7-95c3-9744f64c6e1e`). Never cross-file into another project.
- **How** — create the child issues with `--parent <this-issue-id>`, titled `npm Upgrade — <repo>`. Each child is a normal cycle of its own: decompose it per your playbook (Build → Verify → Review), ONE feature branch and ONE PR to `dev` per child — never a combined PR across repos. Run children sequentially or in parallel per your capacity rules. This description is the approved spec; no product-owner round is needed. In each repo, read its own `CLAUDE.md` / `AGENTS.md` first — repo-local conventions override anything generic here.

# Per-repo spec (applies to every child)

1. **Inventory first.** Run `npm outdated` and `npm audit` and record the before-state.
2. **Upgrade rules:**
   - Stay on the repo's current Node engine (`engines` field) — a Node major bump is out of scope for this run.
   - Stable releases only; never alpha/beta/rc/next tags.
   - `@pulumi/pulumi` and provider SDKs (e.g. `@pulumi/azure-native`, `@pulumi/cloudflare`, `@pulumi/azuread`) to their latest stable versions.
   - All other dependencies and devDependencies: latest stable. If a major-version jump requires more than mechanical code fixes, SKIP it, keep the current version, and report it as deferred with the reason and the blocking breaking change.
   - Update `package.json` version ranges AND the lockfile together; never lockfile-only bumps.
3. **Gate:** clean install from lockfile, build/compile with zero errors, ALL pre-existing tests green (Pulumi runtime mocks only — never real cloud APIs), `npm pack` clean, and no new high/critical `npm audit` findings introduced by the upgrade.
4. **Deliverable:** ONE PR to `dev` whose body contains the version-bump table (package, old → new) and the deferred-upgrades list.

# Steps

1. Set this issue to `in_progress`.
2. Create the four child issues and run each per your squad playbook, applying the per-repo spec.
3. When all children are complete, post the consolidated run report on THIS parent: per repo — bump summary, deferred upgrades with reasons, audit status before/after, PR link; plus anything skipped. A repo whose cycle failed or was partial is reported as such, never as clean. Then finalize per your playbook rules.