# Organize Your Computer for Claude Code (the zero-install version)

*You've been using Claude Code for months. It works - but your repos are everywhere: a few on the Desktop, some in Documents, one or two wherever VS Code happened to clone them, maybe half of them silently syncing to iCloud or OneDrive. Every prompt that references a path is a guess, worktrees have nowhere sane to live, and "where is that project?" has six answers.*

*This doc fixes that in one sitting. It's the copy-paste version of the kit's [`setup-doctor`](skills/setup-doctor/SKILL.md) skill - paste the prompt below into any Claude Code conversation, no install needed. (If you install the kit, you get the same thing as a `/setup-doctor` command forever.)*

## The target state

- **One flat dev root** - `C:\dev\` on Windows, `~/dev` on Mac. One folder per repo. That's the whole filing system.
- **Nothing in Desktop / Documents / Downloads / any cloud-synced folder.** Cloud sync (iCloud, OneDrive, Dropbox) fighting `.git` and `node_modules` is the single most common silent corruptor of a dev machine.
- **Every repo equipped:** a `CLAUDE.md` at its root (what the project is, the commands, the foot-guns) and a `.claude/` folder for repo-specific rules - so every conversation starts with real context instead of re-explaining the project.
- **The global level set:** `~/.claude/CLAUDE.md` for who you are and how you work, plus shared skills/rules (this kit).

Why one flat root matters more than it looks: every future habit - starter prompts, parallel worktrees (`~/dev/myrepo-featurename`), scripts, multi-window orchestration - gets to ASSUME the path shape. Organization compounds. So does scatter.

## The prompt (paste into Claude Code, anywhere)

````
You are my SETUP DOCTOR. My Claude Code setup has accreted over months and my repos are scattered across this computer. Fix it in five phases. Detect my OS (Windows vs macOS) and use the right commands throughout. HARD SAFETY RULE: phases 1-2 are strictly read-only; you MOVE nothing until I approve the plan, and you DELETE nothing without a per-item yes from me.

PHASE 0 - GLOBAL SNAPSHOT. Check ~/.claude/ (does CLAUDE.md exist? skills/? rules/?). Note what's there.

PHASE 1 - INVENTORY. Find every git repo on this machine: search my home directory and the usual scatter zones (Desktop, Documents, Downloads, source, repos, projects, OneDrive/iCloud paths), skipping node_modules / Library / trash. Ask me if there are other places repos might live. For each repo: path, origin remote, branch, dirty or clean, unpushed commits, last commit date, and FLAGS: inside a cloud-synced folder? duplicate clone of the same remote? no remote at all? linked git worktrees? does it have a CLAUDE.md / .claude folder? Show me ONE table.

PHASE 2 - PLAN. Propose the migration: everything to ONE flat dev root (C:\dev\ on Windows, ~/dev on Mac), one folder per repo named after the repo. Duplicates: pick a keeper, send the other to <dev-root>/_archive (never straight to deletion). Dirty repos: list exactly what must be committed/pushed before moving. Repos with no remote: propose creating a private GitHub repo or archiving - my call each. Repos with linked worktrees: move the main checkout then git worktree repair. Cloud-synced repos move FIRST (highest risk). Then STOP and wait for my approval.

PHASE 3 - MIGRATE (only after my approval). Per repo: verify clean + pushed, have me close any editor holding it, move it, then verify (git status clean, git fetch works, worktrees repaired). One repo at a time, logged.

PHASE 4 - EQUIP. For every repo in the dev root: draft a CLAUDE.md at its root by READING the repo (README, manifests, scripts) - what it is, the stack, install/run/test/deploy commands, conventions, and its top 3-5 foot-guns. Keep each under a screen or two. Create .claude/rules/ (empty is fine), commit CLAUDE.md + .claude/ to git, add .claude/settings.local.json to .gitignore. Check .gitignore covers .env + OS junk, and that a .env.example exists wherever there's a .env. Show me each CLAUDE.md draft for a quick review before committing.

PHASE 5 - VERIFY + REPORT. One final table: every repo, new path, clean/pushed, CLAUDE.md, .claude/, flags cleared. Then tell me the one-line rule that now answers "where is everything?" on this machine.
````

## After the cleanup

1. **Install this kit** so the discipline layer (skills + rules + the global CLAUDE.md template) applies everywhere - see the [README](README.md) install prompt.
2. **Go multi-window.** With a flat dev root, parallel Claude Code sessions via git worktrees + an orchestrator conversation become natural: https://github.com/RobBrautigam/ai-orchestrator
3. **Keep it clean:** every new repo gets cloned straight into the dev root, gets its `CLAUDE.md` on day one, and never touches Desktop again.
