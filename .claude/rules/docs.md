# 기획 문서 관리 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## 문서 위치

`docs/` 폴더 = Obsidian 볼트. 마크다운 파일로 직접 읽고 쓴다.

## 3계층 구조: 기획 → 디자인 → 개발

```
docs/
├── specs/          ← 기획 (1)
│   ├── index.md
│   └── auth.md          → [[design-signup-page]], [[design-login-page]]
│
├── design/         ← 디자인 (N) — 기획에 의존
│   ├── design-signup-page.md   → [[auth]], [[dev-auth-signup]]
│   ├── design-login-page.md    → [[auth]], [[dev-auth-login]]
│   └── design-navbar-auth.md   → [[auth]]
│
├── dev/            ← 개발 (M) — 디자인/기획에 의존
│   ├── dev-auth-signup.md      → [[design-signup-page]], [[auth]]
│   ├── dev-auth-login.md       → [[design-login-page]], [[auth]]
│   └── dev-auth-logout.md      → [[design-navbar-auth]], [[auth]]
│
└── notes/          ← 자유 메모
```

### 의존성 방향

```
기획 (specs/)
  ↓ 1:N
디자인 (design/)
  ↓ 1:M
개발 (dev/)
```

- **기획 → 디자인**: 기획 문서에서 `## 디자인 문서` 섹션에 디자인 링크
- **디자인 → 기획**: 디자인 문서에서 `## 기획` 섹션에 기획 링크 (역참조)
- **디자인 → 개발**: 디자인 문서에서 `## 개발` 섹션에 개발 링크
- **개발 → 디자인**: 개발 문서에서 `## 디자인` 섹션에 디자인 링크 (역참조)

## 파일명 규칙

| 계층 | 접두어 | 예시 |
|------|--------|------|
| 기획 | 없음 | `auth.md`, `article.md` |
| 디자인 | `design-` | `design-signup-page.md` |
| 개발 | `dev-` | `dev-auth-signup.md` |

## 문서 템플릿

### 기획 (specs/)

```markdown
# 기능명

> 기획 문서

## 상태: 기획 완료

## 개요
한 줄 설명

## 요구사항
- ...

## 사용자 플로우
1. ...

## 데이터 모델
- ...

## 디자인 문서
- [[design-xxx]] - 설명
```

### 디자인 (design/)

```markdown
# 페이지/컴포넌트명 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[기획문서]] - 설명

## 패턴 라이브러리
- `/pattern-library/` → ...

## 프로덕션 템플릿
- `apps/.../templates/...`

## 레이아웃
설명

## 필드
| 필드 | 타입 | placeholder | 검증 |

## 사용 컴포넌트
- `components/...`

## 개발
- [[dev-xxx]] - 설명
```

### 개발 (dev/)

```markdown
# 기능명 서버 로직

> 개발 문서

## 상태: 미구현

## 디자인
- [[design-xxx]] - 설명

## 기획
- [[기획문서]] - 설명

## 구현 위치
- 뷰: `apps/.../views/async_views.py`
- URL: `METHOD /url/path/`

## 구현 내용
1. ...

## 선행 작업
- ...
```

## 상태 값

| 상태 | 의미 |
|------|------|
| 기획 완료 | 요구사항 확정 |
| 디자인 완료 | 패턴 라이브러리에 UI 있음 |
| 미구현 | 서버 로직 없음 |
| 구현 완료 | 프로덕션 코드 동작 |

## 충돌 감지 규칙

기획을 추가하거나 변경할 때:
1. `[[링크]]`된 모든 문서를 읽어서 내용 충돌 확인
2. 디자인이 기획과 맞지 않으면 알림
3. 개발이 디자인과 맞지 않으면 알림
4. 충돌 발견 시 사용자에게 즉시 보고하고, 어떤 문서를 수정해야 하는지 제안
