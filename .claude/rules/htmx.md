---
globs: ["*.html", "**/*.html", "urls.py", "**/urls.py"]
---

# HTMX 컨벤션

> [← 메인으로 돌아가기](main.md)

## 목차
- [HTML 속성 네이밍](#html-속성-네이밍)
- [URL 패턴](#url-패턴)
- [뷰 패턴](#뷰-패턴)
- [템플릿 구조](#템플릿-구조)
- [응답 헤더](#응답-헤더)
- [에러 핸들링](#에러-핸들링)
- [CSRF 보호](#csrf-보호)
- [디바운싱 및 최적화](#디바운싱-및-최적화)
- [네이밍 컨벤션](#네이밍-컨벤션)
- [JavaScript 코드 스타일](#javascript-코드-스타일)

## HTML 속성 네이밍

```html
<!-- HTMX 속성 사용 -->
<button
    class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white font-semibold rounded-lg transition-colors"
    hx-get="/api/items/"
    hx-target="#item-list"
    hx-swap="innerHTML"
    hx-indicator="#loading-spinner">
    Load Items
</button>

<!-- ID 네이밍: kebab-case -->
<div id="item-list" class="space-y-4"></div>
<div id="loading-spinner" class="htmx-indicator">
    <svg class="animate-spin h-5 w-5 text-blue-500" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
</div>

<!-- 로딩 인디케이터 스타일 -->
<style>
    .htmx-indicator {
        @apply hidden;
    }
    .htmx-request .htmx-indicator,
    .htmx-request.htmx-indicator {
        @apply inline-block;
    }
</style>
```

## URL 패턴

```python
# urls.py
from django.urls import path
from .views import async_views

app_name = 'app_name'

urlpatterns = [
    # 페이지 뷰 (전체 HTML)
    path('', async_views.index, name='index'),

    # HTMX 엔드포인트 (부분 HTML)
    path('htmx/items/', async_views.htmx_item_list, name='htmx_item_list'),
    path('htmx/items/<int:pk>/', async_views.htmx_item_detail, name='htmx_item_detail'),
    path('htmx/items/create/', async_views.htmx_item_create, name='htmx_item_create'),
    path('htmx/items/<int:pk>/update/', async_views.htmx_item_update, name='htmx_item_update'),
    path('htmx/items/<int:pk>/delete/', async_views.htmx_item_delete, name='htmx_item_delete'),
]
```

## 뷰 패턴

```python
# views/async_views.py
from django.http import HttpResponse
from django.shortcuts import render, aget_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Item
from .forms import ItemForm

@require_http_methods(["GET"])
async def htmx_item_list(request):
    """HTMX 리스트 뷰 - 부분 템플릿 반환"""
    items = [item async for item in Item.objects.all()]
    return render(request, 'app_name/partials/item_list.html', {
        'items': items
    })

@require_http_methods(["POST"])
async def htmx_item_create(request):
    """HTMX 생성 뷰"""
    form = ItemForm(request.POST)
    if form.is_valid():
        # Native async create
        item = await Item.objects.acreate(**form.cleaned_data)

        # HX-Trigger 헤더로 이벤트 발생
        response = render(request, 'app_name/partials/item_row.html', {
            'item': item
        })
        response['HX-Trigger'] = 'itemCreated'
        return response

    # 실패 시 폼 에러와 함께 반환
    return render(request, 'app_name/partials/item_form.html', {
        'form': form
    }, status=400)

@require_http_methods(["PUT", "PATCH"])
async def htmx_item_update(request, pk):
    """HTMX 업데이트 뷰"""
    item = await aget_object_or_404(Item, pk=pk)
    form = ItemForm(request.POST, instance=item)

    if form.is_valid():
        # Native async save
        for field, value in form.cleaned_data.items():
            setattr(item, field, value)
        await item.asave()

        return render(request, 'app_name/partials/item_row.html', {
            'item': item
        })

    return render(request, 'app_name/partials/item_form.html', {
        'form': form,
        'item': item
    }, status=400)

@require_http_methods(["DELETE"])
async def htmx_item_delete(request, pk):
    """HTMX 삭제 뷰"""
    item = await aget_object_or_404(Item, pk=pk)
    await item.adelete()

    # 빈 응답 반환 (hx-swap="outerHTML"과 함께 사용)
    response = HttpResponse(status=204)
    response['HX-Trigger'] = 'itemDeleted'
    return response
```

## 템플릿 구조

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}My App{% endblock %}</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    {% block extra_head %}{% endblock %}
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- HTMX 로딩 인디케이터 -->
    <div id="loading-spinner" class="htmx-indicator fixed top-4 right-4 z-50">
        <div class="bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
            <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Loading...</span>
        </div>
    </div>

    {% block content %}{% endblock %}

    <!-- HTMX CSRF 설정 -->
    <script>
        document.body.addEventListener('htmx:configRequest', (event) => {
            event.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
        });
    </script>
    {% block extra_scripts %}{% endblock %}
</body>
</html>

<!-- templates/app_name/pages/index.html -->
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-4xl mx-auto">
        <div class="flex justify-between items-center mb-6">
            <h1 class="text-3xl font-bold text-gray-900">Items</h1>
            <button
                class="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                hx-get="{% url 'app_name:htmx_item_create_form' %}"
                hx-target="#item-form-modal"
                hx-swap="innerHTML">
                Create New Item
            </button>
        </div>

        <!-- 아이템 리스트 -->
        <div
            id="item-list"
            class="space-y-4"
            hx-get="{% url 'app_name:htmx_item_list' %}"
            hx-trigger="load, itemCreated from:body, itemDeleted from:body"
            hx-indicator="#loading-spinner">
            <!-- HTMX로 로드될 영역 -->
        </div>

        <!-- 모달 영역 -->
        <div id="item-form-modal"></div>
    </div>
</div>
{% endblock %}

<!-- templates/app_name/partials/item_list.html -->
{% if items %}
    {% for item in items %}
        {% include "app_name/partials/item_row.html" with item=item %}
    {% endfor %}
{% else %}
    <div class="text-center py-12 bg-white rounded-lg shadow">
        <p class="text-gray-500 text-lg">No items found.</p>
    </div>
{% endif %}

<!-- templates/app_name/partials/item_row.html -->
<div
    id="item-{{ item.id }}"
    class="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6">
    <div class="flex justify-between items-start">
        <div class="flex-1">
            <h3 class="text-xl font-semibold text-gray-900 mb-2">{{ item.title }}</h3>
            <p class="text-gray-600">{{ item.description }}</p>
            <div class="mt-4 flex items-center gap-2 text-sm text-gray-500">
                <span>{{ item.created_at|date:"Y-m-d H:i" }}</span>
            </div>
        </div>
        <div class="flex gap-2 ml-4">
            <button
                class="text-blue-600 hover:text-blue-800 font-medium px-3 py-1"
                hx-get="{% url 'app_name:htmx_item_update' item.id %}"
                hx-target="#item-form-modal"
                hx-swap="innerHTML">
                Edit
            </button>
            <button
                class="text-red-600 hover:text-red-800 font-medium px-3 py-1"
                hx-delete="{% url 'app_name:htmx_item_delete' item.id %}"
                hx-target="#item-{{ item.id }}"
                hx-swap="outerHTML swap:1s"
                hx-confirm="정말 삭제하시겠습니까?"
                hx-indicator="#loading-spinner">
                Delete
            </button>
        </div>
    </div>
</div>

<!-- templates/app_name/partials/item_form.html -->
<div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 p-6">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold text-gray-900">
                {% if item %}Edit Item{% else %}Create Item{% endif %}
            </h2>
            <button
                class="text-gray-400 hover:text-gray-600"
                onclick="this.closest('#item-form-modal').innerHTML = ''">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>

        <form
            {% if item %}
                hx-put="{% url 'app_name:htmx_item_update' item.id %}"
            {% else %}
                hx-post="{% url 'app_name:htmx_item_create' %}"
            {% endif %}
            hx-target="#item-list"
            hx-swap="beforeend"
            class="space-y-4">
            {% csrf_token %}

            <div>
                <label for="id_title" class="block text-sm font-medium text-gray-700 mb-1">
                    Title
                </label>
                <input
                    type="text"
                    name="title"
                    id="id_title"
                    value="{{ form.title.value|default:'' }}"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required>
                {% if form.title.errors %}
                    <p class="mt-1 text-sm text-red-600">{{ form.title.errors.0 }}</p>
                {% endif %}
            </div>

            <div>
                <label for="id_description" class="block text-sm font-medium text-gray-700 mb-1">
                    Description
                </label>
                <textarea
                    name="description"
                    id="id_description"
                    rows="4"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">{{ form.description.value|default:'' }}</textarea>
                {% if form.description.errors %}
                    <p class="mt-1 text-sm text-red-600">{{ form.description.errors.0 }}</p>
                {% endif %}
            </div>

            <div class="flex justify-end gap-3 pt-4">
                <button
                    type="button"
                    class="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
                    onclick="this.closest('#item-form-modal').innerHTML = ''">
                    Cancel
                </button>
                <button
                    type="submit"
                    class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors">
                    {% if item %}Update{% else %}Create{% endif %}
                </button>
            </div>
        </form>
    </div>
</div>
```

## 응답 헤더

```python
from django.http import HttpResponse

# HX-Trigger: 클라이언트 이벤트 트리거
response = HttpResponse()
response['HX-Trigger'] = 'itemCreated'

# HX-Redirect: 클라이언트 리다이렉트
response['HX-Redirect'] = '/success/'

# HX-Refresh: 페이지 새로고침
response['HX-Refresh'] = 'true'
```

## 에러 핸들링

### 서버 사이드 에러 처리

```python
# views/async_views.py
from django.http import HttpResponse

async def htmx_view(request):
    try:
        # 비즈니스 로직
        pass
    except Exception as e:
        return render(request, 'partials/error.html', {
            'error_message': str(e)
        }, status=500)
```

### 에러/성공 템플릿

```html
<!-- templates/partials/error.html -->
<div class="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg" role="alert">
    <div class="flex items-start">
        <svg class="w-6 h-6 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div>
            <h3 class="text-red-800 font-semibold">Error</h3>
            <p class="text-red-700 mt-1">{{ error_message }}</p>
        </div>
    </div>
</div>

<!-- templates/partials/success.html -->
<div class="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg" role="alert">
    <div class="flex items-start">
        <svg class="w-6 h-6 text-green-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <div>
            <h3 class="text-green-800 font-semibold">Success</h3>
            <p class="text-green-700 mt-1">{{ success_message }}</p>
        </div>
    </div>
</div>
```

### 클라이언트 에러 핸들링

```html
<!-- base.html -->
<script>
document.body.addEventListener('htmx:responseError', function(evt) {
    // HTMX 요청 실패 시 처리
    console.error('HTMX Error:', evt.detail);
});

document.body.addEventListener('htmx:sendError', function(evt) {
    // 네트워크 에러 처리
    console.error('Network Error:', evt.detail);
});
</script>
```

## CSRF 보호

```html
<!-- HTMX POST/PUT/DELETE 요청 시 CSRF 토큰 포함 -->
<div hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
    <button hx-post="/api/create/">Create</button>
</div>

<!-- 또는 전역 설정 (권장) -->
<script>
document.body.addEventListener('htmx:configRequest', function(evt) {
    evt.detail.headers['X-CSRFToken'] = '{{ csrf_token }}';
});
</script>
```

## 디바운싱 및 최적화

### 검색 디바운싱

```html
<div class="relative">
    <input
        type="text"
        name="search"
        placeholder="Search items..."
        class="w-full px-4 py-2 pl-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        hx-get="/htmx/search/"
        hx-trigger="keyup changed delay:500ms"
        hx-target="#search-results"
        hx-indicator="#search-spinner">
    <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
    </svg>
    <div id="search-spinner" class="htmx-indicator absolute right-3 top-2.5">
        <svg class="animate-spin h-5 w-5 text-blue-500" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    </div>
</div>
<div id="search-results" class="mt-4"></div>
```

### 무한 스크롤

```html
<div
    hx-get="/htmx/items/?page=2"
    hx-trigger="revealed"
    hx-swap="afterend"
    hx-indicator="#load-more-spinner">
    <div id="load-more-spinner" class="htmx-indicator text-center py-4">
        <svg class="inline-block animate-spin h-8 w-8 text-blue-500" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
    </div>
</div>
```

## 네이밍 컨벤션

### 뷰 함수
- 일반 페이지: `{model}_list`, `{model}_detail`
- HTMX 엔드포인트: `htmx_{model}_{action}`
- 비동기 뷰: `async_views.py` 파일에 위치

### URL 패턴
- 일반 페이지: `/{model}s/`, `/{model}s/{pk}/`
- HTMX 엔드포인트: `/htmx/{model}s/{action}/`

### 템플릿
- 전체 페이지: `pages/{page_name}.html`
- HTMX 부분: `partials/{component_name}.html`
- 재사용 컴포넌트: `components/{component_name}.html`

### HTML ID/Class
- ID: `kebab-case` (예: `item-list`, `user-profile`)
- Class: `kebab-case` (예: `btn-primary`, `form-group`)
- HTMX 타겟: `#{model}-{element}` (예: `#item-list`, `#user-form`)

## JavaScript 코드 스타일

- ESLint 사용
- HTMX 이벤트 리스너는 `htmx:` prefix 확인
- 이벤트 핸들러는 명확하고 간결하게 작성

```javascript
// HTMX 이벤트 리스닝
document.body.addEventListener('htmx:afterSwap', (event) => {
    console.log('Content swapped:', event.detail);
});

// 커스텀 이벤트 발생
document.body.dispatchEvent(new CustomEvent('itemCreated', {
    detail: { itemId: 123 }
}));
```

## 주요 주의사항

1. **HTMX 타겟 명확히**: 항상 `hx-target` 명시
2. **CSRF 토큰**: POST/PUT/DELETE 요청 시 항상 포함
3. **로딩 인디케이터**: `hx-indicator`로 사용자 피드백 제공
4. **에러 메시지**: 사용자 친화적인 에러 메시지 제공

## 관련 리소스

- [HTMX Documentation](https://htmx.org/docs/)
- [HTMX Examples](https://htmx.org/examples/)
- [HTMX Events Reference](https://htmx.org/reference/#events)
