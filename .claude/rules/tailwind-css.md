---
globs: ["*.html", "**/*.html", "*.css", "**/*.css", "input.css"]
---

# Tailwind CSS v4 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## 목차
- [v4 주요 변경점](#v4-주요-변경점)
- [설치 및 설정](#설치-및-설정)
- [CSS 파일 구조](#css-파일-구조)
- [Django 설정](#django-설정)
- [빌드 명령어](#빌드-명령어)
- [클래스 순서 컨벤션](#클래스-순서-컨벤션)
- [커스텀 컴포넌트](#커스텀-컴포넌트)
- [반응형 디자인](#반응형-디자인)
- [다크 모드](#다크-모드)
- [HTMX 인디케이터](#htmx-인디케이터)

## v4 주요 변경점

| v3 | v4 |
|----|-----|
| `npm install tailwindcss` | 독립형 CLI 바이너리 |
| `tailwind.config.js` | CSS 파일에서 `@source` 사용 |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Node.js 필수 | Node.js 불필요 |

## 설치 및 설정

### CLI 바이너리 설치

```bash
# macOS (Apple Silicon)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 tailwindcss
chmod +x tailwindcss

# macOS (Intel)
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-x64
mv tailwindcss-macos-x64 tailwindcss
chmod +x tailwindcss

# Linux
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
mv tailwindcss-linux-x64 tailwindcss
chmod +x tailwindcss
```

## CSS 파일 구조

> **참고**: DaisyUI와 함께 사용하는 경우 [DaisyUI 설정](daisyui.md#설치-및-설정)을 참조하세요.

```css
/* static/css/input.css */

/* 1. Tailwind CSS 가져오기 */
@import "tailwindcss";

/* 2. DaisyUI 가져오기 (선택사항 - 권장) */
/* @plugin "daisyui"; */

/* 3. 템플릿 경로 지정 (v3의 content 역할) */
@source "../../templates/**/*.html";
@source "../../apps/**/templates/**/*.html";

/* 3. 커스텀 테마 (선택사항) */
@theme {
    --color-primary: #4f46e5;
    --color-secondary: #6b7280;
    --color-success: #10b981;
    --color-danger: #ef4444;
    --color-warning: #f59e0b;
}

/* 4. 기본 스타일 */
@layer base {
    body {
        @apply text-gray-900 antialiased;
    }
}

/* 5. 컴포넌트 스타일 */
@layer components {
    .btn {
        @apply inline-flex items-center justify-center px-4 py-2 font-semibold rounded-lg transition-colors;
    }
    .btn-primary {
        @apply bg-indigo-600 text-white hover:bg-indigo-700;
    }
    .btn-secondary {
        @apply bg-gray-200 text-gray-800 hover:bg-gray-300;
    }
    .btn-danger {
        @apply bg-red-600 text-white hover:bg-red-700;
    }
    .input-field {
        @apply block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500;
    }
    .card {
        @apply bg-white rounded-lg shadow-md p-6;
    }
}

/* 6. HTMX 인디케이터 */
.htmx-indicator {
    display: none;
}
.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator {
    display: inline-block;
}
```

## Django 설정

### settings/base.py

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 베이스 템플릿

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My App{% endblock %}</title>

    {% load static %}
    <link rel="stylesheet" href="{% static 'css/output.css' %}">
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>

    {% block extra_head %}{% endblock %}
</head>
<body class="min-h-screen bg-gray-50">
    {% block content %}{% endblock %}
    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

## 빌드 명령어

### 직접 실행

```bash
# 개발 모드 (watch)
./tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch

# 프로덕션 빌드 (minified)
./tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
```

### Django management command

```bash
# 개발 모드
python manage.py tailwind
python manage.py tailwind watch

# 프로덕션 빌드
python manage.py tailwind build
```

## 클래스 순서 컨벤션

Tailwind CSS 클래스는 다음 순서로 작성:

1. **Layout** (display, position, flex, grid)
2. **Sizing** (width, height, max-width, min-height)
3. **Spacing** (margin, padding)
4. **Typography** (font-size, font-weight, text-align, color)
5. **Backgrounds & Borders** (background-color, border)
6. **Effects** (shadow, opacity, transform, transition)
7. **Interactive** (hover, focus, active, disabled)

```html
<!-- Good: 논리적 순서 -->
<button class="flex items-center gap-2 px-4 py-2 text-white font-semibold bg-blue-500 rounded-lg shadow hover:bg-blue-600 transition-colors">
    Click me
</button>

<!-- Bad: 무작위 순서 -->
<button class="hover:bg-blue-600 text-white bg-blue-500 px-4 font-semibold py-2 flex rounded-lg items-center shadow gap-2 transition-colors">
    Click me
</button>
```

## 커스텀 컴포넌트

> **권장**: 커스텀 컴포넌트 대신 [DaisyUI](daisyui.md)를 사용하세요.
> DaisyUI는 `btn`, `card`, `input` 등 시맨틱한 클래스를 제공하여 가독성을 높여줍니다.

### 버튼 컴포넌트 (DaisyUI 미사용 시)

```html
<!-- templates/components/button.html -->
<button
    type="{{ type|default:'button' }}"
    class="{% if size == 'sm' %}px-3 py-1.5 text-sm{% elif size == 'lg' %}px-6 py-3 text-lg{% else %}px-4 py-2{% endif %}
           {% if variant == 'primary' %}bg-indigo-600 hover:bg-indigo-700 text-white
           {% elif variant == 'secondary' %}bg-gray-200 hover:bg-gray-300 text-gray-800
           {% elif variant == 'danger' %}bg-red-600 hover:bg-red-700 text-white
           {% else %}bg-gray-100 hover:bg-gray-200 text-gray-900{% endif %}
           font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed
           {{ class }}"
    {{ attrs }}>
    {{ text }}
</button>

<!-- 사용 예 -->
{% include "components/button.html" with variant="primary" size="md" text="Submit" %}
```

### 카드 컴포넌트

```html
<!-- templates/components/card.html -->
<div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow {{ class }}">
    {% if title %}
        <div class="px-6 py-4 border-b border-gray-200">
            <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
        </div>
    {% endif %}
    <div class="p-6">
        {{ content }}
    </div>
    {% if footer %}
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 rounded-b-lg">
            {{ footer }}
        </div>
    {% endif %}
</div>
```

## 반응형 디자인

```html
<!-- 모바일 우선 접근 -->
<div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <!-- 그리드 아이템 -->
</div>

<!-- 숨김/표시 제어 -->
<div class="hidden md:block">Desktop content</div>
<div class="block md:hidden">Mobile content</div>
```

### 브레이크포인트

| 접두사 | 최소 너비 |
|-------|---------|
| `sm` | 640px |
| `md` | 768px |
| `lg` | 1024px |
| `xl` | 1280px |
| `2xl` | 1536px |

## 다크 모드

v4에서는 CSS 변수를 통해 다크 모드를 설정합니다.

```css
/* static/css/input.css */
@import "tailwindcss";

@theme {
    /* 라이트 모드 기본값 */
    --color-background: #ffffff;
    --color-foreground: #111827;
}

@media (prefers-color-scheme: dark) {
    @theme {
        --color-background: #111827;
        --color-foreground: #f9fafb;
    }
}
```

```html
<!-- 다크 모드 대응 -->
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
    Content
</div>
```

## HTMX 인디케이터

HTMX 요청 중 로딩 상태를 표시하는 스타일:

```css
/* static/css/input.css에 포함됨 */
.htmx-indicator {
    display: none;
}
.htmx-request .htmx-indicator,
.htmx-request.htmx-indicator {
    display: inline-block;
}
```

```html
<!-- 사용 예 -->
<button hx-post="/api/action/" hx-indicator="#spinner">
    <span id="spinner" class="htmx-indicator mr-2">
        <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    </span>
    Submit
</button>
```

## 주요 주의사항

1. **Node.js 불필요**: v4는 독립형 CLI 사용
2. **동적 클래스 주의**: 전체 클래스명을 템플릿에 명시해야 함
3. **클래스 순서**: 일관된 순서로 작성
4. **반응형**: 모바일 우선 접근 방식
5. **.gitignore**: `tailwindcss` 바이너리와 `output.css`는 제외 권장

## 관련 리소스

- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [Tailwind CSS v4 Release Notes](https://tailwindcss.com/blog)
- [DaisyUI 컨벤션](daisyui.md) - 컴포넌트 클래스로 가독성 향상
