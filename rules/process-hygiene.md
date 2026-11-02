# Process Hygiene: What a Session Starts, the Session Stops

Claude Code does not reliably clean up the processes it starts, especially on Windows. Dev servers,
headless browsers, test watchers, `sleep` and `tail` loops and background helpers outlive the
conversation that started them, and a week of that is gigabytes of memory and a fan that never
stops. The cleanup is yours, and it belongs in the session close, not in a monthly panic.

## The laws

1. **Every session stops what it started, before it says it is done.** Dev and preview servers,
   local backends, headless browsers, test servers, watch loops. A session that deliberately leaves
   something running says so in its handoff, with the process id and who stops it.
2. **Start long-running things through the tool's own background run** (Claude Code's
   `run_in_background`), never a shell `&`. A background task the harness knows about can be
   listed and stopped; an `&` child is invisible.
3. **A stopped task is not a stopped process.** Stopping a background task can leave its shell
   wrapper and child running. After stopping one, read the process table and confirm.
4. **Never kill by image name.** No `taskkill /IM`, no `pkill`, no `killall`, no
   `Stop-Process -Name`. Your editor, browser, chat apps and every other Claude session share
   image names with what a session spawns (`node`, `python`, `chrome`). Stop a process only by its
   id, and only after its command line and parent chain prove it belongs to work that is finished.
   (The kit's `hooks/guard_bash.py` refuses the kill-by-name shapes.)
5. **Re-check the id right before you stop it.** Process ids are recycled. Confirm the command line
   still matches what you measured, in the live process table, not a snapshot from minutes ago.
6. **Never elevate, never put a window on the screen from background work.** No administrator
   prompt, no installer window, no browser popping up while the human is in a meeting. If a tool
   truly needs administrator rights, stop and hand the exact command to the human.
7. **Ask before large downloads.** A model, a dataset or an installer over about a gigabyte is a
   one-line question first: what it is, how big, where it goes.
8. **Keep load tests polite on a shared machine.** Synthetic load is small and short (a handful of
   busy processes for a minute), never "saturate the CPU and see".

## Proof before any stop (all four)

- The parent is gone, or the parent chain reaches a process that is gone.
- The command line names a session or folder that is no longer active.
- The process is old enough not to be a live session's short-lived helper (a few minutes).
- The command line still matches what you recorded.

When in doubt, leave it running and write it down.

## The close line

Every session's close gets one more line before "done": what did I start, and is each one stopped?

Related: `concurrent-sessions.md` (dev server bloat, window hygiene), `development-workflow.md`.
