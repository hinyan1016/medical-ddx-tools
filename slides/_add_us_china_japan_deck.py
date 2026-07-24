# -*- coding: utf-8 -*-
"""manifest.json に「対中好感度11%は世界最下位、でも最大の貿易相手は中国」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "us-china-japan",
    "title": "対中好感度11%は世界最下位、でも最大の貿易相手は中国 ― データでみる日本の「三層ねじれ」",
    "subtitle": "安全保障はアメリカ、財布は中国",
    "description": (
        "2026年、世界の好感度調査で米国と中国の評価が約20年ぶりに逆転しました（Pew Research Center調査・"
        "36か国・地域、米国36%・中国46%）。しかしそれは中国が急に好かれたからではなく、前年48%だった米国の"
        "評価が急落した結果です。日本の対中好感度は11%で調査対象37か国・地域の中で最下位、対米好感度50%との"
        "差は世界最大級の39ポイント。この対中警戒は感情論ではなく、尖閣諸島周辺で中国海警局の船が"
        "2024年に355日・2025年に357日確認され、2025年3月には92時間8分という過去最長の領海侵入が起きている"
        "という「現場の接触」に裏打ちされています。それでも2025年の日本の貿易総額は対中国が約45.5兆円で"
        "対米国の約33.3兆円を上回り、世論・安全保障・経済の向きがそろわない「三層ねじれ」を抱えています。"
        "Pew Research Center・財務省貿易統計・海上保安庁・内閣府の公表資料に基づく全17スライド。一般向け。"
        "特定の国・政党・政権への支持や批判、投資判断や渡航判断を推奨するものではありません。"
    ),
    "youtube_id": "3mSczYTVCnk",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/24/194101",
    "source_dir": "米中日関係/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "html_deck": True,
    "infographic": True,
    "tags": ["米中関係", "日中関係", "日米関係", "国際関係", "一般向け"],
    "published_date": "2026-07-24",
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
