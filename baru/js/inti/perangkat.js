// PERANGKAT (paket S1, 19 Nov 2026) — SATU PINTU dari halaman ke perangkat keras lewat aplikasi tablet (APK Capacitor, apk/tambahan/*.java).
// Tiap perangkat = satu plugin kecil di aplikasi: CetakUsb (byte ke printer USB), PrinterSunmi (SDK resmi SUNMI: keadaan printer, hasil cetak,
// laci), Pindai (scanner bawaan), Lampu (LED CPad), Perangkat (kartu nama perangkat), Nfc (pembaca NFC bawaan). Modul ini TIDAK membaca/menulis data toko dan TANPA impor
// (dijalankan apa adanya di jsc oleh alat-uji/uji_perangkat_sunmi.py). Di HP/Mac (bukan aplikasi) semua fungsinya diam: tidak ada yang melempar.

const cap = () => (typeof window !== 'undefined' ? window.Capacitor : null);

/** Halaman ini berjalan di dalam aplikasi tablet (bukan peramban biasa)? */
export function asliAda() { const c = cap(); return !!(c && typeof c.isNativePlatform === 'function' && c.isNativePlatform()); }

/** Plugin `nama` ada di aplikasi yang terpasang? true / false; null = aplikasi tidak bisa ditanya (anggap "coba saja"). APK lama tidak punya plugin baru. */
export function adaPlugin(nama) {
  const c = cap(); if (!asliAda()) return false;
  try { if (Array.isArray(c.PluginHeaders)) return c.PluginHeaders.some((x) => x && x.name === nama); } catch (e) { /* lanjut ke cara lain */ }
  try { if (typeof c.isPluginAvailable === 'function') return !!c.isPluginAvailable(nama); } catch (e) { /* lanjut ke cara lain */ }
  return null;
}

function galat(pesan, kode) { const e = new Error(pesan); e.code = kode; return e; }

/** Panggil satu metode plugin. Menolak dengan Error ber-`code` bila aplikasinya menolak; 'TIDAK_ADA' = bukan aplikasi / plugin tak terpasang. */
export function panggilAsli(plugin, metode, isi) {
  const c = cap();
  if (!asliAda()) return Promise.reject(galat('Bukan aplikasi tablet — ' + plugin + ' hanya ada di aplikasi tablet kasir', 'TIDAK_ADA'));
  if (typeof c.nativePromise === 'function') return c.nativePromise(plugin, metode, isi || {});
  const p = c.Plugins && c.Plugins[plugin]; if (p && typeof p[metode] === 'function') return p[metode](isi || {});
  return Promise.reject(galat('Plugin ' + plugin + ' tidak ada di aplikasi ini — pasang APK terbaru', 'TIDAK_ADA'));
}

/** Dengarkan kejadian plugin (mis. Pindai › 'pindai'). Hasil: fungsi pelepas. Bukan aplikasi = tidak mendengar apa-apa. */
export function dengarAsli(plugin, kejadian, fn) {
  const c = cap(); if (!asliAda()) return () => {};
  const lepas = (h) => () => { Promise.resolve(h).then((x) => { if (x && typeof x.remove === 'function') return x.remove(); }).catch(() => {}); };
  try {
    const p = c.Plugins && c.Plugins[plugin];
    if (p && typeof p.addListener === 'function') return lepas(p.addListener(kejadian, fn));
    if (typeof c.addListener === 'function') return lepas(c.addListener(plugin, kejadian, fn));
    if (typeof c.nativeCallback === 'function') { c.nativeCallback(plugin, 'addListener', { eventName: kejadian }, fn); return () => {}; }
  } catch (e) { /* aplikasi lama tanpa plugin ini */ }
  return () => {};
}

// ---------- cetak lewat aplikasi ----------
/** Galat dari printer yang SUDAH menjawab (kertas habis, tutup terbuka, diam sesudah data dikirim): jangan dikirim ulang lewat jalur lain. */
export function galatPrinter(e) { return !!(e && typeof e.code === 'string' && e.code.indexOf('PRINTER_') === 0); }
const pesanGalat = (e) => (e && e.message ? e.message : String(e));

