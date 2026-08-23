# -*- coding: utf-8 -*-
"""manifest.json に「脳梗塞急性期の降圧治療」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "acute-ischemic-stroke-bp",
    "title": "脳梗塞急性期の血圧はどこまで下げるか｜再灌流療法の有無で変わる降圧の判断【ガイドライン2025・AHA2026対応】",
    "subtitle": "再灌流療法を行わないなら220/120まで下げない、行うなら185/110未満。回収後に140未満を目指さない理由",
    "description": (
        "脳梗塞急性期の血圧管理を、脳卒中治療ガイドライン2021〔改訂2025〕、AHA/ASA 2026、"
        "および主要RCT（ENCHANTED2/MT、OPTIMAL-BP、BEST-II、BP-TARGET、CATIS、SCAST）の一次資料に基づいて整理。"
        "分かれ目は「下げる／下げない」ではなく、再灌流療法を行うのか、行ったのか。"
        "再灌流療法を行わない場合は収縮期220または拡張期120を超えるまで原則降圧しない（推奨度D）、"
        "rt-PA静注療法では投与前185/110未満・投与後24時間は180/105以下、"
        "血栓回収療法後は速やかに180以下へ。ただし回収中・回収後に140以下へ下げることは推奨度E（行わないよう勧められる）で、"
        "強化降圧を検証した4試験がいずれも利益を示せなかった経緯まで全27枚で解説。"
        "内服再開は神経症状が安定していれば発症24時間以降に考慮（推奨度C）。"
    ),
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "脳梗塞急性期_降圧治療/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 27,
    "tags": [
        "脳梗塞",
        "血圧管理",
        "permissive hypertension",
        "rt-PA",
        "血栓回収療法",
        "ENCHANTED2/MT",
        "OPTIMAL-BP",
        "医師向け",
    ],
    "published_date": "2026-08-23",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診断・治療方針を示すものではありません。実際の診療判断は施設プロトコル・最新電子添文に従ってください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/acute-ischemic-stroke-bp/",
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
