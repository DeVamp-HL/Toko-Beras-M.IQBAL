// PERINGATAN UANG → PENGINGAT & LONCENG (paket P3, owner 27 Nov 2026; sensus ulang A4). Tanpa DOM, BACA SAJA, awalan pw.
//
// Keputusan owner 27 Nov 2026 (AskUserQuestion): yang BERBUNYI di lonceng (owner saja) = biaya lewat anggaran · susut beras merah · modal per kg lewat batas ·
// harga di bawah minimum — "Kalau lu ada saran/usulan/ide untuk ditambahkan, boleh tambahkan asal syarat masuk akal". Usulan yang ditambahkan: untung per kg merek
// di bawah target owner · kas di bawah ambang kas minimum. Semuanya bisa dimatikan sendiri di Menu › Toko ini › Pengingat (saklar per jenis, pola yang sama).
//
// TIDAK ADA RUMUS UANG BARU: tiap baris = keadaan yang SUDAH dihitung layar lain, apa adanya:
//   anggaran → kendaliBulan lampu merah (Laporan › Biaya) + PPh final lampu merah (klPph, pos sisihan A47)
//   susut    → shDasborSusut(merekBulan).merah (Laporan › Laba › Susut; ambang merah = setelan susut)
//   hpp      → ckHppLewat 30 hari terakhir (Stok › Barang masuk; batas = setelan HPP per merek)
//   harga    → shRingkasHarga.bawah (Harga › Katalog › Harga minimum; harga yang dipakai kasir)
//   untungKg → klKgBulan.bawah (P1: untung per kg merek < target owner; target 0 = mati)
//   kas      → klKasMinimum (Menu › Toko ini › Target & ambang; ambang 0 = mati)
// Bentuk baris = sumber pengingat sistem-logika ({ id, jenis, kunci, teks, siapa, jatuh, n, ket }). Diteruskan app.js lewat lokal.peringatan (pola lokal.pajak /
// lokal.gudang — sistem-logika tidak mengimpor modul ini), OWNER SAJA (angka uang). Satu sumber yang galat tidak mematikan yang lain (disebut di `tidakTerbaca`).
import { kendaliBulan } from './kendali-biaya-logika.js';
import { merekBulan } from './laporan-logika.js';
import { shDasborSusut, shRingkasHarga } from './susut-harga-logika.js';
import { klPph, klKgBulan, klKasMinimum } from './kpi-laba-logika.js';
import { ckHppLewat } from './stok-catat-logika.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';
import { ingatPerVersi } from '../data/toko.js';

/** Jenis pengingat paket ini — id & nama SAMA dengan SS_JENIS_PENGINGAT sistem-logika (uji_dasbor_p3 membandingkan keduanya). */
export const PW_JENIS = [['anggaran', 'Biaya lewat anggaran'], ['susut', 'Susut beras merah'], ['hpp', 'Modal per kg lewat batas'], ['harga', 'Harga di bawah minimum'],
  ['untungKg', 'Untung per kg di bawah target'], ['kas', 'Kas di bawah ambang minimum']].map((j) => ({ id: j[0], nama: j[1] }));
