# -*- coding: utf-8 -*-
"""manifest.json に 飲酒と認知症（認知症×生活習慣病シリーズ第7弾）deck を追加する（既存なら更新）。"""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "dementia-alcohol",
    "title": "「少量のお酒は脳にいい」は本当か——飲酒と認知症、調べ方で答えが変わる理由",
    "subtitle": "発症率を追うとJカーブ｜脳の画像と遺伝は少量の保護を支持していない｜一致するのは「多く飲むほど不利」という側だけ",
    "description": (
        "「少量なら脳に良い」という話と、「少しでも脳には悪い」という話が、どちらも研究の結果として流れています。"
        "食い違って見えるのは、何を測ったかが違うからです。"
        "発症率を追った観察研究は繰り返しJカーブを出し、17研究・認知症80,680人の用量反応メタ解析では"
        "1日1〜17.5 gで RR 0.92（0.88–0.96）、17.5 gを超えると RR 1.23（1.09–1.35）でした。"
        "一方、30年追跡の脳MRI研究（550人）では、少量飲酒に非飲酒を上回る保護効果は認められず、"
        "週240 g超で海馬萎縮 OR 5.8（1.8–18.6）。UKバイオバンク36,678人では全脳容積・灰白質容積との負の関連が"
        "1日平均1〜2 unitsの人ですでに認められています。"
        "遺伝の情報を使ったメンデルランダム化では、飲酒量・アルコール依存・AUDITのいずれについても"
        "遅発性アルツハイマー病との因果的関連を示す証拠は得られていません。"
        "食い違いの一因は「飲まない人」に体を悪くしてやめた人が混ざることで、"
        "日本のJPHC研究（42,870人・平均14.9年）では長期の非飲酒 HR 1.61（1.28–2.03）に対し断酒者 2.54（1.93–3.35）。"
        "ただし60歳超15研究の個人データ（24,478人）では生涯非飲酒者と断酒者に差を認めず（HR 0.98, 0.81–1.18）、"
        "逆因果だけで全部を説明することもできません。"
        "厚生労働省ガイドラインの男性40 g・女性20 gは「飲んでよい量」ではなく、"
        "同ガイドラインが「これらの量は個々人の許容量を示したものではありません」と明記しています。"
        "扱う研究はほとんどが観察研究で、飲酒を割り付けた認知症の予防試験は倫理的に実施できないため存在しません。"
        "「少量なら脳に良い」ことも「やめれば認知症を防げる」ことも、証明されてはいません。"
        "認知症×生活習慣病シリーズ第7弾／全18スライド。医師・一般の両方に向けた内容です。"
    ),
    "source_dir": "飲酒と認知症/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 18,
    "tags": [
        "飲酒", "認知症", "お酒", "アルコール", "Jカーブ", "純アルコール量",
        "認知症予防", "生活習慣病", "コホート研究", "メンデルランダム化", "脳神経内科",
    ],
    "published_date": "2026-08-16",
    "viewer_notice": (
        "本資料は一般的な医療情報であり、個別の診断・治療に代わるものではありません。"
        "ここで扱った研究はほとんどが観察研究で、少量の飲酒が脳を守ることも、"
        "やめれば認知症を防げることも証明されてはいません。"
        "すでに毎日飲んでいる方、依存が疑われる方が自己判断で急にやめると離脱症状で危険なことがあります。"
        "減らし方や中止の可否は必ず主治医とご相談ください。"
    ),
    "html_deck": True,
    "infographic": True,
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
    # manifest.json は LF のみ。Windows の text mode 既定だと CRLF に化けて全行 diff になるので newline="" を明示する
    with open(MANIFEST, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(m, ensure_ascii=False, indent=2) + "\n")
    print("decks:", len(decks))


if __name__ == "__main__":
    main()
