# -*- coding: utf-8 -*-
"""manifest.json に 成人 周期性嘔吐症候群(CVS) deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "cyclic-vomiting-syndrome-adult",
    "title": "大人の“自家中毒”？ 成人の周期性嘔吐症候群（CVS）を脳神経内科の視点で",
    "subtitle": "小児のアセトン血性嘔吐症の“大人版”＝成人CVSは「片頭痛の親戚（脳腸相関の機能性疾患）」。Rome IV・4相・レッドフラッグ・CHS鑑別・頓挫と予防を1本で整理",
    "description": (
        "成人の周期性嘔吐症候群（CVS）を、小児の「アセトン血性嘔吐症（自家中毒）」の大人版として捉え直し、"
        "脳神経内科の視点で整理。核心は、CVSが消化管だけの病気ではなく、神経細胞の過興奮とミトコンドリア機能障害を"
        "背景とする「片頭痛の親戚＝脳腸相関の機能性神経疾患」だという点。だからこそ片頭痛予防薬アミトリプチリンが"
        "第一選択の予防薬になり、前駆期のトリプタンが発作を頓挫させる。診断はRome IVの除外診断（4相・発作間欠期は"
        "無症状が手がかり）で、後頭蓋窩腫瘍・間欠的腸閉塞・代謝内分泌・妊娠などのレッドフラッグを除外。最重要の鑑別は"
        "慢性大麻使用による大麻性嘔吐症候群（CHS・熱いシャワーで軽快・大麻中止で寛解）。治療は頓挫（早期の輸液・糖・"
        "電解質＋オンダンセトロン＋片頭痛型はトリプタン）と予防（成人はアミトリプチリン第一選択・小児はシプロヘプタジン/"
        "プロプラノロールが前面）の二本立て。ANMS/CVSA 2019ガイドライン・AGA 2024 Practice Update等、PubMed収載の"
        "一次文献に基づき脳神経内科専門医監修で全21スライドに整理。医療従事者向け。"
    ),
    "youtube_id": "K1P1P-LRyXE",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/23/142835",
    "source_dir": "adult_cvs/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 21,
    "html_deck": False,
    "infographic": False,
    "tags": ["周期性嘔吐症候群", "成人CVS", "自家中毒", "片頭痛", "脳神経内科"],
    "published_date": "2026-07-23",
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
