---
globs: ["models.py", "**/models.py", "forms.py", "**/forms.py", "**/editor*.html"]
---

# django-editor-js 컨벤션

> [← 메인으로 돌아가기](main.md)

## 목차
- [모델 정의](#모델-정의)
- [폼 정의](#폼-정의)
- [HTMX 통합](#htmx-통합)
- [컨텐츠 렌더링](#컨텐츠-렌더링)
- [이미지 업로드](#이미지-업로드)

## 모델 정의

```python
# models.py
from django.db import models
from django_editorjs_fields import EditorJsJSONField

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = EditorJsJSONField(
        plugins=[
            "@editorjs/paragraph",
            "@editorjs/header",
            "@editorjs/list",
            "@editorjs/image",
            "@editorjs/code",
            "@editorjs/quote",
        ],
        tools={
            "Header": {
                "config": {
                    "levels": [2, 3, 4],
                    "defaultLevel": 2
                }
            },
            "Image": {
                "config": {
                    "endpoints": {
                        "byFile": "/api/upload-image/",
                    }
                }
            }
        },
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
```

### 사용 가능한 플러그인

- `@editorjs/paragraph` - 기본 텍스트
- `@editorjs/header` - 제목 (H2, H3, H4)
- `@editorjs/list` - 리스트 (ordered, unordered)
- `@editorjs/image` - 이미지 업로드
- `@editorjs/code` - 코드 블록
- `@editorjs/quote` - 인용구
- `@editorjs/delimiter` - 구분선
- `@editorjs/table` - 테이블
- `@editorjs/checklist` - 체크리스트
- `@editorjs/embed` - 임베드 (YouTube, etc.)

## 폼 정의

```python
# forms.py
from django import forms
from django_editorjs_fields import EditorJsWidget
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        widgets = {
            'content': EditorJsWidget(
                config={
                    'minHeight': 300,
                    'logLevel': 'ERROR',
                }
            )
        }
```

### 커스텀 위젯 설정

```python
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg'
            }),
            'content': EditorJsWidget(
                config={
                    'minHeight': 400,
                    'logLevel': 'ERROR',
                    'placeholder': '내용을 입력하세요...',
                    'autofocus': True,
                }
            )
        }
```

## HTMX 통합

```python
# views/async_views.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, aget_object_or_404
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async
from .models import Article
from .forms import ArticleForm

@require_http_methods(["GET", "POST"])
async def htmx_article_form(request, pk=None):
    """HTMX 기사 폼 뷰"""
    article = None
    if pk:
        article = await aget_object_or_404(Article, pk=pk)

    if request.method == "POST":
        # Form validation은 아직 동기 작업
        form = ArticleForm(request.POST, instance=article)
        if await sync_to_async(form.is_valid)():
            # Native async save
            if article:
                for field, value in form.cleaned_data.items():
                    setattr(article, field, value)
                await article.asave()
            else:
                article = await Article.objects.acreate(**form.cleaned_data)

            # 성공 시 상세 페이지로 리다이렉트
            response = HttpResponse()
            response['HX-Redirect'] = f'/articles/{article.id}/'
            return response

        # 실패 시 폼 다시 표시
        return render(request, 'app_name/partials/article_form.html', {
            'form': form,
            'article': article
        }, status=400)

    form = ArticleForm(instance=article)
    return render(request, 'app_name/partials/article_form.html', {
        'form': form,
        'article': article
    })
```

## 컨텐츠 렌더링

### 템플릿

```html
<!-- templates/app_name/partials/article_detail.html -->
<article class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
    <header class="mb-8 border-b pb-6">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">{{ article.title }}</h1>
        <div class="flex items-center gap-4 text-sm text-gray-500">
            <span>{{ article.created_at|date:"Y년 m월 d일" }}</span>
            {% if article.updated_at != article.created_at %}
                <span>• 수정: {{ article.updated_at|date:"Y.m.d H:i" }}</span>
            {% endif %}
        </div>
    </header>

    <div class="article-content prose prose-lg max-w-none">
        {{ article.content|safe }}
    </div>

    <footer class="mt-12 pt-6 border-t flex gap-3">
        <button
            class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
            hx-get="{% url 'app_name:htmx_article_form' article.id %}"
            hx-target="#article-form-modal"
            hx-swap="innerHTML">
            Edit
        </button>
        <button
            class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
            hx-delete="{% url 'app_name:htmx_article_delete' article.id %}"
            hx-confirm="정말 삭제하시겠습니까?"
            hx-target="body"
            hx-swap="none">
            Delete
        </button>
    </footer>
</article>
```

### 스타일 커스터마이징

```html
<!-- Editor.js 컨텐츠 스타일 -->
<style>
    .article-content h2 {
        @apply text-3xl font-bold text-gray-900 mt-8 mb-4;
    }
    .article-content h3 {
        @apply text-2xl font-bold text-gray-900 mt-6 mb-3;
    }
    .article-content h4 {
        @apply text-xl font-bold text-gray-900 mt-4 mb-2;
    }
    .article-content p {
        @apply text-gray-700 leading-relaxed mb-4;
    }
    .article-content ul, .article-content ol {
        @apply ml-6 mb-4;
    }
    .article-content ul {
        @apply list-disc;
    }
    .article-content ol {
        @apply list-decimal;
    }
    .article-content li {
        @apply text-gray-700 mb-2;
    }
    .article-content code {
        @apply bg-gray-100 px-2 py-1 rounded text-sm font-mono text-gray-800;
    }
    .article-content pre {
        @apply bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4;
    }
    .article-content pre code {
        @apply bg-transparent p-0 text-gray-100;
    }
    .article-content blockquote {
        @apply border-l-4 border-blue-500 pl-4 italic text-gray-600 mb-4 py-2;
    }
    .article-content img {
        @apply rounded-lg shadow-md my-6 max-w-full h-auto;
    }
    .article-content table {
        @apply w-full border-collapse mb-4;
    }
    .article-content th {
        @apply bg-gray-100 border border-gray-300 px-4 py-2 text-left font-semibold;
    }
    .article-content td {
        @apply border border-gray-300 px-4 py-2;
    }
</style>
```

## 이미지 업로드

### 엔드포인트 구현

```python
# views/async_views.py
import os
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async

@require_http_methods(["POST"])
async def upload_image(request):
    """Editor.js 이미지 업로드"""
    if 'image' not in request.FILES:
        return JsonResponse({
            'success': 0,
            'message': 'No image provided'
        })

    image = request.FILES['image']

    # 파일 크기 검증 (5MB)
    if image.size > 5 * 1024 * 1024:
        return JsonResponse({
            'success': 0,
            'message': 'File size exceeds 5MB'
        })

    # 파일 확장자 검증
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    file_ext = os.path.splitext(image.name)[1].lower()
    if file_ext not in allowed_extensions:
        return JsonResponse({
            'success': 0,
            'message': 'Invalid file type. Allowed: JPG, PNG, GIF, WebP'
        })

    # 비동기 파일 저장
    file_name = await sync_to_async(default_storage.save)(
        f'editor_images/{image.name}',
        image
    )
    file_url = default_storage.url(file_name)

    return JsonResponse({
        'success': 1,
        'file': {
            'url': file_url
        }
    })
```

### URL 설정

```python
# urls.py
urlpatterns = [
    # ...
    path('api/upload-image/', async_views.upload_image, name='upload_image'),
]
```

### 보안 고려사항

```python
import hashlib
import uuid
from pathlib import Path

@require_http_methods(["POST"])
async def upload_image(request):
    """보안 강화된 이미지 업로드"""
    if 'image' not in request.FILES:
        return JsonResponse({'success': 0, 'message': 'No image provided'})

    image = request.FILES['image']

    # 파일 크기 검증 (5MB)
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        return JsonResponse({
            'success': 0,
            'message': f'File size exceeds {max_size / 1024 / 1024}MB'
        })

    # 파일 확장자 검증
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    file_ext = Path(image.name).suffix.lower()
    if file_ext not in allowed_extensions:
        return JsonResponse({
            'success': 0,
            'message': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
        })

    # 안전한 파일명 생성 (UUID + 확장자)
    safe_filename = f'{uuid.uuid4().hex}{file_ext}'
    file_path = f'editor_images/{safe_filename}'

    # 비동기 파일 저장
    file_name = await sync_to_async(default_storage.save)(file_path, image)
    file_url = default_storage.url(file_name)

    return JsonResponse({
        'success': 1,
        'file': {
            'url': file_url
        }
    })
```

## 데이터 검증

### 컨텐츠 검증

```python
import json
from django.core.exceptions import ValidationError

def validate_editor_content(value):
    """Editor.js 컨텐츠 검증"""
    if not value:
        return

    try:
        # JSON 파싱 가능 여부 확인
        if isinstance(value, str):
            data = json.loads(value)
        else:
            data = value

        # 필수 필드 확인
        if 'blocks' not in data:
            raise ValidationError('Invalid editor content: missing blocks')

        # 블록 개수 제한 (예: 최대 100개)
        if len(data['blocks']) > 100:
            raise ValidationError('Too many blocks (max: 100)')

    except json.JSONDecodeError:
        raise ValidationError('Invalid JSON format')
```

## 주요 주의사항

1. **데이터 검증**: 클라이언트에서 받은 JSON 데이터는 항상 검증 필수
2. **이미지 업로드**: 파일 크기, 확장자, MIME 타입 검증
3. **XSS 방지**: 템플릿에서 `|safe` 필터 사용 시 주의 (django-editor-js는 자동으로 sanitize)
4. **스토리지**: 프로덕션 환경에서는 S3, Cloudinary 등 사용 권장

## 관련 리소스

- [django-editor-js GitHub](https://github.com/2ik/django-editor-js)
- [Editor.js Documentation](https://editorjs.io/)
- [Editor.js Plugins](https://github.com/editor-js)
