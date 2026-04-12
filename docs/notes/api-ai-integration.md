# API + AI 연동 아이디어

> 메모 (MVP 이후)

## 개요
사용자가 자신의 AI(ChatGPT, Claude 등)를 연결해서 에피소드/분기를 작성할 수 있도록 하는 기능.

## 방향: BYOK (Bring Your Own Key)

기존의 REST API + Swagger 방식에서 **BYOK 방식**으로 전환. 자세한 기획은 [[ai-byok]] 참조.

- 사용자가 자신의 API 키를 등록 (OpenAI, Anthropic, Google Gemini, Ollama)
- 서버가 프록시 역할로 AI API를 호출
- 에피소드 작성 페이지의 AI 패널에서 직접 사용
- SSE 스트리밍으로 실시간 응답

## 검토 필요 사항
- AI 생성 콘텐츠에 [AI 작성] 뱃지 표시 여부
- [[plagiarism]] 표절 검사 동일 적용 여부
- Rate limit 정책: 사용자당 분당 20회 ([[ai-byok]] 참조)
- 에피소드 내용 조회 API 범위 (유료 에피소드 포함?)

## 이전 구상 (참고용)
- ~~에피소드 CRUD API 제공 (Swagger/OpenAPI 문서)~~
- ~~사용자 인증 토큰(API Key)으로 접근~~
- ~~플랫폼은 API만 제공, AI 연결은 사용자 책임~~
→ 사용자 편의를 위해 플랫폼 내 통합 AI 패널로 변경
