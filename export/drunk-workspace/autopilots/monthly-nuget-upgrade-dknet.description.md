# Goal

Each month, upgrade every NuGet package reference in the DKNet repository to its latest stable version compatible with the solution's current target framework, delivered as ONE PR against `dev`. The solution currently targets .NET 10 — framework-family packages (`Microsoft.*`, `System.*`, EF Core, ASP.NET Core) go to the latest 10.x.x; third-party packages go to their latest stable release that supports `net10.0`.

# Context

- **Requester** — the workspace owner (resolve at runtime: `multica workspace member list --output json`, role `owner`; never a hardcoded UUID).
- **Scope** — ONE repo: `DKNet` — https://github.com/baoduy/DKNet.git. Do NOT touch `DKNet.Templates` or any other repo in this run.
- **Project** — this run issue and every sub-task live in `drunk-net` (id from `multica project list --output json`). Never cross-file into another project.
- **How** — run your normal squad cycle (Build → Verify → Review) per your playbook. This description is the approved spec; no product-owner round is needed. Read the repo's own `CLAUDE.md` / `AGENTS.md` first — solution-local conventions override anything generic here.

# Spec

1. **Inventory first.** Run `dotnet list package --outdated` across the solution and `dotnet list package --vulnerable --include-transitive`; record the before-state.
2. **Upgrade rules:**
   - Stay on the current target framework (`net10.0`) — a TFM bump is out of scope for this run.
   - Stable releases only; never preview/rc/beta.
   - Framework-family packages align to the latest 10.x.x.
   - Third-party packages: latest stable version compatible with `net10.0`. If a major-version jump requires more than mechanical code fixes, SKIP it, keep the current version, and report it as deferred with the reason and the blocking breaking change.
   - If the solution uses central package management (`Directory.Packages.props`), change versions there only — never scatter per-project overrides.
3. **Gate:** full solution builds with zero errors and zero warnings, ALL pre-existing tests green, `dotnet pack` clean, and the upgrade introduces no new `dotnet list package --vulnerable` findings.
4. **Deliverable:** ONE PR to `dev` whose body contains the version-bump table (package, old → new) and the deferred-upgrades list.

# Steps

1. Set this issue to `in_progress`.
2. Run the cycle per your squad playbook, applying the spec above.
3. Post the run report on this issue: bump table, deferred upgrades with reasons, vulnerable-package status before/after, PR link, anything skipped — a partial run is reported as partial, never as clean. Then finalize per your playbook rules.