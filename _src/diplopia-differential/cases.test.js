/* 複視鑑別ツールの判定ロジックを代表症例で確かめる回帰テスト。
 *
 *   python _src/diplopia-differential/build.py && node _src/diplopia-differential/cases.test.js
 *
 * 公開ファイル（diplopia-differential.html）をヘッドレスブラウザで開き、window.DiplopiaLogic を直接呼ぶ。
 * 各症例は「出るべき警告・候補」と「出てはいけない警告・候補」を id で指定する。
 */
const path = require('path');
const { chromium } = require('playwright');

const NO = ['neuro', 'headache', 'breathing', 'vision', 'suspectedThird', 'wernicke', 'rapidBilateral', 'trauma', 'orbitAcute', 'immuno', 'gca', 'icp'];
const noFlags = extra => Object.assign(Object.fromEntries(NO.map(k => [k, 'no'])), extra);
const mot = (right = [], left = [], status) => {
  const eye = keys => Object.fromEntries(['abd', 'add', 'up', 'down', 'upOut', 'upIn', 'downOut', 'downIn'].map(k => [k, keys.includes(k)]));
  return { status: status !== undefined ? status : (right.length + left.length ? 'limited' : 'normal'), right: eye(right), left: eye(left) };
};
const UNKNOWN = mot([], [], '');
const bino = { cover: 'binocular' };

