// PAKET KPI LABA (owner 24 Nov 2026 — paket brief terakhir sebelum sistem dibekukan 15 Des). Logika TANPA DOM, nama berawalan kl (bundel uji jsc satu lingkup).
// Dijaga alat-uji/uji_kpi_laba.py (jsc kotak pasir + statis + --kontrol).
//
// ATURAN: tiap angka di sini MEMANGGIL fungsi sumber yang sudah dipakai layar lain (satu angka satu sumber) dan menyebut sumbernya; mesin uang (baru/js/mesin/*,
// laba bersih, arus kas) TIDAK disentuh. Yang dihitung di sini hanya PERBANDINGAN (persen, hari, saran) dari angka sumber itu:
//   1 margin laba kotor %   = laba kotor ÷ omzet ber-HPP                  — keManaLabaKotor / jenisBulan (Laporan › Laba)
//   2 margin laba usaha %   = laba kotor − biaya toko − biaya karyawan − potongan QRIS − susut & selisih stok, ÷ omzet ber-HPP
//                             identitas yang DIJAGA: laba usaha − hapus buku piutang + lebih/kurang kas = laba bersih mesin (keManaLabaKotor)
//   3 margin laba bersih %  = laba bersih mesin ÷ omzet ber-HPP, + baris "sesudah perkiraan PPh final" (pjPerkiraanBulan; uang keluar bertulis pajak/PPh di bulan
//                             itu sudah ada di biaya toko → hanya SISANYA yang dikurangkan, tidak terpotong dua kali)
//      Ketiganya memakai penyebut yang SAMA (omzet ber-HPP = omzet yang modalnya tercatat, = penyebut rasio titik impas) supaya tangganya bisa dibandingkan.
//   4 saran harga & mark-up = modal ÷ (1 − target margin) · mark-up = margin ÷ (1 − margin) — target per jenis milik owner (aturanToko/kpiLaba.targetMargin),
//                             BAWAAN = margin terwujud 3 bulan terakhir per jenis dari mesin (lpJenisRentang), bukan angka karangan. Hanya saran.
//   5 pembanding BPS 2016  = konteks, bukan target; sumbernya disebut.
//   6 GMROI per merek       = laba kotor merek (merekBulan) ÷ rata-rata nilai stok merek bulan itu (umNilaiRata = buku Umur & putaran)
//   7 siklus uang (hari)    = hari stok (umRingkas: periode ÷ perputaran) + rata-rata hari bon tertagih (tertagihBon) − rata-rata hari bayar pemasok (bpHariBayar)
//   8 omzet hari ini vs target harian (aturanToko/kpiLaba.targetHarian; bawaan = omzet impas per hari, titikImpas)
//   9 ambang kas minimum    = saldoKantong (layar Uang) — keempat tempat (laci + brankas + rekening + amplop; owner 24 Nov: "Semua empat tempat")
//  11 bon dalam kg beras    = rupiah bon ÷ modal per kg stok karung (nilai neraca: sisa × modal per kg buku)
//  12 HPP maksimal per kg   = stok-catat-logika ckHppLewat (setelan di aturanToko/catatStok, dibaca tablet)
// Butir 10 (nota terbesar) = riwayat-logika rwTerbesar · 13 = bon-pemasok-logika bpHariBayar · 14 = sistem-logika (pengingat cek gudang) · 15 = pesanan-logika poLamaPenuhi.
import { keManaLabaKotor, jenisBulan, lpJenisRentang, merekBulan, lpMerekBuku, lpNamaBulan, rekapHari, LP_JENIS } from './laporan-logika.js';
import { kendaliBulan, titikImpas } from './kendali-biaya-logika.js';
import { pjPerkiraanBulan, PJ_LABEL } from './pajak-logika.js';
import { ugAturDok, ugAngka, ugKosong, saldoKantong, ugNamaTempat } from './uang-logika.js';
import { umRingkas, umNilaiRata } from './stok-logika.js';
import { tertagihBon } from './bon-logika.js';
import { bpHariBayar, bpHariTeks } from './bon-pemasok-logika.js';
import { poLamaPenuhi } from './pesanan-logika.js';
import { rwTerbesar } from './riwayat-logika.js';
import { ckHppLewat } from './stok-catat-logika.js';
import { aturHarga } from './harga-logika.js';
import { JAM_BUKA, JAM_TUTUP } from './ringkasan-logika.js';
import { ambilPengeluaranHarian, cacheMentah, ingatStokKarung, ingatPerVersi } from '../data/toko.js';
import { RP, ANGKA, hariIniIso, tanggalPendek } from '../inti/format.js';
import { akhirBulanIso } from '../mesin/pembantu.js';

