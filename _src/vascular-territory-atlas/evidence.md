# 根拠台帳：MNI脳血管支配領域 3Dアトラス 臨床解説（content.json 2026-10-08版）

- 対象：`content.json`（同フォルダ）の全文。独立監査エージェントの照合用。
- 作成日：2026-10-08
- 照合方法：
  - 実在確認：`medical-content/scripts/pubmed_verify.py --pmid <PMID> --expect-author --expect-year --expect-journal`（全35本 exit 0）。さらに `--file content.json` の一括照合で DOI 34件すべて OK・exit 0（Pritchard 1999 は DOI なしのため PMID 個別照合のみ）。
  - 主張の照合：PubMed 抄録（E-utilities efetch）を読み、PMC 全文がある2本（Liu 2023 = PMC9899211、Thapliyal 2022 = PMC10041230）は `pubmed_fulltext.py` で全文を取得して該当箇所を確認した。他の33本は PMC 全文なし（`pubmed_fulltext.py` exit 2＝全文未確認）のため、**抄録に書かれている範囲だけ**を主張に使った。
  - 統計値は Liu 2023 の「ACA 群 29 例」「排他的病変 10 例未満」以外は content.json に書いていない（頻度は「多い・少ない」の定性表現にとどめた）。

## 0. 全体に関わる前提

| # | 前提 | 根拠 |
|---|---|---|
| P1 | `{contra}`／`{ipsi}` の付与は、運動路・感覚路が交叉する（大脳・視床・脳幹の病変で対側に症状が出る）、脳神経核・小脳半球・下行性交感神経路の障害は同側に出る、という基本解剖に基づく。抄録が側性を明記している箇所は表中に示し、明記がない箇所は「側性：基本解剖」と注記した。 | 標準神経解剖（個別文献なし） |
| P2 | 「このアトラスで塗られている範囲」（atlas_region）は、原著の定義（下記 A 群）と、依頼者が 2mm データで代表座標を確認した結果（下記 A-coord）に基づく。座標確認は概算で、1mm データでの再確認は未了（依頼者が後日実施予定）。私（作成者）はアトラス画像を独自に再測定していない。 | 依頼文・Liu 2023 |
| P3 | 「左半球＝通常の優位半球」として失語系の症候を symptoms_left／tag side=left_hemi に置いた（Kreisler 2000 等の抄録は対象半球を明記していない）。 | 一般的事項 |

### A. アトラス定義（Liu 2023・PMC 全文で確認）

| # | 主張 | refkey | 原文抜粋（全文） |
|---|---|---|---|
| A1 | 急性期脳梗塞 1,298 例。心原性・両側・境界領域のみ・多発は除外 | liu2023 | "580 individuals were excluded because their stroke was (1) of confirmed cardioembolic origin, (2) bilateral, (3) exclusively within "watershed" areas, or (4) multifocal..." |
| A2 | MCA・PCA の葉別区分は脳回の解剖学的ランドマークで区切った | liu2023 | "The "lobar" sub-areas of MCA (frontal, parietal, temporal, insular, occipital) and PCA (occipital, temporal), were defined based on classic anatomical landmarks (gyri...)" |
| A3 | LLS・PCTP・小脳/脳底の下位区分は確率マップの比で決めた | liu2023 | "The same procedure, based on probability ratios, was applied to define the sub-territories of lateral lenticulostriate (within MCA), thalamoperforating (within PCA), and ... cerebellar and basilar (within VB) arteries." |
| A4 | MLS・ACTP は排他的病変 10 例未満のため解剖学的知識で定義 | liu2023 | "...medial lenticulostriate and anterior thalamopeforating (that have less than 10 cases of exclusive lesions in each)... we chose to rely on prior anatomical knowledge." |
| A5 | MLS＝脳梁の位置 | liu2023 | "The medial lenticulostriate territory, within ACA, corresponds to the topography of corpus callosum." |
| A6 | ACTP＝内側側頭葉・海馬の位置、PCA に含まれる | liu2023 | "The anterior thalamoperforating territory, within PCA, corresponds to the topography of the mesial temporal area and hippocampus." |
| A7 | 領域名（PCTP＝後脈絡叢・視床穿通、ACTP＝前脈絡叢・視床穿通、IC/SC/basilar） | liu2023 | "PCA (temporal (PCAt), occipital (PCAo), Posterior Choroidal and Thalamoperforating (postChThp), Anterior Choroidal and Thalamoperforating (antChThp)), and VB (inferior cerebellar (IC), superior cerebellar (SC), and basilar)" |
| A8 | ACA 群は 29 例と少なく境界の精度に限界 | liu2023 | Table 1 "Number of DWIs 1298 29 ..." / "ACA strokes were less represented in our sample which might had affected the definition of border zones." |
| A9 | MCA/PCA 境界は確率マップの比で決めた | liu2023 | "a ratio of p MCA / p PCA > 1 indicates that the given "border zone" voxel is more often affected in MCA strokes than in PCA strokes" |
| A10 | 高齢者の側脳室はテンプレートより大きい | liu2023 | "aged subjects' lateral ventricles are usually larger than the template's lateral ventricles" |
| A11 | 30 領域＋脳室 | liu2023 | "ArterialAtlas.nii: Image defining 30 arterial territories and ventricles." |

### A-coord. 依頼者提供の代表座標確認（2mm・概算）

LLS＝被殻・淡蒼球・尾状核・内包（前脚・膝・後脚）・放線冠／PCTP＝視床・外側膝状体付近・中脳（大脳脚・被蓋）／ACTP＝海馬体部（扁桃体・鉤は MCAT）／B＝橋と延髄（内側・外側とも。延髄外側も B）／IC＝小脳下部／SC＝小脳上部（中脳レベルの虫部上部を含む）／MLS＝脳梁膝部〜体部／脳梁膨大部＝PCAO／楔前部＝ACA／Broca 野・中心前回の手の領域・前頭眼野＝MCAF／角回・縁上回＝MCAP／Wernicke 野・Meyer 係蹄付近＝MCAT／中心前回の下肢領域（内側）＝ACA／紡錘状回・海馬傍回＝PCAT／鳥距溝・舌状回・楔部＝PCAO。
→ 各領域の `atlas_region` と `caution` の「このアトラスでは〜に塗られている」はすべてこの確認結果による。**1mm での再確認が済むまで、小構造の帰属は暫定**。

---

## 1. 文献一覧と照合結果（pubmed_verify.py）

| refkey | PMID | --expect-* 照合 exit | PMC 全文 | 主な用途 |
|---|---|---|---|---|
| liu2023 | 36739282 | 0 | あり（PMC9899211） | アトラス定義 |
| tatu2012 | 22377874 | 0 | なし | 皮質領域の個人差 |
| toyoda2012 | 22377877 | 0 | なし | ACA・Heubner |
| kumral2002aca | 12453077 | 0 | なし | ACA 左右差 |
| giroud1995 | 7673948 | 0 | なし（PMC486019 は抄録のみ・本文0件） | 脳梁梗塞 |
| weiller1990 | 2222240 | 0 | なし | 線条体内包梗塞 |
| melo1992 | 1565233 | 0 | なし | 純粋運動性脳卒中 |
| hupperts1994 | 7922468 | 0 | なし | 前脈絡叢動脈 |
| defreitas2000 | 10768626 | 0 | なし | 下肢を含まない麻痺 |
| gonzalez2012 | 22377875 | 0 | なし | 表在性 MCA |
| kreisler2000 | 10720284 | 0 | なし | 失語の解剖 |
| mort2003 | 12821519 | 0 | なし | 半側空間無視 |
| rusconi2010 | 19903731 | 0 | なし | Gerstmann |
| jacobson1997 | 9109741 | 0 | なし | 1/4盲 |
| cereda2002 | 12499489 | 0 | なし | 島限局梗塞 |
| pritchard1999 | 10495075 | 0 | なし | 島と味覚 |
| colivicchi2004 | 15272134 | 0 | なし | 右島と不整脈 |
| laowattana2006 | 16505298 | 0 | なし | 左島と心イベント |
| hacke1996 | 8929152 | 0 | なし | 悪性 MCA 梗塞 |
| cals2002 | 12140669 | 0 | なし | 表在性 PCA |
| cereda2012 | 22377879 | 0 | なし | PCA 総説 |
| szabo2009 | 19359650 | 0 | なし | 海馬梗塞 |
| erdem1993 | 8331410 | 0 | なし | 海馬の動脈 |
| barton2002 | 11781408 | 0 | なし | 相貌失認 |
| damasio1983 | 6685830 | 0 | なし | 純粋失読 |
| schmahmann2003 | 12933968 | 0 | なし | 視床の血管症候群 |
| kim2005 | 15824351 | 0 | なし | 中脳梗塞 |
| kumral2002pons | 12529787 | 0 | なし | 橋梗塞 |
| sacco1993 | 8503798 | 0 | なし | 延髄外側梗塞 |
| thapliyal2022 | 36993088 | 0 | あり（PMC10041230） | 延髄外側梗塞の古典的症候・側性 |
| kase1993 | 8418555 | 0 | なし | PICA vs SCA |
| amarenco1991 | 1992370 | 0 | なし | SCA 外側枝 |
| lee2006 | 17030749 | 0 | なし | 孤立性めまい |
| lee2009 | 19797177 | 0 | なし | AICA |
| mattle2011 | 22014435 | 0 | なし | 脳底動脈閉塞 |

