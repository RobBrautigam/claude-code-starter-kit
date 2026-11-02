---
name: scaffold-repo
description: Scaffold a new repo from an empty directory or backfill an existing repo with global standards. Triggers on "scaffold repo", "scaffold project", "set up this repo", "backfill this project", "bring this repo up to standard".
---

# Scaffold Repo

Two-mode skill that either scaffolds a brand new repo or backfills an existing one with your global standards.

## Mode Detection

Check the current working directory:

- **No `package.json`, no `pyproject.toml`, no `CLAUDE.md`, and fewer than 5 files** --> Mode 1: Full Scaffold
- **Existing code, dependencies, or CLAUDE.md** --> Mode 2: Backfill

Announce which mode was detected before proceeding.

---

## Mode 1: Full Scaffold

For empty or near-empty directories (you've created the folder and opened it in your editor).

### Step 1: Gather Info

Ask the user for:
1. **Repo name** -- confirm or adjust from directory name
2. **One-line description** -- what this repo is for
3. **What are you building?** -- open-ended, to determine tech stack. Ask follow-ups if unclear.

### Step 2: Scaffold Based on Answers

**Frontend (website, dashboard, internal tool):**
```bash
# Next.js (for websites, apps with API routes)
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
npx shadcn@latest init

# OR Vite + React (for pure dashboards, no SSR needed)
npm create vite@latest . -- --template react-ts
npm install -D tailwindcss @tailwindcss/vite
npx shadcn@latest init
```

**Tailwind v4 is CSS-first. Common gotchas:**
- Do NOT create a `tailwind.config.js` - configuration lives in a `@theme` block in `src/index.css` (or `app/globals.css` for Next.js)
- Do NOT create a `postcss.config.js` for Vite projects - `@tailwindcss/vite` handles it
- Do NOT install `autoprefixer` - v4 ships Lightning CSS with vendor prefixing built in
- Plugins load via `@plugin '<name>';` directive in CSS, not a `plugins: []` array
- Dark mode variant: `@custom-variant dark (&:is(.dark *));` in CSS
- Vite config must import and call the plugin: `import tailwindcss from "@tailwindcss/vite"` and add `tailwindcss()` to `plugins: []`

- Configure ESLint
- Set up path aliases in `tsconfig.json`
- Create `CLAUDE.md` (see template below)
- Create a `DESIGN.md` / `DESIGN_SYSTEM.md` capturing the visual direction (colors, typography, spacing, components) and ask the user about customization
- Create `.env.example` with common variables
- Verify `.gitignore` includes `.env*`, `node_modules/`, `.next/`, `dist/`
- Optionally add a `renovate.json` (see "Renovate config" below)

**Backend service (API, worker, cron job):**
```bash
python -m venv venv
pip install fastapi uvicorn python-dotenv
```
- Create `main.py` with a health check endpoint
- Create `requirements.txt`
- Create `CLAUDE.md`
- Create `.env.example`
- Verify `.gitignore` includes `.env*`, `venv/`, `__pycache__/`, `*.pyc`
- Optionally add a `renovate.json` (see "Renovate config" below)

**CLI tool:**
- Ask the user: Python or Node.js?
- Set up minimal project structure
- Create `CLAUDE.md`
- Verify `.gitignore`

**Multi-service (frontend + backend):**
- Ask follow-up questions about components needed
- Create subdirectory structure (e.g., `dashboard/`, `sync/`, `api/`)
- Each subdirectory gets its own dependencies
- Root `CLAUDE.md` describes the overall architecture

### Step 3: Finalize

```bash
git init
git add -A
git commit -m "initial scaffold"
```

**Install the pre-commit hook - placement depends on the repo's language** (per `rules/git-conventions.md`):

- **TypeScript / Node repos (has a root `package.json`):** use **husky + lint-staged** so the guard checks AND auto-lint/format run on every commit, committed to the repo (survives clones - no per-clone reinstall). Steps:
  ```bash
  npm i -D husky lint-staged prettier            # + prettier-plugin-tailwindcss if Tailwind
  npm pkg set scripts.prepare="husky"
  npx husky init                                 # creates .husky/ and wires core.hooksPath
  ```
  Add a `lint-staged` block to `package.json`:
  ```json
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{json,md,css}": ["prettier --write"]
  }
  ```
  Write `.husky/pre-commit` as a **composite hook** - your guard checks first, then `npx lint-staged` (or `pnpm exec lint-staged`). Because husky sets `core.hooksPath=.husky`, any guard you rely on MUST live inside `.husky/pre-commit` - a `.git/hooks/pre-commit` would be silently bypassed.

- **Python-only repos (no root `package.json`):** install the composite hook at `.git/hooks/pre-commit`, then `chmod +x .git/hooks/pre-commit`. Not versioned - reinstall on every fresh clone.

A common guard check is an **identity guard** - block a commit if `git config user.email` is an address you never want authoring commits in this repo (e.g. a work email in a personal repo, or vice versa). Example check:

```sh
#!/bin/sh
email=$(git config user.email)
case "$email" in
  *@wrong-domain.example*)
    echo "ERROR: commit blocked - user.email is '$email' (wrong identity for this repo)."
    echo "Fix: git config --local user.email <the-correct-address>"
    exit 1
    ;;
esac
exit 0
```

A second common check is a **non-blocking direct-to-main warning** that nudges you to branch. Both checks are language-agnostic; husky just adds lint-staged on top and makes the hook survive clones.

**Create the GitHub repo (private by default):**
```bash
gh repo create <your-account>/{name} --private --source=. --remote=origin --push
```
Never use `--public` without explicit intent.

**Start the dev server and verify:**
- Start the dev server process(es) in the background
- Wait for startup, then verify with a health check or HTTP 200
- Confirm to the user what URL to open (e.g., `http://localhost:3000`)
- Record the dev server commands + ports in the project `CLAUDE.md` (Local Development section below) so future sessions can start them automatically

**Optionally register the repo** in whatever task tracker you use (filesystem READMEs, Linear, GitHub issues, a database). Then print a summary of what was created.

---

## Mode 2: Backfill

For existing repos that predate your global config standards.

### Step 1: Audit

Check for these files and configurations:

| Check | Status |
|---|---|
| `CLAUDE.md` exists? | |
| `CLAUDE.md` references global config? | |
| `DESIGN.md` / `DESIGN_SYSTEM.md` exists? (frontend only) | |
| `.env.example` exists? | |
| `.gitignore` comprehensive? | |
| ESLint configured? (frontend only) | |
| Path aliases configured? (frontend only) | |
| `renovate.json` exists? (optional) | |
| Pre-commit hook installed? (TS repos: husky `.husky/pre-commit` + lint-staged; Python-only: `.git/hooks/pre-commit`) | |
| `husky` + `lint-staged` in `package.json`? (TS repos only) | |

### Step 2: Report

Tell the user what is missing and what needs updating. Do not make changes without permission.

### Step 3: Backfill

With permission, create or update:
- Add or update `CLAUDE.md` to include a global reference note at the top:
  > Global standards inherited from `~/.claude/CLAUDE.md` and `~/.claude/rules/`. This file contains only project-specific configuration.
- Add `DESIGN.md` / `DESIGN_SYSTEM.md` (ask about customization)
- Add `.env.example` if missing
- Update `.gitignore` if incomplete
- Optionally add `renovate.json` (see "Renovate config" below)
- Install the pre-commit hook by language: **TS repos** get husky + lint-staged + a composite `.husky/pre-commit` (see Mode 1 Step 3, and `husky-backfill-checklist.md` in this skill dir for the safe procedure that preserves any existing guard); **Python-only repos** get the composite `.git/hooks/pre-commit`. For an existing TS repo that already has a `.git/hooks/pre-commit`, follow the backfill checklist so the `core.hooksPath` flip to `.husky` does NOT orphan that guard.

**Do NOT:**
- Touch existing code, components, or project structure
- Install new dependencies without asking
- Modify existing configuration files without asking

---

## Project CLAUDE.md Template

When creating a new CLAUDE.md for a scaffolded repo, use this structure:

```markdown
# {Project Name}

> Global standards inherited from `~/.claude/CLAUDE.md` and `~/.claude/rules/`. This file contains only project-specific configuration.

## Overview
{One-line description}

## Tech Stack
- {Framework}
- {Language}
- {Database, if any}
- {Deployment platform}

## Key Files
- {List important files and directories}

## Local Development

Start these processes to run locally:

| Process | Command | Port |
|---|---|---|
| {Server/Frontend/etc} | `{dev command}` | {port} |

Access at: http://localhost:{port}

## Commands
- `{dev command}` -- Start dev server
- `{build command}` -- Production build
- `{test command}` -- Run tests

## Environment Variables
- **Source:** {Platform} (`{pull command}`)
- See `.env.example` for required variables

## Deployment
- **Platform:** {your host}
- **Trigger:** Auto-deploy on push to main
```

---

## Renovate config (optional)

If you use [Renovate](https://docs.renovatebot.com/) for automated dependency updates, add a `renovate.json` at the repo root. The simplest version extends Renovate's recommended preset:

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended"]
}
```

If you maintain your own shared policy preset in a separate repo, extend that instead (e.g. `"github>your-account/renovate-config//single-app"`). Then install the Renovate GitHub App on the new repo at https://github.com/apps/renovate.

**Validation (optional but recommended):**
```bash
npx --yes --package renovate -- renovate-config-validator renovate.json
```
