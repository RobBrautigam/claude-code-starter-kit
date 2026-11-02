# Concurrent Sessions Safety

If you run multiple Claude Code conversations on the same repo at the same time, each conversation is completely isolated with no shared state or awareness of the others. This rule prevents the disasters that follow.

## Parallel conversations require separate git worktrees (MANDATORY)

**Two Claude Code conversations on different branches in the same repo MUST run in separate git worktrees.** This is the single most important rule on this page. Failure to follow it has caused multiple incidents where one conversation's branch switch yanked the other's working tree out from under it - losing untracked files, breaking ship workflows, and corrupting context.

### The fundamental problem

A git checkout / worktree is a single filesystem state. When two Claude conversations point at the same checkout (e.g., `~/dev/myrepo`), they share that filesystem state. Branch operations - `git checkout`, `git switch`, `git pull`, `git stash`, even `git merge` - change the working tree atomically for **every process** that touches that directory. **Conversation A switching branches reaches into Conversation B's reality and changes its file contents, branch name, and uncommitted-state visibility.** Conversation B has no idea this happened until it tries to operate and gets unexpected state.

This is not a Claude-specific bug. It's how filesystems work. The fix is to give each conversation its own physical checkout.

### The required pattern

When starting a parallel Claude conversation in a repo that already has an active conversation, **a git worktree MUST be created before the second conversation does any work.**

```bash
# In the main checkout (where the first conversation is working):
cd ~/dev/myrepo

# Create a worktree for the second conversation with a descriptive suffix:
git worktree add ~/dev/myrepo-feature-x feat/new-feature

# Examples:
git worktree add ~/dev/myrepo-video feat/video-content-engine
git worktree add ~/dev/myrepo-audit -b feat/a11y-audit-pass main
git worktree add ~/dev/myrepo-experiment HEAD
```

Then the second Claude conversation opens VS Code (or equivalent) **pointed at the new worktree directory**, not the original. Each worktree has its own working tree, branch, and uncommitted state. They share the `.git` directory underneath, so commits, refs, remotes, and history are unified - but the working states are isolated.

### Cleanup

When the parallel conversation is fully done (work committed + pushed + merged or abandoned):

```bash
# From the main checkout:
git worktree remove ~/dev/myrepo-feature-x
git worktree prune
```

If the worktree directory was deleted manually first, `git worktree prune` reclaims the slot.

### When worktrees are NOT required

- A single conversation in a repo, even if it spawns subagents (subagents share the same working tree by design).
- Multi-machine work (different laptops have their own checkouts - that's a different separation).
- Branches that haven't been switched into the working tree.

The rule kicks in the moment two Claude *conversations* coexist on the same repo. Not two branches. Not two laptops. Two *conversations*.

## Rules

- At the start of every session, run `git pull` and `git status` to pick up any changes from other sessions.
- Commit and push frequently, especially before pausing or context-switching. Small, frequent commits are always better than large batched ones.
- Before editing a file, re-read it first. Another session may have changed it since you last saw it.
- If you encounter a merge conflict or unexpected file state, stop and tell the user before resolving. Another session may be actively working on those files.
- Never force-push or reset. Another session's work could be on the remote.
- If a `git push` fails due to remote changes, run `git pull --rebase` and retry. If the rebase has conflicts, stop and tell the user.

## Playwright session isolation

Always pass `-s=<session-name>` (or the equivalent session flag) to `npx playwright-cli` and related Playwright invocations when another session may be running Playwright concurrently. Default browser profiles collide and produce flaky screenshots and selector behavior that looks like Playwright bugs but is actually cross-session contention.

## Version-race handling

Before running a version bumper, re-read the version file (`pyproject.toml`, `package.json`, `VERSION`) from disk. If the current version is higher than what your context last observed, another session bumped in parallel - bump from the new baseline, not your stale context.

## File ownership awareness

- If the user tells you which area of the codebase to focus on, stay within that scope. Don't make drive-by edits to unrelated files.
- If you need to touch a file outside your stated scope, flag it first. Another session might own that file right now.

## Multi-machine workflow

If you work across multiple machines, the same rules above apply, plus:

- Always push all changes before ending a work session. Never leave unpushed commits.
- After pulling, check if `package.json` or `pyproject.toml` changed and run `npm install` / `pip install -e .` if needed.
- After pulling, pull the latest env variables from your hosting platform if applicable.

## VS Code window hygiene

Every open VS Code window costs roughly 1-1.5 GB RAM (main process + renderer + extension host + GPU + utility processes) plus one extension-host instance per active extension. With multi-day uptime, extension-host memory leaks compound. Each window also spawns its own copy of every globally-enabled MCP server.

**Discipline:** close VS Code windows for repos you're not actively working in *today*. Don't keep all your repos open as a "workspace" - open them as you need them, close them when you switch context. The cost of re-opening is seconds; the cost of keeping 7-8 windows open for days is sustained 8-15 GB of background RAM and slow desktop responsiveness.

## Dev server bloat (long-session leak)

Long-running Next.js HMR and Vite dev servers leak memory across multi-hour sessions. Single dev-server processes have been measured at 6-12 GB resident after 1-3 hours of active development.

**The 4 GB Node heap cap does NOT bound resident memory under Next.js 16 + Turbopack.** Turbopack runs Rust worker threads that allocate native memory outside V8's heap cap. There is no Node-level knob that prevents this.

**Discipline:**
- Restart your dev server when switching projects, returning from a meal, or any natural session boundary >2 hours. Treat dev server uptime like browser tab uptime.
- Don't run two dev servers for the same project simultaneously.
- Don't auto-restart the dev server in a loop from a Claude conversation. If a parallel conversation is running an audit / preview against localhost and the dev server keeps bloating, redirect the audit to the production URL or a `next start` (production-bundle) server.
