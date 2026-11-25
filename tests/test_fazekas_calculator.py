"""fazekas_calculator.html の合計点と区分を原典と照合する。

原典:
- Fazekas F, et al. AJR 1987;149:351-6.  PVH 0–3、DWMH 0–3、合計0–6点。
- Chan M, et al. Radiat Oncol 2020;15:269.
  治療前 Fazekas 合計 0–2点（白質病変なし〜疑わしい）と 3–6点（確実な白質病変）で比較。
  6/6点の3例は全例が WBRT 後に CTCAE Grade 3 の認知毒性。
- LADIS: Inzitari D, et al. BMJ 2009;339:b2477.  深部白質の Fazekas 1/2/3 を軽度/中等度/高度とした。
"""
from __future__ import annotations

import itertools

from calc_browser import int_text, open_tool, text


def click(page, kind, grade):
    page.locator(f'.grade-btn[data-kind="{kind}"][data-grade="{grade}"]').click()


def rt_keyword(total):
    if total == 6:
        return "6/6点"
    return "3〜6点区分" if total >= 3 else "0〜2点区分"


def test_fazekas_total_and_rt_band():
    with open_tool("fazekas_calculator.html") as page:
        for pvh, dwmh in itertools.product(range(4), repeat=2):
            click(page, "pvh", pvh)
            click(page, "dwmh", dwmh)
            total = pvh + dwmh
            assert int_text(page, "#totalScore") == total, (pvh, dwmh)
            assert rt_keyword(total) in text(page, "#rtRiskPill"), (pvh, dwmh, text(page, "#rtRiskPill"))


def test_fazekas_ladis_severity_follows_dwmh():
    """LADIS の重症度は深部白質（DWMH）の Fazekas 段階だけで決まり、PVH には左右されない。"""
    labels = {1: "軽度", 2: "中等度", 3: "高度"}
    with open_tool("fazekas_calculator.html") as page:
        for pvh, dwmh in itertools.product(range(4), repeat=2):
            click(page, "pvh", pvh)
            click(page, "dwmh", dwmh)
            pill = text(page, "#ladisPill")
            if dwmh == 0:
                expected = "異常なし" if pvh == 0 else "深部白質病変なし"
            else:
                expected = labels[dwmh]
            assert expected in pill, (pvh, dwmh, pill)
            others = [v for k, v in labels.items() if k != dwmh]
            assert not any(o in pill for o in others), (pvh, dwmh, pill)


if __name__ == "__main__":
    test_fazekas_total_and_rt_band()
    test_fazekas_ladis_severity_follows_dwmh()
    print("PASS: Fazekas")
