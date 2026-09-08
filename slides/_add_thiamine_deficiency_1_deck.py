# -*- coding: utf-8 -*-
"""manifest.json に「チアミン欠乏症シリーズ第1回」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "thiamine-deficiency-1-who-is-at-risk",
    "title": "「脚気は過去の病気」は誤りです｜緩和ケア入院の終末期がん234名の36%がチアミン欠乏。今疑うべきリスク集団を整理する【医療者向け】",
    "subtitle": "チアミン（ビタミンB1）欠乏症シリーズ第1回。アルコール以外の現代のリスク集団と、貯蔵が数週間で尽きる機序",
    "description": (
        "緩和ケア病棟へ初回入院した終末期がん患者234名のうち36%（85名）、"
        "維持血液透析患者113名の11.5%がチアミン（ビタミンB1）欠乏だったという実測データを起点に、"
        "高木兼寛・鈴木梅太郎の歴史から現代の非アルコール性リスク集団（消化管手術・減量手術後、"
        "妊娠悪阻、透析、終末期がん、TPN依存）までを整理。体内貯蔵は数十mg・数週間分しかなく、"
        "数日から数週間の嘔吐・絶食で欠乏が成立する機序と、「ブドウ糖より先にチアミン」という"
        "通説の実際のエビデンス水準まで、脳神経内科医が医療者向けに解説。チアミン欠乏症シリーズ"
        "全4回の第1回／全18スライド。"
    ),
    "youtube_id": "Ju2mLRn4aCk",
    "blog_url": "",
    "source_dir": "thiamine-deficiency-1-who-is-at-risk/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "チアミン欠乏症",
        "ビタミンB1欠乏症",
        "脚気",
        "ウェルニッケ脳症",
        "医療者向け",
    ],
    "published_date": "2026-09-08",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診断・治療方針を示すものではありません。実際の診療判断は施設プロトコル・最新のガイドラインに従ってください。",
    "html_deck": True,
}


def main() -> None:
    if not MANIFEST.exists():
        print(f"[ERR] manifest.json が見つかりません: {MANIFEST}")
        sys.exit(1)

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = data.get("decks", [])

    idx = next((i for i, d in enumerate(decks) if d.get("slug") == DECK["slug"]), None)
    if idx is not None:
        print(f"[INFO] 既存 deck を更新: slug={DECK['slug']}")
        decks[idx] = DECK
    else:
        print(f"[INFO] 新規 deck を先頭に追加: slug={DECK['slug']}")
        decks.insert(0, DECK)

    data["decks"] = decks
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] manifest.json を更新しました（全 {len(decks)} 件）")


if __name__ == "__main__":
    main()
