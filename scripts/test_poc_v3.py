"""PoC 시네마틱 리더 E2E 검증 스크립트.

실행:
    uv run --frozen python scripts/test_poc.py

사전조건:
    docker compose -f docker-compose.dev.yml up -d
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8000/static/poc/reader-spread-v3.html"
OUT_DIR = Path("scripts/poc-v3-screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        console_msgs = []
        page_errors = []
        page.on("console", lambda msg: console_msgs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print(f"▶ 로드: {URL}")
        response = page.goto(URL, wait_until="networkidle", timeout=20000)
        print(f"  HTTP {response.status} / {response.url}")

        # 페이지 타이틀 확인
        title = page.title()
        print(f"  <title>: {title}")

        # 초기 로드 대기 (폰트 + Pretext + 렌더 사이클)
        page.wait_for_timeout(1500)

        # 초기 상태 스크린샷
        page.screenshot(path=OUT_DIR / "01_initial.png")
        print("  → 01_initial.png")

        # 초기 DOM 상태
        info = page.evaluate("""() => {
            return {
                pageNum: document.getElementById('pageNum')?.textContent,
                totalPages: document.getElementById('totalPages')?.textContent,
                fps: document.getElementById('fps')?.textContent,
                sceneLabel: document.getElementById('sceneLabel')?.textContent,
                errorVisible: document.getElementById('error')?.style.display !== 'none'
                              && document.getElementById('error')?.textContent?.length > 0,
                errorText: document.getElementById('error')?.textContent,
            }
        }""")
        print(f"  상태: pageNum={info['pageNum']}/{info['totalPages']}, fps={info['fps']}, scene={info['sceneLabel']}")
        if info["errorVisible"]:
            print(f"  ⚠️ 페이지 에러 배너: {info['errorText']}")

        # 페이지에 포커스 주고 키 이벤트
        print("\n▶ → 키 시뮬레이션 (시네마틱 트리거)")
        page.click("canvas#spread")
        page.wait_for_timeout(200)

        # 키 이벤트를 window와 body 양쪽에 보내기
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(400)

        # 시네마틱 중간 스크린샷 (전환 2.4s 중 0.6~1.2s 지점)
        page.wait_for_timeout(600)
        page.screenshot(path=OUT_DIR / "02_mid_transition.png")
        print("  → 02_mid_transition.png (트랜지션 1.2s 지점)")

        mid_info = page.evaluate("""() => ({
            pageNum: document.getElementById('pageNum').textContent,
            scene: document.getElementById('sceneLabel').textContent,
        })""")
        print(f"  상태: pageNum={mid_info['pageNum']}, scene={mid_info['scene']}")

        # 전환 완료 대기
        page.wait_for_timeout(1800)
        page.screenshot(path=OUT_DIR / "03_after.png")
        print("  → 03_after.png (전환 완료 후)")

        after_info = page.evaluate("""() => ({
            pageNum: document.getElementById('pageNum').textContent,
            scene: document.getElementById('sceneLabel').textContent,
            fps: document.getElementById('fps').textContent,
        })""")
        print(f"  상태: pageNum={after_info['pageNum']}, scene={after_info['scene']}, fps={after_info['fps']}")

        # 시네마틱 판정
        print("\n" + "=" * 60)
        print("📊 결과")
        print("=" * 60)

        if page_errors:
            print("❌ JS 에러:")
            for e in page_errors:
                print(f"   {e}")
        else:
            print("✅ JS 에러 없음")

        if console_msgs:
            print(f"\n📝 Console ({len(console_msgs)}개):")
            for m in console_msgs[:20]:
                print(f"   {m}")

        initial_page = int(info["pageNum"]) if info["pageNum"].isdigit() else -1
        final_page = int(after_info["pageNum"]) if after_info["pageNum"].isdigit() else -1

        if final_page > initial_page:
            print(f"\n✅ 페이지 전환 성공: {initial_page} → {final_page}")
        else:
            print(f"\n❌ 페이지 전환 실패: {initial_page} → {final_page}")

        if info["errorVisible"]:
            print("\n❌ PoC가 에러 배너를 표시함 (Pretext 로드 실패 가능성)")

        browser.close()


if __name__ == "__main__":
    main()
