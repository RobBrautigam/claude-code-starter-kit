# Onboarding - Claude Code skills + rules

This package contains a curated set of Claude Code skills, rules and safety hooks I've been refining in daily use for many months. They sit on top of two open frameworks:

- **Superpowers** by Obra (https://github.com/obra/superpowers) - the brainstorm → plan → execute → review chain referenced throughout. Install that first.
- The rules and skills in this package - discipline + workflow on top of Superpowers.

## Quick install (the 30-second version)

From the cloned folder, with Python 3.9 or newer:

```bash
python scripts/install.py --dry-run    # shows what would be copied; writes nothing
python scripts/install.py              # copies skills and rules into ~/.claude
```

It never overwrites a file you changed (pass `--force` to replace, with a backup kept), never touches an existing `~/.claude/CLAUDE.md`, and never deletes anything. Add `--with-hooks` for the command guard (see [hooks/README.md](./hooks/README.md)).

Or paste this prompt into a fresh Claude Code conversation **inside the cloned folder** and let the agent do the copying:

````
I have a folder of Claude Code skills and rules I want to install. The folder structure is:

  skills/        - each subfolder is a skill (SKILL.md inside)
  rules/         - each file is a discipline / workflow rule
  CLAUDE.md.example - example global config

Please install them at the global Claude Code level (~/.claude/) so they apply to every repo. Specifically:

1. Copy every subdirectory under skills/ to ~/.claude/skills/ (preserving the SKILL.md and any bundled files like scripts/).
2. Copy every file under rules/ to ~/.claude/rules/.
3. Show me my current ~/.claude/CLAUDE.md (if it exists). If it doesn't exist, copy CLAUDE.md.example to ~/.claude/CLAUDE.md and tell me to edit the placeholders. If it exists, do NOT overwrite - show me the diff against CLAUDE.md.example and ask whether I want to merge, replace, or leave it alone.
4. Verify the install: list ~/.claude/skills/ and ~/.claude/rules/ so I can see what landed.
5. Tell me to restart Claude Code (or start a fresh conversation) so the new skills auto-register.

Use the Bash tool for file copies. On Windows use PowerShell syntax; on macOS / Linux use cp -R.
````

That's it. Claude Code will copy the files, show you what got installed, and tell you what to edit.

---

## What's in this package

### Skills (14)

| Skill | What it does | When to use |
|---|---|---|
| `setup-doctor` | Whole-computer cleanup: finds every scattered git repo, plans a move into one flat dev root (only after your approval), moves them with git-safety checks, and gives each repo a `CLAUDE.md` + `.claude/` folder. | First install on a machine with history, or whenever repos drift back into the Desktop and Documents. Trigger: "organize my repos", "set up my computer for Claude Code". |
| `project-scaffolder` | Scaffolds a new project from minimal input: `projects/<slug>/` with rich README (origin brief, definition of done, copy-paste starter prompt) plus empty `plan.md` and `report.md` stubs. Supports spin-off mode for ideas that surface mid-project. | Any time you start a new project, OR mid-session when an unrelated idea comes up that you want to capture. Trigger: "start a new project", "scaffold X", "spin off Y". |
| `project-manager` | Session guardrails. Runs the full Superpowers chain (brainstorm → plan → execute → verify → review → ship), creates feature branches + draft PRs at session start, enforces scope discipline. | Any project session. Trigger: "let's work on X", "next project", or just paste a starter prompt. |
| `ship` | Session-close workflow. Version bump, progress log, patch / release report, commit, push, PR merge, deploy verification. | At the end of every session that produced meaningful changes. Trigger: `/ship`, "ship it", "wrap up". |
| `session-handoff` | Structured end-of-session summary for `/clear` + fresh conversation. NOT a project close - this is for context continuity when the conversation is getting long. | When context is getting heavy and you want to start fresh without losing the thread. Trigger: "session handoff", "save context", "prep a handoff". |
| `daily-review` | Lightweight 2-minute morning check-in. Surfaces today's scheduled projects, asks for quick adjustments. | First thing in the morning. Trigger: `/daily-review`, "what should I work on today", "morning check". |
| `weekly-review` | 15-25 minute weekly planning. Curates the todo queue, assigns target dates, audits stuck-in-progress items. | Once a week, ideally Sunday evening or Monday morning. Trigger: `/weekly-review`, "plan my week". |
| `skill-creator` | Create new skills and iteratively improve existing ones. Includes the philosophy + structure of a good skill. | When you notice a workflow repeating 3+ times. Trigger: "create a skill", "turn this into a skill". |
| `research` | Deep, context-aware research, free sources first (GitHub, web search, plain fetches). Runs multi-angle queries, synthesizes through your business lens, saves a full report with its sources. | When you need real research, not just a web search. A Perplexity key is optional (a paid fallback). Trigger: "research X", "look into Y", "dig into Z". |
| `scaffold-repo` | Two-mode: scaffold a brand-new repo (Tailwind v4 CSS-first, path aliases, project `CLAUDE.md`, pre-commit hook placed correctly by language) or backfill an existing repo to standard. Bundles a husky-backfill checklist that prevents `core.hooksPath` from orphaning an existing guard. | Setting up a fresh empty directory, or bringing an old repo up to your conventions. Trigger: "scaffold repo", "set up this repo", "backfill this project". |
| `explore-codebase` | Navigate a large codebase structurally (architecture, modules, callers/callees, flows) via the `code-review-graph` MCP graph, with a mandatory freshness check. | Repos over ~100 files where a structural question would take 3+ greps. Requires the `code-review-graph` MCP server. |
| `debug-issue` | Trace a bug through call chains + execution flows and detect whether a recent change caused it. Pairs with `superpowers:systematic-debugging`. | Multi-module bugs on a large repo where you don't know the entry point. Requires `code-review-graph`. |
| `refactor-safely` | Preview a refactor's full blast radius (rename sites, dependents, dead code, affected flows) before touching code. | Cross-file renames/moves/decomposition on a large repo. Requires `code-review-graph`. Never delete graph-flagged "dead" code without a confirming read + tests. |
| `review-changes` | Risk-aware review of a changeset by blast radius and test coverage, not just diff lines. Composes with `superpowers:requesting-code-review`. | Reviewing a branch/PR diff that touches shared code on a large repo. Requires `code-review-graph`. |

### Rules (24)

All rules auto-load in every conversation. They cover:

| Rule | What it enforces |
|---|---|
| `communication-style.md` | Four laws (plain English, volume cap, one ask per message, short paragraphs), action-first replies, no buzzwords |
| `coding-conventions.md` | Language defaults, testing, linting, security baseline |
| `git-conventions.md` | Lowercase commits under 72 chars, no AI co-author trailer, always branch + draft PR |
| `development-workflow.md` | Localhost-first, shadcn/ui, design systems, no orphaned processes |
| `verify-before-done.md` | "Done" needs evidence from the exercised surface; a new test counts only after it has been seen to fail |
| `research-first.md` | A research pass sized to the build before building, free sources first |
| `process-hygiene.md` | Every session stops what it started, by process id, never by name |
| `public-repos.md` | Nothing private in a public repository: visibility check, private denylist, pre-push guard |
| `agent-fleet-cost.md` | Explicit model and effort on every agent in a fan-out; a wide cheap base, a narrow expensive tip |
| `graph-index-tool-adoption.md` | Measure an index or graph tool against plain grep on your own corpus before adopting it |
| `concurrent-sessions.md` | Multi-conversation safety - worktrees mandatory for parallel work |
| `session-types.md` | How to identify quick fix vs project vs strategy session at the start |
| `best-of-best-modeling.md` | Model Linear / Stripe / Anthropic / Vercel in every decision |
| `brainstorming-question-filter.md` | Lead with a recommendation, never pure-options questions |
| `pushback-on-request.md` | Genuine challenge when asked, not validation in disguise |
| `tdd-loop-discipline.md` | Single-file tests during iteration, full suite at preflight only |
| `use-gha-not-local-ci.md` | Push to CI, don't burn local CPU on full builds |
| `code-review-graph-usage.md` | When (and when NOT) to use the code-review-graph MCP; the freshness law; advisory trust boundary |
| `sharp-edges-convention.md` | Top prod-breaking foot-guns get an inline CLAUDE.md section + a mechanical CI/lint gate |
| `no-bash-heredocs.md` | Heredocs through the Bash tool only when short and plain (no backslashes); otherwise the Write tool, then run the file |
| `autopilot-and-scope-checks.md` | Scope anomalies pause autopilot, even when "full autopilot" was authorized |
| `starter-prompt-code-block-integrity.md` | Use 4-backtick fences for any prompt containing inner code blocks |
| `session-handoffs-required.md` | Always deliver starter prompt + ship + summary when ending a session |
| `session-loose-ends-audit.md` | At session close, account for every idea/aside raised, each with an honest disposition tag |

### Hooks (3)

Rules say what to do; hooks check it at the moment of action. Setup, exit codes and the override are in [hooks/README.md](./hooks/README.md).

| Hook | What it refuses |
|---|---|
| `hooks/guard_bash.py` | (Claude Code PreToolUse) `--no-verify`, a force push to main, `git reset --hard`, kill by name, dropping a database or table, `rm -rf` on a root folder, heredocs with backslashes |
| `hooks/git/commit-msg` | `Co-Authored-By:` trailers and "Generated with ..." lines in commit messages |
| `hooks/git/public_repo_guard.py` | (pre-push) a name from your private denylist going to a public repository |

### CLAUDE.md.example

A template for your global `~/.claude/CLAUDE.md` file. This is what tells Claude Code who you are, what you're building, and which rules / skills to honor by default. Edit the placeholders (`<Your Name>`, `<Role>`, tech stack) before installing.

---

## How the pieces fit together

The mental model:

```
~/.claude/CLAUDE.md            ← who you are, what you're building, points at rules
~/.claude/rules/*.md           ← discipline, auto-loaded into every conversation
~/.claude/skills/<name>/       ← workflows, invoked when their trigger phrases hit
```

A typical session:

1. **Morning:** "morning check" → invokes `daily-review` → surfaces today's projects.
2. **Start a project:** "let's work on the auth migration" → invokes `project-manager` → reads README, scope-checks, creates feature branch, runs Superpowers brainstorming → writes a plan → executes → verifies.
3. **End session:** "let's ship" → invokes `ship` → bumps version, writes progress log + report, commits, pushes, merges PR, verifies deploy.
4. **Context heavy mid-project:** "session handoff" → invokes `session-handoff` → produces a chat-only summary you can paste into a fresh conversation.
5. **Weekly:** "weekly review" → invokes `weekly-review` → curates the queue for the coming week.
6. **Research:** "research the AI agency pricing landscape" → invokes `research` → GitHub and web queries from 2-4 angles + synthesis + saved report with sources.
7. **Notice a pattern:** "this workflow keeps repeating, make it a skill" → invokes `skill-creator` → drafts + tests a new skill.

---

## Required dependencies

### Superpowers (mandatory)

Many of these skills reference `superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:subagent-driven-development`, etc. These come from the Superpowers plugin by Obra.

Install: https://github.com/obra/superpowers

Until Superpowers is installed, the `project-manager` and `ship` skills will reference skills that don't exist yet - the workflow degrades gracefully (Claude will narrate the steps instead of invoking the skill) but the full value comes from having Superpowers installed.

### Python 3.9 or newer

For `scripts/install.py`, the hooks and the tests. Standard library only.

### Perplexity API key (optional, for the research skill's paid fallback)

The research skill uses free sources first and calls this paid API only when they come back thin. Get a key at https://www.perplexity.ai/settings/api. Then either:

```bash
export PERPLEXITY_API_KEY=pplx-...
```

Or add to `~/.claude/.secrets.env`:

```
PERPLEXITY_API_KEY=pplx-...
```

The research script checks env var first, then standard secret locations.

### GitHub CLI (recommended)

Used by the `ship` and `project-manager` skills for PR creation, status checks, and merges:

```bash
# Install: https://cli.github.com/
gh auth login
```

### code-review-graph MCP (only for the four code-graph skills)

`explore-codebase`, `debug-issue`, `refactor-safely`, and `review-changes` all drive the [`code-review-graph`](https://pypi.org/project/code-review-graph/) MCP server. Register it once at user scope (in `~/.claude.json`) so it's available in every repo:

```json
"code-review-graph": {
  "command": "uvx",
  "args": ["code-review-graph", "serve"]
}
```

It's lazy - the process idles until you build a graph (`uvx code-review-graph build` from a repo root) and call a tool. Without it, those four skills have nothing to drive; the rest of the kit is unaffected.

### Codex plugin (optional)

`review-changes` and `scaffold-repo` reference `/codex:review` / `/codex:adversarial-review` for an independent adversarial review pass. If you don't use Codex, read those as "run a deeper review here" prompts - nothing breaks without it.

---

## Adapting to your stack

These skills are written to be tracker-agnostic. Where the original versions queried a Supabase database for project records, the white-labeled versions say "your task tracker - substitute filesystem READMEs, ClickUp, Linear, GitHub issues, or whatever you actually use."

The recommended starting point: filesystem-only. Every project gets a `projects/<slug>/` folder with `README.md` + `plan.md` + `report.md`. The skills assume this layout by default. Upgrade to a database / Linear / etc. later if you outgrow files.

---

## Customizing further

The fastest way to make these your own:

1. Install as-is using the prompt above.
2. Use them for a week.
3. Notice anything that doesn't fit your workflow.
4. Edit the rule or skill file directly at `~/.claude/rules/<file>.md` or `~/.claude/skills/<skill>/SKILL.md`.
5. Restart Claude Code (or start a fresh conversation) - your edits load on next session.

Skills are just markdown files. There's no compile step, no rebuild, no plugin manifest. Edit and reload.

---

## Troubleshooting

**"The skill isn't triggering when I expect."**
Read the skill's frontmatter `description` field. The triggering language is in there. If your wording is too far from what the description names, the skill won't fire. Either rephrase to match, or edit the description to include your phrasing.

**"The skill triggered but produced something weird."**
Read the SKILL.md body. It's a markdown spec - Claude follows it. If the spec has gaps, fill them. If the spec is wrong for your case, edit it.

**"Two skills are fighting for the same trigger."**
Edit one of the descriptions to be narrower. Skills cooperate via specificity - the one with the more specific match wins.

**"Restarting Claude Code didn't pick up my edit."**
Fully quit Claude Code (close its terminal, or the editor window it runs in) and reopen it. If a Claude Code process is still running, stop that one process by its id (Activity Monitor or `ps` on macOS and Linux, Task Manager on Windows). Never stop processes by name; see `rules/process-hygiene.md`.

---

That's the whole package. Use it, fork it, change anything you want.
