"""Regression checks for warfarin_dose_adjuster.html.

提案する飲み方を「毎日同じ量」と「きざみ1つ分だけ違う2つの量の1日おき」に
絞った計算（2026-11-17 改修）と、導入期の提案・Shoji 2020 の式（同日追加）を、node で実際のページの関数を動かして確かめる。
標準ライブラリだけで動く（GitHub Pages のリポジトリに依存を足さない）。
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_PATH = ROOT / "warfarin_dose_adjuster.html"
INDEX_PATH = ROOT / "index.html"
SW_PATH = ROOT / "sw.js"


def extract_calc_script(html: str) -> str:
    """画面に触れない計算部分（IIFE の先頭から window.WFDose の行まで）を取り出す。"""
    start = html.index("<script>\n(function(){")
    body_start = html.index("(function(){", start)
    end_marker = "window.WFDose = {"
    end = html.index(end_marker, body_start)
    end = html.index("\n", end)
    return html[body_start:end] + "\n})();\n"


def run_node(calc_js: str) -> dict:
    node = shutil.which("node")
    assert node, "node が見つからない"
    driver = r"""
var window = {};
%s
var W = window.WFDose;
function pick(g){ return { text: g.text, avg: g.avg, weekly: g.weekly, rp: g.rp, band: g.band, alt: g.alt, hi: g.hi, lo: g.lo }; }
function cand(weekly, dir, u){ var c = W.candidates(weekly, dir, u); return { out: c.out, rows: c.rows.map(pick) }; }
var out = {};
out.reg5 = pick(W.regimen(5, 0.5));
out.reg1 = pick(W.regimen(1, 0.5));
out.reg4 = pick(W.regimen(4, 0.5));
out.cases = {
  d05: cand(3.5, -1, 0.5),
  d10: cand(7, -1, 0.5),
  d15: cand(10.5, -1, 0.5),
  d25: cand(17.5, -1, 0.5),
  d50: cand(35, -1, 0.5),
  d10q: cand(7, -1, 0.25),
  w155: cand(15.5, -1, 0.5),
  up10: cand(70, 1, 0.5)
};
var t = W.candidates(17.5, -1, 0.5);
out.tie15 = pick(t.rows[W.nearest(t.rows, 15)]);
out.days = W.days14(W.regimen(5, 0.5));
out.chg = [W.chgText(14, 17.5), W.chgText(19.25, 17.5), W.chgText(17.5, 17.5)];
out.fmtAvg = [W.fmtAvg(0.875), W.fmtAvg(2.25), W.fmtAvg(15.75), W.fmtAvg(2)];
/* 0.5 mg きざみ：1日平均 1.25-20 mg（0.25 刻み）の全点で、増量・減量とも幅内の候補がある */
var bad = [], d, dir, c, i, g;
for (d = 1.25; d <= 20.0001; d += 0.25) {
  for (dir = -1; dir <= 1; dir += 2) {
    c = W.candidates(d * 7, dir, 0.5);
    if (c.out || c.rows.length < 1 || c.rows.length > 3) { bad.push([d, dir, 'count', c.out, c.rows.length]); continue; }
    for (i = 0; i < c.rows.length; i++) {
      g = c.rows[i];
      if (g.rp < 10 || g.rp > 20) bad.push([d, dir, 'rp', g.rp]);
      if ((g.avg - d) * dir <= 0) bad.push([d, dir, 'direction', g.avg]);
      if (g.alt && Math.abs(g.hi - g.lo - 0.5) > 1e-9) bad.push([d, dir, 'step', g.hi, g.lo]);
      if (!g.alt && g.hi !== g.lo) bad.push([d, dir, 'daily', g.hi, g.lo]);
      if (i > 0 && c.rows[i - 1].rp > g.rp) bad.push([d, dir, 'order']);
    }
  }
}
out.sweepBad = bad;
/* 導入期（status 'init'、PT-INR 5.0 未満） */
function ini(inr, ph, pl, extra){
  var o = { lo: 1.6, hi: 2.6, inr: inr, weekly: 14, unit: 0.5, bleed: 'none', status: 'init',
    transient: false, bleedRisk: false, thrombRisk: false, initPhase: ph, initPrevLow: !!pl, shoji: false };
  var k; if (extra) for (k in extra) o[k] = extra[k];
  var r = W.suggest(o);
  return { cls: r.cls, label: r.label, dir: r.dir, pct: r.pct, recheck: r.recheck, notes: r.notes, steps: r.steps, basis: r.basis };
}
out.init = {
  inEarly: ini(2.0, 'early'),
  lowEarly: ini(1.3, 'early'),
  lowChg: ini(1.3, 'chg'),
  lowOk: ini(1.3, 'ok'),
  lowOk2: ini(1.8 - 0.3, 'ok', true),
  low16: ini(1.55, 'ok'),
  lowTrans: ini(1.3, 'ok', false, { transient: true }),
  lowThromb: ini(1.3, 'early', false, { thrombRisk: true }),
  hiEarly: ini(3.0, 'early'),
  hiOkSmall: ini(3.0, 'ok'),
  hiOkBig: ini(4.0, 'ok'),
  over5: ini(6.0, 'early')
};
out.shoji = [W.shojiEst(1.5, 1.6, 2.6, 14), W.shojiEst(1.0, 1.6, 2.6, 14), W.shojiEst(3.2, 1.6, 2.6, 14),
  W.shojiEst(1.5, 2.0, 3.0, 14), W.shojiEst(1.5, 1.6, 2.6, 21), W.shojiEst(2.2, 1.6, 2.6, 14)];
