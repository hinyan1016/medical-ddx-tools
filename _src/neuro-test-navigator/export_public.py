"""承認済みの検査データを、公開用テンプレートと組み合わせて単一HTMLにする。"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).resolve().parent
URL = 'https://tools.ichisouzo-lab.com/neuro_test_navigator.html'


def catalog_text(html):
    matches = list(re.finditer(r'<script\b(?=[^>]*\bid="catalog-data")[^>]*>(.*?)</script>', html, re.S))
    if len(matches) != 1:
        raise ValueError('検査データを一意に特定できないため書き出しを中止')
    return matches[0].group(1)


def catalog(html):
    return json.loads(catalog_text(html))


def render(source):
    """表示と医学データの正本を分離し、入力の医学データをそのまま保持する。"""
    page = (SOURCE_DIR / 'page.html').read_text(encoding='utf-8')
    slots = {
        '{{NEUROFIND_STYLES}}': (SOURCE_DIR / 'presentation.css').read_text(encoding='utf-8'),
        '{{NEUROFIND_APP}}': (SOURCE_DIR / 'app.js').read_text(encoding='utf-8'),
        '{{NEUROFIND_CATALOG}}': catalog_text(source),
    }
    for token in slots:
        if page.count(token) != 1:
            raise ValueError('公開用テンプレートの差し込み位置を確認してください: ' + token)
    # 差し込み内容に別スロット名が含まれていても再展開しない。
    page = re.sub(r'\{\{NEUROFIND_(?:STYLES|APP|CATALOG)\}\}', lambda match: slots[match.group(0)], page)
    if catalog(page) != catalog(source):
        raise ValueError('検査データの変更を検出したため中止')
    return page


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path, help='確認済み検査データを含むHTML')
    parser.add_argument('--source-commit', required=True, help='入力元の完全なコミットSHA')
    parser.add_argument('--check', action='store_true', help='再生成結果と配信HTMLの一致を確認し、書き込まない')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-f0-9]{40}', args.source_commit):
        parser.error('完全なソースコミットSHAを指定してください')
    raw = args.source.read_bytes()
    source = raw.decode('utf-8-sig').replace('\r\n', '\n')
    page = render(source)
    target = ROOT / 'neuro_test_navigator.html'
    if args.check:
        if target.read_bytes() != page.encode('utf-8'):
            raise SystemExit('再生成結果と配信HTMLが一致しません')
        print('PASS: テンプレート・アプリ・スタイルから配信HTMLを完全再現')
        return
    data = catalog(page)
    ui = (SOURCE_DIR / 'app.js').read_text(encoding='utf-8')
    revision = re.search(r"var UI_REVISION = '([^']+)'", ui)
    if not revision:
        raise ValueError('画面版を特定できません')
    record = {
        'sourceCommit': args.source_commit,
        'sourceHtmlSha256': hashlib.sha256(raw).hexdigest(),
        'publicHtmlSha256': hashlib.sha256(page.encode('utf-8')).hexdigest(),
        'presentationRevision': revision.group(1),
        'publicAppSha256': hashlib.sha256(ui.encode('utf-8')).hexdigest(),
        'templateSha256': hashlib.sha256((SOURCE_DIR / 'page.html').read_bytes()).hexdigest(),
        'styleSha256': hashlib.sha256((SOURCE_DIR / 'presentation.css').read_bytes()).hexdigest(),
        'catalogSha256': hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest(),
        'dataVersion': data['version'],
        'tests': len(data['tests']),
        'referencePages': len(data['coverage']['items']),
        'referenceUpdates': len(data['coverage']['updateItems']),
        'publicUrl': URL,
        'medicalDataIdentical': True,
    }
    target.write_text(page, encoding='utf-8', newline='\n')
    (SOURCE_DIR / 'publication.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(record, ensure_ascii=False))


if __name__ == '__main__':
    main()
