# -*- coding: utf-8 -*-
"""根拠修復バッチ22の2記事（帯状疱疹ワクチン比較・ベンゾジアゼピン離脱）のインフォ原寸ページを作る。
2026-10-22 先生指示「この2枚で進めてください。fotolifeへのアップロード、toolsの拡大ページの公開、修正版への埋め込みと検査までをお願いします」。
infographic.png は medical-content/blog/reference-repair/20261004/articles/<slug>/infographic/generated/ の確定版の複製。
続けて add_nav_and_image.py --no-png --only <slug>・build_index.py --no-thumb・sw.js・check_sw_cache.py。
"""
import json, shutil, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "medical-content/blog/reference-repair/20261004/articles"
ITEMS = [
    dict(slug="herpes-zoster-vaccine-comparison", png="herpes-zoster-vaccine-comparison/infographic/generated/hz_vaccine_infographic_v3.png",
         title="50歳からの帯状疱疹予防", sub="シングリックスとビケンの違い", audience="一般向け",
         desc="2つのワクチンの違い、予防効果の続き方、副反応、受けられる人・受けられない人、2025年度からの定期接種までを1枚に整理（一般向け）",
         blog_url="https://blog.ichisouzo-lab.com/entry/2025/11/14/193519",
         alt="50歳からの帯状疱疹予防。帯状疱疹は50歳代から増えて70歳代で最も多く、治った後も痛みが残ることがある。シングリックスはウイルスの成分を使い筋肉内に2回、ビケンは弱めた生きたウイルスで皮下に1回接種する。厚生労働省のまとめによる予防効果の目安は、シングリックスが1年で9割以上、5年で9割程度、10年で7割程度、ビケンが1年で6割程度、5年で4割程度。副反応はシングリックスで注射部位の痛みや全身の症状が出やすく、ビケンは主に注射部位の赤みやかゆみ。シングリックスは免疫が低下していても受けられるが、ビケンは免疫が低下している人や妊娠中の人は受けられない。2025年度から定期接種となり、65歳を迎える方などがどちらか1種類を受ける。費用や実施期間は市区町村に確認し、医師と相談して選ぶ。"),
    dict(slug="benzodiazepine-withdrawal", png="benzodiazepine-withdrawal/infographic/generated/bzd_withdrawal_infographic_v1.png",
         title="ベンゾジアゼピン離脱症状とその対策", sub="医療従事者向けガイド", audience="医療従事者向け",
         desc="離脱症状と出現時期、ゆっくり減らす漸減の目安、発作リスクのある人と高齢者への注意、減薬を支える方法を1枚に整理（医療従事者向け）",
         blog_url="https://blog.ichisouzo-lab.com/entry/2026/02/03/011211",
         alt="ベンゾジアゼピン離脱症状とその対策。長く使った後の減量・中止で、不安・不眠・振戦・発汗などが起こり、急な中止ではけいれん発作やせん妄も起こりうる。症状は短時間作用型で中止後2日以内、長時間作用型で4〜7日以内に出て、長期使用者では数か月続くこともある。米国の共同ガイドライン（2025）は急に中止せず、はじめは2〜4週ごとに5〜10%ずつ、2週間で25%を超えない目安で減らし、身体依存が強い人はさらにゆっくりを検討し、強い症状が出たら減量を遅らせるか止めるとしている。発作リスクがある人は減量をより遅くすることを検討し、発作時の対応を前もって決め、入院下の減薬も検討する。高齢者は続ける強い理由がなければ多くの人で漸減を勧め、転倒やせん妄に注意する。減薬はCBTや睡眠衛生で支え、補助薬の根拠は限られ、計画を患者と共有し、数か月から数年かかることもある。"),
]
TPL = ('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}｜図で読むポイント</title><style>body{{margin:0;background:#eef6f8;color:#0d3f7a;font-family:Meiryo,sans-serif;line-height:1.8}}main{{max-width:1080px;width:100%;margin:auto}}header,footer{{padding:24px;text-align:center}}section{{margin:0 0 28px}}img{{display:block;width:100%;height:auto}}a{{color:#0e7c86}}</style>\n</head><body>\n'
       '<main><header class="hd"><h1>{title}</h1><p>{sub}</p></header><section><a href="infographic.png" title="画像のみを原寸で開く"><img src="infographic.png" alt="{alt}"></a></section><footer><p>医知創造ラボ｜監修：今村久司</p><p>内容は2026年10月22日時点の資料に基づきます。図はAI画像生成を用いて制作し、文言を解説記事と照合しています。個別の診療判断に代わるものではありません。<br><a href="{blog_url}">解説記事を読む</a></p></footer></main>\n</body></html>\n')
manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
for it in ITEMS:
    if len(sys.argv) > 1 and it["slug"] not in sys.argv[1:]: continue
    d = HERE / it["slug"]; d.mkdir(exist_ok=True)
    shutil.copyfile(SRC / it["png"], d / "infographic.png")
    (d / "index.html").write_text(TPL.format(**it), encoding="utf-8")
    item = dict(slug=it["slug"], title=it["title"], desc=it["desc"], audience=it["audience"], blog_url=it["blog_url"], date="2026-10-22", youtube_id="")
    items = manifest["items"]; idx = next((i for i, x in enumerate(items) if x["slug"] == it["slug"]), None)
    if idx is None: items.insert(0, item)
    else: items[idx] = item
    print("page:", it["slug"])
(HERE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
