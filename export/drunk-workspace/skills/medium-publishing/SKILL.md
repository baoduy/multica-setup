---
name: medium-publishing
description: >-
  Republish a drunkcoding.net blog post (github.com/baoduy/hbd.astro-paper) to
  Medium as a canonical-linked draft via the Medium API. Covers the required
  environment variables, the exact request shape, frontmatter-to-payload
  mapping, link rewriting, and what to do when the API rejects the token. Use
  whenever asked to post, cross-post, mirror, or republish an article to Medium.
category: content
triggers:
  - medium
  - cross-post
  - republish
  - syndicate
  - mirror article
---

# Publishing to Medium

Procedure for mirroring a published drunkcoding.net post onto Medium. The blog
repo stays the source of truth: this skill only reads it, never edits it. Post
authoring rules (location, filename, frontmatter, voice) live in
`astro-paper-blog-conventions` — do not duplicate them here.

## Prerequisites

Two environment variables must be present. They are set on the agent, not in
this skill:

- `MEDIUM_TOKEN` — Medium integration token
  (`medium.com/me/settings/security` → Integration tokens).
- `MEDIUM_USER_ID` — the Medium author id.

`MED-PRE-001` **Verify credentials before doing any work.** Run:

```bash
curl -sS -H "Authorization: Bearer $MEDIUM_TOKEN" https://api.medium.com/v1/me
```

A 200 returns `{"data":{"id":"...","username":"..."}}`. The `id` must match
`MEDIUM_USER_ID`; if it does not, use the value from the response and report the
mismatch. On 401/403 stop immediately and report that the token is invalid,
expired, or revoked — do not retry, and do not attempt any other publishing
route without being asked.

`MED-PRE-002` **The Medium API is unmaintained.** Medium stopped actively
maintaining the public write API and no longer issues integration tokens to
every account. If no token can be obtained, the only remaining route is Medium's
manual "Import a story" tool (`medium.com/p/import`, paste the drunkcoding.net
URL), which a human must run. Say so plainly rather than improvising a scraper
or browser automation.

## Step 1 — Locate the source post

`MED-SRC-001` Check out the blog repo with `multica repo checkout
https://github.com/baoduy/hbd.astro-paper.git` and read the post from
`src/data/blog/`. The file is `<slug>.md`; the live URL is
`https://drunkcoding.net/posts/<slug>`.

`MED-SRC-002` **Only mirror published posts.** If the frontmatter has
`draft: true`, stop and report it — a post that is not live on drunkcoding.net
has no canonical URL to point at, and publishing it to Medium first inverts the
canonical relationship.

## Step 2 — Build the content

`MED-CNT-001` **Strip the YAML frontmatter block** (everything between the
leading `---` fences). None of it belongs in the Medium body.

`MED-CNT-002` **Lead the body with `# <title>`.** Medium's `title` request field
is used for SEO metadata only — the displayed title comes from a leading H1 in
the content. Omit it and the post shows up untitled.

`MED-CNT-003` **Absolutise every relative link and image.** Medium fetches
content from its own domain, so `/posts/az-02-foo` and `./images/x.png` both
break. Rewrite to `https://drunkcoding.net/...`. Astro `<img>`/component syntax
and MDX-style embeds do not render on Medium — replace them with plain Markdown
images or drop them, and note what was dropped in the final report.

`MED-CNT-004` **Leave the empty `## Table of Contents` heading out.** It is an
AstroPaper convention filled in by the blog app; on Medium it renders as an empty
section.

## Step 3 — Post the draft

`MED-API-001` Build the payload as a file, then POST it:

```bash
curl -sS -X POST "https://api.medium.com/v1/users/$MEDIUM_USER_ID/posts" \
  -H "Authorization: Bearer $MEDIUM_TOKEN" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

`payload.json` field mapping, from the post's frontmatter:

| Payload field | Value |
| --- | --- |
| `title` | frontmatter `title` (SEO only — the H1 in `content` is what readers see) |
| `contentFormat` | `"markdown"` |
| `content` | `# <title>` followed by the frontmatter-stripped body |
| `canonicalUrl` | `https://drunkcoding.net/posts/<slug>` |
| `tags` | frontmatter `tags`, at most 5 |
| `publishStatus` | `"draft"` |

`MED-API-002` **`canonicalUrl` is mandatory.** Republishing without it makes
Medium compete with drunkcoding.net for the same content in search results.
Never omit it, and never point it at the Medium post itself.

`MED-API-003` **`publishStatus` is always `"draft"`.** A human reviews the draft
on Medium and publishes it. Never send `"public"` — not even when asked to
"publish", which in this workflow means "get it onto Medium ready to go".

`MED-API-004` **At most 5 tags.** Medium rejects more. When the post carries
more, keep the 5 most specific and report which were dropped.

## Step 4 — Report back

`MED-RPT-001` Report the Medium draft URL (from the response `data.url`), the
canonical URL that was set, the tags that were sent, and anything that was
dropped or rewritten (images, embeds, extra tags). A silent rewrite is a defect —
the author needs to know what changed before publishing.

`MED-RPT-002` **Never commit anything to the blog repo.** This skill is
read-only against `hbd.astro-paper`. If the post needs a `canonicalURL` or any
other edit on the blog side, raise it as a separate request.

## Failure handling

- `401` / `403` — token invalid or revoked. Stop, report, do not retry.
- `400` — payload rejected. Quote the API's error message verbatim; the common
  causes are more than 5 tags and a malformed `canonicalUrl`.
- `429` — rate limited. Report it; do not loop.
- Any other non-2xx — report the status and body verbatim rather than guessing.
