"""Regression checks for levodopa_equivalent_calculator.html.

Uses only the Python standard library so it can run in the GitHub Pages
repository without installing dependencies.
"""

from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "levodopa_equivalent_calculator.html"
INDEX_PATH = ROOT / "index.html"
SW_PATH = ROOT / "sw.js"


def extract_json(html: str, element_id: str):
    match = re.search(
        rf'<script type="application/json" id="{re.escape(element_id)}">\s*(.*?)\s*</script>',
        html,
        flags=re.DOTALL,
    )
    assert match, f"missing JSON block: {element_id}"
    return json.loads(match.group(1))


def assert_close(actual: float, expected: float, label: str) -> None:
    assert math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9), (
        f"{label}: expected {expected}, got {actual}"
    )


def calculate(data, doses, supplement=False):
    """Independent model of the formulas presented in the page."""
    drugs = {item["id"]: item for item in data}
    jns = 0.0
    supplemental = 0.0
    levodopa_base = 0.0
    comt = 0.0

    for drug_id, dose in doses.items():
        drug = drugs[drug_id]
        if dose <= 0:
            continue
        if drug["source"] == "jns":
            if drug["calc"] == "stalevo":
                jns += dose * 1.33
                levodopa_base += dose
                comt += dose * 0.33
            elif drug["calc"] == "entacapone":
                contribution = dose * 0.33
                jns += contribution
                comt += contribution
            else:
                contribution = dose * drug["factor"]
                jns += contribution
                if drug.get("base"):
                    base_factor = drug.get("baseFactor")
                    levodopa_base += dose * base_factor if base_factor is not None else contribution
        elif supplement and drug["calc"] == "linear":
            contribution = dose * drug["factor"]
            supplemental += contribution
            if drug.get("base"):
                base_factor = drug.get("baseFactor")
                levodopa_base += dose * base_factor if base_factor is not None else contribution

    if supplement and doses.get("opicapone") == 25:
        contribution = levodopa_base * 0.5
        supplemental += contribution
        comt += contribution
    if supplement and doses.get("safinamide") in (50, 100):
        supplemental += 150
    if supplement and doses.get("zonisamide") in (25, 50):
        supplemental += 100
    if supplement and (dose := doses.get("ropinirole_patch", 0)):
        drug = drugs["ropinirole_patch"]
        step_count = dose / drug["validStep"]
        if (
            drug["minDose"] <= dose <= drug["maxDose"]
            and math.isclose(step_count, round(step_count), rel_tol=0, abs_tol=1e-9)
        ):
            supplemental += dose * drug["factor"]
    if supplement and doses.get("istradefylline") in (20, 40):
        supplemental += levodopa_base * 0.2
    return jns, supplemental, jns + supplemental


