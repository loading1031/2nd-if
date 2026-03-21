# 인증 시스템

> 기획 문서

## 상태: 기획 완료

## 개요
이메일/비밀번호 기반 인증 시스템. 회원가입, 로그인, 로그아웃을 제공한다.

## 요구사항
- 이메일을 로그인 ID로 사용
- 비밀번호는 최소 8자 이상
- 로그인 상태 유지 옵션 (remember-me)
- 비밀번호 찾기 (추후)

## 사용자 플로우

### 회원가입 - 정상
1. 비회원 → 이메일/닉네임/비밀번호 입력 → 로그인 페이지로 이동
2. 비밀번호 정확히 8자 → 성공

### 회원가입 - 에러
3. 이미 등록된 이메일 → "이미 사용 중인 이메일입니다." 에러
4. 비밀번호 불일치 → "비밀번호가 일치하지 않습니다." 에러
5. 비밀번호 7자 이하 → 에러
6. 이메일 빈칸 → 에러
7. 닉네임 빈칸 → 에러
8. 잘못된 이메일 형식 → 에러

### 로그인 - 정상
9. 이메일/비밀번호 → 홈으로 이동
10. remember-me 체크 → 세션 유지

### 로그인 - 에러
11. 잘못된 비밀번호 → "이메일 또는 비밀번호가 올바르지 않습니다."
12. 존재하지 않는 이메일 → 동일 에러 메시지
13. 이메일/비밀번호 빈칸 → 에러

### 로그아웃
14. 로그인 상태 → 로그아웃 → 홈으로 이동
15. 로그아웃 후 보호 페이지 접근 → 로그인 페이지로 리다이렉트

## 데이터 모델

커스텀 User 모델 (AbstractUser 확장). 위치: `apps/users/models.py`

`AUTH_USER_MODEL = 'users.User'` 설정 필수

| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| email | EmailField | O | unique, 로그인 ID |
| nickname | string | O | 표시 이름 ([[next-episode-ui]] 카드에서 사용) |
| wallet_address | string | X | 코인 수령 지갑 주소 ([[revenue]] 참조) |
| point_balance | int | O | 포인트 잔액, default=0 ([[point-system]] 참조) |
| is_active | BooleanField | O | default=True |
| created_at | DateTimeField | O | auto_now_add |

### 핑거프린트 관련 모델 ([[copy-protection]] 참조)

#### FingerprintLog
| 필드 | 타입 | 설명 |
|------|------|------|
| user | User (nullable) | 로그인 유저 |
| fingerprint | string(64) | 브라우저 핑거프린트 |
| created_at | datetime | 기록 시점 |

#### FingerprintBlacklist
| 필드 | 타입 | 설명 |
|------|------|------|
| fingerprint | string(64) | 차단된 핑거프린트 (unique) |
| reason | text | 차단 사유 |
| created_at | datetime | 차단 시점 |

## 디자인 문서
- [[design-signup-page]] - 회원가입 페이지
- [[design-login-page]] - 로그인 페이지
- [[design-navbar-auth]] - 네비게이션 인증 상태

## 개발 문서
- [[dev-auth-signup]] - 회원가입 서버 로직
- [[dev-auth-login]] - 로그인 서버 로직
- [[dev-auth-logout]] - 로그아웃 서버 로직

## 의존하는 기능
- [[story]] — 작품 생성/연재 시 인증 필요
- [[branch]] — 분기 생성 시 인증 필요
- [[next-episode-ui]] — 읽기 이력 추적 (스포일러 방지)
- [[revenue]] — 지갑 주소 관리
- [[point-system]] — 포인트 잔액 관리

## 비고
- 소셜 로그인은 MVP 범위에서 제외
- 이메일 인증은 MVP 범위에서 제외
