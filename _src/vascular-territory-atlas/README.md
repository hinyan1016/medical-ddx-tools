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
