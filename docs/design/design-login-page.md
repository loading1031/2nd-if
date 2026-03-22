# 로그인 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[auth]] - 인증 시스템

## 패턴 라이브러리
- `/pattern-library/` → pages → login
- `/pattern-library/` → pages → login_error (에러 상태)

## 프로덕션 템플릿
- `apps/users/templates/pages/login.html`

## 레이아웃
- 화면 중앙 정렬 카드 (`max-w-md`)
- 카드 내부: 제목 → 에러 알림 → 폼 → 구분선 → 회원가입 링크

## 필드
| 필드 | 타입 | placeholder | 검증 |
|------|------|-------------|------|
| email | email | example@email.com | 형식 검증 |
| password | password | •••••••• | - |
| remember-me | checkbox | - | 세션 유지 |

## 에러 표현
- 인증 실패: 폼 상단 `alert-error` + "이메일 또는 비밀번호가 올바르지 않습니다."

## 사용 컴포넌트
- `components/form_field.html`
- `components/alert.html`

## 개발
- [[dev-auth-login]] - 로그인 서버 로직
