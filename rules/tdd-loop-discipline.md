# TDD Loop Discipline

When iterating on a single component or feature, **run only the affected tests**, not the full suite. Save the full suite for preflight and ship-time verification.

The motivation: a 3-hour parallel Claude Code session running the full vitest suite (~621 tests) on every save can sustain ~97% system CPU for 3 hours. The full suite is fine to run as a final gate; running it on every save is the bug.

## The principle

Tests serve two purposes that need different commands:

| Purpose | Command | When |
|---|---|---|
| **Iteration feedback** - am I close on this one component? | `pnpm test:file <path>` or `pnpm test:changed` | After every edit during TDD |
| **Preflight verification** - did I break anything else? | `pnpm test` (full suite) | Before commit batches, at ship time, on PR open |

Iteration feedback should be cheap (under 5 seconds, single-file scope). Preflight verification is the expensive but rare gate.

## How to apply

### When iterating on a single test file
```bash
pnpm test:file frontend/src/components/foo/__tests__/MyForm.test.tsx
```
Runs that file only. Sub-second to ~5 seconds depending on file size.

### When working across a few files vs main
```bash
pnpm test:changed
```
Runs only tests for files modified vs `origin/main`. Vitest's `--changed` flag handles the dependency graph.

### When you finish a logical chunk (component done, ready to commit)
```bash
pnpm test
```
Full suite. Once. Before the commit.

### When shipping (final gate)
```bash
pnpm preflight
# or for production-bundle verification:
pnpm preflight:prod
```
Full TypeScript build + full vitest suite + (for `:prod`) production bundle build with mounted browser probe.

## What this rule prevents

A 3-hour TDD loop where the full test suite runs 25 times = sustained CPU pegging on a 16-thread laptop. Each full-suite run spawns 14-16 vitest workers (each ~12 threads, ~250-400 MB), pegging ~5,500% of one core for 20-90 seconds. Targeted runs use a fraction of that - same correctness signal during iteration, drastically lower system load.

## What this rule does NOT change

- Full `pnpm test` is still the right preflight gate. Don't ship without it passing.
- Branch-level CI still runs the full suite - local iteration discipline doesn't replace CI.

## Related discipline

- See `use-gha-not-local-ci.md` - when CI is configured, prefer pushing and using GitHub Actions over running the full suite locally.
