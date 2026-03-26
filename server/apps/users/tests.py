import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


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
