#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ブログ→フォルダ逆方向マッチでスライド公開対象を発掘する。

戦略:
1. AtomPub feed から 2026-04-01 以降の draft=no エントリを取得
2. 各エントリの最初の iframe から YT-ID を抽出（無ければスキップ）
3. 該当 YT-ID に対する slide folder を検索:
   a. folder の何らかの .md / .txt / スクリプトに同じ YT-ID があれば一致 (最も確実)
   b. blog title のキーワード (#NN シリーズ、トピック語) で folder 名と類似度マッチ
4. folder に PDF + PNGs があれば deploy可能、PDF only なら needs-png 扱い
5. 既に manifest に登録済みの slug は除外

出力: medical-ddx-tools/slides/expansion_candidates.csv
"""
from __future__ import annotations

import base64
import csv
import io
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[3]
SLIDES_ROOT = WORKSPACE / "medical-ddx-tools" / "slides"
SOURCE_ROOT = WORKSPACE / "medical-content" / "youtube-slides"
ENV_FILE = WORKSPACE / "medical-content" / "youtube-slides" / "食事指導シリーズ" / "_shared" / ".env"
MANIFEST = SLIDES_ROOT / "manifest.json"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "app": "http://www.w3.org/2007/app"}
IFRAME_YT_PAT = re.compile(
    r'<iframe[^>]+src="[^"]*(?:youtube\.com/embed/|youtu\.be/)([A-Za-z0-9_-]{11})',
    re.IGNORECASE,
)
ANY_YT_PAT = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/))([A-Za-z0-9_-]{11})")
SYMPTOM_SERIES_PAT = re.compile(r"その症状[、,]?\s*大丈夫[？?]?\s*[#＃](\d{1,3})")
KARADA_SERIES_PAT = re.compile(r"からだの不思議[#＃]?(\d{1,3})")
FOLDER_SYMPTOM_PAT = re.compile(r"その症状大丈夫(\d{1,3})")
FOLDER_KARADA_PAT = re.compile(r"からだの不思議(\d{1,3})")

CUTOFF_DATE = "2026-04-01"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    with open(ENV_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def auth(env: dict[str, str]) -> str:
    return "Basic " + base64.b64encode(
        f"{env['HATENA_ID']}:{env['HATENA_API_KEY']}".encode()
    ).decode()


def fetch_entries(env: dict[str, str], max_pages: int = 50) -> list[dict]:
    next_url: str | None = (
        f"https://blog.hatena.ne.jp/{env['HATENA_ID']}/"
        f"{env['HATENA_BLOG_DOMAIN']}/atom/entry"
    )
    out: list[dict] = []
    page = 0
    while next_url and page < max_pages:
        page += 1
        req = urllib.request.Request(next_url, headers={"Authorization": auth(env)})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8")
        root = ET.fromstring(body)
        for entry in root.findall("atom:entry", ATOM_NS):
            alt = None
            for link in entry.findall("atom:link", ATOM_NS):
                if link.get("rel") == "alternate":
                    alt = link.get("href")
            if not alt:
                continue
            title_el = entry.find("atom:title", ATOM_NS)
            content_el = entry.find("atom:content", ATOM_NS)
            pub_el = entry.find("atom:published", ATOM_NS)
            content_text = content_el.text or "" if content_el is not None else ""
            iframe_yts = IFRAME_YT_PAT.findall(content_text)
            ctrl = entry.find("app:control", ATOM_NS)
            draft = "no"
            if ctrl is not None:
                d = ctrl.find("app:draft", ATOM_NS)
                if d is not None and d.text:
                    draft = d.text
            published = pub_el.text if pub_el is not None else ""
            out.append({
                "url": alt,
                "title": title_el.text if title_el is not None else "",
                "primary_yt": iframe_yts[0] if iframe_yts else "",
                "draft": draft,
                "published": published,
            })
        next_url = None
        for link in root.findall("atom:link", ATOM_NS):
            if link.get("rel") == "next":
                next_url = link.get("href")
                break
        # 早期終了: feed は新しい順なので、published < cutoff になったらこれ以上古いものは要らない
        if out and out[-1]["published"][:10] < CUTOFF_DATE:
            break
    # cutoff 適用 + draft=no + 既知の連載まとめ等を除外
    out = [
        e for e in out
        if e["published"][:10] >= CUTOFF_DATE
        and e["draft"] == "no"
        and "YouTube動画まとめ" not in e["title"]
    ]
    return out


def scan_folders() -> list[dict]:
    """各 folder の YT-ID, PNG, PDF を一覧化"""
    out: list[dict] = []
    for folder in sorted(SOURCE_ROOT.iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        # YT-ID 候補を全 md/txt から収集
        yt_ids: set[str] = set()
        for f in list(folder.glob("*.md")) + list(folder.glob("*.txt")):
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            for m in ANY_YT_PAT.finditer(text):
                yid = m.group(1)
                if yid != "VIDEO_ID":
                    yt_ids.add(yid)
        # PNG (どの prefix で何枚)
        png_v3 = sum(1 for _ in folder.glob("slide_v3-??.png"))
        png_v2 = sum(1 for _ in folder.glob("slide_v2-??.png"))
        png_v1 = sum(1 for _ in folder.glob("slide-??.png"))
        if png_v3:
            prefix, count = "slide_v3-", png_v3
        elif png_v2:
            prefix, count = "slide_v2-", png_v2
        elif png_v1:
            prefix, count = "slide-", png_v1
        else:
            prefix, count = "", 0
        # PDF (v3 優先)
        pdfs = sorted(folder.glob("*.pdf"))
        pdf = ""
        for kw in ["_v3", "v3", "_v2", "v2"]:
            for p in pdfs:
                if kw in p.name:
                    pdf = p.name
                    break
            if pdf:
                break
        if not pdf and pdfs:
            pdf = pdfs[0].name
        out.append({
            "folder": folder.name,
            "yt_ids": yt_ids,
            "slide_prefix": prefix,
            "slide_count": count,
            "pdf": pdf,
        })
    return out


def find_folder_by_yt(folders: list[dict], yt: str) -> dict | None:
    for f in folders:
        if yt in f["yt_ids"]:
            return f
    return None


def folder_topic_word(folder_name: str) -> str:
    """フォルダ名からトピック識別語を抽出。シリーズ番号のみ除去し、識別性は最大限残す。"""
    s = re.sub(r"^その症状大丈夫\d+_?", "", folder_name)
    s = re.sub(r"^からだの不思議\d+_?", "", s)
    s = re.sub(r"^てんかんGL2026_?", "", s)
    return s.strip("_")


def validate_match(folder_name: str, blog_title: str) -> bool:
    """folder のトピック語が blog title に含まれていれば valid"""
    topic = folder_topic_word(folder_name)
    if len(topic) < 2:
        return True  # 短すぎ→検証スキップ (ASCII folder などの場合)
    return topic in blog_title


def find_folder_by_title(folders: list[dict], title: str, known_folders: set[str]) -> dict | None:
    """blog title に含まれる folder トピック語で folder を逆引き"""
    best = None
    best_len = 0
    for f in folders:
        if f["folder"] in known_folders:
            continue
        topic = folder_topic_word(f["folder"])
        if len(topic) >= 3 and topic in title and len(topic) > best_len:
            best = f
            best_len = len(topic)
    return best


def find_folder_by_series(folders: list[dict], series: str, num: int) -> dict | None:
    for f in folders:
        if series == "symptom":
            m = FOLDER_SYMPTOM_PAT.search(f["folder"])
            if m and int(m.group(1)) == num:
                return f
        elif series == "karada":
            m = FOLDER_KARADA_PAT.search(f["folder"])
            if m and int(m.group(1)) == num:
                return f
    return None


def main() -> None:
    env = load_env()
    print("Fetching blog feed (April 2026+)...")
    entries = fetch_entries(env)
    print(f"  {len(entries)} entries (filtered)")

    folders = scan_folders()
    print(f"  {len(folders)} video folders")

    # 既存 manifest の slug + blog_url + source_dir
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    known_blogs = {d["blog_url"] for d in manifest["decks"] if d.get("blog_url")}
    known_folders = {d["source_dir"] for d in manifest["decks"]}
    print(f"  {len(known_blogs)} already in manifest")

    rows = []
    for e in entries:
        if e["url"] in known_blogs:
            continue
        yt = e["primary_yt"]

        # 1. シリーズ番号マッチ最優先
        m_sym = SYMPTOM_SERIES_PAT.search(e["title"] or "")
        m_kara = KARADA_SERIES_PAT.search(e["title"] or "")
        folder = None
        match_source = ""
        if m_sym:
            folder = find_folder_by_series(folders, "symptom", int(m_sym.group(1)))
            match_source = f"series-symptom-{m_sym.group(1)}"
        elif m_kara:
            folder = find_folder_by_series(folders, "karada", int(m_kara.group(1)))
            match_source = f"series-karada-{m_kara.group(1)}"

        # 2. YT-ID 完全マッチ + folder トピック語が blog title に含まれること
        if not folder and yt:
            cand = find_folder_by_yt(folders, yt)
            if cand and cand["folder"] not in known_folders and validate_match(cand["folder"], e["title"] or ""):
                folder = cand
                match_source = "folder-yt-exact-validated"

        # 3. fallback: blog title から folder トピック語を逆引き
        if not folder:
            folder = find_folder_by_title(folders, e["title"] or "", known_folders)
            if folder:
                match_source = f"title-contains-{folder_topic_word(folder['folder'])}"

        if not folder:
            continue

        # フォルダの ready 度
        if folder["slide_count"] > 0 and folder["pdf"]:
            ready = "READY"
        elif folder["pdf"]:
            ready = "NEEDS_PNG"
        else:
            ready = "NO_ASSETS"

        rows.append({
            "blog_url": e["url"],
            "blog_title": e["title"][:60],
            "published": e["published"][:10],
            "primary_yt": yt,
            "folder": folder["folder"],
            "folder_yt_ids": "|".join(sorted(folder["yt_ids"])),
            "slide_prefix": folder["slide_prefix"],
            "slide_count": folder["slide_count"],
            "pdf": folder["pdf"],
            "match_source": match_source,
            "ready": ready,
        })

    out = SLIDES_ROOT / "expansion_candidates.csv"
    rows.sort(key=lambda r: r["published"])
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["blog_url"])
        if rows:
            w.writeheader()
            w.writerows(rows)

    ready_n = sum(1 for r in rows if r["ready"] == "READY")
    npng_n = sum(1 for r in rows if r["ready"] == "NEEDS_PNG")
    noa_n = sum(1 for r in rows if r["ready"] == "NO_ASSETS")
    print(f"\nExpansion candidates:")
    print(f"  READY (即時公開可): {ready_n}")
    print(f"  NEEDS_PNG (PNG生成必要): {npng_n}")
    print(f"  NO_ASSETS (PDFなし): {noa_n}")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
