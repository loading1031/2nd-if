"""
Asynchronous views for core app.
"""

from asgiref.sync import sync_to_async
from django.contrib.auth import aget_user
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.stories.models import Work


async def cs_faq(request):
    """FAQ 페이지 — 로그인 불필요."""
    request.user = await aget_user(request)
    return render(request, "core/pages/cs_faq.html")


async def index(request):
    """홈 페이지 — 인기 작품 표시."""
    request.user = await aget_user(request)
    featured_works = [
        w
        async for w in Work.objects.select_related("author")
        .annotate(episode_count=Count("episodes"))
        .order_by("-created_at")[:8]
    ]
    return render(
        request,
        "core/pages/index.html",
        {
            "featured_works": featured_works,
        },
    )


@login_required
async def cs_chat(request):
    """CS 상담 채팅 페이지 — 채팅방 자동 생성."""
    from django.contrib.auth import get_user_model

    from apps.core.models import ChatRoom

    User = get_user_model()
    user_id = await sync_to_async(lambda: request.user.pk)()
    user = await User.objects.aget(pk=user_id)

    room, _ = await ChatRoom.objects.aget_or_create(user=user)
    messages = [msg async for msg in room.messages.select_related("sender").order_by("created_at")]
    last_message_id = messages[-1].id if messages else 0

    return render(
        request,
        "core/pages/cs_chat.html",
        {
            "room": room,
            "messages": messages,
            "last_message_id": last_message_id,
        },
    )


@login_required
@require_http_methods(["POST"])
async def cs_chat_send(request):
    """사용자 메시지 전송 — DB 저장 후 HTML fragment 반환."""
    from django.contrib.auth import get_user_model
    from django.utils import timezone

    from apps.core.models import ChatMessage, ChatRoom

    User = get_user_model()
    user_id = await sync_to_async(lambda: request.user.pk)()
    user = await User.objects.aget(pk=user_id)

    content = request.POST.get("content", "").strip()
    if not content:
        return HttpResponse("", status=400)

    room, _ = await ChatRoom.objects.aget_or_create(user=user)
    message = await ChatMessage.objects.acreate(
        room=room,
        sender=user,
        is_admin=False,
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
async def cs_chat_stream(request):
    """SSE 스트림 — 새 메시지를 실시간으로 전달."""
    import asyncio
    import json

    from django.contrib.auth import get_user_model
    from django.template.loader import render_to_string

    from apps.core.models import ChatRoom

    User = get_user_model()
    user_id = await sync_to_async(lambda: request.user.pk)()
    user = await User.objects.aget(pk=user_id)

    last_id = int(request.GET.get("last_id", 0))

    async def event_stream():
        nonlocal last_id
        try:
            room = await ChatRoom.objects.aget(user=user)
        except ChatRoom.DoesNotExist:
            return

        while True:
            new_messages = [
                msg
                async for msg in room.messages.select_related("sender")
                .filter(id__gt=last_id, is_admin=True)
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