/** Kirim byte struk (base64) lewat aplikasi tablet. Hasil: { jalur: 'sunmi' | 'aplikasi', nama, peringatan, cadanganDari }.
 *  jalur 'sunmi' = SDK resmi SUNMI (keadaan printer diperiksa dulu, hasil cetak dikabari). Kalau SDK gagal SEBELUM ada byte terkirim
 *  (printer tak ketemu, plugin tak ada di APK lama) → jatuh ke CetakUsb, alasannya di `cadanganDari`. Kalau printer menjawab ada halangan
 *  → galatnya dilempar apa adanya: mengirim ulang lewat jalur lain bisa mencetak dobel atau percuma. */
export async function cetakAsli(data, jalur) {
  if (jalur === 'sunmi') {
    let sebab = '';
    try {
      const r = await panggilAsli('PrinterSunmi', 'cetak', { data });
      return { jalur: 'sunmi', nama: (r && r.nama) || '', peringatan: (r && r.peringatan) || '', cadanganDari: '' };
    } catch (e) {
      if (galatPrinter(e)) throw e;
      sebab = pesanGalat(e);
      try { await panggilAsli('PrinterSunmi', 'lepas', {}); } catch (e2) { /* APK lama: plugin tidak ada */ }
    }
    const r = await panggilAsli('CetakUsb', 'cetak', { data });
    return { jalur: 'aplikasi', nama: (r && r.nama) || '', peringatan: '', cadanganDari: sebab };
  }
  const r = await panggilAsli('CetakUsb', 'cetak', { data });
  return { jalur: 'aplikasi', nama: (r && r.nama) || '', peringatan: '', cadanganDari: '' };
}

/** Keadaan printer lewat SDK SUNMI: { status, kalimat, siap, menghalangi, nama, sdk }. Menolak bila tidak bisa ditanya. */
export const printerStatus = () => panggilAsli('PrinterSunmi', 'status', {});

// ---------- scanner ----------
const _pendengarPindai = [];
let _pindaiTerpasang = false;
let _pindaiTerakhir = null;
function pasangPindai() {
  if (_pindaiTerpasang || !asliAda() || adaPlugin('Pindai') === false) return;
  _pindaiTerpasang = true;
  dengarAsli('Pindai', 'pindai', (d) => {
    if (!d || typeof d.data !== 'string' || !d.data) return;
    _pindaiTerakhir = { data: d.data, pada: Date.now() };
    _pendengarPindai.slice().forEach((f) => { try { f(_pindaiTerakhir); } catch (e) { console.error('pindai', e); } });
  });
}
/** Dengarkan hasil scan scanner bawaan: fn({ data, pada }). Hasil: fungsi pelepas. */
export function padaPindai(fn) {
  _pendengarPindai.push(fn); pasangPindai();
  return () => { const i = _pendengarPindai.indexOf(fn); if (i >= 0) _pendengarPindai.splice(i, 1); };
}
/** Hasil scan terakhir sejak halaman dibuka ({ data, pada }) atau null. */
export const pindaiTerakhir = () => _pindaiTerakhir;

// ---------- NFC (paket S2a, 19 Nov 2026) ----------
// Pembaca NFC bawaan tablet: tiap kartu / stiker yang ditempelkan = satu kejadian berisi NOMOR SERI kartu (heksadesimal). Nomor seri bisa ditiru:
// dipakai untuk mengenali (kartu pelanggan), bukan untuk membayar.
const _pendengarTempel = [];
let _tempelTerpasang = false;
let _tempelTerakhir = null;
function pasangTempel() {
  if (_tempelTerpasang || !asliAda() || adaPlugin('Nfc') === false) return;
  _tempelTerpasang = true;
  dengarAsli('Nfc', 'tempel', (d) => {
    // nomor seri kartu = 4 sampai 10 byte heksadesimal; bentuk lain dibuang
    const uid = d && typeof d.uid === 'string' ? d.uid.toUpperCase() : '';
    if (!/^(?:[0-9A-F]{2}){4,10}$/.test(uid)) return;
    _tempelTerakhir = { uid, jenis: Array.isArray(d.jenis) ? d.jenis.map(String) : [], pada: Date.now() };
    _pendengarTempel.slice().forEach((f) => { try { f(_tempelTerakhir); } catch (e) { console.error('tempel', e); } });
  });
}
/** Dengarkan kartu NFC yang ditempelkan ke tablet: fn({ uid, jenis, pada }). Hasil: fungsi pelepas. */
export function padaTempel(fn) {
  _pendengarTempel.push(fn); pasangTempel();
  return () => { const i = _pendengarTempel.indexOf(fn); if (i >= 0) _pendengarTempel.splice(i, 1); };
}
/** Kartu terakhir yang ditempelkan sejak halaman dibuka ({ uid, jenis, pada }) atau null. */
export const tempelTerakhir = () => _tempelTerakhir;

