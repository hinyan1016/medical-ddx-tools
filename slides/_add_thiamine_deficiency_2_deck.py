# -*- coding: utf-8 -*-
"""manifest.json に チアミン欠乏症シリーズ第2回 deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "thiamine-deficiency-2-beriberi-diagnosis",
    "title": "原因不明の乳酸アシドーシスを見たら｜衝心脚気・消化器型脚気の見つけ方と、血中チアミン検査の限界",
    "subtitle": "チアミン（ビタミンB1）欠乏症シリーズ第2回。教科書像から外れる脚気の見つけ方と、診断的治療の判断",
    "description": (
        "湿性脚気の典型的特徴（高心拍出量・低体血管抵抗）は多くの患者で欠けており、心エコーのEFは低下せず"
        "むしろ過収縮を示すことがある。劇症型の衝心脚気は難治性ショックと乳酸アシドーシスをきたし、"
        "消化器型脚気は急性腹症や腸間膜虚血と誤認されて開腹手術に至ることもある。血中チアミン検査は"
        "血漿中濃度が体内総量のごく一部しか反映せず、人種による分散も大きく、結果判明にも時間がかかるため、"
        "疑った時点で結果を待たずにチアミン急速静注の診断的治療へ踏み切ることが救命の鍵になる。"
        "PubMed収載の一次文献に基づき脳神経内科専門医監修で全20スライドに整理。"
        "チアミン欠乏症シリーズ全4回の第2回／医療従事者向け。"
    ),
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "thiamine-deficiency-2-beriberi-diagnosis/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 20,
    "tags": ["チアミン欠乏症", "ビタミンB1欠乏症", "脚気", "衝心脚気", "医療者向け"],
    "published_date": "2026-09-09",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診断・治療方針を示すものではありません。実際の診療判断は施設プロトコル・最新のガイドラインに従ってください。",
    "html_deck": True,
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
