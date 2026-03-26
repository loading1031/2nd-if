import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient

from apps.stories.models import Episode, EpisodePurchase, Work

User = get_user_model()


@pytest.fixture
async def author():
    u = User(email="author@example.com", nickname="작가", wallet_address="0x1234567890abcdef1234567890abcdef12345678")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def buyer():
    u = User(email="buyer@example.com", nickname="독자")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def buyer_client(client, buyer):
    await client.post(
        "/users/htmx/auth/login/",
        {"email": "buyer@example.com", "password": "testpass123"},
    )
    return client


@pytest.fixture
async def author_client(client, author):
    # 별도 클라이언트로 작가 로그인
    c = AsyncClient()
    await c.post(
        "/users/htmx/auth/login/",
        {"email": "author@example.com", "password": "testpass123"},
    )
    return c


@pytest.fixture
async def work(author):
    return await Work.objects.acreate(
        title="유료 작품",
        description="테스트",
        author=author,
        license=Work.License.FREE,
    )


@pytest.fixture
async def paid_episode(work, author):
    return await Episode.objects.acreate(
        work=work,
        episode_number=1,
        title="유료 에피소드",
        content="<p>유료 콘텐츠</p>",
        author=author,
        is_paid=True,
        price=0.5,
    )


@pytest.fixture
async def free_episode(work, author):
    return await Episode.objects.acreate(
        work=work,
        episode_number=2,
        title="무료 에피소드",
        content="<p>무료 콘텐츠</p>",
        author=author,
        is_paid=False,
    )


@pytest.mark.django_db(transaction=True)
class TestPaidEpisodeRequiresWallet:
    """지갑 미등록 작가는 유료 에피소드를 만들 수 없다."""

    async def test_paid_episode_without_wallet_rejected(self, client):
        """지갑 없는 작가가 유료 에피소드 생성 시 에러."""
        no_wallet = User(email="nowallet@test.com", nickname="무지갑")
        no_wallet.set_password("testpass123")
        await no_wallet.asave()

        c = AsyncClient()
        await c.post("/users/htmx/auth/login/", {"email": "nowallet@test.com", "password": "testpass123"})

        w = await Work.objects.acreate(title="작품", author=no_wallet, license=Work.License.FREE)
        response = await c.post(
            f"/stories/htmx/{w.pk}/episodes/create/",
            {"title": "유료화", "content": "<p>내용</p>", "is_paid": "on", "price": "1.00"},
        )
        assert response.status_code == 400
        assert not await Episode.objects.filter(work=w, is_paid=True).aexists()

    async def test_paid_episode_with_wallet_allowed(self, author_client, work):
        """지갑 있는 작가는 유료 에피소드 생성 가능."""
        response = await author_client.post(
            f"/stories/htmx/{work.pk}/episodes/create/",
            {"title": "유료화", "content": "<p>내용</p>", "is_paid": "on", "price": "1.00"},
        )
        # Neo4j 없으면 에러나지만, 지갑 검증은 통과해야 함
        assert response.status_code != 400 or b"\xec\xa7\x80\xea\xb0\x91" not in response.content

    async def test_free_episode_without_wallet_allowed(self, client):
        """지갑 없어도 무료 에피소드는 생성 가능."""
        no_wallet = User(email="nowallet2@test.com", nickname="무지갑2")
        no_wallet.set_password("testpass123")
        await no_wallet.asave()

        c = AsyncClient()
        await c.post("/users/htmx/auth/login/", {"email": "nowallet2@test.com", "password": "testpass123"})

        w = await Work.objects.acreate(title="작품2", author=no_wallet, license=Work.License.FREE)
        response = await c.post(
            f"/stories/htmx/{w.pk}/episodes/create/",
            {"title": "무료화", "content": "<p>내용</p>"},
        )
        # 지갑 관련 에러가 아님
        assert b"\xec\xa7\x80\xea\xb0\x91" not in response.content


