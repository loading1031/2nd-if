import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test import AsyncClient

User = get_user_model()


@pytest.fixture
async def client():
    return AsyncClient()


@pytest.fixture
async def user():
    u = User(email="existing@example.com", nickname="기존유저")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.mark.django_db(transaction=True)
class TestSignup:
    async def test_signup_success(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "new@example.com",
                "nickname": "새유저",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
        )
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/users/login/"
        assert await User.objects.filter(email="new@example.com").aexists()

    async def test_signup_duplicate_email(self, client, user):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "existing@example.com",
                "nickname": "다른유저",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_password_mismatch(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "new@example.com",
                "nickname": "새유저",
                "password": "testpass123",
                "password_confirm": "wrongpass",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_short_password(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "new@example.com",
                "nickname": "새유저",
                "password": "short",
                "password_confirm": "short",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response


@pytest.mark.django_db(transaction=True)
class TestLogin:
    async def test_login_success(self, client, user):
        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "existing@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/"

    async def test_login_wrong_password(self, client, user):
        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "existing@example.com",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_login_nonexistent_user(self, client):
        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "nobody@example.com",
                "password": "testpass123",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_login_empty_fields(self, client):
        response = await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "",
                "password": "",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_empty_email(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "",
                "nickname": "새유저",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_empty_nickname(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "new@example.com",
                "nickname": "",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_invalid_email_format(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "not-an-email",
                "nickname": "새유저",
                "password": "testpass123",
                "password_confirm": "testpass123",
            },
        )
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_password_exactly_8_chars(self, client):
        response = await client.post(
            "/users/htmx/auth/signup/",
            {
                "email": "new@example.com",
                "nickname": "새유저",
                "password": "exactl8!",
                "password_confirm": "exactl8!",
            },
        )
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/users/login/"


@pytest.mark.django_db(transaction=True)
class TestLogout:
    async def test_logout(self, client, user):
        await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "existing@example.com",
                "password": "testpass123",
            },
        )
        response = await client.post("/users/htmx/auth/logout/")
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/"

    async def test_protected_page_after_logout(self, client, user):
        await client.post(
            "/users/htmx/auth/login/",
            {
                "email": "existing@example.com",
                "password": "testpass123",
            },
        )
        await client.post("/users/htmx/auth/logout/")
        response = await client.get("/stories/create/")
        assert response.status_code == 302


# === AI BYOK 테스트 ===


@pytest.fixture
async def ai_user():
    u = User(email="aiuser@example.com", nickname="AI유저")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
async def ai_client(ai_user):
    client = AsyncClient()
    await sync_to_async(client.login)(email="aiuser@example.com", password="testpass123")
    return client


# --- 암호화 테스트 ---


class TestCrypto:
    """API 키 암호화/복호화 테스트."""

    def test_encrypt_decrypt_roundtrip(self):
        """암호화 후 복호화하면 원본과 동일하다."""
        from apps.users.crypto import decrypt_key, encrypt_key

        original = "sk-test-key-12345"
        encrypted = encrypt_key(original)
        decrypted = decrypt_key(encrypted)
        assert decrypted == original

    def test_encrypted_differs_from_plaintext(self):
        """암호화된 값은 원본과 다르다."""
        from apps.users.crypto import encrypt_key

        original = "sk-test-key-12345"
        encrypted = encrypt_key(original)
        assert encrypted != original.encode()

    def test_decrypt_invalid_data_fails(self):
        """잘못된 데이터 복호화 시 에러."""
        from cryptography.fernet import InvalidToken

        from apps.users.crypto import decrypt_key

        with pytest.raises(InvalidToken):
            decrypt_key(b"invalid-data")


# --- UserAIProvider 모델 테스트 ---


@pytest.mark.django_db(transaction=True)
class TestUserAIProvider:
    """UserAIProvider 모델 테스트."""

    async def test_create_provider(self, ai_user):
        """프로바이더를 생성할 수 있다."""
        from apps.users.crypto import encrypt_key
        from apps.users.models import UserAIProvider

        provider = await UserAIProvider.objects.acreate(
            user=ai_user,
            provider="openai",
            display_name="내 GPT",
            api_key_encrypted=encrypt_key("sk-test"),
            model_name="gpt-4o",
        )
        assert provider.pk is not None
        assert provider.is_active is True

    async def test_unique_display_name_per_user(self, ai_user):
        """같은 사용자에게 중복 별칭은 불가하다."""
        from django.db import IntegrityError

        from apps.users.crypto import encrypt_key
        from apps.users.models import UserAIProvider

        await UserAIProvider.objects.acreate(
            user=ai_user,
            provider="openai",
            display_name="내 GPT",
            api_key_encrypted=encrypt_key("sk-1"),
            model_name="gpt-4o",
        )
        with pytest.raises(IntegrityError):
            await UserAIProvider.objects.acreate(
                user=ai_user,
                provider="anthropic",
                display_name="내 GPT",
                api_key_encrypted=encrypt_key("sk-2"),
                model_name="claude-sonnet-4-20250514",
            )

    async def test_different_users_same_name_ok(self, ai_user):
        """다른 사용자는 같은 별칭 사용 가능하다."""
        from apps.users.crypto import encrypt_key
        from apps.users.models import UserAIProvider

        other = User(email="other@example.com", nickname="다른유저")
        other.set_password("pass123")
        await other.asave()
        await UserAIProvider.objects.acreate(
            user=ai_user,
            provider="openai",
            display_name="GPT",
            api_key_encrypted=encrypt_key("sk-1"),
            model_name="gpt-4o",
        )
        p2 = await UserAIProvider.objects.acreate(
            user=other,
            provider="openai",
            display_name="GPT",
            api_key_encrypted=encrypt_key("sk-2"),
            model_name="gpt-4o",
        )
        assert p2.pk is not None


# --- 설정 페이지 뷰 테스트 ---


@pytest.mark.django_db(transaction=True)
class TestAISettingsPage:
    """AI 설정 페이지 테스트."""

    async def test_requires_login(self):
        """미로그인 → 리다이렉트."""
        client = AsyncClient()
        response = await client.get("/users/settings/ai/")
        assert response.status_code == 302

    async def test_page_accessible(self, ai_client):
        """로그인 사용자 → 설정 페이지 표시."""
        response = await ai_client.get("/users/settings/ai/")
        assert response.status_code == 200
        assert "프로바이더" in response.content.decode()

    async def test_add_provider(self, ai_client):
        """프로바이더 추가 → DB 저장."""
        response = await ai_client.post(
            "/users/settings/ai/add/",
            {
                "provider": "openai",
                "display_name": "내 GPT",
                "api_key": "sk-test-12345",
                "model_name": "gpt-4o",
            },
        )
        assert response.status_code == 200

    async def test_delete_provider(self, ai_client, ai_user):
        """프로바이더 삭제."""
        from apps.users.crypto import encrypt_key
        from apps.users.models import UserAIProvider

        p = await UserAIProvider.objects.acreate(
            user=ai_user,
            provider="openai",
            display_name="삭제 테스트",
            api_key_encrypted=encrypt_key("sk-del"),
            model_name="gpt-4o",
        )
        response = await ai_client.delete(f"/users/settings/ai/{p.pk}/delete/")
        assert response.status_code in [200, 204]
        assert not await UserAIProvider.objects.filter(pk=p.pk).aexists()
