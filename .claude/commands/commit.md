# /commit — 스마트 커밋

변경 사항을 분석하여 적절한 커밋을 생성한다.
fix 커밋은 직전 관련 커밋에 amend로 합치고, 그 외에는 새 커밋을 만든다.

## 사용법

```
/commit              — 자동 분석 후 커밋 (amend/new 자동 판단)
/commit amend        — 직전 커밋에 강제 amend
/commit new          — 강제 새 커밋
/commit msg "메시지"  — 메시지 지정하여 새 커밋
```

## 커밋 메시지 규칙

### 접두어

| 작업 유형 | 접두어 | 예시 |
|----------|--------|------|
| 기획 문서 | `docs:` | `docs: 분기 시스템 기획 작성` |
| 디자인 | `design:` | `design: 다음 화 선택 UI 패턴 추가` |
| 기능 개발 | `feat:` | `feat: 회원가입 서버 로직 구현` |
| 버그 수정 | `fix:` | `fix: 로그인 CSRF 토큰 누락` |
| 리팩토링 | `refactor:` | `refactor: 컴포넌트 include 구조로 전환` |
| 테스트 | `test:` | `test: 인증 시나리오 테스트 추가` |
| 설정/도구 | `chore:` | `chore: /doc 스킬 추가` |

### 메시지 작성 원칙
- **한국어** 사용
- **what보다 why** — "로그인 CSRF 토큰 추가"보다 "로그인 CSRF 토큰 누락 수정"
- 50자 이내
- 본문이 필요하면 빈 줄 후 추가 (변경 파일 목록, 이유 등)

## 실행 절차

### 1. 변경 분석
```bash
git status --short
git diff --stat
git diff --cached --stat
```

### 2. amend 판단

**amend 조건** (모두 충족 시):
1. 변경이 직전 커밋과 **같은 기능/같은 접두어**에 속함
2. 변경 유형이 다음 중 하나:
   - lint/format 수정 (ruff, prettier)
   - 테스트 수정 (기존 테스트 assertion 조정)
   - 누락 파일 추가 (migration, __init__.py)
   - 오타/import 정리
3. 직전 커밋이 **아직 push되지 않음** (`git log origin/{현재브랜치}..HEAD`로 확인. remote 브랜치가 없으면 모든 로컬 커밋이 unpushed로 간주 → amend 가능)

**새 커밋 조건**:
- 다른 기능이나 다른 접두어에 속하는 변경
- 의미 있는 독립적 변경 (새 기능, 새 테스트, 새 문서)
- 직전 커밋이 이미 push됨

### 3. 스테이징
```bash
# 관련 파일만 선택적으로 add
git add <관련 파일들>
```

**주의**:
- `.env`, credentials, 시크릿 파일은 절대 add하지 않음
- `git add -A`나 `git add .`는 사용하지 않음
- 변경과 무관한 파일은 스테이징하지 않음

### 4. 커밋 실행

**amend인 경우**:
```bash
# 사용자에게 먼저 확인
# "직전 커밋 '{메시지}'에 amend할까요?"
git commit --amend -m "$(cat <<'EOF'
{기존 또는 수정된 메시지}

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

**새 커밋인 경우**:
```bash
git commit -m "$(cat <<'EOF'
{접두어}: {메시지}

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### 5. 검증
```bash
git log --oneline -3
git status --short
```

## amend 판단 예시

```
직전 커밋: "feat: CS 1:1 관리자 채팅 구현"
현재 변경: ruff format 수정 + migration 추가
→ amend (같은 feat, lint/누락 파일)

직전 커밋: "feat: CS 1:1 관리자 채팅 구현"  
현재 변경: 새 테스트 파일 작성
→ 새 커밋 "test: CS 1:1 채팅 테스트 케이스 작성" (다른 접두어)

직전 커밋: "test: CS 채팅 테스트 작성"
현재 변경: 테스트 assertion 수정 (템플릿에 맞춰 조정)
→ amend (같은 test, assertion 조정)

직전 커밋: "docs: CS 채팅 기획 변경"
현재 변경: 새 모델 + 뷰 구현
→ 새 커밋 "feat: ..." (다른 작업)
```

## 규칙
- amend는 **반드시 사용자 확인 후** 실행 (push된 커밋 amend 방지)
- 기획/디자인/개발 커밋을 **절대 섞지 않음**
- Co-Authored-By 헤더 항상 포함
- pre-commit hook(ruff) 실패 시: 수정 → 같은 커밋으로 재시도 (새 커밋 아님)
