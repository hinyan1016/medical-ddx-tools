# -*- coding: utf-8 -*-
"""manifest.json に パーキンソン病の幻覚・妄想 deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "parkinson-psychosis",
    "title": "パーキンソン病の幻覚・妄想 治療｜ドパミン系とアセチルコリン系を分けて考える",
    "subtitle": "衝動制御障害・病的賭博・パンディングは「減らす」、レビー小体型的な幻視は「足す・置き換える」。症状→系統→治療を1枚のフローで整理",
    "description": (
        "パーキンソン病の幻覚・妄想を、ドパミン系の“過剰”（衝動制御障害・病的賭博・パンディング・"
        "ドパミン調節異常症候群・妄想）とアセチルコリン系の“低下”（レビー小体型認知症的な構築された幻視）"
        "の2つの系統に分けて整理。同じ精神症状でも、前者はまず誘因薬剤を減らし、後者は抗コリン負荷を除いて"
        "コリンエステラーゼ阻害薬を足す、と第一手が正反対になります。抗精神病薬の使い分け（クエチアピン→難治は"
        "クロザピン、定型薬・リスペリドン・オランザピンは回避、ピマバンセリンは国内未承認）とDAWSの注意点まで、"
        "PubMed収載の一次文献に基づき脳神経内科専門医監修で全22スライドに整理。医療者・一般内科医向け。"
        "「ドパミン＝妄想／アセチルコリン＝幻視」は断定ではなく治療判断の“軸”として提示します。"
    ),
    "youtube_id": "71Cge3JUGNc",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/15/082947",
    "source_dir": "パーキンソン病幻覚妄想/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 22,
    "html_deck": False,
    "infographic": False,
    "tags": ["パーキンソン病", "幻覚妄想", "衝動制御障害", "レビー小体型認知症", "脳神経内科"],
    "published_date": "2026-07-15",
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
