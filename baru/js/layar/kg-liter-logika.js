// BERAT 1 LITER (owner 17 Nov 2026, butir 5: "takaran liter di wadah literan bisa diatur tanpa harus ngoding") — modul DAUN tanpa DOM: hanya data & mesin,
// supaya Jual, wadah, harga, harga tingkat (B1) dan nego memakai SATU penentu tanpa lingkar impor.
// Dulu tertanam: RASIO_DEFAULT 0,82 kg/L + RASIO_KONVERSI per merek (ketan & beras merah 0,80–0,815) di mesin (pembantu.js — TIDAK diubah, tetap angka bawaan).
// Setelan owner = kolom kgPerLiter { bawaan, merek{} } pada dokumen atur wadah TERBARU (wadahLiteran tipe 'atur' — dokumen yang sudah terbaca tablet).
// Urutan: angka owner untuk merek itu → angka bawaan mesin untuk merek itu → angka bawaan owner → 0,82.
// Hanya memengaruhi jualan SESUDAH diubah: nota menyimpan totalKg-nya sendiri, stok & modal literan dihitung dari situ.
// Batas wajar 0,5–1,2 kg: 1 liter beras ±0,8 kg; 1,8 kg itu SATU TAKAR (serok), bukan satu liter — owner menyebut "1 liter 1,8 kg" di catatannya 17 Nov.
import { ambilWadahLiteran } from '../data/toko.js';
import { RASIO_KONVERSI, RASIO_DEFAULT } from '../mesin/pembantu.js';

export const KG_LITER_MIN = 0.5;
export const KG_LITER_MAKS = 1.2;
const kglSah = (n) => isFinite(n) && n >= KG_LITER_MIN && n <= KG_LITER_MAKS;
const capWd = (p) => (p.tanggal || '') + ' ' + (p.jam || '');
/** Urutan dua catatan wadah: tanggal+jam dulu; semenit yang sama → id (id = jam mesin saat ditulis, jadi naik terus). Dipakai juga jual-logika (wdTerbaru). */
export function wdSesudah(x, y) {
  const c = capWd(x).localeCompare(capWd(y)); if (c) return c > 0;
  const nx = Number(x.id); const ny = Number(y.id);
  return isFinite(nx) && isFinite(ny) ? nx > ny : String(x.id) > String(y.id);
}
/** Setelan berat per liter dari dokumen (angka di luar batas wajar dibuang). */
export function kglBaku(x) {
  const out = { bawaan: null, merek: {} }; if (!x || typeof x !== 'object') return out;
  if (kglSah(Number(x.bawaan))) out.bawaan = Number(x.bawaan);
  if (x.merek && typeof x.merek === 'object') Object.keys(x.merek).forEach((m) => { if (kglSah(Number(x.merek[m]))) out.merek[String(m)] = Number(x.merek[m]); });
  return out;
}
/** Setelan yang berlaku: dari dokumen atur wadah terbaru. */
export function kglSetelan() {
  const a = (ambilWadahLiteran() || []).filter((w) => w && w.tipe === 'atur').reduce((t, x) => (!t || wdSesudah(x, t) ? x : t), null);
  return kglBaku(a && a.kgPerLiter);
}
/** Berat 1 liter beras merek/wadah ini (kg). */
export function kgPerLiter(merk) {
  const k = kglSetelan(); const m = String(merk || '');
  if (k.merek[m]) return k.merek[m];
  if (RASIO_KONVERSI[m]) return RASIO_KONVERSI[m];
  return k.bawaan || RASIO_DEFAULT;
}
/** Berat 1 liter bawaan (merek yang tidak punya angka sendiri). */
export function kgPerLiterBawaan() { return kglSetelan().bawaan || RASIO_DEFAULT; }
/** Ketikan dari layar (koma / titik desimal, sampai 3 angka di belakang koma) → { n } | { kosong } | { tolak }. */
export function kglBaca(teks, label) {
  const t = String(teks === undefined || teks === null ? '' : teks).trim(); if (!t) return { kosong: true };
  const n = Math.round(Number(t.replace(',', '.')) * 1000) / 1000;
  if (!isFinite(n)) return { tolak: label + ': angkanya tidak terbaca (contoh 0,82)' };
  if (n >= 1.5) return { tolak: label + ': ' + String(n).replace('.', ',') + ' kg itu satu TAKAR (serok), bukan satu liter — 1 liter beras ±0,8 kg' };
  if (!kglSah(n)) return { tolak: label + ': berat 1 liter harus ' + String(KG_LITER_MIN).replace('.', ',') + '–' + String(KG_LITER_MAKS).replace('.', ',') + ' kg' };
  return { n };
}
