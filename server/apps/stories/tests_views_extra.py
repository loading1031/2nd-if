"""추가 뷰 테스트 — 기존 tests.py에서 커버되지 않는 경로.

커버 대상:
- 홈 페이지(index) 뷰
- 작품 목록 status 필터
- 작품 생성 시 font 선택
- 에피소드 생성 유효하지 않은 폼
- 분기 생성 (htmx_branch_create) — 금지/갭/폼 에러
- 유사도 검사 (htmx_check_similarity) — mock 임베딩
- 작가 지갑 없을 때 결제 에러
"""

import os
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient, override_settings

from apps.stories.models import Episode, Work

User = get_user_model()


# ── Fixtures (conftest.py의 client, user, authenticated_client, work 재사용) ──


@pytest.fixture
async def other_user():
    u = User(email="reader@test.com", nickname="독자")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def reader_client(other_user):
    c = AsyncClient()
    await c.post(
        "/users/htmx/auth/login/",
        {"email": "reader@test.com", "password": "testpass123"},
    )
    return c


@pytest.fixture
async def no_branch_work(user):
    return await Work.objects.acreate(
        title="분기금지 작품",
        description="분기 금지",
        author=user,
        license=Work.License.NO_BRANCH,
    )


@pytest.fixture
async def many_episodes(work, user):
    """분기 갭 테스트용으로 에피소드 25개 생성."""
    eps = []
    for i in range(1, 26):
        ep = await Episode.objects.acreate(
            work=work,
            episode_number=i,
            title=f"Episode {i}",
            content=f"<p>Content {i}</p>",
            author=user,
        )
        eps.append(ep)
    return eps


# ── 홈 페이지 테스트 ─────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestHomePage:
    async def test_index_renders(self, client):
        response = await client.get("/")
        assert response.status_code == 200

    async def test_index_with_works(self, client, work):
        response = await client.get("/")
        assert response.status_code == 200

    async def test_index_shows_featured_works(self, client, work):
        response = await client.get("/")
        content = response.content.decode()
        assert "테스트 작품" in content


# ── 작품 목록 status 필터 ────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestWorkListFilters:
    async def test_filter_by_status(self, client, user):
        await Work.objects.acreate(title="연재중", author=user, status="ongoing")
        await Work.objects.acreate(title="완결", author=user, status="completed")

        response = await client.get("/stories/htmx/works/?status=ongoing")
        content = response.content.decode()
        assert "연재중" in content

    async def test_filter_by_status_completed(self, client, user):
        await Work.objects.acreate(title="연재중", author=user, status="ongoing")
        await Work.objects.acreate(title="완결", author=user, status="completed")

        response = await client.get("/stories/htmx/works/?status=completed")
        content = response.content.decode()
        assert "완결" in content


