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


def process(item: dict, do_png: bool):
    slug = item["slug"]; yid = item.get("youtube_id", "")
    f = HERE / slug / "index.html"
    if not f.exists():
        print("  [skip] no index:", slug); return
    if do_png:
        out = HERE / slug / "infographic.png"
        r = subprocess.run([sys.executable, str(RENDER), "--html", str(f), "--out", str(out),
                            "--selector", ".ig", "--dsf", "2"], capture_output=True, text=True, encoding="utf-8")
        print("  png:", slug, "OK" if out.exists() else "FAIL", (r.stderr or "").strip()[:100])
    s = f.read_text(encoding="utf-8")
    # body を縦並び中央寄せに（旧版で未変更なら）
    s = s.replace("display:flex;justify-content:center;", "display:flex;flex-direction:column;align-items:center;")
    # 既存ナビ（旧版含む）を除去してから新ナビを挿入（冪等・差し替え可能）
    s = re.sub(r"\n?<nav data-ig-nav[^>]*>.*?</nav>", "", s, flags=re.S)
    s = re.sub(r"(<body[^>]*>)", r"\1\n" + build_nav(yid, "0", "12px"), s, count=1)
    s = s.replace("</body>", build_nav(yid, "14px", "0") + "\n</body>", 1)
    f.write_text(s, encoding="utf-8", newline="\n")
    print("  [nav~] ", slug, "(YT)" if yid else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--only", help="単一slugのみ")
    args = ap.parse_args()
    items = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["items"]
    targets = [it for it in items if (not args.only or it["slug"] == args.only)]
    for it in targets:
        process(it, do_png=not args.no_png)


if __name__ == "__main__":
    main()
