---
name: astro-paper-blog-conventions
description: >-
  Authoring conventions for the AstroPaper blog at github.com/baoduy/hbd.astro-paper
  (drunkcoding.net) — where posts live, the Markdown filename pattern, the exact
  frontmatter schema (required vs optional fields), and the house writing voice
  taken from the repo's own .prompts/writing.prompt. Use whenever writing,
  editing, or reviewing a blog post for that repo. Every rule carries a stable
  rule-id.
category: content
triggers:
  - blog post
  - astro-paper
  - drunkcoding
  - frontmatter
  - blog writing
---

# AstroPaper Blog Conventions (baoduy/hbd.astro-paper)

Authoring rules for the AstroPaper blog that powers **drunkcoding.net**. Derived
from the live repo `github.com/baoduy/hbd.astro-paper`: the content collection
schema (`src/content.config.ts`), the existing 45 posts in `src/data/blog/`, and
the author's own writing guide at `.prompts/writing.prompt`. This skill covers
the **content layer** (where a post goes, its metadata, its voice). Git and PR
mechanics live in `sdlc-gitflow` — do not duplicate them here.

## Location & filename

- `BLOG-LOC-001` **Posts live in `src/data/blog/`.** The collection loader globs
  `**/[^_]*.md` under that path. A `.md` file anywhere else is not a post; a file
  whose name starts with `_` is intentionally excluded — don't use a leading
  underscore for a real post.
- `BLOG-LOC-002` **Filename is `<series>-NN-<slug>.md`.** Existing series
  prefixes: `az` (Azure/Pulumi), `dotnet` (.NET), `ks` (Kubernetes), `tools`
  (utilities). `NN` is the zero-padded order within the series (`az-00`, `az-01`).
  A standalone post outside any series may use a plain `<slug>.md`; a genuinely
  new series starts its own prefix — confirm the prefix with the requester before
  inventing one.
- `BLOG-LOC-003` **Slug is lowercase-kebab, no spaces.** Match the URL you want:
  the post is served at `/posts/<filename-without-.md>`. In-repo cross-links use
  that path, e.g. `[Day 02](/posts/az-02-...)`.

## Frontmatter schema

YAML frontmatter between `---` fences at the top of every post. Fields (from
`src/content.config.ts`):

- `BLOG-FM-001` **Required: `title`, `description`, `pubDatetime`.** Omitting any
  fails the build. `pubDatetime` is an ISO datetime, e.g.
  `2026-08-11T12:00:00Z`. `title` is a quoted string; a series index post often
  prefixes a tag like `"[Az] ..."`. `description` is a full 1–3 sentence summary
  used for SEO and cards — not a placeholder.
- `BLOG-FM-002` **`author` defaults to "Steven Hoang".** Only set it to override.
- `BLOG-FM-003` **`tags` defaults to `["others"]`.** Provide a real list when the
  post fits existing tags (`AKS`, `Helm`, `CI/CD`, `Pulumi`, `dotnet`, …). Reuse
  existing tag spellings rather than coining near-duplicates.
- `BLOG-FM-004` **Optional flags:** `featured` (bool), `draft` (bool),
  `modDatetime` (ISO or null — set when materially editing a published post),
  `ogImage` (image path or URL), `canonicalURL`, `hideEditPost`, `timezone`.
- `BLOG-FM-005` **Ship new posts with `draft: true`.** The post stays hidden
  until a human reviews the PR and flips it to `false` on/after merge. Never
  publish (`draft: false` or omitted) an unreviewed post.

Minimal valid frontmatter:

```yaml
---
title: "A Clear, Specific Post Title"
description: "One to three sentences summarising what the reader will learn and why it matters."
pubDatetime: 2026-08-11T12:00:00Z
tags:
  - Pulumi
  - Azure
draft: true
---
```

## Writing voice

From the repo's `.prompts/writing.prompt` — the author's standing instruction for
every post:

- `BLOG-VOICE-001` **Upper-intermediate English.** Write so a junior developer or
  second-language reader can follow. Prefer short sentences and plain words over
  jargon; explain a term the first time it appears.
- `BLOG-VOICE-002` **Use "we"/"our", not "you".** Address the reader as a
  companion walking through the steps together, not as someone being instructed.
- `BLOG-VOICE-003` **Professional but accessible tone.** Technical and correct,
  never stiff or academic.
- `BLOG-VOICE-004` **Leave the Table of Contents empty.** Include a `## Table of
  Contents` heading with no body — the blog app auto-generates the list. Do not
  hand-write TOC entries.
- `BLOG-VOICE-005` **Structure like the existing posts.** Open with a `##
  Introduction` that states what the post covers and who it's for, then
  `## Table of Contents`, then the body in `##` sections. For a series index,
  list each day as a bold linked line plus a one-paragraph summary.

## Self-check before opening the PR

A post is ready only if: it's under `src/data/blog/` with a `<series>-NN-<slug>.md`
name; `title`/`description`/`pubDatetime` are present and real; `draft: true`;
`## Table of Contents` is present and empty; voice is "we"/"our" throughout; and
every in-repo link uses `/posts/<slug>`. If any fails, fix before the PR.
