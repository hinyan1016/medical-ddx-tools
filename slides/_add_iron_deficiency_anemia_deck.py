# -*- coding: utf-8 -*-
"""manifest.json に 鉄欠乏性貧血の食事・生活指導（外来指導シリーズ第26弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "iron-deficiency-anemia-guidance",
    "title": "鉄欠乏性貧血の外来指導テンプレート｜やめどきは「ヘモグロビン」ではなくフェリチン",
    "subtitle": "「数値が戻った」で終わらせない ― お茶は禁じない、原因検索は省かない",
    "description": (
        "鉄欠乏性貧血で外来がつまずくのは診断ではなく「鉄剤を出した後」。①やめどきはヘモグロビンではない"
        "——Hbは6〜8週で正常化するが、国内指針の中止時期は「貧血が治癒し、かつ、血清フェリチンが正常化する時」で、"
        "BSGはHb正常化後さらに約3か月の継続を推奨。初回処方時にこれを伝えるかどうかで自己中断が変わる。"
        "②用量は多いほど効くわけではない——同位体試験で投与量6倍でも吸収は3倍、80歳超では15 mgと150 mgでHb反応が同程度。"
        "③隔日投与は「上位互換」ではない——吸収率は上がるが唯一のアウトカムRCTでは連日2回のほうがHb上昇が速く、"
        "BSGは不耐時の選択肢に位置づける。「連日はもう古い」は誤り。④副作用は「やめる理由」ではなく「調整する理由」"
        "——減量→服用時間→剤型→静注の順。⑤お茶は禁じない・ビタミンCは足さない——「食事の鉄」と「鉄剤」で結論が逆になる。"
        "⑥食事は予防、治療は鉄剤。推奨量を大きく超える摂取は治療目的以外では控える。⑦原因検索を省かない"
        "——男性・閉経後女性は上下部内視鏡が第一選択、若年女性は懸念所見があるときのみ。検査待ちで鉄剤を遅らせない。"
        "日本鉄バイオサイエンス学会の治療指針（第3版）・日本人の食事摂取基準2025年版・BSG 2021 を原文で確認し、"
        "脳神経内科・総合内科専門医監修で全17スライドに整理。医療従事者向け。外来患者指導テンプレート・シリーズ第26弾。"
    ),
    "youtube_id": "",
    "blog_url": "",
    "source_dir": "鉄欠乏性貧血生活指導/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 17,
    "tags": ["鉄欠乏性貧血", "鉄剤", "フェリチン", "外来指導", "貧血"],
    "published_date": "2026-07-30",
    "viewer_notice": "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。気になる症状があれば主治医にご相談ください。",
    "html_deck": True,
    "infographic": "https://tools.ichisouzo-lab.com/infographics/iron-deficiency-anemia-guidance/",
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
