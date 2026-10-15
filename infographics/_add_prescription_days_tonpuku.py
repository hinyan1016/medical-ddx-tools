# -*- coding: utf-8 -*-
"""infographics/manifest.json に 処方日数の上限と頓服の回数（医師・薬剤師向け）item を追加する（既存なら更新）。

2026-10-16 先生指示「新しいインフォグラフィックの画像をCodexで作成していれてください。」
ページ本体は infographics/prescription-days-tonpuku/（infographic.png は medical-content/youtube-slides/prescription-days-tonpuku/current/publishing/infographic.png の複製）。
続けて add_nav_and_image.py --no-png --only prescription-days-tonpuku・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
動画は作らない記事なので youtube_id は持たない。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "prescription-days-tonpuku",
    "title": "処方日数の上限と頓服の回数",
    "desc": "処方日数は予見できる必要期間で決め、上限があるのは告示で定められた薬だけ。14日・30日・90日の上限、30日を超えるときの要件、分割指示とリフィル、頓服の数え方、処方箋の使用期間を1枚に整理（医師・薬剤師向け）",
    "audience": "医療従事者向け",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2025/04/26/092856",
    "date": "2026-10-16",
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
