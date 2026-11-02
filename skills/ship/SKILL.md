---
name: ship
description: Session-close workflow. Bumps version, updates progress log, writes a patch or release report, updates project README, commits and pushes, merges the PR. Triggers on /ship, "let's close out", "ship it", "wrap up this session", or when the project-manager skill reaches session end. Use this skill for ANY session closing activity, even if the user just says "done" or "that's it for today".
---

# Ship

Session-close checklist. Outputs: version bump, progress log entry, patch or release report, README updates, optional notification, commit + push, PR merge.

**Prerequisite:** All code changes must already be committed before running this skill. Ship only creates session-close artifacts. If uncommitted code changes exist, commit them first.

**File writing rule (mandatory):** Every markdown artifact in this skill - progress log entries, patch reports, completion reports, README updates - MUST be written with the `Write` or `Edit` tool. **Never use bash heredocs** (`cat > file <<'EOF'`, `cat << EOF >> file`, `printf "..." >`, `echo ... >>`). Heredocs fail on Windows git-bash when content contains backticks, code fences, `$`, single quotes, or multi-line markdown. The authoritative source is the `no-bash-heredocs` rule.

---

## Session types

- **Release** (minor version bump) - A project was completed. One project = one minor version.
- **Patch** (patch bump) - Bug fixes, polish, improvements, backfills, config changes. No project completed.
- **Major** (major bump) - Reserved for milestone releases. User's call, never automatic.

When in doubt, default to patch.

---

## Step 0: Preflight - optional review checkpoint

If you have a code-review tool (Codex, second-opinion agent, etc.), offer it now:

```
Before I ship: want a second-opinion review first?

  Standard review        - good for UI-only / config / docs / progress-log-only
  Adversarial review     - RECOMMENDED for data mutations, auth, cron, migrations, external APIs
  Skip                   - you confirm the change is trivial enough

Pick one and I'll continue with the rest of the ship checklist after.
```

Wait for the review to complete (if picked), incorporate findings, then continue. If the user explicitly skips, note that in the session output.

---

## Step 1: Preflight - uncommitted work check

```bash
git status --short
git diff --stat
```

If anything is uncommitted or untracked outside the standard ship paths (progress log, projects/, version file):

- For tracked changes - ask the user whether they belong in this ship or should be reverted.
- For untracked files - ask explicitly. The default ship commit only stages specific paths; untracked files outside those paths would be silently dropped.

Do not proceed until the working tree is clean enough to ship safely.

---

## Step 2: Bump version

Source of truth depends on the repo:
- Python: `pyproject.toml` `[project] version = "X.Y.Z"`
- Node: `package.json` `"version": "X.Y.Z"`
- Plain: `VERSION` file with `X.Y.Z` on a single line

Common pattern: a `scripts/bump_version.py` (or `npm version`) script that:
1. Reads current version
2. Bumps major / minor / patch
3. Updates the version file
4. Returns the new version string

Decide kind based on session type:
- Release → minor
- Patch → patch
- Major → ask the user explicitly; never default to major

Capture the new version string - you'll reference it in every subsequent artifact.

---

## Step 3: Write session artifacts (parallel)

These four writes are independent. Fire them in parallel.

### 3a. Progress log entry

Append a new entry to your progress log (commonly `docs/progress-log.md`). Reverse chronological - newest entry at the top.

Entry shape:

```markdown
## Session N - vX.Y.Z (YYYY-MM-DD HH:MM TZ)

<one-paragraph summary of what changed and why>

**Type:** Release | Patch
**Branch:** feat/<slug>
**PR:** #<number>

### What changed
- <bullet>
- <bullet>

### What's next
- <next session intent, or "TBD" if closing a project>
```

### 3b. Patch report or completion report

**Patch report** (for patch sessions) - write to `docs/patches/vX.Y.Z.md`:

```markdown
# Patch vX.Y.Z

**Date:** YYYY-MM-DD
**Type:** Patch
**PR:** #<number>

## Summary

<one paragraph>

## Changes

- <bullet>
- <bullet>

## Verification

- `<command>` - <expected outcome>

## Deferred

- <item> - <why>
```

**Completion report** (for release sessions that close a project) - write to `projects/<slug>/report.md`:

```markdown
# <Project Title> - Completion Report

**Shipped:** YYYY-MM-DD as vX.Y.Z
**PR:** #<number>

## What shipped

<2-3 paragraphs describing the end state>

## Deviation from plan

<anything that changed during execution vs the original plan>

## Files changed

- `<path>` - <one-line purpose>
- ...

## What's next

<follow-up work that was deliberately deferred, with links to spin-off projects if any>
```

### 3c. Update the project README

Check off completed items in `projects/<slug>/README.md`. Update the "Files changed" and "Architecture notes" sections if appropriate. Do NOT update status / phase / tags in the README - those live in your task tracker, not in narrative files.

### 3d. Mark the project done (if release session)

If this session closed the project - update its status in your task tracker (database row, ClickUp task, Linear issue, GitHub issue, or whatever you use) to "done".

If this is a patch session, leave status as `in_progress`.

---

## Step 4: Commit + push

```bash
git add docs/progress-log.md docs/patches/ projects/ pyproject.toml package.json VERSION
git commit -m "session N close: <one-line summary> (vX.Y.Z)"
git push
```

Commit message rules: lowercase, under 72 chars, no period at end, no Co-Authored-By trailer unless the user explicitly asks.

---

## Step 5: Mark PR ready + merge

```bash
gh pr ready
gh pr merge --squash --delete-branch
```

For shared / engineer-owned repos with CODEOWNERS, wait for the auto-requested review before merging. For solo repos, squash-merge immediately.

---

## Step 6: Verify the deploy (if applicable)

A project is NOT shipped until the change is live in production. If the repo deploys on push to main:

1. Wait for the deploy to complete (`gh run watch`, `railway logs --deployment`, or your platform's equivalent).
2. Verify the new version is serving - hit a `/health` endpoint or a page that surfaces the version string.
3. Probe a live affordance the change introduced - a new column, a new copy string, a new route. DOM-level verification, not just "build succeeded."

If the deploy is intentionally gated (feature flag, scheduled cutover), say so explicitly at closeout and schedule the verification for the flip date. Don't silently close on a build-but-not-live state.

---

## Step 7: Session-close output

Produce the closeout message in chat. Two formats:

### Release close (minor bump)

```
─────────────────────────────────────────
🚢 Shipped vX.Y.Z - <Project Title>
─────────────────────────────────────────

What was built:
- <bullet>
- <bullet>

Artifacts:
- Plan:   projects/<slug>/plan.md
- README: projects/<slug>/README.md
- Report: projects/<slug>/report.md
- Patch:  docs/patches/vX.Y.Z.md (if applicable)

PR: <url>
Live: <production url>

Next up: <one-line recommendation>
```

### Patch close

```
Session N closed - vX.Y.Z (patch)

- <bullet>
- <bullet>

Patch report: docs/patches/vX.Y.Z.md
PR: <url>
```

---

## When to skip

- Pure research or planning sessions with no code changes.
- Sessions whose only output is a plan file (plan-to-project promotion handles those).

---

## Hard rules

- Never amend a published commit. Always create a new commit.
- Never force-push to main. Branches you own can be force-pushed before sharing.
- Never bypass `--no-verify` on commit. If a hook fails, fix the underlying issue.
- Never run destructive git operations (reset --hard, branch -D) without explicit user authorization.
- Push immediately after commit. A commit that hasn't been pushed is invisible to other sessions, CI, and GitHub notifications.
