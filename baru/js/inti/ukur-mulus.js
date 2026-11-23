// UKUR MULUS — owner 19 Nov 2026: "masih berat untuk penggunaan Android, terutama tablet Sunmi CPad 11".
// Mac tempat sistem ini diuji jauh lebih kencang dari tablet, jadi "terasa lancar di Mac" bukan bukti. Berkas ini mencatat DI PERANGKAT ITU SENDIRI
// tiap kali layar tersendat, supaya yang diperbaiki berikutnya adalah yang benar-benar terjadi di tablet — bukan tebakan:
//  · REAKSI TELAT  = dari jari mengetuk sampai layar selesai berubah ≥ 150 ms (ukuran peramban "event timing": ikut menghitung waktu menggambar);
//  · MACET         = satu pekerjaan menahan layar ≥ 100 ms ("long task") — mis. kabar data datang lalu layar dihitung ulang.
// Dicatat: berapa lama, di layar mana, sesudah ketukan apa. TIDAK ada isi nota, nama, atau rupiah yang dicatat, dan tidak ada yang dikirim ke server —
// tersimpan di perangkat ini saja (localStorage, satu kunci kecil), dibaca di Menu › Sistem › Perangkat › "Perangkat ini".
// Peramban tanpa alat ukurnya (Safari lama) → catatan kosong dan kartunya bilang begitu; tidak ada pengganti yang memboroskan baterai.
// Bagian hitungnya tanpa DOM (nama berawalan lc), diuji alat-uji/uji_ukur_mulus.py.
import { hariIniIso } from './format.js';

export const LC_KUNCI = 'miqbal_baru_ukur_mulus_v1';
export const LC_AMBANG_KETUK = 150;
export const LC_AMBANG_MACET = 100;
export const LC_MAKS_DAFTAR = 40;
export const LC_MAKS_TEMPAT = 30;
export const LC_MAKS_FUNGSI = 6;
const LC_JENDELA_KETUK_MS = 1500;
const LC_JARAK_KETUK_MS = 80;
const LC_MASA_BUKA_MS = 8000;

export const lcKosong = (hari) => ({ hari: String(hari || ''), ketuk: { n: 0, total: 0, terlama: 0 }, macet: { n: 0, total: 0, terlama: 0 }, tempat: {}, daftar: [] });
const lcBulat = (n) => Math.max(0, Math.round(Number(n) || 0));
const lcTeks = (t, maks) => String(t == null ? '' : t).replace(/[^\w ›·.,:()/+\-\u00C0-\u024F]/g, '').slice(0, maks);
/** Isi tersimpan → bentuk yang sah (isi rusak / versi lain → kosong); hari berganti → mulai dari nol. */
export function lcBaca(mentah, hari) {
  let o = null;
  try { o = typeof mentah === 'string' ? JSON.parse(mentah) : mentah; } catch (e) { o = null; }
  if (!o || typeof o !== 'object' || String(o.hari || '') !== String(hari || '') || !o.ketuk || !o.macet || !Array.isArray(o.daftar) || !o.tempat || typeof o.tempat !== 'object') return lcKosong(hari);
  const rk = (x) => ({ n: lcBulat(x && x.n), total: lcBulat(x && x.total), terlama: lcBulat(x && x.terlama) });
  const tempat = {};
  Object.keys(o.tempat).slice(0, LC_MAKS_TEMPAT).forEach((k) => { tempat[lcTeks(k, 60)] = rk(o.tempat[k]); });
  const hasil = { hari: String(hari || ''), ketuk: rk(o.ketuk), macet: rk(o.macet), tempat,
    daftar: o.daftar.slice(-LC_MAKS_DAFTAR).map((x) => ({ jam: lcTeks(x && x.jam, 5), ms: lcBulat(x && x.ms), jenis: x && x.jenis === 'ketuk' ? 'ketuk' : 'macet', tempat: lcTeks(x && x.tempat, 60), aksi: lcTeks(x && x.aksi, 40) })) };
  if (o.bingkai && typeof o.bingkai === 'object' && !Array.isArray(o.bingkai)) {
    const bk = {};
    Object.keys(o.bingkai).slice(0, LC_MAKS_TEMPAT).forEach((k) => { const x = o.bingkai[k] || {}; const fn = {};
      Object.keys(x.fungsi && typeof x.fungsi === 'object' ? x.fungsi : {}).slice(0, LC_MAKS_FUNGSI).forEach((f) => { fn[lcTeks(f, 50)] = lcBulat(x.fungsi[f]); });
      bk[lcTeks(k, 60)] = { n: lcBulat(x.n), total: lcBulat(x.total), skrip: lcBulat(x.skrip), gaya: lcBulat(x.gaya), fungsi: fn }; });
    hasil.bingkai = bk;
  }
  return hasil;
}
/**
 * mulus Android paket 3 (owner 23 Nov 2026): PENYEBAB bingkai panjang (≥ 100 ms) per tempat — dari "long animation frame" peramban: berapa yang SKRIP (hitungan
 * JavaScript) dan berapa yang GAYA & TATA LETAK (peramban menata ulang halaman sesudah skrip), plus nama fungsi skrip terberat. Kartu 19 & 23 Nov tidak bisa
 * membedakan keduanya — kini kartu berikutnya bisa. e = { ms, skrip, gaya, tempat, fungsi: [{ nama, ms }] }. Hasil = isi BARU; di bawah ambang = isi yang sama.
 */
