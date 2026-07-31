# -*- coding: utf-8 -*-
"""manifest.json に 禁煙の外来サポート（外来指導シリーズ第28弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "smoking-cessation-guidance",
    "title": "禁煙の外来指導テンプレート｜「やめる気がありますか」で選別しない・加熱式も保険の対象",
    "subtitle": "意志の問題にする前に ― 12週・5回で組める保険診療と、体重の話を先にする理由",
    "description": (
        "禁煙外来でつまずくのは知識ではなく「どう声をかけるか・保険でどこまで組めるか・どう続けさせるか」の3か所。"
        "①やめる気がない人にも支援を差し出す——医学的理由による助言と、支援を実際に差し出すことを比較したメタ解析では、"
        "助言よりも行動支援やニコチン製剤を「差し出す」ほうが禁煙試行を増やした。著者は、意思を示した人だけでなく"
        "全員に差し出すほうが有効かもしれないと結論している（直接比較された戦略ではなく著者の推論）。増えたのは禁煙試行で、成功率まで及ぶかは示されていない。"
        "「やめる気がありますか」で選別せず、「やめるときになったら保険で薬を出せます」と出口だけ置いて次につなぐ。"
        "ただし短時間介入の絶対効果は小さく、自力の2〜3%に1〜3%の上乗せにとどまることも同時に押さえる。"
        "②加熱式たばこに替えたのは禁煙ではない、しかし保険の対象ではある——コクランのレビューは紙巻たばこの禁煙を"
        "アウトカムとして報告した研究が1本もなく、組み入れたRCTはすべてたばこ企業の資金だったと明記する。"
        "厚生労働省も2026年7月の見解で「紙巻たばこより健康への影響が少ないというエビデンスはない」としている。"
        "一方で診療報酬の通知は加熱式の喫煙者にも標準手順書に沿った禁煙治療を行うとしており、ブリンクマン指数は"
        "加熱式を紙巻に換算して算入する。③保険で治療できるかは4条件で確かめる——TDS 5点以上、35歳以上はブリンクマン"
        "指数200以上（35歳未満は問わない）、直ちに禁煙する意思、文書同意。初回算定日から1年を超えないと再算定できない"
        "点も同時に伝える。④薬は渡すときに全部言う——貼っている間は吸わせない、TTS30を4週・20を2週・10を2週の8週間で"
        "10週を超えない、MRIや電気的除細動・サウナの前には外す、貼付部位は毎回変える。バレニクリンは2026年7月時点で"
        "通常出荷に戻っており後発品はない。⑤体重の話を先にする——手順書の患者向け回答は平均2〜3kg程度、62研究の"
        "メタ解析は12か月で平均4.67kgと食い違うが、いずれにせよ幅が大きく、16%は減り13%は10kgを超えて増えた。"
        "それでも糖尿病のない集団では、禁煙による心血管イベントの低下は体重変化で調整してもほとんど変わらない。⑥「タバコでストレスを"
        "逃している」には、禁煙後に不安・抑うつ・ストレスがいずれも改善したというデータで答える。⑦再喫煙は失敗ではなく"
        "通常の過程だが、保険の1年ルールも同時に伝えて言いっぱなしにしない。禁煙治療のための標準手順書 第8.1版"
        "（2021年9月）・令和8年度診療報酬の告示と通知・PMDA電子添文・コクランレビューを原文で確認し、"
        "脳神経内科・総合内科専門医監修で全17スライドに整理。医療従事者向け。外来患者指導テンプレート・シリーズ第28弾。"
    ),
    "youtube_id": "rC8IcJtgpYo",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/07/31/155114",
    "source_dir": "禁煙外来サポート指導/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": ["禁煙", "禁煙外来", "ニコチン依存症管理料", "外来指導", "加熱式たばこ"],
    "published_date": "2026-07-31",
    "viewer_notice": "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。気になる症状があれば主治医にご相談ください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/smoking-cessation-guidance/",
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
