"""abcd2_calculator.html の5つのスコアを各原著の配点と照合する。

原典:
- ABCD: Rothwell PM, et al. Lancet 2005;366:29-36.
  年齢60以上1、血圧（収縮期>140 または 拡張期≥90）1、片側脱力2／脱力なしの言語障害1、
  持続60分以上2／10–59分1。最大6点。
- ABCD2: Johnston SC, et al. Lancet 2007;369:283-92.
  ABCD の血圧を ≥140/90 とし、糖尿病1を加える。最大7点。
  区分：0–3 低（2日1.0%）、4–5 中（4.1%）、6–7 高（8.1%）。
- ABCD2-I: Giles MF, et al. Stroke 2010;41:1907-13. CT または DWI の梗塞に3点。最大10点。
- ABCD3 / ABCD3-I: Merwick A, et al. Lancet Neurol 2010;9:1060-9.
  dual TIA 2点（ABCD3、最大9点）。さらに同側頸動脈狭窄≥50% 2点・DWI異常 2点（ABCD3-I、最大13点）。
"""
from __future__ import annotations

import random
import re

from calc_browser import fill, open_tool, text

# 画面のボタン位置（data-idx）と、患者の所見との対応
AGE = {"lt60": 0, "ge60": 1}
CLIN = {"weakness": 0, "speech": 1, "other": 2}
DUR = {"ge60": 0, "10to59": 1, "lt10": 2}
DM = {False: 0, True: 1}
DUAL = {False: 0, True: 1}
IMG = {"dwi_pos": 0, "dwi_neg": 1, "ct_pos": 2, "ct_neg": 3, "none": 4}
CAR = {False: 0, True: 1, "none": 2}


def ref_scores(f):
    """原著どおりの配点で5つのスコアを計算する。計算できないものは None。"""
    age = 1 if f["age"] == "ge60" else 0
    clin = {"weakness": 2, "speech": 1, "other": 0}[f["clin"]]
    dur = {"ge60": 2, "10to59": 1, "lt10": 0}[f["dur"]]
    sbp, dbp = f["bp"]
    bp_abcd = 1 if (sbp > 140 or dbp >= 90) else 0
    bp_abcd2 = 1 if (sbp >= 140 or dbp >= 90) else 0
    abcd = age + bp_abcd + clin + dur
    abcd2 = age + bp_abcd2 + clin + dur + (1 if f["dm"] else 0)
    infarct = {"dwi_pos": 3, "ct_pos": 3, "dwi_neg": 0, "ct_neg": 0}.get(f["img"])
    abcd2i = None if infarct is None else abcd2 + infarct
    abcd3 = abcd2 + (2 if f["dual"] else 0)
    dwi = {"dwi_pos": 2, "dwi_neg": 0}.get(f["img"])
    car = None if f["car"] == "none" else (2 if f["car"] else 0)
    abcd3i = None if (dwi is None or car is None) else abcd3 + dwi + car
    return dict(abcd=abcd, abcd2=abcd2, abcd2i=abcd2i, abcd3=abcd3, abcd3i=abcd3i)


def ref_band(abcd2):
    if abcd2 <= 3: return "低リスク"
    if abcd2 <= 5: return "中リスク"
    return "高リスク"


def click(page, item, idx):
    page.locator(f'#itemBody button[data-item="{item}"][data-idx="{idx}"]').click()


def apply(page, f):
    click(page, "age", AGE[f["age"]])
    click(page, "clin", CLIN[f["clin"]])
    click(page, "dur", DUR[f["dur"]])
    click(page, "dm", DM[f["dm"]])
    click(page, "dual", DUAL[f["dual"]])
    click(page, "img", IMG[f["img"]])
    click(page, "car", CAR[f["car"]])
    fill(page, "#sbp", f["bp"][0])
    fill(page, "#dbp", f["bp"][1])


def read_table(page):
    """スコア表（ABCD, ABCD2, ABCD2-I, ABCD3, ABCD3-I の順）を読む。"""
    out = {}
    keys = ["abcd", "abcd2", "abcd2i", "abcd3", "abcd3i"]
    cells = page.locator("#scoreBody td.num").all_inner_texts()
    assert len(cells) == 5, cells
    for key, cell in zip(keys, cells):
        m = re.match(r"\s*(\d+)\s*/", cell)
        out[key] = int(m.group(1)) if m else None
    return out


BP_CASES = [(120, 70), (139, 89), (140, 80), (141, 80), (130, 90), (150, 95)]


def check(page, f):
    apply(page, f)
    exp = ref_scores(f)
    got = read_table(page)
    assert got == exp, f"{f}: expected {exp}, got {got}"
    assert text(page, "#heroScore") == str(exp["abcd2"])
    assert ref_band(exp["abcd2"]) in text(page, "#heroPill")


def test_abcd_family_boundaries():
    with open_tool("abcd2_calculator.html") as page:
        # 入力前はどのスコアも計算しない
        assert read_table(page) == dict(abcd=None, abcd2=None, abcd2i=None, abcd3=None, abcd3i=None)
        base = dict(age="lt60", clin="other", dur="lt10", dm=False, dual=False, img="dwi_neg", car=False, bp=(120, 70))
        check(page, base)
        # ABCD と ABCD2 で血圧基準が違うところ（140/≤89 は ABCD 0点・ABCD2 1点）
        for bp in BP_CASES:
            check(page, dict(base, bp=bp))
        # 最大値：ABCD 6、ABCD2 7、ABCD2-I 10、ABCD3 9、ABCD3-I 13
        worst = dict(age="ge60", clin="weakness", dur="ge60", dm=True, dual=True, img="dwi_pos", car=True, bp=(160, 95))
        check(page, worst)
        assert read_table(page) == dict(abcd=6, abcd2=7, abcd2i=10, abcd3=9, abcd3i=13)
        # CT のみ：ABCD2-I は計算、ABCD3-I は計算しない
        check(page, dict(worst, img="ct_pos"))
        check(page, dict(worst, img="ct_neg"))
        # 画像なし・頸動脈未評価
        check(page, dict(worst, img="none"))
        check(page, dict(worst, car="none"))
        # 区分の境界 3/4 と 5/6
        for clin, dur, dm in (("speech", "10to59", False), ("speech", "10to59", True), ("weakness", "10to59", True), ("weakness", "ge60", True)):
            check(page, dict(base, age="ge60", clin=clin, dur=dur, dm=dm))


def test_abcd_family_random_combinations():
    rng = random.Random(20261125)
    with open_tool("abcd2_calculator.html") as page:
        for _ in range(60):
            f = dict(
                age=rng.choice(list(AGE)), clin=rng.choice(list(CLIN)), dur=rng.choice(list(DUR)),
                dm=rng.choice([False, True]), dual=rng.choice([False, True]),
                img=rng.choice(list(IMG)), car=rng.choice(list(CAR)), bp=rng.choice(BP_CASES),
            )
            check(page, f)


if __name__ == "__main__":
    test_abcd_family_boundaries()
    test_abcd_family_random_combinations()
    print("PASS: ABCD / ABCD2 / ABCD2-I / ABCD3 / ABCD3-I")
