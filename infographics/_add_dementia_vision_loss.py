# -*- coding: utf-8 -*-
"""manifest.json に 視力低下と認知症（認知症×生活習慣病シリーズ第9弾）item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "dementia-vision-loss",
    "title": "視力低下と認知症｜白内障手術で認知症は防げるのか",
    "desc": (
        "2024年、Lancet委員会は「未矯正の視力低下」を認知症の新しい危険因子に加えた（晩年期のPAF 2%）。"
        "約3,000人を7.8年追跡した米国ACT研究では、白内障手術を受けた人でその後の認知症が少なかった"
        "（HR 0.71・95%CI 0.62–0.83）。だがこれは「手術を受けられる人がもともと健康なだけ」かもしれない"
        "——研究者は同じコホートで、視力を戻さない緑内障手術を陰性対照に置いた。結果、関連は消えた"
        "（HR 1.08・0.75–1.56）。それでも「手術で認知症を防げる」ことを示したランダム化比較試験は一つもなく、"
        "メタ解析の著者自身が「RCTでさらに検証すべき」と結論している。日本の藤原京アイスタディでは、"
        "白内障手術歴は軽度認知障害とは関連したが認知症とは有意に関連しなかった。視力低下の寄与度は"
        "測り方で1.8%〜19.0%まで開き、最大の寄与は視力表では拾えないコントラスト感度の低下だった。"
        "認知症×生活習慣病シリーズ第9弾。"
    ),
    "audience": "医療者・一般",
    "blog_url": "",
    "date": "2026-08-18",
    "youtube_id": "",
    "_todo": (
        "投稿後に要更新: blog_url と youtube_id が未確定（作成日2026-08-18時点）。"
        "公開後に実値へ差し替え、add_nav_and_image.py --only dementia-vision-loss を再実行すること。"
    ),
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
