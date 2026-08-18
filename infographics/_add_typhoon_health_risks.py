# -*- coding: utf-8 -*-
"""manifest.json に 台風と病気リスク item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "typhoon-health-risks",
    "title": "台風で増える病気はあるのか？｜脳卒中・心筋梗塞から感染症、持病の悪化まで",
    "desc": (
        "台風の健康リスクは気圧だけではない。日本の全国入院データでは台風曝露後0〜6日で脳卒中入院リスクが"
        "1.049倍（脳内出血1.131倍）、中国の全国規模研究では台風曝露後0〜3日の急性冠症候群リスクが1.14倍。"
        "米国高齢者の研究では熱帯低気圧曝露後1週間で呼吸器疾患入院が14.2%増加。これらはいずれも観察研究で、"
        "個人の発症を保証するものではない。直接の危険・気象変化・避難停電・医療の中断という4つの経路を整理し、"
        "脳卒中や急性冠症候群のレッドフラッグ、避難生活で見逃せない3つの危険（深部静脈血栓症・一酸化炭素中毒・"
        "熱中症）、治療を中断させないための備えを1枚にまとめた。"
    ),
    "audience": "一般",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/18/194444",
    "date": "2026-08-18",
    "youtube_id": "",
    "_todo": (
        "動画公開後に要更新: youtube_id が未確定。"
        "公開後に実値へ差し替え、add_nav_and_image.py --only typhoon-health-risks を再実行すること。"
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
