# -*- coding: utf-8 -*-
"""manifest.json に AGA個人輸入スライドを追加する（既存なら更新）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "aga-personal-import",
    "title": "AGA治療は個人輸入でよい？",
    "subtitle": "5％ミノキシジル外用・フィナステリド・デュタステリドを効果・費用・安全性で比較",
    "description": (
        "男性型脱毛症（AGA）の標準治療である5％ミノキシジル外用、フィナステリド、"
        "デュタステリドについて、効果、費用、安全性を15枚で整理。個人輸入や国内オンライン診療を"
        "選ぶ際に、薬の価格だけでなく、承認区分、品質確認、副作用時の対応、救済制度まで確認する"
        "ポイントを医師が解説します。"
    ),
    "youtube_id": "940jJf6xjmQ",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/14/065654",
    "source_dir": "aga_personal_import/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": ["AGA", "男性型脱毛症", "個人輸入", "薄毛治療"],
    "published_date": "2026-07-14",
    "html_deck": False,
    "infographic": False,
}


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = manifest["decks"]
    index = next((i for i, deck in enumerate(decks) if deck["slug"] == DECK["slug"]), None)
    if index is None:
        decks.insert(0, DECK)
        print("added deck:", DECK["slug"])
    else:
        decks[index] = DECK
        print("updated deck:", DECK["slug"])
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("total decks:", len(decks))


if __name__ == "__main__":
    main()
