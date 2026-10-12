# -*- coding: utf-8 -*-
"""追加アトラスの実データ照合・完全affine・断面/UI/オフライン回帰。"""
import argparse
import json
import time
import zipfile
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
from build_data import read_nifti

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html', nargs='?', default=str(HERE.parent.parent / 'vascular-territory-atlas.html'))
    ap.add_argument('--shots', required=True)
    args = ap.parse_args()
    shots = Path(args.shots); shots.mkdir(parents=True, exist_ok=True)
    meta = json.loads((HERE / 'learning.json').read_text(encoding='utf8'))
    assert len(meta['tracts']) == 20
    assert sum(t['side'] == 'C' for t in meta['tracts']) == 2
    assert sum(t['side'] == 'L' for t in meta['tracts']) == 9
    assert sum(t['side'] == 'R' for t in meta['tracts']) == 9
    for group in ('cort', 'sub'):
        for idx, row in enumerate(meta['anatomy'][group]):
            assert row['source_index'] == idx and row['label'] == idx + 1
    source, aff = read_nifti(HERE / 'sources/JHU-ICBM-tracts-prob-2mm.nii.gz')
    rng = np.random.default_rng(712)
    # 独立した原NIfTIと全チャネルを比較（反転補充・max正規化・名称ずれを検出）。
    points = [(tuple(np.unravel_index(np.argmax(source[..., i]), source.shape[:3])), i) for i in range(20)]
    points += [(tuple(rng.integers([0, 0, 0], source.shape[:3])), i) for i in range(20)]
    url = Path(args.html).resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={'width':1600,'height':1000})
        pg = ctx.new_page(); errors=[]; pg.on('pageerror', lambda e: errors.append(str(e)))
        requests=[]; pg.on('request', lambda r: requests.append(r.url))
        start=time.perf_counter(); pg.goto(url+'#x=-24&y=-10&z=4&lv=1')
        pg.wait_for_function('window.__learning && window.__atlas', timeout=45000)
        print('Initial load %.2fs' % (time.perf_counter()-start))
        for ijk,c in points:
            mm=(aff@np.array([*ijk,1]))[:3].tolist()
            v=pg.evaluate('(a)=>window.__learning.sample(window.__learning.G.vols.tracts_jhu,a[0],a[1],true)',[mm,c])
            assert abs(v-float(source[*ijk,c]))<1e-5, (ijk,c,v)
        print('PASS 原NIfTI20チャネルと左右別データの照合')
        vals=pg.evaluate('''() => {
          var L=window.__learning;
          var v={meta:{dims:[2,2,2]}, nvox:8, data:new Uint8Array([0,1,2,3,4,5,6,7]), inv:[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]};
          var direct=[L.sample(v,[0.5,0.5,0.5],0,true),L.sample(v,[1,1,1],0,true),L.sample(v,[-0.001,0,0],0,true),L.sample(v,[0.49,0,0],0,false)];
          // source voxel -> mm = [2j+10, -2i+20, 2k-30] (90-degree rotation + LAS)
          v.inv=[0,-0.5,0,10,0.5,0,0,-5,0,0,0.5,15,0,0,0,1];
          direct.push(L.sample(v,[11,19,-29],0,true));
          // source voxel -> mm = [2i+j+10,2j+20,2k-30] (shear)
          v.inv=[0.5,-0.25,0,0,0,0.5,0,-10,0,0,0.5,15,0,0,0,1];
          direct.push(L.sample(v,[11.5,21,-29],0,true));
          // 半ボクセル原点
          v.inv=[1,0,0,-0.5,0,1,0,-0.5,0,0,1,-0.5,0,0,0,1];
          direct.push(L.sample(v,[1,1,1],0,true)); return direct;
        }''')
        assert vals==[3.5,7,None,0,3.5,3.5,3.5], vals
        print('PASS 回転・せん断・半ボクセル・端面・範囲外・最近傍/連続補間')
        ho,haff=read_nifti(HERE/'sources/HarvardOxford-sub-maxprob-thr0-2mm.nii.gz')
        for label in [4,6,9,15,17,19]:
            ijk=np.argwhere(ho==label)[len(np.argwhere(ho==label))//2]
            mm=(haff@np.array([*ijk,1]))[:3].tolist()
            result=pg.evaluate('(mm)=>window.__learning.anatomyAt(mm)',mm)
            sub=[g for g in result['groups'] if g['key']=='sub'][0]
            assert sub['label']==label, (label,sub)
            assert sub['candidates']
            assert (mm[0]<0)==(label<12), (label,mm)
        assert all(g.get('outside') for g in pg.evaluate('window.__learning.anatomyAt([500,500,500])')['groups'])
        print('PASS 原maxprobの左右視床・被殻・海馬とXML label=index+1')
        # UI操作だけで選択・移動。断面画素が変わり、比較も保持される。
        pg.click('[data-tab="learning"]')
        assert pg.locator('[data-tract]').count()==20
        pg.fill('#tract-search','ILF')
        assert pg.locator('.tract-choice:visible').count()==2
        pg.fill('#tract-search','')
        pg.evaluate('window.__atlas.setCursorMM(-14,-18,6)')
        before=pg.evaluate('Array.from(window.__atlas.V.axial.oimg.data)')
        pg.locator('[data-tract="jhu_2"]').check()
        pg.wait_for_timeout(400)
        after=pg.evaluate('Array.from(window.__atlas.V.axial.oimg.data)')
        assert before!=after
        pg.locator('[data-tract="jhu_3"]').check()
        pg.locator('[data-tract-jump="jhu_12"]').click()
        pg.wait_for_timeout(500)
        assert pg.evaluate('window.__atlas.vox2mm(window.__atlas.S.i,window.__atlas.S.j,window.__atlas.S.k)[0]')<0
        pg.locator('[data-tract-jump="jhu_13"]').click(); pg.wait_for_timeout(300)
        assert pg.evaluate('window.__atlas.vox2mm(window.__atlas.S.i,window.__atlas.S.j,window.__atlas.S.k)[0]')>0
        assert len(pg.evaluate('Object.keys(window.__learning.G.selected)'))==4
        pg.locator('#sl-tract-threshold').fill('95'); pg.locator('#sl-tract-threshold').dispatch_event('input')
        assert 'しきい値未満' in pg.locator('#tract-position').inner_text()
        pg.locator('#sl-tract-opacity').fill('0'); pg.locator('#sl-tract-opacity').dispatch_event('input')
        assert pg.evaluate('window.__learning.G.opacity')==0
        pg.locator('#sl-tract-threshold').fill('10'); pg.locator('#sl-tract-threshold').dispatch_event('input')
        pg.locator('#sl-tract-opacity').fill('65'); pg.locator('#sl-tract-opacity').dispatch_event('input'); pg.wait_for_timeout(350)
        hash=pg.evaluate('location.hash'); assert 'tracts=' in hash and 'tt=10' in hash
        pg.screenshot(path=str(shots/'learning-desktop.png'))
        pg.reload(); pg.wait_for_function('window.__learning && window.__atlas'); assert len(pg.evaluate('Object.keys(window.__learning.G.selected)'))==4
        print('PASS 検索・複数束・左右移動・透明度/しきい値・URL再読込')
        pg.click('[data-tab="quiz"]'); pg.click('#btn-quiz-start'); pg.wait_for_timeout(300)
        assert 'クイズ中' in pg.locator('#learning-position').inner_text()
        assert pg.evaluate('window.__atlas.S.hideOverlay')
        pg.click('[data-tab="learning"]')
        assert not pg.evaluate('window.__atlas.S.hideOverlay')  # 既存仕様: 別タブへ移動するとクイズ終了
        # オフライン読み込み時に外部ネットワークを要求しない。
        assert not [r for r in requests if r.startswith('http')], requests
        assert not errors, errors
        # 全20構造同時表示の処理時間（測定、速度保証ではない）。
        t=time.perf_counter(); pg.evaluate('''() => { var G=window.__learning.G; for(var i=0;i<20;i++) G.selected['jhu_'+i]=true; window.__atlas.setCursorMM(-20,-20,20); }''')
        pg.wait_for_timeout(100); print('20 structures render roundtrip %.2fs' % (time.perf_counter()-t))
        mob=b.new_context(viewport={'width':390,'height':844},device_scale_factor=2,is_mobile=True,has_touch=True)
        mp=mob.new_page(); mp.goto(url); mp.wait_for_function('window.__learning && window.__atlas')
        mp.click('[data-tab="learning"]'); mp.locator('[data-tract-jump="jhu_2"]').click(); mp.wait_for_timeout(500)
        assert mp.evaluate('document.documentElement.scrollWidth')<=392
        assert mp.evaluate('window.__atlas.S.layout')=='axial'
        mp.screenshot(path=str(shots/'learning-mobile.png'),full_page=True)
        mp.screenshot(path=str(shots/'learning-mobile-top.png'))
        with mp.expect_download() as dl:
            mp.click('#btn-standalone')
        single=shots/'saved-standalone.html'; dl.value.save_as(single)
        saved=b.new_page(); saved.goto(single.resolve().as_uri()); saved.wait_for_function('window.__learning && window.__atlas',timeout=45000)
        assert saved.locator('[data-tract]').count()==20
        assert len(saved.evaluate('Object.keys(window.__learning.G.vols)'))==5
        # 新データでも旧ブラウザ用 inflate 経路を確認。
        fallback=b.new_context(); fallback.add_init_script('delete window.DecompressionStream;')
        fp=fallback.new_page(); fp.goto(url); fp.wait_for_function('window.__learning && window.__atlas',timeout=60000)
        t0=meta['tracts'][2]; mm=t0['center_mm']
        val=fp.evaluate('(mm)=>window.__learning.sample(window.__learning.G.vols.tracts_jhu,mm,2,true)',mm)
        orig=pg.evaluate('(mm)=>window.__learning.sample(window.__learning.G.vols.tracts_jhu,mm,2,true)',mm)
        assert val==orig and val>0
        print('PASS 単体HTML保存後の再読込と新データinflate互換')
        print('PASS クイズ非表示・外部要求ゼロ・モバイル表示')
        b.close()
    zpath=HERE.parent.parent/'downloads/MNI_Vascular_Territory_Atlas_Standalone.zip'
    with zipfile.ZipFile(zpath) as z:
        names=z.namelist()
        for f in ['source/sources/JHU-tracts.xml','source/sources/JHU-ICBM-tracts-prob-2mm.nii.gz','source/licenses/FSL-LICENSE.txt','source/licenses/CC-BY-SA-4.0.txt','source/build_learning.py','source/learning.js','source/template.html']:
            assert f in names, f
        assert any(n.endswith('.html') and not n.startswith('source/') for n in names)
    print('PASS 原データ/XML/加工ソース/ライセンス同梱')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
