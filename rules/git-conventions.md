# Git Conventions

## Commit messages
- Lowercase only
- Under 72 characters
- No period at the end
- No `Co-Authored-By` trailer and no "Generated with ..." attribution line. An AI agent is a tool
  the author used, not a contributor, and a trailer follows the code into every clone, fork and
  contributor graph forever. The kit's `hooks/git/commit-msg` refuses both shapes, so the rule
  holds even when a tool's default template adds them.
- Say what the change does, never who it was for (this matters most in public repositories; see
  `public-repos.md`).

## Workflow
- Always run `git pull` at the start of every session before making any changes.
- **Push immediately after every commit.** A commit that hasn't been pushed is invisible to other sessions, CI, and GitHub notifications. Treat `git commit && git push` as one atomic operation.
- After every significant change, commit and push automatically without waiting to be asked.
- When in doubt about whether a change is significant enough, err on the side of committing.
- Before editing any file, re-read it to catch changes from other sessions.
- If `git push` fails due to remote changes, `git pull --rebase` and retry. If conflicts arise, stop and ask the user.

## Branching

**Default: feature branches for everything.** Even single-session work, even small fixes. This is the standard across all repos, including solo ones.

### The pattern
1. At session start, create a feature branch off the up-to-date main: `feat/short-description`, `fix/short-description`, `chore/short-description`, `docs/short-description`. Keep names descriptive and lowercase.
2. Push the branch early - even before substantial work is done - and open a draft PR. The draft PR's existence is the "I'm working on this" signal that becomes visible in Slack via the GitHub-Slack integration. This prevents parallel-work collisions with collaborators.
3. Commit and push frequently within the branch.
4. When ready, mark the PR ready-for-review (or merge directly if solo).
5. Merge to main via PR. Auto-merge is fine for solo repos. For shared repos with CODEOWNERS, wait for the auto-requested review.
6. Delete the local and remote branch after merge.

### Why this is universal (not just for shared repos)
- **Slack visibility.** The GitHub-Slack integration broadcasts every PR open/merge/comment to the team channel. Direct-to-main commits are silent in comparison.
- **Single mental model.** "Always branch" is one decision made once. "Branch sometimes, direct-to-main other times" is a decision made every session, which means it gets made wrong sometimes.
- **Future-proofing.** Any solo repo could become multi-contributor in a quarter. If the convention is already "branch first," nothing changes when that person arrives.
- **Audit trail.** Every PR is a project record - what changed, why, when, by whom.
- **Trivial reverts.** A PR can be reverted with one click. A pile of master commits cannot.

### Narrow exceptions where direct-to-main is still acceptable
- A ship-skill's version-bump-and-push commit (mechanical, atomic operation by convention).
- Genuinely trivial single-line changes: typo in a comment, a dependency version pin, a config value tweak. When in doubt, branch.
- Initial repo scaffolding before any other contributor exists.

### Hard rules that still apply
- Keep `main` deployable at all times. If it's on main, it should work in production.
- Never force-push to main. Branches you own can be force-pushed before sharing.
- A failed merge or hook does NOT permit `--no-verify` or destructive bypasses. Fix the underlying issue.
  (The kit's `hooks/guard_bash.py` refuses `--no-verify` and a force push to main or master before
  the command runs.)

## Branch communication
If you're new to git, every branch operation should be announced clearly and explained.

- **Creating a branch:** "I'm creating branch `feat/xyz`. All work will happen here. Your live app won't change until we merge this back to `main`."
- **Merging:** "I'm merging `feat/xyz` into `main`. This brings all the project's changes into the live branch. Production will auto-deploy after the push."
- **Rebasing:** "I'm rebasing this branch onto `main`. Another project's changes were merged to `main` since we branched off. Rebasing replays our commits on top of those changes so everything stays compatible. This does NOT go live - it just updates our working branch."
- **Conflict detected:** "There's a merge conflict in [file]. This means another project changed the same lines we changed. I'll stop here so you can decide how to resolve it."

When multiple branches are ready to merge:
1. Merge Branch A into `main` first, push it.
2. Other active branches rebase onto the updated `main` to pick up those changes.
3. Then Branch B merges into `main`.

Always explain which step you're on and why.

## Branch cleanup
- After a branch is merged to `main`, delete the local and remote branch.
- Worktree branches (`worktree-agent-*`) are temporary subagent artifacts. Prune and delete them at session end.
- Never force-delete (`-D`) a branch without checking for unmerged commits first. If unmerged commits exist, flag it to the user.

## Identity
Configure git globally once with your GitHub identity. Never set `--local user.email` per-repo unless there's a specific reason - silent local overrides are a common source of "wrong account committed" incidents.
