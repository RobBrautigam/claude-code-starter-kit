---
name: project-manager
description: Session guardrails and execution discipline for Claude Code conversations. Keeps work on-track, prevents scope creep, enforces the Superpowers skill chain (brainstorm → plan → execute → verify → review → ship), and creates a feature branch + draft PR at session start. Triggers on "let's work on X", "next project", "continue X", "what's next?", or when the user opens with a project name.
---

# Project Manager

Session guardrails and project execution. Keeps work on-track, prevents scope creep, enforces the Superpowers workflow chain, and tracks progress.

This skill is filesystem + git driven by default. If your setup has a richer task tracker (database, ClickUp, Linear, Jira), substitute the "task source" steps with queries against it - the workflow shape stays the same.

---

## When to invoke

- User says: "let's work on X", "next project", "continue X", "what's next", "start the X project", "I want to build Y", or pastes a starter prompt naming a project.
- User pastes a multi-step build request that isn't a quick fix - invoke the `project-scaffolder` skill first to create the project, then resume here.

## When NOT to invoke

- One-sentence bug fixes. Use a Quick Fix flow instead - branch off main, fix, push, ship.
- Strategy / planning conversations with no implementation work.
- Pure exploratory questions ("how does X work?", "what do you think about Y?").

---

## Session start protocol

### Step 1: Identify the project

