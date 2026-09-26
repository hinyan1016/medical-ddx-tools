# -*- coding: utf-8 -*-
"""manifest.json に ナラティブ・ベイスト・メディスン（NBM）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "narrative-based-medicine",
    "title": "ナラティブ・ベイスト・メディスン（NBM）とは｜EBMを患者に届ける「聴く技術」",
    "subtitle": "EBMとの関係・遮らずに聴く・問い方・聴きすぎを防ぐ枠（医療者向け）",
    "description": (
        "NBMはEBMの反対概念ではなく、エビデンスを目の前の患者さんに届けるための枠組みです。"
        "EBMの定義、同じ結果でも語り方で印象が変わる数字（SHEP研究）、診察の冒頭で患者さんの話が遮られているという研究、"
        "開かれた質問から閉じた質問への問い方、聴きすぎを防ぐ時間・場所・役割・記録の枠、外来チェックリストまでを"
        "全17枚のスライドで整理します。"
    ),
    "youtube_id": "xtTPRg9YlJA",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/26/152310",
    "source_dir": "narrative_based_medicine/work/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": ["ナラティブ・ベイスト・メディスン", "NBM", "EBM", "医療コミュニケーション", "医療面接", "医師向け"],
    "published_date": "2026-09-26",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診療判断に代わるものではありません。内容は2026年9月26日時点の資料に基づきます。",
    "html_deck": False,
    "infographic": True,
}


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = m["decks"]
    idx = next((i for i, d in enumerate(decks) if d["slug"] == DECK["slug"]), None)
    if idx is None:
        decks.insert(0, DECK)
        print("added deck:", DECK["slug"])
    else:
        decks[idx] = DECK
        print("updated deck:", DECK["slug"])
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print("total decks:", len(decks))


if __name__ == "__main__":
    main()
