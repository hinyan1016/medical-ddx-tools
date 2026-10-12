# -*- coding: utf-8 -*-
"""実Chromiumでタブ文字・ボタンの重なり、折り返し、クリックを検証。"""
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
DEFAULT_HTML = HERE.parent.parent / 'vascular-territory-atlas.html'

MEASURE = r'''() => {
  const issues=[], groups=['.sidebar-tabs','.plane-tabs','.view-header','.coord-form'];
  const visible=e=>e.getClientRects().length && getComputedStyle(e).visibility!=='hidden';
  const intersect=(a,b)=>Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1;
  const inside=(a,b)=>a.left>=b.left-1 && a.right<=b.right+1 && a.top>=b.top-1 && a.bottom<=b.bottom+1;
  for(const selector of groups) for(const group of document.querySelectorAll(selector)) {
    if(!visible(group))continue;
    const children=[...group.children].filter(visible), gr=group.getBoundingClientRect();
    for(const child of children) {
      const cr=child.getBoundingClientRect();
      if(!inside(cr,gr))issues.push(selector+' child outside: '+child.textContent.trim());
    }
    for(let i=0;i<children.length;i++)for(let j=i+1;j<children.length;j++)
      if(intersect(children[i].getBoundingClientRect(),children[j].getBoundingClientRect()))issues.push(selector+' boxes overlap');
  }
  for(const btn of document.querySelectorAll('.sidebar-tabs button,.plane-tabs button,.view3d-ctrl button')) {
    if(!visible(btn))continue;
    const range=document.createRange();range.selectNodeContents(btn);
    for(const tr of range.getClientRects()) if(!inside(tr,btn.getBoundingClientRect()))issues.push('text outside button: '+btn.textContent.trim());
  }
  const sidebar=document.querySelector('.sidebar-tabs'), rows=[...new Set([...sidebar.children].map(e=>Math.round(e.getBoundingClientRect().top)))];
  const active=document.querySelector('.sidebar-content.on');
  if(active && active.getBoundingClientRect().top<sidebar.getBoundingClientRect().bottom-1)issues.push('tab content overlaps tabs');
  if(document.documentElement.scrollWidth>innerWidth+1)issues.push('document horizontal overflow');
  const wrap=document.querySelector('#wrap-3d');
  if(visible(wrap)){
    const a=wrap.querySelector('.view3d-ctrl'),b=wrap.querySelector('.zoom-ctrl');
    if(a&&b&&intersect(a.getBoundingClientRect(),b.getBoundingClientRect()))issues.push('3D controls overlap zoom');
    for(const c of [a,b])if(c&&!inside(c.getBoundingClientRect(),wrap.getBoundingClientRect()))issues.push('3D control outside canvas');
  }
  return {issues,tabRows:rows.length,tabHeight:sidebar.getBoundingClientRect().height,scrollWidth:document.documentElement.scrollWidth,innerWidth,innerHeight,devicePixelRatio};
}'''

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--html',default=str(DEFAULT_HTML));ap.add_argument('--url')
    ap.add_argument('--shots',default=str(HERE/'atlas-qa/layout'));ap.add_argument('--report',default=str(HERE/'atlas-layout-validation.json'))
    args=ap.parse_args();shots=Path(args.shots);shots.mkdir(parents=True,exist_ok=True)
    url=args.url or Path(args.html).resolve().as_uri()
    # ChromiumのCSS viewport/DPRを125/150/200%のブラウザ拡大時と同じ条件にする。
    cases=[('desktop',1440,960,1),('desktop1280',1280,900,1),('narrow',1024,768,1),('breakpoint901',901,768,1),('tablet900',900,768,1),('attachment-width',634,768,1),('mobile',390,844,2),('small-mobile',320,720,2),('zoom125-equivalent',1152,768,1.25),('zoom150-equivalent',960,640,1.5),('zoom200-equivalent',720,480,2)]
    report={'url':url,'zoom_method':'CSS viewport and DPR equivalent to 1440x960 at 125/150/200%; native browser zoom shortcuts are not used','cases':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch();report['browser']=browser.version
        for name,w,h,dpr in cases:
            ctx=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=dpr,is_mobile=w<=390,has_touch=w<=390)
            pg=ctx.new_page();errors=[];pg.on('pageerror',lambda e:errors.append(str(e)))
            pg.goto(url+'#x=-24&y=-10&z=4&lv=1',wait_until='domcontentloaded');pg.wait_for_function('window.__learning && window.__atlas')
            for tab in ['info','learning','list','lookup','lesion','quiz','settings']:
                pg.locator('[data-tab="'+tab+'"]').click()
                assert pg.locator('#tab-'+tab).evaluate("e=>e.classList.contains('on')"),tab
                state=pg.evaluate(MEASURE);assert not state['issues'],(name,tab,state)
            pg.click('[data-tab="learning"]');pg.locator('[data-tract="jhu_2"]').check();pg.click('#btn-tract-3d')
            pg.wait_for_function('window.__learning.T3.stats.selected===1 && window.__learning.T3.stats.pixels.jhu_2>0')
            for layout in ['axial','coronal','sagittal','3d','all','3d']:
                pg.locator('[data-layout="'+layout+'"]').click()
                assert pg.evaluate('window.__atlas.S.layout')==layout,layout
                state=pg.evaluate(MEASURE);assert not state['issues'],(name,layout,state)
            for view in ['front','top']:
                pg.locator('[data-view3d="'+view+'"]').click()
            pg.select_option('#sel-3dmode','all');pg.select_option('#sel-3dmode','tracts')
            assert pg.evaluate('window.__atlas.R3.mode')=='tracts'
            for level in ['2','1']:pg.click('[data-level="'+level+'"]')
            state=pg.evaluate(MEASURE);assert not state['issues'],(name,state);assert state['tabRows']==2
            pg.evaluate('window.scrollTo(0,0)')
            if name in ['desktop1280','mobile','zoom150-equivalent','zoom200-equivalent']:
                pg.screenshot(path=str(shots/(name+'.png')))
                pg.locator('#sidebar-tabs').screenshot(path=str(shots/(name+'-tabs.png')))
            # 将来さらに長い日本語名称になっても高さを固定せず、文字を内側で折り返す。
            pg.evaluate("document.querySelector('[data-tab=learning]').textContent='脳の解剖構造と神経束の立体表示・詳細な学習情報'; document.querySelector('[data-layout=all]').textContent='すべての断面と三次元表示を同時に表示';")
            long_state=pg.evaluate(MEASURE);assert not long_state['issues'],(name,'long labels',long_state)
            pg.click('[data-tab="info"]');pg.click('[data-tab="learning"]');pg.click('[data-layout="all"]');pg.click('[data-layout="3d"]')
            long_state=pg.evaluate(MEASURE);assert not long_state['issues'],(name,'long labels clicked',long_state)
            if name in ['desktop1280','small-mobile']:
                pg.locator('#sidebar-tabs').screenshot(path=str(shots/(name+'-long-tabs.png')))
            assert not errors,(name,errors)
            report['cases'].append({'name':name,'normal':state,'longLabels':long_state,'allTabsClicked':True,'allLayoutsClicked':True,'3dControlsClicked':True,'errors':errors})
            print('PASS '+name,flush=True);ctx.close()
        browser.close()
    Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