exit 0 でなかったもの：**なし**（exit 1・2 ともゼロ）。

---

## 2. 領域別の主張と根拠

表記：「主張」は content.json の該当文の要旨。抜粋は抄録（全文があるものは全文）からの短い引用。

### ACA（前大脳動脈・皮質枝）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| ACA-1 | atlas_region（内側面前頭〜頭頂、下肢運動野・楔前部を含む、脳梁は MLS、膨大部は PCAO） | liu2023 | A2, A5 | A-coord |
| ACA-2 | 傍中心小葉を含む内側面を灌流 | toyoda2012 | "Predominant leg weakness is attributed to damage in the paracentral lobule" | |
| ACA-3 | 脳梁も ACA 系から灌流（脳梁症候群を伴いうる） | toyoda2012, kumral2002aca | "...the alien hand sign, can present as callosal disconnection signs" / "frontal dysfunctions and callosal syndromes can help to make a clinical differential diagnosis" | 間接的支持（ACA 梗塞で脳梁症候群が出る） |
| ACA-4 | 皮質領域の境界には個人差 | tatu2012 | "we present the variability of the cortical territories of the three main cerebral arteries and define the minimal and maximal cortical supply areas" | |
| ACA-5 | {contra}下肢に強い片麻痺（単麻痺も） | toyoda2012 | "contralateral hemiparesis or monoparesis, usually affecting the leg predominantly" | 側性：抄録明記 |
| ACA-6 | 意欲低下（両側で無動性無言） | toyoda2012, kumral2002aca | "Hypobulia, typically 'akinetic mutism', is also common" / "bilateral infarction ... presented with akinetic mutism" | |
| ACA-7 | 把握反射・他人の手徴候などの脳梁離断徴候 | toyoda2012 | "including the grasp reflex and the alien hand sign, can present as callosal disconnection signs" | |
| ACA-8 | 尿失禁 | toyoda2012 | "Transcortical aphasia and urinary incontinence are other frequent symptoms" | |
| ACA-9 | 左：無言・超皮質性運動失語 | kumral2002aca | "left-side infarction ... consisting of mutism, transcortical motor aphasia, and hemiparesis with lower limb predominance" | |
| ACA-10 | 右：急性錯乱状態・運動性半側無視 | kumral2002aca | "right side infarction ... accompanied by acute confusional state, motor hemineglect and hemiparesis" | |
| ACA-11 | 上肢・顔面の筋力低下は Heubner・内側線条体動脈の関与 | toyoda2012 | "weakness of the arm and face is associated with involvement of Heubner's artery and the medial striate arteries" | 「LLS 側に塗られる」は A-coord |
| ACA-12 | 前頭葉機能障害・脳梁症候群が MCA 梗塞との鑑別点 | kumral2002aca | "frontal dysfunctions and callosal syndromes can help to make a clinical differential diagnosis" | |
| ACA-13 | ACA 梗塞は少ない。日本では解離が多く、拍動性でない頭痛 | toyoda2012 | "account for 0.5-3% of all ischemic strokes" / "ACA dissection is a frequent cause in Japan" / "A non-throbbing headache is common at stroke onset in patients with ACA dissection" | 数値は本文に書いていない |
| ACA-14 | caution：ACA 群 29 例、境界の精度に限界 | liu2023 | A8 | |

### MLS（内側レンズ核線条体動脈・アトラス上は脳梁）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| MLS-1 | atlas_region（脳梁膝部〜体部、解剖学的知識で定義、膨大部は PCAO） | liu2023 | A4, A5 | A-coord |
| MLS-2 | 内側線条体動脈・Heubner は ACA 系の深部穿通枝で線条体・内包を灌流 | weiller1990, toyoda2012 | "the lesions corresponded to the territories of the medial and lateral group of the lenticulostriate arteries, Heubner's artery, or the anterior choroidal artery"（線条体内包梗塞） / 題名 "Anterior cerebral artery and Heubner's artery territory infarction" | 「ACA 系から出る」は Toyoda の題名・文脈からの読み取り |
| MLS-3 | 脳梁そのものは ACA 系から灌流 | toyoda2012, kumral2002aca | ACA-3 と同じ | 間接的支持 |
| MLS-4 | 左手の観念運動失行・左手の失書・構成障害（脳梁前部の病変で） | giroud1995 | "related to a single, large infarct or several infarctions in the anterior part of the corpus callosum. Clinical features were characterised by left ideomotor apraxia, construction apraxia, and left agraphia" | |
| MLS-5 | 他人の手徴候 | giroud1995 | "Alien hand was noted in only two cases." | |
| MLS-6 | 歩行障害（脳梁＋両側皮質下の多発ラクナ） | giroud1995 | "gait disorders in three cases with MRI features of multiple lacunes in a large part of the corpus callosum, and also the subcortical areas of both hemispheres" | |
| MLS-7 | 脳梁梗塞はまれではなく、離断症候群がそろうのは一部 | giroud1995 | "callosal infarctions are not rare" / "A callosal disconnection syndrome occurred in only five of eight patients" | |
| MLS-8 | Heubner・内側線条体動脈の梗塞は顔面・上肢の筋力低下（深部構造は LLS に塗られる） | toyoda2012 | ACA-11 | 後半は A-coord |
| MLS-9 | caution：名称と部位の不一致 | liu2023 | A4, A5 | A-coord |

### LLS（外側レンズ核線条体動脈）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| LLS-1 | atlas_region（被殻・淡蒼球・尾状核・内包・放線冠、確率マップで定義） | liu2023 | A3 | A-coord |
| LLS-2 | MCA 近位部（M1）から出る深部穿通枝 | liu2023, weiller1990 | "lateral lenticulostriate (within MCA)" / "embolization into the M1 segment ... lesions that acutely and simultaneously occluded the orifices of the lenticulostriate or neighboring arteries" | |
| LLS-3 | 内包後脚の後方2/3と後部脳室周囲放線冠は前脈絡叢動脈の領域 | hupperts1994 | "the posterior two-thirds of the posterior leg of the internal capsule was considered as certain AChA territory" / "the posterior paraventricular corona radiata region is most likely supplied by the AChA" | |
| LLS-4 | {contra}顔面・上下肢におよぶ片麻痺（純粋運動性脳卒中） | melo1992 | "patients with FUL distribution and hypertension had a 90% probability of deep infarct" | 数値は本文に書いていない。側性：基本解剖 |
| LLS-5 | 構音障害 | melo1992 | "Twenty-nine percent of the patients had dysarthria, which was of no localizing value." | |
| LLS-6 | 大きな線条体内包梗塞で失語・無視 | weiller1990 | "Eight of them had aphasia or neglect." | |
| LLS-7 | 左：非流暢性失語（被殻を含む病変） | kreisler2000 | "Nonfluent aphasia depended on the presence of frontal or putaminal lesions" | P3 |
| LLS-8 | 右：半側空間無視（大きな線条体内包梗塞） | weiller1990 | LLS-6 | 無視は右半球に多いという一般的事項で右に配置 |
| LLS-9 | FUL＋高血圧で深部梗塞の可能性が高い、単麻痺は深部梗塞でほぼ起こらない | melo1992 | LLS-4 / "Pure motor monoparesis was almost never caused by a deep infarct." | |
| LLS-10 | 深部梗塞は半数未満、塞栓源をもつ例も | melo1992 | "Less than one half of the patients had a deep infarct, and one third had a potential embolic source from the heart or large arteries" | |
| LLS-11 | 大きな線条体内包梗塞は M1 塞栓・狭窄、ラクナと機序が異なる、失語・無視例では皮質血流低下 | weiller1990 | "Large striatocapsular infarctions occur due to occlusive disease of the middle cerebral artery (large-vessel disease) and not due to ... small-vessel disease" / "Persistent occlusion of the middle cerebral arteries and a decrease of cortical regional cerebral blood flow were only found in patients with aphasia or neglect." | |
| LLS-12 | caution：LLS は前脈絡叢動脈・Heubner の深部構造も含む | hupperts1994, liu2023 | LLS-3 | A-coord |

