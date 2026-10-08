# -*- coding: utf-8 -*-
"""血管支配領域アトラスの動作確認（Playwright / Chromium）。

  python test_atlas.py [HTMLのパス] [--shots <スクリーンショットの保存先>]

確認すること:
  - 読み込み時にコンソールエラーが出ない
  - MNI 座標の左右（左半球ラベルで X が負）と代表断面のラベル
  - URL ハッシュでの位置指定
  - DecompressionStream が無いブラウザ向けの inflate 経路
  - NIfTI 読込（sform あり・qform のみ・gzip）と病変集計
  - ブラシでの病変描画・逆引き・クイズ・3D 表示が例外なく動く
exit 0 = 全項目合格 / 1 = 不合格あり
"""
import argparse
import gzip
import struct
import sys
import tempfile
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FAILS = []


def check(cond, msg):
    print(('  OK   ' if cond else '  FAIL ') + msg)
    if not cond:
        FAILS.append(msg)


def make_nifti(path, shape, affine, data, use_sform=True, gz=False, dtype=np.uint8):
    """最小の NIfTI-1 を書く（テスト用の病変マスク）"""
    hdr = bytearray(348)
    struct.pack_into('<i', hdr, 0, 348)
    dims = [3, shape[0], shape[1], shape[2], 1, 1, 1, 1]
    struct.pack_into('<8h', hdr, 40, *dims)
    code = {np.uint8: 2, np.float32: 16, np.int16: 4}[dtype]
    struct.pack_into('<h', hdr, 70, code)
    struct.pack_into('<h', hdr, 72, np.dtype(dtype).itemsize * 8)
    vx = [abs(affine[0][0]), abs(affine[1][1]), abs(affine[2][2])]
    qfac = 1.0
    struct.pack_into('<8f', hdr, 76, qfac, vx[0], vx[1], vx[2], 0, 0, 0, 0)
    struct.pack_into('<f', hdr, 108, 352.0)
    struct.pack_into('<2f', hdr, 112, 1.0, 0.0)
    if use_sform:
        struct.pack_into('<2h', hdr, 252, 0, 1)
        struct.pack_into('<12f', hdr, 280, *[float(v) for row in affine[:3] for v in row])
    else:
        # x 軸だけ反転（LAS）: 四元数 b=0,c=1,d=0 → R=diag(-1,1,-1)、qfac=-1 で z を戻す
        struct.pack_into('<2h', hdr, 252, 1, 0)
        struct.pack_into('<6f', hdr, 256, 0.0, 1.0, 0.0, affine[0][3], affine[1][3], affine[2][3])
        struct.pack_into('<f', hdr, 76, -1.0)
    hdr[344:348] = b'n+1\x00'
    body = bytes(hdr) + b'\x00' * 4 + np.asarray(data, dtype=dtype).transpose(2, 1, 0).tobytes()
    if gz:
        body = gzip.compress(body)
    Path(path).write_bytes(body)


