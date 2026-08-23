# -*- coding: utf-8 -*-
"""manifest.json に 脳梗塞急性期の降圧 item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "acute-ischemic-stroke-bp",
    "title": "脳梗塞急性期の血圧はどこまで下げるか｜再灌流療法の有無で変わる降圧の判断",
    "desc": (
        "脳梗塞急性期の血圧管理は「下げる／下げない」ではなく、再灌流療法を行うのか、行ったのかで判断が分かれる。"
        "再灌流療法を行わない場合は原則として降圧せず、収縮期220または拡張期120を超える持続例で慎重に考慮する"
        "（推奨度D・エビデンスレベル高。CATIS・SCASTとも転帰を改善しなかった）。"
        "rt-PA静注療法では投与前185/110未満、投与後24時間は180/105以下。血栓回収療法後は速やかに180以下へ。"
        "ただし回収中・回収後に140以下へ下げることは推奨度E（行わないよう勧められる）で、"
        "ENCHANTED2/MT・OPTIMAL-BP・BEST-II・BP-TARGETのいずれも利益を示せなかった。"
        "内服は神経症状が安定していれば発症24時間以降に再開を考慮してよい（COSSACS・ENOS）。"
        "脳卒中治療ガイドライン2021〔改訂2025〕およびAHA/ASA 2026に基づき、判断フロー1枚に整理した医療従事者向けの図。"
    ),
    "audience": "医療従事者向け",
    "blog_url": "",
    "date": "2026-08-23",
    "youtube_id": "",
    "_todo": (
        "公開後に要更新: blog_url と youtube_id が未確定（Phase F 未実施）。"
        "公開後に実値へ差し替え、add_nav_and_image.py --only acute-ischemic-stroke-bp --no-png と "
        "build_index.py --no-thumb を再実行すること。"
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
