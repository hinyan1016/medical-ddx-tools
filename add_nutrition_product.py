# -*- coding: utf-8 -*-
"""必要エネルギー・タンパク質・水分量計算ツールに栄養剤を1つ追加する。

calorie_protein_calculator.html の EXTRA_PRODUCTS に1行足し、sw.js の CACHE_NAME を1つ上げる。
追加した製剤は、製剤一覧表・白湯プランの選択ボタン・組み合わせ計算の選択肢に自動で出る。
手順書：calorie_protein_calculator_PRODUCTS.md

使い方:
  python add_nutrition_product.py --name "ペプタメン スタンダード" --kubun 食品 \
      --amount 200 --unit mL --count パック --kcal 300 --protein 10.5 --water 156 \
      --note "消化態・1.5kcal/mL" --source "メーカー製品情報 2026-11-01確認"
  python add_nutrition_product.py ... --dry-run     # 書き込まずに点検だけ
  python add_nutrition_product.py --list            # 追加済みの製剤を表示
  python add_nutrition_product.py --remove "品名"   # 追加分から1件外す

exit: 0=成功 / 1=点検で不合格（何も書き込まない）
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]

HERE = Path(__file__).resolve().parent
MARKER = "// @@EXTRA_PRODUCTS@@"
LINE_RE = re.compile(r"^    \{ name: .*\},(?=\r?$)", re.M)


def read(p: Path) -> str:
    return p.read_bytes().decode("utf-8")


def write(p: Path, s: str) -> None:
    p.write_bytes(s.encode("utf-8"))  # 改行コードを作り替えない


def existing_names(html: str) -> list[str]:
    names = re.findall(r"\bname: '([^']+)'", html)  # 既存18製剤（シングルクォート）
    names += re.findall(r'\bname: "([^"]+)"', html)  # 追加分（JSON 形式）
    return names


def extra_lines(html: str) -> list[str]:
    block = html[html.index("var EXTRA_PRODUCTS = ["):html.index(MARKER)]
    return LINE_RE.findall(block)


def check(a) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    if a.kcal <= 0:
        errors.append("kcal は 0 より大きくしてください")
    if a.protein < 0 or a.water < 0 or a.amount <= 0:
        errors.append("protein・water は 0 以上、amount は 0 より大きくしてください")
    if a.protein * 4 > a.kcal:
        errors.append(f"タンパク質のエネルギー（{a.protein:g}g×4＝{a.protein * 4:g}kcal）が総エネルギー {a.kcal:g}kcal を超えています")
    if a.unit == "mL":
        if a.water > a.amount:
            errors.append(f"水分 {a.water:g}mL が容量 {a.amount:g}mL を超えています")
        elif a.amount > 0 and not (0.3 <= a.water / a.amount <= 0.95):
            warns.append(f"水分の割合が {a.water / a.amount * 100:.0f}% です（多くの製剤は 50〜90%）。値を確かめてください")
        if a.amount > 0 and a.kcal / a.amount > 2.5:
            warns.append(f"エネルギー濃度が {a.kcal / a.amount:.2f} kcal/mL と高めです。値を確かめてください")
    if not a.source:
        warns.append("--source（出典と確認日）が空です。添付文書やメーカー資料の確認日を残すことを勧めます")
    return errors, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="計算ツールに栄養剤を1つ追加する")
    ap.add_argument("--name", help="品名（画面に出る名前）")
    ap.add_argument("--kubun", choices=["医薬品", "食品"], help="区分")
    ap.add_argument("--amount", type=float, help="1本（1パック）の量。例 200")
    ap.add_argument("--unit", default="mL", help="量の単位。mL か g（既定 mL）")
    ap.add_argument("--count", help="数え方。例 本・パック・袋・缶")
    ap.add_argument("--kcal", type=float, help="1本あたりのエネルギー kcal")
    ap.add_argument("--protein", type=float, help="1本あたりのタンパク質 g")
    ap.add_argument("--water", type=float, help="1本あたりの水分 mL")
    ap.add_argument("--note", default="", help="特徴の一言（一覧表に出る）")
    ap.add_argument("--source", default="", help="出典と確認日（画面には出さない）")
    ap.add_argument("--no-tube", action="store_true", help="経管では使わない（白湯プランの選択ボタンに出さない）")
    ap.add_argument("--reference", action="store_true", help="主要製剤ではなく参考製剤として扱う（初期表示に出さない）")
    ap.add_argument("--dry-run", action="store_true", help="書き込まずに点検だけする")
    ap.add_argument("--list", action="store_true", help="追加済みの製剤を表示する")
    ap.add_argument("--remove", metavar="品名", help="追加分から指定した品名の1件を外す")
    ap.add_argument("--html", default=str(HERE / "calorie_protein_calculator.html"))
    ap.add_argument("--sw", default=str(HERE / "sw.js"))
    a = ap.parse_args()

    html_p, sw_p = Path(a.html), Path(a.sw)
    html = read(html_p)
    if MARKER not in html:
        print(f"!! {html_p.name} に {MARKER} が見つかりません。中断します。")
        return 1
    nl = "\r\n" if "\r\n" in html else "\n"

    if a.list:
        lines = extra_lines(html)
        print(f"追加済み {len(lines)} 件")
        for ln in lines:
            print("  " + ln.strip())
        return 0

    if a.remove:
        lines = [ln for ln in extra_lines(html) if json.dumps(a.remove, ensure_ascii=False) in ln]
        if len(lines) != 1:
            print(f"!! 追加分に「{a.remove}」が {len(lines)} 件あります（1件だけのときに外せます）。")
            return 1
        new_html = html.replace(lines[0] + nl, "", 1)
        action = f"外しました：{a.remove}"
    else:
        missing = [k for k in ("name", "kubun", "amount", "count", "kcal", "protein", "water") if getattr(a, k) is None]
        if missing:
            print("!! 必須の項目がありません: " + ", ".join("--" + m for m in missing))
            return 1
        if a.unit not in ("mL", "g"):
            print("!! --unit は mL か g にしてください")
            return 1
        errors, warns = check(a)
        if a.name in existing_names(html):
            errors.append(f"「{a.name}」はすでに登録されています")
        for w in warns:
            print("  注意: " + w)
        if errors:
            for e in errors:
                print("!! " + e)
            print("点検で不合格のため、何も書き込みません。")
            return 1
        entry = {"name": a.name, "kubun": a.kubun, "amount": a.amount, "amountUnit": a.unit, "count": a.count,
                 "kcal": a.kcal, "protein": a.protein, "water": a.water}
        if a.no_tube:
            entry["tube"] = False
        if a.reference:
            entry["main"] = False
        if a.note:
            entry["note"] = a.note
        if a.source:
            entry["source"] = a.source
        def js(v):
            if isinstance(v, float) and v.is_integer():
                v = int(v)  # 200.0 → 200
            return json.dumps(v, ensure_ascii=False)
        body = ", ".join(f"{k}: {js(v)}" for k, v in entry.items())
        line = "    { " + body + " },"
        idx = html.index(MARKER)
        line_start = html.rfind("\n", 0, idx) + 1
        new_html = html[:line_start] + line + nl + html[line_start:]
        action = "追加します：" + line.strip()

    if a.dry_run:
        print("[dry-run] " + action)
        return 0

    sw = read(sw_p)
    m = re.search(r"ddx-tools-v(\d+)'", sw)
    if not m:
        print("!! sw.js の CACHE_NAME が見つかりません。中断します。")
        return 1
    v = int(m.group(1))
    write(html_p, new_html)
    write(sw_p, sw.replace(m.group(0), f"ddx-tools-v{v + 1}'", 1))
    print(action)
    print(f"sw.js の CACHE_NAME を v{v} → v{v + 1} に上げました。")
    print("次に: python check_sw_cache.py → ブラウザで表示を確認 → コミットして push")
    return 0


if __name__ == "__main__":
    sys.exit(main())