### MCAF（MCA 前頭葉）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| MCAF-1 | atlas_region（Broca 野・手の領域・前頭眼野付近、脳回で区切る） | liu2023 | A2 | A-coord |
| MCAF-2 | MCA 表在枝は外側面の大部分を灌流、個人差あり | gonzalez2012, tatu2012 | "The superficial middle cerebral artery (MCA) territory includes the greater part of the lateral surface of the cerebral hemisphere." / "anatomical variations should be considered" | |
| MCAF-3 | {contra}顔面・上肢優位の片麻痺 | defreitas2000 | "the majority were caused by superficial infarcts. Almost half of the lesions were confined to superficial branches of the middle cerebral artery territory" | 側性：基本解剖 |
| MCAF-4 | 左：非流暢性失語 | kreisler2000 | LLS-7 | P3 |
| MCAF-5 | 前方（上方）枝が多い、塞栓が半数以上 | defreitas2000 | "276 (30.8%) in the anterior (superior) and 138 (15.4%) in the posterior (inferior)" / "More than half of the infarcts had a presumed embolic source from large-artery disease or from the heart." | |
| MCAF-6 | 失語型は病変部位と対応 | kreisler2000 | "Lesion location is the main determinant of aphasic disorders at the acute stage." | |
| MCAF-7 | caution：葉別区分は脳回ランドマークで分枝域と一致しない | liu2023 | A2 | |

### MCAP（MCA 頭頂葉）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| MCAP-1 | atlas_region（縁上回・角回を含む頭頂葉外側面） | liu2023 | A2 | A-coord |
| MCAP-2 | MCA 表在枝が灌流、境界に個人差 | gonzalez2012, tatu2012 | MCAF-2 | |
| MCAP-3 | {contra}半身の感覚障害 | gonzalez2012 | "insular syndrome and sensitive, motor or language disturbances" | 表在性 MCA 一般の記載。頭頂葉＝体性感覚野は基本解剖 |
| MCAP-4 | {contra}下1/4盲（頭頂葉、通常ほかの局在徴候を伴う） | jacobson1997 | "inferior quadrantanopia was occipital lobe (76%), parietal lobe (22%)..." / "Quadrantanopias caused by lesions of the parietal lobe usually are associated with other localizing signs." | |
| MCAP-5 | 左：Gerstmann 症候群（4徴） | rusconi2010 | "discriminating their own fingers, writing by hand, distinguishing left from right and performing calculations ... assigned it to a lesion of the dominant parietal lobe" | |
| MCAP-6 | 右：半側空間無視（角回） | mort2003 | "For patients with MCA territory strokes, the critical area involved in all neglect patients was the angular gyrus of the inferior parietal lobe (IPL)." | 対象は右半球病変 35 例 |
| MCAP-7 | 上側頭回説には異論 | mort2003 | "our findings challenge the recent influential proposal that lesions of this area are critically associated with neglect" | |
| MCAP-8 | Gerstmann の4徴を同一皮質で説明できるかは疑問、皮質下白質の離断説 | rusconi2010 | "it is very unlikely that damage to the same population of cortical neurons should account for all of the four symptoms" / "a pure form ... might arise from disconnection ... in the subcortical parietal white matter" | |
| MCAP-9 | 頭頂葉病変の1/4盲はほとんどがほかの局在徴候を伴う | jacobson1997 | MCAP-4 | |

### MCAT（MCA 側頭葉）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| MCAT-1 | atlas_region（Wernicke 野・Meyer 係蹄付近、扁桃体・鉤も含む） | liu2023 | A2 | A-coord |
| MCAT-2 | 鉤溝で前脈絡叢動脈と PCA の海馬枝が吻合 | erdem1993 | "The uncal sulcus was found to be an important anastomotic site between the hippocampal branches of the AChA and the hippocampal branches of the PCA." | |
| MCAT-3 | {contra}上1/4盲（Meyer 係蹄） | jacobson1997 | "superior quadrantanopias was occipital lobe (83%), parietal lobe (3%), and temporal lobe (13%)" | 側頭葉病変でも生じることの根拠 |
| MCAT-4 | 左：理解障害・錯語の目立つ失語 | kreisler2000 | "comprehension disorder on posterior lesions of the temporal gyri" / "verbal paraphasia on temporal or caudate lesions" | P3。「流暢性」の語は抄録になく、タグ名は「理解障害・錯語が目立つ失語（Wernicke型）」とした |
| MCAT-5 | 失語型はおおむね古典的解剖どおり | kreisler2000 | "Most clinical-radiologic correlations supported the classic anatomy of aphasia." | |
| MCAT-6 | 上1/4盲は後頭葉病変のほうが多い | jacobson1997 | MCAT-3 / "in the case of a superior quadrantanopia, the possibility of a temporal lobe lesion can not be excluded" | |
| MCAT-7 | caution：扁桃体・鉤が MCAT、即断しない | erdem1993, liu2023 | MCAT-2, A2 | A-coord |

### MCAO（MCA 後頭葉）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| MCAO-1 | atlas_region（後頭葉外側面、内側面は PCAO） | liu2023 | A2 | A-coord |
| MCAO-2 | MCA/PCA 皮質境界は個人差が大きい | tatu2012 | ACA-4 | |
| MCAO-3 | {contra}同名性視野障害（1/4盲も） | gonzalez2012, jacobson1997 | "disorientation, hemianopia or hemineglect"（表在性 MCA の症候） / 後頭葉病変が1/4盲の最多原因 | 側性：基本解剖 |
| MCAO-4 | 孤立した1/4盲は後頭葉が多い | jacobson1997 | "A patient with a neurologically isolated quadrantanopia is likely to have a lesion in the occipital lobe" | |
| MCAO-5 | MCA/PCA 境界は確率マップの比 | liu2023 | A9 | |
| MCAO-6 | caution：脳回ランドマーク区分、PCA 閉塞の可能性 | liu2023, tatu2012 | A2, ACA-4 | 推論（個人差からの帰結） |

### MCAI（MCA 島）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| MCAI-1 | atlas_region（島皮質、ランドマーク定義） | liu2023 | A2 | |
| MCAI-2 | 島は MCA 表在領域、急性期脳梗塞の連続例で島を含む梗塞は左右とも少なくない | gonzalez2012, colivicchi2004 | "insular syndrome"（表在性 MCA） / "Insular involvement was present in 33 patients with right-sided stroke (67.3%) and in 36 patients with left-sided stroke (66.6%)." | 数値は本文に書いていない |
| MCAI-3 | {contra}感覚障害（島後部で一過性の偽視床型） | cereda2002 | "somatosensory deficits in three patients with posterior insular stroke (two with a transient pseudothalamic sensory syndrome...)" | 側性：基本解剖 |
| MCAI-4 | めまい・ふらつき・転倒傾向（眼振なし） | cereda2002 | "vestibular-like syndrome, with dizziness, gait instability, and tendency to fall, but no nystagmus" | |
| MCAI-5 | 構音障害 | cereda2002 | "neuropsychological disorders, including aphasia (left posterior insula), dysarthria" | |
| MCAI-6 | 味覚障害は同側の舌に出たとの報告 | pritchard1999 | "Damage to the right insula produced ipsilateral taste recognition and intensity deficits." | |
| MCAI-7 | 右島：同側の認知・強度低下／左島：同側の強度低下＋両側の認知障害 | pritchard1999 | MCAI-6 / "Damage to the left insula caused an ipsilateral deficit in taste intensity but a bilateral deficit in taste recognition." | n=6 の小規模研究 |
| MCAI-8 | （味覚）左島後部梗塞での味覚障害例 | cereda2002 | "gustatory disorder in a patient with left posterior insular infarct" | |
| MCAI-9 | 心自律神経・不整脈：右島で HRV 低下と複雑な不整脈 | colivicchi2004 | "subjects with right-sided insular damage showed significantly lower values of the standard deviation of all normal-to-normal (SDNN)..." / "Right insular stroke was also associated with more complex arrhythmias" | |
| MCAI-10 | 左島梗塞で1年以内の心イベント増加 | laowattana2006 | "Left insular stroke is associated with an increased risk of adverse cardiac outcome" / "(cardiac death, myocardial infarction, angina, and heart failure) were assessed over 1 year" | |
| MCAI-11 | 左右差は一定しない | colivicchi2004, laowattana2006 | MCAI-9 と MCAI-10 が逆方向（Laowattana: "Right insular stroke was not associated with adverse cardiac outcomes"） | 2研究の対比による記述 |
| MCAI-12 | 左：失語・復唱障害（島・外包） | kreisler2000, cereda2002 | "repetition disorder on insula-external capsule lesions" / "aphasia (left posterior insula)" | |
| MCAI-13 | 右：一過性の身体パラフレニア、血圧上昇発作 | cereda2002 | "transient somatoparaphrenia (right posterior insula)" / "hypertensive episodes in a patient with a right posterior insular infarct" | |
| MCAI-14 | 島後部の限局梗塞で偽視床型感覚障害・前庭様症状が前景 | cereda2002 | "Strokes restricted to the posterior insula may present with pseudothalamic sensory and vestibular-like syndromes as prominent clinical manifestations" | |
| MCAI-15 | caution：左右差は小規模研究に基づく | pritchard1999, cereda2002 | Pritchard "6 patients with unilateral damage to the insula" / Cereda "four patients" | |

