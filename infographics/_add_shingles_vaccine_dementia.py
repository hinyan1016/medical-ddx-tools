# -*- coding: utf-8 -*-
"""manifest.json に 帯状疱疹ワクチンと認知症 item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "shingles-vaccine-dementia",
    "title": "帯状疱疹ワクチンで認知症も減る？｜最新研究で分かったこと・まだ言えないこと",
    "desc": (
        "帯状疱疹ワクチンと認知症の関係を「確立していること」「分かってきたこと」「まだ言えないこと」の"
        "3段階で整理。ウェールズ自然実験（生ワクチン）では7年間で新たに認知症と診断された人が100人中約3.5人少ない"
        "（相対約20%減）。「健康な人ほど打つ」「診断が遅れただけ」「先に亡くなった人」という別の説明、"
        "組換えワクチンの無作為化試験（2026年開始・主な結果は2029〜2030年以降）まで1枚にまとめた。"
    ),
    "audience": "一般",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/07/071412",
    "date": "2026-09-07",
    "youtube_id": "ihG-WRWm0jE",
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
