#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""指定フォルダの PDF から slide-NN.png を pdftoppm で生成する。

使い方:
    python generate_pngs.py --folder バーナム効果 --pdf バーナム効果_スライド.pdf
    python generate_pngs.py --batch needs_png.csv

needs_png.csv は (folder, pdf_filename) の2列。

- 既存の slide-NN.png は保持 (slide-NN.png が既にあれば skip)
- pdftoppm のゼロパディング動作 (枚数 >=10 なら 2桁固定、<10 なら 1桁) を吸収して
  常に slide-NN.png 形式に正規化する
- 出力先は source folder (medical-content/youtube-slides/<folder>/)
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import subprocess
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WORKSPACE = Path(__file__).resolve().parents[3]
SOURCE_ROOT = WORKSPACE / "medical-content" / "youtube-slides"
PDFTOPPM = Path(
    r"C:\Users\jsber\AppData\Local\Microsoft\WinGet\Packages"
    r"\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\poppler-25.07.0\Library\bin\pdftoppm.exe"
)


def generate(folder_name: str, pdf_filename: str, dpi: int = 150, force: bool = False) -> tuple[bool, str]:
    folder = SOURCE_ROOT / folder_name
    pdf = folder / pdf_filename
    if not pdf.exists():
        return False, f"PDF not found: {pdf}"

    # 既存 slide-NN.png が10枚以上あれば skip (force でない限り)
    existing = sorted(folder.glob("slide-??.png"))
    if existing and not force:
        return True, f"already has {len(existing)} PNGs (skip)"

    # pdftoppm を実行
    out_prefix = folder / "slide"
    cmd = [
        str(PDFTOPPM),
        "-png",
        "-r", str(dpi),
        str(pdf),
        str(out_prefix),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "pdftoppm timeout"
    if result.returncode != 0:
        return False, f"pdftoppm failed: {result.stderr[:200]}"

    # 出力ファイル収集
    generated = sorted(folder.glob("slide-*.png"))
    # 1桁名 (slide-1.png 等) を 2桁にリネーム
    renamed = 0
    for f in generated:
        m = re.match(r"slide-(\d+)\.png", f.name)
        if not m:
            continue
        n = int(m.group(1))
        new_name = f"slide-{n:02d}.png"
        if f.name != new_name:
            target = f.with_name(new_name)
            f.rename(target)
            renamed += 1

    final = sorted(folder.glob("slide-??.png"))
    return True, f"generated {len(final)} PNGs (renamed {renamed})"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", help="単一フォルダ名")
    parser.add_argument("--pdf", help="PDFファイル名 (folder と組で使用)")
    parser.add_argument("--batch", help="CSV (folder,pdf_filename)")
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.folder and args.pdf:
        ok, msg = generate(args.folder, args.pdf, dpi=args.dpi, force=args.force)
        print(f"[{'OK' if ok else 'FAIL'}] {args.folder}: {msg}")
        sys.exit(0 if ok else 1)

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            folder = r["folder"]
            pdf = r["pdf"] or r.get("pdf_filename", "")
            if not pdf:
                print(f"[SKIP] {folder}: no PDF specified")
                continue
            ok, msg = generate(folder, pdf, dpi=args.dpi, force=args.force)
            print(f"[{'OK' if ok else 'FAIL'}] {folder}: {msg}")
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
