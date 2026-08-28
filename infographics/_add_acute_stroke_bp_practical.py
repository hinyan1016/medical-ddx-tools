# -*- coding: utf-8 -*-
"""manifest.json に 脳卒中急性期の降圧実務 item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "acute-stroke-bp-practical",
    "title": "脳卒中急性期の降圧はどう行うか｜脳梗塞・脳出血に共通するニカルジピン持続静注の計算・上げ下げ・内服移行の臨床実務",
    "desc": (
        "脳卒中（脳梗塞・脳出血）急性期の降圧目標値は病型により異なるが、第一選択薬であるニカルジピン持続静注の"
        "換算計算式、増減プロトコル、偽高血圧の除外、嚥下評価後の内服移行手順は共通している。"
        "開始量0.5 µg/kg/分（＝0.03 mg/kg/時）から、5倍希釈なら「体重×0.15 mL/時」で計算。"
        "増量前に尿閉・疼痛・カフ不良を除外。内服移行時は水飲みテスト等で嚥下を確認し、"
        "アムロジピン等の長時間作用薬を開始後、数時間静注を重ねるオーバーラップ投与で安全に漸減離脱する。"
        "脳卒中治療ガイドライン2021〔改訂2025〕および添付文書・主要RCTに基づき整理した医療従事者向けの図。"
    ),
    "audience": "医療従事者向け",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/29/083033",
    "date": "2026-08-29",
    "youtube_id": "cd2kMzEt6HI",
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