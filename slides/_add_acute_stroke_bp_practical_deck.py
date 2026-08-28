# -*- coding: utf-8 -*-
"""manifest.json に「脳卒中急性期の降圧実務」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "acute-stroke-bp-practical",
    "title": "脳卒中急性期の降圧はどう行うか｜脳梗塞・脳出血に共通するニカルジピン持続静注の計算・上げ下げ・内服移行の臨床実務【ガイドライン2025・AHA対応】",
    "subtitle": "開始量0.5 µg/kg/分から体重×0.15 mL/時へ。増量前に尿閉・疼痛を除外、嚥下後にオーバーラップ移行",
    "description": (
        "脳卒中（脳梗塞・脳出血）急性期の降圧目標値は病型により異なりますが、第一選択となるニカルジピン持続静注の"
        "換算・増減調整や内服移行の実務は共通しています。国内添付文書の希釈換算式（0.5 µg/kg/分 ＝ 体重×0.15 mL/時）、"
        "AHA方式との違い、安全な増減プロトコル、偽高血圧（尿閉・疼痛等）の除外、嚥下機能評価後の内服移行手順まで、"
        "脳卒中治療ガイドライン2021〔改訂2025〕・AHA/ASA 2026・ATACH-2・ENCHANTED2/MT等の一次資料に基づき全18スライドで解説。"
    ),
    "youtube_id": "cd2kMzEt6HI",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/29/083033",
    "source_dir": "acute_stroke_bp_practical/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "脳卒中",
        "脳梗塞",
        "脳出血",
        "ニカルジピン",
        "ペルジピン",
        "血圧管理",
        "持続静注",
        "医師向け",
    ],
    "published_date": "2026-08-29",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診断・治療方針を示すものではありません。実際の診療判断は施設プロトコル・最新電子添文に従ってください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/acute-stroke-bp-practical/",
}


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = data["decks"]
    for i, d in enumerate(decks):
        if d.get("slug") == DECK["slug"]:
            decks[i] = DECK
            action = "更新"
            break
    else:
        decks.insert(0, DECK)
        action = "追加"
    MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print(f"{action}: {DECK['slug']}（decks {len(decks)} 件）")


if __name__ == "__main__":
    main()