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

### 0. 전제조건 체크

1. **워크트리 존재 확인**:
```bash
git worktree list
```
- dev 외에 워크트리가 없으면: "merge할 워크트리가 없습니다. 먼저 병렬 작업을 수행하세요." 안내 후 종료

2. **dev 브랜치 상태 확인**:
```bash
git status
```
- 현재 브랜치가 dev가 아니면: `git checkout dev` 안내
- uncommitted 변경이 있으면: "dev에 커밋되지 않은 변경이 있습니다. 먼저 커밋하거나 stash하세요." 안내 후 종료

### 1. 워크트리 merge

- `git worktree list`로 남은 워크트리 확인
- 미merge 워크트리가 있으면 순차 merge 진행:
```bash
git merge worktree-{name}
```

#### 충돌 해결 전략

충돌 발생 시 유형별로 처리:

| 충돌 유형 | 처리 방법 |
|----------|----------|
| **import 충돌** | 양쪽 import 모두 유지. 중복 제거 후 알파벳순 정렬 |
| **urls.py 등 목록형 파일** | 양쪽 항목 모두 유지. urlpatterns, INSTALLED_APPS 등은 순서만 정리 |
| **같은 함수/클래스 수정** | 자동 해결 불가 → 사용자에게 알림. 양쪽 변경 내용을 보여주고 선택 요청 |
| **설정 파일 (settings, config)** | 양쪽 설정 모두 유지. 값이 다른 경우 사용자에게 확인 |
| **템플릿 파일** | 구조 변경은 사용자 확인 필요. 단순 추가는 양쪽 모두 유지 |

**merge 실패 시**:
```bash
# 충돌 상태 확인
git diff --name-only --diff-filter=U

# 해결 불가 시 merge 중단
git merge --abort
```
- 사용자에게 충돌 파일 목록과 함께 "수동 해결이 필요합니다" 안내
- `git merge --abort`로 원래 상태로 복원 가능함을 알림

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
- 충돌 해결 시 자동 판단이 불확실하면 반드시 사용자에게 확인
- merge 실패 시 `git merge --abort`로 안전하게 복원 후 사용자에게 보고
