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

## 병렬 작업: Worktree + Subagent

독립적인 작업이 여러 개일 때, **worktree isolation**으로 subagent를 병렬 실행하고 결과를 merge한다.

### 언제 사용하나

- 서로 다른 파일/앱을 수정하는 독립적인 작업이 2개 이상일 때
- 예: "users 앱에 로그아웃 구현" + "articles 앱 모델 생성"을 동시에

### 언제 사용하지 않나

- 같은 파일을 수정해야 하는 작업 (충돌 위험)
- 작업 간 의존성이 있을 때 (B가 A의 결과에 의존)
- 단일 작업이거나 작업량이 적을 때

### 실행 방법

```
1. Agent tool에 isolation: "worktree" 설정
2. 각 subagent에 명확한 작업 범위와 브랜치명 지시
3. 결과 확인 후 dev 브랜치에 순차 merge
```

### 주의사항

- merge 전 각 worktree의 변경 사항을 반드시 리뷰
- 충돌 발생 시 사용자에게 확인 후 해결
- worktree에서 생성된 브랜치는 merge 후 정리
