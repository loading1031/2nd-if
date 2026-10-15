import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "check_git_policy.py"
SPEC = importlib.util.spec_from_file_location("git_policy", SCRIPT)
policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(policy)


class MessagePolicyTest(unittest.TestCase):
    def test_issue_and_maintenance_trailers(self):
        for branch, message in [
            ("codex/chore/23-planning", "chore: 규칙 전환\n\nRefs: #23\n"),
            ("plan/23-planning", "docs: 요구사항 정리\n\nRefs: #23\n"),
            ("feature/ai-worldbible-draft", "feat: 세계관 저장\n\nRefs: #17\n"),
            ("fix/maintenance", "fix: 오타 수정\n\nRefs: maintenance\n"),
            ("dev", "chore: 도구 설정\n"),
        ]:
            with self.subTest(branch=branch):
                self.assertEqual(policy.validate_message(message, branch), [])

    def test_missing_prefix_or_trailer_and_inline_ref_are_rejected(self):
        for message in ["메시지\n\nRefs: #23", "feat: 구현", "feat: 구현\n\n본문 Refs: #23"]:
            with self.subTest(message=message):
                self.assertTrue(policy.validate_message(message, "feat/23-topic"))

    def test_product_commits_on_integration_branches_are_rejected(self):
        for branch in ["dev", "main"]:
            for prefix in ["feat", "fix", "refactor", "test", "design"]:
                self.assertTrue(policy.validate_message(f"{prefix}: 직접 변경\n\nRefs: #23", branch))

    def test_closing_keywords_belong_in_pr_body(self):
        for closing in [
            "Closes #23",
            "Fixes loading1031/2nd-if#23",
            "Resolves https://github.com/loading1031/2nd-if/issues/23",
        ]:
            self.assertTrue(policy.validate_message(f"feat: 구현\n\n{closing}\nRefs: #23", "feat/23-topic"))

    def test_trailer_must_be_in_final_trailer_block(self):
        self.assertTrue(policy.validate_message("feat: 구현\n\nRefs: #23\n\n뒤에 추가 본문", "feat/23-topic"))
        self.assertEqual(
            policy.validate_message("feat: 구현\n\nRefs: #23\nCo-Authored-By: Person <p@example.com>", "feat/23-topic"),
            [],
        )

    def test_cli_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            message = Path(directory) / "message"
            message.write_text("feat: 구현\n\nRefs: #17\n\n# Git editor comments\n")
            good = subprocess.run(
                [sys.executable, str(SCRIPT), "commit", str(message), "--branch", "feature/world"], capture_output=True
            )
            bad = subprocess.run(
                [sys.executable, str(SCRIPT), "commit", str(message), "--branch", "dev"], capture_output=True
            )
            self.assertEqual(good.returncode, 0)
            self.assertNotEqual(bad.returncode, 0)


class PRPolicyTest(unittest.TestCase):
    def test_work_targets_dev_and_release_is_dev_to_main(self):
        self.assertEqual(policy.validate_pr("dev", "codex/chore/23-planning"), [])
        self.assertEqual(policy.validate_pr("main", "dev"), [])
        self.assertTrue(policy.validate_pr("main", "feat/23-topic"))
        self.assertTrue(policy.validate_pr("other", "feat/23-topic"))

    def test_pull_request_commit_range_uses_real_git_history(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)

            def git(*args):
                return subprocess.check_output(["git", "-C", directory, *args], text=True).strip()

            git("init", "-b", "dev")
            git("config", "user.name", "Policy Test")
            git("config", "user.email", "policy@example.com")
            git("commit", "--allow-empty", "-m", "legacy initial commit")
            base = git("rev-parse", "HEAD")
            git("checkout", "-b", "feat/23-topic")
            git("commit", "--allow-empty", "-m", "feat: 구현\n\nRefs: #23")
            event = repo / "event.json"

            def check(base_ref="dev", head_ref="feat/23-topic", extra=(), head_repo="owner/repo"):
                event.write_text(
                    json.dumps(
                        {
                            "pull_request": {
                                "base": {"ref": base_ref, "sha": base, "repo": {"full_name": "owner/repo"}},
                                "head": {
                                    "ref": head_ref,
                                    "sha": git("rev-parse", "HEAD"),
                                    "repo": {"full_name": head_repo},
                                },
                            }
                        }
                    )
                )
                return subprocess.run(
                    [sys.executable, str(SCRIPT), "pr", str(event), *extra], cwd=repo, capture_output=True
                )

            self.assertEqual(check().returncode, 0)
            self.assertEqual(check(extra=("--legacy-base", "a" * 40)).returncode, 0)
            self.assertEqual(check("main", "dev").returncode, 0)
            self.assertNotEqual(check("main", "dev", head_repo="fork/repo").returncode, 0)
            git("commit", "--allow-empty", "-m", "missing prefix")
            self.assertNotEqual(check().returncode, 0)
            legacy = git("rev-parse", "HEAD")
            git("commit", "--allow-empty", "-m", "chore: 전환 이후 변경\n\nRefs: #23")
            self.assertEqual(check(extra=("--legacy-base", legacy)).returncode, 0)
            git("commit", "--allow-empty", "-m", "another invalid message")
            self.assertNotEqual(check(extra=("--legacy-base", legacy)).returncode, 0)


class HookInstallationTest(unittest.TestCase):
    def test_installed_hook_blocks_bad_message_and_keeps_precommit(self):
        installer = SCRIPT.with_name("install_git_hooks.py")
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-b", "feat/23-topic", directory], check=True, capture_output=True)
            repo = Path(directory)
            scripts = repo / "scripts"
            scripts.mkdir()
            (scripts / SCRIPT.name).write_text(SCRIPT.read_text())
            hook = repo / ".git/hooks/pre-commit"
            hook.write_text("#!/bin/sh\nexit 0\n")
            hook.chmod(0o755)
            subprocess.run([sys.executable, str(installer)], cwd=repo, check=True, capture_output=True)
            self.assertEqual(hook.read_text(), "#!/bin/sh\nexit 0\n")
            for message, expected in [("bad message", False), ("chore: 설정\n\nRefs: #23", True)]:
                result = subprocess.run(
                    [
                        "git",
                        "-c",
                        "user.name=Policy Test",
                        "-c",
                        "user.email=policy@example.com",
                        "commit",
                        "--allow-empty",
                        "-m",
                        message,
                    ],
                    cwd=repo,
                    capture_output=True,
                )
                self.assertEqual(result.returncode == 0, expected, result.stderr.decode())

    def test_hook_does_not_block_older_checkout_without_policy_file(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-b", "legacy", directory], check=True, capture_output=True)
            subprocess.run(
                [sys.executable, str(SCRIPT.with_name("install_git_hooks.py"))],
                cwd=directory,
                check=True,
                capture_output=True,
            )
            result = subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=Policy Test",
                    "-c",
                    "user.email=policy@example.com",
                    "commit",
                    "--allow-empty",
                    "-m",
                    "legacy message",
                ],
                cwd=directory,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_installer_preserves_unknown_commit_hook(self):
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", directory], check=True, capture_output=True)
            hook = Path(directory) / ".git/hooks/commit-msg"
            original = "#!/bin/sh\n# another tool\nexit 0\n"
            hook.write_text(original)
            result = subprocess.run(
                [sys.executable, str(SCRIPT.with_name("install_git_hooks.py"))], cwd=directory, capture_output=True
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(hook.read_text(), original)


if __name__ == "__main__":
    unittest.main()
