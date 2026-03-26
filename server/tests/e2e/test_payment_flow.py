"""결제/지갑/페이월 E2E 테스트.

MetaMask 확장프로그램은 Playwright에서 자동화 불가하므로,
페이지 렌더링과 UI 상태만 검증한다.
"""

import pytest
from django.contrib.auth import get_user_model
from playwright.sync_api import expect

from apps.stories.models import Episode, EpisodePurchase, Work

User = get_user_model()


def _login(page, base_url, email, password="testpass123"):
    page.goto(f"{base_url}/users/login/")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_url(f"{base_url}/")


@pytest.fixture()
def author(db):
    user = User(
        email="author@e2e.com",
        nickname="작가",
        wallet_address="0x1234567890abcdef1234567890abcdef12345678",
    )
    user.set_password("testpass123")
    user.save()
    return user


@pytest.fixture()
def reader(db):
    user = User(email="reader@e2e.com", nickname="독자")
    user.set_password("testpass123")
    user.save()
    return user


@pytest.fixture()
def paid_work(author):
    work = Work.objects.create(title="유료 작품", author=author, license=Work.License.FREE)
    Episode.objects.create(
        work=work,
        episode_number=1,
        title="무료 에피소드",
        content="<p>무료 내용</p>",
        author=author,
        is_paid=False,
    )
    Episode.objects.create(
        work=work,
        episode_number=2,
        title="유료 에피소드",
        content="<p>유료 내용</p>",
        author=author,
        is_paid=True,
        price=1.00,
    )
    return work


# ── 페이월 테스트 ──────────────────────────────


@pytest.mark.django_db(transaction=True)
def test_free_episode_shows_content(page, live_server_url, paid_work, reader):
    """무료 에피소드는 본문이 보인다."""
    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/1/")
    # 워터마크 zero-width 문자 때문에 텍스트 비교 대신 본문 요소 존재 확인
    page.wait_for_selector(".prose p", timeout=5000)
    expect(page.locator(".prose p")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_paid_episode_shows_paywall(page, live_server_url, paid_work, reader):
    """미구매 유료 에피소드는 페이월이 표시된다."""
    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/2/")
    page.wait_for_timeout(2000)

    content = page.content()
    assert "유료 에피소드입니다" in content
    assert "유료 내용" not in content


@pytest.mark.django_db(transaction=True)
def test_paid_episode_paywall_has_payment_button(page, live_server_url, paid_work, reader):
    """페이월에 결제 버튼이 있다."""
    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/2/")
    page.wait_for_timeout(2000)

    expect(page.locator('button:has-text("USDC로 결제")')).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_paid_episode_author_sees_content(page, live_server_url, paid_work, author):
    """작가 본인은 유료 에피소드 본문을 볼 수 있다."""
    _login(page, live_server_url, "author@e2e.com")
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/2/")
    page.wait_for_selector(".prose", timeout=5000)

    content = page.content()
    assert "유료 에피소드입니다" not in content


@pytest.mark.django_db(transaction=True)
def test_paid_episode_purchased_shows_content(page, live_server_url, paid_work, reader):
    """구매한 유료 에피소드는 본문이 보인다."""
    ep = Episode.objects.get(work=paid_work, episode_number=2)
    EpisodePurchase.objects.create(
        episode=ep,
        buyer=reader,
        tx_hash="0x" + "a" * 64,
        token="USDC",
        amount=1.00,
        confirmed=True,
    )

    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/2/")
    page.wait_for_selector(".prose", timeout=5000)

    content = page.content()
    assert "유료 에피소드입니다" not in content


@pytest.mark.django_db(transaction=True)
def test_anonymous_paid_episode_shows_login(page, live_server_url, paid_work):
    """비로그인 시 유료 에피소드 → 로그인 유도."""
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/2/")
    page.wait_for_timeout(2000)

    expect(page.locator('a:has-text("로그인 후 결제")')).to_be_visible()


# ── 지갑 설정 테스트 ──────────────────────────────


@pytest.mark.django_db(transaction=True)
def test_wallet_page_requires_login(page, live_server_url):
    """비로그인 시 지갑 설정 → 로그인 페이지로."""
    page.goto(f"{live_server_url}/users/wallet/")
    page.wait_for_url("**/users/login/**")


@pytest.mark.django_db(transaction=True)
def test_wallet_page_loads(page, live_server_url, author):
    """지갑 설정 페이지가 로드된다."""
    _login(page, live_server_url, "author@e2e.com")
    page.goto(f"{live_server_url}/users/wallet/")

    expect(page.locator("h2")).to_contain_text("지갑 설정")
    # 기존 지갑 주소 표시 (p.font-mono로 한정)
    expect(page.locator("p.font-mono")).to_contain_text("0x1234")


@pytest.mark.django_db(transaction=True)
def test_wallet_save(page, live_server_url, reader):
    """지갑 주소 저장이 동작한다."""
    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/users/wallet/")

    page.fill("#wallet-address-input", "0xAbCdEf1234567890AbCdEf1234567890AbCdEf12")
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)

    expect(page.locator(".alert-success")).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_wallet_invalid_address(page, live_server_url, reader):
    """잘못된 지갑 주소 → 에러."""
    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/users/wallet/")

    page.fill("#wallet-address-input", "invalid-address")
    # HTML5 pattern 검증으로 제출 자체가 안 될 수 있음
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)

    # 여전히 지갑 설정 페이지에 있어야 함
    expect(page.locator("h2")).to_contain_text("지갑 설정")


# ── 네비게이션 테스트 ──────────────────────────────


@pytest.mark.django_db(transaction=True)
def test_navbar_shows_wallet_link(page, live_server_url, author):
    """로그인 후 navbar에 지갑 설정 링크가 있다."""
    _login(page, live_server_url, "author@e2e.com")
    page.goto(f"{live_server_url}/")

    # 닉네임 드롭다운 클릭
    page.click('.dropdown [role="button"]')
    expect(page.locator('a:has-text("지갑 설정")')).to_be_visible()


@pytest.mark.django_db(transaction=True)
def test_payment_modal_opens(page, live_server_url, paid_work, reader):
    """결제 버튼 클릭 시 결제 모달이 열린다."""
    _login(page, live_server_url, "reader@e2e.com")
    page.goto(f"{live_server_url}/stories/{paid_work.pk}/episodes/2/")
    page.wait_for_timeout(2000)

    # 결제 버튼 클릭
    page.click('button:has-text("USDC로 결제")')
    page.wait_for_timeout(500)

    # 모달이 열림
    expect(page.locator("#payment-modal")).to_be_visible()
    expect(page.locator("#payment-modal")).to_contain_text("에피소드 구매")