// ---------- pembanding BPS (butir 5): konteks, BUKAN target ----------
export const KL_BPS = { grosir: 9.84, eceran: 11.35, tahun: 2016,
  sumber: 'BPS, Distribusi Perdagangan Komoditas Beras Indonesia 2016, hlm. 17 — rata-rata rasio margin perdagangan & pengangkutan (MPP) beras: pedagang besar 9,84 %, pedagang eceran 11,35 % (termasuk ongkos angkut). MPP = nilai penjualan − nilai pembelian (hlm. 6); publikasi tidak menyebut pembaginya (harga beli atau harga jual), jadi bandingkan dengan margin DAN mark-up toko',
  pendek: 'BPS 2016 (termasuk angkut)' };
export const KL_ID = 'kpiLaba';
export const KL_JENIS = LP_JENIS;   // karung · kemasan · literan · repack — satu daftar dengan Laporan › Laba › Per jenis
export const KL_TARGET_MAKS = 90;   // target margin % (lebih dari 0 sampai 90) — penjaga salah ketik, bukan kebijakan
export const KL_RP_MAKS = 10000000000;   // penjaga salah ketik rupiah (Rp10 miliar)
const klPct = (a, b) => (b > 0 && a !== null && a !== undefined && isFinite(a) ? a / b * 100 : null);
/** Persen untuk layar: '—' = belum bisa dihitung (bukan 0). Satu angka di belakang koma; di bawah 1 % dua angka. */
export const klPctTeks = (p) => (p === null || p === undefined || !isFinite(p) ? '—' : (p < 0 ? '−' : '') + String(Math.abs(p) < 1 ? Math.round(Math.abs(p) * 100) / 100 : Math.round(Math.abs(p) * 10) / 10).replace('.', ',') + ' %');
/** Mark-up dari margin (keduanya persen): m ÷ (100 − m) × 100. margin ≥ 100 % → null. */
export const klMarkup = (m) => (m === null || m === undefined || !isFinite(m) || m >= 100 ? null : m / (100 - m) * 100);
/** Harga saran dari modal satuan & target margin %: modal ÷ (1 − m); dibulatkan KE ATAS ke kelipatan `bulat` (aturan bulat katalog). null bila tak bisa. */
export function klHargaSaran(modal, targetPct, bulat) {
  if (!(modal > 0) || targetPct === null || targetPct === undefined || !(targetPct >= 0) || targetPct >= 100) return null;
  const x = modal / (1 - targetPct / 100); const k = Number(bulat) || 0; return k > 0 ? Math.ceil(x / k - 1e-9) * k : Math.round(x);
}

// ---------- setelan owner: aturanToko/kpiLaba ----------
/** { targetHarian (Rp, 0 = bawaan omzet impas), kasMinimum (Rp, 0 = mati), targetMargin { jenis: % } (tidak ada = bawaan 3 bulan), dariOwner }. */
export function klAtur() {
  const a = ugAturDok(KL_ID) || {}; const rp = (v) => { const n = Number(v); return isFinite(n) && n > 0 && n <= KL_RP_MAKS ? Math.round(n) : 0; };
  const tm = {}; KL_JENIS.forEach((j) => { const n = Number(a.targetMargin && a.targetMargin[j.id]); if (isFinite(n) && n > 0 && n <= KL_TARGET_MAKS) tm[j.id] = Math.round(n * 100) / 100; });
  return { targetHarian: rp(a.targetHarian), kasMinimum: rp(a.kasMinimum), targetMargin: tm, dariOwner: !!ugAturDok(KL_ID), tanggal: a.tanggal || '' };
}
/**
 * Simpan setelan. isi boleh berisi sebagian: { targetHarian, kasMinimum, targetMargin: { jenis: ketikan } } — kolom yang TIDAK dikirim tetap seperti tersimpan
 * (Menu menyimpan target & kas, Harga menyimpan target margin, tidak saling menimpa). Kosong = bawaan / mati. Ketikan rusak DITOLAK dengan kalimat (tidak dibulatkan diam-diam).
 */
