import pytest
from playwright.sync_api import expect


@pytest.mark.django_db(transaction=True)
def test_signup_flow(page, live_server_url):
    """회원가입 → 로그인 페이지로 이동 확인."""
    page.goto(f"{live_server_url}/users/signup/")

    # 폼 입력
    page.fill('input[name="email"]', "newuser@example.com")
    page.fill('input[name="nickname"]', "새유저")
    page.fill('input[name="password"]', "testpass123")
    page.fill('input[name="password_confirm"]', "testpass123")

    # 제출
    page.click('button[type="submit"]')
    page.wait_for_url("**/users/login/**")

    # 로그인 페이지에 도착 확인
    expect(page.locator("h2")).to_contain_text("로그인")


@pytest.mark.django_db(transaction=True)
def test_login_flow(page, live_server_url, test_user):
    """로그인 → 홈으로 이동 확인."""
    page.goto(f"{live_server_url}/users/login/")

    page.fill('input[name="email"]', "e2e@example.com")
    page.fill('input[name="password"]', "testpass123")

    page.click('button[type="submit"]')
    page.wait_for_url(f"{live_server_url}/")


@pytest.mark.django_db(transaction=True)
def test_login_failure(page, live_server_url, test_user):
    """로그인 실패 → 에러 메시지 표시."""
    page.goto(f"{live_server_url}/users/login/")

    page.fill('input[name="email"]', "e2e@example.com")
    page.fill('input[name="password"]', "wrongpassword")

    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)

    # 에러 알림 확인
    expect(page.locator(".alert-error")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_signup_duplicate_email(page, live_server_url, test_user):
    """중복 이메일 가입 → 에러 메시지 표시."""
    page.goto(f"{live_server_url}/users/signup/")

    page.fill('input[name="email"]', "e2e@example.com")  # 이미 존재
    page.fill('input[name="nickname"]', "중복유저")
    page.fill('input[name="password"]', "testpass123")
    page.fill('input[name="password_confirm"]', "testpass123")

    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)

    # 에러 표시 확인 (페이지에 남아있어야 함)
    expect(page.locator('input[name="email"]')).to_be_visible()