### PCAT（PCA 側頭葉）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| PCAT-1 | atlas_region（紡錘状回・海馬傍回、海馬体部は ACTP、扁桃体・鉤は MCAT） | liu2023 | A2 | A-coord |
| PCAT-2 | 海馬も PCA とその分枝（下側頭枝など）が主に灌流、前脈絡叢動脈の寄与は小さい | erdem1993 | "in 27%, all of the inferior temporal branches of the PCA predominantly supplied the hippocampus" / "the PCA directly and by its branches contributes much more to the blood supply of the hippocampal formation than the AChA" | 「側頭葉底面・内側面を PCA 皮質枝が灌流」は tatu2012 の地図による一般的記述 |
| PCAT-3 | 左：記憶障害（表在性 PCA 梗塞では左病変で多い） | cals2002 | "memory impairment in 20 (17.5 %; with left [L], right [R], or bilateral [B] lesions in 15, 2, or 3 patients, respectively)" | 数値は本文に書いていない。PCA 表在梗塞全体のデータで、PCAT 単独の局在データではない |
| PCAT-4 | 左：色名呼称障害（左後頭側頭葉内側） | damasio1983, cals2002 | "The lesion associated with color anomia was in the mesial occipitotemporal junction of the left hemisphere." / "color dysnomia in 6 (5 %; L: 6)" | |
| PCAT-5 | 右：相貌失認（右紡錘状回を含む後頭側頭葉内側、両側でも） | barton2002, cals2002 | "Prosopagnosia ... is associated with medial occipitotemporal lesions, especially on the right." / "prosopagnosia in 7 (6 %; R/B: 4/3)" | |
| PCAT-6 | 右：半側空間無視（海馬傍回） | mort2003 | "For PCA territory strokes, all patients with neglect had lesions involving the parahippocampal region" | |
| PCAT-7 | 神経心理症状は系統的に調べると高頻度 | cals2002 | "Neuropsychological deficits are frequent if systematically searched for." | |
| PCAT-8 | caution：海馬体部は ACTP | liu2023 | A6 | A-coord |

### PCAO（PCA 後頭葉）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| PCAO-1 | atlas_region（鳥距溝・舌状回・楔部、脳梁膨大部） | liu2023 | A2 | A-coord |
| PCAO-2 | PCA 皮質枝が後頭葉内側面を灌流 | cals2002, cereda2012 | "hemianopsia in 78 (67 %)"（表在性 PCA） / "After superficial PCA infarcts, visual field defects and somatosensory deficits are the most frequent signs." | |
| PCAO-3 | {contra}同名半盲（1/4盲も） | cals2002, jacobson1997 | "hemianopsia ..., quadrantanopsia in 26 (22 %)" / MCAO-4 | 側性：基本解剖 |
| PCAO-4 | 左：失書を伴わない失読（左後頭葉脳室周囲白質、右同名半盲を伴うことが多い） | damasio1983, cals2002 | "The crucial anatomic correlate of alexia was a lesion of the paraventricular white matter of the left occipital lobe" / "Right homonymous hemianopia failed to appear in three patients"（16例中） / "dyslexia without dysgraphia in 10 (8.5 %; L/B: 8/2)" | |
| PCAO-5 | 原因は塞栓（心原性が多い）、塞栓源不明も多い | cals2002 | "embolism in 64 (54.5 %) patients [cardiac in 51 (43.5 %)...]" / "identification of the emboli source is often not possible" | |
| PCAO-6 | 両側後頭葉で皮質盲、見えているように振る舞う | cereda2012 | "After bilateral PCA infarcts, amnesia, cortical blindness (the patient cannot see but pretend he can) may occur." | 「Anton症候群」の名称は抄録にないため本文で使っていない |
| PCAO-7 | アトラス作成では両側梗塞を除外 | liu2023 | A1 | |
| PCAO-8 | 孤立した1/4盲は後頭葉が多い | jacobson1997 | MCAO-4 | |
| PCAO-9 | caution：膨大部は PCAO | liu2023 | — | A-coord |
| PCAO-tag | 上・下1/4盲タグ | jacobson1997 | 後頭葉が上下とも最多の責任部位 | 鳥距溝の上下と視野の対応は本文に書いていない |

### PCTP（後脈絡叢・視床穿通）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| PCTP-1 | atlas_region（視床・外側膝状体付近・中脳、確率マップ） | liu2023 | A3 | A-coord |
| PCTP-2 | P1 傍正中穿通枝、P2 の視床膝状体動脈・後脈絡叢動脈 | cereda2012 | "Occlusion of paramedian perforating arteries arising from P1 causes rostral midbrain infarction with or without thalamic lesion." / "Two main arterial groups arise from P2: ... thalamogeniculate arteries ... posterior choroidal arteries" | 「主に」とした（結節視床動脈の起始は書いていない） |
| PCTP-3 | 視床の4動脈領域 | schmahmann2003 | "Tuberothalamic ... Paramedian ... Inferolateral ... Posterior choroidal" | |
| PCTP-4 | {contra}感覚障害・半身失調・片麻痺（下外側） | schmahmann2003, cereda2012 | "Inferolateral territory strokes produce contralateral hemisensory loss, hemiparesis and hemiataxia" / "thalamogeniculate arteries causes severe contralateral hypesthesia and ataxia" | 側性：抄録明記 |
| PCTP-5 | {contra}中枢性疼痛（右で多い） | schmahmann2003 | "and pain syndromes that are more common after right thalamic lesions" | 「遅発性」は抄録にないため書いていない |
| PCTP-6 | 傾眠・覚醒低下（傍正中、特に両側） | schmahmann2003, cereda2012 | "Paramedian infarcts cause decreased arousal, particularly if the lesion is bilateral" / "hypersomnolence" | |
| PCTP-7 | 記憶・学習障害（結節視床・傍正中） | schmahmann2003 | "Tuberothalamic territory strokes produce impairments of ... learning and memory" / "Paramedian infarcts cause ... impaired learning and memory" | |
| PCTP-8 | 垂直性眼球運動障害（視床中脳傍正中） | cereda2012 | "The classical clinical triad after thalamomesencephalic infarcts is hypersomnolence, cognitive deficits and vertical oculomotor paresis." | |
| PCTP-9 | {ipsi}動眼神経麻痺、核間性眼筋麻痺（中脳） | kim2005 | "third nerve palsy in 14 (35%)" / "internuclear ophthalmoplegia in five (13%)" | 側性：基本解剖（抄録は側性を明記せず） |
| PCTP-10 | 歩行失調・四肢失調・構音障害（中脳） | kim2005 | "gait ataxia in 27 (68%) patients, dysarthria in 22 (55%), limb ataxia in 20 (50%)" | 数値は本文に書いていない |
| PCTP-11 | {contra}扇形の同名性視野欠損（外側膝状体を含む後脈絡叢） | cereda2012 | "posterior choroidal arteries results in sectoranopia with involvement of the lateral geniculate body" | 側性：基本解剖 |
| PCTP-12 | ジストニア・振戦（後脈絡叢） | schmahmann2003 | "Posterior choroidal lesions result in visual field deficits, variable sensory loss, weakness, dystonia, tremors" | tag side=contra は基本解剖 |
| PCTP-13 | 左：失語（傍正中・結節視床） | schmahmann2003 | "Language deficits result from left paramedian lesions and from left tuberothalamic lesions" | |
| PCTP-14 | 右：半側空間無視などの視空間障害 | schmahmann2003 | "Right thalamic lesions in both these vascular territories produce visual-spatial deficits, including hemispatial neglect." | |
| PCTP-15 | 症候は動脈領域で異なり、覚醒・記憶・遂行機能・人格の変化が前景に | schmahmann2003 | "impairments of arousal and orientation, learning and memory, personality, and executive function" | |
| PCTP-16 | 中脳梗塞の症候頻度、前内側で眼球運動障害、原因は大血管・細小血管、心原性はまれ | kim2005 | "The anteromedial group ... was characterized by oculomotor disturbances (89%)" / "Large vessel disease and small vessel disease are usual pathogenic mechanisms, whereas cardiogenic embolism is rare." | |
| PCTP-17 | caution：視床全体＋中脳を一括、Level 2 は PCA | liu2023 | A3, A7 | A-coord |

