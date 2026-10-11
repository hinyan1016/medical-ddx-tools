# -*- coding: utf-8 -*-
"""infographics/manifest.json に 抗てんかん発作薬の作用機序と合理的多剤併用（図14点の一覧ページ）item を追加する（既存なら更新）。

公開前の下書き（2026-10-11）。ページ本体は publishing/infographics/asm-mechanism-polytherapy/（build_gallery.py の出力）。
先生の公開承認のあと、そのフォルダを medical-ddx-tools/infographics/ にコピーし、この台本を infographics/ に置いて実行する。
続けて card.webp・cards.json・infographics/index.html（build_index.py）・sw.js の ASSETS と CACHE_NAME の版上げ、
check_sw_cache.py を通す（tools 登録の6点セット）。blog_url・youtube_id は公開後に実値へ。
parkinson-genetics/current/publishing/_add_parkinson_genetics_infographic.py と同じ型。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "asm-mechanism-polytherapy",
    "title": "抗てんかん発作薬の作用機序と合理的多剤併用｜図で読むポイント",
    "desc": "Naチャネル・SV2A・α2δ・GABA・AMPA・T型Caの標的と代表薬、複数の標的をもつ薬、単剤で発作が止まる割合、相乗・相加・拮抗、組み合わせの根拠の強さ、バルプロ酸＋ラモトリギン、Na遮断薬の重ね合わせ、2剤目の考え方を14枚の図で整理（医師向け）",
    "audience": "医師向け",
    "blog_url": "",
    "date": "2026-10-11",
    "youtube_id": "gxXwoDWKvoA",
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