export function susunAturKpi(isi, w) {
  const lama = ugAturDok(KL_ID) || {}; const data = Object.assign({}, lama, { id: KL_ID, tanggal: w.tanggal, jam: w.jam }); const ubah = [];
  const rupiah = (k, nama) => { if (!isi || !(k in isi)) return ''; const v = isi[k]; if (ugKosong(v)) { data[k] = 0; ubah.push(nama + ' kosong'); return ''; } const n = ugAngka(v);
    if (!(n >= 0) || n > KL_RP_MAKS || Math.round(n) !== n) return nama + ' ditulis dalam rupiah bulat, 0 sampai ' + RP(KL_RP_MAKS); data[k] = n; ubah.push(nama + ' ' + (n ? RP(n) : 'kosong')); return ''; };
  let tolak = rupiah('targetHarian', 'Target omzet harian') || rupiah('kasMinimum', 'Ambang kas minimum');
  if (!tolak && isi && isi.targetMargin) { const tm = Object.assign({}, lama.targetMargin || {});
    KL_JENIS.forEach((j) => { if (tolak || !(j.id in isi.targetMargin)) return; const v = isi.targetMargin[j.id]; if (ugKosong(v)) { delete tm[j.id]; ubah.push('target ' + j.nama.toLowerCase() + ' bawaan'); return; }
      const n = ugAngka(v); if (!(n > 0) || n > KL_TARGET_MAKS) { tolak = 'Target margin ' + j.nama.toLowerCase() + ' ditulis dalam persen: lebih dari 0 sampai ' + KL_TARGET_MAKS + ' (2,5 = 2,5 %) — kosong = bawaan 3 bulan'; return; }
      tm[j.id] = Math.round(n * 100) / 100; ubah.push('target ' + j.nama.toLowerCase() + ' ' + klPctTeks(tm[j.id])); });
    data.targetMargin = tm; }
  if (tolak) return { tolak };
  if (!ubah.length) return { tolak: 'Tidak ada yang diubah' };
  return { dokumen: [{ koleksi: 'aturanToko', data }], patch: { aturKpi: null, kabar: 'Setelan tersimpan — ' + ubah.join(' · '), kabarAwas: false } };
}

// ---------- 1 · 2 · 3 · 5 : tiga margin satu bulan ----------
const KL_KATA_PAJAK = /(^|[^a-z])(pph|pajak)([^a-z]|$)/i;
/** Uang keluar toko bulan itu yang keterangannya menyebut pajak / PPh — SUDAH ada di biaya toko (mesin), jadi tidak dipotong lagi di baris "sesudah PPh". */
export function klPajakDiBiaya(key) {
  const awal = key + '-01', akhir = akhirBulanIso(key); let rp = 0, n = 0;
  ambilPengeluaranHarian().forEach((h) => { if (!(h.kategori === 'toko' || h.kategori === 'tokoDompet') || !h.tanggal || h.tanggal < awal || h.tanggal > akhir || !KL_KATA_PAJAK.test(String(h.keterangan || ''))) return; rp += Number(h.nominal) || 0; n += 1; });
  return { rp, n };
}
/**
 * Tiga margin satu bulan + per jenis + pembanding BPS. Semua rupiah dari keManaLabaKotor (kartu "Laba kotor → ke mana", mesin laba Laporan) dan jenisBulan
 * (Per jenis). menutup = identitas laba usaha → laba bersih benar sampai rupiah DAN per jenis menutup ke laba kotor (bila rinciannya ada).
 */
