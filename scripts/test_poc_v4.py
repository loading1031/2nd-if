"""PoC v4 E2E — breathing + reflow + slide 전환 검증."""

from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8000/static/poc/reader-spread-v4.html"
OUT_DIR = Path("scripts/poc-v4-screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 900})
        page = context.new_page()

        errors, msgs = [], []
        page.on("console", lambda m: msgs.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: errors.append(str(e)))

        print(f"▶ 로드: {URL}")
        resp = page.goto(URL, wait_until="networkidle", timeout=20000)
        print(f"  HTTP {resp.status}")
        page.wait_for_timeout(1500)

        # 01 — 첫 스프레드 정적 (breath 영향 있는 순간)
        page.screenshot(path=OUT_DIR / "01_initial.png")
        print("  → 01_initial.png")

        # 02 — 1.75초 뒤 (breath 반대 상태)
        page.wait_for_timeout(1750)
        page.screenshot(path=OUT_DIR / "02_breath_reverse.png")
        print("  → 02_breath_reverse.png")

        info = page.evaluate("""() => ({
            pageNum: document.getElementById('pageNum').textContent,
            totalPages: document.getElementById('totalPages').textContent,
            fps: document.getElementById('fps').textContent,
        })""")
        print(f"  상태: {info}")

        # 03 — 전환 시작 직후 (슬라이드 중간쯤)
        page.click("canvas#spread")  # focus
        page.wait_for_timeout(200)
        page.keyboard.press("ArrowRight")
        page.wait_for_timeout(220)  # 전환 500ms 중간쯤
        page.screenshot(path=OUT_DIR / "03_transition_mid.png")
        print("  → 03_transition_mid.png")

        # 04 — 전환 완료 후 (spread 2)
        page.wait_for_timeout(400)
        page.screenshot(path=OUT_DIR / "04_after_transition.png")
        print("  → 04_after_transition.png")

        info2 = page.evaluate("""() => ({
            pageNum: document.getElementById('pageNum').textContent,
            fps: document.getElementById('fps').textContent,
        })""")
        print(f"  상태: {info2}")

        # 05 — spread 2 정적 breath 중
        page.wait_for_timeout(1500)
        page.screenshot(path=OUT_DIR / "05_spread2_breath.png")
        print("  → 05_spread2_breath.png")

        print("\n" + "=" * 60)
        if errors:
            print("❌ JS 에러:")
            for e in errors:
                print(f"   {e}")
        else:
            print("✅ JS 에러 없음")
        if msgs:
            print(f"📝 Console ({len(msgs)}):")
            for m in msgs[:10]:
                print(f"   {m}")

        if int(info2["pageNum"]) > int(info["pageNum"]):
            print(f"\n✅ 전환 성공: {info['pageNum']} → {info2['pageNum']}")
        else:
            print(f"\n❌ 전환 실패: {info['pageNum']} → {info2['pageNum']}")

        browser.close()


if __name__ == "__main__":
    main()
