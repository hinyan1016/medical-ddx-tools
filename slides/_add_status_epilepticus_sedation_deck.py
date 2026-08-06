# -*- coding: utf-8 -*-
"""manifest.json に「高齢者のてんかん重積：麻酔薬導入の判断」deck を追加する（既存なら更新）。

blog_url はブログ公開のあとに埋める。
再実行すると slug 一致で更新されるので、URL が確定したら本ファイルを書き換えて再実行すればよい。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "status-epilepticus-sedation",
    "title": "高齢者のてんかん重積、どこで麻酔薬・挿管に踏み切るか｜けいれん性と非けいれん性で分かれる判断軸",
    "subtitle": "分岐の軸は年齢でも入院前ADLでもなく、発作型 × 意識レベル",
    "description": (
        "複数の抗てんかん薬でも発作が止まらない高齢者に、持続静注麻酔薬を入れて挿管まで踏み切るか。"
        "日本語の解説の多くは「第2段階で止まらなければ約30分で全身麻酔へ」と発作型を問わず一律に提示するが、"
        "2026年時点の国際文献が示す答えは違う。①中欧3か国9施設の前向きレジストリでは、難治性重積に進展した"
        "545例のうち71.7%が挿管されずに治療され、52.7%が良好転帰だった。しかも重症度が均質な集団でも、"
        "治療的昏睡の使用率は施設間で25.4%対9.75%と2.6倍違う＝いまの判断はエビデンスより施設文化に依存している。"
        "②2026年のスコーピングレビューは、持続静注麻酔薬が正当化されるのはけいれん性の難治性重積・subtle SE・"
        "昏睡を伴うNCSEであり、意識が保たれたNCSEと焦点運動発作性重積（EPC）では役割が乏しいと結論している。"
        "覚醒例の致死率8.2%に対し意識障害例は33%。③ILAE定義のt1（治療を開始すべき時点＝5分）とt2（神経損傷の"
        "リスクが生じる時点＝30分）が与えられているのはけいれん性重積だけで、他の病型にはデータがない。"
        "④「麻酔薬が予後を悪くする」の根拠とされるコホートは、原著自身が難治性で追加調整すると有意でなくなったと"
        "明記しており、前向き多施設研究でも調整後に差は消えた＝適応による交絡。⑤入院前の機能障害がある群では"
        "治療制限が約3倍多く行われたが、1年後に機能が悪化しなかった割合は42.9%対44.1%でほぼ同じで、多変量解析でも"
        "入院前の機能状態は独立して関連しなかった＝差し控えの根拠に最もよく使われる因子が、最も予測力が乏しかった。"
        "⑥導入前の3ゲート（本当にNCSEか・病因は治療しうるか・上流を尽くしたか）と、導入後の4原則"
        "（遅らせない・目標は発作停止・期間は最短・持続脳波で離脱）。期間の最短化はそのまま廃用対策になる。"
        "PubMed収載の一次文献21件をメタデータ照合したうえで全26スライドに整理。脳神経内科医・救急医・集中治療医向け。"
    ),
    "youtube_id": "2Jbvih_BZx0",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/06/170325",
    "source_dir": "高齢者てんかん重積_麻酔導入判断/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 26,
    "tags": [
        "てんかん重積",
        "難治性てんかん重積",
        "非けいれん性てんかん重積",
        "集中治療",
        "医師向け",
    ],
    "published_date": "2026-08-06",
    "viewer_notice": "本資料は医療従事者向けの教育・知識整理であり、個々の診療方針を保証するものではありません。引用研究の大半は観察研究です。薬剤の用量・投与速度は各施設のプロトコルと添付文書に従ってください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/status-epilepticus-sedation/",
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
