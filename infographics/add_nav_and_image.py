#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""各インフォグラフィック index.html に
  (1) 画像版 PNG（infographic.png）を .ig からレンダリングして同フォルダに配置
  (2) 上下に「インフォグラフィック一覧へ」「画像版（PNG）」ナビを挿入
を行う。冪等（マーカーで二重挿入防止）。nav は .ig の外なので PNG/サムネには写らない。
  (3) SNSで共有したときのプレビュー（説明文・OGP・Twitterカード）を <head> に入れる。
      og:image はトップ側の thumbs/og/<slug>.jpg（ichisouzo-lab.com が6時間ごとに作る、上部を切り出したJPEG）

実行: python add_nav_and_image.py [--no-png] [--only <slug>]
      python add_nav_and_image.py --meta-only   # 共有用の<head>だけを全件に入れ直す（ナビ・PNGは触らない）
"""
import argparse, html, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDER = HERE.parent.parent / "medical-content" / "youtube-slides" / "_shared_scripts" / "render_html_to_png.py"
MARK = "ig-nav-v2"
_BTN = "display:inline-flex;align-items:center;gap:6px;text-decoration:none;font-weight:700;font-size:14px;padding:9px 15px;border-radius:8px;"


def build_nav(youtube_id: str, mt: str, mb: str) -> str:
    yt = ('<a href="https://youtu.be/{yid}" target="_blank" rel="noopener" style="{b}background:#C0392B;color:#fff;">▶ 解説動画（YouTube）</a>'.format(yid=youtube_id, b=_BTN)
          if youtube_id else "")
    return (
        '<nav data-{mark} style="width:100%;max-width:1080px;display:flex;gap:10px;flex-wrap:wrap;'
        'align-items:center;margin:{mt} auto {mb};font-family:\'Hiragino Kaku Gothic ProN\',\'Yu Gothic\',\'Segoe UI\',sans-serif;">'
        '<a href="../" style="{b}background:#1A5276;color:#fff;">🖼️ インフォグラフィック一覧</a>'
        '{yt}'
        '<a href="infographic.png" target="_blank" rel="noopener" style="{b}background:#fff;color:#1A5276;border:1px solid #cfdae6;">📥 画像版（PNG）</a>'
        '</nav>'
    ).format(mark=MARK, mt=mt, mb=mb, b=_BTN, yt=yt)


# render_html_to_png.py の既定ビューポートは 1200。要素スクショなので、.ig が
# 固定幅ならビューポート幅は結果に効かないが、**流動幅（width:100%）のページでは
# ビューポート幅がそのまま PNG 幅になる**。1200 を超えるキャンバスを持つページを
# 既定のまま撮ると、狭いビューポートに合わせて黙って縮む。
# そこでページ自身が宣言している幅を読み、それが収まるビューポートを渡す。
_IG_RULE = re.compile(r"\.ig\s*\{([^}]*)\}")
_PX = re.compile(r"(?:max-)?width\s*:\s*(\d+)px")


def canvas_width(html: str):
    """.ig の基底ルールが宣言している最大の px 幅。見つからなければ None。

    最初に現れる .ig ルールだけを見る（media query 内の上書きは基底より後ろ）。
    """
    m = _IG_RULE.search(html)
    if not m:
        return None
    vals = [int(v) for v in _PX.findall(m.group(1))]
    return max(vals) if vals else None


META_START, META_END = "<!-- ig-meta -->", "<!-- /ig-meta -->"
_META_BLOCK = re.compile(r"\n?" + re.escape(META_START) + r".*?" + re.escape(META_END) + r"\n?", re.S)


def apply_meta(page: str, item: dict) -> str:
    """共有用の<head>（説明文・OGP・Twitterカード）を、目印コメントの間に入れ直す。冪等。"""
    slug = item["slug"]
    attr = lambda s: html.escape(s or "", quote=True)
    page = _META_BLOCK.sub("", page)
    title, desc = item.get("title", ""), item.get("desc", "")
    lines = [META_START]
    if not re.search(r'<meta\s+name="description"', page, re.I):
        lines.append('<meta name="description" content="{}">'.format(attr(desc)))
    lines += [
        '<meta property="og:title" content="{}">'.format(attr(title)),
        '<meta property="og:description" content="{}">'.format(attr(desc)),
        '<meta property="og:type" content="article">',
        '<meta property="og:url" content="https://tools.ichisouzo-lab.com/infographics/{}/">'.format(slug),
        '<meta property="og:image" content="https://ichisouzo-lab.com/thumbs/og/{}.jpg">'.format(slug),
        '<meta property="og:image:alt" content="{}">'.format(attr(title)),
        '<meta property="og:site_name" content="医知創造ラボ">',
        '<meta property="og:locale" content="ja_JP">',
        '<meta name="twitter:card" content="summary_large_image">',
        META_END,
    ]
    # 前後に改行を1つずつ付けて入れ、外すときも1つずつ外す（1行に詰めた<head>でも元に戻る）。
    block = "\n" + "\n".join(lines) + "\n"
    if re.search(r"</head>", page, re.I):
        return re.sub(r"</head>", lambda m: block + m.group(0), page, count=1, flags=re.I)
    return re.sub(r"</title>", lambda m: m.group(0) + block, page, count=1, flags=re.I)


def process(item: dict, do_png: bool):
    slug = item["slug"]; yid = item.get("youtube_id", "")
    f = HERE / slug / "index.html"
    if not f.exists():
        print("  [skip] no index:", slug); return
    if do_png:
        out = HERE / slug / "infographic.png"
        cw = canvas_width(f.read_text(encoding="utf-8"))
        cmd = [sys.executable, str(RENDER), "--html", str(f), "--out", str(out),
               "--selector", ".ig", "--dsf", "2"]
        if cw and cw > 1200:
            cmd += ["--width", str(cw + 100)]   # 余白100pxはスクロールバー分
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        print("  png:", slug, "OK" if out.exists() else "FAIL", (r.stderr or "").strip()[:100])
    s = f.read_text(encoding="utf-8")
    # body を縦並び中央寄せに（旧版で未変更なら）
    # 末尾セミコロンの有無どちらにも対応（HTMLデッキ版は `...center}` で `;` が無く、
    # 旧 .replace() では置換漏れ→bodyが横並びflexのまま、ナビと本体がモバイルで左右に潰れる不具合があった）
    s = re.sub(r"display:flex;\s*justify-content:center;?",
               "display:flex;flex-direction:column;align-items:center;", s)
    # 既存ナビ（旧版含む）を除去してから新ナビを挿入（冪等・差し替え可能）
    s = re.sub(r"\n?<nav data-ig-nav[^>]*>.*?</nav>", "", s, flags=re.S)
    s = re.sub(r"(<body[^>]*>)", r"\1\n" + build_nav(yid, "0", "12px"), s, count=1)
    s = s.replace("</body>", build_nav(yid, "14px", "0") + "\n</body>", 1)
    s = apply_meta(s, item)
    f.write_text(s, encoding="utf-8", newline="\n")
    print("  [nav~] ", slug, "(YT)" if yid else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--only", help="単一slugのみ")
    ap.add_argument("--meta-only", action="store_true", help="共有用の<head>だけを入れ直す（ナビ・PNG・本文は触らない）")
    args = ap.parse_args()
    items = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["items"]
    targets = [it for it in items if (not args.only or it["slug"] == args.only)]
    for it in targets:
        if args.meta_only:
            f = HERE / it["slug"] / "index.html"
            if not f.exists():
                continue
            raw = f.read_bytes().decode("utf-8")
            newline = "\r\n" if "\r\n" in raw else "\n"
            updated = apply_meta(raw.replace("\r\n", "\n"), it).replace("\n", newline)
            if updated != raw:
                f.write_bytes(updated.encode("utf-8"))
                print("  [meta~]", it["slug"])
            continue
        process(it, do_png=not args.no_png)


if __name__ == "__main__":
    main()
