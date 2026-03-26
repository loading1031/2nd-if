"""에피소드 작성/읽기/별점 E2E 테스트."""

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from apps.stories.models import Episode, Work

User = get_user_model()


def _login(page, base_url, email="e2e@example.com", password="testpass123"):
    page.goto(f"{base_url}/users/login/")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/")


@pytest.fixture()
def author_with_work(db):
    user = User(email="e2e@example.com", nickname="E2E작가")
    user.set_password("testpass123")
    user.save()
    work = Work.objects.create(title="E2E 작품", description="테스트", author=user, license=Work.License.FREE)
    return user, work


@pytest.fixture()
def work_with_episodes(author_with_work):
    user, work = author_with_work
    for i in range(1, 4):
        Episode.objects.create(
            work=work,
            episode_number=i,
            title=f"테스트 {i}화",
            content=f"<p>본문 {i}화 내용입니다.</p>",
            author=user,
        )
    return user, work


@pytest.mark.django_db(transaction=True)
def test_episode_write_page_loads(page, live_server_url, author_with_work):
    """에피소드 작성 페이지가 로드된다."""
    user, work = author_with_work
    _login(page, live_server_url)

    page.goto(f"{live_server_url}/stories/{work.pk}/episodes/write/")
    expect(page.locator("h2")).to_contain_text("새 에피소드")
    # TipTap 에디터 로드 확인
    expect(page.locator("#editor .tiptap")).to_be_visible(timeout=5000)


@pytest.mark.django_db(transaction=True)
def test_episode_write_requires_login(page, live_server_url, author_with_work):
    """비로그인 시 에피소드 작성 → 로그인 페이지로."""
    _, work = author_with_work
    page.goto(f"{live_server_url}/stories/{work.pk}/episodes/write/")
    page.wait_for_url("**/users/login/**")


@pytest.mark.django_db(transaction=True)
def test_episode_read_page(page, live_server_url, work_with_episodes):
    """에피소드 읽기 페이지가 본문을 표시한다."""
    _, work = work_with_episodes
    page.goto(f"{live_server_url}/stories/{work.pk}/episodes/1/")

    # HTMX 로드 대기 (워터마크 zero-width 문자 때문에 텍스트 비교 대신 요소 존재 확인)
    page.wait_for_selector(".prose p", timeout=5000)
    expect(page.locator(".prose p")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_episode_read_shows_rating(page, live_server_url, work_with_episodes):
    """에피소드 읽기 페이지에 별점 UI가 표시된다."""
    _, work = work_with_episodes
    page.goto(f"{live_server_url}/stories/{work.pk}/episodes/1/")

    page.wait_for_selector(".rating", timeout=5000)
    expect(page.locator(".rating")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_rating_submission(page, live_server_url, work_with_episodes):
    """로그인 후 별점 제출이 동작한다."""
    _, work = work_with_episodes
    _login(page, live_server_url)

    page.goto(f"{live_server_url}/stories/{work.pk}/episodes/1/")
    page.wait_for_selector(".rating", timeout=5000)

    # 4점 클릭
    page.click('.rating input[value="4"]')
    page.wait_for_timeout(1000)

    # 별점 결과 영역 확인
    expect(page.locator("#rating-result")).not_to_be_empty()


@pytest.mark.django_db(transaction=True)
def test_episode_navigation(page, live_server_url, work_with_episodes):
    """에피소드 이전/다음 네비게이션이 동작한다."""
    _, work = work_with_episodes
    page.goto(f"{live_server_url}/stories/{work.pk}/episodes/2/")

    page.wait_for_selector("a.btn-ghost", timeout=5000)
    # "이전 화" 링크 존재
    prev_link = page.locator('a.btn-ghost:has-text("이전 화")')
    expect(prev_link).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_work_detail_shows_episodes(page, live_server_url, work_with_episodes):
    """작품 상세에서 에피소드 목록이 표시된다."""
    _, work = work_with_episodes
    page.goto(f"{live_server_url}/stories/{work.pk}/")

    page.wait_for_timeout(2000)
    content = page.content()
    assert "테스트 1화" in content
