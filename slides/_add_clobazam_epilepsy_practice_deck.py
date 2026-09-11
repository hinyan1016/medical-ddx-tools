# -*- coding: utf-8 -*-
"""manifest.json に「抗てんかん発作薬クロバザムの臨床薬理と実践活用」deck を追加・更新する。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "clobazam-epilepsy-practice",
    "title": "抗てんかん発作薬クロバザムの臨床薬理と実践活用",
    "subtitle": "クロナゼパム・ジアゼパムとの違い・主代謝物N-CLB・CYP2C19・TDM",
    "description": (
        "抗てんかん発作薬（ASM）クロバザム（商品名：マイスタン）の臨床薬理とエビデンスを脳神経内科専門医が解説。"
        "1,4-BZD（ジアゼパム・クロナゼパム）との受容体選択性（α2選択的結合）の違いによる過鎮静・筋弛緩の軽減、"
        "主代謝物N-デスメチルクロバザム（N-CLB）の体内動態と蓄積（力価1/5・濃度5倍）、"
        "日本人の約15〜20%を占めるCYP2C19 Poor Metabolizerでの過鎮静対策、薬物相互作用（CBD・スチリペントール）、"
        "ILAEガイドラインに基づくTDM基準域と解釈、CONTAIN試験エビデンス、月経てんかん・高齢者での実践処方設計まで、"
        "全18枚のスライドで網羅的に整理します。"
    ),
    "youtube_id": "VK8ynKw3whI",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/11/180415",
    "source_dir": "clobazam-epilepsy-practice/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "クロバザム",
        "抗てんかん発作薬",
        "てんかん",
        "CYP2C19",
        "TDM",
        "脳神経内科",
        "医師向け",
    ],
    "published_date": "2026-09-11",
    "viewer_notice": "本資料は医療従事者・医療系学生向けの学習教材です。診療判断は必ず最新ガイドライン・主治医判断に従ってください。",
    "html_deck": True,
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
