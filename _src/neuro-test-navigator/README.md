# NeuroFind 公開版

公開URL: https://tools.ichisouzo-lab.com/neuro_test_navigator.html

2026-11-05更新：画面版 **2026.11.05-r4**。先生が確認したUI改善版を公開に反映。データ版は **2026.11.04.1**、131項目・参考74ページ・更新11項目の対応表を保持し、医学データは変更していない。

## 画面と生成用ソース

- `../../neuro_test_navigator.html`：配信する単一HTML。
- `page.html`：公開用の画面構造。PWA・canonical・謝辞を含む。
- `presentation.css`：基本スタイルとr4の表示改善を含む全スタイル。
- `app.js`：検索・比較・お気に入り・手動更新・持ち出しの動作。
- `export_public.py`：上の3ファイルへ確認済みHTMLの検査データを差し込み、配信HTMLと`publication.json`を生成する。

旧試作の画面に対する文字列変換をやめ、公開用テンプレートを画面の正本にした。新しい検査データを取り込んでも、承認済みr4の見た目・操作を保持する。

PowerShellでは先に `$env:PYTHONIOENCODING='utf-8'` を設定する。

```powershell
python _src/neuro-test-navigator/export_public.py --source <確認済みHTMLの絶対パス> --source-commit <入力元の完全なコミットSHA>
```

入力HTMLには`catalog-data`のJSONが1つ必要。入力と出力の医学データが一致しなければ停止する。`--check`はファイルを書き換えず、再生成結果が配信HTMLとバイト単位で一致することを検査する。

```powershell
python _src/neuro-test-navigator/export_public.py --source neuro_test_navigator.html --source-commit <完全なコミットSHA> --check
python _src/neuro-test-navigator/verify_public.py --artifacts <検証出力フォルダ>
```

## r4の操作改善

検索欄を上部にまとめ、詳細条件を開閉式にした。モバイルで分野とお気に入りへ直接アクセスできる。カード／一覧の選択をブラウザに保存。比較は2〜3件で実行し、選択中の検査を個別解除できる。詳細画面は内部をスクロールし、閉じるボタンを常時表示。保存や比較の操作後のスクロール位置とフォーカスを維持する。

## オフライン保存と更新

「HTMLを保存」「オフライン版を保存」で、検査データと全機能を含む単一HTML（末尾`_ui-r4.html`）を保存する。院内ではブラウザでファイルを開くだけで検索・詳細・比較を利用可能。公開ドメイン用のSW・manifest・アイコン等と、一時的な操作抑止属性は保存時に除く。出典リンクの閲覧にはネット接続が必要。

「データの手動更新」からJSONを書き出し、公式原典・変更通知を確認して編集し、取り込む。確認日は実際に確認した日、版番号は更新後の値を記録する。取り込み後のHTMLを保存して院内版を入れ替える。取り込みだけでは公開サイトは変わらない。

医学データの改訂では原典照合を別途行う。Web公開時は先生の明示承認、並走確認、バックアップ、SW版更新、動作・持ち出し検査、配信後検査を行う。過去の制作・照合資料は`KAZUSA_REVIEW.md`・`VALIDATION.md`と`publication.json`を参照。

## 謝辞・来歴

綾木先生の「脳内検査検索サイト」を着想と収録候補の照合に利用。謝辞と監修・提携がないことを画面に明記し、掲載条件は受託機関の公式資料で確認している。74行の対応表は「更新履歴と機能」→「検証資料・対応表を見る」に保持。

かずさ26項目は2026-11-04に追加。原典は元プロジェクト`sources/kazusa-20261104/`、追加データは`kazusa-20261104.json`、差分は`KAZUSA_REVIEW.md`。検査データのSHA256はr3から変更していない。
