# vascular-territory-atlas（ソース）

公開ファイル `../../vascular-territory-atlas.html` はこのフォルダから生成する。**公開ファイルを直接編集しない。**
`_` で始まるフォルダなので GitHub Pages（Jekyll）では配信されず、`check_sw_cache.py` の走査対象にも入らない。

| ファイル | 役割 |
|---|---|
| `template.html` | ビュアー本体（HTML/CSS/JS）。JS は ES5 のみ（`build.py` が検査する） |
| `content.json` | 臨床解説・症候タグ・参考文献（PubMed 逆引き確認済みのものだけ） |
| `evidence.md` | content.json の主張 → 文献 → 抄録/全文の該当箇所の対応表（監査用） |
| `atlas_data.bin.gz` | 埋め込むボリューム（`build_data.py` が作る） |
| `build_info.json` | 背景画像の出典表示など、データ由来の表記 |
| `build_data.py` | NIfTI（または旧版HTML）→ `atlas_data.bin.gz` |
| `build.py` | template + content + data → 公開HTML（`--zip` で downloads/ の単体版も） |
| `test_atlas.py` | Playwright での動作確認（座標の左右・代表断面・NIfTI 読込・inflate 互換など） |
| `README_offline.txt` | 単体版 ZIP に同梱する説明 |

原著全文は `medical-content/scripts/pubmed_fulltext.py --pmid 36739282 --dump <path>` で取り直せる（PMC9899211）。

## 作り直し

```bash
PY="/c/Users/jsber/AppData/Local/Programs/Python/Python313/python.exe"; [ -x "$PY" ] || PY=python
# 1) データ（原データは NITRC https://www.nitrc.org/projects/arterialatlas/ ・要ログイン（Google ログイン可）。リポジトリには入れない）
#    使うのは Atlas_MNI152.zip（2021-11 公開）の Atlas_182_MNI152/。ArterialAtlas.zip（2021-10）の Atlas_182/ は
#    ボクセル値は同じだが sform の原点が 0 になっている（MNI 座標がずれる）ので使わない。
D=<展開先>/Atlas_182_MNI152
PYTHONIOENCODING=utf-8 "$PY" build_data.py --l1 $D/ArterialAtlas.nii --l2 $D/ArterialAtlas_level2.nii   --prob $D/ProbArterialAtlas_average.nii --bz $D/BorderZone_ProbAve.nii \n  --t1 <tpl-MNI152NLin6Asym_res-01_desc-brain_T1w.nii.gz> --out atlas_data.bin.gz
#    T1 は TemplateFlow から: https://templateflow.s3.amazonaws.com/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-01_desc-brain_T1w.nii.gz（約3.3MB）
# 2) 公開HTMLと単体版ZIP
PYTHONIOENCODING=utf-8 "$PY" build.py --zip
# 3) 動作確認（exit 0 = 合格）
PYTHONIOENCODING=utf-8 "$PY" test_atlas.py
```

公開前は `sw.js` の `CACHE_NAME` を1つ上げ、`check_sw_cache.py` を通す。

## 解剖・神経束の追加（2026-10-12 改修）

- `learning.json`: 日本語/英語名、解剖・機能・関連症候・出典と全20構造の共通レジストリ。
- `learning.js`: 完全affineによる位置照会、候補表示、検索/複数選択、断面確率オーバーレイ、URL状態。
- `build_learning.py`: FSL配布元NIfTI/XMLから `learning_data.bin.gz` を生成。既存 `atlas_data.bin.gz` を変更しない。
- `sources/` / `licenses/` / `SOURCES_AND_LICENSES.md`: 元データ、対応XML、ライセンス全文、出典と改変記録。
- `test_learning.py`: 原画像との全チャネル照合、左右/名前/ラベル番号、回転・せん断/補間、UI・URL・オフライン検証。

```powershell
$env:PYTHONIOENCODING='utf-8'
python build_learning.py --inputs sources
python build.py --zip
python test_atlas.py --shots <検証画像の保存先>
python test_learning.py --shots <追加機能の検証画像の保存先>
```

