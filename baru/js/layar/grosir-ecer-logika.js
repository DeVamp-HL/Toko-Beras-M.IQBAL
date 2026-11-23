// GROSIR vs ECER PER JENIS BARANG (owner 24 Nov 2026, keputusan brief 9 Okt "eceran vs grosir = jenis barang"). Logika tanpa DOM & tanpa Firebase; awalan ge.
// Otomatis dari jenis baris nota, tanpa isian: karung utuh = GROSIR; literan, kemasan, repack = ECER. Sisanya (wadah yang dijual, ongkir antar, karcis kasir
// darurat yang belum dirinci) = LAIN, disebut terpisah supaya jumlah ketiganya = omzet penjualan hari itu (sebelum retur).
// "Eceran" di Laporan › Per pelanggan (B5) dulu berarti pembeli tanpa tingkat harga — diganti "Pembeli umum" supaya satu kata satu arti.
// Nota yang berisi karung DAN kemasan dihitung di kedua kelompok (jumlah nota per kelompok bisa lebih dari nota hari itu) — kalimatnya menyebut itu.
import { ambilPenjualan, kunciNota } from '../data/toko.js';

export const GE_NAMA = { grosir: 'Grosir (karung utuh)', ecer: 'Ecer (literan · kemasan · repack)', lain: 'Lain (wadah · ongkir · karcis belum dirinci)' };
/** Kelompok satu baris penjualan: 'grosir' | 'ecer' | 'lain'. */
export function geJenis(p) {
  const j = String((p && p.jenis) || '');
  return j === 'karung' ? 'grosir' : j === 'literan' || j === 'kemasan' || j === 'repacking' ? 'ecer' : 'lain';
}
/** Ringkasan per kelompok untuk tanggal yang cocok: { grosir, ecer, lain: { omzet, kg, nota }, omzet (jumlah ketiganya), notaCampur }. */
export function geRingkas(cocok) {
  const out = { grosir: { omzet: 0, kg: 0, nota: 0 }, ecer: { omzet: 0, kg: 0, nota: 0 }, lain: { omzet: 0, kg: 0, nota: 0 }, omzet: 0, notaCampur: 0 };
  const nota = { grosir: new Set(), ecer: new Set(), lain: new Set() }; const per = {};
  (ambilPenjualan() || []).forEach((p) => {
    if (!p || !cocok(String(p.tanggal || ''))) return; const g = geJenis(p); const n = Number(p.hargaTotal) || 0; const k = kunciNota(p);
    // B3: ongkir antar menumpang di hargaTotal satu baris (kolom ongkirAntar) — dipisah ke "lain", barangnya tetap di kelompoknya
    const ongkir = Math.max(0, Math.min(n, Number(p.ongkirAntar) || 0)); if (ongkir) { out.lain.omzet += ongkir; nota.lain.add(k); }
    out[g].omzet += n - ongkir; out[g].kg += g === 'lain' ? 0 : Number(p.totalKg) || 0; nota[g].add(k); out.omzet += n;
    if (g !== 'lain') { per[k] = per[k] || {}; per[k][g] = true; }
  });
  ['grosir', 'ecer', 'lain'].forEach((g) => { out[g].nota = nota[g].size; out[g].omzet = Math.round(out[g].omzet); out[g].kg = Math.round(out[g].kg * 10) / 10; });
  out.omzet = Math.round(out.omzet); out.notaCampur = Object.keys(per).filter((k) => per[k].grosir && per[k].ecer).length;
  return out;
}
const geKg = (kg) => String(kg).replace('.', ',') + ' kg';
/** Baris teks untuk rekap (WA / kertas): [label, isi] — kelompok yang kosong tidak ditulis; kelompok lain hanya bila ada. */
export function geBaris(G, rp) {
  const b = [];
  ['grosir', 'ecer', 'lain'].forEach((g) => { const x = G[g]; if (!x.nota && !x.omzet) return; b.push([GE_NAMA[g], rp(x.omzet) + (g === 'lain' ? '' : ' · ' + geKg(x.kg)) + ' · ' + x.nota + ' nota']); });
  if (G.notaCampur) b.push(['Nota campuran', G.notaCampur + ' nota berisi karung & ecer — dihitung di keduanya']);
  return b;
}