export function klMarginBulan(key, kini) {
  const K = keManaLabaKotor(key, kini); const L = K.L || {}; const omzet = Number(L.omzetHitung) || 0;
  const mdr = K.pilah && isFinite(Number(K.pilah.mdr)) ? Number(K.pilah.mdr) : 0; const lk = Number(L.lebihKurangKas) || 0;
  // aset tetap (owner 26 Nov 2026): penyusutan = biaya usaha; uang keluar yang dipindah jadi aset bukan biaya lagi (asetEA = 0 tanpa aset)
  const asetPen = Number(L.penyusutan) || 0, asetDari = Number(L.asetDariBiaya) || 0;
  const labaKotor = K.labaKotor; const labaUsaha = K.labaKotor - K.biayaToko - K.biayaKaryawan + K.susut - asetPen + asetDari; const labaBersih = K.labaBersih;
  const identitas = { usaha: labaUsaha, hapus: K.hapusBuku, lebihKurang: lk, bersih: labaBersih, beda: labaUsaha - K.hapusBuku + lk - labaBersih };
  const tutupUsaha = Math.abs(identitas.beda) < 0.5;
  // PPh final: perkiraan modul pajak (owner saja); yang sudah dibayar dari laci & dicatat sebagai uang keluar toko sudah memotong laba bersih
  let P = { pph: null, lengkap: false }; try { P = pjPerkiraanBulan(key, kini); } catch (e) { P = { pph: null, lengkap: false, galat: String((e && e.message) || e) }; }
  const D = klPajakDiBiaya(key); const pph = P.pph === null || P.pph === undefined ? null : Math.round(P.pph); const potong = pph === null ? null : Math.max(0, pph - D.rp);
  const sesudahPph = pph === null ? null : labaBersih - potong;
  const J = jenisBulan(key, kini); const jenis = J.diarsip ? [] : J.jenis.map((g) => ({ id: g.id, nama: g.nama, omzet: g.omzet, margin: g.margin, pct: g.pct, markup: klMarkup(g.pct), keadaan: g.keadaan, kg: g.kg, nBaris: g.nBaris }));
  const ecer = J.diarsip ? null : J.jenis.filter((g) => g.id !== 'karung').reduce((a, g) => ({ omzet: a.omzet + g.omzet, margin: a.margin + (g.margin || 0), ada: a.ada || g.margin !== null }), { omzet: 0, margin: 0, ada: false });
  const grosir = J.diarsip ? null : J.jenis.find((g) => g.id === 'karung');
  const pctGrosir = grosir && grosir.margin !== null ? klPct(grosir.margin, grosir.omzet) : null; const pctEcer = ecer && ecer.ada ? klPct(ecer.margin, ecer.omzet) : null;
  const tangga = [
    { id: 'kotor', nama: 'Margin laba kotor', rp: labaKotor, pct: klPct(labaKotor, omzet), ket: 'laba kotor ÷ omzet ber-HPP' },
    { id: 'usaha', nama: 'Margin laba usaha', rp: labaUsaha, pct: klPct(labaUsaha, omzet), ket: 'laba kotor − biaya toko − biaya karyawan − potongan QRIS − susut & selisih stok' + (asetPen || asetDari ? ' − penyusutan aset tetap' + (asetDari ? ' + uang keluar yang jadi aset' : '') : '') },
    { id: 'bersih', nama: 'Margin laba bersih', rp: labaBersih, pct: klPct(labaBersih, omzet), ket: 'laba bersih mesin (Laporan › Laba)' },
  ].concat(pph === null ? [] : [{ id: 'pph', nama: 'Sesudah perkiraan PPh final', rp: sesudahPph, pct: klPct(sesudahPph, omzet), ket: PJ_LABEL + ' · PPh ' + RP(pph) + (D.rp ? ' − sudah dicatat di uang keluar ' + RP(D.rp) + ' = dipotong ' + RP(potong) : '') + (P.lengkap ? '' : ' · omzet tahun ini belum lengkap') }]);
  tangga.forEach((t) => { t.markup = klMarkup(t.pct); });
  const rincianUsaha = [['Laba kotor', labaKotor], ['Biaya toko (tanpa potongan QRIS)', -(K.biayaToko - mdr)], ['Biaya karyawan', -K.biayaKaryawan]].concat(mdr ? [['Potongan QRIS', -mdr]] : []).concat([['Susut & selisih stok', K.susut]]).concat(asetDari ? [['Uang keluar dipindah jadi aset tetap', asetDari]] : []).concat(asetPen ? [['Penyusutan aset tetap', -asetPen]] : []).concat([['Laba usaha', labaUsaha]])
    .concat(K.hapusBuku ? [['Hapus buku piutang', -K.hapusBuku]] : []).concat(lk ? [['Lebih/kurang kas', lk]] : []).concat([['Laba bersih', labaBersih]]).map((r) => ({ nama: r[0], n: r[1] }));
  return { key, nama: K.nama || lpNamaBulan(key), berjalan: K.berjalan, final: K.final, diarsip: !!K.diarsip, tanpaCatatan: !!K.tanpaCatatan, omzet, omzetTanpaHpp: Number(L.omzetTanpaHpp) || 0,
    labaKotor, labaUsaha, labaBersih, mdr, pph, pajakDiBiaya: D, potongPph: potong, sesudahPph, tangga, rincianUsaha, identitas, tutupUsaha,
    jenis, jenisMenutup: J.diarsip ? null : J.menutup, jenisKalimat: J.kalimat, jenisArsip: !!J.diarsip,
    bps: { grosir: KL_BPS.grosir, eceran: KL_BPS.eceran, tokoGrosir: pctGrosir, tokoEcer: pctEcer, markupGrosir: klMarkup(pctGrosir), markupEcer: klMarkup(pctEcer), sumber: KL_BPS.sumber, pendek: KL_BPS.pendek },
    menutup: tutupUsaha && (J.diarsip || J.menutup === true), sumber: 'Laporan › Laba (laba kotor → ke mana · per jenis)' };
}

