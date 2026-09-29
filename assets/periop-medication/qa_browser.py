"""実ブラウザで操作・モバイル幅・印刷・単一ファイル動作を確認する。"""
import json
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(tempfile.gettempdir()) / 'periop-medication-20260929' / 'qa'
OUT.mkdir(parents=True, exist_ok=True)
URL = 'http://127.0.0.1:8769/periop_medication_navigator.html'

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1280, 'height': 720}, timezone_id='Asia/Tokyo')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL)
    page.screenshot(path=str(OUT / 'desktop-start.png'), full_page=True)
    page.locator('#assessed').fill('2026-09-29T12:00')
    page.locator('#surgery').fill('2026-10-10T09:00')
    for key, value in [('urgency','elective'),('procedure','major'),('anesthesia','general'),('fasting','yes')]:
        page.locator('#'+key).select_option(value)
    page.locator('#search').fill('フォシーガ錠５ｍｇ')
    page.locator('[data-add="dapa"]').click()
    page.locator('#dose-0').fill('フォシーガ錠5 mg・1日1回朝')
    page.locator('#search').fill('エクメット')
    page.locator('[data-add="equmet"]').click()
    for key in ['eating','hydration','kidney','ketoneSafe','bp','oxygen']:
        page.locator('#fact-'+key).select_option('yes')
    page.locator('#fact-egfr').fill('60')
    page.locator('#fact-contrast').select_option('no')
    page.locator('#evaluate').click()
    assert page.locator('.result-card').count() == 3
    assert '2026-10-07 00:00' in page.locator('#results').inner_text()
    assert 'エクメット' in page.locator('#handoff').input_value()
    assert 'メトホルミン' in page.locator('#handoff').input_value()
    page.locator('#results').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / 'desktop-results.png'), full_page=True)
    page.locator('#fact-egfr').fill('29')
    assert page.locator('#results').inner_text() == '', '古い結果が残っている'
    page.locator('#evaluate').click()
    assert 'eGFR 30未満' in page.locator('#results').inner_text()
    page.locator('#fact-egfr').fill('60')
    page.locator('[data-mode="post"]').click()
    page.locator('#assessed').fill('2026-10-12T12:00')
    page.locator('#fact-glucose').select_option('yes')
    page.locator('#evaluate').click()
    assert '担当医が再開を判断' in page.locator('#results').inner_text()
    page.locator('#results details').evaluate_all('(els) => els.forEach(el => el.open = true)')
    page.pdf(path=str(OUT / 'print-review.pdf'), print_background=True, prefer_css_page_size=True)
    page.set_viewport_size({'width':390,'height':844})
    page.screenshot(path=str(OUT / 'mobile-results.png'), full_page=True)
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'スマートフォンで横はみ出し'
    assert page.locator('#handoff').input_value().find('評価日時') >= 0
    page.locator('[data-remove="1"]').click()
    assert page.locator('.selected-card').count() == 1
    assert not page.locator('#fact-egfr').count(), '無関係な質問が残った'
    page.locator('#search').fill('<img src=x onerror=alert(1)>')
    page.locator('[data-unknown]').click()
    page.locator('#evaluate').click()
    assert '<img src=x onerror=alert(1)>' in page.locator('#results').inner_text()
    assert not page.locator('#results img').count(), '薬名入力がHTMLとして実行された'
    page.locator('[data-mode="missed"]').click()
    page.locator('#assessed').fill('2026-09-29T12:00')
    page.locator('#state-0').select_option('taken')
    page.locator('#last-0').fill('2026-09-29T08:00')
    page.locator('#evaluate').click()
    assert '実際の状況：服用・投与した' in page.locator('#results').inner_text()
    page.locator('#scope').select_option('other')
    page.locator('#evaluate').click()
    assert '対象範囲外' in page.locator('#results').inner_text()
    page.locator('#scope').select_option('adult')
    page.locator('#procedure').select_option('minor')
    page.locator('#urgency').select_option('emergency')
    page.locator('#evaluate').click()
    assert not page.locator('.schedule').count()
    page.locator('#results').scroll_into_view_if_needed()
    page.screenshot(path=str(OUT / 'mobile-viewport.png'))
    # すべての候補を加えた最長フォームもモバイルで確認。
    page.reload()
    page.locator('#showAll').click()
    ids = page.locator('[data-add]').evaluate_all('(els) => els.map(el => el.dataset.add)')
    for drug_id in ids:
        page.locator('#showAll').click()
        page.locator('[data-add="'+drug_id+'"]').click()
    page.locator('#evaluate').click()
    assert page.locator('.selected-card').count() == 38
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(OUT / 'mobile-all-drugs.png'), full_page=True)
    # ネットワークがなくても保存した単一HTMLの判定が動く。
    offline = browser.new_context(offline=True, viewport={'width':390,'height':844})
    local = offline.new_page()
    local_errors = []
    local.on('pageerror', lambda e: local_errors.append(str(e)))
    local.goto((ROOT / 'periop_medication_navigator.html').as_uri())
    local.locator('#search').fill('リーマス')
    local.locator('[data-add="lithium"]').click()
    local.locator('#evaluate').click()
    assert local.locator('.result-card').count() == 1
    print(json.dumps({'desktop_mobile_ui':'PASS','invalidation':'PASS','compound_drug':'PASS','xss':'PASS','offline_file':'PASS','browser_errors':errors,'file_errors':local_errors,'outputs':str(OUT)},ensure_ascii=False,indent=2))
    assert not errors, errors
    assert not local_errors, local_errors
    browser.close()
