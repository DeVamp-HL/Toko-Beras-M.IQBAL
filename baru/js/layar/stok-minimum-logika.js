// STOK MINIMUM PER BARANG (owner 26 Nov 2026, sensus ulang 1c B127 — "Hari + kg per barang"). Logika tanpa DOM, awalan sm. Modul DAUN: hanya data/toko.js
// & format, supaya Dasbor, Perlu perhatian (Ringkasan), Belanja, dan Stok bisa memakainya tanpa saling mengimpor.
//
// Aturan (keputusan owner):
//  - BAWAAN semua barang = angka hari "Disarankan kalau habis dalam" di Harga & Pemasok › Belanja › Atur (aturanToko/belanja.ambangHari, bawaan 7) — jadi
//    Dasbor, Perlu perhatian & Belanja memakai SATU angka. Dibaca dengan aturan yang SAMA dengan belanja-logika aturBelanja (uji_dasbor_sensus menutupnya).
//  - Per barang owner boleh mengisi HARI lain, ATAU MINIMUM JUMLAH (kg untuk beras karung, bungkus untuk kemasan). Setelan = aturanToko/stokMinimum (owner saja,
//    tanpa rules baru: aturanToko/{id} owner create/update). Kosong = ikut bawaan.
//  - Hari tersisa dihitung seperti Belanja (hariHabis): stok 0 / minus yang masih laku = 0 hari; tanpa gerak jual = TIDAK ditebak (bukan "aman", bukan "habis").
//  - Di bawah minimum: buku minus · minimum jumlah: sisa < minimum · minimum hari: hari tersisa ≤ batas.
// Konstanta lama AMBANG_HARI_KRITIS (4 hari, pembantu.js beku) TETAP dipakai tablet penjaga (staf tidak membaca aturanToko/belanja & stokMinimum).
import { cacheMentah } from '../data/toko.js';
import { DESIMAL } from '../inti/format.js';

export const SM_ID = 'stokMinimum';
export const SM_HARI_BAWAAN = 7;   // = belanja-logika ATUR_BELANJA_BAWAAN.ambangHari
export const SM_HARI_MAKS = 60;    // = batas "Disarankan kalau habis dalam" di Belanja › Atur
export const SM_JUMLAH_MAKS = 100000;
export const SM_CARA = [['bawaan', 'ikut bawaan'], ['hari', 'hari'], ['min', 'minimum jumlah']];
const smDok = (id) => cacheMentah('aturan').find((d) => String(d.id) === id) || null;
const smBil = (v) => { const t = String(v === undefined || v === null ? '' : v).trim().replace(/\s/g, ''); if (!t) return NaN;
  const n = Number(t.indexOf(',') >= 0 ? t.replace(/\./g, '').replace(',', '.') : /^-?\d{1,3}(\.\d{3})+$/.test(t) ? t.replace(/\./g, '') : t); return isFinite(n) ? n : NaN; };

