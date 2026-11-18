"""診療テーマの一覧・絞り込み・検索で、同じ掲載物にたどり着けることを確かめる。"""
import re
from pathlib import Path

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PERIOP = "periop_antithrombotic_consult.html"


def check_catalog(page, url, mobile):
    page.goto(url)
    expect(page.locator("#leadCounts")).to_contain_text("・資料")
    expect(page.locator("#loadStatus")).to_be_hidden()
    total = int(page.locator("#count b").inner_text())
    sections = page.locator("#catalog .section")
    groups = {
        section.get_attribute("id").removeprefix("sec-"):
        section.locator("a[data-id]").evaluate_all("links => links.map(a => a.dataset.id)")
        for section in sections.all()
    }
    assert len({item for group in groups.values() for item in group}) == total
    assert PERIOP in groups["stroke"] and PERIOP in groups["medication"]
    assert "select_score.html" in groups["stroke"] and "select_score.html" in groups["epilepsy"]
    assert "handouts/heatstroke-hydration-guidance/" not in groups["stroke"]

    for theme, members in groups.items():
        if mobile:
            page.locator("#themeSelect").select_option(theme)
        else:
            page.locator('#themeList [data-theme="' + theme + '"]').click()
        cards = page.locator("#catalog h3 a").evaluate_all("links => links.map(a => a.dataset.id)")
        assert len(cards) == len(set(cards)) == int(page.locator("#count b").inner_text())
        assert sorted(cards) == sorted(members), theme
        assert page.evaluate("document.documentElement.scrollWidth === innerWidth"), theme

    page.goto(url)
    page.locator("#quick").get_by_role("button", name="脳梗塞 休薬").click()
    expect(page.locator("#catalog h3 a").first).to_have_attribute("href", PERIOP)
    for q in ["脳梗塞後 休薬", "術前　抗凝固薬", "周術期の抗血栓薬の調整", "ＤＯＡＣ"]:
        page.locator("#searchInput").fill(q)
        expect(page.locator("#catalog h3 a").first).to_have_attribute("href", PERIOP)
        expect(page.locator('#catalog a[href="' + PERIOP + '"]')).to_have_count(1)
    if mobile:
        page.locator("#filterToggle").click()
    for purpose in ["treatment", "communication"]:
        page.locator("#purposeFilter").select_option(purpose)
        expect(page.locator("#catalog h3 a").first).to_have_attribute("href", PERIOP)
    page.reload()
    expect(page.locator("#purposeFilter")).to_have_value("communication")
    expect(page.locator("#searchInput")).to_have_value("ＤＯＡＣ")
    expect(page.locator("#catalog h3 a").first).to_have_attribute("href", PERIOP)
    page.locator("#chips [data-reset]").click()
    page.locator("#searchInput").fill("低Ｎａ")
    expect(page.locator("#catalog h3 a").first).to_have_attribute("href", "hyponatremia.html")
    page.goto(url + "?theme=renal&q=DOAC")
    expect(page.locator("#searchEverywhere")).to_be_visible()
    page.locator("#searchEverywhere").click()
    expect(page.locator("#searchInput")).to_have_value("DOAC")
    expect(page.locator("#catalog h3 a").first).to_have_attribute("href", PERIOP)


def test_catalog_themes():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for width in [1440, 390]:
            page = browser.new_page(viewport={"width": width, "height": 900}, service_workers="block")
            page.route(re.compile(r"^https://catalog\.test/(?:\?.*)?$"),
                       lambda route: route.fulfill(path=ROOT / "index.html"))
            page.route("**/handouts/manifest.json", lambda route: route.fulfill(path=ROOT / "handouts/manifest.json"))
            check_catalog(page, "https://catalog.test/", mobile=width < 980)
            page.close()
        browser.close()
