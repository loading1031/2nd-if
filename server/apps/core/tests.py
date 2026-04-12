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


# ──────────────────────────────────────────────
# ChatRoom / ChatMessage 모델 Unit 테스트 (TDD)
# ──────────────────────────────────────────────


@pytest.fixture
def chat_user(db):
    return User.objects.create_user(email="chatuser@example.com", password="testpass123", nickname="채팅유저")


@pytest.fixture
def chat_admin_user(db):
    return User.objects.create_user(
        email="chatadmin@example.com",
        password="adminpass123",
        nickname="관리자",
        is_staff=True,
    )


@pytest.fixture
def chat_room(chat_user):
    from apps.core.models import ChatRoom

    return ChatRoom.objects.create(user=chat_user)


# === ChatRoom 테스트 ===


class TestChatRoom:
    """ChatRoom 모델 테스트"""

    @pytest.mark.django_db
    def test_create_chat_room(self, chat_user):
        """사용자의 채팅방을 생성할 수 있다."""
        from apps.core.models import ChatRoom

        room = ChatRoom.objects.create(user=chat_user)
        assert room.pk is not None
        assert room.user == chat_user
        assert room.status == "open"

    @pytest.mark.django_db
    def test_chat_room_unique_per_user(self, chat_user, chat_room):
        """사용자당 채팅방은 1개만 존재할 수 있다."""
        from django.db import IntegrityError

        from apps.core.models import ChatRoom

        with pytest.raises(IntegrityError):
            ChatRoom.objects.create(user=chat_user)

    @pytest.mark.django_db
    def test_chat_room_default_status(self, chat_room):
        """채팅방 기본 상태는 open이다."""
        assert chat_room.status == "open"

    @pytest.mark.django_db
    def test_chat_room_status_change(self, chat_room):
        """채팅방 상태를 변경할 수 있다."""
        chat_room.status = "resolved"
        chat_room.save()
        chat_room.refresh_from_db()
        assert chat_room.status == "resolved"


# === ChatMessage 테스트 ===


class TestChatMessage:
    """ChatMessage 모델 테스트"""

    @pytest.mark.django_db
    def test_create_user_message(self, chat_user, chat_room):
        """사용자 메시지를 생성할 수 있다."""
        from apps.core.models import ChatMessage

        msg = ChatMessage.objects.create(
            room=chat_room,
            sender=chat_user,
            is_admin=False,
            content="로그인이 안됩니다",
        )
        assert msg.pk is not None
        assert msg.is_admin is False
        assert msg.is_read is False

    @pytest.mark.django_db
    def test_create_admin_message(self, chat_admin_user, chat_room):
        """관리자 메시지를 생성할 수 있다."""
        from apps.core.models import ChatMessage

        msg = ChatMessage.objects.create(
            room=chat_room,
            sender=chat_admin_user,
            is_admin=True,
            content="확인해보겠습니다.",
        )
        assert msg.is_admin is True

    @pytest.mark.django_db
    def test_message_ordering(self, chat_user, chat_admin_user, chat_room):
        """메시지는 생성 순서대로 정렬된다."""
        from apps.core.models import ChatMessage

        msg1 = ChatMessage.objects.create(room=chat_room, sender=chat_user, content="질문1")
        msg2 = ChatMessage.objects.create(
            room=chat_room,
            sender=chat_admin_user,
            is_admin=True,
            content="답변1",
        )
        msg3 = ChatMessage.objects.create(room=chat_room, sender=chat_user, content="질문2")
        messages = list(chat_room.messages.order_by("created_at"))
        assert messages == [msg1, msg2, msg3]

    @pytest.mark.django_db
    def test_unread_count(self, chat_user, chat_admin_user, chat_room):
        """미읽음 메시지 수를 카운트할 수 있다."""
        from apps.core.models import ChatMessage

        ChatMessage.objects.create(
            room=chat_room,
            sender=chat_admin_user,
            is_admin=True,
            content="답변1",
            is_read=False,
        )
        ChatMessage.objects.create(
            room=chat_room,
            sender=chat_admin_user,
            is_admin=True,
            content="답변2",
            is_read=False,
        )
        ChatMessage.objects.create(
            room=chat_room,
            sender=chat_admin_user,
            is_admin=True,
            content="답변3",
            is_read=True,
        )
        unread = chat_room.messages.filter(is_admin=True, is_read=False).count()
        assert unread == 2

    @pytest.mark.django_db
    def test_message_cascade_delete(self, chat_user, chat_room):
        """채팅방 삭제 시 메시지도 삭제된다."""
        from apps.core.models import ChatMessage

        ChatMessage.objects.create(room=chat_room, sender=chat_user, content="테스트")
        room_id = chat_room.pk
        chat_room.delete()
        assert ChatMessage.objects.filter(room_id=room_id).count() == 0