// ---------- 4 · target margin per jenis & saran harga di katalog ----------
const klGeserBulan = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; const d = new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)); return d.toISOString().slice(0, 7); };
/** Target margin per jenis: owner (aturanToko/kpiLaba) atau BAWAAN = margin terwujud 3 bulan terakhir (awal bulan ke-2 sebelum ini → hari ini) dari mesin. */
export function klTargetMargin(kini) { const iso = hariIniIso(kini); return ingatPerVersi('klTargetMargin|' + iso, () => klTargetMarginHitung(iso)); }
function klTargetMarginHitung(iso) {
   const dari = klGeserBulan(iso.slice(0, 7), -2) + '-01'; const A = klAtur(); const R = lpJenisRentang(dari, iso);
  const out = {}; KL_JENIS.forEach((j) => { const g = R.jenis.find((x) => x.id === j.id); const bawaan = g && g.margin !== null && g.omzet > 0 ? g.margin / g.omzet * 100 : null;
    const own = A.targetMargin[j.id]; out[j.id] = { id: j.id, nama: j.nama, pct: own !== undefined ? own : bawaan, dariOwner: own !== undefined, bawaan, bawaanTeks: bawaan === null ? 'belum ada jualan ber-modal 3 bulan ini' : 'margin terwujud ' + klPctTeks(bawaan) + ' (' + tanggalPendek(dari) + ' – ' + tanggalPendek(iso) + ')' }; });
  return { dari, sampai: iso, jenis: out, menutup: R.menutup };
}
/** Jenis yang digerakkan satu baris katalog: literan · kemasan (< 25 kg) · karung (karung utuh ≥ 25 kg) · per kg = repack (+ karung utuh bila merek itu tanpa harga karung utuh sendiri). */
export function klJenisKatalog(b, adaKarungUtuh) {
  const id = String(b && b.st ? b.st.id : ''); if (id === 'L') return ['literan']; if (id === 'S') return adaKarungUtuh ? ['repack'] : ['repack', 'karung'];
  const u = Number(id.slice(1)); return u >= 25 ? ['karung'] : ['kemasan'];
}
/**
 * Saran per baris katalog Harga (hgSemua): margin & mark-up harga sekarang (dari modal satuan yang SAMA dengan katalog) + harga saran tiap jenis yang digerakkannya.
 * T = klTargetMargin(kini). Tanpa modal / tanpa target = tanpa saran (disebut). Harga TIDAK berubah — ini cuma saran.
 */
export function klSaranBaris(b, T, S) {
  const atur = (S && S.atur) || aturHarga(); const ku = S && S.baris ? S.baris.some((x) => x.merk === b.merk && x.st.id !== 'S' && x.st.id !== 'L' && Number(x.st.id.slice(1)) >= 25 && x.n > 0) : false;
  const pctKini = b.modalUnit > 0 && b.n > 0 ? (b.n - b.modalUnit) / b.n * 100 : null;
  const saran = klJenisKatalog(b, ku).map((jid) => { const t = T.jenis[jid]; const h = t && t.pct !== null ? klHargaSaran(b.modalUnit, t.pct, atur[b.st.bulat]) : null;
    const satu = b.st.id === 'S' && jid === 'karung' ? 50 : 1;   // harga karung utuh dari harga per kg × 50 kg (hargaKarungUtuh mesin)
    return { jenis: jid, nama: t ? t.nama : jid, target: t ? t.pct : null, dariOwner: !!(t && t.dariOwner), markup: klMarkup(t ? t.pct : null), harga: h, beda: h !== null && b.n > 0 ? h - b.n : null, karungUtuh: satu === 50 ? (h !== null ? h * 50 : null) : null }; });
  return { k: b.k, modal: b.modalUnit, harga: b.n, pctKini, markupKini: klMarkup(pctKini), saran, tanpaModal: !(b.modalUnit > 0) };
}

