# -*- coding: utf-8 -*-
"""manifest.json に 抗てんかん発作薬の作用機序と合理的多剤併用（医師向け）deck を追加する（既存なら更新）。

2026-10-11：パーキンソン病と遺伝子異常（_add_parkinson_genetics_deck.py）と同じ型。スライド・PDFは
medical-content/youtube-slides/asm-mechanism-polytherapy/work/rc6-20261011h/viewer/generated/ に整えてある
（slide_01〜20.png＝deck-motion-v2.html を export_deck_slides.py で書き出したもの、slides.pdf＝同じ書き出し）。
公開前の下書き。medical-ddx-tools/slides/ に置いて実行するのは、先生の公開承認のあと。
公開後に youtube_id・blog_url・published_date を実値にして実行し、_template/build.py --slug asm-mechanism-polytherapy を回す。
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MANIFEST = Path(__file__).parent / "manifest.json"

DECK = {
    "slug": "asm-mechanism-polytherapy",
    "title": "抗てんかん発作薬（ASM）の作用機序と合理的多剤併用｜Naチャネル・SV2A・GABA・AMPAの図解と、2剤目を考えるときの根拠【医師向け】",
    "subtitle": "作用機序の全体像・Naチャネル・シナプス前終末・GABA系・グルタミン酸系・T型Ca・単剤の成績・相乗と拮抗・組み合わせの根拠・2剤目の考え方（医師向け）",
    "description": "抗てんかん発作薬の作用機序と合理的多剤併用を、医師向けに模式図で整理します。作用は大きく、イオンチャネル、GABAによる抑制の増強、シナプスの放出機構、グルタミン酸受容体の4つの群に分けられ、1つの薬が複数の群にまたがることや、作用機序が分かっていない薬もあります。グラスゴーで新しく診断された1795人を30年追った研究では、最終的に発作が止まった人の86.8%は単剤で止まっていました。観察研究では機序の違う組み合わせのほうが長く続けられていましたが、続いたことは効いたことと同じではなく、機序の違う薬を組み合わせると効きやすいという考えは主に動物実験からの知見です。総説によると、相乗効果が示された組み合わせはバルプロ酸とラモトリギンだけです。Naチャネル遮断薬を重ねるときは神経毒性に注意します。全20枚のスライドで説明します。",
    "youtube_id": "gxXwoDWKvoA",
    "blog_url": "https://blog.ichisouzo-lab.com/entry/2026/10/12/000954",
    "source_dir": "asm-mechanism-polytherapy/work/rc6-20261011h/viewer/generated",
    "slide_prefix": "slide_",
    "pdf_filename": "slides.pdf",
    "slide_count": 20,
    "tags": ["抗てんかん発作薬", "抗てんかん薬", "作用機序", "合理的多剤併用", "Naチャネル", "SV2A", "てんかん", "脳神経内科", "医師向け"],
    "published_date": "2026-10-11",
    "viewer_notice": "医師向けの情報整理です。個々の診療の判断に代わるものではありません。機序の違う薬を組み合わせると効きやすいという考えは主に動物実験からの知見で、ヒトでの決定的な証拠はまだありません。図は文献をもとに作成した模式図で、実際の縮尺や実測値ではないものを含みます。用量・併用は最新の電子添文をご確認ください。内容は2026年10月11日時点の論文・電子添文・公的資料に基づきます。",
    "html_deck": False,
    "infographic": False
}


def main() -> None:
    if "TBD" in (DECK["youtube_id"], DECK["blog_url"], DECK["published_date"]):
        sys.exit("TBD が残っています（公開後に実値を入れてから実行する）。")
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