def over_limit(drug, result):
    """Independent model of updateConversion()'s over-limit warning condition."""
    limit = drug.get("doseLimit")
    if not isinstance(limit, (int, float)):
        return False
    return result > limit + 1e-9


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    index_html = INDEX_PATH.read_text(encoding="utf-8")
    service_worker = SW_PATH.read_text(encoding="utf-8")
    drugs = extract_json(html, "calcDrugData")
    japan_drugs = extract_json(html, "japanDrugData")
    bands = extract_json(html, "dopamineBandData")
    by_id = {item["id"]: item for item in drugs}

    expected_jns = {
        "levodopa_dci": 1,
        "stalevo": 1.33,
        "duodopa": 1.11,
        "entacapone": 0.33,
        "selegiline": 10,
        "rasagiline": 100,
        "bromocriptine": 10,
        "cabergoline": 66.7,
        "pergolide": 100,
        "pramipexole": 100,
        "ropinirole_oral": 20,
        "rotigotine": 13.3,
        "apomorphine": 10,
        "amantadine": 1,
    }
    assert {item["id"] for item in drugs if item["source"] == "jns"} == set(expected_jns)
    for drug_id, factor in expected_jns.items():
        assert_close(by_id[drug_id]["factor"], factor, drug_id)

    assert by_id["rotigotine"]["factor"] == 13.3
    assert "総含量" in by_id["rotigotine"]["name"]
    assert by_id["ropinirole_patch"]["source"] == "pmda"
    assert by_id["ropinirole_patch"]["calc"] == "haruropi"
    assert by_id["ropinirole_patch"]["factor"] == 5
    assert by_id["ropinirole_patch"]["validStep"] == 8
    assert by_id["ropinirole_patch"]["minDose"] == 8
    assert by_id["ropinirole_patch"]["maxDose"] == 64
    assert by_id["ropinirole_patch"]["factor"] != by_id["ropinirole_oral"]["factor"]
    assert by_id["foslevodopa"]["factor"] == 0.75
    assert by_id["opicapone"]["calc"] == "opicapone"
    assert by_id["opicapone"]["factor"] == 0.5
    assert by_id["safinamide"]["validDoses"] == [50, 100]
    assert by_id["zonisamide"]["validDoses"] == [25, 50]
    assert by_id["istradefylline"]["factor"] == 0.2

    assert len(japan_drugs) == 26
    assert any(item["ingredient"] == "ロピニロール（貼付）" and item["basis"] == "pmda" for item in japan_drugs)
    assert any(item["ingredient"] == "レボドパ単剤" and item["basis"] == "none" for item in japan_drugs)
    assert any(
        "ハルロピテープ" in item["products"]
        and "久光製薬：製造販売" in item["products"]
        and "協和キリン：発売" in item["products"]
        for item in japan_drugs
    )
    assert any("ヴィアレブ" in item["products"] and item["basis"] == "mds" for item in japan_drugs)

    assert len(bands) == 4
    assert [band["rotigotine"]["text"] for band in bands] == ["4.5", "9", "13.5", "18"]
    assert bands[2]["pergolide"]["text"].endswith("（適応外）")
    assert bands[3]["ropinirole_oral"]["text"] == "8–9"

    _, _, total = calculate(drugs, {"levodopa_dci": 300, "pramipexole": 1.5})
    assert_close(total, 450, "JNS combined example")
    _, _, total = calculate(drugs, {"stalevo": 300})
    assert_close(total, 399, "Stalevo")
    _, _, total = calculate(drugs, {"duodopa": 1000})
    assert_close(total, 1110, "Duodopa")
    _, _, total = calculate(drugs, {"rotigotine": 4.5})
    assert_close(total, 59.85, "Japan rotigotine label")
    _, supplement, total = calculate(
        drugs, {"levodopa_dci": 600, "opicapone": 25}, supplement=True
    )
    assert_close(supplement, 300, "Opicapone supplement")
    assert_close(total, 900, "Opicapone total")
    _, supplement, total = calculate(
        drugs,
        {"levodopa_dci": 600, "opicapone": 25, "istradefylline": 20},
        supplement=True,
    )
    assert_close(supplement, 420, "Opicapone plus istradefylline supplement")
    assert_close(total, 1020, "Opicapone plus istradefylline total")
    for dose in (50, 100):
        _, supplement, _ = calculate(drugs, {"safinamide": dose}, supplement=True)
        assert_close(supplement, 150, f"Safinamide {dose}")
    for dose in (25, 50):
        _, supplement, _ = calculate(drugs, {"zonisamide": dose}, supplement=True)
        assert_close(supplement, 100, f"Zonisamide {dose}")
    _, supplement, total = calculate(
        drugs, {"ropinirole_patch": 8}, supplement=True
    )
    assert_close(supplement, 40, "Haruropi 8 mg supplement")
    assert_close(total, 40, "Haruropi 8 mg total")
    _, supplement, total = calculate(
        drugs, {"ropinirole_patch": 64}, supplement=True
    )
    assert_close(supplement, 320, "Haruropi 64 mg supplement")
    assert_close(total, 320, "Haruropi 64 mg total")
    for invalid_dose in (12, 72):
        _, supplement, total = calculate(
            drugs, {"ropinirole_patch": invalid_dose}, supplement=True
        )
        assert_close(supplement, 0, f"Haruropi invalid {invalid_dose}")
        assert_close(total, 0, f"Haruropi invalid total {invalid_dose}")
    _, supplement, total = calculate(drugs, {"ropinirole_patch": 16})
    assert_close(supplement, 0, "Haruropi default off supplement")
    assert_close(total, 0, "Haruropi default off total")

    # --- Fix A: dose-limit guard on convertible drugs -------------------
    convertible_jns_ids = {
        item["id"] for item in drugs if item["source"] == "jns" and item.get("convertible")
    }
    assert convertible_jns_ids == {
        "levodopa_dci", "duodopa", "bromocriptine", "cabergoline",
        "pergolide", "pramipexole", "ropinirole_oral", "rotigotine",
    }, convertible_jns_ids
    for excluded_id in ("selegiline", "rasagiline", "apomorphine", "amantadine"):
        assert by_id[excluded_id]["convertible"] is False, excluded_id
        assert by_id[excluded_id]["source"] == "jns", excluded_id

    dose_limits = {
        "cabergoline": (3, "max"),
        "pramipexole": (4.5, "max"),
        "ropinirole_oral": (15, "max"),
        "rotigotine": (36, "max"),
        "pergolide": (1.25, "maintenance"),
        "bromocriptine": (22.5, "maintenance"),
    }
    for drug_id, (limit, limit_type) in dose_limits.items():
        assert_close(by_id[drug_id]["doseLimit"], limit, drug_id + " doseLimit")
        assert by_id[drug_id]["doseLimitType"] == limit_type, drug_id
    for item in drugs:
        if "doseLimitType" in item:
            assert item["doseLimitType"] in ("max", "maintenance"), item["id"]

    for drug_id, (limit, limit_type) in dose_limits.items():
        factor = by_id[drug_id]["factor"]
        boundary_led = limit * factor
        result_at_boundary = boundary_led / factor
        assert not over_limit(by_id[drug_id], result_at_boundary), (
            f"{drug_id} at exactly the dose limit should not warn"
        )
        result_over = (boundary_led + 0.1) / factor
        assert over_limit(by_id[drug_id], result_over), (
            f"{drug_id} just over the dose limit should warn"
        )
    assert_close(by_id["rotigotine"]["doseLimit"] * by_id["rotigotine"]["factor"], 478.8, "rotigotine limit LEDD")
    assert not over_limit(by_id["rotigotine"], 478.8 / by_id["rotigotine"]["factor"])
    assert over_limit(by_id["rotigotine"], 478.9 / by_id["rotigotine"]["factor"])

    # --- Fix C: istradefylline follows Jost (no COMT contribution) ------
    _, supplement, total = calculate(
        drugs,
        {"levodopa_dci": 400, "opicapone": 25, "istradefylline": 20},
        supplement=True,
    )
    assert_close(supplement, 280, "L-dopa400+opicapone25+istradefylline20 supplement")
    assert_close(supplement - 200, 80, "istradefylline contribution (not 120)")
    assert_close(total, 680, "L-dopa400+opicapone25+istradefylline20 total")

    # --- Fix D: duodopa base uses raw dose (baseFactor), not ×1.11 ------
    _, supplement, total = calculate(
        drugs, {"duodopa": 1000, "opicapone": 25}, supplement=True
    )
    assert_close(supplement, 500, "duodopa1000+opicapone25 supplement (not 555)")
    assert_close(total, 1610, "duodopa1000+opicapone25 total (not 1665)")

    # --- Regression: existing behaviour must not break -------------------
    _, supplement, total = calculate(
        drugs, {"levodopa_dci": 400, "ropinirole_patch": 40}, supplement=True
    )
    assert_close(total, 600, "L-dopa400+haruropi40 total")

    required_strings = [
        "日本神経学会2018",
        "学会表外補足（初期OFF）",
        "処方切替量ではありません",
        "ハルロピテープ：PMDA臨床試験時の切替開始量表",
        "貼付総量へ経口係数×20を直接適用しません",
        "久光製薬（製造販売元）／協和キリン（発売元）",
        "https://www.neurology-jp.org/guidelinem/pdgl/parkinson_2018_08.pdf",
        "https://www.mhlw.go.jp/topics/2026/04/tp20260401-01.html",
        "https://www.pmda.go.jp/PmdaSearch/rdDetail/iyaku/1169701S1020_1?user=1",
        "https://www.pmda.go.jp/drugs/2019/P20190917004/650034000_30100AMX00248_K102_1.pdf",
        "https://pubmed.ncbi.nlm.nih.gov/37147135/",
        "経口L-dopaと静注L-dopaの正確な換算式は確立していない",
    ]
    for required in required_strings:
        assert required in html, f"missing required text: {required}"
    assert 'href="levodopa_equivalent_calculator.html"' in index_html
    assert "'./levodopa_equivalent_calculator.html'" in service_worker

    ids = re.findall(r'\sid="([^"]+)"', html)
    assert len(ids) == len(set(ids)), "duplicate HTML id found"
    for label_target in re.findall(r'\sfor="([^"]+)"', html):
        assert label_target in ids, f"label points to missing id: {label_target}"
    for required_id in (
        "regimenRows",
        "regimenAlerts",
        "totalValue",
        "convertFrom",
        "convertTo",
        "drugTableBody",
        "copyStatus",
    ):
        assert required_id in ids
    assert "@media (max-width: 780px)" in html
    assert "@media (max-width: 620px)" in html
    assert "@media print" in html
    assert "event.key==='ArrowRight'" in html
    assert "event.key==='ArrowLeft'" in html

    assert "=>" not in html, "arrow functions are not allowed by repository compatibility rules"
    assert "`" not in html, "template literals are not allowed by repository compatibility rules"

    executable_scripts = re.findall(
        r"<script(?:\s[^>]*)?>(.*?)</script>", html, flags=re.DOTALL
    )
    executable_scripts = [
        script
        for script in executable_scripts
        if not script.lstrip().startswith("[")
    ]
    node = shutil.which("node")
    if node:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False) as handle:
            handle.write("\n".join(executable_scripts))
            temp_path = Path(handle.name)
        try:
            result = subprocess.run(
                [node, "--check", str(temp_path)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            assert result.returncode == 0, result.stderr
        finally:
            temp_path.unlink(missing_ok=True)

    # --- Haruropi in the converter tab (supplement-only) ----------------
    patch = by_id["ropinirole_patch"]
    assert patch["convertible"] is False, "Haruropi must stay out of the JNS-only list"
    assert patch["convertibleSupplement"] is True, "Haruropi must be selectable when supplement is ON"
    assert_close(patch["doseLimit"], 64, "Haruropi doseLimit")
    assert patch["doseLimitType"] == "max", "Haruropi limit is a package-insert maximum"
    supplement_convertible = {
        item["id"] for item in drugs if item.get("convertibleSupplement")
    }
    assert supplement_convertible == {"ropinirole_patch"}, supplement_convertible
    # the JNS-only option set must be unchanged by adding the supplement group
    assert convertible_jns_ids == {
        "levodopa_dci", "duodopa", "bromocriptine", "cabergoline",
        "pergolide", "pramipexole", "ropinirole_oral", "rotigotine",
    }
    # converter math must reproduce the PMDA 17.1.3 switching table exactly
    patch_factor = patch["factor"]
    oral_factor = by_id["ropinirole_oral"]["factor"]
    pmda_switch_table = [(8, 2), (16, 4), (24, 6), (32, 8), (40, 10), (48, 12), (56, 14), (64, 16)]
    for patch_dose, oral_dose in pmda_switch_table:
        assert_close(
            patch_dose * patch_factor / oral_factor, oral_dose,
            f"patch {patch_dose}mg -> oral ER (PMDA 17.1.3)",
        )
        assert_close(
            oral_dose * oral_factor / patch_factor, patch_dose,
            f"oral ER {oral_dose}mg -> patch (PMDA 17.1.3)",
        )
        assert not over_limit(patch, patch_dose), f"patch {patch_dose}mg is within the approved range"
    assert over_limit(patch, 64 + 0.1), "above 64mg/day must warn"
    for marker in (
        "convertibleSupplement",
        "renderConverterOptions",
        "学会係数ではありません",
        "8mg刻みでのみ使用します",
    ):
        assert marker in html, f"missing converter-supplement marker: {marker}"

    print("PASS: society coefficients, Haruropi bridge, supplemental formulas, Japan list, integration, safety text, and JS syntax")


if __name__ == "__main__":
    main()
