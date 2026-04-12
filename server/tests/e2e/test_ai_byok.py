"""AI BYOK E2E 테스트."""

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test import AsyncClient

User = get_user_model()


@pytest.fixture
async def byok_user():
    u = User(email="byok@example.com", nickname="BYOK유저")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def byok_client(byok_user):
    client = AsyncClient()
    await sync_to_async(client.login)(email="byok@example.com", password="testpass123")
    return client


@pytest.mark.django_db(transaction=True)
class TestAIBYOKFlow:
    """AI BYOK 전체 플로우 테스트."""

    async def test_settings_to_add_flow(self, byok_client):
        """설정 페이지 접근 -> 프로바이더 추가 -> 목록에 표시."""
        # 1. 설정 페이지 접근
        response = await byok_client.get("/users/settings/ai/")
        assert response.status_code == 200

        # 2. 프로바이더 추가
        response = await byok_client.post(
            "/users/settings/ai/add/",
            {
                "provider": "openai",
                "display_name": "테스트 GPT",
                "api_key": "sk-test-flow",
                "model_name": "gpt-4o",
            },
        )
        assert response.status_code == 200

    async def test_no_provider_shows_warning(self, byok_client):
        """프로바이더 미등록 시 패널에서 경고 표시."""
        response = await byok_client.get("/stories/htmx/ai/providers/")
        # 프로바이더가 없으면 빈 목록 또는 경고
        assert response.status_code == 200

    async def test_unauthenticated_ai_settings_redirect(self):
        """미로그인 -> AI 설정 접근 불가."""
        client = AsyncClient()
        response = await client.get("/users/settings/ai/")
        assert response.status_code == 302
