# -*- coding: utf-8 -*-
"""template.html にアトラスデータと臨床解説を埋め込み、公開用の単一HTMLを作る。

  python build.py                       # 既定: atlas_data.bin.gz + content.json → ../../vascular-territory-atlas.html
  python build.py --zip                 # あわせて downloads/ の単体版ZIPも作り直す
  python build.py --content <別のjson>  # 開発用

テンプレートの JS が ES5 だけで書かれているか（TOOL_AUTHORING_GUIDE の互換性ルール）もここで確かめる。
"""
import argparse
import base64
import datetime
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # medical-ddx-tools/

ZIP_HTML_NAME = 'MNI_脳血管支配領域_3Dアトラス_オフライン版.html'
ZIP_README_NAME = 'README_オフライン起動手順.txt'


def es5_violations(js):
    """コメントと文字列を除いた本体に ES2015 以降の構文が無いかを見る（素朴な検査）。"""
    body = re.sub(r'/\*.*?\*/', '', js, flags=re.S)
    body = re.sub(r'(?m)(^|[^:\\])//.*$', r'\1', body)
    body = re.sub(r"'(?:\\.|[^'\\\n])*'", "''", body)
    body = re.sub(r'"(?:\\.|[^"\\\n])*"', '""', body)
    body = re.sub(r'/(?:\\.|\[(?:\\.|[^\]\\\n])*\]|[^/\\\n\[])+/[gimsuy]*(?=\s*[,.;)\]])', '/r/', body)
    rules = [
        (r'=>', 'アロー関数'), (r'\bconst\s', 'const'), (r'\blet\s', 'let'), (r'`', 'テンプレートリテラル'),
        (r'\bclass\s+[A-Z]', 'class'), (r'\.\.\.[A-Za-z_$\[]', 'スプレッド構文'), (r'\basync\s+function', 'async'),
        (r'\bawait\s', 'await'), (r'\.includes\(', 'includes'), (r'\.startsWith\(', 'startsWith'), (r'\.endsWith\(', 'endsWith'),
        (r'\bArray\.from\(', 'Array.from'), (r'\bObject\.assign\(', 'Object.assign'), (r'\.find\(', 'Array.find'),
        (r'\bfor\s*\(\s*var\s+\w+\s+of\s', 'for...of'), (r'\bMath\.sign\(', 'Math.sign'), (r'\.padStart\(', 'padStart'),
    ]
    found = []
    for pat, name in rules:
        for m in re.finditer(pat, body):
            line = body.count('\n', 0, m.start()) + 1
            found.append('%s（本体 %d 行目付近）' % (name, line))
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--template', default=str(HERE / 'template.html'))
    ap.add_argument('--data', default=str(HERE / 'atlas_data.bin.gz'))
    ap.add_argument('--content', default=str(HERE / 'content.json'))
    ap.add_argument('--build-info', default=str(HERE / 'build_info.json'))
    ap.add_argument('--out', default=str(ROOT / 'vascular-territory-atlas.html'))
    ap.add_argument('--zip', action='store_true')
    args = ap.parse_args()

    tpl = Path(args.template).read_text(encoding='utf-8')
    scripts = re.findall(r'<script>(.*?)</script>', tpl, flags=re.S)
    bad = es5_violations('\n'.join(scripts))
    if bad:
        print('ES5 違反:', *bad, sep='\n  ')
        return 1

    data = Path(args.data).read_bytes()
    b64 = base64.b64encode(data).decode('ascii')
    content = None
    if Path(args.content).exists():
        content = json.loads(Path(args.content).read_text(encoding='utf-8'))
    else:
        print('注意: content.json が無いので臨床解説なしで作ります')
    info = {}
    if Path(args.build_info).exists():
        info = json.loads(Path(args.build_info).read_text(encoding='utf-8'))
    info['date'] = datetime.date.today().isoformat()

    def js_literal(obj):
        s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
        return s.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

    html = tpl
    for key, val in (('@@ATLAS_DATA_B64@@', b64),
                     ('/*@@CONTENT@@*/null', js_literal(content)),
                     ('/*@@BUILD_INFO@@*/{}', js_literal(info))):
        if html.count(key) != 1:
            print('テンプレートの差し込み位置が見つからないか重複:', key)
            return 1
        html = html.replace(key, val)
    Path(args.out).write_bytes(html.encode('utf-8'))
    print('書き出し:', args.out, '%.2f MB' % (len(html.encode('utf-8')) / 1e6))

    if args.zip:
        zpath = ROOT / 'downloads' / 'MNI_Vascular_Territory_Atlas_Standalone.zip'
        readme = (HERE / 'README_offline.txt').read_text(encoding='utf-8')
        with zipfile.ZipFile(zpath, 'w', compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(ZIP_HTML_NAME, html.encode('utf-8'))
            z.writestr(ZIP_README_NAME, readme.encode('utf-8'))
        print('ZIP:', zpath)
    return 0


if __name__ == '__main__':
    sys.exit(main())
