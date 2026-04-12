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
        response = await authenticated_client.post(
            "/stories/htmx/works/create/",
            {
                "title": "새 작품",
                "description": "새 작품 소개",
                "license": "free",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" in response
        assert await Work.objects.filter(title="새 작품").aexists()

    async def test_work_create_requires_login(self, client):
        response = await client.post(
            "/stories/htmx/works/create/",
            {
                "title": "새 작품",
                "license": "free",
            },
        )
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

    @pytest.mark.skipif(
        not __import__("os").environ.get("NEO4J_BOLT_URL"),
        reason="Neo4j not available in CI",
    )
    async def test_episode_create(self, authenticated_client, work):
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/create/",
            {
                "title": "새 에피소드",
            },
        )
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

    async def test_rate_zero(self, authenticated_client, work, episodes):
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/rate/",
            {"score": "0"},
        )
        assert response.status_code == 400

    async def test_rate_requires_login(self, client, work, episodes):
        response = await client.post(
            f"/stories/htmx/{work.pk}/episodes/1/rate/",
            {"score": "4"},
        )
        assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
class TestWorkErrors:
    async def test_work_create_empty_title(self, authenticated_client):
        response = await authenticated_client.post(
            "/stories/htmx/works/create/",
            {
                "title": "",
                "license": "free",
            },
        )
        assert response.status_code == 400

    async def test_work_detail_not_found(self, client):
        response = await client.get("/stories/99999/")
        assert response.status_code == 200  # 페이지는 렌더링, HTMX가 404 처리

    async def test_episode_create_requires_login(self, client, work):
        response = await client.post(
            f"/stories/htmx/{work.pk}/episodes/create/",
            {
                "title": "무단 에피소드",
            },
        )
        assert response.status_code == 302

    async def test_episode_read_not_found(self, client, work):
        response = await client.get(f"/stories/htmx/{work.pk}/episodes/999/")
        assert response.status_code == 404

    async def test_episode_view_count_increments(self, client, work, episodes):
        await client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        await client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        ep = await Episode.objects.aget(work=work, episode_number=1)
        assert ep.view_count == 2


# === 동적 텍스트 리더 Phase 1 테스트 ===


@pytest.mark.django_db(transaction=True)
class TestDynamicReaderSanitize:
    """nh3 새니타이징에서 data-fx 속성이 보존되는지 테스트."""

    def test_data_fx_preserved(self):
        """data-fx 속성이 새니타이징 후 유지된다."""
        from apps.stories.forms import _clean_html_content

        html = '<p data-fx="shake">쾅!</p>'
        result = _clean_html_content(html)
        assert 'data-fx="shake"' in result

    def test_data_delay_preserved(self):
        """data-delay 속성이 새니타이징 후 유지된다."""
        from apps.stories.forms import _clean_html_content

        html = '<p data-fx="fade-in" data-delay="500">천천히</p>'
        result = _clean_html_content(html)
        assert 'data-delay="500"' in result

    def test_all_fx_types_preserved(self):
        """5종 효과 모두 보존된다."""
        from apps.stories.forms import _clean_html_content

        effects = ["shake", "fade-in", "rush", "typewriter", "float"]
        for fx in effects:
            html = f'<p data-fx="{fx}">테스트</p>'
            result = _clean_html_content(html)
            assert f'data-fx="{fx}"' in result, f"{fx} 효과가 새니타이징에서 제거됨"

    def test_invalid_data_attr_stripped(self):
        """허용되지 않은 data 속성은 제거된다."""
        from apps.stories.forms import _clean_html_content

        html = '<p data-fx="shake" data-evil="xss">테스트</p>'
        result = _clean_html_content(html)
        assert "data-evil" not in result

    def test_script_in_data_fx_stripped(self):
        """data-fx에 스크립트 주입 시도는 일반 텍스트로 처리된다."""
        from apps.stories.forms import _clean_html_content

        html = '<p data-fx="shake" onclick="alert(1)">테스트</p>'
        result = _clean_html_content(html)
        assert "onclick" not in result


@pytest.mark.django_db(transaction=True)
class TestDynamicReaderEpisode:
    """에피소드에 data-fx가 포함된 콘텐츠 저장/조회 테스트."""

    async def test_episode_with_fx_content(self, authenticated_client, work):
        """data-fx가 포함된 에피소드를 작성할 수 있다."""
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/create/",
            {
                "title": "효과 테스트 화",
                "content": '<p data-fx="shake">쾅!</p><p data-fx="fade-in">눈을 떴다</p>',
            },
        )
        assert response.status_code == 200
        ep = await Episode.objects.filter(title="효과 테스트 화").afirst()
        assert ep is not None
        assert 'data-fx="shake"' in ep.content
        assert 'data-fx="fade-in"' in ep.content

    async def test_episode_without_fx_unchanged(self, authenticated_client, work):
        """일반 에피소드는 기존과 동일하게 동작한다."""
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/create/",
            {
                "title": "일반 화",
                "content": "<p>일반 텍스트</p>",
            },
        )
        assert response.status_code == 200
        ep = await Episode.objects.filter(title="일반 화").afirst()
        assert ep is not None
        assert "data-fx" not in ep.content
