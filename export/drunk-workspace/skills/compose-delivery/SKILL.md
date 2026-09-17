---
name: compose-delivery
description: >-
  Safe procedure for changing a docker-compose deployment file — read
  current file from tracked branch not a stale worktree, validate
  resolved config with `docker compose config` before opening PR, and
  deliver via normal PR flow. Use when editing docker-compose.yml services,
  env/config blocks, volumes, ports, or adding a service to a compose stack.
category: devops
triggers:
  - docker compose
  - compose file
  - docker-compose.yml
  - compose stack
---

# Docker Compose Delivery

A compose file is deploy artifact for a stack, but — unlike a GitOps helm
chart — **merging it does not auto-deploy.** A human runs `docker compose up -d`
(or an install script) after change lands. So delivery flow is
ordinary app-repo PR flow: there is no "never merge" GitOps gate. What matters is
that file you ship actually parses and resolves.

## Read current file from remote, never a stale worktree

An agent checkout may sit on a stale per-agent branch. Read real current
state from tracked branch:

```bash
git fetch origin <branch>
git show origin/<branch>:<path/to/docker-compose.yml>
```

## Make change

Locate blocks by their **service name or key**, never by line number — compose
files get reordered and a line-number edit silently lands in wrong service.

## Validate before opening PR

`config` is compose analogue of `helm template`: it merges overrides,
resolves `${VAR}` interpolation and `env_file`, and fails on an invalid schema.

```bash
docker compose -f <path> config -q     # parses + resolves; exits non-zero on error
docker compose -f <path> config        # inspect fully-resolved output
```

Confirm **your change appears in resolved output.** A block that still
renders OLD value means your edit did not take effect — wrong file, wrong
key, or overridden by an override file / env.

If `docker compose` is not available, **say so explicitly in PR body** —
never let a reviewer assume validation passed silently.

## Deliver via normal PR flow

Follow `sdlc-gitflow`: push a `chore/<issue-key>` branch by refspec (never
`git checkout` a shared branch), open ONE PR to repo's integration branch
with `--head` and `--base` explicit, and report link. A human merges and
deploys. State in PR body whether a manual deploy step is required after
merge.

## Never

- **Never assume merging deploys** — but DO say in PR whether a human deploy
  step is required after merge.
- **Never validate against a stale worktree copy;** read from tracked branch.
- **Never edit by line number.**

## Verification checklist

- [ ] Current file read via `git show origin:<branch>:<path>`
- [ ] Edit located by service/key, not line number
- [ ] `docker compose config -q` exits clean
- [ ] Resolved `config` output shows NEW value
- [ ] PR opened to integration branch, head `chore/<issue-key>`
- [ ] PR body states whether a manual deploy step follows merge
- [ ] PR reported, not merged