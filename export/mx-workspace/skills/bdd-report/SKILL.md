---
name: bdd-report
description: "Use BEFORE executing any BDD suite against Monxa SANDBOX (suite runs on GitHub Actions, never locally) and when writing results report on qc-team sub-issue."
---

# BDD Execution & Report Format

## Execution — dispatch to GitHub Actions, never run suite locally

Your runtime kills any single shell command at 600 000 ms and **discards its output**, then force-stops your whole run after 10 minutes without message from you. The payment-gateway suite alone is 45 feature files / 313 scenarios — it cannot finish inside one shell call. Running it locally does not fail slowly, it produces **nothing**: no partial results, no failure list, and sub-issue stranded with idle-watchdog comment.

Run it in CI. In `monxa.bdd-integration`:

**1. Dispatch.** The workflow definition is read from default branch, so branch under test does NOT need workflow file — pass it as `ref`:
```
gh workflow run bdd-sandbox.yml --repo the-wixo/monxa.bdd-integration \
  -f ref=<branch-tag-or-sha> \
  -f scope=Api/payment-gateway/features/   # omit for the full suite
```
Optional inputs: `grep=@smoke` (tag filter), `workers=N`. **Leave `workers` at its default of 1** — SANDBOX is shared and scenarios share fixtures and seeded data; parallel workers buy minutes and cost you false failures.

**2. Get run id.** The dispatch prints nothing:
```
gh run list --workflow bdd-sandbox.yml --repo the-wixo/monxa.bdd-integration -L 3 \
  --json databaseId,status,createdAt,url
```
Take newest `queued`/`in_progress` run. If it is not listed yet, run command again — do not guess id.

**3. Wait in chunks under shell cap.** One tool call per chunk, so you keep emitting messages and idle watchdog never fires:
```
timeout 540 gh run watch <run-id> --repo the-wixo/monxa.bdd-integration --exit-status; echo "exit=$?"
```
- `exit=0` → suite is green.
- `exit=124` → 540 s chunk elapsed and run is still going. **Repeat identical command.** A full suite takes 20–40 minutes, so expect several chunks.
- any other non-zero → run finished and at least one scenario failed. Go to step 4 for details.

Never wrap this in one longer wait, never background it, and never poll in loop inside single call — each chunk must be its own tool call.

**4. Pull machine-readable result:**
```
gh run download <run-id> --repo the-wixo/monxa.bdd-integration --name cucumber-json --dir ./bdd-result
```
`./bdd-result/cucumber.json` holds every executed scenario. Read: feature `name` and `uri`, each element's scenario `name`, each step's `result.status` and `result.error_message`. `gh run view <run-id>` also prints pass/fail/skip totals from Step Summary if that is all you need.

**Rules**

- Report only what `cucumber.json` shows. **A missing artifact means run produced no results — that is blocker, not pass.**
- Never dispatch with `ref=main` from verification gate: `main` runs publish report to public Cloudflare Pages site.
- One dispatch per verification round. Need wider scope? Dispatch again with wider `scope` — never fall back to running Playwright locally.
- `npx bddgen` alone is fast and safe locally; use it to check regeneration exits 0 and leaves no `.features-gen/` diff.

## Report Structure

Post ONE comment on your sub-issue with this structure:

### 1. Run Info

- **Ref:** branch/tag/commit suite was executed against (the `ref` input)
- **Scope:** the `scope` / `grep` inputs used, and `workers`
- **CI run:** GitHub Actions run URL
- **Environment:** SANDBOX base URL
- **Date/Time:** when run occurred

### 2. Results Table

| # | Feature | Scenario | Status | Error |
|---|---------|----------|--------|-------|
| 1 | `login.feature` | Successful login with valid credentials | PASS | — |
| 2 | `login.feature` | Login with invalid password | PASS | — |
| 3 | `payments.feature` | Process refund for settled transaction | FAIL | Expected 200, got 500. Response: `{"error":"internal"}` |

### 3. Failure Details

For each FAIL row: HTTP method, URL, request body (sanitized), expected status/body, actual status/body. Redact secrets.

### 4. Coverage Gaps

Existing tests that didn't cover requested scenario → note which, don't write new ones.

### 5. Verdict

- **All PASS** → flip sub-issue to `done`
- **Any FAIL** → flip to `blocked`, post short summary on parent issue
- **Coverage gaps** → flip to `blocked`, post on parent issue
