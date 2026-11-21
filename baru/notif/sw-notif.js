// SERVICE WORKER NOTIFIKASI HP OWNER (owner 21 Nov 2026). Hanya menampilkan notifikasi push yang dikirim fungsi server (functions/index.js)
// dan membuka aplikasi saat diketuk. TIDAK menyimpan salinan halaman dan TIDAK membaca data toko — salinan aplikasi tablet tetap sw-baru.js.
// Lingkupnya sendiri (baru/notif/), jadi tidak berebut halaman dengan sw-baru.js. Dipasang hanya saat owner menekan "Nyalakan" di Menu ›
// Toko ini › Perangkat & antrean.
'use strict';

/** Isi pesan push FCM → { judul, isi, tag, layar }. Bentuk pesan DATA FCM: { data: {...}, from, fcmMessageId, ... }; pesan lain diterima apa adanya. */
function bacaPesan(teks) {
  let p = null; try { p = JSON.parse(teks); } catch (e) { p = null; }
  const d = (p && typeof p === 'object' && p.data && typeof p.data === 'object') ? p.data : (p && typeof p === 'object' ? p : {});
  const n = (p && p.notification) || {};
  return { judul: String(d.judul || n.title || 'Toko Beras M.IQBAL'), isi: String(d.isi || n.body || (p ? '' : String(teks || ''))), tag: String(d.tag || 'toko'), layar: String(d.layar || '') };
}

self.addEventListener('install', () => { self.skipWaiting(); });
self.addEventListener('activate', (e) => { e.waitUntil(self.clients.claim()); });

self.addEventListener('push', (e) => {
  // tiap push WAJIB menampilkan notifikasi (Safari mencabut izin push dari situs yang diam-diam menerima push)
  const m = bacaPesan(e.data ? e.data.text() : '');
  e.waitUntil(self.registration.showNotification(m.judul, { body: m.isi, tag: m.tag, renotify: true, icon: '../../icon-sistem-192.png', badge: '../../icon-sistem-192.png', data: { layar: m.layar } }));
});

self.addEventListener('notificationclick', (e) => {
  e.notification.close();
  const layar = (e.notification.data && e.notification.data.layar) || '';
  const tuju = new URL('../' + (layar ? '#' + encodeURIComponent(layar) : ''), self.registration.scope).href;
  e.waitUntil(self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((daftar) => {
    const ada = daftar.find((c) => c.url.indexOf(new URL('../', self.registration.scope).href) === 0);
    if (ada) { ada.postMessage({ jenis: 'buka-layar', layar }); return ada.focus(); }
    return self.clients.openWindow(tuju);
  }));
});
