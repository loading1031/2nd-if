# 에피소드 작성 AI 패널 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[ai-byok]] - AI 연동 (BYOK) 기획

## 패턴 라이브러리
- `/pattern-library/` → components → ai_panel (추후 추가)

## 프로덕션 템플릿
- `apps/stories/templates/stories/partials/ai_panel.html`
- `apps/stories/templates/stories/partials/ai_result.html`
- `apps/stories/templates/stories/partials/ai_provider_select.html`

## 레이아웃

에피소드 작성 페이지 하단에 접이식 패널로 배치.

### 구조
1. **접이식 헤더** (DaisyUI collapse + collapse-arrow)
   - 제목: "AI 어시스턴트"
   - 접힌 상태가 기본값
2. **패널 내부**
   - 상단: 프로바이더 선택 (select, HTMX GET으로 사용자 등록 목록 로드)
   - 프롬프트 영역: textarea (placeholder: "이어질 내용을 설명해주세요...")
   - 버튼 바: "생성" (btn-primary) + "취소" (btn-ghost, 생성 중일 때만 표시)
3. **생성 결과 영역**
   - SSE 스트리밍 텍스트가 실시간으로 표시되는 영역
   - 배경: bg-base-200, 모노스페이스 아닌 본문 폰트
   - 스트리밍 중: loading-dots 인디케이터 표시
4. **결과 액션 바** (결과가 있을 때만 표시)
   - "에디터에 삽입" (btn-primary btn-sm)
   - "재생성" (btn-outline btn-sm)

### HTMX / SSE 동작
- 프로바이더 목록 로드: `hx-get="/stories/htmx/ai/providers/"` → select 옵션 채우기
- AI 생성: JavaScript로 `POST /stories/htmx/ai/generate/` → SSE EventSource로 수신
- 취소: EventSource.close() 호출
- 에디터에 삽입: JavaScript로 TipTap `editor.commands.insertContent()` 호출

### 프로바이더 미등록 상태
- 프로바이더 목록이 비어있을 때: alert-warning 표시
- "AI 프로바이더를 먼저 등록해주세요." + 설정 페이지 링크 (btn-link)

## 사용 컴포넌트
- DaisyUI: collapse, textarea, select, btn, alert, loading
- TipTap: editor.commands.insertContent()
- SSE: EventSource API (JavaScript)

## 개발
- [[dev-ai-byok]] - AI BYOK 서버 로직
