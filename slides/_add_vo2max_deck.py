# -*- coding: utf-8 -*-
"""manifest.json に VO2max deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "vo2max",
    "title": "VO2 maxを上げる具体的な方法｜運動ゼロから安全に伸ばす4つの柱",
    "subtitle": "有酸素・インターバル・筋トレ・回復の4つの柱と、Apple Watchの数字の正しい見方を医師が解説",
    "description": (
        "VO2 max（最大酸素摂取量＝持久力・体力の総合指標）を、運動習慣ゼロからでも安全に"
        "伸ばす方法を医師が解説。①楽な有酸素運動で土台をつくる（週3〜5回・会話できる強度）"
        "②短いインターバルを少量足す（週1回）③筋トレで支える（週2回・自重）④回復＝睡眠・"
        "栄養・鉄を軽視しない、の4つの柱に整理。有酸素とHIITの効果をメタ解析で比較し（いき"
        "なりキツいHIITは不要）、運動ゼロから始める12週間プラン、Apple WatchのVO2 max推定"
        "値の正しい見方（4週間の傾向で見る）、運動を中止して受診すべきサインまで、全21スライドで。"
    ),
    "youtube_id": "BJGPUzJZXuY",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/13/161007",
    "source_dir": "vo2max/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 21,
    "tags": ["VO2max", "最大酸素摂取量", "有酸素運動", "生活習慣"],
    "published_date": "2026-07-13",
    "html_deck": False,
    "infographic": False,
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
