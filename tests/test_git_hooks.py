"""Tests for the two git hooks: hooks/git/public_repo_guard.py (pre-push) and hooks/git/commit-msg."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUARD = ROOT / "hooks" / "git" / "public_repo_guard.py"
COMMIT_MSG = ROOT / "hooks" / "git" / "commit-msg"
ZERO = "0" * 40

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


def git(folder, *args):
    return subprocess.run(["git", "-C", str(folder), *args], check=True, env=GIT_ENV,
                          capture_output=True, text=True).stdout.strip()


class PublicRepoGuard(unittest.TestCase):
    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp(prefix="public-guard-"))
        self.remote = self.scratch / "remote.git"
        self.repo = self.scratch / "work"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(self.remote)], check=True, env=GIT_ENV)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True, env=GIT_ENV)
        git(self.repo, "remote", "add", "origin", str(self.remote))
        self.denylist = self.scratch / "denylist.txt"
        self.denylist.write_text("# private names, never in a repository\nacme\\s*widgets\nsecret-host\\.internal\n",
                                 encoding="utf-8")
        self.env = {**GIT_ENV, "PUBLIC_REPO_DENYLIST": str(self.denylist)}

    def tearDown(self):
        shutil.rmtree(self.scratch, ignore_errors=True)

    def commit(self, name, content, message="add file"):
        (self.repo / name).write_text(content, encoding="utf-8")
        git(self.repo, "add", name)
        git(self.repo, "commit", "-q", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")

    def push_check(self, local_sha, remote_sha=ZERO, url=None):
        stdin = f"refs/heads/main {local_sha} refs/heads/main {remote_sha}\n"
        return subprocess.run([sys.executable, str(GUARD), "origin", url or str(self.remote)], input=stdin,
                              cwd=self.repo, env=self.env, capture_output=True, text=True, timeout=60)

    def test_renamed_and_empty_file_paths_are_checked(self):
        git(self.repo, "config", "guard.visibility", "public")
        base = self.commit("notes.txt", "plain content\n")
        git(self.repo, "mv", "notes.txt", "acme widgets plan.txt")
        git(self.repo, "commit", "-q", "-m", "rename notes")
        renamed = self.push_check(git(self.repo, "rev-parse", "HEAD"), remote_sha=base)
        self.assertEqual(renamed.returncode, 1, renamed.stderr)
        before_empty = git(self.repo, "rev-parse", "HEAD")
        empty = self.commit("acme widgets empty.txt", "", message="add empty file")
        result = self.push_check(empty, remote_sha=before_empty)
        self.assertEqual(result.returncode, 1, result.stderr)

    def test_private_name_in_a_line_blocks_a_public_push(self):
        git(self.repo, "config", "guard.visibility", "public")
        sha = self.commit("notes.md", "intro\nBuilt for Acme Widgets last spring\n")
        result = self.push_check(sha)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("notes.md:2", result.stderr)
        self.assertIn("denylist line 2", result.stderr)
        self.assertNotIn("acme\\s*widgets", result.stderr)  # the pattern itself is never printed

    def test_private_name_in_the_message_blocks(self):
        git(self.repo, "config", "guard.visibility", "public")
        sha = self.commit("a.txt", "clean\n", message="deploy to secret-host.internal")
        result = self.push_check(sha)
        self.assertEqual(result.returncode, 1)
        self.assertIn("message", result.stderr)

    def test_clean_public_push_passes(self):
        git(self.repo, "config", "guard.visibility", "public")
        sha = self.commit("a.txt", "nothing private here\n")
        self.assertEqual(self.push_check(sha).returncode, 0)

    def test_private_repository_is_not_scanned(self):
        git(self.repo, "config", "guard.visibility", "private")
        sha = self.commit("notes.md", "Acme Widgets\n")
        result = self.push_check(sha)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_unknown_visibility_is_treated_as_public(self):
        sha = self.commit("notes.md", "Acme Widgets\n")
        result = self.push_check(sha, url="https://git.example.com/team/repo.git")
        self.assertEqual(result.returncode, 1)
        self.assertIn("treated as public", result.stderr)

    def test_only_unpublished_commits_are_read(self):
        git(self.repo, "config", "guard.visibility", "public")
        first = self.commit("old.md", "Acme Widgets\n")
        git(self.repo, "push", "-q", "origin", "main")  # already public before the guard existed
        second = self.commit("new.md", "fresh and clean\n")
        self.assertEqual(self.push_check(second, remote_sha=first).returncode, 0)

    def test_denylist_inside_the_repository_blocks(self):
        git(self.repo, "config", "guard.visibility", "public")
        inside = self.repo / "denylist.txt"
        inside.write_text("acme\n", encoding="utf-8")
        self.env["PUBLIC_REPO_DENYLIST"] = str(inside)
        sha = self.commit("a.txt", "clean\n")
        result = self.push_check(sha)
        self.assertEqual(result.returncode, 1)
        self.assertIn("inside this repository", result.stderr)

    def test_missing_denylist_passes_with_a_note(self):
        git(self.repo, "config", "guard.visibility", "public")
        self.env["PUBLIC_REPO_DENYLIST"] = str(self.scratch / "absent.txt")
        sha = self.commit("a.txt", "Acme Widgets\n")
        result = self.push_check(sha)
        self.assertEqual(result.returncode, 0)
        self.assertIn("no denylist", result.stderr)


@unittest.skipIf(shutil.which("sh") is None, "needs a POSIX sh")
class CommitMsg(unittest.TestCase):
    def run_hook(self, message):
        folder = Path(tempfile.mkdtemp(prefix="commit-msg-"))
        try:
            path = folder / "MSG"
            path.write_bytes(message.encode("utf-8"))  # bytes, so the hook reads LF on every platform
            return subprocess.run(["sh", str(COMMIT_MSG), str(path)], capture_output=True, text=True, timeout=30)
        finally:
            shutil.rmtree(folder, ignore_errors=True)

    def test_co_author_trailer_blocked(self):
        result = self.run_hook("fix the login redirect\n\nCo-Authored-By: Some Agent <agent@example.com>\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Co-Authored-By", result.stdout)

    def test_generated_with_line_blocked(self):
        self.assertEqual(self.run_hook("add search\n\nGenerated with [Some Tool](https://example.com)\n").returncode, 1)
        self.assertEqual(self.run_hook("add search\n\n:robot: Generated with Claude Code\n").returncode, 1)

    def test_ordinary_messages_pass(self):
        self.assertEqual(self.run_hook("regenerated with the new script\n").returncode, 0)
        self.assertEqual(self.run_hook("fixtures were generated with a fixed seed\n").returncode, 0)

    def test_verbose_diff_below_scissors_is_ignored(self):
        message = (
            "update the hook docs\n"
            "# ------------------------ >8 ------------------------\n"
            "+Co-Authored-By: quoted inside the diff\n"
        )
        self.assertEqual(self.run_hook(message).returncode, 0)


if __name__ == "__main__":
    unittest.main()
