---
globs: ["*.html", "**/*.html", "*.css", "**/*.css", "input.css"]
---

# DaisyUI 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## 목차
- [DaisyUI 소개](#daisyui-소개)
- [설치 및 설정](#설치-및-설정)
- [클래스 사용 원칙](#클래스-사용-원칙)
- [주요 컴포넌트](#주요-컴포넌트)
- [폼 컴포넌트](#폼-컴포넌트)
- [테마 설정](#테마-설정)
- [HTMX 통합](#htmx-통합)
- [DaisyUI vs 순수 Tailwind 비교](#daisyui-vs-순수-tailwind-비교)

## DaisyUI 소개

DaisyUI는 Tailwind CSS 위에 구축된 컴포넌트 라이브러리입니다.

**장점:**
- 시맨틱한 클래스명으로 가독성 향상
- 긴 Tailwind 유틸리티 클래스 조합 대신 간결한 클래스 사용
- 테마 시스템 내장
- Tailwind와 100% 호환

## 설치 및 설정

### npm으로 설치

```bash
npm install daisyui@latest
```

### CSS 파일 구조 (Tailwind v4 + DaisyUI)

```css
/* static/css/input.css */

/* 1. Tailwind CSS 가져오기 */
@import "tailwindcss";

/* 2. DaisyUI 가져오기 */
@plugin "daisyui";

/* 3. 템플릿 경로 지정 */
@source "../../templates/**/*.html";
@source "../../apps/**/templates/**/*.html";

/* 4. DaisyUI 테마 설정 */
@plugin "daisyui" {
    themes: light, dark, corporate;
    darkTheme: dark;
}

/* 5. HTMX 인디케이터 */
.htmx-indicator {
    display: none;
}
.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator {
    display: inline-block;
}
```

## 클래스 사용 원칙

### 우선순위

1. **DaisyUI 컴포넌트 클래스 우선** - 버튼, 카드, 폼 등
2. **Tailwind 유틸리티로 미세 조정** - 간격, 크기 등 세부 조정만

### 원칙

```html
<!-- Good: DaisyUI 컴포넌트 + 최소한의 Tailwind -->
<button class="btn btn-primary">Submit</button>
<div class="card bg-base-100 shadow-xl">...</div>
<input class="input input-bordered w-full" />

<!-- Bad: 긴 Tailwind 유틸리티 조합 -->
<button class="inline-flex items-center justify-center px-4 py-2 font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-colors">
    Submit
</button>
```

## 주요 컴포넌트

### 버튼 (Button)

```html
<!-- 기본 버튼 -->
<button class="btn">Default</button>
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-accent">Accent</button>
<button class="btn btn-info">Info</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-warning">Warning</button>
<button class="btn btn-error">Error</button>

<!-- 크기 -->
<button class="btn btn-xs">Tiny</button>
<button class="btn btn-sm">Small</button>
<button class="btn btn-md">Normal</button>
<button class="btn btn-lg">Large</button>

<!-- 변형 -->
<button class="btn btn-outline btn-primary">Outline</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-link">Link</button>

<!-- 상태 -->
<button class="btn btn-primary loading">Loading</button>
<button class="btn btn-disabled">Disabled</button>
```

### 카드 (Card)

```html
<div class="card bg-base-100 shadow-xl">
    <figure>
        <img src="image.jpg" alt="Card image" />
    </figure>
    <div class="card-body">
        <h2 class="card-title">Card Title</h2>
        <p>Card description goes here.</p>
        <div class="card-actions justify-end">
            <button class="btn btn-primary">Action</button>
        </div>
    </div>
</div>

<!-- 컴팩트 카드 -->
<div class="card card-compact bg-base-100 shadow-xl">
    <div class="card-body">
        <h2 class="card-title">Compact Card</h2>
        <p>Less padding</p>
    </div>
</div>
```

### 모달 (Modal)

```html
<!-- 모달 트리거 -->
<button class="btn" onclick="my_modal.showModal()">Open Modal</button>

<!-- 모달 -->
<dialog id="my_modal" class="modal">
    <div class="modal-box">
        <h3 class="font-bold text-lg">Modal Title</h3>
        <p class="py-4">Modal content goes here.</p>
        <div class="modal-action">
            <form method="dialog">
                <button class="btn">Close</button>
            </form>
        </div>
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
```

### 알림 (Alert)

```html
<div class="alert">
    <span>Default alert message</span>
</div>
<div class="alert alert-info">
    <span>Info message</span>
</div>
<div class="alert alert-success">
    <span>Success message</span>
</div>
<div class="alert alert-warning">
    <span>Warning message</span>
</div>
<div class="alert alert-error">
    <span>Error message</span>
</div>
```

### 배지 (Badge)

```html
<span class="badge">Default</span>
<span class="badge badge-primary">Primary</span>
<span class="badge badge-secondary">Secondary</span>
<span class="badge badge-outline">Outline</span>
<span class="badge badge-lg">Large</span>
<span class="badge badge-sm">Small</span>
```

### 드롭다운 (Dropdown)

```html
<div class="dropdown">
    <div tabindex="0" role="button" class="btn m-1">Click</div>
    <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-10 w-52 p-2 shadow">
        <li><a>Item 1</a></li>
        <li><a>Item 2</a></li>
    </ul>
</div>
```

### 탭 (Tabs)

```html
<div role="tablist" class="tabs tabs-boxed">
    <a role="tab" class="tab">Tab 1</a>
    <a role="tab" class="tab tab-active">Tab 2</a>
    <a role="tab" class="tab">Tab 3</a>
</div>

<!-- 테두리 스타일 -->
<div role="tablist" class="tabs tabs-bordered">
    <a role="tab" class="tab">Tab 1</a>
    <a role="tab" class="tab tab-active">Tab 2</a>
</div>
```

### 네비게이션 (Navbar)

```html
<div class="navbar bg-base-100">
    <div class="flex-1">
        <a class="btn btn-ghost text-xl">Logo</a>
    </div>
    <div class="flex-none">
        <ul class="menu menu-horizontal px-1">
            <li><a>Link 1</a></li>
            <li><a>Link 2</a></li>
        </ul>
    </div>
</div>
```

## 폼 컴포넌트

### 텍스트 입력 (Input)

```html
<!-- 기본 -->
<input type="text" placeholder="Type here" class="input input-bordered w-full max-w-xs" />

<!-- 크기 -->
<input type="text" class="input input-bordered input-xs" />
<input type="text" class="input input-bordered input-sm" />
<input type="text" class="input input-bordered input-md" />
<input type="text" class="input input-bordered input-lg" />

<!-- 색상 -->
<input type="text" class="input input-bordered input-primary" />
<input type="text" class="input input-bordered input-error" />

<!-- 라벨과 함께 -->
<label class="form-control w-full max-w-xs">
    <div class="label">
        <span class="label-text">Email</span>
    </div>
    <input type="email" placeholder="email@example.com" class="input input-bordered w-full" />
    <div class="label">
        <span class="label-text-alt text-error">Error message</span>
    </div>
</label>
```

### 텍스트영역 (Textarea)

```html
<textarea class="textarea textarea-bordered w-full" placeholder="Bio"></textarea>
```

### 선택 (Select)

```html
<select class="select select-bordered w-full max-w-xs">
    <option disabled selected>Pick one</option>
    <option>Option 1</option>
    <option>Option 2</option>
</select>
```

### 체크박스 (Checkbox)

```html
<label class="label cursor-pointer">
    <span class="label-text">Remember me</span>
    <input type="checkbox" class="checkbox checkbox-primary" />
</label>
```

### 토글 (Toggle)

```html
<input type="checkbox" class="toggle toggle-primary" />
```

### 라디오 (Radio)

```html
<label class="label cursor-pointer">
    <span class="label-text">Option A</span>
    <input type="radio" name="radio-1" class="radio radio-primary" />
</label>
```

### 파일 입력 (File Input)

```html
<input type="file" class="file-input file-input-bordered w-full max-w-xs" />
```

### 폼 그룹 예시

```html
<form class="space-y-4">
    <label class="form-control w-full">
        <div class="label">
            <span class="label-text">Title</span>
        </div>
        <input type="text" name="title" class="input input-bordered w-full" required />
    </label>

    <label class="form-control w-full">
        <div class="label">
            <span class="label-text">Category</span>
        </div>
        <select name="category" class="select select-bordered w-full">
            <option disabled selected>Select category</option>
            <option value="tech">Technology</option>
            <option value="life">Lifestyle</option>
        </select>
    </label>

    <label class="form-control w-full">
        <div class="label">
            <span class="label-text">Description</span>
        </div>
        <textarea name="description" class="textarea textarea-bordered w-full" rows="4"></textarea>
    </label>

    <div class="flex justify-end gap-2">
        <button type="button" class="btn btn-ghost">Cancel</button>
        <button type="submit" class="btn btn-primary">Submit</button>
    </div>
</form>
```

## 테마 설정

### 내장 테마 목록

- light, dark, cupcake, bumblebee, emerald, corporate
- synthwave, retro, cyberpunk, valentine, halloween
- garden, forest, aqua, lofi, pastel, fantasy
- wireframe, black, luxury, dracula, cmyk, autumn
- business, acid, lemonade, night, coffee, winter
- dim, nord, sunset

### 테마 적용

```html
<!-- HTML 태그에 data-theme 속성 -->
<html data-theme="corporate">

<!-- 또는 특정 요소에만 -->
<div data-theme="dark" class="bg-base-100 p-4">
    Dark theme section
</div>
```

### 테마 토글 (JavaScript)

```html
<label class="swap swap-rotate">
    <input type="checkbox" class="theme-controller" value="dark" />
    <svg class="swap-on h-6 w-6" fill="currentColor" viewBox="0 0 24 24"><!-- sun icon --></svg>
    <svg class="swap-off h-6 w-6" fill="currentColor" viewBox="0 0 24 24"><!-- moon icon --></svg>
</label>
```

### 커스텀 테마 정의

```css
/* input.css */
@plugin "daisyui" {
    themes: light, dark, {
        mytheme: {
            "primary": "#4f46e5",
            "secondary": "#6b7280",
            "accent": "#10b981",
            "neutral": "#1f2937",
            "base-100": "#ffffff",
            "info": "#3b82f6",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "error": "#ef4444",
        }
    };
}
```

## HTMX 통합

### HTMX + DaisyUI 버튼

```html
<button
    class="btn btn-primary"
    hx-post="{% url 'app:create_item' %}"
    hx-target="#item-list"
    hx-swap="beforeend"
    hx-indicator="#loading">
    <span id="loading" class="loading loading-spinner htmx-indicator"></span>
    Create Item
</button>
```

### HTMX 로딩 인디케이터 (DaisyUI 스타일)

```html
<!-- 스피너 -->
<span class="loading loading-spinner loading-md htmx-indicator"></span>

<!-- 점 -->
<span class="loading loading-dots loading-md htmx-indicator"></span>

<!-- 링 -->
<span class="loading loading-ring loading-md htmx-indicator"></span>

<!-- 볼 -->
<span class="loading loading-ball loading-md htmx-indicator"></span>

<!-- 바 -->
<span class="loading loading-bars loading-md htmx-indicator"></span>
```

### HTMX 폼 with DaisyUI

```html
<form
    hx-post="{% url 'app:htmx_item_create' %}"
    hx-target="#item-list"
    hx-swap="beforeend"
    hx-indicator="#form-loading"
    class="space-y-4">
    {% csrf_token %}

    <label class="form-control w-full">
        <div class="label">
            <span class="label-text">Title</span>
        </div>
        <input type="text" name="title" class="input input-bordered w-full" required />
    </label>

    <div class="flex justify-end gap-2">
        <button type="button" class="btn btn-ghost" onclick="this.closest('dialog').close()">
            Cancel
        </button>
        <button type="submit" class="btn btn-primary">
            <span id="form-loading" class="loading loading-spinner htmx-indicator"></span>
            Submit
        </button>
    </div>
</form>
```

### HTMX 모달 with DaisyUI

```html
<!-- 모달 트리거 -->
<button
    class="btn btn-primary"
    hx-get="{% url 'app:htmx_item_form' %}"
    hx-target="#modal-container"
    hx-swap="innerHTML"
    onclick="item_modal.showModal()">
    New Item
</button>

<!-- 모달 -->
<dialog id="item_modal" class="modal">
    <div id="modal-container" class="modal-box">
        <!-- HTMX로 로드될 폼 -->
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>
```

### 에러/성공 알림

```html
<!-- templates/partials/alert_error.html -->
<div class="alert alert-error">
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span>{{ error_message }}</span>
</div>

<!-- templates/partials/alert_success.html -->
<div class="alert alert-success">
    <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
    <span>{{ success_message }}</span>
</div>
```

## DaisyUI vs 순수 Tailwind 비교

### 버튼

```html
<!-- DaisyUI -->
<button class="btn btn-primary">Submit</button>

<!-- 순수 Tailwind -->
<button class="inline-flex items-center justify-center px-4 py-2 font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors">
    Submit
</button>
```

### 입력 필드

```html
<!-- DaisyUI -->
<input type="text" class="input input-bordered w-full" />

<!-- 순수 Tailwind -->
<input type="text" class="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors" />
```

### 카드

```html
<!-- DaisyUI -->
<div class="card bg-base-100 shadow-xl">
    <div class="card-body">
        <h2 class="card-title">Title</h2>
        <p>Content</p>
    </div>
</div>

<!-- 순수 Tailwind -->
<div class="bg-white rounded-lg shadow-xl overflow-hidden">
    <div class="p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-2">Title</h2>
        <p class="text-gray-600">Content</p>
    </div>
</div>
```

### 알림

```html
<!-- DaisyUI -->
<div class="alert alert-error">
    <span>Error message</span>
</div>

<!-- 순수 Tailwind -->
<div class="flex items-center gap-3 p-4 bg-red-50 border-l-4 border-red-500 text-red-800 rounded-r-lg">
    <svg class="w-6 h-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">...</svg>
    <span>Error message</span>
</div>
```

## 주요 주의사항

1. **DaisyUI 우선**: UI 컴포넌트는 DaisyUI 클래스를 먼저 사용
2. **Tailwind 보조**: 간격, 크기 등 미세 조정에만 Tailwind 유틸리티 사용
3. **테마 일관성**: 프로젝트 전체에서 동일한 테마 사용
4. **색상 변수**: `bg-primary`, `text-secondary` 등 시맨틱 색상 클래스 사용
5. **베이스 색상**: 배경에는 `bg-base-100`, `bg-base-200` 등 사용

## 관련 리소스

- [DaisyUI Documentation](https://daisyui.com/)
- [DaisyUI Components](https://daisyui.com/components/)
- [DaisyUI Themes](https://daisyui.com/docs/themes/)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
