# CodeGraph — Semantic Code Intelligence

[CodeGraph](https://github.com/colbymchenry/codegraph) is pre-built knowledge graph of every symbol, call edge, and dependency in your codebase. It hands agent exact code it needs in **one tool call** — no grep, glob, or file-reading loop.

## When to Use

- **Understanding unfamiliar code** — "how does X work", "how does X reach Y"
- **Tracing execution flows** — URL → handler → service → database
- **Impact analysis** — "what breaks if I change this symbol?"
- **Architecture questions** — how modules communicate, layering, dead code
- **Finding symbols** — "where is UserService defined?"

**Do NOT use when:**
- There is no index and nobody asked you to build one — indexing is user's decision, fall back to grep/read
- You need **live content** of file that was just edited (pending sync) — staleness banner tells you; use `Read` tool directly

## Gotcha that breaks fresh checkouts

**`.codegraph/` is gitignored, so fresh checkout never has usable index.** Repos "with CodeGraph set up" commit only `.codegraph/.gitignore` — directory **exists** while database does **not**, so any `if [ -d .codegraph ]` check passes and you query empty index. On ephemeral runtimes (CI, scheduled agents, fresh `multica repo checkout`) this is normal case.

**Verify with `codegraph status`, never with directory existence:**

```bash
codegraph status . 2>/dev/null | grep -q "Nodes:" || codegraph init .
codegraph status .      # confirm Nodes / Edges non-zero
```

Never commit index or include it in PR. Incremental update: `codegraph sync`.

## MCP Tool: `codegraph_explore`

**Primary** tool — answers almost any question in one call: relevant symbols' verbatim source grouped by file, call paths between them (including dynamic-dispatch hops grep can't follow), blast-radius summary.

Query by **concept**, not just filename:

- `"How does the auth middleware work?"`
- `"Trace the request flow from the login endpoint to the database"`
- `"What is affected if I change PaymentProcessor.process()?"`

Pass `projectPath` to query any indexed project in monorepo or second repo.

## CLI Equivalents (when MCP unavailable; same output)

| Command | Purpose |
|---------|---------|
| `codegraph explore "<query>"` | Same output as `codegraph_explore` MCP tool |
| `codegraph node <symbol>` | One symbol's source + callers |
| `codegraph query <search>` | Search symbols by name |
| `codegraph callers <symbol>` / `callees <symbol>` | What calls this / what this calls |
| `codegraph impact <symbol>` | Blast radius |
| `codegraph affected <files>` | Test files affected by changes |
| `codegraph status` | Index statistics |
| `codegraph init [path]` | Initialize + build index |
| `codegraph sync` | Force incremental update |

## Common Pitfalls

1. **Testing `[ -d .codegraph ]` instead of `codegraph status`.** Directory is committed; index is not.
2. **Grep/read loops after CodeGraph answered.** Trust results — one call returned source; treat it as already read, no `Read` needed.
3. **Querying by filename instead of concept.** `explore` works best with conceptual queries ("how does auth work").
4. **Ignoring staleness banner.** After edit, `Read` pending files directly for live content.
5. **Silently degrading to grep when index missing.** Say index is missing, then fall back — layering/dead-code/blast-radius conclusions are materially weaker without call graph.