### ACTP（前脈絡叢・視床穿通・アトラス上は海馬）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| ACTP-1 | atlas_region（海馬体部中心、解剖学的知識で定義、Level 2 は PCA） | liu2023 | A4, A6 | A-coord |
| ACTP-2 | 前脈絡叢動脈は内包後脚後方2/3・後部脳室周囲放線冠を灌流 | hupperts1994 | LLS-3 | |
| ACTP-3 | 海馬は PCA 系の寄与が大きく、鉤溝で吻合 | erdem1993 | PCAT-2, MCAT-2 | |
| ACTP-4 | 記憶障害（神経心理検査で明らかになることがある） | szabo2009 | "mnestic deficits were prominent in only 11/57 patients, neuropsychological examination in 20 patients showed deficits" | |
| ACTP-5 | 左：言語性、右：非言語性エピソード記憶 | szabo2009 | "deficits of verbal episodic long-term memory in left and of nonverbal episodic long-term memory in right HI" | |
| ACTP-6 | 海馬梗塞は全例で後方循環のほかの病変を伴う、症候は海馬外の病変が前景 | szabo2009 | "In all cases DWI showed further ischemic lesions in the posterior circulation." / "Symptoms from lesions outside the hippocampus were the common leading clinical signs." / "usually occur as part of multifocal PCA ischemia" | |
| ACTP-7 | 前脈絡叢動脈梗塞は他の小深部梗塞と差がなく独立病型でない、大きな梗塞は少ない | hupperts1994 | "The frequency of a clinical lacunar or a cortical syndrome did not differ between small deep AChA and remaining small deep infarcts." / "Larger AChA infarcts were infrequent in our series" / "AChA infarcts do not constitute a separate brain infarct entity" | 抄録は400語で途中切れ（TRUNCATED） |
| ACTP-8 | caution：名称と部位の不一致、内包後脚は LLS、外側膝状体付近は PCTP | hupperts1994, erdem1993, liu2023 | ACTP-2, ACTP-3, A6 | A-coord |

### B（脳底動脈領域：橋・延髄）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| B-1 | atlas_region（橋・延髄、延髄外側も B、確率マップ） | liu2023 | A3 | A-coord |
| B-2 | 橋は脳底動脈からの穿通枝群が一定の領域を灌流 | kumral2002pons | "five main clinical patterns that depended on the constant territories of intrinsic pontine arteries" / "basilar artery branch disease (BABD)" | |
| B-3 | 延髄外側は椎骨動脈・PICA | thapliyal2022 | 抄録 "Thrombosis, embolization, or dissection of vertebral or posterior inferior cerebellar artery (PICA) often results into LMS." | |
| B-4 | {contra}片麻痺（前内側、構音障害・失調を伴いうる） | kumral2002pons | "anteromedial pontine syndrome (58%) presented with motor deficit with dysarthria, ataxia" | 側性：基本解剖 |
| B-5 | {contra}半身の感覚障害（前外側・被蓋） | kumral2002pons | "anterolateral pontine syndrome ... developed with motor and sensory deficits" / "tegmental pontine syndrome ... associated with sensory syndromes" | 側性：基本解剖 |
| B-6 | 眼球運動障害・めまい・失調（被蓋） | kumral2002pons | "eye movement disorders and vestibular system symptoms including vertigo, dizziness and ataxia" | |
| B-7 | 両側橋梗塞：意識消失・四肢麻痺・急性仮性球麻痺 | kumral2002pons | "bilateral pontine syndrome (11%) consisted with transient consciousness loss, tetraparesis and acute pseudobulbar palsy" | |
| B-8 | Wallenberg：{ipsi}顔面＋{contra}体幹・四肢の温痛覚障害、{ipsi}Horner、{ipsi}失調、めまい・眼振、嚥下障害・嗄声 | thapliyal2022, sacco1993 | 全文 "loss of pain and temperature sensation on ipsilateral face and contralateral side of rest of the body" / 全文 "ascending sympathetic fibres is associated with development of ipsilateral Horner's syndrome" / 抄録 "ipsilateral ataxia, vertigo, nystagmus, dysphagia, hoarseness, hiccups and Horner's syndrome" / Sacco "Horner's syndrome was found in 91%, ipsilateral ataxia in 85%, and contralateral hypalgesia in 85%" | 側性：Thapliyal 全文で明記 |
| B-9 | {ipsi}難聴を伴うめまい（AICA） | lee2009 | "the most common pattern of audiovestibular dysfunction was the combined loss of auditory and vestibular function" | 側性：基本解剖（内耳は同側の AICA 系）。抄録に側性の明記なし |
| B-10 | 孤立性橋梗塞の原因は BAD 最多、次いで細小血管病、両側以外は予後良好 | kumral2002pons | "The main etiology of stroke was basilar artery branch disease (BABD) ... followed by small-artery disease" / "outcome is in general excellent except in those with bilateral pontine lesions" | |
| B-11 | 伝統的に PICA 症候群、最多原因は椎骨動脈病変 | thapliyal2022, sacco1993 | 全文 "Though traditionally LMS is commonly known as PICA syndrome, the commonest cause of LMS is atherothrombotic occlusion of the vertebral artery." / Sacco "Vertebral artery disease was confirmed ... in 73% of patients." | |
| B-12 | 小脳梗塞を伴うことは少ない | sacco1993 | "Cerebellar infarcts only infrequently accompany lateral medullary syndrome, suggesting that most of the posterior inferior cerebellar artery territory is spared" | アトラス上 B に入ることと整合 |
| B-13 | 3徴（Horner・同側失調・対側温痛覚低下）が手がかり | sacco1993 | "The triad of Horner's syndrome, ipsilateral ataxia, and contralateral hypalgesia will clinically identify patients with lateral medullary infarction." | 「必発」とは書いていない |
| B-14 | 橋被蓋最背側・最外側の梗塞は孤立例で見られず小脳梗塞に伴う | kumral2002pons | "there was no infarct in the extreme dorsal and lateral tegmental pontine territories which have been mostly associated with cerebellar infarctions" | |
| B-15 | caution：延髄外側は B、AICA は独立定義なし | liu2023 | A3, A7 | A-coord |

### SC（上小脳）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| SC-1 | atlas_region（小脳上部、虫部上部を含む、確率マップ） | liu2023 | A3 | A-coord |
| SC-2 | SCA は小脳上部、外側枝は吻側前部 | amarenco1991, kase1993 | "the anterior part of the rostral cerebellum, ie, the territory of the lateral branch of the superior cerebellar artery" / "superior cerebellar artery distribution" | |
| SC-3 | {ipsi}四肢の測定障害、構音障害、ふらつき、体軸の側方突進 | amarenco1991 | "The main clinical features were ipsilateral dysmetria and axial lateropulsion, dysarthria, and unsteadiness." | 側性：抄録明記 |
| SC-4 | 発症時に歩行障害、めまい・頭痛は PICA より少ない、経過良好、浮腫・水頭症は少ない | kase1993 | "In 30 patients with superior cerebellar artery infarcts, gait disturbance predominated at onset; vertigo and headache were significantly less common. The clinical course was usually benign." / "marked cerebellar mass effect, hydrocephalus, and brain stem compression in only two instances (7%)" | |
| SC-5 | 小脳吻側前部の梗塞はラクナ様（構音障害・手の不器用）、心原性塞栓が多い | amarenco1991 | "the clinical presentation mimicked a lacunar stroke (dysarthria and clumsy hand syndrome)" / "Six patients had a cardiac source of emboli." | 9例中6例 |
| SC-6 | 孤立性めまいの小脳梗塞に SCA 領域は含まれず | lee2006 | "None of patients with infarcts in the territory of the superior cerebellar artery or multiple cerebellar arteries showed isolated spontaneous prolonged vertigo." | |
| SC-7 | caution：SC/IC と SCA/AICA/PICA は一対一でない | liu2023 | A3 | 推論（確率マップ定義からの帰結） |

