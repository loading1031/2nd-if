# /merge — 워크트리 병렬 작업 후처리

워크트리 에이전트들의 결과를 dev에 merge한 후, 공통 파일을 정리하는 스킬.

## 사용법

```
/merge              — 전체 후처리 (역링크 + CSS + 검사)
/merge backlinks    — 역링크만 추가
/merge css          — CSS 빌드만
/merge check        — 충돌 검사만
```

## 실행 절차

### 1. 워크트리 merge 확인
- `git worktree list`로 남은 워크트리 확인
- 미merge 워크트리가 있으면 순차 merge 진행
- 충돌 발생 시 양쪽 모두 포함하는 방향으로 해결

### 2. 역링크 추가 (backlinks)
새로 생성된 디자인/개발 문서를 기획 문서에 연결:
1. `docs/design/` 에서 새로 추가된 파일 확인
2. 각 디자인 문서의 `## 기획` 섹션에서 링크된 specs 파일 확인
3. 해당 specs 파일의 `## 디자인 문서` 섹션에 역링크 추가
4. `docs/dev/`도 동일하게 처리
5. `docs/specs/index.md` 갱신

### 3. CSS 빌드
```bash
cd server && ./tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

### 4. 충돌 검사
`/doc check` 실행하여:
- 깨진 [[링크]] 확인
- 누락된 역링크 확인
- 필드/상태 불일치 확인

### 5. 워크트리 정리
```bash
git worktree list
# 각 워크트리 제거
git worktree remove --force .claude/worktrees/{name}
git branch -D worktree-{name}
```

### 6. 커밋
모든 후처리를 단일 커밋으로:
```
chore: 워크트리 merge 후처리 (역링크, CSS, 정리)
```

## 규칙
- 워크트리 에이전트는 새 파일만 생성, 기존 파일 수정 안 함
- 이 스킬이 기존 파일(specs 역링크, index 등)을 일괄 정리
- 후처리 완료 후 반드시 /doc check로 검증
