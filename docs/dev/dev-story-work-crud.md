# 작품 CRUD 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-work-list]] - 작품 목록 페이지
- [[design-work-create]] - 작품 생성 페이지
- [[design-work-detail]] - 작품 상세 페이지

## 기획
- [[story]] - 작품/에피소드 시스템
- [[license]] - 콘텐츠 라이선스

## 구현 위치
- 모델: `apps/stories/models.py` → Work
- 폼: `apps/stories/forms.py` → WorkCreateForm
- 페이지 뷰: `apps/stories/views/sync_views.py` → `work_list()`, `work_create()`, `work_detail()`
- HTMX 뷰: `apps/stories/views/async_views.py` → `htmx_work_list()`, `htmx_work_create()`
- URL:
  - `GET /stories/` — 작품 목록 페이지
  - `GET /stories/create/` — 작품 생성 페이지 (로그인 필수)
  - `GET /stories/<pk>/` — 작품 상세 페이지
  - `GET /stories/htmx/works/` — HTMX 작품 목록 (검색/필터)
  - `POST /stories/htmx/works/create/` — HTMX 작품 생성

## 구현 내용
1. 작품 목록: 검색(title__icontains) + 상태 필터 + episode_count annotate
2. 작품 생성: title/description/license/font 폼 검증 → Work 생성 → 상세 페이지로 HX-Redirect
3. 작품 상세: sync_views에서 페이지 렌더링, HTMX로 에피소드 목록 로드

## 선행 작업
- User 모델 (작성자 FK)
