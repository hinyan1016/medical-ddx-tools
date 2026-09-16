# -*- coding: utf-8 -*-
"""index.html → infographic.png（幅1080・全高）。CSS純描画。"""
import os, sys
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
URL = "file:///" + os.path.join(HERE, "index.html").replace("\\", "/")
OUT = os.path.join(HERE, "infographic.png")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1400}, device_scale_factor=2)
    pg.goto(URL)
    pg.wait_for_timeout(500)
    el = pg.query_selector(".info")
    box = el.bounding_box()
    el.screenshot(path=OUT)
    b.close()
    print(f"infographic.png 書き出し完了 size~ 1080 x {round(box['height'])}")
