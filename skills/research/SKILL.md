---
name: research
description: Context-aware deep research, free sources first (GitHub, plain fetches, Claude Code's built-in web search), with an optional paid search API only when the free sources fail. Use this skill whenever the user asks to research any topic, investigate a market, evaluate tools or software, explore pricing models, competitive intelligence, hiring practices, content strategy, AI tooling, agency operations, or anything requiring synthesized multi-angle knowledge beyond a basic search. Also triggers on "look into", "find out about", "dig into", "what do you know about", "investigate", "research for me", "get me intel on", "help me understand the landscape of", "what are people doing with", "how does X work in the context of". If there is any chance this skill applies, invoke it - vague questions are especially good candidates since they benefit most from structured research.
---

# Research

Deep, context-aware research. Every research task reads available project context first, runs multi-angle queries through the free sources first, synthesizes findings through the user's business lens, saves a full report with its sources, and delivers a tight summary. The rule behind it is `rules/research-first.md`.

## Setup

Nothing to install for the default path: it uses the GitHub CLI (`gh`), plain web fetches and
Claude Code's built-in web search.

Optional, for when the free sources come back thin: the bundled Perplexity script (a paid API,
billed per call). Get a key at https://www.perplexity.ai/settings/api and add it to your
environment (`export PERPLEXITY_API_KEY=pplx-...`) or to `~/.claude/.secrets.env`. The script
searches a few standard locations; see the script for the order.

---

## Step 1 - Understand the question

Before touching any research tool, make sure you know what you're actually looking for.

- If the request is vague or could mean multiple things, ask 1-2 focused clarifying questions before proceeding. One round of clarification is worth more than a well-researched answer to the wrong question.
- Identify which domain the question belongs to:
  - Business operations (revenue, pricing, products, clients, ops)
  - Personal brand / content strategy (positioning, authority, social platforms)
  - Team and hiring (contractors, workflows, systems)
  - Market and competitive (what others in the space are doing)
  - Tech and tooling (AI, automation, software evaluation)
  - Other (flag what you think it is)
- State the refined research question back in one sentence before moving on. This anchors the research and catches misalignment early.

---

## Step 2 - Load context

Read available context before formulating a single query. This is what separates useful research from generic information dumps.

**If the repo has a `context/` directory** (or similar location for personal / business context), read relevant files. Common files:

- `context/me.md` - who the user is, role, priorities
- `context/work.md` - business details, products, pricing, revenue, tech stack
- `context/team.md` - team structure, key people, communication channels
- `context/current-priorities.md` - current focus areas
- `context/goals.md` - revenue targets, business / brand goals

**If no `context/` directory exists:**
- Read `CLAUDE.md` for project-level context.
- Use whatever the current conversation has surfaced about the user's situation.
- Ask 1-2 clarifying questions about the user's business context if the research needs to be specific.

**Also scan (if available):**
- Any `projects/*/README.md` files that seem relevant to the topic.

**Then summarize** 2-4 bullets on what's most relevant to this specific question - this becomes the context that shapes every query. Be concrete: current revenue, specific products, active priorities. Generic context produces generic results.

---

## Step 3 - Formulate queries

Break the topic into 2-4 distinct angles. Each angle should be a separate query so you get depth from multiple directions, not one sprawling question that gets a shallow answer.

**Typical angle breakdown:**
- Market landscape - what exists, who the players are, how it's structured
- Competitive positioning - what similar companies / people are doing, how they're winning
- Tactical implementation - how to actually do the thing, best practices, pitfalls
- Pricing / benchmarks / data - numbers, ranges, industry standards

**Embed context into every query.** Don't ask *"what are best practices for AI agency pricing?"* Ask *"what are pricing models and structures used by AI-powered B2B agencies doing $100k-$200k/month in the personal branding and podcast booking space?"* The specificity is the point.

---

## Step 4 - Run the queries, free sources first

One pass per query angle. Move down the list only when the source above has failed for that angle:

1. **GitHub through `gh`** for anything about code, tools or open source: `gh search repos "<topic>" --sort stars`, then read the top READMEs (`gh api repos/<owner>/<repo>/readme -H "Accept: application/vnd.github.raw"`), noting stars, last commit and license.
2. **Claude Code's built-in web search and plain fetches** for everything else. Read the pages in full, not the snippets.
3. **The optional paid script**, only when the free passes came back thin, and only after telling the user which angle failed and that the next call costs money. Set a ceiling on the number of calls first.

For the paid script, pass the context summary from Step 2 as a system prompt (`sonar` by default, `sonar-pro` for complex synthesis):

```bash
python ~/.claude/skills/research/scripts/perplexity_research.py \
  --query "your query here" \
  --model sonar \
  --system-prompt "You are a research assistant for <user role + business>. <2-4 context bullets>. Filter your answer to this context."
```

**Sources rule:** a claim the report states as fact carries three independent sources; anything with fewer is labeled ("single source: the vendor's pricing page"). Date every source you read.

---

## Step 5 - Synthesize

With all the responses in hand, now do the actual thinking.

- Combine findings across all query angles - look for patterns, contradictions, and gaps.
- Cut anything generic or obvious - if the user already knows it, don't repeat it.
- Actively connect findings to the context you loaded in Step 2.
- Identify what's immediately actionable vs interesting-but-not-now.
- Flag anything that contradicts assumptions or surfaces a risk worth noting.

---

## Step 6 - Save report

Write the full report to `research/YYYY-MM-DD-topic-slug.md`. Use this template:

```markdown
# Research: [Topic]

*Date: YYYY-MM-DD | Sources: free (GitHub, web) or paid (name it)*

## Summary
- [3-5 bullet takeaways - the most important things to know]

## Key Findings
[Detailed synthesis of what the research uncovered, organized by theme or query angle]

## Business Implications
[Specific implications for the business - products, pricing, positioning, ops, clients. Adapt heading if context differs.]

## Personal Implications
[Implications for the user's role, decisions, time, leadership, or personal development]

## Content Angles
[2-4 specific content ideas or angles this research suggests. Skip if user has no content / brand focus.]

## Connections to Current Priorities & Projects
[How this connects to active work - be explicit about which priorities / projects are affected. Skip if no project context available.]

## Next Steps
[2-4 concrete actions worth taking, ordered by priority]

## Sources
[Every source with its link and the date you read it. Mark single-source claims.]
```

---

## Step 7 - Present summary

After saving the report, give the user the short version:

- 3-5 bullet takeaways - lead with the "so what?", the most actionable or surprising insight.
- One sentence on what this means for the user / business specifically.
- Where the report lives: `research/YYYY-MM-DD-topic-slug.md`.
- 2-3 next steps, concrete and ranked.

Keep it tight. The full report exists for when the user wants to go deeper - the summary should be scannable in 30 seconds.
