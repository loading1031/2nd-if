# AI 연동 (BYOK)

> 기획 문서

## 상태: 기획 완료

## 개요
사용자가 자신의 API 키(OpenAI, Anthropic, Google) 또는 로컬 Ollama를 연결하여 AI 보조로 소설을 작성하는 기능. 서버는 프록시 역할만 수행하며, AI 호출 비용은 사용자가 부담한다 (BYOK: Bring Your Own Key).

## 요구사항
- 지원 프로바이더: OpenAI, Anthropic, Google Gemini, Ollama (로컬)
- API 키는 Fernet 대칭 암호화로 저장 (`cryptography` 라이브러리)
- 에피소드 작성 시 TipTap 에디터 하단에 접이식 AI 패널 제공
- SSE(Server-Sent Events) 스트리밍으로 AI 응답 실시간 표시
- "에디터에 삽입" / "재생성" / "취소" 버튼 제공
- 프로바이더 연결 테스트 기능 (API 키 유효성 확인)
- 사용자당 분당 20회 요청 제한 (Rate Limiting)

## 사용자 플로우

### AI 설정 - 정상
1. 로그인 유저 → AI 설정 페이지(`/users/settings/ai/`) 이동
2. 프로바이더 추가 폼에서 프로바이더 선택(OpenAI 등) → API 키 입력 → 모델명 입력 → 저장
3. "연결 테스트" 버튼 클릭 → 성공 알림 표시
4. 등록된 프로바이더 테이블에서 목록 확인 (마스킹된 키 표시: `sk-...abc`)

### AI 생성 - 정상
5. 에피소드 작성 페이지 → AI 패널 열기 (접이식)
6. 프로바이더 선택 → 프롬프트 입력 → "생성" 버튼
7. SSE 스트리밍으로 AI 응답이 실시간 표시
8. "에디터에 삽입" 클릭 → TipTap 에디터 커서 위치에 텍스트 삽입
9. "재생성" 클릭 → 동일 프롬프트로 재요청
10. "취소" 클릭 → 진행 중인 SSE 스트림 중단

### AI 설정 - 에러
11. 잘못된 API 키 입력 → 연결 테스트 실패 → "API 키가 유효하지 않습니다." 에러
12. 동일 프로바이더 중복 등록 → 기존 키 업데이트 확인 모달

### AI 생성 - 에러
13. API 호출 실패 (잔액 부족, 쿼터 초과) → "프로바이더에서 오류가 반환되었습니다: {에러 메시지}" 표시
14. 프로바이더 서버 장애 → 30초 타임아웃 후 "응답 시간이 초과되었습니다." 안내
15. 분당 20회 요청 초과 → "요청 제한을 초과했습니다. 잠시 후 다시 시도해주세요." 표시

### 엣지 케이스
16. Ollama 로컬 서버 미실행 상태에서 연결 테스트 → "로컬 서버에 연결할 수 없습니다. Ollama가 실행 중인지 확인해주세요."
17. 프로바이더 미등록 상태에서 AI 생성 시도 → "등록된 AI 프로바이더가 없습니다." + AI 설정 페이지 링크 안내
18. Django `SECRET_KEY` 변경 시 → 기존 암호화 키 복호화 불가 → 프로바이더 재등록 필요 (연결 테스트 실패로 감지)
19. 빈 프롬프트로 생성 시도 → 클라이언트 검증으로 차단
20. SSE 스트리밍 중 네트워크 끊김 → 자동 재연결 없이 에러 표시, 재생성 버튼으로 재시도 유도

## 데이터 모델

### UserAIProvider
위치: `apps/users/models.py`

| 필드 | 타입 | 필수 | 비고 |
|------|------|------|------|
| user | User (FK) | O | 소유자 |
| provider | CharField | O | choices: openai, anthropic, google, ollama |
| display_name | CharField | O | 사용자 지정 별칭 (예: "내 GPT-4") |
| api_key_encrypted | BinaryField | O | Fernet 암호화된 API 키 |
| base_url | URLField | X | Ollama 등 커스텀 엔드포인트 (blank) |
| model_name | CharField | O | 모델명 (예: gpt-4o, claude-sonnet-4-20250514, gemini-2.0-flash) |
| is_active | BooleanField | O | default=True |
| created_at | DateTimeField | O | auto_now_add |
| updated_at | DateTimeField | O | auto_now |

> unique_together: (user, provider) -- 프로바이더당 1개 키만 등록

### 암호화
- `cryptography.fernet.Fernet` 사용
- 암호화 키: Django `SECRET_KEY`에서 파생 (PBKDF2)
- 저장: `BinaryField`에 암호화된 바이트 저장
- 복호화: 뷰에서 AI API 호출 직전에만 복호화, 메모리에 유지하지 않음

## 아키텍처

```
브라우저 (TipTap AI 패널)
  │
  ├── POST /stories/htmx/ai/generate/
  │     body: { provider_id, prompt, episode_id }
  │     Accept: text/event-stream
  │
  ▼
Django (프록시)
  │
  ├── 1. 인증 확인 + Rate Limit 검사
  ├── 2. UserAIProvider에서 암호화된 키 조회 → 복호화
  ├── 3. 프로바이더별 Client 생성 (Factory 패턴)
  ├── 4. AI Provider API에 스트리밍 요청
  └── 5. SSE로 청크 단위 브라우저 전송
        │
        ▼
  AI Provider API (OpenAI / Anthropic / Google / Ollama)
```

### 프로바이더 추상화
```
apps/stories/ai/
├── base.py              ← AIProvider 추상 클래스
├── openai_provider.py   ← OpenAI 구현
├── anthropic_provider.py ← Anthropic 구현
├── google_provider.py   ← Google Gemini 구현
├── ollama_provider.py   ← Ollama 구현
├── factory.py           ← provider 문자열 → 인스턴스 생성
└── prompts.py           ← 시스템 프롬프트 템플릿
```

## 보안 고려사항
- API 키는 평문으로 절대 저장하지 않음 (Fernet 암호화 필수)
- API 키는 응답에 절대 포함하지 않음 (마스킹된 형태만 표시)
- 복호화된 키는 요청 처리 중에만 메모리에 존재
- Rate Limiting으로 과도한 요청 방지
- SSE 엔드포인트는 @login_required

## 의존하는 기능
- [[auth]] - 사용자 인증 (로그인 필수)
- [[story]] - 에피소드 작성 페이지에서 AI 패널 사용

## 디자인 문서
- [[design-ai-settings]] - AI 설정 페이지
- [[design-ai-panel]] - 에피소드 작성 AI 패널

## 개발 문서
- [[dev-ai-byok]] - AI BYOK 서버 로직
