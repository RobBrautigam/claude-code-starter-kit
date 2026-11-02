# Session Handoffs Are Required

When telling the user that the current Claude Code conversation is done and they need to start a fresh one to continue, you MUST:

1. **Provide the starter prompt FIRST**, before invoking ship. Ship takes a while (commits, push, PR, auto-merge). Surfacing the starter prompt up front lets the user copy it and be ready to start the next session the moment ship finishes - instead of waiting for ship to complete before they see the prompt.
2. **Run the `ship` skill** to close out the session cleanly (version bump, progress log finalization, changelog entry, commit / push, README updates).
3. **Run the `session-handoff` skill** OR produce its equivalent inline - a structured chat-only summary covering: decisions made, what shipped, key files touched, current branch + PR state, verification steps, deferrals, and open questions.

The starter prompt must include:
- Project name + project ID (or task tracker URL)
- Branch name and PR number (if applicable)
- What was just shipped (one-paragraph context)
- What to read first (specific file paths, in order)
- The first concrete action to take
- Critical constraints carried over from this session (credentials to ask about, decisions made, etc.)
- **MANDATORY: parallel-session safety check** (see next section)

## Parallel-session safety check - MUST appear in every starter prompt

The single biggest source of cross-session corruption is two Claude Code conversations operating on the same physical working tree at the same time. Even if you THINK the previous session has ended, it may still be alive - running a background task, waiting for user input, doing cleanup hooks, or doing diagnostic git operations like `git stash` / `git stash pop` / `git checkout`. Any of those operations atomically rewrites the shared `.git/index` and working tree, **corrupting the new session's state mid-flight**.

The rule: **every starter prompt MUST contain an explicit parallel-session check as a step in its pre-flight, BEFORE any other instruction.**

### Boilerplate to bake into every starter prompt's pre-flight section

When writing a starter prompt, copy this block verbatim into the pre-flight (adapt repo path):

```
Pre-flight (MANDATORY - do not skip):

1. Parallel-session check: confirm no other Claude Code conversation is active in this repo. If the previous session is still open in a different window, STOP and tell me - we need to either close it first or set up a git worktree per the concurrent-sessions rule before either session does any work.
2. Re-read the previous session's final message: if it was paused mid-task (waiting for confirmation, mid-command, asking a question), tell me before continuing.
3. Now do the rest of the pre-flight: git status (verify clean), git fetch, git status again (verify still clean after fetch), git log --oneline, git worktree list (note stale worktrees but don't touch them).
```

This block is mandatory in every starter prompt - copy it, adapt the repo path, do not omit it.

## The prompt MUST be delivered inline in the conversation chat (mandatory)

The starter prompt MUST appear as a copy-paste fenced code block IN THE CONVERSATION CHAT itself. Never put the prompt only in a file (`tmp/`, `docs/`, project README, etc.) and expect the user to retrieve it from disk. Writing the prompt to a file IS allowed as a supplement, but the inline chat version is non-negotiable.

The correct shape:

> Some explanatory framing if useful, then:
>
> ````
> ```
> <the full multi-paragraph starter prompt the next session pastes>
> ```
> ````
>
> Then any necessary closing context (e.g., "I'll invoke /ship now").

If you've written the prompt to a file (e.g., `projects/<slug>/session-N-starter.md` for archival), still paste the full content back into the chat. The file is a backup, not a substitute.

## Handoff prompts come LAST - never deliver one while work remains in this session

Before you deliver any handoff prompt for a fresh session, this session must be GENUINELY DONE. "Done" means: no review still owed, no findings still to triage, no commits still likely, no decisions still pending.

If there's a single piece of work still owed in this session - review pending, a test still to triage, a question about scope, a commit to make - **do not deliver the handoff prompt yet.** Tell the user the one thing that needs to happen next in THIS session, then wait.

## Handoff prompts are TERMINAL - never ask questions after delivering one

When you deliver a copy-paste starter prompt for a fresh conversation, that prompt IS the handoff. Do not ask follow-up questions after delivering it. Do not say "want me to also ship now?" or "should I confirm X?" - execute everything that doesn't need the user's input automatically in the same response.

## The prompt itself must commit to ONE path - never embed decisions

The previous section handles "don't ask questions in the SAME message as the prompt." This section handles the worse, sneakier variant: **putting decision points INSIDE the prompt body that the NEXT session will surface as questions back to the user.**

If the prompt says "PATH A or PATH B, pick one", or "Recommendation: X. Want me to also do Y?", or "Two options for the first task - let me know", **the prompt has failed.** The user pastes it into a fresh session and the very first response is another question.

### The correct pattern

1. **Before writing the prompt**, identify every decision point.
2. **For each decision point**, either:
   - Decide it yourself with one-line reasoning (engineering decisions), OR
   - Ask the user ONCE in the current session, get the answer, fold it into the prompt.
3. **The prompt then describes ONE execution path.** No menus. No "if user says X do Y else Z". No "your call". The next session reads the prompt and executes - no decisions remain.

The pattern is always:
- recommend + ask (if needed) → answer → write the prompt with the answer baked in → deliver prompt → silent ship → stop.

Never:
- write a prompt that contains the question → deliver → make the NEXT session ask the user.

## Why this rule exists

Partial handoffs have repeatedly lost context. The new session reinvents decisions, re-litigates architecture, or works on the wrong scope. Always deliver all three pieces (starter prompt + ship + handoff summary), in the right order, with the right content.

## Carve-out

If the user explicitly says "don't ship this" or "skip the handoff, just hand me the prompt", honor that - explicit instruction trumps the rule. But if no override is given and the situation is "session is done, work continues elsewhere," all three pieces are required.