### IC（下小脳）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| IC-1 | atlas_region（小脳下部、延髄外側は B） | liu2023 | A3 | A-coord |
| IC-2 | 小脳下部は主に PICA、内側枝の領域あり、AICA は独立定義なし | kase1993, lee2006, liu2023 | "posterior inferior cerebellar artery territory infarcts" / "the medial branch of the posterior inferior cerebellar artery territory" / A7 | |
| IC-3 | めまい・頭痛・歩行時のふらつき（PICA 発症時） | kase1993 | "a triad of vertigo, headache, and gait imbalance predominated at stroke onset" | |
| IC-4 | めまいとふらつきだけの発症（前庭神経炎類似、PICA 内側枝） | lee2006 | "isolated spontaneous prolonged vertigo with imbalance as a sole manifestation of cerebellar infarction" / "most commonly involved was the medial branch of the posterior inferior cerebellar artery territory" | |
| IC-5 | {ipsi}難聴を伴うめまい（AICA） | lee2009 | B-9 | 側性：基本解剖 |
| IC-6 | 前庭神経炎類似の小脳梗塞は従来考えより多い | lee2006 | "Cerebellar infarction simulating vestibular neuritis is more common than previously thought." | |
| IC-7 | PICA で浮腫・水頭症・脳幹圧迫、死亡例、経過観察 | kase1993 | "postinfarct swelling led to brain stem compression that resulted in four deaths" / "These differences should help in the selection of appropriate monitoring and treatment strategies." | |
| IC-8 | AICA では聴覚と前庭の両方が障害されやすい | lee2009 | "Unlike a viral cause, labyrinthine dysfunction of a vascular cause usually leads to combined loss of both auditory and vestibular functions." | |
| IC-9 | caution：延髄外側は B、IC≠PICA 全域 | sacco1993, liu2023 | B-12, A3 | A-coord |

### LV（側脳室）

| # | 主張 | refkey | 根拠抜粋 | 注記 |
|---|---|---|---|---|
| LV-1 | 動脈領域ではなく解剖の目印 | liu2023 | A11 | |
| LV-2 | 周囲の深部構造と LLS・PCTP が接する | — | A-coord | アトラス上の位置関係の記述 |
| LV-3 | 高齢者で脳室拡大、位置合わせで脳室周囲の病変位置がずれうる | liu2023 | A10 / "High γ OSLV is common in this population since aged subjects' lateral ventricles are usually larger than the template's" | |

### Level 2

| # | 主張 | refkey | 根拠 |
|---|---|---|---|
| L2-ACA | 概要・症候・左右差・両側 ACA で無動性無言＋括約筋障害・予後不良 | toyoda2012, kumral2002aca, giroud1995, liu2023 | ACA-5〜13、Kumral "bilateral infarction ... presented with akinetic mutism, severe sphincter dysfunction, and dependent functional outcome" |
| L2-MCA | 表在枝で外側面の大部分、深部穿通枝で線条体・内包、M1 閉塞で両方 | gonzalez2012, weiller1990, liu2023 | MCAF-2, LLS-2, LLS-11 |
| L2-MCA | 悪性 MCA 梗塞：内頸動脈遠位部/MCA 主幹閉塞、数日にかけ占拠性浮腫、テント切痕ヘルニア、予後不良 | hacke1996 | "caused by occlusion of either the distal intracranial carotid artery or the proximal middle cerebral artery trunk" / "A space-occupying mass effect develops rapidly and predictably over the initial 5 days" / "The cause of death was transtentorial herniation" / "The prognosis of complete middle cerebral artery territory stroke is very poor" |
| L2-MCA | 症候（顔面上肢優位麻痺・感覚・視野・失語・無視） | defreitas2000, gonzalez2012, kreisler2000, mort2003 | MCAF-3, MCAP-3, MCAO-3, MCAF-4/MCAT-4/MCAI-12, MCAP-6 |
| L2-PCA | 深部枝（P1・P2）と表在枝（P3・P4） | cereda2012 | "The PCA can be divided into 'deep' (P1 and P2 segments) and 'superficial' (P3 and P4) segments." |
| L2-PCA | 症候：視野・感覚・記憶・傾眠/垂直眼球運動障害、左：失読・失語・色名呼称、右：視覚性無視・場所の失見当・相貌失認 | cereda2012, cals2002, damasio1983 | PCAO-2/3, PCTP-8, PCAT-3〜5, Cereda "disorders of reading may be seen after unilateral left infarction and disorientation for place and visual neglect after right lesion", Cals "dysphasia in 17 (14.5 %; L/B: 14/3)", "visual neglect in 11 (9.5 %; L/R: 2/9)" |
| L2-PCA | 急性期血栓溶解は前方循環と同様に有用、死亡率は低いが長期障害は過小評価 | cereda2012 | "Acute thrombolysis is as useful after PCA infarctions as after anterior circulation strokes. Mortality after PCA strokes is low, but long-term behavioral and cognitive deficits are underestimated." |
| L2-VB | 脳底動脈閉塞の臨床像と前駆症状、確認・除外を急ぐ、早期確認で血栓溶解・血管内治療 | mattle2011 | "ranges from mild transient symptoms to devastating strokes" / "non-specific prodromal symptoms such as vertigo or headaches ... followed by the hallmarks of BAO, including decreased consciousness, quadriparesis, pupillary and oculomotor abnormalities, dysarthria, and dysphagia" / "BAO has to be confirmed or ruled out as a matter of urgency" / "intravenous thrombolysis or endovascular treatment can be undertaken" |
| L2-VB | 症候（めまい・構音/嚥下・眼球運動・{ipsi}四肢失調・意識障害/四肢麻痺・頭痛） | mattle2011, kumral2002pons, sacco1993, amarenco1991, kase1993 | B-6〜8, SC-3, IC-3 |
| L2-VB | 孤立性めまいの小脳梗塞（PICA 内側枝）、PICA の浮腫 | lee2006, kase1993 | IC-4, IC-7 |
| L2-VB/PCA | 中脳・視床は PCA に分類 | liu2023 | A3, A7 |
| L2-LV | 動脈領域でない、脳室拡大と位置合わせ | liu2023 | A10, A11 |

---

## 3. 書かなかった主張・`[要出典]`（content.json に入れていない）

| # | 主張 | 扱い | 理由 |
|---|---|---|---|
| X1 | MLS＝Heubner 反回動脈・尾状核頭の症候（従来版） | 削除 | アトラス上 MLS は脳梁（A5）。Heubner の深部構造は LLS 側。尾状核頭という具体的部位を支える抄録も今回の文献セットにない |
| X2 | ACTP＝内包後脚・外側膝状体、前脈絡叢動脈症候群の3徴「が揃うのが決定打」（従来版） | 削除 | アトラス上 ACTP は海馬（A6）。Hupperts 1994 は大きな AChA 梗塞は少なく独立病型でないと報告。3徴（片麻痺・感覚障害・半盲）の内容自体も今回の抄録には書かれていないため本文で3徴を列挙していない `[要出典]` |
| X3 | SCA 梗塞の「温痛覚障害（外側毛帯）」（従来版） | 削除 | 解剖学的誤り（外側毛帯は聴覚路）。SCA 領域の感覚症状を支える抄録も今回のセットにない |
| X4 | Wallenberg 症候群の症状が「必発」（従来版） | 削除 | Sacco 1993 でも各症候は一部の例にのみ見られる。「3徴が臨床的な手がかり」とだけ書いた |
| X5 | 右島皮質で「左味覚障害」（従来版） | 削除・訂正 | Pritchard 1999 では右島病変は同側（右）の味覚障害 |
| X6 | 右島皮質と不整脈を右側特有とする記述（従来版） | 訂正 | 左島の報告（Laowattana 2006）もあり、左右差は一定しないと書いた |
| X7 | MCA 後頭枝の「黄斑回避傾向」（従来版） | `[要出典]`・削除 | 根拠文献を確認できず |
| X8 | 共同偏視（前頭眼野・頭頂葉病変） | 不採用 | 候補 Tijssen 1991（PMID 2046929）は検索で実在を見たが、文献数を30本前後に絞るため採用せず、`--expect-*` 照合もしていない。採用する場合は再照合のうえ「右半球病変で多く、前頭眼野が直接障害されない例も多い」と書くのが抄録に沿う |
| X9 | 病態失認（右島後部） | 不採用 | 候補 Karnath 2005（PMID 16079395）。文献数の都合で不採用。右島は「一過性の身体パラフレニア」（Cereda 2002）のみ記載 |
| X10 | 観念運動失行（左頭頂葉） | 不採用 | 候補 Manuel 2013（PMID 22989580）は左下前頭と側頭頭頂の両方を示し、頭頂葉に限定できない。脳梁性の左手失行（Giroud 1995）のみ記載 |
| X11 | 中心前回 hand knob 梗塞が末梢神経麻痺に似る | 不採用 | 候補 Rissardo 2024（PMID 38399606）。文献数の都合で不採用 |
| X12 | 視床痛が「遅発性」に出る | 書かない `[要出典]` | Schmahmann 2003 抄録に発症時期の記載なし |
| X13 | 結節視床動脈が後交通動脈から出る | 書かない `[要出典]` | 今回の抄録に起始の記載なし（PCTP の classic_supply は「主に PCA 近位部」とした） |
| X14 | 前脈絡叢動脈が内頸動脈から出る、視索・大脳脚を灌流 | 書かない | 候補 Pezzella 2012（PMID 22377878）に記載があるが不採用 |
| X15 | 脳梁が「脳梁周囲動脈・後脳梁周囲動脈」から灌流、前交通動脈由来の枝 | 書かない | 候補 Türe 1996（PMID 8938760・exit 0 を一度確認）は文献数の都合で不採用。「ACA 系から灌流を受ける」と間接的に書くにとどめた |
| X16 | 脳梁膨大部を PCA の膨大部枝が灌流 | 書かない | Erdem 1993 の "splenial artery" は海馬尾部への分布の記載で、膨大部そのものの灌流は書かれていない |
| X17 | 島皮質の M2 島部枝 | 書かない | 抄録に記載なし |
| X18 | 鳥距溝の上下（舌状回・楔部）と上・下1/4盲の対応 | 書かない | 今回の抄録に記載なし。タグは Jacobson 1997（後頭葉が上下とも最多）で付与 |
| X19 | 中脳の Weber 型（動眼神経麻痺＋対側片麻痺） | 書かない | 候補 Kumral 2002 Stroke（PMID 12215591）に "nuclear or fascicular third-nerve palsy and contralateral motor deficits" とあるが不採用 |
| X20 | HINTS（頭位眼振・skew）による末梢/中枢の鑑別 | 書かない | 候補 Kattah 2009（PMID 19762709）。文献数の都合で不採用 |
| X21 | 「Anton 症候群」という名称 | 書かない | Cereda 2012 抄録は症状記述のみで名称なし |
| X22 | 中心後回病変の皮質性感覚障害（口周囲・手指に限局）、島・弁蓋部病変と中枢性疼痛 | 書かない | 候補 Kim JS 2007（PMID 17224568）。文献数の都合で不採用。島の感覚障害は Cereda 2002 の範囲（偽視床型）で記載 |
| X23 | Gerstmann の単一症候群としての確実性 | 限定付きで記載 | Rusconi 2010 のとおり「疑問視」と併記 |

