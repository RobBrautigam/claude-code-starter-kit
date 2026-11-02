# code-review-graph: When and How to Use the Code Knowledge Graph

`code-review-graph` is an MCP server (`uvx code-review-graph serve`) that builds a structural knowledge graph of a codebase - functions, classes, imports, call sites, communities, execution flows, test coverage - and answers structural questions (callers, callees, impact radius, change risk) far cheaper than repeated Grep/Read. Treat it as your committed global code-navigation memory.

It pairs with four skills in this kit. This rule is the shared policy they all point back to.

## The four skills that drive it

- `explore-codebase` - understand structure (architecture, communities, callers/callees, flows)
- `debug-issue` - trace a bug through call chains + recent-change detection
- `refactor-safely` - rename/dead-code/impact preview before touching code
- `review-changes` - risk-scored review of a changeset by blast radius + test coverage

## When to use the graph

- Repos **over ~100 files** where "where does X live / what touches Y / what breaks if I change this" would take 3+ greps.
- Impact / caller-chain / execution-flow questions.
- Reviewing a diff that touches shared utilities or core modules.

## When NOT to use it (default to Grep/Glob/Explore)

- Repos **under ~100 files** - plain search is faster; the graph adds nothing (on tiny corpora the structural benefit is near zero).
- Single-symbol lookups ("where is `foo` defined").
- A change contained to one file you can just read.

Do not reflexively open `explore-codebase` on every repo. Small repos, config repos, and single-file questions are Grep/Read territory.

## The freshness law (the one real risk - read this)

**A stale graph gives confident WRONG answers.** "This function has 0 callers" against a graph built before a refactor will get live code deleted. Mitigation, mandatory before trusting any caller/impact/dead-code answer:

1. `uvx code-review-graph update` (incremental) or `build` (first time) from the repo root.
2. `uvx code-review-graph detect-changes` (or the `detect_changes` MCP tool) to confirm the graph matches the working tree.
3. Only then trust structural answers. If you cannot confirm freshness, treat output as a hint and verify with a Read.

`code-review-graph watch` / commit hooks can keep a graph fresh automatically. If you run multiple Claude conversations on the same repo, weigh `--watch` against the concurrent-session hazards in `rules/concurrent-sessions.md` - building/updating on demand is the safer default.

## Trust boundary

Graph output is **advisory**. It does not catch logic bugs, security flaws, or business-rule violations, and it can miss dynamic dispatch, reflection, and string-based imports. Before any destructive action (delete, signature change, "no callers so remove it"), confirm with a targeted Read + a test run. Use the graph to FOCUS review on high-blast-radius areas, not to replace reading the risky code. Pair it with a deeper adversarial review for high-risk surfaces (data mutations, auth, migrations, schedulers).

## Language coverage

The graph parses many languages via Tree-sitter - Python, TypeScript, TSX, JavaScript, SQL, bash, PowerShell among them. It works on backend and frontend code alike; no language scoping needed for mixed repos. Run `uvx code-review-graph status` after a build to confirm which languages it picked up for your repo.

## Operational notes

- Register the MCP server at **user scope** (in `~/.claude.json`) so it's available in every session, every repo, with no per-repo `.mcp.json`.
- It is **lazy**: the `serve` process idles until a graph is built and a tool is called. The expensive step is the explicit `build`.
- A health check (`claude mcp list`) can show "Failed to connect" on a cold `uvx` resolve; once warm + a graph exists, it shows "✓ Connected". Its tools load at session start, so after first registration they're available the next session.
- The graph store lives outside the repo (under code-review-graph's own cache), so it does not pollute git - no `.gitignore` changes needed.

## Related

- `rules/concurrent-sessions.md` - why not to enable `--watch` globally when running parallel conversations.
- This rule has the same "prefer this tool, here's exactly when not to" shape as a tool-selection rule: the discipline is knowing when the graph earns its cost and when plain search wins.
