// NOTIFIKASI APLIKASI TABLET (owner 23 Nov 2026: "Push penuh lewat Google"). Aplikasi tablet (cangkang Capacitor) tidak punya push peramban
// (WebView Android tanpa PushManager — dulu kartu Notifikasi menulis "Peramban ini tidak mendukung notifikasi push"). Jalurnya: plugin resmi
// @capacitor/push-notifications (Firebase Cloud Messaging Android, APK baru) → token disimpan di notifPerangkat/{uid}_{id perangkat} atas nama AKUN
// yang masuk di tablet (rules v17) → fungsi server kabarTablet (functions/) mengirim jawaban owner (disetujui / ditolak / dibaca + balasan) atas
// permintaan akun itu, walau aplikasi tablet ditutup. Kabar saat aplikasi TERBUKA tetap lewat notifikasi dalam aplikasi (pita, bunyi, lampu, lonceng).
// Tanpa impor & tanpa Firebase langsung — alat simpan/hapus/info DISUNTIK app.js (ntPasang); diuji di jsc (alat-uji/uji_tablet_tampilan.py).
const ntCap = () => (typeof window !== 'undefined' ? window.Capacitor : null);
let _ntAlat = {
  simpan: async () => ({ gagal: true, pesan: 'Notifikasi belum tersambung ke Firebase' }),
  hapus: async () => ({ gagal: true, pesan: 'Notifikasi belum tersambung ke Firebase' }),
  info: async () => ({}),
  uid: () => '',
  tungguMs: 0,   // 0 = NT_TUNGGU_MS (alat uji menyingkatnya)
};
/** app.js: { simpan: (token) => hasil {ok,id}|{gagal,pesan}, hapus: () => hasil, info: () => Perangkat.info, uid: () => uid akun yang masuk }. */
export function ntPasang(alat) { _ntAlat = Object.assign({}, _ntAlat, alat || {}); }

export const NT_PLUGIN = 'PushNotifications';
export const NT_KUNCI = 'miqbal_notif_tablet_v1';
export const NT_SALURAN = 'kabar';
export const NT_TUNGGU_MS = 20000;
export const NT_APK = 'Aplikasi tablet ini belum membawa notifikasi — pasang APK terbaru dari GitHub Actions (langkahnya di docs/notifikasi-tablet.md)';
export const NT_TANPA_FIREBASE = 'APK ini dibangun tanpa berkas Firebase (google-services.json) — owner menyimpan isinya di rahasia repo GOOGLE_SERVICES_JSON, lalu pasang APK yang dibangun sesudahnya (docs/notifikasi-tablet.md)';
export const NT_DITOLAK = 'Izin notifikasi DITOLAK di tablet ini — buka Setelan Android › Aplikasi › Toko Beras M.IQBAL › Notifikasi, izinkan, lalu coba lagi';

const ntAsli = () => { const c = ntCap(); return !!(c && typeof c.isNativePlatform === 'function' && c.isNativePlatform()); };
const ntPlugin = () => { const c = ntCap(); return c && c.Plugins ? c.Plugins[NT_PLUGIN] || null : null; };
function ntAdaPluginPush() {
  const c = ntCap(); if (!c) return false;
  try { if (Array.isArray(c.PluginHeaders)) return c.PluginHeaders.some((x) => x && x.name === NT_PLUGIN); } catch (e) { /* lanjut */ }
  return !!ntPlugin();
}
const ntPesanGalat = (e) => String((e && (e.message || e.code)) || e || 'tanpa keterangan');

/** Halaman ini di aplikasi tablet? (kartu Notifikasi memilih jalur tablet, bukan push peramban) */
export const ntAplikasi = () => ntAsli();
/** Bisa dinyalakan di tablet ini? info = Perangkat.info ({ pushSiap }) — boleh kosong. Hasil { ok, sebab }. */
export function ntDukung(info) {
  if (!ntAsli()) return { ok: false, sebab: 'Bukan aplikasi tablet' };
  if (!ntAdaPluginPush()) return { ok: false, sebab: NT_APK };
  if (info && info.pushSiap === false) return { ok: false, sebab: NT_TANPA_FIREBASE };
  return { ok: true, sebab: '' };
}
/** Keadaan tersimpan untuk akun `uid` di tablet ini: { uid, id, pada, ujung } atau null (akun lain yang menyalakan = null). */
export function ntTersimpan(uid) {
  let x = null; try { x = JSON.parse(localStorage.getItem(NT_KUNCI) || 'null'); } catch (e) { x = null; }
  return x && (!uid || x.uid === uid) ? x : null;
}
const ntUjung = (t) => String(t || '').slice(-16);

