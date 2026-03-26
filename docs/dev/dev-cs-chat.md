# CS 상담 채팅 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-cs-chat-page]] - CS 채팅 페이지 UI

## 기획
- [[cs-chat]] - CS 상담 채팅

## 구현 위치
- 뷰: `apps/core/views/async_views.py` → `cs_chat()`, `cs_chat_send()`
- 템플릿: `apps/core/templates/core/pages/cs_chat.html`
- URL:
  - `GET /cs/` — 채팅 페이지 (로그인 필수)
  - `POST /cs/chat/` — Dify API 프록시 (SSE 스트리밍)

## 구현 내용
1. 채팅 페이지: 로그인 필수, DaisyUI chat 컴포넌트
2. 메시지 전송: JSON body(query, conversation_id) → Dify Chat API 호출
3. SSE 스트리밍: httpx.AsyncClient로 Dify 응답을 StreamingHttpResponse로 프록시
4. 대화 맥락: conversation_id로 연속 대화 유지

## 환경 변수
- `DIFY_API_URL` — Dify API 엔드포인트
- `DIFY_API_KEY` — Dify API 키

## 선행 작업
- Dify 서버 + Knowledge Base 설정
- [[dev-auth-login]] — 로그인 필수
