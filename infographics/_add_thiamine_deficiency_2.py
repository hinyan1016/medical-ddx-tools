# -*- coding: utf-8 -*-
"""manifest.json に チアミン欠乏症シリーズ第2回 item を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

ITEM = {
    "slug": "thiamine-deficiency-2-beriberi-diagnosis",
    "title": "原因不明の乳酸アシドーシスを見たら｜衝心脚気・消化器型脚気の見つけ方と、血中チアミン検査の限界",
    "desc": (
        "湿性脚気の典型的特徴はしばしば欠け、EFは低下せずむしろ過収縮を示す。衝心脚気・消化器型脚気は"
        "敗血症や急性腹症と誤認されやすい。血漿チアミンは体内のごく一部しか反映せず、全血TDPは人種差が"
        "診断名より10倍以上分散を説明する。疑ったら結果を待たずにチアミン急速静注へ踏み切る診断的治療の"
        "原則を整理。チアミン欠乏症シリーズ第2回。"
    ),
    "audience": "医療者",
    "blog_url": "",
    "date": "2026-09-09",
    "youtube_id": "",
    "_todo": (
        "投稿後に要更新: blog_url と youtube_id が未確定（作成日2026-09-09時点）。"
        "公開後に実値へ差し替え、index.htmlのnav内リンクとbuild_index.pyを再実行すること。"
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
