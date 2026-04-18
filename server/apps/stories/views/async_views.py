from asgiref.sync import sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import aget_object_or_404, render
from django.views.decorators.http import require_http_methods

from ..forms import BranchCreateForm, EpisodeCreateForm, WorkCreateForm
from ..graph_service import aget_or_create_link, get_next_episodes_sorted, increment_visit
from ..models import Episode, EpisodeLink, EpisodePurchase, Rating, Work
from ..similarity import find_similar_branches
from ..watermark import embed_watermark


async def _get_user(request):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import AnonymousUser

    User = get_user_model()
    user_id = await sync_to_async(lambda: request.user.pk)()
    if user_id is None:
        return AnonymousUser()
    return await User.objects.aget(pk=user_id)


@require_http_methods(["GET"])
async def htmx_work_list(request):
    """HTMX 작품 목록."""
    from django.db.models import Count

    search = request.GET.get("search", "")
    status_filter = request.GET.get("status", "")

    qs = Work.objects.select_related("author").annotate(episode_count=Count("episodes"))
    if search:
        qs = qs.filter(title__icontains=search)
    if status_filter:
        qs = qs.filter(status=status_filter)

    works = [w async for w in qs]
    return render(request, "stories/partials/work_list.html", {"works": works})


@require_http_methods(["GET"])
async def htmx_episode_list(request, work_pk):
    """HTMX 에피소드 목록."""
    work = await aget_object_or_404(Work.objects.select_related("author"), pk=work_pk)
    episodes = [ep async for ep in Episode.objects.filter(work=work).select_related("author")]
    return render(
        request,
        "stories/partials/episode_list.html",
        {
            "work": work,
            "episodes": episodes,
        },
    )


@require_http_methods(["POST"])
@login_required
async def htmx_work_create(request):
    """HTMX 작품 생성."""
    form = WorkCreateForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()

    if not is_valid:
        return render(
            request,
            "stories/partials/work_create_form.html",
            {
                "form": form,
            },
            status=400,
        )

    work = form.instance
    work.author = await _get_user(request)
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
        return render(
            request,
            "stories/partials/episode_write_form.html",
            {
                "form": form,
                "work": work,
            },
            status=400,
        )

    episode = form.instance
    episode.work = work
    episode.author = await _get_user(request)

    # 유료 에피소드는 작가 지갑 필수
    if episode.is_paid and not episode.author.wallet_address:
        return HttpResponse("유료 에피소드를 만들려면 먼저 지갑 주소를 등록하세요.", status=400)

    episode.episode_number = await Episode.objects.filter(work=work).acount() + 1
    await episode.asave()

    # NEXT 링크 생성
    if episode.episode_number > 1:
        prev_episode = await Episode.objects.aget(work=work, episode_number=episode.episode_number - 1)
        await aget_or_create_link(prev_episode.pk, episode.pk, EpisodeLink.LinkType.NEXT, is_original=True)

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

    user = await _get_user(request)

    # 유료 에피소드 열람 제어
    if episode.is_paid:
        author_id = await sync_to_async(lambda: episode.author_id)()
        is_author = user.is_authenticated and user.pk == author_id
        has_purchased = (
            user.is_authenticated
            and await EpisodePurchase.objects.filter(episode=episode, buyer=user, confirmed=True).aexists()
        )

        if not is_author and not has_purchased:
            author = await sync_to_async(lambda: episode.work.author)()
            return render(
                request,
                "stories/partials/episode_paywall.html",
                {
                    "episode": episode,
                    "work_pk": work_pk,
                    "author_wallet": author.wallet_address,
                    "price": episode.price,
                },
            )

    # 조회수 증가
    episode.view_count += 1
    await episode.asave(update_fields=["view_count"])

    # 워터마크 식별자 결정
    if user.is_authenticated:
        wm_id = str(user.id)
        wm_label = user.nickname
    else:
        if not request.session.session_key:
            await sync_to_async(request.session.create)()
        wm_id = f"anon:{request.session.session_key[:16]}"
        wm_label = f"anon-{request.session.session_key[:8]}"

    # 콘텐츠에 워터마크 삽입
    watermarked_content = embed_watermark(episode.content or "", wm_id)

    return render(
        request,
        "stories/partials/episode_content.html",
        {
            "episode": episode,
            "watermarked_content": watermarked_content,
            "user_watermark_label": wm_label,
        },
    )


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

    user = await _get_user(request)
    rating, created = await Rating.objects.aupdate_or_create(
        episode=episode,
        user=user,
        defaults={"score": score},
    )

    # avg_rating, rating_count는 DB 트리거가 자동 갱신
    await episode.arefresh_from_db(fields=["avg_rating", "rating_count"])

    return render(
        request,
        "stories/partials/rating_result.html",
        {
            "episode": episode,
            "user_score": score,
        },
    )


