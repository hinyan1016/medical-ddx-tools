# -*- coding: utf-8 -*-
"""infographics/manifest.json に 抗てんかん薬の定期検査とモニタリング item を追加する（既存なら更新）。

2026-10-22 先生指示「バッチ21の3記事を公開してください。」（過去記事の根拠修復で作り直したインフォ画像）。
ページ本体は infographics/asm-lab-monitoring/（infographic.png は medical-content/blog/reference-repair/20261004/articles/asm-lab-monitoring/infographic/generated/ の確定版の複製）。
続けて add_nav_and_image.py --no-png --only asm-lab-monitoring・build_index.py --no-thumb・sw.js の ASSETS と CACHE_NAME・check_sw_cache.py。
blog_url は既存記事のURL（本文の差し替えでURLは変わらない）。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "asm-lab-monitoring",
    "title": "抗てんかん薬の定期検査とモニタリング",
    "desc": "多くの添付文書は検査の間隔を定めていない──薬ごとの検査項目、血中濃度測定が役立つ場面、HLA・妊娠・併用薬の注意を1枚に整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2025/12/24/090816",
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
