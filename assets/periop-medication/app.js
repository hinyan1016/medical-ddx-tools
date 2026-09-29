/* 判定は純粋関数として実装し、画面と症例テストで同じ関数を使う。 */
(function (root) {
  'use strict';
  var DATA = PERIOP_DATA;
  var FIELDS = {
    eating: ['通常の食事・水分を十分摂取できる', 'yesno'],
    hydration: ['脱水がなく体液量が評価・管理されている', 'yesno'],
    kidney: ['腎機能が評価され、安定している', 'yesno'],
    ketoneSafe: ['ケトアシドーシスが否定されている', 'yesno'],
    bp: ['血圧・循環動態が安定している', 'yesno'],
    oxygen: ['低酸素・低灌流がない', 'yesno'],
    glucose: ['血糖を確認し、管理計画がある', 'yesno'],
    electrolytes: ['電解質が評価・管理されている', 'yesno'],
    giClear: ['悪心・嘔吐・腹痛・著明な便秘などがない', 'yesno'],
    escalation: ['GLP-1関連薬の開始・増量中', 'yesno'],
    gastric: ['胃排出遅延を伴う病態がある', 'yesno'],
    highDose: ['GLP-1関連薬は高用量（処方医の評価）', 'yesno'],
    pulse: ['脈拍が評価され、徐脈等の問題がない', 'yesno'],
    betaPlan: ['β遮断薬の国内添文と臨床状態を踏まえた管理指示がある', 'yesno'],
    route: ['定時投与を確保する経路・吸収を確認した', 'yesno'],
    interaction: ['麻酔・鎮痛・制吐薬等との相互作用を確認した', 'yesno'],
    mobility: ['完全に歩行可能で長期安静状態ではない', 'yesno'],
    immobilization: ['長期不動・長期安静の予定がある', 'yesno'],
    immobileStart: ['長期不動・長期安静の開始日時', 'datetime-local'],
    contrast: ['ヨード造影剤の使用予定／使用がある', 'yesno'],
    contrastTime: ['ヨード造影剤の使用日時（術後評価時）', 'datetime-local'],
    egfr: ['直近のeGFR（mL/min/1.73m²）', 'number'],
    cvRisk: ['非心臓手術の心血管リスク評価', 'risk'],
    diabetesType: ['糖尿病の型', 'diabetes'],
    dosingPlan: ['担当医による投与量・投与経路の計画がある', 'yesno']
  };
  function unique(xs) { return xs.filter(function (v, i, a) { return a.indexOf(v) === i; }); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
  function stamp(s) {
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(s || '')) return null;
    var n = Date.parse(s + ':00+09:00');
    if (!isFinite(n) || iso(n) !== s) return null;
    return n;
  }
  function iso(n) { return new Date(n + 9 * 3600000).toISOString().slice(0,16); }
  function fmt(n) { return iso(n).replace('T', ' '); }
  function midnight(s) { return stamp(s.slice(0,10) + 'T00:00'); }
  function byId(id) { return DATA.drugs.filter(function (d) { return d.id === id; })[0]; }
  function norm(s) {
    s = String(s || '');
    if (s.normalize) s = s.normalize('NFKC');
    return s.toLowerCase().replace(/[\s・\-‐]/g, '').replace(/[ぁ-ゖ]/g, function (c) { return String.fromCharCode(c.charCodeAt(0) + 96); });
  }
  function search(q) {
    var raw = String(q || '');
    if (raw.normalize) raw = raw.normalize('NFKC');
    var cleaned = raw.replace(/\d+(?:\.\d+)?\s*(?:mg|mcg|μg|µg|ml|単位)/gi,'').replace(/配合錠|OD錠|錠|カプセル|配合/gi,'').trim();
    if (raw.trim() && !cleaned) return [];
    var parts = cleaned.split(/\s+/).map(norm);
    return DATA.drugs.filter(function (d) {
      var text = norm([d.name, d.category].concat(d.aliases).join(' '));
      return parts.every(function (p) { return text.indexOf(p) >= 0; });
    });
  }
  function fieldsFor(drugs, mode) {
    var ids = [];
    drugs.forEach(function (d) {
      var base = byId(d.id);
      (base ? base.components : ['consult']).forEach(function (k) {
        if (mode === 'post') ids = ids.concat(DATA.rules[k].conditions);
        if (k === 'sglt2') ids = ids.concat(['eating','hydration','kidney','ketoneSafe']);
        if (k === 'metformin') ids = ids.concat(['kidney','egfr','hydration','bp','oxygen','contrast','contrastTime']);
        if (k === 'glp') ids = ids.concat(['giClear','escalation','gastric','highDose']);
        if (k === 'raas') ids = ids.concat(['cvRisk','bp','kidney','electrolytes']);
        if (k === 'arni' || k === 'diuretic' || k === 'lithium') ids = ids.concat(['bp','hydration','kidney','electrolytes']);
        if (k === 'insulin' || k === 'steroid') ids.push('dosingPlan');
        if (k === 'insulin') ids.push('diabetesType');
        if (k === 'beta') ids = ids.concat(['bp','pulse','betaPlan']);
        if (k === 'ccb') ids.push('bp');
        if (k === 'maob') ids.push('interaction');
        if (k === 'aed' || k === 'levodopa') ids.push('route');
        if (k === 'ralox') ids = ids.concat(['immobilization','immobileStart']);
        if (k === 'hormone' || k === 'oc') ids.push('immobilization');
      });
    });
    return unique(ids);
  }
  function evaluate(input, now) {
    var g = input.global || {}, f = input.facts || {}, mode = input.mode || 'pre';
    var op = stamp(g.surgery), at = stamp(g.assessed), errors = [], notices = [];
    var stale = iso(now == null ? Date.now() : now).slice(0,10) > DATA.review_due;
    if (['pre','missed','post'].indexOf(mode) < 0) errors.push('確認する場面が不正です。');
    if (g.scope !== 'adult') errors.push('対象範囲外または対象不明です。成人・非心臓手術に限って参考情報を整理しています。');
    if (!g.urgency) errors.push('手術の緊急性が未確認です。');
    if (at === null) errors.push('評価日時を正しく入力してください。');
    if (op === null && g.urgency !== 'emergency') errors.push('手術日時を正しく入力してください。');
    if (at !== null && op !== null && ((mode === 'post' && op > at) || (mode !== 'post' && op < at))) errors.push('手術日時と確認する場面が一致しません。術後は「術後の再開」を選択してください。');
    if (g.fastingStart && stamp(g.fastingStart) === null) errors.push('絶食開始日時が不正です。');
    if (g.fastingStart && op !== null && stamp(g.fastingStart) > op) errors.push('絶食開始日時が手術日時より後です。');
    if (stale) errors.push('根拠の再確認期限を過ぎています。休薬予定の自動計算を停止しました。最新資料で確認してください。');
    if (op !== null && g.surgery.slice(0,10)>DATA.review_due) notices.push('手術予定日が根拠の再確認期限より後です。実施前に最新資料で管理計画を見直してください。');
    if (g.urgency === 'emergency') notices.push('緊急・準緊急手術：待機手術の休薬期間を満たすために自動延期せず、麻酔科・術者・処方医で即時協議してください。');
    if (mode === 'missed') notices.push('誤休薬・休薬忘れは薬剤ごとに対応が異なります。症状・バイタルに問題があれば薬剤確認と並行して診療を優先してください。');
    var seen = {}, items = [];
    (input.drugs || []).forEach(function (d) {
      var base = byId(d.id) || {name:d.name || '未収載薬',components:['consult'],form:'未確認',identity_sources:[]};
      base.components.forEach(function (key) {
        var r = DATA.rules[key], last = stamp(d.last), missing = [], issues = [], schedule = null;
        var status = '個別協議', level = 'review', pre = r.pre, restart = r.restart, required = [];
        if (!g.procedure) missing.push('手術の規模');
        if (!g.anesthesia) missing.push('麻酔・鎮静');
        if (!g.fasting) missing.push('飲食制限・絶食');
        if (mode === 'missed' && !d.state) missing.push('実際の服用・中止状況');
        if (mode === 'missed' && last === null) missing.push('最終投与日時');
        if (d.last && last === null) issues.push('最終投与日時が不正です。');
        if (last !== null && at !== null && last > at) issues.push('「実際の最終投与」が評価日時より未来です。予定日時はここに入力しないでください。');
        function need(keys) { required = required.concat(keys.split(' ')); }
        function calendar(days, anchor, basis) {
          if (anchor !== null) schedule = {cutoff:anchor - days * 86400000,basis:basis,unit:'calendar',text:'この日から服用しない計画を処方医と確認'};
        }
        function hours(n, basis) { if (op !== null) schedule = {cutoff:op - n * 3600000,basis:basis,unit:'hours',text:'この時刻以降の投与を省略する計画を協議'}; }
        if (key === 'sglt2') {
          need('hydration kidney ketoneSafe');
          status = '休薬計画を確認'; calendar(3, op === null ? null : midnight(g.surgery), '国内学会：手術の3暦日前から休薬');
          if (f.ketoneSafe === 'no') { issues.push('ケトアシドーシスが否定されていません。血糖だけで除外せず担当医へ速やかに相談。'); level='alert'; }
        }
        if (key === 'metformin') {
          need('kidney egfr hydration bp oxygen contrast');
          if (f.egfr !== '' && f.egfr != null && (!isFinite(Number(f.egfr)) || Number(f.egfr) <= 0 || Number(f.egfr) > 200)) issues.push('eGFRの入力範囲を確認してください。');
          if (f.egfr !== '' && f.egfr != null && Number(f.egfr) < 30) {issues.push('eGFR 30未満：国内の禁忌に該当します。周術期に限らず処方医へ確認。');level='alert';}
          if (g.procedure === 'minor' && g.fasting === 'no') status='小手術の条件を個別確認';
          else status='休薬・血糖管理を相談';
          if (f.contrast === 'yes') {
            restart += ' ヨード造影剤使用時は、少なくとも使用後48時間の再開制限と腎機能の再評価を製品添文で確認する。';
            if (mode === 'post') {
              need('contrastTime');
              var ct=stamp(f.contrastTime);
              if (ct === null && f.contrastTime) issues.push('造影剤の使用日時が不正です。');
              if (ct !== null && at !== null && ct > at) issues.push('造影剤の使用日時が評価日時より未来です。');
              else if (ct !== null && at !== null && at-ct < 48*3600000) issues.push('造影剤使用後48時間に達していません。再開を処方医へ確認。');
            }
          }
        }
        if (key === 'su') {
          status='当日投与の省略を相談'; calendar(0,op === null ? null : midnight(g.surgery),'英国資料：グリメピリドの手術当日投与を省略');
          var fast=stamp(g.fastingStart);
          if (schedule && fast !== null && fast < schedule.cutoff) {schedule=null;issues.push('手術前日以前からの絶食：通常の当日省略だけでは対応できないため、絶食開始時からの指示を確認。');}
        }
        if (key === 'glp') {
          need('giClear escalation gastric highDose');
          if (f.giClear === 'no' || f.escalation === 'yes' || f.gastric === 'yes' || f.highDose === 'yes') {status='誤嚥リスクを麻酔科と評価';level='alert';issues.push('消化器症状・開始増量期・胃排出遅延・高用量のいずれかに該当。休薬日数だけで安全確認としない。');}
          else if (f.giClear === 'yes' && f.escalation === 'no' && f.gastric === 'no' && f.highDose === 'no') status='継続を含め麻酔科と相談';
          if (g.anesthesia === 'local' || g.anesthesia === 'regional') pre += ' 深い鎮静の追加・全身麻酔への変更の可能性も共有する。';
        }
        if (key === 'raas') {
          if (!d.indication) missing.push('ACE阻害薬・ARBの使用目的');
          need('bp kidney electrolytes');
          if (d.indication === 'hfrEF') {status='HFrEF：継続を検討';pre='HFrEFに対する継続治療は周術期も継続が合理的とする米国推奨。低血圧・腎機能悪化等があれば循環器・麻酔科で調整する。';}
          else if (d.indication === 'htn') {
            need('cvRisk');
            if (f.cvRisk === 'elevated' && f.bp === 'yes') {status='24時間前省略を検討';hours(24,'米国GL：血圧管理良好・高血圧目的・心血管リスクの高い非心臓手術');}
          }
        }
        if (['arni','diuretic','lithium'].indexOf(key)>=0) need('bp kidney hydration electrolytes');
        if (key === 'lithium') {
          if (g.procedure==='minor') status='小手術：継続を相談';
          if (g.procedure==='major') {status='大手術：休薬を相談';hours(24,'英国資料：大手術では24時間前中止（国内施設の方針を確認）');}
        }
        if (key === 'beta') {need('bp pulse betaPlan');status='国内添文・海外推奨を照合';}
        if (key === 'ccb') {need('bp');status='継続を確認';}
        if (key === 'steroid' || key === 'insulin') {need('dosingPlan');status='投与量・経路の計画を確認';}
        if (key === 'insulin') {need('diabetesType'); if (f.diabetesType==='type1') issues.push('1型糖尿病：基礎インスリンが途切れない計画を糖尿病担当医に確認。');}
        if (key === 'maob') need('interaction');
        if (key === 'aed' || key === 'levodopa') {need('route');status='定時投与・代替経路を確認';}
        if (key === 'oc') {
          status='添付文書の禁忌期間を確認'; calendar(28,op===null?null:midnight(g.surgery),'ヤーズ収載添付文書：手術前4週以内の禁忌');
          if (schedule) schedule.text='手術の28暦日前から服用しない計画を、禁忌期間に入る前に処方医と確認';
          if (mode==='post' && op!==null && at!==null && at-op<=14*86400000) issues.push('術後2週以内の禁忌期間です。日数と離床状況を婦人科へ確認。');
        }
        if (key === 'ralox') {
          need('immobilization');
          if (f.immobilization==='yes') {
            need('immobileStart'); var im=stamp(f.immobileStart);
            if (f.immobileStart && im===null) issues.push('長期不動の開始日時が不正です。');
            calendar(3,im===null?null:midnight(f.immobileStart),'長期不動に入る3暦日前から休薬');status='長期不動前の休薬を確認';
          }
        }
        if (mode === 'post') {
          schedule=null; required=required.concat(r.conditions);
          if (key!=='consult') status='再開条件を確認';
        }
        unique(required).forEach(function (k) {
          if (f[k] === '' || f[k] == null) missing.push(FIELDS[k][0]);
          else if (['egfr','contrast','contrastTime','escalation','gastric','highDose','immobilization','immobileStart','cvRisk','diabetesType'].indexOf(k)<0 && f[k]==='no') issues.push('条件未充足：'+FIELDS[k][0]);
        });
        if (r.critical && ((mode==='missed' && (d.state==='held' || d.state==='missed')) || f.route==='no' || ((key==='steroid'||key==='insulin') && f.dosingPlan==='no'))) {
          status='投与中断・代替経路を優先相談';level='alert';issues.push('通常食の再開を待たず、必要な治療を確保する方法を担当医に確認してください。');
        }
        if (key==='consult') {status='未収載：薬剤別確認';missing.push('薬剤固有の一次資料・管理指示');}
        if (missing.length) {if (level!=='alert') status='情報不足：追加確認';schedule=null;}
        if (issues.length) {level='alert';schedule=null;if (!r.critical) status='問題・未充足条件を確認';}
        if (errors.length) {status='入力・対象の確認が必要';level='alert';schedule=null;}
        if (g.urgency==='emergency') {status='緊急：担当科と即時協議';level='alert';schedule=null;pre='待機手術の休薬日数をそのまま当てはめず、最終投与と患者状態を共有して、麻酔科・術者・処方医で対応を決定する。';}
        if (schedule && last!==null && last>=schedule.cutoff) {
          issues.push('実際の最終投与が休薬開始の目安以降です。休薬忘れ／期間不足の可能性を担当科へ共有。');status='休薬期間の不足を確認';level='alert';
        }
        if (schedule && at!==null && schedule.cutoff<at && last===null) {
          missing.push('休薬開始の目安を過ぎているため、実際の最終投与日時');status='最終投与の確認が必要';
        }
        if (mode==='post' && !missing.length && !issues.length && !errors.length && key!=='consult' && g.urgency!=='emergency') status='入力条件を満たす：担当医が再開を判断';
        if (r.critical && mode==='post' && status==='入力条件を満たす：担当医が再開を判断') status='担当医と継続・投与経路を確認';
        if (!missing.length && !issues.length && !errors.length && /継続を確認|定時投与/.test(status)) level='normal';
        var componentKey = key;
        if (seen[componentKey] && seen[componentKey]!==d.id) notices.push(r.name+'を含む項目が複数あります。重複処方・同一薬の二重登録と配合成分を照合してください。');
        seen[componentKey]=d.id;
        items.push({drugId:d.id,name:base.name,entered:d.entered || d.name || '',form:base.form,dose:d.dose||'',last:d.last||'',state:d.state||'',indication:d.indication||'',rule:key,ruleName:r.name,status:status,level:level,pre:pre,missed:r.missed,restart:restart,kind:r.kind,schedule:schedule,missing:unique(missing),issues:unique(issues),conditions:r.conditions,sources:unique(r.sources.concat(base.identity_sources||[]))});
      });
    });
    return {mode:mode,global:g,facts:f,errors:unique(errors),notices:unique(notices),items:items,version:DATA.version,checked:DATA.checked};
  }
  function handoff(result) {
    var g=result.global, lines=['【周術期薬剤確認・医療者確認用／処方指示ではありません】','場面：'+({pre:'術前',missed:'休薬忘れ・誤休薬',post:'術後再開'}[result.mode]),'手術日時：'+(g.surgery||'不明')+'（日本時間）／評価日時：'+(g.assessed||'不明'),'対象：'+(g.scope==='adult'?'成人・非心臓手術':'対象外／不明')+'／緊急性：'+(g.urgency==='elective'?'待機':g.urgency==='emergency'?'緊急・準緊急':'不明'),'根拠確認：'+DATA.checked+'／ツール版：'+DATA.version];
    lines=lines.concat(result.errors.map(function (x){return '要確認：'+x;}),result.notices);
    result.items.forEach(function (r) {
      lines.push('\n■ '+r.name+'［'+r.ruleName+'］：'+r.status);
      lines.push('製剤：'+r.form+'／入力した薬名：'+(r.entered||'なし')+'／用量・間隔：'+(r.dose||'未入力')+'／最終投与：'+(r.last||'不明'));
      if(r.indication) lines.push('使用目的：'+valueLabel(r.indication));
      if(r.state) lines.push('実際の状況：'+valueLabel(r.state));
      if(r.schedule) lines.push('休薬開始目安：'+fmt(r.schedule.cutoff)+'（日本時間）。'+r.schedule.basis+'。'+r.schedule.text);
      lines.push(result.mode==='post'?r.restart:result.mode==='missed'?r.missed:r.pre);
      if(result.mode!=='post') lines.push('術後：'+r.restart);
      if(r.missing.length) lines.push('不足：'+r.missing.join('／'));
      r.issues.forEach(function(x){lines.push('要確認：'+x);});
      lines.push('根拠区分：'+r.kind);
      r.sources.forEach(function(k){var s=DATA.sources[k];lines.push('出典：'+s.title+' '+s.url+' ['+s.source_locator+']');});
    });
    lines.push('\n【入力条件】');
    ['procedure','anesthesia','fasting','fastingStart'].forEach(function(k){lines.push(({procedure:'手術規模',anesthesia:'麻酔',fasting:'飲食制限',fastingStart:'絶食開始'})[k]+': '+valueLabel(g[k]));});
    fieldsFor((result.items.map(function(x){return {id:x.drugId};})),result.mode).forEach(function(k){lines.push(FIELDS[k][0]+': '+valueLabel(result.facts[k]));});
    lines.push('\n最終的な休薬・代替投与・再開の指示と確認者は診療記録に記載してください。');
    return lines.join('\n');
  }
  function valueLabel(v){return {'yes':'はい','no':'いいえ','minor':'小手術','major':'大手術','general':'全身麻酔／深い鎮静','regional':'区域麻酔（深い鎮静なし）','local':'局所麻酔（深い鎮静なし）','elevated':'心血管リスクが高い','low':'心血管リスクが低い','type1':'1型糖尿病','type2':'2型糖尿病','other':'その他','htn':'高血圧','hfrEF':'HFrEF','taken':'服用・投与した','held':'休薬した','missed':'投与し忘れた'}[v] || v || '不明';}
  root.PeriopEngine = {evaluate:evaluate,handoff:handoff,search:search,stamp:stamp,iso:iso,fieldsFor:fieldsFor,data:DATA};
  if (typeof document==='undefined') return;
  var state={mode:'pre',drugs:[],facts:{},result:null};
  function el(id){return document.getElementById(id);}
  function options(kind,value){
    var opts=[['','不明・未確認']];
    if(kind==='yesno')opts=opts.concat([['yes','はい'],['no','いいえ']]);
    if(kind==='risk')opts=opts.concat([['elevated','心血管リスクが高い'],['low','心血管リスクが低い']]);
    if(kind==='diabetes')opts=opts.concat([['type1','1型糖尿病'],['type2','2型糖尿病'],['other','その他']]);
    return opts.map(function(o){return '<option value="'+o[0]+'"'+(value===o[0]?' selected':'')+'>'+o[1]+'</option>';}).join('');
  }
  function invalidate(){state.result=null;el('results').innerHTML='';el('status').textContent='入力を変更しました。確認結果を作成してください。';}
  function renderSearch(all){
    var q=el('search').value.trim(), found=search(q);
    if(!q&&!all){el('searchResults').innerHTML='';el('searchCount').textContent='';return;}
    el('searchCount').textContent=found.length+'件の収載項目（分類の項目も含みます）';
    var html=found.map(function(d){var selected=state.drugs.some(function(x){return x.id===d.id;});return '<button type="button" class="drug-choice" data-add="'+d.id+'"'+(selected?' disabled':'')+'><span>'+esc(d.name)+'<small>'+esc(d.aliases.join(' / '))+'</small></span><span>'+ (selected?'追加済み':'＋')+'</span></button>';}).join('');
    if(q) html+='<button type="button" class="drug-choice" data-unknown="1"><span>「'+esc(q)+'」を未収載薬として追加<small>一致する製品・分類がない場合。薬剤別確認として残します。</small></span><span>＋</span></button>';
    el('searchResults').innerHTML=html;
  }
  function renderSelected(){
    el('selectedCount').textContent=state.drugs.length;
    el('selected').innerHTML=state.drugs.length?state.drugs.map(function(d,i){
      var b=byId(d.id)||{name:d.name,components:['consult'],form:'未確認'};
      var h='<article class="selected-card"><div class="row"><div><h3>'+esc(b.name)+'</h3><span class="small">'+esc(b.form)+(d.entered?' / 検索時の入力：'+esc(d.entered):'')+'</span></div><button type="button" data-remove="'+i+'" aria-label="'+esc(b.name)+'を削除">削除</button></div>';
      h+=b.components.map(function(k){return '<span class="tag">'+esc(DATA.rules[k].name)+'</span>';}).join('');
      if(b.components.length>1)h+='<p class="small">配合剤全体の指示が必要です。成分だけを休薬する場合は、別製剤への変更を処方医と相談してください。</p>';
      h+='<div class="grid"><div class="field"><label for="dose-'+i+'">製品・用量・投与間隔（記録用）</label><input id="dose-'+i+'" data-i="'+i+'" data-prop="dose" maxlength="160" value="'+esc(d.dose)+'" placeholder="例：5 mg、1日1回 朝"><small>自動用量計算には使いません。分類項目は実際の製品名も記載。</small></div>';
      h+='<div class="field"><label for="last-'+i+'">実際の最終服用・注射日時</label><input type="datetime-local" id="last-'+i+'" data-i="'+i+'" data-prop="last" value="'+esc(d.last)+'"><small>予定ではなく投与済みの日時。空欄＝不明。</small></div>';
      if(state.mode==='missed')h+='<div class="field"><label for="state-'+i+'">実際の状況</label><select id="state-'+i+'" data-i="'+i+'" data-prop="state"><option value="">不明・未確認</option><option value="taken"'+(d.state==='taken'?' selected':'')+'>服用・投与した</option><option value="held"'+(d.state==='held'?' selected':'')+'>休薬した</option><option value="missed"'+(d.state==='missed'?' selected':'')+'>投与し忘れた・遅れた</option></select></div>';
      if(b.components.indexOf('raas')>=0)h+='<div class="field full"><label for="indication-'+i+'">ACE阻害薬・ARBの使用目的</label><select id="indication-'+i+'" data-i="'+i+'" data-prop="indication">'+[['','不明・未確認'],['htn','高血圧（HFrEFを伴わない）'],['hfrEF','駆出率の低下した心不全（HFrEF）'],['other','その他・複数の適応で判断が必要']].map(function(o){return '<option value="'+o[0]+'"'+(d.indication===o[0]?' selected':'')+'>'+o[1]+'</option>';}).join('')+'</select></div>';
      return h+'</div></article>';
    }).join(''):'<p class="empty">確認する薬剤を検索して追加してください。</p>';
  }
  function renderConditions(){
    var keys=fieldsFor(state.drugs,state.mode);
    el('conditions').innerHTML=keys.length?keys.map(function(k){
      var f=FIELDS[k],v=state.facts[k]||'',h='<div class="field"><label for="fact-'+k+'">'+esc(f[0])+'</label>';
      if(f[1]==='number'||f[1]==='datetime-local')h+='<input id="fact-'+k+'" data-fact="'+k+'" type="'+f[1]+'" value="'+esc(v)+'"'+(f[1]==='number'?' min="1" max="200" step="0.1"':'')+'>';
      else h+='<select id="fact-'+k+'" data-fact="'+k+'">'+options(f[1],v)+'</select>';
      if(k==='contrastTime')h+='<small>造影あり・術後評価時のみ必要。</small>';
      if(k==='immobileStart')h+='<small>長期不動ありの場合のみ必要。手術日時と異なる場合は実際の開始予定を入力。</small>';
      return h+'</div>';
    }).join(''):'<p class="small">薬剤を追加すると、必要な確認項目が表示されます。</p>';
  }
  function sourceHtml(keys){return '<ul class="source-list">'+keys.map(function(k){var s=DATA.sources[k];return '<li><a href="'+esc(s.url)+'" target="_blank" rel="noopener">'+esc(s.title)+' ↗</a><small>'+esc(s.kind)+'／'+esc(s.version)+'／確認 '+s.checked+'</small><small>該当箇所：'+esc(s.source_locator)+'</small>'+(s.note?'<small>'+esc(s.note)+'</small>':'')+'</li>';}).join('')+'</ul>';}
  function collect(){var g={};['scope','urgency','surgery','assessed','procedure','anesthesia','fasting','fastingStart'].forEach(function(k){g[k]=el(k).value;});return {mode:state.mode,drugs:state.drugs,global:g,facts:state.facts};}
  function list(xs,css){return xs.length?'<ul'+(css?' class="'+css+'"':'')+'>'+xs.map(function(x){return '<li>'+esc(x)+'</li>';}).join('')+'</ul>':'';}
  function renderResult(r){
    var h='<div class="result-head"><div><div class="eyebrow">REVIEW SUMMARY</div><h2>薬剤ごとの確認結果</h2><p class="small">'+esc(r.global.surgery||'手術日時不明')+'／'+({pre:'術前の準備',missed:'休薬忘れ・誤休薬',post:'術後の再開'}[r.mode])+'／日本時間</p></div><div class="actions"><button type="button" id="print">確認表を印刷</button><button type="button" id="copy">申し送りをコピー</button></div></div>';
    h+='<p class="print-only">医療者確認用。処方指示・手術実施許可ではありません。確認 '+DATA.checked+'／版 '+DATA.version+'</p>';
    if(r.errors.length) h+='<div class="alert-box"><strong>入力・対象を確認してください</strong>'+list(r.errors)+'</div>';
    if(r.notices.length)h+='<div class="notice">'+list(r.notices)+'</div>';
    var contextLines=['対象：'+(r.global.scope==='adult'?'成人・非心臓手術':'対象外／不明'),'緊急性：'+(r.global.urgency==='elective'?'待機':r.global.urgency==='emergency'?'緊急・準緊急':'不明'),'評価日時：'+(r.global.assessed||'不明')+'（日本時間）'];
    ['procedure','anesthesia','fasting','fastingStart'].forEach(function(k){contextLines.push(({procedure:'手術規模',anesthesia:'麻酔',fasting:'飲食制限',fastingStart:'絶食開始'})[k]+'：'+valueLabel(r.global[k]));});
    fieldsFor(state.drugs,r.mode).forEach(function(k){contextLines.push(FIELDS[k][0]+'：'+valueLabel(r.facts[k]));});
    h+='<details class="panel"><summary>評価に使用した入力条件（印刷にも含みます）</summary>'+list(contextLines)+'</details>';
    h+='<div class="table-scroll"><table class="summary-table"><thead><tr><th>薬剤</th><th>確認結果</th><th>休薬開始の目安</th></tr></thead><tbody>'+r.items.map(function(x){return '<tr><td>'+esc(x.name)+'<br><span class="small">'+esc(x.ruleName)+'</span></td><td>'+esc(x.status)+'</td><td>'+(x.schedule?esc(fmt(x.schedule.cutoff))+'<br>'+esc(x.schedule.basis):'日付を自動決定しない')+'</td></tr>';}).join('')+'</tbody></table></div>';
    r.items.forEach(function(x){
      h+='<article class="result-card '+x.level+'"><div class="result-title"><span class="badge">'+esc(x.status)+'</span><h3>'+esc(x.name)+'</h3><p class="small">'+esc(x.ruleName)+'／'+esc(x.kind)+'</p></div><p class="small">製剤：'+esc(x.form)+'／用量・間隔：'+esc(x.dose||'未入力')+'／最終投与：'+esc(x.last||'不明')+'</p>';
      if(x.entered)h+='<p class="small">入力した薬名：'+esc(x.entered)+'</p>';
      if(x.indication)h+='<p class="small">使用目的：'+esc(valueLabel(x.indication))+'</p>';
      if(x.state)h+='<p class="small">実際の状況：'+esc(valueLabel(x.state))+'</p>';
      if(x.schedule)h+='<div class="schedule"><strong>休薬開始目安：'+esc(fmt(x.schedule.cutoff))+'（日本時間）</strong><br>'+esc(x.schedule.text)+'<br><small>'+esc(x.schedule.basis)+'。最終服用予定は処方時刻・投与間隔を確認して決めます。</small></div>';
      if(x.missing.length)h+='<div class="missing"><strong>追加で必要な情報</strong>'+list(x.missing)+'</div>';
      if(x.issues.length)h+='<div class="alert-box">'+list(x.issues)+'</div>';
      if(r.mode!=='post')h+='<h4>'+ (r.global.urgency==='emergency'?'緊急時の確認':'術前の考え方')+'</h4><p>'+esc(x.pre)+'</p>';
      if(r.mode==='missed'||r.global.urgency==='emergency')h+='<h4>服用・休薬状況への対応</h4><p>'+esc(x.missed)+'</p>';
      h+='<h4>術後・再開時に確認すること</h4><p>'+esc(x.restart)+'</p>';
      if(r.mode==='post' && x.conditions.length)h+=list(x.conditions.map(function(k){return FIELDS[k][0]+'：'+valueLabel(r.facts[k]);}));
      h+='<details><summary>この結果の根拠・該当箇所</summary>'+(x.sources.length?sourceHtml(x.sources):'<p>薬剤別の根拠は未収載です。製品の電子添文と専門科の指示を確認してください。</p>')+'</details></article>';
    });
    h+='<section class="panel" id="handoffPanel"><h2>申し送り文</h2><p class="sub">入力条件・未確定事項・出典を含みます。処方指示に転用する前に担当医が確認してください。</p><label class="small" for="handoff">コピー用テキスト</label><textarea readonly id="handoff">'+esc(handoff(r))+'</textarea></section>';
    el('results').innerHTML=h;
    el('print').onclick=function(){document.querySelectorAll('#results details').forEach(function(d){d.open=true;});window.print();};
    el('copy').onclick=function(){var t=el('handoff');function fallback(){t.focus();t.select();var ok=false;try{ok=document.execCommand('copy');}catch(e){}el('status').textContent=ok?'申し送り文をコピーしました。':'テキストを選択しました。コピー操作で保存してください。';}if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t.value).then(function(){el('status').textContent='申し送り文をコピーしました。';},fallback);else fallback();};
  }
  function sync(){renderSelected();renderConditions();renderSearch(false);}
  el('assessed').value=iso(Date.now());
  document.querySelectorAll('[data-mode]').forEach(function(b){b.onclick=function(){state.mode=b.getAttribute('data-mode');document.querySelectorAll('[data-mode]').forEach(function(x){x.setAttribute('aria-pressed',String(x===b));});el('modeDescription').textContent={pre:'術前の休薬・継続について、根拠と必要な条件を整理します。',missed:'実際の服用・中止状況を確認し、追加評価と相談事項を整理します。',post:'日付だけで再開を決めず、必要な全身状態と投与経路を確認します。'}[state.mode];invalidate();sync();};});
  el('search').oninput=function(){renderSearch(false);};
  el('showAll').onclick=function(){el('search').value='';renderSearch(true);};
  el('searchResults').onclick=function(e){var b=e.target.closest('button');if(!b)return;var id=b.getAttribute('data-add'),q=el('search').value.trim();if(id && !state.drugs.some(function(x){return x.id===id;}))state.drugs.push({id:id,entered:q,dose:'',last:'',state:'',indication:''});else if(b.hasAttribute('data-unknown')&&q)state.drugs.push({id:'unknown-'+Date.now()+'-'+state.drugs.length,name:q,entered:q,dose:'',last:'',state:''});else return;invalidate();sync();};
  el('selected').onclick=function(e){var b=e.target.closest('[data-remove]');if(!b)return;state.drugs.splice(Number(b.getAttribute('data-remove')),1);invalidate();sync();};
  el('selected').addEventListener('input',function(e){var i=e.target.getAttribute('data-i'),p=e.target.getAttribute('data-prop');if(i!==null&&p){state.drugs[Number(i)][p]=e.target.value;invalidate();}});
  el('conditions').addEventListener('input',function(e){var k=e.target.getAttribute('data-fact');if(k){state.facts[k]=e.target.value;invalidate();}});
  ['scope','urgency','surgery','assessed','procedure','anesthesia','fasting','fastingStart'].forEach(function(k){el(k).addEventListener('input',invalidate);});
  el('evaluate').onclick=function(){if(!state.drugs.length){el('status').textContent='薬剤を1件以上追加してください。';el('search').focus();return;}state.result=evaluate(collect());renderResult(state.result);el('status').textContent='確認結果を作成しました。不足情報と根拠を確認してください。';el('results').scrollIntoView({behavior:'smooth',block:'start'});};
  el('reset').onclick=function(){if(!window.confirm('入力と確認結果をすべて消去しますか？'))return;state.drugs=[];state.facts={};['surgery','procedure','anesthesia','fasting','fastingStart','urgency'].forEach(function(k){el(k).value='';});el('scope').value='adult';el('assessed').value=iso(Date.now());el('search').value='';invalidate();sync();el('status').textContent='入力をリセットしました。';};
  el('versionNote').textContent='版 '+DATA.version+'／根拠確認 '+DATA.checked+'／再確認期限 '+DATA.review_due;
  el('allSources').innerHTML='<p>'+esc(DATA.scope)+'</p>'+list(DATA.evidence_limitations)+sourceHtml(Object.keys(DATA.sources));
  window.addEventListener('beforeprint',function(){document.querySelectorAll('#results details').forEach(function(d){d.open=true;});});
  if(iso(Date.now()).slice(0,10)>DATA.review_due)el('freshness').innerHTML='<div class="alert-box">根拠の再確認期限を過ぎています。自動の日付計算を停止しています。</div>';
  sync();
})(typeof window!=='undefined'?window:globalThis);