export function lcCatatBingkai(isi, e, hari) {
  const hariIni = String(hari || ''); const dasar = isi && isi.hari === hariIni ? isi : lcKosong(hariIni);   // hari berganti = mulai dari nol
  const ms = lcBulat(e && e.ms); if (ms < LC_AMBANG_MACET) return dasar;
  const nama = lcTeks(e.tempat, 60) || 'lainnya'; const bk = Object.assign({}, dasar.bingkai || {});
  if (!bk[nama] && Object.keys(bk).length >= LC_MAKS_TEMPAT) return dasar;
  const lama = bk[nama] || { n: 0, total: 0, skrip: 0, gaya: 0, fungsi: {} }; const fn = Object.assign({}, lama.fungsi);
  ((e && e.fungsi) || []).forEach((f) => { const k = lcTeks(f && f.nama, 50); if (!k) return; if (fn[k] !== undefined || Object.keys(fn).length < LC_MAKS_FUNGSI) fn[k] = (fn[k] || 0) + lcBulat(f.ms); });
  bk[nama] = { n: lama.n + 1, total: lama.total + ms, skrip: lama.skrip + Math.min(ms, lcBulat(e.skrip)), gaya: lama.gaya + Math.min(ms, lcBulat(e.gaya)), fungsi: fn };
  return Object.assign({}, dasar, { bingkai: bk });
}
const lcPersen = (x, t) => (t > 0 ? Math.round(Math.min(x, t) / t * 100) : 0);
/** Baris teks salin untuk satu tempat: "Jual › Sering: 12 · skrip 70% · gaya & tata letak 20% · lain 10% · terberat: gambarGulir (jual.js) 900 ms". */
export function lcTeksBingkai(nama, x) {
  const sk = lcPersen(x.skrip, x.total); const gyTot = Math.min(100 - sk, lcPersen(x.gaya, x.total));   // skrip & gaya tidak bertumpuk: jumlahnya ≤ 100%
  const top = Object.keys(x.fungsi || {}).map((k) => [k, x.fungsi[k]]).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 2);
  return nama + ': ' + x.n + ' · skrip ' + sk + '% · gaya & tata letak ' + gyTot + '% · lain ' + Math.max(0, 100 - sk - gyTot) + '%' + (top.length ? ' · terberat: ' + top.map((t) => t[0] + ' ' + t[1] + ' ms').join(', ') : '');
}
/**
 * Catat satu kejadian: e = { jenis: 'ketuk' | 'macet', ms, tempat, aksi, jam }. Di bawah ambang → tidak dicatat. Hasil = isi BARU (isi lama tidak diubah).
 * Hari berganti → mulai dari nol untuk hari itu.
 */