// [名前, 入力, 眼球運動, 期待]
// 期待: pattern / side / alerts / noAlerts / cands / noCands / level / notices(件数) / first(先頭候補)
const CASES = [
  ['未入力', {}, UNKNOWN, { pattern: 'unknown', level: 'pending', alerts: [], cands: ['none'] }],
  ['全項目なし・運動正常', noFlags({ ...bino, lid: 'no', pupil: 'equal', onset: 'gradual' }), mot(), { pattern: 'normal', level: 'clear', alerts: [] }],
  ['右外転神経麻痺・高齢・危険因子', noFlags({ ...bino, onset: 'sudden', axis: 'horizontal', range: 'far', gaze: 'right', age: 'older', bg: { vascular: true }, pupil: 'equal', lid: 'no' }), mot(['abd']), { pattern: 'abd', side: 'right', cands: ['sixth', 'micro'], alerts: ['acute'], noCands: ['mg', 'third'], notices: 0 }],
  ['右外転神経麻痺・若年', noFlags({ ...bino, onset: 'days', age: 'young' }), mot(['abd']), { pattern: 'abd', cands: ['sixth'], noCands: ['micro'] }],
  ['左右の取り違え（問診は右、運動は左）', noFlags({ ...bino, gaze: 'right', axis: 'horizontal' }), mot([], ['abd']), { pattern: 'abd', side: 'left', notices: 1 }],
  ['左核間性眼筋麻痺・突然・高齢', { ...bino, onset: 'sudden', age: 'older', nystagmus: 'right' }, mot([], ['add']), { pattern: 'add', side: 'left', alerts: ['stroke'], cands: ['ino'] }],
  ['内転制限のみ・眼振未確認', noFlags({ ...bino, onset: 'gradual' }), mot(['add']), { pattern: 'add', side: 'right', cands: ['ino'], noAlerts: ['stroke'] }],
  ['両側核間性眼筋麻痺・若年', noFlags({ ...bino, onset: 'days', age: 'young', pupil: 'equal' }), mot(['add'], ['add']), { pattern: 'biINO', cands: ['ino', 'mg'] }],
  ['右動眼神経麻痺・瞳孔同大', noFlags({ ...bino, suspectedThird: 'yes', onset: 'sudden', lid: 'newRight', pupil: 'equal', age: 'older', bg: { vascular: true } }), mot(['add', 'up', 'down']), { pattern: 'third', side: 'right', alerts: ['third'], cands: ['third', 'micro'], first: 'third' }],
  ['動眼神経麻痺・緊急所見は未入力でも警告', { ...bino, lid: 'newLeft', pupil: 'leftMyd' }, UNKNOWN, { alerts: ['third'], cands: ['third'] }],
  ['動眼神経の部分麻痺', noFlags({ ...bino, onset: 'days' }), mot(['add', 'up']), { pattern: 'partialThird', alerts: ['third'], cands: ['third'] }],
  ['右ホルネル症候群・痛みあり', noFlags({ ...bino, onset: 'sudden', lid: 'newRight', pupil: 'rightMio', pain: 'periorbital' }), mot(), { alerts: ['horner'], cands: ['horner'], noAlerts: ['third'], noCands: ['third'] }],
  ['下垂と散瞳の左右不一致', noFlags({ ...bino, lid: 'newRight', pupil: 'leftMyd' }), UNKNOWN, { notices: 1 }],
  ['右 one-and-a-half 症候群', noFlags({ ...bino, onset: 'sudden' }), mot(['abd', 'add'], ['add']), { pattern: 'onehalf', side: 'right', alerts: ['stroke'], cands: ['pons'] }],
  ['左 one-and-a-half 症候群', noFlags({ ...bino, onset: 'gradual' }), mot(['add'], ['abd', 'add']), { pattern: 'onehalf', side: 'left', cands: ['pons'], noAlerts: ['stroke'] }],
  ['右への水平注視麻痺', noFlags({ ...bino, onset: 'sudden' }), mot(['abd'], ['add']), { pattern: 'gazeH', side: 'right', alerts: ['stroke'], cands: ['pons'] }],
  ['上方注視麻痺', noFlags({ ...bino, onset: 'gradual' }), mot(['up'], ['up']), { pattern: 'upgaze', cands: ['midbrain', 'ted'] }],
  ['垂直注視麻痺・突然', noFlags({ ...bino, onset: 'sudden' }), mot(['up', 'down'], ['up', 'down']), { pattern: 'vgaze', alerts: ['stroke'], cands: ['midbrain', 'mg'] }],
  ['両側外転制限・ウェルニッケ', noFlags({ ...bino, wernicke: 'yes', onset: 'days' }), mot(['abd'], ['abd']), { pattern: 'biAbd', alerts: ['wernicke'], cands: ['sixth', 'wernicke'] }],
  ['両側外転制限・急性・頭蓋内圧は未確認', { ...bino, onset: 'days' }, mot(['abd'], ['abd']), { pattern: 'biAbd', alerts: ['icp'], cands: ['sixth', 'wernicke'] }],
  ['全外眼筋麻痺・数日', noFlags({ ...bino, onset: 'days', pupil: 'equal' }), mot(['abd', 'add', 'up', 'down'], ['abd', 'add', 'up', 'down']), { pattern: 'total', alerts: ['rapid'], cands: ['total', 'mg'] }],
  ['全外眼筋麻痺・数日・背景は未確認', { ...bino, onset: 'days' }, mot(['abd', 'add', 'up', 'down'], ['abd', 'add', 'up', 'down']), { pattern: 'total', alerts: ['rapid'], cands: ['total', 'wernicke'] }],
  ['全外眼筋麻痺・慢性', noFlags({ ...bino, onset: 'gradual', wernicke: 'no' }), mot(['abd', 'add', 'up', 'down'], ['abd', 'add', 'up', 'down']), { pattern: 'total', alerts: [], cands: ['total', 'mg'], noCands: ['wernicke'] }],
  ['片眼の全方向制限と顔面感覚低下', noFlags({ ...bino, onset: 'gradual', sensation: 'right', pain: 'periorbital' }), mot(['abd', 'add', 'up', 'down']), { pattern: 'uniTotal', side: 'right', cands: ['cavernous', 'painful'] }],
  ['甲状腺眼症（上転・外転の制限、眼球突出）', noFlags({ ...bino, onset: 'gradual', bg: { thyroid: true }, orbit: { proptosis: true, retraction: true }, pupil: 'equal' }), mot(['abd', 'up']), { pattern: 'uniMulti', cands: ['ted', 'mg'], alerts: [] }],
  ['片眼の上転制限', noFlags({ ...bino, onset: 'gradual' }), mot([], ['upOut']), { pattern: 'uniUp', side: 'left', cands: ['ted'] }],
  ['外傷後の右滑車神経麻痺（3段階法）', noFlags({ ...bino, trauma: 'yes', onset: 'sudden', axis: 'vertical', gaze: 'down', hyper: 'right', hyperGaze: 'left', tilt: 'right' }), mot(['downIn']), { pattern: 'uniDown', side: 'right', alerts: ['trauma'], cands: ['fourth', 'trauma'], noCands: ['vertical'] }],
  ['3段階法が上斜筋以外を示す', noFlags({ ...bino, axis: 'vertical', hyper: 'right', hyperGaze: 'right', tilt: 'left' }), UNKNOWN, { cands: ['threestepOther'], noCands: ['fourth'] }],
  ['縦の複視・3段階法は未入力', noFlags({ ...bino, axis: 'vertical' }), UNKNOWN, { cands: ['vertical'] }],
  ['重症筋無力症（変動、易疲労性）', noFlags({ ...bino, course: 'variable', lid: 'variable', fatigue: 'yes', pupil: 'equal' }), mot(['add'], ['up']), { pattern: 'mixed', cands: ['mg'], first: 'mg' }],
  ['呼吸症状', { ...bino, breathing: 'yes', course: 'variable', lid: 'variable' }, UNKNOWN, { level: 'urgent', alerts: ['breathing'], cands: ['mg'] }],
  ['単眼性複視と急性神経症状', { cover: 'monoR', onset: 'sudden', neuro: 'yes' }, UNKNOWN, { alerts: ['stroke'], cands: ['mono'], first: 'mono' }],
  ['単眼性複視のみ', noFlags({ cover: 'monoBoth', onset: 'gradual' }), UNKNOWN, { alerts: [], cands: ['mono'], noCands: ['mg', 'vertical'] }],
  ['サギングアイ症候群', noFlags({ ...bino, onset: 'gradual', course: 'stable', axis: 'horizontal', range: 'far', gaze: 'same', age: 'older', pupil: 'equal', lid: 'no' }), mot(), { pattern: 'normal', cands: ['sagging'], alerts: [], noCands: ['sixth'] }],
  ['遠くで強い水平複視・運動未確認', noFlags({ ...bino, axis: 'horizontal', range: 'far' }), UNKNOWN, { cands: ['distance'] }],
  ['輻輳不全', noFlags({ ...bino, onset: 'gradual', axis: 'horizontal', range: 'near', bg: { strabismus: true } }), mot(), { cands: ['convergence'] }],
  ['運動未確認・右で強い水平複視', noFlags({ ...bino, axis: 'horizontal', gaze: 'right' }), UNKNOWN, { cands: ['gazeHx'] }],
  ['一過性・突然', { ...bino, course: 'transient', onset: 'sudden' }, UNKNOWN, { alerts: ['tia'], cands: ['transient'] }],
  ['進行性と悪性腫瘍の既往', noFlags({ ...bino, onset: 'gradual', course: 'progressive', age: 'older', bg: { cancer: true, vascular: true } }), mot(['abd']), { cands: ['sixth', 'progressive', 'cancer'], noCands: ['micro'] }],
  ['巨細胞性動脈炎', noFlags({ ...bino, gca: 'yes', age: 'older', onset: 'days' }), UNKNOWN, { alerts: ['gca'] }],
  ['突然の頭痛と視力低下', { ...bino, headache: 'yes', vision: 'yes', onset: 'sudden' }, UNKNOWN, { alerts: ['headache', 'vision'], noAlerts: ['acute'] }],
  ['免疫不全・眼窩の急性所見', { ...bino, immuno: 'yes', orbitAcute: 'yes' }, UNKNOWN, { alerts: ['immuno', 'orbit'] }],
  ['頭蓋内圧亢進', noFlags({ ...bino, icp: 'yes', onset: 'gradual' }), mot(['abd']), { alerts: ['icp'], cands: ['sixth'] }],
  ['結膜浮腫と雑音', noFlags({ ...bino, onset: 'gradual', orbit: { chemosis: true, bruit: true } }), mot(['abd']), { cands: ['ccf', 'sixth'] }],
  ['現在は複視なし', noFlags({ cover: 'absent', onset: 'gradual' }), UNKNOWN, { alerts: [] }],
];

