# 작품 목록 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[story]] - 작품/에피소드 시스템

## 패턴 라이브러리
- `/pattern-library/` → pages → work_list
- `/pattern-library/` → components → work_card

## 프로덕션 템플릿
- (추후 구현)

## 레이아웃
- 페이지 헤더: 제목 + "새 작품 만들기" 버튼
- 검색바: HTMX 디바운스 검색 (500ms delay)
- 필터 탭: 전체, 연재중, 완결, 인기순 (DaisyUI tabs-bordered)
- 작품 그리드: 반응형 (1열 모바일 / 2열 sm / 3열 md / 4열 lg)
- 페이지네이션: DaisyUI join 버튼 그룹

## 사용 컴포넌트
- `components/work_card.html` - 작품 카드 (title, author, status, description, episode_count, view_count, branch_count, avg_rating)

## 개발
- (추후 추가)
