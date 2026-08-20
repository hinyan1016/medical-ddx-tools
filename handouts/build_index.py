#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ハンドアウト一覧（ギャラリー）ページを manifest.json から生成する。

  handouts/index.html = _index_template.html の <!--CARDS--> を
  manifest.json の items（カード定義）で置き換えたもの。

実行:
  python build_index.py            # index.html を再生成
  python build_index.py --check    # 生成せず検査だけ（CI・投稿前ゲート用）

--check の exit code:
  0 = 整合（未掲載スラッグ0件・index.html が manifest と一致）
  1 = 要対処（未掲載スラッグあり／index.html が古い／リンク先ディレクトリ欠落）
  2 = 未検査（manifest.json や index_template.html が読めない）

新しいハンドアウトを追加したら manifest.json に1件足して本スクリプトを実行する。
index.html を手で編集しないこと（次回の生成で消える）。
"""
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "manifest.json"
TEMPLATE = HERE / "_index_template.html"
INDEX = HERE / "index.html"

CARD = (
    '  <a class="ho-card{accent}" href="{slug}/">\n'
    '    <div class="ho-emoji">{emoji}</div>\n'
    '    <div class="ho-body">\n'
    '      <div class="ho-meta"><span class="num">{series}</span>'
    '<span class="aud">{audience}</span></div>\n'
    '      <div class="ho-title">{title}</div>\n'
    '      <div class="ho-desc">{desc}</div>\n'
    '    </div>\n'
    '    <div class="ho-arrow">→</div>\n'
    '  </a>'
)

# カード化しない（一覧に出さない）ディレクトリ
SKIP_DIRS = {"__pycache__"}


def load_items():
    items = json.loads(MANIFEST.read_text(encoding="utf-8"))["items"]
    seen = set()
    for it in items:
        if it["slug"] in seen:
            raise ValueError("manifest.json にスラッグの重複: " + it["slug"])
        seen.add(it["slug"])
    return items


def render(items):
    cards = []
    for it in items:
        accent = it.get("accent", "").strip()
        cards.append(CARD.format(
            accent=(" " + accent) if accent else "",
            slug=it["slug"], emoji=it["emoji"], series=it["series"],
            audience=it["audience"], title=it["title"], desc=it["desc"]))
    tpl = TEMPLATE.read_text(encoding="utf-8")
    if "<!--CARDS-->" not in tpl:
        raise ValueError("_index_template.html に <!--CARDS--> がありません")
    return tpl.replace("<!--CARDS-->", "\n\n".join(cards))


def audit(items):
    """ディスク上のハンドアウトと manifest の突き合わせ。"""
    on_disk = {p.name for p in HERE.iterdir()
               if p.is_dir() and p.name not in SKIP_DIRS and (p / "index.html").exists()}
    listed = {it["slug"] for it in items}
    missing = sorted(on_disk - listed)   # 実体はあるのに一覧に出ていない（本命の事故）
    dangling = sorted(listed - on_disk)  # 一覧にあるのに実体が無い（リンク切れ）
    return missing, dangling


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="生成せず検査のみ")
    a = ap.parse_args()

    try:
        items = load_items()
        html = render(items)
    except Exception as e:                      # noqa: BLE001
        print("[未検査] {}".format(e))
        return 2

    missing, dangling = audit(items)
    for s in missing:
        print("[FAIL] 一覧に未掲載: {}/ （ページは存在するのにカードが無い）".format(s))
    for s in dangling:
        print("[FAIL] リンク先が存在しない: {}/ （manifest にあるがディレクトリが無い）".format(s))

    if a.check:
        current = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
        stale = current != html
        if stale:
            print("[FAIL] index.html が manifest.json と一致しません（build_index.py を実行してください）")
        ok = not (missing or dangling or stale)
        print("検査: カード {} 件 / ディスク {} 件 → {}".format(
            len(items), len(items) + len(missing) - len(dangling), "OK" if ok else "要対処"))
        return 0 if ok else 1

    INDEX.write_text(html, encoding="utf-8", newline="\n")
    print("index.html 生成: {} 件".format(len(items)))
    return 1 if (missing or dangling) else 0


if __name__ == "__main__":
    sys.exit(main())
