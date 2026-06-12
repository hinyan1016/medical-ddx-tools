#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スライド公開ページビルダー
==========================
manifest.json を読み、各 deck のフォルダにビューア index.html / PDF / PNG を配置する。

実行例:
  python build.py                # 全 deck をビルド
  python build.py --slug dementia-feeding-refusal   # 単一 deck
  python build.py --dry-run      # コピー先・上書き予定をプレビュー

前提:
  - medical-content/youtube-slides/<source_dir>/ にPNGとPDFがある
  - medical-ddx-tools/slides/_template/viewer.html, index_template.html が存在

CRLF回避: open(..., newline='') で書き込む。
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
SLIDES_ROOT = THIS.parent.parent                    # medical-ddx-tools/slides/
DDX_ROOT = SLIDES_ROOT.parent                       # medical-ddx-tools/
WORKSPACE = DDX_ROOT.parent                          # Claude_task_new/
SOURCE_ROOT = WORKSPACE / "medical-content" / "youtube-slides"
TEMPLATE_DIR = SLIDES_ROOT / "_template"
MANIFEST = SLIDES_ROOT / "manifest.json"


def load_manifest():
    with open(MANIFEST, "r", encoding="utf-8") as f:
        return json.load(f)


def render_viewer(deck: dict, slide_count: int) -> str:
    template = (TEMPLATE_DIR / "viewer.html").read_text(encoding="utf-8")

    cards_html = []
    for i in range(1, slide_count + 1):
        num = f"{i:02d}"
        cards_html.append(
            f'    <div class="slide-card" data-idx="{i-1}">\n'
            f'      <span class="slide-num">{i} / {slide_count}</span>\n'
            f'      <img src="slide-{num}.png" alt="スライド{i}" loading="lazy">\n'
            f'    </div>'
        )

    blog_button = ""
    if deck.get("blog_url"):
        blog_button = (
            f'    <a class="btn btn-blog" href="{deck["blog_url"]}" target="_blank" rel="noopener">\n'
            f'      📝 解説記事を読む\n'
            f'    </a>'
        )

    youtube_button = ""
    yt_id = deck.get("youtube_id") or ""
    if yt_id:
        youtube_button = (
            f'    <a class="btn btn-youtube" href="https://youtu.be/{yt_id}" target="_blank" rel="noopener">\n'
            f'      ▶ YouTubeで動画を見る\n'
            f'    </a>'
        )

    html_deck_button = ""
    if deck.get("html_deck"):
        html_deck_button = (
            '    <a class="btn btn-deck" href="deck.html" target="_blank" rel="noopener">\n'
            '      🖥 インタラクティブ版（HTMLスライド）\n'
            '    </a>'
        )

    replacements = {
        "{{HTML_DECK_BUTTON}}": html_deck_button,
        "{{TITLE}}": deck["title"],
        "{{SUBTITLE}}": deck.get("subtitle", ""),
        "{{DESCRIPTION}}": deck.get("description", deck["title"]),
        "{{YOUTUBE_ID}}": yt_id,
        "{{YOUTUBE_BUTTON}}": youtube_button,
        "{{SLIDE_COUNT}}": str(slide_count),
        "{{SLIDE_CARDS}}": "\n".join(cards_html),
        "{{BLOG_BUTTON}}": blog_button,
    }
    html = template
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html


def render_index(decks: list) -> str:
    template = (TEMPLATE_DIR / "index_template.html").read_text(encoding="utf-8")

    cards_html = []
    for d in decks:
        search_text = " ".join([
            d.get("title", ""),
            d.get("subtitle", ""),
            d.get("description", ""),
            " ".join(d.get("tags", [])),
        ]).lower()
        tags_html = "".join(
            f'<span class="tag">{t}</span>' for t in d.get("tags", [])[:3]
        )
        cards_html.append(
            f'    <a class="deck-card" href="{d["slug"]}/" data-search="{search_text}">\n'
            f'      <div class="thumb"><img src="{d["slug"]}/slide-01.png" alt="" loading="lazy"></div>\n'
            f'      <div class="body">\n'
            f'        <div class="deck-title">{d["title"]}</div>\n'
            f'        <div class="deck-desc">{d.get("subtitle", "")}</div>\n'
            f'        <div class="deck-meta">{tags_html}<span>📊 {d["slide_count"]}枚</span></div>\n'
            f'      </div>\n'
            f'    </a>'
        )
    return template.replace("{{DECK_CARDS}}", "\n".join(cards_html))


def build_deck(deck: dict, dry_run: bool = False) -> bool:
    slug = deck["slug"]
    src = SOURCE_ROOT / deck["source_dir"]
    dst = SLIDES_ROOT / slug

    if not src.exists():
        print(f"  [SKIP] source not found: {src}", file=sys.stderr)
        return False

    prefix = deck.get("slide_prefix", "slide-")
    slide_count = deck["slide_count"]

    # PNG existence check
    missing = []
    for i in range(1, slide_count + 1):
        png = src / f"{prefix}{i:02d}.png"
        if not png.exists():
            missing.append(png.name)
    if missing:
        print(f"  [SKIP] missing PNGs: {missing[:3]}{'...' if len(missing)>3 else ''}", file=sys.stderr)
        return False

    pdf_src = src / deck["pdf_filename"]
    if not pdf_src.exists():
        print(f"  [SKIP] PDF not found: {pdf_src.name}", file=sys.stderr)
        return False

    if dry_run:
        print(f"  [DRY] would write {dst}/  (PNG x{slide_count}, PDF, index.html)")
        return True

    dst.mkdir(parents=True, exist_ok=True)

    # Copy PNGs (normalize to slide-NN.png)
    for i in range(1, slide_count + 1):
        png_src = src / f"{prefix}{i:02d}.png"
        png_dst = dst / f"slide-{i:02d}.png"
        shutil.copy2(png_src, png_dst)

    # Copy PDF (rename to slides.pdf for stable URL)
    shutil.copy2(pdf_src, dst / "slides.pdf")

    # Write viewer
    viewer_html = render_viewer(deck, slide_count)
    (dst / "index.html").write_text(viewer_html, encoding="utf-8", newline="\n")

    print(f"  [OK] {slug} ({slide_count}枚 + PDF)")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug", help="特定の slug のみビルド")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-index", action="store_true", help="一覧ページの再生成をスキップ")
    args = parser.parse_args()

    manifest = load_manifest()
    decks = manifest["decks"]

    if args.slug:
        decks_to_build = [d for d in decks if d["slug"] == args.slug]
        if not decks_to_build:
            print(f"slug not found in manifest: {args.slug}", file=sys.stderr)
            sys.exit(1)
    else:
        decks_to_build = decks

    print(f"Building {len(decks_to_build)} deck(s)...")
    built = []
    for d in decks_to_build:
        ok = build_deck(d, dry_run=args.dry_run)
        if ok:
            built.append(d)

    if not args.skip_index and not args.dry_run:
        # 一覧は manifest 全体で再生成
        index_html = render_index(decks)
        (SLIDES_ROOT / "index.html").write_text(index_html, encoding="utf-8", newline="\n")
        print(f"  [OK] index.html ({len(decks)} decks)")

    print(f"Done. {len(built)} deck(s) built.")


if __name__ == "__main__":
    main()
