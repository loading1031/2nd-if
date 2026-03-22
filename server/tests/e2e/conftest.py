import os

# pytest 수집 단계에서 이미 필요 — fixture가 아닌 모듈 레벨에서 설정
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture()
def live_server_url(live_server):
    return live_server.url


@pytest.fixture()
def test_user(db):
    user = User(email="e2e@example.com", nickname="E2E유저")
    user.set_password("testpass123")
    user.save()
    return user
