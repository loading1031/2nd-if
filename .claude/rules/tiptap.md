# TipTap 에디터 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## 개요

TipTap vanilla JS를 소설 작성용 미니멀 에디터로 사용한다.
React 없이 `@tiptap/core`로 직접 초기화.

## 설치 및 빌드

```bash
# 패키지 (package.json에 이미 포함)
npm install @tiptap/core @tiptap/pm @tiptap/starter-kit \
  @tiptap/extension-image @tiptap/extension-placeholder \
  @tiptap/extension-bubble-menu @tiptap/extension-horizontal-rule

# 번들 빌드
npm run build:editor
# → server/static/js/tiptap-bundle.js 생성
```

## 에디터 구성

- **확장**: paragraph, bold, italic, heading(2,3), image, horizontal-rule
- **버블 메뉴**: 텍스트 선택 시 bold/italic 토글
- **슬래시 커맨드**: `/` 입력 시 삽화 삽입, 구분선 메뉴
- **이미지**: 드래그앤드롭, 붙여넣기, 파일 선택 지원
- **출력**: HTML (`editor.getHTML()`)

## 템플릿 사용법

```html
<!-- 에디터 영역 -->
<div id="editor" class="border border-base-300 rounded-lg min-h-[400px] bg-base-100"></div>
<input type="hidden" name="content" id="content-input" />

<!-- 번들 로드 -->
{% load static %}
<script src="{% static 'js/tiptap-bundle.js' %}"></script>
```

`tiptap-bundle.js`가 `#editor`와 `#content-input`을 자동으로 찾아 초기화한다.
폼 제출 시 `editor.getHTML()`이 hidden input에 자동 저장된다.

## 콘텐츠 저장

- 모델: `Episode.content = TextField` (HTML 문자열)
- 새니타이징: `EpisodeCreateForm.clean_content()`에서 `nh3`로 허용 태그만 통과
- 허용 태그: `p, strong, em, br, img, hr, h2, h3, ul, ol, li`
- 허용 속성: `img`의 `src`, `alt`만

## 이미지 업로드

- 엔드포인트: `POST /api/upload-image/`
- 요청: `FormData`에 `image` 파일
- 응답: `{success: 1, file: {url: "..."}}` 또는 `{url: "..."}`
- 검증: 5MB 제한, jpg/png/gif/webp만 허용

## HTMX 통합

```javascript
// htmx:configRequest 이벤트에서 content 동기화
document.body.addEventListener('htmx:configRequest', (evt) => {
    if (form.contains(evt.detail.elt)) {
        contentInput.value = editor.getHTML()
    }
})
```

## 주의사항

1. **XSS 방지**: 서버에서 반드시 `nh3`로 새니타이징
2. **번들 빌드**: `tiptap-editor.js` 수정 후 `npm run build:editor` 필수
3. **output.css**: `.gitignore`에 포함됨, 로컬에서 `tailwind build` 필요