---

## 4. アトラス定義と教科書の食い違い（content.json の caution に反映した箇所）

1. **MLS**：名称は内側レンズ核線条体動脈だが、塗られているのは脳梁の膝部〜体部（解剖学的知識で定義）。Heubner 反回動脈・内側線条体動脈の深部構造は LLS 側。
2. **ACTP**：名称は前脈絡叢・視床穿通だが、塗られているのは海馬（体部）中心の内側側頭葉（解剖学的知識で定義）。前脈絡叢動脈梗塞の主病変（内包後脚）は LLS、外側膝状体付近は PCTP。海馬の主な灌流は PCA 系（Erdem 1993）。Level 2 では PCA。
3. **B**：延髄外側（Wallenberg）が B に塗られている（臨床的には椎骨動脈/PICA）。B は脳底動脈本幹の閉塞だけを意味しない。
4. **IC**：小脳下部のみ。PICA の全灌流域（延髄外側を含む）とは一致しない。
5. **AICA**：独立した領域なし。病変は B と IC にまたがりうる。
6. **SC/IC**：確率マップ上の上下区分で、SCA/AICA/PICA の灌流域と一対一ではない。
7. **PCAT と海馬**：海馬体部は PCAT ではなく ACTP。扁桃体・鉤は MCAT。
8. **MCAT**：扁桃体・鉤（前脈絡叢動脈と PCA の枝が吻合する部位）が MCA 側に入る。
9. **LLS**：尾状核・内包前脚〜後脚・放線冠を一括。前脈絡叢動脈の内包後脚後部や Heubner の深部構造も含む。
10. **PCTP**：視床の4動脈領域を区別せず、中脳も含む（中脳は Level 2 で PCA、VB ではない）。
11. **PCAO**：脳梁膨大部を含む。
12. **MCA の葉別区分（F/P/T/O/I）**：脳回ランドマークによる区分で、MCA 分枝（上枝・下枝）の支配域ではない。MCAO は後頭葉外側面で、MCA/PCA 境界は個人差が大きい。
13. **ACA**：原著 ACA 群は 29 例と少なく、境界の精度に限界（著者記載）。
14. **アトラス全体**：心原性塞栓・両側・境界領域のみ・多発の梗塞は作成時に除外されている。

## 5. 独立監査（2026-10-08・別会話の medical-claim-evidence-auditor）と修正

初回監査の判定は **fail（ブロック10件・助言18件）**。書誌35本は PubMed と一致し、台帳の抜粋192件はすべて原文に実在した。問題は「言い換えが抜粋の範囲を超えている」箇所だった。以下のとおり content.json を直した（修正前の版は作業用に控えてある）。

| # | 箇所 | 修正 | 根拠 |
|---|---|---|---|
| B1 | ACA.atlas_region | 楔前部は「前上部」がACA、「後下部」はPCAO。脳梁膨大部は「主に」PCAO | 36739282 "Pre Cuneus is partially in the PCA territory"／2mm データ：膨大部の箱で PCAO 91・ACA 9 |
| B2 | ACA・L2 ACA.symptoms_common | 把握反射を離断徴候から分け「把握反射などの行動異常や、他人の手徴候などの脳梁離断徴候」 | 確立した神経学（把握反射は前頭葉内側の徴候） |
| B3 | MLS.classic_supply | 脳梁全体ではなく「膝部〜体部は主にACA系」。穿通枝の記述は起始を書かずに弱めた | 監査指摘（膨大部は主にPCA系・ツール内でも PCAO） |
| B4 | MLS.clinical_points[0] | 「離断症候群を呈さない例もある。離断症状は脳梁前部の単一の大きな梗塞または多発梗塞の例でみられた」 | 7673948 "occurred in only five of eight patients, related to a single, large infarct or several infarctions in the anterior part" |
| B5 | MCAF.clinical_points[0]・L2 MCA[1] | 「多くは表在性の梗塞」「半数近くはMCA表在枝に限局」「前方枝が後方枝より多い」 | 10768626 "the majority were caused by superficial infarcts. Almost half … confined to superficial branches … 30.8% … anterior … 15.4% … posterior" |
| B6 | MCAI.symptoms_common[4] | 右島＝心拍変動低下・複雑な不整脈、左島＝1年以内の心イベント増加、と評価項目を分けて記載 | 15272134・16505298 |
| B7 | PCAO.clinical_points[1] | 「皮質盲を来すことがあり、…振る舞う例もある」 | 22377879 "may occur" |
| B8 | L2 PCA.clinical_points[1] | 括弧書きを皮質盲の定義に読めない形へ | 22377879 |
| B9 | B.tags | `limb_ataxia` の `contra`（橋前内側＝失調性片麻痺）を追加。`ipsi`（延髄外側）は残す | 12529787 "motor deficit with dysarthria, ataxia" |
| B10 | references | 単著3本の「et al.」を削除（Toyoda K・Jacobson DM・Schmahmann JD） | PubMed esummary の著者数 |
| 助言 | 2名著者5本 | Giroud M, Dumas R／González Delgado M, Bogousslavsky J／Cereda C, Carrera E／Damasio AR, Damasio H／Kim JS, Kim J | PubMed esummary |
| 助言 | MCAF/MCAP/MCAT.caution | 「MCA分枝の支配域とは一致しない」→「支配域に基づく区分ではない」 | 原著の記載範囲 |
| 助言 | LLS.clinical_points[0][2]・L2 MCA[2] | 原文の条件の向きにそろえた（単麻痺の原因が深部梗塞であることはほとんどない／MCA閉塞の持続と皮質血流低下は失語・無視例にだけ） | 10768626・2222240 |
| 助言 | B.symptoms_common[3]・clinical_points[0] | 「一過性の意識消失」、BAD→BABD（basilar artery branch disease）と定義を添えた | 12529787 |
| 助言 | SC.clinical_points[1] | 「心臓に塞栓源をもつ例が多かった」 | 1992370 "Six patients had a cardiac source of emboli"（9例中）, "frequently, a cardiac source of emboli" |
| 助言 | ACTP.caution | 「名称が示す動脈の主な灌流域（内包後脚など）と一致しない」 | 8331410（前脈絡叢動脈も海馬に枝を出す） |
| 助言 | MCAO.clinical_points | 1/4盲の後頭葉の記述を削除（PCAO 側に残す） | 9109741 は鳥距溝周囲＝PCAO 側 |
| 助言 | LV.atlas_region | 「動脈領域ではないが、ラベルとして含まれている」 | 36739282 "30 arterial territories and ventricles" |
| 助言 | pritchard1999 | DOI 10.1037/0735-7044.113.4.663 を追記 | 監査で Crossref 一致を確認 |
| 助言 | tags.crossed_sensory | ラベルに「側は顔面で選ぶ」を追記（逆引きUIの前提） | — |
| 2mm指摘 | ACTP.caution・LLS.atlas_region/caution | 内包後脚の後部は「主にLLS、一部はPCTP」に弱めた | 2mm データ：後脚後部の白質（T1>150）で LLS 135・PCTP 40 |

