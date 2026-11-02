---
name: refactor-safely
description: Plan and execute a refactor using the code-review-graph dependency analysis (rename previews, dead-code detection, impact radius, affected flows) before touching code. Use on repos over ~100 files for renames/moves/decomposition that ripple across files. For local single-file refactors, just edit and run the tests.
---

# Refactor Safely (code-review-graph)

Use the `code-review-graph` MCP knowledge graph to see the full blast radius of a refactor BEFORE making changes - every rename site, every dependent, every affected flow.

## When NOT to use (read first)

- **Repos under ~100 files** - your editor + Grep find every call site fast enough.
- **A refactor contained to one file** - just edit it and run the tests.

Reach for the graph for cross-file renames, moving a symbol between modules, deleting code you believe is unused, or decomposing a large function with many callers.

## Freshness precondition (MANDATORY - do not skip)

A stale graph is especially dangerous for refactors - "dead code" that the graph missed a caller for, or a rename that skips a site, breaks the build or prod. Before trusting any refactor analysis:

1. `uvx code-review-graph update` (or `build` if none) from the repo root.
2. `detect_changes` to confirm the graph matches the working tree.
3. Then trust rename/dead-code/impact answers.

## Steps

1. `refactor_tool` mode=`suggest` - community-driven refactoring suggestions.
2. `refactor_tool` mode=`dead_code` - find unreferenced code.
3. For renames: `refactor_tool` mode=`rename` - preview ALL affected locations before applying.
4. `apply_refactor_tool` with the refactor_id - apply the rename across sites.
5. After changes: `detect_changes` to verify the refactoring impact landed as expected.

## Safety checks

- Always preview before applying (rename mode gives an edit list - review it).
- Run `get_impact_radius` before any major refactor.
- Run `get_affected_flows` to ensure no critical execution paths break.
- `find_large_functions` identifies decomposition targets.

## Trust boundary

NEVER delete code the graph calls "dead" without a confirming Read + a test run. The graph can miss dynamic dispatch, reflection, string-based imports, and cross-language call sites. Dead-code detection is a strong hint, not proof. Run the test suite after every refactor and confirm green before committing (per `superpowers:verification-before-completion`).

See `rules/code-review-graph-usage.md` for the full usage policy.