@pytest.mark.django_db(transaction=True)
class TestPaymentConfirm:
    async def test_missing_tx_hash(self, buyer_client, work, paid_episode):
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/pay/",
            {"tx_hash": "", "token": "USDC"},
        )
        assert response.status_code == 400

    async def test_invalid_token(self, buyer_client, work, paid_episode):
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/pay/",
            {"tx_hash": "0x" + "a" * 64, "token": "ETH"},
        )
        assert response.status_code == 400

    async def test_invalid_tx_hash_format(self, buyer_client, work, paid_episode):
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/pay/",
            {"tx_hash": "invalid", "token": "USDC"},
        )
        assert response.status_code == 400

    async def test_free_episode_payment(self, buyer_client, work, free_episode):
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/2/pay/",
            {"tx_hash": "0x" + "a" * 64, "token": "USDC"},
        )
        assert response.status_code == 400

    async def test_requires_login(self, client, work, paid_episode):
        response = await client.post(
            f"/stories/htmx/{work.pk}/episodes/1/pay/",
            {"tx_hash": "0x" + "a" * 64, "token": "USDC"},
        )
        assert response.status_code == 302

    async def test_duplicate_purchase(self, buyer_client, work, paid_episode, buyer):
        # 기존 구매 기록 생성
        await EpisodePurchase.objects.acreate(
            episode=paid_episode,
            buyer=buyer,
            tx_hash="0x" + "b" * 64,
            token="USDC",
            amount=0.5,
            confirmed=True,
        )
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/pay/",
            {"tx_hash": "0x" + "a" * 64, "token": "USDC"},
        )
        assert response.status_code == 400

    async def test_reused_tx_hash(self, buyer_client, work, paid_episode, author):
        # 다른 에피소드에서 같은 tx_hash 사용
        other_ep = await Episode.objects.acreate(
            work=work,
            episode_number=3,
            title="다른 에피소드",
            content="<p>내용</p>",
            author=author,
            is_paid=True,
            price=0.5,
        )
        await EpisodePurchase.objects.acreate(
            episode=other_ep,
            buyer=author,
            tx_hash="0x" + "c" * 64,
            token="USDC",
            amount=0.5,
            confirmed=True,
        )
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/1/pay/",
            {"tx_hash": "0x" + "c" * 64, "token": "USDC"},
        )
        assert response.status_code == 400

    async def test_episode_not_found(self, buyer_client, work):
        response = await buyer_client.post(
            f"/stories/htmx/{work.pk}/episodes/999/pay/",
            {"tx_hash": "0x" + "a" * 64, "token": "USDC"},
        )
        assert response.status_code == 404


@pytest.mark.django_db(transaction=True)
class TestWalletSettings:
    async def test_wallet_page_requires_login(self, client):
        response = await client.get("/users/wallet/")
        assert response.status_code == 302

    async def test_wallet_page_loads(self, author_client):
        response = await author_client.get("/users/wallet/")
        assert response.status_code == 200

    async def test_save_valid_wallet(self, author_client):
        response = await author_client.post(
            "/users/htmx/wallet/save/",
            {"wallet_address": "0xAbCdEf1234567890AbCdEf1234567890AbCdEf12"},
        )
        assert response.status_code == 200
        user = await User.objects.aget(email="author@example.com")
        assert user.wallet_address == "0xAbCdEf1234567890AbCdEf1234567890AbCdEf12"

    async def test_save_invalid_wallet(self, author_client):
        response = await author_client.post(
            "/users/htmx/wallet/save/",
            {"wallet_address": "not-a-wallet"},
        )
        assert response.status_code == 400

    async def test_save_short_wallet(self, author_client):
        response = await author_client.post(
            "/users/htmx/wallet/save/",
            {"wallet_address": "0x1234"},
        )
        assert response.status_code == 400

    async def test_clear_wallet(self, author_client):
        response = await author_client.post(
            "/users/htmx/wallet/save/",
            {"wallet_address": ""},
        )
        assert response.status_code == 200
        user = await User.objects.aget(email="author@example.com")
        assert user.wallet_address == ""

    async def test_save_wallet_requires_login(self, client):
        response = await client.post(
            "/users/htmx/wallet/save/",
            {"wallet_address": "0x1234567890abcdef1234567890abcdef12345678"},
        )
        assert response.status_code == 302


