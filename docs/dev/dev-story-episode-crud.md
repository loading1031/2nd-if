# 에피소드 CRUD 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-episode-write]] - 에피소드 작성 페이지
- [[design-episode-reader]] - 에피소드 리더 페이지
- [[design-episode-reader-protection]] - 복사 방지 / 워터마크

## 기획
- [[story]] - 작품/에피소드 시스템
- [[copy-protection]] - 복사 방지 시스템

## 구현 위치
- 모델: `apps/stories/models.py` → Episode
- 폼: `apps/stories/forms.py` → EpisodeCreateForm
- 워터마크: `apps/stories/watermark.py` → `embed_watermark()`
- 페이지 뷰: `apps/stories/views/sync_views.py` → `episode_write()`, `episode_read()`
- HTMX 뷰: `apps/stories/views/async_views.py` → `htmx_episode_list()`, `htmx_episode_create()`, `htmx_episode_read()`
- URL:
  - `GET /stories/<work_pk>/episodes/write/` — 에피소드 작성 페이지 (로그인 필수)
  - `GET /stories/<work_pk>/episodes/<episode_number>/` — 에피소드 읽기 페이지
  - `GET /stories/htmx/<work_pk>/episodes/` — HTMX 에피소드 목록
  - `POST /stories/htmx/<work_pk>/episodes/create/` — HTMX 에피소드 생성
  - `GET /stories/htmx/<work_pk>/episodes/<episode_number>/` — HTMX 본문 로드

## 구현 내용
1. 에피소드 목록: work FK 기준 조회, select_related("author")
2. 에피소드 생성: 폼 검증 → episode_number 자동 채번 → Neo4j 노드 생성 + NEXT 연결 → 읽기 페이지로 HX-Redirect
3. 에피소드 읽기: 조회수 +1, 워터마크 식별자(user.id / session_key) 결정 → embed_watermark로 삽입
4. 워터마크: zero-width 문자로 식별자 인코딩 (로그인: user.id, 비로그인: session_key)

## 선행 작업
- [[dev-story-work-crud]] — Work 존재해야 에피소드 생성 가능
