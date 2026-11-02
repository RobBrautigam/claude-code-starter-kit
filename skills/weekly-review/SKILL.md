---
name: weekly-review
description: Interactive weekly review and planning session. Curates the todo queue, assigns target dates, and audits in-progress projects. Run at least weekly. Use when the user says "weekly review", "plan my week", "review my projects", or at the start of a week. Also triggers on /weekly-review.
---

# Weekly Review

Interactive session to organize the project pipeline for the coming week. Curate the queue, assign target dates, audit anything stuck in-progress, promote backlog items.

Task-tracker-agnostic. Substitute the "load pipeline" step with whatever you actually use (filesystem scan, ClickUp, Linear, GitHub issues, a SQL query - same flow shape).

---

## Step 1: Gather pipeline state

Load four datasets:

1. **Todo queue** - projects currently in todo, ordered by queue position.
2. **In-progress** - projects currently in_progress, ordered by `updated_at` ascending (oldest = most stale).
3. **Backlog pool** - backlog projects, most recent first, capped at ~50.
4. **Active initiatives / strategic threads** - whatever long-running goals you organize work around.

Filter by repo scope when applicable.

Compute `days_stale = today - updated_at` for in-progress items.

---

## Step 2: Audit in-progress

For each in-progress item, ask:

- Is it genuinely active (worked on within the last 7 days)?
- Is it blocked? On what?
- Should it move back to todo (paused, but still committed)?
- Should it move to backlog (deprioritized)?
- Should it move to done (it's actually finished but never closed out)?

Anything in_progress >14 days without recent activity is almost certainly stale - flag it.

---

## Step 3: Promote from backlog

Look at the backlog pool. Anything that should graduate to todo this week?

Criteria for promotion:
- Aligned with active initiatives / strategic threads.
- Unblocked (dependencies cleared).
- Right size for the available bandwidth.
- Time-sensitive (deadline approaching).

Move them to todo and assign a queue position.

---

## Step 4: Curate the todo queue

Now the todo list is the actual queue for the week. Order it:

- Highest-impact / highest-leverage first.
- Cluster related items so context-switching is minimized.
- Account for initiative phase ordering - don't start phase 3 work while phase 1 is incomplete *within the same initiative*. Different initiatives are independent.

---

## Step 5: Assign target dates

Walk down the curated queue and assign a target date to each item. Spread items across the week to match capacity. Don't over-commit - empty days are fine; missed targets erode trust in the system.

---

## Step 6: Confirm and write

Show the user the final week plan in one table:

| # | Title | Status | Initiative | Target date | Notes |
|---|-------|--------|------------|-------------|-------|

User can adjust before you write to the tracker.

Then commit the changes (update target_date, queue_position, status as needed).

---

## Step 7: One-paragraph summary

End with a short summary:

```
Week of <date>:
- N projects scheduled
- Top focus: <one-line>
- Stale in-progress audited: <count>, <action taken>
- Promoted from backlog: <count>
- Outstanding risks: <one-line, or "none">
```

---

## Tone

Calmer than daily-review. This is the planning session - deliberate, thorough, but not bureaucratic. Aim for 15-25 minutes total.

## Rules

- Don't auto-start any project sessions.
- Don't reorder items the user hasn't asked you to reorder.
- Be honest about staleness - call out anything that's been in_progress for weeks.
- Empty days in the week are acceptable; over-scheduling is a planning anti-pattern.
- One project per day per slot is plenty if the projects are non-trivial.
