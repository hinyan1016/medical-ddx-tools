# -*- coding: utf-8 -*-
"""manifest.json に「レケンビ皮下注ペン承認」deck を追加・更新する。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "lecanemab-sc-pen",
    "title": "レケンビ皮下注ペン承認 ― 点滴に加えて週1回の自己注射も選択肢に",
    "subtitle": "認知症治療のハードルはどう下がるか｜「同等」と言えるのは薬物動態の類似性まで",
    "description": (
        "抗アミロイドβ抗体レカネマブの皮下注射製剤「レケンビ皮下注250mgペン」の承認を、添付文書の原文をもとに脳神経内科の勤務医向けに整理。"
        "2週間に1回の点滴に加えて、週1回の自己注射という選択肢が加わった（点滴に取って代わるものではない）。"
        "用法の要点（500mg週1回・1回にペン2本・投与開始は医療施設で医師の監督下）、通院・介護負担の変化（患者選好やコスト推計はエーザイ資金提供のモデル研究）、"
        "点滴版と「同等」と言えるのは薬物動態の類似性（AUC比1.04）までで臨床的な非劣性は検証されていないこと、"
        "自己注射になってもMRIモニタリング・禁忌の確認などの安全管理は簡略化されないこと（ApoE遺伝子検査は投与開始前に実施を考慮）、"
        "日本の実臨床ARIAデータは現時点で点滴版のものであることを、全20枚のスライドで確認します。"
    ),
    "youtube_id": "6a3LgZu8EPw",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/17/080546",
    "source_dir": "レケンビ皮下注/generated-slides/bundle/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 20,
    "tags": [
        "レカネマブ",
        "レケンビ皮下注",
        "アルツハイマー病",
        "ARIA",
        "自己注射",
        "脳神経内科",
        "医師向け",
    ],
    "published_date": "2026-09-18",
    "viewer_notice": "本資料は医療従事者・医療系学生向けの学習教材であり、個別の患者への投与判断に代わるものではありません。診療判断は必ず最新の添付文書・ガイドライン・主治医判断に従ってください。",
    # RC5 bundle は <フォルダ名>.html 形式のデッキを持たないためインタラクティブ版は出さない。
    # インフォグラフィックは infographics/lecanemab-sc-mri-schedule/ に HTML 版があるので複製しない。
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
        decks.insert(0, DECK)
        print(f"Added deck: {DECK['slug']}")

    MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Total decks in manifest: {len(decks)}")


if __name__ == "__main__":
    main()
