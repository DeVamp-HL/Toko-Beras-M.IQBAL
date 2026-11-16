// Salinan aplikasi di perangkat — sisi halaman (putaran T1 langkah 4, owner 16 Nov 2026: tablet kasir bisa DIBUKA tanpa internet).
// Pekerjanya baru/sw-baru.js (dicap saat terbit). Di sini: siapa yang memasang, kapan versi baru boleh dipakai, dan kalimat statusnya.
//  · Memasang: hanya aplikasi tablet (asliAda) — HP & Mac owner tidak berubah; perangkat yang SUDAH memakai salinan terus memperbaruinya;
//    ?salinan=pasang (uji peramban) / ?salinan=lepas (hapus salinan & muat ulang dari internet).
//  · Versi baru diunduh di belakang layar lalu MENUNGGU. Dipakai (muat ulang) hanya saat AMAN: layar tertutup gerbang (belum masuk / "Siapa yang
//    jaga?" / belum disetujui) DAN tidak ada isian yang belum disimpan DAN tidak ada yang sedang mengetik. Orang yang sedang jualan tidak pernah
//    dimuat ulang di tengah jalan; sesudah 5 menit tak disentuh tablet kembali ke "Siapa yang jaga?" dan di situ versi baru dipasang.
//  · Diperiksa ulang tiap 15 menit dan saat internet kembali — tablet yang menyala seharian tetap ikut terbitan baru.
export const SL_JEDA_PERIKSA_MS = 15 * 60 * 1000;
export const SL_JEDA_COBA_MS = 30 * 1000;
const BULAN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];

/** Perlu memasang / memperbarui salinan di perangkat ini? */
export function slPerluPasang(o) {
  const x = o || {};
  if (x.minta === 'lepas') return false;
  return !!(x.asli || x.dikendalikan || x.minta === 'pasang');
}
/** Boleh memuat ulang ke versi baru SEKARANG? gerbang = layar tertutup gerbang (tidak ada yang sedang bekerja). */
export function slAman(k) {
  const x = k || {};
  return !!x.gerbang && !(x.isian > 0) && !x.mengetik;
}
/** Waktu terbit (UTC) → tanggal & jam SETEMPAT ("16 Nov 18.35"). */
export function slWaktu(iso) {
  const d = new Date(iso || ''); if (!iso || isNaN(d.getTime())) return '';
  const dua = (n) => (n < 10 ? '0' : '') + n;
  return d.getDate() + ' ' + BULAN[d.getMonth()] + ' ' + dua(d.getHours()) + '.' + dua(d.getMinutes());
}
/** Kalimat status untuk orang toko — jujur: "bisa dibuka tanpa internet" HANYA bila salinan lengkap sedang dipakai. */
export function slKalimat(st) {
  const s = st || {};
  if (!s.didukung || !s.dipasang) return '';
  if (!s.dikendalikan || !s.aktif || !s.aktif.lengkap) {
    if (s.gagal) return 'Belum bisa dibuka tanpa internet — menyimpan aplikasi gagal (' + s.gagal + '). Dicoba lagi otomatis.';
    if (s.memasang) return 'Menyimpan aplikasi di perangkat ini supaya bisa dibuka tanpa internet…';
    return 'Belum bisa dibuka tanpa internet — tunggu sebentar selagi ada internet.';
  }
  const w = slWaktu(s.aktif.terbit);
  const dasar = 'Bisa dibuka tanpa internet · versi ' + (w || s.aktif.versi);
  if (s.menunggu) return dasar + ' · versi baru siap, dipasang saat layar "Siapa yang jaga?" terbuka tanpa isian';
  if (s.memasang) return dasar + ' · menyimpan versi baru…';
  if (s.gagal) return dasar + ' · versi baru belum bisa disimpan (' + s.gagal + '), dicoba lagi';
  return dasar;
}

/**
 * Pasang & jaga salinan. o: { perlu, lepas, aman(), sebelumMuatUlang(), berubah(status) }. → { status(), cobaPakai(), pakaiSekarang(), periksa(), lepas() }
 * Tanpa service worker (peramban lama / bukan https) = diam.
 */
