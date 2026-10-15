# -*- coding: utf-8 -*-
"""infographics/manifest.json に 低血糖脳症の画像と予後（医師向け）item を追加する（既存なら更新）。

2026-10-16 先生指示「ブログは公開、Youtubeは限定公開」。
ページ本体は infographics/hypoglycemic-encephalopathy/（infographic.png は medical-content/youtube-slides/hypoglycemic-encephalopathy/current/publishing/infographic.png の複製）。
続けて add_nav_and_image.py --no-png --only hypoglycemic-encephalopathy・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
blog_url は公開後に実値へ。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "hypoglycemic-encephalopathy",
    "title": "低血糖脳症の画像と予後",
    "desc": "ブドウ糖で意識が戻らないとき──片麻痺でも、まず血糖を測り、予後は画像と経過を合わせて考える。血糖の目安、MRIの所見と経過、注意点、初期対応を1枚に整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "",
    "date": "2026-10-16",
    "youtube_id": "kp94SIZhoME",
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
