# 동적 텍스트 리더 서버/클라이언트 로직

> 개발 문서

## 상태: 미구현

## 디자인
- [[design-dynamic-reader]] - 동적 텍스트 리더 디자인

## 기획
- [[dynamic-reader]] - 동적 텍스트 리더 기획

## 구현 위치

### CSS 애니메이션
- `server/static/css/input.css` — @layer components에 data-fx 애니메이션 추가
  - `[data-fx]` 초기 상태 스타일
  - `[data-fx].fx-active` 활성화 애니메이션
  - `@keyframes` 정의 (shake, fade-in, rush, typewriter, float)
  - `@media (prefers-reduced-motion: reduce)` 폴백

### JavaScript (리더)
- `server/static/js/reader-fx.js` — Intersection Observer + data-fx 파싱
  - `[data-fx]` 요소 수집
  - IntersectionObserver 등록 (threshold: 0.3)
  - 뷰포트 진입 시 `fx-active` 클래스 토글
  - typewriter 효과: 글자 수 기반 동적 duration 계산
  - 1회 재생 후 unobserve

### TipTap 에디터 확장
- `server/static/js/tiptap-editor.js` — /effect 슬래시 메뉴 확장
  - `/effect` 명령어 추가
  - 효과 목록 메뉴 렌더링 (shake, fade-in, rush, typewriter, float)
  - 선택 시 현재 블록에 `data-fx` 속성 부여
  - 기존 효과 교체 지원

### 새니타이징 업데이트
- `apps/stories/forms.py` — nh3 허용 속성에 data-fx, data-delay 추가
  - `EpisodeCreateForm.clean_content()` 내 nh3 설정 수정
  - 허용 속성: 기존 + `data-fx`, `data-delay` (p 태그)

### 번들 빌드
- `package.json` — `build:reader` 스크립트 추가
  - esbuild로 `reader-fx.js` 번들링
  - 에피소드 리더 페이지에서 `<script>` 로드

### 템플릿
- `apps/stories/templates/stories/pages/episode_read.html`
  - reader-fx.js `<script>` 태그 추가 ({% load static %})
  - output.css에 data-fx 스타일 포함 (빌드 시 자동)

## 구현 내용

1. **CSS 애니메이션 정의**: input.css에 5종 효과의 keyframes + 초기/활성 상태 스타일 추가
2. **Intersection Observer**: reader-fx.js에서 `[data-fx]` 요소를 감시, 뷰포트 30% 진입 시 `fx-active` 클래스 추가
3. **TipTap /effect 메뉴**: 슬래시 메뉴에 효과 선택 항목 추가, 선택 시 블록 노드에 data-fx 속성 설정
4. **nh3 허용 속성 추가**: `data-fx`, `data-delay`를 p 태그 허용 속성에 추가
5. **접근성**: `prefers-reduced-motion` 미디어 쿼리로 모든 애니메이션 비활성화 처리
6. **점진적 향상**: JS 비활성화 시 텍스트는 정적으로 표시 (기존과 동일)

## 선행 작업
- [[dev-story-episode-crud]] — 에피소드 CRUD (Episode.content HTML 저장)
