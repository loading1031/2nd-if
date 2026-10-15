"""Install the shared commit-msg check without replacing other Git hooks."""

import subprocess
from pathlib import Path

MARKER = "# 2nd-if shared commit policy"
HOOK = """#!/bin/sh
# 2nd-if shared commit policy
set -e
root=$(git rev-parse --show-toplevel)
# Older branches/worktrees do not opt into this policy until they contain it.
if ! test -f "$root/scripts/check_git_policy.py"; then
    exit 0
fi
# Git-generated merge messages are not ordinary authored commits.
if test -f "$(git rev-parse --git-path MERGE_HEAD)"; then
    exit 0
fi
exec python3 "$root/scripts/check_git_policy.py" commit "$1"
"""


def main() -> int:
    hooks = Path(subprocess.check_output(["git", "rev-parse", "--git-path", "hooks"], text=True).strip())
    target = hooks / "commit-msg"
    if target.is_symlink() or (target.exists() and MARKER not in target.read_text()):
        print(f"기존 commit-msg를 덮어쓰지 않습니다: {target}")
        return 1
    hooks.mkdir(parents=True, exist_ok=True)
    target.write_text(HOOK)
    target.chmod(0o755)
    print(f"commit-msg 설치: {target.resolve()} (기존 pre-commit 유지)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
