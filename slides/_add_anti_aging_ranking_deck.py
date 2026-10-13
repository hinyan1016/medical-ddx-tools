# -*- coding: utf-8 -*-
"""manifest.json に アンチエイジング18の方法ランキング（医師が採点するアンチエイジング 第16回・最終回）deck を追加する（既存なら更新）。

2026-10-13：第15回（_add_anti_aging_gh_dhea_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-ranking/work/rc6-20261013n/viewer/ に整えてある
（slide_01〜15.png・slides.pdf＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、infographic.png＝publishing の複製）。
公開前は youtube_id・blog_url を空で登録する。公開後に実値を入れて再実行し、_template/build.py --slug anti-aging-ranking を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-ranking",
    "title": "アンチエイジング18の方法を採点してランキング発表（医師が採点するアンチエイジング 第16回・最終回）",
    "subtitle": "「効く」と言えたのは4つだけ。順位表と、まず始めること（一般向け）",
    "description": "アンチエイジングの18の方法を、4つの物差しで採点してランキングにしました。「効く」と言えたのは、地中海食（条件つき）・筋トレ・日焼け止め・処方のトレチノインの塗り薬（条件つき）の4つです。サプリ・薬・注射・点滴などで体に補う12の方法は、どれも「効く」には届きませんでした。老化予防の目的では医師としておすすめできない3つ（成長ホルモンの注射・ビタミンDのサプリ・ホルモン補充療法）は、順位をつけていません。順位は、根拠の強さを最優先に、効果、安全性の順で並べました。費用・手間は順位に使っていません。このスライドのために新しく論文を調べ直してはいません。全15枚のスライドで説明します。",
    "youtube_id": "kqNCbV7dudo",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/13/215843",
    "source_dir": "anti-aging-ranking/current/publishing/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": [
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "ランキング",
        "一般向け"
    ],
    "published_date": "2026-10-13",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。順位は、根拠の強さを最優先に、効果、安全性の順で並べたもので、費用・手間は順位に使っていません。老化予防の目的では医師としておすすめできない3つは、順位をつけていません。「効く」と言えた4つも、老化を止める証明ではありません。病気の治療で使っている薬は、自己判断でやめないでください。このスライドのために新しく論文を調べ直してはいません。",
    "html_deck": False,
    "infographic": True
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