console.log(JSON.stringify(out));
""" % calc_js
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(driver)
        path = Path(fh.name)
    try:
        result = subprocess.run(
            [node, str(path)], capture_output=True, text=True, encoding="utf-8", check=False
        )
    finally:
        path.unlink(missing_ok=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def texts(case: dict) -> list[str]:
    return [row["text"] for row in case["rows"]]


def main() -> None:
    html = HTML_PATH.read_text(encoding="utf-8")
    index_html = INDEX_PATH.read_text(encoding="utf-8")
    service_worker = SW_PATH.read_text(encoding="utf-8")

    # --- iOS Safari 互換の記法（メインのスクリプト） --------------------
    main_js = html[html.index("<script>\n(function(){"): html.rindex("</script>")]
    for pattern, label in [
        (r"\bconst\s", "const"),
        (r"\blet\s", "let"),
        (r"=>", "arrow function"),
        (r"`", "template literal"),
    ]:
        assert not re.search(pattern, main_js), f"使わない記法が残っている: {label}"

    # --- 古い「週N日」方式が残っていない ---------------------------------
    for old in ["scheduleText", "function adjust(", "function schedule(", "pickedPct", "を週' + "]:
        assert old not in html, f"旧方式の名残: {old}"

    # --- 説明文の一致（description・og:description・一覧カード） --------
    desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    og = re.search(r'<meta property="og:description" content="([^"]+)"', html).group(1)
    assert desc == og, "description と og:description が違う"
    assert "毎日同じ量か、1日おき" in desc
    card = re.search(
        r'<a class="tool-card" href="warfarin_dose_adjuster\.html"[^>]*>.*?<div class="tool-desc">(.*?)</div>',
        index_html,
        flags=re.DOTALL,
    )
    assert card, "index.html にカードがない"
    assert card.group(1).strip() == desc, "一覧カードの説明が description と違う"
    assert "'./warfarin_dose_adjuster.html'" in service_worker

    # --- 計算 ---------------------------------------------------------------
    out = run_node(extract_calc_script(html))

    assert out["reg5"]["text"] == "1.5 mg と 1 mg を1日おき"
    assert out["reg5"]["avg"] == 1.25 and out["reg5"]["alt"] is True
    assert out["reg1"]["text"] == "0.5 mg を1日おき（間の日は飲まない）"
    assert out["reg4"]["text"] == "1 mg を毎日" and out["reg4"]["alt"] is False

    cases = out["cases"]
    # 1日 0.5 mg・1 mg からの減量は、0.5 mg きざみでは幅に入らない
    assert cases["d05"]["out"] is True
    assert texts(cases["d05"]) == ["0.5 mg を1日おき（間の日は飲まない）"]
    assert cases["d05"]["rows"][0]["band"] == "above" and cases["d05"]["rows"][0]["rp"] == 50
    assert cases["d10"]["out"] is True
    assert texts(cases["d10"]) == ["1 mg と 0.5 mg を1日おき"]
    assert cases["d10"]["rows"][0]["rp"] == 25
    # 0.25 mg きざみなら 1 mg からの減量も幅に入る
    assert cases["d10q"]["out"] is False
    assert texts(cases["d10q"]) == ["1 mg と 0.75 mg を1日おき"]
    assert cases["d10q"]["rows"][0]["rp"] == 13

    assert cases["d15"]["out"] is False
    assert texts(cases["d15"]) == ["1.5 mg と 1 mg を1日おき"]
    assert cases["d15"]["rows"][0]["rp"] == 17

    assert texts(cases["d25"]) == ["2.5 mg と 2 mg を1日おき", "2 mg を毎日"]
    assert [r["rp"] for r in cases["d25"]["rows"]] == [10, 20]

    assert texts(cases["d50"]) == ["4.5 mg を毎日", "4.5 mg と 4 mg を1日おき", "4 mg を毎日"]
    assert [r["rp"] for r in cases["d50"]["rows"]] == [10, 15, 20]

    # 曜日別入力（週 15.5 mg）：9.7% は丸めて 10% として幅に入れる
    assert texts(cases["w155"]) == ["2 mg を毎日"]
    assert cases["w155"]["rows"][0]["rp"] == 10

    # 幅に入る候補が4つ以上のときは 10・15・20% に近い3つに絞る
    assert texts(cases["up10"]) == ["11 mg を毎日", "11.5 mg を毎日", "12 mg を毎日"]

    # 同じ近さなら毎日同じ量を目安にする
    assert out["tie15"]["text"] == "2 mg を毎日"

    assert out["days"] == [1.5, 1, 1.5, 1, 1.5, 1, 1.5, 1, 1.5, 1, 1.5, 1, 1.5, 1]
    assert out["chg"] == ["現在より約20%減", "現在より約10%増", "現在とほぼ同じ"]
    assert out["fmtAvg"] == ["0.875", "2.25", "15.75", "2"]
    assert out["sweepBad"] == [], out["sweepBad"][:10]

    # --- 導入期 ---------------------------------------------------------------
    NOT_VALIDATED = "導入期に検証された方式ではありません"
    it = out["init"]
    assert it["inEarly"]["label"] == "継続" and it["inEarly"]["dir"] == 0
    assert it["inEarly"]["notes"] == []  # 目標域内では当てはめの注記を出さない
    assert "週1回" in it["inEarly"]["recheck"]
    for key in ["lowEarly", "lowChg"]:
        r = it[key]
        assert r["label"] == "継続して再検" and r["dir"] == 0, key
        assert "2-4日後" in r["recheck"], key
        # 候補を出さない「継続して再検」では、候補の当てはめの注記を出さない
        assert not any(NOT_VALIDATED in n for n in r["notes"]), key
    assert any("4-5日" in s for s in it["lowChg"]["steps"])
    assert any("5-7日" in s for s in it["lowEarly"]["steps"])
    assert it["lowOk"]["label"] == "増量" and it["lowOk"]["dir"] == 1 and it["lowOk"]["pct"] == 15
    assert it["low16"]["dir"] == 1 and it["low16"]["pct"] == 10
    assert any("2回続けば増量" in s for s in it["lowOk2"]["steps"])
    assert not any("2回続けば増量" in s for s in it["lowOk"]["steps"])
    assert it["lowTrans"]["dir"] == 0 and it["lowTrans"]["label"] == "継続して再検"
    assert any("ヘパリン等の併用を考慮" in n for n in it["lowThromb"]["notes"])
    assert it["hiEarly"]["label"] == "減量" and it["hiEarly"]["dir"] == -1 and it["hiEarly"]["pct"] == 15
    assert it["hiOkSmall"]["pct"] == 10 and it["hiOkBig"]["pct"] == 15
    for key in ["hiEarly", "hiOkSmall", "lowOk"]:
        assert any(NOT_VALIDATED in n for n in it[key]["notes"]), key
        assert "Table 3 の増減幅を導入期に当てはめ" in it[key]["basis"], key
    assert it["over5"]["label"] == "休薬"  # 5.0 以上は従来どおり

    # --- Shoji 2020 の式（参考値） -----------------------------------------
    sh = out["shoji"]
    assert sh[0]["ok"] is True and sh[0]["raw"] == 3.159 and sh[0]["mg"] == 3.5
    assert sh[1]["ok"] is False  # 初回 PT-INR 1.1 未満は式の対象外
    assert sh[2]["ok"] is False  # 推定値が 0 以下
    assert sh[3]["ok"] is False  # 目標 1.6-2.6 以外
    assert sh[4]["ok"] is False  # 1日 2 mg（週 14 mg）以外
    assert sh[5]["ok"] is True and sh[5]["mg"] == 2.0  # -2.009*2.2+6.172=1.752 -> 2.0

    # --- 画面の文言 ---------------------------------------------------------
    assert "導入期の開始量の目安" in desc
    assert 'id="initBox"' in html and 'id="startGuide"' in html
    assert html.count('class="lowStart"') == 7
    assert "PMID:31511484" in html and "PMID:35068386" in html

    print("ok: warfarin_dose_adjuster")


if __name__ == "__main__":
    main()
