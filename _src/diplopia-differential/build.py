#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""page.html に図版を埋め込み、公開用の単一ファイル diplopia-differential.html を書き出す。

  python _src/diplopia-differential/build.py

公開ファイルは外部依存なしの単一HTML（TOOL_AUTHORING_GUIDE.md）なので、図は data URI で埋め込む。
編集は page.html に対して行い、公開ファイルを直接編集しない。
"""
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "diplopia-differential.html")
FIGS = {
    "{{FIG_COVER}}": "fig-cover.webp",
    "{{FIG_MUSCLES}}": "fig-muscles.webp",
    "{{FIG_ABDUCTION}}": "fig-abduction.webp",
}


def main():
    with open(os.path.join(HERE, "page.html"), encoding="utf-8") as f:
        html = f.read()
    for token, name in FIGS.items():
        if token not in html:
            raise SystemExit("page.html に %s がありません" % token)
        with open(os.path.join(HERE, name), "rb") as f:
            html = html.replace(token, "data:image/webp;base64," + base64.b64encode(f.read()).decode("ascii"))
    for bad in ("～", "〜"):
        if bad in html:
            raise SystemExit("全角チルダ・波ダッシュが含まれています（作成ガイドで禁止）")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("wrote %s (%.0f KB)" % (os.path.normpath(OUT), os.path.getsize(OUT) / 1024))


if __name__ == "__main__":
    main()