export function pasangSalinan(o) {
  const sw = typeof navigator !== 'undefined' && navigator.serviceWorker ? navigator.serviceWorker : null;
  const st = { didukung: !!sw, dipasang: false, dikendalikan: !!(sw && sw.controller), aktif: null, menunggu: false, memasang: false, gagal: '' };
  const kabar = () => { try { if (o.berubah) o.berubah(Object.assign({}, st)); } catch (e) { /* kalimat status tidak boleh menjatuhkan halaman */ } };
  const api = { status: () => Object.assign({}, st), cobaPakai() {}, pakaiSekarang() {}, periksa() {}, lepas: () => Promise.resolve() };
  if (!sw) return api;
  const awalDikendalikan = st.dikendalikan; let diminta = false; let reg = null; let muat = false;
  const tanyaVersi = (w) => new Promise((jadi) => {
    if (!w) { jadi(null); return; }
    const ch = new MessageChannel(); const t = setTimeout(() => jadi(null), 4000);
    ch.port1.onmessage = (e) => { clearTimeout(t); jadi(e.data || null); };
    try { w.postMessage({ jenis: 'versi' }, [ch.port2]); } catch (e) { clearTimeout(t); jadi(null); }
  });
  const segarkan = () => {
    st.dikendalikan = !!sw.controller; st.menunggu = !!(reg && reg.waiting); st.memasang = !!(reg && reg.installing);
    return tanyaVersi(sw.controller).then((v) => { st.aktif = v; kabar(); });
  };
  api.lepas = () => sw.getRegistrations().then((rs) => Promise.all(rs.filter((r) => /\/sw-baru\.js$/.test((r.active || r.waiting || r.installing || {}).scriptURL || '')).map((r) => r.unregister())))
    .then(() => (typeof caches !== 'undefined' ? caches.keys().then((ks) => Promise.all(ks.filter((k) => /^baru-(salinan|luar|huruf)-/.test(k)).map((k) => caches.delete(k)))) : null))
    .catch(() => null);
  if (o.lepas) {
    api.lepas().then(() => { const u = new URL(location.href); u.searchParams.delete('salinan'); location.replace(u.href); });
    return api;
  }
  if (!o.perlu) return api;
  st.dipasang = true;
  api.pakaiSekarang = () => { if (reg && reg.waiting) { diminta = true; reg.waiting.postMessage({ jenis: 'aktifkan' }); } };
  api.cobaPakai = () => { if (reg && reg.waiting && !diminta) { let ok = false; try { ok = !!o.aman(); } catch (e) { ok = false; } if (ok) api.pakaiSekarang(); } };
  api.periksa = () => { if (reg && navigator.onLine !== false) reg.update().catch(() => {}); };
  sw.addEventListener('controllerchange', () => {
    // pindah ke versi baru yang diminta halaman ini (atau ke versi baru sesudah salinan lama) → muat ulang SEKALI; pemasangan pertama tidak memuat ulang
    if ((diminta || awalDikendalikan) && !muat) { muat = true; try { if (o.sebelumMuatUlang) o.sebelumMuatUlang(); } catch (e) { /* tetap muat ulang */ } location.reload(); return; }
    segarkan();
  });
  sw.addEventListener('message', (e) => {
    const d = e.data || {}; if (d.asal !== 'salinan') return;
    if (d.jenis === 'memasang') { st.memasang = true; st.gagal = ''; } else if (d.jenis === 'gagal') { st.memasang = false; st.gagal = String(d.sebab || 'tidak diketahui'); } else if (d.jenis === 'terpasang') { st.memasang = false; st.gagal = ''; }
    kabar(); setTimeout(() => { segarkan().then(api.cobaPakai); }, 0);
  });
  const pantau = (w) => { if (w) w.addEventListener('statechange', () => { segarkan().then(api.cobaPakai); }); };
  sw.register('sw-baru.js').then((r) => {
    reg = r; pantau(r.installing); pantau(r.waiting);
    r.addEventListener('updatefound', () => { pantau(r.installing); segarkan(); });
    segarkan().then(api.cobaPakai);
    api.periksa();   // tiap kali dibuka: tanya versi terbaru (tanpa internet = diam)
  }, (e) => { st.gagal = String((e && e.message) || e); kabar(); });
  setInterval(api.periksa, SL_JEDA_PERIKSA_MS);
  setInterval(api.cobaPakai, SL_JEDA_COBA_MS);
  if (typeof window !== 'undefined') window.addEventListener('online', api.periksa);
  return api;
}
