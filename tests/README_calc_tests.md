# スコア計算ツールの照合テスト

スコア系ツール12本（ABCD2・ASPECTS・BFCRS・CAVE・Fazekas・GLIM・HIT-6・MIBS-4・MIDAS・NEWS2・リフィーディング・SeLECT）について、
実際のページをヘッドレスブラウザで開いてボタン・入力欄を操作し、表示された点数・区分を各原著の配点表と照合します。
期待値は各テストファイル内の参照実装（原著の表をそのまま書き下したもの）で計算しており、ページのコードは参照していません。
原典は各ファイル冒頭の docstring に記載しています。

## 実行方法

```bash
pip install pytest playwright
python -m playwright install chromium   # 初回のみ
python -m pytest tests/test_news2_calculator.py tests/test_abcd2_calculator.py tests/test_cave_score.py \
  tests/test_select_score.py tests/test_bfcrs_calculator.py tests/test_aspects_calculator.py \
  tests/test_fazekas_calculator.py tests/test_headache_scales.py tests/test_nutrition_criteria.py
```

各ファイルは `python tests/test_news2_calculator.py` のように単体でも実行できます。
Chromium を別の場所に置いている場合は `PLAYWRIGHT_CHROMIUM_EXECUTABLE` にパスを指定してください。

## 既知の不具合（xfail）

- `test_nutrition_criteria.py::test_refeeding_aspen_exact_boundaries`
  リフィーディングツールの ASPEN 2020 重症度判定で、低下率を丸めずに比較しているため、
  ちょうど10%・20%の低下が一段軽く、ちょうど30%の低下が重症に判定されます。ページ側を直したら `xfail` を外してください。
