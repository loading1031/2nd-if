"""결제 확인 HTMX 뷰."""

from decimal import Decimal

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import aget_object_or_404, render
from django.views.decorators.http import require_http_methods

from ..models import Episode, EpisodePurchase, Work
from ..payment import verify_transaction

User = get_user_model()


async def _get_user(request):
    """async 뷰에서 request.user를 안전하게 조회."""
    user_id = await sync_to_async(lambda: request.user.pk)()
    if user_id is None:
        return None
    return await User.objects.aget(pk=user_id)


@require_http_methods(["POST"])
@login_required
async def htmx_confirm_payment(request, work_pk: int, episode_number: int):
    """결제 확인 - 프론트에서 tx_hash를 받아서 검증.

    POST 파라미터:
        tx_hash: Polygon 트랜잭션 해시
        token: "USDC" or "USDT"
    """
    tx_hash = request.POST.get("tx_hash", "").strip()
    token = request.POST.get("token", "").strip()

    # 기본 검증
    if not tx_hash:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "트랜잭션 해시를 입력해주세요."},
            status=400,
        )

    if token not in ("USDC", "USDT"):
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "지원하지 않는 토큰입니다. (USDC 또는 USDT)"},
            status=400,
        )

    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "올바르지 않은 트랜잭션 해시 형식입니다."},
            status=400,
        )

    # 에피소드 및 작품 조회
    episode = await aget_object_or_404(
        Episode,
        work_id=work_pk,
        episode_number=episode_number,
    )
    work = await aget_object_or_404(Work.objects.select_related("author"), pk=work_pk)
    author = await sync_to_async(lambda: work.author)()

    user = await _get_user(request)

    # 유료 에피소드인지 확인
    if not episode.is_paid:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "무료 에피소드입니다."},
            status=400,
        )

    # 중복 구매 확인
    already_purchased = await EpisodePurchase.objects.filter(
        episode=episode,
        buyer=user,
    ).aexists()
    if already_purchased:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "이미 구매한 에피소드입니다."},
            status=400,
        )

    # 같은 tx_hash로 이미 처리된 구매가 있는지 확인
    tx_used = await EpisodePurchase.objects.filter(tx_hash=tx_hash).aexists()
    if tx_used:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "이미 사용된 트랜잭션입니다."},
            status=400,
        )

    # 작가 지갑 주소 확인
    if not author.wallet_address:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": "작가의 지갑 주소가 설정되지 않았습니다."},
            status=500,
        )

    # 트랜잭션 검증
    expected_amount = Decimal(str(episode.price)) if episode.price else Decimal("0")
    result = await verify_transaction(
        tx_hash=tx_hash,
        expected_to=author.wallet_address,
        expected_token=token,
        expected_amount=expected_amount,
    )

    if not result["valid"]:
        return render(
            request,
            "stories/partials/payment_error.html",
            {"error_message": result["error"]},
            status=400,
        )

    # EpisodePurchase 생성
    await EpisodePurchase.objects.acreate(
        episode=episode,
        buyer=user,
        tx_hash=tx_hash,
        token=token,
        amount=expected_amount,
    )

    # 성공 응답
    return render(
        request,
        "stories/partials/payment_success.html",
        {
            "episode": episode,
            "work": work,
        },
    )
