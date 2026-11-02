#!/usr/bin/env python3
"""guard_bash.py: a Claude Code PreToolUse hook that refuses a short list of irreversible
accidents before the Bash (or PowerShell) tool runs them.

    Register it in ~/.claude/settings.json (see hooks/README.md):
        PreToolUse, matcher "Bash|PowerShell", command: python <path>/guard_bash.py

What it refuses (each refusal names the check, the reason and the fix):

    no-verify        git commit / push / merge / rebase / cherry-pick / am with --no-verify
                     (or `git commit -n`): a failed hook is fixed, never skipped
    force-push-main  git push --force / -f / --force-with-lease / a +refspec, aimed at main or
                     master (named, implied by the current branch, or --all / --mirror)
    reset-hard       git reset --hard: it throws away uncommitted work, possibly another
                     session's in the same folder
    kill-by-name     taskkill /IM, pkill, killall, Stop-Process -Name, Get-Process <name> |
                     Stop-Process: a name matches your editor and browser too; stop by process id
    data-delete      dropdb, gh repo delete, supabase projects delete, supabase db reset --linked,
                     and DROP TABLE / DATABASE / SCHEMA, TRUNCATE or DELETE FROM without WHERE
                     when an SQL client (psql, mysql, sqlite3, ...) runs them
    rm-root          rm -rf aimed at /, /*, ~, $HOME or ${HOME}, with or without /*
    heredoc-backslash  a Bash heredoc whose body holds a backslash under an unquoted delimiter,
                     or two backslashes in a row under any delimiter: bash and the tool layer
                     rewrite them, so the program does not get the bytes you wrote

The override, for the one time a human asked for exactly this: start the command with
    GUARD_OK="<the human's reason>" <command>            (bash)
    $env:GUARD_OK="<the human's reason>"; <command>      (PowerShell)
It covers that one command (or that one pipeline), never the rest of a chain after it.

How it reads a command: it splits the line on ; && || & and newlines, keeps a pipeline
together, drops redirections (2>&1, > file), skips wrapper flags and their values (sudo -u
bob, timeout 30), and reads the script inside bash -c / -lc / -ec, sh -c and powershell
-Command. A line it cannot tokenize is split roughly and still checked, never waved
through. SQL is read from a client's own arguments, a pipe into it and a heredoc fed to
it; a file fed with `< wipe.sql` is not opened.
A refusal is the hook exiting 2 with the reason on stderr, which Claude Code shows to Claude.

This is pattern matching on the command text to stop accidents. It is not a security boundary:
a determined or obfuscated command can get past it. Standard library only; Python 3.9+.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from typing import Iterable, List, Optional, Tuple

PROTECTED_BRANCHES = {"main", "master"}
WRAPPERS = {"sudo", "env", "time", "nice", "nohup", "command", "builtin", "exec", "xargs", "timeout"}
SHELLS_WITH_C = {"bash", "sh", "zsh", "dash"}
POWERSHELLS = {"powershell", "powershell.exe", "pwsh", "pwsh.exe"}
SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "\n", ";;", "|&"}
# The override prefix, in bash form (GUARD_OK="why" cmd) or PowerShell form ($env:GUARD_OK="why"; cmd).
# It covers the one command (or pipeline) that follows it, never the rest of a chained line.
OVERRIDE_RE = re.compile(
    r"^\s*(?:GUARD_OK=(?:\"[^\"]+\"|'[^']+'|[^\s\"';&|]+)\s+"
    r"|\$env:GUARD_OK\s*=\s*(?:\"[^\"]+\"|'[^']+')\s*;\s*)"
)
WRAPPER_VALUE_FLAGS = {
    "sudo": {"-u", "-g", "-h", "-p", "-C", "-D", "-r", "-t", "-U", "-T", "--user", "--group"},
    "env": {"-u", "-C", "-S", "--unset", "--chdir", "--split-string"},
    "nice": {"-n", "--adjustment"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "xargs": {"-I", "-L", "-n", "-P", "-d", "-E", "-s", "-a"},
    "exec": {"-a"},
}

Refusal = Tuple[str, str, str]  # (check, why, fix)


# --------------------------------------------------------------------------------------------
# Heredocs: found first, so their bodies are checked on their own and never read as commands.
# --------------------------------------------------------------------------------------------

HEREDOC_OPEN_RE = re.compile(r"(?<!<)<<(?!<)(-?)\s*(\\?)(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\3")


def split_heredocs(command: str) -> Tuple[str, List[Tuple[str, bool, str]]]:
    """Return (the command with heredoc bodies removed, [(delimiter, quoted, body), ...])."""
    lines = command.split("\n")
    kept: List[str] = []
    bodies: List[Tuple[str, bool, str]] = []
    pending: List[Tuple[str, bool, bool]] = []  # (delimiter, quoted, strip_tabs)
    i = 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        for match in HEREDOC_OPEN_RE.finditer(line):
            strip_tabs = match.group(1) == "-"
            quoted = bool(match.group(2) or match.group(3))
            pending.append((match.group(4), quoted, strip_tabs))
        i += 1
        while pending:
            delimiter, quoted, strip_tabs = pending.pop(0)
            body: List[str] = []
            while i < len(lines):
                candidate = lines[i].lstrip("\t") if strip_tabs else lines[i]
                i += 1
                if candidate.rstrip("\r") == delimiter:
                    break
                body.append(lines[i - 1])
            bodies.append((delimiter, quoted, "\n".join(body)))
    return "\n".join(kept), bodies


def check_heredocs(bodies: Iterable[Tuple[str, bool, str]]) -> Optional[Refusal]:
    for delimiter, quoted, body in bodies:
        if "\\\\" in body:
            return (
                "heredoc-backslash",
                f"the heredoc <<{delimiter} holds two backslashes in a row; the tool layer can hand "
                "bash one, so the program reads different bytes than you wrote",
                "write the content with the Write tool, then run the file",
            )
        if not quoted and "\\" in body:
            return (
                "heredoc-backslash",
                f"the heredoc <<{delimiter} has an unquoted delimiter and a backslash in its body; "
                "bash rewrites backslashes there",
                "quote the delimiter (<<'EOF'), or better, write the file with the Write tool",
            )
    return None


# --------------------------------------------------------------------------------------------
# Splitting a command into simple commands (lists of words).
# --------------------------------------------------------------------------------------------


def tokenize(command: str) -> List[str]:
    """Shell words and operators. A command shlex cannot read (an unbalanced quote, a PowerShell
    backtick escape) falls back to a rough split, so the checks still run: never fail open."""
    text = command.replace("\r", "")
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
        lexer.whitespace = " \t"
        lexer.wordchars += "~-./*$:\\=@%+,{}[]"
        return list(lexer)
    except ValueError:
        return [t.strip("\"'`") for t in re.findall(r"[;&|()<>\n]+|[^\s;&|()<>]+", text)]


def is_redirect(token: str) -> bool:
    return bool(token) and set(token) <= set("<>&|") and ("<" in token or ">" in token)


def drop_redirects(tokens: List[str]) -> List[str]:
    """Remove redirections (`> log`, `2>&1`, `< in.sql`) so their targets are never read as
    arguments; a file descriptor number written before the operator goes with it."""
    kept: List[str] = []
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            if not (token in SEPARATORS or set(token) <= set(";&|()\n")):
                continue
        if is_redirect(token):
            if kept and kept[-1].isdigit():
                kept.pop()
            skip_next = True
            continue
        kept.append(token)
    return kept


def command_groups(command: str, depth: int = 0) -> List[List[List[str]]]:
    """Split a command line into groups (split on ; && || & and newlines), each group a list of
    simple commands (a pipeline stays one group). Scripts inside bash -c and powershell -Command
    are expanded into the group that runs them."""
    groups: List[List[List[str]]] = [[]]
    current: List[str] = []
    for token in drop_redirects(tokenize(command)):
        if token in SEPARATORS or set(token) <= set(";&|()\n"):
            if current:
                groups[-1].append(current)
            current = []
            if token not in ("|", "|&") and groups[-1]:
                groups.append([])
        else:
            current.append(token)
    if current:
        groups[-1].append(current)
    result: List[List[List[str]]] = []
    for group in groups:
        expanded: List[List[str]] = []
        for words in group:
            words = strip_prefixes(words)
            if not words:
                continue
            expanded.append(words)
            inner = inner_script(words)
            if inner is not None and depth < 3:
                for inner_group in command_groups(inner, depth + 1):
                    expanded.extend(inner_group)
        if expanded:
            result.append(expanded)
    return result


def simple_commands(command: str, depth: int = 0) -> List[List[str]]:
    return [words for group in command_groups(command, depth) for words in group]


def strip_prefixes(words: List[str]) -> List[str]:
    """Drop NAME=value assignments and wrappers like sudo -u someone, env, timeout 30."""
    i = 0
    while i < len(words):
        word = words[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", word):
            i += 1
        elif base(word) in WRAPPERS:
            takes_value = WRAPPER_VALUE_FLAGS.get(base(word), set())
            i += 1
            while i < len(words) and (words[i].startswith("-") or re.match(r"^\d+(\.\d+)?[smhd]?$", words[i])):
                i += 2 if words[i] in takes_value else 1
        else:
            break
    return words[i:]


def inner_script(words: List[str]) -> Optional[str]:
    program = base(words[0])
    if program in SHELLS_WITH_C:
        for index, word in enumerate(words[1:], 1):
            if re.match(r"^-[A-Za-z]*c[A-Za-z]*$", word):  # -c, and clusters like -lc, -ec, -xc
                return words[index + 1] if index + 1 < len(words) else None
        return None
    if program in POWERSHELLS:
        for flag in ("-Command", "-command", "-c", "-C"):
            if flag in words[1:]:
                index = words.index(flag)
                return " ".join(words[index + 1:]) or None
    return None


def base(word: str) -> str:
    return re.split(r"[\\/]", word)[-1].lower()


# --------------------------------------------------------------------------------------------
# The checks on simple commands.
# --------------------------------------------------------------------------------------------


def git_parts(words: List[str]) -> Optional[Tuple[Optional[str], str, List[str]]]:
    """For a git command return (the -C folder or None, subcommand, the rest)."""
    if base(words[0]) not in ("git", "git.exe"):
        return None
    folder = None
    i = 1
    while i < len(words) and words[i].startswith("-"):
        if words[i] == "-C" and i + 1 < len(words):
            folder = words[i + 1]
            i += 2
        elif words[i] in ("-c", "--git-dir", "--work-tree") and i + 1 < len(words):
            i += 2
        else:
            i += 1
    if i >= len(words):
        return None
    return folder, words[i], words[i + 1:]


def current_branch(folder: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "-C", folder, "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def commit_short_no_verify(rest: List[str]) -> bool:
    """True when a short-flag cluster of `git commit` holds -n. Flags that take a value end the
    cluster (-m, -F, -C, -c, -t) and their next word is the value; -u and -S take an attached one."""
    skip_value = False
    for word in rest:
        if skip_value:
            skip_value = False
            continue
        if not word.startswith("-") or word.startswith("--") or word == "-":
            continue
        cluster = word[1:]
        for position, flag in enumerate(cluster):
            if flag == "n":
                return True
            if flag in "mFCct":
                skip_value = position == len(cluster) - 1
                break
            if flag in "uS":
                break
    return False


def check_git(words: List[str], cwd: str) -> Optional[Refusal]:
    parts = git_parts(words)
    if parts is None:
        return None
    folder, sub, rest = parts
    where = os.path.join(cwd, folder) if folder else cwd
    if sub in ("commit", "push", "merge", "rebase", "cherry-pick", "am", "revert") and (
        "--no-verify" in rest or (sub == "commit" and commit_short_no_verify(rest))
    ):
        return (
            "no-verify",
            f"git {sub} with --no-verify skips the hooks that exist to stop this exact mistake",
            "read what the hook refused and fix that; run the command again without --no-verify",
        )
    if sub == "push":
        forced = any(
            w in ("-f", "--force", "--force-with-lease", "--force-if-includes")
            or w.startswith("--force-with-lease=")
            or (re.match(r"^-[a-zA-Z]+$", w) is not None and "f" in w)
            or w == "--mirror"  # a mirror push force-updates every remote ref, main included
            for w in rest
        )
        refspecs = [w for w in rest if not w.startswith("-")][1:]  # first plain word is the remote
        plus_specs = [w for w in refspecs if w.startswith("+")]
        if forced or plus_specs:
            targets = [w.lstrip("+").split(":")[-1].replace("refs/heads/", "") for w in (refspecs if forced else plus_specs)]
            if "HEAD" in targets:
                targets.append(current_branch(where) or "main")  # unknown branch: assume the worst
            aims_protected = any(t in PROTECTED_BRANCHES for t in targets)
            if not refspecs:
                branch = current_branch(where)
                aims_protected = branch is None or branch in PROTECTED_BRANCHES
            if "--all" in rest or "--mirror" in rest or "--branches" in rest:
                aims_protected = True
            if aims_protected:
                return (
                    "force-push-main",
                    "a force push to main or master rewrites the history everyone else has",
                    "pull --rebase and push normally; if history must change, do it on a branch through a pull request",
                )
    if sub == "reset" and "--hard" in rest:
        return (
            "reset-hard",
            "git reset --hard throws away uncommitted work, and another session may be working in this folder",
            "commit the work first (a WIP commit is fine), or use git restore on the one file you mean",
        )
    return None


def check_kill(words: List[str]) -> Optional[Refusal]:
    program = base(words[0])
    lowered = [w.lower() for w in words[1:]]
    by_name = False
    if program in ("taskkill", "taskkill.exe") and any(w.lstrip("/-") == "im" for w in lowered):
        by_name = True
    elif program in ("pkill", "killall"):
        by_name = True
    elif program in ("stop-process", "spps") and any(w in ("-name", "-processname") or w.startswith("-n") and not w.startswith("-no") for w in lowered):
        by_name = True
    elif program == "kill" and any(w in ("-name", "-processname") for w in lowered):
        by_name = True  # PowerShell's kill alias for Stop-Process; bash kill takes ids only
    if by_name:
        return (
            "kill-by-name",
            f"{words[0]} stops processes by name, which also matches your editor, browser and other sessions",
            "find the process id (and check its command line and parent), then stop that id only",
        )
    return None


def check_kill_pipeline(group: List[List[str]]) -> Optional[Refusal]:
    """In one pipeline: Get-Process selected by name (or not at all) piped into Stop-Process."""
    selector_by_name = False
    for words in group:
        program = base(words[0])
        lowered = [w.lower() for w in words[1:]]
        if program in ("get-process", "gps", "ps") and not any(w in ("-id", "-inputobject") for w in lowered):
            selector_by_name = program != "ps" or any(w in ("-name", "-processname") for w in lowered)
        elif program in ("stop-process", "spps", "kill") and selector_by_name and not any(w == "-id" for w in lowered):
            return (
                "kill-by-name",
                "Get-Process <name> | Stop-Process stops every process with that name",
                "select by id (Get-Process -Id <pid>) after checking it is the one you started",
            )
    return None


DATA_DELETE_PATTERNS = [
    (re.compile(r"\bdrop\s+(table|database|schema)\b", re.IGNORECASE), "a DROP statement"),
    (re.compile(r"\btruncate\s+(table\s+)?[A-Za-z_\"`]", re.IGNORECASE), "a TRUNCATE statement"),
]


def check_data_delete(words: List[str], raw: str) -> Optional[Refusal]:
    program = base(words[0])
    rest = [w.lower() for w in words[1:]]
    reason = None
    if program == "dropdb":
        reason = "dropdb deletes a whole database"
    elif program in ("gh", "gh.exe") and rest[:2] == ["repo", "delete"]:
        reason = "gh repo delete removes a repository and its history"
    elif program in ("supabase", "npx") and "projects" in rest and "delete" in rest:
        reason = "supabase projects delete removes a hosted project"
    elif program in ("supabase", "npx") and "reset" in rest and "--linked" in rest:
        reason = "supabase db reset --linked wipes the linked (remote) database"
    if reason:
        return ("data-delete", reason, "get the human's word for this exact action, then use the override")
    return None


def check_sql_text(command: str) -> Optional[Refusal]:
    for pattern, label in DATA_DELETE_PATTERNS:
        if pattern.search(command):
            return ("data-delete", f"the command carries {label}", "get the human's word for this exact action, then use the override")
    for match in re.finditer(r"\bdelete\s+from\s+[A-Za-z_\"`.]+", command, re.IGNORECASE):
        statement = re.split(r"[;\"']", command[match.end():], maxsplit=1)[0]
        if not re.search(r"\bwhere\b", statement, re.IGNORECASE):
            return (
                "data-delete",
                "DELETE FROM without a WHERE clause empties the table",
                "add the WHERE clause you mean; for a deliberate wipe get the human's word, then use the override",
            )
    return None


def check_rm(words: List[str]) -> Optional[Refusal]:
    if base(words[0]) != "rm":
        return None
    flags = "".join(w.lstrip("-") for w in words[1:] if w.startswith("-") and not w.startswith("--"))
    long_flags = [w for w in words[1:] if w.startswith("--")]
    recursive = "r" in flags.lower() or "--recursive" in long_flags
    if not recursive:
        return None
    targets = [w for w in words[1:] if not w.startswith("-")]
    dangerous = {"/", "/*", "~", "~/", "~/*", "$HOME", "$HOME/", "$HOME/*", "${HOME}", "${HOME}/", "${HOME}/*"}
    if any(t.rstrip() in dangerous for t in targets):
        return ("rm-root", "rm -r aimed at the filesystem root or your home folder", "name the exact folder you mean to remove")
    return None


# --------------------------------------------------------------------------------------------


SQL_CLIENTS = {"psql", "mysql", "mariadb", "sqlite3", "sqlcmd", "duckdb", "supabase", "cockroach", "clickhouse-client"}


def evaluate(tool_name: str, command: str, cwd: str) -> Optional[Refusal]:
    # The override covers the first command (or pipeline) after it, and only that one.
    override = OVERRIDE_RE.match(command)
    if override:
        command = command[override.end():]
    without_bodies, bodies = split_heredocs(command) if tool_name == "Bash" else (command, [])
    groups = command_groups(without_bodies)
    if override:
        groups = groups[1:]
    elif tool_name == "Bash":
        refusal = check_heredocs(bodies)
        if refusal:
            return refusal
    sql_client_seen = False
    for group in groups:
        for words in group:
            for check in (lambda w: check_git(w, cwd), check_kill, lambda w: check_data_delete(w, without_bodies), check_rm):
                refusal = check(words)
                if refusal:
                    return refusal
        refusal = check_kill_pipeline(group)
        if refusal:
            return refusal
        # SQL text is read only in a pipeline an SQL client is part of (`psql -c "..."`,
        # `echo "..." | psql`), so a commit message that says "drop table support" is never
        # mistaken for a DROP. A file fed with `< wipe.sql` is not opened.
        if any(base(words[0]).removesuffix(".exe") in SQL_CLIENTS for words in group):
            sql_client_seen = True
            refusal = check_sql_text(" ".join(" ".join(words) for words in group))
            if refusal:
                return refusal
    if sql_client_seen:
        for _, _, body in bodies:
            refusal = check_sql_text(body)
            if refusal:
                return refusal
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0  # not a hook payload; never block on our own parse failure
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Bash", "PowerShell"):
        return 0
    command = (payload.get("tool_input") or {}).get("command") or ""
    cwd = payload.get("cwd") or os.getcwd()
    refusal = evaluate(tool_name, command, cwd)
    if refusal is None:
        return 0
    check, why, fix = refusal
    sys.stderr.write(
        f"BLOCKED by guard_bash ({check}): {why}.\n"
        f"Fix: {fix}.\n"
        'Override (only when the human asked for this exact action): start that one command with '
        'GUARD_OK="<their reason>" (in PowerShell: $env:GUARD_OK="<their reason>"; ).\n'
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
