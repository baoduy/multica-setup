---
name: autopilot-spec
description: "Standard structure for writing effective Multica autopilot runbooks. Use when creating or modifying autopilots. Every autopilot description must follow Goal → Context → Steps format."
user-invocable: true
allowed-tools: Bash(multica *)
---

# Autopilot Spec

Use this skill when creating or updating Multica autopilot's description. The description is read by agent on every run — its structure determines whether agent produces useful output.

## Standard Structure

Every autopilot description must have exactly these three sections:

### Goal

What should agent accomplish in this run? One sentence. No ambiguity.

Good: "Post daily summary of all open P1 issues to the #ops Slack channel."
Bad: "Check on things."

### Context

Who is this for? What are constraints? What workspace/project/issue context applies?

- **Audience** — who receives output?
- **Scope** — what repos, services, projects, or issue filters are relevant?
- **Constraints** — any limits (read-only, destructive ops forbidden, time window, rate limits)?
- **Inputs** — environment variables, webhook payload shape, or other data run receives.

### Steps

Numbered, actionable steps agent performs in order. Each step starts with concrete verb (Check, Fetch, Parse, Post, Create, Update,...).

1. [First action — what agent does first]
2. [Second action — builds on previous step]
3. [Final step — deliver or report result]

Each step must be testable: observer can tell if step succeeded.

## Output Format (optional)

Only include if agent must produce output in specific shape (Slack message format, JSON, issue comment style, etc.).

## Examples

### Daily issue summary (schedule-triggered)
```
# Goal
Post a summary of all issues updated in the last 24h in project mx-main to a Slack webhook.

# Context
- Audience: the workspace team (drunkcoding, dev-team, qc-team)
- Scope: issues in project mx-main (8008ea4e...)
- Constraints: read-only, Slack webhook URL from env SLACK_WEBHOOK_URL
- Inputs: none (self-triggered on schedule)

# Steps
1. Use `multica issue list --project 8008ea4e-76ce-4035-9824-8041e82d1b68 --updated-since "24h" --output json` to fetch recent issues.
2. Format a Slack message: one line per issue with title, status, priority, assignee.
3. POST the formatted message to SLACK_WEBHOOK_URL.
```
### Webhook-triggered notification
```
# Goal
When a GitHub push webhook fires, parse the payload and create a Multica issue if the branch is `dev`.

# Context
- Audience: product-owner agent for triage
- Scope: any repo with a push to `dev`
- Constraints: only act on push events to `dev`; ignore tag pushes, other branches
- Inputs: webhook payload (push event JSON)

# Steps
1. Parse the webhook payload: extract repo name, pusher, commit messages.
2. If ref is `refs/heads/dev`, create a Multica issue titled "Push to dev: <repo>" with the commit list.
3. Assign the new issue to product-owner for review.
```