# 분기 생성 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[branch]] - 분기 시스템
- [[story]] - 작품/에피소드 시스템
- [[license]] - 라이선스 표시

## 패턴 라이브러리
- `/pattern-library/` → pages → branch_create

## 프로덕션 템플릿
- (추후 구현)

## 레이아웃
- Breadcrumb: 작품명 > 원점 에피소드 > 새 분기
- 분기 원점 정보 카드: 작품명, 화 번호, 작가, 라이선스 배지
- info alert: "이 분기는 {작품명} {N}화에서 시작됩니다"
- 카드 폼: 제목 입력 → EditorJS 본문 영역 → 유료/무료 토글 → 가격 입력
- 액션: 취소 (ghost) / 분기 발행 (primary)

## 사용 컴포넌트
- DaisyUI: card, input, toggle, btn, breadcrumbs, badge, alert, divider

## 개발
- (추후 추가)