The project is either:
- **Already scaffolded** - its files live at `projects/<slug>/README.md` (or your repo's equivalent path). Read the README first.
- **Brand new** - the user just described what they want to build. Pause and invoke the `project-scaffolder` skill before continuing. It creates `projects/<slug>/README.md` with the full rich context (origin brief, definition of done, starter prompt) plus empty `plan.md` and `report.md` stubs. Once scaffolding completes, resume this skill from Step 2 with the freshly-scaffolded project.

### Step 2: Reconcile scope against canonical sources

The starter prompt the user pasted is ONE input - not the binding scope. Before brainstorming, reconcile against:

1. The project's `README.md`
2. Any existing plan at `projects/<slug>/plan.md`
3. Any existing design spec at `docs/specs/*-<slug>-design.md`
4. Sibling project READMEs (when the README names dependencies)
5. Recent patch reports / progress log entries that reference this project

For each source, ask: *"Does the user-supplied framing match what these documents say the project is?"*

**If everything aligns** - proceed silently to Step 3.

**If anything diverges** - STOP and present a scope-divergence report:

1. TL;DR: "I found a scope divergence between the starter prompt and the canonical project record."
2. What the canonical sources say (bullets).
3. What the starter prompt / current framing covers (bullets, side-by-side).
4. Delta table with severity per row (CATASTROPHIC / MAJOR / MEDIUM / LOW).
5. Downstream consequences (sibling project breaks, deferred commitments).
6. Recommendation with reasoning (usually: "build the canonical scope").
7. 2-3 framed options for the user to pick.

Do not proceed without an explicit scope decision.

### Step 3: Create local feature branch

Every project session runs on a feature branch with a draft PR. Create the branch now (the PR opens later, after the first commit).

```bash
git fetch origin
git checkout main
git pull --ff-only
git checkout -b feat/<project-slug>
```

If you're already on `feat/<project-slug>`, you're resuming an in-progress session - skip the branch creation.

If you're on a different feature branch from a parallel project - STOP. This is a scope anomaly. Confirm with the user before continuing.

**Branch communication template:** *"Creating branch `feat/<slug>` off latest main. All project work happens here. Production won't change until we merge this back to main at session close."*

### Step 4: Design or resume

> **MANDATORY GUARD - do not skip.**
>
> Brainstorming is required UNLESS a saved plan already exists at `projects/<slug>/plan.md`. The existence of an origin brief, a starter prompt, a status field, or a "Session N" framing is **not** sufficient. Only a saved plan file authorizes a resume.

**No saved plan exists (new project):**

1. Invoke `superpowers:brainstorming` - explores requirements, asks clarifying questions, proposes 2-3 approaches, presents a design, and writes a design spec to `docs/specs/`. Every project goes through this regardless of perceived simplicity.

   Claude makes architecture and engineering decisions autonomously. Clarifying questions focus on UX, functionality, and user-facing behavior - not implementation details. Always present a recommended option when showing approaches.

2. When the brainstorming skill transitions to `superpowers:writing-plans`, save a copy of the plan to `projects/<slug>/plan.md` for permanent record.

3. The writing-plans skill will ask the user to choose an execution approach:
   - **Subagent-Driven (recommended)** - Fresh subagent per task with two-stage code review between tasks.
   - **Inline Execution** - Execute tasks sequentially in the current session with checkpoints.

**Saved plan exists (resuming):**

- Read `projects/<slug>/plan.md` fully.
- Show the implementation checklist with progress.
- Confirm where to resume: *"Working on {title}. {X remaining items}. Ready to go?"*

### Step 5: Push branch + open draft PR

After the design spec is committed locally, push the branch and open a draft PR:

```bash
git push -u origin feat/<slug>
gh pr create --draft \
  --title "feat: <project title>" \
  --body "$(cat <<'BODY'
## Project

**<Title>**

<2-3 sentence description>

## Scope

(see projects/<slug>/README.md for the binding scope)

## Out of Scope

(see the README's "deferred" / "out of scope" list)

---

🤖 Opened by Claude Code via the project-manager skill at session start.
BODY
)"
```

Draft PRs give Slack / GitHub integration something to broadcast and create a visible work-in-progress marker. The PR stays draft until ship time.

---

## During the session

### Execution with Superpowers

- **`superpowers:subagent-driven-development`** (recommended). Fresh subagent per task. Each subagent:
  - Follows `superpowers:test-driven-development` (write failing test first, then implement)
  - Self-reviews before returning
  - Gets reviewed via `superpowers:requesting-code-review` (two-stage: spec compliance + code quality)
  - Fixes any Critical or Important issues before moving to the next task

- **`superpowers:executing-plans`** (alternative). Execute tasks inline with batch checkpoints for review.

- Both paths use **`superpowers:using-git-worktrees`** to create an isolated workspace when the project scope is large enough to warrant it.

### When bugs are encountered

- **STOP.** Do not guess at fixes.
- Invoke **`superpowers:systematic-debugging`** - four-phase approach: investigate root cause, analyze patterns, form hypothesis, then implement fix.
- Only after root cause is identified, write a failing test case, then fix.

### When multiple independent failures appear

- Use **`superpowers:dispatching-parallel-agents`** to investigate each failure concurrently.
- Review results, check for conflicts, then integrate fixes.

### Scope monitoring

**Proactive expansion (default):** Adjacent enhancements under ~30% extra effort are included automatically - mention them in progress updates without asking permission.

**Flagged expansion:** Enhancements over ~30% extra effort: recommend with reasoning. Default to inclusion if the user doesn't object.

**Unrelated work:**
1. Quick fix (<30 min) and foundational → inline, it's an investment.
2. Unrelated and non-trivial → **spin off a new project via the `project-scaffolder` skill**, then refocus on the current one. The scaffolder captures the verbatim trigger from the mid-session conversation as the new project's `raw_input` and references the current project as the parent in the origin brief, so the lineage stays clear when the spin-off is picked up later.
3. **Never silently drift.** If you notice a tangent worth pursuing, scaffold the spin-off now so it doesn't get forgotten, then return to the current scope.

### Mid-session spin-offs (the common case)

Ideas that surface mid-project are the most valuable thing to capture, and the easiest to lose. As soon as a tangent comes up that isn't going to ship inline:

1. Pause the current work briefly.
2. Invoke `project-scaffolder` with the spin-off as input. Tell the scaffolder the parent project's slug so the lineage gets recorded in the new project's `Session Context` block.
3. The scaffolder creates `projects/<spin-off-slug>/` and writes the rich context. No tracker insert needed if you don't use one - the README is the record.
4. Return to the original project. The spin-off is now in `projects/` waiting for the weekly review or daily pick.

This pattern is how the kit prevents the "I'll remember to come back to this" failure mode. You almost never remember. Scaffolding takes 30 seconds and makes the idea concrete instead of a fading thought.

### Progress tracking

- As you complete plan items, check them off in `projects/<slug>/README.md`.
- Commit AND push every time. A commit that sits local is invisible to other sessions and CI. `git commit && git push` is one operation.

---

## Before claiming completion

**Always invoke `superpowers:verification-before-completion` before claiming any work is done.**

Run the actual test/build/lint commands. Confirm zero failures. Never say "should work" without evidence.

---

## Session end protocol

Invoke your `ship` skill (or equivalent session-close workflow). Ship handles version bump, progress log, commit, push, PR ready-for-review, and merge.

### Before invoking ship

1. **Verify completion** - run `superpowers:verification-before-completion`.
2. **Optional review checkpoint** - if you have a Codex review skill (or any second-opinion review tool), offer it now:
   - Adversarial review when the session touched data mutations, auth, cron jobs, migrations, or unattended production code.
   - Standard review for UI-only / config / docs.
   - Skip only for trivial changes.
3. **Finish the branch** - if work was done in a worktree, run `superpowers:finishing-a-development-branch`. Otherwise skip.
4. **Summarize against the plan** - report items completed vs total plan items.

---

## Key principles

- **Claude is the technical lead.** Own architecture and engineering decisions. State what was chosen, give a one-line reason, note one alternate path considered. Ask about UX, functionality, and user-facing behavior - not implementation details.
- **Always recommend.** Lead with a clear recommendation and reasoning. Never present a "you pick" moment on the technical side.
- **The starter prompt is one input, not the scope.** Reconcile against the canonical sources (README, plan, sibling READMEs, recent reports) before brainstorming. Silent scope cuts and silent scope expansions both get surfaced.
- **Build it right.** Proper error handling, validation, pagination, test coverage, and reusable patterns are the baseline, not extras.
- **Proactive scope expansion.** Include adjacent enhancements that build a stronger foundation when they add less than ~30% effort.
- **Use Superpowers at every step.** Brainstorm before building. Plan before coding. Test before implementing. Verify before claiming. Review before merging.
- **One project per session.** Small projects might fit two, but never split focus on large ones.
- **Evidence before assertions.** Run the code, check the output, verify the deploy before claiming something works.
- **Branch communication.** Every project session runs on a feature branch with a draft PR. Communicate every branch operation in plain English (not git jargon) - users who are still learning git appreciate the translation.

---

## Execution summary (session start)

| Step | Operations |
|------|-----------|
| 1 | Identify project (read README) |
| 2 | Scope reconciliation against canonical sources |
| 3 | Create feature branch |
| 4 | Brainstorming or resume from saved plan |
| 5 | Push + open draft PR |

Then the Superpowers chain takes over.
