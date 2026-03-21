# 폰트 선택 UI 디자인

> 디자인 문서

## 상태: 디자인 완료

## 기획
- [[font-system]] - 장르별 글씨체 시스템
- [[story]] - 작품 시스템

## 패턴 라이브러리
- (작품 생성 페이지에 통합)

## 프로덕션 템플릿
- `server/apps/stories/templates/stories/pages/work_create.html`

## 폰트 선택 UI

작품 생성 폼에서 라디오 카드 형태로 폰트 선택:

```
글씨체 선택

[● 기본 (Pretendard)]  샘플 텍스트 미리보기...
[○ 명조 (Noto Serif KR)]  샘플 텍스트 미리보기...
[○ 궁서 (Gowun Batang)]  샘플 텍스트 미리보기...
[○ 고딕 (Noto Sans KR)]  샘플 텍스트 미리보기...
```

각 옵션에 해당 폰트로 렌더링된 샘플 텍스트를 보여줌.

## 에피소드 읽기 적용

`<article>` 태그에 `font-{work.font}` 클래스 적용.
CSS 클래스가 `.prose` 안의 폰트를 오버라이드.

## 사용 컴포넌트
- CSS `.font-default`, `.font-serif`, `.font-classic`, `.font-modern`
- Google Fonts CDN

## 개발
- (Step 5에서 구현)
