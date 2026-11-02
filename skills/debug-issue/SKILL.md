---
name: debug-issue
description: Systematically trace and debug an issue using the code-review-graph knowledge graph (call chains, flows, impact radius, recent-change detection). Use on repos over ~100 files when tracing how a bug propagates. For small repos, use superpowers:systematic-debugging with plain Grep/Read.
---

# Debug Issue (code-review-graph)

Use the `code-review-graph` MCP knowledge graph to trace a bug through call chains and execution flows, and to check whether a recent change caused it. Pairs with `superpowers:systematic-debugging` (root-cause first, then fix).

## When NOT to use (read first)

- **Repos under ~100 files** - Grep/Read + systematic-debugging is faster.
- **The bug is already localized to one file/function** - just read it.

Reach for the graph when the bug spans modules, you don't know the entry point, or you suspect a recent change rippled into a distant failure.

## Freshness precondition (MANDATORY - do not skip)

A stale graph mis-attributes call chains and impact. Before trusting graph output:

1. `uvx code-review-graph update` (or `build` if none) from the repo root.
2. `detect_changes` to confirm the graph matches the working tree.
3. Then trust the call-chain / impact answers.

If freshness is unconfirmed, treat output as a lead and verify by reading the code.

## Steps

1. `semantic_search_nodes` - find code related to the symptom.
2. `query_graph` with `callers_of` / `callees_of` - trace the call chain around the suspect.
3. `get_flow` - see full execution paths through the suspected area.
4. `detect_changes` - check whether recent changes touched the suspect (recent changes are the most common cause of new bugs).
5. `get_impact_radius` on the suspect file - see what else is affected.

## Tips

- Check both callers and callees for full context.
- Use affected flows to find the entry point that triggers the bug.

## Trust boundary

The graph points you at suspects; it does not prove causation. Confirm the root cause by reading the code and reproducing, then write a failing test before fixing (per `superpowers:systematic-debugging` + `superpowers:test-driven-development`).

See `rules/code-review-graph-usage.md` for the full usage policy.