全20構造は11束種（9組の左右別領域＋2交連領域）。SLF側頭部をAFと同一視しない。
神経束は断面と3Dで確率領域を表示。`learning_3d.js` は元2mm格子の閾値境界を追加間引きせず点群化する。
「選択した神経束を3Dで見る」または3Dの表示内容「神経束（確率分布）」を使う。
断面と選択・閾値・不透明度を共有し、3Dの薄い脳表参照を切り替えられる。3Dの黄色のカーソル印にはHOの位置名も表示する。
各束の手前側の面を個別Zバッファで描き、複数束を半透明色合成する。重なりの前後関係を厳密に判定する描画ではない。
3Dの面の不透明度はスライダー、確率は色の明るさに反映する。断面は確率に応じた不透明度なので見え方は同一ではない。
`test_learning_3d.py --shots <保存先>` で原境界一致、左右/交連、回転/ズーム、閾値、モバイル等を確認する。
既存3Dの血管・病変モードも保持。個人のstreamline、軸索、走行方向は描画しない。
解剖ラベルは原maxprob最近傍、候補確率は2mm各格子点の上位3候補を補間（小候補の省略を表示）。
神経束確率は2mmのまま保持し、選択された束だけを断面上で連続補間する。
異なるatlasを追加するときは `learning.json` にatlas/volume/channel/side/source等を登録し、同形式のボリュームをpackする。
名前や左右をコードに固定せず、複数束の重なりを許す。許諾・テンプレート・affineの確認なしに新データを加えない。
詳細な配布条件は `SOURCES_AND_LICENSES.md`。単体HTMLの再配布時もソース一式を省略しない。

## 座標の約束

- ボリュームは x 最速（`idx = i + j*nx + k*nx*ny`）。各ボリュームに voxel→MNI(mm) の affine を持たせ、
  ビュアーは affine から MNI 座標・左右・断面の向きを決める（2026-10-08 以前の版は X の符号が逆で、
  代表断面も 24mm 上にずれていた）。
- 放射線科式の表示では画面の左が患者の右（MNI の x が正）。
- ラベル番号は原データの `ArterialAtlasLables.txt` のとおり（奇数=左・偶数=右、31/32 は側脳室）。
  Level 2 は Level 1 からの写像で作る（`L1_TO_L2`）。

## 臨床解説の約束

- 「このアトラスで塗られている範囲」と「教科書的な灌流域」を分けて書く。原著は MLS（内側レンズ核線条体）を
  脳梁の位置、ACTP（前脈絡叢・視床穿通）を内側側頭葉・海馬の位置として、解剖学的知識で定義している。
  延髄は外側も含めて B（脳底動脈）に塗られている。
- 引用は PubMed 逆引きで実在と内容を確かめたものだけ。`evidence.md` に根拠の抜粋を残す。

## データの約束（2026-10-08 に 1mm 原データへ移行）

- 原データに T1 は同梱されていない。背景 T1 は FSL 同梱の MNI152（MNI152NLin6Asym、Janke AL）を TemplateFlow から取得（2026-10-08 先生選択）。
  アトラスの FSL 格子と格子点が一致する（向きだけ逆で、`build_data.py` が並べ替える）。明示のライセンス文は見つかっていない（TemplateFlow の LICENSE 欠落）。
  7bit に落として x 方向の差分で格納し、ビュアーで累積和に戻す。旧版の 2mm 背景とは相関 0.95（同系統）。
- 確率マップ（平均法）と境界領域（MCA/ACA・MCA/PCA の確率比）は、原著が右半球の病変を左右反転して左半球にまとめて作っているため、
  左半球にしか値がない。`build_data.py` は右半球を左半球の左右反転で埋める（`--no-mirror` で無効）。画面にも注記している。
- 確率マップは 2×2×2 で平均して 2mm にし、血管ごとに最大値で 0–255 に量子化する（0 でない値は 1 以上に残す）。境界領域は 1mm のまま比×50 で保存。
- Level 2 は Level 1 からの写像で作る。原データの ArterialAtlas_level2.nii とは 318 ボクセル（主に脳室の縁）が食い違うが、写像のほうを採る。
