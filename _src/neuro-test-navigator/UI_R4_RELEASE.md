# UI r4 公開記録

2026-11-05。先生の「はい、この改善版を公開サイトに反映してください。」という承認に基づく。

## 対象

画面版`2026.11.05-r4`。検索を中心にした画面、モバイルの分野選択・お気に入り、詳細条件の開閉、条件の解除、比較の個別解除、表示形式の記憶、詳細画面のスクロールとフォーカスを改善。医学データ版`2026.11.04.1`の131項目は保持。

承認された候補と配信HTMLのSHA256：
`2d1d61a3e1954d6961deef92603195693cdb2adf2c7e6eb904a3e3c42e048f9a`

医学カタログSHA256（前版と一致）：
`a0dc773de8749b5f0a43a5e080f2c418d8e676421c9bbcbec75c028cf7e919e4`

## 変更ファイル

- `neuro_test_navigator.html`：承認済み公開候補を反映。
- `sw.js`：`ddx-tools-v333` → `ddx-tools-v334`。
- `_src/neuro-test-navigator/page.html`：公開用レイアウトの正本を追加。
- `_src/neuro-test-navigator/app.js`・`presentation.css`：承認済みの動作・見た目。
- `_src/neuro-test-navigator/export_public.py`：テンプレートと検査データから生成。再生成一致を検査する`--check`を追加。
- `_src/neuro-test-navigator/publication.json`：配信HTML・テンプレート・CSS・JS・カタログのSHA。
- `_src/neuro-test-navigator/verify_public.py`：保存名と画面版の検査を公開記録の値に追従。
- `_src/neuro-test-navigator/public-validation.json`・`VALIDATION.md`：公開前検査。
- `_src/neuro-test-navigator/README.md`・本記録：生成方法・公開範囲・戻し方。

## 保全と並走確認

自宅用PCで作業。公開直前にチャット一覧を確認し、関連する別チャットはidle。他の変更を含めず、上の明示対象だけをコミットする。

着手時のHTMLは`work/neurofind-ui-20261105/original.html`、公開作業前の10ファイルは`work/neurofind-ui-20261105/publish-backup-20261105/`に保存。`inventory.json`に元ファイルのSHAを記録した。承認候補・差分・検収画像も同じ作業フォルダに保存。

## 検証

`VALIDATION.md`と`public-validation.json`を参照。公開前の実ブラウザ検査はexit 0、承認候補との完全一致と再生成の一致も確認。公開処理とPythonの独立レビューはいずれも重要指摘0件。テンプレート末尾の改行位置のみソース上で整理し、配信HTMLの完全一致は再確認した。

公開後の配信確認は、ローカル検査と区別して`live-validation.json`に記録する。

## 戻し方

公開コミットの親は`ab42268e75b6171d2720ed388ba9db6e425036a9`。戻す必要が生じたら、公開コミットをrevertし、SWの版は既使用の番号に戻さず新しい番号へ上げて再配信する。公開履歴を書き換えるforce pushは使わない。個別ファイルは上のバックアップとSHAから復元できる。
