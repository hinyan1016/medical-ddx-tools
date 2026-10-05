# -*- coding: utf-8 -*-
"""manifest.json に 女性のホルモン補充療法と老化（医師が採点するアンチエイジング 第10回）deck を追加する（既存なら更新）。

2026-10-06：第9回（_add_anti_aging_tadalafil_deck.py）と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/anti-aging-hrt/work/rc6-20261006/viewer/ に整えてある
（slide_01〜18.png＝static-render の複製、slides.pdf＝それを1枚1ページで束ねたもの、infographic.png＝publishing の複製）。
YouTube は限定公開（woYOwAXPLlI）、ブログは 2026-10-06 に公開（blog_url 反映済み）。
公開後に実の ID と URL を下の DECK に入れて再実行し、build.py --slug anti-aging-hrt を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-hrt",
    "title": "女性のホルモン補充療法で、老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第10回）",
    "subtitle": "国が認めた使い道・WHI試験・開始時期と認知症・皮膚の研究・害と向かない人（一般向け）",
    "description": "女性のホルモン補充療法は老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、閉経後の女性が老化予防目的でホルモン補充療法を使うことは「勧められない」。大規模な比較試験（WHI）は慢性病の予防を支持せず、開始時期で分けた解析や非盲検の試験にある有利な結果も、確実性は高くありません。老化を結果にしたヒトの比較試験は、調べた範囲では見つかっていません。国が認めた使い道（更年期の症状・閉経後骨粗鬆症）は、老化予防とは分けて考えます。大規模試験の読み方と、害と向かない人を、全18枚のスライドで説明します。",
    "youtube_id": "woYOwAXPLlI",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/06/082833",
    "source_dir": "anti-aging-hrt/work/rc6-20261006/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "ホルモン補充療法",
        "老化予防",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-06",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。「勧められない」は、閉経後の女性が老化予防目的でホルモン補充療法を使うことについての判定で、国が認めた使い道（更年期の症状・閉経後骨粗鬆症）とは分けて考えます。老化予防目的で、自己判断で使ったり、個人輸入で手に入れたりしないでください。すでに使っている人は、やめる前も続ける前も、自己判断せず主治医に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月6日時点の研究・公的資料に基づきます。",
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
