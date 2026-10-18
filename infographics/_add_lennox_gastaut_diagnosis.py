# -*- coding: utf-8 -*-
"""infographics/manifest.json に レノックス・ガストー症候群の診断（医師向け）item を追加する（既存なら更新）。

2026-10-18 先生指示「ブログとYouTubeは公開作業をすすめてください」。
ページ本体は infographics/lennox-gastaut-diagnosis/（infographic.png は medical-content/youtube-slides/lennox-gastaut-diagnosis/current/publishing/infographic.png の複製）。
続けて add_nav_and_image.py --no-png --only lennox-gastaut-diagnosis・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
blog_url は公開後に実値へ。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "lennox-gastaut-diagnosis",
    "title": "レノックス・ガストー症候群の診断",
    "desc": "ILAE 2022と指定難病の基準から──強直発作と2つの脳波所見を確かめ、成人では睡眠を含むビデオ脳波で確かめる。必須項目、指定難病との違い、注意点、見分ける病気、原因の調べ方を1枚に整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "",
    "date": "2026-10-18",
    "youtube_id": "uO4F4mw6W4g",
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
