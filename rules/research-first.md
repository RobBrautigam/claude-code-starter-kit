# Research First, Free Doors First

Before any build, a research pass sized to the build. Someone has almost always solved most of
your problem already, and ten minutes of looking beats a day of reinventing it worse.

## The pass, sized to the build

| Build size | The research pass |
|---|---|
| A small change (a helper, a config, a fix) | Search GitHub for the pattern: `gh search repos "<topic>" --sort stars`, then read the top results' stars, last commit date and license |
| A page, a workflow, a feature | The `research` skill: several angles, each read in full, findings written to a dated file |
| A system or a product | The same, plus the official docs of every service involved, read whole, and a short written comparison before the first line of code |

Every build prompt you write for a session (or a subagent) names its research step first: what to
search, which sources, and any spending limit. A build prompt without one is incomplete.

## Free doors first, paid per call last

Use the sources in this order, and move down only when the one above has failed on that source:

1. The GitHub API through `gh` (search, metadata, READMEs, file contents).
2. A plain web fetch, and Claude Code's built-in web search.
3. A headless browser fetch for pages that need JavaScript.
4. Tools you already pay a flat subscription for.
5. A paid-per-call API (a search API, a scraping API, an LLM API). Name the source and why the free
   doors failed before you spend, and set a ceiling for the whole run before the first call.

## Claims carry their sources

- A claim reported as a fact carries three independent sources. Fewer than three is labeled
  ("single source: the vendor's pricing page").
- Several outlets repeating one press release is one source, not several.
- A dated source is dated in the write-up ("pricing page, read 2026-03-14"), because prices, limits
  and APIs move.

## Reuse before you write

When the research is done, pick the cheapest thing that does the job, in this order: what the repo
already has, the language's standard library, a built-in platform feature, a package you already
installed, a well-maintained new package, and only then new code. Thoroughness belongs in the guards
(validation, error handling, tests), never in the size of the mechanism.

## Why this rule exists

Agents start typing by default. The habit that separates a good build from a fast one is the five
minutes spent finding out what already exists, what it costs and what broke for the last person who
tried. Free sources first keeps the habit from becoming a bill.

Related: the `research` skill, `best-of-best-modeling.md`.
