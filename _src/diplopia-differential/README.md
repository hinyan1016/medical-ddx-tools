# 成人の複視｜初診時の鑑別支援（ソース）

公開ファイル `diplopia-differential.html` は、ここの `page.html` に図版を埋め込んで書き出したものです。

- `page.html` … 本体（CSS・JS内包）。編集はこのファイルに行う
- `fig-*.webp` … 埋め込む図版（幅1280px）
- `build.py` … 公開ファイルを書き出す
- `cases.test.js` … 判定ロジックの回帰テスト（代表症例、3段階法、入力方式の往復）

```
python _src/diplopia-differential/build.py
node _src/diplopia-differential/cases.test.js
```

公開時は `sw.js` の `CACHE_NAME` を1つ上げる（TOOL_AUTHORING_GUIDE.md）。

## 判定の構成

1. `motPattern` … 左右の眼の運動制限の組み合わせから局在パターンを決める
2. `assess` … 緊急所見・遮閉・問診・診察とパターンから、警告・候補・未確認項目を作る
3. `handoff` … 申し送り文を作る（波ダッシュは半角ハイフンに置換）

判定を変えたら `cases.test.js` に症例を足す。
