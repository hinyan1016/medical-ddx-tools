"""追加データとは別の期待値で、公開・保存HTMLの検索と対象の取り違えを検査。"""
import argparse, json, re, subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, expect

base=Path(__file__).resolve().parent
repo=(base/'neurofind-work') if (base/'neurofind-work').exists() else base.parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
target=args.url or (repo/'neuro_test_navigator.html').as_uri()
out=base/('qa-live' if args.url else 'qa-kazusa');out.mkdir(exist_ok=True)
baseline=subprocess.check_output(['git','-C',str(repo),'show','2894419:neuro_test_navigator.html']).decode('utf-8')
before=json.loads(re.search(r'<script type="application/json" id="catalog-data">(.*?)</script>',baseline,re.S)[1])
expectations={'CARASIL':'htra1-gene','瀬川病':'hereditary-dystonia-panel','Wilson':'wilson-gene','HDLS':'hdls-gene','NAA60':'pfbc-gene','CYP27A1':'ctx-gene','CLCN1':'non-dystrophic-myotonia-gene','ASS1':'citrullinemia1-gene','SLC25A13':'citrin-gene','Krabbe':'krabbe-gene','Canavan':'canavan-gene','Perry':'perry-gene','那須ハコラ':'nasu-hakola-gene','Refsum':'refsum-gene','TSC2':'tsc-gene','PSMB8':'nakajo-nishimura-gene','AGL':'muscle-glycogen-gene','MEFV':'fmf-gene','HTRA1':'htra1-gene','GALC':'krabbe-gene','ARSA':'mld-gene','KCNJ5':'periodic-paralysis-gene','OTC':'urea-cycle-gene','Alexander':'alexander-gene','COL3A1':'vascular-eds-gene','AEBP1':'classical-eds-gene','SERPING1':'hae-complement-gene'}
errors=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch();ctx=browser.new_context(viewport={'width':1440,'height':1000},accept_downloads=True,service_workers='block');page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(target)
    d=json.loads(page.locator('#catalog-data').text_content());byid={t['id']:t for t in d['tests']};added=set(byid)-{t['id'] for t in before['tests']}
    assert len(byid)==131 and len(added)==26
    for t in before['tests']:assert byid[t['id']]==t,t['id']
    # 公開HTMLの個人連絡先・料金の混入を検知（既存部分と新規部分を分離）。
    for ident in added:
        t=byid[ident];s=json.dumps(t,ensure_ascii=False)
        assert not re.search(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\d{2,4}-\d{2,4}-\d{4}|\d[\d,]*[円点]',s),ident
        assert t['providers'][0]['checked']=='2026-11-04'
        assert t['review']=='source-checked'
    for q,ident in expectations.items():
        page.locator('#search').fill(q);expect(page.locator('[data-test-id="'+ident+'"]')).to_be_visible()
    page.locator('#search').fill('かずさDNA研究所');expect(page.locator('.test-card')).to_have_count(35)
    page.locator('#search').fill('');page.locator('#provider-filter').select_option('かずさ遺伝子検査室');expect(page.locator('.test-card')).to_have_count(35)
    page.screenshot(path=str(out/'kazusa-desktop.png'),full_page=True)
    for ident in sorted(added):
        page.locator('[data-test-id="'+ident+'"] .card-title').click();expect(page.locator('#modal-title')).to_have_text(byid[ident]['name']);expect(page.locator('.provider-card')).to_have_count(1);expect(page.locator('.provider-footer a').first).to_have_attribute('href',byid[ident]['providers'][0]['url']);page.keyboard.press('Escape')
    for ident in ['muscle-glycogen-gene','pompe-gene','liver-glycogen-gene']:page.locator('[data-compare="'+ident+'"]').check()
    page.locator('[data-action="compare"]').click();expect(page.locator('.comparison thead th')).to_have_count(4);page.screenshot(path=str(out/'glycogen-comparison.png'));page.keyboard.press('Escape')
    for width in [320,390,760,1024,1440]:
        page.set_viewport_size({'width':width,'height':900});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        for ident in ['hereditary-dystonia-panel','pfbc-gene','muscle-glycogen-gene']:
            page.locator('[data-test-id="'+ident+'"] .card-title').click();assert page.locator('.modal').evaluate('(el)=>el.scrollWidth<=el.clientWidth');page.screenshot(path=str(out/(str(width)+'-'+ident+'.png')));page.keyboard.press('Escape')
    assert not errors,errors
    browser.close()
result={'status':'PASS','url':target,'version':d['version'],'total':131,'added':26,'preservedExisting':105,'kazusaItems':35,'aliasQueries':len(expectations),'detailDialogs':26,'viewports':[320,390,760,1024,1440],'javascriptErrors':errors}
(out/'kazusa-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
