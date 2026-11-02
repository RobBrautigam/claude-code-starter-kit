---
name: project-scaffolder
description: Scaffold new projects end-to-end from minimal input. Creates the project folder, writes a rich README with origin brief, definition of done, and a copy-paste starter prompt for future sessions. Triggers on "start a new project", "create a project", "add this as a project", "scaffold project", "new project for", or any natural language about creating a new project entry. Supports batch creation when given multiple projects at once.
---

# Project Scaffolder

Creates fully scaffolded projects from minimal input. One invocation generates the folder, writes a rich README, and optionally inserts a row into your task tracker if you use one.

The skill is filesystem-first. The README it generates carries enough context that a future Claude Code session can pick the project up cold without needing any task tracker.

## What "scaffolding" means here

A scaffolded project produces this on disk:

```
projects/<slug>/
├── README.md     ← rich context: description, origin brief, definition of done, starter prompt
├── plan.md       ← empty stub, filled in by superpowers:brainstorming + writing-plans
└── report.md     ← empty stub, filled in by the ship skill at session close
```

The README is the load-bearing artifact. Everything else builds on it.

---

## When to invoke

- User says "start a new project", "create a project", "add this as a project", "scaffold project", "new project for X", "let's build Y", "I need a tool that does Z", or any near-equivalent.
- The `project-manager` skill calls this when a multi-step build starts and no project folder exists for the named slug.
- The `session-types` rule's Ad-Hoc Build flow routes here automatically.
- The user lists multiple projects at once (e.g., "scaffold these three: A, B, C"). Use batch mode.

## When NOT to invoke

- One-sentence bug fixes. Branch + fix + push + ship is faster than scaffolding ceremony.
- Strategy / planning conversations with no buildable output.
- Pure exploratory questions ("how does X work?", "what do you think about Y?").
- Updating or renaming an existing project. That's an edit, not a scaffold.

If genuinely ambiguous (could be a quick fix or a project), ask once: *"This could go either way - want me to scaffold a project for this, or just handle it inline?"*

---

## Input

- **Minimum:** Project name + one-line description.
- **Optional:** category (project | task), size (small | medium | large), parent project slug if it's a spin-off from an active session.
- **Batch:** Accepts a list of projects in one invocation.

### Spin-off mode (the most important variant)

The most common way this skill gets invoked is mid-project. The user is working on Project A, an idea surfaces that's worth pursuing but doesn't belong in Project A's scope, and the right move is to scaffold it now (not "I'll remember to come back to this" - you won't). Spin-off mode captures the lineage so the new project records where it came from.

When invoked with a parent project context:

- The new project's `Session Context` block in the README records the parent project's title and slug, the date, and the verbatim quote or paraphrase that triggered the spin-off.
- The new project lives in `projects/<spin-off-slug>/` alongside its parent, not nested under it. Lineage is a metadata relationship, not a folder hierarchy.
- The new project inherits status `backlog` (never `in_progress` or `todo` - spin-offs are captured, not started).
- The new project gets its own `starter_prompt`, written so a future session can resume the spin-off without needing context from the parent session. The starter_prompt references the parent project's README as background reading but doesn't depend on the parent session's conversation history.

Spin-off mode is what makes mid-project ideation safe. The cost of scaffolding is 30 seconds; the cost of losing a good idea is whatever the idea was worth.

## Defaults (non-negotiable)

- status: `backlog` - never `in_progress` at creation. Weekly review is the gate to active work.
- category: `project` unless the input clearly describes a one-off task.
- size: infer from scope (small = 1 session, medium = 2-3 sessions, large = 4+).
- source: `claude` (or whatever marker your tracker uses for AI-created entries).

Do not accept status overrides at scaffolding time. Capture to backlog first, organize during weekly review.

---

## Step 1 - Parse input

Extract the title and description from the user's request. Generate the slug:

- Lowercase everything
- Replace spaces with hyphens
- Strip special characters (`'`, `&`, `?`, `!`, `:`, etc.)
- Example: *"Content Repurposing Skill"* → `content-repurposing-skill`

Infer category from context. Default `project` unless the input is clearly a one-off task (a single discrete action, no phases, no sub-tasks).

Infer size:
- **small** - fits in one session, no sub-tasks, no architectural decisions
- **medium** - 2-3 sessions, some sub-tasks, requires brainstorming + plan
- **large** - 4+ sessions, multiple phases, multiple sub-projects

---

## Step 2 - Check for duplicates

Two parallel checks:

**2a. Folder check:** Does `projects/<slug>/` already exist? Use Glob.

**2b. Tracker check (optional):** If you use a task tracker (database, ClickUp, Linear, Jira, GitHub issues), query it for existing projects with the same slug or title.