/** Bawaan semua barang (hari): aturanToko/belanja.ambangHari 0–60, selain itu 7 — bentuk baca yang sama dengan aturBelanja (Number(null) = 0 ikut). */
export function smHariBawaan() { const a = smDok('belanja'); const v = a ? Number(a.ambangHari) : NaN; return a && isFinite(v) && v >= 0 && v <= SM_HARI_MAKS ? v : SM_HARI_BAWAAN; }
/** Kunci barang: 'karung|<merek>' · 'kemasan|<kunciKemasan>' — sama dengan daftarBarang (stok-logika) jenis + '|' + kunci. */
export const smKunci = (jenis, kunci) => String(jenis || '') + '|' + String(kunci || '');
export const smSatuan = (kunci) => (String(kunci).indexOf('kemasan|') === 0 ? 'bungkus' : 'kg');
/** Peta angka milik owner { kunci: { hari } | { min } } — isian rusak dibuang (barang itu ikut bawaan). */
export function smPeta() {
  const a = smDok(SM_ID); const b = a && a.barang && typeof a.barang === 'object' ? a.barang : {}; const out = {};
  Object.keys(b).forEach((k) => { const x = b[k] || {}; const h = Number(x.hari), m = Number(x.min);
    if (x.min !== undefined && x.min !== null && isFinite(m) && m > 0 && m <= SM_JUMLAH_MAKS) out[k] = { min: m };
    else if (x.hari !== undefined && x.hari !== null && isFinite(h) && h >= 0 && h <= SM_HARI_MAKS) out[k] = { hari: Math.round(h) }; });
  return out;
}
/** Setelan lengkap: bawaan hari + peta per barang + kapan disimpan. */
export function smAtur() { const d = smDok(SM_ID); return { bawaan: smHariBawaan(), peta: smPeta(), dariOwner: !!d, tanggal: d ? String(d.tanggal || '') : '', jam: d ? String(d.jam || '') : '' }; }
/** Batas satu barang: { hari, min, asal: 'barang'|'bawaan', teks }. */
export function smBatas(kunci, peta, bawaan) {
  const x = (peta || {})[kunci]; const sat = smSatuan(kunci);
  if (x && x.min !== undefined) return { hari: null, min: x.min, asal: 'barang', teks: 'minimum ' + DESIMAL(x.min) + ' ' + sat };
  if (x && x.hari !== undefined) return { hari: x.hari, min: null, asal: 'barang', teks: '≤ ' + x.hari + ' hari' };
  return { hari: bawaan, min: null, asal: 'bawaan', teks: '≤ ' + bawaan + ' hari (bawaan)' };
}
/** Hari tersisa seperti Belanja (hariHabis): tanpa laju = null; stok 0 / minus yang masih laku = 0; selain itu dibulatkan ke bawah. */
export const smHari = (sisa, laju) => (!(laju > 0) ? null : !(sisa > 0) ? 0 : Math.floor(sisa / laju + 1e-9));
/**
 * Satu barang dicek terhadap batasnya. b = { kunci, sisa, laju } (daftarBarang / buku stok). → { bawah, minus, hari, batas, kenapa }.
 * kenapa: 'minus' | 'jumlah' (sisa < minimum) | 'hari' (hari tersisa ≤ batas) | '' (aman / tidak ditebak).
 */
export function smCek(b, peta, bawaan) {
  const B = smBatas(b.kunci, peta, bawaan); const sisa = Number(b.sisa) || 0; const hari = smHari(sisa, Number(b.laju) || 0); const minus = sisa < -0.004;
  const kenapa = minus ? 'minus' : B.min !== null ? (sisa < B.min ? 'jumlah' : '') : hari !== null && hari <= B.hari ? 'hari' : '';
  return { bawah: !!kenapa, minus, hari, batas: B, kenapa, ditebak: B.min !== null || hari !== null };
}
/** Kata singkat keadaan satu barang terhadap batasnya (layar). */
export function smKata(C, satuan) {
  const bt = C.batas.min !== null ? C.batas.teks : '≤ ' + C.batas.hari + ' hari' + (C.batas.asal === 'bawaan' ? ', bawaan' : '');
  if (C.kenapa === 'minus') return 'buku MINUS — cocokkan';
  if (C.kenapa === 'jumlah') return 'di bawah ' + C.batas.teks;
  if (C.kenapa === 'hari') return C.hari <= 0 ? 'habis hari ini (batas ' + bt + ')' : '±' + C.hari + ' hari lagi (batas ' + bt + ')';
  if (!C.ditebak) return 'belum ada gerak jual — tidak ditebak';
  return C.batas.min !== null ? 'aman (' + C.batas.teks + ')' : '±' + C.hari + ' hari lagi · aman';
}
/**
 * Barang di bawah minimum dari baris buku stok [{ jenis: 'karung'|'kemasan', kunci, nama, sisa, laju, wadahStok }] — bentuk daftarBarang (stok-logika). Yang
 * dicek: beras karung (bukan buku stok wadah literan — wadah diisi dari karung, tidak dibeli) & kemasan, yang masih berbuku atau masih laku. SATU penghitung
 * untuk Dasbor & Perlu perhatian. Urut: buku minus dulu, lalu hari tersisa tersedikit, lalu minimum jumlah (kekurangan terbesar).
 */
