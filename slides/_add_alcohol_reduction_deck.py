# -*- coding: utf-8 -*-
"""manifest.json に 節酒・減酒の外来サポート（外来指導シリーズ第33弾）deck を追加する（既存なら更新）。

youtube_id / blog_url は動画アップロードとブログ公開のあとに埋める。
再実行すると slug 一致で更新されるので、ID が確定したら本ファイルを書き換えて再実行すればよい。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "alcohol-reduction-guidance",
    "title": "節酒・減酒の外来指導テンプレート｜「やめられますか」で始めない・40gは許容量ではない",
    "subtitle": "断酒一択にしない ― 数える・目標を置く・急にやめさせない",
    "description": (
        "外来で飲酒の話を切り出しにくいのは、聞いた先に「やめられますか」しか用意がないからである。"
        "①最初の質問を「やめられますか」にしない——学会の手引き（2019年小改訂）は、軽症の依存症で明確な合併症を"
        "有しないケースで、患者が断酒を望む場合などを除き、飲酒量低減が治療目標になるとしている。"
        "同手引きは、精神科などの専門医療機関でなくても対応が可能となることを目的として作成されたと明記し、"
        "プライマリケア医や内科医、研修医を対象に挙げている。まずやるのは純アルコール量の計算"
        "（飲んだ量mL × 度数% ÷ 100 × 0.8）とAUDIT-Cの3問だけでよい。"
        "②男性40g・女性20gは「ここまで飲んでよい量」ではない——厚生労働省の飲酒ガイドラインと"
        "アルコール健康障害対策推進基本計画は、いずれも「これらの量は個々人の許容量を示したものではありません」と"
        "明記している。生活習慣病のリスクを高める量であり、ここから下げていく出発点として使う。"
        "③効果判定を「40g/20gに届いたか」で行わない——手引きは、この目安に達しなくとも、治療開始時よりも"
        "飲酒量が低下し、飲酒に関係した健康障害や社会・家族問題の軽減が認められる場合、飲酒量低減による治療の"
        "効果が認められたと判断できるとしている。"
        "④心理社会的治療が主役で、薬は補助である——飲酒量低減の適応を持つのはナルメフェンのみで、"
        "電子添文は心理社会的治療と併用していない場合の有効性は確立していないと明記する。"
        "アカンプロサートとジスルフィラム・シアナミドは断酒目標の薬であり、減酒薬として並べない。"
        "簡易介入の効果量は小さく、それを正直に伝えたうえで外来で繰り返す。"
        "⑤自分の判断で急にやめてはいけない人がいる——離脱けいれんは最後の飲酒から6〜48時間、"
        "振戦せん妄は48〜72時間で現れうる。最も信頼できる予測因子は「前にも起きたこと」であり、"
        "性別や肝疾患の合併は予測因子ではなかった。離脱の既往・朝の手のふるえ・迎え酒があれば、"
        "「今日から一滴もやめます」をそのまま帰さない。"
        "厚生労働省の飲酒ガイドラインと基本計画、学会の手引き、PMDA電子添文を原文で確認し、"
        "PubMed収載文献と突き合わせて全17スライドに整理。医療従事者向け。外来患者指導テンプレート・シリーズ第33弾。"
    ),
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "減酒指導/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": [
        "減酒",
        "節酒",
        "飲酒量",
        "純アルコール量",
        "AUDIT-C",
        "外来指導",
    ],
    "published_date": "2026-08-04",
    "viewer_notice": "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。気になる症状があれば主治医にご相談ください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/alcohol-reduction-guidance/",
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
    # indent=2 / ensure_ascii=False / LF を守らないと全行書換の diff になる
    MANIFEST.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    print("{}: {}（decks {} 件）".format(action, DECK["slug"], len(decks)))


if __name__ == "__main__":
    main()
