# -*- coding: utf-8 -*-
"""manifest.json に ICIによる筋炎（irAE筋炎・医師向け）deck を追加する（既存なら更新）。

2026-10-13：_add_anti_aging_gh_dhea_deck.py と同じ型。スライド・PDF・インフォは
medical-content/youtube-slides/irae-myositis/work/rc6-20261013e/viewer/ に整えてある
（slide_01〜16.png・slides.pdf＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、infographic.png＝publishing の複製）。
先生指示「公開の作業をすすめてください。ブログは公開、動画は限定公開でお願いします。」
動画 xXp9DywlVu0（限定公開）。blog_url は公開後に実値を入れて再実行し、_template/build.py --slug irae-myositis を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "irae-myositis",
    "title": "免疫チェックポイント阻害薬による筋炎を見逃さない：心筋炎・重症筋無力症の合併（医師向け）",
    "subtitle": "頻度と時期・MGに似た症状・合併と死亡・疑ったときの検査・治療と再投与（医師向け）",
    "description": "免疫チェックポイント阻害薬（ICI）による筋炎を、脳神経内科医向けに整理します。頻度はICIを受けた人の0.2〜0.4%と高くありませんが、ICIを始めて1か月ほどで起こり、眼瞼下垂などMGに似た症状や、飲み込み・呼吸の障害を伴いやすい病気です。亡くなる人の多くは、心筋炎かMGを合併した例です。どれか1つを疑ったら3つとも調べ、CKが正常でも筋炎は否定しません。トロポニンTは筋の病気でも上がるので、トロポニンIや心電図、心臓MRIも合わせて判断します。治療の柱はICIの中止とステロイドです。全16枚のスライドで説明します。",
    "youtube_id": "xXp9DywlVu0",
    "blog_url": "",
    "source_dir": "irae-myositis/work/rc6-20261013e/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 16,
    "tags": [
        "免疫チェックポイント阻害薬",
        "irAE",
        "筋炎",
        "心筋炎",
        "重症筋無力症",
        "医師向け"
    ],
    "published_date": "2026-10-13",
    "viewer_notice": "医師向けの医学情報です。個々の患者さんの診断や治療方針は、担当の医師の判断によります。数値は、どの集団を分母にしたものかで大きく変わります（スライドの注記と記事の参考文献をご覧ください）。治療の推奨は2021年のSITCのガイドラインにもとづき、その多くは比較試験ではなく専門家の合意です。内容は2026年10月13日時点の文献と国内の添付文書に基づきます。",
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
