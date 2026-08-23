# -*- coding: utf-8 -*-
"""manifest.json に「脳出血急性期の降圧治療」deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "acute-ich-bp",
    "title": "脳出血急性期の血圧はどこまで下げるか｜140未満を目指し110未満を避ける理由【ガイドライン・INTERACT/ATACH-2対応】",
    "subtitle": "血腫拡大阻止の早期140未満目標と、ATACH-2が示した過度急速降圧（110未満）回避の安全域",
    "description": (
        "脳出血急性期の血圧管理を、脳卒中治療ガイドライン2021［改訂2023］、AHA/ASA 2022、"
        "および主要RCT（INTERACT2/3、ATACH-2）の一次資料に基づいて整理。"
        "脳梗塞の permissive hypertension（下げない）とは真逆の病態生理から、"
        "発症早期の血腫拡大（約38%発生・死亡リスク5倍）を防ぐ「速やかな SBP 140 mmHg 未満」の必要性、"
        "ATACH-2 で示された「110〜120 未満への過度降圧による腎障害増加（9.0% vs 4.0%）」の教訓、"
        "ニカルジピン持続点滴の実務と血圧変動性（ばらつき）管理、抗凝固薬緊急中和との連動まで全18枚で解説。"
    ),
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "脳出血急性期_降圧治療/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "脳出血",
        "血圧管理",
        "降圧目標",
        "INTERACT2",
        "ATACH-2",
        "ニカルジピン",
        "医師向け",
    ],
    "published_date": "2026-08-23",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個別の診断・治療方針を示すものではありません。実際の診療判断は施設プロトコル・最新電子添文に従ってください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/acute-ich-bp/",
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
