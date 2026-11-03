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
    if catalog(page) != data:
        raise SystemExit('検査データの変更を検出したため中止')
    target = ROOT / 'neuro_test_navigator.html'
    target.write_text(page, encoding='utf-8')
    record = {
        'sourceCommit': args.source_commit,
        'sourceHtmlSha256': hashlib.sha256(raw).hexdigest(),
        'publicHtmlSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
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
