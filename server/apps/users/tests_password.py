from unittest.mock import patch

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import AsyncClient
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


@pytest.fixture
async def user(db):
    """테스트용 사용자 생성"""
    u = User(email="test@example.com", nickname="테스트유저")
    u.set_password("testpass123")
    await u.asave()
    return u


@pytest.fixture
def client():
    return AsyncClient()


@pytest.mark.django_db(transaction=True)
class TestPasswordResetPage:
    async def test_password_reset_page_renders(self, client):
        """비밀번호 찾기 페이지가 정상 렌더링되는지 확인"""
        response = await client.get("/users/password-reset/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "비밀번호 찾기" in content
        assert "이메일" in content


@pytest.mark.django_db(transaction=True)
class TestPasswordResetSubmit:
    @patch("apps.users.views.password_views.send_mail")
    async def test_password_reset_sends_email(self, mock_send_mail, client, user):
        """존재하는 이메일로 요청 시 이메일이 발송되는지 확인"""
        mock_send_mail.return_value = 1

        response = await client.post(
            "/users/htmx/auth/password-reset/",
            {
                "email": "test@example.com",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "이메일을 확인하세요" in content
        mock_send_mail.assert_called_once()

    async def test_password_reset_nonexistent_email_no_error(self, client):
        """존재하지 않는 이메일로 요청해도 에러를 노출하지 않는지 확인 (보안)"""
        response = await client.post(
            "/users/htmx/auth/password-reset/",
            {
                "email": "nonexistent@example.com",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        # Should still show success page (no email enumeration)
        assert "이메일을 확인하세요" in content

    async def test_password_reset_empty_email(self, client):
        """이메일 미입력 시 에러 메시지 표시"""
        response = await client.post(
            "/users/htmx/auth/password-reset/",
            {
                "email": "",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "이메일 주소를 입력해주세요" in content


@pytest.mark.django_db(transaction=True)
class TestPasswordResetConfirm:
    def _generate_token_and_uid(self, user):
        """테스트용 토큰 및 UID 생성"""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return uid, token

    async def test_password_reset_confirm_page_renders(self, client, user):
        """새 비밀번호 설정 페이지가 정상 렌더링되는지 확인"""
        uid, token = self._generate_token_and_uid(user)
        response = await client.get(f"/users/password-reset/{uid}/{token}/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "새 비밀번호 설정" in content

    async def test_password_reset_confirm_success(self, client, user):
        """유효한 토큰으로 비밀번호 변경 성공"""
        uid, token = self._generate_token_and_uid(user)
        response = await client.post(
            f"/users/htmx/auth/password-reset/{uid}/{token}/",
            {
                "new_password": "newpass1234",
                "new_password_confirm": "newpass1234",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "비밀번호가 변경되었습니다" in content

        # Verify password was actually changed
        await user.arefresh_from_db()
        is_valid = await sync_to_async(user.check_password)("newpass1234")
        assert is_valid

    async def test_password_reset_confirm_mismatch(self, client, user):
        """비밀번호 불일치 시 에러 메시지 표시"""
        uid, token = self._generate_token_and_uid(user)
        response = await client.post(
            f"/users/htmx/auth/password-reset/{uid}/{token}/",
            {
                "new_password": "newpass1234",
                "new_password_confirm": "differentpass",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "비밀번호가 일치하지 않습니다" in content

    async def test_password_reset_confirm_short_password(self, client, user):
        """8자 미만 비밀번호 시 에러 메시지 표시"""
        uid, token = self._generate_token_and_uid(user)
        response = await client.post(
            f"/users/htmx/auth/password-reset/{uid}/{token}/",
            {
                "new_password": "short",
                "new_password_confirm": "short",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "너무 짧습니다" in content

    async def test_password_reset_confirm_invalid_token(self, client, user):
        """유효하지 않은 토큰으로 요청 시 에러 메시지 표시"""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = await client.post(
            f"/users/htmx/auth/password-reset/{uid}/invalid-token/",
            {
                "new_password": "newpass1234",
                "new_password_confirm": "newpass1234",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "만료되었거나 이미 사용된 링크입니다" in content

    async def test_password_reset_confirm_invalid_uid(self, client):
        """유효하지 않은 UID로 요청 시 에러 메시지 표시"""
        response = await client.post(
            "/users/htmx/auth/password-reset/invalid-uid/invalid-token/",
            {
                "new_password": "newpass1234",
                "new_password_confirm": "newpass1234",
            },
        )
        assert response.status_code == 200
        content = response.content.decode()
        assert "유효하지 않은 링크입니다" in content
