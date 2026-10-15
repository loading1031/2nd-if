---
globs: ["*.py", "**/*.py"]
---

# Django 6.0+ Native Async ORM 컨벤션

> [← 메인으로 돌아가기](CLAUDE.md)

## 목차
- [비동기 뷰 정의](#비동기-뷰-정의)
- [비동기 뷰 사용 시점](#비동기-뷰-사용-시점)
- [병렬 쿼리](#병렬-쿼리)
- [데이터베이스 쿼리 최적화](#데이터베이스-쿼리-최적화)
- [권한 검증](#권한-검증)
- [테스트](#테스트)
- [Python 코드 스타일](#python-코드-스타일)
- [Native Async ORM 메서드 참고](#native-async-orm-메서드-참고)

## 비동기 뷰 정의

```python
# views/async_views.py
from django.http import HttpResponse
from django.shortcuts import render, aget_object_or_404
from .models import Item

# 함수 기반 비동기 뷰
async def async_list_view(request):
    """비동기 리스트 뷰"""
    # async for로 QuerySet을 리스트로 변환
    items = [item async for item in Item.objects.all()]
    return render(request, 'app_name/partials/item_list.html', {
        'items': items
    })

async def async_detail_view(request, pk):
    """비동기 상세 뷰"""
    item = await aget_object_or_404(Item, pk=pk)
    return render(request, 'app_name/partials/item_detail.html', {
        'item': item
    })

# Native async ORM 메서드들
async def create_item(title: str, description: str) -> Item:
    return await Item.objects.acreate(title=title, description=description)

async def update_item(pk: int, **kwargs) -> Item:
    item = await Item.objects.aget(pk=pk)
    for key, value in kwargs.items():
        setattr(item, key, value)
    await item.asave()
    return item

async def delete_item(pk: int) -> None:
    item = await Item.objects.aget(pk=pk)
    await item.adelete()
```

## 비동기 뷰 사용 시점

### 사용해야 할 때
- 외부 API 호출 (httpx, aiohttp 사용)
- 여러 데이터베이스 쿼리를 병렬로 실행
- I/O 바운드 작업

### 주의사항
- CPU 집약적 작업은 별도 프로세스/스레드로 처리
- 동기 라이브러리 사용 시에만 `sync_to_async` 필요 (예: Pillow, pandas, Form.is_valid)
- **`alist()`는 Django 6.0에 없음** — `async for`를 사용

## 병렬 쿼리

```python
import asyncio

async def get_dashboard_data(user_id: int):
    """여러 쿼리를 병렬로 실행"""
    items_count, first_order, first_notification = await asyncio.gather(
        Item.objects.filter(user_id=user_id).acount(),
        Order.objects.filter(user_id=user_id, status='pending').afirst(),
        Notification.objects.filter(user_id=user_id, read=False).afirst(),
    )
    return {
        'items_count': items_count,
        'first_order': first_order,
        'first_notification': first_notification,
    }
```

## 데이터베이스 쿼리 최적화

```python
# 관련 객체와 함께 조회 (N+1 방지)
async def get_items_with_related():
    return [
        item async for item in Item.objects.select_related('author').prefetch_related('tags')
    ]

# 특정 필드만 조회
async def get_item_titles():
    return [row async for row in Item.objects.values_list('id', 'title')]

# 집계 쿼리
async def get_item_stats():
    from django.db.models import Count, Avg
    return await Item.objects.aaggregate(
        total=Count('id'),
        avg_price=Avg('price')
    )

# 대량 생성/업데이트
async def bulk_create_items(items_data):
    items = [Item(**data) for data in items_data]
    return await Item.objects.abulk_create(items)
```

## 권한 검증

```python
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async

@login_required
async def htmx_protected_view(request):
    """로그인 필요한 HTMX 뷰"""
    has_perm = await sync_to_async(request.user.has_perm)('app_name.view_item')
    if not has_perm:
        return render(request, 'partials/error.html', {
            'error_message': '권한이 없습니다.'
        }, status=403)
```

### async 뷰에서 request.user 접근

`request.user`는 lazy 객체라 async 뷰에서 직접 접근하면 `SynchronousOnlyOperation` 발생.

```python
# Bad: 직접 접근 → 동기 DB 호출 발생
work.author = request.user

# Good: 실제 User 인스턴스를 비동기로 조회
async def _get_user(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_id = await sync_to_async(lambda: request.user.pk)()
    return await User.objects.aget(pk=user_id)

work.author = await _get_user(request)
```

## 테스트

```python
import pytest
from django.test import AsyncClient

@pytest.mark.django_db(transaction=True)
async def test_htmx_item_list():
    client = AsyncClient()
    response = await client.get('/htmx/items/')
    assert response.status_code == 200
```

## Python 코드 스타일

- PEP 8 준수
- 비동기 함수는 `async def` 명시
- Type hints 사용 권장

```python
from typing import Optional

async def get_item_by_id(item_id: int) -> Item:
    return await Item.objects.aget(id=item_id)

async def get_item_or_none(item_id: int) -> Optional[Item]:
    try:
        return await Item.objects.aget(id=item_id)
    except Item.DoesNotExist:
        return None

async def filter_items(user_id: int, status: str = 'active', limit: int = 10) -> list[Item]:
    return [item async for item in Item.objects.filter(user_id=user_id, status=status)[:limit]]
```

## Native Async ORM 메서드 참고

### 조회 메서드
| 동기 메서드 | 비동기 메서드 | 설명 |
|-----------|-------------|------|
| `.get()` | `.aget()` | 단일 객체 조회 |
| `.first()` | `.afirst()` | 첫 번째 객체 |
| `.last()` | `.alast()` | 마지막 객체 |
| `.exists()` | `.aexists()` | 존재 여부 |
| `.count()` | `.acount()` | 개수 |
| `list(qs)` | `[item async for item in qs]` | 리스트 변환 |
| `.iterator()` | `.aiterator()` | 반복자 |

> **주의**: `alist()`는 Django 6.0에 존재하지 않음. `async for`를 사용할 것.

### 수정 메서드
| 동기 메서드 | 비동기 메서드 | 설명 |
|-----------|-------------|------|
| `.create()` | `.acreate()` | 생성 |
| `.get_or_create()` | `.aget_or_create()` | 조회 또는 생성 |
| `.update_or_create()` | `.aupdate_or_create()` | 업데이트 또는 생성 |
| `.bulk_create()` | `.abulk_create()` | 대량 생성 |
| `.bulk_update()` | `.abulk_update()` | 대량 업데이트 |
| `.update()` | `.aupdate()` | 쿼리셋 업데이트 |
| `.delete()` | `.adelete()` | 삭제 |
| `.save()` | `.asave()` | 저장 (인스턴스 메서드) |

### 집계 메서드
| 동기 메서드 | 비동기 메서드 | 설명 |
|-----------|-------------|------|
| `.aggregate()` | `.aaggregate()` | 집계 |
| `.in_bulk()` | `.ain_bulk()` | 딕셔너리로 조회 |

## 주요 주의사항

1. **`alist()` 미지원**: Django 6.0에서 `alist()`는 없음. `[item async for item in qs]` 사용
2. **`request.user` lazy 접근 금지**: async 뷰에서 `_get_user()` 헬퍼 사용
3. **`sync_to_async`는 필요할 때만**: Form validation, 서드파티 라이브러리 등
4. **select_related 필수**: 템플릿에서 FK 접근 시 동기 DB 호출 방지

## 관련 리소스

- [Django Async Views](https://docs.djangoproject.com/en/stable/topics/async/)
- [Django Async ORM](https://docs.djangoproject.com/en/stable/topics/async/#asynchronous-support)
