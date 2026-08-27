#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""tools.ichisouzo-lab.com のツールを、オフライン端末（電子カルテ共有フォルダ等）で
file:// から直接開ける形にパッケージするビルドスクリプト。

使い方:
    python make_offline_package.py                 # 既定の出力先に生成
    python make_offline_package.py --out <dir>     # 出力先を指定
    python make_offline_package.py --no-zip        # zip を作らない
    python make_offline_package.py --with-infographics   # インフォグラフィックも同梱(重い)

やっていること:
  1. index.html が参照している 49 本のツールHTML（＋infographics/tolosa_hunt.html）と
     患者ハンドアウト（handouts/）を出力先へコピー
  2. index.html から Service Worker 登録を除去（file:// では動かずコンソールエラーになるため）
  3. ディレクトリ参照リンク（href="foo/"）を href="foo/index.html" に書き換え
     （file:// はディレクトリインデックスを返さないため）
  4. 同梱しないセクション（スライド／インフォ ギャラリー）のカードを除去
  5. 外部サイトへのナビリンクを非リンク化（オフラインで押しても何も起きないため）
  6. README.txt と zip を生成
"""
import argparse
import os
import re
import shutil
import stat
import sys
import time
from pathlib import Path

SRC = Path(__file__).resolve().parent
DEFAULT_OUT = SRC.parent / "offline-tools-package" / "医知創造ラボ_診断支援ツール_オフライン版"

EXTRA_FILES = ["manifest.json"]
EXTRA_DIRS = ["icons"]


def rmtree_retry(path, attempts=5):
    """OneDrive 配下は同期中に一時的に削除を拒否するのでリトライする。"""
    def onexc(func, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            raise
    last = None
    for i in range(attempts):
        try:
            shutil.rmtree(path, onexc=onexc)
            return
        except OSError as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def tool_hrefs(index_html: str):
    """index.html が実際にリンクしている .html を収集する（正本はindex.html）。"""
    hrefs = re.findall(r'href="([^"]+\.html)"', index_html)
    out = []
    for h in hrefs:
        if h.startswith("http") or h.startswith("#"):
            continue
        if h not in out:
            out.append(h)
    return out


def rewrite_index(html: str, drop_sections, keep_handouts: bool) -> str:
    # 1) Service Worker 登録・更新スクリプトを除去
    html = re.sub(
        r"<script>if\('serviceWorker'in navigator\).*?</script>\s*",
        "", html, flags=re.S)
    html = re.sub(
        r"if \('serviceWorker' in navigator\) \{.*?\n\}\n",
        "", html, flags=re.S)

    # 2) 同梱しないセクションのカード <a ...>...</a> を丸ごと除去
    for slug in drop_sections:
        html = re.sub(
            r'\s*<a href="%s/"[^>]*>.*?</a>' % re.escape(slug),
            "", html, flags=re.S)

    if not keep_handouts:
        html = re.sub(r'\s*<a href="handouts/"[^>]*>.*?</a>', "", html, flags=re.S)

    # 3) ディレクトリ参照 → index.html
    html = re.sub(r'href="([^":]+)/"', r'href="\1/index.html"', html)

    # 4) 外部リンクを非リンク化（オフライン端末では押しても何も起きない）
    def delink(m):
        inner = m.group(2)
        style = m.group(1)
        return '<span style="%s">%s</span>' % (style, inner)
    html = re.sub(
        r'<a href="https?://[^"]+" style="([^"]*)">(.*?)</a>',
        delink, html, flags=re.S)

    return html


def rewrite_dir_links(html: str) -> str:
    return re.sub(r'href="([^":#]+)/"', r'href="\1/index.html"', html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--no-zip", action="store_true")
    ap.add_argument("--no-handouts", action="store_true")
    ap.add_argument("--with-infographics", action="store_true")
    args = ap.parse_args()

    out = Path(args.out)
    if out.exists():
        rmtree_retry(out)
    out.mkdir(parents=True)

    index_src = (SRC / "index.html").read_text(encoding="utf-8")
    hrefs = tool_hrefs(index_src)

    copied = 0
    missing = []
    for h in hrefs:
        src = SRC / h
        if not src.exists():
            missing.append(h)
            continue
        dst = out / h
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1

    for f in EXTRA_FILES:
        if (SRC / f).exists():
            shutil.copy2(SRC / f, out / f)
    for d in EXTRA_DIRS:
        if (SRC / d).is_dir():
            shutil.copytree(SRC / d, out / d)

    drop = ["slides"]
    if not args.with_infographics:
        drop.append("infographics")
    else:
        shutil.copytree(SRC / "infographics", out / "infographics",
                        ignore=shutil.ignore_patterns("__pycache__", "*.py"),
                        dirs_exist_ok=True)

    keep_handouts = not args.no_handouts
    if keep_handouts:
        shutil.copytree(SRC / "handouts", out / "handouts",
                        ignore=shutil.ignore_patterns("__pycache__", "*.py",
                                                      "_index_template.html"))

    (out / "index.html").write_text(
        rewrite_index(index_src, drop, keep_handouts), encoding="utf-8")

    # 配下 index.html のディレクトリリンクも file:// 用に書き換える
    for sub in out.rglob("index.html"):
        if sub == out / "index.html":
            continue
        t = sub.read_text(encoding="utf-8")
        sub.write_text(rewrite_dir_links(t), encoding="utf-8")

    readme = out.parent / "はじめにお読みください.txt"
    readme.write_text(README.format(name=out.name), encoding="utf-8")

    total = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    n_files = sum(1 for f in out.rglob("*") if f.is_file())
    print("出力先: %s" % out)
    print("ツールHTML: %d 本コピー" % copied)
    if missing:
        print("!! index.html が参照しているが存在しないファイル: %s" % ", ".join(missing))
    print("総ファイル数: %d / 合計 %.1f MB" % (n_files, total / 1024 / 1024))

    if not args.no_zip:
        zip_base = out.parent / out.name
        shutil.make_archive(str(zip_base), "zip", root_dir=out.parent, base_dir=out.name)
        print("zip: %s.zip (%.1f MB)" % (zip_base, (zip_base.with_suffix('.zip')).stat().st_size / 1024 / 1024))

    return 1 if missing else 0


README = u"""医知創造ラボ 診断支援ツール オフライン版
=========================================