// ---------- 6 · GMROI per merek ----------
/** Laba kotor merek bulan itu (merekBulan) ÷ rata-rata nilai stok merek di bulan itu (umNilaiRata — buku per tanggal, sampai hari ini untuk bulan berjalan). */
export function klGmroi(key, kini) { const iso = hariIniIso(kini); return ingatPerVersi('klGmroi|' + key + '|' + iso, () => klGmroiHitung(key, kini)); }
function klGmroiHitung(key, kini) {
  const M = merekBulan(key, kini); const iso = hariIniIso(kini); const awal = key + '-01'; const akhir = akhirBulanIso(key); const sampai = akhir < iso ? akhir : iso;
  if (M.diarsip) return { key, nama: M.nama, diarsip: true, daftar: [], kalimat: M.kalimat };
  if (sampai < awal) return { key, nama: M.nama, daftar: [], kalimat: 'Bulan ini belum mulai' };
  const S = umNilaiRata(awal, sampai); const nilai = {}; Object.keys(S.buku).forEach((k) => { const m = lpMerekBuku(k); if (!m) return; const o = nilai[m] || (nilai[m] = { rp: 0, kg: 0 }); o.rp += S.buku[k].rp; o.kg += S.buku[k].kg; });
  let lk = 0, ln = 0; const daftar = M.merek.map((g) => { const v = nilai[g.merek] || { rp: 0, kg: 0 }; const gm = g.margin !== null && v.rp > 0.5 ? g.margin / v.rp : null; if (gm !== null) { lk += g.margin; ln += v.rp; }
    return { merek: g.merek, laba: g.margin, nilaiRata: v.rp, kgRata: v.kg, gmroi: gm, keadaan: g.margin === null ? 'tanpaLaba' : v.rp > 0.5 ? 'ada' : 'tanpaStok' }; })
    .sort((a, b) => (b.gmroi === null ? -1e9 : b.gmroi) - (a.gmroi === null ? -1e9 : a.gmroi) || a.merek.localeCompare(b.merek));
  const total = ln > 0 ? lk / ln : null;
  return { key, nama: M.nama, berjalan: M.berjalan, dari: awal, sampai, nHari: S.n, daftar, total, labaDihitung: lk, nilaiDihitung: ln,
    kalimat: total === null ? 'GMROI belum bisa dihitung — belum ada merek yang punya laba kotor dan stok bulan ini' : 'Tiap Rp1.000 modal yang rata-rata tertanam di stok menghasilkan ' + RP(Math.round(total * 1000)) + ' laba kotor dalam ' + S.n + ' hari (' + tanggalPendek(awal) + ' – ' + tanggalPendek(sampai) + ')' };
}
/** GMROI untuk layar: "0,42×" (laba kotor per Rp1 stok sebulan). */
export const klGmroiTeks = (g) => (g === null || g === undefined || !isFinite(g) ? '—' : String(Math.round(g * 100) / 100).replace('.', ',') + '×');

// ---------- 7 · siklus uang ----------
/** Hari stok + hari bon pelanggan tertagih − hari bayar pemasok. Bagian yang belum bisa dihitung DISEBUT (keadaan 'belum'), tidak dianggap 0. */
export function klSiklusUang(kini) {
  const U = umRingkas(kini); const T = tertagihBon(kini); const B = bpHariBayar(kini, T.hari);
  const hariStok = U.putaranMerek > 0 && U.periode && U.periode.n > 0 ? U.periode.n / U.putaranMerek : null;
  const bagian = [{ id: 'stok', nama: 'Hari stok', hari: hariStok, tanda: 1, ket: hariStok === null ? 'perputaran belum bisa dihitung' : 'periode ' + U.periode.n + ' hari ÷ perputaran ' + String(Math.round(U.putaranMerek * 10) / 10).replace('.', ',') + '×', sumber: 'Stok › Umur & putaran', tujuan: { ke: 'stok', tab: 'umur' } },
    { id: 'tagih', nama: 'Hari bon pelanggan tertagih', hari: T.rataHari, tanda: 1, ket: T.rataHari === null ? 'belum ada bon yang lunas ditagih' : T.tertagih.n + ' bon lunas, ' + T.hari + ' hari terakhir (penjualan tunai tidak ikut)', sumber: 'Pelanggan › Bon', tujuan: { ke: 'pelanggan', keluarga: 'bon' } },
    { id: 'bayar', nama: 'Hari bayar pemasok', hari: B.rataHari, tanda: -1, ket: B.rataHari === null ? 'belum ada pembayaran bon pemasok yang menunjuk bonnya' : B.total.n + ' pembayaran, ' + B.hari + ' hari terakhir', sumber: 'Harga & Pemasok › Bon pemasok', tujuan: { ke: 'harga', keluarga: 'bon' } }];
  const kurang = bagian.filter((x) => x.hari === null); const hari = kurang.length ? null : bagian.reduce((a, x) => a + x.tanda * x.hari, 0);
  return { hari, bagian, keadaan: kurang.length ? 'belum' : 'ada', kurang: kurang.map((x) => x.nama),
    kalimat: hari === null ? 'Siklus uang belum bisa dihitung — ' + kurang.map((x) => x.nama.toLowerCase() + ': ' + x.ket).join(' · ')
      : 'Uang toko berputar ±' + String(Math.round(hari * 10) / 10).replace('.', ',') + ' hari: beras ' + klHari(hariStok) + ' di rak + bon ' + klHari(T.rataHari) + ' baru tertagih − pemasok dibayar ' + klHari(B.rataHari) + ' sesudah datang' };
}
const klHari = (h) => (h === null || !isFinite(h) ? '—' : String(Math.round(h * 10) / 10).replace('.', ',') + ' hari');

