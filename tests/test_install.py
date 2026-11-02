"""Tests for scripts/install.py: installs, is idempotent, never overwrites or deletes without asking."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALL = ROOT / "scripts" / "install.py"


class Install(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp(prefix="kit-install-"))
        self.target = self.scratch / ".claude"

    def tearDown(self):
        shutil.rmtree(self.scratch, ignore_errors=True)

    def run_install(self, *args):
        return subprocess.run([sys.executable, str(INSTALL), "--target", str(self.target), *args],
                              capture_output=True, text=True, timeout=120)

    def test_dry_run_writes_nothing(self):
        result = self.run_install("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse(self.target.exists())

    def test_installs_every_skill_and_rule(self):
        self.assertEqual(self.run_install().returncode, 0)
        skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
        rules = sorted(p.name for p in (ROOT / "rules").glob("*.md"))
        self.assertEqual(sorted(p.name for p in (self.target / "skills").iterdir()), skills)
        self.assertEqual(sorted(p.name for p in (self.target / "rules").iterdir()), rules)
        for skill in skills:
            self.assertTrue((self.target / "skills" / skill / "SKILL.md").exists(), skill)
        self.assertTrue((self.target / "CLAUDE.md").exists())

    def test_second_run_changes_nothing(self):
        self.run_install()
        result = self.run_install()
        self.assertIn("installed: 0", result.stdout)

    def test_your_edits_are_kept_without_force(self):
        self.run_install()
        rule = self.target / "rules" / "git-conventions.md"
        rule.write_text("my own version\n", encoding="utf-8")
        result = self.run_install()
        self.assertIn("kept yours: 1", result.stdout)
        self.assertIn("rerun with --force", result.stdout)
        self.assertEqual(rule.read_text(encoding="utf-8"), "my own version\n")

    def test_rerun_does_not_offer_force_for_your_claude_md(self):
        self.run_install()
        result = self.run_install()
        self.assertIn("kept yours: 0", result.stdout)
        self.assertIn("your CLAUDE.md (never touched): 1", result.stdout)
        self.assertNotIn("rerun with --force", result.stdout)

    def test_force_backs_up_before_replacing(self):
        self.run_install()
        rule = self.target / "rules" / "git-conventions.md"
        rule.write_text("my own version\n", encoding="utf-8")
        self.run_install("--force")
        backups = list((self.target / "rules").glob("git-conventions.md.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(encoding="utf-8"), "my own version\n")
        self.assertEqual(rule.read_bytes(), (ROOT / "rules" / "git-conventions.md").read_bytes())

    def test_existing_claude_md_is_never_touched(self):
        self.target.mkdir(parents=True)
        (self.target / "CLAUDE.md").write_text("mine\n", encoding="utf-8")
        self.run_install("--force")
        self.assertEqual((self.target / "CLAUDE.md").read_text(encoding="utf-8"), "mine\n")

    def test_with_hooks_copies_the_guard_and_prints_settings(self):
        result = self.run_install("--with-hooks")
        self.assertTrue((self.target / "hooks" / "guard_bash.py").exists())
        printed = result.stdout[result.stdout.index("{"):result.stdout.rindex("}") + 1]
        settings = json.loads(printed)  # the printed block must be valid JSON to paste
        command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        self.assertIn("guard_bash.py", command)


if __name__ == "__main__":
    unittest.main()
