"""栄養系2ツール（GLIM 低栄養診断・リフィーディング症候群リスク）を原典と照合する。

原典:
- GLIM: Cederholm T, et al. Clin Nutr 2019;38:1-9.
  表現型（体重減少・低BMI・筋肉量減少）1つ以上 ＋ 病因（摂取量減少/吸収不良・疾患負荷/炎症）1つ以上で低栄養。
  重症度（ステージ2）は体重減少 6か月以内>10% / 6か月超>20%。
  アジア人の低BMI: 70歳未満 <18.5、70歳以上 <20 kg/m2。
- NICE CG32（2006, 2017更新）Box 1 / 1.4.8:
  高リスク＝大基準（BMI<16、3–6か月で>15%の体重減少、摂取ほぼ無し>10日、投与前の K/P/Mg 低値）1つ以上、
  または小基準（BMI<18.5、>10%の体重減少、摂取ほぼ無し>5日、アルコール多飲・該当薬剤）2つ以上。
  開始量は最大 10 kcal/kg/日、極端な例（BMI<14 または摂取ほぼ無し>15日）は 5 kcal/kg/日。
  補充: K 2–4、P 0.3–0.6、Mg 静注0.2・経口0.4 mmol/kg/日。
- ASPEN 2020: da Silva JSV, et al. Nutr Clin Pract 2020;35:178-95.
  栄養再開5日以内に P・K・Mg のいずれかが 10–20%低下＝軽症、20–30%＝中等症、>30% または臓器障害＝重症。
"""
from __future__ import annotations

import pytest

from calc_browser import fill, open_tool, seg_click, text


# ---------------- GLIM ----------------

def glim_ref(age, bmi, wl, mus, intake, dis):
    low_bmi = bmi < (20 if age >= 70 else 18.5)
    pheno = (wl != "none") + low_bmi + (mus != "none")
    etio = intake + dis
    if pheno >= 1 and etio >= 1:
        return True, ("重度" if wl == "sev" else "中等度")
    return False, None


GLIM_CASES = [
    # age, BMI, 体重減少, 筋肉量, 摂取減少, 疾患負荷
    (75, 19.9, "none", "none", True, False),    # 70歳以上は BMI<20 で表現型
    (75, 20.0, "none", "none", True, False),    # 20.0 は該当しない
    (69, 19.9, "none", "none", True, False),    # 70歳未満は BMI<18.5
    (69, 18.4, "none", "none", False, True),
    (69, 18.5, "none", "none", False, True),
    (50, 22.0, "mod", "none", False, False),    # 表現型のみ → 診断しない
    (50, 17.0, "sev", "mild", False, False),
    (50, 22.0, "none", "none", True, True),     # 病因のみ → 診断しない
    (50, 22.0, "mod", "none", True, False),     # 中等度
    (80, 22.0, "sev", "none", False, True),     # 重度（体重減少で判定）
    (80, 17.0, "mod", "sev", True, True),       # BMI・筋肉量が低くても重症度は体重減少で判定
]


def test_glim_diagnosis_and_severity():
    with open_tool("glim_nutrition.html") as page:
        seg_click(page, "segBmiMode", "direct")
        for age, bmi, wl, mus, intake, dis in GLIM_CASES:
            fill(page, "#age", age)
            fill(page, "#bmiVal", bmi)
            seg_click(page, "segWL", wl)
            seg_click(page, "segMus", mus)
            seg_click(page, "segIntake", "yes" if intake else "no")
            seg_click(page, "segDis", "yes" if dis else "no")
            diagnosed, severity = glim_ref(age, bmi, wl, mus, intake, dis)
            result = text(page, "#resultValue")
            case = (age, bmi, wl, mus, intake, dis)
            if diagnosed:
                assert "GLIM基準を満たす" in result, (case, result)
                assert severity in text(page, "#severityPill"), (case, text(page, "#severityPill"))
            else:
                assert "満たしません" in result, (case, result)


def test_glim_bmi_from_height_weight():
    with open_tool("glim_nutrition.html") as page:
        seg_click(page, "segBmiMode", "hw")
        seg_click(page, "segIntake", "yes")
        fill(page, "#age", 75)
        # 160 cm・51 kg → 19.9（70歳以上で該当）、52 kg → 20.3（非該当）
        for weight, bmi, hit in ((51, "19.9", True), (52, "20.3", False)):
            fill(page, "#height", 160)
            fill(page, "#weight", weight)
            assert f"BMI {bmi}" in text(page, "#bmiReadout")
            assert ("GLIM基準を満たす" in text(page, "#resultValue")) == hit, weight


# ---------------- リフィーディング ----------------

def nice_ref(bmi=None, wl=None, days=None, lyte=False, drug=False):
    major = [bmi is not None and bmi < 16, wl is not None and wl > 15, days is not None and days > 10, lyte]
    minor = [bmi is not None and bmi < 18.5, wl is not None and wl > 10, days is not None and days > 5, drug]
    high = any(major) or sum(minor) >= 2
    extreme = (bmi is not None and bmi < 14) or (days is not None and days > 15)
    return high, (5 if extreme else 10)


