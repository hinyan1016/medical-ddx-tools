# -*- coding: utf-8 -*-
"""manifest.json に「DEFT-AIアプローチ」deck を追加する（既存なら更新）。

blog_url / youtube_id はブログ公開・動画公開のあとに埋める。
再実行すると slug 一致で更新されるので、URL が確定したら本ファイルを書き換えて再実行すればよい。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "deft-ai-clinical-reasoning",
    "title": "研修医がAIの鑑別を持ってきたとき、指導医は何を聞くか｜DEFT-AIアプローチの5ステップ",
    "subtitle": "DEFT-AIは4段階ではなく5段階。5番目「どの監督レベルでAIを使ってよいか」が本体",
    "description": (
        "研修医が「ChatGPTに聞いたらこの鑑別が出ました」と言ってきたとき、指導医は何を返すべきか。"
        "NEJM 2025 が提唱した DEFT-AI は、AIの使用を禁じる枠組みではなく、使った瞬間を教育機会に変える"
        "問いかけの型である。日本語の解説の多くは「4ステップ」と紹介するが、原著の KEY POINTS は "
        "DEFT-AI (diagnosis, evidence, feedback, teaching, and recommendation for AI use) と逐語で記しており、"
        "実際は5段階。D・E・F・T の4つは Savaria 2022 の DEFT（＝Neher 1992 の One-Minute Preceptor を"
        "整理したもの）そのままで、著者らが足したのは5番目の AI Engagement Recommendation＝"
        "「この学習者は次にどの監督レベルでAIを使ってよいか」を言語化して手渡すステップである。"
        "研修医の手技と同じ監督レベル管理を、AI利用に持ち込んだ点が新しい。"
        "枠組みの紹介にとどめず、必要性を一次文献の数値で示した。①LLMを渡しても医師の診断推論は改善しない"
        "（補正差2ポイント、P=.60。一方LLM単独は+16ポイント／Goh 2024）。②英国レプリケーションでは"
        "設問の30%しかLLMに投げられていなかった＝性能でなく使い方の問題（Healy 2026）。"
        "③系統的に偏ったAIでは診断精度が−11.3ポイント、説明をつけても−9.1ポイントで改善しない"
        "＝得より損が大きい非対称（Jabbour 2023, n=457）。④最終学年の医学生148名がLLM出力を正しく評価できたのは"
        "中央値56%、clinical prompt engineering を知っていたのは5%（Waldock 2025）。"
        "⑤LLMはアンカーを1位に置く率が55.6%で研修医21.2%・指導医10.0%より高く、AIに投げてもアンカリングは"
        "軽減されず増幅されうる（Sheppert 2026）。⑥AIが見逃した症例では読影者の感度が71%→39%に低下（Taib 2026）。"
        "そのうえで、DEFT-AI の有効性を検証した研究はまだ無いこと（原典は総説、類縁のSNAPPSですら"
        "Kirkpatrick Level 3/4 の報告はゼロ）も併記した。PubMed逆引きで実在確認した一次文献19件を"
        "全21スライドに整理。指導医・研修医・医学生向け。"
    ),
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "deft_ai_clinical_reasoning/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 21,
    "tags": [
        "臨床推論",
        "医学教育",
        "生成AI",
        "DEFT-AI",
        "研修医指導",
        "医師向け",
    ],
    "published_date": "",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個々の指導方法や診療方針の成果を保証するものではありません。DEFT-AIは2025年に提唱された枠組みで、本資料作成時点でその有効性を検証した研究は確認できていません。引用研究の多くはビネット研究・観察研究・総説です。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/deft-ai-clinical-reasoning/",
}


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    decks = data["decks"]
    for i, d in enumerate(decks):
        if d.get("slug") == DECK["slug"]:
            decks[i] = DECK
            action = "更新"
            break
    else:
        decks.append(DECK)
        action = "追加"
    MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print("{}: {}（decks {} 件）".format(action, DECK["slug"], len(decks)))


if __name__ == "__main__":
    main()
