# /commit — 명시적 범위 커밋

먼저 `.claude/rules/workflow.md`를 읽는다. `/commit [new|amend|msg "메시지"]`를 지원한다.

1. 현재 브랜치·작업 트리·기존 index를 확인하고 관련 이슈를 찾는다.
2. 사용자 요청 범위의 파일만 선택한다. 다른 WIP·시크릿은 제외한다. 전체 스테이징을 하지 않는다.
3. 접두어와 변경 이유가 있는 메시지를 작성하고 작업 브랜치에서는 본문 끝에 `Refs: #N` 또는 이슈 없는 작은 수정의 `Refs: maintenance`를 넣는다.
4. `python3 scripts/check_git_policy.py commit <message-file> --branch <현재브랜치>`로 검사한다.
5. 명시한 파일만 스테이징하고 같은 파일 목록으로 경로 제한 커밋을 만든다. 메시지는 임시 파일에서 `python3 scripts/commit_with_retry.py -F <message-file> -- <파일 목록>`으로 전달한다. 스크립트는 `index.lock` 경합이면 최대 30초간 기다렸다 재시도하며, 대기 시간은 `--timeout <초>`로 조정할 수 있다.
6. 커밋 후 포함 파일·메시지·남은 변경을 확인한다.

기본은 새 커밋이다. `amend`는 사용자의 명시적 요청이고 원격 게시 전인 경우에만 수행한다. 훅 실패는 원인을 고쳐 재검증하고 우회하지 않는다. 임의 모델명·저자 이메일을 추가하지 않는다. push는 별도 승인 범위를 확인한다.
