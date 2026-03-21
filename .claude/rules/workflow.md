# 개발 워크플로우 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## Git 브랜치 전략

```
main          ← 안정 버전, 직접 커밋 금지 (초기 세팅 제외)
└── dev       ← 개발 브랜치, 모든 작업의 기준점
    ├── feat/signup-logic
    ├── feat/article-crud
    └── fix/login-error
```

### 규칙

1. **main**: 초기 세팅 완료 후 직접 커밋하지 않음. dev에서 PR/merge로만 반영.
2. **dev**: 모든 feature/fix 브랜치의 기준. 작업 완료 후 dev로 merge.
3. **작업 브랜치**: `dev`에서 분기. 네이밍: `feat/{기능명}`, `fix/{버그명}`, `refactor/{대상}`

### 브랜치 생성 예시

```bash
git checkout dev
git checkout -b feat/article-crud
# 작업 완료 후
git checkout dev
git merge feat/article-crud
```

## 커밋 규칙

작업 단위마다 즉시 커밋한다. 밀어두지 않는다.

### 커밋 분리 기준

| 작업 유형 | 커밋 접두어 | 예시 |
|----------|-----------|------|
| 기획 문서 | `docs:` | `docs: 분기 시스템 기획 작성` |
| 디자인 (패턴/템플릿) | `design:` | `design: 다음 화 선택 UI 패턴 추가` |
| 기능 개발 | `feat:` | `feat: 회원가입 서버 로직 구현` |
| 버그 수정 | `fix:` | `fix: 로그인 CSRF 토큰 누락` |
| 리팩토링 | `refactor:` | `refactor: 컴포넌트 include 구조로 전환` |
| 설정/도구 | `chore:` | `chore: /doc 스킬 추가` |

### 원칙

- **기획/디자인/개발 커밋을 섞지 않는다**
- 스킬, 규칙 등 도구 변경도 별도 커밋
- 디펜던시 없는 변경은 발생 즉시 커밋

## 병렬 작업: Worktree + Subagent

독립적인 작업이 여러 개일 때, **worktree isolation**으로 subagent를 병렬 실행하고 결과를 merge한다.

### 언제 사용하나

- 서로 다른 파일/앱을 수정하는 독립적인 작업이 2개 이상일 때
- 예: "users 앱에 로그아웃 구현" + "articles 앱 모델 생성"을 동시에

### 언제 사용하지 않나

- 같은 파일을 수정해야 하는 작업 (충돌 위험)
- 작업 간 의존성이 있을 때 (B가 A의 결과에 의존)
- 단일 작업이거나 작업량이 적을 때

### 워크트리 에이전트 역할 분리 (충돌 방지)

워크트리 에이전트는 **새 파일 생성만** 한다. 기존 공통 파일은 수정하지 않는다.

```
워크트리 Agent: 새 파일만 생성
  - components/, patterns/ 템플릿
  - docs/design/ 디자인 문서
  - 기존 파일(specs/, index.md 등) 수정 금지

    ↓ merge (충돌 없음)

dev에서 정리: /merge 스킬로 후처리
  - specs 문서에 디자인 역링크 추가
  - index.md 갱신
  - CSS 빌드
  - 충돌 검사 (/doc check)
```

### 실행 방법

```
1. Agent tool에 isolation: "worktree" 설정
2. 각 subagent에 "기존 파일 수정 금지" 명시
3. 전체 완료 후 dev에서 순차 merge
4. /merge 스킬로 후처리 (역링크, CSS, 검사)
```

### 주의사항

- 워크트리 에이전트에게 "기존 파일 수정 금지, 새 파일 생성만" 반드시 명시
- merge 전 각 worktree의 변경 사항을 반드시 리뷰
- worktree에서 생성된 브랜치는 merge 후 정리
