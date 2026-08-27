const CACHE_NAME = 'ddx-tools-v146';
const ASSETS = [
  './infographics/cerebral-venous-thrombosis/index.html',
  './infographics/cerebral-venous-thrombosis/infographic.png',
  './infographics/cerebral-venous-thrombosis/thumb.png',
  './slides/cerebral-venous-thrombosis/index.html',
  './slides/cerebral-venous-thrombosis/deck.html',
  './slides/cerebral-venous-thrombosis/slides.pdf',
  './slides/cerebral-venous-thrombosis/slide-01.png',
  './',
  './index.html',
  './periop_antithrombotic_consult.html',
  './antiepileptic_load_calculator.html',
  './vascular-territory-atlas.html',
  './aki.html',
  './edema.html',
  './edema_distribution.html',
  './hyponatremia.html',
  './hypernatremia.html',
  './hyperckemia.html',
  './hypokalemia.html',
  './highbun.html',
  './abdominal_pain.html',
  './bilateral_thalamus.html',
  './sensory_polyneuropathy.html',
  './abducens_palsy.html',
  './polyneuropathy_workup.html',
  './secondary_hypertension.html',
  './nerve_localization.html',
  './neurodiagnosis.html',
  './headache.html',
  './vertigo.html',
  './consciousness.html',
  './cceeg.html',
  './dyspnea.html',
  './chest_pain.html',
  './fuo.html',
  './hypercalcemia.html',
  './tremor.html',
  './levodopa_equivalent_calculator.html',
  './gait_ataxia.html',
  './liver_dysfunction.html',
  './anemia.html',
  './syncope.html',
  './vestibular_neuritis.html',
  './vestibular_migraine.html',
  './thyroid_dysfunction.html',
  './hemichorea.html',
  './cavernous_sinus.html',
  './stroke_reperfusion.html',
  './hypoactive_delirium.html',
  './dex_calculator.html',
  './nad_calculator.html',
  './ivig_calculator.html',
  './spikes_explainer.html',
  './news2_calculator.html',
  './bfcrs_calculator.html',
  './glim_nutrition.html',
  './infographics/abi-epilepsy/index.html',
  './infographics/acute-ich-bp/index.html',
  './infographics/acute-ischemic-stroke-bp/index.html',
  './infographics/alcohol-reduction-guidance/index.html',
  './infographics/allergic-rhinitis-guidance/index.html',
  './infographics/anemia-headache/index.html',
  './infographics/anxiety-lifestyle-guidance/index.html',
  './infographics/aspiration-prevention-guidance/index.html',
  './infographics/atrial-fibrillation-guidance/index.html',
  './infographics/beauty-infusion-evidence/index.html',
  './infographics/bilateral-leg-edema-guidance/index.html',
  './infographics/bpsd-family-care/index.html',
  './infographics/carpal-tunnel-b12/index.html',
  './infographics/carpal-tunnel-syndrome-guidance/index.html',
  './infographics/catatonia/index.html',
  './infographics/chronic-constipation-guidance/index.html',
  './infographics/chronic-dizziness-guidance/index.html',
  './infographics/ckd-lifestyle-guidance/index.html',
  './infographics/cns-sjogren/index.html',
  './infographics/common-cold-selfcare-guidance/index.html',
  './infographics/cpap-adherence-guidance/index.html',
  './infographics/deft-ai-clinical-reasoning/index.html',
  './infographics/dementia-14-risk-factors/index.html',
  './infographics/dementia-atherosclerosis/index.html',
  './infographics/dementia-vision-loss/index.html',
  './infographics/dementia-atrial-fibrillation/index.html',
  './infographics/dementia-sleep-apnea/index.html',
  './infographics/dementia-ckd/index.html',
  './infographics/dementia-multidomain-intervention/index.html',
  './handouts/dementia-multidomain-intervention/index.html',
  './slides/dementia-multidomain-intervention/index.html',
  './infographics/dementia-multiple-risk-factors/index.html',
  './handouts/dementia-multiple-risk-factors/index.html',
  './slides/dementia-multiple-risk-factors/index.html',
  './infographics/dementia-diabetes/index.html',
  './infographics/dementia-alcohol/index.html',
  './infographics/dementia-hearing-loss/index.html',
  './infographics/dementia-hypertension/index.html',
  './infographics/dementia-ldl-cholesterol/index.html',
  './infographics/dementia-obesity/index.html',
  './infographics/dementia-prevention-guidance/index.html',
  './infographics/dementia-smoking/index.html',
  './infographics/diabetes-2025-2026-impact/index.html',
  './infographics/diabetic-foot-care-guidance/index.html',
  './infographics/diabetic-tendon-pain/index.html',
  './infographics/dyslipidemia-lifestyle-guidance/index.html',
  './infographics/epilepsy-ai-eeg-reading/index.html',
  './infographics/epilepsy-ai-llm-support/index.html',
  './infographics/epilepsy-ai-neuroimaging/index.html',
  './infographics/epilepsy-ai-overview/index.html',
  './infographics/epilepsy-ai-surgery-drug-response/index.html',
  './infographics/epilepsy-lifestyle-guidance/index.html',
  './infographics/essential-tremor-guidance/index.html',
  './infographics/extracellular-fluid/index.html',
  './infographics/facial-palsy-rehab-guidance/index.html',
  './infographics/fall-prevention-guidance/index.html',
  './infographics/fatty-liver-masld-guidance/index.html',
  './infographics/flu-covid-home-care-guidance/index.html',
  './infographics/fukuri-no-chikara/index.html',
  './infographics/gerd-lifestyle-guidance/index.html',
  './infographics/glim-criteria/index.html',
  './infographics/health-anxiety-visits/index.html',
  './infographics/heart-failure-selfcare-guidance/index.html',
  './infographics/heatstroke-hydration-guidance/index.html',
  './infographics/hemianopia-vs-neglect/index.html',
  './infographics/high-cost-medical-expense/index.html',
  './infographics/how-to-stop-sleeping-pills/index.html',
  './infographics/hypertension-lifestyle-guidance/index.html',
  './infographics/hyperuricemia-gout-guidance/index.html',
  './infographics/icans/index.html',
  './infographics/index.html',
  './infographics/individual-jgb/index.html',
  './infographics/insomnia-nondrug-therapy/index.html',
  './infographics/internuclear-ophthalmoplegia/index.html',
  './infographics/iron-deficiency-anemia-guidance/index.html',
  './infographics/japan-healthcare-intl/index.html',
  './infographics/kampo-evidence-specific-2026/index.html',
  './infographics/kampo-evidence/index.html',
  './infographics/lake-marsh-pond-lagoon-differences/index.html',
  './infographics/lowering-cholesterol/index.html',
  './infographics/medical-expense-deduction/index.html',
  './infographics/migraine-selfcare-guidance/index.html',
  './infographics/minoxidil5-where-to-buy/index.html',
  './infographics/mollaret-meningitis/index.html',
  './infographics/mus-management/index.html',
  './infographics/neuro-breakthroughs-2025-2026/index.html',
  './infographics/ninchisho-koza-toketsu/index.html',
  './infographics/obesity-weight-loss-guidance/index.html',
  './infographics/orthostatic-hypotension-guidance/index.html',
  './infographics/osteoporosis/index.html',
  './infographics/overactive-bladder/index.html',
  './infographics/parkinson-best-on/index.html',
  './infographics/parkinson-brain-first-body-first/index.html',
  './infographics/parkinson-rehab-guidance/index.html',
  './infographics/peiof-chokin-hoken/index.html',
  './infographics/perioperative-watershed-infarction/index.html',
  './infographics/rls-lifestyle-guidance/index.html',
  './infographics/sciatica-leg-pain/index.html',
  './infographics/seinenkoken-kazokushintaku/index.html',
  './infographics/seizure-rescue-home/index.html',
  './infographics/sickness-allowance/index.html',
  './infographics/sinusitis/index.html',
  './infographics/smoking-cessation-guidance/index.html',
  './infographics/status-epilepticus-sedation/index.html',
  './infographics/statin-fibrate-tg-management/index.html',
  './infographics/stroke-secondary-prevention/index.html',
  './infographics/supplement-guide/index.html',
  './infographics/tension-headache-guidance/index.html',
  './infographics/tolosa_hunt.html',
  './infographics/typhoon-health-risks/index.html',
  './infographics/type2-diabetes-lifestyle-guidance/index.html',
  './infographics/what-is-happiness/index.html',
  './handouts/index.html',
  './handouts/stroke-secondary-prevention/index.html',
  './handouts/parkinson-rehab-guidance/index.html',
  './handouts/orthostatic-hypotension-guidance/index.html',
  './handouts/bpsd-family-care/index.html',
  './handouts/dementia-prevention-guidance/index.html',
  './handouts/hypertension-lifestyle-guidance/index.html',
  './handouts/chronic-dizziness-guidance/index.html',
  './handouts/type2-diabetes-lifestyle-guidance/index.html',
  './handouts/epilepsy-lifestyle-guidance/index.html',
  './handouts/dyslipidemia-lifestyle-guidance/index.html',
  './handouts/migraine-selfcare-guidance/index.html',
  './handouts/hyperuricemia-gout-guidance/index.html',
  './handouts/common-cold-selfcare-guidance/index.html',
  './handouts/carpal-tunnel-syndrome-guidance/index.html',
  './handouts/ckd-lifestyle-guidance/index.html',
  './handouts/rls-lifestyle-guidance/index.html',
  './handouts/anxiety-lifestyle-guidance/index.html',
  './handouts/gerd-lifestyle-guidance/index.html',
  './handouts/diabetic-foot-care-guidance/index.html',
  './handouts/chronic-constipation-guidance/index.html',
  './handouts/obesity-weight-loss-guidance/index.html',
  './handouts/allergic-rhinitis-guidance/index.html',
  './handouts/facial-palsy-rehab-guidance/index.html',
  './handouts/fatty-liver-masld-guidance/index.html',
  './handouts/flu-covid-home-care-guidance/index.html',
  './handouts/iron-deficiency-anemia-guidance/index.html',
  './handouts/essential-tremor-guidance/index.html',
  './handouts/smoking-cessation-guidance/index.html',
  './handouts/tension-headache-guidance/index.html',
  './handouts/bilateral-leg-edema-guidance/index.html',
  './handouts/osteoporosis/index.html',
  './handouts/overactive-bladder-frequency/index.html',
  './handouts/alcohol-reduction-guidance/index.html',
  './handouts/heatstroke-hydration-guidance/index.html',
  './handouts/cpap-adherence-guidance/index.html',
  './handouts/fall-prevention-guidance/index.html',
  './handouts/atrial-fibrillation-guidance/index.html',
  './handouts/how-to-stop-sleeping-pills/index.html',
  './handouts/aspiration-prevention-guidance/index.html',
  './handouts/heart-failure-selfcare-guidance/index.html',
  './handouts/dementia-hypertension/index.html',
  './handouts/dementia-hearing-loss/index.html',
  './handouts/dementia-ldl-cholesterol/index.html',
  './handouts/dementia-diabetes/index.html',
  './handouts/dementia-smoking/index.html',
  './handouts/dementia-obesity/index.html',
  './handouts/dementia-alcohol/index.html',
  './handouts/dementia-atherosclerosis/index.html',
  './handouts/dementia-vision-loss/index.html',
  './handouts/dementia-atrial-fibrillation/index.html',
  './handouts/dementia-sleep-apnea/index.html',
  './handouts/dementia-ckd/index.html',
  './status_epilepticus_sedation.html',
  './handouts/status-epilepticus-sedation/index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png'
];

// Install: cache all assets, skip waiting to activate immediately
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: clean ALL old caches, claim clients, notify for reload
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
     .then(() => self.clients.matchAll().then(cls => {
       cls.forEach(c => c.postMessage({ type: 'SW_UPDATED' }));
     }))
  );
});

// Fetch: network-first for HTML, cache-first for other assets
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  const isHTML = e.request.mode === 'navigate' ||
                 url.pathname.endsWith('.html') ||
                 url.pathname.endsWith('/');

  if (isHTML) {
    // Network-first for HTML pages
    e.respondWith(
      fetch(e.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
        }
        return response;
      }).catch(() => caches.match(e.request))
    );
  } else {
    // Cache-first for static assets (icons, manifest, etc.)
    e.respondWith(
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        return fetch(e.request).then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(e.request, clone));
          }
          return response;
        });
      })
    );
  }
});
