# -*- coding: utf-8 -*-
"""血管支配領域アトラスの埋め込みデータ（atlas_data.bin.gz）を作る。

入力は2通り:
  1) --legacy <旧版HTML>   旧版に埋め込まれていた2mmボリューム（T1/Level1）を取り出す
  2) --l1 <ArterialAtlas.nii[.gz]> [--l2 ...] [--t1 ...] [--prob ...] [--bz ...]
     NITRC 配布の原データ（Liu CF, et al. Sci Data 2023;10:74）から作る

出力形式（ビュアー側 template.html の loadAtlasData と対で読む）:
  b"VTA1" + uint32(ヘッダ長) + ヘッダJSON(ASCII) + 4バイト境界まで0埋め + 各ボリュームの生バイト
  ボリュームは x が最速（idx = i + j*nx + k*nx*ny）。affine は voxel→MNI(mm) の4x4（行優先）。

使い方:
  python build_data.py --legacy ../../vascular-territory-atlas.html --out atlas_data.bin.gz
  python build_data.py --l1 Atlas_182_MNI152/ArterialAtlas.nii --l2 Atlas_182_MNI152/ArterialAtlas_level2.nii \
      --prob Atlas_182_MNI152/ProbArterialAtlas_average.nii --bz Atlas_182_MNI152/BorderZone_ProbAve.nii \
      --t1-legacy <旧版HTML> --out atlas_data.bin.gz

確率マップと境界領域について:
  原著は右半球の病変を左右反転し、すべて左半球として集計している（Liu 2023 Methods）。そのため原データの
  確率マップ・境界領域は左半球にしか値がない。既定では x>0 の側を左半球の値の左右反転で埋める（--no-mirror で無効）。
"""
import argparse
import base64
import gzip
import json
import re
import struct
import sys
from pathlib import Path

import numpy as np

# Level1 → Level2 の対応（ArterialAtlasLables.txt の Level2_intensity 列）
L1_TO_L2 = {1: 1, 2: 2, 3: 1, 4: 2, 5: 3, 6: 4, 7: 3, 8: 4, 9: 3, 10: 4, 11: 3, 12: 4,
            13: 3, 14: 4, 15: 3, 16: 4, 17: 5, 18: 6, 19: 5, 20: 6, 21: 5, 22: 6,
            23: 5, 24: 6, 25: 7, 26: 8, 27: 7, 28: 8, 29: 7, 30: 8, 31: 9, 32: 10}


# ---------------------------------------------------------------- NIfTI-1 最小リーダ
NIFTI_DTYPES = {2: 'u1', 4: 'i2', 8: 'i4', 16: 'f4', 64: 'f8', 256: 'i1', 512: 'u2', 768: 'u4'}


def read_nifti(path):
    """(data[x,y,z,(t)], affine 4x4) を返す。sform 優先、無ければ qform、どちらも無ければ pixdim。"""
    raw = Path(path).read_bytes()
    if raw[:2] == b'\x1f\x8b':
        raw = gzip.decompress(raw)
    for end in ('<', '>'):
        if struct.unpack(end + 'i', raw[0:4])[0] == 348:
            break
    else:
        raise ValueError('NIfTI-1 ではありません: %s' % path)
    dim = struct.unpack(end + '8h', raw[40:56])
    datatype = struct.unpack(end + 'h', raw[70:72])[0]
    pixdim = struct.unpack(end + '8f', raw[76:108])
    vox_offset = int(struct.unpack(end + 'f', raw[108:112])[0])
    slope, inter = struct.unpack(end + '2f', raw[112:120])
    qform_code, sform_code = struct.unpack(end + '2h', raw[252:256])
    qb, qc, qd, qx, qy, qz = struct.unpack(end + '6f', raw[256:280])
    srow = struct.unpack(end + '12f', raw[280:328])
    ndim = dim[0]
    shape = tuple(dim[1:1 + ndim])
    dt = np.dtype(end + NIFTI_DTYPES[datatype])
    count = int(np.prod(shape))
    data = np.frombuffer(raw, dtype=dt, count=count, offset=vox_offset).reshape(shape, order='F')
    if data.ndim == 4 and data.shape[3] == 1:
        data = data[..., 0]
    if slope not in (0.0, 1.0) or inter != 0.0:
        data = data.astype(np.float32) * (slope if slope != 0 else 1.0) + inter
    if sform_code > 0:
        aff = np.array([srow[0:4], srow[4:8], srow[8:12], [0, 0, 0, 1]], dtype=np.float64)
    elif qform_code > 0:
        qa = np.sqrt(max(0.0, 1.0 - (qb * qb + qc * qc + qd * qd)))
        b, c, d, a = qb, qc, qd, qa
        R = np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                      [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
                      [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - c * c - b * b]])
        qfac = -1.0 if pixdim[0] < 0 else 1.0
        aff = np.eye(4)
        aff[:3, :3] = R @ np.diag([pixdim[1], pixdim[2], pixdim[3] * qfac])
        aff[:3, 3] = [qx, qy, qz]
    else:
        aff = np.diag([pixdim[1], pixdim[2], pixdim[3], 1.0])
    return np.asarray(data), aff


