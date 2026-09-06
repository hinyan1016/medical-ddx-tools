# -*- coding: utf-8 -*-
"""manifest.json に 帯状疱疹ワクチンと認知症 deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "shingles-vaccine-dementia",
    "title": "帯状疱疹ワクチンで認知症も減る？ 最新研究で分かったこと・まだ言えないこと",
    "subtitle": "生ワクチンの自然実験で認知症診断が相対約20%減｜組換えワクチンは観察研究のみ｜無作為化試験の結果は2029〜2030年以降",
    "description": (
        "帯状疱疹ワクチンを受けた人に認知症の診断が少ないという研究から、どこまで言えるのかを脳神経内科医が整理。"
        "ウェールズ・オーストラリア・カナダの自然実験（いずれも生ワクチン）、アメリカの組換えワクチン観察研究、"
        "相対と絶対の数字の読み方（100人中約3.5人少ない／7年間）、「健康な人ほど打つ」「診断が遅れただけ」"
        "「先に亡くなった人」という別の説明、進行中の無作為化試験まで、「確立していること」「分かってきたこと」"
        "「まだ言えないこと」の3段階で18枚にまとめた。一般向け。"
    ),
    "youtube_id": "ihG-WRWm0jE",
    "blog_url": "",
    "source_dir": "帯状疱疹ワクチンと認知症/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "帯状疱疹ワクチン", "認知症", "認知症予防", "シングリックス", "組換えワクチン",
        "生ワクチン", "自然実験", "定期接種", "脳神経内科", "一般向け",
    ],
    "published_date": "2026-09-07",
    "viewer_notice": (
        "本資料は一般向けの医療情報であり、個別の診断・治療に代わるものではありません。"
        "紹介した研究は観察研究・自然実験であり、ワクチンが認知症を防ぐことを証明したものではありません。"
        "接種についてはかかりつけの医師と自治体にご相談ください。"
    ),
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
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("decks:", len(decks))


if __name__ == "__main__":
    main()
