import os
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML_PATH = Path(__file__).resolve().parent / "bilateral_facial_palsy.html"
SHOT_DIR = (
    Path(os.environ["BFP_SHOT_DIR"])
    if os.environ.get("BFP_SHOT_DIR")
    else None
)

EXPECTED_DISEASES = {
    "gbs",
    "lyme",
    "sarcoid",
    "meningeal_ca",
    "pcnsl",
    "infection_other",
    "pons",
    "mg",
    "trauma",
    "congenital",
    "bell_bilateral",
}


def launch_browser(p):
    try:
        return p.chromium.launch(channel="msedge")
    except Exception:
        return p.chromium.launch()


def assert_no_horizontal_overflow(page, label):
    metrics = page.evaluate(
        "() => ({ sw: document.documentElement.scrollWidth, iw: window.innerWidth })"
    )
    assert metrics["sw"] <= metrics["iw"], (
        f"[{label}] horizontal overflow detected: scrollWidth={metrics['sw']} > innerWidth={metrics['iw']}"
    )


def save_shot(page, filename):
    if SHOT_DIR is None:
        return
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(SHOT_DIR / filename), full_page=False)


def test_bilateral_facial_palsy_tool():
    url = HTML_PATH.as_uri()

    with sync_playwright() as p:
        browser = launch_browser(p)
        try:
            # 1. Desktop 1280x800 full interactive & screenshot suite
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                permissions=["clipboard-read", "clipboard-write"],
            )
            page = context.new_page()
            console_errors = []
            page_errors = []
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text)
                if msg.type == "error"
                else None,
            )
            page.on("pageerror", lambda err: page_errors.append(str(err)))

            page.goto(url, wait_until="load")
            assert_no_horizontal_overflow(page, "desktop_initial")
            save_shot(page, "desktop_top_1280.png")

            # Verify all 11 disease IDs exist in DOM
            dom_ids = set(
                page.evaluate(
                    "() => Array.from(document.querySelectorAll('.ddx-card')).map(el => el.getAttribute('data-disease-id'))"
                )
            )
            assert dom_ids == EXPECTED_DISEASES, f"Disease IDs mismatch: {dom_ids}"

            # Verify <details> explicit text & toggle (click + Space)
            details = page.locator("details.anat-details")
            summary = details.locator("summary")
            assert "クリック／タップで開閉" in summary.inner_text()
            assert not details.evaluate("el => el.open")

            summary.click()
            assert details.evaluate("el => el.open")
            svgs = details.locator("svg")
            assert svgs.count() == 2
            details.scroll_into_view_if_needed()
            save_shot(page, "anatomy_svgs_1280.png")

            summary.focus()
            page.keyboard.press("Space")
            assert not details.evaluate("el => el.open")
            page.keyboard.press("Enter")
            assert details.evaluate("el => el.open")
            summary.click()  # close before preset tests

            # Test all 6 presets and verify top ranked candidate & banners
            preset_expectations = [
                ("gbs", "gbs", "気道・球麻痺・呼吸予備能のアラート"),
                ("lyme", "lyme", "髄液細胞数 10〜50 /μL"),
                ("sarcoid", "sarcoid", "髄液細胞数 10〜50 /μL"),
                ("pontine", "pons", "緊急脳MRI（DWI含む）を優先"),
                ("mg", "mg", "気道・球麻痺・呼吸予備能のアラート"),
                ("meningeal", "meningeal_ca", "原因確定前の経験的全身ステロイド投与に関する注意"),
            ]
            for preset_key, top_id, expected_banner_substr in preset_expectations:
                page.click(f'.preset-btn[data-preset="{preset_key}"]')
                first_id = page.locator(".ddx-card").first.get_attribute("data-disease-id")
                assert first_id == top_id, (
                    f"Preset {preset_key}: expected top disease {top_id}, got {first_id}"
                )
                body_text = page.locator("body").inner_text()
                assert expected_banner_substr in body_text, (
                    f"Preset {preset_key}: missing banner '{expected_banner_substr}'"
                )
                if preset_key == "gbs":
                    page.locator("#sec-step1").scroll_into_view_if_needed()
                    save_shot(page, "preset_gbs_1280.png")
                if preset_key == "pontine":
                    page.locator(".ddx-card").first.scroll_into_view_if_needed()
                    save_shot(page, "preset_pontine_1280.png")

            # Direct interaction: reset then click checkboxes & radios directly
            page.click("#btn-reset")
            assert page.locator("#selected-count-pill").inner_text() == "選択中の所見：0項目"
            assert "陰性または安全を意味するものではありません" in page.locator("#step1-feedback").inner_text()

            page.click('input[name="triage"][value="corneal_danger"]')
            page.click('input[name="triage"][value="high_trauma"]')
            page.click('input[name="onset"][value="congenital"]')
            page.click('input[name="finding"][value="csf_pleo_gt50"]')
            assert "角膜潰瘍・穿孔" in page.locator("#step1-feedback").inner_text()
            assert "ATLSに基づく外傷初期診療" in page.locator("#step1-feedback").inner_text()
            assert "髄液細胞数 > 50 /μL" in page.locator("#step5-feedback").inner_text()
            assert page.locator("#selected-count-pill").inner_text() == "選択中の所見：4項目"

            # Verify summary text has no 〜 / ～ and copy normalizes tilde
            summary_val = page.locator("#summary-text").input_value()
            assert "～" not in summary_val and "〜" not in summary_val
            assert "眼痛・充血・角膜リスクあり" in summary_val

            page.evaluate(
                "() => { window.__copiedText = ''; navigator.clipboard.writeText = function(t){ window.__copiedText = t; return Promise.resolve(); }; document.getElementById('summary-text').value += '\\nテスト〜～範囲'; }"
            )
            page.click("#btn-copy")
            copied = page.evaluate("() => window.__copiedText")
            assert "〜" not in copied and "～" not in copied and "テスト--範囲" in copied, (
                f"Clipboard tilde normalization failed: {copied!r}"
            )

            # Final reset check
            page.click("#btn-reset")
            assert page.locator("#selected-count-pill").inner_text() == "選択中の所見：0項目"

            assert not console_errors, f"Console errors: {console_errors}"
            assert not page_errors, f"Page errors: {page_errors}"
            context.close()

            # 2. Mobile 390x844 and narrow 360x800 checks
            for w, h, shot_name in [(390, 844, "mobile_390.png"), (360, 800, None)]:
                mctx = browser.new_context(viewport={"width": w, "height": h})
                mpage = mctx.new_page()
                m_errors = []
                mpage.on("pageerror", lambda err: m_errors.append(str(err)))
                mpage.goto(url, wait_until="load")
                mpage.click("details.anat-details summary")
                assert mpage.locator("details.anat-details").evaluate("el => el.open")
                mpage.click('.preset-btn[data-preset="gbs"]')
                assert_no_horizontal_overflow(mpage, f"mobile_{w}x{h}")
                if shot_name:
                    mpage.evaluate("window.scrollTo(0, 0)")
                    save_shot(mpage, shot_name)
                assert not m_errors, f"Mobile {w}x{h} errors: {m_errors}"
                mctx.close()
        finally:
            browser.close()


if __name__ == "__main__":
    test_bilateral_facial_palsy_tool()
    print("ALL PLAYWRIGHT CHECKS PASSED")
