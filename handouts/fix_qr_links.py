#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ハンドアウトのQRコードを、対応するブログ記事へ向け直す（href と QR画像の両方）。

キャプションは「くわしい解説記事」であり、QRは**記事URL**に飛ぶのが正しい。
記事URLの正本は `slides/manifest.json` の `blog_url`。`infographics/manifest.json`
にも同名フィールドがあるが**空のまま放置されていることがある**ため、slides を優先し、
slides に無い slug だけ infographics で補う。シリーズのProject Logにも記事URLが
載っているが**下書き時代の旧URLが残っている**ので、manifest 以外から取ってはいけない。

対応する構造は2種類。どちらも「既にファイルにある見た目」をそのまま引き継ぎ、
**QRの中身（ペイロード）と href だけ**を書き換える。

  現行（第2弾以降）:
    <a class="qr" href="記事URL"><div class="qr-box"><svg …></svg></div>
      <span class="qrcap">…</span></a>
  旧（第1弾・外来指導シリーズ）:
    <div class="qr"><svg …></svg><div class="qr-cap">…</div>

安全機構:
  - **href と QR画像は必ず同時に書き換える。** 片方だけ変わると、見た目は正しいのに
    読み取ると別の場所へ飛ぶ最悪の壊れ方をする
  - 照合は**デコードで確認しない**。QRの誤り訂正が効くため、多少壊れていても復号でき
    てしまい合格に見える。**同じURLから再生成した `<path d="…">` と厳密一致するか**で
    判定する（--self-test で、別URLから生成したものとは不一致になることも確認する）
  - blog_url が空、または HTTP 200 を返さない slug は **書き換えない**（下書きは404）
  - 既定は dry-run。書き換えは --apply を明示したときだけ
  - HTMLコメントの中は見ない（手順コメントに書かれた雛形に誤ヒットするため）
  - ハンドアウトごとのテーマ色・SVGの描き方（segno 版 / crispEdges 版）を引き継ぐ
  - 書き込みはバイト列で行い、改行コードに触らない（CRLF のファイルがある）

QR生成は segno。error="m" / border=4 / svgclass="segno" / lineclass="qrline" /
omitsize=True（現行ハンドアウトと同じ設定）。--self-test が既存2件との一致を確認する。

使い方:
    PYTHONIOENCODING=utf-8 python fix_qr_links.py                 # 監査＋差分の確認（既定）
    PYTHONIOENCODING=utf-8 python fix_qr_links.py --slug dementia-diabetes
    PYTHONIOENCODING=utf-8 python fix_qr_links.py --apply         # 書き換える（HTTP疎通確認つき）
    PYTHONIOENCODING=utf-8 python fix_qr_links.py --apply --skip-http-check
    PYTHONIOENCODING=utf-8 python fix_qr_links.py --self-test     # 生成器の回帰テスト

