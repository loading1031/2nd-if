"""
Admin views for CS chat management.
"""

import asyncio
import json

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.core.models import ChatMessage, ChatRoom

User = get_user_model()


def staff_required(view_func):
    """staff가 아니면 403 반환하는 데코레이터."""

    async def wrapper(request, *args, **kwargs):
        is_staff = await sync_to_async(lambda: request.user.is_staff)()
        if not is_staff:
            return HttpResponse("Forbidden", status=403)
        return await view_func(request, *args, **kwargs)

    wrapper.__name__ = view_func.__name__
    wrapper.__module__ = view_func.__module__
    return wrapper


@login_required
@staff_required
async def cs_admin_list(request):
    """관리자 — 대화방 목록."""
    status_filter = request.GET.get("status", "open")

    rooms = [
        room
        async for room in ChatRoom.objects.select_related("user")
        .filter(status=status_filter)
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_admin=False, messages__is_read=False),
            )
        )
        .order_by("-last_message_at")
    ]

    # 마지막 메시지 미리보기 추가
    for room in rooms:
        last_msg = await room.messages.order_by("-created_at").afirst()
        room.last_message_preview = last_msg.content[:50] if last_msg else ""

    open_count = await ChatRoom.objects.filter(status="open").acount()

    return render(
        request,
        "core/pages/cs_admin_list.html",
        {
            "rooms": rooms,
            "status_filter": status_filter,
            "open_count": open_count,
        },
    )


@login_required
@staff_required
async def cs_admin_room(request, room_id):
    """관리자 — 대화방 상세 (채팅)."""
    from django.shortcuts import aget_object_or_404

    room = await aget_object_or_404(
        ChatRoom.objects.select_related("user"),
        pk=room_id,
    )
    messages = [msg async for msg in room.messages.select_related("sender").order_by("created_at")]

    # 사용자 메시지를 읽음 처리
    await room.messages.filter(is_admin=False, is_read=False).aupdate(is_read=True)

    last_message_id = messages[-1].id if messages else 0

    return render(
        request,
        "core/pages/cs_admin_room.html",
        {
            "room": room,
            "messages": messages,
            "last_message_id": last_message_id,
        },
    )


@login_required
@staff_required
@require_http_methods(["POST"])
async def cs_admin_send(request, room_id):
    """관리자 — 답변 전송."""
    from django.shortcuts import aget_object_or_404

    room = await aget_object_or_404(ChatRoom, pk=room_id)

    content = request.POST.get("content", "").strip()
    if not content:
        return HttpResponse("", status=400)

    admin_user_id = await sync_to_async(lambda: request.user.pk)()
    admin_user = await User.objects.aget(pk=admin_user_id)

    message = await ChatMessage.objects.acreate(
        room=room,
        sender=admin_user,
        is_admin=True,
        content=content,
    )

    room.last_message_at = timezone.now()
    await room.asave(update_fields=["last_message_at"])

    return render(
        request,
        "core/partials/chat_message.html",
        {
            "message": message,
        },
    )


@login_required
@staff_required
async def cs_admin_stream(request, room_id):
    """관리자 — SSE 스트림 (사용자 메시지 실시간 수신)."""
    from django.shortcuts import aget_object_or_404

    room = await aget_object_or_404(ChatRoom, pk=room_id)
    last_id = int(request.GET.get("last_id", 0))

    async def event_stream():
        nonlocal last_id
        while True:
            # 관리자는 사용자 메시지(is_admin=False)를 수신
            new_messages = [
                msg
                async for msg in room.messages.select_related("sender")
                .filter(id__gt=last_id, is_admin=False)
                .order_by("created_at")
            ]
            for msg in new_messages:
                msg.is_read = True
                await msg.asave(update_fields=["is_read"])

                html = await sync_to_async(render_to_string)(
                    "core/partials/chat_message.html",
                    {"message": msg},
                )
                data = json.dumps({"id": msg.id, "html": html})
                yield f"data: {data}\n\n"
                last_id = msg.id

            await asyncio.sleep(2)

    return StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@login_required
@staff_required
@require_http_methods(["PATCH"])
async def cs_admin_status(request, room_id):
    """관리자 — 대화방 상태 변경."""
    from django.shortcuts import aget_object_or_404

    room = await aget_object_or_404(ChatRoom, pk=room_id)

    # HTMX에서 hx-vals로 전달된 status
    body = json.loads(request.body) if request.body else {}
    new_status = body.get("status", request.POST.get("status", ""))

    valid_statuses = ["open", "resolved", "closed"]
    if new_status not in valid_statuses:
        return HttpResponse("Invalid status", status=400)

    room.status = new_status
    await room.asave(update_fields=["status", "updated_at"])

    return HttpResponse(status=204)
