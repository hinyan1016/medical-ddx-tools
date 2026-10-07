# -*- coding: utf-8 -*-
"""manifest.json に 幹細胞・エクソソームと老化（医師が採点するアンチエイジング 第12回）deck を追加する（既存なら更新）。

2026-10-08：第11回（_add_anti_aging_placenta_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-stem-cell/work/rc6-20261008g/viewer/ に整えてある
（slide_01〜19.png＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、slides.pdf＝同じ書き出し、infographic.png＝publishing の複製）。
YouTube・ブログは未公開。公開後に実の ID と URL を下の DECK に入れて再実行し、_template/build.py --slug anti-aging-stem-cell を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-stem-cell",
    "title": "幹細胞点滴・エクソソームで、老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第12回）",
    "subtitle": "国の位置づけ・「届け出」と「承認」の違い・フレイルと肌の試験・管理された試験の内と外・国内の事案（一般向け）",
    "description": "幹細胞の点滴・注射やエクソソーム・培養上清は老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、老化予防・美容を目的にした場合は「まだ分からない」。健康な人が老化予防目的で使い、死亡や寿命などを調べたランダム化比較試験は、調べた範囲では見つかっていません。ヒトの比較試験は、フレイルと診断された高齢者への点滴と、顔の皮膚の小さな試験が中心です。管理された試験の外では重い害の報告があり、国内では自分の脂肪から取った幹細胞の治療（慢性の痛みが目的）の投与中に亡くなる事案がありました（死因は調査中）。「国に届け出た」と「国が承認した」の違いとあわせて、全19枚のスライドで説明します。",
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "anti-aging-stem-cell/work/rc6-20261008g/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": [
        "幹細胞",
        "エクソソーム",
        "老化予防",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-08",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。「まだ分からない」は、健康な人が老化予防・美容を目的に、自費で幹細胞の点滴・注射やエクソソーム・培養上清を使うことについての判定で、国が承認した再生医療等製品（特定の病気の治療）とは分けて考えます。医療機関が国に計画を出していることは、国が効果を認めたという意味ではありません。点滴や注射のあとに、発熱・息苦しさ・皮膚の痛みや色の変化・しこりなどが出たら、すぐに医療機関を受診してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月8日時点の研究・公的資料に基づきます。",
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
