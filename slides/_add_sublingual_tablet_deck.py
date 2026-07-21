# -*- coding: utf-8 -*-
"""manifest.json に 舌下錠 deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "sublingual-tablet",
    "title": "舌下錠を飲み込んだらどうする？｜ニトロペン・シクレストとOD錠の違い",
    "subtitle": "飲み込んだ後の対応は「発作を止める薬」か「毎日続ける薬」かで正反対になる",
    "description": (
        "舌下錠（ぜっかじょう）をうっかり飲み込んでしまったとき、どうすればよいのかを"
        "添付文書・患者向医薬品ガイドの原文に沿って解説。ニトロペン舌下錠の添付文書には"
        "「本剤は舌下で溶解させ、口腔粘膜より吸収されて速やかに効果を発現するもので、"
        "内服では効果がない」と明記されています。ただし飲み込んだ後にどうするかは薬の役割で"
        "正反対で、ニトログリセリンは数分で効果がなければ追加投与が用法に組み込まれている一方、"
        "アセナピン（シクレスト）は添付文書に追加服用の指示がなく「決して2回分を一度に使用"
        "しないでください」と明記されています。名前が似ているOD錠（口腔内崩壊錠）は公式資材に"
        "「服用後に唾液を飲み込むようにしたり、水で流し込んだりしてください」とある"
        "飲み込む前提の剤形で、舌下免疫療法錠は舌下で1分間保持した後に飲み込む第三のパターン。"
        "舌下錠・OD錠・舌下免疫療法錠・普通の錠剤の比較表、溶けない・効かないときの確認点まで、"
        "全19スライドで整理しています。"
    ),
    "youtube_id": "TRDYjM8-fEw",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/21/185842",
    "source_dir": "sublingual_tablet/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": ["舌下錠", "OD錠", "ニトログリセリン", "アセナピン", "薬の飲み方"],
    "published_date": "2026-07-21",
    "html_deck": True,
    "infographic": False,
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
