# -*- coding: utf-8 -*-
"""根拠修復バッチ23の2記事（外転神経麻痺・寝違え）のインフォ原寸ページを作る。
2026-10-22 先生指示「2枚とも確定です。fotolife へのアップロード、tools の infographics ページ作成、revised.html の差し替えとゲートの再実行まで進めてください。」。
infographic.png は medical-content/blog/reference-repair/20261004/articles/<slug>/infographic/generated/ の確定版の複製。
続けて add_nav_and_image.py --no-png --only <slug>・build_index.py --no-thumb・sw.js・check_sw_cache.py。
"""
import json, shutil, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
SRC = HERE.parents[1] / "medical-content/blog/reference-repair/20261004/articles"
ITEMS = [
    dict(slug="abducens-palsy", png="abducens-palsy/infographic/generated/infographic_v2.png",
         title="外転神経麻痺の原因を見極める", sub="成人の単独の眼球運動神経麻痺のなかで最も多い", audience="医師向け",
         desc="現れ方、主な原因、MRIによる評価が勧められる場合、見逃さない鑑別（Tolosa-Hunt症候群・巨細胞性動脈炎・重症筋無力症・甲状腺眼症）、経過観察を1枚に整理（医師向け）",
         blog_url="https://blog.ichisouzo-lab.com/entry/2025/06/03/034217",
         alt="外転神経麻痺の原因を見極める。成人の単独の眼球運動神経麻痺のなかで最も多い。右の外転神経麻痺で右を見ようとすると、患側の眼球が外転できず、水平方向の二重視が患側を見たときに強くなる。主な原因は微小血管障害（糖尿病や高血圧）、腫瘍による圧迫（髄膜腫・転移性腫瘍）、炎症性疾患（Tolosa-Hunt症候群）、感染症（髄膜炎・Gradenigo症候群）、その他（脳幹梗塞・出血、多発性硬化症、頭蓋内圧亢進による偽局在徴候）で、痛みの有無では原因を区別できない。50歳未満、リスク因子が無い例、他の神経症状を伴う例、症状が進行性である例ではMRIによる評価が勧められ、複数の脳神経麻痺では急いで神経画像検査を行う。50歳以上で血管危険因子がある場合の扱いは意見が分かれており、前向き研究は初期評価でMRIと血液検査を行う意義を示した。見逃さない鑑別はTolosa-Hunt症候群（眼窩部の痛みが先行し、ステロイドで痛みと麻痺が改善）、巨細胞性動脈炎（高齢者、赤沈・CRP）、厳密には神経麻痺ではない重症筋無力症（症状が変動し易疲労性）と甲状腺眼症（牽引試験で受動的にも外転できない）。経過中に悪化や新たな症状があれば再評価し、6か月を過ぎても複視が残れば斜視手術を検討する。"),
    dict(slug="acute-neck-pain", png="acute-neck-pain/infographic/generated/infographic_v2.png",
         title="寝違え（急性の首の痛み）", sub="安全な対処法と受診の目安", audience="一般向け",
         desc="寝違えの症状、はじめのセルフケアと動かし始める目安、整形外科を受診する場合、すぐに受診・救急に向かうべき症状を1枚に整理（一般向け）",
         blog_url="https://blog.ichisouzo-lab.com/entry/2026/02/24/185136",
         alt="寝違え（急性の首の痛み）、安全な対処法と受診の目安。起床時に首の後ろから肩が痛み、首を動かすと痛む・動かせない。多くは軽症。まずはセルフケアで、はじめは痛い方向に無理に動かさず、数時間から数日で和らいでいくなら徐々に首を動かしていく。消炎鎮痛薬の貼り薬・塗り薬、必要に応じて短期間の内服鎮痛薬を使い、痛みが増えるやり方は避ける。痛みが強い・治らないときは整形外科へ。首が裂けるような痛み・頭痛、ものが二重に見える、めまい・失神、片側の手足の脱力やしびれといった血管の病気を疑う症状は、ためらわず救急へ。発熱や寝汗、発熱とともに首を前に曲げられない、外傷（転倒・事故など）のあと、がんの既往、手足のしびれ・力が入りにくい、歩きにくさ・排尿排便の異常が一部でも当てはまれば早めに受診する。"),
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
