# -*- coding: utf-8 -*-
"""manifest.json に 非結核性抗酸菌症（MACとNTMの違い）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "ntm-nontuberculous-mycobacteria",
    "title": "以前はMAC、今はNTM？｜非結核性抗酸菌症を名称・診断・治療・2026年の新知見で整理",
    "subtitle": "日本の診断指針2024・化学療法見解2023と一次資料に基づく医療者向け解説",
    "description": (
        "MACとNTMは新旧の呼び名ではなく、NTM（非結核性抗酸菌）は結核菌群やらい菌などを除く抗酸菌の総称で、"
        "MACはその代表的な一群です。日本での増加、気管支拡張症などのリスク、菌が出た＝病気ではない診断の考え方、"
        "診断＝即治療でもない治療開始の判断、肺MAC症の多剤併用療法、他科外来で気をつけたいエタンブトールの"
        "視神経障害とリファンピシンの相互作用、吸入アミカシン（ALIS）の新しい試験までを全15枚のスライドで整理します。"
    ),
    "youtube_id": "PTEyH1m9FY0",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/24/115541",
    "source_dir": "ntm-nontuberculous-mycobacteria/work/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": ["非結核性抗酸菌症", "NTM", "肺MAC症", "吸入アミカシン", "感染症", "医師向け"],
    "published_date": "2026-09-24",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診断・治療方針を示すものではありません。内容は2026年9月24日時点の資料に基づきます。用量や適応は日本の指針・見解と最新の添付文書で確認してください。",
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
