# 작품 상세 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[story]] - 작품/에피소드 시스템

## 패턴 라이브러리
- `/pattern-library/` → pages → work_detail

## 프로덕션 템플릿
- `apps/stories/templates/stories/pages/work_detail.html`
- `apps/stories/templates/stories/partials/episode_list.html`

## 레이아웃
작품 상세 페이지는 단일 작품의 정보와 에피소드 목록을 보여주는 메인 페이지이다.

상단에 작품 헤더 카드가 위치하며, 제목/작가/연재 상태 배지/작품 소개/라이선스/통계(총 조회수, 분기 수, 평균 별점)를 표시한다.

헤더 아래에 탭 네비게이션이 있으며, "에피소드 목록"과 "분기 트리" 두 탭으로 구성된다. 분기 트리 탭은 추후 구현 예정이므로 비활성 상태로 표시만 한다.

에피소드 목록은 세로 리스트 형태로, 각 행은 `episode_row` 컴포넌트를 사용한다. 원작 에피소드와 분기 에피소드가 같은 리스트에 섞여 표시되며, 배지 색상(원작: primary, 분기: accent)으로 구분한다. 유료 에피소드는 별도 warning 배지로 가격을 표시한다.

## 사용 컴포넌트
- `components/episode_row.html` - 에피소드 행 (번호, 제목, 작가, 조회수, 별점, 원작/분기 배지, 유료 배지)

## 개발
- [[dev-story-work-crud]] - 작품 CRUD 서버 로직
