# 다음 화 목록 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-next-episode-card]] - 다음 화 카드 컴포넌트
- [[design-episode-reader]] - 에피소드 리더 페이지 (다음 화 섹션)

## 기획
- [[next-episode-ui]] - 다음 화 선택 UI 및 가중치 정렬
- [[branch]] - 분기 시스템

## 구현 위치
- 그래프: `apps/stories/graph.py` → `EpisodeNode.get_next_episodes_sorted()`, `increment_visit()`
- HTMX 뷰: `apps/stories/views/async_views.py` → `htmx_next_episodes()`, `htmx_visit_episode()`
- URL:
  - `GET /stories/htmx/<work_pk>/episodes/<episode_number>/next/` — 다음 화 목록
  - `POST /stories/htmx/<work_pk>/episodes/<from_number>/visit/<to_number>/` — 경로 이동

## 구현 내용
1. 다음 화 목록: Neo4j에서 NEXT 관계 조회 → engagement_score 내림차순 정렬 (원작 항상 최상단)
2. Django Episode 정보(author, avg_rating 등) enrichment
3. 분기 가능 여부: 라이선스 != no_branch && 20화 제한 && 로그인 상태
4. visit_count 증가: 별점 3점 이하면 증가 안 함 (저품질 필터)

## 선행 작업
- [[dev-story-branch]] — 분기 데이터가 있어야 다음 화 목록에 표시
