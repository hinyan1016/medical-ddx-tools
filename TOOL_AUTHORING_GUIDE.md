# 医学診断ツール作成ガイド

> このファイルは Claude_task_new/CLAUDE.md から分離した詳細ガイド。**新規診断ツールを作成・改修するときは必ず本ファイルを読むこと**。

## ファイル構成
- ツール本体: `C:\Users\jsber\OneDrive\Documents\Claude_task_new\medical-ddx-tools\`
- 全ツール単一HTMLファイル（CSS・JS内包、外部依存なし）
- `index.html` — ツール一覧ページ（カード型リンク集）
- `sw.js` — Service Worker（キャッシュ管理）
- `manifest.json` — PWA設定

## 新規ツール作成時の全手順
1. **HTMLファイル作成** — 下記アーキテクチャに従い `<tool_name>.html` を作成
2. **index.htmlにカード追加** — 適切な位置に `<a class="tool-card">` ブロックを追加
3. **sw.js更新** — ASSETS配列に `'./<tool_name>.html'` を追加し、`CACHE_NAME` のバージョンを1つ上げる（例: `ddx-tools-v8` → `ddx-tools-v9`）
4. **git commit & push** — `git add <files> && git commit && git push origin main`
5. **デプロイ確認** — 45秒待機後、WebFetchで `https://hinyan1016.github.io/medical-ddx-tools/<tool_name>.html` を確認

## HTMLテンプレート構造（`<head>`必須要素）
```html
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<script>if('serviceWorker'in navigator){navigator.serviceWorker.getRegistrations().then(function(r){r.forEach(function(reg){reg.update()})});navigator.serviceWorker.addEventListener('message',function(e){if(e.data&&e.data.type==='SW_UPDATED')window.location.reload()})}</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#XXXXXX">
<meta name="apple-mobile-web-app-capable" content="yes">
<link rel="manifest" href="manifest.json">
<link rel="apple-touch-icon" href="icons/icon-192.png">
<title>ツール名</title>
```
- `<meta charset>` 直後にSW強制更新スクリプト（必須、省略不可）
- `theme-color` はツールごとのテーマカラーに合わせる

## JSアーキテクチャ
```
DISEASES = { disease_id: { name, category, description, tags: {step_id: [tag_ids]}, keyFindings, workup } }
STEPS = [ { id, title, subtitle, multi, options: [{id, label, icon}] } ]
calcScores(answers) → {disease_id: score}
rankDiseases(scores) → [{id, score, ...}]
getProbLevel(score) → "high"/"moderate"/"low"/"very_low"
render() → DOM更新
```

## JS記法ルール（ブラウザ互換性）
- `var` を使用（`const`/`let` ではなく）
- `function(){}` を使用（アロー関数 `=>` ではなく）
- render()内は文字列連結（テンプレートリテラルではなく）
- これによりiOS Safari古いバージョンなどでの互換性を確保

## テーマカラー一覧（既存ツール）
| ツール | primary-dark | primary | 用途 |
|--------|-------------|---------|------|
| AKI | #1A5276 | #2E86C1 | 腎臓系 |
| 浮腫 | #1A5276 | #2E86C1 | 腎臓系 |
| 低Na | #1A5276 | #2E86C1 | 電解質 |
| 高Na | #1A5276 | #2E86C1 | 電解質 |
| 高CK | #1A5276 | #2E86C1 | 筋疾患 |
| 低K | #1A5276 | #2E86C1 | 電解質 |
| 高BUN | #1A5276 | #2E86C1 | 腎臓系 |
| 腹痛 | #1A5276 | #2E86C1 | 消化器 |
| 両側視床 | #4A0E4E | #7B2D8E | 神経画像 |
| 感覚性PN | #1A5276 | #2E86C1 | 神経 |
| 二次性高血圧 | #8B1A1A | #C0392B | 循環器 |
| 外転神経麻痺 | #1A5276 | #2E86C1 | 神経 |
| PN鑑別・検査 | #2C6E49 | #4C956C | 神経 |
| 神経局在 | #1A5276 | #2E86C1 | 神経 |
| 多発脳神経 | #1A5276 | #2E86C1 | 神経 |

## index.htmlカード形式
```html
<a class="tool-card" href="<tool_name>.html">
  <div class="tool-emoji">絵文字</div>
  <div class="tool-name">ツール名</div>
  <div class="tool-desc">説明文</div>
  <span class="tool-tag">Nステップ / N疾患鑑別</span>
</a>
```

## Service Worker (sw.js) 仕様
- CACHE_NAME: `ddx-tools-vN`（新ツール追加ごとにN+1）
- ASSETS配列: 全HTML + manifest.json + icons
- フェッチ戦略: HTML=network-first / 静的アセット=cache-first
- activateイベントで古いキャッシュ削除 + `SW_UPDATED` postMessage
- 各HTMLのheadにSW更新リスナー（上記テンプレート参照）

## 参考ブログ記事からツール作成する際の流れ
1. WebFetchでブログ記事の内容を取得
2. 疾患リスト・鑑別ステップ・検査項目を抽出
3. 医学的正確性を確認（ガイドライン・基準値の照合）
4. 上記アーキテクチャに従いHTMLファイルを作成
5. index.html・sw.js更新 → git push → デプロイ確認

## 既知の注意点
- render()内でダブルクォートを含む文字列（例: "vanishing tumor"）は文字列連結で安全に処理する
- 空ページ問題の主原因はSWキャッシュ。sw.jsのバージョンを必ず上げること
- GitHub Pagesデプロイには約30-60秒かかる
- 公開URLは独自ドメイン `tools.ichisouzo-lab.com`（github.io は301でここへ転送）