// ---------- ketikan papan fisik vs scanner (panel PIN) ----------
// Scanner bermode "ketikan" mengetik isi kode seperti papan ketik, jauh lebih cepat dari jari. Di panel PIN ketikan seperti itu dulu
// terbaca sebagai PIN salah (5 kali = nama terkunci 5 menit). Ketikan papan fisik karena itu DITAMPUNG sebentar: beruntun secepat mesin = dibuang.
export const KETIK_JEDA_MESIN = 35;   // ms antara dua ketukan: di bawah ini bukan jari
export const KETIK_MESIN_MIN = 3;     // sekian ketukan berturut-turut secepat itu = scanner
export const KETIK_TUNGGU = 80;       // ms diam sebelum tampungan diteruskan ke PIN
/** Tampungan baru sesudah satu ketukan (tidak mengubah masukan). t = saat ketukan TERJADI (ev.timeStamp), bukan saat diproses. */
export function ketikTambah(tampung, k, t) { return (tampung || []).concat([{ k: String(k), t: Number(t) || 0 }]); }
/** Tampungan ini ketikan mesin? */
export function ketikMesin(tampung) {
  let beruntun = 1;
  for (let i = 1; i < (tampung || []).length; i++) {
    if (tampung[i].t - tampung[i - 1].t < KETIK_JEDA_MESIN) { beruntun += 1; if (beruntun >= KETIK_MESIN_MIN) return true; } else beruntun = 1;
  }
  return false;
}

// ---------- lampu ----------
export const LAMPU_WARNA = { merah: 1, hijau: 2, biru: 3, kuning: 4, sian: 5, magenta: 6, putih: 7 };
let _lampuMati = false;   // aplikasi ini terbukti tidak punya plugin Lampu → berhenti memanggil
/** Nyalakan lampu perangkat. Tidak pernah melempar: tanpa lampu = { ok: false }. o = { kedip, nyalaMs, matiMs, batasMs }. */
export function lampu(warna, o) {
  if (_lampuMati || !asliAda() || adaPlugin('Lampu') === false) return Promise.resolve({ ok: false });
  const isi = Object.assign({ warna: LAMPU_WARNA[warna] || LAMPU_WARNA.hijau, kedip: false, batasMs: 2000 }, o || {});
  return panggilAsli('Lampu', 'nyala', isi).then((r) => r || { ok: false }).catch(() => { _lampuMati = true; return { ok: false }; });
}
export function lampuPadam() {
  if (_lampuMati || !asliAda() || adaPlugin('Lampu') === false) return Promise.resolve({ ok: false });
  return panggilAsli('Lampu', 'mati', {}).then((r) => r || { ok: false }).catch(() => ({ ok: false }));
}
/** Nota tersimpan: hijau sebentar. */
export const lampuBerhasil = () => lampu('hijau', { batasMs: 1500 });
/** Cetak gagal / perlu perhatian: merah berkedip beberapa detik. */
export const lampuGagal = () => lampu('merah', { kedip: true, nyalaMs: 250, matiMs: 250, batasMs: 6000 });

// ---------- kartu kemampuan (layar diagnosis) ----------
/** Ringkasan apa yang ada di perangkat ini. Tidak pernah melempar. */
export async function kemampuan() {
  const k = { aplikasi: asliAda(), plugin: {}, info: null, lampu: null, pindai: null, nfc: null };
  if (!k.aplikasi) return k;
  ['CetakUsb', 'PrinterSunmi', 'Pindai', 'Lampu', 'Perangkat', 'Nfc'].forEach((n) => { k.plugin[n] = adaPlugin(n); });
  const coba = (plugin, metode) => (k.plugin[plugin] === false ? Promise.resolve(null) : panggilAsli(plugin, metode, {}).catch(() => null));
  [k.info, k.lampu, k.pindai, k.nfc] = await Promise.all([coba('Perangkat', 'info'), coba('Lampu', 'dukung'), coba('Pindai', 'info'), coba('Nfc', 'info')]);
  return k;
}
