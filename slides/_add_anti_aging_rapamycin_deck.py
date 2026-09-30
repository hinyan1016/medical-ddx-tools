# -*- coding: utf-8 -*-
"""manifest.json に ラパマイシンと老化（医師が採点するアンチエイジング 第4回）deck を追加する（既存なら更新）。

2026-09-30 公開：youtube_id（10/1 0:00 まで限定公開）・blog_url・published_date を記入。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-rapamycin",
    "title": "ラパマイシンは、老化を遅らせる薬？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第4回）",
    "subtitle": "マウスと人の研究・何を測った試験か・似た別の薬の試験・個人輸入と自己判断（一般向け）",
    "description": (
        "ラパマイシンは老化を遅らせる薬なのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は「まだ分からない」。"
        "マウスでは寿命が延びましたが、人で老化を遅らせると確かめた研究は見つかりませんでした。"
        "人の試験が何を測ったのか、似た別の薬の試験との違い、個人輸入と自己判断の危うさを、全17枚のスライドで説明します。"
    ),
    "youtube_id": "-3U59qtPgCA",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/30/112824",
    "source_dir": "anti-aging-rapamycin/work/rc6-20260930b/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": ["ラパマイシン", "老化", "アンチエイジング", "医師が採点するアンチエイジング", "一般向け"],
    "published_date": "2026-09-30",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。薬を飲む・やめるときは、担当の医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年9月30日時点の研究・公的資料に基づきます。",
    "html_deck": False,
    "infographic": True,
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
        sys.exit("TBD が残っています。公開後の実値を入れてから実行してください。")
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
