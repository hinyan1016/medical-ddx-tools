# -*- coding: utf-8 -*-
"""manifest.json に 台風と病気リスク deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "typhoon-health-risks",
    "title": "台風で増える病気はあるのか？ 脳卒中・心筋梗塞から感染症、持病の悪化まで",
    "subtitle": "日本の全国入院データで脳卒中入院リスク1.049倍｜中国の研究で急性冠症候群リスク1.14倍｜観察研究であり個人の発症を保証するものではない",
    "description": (
        "台風の健康リスクは気圧だけではない。日本の全国入院データでは台風曝露後0〜6日で脳卒中入院リスクが"
        "1.049倍（脳内出血1.131倍）、中国の全国規模研究では台風曝露後0〜3日の急性冠症候群リスクが1.14倍。"
        "米国高齢者の研究では熱帯低気圧曝露後1週間で呼吸器疾患入院が14.2%増加。これらはいずれも観察研究で、"
        "個人の発症を保証するものではない。直接の危険・気象変化・避難停電・医療の中断という4つの経路を整理し、"
        "脳卒中や急性冠症候群のレッドフラッグ、避難生活で見逃せない3つの危険（深部静脈血栓症・一酸化炭素中毒・"
        "熱中症）、治療を中断させないための備えを16枚で解説。一般向け。"
    ),
    "source_dir": "台風と病気リスク/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 16,
    "tags": [
        "台風", "脳卒中", "心筋梗塞", "防災", "一酸化炭素中毒",
        "深部静脈血栓症", "片頭痛", "てんかん", "避難生活", "脳神経内科",
    ],
    "published_date": "2026-08-19",
    "viewer_notice": (
        "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。"
        "紹介した研究の多くは観察研究であり、台風が個人の発症を直接引き起こすことを証明したものではありません。"
        "危険な症状があるときは、天候にかかわらず救急要請や医療機関への相談を優先してください。"
    ),
    "html_deck": True,
    "infographic": True,
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/18/194444",
    "youtube_id": "GufP8Wb2rrw",
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
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("decks:", len(decks))


if __name__ == "__main__":
    main()
