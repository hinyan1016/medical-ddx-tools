# -*- coding: utf-8 -*-
"""manifest.json に 高齢者の皮膚のかゆみ deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "elderly-itch-pruritus",
    "title": "高齢者の皮膚のかゆみ｜いちばん多い原因は乾燥・家でできるケアと受診の目安",
    "subtitle": "発疹がないのにかゆい原因、薬や病気の見分け、入浴と保湿のコツを医師が解説",
    "description": (
        "高齢者で発疹がないのに続く皮膚のかゆみ（皮膚瘙痒症）について、いちばん多い原因で"
        "ある皮膚の乾燥のしくみ、掻くほどかゆくなる悪循環、ふだんの薬・体の病気・疥癬や"
        "水疱性類天疱瘡など見落とされやすい原因、病院での診察と検査を整理。ぬるめのお湯・"
        "やさしい洗い方・入浴後の保湿など家庭でできるケア、病院での治療、ご家族の方への"
        "ヒント、受診を考えたい目安まで、全24スライドで。"
    ),
    "youtube_id": "8H_w7eTzQaQ",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2025/05/05/233646",
    "source_dir": "elderly-itch-pruritus/work/20261106-imagegen/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 24,
    "tags": ["皮膚のかゆみ", "皮膚瘙痒症", "高齢者", "保湿", "スキンケア"],
    "published_date": "2026-11-06",
    "html_deck": False,
    "infographic": False,
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
