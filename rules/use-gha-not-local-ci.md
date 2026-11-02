# Use GitHub Actions, not local CI

When a repo has CI configured (any `.github/workflows/*.yml` that runs tests + build on push), **never run the full test suite, full TypeScript check, or full production build locally.** Push the commit and check CI status via `gh pr checks <N>`.

Local runs that peg the CPU for minutes at a time are an anti-pattern when CI does the same job on remote hardware, in parallel, on every push.

## The rule

**Forbidden locally** (when CI exists for the repo):

- `npx vitest run` (full suite, no path argument)
- `npx vitest` (watch mode that runs the full suite at start)
- `npm test` / `pnpm test` / `yarn test` (full suite)
- `npm run build` / `next build` / `vite build` (full production build)
- `npx tsc --noEmit` (full project typecheck)
- `next build --webpack` / equivalent variants
- `pytest` against the full repo (Python equivalent)
- Any other "run the entire project's checks" invocation

**Allowed locally:**

- `npx vitest run path/to/single.test.ts` (single test file, sub-5s, no CPU peg)
- `npx vitest run path/to/dir/` (a single directory's tests, when small and self-contained)
- `pytest path/to/test_one_thing.py` (single Python test file)
- `node --check path/to/file.js` (syntax check on one file)
- VS Code TS language service (passive, on-save type check of the open file)
- `eslint path/to/file.tsx` (lint one file)
- The dev server (`npm run dev` / `next dev`) - only when actually exercising a feature in the browser, NOT as a verification step before commit

## Verification flow when CI exists

1. Make changes locally.
2. Commit to the feature branch.
3. Push.
4. `gh pr checks <PR>` - get current CI status (lightweight remote call).
5. If pending: set up a `Monitor` (Claude Code's Monitor tool with a `gh pr checks` poll loop) so you're notified on completion without polling locally. Continue with other work in the meantime.
6. If failed: `gh run view <run-id> --log-failed` to see the failure log (remote - no local CPU).
7. Fix the specific issue. Push. Repeat from step 4.

This is **identical or faster** than running the full suite locally (CI runs jobs in parallel), without the CPU cost.

## When this rule does NOT apply

- **No CI configured** - local is the only option. Tell the user if a frequently-shipped repo lacks CI so they can decide whether to wire one.
- **CI is unavailable** - outage, billing-blocked, infrastructure issue.
- **Single-file iteration** - fast, scoped, no CPU peg. Use freely.
- **TDD on a single component** - write test, run THAT test only, implement, run THAT test only.
- **Live debugging** - running the actual production-bug scenario via `npm run dev` to step through it.
- **User explicitly says "run it locally"** - explicit instruction overrides the rule.

## Subagent discipline (especially important)

Subagents dispatched via `subagent-driven-development` historically default to "run the full suite to verify my work" before reporting DONE. This is exactly the anti-pattern this rule prevents.

Every implementer-subagent prompt MUST include explicit instruction:

> **Do NOT run `npm run build` / `npx vitest run` (full) / `npx tsc --noEmit` locally.** The user's CPU is precious. After commit + push, the orchestrator checks `gh pr checks <PR>` for CI verification. Trust your implementation. If GHA reports a failure, the orchestrator surfaces the specific log and you fix that one issue.

## How to detect a violation in real time

Symptoms:
- Fans audibly spin up
- VS Code becomes sluggish
- Task Manager / Activity Monitor shows `node.exe` / `node` consuming 90%+ CPU sustained
- A subagent is running and silent for >2 minutes

If you notice you're about to type any of the forbidden commands, **STOP**. The expected value is:

- Local full run: 1-5 minutes of pegged CPU, blocks other work, single failure point.
- Push + GHA: ~30 seconds local (push), then 2-5 minutes on remote in parallel, user can keep working.

The local run is the slower path almost every time.
