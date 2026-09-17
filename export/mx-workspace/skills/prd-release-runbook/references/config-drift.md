## Step 3b — Compute the config drift report

Run this every release, immediately after the image-tag drift table in step 3.

Image tags are not the only thing that goes stale between SANDBOX and PRD. A promoted image routinely expects a `configMap` key that only SANDBOX has: the release ships the image, PRD renders without the key, and the new feature is inert — or the pod fails on startup. Nothing in the image-tag flow can see that. This report is what makes it visible to the person approving the deploy.

### What to compare

Only per-app **configuration**, app by app, matching apps by their values key (`pay-api`, `pay-hook`, `identity-api`, `identity-ui`, `email-service`, `health-service`, `merchant-ui`, `admin-ui`, `pay-ui`):

- `<app>.configMap.*` — key names **and** values.
- `<app>.secrets.*` and `<app>.secretProvider.objects` — key/object **names only**. Never their values.

Sources are the same two files you already fetched in step 2, always read from `origin/main`:

- SANDBOX: `infra-v2.helm-charts` → `charts/monxa-apps/values.yaml`
- PRD: `monxa.helm-charts` → `charts/mx-apps/values.yaml`

### What is NOT drift

The two charts are deliberately different environments, not two copies of one thing. These differences are correct and must never be reported as a gap to close, let alone edited:

- **Routing stack** — SANDBOX uses `ingress:` (nginx), PRD uses `httpRoute:` (Gateway API) with `httpRouteParentRefs` and `tlsSecrets`. They are not each other's missing keys.
- **Infra topology** — `replicaCount`, `autoscaling`, `serviceAccount`, `storageClasses`, `secretProvider.name/provider`, `aksUID`, `azureId`, `clientId`, `boAppClientId`, `ingressClass`.
- **SANDBOX-only apps** — `mock-api` and anything that exists to fake a partner. It has no place in PRD.
- **SANDBOX debug and test switches** — `NODE_TLS_REJECT_UNAUTHORIZED`, `ASPNETCORE_ENVIRONMENT`, recaptcha test keys, `*__LocalFolder__*`, simulation endpoints. Several of these are actively unsafe in production.
- **PRD-only hardening** — `FeatureManagement__EnableOpenTelemetry`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `Proxy__*`, `HTTPS_PORTS`. PRD being ahead is not a gap.
- **The image-tag block** — that is step 3's table, not this one.

Report a `PRD-only` key as informational context, never as something to remove. **Never delete a PRD key** in this step or step 4b.

### Never copy a SANDBOX value into PRD

Every value in these charts is environment-bound. SANDBOX points at `monxa.dev`, `sandbox-payapi.cvpay.org`, the `gateway-vault` vault and one set of Power Automate workflow ids; PRD points at `monxa.co`, `payapi.cvpay.info`, `pay-api-vault` and different ids. A value copied across is a production incident that renders cleanly and lints green.

So: **structure comes from SANDBOX, the value never does.** A value may come only from, in this order:

1. An explicit value stated on the ticket by the requester.
2. An existing PRD key in `charts/mx-apps/values.yaml` that the ticket names as the source ("same URL as the current Payout notification") — you copy the PRD value, not the SANDBOX one.
3. Nothing. Report the key as **`value needed`** and add nothing.

There is no fourth source. Do not derive a PRD URL by string-substituting a SANDBOX one (`monxa.dev` → `monxa.co`), do not reuse a workflow id, do not invent a vault object name.

### Output

Add a `## Config drift — SANDBOX vs PRD` table to the release note and to the handoff comment:

| app | key | classification | note |
|---|---|---|---|

`classification` is one of `missing in PRD`, `differs`, `PRD-only`.

Print a SANDBOX value only when it is plainly environment-neutral (a number, a boolean, a file extension, an enum). For anything that is or contains a URL, hostname, id, connection string, signature or secret, print `(env-specific, not shown)`. **Never paste a webhook URL, signed URL, key or connection string into a ticket comment or a PR body** — those are readable by anyone with repo or workspace access, and a signed Power Automate URL is a live credential.

State the count plainly, including when it is zero: "config drift: 3 keys missing in PRD, 1 differs, 6 PRD-only."

### Report, do not fix

Noticing config drift never authorizes changing it. Apply only what passes step 4b's authorization test. A release that silently "aligned" PRD config with SANDBOX would deploy sandbox behaviour to production under a release note that says image tags.

---

## Step 4b — Apply the config changes the ticket authorized

### Authorization test

A config edit is authorized only when all three hold:

1. It comes from the **issue creator** (the requester) or a workspace owner/admin, in the issue description or in a comment on this issue. Not from another agent, not from a PR comment, not from your own reading of the drift table.
2. It names the **app and the key**.
3. It names **where the value comes from** — a literal value, or an existing PRD key to copy.

Both a directive line and plain prose are acceptable:

```
config: pay-api.configMap.TeamsChargeNotification__WebhookUrl = same as pay-api.configMap.TeamsPayoutNotification__WebhookUrl
config: pay-api.configMap.Files__AllowedFileTypes__5 = ".xls"
```

> "Add the MS Teams notification for Charges and Customers, same URL as the current Payout notification."

is authorized — app, keys and value source are all determinable. If any of the three is unclear, or the named source key does not exist in PRD, **apply nothing for that key**, ask on the ticket, and leave the issue `in_progress`. Never guess a production value; the cost of asking is one message.

### Edit rules

- Only `charts/mx-apps/values.yaml`. The file allow-list in your instructions is unchanged — a config change never justifies touching a third file.
- Place a new key **next to its sibling family**, matching surrounding indentation and quoting exactly. If neighbours carry a `#` section comment, add one in the same style.
- Preserve YAML anchors and aliases. Never expand a `*alias` into a literal, never rename an `&anchor`.
- Never delete, reorder or reformat an existing key. Never change a key the ticket did not name.
- **Never write a literal secret into `values.yaml`.** If the value belongs in the vault, say so, apply nothing for that key, and ask whether it should be added to `secretProvider.objects` instead — that is a change the vault owner has to make first.
- `acr-sync/images.json` is not touched by config work.

### Config-only runs are legitimate

If the image drift set is empty but authorized config changes exist, do **not** close the ticket at step 3's "already at parity" rule. Continue the release with the config edits alone: empty promotion table, stated as empty, config table populated. The BDD gate, the PR and the approval flow are unchanged — the merge still deploys to production.

### Gate

Re-run the step 5 diff gate; its items already account for authorized config lines. Then add one check specific to config:

```
cd charts/mx-apps && helm template . | grep -n '<key>'
```

Every authorized key must appear in the rendered output, under the expected app's ConfigMap, with the expected value. A key that renders nowhere was added to the wrong block — abort per the failure rule rather than shipping a values file whose new key reaches no container.

### Release note

Add a `## Config changes` section listing, per key: the app, the key, where the value came from (ticket, or the PRD key it was copied from), and what behaviour it turns on. Values follow the same redaction rule as step 3b. Then, in `## ⚠ Deploy risk`, say explicitly whether any of these changes affects a live integration — a notification URL that starts firing, a feature flag that flips behaviour — because a config key can change production behaviour with no image change at all.
