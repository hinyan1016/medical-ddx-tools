"""cave_score.html を CAVE スコア原著と照合する。

原典: Haapaniemi E, et al. The CAVE score for predicting late seizures after
intracerebral hemorrhage. Stroke 2014;45:1971-6.
皮質進展・65歳未満・血腫量>10 mL・発症7日以内の早期発作が各1点（0–4点）。
点数別の遅発発作リスク（導出コホート）：0.6%, 3.6%, 9.8%, 34.8%, 46.2%。
血腫量の ABC/2 法: Kothari RU, et al. Stroke 1996;27:1304-5.
"""
from __future__ import annotations

import itertools

from calc_browser import fill, int_text, open_tool, text

RISK = ["0.6", "3.6", "9.8", "34.8", "46.2"]


def click(page, idx, val):
    page.locator(f'#itemBody .seg[data-idx="{idx}"] button[data-val="{val}"]').click()


def test_cave_all_16_combinations():
    with open_tool("cave_score.html") as page:
        assert text(page, "#totalScore") == "—"
        for combo in itertools.product((0, 1), repeat=4):
            for idx, val in enumerate(combo):
                click(page, idx, val)
            total = sum(combo)
            assert int_text(page, "#totalScore") == total, combo
            assert f"{RISK[total]}%" in text(page, "#riskPill"), (combo, text(page, "#riskPill"))
            assert f"合計：{total} / 4 点" in text(page, "#summaryBox")


def test_cave_incomplete_is_not_scored():
    with open_tool("cave_score.html") as page:
        for idx in range(3):
            click(page, idx, 1)
        assert text(page, "#totalScore") == "—"
        assert "あと1項目" in text(page, "#riskPill")
        page.locator("#resetBtn").click()
        assert text(page, "#totalScore") == "—"


def test_cave_abc2_helper():
    """ABC/2：A×B×C÷2。10 mL ちょうどは「>10 mL」に当たらない。"""
    with open_tool("cave_score.html") as page:
        page.locator("details.helper summary").click()
        for a, b, c, volume, v_point in ((3, 2, 4, 12.0, 1), (2, 2, 5, 10.0, 0), (2.5, 2, 4.2, 10.5, 1), (1, 1, 1, 0.5, 0)):
            fill(page, "#abcA", a)
            fill(page, "#abcB", b)
            fill(page, "#abcC", c)
            assert f"推定血腫量 {volume:.1f} mL" in text(page, "#abcResult"), (a, b, c)
            page.locator("#abcApply").click()
            assert text(page, "#b_2") == f"{v_point} 点", (a, b, c)
        fill(page, "#abcC", "")
        assert page.locator("#abcApply").is_disabled()


if __name__ == "__main__":
    test_cave_all_16_combinations()
    test_cave_incomplete_is_not_scored()
    test_cave_abc2_helper()
    print("PASS: CAVE score")
