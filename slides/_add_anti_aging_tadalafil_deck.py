# -*- coding: utf-8 -*-
"""manifest.json に 毎日タダラフィルと老化（医師が採点するアンチエイジング 第9回）deck を追加する（既存なら更新）。

2026-10-04：第8回（_add_anti_aging_vitamind_omega3_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-tadalafil/work/rc6-20261004e/viewer/ に整えてある
（slide_01〜19.png＝static-render の複製、slides.pdf＝それを1枚1ページで束ねたもの、infographic.png＝publishing の複製）。
YouTube は限定公開（4O16_n4XUek）、ブログは 2026-10-04 に公開（blog_url 反映済み）
（第7・8回の初回登録と同じ扱い）。公開後に実の ID と URL を入れて再実行し、build.py --slug anti-aging-tadalafil を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-tadalafil",
    "title": "毎日タダラフィルで、老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第9回）",
    "subtitle": "国が認めた使い道・観察研究の読み方・認知症の研究・血管の検査値・害と向かない人（一般向け）",
    "description": "毎日少量のタダラフィルは老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、健康な中高年が老化予防目的で毎日少量のタダラフィルを飲むことは「まだ分からない」。老化や、健康な人の死亡・認知症を結果にして、ヒトで確かめた比較試験は、調べた範囲では見つかっていません。「死亡が少ない」という報告は観察研究の「関連」までです。国が認めた使い道（ED〔勃起不全〕・前立腺肥大症に伴う排尿の症状・肺動脈性肺高血圧症）は、老化予防とは分けて考えます。観察研究の読み方と、害と向かない人を、全19枚のスライドで説明します。",
    "youtube_id": "4O16_n4XUek",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/04/192328",
    "source_dir": "anti-aging-tadalafil/work/rc6-20261004e/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": [
        "タダラフィル",
        "老化予防",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-04",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。「まだ分からない」は、健康な中高年が老化予防目的で毎日少量のタダラフィルを飲むことについての判定で、国が認めた使い道（病気の治療）とは分けて考えます。老化予防目的で、自己判断で飲んだり、個人輸入で手に入れたりしないでください。薬を飲んでいる人、持病のある人は、医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月4日時点の研究・公的資料に基づきます。",
    "html_deck": False,
    "infographic": True
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
        sys.exit("TBD が残っています。")
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
