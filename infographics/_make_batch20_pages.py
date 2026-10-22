# -*- coding: utf-8 -*-
"""根拠修復バッチ20の2記事（MGクリーゼ・無菌性髄膜炎）のインフォ原寸ページを作る。
2026-10-22 先生指示「インフォグラフィックをCodexの画像生成で作成して埋め込んでください」。
infographic.png は medical-content/blog/reference-repair/20261004/articles/<slug>/infographic/generated/ の確定版の複製。
続けて manifest 追加・add_nav_and_image.py --no-png --only <slug>・build_index.py --no-thumb・sw.js・check_sw_cache.py。
"""
import json, shutil, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "medical-content/blog/reference-repair/20261004/articles"
ITEMS = [
    dict(slug="mg-crisis", png="mg-crisis/infographic/generated/mg_crisis_infographic_v2.png",
         title="重症筋無力症クリーゼ", sub="ガイドラインに基づく診断と治療（医師向け）",
         desc="クリーゼとは、初期対応、呼吸管理（NIV・挿管・抜管）、血漿浄化療法とIVIG、再発予防と長期管理までを1枚に整理（医師向け）",
         blog_url="https://blog.ichisouzo-lab.com/entry/2025/12/08/051011",
         alt="重症筋無力症クリーゼの全体像。クリーゼは呼吸不全で人工呼吸が必要な状態で、誘因は感染が最多だが不明のこともある。初期対応はICUで呼吸を監視し、悪化に関与しうる薬を見直し、抗コリンエステラーゼ薬は中止を考える。呼吸管理では高二酸化炭素血症が進む前にNIVを試み、球麻痺では誤嚥に注意する。挿管の目安は日本のガイドラインで肺活量15 mL/kg以下で、予定した挿管が望ましい。抜管は筋力と嚥下の回復後。急性期の免疫治療は血漿浄化療法とIVIGを併存症で選び、MuSK抗体陽性では血漿浄化療法、ステロイド併用は初期増悪に注意する。再発予防は維持免疫療法、胸腺病変への対応、感染予防と薬の確認、新しい分子標的薬は国内の適用条件がある。"),
    dict(slug="aseptic-meningitis-treatment", png="aseptic-meningitis-treatment/infographic/generated/meningitis_infographic_v3.png",
         title="無菌性髄膜炎の診療", sub="見逃さない疾患の除外から原因別の治療まで（医師向け）",
         desc="細菌性髄膜炎と単純ヘルペス脳炎を見逃さない初期治療、髄液検査・MRI・多項目PCR、原因別の治療、低Na血症、予後を1枚に整理（医師向け）",
         blog_url="https://blog.ichisouzo-lab.com/entry/2025/09/25/094947",
         alt="無菌性髄膜炎の診療の流れ。培養で細菌・真菌が検出されない髄膜炎で、最多の原因はウイルス。まず細菌性髄膜炎（検査から抗菌薬まで1時間以内）と単純ヘルペス脳炎（受診後6時間以内にアシクロビル）を見逃さず、結果を待たずに治療を始める。診断は髄液検査・頭部MRI・多項目PCRで、陰性でも否定できず培養も必要。原因別の治療は、ウイルス性は対症療法、HSV・VZVはアシクロビル、結核性は抗結核薬4剤とステロイド、クリプトコッカスは抗真菌薬の導入・地固め・維持、薬剤性は原因薬の中止。合併症の低ナトリウム血症（とくに結核性）ではCSWとSIADHを見分け、結核性では水制限を避ける。予後はウイルス性の多くが後遺症なく回復し、結核性・真菌性は重篤で長期のフォローが必要。"),
]
TPL = ('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}｜図で読むポイント</title><style>body{{margin:0;background:#eef6f8;color:#0d3f7a;font-family:Meiryo,sans-serif;line-height:1.8}}main{{max-width:1080px;width:100%;margin:auto}}header,footer{{padding:24px;text-align:center}}section{{margin:0 0 28px}}img{{display:block;width:100%;height:auto}}a{{color:#0e7c86}}</style>\n</head><body>\n'
       '<main><header class="hd"><h1>{title}</h1><p>{sub}</p></header><section><a href="infographic.png" title="画像のみを原寸で開く"><img src="infographic.png" alt="{alt}"></a></section><footer><p>医知創造ラボ｜監修：今村久司</p><p>内容は2026年10月22日時点の資料に基づきます。図はAI画像生成を用いて制作し、文言を解説記事と照合しています。個別の診療判断に代わるものではありません。<br><a href="{blog_url}">解説記事を読む</a></p></footer></main>\n</body></html>\n')
manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
for it in ITEMS:
    if len(sys.argv) > 1 and it["slug"] not in sys.argv[1:]: continue
    d = HERE / it["slug"]; d.mkdir(exist_ok=True)
    shutil.copyfile(SRC / it["png"], d / "infographic.png")
    (d / "index.html").write_text(TPL.format(**it), encoding="utf-8")
    item = dict(slug=it["slug"], title=it["title"], desc=it["desc"], audience="医師向け", blog_url=it["blog_url"], date="2026-10-22", youtube_id="")
    items = manifest["items"]; idx = next((i for i, x in enumerate(items) if x["slug"] == it["slug"]), None)
    if idx is None: items.insert(0, item)
    else: items[idx] = item
    print("page:", it["slug"])
(HERE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
