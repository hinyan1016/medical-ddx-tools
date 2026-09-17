# -*- coding: utf-8 -*-
"""manifest.json に「脳梗塞治療中の偽痛風」deck を追加・更新する。

slug は公開済みURL（ブログのボタン・YouTube概要欄が参照）に合わせて stroke-cppd のまま。
2026-09-17 に manifest 未登録で手置きされていたものを、2026-09-18 に正規経路へ載せ替えた。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "stroke-cppd",
    "title": "脳梗塞治療中の偽痛風：頻度・発症機序から、抗血栓薬使用中の治療と感染の見極めまで",
    "subtitle": "5.5%の頻度の読み方・結晶陽性でも除外できない化膿性関節炎・DOAC内服下の穿刺・抗炎症治療の使い分け",
    "description": (
        "脳梗塞の治療中に遭遇しやすい急性関節炎「偽痛風（急性CPP結晶性関節炎）」の診断・治療戦略を整理します。"
        "5.5%という頻度の解釈と非麻痺側の発症、結晶陽性でも化膿性関節炎を除外できない落とし穴、"
        "DOAC内服下での穿刺の可否（1,050手技の観察研究）、コルヒチン・ステロイド・NSAIDsの使い分けと国内保険適応まで、"
        "一次資料に基づいて解説します。全17枚のスライド。"
    ),
    "youtube_id": "cLdTouHZQlw",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/16/165718",
    "source_dir": "stroke-cppd-navy-rc5/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": [
        "偽痛風",
        "CPPD",
        "脳梗塞",
        "抗血栓薬",
        "化膿性関節炎",
        "脳神経内科",
        "医師向け",
    ],
    "published_date": "2026-09-17",
    "viewer_notice": "本資料は医療従事者・医療系学生向けの学習教材であり、個別の診断・治療方針を示すものではありません。診療判断は必ず最新の添付文書・ガイドライン・主治医判断に従ってください。",
    # RC5 bundle は <フォルダ名>.html 形式のデッキを持たないためインタラクティブ版は出さない。
    "html_deck": False,
    "infographic": False,
}


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = data["decks"]
    for i, d in enumerate(decks):
        if d.get("slug") == DECK["slug"]:
            decks[i] = DECK
            print(f"Updated deck: {DECK['slug']}")
            break
    else:
        # 公開日順を保つため、レケンビ（2026-09-18）の直後に入れる
        pos = next((i + 1 for i, d in enumerate(decks) if d.get("slug") == "lecanemab-sc-pen"), 0)
        decks.insert(pos, DECK)
        print(f"Added deck: {DECK['slug']} (position {pos})")

    MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Total decks in manifest: {len(decks)}")


if __name__ == "__main__":
    main()
