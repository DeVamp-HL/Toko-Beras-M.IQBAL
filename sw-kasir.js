// Service worker kasir M.IQBAL — kasir kebuka instan & tetap jalan offline.
const VERSI = 'kasir-v3';
const FILES = ['kasir.html', 'manifest-kasir.json', 'icon-kasir-192.png', 'icon-kasir-512.png', 'icon-kasir-180.png', 'icon-kasir-32.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(VERSI).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSI).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  // Hanya tangani file kasir sendiri. Firestore, index.html, dan lainnya lewat jaringan biasa.
  if (url.origin !== location.origin) return;
  const nama = url.pathname.split('/').pop();
  if (!FILES.includes(nama)) return;
  if (nama === 'kasir.html') {
    // network-first: dapat versi terbaru kalau online, cache kalau offline
    e.respondWith(
      fetch(e.request).then((r) => {
        const salinan = r.clone();
        caches.open(VERSI).then((c) => c.put(e.request, salinan));
        return r;
      }).catch(() => caches.match(e.request))
    );
  } else {
    e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
  }
});
