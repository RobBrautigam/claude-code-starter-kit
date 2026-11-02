"""Tests for hooks/guard_bash.py: every check refuses its shape and lets the near misses through."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "hooks"))

import guard_bash  # noqa: E402

GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
    # Isolate the tests from the developer's own git setup (global hooks, templates, autocrlf).
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
}


def make_repo(branch: str) -> str:
    folder = tempfile.mkdtemp(prefix="guard-test-")
    subprocess.run(["git", "init", "-q", "-b", branch, folder], check=True, env=GIT_ENV)
    subprocess.run(["git", "-C", folder, "commit", "-q", "--allow-empty", "-m", "start"], check=True, env=GIT_ENV)
    return folder


REPOS = {}


def setUpModule():
    REPOS["main"] = make_repo("main")
    REPOS["feature"] = make_repo("feat-x")


def tearDownModule():
    for folder in REPOS.values():
        shutil.rmtree(folder, ignore_errors=True)


class Base(unittest.TestCase):
    @property
    def main_repo(self):
        return REPOS["main"]

    @property
    def feature_repo(self):
        return REPOS["feature"]

    def check(self, command, tool="Bash", cwd=None):
        refusal = guard_bash.evaluate(tool, command, cwd or self.feature_repo)
        return refusal[0] if refusal else None


class NoVerify(Base):
    def test_refused(self):
        self.assertEqual(self.check('git commit --no-verify -m "x"'), "no-verify")
        self.assertEqual(self.check("git push --no-verify origin feat-x"), "no-verify")
        self.assertEqual(self.check('git commit -n -m "x"'), "no-verify")

    def test_allowed(self):
        self.assertIsNone(self.check('git commit -m "docs: explain why --no-verify is banned"'))
        self.assertIsNone(self.check('git commit -am "fix"'))


class ForcePush(Base):
    def test_named_main_refused(self):
        self.assertEqual(self.check("git push --force origin main"), "force-push-main")
        self.assertEqual(self.check("git push origin +main"), "force-push-main")
        self.assertEqual(self.check("git push -f origin HEAD:master"), "force-push-main")
        self.assertEqual(self.check("git push --force-with-lease --all origin"), "force-push-main")

    def test_implied_main_refused(self):
        self.assertEqual(self.check("git push -f", cwd=self.main_repo), "force-push-main")
        self.assertEqual(self.check("git push -f origin HEAD", cwd=self.main_repo), "force-push-main")

    def test_own_branch_allowed(self):
        self.assertIsNone(self.check("git push --force-with-lease origin feat-x"))
        self.assertIsNone(self.check("git push -f"))  # current branch is feat-x
        self.assertIsNone(self.check("git push origin main", cwd=self.main_repo))


class ResetHard(Base):
    def test_refused(self):
        self.assertEqual(self.check("git reset --hard origin/main"), "reset-hard")
        self.assertEqual(self.check("git -C ../other reset --hard"), "reset-hard")

    def test_allowed(self):
        self.assertIsNone(self.check("git reset HEAD~1"))
        self.assertIsNone(self.check("git restore src/app.py"))


class KillByName(Base):
    def test_refused(self):
        self.assertEqual(self.check("taskkill /IM node.exe /F"), "kill-by-name")
        self.assertEqual(self.check("taskkill //IM node.exe //F"), "kill-by-name")
        self.assertEqual(self.check("pkill -f next-server"), "kill-by-name")
        self.assertEqual(self.check("killall node"), "kill-by-name")
        self.assertEqual(self.check("Stop-Process -Name node", tool="PowerShell"), "kill-by-name")
        self.assertEqual(self.check("Get-Process node | Stop-Process", tool="PowerShell"), "kill-by-name")

    def test_allowed(self):
        self.assertIsNone(self.check("taskkill /PID 4242 /F"))
        self.assertIsNone(self.check("kill 4242"))
        self.assertIsNone(self.check("Stop-Process -Id 4242", tool="PowerShell"))
        self.assertIsNone(self.check("Get-Process -Id 4242 | Stop-Process", tool="PowerShell"))


class DataDelete(Base):
    def test_refused(self):
        self.assertEqual(self.check('psql "$DATABASE_URL" -c "DROP TABLE users"'), "data-delete")
        self.assertEqual(self.check('psql -c "DELETE FROM users"'), "data-delete")
        self.assertEqual(self.check("psql <<'SQL'\nTRUNCATE orders;\nSQL"), "data-delete")
        self.assertEqual(self.check("gh repo delete me/project --yes"), "data-delete")
        self.assertEqual(self.check("dropdb app_production"), "data-delete")
        self.assertEqual(self.check("supabase db reset --linked"), "data-delete")

    def test_allowed(self):
        self.assertIsNone(self.check('psql -c "DELETE FROM sessions WHERE expires_at < now()"'))
        self.assertIsNone(self.check('git commit -m "drop table support from the export"'))
        self.assertIsNone(self.check("supabase db reset"))  # the local database

    def test_override(self):
        self.assertIsNone(self.check('GUARD_OK="owner asked to drop the scratch db" dropdb scratch'))


class RmRoot(Base):
    def test_refused(self):
        self.assertEqual(self.check("rm -rf /"), "rm-root")
        self.assertEqual(self.check('rm -rf "$HOME"'), "rm-root")
        self.assertEqual(self.check("sudo rm -fr ~"), "rm-root")

    def test_allowed(self):
        self.assertIsNone(self.check("rm -rf ./build"))
        self.assertIsNone(self.check("rm notes.txt"))


class Heredocs(Base):
    def test_unquoted_backslash_refused(self):
        self.assertEqual(self.check('python - <<EOF\nprint("a\\nb")\nEOF'), "heredoc-backslash")

    def test_double_backslash_refused_even_quoted(self):
        self.assertEqual(self.check("cat > out.txt <<'EOF'\nC:\\\\Users\\\\you\nEOF"), "heredoc-backslash")

    def test_quoted_single_backslash_allowed(self):
        self.assertIsNone(self.check("cat > out.txt <<'EOF'\nline one\\n stays literal\nEOF"))

    def test_body_is_not_read_as_commands(self):
        self.assertIsNone(self.check("cat > notes.md <<'EOF'\nNever run pkill or git reset --hard.\nEOF"))

    def test_here_string_is_not_a_heredoc(self):
        self.assertIsNone(self.check('grep -c x <<< "a\\b"'))


class Wrappers(Base):
    def test_bash_c_is_read(self):
        self.assertEqual(self.check('bash -c "git push --force origin main"'), "force-push-main")

    def test_chains_are_read(self):
        self.assertEqual(self.check("npm test && git reset --hard"), "reset-hard")


class HookProtocol(unittest.TestCase):
    def run_hook(self, payload):
        return subprocess.run(
            [sys.executable, str(ROOT / "hooks" / "guard_bash.py")],
            input=json.dumps(payload), capture_output=True, text=True, timeout=30,
        )

    def test_block_is_exit_2_with_reason_on_stderr(self):
        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "pkill node"}, "cwd": str(ROOT)})
        self.assertEqual(result.returncode, 2)
        self.assertIn("kill-by-name", result.stderr)

    def test_pass_is_exit_0_and_silent(self):
        result = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "git status"}, "cwd": str(ROOT)})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_other_tools_pass(self):
        result = self.run_hook({"tool_name": "Write", "tool_input": {"content": "pkill node"}})
        self.assertEqual(result.returncode, 0)

    def test_bad_input_never_blocks(self):
        result = subprocess.run([sys.executable, str(ROOT / "hooks" / "guard_bash.py")], input="not json",
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
