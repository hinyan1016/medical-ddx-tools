# -*- coding: utf-8 -*-
"""manifest.json の先頭に「高齢者の皮膚のかゆみ」を追加する（既存なら置換）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"
ITEM = {
    "slug": "elderly-itch-pruritus",
    "title": "高齢者の皮膚のかゆみ",
    "desc": "発疹のないかゆみで多い原因は乾燥。薬・体の病気・疥癬が隠れることも。ぬるめの入浴とすぐの保湿、受診の目安を図で整理。",
    "audience": "一般向け",
    "date": "2026-11-06",
    "youtube_id": "8H_w7eTzQaQ",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2025/05/05/233646",
}


def main():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    items = m["items"]
    idx = next((i for i, it in enumerate(items) if it["slug"] == ITEM["slug"]), None)
    if idx is None:
        items.insert(0, ITEM)
    else:
        items[idx] = ITEM
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK", ITEM["slug"], "idx" if idx is not None else "inserted")


if __name__ == "__main__":
    main()
