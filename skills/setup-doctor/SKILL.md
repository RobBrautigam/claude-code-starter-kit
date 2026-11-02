---
name: setup-doctor
description: Diagnose and fix a messy Claude Code setup across the ENTIRE computer - Windows or Mac. Finds every git repo scattered around the machine (Desktop, Documents, Downloads, cloud-synced folders, random editor clone locations), plans a migration into ONE flat dev root, moves repos only after explicit approval with git-safety checks, then equips every repo with a CLAUDE.md + .claude/ folder and baseline hygiene. Use when the operator says "/setup-doctor", "organize my repos", "clean up my claude code setup", "my folders are a mess", "set up my computer for claude code", or when starting Claude Code on a machine with repos in scattered locations.
---

# Setup Doctor

Turn a scattered, accreted Claude Code setup into one organized system: **every repo in one flat dev root, every repo equipped with a `CLAUDE.md` and a `.claude/` folder, the global `~/.claude/` level configured.** Works identically on Windows and macOS - detect the OS first and use the right commands throughout.

**The prescribed convention (opinionated on purpose):**

- **One flat dev root:** `C:\dev\` on Windows, `~/dev` on macOS/Linux. One folder per repo, folder name = repo name. No nesting, no "projects/clients/2024" trees.
- **Never** inside Desktop, Documents, Downloads, or ANY cloud-synced directory (iCloud, OneDrive, Dropbox, Google Drive). On a Mac, "Desktop & Documents in iCloud" is the classic trap: iCloud syncing `node_modules` and `.git` churn corrupts state, burns bandwidth, and breaks locks. On Windows, OneDrive's Documents folder does the same.
- Why flat + predictable: starter prompts, worktree siblings (`~/dev/myrepo-featurename`), scripts, and every future orchestration habit can assume the path shape. Organization compounds; scatter compounds too.

**The safety posture (non-negotiable): scan first, plan second, MOVE ONLY AFTER EXPLICIT APPROVAL.** Never move, delete, or rewrite anything during the scan. The operator approves the plan as a whole and any deletion individually.

## Phase 0 - Snapshot the global level (read-only)

- Does `~/.claude/` exist? `CLAUDE.md`? `skills/`? `rules/`? Note what's there.
- Which editor(s) and terminals are in play (VS Code, Cursor, plain terminal)? Ask the operator only if it isn't obvious.
- Detect OS + shell and say which command set you'll use.

## Phase 1 - INVENTORY: find every repo on the machine (read-only)

Search the common scatter zones, skipping heavy noise. Time-box it; ask before scanning unusual drives.

macOS / Linux:

```bash
find ~ -maxdepth 6 -type d -name .git \
  \( -path "*/Library/*" -o -path "*/node_modules/*" -o -path "*/.Trash/*" \) -prune -o \
  -type d -name .git -print 2>/dev/null
