# -*- coding: utf-8 -*-
"""manifest.json に プラセンタと老化（医師が採点するアンチエイジング 第11回）deck を追加する（既存なら更新）。

2026-10-07：第10回（_add_anti_aging_hrt_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-placenta/work/rc6-20261007/viewer/ に整えてある
（slide_01〜19.png＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、slides.pdf＝同じ書き出し、infographic.png＝publishing の複製）。
YouTube・ブログは未公開。公開後に実の ID と URL を下の DECK に入れて再実行し、_template/build.py --slug anti-aging-placenta を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-placenta",
    "title": "プラセンタ注射・サプリで、老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第11回）",
    "subtitle": "国が認めた使い道・更年期・皮膚・疲労・肝臓の試験・害と献血の制限・サプリと化粧品の位置づけ（一般向け）",
    "description": "プラセンタ（胎盤エキス）の注射やサプリは老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、老化予防・美容を目的にしたプラセンタは「まだ分からない（予防目的では根拠が乏しい）」。老化の予防を目的に死亡・骨折・認知症などを調べた比較試験は、調べた範囲では見つかっていません。ヒトの試験は小規模で短く、結果もそろっていません。国が認めた使い道（更年期障害・乳汁分泌不全・慢性肝疾患の肝機能改善）は、老化予防・美容とは分けて考えます。試験の読み方と、副作用・献血の制限を、全19枚のスライドで説明します。",
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "anti-aging-placenta/work/rc6-20261007/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": [
        "プラセンタ",
        "老化予防",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-07",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。「まだ分からない」は、健康な人が老化予防・美容を目的にプラセンタの注射やサプリを使うことについての判定で、国が認めた使い道（更年期障害・乳汁分泌不全・慢性肝疾患の肝機能改善）とは分けて考えます。注射には、ショックなどの副作用や理論上の感染のおそれがあり、使うと献血は最後の使用日から3か月待つ扱いです（最新の運用は日本赤十字社で確認してください）。つらい症状や肝臓の病気は、医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月7日時点の研究・公的資料に基づきます。",
    "html_deck": False,
    "infographic": True
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
        sys.exit("TBD が残っています。")
    # 公開前は youtube_id・blog_url が空のまま登録する（第10回の初回コミットと同じ。公開後に実値を入れて再実行）。
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