If either source returns a match, STOP. Show the existing project's location and details. Do not create a duplicate. Ask the user whether to:
- Open the existing project instead
- Pick a different slug for the new one
- Cancel

---

## Step 3 - Generate rich context (MANDATORY)

This is the heart of the skill. Bare-minimum READMEs that just say "Project X - does Y" are the failure mode this skill exists to prevent. Every scaffolded project gets the full context block.

Produce these four blocks of content **before writing any file:**

### 3a. `origin_brief` - the full project context

Format as markdown. This becomes the bulk of the README.

```markdown
# {Title}

{2-3 sentence description of what the project is and why it matters.}

**Created:** {YYYY-MM-DD}
**Size:** {small | medium | large}
**Source:** {claude session N | direct request | spin-off from <parent>}

## Problem Statement

{3-6 sentences describing the real-world pain this project addresses. Be specific about user-visible problems, not technical abstractions.}

## Goals

- {4-8 concrete goals}

## Scope

- {What's in scope, bullet list}

## Out of Scope / Deferred

- {What's explicitly NOT in scope}

## Phases

{If the project is medium or large, list the phases. Otherwise describe the straight-line path.}

## Definition of Done

- [ ] {Specific, testable completion criteria}
- [ ] {More criteria - every box should be something a reader can objectively verify}

## Related Projects

- {Cross-reference any existing projects whose work this builds on or feeds into}

## Session Context

**Parent session:** {Brief description of what was being worked on when this was created, or "direct request" if user opened a fresh conversation}
**Triggered by:** {Verbatim quote or close paraphrase of what the user said}
**Date:** {YYYY-MM-DD}
**Commits / branches from parent session:** {SHAs or branches if relevant, or "none"}

## Key Files to Touch

{List of files that will likely be modified, grouped by area. Use absolute or repo-relative paths.}

## Dependencies

{Other projects, environment variables, external services, or infrastructure this depends on. List explicitly so future sessions don't have to rediscover them.}
```

### 3b. `definition_of_done` - concise completion criteria

A markdown bullet list. Same criteria as in `origin_brief`, but extracted as a standalone field for easy reference. 4-10 bullets, each objectively verifiable.

### 3c. `starter_prompt` - the copy-paste prompt for future sessions

This is the artifact a future session pastes into a fresh Claude Code conversation to resume work on this project. Format:

```
I'm ready to work on {title}.

Read the full project context at projects/{slug}/README.md.

**Origin:** {one sentence about what spawned this project}

**What to do first:**
1. Read the README's Problem Statement, Goals, and Definition of Done sections
2. Invoke superpowers:brainstorming to explore the approach before writing code
3. This is a {size} project - estimated {N} session(s)

**Key files to touch:**
- {file 1}
- {file 2}
- {file 3}

**Dependencies / constraints carried over:**
- {anything the new session needs to know that isn't obvious from the README}

Let's go.
```

The starter_prompt should be self-contained. A future session should be able to paste it into a fresh conversation and pick up cleanly without needing the current session's context.

### 3d. `raw_input` - what the user actually said

The literal message or close paraphrase of what triggered this scaffold. Never empty. If you can't quote verbatim, write a 1-2 sentence summary of the conversation context that produced the project.

Why this matters: months later when the user re-reads the project record, the verbatim trigger is what reconstructs the original intent. *"User asked to scaffold this after hitting the same manual triage three times in one week"* tells you more than *"new project for triage tooling"*.

---

## Step 4 - Write the files

Write `projects/<slug>/README.md` with this structure:

```markdown
{origin_brief from Step 3a}

---

## Starter Prompt

Paste this into a fresh Claude Code conversation to resume work on this project:

````
{starter_prompt from Step 3c}
````

---

## Raw Input

> {raw_input from Step 3d}
```

Then write empty stubs for the other two files in the project folder:

- `projects/<slug>/plan.md` - header only: `# Plan: {Title}\n\n_To be filled in by the brainstorming + writing-plans skills._`
- `projects/<slug>/report.md` - header only: `# Completion Report: {Title}\n\n_To be filled in by the ship skill at project close._`

**File writing rule:** Use the `Write` tool for every file. Never use bash heredocs (`cat > file <<EOF`). Heredocs fail on apostrophes in prose content, which scaffolded README content almost always contains. See the `no-bash-heredocs` rule for the authoritative reasoning.

---

## Step 5 - Optional task tracker insert

If you use a task tracker for projects (database, ClickUp, Linear, Jira, GitHub issues, Notion), insert a row here. The fields to populate:

