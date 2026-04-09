const CACHE_NAME = 'ddx-tools-v30';
const ASSETS = [
  './',
  './index.html',
  './aki.html',
  './edema.html',
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
  './gait_ataxia.html',
  './liver_dysfunction.html',
  './anemia.html',
  './syncope.html',
  './vestibular_neuritis.html',
  './thyroid_dysfunction.html',
  './hemichorea.html',
  './cavernous_sinus.html',
  './stroke_reperfusion.html',
  './hypoactive_delirium.html',
  './infographics/tolosa_hunt.html',
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
