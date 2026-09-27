# -*- coding: utf-8 -*-
"""manifest.json に NMN（医師が採点するアンチエイジング 第1回）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-nmn",
    "title": "NMNで若返る？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第1回）",
    "subtitle": "ヒトの試験で分かったこと・分からないこと・広告の読み方・今日からやること（一般向け）",
    "description": (
        "若返りをうたうサプリの成分NMNについて、ヒトの試験で分かったことと、まだ分からないことを分けて、"
        "根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は「まだ分からない」。"
        "血液中のNAD+が増えることと、病気が減る・長生きできることは別の話であることを、全15枚のスライドで説明します。"
    ),
    "youtube_id": "RQ3NsoeIp0A",
    "blog_url": "",
    "source_dir": "anti-aging-nmn/work/rc6-20260928l/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": ["NMN", "アンチエイジング", "サプリメント", "NAD+", "医師が採点するアンチエイジング", "一般向け"],
    "published_date": "2026-09-28",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。治療中の方・薬を飲んでいる方は、担当の医師や薬剤師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年9月27日時点の研究・公的資料に基づきます。",
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
