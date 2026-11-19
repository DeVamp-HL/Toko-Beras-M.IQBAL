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
  return { hari: String(hari || ''), ketuk: rk(o.ketuk), macet: rk(o.macet), tempat,
    daftar: o.daftar.slice(-LC_MAKS_DAFTAR).map((x) => ({ jam: lcTeks(x && x.jam, 5), ms: lcBulat(x && x.ms), jenis: x && x.jenis === 'ketuk' ? 'ketuk' : 'macet', tempat: lcTeks(x && x.tempat, 60), aksi: lcTeks(x && x.aksi, 40) })) };
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
  return { hari: dasar.hari, ketuk: jenis === 'ketuk' ? tambah(dasar.ketuk) : dasar.ketuk, macet: jenis === 'macet' ? tambah(dasar.macet) : dasar.macet, tempat, daftar };
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
  return { n, terlama, judul, baris, tempat: tempat.map((t) => ({ nama: t.nama, teks: t.n + ' kali · terlama ' + lcLama(t.terlama) + ' · jumlah ' + lcLama(t.total) })), adaIsi: n > 0 };
}
/** Teks untuk disalin (dikirim ke yang memperbaiki): ringkasan + tiap tempat + kejadian terakhir. info = { perangkat, peramban, layarPx }. */
export function lcTeksSalin(isi, didukung, info) {
  const I = isi || lcKosong(''); const R = lcRingkas(I, didukung); const f = info || {};
  const tempat = Object.keys(I.tempat).map((k) => Object.assign({ nama: k }, I.tempat[k])).sort((a, b) => b.total - a.total || a.nama.localeCompare(b.nama));
  return ['KELANCARAN ' + I.hari + (f.perangkat ? ' · ' + f.perangkat : ''), f.peramban ? 'peramban: ' + f.peramban : '', f.layarPx ? 'layar: ' + f.layarPx : '', R.judul].concat(R.baris)
    .concat(tempat.length ? ['— per tempat (kali · terlama · jumlah) —'] : []).concat(tempat.map((t) => t.nama + ': ' + t.n + ' · ' + lcBulat(t.terlama) + ' ms · ' + lcBulat(t.total) + ' ms'))
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
  document.addEventListener('visibilitychange', () => { if (document.hidden && _jamSimpan) { clearTimeout(_jamSimpan); lcSimpan(); } });
  return _didukung;
}
/** Untuk kartu di Sistem › Perangkat. */
export const ukurMulusRingkas = () => lcRingkas(lcMuat(), _didukung);
export const ukurMulusSalin = (info) => lcTeksSalin(lcMuat(), _didukung, info);
export function ukurMulusKosongkan() { _isi = lcKosong(lcHari()); if (_jamSimpan) { clearTimeout(_jamSimpan); } lcSimpan(); return _isi; }
