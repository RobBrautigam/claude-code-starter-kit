# Hooks

Rules tell Claude what to do. Hooks check it at the moment of action, so the rule still holds on
the day the model forgets it. This folder holds three small guards, standard library Python and
POSIX sh only, each with its tests in `tests/`.

| Hook | Kind | What it refuses |
|---|---|---|
| [`guard_bash.py`](guard_bash.py) | Claude Code `PreToolUse` hook, on the Bash and PowerShell tools | `--no-verify`, a force push to `main` or `master`, `git reset --hard`, killing a process by name, dropping a database or table, `rm -rf` on a root or home folder, and heredoc bodies with backslashes |
| [`git/commit-msg`](git/commit-msg) | git `commit-msg` hook | a `Co-Authored-By:` trailer and a "Generated with ..." attribution line |
| [`git/public_repo_guard.py`](git/public_repo_guard.py) | git `pre-push` hook | publishing a name from your private denylist to a PUBLIC repository |

None of them is a security boundary. They are pattern matches that stop accidents: a determined
or obfuscated command can get past them. Their job is the honest mistake at 2 a.m.

## guard_bash.py: the command guard

### What each check refuses

| Check | Refused | The fix it prints |
|---|---|---|
| `no-verify` | `git commit`, `push`, `merge`, `rebase`, `cherry-pick` or `am` with `--no-verify`, and `git commit -n` | fix what the hook found and run the command again |
| `force-push-main` | `git push --force`, `-f`, `--force-with-lease`, `--force-if-includes` or a `+refspec` aimed at `main` or `master`: named, implied by the branch you are on, or through `--all`, `--branches` or `--mirror` | pull with rebase and push normally; change history on a branch, through a pull request |
| `reset-hard` | `git reset --hard` anywhere | commit the work first (a WIP commit is fine), or `git restore` the one file |
| `kill-by-name` | `taskkill /IM`, `pkill`, `killall`, `Stop-Process -Name`, `kill -Name`, and `Get-Process <name>` piped into `Stop-Process` in any pipeline of the line | find the process id, check it, and stop that id only |
| `data-delete` | `dropdb`, `gh repo delete`, `supabase projects delete`, `supabase db reset --linked`, and `DROP TABLE`, `DROP DATABASE`, `DROP SCHEMA`, `TRUNCATE` or a `DELETE FROM` with no `WHERE` given to an SQL client (as its argument, piped into it, or in a heredoc fed to it; a file fed with `< file.sql` is not opened) | get the human's word for this exact action, then use the override below |
| `rm-root` | `rm -r` aimed at `/`, `/*`, `~`, `$HOME` or `${HOME}`, with or without `/*` | name the exact folder |
| `heredoc-backslash` | a heredoc whose body holds a backslash under an unquoted delimiter, or two backslashes in a row under any delimiter | write the file with the Write tool, then run it (see `rules/no-bash-heredocs.md`) |

It also reads inside `bash -c "..."` (and flag clusters such as `bash -lc`), `sh -c`,
`powershell -Command "..."` and common wrappers (`sudo -u <user>`, `env`, `time`, `timeout 30`,
`nohup`, `xargs`), so wrapping a command does not hide it. Redirections such as `2>&1` or
`> push.log` are dropped before a command is read, and a line it cannot tokenize is still
split and checked rather than allowed.

### How a refusal looks

The hook exits with code 2 and writes the reason to stderr. Claude Code blocks the tool call and
shows Claude the message, which names the check, why, and the fix:

```
BLOCKED by guard_bash (reset-hard): git reset --hard throws away uncommitted work, and another session may be working in this folder.
Fix: commit the work first (a WIP commit is fine), or use git restore on the one file you mean.
Override (only when the human asked for this exact action): start the command with GUARD_OK="<their reason>".
```

| Exit code | Meaning |
|---|---|
| 0 | allowed (also for any tool other than Bash or PowerShell, and for input it cannot parse) |
| 2 | refused; stderr carries the reason |

### The override

