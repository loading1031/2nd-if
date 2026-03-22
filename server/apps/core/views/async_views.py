"""
Asynchronous views for core app.
"""

import json
import os

import httpx
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.stories.models import Work

DIFY_API_URL = os.environ.get("DIFY_API_URL", "http://localhost/v1")
DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "")


async def index(request):
    """홈 페이지 — 인기 작품 표시."""
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
    """CS 상담 채팅 페이지."""
    return render(request, "core/pages/cs_chat.html")


@login_required
@require_http_methods(["POST"])
async def cs_chat_send(request):
    """Dify Chat API를 호출하고 SSE로 스트리밍 응답."""
    body = json.loads(request.body)
    query = body.get("query", "")
    conversation_id = body.get("conversation_id", "")

    user_id = str(request.user.pk)

    async def stream_dify():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{DIFY_API_URL}/chat-messages",
                headers={
                    "Authorization": f"Bearer {DIFY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "inputs": {},
                    "query": query,
                    "response_mode": "streaming",
                    "conversation_id": conversation_id,
                    "user": user_id,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        yield f"{line}\n\n"

    return StreamingHttpResponse(
        stream_dify(),
        content_type="text/event-stream",
    )
