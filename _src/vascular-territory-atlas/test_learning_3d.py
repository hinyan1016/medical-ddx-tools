# -*- coding: utf-8 -*-
"""神経束3D: 原2mm境界全点、左右/交連、透明比較、閾値再生成、実Chromium/モバイル。"""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from build_data import read_nifti

HERE=Path(__file__).resolve().parent


def expected_surface(data, threshold):
    m=data>=threshold
    padded=np.pad(m,1)
    inside=padded[0:-2,1:-1,1:-1] & padded[2:,1:-1,1:-1] & padded[1:-1,0:-2,1:-1] & padded[1:-1,2:,1:-1] & padded[1:-1,1:-1,0:-2] & padded[1:-1,1:-1,2:]
    return int((m & ~inside).sum()),int(m.sum())


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--html',default=str(HERE.parent.parent/'vascular-territory-atlas.html')); ap.add_argument('--shots',required=True); a=ap.parse_args()
    shots=Path(a.shots); shots.mkdir(parents=True,exist_ok=True)
    source,aff=read_nifti(HERE/'sources/JHU-ICBM-tracts-prob-2mm.nii.gz')
    url=Path(a.html).resolve().as_uri()
    with sync_playwright() as p:
        b=p.chromium.launch(); ctx=b.new_context(viewport={'width':1440,'height':960}); pg=ctx.new_page(); errors=[]; pg.on('pageerror',lambda e:errors.append(str(e)))
        pg.goto(url+'#x=-18&y=-18&z=6'); pg.wait_for_function('window.__learning && window.__atlas')
        pg.click('[data-tab="learning"]'); pg.locator('[data-tract="jhu_2"]').check(); pg.locator('[data-tract="jhu_3"]').check(); pg.click('#btn-tract-3d')
        pg.wait_for_function('window.__learning.T3.stats.selected===2 && window.__learning.T3.stats.pixels.jhu_2>0')
        assert pg.evaluate('window.__atlas.R3.mode')=='tracts'
        assert '個人の線維追跡' in pg.locator('#tract3d-status').inner_text()
        pg.click('[data-view3d="front"]'); pg.wait_for_timeout(200)
        geometry=pg.evaluate('''() => { var l=window.__learning,out={}; for(var k in l.T3.surfaces){var s=l.T3.surfaces[k],mn=1e9,mx=-1e9;for(var i=0;i<s.n;i++){mn=Math.min(mn,s.pts[i*3]);mx=Math.max(mx,s.pts[i*3]);}out[k]={n:s.n,count:s.count,minx:mn,maxx:mx};} return out;}''')
        for channel in [2,3]:
            exp,count=expected_surface(source[...,channel],10); d=geometry['jhu_'+str(channel)]
            assert (d['n'],d['count'])==(exp,count),(channel,d,exp,count)
        assert geometry['jhu_2']['minx']<0 and geometry['jhu_3']['maxx']>0
        projection=pg.evaluate('''() => { var a=window.__atlas,l=window.__learning; var L=l.G.vols.tracts_jhu.meta.affine;var out1=[0,0,0],out2=[0,0,0];a.R3.project(-18,-18,6,out1);a.R3.project(18,-18,6,out2);return [out1[0],out2[0]];}''')
        assert projection[0]>projection[1]  # 前から見た患者左が画面右
        pg.screenshot(path=str(shots/'cst-bilateral-front.png')); pg.locator('#wrap-3d').screenshot(path=str(shots/'cst-front-canvas.png'))
        print('PASS CST左右、前面の方向、原2mm全境界点一致')
        # 3D画質の血管間引き設定を変えても、細い束を追加で間引かない。
        n0=geometry['jhu_2']['n']; options=pg.locator('#sel-3dq option').all(); last=options[-1].get_attribute('value')
        pg.click('[data-tab="settings"]')
        pg.select_option('#sel-3dq',last); pg.wait_for_timeout(200)
        pg.click('[data-tab="learning"]')
        assert pg.evaluate('window.__learning.T3.surfaces.jhu_2.n')==n0
        pg.locator('[data-tract="jhu_2"]').uncheck(); pg.wait_for_timeout(200)
        assert 'jhu_2' not in pg.evaluate('Object.keys(window.__learning.T3.surfaces)')
        assert pg.evaluate('window.__learning.T3.stats.pixels.jhu_3')>0
        pg.locator('[data-tract="jhu_2"]').check()
        pg.wait_for_function('window.__learning.T3.stats.selected===2 && window.__learning.T3.surfaces.jhu_2')
        pg.wait_for_timeout(100)
        # 回転・ズームが実操作で反映され、幾何を再生成しない。
        builds=pg.evaluate('window.__learning.T3.builds'); yaw=pg.evaluate('window.__atlas.R3.yaw'); box=pg.locator('#canvas-3d').bounding_box()
        pg.mouse.move(box['x']+box['width']*.55,box['y']+box['height']*.5); pg.mouse.down(); pg.mouse.move(box['x']+box['width']*.55+70,box['y']+box['height']*.5+25,steps=6); pg.mouse.up(); pg.wait_for_timeout(250)
        assert pg.evaluate('window.__atlas.R3.yaw')!=yaw
        zoom=pg.evaluate('window.__atlas.R3.zoom'); pg.locator('#panel-3d [data-zoom="in"]').click(); pg.wait_for_timeout(150)
        assert pg.evaluate('window.__atlas.R3.zoom')>zoom
        assert pg.evaluate('window.__learning.T3.builds')==builds
        pg.screenshot(path=str(shots/'cst-oblique.png'))
        pg.click('#chk-tract-brain'); pg.wait_for_timeout(150); assert not pg.evaluate('window.__learning.T3.brain')
        pg.click('#chk-tract-brain'); pg.wait_for_timeout(150)
        pg.locator('#sl-tract-opacity').fill('0'); pg.locator('#sl-tract-opacity').dispatch_event('input'); pg.wait_for_timeout(100)
        assert pg.evaluate('Object.keys(window.__learning.T3.stats.pixels).length')==0
        pg.locator('#sl-tract-opacity').fill('65'); pg.locator('#sl-tract-opacity').dispatch_event('input')
        pg.locator('#sl-tract-threshold').fill('95'); pg.locator('#sl-tract-threshold').dispatch_event('input'); pg.wait_for_timeout(200)
        assert pg.evaluate('window.__learning.T3.surfaces.jhu_2.n')==0
        assert '閾値以上なし' in pg.locator('#tract3d-status').inner_text()
        pg.locator('#sl-tract-threshold').fill('10'); pg.locator('#sl-tract-threshold').dispatch_event('input'); pg.wait_for_timeout(200)
        assert pg.evaluate('window.__learning.T3.surfaces.jhu_2.n')==n0
        print('PASS 細い領域保持・再選択・回転/ズーム・透明度/閾値変更・脳表参照切替')
        # 交連束は左右別と捏造せず、実データが正中をまたぐことを確認。
        pg.click('#btn-tract-clear'); pg.wait_for_timeout(150)
        assert pg.evaluate('Object.keys(window.__learning.T3.surfaces).length')==0
        for channel in [8,9]: pg.locator('[data-tract="jhu_'+str(channel)+'"]').check()
        pg.wait_for_timeout(250); pg.click('[data-view3d="top"]'); pg.wait_for_timeout(150)
        cc=pg.evaluate('''() => { var out={};[8,9].forEach(function(id){var s=window.__learning.T3.surfaces['jhu_'+id],mn=999,mx=-999;for(var i=0;i<s.n;i++){mn=Math.min(mn,s.pts[i*3]);mx=Math.max(mx,s.pts[i*3]);}out[id]=[mn,mx,s.n];});return out;}''')
        for k in ['8','9']: assert cc[k][0]<0<cc[k][1] and cc[k][2]>0
        pg.screenshot(path=str(shots/'forceps-top.png'))
        pg.wait_for_timeout(300); hash=pg.evaluate('location.hash'); assert 'd3t=1' in hash
        pg.reload(); pg.wait_for_function('window.__learning && window.__atlas'); pg.wait_for_timeout(300)
        assert pg.evaluate('window.__atlas.R3.mode')=='tracts' and pg.evaluate('window.__atlas.S.layout')=='3d'
        assert pg.evaluate('window.__atlas.S.activeView')=='3d'
        assert pg.evaluate('window.__learning.T3.stats.selected')==2
        print('PASS 脳梁大鉗子/小鉗子の正中越え、全解除、3D URL再読込')
        # 全20チャンネルを比較、独立surfaceがすべて表示画素を持つ。
        pg.click('[data-tab="learning"]'); t=time.perf_counter()
        for i in range(20): pg.locator('[data-tract="jhu_'+str(i)+'"]').check()
        pg.wait_for_function('window.__learning.T3.stats.selected===20'); pg.wait_for_timeout(100)
        stats=pg.evaluate('window.__learning.T3.stats'); print('20 structures select/render %.2fs' % (time.perf_counter()-t))
        for i in range(20):
            exp,count=expected_surface(source[...,i],10)
            assert pg.evaluate('(id)=>window.__learning.T3.surfaces[id].n','jhu_'+str(i))==exp
            assert stats['pixels']['jhu_'+str(i)]>0,(i,stats)
        pg.evaluate("window.__atlas.R3.setView('home')"); pg.wait_for_timeout(200)
        pg.screenshot(path=str(shots/'all20-oblique.png'))
        print('PASS 全20構造の原NIfTI境界一致・個別描画画素あり')
        pg.select_option('#sel-3dmode','all'); pg.wait_for_timeout(200); assert not pg.locator('#tract3d-status').is_visible()
        pg.select_option('#sel-3dmode','tracts'); pg.wait_for_timeout(200); assert pg.evaluate('window.__learning.T3.stats.selected')==20
        pg.click('[data-tab="quiz"]'); pg.click('#btn-quiz-start'); pg.wait_for_timeout(200)
        assert 'クイズ中' in pg.locator('#tract3d-status').inner_text()
        assert 'MNI' not in pg.locator('#tract3d-status').inner_text()
        assert not pg.evaluate('Object.keys(window.__learning.T3.stats.pixels).length')
        pg.click('[data-tab="learning"]'); pg.wait_for_timeout(200)
        pg.click('#btn-tract-clear'); pg.wait_for_timeout(100); assert pg.evaluate('window.__learning.T3.stats.selected')==0
        assert not errors,errors
        print('PASS 血管/神経束モード往復・全解除・コンソールエラーなし')
        mobile=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True); mp=mobile.new_page(); mp.goto(url); mp.wait_for_function('window.__learning && window.__atlas')
        mp.click('[data-tab="learning"]'); mp.locator('[data-tract="jhu_2"]').check(); mp.locator('[data-tract="jhu_14"]').check(); mp.click('#btn-tract-3d'); mp.wait_for_function('window.__learning.T3.stats.selected===2'); mp.wait_for_timeout(200)
        assert mp.evaluate('document.documentElement.scrollWidth')<=392
        assert mp.locator('#canvas-3d').bounding_box()['height']>100
        mp.evaluate('window.scrollTo(0,0)'); mp.screenshot(path=str(shots/'mobile-3d.png'))
        mp.locator('#wrap-3d').screenshot(path=str(shots/'mobile-3d-canvas.png'))
        gesture=mp.evaluate('''() => {
          var c=document.getElementById('canvas-3d'), r=c.getBoundingClientRect(), a=window.__atlas.R3, yaw=a.yaw, zoom=a.zoom;
          function send(type,pts){var ev=new Event(type,{bubbles:true,cancelable:true});ev.touches=pts.map(function(p){return {clientX:r.left+p[0],clientY:r.top+p[1]};});c.dispatchEvent(ev);}
          send('touchstart',[[100,100]]);send('touchmove',[[140,115]]);send('touchend',[]);
          send('touchstart',[[100,100],[160,100]]);send('touchmove',[[80,100],[180,100]]);send('touchend',[]);
          return [a.yaw!==yaw,a.zoom>zoom];
        }'''); assert gesture==[True,True]
        t=time.perf_counter(); mp.evaluate('''() => {document.querySelectorAll('[data-tract]').forEach(function(el){el.checked=true;el.dispatchEvent(new Event('change',{bubbles:true}));});}''')
        mp.wait_for_function('window.__learning.T3.stats.selected===20'); mp.wait_for_timeout(100)
        assert all(v>0 for v in mp.evaluate('window.__learning.T3.stats.pixels').values())
        print('Mobile 20 structures select/render %.2fs' % (time.perf_counter()-t))
        print('PASS 390pxタッチ端末エミュレーション・3D複数選択表示')
        b.close()
    return 0


if __name__=='__main__': raise SystemExit(main())
