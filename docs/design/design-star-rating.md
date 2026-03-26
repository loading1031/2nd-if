# 별점 평가 컴포넌트 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[story]] - 에피소드 별점 평균 (avg_rating) 필드
- [[next-episode-ui]] - 카드에 별점 표시, 별점 기반 가중치 필터링

## 패턴 라이브러리
- `/pattern-library/` → components → star_rating

## 프로덕션 템플릿
- `apps/stories/templates/stories/partials/rating_result.html`

## 레이아웃
DaisyUI `rating` 컴포넌트 기반 두 가지 모드:

### Interactive 모드
- 1~5점 전체 별 선택 (`rating-lg`)
- 폼 제출용 radio input (name 파라미터로 구분)
- 에피소드 리더 하단에서 사용

### Readonly 모드
- 0.5점 단위 반별 표시 (`rating-half`, `rating-sm`)
- disabled 상태로 클릭 불가
- 카드, 리스트 등 표시 전용

## 사용 컴포넌트
- `components/star_rating.html`

## 개발
- [[dev-story-rating]] - 별점 평가 서버 로직
