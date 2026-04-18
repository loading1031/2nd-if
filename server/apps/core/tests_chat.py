"""
CS 1:1 채팅 E2E 테스트.

TDD 방식 — 아직 모델/뷰/URL이 구현되지 않은 상태에서 먼저 작성.
Django AsyncClient 기반 HTTP 레벨 테스트.
"""

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test import AsyncClient

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def user():
    """일반 사용자 생성."""
    return await sync_to_async(User.objects.create_user)(
        email="csuser@example.com",
        password="testpass123",
        nickname="CS테스터",
    )


@pytest.fixture()
async def admin_user():
    """관리자(staff) 사용자 생성."""
    return await sync_to_async(User.objects.create_user)(
        email="csadmin@example.com",
        password="adminpass123",
        nickname="CS관리자",
        is_staff=True,
    )


@pytest.fixture()
async def logged_in_client(user):
    """로그인된 일반 사용자 AsyncClient."""
    client = AsyncClient()
    logged_in = await sync_to_async(client.login)(email="csuser@example.com", password="testpass123")
    assert logged_in, "일반 사용자 로그인 실패"
    return client


@pytest.fixture()
async def admin_client(admin_user):
    """로그인된 관리자 AsyncClient."""
    client = AsyncClient()
    logged_in = await sync_to_async(client.login)(email="csadmin@example.com", password="adminpass123")
    assert logged_in, "관리자 사용자 로그인 실패"
    return client


# ---------------------------------------------------------------------------
# 1. 미로그인 사용자 → /cs/ 접근 → 로그인 리다이렉트
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_cs_page_requires_login():
    """미로그인 상태에서 /cs/ 접근 시 로그인 페이지로 리다이렉트."""
    client = AsyncClient()
    response = await client.get("/cs/")

    assert response.status_code == 302
    assert "/users/login/" in response["Location"]


# ---------------------------------------------------------------------------
# 2. 로그인 사용자 → /cs/ 접근 → 채팅 페이지 표시
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_cs_page_shows_chat(logged_in_client):
    """로그인 후 /cs/ 접근 시 채팅 페이지 200 응답 및 주요 요소 표시."""
    response = await logged_in_client.get("/cs/")

    assert response.status_code == 200

    content = response.content.decode()
    assert "고객 상담" in content
    # 메시지 입력 폼 존재 확인
    assert "<form" in content or "hx-post" in content


# ---------------------------------------------------------------------------
# 3. 사용자 메시지 전송 → DB 저장
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_user_send_message(logged_in_client, user):
    """사용자가 메시지를 전송하면 ChatMessage가 DB에 저장된다."""
    response = await logged_in_client.post(
        "/cs/send/",
        {"content": "테스트 메시지"},
        HTTP_HX_REQUEST="true",
    )

    # 성공 응답 (200 또는 201)
    assert response.status_code in (200, 201)

    # DB에서 메시지 확인 (모델 import는 함수 내부)
    from apps.core.models import ChatMessage, ChatRoom

    # ChatRoom 자동 생성 확인
    room_exists = await ChatRoom.objects.filter(user=user).aexists()
    assert room_exists, "ChatRoom이 자동 생성되지 않았습니다."

    # ChatMessage 생성 확인
    msg = await ChatMessage.objects.filter(room__user=user, content="테스트 메시지").afirst()
    assert msg is not None, "ChatMessage가 저장되지 않았습니다."
    assert msg.is_admin is False


# ---------------------------------------------------------------------------
# 4. 관리자 → /cs/admin/ → 대화방 목록 표시
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_admin_room_list(admin_client, logged_in_client, user):
    """관리자가 /cs/admin/ 접근 시 대화방 목록을 확인할 수 있다."""
    # 사용자가 먼저 메시지를 보내서 대화방 생성
    await logged_in_client.post(
        "/cs/send/",
        {"content": "도움이 필요합니다"},
        HTTP_HX_REQUEST="true",
    )

    response = await admin_client.get("/cs/admin/")

    assert response.status_code == 200

    content = response.content.decode()
    # 사용자 닉네임 또는 이메일이 목록에 표시
    assert "CS테스터" in content or "csuser@example.com" in content


# ---------------------------------------------------------------------------
# 5. 관리자 → 대화방 진입 → 답변 전송
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_admin_reply_message(admin_client, logged_in_client, user):
    """관리자가 대화방에서 답변을 전송하면 is_admin=True로 저장된다."""
    # 사용자가 먼저 메시지를 보내서 대화방 생성
    await logged_in_client.post(
        "/cs/send/",
        {"content": "문의합니다"},
        HTTP_HX_REQUEST="true",
    )

    from apps.core.models import ChatRoom

    room = await ChatRoom.objects.filter(user=user).afirst()
    assert room is not None, "ChatRoom이 생성되지 않았습니다."

    # 관리자 대화방 페이지 접근
    response = await admin_client.get(f"/cs/admin/{room.pk}/")
    assert response.status_code == 200

    # 관리자 답변 전송
    response = await admin_client.post(
        f"/cs/admin/{room.pk}/send/",
        {"content": "답변입니다"},
        HTTP_HX_REQUEST="true",
    )
    assert response.status_code in (200, 201)

    # DB에서 관리자 메시지 확인
    from apps.core.models import ChatMessage

    admin_msg = await ChatMessage.objects.filter(room=room, content="답변입니다").afirst()
    assert admin_msg is not None, "관리자 ChatMessage가 저장되지 않았습니다."
    assert admin_msg.is_admin is True


# ---------------------------------------------------------------------------
# 6. 비staff 사용자 → /cs/admin/ 접근 → 403 또는 리다이렉트
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_non_staff_cannot_access_admin(logged_in_client):
    """일반 사용자가 /cs/admin/ 접근 시 403 또는 로그인 리다이렉트."""
    response = await logged_in_client.get("/cs/admin/")

    # 403 Forbidden 또는 302 리다이렉트(login 페이지)
    assert response.status_code in (302, 403)

    if response.status_code == 302:
        assert "/users/login/" in response["Location"]