const STEP = [
  ['right', 'left', 'right', 'right', '上斜筋'], ['right', 'left', 'left', 'left', '上直筋'],
  ['right', 'right', 'right', 'left', '下斜筋'], ['right', 'right', 'left', 'right', '下直筋'],
  ['left', 'right', 'left', 'left', '上斜筋'], ['left', 'right', 'right', 'right', '上直筋'],
  ['left', 'left', 'left', 'right', '下斜筋'], ['left', 'left', 'right', 'left', '下直筋'],
];

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  const errors = [];
  // file:// ではサービスワーカーを取得できないため、その例外だけ除外する
  page.on('pageerror', e => { if (!/ServiceWorker/.test(String(e))) errors.push(String(e)); });
  await page.goto('file://' + path.resolve(__dirname, '../../diplopia-differential.html'));
  let failed = 0;
  const fail = (name, msg) => { failed++; console.log('NG  ' + name + ' : ' + msg); };

  for (const [name, a, m, want] of CASES) {
    const r = await page.evaluate(([a, m]) => {
      const L = window.DiplopiaLogic, res = L.assess(a, m);
      return { pattern: res.pattern.key, side: res.pattern.side, level: res.level, alerts: res.alerts.map(x => x.id), cands: res.candidates.map(x => x.id), notices: res.notices.length, text: L.handoff(a, m, res) };
    }, [a, m]);
    const before = failed;
    if (want.pattern && r.pattern !== want.pattern) fail(name, 'pattern ' + r.pattern + ' (want ' + want.pattern + ')');
    if (want.side && r.side !== want.side) fail(name, 'side ' + r.side);
    if (want.level && r.level !== want.level) fail(name, 'level ' + r.level);
    if (want.alerts && want.alerts.length === 0 && r.alerts.length) fail(name, 'unexpected alerts ' + r.alerts);
    for (const id of want.alerts || []) if (!r.alerts.includes(id)) fail(name, 'missing alert ' + id + ' (got ' + r.alerts + ')');
    for (const id of want.noAlerts || []) if (r.alerts.includes(id)) fail(name, 'unwanted alert ' + id);
    for (const id of want.cands || []) if (!r.cands.includes(id)) fail(name, 'missing candidate ' + id + ' (got ' + r.cands + ')');
    for (const id of want.noCands || []) if (r.cands.includes(id)) fail(name, 'unwanted candidate ' + id);
    if (want.first && r.cands[0] !== want.first) fail(name, 'first candidate ' + r.cands[0]);
    if (want.notices !== undefined && r.notices !== want.notices) fail(name, 'notices ' + r.notices);
    if (/[～〜]/.test(r.text)) fail(name, 'handoff contains a wave dash');
    if (!r.cands.length) fail(name, 'no candidates');
    if (failed === before) console.log('ok  ' + name);
  }

  for (const [hyper, gaze, tilt, side, muscle] of STEP) {
    const r = await page.evaluate(x => window.DiplopiaLogic.threeStep(x[0], x[1], x[2]), [hyper, gaze, tilt]);
    const name = '3段階法 ' + [hyper, gaze, tilt].join('/');
    if (!r || r.side !== side || r.muscle !== muscle) fail(name, JSON.stringify(r)); else console.log('ok  ' + name);
  }

  // かんたん入力 → 眼位図 → かんたん入力 の往復で制限が保たれること
  const trips = [mot(['abd']), mot(['add', 'up', 'down']), mot(['abd', 'add'], ['add']), mot(['up'], ['up']), mot(['downIn']), mot([], ['upOut']), mot()];
  for (const m of trips) {
    const back = await page.evaluate(m => { const L = window.DiplopiaLogic; return L.deriveMot(L.seedRecords(m)); }, m);
    const name = '往復 ' + JSON.stringify([Object.keys(m.right).filter(k => m.right[k]), Object.keys(m.left).filter(k => m.left[k])]);
    if (JSON.stringify(back) !== JSON.stringify(m)) fail(name, JSON.stringify(back)); else console.log('ok  ' + name);
  }
  // 眼位図：1方向だけの記録は「未記録の方向あり」
  const partial = await page.evaluate(() => window.DiplopiaLogic.deriveMot({ center: { right: { x: 0, y: 0 }, left: { x: 0, y: 0 } }, right: { right: { x: -0.8, y: 0 }, left: { x: -0.8, y: 0 } } }).status);
  if (partial !== 'partial') fail('眼位図の部分記録', partial); else console.log('ok  眼位図の部分記録');

  if (errors.length) fail('page errors', errors.join(' | '));
  await browser.close();
  console.log(failed ? '\n' + failed + ' failure(s)' : '\nall passed (' + (CASES.length + STEP.length + trips.length + 1) + ' checks)');
  process.exit(failed ? 1 : 0);
})();
