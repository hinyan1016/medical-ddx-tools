# -*- coding: utf-8 -*-
"""manifest.json に 喫煙と認知症（認知症×生活習慣病シリーズ第5弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "dementia-smoking",
    "title": "「いまさらやめても遅い」——喫煙と認知症、やめてから何年でどうなるのか",
    "subtitle": "現在喫煙者は約1.3倍｜元喫煙者では差が見えなくなる｜ただし何年かかるかは研究で食い違う（3年・約7年・9年）",
    "description": (
        "「もう何十年も吸ってきたのに、いまさらやめて意味があるのか」——それを直接調べた"
        "5つのデータを、集団も基準にした群も違うまま並べずに、ひとつずつ確認します。"
        "メタ解析では現在喫煙者の認知症リスクは1.30倍（95%CI 1.18–1.45）、1日20本増えるごとに1.34倍。"
        "一方で元喫煙者は1.01倍（0.96–1.06）で非喫煙者との差が見えません。"
        "日本の大崎コホート（65歳以上12,489人）では禁煙3〜5年の群で差が見えなくなり、"
        "米国 Health and Retirement Study（32,802人）のスプライン曲線では禁煙後およそ7年で頭打ち、"
        "米国 ARIC（13,002人）では9年以上前にやめた人で関連が見られませんでした。"
        "推定値が食い違うのは集団も基準群も違うためで、ひとつの年数には決められません。"
        "韓国 NHIS（789,532人）では本数を半分以下に減らした群で禁煙と同じ結果にはなっておらず、"
        "減煙で禁煙と同じ利益が得られることは確認されていません。"
        "禁煙後の体重増加の扱い、Lancet 2024 委員会報告における喫煙の人口寄与割合（PAF）2%の読み方、"
        "受動喫煙と加熱式たばこについて言えること／言えないことまで扱います。"
        "扱うのはすべて観察研究で、喫煙や禁煙を割り付けた比較試験ではありません。"
        "認知症×生活習慣病シリーズ第5弾／全18スライド。医師・一般の両方に向けた内容です。"
    ),
    "source_dir": "喫煙と認知症/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "禁煙", "認知症", "たばこ", "喫煙", "認知症予防", "受動喫煙",
        "加熱式たばこ", "生活習慣病", "コホート研究", "脳神経内科",
    ],
    "published_date": "2026-08-15",
    "viewer_notice": (
        "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。"
        "ここで扱ったのはすべて観察研究で、禁煙によって認知症を防げることが証明されたわけではありません。"
        "気になる症状があれば主治医にご相談ください。"
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
