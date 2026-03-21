---
globs: ["*.py", "**/*.py"]
---

# Django 6.0+ Native Async ORM 컨벤션

> [← 메인으로 돌아가기](main.md)

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
    # Native async ORM - QuerySet을 리스트로 변환
    items = [item async for item in Item.objects.all()]
    return render(request, 'app_name/partials/item_list.html', {
        'items': items
    })

async def async_detail_view(request, pk):
    """비동기 상세 뷰"""
    # Native async aget_object_or_404
    item = await aget_object_or_404(Item, pk=pk)
    return render(request, 'app_name/partials/item_detail.html', {
        'item': item
    })

# Native async ORM 메서드들
async def create_item(title: str, description: str) -> Item:
    """아이템 생성"""
    return await Item.objects.acreate(
        title=title,
        description=description
    )

async def update_item(pk: int, **kwargs) -> Item:
    """아이템 업데이트"""
    item = await Item.objects.aget(pk=pk)
    for key, value in kwargs.items():
        setattr(item, key, value)
    await item.asave()
    return item

async def delete_item(pk: int) -> None:
    """아이템 삭제"""
    item = await Item.objects.aget(pk=pk)
    await item.adelete()

async def get_first_item():
    """첫 번째 아이템 조회"""
    return await Item.objects.afirst()

async def item_exists(pk: int) -> bool:
    """아이템 존재 여부"""
    return await Item.objects.filter(pk=pk).aexists()

async def count_items() -> int:
    """아이템 개수"""
    return await Item.objects.acount()
```

## 비동기 뷰 사용 시점

### 사용해야 할 때
- 외부 API 호출 (httpx, aiohttp 사용)
- 여러 데이터베이스 쿼리를 병렬로 실행
- I/O 바운드 작업
- **Django 6.0의 Native Async ORM은 모든 CRUD 작업에 사용 가능**

### 주의사항
- CPU 집약적 작업은 별도 프로세스/스레드로 처리
- 동기 라이브러리 사용 시에만 `sync_to_async` 필요 (예: Pillow, pandas)
- `async for`는 대량 데이터 스트리밍에 유용

## 병렬 쿼리

```python
import asyncio

async def get_dashboard_data(user_id: int):
    """여러 쿼리를 병렬로 실행"""
    # asyncio.gather로 병렬 실행
    items, orders, notifications = await asyncio.gather(
        Item.objects.filter(user_id=user_id).acount(),
        Order.objects.filter(user_id=user_id, status='pending').alist(),
        Notification.objects.filter(user_id=user_id, read=False).alist()
    )
    return {
        'items_count': items,
        'pending_orders': orders,
        'unread_notifications': notifications
    }
```

## 데이터베이스 쿼리 최적화

```python
# Native async ORM 쿼리 최적화
async def get_items_with_related():
    """관련 객체와 함께 조회 (N+1 방지)"""
    return [
        item async for item in Item.objects.select_related('author').prefetch_related('tags')
    ]

# alist() 메서드 사용 (리스트로 한번에 로드)
async def get_items_list():
    """리스트로 한번에 로드"""
    return await Item.objects.select_related('author').alist()

# 특정 필드만 조회
async def get_item_titles():
    """특정 필드만 조회"""
    return await Item.objects.values_list('id', 'title').alist()

# 집계 쿼리
async def get_item_stats():
    """집계 쿼리"""
    from django.db.models import Count, Avg
    return await Item.objects.aaggregate(
        total=Count('id'),
        avg_price=Avg('price')
    )

# 대량 생성
async def bulk_create_items(items_data):
    """대량 생성"""
    items = [Item(**data) for data in items_data]
    return await Item.objects.abulk_create(items)

# 대량 업데이트
async def bulk_update_items(items, fields):
    """대량 업데이트"""
    await Item.objects.abulk_update(items, fields)
```

## 권한 검증

```python
# views/async_views.py
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from asgiref.sync import sync_to_async

@login_required
async def htmx_protected_view(request):
    """로그인 필요한 HTMX 뷰"""
    # 추가 권한 검증
    has_perm = await sync_to_async(request.user.has_perm)('app_name.view_item')
    if not has_perm:
        return render(request, 'partials/error.html', {
            'error_message': '권한이 없습니다.'
        }, status=403)
    # ...

# 소유자 검증
async def htmx_item_update_owner_check(request, pk):
    """소유자만 수정 가능"""
    item = await aget_object_or_404(Item, pk=pk)

    # 소유자 확인
    if item.user_id != request.user.id:
        return render(request, 'partials/error.html', {
            'error_message': '본인의 게시물만 수정할 수 있습니다.'
        }, status=403)

    # 수정 로직
    # ...
```

## 테스트

```python
# tests.py
import pytest
from django.test import AsyncClient

@pytest.mark.asyncio
async def test_htmx_item_list():
    """HTMX 리스트 뷰 테스트"""
    client = AsyncClient()
    response = await client.get('/htmx/items/')
    assert response.status_code == 200
    assert b'item-list' in response.content
```

## Python 코드 스타일

- PEP 8 준수
- 비동기 함수는 `async def` 명시
- Type hints 사용 권장 (Python 3.10+ 기준)

```python
from typing import Optional

async def get_item_by_id(item_id: int) -> Item:
    """ID로 아이템 조회 (Native async ORM)"""
    return await Item.objects.aget(id=item_id)

async def get_item_or_none(item_id: int) -> Optional[Item]:
    """ID로 아이템 조회 (없으면 None)"""
    try:
        return await Item.objects.aget(id=item_id)
    except Item.DoesNotExist:
        return None

async def filter_items(
    user_id: int,
    status: str = 'active',
    limit: int = 10
) -> list[Item]:
    """아이템 필터링"""
    return await Item.objects.filter(
        user_id=user_id,
        status=status
    )[:limit].alist()
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
| `list(qs)` | `.alist()` | 리스트 변환 |
| `.iterator()` | `.aiterator()` | 반복자 |

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

1. **Native Async ORM 사용**: `sync_to_async`는 필요할 때만 사용 (Form validation, 서드파티 라이브러리 등)

2. **QuerySet 평가 타이밍**:
   ```python
   # Bad: async for 없이 리스트 변환 시도
   items = list(Item.objects.all())  # 동기 작업!

   # Good: async for 또는 alist() 사용
   items = [item async for item in Item.objects.all()]
   items = await Item.objects.all().alist()
   ```

## 관련 리소스

- [Django Async Views](https://docs.djangoproject.com/en/stable/topics/async/)
- [Django Async ORM](https://docs.djangoproject.com/en/stable/topics/async/#asynchronous-support)
