# AI BYOK 서버 로직

> 개발 문서

## 상태: 미구현

## 디자인
- [[design-ai-settings]] - AI 설정 페이지 디자인
- [[design-ai-panel]] - 에피소드 작성 AI 패널 디자인

## 기획
- [[ai-byok]] - AI 연동 (BYOK) 기획

## 구현 위치

### 모델 & 암호화
- 모델: `apps/users/models.py` → `UserAIProvider`
- 암호화: `apps/users/crypto.py` → `encrypt_api_key()`, `decrypt_api_key()`
- 키 파생: Django `SECRET_KEY` → PBKDF2 → Fernet 키

### AI 설정 (users 앱)
- 뷰: `apps/users/views/ai_views.py`
  - `htmx_ai_settings()` — GET: 설정 페이지 렌더링
  - `htmx_ai_provider_create()` — POST: 프로바이더 추가
  - `htmx_ai_provider_delete()` — DELETE: 프로바이더 삭제
  - `htmx_ai_provider_test()` — POST: 연결 테스트
- URL:
  - `GET /users/settings/ai/` → 설정 페이지
  - `POST /users/htmx/ai/providers/create/` → 프로바이더 추가
  - `DELETE /users/htmx/ai/providers/<int:pk>/delete/` → 프로바이더 삭제
  - `POST /users/htmx/ai/providers/<int:pk>/test/` → 연결 테스트

### AI 생성 (stories 앱)
- 프로바이더 추상화: `apps/stories/ai/`
  - `base.py` → `AIProvider` 추상 클래스 (generate_stream 메서드)
  - `openai_provider.py` → OpenAI 구현 (httpx async)
  - `anthropic_provider.py` → Anthropic 구현 (httpx async)
  - `google_provider.py` → Google Gemini 구현 (httpx async)
  - `ollama_provider.py` → Ollama 구현 (httpx async)
  - `factory.py` → provider 문자열로 인스턴스 생성
  - `prompts.py` → 시스템 프롬프트 템플릿 (소설 작성 보조용)
- 뷰: `apps/stories/views/ai_views.py`
  - `htmx_ai_generate()` — POST: SSE 스트리밍 생성 (StreamingHttpResponse)
  - `htmx_ai_providers()` — GET: 사용자의 활성 프로바이더 목록 (select 옵션)
- URL:
  - `POST /stories/htmx/ai/generate/` → AI 생성 (SSE)
  - `GET /stories/htmx/ai/providers/` → 프로바이더 목록 (partial)

### 의존성
- `cryptography` — Fernet 암호화 (pyproject.toml에 추가)
- `httpx` — 비동기 HTTP 클라이언트 (AI Provider API 호출)

## 구현 내용

### 1. UserAIProvider 모델 & 마이그레이션
- `apps/users/models.py`에 모델 추가
- unique_together: (user, provider)
- 마이그레이션 생성 및 적용

### 2. Fernet 암호화 유틸리티
- `apps/users/crypto.py`
- `get_fernet_key()`: SECRET_KEY → PBKDF2 → base64 → Fernet 키
- `encrypt_api_key(plain_key: str) -> bytes`: 평문 → 암호화 바이트
- `decrypt_api_key(encrypted: bytes) -> str`: 암호화 바이트 → 평문

### 3. AI 설정 뷰 (HTMX)
- 프로바이더 CRUD: acreate, adelete
- 연결 테스트: 각 프로바이더 API에 간단한 요청 (models list 등)
- API 키 마스킹: 앞 3자 + "..." + 뒤 3자

### 4. 프로바이더 추상화 (Factory 패턴)
- `AIProvider` ABC: `async def generate_stream(prompt, system_prompt) -> AsyncGenerator[str, None]`
- 각 프로바이더별 API 스펙에 맞는 스트리밍 구현
- httpx AsyncClient로 비동기 스트리밍

### 5. SSE 스트리밍 뷰
- `StreamingHttpResponse(content_type='text/event-stream')`
- async generator로 청크 단위 전송
- Rate Limiting: Django cache 기반 분당 20회 제한
- 타임아웃: 30초

### 6. Rate Limiting
- Django cache framework 활용
- 키: `ai_ratelimit:{user_id}`
- 분당 20회 초과 시 429 응답

## 선행 작업
- User 모델 마이그레이션 완료 ([[dev-auth-signup]])
- `cryptography`, `httpx` 패키지 설치
- Episode 작성 페이지 구현 ([[story]])