export function smBawahDari(baris, peta, bawaan) {
  const P = peta || smPeta(); const bw = bawaan === undefined ? smHariBawaan() : bawaan; const out = []; let dicek = 0;
  (baris || []).forEach((b) => { if ((b.jenis !== 'karung' && b.jenis !== 'kemasan') || b.wadahStok) return; const sisa = Number(b.sisa) || 0; const laju = Number(b.laju) || 0;
    if (Math.abs(sisa) <= 0.004 && !(laju > 0)) return; dicek += 1; const kunci = smKunci(b.jenis, b.kunci); const C = smCek({ kunci, sisa, laju }, P, bw);
    if (C.bawah) out.push({ kunci, jenis: b.jenis, nama: b.nama, sisa, laju, satuan: b.jenis === 'kemasan' ? 'bungkus' : 'kg', cek: C, kata: smKata(C) }); });
  const urut = (x) => (x.cek.minus ? -1 : x.cek.kenapa === 'hari' ? x.cek.hari : 1e6);
  out.sort((a, b) => urut(a) - urut(b) || (a.cek.kenapa === 'jumlah' && b.cek.kenapa === 'jumlah' ? (a.sisa - a.cek.batas.min) - (b.sisa - b.cek.batas.min) : 0) || a.nama.localeCompare(b.nama));
  return { daftar: out, n: out.length, dicek, bawaan: bw, nSendiri: Object.keys(P).length };
}
/** Belanja (Harga & Pemasok › Belanja): batas hari SATU kelompok harga = batas terbesar di antara anggotanya. Minimum jumlah diubah jadi hari dengan laju jual
 *  merek itu (min ÷ laju, dibulatkan ke atas) — Belanja menyarankan dari laju. Tanpa angka per barang = atur apa adanya (Belanja tidak berubah). */
export function smAturKelompok(atur, isi, peta) {
  const P = peta || smPeta(); if (!Object.keys(P).length) return atur; let hari = atur.ambangHari;
  (isi || []).forEach((x) => { const B = smBatas(smKunci('karung', x.merk), P, atur.ambangHari); const h = B.min !== null ? (x.laju > 0 ? Math.ceil(B.min / x.laju - 1e-9) : null) : B.hari; if (h !== null && h > hari) hari = h; });
  return hari === atur.ambangHari ? atur : Object.assign({}, atur, { ambangHari: hari });
}
/** Batas hari satu merek untuk daftar Belanja "Habis dalam N hari" (sama dengan smAturKelompok untuk satu merek). */
export function smHariMerek(merk, laju, atur, peta) { const B = smBatas(smKunci('karung', merk), peta || smPeta(), atur.ambangHari); return B.min !== null ? (laju > 0 ? Math.ceil(B.min / laju - 1e-9) : atur.ambangHari) : B.hari; }

/** Draf lembar Atur dari peta: { kunci: { cara, n } }. */
export function smDraf(peta) { const P = peta || smPeta(); const out = {}; Object.keys(P).forEach((k) => { out[k] = P[k].min !== undefined ? { cara: 'min', n: DESIMAL(P[k].min) } : { cara: 'hari', n: String(P[k].hari) }; }); return out; }
/**
 * Simpan stok minimum per barang (owner). draf = { kunci: { cara: 'bawaan'|'hari'|'min', n } }; barang yang "ikut bawaan" tidak disimpan. Satu dokumen
 * aturanToko/stokMinimum — tidak menyentuh stok, harga, maupun uang.
 */
export function susunAturStokMinimum(draf, w) {
  const D = draf || {}; const barang = {}; let tolak = '';
  Object.keys(D).sort().forEach((k) => { if (tolak) return; const x = D[k] || {}; if (!x.cara || x.cara === 'bawaan') return;
    if (k.indexOf('karung|') !== 0 && k.indexOf('kemasan|') !== 0) { tolak = 'Barang tidak dikenal: ' + k; return; }
    const n = smBil(x.n); const nama = k.slice(k.indexOf('|') + 1);
    if (x.cara === 'hari') { if (!(isFinite(n) && n >= 0 && n <= SM_HARI_MAKS && Math.round(n) === n)) { tolak = nama + ': hari ditulis bilangan bulat 0–' + SM_HARI_MAKS; return; } barang[k] = { hari: n }; }
    else if (x.cara === 'min') { if (!(isFinite(n) && n > 0 && n <= SM_JUMLAH_MAKS)) { tolak = nama + ': minimum ' + smSatuan(k) + ' ditulis lebih dari 0 sampai 100.000'; return; } barang[k] = { min: Math.round(n * 100) / 100 }; }
    else tolak = nama + ': pilih bawaan, hari, atau minimum jumlah'; });
  if (tolak) return { tolak };
  const n = Object.keys(barang).length; const bawaan = smHariBawaan();
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: SM_ID, tanggal: w.tanggal, jam: w.jam, barang } }],
    patch: { smDraf: null, kabar: 'Stok minimum disimpan — ' + (n ? n + ' barang punya angka sendiri, sisanya' : 'semua barang') + ' ikut bawaan ≤ ' + bawaan + ' hari (Harga & Pemasok › Belanja › Atur)', kabarAwas: false } };
}
