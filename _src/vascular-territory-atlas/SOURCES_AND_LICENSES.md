# 解剖・神経束データと配布条件（2026-10-12）

## 取得元・版

- FSL公式配布 `fsl-data_atlases-2103.0-0.tar.bz2`。
  https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/public/noarch/fsl-data_atlases-2103.0-0.tar.bz2
  SHA256 `3ac89f5f67de84054e1e576c9ad5f7ef6f562cef7b2504a3fa992c079cf72f8c`。
- `sources/` はこの配布物から抽出した未加工の選択原ファイル。各ファイルのSHA256は `learning.json` の `data_provenance`。
- Harvard–Oxford cortical 48 / subcortical 21チャネル（2mm確率・maxprob-thr0・対応XML）。
- JHU **tractography** atlas 20チャネル（9左右ペアとforceps major/minor）。ICBM-DTI-81 labels atlasではない。
- どちらも配布画像の affine は `diag(-2,2,2,1)`、原点 `(90,-126,-72)`。FSL MNI152標準空間の画像として既存のFSL MNI152背景に重ねる。主血管ラベルは1mm、切り詰め後の原点 `(77,-112,-72)`。非線形の追加変形はしていない。
- 解剖・神経束の照会は副格子の完全な affine の逆行列を使う。MNIという名称だけで別のテンプレート世代を同一扱いせず、今後の追加時には空間・変形の適合を再確認する。

## 変更内容

- HO: 原maxprobラベルを最近傍で照会。候補は各2mm格子点の確率上位3個を `index+1` と0–100%で保存し、8近傍の候補を重みづけして連続補間する。確率は各候補間で正規化しない。小候補の省略と量子化を画面に注記する。
- JHU: 全20確率チャネルの値を未変更のuint8（0–100%）で埋め込む。2mm格子を保持し、三線形補間で断面表示・カーソル照会する。左右反転による補充も最大値での再正規化も行わない。
- 日本語名・教育用解説・検索/選択/表示UIを追加。代表位置は各チャネルの最大値の格子点で、束の唯一の中心や機能局在を意味しない。
- 複数束の重なりでは表示色を混合する。混合色の重みづけは視覚合成だけであり、元の確率表示を100%に直さない。
- SLFの枝別、独立したAF、視放線、脳弓は本atlasにないため追加しない。SLFとtSLFは重なりうる。
- 3D追加: 元2mm格子で閾値以上の領域の6近傍境界を全点抽出する。3D画質による追加間引きや、線維曲線・軸索・方向の生成は行わない。原確率とaffineは変更しない。
- 3Dは各束の手前側の面をZバッファで描き、束間は半透明で色合成する。重なりの前後関係は厳密に判定できない。面の不透明度と確率による色の明るさは表示用であり、原確率の正規化ではない。
- 既存血管atlasの外形を薄い脳表参照に使う。HOは3Dカーソル位置の部位名参照に使い、HOの灰白質表面を生成していない。

## Harvard–Oxford: CC BY-SA 4.0

原データ名: Harvard–Oxford Cortical/Subcortical Structural Atlases。
Harvard Center for Morphometric Analysisの分割データを基礎にFSLが配布。
FSLの公式謝辞は David Kennedy、Christian Haselgrove、Bruce Fischl、Janis Breeze、Jean Frazier、Larry Seidman、Jill Goldsteinと各所属・研究支援への謝辞を含む。
原作者・提供者の正式な説明は https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html#harvard-oxford-cortical-and-subcortical-structural-atlases 。
公式ライセンスは https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html 。
全文は `licenses/CC-BY-SA-4.0.txt`。上記改変を明示し、改変データは同じCC BY-SA 4.0で提供する。作者の推奨・承認を意味しない。

## JHU: FSL非商用条件

原データ名: JHU White-Matter Tractography Atlas。Susumu Mori / Laboratory of Brain Anatomical MRI, Johns Hopkins University 提供。
原著: Hua et al. (2008), Tract Probability Maps in Stereotaxic Spaces, NeuroImage 39:336–347。 https://pmc.ncbi.nlm.nih.gov/articles/PMC2724595/ 。
無償・非商用の教育用途で提供する。financial returnを伴う用途は本許諾の対象外。受領者にも同じ条件を引き継ぐこと。
複製・改変・送信・移転の条件、原/改変sourceを含める条件、免責・無保証等を省略せず `licenses/FSL-LICENSE.txt` に同梱する。公式取得ページの原HTMLも `licenses/FSL-official-license.html` に保存。
単体HTMLだけを再配布せず、`sources/` の採用原NIfTI/XML、`build_learning.py`・`build_data.py`・`learning.js`・`template.html`・説明/変更記録等を含む本パッケージを一緒に配布する。
FSL全体をインストール・同梱したものではない。データの条件と、各データ/説明/プログラムの権利は一括して別のライセンスへ変更しない。

## 解説の根拠と限界

`learning.json` の参考資料は、部位の定義/atlas生成根拠と、別研究での機能・症候の関連を区別する。
JHU束の機能・関連症候は依頼元の一次資料照合済みの情報から、研究集団と関連という限定を維持して採用した。
HOの機能は NINDS の大区分の説明と既存 `content.json` / `evidence.md` の確認済み文献を再利用した概説。各細分ラベルの固有機能が検証されたという意味ではない。扁桃体・側坐核等の個別症候は断定していない。
集団分布は患者個人の線維の存在確率、結合強度、機能強度、障害率ではない。低確率域が非表示でも線維の不存在とは判断しない。
