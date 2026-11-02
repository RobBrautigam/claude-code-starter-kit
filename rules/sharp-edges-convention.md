# Sharp Edges Convention

The highest-severity, prod-breaking, easy-to-trip foot-guns in a repo get an inline `## Sharp Edges` section near the top of that repo's `CLAUDE.md` AND - where the foot-gun is mechanically checkable - a **CI grep gate or lint rule that fails the build.**

## The core principle: the gate is the enforcement, the prose is the companion

A Sharp Edge is a foot-gun that already cost real time in production (or nearly did). Documenting it matters, but **documentation alone does not change behavior** - and any text loaded into context every session (a CLAUDE.md or an auto-loaded rule) is read the same way whether the foot-gun lives in one file or another. Moving a foot-gun between context-loaded surfaces changes nothing about whether the model sees it.

What actually prevents the regression is a **mechanical check**: a CI grep that fails on the forbidden pattern, a lint rule, a test. A canonical example: a React app where `useSyncExternalStore`'s `getSnapshot` callback returned a fresh object literal on every call, causing an infinite render loop in production. The fix was a CI grep that fails the build if `getSnapshot` returns a new object - *that grep* is the real artifact; the CLAUDE.md prose is the human-readable companion that explains WHY.

**So when you identify a Sharp Edge, always ask: can this be a grep/lint/test gate?** If yes, build the gate - that's 80% of the value. The inline prose is the remaining 20%.

## The three documentation tiers (don't let them overlap)

| Tier | Lives in | Holds |
|---|---|---|
| **Inline Sharp Edges** | `## Sharp Edges` near the top of the repo's `CLAUDE.md` | The top 3-5 prod-breaking foot-guns specific to THIS repo - read-before-touching |
| **Repo rules** | `.claude/rules/*.md` in the repo | The broader repo-specific reference layer (conventions, post-mortems, patterns) |
| **Global rules** | `~/.claude/rules/*.md` | Standards that apply across all your repos |

A foot-gun is a Sharp Edge (top tier) only if tripping it breaks production or corrupts data AND it's non-obvious. Everything else is a repo rule. When in doubt, it's a repo rule, not a Sharp Edge - the Sharp Edges section stays short (3-5 items) so it keeps its signal.

## Copyable section template

Paste near the top of the repo `CLAUDE.md` (right after the project description / core rules):

```markdown
## Sharp Edges - Read Before Touching {Area}

These took down {what} on {date} ({incident / commit refs}). They are NOT obvious
from local dev because {why it only shows in prod / under load / etc}. Default to
the safe pattern below.

### {Foot-gun name}

{1-2 sentences on the failure mechanism and its blast radius.}

**FORBIDDEN ({where - e.g. in client-component render}):**
- `{anti-pattern code or call}` - {why it breaks}

**REQUIRED:**
- `{safe pattern}` - see `{path/to/canonical/implementation}`

**Gate:** `{CI grep / lint rule / test that fails the build on the forbidden pattern}`
  (e.g. `grep -rn "getSnapshot.*return {" src/ && exit 1` in CI)
  - OR "no mechanical gate yet; {why}, candidate for one."
```

The `Gate:` line is mandatory. If you genuinely can't mechanize the check, say so explicitly and note it as a candidate - don't silently leave prose-only.

## Relationship to other discipline

This composes with the FORBIDDEN/REQUIRED + "Why this rule exists" post-mortem shape used across well-run rule sets (e.g. `rules/no-bash-heredocs.md`). It adds two things: (1) the **inline-in-CLAUDE placement** for the per-repo top-tier foot-guns (so they're the first thing read in a repo), and (2) the **explicit push toward a mechanical gate** for each one. The bulk of foot-gun documentation stays in rules files; Sharp Edges is the short, inline, gate-backed top tier.

A pre-commit hook (see `rules/git-conventions.md`) and CI (see `rules/use-gha-not-local-ci.md`) are the two most common places these gates run.