For the one time a human asked for exactly this, start the command with the human's reason:

```bash
GUARD_OK="the owner asked to drop the scratch database" dropdb scratch
```

```powershell
$env:GUARD_OK="the owner asked to stop this one process"; Stop-Process -Name node
```

The reason is the point: it puts the human's words beside the command in the transcript. The
override covers the one command (or pipeline) right after it; anything chained after that with
`;`, `&&` or `||` is still checked.

### Turn it on

1. Copy it into your Claude Code folder. The installer does this and prints the settings lines:

   ```bash
   python scripts/install.py --with-hooks
   ```

2. Merge the printed block into `~/.claude/settings.json` (the installer never edits that file).
   It looks like this, with your own path:

   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "Bash|PowerShell",
           "hooks": [
             { "type": "command", "command": "python \"/home/you/.claude/hooks/guard_bash.py\"" }
           ]
         }
       ]
     }
   }
   ```

3. Restart Claude Code, then check it: ask Claude to run `git reset --hard` in a scratch repository.
   The call should come back blocked with the message above.

The printed command names the Python that ran the installer by its full path, and the hook by
its absolute path, so it works whatever your system calls Python.

## git/commit-msg: no AI attribution in commit messages

An AI agent is a tool the author used, not a contributor. A trailer follows the code into every
clone, fork and contributor graph, and taking it out later means rewriting published history. The
hook refuses any `Co-Authored-By:` trailer (on purpose for every name: a list of known tools is a
list the next tool walks past) and the "Generated with ..." line. It reads only what you wrote, so a
`git commit --verbose` diff that quotes the hook does not block its own commit.

Install it in one repository:

```bash
cp hooks/git/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

Or for every repository you create or clone from now on, through a git template folder:

```bash
mkdir -p ~/.git-templates/hooks
cp hooks/git/commit-msg ~/.git-templates/hooks/commit-msg
chmod +x ~/.git-templates/hooks/commit-msg
git config --global init.templateDir ~/.git-templates
```

A repository that already exists picks up the template on `git init` (run it again inside the
repository; it is safe and only adds missing hooks). A repository that uses husky keeps the hook in
`.husky/commit-msg` instead.

## git/public_repo_guard.py: nothing private in a public repository

You keep a private denylist OUTSIDE every repository: client names, company names, your machine
name, private paths, internal hostnames. When you push to a repository that is public, the hook
reads everything the push would publish (each new commit's message, every added line, and the
path of every file added, changed or renamed, an empty file included) and refuses the push when
any of it matches.

1. Write the denylist at `~/.config/public-repo-guard/denylist.txt` (or point
   `PUBLIC_REPO_DENYLIST` at another path). One Python regular expression per line, matched
   case-insensitively; blank lines and `#` comments are ignored:

   ```
   # clients
   acme\s*widgets
   # machine and paths
   my-desktop-name
   /home/you/private
   ```

2. Install it as the `pre-push` hook of a repository you push to, from inside that repository,
   with `KIT` set to where you cloned this kit:

   ```bash
   KIT="$HOME/claude-code-starter-kit"
   printf '#!/bin/sh\nexec python "%s" "$@"\n' "$KIT/hooks/git/public_repo_guard.py" > .git/hooks/pre-push
   chmod +x .git/hooks/pre-push
   ```

How it decides a repository is public: `git config guard.visibility public` (or `private`) wins;
otherwise it asks GitHub through `gh repo view`. When it cannot tell, it treats the push as public,
because a name that reaches a public repository is there for good.

What it never does: print a pattern from your denylist (it prints the line number), or accept a
denylist that lives inside the repository being pushed.

The fix for a refusal: take the text out of the commits that are not on the remote yet (amend, or
rebase those commits), then push again. Never `--no-verify`.

## Tests

```bash
python -m unittest discover -s tests -v
```

The git hook tests build throwaway repositories in a temporary folder with your global git config
switched off, so they never touch your own repositories or settings. The `commit-msg` tests skip
themselves where no `sh` is available.
