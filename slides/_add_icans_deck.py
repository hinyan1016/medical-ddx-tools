# -*- coding: utf-8 -*-
"""manifest.json に ICANS deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "icans",
    "title": "CAR-T後の意識障害、ICANSか それ以外か｜ICEスコア・ASTCT分類・除外すべき5つの病態",
    "subtitle": "ICANSは除外診断 ― CRSの先行がなければ、まず他の原因を疑う",
    "description": (
        "CAR-T細胞療法や二重特異性抗体のあとに生じる意識障害を、ICANS（免疫エフェクター細胞関連"
        "神経毒性症候群）と決めつけないための医療従事者向けスライド。ASTCT合意基準による定義と発症の"
        "時間軸（輸注後 中央値4〜6日）、グレーディングで最も誤解されやすい3つの落とし穴"
        "（ICEスコア単独では決まらない・けいれんは脳波上のみでもGrade 3・頭痛や振戦は定義から除外）、"
        "除外すべき5つの病態（敗血症性脳症・中枢神経浸潤/再発・感染性脳炎(特にHHV-6)・代謝性/薬剤性脳症・"
        "脳血管障害/PRES）、頭部MRIは典型的に正常で脳波を撮らなければ非けいれん性てんかん重積(NCSE)を"
        "見逃す点、そして夜間にコールされたときの初動5項目までを、脳神経内科医の視点から全26スライドで整理。"
    ),
    "youtube_id": "9jDMcW0RYaA",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/22/080151",
    "source_dir": "ICANS/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 26,
    "tags": ["ICANS", "CAR-T", "ASTCT", "ICEスコア", "神経毒性"],
    "published_date": "2026-07-22",
    "html_deck": True,
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
