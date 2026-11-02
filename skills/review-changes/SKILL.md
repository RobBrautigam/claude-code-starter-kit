---
name: review-changes
description: Perform a risk-aware code review of a changeset using code-review-graph change detection, impact radius, affected flows, and test-coverage queries. Use on repos over ~100 files when reviewing a branch/PR diff that touches shared code. For small diffs, read the diff directly.
---

# Review Changes (code-review-graph)

Use the `code-review-graph` MCP knowledge graph to review a changeset by its blast radius and test coverage, not just the diff lines.

## When NOT to use (read first)

- **Repos under ~100 files** - read the diff directly.
- **A small, self-contained diff** (one file, no shared utilities) - read it.

Reach for the graph when the diff touches shared utilities, core modules, or anything with many dependents - where "what else does this affect" isn't obvious from the diff alone. Composes with `superpowers:requesting-code-review` and an independent adversarial review pass (e.g. `/codex:review` if you use the Codex plugin).

## Freshness precondition (MANDATORY - do not skip)

Review against a stale graph misreports impact and coverage. Before trusting output:

1. `uvx code-review-graph update` (or `build` if none) from the repo root.
2. `detect_changes` to confirm the graph reflects the branch under review.
3. Then trust impact/coverage answers.

## Steps

1. `detect_changes` - risk-scored change analysis for the diff.
2. `get_affected_flows` - execution paths the change touches.
3. For each high-risk function: `query_graph` pattern=`tests_for` - check test coverage.
4. `get_impact_radius` - full blast radius.
5. For any untested changes, suggest specific test cases.

## Output format

Group findings by risk (high/medium/low), each with:
- What changed and why it matters
- Test coverage status
- Suggested improvements
- Overall merge recommendation

## Trust boundary

The graph scores risk; it does not catch logic bugs, security flaws, or business-rule violations. Use it to FOCUS a human/AI review on the high-blast-radius areas - not to replace reading the high-risk code. Pair with a deeper adversarial review (e.g. `/codex:adversarial-review`) for changes touching data mutations, auth, migrations, or scheduled jobs.

See `rules/code-review-graph-usage.md` for the full usage policy.
