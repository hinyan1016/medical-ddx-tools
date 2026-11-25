"""bfcrs_calculator.html を Bush-Francis Catatonia Rating Scale の原著と照合する。

原典: Bush G, et al. Catatonia. I. Rating scale and standardized examination.
Acta Psychiatr Scand 1996;93:129-36.
- 23項目。多くは 0–3 点、蝋屈症・ミットゲーエン・ゲーゲンハルテン・両価運動・
  把握反射・保続の6項目は「なし0／あり3」。最大69点。
- スクリーニング（BFCSI）は項目1–14で、2項目以上が陽性ならカタトニア疑い。
"""
from __future__ import annotations

import random

from calc_browser import int_text, open_tool, text

BINARY_ITEMS = {13, 17, 18, 19, 20, 21}   # 項目番号（1始まり）


def allowed(n):
    return [0, 3] if n in BINARY_ITEMS else [0, 1, 2, 3]


def click(page, idx, val):
    page.locator(f'#itemBody .seg[data-idx="{idx}"] button[data-val="{val}"]').click()


def ref(scores):
    total = sum(scores)
    screen = sum(1 for n, s in enumerate(scores, 1) if n <= 14 and s >= 1)
    pos = sum(1 for s in scores if s > 0)
    return total, screen, pos, screen >= 2


def check(page, scores):
    total, screen, pos, positive = ref(scores)
    assert int_text(page, "#totalScore") == total, scores
    assert int_text(page, "#screenCount") == screen, scores
    assert int_text(page, "#posCount") == pos, scores
    pill = text(page, "#screenPill")
    assert ("陽性" in pill) == positive, (scores, pill)


def test_bfcrs_item_options_match_original():
    with open_tool("bfcrs_calculator.html") as page:
        for n in range(1, 24):
            vals = page.locator(f'#itemBody .seg[data-idx="{n-1}"] button').evaluate_all(
                "(bs) => bs.map(b => parseInt(b.getAttribute('data-val'), 10))")
            assert vals == allowed(n), (n, vals)


def test_bfcrs_screening_and_total():
    with open_tool("bfcrs_calculator.html") as page:
        scores = [0] * 23
        check(page, scores)
        # 項目1–14の1項目だけ → 陰性、2項目 → 陽性
        click(page, 0, 1); scores[0] = 1
        check(page, scores)
        click(page, 12, 3); scores[12] = 3   # 蝋屈症（項目13）
        check(page, scores)
        # 項目15以降はスクリーニングに数えない
        page.locator("#resetBtn").click(); scores = [0] * 23
        for idx in range(14, 23):
            v = allowed(idx + 1)[-1]
            click(page, idx, v); scores[idx] = v
        check(page, scores)
        # 全項目最大 → 69点
        for idx in range(23):
            v = allowed(idx + 1)[-1]
            click(page, idx, v); scores[idx] = v
        check(page, scores)
        assert int_text(page, "#totalScore") == 69


def test_bfcrs_random_states():
    rng = random.Random(1996)
    with open_tool("bfcrs_calculator.html") as page:
        scores = [0] * 23
        for _ in range(40):
            for idx in rng.sample(range(23), 5):
                v = rng.choice(allowed(idx + 1))
                click(page, idx, v); scores[idx] = v
            check(page, scores)


if __name__ == "__main__":
    test_bfcrs_item_options_match_original()
    test_bfcrs_screening_and_total()
    test_bfcrs_random_states()
    print("PASS: BFCRS")