def mirror_left_to_right(vol, aff):
    """x>0（右半球）を、左半球（x<0）の値の左右反転で置き換える。x 軸が格子の第1軸に平行な前提。"""
    out = vol.copy()
    a, b = aff[0, 0], aff[0, 3]
    n = vol.shape[0]
    for i in range(n):
        x = a * i + b
        if x <= 0:
            continue
        j = int(round((-x - b) / a))
        out[i] = vol[j] if 0 <= j < n else 0
    return out


def block_mean(vol, step):
    """step ボクセル四方の立方体で平均する（端の余りは捨てる）"""
    if step == 1:
        return vol
    sx, sy, sz = (d // step for d in vol.shape[:3])
    v = vol[:sx * step, :sy * step, :sz * step]
    v = v.reshape(sx, step, sy, step, sz, step, *vol.shape[3:])
    return v.mean(axis=(1, 3, 5))


# ---------------------------------------------------------------- 旧版HTMLから取り出す
def read_legacy(html_path):
    src = Path(html_path).read_text(encoding='utf-8')
    b64 = re.search(r'GZ_B64\s*=\s*["\']([A-Za-z0-9+/=]+)["\']', src).group(1)
    raw = gzip.decompress(base64.b64decode(b64))
    nx, ny, nz = raw[0], raw[1], raw[2]
    n = nx * ny * nz
    arr = np.frombuffer(raw[3:3 + 3 * n], dtype=np.uint8)
    t1 = arr[:n].reshape((nz, ny, nx)).transpose(2, 1, 0)
    l1 = arr[n:2 * n].reshape((nz, ny, nx)).transpose(2, 1, 0)
    l2 = arr[2 * n:].reshape((nz, ny, nx)).transpose(2, 1, 0)
    # 旧版は FSL MNI152 2mm 格子（182x218x182 を 2mm に間引き）。左ラベル（奇数ID）が i の大きい側に
    # あることから、x(mm) = 90 - 2i の向きと確認済み（2026-10-08）。
    aff = np.array([[-2, 0, 0, 90], [0, 2, 0, -126], [0, 0, 2, -72], [0, 0, 0, 1]], dtype=np.float64)
    return t1, l1, l2, aff


# ---------------------------------------------------------------- 書き出し
def to_u8(vol, lo=None, hi=None):
    v = vol.astype(np.float32)
    lo = np.percentile(v[v > 0], 0.5) if lo is None else lo
    hi = np.percentile(v[v > 0], 99.7) if hi is None else hi
    return np.clip((v - lo) / (hi - lo) * 255.0, 0, 255).round().astype(np.uint8)


def crop_box(mask, margin=2):
    idx = np.nonzero(mask)
    lo = [max(0, int(a.min()) - margin) for a in idx]
    hi = [min(s, int(a.max()) + 1 + margin) for a, s in zip(idx, mask.shape)]
    return lo, hi


def shift_affine(aff, lo):
    out = aff.copy()
    out[:3, 3] = aff[:3, :3] @ np.array(lo, dtype=np.float64) + aff[:3, 3]
    return out


def pack(volumes, meta, out_path):
    """volumes: [(name, array(x,y,z) or (x,y,z,c), affine, extra dict)]"""
    header = {'vols': {}, **meta}
    blobs = []
    offset = 0
    for name, arr, aff, extra in volumes:
        arr = np.ascontiguousarray(arr)
        if arr.ndim == 4:
            data = b''.join(np.ascontiguousarray(arr[..., c]).transpose(2, 1, 0).tobytes() for c in range(arr.shape[3]))
            dims = list(arr.shape[:3])
        else:
            data = arr.transpose(2, 1, 0).tobytes()  # x 最速
            dims = list(arr.shape)
        entry = {'offset': offset, 'dims': dims, 'affine': [round(float(v), 6) for v in aff.reshape(-1)], 'type': 'u8'}
        entry.update(extra)
        header['vols'][name] = entry
        blobs.append(data)
        offset += len(data)
    hjson = json.dumps(header, ensure_ascii=True, separators=(',', ':')).encode('ascii')
    pad = (4 - (8 + len(hjson)) % 4) % 4
    payload = b'VTA1' + struct.pack('<I', len(hjson) + pad) + hjson + b' ' * pad + b''.join(blobs)
    gz = gzip.compress(payload, compresslevel=9, mtime=0)
    Path(out_path).write_bytes(gz)
    return len(payload), len(gz), header


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--legacy')
    ap.add_argument('--l1')
    ap.add_argument('--l2')
    ap.add_argument('--t1')
    ap.add_argument('--prob', help='4D 確率マップ（ACA, MCA, PCA, VB の順）')
    ap.add_argument('--prob-step', type=int, default=2, help='確率マップを何ボクセル四方で平均するか（1mm→2mm なら 2）')
    ap.add_argument('--bz', help='BorderZone_ProbAve.nii（MCA/ACA, MCA/PCA の確率比）')
    ap.add_argument('--no-mirror', action='store_true', help='確率マップ・境界領域を右半球へ反転しない')
    ap.add_argument('--t1-legacy', help='背景T1だけを旧版HTMLの2mmデータから取る')
    ap.add_argument('--t1-step', type=int, default=1)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    if args.legacy:
        t1, l1, l2_given, aff = read_legacy(args.legacy)
        t1_aff = aff
        source = 'legacy-2mm'
    else:
        l1_raw, aff = read_nifti(args.l1)
        l1 = np.rint(l1_raw).astype(np.uint8)
        l2_given = None
        if args.l2:
            l2_raw, aff2 = read_nifti(args.l2)
            assert np.allclose(aff, aff2), 'Level1 と Level2 の格子が違う'
            l2_given = np.rint(l2_raw).astype(np.uint8)
        if args.t1:
            t1_raw, t1_aff = read_nifti(args.t1)
            t1 = to_u8(t1_raw)
        elif args.t1_legacy:
            t1, _l1o, _l2o, t1_aff = read_legacy(args.t1_legacy)
        else:
            t1, t1_aff = None, None
        source = 'nifti'

    # Level2 は Level1 からの写像で作る（原データの Level2 と一致するか確認）
    lut = np.zeros(256, dtype=np.uint8)
    for k, v in L1_TO_L2.items():
        lut[k] = v
    if l2_given is not None:
        mism = int((lut[l1] != l2_given).sum())
        print('Level2 写像の不一致ボクセル:', mism, '/', int((l1 > 0).sum()))

    # 主格子（ラベル）を脳の外接箱で切り詰める
    mask = l1 > 0
    if t1 is not None and t1.shape == l1.shape:
        mask = mask | (t1 > 20)
    lo, hi = crop_box(mask)
    sl = tuple(slice(a, b) for a, b in zip(lo, hi))
    l1c = l1[sl]
    aff_c = shift_affine(aff, lo)
    vols = [('l1', l1c, aff_c, {})]

    if t1 is not None:
        # 同じ格子点の集合で軸の向きだけ違う（例: TemplateFlow の RAS と FSL の LAS）なら並べ替えて主格子にそろえる
        M = np.linalg.inv(t1_aff) @ aff
        R = M[:3, :3]
        if (np.allclose(R, np.diag(np.diag(R))) and np.allclose(np.abs(np.diag(R)), 1)
                and np.allclose(M[:3, 3], np.rint(M[:3, 3]))):
            idx = [np.rint(R[a, a] * np.arange(l1.shape[a]) + M[a, 3]).astype(int) for a in range(3)]
            if all(ix.min() >= 0 and ix.max() < t1.shape[a] for a, ix in enumerate(idx)):
                t1 = t1[np.ix_(*idx)]
                t1_aff = aff
        if t1.shape == l1.shape and np.allclose(t1_aff, aff) and not args.legacy:
            # 背景用なので 7bit に落とし、x 方向の差分で持つ（gzip が約3割よく効く）。ビュアー側で累積和に戻す
            q = (t1[sl].astype(np.int16) >> 1) << 1
            d = (np.diff(q, axis=0, prepend=0) & 0xFF).astype(np.uint8)
            vols.append(('t1', d, aff_c, {'enc': 'delta-x', 'bits': 7}))
        elif t1.shape == l1.shape and np.allclose(t1_aff, aff):
            vols.append(('t1', t1[sl], aff_c, {}))
        else:
            step = args.t1_step
            vols.append(('t1', t1[::step, ::step, ::step], t1_aff @ np.diag([step, step, step, 1]), {}))

    mirror = not args.no_mirror
    if args.prob:
        prob, paff = read_nifti(args.prob)
        assert prob.ndim == 4 and prob.shape[3] >= 4, 'prob は4D（ACA,MCA,PCA,VB）'
        p = np.nan_to_num(np.asarray(prob[..., :4], dtype=np.float64))
        if mirror:
            p = mirror_left_to_right(p, paff)
        step = args.prob_step
        p = block_mean(p, step)
        scales, chans = [], []
        for c in range(4):
            mx = float(p[..., c].max()) or 1.0
            q = np.clip(np.rint(p[..., c] / mx * 255.0), 0, 255)
            q[(p[..., c] > 0) & (q < 1)] = 1  # 0 でない値は 1 以上に残す
            scales.append(round(mx, 6))
            chans.append(q.astype(np.uint8))
        pu8 = np.stack(chans, axis=-1)
        # 平均後の格子の voxel i は、元の voxel step*i + (step-1)/2 が中心
        h = (step - 1) / 2
        paff2 = paff @ np.array([[step, 0, 0, h], [0, step, 0, h], [0, 0, step, h], [0, 0, 0, 1]], dtype=np.float64)
        vols.append(('prob', pu8, paff2, {'channels': 4, 'names': ['ACA', 'MCA', 'PCA', 'VB'], 'scale': scales,
                                           'mirrored': mirror, 'method': 'average'}))
        print('確率マップ: 各血管の最大値', scales)
    if args.bz:
        bz, baff = read_nifti(args.bz)
        assert np.allclose(baff, aff), '境界領域とラベルの格子が違う'
        b = np.asarray(bz, dtype=np.float64)
        b = np.where(np.isfinite(b) & (b > 0), b, 0.0)
        if mirror:
            b = mirror_left_to_right(b, baff)
        DIV = 50.0
        q = np.clip(np.rint(b * DIV), 0, 255)
        q[(b > 0) & (q < 1)] = 1
        q = q.astype(np.uint8)[sl[0], sl[1], sl[2], :2]
        vols.append(('bz', q, aff_c, {'channels': 2, 'names': ['MCA/ACA', 'MCA/PCA'], 'div': DIV, 'mirrored': mirror}))
        print('境界領域: MCA/ACA %d・MCA/PCA %d ボクセル（反転・切り詰め後）' % (int((q[..., 0] > 0).sum()), int((q[..., 1] > 0).sum())))

    meta = {'source': source, 'l2map': {str(k): v for k, v in L1_TO_L2.items()}}
    raw_len, gz_len, header = pack(vols, meta, args.out)
    print('dims(l1)=', header['vols']['l1']['dims'], 'raw=%.2fMB gz=%.2fMB b64=%.2fMB' % (
        raw_len / 1e6, gz_len / 1e6, gz_len * 4 / 3 / 1e6))
    for k, v in header['vols'].items():
        print(' ', k, v['dims'], v.get('channels', 1), 'ch')


if __name__ == '__main__':
    sys.exit(main())
