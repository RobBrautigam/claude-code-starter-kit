---
name: daily-review
description: Lightweight daily check-in that surfaces today's scheduled projects and gets you moving. 2 minutes, not 20. Use at the start of any work session, when the user asks "what should I work on", "what's on deck", "morning check", "start my day", "today's schedule", "what's scheduled", or any variation of daily planning. If it's the first conversation of the day, suggest this skill proactively.
triggers:
  - /daily-review
  - what should I work on today
  - daily planning
  - plan my day
  - what's on deck
  - morning check
  - start my day
  - today's schedule
  - what's scheduled today
---

# Daily Review

Quick check-in to surface today's projects. The weekly review already made the hard decisions - this just gets you moving.

The skill is task-tracker-agnostic. Substitute the "task source" steps with whatever you actually use (filesystem README scan, ClickUp, Linear, GitHub issues, a SQL query - same flow shape).

---

## Pre-flight: load three lists

Pull three datasets:

1. **Today's scheduled projects** - projects with `target_date == today` and status in {todo, in_progress}.
2. **Overdue items** - projects with `target_date < today` and status in {todo, in_progress}.
3. **In-progress (any schedule)** - everything currently `in_progress` regardless of target_date.

Filter by repo scope when applicable so cross-repo work in the same tracker doesn't leak in.

---

## Flow

### 1. Present the day

Show today's projects in a friendly format:
- Number, title, brief description, any initiative / phase context you have.
- Flag overdue items from previous days.
- Note anything currently in-progress that's NOT on today's list (potential context-switch cost).

### 2. Quick adjustments

The user can:
- *"Swap 1 and 2"*
- *"Skip the third one today"*
- *"I'm in content mode, pull something from content pipeline"*
- *"Reschedule X to tomorrow"*

Make the changes in the task tracker. Don't re-plan the whole week - that's the weekly review's job.

### 3. Pick and go

Once the user picks a project (or accepts #1), end the skill. Do NOT auto-invoke project-manager or brainstorming - let the user start the project session however they normally do.

---

## Tone

Brief and energizing. Like a quick standup with yourself. Not a planning session.

## Rules

- No full pipeline analysis - that's the weekly review.
- No reordering the whole queue - that's the weekly review.
- Don't auto-start project sessions.
- If nothing is scheduled for today, suggest running the weekly review.
- Filter by repo when relevant - this skill is meant to be repo-scoped, not global.
