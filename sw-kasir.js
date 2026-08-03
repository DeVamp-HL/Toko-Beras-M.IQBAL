// Service worker kasir M.IQBAL — kasir kebuka INSTAN di HP lemah & tetap jalan offline.
// v4 (4 Agustus 2026): strategi kasir.html diganti network-first -> CACHE DULU, perbarui
// di belakang layar (stale-while-revalidate). Alasan: di HP kentang + sinyal jelek,
// network-first membuat halaman menunggu jaringan gagal dulu baru buka — bisa belasan
// detik. Sekarang: buka langsung dari cache (<1 detik), versi baru diunduh diam-diam
// untuk pembukaan berikutnya. kasir-darurat-nominal.html ikut di-cache — katup darurat
// justru paling wajib bisa kebuka saat jaringan mati.
const VERSI = 'kasir-v4';
const FILES = ['kasir.html', 'kasir-darurat-nominal.html', 'manifest-kasir.json', 'icon-kasir-192.png', 'icon-kasir-512.png', 'icon-kasir-180.png', 'icon-kasir-32.png'];
const HTML_SWR = ['kasir.html', 'kasir-darurat-nominal.html'];

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
  if (HTML_SWR.includes(nama)) {
    // cache dulu (instan), lalu perbarui di belakang layar untuk buka berikutnya
    e.respondWith(
      caches.match(e.request).then((tersimpan) => {
        const dariJaringan = fetch(e.request).then((r) => {
          if (r && r.ok) {
            const salinan = r.clone();
            caches.open(VERSI).then((c) => c.put(e.request, salinan));
          }
          return r;
        }).catch(() => tersimpan);
        return tersimpan || dariJaringan;
      })
    );
  } else {
    e.respondWith(caches.match(e.request).then((r) => r || fetch(e.request)));
  }
});
