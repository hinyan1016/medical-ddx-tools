# -*- coding: utf-8 -*-
"""manifest.json に 地中海食・ビーガンと老化（医師が採点するアンチエイジング 第7回）deck を追加する（既存なら更新）。

2026-10-02：動画は限定公開・ブログは下書き（先生指示「第７回もブログの下書き投稿、Youtubeの限定公開をお願いします。」）で blog_url を空にして登録。2026-10-03 先生指示でブログ・動画を公開し、実URLを入れて再実行した。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "anti-aging-mediterranean-vegan",
    "title": "地中海食とビーガンで、老化は遅れる？ 医師が4つの物差しで採点（医師が採点するアンチエイジング 第7回）",
    "subtitle": "地中海食の試験・論文の取り下げと出し直し・ビーガンの研究・ビタミンB12・日本人の取り入れ方（一般向け）",
    "description": "地中海食やビーガンは老化を遅らせるのかを、根拠の強さ・効果の大きさ・安全性・費用と手間の4つの物差しで採点します。判定は、地中海食が「効く（条件つき）」、ビーガンが「まだ分からない」。地中海食は、危険の高い人の試験で心筋梗塞・脳卒中などを合わせた件数が約3割少なくなりましたが、全体の死亡は減っていません。ビーガンで足りなくなる栄養、日本人はどう取り入れるかを、全18枚のスライドで説明します。",
    "youtube_id": "2DS40EXawm4",
    "blog_url": "",
    "source_dir": "anti-aging-mediterranean-vegan/work/rc6-20261002d/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "地中海食",
        "ビーガン",
        "アンチエイジング",
        "医師が採点するアンチエイジング",
        "一般向け"
    ],
    "published_date": "2026-10-02",
    "viewer_notice": "一般向けの医学情報です。個別の診療判断に代わるものではありません。ビーガンにする場合はビタミンB12を必ず補い、高齢の人、妊娠中・授乳中の人、子どもは、始める前に医師や管理栄養士に相談してください。持病のある人は、食事を大きく変える前に担当の医師に相談してください。採点はこのチャンネルの物差しによるもので、診療ガイドラインではありません。内容は2026年10月1日時点の研究・公的資料に基づきます。",
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
