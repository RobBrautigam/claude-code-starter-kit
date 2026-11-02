# Heredocs Through the Bash Tool: Short and Plain Only

**Anything substantial goes through the Write tool, then runs as a file.** A heredoc through the
Bash tool is fine for a short, plain snippet (roughly 20 lines or fewer, no backslashes). Past
that, or with a backslash anywhere in the body, write the file first.

## Why (what goes wrong)

The Bash tool hands your command to bash through its own wrapping layer, and both layers can change
the bytes of a heredoc body before the program reads them:

- **Backslashes get rewritten.** Under an unquoted delimiter (`<<EOF`), bash itself rewrites `\\`,
  `\$` and backticks in the body. Under any delimiter, two backslashes in a row can arrive as one,
  because the tool layer processes them before bash reads the quotes. A regex, a Windows path or a
  Unicode escape in a heredoc-fed Python script is exactly where this bites.
- **Quoting surprises.** Prose bodies with apostrophes, backticks, `$` and code fences are where a
  wrapper's quoting most often ends early, and the failure shows up dozens of lines later as an
  "unexpected EOF".
- **Long bodies fail far from the cause,** and a failed heredoc is usually retried as another
  heredoc. The recovery is always the Write tool, so start there.

The kit's `hooks/guard_bash.py` refuses the backslash shapes (an unquoted delimiter with any
backslash in the body, or two backslashes in a row under any delimiter).

## Decision tree (apply at the moment of choice)

1. **A single shell command with no prose arguments** (`git status`, `pytest tests/`,
   `gh pr list`): Bash tool, direct.
2. **A short heredoc, quoted delimiter (`<<'EOF'`), no backslashes, a few lines:** fine.
3. **Anything else** (a multi-line script, prose, any backslash, anything you would hate to debug):
   write the file with the Write tool, then run it with `python path/to/file.py` or
   `bash path/to/file.sh`.

## Two distinct cases: use the right tool for each

| Goal | Right pattern | Wrong pattern |
|---|---|---|
| Create a file with content (markdown, JSON, config, README) | the Write tool, straight to the destination path | a script that calls `write_text(...)` to do the same write; or `cat > file <<EOF` |
| Run multi-line logic | the Write tool to create `tmp/<purpose>.py`, then `python tmp/<purpose>.py` | `python - <<'PY' ... PY` with a long or backslash-heavy body |

## Scripted edits keep each file's line endings

A script that rewrites files can silently change CRLF to LF or the reverse (GNU `sed -i` in Git
Bash turns CRLF into LF; Python's text mode on Windows writes CRLF). That shows up as a diff of
every line in the file. Before and after a scripted edit, count the line endings in bytes
(`open(p, "rb").read().count(b"\r\n")`), prefer the Edit tool for small changes, and write files
back in the ending they had. A `.gitattributes` file settles it for a whole repository.

## Where to put temp scripts

- Canonical location: `tmp/` inside the repo (add it to `.gitignore`).
- Descriptive names: `tmp/scaffold_seo.py`, not `tmp/x.py`.
- Not `/tmp/`: it means different things in Git Bash on Windows and on Unix, and parallel sessions
  share it.
- Do not promote one-off scripts into `scripts/`. That folder is for committed, reused tooling.
