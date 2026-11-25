"""計算ツールのブラウザ検査で共通に使う小道具。

ページの計算は IIFE の中に閉じているので、実際のページを開いて
ボタン・入力欄を操作し、画面に出た数値を読んで確かめる。

Chromium の場所が既定と違う環境では、環境変数
PLAYWRIGHT_CHROMIUM_EXECUTABLE に実行ファイルのパスを入れる。
"""
from __future__ import annotations

import os
import re
from contextlib import contextmanager
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def open_tool(filename: str):
    """ツールのページを開き、page を返す。外部への通信は止め、JS の例外があれば失敗にする。"""
    errors: list[str] = []
    exe = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
    with sync_playwright() as p:
        browser = p.chromium.launch(**({"executable_path": exe} if exe else {}))
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        # file:// では Service Worker を登録できない。ページの計算とは無関係なので除外する。
        ignore = re.compile(r"ServiceWorker")
        page.route(re.compile(r"^https?://"), lambda route: route.abort())
        page.goto((ROOT / filename).as_uri(), wait_until="load")
        try:
            yield page
        finally:
            browser.close()
    errors = [e for e in errors if not ignore.search(e)]
    assert not errors, f"{filename}: JS errors: {errors}"


def text(page, selector: str) -> str:
    return page.locator(selector).inner_text().strip()


def int_text(page, selector: str) -> int | None:
    """数字だけの表示を int で返す。「—」などは None。"""
    s = text(page, selector)
    m = re.fullmatch(r"-?\d+", s)
    return int(s) if m else None


def fill(page, selector: str, value) -> None:
    page.locator(selector).fill("" if value is None else str(value))


def seg_click(page, seg_id: str, value: str, attr: str = "data-val") -> None:
    page.locator(f'#{seg_id} button[{attr}="{value}"]').click()
