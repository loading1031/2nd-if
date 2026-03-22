# API + AI 연동 아이디어

> 메모 (MVP 이후)

## 개요
사용자가 자신의 AI(ChatGPT, Claude 등)를 연결해서 에피소드/분기를 원격 작성할 수 있도록 REST API + Swagger 문서를 제공하는 기능.

## 구상
- 에피소드 CRUD API 제공 (Swagger/OpenAPI 문서)
- 사용자 인증 토큰(API Key)으로 접근
- 플랫폼은 API만 제공, AI 연결은 사용자 책임

## 검토 필요 사항
- AI 생성 콘텐츠에 [AI 작성] 뱃지 표시 여부
- [[plagiarism]] 표절 검사 동일 적용 여부
- API Rate limit 정책
- 에피소드 내용 조회 API 범위 (유료 에피소드 포함?)