export const PW_HPP_HARI = 30;   // kedatangan lewat batas HPP dibaca 30 hari terakhir (jatuh = tanggal kedatangannya)
const pwGeser = (iso, n) => { const d = new Date(String(iso) + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const pwId = (t) => String(t).replace(/\//g, '∕');   // id dipakai sebagai nama dokumen keadaan pengingat — garis miring tidak boleh
const pwPct = (x) => (x === null || x === undefined || !isFinite(x) ? '—' : String(Math.round(x * 10) / 10).replace('.', ',') + '%');

/**
 * Semua peringatan uang yang menyala SEKARANG → baris sumber pengingat. id stabil supaya "Selesai" di Pengingat berlaku sampai keadaannya berganti, bukan ditagih
 * ulang tiap hari: anggaran per bulan & pos · modal lewat batas per kedatangan · susut merah, harga di bawah minimum & untung per kg di bawah target = SATU baris
 * per jenis per bulan yang memuat JUMLAHNYA (asap cadangan 25 Nov: 14 merek susut merah + 18 merek di bawah target — satu baris per merek membanjiri lonceng;
 * jumlahnya berubah = baris baru). Kas: satu per hari selama di bawah ambang. Garis miring di id diganti (id = nama dokumen keadaan pengingat).
 * → array baris + .tidakTerbaca (sumber yang gagal dibaca, kalimat — bukan `galat`, supaya kelompok Dasbor tidak dianggap gagal seluruhnya).
 */
export function pwSumberPengingat(kini) { const iso = hariIniIso(kini); return ingatPerVersi('pwSumber|' + iso, () => pwSumberHitung(kini, iso)); }   // satu hitungan per hari & versi data (Menu, lonceng, Dasbor)
function pwSumberHitung(kini, iso) {
  const key = iso.slice(0, 7); const out = []; const tak = [];
  const coba = (nama, f) => { try { f(); } catch (e) { tak.push(nama + ': ' + String((e && e.message) || e)); } };
  coba('anggaran', () => { const K = kendaliBulan(key, kini);
    K.baris.forEach((r) => { if (r.lampu !== 'merah') return; out.push({ id: 'anggaran|' + key + '|' + r.id, jenis: 'anggaran', kunci: r.id, teks: r.nama + ' lewat anggaran', siapa: 'biaya', jatuh: iso,
      n: Math.max(0, Math.round(r.selisih || 0)), ket: r.lampuTeks + (r.proyeksi !== null && r.proyeksi !== undefined ? ' · perkiraan sebulan ' + RP(r.proyeksi) : '') + ' — Laporan › Biaya', tujuan: { ke: 'laporan', keluarga: 'biaya', bulan: key } }); });
    const X = klPph(K, kini); if (X && X.lampu === 'merah') out.push({ id: 'anggaran|' + key + '|pph', jenis: 'anggaran', kunci: 'pph', teks: X.nama + ' lewat anggaran', siapa: 'pajak', jatuh: iso,
      n: Math.max(0, Math.round(X.selisih || 0)), ket: X.lampuTeks + ' · pos sisihan, di luar laba bersih — Laporan › Biaya', tujuan: X.tujuan || { ke: 'laporan', keluarga: 'biaya', bulan: key } }); });
  coba('susut', () => { const M = merekBulan(key, kini); if (M.diarsip) return; const S = shDasborSusut(M, kini); if (!S.merah.length) return;
    const g = (m) => (M.susut && M.susut.tinggi || []).find((x) => x.merek === m) || {}; const nama = S.merah.slice(0, 3).map((m) => m + (g(m).susutPct !== undefined ? ' ' + pwPct(g(m).susutPct) : '')).join(', ') + (S.merah.length > 3 ? ', +' + (S.merah.length - 3) + ' merek' : '');
    out.push({ id: 'susut|' + key + '|' + S.merah.length, jenis: 'susut', kunci: 'susut', teks: (S.merah.length === 1 ? 'Susut ' + S.merah[0] : S.merah.length + ' merek susutnya') + ' merah', siapa: 'stok', jatuh: iso,
      n: Math.round(S.merah.reduce((a, m) => a + Math.abs(Number(g(m).susutRp) || 0), 0)), merek: S.merah.slice(),
      ket: nama + ' — di atas ambang merah ' + pwPct(S.ambangMerah) + ' (target toko ' + pwPct(S.target) + ') · Laporan › Laba › Susut, cari sebabnya di Stok › Cocokkan', tujuan: { ke: 'laporan', keluarga: 'laba', bulan: key } }); });
  coba('hpp', () => { const L = ckHppLewat(pwGeser(iso, -(PW_HPP_HARI - 1)), iso); if (!L.ada) return;
    L.daftar.forEach((x) => out.push({ id: pwId('hpp|' + x.batchId + '|' + x.merk), jenis: 'hpp', kunci: x.merk, teks: 'Modal ' + x.merk + ' lewat batas', siapa: x.pemasok || 'pemasok', jatuh: x.tanggal,
      n: Math.max(0, Math.round(x.lebihPerKg * x.kg)), ket: 'modal ' + RP(Math.round(x.hppPerKg)) + '/kg > batas ' + RP(x.batas) + '/kg · ' + (x.pemasok || 'pemasok') + ' ' + tanggalPendek(x.tanggal) + ' · lebih ' + RP(Math.round(x.lebihPerKg)) + '/kg — Stok › Barang masuk', tujuan: { ke: 'stok', lembar: 'masuk' } })); });
  coba('harga', () => { const H = shRingkasHarga(kini); if (H.keadaanMin === 'tanpaBiaya' || !(H.nBawah > 0)) return; const B = H.bawah;
    out.push({ id: 'harga|' + key + '|' + H.nBawah, jenis: 'harga', kunci: 'harga', teks: (H.nBawah === 1 && B[0] ? B[0].judul : H.nBawah + ' harga') + ' di bawah harga minimum', siapa: 'harga', jatuh: iso,
      n: 0, judul: B.map((x) => x.judul),   // tanpa jumlah rupiah: selisih hanya diketahui untuk contoh teratas (pratinjau 27 Nov: total beberapa contoh untuk belasan harga menyesatkan)
      ket: B.slice(0, 3).map((x) => x.judul + ' ' + RP(x.n) + ' < ' + RP(x.minimum)).join(' · ') + (H.nBawah > 3 ? ' · +' + (H.nBawah - 3) + ' lainnya' : '') + ' (minimum = modal + biaya toko per kg) — Harga › Katalog', tujuan: { ke: 'harga', keluarga: 'katalog' } }); });
  coba('untungKg', () => { const G = klKgBulan(key, kini); if (!(G.target && G.target.rp > 0) || G.diarsip) return;
    if (!G.bawah.length) return;
    out.push({ id: 'untungKg|' + key + '|' + G.bawah.length, jenis: 'untungKg', kunci: 'untungKg', teks: (G.bawah.length === 1 ? 'Untung ' + G.bawah[0].merek : G.bawah.length + ' merek untungnya') + ' di bawah target', siapa: 'harga', jatuh: iso, n: 0, merek: G.bawah.map((x) => x.merek),
      ket: G.bawah.slice(0, 3).map((x) => x.merek + ' ' + RP(Math.round(x.marginKg)) + '/kg').join(' · ') + (G.bawah.length > 3 ? ' · +' + (G.bawah.length - 3) + ' merek' : '') + ' < target ' + RP(G.target.rp) + '/kg ' + G.nama + ' — Laporan › Laba › Per merek', tujuan: G.tujuan }); });
  coba('kas', () => { const K = klKasMinimum(); if (!K.nyala || !K.bawah) return;
    out.push({ id: 'kas|' + iso, jenis: 'kas', kunci: 'kas', teks: 'Kas di bawah ambang minimum', siapa: 'uang', jatuh: iso, n: Math.round(K.kurang || 0), ket: K.teks + ' — Uang › Pindah uang', tujuan: K.tujuan || { ke: 'uang', keluarga: 'pindah' } }); });
  out.tidakTerbaca = tak; return out;
}

/** Ringkas untuk Dasbor (widget "Peringatan uang"): baris yang sama dengan lonceng, dikelompokkan per jenis (urutan PW_JENIS). */
export function pwRingkas(kini) {
  const S = pwSumberPengingat(kini); const jenis = PW_JENIS.map((j) => { const d = S.filter((x) => x.jenis === j.id); return { id: j.id, nama: j.nama, n: d.length, rp: d.reduce((a, x) => a + (x.n || 0), 0), daftar: d }; });
  const n = S.length;
  return { n, jenis, daftar: S, tidakTerbaca: S.tidakTerbaca || [], kalimat: n ? n + ' peringatan uang menyala · ' + jenis.filter((j) => j.n).map((j) => j.nama.toLowerCase() + ' ' + j.n).join(' · ') : 'Tidak ada peringatan uang yang menyala',
    sumber: 'Menu › Toko ini › Pengingat', tujuan: { ke: 'sistem', sistem: 'pengingat' } };
}
