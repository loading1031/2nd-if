# AI 설정 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[ai-byok]] - AI 연동 (BYOK) 기획

## 패턴 라이브러리
- `/pattern-library/` → pages → ai_settings (추후 추가)

## 프로덕션 템플릿
- `apps/users/templates/users/pages/ai_settings.html`
- `apps/users/templates/users/partials/ai_provider_row.html`
- `apps/users/templates/users/partials/ai_provider_form.html`
- `apps/users/templates/users/partials/ai_test_result.html`

## 레이아웃

페이지 URL: `/users/settings/ai/`

### 구조
1. **페이지 제목**: "AI 프로바이더 설정"
2. **등록된 프로바이더 테이블** (DaisyUI table)
   - 컬럼: 프로바이더, 별칭, 모델명, API 키 (마스킹), 상태, 액션
   - API 키 표시: `sk-...abc` (앞 3자 + ... + 뒤 3자)
   - 액션 버튼: "테스트" (btn-info btn-sm), "삭제" (btn-error btn-sm btn-outline)
   - 빈 상태: "등록된 프로바이더가 없습니다." 안내 문구
3. **프로바이더 추가 폼** (DaisyUI card + form-control)
   - 프로바이더 선택: select (OpenAI / Anthropic / Google Gemini / Ollama)
   - 별칭: input (placeholder: "내 GPT-4")
   - API 키: input type=password (placeholder: "sk-...")
   - 모델명: input (placeholder: "gpt-4o")
   - Base URL: input (placeholder: "http://localhost:11434", Ollama 선택 시 표시)
   - 버튼: "추가" (btn-primary)

### HTMX 동작
- 프로바이더 추가: `hx-post` → 테이블에 새 행 추가 (`beforeend`)
- 프로바이더 삭제: `hx-delete` → 해당 행 제거 (`outerHTML` swap)
- 연결 테스트: `hx-post` → 결과 알림 표시 (alert-success 또는 alert-error)
- 프로바이더 선택 변경: `hx-get` → Base URL 필드 표시/숨김 토글

### 필드

| 필드 | 타입 | placeholder | 검증 |
|------|------|-------------|------|
| provider | select | "프로바이더 선택" | 필수, choices |
| display_name | text | "내 GPT-4" | 필수, max 50자 |
| api_key | password | "sk-..." | 필수 (Ollama 제외) |
| model_name | text | "gpt-4o" | 필수 |
| base_url | url | "http://localhost:11434" | Ollama일 때 필수 |

## 사용 컴포넌트
- DaisyUI: card, table, form-control, input, select, btn, alert, badge
- HTMX: hx-post, hx-delete, hx-target, hx-swap, hx-indicator

## 개발
- [[dev-ai-byok]] - AI BYOK 서버 로직
