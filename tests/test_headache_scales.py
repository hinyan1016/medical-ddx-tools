"""頭痛の支障度3尺度（HIT-6・MIBS-4・MIDAS）の採点を原典と照合する。

原典:
- HIT-6: Kosinski M, et al. Qual Life Res 2003;12:963-74.
  回答の重み 6/8/10/11/13、合計36–78点。区分は 49以下・50–55・56–59・60以上。
  変化量の目安: Coeytaux RR, et al. Health Qual Life Outcomes 2006;4:70（-2.5〜-6）、
  慢性片頭痛での6点低下: Houts CR, et al. Headache 2020;60:28-39。
- MIBS-4: Buse DC, et al. Neurology 2007;68:1764-72（外来版の採点）。
  まったくない0・めったにない1・ときどき2・しばしば3・ほとんど/いつも3、わからない/該当なし0。
  区分は 0 負担なし・1–2 軽度・3–4 中等度・5以上 重度。
- MIDAS: Stewart WF, et al. Neurology 2001;56(6 Suppl 1):S20-8.
  設問1–5の日数の合計。Grade I 0–5・II 6–10・III 11–20・IV 21以上。設問A・Bは採点外。
  改善基準: American Headache Society. Headache 2021;61:1021-39（Table 8）
  治療前11–20 → 5点以上の低下、治療前20超 → 30%以上の低下。
"""
from __future__ import annotations

import itertools
import random

from calc_browser import fill, int_text, open_tool, text

HIT6_WEIGHTS = [6, 8, 10, 11, 13]
MIBS4_POINTS = [0, 0, 1, 2, 3, 3]   # data-opt 0=わからない/該当なし, 1=まったくない, … 5=ほとんど/いつも


def click_opt(page, idx, opt):
    page.locator(f'#itemBody .seg[data-idx="{idx}"] button[data-opt="{opt}"]').click()


def answer(page, combo, prev):
    """前の回答と違う項目だけ押す（同じボタンを再度押すと未回答に戻る仕様のため）。"""
    for idx, opt in enumerate(combo):
        if prev is None or prev[idx] != opt:
            click_opt(page, idx, opt)
    return combo


# ---------------- HIT-6 ----------------

def hit6_grade(total):
    if total <= 49: return "ほとんど／まったく支障なし"
    if total <= 55: return "いくらか支障あり"
    if total <= 59: return "かなり支障あり"
    return "重度の支障あり"


def hit6_answers_for(total):
    """合計が total になる回答の組を1つ探す（境界値の検査用）。"""
    for combo in itertools.product(range(5), repeat=6):
        if sum(HIT6_WEIGHTS[o] for o in combo) == total:
            return combo
    raise AssertionError(total)


def test_hit6_scoring_and_grades():
    rng = random.Random(2003)
    with open_tool("hit6_calculator.html") as page:
        assert text(page, "#totalScore") == "—"
        cases = [hit6_answers_for(t) for t in (36, 49, 50, 55, 56, 59, 60, 78)]
        cases += [tuple(rng.randrange(5) for _ in range(6)) for _ in range(30)]
        prev = None
        for combo in cases:
            prev = answer(page, combo, prev)
            total = sum(HIT6_WEIGHTS[o] for o in combo)
            assert int_text(page, "#totalScore") == total, combo
            assert hit6_grade(total) in text(page, "#gradePill"), (total, text(page, "#gradePill"))
        # 同じ回答をもう一度押すと未回答に戻り、合計は出さない
        click_opt(page, 0, prev[0])
        assert text(page, "#totalScore") == "—"


def test_hit6_change_from_previous():
    with open_tool("hit6_calculator.html") as page:
        answer(page, hit6_answers_for(56), None)
        for prev, delta, keyword in ((62, -6, "6点以上の低下"), (61, -5, "3〜5点の低下"), (59, -3, "3〜5点の低下"),
                                     (58, -2, "ほぼ不変"), (54, 2, "ほぼ不変"), (53, 3, "3点以上の上昇")):
            fill(page, "#prevScore", prev)
            assert text(page, "#deltaVal") == (f"+{delta}" if delta > 0 else str(delta)), prev
            assert keyword in text(page, "#warningArea"), (prev, text(page, "#warningArea"))
        # 36–78 の整数以外は受け付けない
        for bad in (35, 79, 50.5):
            fill(page, "#prevScore", bad)
            assert text(page, "#deltaVal") == "—"
            assert "前回の合計点を確認" in text(page, "#warningArea")


# ---------------- MIBS-4 ----------------

