# -*- coding: utf-8 -*-
"""infographics/manifest.json に ICIによる筋炎（irAE筋炎・医師向け）item を追加する（既存なら更新）。

2026-10-13 先生指示「公開の作業をすすめてください。ブログは公開、動画は限定公開でお願いします。」
ページ本体は infographics/irae-myositis/（infographic.png は medical-content/youtube-slides/irae-myositis/current/publishing/infographic.png の複製）。
続けて add_nav_and_image.py --only irae-myositis・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
blog_url は公開後に実値へ。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "irae-myositis",
    "title": "ICIによる筋炎を見逃さない",
    "desc": "免疫チェックポイント阻害薬による筋炎──MGに見えても筋炎と心筋炎を疑い、1つを疑ったら3つとも調べる。頻度・時期、合併と死亡、検査の注意点、治療の柱を1枚に整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "",
    "date": "2026-10-13",
    "youtube_id": "xXp9DywlVu0",
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
