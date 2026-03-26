# 회원가입 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-signup-page]] - 회원가입 페이지 디자인

## 기획
- [[auth]] - 인증 시스템

## 구현 위치
- 뷰: `apps/users/views/async_views.py` → `htmx_signup()`
- 모델: `apps/users/models.py` → User
- URL: `POST /users/htmx/auth/signup/`

## 구현 내용
1. 폼 데이터 검증 (email, password, password_confirm)
2. 이메일 중복 검사
3. 비밀번호 일치 확인
4. User 생성 (acreate)
5. 성공 시 로그인 페이지로 HX-Redirect
6. 실패 시 에러와 함께 폼 재렌더링

## 선행 작업
- User 모델 정의 및 마이그레이션
- `AUTH_USER_MODEL` 설정
