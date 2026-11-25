"""aspects_calculator.html を ASPECTS / pc-ASPECTS の原著と照合する。

原典:
- ASPECTS: Barber PA, et al. Lancet 2000;355:1670-4.
  MCA 領域10区域（C, L, IC, I, M1–M6）から、早期虚血変化のある区域ごとに1点減点。
- pc-ASPECTS: Puetz V, et al. Stroke 2008;39:2485-90.
  中脳・橋 各2点、左右の視床・小脳・PCA 領域 各1点を減点（10点満点）。
区分の境界（ASPECTS 6以上 / 3–5 / 3未満、pc-ASPECTS 8以上 / 6–7 / 6未満）は
ページが引用する国内ガイドライン・原著の区切りに合わせている。
"""
from __future__ import annotations

import random
import re

from calc_browser import open_tool, seg_click, text

A_REGIONS = ["C", "L", "IC", "I", "M1", "M2", "M3", "M4", "M5", "M6"]
P_WEIGHTS = {"mid": 2, "pons": 2, "thR": 1, "thL": 1, "cbR": 1, "cbL": 1, "pcaR": 1, "pcaL": 1}


def score(page):
    m = re.match(r"(-?\d+)", text(page, "#scoreBig"))
    return int(m.group(1))


def select(page, box, wanted, current):
    for rid in set(wanted) ^ set(current):
        page.locator(f'#{box} .chip[data-id="{rid}"]').click()


def a_band(s):
    return "6点以上" if s >= 6 else ("3〜5点" if s >= 3 else "3点未満")


def p_band(s):
    return "8点以上" if s >= 8 else ("6〜7点" if s >= 6 else "6点未満")


def test_aspects_anterior():
    rng = random.Random(2000)
    with open_tool("aspects_calculator.html") as page:
        for mode in ("ct", "dwi"):
            seg_click(page, "modeSeg", mode, attr="data-v")
            page.locator("#resetBtn").click()
            current: set[str] = set()
            assert score(page) == 10
            cases = [set(A_REGIONS[:k]) for k in range(11)]
            cases += [set(rng.sample(A_REGIONS, rng.randint(0, 10))) for _ in range(25)]
            for wanted in cases:
                select(page, "chipsA", wanted, current)
                current = set(wanted)
                expected = 10 - len(wanted)
                assert score(page) == expected, (mode, sorted(wanted))
                assert a_band(expected) in text(page, "#scoreBand"), (mode, expected, text(page, "#scoreBand"))


def test_pc_aspects():
    rng = random.Random(2008)
    regions = list(P_WEIGHTS)
    with open_tool("aspects_calculator.html") as page:
        seg_click(page, "modeSeg", "pc", attr="data-v")
        current: set[str] = set()
        assert score(page) == 10
        cases = [{"mid"}, {"pons"}, {"mid", "pons"}, {"thR", "thL"}, {"cbR", "pcaL"}, set(regions)]
        cases += [set(rng.sample(regions, rng.randint(0, 8))) for _ in range(30)]
        for wanted in cases:
            select(page, "chipsP", wanted, current)
            current = set(wanted)
            expected = 10 - sum(P_WEIGHTS[r] for r in wanted)
            assert score(page) == expected, sorted(wanted)
            assert p_band(expected) in text(page, "#scoreBand"), (expected, text(page, "#scoreBand"))
        assert score(page) == expected
        # 全区域で 0 点
        select(page, "chipsP", set(regions), current)
        assert score(page) == 0


if __name__ == "__main__":
    test_aspects_anterior()
    test_pc_aspects()
    print("PASS: ASPECTS / pc-ASPECTS")
