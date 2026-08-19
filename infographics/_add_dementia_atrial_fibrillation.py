# -*- coding: utf-8 -*-
"""manifest.json に 心房細動と認知症（認知症×生活習慣病シリーズ第10弾）item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "dementia-atrial-fibrillation",
    "title": "心房細動と認知症｜脳梗塞がなくてもリスクは上がるのか",
    "desc": (
        "心房細動のある人では、臨床的な脳梗塞を起こしていなくても、その後の認知症が多い——"
        "43研究のメタ解析で調整OR1.6（95%CI 1.3–2.1）。脳卒中を考慮・打ち切っても関連は残る"
        "（RR1.34・HR1.23・HR1.33）が、67歳以上では有意でない。では抗凝固薬でそのリスクを"
        "下げられるのか。観察研究では使っている人で認知症が少なく見える（HR0.71）が、"
        "観察ウィンドウを揃えるとRR0.75、日本のレセプトデータでもHR0.66に消え、いずれも有意でない。"
        "検証した最大のランダム化試験（BRAIN-AF）はHR1.10で無益と判定され早期中止された"
        "（対象は平均53.4歳の低リスク層）。心房細動はLancetの認知症14因子リストには入っていないが、"
        "それは「重要でない」という意味ではない。認知症×生活習慣病シリーズ第10弾。"
    ),
    "audience": "医療者・一般",
    "blog_url": "",
    "date": "2026-08-19",
    "youtube_id": "",
    "_todo": (
        "投稿後に要更新: blog_url と youtube_id が未確定（作成日2026-08-19時点）。"
        "公開後に実値へ差し替え、add_nav_and_image.py --only dementia-atrial-fibrillation を再実行すること。"
    ),
}


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = m["items"]
    idx = next((i for i, it in enumerate(items) if it["slug"] == ITEM["slug"]), None)
    if idx is None:
        items.insert(0, ITEM)
        print("added item:", ITEM["slug"])
    else:
        items[idx] = ITEM
        print("updated item:", ITEM["slug"])
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("items:", len(items))


if __name__ == "__main__":
    main()
