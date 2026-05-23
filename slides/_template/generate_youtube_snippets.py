#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""manifest.json の各 deck に対し、YouTube 概要欄追加用スニペットを生成。

出力:
- youtube_snippets.md: 人間用一覧 (YouTube ID, 編集URL, 追加スニペット)
- youtube_snippets.json: 機械処理用 (Claude in Chrome 自動化など)

スニペット仕様:
- 5000字制限を考慮し、できるだけ簡潔
- YouTube Studio で禁止される < > は使わない
- スライド資料への直リンクと一覧へのリンクの両方を提供
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[3]
SLIDES_ROOT = WORKSPACE / "medical-ddx-tools" / "slides"
MANIFEST = SLIDES_ROOT / "manifest.json"
OUT_MD = SLIDES_ROOT / "youtube_snippets.md"
OUT_JSON = SLIDES_ROOT / "youtube_snippets.json"

SNIPPET_TEMPLATE = """━━━━━━━━━━━━━━━━━━━━
📊 スライド資料（動画を見る時間がない方へ）

▼ 本動画のスライドを閲覧/PDFダウンロード
{deck_url}

▼ 医知創造ラボ スライド資料一覧（全{total_decks}本）
{index_url}

▼ 鑑別診断ツール集
https://tools.ichisouzo-lab.com/

▼ ブログ「医知創造ラボ」
https://blog.ichisouzo-lab.com/
━━━━━━━━━━━━━━━━━━━━"""


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = manifest["decks"]
    total_decks = sum(1 for d in decks if d.get("youtube_id"))

    snippets = []
    for d in decks:
        yt_id = d.get("youtube_id")
        if not yt_id:
            continue
        slug = d["slug"]
        deck_url = f"https://tools.ichisouzo-lab.com/slides/{slug}/"
        index_url = "https://tools.ichisouzo-lab.com/slides/"
        snippet = SNIPPET_TEMPLATE.format(
            deck_url=deck_url,
            index_url=index_url,
            total_decks=total_decks,
        )
        edit_url = f"https://studio.youtube.com/video/{yt_id}/edit"
        snippets.append({
            "slug": slug,
            "title": d["title"],
            "youtube_id": yt_id,
            "edit_url": edit_url,
            "watch_url": f"https://youtu.be/{yt_id}",
            "deck_url": deck_url,
            "snippet": snippet,
        })

    # JSON output
    OUT_JSON.write_text(
        json.dumps(snippets, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )

    # Markdown output (一覧 + 各動画のスニペット)
    md = []
    md.append(f"# YouTube 概要欄追加スニペット")
    md.append("")
    md.append(f"対象: {len(snippets)} 動画（manifest中 youtube_id を持つもの）")
    md.append(f"生成日: 2026-05-24")
    md.append("")
    md.append("## 追加方法")
    md.append("各動画のYouTube Studio (`edit_url` 列のURL) を開き、")
    md.append("「説明」欄の**末尾**にスニペットを貼り付ける。")
    md.append("既存の説明文は保持。")
    md.append("")
    md.append("## 動画一覧と編集URL")
    md.append("")
    md.append("| slug | YouTube | 編集URL |")
    md.append("|---|---|---|")
    for s in snippets:
        md.append(f"| {s['slug']} | [{s['youtube_id']}]({s['watch_url']}) | [Edit]({s['edit_url']}) |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 各動画のスニペット")
    md.append("")
    for s in snippets:
        md.append(f"### {s['title']}")
        md.append(f"- YouTube: {s['watch_url']}")
        md.append(f"- 編集URL: {s['edit_url']}")
        md.append("")
        md.append("```")
        md.append(s["snippet"])
        md.append("```")
        md.append("")
    OUT_MD.write_text("\n".join(md), encoding="utf-8", newline="\n")

    print(f"Generated {len(snippets)} snippets")
    print(f"  MD: {OUT_MD}")
    print(f"  JSON: {OUT_JSON}")


if __name__ == "__main__":
    main()
