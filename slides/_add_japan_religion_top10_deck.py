# -*- coding: utf-8 -*-
"""manifest.json に 日本の宗教 信者数トップ10 deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "japan-religion-top10",
    "title": "日本の宗教 信者数トップ10｜人口より多い信者数の理由と上位10の宗教",
    "subtitle": "文化庁『宗教年鑑』令和7年版と各団体の公式サイトから、信者数の多い宗教を順に紹介",
    "description": (
        "文化庁『宗教年鑑』令和7年版（令和6年12月31日現在）の信者数の合計は約1億7505万人で、"
        "日本の総人口の約1.4倍にあたります。人口より多くなる理由と順位の見方を整理したうえで、"
        "神道系・仏教系・キリスト教系の系統合計と新宗教の教団を並べた信者数トップ10を、"
        "数字を見るときの注意とあわせて全17スライドで紹介します。"
    ),
    "youtube_id": "Gc7XyzuuBcg",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/01/11/004510",
    "source_dir": "japan-religion-top10/work/20261109-imagegen/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": ["日本の宗教", "信者数", "宗教年鑑", "新宗教", "一般教養"],
    "published_date": "2026-11-09",
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
