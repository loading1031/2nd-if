import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient

from apps.stories.models import Episode, EpisodePurchase, Work

User = get_user_model()


@pytest.fixture
async def client():
    return AsyncClient()


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