def sphere_mask(shape, affine, center_mm, radius):
    inv = np.linalg.inv(np.array(affine, dtype=float))
    i, j, k = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), np.arange(shape[2]), indexing='ij')
    A = np.array(affine, dtype=float)
    x = A[0, 0] * i + A[0, 3]
    y = A[1, 1] * j + A[1, 3]
    z = A[2, 2] * k + A[2, 3]
    d2 = (x - center_mm[0]) ** 2 + (y - center_mm[1]) ** 2 + (z - center_mm[2]) ** 2
    _ = inv
    return (d2 <= radius ** 2).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html', nargs='?', default=str(HERE.parent.parent / 'vascular-territory-atlas.html'))
    ap.add_argument('--shots', default=None)
    args = ap.parse_args()
    url = Path(args.html).resolve().as_uri()
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix='atlas_test_'))

    # テスト用病変: 左被殻付近の球（FSL 1mm 格子・sform）／同じ球を 2mm・qform のみ・gzip
    aff1 = [[-1, 0, 0, 90], [0, 1, 0, -126], [0, 0, 1, -72], [0, 0, 0, 1]]
    m1 = sphere_mask((182, 218, 182), aff1, (-24, 2, 2), 6)
    make_nifti(tmp / 'lesion_1mm.nii', (182, 218, 182), aff1, m1)
    aff2 = [[-2, 0, 0, 90], [0, 2, 0, -126], [0, 0, 2, -72], [0, 0, 0, 1]]
    m2 = sphere_mask((91, 109, 91), aff2, (24, 2, 2), 6)  # 右側
    make_nifti(tmp / 'lesion_2mm_q.nii.gz', (91, 109, 91), aff2, m2, use_sform=False, gz=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={'width': 1600, 'height': 1000})
        page = ctx.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.goto(url + '#x=-38&y=-20&z=56&lv=1')
        page.wait_for_function('window.__atlas && window.__atlas.A.l1', timeout=30000)
        page.wait_for_timeout(400)
        print('[読み込み]')
        code = page.evaluate('(function(){var a=window.__atlas;var i=a.labelInfo(a.S.level,a.currentLabelId());return i?i.code:null;})()')
        check(code == 'MCAFL', 'ハッシュ #x=-38&y=-20&z=56 → MCAFL（実際: %s）' % code)
        print('[座標の左右]')
        res = page.evaluate('''(function(){var a=window.__atlas, A=a.A, out={};
          [1,2,5,6,29,30].forEach(function(id){var m=A.medoid1[id];var mm=a.vox2mm(m[0],m[1],m[2]);out[id]=mm[0];});return out;})()''')
        check(res['1'] < 0 and res['5'] < 0 and res['29'] < 0, '左ラベル（ACAL・LLSL・ICL）の X が負: %s' % res)
        check(res['2'] > 0 and res['6'] > 0 and res['30'] > 0, '右ラベル（ACAR・LLSR・ICR）の X が正')
        print('[確率マップ・境界領域]')
        pr = page.evaluate('''(function(){var a=window.__atlas, A=a.A; if(!A.prob) return null;
          function at(x,y,z){a.setCursorMM(x,y,z); return [a.S.i,a.S.j,a.S.k];}
          var L=at(-40,-20,40), pl=window.__atlasProb(L[0],L[1],L[2]); var R=at(40,-20,40), pr=window.__atlasProb(R[0],R[1],R[2]);
          var nbz=0; if(A.bz){for(var q=0;q<A.n;q++) if(A.bz[q]) nbz++;}
          return {left:pl, right:pr, nbz:nbz, vox:A.vox[0]};})()''')
        if pr is None:
            print('  INFO 確率マップを含まないデータ')
        else:
            check(pr['vox'] == 1, '1mm 格子（%s mm）' % pr['vox'])
            check(sum(pr['left']) > 0 and all(abs(x - y) < 0.02 for x, y in zip(pr['left'], pr['right'])), '確率マップが左右対称に表示される %s / %s' % ([round(v, 3) for v in pr['left']], [round(v, 3) for v in pr['right']]))
            check(pr['nbz'] > 10000, '境界領域のボクセルがある（%d）' % pr['nbz'])
        print('[代表断面]')
        expect = {'延髄': 'BL', '橋': 'BL', '中脳': 'PCTPL', '海馬': 'ACTPL', '基底核・視床': 'LLSL', '放射冠': 'LLSL', '中心前回': 'MCAFL'}
        pres = page.evaluate('''(function(){var a=window.__atlas,out={};a.PRESETS.forEach(function(p){a.setCursorMM(p.x,p.y,p.z);
          var i=a.labelInfo(1,a.A.l1[a.S.i+a.S.j*a.A.nx+a.S.k*a.A.nx*a.A.ny]);var mm=a.vox2mm(a.S.i,a.S.j,a.S.k);out[p.label]=[i?i.code:null,mm[2]];});return out;})()''')
        for k, (c, z) in pres.items():
            if k in expect:
                check(c == expect[k], '代表断面「%s」→ %s（Z=%+d）期待 %s' % (k, c, round(z), expect[k]))
            else:
                print('  INFO 代表断面「%s」→ %s（Z=%+d）' % (k, c, round(z)))
        if shots:
            page.evaluate('window.__atlas.setCursorMM(-24,-10,4)')
            page.wait_for_timeout(300)
            page.screenshot(path=str(shots / 'desktop_all.png'))
        print('[病変: NIfTI]')
        page.evaluate("window.__atlas.setTab('lesion')")
        page.set_input_files('#file-nifti', str(tmp / 'lesion_1mm.nii'))
        page.wait_for_function('window.__atlas.lesionStats()', timeout=20000)
        st = page.evaluate('''(function(){var s=window.__atlas.lesionStats();var best=0,bi=0;for(var i=1;i<33;i++){if(s.c1[i]>best){best=s.c1[i];bi=i;}}
          return {vml:s.vml, top:window.__atlas.labelInfo(1,bi).code, cen:s.cen};})()''')
        exp_ml = 4 / 3 * np.pi * 6 ** 3 / 1000
        check(st['top'] == 'LLSL', '左被殻の球 → 最多は LLSL（実際: %s）' % st['top'])
        check(abs(st['vml'] - exp_ml) / exp_ml < 0.35, '体積 %.2f mL ≈ 理論値 %.2f mL' % (st['vml'], exp_ml))
        check(st['cen'][0] < -15, '重心 X が左（%.1f）' % st['cen'][0])
        page.click('#btn-lesion-clear')
        page.set_input_files('#file-nifti', str(tmp / 'lesion_2mm_q.nii.gz'))
        page.wait_for_timeout(1500)
        st2 = page.evaluate('''(function(){var s=window.__atlas.lesionStats();if(!s)return null;var best=0,bi=0;for(var i=1;i<33;i++){if(s.c1[i]>best){best=s.c1[i];bi=i;}}
          return {top:window.__atlas.labelInfo(1,bi).code, cen:s.cen};})()''')
        check(st2 is not None and st2['top'] == 'LLSR' and st2['cen'][0] > 15, 'qform のみ・gzip の 2mm 球（右）→ LLSR（実際: %s）' % st2)
        if shots:
            page.screenshot(path=str(shots / 'desktop_lesion.png'))
        page.click('#btn-lesion-clear')
        print('[ブラシ]')
        page.click('[data-tool="brush"]')
        box = page.locator('#canvas-axial').bounding_box()
        cx, cy = box['x'] + box['width'] * 0.4, box['y'] + box['height'] * 0.5
        page.mouse.move(cx, cy)
        page.mouse.down()
        page.mouse.move(cx + 30, cy + 10, steps=6)
        page.mouse.up()
        page.wait_for_timeout(400)
        n = page.evaluate('(function(){var s=window.__atlas.lesionStats();return s?s.total:0;})()')
        check(n > 0, 'ブラシで病変が描ける（%d ボクセル）' % n)
        page.click('#btn-undo')
        page.wait_for_timeout(300)
        n2 = page.evaluate('(function(){var s=window.__atlas.lesionStats();return s?s.total:0;})()')
        check(n2 == 0, '元に戻すで消える（%d）' % n2)
        page.click('[data-tool="cursor"]')
        print('[逆引き・クイズ・3D]')
        page.evaluate("window.__atlas.setTab('lookup')")
        chips = page.locator('.tag-chip')
        if chips.count():
            chips.first.click()
            page.wait_for_timeout(200)
            check(page.locator('#lookup-results .result-item').count() > 0, '逆引きで候補が出る')
        page.evaluate("window.__atlas.setTab('quiz')")
        page.click('#btn-quiz-start')
        page.wait_for_timeout(300)
        check(page.locator('.quiz-choice').count() >= 2, 'クイズの選択肢が出る')
        page.locator('.quiz-choice').first.click()
        page.wait_for_timeout(200)
        check(page.locator('#quiz-feedback .section-title').count() == 1, 'クイズに答えると正誤が出る')
        page.evaluate("window.__atlas.setTab('info')")
        page.click('[data-layout="3d"]')
        page.wait_for_timeout(500)
        if shots:
            page.screenshot(path=str(shots / 'desktop_3d.png'))
            for name in ('front', 'left', 'top'):
                page.evaluate("window.__atlas.R3.setView('%s')" % name)
                page.wait_for_timeout(300)
                page.locator('#wrap-3d').screenshot(path=str(shots / ('view3d_%s.png' % name)))
            page.evaluate("window.__atlas.R3.setView('home')")
        page.click('[data-layout="all"]')
        page.click('#chk-bz') if page.locator('#chk-bz').is_enabled() else None
        page.wait_for_timeout(300)
        check(not errors, 'コンソールエラーなし %s' % errors[:3])

        print('[inflate 互換経路]')
        ctx2 = browser.new_context(viewport={'width': 1200, 'height': 800})
        ctx2.add_init_script('delete window.DecompressionStream;')
        p2 = ctx2.new_page()
        err2 = []
        p2.on('pageerror', lambda e: err2.append(str(e)))
        p2.goto(url)
        p2.wait_for_function('window.__atlas && window.__atlas.A.l1', timeout=60000)
        s1 = page.evaluate('(function(){var a=window.__atlas.A.l1,s=0;for(var i=0;i<a.length;i++)s=(s+a[i]*((i%997)+1))%1000000007;return s;})()')
        s2 = p2.evaluate('(function(){var a=window.__atlas.A.l1,s=0;for(var i=0;i<a.length;i++)s=(s+a[i]*((i%997)+1))%1000000007;return s;})()')
        check(s1 == s2 and not err2, 'DecompressionStream なしでも同じデータに展開できる（%s / %s）' % (s1, s2))

        print('[スマホ表示]')
        ctx3 = browser.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        p3 = ctx3.new_page()
        err3 = []
        p3.on('pageerror', lambda e: err3.append(str(e)))
        p3.goto(url)
        p3.wait_for_function('window.__atlas && window.__atlas.A.l1', timeout=30000)
        p3.wait_for_timeout(400)
        sw = p3.evaluate('document.documentElement.scrollWidth')
        check(sw <= 392, '横スクロールが出ない（scrollWidth=%d）' % sw)
        if shots:
            p3.screenshot(path=str(shots / 'mobile_top.png'))
            p3.screenshot(path=str(shots / 'mobile_full.png'), full_page=True)
        check(not err3, 'スマホでもエラーなし %s' % err3[:3])
        browser.close()
    print('不合格 %d 件' % len(FAILS))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
