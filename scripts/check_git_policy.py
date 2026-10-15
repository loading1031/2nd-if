"""Shared commit/PR policy. Uses only Python's standard library and Git."""

import argparse
import json
import re
import subprocess
from pathlib import Path

PREFIX = re.compile(r"^(docs|feat|fix|refactor|test|chore|design)(\([^)]+\))?!?: \S")
PRODUCT = re.compile(r"^(feat|fix|refactor|test|design)(\([^)]+\))?!?:")
REFS = re.compile(r"^Refs: (#[1-9]\d*|maintenance)$", re.MULTILINE)
CLOSING = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+"
    r"(?:#[1-9]\d*|[\w.-]+/[\w.-]+#[1-9]\d*|https://github\.com/[^\s]+/issues/[1-9]\d*)",
    re.IGNORECASE,
)


def validate_message(message: str, branch: str, *, direct_commit: bool = True) -> list[str]:
    lines = message.strip().splitlines()
    subject = lines[0] if lines else ""
    errors = []
    if not PREFIX.match(subject):
        errors.append("커밋 첫 줄에 docs/feat/fix/refactor/test/chore/design 접두어가 필요합니다.")
    if direct_commit and branch in {"dev", "main"} and PRODUCT.match(subject):
        errors.append("제품 코드 변경은 작업 브랜치에서 커밋하세요.")
    trailer = message.strip().rsplit("\n\n", 1)[-1]
    if (branch not in {"dev", "main"} or not direct_commit) and (
        not REFS.search(trailer) or any(not re.match(r"^[A-Za-z][A-Za-z-]*: .+", line) for line in trailer.splitlines())
    ):
        errors.append("본문 마지막 trailer 묶음에 Refs: #<이슈> 또는 Refs: maintenance가 필요합니다.")
    if CLOSING.search(message):
        errors.append("이슈 종료 키워드는 커밋 대신 PR 본문에 넣으세요.")
    return errors


def validate_pr(base: str, head: str) -> list[str]:
    if base == "dev" or (base == "main" and head == "dev"):
        return []
    return ["일반 작업 PR의 base는 dev이며 릴리스만 dev → main입니다."]


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def check_pr(event_path: Path, legacy_bases: list[str]) -> list[str]:
    pr = json.loads(event_path.read_text())["pull_request"]
    base, head = pr["base"], pr["head"]
    errors = validate_pr(base["ref"], head["ref"])
    if base["ref"] == "main" and head.get("repo", {}).get("full_name") != base.get("repo", {}).get("full_name"):
        errors.append("릴리스 dev 브랜치는 대상 저장소의 브랜치여야 합니다.")
    if any(not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in legacy_bases):
        raise ValueError("legacy-base는 불변 40자리 커밋 SHA여야 합니다.")
    available = [
        sha
        for sha in legacy_bases
        if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], capture_output=True).returncode == 0
    ]
    exclusions = ["--not", *available] if available else []
    for sha in git("rev-list", "--no-merges", f"{base['sha']}..{head['sha']}", *exclusions).splitlines():
        for error in validate_message(git("show", "-s", "--format=%B", sha), head["ref"], direct_commit=False):
            errors.append(f"{sha[:12]}: {error}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commit = commands.add_parser("commit")
    commit.add_argument("message", type=Path)
    commit.add_argument("--branch")
    pr = commands.add_parser("pr")
    pr.add_argument("event", type=Path)
    pr.add_argument("--legacy-base", action="append", default=[])
    args = parser.parse_args()
    try:
        if args.command == "commit":
            branch = args.branch if args.branch is not None else git("branch", "--show-current")
            message = subprocess.check_output(
                ["git", "stripspace", "--strip-comments"], input=args.message.read_text(), text=True
            )
            errors = validate_message(message, branch)
        else:
            errors = check_pr(args.event, args.legacy_base)
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print(f"Git 규칙 검사 실패: {error}")
        return 1
    for error in errors:
        print(error)
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
