# Agent Fleets: Pick the Model and the Effort, Every Time

The moment you spawn more than about three subagents at once (a fan-out of Agent calls, a workflow,
a skill that runs its own fleet), cost becomes a design decision. A subagent with no model named
inherits the main session's model, which is usually your most expensive one. Fifty agents that
inherit it can burn a week of usage in one run.

## FORBIDDEN

- **A fan-out of more than about three agents without an explicit model on every one.** Never let a
  fleet inherit the session model: you switch models freely, and inheritance couples fifty agents'
  cost to whatever you last clicked.
- **The top-tier model as the fleet.** It is for the single hardest call, not for fifty file reads.
- **Leaving effort at its default in a fleet.** Mechanical stages get low effort.
- **Launching a large fan-out without saying, before it starts, how many agents on which model.**
- **A runaway left running.** If a fan-out turns out to be wrong, stop it at once; a background
  workflow keeps spending after you have noticed the mistake.

## REQUIRED: a wide cheap base, a narrow expensive tip

| Stage | Model tier | Effort |
|---|---|---|
| Read files, grep, extract into a fixed shape, mechanical transforms | the smallest, fastest tier | low |
| Summarize, merge, dedupe, classify, draft | the middle tier | low to medium |
| Adversarial checks, architecture calls, the final synthesis | the middle tier, or the top tier only where the judgment carries the result | medium to high |
| Anything the human named a model for | what they said | as asked |

Forty small readers feeding three mergers feeding one careful synthesis is right. Fifty of anything
expensive is wrong. State the plan in one line before launching: *"40 agents on the small tier at
low effort for the read, 3 on the middle tier for the merge."* If that sentence would embarrass you
on the bill, change it first.

## REQUIRED: size the context, not just the count

Most of a fan-out's cost is context, not output. Every agent re-reads what you hand it.

- Narrow the corpus with `grep` and `Glob` in the main conversation (free) before spawning readers.
- Batch files so each agent reads what it needs and no more; never hand an agent a large dump "for
  context" it will not use.
- Long-running sessions cost more on every turn, because each turn re-reads the growing transcript.
  End an arc's session and start a fresh one rather than letting one conversation grow for hours.

## REQUIRED: paid APIs only through a client with a ceiling

A fleet that calls a metered API (search, scraping, an LLM API) calls it through one client that
enforces a per-call cap and a ceiling for the whole run, never raw from each agent. A "within
reason" budget is stated as a number before launch.

## Why this rule exists

The intelligence is in the orchestration, never in the size of the fleet. A well-shaped fan-out
costs a slice of one usage window; a badly shaped one costs all of it and stops every other piece
of work you had planned.

Related: `graph-index-tool-adoption.md` (measure before adopting standing infrastructure).
