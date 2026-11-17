"""脳波所見作成ツールの発作時記録を実ブラウザで検査する。

2026-11-17：臨床症状を伴う発作・脳波上の発作の判読文に
「臨床的イベントを記録したが、脳波変化を認めない」が必ず付く不具合の再発防止。
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
NOEEG_JA = '脳波変化を認めない'
NOEEG_EN = 'without an EEG change'

RUN = """(spec) => {
  S = defaults();
  if (spec.cls) S.cls = spec.cls;
  if (spec.term) S.term = spec.term;
  for (var i = 0; i < spec.findings.length; i++) {
    var f = newFinding('seiz');
    for (var k in spec.findings[i]) f[k] = spec.findings[i][k];
    S.findings.push(f);
  }
  var o = {};
  S.lang = 'ja'; o.ja = buildText('all'); o.interpJa = buildText('interp'); o.findJa = buildText('findings');
  S.lang = 'en'; o.en = buildText('all'); o.interpEn = buildText('interp');
  S.lang = 'ja'; o.warn = warnings();
  return o;
}"""


def main():
    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        # file:// では Service Worker を登録できないので、その通知だけは数えない
        page.on('pageerror', lambda e: None if 'ServiceWorkerRegistration' in str(e) else errors.append(str(e)))
        page.goto((ROOT / 'eeg_report_writer.html').as_uri())

        def run(findings, **kw):
            return page.evaluate(RUN, dict(findings=findings, **kw))

        # 1) 臨床症状を伴う発作：脳波変化なしの文が混ざらない
        r = run([dict(side='L', dur='90')], cls='moderate')
        assert '左側頭部から出現する焦点意識減損発作がビデオと脳波で記録されている。' in r['interpJa'], r
        assert NOEEG_JA not in r['interpJa'] and NOEEG_EN not in r['interpEn'], r
        assert '左側頭部に起始、律動性デルタ活動、持続90秒' in r['findJa'], r
        assert r['warn'] == [], r

        # 2) 脳波上の発作：同じく混ざらない。回数と持続の範囲が出る
        r = run([dict(kind='eeg', count='3', dist='generalized', pat='gsw', f1='3', dur='15', dur2='40')], cls='moderate')
        assert NOEEG_JA not in r['interpJa'] and NOEEG_EN not in r['interpEn'], r
        assert '3 Hzの全般性棘徐波、持続15-40秒' in r['findJa'], r
        assert 'が3回記録されている。' in r['interpJa'], r

        # 3) 脳波変化を伴わない臨床的イベント：正常判定のまま警告が出ない
        r = run([dict(kind='noeeg')])
        assert r['warn'] == [], r
        assert '正常脳波である。' in r['interpJa'] and '明らかなてんかん性放電を認めない' in r['interpJa'], r
        assert '焦点意識保持発作は頭皮脳波に変化が出ないことが多く' in r['interpJa'], r
        r = run([dict(kind='noeeg')], term='classic')
        assert '単純部分発作は頭皮脳波に変化が出ないことが多く' in r['interpJa'], r

        # 4) 事実だけを書く・アーチファクト
        r = run([dict(kind='noeeg', evt='plain', pdrKept=True, count='2')])
        assert '2回記録したが、いずれもイベント中の脳波変化を認めず、後頭部優位律動が保たれている。臨床的相関の検討を要する。' in r['interpJa'], r
        assert '頭皮脳波に変化が出ない' not in r['interpJa'], r
        r = run([dict(kind='noeeg', evt='artifact')])
        assert 'アーチファクトのため評価が困難である' in r['interpJa'] and NOEEG_JA not in r['ja'], r

        # 5) 重積：臨床症状を伴う発作は ECSE、脳波上の発作は ESE
        r = run([dict(stype='gtc', dist='generalized', dur='6', durU='m', ese=True)], cls='marked')
        assert 'ECSE' in r['interpJa'] and '5分以上連続' in r['interpJa'] and 'ESE：' not in r['interpJa'], r
        assert r['warn'] == [], r
        r = run([dict(kind='eeg', dur='12', durU='m', ese=True)], cls='marked')
        assert 'ESE：10分以上連続' in r['interpJa'] and 'ECSE' not in r['interpJa'], r

        # 6) 警告：重積の基準と持続の食い違い、起始と発作型の食い違い
        r = run([dict(kind='eeg', dur='12', durU='m'), dict(kind='eeg', dur='3', durU='m', ese=True),
                 dict(dist='generalized', stype='fias'), dict(stype='abs'), dict(kind='eeg', dur='5', dur2='8')], cls='marked')
        w = '\n'.join(r['warn'])
        assert '1) 持続が10分以上です' in w and '2) 1回で10分未満の発作' in w, r['warn']
        assert '3) 起始の分布が全般性ですが' in w and '4) 起始の分布が局在性・一側性ですが' in w, r['warn']
        assert '5) ACNSの脳波上の発作（ESz）は10秒以上です' in w, r['warn']
        r = run([dict(stype='fbtc', dur='5', durU='m')], cls='marked')
        assert any('持続が5分以上です' in x for x in r['warn']), r['warn']

        # 7) 起始を特定できない発作
        r = run([dict(dist='unclear', count='2')], cls='moderate')
        assert '起始部位は特定できない' in r['findJa'], r
        assert '焦点意識減損発作が2回、ビデオと脳波で記録されている。' in r['interpJa'] and '発作時脳波の起始部位は特定できない。' in r['interpJa'], r
        assert 'Focal impaired awareness seizures (x2) were recorded on video-EEG.' in r['interpEn'], r

        # 8) 記入例（発作時記録）が警告なしで読み込める
        page.evaluate("loadSample('ictal')")
        s = page.evaluate("(function(){ S.lang='ja'; return { t: buildText('all'), w: warnings(), cards: document.querySelectorAll('.finding').length }; })()")
        assert s['w'] == [] and s['cards'] == 2, s
        assert '睡眠時に出現、左前側頭部（F7最大）に起始、5-7 Hzの律動性シータ活動、同側半球へ伝播、持続60-90秒。脳波変化は臨床症状に約10秒先行。' in s['t'], s
        assert '発作後：左側優位の徐波化' in s['t'], s
        # ビデオ記録の注記は発作の記載に付き、発作後の脳波はその後に続く
        assert '右上肢のジストニア肢位（ビデオ脳波で記録）。発作後：左側優位の徐波化' in s['t'], s

        # 8b) 発作後変化の持続：括弧を重ねず、秒と分を選べる
        r = run([dict(stype='gtc', dist='generalized', post='supp', postDur='40')], cls='marked')
        assert '（ビデオ脳波で記録）。発作後：全般性の抑制（postictal generalized EEG suppression）、約40秒持続' in r['findJa'], r
        assert '）（' not in r['findJa'].split('発作後：')[1], r
        assert '(recorded on video-EEG). Postictal: generalized EEG suppression (PGES) for about 40 sec' in r['en'], r
        r = run([dict(side='L', post='lslow', postDur='3', postDurU='m', video=False)], cls='moderate')
        assert '発作後：左側優位の徐波化、約3分持続' in r['findJa'] and 'ビデオ脳波で記録' not in r['findJa'], r
        assert 'Postictal: left-predominant slowing for about 3 min' in r['en'], r

        # 9) 種類を切り替えると入力欄が入れ替わる（8b で状態を作り替えたので記入例を読み直す）
        page.evaluate("loadSample('ictal')")
        page.select_option('#fc1 select[data-k="kind"]', 'noeeg')
        assert page.locator('#fc1 select[data-k="evt"]').count() == 1
        assert page.locator('#fc1 select[data-k="dist"]').count() == 0
        page.select_option('#fc1 select[data-k="kind"]', 'clin')
        page.select_option('#fc1 select[data-k="dist"]', 'unclear')
        assert page.locator('#fc1 select[data-k="loc"]').count() == 0
        assert page.locator('#fc1 select[data-k="lead"]').count() == 1
        assert page.locator('#fc1 select[data-k="postDurU"]').count() == 1

        browser.close()
    assert errors == [], errors
    print('OK: eeg_report_writer 発作時記録 10項目')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
