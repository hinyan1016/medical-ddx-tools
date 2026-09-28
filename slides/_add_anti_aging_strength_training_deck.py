# -*- coding: utf-8 -*-
"""manifest.json に 筋トレと寿命（医師が採点するアンチエイジング 第2回）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-strength-training",
    "title": "筋トレで長生きできる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第2回）",
    "subtitle": "長生きとの関係・どれくらいやるか・ヒトの試験で確かめたこと・始める前の注意（一般向け）",
    "description": (
        "筋トレで長生きできるのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は「効く」。"
        "筋力と体の動きが良くなることは試験で確かめられ、長生きは観察研究の関連までです。"
        "目安は週2〜3日・合計30〜60分で、多くやるほど良いわけではないことを、全14枚のスライドで説明します。"
    ),
    "youtube_id": "L563GJ-bhrA",
    "blog_url": "",
    "source_dir": "anti-aging-strength-training/work/rc6-20260928c/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 14,
    "tags": ["筋トレ", "アンチエイジング", "健康長寿", "運動", "医師が採点するアンチエイジング", "一般向け"],
    "published_date": "2026-09-28",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。血圧がかなり高い方、糖尿病の合併症がある方、膝や腰が痛む方、持病で治療中の方は、始める前に担当の医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年9月28日時点の研究・公的資料に基づきます。",
    "html_deck": False,
    "infographic": True,
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
