# -*- coding: utf-8 -*-
"""manifest.json に「先発薬の追加負担【2026年版】」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "brand-drug-copay-2026",
    "title": "いつもの薬が高くなった？ 先発薬の追加負担と、対象外になるケース【2026年版】",
    "subtitle": "2026年6月改定で「差額の2分の1」へ引き上げ｜選定療養の仕組みと3つの対象外ケース",
    "description": (
        "2026年6月1日施行の長期収載品（後発医薬品のある先発医薬品）の選定療養改定について、"
        "厚生労働省告示および通知に基づき解説。先発医薬品を選んだ場合の特別料金（保険給付外・課税）が"
        "後発医薬品最高価格との価格差の4分の1から「2分の1相当」へ引き上げられた背景と正確な計算式、"
        "30日分処方での具体例、そして追加負担がかからない「3つの対象外ケース」（医療上の必要性・"
        "薬局の在庫流通事情・制度上の区分）、不安な場合の相談手順まで、全13スライドで整理しています。"
    ),
    "youtube_id": "nLN2rVbUe44",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/09/06/124736",
    "source_dir": "先発薬追加負担2026/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 13,
    "tags": ["先発医薬品", "ジェネリック", "選定療養", "長期収載品", "医療費"],
    "published_date": "2026-09-06",
    "viewer_notice": "本資料は医療保険制度および薬事情報に関する客観的な制度解説です。個別の処方や服薬変更については主治医・薬剤師にご相談ください。",
    "html_deck": True,
    "infographic": False,
}

def main() -> None:
    if not MANIFEST.exists():
        print(f"[ERR] manifest.json が見つかりません: {MANIFEST}")
        sys.exit(1)

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = data.get("decks", [])

    idx = next((i for i, d in enumerate(decks) if d.get("slug") == DECK["slug"]), None)
    if idx is not None:
        print(f"[INFO] 既存 deck を更新: slug={DECK['slug']}")
        decks[idx] = DECK
    else:
        print(f"[INFO] 新規 deck を先頭に追加: slug={DECK['slug']}")
        decks.insert(0, DECK)

    data["decks"] = decks
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(f"[OK] manifest.json 更新完了 (total={len(decks)})")

if __name__ == "__main__":
    main()
