"""The kit checks itself: the docs' counts and lists match the files, every skill is well formed,
every relative link resolves, the version agrees with the changelog, and no text file carries a
long dash or a private-looking path or email. Standard library only.

    python -m unittest tests.test_repo_consistency -v
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path
from typing import List

KIT = Path(__file__).resolve().parent.parent
TEXT_SUFFIXES = {".md", ".py", ".example", ".txt", ".yml", ".yaml", ".json", ""}
SKIP_DIRS = {".git", "__pycache__", "tmp", "scratch-clone", "node_modules"}


def read(relative: str) -> str:
    return (KIT / relative).read_text(encoding="utf-8")


def skill_names() -> List[str]:
    return sorted(p.name for p in (KIT / "skills").iterdir() if p.is_dir() and (p / "SKILL.md").exists())


def rule_files() -> List[str]:
    return sorted(p.name for p in (KIT / "rules").glob("*.md"))


def text_files() -> List[Path]:
    """Tracked and untracked-but-not-ignored files when git is available, else a folder walk."""
    try:
        out = subprocess.run(
            ["git", "-C", str(KIT), "ls-files", "--cached", "--others", "--exclude-standard"],
            capture_output=True, text=True, check=True,
        ).stdout
        paths = [KIT / line for line in out.splitlines() if line]
    except (OSError, subprocess.CalledProcessError):
        paths = [p for p in KIT.rglob("*") if p.is_file() and not (set(p.relative_to(KIT).parts) & SKIP_DIRS)]
    return [p for p in paths if p.exists() and p.suffix in TEXT_SUFFIXES and not (set(p.relative_to(KIT).parts) & SKIP_DIRS)]


def heading_count(text: str, pattern: str) -> int:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise AssertionError(f"heading not found: {pattern}")
    return int(match.group(1))


class Skills(unittest.TestCase):
    def test_every_skill_has_frontmatter_named_for_its_folder(self):
        names = skill_names()
        self.assertGreater(len(names), 0)
        for name in names:
            text = read(f"skills/{name}/SKILL.md")
            self.assertTrue(text.startswith("---\n"), f"{name}: SKILL.md must open with frontmatter")
            front = text.split("---\n", 2)[1]
            self.assertRegex(front, rf"(?m)^name:\s*{re.escape(name)}\s*$", f"{name}: frontmatter name must match the folder")
            self.assertRegex(front, r"(?m)^description:\s*\S", f"{name}: frontmatter needs a description")


class DocCounts(unittest.TestCase):
    def test_readme_counts_match_the_files(self):
        readme = read("README.md")
        self.assertEqual(heading_count(readme, r"^## The skills \((\d+)\)"), len(skill_names()))
        self.assertEqual(heading_count(readme, r"^## The rules \((\d+)\)"), len(rule_files()))
        first = readme.split("\n\n", 2)[1]
        self.assertTrue(f"{len(skill_names())} skills" in first, "the README's first paragraph has the wrong skill count")
        self.assertTrue(f"{len(rule_files())} rules" in first, "the README's first paragraph has the wrong rule count")

    def test_readme_lists_every_skill_and_rule(self):
        readme = read("README.md")
        missing = [f"skills/{n}" for n in skill_names() if f"(./skills/{n}/)" not in readme]
        missing += [f"rules/{r}" for r in rule_files() if f"(./rules/{r})" not in readme]
        missing += [f"layout: {r}" for r in rule_files() if f"── {r}" not in readme]
        missing += [f"layout: {n}/" for n in skill_names() if f"── {n}/" not in readme]
        self.assertEqual(missing, [], "README does not list these")

    def test_instructions_counts_and_lists(self):
        text = read("INSTRUCTIONS.md")
        self.assertEqual(heading_count(text, r"^### Skills \((\d+)\)"), len(skill_names()))
        self.assertEqual(heading_count(text, r"^### Rules \((\d+)\)"), len(rule_files()))
        missing = [n for n in skill_names() if f"| `{n}` |" not in text]
        missing += [r for r in rule_files() if f"| `{r}` |" not in text]
        self.assertEqual(missing, [], "INSTRUCTIONS does not list these")

    def test_architecture_counts(self):
        text = read("ARCHITECTURE.md")
        self.assertEqual(heading_count(text, r"\((\d+) rules\)"), len(rule_files()))
        self.assertEqual(heading_count(text, r"\((\d+) skills\)"), len(skill_names()))

    def test_claude_md_template_lists_every_rule(self):
        text = read("CLAUDE.md.example")
        self.assertEqual([r for r in rule_files() if f"`{r}`" not in text], [], "CLAUDE.md.example does not list these")


class Links(unittest.TestCase):
    LINK_RE = re.compile(r"\]\(([^)\s]+)\)")

    def test_relative_markdown_links_resolve(self):
        broken = []
        for path in text_files():
            if path.suffix != ".md":
                continue
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"(?s)```.*?```", "", text)  # links inside code samples are examples
            for target in self.LINK_RE.findall(text):
                if re.match(r"^(https?:|mailto:|#)", target):
                    continue
                file_part = target.split("#", 1)[0]
                if not file_part:
                    continue
                if not (path.parent / file_part).exists():
                    broken.append(f"{path.relative_to(KIT).as_posix()} -> {target}")
        self.assertEqual(broken, [], "broken relative links")


class Version(unittest.TestCase):
    def test_version_matches_the_top_changelog_entry(self):
        version = read("VERSION").strip()
        self.assertRegex(version, r"^\d+\.\d+\.\d+$")
        top = re.search(r"(?m)^## \[(\d+\.\d+\.\d+)\]", read("CHANGELOG.md"))
        self.assertIsNotNone(top, "CHANGELOG.md has no version entry")
        self.assertEqual(top.group(1), version)
        self.assertIn(f"Version {version}", read("README.md"))


class Hygiene(unittest.TestCase):
    PRIVATE_PATH_RE = re.compile(
        r"[A-Za-z]:[\\/]+Users[\\/]+(?!you\b|<|YOU\b|%)[A-Za-z0-9]"
        r"|/Users/(?!you\b|<|\$)[A-Za-z0-9]"
        r"|/home/(?!you\b|<|runner\b|\$)[A-Za-z0-9]"
    )
    EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")
    ALLOWED_EMAIL_DOMAINS = ("example.com", "example.org", "example.net", "users.noreply.github.com")

    def test_no_long_dashes(self):
        found = []
        long_dashes = (chr(0x2014), chr(0x2013))  # em and en dash, by code point
        for path in text_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if any(dash in line for dash in long_dashes):
                    found.append(f"{path.relative_to(KIT).as_posix()}:{number}")
        self.assertEqual(found, [], "em or en dashes (communication-style asks for spaced hyphens)")

    def test_no_private_paths(self):
        found = []
        for path in text_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if self.PRIVATE_PATH_RE.search(line):
                    found.append(f"{path.relative_to(KIT).as_posix()}:{number}")
        self.assertEqual(found, [], "a real-looking home folder path; use ~ or a placeholder like /home/you")

    def test_only_example_emails(self):
        found = []
        for path in text_files():
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in self.EMAIL_RE.finditer(line):
                    if not match.group(0).lower().endswith(self.ALLOWED_EMAIL_DOMAINS):
                        found.append(f"{path.relative_to(KIT).as_posix()}:{number}")
        self.assertEqual(found, [], "an email address that is not an example.com placeholder")

    def test_shell_hook_has_lf_endings(self):
        self.assertNotIn(b"\r\n", (KIT / "hooks" / "git" / "commit-msg").read_bytes())


if __name__ == "__main__":
    unittest.main()
