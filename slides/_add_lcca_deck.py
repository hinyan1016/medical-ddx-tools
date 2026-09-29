# -*- coding: utf-8 -*-
"""manifest.json に 晩発性皮質性小脳萎縮症（LCCA）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "lcca",
    "title": "晩発性皮質性小脳萎縮症（LCCA）の診断と臨床マネジメント",
    "subtitle": "MSA-Cとの鑑別・除外ワークアップ・指定難病（告示18）申請と集中リハビリテーション（臨床医向けエビデンス解説）",
    "description": (
        "晩発性皮質性小脳萎縮症（LCCA）の診断基準・多系統萎縮症（MSA-C）との鑑別・二次性失調症除外ワークアップ・"
        "指定難病（告示18）申請と集中リハビリテーションを解説。国内SCDの約67%を占める孤発例への体系的アプローチを全13枚のスライドで解説します。"
    ),
    "youtube_id": "YYqFdbfiswU",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/29/111318",
    "source_dir": "lcca/current/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 13,
    "tags": [
        "晩発性皮質性小脳萎縮症",
        "LCCA",
        "脊髄小脳変性症",
        "多系統萎縮症",
        "MSA-C",
        "指定難病",
        "告示18",
        "リハビリテーション",
        "脳神経内科",
        "医師向け"
    ],
    "published_date": "2026-09-29",
    "viewer_notice": "本資料は医療従事者向けの医学教育および知識整理であり、個別の診療判断に代わるものではありません。内容は2026年9月29日時点の資料に基づきます。",
    "html_deck": False,
    "infographic": True,
}


def main() -> None:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = m["decks"]
    idx = next((i for i, d in enumerate(decks) if d["slug"] == DECK["slug"]), None)
    if idx is None:
        decks.insert(0, DECK)
        print("added deck:", DECK["slug"])
    else:
        decks[idx] = DECK
        print("updated deck:", DECK["slug"])
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print("total decks:", len(decks))


if __name__ == "__main__":
    main()
