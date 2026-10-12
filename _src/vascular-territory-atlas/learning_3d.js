// JHU等の確率領域の立体表示。元2mm格子の閾値境界を全点使用し、曲線や軸索を生成しない。
// 独立した束ごとの手前側Zバッファを合成。半透明比較では奥の束も色として残す。
var T3 = { threshold: -1, surfaces: {}, builds: 0, brain: true, stats: {}, raster: null };
function ensureTractSurfaces() {
  var ts = selectedTracts(), wanted = {}, n, t;
  if (T3.threshold !== G.threshold) { T3.surfaces = {}; T3.threshold = G.threshold; }
  for (n = 0; n < ts.length; n++) {
    t = ts[n]; wanted[t.id] = true;
    if (T3.surfaces[t.id]) continue;
    var v = G.vols[t.volume], dims = v.meta.dims, nx = dims[0], ny = dims[1], nz = dims[2], nxy = nx * ny, off = t.channel * v.nvox;
    var data = v.data, threshold = G.threshold, xs = [], ps = [], i, j, k, q, val, mm, count = 0;
    // 3D画質セレクタの間引きは神経束には適用しない。1ボクセル厚の領域も保持する。
    for (k = 0; k < nz; k++) for (j = 0; j < ny; j++) for (i = 0; i < nx; i++) {
      q = i + j * nx + k * nxy; val = data[off + q];
      if (val < threshold || val === 0) continue;
      count++;
      if (i > 0 && i < nx - 1 && j > 0 && j < ny - 1 && k > 0 && k < nz - 1 &&
          data[off + q - 1] >= threshold && data[off + q + 1] >= threshold &&
          data[off + q - nx] >= threshold && data[off + q + nx] >= threshold &&
          data[off + q - nxy] >= threshold && data[off + q + nxy] >= threshold) continue;
      mm = apply4(v.meta.affine, i, j, k);
      xs.push(mm[0], mm[1], mm[2]); ps.push(val);
    }
    var vox = Math.max(Math.sqrt(v.meta.affine[0] * v.meta.affine[0] + v.meta.affine[4] * v.meta.affine[4] + v.meta.affine[8] * v.meta.affine[8]),
      Math.sqrt(v.meta.affine[1] * v.meta.affine[1] + v.meta.affine[5] * v.meta.affine[5] + v.meta.affine[9] * v.meta.affine[9]),
      Math.sqrt(v.meta.affine[2] * v.meta.affine[2] + v.meta.affine[6] * v.meta.affine[6] + v.meta.affine[10] * v.meta.affine[10]));
    T3.surfaces[t.id] = { pts: new Float32Array(xs), prob: new Uint8Array(ps), n: ps.length, count: count, voxel: vox };
    T3.builds++;
  }
  for (t in T3.surfaces) if (!wanted[t]) delete T3.surfaces[t];
  return ts;
}
function tract3DStatus(ts) {
  var el = $('tract3d-status');
  if (!el) return;
  el.style.display = R3.mode === 'tracts' ? 'block' : 'none';
  if (R3.mode !== 'tracts') return;
  var h = '<b>標準アトラスの確率領域（2mm）</b> — 個人の線維追跡・軸索・走行方向を描いたものではありません。<br>';
  if (S.hideOverlay) h += 'クイズ中は神経束を隠しています。';
  else if (!ts.length) h += '「解剖・神経束」タブで表示する束を選んでください。';
  else {
    for (var n = 0; n < ts.length; n++) {
      var s = T3.surfaces[ts[n].id];
      h += '<span style="display:inline-block;margin-right:8px;color:' + rgb(ts[n].color) + ';">● ' + esc(ts[n].ja) + (s && s.n ? '' : '（閾値以上なし）') + '</span>';
    }
    h += '<br>表示閾値 ' + G.threshold + '% / 面の不透明度 ' + Math.round(G.opacity * 100) + '%。色の明るさに確率を反映します。各束の手前側の面を半透明で色合成し、重なりの前後関係は厳密に判定できません。';
  }
  if (!S.hideOverlay) {
    var mm = vox2mm(S.i, S.j, S.k), ar = anatomyAt(mm), name = '';
    for (var j = 0; j < ar.groups.length; j++) if (ar.groups[j].label) { name = anatomyName(ar.groups[j].key, ar.groups[j].label, mm, false); break; }
    h += '<br><span style="color:#facc15;">黄色の印: カーソル位置</span>' + (name ? ' — ' + esc(name) : ' — 解剖ラベル未収録') + '（MNI ' + fmtSigned(mm[0]) + ', ' + fmtSigned(mm[1]) + ', ' + fmtSigned(mm[2]) + '）';
  }
  // 名前/閾値等が変わる時だけDOMを更新し、回転時のcanvas寸法を安定させる。
  if (el.innerHTML !== h) el.innerHTML = h;
}
function drawTracts3D(renderer, img, w, h, scale) {
  var ts = ensureTractSurfaces();
  T3.stats = { points: {}, pixels: {}, selected: ts.length, threshold: G.threshold, opacity: G.opacity };
  var N = w * h, n, p;
  if (!ts.length || S.hideOverlay || G.opacity <= 0) return;
  if (!T3.raster || T3.raster.N !== N) {
    T3.raster = { N: N, z: new Float32Array(N), prob: new Uint8Array(N), r: new Float32Array(N), g: new Float32Array(N), b: new Float32Array(N), sum: new Float32Array(N), reveal: new Float32Array(N) };
  }
  var rr = T3.raster, zbuf = rr.z, probs = rr.prob, cr = rr.r, cg = rr.g, cb = rr.b, sum = rr.sum, reveal = rr.reveal;
  for (p = 0; p < N; p++) { cr[p] = 0; cg[p] = 0; cb[p] = 0; sum[p] = 0; reveal[p] = 1; }
  var out = [0, 0, 0], ox = w / 2, oy = h / 2;
  for (n = 0; n < ts.length; n++) {
    var t = ts[n], s = T3.surfaces[t.id], pts = s.pts, prob = s.prob, q, sx, sy, depth, a, b, x, y, val, px = 0;
    T3.stats.points[t.id] = s.n;
    if (!s.n) { T3.stats.pixels[t.id] = 0; continue; }
    for (p = 0; p < N; p++) { zbuf[p] = 1e9; probs[p] = 0; }
    // 元格子幅に対応する点スプラット。1ボクセルの細い束を間引かない。
    var diam = Math.max(2, Math.ceil(scale * s.voxel * 1.15)), half = diam >> 1;
    for (q = 0; q < s.n; q++) {
      renderer.project(pts[q * 3], pts[q * 3 + 1], pts[q * 3 + 2], out);
      sx = Math.round(ox + out[0] * scale); sy = Math.round(oy - out[1] * scale); depth = out[2]; val = prob[q];
      for (b = 0; b < diam; b++) {
        y = sy + b - half; if (y < 0 || y >= h) continue;
        for (a = 0; a < diam; a++) {
          x = sx + a - half; if (x < 0 || x >= w) continue;
          p = y * w + x;
          if (depth < zbuf[p]) { zbuf[p] = depth; probs[p] = val; }
          else if (Math.abs(depth - zbuf[p]) < 0.01 && val > probs[p]) probs[p] = val;
        }
      }
    }
    for (p = 0; p < N; p++) if (probs[p]) {
      var alpha = G.opacity;
      // 3D閾値面はスライダーの不透明度で描き、低確率の薄い境界を消さない。
      // 明るさに確率と弱い奥行き陰影を反映する（確率データ自体の変更・正規化はしない）。
      var shade = (0.75 + 0.25 * probs[p] / 100) * (0.9 + 0.1 * clamp((renderer.radius - zbuf[p]) / (renderer.radius * 2), 0, 1));
      cr[p] += t.color[0] * shade * alpha; cg[p] += t.color[1] * shade * alpha; cb[p] += t.color[2] * shade * alpha;
      sum[p] += alpha; reveal[p] *= 1 - alpha; px++;
    }
    T3.stats.pixels[t.id] = px;
  }
  for (p = 0; p < N; p++) if (sum[p]) {
    var total = 1 - reveal[p], inv = total / sum[p], off = p * 4;
    img[off] = img[off] * reveal[p] + cr[p] * inv;
    img[off + 1] = img[off + 1] * reveal[p] + cg[p] * inv;
    img[off + 2] = img[off + 2] * reveal[p] + cb[p] * inv;
  }
}
