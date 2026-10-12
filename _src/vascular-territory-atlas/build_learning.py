# -*- coding: utf-8 -*-
"""HO 解剖候補と JHU 全20構造を別データとして準備する（左右反転しない）。

python build_learning.py --inputs <FSL配布物から選択抽出したディレクトリ>
原データ・XML は sources/ にコピーして配布する。VTA1 の主格子を変更しない。
"""
import argparse
import gzip
import hashlib
import json
import shutil
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from build_data import read_nifti, pack

HERE = Path(__file__).resolve().parent
FSL_URL = 'https://fsl.fmrib.ox.ac.uk/fsl/docs/other/datasets.html'


def xml_labels(path):
    labels = {int(e.attrib['index']): e.text.strip() for e in ET.parse(path).findall('./data/label')}
    if sorted(labels) != list(range(len(labels))):
        raise ValueError('連続した0始まり XML index が必要です')
    return labels


def copy_source(src, dst):
    if src.resolve() != dst.resolve():
        shutil.copy2(src, dst)


def sparse_top3(prob):
    """上位3候補の label=index+1 と0–100%を保持。最大値で正規化しない。"""
    ids = np.argsort(-prob.astype(np.float32), axis=3, kind='stable')[..., :3]
    values = np.take_along_axis(prob, ids, axis=3)
    positive = values > 0
    labels = np.where(positive, ids + 1, 0).astype(np.uint8)
    q = np.clip(np.rint(values), 0, 100).astype(np.uint8)
    q[positive & (q == 0)] = 1
    return np.concatenate([labels, q], axis=3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', required=True)
    args = ap.parse_args()
    src = Path(args.inputs)
    sources = HERE / 'sources'
    sources.mkdir(exist_ok=True)
    content = json.loads((HERE / 'learning.json').read_text(encoding='utf-8'))
    vols, provenance = [], []
    for group, xml in [('cort', 'HarvardOxford-Cortical.xml'), ('sub', 'HarvardOxford-Subcortical.xml')]:
        labels = xml_labels(src / xml)
        pn = 'HarvardOxford-%s-prob-2mm.nii.gz' % group
        mn = 'HarvardOxford-%s-maxprob-thr0-2mm.nii.gz' % group
        p, aff = read_nifti(src / pn)
        m, maff = read_nifti(src / mn)
        if p.shape[3] != len(labels) or not np.allclose(aff, maff):
            raise ValueError('HO XML / probability / maxprob の対応が不一致')
        # 同率のwinnerは供給元で異なり得る。maxprob の値が最大確率のチャネルを指すことを全ボクセル照合。
        active = m > 0
        picked = np.take_along_axis(p, np.maximum(m.astype(int) - 1, 0)[..., None], axis=3)[..., 0]
        if not np.allclose(picked[active], p.max(axis=3)[active], atol=1e-4):
            raise ValueError('HO maxprob label != XML index+1')
        for idx, name in labels.items():
            if content['anatomy'][group][idx]['en_original'] != name:
                raise ValueError('名称のずれ: %s:%s' % (group, idx))
        vols.extend([(group + '_top', sparse_top3(p), aff, {'channels': 6, 'retained': 3}),
                     (group + '_label', m.astype(np.uint8), aff, {})])
        provenance.append({'group': group, 'affine': aff.tolist(), 'dims': list(p.shape), 'maxprob_index_check': True})
        for name in [pn, mn, xml]:
            copy_source(src / name, sources / name)

    pn, xml = 'JHU-ICBM-tracts-prob-2mm.nii.gz', 'JHU-tracts.xml'
    labels = xml_labels(src / xml)
    p, aff = read_nifti(src / pn)
    summary, saff = read_nifti(src / 'JHU-ICBM-tracts-maxprob-thr0-2mm.nii.gz')
    active = summary > 0
    picked = np.take_along_axis(p, np.maximum(summary.astype(int) - 1, 0)[..., None], axis=3)[..., 0]
    if not np.allclose(aff, saff) or not np.allclose(picked[active], p.max(axis=3)[active]):
        raise ValueError('JHU maxprob label != XML index+1')
    indexes = list(range(len(labels)))
    selected = []
    for idx, t in zip(indexes, content['tracts']):
        if labels[idx] != t['en_original'] or t['source_index'] != idx:
            raise ValueError('JHU index / 名称のずれ')
        data = p[..., idx]
        if float(data.max()) <= 0 or float(data.max()) > 100:
            raise ValueError('JHU の0–100%範囲外')
        i, j, k = np.unravel_index(np.argmax(data), data.shape)
        mm = aff @ np.array([i, j, k, 1.0])
        if (t['side'] == 'L' and mm[0] >= 0) or (t['side'] == 'R' and mm[0] <= 0):
            raise ValueError('JHU の左右ラベルと座標が不一致')
        t['center_mm'] = mm[:3].tolist()
        t['available'] = True
        selected.append(data.astype(np.uint8))
    vols.append(('tracts_jhu', np.stack(selected, axis=3), aff, {'channels': len(indexes), 'unit': 'percent', 'mirrored': False, 'source_indexes': indexes}))
    for name in [pn, xml, 'JHU-ICBM-tracts-maxprob-thr0-2mm.nii.gz']:
        copy_source(src / name, sources / name)
    files = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sources.iterdir() if f.is_file()}
    content['data_provenance'] = {'files_sha256': files, 'ho': provenance, 'jhu': {'affine': aff.tolist(), 'dims': list(p.shape)}, 'mirrored': False}
    raw_len, gz_len, _ = pack(vols, {'learning_version': 1}, HERE / 'learning_data.bin.gz')
    (HERE / 'learning.json').write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('learning data: raw=%d gzip=%d' % (raw_len, gz_len))
    print('XML index / maxprob / 左右検査 PASS')


if __name__ == '__main__':
    main()
