# -*- coding: utf-8 -*-
"""manifest.json に 低血糖脳症の画像と予後（医師向け）deck を追加する（既存なら更新）。

2026-10-16：_add_irae_myositis_deck.py と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/hypoglycemic-encephalopathy/work/rc6-20261015d/viewer/ に整えてある
（slide_01〜19.png・slides.pdf＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、infographic.png＝publishing の複製）。
7・9・10・11枚目の MRI は CC BY 4.0 の症例報告の図（出典と改変をスライドのフッターに表示）。
先生指示「ブログは公開、Youtubeは限定公開」。
動画 kp94SIZhoME（限定公開）。blog_url は公開後に実値を入れて再実行し、_template/build.py --slug hypoglycemic-encephalopathy を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "hypoglycemic-encephalopathy",
    "title": "低血糖脳症の画像と予後：ブドウ糖で意識が戻らないとき（医師向け）",
    "subtitle": "どの血糖から・神経細胞が死ぬ仕組み・片麻痺で来る低血糖・MRIの病変と予後・持続時間と脳波・初期対応（医師向け）",
    "description": "低血糖脳症を、脳神経内科医向けに整理します。ADAの分類では54 mg/dL未満で神経糖欠乏症状が出始めます。片麻痺で来る低血糖では、DWIで内包に高信号が出て脳梗塞に似ることがあり、片麻痺でもまず血糖を測ります。MRIに異常がない人や内包の小さな病変の人は回復しやすく、広い皮質や線条体の病変は転帰が悪いことが多いですが、病変の場所は撮影の時期で変わる可能性があり、画像だけで予後は決められません。低血糖が何時間続くと後遺症が残るという境目は、ヒトでは確認できませんでした。症例報告に載っている実際のMRI画像（CC BY 4.0）も紹介します。全19枚のスライドで説明します。",
    "youtube_id": "kp94SIZhoME",
    "blog_url": "",
    "source_dir": "hypoglycemic-encephalopathy/work/rc6-20261015d/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 19,
    "tags": [
        "低血糖脳症",
        "低血糖",
        "MRI",
        "意識障害",
        "脳神経内科",
        "医師向け"
    ],
    "published_date": "2026-10-16",
    "viewer_notice": "医師向けの医学情報です。個々の患者さんの診断や治療方針は、担当の医師の判断によります。予後の研究は少人数で、研究ごとに転帰を見た時期が違います（スライドの注記と記事の参考文献をご覧ください）。7・9・10・11枚目のMRIは、CC BY 4.0 の症例報告の図を並べ替え、見出しを加えたものです。内容は2026年10月15日時点の文献に基づきます。",
    "html_deck": False,
    "infographic": True
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