- `title` - from input
- `slug` - generated in Step 1
- `description` - short version
- `origin_brief` - full markdown from Step 3a
- `starter_prompt` - from Step 3c
- `definition_of_done` - from Step 3b
- `raw_input` - from Step 3d
- `status` - `backlog`
- `category` - `project` or `task`
- `size` - `small | medium | large`
- `source` - `claude` (or your equivalent)
- `created_at` - now

**Ordering matters when both filesystem and tracker writes are involved.** Insert into the tracker first (it's your source of truth for metadata), then write the filesystem files. If the filesystem write fails, delete the tracker row to keep state consistent. The reverse order (filesystem first, then tracker) produces silent half-failures where the folder exists but no tracker row does.

If you don't use a task tracker, the filesystem is the tracker. The README's content IS the project record. Skip this step entirely.

---

## Step 6 - Optional notification

Per-repo notification conventions vary. If your repo has a Slack webhook script, a Telegram bot, an email notifier, or any equivalent - fire it now with a one-line summary:

```
🚢 New project scaffolded: {Title}
   Slug: {slug}
   Size: {size}
   Folder: projects/{slug}/
```

Skip silently if no notification path exists. Don't hardcode tokens, webhook URLs, or bot IDs in this skill - those are repo-local concerns.

---

## Batch mode

When the user provides multiple projects in one request:

1. Loop through Steps 1-5 for each project.
2. Collect results as you go.
3. At the end, display a summary table:

```
| # | Project | Slug | Size | Folder | Tracker |
|---|---------|------|------|--------|---------|
| 1 | Content Repurposing Skill | content-repurposing-skill | medium | created | inserted |
| 2 | Client Onboarding Template | client-onboarding-template | small | created | inserted |
| 3 | Pricing Page Rewrite | pricing-page-rewrite | small | created | n/a |
```

4. Send a single notification summarizing all created projects (not one per project).

---

## After scaffolding

- Confirm what was created. Show the path: `projects/<slug>/README.md`.
- If any steps failed, report which ones and why.
- **Do NOT automatically commit.** The user may want to scaffold more projects or adjust the README before committing. Let them invoke their git workflow when ready.
- **Do NOT automatically invoke `project-manager`.** Scaffolding and starting work on the project are two distinct sessions. Scaffolder creates the artifact; project-manager picks it up later. Mixing them produces sessions that ship the project from the same prompt that created it, with no brainstorming gate in between.

---

## Hard rules

1. **Every project gets the full rich-context fields.** No bare-minimum READMEs. The four blocks in Step 3 (origin_brief, definition_of_done, starter_prompt, raw_input) are non-negotiable.
2. **Never overwrite an existing project.** Step 2 catches duplicates. If a folder exists, stop and ask.
3. **Status is always `backlog` at creation.** Never `in_progress`, never `todo`. The weekly review is the only gate to active work.
4. **Filesystem and tracker stay consistent.** If both are in use, insert into the tracker first, then write the filesystem. Roll back on failure.
5. **No bash heredocs.** Use the `Write` tool for all file writes. Heredocs fail on apostrophes in prose, which README content almost always contains.
6. **Don't auto-commit.** The user controls their git workflow.
7. **Don't auto-start work on the new project.** Scaffolding ends; the next session picks up.

---

## Anti-patterns

- Scaffolding a project for a one-line bug fix. Branch + fix + ship is faster.
- Generating an `origin_brief` that's three bullet points and a heading. The whole point of the skill is the rich context - if you don't have enough information to write 3-6 sentences for the Problem Statement, ask the user before scaffolding.
- Writing the starter_prompt as a vague *"work on the project"*. The prompt must be self-contained and reference specific files and constraints.
- Inferring `world` / `category` / `size` from thin air. If genuinely ambiguous, ask once.
- Inserting into the tracker without writing the filesystem (orphan row) or writing the filesystem without inserting into the tracker (orphan folder). Either is a failure mode that requires manual reconciliation later.
- Auto-invoking `project-manager` after scaffolding. Two distinct flows, two distinct sessions.

---

## How this skill cooperates with the rest of the kit

- **`session-types` rule** - the Ad-Hoc Build flow routes here automatically when the user opens a fresh conversation with a multi-step build request.
- **`project-manager` skill** - when invoked on a project that has no `projects/<slug>/README.md`, project-manager pauses and calls this skill first, then resumes with the freshly-scaffolded project.
- **`ship` skill** - fills in `projects/<slug>/report.md` at project close, the stub that this skill creates at scaffolding time.
- **`weekly-review` skill** - promotes scaffolded backlog projects into the active queue.
- **`daily-review` skill** - surfaces them once they have target dates.

The filesystem shape this skill creates (`projects/<slug>/README.md` + `plan.md` + `report.md`) is the convention the other skills expect.
