#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ハンドアウトのQRコードを、対応するブログ記事へ向け直す。

これまでQRにはハンドアウト自身のURL（`.../handouts/<slug>/`）が入っていたが、
キャプションは「動画・くわしい解説はこちら」であり、記事に飛ぶのが正しい。

記事URLの正本は `infographics/manifest.json` の `blog_url`。
シリーズのProject Logにも記事URLが載っているが、**下書き時代の旧URLが残っている**
（下書きPUTのたびに再採番されるため）。manifest 以外から取ってはいけない。

安全機構:
  - blog_url が空、または HTTP 200 を返さない slug は **書き換えない**（下書き記事は404になる）
  - 書き換え後に生成したQRを実際にデコードし、狙ったURLと一致するか確認する
  - ハンドアウトごとのテーマ色をそのまま引き継ぐ

使い方:
    PYTHONIOENCODING=utf-8 python fix_qr_links.py                 # 差分の確認だけ（既定）
    PYTHONIOENCODING=utf-8 python fix_qr_links.py --apply         # 書き換える
    PYTHONIOENCODING=utf-8 python fix_qr_links.py --apply --skip-http-check
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

import segno

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MANIFEST = os.path.join(REPO, "infographics", "manifest.json")

# ハンドアウトのフォルダ名とインフォグラフィックの slug が違うもの
SLUG_ALIAS = {"overactive-bladder-frequency": "overactive-bladder"}

BORDER = 2
UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "text/html",
}

RE_QR_BLOCK = re.compile(r'(<div class="qr">\s*)(<svg\b.*?</svg>)', re.S)
RE_COLOR = re.compile(r'(?:fill|stroke)="(#[0-9A-Fa-f]{3,8})"')


def load_blog_urls():
    data = json.load(open(MANIFEST, encoding="utf-8"))
    items = data if isinstance(data, list) else (data.get("items") or list(data.values())[0])
    return {it["slug"]: (it.get("blog_url") or "").strip()
            for it in items if isinstance(it, dict) and it.get("slug")}


def http_status(url, tries=4, wait=8):
    """はてなは連続アクセスに 403 を返すため、間隔を空けて再試行する。"""
    for i in range(tries):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=25).status
        except urllib.error.HTTPError as e:
            if e.code == 403 and i < tries - 1:
                time.sleep(wait)
                continue
            return e.code
        except Exception:
            return "ERR"
    return "ERR"


def theme_color(svg):
    """既存QRの色を拾う（白は背景なので除く）。"""
    for c in RE_COLOR.findall(svg):
        if c.lower() not in ("#fff", "#ffffff"):
            return c
    return "#000000"


def make_qr_svg(url, color):
    matrix = segno.make(url, error="m").matrix
    n = len(matrix) + BORDER * 2
    d = "".join(
        "M%d %dh1v1h-1z" % (x + BORDER, y + BORDER)
        for y, row in enumerate(matrix)
        for x, v in enumerate(row) if v
    )
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'shape-rendering="crispEdges" role="img" aria-label="QRコード">'
            '<rect width="%d" height="%d" fill="#fff"/>'
            '<path d="%s" fill="%s"/></svg>' % (n, n, n, n, d, color))


def decode_qr_svg(svg):
    """生成したSVGを画像に起こして読み取り、狙ったURLが入っているか確かめる。"""
    import cv2
    import numpy as np

    m = re.search(r'viewBox="0 0 (\d+) \d+"', svg)
    if not m:
        return None
    n = int(m.group(1))
    grid = np.full((n, n), 255, dtype=np.uint8)
    for x, y in re.findall(r"M(\d+) (\d+)h1v1h-1z", svg):
        grid[int(y), int(x)] = 0
    big = cv2.resize(grid, (n * 12, n * 12), interpolation=cv2.INTER_NEAREST)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(big)
    return text or None


def main():
    ap = argparse.ArgumentParser(description="ハンドアウトのQRを記事URLに向け直す")
    ap.add_argument("--apply", action="store_true", help="実際に書き換える")
    ap.add_argument("--skip-http-check", action="store_true",
                    help="記事URLの疎通確認を省く（確認済みの再実行用）")
    args = ap.parse_args()

    blog = load_blog_urls()
    slugs = sorted(d for d in os.listdir(HERE) if os.path.isdir(os.path.join(HERE, d)))

    changed, skipped, failed = [], [], []
    for slug in slugs:
        path = os.path.join(HERE, slug, "index.html")
        if not os.path.isfile(path):
            continue
        text = open(path, encoding="utf-8").read()
        m = RE_QR_BLOCK.search(text)
        if not m:
            failed.append((slug, "QRのSVGが見つからない"))
            continue

        url = blog.get(SLUG_ALIAS.get(slug, slug), "")
        if not url:
            skipped.append((slug, "記事URLが未登録（記事が下書き）"))
            continue
        if not args.skip_http_check:
            st = http_status(url)
            time.sleep(2.5)
            if st != 200:
                skipped.append((slug, "記事URLが HTTP %s" % st))
                continue

        color = theme_color(m.group(2))
        new_svg = make_qr_svg(url, color)
        got = decode_qr_svg(new_svg)
        if got != url:
            failed.append((slug, "生成したQRの読み取り結果が不一致: %r" % got))
            continue

        if args.apply:
            open(path, "w", encoding="utf-8").write(
                text[:m.start(2)] + new_svg + text[m.end(2):])
        changed.append((slug, color, url))

    print("=== 書き換え%s ===" % ("済" if args.apply else "対象（--apply で実行）"))
    for slug, color, url in changed:
        print("  %-38s %s  %s" % (slug, color, url))
    if skipped:
        print("\n=== 対象外（QRは元のまま） ===")
        for slug, why in skipped:
            print("  %-38s %s" % (slug, why))
    if failed:
        print("\n=== 失敗 ===")
        for slug, why in failed:
            print("  %-38s %s" % (slug, why))

    print("\n書き換え %d 件 ／ 対象外 %d 件 ／ 失敗 %d 件" % (len(changed), len(skipped), len(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
