# -*- coding: utf-8 -*-
"""manifest.json に メトホルミンと老化（医師が採点するアンチエイジング 第5回）deck を追加する（既存なら更新）。

2026-10-01 公開：youtube_id（10/2 0:00 まで限定公開）・blog_url・published_date を記入。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-metformin",
    "title": "メトホルミンは、老化を遅らせる薬？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第5回）",
    "subtitle": "観察研究・人の大きな試験・運動との相性・飲む前の注意（一般向け）",
    "description": (
        "糖尿病の薬メトホルミンは老化を遅らせる薬なのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は「まだ分からない」。"
        "糖尿病の手前の人を約21年追った大きな試験では、糖尿病は減りましたが、糖尿病以外の病気と死亡は減りませんでした。"
        "観察研究の読み方、運動の効果を弱めるかもしれない試験、飲む前の注意を、全18枚のスライドで説明します。"
    ),
    "youtube_id": "z3KCpwNT_nA",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/01/035301",
    "source_dir": "anti-aging-metformin/work/rc6-20261001b/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": ["メトホルミン", "老化", "アンチエイジング", "医師が採点するアンチエイジング", "一般向け"],
    "published_date": "2026-10-01",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。糖尿病の治療で薬を飲んでいる人は、自分でやめずに担当の医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月1日時点の研究・公的資料に基づきます。",
    "html_deck": False,
    "infographic": True,
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
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