@pytest.mark.django_db(transaction=True)
class TestEpisodeAccessControl:
    """유료 에피소드 열람 제어 테스트."""

    async def test_free_episode_accessible(self, client, work, free_episode):
        """무료 에피소드는 누구나 읽을 수 있다."""
        response = await client.get(f"/stories/htmx/{work.pk}/episodes/2/")
        assert response.status_code == 200
        assert b"<p>" in response.content  # 본문 HTML 포함

    async def test_paid_episode_blocked_without_purchase(self, buyer_client, work, paid_episode):
        """미구매 유료 에피소드는 본문 대신 결제 안내를 표시한다."""
        response = await buyer_client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        assert response.status_code == 200
        assert b"payment" in response.content or b"\xea\xb2\xb0\xec\xa0\x9c" in response.content  # "결제" 포함

    async def test_paid_episode_accessible_after_purchase(self, buyer_client, work, paid_episode, buyer):
        """구매한 유료 에피소드는 본문을 볼 수 있다."""
        await EpisodePurchase.objects.acreate(
            episode=paid_episode,
            buyer=buyer,
            tx_hash="0x" + "a" * 64,
            token="USDC",
            amount=0.5,
            confirmed=True,
        )
        response = await buyer_client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        assert response.status_code == 200
        # 워터마크(zero-width chars)가 삽입되어 있어도 <p> 태그로 본문 존재 확인
        assert b"<p>" in response.content
        assert "결제" not in response.content.decode()

    async def test_paid_episode_accessible_by_author(self, author_client, work, paid_episode):
        """작가 본인은 구매 없이 유료 에피소드를 볼 수 있다."""
        response = await author_client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        assert response.status_code == 200
        assert b"<p>" in response.content
        assert "결제" not in response.content.decode()

    async def test_paid_episode_anonymous_blocked(self, client, work, paid_episode):
        """비로그인 사용자는 유료 에피소드 본문을 볼 수 없다."""
        response = await client.get(f"/stories/htmx/{work.pk}/episodes/1/")
        assert response.status_code == 200
        assert "유료 콘텐츠" not in response.content.decode()


@pytest.mark.django_db(transaction=True)
class TestEpisodePurchaseModel:
    async def test_create_purchase(self, paid_episode, buyer):
        purchase = await EpisodePurchase.objects.acreate(
            episode=paid_episode,
            buyer=buyer,
            tx_hash="0x" + "d" * 64,
            token="USDC",
            amount=0.5,
            confirmed=True,
        )
        assert purchase.pk is not None
        assert purchase.token == "USDC"

    async def test_unique_episode_buyer(self, paid_episode, buyer):
        await EpisodePurchase.objects.acreate(
            episode=paid_episode,
            buyer=buyer,
            tx_hash="0x" + "e" * 64,
            token="USDC",
            amount=0.5,
        )
        from django.db import IntegrityError

        with pytest.raises(IntegrityError):
            await EpisodePurchase.objects.acreate(
                episode=paid_episode,
                buyer=buyer,
                tx_hash="0x" + "f" * 64,
                token="USDT",
                amount=0.5,
            )

    async def test_unique_tx_hash(self, paid_episode, buyer, author):
        await EpisodePurchase.objects.acreate(
            episode=paid_episode,
            buyer=buyer,
            tx_hash="0x" + "a" * 64,
            token="USDC",
            amount=0.5,
        )
        from django.db import IntegrityError

        other_ep = await Episode.objects.acreate(
            work=paid_episode.work,
            episode_number=10,
            title="다른",
            content="<p>t</p>",
            author=author,
        )
        with pytest.raises(IntegrityError):
            await EpisodePurchase.objects.acreate(
                episode=other_ep,
                buyer=author,
                tx_hash="0x" + "a" * 64,
                token="USDC",
                amount=0.5,
            )
