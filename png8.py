#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""公開用PNGの256色化（PNG-8）ユーティリティ。

GitHub Pages の公開実体は 1GB 上限がある。インフォグラフィック・サムネ・
表紙スライドはフラットなベクター調なので、256色に量子化しても見た目は
ほぼ変わらないまま 60〜75% 小さくなる（2026-09-10 に既存558枚へ適用、
447.7MB → 133.4MB）。**拡張子・Content-Type・URL は変わらない**ので、
公開済みブログからのホットリンク（img src / preload / JSON-LD image）は壊れない。

新規書き出しでも同じ状態を保つため、**保存直後にこの関数を1行呼ぶ**。
デプロイ前の見張りは medical-ddx-tools/check_png8.py。

安全策:
  - 実際に透明画素があるものは触らない（量子化で背景が壊れるため）
  - 量子化して大きくなるものは元のまま残す
"""
from PIL import Image

Image.MAX_IMAGE_PIXELS = None   # 縦長インフォ（2160x11038 等）で誤検知させない

MAX_COLORS = 256


def quantize_png(path, colors=MAX_COLORS):
    """path のPNGを 256色PNG に置き換える。実施したら True。

    透明画素があるもの・量子化で増えるものは元のまま残して False を返す。
    """
    import os

    path = str(path)
    before = os.path.getsize(path)
    with Image.open(path) as im:
        im.load()
        if im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info):
            if im.convert("RGBA").getchannel("A").getextrema()[0] < 255:
                return False        # 本当に透明。触らない
        q = im.convert("RGB").quantize(
            colors=colors, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG
        )
    tmp = path + ".png8.tmp"
    q.save(tmp, "PNG", optimize=True)
    if os.path.getsize(tmp) < before:
        os.replace(tmp, path)
        return True
    os.remove(tmp)
    return False


def is_png8(path):
    """path が 256色以下のPNGなら True（未検査ではなく実測）。"""
    with Image.open(path) as im:
        if im.mode != "P":
            return False
        pal = im.getpalette() or []
        return len(pal) // 3 <= MAX_COLORS
