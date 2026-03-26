# 분기 생성 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-branch-create]] - 분기 생성 페이지

## 기획
- [[branch]] - 분기 시스템
- [[license]] - 분기 허용 여부 결정

## 구현 위치
- 그래프: `apps/stories/graph.py` → EpisodeNode, NextRel
- 페이지 뷰: `apps/stories/views/sync_views.py` → `branch_create()`
- HTMX 뷰: `apps/stories/views/async_views.py` → `htmx_branch_create()`
- URL:
  - `GET /stories/<work_pk>/episodes/<episode_number>/branch/` — 분기 생성 페이지 (로그인 필수)
  - `POST /stories/htmx/<work_pk>/episodes/<episode_number>/branch/` — HTMX 분기 생성

## 구현 내용
1. 분기 가능 여부 검증:
   - 라이선스가 `no_branch`이면 403
   - episode_number > 최신화 - 20이면 403 (20화 제한)
2. 폼 검증 → 새 Episode 생성 (episode_number = 최신 + 1)
3. Neo4j: 원점 노드에서 분기 노드로 NEXT(is_original=False) + BRANCHES_FROM 관계 생성
4. 읽기 페이지로 HX-Redirect

## 선행 작업
- [[dev-story-episode-crud]] — 원점 에피소드 존재 필요
- Neo4j 연결 설정