exit: 0=全件整合 ／ 1=不整合あり（要対処）／ 2=未検査（URL未登録・QR無し・疎通不明）
"""

import argparse
import io
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
MANIFESTS = [
    (os.path.join(REPO, "slides", "manifest.json"), "decks"),          # 正本
    (os.path.join(REPO, "infographics", "manifest.json"), "items"),    # 補完
]

# ハンドアウトのフォルダ名と manifest の slug が違うもの
SLUG_ALIAS = {"overactive-bladder-frequency": "overactive-bladder"}

# 現行ハンドアウトの生成条件。ここを変えると既存2件と出力が変わる（--self-test が落ちる）
BORDER = 4
ERROR = "m"
SEGNO_SVG_KW = dict(kind="svg", border=BORDER, svgclass="segno", lineclass="qrline",
                    omitsize=True, xmldecl=False, svgns=True)
A11Y = 'role="img" aria-label="QRコード" '

UA = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "text/html",
}

# <a class="qr" href="…"><div class="qr-box"><svg …></svg></div>
RE_ANCHOR = re.compile(
    r'<a\b(?P<attrs>[^>]*\bclass="qr"[^>]*)>\s*<div class="qr-box">\s*(?P<svg><svg\b.*?</svg>)',
    re.S)
# <div class="qr"><svg …></svg>   … href を持たない旧構造
RE_LEGACY = re.compile(r'<div class="qr">\s*(?P<svg><svg\b.*?</svg>)', re.S)
RE_HREF = re.compile(r'href="(?P<url>[^"]*)"')
RE_PATH_D = re.compile(r'<path\b[^>]*\bd="(?P<d>[^"]+)"')
RE_STROKE = re.compile(r'stroke="(#[0-9A-Fa-f]{3,8})"')
RE_FILL = re.compile(r'fill="(#[0-9A-Fa-f]{3,8})"')
RE_COMMENT = re.compile(r"<!--.*?-->", re.S)


# --------------------------------------------------------------------------- 生成

def render_segno(url, color):
    """現行ハンドアウトと同じ segno 版SVG（<path class="qrline" stroke=…>）。"""
    buf = io.BytesIO()
    segno.make(url, error=ERROR).save(buf, **SEGNO_SVG_KW)
    svg = buf.getvalue().decode("utf-8").strip()
    svg = svg.replace("<svg ", "<svg " + A11Y, 1)
    if color and color.lower() not in ("#000", "#000000"):
        svg = svg.replace('stroke="#000"', 'stroke="%s"' % color, 1)
    return svg


def render_crisp(url, color):
    """旧ハンドアウトと同じ crispEdges 版SVG（1モジュール1矩形の <path d=… fill=…>）。"""
    matrix = segno.make(url, error=ERROR).matrix
    n = len(matrix) + BORDER * 2
    d = "".join(
        "M%d %dh1v1h-1z" % (x + BORDER, y + BORDER)
        for y, row in enumerate(matrix)
        for x, v in enumerate(row) if v
    )
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'shape-rendering="crispEdges" %s>'
            '<rect width="%d" height="%d" fill="#fff"/>'
            '<path d="%s" fill="%s"/></svg>'
            % (n, n, A11Y.rstrip(), n, n, d, color or "#000000"))


RENDERERS = {"segno": render_segno, "crisp": render_crisp}


def detect_style(svg):
    return "segno" if 'class="segno"' in svg or 'class="qrline"' in svg else "crisp"


def theme_color(svg):
    """既存QRの色を拾う（白は背景なので除く）。"""
    for c in RE_STROKE.findall(svg) + RE_FILL.findall(svg):
        if c.lower() not in ("#fff", "#ffffff"):
            return c
    return "#000000"


def path_d(svg):
    m = RE_PATH_D.search(svg)
    return m.group("d") if m else None


def needs_update(block, url):
    """href（あれば）と QR画像の**両方**が url を指しているか。片方でも違えば要更新。"""
    if block.href_span is not None and block.href != url:
        return True
    return not qr_matches(url, block.svg)


def qr_matches(url, svg):
    """svg のQRが url から生成したものと厳密一致するか（デコードはしない）。"""
    if not url:
        return False
    expected = path_d(RENDERERS[detect_style(svg)](url, theme_color(svg)))
    return expected is not None and path_d(svg) == expected


def _cells_from_path(d):
    """QRの <path d> から黒モジュールの座標を復元する（crispEdges版・segno版の両方）。"""
    cells = [(int(x), int(y)) for x, y in re.findall(r"M(\d+) (\d+)h1v1h-1z", d)]
    if cells:
        return cells
    # segno版: "M4 4.5h7m1 0h2…" 横線の連結パス（yは行の中心なので .5 が付く）
    m = re.match(r"M(-?\d+) (-?\d+)(?:\.5)?", d)
    if not m:
        return []
    x, y = int(m.group(1)), int(m.group(2))
    for op, a, b in re.findall(r"([mh])(-?\d+)(?: (-?\d+))?", d[m.end():]):
        if op == "m":
            x += int(a)
            y += int(b or 0)
        else:
            for i in range(int(a)):
                cells.append((x + i, y))
            x += int(a)
    return cells


def diagnose(svg):
    """**診断専用**。厳密一致しなかったQRが何を指しているかを読み取って説明する。

    合否判定には絶対に使わない（誤り訂正が効くので、壊れたQRでも復号できてしまう）。
    「別URLに向いている」のか「中身は同じで生成器が違うだけ」のかを人が判断するための材料。
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return None
    d = path_d(svg)
    m = re.search(r'viewBox="0 0 (\d+)', svg)
    if not d or not m:
        return None
    n = int(m.group(1))
    grid = np.full((n, n), 255, dtype=np.uint8)
    cells = _cells_from_path(d)
    if not cells:
        return None
    for x, y in cells:
        grid[y, x] = 0
    big = cv2.resize(grid, (n * 12, n * 12), interpolation=cv2.INTER_NEAREST)
    return cv2.QRCodeDetector().detectAndDecode(big)[0] or None


# --------------------------------------------------------------------------- 解析

def mask_comments(text):
    """HTMLコメントを同じ長さの空白で潰す。オフセットは元テキストと一致したまま。"""
    return RE_COMMENT.sub(lambda m: " " * len(m.group(0)), text)


class Block(object):
    """ハンドアウト1件のQR。svg_span/href_span は元テキスト上の絶対オフセット。"""

    def __init__(self, kind, svg, svg_span, href, href_span):
        self.kind = kind          # "anchor" / "legacy"
        self.svg = svg
        self.svg_span = svg_span
        self.href = href          # 旧構造は None
        self.href_span = href_span
        self.style = detect_style(svg)
        self.color = theme_color(svg)


