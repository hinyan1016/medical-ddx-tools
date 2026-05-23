#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ローカルブログHTML + AtomPub feed から、video_survey.csv の各動画に対応する
ブログ記事 URL と正規YouTube ID を取得して match_result.csv に出力。

戦略:
1. medical-content/blog/posts/*.html を全件スキャン → 各HTMLからYT-ID抽出
2. AtomPub feed をスキャン → 全エントリの (URL, title, content-yt-id) を取得
3. 各 ready video の youtube_id を blog YT-ID と突合 → 1対1マッチ
4. 一致しない videos については「タイトル前方一致」フォールバック
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
BLOG_POSTS = WORKSPACE / "medical-content" / "blog" / "posts"
ENV_FILE = WORKSPACE / "medical-content" / "youtube-slides" / "食事指導シリーズ" / "_shared" / ".env"

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "app": "http://www.w3.org/2007/app"}
YT_PAT = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/))([A-Za-z0-9_-]{11})")
H1_PAT = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL)
IFRAME_YT_PAT = re.compile(
    r'<iframe[^>]+src="[^"]*(?:youtube\.com/embed/|youtu\.be/)([A-Za-z0-9_-]{11})',
    re.IGNORECASE,
)


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
    return "Basic " + base64.b64encode(f"{env['HATENA_ID']}:{env['HATENA_API_KEY']}".encode()).decode()


def fetch_blog_entries(env: dict[str, str], max_pages: int = 30) -> list[dict]:
    """AtomPub feed から全エントリ取得"""
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
            # メイン動画 = iframe で最初に出てくる YT ID
            iframe_yt = IFRAME_YT_PAT.findall(content_text)
            primary_yt = iframe_yt[0] if iframe_yt else ""
            yt_ids = list(set(YT_PAT.findall(content_text)))
            draft = "no"
            ctrl = entry.find("app:control", ATOM_NS)
            if ctrl is not None:
                draft_el = ctrl.find("app:draft", ATOM_NS)
                if draft_el is not None:
                    draft = draft_el.text or "no"
            out.append({
                "url": alt,
                "title": title_el.text if title_el is not None else "",
                "yt_ids": yt_ids,
                "primary_yt": primary_yt,
                "draft": draft,
            })
        next_url = None
        for link in root.findall("atom:link", ATOM_NS):
            if link.get("rel") == "next":
                next_url = link.get("href")
                break
    return out


def scan_local_blog_posts() -> list[dict]:
    """ローカル blog/posts/*.html から (filename, title, yt_ids) 抽出"""
    out: list[dict] = []
    for html in sorted(BLOG_POSTS.glob("*.html")):
        try:
            text = html.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        yt_ids = list(set(YT_PAT.findall(text)))
        m = H1_PAT.search(text)
        title = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""
        out.append({"filename": html.name, "title": title, "yt_ids": yt_ids})
    return out


def main() -> None:
    env = load_env()

    # video survey 読み込み
    with open(SLIDES_ROOT / "video_survey.csv", encoding="utf-8") as f:
        surveys = [r for r in csv.DictReader(f) if r["ready"] == "YES"]
    print(f"Ready videos: {len(surveys)}")

    print("Scanning local blog/posts/*.html ...")
    locals_ = scan_local_blog_posts()
    print(f"  local posts: {len(locals_)}")

    # ローカルでyt_idsを持つもの
    local_by_yt: dict[str, list[dict]] = {}
    for p in locals_:
        for yid in p["yt_ids"]:
            local_by_yt.setdefault(yid, []).append(p)

    print("Fetching AtomPub feed ...")
    entries = fetch_blog_entries(env)
    print(f"  feed entries: {len(entries)}")

    # メイン動画 (=最初のiframe) でのみマッチを取る。これにより
    # 「関連動画として埋め込まれているだけ」のブログを除外できる
    feed_by_primary_yt: dict[str, list[dict]] = {}
    for e in entries:
        if e["primary_yt"]:
            feed_by_primary_yt.setdefault(e["primary_yt"], []).append(e)
    # フォールバック用: 全YT-IDからのマッチ
    feed_by_yt: dict[str, list[dict]] = {}
    for e in entries:
        for yid in e["yt_ids"]:
            feed_by_yt.setdefault(yid, []).append(e)

    # シリーズ番号 (#NN) でブログをインデックス化
    series_pat = re.compile(r"[#＃](\d{1,3})\b|#(\d{1,3})$")
    series_index_pat = re.compile(r"その症状[、,]?\s*大丈夫[？?]?\s*[#＃](\d{1,3})")
    karadafu_pat = re.compile(r"からだの不思議[#＃](\d{1,3})|からだの不思議\s*第?(\d{1,3})")
    feed_by_series: dict[tuple[str, int], dict] = {}  # ('symptom_concern', 11) -> entry
    for e in entries:
        title = e.get("title") or ""
        m = series_index_pat.search(title)
        if m:
            feed_by_series[("symptom_concern", int(m.group(1)))] = e
        m2 = karadafu_pat.search(title)
        if m2:
            n = int(m2.group(1) or m2.group(2))
            feed_by_series[("karadafu", n)] = e

    folder_series_pat = re.compile(r"その症状大丈夫(\d{1,3})|symptom.*?(\d{1,3})")
    folder_kara_pat = re.compile(r"からだの不思議(\d{1,3})")

    rows = []
    for s in surveys:
        yid = s["youtube_id"]
        match_url = ""
        match_title = ""
        match_source = ""
        confidence = ""
        authoritative_yt = yid  # デフォルトは folder の YT-ID

        # 0. フォルダ名のシリーズ番号でブログをルックアップ (最優先・YT-ID信頼しない)
        folder = s["folder"]
        m_sym = folder_series_pat.search(folder)
        m_kara = folder_kara_pat.search(folder)
        series_key = None
        if m_sym:
            series_key = ("symptom_concern", int(m_sym.group(1) or m_sym.group(2)))
        elif m_kara:
            series_key = ("karadafu", int(m_kara.group(1)))

        if series_key and series_key in feed_by_series:
            e = feed_by_series[series_key]
            match_url = e["url"]
            match_title = e["title"]
            match_source = f"series-{series_key[0]}-{series_key[1]}"
            confidence = "HIGH"
            # 信頼できるYT-IDをブログのiframeから取得
            if e.get("primary_yt"):
                authoritative_yt = e["primary_yt"]

        # 1. メイン動画 (iframe1番目) として完全一致
        # ただし: フォルダ名とブログタイトルにキーワード重複が無い場合は WEAK 扱い
        elif yid in feed_by_primary_yt and len(feed_by_primary_yt[yid]) == 1:
            e = feed_by_primary_yt[yid][0]
            # フォルダ名から番号・記号を除いたキーワード抽出
            folder_clean = re.sub(r"[_\d]", "", folder)
            blog_title_clean = e["title"] or ""
            overlap = sum(1 for ch in set(folder_clean) if ch in blog_title_clean)
            if overlap >= 2:
                match_url = e["url"]
                match_title = e["title"]
                match_source = "primary-yt-exact"
                confidence = "HIGH"
            else:
                # フォルダ名とブログタイトルが無関係 → folder の YT-ID が誤りの可能性
                match_url = e["url"]
                match_title = e["title"]
                match_source = "primary-yt-but-title-mismatch"
                confidence = "REJECT"
        elif yid in feed_by_primary_yt and len(feed_by_primary_yt[yid]) > 1:
            # 同じメイン動画を持つ blog が複数 (ありえない通常)
            best = max(feed_by_primary_yt[yid], key=lambda e: title_similarity(s["title"], e["title"]))
            match_url = best["url"]
            match_title = best["title"]
            match_source = "primary-yt-multi"
            confidence = "REVIEW"
        # 2. ローカルHTML優先 (公開前下書きの可能性)
        elif yid in local_by_yt and len(local_by_yt[yid]) == 1:
            match_url = "(local-only: " + local_by_yt[yid][0]["filename"] + ")"
            match_title = local_by_yt[yid][0]["title"]
            match_source = "local-yt"
            confidence = "REVIEW"
        # 3. それでも見つからなければ「メイン動画ではないが言及あり」を弱マッチ
        elif yid in feed_by_yt and len(feed_by_yt[yid]) == 1:
            e = feed_by_yt[yid][0]
            match_url = e["url"]
            match_title = e["title"]
            match_source = "feed-yt-mention-only"
            confidence = "WEAK"

        rows.append({
            "folder": s["folder"],
            "youtube_id_folder": yid,
            "youtube_id_authoritative": authoritative_yt,
            "video_title": s["title"][:60],
            "blog_url": match_url,
            "blog_title": match_title,
            "match_source": match_source,
            "confidence": confidence,
        })

    out = SLIDES_ROOT / "match_result.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    by_conf: dict[str, int] = {}
    for r in rows:
        by_conf[r["confidence"] or "NONE"] = by_conf.get(r["confidence"] or "NONE", 0) + 1
    print(f"\nResult:")
    for k in ("HIGH", "REVIEW", "WEAK", "REJECT", "NONE"):
        if k in by_conf:
            print(f"  {k}: {by_conf[k]}")
    print(f"Output: {out}")


def title_similarity(a: str, b: str) -> float:
    """簡易類似度（共通文字数 / max(len)）"""
    if not a or not b:
        return 0.0
    s1 = set(a.replace("【", "").replace("】", ""))
    s2 = set(b.replace("【", "").replace("】", ""))
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / max(len(s1), len(s2))


if __name__ == "__main__":
    main()