■ 置き方
  フォルダ「{name}」をそのまま
  電子カルテの共有フォルダにコピーしてください。
  フォルダの中身（相対リンク）でつながっているので、
  フォルダごと移動する分にはどこに置いても動きます。

■ 使い方
  フォルダ内の index.html をダブルクリックで開く。
  そこから各ツール・患者ハンドアウトへ移動できます。
  よく使う人は index.html のショートカットをデスクトップに置くと便利です。

■ 動作条件
  ・インターネット接続は不要です（全ツールが単一HTMLで完結しています）。
  ・ブラウザは Edge / Chrome を推奨。IE では動きません。
  ・入力したデータはどこにも送信されません。端末内で完結します。

■ 注意
  ・トップページ上部の「ホーム」「ブログ」「YouTube」は、オフライン版では
    リンクを外して文字だけにしてあります。ハンドアウト一覧など下層ページに
    残っている外部リンクは、押してもエラー画面になります（無視して戻ってください）。
  ・スライド／インフォグラフィックのギャラリーは容量が大きいため
    このパッケージには含めていません。
  ・内容の更新はオンライン側（tools.ichisouzo-lab.com）が正本です。
    ツールが増えたらパッケージを作り直して差し替えてください。

■ 免責
  本ツールは医療従事者の思考整理を支援するものであり、
  診断・治療の最終判断に代わるものではありません。
"""

if __name__ == "__main__":
    sys.exit(main())
