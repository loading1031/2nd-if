# CS 상담 채팅

> 기획 문서

## 상태: 기획 완료

## 개요

관리자 1:1 고객 상담 채팅. Django DB 기반 실시간 메시징으로 관리자가 직접 사용자 문의에 답변한다.

## 요구사항

### 핵심
- 로그인한 사용자만 이용 가능
- 관리자(is_staff)가 직접 답변
- SSE(Server-Sent Events)로 실시간 메시지 수신
- 대화 기록 DB 저장 (Django ORM)
- 대화방 상태 관리 (open / resolved / closed)

### 확장성
- 향후: 미답변 알림 이메일
- 향후: FAQ 자동응답 봇 추가 (별도 LLM 연동 시)

## 아키텍처

```
[브라우저]                [Django]              [DB]
 채팅 UI (DaisyUI)  →  POST /cs/send/    →  ChatMessage 저장
 SSE EventSource   ←  GET /cs/stream/   ←  새 메시지 폴링(2초)
                       
[관리자 브라우저]         [Django]
 관리자 채팅 UI    →  POST /cs/admin/{id}/send/
 SSE EventSource  ←  GET /cs/admin/{id}/stream/
```

## 데이터 모델

### ChatRoom

| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| id | AutoField | O | PK |
| user | FK(User, unique) | O | 사용자당 1개 |
| status | CharField | O | open / resolved / closed (기본: open) |
| last_message_at | DateTimeField | X | 정렬용 |
| created_at | DateTimeField | O | 자동 |
| updated_at | DateTimeField | O | 자동 |

### ChatMessage

| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| id | AutoField | O | PK |
| room | FK(ChatRoom) | O | related_name='messages' |
| sender | FK(User) | X | null=시스템 메시지 |
| is_admin | BooleanField | O | 기본: False |
| content | TextField | O | |
| is_read | BooleanField | O | 기본: False |
| created_at | DateTimeField | O | 자동 |

## 사용자 플로우

### 정상 - 사용자 메시지 전송
1. 로그인된 사용자 → `/cs/` 접속
2. ChatRoom 자동 생성 (없으면) 또는 기존 방 로드
3. 기존 메시지 목록 표시
4. 메시지 입력 → 전송 (HTMX POST)
5. ChatMessage DB 저장 → HTML fragment 반환
6. SSE로 관리자 답변 실시간 수신

### 정상 - 관리자 답변
1. 관리자 → `/cs/admin/` 접속 (staff only)
2. 미답변 대화방 목록 확인 (미읽음 배지)
3. 대화방 선택 → 메시지 이력 확인
4. 답변 입력 → 전송
5. 사용자 측 SSE로 답변 실시간 표시
6. 대화방 상태 변경 가능 (open → resolved → closed)

### 에러 - 미로그인
1. 비로그인 사용자 → `/cs/` 접속 → 로그인 페이지 리다이렉트

### 에러 - SSE 연결 끊김
1. 네트워크 끊김 → EventSource 자동 재연결 (브라우저 기본)
2. 재연결 시 last_id 기반으로 놓친 메시지 수신

### 에러 - 서버 장애
1. POST 전송 실패 → "연결 오류가 발생했습니다. 다시 시도해주세요." 표시

### 엣지 - 빈 메시지
1. 빈 입력 전송 시도 → 클라이언트 required 속성으로 차단

### 엣지 - 관리자 부재
1. 사용자 메시지 전송 → 관리자 미응답 → 자동 안내 없음 (향후: 미답변 알림 이메일)

### 엣지 - 동시 메시지
1. 사용자와 관리자가 동시에 메시지 전송 → 각각 DB 저장, SSE로 양쪽에 전달 (순서: created_at 기준)

## 디자인 문서
- [[design-cs-chat-page]] - CS 채팅 페이지 UI

## 관련 기능
- [[cs-faq]] — FAQ 페이지 (해결 안 되면 1:1 채팅으로 연결)

## 의존하는 기능
- [[auth]] — 로그인 필수
