from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, aget_object_or_404
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async

from ..models import Work, Episode, Rating
from ..forms import WorkCreateForm, EpisodeCreateForm


@require_http_methods(["GET"])
async def htmx_work_list(request):
    """HTMX 작품 목록."""
    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    qs = Work.objects.select_related("author")
    if search:
        qs = qs.filter(title__icontains=search)
    if status_filter:
        qs = qs.filter(status=status_filter)

    works = await qs.alist()
    return render(request, "stories/partials/work_list.html", {"works": works})


@require_http_methods(["GET"])
async def htmx_episode_list(request, work_pk):
    """HTMX 에피소드 목록."""
    work = await aget_object_or_404(Work, pk=work_pk)
    episodes = await Episode.objects.filter(work=work).select_related("author").alist()
    return render(request, "stories/partials/episode_list.html", {
        "work": work,
        "episodes": episodes,
    })


@require_http_methods(["POST"])
@login_required
async def htmx_work_create(request):
    """HTMX 작품 생성."""
    form = WorkCreateForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()

    if not is_valid:
        return render(request, "stories/partials/work_create_form.html", {
            "form": form,
        }, status=400)

    work = form.instance
    work.author = request.user
    await work.asave()

    response = HttpResponse()
    response["HX-Redirect"] = f"/stories/{work.pk}/"
    return response


@require_http_methods(["POST"])
@login_required
async def htmx_episode_create(request, work_pk):
    """HTMX 에피소드 생성."""
    work = await aget_object_or_404(Work, pk=work_pk)

    form = EpisodeCreateForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()

    if not is_valid:
        return render(request, "stories/partials/episode_write_form.html", {
            "form": form,
            "work": work,
        }, status=400)

    episode = form.instance
    episode.work = work
    episode.author = request.user
    episode.episode_number = await Episode.objects.filter(work=work).acount() + 1
    await episode.asave()

    response = HttpResponse()
    response["HX-Redirect"] = f"/stories/{work.pk}/episodes/{episode.episode_number}/"
    return response


@require_http_methods(["GET"])
async def htmx_episode_read(request, work_pk, episode_number):
    """HTMX 에피소드 본문 로드."""
    episode = await aget_object_or_404(
        Episode.objects.select_related("work", "author"),
        work_id=work_pk,
        episode_number=episode_number,
    )

    # 조회수 증가
    episode.view_count += 1
    await episode.asave(update_fields=["view_count"])

    return render(request, "stories/partials/episode_content.html", {
        "episode": episode,
    })


@require_http_methods(["POST"])
@login_required
async def htmx_rate_episode(request, work_pk, episode_number):
    """HTMX 별점 등록/수정."""
    episode = await aget_object_or_404(
        Episode,
        work_id=work_pk,
        episode_number=episode_number,
    )

    score = int(request.POST.get("score", 0))
    if not 1 <= score <= 5:
        return HttpResponse(status=400)

    rating, created = await Rating.objects.aupdate_or_create(
        episode=episode,
        user=request.user,
        defaults={"score": score},
    )

    # 별점 평균 갱신
    from django.db.models import Avg
    result = await Rating.objects.filter(episode=episode).aaggregate(
        avg=Avg("score"),
    )
    episode.avg_rating = result["avg"]
    episode.rating_count = await Rating.objects.filter(episode=episode).acount()
    await episode.asave(update_fields=["avg_rating", "rating_count"])

    return render(request, "stories/partials/rating_result.html", {
        "episode": episode,
        "user_score": score,
    })
