// 解剖 / 神経束の共通レジストリ。血管確率と独立し、左右反転による補充を行わない。
var G = { vols: {}, selected: {}, opacity: 0.65, threshold: 10, anatomy: null };
function parseLearning(bytes) {
  if (String.fromCharCode(bytes[0], bytes[1], bytes[2], bytes[3]) !== 'VTA1') throw new Error('学習データの形式が違います');
  var hlen = bytes[4] | (bytes[5] << 8) | (bytes[6] << 16) | (bytes[7] << 24), hs = '', n, key;
  for (n = 0; n < hlen; n++) hs += String.fromCharCode(bytes[8 + n]);
  var h = JSON.parse(hs), base = 8 + hlen;
  for (key in h.vols) {
    if (!Object.prototype.hasOwnProperty.call(h.vols, key)) continue;
    var m = h.vols[key], nv = m.dims[0] * m.dims[1] * m.dims[2];
    if (m.type !== 'u8') throw new Error('未対応の学習データ型');
    G.vols[key] = { meta: m, nvox: nv, inv: matInv4(m.affine), data: bytes.subarray(base + m.offset, base + m.offset + nv * (m.channels || 1)) };
  }
}
// 完全な4x4 affineを使う。回転・せん断・RAS/LAS・半ボクセルを扱う。
function learningPoint(v, mm) { return apply4(v.inv, mm[0], mm[1], mm[2]); }
function learningInside(v, p) { return p[0] >= 0 && p[1] >= 0 && p[2] >= 0 && p[0] <= v.meta.dims[0] - 1 && p[1] <= v.meta.dims[1] - 1 && p[2] <= v.meta.dims[2] - 1; }
function learningIndex(v, i, j, k) { return i + j * v.meta.dims[0] + k * v.meta.dims[0] * v.meta.dims[1]; }
function sampleLearning(v, mm, channel, linear) {
  if (!v) return null;
  var p = learningPoint(v, mm);
  if (!learningInside(v, p)) return null;
  var off = channel * v.nvox;
  if (!linear) return v.data[off + learningIndex(v, Math.round(p[0]), Math.round(p[1]), Math.round(p[2]))];
  var x0 = Math.floor(p[0]), y0 = Math.floor(p[1]), z0 = Math.floor(p[2]), sum = 0, dx, dy, dz;
  for (dz = 0; dz < 2; dz++) for (dy = 0; dy < 2; dy++) for (dx = 0; dx < 2; dx++) {
    var w = (dx ? p[0] - x0 : 1 - p[0] + x0) * (dy ? p[1] - y0 : 1 - p[1] + y0) * (dz ? p[2] - z0 : 1 - p[2] + z0);
    if (!w) continue;
    var x = Math.min(x0 + dx, v.meta.dims[0] - 1), y = Math.min(y0 + dy, v.meta.dims[1] - 1), z = Math.min(z0 + dz, v.meta.dims[2] - 1);
    sum += w * v.data[off + learningIndex(v, x, y, z)];
  }
  return sum;
}
function anatomyAt(mm) {
  var out = { mm: mm, groups: [] }, names = ['cort', 'sub'], n;
  for (n = 0; n < names.length; n++) {
    var key = names[n], v = G.vols[key + '_top'], m = G.vols[key + '_label'];
    if (!v || !m) continue;
    var p = learningPoint(v, mm), group = { key: key, label: sampleLearning(m, mm, 0, false), candidates: [] };
    if (!learningInside(v, p)) { group.outside = true; out.groups.push(group); continue; }
    var x0 = Math.floor(p[0]), y0 = Math.floor(p[1]), z0 = Math.floor(p[2]), sums = {}, dx, dy, dz, rank, id;
    for (dz = 0; dz < 2; dz++) for (dy = 0; dy < 2; dy++) for (dx = 0; dx < 2; dx++) {
      var w = (dx ? p[0] - x0 : 1 - p[0] + x0) * (dy ? p[1] - y0 : 1 - p[1] + y0) * (dz ? p[2] - z0 : 1 - p[2] + z0);
      if (!w) continue;
      var q = learningIndex(v, Math.min(x0 + dx, v.meta.dims[0] - 1), Math.min(y0 + dy, v.meta.dims[1] - 1), Math.min(z0 + dz, v.meta.dims[2] - 1));
      for (rank = 0; rank < 3; rank++) {
        id = v.data[q + rank * v.nvox];
        if (id) sums[id] = (sums[id] || 0) + w * v.data[q + (rank + 3) * v.nvox];
      }
    }
    for (id in sums) if (Object.prototype.hasOwnProperty.call(sums, id) && sums[id] >= 1) group.candidates.push({ id: parseInt(id, 10), percent: sums[id] });
    group.candidates.sort(function (a, b) { return b.percent - a.percent || a.id - b.id; });
    group.candidates = group.candidates.slice(0, 3);
    out.groups.push(group);
  }
  return out;
}
function anatomyName(group, id, mm, english) {
  var d = LEARNING.anatomy[group][id - 1];
  if (!d) return '未定義';
  var s = english ? d.en : d.ja;
  if (group === 'cort') s = (mm[0] < -0.5 ? (english ? 'Left ' : '左 ') : mm[0] > 0.5 ? (english ? 'Right ' : '右 ') : (english ? 'Midline vicinity ' : '正中付近 ')) + s;
  return s;
}
function learningRefsHTML(keys) {
  var h = '', n, seen = {};
  for (n = 0; n < keys.length; n++) { var r = LEARNING.references[keys[n]]; if (r && !seen[keys[n]]) { seen[keys[n]] = true; h += '<div class="meta-line"><a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.title) + '</a></div>'; } }
  return h;
}
function anatomyHTML(mm) {
  if (!LEARNING || !G.vols.cort_top) return '<div class="info-card"><div class="note">解剖アトラス未収録</div></div>';
  var result = anatomyAt(mm), h = '<div class="info-card" class="anatomy-position"><div class="section-title">🧠 この位置の解剖</div>', n, j;
  for (n = 0; n < result.groups.length; n++) {
    var g = result.groups[n];
    h += '<div class="sub-head">' + (g.key === 'cort' ? '皮質の候補' : '皮質下・組織の候補') + '</div>';
    if (g.outside) { h += '<div class="note">この解剖アトラスの収録範囲外です。</div>'; continue; }
    if (!g.candidates.length) { h += '<div class="note">候補なし（未収録・確率1%未満）。小脳等をこのアトラスで細分できません。</div>'; continue; }
    if (g.label) h += '<div class="meta-line">最近傍の代表ラベル: ' + esc(anatomyName(g.key, g.label, mm, false)) + '</div>';
    for (j = 0; j < g.candidates.length; j++) {
      var c = g.candidates[j], d = LEARNING.anatomy[g.key][c.id - 1];
      h += '<details' + (j === 0 ? ' open' : '') + '><summary><b>' + esc(anatomyName(g.key, c.id, mm, false)) + '</b> <span class="mono">' + c.percent.toFixed(1) + '%</span></summary><div class="territory-en">' + esc(anatomyName(g.key, c.id, mm, true)) + '</div><div class="section-body">' + esc(d.function) + '</div><div class="note">関連症候: ' + esc(d.symptoms) + '</div>' + learningRefsHTML(d.refs) + '</details>';
    }
  }
  h += '<div class="note">Harvard–Oxford の集団分布です。各2mm格子点の上位3候補を保存し、確率は連続補間しています。小さい候補は省略され、合計は100%とは限りません。皮質の左右はMNI X座標に基づく表示です。患者個人の部位や症候を確定しません。</div></div>';
  return h;
}
function selectedTracts() {
  var out = [], n;
  for (n = 0; n < LEARNING.tracts.length; n++) if (G.selected[LEARNING.tracts[n].id] && G.vols[LEARNING.tracts[n].volume]) out.push(LEARNING.tracts[n]);
  return out;
}
function tractValuesAt(mm, all) {
  var out = [], ts = all ? LEARNING.tracts : selectedTracts(), n;
  for (n = 0; n < ts.length; n++) { var t = ts[n], val = sampleLearning(G.vols[t.volume], mm, t.channel, true); out.push({ id: t.id, percent: val }); }
  return out;
}
function tractColorAt(mm, tracts) {
  var r = 0, g = 0, b = 0, weight = 0, max = 0, n;
  for (n = 0; n < tracts.length; n++) {
    var t = tracts[n], v = sampleLearning(G.vols[t.volume], mm, t.channel, true);
    if (v == null || v <= 0 || v < G.threshold) continue;
    weight += v; r += t.color[0] * v; g += t.color[1] * v; b += t.color[2] * v; max = Math.max(max, v);
  }
  return weight ? [Math.round(r / weight), Math.round(g / weight), Math.round(b / weight), G.opacity * max / 100] : null;
}
function updateLearningPosition(mm) {
  if (!$('learning-position')) return;
  $('learning-position').innerHTML = S.hideOverlay ? '<div class="note">クイズ中は部位名・神経束情報を隠しています。</div>' : anatomyHTML(mm);
  var ts = selectedTracts(), h = '', n;
  for (n = 0; n < ts.length; n++) {
    var t = ts[n], v = sampleLearning(G.vols[t.volume], mm, t.channel, true);
    h += '<div class="info-card"><div class="section-title" style="color:' + rgb(t.color) + '">' + esc(t.ja) + '</div><div class="territory-en">' + esc(t.en) + '</div><div class="meta-line">この位置: ' + (v == null ? 'データ範囲外' : v <= 0 ? '分布なし' : v.toFixed(1) + '%（' + (v < G.threshold ? '表示しきい値未満' : '表示範囲内') + '）') + '</div><div class="section-body">走行・接続: ' + esc(t.course) + '<br>機能: ' + esc(t.function) + '</div><div class="note">関連症候: ' + esc(t.symptoms) + '</div>' + learningRefsHTML(t.refs) + '</div>';
  }
  $('tract-position').innerHTML = S.hideOverlay ? '' : h;
}
function buildLearningUI() {
  if (!LEARNING) return;
  var h = '', n, ts = LEARNING.tracts;
  for (n = 0; n < ts.length; n++) {
    var t = ts[n], available = t.available && !!G.vols[t.volume];
    h += '<div class="info-card tract-choice" data-search="' + esc((t.ja + ' ' + t.en + ' ' + t.family).toLowerCase()) + '"><label><input type="checkbox" data-tract="' + esc(t.id) + '"' + (available ? '' : ' disabled') + '> <span style="color:' + rgb(t.color) + '">●</span> ' + esc(t.ja) + '</label><div class="territory-en">' + esc(t.en) + '</div><button type="button" class="btn btn-secondary btn-small" data-tract-jump="' + esc(t.id) + '"' + (available ? '' : ' disabled') + '>代表位置へ移動</button>' + (available ? '' : '<div class="note">実データ未収録のため利用できません。</div>') + '</div>';
  }
  $('tract-list').innerHTML = h;
  $('learning-license').innerHTML = '<div class="credit">解剖: Harvard–Oxford（CC BY-SA 4.0、上位候補抽出・日本語説明を追加）。神経束: JHU tractography atlas（FSL非商用条件）。JHUの全20構造は9組の左右別構造と2つの交連構造です。SLFの枝別・独立AFは収録しません。<br><a href="downloads/MNI_Vascular_Territory_Atlas_Standalone.zip">原データ・XML・加工コード・ライセンス全文を含む配布ZIP</a><br>JHUデータと派生物は無償・非商用条件を受領者にも引き継いでください。単体HTMLだけを再配布せずソース一式を同梱してください。ZIP内に全文と変更記録があります。<details><summary>FSLライセンス全文（オフラインでも読めます）</summary><pre style="white-space:pre-wrap;word-break:break-word;">' + esc(LEARNING.license_text || '') + '</pre></details></div>';
  on($('tract-list'), 'change', function (e) {
    var id = e.target.getAttribute('data-tract'); if (!id) return;
    G.selected[id] = !!e.target.checked; markAllDirty(); updateLearningPosition(vox2mm(S.i, S.j, S.k)); scheduleHash(); requestRender();
  });
  on($('tract-list'), 'click', function (e) {
    var id = e.target.getAttribute('data-tract-jump'); if (!id) return;
    for (var j = 0; j < ts.length; j++) if (ts[j].id === id && ts[j].available) {
      G.selected[id] = true; var c = $('tract-list').querySelector('[data-tract="' + id + '"]'); if (c) c.checked = true;
      setLayout(window.innerWidth > 900 ? 'all' : 'axial'); setCursorMM(ts[j].center_mm[0], ts[j].center_mm[1], ts[j].center_mm[2]); markAllDirty(); requestRender(); break;
    }
  });
  on($('tract-search'), 'input', function () {
    var term = this.value.toLowerCase(); forEachNode(document.querySelectorAll('.tract-choice'), function (el) { el.style.display = el.getAttribute('data-search').indexOf(term) >= 0 ? '' : 'none'; });
  });
  on($('sl-tract-opacity'), 'input', function () { G.opacity = parseInt(this.value, 10) / 100; $('lb-tract-opacity').textContent = this.value + '%'; markAllDirty(); scheduleHash(); requestRender(); });
  on($('sl-tract-threshold'), 'input', function () { G.threshold = parseInt(this.value, 10); $('lb-tract-threshold').textContent = this.value + '%'; markAllDirty(); updateLearningPosition(vox2mm(S.i, S.j, S.k)); scheduleHash(); requestRender(); });
  on($('btn-tract-clear'), 'click', function () { G.selected = {}; forEachNode(document.querySelectorAll('[data-tract]'), function (el) { el.checked = false; }); markAllDirty(); updateLearningPosition(vox2mm(S.i, S.j, S.k)); scheduleHash(); requestRender(); });
  on($('btn-tract-3d'), 'click', function () { R3.mode = 'tracts'; $('sel-3dmode').value = 'tracts'; setLayout('3d'); scheduleHash(); requestRender(); });
  on($('chk-tract-brain'), 'change', function () { T3.brain = this.checked; scheduleHash(); requestRender(); });
}
function restoreLearningHash(h) {
  G.selected = {};
  var ids = typeof h.tracts === 'string' ? h.tracts.split(',') : [], n, j;
  for (n = 0; n < ids.length; n++) for (j = 0; j < LEARNING.tracts.length; j++) if (ids[n] === LEARNING.tracts[j].id && LEARNING.tracts[j].available) G.selected[ids[n]] = true;
  G.threshold = isNaN(h.tt) ? 10 : clamp(h.tt, 1, 100);
  G.opacity = isNaN(h.to) ? 0.65 : clamp(h.to, 0, 100) / 100;
  forEachNode(document.querySelectorAll('[data-tract]'), function (el) { el.checked = !!G.selected[el.getAttribute('data-tract')]; });
  $('sl-tract-opacity').value = Math.round(G.opacity * 100); $('lb-tract-opacity').textContent = Math.round(G.opacity * 100) + '%';
  $('sl-tract-threshold').value = G.threshold; $('lb-tract-threshold').textContent = G.threshold + '%';
  T3.brain = h.d3b !== 0; $('chk-tract-brain').checked = T3.brain;
  if (h.d3t === 1) { R3.mode = 'tracts'; $('sel-3dmode').value = 'tracts'; }
}
