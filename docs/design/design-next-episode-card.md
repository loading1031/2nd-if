# 다음 화 카드 컴포넌트 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[next-episode-ui]] - 다음 화 선택 UI 및 가중치 정렬
- [[branch]] - 분기 시스템 (원작/분기 구분)

## 패턴 라이브러리
- `/pattern-library/` → components → next_episode_card

## 프로덕션 템플릿
- `apps/stories/templates/stories/partials/next_episodes.html`

## 레이아웃
DaisyUI `card card-compact` 기반 가로형 카드:
- 좌측: [원작]/[분기] 배지 + 에피소드 번호/제목 + 작성자/별점/이동 횟수
- 우측: 화살표 아이콘 (이동 힌트)

### 원작 카드
- `border-2 border-primary`로 시각적 강조
- `badge-primary` 라벨

### 분기 카드
- `border border-base-300` 기본 테두리
- `badge-secondary` 라벨

### 표시 정보
| 항목 | 설명 |
|------|------|
| 라벨 | [원작] 또는 [분기] (badge) |
| 에피소드 번호 | "제N화:" 형식 |
| 제목 | 에피소드 제목 (truncate 처리) |
| 작성자 | "by {닉네임}" |
| 별점 | 별 아이콘 + avg_rating (없으면 미표시) |
| 이동 횟수 | 눈 아이콘 + visit_count |

## 사용 컴포넌트
- `components/next_episode_card.html`

## 개발
- [[dev-story-next-episodes]] - 다음 화 목록 서버 로직
