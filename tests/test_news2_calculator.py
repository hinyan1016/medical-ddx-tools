"""news2_calculator.html の配点を RCP NEWS2（2017）の採点表と照合する。

原典: Royal College of Physicians. National Early Warning Score (NEWS) 2, 2017.
Chart 1（採点表）と Chart 2/Table（臨床リスク区分）の境界値を1つずつ確かめる。
"""
from __future__ import annotations

from calc_browser import fill, int_text, open_tool, seg_click, text

# ---- RCP NEWS2 Chart 1 をそのまま書き下した参照実装 ----

def ref_resp(v):
    if v <= 8: return 3
    if v <= 11: return 1
    if v <= 20: return 0
    if v <= 24: return 2
    return 3


def ref_spo2_scale1(v):
    if v <= 91: return 3
    if v <= 93: return 2
    if v <= 95: return 1
    return 0


def ref_spo2_scale2(v, on_o2):
    if v <= 83: return 3
    if v <= 85: return 2
    if v <= 87: return 1
    if v <= 92: return 0
    if not on_o2: return 0          # ≥93 on air
    if v <= 94: return 1
    if v <= 96: return 2
    return 3


def ref_sbp(v):
    if v <= 90: return 3
    if v <= 100: return 2
    if v <= 110: return 1
    if v <= 219: return 0
    return 3


def ref_hr(v):
    if v <= 40: return 3
    if v <= 50: return 1
    if v <= 90: return 0
    if v <= 110: return 1
    if v <= 130: return 2
    return 3


def ref_temp(v):
    if v <= 35.0: return 3
    if v <= 36.0: return 1
    if v <= 38.0: return 0
    if v <= 39.0: return 1
    return 2


NORMAL = dict(resp=16, spo2=98, sbp=120, hr=70, temp=37.0)


def set_vitals(page, **v):
    for key in ("resp", "spo2", "sbp", "hr", "temp"):
        fill(page, "#" + key, v[key])


def test_news2_chart_boundaries():
    with open_tool("news2_calculator.html") as page:
        set_vitals(page, **NORMAL)
        assert int_text(page, "#totalScore") == 0
        assert "低リスク（0）" in text(page, "#riskPill")

        sweeps = {
            "resp": ([8, 9, 11, 12, 20, 21, 24, 25], ref_resp),
            "spo2": ([91, 92, 93, 94, 95, 96], ref_spo2_scale1),
            "sbp": ([90, 91, 100, 101, 110, 111, 219, 220], ref_sbp),
            "hr": ([40, 41, 50, 51, 90, 91, 110, 111, 130, 131], ref_hr),
            "temp": ([35.0, 35.1, 36.0, 36.1, 38.0, 38.1, 39.0, 39.1], ref_temp),
        }
        for key, (values, ref) in sweeps.items():
            for v in values:
                set_vitals(page, **dict(NORMAL, **{key: v}))
                got = int_text(page, "#totalScore")
                assert got == ref(v), f"{key}={v}: expected {ref(v)}, got {got}"
            set_vitals(page, **NORMAL)

        # 意識：Alert 以外（新たな混乱を含む）は3点
        for level, pts in (("A", 0), ("C", 3), ("V", 3), ("P", 3), ("U", 3)):
            seg_click(page, "segAcvpu", level)
            assert int_text(page, "#totalScore") == pts, level
        seg_click(page, "segAcvpu", "A")

        # 酸素投与は2点（Scale 1）
        seg_click(page, "segO2", "o2")
        assert int_text(page, "#totalScore") == 2
        seg_click(page, "segO2", "air")


def test_news2_spo2_scale2():
    with open_tool("news2_calculator.html") as page:
        set_vitals(page, **NORMAL)
        seg_click(page, "segScale", "2")
        for on_o2 in (False, True):
            seg_click(page, "segO2", "o2" if on_o2 else "air")
            for v in (83, 84, 85, 86, 87, 88, 92, 93, 94, 95, 96, 97, 100):
                fill(page, "#spo2", v)
                expected = ref_spo2_scale2(v, on_o2) + (2 if on_o2 else 0)
                got = int_text(page, "#totalScore")
                assert got == expected, f"scale2 spo2={v} o2={on_o2}: expected {expected}, got {got}"


def test_news2_risk_bands():
    """RCP の臨床リスク区分：0–4 低、単項目3点は低〜中、5–6 中、7以上 高。"""
    with open_tool("news2_calculator.html") as page:
        cases = [
            # (vitals, expected total, pill keyword)
            (dict(NORMAL, resp=22), 2, "低リスク（1〜4）"),
            (dict(NORMAL, resp=22, hr=105, temp=38.5), 4, "低リスク（1〜4）"),
            (dict(NORMAL, resp=26), 3, "単項目3点"),
            (dict(NORMAL, resp=22, hr=115, temp=38.5), 5, "中リスク"),
            (dict(NORMAL, resp=22, hr=115, temp=39.5), 6, "中リスク"),
            (dict(NORMAL, resp=26, hr=115, temp=39.5), 7, "高リスク"),
            (dict(NORMAL, resp=26, hr=115, temp=39.5, sbp=85), 10, "高リスク"),
        ]
        for vitals, total, keyword in cases:
            set_vitals(page, **vitals)
            assert int_text(page, "#totalScore") == total, vitals
            assert keyword in text(page, "#riskPill"), (vitals, text(page, "#riskPill"))
        # 入力が欠けたら合計に＊を付け、判定しない
        fill(page, "#resp", "")
        assert text(page, "#totalScore").endswith("＊")
        assert "未入力" in text(page, "#riskPill")


if __name__ == "__main__":
    test_news2_chart_boundaries()
    test_news2_spo2_scale2()
    test_news2_risk_bands()
    print("PASS: NEWS2 chart boundaries, scale 2, risk bands")
