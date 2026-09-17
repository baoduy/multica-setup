---
name: codegraph
description: >-
  Set up and use CodeGraph for surgical code understanding — one tool call
  returns exact symbols, call paths, and blast radius instead of grep/read
  loops. Covers indexing a repo (`codegraph init`), verifying the index, and
  query patterns. Use when exploring unfamiliar code, tracing execution flows,
  analyzing impact of changes, answering architecture questions, or when
  codegraph_explore returns nothing and the index needs building.
category: software-development
triggers:
  - codegraph
  - code graph
  - code index
  - semantic code search
  - code exploration
---

# CodeGraph — Semantic Code Intelligence

[CodeGraph](https://github.com/colbymchenry/codegraph) is a knowledge graph of every symbol, call edge, and dependency in a codebase. It hands you exact code you need in **one call** — no grep/glob/read loop. CLI reference below verified against **v1.2.0**.

## When to Use

- **Understanding unfamiliar code** — "how does X work", "how does X reach Y"
- **Tracing execution flows** — URL → handler → service → database
- **Impact analysis** — "what breaks if I change this symbol?"
- **Architecture questions** — how modules communicate, layering, dead code
- **Finding symbols** — "where is UserService defined?"

**Do NOT use when:**
- There is no index and nobody asked you to build one — indexing is user's decision; fall back to grep/read
- You need **live** content of a just-edited file (pending sync) — staleness banner says so; use `Read`

The MCP server is registered once at user level and inherited automatically — if `codegraph_explore` is missing from your tool list, that is a user-level install issue, not per-project. What IS per project is the index.

## Gotcha that breaks fresh checkouts

**`.codegraph/` is gitignored, so a fresh checkout never has a usable index.** Repos that "have CodeGraph set up" commit only `.codegraph/.gitignore` — the directory **exists** while the database does **not**, so any `if [ -d .codegraph ]` check passes and you query an empty index. On ephemeral runtimes (CI, scheduled agents, fresh `multica repo checkout`) this is the normal case.

**Verify with `codegraph status`, never with directory existence:**

```bash
codegraph status . 2>/dev/null | grep -q "Nodes:" || codegraph init .
codegraph status .      # confirm Nodes / Edges are non-zero
```

Indexing is cheap against any multi-file analysis it replaces (~2 min on a 1,174-file .NET solution). Incremental update: `codegraph sync`. Never commit the index or include it in a PR. CLI absent: `npm i -g @colbymchenry/codegraph`.

## MCP Tool: `codegraph_explore`

**Primary** tool — answers almost any question in one call. Returns relevant symbols' verbatim source grouped by file, call paths between them (including dynamic-dispatch hops grep can't follow), and a blast-radius summary.

Query by **concept**, not just filename:

- `"How does the auth middleware work?"`
- `"Trace the request flow from the login endpoint to the database"`
- `"What is affected if I change PaymentProcessor.process()?"`

Pass `projectPath` to query any indexed project in a monorepo or second repo.

`explore` also reports **"no covering tests found"** per symbol — useful for weighting severity in reviews: an untested symbol with a defect outranks a tested one.

## CLI reference (when MCP is unavailable; output matches MCP)

| Command | Purpose | Key flags |
|---|---|---|
| `codegraph explore <query>` | Source + call paths + blast radius | — |
| `codegraph node <symbol\|file>` | One symbol's source + caller/callee trail | — |
| `codegraph query <search>` | Search symbols by name | `--kind`, `--limit`, `--json` |
| `codegraph callers <symbol>` / `callees <symbol>` | What calls this / what this calls | `--limit`, `--json` |
| `codegraph impact <symbol>` | Blast radius | `--depth`, `--json` |
| `codegraph affected [files...]` | Tests affected by changes | `--stdin`, `--depth`, `--json` |
| `codegraph status [path]` | Index statistics | — |
| `codegraph init [path]` | Initialize + build index | `--force`, `--verbose` |
| `codegraph index [path]` | Full re-index | `--force`, `--quiet` |
| `codegraph sync [path]` | Incremental update | — |
| `codegraph unlock [path]` | Clear stale lock | — |

## Tuning with `codegraph.json`

Optional, at repo root. Defaults already exclude `node_modules`, `dist`, `build`, files >1 MB, and everything in `.gitignore`. For .NET solutions, excluding generated code sharpens results and cuts index time — EF migrations especially:

```json
{ "exclude": ["**/Migrations/**", "**/GeneratedDtos/**", "**/obj/**", "**/bin/**"] }
```

Weigh it first: excluding a directory also removes it from blast-radius output, so keep anything you need impact analysis over.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Empty results but `.codegraph/` exists | No DB — gitignored index. `codegraph init .` |
| Stale lock blocks sync | `codegraph unlock [path]` |
| Missing symbols after edits | `codegraph sync`, then `codegraph status` |
| MCP transport errors on WSL2 / network share | `CODEGRAPH_NO_DAEMON=1`, or move to local Linux filesystem |
| Index huge / slow | Add `exclude` patterns in `codegraph.json` |

## Pitfalls

1. **Testing `[ -d .codegraph ]` instead of `codegraph status`.** Directory is committed; index is not.
2. **Grep/read loops after CodeGraph already answered.** Trust results — one call returned source; treat it as already read.
3. **Querying by filename instead of concept.** `explore` is strongest with conceptual queries.
4. **Ignoring staleness banner.** After an edit, `Read` pending files directly.
5. **Indexing a repo nobody asked you to index.** Default is still to fall back to grep/read.
6. **Committing `.codegraph/`** or including it in a PR.
7. **Silently degrading to grep when indexing fails.** Say index is missing, then fall back — conclusions about layering, dead code and blast radius are materially weaker without a call graph.
