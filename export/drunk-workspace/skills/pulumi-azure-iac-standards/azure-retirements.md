# Azure retirement list (pinned)

**Last human verification: NEVER — this file has not yet been verified by a human.**
**Compiled: 2026-08-28. Owner: workspace owner (drunkcoding).**

This file is the **only** source a review run may cite for a `PULUMI-DEP-001` or `PULUMI-DEP-002`
finding. Retirement dates recalled from a model's memory are unreliable, and a wrong date in a
finding costs the reviewer a month of trust — so the rule is mechanical:

1. A service **not listed here** is not a `PULUMI-DEP-001` finding. Propose a row instead.
2. A date **not written here** never appears in a finding.
3. A row marked `confidence: verify` may **not** be filed as a code finding until a human confirms
   it and flips the row to `confidence: confirmed`. It may only be raised in the list-update issue.
4. Confirm every row against <https://azure.microsoft.com/updates/?updateType=retirements> and the
   service's own `learn.microsoft.com` page. The `source` column is a search hint, not a citation —
   do not paste it into a finding as if it were a verified reference.

## Retired — past date

| Service / SKU | Retired | Replacement | Confidence | Source hint |
|---|---|---|---|---|
| Azure Database for MySQL — Single Server | 2024-09-16 | Flexible Server | verify | retirement hub, "MySQL Single Server" |
| Azure Database for PostgreSQL — Single Server | 2025-03-28 | Flexible Server | verify | retirement hub, "PostgreSQL Single Server" |
| Log Analytics agent (MMA/OMS) | 2024-08-31 | Azure Monitor Agent | verify | retirement hub, "Log Analytics agent" |
| Azure Media Services | 2024-06-30 | partner encoders / Azure AI Video Indexer | verify | retirement hub, "Media Services" |
| Azure Data Lake Storage Gen1 | 2024-02-29 | ADLS Gen2 on Storage | verify | retirement hub, "Data Lake Storage Gen1" |
| API Management — `stv1` compute platform | 2024-08-31 | `stv2` platform | verify | retirement hub, "API Management stv1" |
| Classic (ASM) storage accounts | 2024-08-31 | ARM storage accounts | verify | retirement hub, "classic storage accounts" |
| Azure AD Authentication Library (ADAL) | 2023-06-30 | MSAL | verify | Entra ID docs, "ADAL end of support" |
| Azure AD Graph API | see source | Microsoft Graph | verify | Entra ID docs — staged dates, confirm before use |
| AKS — AAD Integration (legacy, non-managed) | 2023-06-01 | AKS-managed Entra integration | verify | AKS docs, "AAD Integration legacy" |
| Azure Automation — Run As accounts | 2023-09-30 | managed identity | verify | retirement hub, "Run As accounts" |
| Container Registry — Classic SKU | 2019-03-31 | Basic / Standard / Premium | verify | ACR docs, "classic SKU deprecation" |
| Azure Monitor — classic metric alerts | see source | metric alerts (near-real-time) | verify | retirement hub, "classic alerts" |
| Basic SKU public IP addresses | 2025-09-30 | Standard SKU public IP | verify | retirement hub, "Basic public IP" |
| Basic SKU Load Balancer | 2025-09-30 | Standard Load Balancer | verify | retirement hub, "Basic Load Balancer" |
| Unmanaged disks | 2025-09-30 | managed disks | verify | retirement hub, "unmanaged disks" |
| Azure CDN from Edgio | 2025-01-15 | Front Door Standard/Premium | verify | retirement hub, "Edgio CDN" |
| Kubernetes PodSecurityPolicy (AKS) | removed in K8s 1.25 | Azure Policy for AKS / Pod Security Admission | verify | AKS docs, "PodSecurityPolicy removal" |

## Announced — future date (deprecate now, delete at the major)

| Service / SKU | Retires | Replacement | Confidence | Source hint |
|---|---|---|---|---|
| Application Gateway v1 (Standard / WAF) | 2026-04-28 | Application Gateway v2 | verify | retirement hub, "Application Gateway V1" |
| Azure Front Door (classic) | 2027-03-31 | Front Door Standard/Premium | verify | retirement hub, "Front Door classic" |
| Azure CDN Standard from Microsoft (classic) | see source | Front Door Standard/Premium | verify | retirement hub, "CDN classic" |
| Azure Spring Apps | see source | Azure Container Apps | verify | retirement hub, "Spring Apps" |

## Not a retirement — do not file as `PULUMI-DEP-001`

These come up in reviews and are **not** retirements. Use the rule named instead.

- A provider property marked `@deprecated` in the Pulumi SDK → `PULUMI-UP-004`.
- A dated API-version import with an open support window → `PULUMI-UP-003`.
- TLS 1.0/1.1 minimums → `PULUMI-SEC-004` (a hardening default, not a service retirement).
- A local wrapper superseded by an upstream component → `PULUMI-UP-005`.

## Maintenance

The monthly review run **proposes**; a human **confirms**. Each run that finds a gap files exactly
one issue, `[<RULE-PREFIX>] azure-retirements.md needs updating`, containing the proposed rows in
this table format plus the source it read them from. When a human verifies a row, flip its
`confidence` to `confirmed`, add the verification date to the header, and only then may that row
back a `PULUMI-DEP-001` finding.
