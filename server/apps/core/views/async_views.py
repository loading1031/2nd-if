"""
Asynchronous views for core app.
"""

from django.db.models import Count
from django.shortcuts import render

from apps.stories.models import Work


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
