# Husky + lint-staged Backfill Checklist (existing TS repos)

How to add husky + lint-staged to an **existing** TypeScript/Node repo WITHOUT silently losing any pre-commit guard you already rely on (an identity check, a direct-to-main warning, etc.).

## The trap this prevents

Installing husky sets `git config core.hooksPath .husky`. Git then runs `.husky/pre-commit` and **ignores `.git/hooks/pre-commit` entirely.** If your identity/branch guard lived in `.git/hooks/pre-commit`, it goes silently dead the moment `npm install` runs the `prepare` script. A commit could then land under the wrong identity - the exact failure your guard existed to prevent. So the guard MUST be folded into `.husky/pre-commit`.

## Per-repo steps

1. **Confirm it's a TS/Node repo with a root `package.json`.** (Python-only repos keep `.git/hooks/pre-commit` - do not add husky.)
2. **Install deps** (husky/lint-staged/prettier are dev-only - they don't run in prod):
   ```bash
   npm i -D husky lint-staged prettier        # + prettier-plugin-tailwindcss if Tailwind
   ```
3. **Wire husky:**
   ```bash
   npm pkg set scripts.prepare="husky"
   npx husky init
   ```
4. **Add the `lint-staged` block** to `package.json` (tune globs to the repo's languages):
   ```json
   "lint-staged": {
     "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
     "*.{json,md,css}": ["prettier --write"]
   }
   ```
5. **Write the composite `.husky/pre-commit`** - your guard checks first (fail-fast), then the lint-staged runner:
   - (1) any identity/branch guard you rely on (e.g. an `exit 1` on the wrong `user.email`)
   - (2) optional non-blocking direct-to-main warning
   - (3) `npx lint-staged` (or `pnpm exec lint-staged`)
6. **Delete or neutralize any old `.git/hooks/pre-commit`** so there's no confusion about which fires (it won't run under `core.hooksPath=.husky`, but leaving a dead guard file is misleading).
7. **Verify the guard survived the flip:**
   ```bash
   git config core.hooksPath          # should print .husky
   git config user.email              # should be the address you expect
   ```
   Then make a trivial staged change and commit on a feature branch - confirm lint-staged runs and your guard checks are present in `.husky/pre-commit`.
8. **Commit the husky files** (`.husky/`, `package.json`, lockfile) - unlike `.git/hooks`, these ARE versioned and survive clones.

## Coordinate on shared repos

- **Solo / direct-ownership repos** - safe to backfill on your own.
- **Repos shared with other contributors** - coordinate before pushing; husky changes everyone's local commit behavior, so open a PR and flag it rather than surprising the team.
- **Repos owned by another engineer** - their call. Don't add husky to a repo you don't own without asking.

## Why not just rely on CI?

CI catches lint/build failures at PR time, but: husky gives feedback in ~3s at commit time instead of minutes at CI time, and `prettier --write` auto-fixes locally (CI can only fail, not fix-and-commit cleanly). lint-staged runs ONLY on staged files, so it does not violate the "use CI, not local full builds" discipline (`rules/use-gha-not-local-ci.md` targets full suites/builds, not staged-file format/lint). Husky and CI are complementary gates, not redundant.
