# Session Types

Every Claude Code conversation falls into one of four types. Identify the type from the opening message and follow the corresponding workflow.

## 1. Project Session

**Trigger:** User pastes a starter prompt from a tracker, says "next project", "let's work on X", or names a specific in-progress project.

**Workflow:** Invoke the `project-manager` skill. It reads the project record, identifies what's next, and runs the full Superpowers chain.

**Rules:**
- One project per session.
- Stay on scope. Spin off tangents as backlog items.
- Follow the phase / sequencing of the project's plan unless the user explicitly overrides.

## 2. Quick Fix Session

**Trigger:** User describes a specific bug, error, env var issue, or small tweak. Can be described in one sentence. Examples: "fix the typo in the header", "the date format is wrong", "add X env var to production".

**Workflow:**
1. Branch off latest main: `git checkout main && git pull --ff-only && git checkout -b fix/<short-description>`
2. Diagnose the issue, fix it, verify it works.
3. Commit on the branch: `git add <paths> && git commit -m "<lowercase message>"`
4. Push and let the ship skill handle PR creation + auto-merge: `git push -u origin fix/<short-description>` then invoke `/ship`.

**Carve-out - when to skip the branch:** Single-line typo or comment fix where opening a PR adds more friction than the change is worth.

**Quick fix definition:** Fits in one sentence, fixes in under 30 minutes. If it grows beyond either, stop and create a project for it.

**Rules:**
- No brainstorming or implementation plans. Just fix and ship.
- If the fix takes longer than 30 minutes, it's not a quick fix. Stop and create a project for it.
- If the fix is related to an in-progress project, note it in that project's README.

## 3. Strategy / Audit Session

**Trigger:** User wants to step back and discuss the big picture. Examples: "are we on track?", "should we change the roadmap?", "review our progress", "I have a question about the plan".

**Workflow:** Query all active projects / initiatives from your task tracker. Show phase progress and statuses across every active workstream. If the user is asking about a specific initiative, focus there. If asking broadly, summarize all of them. Provide analysis and recommendations. Update records if decisions are made.

**Rules:**
- No building. This is thinking and planning, not implementation.
- If the session produces roadmap changes, update the relevant initiative / phase / pipeline records.
- If the session identifies bugs or issues, log them for a quick fix session or add to a project scope.

## 4. Ad-Hoc Build Session

**Trigger:** User opens a fresh conversation with a multi-step request that isn't tied to an existing project. Examples: "build me a script that does X", "I need a new page that shows Y", "set up integration with Z".

**Workflow:**
1. Recognize this is a multi-step build (not a quick fix).
2. Invoke the `project-scaffolder` skill - no need to ask. It creates `projects/<slug>/` with a full rich-context README, an empty `plan.md`, and an empty `report.md`.
3. Invoke the `project-manager` skill, which picks up the freshly-scaffolded project and kicks off the full Superpowers chain (brainstorm, plan, execute, ship).

**Rules:**
- If clearly multi-step, scaffold without asking. The filesystem (and tracker, if you use one) is the system of record and every meaningful piece of work belongs there.
- If genuinely ambiguous (could be a quick fix or a project), ask once: *"This could go either way - want me to scaffold a project for this, or just handle it inline?"*
- Quick fixes never get scaffolded. The line: if it can be described in one sentence and fixed in under 30 minutes, it's a quick fix.

## Spin-off ideas mid-session

A fifth pattern surfaces mid-project: an idea comes up that's worth pursuing but doesn't belong in the current project's scope. Do NOT silently absorb it (scope drift) and do NOT trust yourself to "come back to it later" (you won't). The right move is to invoke `project-scaffolder` mid-session in spin-off mode - it captures the verbatim trigger as the new project's `raw_input` and records the current project as the parent. The spin-off lands in `projects/<new-slug>/` in status `backlog` and the original session resumes. This is the kit's primary mechanism for preventing lost ideas.

## How to tell the difference

| Signal | Session type |
|---|---|
| One sentence problem description | Quick fix |
| Named project from the roadmap or starter prompt | Project session |
| Multi-step request in a fresh conversation, no existing project | Ad-hoc build |
| Questioning the roadmap or asking "what should we do?" | Strategy session |
| Genuinely ambiguous | Ask once, then proceed |

When in doubt, ask: *"Is this a quick fix, a project session, or a strategy conversation?"*
