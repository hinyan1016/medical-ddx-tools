#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""各インフォグラフィック index.html に
  (1) 画像版 PNG（infographic.png）を .ig からレンダリングして同フォルダに配置
  (2) 上下に「インフォグラフィック一覧へ」「画像版（PNG）」ナビを挿入
を行う。冪等（マーカーで二重挿入防止）。nav は .ig の外なので PNG/サムネには写らない。

実行: python add_nav_and_image.py [--no-png]
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDER = HERE.parent.parent / "medical-content" / "youtube-slides" / "_shared_scripts" / "render_html_to_png.py"
MARK = "ig-nav-v1"

NAV = (
    '<nav data-{mark} style="width:100%;max-width:1080px;display:flex;gap:10px;flex-wrap:wrap;'
    'align-items:center;margin:{mt} auto {mb};font-family:\'Hiragino Kaku Gothic ProN\',\'Yu Gothic\',\'Segoe UI\',sans-serif;">'
    '<a href="../" style="display:inline-flex;align-items:center;gap:6px;background:#1A5276;color:#fff;'
    'text-decoration:none;font-weight:700;font-size:14px;padding:9px 15px;border-radius:8px;">🖼️ インフォグラフィック一覧</a>'
    '<a href="infographic.png" target="_blank" rel="noopener" style="display:inline-flex;align-items:center;gap:6px;'
    'background:#fff;color:#1A5276;text-decoration:none;font-weight:700;font-size:14px;padding:9px 15px;'
    'border-radius:8px;border:1px solid #cfdae6;">📥 画像版（PNG）</a>'
    '</nav>'
)
NAV_TOP = NAV.format(mark=MARK, mt="0", mb="12px")
NAV_BOTTOM = NAV.format(mark=MARK, mt="14px", mb="0")


def process(slug: str, do_png: bool):
    f = HERE / slug / "index.html"
    if not f.exists():
        print("  [skip] no index:", slug); return
    if do_png:
        out = HERE / slug / "infographic.png"
        r = subprocess.run([sys.executable, str(RENDER), "--html", str(f), "--out", str(out),
                            "--selector", ".ig", "--dsf", "2"], capture_output=True, text=True, encoding="utf-8")
        print("  png:", slug, "OK" if out.exists() else "FAIL", (r.stderr or "").strip()[:100])
    s = f.read_text(encoding="utf-8")
    if MARK in s:
        print("  [nav exists] ", slug); return
    # body を縦並び中央寄せに（nav と .ig を縦に積む）
    s = s.replace("display:flex;justify-content:center;", "display:flex;flex-direction:column;align-items:center;")
    # 先頭 nav を <body> 直後、末尾 nav を </body> 直前に
    s = re.sub(r"(<body[^>]*>)", r"\1\n" + NAV_TOP, s, count=1)
    s = s.replace("</body>", NAV_BOTTOM + "\n</body>", 1)
    f.write_text(s, encoding="utf-8", newline="\n")
    print("  [nav+] ", slug)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--only", help="単一slugのみ")
    args = ap.parse_args()
    items = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["items"]
    slugs = [args.only] if args.only else [it["slug"] for it in items]
    for sl in slugs:
        process(sl, do_png=not args.no_png)


if __name__ == "__main__":
    main()
