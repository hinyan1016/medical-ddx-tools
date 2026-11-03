"""承認済みの単一HTMLを独自ドメイン用に書き出す。検査データは変更しない。"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = 'https://tools.ichisouzo-lab.com/neuro_test_navigator.html'


def catalog(html):
    match = re.search(r'<script type="application/json" id="catalog-data">(.*?)</script>', html, re.S)
    if not match:
        raise SystemExit('検査データが見つからないため書き出しを中止')
    return json.loads(match.group(1))


def replace_once(html, before, after):
    if html.count(before) != 1:
        raise SystemExit('元HTMLの形式が変わったため要確認: ' + before[:100])
    return html.replace(before, after, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', required=True, type=Path, help='確認済みのdist/index.html')
    parser.add_argument('--source-commit', required=True, help='確認済みソースのコミットSHA')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{40}', args.source_commit):
        raise SystemExit('完全なソースコミットSHAを指定してください')
    raw = args.source.read_bytes()
    source = raw.decode('utf-8-sig').replace('\r\n', '\n')
    data = catalog(source)
    page = replace_once(source, '<meta charset="UTF-8">', '''<meta charset="UTF-8">
<script data-online-only>if(/^https?:$/.test(location.protocol)&&'serviceWorker'in navigator){navigator.serviceWorker.getRegistrations().then(function(r){r.forEach(function(reg){reg.update().catch(function(){})})}).catch(function(){});navigator.serviceWorker.addEventListener('message',function(e){if(e.data&&e.data.type==='SW_UPDATED')window.location.reload()})}</script>
<meta name="apple-mobile-web-app-capable" content="yes" data-online-only>
<link rel="manifest" href="manifest.json" data-online-only>
<link rel="apple-touch-icon" href="icons/icon-192.png" data-online-only>''')
    page = replace_once(page, '<meta name="robots" content="noindex,nofollow">', f'''<meta name="robots" content="index,follow" data-online-only>
<link rel="canonical" href="{URL}" data-online-only>
<meta property="og:title" content="NeuroFind｜脳神経内科の検査ナビ" data-online-only>
<meta property="og:description" content="脳神経内科の特殊検査・外注検査を、検査名・疾患名・依頼先から検索。公式案内と確認日を確認でき、単一HTMLのオフライン保存に対応。" data-online-only>
<meta property="og:type" content="website" data-online-only>
<meta property="og:url" content="{URL}" data-online-only>
<meta property="og:image" content="https://tools.ichisouzo-lab.com/assets/og-tools.png" data-online-only>
<meta property="og:site_name" content="医知創造ラボ" data-online-only>''')
    page = replace_once(page, '医療者向けリファレンス <span aria-hidden="true">/</span>', '<a href="./" data-online-only style="color:inherit;text-decoration:none">ツール一覧</a><span aria-hidden="true" data-online-only>/</span>')
    page = replace_once(page, 'Sitesでの試作を閲覧するときはSitesの認証・配信機能が使われます。', '公開サイトの表示・更新には同じドメインの配信機能を使います。保存したオフラインHTMLは、ネット接続なしで使用できます。')
    page = replace_once(page, '本体は標準の静的HTMLです。将来、先生のドメインの任意のフォルダへ配置できます。Webサーバー固有のAPIやSitesのデータベースは使っていません。', 'JSONの取り込みだけでは公開サイトは書き換わりません。更新後はHTMLを保存して院内版を入れ替え、Web版は管理者が別途差し替えます。')
    page = replace_once(page, 'var copy=document.documentElement.cloneNode(true);', "var copy=document.documentElement.cloneNode(true);Array.prototype.forEach.call(copy.querySelectorAll('[data-online-only]'),function(node){node.parentNode.removeChild(node);});")
    page = replace_once(page, '</body>', '''<script data-online-only>if(/^https?:$/.test(location.protocol)&&'serviceWorker'in navigator){navigator.serviceWorker.register('./sw.js',{updateViaCache:'none'}).then(function(reg){return reg.update();}).catch(function(){});}</script>
</body>''')
    # 公開版の画面はこのフォルダで管理し、旧試作からの再生成でも保持する。
    ui_path = Path(__file__).parent / 'app.js'
    ui = ui_path.read_text(encoding='utf-8')
    matches = [m for m in re.finditer(r'<script(?:\s[^>]*)?>(.*?)</script>', page, re.S)
               if 'function coverage()' in m.group(1)]
    if len(matches) != 1:
        raise SystemExit('元HTMLのアプリ本体を特定できないため中止')
    page = replace_once(page, matches[0].group(0), '<script id="neurofind-app">' + ui + '</script>')
    page = replace_once(page, '<button class="side-link" data-action="coverage"><span class="icon-slot" data-icon="check"></span>更新と収録範囲</button>', '<button class="side-link" data-action="updates"><span class="icon-slot" data-icon="check"></span>更新履歴と機能</button>')
    page = replace_once(page, '<button class="side-link" data-action="manage"><span class="icon-slot" data-icon="database"></span>データの手動更新</button>', '<button class="side-link" data-action="manage"><span class="icon-slot" data-icon="database"></span>データの手動更新</button>\n  <button class="side-link" data-action="about"><span class="icon-slot" data-icon="info"></span>このサイトについて・謝辞</button>')
    page = replace_once(page, 'data-action="about">情報の範囲と利用について</button>', 'data-action="about">このサイトについて・謝辞</button>')
    page = replace_once(page, '特殊検査の名前から、依頼先の公式案内まで。<br>疾患名や略語でも、まとめて探せます。', '検体や依頼先で絞り込み、並べて比較。<br>検査情報を保存して、院内でも使えます。')
    page = replace_once(page, '<span data-icon="search"></span><i></i><span data-icon="vial"></span><i></i><span data-icon="external"></span>', '<span data-icon="search"></span><i></i><span data-icon="compare"></span><i></i><span data-icon="download"></span>')
    page = replace_once(page, '検査を探す <b>→</b> 検体を確認 <b>→</b> 公式案内へ', '探す <b>→</b> 比べる <b>→</b> 院内で使う')
    page = replace_once(page, '</footer>', '</footer>\n    <p class="acknowledgement-note">着想・収録候補の参考：綾木先生の<a href="https://sites.google.com/kuhp.kyoto-u.ac.jp/gaichukensa/脳内検査ホーム" target="_blank" rel="noopener noreferrer">「脳内検査検索サイト」</a>。検査情報を整理・公開されたご尽力に感謝いたします。</p>')
    page = replace_once(page, '</style>', '\n' + (Path(__file__).parent / 'presentation.css').read_text(encoding='utf-8') + '\n</style>')
    if catalog(page) != data:
        raise SystemExit('検査データの変更を検出したため中止')
    target = ROOT / 'neuro_test_navigator.html'
    target.write_text(page, encoding='utf-8', newline='\n')
    record = {
        'sourceCommit': args.source_commit,
        'sourceHtmlSha256': hashlib.sha256(raw).hexdigest(),
        'publicHtmlSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
        'presentationRevision': re.search(r"var UI_REVISION = '([^']+)'", ui).group(1),
        'publicAppSha256': hashlib.sha256(ui.encode('utf-8')).hexdigest(),
        'catalogSha256': hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest(),
        'dataVersion': data['version'],
        'tests': len(data['tests']),
        'referencePages': len(data['coverage']['items']),
        'referenceUpdates': len(data['coverage']['updateItems']),
        'publicUrl': URL,
        'medicalDataIdentical': True,
    }
    (Path(__file__).parent / 'publication.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
