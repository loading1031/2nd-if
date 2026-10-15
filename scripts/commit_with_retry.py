#!/usr/bin/env python3
"""Retry git commit when another Git process briefly owns the index lock."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_TIMEOUT = 30
RETRY_DELAY = 1


def git_path(path: str) -> Path:
    resolved = subprocess.check_output(["git", "rev-parse", "--git-path", path], text=True).strip()
    return Path(resolved).resolve()


def is_lock_contention(stderr: str, lock_path: Path) -> bool:
    message = stderr.lower()
    lock = str(lock_path).lower()
    lock_creation_failure = "unable to create" in message or "permission denied" in message or "operation not permitted" in message
    return lock in message and ("file exists" in message or lock_creation_failure)


def run_commit(args: list[str], timeout: int) -> int:
    lock_path = git_path("index.lock")
    deadline = time.monotonic() + timeout
    attempt = 1

    while True:
        result = subprocess.run(["git", "commit", *args], text=True, capture_output=True)
        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.returncode == 0:
            if result.stderr:
                sys.stderr.write(result.stderr)
            return 0

        if result.stderr:
            sys.stderr.write(result.stderr)
        if not is_lock_contention(result.stderr, lock_path):
            return result.returncode

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print(f"인덱스 잠금 경합이 {timeout}초 동안 해소되지 않아 중단했습니다: {lock_path}", file=sys.stderr)
            return result.returncode

        delay = min(RETRY_DELAY, remaining)
        print(f"다른 Git 작업이 인덱스를 사용 중입니다. {delay:.0f}초 후 재시도합니다 ({attempt}).", file=sys.stderr)
        time.sleep(delay)
        attempt += 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="최대 대기 시간(초, 기본 30)")
    parsed, args = parser.parse_known_args()
    if args and args[0] == "--":
        args = args[1:]
    if parsed.timeout < 0:
        parser.error("--timeout은 0 이상이어야 합니다")
    if not args or args[0] in {"-h", "--help"}:
        parser.error("git commit 인자를 지정하세요. 예: scripts/commit_with_retry.py -F /tmp/msg -- file.md")
    if args[0] == "commit":
        args = args[1:]
    return run_commit(args, parsed.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
