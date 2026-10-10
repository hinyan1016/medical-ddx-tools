# -*- coding: utf-8 -*-
"""manifest.json に パーキンソン病と遺伝子異常（医師向け）deck を追加する（既存なら更新）。

2026-10-10：アンチエイジング第14回（_add_anti_aging_retinoid_deck.py）と同じ型。スライド・PDFは
medical-content/youtube-slides/parkinson-genetics/work/rc6-20261010c/viewer/generated/ に整えてある
（slide_01〜19.png＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、slides.pdf＝同じ書き出し）。
公開前の下書き。medical-ddx-tools/slides/ に置いて実行するのは、先生の公開承認のあと。
公開後に youtube_id・blog_url・published_date を実値にして実行し、_template/build.py --slug parkinson-genetics を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "parkinson-genetics",
    "title": "パーキンソン病と遺伝子異常｜GBA1・LRRK2・PRKNの臨床像、遺伝学的検査、遺伝子標的治療の現状【医師向け】",
    "subtitle": "遺伝的構造・発症年齢と遺伝形式・3つの経路・検査で見つかる割合・日本人のデータ・SAAとDBS・検査の考え方・治療開発（医師向け）",
    "description": "パーキンソン病と遺伝子異常を、医師向けに図で整理します。北米で8301人を調べた研究では12.9%で変異が見つかり、最も多いのはGBA1でした（白人中心のデータ）。GBA1は重症型ほどリスクが高く、認知症の危険も高いと報告されています。LRRK2 G2019Sを受け継いでも高齢で全員が発症するわけではなく、日本人ではLRRK2の病的変異はまれで、G2385Rが発症と関連します。PRKNは日本人の患者から発見された遺伝子で、若年発症ほど見つかりやすい遺伝子です。髄液SAAの陽性率は遺伝型で異なり、視床下核DBSの後はGBA1で認知機能の低下に注意が必要です。調べた範囲では、遺伝子型に合わせて承認された治療はまだありません。全19枚のスライドで説明します。",
    "youtube_id": "owAAzGe1M7Q",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/11/025722",
    "source_dir": "parkinson-genetics/work/rc6-20261010c/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": ["パーキンソン病", "遺伝子", "GBA1", "LRRK2", "PRKN", "遺伝学的検査", "脳神経内科", "医師向け"],
    "published_date": "2026-10-11",
    "viewer_notice": "医師向けの情報整理です。個々の診療の判断に代わるものではありません。検査で見つかる割合などの数字の多くは白人中心のデータで、日本人にそのまま当てはめることはできません。遺伝学的検査は、説明と同意、遺伝カウンセリングとともに行います。内容は2026年10月10日時点の論文・試験登録・公的資料に基づきます。図のうち4点は総説の図（CC BY 4.0）を日本語化して改変したものです。",
    "html_deck": False,
    "infographic": False
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
        sys.exit("TBD が残っています（公開後に実値を入れてから実行する）。")
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
