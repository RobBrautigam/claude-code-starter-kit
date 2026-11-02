---
name: explore-codebase
description: Navigate and understand a large codebase's structure using the code-review-graph knowledge graph (callers, callees, communities, flows). Use on repos over ~100 files when "where does X live / what connects to Y" would take many greps. For small repos or single-symbol lookups, use Grep/Glob/Explore instead.
---

# Explore Codebase (code-review-graph)

Use the `code-review-graph` MCP knowledge graph to explore and understand a codebase structurally - callers, callees, imports, communities, and execution flows - instead of grepping blind.

## When NOT to use (read first)

- **Repos under ~100 files** - plain Grep/Glob/Explore is faster; the graph adds nothing.
- **Single-symbol lookups** ("where is `foo` defined") - one Grep answers it.
- **Repos with no built graph and no time to build one** - see freshness below.

Reach for the graph when the question is *structural* and would otherwise take 3+ greps: "what's the architecture", "what are the major modules", "what calls into this subsystem", "trace the request flow".

## Freshness precondition (MANDATORY - do not skip)

A stale graph gives confident WRONG answers (e.g. "0 callers" after a refactor). Before trusting any graph answer:

1. Ensure a graph exists / is current for the repo: run `uvx code-review-graph update` (incremental) or `uvx code-review-graph build` (first time) from the repo root.
2. Run `detect_changes` (or `uvx code-review-graph detect-changes`) to confirm the graph reflects the working tree.
3. Only then trust caller/callee/impact answers.

If you cannot confirm freshness, treat graph output as a hint and verify with a Read.

## Steps

1. `list_graph_stats` / `uvx code-review-graph status` - overall metrics, languages, last-built commit.
2. `get_architecture_overview` - high-level community structure.
3. `list_communities`, then `get_community` for details on a module.
4. `semantic_search_nodes` - find specific functions/classes by meaning.
5. `query_graph` with `callers_of` / `callees_of` / `imports_of` - trace relationships.
6. `list_flows` / `get_flow` - understand execution paths.

## Tips

- Start broad (stats, architecture) then narrow to specific areas.
- `children_of` on a file lists its functions/classes; `find_large_functions` finds complexity hotspots.

## Trust boundary

Graph answers are advisory. Before any destructive action (delete, signature change, "this has no callers so I'll remove it"), confirm with a targeted Read of the actual code. The graph informs; the code decides.

See `rules/code-review-graph-usage.md` for the full usage policy (when to use it, the freshness law, and the trust boundary).
