# -*- coding: utf-8 -*-
"""manifest.json に「猫背改善シリーズ第1回」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "kyphosis-cause-redflags",
    "title": "その猫背、本当に「ただの姿勢の悪さ」？〜見逃してはいけない骨粗鬆症・脊柱変形と受診の目安【猫背改善シリーズ①】",
    "subtitle": "猫背改善シリーズ第1回。7つの医学的病態、4大危険サイン、自宅でできる3つのセルフチェック",
    "description": (
        "猫背は単なる生活習慣の癖ではなく、背骨の骨折（骨粗鬆症性椎体骨折）や構築性の脊柱変形、"
        "さらには神経の病気が隠れていることがあります。骨粗鬆症による背骨の骨折の約3分の2は痛みのない"
        "「いつの間にか骨折」であり、骨が脆い状態で無理に背筋を反らすと新たな骨折を招く危険があります。"
        "神経内科・総合内科専門医の視点から、7つの医学的分類、4大危険サイン、自宅でできる3つのセルフチェック、"
        "受診すべき科の目安を解説。猫背改善シリーズ全4回の第1回／全15スライド。"
    ),
    "youtube_id": "",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/kyphosis-cause-redflags",
    "source_dir": "kyphosis-cause-redflags/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 15,
    "tags": [
        "猫背",
        "姿勢改善",
        "骨粗鬆症",
        "椎体骨折",
        "胸椎過後弯",
        "一般・患者向け",
    ],
    "published_date": "2026-09-12",
    "viewer_notice": "本資料は一般的な医学情報の解説であり、個別の診断・治療方針を示すものではありません。気になる症状がある場合は、かかりつけ医や専門医療機関（整形外科・脳神経内科など）にご相談ください。",
    "html_deck": True,
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
    MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] manifest.json を更新しました（全 {len(decks)} 件）")


if __name__ == "__main__":
    main()
