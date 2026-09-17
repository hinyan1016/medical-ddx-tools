# -*- coding: utf-8 -*-
"""manifest.json に「ナッツの健康効果」item を追加する（既存なら更新）。

2026-09-06 にブログ・動画を公開した際、infographic.png だけがコミットされ、
index.html（HTML版）と manifest 登録が漏れていた（ブログからのリンクが404）。2026-09-18 に登録。
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "nuts-health-benefits",
    "title": "健康にいいナッツ、どこまで食べていい？｜太らない理由と1日28gの限界線",
    "desc": (
        "高カロリーなのに体重が増えにくい3つの理由（アトウォーター係数の乖離・エネルギー補償・86件のRCTメタ解析）、"
        "普段の食事に「追加」するのと間食から「置き換える」のとで体脂肪率の変化が違うこと、"
        "効果が頭打ちになる1日約28g（手のひら一杯）の目安を、ナッツの種類別の粒数とあわせて1枚に整理。一般向け。"
    ),
    "audience": "一般",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/06/100445",
    "date": "2026-09-06",
    "youtube_id": "Vfev6X29GaA",
}


def main() -> None:
    raw = MANIFEST.read_bytes()
    crlf = b"\r\n" in raw   # 改行コードを保つ（LFで書き直すと全行差分に化ける）
    m = json.loads(raw.decode("utf-8"))
    items = m["items"]
    idx = next((i for i, it in enumerate(items) if it["slug"] == ITEM["slug"]), None)
    if idx is None:
        # 新しい順に並んでいるので、公開日（2026-09-06）より新しい item の直後に入れる
        pos = next((i for i, it in enumerate(items) if it.get("date", "") <= ITEM["date"]), len(items))
        items.insert(pos, ITEM)
        print(f"added item: {ITEM['slug']} (position {pos})")
    else:
        items[idx] = ITEM
        print("updated item:", ITEM["slug"])
    text = json.dumps(m, ensure_ascii=False, indent=2) + "\n"
    MANIFEST.write_bytes((text.replace("\n", "\r\n") if crlf else text).encode("utf-8"))
    print("total items:", len(items))


if __name__ == "__main__":
    main()