def find_blocks(text):
    scan = mask_comments(text)
    blocks = []
    for m in RE_ANCHOR.finditer(scan):
        href, href_span = None, None
        h = RE_HREF.search(m.group("attrs"))
        if h:
            href = h.group("url")
            base = m.start("attrs")
            href_span = (base + h.start("url"), base + h.end("url"))
        blocks.append(Block("anchor", text[m.start("svg"):m.end("svg")],
                            m.span("svg"), href, href_span))
    for m in RE_LEGACY.finditer(scan):
        blocks.append(Block("legacy", text[m.start("svg"):m.end("svg")],
                            m.span("svg"), None, None))
    blocks.sort(key=lambda b: b.svg_span[0])
    return blocks


def splice(text, edits):
    """(start, end, replacement) を後ろから当てる。改行コードには触らない。"""
    for start, end, repl in sorted(edits, reverse=True):
        text = text[:start] + repl + text[end:]
    return text


# --------------------------------------------------------------------------- URL

def load_blog_urls():
    """slug -> (url, どのmanifestから取ったか)。slides を優先し infographics で補う。"""
    out = {}
    for path, key in MANIFESTS:
        if not os.path.isfile(path):
            continue
        data = json.load(open(path, encoding="utf-8"))
        items = data.get(key) if isinstance(data, dict) else data
        if items is None:
            items = [v for k, v in data.items() if k != "_comment"][0]
        src = os.path.basename(os.path.dirname(path))
        for it in items:
            if not isinstance(it, dict) or not it.get("slug"):
                continue
            url = (it.get("blog_url") or "").strip()
            if url and it["slug"] not in out:
                out[it["slug"]] = (url, src)
    return out


def resolve_url(slug, blog):
    for key in (slug, SLUG_ALIAS.get(slug)):
        if key and key in blog:
            return blog[key]
    return ("", "")


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


# --------------------------------------------------------------------------- 自己テスト

# 既存の公開済みハンドアウト。ここと同じ出力になることを回帰テストにする。
FIXTURES = [
    ("dementia-hearing-loss", "https://blog.ichisouzo-lab.com/entry/2026/08/13/120424", "segno"),
    ("dementia-diabetes",     "https://blog.ichisouzo-lab.com/entry/2026/08/14/154829", "segno"),
    ("dementia-hypertension", "https://blog.ichisouzo-lab.com/entry/2026/08/11/225112", "crisp"),
]
OTHER_URL = "https://blog.ichisouzo-lab.com/entry/2026/01/01/000000"


def self_test():
    ok = True
    for slug, url, style in FIXTURES:
        path = os.path.join(HERE, slug, "index.html")
        if not os.path.isfile(path):
            print("  SKIP %-24s index.html が無い" % slug)
            ok = False
            continue
        blocks = find_blocks(open(path, encoding="utf-8").read())
        if not blocks:
            print("  FAIL %-24s QRブロックを検出できない" % slug)
            ok = False
            continue
        b = blocks[0]
        if b.style != style:
            print("  FAIL %-24s 描き方の判定が %s（期待 %s）" % (slug, b.style, style))
            ok = False
            continue
        got = path_d(b.svg)
        exp = path_d(RENDERERS[style](url, b.color))
        neg = path_d(RENDERERS[style](OTHER_URL, b.color))
        if got != exp:
            print("  FAIL %-24s 再生成した path d が既存と一致しない（%s版）" % (slug, style))
            ok = False
        elif exp == neg:
            print("  FAIL %-24s 別URLからの生成物と区別できない" % slug)
            ok = False
        else:
            print("  PASS %-24s %s版 path d 一致・別URLとは不一致 (%d文字)" % (slug, style, len(got)))

    # 構造の検出そのもの
    sample = ('<a class="qr" href="https://x/a"><div class="qr-box">'
              '<svg class="segno"><path class="qrline" stroke="#000" d="M4 4.5h7"/></svg></div>'
              '<span class="qrcap">くわしい解説記事</span></a>')
    found = find_blocks(sample)
    if len(found) != 1 or found[0].href != "https://x/a":
        print("  FAIL 現行構造（a.qr > div.qr-box > svg）を検出できない")
        ok = False
    else:
        print("  PASS 現行構造（a.qr > div.qr-box > svg）を href つきで検出")
    if find_blocks("<!-- " + sample + " -->"):
        print("  FAIL HTMLコメント内の雛形に誤ヒットする")
        ok = False
    else:
        print("  PASS HTMLコメント内の雛形は無視する")
    return 0 if ok else 1


# --------------------------------------------------------------------------- 本体

