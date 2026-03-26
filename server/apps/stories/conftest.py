"""stories 앱 테스트 공용 fixtures."""

import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient

from apps.stories.models import Episode, Work

User = get_user_model()


@pytest.fixture
async def client():
    return AsyncClient()


@pytest.fixture
async def user():
    u = User(email="author@example.com", nickname="작가")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def authenticated_client(client, user):
    await client.post(
        "/users/htmx/auth/login/",
        {
            "email": "author@example.com",
            "password": "testpass123",
        },
    )
    return client


@pytest.fixture
async def work(user):
    return await Work.objects.acreate(
        title="테스트 작품",
        description="테스트 소개",
        author=user,
        license=Work.License.FREE,
    )


@pytest.fixture
async def episodes(work, user):
    eps = []
    for i in range(1, 4):
        ep = await Episode.objects.acreate(
            work=work,
            episode_number=i,
            title=f"테스트 {i}화",
            content=f"<p>내용 {i}</p>",
            author=user,
        )
        eps.append(ep)
    return eps
