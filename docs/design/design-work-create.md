# 작품 생성 페이지 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[story]] - 작품/에피소드 시스템
- [[license]] - 콘텐츠 라이선스

## 패턴 라이브러리
- `/pattern-library/` → pages → work_create
- `/pattern-library/` → components → license_selector

## 프로덕션 템플릿
- `apps/stories/templates/stories/pages/work_create.html`
- `apps/stories/templates/stories/partials/work_create_form.html`

## 레이아웃
- 중앙 정렬 폼 (`max-w-2xl`)
- 작품 제목 입력 (form_field 컴포넌트)
- 작품 소개 텍스트영역 (선택사항)
- 라이선스 선택 (라디오 카드 그룹)
- 라이선스 안내 알림 (alert-info)
- 제출 버튼 (취소/작품 만들기)

## 필드
| 필드 | 타입 | placeholder | 검증 |
|------|------|-------------|------|
| title | text | 작품 제목을 입력하세요 | 필수 |
| description | textarea | 작품에 대한 간단한 소개를 작성하세요 | 선택 |
| license | radio | - | 필수 (기본값: 자유 분기 허용) |

## 사용 컴포넌트
- `components/form_field.html` - 제목 입력
- `components/license_selector.html` - 라이선스 선택 (라디오 카드 그룹)

## 개발
- [[dev-story-work-crud]] - 작품 CRUD 서버 로직
