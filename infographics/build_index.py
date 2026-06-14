#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""インフォグラフィック一覧（ギャラリー）ページを manifest.json から生成する。

  1. 各 <slug>/index.html の .hd（ヘッダー）を <slug>/thumb.png に書き出し（サムネ）
  2. infographics/index.html を生成（検索ボックス＋カードグリッド）

実行:
  python build_index.py            # サムネ生成 + index.html 生成
  python build_index.py --no-thumb # index.html のみ再生成（サムネ据え置き）
"""
import argparse, html, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RENDER = HERE.parent.parent / "medical-content" / "youtube-slides" / "_shared_scripts" / "render_html_to_png.py"


def render_thumbs():
    items = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["items"]
    for it in items:
        src = HERE / it["slug"] / "index.html"
        out = HERE / it["slug"] / "thumb.png"
        if not src.exists():
            print("  [skip] no index:", it["slug"]); continue
        r = subprocess.run([sys.executable, str(RENDER), "--html", str(src), "--out", str(out),
                            "--selector", ".hd", "--dsf", "1"], capture_output=True, text=True, encoding="utf-8")
        print("  thumb:", it["slug"], "OK" if out.exists() else "FAIL", (r.stderr or "").strip()[:120])


def build_index():
    items = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["items"]
    cards = []
    for it in items:
        s = it["slug"]; t = html.escape(it["title"]); d = html.escape(it.get("desc", ""))
        aud = html.escape(it.get("audience", "")); date = html.escape(it.get("date", ""))
        blog = it.get("blog_url", "")
        search = html.escape("{} {} {}".format(it["title"], it.get("desc", ""), it.get("audience", "")))
        aud_cls = "aud-pro" if "医療" in it.get("audience", "") else "aud-gen"
        thumb = "{}/thumb.png".format(s) if (HERE / s / "thumb.png").exists() else ""
        thumb_html = ('<a class="thumb" href="{s}/" aria-label="{t}"><img src="{th}" alt="{t} サムネイル" loading="lazy"></a>'.format(s=s, t=t, th=thumb)
                      if thumb else '<a class="thumb thumb--noimg" href="{s}/">✚</a>'.format(s=s))
        blog_link = '<a class="lnk" href="{b}" target="_blank" rel="noopener">解説記事</a>'.format(b=html.escape(blog)) if blog else ""
        cards.append(
            '  <article class="card" data-search="{sr}">\n'
            '    {th}\n'
            '    <div class="body">\n'
            '      <h2 class="title"><a href="{s}/">{t}</a></h2>\n'
            '      <p class="desc">{d}</p>\n'
            '      <div class="meta"><span class="tag {ac}">{aud}</span><span class="date">{date}</span></div>\n'
            '      <div class="links"><a class="lnk lnk--main" href="{s}/">📊 図を開く</a>{bl}</div>\n'
            '    </div>\n'
            '  </article>'.format(sr=search, th=thumb_html, s=s, t=t, d=d, ac=aud_cls, aud=aud, date=date, bl=blog_link))
    grid = "\n".join(cards)
    tpl = TEMPLATE.replace("<!--CARDS-->", grid).replace("<!--COUNT-->", str(len(items)))
    (HERE / "index.html").write_text(tpl, encoding="utf-8", newline="\n")
    print("index.html 生成: {} 件".format(len(items)))


TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#1A5276">
<meta name="description" content="医学教育インフォグラフィック一覧。診断・治療・生活のポイントを1枚にまとめた、拡大しても鮮明なHTML図解集。医療従事者向け・一般向け。">
<title>インフォグラフィック一覧｜医知創造ラボ</title>
<style>
  :root{--navy:#1A5276;--navy-ink:#10324a;--blue:#2C5AA0;--accent:#FF7A59;--bg:#F4F6F8;--white:#fff;--text:#222;--muted:#667;--line:#e2e8ef;--shadow:0 2px 12px rgba(16,50,74,.12);--radius:12px;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:"Hiragino Kaku Gothic ProN","Yu Gothic","Segoe UI",sans-serif;background:var(--bg);color:var(--text);min-height:100vh;padding:0 0 60px;line-height:1.6;}
  header{background:linear-gradient(135deg,var(--navy-ink),var(--blue));color:#fff;padding:42px 20px 34px;text-align:center;box-shadow:0 4px 16px rgba(16,50,74,.18);position:relative;overflow:hidden;}
  header::after{content:"";position:absolute;right:-80px;top:-80px;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle at 30% 30%,rgba(255,122,89,.45),transparent 65%);}
  header .brand{font-size:.9em;font-weight:700;opacity:.9;}
  header .brand .cross{color:var(--accent);}
  header h1{font-size:1.8em;font-weight:800;letter-spacing:.02em;margin-top:8px;}
  header p{font-size:.95em;margin-top:10px;opacity:.9;}
  .container{max-width:1000px;margin:0 auto;padding:26px 16px;}
  .search-box{position:relative;margin-bottom:14px;}
  .search-input{width:100%;padding:12px 14px 12px 42px;border:2px solid #d1d5db;border-radius:var(--radius);font-size:1em;font-family:inherit;background:#fff;box-shadow:var(--shadow);outline:none;}
  .search-input:focus{border-color:var(--blue);}
  .search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#9aa7b4;}
  .count{font-size:.84em;color:var(--muted);margin:0 2px 16px;}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:18px;}
  .card{background:#fff;border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow);display:flex;flex-direction:column;transition:transform .12s,box-shadow .12s;}
  .card:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(16,50,74,.18);}
  .thumb{display:block;aspect-ratio:16/9;overflow:hidden;background:linear-gradient(135deg,var(--navy-ink),var(--blue));}
  .thumb img{width:100%;height:100%;object-fit:cover;object-position:top;display:block;}
  .thumb--noimg{display:flex;align-items:center;justify-content:center;color:#fff;font-size:2em;text-decoration:none;}
  .body{padding:15px 17px;flex:1;display:flex;flex-direction:column;}
  .title{font-size:1.04em;font-weight:800;color:var(--navy);line-height:1.4;}
  .title a{color:inherit;text-decoration:none;}
  .title a:hover{text-decoration:underline;}
  .desc{font-size:.85em;color:#556;line-height:1.55;margin-top:7px;flex:1;}
  .meta{display:flex;gap:9px;align-items:center;margin-top:11px;flex-wrap:wrap;}
  .tag{font-size:.74em;font-weight:700;border-radius:999px;padding:3px 11px;}
  .aud-gen{background:#fdeee9;color:#c2410c;}
  .aud-pro{background:#e8f2fb;color:var(--blue);}
  .date{font-size:.76em;color:var(--muted);}
  .links{display:flex;gap:8px;margin-top:13px;flex-wrap:wrap;}
  .lnk{font-size:.82em;font-weight:700;text-decoration:none;padding:7px 13px;border-radius:8px;}
  .lnk--main{background:var(--navy);color:#fff;}
  .lnk--main:hover{background:var(--blue);}
  .lnk:not(.lnk--main){color:var(--blue);border:1px solid var(--line);}
  .empty{text-align:center;color:var(--muted);padding:40px 0;display:none;}
  footer{text-align:center;color:var(--muted);font-size:.8em;margin-top:34px;}
  footer a{color:var(--blue);}
  @media(max-width:640px){.grid{grid-template-columns:1fr;}header h1{font-size:1.45em;}}
</style>
</head>
<body>
<header>
  <div class="brand"><span class="cross">✚</span> 医知創造ラボ</div>
  <h1>インフォグラフィック一覧</h1>
  <p>診断・治療・生活のポイントを1枚に。拡大しても鮮明なHTML図解集です。</p>
</header>
<div class="container">
  <div class="search-box">
    <span class="search-icon">🔍</span>
    <input class="search-input" id="q" type="search" placeholder="キーワードで絞り込み（例：頻尿、骨、てんかん、幸せ）" oninput="filt()">
  </div>
  <p class="count"><!--COUNT--> 件の図解</p>
  <div class="grid" id="grid">
<!--CARDS-->
  </div>
  <p class="empty" id="empty">該当する図解が見つかりませんでした。</p>
  <footer>※各図は教育・情報提供を目的とした要約であり、診断・治療を代替しません。｜<a href="https://tools.ichisouzo-lab.com/slides/">スライド資料一覧はこちら</a></footer>
</div>
<script>
function filt(){var q=document.getElementById('q').value.trim().toLowerCase();var n=0;
  document.querySelectorAll('.card').forEach(function(c){var hit=c.getAttribute('data-search').toLowerCase().indexOf(q)>=0;c.style.display=hit?'':'none';if(hit)n++;});
  document.getElementById('empty').style.display=n?'none':'block';}
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-thumb", action="store_true")
    args = ap.parse_args()
    if not args.no_thumb:
        print("サムネ生成...")
        render_thumbs()
    build_index()


if __name__ == "__main__":
    main()