```

Windows (PowerShell) - scan the likely roots rather than all of `C:\`:

```powershell
$roots = "$HOME\Desktop","$HOME\Documents","$HOME\Downloads","$HOME\source","$HOME\repos","$HOME\projects","C:\dev","$HOME\OneDrive"
foreach ($r in $roots) { if (Test-Path $r) {
  Get-ChildItem $r -Recurse -Depth 5 -Force -Directory -Filter ".git" -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty Parent | Select-Object -ExpandProperty FullName
}}
```

Also ask the operator: "any other place you know repos live?" (external drives, a work folder, a VM share).

For EACH repo found, gather (read-only): path · `origin` remote URL · current branch · dirty/clean (`git status -s`) · ahead/behind upstream · last commit date · approximate size · **flags**: inside a cloud-synced dir? duplicate clone (same remote as another find)? no remote at all? a linked git worktree (`git worktree list` shows siblings)? Claude Code presence (`CLAUDE.md`? `.claude/`?).

Output: one table, one row per repo, with flags. This table is the diagnosis.

## Phase 2 - PLAN: propose the target layout (still read-only)

Present a migration plan and STOP for approval:

- Target: `<dev-root>/<repo-name>` for every repo (kebab-case, matching the remote name).
- **Duplicate clones of the same remote:** pick the keeper (freshest, or the one with unpushed work); compare branches + stashes on the loser; propose the loser goes to `<dev-root>/_archive/<name>-dupe` (NOT deleted - deletion only later, per-item, with explicit approval).
- **Repos with uncommitted or unpushed work:** the plan lists exactly what's dirty; those get committed/pushed (or deliberately stashed with a note) BEFORE any move.
- **Repos with no remote:** propose creating a private GitHub repo (`gh repo create <name> --private --source . --push`) or archiving - operator's call per repo.
- **Repos with linked worktrees:** move the MAIN checkout first, then run `git worktree repair` from it (git >= 2.30); or remove + re-add the worktrees. Never move a linked worktree folder naively.
- **Cloud-synced locations:** flagged rows move out as the highest-priority items; on a Mac also tell the operator if "Desktop & Documents" iCloud sync is on (System Settings > Apple ID > iCloud Drive), because anything left there stays at risk.
- Note: editors' "recent projects" lists will point at old paths after the move - reopen from the new location once.

Wait for the operator's explicit "go" on the plan. Deletions are NEVER part of the bulk approval.

## Phase 3 - MIGRATE (approved moves only)

Per repo, in this order:

1. Pre-flight: `git -C <old> status -s` (must be clean or deliberately stashed) · everything pushed (`git -C <old> log --oneline @{u}..` empty, per branch that matters).
2. Close editors/terminals holding the folder (Windows file locks; ask the operator to close windows if a move fails on a lock).
3. Move: `Move-Item <old> <new>` (PowerShell) / `mv <old> <new>` (bash). Moving a git repo is safe - its internals use relative paths.
4. Verify: `git -C <new> status` clean · `git -C <new> fetch` works (remote intact) · if it had worktrees, `git -C <new> worktree repair` then `git worktree list` is sane.
5. Only then proceed to the next repo. Log each move as done.

Archive-not-delete: duplicates and dead repos go to `<dev-root>/_archive/`. Offer per-item deletion at the END, one by one, each with its own yes.

## Phase 4 - EQUIP every repo (the Claude Code layer)

For each repo now in the dev root, set up the baseline (generate drafts by READING the repo - its README, manifests, scripts - then let the operator review):

- **`CLAUDE.md` at the repo root** - from the kit's [templates/repo-CLAUDE.md](../../templates/repo-CLAUDE.md): what the project is (2-3 sentences), the stack, the commands that matter (install / run / test / deploy), conventions, and a short "sharp edges" list of this repo's foot-guns. Keep it under a screen or two - it loads into every conversation; bloat costs every session.
- **`.claude/` folder:** `.claude/rules/` for repo-specific rules (empty is fine to start), `.claude/skills/` only if the repo needs repo-local skills. Commit `CLAUDE.md` and `.claude/` to git; add `.claude/settings.local.json` to `.gitignore` (it's personal/machine-local).
- **Hygiene checks:** `.gitignore` covers `.env`, `node_modules`/build dirs, and OS junk (`.DS_Store` on Mac, `Thumbs.db` on Windows) · a `.env.example` exists if the repo uses a `.env` · `git config user.email` has no surprising local override.
- **Global level (once):** `~/.claude/CLAUDE.md` from this kit's `CLAUDE.md.example` (personal identity, decision authority, standards), plus the kit's skills + rules installed per the README.

## Phase 5 - VERIFY + the final report

End with one table: every repo · new path · clean/pushed ✓ · CLAUDE.md ✓ · .claude/ ✓ · flags cleared. The end state to aim for: **the operator can answer "where is X?" for every project on the machine with one rule, and every repo boots Claude Code with real context.**

Then offer the natural next step: with everything in one flat root, the machine is ready for multi-window parallel work - the sibling-worktree + orchestrator method lives at https://github.com/RobBrautigam/ai-orchestrator.

## Do not

- Move anything before the plan is approved. Delete anything without a per-item yes.
- Touch repos that are actively open in another Claude Code conversation (ask the operator to close them first - two sessions in one folder corrupt each other).
- Use `git worktree remove --force` on anything (a partially-failed forced delete can damage the shared main checkout).
- Scan network drives, VMs, or backup volumes without asking.
