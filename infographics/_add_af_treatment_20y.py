# -*- coding: utf-8 -*-
"""infographics/manifest.json に 心房細動治療 この20年の変遷 item を追加する（既存なら更新）。

2026-10-22 先生指示「バッチ21の3記事を公開してください。」（過去記事の根拠修復で作り直したインフォ画像）。
ページ本体は infographics/af-treatment-20y/（infographic.png は medical-content/blog/reference-repair/20261004/articles/af-treatment-20y/infographic/generated/ の確定版の複製）。
続けて add_nav_and_image.py --no-png --only af-treatment-20y・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
blog_url は既存記事のURL（本文の差し替えでURLは変わらない）。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "af-treatment-20y",
    "title": "心房細動治療 この20年の変遷",
    "desc": "2005年頃から現在まで──ワルファリンからDOACへ、リスク評価、早期リズムコントロール、アブレーション、左心耳閉鎖、検出の進歩、包括的ケアを1枚に整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2025/05/19/193255",
    "date": "2026-10-22",
    "youtube_id": "",
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
