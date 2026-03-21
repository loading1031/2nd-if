import pytest
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
        response = await client.post("/users/htmx/auth/signup/", {
            "email": "new@example.com",
            "nickname": "새유저",
            "password": "testpass123",
            "password_confirm": "testpass123",
        })
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/users/login/"
        assert await User.objects.filter(email="new@example.com").aexists()

    async def test_signup_duplicate_email(self, client, user):
        response = await client.post("/users/htmx/auth/signup/", {
            "email": "existing@example.com",
            "nickname": "다른유저",
            "password": "testpass123",
            "password_confirm": "testpass123",
        })
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_password_mismatch(self, client):
        response = await client.post("/users/htmx/auth/signup/", {
            "email": "new@example.com",
            "nickname": "새유저",
            "password": "testpass123",
            "password_confirm": "wrongpass",
        })
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_signup_short_password(self, client):
        response = await client.post("/users/htmx/auth/signup/", {
            "email": "new@example.com",
            "nickname": "새유저",
            "password": "short",
            "password_confirm": "short",
        })
        assert response.status_code == 200
        assert "HX-Redirect" not in response


@pytest.mark.django_db(transaction=True)
class TestLogin:
    async def test_login_success(self, client, user):
        response = await client.post("/users/htmx/auth/login/", {
            "email": "existing@example.com",
            "password": "testpass123",
        })
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/"

    async def test_login_wrong_password(self, client, user):
        response = await client.post("/users/htmx/auth/login/", {
            "email": "existing@example.com",
            "password": "wrongpass",
        })
        assert response.status_code == 200
        assert "HX-Redirect" not in response

    async def test_login_nonexistent_user(self, client):
        response = await client.post("/users/htmx/auth/login/", {
            "email": "nobody@example.com",
            "password": "testpass123",
        })
        assert response.status_code == 200
        assert "HX-Redirect" not in response


@pytest.mark.django_db(transaction=True)
class TestLogout:
    async def test_logout(self, client, user):
        await client.post("/users/htmx/auth/login/", {
            "email": "existing@example.com",
            "password": "testpass123",
        })
        response = await client.post("/users/htmx/auth/logout/")
        assert response.status_code == 200
        assert response["HX-Redirect"] == "/"
