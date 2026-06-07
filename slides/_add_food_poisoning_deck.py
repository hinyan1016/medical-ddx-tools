# -*- coding: utf-8 -*-
"""manifest.json に夏の食中毒 deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "summer-food-poisoning",
    "title": "夏の食中毒、その下痢どうする？",
    "subtitle": "原因菌×潜伏時間の早見表・下痢止めNG・O157の危険サイン",
    "description": (
        "夏に増える細菌性食中毒（カンピロバクター・O157・サルモネラ・黄色ブドウ球菌・"
        "腸炎ビブリオ）を脳神経内科医が解説。原因菌ごとの潜伏時間の早見表、家庭での正しい"
        "水分補給、やってはいけない下痢止め・残り物の抗生物質、O157の溶血性尿毒症症候群"
        "（HUS）の危険サインと受診の目安まで、全14スライドで。"
    ),
    "youtube_id": "sOMj9mbSJfU",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/06/08/032049",
    "source_dir": "夏の食中毒/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "../summer-food-poisoning_スライド.pdf",
    "slide_count": 14,
    "tags": ["食中毒", "夏の感染症", "O157"],
    "published_date": "2026-06-08",
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
    MANIFEST.write_text(
        json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print("total decks:", len(decks))


if __name__ == "__main__":
    main()
