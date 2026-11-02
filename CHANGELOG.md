# Changelog

All notable changes to this kit. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/). The current version is in [VERSION](./VERSION).

## [1.1.0] - 2026-11-02

### Added

- **Safety hooks** in [`hooks/`](./hooks/README.md), each with tests:
  - `hooks/guard_bash.py`: a Claude Code `PreToolUse` hook for the Bash and PowerShell tools. It refuses `--no-verify`, a force push to main or master, `git reset --hard`, killing processes by name, dropping a database, schema or table, `rm -rf` on a root or home folder, and heredoc bodies with backslashes. A `GUARD_OK="<reason>"` prefix (in PowerShell, `$env:GUARD_OK="<reason>"; `) overrides it for the one command after it, for the one time a human asked. It drops redirections, keeps pipelines together, reads `bash -lc`-style flag clusters and wrapper flags such as `sudo -u <user>`, reads SQL piped into a client, and checks a line it cannot tokenize instead of allowing it.
  - `hooks/git/commit-msg`: refuses a `Co-Authored-By:` trailer and a "Generated with ..." attribution line.
  - `hooks/git/public_repo_guard.py`: a `pre-push` hook that refuses to publish a name from a private denylist (kept outside every repository) to a public repository, and treats unknown visibility as public. It reads the path of every file a push adds, changes or renames, an empty file included.
- **`scripts/install.py`**: a safe installer with `--dry-run`, `--force` (with a timestamped backup), `--target` and `--with-hooks`. It never overwrites a file you changed without `--force`, never touches an existing `CLAUDE.md`, never deletes and never edits `settings.json`. The hook settings it prints name the Python that ran it and the hook by absolute paths.
- **Five rules:** `verify-before-done`, `research-first`, `process-hygiene`, `public-repos`, `agent-fleet-cost`.
- **Tests** (`python -m unittest discover -s tests`, standard library only) for the hooks, the installer and the repository's own consistency (counts in the docs, skill frontmatter, links, no long dashes, no private-path shapes), and a GitHub Actions workflow that runs them on Linux and Windows.
- `CHANGELOG.md`, `VERSION`, `.gitattributes` (LF line endings everywhere, which the shell hook needs) and `.gitignore`.

### Changed

- `communication-style`: rewritten around four laws (plain English, a volume cap, one ask per message, short paragraphs) and an action-first shape.
- `no-bash-heredocs`: now "short and plain only", with the backslash hazard, a decision tree and a section on keeping line endings in scripted edits.
- `pushback-on-request`: push back unprompted when a stated fact or plan is wrong; a decision already made is settled and looked up, never asked again.
- `git-conventions`: no AI co-author trailer or "Generated with" line; neutral commit messages; points at the hooks.
- `development-workflow`: stop processes by id, with a pointer to `process-hygiene`.
- The `research` skill uses free sources first (GitHub, web search, plain fetches); the Perplexity key is now an optional paid fallback.
- README: a quick start from a clean clone, what's new, the safety hooks, corrected counts (14 skills, 24 rules) and the getting-help section. INSTRUCTIONS, ARCHITECTURE and `CLAUDE.md.example` list the new rules and hooks.

### Fixed

- Links to the orchestrator repository point at its current name, `ai-orchestrator`.
- The troubleshooting advice no longer suggests `pkill -f`, which stops every process whose command line matches; stop the one process by id instead.
- The README said 18 rules (there were 19) and ARCHITECTURE and INSTRUCTIONS said 13 skills (there were 14).
- Long dashes replaced with spaced hyphens across the kit, as `communication-style` asks.

## [1.0.0] - 2026-07-24

The state of the kit before versioning began, summarized from the commit history:

- 2026-05-28: the first release, with 7 skills, 15 rules, the `CLAUDE.md` template and the install guide; the expanded README; the `project-scaffolder` skill with spin-off mode.
- 2026-05-29: the four code-graph skills (`explore-codebase`, `debug-issue`, `refactor-safely`, `review-changes`), `scaffold-repo` with its husky checklist, and the `code-review-graph-usage`, `session-loose-ends-audit` and `sharp-edges-convention` rules; the rename to `claude-code-starter-kit`.
- 2026-05-30: the `graph-index-tool-adoption` rule.
- 2026-07-24: the whole-computer organization system (`ORGANIZE-YOUR-COMPUTER.md` and the `setup-doctor` skill) and the per-repo `CLAUDE.md` template.

[1.1.0]: https://github.com/RobBrautigam/claude-code-starter-kit/compare/428e148...main
[1.0.0]: https://github.com/RobBrautigam/claude-code-starter-kit/commit/428e148