export function lcCatat(isi, e, hari) {
  const dasar = isi && isi.hari === String(hari || '') ? isi : lcKosong(hari);
  const jenis = e && e.jenis === 'ketuk' ? 'ketuk' : 'macet'; const ms = lcBulat(e && e.ms);
  if (ms < (jenis === 'ketuk' ? LC_AMBANG_KETUK : LC_AMBANG_MACET)) return dasar;
  const tambah = (x) => ({ n: x.n + 1, total: x.total + ms, terlama: Math.max(x.terlama, ms) });
  const nama = lcTeks(e.tempat, 60) || 'lainnya';
  const tempat = Object.assign({}, dasar.tempat);
  if (tempat[nama] || Object.keys(tempat).length < LC_MAKS_TEMPAT) tempat[nama] = tambah(tempat[nama] || { n: 0, total: 0, terlama: 0 });
  const daftar = dasar.daftar.concat([{ jam: lcTeks(e.jam, 5), ms, jenis, tempat: nama, aksi: lcTeks(e.aksi, 40) }]).slice(-LC_MAKS_DAFTAR);
  const out = { hari: dasar.hari, ketuk: jenis === 'ketuk' ? tambah(dasar.ketuk) : dasar.ketuk, macet: jenis === 'macet' ? tambah(dasar.macet) : dasar.macet, tempat, daftar };
  if (dasar.bingkai) out.bingkai = dasar.bingkai;   // penyebab bingkai panjang (lcCatatBingkai) ikut terbawa
  return out;
}
/** Bahasa biasa: sepersepuluh detik — "0,8 dtk", "1,3 dtk"; di bawah 0,1 detik baru disebut ms ("60 ms"). */
export const lcLama = (ms) => (ms >= 100 ? String(Math.round(ms / 100) / 10).replace('.', ',') + ' dtk' : lcBulat(ms) + ' ms');
const lcDetik = (ms) => String(ms / 1000).replace('.', ',') + ' detik';
/** Ringkasan untuk kartu: kalimat biasa + tiga tempat terberat (menurut total waktu). didukung = peramban punya alat ukurnya. */
export function lcRingkas(isi, didukung) {
  const I = isi || lcKosong(''); const n = I.ketuk.n + I.macet.n; const terlama = Math.max(I.ketuk.terlama, I.macet.terlama);
  const tempat = Object.keys(I.tempat).map((k) => Object.assign({ nama: k }, I.tempat[k])).sort((a, b) => b.total - a.total || b.n - a.n || a.nama.localeCompare(b.nama)).slice(0, 3);
  const judul = !didukung.ketuk && !didukung.macet ? 'Peramban ini tidak punya alat ukurnya' : !n ? 'Hari ini belum pernah tersendat' : 'Tersendat hari ini: ' + n + ' kali · terlama ' + lcLama(terlama);
  const baris = [];
  if (didukung.ketuk) baris.push('Reaksi ketukan telat (' + lcDetik(LC_AMBANG_KETUK) + ' ke atas): ' + (I.ketuk.n ? I.ketuk.n + ' kali · terlama ' + lcLama(I.ketuk.terlama) : 'tidak ada'));
  if (didukung.macet) baris.push('Layar macet (' + lcDetik(LC_AMBANG_MACET) + ' ke atas): ' + (I.macet.n ? I.macet.n + ' kali · terlama ' + lcLama(I.macet.terlama) : 'tidak ada'));
  const BK = Object.keys(I.bingkai || {}).map((k) => I.bingkai[k]); const bkT = BK.reduce((x, b) => x + b.total, 0);
  if (bkT > 0) { const sk = lcPersen(BK.reduce((x, b) => x + b.skrip, 0), bkT); const gy = Math.min(100 - sk, lcPersen(BK.reduce((x, b) => x + b.gaya, 0), bkT));
    baris.push('Penyebab bingkai panjang: skrip ' + sk + '% · gaya & tata letak ' + gy + '% · lain ' + (100 - sk - gy) + '%'); }
  return { n, terlama, judul, baris, tempat: tempat.map((t) => ({ nama: t.nama, teks: t.n + ' kali · terlama ' + lcLama(t.terlama) + ' · jumlah ' + lcLama(t.total) })), adaIsi: n > 0 };
}
/** Teks untuk disalin (dikirim ke yang memperbaiki): ringkasan + tiap tempat + kejadian terakhir. info = { perangkat, peramban, layarPx }. */
export function lcTeksSalin(isi, didukung, info) {
  const I = isi || lcKosong(''); const R = lcRingkas(I, didukung); const f = info || {};
  const tempat = Object.keys(I.tempat).map((k) => Object.assign({ nama: k }, I.tempat[k])).sort((a, b) => b.total - a.total || a.nama.localeCompare(b.nama));
  return ['KELANCARAN ' + I.hari + (f.perangkat ? ' · ' + f.perangkat : ''), f.peramban ? 'peramban: ' + f.peramban : '', f.layarPx ? 'layar: ' + f.layarPx : '', R.judul].concat(R.baris)
    .concat(tempat.length ? ['— per tempat (kali · terlama · jumlah) —'] : []).concat(tempat.map((t) => t.nama + ': ' + t.n + ' · ' + lcBulat(t.terlama) + ' ms · ' + lcBulat(t.total) + ' ms'))
    .concat(I.bingkai && Object.keys(I.bingkai).length ? ['— penyebab bingkai panjang per tempat (kali · skrip · gaya & tata letak · lain) —'] : [])
    .concat(Object.keys(I.bingkai || {}).map((k) => Object.assign({ nama: k }, I.bingkai[k])).sort((a, b) => b.total - a.total || a.nama.localeCompare(b.nama)).map((x) => lcTeksBingkai(x.nama, x)))
    .concat(I.daftar.length ? ['— ' + I.daftar.length + ' kejadian terakhir —'] : []).concat(I.daftar.map((x) => x.jam + ' ' + (x.jenis === 'ketuk' ? 'ketuk' : 'macet') + ' ' + x.ms + ' ms · ' + x.tempat + (x.aksi ? ' · ' + x.aksi : '')))
    .filter(Boolean).join('\n');
}

