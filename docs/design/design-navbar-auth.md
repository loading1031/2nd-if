# 네비게이션 인증 상태 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[auth]] - 인증 시스템

## 패턴 라이브러리
- `/pattern-library/` → components → navbar

## 프로덕션 템플릿
- `templates/components/navbar.html`

## 상태별 표시

### 비로그인
- "로그인" 텍스트 링크
- "회원가입" primary 버튼

### 로그인
- 이메일 텍스트 표시
- "로그아웃" ghost 버튼

## 사용 컴포넌트
- `components/navbar.html`

## 개발
- [[dev-auth-login]] - 로그인 상태 확인
- [[dev-auth-logout]] - 로그아웃 처리