// ---------- 8 · omzet hari ini vs target harian ----------
/** Bagian hari toko yang sudah lewat (jam cincin Ringkasan JAM_BUKA–JAM_TUTUP, WIB perangkat): 0 sebelum buka, 1 sesudah tutup. */
export function klBagianHari(kini) { const d = new Date(kini || Date.now()); const j = d.getHours() + d.getMinutes() / 60; return Math.max(0, Math.min(1, (j - JAM_BUKA) / (JAM_TUTUP - JAM_BUKA))); }
/**
 * Omzet hari ini (rekapHari — Laporan › Harian) dibanding target harian owner, atau BAWAAN omzet impas per hari (titikImpas — Laporan › Biaya).
 * Lampu: HIJAU = target tercapai · KUNING = belum tercapai tapi sesuai laju jam (omzet ≥ target × bagian hari yang lewat) · MERAH = di bawah laju.
 * Laju jam supaya pagi hari tidak selalu merah (alarm yang selalu menyala akan diabaikan).
 */
export function klTargetHari(kini) {
  const iso = hariIniIso(kini); const R = rekapHari(iso); const A = klAtur(); let bawaan = null, bawaanTeks = '';
  try { const K = kendaliBulan(iso.slice(0, 7), kini); const T = titikImpas(K, kini); bawaan = T.omzetImpasHari; bawaanTeks = bawaan === null ? 'omzet impas belum bisa dihitung (' + T.teks + ')' : 'omzet impas per hari ' + RP(bawaan) + ' (Laporan › Biaya)'; } catch (e) { bawaanTeks = 'omzet impas galat: ' + String((e && e.message) || e); }
  const target = A.targetHarian > 0 ? A.targetHarian : bawaan; const omzet = R.omzet || 0; const bagian = klBagianHari(kini);
  if (!(target > 0)) return { iso, omzet, target: null, dariOwner: false, lampu: 'tanpa', bawaan, bawaanTeks, teks: 'Target harian belum ada — ' + bawaanTeks + '. Atur di Menu › Toko ini › Target & ambang.', sumber: 'Laporan › Harian', tujuan: { ke: 'laporan', keluarga: 'harian', hari: iso } };
  const laju = Math.round(target * bagian); const lampu = omzet >= target ? 'hijau' : omzet >= laju ? 'kuning' : 'merah';
  return { iso, omzet, target, dariOwner: A.targetHarian > 0, bawaan, bawaanTeks, bagian, laju, persen: klPct(omzet, target), kurang: Math.max(0, target - omzet), lampu, sumber: 'Laporan › Harian', tujuan: { ke: 'laporan', keluarga: 'harian', hari: iso },
    teks: lampu === 'hijau' ? 'Target ' + RP(target) + ' tercapai — omzet ' + RP(omzet) + ' (' + klPctTeks(klPct(omzet, target)) + ')' : lampu === 'kuning' ? 'Sesuai laju jam: ' + RP(omzet) + ' dari ' + RP(target) + ' — kurang ' + RP(target - omzet) + ' sampai tutup'
      : 'Di bawah laju jam: ' + RP(omzet) + ', seharusnya sudah ±' + RP(laju) + ' dari target ' + RP(target) + ' — kurang ' + RP(target - omzet),
    targetTeks: A.targetHarian > 0 ? 'target owner' : 'bawaan: ' + bawaanTeks };
}

