# -*- coding: utf-8 -*-
"""infographics/manifest.json に パーキンソン病と遺伝子異常（図13点の一覧ページ）item を追加する（既存なら更新）。

公開前の下書き（2026-10-10）。ページ本体は publishing/infographics/parkinson-genetics/（build_gallery.py の出力）。
先生の公開承認のあと、そのフォルダを medical-ddx-tools/infographics/ にコピーし、この台本を infographics/ に置いて実行する。
続けて card.webp・cards.json・infographics/index.html（build_index.py）・sw.js の ASSETS と CACHE_NAME の版上げ、
check_sw_cache.py を通す（tools 登録の6点セット）。blog_url・youtube_id は公開後に実値へ。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "parkinson-genetics",
    "title": "パーキンソン病と遺伝子異常｜図で読むポイント",
    "desc": "GBA1・LRRK2・PRKN を中心に、遺伝的構造、発症年齢、関わる経路、検査で見つかる割合、日本人のデータ、SAA と DBS、遺伝学的検査の考え方、遺伝子標的治療の現状を13枚の図で整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/11/025722",
    "date": "2026-10-10",
    "youtube_id": "owAAzGe1M7Q",
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
