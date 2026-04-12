"""AI 프로바이더 설정 뷰."""

import httpx
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from apps.users.crypto import decrypt_key, encrypt_key
from apps.users.models import UserAIProvider

User = get_user_model()


async def _get_user(request):
    user_id = await sync_to_async(lambda: request.user.pk)()
    return await User.objects.aget(pk=user_id)


@login_required
async def ai_settings(request):
    """AI 프로바이더 설정 페이지."""
    user = await _get_user(request)
    providers = [p async for p in UserAIProvider.objects.filter(user=user).order_by("-created_at")]
    return render(request, "users/pages/ai_settings.html", {"providers": providers})


@login_required
@require_http_methods(["POST"])
async def ai_provider_add(request):
    """프로바이더 추가."""
    user = await _get_user(request)

    provider = request.POST.get("provider", "")
    display_name = request.POST.get("display_name", "").strip()
    api_key = request.POST.get("api_key", "").strip()
    model_name = request.POST.get("model_name", "").strip()
    base_url = request.POST.get("base_url", "").strip()

    if not all([provider, display_name, model_name]):
        return HttpResponse("필수 항목을 입력해주세요.", status=400)

    # Ollama는 API 키 불필요
    if provider != "ollama" and not api_key:
        return HttpResponse("API 키를 입력해주세요.", status=400)

    encrypted = encrypt_key(api_key) if api_key else encrypt_key("")

    p = await UserAIProvider.objects.acreate(
        user=user,
        provider=provider,
        display_name=display_name,
        api_key_encrypted=encrypted,
        base_url=base_url,
        model_name=model_name,
    )
    return render(request, "users/partials/ai_provider_row.html", {"provider": p})


@login_required
@require_http_methods(["DELETE"])
async def ai_provider_delete(request, pk):
    """프로바이더 삭제."""
    user = await _get_user(request)
    try:
        p = await UserAIProvider.objects.aget(pk=pk, user=user)
        await p.adelete()
    except UserAIProvider.DoesNotExist:
        pass
    return HttpResponse(status=204)


@login_required
@require_http_methods(["POST"])
async def ai_provider_test(request, pk):
    """프로바이더 연결 테스트."""
    user = await _get_user(request)
    try:
        p = await UserAIProvider.objects.aget(pk=pk, user=user)
    except UserAIProvider.DoesNotExist:
        return render(
            request,
            "users/partials/ai_test_result.html",
            {"success": False, "message": "프로바이더를 찾을 수 없습니다."},
        )

    api_key = decrypt_key(bytes(p.api_key_encrypted))
    base_url = p.base_url

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if p.provider in ("openai", "ollama"):
                url = (base_url or "https://api.openai.com") + "/v1/models"
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                resp = await client.get(url, headers=headers)
            elif p.provider == "anthropic":
                resp = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                    },
                )
            elif p.provider == "google":
                resp = await client.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
            else:
                resp = None

            if resp and resp.status_code == 200:
                return render(
                    request,
                    "users/partials/ai_test_result.html",
                    {"success": True, "message": "연결 성공!"},
                )
            else:
                status = resp.status_code if resp else "unknown"
                return render(
                    request,
                    "users/partials/ai_test_result.html",
                    {"success": False, "message": f"연결 실패 (HTTP {status})"},
                )
    except Exception as e:
        return render(
            request,
            "users/partials/ai_test_result.html",
            {"success": False, "message": f"연결 실패: {str(e)}"},
        )