// ---------- 9 · ambang kas minimum ----------
/** Kas = saldoKantong layar Uang, keempat tempat (laci + brankas + rekening + amplop). Ambang 0 = mati. Titik kas belum disetel = belum bisa dibandingkan (disebut). */
export function klKasMinimum() {
  const A = klAtur(); const S = saldoKantong(); const tempat = ['laci', 'brankas', 'rekening', 'amplop'].map((id) => ({ id, nama: ugNamaTempat(id), n: S.ada ? S[id] : null }));
  if (!(A.kasMinimum > 0)) return { nyala: false, batas: 0, kas: S.ada ? S.total : null, tempat, teks: 'Ambang kas minimum mati — atur di Menu › Toko ini › Target & ambang', sumber: 'Uang › Pindah uang' };
  if (!S.ada) return { nyala: true, batas: A.kasMinimum, kas: null, tempat, bawah: null, teks: 'Kas belum bisa dibandingkan — titik kas belum disetel (Uang › Tutup hari)', sumber: 'Uang › Pindah uang' };
  const bawah = S.total < A.kasMinimum;
  return { nyala: true, batas: A.kasMinimum, kas: S.total, tempat, bawah, kurang: bawah ? A.kasMinimum - S.total : 0, titik: S.teksTitik, sumber: 'Uang › Pindah uang', tujuan: { ke: 'uang', keluarga: 'pindah' },
    teks: bawah ? 'Kas ' + RP(S.total) + ' DI BAWAH ambang ' + RP(A.kasMinimum) + ' — kurang ' + RP(A.kasMinimum - S.total) + ' (laci + brankas + rekening + amplop)' : 'Kas ' + RP(S.total) + ' di atas ambang ' + RP(A.kasMinimum) };
}

// ---------- 11 · bon dalam kg beras ----------
/** Modal per kg stok karung sekarang = Σ (sisa × modal per kg buku) ÷ Σ sisa — nilai yang sama dengan neraca (hppTerakhirPerKg). null bila tak ada stok. */
export function klModalPerKg() {
  const B = ingatStokKarung(); let kg = 0, rp = 0; Object.keys(B).forEach((k) => { const x = B[k]; const s = Number(x.sisaKg) || 0; if (!(s > 0)) return; kg += s; rp += s * (Number(x.hppTerakhirPerKg) || 0); });
  return { kg, rp, perKg: kg > 0 && rp > 0 ? rp / kg : null };
}
/** "bon Rp X ≈ Y kg beras pada modal Rp Z/kg". */
export function klBonKg(rp, M) {
  const m = M || klModalPerKg(); const n = Number(rp) || 0; if (!(m.perKg > 0)) return { rp: n, kg: null, perKg: null, teks: '' };
  const kg = n / m.perKg; return { rp: n, kg, perKg: m.perKg, teks: 'bon ' + RP(n) + ' ≈ ' + ANGKA(Math.round(kg)) + ' kg beras pada modal ' + RP(Math.round(m.perKg)) + '/kg' };
}

// ---------- 12 · kedatangan lewat batas HPP ----------
/** Kedatangan bulan itu yang HPP per kg-nya lebih dari batas owner (ckHppLewat, Barang masuk). */
export function klHppLewatBulan(key) { const L = ckHppLewat(key + '-01', akhirBulanIso(key)); return Object.assign({ key, nama: lpNamaBulan(key) }, L); }

// ---------- 10 · nota terbesar hari / minggu / bulan ----------
export const KL_RENTANG_NOTA = [['hari', 'Hari ini'], ['minggu', '7 hari'], ['bulan', 'Bulan ini']];
/** 10 nota terbesar (rwTerbesar — nota yang sama dengan Jual › Riwayat). rentang: hari | minggu (7 hari s.d. hari ini) | bulan (sejak tanggal 1). */
export function klNotaTerbesar(rentang, kini, n) {
  const iso = hariIniIso(kini); const geser = (d, k) => new Date(Date.UTC(+d.slice(0, 4), +d.slice(5, 7) - 1, +d.slice(8, 10) + k)).toISOString().slice(0, 10);
  const dari = rentang === 'minggu' ? geser(iso, -6) : rentang === 'bulan' ? iso.slice(0, 8) + '01' : iso;
  return Object.assign({ rentang: KL_RENTANG_NOTA.some((x) => x[0] === rentang) ? rentang : 'hari' }, rwTerbesar(dari, iso, n || 10));
}

// ---------- 15 · lama pemenuhan pesanan (ringkas untuk Dasbor) ----------
export const klLamaPesanan = (kini) => poLamaPenuhi(kini, 90);
export { bpHariTeks };
/** Setelan owner tersimpan apa adanya (untuk lembar Atur). */
export const klDokAtur = () => cacheMentah('aturan').find((d) => String(d.id) === KL_ID) || null;
