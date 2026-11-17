import json,re,subprocess,threading,functools,argparse,hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright,expect
R=Path(__file__).resolve().parents[2];S=Path(__file__).parent
def catalog(h):return json.loads(re.search(r'<script[^>]*id="catalog-data"[^>]*>(.*?)</script>',h,re.S).group(1))
def main():
 p=argparse.ArgumentParser();p.add_argument('--url');p.add_argument('--artifacts',required=True);args=p.parse_args();qa=Path(args.artifacts);qa.mkdir(parents=True,exist_ok=True)
 h=(R/'neuro_test_navigator.html').read_text(encoding='utf-8');d=catalog(h);record=json.loads((S/'publication.json').read_text(encoding='utf-8'))
 old=catalog(subprocess.check_output(['git','show',record['sourceCommit']+':neuro_test_navigator.html'],cwd=R).decode())
 assert d['tests'][:-1]==old['tests'] and len(d['tests'])==136
 assert d['coverage']==old['coverage'] and d['updates']==old['updates']
 assert '綾木' not in h and len({t['id'] for t in d['tests']})==136
 assert hashlib.sha256((R/'neuro_test_navigator.html').read_bytes()).hexdigest()==record['publicHtmlSha256']
 server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(SimpleHTTPRequestHandler,directory=str(R)));threading.Thread(target=server.serve_forever,daemon=True).start()
 errors=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch();ctx=b.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,service_workers='block');page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(args.url or f'http://127.0.0.1:{server.server_port}/neuro_test_navigator.html',wait_until='networkidle');assert catalog(page.content())==d
  expect(page.locator('.test-card')).to_have_count(136)
  for q in ['ライム病','ボレリア','Lyme','03833','神経ボレリア症']:
   page.locator('#search').fill(q);expect(page.locator('[data-test-id="lyme-borreliosis"]')).to_be_visible()
  page.locator('[data-test-id="lyme-borreliosis"] .card-title').click();expect(page.locator('.provider-card')).to_have_count(2);expect(page.locator('#modal-body')).to_contain_text('行政検査');expect(page.locator('#modal-body')).to_contain_text('14～21日')
  for w in [1440,390,320]:
   page.set_viewport_size({'width':w,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');assert page.locator('#modal-body').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1');page.screenshot(path=str(qa/f'detail-{w}.png'))
  page.keyboard.press('Escape');page.set_viewport_size({'width':1440,'height':1000});page.locator('[data-action="manage"]').first.click()
  with page.expect_download() as dl:page.locator('[data-action="export-json"]').click()
  exported=qa/'NeuroFind-current.json';dl.value.save_as(exported);assert json.loads(exported.read_text(encoding='utf-8'))==d
  page.locator('#import-file').set_input_files(str(exported));expect(page.locator('.imported-notice')).to_be_visible()
  with page.expect_download() as dl:page.locator('.management-grid [data-action="download"]').click()
  offline=qa/'NeuroFind-offline.html';dl.value.save_as(offline);ctx.set_offline(True);page.goto(offline.as_uri());page.locator('#search').fill('ライム病');expect(page.locator('[data-test-id="lyme-borreliosis"]')).to_be_visible();page.locator('[data-test-id="lyme-borreliosis"] .card-title').click();expect(page.locator('.provider-card')).to_have_count(2)
  assert not errors,errors;b.close()
 server.shutdown();print('PASS: 135 existing records unchanged; 136 unique records; search, details, desktop/mobile, JSON import/export and offline HTML verified')
if __name__=='__main__':main()