/** Izin notifikasi Android (13+ wajib diminta) → daftar ke Google → tunggu token. Hasil { ok, token } atau { gagal, pesan }. Tanpa minta izin bila mintaIzin false. */
export async function ntToken(mintaIzin, tunggu) {
  tunggu = tunggu || _ntAlat.tungguMs || NT_TUNGGU_MS;
  const P = ntPlugin(); if (!P) return { gagal: true, pesan: NT_APK };
  let iz;
  try { iz = await P.checkPermissions(); if ((!iz || iz.receive !== 'granted') && mintaIzin !== false) iz = await P.requestPermissions(); } catch (e) { return { gagal: true, pesan: 'Izin notifikasi tidak bisa diminta: ' + ntPesanGalat(e) }; }
  if (!iz || iz.receive !== 'granted') return { gagal: true, ditolak: true, pesan: NT_DITOLAK };
  const pegang = []; let usai = false; let selesai; let jam = null;
  const hasil = new Promise((r) => { selesai = r; });
  const tutup = (h) => { if (usai) return; usai = true; if (jam) clearTimeout(jam); pegang.forEach((x) => { try { if (x && typeof x.remove === 'function') x.remove(); } catch (e) { /* sudah lepas */ } }); selesai(h); };
  const dengar = async (nama, fn) => { try { const x = await P.addListener(nama, fn); if (usai) { try { x.remove(); } catch (e) { /* sudah lepas */ } } else pegang.push(x); } catch (e) { /* ntPlugin lama */ } };
  await dengar('registration', (x) => tutup(x && x.value ? { ok: true, token: String(x.value) } : { gagal: true, pesan: 'Google mengirim token kosong' }));
  await dengar('registrationError', (x) => tutup({ gagal: true, pesan: 'Google menolak pendaftaran tablet ini: ' + ntPesanGalat(x && (x.error || x)) }));
  jam = setTimeout(() => tutup({ gagal: true, pesan: 'Token notifikasi tidak datang dalam ' + Math.round(tunggu / 1000) + ' detik — periksa internet tablet, lalu coba lagi' }), tunggu);
  try { await P.register(); } catch (e) { tutup({ gagal: true, pesan: 'Pendaftaran notifikasi gagal: ' + ntPesanGalat(e) }); }
  return hasil;
}

/** Saluran "Kabar toko" (bunyi + muncul di atas layar). MainActivity APK baru juga membuatnya; ini cadangan. */
async function ntPastikanSaluran() {
  const P = ntPlugin(); if (!P || typeof P.createChannel !== 'function') return;
  try { await P.createChannel({ id: NT_SALURAN, name: 'Kabar toko', description: 'Jawaban owner, balasan pesan, dan permintaan dari aplikasi toko', importance: 5, visibility: 1, vibration: true, lights: true }); } catch (e) { /* saluran sudah ada */ }
}

/** Nyalakan di tablet ini — panggil LANGSUNG dari ketukan. Hasil { ok } atau { gagal, pesan }. */
export async function ntNyalakan() {
  let info = {}; try { info = (await _ntAlat.info()) || {}; } catch (e) { info = {}; }
  const d = ntDukung(info); if (!d.ok) return { gagal: true, pesan: d.sebab };
  await ntPastikanSaluran();
  const t = await ntToken(true); if (!t.ok) return t;
  const r = await _ntAlat.simpan(t.token); if (!r || r.gagal) return r || { gagal: true, pesan: 'Token tidak tersimpan' };
  try { localStorage.setItem(NT_KUNCI, JSON.stringify({ uid: String(_ntAlat.uid() || ''), id: r.id, pada: new Date().toISOString(), ujung: ntUjung(t.token) })); } catch (e) { /* keadaan lokal saja */ }
  return { ok: true };
}
/** Matikan di tablet ini: token dicabut dari Google & dikosongkan di notifPerangkat (akun tablet tidak boleh menghapus — rules v17). */
export async function ntMatikan() {
  const P = ntPlugin(); try { if (P && typeof P.unregister === 'function') await P.unregister(); } catch (e) { /* sudah tidak terdaftar */ }
  const r = await _ntAlat.hapus(); if (!r || r.gagal) return r || { gagal: true, pesan: 'Gagal mematikan' };
  try { localStorage.removeItem(NT_KUNCI); } catch (e) { /* keadaan lokal saja */ }
  return { ok: true };
}
/** Sesudah masuk: tablet yang sudah menyalakan memperbarui tokennya diam-diam bila Google menggantinya. Tidak pernah meminta izin. */
export async function ntSegarkan() {
  const uid = String(_ntAlat.uid() || ''); const lama = ntTersimpan(uid); if (!lama || !ntAsli() || !ntPlugin()) return { lewat: true };
  const t = await ntToken(false); if (!t.ok) return t;
  if (lama.ujung === ntUjung(t.token)) return { ok: true, sama: true };
  const r = await _ntAlat.simpan(t.token); if (!r || r.gagal) return r || { gagal: true };
  try { localStorage.setItem(NT_KUNCI, JSON.stringify(Object.assign({}, lama, { id: r.id, pada: new Date().toISOString(), ujung: ntUjung(t.token) }))); } catch (e) { /* keadaan lokal saja */ }
  return { ok: true, baru: true };
}
/** Notifikasi diketuk di bilah notifikasi → fn(layar) ('menu' / 'uang' / ''). Hasil: pelepas. */
export function ntPadaKetuk(fn) {
  const P = ntPlugin(); if (!P || typeof P.addListener !== 'function') return () => {};
  let h = null; let lepas = false;
  Promise.resolve(P.addListener('pushNotificationActionPerformed', (x) => { const d = (x && x.notification && x.notification.data) || {}; try { fn(String(d.layar || '')); } catch (e) { /* layar tujuan tidak ada */ } }))
    .then((x) => { h = x; if (lepas && h && h.remove) h.remove(); }).catch(() => {});
  return () => { lepas = true; if (h && h.remove) h.remove(); };
}
