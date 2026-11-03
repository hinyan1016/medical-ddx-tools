"""公開への移設に伴う導線・保存HTML・PWAを実ブラウザで検収する。"""
import argparse
import functools
import hashlib
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--artifacts', required=True, type=Path)
    args = parser.parse_args()
    qa = args.artifacts.resolve()
    qa.mkdir(parents=True, exist_ok=True)
    record = json.loads((Path(__file__).parent / 'publication.json').read_text(encoding='utf-8'))
    html = (ROOT / 'neuro_test_navigator.html').read_bytes()
    assert hashlib.sha256(html).hexdigest() == record['publicHtmlSha256']
    soup = BeautifulSoup(html, 'html.parser')
    data = json.loads(soup.select_one('#catalog-data').get_text())
    assert len(data['tests']) == record['tests'] == 105
    assert len(data['coverage']['items']) == 73
    assert soup.select_one('link[rel="canonical"]')['href'] == record['publicUrl']
    assert soup.select_one('meta[name="robots"]')['content'] == 'index,follow'
    assert hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest() == record['catalogSha256']
    checks = ['承認済みの105検査データ・73ページ対応・公開用canonicalを保持']
    errors, offline_requests = [], []
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = 'http://127.0.0.1:' + str(server.server_port)
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            context = browser.new_context(viewport={'width': 1440, 'height': 1000}, accept_downloads=True, service_workers='block')
            page = context.new_page()
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.goto(url + '/')
            page.locator('#searchInput').fill('外注')
            page.locator('.theme-button[data-theme="neuro"]').click()
            page.locator('#purposeFilter').select_option('diagnosis')
            expect(page.locator('a.tool-card[href="neuro_test_navigator.html"]')).to_be_visible()
            expect(page.locator('#catalog a.tool-card')).to_have_count(1)
            page.screenshot(path=str(qa / 'public-index.png'))
            page.locator('a.tool-card[href="neuro_test_navigator.html"]').click()
            expect(page.locator('.test-card')).to_have_count(105)
            page.screenshot(path=str(qa / 'public-desktop.png'))
            checks.append('ツール一覧の外注検索・神経分類・鑑別用途から新しいページへ移動')
            page.locator('#search').fill('AQP4 CBA')
            expect(page.locator('.test-card')).to_have_count(1)
            page.locator('.card-title').click()
            expect(page.locator('.provider-card')).to_have_count(3)
            page.keyboard.press('Escape')
            checks.append('公開用HTMLでもAQP4 CBAの3依頼経路を確認')
            page.locator('[data-action="manage"]').first.click()
            with page.expect_download() as exported:
                page.locator('[data-action="export-json"]').click()
            json_file = qa / 'manual-update.json'
            exported.value.save_as(json_file)
            edited = json.loads(json_file.read_text(encoding='utf-8'))
            edited['version'] += '-offline-check'
            json_file.write_text(json.dumps(edited, ensure_ascii=False), encoding='utf-8')
            page.locator('#import-file').set_input_files(str(json_file))
            expect(page.locator('.imported-notice')).to_be_visible()
            expect(page.locator('.data-summary')).to_contain_text('-offline-check')
            with page.expect_download() as download:
                page.locator('.management-grid [data-action="download"]').click()
            saved = qa / 'NeuroFind-offline-verified.html'
            download.value.save_as(saved)
            saved_soup = BeautifulSoup(saved.read_text(encoding='utf-8'), 'html.parser')
            assert not saved_soup.select('[data-online-only],link[rel="manifest"],link[rel="apple-touch-icon"]')
            assert not saved_soup.select('script[src],link[rel="stylesheet"],img[src]')
            checks.append('JSON手動更新を含むHTMLを保存し、公開用SW・manifest等を除去')
            context.set_offline(True)
            standalone = context.new_page()
            standalone.on('pageerror', lambda e: errors.append(str(e)))
            standalone.on('request', lambda r: offline_requests.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
            standalone.goto(saved.as_uri())
            expect(standalone.locator('.test-card')).to_have_count(105)
            expect(standalone.locator('#data-version')).to_contain_text('-offline-check')
            standalone.locator('[data-action="coverage"]').click()
            expect(standalone.locator('.coverage-table tbody tr')).to_have_count(73)
            expect(standalone.locator('.coverage-changes li')).to_have_count(11)
            standalone.screenshot(path=str(qa / 'public-offline-coverage.png'))
            standalone.keyboard.press('Escape')
            standalone.locator('#search').fill('AQP4 CBA')
            expect(standalone.locator('[data-test-id="aqp4-cba"]')).to_be_visible()
            checks.append('保存HTMLを完全オフラインのfile://で開き、更新データ・検索・全対応表を確認')
            for width in [1440, 390, 320]:
                standalone.set_viewport_size({'width': width, 'height': 900})
                assert standalone.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            standalone.set_viewport_size({'width': 390, 'height': 844})
            standalone.screenshot(path=str(qa / 'public-offline-mobile.png'))
            assert not offline_requests
            checks.append('保存HTMLは320/390/1440pxで横はみ出しなし・外部HTTP要求0')
            context.close()

            # 実ファイル545アセットを実際に読み込む新規PWAコンテキスト。
            pwa = browser.new_context()
            live = pwa.new_page()
            live.on('pageerror', lambda e: errors.append(str(e)))
            live.goto(url + '/neuro_test_navigator.html')
            live.wait_for_function('navigator.serviceWorker.controller !== null', timeout=120000)
            expect(live.locator('.test-card')).to_have_count(105)
            cache = live.evaluate("async function(){var c=await caches.open('ddx-tools-v329');var r=await c.match('./neuro_test_navigator.html');return !!r&&r.status===200;}")
            assert cache
            pwa.set_offline(True)
            cached = pwa.new_page()
            cached.on('pageerror', lambda e: errors.append(str(e)))
            cached.goto(url + '/neuro_test_navigator.html')
            expect(cached.locator('.test-card')).to_have_count(105)
            cached.locator('#search').fill('MOG')
            expect(cached.locator('[data-test-id="mog"]')).to_be_visible()
            checks.append('新SWの全実アセットをキャッシュし、オフライン再訪でも105項目を表示・検索')
            assert not errors, errors
            pwa.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
    result = {'status': 'PASS', 'dataVersion': record['dataVersion'], 'checks': checks,
              'publicHtmlSha256': record['publicHtmlSha256'], 'javascriptErrors': errors,
              'standaloneExternalHttpRequests': offline_requests,
              'scope': 'ローカルHTTP＋保存file://のChromium検収。公開後HTTP/表示確認は別記。'}
    (qa / 'public-validation.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
