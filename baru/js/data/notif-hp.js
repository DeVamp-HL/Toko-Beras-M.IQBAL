// NOTIFIKASI HP / MAC OWNER saat aplikasi tertutup (owner 21 Nov 2026). Menyalakan = izin notifikasi → service worker baru/notif/sw-notif.js →
// token Firebase Cloud Messaging → notifOwner/{id perangkat} (rules v13: owner saja). Fungsi server (functions/index.js) mengirim ke semua token itu
// begitu tablet menulis permintaan baru. Bagian murni (nhDukung, nhVapidSah) tanpa peramban nyata — diuji di jsc (alat-uji/uji_notif_hp.py).
// Alat Firebase DISUNTIK app.js (nhPasang) — modul layar tidak mengimpor firebase.js (SDK dari gstatic) secara langsung.
let _alat = { app: () => null, simpan: async () => ({ gagal: true, pesan: 'Notifikasi belum tersambung ke Firebase' }), hapus: async () => ({ gagal: true, pesan: 'Notifikasi belum tersambung ke Firebase' }) };
/** app.js: { app: () => app Firebase, simpan: (token) => hasil, hapus: () => hasil } (firebase.js appFirebase / simpanTokenNotif / hapusTokenNotif). */
export function nhPasang(alat) { _alat = Object.assign({}, _alat, alat || {}); }

export const NH_SDK = 'https://www.gstatic.com/firebasejs/10.13.0/firebase-messaging.js';
export const NH_SW = 'notif/sw-notif.js';
export const NH_SCOPE = 'notif/';
export const NH_KUNCI = 'miqbal_notif_hp_v1';
/** Kunci publik web push (VAPID) proyek: base64url ±87 huruf, diawali B. Bukan rahasia — pasangan privatnya disimpan Firebase. */
export const nhVapidSah = (v) => /^B[A-Za-z0-9_-]{60,120}$/.test(String(v || '').trim());

/**
 * Perangkat ini bisa menerima push? env = { nav, win } (bawaan: navigator & window). Hasil { ok, sebab }. iPhone / iPad: hanya dari aplikasi di Layar
 * Utama (iOS 16.4+), bukan tab Safari biasa.
 */
export function nhDukung(env) {
  const E = env || {}; const nav = E.nav !== undefined ? E.nav : (typeof navigator !== 'undefined' ? navigator : null); const win = E.win !== undefined ? E.win : (typeof window !== 'undefined' ? window : null);
  if (!nav || !win) return { ok: false, sebab: 'Bukan peramban' };
  const ios = /iPhone|iPad|iPod/.test(String(nav.userAgent || '')) || (nav.platform === 'MacIntel' && Number(nav.maxTouchPoints) > 1);
  let mandiri = false; try { mandiri = nav.standalone === true || (typeof win.matchMedia === 'function' && win.matchMedia('(display-mode: standalone)').matches); } catch (e) { mandiri = false; }
  if (win.isSecureContext === false) return { ok: false, sebab: 'Halaman ini bukan https — notifikasi hanya bisa di alamat aplikasi yang aman' };
  if (ios && !mandiri) return { ok: false, sebab: 'Di iPhone / iPad notifikasi hanya bisa dari ikon aplikasi di Layar Utama: buka halaman ini di Safari › tombol Bagikan › Tambah ke Layar Utama, lalu buka dari ikon itu dan nyalakan di sini (iOS 16.4 ke atas)' };
  if (!('serviceWorker' in nav) || !('PushManager' in win) || !('Notification' in win)) return { ok: false, sebab: 'Peramban ini tidak mendukung notifikasi push' };
  return { ok: true, sebab: '' };
}
/** Keadaan tersimpan perangkat ini: { id, pada } atau null. */
export function nhTersimpan() { try { return JSON.parse(localStorage.getItem(NH_KUNCI) || 'null'); } catch (e) { return null; } }
export const nhIzin = () => (typeof Notification !== 'undefined' ? Notification.permission : 'tidak-ada');

/** Tunggu service worker registrasi ini aktif (paling lama ms). */
function tungguAktif(reg, ms) {
  return new Promise((selesai) => {
    if (reg.active) return selesai(true);
    const sw = reg.installing || reg.waiting; if (!sw) return selesai(!!reg.active);
    const t = setTimeout(() => selesai(!!reg.active), ms);
    sw.addEventListener('statechange', () => { if (sw.state === 'activated') { clearTimeout(t); selesai(true); } });
  });
}

/**
 * Nyalakan notifikasi di perangkat ini. WAJIB dipanggil langsung dari ketukan (Safari: izin hanya boleh diminta saat orangnya mengetuk) — karena itu
 * permintaan izin adalah langkah PERTAMA, sebelum apa pun yang menunggu. vapid = kunci publik web push proyek (Console › Project settings › Cloud
 * Messaging › Web Push certificates). Hasil { ok } atau { gagal, pesan }.
 */
export async function nhNyalakan(vapid) {
  const d = nhDukung(); if (!d.ok) return { gagal: true, pesan: d.sebab };
  if (!nhVapidSah(vapid)) return { gagal: true, pesan: 'Kunci notifikasi (VAPID) belum dipasang owner — tempel dulu di kotak di atas' };
  let izin; try { izin = await Notification.requestPermission(); } catch (e) { izin = 'denied'; }
  if (izin !== 'granted') return { gagal: true, pesan: izin === 'denied' ? 'Izin notifikasi DITOLAK di perangkat ini — buka setelan peramban / iPhone › Notifikasi untuk mengizinkannya, lalu coba lagi' : 'Izin notifikasi belum diberikan' };
  try {
    const reg = await navigator.serviceWorker.register(NH_SW, { scope: NH_SCOPE });
    if (!(await tungguAktif(reg, 15000))) return { gagal: true, pesan: 'Service worker notifikasi belum aktif — muat ulang halaman lalu coba lagi' };
    const M = await import(NH_SDK);
    if (!(await M.isSupported())) return { gagal: true, pesan: 'Firebase Messaging tidak mendukung peramban ini' };
    const token = await M.getToken(M.getMessaging(_alat.app()), { vapidKey: String(vapid).trim(), serviceWorkerRegistration: reg });
    if (!token) return { gagal: true, pesan: 'Token notifikasi tidak didapat' };
    const r = await _alat.simpan(token); if (r.gagal) return r;
    try { localStorage.setItem(NH_KUNCI, JSON.stringify({ id: r.id, pada: new Date().toISOString() })); } catch (e) { /* keadaan lokal saja */ }
    return { ok: true };
  } catch (e) { return { gagal: true, pesan: String((e && (e.code || e.message)) || e) }; }
}
/** Matikan notifikasi di perangkat ini: token dicabut dari Firebase & dari notifOwner. */
export async function nhMatikan() {
  try {
    const reg = 'serviceWorker' in navigator ? await navigator.serviceWorker.getRegistration(NH_SCOPE) : null;
    if (reg) { try { const M = await import(NH_SDK); await M.deleteToken(M.getMessaging(_alat.app())); } catch (e) { /* token sudah tidak ada */ } }
    const r = await _alat.hapus(); if (r.gagal) return r;
    try { localStorage.removeItem(NH_KUNCI); } catch (e) { /* keadaan lokal saja */ }
    return { ok: true };
  } catch (e) { return { gagal: true, pesan: String((e && (e.code || e.message)) || e) }; }
}
