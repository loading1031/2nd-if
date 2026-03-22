import json
import os
from unittest.mock import AsyncMock, patch

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient

User = get_user_model()


@pytest.fixture
async def client():
    return AsyncClient()


@pytest.fixture
async def user():
    u = User(email="cs@example.com", nickname="CS유저")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def auth_client(client, user):
    """로그인된 클라이언트 — 실제 로그인 API 호출."""
    await client.post(
        "/users/htmx/auth/login/",
        {"email": "cs@example.com", "password": "testpass123"},
    )
    return client


@pytest.mark.django_db(transaction=True)
class TestCsChatPage:
    """CS 채팅 페이지 접근 테스트."""

    async def test_page_requires_login(self, client):
        """미로그인 → 로그인 페이지로 리다이렉트."""
        response = await client.get("/cs/")
        assert response.status_code == 302
        assert "/users/login/" in response["Location"]

    async def test_page_accessible_when_logged_in(self, auth_client):
        """로그인 → 페이지 정상 접근."""
        response = await auth_client.get("/cs/")
        assert response.status_code == 200
        assert "고객 상담" in response.content.decode()

    async def test_page_has_chat_ui(self, auth_client):
        """페이지에 채팅 UI 요소 존재."""
        response = await auth_client.get("/cs/")
        content = response.content.decode()
        assert 'id="chat-messages"' in content
        assert 'id="chat-form"' in content
        assert 'id="chat-input"' in content


@pytest.mark.django_db(transaction=True)
class TestCsChatSend:
    """CS 채팅 메시지 전송 테스트."""

    async def test_send_requires_login(self, client):
        """미로그인 → 리다이렉트."""
        response = await client.post(
            "/cs/chat/",
            json.dumps({"query": "테스트"}),
            content_type="application/json",
        )
        assert response.status_code == 302

    async def test_send_rejects_get(self, auth_client):
        """GET 메서드 → 405."""
        response = await auth_client.get("/cs/chat/")
        assert response.status_code == 405

    @patch("apps.core.views.async_views.httpx.AsyncClient")
    async def test_send_returns_sse(self, mock_client_cls, auth_client):
        """정상 요청 → SSE 스트리밍 응답."""
        mock_response = AsyncMock()
        mock_response.aiter_lines = lambda: _async_iter(
            [
                'data: {"event": "message", "answer": "안녕하세요", "conversation_id": "conv-1"}',
                'data: {"event": "message_end", "conversation_id": "conv-1"}',
            ]
        )
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=False)

        mock_instance = AsyncMock()
        mock_instance.stream = AsyncMock(return_value=mock_response)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=False)
        mock_client_cls.return_value = mock_instance

        response = await auth_client.post(
            "/cs/chat/",
            json.dumps({"query": "로그인이 안돼"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response["Content-Type"] == "text/event-stream"


async def _async_iter(items):
    """리스트를 async iterator로 변환."""
    for item in items:
        yield item
