# -*- coding: utf-8 -*-
"""manifest.json に 視力低下と認知症（認知症×生活習慣病シリーズ第9弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "dementia-vision-loss",
    "title": "「白内障の手術で認知症が減る」——その研究、緑内障の手術と比べてみたら",
    "subtitle": "白内障手術を受けた人はHR 0.71｜視力を戻さない緑内障手術という陰性対照ではHR 1.08｜それでもランダム化試験は一つもない",
    "description": (
        "2024年、Lancet委員会は「未矯正の視力低下」を認知症の新しい危険因子に加えました（晩年期のPAF 2%）。"
        "約3,000人を7.8年追跡した米国ACT研究では、白内障手術を受けた人でその後の認知症が少なかった"
        "（HR 0.71・95%CI 0.62–0.83）という結果があります。ですがそれは「手術を受けられる人がもともと健康なだけ」"
        "かもしれません。研究者は同じコホートの中で、視力を回復させない緑内障手術を「陰性対照」として置きました。"
        "結果、関連は消えました（HR 1.08・95%CI 0.75–1.56）。それでも「手術で認知症を防げる」ことを示した"
        "ランダム化比較試験は一つもなく、メタ解析の著者自身が「ランダム化試験でさらに検証されるべきだ」と"
        "結論しています。日本の藤原京アイスタディでは、白内障手術歴は軽度認知障害とは関連しましたが"
        "認知症そのものとは有意に関連しませんでした。視力低下が認知症に占める割合は、測り方によって"
        "1.8%から19.0%まで大きく異なり、その理由も扱います。扱うのはすべて観察研究とメンデルランダム化研究で、"
        "手術を割り付けた比較試験ではありません。認知症×生活習慣病シリーズ第9弾（第2期の初弾）／全18スライド。"
        "医師・一般の両方に向けた内容です。"
    ),
    "source_dir": "視力低下と認知症/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "白内障", "白内障手術", "視力低下", "緑内障", "認知症", "認知症予防",
        "コントラスト感度", "生活習慣病", "コホート研究", "脳神経内科",
    ],
    "published_date": "2026-08-18",
    "viewer_notice": (
        "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。"
        "ここで扱ったのはすべて観察研究とメンデルランダム化研究で、白内障の手術によって"
        "認知症を防げることが証明されたわけではありません。気になる症状があれば主治医にご相談ください。"
    ),
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
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("decks:", len(decks))


if __name__ == "__main__":
    main()