/**
 * Peristiwa ketukan/ketikan dari peramban → satu kejadian per ketukan: peristiwa yang mulainya berdekatan (≤ 80 ms, juga dengan kejadian terakhir yang sudah
 * dicatat: `akhir`) digabung, diambil yang TERLAMA beserta nama tombolnya. Hanya click / pointerup / keydown / input.
 */
export function lcKelompokKetuk(daftar, akhir) {
  const pakai = (daftar || []).filter((e) => e && (e.nama === 'click' || e.nama === 'pointerup' || e.nama === 'keydown' || e.nama === 'input')).slice().sort((a, b) => a.mulai - b.mulai);
  const out = []; let batas = typeof akhir === 'number' ? akhir : -1e9; let g = null;
  pakai.forEach((e) => {
    if (g && e.mulai - g.akhir <= LC_JARAK_KETUK_MS) { g.akhir = e.mulai; if (e.ms > g.ms) { g.ms = e.ms; g.aksi = e.aksi || g.aksi; } else if (!g.aksi) g.aksi = e.aksi; return; }
    if (e.mulai - batas <= LC_JARAK_KETUK_MS) { batas = e.mulai; return; }
    g = { mulai: e.mulai, akhir: e.mulai, ms: e.ms, aksi: e.aksi || '' }; out.push(g);
  });
  return out.map((x) => ({ mulai: x.akhir, ms: x.ms, aksi: x.aksi }));
}

