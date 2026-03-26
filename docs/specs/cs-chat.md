# CS 상담 채팅

> 기획 문서

## 상태: 기획 완료

## 개요

AI 기반 고객 상담 채팅. Dify Chatflow를 백엔드로 사용하여 FAQ 자동 응답 및 미해결 문의 에스컬레이션을 제공한다.

## 요구사항

### 핵심
- 로그인한 사용자만 이용 가능
- FAQ 기반 자동 응답 (Dify Knowledge Base)
- 실시간 스트리밍 응답 (SSE)
- 대화 맥락 유지 (conversation_id)

### 에스컬레이션
- FAQ에 없는 질문은 "고객센터로 문의" 안내
- 향후: 미해결 문의를 Django DB에 티켓으로 저장
- 향후: 티켓 목록 조회 페이지

### 확장성
- Django 코드 수정 없이 Dify 플로우 노드 추가만으로 기능 확장
- 예: 외부 API 연동 (WMS, ERP 등)은 Dify HTTP Request 노드로 처리

## 사용자 플로우

### 정상 - FAQ 자동 응답
1. 로그인된 사용자 → `/cs/` 접속
2. 인사 메시지 자동 표시
3. 사용자 질문 입력 → 전송
4. Dify가 FAQ에서 유사 답변 검색 → LLM이 답변 생성
5. SSE 스트리밍으로 실시간 답변 표시
6. 추가 질문 시 같은 conversation_id로 맥락 유지

### 정상 - 연속 대화
1. 사용자 첫 질문 → conversation_id 발급
2. 후속 질문 → 같은 conversation_id 전송
3. Dify가 이전 맥락을 참고하여 답변

### 에러 - FAQ에 없는 질문
1. 사용자 질문 → Dify Knowledge 검색 → 유사도 낮음
2. LLM이 "확인 후 답변드리겠습니다. 고객센터로 문의해주세요." 응답
3. 향후: 자동으로 문의 티켓 생성 + 티켓 번호 안내

### 에러 - 미로그인
1. 비로그인 사용자 → `/cs/` 접속 시도
2. 로그인 페이지로 리다이렉트

### 에러 - Dify 서버 장애
1. 사용자 질문 전송 → Dify API 연결 실패
2. "연결 오류가 발생했습니다. 다시 시도해주세요." 표시

### 엣지 - 빈 메시지
1. 빈 입력으로 전송 시도 → 클라이언트에서 차단 (required)

### 엣지 - 긴 메시지
1. 매우 긴 메시지 입력 → Dify API가 처리 (별도 제한 없음)

## 아키텍처

```
[브라우저]                [Django]                 [Dify API]
 채팅 UI (DaisyUI)  →  POST /cs/chat/       →  POST /v1/chat-messages
 fetch + SSE 파싱   ←  StreamingHttpResponse ←  SSE 스트리밍
                        (httpx async)
```

- Django: 인증 + SSE 프록시만 담당
- Dify: Knowledge 검색 + LLM 추론 + 비즈니스 로직
- FAQ 데이터: Dify Knowledge Base에 저장 (cs-faq.md)

## 데이터 모델

### 현재 (MVP)
별도 모델 없음. 대화 기록은 Dify 내부에 저장.

### 향후 (에스컬레이션)
| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| id | AutoField | O | PK |
| user | FK(User) | O | 문의한 사용자 |
| conversation_id | CharField | O | Dify 대화 ID |
| summary | TextField | O | 문의 요약 (LLM 생성) |
| status | CharField | O | open / resolved / closed |
| created_at | DateTimeField | O | 생성일 |

## 디자인 문서
- [[design-cs-chat-page]] - CS 채팅 페이지 UI

## 개발 문서
- [[dev-cs-chat]] - CS 채팅 서버 로직

## 의존하는 기능
- [[auth]] — 로그인 필수
