import pytest
from django.contrib.auth import get_user_model
from django.test import AsyncClient

User = get_user_model()


@pytest.fixture
async def client():
    return AsyncClient()


@pytest.fixture
async def user():
    u = User(email="fp@example.com", nickname="핑거유저")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.mark.django_db(transaction=True)
class TestFingerprintBlacklist:
    async def test_signup_normal_fingerprint(self, client):
        """시나리오 8: 정상 핑거프린트로 가입."""
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "new@example.com",
                "nickname": "새유저",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
            headers={"X-Fingerprint": "normal-fp-123"},
        )
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/users/login/"

    async def test_login_normal_fingerprint(self, client, user):
        """시나리오 9: 정상 핑거프린트로 로그인."""
        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "fp@example.com",
                "password": "testpass123",
            },
            headers={"X-Fingerprint": "normal-fp-123"},
        )
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/"

    async def test_fingerprint_logged(self, client, user):
        """시나리오 10: 접속 시 FingerprintLog 기록."""
        from apps.users.models import FingerprintLog

        await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "fp@example.com",
                "password": "testpass123",
            },
            headers={"X-Fingerprint": "logged-fp-456"},
        )

        assert await FingerprintLog.objects.filter(fingerprint="logged-fp-456").aexists()

    async def test_signup_blacklisted_fingerprint(self, client):
        """시나리오 11: 블랙리스트 핑거프린트로 가입 거부."""
        from apps.users.models import FingerprintBlacklist

        await FingerprintBlacklist.objects.acreate(
            fingerprint="banned-fp-789",
            reason="테스트 제재",
        )

        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "banned@example.com",
                "nickname": "밴유저",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
            headers={"X-Fingerprint": "banned-fp-789"},
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response  # 가입 실패
        assert not await User.objects.filter(email="banned@example.com").aexists()

    async def test_login_blacklisted_fingerprint(self, client, user):
        """시나리오 12: 블랙리스트 핑거프린트로 로그인 거부."""
        from apps.users.models import FingerprintBlacklist

        await FingerprintBlacklist.objects.acreate(
            fingerprint="banned-fp-login",
            reason="테스트 제재",
        )

        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "fp@example.com",
                "password": "testpass123",
            },
            headers={"X-Fingerprint": "banned-fp-login"},
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response  # 로그인 실패

    async def test_no_fingerprint_header(self, client, user):
        """시나리오 14: 핑거프린트 없이 요청 → 정상 처리."""
        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "fp@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/"

    async def test_multiple_accounts_same_fingerprint(self, client, user):
        """시나리오 15: 같은 핑거프린트로 여러 계정."""
        from apps.users.models import FingerprintLog

        # 첫 번째 계정 로그인
        await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "fp@example.com",
                "password": "testpass123",
            },
            headers={"X-Fingerprint": "shared-fp"},
        )

        # 두 번째 계정 가입
        await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "fp2@example.com",
                "nickname": "두번째",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
            headers={"X-Fingerprint": "shared-fp"},
        )

        logs = await FingerprintLog.objects.filter(fingerprint="shared-fp").acount()
        assert logs >= 2
