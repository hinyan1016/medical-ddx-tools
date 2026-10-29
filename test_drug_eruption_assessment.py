from pathlib import Path
from playwright.sync_api import sync_playwright

def test_clinical_inputs_and_reset():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for width in (390, 1280):
            page = browser.new_page(viewport={"width": width, "height": 844})
            page.goto(Path(__file__).with_name("drug_eruption_assessment.html").as_uri())
            assert page.locator("input[value=unknown]:checked").count() == 8
            assert "未確認が8項目" in page.locator("#urgency").inner_text()
            page.locator("input[name=emergency][value=yes]").check()
            assert "緊急対応を優先" in page.locator("#urgency").inner_text()
            page.locator("input[name=emergency][value=no]").check()
            page.locator("input[name=mucosal][value=yes]").check()
            assert "SJS/TEN" in page.locator("#differential").inner_text()
            page.locator("input[value=pustules]").check()
            page.locator("input[value=fixed]").check()
            assert "AGEP" in page.locator("#differential").inner_text()
            assert "固定薬疹" in page.locator("#differential").inner_text()
            page.locator(".drug-name").first.fill("薬A")
            assert "薬A" in page.locator("#summary").input_value()
            page.locator("#add-drug").click()
            assert page.locator(".drug-name").count() == 2
            page.on("dialog", lambda d: d.accept())
            page.locator("#reset").click()
            assert page.locator("input[value=unknown]:checked").count() == 8
            assert page.locator(".drug-name").first.input_value() == ""
            assert page.evaluate("document.documentElement.scrollWidth-innerWidth") == 0
            page.close()
        browser.close()
