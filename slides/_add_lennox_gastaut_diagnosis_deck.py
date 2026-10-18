# -*- coding: utf-8 -*-
"""manifest.json に レノックス・ガストー症候群の診断（医師向け）deck を追加する（既存なら更新）。

2026-10-18：_add_hypoglycemic_encephalopathy_deck.py と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/lennox-gastaut-diagnosis/work/rc6-20261018d/viewer/ に整えてある
（slide_01〜20.png・slides.pdf＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、infographic.png＝publishing の複製）。
9・10枚目の脳波は CC BY 4.0 の総説の図（Alcala-Zermeno 2025・Fig.16A/19A を切り抜き縮小。出典をスライドのフッターに表示）。
先生指示「ブログとYouTubeは公開作業をすすめてください」。動画 uO4F4mw6W4g。
blog_url は公開後に実値を入れて再実行し、_template/build.py --slug lennox-gastaut-diagnosis を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "lennox-gastaut-diagnosis",
    "title": "レノックス・ガストー症候群の診断：ILAE 2022と指定難病の基準、成人で見逃さないための睡眠脳波（医師向け）",
    "subtitle": "ILAE 2022の必須項目・指定難病144との違い・最初はそろわない・脳波で確かめること（論文の脳波図）・成人での見え方・鑑別と原因検索（医師向け）",
    "description": "レノックス・ガストー症候群（LGS）の診断を、脳神経内科医向けに整理します。ILAE 2022では、強直発作を含む2種類以上の発作、2.5 Hz未満の全般性遅棘徐波、睡眠中のGPFA、18歳未満の発症が必須で、脳波の2項目は以前の脳波の記録でも構いません。指定難病144の基準は精神発達遅滞をすべての区分で求め、ProbableとPossibleには強直発作がなくても当てはまる組み合わせがあります。成人では典型的な遅棘徐波が見られないことが多いので、睡眠を含むビデオ脳波で確かめます。遅棘徐波とGPFAの実際の脳波（CC BY 4.0 の論文図）も紹介します。全20枚のスライドで説明します。",
    "youtube_id": "uO4F4mw6W4g",
    "blog_url": "",
    "source_dir": "lennox-gastaut-diagnosis/work/rc6-20261018d/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 20,
    "tags": [
        "レノックス・ガストー症候群",
        "LGS",
        "てんかん",
        "脳波",
        "脳神経内科",
        "医師向け"
    ],
    "published_date": "2026-10-18",
    "viewer_notice": "医師向けの医学情報です。個々の患者さんの診断や治療方針は、担当の医師の判断によります。根拠の多くは専門家意見・総説・少人数の研究です（スライドの注記と記事の参考文献をご覧ください）。9・10枚目の脳波は、CC BY 4.0 の総説（Alcala-Zermeno 2025）の図のパネルAを切り抜いて縮小したものです。内容は2026年10月17日時点の資料に基づきます。",
    "html_deck": False,
    "infographic": True
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
