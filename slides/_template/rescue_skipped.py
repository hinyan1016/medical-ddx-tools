#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""スキップした8本のスライドを救済する。

フォルダ内 .md の YouTube ID は信用せず、ブログのタイトル検索でマッチを取り、
そのブログの最初の iframe から正規 YT-ID を抽出する。

対象 (スキップ8本):
- その症状大丈夫02_ろれつ
- その症状大丈夫04_顔のピクつき
- その症状大丈夫05_足がつる
- からだの不思議01_物忘れと認知症
- からだの不思議03_手のしびれ
- からだの不思議04_めまい
- からだの不思議05_機能性神経障害
- からだの不思議08_まぶたピクピク

出力: rescue_candidates.csv (folder, keyword_match, blog_url, blog_yt_id, blog_title)
"""
from __future__ import annotations

import base64
import csv
import io
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[3]
SLIDES_ROOT = WORKSPACE / "medical-ddx-tools" / "slides"
ENV_FILE = WORKSPACE / "medical-content" / "youtube-slides" / "食事指導シリーズ" / "_shared" / ".env"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "app": "http://www.w3.org/2007/app"}
IFRAME_YT_PAT = re.compile(
    r'<iframe[^>]+src="[^"]*(?:youtube\.com/embed/|youtu\.be/)([A-Za-z0-9_-]{11})',
    re.IGNORECASE,
)

# folder -> 必須キーワード（リスト中いずれかが blog タイトル内にあればマッチ）
# 厳しめに設定して、誤マッチを防ぐ
RESCUE_RULES: dict[str, dict] = {
    "その症状大丈夫02_ろれつ": {
        "must_any": ["ろれつ", "構音障害", "言語障害"],
        "exclude": ["振戦", "手が震える"],
    },
    "その症状大丈夫04_顔のピクつき": {
        "must_any": ["顔のピクピク", "顔がピクピク", "片側顔面けいれん", "顔面けいれん"],
        "exclude": ["手に力が入らない"],
    },
    "その症状大丈夫05_足がつる": {
        "must_any": ["足がつる", "こむら返り", "夜間のこむら"],
        "exclude": ["顔がピクピク"],
    },
    "からだの不思議01_物忘れと認知症": {
        "must_any": ["物忘れと認知症", "物忘れ", "認知症との違い", "加齢と認知症"],
        "exclude": [],
    },
    "からだの不思議03_手のしびれ": {
        "must_any": ["手のしびれ", "手がしびれ"],
        "exclude": ["スマホ"],  # スマホ首 #16 を除外
    },
    "からだの不思議04_めまい": {
        "must_any": ["めまい", "回転性"],
        "exclude": ["片頭痛"],  # 前庭性片頭痛を除外
    },
    "からだの不思議05_機能性神経障害": {
        "must_any": ["機能性神経障害", "心因性", "FND"],
        "exclude": [],
    },
    "からだの不思議08_まぶたピクピク": {
        "must_any": ["まぶたピクピク", "まぶたがピクピク", "眼瞼ミオキミア", "眼瞼けいれん"],
        "exclude": [],
    },
}


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


def fetch_entries(env: dict[str, str], max_pages: int = 200) -> list[dict]:
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
            content_text = content_el.text or "" if content_el is not None else ""
            iframe_yt = IFRAME_YT_PAT.findall(content_text)
            ctrl = entry.find("app:control", ATOM_NS)
            draft = "no"
            if ctrl is not None:
                d = ctrl.find("app:draft", ATOM_NS)
                if d is not None and d.text:
                    draft = d.text
            out.append({
                "url": alt,
                "title": title_el.text if title_el is not None else "",
                "primary_yt": iframe_yt[0] if iframe_yt else "",
                "draft": draft,
            })
        next_url = None
        for link in root.findall("atom:link", ATOM_NS):
            if link.get("rel") == "next":
                next_url = link.get("href")
                break
    return out


def match_entry(entries: list[dict], rule: dict) -> dict | None:
    """rule[must_any] のいずれかをタイトルに含み、 exclude を含まないエントリを返す。
    複数候補のうち、drafat=no を優先、次にURL新しい順。"""
    cands = []
    for e in entries:
        title = e["title"] or ""
        if not any(kw in title for kw in rule["must_any"]):
            continue
        if any(kw in title for kw in rule.get("exclude", [])):
            continue
        cands.append(e)
    if not cands:
        return None
    # 下書きでないもの優先、URL新しい順
    cands.sort(key=lambda e: (e["draft"] != "no", -int(re.sub(r"\D", "", e["url"]) or "0")))
    return cands[0]


def main() -> None:
    env = load_env()
    print("Fetching blog feed...")
    entries = fetch_entries(env)
    print(f"  {len(entries)} entries")

    rows = []
    for folder, rule in RESCUE_RULES.items():
        e = match_entry(entries, rule)
        if e:
            rows.append({
                "folder": folder,
                "blog_url": e["url"],
                "blog_title": e["title"],
                "blog_yt_id": e["primary_yt"],
                "matched_keyword": next((k for k in rule["must_any"] if k in (e["title"] or "")), ""),
                "draft": e["draft"],
            })
        else:
            rows.append({
                "folder": folder,
                "blog_url": "",
                "blog_title": "",
                "blog_yt_id": "",
                "matched_keyword": "",
                "draft": "",
            })

    out = SLIDES_ROOT / "rescue_candidates.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"\nRescue candidates:")
    for r in rows:
        status = "OK" if r["blog_yt_id"] else ("BLOG_FOUND_NO_YT" if r["blog_url"] else "NOT_FOUND")
        print(f"  [{status}] {r['folder']}")
        if r["blog_url"]:
            print(f"      blog: {r['blog_url']} (draft={r['draft']})")
            print(f"      title: {r['blog_title'][:60]}")
            print(f"      yt: {r['blog_yt_id']}")
    print(f"\nOutput: {out}")


if __name__ == "__main__":
    main()
