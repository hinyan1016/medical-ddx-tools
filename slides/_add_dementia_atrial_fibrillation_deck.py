# -*- coding: utf-8 -*-
"""manifest.json に 心房細動と認知症（認知症×生活習慣病シリーズ第10弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "dementia-atrial-fibrillation",
    "title": "心房細動と認知症｜脳梗塞を起こさなくてもリスクは上がるのか——「薬で下げられる」はどこまで確かめられているか",
    "subtitle": "43研究のメタ解析でOR1.6｜抗凝固薬使用者ではHR0.71も観察デザインを揃えるとHR0.75へ消える｜最大のランダム化試験（BRAIN-AF）はHR1.10で無益・早期中止",
    "description": (
        "心房細動（心臓の上の部屋が細かく震える不整脈）のある人では、臨床的な脳梗塞を起こしていなくても、"
        "その後の認知症が多い——複数の大規模観察研究がその方向を示します。43研究をまとめたメタ解析では"
        "調整オッズ比1.6（95%CI 1.3–2.1）。脳卒中を考慮・打ち切っても関連は残ります"
        "（RR1.34・HR1.23・HR1.33）が、オランダの住民コホートでは67歳以上で有意ではありません。"
        "では抗凝固薬（血液を固まりにくくする薬）でそのリスクを下げられるのでしょうか。観察研究では"
        "抗凝固薬を使っている人のほうが認知症が少なく見えます（スウェーデン44万人でHR0.71）が、"
        "観察ウィンドウを設けた4研究に絞るとRR0.75（有意でない）、日本のレセプトデータでもHR0.66"
        "（有意でない）に消えます。検証した最大のランダム化試験（BRAIN-AF）はHR1.10（95%CI 0.86–1.40）で"
        "無益と判定され早期中止されました。対象は平均53.4歳の低リスク層で、著者は結果を心房細動患者全体に"
        "外挿すべきではないと明記しています。心房細動はLancet委員会の認知症14の危険因子リストには"
        "入っていませんが、それは「重要でない」という意味ではありません。認知症×生活習慣病シリーズ"
        "第10弾（第2期「リストの外側」編の初弾）／全18スライド。医師・一般の両方に向けた内容です。"
    ),
    "source_dir": "心房細動と認知症/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "心房細動", "不整脈", "認知症", "認知症予防", "脳梗塞",
        "抗凝固薬", "無症候性脳梗塞", "ランダム化比較試験", "生活習慣病", "脳神経内科",
    ],
    "published_date": "2026-08-19",
    "viewer_notice": (
        "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。"
        "心房細動の治療で認知症を防げると証明されたわけではありません。ここで扱った観察研究は"
        "因果関係を示すものではなく、最大のランダム化試験（BRAIN-AF）の対象は血栓塞栓リスクが低い集団で、"
        "著者自身が結果を心房細動患者全体に外挿すべきではないと明記しています。自己判断で抗凝固薬を"
        "やめないでください。気になる症状があれば主治医にご相談ください。"
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
