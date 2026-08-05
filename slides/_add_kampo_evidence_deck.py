# -*- coding: utf-8 -*-
"""manifest.json に 漢方エビデンス deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "kampo-evidence",
    "title": "エビデンスのある漢方はどれ？｜ガイドラインが「強く推奨」した処方と「使うな」とされた処方",
    "subtitle": "推奨の強さとエビデンスレベルで、漢方を格付けする",
    "description": (
        "漢方は「効く・効かない」の二択ではなく、処方と病気の組み合わせごとに評価が分かれます。"
        "日本東洋医学会EBM委員会が集計した一次資料（KCPG2025 H1・調査期間〜2025年9月）によると、"
        "調査対象の診療ガイドライン1,955件のうち漢方の記載があるのは170件（8.6%）で、"
        "エビデンスレベルと推奨の強さの両方が付いた「タイプA」は47件だけです。"
        "そのなかで、機能性ディスペプシア（胃もたれ）に対する六君子湯は"
        "「推奨の強さ：強、エビデンスレベル：A」で、標準治療に近い位置づけまで来ています"
        "（機能性消化管疾患診療ガイドライン2021）。ただし根拠となったRCTは、"
        "主要評価項目を達成したDREAM試験と、達成できなかった2014年の247人試験の両方があります。"
        "一方、多系統萎縮症の便秘に対する大建中湯は推奨が最上位の「強く推奨する」でありながら、"
        "根拠は10例ほどのオープン試験で、ガイドライン自身が「エビデンスの高い研究は少ない」と注記しています"
        "＝「推奨の強さ」と「根拠の質」は別物です。抑肝散は認知症の行動・心理症状に対して"
        "推奨「弱」・エビデンス「C」で、低カリウム血症への注意が明記されています。"
        "そして牛車腎気丸は、抗がん剤による末梢神経障害の予防について"
        "「投与しないことを提案する」と否定されており、第III相のGENIUS試験では"
        "日常生活に支障が出るレベルのしびれが牛車腎気丸群50.6%・偽薬群31.2%と"
        "投与群のほうが多く、中間解析で試験が中止されています。全22スライド。"
    ),
    "youtube_id": "VFrY8SGc_Cw",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/05/135706",
    "source_dir": "漢方エビデンス/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 22,
    "tags": ["漢方", "エビデンス", "六君子湯", "抑肝散", "牛車腎気丸", "診療ガイドライン"],
    "published_date": "2026-08-05",
    "html_deck": True,
    "infographic": False,
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
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print("total decks:", len(decks))


if __name__ == "__main__":
    main()
