from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, aget_object_or_404
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async

from ..models import Work, Episode, Rating
from ..forms import WorkCreateForm, EpisodeCreateForm
from ..graph import EpisodeNode


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

    # Neo4j 노드 생성 + NEXT 연결
    node = await sync_to_async(EpisodeNode.get_or_create_node)(episode.pk, work.pk)
    if episode.episode_number > 1:
        prev_episode = await Episode.objects.aget(work=work, episode_number=episode.episode_number - 1)
        prev_node = await sync_to_async(EpisodeNode.get_or_create_node)(prev_episode.pk, work.pk)
        await sync_to_async(prev_node.add_next)(node, is_original=True)

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


@require_http_methods(["GET"])
async def htmx_next_episodes(request, work_pk, episode_number):
    """HTMX 다음 화 목록 (가중치 순 정렬)."""
    episode = await aget_object_or_404(Episode, work_id=work_pk, episode_number=episode_number)

    try:
        node = await sync_to_async(lambda: EpisodeNode.nodes.get(episode_id=episode.pk))()
        next_list = await sync_to_async(node.get_next_episodes_sorted)()
    except EpisodeNode.DoesNotExist:
        next_list = []

    # Django Episode 정보를 붙여서 전달
    enriched = []
    for item in next_list:
        ep = await Episode.objects.select_related("author").aget(pk=item["node"].episode_id)
        enriched.append({
            "episode": ep,
            "is_original": item["is_original"],
            "visit_count": item["visit_count"],
        })

    # 분기 가능 여부 확인 (20화 제한 + 라이선스)
    work = await aget_object_or_404(Work, pk=work_pk)
    latest_episode_number = await Episode.objects.filter(work=work).acount()
    can_branch = (
        work.license != Work.License.NO_BRANCH
        and episode_number <= latest_episode_number - 20
        and request.user.is_authenticated
    )

    return render(request, "stories/partials/next_episodes.html", {
        "episode": episode,
        "next_list": enriched,
        "can_branch": can_branch,
        "work": work,
    })


@require_http_methods(["POST"])
@login_required
async def htmx_branch_create(request, work_pk, episode_number):
    """HTMX 분기 생성."""
    origin_work = await aget_object_or_404(Work, pk=work_pk)
    origin_episode = await aget_object_or_404(Episode, work=origin_work, episode_number=episode_number)

    # 분기 가능 여부 검증
    latest_count = await Episode.objects.filter(work=origin_work).acount()
    if origin_work.license == Work.License.NO_BRANCH:
        return HttpResponse("이 작품은 분기가 금지되어 있습니다.", status=403)
    if episode_number > latest_count - 20:
        return HttpResponse("최신 20화 이내에서는 분기할 수 없습니다.", status=403)

    form = EpisodeCreateForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()
    if not is_valid:
        return render(request, "stories/partials/branch_create_form.html", {
            "form": form,
            "origin_episode": origin_episode,
            "work": origin_work,
        }, status=400)

    # 분기 에피소드 저장 (같은 work에 속함)
    branch_episode = form.instance
    branch_episode.work = origin_work
    branch_episode.author = request.user
    branch_episode.episode_number = latest_count + 1
    await branch_episode.asave()

    # Neo4j: 분기 노드 생성 + BRANCHES_FROM + NEXT 연결
    origin_node = await sync_to_async(EpisodeNode.get_or_create_node)(origin_episode.pk, origin_work.pk)
    branch_node = await sync_to_async(EpisodeNode.get_or_create_node)(branch_episode.pk, origin_work.pk)
    await sync_to_async(origin_node.add_next)(branch_node, is_original=False)
    await sync_to_async(origin_node.add_branch)(branch_node)

    response = HttpResponse()
    response["HX-Redirect"] = f"/stories/{origin_work.pk}/episodes/{branch_episode.episode_number}/"
    return response


@require_http_methods(["POST"])
async def htmx_visit_episode(request, work_pk, from_number, to_number):
    """경로 이동 시 visit_count 증가."""
    from_ep = await aget_object_or_404(Episode, work_id=work_pk, episode_number=from_number)
    to_ep = await aget_object_or_404(Episode, work_id=work_pk, episode_number=to_number)

    await sync_to_async(EpisodeNode.increment_visit)(
        from_ep.pk, to_ep.pk, to_ep.avg_rating
    )

    response = HttpResponse()
    response["HX-Redirect"] = f"/stories/{work_pk}/episodes/{to_number}/"
    return response
