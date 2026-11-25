"""select_score.html を SeLECT / SeLECT 2.0 の原著配点と照合する。

原典:
- SeLECT: Galovic M, et al. Lancet Neurol 2018;17:143-52.
  重症度（NIHSS ≤3: 0, 4–10: 1, ≥11: 2）、大血管アテローム硬化 1、早期発作 3、
  皮質病変 2、MCA 領域 1。0–9点。
- SeLECT 2.0: Sinka L, et al. JAMA Neurol 2023;80:605-13.
  早期発作を「短い発作 3／てんかん重積状態 7」に分けた。0–13点。
"""
from __future__ import annotations

import itertools

from calc_browser import int_text, open_tool, text

# 項目ごとの選択肢（data-opt の順）→ (SeLECT 2.0 の点, 旧 SeLECT の点)
OPTIONS = [
    [(0, 0), (1, 1), (2, 2)],   # S: NIHSS ≤3 / 4–10 / ≥11
    [(0, 0), (1, 1)],           # L
    [(0, 0), (3, 3), (7, 3)],   # E: なし / 短い発作 / 重積
    [(0, 0), (2, 2)],           # C
    [(0, 0), (1, 1)],           # T
]


def click(page, idx, opt):
    page.locator(f'#itemBody .seg[data-idx="{idx}"] button[data-opt="{opt}"]').click()


def test_select_all_72_combinations():
    with open_tool("select_score.html") as page:
        assert text(page, "#totalScore") == "—"
        prev = [None] * 5
        for combo in itertools.product(*[range(len(o)) for o in OPTIONS]):
            for idx, opt in enumerate(combo):
                if prev[idx] != opt:
                    click(page, idx, opt)
            prev = list(combo)
            v2 = sum(OPTIONS[i][o][0] for i, o in enumerate(combo))
            v1 = sum(OPTIONS[i][o][1] for i, o in enumerate(combo))
            assert int_text(page, "#totalScore") == v2, combo
            assert f"{v1} / 9 点" in text(page, "#origScore"), combo
            status_epilepticus = combo[2] == 2
            assert ("てんかん重積状態だった場合" in text(page, "#warningArea")) == status_epilepticus
        # 最大値
        assert v2 == 13 and v1 == 9


def test_select_incomplete_is_not_scored():
    with open_tool("select_score.html") as page:
        for idx in range(4):
            click(page, idx, 1)
        assert text(page, "#totalScore") == "—"
        assert "あと1項目" in text(page, "#riskPill")


if __name__ == "__main__":
    test_select_all_72_combinations()
    test_select_incomplete_is_not_scored()
    print("PASS: SeLECT 2.0 score")
