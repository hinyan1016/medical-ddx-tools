# -*- coding: utf-8 -*-
"""manifest.json に 熱中症・脱水の予防と経口補水（外来指導シリーズ第34弾）deck を追加する（既存なら更新）。

youtube_id / blog_url は動画アップロードとブログ公開のあとに埋める。
再実行すると slug 一致で更新されるので、ID が確定したら本ファイルを書き換えて再実行すればよい。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "heatstroke-hydration-guidance",
    "title": "熱中症・脱水の水分補給指導テンプレート｜経口補水液は「病者用食品」・のどの渇きは相手で逆",
    "subtitle": "予防に毎日ではない ― 3段階で使い分け・のどの渇きは運動する人と高齢者で逆",
    "description": (
        "経口補水液を「予防のために毎日飲む物」と誤解している患者は多いが、国の分類では"
        "特別用途食品のうちの病者用食品であり、消費者庁は脱水状態でない方が普段の水分補給として"
        "飲むものではないと明記している。①飲み物は3段階で選ぶ——普段は水・麦茶、汗をかいている"
        "最中は塩分の入ったもの、下痢・嘔吐・熱中症の症状で脱水したときに初めて経口補水液を使う。"
        "水だけでは飲んだそばから尿になって出ていきやすく、足がつりやすくなる。"
        "②経口補水液はスポーツドリンクよりナトリウム・カリウムが約3〜4倍多く、濃さが違う飲み物である。"
        "③「のどが渇く前に飲む」は相手によって逆になる——運動・労働する成人はのどが渇いたら飲むで"
        "合っているが、高齢者はのどの渇きを当てにしてはいけない。高齢者が水分をとってくれない本当の"
        "理由は知識不足ではなく尿失禁への不安であり、地域高齢者への面接調査で報告されている。"
        "服薬時・食事時に必ずコップ1杯という新しい習慣を足さない指導が効く。"
        "④腎臓・心臓・糖尿病の治療中は、経口補水液を飲む前に主治医へ確認する。"
        "⑤熱中症警戒アラート（WBGT33）を待たない——危険の目安はWBGT31から。特別警戒アラートは35。"
        "⑥受診ラインはI度（現場対応可）とII度以上（受診）、意識障害や自力飲水不能は救急を明確に区別する。"
        "日本救急医学会「熱中症診療ガイドライン2024」、消費者庁、環境省の一次資料とPubMed収載文献を"
        "原文で確認し、全17スライドに整理。医療従事者向け。外来患者指導テンプレート・シリーズ第34弾。"
    ),
    "youtube_id": "Dc1JOpBv-zk",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/08/06/120024",
    "source_dir": "熱中症・脱水の予防と経口補水/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": [
        "熱中症",
        "脱水",
        "経口補水液",
        "水分補給",
        "外来指導",
    ],
    "published_date": "2026-08-06",
    "viewer_notice": "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。気になる症状があれば主治医にご相談ください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/heatstroke-hydration-guidance/",
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
