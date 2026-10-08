#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一覧カード用の軽量サムネイル（16:9・幅800px以下のWebP）を作る。

インフォグラフィック一覧・スライド一覧のカードで、原寸PNG（数百KB〜2MB）や
タイトル帯だけの細長い thumb.png を 16:9 枠に拡大して見せていたのを置き換える。
縦長の図は上端から 16:9 を切り出し（カードと同じく上寄せ）、横長は中央で切る。拡大はしない。

使う場所: infographics/build_index.py（card.webp）、slides/_template/build.py（card.webp）。
既存の png8.py と同じく、書き出し側で1行呼ぶ。
"""
import io

from PIL import Image

Image.MAX_IMAGE_PIXELS = None   # 縦長インフォ（2160x11038 等）で誤検知させない

WIDTH, HEIGHT = 800, 450


def _flatten(image):
    """透明部分は白で塗り、RGBにそろえる。"""
    if image.mode == "P":
        image = image.convert("RGBA")
    if image.mode in ("RGBA", "LA"):
        background = Image.new("RGB", image.size, "white")
        background.paste(image, mask=image.getchannel("A"))
        return background
    return image.convert("RGB")


def card_bytes(src):
    """画像ファイル src から、カード用WebPのバイト列を返す。"""
    with Image.open(src) as source:
        image = _flatten(source)
    width, height = image.size
    if width * HEIGHT > height * WIDTH:
        crop = round(height * WIDTH / HEIGHT)
        left = (width - crop) // 2
        image = image.crop((left, 0, left + crop, height))
    else:
        image = image.crop((0, 0, width, round(width * HEIGHT / WIDTH)))
    if image.width > WIDTH:
        image = image.resize((WIDTH, HEIGHT), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, "WEBP", quality=80, method=6)
    return buffer.getvalue()


def write_card(src, dst):
    """dst（card.webp）を書き出す。中身が同じなら書き換えない。書き換えたら True。"""
    data = card_bytes(src)
    try:
        if dst.read_bytes() == data:
            return False
    except FileNotFoundError:
        pass
    dst.write_bytes(data)
    return True
