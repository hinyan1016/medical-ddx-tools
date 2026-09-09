#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""デプロイ前ゲート: 公開PNGにフルカラー（PNG-24）が新規に混ざっていないか。

GitHub Pages の公開実体は 1GB 上限。2026-09-10 に既存558枚を256色化して
447.7MB→133.4MB にしたが、**書き出しスクリプトを通さずに置いたPNG**や
新規トピックのフルカラーPNGが混ざると、また静かに膨らむ。
書き出し側の予防（png8.quantize_png の1行）とセットで、ここが見張り役。

対象（公開ページから直接参照され、ホットリンクでURLを変えられないもの）:
  infographics/<slug>/infographic.png
  infographics/<slug>/thumb.png
  slides/<slug>/infographic.png
  slides/<slug>/slide-01.png     ← 表紙。本文スライドは WebP なので対象外

透明画素が実在するものは量子化すると背景が壊れるので**免除**（png8.py と同じ判定）。

exit 0=全部256色（または正当な免除）／1=フルカラーあり（要対処）／2=未検査

  python check_png8.py            # 検査のみ
  python check_png8.py --fix      # その場で256色化して直す
"""
import argparse
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PATTERNS = [
    ("infographics", "infographic.png"),
    ("infographics", "thumb.png"),
    ("slides", "infographic.png"),
    ("slides", "slide-01.png"),
]
LIMIT_MB = 1.0      # これを超えるフルカラーは「大物」として先に出す


def targets():
    for top, name in PATTERNS:
        d = os.path.join(HERE, top)
        if not os.path.isdir(d):
            continue
        for slug in sorted(os.listdir(d)):
            p = os.path.join(d, slug, name)
            if os.path.isfile(p):
                yield p


def main():
    ap = argparse.ArgumentParser(description="公開PNGのPNG-24混入チェック")
    ap.add_argument("--fix", action="store_true", help="見つかったら その場で256色化する")
    args = ap.parse_args()

    try:
        from PIL import Image
        from png8 import quantize_png, is_png8
    except Exception as e:
        print(f"未検査: Pillow / png8.py を読み込めません: {e}")
        return 2
    Image.MAX_IMAGE_PIXELS = None

    files = list(targets())
    if not files:
        print("未検査: 対象PNGが1枚も見つかりません（パス構成が変わった可能性）")
        return 2

    bad, exempt, fixed = [], [], []
    for p in files:
        if is_png8(p):
            continue
        with Image.open(p) as im:
            im.load()
            has_alpha = (
                im.mode in ("RGBA", "LA", "PA")
                or (im.mode == "P" and "transparency" in im.info)
            ) and im.convert("RGBA").getchannel("A").getextrema()[0] < 255
        rel = os.path.relpath(p, HERE).replace("\\", "/")
        if has_alpha:
            exempt.append(rel)
            continue
        if args.fix and quantize_png(p):
            fixed.append(rel)
            continue
        bad.append((os.path.getsize(p) / 1048576, rel))

    print(f"対象 {len(files)} 枚 / 256色 {len(files) - len(bad) - len(exempt) - len(fixed)} 枚"
          f" / 透明ありで免除 {len(exempt)} 枚"
          + (f" / 今回修正 {len(fixed)} 枚" if args.fix else ""))
    for rel in exempt:
        print(f"  [免除] 透明あり: {rel}")
    for rel in fixed:
        print(f"  [修正] 256色化: {rel}")

    if not bad:
        print("OK: フルカラーPNGの新規混入なし")
        return 0

    bad.sort(reverse=True)
    total = sum(mb for mb, _ in bad)
    print(f"\nNG: フルカラー(PNG-24)が {len(bad)} 枚 / 合計 {total:.1f}MB")
    for mb, rel in bad:
        mark = " ★大物" if mb >= LIMIT_MB else ""
        print(f"  {mb:7.2f}MB  {rel}{mark}")
    print("\n対処: python check_png8.py --fix  で256色化する"
          "（URL・拡張子は変わらないのでホットリンクは壊れない）。"
          "\n      書き出し側は png8.quantize_png() を通す。写真素材で意図的にフルカラーへ"
          "残すなら、この一覧に載ることを承知のうえで判断する。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