def main():
    ap = argparse.ArgumentParser(description="ハンドアウトのQR（href＋画像）を記事URLに向け直す")
    ap.add_argument("--apply", action="store_true", help="実際に書き換える")
    ap.add_argument("--slug", action="append", default=[], help="対象を絞る（複数可）")
    ap.add_argument("--check-http", action="store_true",
                    help="dry-run でも記事URLの疎通を確認する（--apply では既定で確認する）")
    ap.add_argument("--skip-http-check", action="store_true",
                    help="--apply でも疎通確認を省く（確認済みの再実行用）")
    ap.add_argument("--diagnose", action="store_true",
                    help="厳密一致しなかったQRを読み取って中身を表示する（診断専用・合否には使わない）")
    ap.add_argument("--self-test", action="store_true", help="生成器の回帰テストだけ行う")
    args = ap.parse_args()

    if args.self_test:
        print("=== 生成器の回帰テスト ===")
        return self_test()

    check_http = (args.apply and not args.skip_http_check) or args.check_http
    blog = load_blog_urls()
    slugs = args.slug or sorted(d for d in os.listdir(HERE)
                                if os.path.isdir(os.path.join(HERE, d)) and d != "__pycache__")

    ok, changed, skipped, failed = [], [], [], []
    for slug in slugs:
        path = os.path.join(HERE, slug, "index.html")
        if not os.path.isfile(path):
            skipped.append((slug, "index.html が無い"))
            continue
        text = open(path, "rb").read().decode("utf-8")
        blocks = find_blocks(text)
        if not blocks:
            skipped.append((slug, "QRブロックが無い"))
            continue

        url, src = resolve_url(slug, blog)
        if not url:
            # URLが分からなくても、いま入っている href と画像が食い違っていないかは見る
            broken = [b for b in blocks if b.href and not qr_matches(b.href, b.svg)]
            if broken:
                failed.append((slug, "href と QR画像が食い違っている（記事URLも未登録）"))
            else:
                skipped.append((slug, "記事URLが未登録（記事が下書き）"))
            continue

        need = [b for b in blocks if needs_update(b, url)]
        if not need:
            ok.append((slug, url, src))
            continue
        note = ("旧構造（href 無し・画像のみ更新）"
                if all(b.href_span is None for b in need) else "")

        if check_http:
            st = http_status(url)
            time.sleep(2.5)
            if st != 200:
                skipped.append((slug, "記事URLが HTTP %s のため触らない" % st))
                continue

        edits, why, notes, bad = [], [], ([note] if note else []), None
        for b in need:
            new_svg = RENDERERS[b.style](url, b.color)
            # 生成器そのものの健全性（決定的か・別URLと区別できるか）を毎回確かめる
            if path_d(new_svg) != path_d(RENDERERS[b.style](url, b.color)):
                bad = "QR生成が非決定的（想定外）"
                break
            if path_d(new_svg) == path_d(RENDERERS[b.style](OTHER_URL, b.color)):
                bad = "別URLと同じQRが出た（想定外）"
                break
            if path_d(b.svg) != path_d(new_svg):
                edits.append((b.svg_span[0], b.svg_span[1], new_svg))
                why.append("画像")
                if args.diagnose:
                    got = diagnose(b.svg)
                    notes.append("いまのQRの中身=%s" % (got if got else "読み取れない"))
            if b.href_span and b.href != url:
                edits.append((b.href_span[0], b.href_span[1], url))
                why.append("href")
        if bad:
            failed.append((slug, bad))
            continue

        if args.apply:
            open(path, "wb").write(splice(text, edits).encode("utf-8"))
            # 書いたものを読み直して厳密照合する
            after = find_blocks(open(path, "rb").read().decode("utf-8"))
            if any(not qr_matches(url, b.svg) or (b.href_span and b.href != url) for b in after):
                failed.append((slug, "書き換え後の照合に失敗した"))
                continue
        changed.append((slug, url, src,
                        " ／ ".join(["＋".join(sorted(set(why)))] + notes)))

    print("=== 整合済み（QR画像と href が記事URLと厳密一致） ===")
    for slug, url, src in ok:
        print("  %-38s %-14s %s" % (slug, "[%s]" % src, url))
    if changed:
        print("\n=== 書き換え%s ===" % ("済" if args.apply else "対象（--apply で実行）"))
        for slug, url, src, why in changed:
            print("  %-38s %-14s %s  (%s)" % (slug, "[%s]" % src, url, why))
    if skipped:
        print("\n=== 未検査（QRは元のまま） ===")
        for slug, why in skipped:
            print("  %-38s %s" % (slug, why))
    if failed:
        print("\n=== 失敗 ===")
        for slug, why in failed:
            print("  %-38s %s" % (slug, why))

    print("\n整合 %d 件 ／ 書き換え%s %d 件 ／ 未検査 %d 件 ／ 失敗 %d 件"
          % (len(ok), "済" if args.apply else "対象", len(changed), len(skipped), len(failed)))
    if failed:
        return 1
    if skipped or (changed and not args.apply):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
