#!/usr/bin/env python3
"""public_repo_guard.py: a git pre-push hook that refuses to publish a private name to a PUBLIC
repository.

You keep a private denylist OUTSIDE every repository (client names, company names, your machine
name, private paths, internal hostnames, account ids), one regular expression per line. When you
push to a repository that is public, this hook reads everything the push would publish (each new
commit's message, every line it adds and every file path it adds) and refuses the push if any of
it matches. Nothing leaves the machine before a push, so this is the moment that matters.

    Install (per repository, or through a git template folder for every new clone):
        .git/hooks/pre-push   ->  #!/bin/sh
                                  exec python "<kit>/hooks/git/public_repo_guard.py" "$@"

    The denylist:   $PUBLIC_REPO_DENYLIST, else ~/.config/public-repo-guard/denylist.txt
                    one Python regular expression per line, matched case-insensitively;
                    blank lines and lines starting with # are ignored
    Visibility:     `git config guard.visibility public|private` wins; else GitHub is asked
                    (`gh repo view <owner>/<repo> --json visibility`); a push whose visibility
                    cannot be read is treated as PUBLIC, because a name that reaches a public
                    repository is there for good

Silent and fast for a private repository. In a public one it fails closed: a scan that cannot
finish refuses the push and says why. The refusal names where each match is (commit, message or
file and line) and the denylist line number that matched, never the pattern itself.

The fix for a refusal: take the text out of the unpushed commits (amend, or an interactive
rebase of the commits that are not on the remote yet), then push again. Never --no-verify.

Standard library only; Python 3.9+.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

ZERO = "0" * 40
MAX_FINDINGS = 12
GITHUB_RE = re.compile(r"github\.com[:/]+([^/\s]+)/([^/\s]+?)(?:\.git)?/?$", re.IGNORECASE)


def git(*args: str, cwd: Optional[str] = None) -> str:
    result = subprocess.run(["git", *args], capture_output=True, cwd=cwd, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])} failed: {result.stderr.decode('utf-8', 'replace').strip()}")
    return result.stdout.decode("utf-8", "replace")


def denylist_path() -> Path:
    configured = os.environ.get("PUBLIC_REPO_DENYLIST")
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config" / "public-repo-guard" / "denylist.txt"


def load_denylist(path: Path) -> List[Tuple[int, re.Pattern]]:
    patterns = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        try:
            patterns.append((number, re.compile(text, re.IGNORECASE)))
        except re.error as error:
            raise RuntimeError(f"denylist line {number} is not a valid regular expression: {error}")
    return patterns


def visibility(remote_url: str) -> str:
    """Return 'public', 'private' or 'unknown'."""
    try:
        configured = git("config", "--get", "guard.visibility").strip().lower()
    except RuntimeError:
        configured = ""
    if configured in ("public", "private"):
        return configured
    match = GITHUB_RE.search(remote_url or "")
    if not match:
        return "unknown"
    try:
        result = subprocess.run(
            ["gh", "repo", "view", f"{match.group(1)}/{match.group(2)}", "--json", "visibility", "-q", ".visibility"],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    answer = result.stdout.strip().lower()
    if result.returncode == 0 and answer in ("public", "private", "internal"):
        return "private" if answer == "internal" else answer
    return "unknown"


def pushed_text(remote: str, updates: List[Tuple[str, str, str, str]]) -> str:
    """The log of every commit this push would publish, with patches (added lines only matter)."""
    chunks = []
    for _local_ref, local_sha, _remote_ref, remote_sha in updates:
        if local_sha == ZERO:
            continue  # a branch delete publishes nothing
        revs = [local_sha, "--not", f"--remotes={remote}"] if remote_sha == ZERO else [f"{remote_sha}..{local_sha}"]
        # --no-renames: a rename shows as a new file, so its new path is read; quotepath off: a
        # non-ASCII path is read as itself, not as octal escapes.
        chunks.append(git("-c", "core.quotepath=off", "log", "--no-color", "--no-ext-diff", "--no-renames", "-p", "-U0",
                          "--format=%x1eCOMMIT %H%n%B%x1f", *revs))
    return "".join(chunks)


def header_path(line: str) -> str:
    """The path from a `diff --git a/<path> b/<path>` header. With --no-renames both halves name the
    same path, so the split is by length, which a space or a "b/" inside the name cannot fool.
    Git quotes both halves when the path has a quote, a backslash or a control character."""
    rest = line[len("diff --git "):]
    quoted = rest.startswith('"')
    size = (len(rest) - (8 if quoted else 5)) // 2
    start = 3 if quoted else 2
    path = rest[start:start + size]
    if size > 0 and rest == (f'"a/{path}" "b/{path}"' if quoted else f"a/{path} b/{path}"):
        return path
    found = re.findall(r'"?b/(.*?)"?$', rest)
    return found[-1] if found else rest


def scan(log_text: str, patterns: List[Tuple[int, re.Pattern]]) -> List[str]:
    findings: List[str] = []
    for record in log_text.split("\x1e"):
        if not record.strip():
            continue
        header, _, rest = record.partition("\n")
        sha = header.replace("COMMIT ", "").strip()[:7]
        message, _, patch = rest.partition("\x1f")
        places: List[Tuple[str, str]] = [(f"{sha} message", line) for line in message.splitlines()]
        current_file, line_number = "?", 0
        header_place: Optional[int] = None
        for line in patch.splitlines():
            if line.startswith("diff --git "):
                # Every changed file has this header, an empty new file included (it has no +++ line).
                current_file = header_path(line)
                header_place = len(places)
                places.append((f"{sha} path", current_file))
            elif line.startswith("deleted file mode") and header_place is not None:
                places.pop(header_place)  # removing a file publishes nothing new
                header_place = None
            elif line.startswith("+++ "):
                header_place = None
                if line[4:] != "/dev/null":
                    current_file = line[4:].strip('"').removeprefix("b/")
            elif line.startswith("@@"):
                header_place = None
                hunk = re.search(r"\+(\d+)", line)
                line_number = int(hunk.group(1)) if hunk else 0
            elif line.startswith("+"):
                places.append((f"{sha} {current_file}:{line_number}", line[1:]))
                line_number += 1
        for where, text in places:
            for number, pattern in patterns:
                match = pattern.search(text)
                if match:
                    findings.append(f"  {where}: denylist line {number} matched {match.group(0)!r}")
                    break
            if len(findings) >= MAX_FINDINGS:
                return findings
    return findings


def inside(path: Path, folder: Path) -> bool:
    try:
        path.resolve().relative_to(folder.resolve())
        return True
    except ValueError:
        return False


def main(argv: List[str]) -> int:
    remote = argv[1] if len(argv) > 1 else "origin"
    url = argv[2] if len(argv) > 2 else ""
    updates = []
    for line in sys.stdin.read().splitlines():
        parts = line.split()
        if len(parts) == 4:
            updates.append((parts[0], parts[1], parts[2], parts[3]))
    if not updates:
        return 0

    seen = visibility(url)
    if seen == "private":
        return 0

    path = denylist_path()
    if not path.exists():
        sys.stderr.write(f"public_repo_guard: no denylist at {path}; nothing to check.\n")
        return 0
    try:
        top = Path(git("rev-parse", "--show-toplevel").strip())
        if inside(path, top):
            sys.stderr.write("PUSH BLOCKED by public_repo_guard: the denylist sits inside this repository, "
                             "so it would be published. Move it outside every repository.\n")
            return 1
        patterns = load_denylist(path)
        findings = scan(pushed_text(remote, updates), patterns)
    except Exception as error:  # a public repository fails closed
        sys.stderr.write(f"PUSH BLOCKED by public_repo_guard: the scan could not finish ({error}).\n")
        return 1

    if not findings:
        return 0
    label = "a PUBLIC repository" if seen == "public" else "a repository whose visibility could not be read (treated as public)"
    sys.stderr.write(
        f"PUSH BLOCKED by public_repo_guard: this push to {label} carries private text.\n"
        + "\n".join(findings)
        + "\nFix: take the text out of the unpushed commits (amend, or rebase the commits not on the remote), "
        "then push again. Never --no-verify.\n"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
