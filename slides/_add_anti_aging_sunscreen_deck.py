# -*- coding: utf-8 -*-
"""manifest.json に 日焼け止めと肌の老化（医師が採点するアンチエイジング 第3回）deck を追加する（既存なら更新）。

2026-09-29 公開：youtube_id・published_date を記入。blog_url 記入済み。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-sunscreen",
    "title": "日焼け止めで肌の老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第3回）",
    "subtitle": "光老化・毎日塗った試験の結果・皮膚がんとの関係・塗り方と安全性（一般向け）",
    "description": (
        "日焼け止めで肌の老化は防げるのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は「効く」。"
        "毎日塗れば肌の老化の進みを遅らせますが、今あるシワやシミを消す効果は確かめられていません。"
        "毎日・たっぷり・塗り直す、という塗り方と、かぶれ・ビタミンDなどの安全性を、全16枚のスライドで説明します。"
    ),
    "youtube_id": "xe88aMqhvNs",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/29/121452",
    "source_dir": "anti-aging-sunscreen/work/rc6-20260929c/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 16,
    "tags": ["日焼け止め", "紫外線", "アンチエイジング", "医師が採点するアンチエイジング", "一般向け"],
    "published_date": "2026-09-29",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。赤みやかゆみが続くときは、皮膚科に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年9月29日時点の研究・公的資料に基づきます。",
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
