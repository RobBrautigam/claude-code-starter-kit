---
name: session-handoff
description: Use when the user says "session handoff", "hand off", "handoff summary", "prep a handoff", "wrap up before I clear", "save context", or otherwise asks for a structured end-of-session summary they can paste into a fresh conversation. Produces a chat-only handoff covering decisions, shipped changes, key files, running state, verification steps, deferrals, and open questions so a fresh agent can continue seamlessly. This is NOT a project-closure workflow - do not use for "ship it", "close out the project", or commit/release flows; those belong in your own shipping skill or process. Use this whenever context is getting long and the user wants to /clear and continue.
---

# Session Handoff

Produce a repeatable end-of-session summary so the user can `/clear` and start a fresh Claude Code conversation without losing continuity. The next agent should be able to pick up by reading this summary alone - no conversation scroll-back required.

This is a **context-handoff artifact**, not a status report and not a session close. The audience is a future instance of you, not a stakeholder.

## When to invoke

User says: "session handoff", "hand off", "handoff summary", "prep a handoff", "let's wrap up", "summarize before I clear", "save our context", or any near-equivalent. Also invoke proactively if the user says they're about to `/clear` without having run it yet.

## When NOT to invoke

- If the user says "ship it", "let's close out", "wrap up this session" in the context of shipping a completed project - that belongs to a release/ship workflow (version bump, changelog, commit, push). This skill is purely for context continuity.
- If the user wants a patch report or completion report written to disk - that's a ship-style workflow too.
- If the user just wants a conversational summary ("what did we do today?") - answer directly in chat without this structured template.

If there's ambiguity between handoff and ship, ask once: "Is this a project close (version bump, commit, release artifacts), or a context save so you can /clear and continue in a fresh conversation?"

## How to produce the summary

1. **Review the full conversation**, not just the last few turns. Handoffs miss things when they only summarize recent context.
2. **Pull state from these sources (in order):**
   - Plan files referenced this session. Check Claude Code's scratch plans dir (`~/.claude/plans/`) AND any project-specific plan location used by the repo's conventions (commonly `projects/{slug}/plan.md`, `docs/plans/`, or similar).
   - TodoWrite state - any in-progress or pending tasks.
   - Background processes you started with `run_in_background` - shell IDs are load-bearing for the next agent; without them the next session cannot find or stop them.
   - Background agents dispatched (Agent tool in `run_in_background: true` mode) - their agent IDs/names and what they were investigating.
   - Files created or modified this session - you know what you touched; don't grep to re-discover.
   - Memory / persistent-state files written or updated (whatever persistent memory layer this Claude Code install uses, e.g. `~/.claude/projects/<repo-slug>/memory/`).
   - Database mutations made this session (if any DB writes happened - status changes, new rows, schema changes, migrations). The next agent needs to know what's already committed to the DB versus what's still pending.
   - Git state that matters: active feature branch (if not main), uncommitted changes, commits pushed this session, whether a deploy was triggered. If on a feature branch with an open PR, fetch the URL via `gh pr view --json url -q .url` so the next agent can open the PR directly without searching.
   - Playwright sessions started (if any) - note the session name so the next agent can reconnect with `-s=<name>` and avoid colliding with parallel sessions.
   - Unresolved questions - things you asked the user that never got a clear answer, or things the user asked that got deflected.
3. **Do NOT audit the filesystem.** This is synthesis of what happened in THIS session. No `git log` sweeps, no broad `Glob` passes. If you didn't touch it this session, it doesn't belong here.
4. **Produce the output in chat.** Do not write a file. Do not update memory. Do not bump the version. Do not touch any progress log. Chat-only.

## Output template - use exactly this structure, every time

```
# Session Handoff - <one-line title of what this session was about>

## Where it started
<2-3 sentences: what the user asked for, key framing or constraints that emerged>

## Decisions locked + what shipped
- <decision or change> - <why, and where it lives (absolute path if a file)>
- ...

## Key files for next session
- `<absolute path>` - <why the next agent should read this first>
- Plan file: `<path>` (if a plan drove the session)
- Memory / persistent-state files touched: `<paths>` (if any)

## Running state
- Background processes: <shell IDs + what they are + how to kill> - or "none"
- Background agents: <agent IDs + what they're investigating> - or "none"
- Dev servers / ports: <url + port> - or "none"
- Open worktrees / branches: <path> on <branch> (PR <url>) - or "none"
- Playwright sessions: <session name> - or "none"
- Database mutations already committed: <summary> - or "none"

## Verification - how to confirm things still work
- `<command>` - <expected outcome>
- ...

## Deferred + open questions
- Deferred: <item> - <why pushed to later>
- Open: <question needing the user's input> - <context>

## Pick up here
<1-2 sentences: the single most likely next action for a fresh agent>
```

## Hard rules

1. **Chat output only.** Never write the handoff to a file. Never update memory from this skill. No version bump. No progress log entry. No commits. If the user wants a persistent artifact, they want a ship/release workflow, not this.
2. **Never invent state.** If a section has nothing to report, write "none" - do not omit the section. Structure stability is the whole point; the next agent should see a predictable shape every time.
3. **Absolute paths always.** The next agent may have a different working directory, and many users work across multiple machines - relative paths break the handoff.
4. **If a plan file drove the session, name it first** in "Key files" so the next agent reads it before anything else.
5. **No emojis, no hype, no "great job" summaries.** Terse and concrete - paths, commands, shell IDs, decisions. Match the tone of a seasoned engineer handing off at end-of-shift.
6. **Background process IDs are critical.** If you started any `run_in_background` shells, their IDs must appear in "Running state" with the kill command - the next agent cannot find them otherwise. Same for background agents.
7. **Database mutation summary must be honest about what is and isn't committed.** Multiple Claude Code sessions may run against the same database. A handoff that omits "I already updated row X to status=done" risks the next session doing it again or making a conflicting edit.

## Anti-patterns - do not do these

- Summarizing the last 3 turns and calling it a handoff.
- Listing files by relative path.
- Skipping the "Running state" section because "nothing is running" - write "none" instead.
- Writing the summary to `docs/`, `.claude/handoffs/`, or any file. This is chat-only by design.
- Adding a "what went well / what went poorly" retrospective. This isn't a retro.
- Recommending next steps beyond the single "Pick up here" line. The next agent decides; you just hand off.
- Triggering ship/release workflows (version bump, changelog, commit) during this skill. If the session should be shipped, tell the user to run their ship workflow separately.
