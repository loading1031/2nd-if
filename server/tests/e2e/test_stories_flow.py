import pytest
from playwright.sync_api import expect


def _login(page, base_url, email="e2e@example.com", password="testpass123"):
    """로그인 헬퍼."""
    page.goto(f"{base_url}/users/login/")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/")


@pytest.mark.django_db(transaction=True)
def test_work_list_page(page, live_server_url):
    """작품 목록 페이지 접근."""
    page.goto(f"{live_server_url}/stories/")
    expect(page.locator("h1")).to_contain_text("작품 목록")


@pytest.mark.django_db(transaction=True)
def test_work_create_requires_login(page, live_server_url):
    """비로그인 시 작품 생성 → 로그인 페이지로 리다이렉트."""
    page.goto(f"{live_server_url}/stories/create/")
    page.wait_for_url("**/users/login/**")


@pytest.mark.django_db(transaction=True)
def test_work_create_flow(page, live_server_url, test_user):
    """로그인 → 작품 생성 → 상세 페이지 이동."""
    _login(page, live_server_url)

    page.goto(f"{live_server_url}/stories/create/")
    page.fill('input[name="title"]', "E2E 테스트 작품")
    page.fill('textarea[name="description"]', "Playwright로 생성한 작품입니다.")

    page.click('button[type="submit"]')
    page.wait_for_url("**/stories/*/")


@pytest.mark.django_db(transaction=True)
def test_pages_render_without_error(page, live_server_url):
    """주요 페이지들이 500 에러 없이 렌더링 확인."""
    pages = [
        "/",
        "/users/signup/",
        "/users/login/",
        "/stories/",
    ]
    for path in pages:
        response = page.goto(f"{live_server_url}{path}")
        assert response.status == 200, f"{path} returned {response.status}"
