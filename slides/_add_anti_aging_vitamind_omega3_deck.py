# -*- coding: utf-8 -*-
"""manifest.json に ビタミンD・魚油（オメガ3）と老化（医師が採点するアンチエイジング 第8回）deck を追加する（既存なら更新）。

2026-10-04：動画は限定公開。ブログはまだ公開前で実URLが無いため blog_url を空にして登録した（第7回の初回登録と同じ扱い）。ブログ公開後に実URLを入れて再実行する。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-vitamind-omega3",
    "title": "ビタミンDと魚油のサプリで、老化は防げる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第8回）",
    "subtitle": "大規模な試験の読み方・ビタミンD・魚油・処方薬の高用量EPA・日本の基準（一般向け）",
    "description": "ビタミンDと魚油（オメガ3）のサプリは老化を防ぐのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、ビタミンDが「効かない（条件つき）」、魚油が「まだ分からない」。「効かない」は、健康で血液中のビタミンDの濃度がおおむね足りている中高年の大規模な試験では、主な結果に差が出なかったという意味です。もともと不足している人や日本人で確かめた大規模な試験は、調べた範囲では見つかっていません。参考として、病院で処方される高用量のEPAは、対象を限れば効く可能性がありますが、まだ決着していません。大規模な試験の読み方と、やることを、全19枚のスライドで説明します。",
    "youtube_id": "EYy37LoY8pA",
    "blog_url": "",
    "source_dir": "anti-aging-vitamind-omega3/work/rc6-20261004e/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": [
        "ビタミンD",
        "魚油",
        "オメガ3",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-04",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。ビタミンDの「効かない」は、健康で血液中の濃度がおおむね足りている中高年の大規模な試験での結果で、もともと不足している人や日本人で確かめたものではありません。薬を飲んでいる人、持病のある人は、サプリを始める前に医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月4日時点の研究・公的資料に基づきます。",
    "html_deck": False,
    "infographic": True
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]) or not DECK["youtube_id"]:
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
