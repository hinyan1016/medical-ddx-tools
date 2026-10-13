# -*- coding: utf-8 -*-
"""infographics/manifest.json に アンチエイジング18の方法ランキング（医師が採点するアンチエイジング 第16回・最終回）item を追加する（既存なら更新）。

2026-10-13：ページ本体は infographics/anti-aging-ranking/（infographic.png は
medical-content/youtube-slides/anti-aging-ranking/current/publishing/infographic.png の複製）。
続けて add_nav_and_image.py --no-png --only anti-aging-ranking・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
公開前は blog_url・youtube_id を空で登録する。公開後に実値を入れて再実行する。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "anti-aging-ranking",
    "title": "アンチエイジング18の方法、ランキング発表",
    "desc": "医師が採点した18の方法の順位。「効く」と言えたのは4つだけ。老化予防の目的でおすすめできない3つは順位なし",
    "audience": "一般向け",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/13/215843",
    "date": "2026-10-13",
    "youtube_id": "kqNCbV7dudo",
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