def set_refeeding(page, bmi=None, weight=None, wl=None, days=None, lyte=False, drug=False):
    fill(page, "#bmiVal", bmi)
    fill(page, "#weight2", weight)
    fill(page, "#wloss", wl)
    fill(page, "#days", days)
    seg_click(page, "segLyte", "yes" if lyte else "no")
    seg_click(page, "segDrug", "yes" if drug else "no")


REFEEDING_CASES = [
    dict(bmi=22),
    dict(bmi=15.9),                       # 大基準 BMI<16
    dict(bmi=16.0),                       # 小基準1つのみ
    dict(bmi=18.4, drug=True),            # 小基準2つ
    dict(bmi=20, wl=15),                  # 15% ちょうどは大基準でない（小基準1つ）
    dict(bmi=20, wl=15.1),
    dict(bmi=20, wl=10.1, days=6),        # 小基準2つ
    dict(bmi=20, wl=10, days=5),          # 境界ちょうどはどちらも非該当
    dict(bmi=20, days=10),                # 小基準1つ
    dict(bmi=20, days=11),                # 大基準
    dict(bmi=20, lyte=True),              # 大基準（投与前の電解質低値）
    dict(bmi=13.9),                       # 極端：5 kcal/kg
    dict(bmi=14.0),                       # 10 kcal/kg
    dict(bmi=20, days=16),                # 極端：5 kcal/kg
    dict(bmi=20, days=15),
]


def test_refeeding_nice_high_risk_and_start_rate():
    with open_tool("refeeding_risk.html") as page:
        seg_click(page, "segBmiMode", "direct")
        for case in REFEEDING_CASES:
            set_refeeding(page, weight=40, **case)
            high, rate = nice_ref(**case)
            summary = text(page, "#summaryBox")
            assert ("判定: 高リスク" in summary) == high, (case, summary)
            if high:
                assert f"最大 {rate} kcal/kg/日（約 {40 * rate} kcal/日）" in summary, (case, summary)
                # 40 kg: K 80–160、P 12–24、Mg 静注8・経口16 mmol/日
                assert "K 約80〜160 ／ P 約12〜24 ／ Mg 静注約8・経口約16 mmol/日" in summary, summary


def aspen_ref(max_drop, organ):
    if organ and max_drop >= 10: return "重症"
    if max_drop > 30: return "重症"
    if max_drop >= 20: return "中等症"
    if max_drop >= 10: return "軽症"
    return "基準未満"


ASPEN_IDS = (("pBase", "pCur"), ("kBase", "kCur"), ("mgBase", "mgCur"))


def check_aspen(page, p, k, mg, organ, drop):
    for (b_id, c_id), pair in zip(ASPEN_IDS, (p, k, mg)):
        fill(page, "#" + b_id, None if pair is None else pair[0])
        fill(page, "#" + c_id, None if pair is None else pair[1])
    seg_click(page, "segOrgan", "yes" if organ else "no")
    expected = aspen_ref(drop, organ)
    summary = text(page, "#summaryBox")
    assert f"−{drop:.1f}%" in summary, (drop, summary)
    assert ("→ " + expected) in summary, (p, k, mg, organ, summary.splitlines()[-1])


def test_refeeding_aspen_severity():
    # 区分の境界から離れた値（浮動小数の丸めに左右されない値）で照合する
    cases = [
        ((1.0, 0.95), None, None, False, 5),
        ((1.0, 0.88), None, None, False, 12),
        ((1.0, 0.85), (4.0, 3.9), None, False, 15),   # 大きいほう（P 15%）で判定
        ((1.0, 0.75), None, None, False, 25),
        (None, (4.0, 2.6), None, False, 35),
        (None, None, (2.0, 1.38), False, 31),
        ((1.0, 0.88), None, None, True, 12),          # 臓器障害ありは重症
        ((1.0, 0.95), None, None, True, 5),           # 臓器障害ありでも10%未満は基準未満
    ]
    with open_tool("refeeding_risk.html") as page:
        for case in cases:
            check_aspen(page, *case)


@pytest.mark.xfail(strict=True, reason=(
    "既知の不具合: 低下率を丸めずに比較するため、1.0→0.9 のようなちょうど10%・20%の低下が"
    "9.999…% として一段軽く、4.0→2.8 のようなちょうど30%の低下が 30.000…% として重症に判定される。"
    "画面には −10.0% と出るのに『基準未満』となる。ページ側を直したら xfail を外す。"))
def test_refeeding_aspen_exact_boundaries():
    with open_tool("refeeding_risk.html") as page:
        check_aspen(page, (1.0, 0.9), None, None, False, 10)    # 10% ちょうど → 軽症
        check_aspen(page, (1.0, 0.8), None, None, False, 20)    # 20% ちょうど → 中等症
        check_aspen(page, None, (4.0, 2.8), None, False, 30)    # 30% ちょうど → 中等症（重症は30%超）


if __name__ == "__main__":
    test_glim_diagnosis_and_severity()
    test_glim_bmi_from_height_weight()
    test_refeeding_nice_high_risk_and_start_rate()
    test_refeeding_aspen_severity()
    print("PASS: GLIM / refeeding")
