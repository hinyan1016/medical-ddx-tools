"""2026-11-12差分：データ保全・重複・検索・詳細・JSON往復・持出し検査。"""
import argparse
import functools
import hashlib
import importlib.util
import json
import re
import subprocess
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[2]
SRC=Path(__file__).resolve().parent

def catalog(html):
    return json.loads(re.search(r'<script[^>]*id="catalog-data"[^>]*>(.*?)</script>',html,re.S).group(1))

def normalized(value,key=''):
    # 手動取り込みはURLの日本語をパーセント表記へ、未設定のavailabilityを空文字へ正規化する。
    if isinstance(value,dict):
        return {k:normalized(v,k) for k,v in value.items() if not (k=='availability' and v=='')}
    if isinstance(value,list): return [normalized(v,key) for v in value]
    if isinstance(value,str) and key.lower().endswith('url'): return unquote(value)
    return value

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--artifacts',type=Path,required=True)
    parser.add_argument('--url',help='公開後のUIを同じ項目で確認する場合')
    args=parser.parse_args()
    qa=args.artifacts.resolve();qa.mkdir(parents=True,exist_ok=True)
    publication=json.loads((SRC/'publication.json').read_text(encoding='utf-8'))
    raw=(ROOT/'neuro_test_navigator.html').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==publication['publicHtmlSha256']
    current=catalog(raw.decode('utf-8'))
    baseline=catalog(subprocess.check_output(['git','show',publication['sourceCommit']+':neuro_test_navigator.html'],cwd=ROOT).decode('utf-8'))
    patch=json.loads((SRC/'cosmic-20261112-patches.json').read_text(encoding='utf-8'))
    assert len(current['tests'])==len(baseline['tests'])==135
    assert [t['id'] for t in current['tests']]==[t['id'] for t in baseline['tests']]
    assert len({t['id'] for t in current['tests']})==135
    assert current['coverage']==baseline['coverage']
    changed=[]
    for old,new in zip(baseline['tests'],current['tests']):
        if old!=new:
            changed.append(new['id'])
            expected=dict(old);expected.update(patch['changedTests'][new['id']])
            assert new==expected
    assert set(changed)=={'mog','encephalitis7'}
    assert current['updates']==baseline['updates']+patch['addedUpdates']
    assert len({u['url'] for u in current['updates']})==len(current['updates'])
    evidence=SRC/'sources/cosmic-20261112'
    for term in ['10001926','10001782','2026年10月1日']:
        assert term in (evidence/'panel.txt').read_text(encoding='utf-8')
    for term in ['10001923','10001924','10001925','2026年9月30日']:
        assert term in (evidence/'stopped.txt').read_text(encoding='utf-8')
    for term in ['IgG１法を採用','東北大学と完全同一のアッセイ法ではありません']:
        assert term in (evidence/'services-flight.txt').read_text(encoding='utf-8')
    checks=['135項目のID・順番・参照対応表を保持、133項目は完全一致','変更2項目と追加通知1件が保存差分に一致、検査・通知URLの重複なし','新しいコード・日付・MOG説明を保存公式原典と照合']
    # sparse checkoutでも、同じキャッシュ検査関数にGitの配信ファイル一覧を渡して判定する。
    spec=importlib.util.spec_from_file_location('cache_check',ROOT/'check_sw_cache.py')
    cache_check=importlib.util.module_from_spec(spec);spec.loader.exec_module(cache_check)
    files=set(subprocess.check_output(['git','ls-tree','-r','--name-only','HEAD'],cwd=ROOT,text=True,encoding='utf-8').splitlines())
    for path in ROOT.rglob('*'):
        if path.is_file() and '.git' not in path.parts: files.add(path.relative_to(ROOT).as_posix())
    pages={name for name in files if name.endswith('.html') and (('/' not in name and cache_check.is_page_name(name)) or (name.split('/')[0] in cache_check.PAGE_SUBDIRS and all(cache_check.is_page_name(part) for part in name.split('/'))))}
    original_files,original_pages=cache_check.collect_files,cache_check.collect_pages
    cache_check.collect_files=lambda root: files
    cache_check.collect_pages=lambda root: pages
    original_argv=__import__('sys').argv
    __import__('sys').argv=['check_sw_cache.py','--root',str(ROOT)]
    try: assert cache_check.main()==0
    finally:
        __import__('sys').argv=original_argv
        cache_check.collect_files,cache_check.collect_pages=original_files,original_pages
    checks.append('既存check_sw_cache.pyのゲートPASS（Git配信ツリー＋ローカル差分を対象、画像実体の全取得は省略）')
    errors=[];network=[]
    server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    target=args.url or 'http://127.0.0.1:'+str(server.server_port)+'/neuro_test_navigator.html'
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch()
            context=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,service_workers='block')
            page=context.new_page();page.on('pageerror',lambda err:errors.append(str(err)))
            page.goto(target,wait_until='networkidle')
            expect(page.locator('.test-card')).to_have_count(135)
            expect(page.locator('#data-version')).to_contain_text('2026.11.12.1')
            live=page.locator('#catalog-data').text_content()
            assert json.loads(live)==current
            page.screenshot(path=str(qa/'desktop.png'),full_page=False)
            for query,test_id in [('10001926','encephalitis7'),('10001782','encephalitis7'),('10001923','encephalitis7'),('10001924','encephalitis7'),('10001925','encephalitis7'),('GABA-BR','encephalitis7'),('GABA-AR','encephalitis7'),('TBA','encephalitis-tba'),('NMDAR 半定量','nmdar'),('gAChR RIA','gachr'),('MOG IgG1','mog')]:
                page.locator('#search').fill(query)
                expect(page.locator('[data-test-id="'+test_id+'"]')).to_be_visible()
            page.locator('#search').fill('10001923')
            expect(page.locator('.test-card')).to_have_count(1)
            page.locator('.card-title').click()
            expect(page.locator('#modal-body')).to_contain_text('2026年9月30日')
            expect(page.locator('#modal-body')).to_contain_text('10001926')
            expect(page.locator('#modal-body a[href="https://www.cosmic-jpn.co.jp/news/czvX-bYnU"]')).to_have_count(1)
            page.screenshot(path=str(qa/'panel-desktop.png'))
            for width in [1440,390,320]:
                page.set_viewport_size({'width':width,'height':900})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                assert page.locator('#modal-body').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1')
                if width==390:
                    page.locator('.provider-card').first.scroll_into_view_if_needed()
                    page.screenshot(path=str(qa/'panel-mobile.png'))
            page.keyboard.press('Escape')
            page.locator('#search').fill('MOG IgG1')
            page.locator('[data-test-id="mog"] .card-title').click()
            expect(page.locator('#modal-body')).to_contain_text('完全同一のアッセイ法ではありません')
            expect(page.locator('.provider-card')).to_have_count(2)
            page.locator('.provider-card').first.scroll_into_view_if_needed()
            page.screenshot(path=str(qa/'mog-mobile.png'))
            page.keyboard.press('Escape')
            page.set_viewport_size({'width':1440,'height':1000})
            page.locator('#sidebar [data-action="updates"]').click()
            expect(page.locator('.site-history li')).to_have_count(6)
            expect(page.locator('.provider-updates li')).to_have_count(8)
            expect(page.locator('.provider-updates a[href="https://www.cosmic-jpn.co.jp/news/0WgxEIoSU"]')).to_have_count(1)
            page.keyboard.press('Escape')
            checks.append('PC・390/320px：新旧コード・抗体表記・既存検査で検索、詳細と終了案内・公式リンク・更新履歴、横はみ出しなし')
            page.locator('[data-action="manage"]').first.click()
            with page.expect_download() as download:
                page.locator('[data-action="export-json"]').click()
            exported=qa/'NeuroFind-current.json';download.value.save_as(exported)
            assert json.loads(exported.read_text(encoding='utf-8'))==current
            page.locator('#import-file').set_input_files(str(exported))
            expect(page.locator('.imported-notice')).to_be_visible()
            with page.expect_download() as download:
                page.locator('.management-grid [data-action="download"]').click()
            saved=qa/'NeuroFind-offline-verified.html';download.value.save_as(saved)
            assert normalized(catalog(saved.read_text(encoding='utf-8')))==normalized(current)
            context.set_offline(True)
            offline=context.new_page();offline.on('pageerror',lambda err:errors.append(str(err)))
            offline.on('request',lambda r:network.append(r.url) if r.url.startswith(('http:','https:')) else None)
            offline.goto(saved.as_uri())
            expect(offline.locator('.test-card')).to_have_count(135)
            offline.locator('#search').fill('10001923')
            expect(offline.locator('.test-card')).to_have_count(1)
            offline.locator('.card-title').click()
            expect(offline.locator('#modal-body')).to_contain_text('10001926')
            assert not network and not errors, (network,errors)
            checks.append('JSON出力は全データ一致。取り込み→HTML保存→完全オフライン再読込はURL表記・空の受付状態を正規化して全データ一致、135項目・コード検索を保持、外部HTTP要求0・JS例外0')
            browser.close()
    finally: server.shutdown();server.server_close()
    result={'status':'PASS','date':'2026-11-12','dataVersion':current['version'],'tests':135,'changedTests':changed,'checks':checks,'url':target,'javascriptErrors':errors,'offlineExternalRequests':network,'scope':'差分の原典照合とChromiumでの機能検査。提出条件全体の医学監査・受託機関への直接照会は含まない。'}
    (qa/'cosmic-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
