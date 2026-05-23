#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""expansion_candidates.csv の確定済み候補を manifest.json に追加する。
slug, タイトル, 説明, タグ, slide_count は手書きで明示指定。
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[3]
MANIFEST = WORKSPACE / "medical-ddx-tools" / "slides" / "manifest.json"

# 各エントリ: (slug, source_dir, pdf_filename, slide_count, youtube_id, blog_url,
#             title, subtitle, description, tags, published_date)
NEW_DECKS = [
    # シリーズ・既存PNG完備
    {
        "slug": "handedness",
        "title": "利き手はなぜ決まるのか？",
        "subtitle": "脳の左右非対称と遺伝のしくみ｜からだの不思議 #11",
        "description": "利き手が決まる仕組みを脳の左右機能差・遺伝・環境要因から解説。",
        "youtube_id": "sSF6r7Eu_hU",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/11/083220",
        "source_dir": "からだの不思議11_利き手",
        "slide_prefix": "slide-",
        "pdf_filename": "利き手_スライド.pdf",
        "slide_count": 11,
        "tags": ["脳科学", "利き手", "発達"],
        "published_date": "2026-04-11",
    },
    {
        "slug": "bathing-epilepsy",
        "title": "お風呂で決まって意識を失う ― 入浴てんかん",
        "subtitle": "正体と安全対策",
        "description": "入浴中の意識消失発作（入浴てんかん）の特徴・診断・予防策を脳神経内科医が解説。",
        "youtube_id": "GL9Tfw8wOpQ",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/14/063202",
        "source_dir": "入浴てんかん",
        "slide_prefix": "slide-",
        "pdf_filename": "bathing_epilepsy_slides.pdf",
        "slide_count": 9,
        "tags": ["てんかん", "意識消失", "高齢者"],
        "published_date": "2026-04-14",
    },
    {
        "slug": "stroke-acute-heparin",
        "title": "脳梗塞急性期のヘパリン、結局どう使う？",
        "subtitle": "1万単位 vs APTT管理・ブリッジング不要論・HIT対応",
        "description": "脳梗塞急性期のヘパリン使い分け：用量・モニタリング・HIT対応をガイドラインで整理。",
        "youtube_id": "WdGXFCNDaBo",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/22/135449",
        "source_dir": "脳梗塞急性期のヘパリン",
        "slide_prefix": "slide-",
        "pdf_filename": "脳梗塞急性期のヘパリン_スライド.pdf",
        "slide_count": 11,
        "tags": ["脳梗塞", "抗凝固", "医師向け"],
        "published_date": "2026-04-22",
    },
    {
        "slug": "sudden-weakness",
        "title": "突然手に力が入らない ― 脳？神経？筋肉？",
        "subtitle": "原因の見分け方｜その症状、大丈夫？ #03",
        "description": "急に手に力が入らないときの原因を脳・神経・筋肉の3階層で鑑別。",
        "youtube_id": "ldXs_bJaLnc",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/23/133800",
        "source_dir": "その症状大丈夫03_力が入らない",
        "slide_prefix": "slide-",
        "pdf_filename": "weakness_slides.pdf",
        "slide_count": 13,
        "tags": ["脱力", "脳神経内科", "症状チェック"],
        "published_date": "2026-04-23",
    },
    {
        "slug": "autonomic-dysfunction",
        "title": "「自律神経失調症」と言われたら",
        "subtitle": "本当の原因と正しい受診先｜その症状、大丈夫？ #06",
        "description": "「自律神経失調症」と診断されたとき、隠れた疾患を見逃さないための受診先選択。",
        "youtube_id": "6KkLHc5jnKM",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/27/212110",
        "source_dir": "その症状大丈夫06_自律神経",
        "slide_prefix": "slide-",
        "pdf_filename": "autonomic_nerves_slides.pdf",
        "slide_count": 13,
        "tags": ["自律神経", "脳神経内科", "症状チェック"],
        "published_date": "2026-04-27",
    },
    {
        "slug": "dysphagia-aging",
        "title": "「むせやすくなった」は老化のせい？",
        "subtitle": "嚥下障害の早期サインと受診の目安｜その症状、大丈夫？ #08",
        "description": "むせ・嚥下障害の早期発見と受診のタイミングを脳神経内科医が解説。",
        "youtube_id": "n1EWu3OqQ_g",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/30/145740",
        "source_dir": "その症状大丈夫08_嚥下障害",
        "slide_prefix": "slide-",
        "pdf_filename": "dysphagia_slides.pdf",
        "slide_count": 13,
        "tags": ["嚥下障害", "誤嚥", "症状チェック"],
        "published_date": "2026-04-30",
    },
    {
        "slug": "head-injury",
        "title": "頭をぶつけた後、病院に行くべき？",
        "subtitle": "48時間ルールと危険なサイン｜その症状、大丈夫？ #12",
        "description": "頭部外傷後の48時間以内に注意すべきサインと医療機関を受診すべき目安。",
        "youtube_id": "LuNdp9GhQBE",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/06/204047",
        "source_dir": "その症状大丈夫12_頭をぶつけた",
        "slide_prefix": "slide-",
        "pdf_filename": "head_injury_slides.pdf",
        "slide_count": 13,
        "tags": ["頭部外傷", "脳神経外科", "症状チェック"],
        "published_date": "2026-05-06",
    },
    {
        "slug": "weather-headache",
        "title": "雨の日に頭が痛くなる科学的理由",
        "subtitle": "気象病・片頭痛のメカニズムと最新治療｜その症状、大丈夫？ #13",
        "description": "天気の変化で頭痛が悪化する科学的メカニズムと、片頭痛の最新治療オプション。",
        "youtube_id": "4z3ameYH6T0",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/07/093954",
        "source_dir": "その症状大丈夫13_天気と頭痛",
        "slide_prefix": "slide-",
        "pdf_filename": "weather_headache_slides.pdf",
        "slide_count": 13,
        "tags": ["気象病", "片頭痛", "症状チェック"],
        "published_date": "2026-05-07",
    },
    {
        "slug": "taste-disorder",
        "title": "味がしない・味が変わった",
        "subtitle": "コロナだけじゃない味覚障害の原因と受診の目安｜その症状、大丈夫？ #14",
        "description": "味覚障害の原因（亜鉛欠乏・薬剤性・神経性など）と受診先の選び方。",
        "youtube_id": "pvcDfEEkyf4",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/09/070013",
        "source_dir": "その症状大丈夫14_味がわからない",
        "slide_prefix": "slide-",
        "pdf_filename": "taste_disorder_slides.pdf",
        "slide_count": 13,
        "tags": ["味覚障害", "症状チェック", "脳神経内科"],
        "published_date": "2026-05-09",
    },
    {
        "slug": "dementia-driving",
        "title": "認知症と運転免許",
        "subtitle": "家族が知っておくべき制度と説得のコツ｜その症状、大丈夫？ #19",
        "description": "認知症高齢者の運転免許更新制度と、家族としての対応・説得のコツ。",
        "youtube_id": "kklCC3UJaGA",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/20/082251",
        "source_dir": "その症状大丈夫19_認知症と運転",
        "slide_prefix": "slide-",
        "pdf_filename": "dementia_driving_clicks_split.pdf",
        "slide_count": 13,
        "tags": ["認知症", "高齢者", "運転免許"],
        "published_date": "2026-05-20",
    },
    {
        "slug": "brain-checkup",
        "title": "脳ドックは受けるべき？",
        "subtitle": "検査の意味と結果の活かし方｜その症状、大丈夫？ #20",
        "description": "脳ドックの検査内容・対象者・結果の解釈と、過剰検査を避けるための判断。",
        "youtube_id": "5i671IAa8qo",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/21/075558",
        "source_dir": "その症状大丈夫20_脳ドック",
        "slide_prefix": "slide-",
        "pdf_filename": "brain_dock_slides.pdf",
        "slide_count": 13,
        "tags": ["脳ドック", "予防医療", "症状チェック"],
        "published_date": "2026-05-21",
    },
    {
        "slug": "reiwa8-fee-revision",
        "title": "令和8年度診療報酬改定の全体像",
        "subtitle": "+3.09%改定の内訳と医科の主要変更点",
        "description": "令和8年度診療報酬改定の全体像。改定率の内訳・医科主要変更点を徹底解説。",
        "youtube_id": "__Xp5QYmZpw",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/10/141419",
        "source_dir": "令和8年度診療報酬改定",
        "slide_prefix": "slide-",
        "pdf_filename": "令和8年度診療報酬改定_スライド.pdf",
        "slide_count": 14,
        "tags": ["診療報酬", "2026改定", "医療政策"],
        "published_date": "2026-04-10",
    },
    # NEEDS_PNG (PNG生成済)
    {
        "slug": "migraine-basics",
        "title": "片頭痛持ちが知っておくべき5つのこと",
        "subtitle": "「我慢しない」ための知識｜からだの不思議",
        "description": "片頭痛と上手に付き合うために知っておくべき5つの基礎知識。",
        "youtube_id": "",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/02/192008",
        "source_dir": "からだの不思議02_片頭痛",
        "slide_prefix": "slide-",
        "pdf_filename": "片頭痛_スライド.pdf",
        "slide_count": 9,
        "tags": ["片頭痛", "頭痛"],
        "published_date": "2026-04-02",
    },
    {
        "slug": "yawn-contagion",
        "title": "なぜあくびはうつるのか？",
        "subtitle": "ミラーニューロンと共感の脳科学｜からだの不思議",
        "description": "あくびがうつる神経科学的メカニズムと共感の脳基盤。",
        "youtube_id": "TNuexPK3Dxo",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/06/071409",
        "source_dir": "からだの不思議06_あくび",
        "slide_prefix": "slide-",
        "pdf_filename": "あくび_スライド.pdf",
        "slide_count": 9,
        "tags": ["脳科学", "ミラーニューロン", "共感"],
        "published_date": "2026-04-06",
    },
    {
        "slug": "hypnic-jerk",
        "title": "寝る瞬間にビクッとなる原因",
        "subtitle": "入眠時ミオクローヌスとは何か・対処法・受診の目安｜からだの不思議",
        "description": "入眠時ミオクローヌス（hypnic jerk）の機序と病的ミオクローヌスとの鑑別。",
        "youtube_id": "9ITt6p-J7Ik",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/07/052718",
        "source_dir": "からだの不思議07_入眠時ミオクローヌス",
        "slide_prefix": "slide-",
        "pdf_filename": "入眠時ミオクローヌス_スライド.pdf",
        "slide_count": 9,
        "tags": ["睡眠", "ミオクローヌス", "脳科学"],
        "published_date": "2026-04-07",
    },
    {
        "slug": "hypoactive-delirium",
        "title": "低活動性せん妄 ― 「静かなせん妄」を見逃さない",
        "subtitle": "実践ガイド",
        "description": "低活動性せん妄の臨床像・スクリーニング・対処方針を実践的に整理。",
        "youtube_id": "",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/09/161517",
        "source_dir": "低活動性せん妄",
        "slide_prefix": "slide-",
        "pdf_filename": "低活動性せん妄.pdf",
        "slide_count": 11,
        "tags": ["せん妄", "高齢者", "医師向け"],
        "published_date": "2026-04-09",
    },
    {
        "slug": "deja-vu",
        "title": "デジャヴの正体を神経科学で解説",
        "subtitle": "\"既視感\"はなぜ起きるのか｜からだの不思議",
        "description": "デジャヴ現象の神経学的メカニズム（側頭葉てんかんとの違いを含む）。",
        "youtube_id": "dVni98076r4",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/09/135347",
        "source_dir": "からだの不思議09_デジャヴ",
        "slide_prefix": "slide-",
        "pdf_filename": "デジャヴ_スライド.pdf",
        "slide_count": 10,
        "tags": ["脳科学", "記憶", "側頭葉"],
        "published_date": "2026-04-09",
    },
    {
        "slug": "dangerous-headache",
        "title": "この頭痛、病院に行くべき？",
        "subtitle": "危険な頭痛の見分け方｜からだの不思議",
        "description": "危険な頭痛（くも膜下出血・髄膜炎など）と一次性頭痛との鑑別ポイント。",
        "youtube_id": "f6hSRaATvtw",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/13/182624",
        "source_dir": "からだの不思議13_危険な頭痛",
        "slide_prefix": "slide-",
        "pdf_filename": "危険な頭痛_スライド.pdf",
        "slide_count": 9,
        "tags": ["頭痛", "くも膜下出血", "症状チェック"],
        "published_date": "2026-04-13",
    },
    {
        "slug": "stumbling",
        "title": "「最近つまずきやすい」は脳の問題？",
        "subtitle": "歩行とつまずきの原因を解剖学レベルで解説｜からだの不思議 #15",
        "description": "つまずきやすさの背景にある神経・筋・骨関節の問題を解剖学的に整理。",
        "youtube_id": "",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/15/104135",
        "source_dir": "からだの不思議15_つまずき",
        "slide_prefix": "slide-",
        "pdf_filename": "つまずき_スライド.pdf",
        "slide_count": 9,
        "tags": ["歩行", "高齢者", "脳神経内科"],
        "published_date": "2026-04-15",
    },
    {
        "slug": "hypertension-2025",
        "title": "高血圧の新基準（2025年）と減塩対策",
        "subtitle": "130/80mmHg時代の診療と日本人の3人に1人",
        "description": "高血圧の2025年新基準（130/80mmHg）と日常の減塩対策・薬物療法。",
        "youtube_id": "pNiyz5WfJ7w",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/04/17/063136",
        "source_dir": "高血圧",
        "slide_prefix": "slide-",
        "pdf_filename": "高血圧_スライド.pdf",
        "slide_count": 10,
        "tags": ["高血圧", "循環器", "減塩"],
        "published_date": "2026-04-17",
    },
    {
        "slug": "migraine-update-2026",
        "title": "片頭痛診療アップデート2026",
        "subtitle": "トリプタン・ジタン・ゲパント・抗CGRP抗体の使い分け完全ガイド",
        "description": "片頭痛急性期治療と予防療法の最新アルゴリズム。抗CGRP抗体までの使い分け。",
        "youtube_id": "bZXS9GON-NA",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/04/033758",
        "source_dir": "片頭痛診療アップデート2026",
        "slide_prefix": "slide-",
        "pdf_filename": "片頭痛診療アップデート2026_slides.pdf",
        "slide_count": 18,
        "tags": ["片頭痛", "抗CGRP抗体", "医師向け"],
        "published_date": "2026-05-04",
    },
    {
        "slug": "barnum-effect",
        "title": "「バーナム効果」の正しい使い方",
        "subtitle": "日常診療と人間関係に活かす心理テクニック",
        "description": "バーナム効果（誰にでも当てはまる記述を自分のことと感じる現象）の臨床応用。",
        "youtube_id": "J0GG8ubkLl4",
        "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/05/20/084057",
        "source_dir": "バーナム効果",
        "slide_prefix": "slide-",
        "pdf_filename": "バーナム効果_スライド.pdf",
        "slide_count": 10,
        "tags": ["心理学", "コミュニケーション", "医師向け"],
        "published_date": "2026-05-20",
    },
]


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    existing_slugs = {d["slug"] for d in manifest["decks"]}
    existing_blogs = {d.get("blog_url", "") for d in manifest["decks"]}

    added = 0
    for d in NEW_DECKS:
        if d["slug"] in existing_slugs:
            print(f"  [SKIP-DUP-SLUG] {d['slug']}")
            continue
        if d.get("blog_url") and d["blog_url"] in existing_blogs:
            print(f"  [SKIP-DUP-BLOG] {d['slug']} -> {d['blog_url']}")
            continue
        manifest["decks"].append(d)
        existing_slugs.add(d["slug"])
        existing_blogs.add(d.get("blog_url", ""))
        added += 1
        print(f"  [ADD] {d['slug']}")

    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    print(f"\n{added} decks added. Total: {len(manifest['decks'])}")


if __name__ == "__main__":
    main()
