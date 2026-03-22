# 회원가입 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[auth]] - 인증 시스템

## 패턴 라이브러리
- `/pattern-library/` → pages → signup
- `/pattern-library/` → pages → signup_error (에러 상태)

## 프로덕션 템플릿
- `apps/users/templates/pages/signup.html`

## 레이아웃
- 화면 중앙 정렬 카드 (`max-w-md`)
- 카드 내부: 제목 → 에러 알림 → 폼 → 구분선 → 로그인 링크

## 필드
| 필드 | 타입 | placeholder | 검증 |
|------|------|-------------|------|
| email | email | example@email.com | 형식 검증, 중복 검사 |
| password | password | •••••••• | 최소 8자 |
| password_confirm | password | •••••••• | password와 일치 |

## 에러 표현
- 필드 에러: `input-error` 클래스 + 필드 하단 빨간 텍스트
- 전체 에러: 폼 상단 `alert-error`

## 사용 컴포넌트
- `components/form_field.html`
- `components/alert.html`

## 개발
- [[dev-auth-signup]] - 회원가입 서버 로직