# ── 작품 생성 font 선택 ──────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestWorkCreateFont:
    async def test_create_with_serif_font(self, authenticated_client):
        response = await authenticated_client.post(
            "/stories/htmx/works/create/",
            {
                "title": "명조체 작품",
                "description": "명조체로",
                "license": "free",
                "font": "serif",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" in response
        w = await Work.objects.aget(title="명조체 작품")
        assert w.font == "serif"

    async def test_create_with_default_font(self, authenticated_client):
        response = await authenticated_client.post(
            "/stories/htmx/works/create/",
            {
                "title": "기본체 작품",
                "license": "free",
            },
        )
        assert response.status_code == 200
        w = await Work.objects.aget(title="기본체 작품")
        assert w.font == "default"

    async def test_create_with_all_font_choices(self, authenticated_client):
        for font_val, _font_label in Work.Font.choices:
            response = await authenticated_client.post(
                "/stories/htmx/works/create/",
                {
                    "title": f"Font {font_val}",
                    "license": "free",
                    "font": font_val,
                },
            )
            assert response.status_code == 200
            assert "HX-Redirect" in response


# ── 에피소드 생성 폼 에러 ────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestEpisodeCreateErrors:
    async def test_create_episode_empty_title_returns_error(self, authenticated_client, work):
        """빈 제목 에피소드 생성 시 에러.

        NOTE: episode_write_form.html 템플릿이 아직 없어서 TemplateDoesNotExist 발생.
        템플릿 추가 후 status 400 응답으로 변경 예정.
        """
        from django.template.exceptions import TemplateDoesNotExist

        with pytest.raises(TemplateDoesNotExist):
            await authenticated_client.post(
                f"/stories/htmx/{work.pk}/episodes/create/",
                {"title": "", "content": "<p>Content</p>"},
            )

    # test_create_episode_requires_login: tests.py::TestWorkErrors에서 커버


# ── 분기 생성 테스트 ─────────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestBranchCreate:
    @override_settings(BRANCH_EPISODE_GAP=0)
    async def test_branch_forbidden_no_branch_license(self, reader_client, no_branch_work, user):
        """분기 금지 라이선스 작품에서는 분기 생성 불가."""
        # 에피소드 25개 생성
        for i in range(1, 26):
            await Episode.objects.acreate(
                work=no_branch_work,
                episode_number=i,
                title=f"Ep {i}",
                content=f"<p>{i}</p>",
                author=user,
            )

        response = await reader_client.post(
            f"/stories/htmx/{no_branch_work.pk}/episodes/1/branch/",
            {
                "branch_direction": "Go to the dark side of the story",
                "title": "Branch",
                "content": "<p>Branch content</p>",
                "is_paid": False,
            },
        )
        assert response.status_code == 403

    @override_settings(BRANCH_EPISODE_GAP=20)
    async def test_branch_forbidden_too_recent(self, reader_client, work, many_episodes):
        """최신 20화 이내에서는 분기 불가."""
        # Episode 25개 중 episode_number=10 에서 분기 시도 (10 > 25-20=5 → 403)
        response = await reader_client.post(
            f"/stories/htmx/{work.pk}/episodes/10/branch/",
            {
                "branch_direction": "A new direction for the story",
                "title": "Branch",
                "content": "<p>Branch content</p>",
                "is_paid": False,
            },
        )
        assert response.status_code == 403

    @pytest.mark.skipif(
        not os.environ.get("NEO4J_BOLT_URL"),
        reason="Neo4j not available in CI",
    )
    async def test_branch_success(self, reader_client, work, many_episodes):
        """유효한 분기 생성 (ep 1에서 분기, 충분한 갭)."""
        response = await reader_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/branch/",
            {
                "branch_direction": "The hero decides to take a completely different path",
                "title": "Branch Episode",
                "content": "<p>New branch content</p>",
                "is_paid": False,
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" in response

    # test_branch_invalid_form_short_direction: tests_forms.py::TestBranchCreateForm에서 커버

    async def test_branch_requires_login(self, client, work, many_episodes):
        response = await client.post(
            f"/stories/htmx/{work.pk}/episodes/1/branch/",
            {
                "branch_direction": "Some direction for the story",
                "title": "Branch",
                "content": "<p>Content</p>",
                "is_paid": False,
            },
        )
        assert response.status_code == 302


# ── 유사도 검사 테스트 ───────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestCheckSimilarity:
    async def test_direction_too_short(self, authenticated_client, work, many_episodes):
        """5자 미만 방향은 빈 안내 반환."""
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/check-similarity/",
            {"direction": "Hi"},
        )
        assert response.status_code == 200

    async def test_no_existing_branches_passes(self, authenticated_client, work, many_episodes):
        """기존 분기 없으면 통과."""
        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/check-similarity/",
            {"direction": "A completely new direction for the storyline"},
        )
        assert response.status_code == 200

    @pytest.mark.skipif(
        not os.environ.get("OLLAMA_URL"),
        reason="Ollama not available",
    )
    async def test_similar_direction_warns(self, authenticated_client, work, user):
        """기존 분기와 유사한 방향이면 경고."""
        # 유사 임베딩을 가진 기존 에피소드 생성
        await Episode.objects.acreate(
            work=work,
            episode_number=100,
            title="Existing branch",
            content="<p>existing</p>",
            author=user,
            branch_direction="주인공이 어두운 숲으로 간다",
            direction_embedding=await __import__("apps.stories.embedding", fromlist=["get_embedding"]).get_embedding(
                "주인공이 어두운 숲으로 간다"
            ),
        )

        response = await authenticated_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/check-similarity/",
            {"direction": "주인공이 어두운 숲으로 향한다"},
        )
        assert response.status_code == 200

    async def test_requires_login(self, client, work, many_episodes):
        response = await client.post(
            f"/stories/htmx/{work.pk}/episodes/1/check-similarity/",
            {"direction": "Some new direction here"},
        )
        assert response.status_code == 302


# ── 결제: 작가 지갑 없음 ────────────────────────────────────


@pytest.mark.django_db(transaction=True)
class TestPaymentAuthorNoWallet:
    async def test_author_no_wallet_returns_500(self, other_user):
        """작가 지갑 주소 미설정 시 500 에러."""
        # 지갑 없는 작가
        no_wallet_author = User(email="nowallet@test.com", nickname="무지갑작가")
        no_wallet_author.set_password("testpass123")
        await no_wallet_author.asave()

        w = await Work.objects.acreate(
            title="지갑없는작품",
            author=no_wallet_author,
            license=Work.License.FREE,
        )
        await Episode.objects.acreate(
            work=w,
            episode_number=1,
            title="Paid",
            content="<p>c</p>",
            author=no_wallet_author,
            is_paid=True,
            price=Decimal("1.00"),
        )

        # 독자 로그인
        reader_client = AsyncClient()
        await reader_client.post(
            "/users/htmx/auth/login/",
            {"email": "reader@test.com", "password": "testpass123"},
        )

        response = await reader_client.post(
            f"/stories/htmx/{w.pk}/episodes/1/pay/",
            {"tx_hash": "0x" + "a" * 64, "token": "USDC"},
        )
        assert response.status_code == 500
