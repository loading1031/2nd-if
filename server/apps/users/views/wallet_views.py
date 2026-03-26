"""지갑 설정 HTMX 뷰."""

import re

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

User = get_user_model()

# 0x + 40자 hex
WALLET_ADDRESS_PATTERN = re.compile(r"^0x[0-9a-fA-F]{40}$")


async def _get_user(request):
    """async 뷰에서 request.user를 안전하게 조회."""
    user_id = await sync_to_async(lambda: request.user.pk)()
    if user_id is None:
        return None
    return await User.objects.aget(pk=user_id)


@login_required
@require_http_methods(["GET"])
async def wallet_settings_page(request):
    """지갑 설정 페이지."""
    user = await _get_user(request)
    return render(
        request,
        "users/pages/wallet_settings.html",
        {
            "wallet_address": user.wallet_address,
        },
    )


@require_http_methods(["POST"])
@login_required
async def htmx_save_wallet(request):
    """지갑 주소 저장."""
    wallet_address = request.POST.get("wallet_address", "").strip()

    # 빈 값이면 지갑 주소 제거
    if not wallet_address:
        user = await _get_user(request)
        user.wallet_address = ""
        await user.asave(update_fields=["wallet_address"])
        return render(
            request,
            "users/partials/wallet_save_success.html",
            {"success_message": "지갑 주소가 제거되었습니다."},
        )

    # 형식 검증: 0x + 40자 hex
    if not WALLET_ADDRESS_PATTERN.match(wallet_address):
        return render(
            request,
            "users/partials/wallet_save_error.html",
            {"error_message": "올바르지 않은 지갑 주소 형식입니다. (0x + 40자 hex)"},
            status=400,
        )

    # User.wallet_address 업데이트
    user = await _get_user(request)
    user.wallet_address = wallet_address
    await user.asave(update_fields=["wallet_address"])

    return render(
        request,
        "users/partials/wallet_save_success.html",
        {
            "success_message": "지갑 주소가 저장되었습니다.",
            "wallet_address": wallet_address,
        },
    )