// ---------- bagian peramban ----------
let _akhirKetuk = -1e9;
let _isi = null; let _didukung = { ketuk: false, macet: false }; let _tempat = () => ''; let _aksi = { nama: '', t: -1e9 }; let _jamSimpan = null; let _pernahKetuk = false;
const lcHari = () => hariIniIso(new Date());
const lcJam = () => { const d = new Date(); return String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0'); };
function lcMuat() { if (_isi && _isi.hari === lcHari()) return _isi; let m = null; try { m = localStorage.getItem(LC_KUNCI); } catch (e) { m = null; } _isi = lcBaca(m, lcHari()); return _isi; }
function lcSimpan() { _jamSimpan = null; try { localStorage.setItem(LC_KUNCI, JSON.stringify(_isi)); } catch (e) { /* simpanan penuh / dilarang: catatan hari ini tetap di ingatan */ } }
function lcTunda() { if (_jamSimpan) return; _jamSimpan = setTimeout(lcSimpan, 4000); }
const lcNamaAksi = (el) => { const a = el && el.closest ? el.closest('[data-aksi], [data-tujuan], [data-ketik]') : null; return a ? (a.dataset.aksi || (a.dataset.tujuan ? 'pindah ' + a.dataset.tujuan : '') || (a.dataset.ketik ? 'ketik ' + a.dataset.ketik : '')) : ''; };
function lcTerima(jenis, ms, aksi) {
  const kini = typeof performance !== 'undefined' ? performance.now() : 0;
  const dekat = kini - _aksi.t < LC_JENDELA_KETUK_MS;
  const tempat = !_pernahKetuk && kini < LC_MASA_BUKA_MS ? 'membuka aplikasi' : (_tempat() || 'lainnya');
  const sebelum = lcMuat(); _isi = lcCatat(sebelum, { jenis, ms, tempat, aksi: aksi || (dekat ? _aksi.nama : jenis === 'macet' ? 'tanpa ketukan (kabar data / latar)' : ''), jam: lcJam() }, lcHari());
  if (_isi !== sebelum) lcTunda();
}
const lcBerkas = (u) => String(u || '').split('?')[0].split('/').pop();
/** Satu entri long-animation-frame → { ms, skrip, gaya, fungsi } (bagian peramban; hitungannya di lcCatatBingkai). */
export function lcUraiBingkai(e) {
  const akhir = (e.startTime || 0) + (e.duration || 0); const scripts = Array.isArray(e.scripts) ? e.scripts : [];
  const skrip = scripts.reduce((a, x) => a + (Number(x.duration) || 0), 0);
  const gaya = e.styleAndLayoutStart > 0 ? Math.max(0, akhir - e.styleAndLayoutStart) : 0;
  const fungsi = scripts.map((x) => ({ nama: (x.sourceFunctionName || String(x.invoker || '').slice(0, 30) || 'tanpa nama') + (x.sourceURL ? ' (' + lcBerkas(x.sourceURL) + ')' : ''), ms: Number(x.duration) || 0 }))
    .sort((a, b) => b.ms - a.ms).slice(0, 2);
  return { ms: e.duration, skrip, gaya, fungsi };
}
function lcTerimaBingkai(e) {
  const kini = typeof performance !== 'undefined' ? performance.now() : 0;
  const tempat = !_pernahKetuk && kini < LC_MASA_BUKA_MS ? 'membuka aplikasi' : (_tempat() || 'lainnya');
  const sebelum = lcMuat(); _isi = lcCatatBingkai(sebelum, Object.assign(lcUraiBingkai(e), { tempat }), lcHari());
  if (_isi !== sebelum) lcTunda();
}
/**
 * Pasang pencatat (sekali, saat aplikasi mulai). opsi.tempat() = nama layar yang sedang tampil, bahasa biasa (mis. "Jual › Riwayat").
 * Ongkosnya: dua pengamat peramban yang hanya berbunyi saat ada kejadian di atas ambang + satu pendengar ketukan yang menyimpan nama tombolnya.
 */
export function pasangUkurMulus(opsi) {
  _tempat = (opsi && opsi.tempat) || (() => '');
  if (typeof document === 'undefined' || typeof PerformanceObserver === 'undefined') return _didukung;
  const jenisAda = PerformanceObserver.supportedEntryTypes || [];
  document.addEventListener('pointerdown', (ev) => { _pernahKetuk = true; _aksi = { nama: lcNamaAksi(ev.target), t: performance.now() }; }, { capture: true, passive: true });
  if (jenisAda.indexOf('event') >= 0) {
    try {
      // satu ketukan = beberapa peristiwa beruntun (pointerup, click; keydown, input) dengan lama yang hampir sama → dihitung SEKALI, diambil yang terlama
      new PerformanceObserver((l) => { lcKelompokKetuk(l.getEntries().map((e) => ({ nama: e.name, mulai: e.startTime, ms: e.duration, aksi: lcNamaAksi(e.target) })), _akhirKetuk).forEach((g) => { _akhirKetuk = g.mulai; lcTerima('ketuk', g.ms, g.aksi); }); })
        .observe({ type: 'event', durationThreshold: LC_AMBANG_KETUK, buffered: false });
      _didukung = Object.assign({}, _didukung, { ketuk: true });
    } catch (e) { /* peramban menolak pilihan ini: bagian ketukan tidak diukur */ }
  }
  if (jenisAda.indexOf('longtask') >= 0) {
    try { new PerformanceObserver((l) => { l.getEntries().forEach((e) => lcTerima('macet', e.duration, '')); }).observe({ type: 'longtask', buffered: false }); _didukung = Object.assign({}, _didukung, { macet: true }); } catch (e) { /* tidak diukur */ }
  }
  // mulus Android paket 3: penyebab bingkai panjang (Chrome / WebView Android ≥ 123; Safari tidak punya → bagian ini kosong, kartu tidak menebak)
  if (jenisAda.indexOf('long-animation-frame') >= 0) {
    try {
      new PerformanceObserver((l) => { l.getEntries().forEach((e) => { if (e.duration < LC_AMBANG_MACET) return; lcTerimaBingkai(e); }); }).observe({ type: 'long-animation-frame', buffered: false });
      _didukung = Object.assign({}, _didukung, { bingkai: true });
    } catch (e) { /* tidak diukur */ }
  }
  document.addEventListener('visibilitychange', () => { if (document.hidden && _jamSimpan) { clearTimeout(_jamSimpan); lcSimpan(); } });
  return _didukung;
}
/** Untuk kartu di Sistem › Perangkat. */
export const ukurMulusRingkas = () => lcRingkas(lcMuat(), _didukung);
export const ukurMulusSalin = (info) => lcTeksSalin(lcMuat(), _didukung, info);
export function ukurMulusKosongkan() { _isi = lcKosong(lcHari()); if (_jamSimpan) { clearTimeout(_jamSimpan); } lcSimpan(); return _isi; }
