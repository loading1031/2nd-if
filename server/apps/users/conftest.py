"""users 앱 테스트 공용 fixtures."""

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
