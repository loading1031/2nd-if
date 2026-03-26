# 로그인 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-login-page]] - 로그인 페이지 디자인

## 기획
- [[auth]] - 인증 시스템

## 구현 위치
- 뷰: `apps/users/views/async_views.py` → `htmx_login()`
- URL: `POST /users/htmx/auth/login/`

## 구현 내용
1. 이메일/비밀번호로 인증
2. remember-me 체크 시 세션 연장
3. 성공 시 홈으로 HX-Redirect
4. 실패 시 alert-error와 함께 폼 재렌더링

## 선행 작업
- User 모델 정의 및 마이그레이션
- [[dev-auth-signup]] 완료 (테스트용 계정 필요)
