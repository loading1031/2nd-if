"""동적 텍스트 리더 E2E 테스트."""

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test import AsyncClient

from apps.stories.models import Episode, Work

User = get_user_model()


@pytest.fixture
async def reader_user():
    u = User(email="reader@example.com", nickname="독자")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def reader_client(reader_user):
    client = AsyncClient()
    await sync_to_async(client.login)(email="reader@example.com", password="testpass123")
    return client


@pytest.fixture
async def fx_episode(reader_user):
    work = await Work.objects.acreate(
        title="효과 테스트 작품",
        description="테스트",
        author=reader_user,
        license=Work.License.FREE,
    )
    return await Episode.objects.acreate(
        work=work,
        episode_number=1,
        title="효과 테스트 화",
        content='<p data-fx="shake">쾅!</p><p data-fx="fade-in">눈을 떴다</p><p>일반 텍스트</p>',
        author=reader_user,
    )


@pytest.mark.django_db(transaction=True)
class TestDynamicReaderPage:
    """에피소드 리더에서 data-fx가 포함된 HTML이 렌더링되는지 테스트."""

    async def test_fx_content_rendered(self, reader_client, fx_episode):
        """에피소드 리더에서 data-fx 속성이 포함된 HTML이 반환된다."""
        work_id = fx_episode.work_id
        response = await reader_client.get(f"/stories/htmx/{work_id}/episodes/{fx_episode.episode_number}/")
        content = response.content.decode()
        assert 'data-fx="shake"' in content
        assert 'data-fx="fade-in"' in content

    async def test_normal_text_unaffected(self, reader_client, fx_episode):
        """data-fx가 없는 텍스트는 그대로 표시된다."""
        work_id = fx_episode.work_id
        response = await reader_client.get(f"/stories/htmx/{work_id}/episodes/{fx_episode.episode_number}/")
        content = response.content.decode()
        assert "일반 텍스트" in content

    async def test_reader_fx_js_loaded(self, reader_client, fx_episode):
        """에피소드 리더 페이지에 reader-fx.js가 로드된다."""
        work_id = fx_episode.work_id
        response = await reader_client.get(f"/stories/{work_id}/episodes/{fx_episode.episode_number}/")
        content = response.content.decode()
        assert "reader-fx" in content or "reader_fx" in content
