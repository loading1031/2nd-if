# 에피소드 리더 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[story]] - 작품/에피소드 시스템
- [[branch]] - 분기 시스템
- [[next-episode-ui]] - 다음 화 선택 UI 및 가중치 정렬

## 패턴 라이브러리
- `/pattern-library/` → pages → episode_reader

## 프로덕션 템플릿
- `apps/stories/templates/stories/pages/episode_read.html`
- `apps/stories/templates/stories/partials/episode_content.html`
- `apps/stories/templates/stories/partials/next_episodes.html`
- `apps/stories/templates/stories/partials/rating_result.html`

## 레이아웃
상단부터 순서대로:
1. **Breadcrumb**: 작품명 > 에피소드 N화
2. **에피소드 헤더**: [원작]/[분기] 배지 + 화 번호, 제목, 작성자, 날짜
3. **본문 영역**: TipTap HTML 렌더링 (`prose` 스타일)
4. **에피소드 푸터**: 별점 평가 (interactive) + 조회수/평균 별점 통계
5. **구분선**
6. **다음 화 선택** (핵심 기능):
   - 섹션 제목 "다음 화"
   - 원작 다음 화 카드 (항상 최상단, primary 테두리 강조)
   - 분기 에피소드 카드들 (engagement_score 내림차순)
   - "+ 여기서 새 분기 만들기" 버튼 (분기 가능 조건 충족 시)
7. **이전 화/목록 내비게이션**

최대 너비 `max-w-3xl`, 모바일 반응형 대응.

## 사용 컴포넌트
- `components/star_rating.html` - 별점 평가 (interactive + readonly)
- `components/next_episode_card.html` - 다음 화 카드 (원작/분기)

## 개발
- [[dev-story-episode-crud]] - 에피소드 CRUD 서버 로직
- [[dev-story-rating]] - 별점 평가 서버 로직
- [[dev-story-next-episodes]] - 다음 화 목록 서버 로직
