# CS 상담 채팅 서버 로직

> 개발 문서

## 상태: 구현 이력 있음 (현재 동작 재검증 전)

과거 미구현 표시는 구현 커밋과 불일치해 정정했다. [구현 이력 이슈 #10](https://github.com/loading1031/2nd-if/issues/10)과 커밋 `0862dd8`를 참고한다. 현재 기능 테스트·배포를 다시 확인한 상태는 아니다.

## 디자인
- [[design-cs-chat-page]] - CS 채팅 페이지 디자인

## 기획
- [[cs-chat]] - CS 상담 채팅 기획

## 구현 위치

### 모델
- `apps/core/models.py` → `ChatRoom`, `ChatMessage`

### 사용자 뷰
- `apps/core/views/async_views.py` → `cs_chat()`, `cs_chat_send()`, `cs_chat_stream()`

### 관리자 뷰
- `apps/core/views/admin_views.py` → `cs_admin_list()`, `cs_admin_room()`, `cs_admin_send()`, `cs_admin_stream()`, `cs_admin_status()`

### 템플릿
- `apps/core/templates/core/pages/cs_chat.html` (사용자)
- `apps/core/templates/core/pages/cs_admin_list.html` (관리자 목록)
- `apps/core/templates/core/pages/cs_admin_room.html` (관리자 채팅)
- `apps/core/templates/core/partials/chat_message.html` (공용 메시지 fragment)

### URL
- `GET /cs/` — 사용자 채팅 페이지 (로그인 필수)
- `POST /cs/send/` — 사용자 메시지 전송 (HTMX)
- `GET /cs/stream/` — SSE 스트림 (새 메시지 수신)
- `GET /cs/admin/` — 관리자 대화방 목록 (staff only)
- `GET /cs/admin/<room_id>/` — 관리자 채팅방 (staff only)
- `POST /cs/admin/<room_id>/send/` — 관리자 답변 (HTMX)
- `GET /cs/admin/<room_id>/stream/` — 관리자 SSE 스트림
- `PATCH /cs/admin/<room_id>/status/` — 대화방 상태 변경

## 구현 내용

1. **사용자 채팅**: ChatRoom 자동 생성, 메시지 HTMX POST → DB 저장 → HTML fragment 반환
2. **SSE 스트림**: StreamingHttpResponse, 2초 간격 폴링, last_id 기반 새 메시지 전달
3. **관리자 목록**: 미읽음 카운트, last_message_at 정렬, 상태 필터
4. **관리자 채팅**: 사용자와 동일 패턴 + 상태 변경 기능

## 선행 작업
- [[dev-auth-login]] — 로그인 필수
