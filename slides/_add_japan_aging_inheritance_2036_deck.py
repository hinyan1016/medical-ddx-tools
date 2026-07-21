# -*- coding: utf-8 -*-
"""manifest.json に「2036年の日本、大相続時代と『消費なき相続』」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "japan-aging-inheritance-2036",
    "title": "2036年の日本、大相続時代と「消費なき相続」｜高齢化で資産・地方・格差はどう変わるか",
    "subtitle": "増えるのは高齢者の数ではなく「動いても使われないお金」",
    "description": (
        "2036年の日本で最も重い変化は、高齢者の急増ではなく現役世代の急減です。"
        "15〜64歳人口は10年で約647万人（約8.9%）減る一方、65歳以上は約147万人増え、"
        "高齢化率は29.8%から32.8%へ。家計金融資産2,386兆円（現金・預金1,126兆円、保険・年金等584兆円、"
        "株式等398兆円、投資信託165兆円）は人口減少だけでは消えず、高齢の親から"
        "すでに高齢になった子へ移ります。相続税の申告データでみると相続人の52.1%が60歳以上・"
        "被相続人の72%が80歳以上（ただし課税割合10.4%＝相続全体の約1割に限られる点に注意）。"
        "地域をまたいで動く金融資産は約125兆円、東京圏への純流入38.1兆円でシェアは36.4%から41.0%へ。"
        "流動資産は都市へ動く一方、実家・山林と管理負担は地方に残ります。受け取るのが老後不安を抱える"
        "60代であるため相続資産は消費に回りにくく、広がるのは世代間格差より「同世代内の相続格差」です。"
        "公的統計（国立社会保障・人口問題研究所／日本銀行／国税庁／内閣府）と民間試算に基づく全18スライド。"
        "一般向け。特定の金融商品の売買・投資判断・相続対策を推奨するものではありません。"
    ),
    "youtube_id": "V2_sAR7UVGo",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/21/125720",
    "source_dir": "2036年消費なき大相続/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "html_deck": True,
    "infographic": True,
    "tags": ["大相続時代", "老老相続", "高齢化社会", "人口減少", "一般向け"],
    "published_date": "2026-07-21",
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