@require_http_methods(["GET"])
async def htmx_next_episodes(request, work_pk, episode_number):
    """HTMX 다음 화 목록 (가중치 순 정렬)."""
    episode = await aget_object_or_404(Episode, work_id=work_pk, episode_number=episode_number)

    links = [link async for link in get_next_episodes_sorted(episode.pk)]

    enriched = [
        {
            "episode": link.to_episode,
            "is_original": link.is_original,
            "visit_count": link.visit_count,
        }
        for link in links
    ]

    # 분기 가능 여부 확인 (N화 제한 + 라이선스)
    from django.conf import settings

    work = await aget_object_or_404(Work, pk=work_pk)
    latest_episode_number = await Episode.objects.filter(work=work).acount()
    gap = getattr(settings, "BRANCH_EPISODE_GAP", 20)
    can_branch = (
        work.license != Work.License.NO_BRANCH
        and episode_number <= latest_episode_number - gap
        and request.user.is_authenticated
    )

    return render(
        request,
        "stories/partials/next_episodes.html",
        {
            "episode": episode,
            "next_list": enriched,
            "can_branch": can_branch,
            "work": work,
        },
    )


@require_http_methods(["POST"])
@login_required
async def htmx_check_similarity(request, work_pk, episode_number):
    """HTMX 분기 방향 유사도 검사 (pg_trgm)."""
    direction = request.POST.get("direction", "").strip()
    if len(direction) < 5:
        return render(request, "stories/partials/similarity_info.html")

    # pg_trgm으로 유사 분기 검색
    similar = await sync_to_async(
        lambda: list(find_similar_branches(work_pk, direction).select_related("author")[:1])
    )()

    if similar:
        ep = similar[0]
        return render(
            request,
            "stories/partials/similarity_warning.html",
            {
                "similar_episode": ep,
                "similarity": round(ep.sim * 100),
                "work_pk": work_pk,
            },
        )

    return render(request, "stories/partials/similarity_pass.html")


@require_http_methods(["POST"])
@login_required
async def htmx_branch_create(request, work_pk, episode_number):
    """HTMX 분기 생성."""
    origin_work = await aget_object_or_404(Work, pk=work_pk)
    origin_episode = await aget_object_or_404(Episode, work=origin_work, episode_number=episode_number)

    # 분기 가능 여부 검증
    from django.conf import settings

    latest_count = await Episode.objects.filter(work=origin_work).acount()
    gap = getattr(settings, "BRANCH_EPISODE_GAP", 20)
    if origin_work.license == Work.License.NO_BRANCH:
        return HttpResponse("이 작품은 분기가 금지되어 있습니다.", status=403)
    if episode_number > latest_count - gap:
        return HttpResponse(f"최신 {gap}화 이내에서는 분기할 수 없습니다.", status=403)

    form = BranchCreateForm(request.POST)
    is_valid = await sync_to_async(form.is_valid)()
    if not is_valid:
        return render(
            request,
            "stories/pages/branch_create.html",
            {
                "form": form,
                "work_id": origin_work.pk,
                "episode_number": episode_number,
            },
            status=400,
        )

    user = await _get_user(request)
    branch_episode = form.instance
    branch_episode.work = origin_work
    branch_episode.author = user

    # 유료 분기는 작가 지갑 필수
    if branch_episode.is_paid and not user.wallet_address:
        return HttpResponse("유료 에피소드를 만들려면 먼저 지갑 주소를 등록하세요.", status=400)

    branch_episode.episode_number = latest_count + 1
    await branch_episode.asave()

    # NEXT + BRANCHES_FROM 링크 생성
    await aget_or_create_link(origin_episode.pk, branch_episode.pk, EpisodeLink.LinkType.NEXT, is_original=False)
    await aget_or_create_link(origin_episode.pk, branch_episode.pk, EpisodeLink.LinkType.BRANCHES_FROM)

    response = HttpResponse()
    response["HX-Redirect"] = f"/stories/{origin_work.pk}/episodes/{branch_episode.episode_number}/"
    return response


@require_http_methods(["POST"])
async def htmx_visit_episode(request, work_pk, from_number, to_number):
    """경로 이동 시 visit_count 증가."""
    from_ep = await aget_object_or_404(Episode, work_id=work_pk, episode_number=from_number)
    to_ep = await aget_object_or_404(Episode, work_id=work_pk, episode_number=to_number)

    await increment_visit(from_ep.pk, to_ep.pk, to_ep.avg_rating)

    response = HttpResponse()
    response["HX-Redirect"] = f"/stories/{work_pk}/episodes/{to_number}/"
    return response
