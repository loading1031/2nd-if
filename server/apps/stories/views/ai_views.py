"""AI 생성 뷰."""

import json

import httpx
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from django.shortcuts import render

from apps.users.crypto import decrypt_key
from apps.users.models import UserAIProvider

User = get_user_model()


async def _get_user(request):
    user_id = await sync_to_async(lambda: request.user.pk)()
    return await User.objects.aget(pk=user_id)


@login_required
async def htmx_ai_providers(request):
    """사용자의 AI 프로바이더 목록 (패널 select용)."""
    user = await _get_user(request)
    providers = [p async for p in UserAIProvider.objects.filter(user=user, is_active=True)]
    return render(request, "stories/partials/ai_provider_select.html", {"providers": providers})


@login_required
async def htmx_ai_generate(request):
    """AI 텍스트 생성 -- SSE 스트리밍."""
    user = await _get_user(request)

    provider_id = request.GET.get("provider_id")
    prompt = request.GET.get("prompt", "")
    context = request.GET.get("context", "")

    if not provider_id or not prompt:
        return StreamingHttpResponse(
            _error_stream("프로바이더와 프롬프트를 입력해주세요."),
            content_type="text/event-stream",
        )

    try:
        p = await UserAIProvider.objects.aget(pk=provider_id, user=user)
    except UserAIProvider.DoesNotExist:
        return StreamingHttpResponse(
            _error_stream("프로바이더를 찾을 수 없습니다."),
            content_type="text/event-stream",
        )

    api_key = decrypt_key(bytes(p.api_key_encrypted))

    system_prompt = "당신은 소설 작성을 돕는 AI 어시스턴트입니다. 사용자의 지시에 따라 소설 내용을 이어서 작성해주세요."
    user_prompt = f"이전 내용:\n{context}\n\n지시사항:\n{prompt}" if context else prompt

    async def stream():
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                if p.provider in ("openai", "ollama"):
                    async for chunk in _stream_openai(
                        client,
                        api_key,
                        p.base_url,
                        p.model_name,
                        system_prompt,
                        user_prompt,
                    ):
                        yield chunk
                elif p.provider == "anthropic":
                    async for chunk in _stream_anthropic(
                        client,
                        api_key,
                        p.model_name,
                        system_prompt,
                        user_prompt,
                    ):
                        yield chunk
                elif p.provider == "google":
                    async for chunk in _stream_google(
                        client,
                        api_key,
                        p.model_name,
                        system_prompt,
                        user_prompt,
                    ):
                        yield chunk
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingHttpResponse(
        stream(),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _stream_openai(client, api_key, base_url, model, system_prompt, user_prompt):
    url = (base_url or "https://api.openai.com") + "/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": True,
    }
    async with client.stream("POST", url, json=body, headers=headers) as resp:
        async for line in resp.aiter_lines():
            if line.startswith("data: ") and line != "data: [DONE]":
                try:
                    data = json.loads(line[6:])
                    delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                    if delta:
                        yield f"data: {json.dumps({'text': delta})}\n\n"
                except json.JSONDecodeError:
                    pass


async def _stream_anthropic(client, api_key, model, system_prompt, user_prompt):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": 2048,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
        "stream": True,
    }
    async with client.stream("POST", url, json=body, headers=headers) as resp:
        async for line in resp.aiter_lines():
            if line.startswith("data: "):
                try:
                    data = json.loads(line[6:])
                    if data.get("type") == "content_block_delta":
                        text = data.get("delta", {}).get("text", "")
                        if text:
                            yield f"data: {json.dumps({'text': text})}\n\n"
                except json.JSONDecodeError:
                    pass


async def _stream_google(client, api_key, model, system_prompt, user_prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={api_key}"
    body = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
    }
    async with client.stream("POST", url, json=body) as resp:
        buffer = ""
        async for chunk in resp.aiter_bytes():
            buffer += chunk.decode()
            while '"text"' in buffer:
                try:
                    data = json.loads(buffer)
                    for candidate in data:
                        for part in candidate.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                            text = part.get("text", "")
                            if text:
                                yield f"data: {json.dumps({'text': text})}\n\n"
                    buffer = ""
                except json.JSONDecodeError:
                    break


async def _error_stream(message):
    yield f"data: {json.dumps({'error': message})}\n\n"
    yield f"data: {json.dumps({'done': True})}\n\n"
