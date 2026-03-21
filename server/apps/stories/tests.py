import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient

from apps.stories.models import Work, Episode, Rating

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
    await client.post("/users/htmx/auth/login/", {
        "email": "author@example.com",
        "password": "testpass123",
    })
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
            content={"blocks": [{"type": "paragraph", "data": {"text": f"내용 {i}"}}]},
            author=user,
        )
        eps.append(ep)
    return eps


@pytest.mark.django_db(transaction=True)
class TestWorkCRUD:
    async def test_work_list_page(self, client):
        response = await client.get("/stories/")
        assert response.status_code == 200

    async def test_htmx_work_list(self, client, work):
        response = await client.get("/stories/htmx/works/")
        assert response.status_code == 200

    async def test_htmx_work_list_search(self, client, work):
        response = await client.get("/stories/htmx/works/?search=테스트")
        assert response.status_code == 200

    async def test_work_create(self, authenticated_client):
        response = await authenticated_client.post("/stories/htmx/works/create/", {
            "title": "새 작품",
            "description": "새 작품 소개",
            "license": "free",
        })
        assert response.status_code == 200
        assert "HX-Redirect" in response
        assert await Work.objects.filter(title="새 작품").aexists()

    async def test_work_create_requires_login(self, client):
        response = await client.post("/stories/htmx/works/create/", {
            "title": "새 작품",
            "license": "free",
        })
        assert response.status_code == 302  # redirect to login


@pytest.mark.django_db(transaction=True)
class TestEpisodeCRUD:
    async def test_episode_list(self, client, work, episodes):
        response = await client.get(f"/stories/htmx/{work.pk}/episodes/")
        assert response.status_code == 200

    async def test_episode_read(self, client, work, episodes):
        response = await client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        assert response.status_code == 200
        # 조회수 증가 확인
        ep = await Episode.objects.aget(work=work, episode_number=1)
        assert ep.view_count == 1

    async def test_episode_create(self, authenticated_client, work):
        response = await authenticated_client.post(f"/stories/htmx/{work.pk}/episodes/create/", {
            "title": "새 에피소드",
        })
        assert response.status_code == 200
        assert "HX-Redirect" in response
        assert await Episode.objects.filter(work=work, title="새 에피소드").aexists()


@pytest.mark.django_db(transaction=True)
class TestRating:
    async def test_rate_episode(self, authenticated_client, work, episodes):
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/rate/",
            {"score": "4"},
        )
        assert response.status_code == 200
        ep = await Episode.objects.aget(work=work, episode_number=1)
        assert ep.avg_rating == 4.0
        assert ep.rating_count == 1

    async def test_rate_invalid_score(self, authenticated_client, work, episodes):
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/rate/",
            {"score": "6"},
        )
        assert response.status_code == 400

    async def test_rate_update(self, authenticated_client, work, episodes):
        await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/rate/",
            {"score": "3"},
        )
        await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/rate/",
            {"score": "5"},
        )
        ep = await Episode.objects.aget(work=work, episode_number=1)
        assert ep.avg_rating == 5.0  # 같은 유저 업데이트
