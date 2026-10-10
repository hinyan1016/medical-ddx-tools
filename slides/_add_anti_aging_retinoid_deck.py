# -*- coding: utf-8 -*-
"""manifest.json に レチノイドの塗り薬と肌の老化（医師が採点するアンチエイジング 第14回）deck を追加する（既存なら更新）。

2026-10-10：第13回（_add_anti_aging_collagen_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-retinoid/work/rc6-20261010c/viewer/ に整えてある
（slide_01〜15.png＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、slides.pdf＝同じ書き出し、infographic.png＝publishing の複製）。
公開前の下書き。medical-ddx-tools/slides/ に置いて実行するのは、先生の公開承認のあと。
公開後に youtube_id・blog_url・published_date を実値にして再実行し、_template/build.py --slug anti-aging-retinoid を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-retinoid",
    "title": "レチノイドの塗り薬で、肌の老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第14回）",
    "subtitle": "しわ・しみへの効果のメタ解析・濃さと刺激・副作用と妊娠・国内で使える薬と化粧品（一般向け）",
    "description": "レチノイドの塗り薬は肌の老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、処方のトレチノインの塗り薬は「効く（条件つき）」。8件のランダム化比較試験をまとめた解析で、日光による肌の老化（光老化）の細かいしわも粗いしわも、有効成分を抜いた同じ塗り薬（基剤）より改善しました。一方で、試験は古く米国が中心で、刺激が出やすく、妊娠中は使いません。皮膚がんになりやすい人の試験では、皮膚がんを防ぐ効果もみられませんでした。国内でしわを効能とするトレチノインの承認薬は、調べた範囲では見つかっていません。市販のレチノール化粧品は別枠で「まだ分からない」です。全15枚のスライドで説明します。",
    "youtube_id": "FbxzkztlJwU",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/10/093024",
    "source_dir": "anti-aging-retinoid/work/rc6-20261010c/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": [
        "レチノイド",
        "トレチノイン",
        "肌の老化",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-10",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。「効く（条件つき）」は、処方のトレチノインの塗り薬による光老化のしわ・しみの見た目についての判定で、老化そのものを止める証明ではありません。妊娠中や妊娠を考えている人は、レチノイドの塗り薬を使いません。処方の塗り薬を使いたいときは、皮膚科の医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月10日時点の研究と国内の医薬品情報に基づきます。",
    "html_deck": False,
    "infographic": True
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
        sys.exit("TBD が残っています。")
    # 公開前は youtube_id・blog_url が空のまま登録する（第11回の初回コミットと同じ。公開後に実値を入れて再実行）。
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
