# Policy 10 — Ticket Ownership & Owner Pickup

| | |
|---|---|
| **Policy ID** | DRK-POL-10 |
| **Version** | 1.3 |
| **Status** | Active |
| **Owner** | product-owner (sets Owner on the tickets it creates; every agent shares the resolution duty) |
| **Applies to** | Every ticket in the workspace — main tickets, spec-review sub-tasks, phase tickets, dev sub-tasks, gate handoffs, arch/BDD findings, and autopilot-filed issues |
| **Related skills** | [`sdlc-flow-delivery-pipeline`](../../skills/sdlc-flow-delivery-pipeline/SKILL.md) · [`sdlc-flow-po-orchestration`](../../skills/sdlc-flow-po-orchestration/SKILL.md) · [`sdlc-flow-squad-leader-playbook`](../../skills/sdlc-flow-squad-leader-playbook/SKILL.md) · [`spec-review-gate`](../../skills/spec-review-gate/SKILL.md) · [`pr-review-gate`](../../skills/pr-review-gate/SKILL.md) |
| **Enforced at** | product-owner, squad leaders, spec/PR gates, arch-reviewer, autopilots |

> **Authority.** This policy is the source of truth for *who the human owner of a ticket is*
> and *how an agent finds them*. The related skills **implement** the resolution order and
> the set-on-create rule; the `Owner` custom-property definition below is the shared
> mechanism. Amend this policy first, then cascade — see
> [change control](00-policies-index.md#change-control).

## Owner pickup at a glance

```
   agent needs the human owner of a ticket
                 │
                 ▼
   ① ticket's own `Owner` property set? ───────────────── yes ─▶ that member
                 │ no
                 ▼
   ② nearest ancestor's custom `Owner` (walk parent_id to root)? ─ yes ─▶ that member
                 │ no
                 ▼
   ③ ROOT ticket creator_type == member? ───────────────── yes ─▶ root creator_id
                 │ no (agent creator / lookup failed)
                 ▼
   ④ workspace owner (multica workspace member list, role owner)  ◀── LAST resort
```

## Purpose

Before this policy, agents that needed a human — a gate handing back a review, a squad
escalating a blocker — resolved the human inconsistently. Some walked to the ROOT creator
first; the review gates skipped straight to the **workspace owner**. On an agent-created
root (a QC-filed defect, an arch finding promoted to a bug) that shortcut always landed on
the workspace owner, so *every* ticket appeared to be owned by one person (the incident on
MXW-2066). This policy makes ownership **explicit, propagated, and resolved the same way by
every agent**, so the right human is reached and the workspace owner is only ever the
fallback.

## Scope

- **In scope**: resolving the human owner of any ticket; stamping ownership at create time;
every human handoff (gate manual-handoff, squad escalation, clarification, FYI).
- **Out of scope**: *agent* assignment and wake mechanics (Policy 05 statements 5 and 6;
the Workspace Context, "Status and wakes"); which human makes which *decision* (Policy 05 escalation
map). This policy answers only **which human**, not what they are asked to do.

## The `Owner` custom property

- The workspace defines a custom issue property named `**Owner**` (drunk-workspace type
`actor` — a single member). It is the deliberate, machine-readable designation of a
ticket's human owner.
- Read it: `multica issue property list <issue-id> --output json`.
- Set it: `multica issue property set <issue-id> --name Owner --value "<member-name-or-id>"`.

## Policy statements

1. **Every ticket has exactly one resolvable human owner.** An agent that needs a human for
 a ticket MUST be able to name that member — resolution never ends in "unknown".
2. **Resolution order is Owner-property-first** (the "owner pickup" order): (1) the ticket's
 own `Owner` property; else (2) the nearest ancestor's `Owner`, walking `parent_id` toward
 the root; else (3) the ROOT ticket's `creator_id` when its `creator_type` is `member`;
 else (4) the workspace owner (`multica workspace member list --output json`, role
 `owner`). The first step that yields a member wins. This is the single order every agent
 uses; no role resolves ownership any other way.
3. **The `Owner` property is authoritative when set.** Because it is the deliberate
 designation, a set `Owner` outranks the root creator — it is checked first (statement 2).
 This lets an agent-filed root name a human the automatic creator lookup could not.
4. **Set `Owner` on every issue you create.** After creating a ticket, resolve the owner
 from its parent (statement 2) and stamp it: `multica issue property set <new-id> --name  Owner --value "<member>"`. This propagates ownership down the tree so a descendant
 resolves the human in one lookup instead of falling through to the workspace owner.
5. **An agent that files a ROOT ticket sets `Owner` to the human the work is for.** A root
 created by an agent (QC-consolidated defect, arch finding routed as a bug, autopilot
 escalation) has no member creator, so statement 3 cannot help a descendant — the creating
 agent MUST stamp `Owner` explicitly.
6. **Never hardcode a member name or UUID for owner routing.** Resolve at runtime, every
 time, via statement 2. A pinned name/UUID in a skill, agent instruction, squad briefing,
 or autopilot is a policy violation — it silently breaks when ownership changes and it
 reintroduces the "one person owns everything" failure.
 The same rule holds for every other id an instruction could pin — agent, squad and project — resolved with `multica agent|squad|project list --output json` at run time. An agent mention link is the sharpest case: it is a wake wherever it appears, so an instruction states the recipe and never the link (Workspace Context, Status and wakes). A platform-generated squad roster is not a pin.
7. **The workspace owner is the last resort, never the default.** Reaching step 4 means
 steps 1–3 all failed; if that happens often it signals missing `Owner` stamps upstream
 (statement 4/5), not correct routing.
8. **Deliver a human handoff by ASSIGNMENT, not by mention.** Once the owner is resolved,
 reassign the relevant ticket to that member at `todo` (`--assignee-id <member-uuid>`); a
 member mention only notifies and enqueues no work. (Cross-references Policy 05 / the
 wake-signal contract.)
9. **Gates resolve via statement 2 — no workspace-owner shortcut.** `spec-review-gate` and
 `pr-review-gate` manual handoffs resolve the human by the full order, not straight to the
 workspace owner.
10. **Finding-filers file to the resolved triager.** `arch-reviewer` (and any monthly sweep)
  assigns findings to the human triager resolved at runtime — for an unattended sweep with
  no member-created parent, that resolves to the workspace owner via step 4, but it is
  resolved, never hardcoded.

## Roles & responsibilities

- **product-owner** — stamps `Owner` on every child it creates (`[S#]`, `[P<num>-*]`), and
on any root it files itself; resolves the human for clarifications/escalations via the order.
- **Squad leaders** — stamp `Owner` on every sub-task they create from the cycle parent.
- **spec/PR review gates** — resolve the manual-handoff human via the order (statement 9).
- **arch-reviewer / autopilots** — resolve the triager/audience at runtime (statement 10),
never a pinned UUID.
- **workspace owner** — the escalation valve of last resort (step 4); not the default owner.

## Definition of Done / compliance

- Any open ticket resolves to a **non-null member** through the order in statement 2.
- Every agent-created child carries an `Owner` property (spot-check:
`multica issue property list <child-id>` returns an `Owner` value).
- No skill, agent, squad, or autopilot contains a hardcoded member name/UUID for owner
routing (`grep` for the workspace owner's UUID returns only the Policy 09 identity header,
historical audit notes, and the blog domain).

## Enforcement

- **At every human handoff** — the gate/leader resolving the human applies statement 2; a
handoff that jumped to the workspace owner while an `Owner` property or member creator
existed is a defect.
- **At create time** — a created child missing its `Owner` stamp is a defect in the creating
agent's run.
- **Monthly architecture-review sweep** and code review catch hardcoded UUIDs reintroduced
into skills/agents.

## Exceptions & waivers

- The Policy 09 workspace-identity header (`Owner | <workspace owner>`) legitimately names
the human — it is the single source of who the current owner *is*, not a routing hardcode.
- Historical/audit references naming a person (e.g. "authorized the REST exception on
2026-07-27") and the `drunkcoding.net` blog-domain references are not owner routing and are
out of scope.
- No agent may waive statement 6 (no hardcoding) on its own; a genuine need for a fixed
assignee is a policy amendment, not a local exception.

## References

- [Policy 05 — SDLC Delivery Lifecycle](05-sdlc-delivery-lifecycle.md) — escalation map, wake/status discipline.
- [Policy 09 — Agent Roles & Responsibilities](09-agent-roles-and-responsibilities.md) — workspace-identity header, triager routing.
- The Workspace Context, **Tickets** ("Set the `Owner` property on every issue you create" and the resolution order) — the implementing contract every agent run carries.
- Incident: MXW-2066 (`[D2058-3] Review`) — gate resolved to workspace owner because the 2-step order skipped the `Owner` property; the fix that motivated this policy.

