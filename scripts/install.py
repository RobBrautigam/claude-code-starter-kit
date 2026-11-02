#!/usr/bin/env python3
"""install.py: copy the kit's skills and rules into your Claude Code folder, safely.

    python scripts/install.py --dry-run           # show what would happen, write nothing
    python scripts/install.py                     # install into ~/.claude
    python scripts/install.py --target ./x/.claude    # install somewhere else (a test folder)
    python scripts/install.py --with-hooks        # also copy hooks/guard_bash.py and print
                                                  # the settings.json lines that turn it on

What it does, and what it never does:

- Copies every skills/<name>/ folder to <target>/skills/<name>/ and every rules/*.md to
  <target>/rules/.
- A file that already exists and is identical is left alone ("unchanged").
- A file that already exists and DIFFERS is kept as yours ("kept yours") unless you pass
  --force, which first saves your copy beside it as <file>.bak-<timestamp>, then overwrites.
- CLAUDE.md.example becomes <target>/CLAUDE.md only when you have no CLAUDE.md yet. An existing
  CLAUDE.md is never touched, with or without --force.
- Never deletes anything. Never edits settings.json (it prints the lines for you to add).

Standard library only; Python 3.9+.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

KIT = Path(__file__).resolve().parent.parent
SKIP_NAMES = {"__pycache__", ".DS_Store", "Thumbs.db"}


def planned_copies(with_hooks: bool) -> List[Tuple[Path, Path]]:
    """(source, path relative to the target) for every file the kit installs."""
    pairs: List[Tuple[Path, Path]] = []
    for skill in sorted((KIT / "skills").iterdir()):
        if not skill.is_dir():
            continue
        for source in sorted(skill.rglob("*")):
            if source.is_file() and not (set(source.parts) & SKIP_NAMES):
                pairs.append((source, Path("skills") / source.relative_to(KIT / "skills")))
    for rule in sorted((KIT / "rules").glob("*.md")):
        pairs.append((rule, Path("rules") / rule.name))
    if with_hooks:
        pairs.append((KIT / "hooks" / "guard_bash.py", Path("hooks") / "guard_bash.py"))
    return pairs


def install(target: Path, dry_run: bool, force: bool, with_hooks: bool) -> Dict[str, List[str]]:
    report: Dict[str, List[str]] = {
        "installed": [],
        "unchanged": [],
        "kept yours": [],
        "replaced (backup kept)": [],
        "your CLAUDE.md (never touched)": [],
    }
    stamp = time.strftime("%Y%m%d-%H%M%S")
    for source, relative in planned_copies(with_hooks):
        destination = target / relative
        if destination.exists():
            if filecmp.cmp(source, destination, shallow=False):
                report["unchanged"].append(str(relative))
                continue
            if not force:
                report["kept yours"].append(str(relative))
                continue
            report["replaced (backup kept)"].append(str(relative))
            if not dry_run:
                shutil.copy2(destination, destination.with_name(f"{destination.name}.bak-{stamp}"))
                shutil.copy2(source, destination)
            continue
        report["installed"].append(str(relative))
        if not dry_run:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

    claude_md = target / "CLAUDE.md"
    if claude_md.exists():
        report["your CLAUDE.md (never touched)"].append("CLAUDE.md (compare it with CLAUDE.md.example for new rules)")
    else:
        report["installed"].append("CLAUDE.md (from CLAUDE.md.example: fill in the <placeholders>)")
        if not dry_run:
            target.mkdir(parents=True, exist_ok=True)
            shutil.copy2(KIT / "CLAUDE.md.example", claude_md)
    return report


def hook_settings(target: Path) -> str:
    command = f'python "{(target / "hooks" / "guard_bash.py").as_posix()}"'
    settings = {"hooks": {"PreToolUse": [{"matcher": "Bash|PowerShell", "hooks": [{"type": "command", "command": command}]}]}}
    return json.dumps(settings, indent=2)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Install the starter kit's skills and rules.")
    parser.add_argument("--target", default=str(Path.home() / ".claude"), help="Claude Code folder (default ~/.claude)")
    parser.add_argument("--dry-run", action="store_true", help="show the plan, write nothing")
    parser.add_argument("--force", action="store_true", help="replace files that differ, keeping a .bak copy of yours")
    parser.add_argument("--with-hooks", action="store_true", help="also copy the guard hook and print its settings")
    args = parser.parse_args(argv)

    target = Path(args.target).expanduser()
    report = install(target, args.dry_run, args.force, args.with_hooks)

    print(f"{'DRY RUN: nothing written. ' if args.dry_run else ''}Target: {target}")
    for heading, items in report.items():
        if heading.startswith("your CLAUDE.md") and not items:
            continue
        print(f"\n{heading}: {len(items)}")
        for item in items[:200]:
            print(f"  - {item}")
    if report["kept yours"] and not args.force:
        print("\nFiles marked 'kept yours' differ from the kit. Compare them, or rerun with --force "
              "(your copies are saved as .bak files first).")
    if args.with_hooks:
        print("\nTo turn the guard on, merge this into ~/.claude/settings.json (see hooks/README.md):\n")
        print(hook_settings(target))
    print("\nNext: start a fresh Claude Code conversation so the new skills and rules load.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