def mibs4_grade(total):
    if total == 0: return "負担なし"
    if total <= 2: return "軽度の負担"
    if total <= 4: return "中等度の負担"
    return "重度の負担"


def test_mibs4_scoring_and_grades():
    rng = random.Random(2007)
    with open_tool("mibs4_calculator.html") as page:
        assert text(page, "#totalScore") == "—"
        cases = [(0, 0, 0, 0), (1, 1, 1, 1), (2, 1, 1, 1), (2, 2, 1, 1), (3, 2, 1, 1), (4, 2, 1, 1),
                 (3, 3, 1, 0), (5, 5, 5, 5), (4, 4, 4, 4)]
        cases += [tuple(rng.randrange(6) for _ in range(4)) for _ in range(30)]
        prev = None
        for combo in cases:
            prev = answer(page, combo, prev)
            total = sum(MIBS4_POINTS[o] for o in combo)
            assert int_text(page, "#totalScore") == total, combo
            assert mibs4_grade(total) in text(page, "#gradePill"), (combo, text(page, "#gradePill"))
        # 「しばしば」と「ほとんど/いつも」はどちらも3点、最大12点
        assert int_text(page, "#totalScore") == sum(MIBS4_POINTS[o] for o in cases[-1])


def test_mibs4_incomplete_is_not_scored():
    with open_tool("mibs4_calculator.html") as page:
        for idx in range(3):
            click_opt(page, idx, 5)
        assert text(page, "#totalScore") == "—"
        assert "未回答 1 項目" in text(page, "#gradePill")


# ---------------- MIDAS ----------------

def midas_grade(total):
    if total <= 5: return "Grade I："
    if total <= 10: return "Grade II："
    if total <= 20: return "Grade III："
    return "Grade IV："


def set_midas(page, q, qa=None, qb=None):
    for key, v in zip(("q1", "q2", "q3", "q4", "q5"), q):
        fill(page, f"#in_{key}", v)
    fill(page, "#in_qa", qa)
    fill(page, "#in_qb", qb)


def test_midas_sum_and_grades():
    with open_tool("midas_calculator.html") as page:
        assert text(page, "#totalScore") == "—"
        for q in ((0, 0, 0, 0, 0), (1, 1, 1, 1, 1), (2, 1, 1, 1, 1), (2, 2, 2, 2, 2), (3, 2, 2, 2, 2),
                  (4, 4, 4, 4, 4), (5, 4, 4, 4, 4), (10, 10, 10, 10, 10)):
            # 設問A・B（採点外）を入れても合計は変わらない
            set_midas(page, q, qa=60, qb=8)
            total = sum(q)
            assert int_text(page, "#totalScore") == total, q
            assert midas_grade(total) in text(page, "#gradePill"), (q, text(page, "#gradePill"))
        # 1問でも空欄なら採点しない
        set_midas(page, (1, 1, 1, 1, None))
        assert text(page, "#totalScore") == "—"
        # 範囲外（93日以上・小数）は採点しない
        set_midas(page, (1, 1, 1, 1, 93))
        assert text(page, "#totalScore") == "—"
        set_midas(page, (1, 1, 1, 1, 1.5))
        assert text(page, "#totalScore") == "—"


def test_midas_ahs_2021_improvement():
    cases = [
        # (前回, 今回, 判定キーワード)
        (15, 10, "改善基準を満たします"),     # 11–20: 5点低下
        (15, 11, "改善基準には届きません"),
        (11, 6, "改善基準を満たします"),
        (20, 16, "改善基準には届きません"),
        (30, 21, "改善基準を満たします"),     # >20: 30%低下
        (30, 22, "改善基準には届きません"),
        (21, 15, "改善基準には届きません"),   # -28.6%
        (21, 14, "改善基準を満たします"),     # -33.3%
        (10, 2, "当てはまりません"),          # 10以下は対象外
    ]
    with open_tool("midas_calculator.html") as page:
        for prev, cur, keyword in cases:
            q = (cur, 0, 0, 0, 0)
            set_midas(page, q)
            fill(page, "#prevScore", prev)
            d = cur - prev
            assert keyword in text(page, "#warningArea"), (prev, cur, text(page, "#warningArea"))
            assert text(page, "#deltaVal") == (f"+{d}" if d > 0 else str(d))


if __name__ == "__main__":
    test_hit6_scoring_and_grades()
    test_hit6_change_from_previous()
    test_mibs4_scoring_and_grades()
    test_mibs4_incomplete_is_not_scored()
    test_midas_sum_and_grades()
    test_midas_ahs_2021_improvement()
    print("PASS: HIT-6 / MIBS-4 / MIDAS")
