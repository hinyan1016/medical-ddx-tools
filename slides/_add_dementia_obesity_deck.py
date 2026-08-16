# -*- coding: utf-8 -*-
"""manifest.json に 肥満と認知症（認知症×生活習慣病シリーズ第6弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "dementia-obesity",
    "title": "「太っていると認知症になる」は本当か——肥満と認知症、40代と70代で見え方が逆になる理由",
    "subtitle": "問題になるのは中年期の体重｜高齢のやせは前駆期の体重減少（逆因果）で説明できる｜減量で認知症が減った試験はまだない",
    "description": (
        "「太っていると認知症になる」——この問いには、そのままでは答えられません。"
        "同じ肥満でも、40代で測った体重と70代で測った体重では、認知症との関係が逆向きに見えるからです。"
        "おおむね40代〜50代の肥満は認知症リスクと関連しますが、"
        "Whitehall II（28年追跡）で有意だったのは50歳時点の肥満だけで、60歳・70歳では関連が見られません。"
        "日本人でも向きは同じで、JPHC研究では中年期の肥満で男性 HR 1.31・女性 HR 1.37。"
        "ただしこの研究の「肥満」は BMI 27.0〜39.9 であって、日本の肥満基準（25以上）とは別物です。"
        "一方、高齢者を対象にすると関連は消えるか逆向きに見えます。"
        "その主な説明が逆因果で、個人データ130万人の解析では、BMI を診断の10年以内に測ると HR 0.71、"
        "10〜20年前で 0.94、20年より前に測ると 1.16 と、測った時期で符号が変わります。"
        "体重が減り始めるのは診断のおよそ8年前からで、診断が近づくほど減少が加速します。"
        "つまり「高齢でやせている＝安全」ではなく、体重が減ってきたこと自体が別の意味を持ちます。"
        "BMI だけで足りるのかという問い（腹部の脂肪は BMI 調整後も HR 1.92）、"
        "遺伝学的手法（メンデルランダム化）が2本あって結論が逆向きであること、"
        "10年間の減量介入で認知機能障害の頻度が変わらなかった介入試験、"
        "14の危険因子のなかで肥満の人口寄与割合が1%と小さく見える理由まで扱います。"
        "扱う研究の大半は観察研究で、減量によって認知症を防げることが示されたわけではありません。"
        "認知症×生活習慣病シリーズ第6弾／全18スライド。医師・一般の両方に向けた内容です。"
    ),
    "source_dir": "肥満と認知症/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "肥満", "認知症", "BMI", "中年期", "内臓脂肪", "体重減少",
        "認知症予防", "生活習慣病", "コホート研究", "脳神経内科",
    ],
    "published_date": "2026-08-16",
    "viewer_notice": (
        "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。"
        "ここで扱った研究の大半は観察研究で、減量によって認知症を防げることが証明されたわけではありません。"
        "体重が減ってきた高齢の方は、自己判断せず主治医にご相談ください。"
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
    # manifest.json は LF のみ。Windows の text mode 既定だと CRLF に化けて全行 diff になるので newline="" を明示する
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(m, ensure_ascii=False, indent=2) + "\n")
    print("decks:", len(decks))


if __name__ == "__main__":
    main()
