# 로그아웃 서버 로직

> 개발 문서

## 상태: 미구현

## 디자인
- [[design-navbar-auth]] - 네비게이션 인증 상태

## 기획
- [[auth]] - 인증 시스템

## 구현 위치
- 뷰: `apps/users/views/async_views.py` → `htmx_logout()`
- URL: `POST /users/htmx/auth/logout/`

## 구현 내용
1. 세션 무효화 (Django logout)
2. HX-Redirect → `/`
