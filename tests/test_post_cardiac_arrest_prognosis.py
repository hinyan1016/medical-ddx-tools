"""予後判定支援の境界条件・重複加算・保留条件を実ブラウザで検査する。"""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT.parent / 'medical-content/blog/revisions/post-cardiac-arrest-20261022/qa'
BASE = dict(scope='adult', motor='1', rosc='120', timing='cautious', cooling='no', sedation='no',
            drugClear='clear', tempClear='clear', metabolicClear='clear', systemicClear='clear', seizureClear='clear')


def main():
    REPORT.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1050}, device_scale_factor=1)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto((ROOT / 'post_cardiac_arrest_prognosis.html').as_uri())

        def check(name, changes, status=None, count=None, good=None, base=True):
            answer = dict(BASE, **changes) if base else changes
            r = page.evaluate('(a) => evaluate(a)', answer)
            if status is not None:
                assert r['status'] == status, (name, r)
            if count is not None:
                assert r['count'] == count, (name, r)
            if good is not None:
                assert len(r['good']) == good, (name, r)
            results.append({'case': name, 'status': r['status'], 'count': r['count'], 'passed': True})
            return r

        check('初期値は未確認で保留', {}, 'pending', 0, base=False)
        check('前提のみでは良好と判定しない', {}, 'uncertain', 0)
        check('小児等は対象外', {'scope': 'outside'}, 'outside')
        check('指示に従えば昏睡アルゴリズム対象外', {'motor': '6'}, 'recovery')
        check('ROSC 71.99hは保留', {'rosc': '71.99'}, 'pending')
        check('ROSC 72hは待機基準到達', {'rosc': '72'}, 'uncertain')
        check('復温後71.99hは保留', {'cooling': 'yes', 'rewarm': '71.99'}, 'pending')
        check('復温後72hは待機基準到達', {'cooling': 'yes', 'rewarm': '72'}, 'uncertain')
        check('鎮静中止後71.99hは保留', {'sedation': 'yes', 'sedstop': '71.99'}, 'pending')
        check('薬剤影響が残れば待機時間を超えても保留', {'drugClear': 'present'}, 'pending')
        check('交絡因子未確認も保留', {'metabolicClear': ''}, 'pending')
        check('復温時間の逆転', {'cooling': 'yes', 'rewarm': '121'}, 'pending')
        check('鎮静中止時間の逆転', {'sedation': 'yes', 'sedstop': '121'}, 'pending')
        reflex = dict(pupils='absent', corneal='absent', reflexTime='72', reflexQuality='yes')
        check('瞳孔と角膜は合わせて1項目', reflex, 'uncertain', 1)
        check('角膜単独を独立加算しない', dict(reflex, pupils='present'), 'uncertain', 0)
        check('脳幹反射71.99hを除外', dict(reflex, reflexTime='71.99'), 'uncertain', 0)
        check('反射の技術的条件未確認を除外', dict(reflex, reflexQuality=''), 'uncertain', 0)
        ssep = dict(ssep='absent', ssepTime='24', ssepQuality='yes')
        check('ERC N20は24hを含む', ssep, 'uncertain', 1)
        check('N20 23.99hを除外', dict(ssep, ssepTime='23.99'), 'uncertain', 0)
        check('N20保持を良好判定へ反転しない', dict(ssep, ssep='present'), 'uncertain', 0, 0)
        eeg = dict(eeg='burst', eegTime='24', eegQuality='yes')
        check('EEG 24hちょうどはERC >24hを満たさない', eeg, 'uncertain', 0)
        check('EEG 24.01hはERC条件内', dict(eeg, eegTime='24.01'), 'uncertain', 1)
        check('反応性消失・発作だけを加算しない', dict(eeg, eeg='other'), 'uncertain', 0)
        check('NSE 60は >60を満たさない', {'nse48': '60', 'nse48Quality': 'yes'}, 'uncertain', 0)
        nse = dict(nse48='60.01', nse48Quality='yes', nse72='140', nse72Quality='yes')
        check('NSE両時点でも1項目', nse, 'uncertain', 1)
        check('溶血した高NSEを除外', dict(nse, nse48Quality='no', nse72Quality='no'), 'uncertain', 0)
        check('ERC良好NSEは17を含む', {'nse48': '17', 'nse48Quality': 'yes'}, 'recovery', 0, 1)
        check('17を超えるNSEを良好所見にしない', {'nse48': '17.01', 'nse48Quality': 'yes'}, 'uncertain', 0, 0)
        check('条件未確認の低NSEを良好所見にしない', {'nse48': '10', 'nse48Quality': ''}, 'uncertain', 0, 0)
        check('低NSEと高NSEが混在なら再評価', dict(nse, nse48='17'), 'discordant', 1, 1)
        check('まだ採血できない未来のNSEを検出', dict(nse, rosc='60'), 'pending', 1)
        imaging = dict(ct='diffuse', ctTime='60', ctQuality='yes', mri='diffuse', mriTime='96', mriQuality='yes')
        check('CTとMRIでも1項目', imaging, 'uncertain', 1)
        check('MRIは48hから', dict(imaging, ct='other', mriTime='48'), 'uncertain', 1)
        check('MRI 47.99hを除外', dict(imaging, ct='other', mriTime='47.99'), 'uncertain', 0)
        check('MRIは168hを含む', dict(imaging, rosc='200', ct='other', mriTime='168'), 'uncertain', 1)
        check('MRI 168.01hを除外', dict(imaging, rosc='200', ct='other', mriTime='168.01'), 'uncertain', 0)
        check('未来の検査時刻は保留', dict(imaging, mriTime='121'), 'pending', 1)
        myo = dict(myoclonus='status', myoTime='72', myoQuality='yes')
        check('厳密なミオクローヌス定義・72hを含む', myo, 'uncertain', 1)
        check('一般のミオクローヌスを加算しない', dict(myo, myoclonus='other'), 'uncertain', 0)
        check('ミオクローヌス72h超を除外', dict(myo, myoTime='72.01'), 'uncertain', 0)
        multiple = dict(reflex, **ssep)
        check('異なる2項目がそろう', multiple, 'multi', 2)
        check('2項目あっても交絡因子ありなら保留', dict(multiple, drugClear='present'), 'pending', 2)
        check('不良所見と逃避反応が混在なら再評価', dict(multiple, motor='4'), 'discordant', 2, 1)
        check('不良所見と良好MRIが混在なら再評価', dict(multiple, mri='normal', mriTime='96', mriQuality='yes'), 'discordant', 2, 1)
        check('早期正常CTだけで良好としない', {'ct': 'other', 'ctTime': '2', 'ctQuality': 'yes'}, 'uncertain', 0, 0)
        check('NPiやNfLの独自閾値・点数を作らない', {'nfl': 'high'}, 'uncertain', 0)
        check('ERC時間設定では鎮静中止72hを一律強制しない', {'timing': 'erc', 'sedation': 'yes', 'sedstop': '30'}, 'uncertain')
        check('ERC時間設定も残存薬剤作用を除外する', {'timing': 'erc', 'sedation': 'yes', 'sedstop': '30', 'drugClear': 'present'}, 'pending')
        all_bad = dict(reflex, **ssep, **dict(eeg, eegTime='80'), **nse, **imaging, **myo)
        check('6項目の重複なし', all_bad, 'multi', 6)

        # 実際のフォーム操作と描画・記録を検査する。
        for key, value in dict(BASE, **multiple).items():
            loc = page.locator('#'+key)
            if loc.evaluate('(e) => e.tagName') == 'SELECT':
                loc.select_option(value)
            else:
                loc.fill(value)
        assert '複数の不良所見' in page.locator('#resultTitle').inner_text()
        assert '両側N20消失' in page.locator('#record').input_value()
        assert page.locator('#rewarm').is_disabled()
        page.locator('#cooling').select_option('yes')
        assert not page.locator('#rewarm').is_disabled()
        assert '保留' in page.locator('#resultTitle').inner_text()
        page.locator('#rewarm').fill('72')
        page.locator('#motor').select_option('4')
        assert '食い違' in page.locator('#resultTitle').inner_text()

        for width, name in [(1440, 'desktop'), (390, 'mobile'), (320, 'narrow')]:
            page.set_viewport_size({'width': width, 'height': 1000})
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), name
            assert page.locator('#resultTitle').is_visible()
            if name != 'narrow':
                page.evaluate('window.scrollTo(0,0)')
                page.screenshot(path=str(REPORT / (name+'.png')), full_page=True)
                page.screenshot(path=str(REPORT / (name+'-top.png')))
                page.locator('#result').screenshot(path=str(REPORT / (name+'-result.png')))
        page.emulate_media(media='print')
        page.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        assert page.locator('#record').is_visible()
        page.emulate_media(media='screen')
        page.locator('#copyButton').click()
        assert page.locator('#copyStatus').inner_text()
        page.evaluate('window.print = function(){ window.printInvoked = true; }')
        page.locator('#printButton').click()
        assert page.evaluate('window.printInvoked === true')
        page.once('dialog', lambda dialog: dialog.accept())
        page.locator('#resetButton').click()
        assert page.locator('#scope').input_value() == ''
        assert page.locator('#rosc').input_value() == ''
        assert '保留' in page.locator('#resultTitle').inner_text()
        assert not errors, errors
        browser.close()
    (REPORT / 'test-results.json').write_text(json.dumps({'passed': len(results), 'cases': results, 'browser_errors': errors, 'responsive_widths': [1440,390,320]}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(str(len(results))+' clinical boundary cases PASS; form, record, print, responsive checks PASS')


if __name__ == '__main__':
    main()
