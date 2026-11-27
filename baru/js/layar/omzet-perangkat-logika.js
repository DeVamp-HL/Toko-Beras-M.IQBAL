// OMZET PER PERANGKAT (paket P8, owner 27 Nov 2026 — sensus B13: "Bangun kartunya"). Logika TANPA DOM, BACA SAJA, nama berawalan orp. Dijaga alat-uji/uji_arsip_audit_p8.py.
//
// Tiap nota menyimpan perangkat yang MENCATATNYA (kolom `perangkat` = nama perangkat yang diatur di Menu › Toko ini › Perangkat & antrean, atau id perangkat bila belum dinamai;
// diisi penulis pusat sejak Agu 2026). Kartu ini menjumlah nota per perangkat itu — omzet = Σ hargaTotal nota yang masih berlaku (ambilPenjualan, angka yang sama dengan
// omzet per lokasi ssLaporLokasi), SEBELUM retur (uang retur dicatat perangkat yang melayani retur, bukan perangkat notanya — disebut, tidak dibagi). Nota lama tanpa
// nama perangkat dikelompokkan sendiri ("tidak tercatat"), nota kasir darurat (asalDarurat / id d-…) dikenali walau tanpa nama.
// JENIS (Mac/komputer · tablet · HP · kasir darurat · HP kasir lama) = TEBAKAN dari nama perangkat & aplikasinya di denyut (perangkatStatus) — disebut tebakan di layar.
import { ambilPenjualan, cacheMentah } from '../data/toko.js';
import { hariIniIso } from '../inti/format.js';

export const ORP_TANPA = 'tidak tercatat';
export const ORP_JENIS = [['komputer', 'Mac / komputer'], ['tablet', 'Tablet'], ['hp', 'HP'], ['darurat', 'Kasir darurat'], ['kasirLama', 'HP kasir (sistem lama)'], ['lain', 'Belum dikenali']];
const orpNamaJenis = (j) => (ORP_JENIS.find((x) => x[0] === j) || ORP_JENIS[ORP_JENIS.length - 1])[1];
const orpGeserBulan = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; return new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)).toISOString().slice(0, 7); };
/** Label perangkat satu nota: nama/id perangkat pencatat; kasir darurat tanpa nama = 'kasir darurat'; tanpa keterangan = ORP_TANPA. */
export function orpLabel(p) {
  const x = String((p && p.perangkat) || '').trim(); if (x) return x.slice(0, 60);
  return p && p.asalDarurat ? 'kasir darurat' : ORP_TANPA;
}
/** Tebak jenis perangkat dari label + denyutnya (aplikasi). */
export function orpJenis(label, denyut) {
  const L = String(label || ''); const a = denyut && denyut.aplikasi; const id = String((denyut && denyut.id) || L);
  if (a === 'darurat' || /^d-/.test(id) || /darurat/i.test(L)) return 'darurat';
  if (a === 'kasir' || /^k-/.test(id)) return 'kasirLama';
  if (/tablet|cpad|sunmi|\bpad\b|ipad/i.test(L)) return 'tablet';
  if (/\bhp\b|iphone|android|ponsel|handphone|samsung|oppo|vivo|xiaomi|redmi/i.test(L)) return 'hp';
  if (/\bmac\b|macbook|imac|laptop|komputer|\bpc\b|\bweb\b|windows/i.test(L)) return 'komputer';
  return 'lain';
}
/** Denyut perangkat yang cocok dengan label (nama sama, atau id sama). */
function orpDenyut(label) {
  const D = cacheMentah('perangkat') || []; const L = String(label || '');
  return D.find((d) => d && String(d.id || '').split('~')[0] === L) || D.find((d) => d && String(d.nama || '').trim() === L) || null;
}
const orpKunciNota = (p) => String(p.grupNota || p.trxId || p.id);
/** Jumlah per perangkat untuk nota-nota `daftar`: [{ label, jenis, jenisNama, omzet, nota, baris, aplikasi }] urut omzet terbesar; + total. */
export function orpJumlah(daftar) {
  const per = {}; let total = 0; const semuaNota = new Set();
  (daftar || []).forEach((p) => { const L = orpLabel(p); const g = per[L] = per[L] || { label: L, omzet: 0, nota: new Set(), baris: 0 }; const n = Number(p.hargaTotal) || 0;
    g.omzet += n; g.baris += 1; g.nota.add(orpKunciNota(p)); total += n; semuaNota.add(orpKunciNota(p)); });
  const baris = Object.keys(per).map((L) => { const g = per[L]; const d = L === ORP_TANPA ? null : orpDenyut(L); const j = L === ORP_TANPA ? 'lain' : orpJenis(L, d || (L === 'kasir darurat' ? { aplikasi: 'darurat' } : null));
    return { label: L, jenis: j, jenisNama: L === ORP_TANPA ? 'nota lama tanpa nama perangkat' : orpNamaJenis(j), omzet: Math.round(g.omzet), nota: g.nota.size, baris: g.baris,
      aplikasi: d ? (d.aplikasi === 'baru' ? 'sistem baru' : d.aplikasi === 'darurat' ? 'kasir darurat' : d.aplikasi === 'kasir' ? 'kasir' : 'sistem lama') : '', tanpa: L === ORP_TANPA }; })
    .sort((a, b) => (a.tanpa ? 1 : 0) - (b.tanpa ? 1 : 0) || b.omzet - a.omzet || a.label.localeCompare(b.label));
  const perJenis = ORP_JENIS.map(([j, nama]) => { const r = baris.filter((b) => !b.tanpa && b.jenis === j); return { jenis: j, nama, omzet: r.reduce((a, b) => a + b.omzet, 0), nota: r.reduce((a, b) => a + b.nota, 0), n: r.length }; }).filter((x) => x.n);
  return { baris, perJenis, total: Math.round(total), nota: semuaNota.size, tanpa: baris.filter((b) => b.tanpa).reduce((a, b) => a + b.omzet, 0) };
}
/** Kartu Omzet per perangkat: hari ini · bulan ini · bulan lalu (pilih), Σ per perangkat MENUTUP ke Σ nota rentang itu. */
export function orpRingkas(kini, pilih) {
  const iso = hariIniIso(kini); const bulan = iso.slice(0, 7); const lalu = orpGeserBulan(bulan, -1);
  const P = { hari: { nama: 'Hari ini', f: (t) => t === iso }, bulan: { nama: 'Bulan ini', f: (t) => t.slice(0, 7) === bulan }, lalu: { nama: 'Bulan lalu', f: (t) => t.slice(0, 7) === lalu } };
  const id = P[pilih] ? pilih : 'bulan'; const nota = ambilPenjualan().filter((p) => p && P[id].f(String(p.tanggal || '')));
  const J = orpJumlah(nota);
  return Object.assign({ pilih: id, nama: P[id].nama, pilihan: Object.keys(P).map((k) => [k, P[k].nama]), sumber: 'nota (Jual) · kolom perangkat pencatat · sebelum retur',
    kalimat: !nota.length ? 'Belum ada nota ' + P[id].nama.toLowerCase() : J.baris.filter((b) => !b.tanpa).length + ' perangkat mencatat ' + J.nota + ' nota ' + P[id].nama.toLowerCase()
      + (J.tanpa ? ' · sebagian nota lama tanpa nama perangkat' : ''),
    catatan: 'Jenis perangkat = tebakan dari namanya (Menu › Toko ini › Perangkat & antrean — beri nama yang jelas, mis. "Tablet kasir"). Omzet sebelum retur: uang retur dicatat perangkat yang melayani retur.' }, J);
}