### 追加した主張（再監査の対象）

| 主張 | refkey | 抜粋 | 照合 |
|---|---|---|---|
| IC.symptoms_common「めまいなどの偽迷路性症候に、{ipsi}四肢の測定障害・失調を伴うことがあり、体軸の側方突進が目立つ（延髄が保たれたPICA内側枝領域の梗塞で）」／IC.tags `limb_ataxia` ipsi | amarenco1990（PMID 2246654） | "pseudolabyrinthine signs with or without dysmetria and ataxia when the medulla was spared; marked axial lateropulsion was present in most cases" | pubmed_verify.py exit 0（著者・年・誌名一致）。PMC1014248 は抄録のみ（pubmed_fulltext.py exit 2）。側性は抄録に記載がなく、小脳性の測定障害は同側という基本解剖による |

### 見送った助言
- IC の四肢失調は上記で対応。PCTP の失調の側（中脳では同側・両側もありうる）は tags の注記で足りるため見送り。
- Thapliyal 2022 の全文にある交感神経路の誤り（上行性）は本文に持ち込んでいない。B-8 の根拠は同文献の「Horner は同側」という結論部分のみ。差し替えは今後の課題。
- Mattle 2011 は治療の可能性の記述のみに使っており、現行の知見と矛盾しないため据え置き。
- 監査の「照合できなかった主張」のうち、2mm データでの小構造の帰属は 1mm データ入手後に再確認する。

### 再監査（1回目）への対応
再監査の判定は **fail（ブロック1件・助言6件）**。前回のブロック10件はすべて解消と判定された。

| 区分 | 箇所 | 修正 | 根拠 |
|---|---|---|---|
| ブロック | MCAI.tags `cardiac_autonomic` | side を any → right_hemi（本文の右島＝心拍変動低下・不整脈に合わせた。左島の研究は心イベントで自律神経・不整脈ではない） | 15272134・16505298 |
| 助言1 | IC.symptoms_common[2] | 「多くの例で体軸の側方突進が目立った」 | 2246654 "marked axial lateropulsion was present in most cases" |
| 助言2 | MLS.atlas_region・PCAO.caution | 脳梁膨大部を「主に」PCAO にそろえた | 2mm：膨大部の箱で PCAO 91・ACA 9 |
| 助言3 | PCTP.atlas_region | 「内包後脚の後部の一部もここに塗られている」を追加（LLS・ACTP と対） | 2mm：後脚後部の白質で LLS 135・PCTP 40 |
| 助言4 | PCTP.symptoms_common[6] | 「失調は両側に出ることもある」を追加（前回の見送り理由「tags の注記で足りる」は tags に注記欄がなく不成立のため撤回） | 15824351 "ataxia (89%, bilateral in 17%)" |
| 助言5 | 台帳 B-8 | Thapliyal 全文の "ascending sympathetic fibres" の一文は解剖の誤り（延髄外側で障害されるのは下行性の交感神経路）を含む。Horner の側性の根拠は同文献の結論と Sacco 1993 "Horner's syndrome was found in 91%" とし、この一文は根拠に使わない | 監査指摘 |
| 助言6 | 前回の助言18（VB 下位区分の表記揺れ） | 見送り。原著のラベル名（SC/IC）に統一して表示しており、本文の "anterior and posterior cerebellar" の言い換えに触れなくても誤読は生じにくいため | — |

### 再監査（2回目）
判定 **pass（ブロック0件・助言1件）**。助言（IC.symptoms_common[2] の限定句を文頭へ）は監査の示した文をそのまま採用した：「延髄が保たれたPICA内側枝領域の梗塞では、めまいなどの偽迷路性症候に{ipsi}四肢の測定障害・失調を伴うことがあり、多くの例で体軸の側方突進が目立った。」（語の並べ替えのみで、主張の範囲は監査済みの文と同じ）。
残る確認事項：2mm データに基づく小構造の帰属（内包後脚後部・扁桃体/鉤・脳梁膨大部）は 1mm データで再確認する。

## 6. 1mm 原データでの再確認（2026-10-08・NITRC Atlas_MNI152.zip / Atlas_182_MNI152）

2mm の旧データは 1mm 原データを 2 ボクセルおきに取ったものと完全に一致した（一致率 1.0000）。代表部位を 1mm で数え直した結果（MNI 座標の箱内のラベル数。座標は概算）:

| 部位 | 1mm での内訳 | content.json の扱い |
|---|---|---|
| 内包後脚（白質 T1>150、x=−20〜−30, z=+2〜+14） | y≈−12: LLS 832・PCTP 26／y≈−18: LLS 612・PCTP 246／y≈−24: LLS 434・PCTP 411 | 前〜中部は LLS、後部は LLS と PCTP にまたがる → LLS.caution の「後部の多く」を「後部の一部」に修正（他の記述は据え置き） |
| 扁桃体（−22,−4,−18）±4 | MCAT 720 | 「扁桃体・鉤は MCAT」を確認 |
| 鉤（−24,−6,−28）±2 | MCAT 125 | 同上 |
| 海馬頭（−26,−14,−18）±2／体部（−30,−26,−10）±2 | ACTP 92・MCAT 33／ACTP 125 | 「海馬は ACTP」を確認 |
| 脳梁膝部・体部 | MLS（膝 337/343、体部は LV を除き MLS） | 確認 |
| 脳梁膨大部（0,−38,+12）±4 | PCAO 708・ACA 21 | 「主に PCAO」を確認 |
| 楔前部 前上部（−6,−60,+44）／後下部（−8,−70,+36） | ACA 729／PCAO 729 | 確認 |
| 外側膝状体付近（−22,−26,−6）±2 | PCTP 71・ACTP 54 | 「PCTP に塗られている」は言い切りすぎ → ACTP.caution と PCTP.atlas_region を「PCTP と ACTP の境界にあたる」に修正 |
| 延髄外側（−8,−42,−48）±2 | B 101・IC 24 | 「延髄外側は B」を確認 |

確率マップと境界領域: 原著 Methods "Images of patients with strokes in the right hemisphere were flipped along the x-axis so that all the stroke masks were considered in the left hemisphere" のとおり、原データの ProbArterialAtlas_average・BorderZone_ProbAve は左半球にしか値がない（右半球に値があるのは正中を越えた病変のわずかな分）。ツールでは右半球を左半球の値の左右反転で表示し、画面に注記した。境界領域は原著の BorderZone_ProbAve（MCA/ACA・MCA/PCA の確率比）をそのまま使う（「確率>0 が2血管」で定義し直すと脳の約1割になり、原著のファイルより広すぎるため）。

### 1mm 再確認の監査（2026-10-08）
判定 **pass（ブロック0件・助言2件）**。監査役は 1mm 原データを自分で読み直し、旧2mm＝1mm の2ボクセルおき（一致率1.000000）、現在の埋め込みデータ＝原データ（全ボクセル一致）も確かめた。
- 助言1（採用）：外側膝状体付近は左右とも過半が PCTP（左 PCTP 71・ACTP 54、右 PCTP 120・ACTP 5）。監査の示した文言どおり ACTP.caution・PCTP.atlas_region を「主にPCTPで、ACTPとの境界に接する（左では一部がACTPにかかる）」に直した。
- 助言2（記録）：ラベルのアトラスは左右対称ではない。右半球の集計（監査役）：内包後脚 y≈−24 の白質で 右 PCTP 367・LLS 307（左 LLS 361・PCTP 102）、扁桃体 右 MCAT 717、鉤 右 MCAT 125、海馬頭 右 ACTP 70・MCAT 55、海馬体部 右 ACTP 125、楔前部 右 ACA 728／PCAO 729、延髄外側 右 B 125。「内包後脚の後部の一部は PCTP」は右（約半分）とも矛盾しない。
