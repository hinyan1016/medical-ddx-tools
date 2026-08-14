#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""【デプロイ前ゲート】Service Worker のキャッシュ更新漏れを検出する。

空ページ問題の主因は SW キャッシュ。新ツールを ASSETS に足しても CACHE_NAME を
上げないと、既にサイトを開いたことがある訪問者には古いキャッシュが返り続け、
新しいページが真っ白になる。これまでこの手順は plan の文章と人間の注意力だけで
守られていた（検出するチェックすら無かった）。

見るもの:
    1. ASSETS に載っているのに実ファイルが無いパス（消したツールの残骸）
    2. 実ファイルがあるのに ASSETS に載っていないページ（キャッシュ漏れ）
       対象はトップレベルの *.html と PAGE_SUBDIRS 配下。除外したディレクトリは
       件数と理由を必ず出力する（黙って落とすと「全部見た」と誤読される）。
    3. git HEAD と比べて ASSETS が変わったのに CACHE_NAME が上がっていない

使い方:
    python check_sw_cache.py                 # リポジトリ直下で実行
    python check_sw_cache.py --sw sw.js --root .

終了コード: 0=整合 / 1=要対処 / 2=未検査（git と比較できない等）
"""
from __future__ import annotations

import argparse
import io
import re
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)

_CACHE_NAME = re.compile(r"""CACHE_NAME\s*=\s*["']([^"']+)["']""")
_ASSETS_BLOCK = re.compile(r"ASSETS\s*=\s*\[(.*?)\]", re.DOTALL)
_ASSET_ITEM = re.compile(r"""["']([^"']+)["']""")
_VERSION = re.compile(r"v(\d+)\s*$")

# 配信対象でない HTML（テンプレ・作業用）は ASSETS 網羅の対象から外す
IGNORED_PREFIXES = ("_", ".")
IGNORED_NAMES = {"test.html", "sample.html"}

# ASSETS 網羅の対象にするサブディレクトリ。
# 2026-08-15 まではトップレベルの *.html しか数えておらず、infographics/ 配下の
# キャッシュ漏れ（認知症シリーズ第4弾のインフォページ）を素通りさせた。
# ASSETS には最初からサブディレクトリ配下が載っていたので、実在確認だけが効いて
# 網羅確認が効かない非対称になっていた。
PAGE_SUBDIRS = ("infographics", "handouts")

# 意図的に網羅対象から外すディレクトリと、その理由。
# 黙って除外すると「全部見た上での PASS」と読めてしまうので、必ず件数を出力する。
EXCLUDED_SUBDIRS = {
    "slides": "動画デッキの原本。PWA のオフライン対象ではない",
    "infographics-gallery": "旧ギャラリー（webp 十数MB）。現行は infographics/index.html",
}


def parse_cache_name(js: str) -> str | None:
    m = _CACHE_NAME.search(js)
    return m.group(1) if m else None


def parse_assets(js: str) -> list[str]:
    """ASSETS 配列のエントリを順に返す。配列の閉じ括弧より後ろは読まない。"""
    m = _ASSETS_BLOCK.search(js)
    if not m:
        return []
    return [x.group(1) for x in _ASSET_ITEM.finditer(m.group(1))]


def version_of(cache_name: str | None) -> int | None:
    if not cache_name:
        return None
    m = _VERSION.search(cache_name)
    return int(m.group(1)) if m else None


def missing_assets(assets: list[str], existing: set[str]) -> list[str]:
    """ASSETS に載っているのに実ファイルが無いものを返す（'./' は除く）。"""
    out = []
    for a in assets:
        name = a[2:] if a.startswith("./") else a
        if not name or name.endswith("/"):
            continue
        if name not in existing:
            out.append(a)
    return out


def unlisted_pages(existing: set[str], assets: list[str]) -> list[str]:
    """実ファイルがあるのに ASSETS に載っていないページを返す。"""
    listed = {a[2:] if a.startswith("./") else a for a in assets}
    return sorted(n for n in existing if n not in listed)


def needs_bump(old_assets: list[str], new_assets: list[str],
               old_version: int | None, new_version: int | None) -> bool:
    """ASSETS が変わったのに CACHE_NAME が上がっていないなら True。"""
    if list(old_assets) == list(new_assets):
        return False
    if old_version is None or new_version is None:
        return True          # 版が読めないなら上がった保証が無い
    return new_version <= old_version


def decide_exit(missing: int, unlisted: int, bump_needed: bool, compared: bool) -> int:
    if missing or unlisted or bump_needed:
        return 1
    return 0 if compared else 2


def git_head_sw(repo: Path, rel: str) -> str | None:
    """git HEAD 版の sw.js を取る。取れなければ None（未検査）。"""
    try:
        p = subprocess.run(["git", "-C", str(repo), "show", f"HEAD:{rel}"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
    except Exception:
        return None
    return p.stdout if p.returncode == 0 else None


def is_page_name(name: str) -> bool:
    """テンプレ・作業用のファイル／ディレクトリ名でないなら True。"""
    return not name.startswith(IGNORED_PREFIXES) and name not in IGNORED_NAMES


def collect_pages(root: Path) -> set[str]:
    """ASSETS 網羅の対象にする配信ページを root からの相対パスで返す。

    トップレベルの診断ツール HTML に加えて、PAGE_SUBDIRS 配下のページも数える。
    パスの途中に '_shared' のような作業用ディレクトリが挟まるものは除く。
    """
    pages = {p.name for p in root.glob("*.html") if is_page_name(p.name)}
    for sub in PAGE_SUBDIRS:
        d = root / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*.html"):
            rel = p.relative_to(root).as_posix()
            if all(is_page_name(part) for part in rel.split("/")):
                pages.add(rel)
    return pages


def excluded_summary(root: Path) -> list[tuple[str, int, str]]:
    """網羅対象から外したディレクトリと、その HTML 件数・理由。"""
    out = []
    for sub, why in EXCLUDED_SUBDIRS.items():
        d = root / sub
        if d.is_dir():
            out.append((sub, sum(1 for _ in d.rglob("*.html")), why))
    return sorted(out)


def collect_files(root: Path) -> set[str]:
    """ASSETS の実在確認に使う、root からの相対パス一式。

    ASSETS には './handouts/<slug>/index.html' のようなサブディレクトリ配下も
    載るので、ファイル名だけで照合してはいけない。
    """
    out: set[str] = set()
    for p in root.rglob("*"):
        if p.is_file() and ".git" not in p.parts:
            out.add(p.relative_to(root).as_posix())
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Service Worker キャッシュの整合ゲート")
    ap.add_argument("--sw", default="sw.js")
    ap.add_argument("--root", default=".", help="配信ルート（*.html を探す場所）")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    sw_path = (root / a.sw) if not Path(a.sw).is_absolute() else Path(a.sw)
    if not sw_path.exists():
        print(f"[エラー] sw.js がありません: {sw_path}", file=sys.stderr)
        return 2

    js = sw_path.read_text(encoding="utf-8", errors="replace")
    cache_name = parse_cache_name(js)
    assets = parse_assets(js)
    if not assets:
        print("[未検査] ASSETS を読み取れませんでした。書式を確認すること。", file=sys.stderr)
        return 2

    pages = collect_pages(root)
    missing = missing_assets(assets, collect_files(root))
    unlisted = unlisted_pages(pages, assets)

    head_js = git_head_sw(root, sw_path.name)
    compared = head_js is not None
    bump = False
    if compared:
        bump = needs_bump(parse_assets(head_js), assets,
                          version_of(parse_cache_name(head_js)), version_of(cache_name))

    print(f"CACHE_NAME: {cache_name}  /  ASSETS {len(assets)} 件  /  配信ページ {len(pages)} 件"
          f"（トップレベル + {'/ '.join(PAGE_SUBDIRS)}/）")
    for sub, n, why in excluded_summary(root):
        print(f"  網羅対象外: {sub}/ {n} 件 — {why}")
    if compared:
        print(f"HEAD との比較: CACHE_NAME {parse_cache_name(head_js)} → {cache_name}")
    else:
        print("HEAD と比較できませんでした（未コミット・git 不在など）")

    if missing:
        print(f"\n❌ ASSETS に載っているが実ファイルが無い: {len(missing)} 件")
        for x in missing:
            print("   ", x)
    if unlisted:
        print(f"\n❌ 実ファイルがあるが ASSETS に無い: {len(unlisted)} 件（キャッシュされない）")
        for x in unlisted:
            print("   ", x)
    if bump:
        print(f"\n❌ ASSETS を変更したのに CACHE_NAME が上がっていません（現在 {cache_name}）")
        v = version_of(cache_name)
        if v is not None:
            print(f"   → 'ddx-tools-v{v + 1}' に上げること。上げないと既存訪問者に"
                  "古いキャッシュが返り、新しいページが空になります。")

    rc = decide_exit(len(missing), len(unlisted), bump, compared)
    print("\n判定:", {0: "✅ PASS", 1: "FAIL（デプロイしない）",
                     2: "未検査（合格ではない）"}[rc])
    return rc


if __name__ == "__main__":
    sys.exit(main())
