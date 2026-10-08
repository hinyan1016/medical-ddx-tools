# -*- coding: utf-8 -*-
"""manifest.json に コラーゲンのサプリと肌の老化（医師が採点するアンチエイジング 第13回）deck を追加する（既存なら更新）。

2026-10-09：第12回（_add_anti_aging_stem_cell_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-collagen/work/rc6-20261009b/viewer/ に整えてある
（slide_01〜14.png＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、slides.pdf＝同じ書き出し、infographic.png＝publishing の複製）。
公開前の下書き。medical-ddx-tools/slides/ に置いて実行するのは、先生の公開承認のあと。
公開後に youtube_id・blog_url・published_date を実値にして再実行し、_template/build.py --slug anti-aging-collagen を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-collagen",
    "title": "コラーゲンのサプリで、肌の老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第13回）",
    "subtitle": "肌の水分と弾力のメタ解析・健康な成人の試験・試験の質と偏り・副作用と注意（一般向け）",
    "description": "コラーゲンのサプリは肌の老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、老化予防を目的にした場合は「まだ分からない」。肌の水分は複数のメタ解析で偽薬より改善した一方、弾力は解析によって結果が分かれ、死亡・認知症・骨折などを結果にした比較試験は、調べた範囲では見つかりませんでした。試験の多くは小規模・短期で、企業の社員が著者に入る試験もあります。原料へのアレルギーの確認とあわせて、全14枚のスライドで説明します。",
    "youtube_id": "V7RHkGvn4RQ",
    "blog_url": "",
    "source_dir": "anti-aging-collagen/work/rc6-20261009b/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 14,
    "tags": [
        "コラーゲン",
        "サプリメント",
        "肌の老化",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-09",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。「まだ分からない」は、老化予防を目的にコラーゲンのサプリを使うことについての判定です。肌の水分の改善は、老化を防ぐことの証明ではありません。原料（魚・牛・鶏など）にアレルギーのある方は注意し、飲み始めて体調の変化があれば中止して相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月8日時点の研究に基づきます。",
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
