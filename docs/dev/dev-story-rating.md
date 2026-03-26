# 별점 평가 서버 로직

> 개발 문서

## 상태: 구현 완료

## 디자인
- [[design-star-rating]] - 별점 평가 컴포넌트

## 기획
- [[story]] - 에피소드 별점 (avg_rating, rating_count)
- [[next-episode-ui]] - 별점 3점 이하 visit_count 제외

## 구현 위치
- 모델: `apps/stories/models.py` → Rating
- HTMX 뷰: `apps/stories/views/async_views.py` → `htmx_rate_episode()`
- URL: `POST /stories/htmx/<work_pk>/episodes/<episode_number>/rate/`

## 구현 내용
1. score 범위 검증 (1~5, 범위 밖이면 400)
2. Rating upsert (aupdate_or_create) — 같은 유저가 재평가하면 업데이트
3. Episode.avg_rating / rating_count 갱신 (Avg aggregate + acount)
4. 로그인 필수 (@login_required)

## 선행 작업
- [[dev-story-episode-crud]] — Episode 존재해야 별점 가능
