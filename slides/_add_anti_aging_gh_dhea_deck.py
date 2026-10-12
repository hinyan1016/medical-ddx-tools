# -*- coding: utf-8 -*-
"""manifest.json に 成長ホルモンとDHEAと老化（医師が採点するアンチエイジング 第15回）deck を追加する（既存なら更新）。

2026-10-12：第14回（_add_anti_aging_retinoid_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-gh-dhea/work/rc6-20261012a/viewer/ に整えてある
（slide_01〜15.png・slides.pdf＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、infographic.png＝publishing の複製）。
公開前は youtube_id・blog_url を空で登録する。公開後に実値を入れて再実行し、_template/build.py --slug anti-aging-gh-dhea を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-gh-dhea",
    "title": "成長ホルモンとDHEAで、老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第15回）",
    "subtitle": "体の組成と筋力・副作用・長い期間の安全性・国内の扱いと個人輸入（一般向け）",
    "description": "成長ホルモンとDHEAで老化は防げるのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。健康な人が老化予防のために使う場合、成長ホルモンの注射は「効かない」、DHEAは「まだ分からない」と判定しました。成長ホルモンは、脂肪が減り脂肪以外の重さが増えますが、筋力の改善は確かめられず、むくみ・関節の痛み・血糖の異常が増えました。DHEAは、2年の試験で体の組成・体力・筋力に意味のある改善がなく、大きな副作用もありませんでしたが、調べた試験は最長2年までで、それより長い安全性は分かっていません。海外の製品の個人輸入には、国の確認が要ります。全15枚のスライドで説明します。",
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "anti-aging-gh-dhea/work/rc6-20261012a/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": [
        "成長ホルモン",
        "DHEA",
        "ホルモン補充",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-12",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。判定は、健康な人が老化予防を目的に使う場合のものです。病気の治療として国が認めた使い方は、採点の外に置いています。体の組成や検査値が変わることは、老化を止める証明ではありません。がんのある人は成長ホルモンの注射薬を使えません。海外の製品を個人で輸入するときは、国の確認が要ります。使うかどうか迷うときは、担当の医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月12日時点の研究と国内の医薬品情報に基づきます。",
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
