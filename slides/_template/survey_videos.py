#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""動画フォルダを走査し、スライド公開可能なものをCSV出力。

medical-content/youtube-slides/<folder>/ を全件走査し、以下を判定:
- has_pdf: *.pdf があるか
- has_png_v1 / has_png_v2 / has_png_v3: slide-NN.png / slide_v2-NN.png / slide_v3-NN.png
- has_yt_desc: YouTube説明欄.md または *YouTube概要欄.* があるか
- slide_count: PNG最大版の枚数
- youtube_id: 説明欄から正規表現抽出を試行

出力: medical-ddx-tools/slides/video_survey.csv
"""
from __future__ import annotations

import csv
import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[3]
SOURCE_ROOT = WORKSPACE / "medical-content" / "youtube-slides"
OUT_CSV = WORKSPACE / "medical-ddx-tools" / "slides" / "video_survey.csv"

YT_ID_PATTERNS = [
    re.compile(r"youtu\.be/([A-Za-z0-9_-]{11})"),
    re.compile(r"youtube\.com/(?:watch\?v=|embed/)([A-Za-z0-9_-]{11})"),
]


def find_yt_id(folder: Path) -> str:
    """folder内全 .md / .txt から YouTube ID を抽出 (placeholder VIDEO_ID は無視)"""
    candidates = list(folder.glob("*.md")) + list(folder.glob("*.txt"))
    for f in candidates:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for pat in YT_ID_PATTERNS:
            for m in pat.finditer(text):
                yid = m.group(1)
                if yid != "VIDEO_ID":  # テンプレ未置換を除外
                    return yid
    return ""


def count_pngs(folder: Path, prefix: str) -> int:
    n = 0
    for i in range(1, 100):
        if (folder / f"{prefix}{i:02d}.png").exists():
            n = i
        else:
            break
    return n


def find_pdf(folder: Path) -> str:
    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        return ""
    # v3 > v2 > v1 > その他、で最新版を優先
    for kw in ["_v3", "v3", "_v2", "v2"]:
        for p in pdfs:
            if kw in p.name:
                return p.name
    return pdfs[0].name


def read_title(folder: Path) -> str:
    """YT説明欄の1行目をタイトルとして抽出"""
    candidates = (
        list(folder.glob("YouTube*.md"))
        + list(folder.glob("*YouTube*.txt"))
        + list(folder.glob("*YouTube*.md"))
        + list(folder.glob("*概要欄*"))
    )
    for f in candidates:
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#") and not line.startswith("---"):
                return line[:80]
    return ""


def main() -> None:
    rows = []
    for folder in sorted(SOURCE_ROOT.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name.startswith("_"):
            continue

        pdf = find_pdf(folder)
        yt_id = find_yt_id(folder)
        title = read_title(folder)

        # PNG prefix priority: slide_v3- > slide_v2- > slide-
        png_v3 = count_pngs(folder, "slide_v3-")
        png_v2 = count_pngs(folder, "slide_v2-")
        png_v1 = count_pngs(folder, "slide-")

        if png_v3:
            prefix, count = "slide_v3-", png_v3
        elif png_v2:
            prefix, count = "slide_v2-", png_v2
        elif png_v1:
            prefix, count = "slide-", png_v1
        else:
            prefix, count = "", 0

        # readiness 判定
        ready = bool(pdf and yt_id and count > 0)
        needs_png = bool(pdf and yt_id and count == 0)

        rows.append({
            "folder": folder.name,
            "title": title,
            "youtube_id": yt_id,
            "pdf": pdf,
            "slide_prefix": prefix,
            "slide_count": count,
            "ready": "YES" if ready else "",
            "needs_png": "YES" if needs_png else "",
        })

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    ready_n = sum(1 for r in rows if r["ready"] == "YES")
    need_png_n = sum(1 for r in rows if r["needs_png"] == "YES")
    no_pdf_or_yt = len(rows) - ready_n - need_png_n
    print(f"Total folders: {len(rows)}")
    print(f"  Ready (PDF+YT+PNG): {ready_n}")
    print(f"  Need PNG (PDF+YT only): {need_png_n}")
    print(f"  Skip (no PDF or no YT): {no_pdf_or_yt}")
    print(f"Output: {OUT_CSV}")


if __name__ == "__main__":
    main()
