// PONDASI (owner 24 Nov 2026 — dari catatan owner "Pondasi bisnis": usaha runtuh saat naik tingkat karena yang dibesarkan cuma omzet, sedangkan keuangan,
// organisasi & rantai pasoknya tidak ikut dikuatkan). Logika TANPA DOM, nama berawalan pd (bundel uji jsc satu lingkup). Dijaga alat-uji/uji_pondasi.py.
//
// ATURAN (sama dengan kpi-laba-logika): tiap angka di sini MEMANGGIL fungsi sumber yang sudah dipakai layar lain dan menyebut sumbernya; mesin uang
// (baru/js/mesin/*, laba bersih, arus kas, neraca) TIDAK disentuh. Modul ini HANYA MEMBACA dan membandingkan. Satu-satunya tulisan = setelan ambang owner
// (aturanToko/pondasi). Yang belum bisa dihitung DISEBUT "belum" — tidak dianggap 0, tidak diberi warna.
//
// Delapan lampu — satu pertanyaan: "pondasi toko kuat tidak untuk naik tingkat?"
//   1 utang dibanding harta        = kewajiban ÷ aset                                   — neracaPada (Laporan › Neraca)
//   2 bon yang segera jatuh tempo  = bon lewat tempo + jatuh ≤ N hari (setelan Bon pemasok) vs uang toko — susunBon (Harga & Pemasok › Bon pemasok)
//   3 kas cukup berapa hari        = uang toko ÷ biaya toko per hari (30 hari terakhir)  — neracaPada.kas · ugLabaBersih.biayaToko
//   4 hasil atas harta & modal     = laba bersih 30 hari ÷ aset, ÷ modal owner tertanam  — ugLabaBersih · neracaPada
//   5 ambil pribadi vs laba        = ambil pribadi 90 hari vs laba bersih 90 hari        — priveRentang · ugLabaBersih · aturKeluar (batas aman bulan ini)
//   6 laju tumbuh                  = omzet 30 hari vs 30 hari sebelumnya, dibanding gerak utang pemasok & uang toko — lpHariRentang · neracaPada dua tanggal
//   7 bergantung pada satu pemasok = porsi belanja pemasok terbesar, 90 hari             — daftarPemasok (kedatangan nyata)
//   8 prakiraan 30 hari [PERKIRAAN] = uang toko + gerak toko 30 hari terakhir sebelum bayar pemasok − bon jatuh tempo 30 hari
//                                    — neracaPada · uang 30 hari lalu (mesin, atau hitungan tutup hari: lpKasPadaTanggal) · modalTertanam · bpHariBayar · susunBon; ambang kuning = kas minimum owner (kpiLaba)
// Warna: yang berupa FAKTA hitung (uang tidak cukup untuk bon yang segera jatuh tempo, bon lewat tempo, ambil lebih besar dari laba, rugi) langsung berwarna; yang berupa KEBIJAKAN
// (berapa persen utang yang masih wajar, berapa hari kas minimal, berapa porsi satu pemasok) hanya berwarna bila owner mengisi ambangnya — tanpa itu
// angkanya tampil tanpa warna. "Kuning mendekati batas" = dalam PD_DEKAT % dari ambang owner.
import { neracaPada, lpHariRentang, hariTerakhir, lpPertama, lpKasPadaTanggal, lpKasAkhirBulan, daftarBulan, merekRentang } from './laporan-logika.js';
import { ugAturDok, ugAngka, ugKosong, ugLabaBersih, ugTambahHari, aturKeluar, priveBulan, priveRentang, modalTertanam } from './uang-logika.js';
import { susunBon as bpSusunBon, daftarPemasok, bpHariBayar, bpLamaKirim, tempoPemasok, bpHariTeks } from './bon-pemasok-logika.js';
import { rwPerOrang } from './riwayat-logika.js';
import { pelangganBulan } from './laba-pelanggan-logika.js';
import { semuaOrang } from './pelanggan-logika.js';
import { ngBuku } from './nego-logika.js';
import { riwayatTutup } from './tutup-hari-logika.js';
import { klAtur } from './kpi-laba-logika.js';
import { kendaliBulan } from './kendali-biaya-logika.js';
import { ssCekGudang, ssTargetKuartal, ssKuartalNama, ssKuartalKey, ssKuartalGeser, SS_TARGET_KUARTAL, ssTugas, ssPercobaan, ssDrafPercobaan, susunPercobaan, susunHapusPercobaan, SS_PERCOBAAN_MAKS } from './sistem-logika.js';
import { ambilTutupHari, ambilTitikKas, ingatPerVersi } from '../data/toko.js';
import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';

export const PD_ID = 'pondasi';
/** Jendela "sebulan" semua lampu: 30 hari terakhir / 30 hari ke depan. */
export const PD_HARI = 30;
/** Jendela belanja per pemasok & ambil pribadi vs laba: 90 hari terakhir. */
export const PD_HARI_PANJANG = 90;
/** "Mendekati batas" = dalam 10 % dari ambang owner. */
export const PD_DEKAT = 10;
/** Empat ambang kebijakan milik owner (aturanToko/pondasi). 0 / kosong = mati (lampunya tanpa warna). maks = penjaga salah ketik, bukan kebijakan. */
export const PD_ATUR = [
  { id: 'utangMaks', nama: 'Utang paling banyak', satuan: '% dari harta', maks: 1000, ket: 'lampu Utang dibanding harta merah bila lewat angka ini' },
  { id: 'kasHariMin', nama: 'Uang toko paling sedikit cukup', satuan: 'hari biaya', maks: 3650, ket: 'lampu Kas cukup berapa hari merah bila di bawah angka ini' },
  { id: 'hasilMin', nama: 'Laba bersih 30 hari paling sedikit', satuan: '% dari harta', maks: 100, ket: 'lampu Hasil atas harta kuning bila di bawah angka ini' },
  { id: 'pemasokMaks', nama: 'Belanja ke satu pemasok paling banyak', satuan: '% dari belanja', maks: 100, ket: 'lampu Bergantung pada satu pemasok merah bila lewat angka ini' },
  { id: 'pembeliMaks', nama: 'Omzet dari satu pembeli paling banyak', satuan: '% dari omzet', maks: 100, ket: 'kartu Pelanggan: pembeli terbesar merah bila lewat angka ini' }];
/** Yang tidak bisa diukur sistem — pertanyaan untuk owner, bukan lampu. */
export const PD_LUAR = [
  'Rekening toko sudah terpisah dari rekening pribadi? Selama masih satu, uang pribadi dan uang toko hanya terpisah lewat catatan ambil pribadi.',
  'Legalitas (NPWP, NIB, badan usaha) sudah ada? Bank dan pemasok besar memintanya saat toko mau naik tingkat.',
  'Uang yang dulu benar-benar ditanam sebelum sistem mulai mencatat tidak ada catatannya — hasil atas modal di sini memakai posisi toko pada hari pertama sistem mencatat (harta dikurangi utang menurut buku).'];

const pdBilangan = (n) => typeof n === 'number' && isFinite(n);
const pdSatu = (n) => String(Math.round(Math.abs(n) * 10) / 10).replace('.', ',');
/** Persen untuk layar: '—' = belum bisa dihitung (bukan 0). */
export const pdPctTeks = (p) => (!pdBilangan(p) ? '—' : (p < 0 ? '−' : '') + pdSatu(p) + ' %');
const pdJumlah = (d, f) => d.reduce((a, x) => a + (Number(f(x)) || 0), 0);
/** Lampu ambang ATAS (makin besar makin buruk) & ambang BAWAH (makin kecil makin buruk). Ambang 0 = tanpa warna. */
export const pdLampuAtas = (nilai, batas) => (!(batas > 0) ? 'tanpa' : nilai > batas ? 'merah' : nilai > batas * (1 - PD_DEKAT / 100) ? 'amber' : 'hijau');
export const pdLampuBawah = (nilai, batas) => (!(batas > 0) ? 'tanpa' : nilai < batas ? 'merah' : nilai < batas * (1 + PD_DEKAT / 100) ? 'amber' : 'hijau');
/** Hasil atas harta: rugi = merah (fakta); selain itu hanya berwarna bila owner mengisi ambangnya (di bawah ambang = kuning). */
export const pdLampuHasil = (laba, hasil, batas) => (laba < 0 ? 'merah' : batas > 0 ? (hasil < batas ? 'amber' : 'hijau') : 'tanpa');
/** Ambil pribadi: merah = ADA yang diambil dan jumlahnya lebih besar dari laba bersih masa yang sama (toko mengecil karena diambil); kuning = bulan ini lewat batas aman. */
export const pdLampuAmbil = (ambil, laba, lewatBulan) => (ambil > 0 && ambil > laba ? 'merah' : lewatBulan ? 'amber' : 'hijau');
/** Laju tumbuh: hanya dinilai bila omzet NAIK. merah = utang pemasok naik lebih cepat dari omzet DAN uang toko turun; kuning = salah satunya. */
export const pdLampuTumbuh = (tumbuh, utangCepat, kasTurun) => (!(tumbuh > 0) ? 'tanpa' : utangCepat && kasTurun ? 'merah' : utangCepat || kasTurun ? 'amber' : 'hijau');
/**
 * Prakiraan uang toko PD_HARI hari lagi. gerak = gerak toko PD_HARI hari terakhir SEBELUM bayar pemasok = perubahan uang toko, tanpa setoran / tarikan modal owner
 * (dModal), ditambah kembali yang sudah dibayarkan ke pemasok (bayar). kasDepan = uang sekarang + gerak − bon yang jatuh tempo (jatuh).
 */
export function pdKasDepan(kas0, kas1, dModal, bayar, jatuh) { const gerak = (kas0 - kas1) - dModal + bayar; return { gerak, kasDepan: kas0 + gerak - jatuh }; }
const pdAmbangTeks = (batas, kalimat) => (batas > 0 ? kalimat : 'ambang belum diatur — angkanya tampil tanpa warna');
const pdBelum = (id, nama, kenapa, sumber, tujuan) => ({ id, nama, lampu: 'tanpa', keadaan: 'belum', nilai: 'belum bisa', kalimat: kenapa, rinci: [], ambang: '', sumber, tujuan });

// ---------- setelan owner: aturanToko/pondasi ----------
/** { utangMaks, kasHariMin, hasilMin, pemasokMaks (0 = mati), dariOwner, tanggal }. */
export function pdAtur() {
  const a = ugAturDok(PD_ID) || {}; const out = { dariOwner: !!ugAturDok(PD_ID), tanggal: a.tanggal || '' };
  PD_ATUR.forEach((x) => { const n = Number(a[x.id]); out[x.id] = isFinite(n) && n > 0 && n <= x.maks ? Math.round(n * 100) / 100 : 0; });
  return out;
}
/** Draf lembar Atur: ketikan per ambang ('' = mati). */
export function pdDrafAtur() { const A = pdAtur(); const d = {}; PD_ATUR.forEach((x) => { d[x.id] = A[x.id] ? String(A[x.id]).replace('.', ',') : ''; }); return d; }
/** Simpan ambang. Kosong = mati. Ketikan rusak DITOLAK dengan kalimat (tidak dibulatkan diam-diam). Kolom yang tidak dikirim tetap seperti tersimpan. */
export function susunAturPondasi(isi, w) {
  const lama = ugAturDok(PD_ID) || {}; const data = Object.assign({}, lama, { id: PD_ID, tanggal: w.tanggal, jam: w.jam }); const ubah = []; let tolak = '';
  PD_ATUR.forEach((x) => {
    if (tolak || !isi || !(x.id in isi)) return;
    const v = isi[x.id]; const dulu = Number(lama[x.id]) || 0;
    if (ugKosong(v)) { if (dulu) ubah.push(x.nama.toLowerCase() + ' mati'); data[x.id] = 0; return; }
    const n = ugAngka(v);
    if (!(n > 0) || n > x.maks) { tolak = x.nama + ' ditulis dalam ' + x.satuan + ': lebih dari 0 sampai ' + x.maks + ' — kosong = mati'; return; }
    const bulat = Math.round(n * 100) / 100; data[x.id] = bulat; if (bulat !== dulu) ubah.push(x.nama.toLowerCase() + ' ' + String(bulat).replace('.', ',') + ' ' + x.satuan);
  });
  if (tolak) return { tolak };
  if (!ubah.length) return { tolak: 'Tidak ada yang diubah' };
  return pdSimpanAtur(data, { aturPd: null, kabar: 'Ambang pondasi tersimpan — ' + ubah.join(' · '), kabarAwas: false });
}
/** SATU pintu tulis modul ini: dokumen aturanToko/pondasi (ambang lampu + target kuartal dalam satu dokumen; kolom yang tidak disentuh ikut disalin). */
const pdSimpanAtur = (data, patch) => ({ dokumen: [{ koleksi: 'aturanToko', data }], patch });
export const PD_TARGET_MAKS = 100000000000;
/** Draf lembar "Atur target" satu kuartal: ketikan per target ('' = belum diisi). */
export function pdDrafTarget(key) { const T = ssTargetKuartal(key); const d = { key }; SS_TARGET_KUARTAL.forEach((x) => { d[x.id] = T[x.id] ? String(T[x.id]) : ''; }); return d; }
/**
 * Simpan target owner SATU kuartal ke aturanToko/pondasi.targetKuartal[key] — target kuartal lain & ambang lampu tidak tersentuh. Kosong = target itu dihapus.
 * Rupiah bulat lebih dari 0; ketikan rusak DITOLAK dengan kalimat. Hanya setelan: tidak ada uang, stok, atau laporan yang berubah.
 */
export function susunTargetKuartal(key, isi, w) {
  if (!/^\d{4}-K[1-4]$/.test(String(key))) return { tolak: 'Kuartal tidak dikenal' };
  const lama = ugAturDok(PD_ID) || {}; const semua = Object.assign({}, lama.targetKuartal && typeof lama.targetKuartal === 'object' ? lama.targetKuartal : {}); const dulu = ssTargetKuartal(key); const baru = {}; const ubah = []; let tolak = '';
  SS_TARGET_KUARTAL.forEach((x) => {
    if (tolak) return; const v = isi ? isi[x.id] : undefined;
    if (v === undefined) { if (dulu[x.id]) baru[x.id] = dulu[x.id]; return; }
    if (ugKosong(v)) { if (dulu[x.id]) ubah.push(x.nama.toLowerCase() + ' dihapus'); return; }
    const n = ugAngka(v); if (!(n > 0) || n > PD_TARGET_MAKS || Math.round(n) !== n) { tolak = x.nama + ' ditulis dalam rupiah bulat, lebih dari 0 — kosong = tidak ditarget'; return; }
    baru[x.id] = n; if (n !== dulu[x.id]) ubah.push(x.nama.toLowerCase() + ' ' + RP(n));
  });
  if (tolak) return { tolak };
  if (!ubah.length) return { tolak: 'Tidak ada yang diubah' };
  if (Object.keys(baru).length) semua[key] = baru; else delete semua[key];
  return pdSimpanAtur(Object.assign({}, lama, { id: PD_ID, tanggal: w.tanggal, jam: w.jam, targetKuartal: semua }), { aturTq: null, kabar: 'Target ' + ssKuartalNama(key) + ' tersimpan — ' + ubah.join(' · '), kabarAwas: false });
}

// ---------- sumber bersama: dihitung SEKALI per susunan, hanya saat lampunya memintanya ----------
function pdSumber(kini) {
  const iso = hariIniIso(kini); const h = (n) => ugTambahHari(iso, n); const simpan = {};
  const sekali = (k, f) => () => { if (!(k in simpan)) simpan[k] = f(); return simpan[k]; };
  return { kini, iso, h, A: pdAtur(),
    N0: sekali('N0', () => neracaPada(null, kini)),
    N1: sekali('N1', () => neracaPada(h(-PD_HARI), kini)),
    kas1: sekali('kas1', () => pdKasLalu(neracaPada(h(-PD_HARI), kini), h(-PD_HARI))),
    L30: sekali('L30', () => ugLabaBersih(h(-(PD_HARI - 1)), iso)),
    O30: sekali('O30', () => lpHariRentang(h(-(PD_HARI - 1)), iso)),
    B: sekali('B', () => bpSusunBon(kini)),
    bon30: sekali('bon30', () => pdBon30(bpSusunBon(kini))) };
}
/**
 * Uang toko PD_HARI hari lalu: dari mesin bila titik kas masih mencakup tanggal itu; kalau tidak (titik kas maju tiap tutup hari) dari hitungan fisik tutup hari
 * pada/sebelum tanggal itu — lpKasPadaTanggal (aturan kas akhir bulan Neraca). → { kas (null = belum bisa), kenapa, sumber }.
 */
function pdKasLalu(N1, iso) {
  const n = N1 && N1.N ? N1.N.kas : null; if (pdBilangan(n)) return { kas: n, kenapa: '', sumber: 'titik kas + gerakan sesudahnya' };
  const K = lpKasPadaTanggal(iso); return pdBilangan(K.kas) ? K : { kas: null, kenapa: K.kenapa || 'titik kas disetel sesudah tanggal itu', sumber: '' };
}
/** Bon pemasok bertempo yang jatuh tempo sampai PD_HARI hari lagi (yang sudah lewat ikut) + yang tanpa tempo (disebut, tidak dihitung). */
function pdBon30(B) {
  const jatuh = B.bon.filter((b) => b.jatuh && b.sisaHari !== null && b.sisaHari <= PD_HARI);
  return { n: jatuh.length, rp: pdJumlah(jatuh, (b) => b.sisa), nLewat: B.lewat.length, rpLewat: pdJumlah(B.lewat, (b) => b.sisa), nTanpa: B.tanpaTempo.length, rpTanpa: pdJumlah(B.tanpaTempo, (b) => b.sisa) };
}

// ---------- 1 · utang dibanding harta ----------
function pdUtang(X) {
  const id = 'utang', nama = 'Utang dibanding harta', sumber = 'Laporan › Neraca', tujuan = { ke: 'laporan', keluarga: 'neraca' }; const N = X.N0();
  if (!pdBilangan(N.aset)) return pdBelum(id, nama, N.tolak || 'Uang toko belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya.', sumber, tujuan);
  if (!(N.aset > 0)) return pdBelum(id, nama, 'Harta toko yang tercatat nol atau minus — perbandingannya tidak bisa dihitung.', sumber, tujuan);
  const pct = N.kewajiban / N.aset * 100; const batas = X.A.utangMaks; const kurang = N.kewajiban - N.aset;
  return { id, nama, keadaan: 'ada', pct, lampu: pdLampuAtas(pct, batas), nilai: pdPctTeks(pct),
    kalimat: 'Dari tiap Rp1.000 harta toko, ' + RP(Math.round(pct * 10)) + ' dibiayai utang. '
      + (kurang > 0 ? 'Kalau semua utang ditagih hari ini, harta yang tercatat belum cukup menutupnya — kurang ' + RP(kurang) + '.' : 'Sesudah semua utang dibayar masih tersisa ' + RP(-kurang) + '.'),
    rinci: [['Harta toko', RP(N.aset)], ['Utang ke pemasok', RP(N.N.utangPemasok)], ['Utang toko ke owner', RP(N.N.utangOwner)], ['Jumlah utang', RP(N.kewajiban)]],
    ambang: pdAmbangTeks(batas, 'ambang owner: paling banyak ' + pdPctTeks(batas) + ' dari harta'), sumber, tujuan };
}

// ---------- 2 · bon pemasok yang segera jatuh tempo vs uang toko ----------
// "Segera" = yang sudah lewat tempo + yang jatuh tempo sampai `dekatHari` hari lagi (setelan owner di Bon pemasok; = angka "jatuh ≤ N hari" di layar itu).
// Bon yang temponya masih lebih jauh dibayar dari penjualan sebelum temponya — itu urusan lampu Prakiraan, bukan lampu ini (kalau dibandingkan dengan uang
// hari ini saja, toko yang berjalan di atas tempo pemasok akan merah selamanya dan lampunya tidak dibaca lagi).
function pdBon(X) {
  const id = 'bon', nama = 'Bon pemasok yang segera jatuh tempo', sumber = 'Harga & Pemasok › Bon pemasok', tujuan = { ke: 'harga', keluarga: 'bon' }; const B = X.B(); const J = X.bon30();
  const dekat = B.atur.dekatHari; const nSegera = B.lewat.length + B.dekat.length; const rpSegera = pdJumlah(B.lewat.concat(B.dekat), (b) => b.sisa);
  const tanpa = J.nTanpa ? ' ' + J.nTanpa + ' bon tanpa tempo (' + RP(J.rpTanpa) + ') belum ikut dihitung — isi temponya di kartu pemasok.' : '';
  if (!B.bon.length) return { id, nama, keadaan: 'ada', lampu: 'hijau', nilai: 'tidak ada bon', kalimat: 'Tidak ada bon pemasok yang terbuka.', rinci: [], ambang: '', sumber, tujuan };
  if (!pdBilangan(B.kas)) return pdBelum(id, nama, 'Bon yang jatuh tempo sampai ' + dekat + ' hari lagi ' + RP(rpSegera) + ', tetapi ' + B.kasTeks + '.' + tanpa, sumber, tujuan);
  const sisa = B.kas - rpSegera; const kurang = rpSegera > 0 && sisa < 0; const lampu = J.nLewat || kurang ? 'merah' : J.nTanpa ? 'amber' : 'hijau';
  return { id, nama, keadaan: 'ada', lampu, nilai: kurang ? 'kurang ' + RP(-sisa) : J.nLewat ? J.nLewat + ' lewat tempo' : nSegera ? 'cukup' : 'belum ada yang dekat',
    kalimat: (nSegera ? 'Bon pemasok yang jatuh tempo sampai ' + dekat + ' hari lagi ' + RP(rpSegera) + ' (' + nSegera + ' bon' + (J.nLewat ? ', ' + J.nLewat + ' sudah LEWAT tempo ' + RP(J.rpLewat) : '') + '); uang toko sekarang ' + RP(B.kas) + ' — '
        + (kurang ? 'KURANG ' + RP(-sisa) + '.' : 'cukup, sisa ' + RP(sisa) + '.') : 'Tidak ada bon pemasok yang jatuh tempo sampai ' + dekat + ' hari lagi; uang toko sekarang ' + RP(B.kas) + '.')
      + (J.n > nSegera ? ' Sampai ' + PD_HARI + ' hari lagi jatuh tempo ' + RP(J.rp) + ' (' + J.n + ' bon) — dibayar dari penjualan sebelum temponya; lihat lampu Prakiraan.' : '') + tanpa,
    rinci: [['Uang toko sekarang', RP(B.kas)], ['Jatuh tempo ≤ ' + dekat + ' hari (termasuk yang lewat)', RP(rpSegera) + ' · ' + nSegera + ' bon'], ['Sudah lewat tempo', J.nLewat ? RP(J.rpLewat) + ' · ' + J.nLewat + ' bon' : 'tidak ada'],
      ['Jatuh tempo ≤ ' + PD_HARI + ' hari', RP(J.rp) + ' · ' + J.n + ' bon'], ['Tanpa tempo', J.nTanpa ? RP(J.rpTanpa) + ' · ' + J.nTanpa + ' bon' : 'tidak ada'], ['Semua bon terbuka', RP(B.total) + ' · ' + B.nBon + ' bon']],
    ambang: 'merah = ada bon lewat tempo, atau bon yang jatuh tempo ≤ ' + dekat + ' hari lebih besar dari uang toko · kuning = ada bon tanpa tempo · ' + dekat + ' hari = setelan "dekat" di Bon pemasok', sumber, tujuan };
}

// ---------- 3 · kas cukup berapa hari biaya ----------
function pdKasHari(X) {
  const id = 'kasHari', nama = 'Uang toko cukup berapa hari', sumber = 'Uang › Pindah uang · Laporan › Biaya', tujuan = { ke: 'uang', keluarga: 'pindah' }; const N = X.N0(); const kas = N.N ? N.N.kas : null;
  if (!pdBilangan(kas)) return pdBelum(id, nama, 'Uang toko belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya.', sumber, tujuan);
  const L = X.L30(); const biayaHari = (Number(L.biayaToko) || 0) / PD_HARI;
  if (!(biayaHari > 0)) return pdBelum(id, nama, 'Belum ada biaya toko yang tercatat dalam ' + PD_HARI + ' hari terakhir — lamanya tidak bisa dihitung.', sumber, tujuan);
  const hari = kas / biayaHari; const batas = X.A.kasHariMin; const lampu = kas <= 0 ? 'merah' : pdLampuBawah(hari, batas);
  return { id, nama, keadaan: 'ada', hari, lampu, nilai: kas <= 0 ? 'uang habis' : '±' + Math.floor(hari) + ' hari',
    kalimat: (kas <= 0 ? 'Uang toko ' + RP(kas) + ' — tidak ada yang tersisa untuk membayar biaya.' : 'Kalau besok tidak ada penjualan sama sekali, uang toko ' + RP(kas) + ' cukup membayar biaya toko ±' + Math.floor(hari) + ' hari')
      + (kas <= 0 ? '' : ' (biaya ±' + RP(Math.round(biayaHari)) + ' per hari, ' + PD_HARI + ' hari terakhir).') + ' Bon pemasok tidak ikut — lihat lampu Bon pemasok.',
    rinci: [['Uang toko (laci · brankas · rekening · amplop)', RP(kas)], ['Biaya toko ' + PD_HARI + ' hari terakhir', RP(L.biayaToko)], ['Biaya per hari', RP(Math.round(biayaHari))]],
    ambang: pdAmbangTeks(batas, 'ambang owner: paling sedikit ' + pdSatu(batas) + ' hari'), sumber, tujuan };
}

// ---------- 4 · hasil atas harta & modal owner ----------
function pdHasil(X) {
  const id = 'hasil', nama = 'Hasil atas harta & modal', sumber = 'Laporan › Laba · Laporan › Neraca', tujuan = { ke: 'laporan', keluarga: 'laba' }; const N = X.N0();
  if (!pdBilangan(N.aset) || !(N.aset > 0)) return pdBelum(id, nama, N.tolak || 'Harta toko belum bisa dihitung — titik kas belum disetel.', sumber, tujuan);
  const L = X.L30(); const laba = Number(L.labaBersih) || 0; const hasil = laba / N.aset * 100; const modal = Number(N.modal) || 0; const batas = X.A.hasilMin;
  const lampu = pdLampuHasil(laba, hasil, batas);
  // owner 24 Nov 2026 ("modal awal tulis aja dimulai 8 Agustus, karena sebelumnya gak ada catatan"): modal yang dibandingkan = POSISI TOKO saat sistem mulai
  // mencatat, DIHITUNG dari buku (kekayaan bersih sekarang − laba bersih kumulatif mesin + ambil pribadi = modal tercatat + beda "belum terjelaskan buku"
  // di Neraca) — tidak ditulis sebagai setoran modal (itu menaikkan uang toko). Posisi itu nol/minus → DISEBUT, hasil atas modal tidak dihitung.
  const mulai = lpPertama(); const dasar = pdBilangan(N.selisihBuku) ? modal + N.selisihBuku : null; const sejak = mulai ? tanggalPendek(mulai) : 'awal catatan';
  const atasModal = dasar === null ? ' Modal owner yang tercatat ' + RP(modal) + ' — posisi toko saat sistem mulai mencatat belum bisa dihitung, jadi hasil atas modal belum bisa dihitung.'
    : dasar > 0 ? ' Dibanding modal yang tertanam di toko ' + RP(dasar) + ' (posisi toko saat sistem mulai mencatat ' + sejak + ' menurut buku, termasuk setoran modal ' + RP(modal) + '): ' + pdPctTeks(laba / dasar * 100) + (laba > 0 ? ' — balik modal ±' + pdSatu(dasar / laba) + ' bulan kalau lajunya tetap.' : '.')
      : ' Saat sistem mulai mencatat (' + sejak + ') utang toko lebih besar ' + RP(-dasar) + ' dari hartanya menurut buku — tidak ada modal bersih untuk dibandingkan, jadi hasil atas modal tidak dihitung.';
  return { id, nama, keadaan: 'ada', pct: hasil, lampu, nilai: pdPctTeks(hasil),
    kalimat: (laba < 0 ? 'Toko RUGI ' + RP(-laba) + ' dalam ' + PD_HARI + ' hari terakhir.' : 'Tiap Rp1.000 harta toko menghasilkan ' + RP(Math.round(hasil * 10)) + ' laba bersih dalam ' + PD_HARI + ' hari (laba bersih ' + RP(laba) + ').') + atasModal,
    rinci: [['Laba bersih ' + PD_HARI + ' hari terakhir', RP(laba)], ['Harta toko', RP(N.aset)], ['Setoran modal owner yang tercatat', RP(modal)], ['Posisi toko saat sistem mulai mencatat (' + sejak + '), dihitung', dasar === null ? 'belum bisa dihitung' : RP(dasar)]],
    ambang: pdAmbangTeks(batas, 'ambang owner: paling sedikit ' + pdPctTeks(batas) + ' dari harta per ' + PD_HARI + ' hari') + ' · merah = rugi', sumber, tujuan };
}

// ---------- 5 · ambil pribadi vs laba (ekuitas pribadi vs ekuitas toko) ----------
function pdAmbil(X) {
  const id = 'ambil', nama = 'Ambil pribadi dibanding laba', sumber = 'Uang › Owner & toko · Laporan › Laba', tujuan = { ke: 'uang', keluarga: 'owner' };
  const awal = X.h(-(PD_HARI_PANJANG - 1)); const P90 = priveRentang(awal, X.iso); const L90 = ugLabaBersih(awal, X.iso); const laba = Number(L90.labaBersih) || 0; const tinggal = laba - P90.total;
  const A = aturKeluar(X.iso); const P = priveBulan(X.iso); const lewatBulan = P.total > A.aman;
  const lampu = pdLampuAmbil(P90.total, laba, lewatBulan); const ada = P90.total > 0;
  return { id, nama, keadaan: 'ada', lampu, nilai: !ada ? 'tidak ada ambil' : tinggal < 0 ? 'toko mengecil ' + RP(-tinggal) : 'tinggal ' + RP(tinggal),
    kalimat: PD_HARI_PANJANG + ' hari terakhir laba bersih toko ' + RP(laba) + (!ada ? '; owner tidak mengambil apa pun untuk pribadi.' : ' dan owner mengambil ' + RP(P90.total) + ' untuk pribadi — '
      + (tinggal >= 0 ? 'yang tinggal di toko ' + RP(tinggal) + '.' : laba < 0 ? 'toko sedang rugi dan tetap diambil: toko mengecil ' + RP(-tinggal) + '.' : 'yang diambil LEBIH BESAR ' + RP(-tinggal) + ' dari yang dihasilkan: toko mengecil.'))
      + ' Bulan ini diambil ' + RP(P.total) + ' dari batas aman ' + RP(A.aman) + ' (' + (A.amanDariLaba ? 'laba bersih bulan berjalan' : 'setelan owner') + ')' + (lewatBulan ? ' — LEWAT ' + RP(P.total - A.aman) + '.' : '.'),
    rinci: [['Laba bersih ' + PD_HARI_PANJANG + ' hari', RP(laba)], ['Ambil pribadi ' + PD_HARI_PANJANG + ' hari', RP(P90.total)], ['Tinggal di toko', RP(tinggal)], ['Ambil pribadi bulan ini', RP(P.total)], ['Batas aman bulan ini', RP(A.aman)]],
    ambang: 'merah = ada ambil pribadi ' + PD_HARI_PANJANG + ' hari dan jumlahnya lebih besar dari laba bersihnya · kuning = bulan ini lewat batas aman (Uang › Uang keluar)', sumber, tujuan };
}

// ---------- 6 · laju tumbuh: omzet naik ditopang apa ----------
function pdTumbuh(X) {
  const id = 'tumbuh', nama = 'Laju tumbuh', sumber = 'Laporan › Harian · Laporan › Neraca', tujuan = { ke: 'laporan', keluarga: 'bulanan' };
  const pertama = lpPertama(); const awalLalu = X.h(-(2 * PD_HARI - 1));
  if (!pertama || pertama > awalLalu) return pdBelum(id, nama, 'Butuh ' + (2 * PD_HARI) + ' hari catatan untuk membandingkan dua masa ' + PD_HARI + ' hari' + (pertama ? ' — catatan pertama ' + tanggalPendek(pertama) + '.' : ' — belum ada catatan.'), sumber, tujuan);
  const kini30 = Number(X.O30().omzetPenuh) || 0; const lalu30 = Number(lpHariRentang(awalLalu, X.h(-PD_HARI)).omzetPenuh) || 0;
  if (!(lalu30 > 0)) return pdBelum(id, nama, 'Tidak ada omzet di ' + PD_HARI + ' hari sebelumnya — lajunya tidak bisa dibandingkan.', sumber, tujuan);
  const tumbuh = (kini30 - lalu30) / lalu30 * 100; const N0 = X.N0(), N1 = X.N1(); const a = N0.N || {}, b = N1.N || {};
  const utangAda = pdBilangan(a.utangPemasok) && pdBilangan(b.utangPemasok); const dUtang = utangAda ? a.utangPemasok - b.utangPemasok : null;
  const tumbuhUtang = !utangAda ? null : b.utangPemasok > 0 ? dUtang / b.utangPemasok * 100 : dUtang > 0 ? Infinity : 0;
  const KL1 = X.kas1(); const kasAda = pdBilangan(a.kas) && pdBilangan(KL1.kas); const dKas = kasAda ? a.kas - KL1.kas : null; const dStok = pdBilangan(a.stok) && pdBilangan(b.stok) ? a.stok - b.stok : null;
  const gerak = (n) => (n === null ? 'belum bisa dihitung' : (n > 0 ? 'naik ' : n < 0 ? 'turun ' : 'tetap ') + (n ? RP(Math.abs(n)) : ''));
  let lampu = 'tanpa'; let inti = '';
  if (!(tumbuh > 0)) inti = tumbuh < 0 ? 'Omzet turun ' + pdPctTeks(-tumbuh) + ' — ini bukan soal tumbuh terlalu cepat.' : 'Omzet sama dengan ' + PD_HARI + ' hari sebelumnya.';
  else {
    const utangCepat = utangAda && dUtang > 0 && tumbuhUtang > tumbuh; const kasTurun = kasAda && dKas < 0;
    lampu = pdLampuTumbuh(tumbuh, utangCepat, kasTurun);
    inti = 'Omzet naik ' + pdPctTeks(tumbuh) + '. ' + (utangCepat && kasTurun ? 'Tumbuhnya ditopang utang: utang pemasok naik lebih cepat dari omzet DAN uang toko turun.' : utangCepat ? 'Utang pemasok naik lebih cepat dari omzet.' : kasTurun ? 'Omzet naik tetapi uang toko turun.' : 'Utang pemasok tidak melaju lebih cepat dari omzet dan uang toko tidak turun.');
  }
  return { id, nama, keadaan: 'ada', pct: tumbuh, lampu, nilai: (tumbuh > 0 ? '+' : '') + pdPctTeks(tumbuh),
    kalimat: inti + ' Dalam ' + PD_HARI + ' hari: utang pemasok ' + gerak(dUtang) + ', uang toko ' + gerak(dKas) + ', nilai stok ' + gerak(dStok) + '.' + (kasAda ? '' : ' Uang toko ' + PD_HARI + ' hari lalu belum bisa dihitung' + (KL1.kenapa ? ' (' + KL1.kenapa + ')' : '') + '.'),
    rinci: [['Omzet ' + PD_HARI + ' hari terakhir', RP(kini30)], ['Omzet ' + PD_HARI + ' hari sebelumnya', RP(lalu30)], ['Utang pemasok', gerak(dUtang) + (pdBilangan(tumbuhUtang) ? ' (' + pdPctTeks(tumbuhUtang) + ')' : '')], ['Uang toko', gerak(dKas)], ['Nilai stok', gerak(dStok)]],
    ambang: 'merah = omzet naik, utang pemasok naik lebih cepat DAN uang toko turun · kuning = salah satunya', sumber, tujuan };
}

// ---------- 7 · bergantung pada satu pemasok ----------
/** Porsi RUPIAH belanja beras per pemasok dalam [awal, akhir] (kedatangan nyata; yang di arsip tutup buku hanya dihitung jumlahnya). Terbesar dulu. */
export function pdPorsiPemasok(awal, akhir) {
  let total = 0, arsip = 0; const d = [];
  daftarPemasok().forEach((p) => { let rp = 0, n = 0;
    (p.batch || []).forEach((k) => { if (!k.tanggal || k.tanggal < awal || k.tanggal > akhir) return; if (k.arsip) { arsip += 1; return; } rp += Number(k.nilai) || 0; n += 1; });
    if (rp > 0) { d.push({ nama: p.nama, kunci: p.kunci, rp, n }); total += rp; } });
  d.sort((x, y) => y.rp - x.rp || x.nama.localeCompare(y.nama));
  return { awal, akhir, total, arsip, daftar: d, pct: total > 0 ? d[0].rp / total * 100 : null };
}
function pdPemasok(X) {
  const id = 'pemasok', nama = 'Bergantung pada satu pemasok', sumber = 'Harga & Pemasok › Bon pemasok', tujuan = { ke: 'harga', keluarga: 'bon' };
  const P = pdPorsiPemasok(X.h(-(PD_HARI_PANJANG - 1)), X.iso); const total = P.total, arsip = P.arsip, d = P.daftar;
  const ketArsip = arsip ? ' ' + arsip + ' kedatangan di tahun yang sudah ditutup buku tidak ikut (nilainya ada di arsip).' : '';
  if (!(total > 0)) return pdBelum(id, nama, 'Belum ada kedatangan beras bernilai dalam ' + PD_HARI_PANJANG + ' hari terakhir.' + ketArsip, sumber, tujuan);
  const atas = d[0]; const pct = P.pct; const batas = X.A.pemasokMaks;
  return { id, nama, keadaan: 'ada', pct, lampu: pdLampuAtas(pct, batas), nilai: pdPctTeks(pct),
    kalimat: 'Dari tiap Rp1.000 belanja beras ' + PD_HARI_PANJANG + ' hari terakhir, ' + RP(Math.round(pct * 10)) + ' ke ' + atas.nama + '. '
      + (d.length === 1 ? 'Seluruh belanja dari SATU pemasok — kalau ia berhenti mengirim atau menaikkan harga, toko tidak punya pilihan lain.' : d.length + ' pemasok mengirim dalam masa itu.') + ketArsip,
    rinci: d.slice(0, 5).map((x) => [x.nama, RP(x.rp) + ' · ' + pdPctTeks(x.rp / total * 100) + ' · ' + x.n + ' kedatangan']).concat([['Jumlah belanja', RP(total)]]),
    ambang: pdAmbangTeks(batas, 'ambang owner: paling banyak ' + pdPctTeks(batas) + ' ke satu pemasok'), sumber, tujuan };
}

// ---------- 8 · prakiraan 30 hari ke depan [PERKIRAAN] ----------
function pdDepan(X) {
  const id = 'depan', nama = 'Prakiraan ' + PD_HARI + ' hari ke depan', sumber = 'Laporan › Neraca · Harga & Pemasok › Bon pemasok', tujuan = { ke: 'harga', keluarga: 'bon' };
  const N0 = X.N0(); const KL1 = X.kas1(); const kas0 = N0.N ? N0.N.kas : null, kas1 = KL1.kas;
  if (!pdBilangan(kas0)) return pdBelum(id, nama, 'Uang toko belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya.', sumber, tujuan);
  if (!pdBilangan(kas1)) return pdBelum(id, nama, 'Uang toko ' + PD_HARI + ' hari lalu belum bisa dihitung (' + KL1.kenapa + ') — prakiraan butuh gerak uang ' + PD_HARI + ' hari penuh.', sumber, tujuan);
  const dModal = modalTertanam(X.iso) - modalTertanam(X.h(-PD_HARI)); const HB = bpHariBayar(X.kini, PD_HARI);
  const bayar = HB.total.rp + HB.saldoAwal.rp + HB.tanpaTunjuk.rp + HB.janggal.rp; const J = X.bon30();
  const G = pdKasDepan(kas0, kas1, dModal, bayar, J.rp); const gerak = G.gerak, kasDepan = G.kasDepan; const min = klAtur().kasMinimum;
  const lampu = kasDepan < 0 ? 'merah' : min > 0 && kasDepan < min ? 'amber' : 'hijau';
  const O = X.O30(); const L = X.L30();
  return { id, nama, keadaan: 'ada', perkiraan: true, kasDepan, lampu, nilai: '±' + RP(kasDepan),
    kalimat: '[PERKIRAAN] Kalau ' + PD_HARI + ' hari ke depan berjalan seperti ' + PD_HARI + ' hari terakhir (omzet ±' + RP(O.omzetPenuh) + ', laba bersih ±' + RP(L.labaBersih) + ') dan semua bon yang jatuh tempo dibayar, uang toko ' + PD_HARI + ' hari lagi ±' + RP(kasDepan)
      + (kasDepan < 0 ? ' — TIDAK CUKUP.' : min > 0 && kasDepan < min ? ' — di bawah kas minimum ' + RP(min) + '.' : '.') + (J.nTanpa ? ' ' + J.nTanpa + ' bon tanpa tempo (' + RP(J.rpTanpa) + ') belum ikut.' : ''),
    rinci: [['Uang toko sekarang', RP(kas0)], ['Uang toko ' + PD_HARI + ' hari lalu', RP(kas1) + ' · ' + KL1.sumber], ['Gerak toko ' + PD_HARI + ' hari terakhir, sebelum bayar pemasok', RP(gerak)], ['— uang toko berubah', RP(kas0 - kas1)], ['— setor / tarik modal owner (dikeluarkan)', RP(dModal)], ['— sudah dibayar ke pemasok (ditambah kembali)', RP(bayar)],
      ['Bon jatuh tempo ≤ ' + PD_HARI + ' hari', RP(J.rp) + ' · ' + J.n + ' bon'], ['Perkiraan uang toko ' + PD_HARI + ' hari lagi', RP(kasDepan)]],
    ambang: 'merah = perkiraan uang toko di bawah nol · kuning = di bawah kas minimum owner' + (min > 0 ? ' ' + RP(min) : ' (belum diatur — Menu › Toko ini › Target & ambang)') + ' · pinjaman owner ke toko ikut terhitung sebagai gerak toko', sumber, tujuan };
}

/** Urutan lampu di layar. */
export const PD_LAMPU = [['utang', 'Utang dibanding harta', pdUtang], ['bon', 'Bon pemasok yang segera jatuh tempo', pdBon], ['kasHari', 'Uang toko cukup berapa hari', pdKasHari], ['hasil', 'Hasil atas harta & modal', pdHasil],
  ['ambil', 'Ambil pribadi dibanding laba', pdAmbil], ['tumbuh', 'Laju tumbuh', pdTumbuh], ['pemasok', 'Bergantung pada satu pemasok', pdPemasok], ['depan', 'Prakiraan ' + PD_HARI + ' hari ke depan', pdDepan]];
export const PD_KATA_LAMPU = { merah: 'merah', amber: 'kuning', hijau: 'aman', tanpa: 'tanpa warna' };

/**
 * Delapan lampu pondasi untuk satu saat. Tiap lampu dibungkus: galat di satu lampu tampil sebagai kalimat di lampu itu, lampu lain tetap jalan.
 * → { iso, lampu: [{ id, nama, lampu 'merah'|'amber'|'hijau'|'tanpa', keadaan 'ada'|'belum'|'galat', nilai, kalimat, rinci [[nama, teks]], ambang, sumber, tujuan }],
 *     hitung { merah, amber, hijau, tanpa, belum }, kalimat, atur, luar }.
 */
export function pdPondasi(kini) {
  // mulus (pola ingatNeraca): hasilnya hanya bergantung pada data, hari & titik kas → diingat per versi; ketukan di layar (buka rincian, ganti tab) tidak
  // menghitung ulang neraca dua tanggal, laba 30 & 90 hari, dan bon. Hasil DIPAKAI BERSAMA — jangan diubah di tempat.
  return ingatPerVersi('pdPondasi|' + hariIniIso(kini) + '|' + JSON.stringify(ambilTitikKas()), () => pdPondasiHitung(kini));
}
function pdPondasiHitung(kini) {
  const X = pdSumber(kini);
  const lampu = PD_LAMPU.map(([id, nama, f]) => { try { return f(X); } catch (e) { if (typeof console !== 'undefined') console.error('pondasi ' + id, e);
    return { id, nama, lampu: 'tanpa', keadaan: 'galat', nilai: 'gagal dihitung', kalimat: 'Gagal dihitung: ' + String((e && e.message) || e), rinci: [], ambang: '', sumber: '', tujuan: null }; } });
  const hitung = { merah: 0, amber: 0, hijau: 0, tanpa: 0, belum: 0 }; lampu.forEach((l) => { hitung[l.lampu] += 1; if (l.keadaan !== 'ada') hitung.belum += 1; });
  const sebut = (w) => lampu.filter((l) => l.lampu === w).map((l) => l.nama.toLowerCase()).join(' · ');
  const kalimat = (hitung.merah ? hitung.merah + ' lampu merah: ' + sebut('merah') + '. ' : '') + (hitung.amber ? hitung.amber + ' lampu kuning: ' + sebut('amber') + '. ' : '')
    + (!hitung.merah && !hitung.amber ? 'Tidak ada lampu merah atau kuning. ' : '') + (hitung.tanpa ? hitung.tanpa + ' lampu tanpa warna' + (hitung.belum ? ' (' + hitung.belum + ' belum bisa dihitung)' : '') + '.' : '');
  return { iso: X.iso, lampu, hitung, kalimat: kalimat.trim(), atur: X.A, luar: PD_LUAR };
}

// ---------- disiplin dalam (organisasi): kebiasaan yang membuat angka di atas bisa dipercaya ----------
/**
 * Dua kebiasaan yang SUDAH dicatat sistem: tutup hari tiap malam berjualan (30 hari terakhir, tanpa hari ini & tanpa hari di tahun yang sudah ditutup buku) dan
 * cek mingguan gudang (ssCekGudang). Baca saja. → { baris: [{ id, nama, lampu, nilai, kalimat, sumber, tujuan }] }.
 */
export function pdDisiplin(kini) { return ingatPerVersi('pdDisiplin|' + hariIniIso(kini), () => pdDisiplinHitung(kini)); }
function pdDisiplinHitung(kini) {
  const H = hariTerakhir(kini, PD_HARI + 1).filter((d) => !d.hariIni && !d.diarsip && d.n > 0); const tutup = {}; ambilTutupHari().forEach((d) => { if (d && d.tanggal) tutup[String(d.tanggal)] = true; });
  const tanpa = H.filter((d) => !tutup[d.iso]); const G = ssCekGudang(kini);
  return { baris: [
    { id: 'tutup', nama: 'Tutup hari tiap malam', lampu: !H.length ? 'tanpa' : tanpa.length ? 'amber' : 'hijau', nilai: !H.length ? 'belum ada' : (H.length - tanpa.length) + ' dari ' + H.length + ' hari',
      kalimat: !H.length ? 'Belum ada hari berjualan dalam ' + PD_HARI + ' hari terakhir.' : tanpa.length ? tanpa.length + ' hari berjualan tidak ditutup malamnya: ' + tanpa.slice(0, 6).map((d) => tanggalPendek(d.iso).slice(0, 6).trim()).join(', ') + (tanpa.length > 6 ? ' …' : '') + '. Tanpa tutup hari, uang toko di lampu-lampu di atas hanya hitungan mesin, belum dicocokkan dengan uang sungguhan.'
        : 'Semua ' + H.length + ' hari berjualan ditutup malamnya — uang toko di lampu-lampu di atas sudah dicocokkan dengan hitungan laci.', sumber: 'Uang › Tutup hari', tujuan: { ke: 'uang', keluarga: 'tutup' } },
    { id: 'gudang', nama: 'Cek mingguan gudang', lampu: !G.terakhir ? 'amber' : G.sisa < 0 ? 'merah' : G.sisa === 0 ? 'amber' : 'hijau', nilai: !G.terakhir ? 'belum pernah' : G.sisa < 0 ? 'lewat ' + (-G.sisa) + ' hari' : 'terjaga',
      kalimat: G.teks + (G.terakhir && G.terakhir.masalah.length ? ' · cek terakhir menemukan: ' + G.terakhir.masalah.join(', ') : '') + '.', sumber: 'Menu · pengingat cek gudang', tujuan: { ke: 'menu' } }] };
}

// ==================== PAKET KEDUA (owner 24 Nov 2026): kekayaan dari waktu ke waktu · rantai pasok · risiko & prakiraan · organisasi ====================
const pdKunciIngat = (nama, kini) => nama + '|' + hariIniIso(kini) + '|' + JSON.stringify(ambilTitikKas());
/** Akhir bulan 'YYYY-MM' → 'YYYY-MM-DD' (tanpa mesin: hari sebelum tanggal 1 bulan berikutnya). */
export const pdAkhirBulan = (key) => { const t = Number(String(key).slice(0, 4)), m = Number(String(key).slice(5, 7)); return ugTambahHari((m === 12 ? t + 1 : t) + '-' + String(m === 12 ? 1 : m + 1).padStart(2, '0') + '-01', -1); };

// ---------- kekayaan toko dari waktu ke waktu ----------
/**
 * Harta, utang & kekayaan bersih tiap AKHIR BULAN sejak catatan pertama (bulan berjalan: hari ini), TERBARU dulu. Bulan lampau: neracaPada + kas dari hitungan
 * fisik tutup hari akhir bulan itu (lpKasAkhirBulan — aturan Neraca berkop). Bulan yang kasnya tidak bisa dihitung DISEBUT (ada = false + sebab).
 */
export function pdKekayaan(kini) { return ingatPerVersi(pdKunciIngat('pdKekayaan', kini), () => pdKekayaanHitung(kini)); }
function pdKekayaanHitung(kini) {
  const iso = hariIniIso(kini);
  const bulan = daftarBulan(kini, 18).map((b) => {
    const per = b.berjalan ? iso : pdAkhirBulan(b.key); let N = null, galat = '', KB = null;
    try { KB = b.berjalan ? null : lpKasAkhirBulan(b.key); N = b.berjalan ? neracaPada(null, kini) : neracaPada(per, kini, KB); } catch (e) { galat = String((e && e.message) || e); }
    if (!N || !pdBilangan(N.aset) || !pdBilangan(N.kewajiban)) return { key: b.key, nama: b.pendek, per, berjalan: !!b.berjalan, ada: false,
      kenapa: galat ? 'gagal dihitung: ' + galat : KB && KB.kas === null && KB.kenapa ? 'uang toko akhir bulan ini belum bisa dihitung — ' + KB.kenapa : (N && N.tolak) || 'uang toko akhir bulan itu belum bisa dihitung' };
    return { key: b.key, nama: b.pendek, per, berjalan: !!b.berjalan, ada: true, aset: N.aset, kewajiban: N.kewajiban, bersih: N.aset - N.kewajiban };
  });
  const ada = bulan.filter((b) => b.ada);
  bulan.forEach((b, i) => { if (!b.ada) return; const lalu = bulan.slice(i + 1).find((x) => x.ada); b.naik = lalu ? b.bersih - lalu.bersih : null; });
  const maks = Math.max(1, ...ada.map((b) => Math.max(Math.abs(b.aset), Math.abs(b.kewajiban))));
  const kini0 = ada[0] || null, awal0 = ada[ada.length - 1] || null; const ubah = kini0 && awal0 && kini0 !== awal0 ? kini0.bersih - awal0.bersih : null;
  return { bulan, maks, n: ada.length, ubah,
    kalimat: !kini0 ? 'Kekayaan toko belum bisa dihitung — titik kas belum disetel.' : ubah === null ? 'Baru satu titik yang bisa dihitung (' + kini0.nama + ') — belum ada pembanding.'
      : 'Sejak ' + awal0.nama + ' kekayaan bersih toko ' + (ubah >= 0 ? 'NAIK ' : 'TURUN ') + RP(Math.abs(ubah)) + ' (' + RP(awal0.bersih) + ' → ' + RP(kini0.bersih) + ').' };
}

// ---------- rantai pasok: per pemasok ----------
/**
 * Per pemasok: porsi belanja 90 hari (pdPorsiPemasok), lama kirim sejak dipesan (bpLamaKirim, 180 hari), gerak harga beli (harga beli terakhir vs kedatangan
 * sebelumnya per merek — riwayat harga kartu pemasok), tempo (tempoPemasok) & kebiasaan bayar. Pemasok tanpa kedatangan 180 hari tidak ditampilkan.
 */
export function pdRantai(kini) { return ingatPerVersi(pdKunciIngat('pdRantai', kini), () => pdRantaiHitung(kini)); }
function pdRantaiHitung(kini) {
  const iso = hariIniIso(kini); const h = (n) => ugTambahHari(iso, n); const P = pdPorsiPemasok(h(-(PD_HARI_PANJANG - 1)), iso); const K = bpLamaKirim(kini, 2 * PD_HARI_PANJANG); const batasLama = h(-(2 * PD_HARI_PANJANG - 1));
  const pemasok = daftarPemasok().filter((p) => (p.terakhir || '') >= batasLama).map((p) => {
    const porsi = P.daftar.find((x) => x.kunci === p.kunci) || null; const kirim = K.pemasok.find((x) => x.kunci === p.kunci) || null; let naik = 0, turun = 0, tetap = 0; const gerak = [];
    Object.keys(p.hargaPerMerk || {}).forEach((m) => { const r = (p.hargaPerMerk[m].riwayat || []).filter((x) => !x.arsip && x.tanggal >= batasLama); if (r.length < 2) return;
      const d = r[0].hargaPerKg - r[1].hargaPerKg; if (d > 0) naik += 1; else if (d < 0) turun += 1; else tetap += 1; if (d) gerak.push({ merek: m, dari: r[1].hargaPerKg, ke: r[0].hargaPerKg, beda: d, tanggal: r[0].tanggal }); });
    gerak.sort((a, b) => Math.abs(b.beda) - Math.abs(a.beda)); const T = tempoPemasok(p.nama);
    return { kunci: p.kunci, nama: p.nama, terakhir: p.terakhir, rp: porsi ? porsi.rp : 0, pct: porsi && P.total > 0 ? porsi.rp / P.total * 100 : null, nDatang: porsi ? porsi.n : 0,
      kirim: kirim ? { n: kirim.n, rataHari: kirim.rataHari, maks: kirim.maks } : null, naik, turun, tetap, gerak: gerak.slice(0, 3), tempo: T.teks, cara: p.caraTeks || '',
      kalimat: (porsi ? pdPctTeks(porsi.rp / P.total * 100) + ' belanja ' + PD_HARI_PANJANG + ' hari (' + RP(porsi.rp) + ', ' + porsi.n + ' kedatangan)' : 'tidak ada kedatangan ' + PD_HARI_PANJANG + ' hari terakhir')
        + ' · ' + (kirim ? 'dari dipesan sampai datang ' + bpHariTeks(kirim.rataHari) + ' (' + kirim.n + ' pesanan, terlama ' + kirim.maks + ' hari)' : 'lama kirim belum bisa dihitung — belum ada pesanan lewat Belanja yang sudah datang')
        + ' · harga beli: ' + (naik + turun + tetap ? naik + ' merek naik, ' + turun + ' turun, ' + tetap + ' tetap' : 'belum ada merek dengan dua kedatangan') + ' · ' + T.teks };
  }).sort((a, b) => b.rp - a.rp || String(b.terakhir).localeCompare(String(a.terakhir)));
  return { pemasok, total: P.total, nPesananMenunggu: K.menunggu, rataKirim: K.rataHari,
    kalimat: !pemasok.length ? 'Belum ada pemasok yang mengirim dalam ' + (2 * PD_HARI_PANJANG) + ' hari terakhir.' : pemasok.length + ' pemasok mengirim dalam ' + (2 * PD_HARI_PANJANG) + ' hari terakhir'
      + (K.rataHari === null ? '' : '; dari dipesan sampai datang ' + bpHariTeks(K.rataHari) + ' (' + K.n + ' pesanan lewat Belanja)') + (K.menunggu ? '; ' + K.menunggu + ' pesanan masih menunggu datang' : '') + '.' };
}

// ---------- pelanggan: pilar marketing ----------
export const PD_PEMBELI_TERATAS = 5;
export const PD_BULAN_PELANGGAN = 3;
/**
 * Paket ketiga (owner 25 Nov 2026 — pilar "Marketing" di catatan Pondasi bisnis: segmen · target · posisi hanya bisa dikerjakan kalau pembelinya DIKENAL).
 * Baca saja, tanpa rumus uang baru:
 *  - dikenal            = porsi omzet barang 3 bulan (bulan berjalan + 2 sebelumnya) yang pembelinya bernama; sisanya nota tanpa nama — pelangganBulan
 *  - satu pembeli       = porsi omzet pembeli bernama terbesar; warna hanya bila owner mengisi ambang pembeliMaks (kebijakan)
 *  - segmen             = laba kotor & margin per tingkat harga + pembeli umum, angka pelangganBulan apa adanya (Laporan › Laba › Per pelanggan)
 *  - datang lagi, 30 hr = orang baru · yang kembali · bangku kosong (langganan yang sudah lewat N× selangnya sendiri) — semuaOrang (Pelanggan)
 * Pembeli dikenali dari NAMA di nota; nota tanpa nama tidak bisa dipilah, dan itu DISEBUT (bukan dianggap satu orang).
 */
export function pdPelanggan(kini) { return ingatPerVersi(pdKunciIngat('pdPelanggan', kini), () => pdPelangganHitung(kini)); }
function pdPelangganHitung(kini) {
  const iso = hariIniIso(kini); const A = pdAtur(); const B = pelangganBulan(iso.slice(0, 7), PD_BULAN_PELANGGAN, kini); const awal = ugTambahHari(iso, -(PD_HARI - 1));
  // datang lagi atau tidak — orang = nama di nota / buku bon; hari datang = hari ada nota atau bayar bon
  const S = semuaOrang(kini).filter((o) => o.kunjungan > 0); const datangList = S.filter((o) => o.terakhir >= awal); const baru = datangList.filter((o) => o.pertama >= awal);
  const lama = S.filter((o) => o.pertama < awal); const kembali = datangList.length - baru.length;
  const kosong = S.filter((o) => o.kosong).sort((a, b) => b.total - a.total || a.nama.localeCompare(b.nama));
  const datang = { dari: awal, sampai: iso, nDatang: datangList.length, baru: baru.length, kembali, lama: lama.length, pctKembali: lama.length ? kembali / lama.length * 100 : null, nKosong: kosong.length,
    kosong: kosong.slice(0, PD_PEMBELI_TERATAS).map((o) => ({ kunci: o.kunci, nama: o.nama, sejak: o.sejak, selang: o.selang, total: o.total })),
    kalimat: !S.length ? 'Belum ada pembeli bernama yang tercatat.'
      : PD_HARI + ' hari terakhir: ' + datangList.length + ' orang bernama datang — ' + baru.length + ' baru pertama kali, ' + kembali + ' sudah pernah datang sebelumnya'
        + (lama.length ? ' (dari ' + lama.length + ' orang yang pernah datang sebelum itu, ' + pdPctTeks(kembali / lama.length * 100) + ' datang lagi)' : '') + '. '
        + (kosong.length ? kosong.length + ' langganan sudah lebih lama dari biasanya tidak datang.' : 'Tidak ada langganan yang lebih lama dari biasanya tidak datang.') };
  const dasar = { iso, rentang: B.nama, datang, ambang: A.pembeliMaks > 0 ? 'merah bila satu pembeli lebih dari ' + pdPctTeks(A.pembeliMaks) + ' omzet (ambang owner)' : 'ambang satu pembeli belum diatur — tanpa warna',
    sumber: 'Laporan › Laba › Per pelanggan · Pelanggan' };
  if (B.diarsip || !B.pembeli) return Object.assign(dasar, { ada: false, lampu: 'tanpa', kalimat: B.kalimatArsip || 'Catatan per nota ' + B.nama + ' tidak tersedia.', dikenal: null, terbesar: null, pembeli: [], segmen: [], segmenLaba: null, segmenMargin: null, menutup: true });
  const omzet = Number(B.omzetBarang) || 0; const omzetNama = B.pembeli.reduce((a, o) => a + o.omzet, 0); const T = B.tanpaNama || { omzet: 0, nNota: 0 };
  const dikenal = { omzet, omzetNama, omzetTanpa: T.omzet, nOrang: B.pembeli.length, nNotaNama: B.pembeli.reduce((a, o) => a + o.nNota, 0), nNotaTanpa: T.nNota, pct: omzet > 0 ? omzetNama / omzet * 100 : null };
  const pembeli = B.pembeli.slice(0, PD_PEMBELI_TERATAS).map((o) => ({ kunci: o.kunci, nama: o.nama, usaha: o.usaha, tingkatNama: o.tingkatNama, omzet: o.omzet, labaKotor: o.labaKotor, nNota: o.nNota, pct: o.porsiOmzet }));
  const t0 = pembeli.length && pembeli[0].omzet > 0 && pembeli[0].pct !== null ? pembeli[0] : null; const lampu = t0 ? pdLampuAtas(t0.pct, A.pembeliMaks) : 'tanpa';
  const segmen = B.tingkat.map((g) => ({ id: g.id, nama: g.nama, nOrang: g.nOrang, omzet: g.omzet, labaKotor: g.labaKotor, margin: g.pct, porsiLaba: g.porsiLaba, porsiOmzet: g.porsiOmzet }));
  const berLaba = segmen.filter((g) => g.labaKotor !== null && g.omzet > 0); const segmenLaba = berLaba.slice().sort((a, b) => b.labaKotor - a.labaKotor)[0] || null;
  const segmenMargin = berLaba.filter((g) => g.margin !== null).sort((a, b) => b.margin - a.margin)[0] || null;
  const kalimat = !B.menutup ? 'Angka per pelanggan ' + B.nama + ' TIDAK menutup ke Laporan — jangan dipakai memutuskan; lihat Laporan › Laba › Per pelanggan.'
    : !(omzet > 0) ? 'Belum ada jualan ' + B.nama + ' yang bisa dipilah per pembeli.'
      : pdPctTeks(dikenal.pct) + ' omzet barang ' + B.nama + ' pembelinya bernama (' + RP(omzetNama) + ' dari ' + RP(omzet) + ', ' + dikenal.nOrang + ' orang); '
        + (T.nNota ? T.nNota + ' nota tanpa nama (' + RP(T.omzet) + ') tidak bisa dipilah siapa pembelinya. ' : 'tidak ada nota tanpa nama. ')
        + (t0 ? 'Pembeli terbesar ' + t0.nama + ': ' + pdPctTeks(t0.pct) + ' omzet.' : 'Belum ada pembeli bernama.')
        + (segmenLaba ? ' Laba kotor terbesar dari ' + segmenLaba.nama + (segmenLaba.porsiLaba !== null ? ' (' + pdPctTeks(segmenLaba.porsiLaba) + ')' : '') + (segmenMargin && segmenMargin.id !== segmenLaba.id ? '; margin tertinggi ' + segmenMargin.nama + ' (' + pdPctTeks(segmenMargin.margin) + ')' : '') + '.' : '');
  return Object.assign(dasar, { ada: omzet > 0, lampu, kalimat, dikenal, terbesar: t0, pembeli, segmen, segmenLaba, segmenMargin, menutup: !!B.menutup, berjalan: !!B.berjalan });
}

// ---------- risiko: kalau omzet turun ----------
export const PD_TURUN = [10, 20, 30, 50];
/**
 * Skenario omzet turun `turunPct` %: laba kotor ikut turun SEBANDING (rasio margin tetap), biaya toko TETAP. → laba bersih 30 hari sesudah turun; kalau jadi rugi,
 * tahanHari = uang toko ÷ rugi per hari (null = masih untung). Ambil pribadi & pembayaran bon pemasok TIDAK ikut (disebut di layar).
 */
export function pdSkenario(labaKotor30, labaBersih30, kas, turunPct) {
  const hilang = labaKotor30 * turunPct / 100; const laba = labaBersih30 - hilang; const rugiHari = laba < 0 ? -laba / PD_HARI : 0;
  return { turunPct, hilang, laba, rugiHari, tahanHari: laba >= 0 ? null : kas > 0 ? kas / rugiHari : 0 };
}
/** Omzet boleh turun paling banyak berapa persen sebelum toko rugi = laba bersih 30 hari ÷ laba kotor 30 hari. null = sudah rugi / laba kotor tidak positif. */
export const pdBatasTurun = (labaKotor30, labaBersih30) => (labaKotor30 > 0 && labaBersih30 > 0 ? Math.min(100, labaBersih30 / labaKotor30 * 100) : null);
const PD_NAMA_HARI = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
const pdHariKe = (iso) => new Date(String(iso) + 'T00:00:00').getDay();
/**
 * Pola hari dalam minggu dari 56 hari terakhir (tanpa hari ini): rata-rata omzet per nama hari (hari tanpa jualan ikut dihitung Rp0) → prakiraan omzet 30 hari
 * ke depan = Σ rata-rata hari-harinya [PERKIRAAN]. Belum 28 hari catatan → belum bisa (disebut). Musim (Lebaran, panen) TIDAK terbaca: catatan belum setahun.
 */
export function pdPolaHari(kini) {
  const iso = hariIniIso(kini); const p = lpPertama(); const H = hariTerakhir(kini, 57).filter((d) => !d.hariIni && !d.diarsip && (!p || d.iso >= p));
  if (H.length < 28) return { ada: false, kenapa: 'butuh 28 hari catatan untuk membaca pola hari — baru ' + H.length + ' hari' };
  const per = PD_NAMA_HARI.map((nama, i) => ({ i, nama, n: 0, rp: 0 })); H.forEach((d) => { const x = per[pdHariKe(d.iso)]; x.n += 1; x.rp += Number(d.omzet) || 0; });
  per.forEach((x) => { x.rata = x.n ? x.rp / x.n : 0; }); let depan = 0; for (let k = 1; k <= PD_HARI; k++) depan += per[pdHariKe(ugTambahHari(iso, k))].rata;
  const urut = per.filter((x) => x.n).slice().sort((a, b) => b.rata - a.rata);
  return { ada: true, nHari: H.length, per, depan: Math.round(depan), ramai: urut[0], sepi: urut[urut.length - 1] };
}
export function pdRisiko(kini) { return ingatPerVersi(pdKunciIngat('pdRisiko', kini), () => pdRisikoHitung(kini)); }
function pdRisikoHitung(kini) {
  const iso = hariIniIso(kini); const L = ugLabaBersih(ugTambahHari(iso, -(PD_HARI - 1)), iso); const N = neracaPada(null, kini); const kas = N.N ? N.N.kas : null;
  const labaKotor = Number(L.margin) || 0, laba = Number(L.labaBersih) || 0; const batas = pdBatasTurun(labaKotor, laba); const pola = pdPolaHari(kini);
  const skenario = PD_TURUN.map((t) => { const S = pdSkenario(labaKotor, laba, pdBilangan(kas) ? kas : 0, t);
    return Object.assign(S, { kasAda: pdBilangan(kas), kalimat: S.laba >= 0 ? 'masih untung ' + RP(S.laba) + ' per ' + PD_HARI + ' hari' : 'RUGI ' + RP(-S.laba) + ' per ' + PD_HARI + ' hari' + (pdBilangan(kas) ? (kas > 0 ? ' — uang toko tahan ±' + Math.floor(S.tahanHari) + ' hari' : ' — uang toko sudah habis') : ' — uang toko belum bisa dihitung') }); });
  return { labaKotor, laba, omzet: Number(L.omzetPenuh) || 0, kas, batas, skenario, pola,
    kalimat: !(labaKotor > 0) ? 'Laba kotor ' + PD_HARI + ' hari terakhir nol atau minus — skenario omzet turun tidak bermakna; bahasannya harga jual.'
      : batas === null ? 'Toko sudah RUGI ' + RP(-laba) + ' dalam ' + PD_HARI + ' hari terakhir — tiap penurunan omzet menambah ruginya.'
        : 'Omzet boleh turun paling banyak ' + pdPctTeks(batas) + ' sebelum toko rugi (laba bersih ' + RP(laba) + ' dari laba kotor ' + RP(labaKotor) + ', ' + PD_HARI + ' hari terakhir; biaya toko dianggap tetap).' };
}

// ---------- organisasi: siapa mencatat apa ----------
/**
 * Per orang, 30 hari terakhir: nota yang dicatat & yang dibatalkan (rwPerOrang — nota Jual › Riwayat), nego yang jadi nota & potongannya (ngBuku — Buku Nego),
 * tutup hari yang dihitungnya & selisih lacinya (riwayatTutup). Nama = isi kolom `oleh` catatannya; kosong = "tanpa nama pencatat". Baca saja.
 */
export function pdOrganisasi(kini) { return ingatPerVersi(pdKunciIngat('pdOrganisasi', kini), () => pdOrganisasiHitung(kini)); }
function pdOrganisasiHitung(kini) {
  const iso = hariIniIso(kini); const awal = ugTambahHari(iso, -(PD_HARI - 1)); const per = {}; const orang = (nama) => { const k = String(nama || '').trim(); return per[k] || (per[k] = { nama: k, nota: 0, omzet: 0, batal: 0, nego: 0, potongan: 0, tutup: 0, selisih: 0, nSelisih: 0 }); };
  const R = rwPerOrang(awal, iso); R.orang.forEach((o) => { const x = orang(o.nama); x.nota += o.nota; x.omzet += o.omzet; x.batal += o.batal; });
  for (let k = 0; k < PD_HARI; k++) ngBuku(ugTambahHari(iso, -k)).baris.forEach((b) => { if (b.jenis !== 'nota') return; const x = orang(b.oleh); x.nego += 1; if (b.totalSelisih < 0) x.potongan += -b.totalSelisih; });
  riwayatTutup(PD_HARI + 5).forEach((t) => { if (!t.tanggal || t.tanggal < awal || t.tanggal > iso) return; const x = orang(t.oleh); x.tutup += 1; const s = Number(t.selisih) || 0; x.selisih += s; if (Math.abs(s) > 0.5) x.nSelisih += 1; });
  const daftar = Object.keys(per).map((k) => per[k]).filter((x) => x.nota || x.batal || x.nego || x.tutup).sort((a, b) => b.nota - a.nota || b.tutup - a.tutup || a.nama.localeCompare(b.nama));
  daftar.forEach((x) => { x.tampil = x.nama || 'tanpa nama pencatat';
    x.kalimat = x.nota + ' nota ' + RP(x.omzet) + (x.batal ? ' · ' + x.batal + ' dibatalkan' : '') + (x.nego ? ' · ' + x.nego + ' nego, potongan ' + RP(x.potongan) : '') + (x.tutup ? ' · ' + x.tutup + ' tutup hari' + (x.nSelisih ? ', ' + x.nSelisih + ' malam berselisih (jumlah ' + RP(x.selisih) + ')' : ', tanpa selisih') : ''); });
  const tanpaNama = per[''] ? per[''].nota : 0;
  return { dari: awal, sampai: iso, orang: daftar, nBerlaku: R.nBerlaku, nBatal: R.nBatal, tanpaNama,
    kalimat: !daftar.length ? 'Belum ada catatan ' + PD_HARI + ' hari terakhir.' : R.nBerlaku + ' nota dicatat ' + daftar.filter((x) => x.nama).length + ' orang dalam ' + PD_HARI + ' hari' + (R.nBatal ? '; ' + R.nBatal + ' nota dibatalkan' : '')
      + (tanpaNama ? '; ' + tanpaNama + ' nota tanpa nama pencatat — tidak bisa ditelusuri siapa yang mencatat' : '') + '.' };
}

// ---------- organisasi: siapa pegang apa (paket keempat) ----------
/** Pembagian tugas apa adanya dari ssTugas (Menu › Toko ini › Buku pegangan) + satu kalimat. Urusan tanpa pengganti = kuning (toko berhenti kalau orangnya absen). */
export function pdTugas() {
  const T = ssTugas();
  return Object.assign({}, T, { lampu: !T.ada ? 'tanpa' : T.nTanpaGanti ? 'amber' : 'hijau',
    kalimat: !T.ada ? 'Belum ada pembagian tugas tertulis — siapa memegang urusan apa masih di kepala.'
      : T.n + ' urusan tertulis; ' + (T.nTanpaGanti ? T.nTanpaGanti + ' belum punya pengganti: ' + T.tanpaGanti.slice(0, 4).join(' · ') + (T.nTanpaGanti > 4 ? ' …' : '') + '.' : 'semuanya punya pengganti.')
        + (T.bebanTerbanyak && T.bebanTerbanyak.n > 1 ? ' Paling banyak memegang: ' + T.bebanTerbanyak.nama + ' (' + T.bebanTerbanyak.n + ' urusan).' : '') });
}

// ---------- percobaan: R&D yang diukur (paket keempat) ----------
const pdHariAntara = (a, b) => Math.round((Date.parse(b + 'T00:00:00Z') - Date.parse(a + 'T00:00:00Z')) / 86400000) + 1;
const pdRingkasMerek = (g, hari) => { const ada = !!g && g.nBaris + g.nRetur > 0; const omzet = ada ? g.omzet + g.omzetTanpaHpp : 0;
  return { ada, hari, nBaris: ada ? g.nBaris : 0, kg: ada ? g.kg : 0, omzet, laba: ada ? g.margin : null, margin: ada ? g.pct : null, nTanpaHpp: ada ? g.nTanpaHpp : 0,
    omzetHari: hari > 0 ? omzet / hari : 0, kgHari: hari > 0 && ada ? g.kg / hari : 0, labaHari: hari > 0 && ada && g.margin !== null ? g.margin / hari : null }; };
const pdBedaPct = (baru, lama) => (pdBilangan(baru) && pdBilangan(lama) && lama > 0 ? (baru - lama) / lama * 100 : null);
// pintu tulis percobaan tetap di sistem-logika (satu dokumen aturanToko/percobaan); Laporan memanggilnya lewat sini supaya layar cukup mengenal pondasi-logika
// fungsi (bukan const): bundel Dasbor memuat modul ini TANPA sistem-logika — nama dari sana tidak boleh dibaca saat modul dimuat
export const pdPercobaanMaks = () => SS_PERCOBAAN_MAKS;
export const pdDrafPercobaan = (id, hariIni) => ssDrafPercobaan(id, hariIni);
export const pdSusunPercobaan = (d, w) => susunPercobaan(d, w);
export const pdSusunHapusPercobaan = (id, w) => susunHapusPercobaan(id, w);
export const PD_MEREK_PILIH = 12;   // pilihan merek yang langsung tampil di lembar percobaan (terlaris dulu); sisanya di balik "semua merek"
/** Merek yang punya jualan 90 hari terakhir (kg terbanyak dulu) — pilihan di lembar tulis percobaan. */
export function pdMerekPilihan(kini) { const iso = hariIniIso(kini); const R = merekRentang(ugTambahHari(iso, -(PD_HARI_PANJANG - 1)), iso);
  return Object.keys(R.merek).filter((n) => R.merek[n].nBaris > 0).sort((a, b) => R.merek[b].kg - R.merek[a].kg || a.localeCompare(b)); }
/**
 * Tiap percobaan owner (ssPercobaan) diukur dari nota: SELAMA percobaan (mulai … selesai / hari ini) dibanding rentang SAMA PANJANG tepat sebelumnya, per hari —
 * omzet, kg, laba kotor, margin. Sumber merekRentang (peta merek & modal nota yang sama dengan Laporan › Laba › Per merek, tanpa susut). Yang belum bisa
 * dibandingkan DISEBUT: belum mulai, rentang pembanding lebih tua dari catatan pertama, menyentuh tahun yang sudah tutup buku, atau mereknya tanpa jualan.
 */
export function pdPercobaan(kini) { return ingatPerVersi(pdKunciIngat('pdPercobaan', kini), () => pdPercobaanHitung(kini)); }
function pdPercobaanHitung(kini) {
  const iso = hariIniIso(kini); const P = ssPercobaan(); const mulaiCatat = lpPertama() || '';
  const daftar = P.daftar.map((x) => {
    const dasar = Object.assign({}, x, { sasaran: x.merek || 'seluruh toko' });
    if (x.mulai > iso) return Object.assign(dasar, { status: 'belum', statusNama: 'belum mulai', hari: 0, selama: null, sebelum: null, beda: null, bisaBanding: false, kalimat: 'Mulai ' + tanggalPendek(x.mulai) + ' — belum ada yang diukur.' });
    const akhir = x.selesai && x.selesai < iso ? x.selesai : iso; const hari = pdHariAntara(x.mulai, akhir); const awalB = ugTambahHari(x.mulai, -hari), akhirB = ugTambahHari(x.mulai, -1);
    const RS = merekRentang(x.mulai, akhir), RB = merekRentang(awalB, akhirB); const pilih = (R) => (x.merek ? R.merek[x.merek] : R.semua);
    const selama = pdRingkasMerek(pilih(RS), hari), sebelum = pdRingkasMerek(pilih(RB), hari); const status = x.selesai && x.selesai <= iso ? 'selesai' : 'berjalan';
    const kenapa = RS.arsip || RB.arsip ? 'rentangnya menyentuh tahun yang sudah tutup buku — notanya ikut arsip'
      : mulaiCatat && awalB < mulaiCatat ? 'rentang pembanding (' + tanggalPendek(awalB) + ' – ' + tanggalPendek(akhirB) + ') lebih tua dari catatan pertama toko (' + tanggalPendek(mulaiCatat) + ')'
        : !sebelum.ada ? (x.merek ? x.merek + ' tidak punya jualan' : 'toko tidak punya jualan') + ' pada ' + hari + ' hari sebelum percobaan — tidak ada pembanding' : '';
    const bisa = !kenapa; const beda = bisa ? { omzet: pdBedaPct(selama.omzetHari, sebelum.omzetHari), kg: pdBedaPct(selama.kgHari, sebelum.kgHari), laba: pdBedaPct(selama.labaHari, sebelum.labaHari),
      marginPoin: pdBilangan(selama.margin) && pdBilangan(sebelum.margin) ? selama.margin - sebelum.margin : null } : null;
    const arah = (p) => (p === null ? 'tidak bisa dibandingkan' : (p >= 0 ? 'naik ' : 'turun ') + pdPctTeks(Math.abs(p)));
    const kalimat = !selama.ada ? (x.merek || 'Toko') + ' belum punya jualan selama percobaan (' + hari + ' hari).' + (kenapa ? '' : ' Sebelumnya ' + RP(Math.round(sebelum.omzetHari)) + ' per hari.')
      : !bisa ? hari + ' hari percobaan: omzet ' + RP(Math.round(selama.omzetHari)) + ' per hari' + (selama.labaHari === null ? '' : ', laba kotor ' + RP(Math.round(selama.labaHari)) + ' per hari') + '. Belum bisa dibandingkan: ' + kenapa + '.'
        : 'Per hari, ' + hari + ' hari percobaan dibanding ' + hari + ' hari sebelumnya: omzet ' + arah(beda.omzet) + ', kg ' + arah(beda.kg) + ', laba kotor ' + arah(beda.laba)
          + (beda.marginPoin === null ? '' : '; margin ' + pdPctTeks(sebelum.margin) + ' → ' + pdPctTeks(selama.margin)) + '.';
    return Object.assign(dasar, { status, statusNama: status === 'selesai' ? 'selesai' : 'berjalan', hari, akhir, pembanding: { awal: awalB, akhir: akhirB }, selama, sebelum, beda, bisaBanding: bisa, kenapa, kalimat });
  });
  const jalan = daftar.filter((d) => d.status === 'berjalan').length;
  return { iso, ada: P.ada, n: P.n, daftar, kalimat: !P.ada ? 'Belum ada percobaan yang dicatat. Tiap mencoba merek, harga, atau kemasan baru: catat di sini, sistem mengukur hasilnya dari nota.'
    : P.n + ' percobaan dicatat' + (jalan ? ', ' + jalan + ' masih berjalan' : '') + '. Angkanya dari nota — tanpa susut stok, dan tidak memisahkan sebab lain (musim, harga pemasok).' };
}

// ==================== paket kelima (owner 25 Nov 2026): upah · biaya antar · harta pribadi ====================
export const PD_BULAN_UPAH = 3;
export const pdBulanTeks = (n) => (!pdBilangan(n) ? '—' : pdSatu(n) + ' bln');
/**
 * Sanggup bayar upah — catatan Pondasi bisnis menyebut gaji karyawan sebagai ukuran sehat tersendiri. Baca saja: upah per bulan = baris "Upah & gaji" Kendali
 * biaya (kendaliBulan: gaji kotor mesin laba) rata-rata ≤ 3 bulan penuh terakhir yang ada upahnya; upah yang sudah dikerjakan tapi belum dibayar = kendaliBulan
 * bulan berjalan (U.total, dari buku upah); uang toko = neracaPada hari ini. Warna = FAKTA: uang toko kurang dari upah yang belum dibayar → merah; kurang dari
 * satu bulan upah → kuning.
 */
export function pdUpah(kini) { return ingatPerVersi(pdKunciIngat('pdUpah', kini), () => pdUpahHitung(kini)); }
function pdUpahHitung(kini) {
  const B = daftarBulan(kini, PD_BULAN_UPAH + 1); const jalan = B.find((b) => b.berjalan) || null; const N = neracaPada(null, kini); const kas = N.N && pdBilangan(N.N.kas) ? N.N.kas : null;
  const bulan = B.filter((b) => !b.berjalan).map((b) => { const K = kendaliBulan(b.key, kini); return { key: b.key, nama: b.pendek, upah: Number(K.per.upah.n) || 0 }; }); const ada = bulan.filter((b) => b.upah > 0);
  const rata = ada.length ? Math.round(ada.reduce((a, b) => a + b.upah, 0) / ada.length) : null; const KJ = jalan ? kendaliBulan(jalan.key, kini) : null; const belum = KJ && KJ.U ? Number(KJ.U.total) || 0 : 0;
  const cukup = rata && kas !== null ? Math.max(0, kas) / rata : null; const lampu = kas === null || (!rata && !belum) ? 'tanpa' : kas < 0 || kas < belum ? 'merah' : rata && kas < rata ? 'amber' : 'hijau';
  return { kas, rata, nBulan: ada.length, bulan, belum, belumTeks: KJ && KJ.U ? KJ.U.teks : '', cukup, lampu, sumber: 'Laporan › Biaya · Uang › Upah',
    kalimat: kas === null ? 'Uang toko belum bisa dihitung — titik kas belum disetel.'
      : !rata && !belum ? 'Belum ada upah yang tercatat di ' + PD_BULAN_UPAH + ' bulan penuh terakhir.'
        : (rata ? 'Upah rata-rata ' + RP(rata) + ' per bulan (' + ada.map((b) => b.nama).join(', ') + '); uang toko ' + RP(kas) + (kas < 0 ? ' — MINUS, tidak cukup untuk upah.' : ' cukup untuk ' + pdSatu(cukup) + ' bulan upah.') : 'Belum ada bulan penuh yang upahnya tercatat.')
          + (belum > 0 ? ' Upah yang sudah dikerjakan dan belum dibayar: ' + RP(belum) + (kas < belum ? ' — LEBIH BESAR dari uang toko.' : '.') : ' Tidak ada upah yang menunggu dibayar.') };
}
/**
 * Biaya antar per kiriman (rantai pasok · distribusi). Baca saja, 3 bulan (berjalan + 2 sebelumnya), dari baris "Bensin & angkut" Kendali biaya: biaya yang
 * tercatat, ongkir yang DITAGIH ke pembeli & jumlah nota yang diantar (ajOngkirRentang lewat kendaliBulan). Baris itu juga memuat kuli & parkir yang bukan
 * antaran — DISEBUT, tidak dipisah-pisah dengan tebakan. Tanpa warna: berapa yang wajar ditanggung toko = kebijakan owner.
 */
export function pdAntar(kini) { return ingatPerVersi(pdKunciIngat('pdAntar', kini), () => pdAntarHitung(kini)); }
function pdAntarHitung(kini) {
  const bulan = daftarBulan(kini, 3).map((b) => { const K = kendaliBulan(b.key, kini); const r = (K.baris || []).find((x) => x.id === 'angkut') || {};
    return { key: b.key, nama: b.pendek, berjalan: !!b.berjalan, biaya: Number(K.per.angkut.n) || 0, ongkir: Number(r.ongkirMasuk) || 0, n: Number(r.nAntar) || 0 }; });
  const biaya = bulan.reduce((a, b) => a + b.biaya, 0), ongkir = bulan.reduce((a, b) => a + b.ongkir, 0), n = bulan.reduce((a, b) => a + b.n, 0);
  const perKirim = n > 0 && biaya > 0 ? Math.round(biaya / n) : null, ongkirPerKirim = n > 0 ? Math.round(ongkir / n) : null, tertutup = biaya > 0 ? ongkir / biaya * 100 : null;
  const rentang = bulan.length ? bulan[bulan.length - 1].nama + ' – ' + bulan[0].nama : '';
  return { bulan, rentang, biaya, ongkir, n, perKirim, ongkirPerKirim, tertutup, ditanggung: biaya - ongkir, sumber: 'Laporan › Biaya › Bensin & angkut · Surat jalan',
    kalimat: !biaya && !n ? 'Belum ada biaya bensin & angkut maupun nota yang diantar dalam ' + bulan.length + ' bulan ini.'
      : !biaya ? n + ' nota diantar (' + rentang + ') dengan ongkir ditagih ' + RP(ongkir) + ', tapi belum ada biaya bensin & angkut yang dicatat — biaya per kiriman belum bisa dihitung.'
      : !n ? 'Bensin & angkut ' + RP(biaya) + ' (' + rentang + '), tapi tidak ada nota yang dicatat diantar — biaya per kiriman belum bisa dihitung.'
        : n + ' nota diantar (' + rentang + '): bensin & angkut ' + RP(biaya) + ' = ' + RP(perKirim) + ' per kiriman; ongkir yang ditagih ' + RP(ongkir) + ' = ' + RP(ongkirPerKirim) + ' per kiriman'
          + (tertutup === null ? '.' : ' — menutup ' + pdPctTeks(tertutup) + ' biayanya' + (biaya > ongkir ? ', sisanya ' + RP(biaya - ongkir) + ' ditanggung toko.' : '.')) };
}

// ---------- harta pribadi owner per kuartal (ekuitas pribadi vs ekuitas toko) ----------
export const PD_KUARTAL_PRIBADI = 4;
const pdPribadiPeta = () => { const d = ugAturDok(PD_ID) || {}; return d.pribadi && typeof d.pribadi === 'object' ? d.pribadi : {}; };
/** Simpan harta pribadi owner untuk satu kuartal (rupiah bulat > 0; kosong = dihapus) — kolom `pribadi` dokumen aturanToko/pondasi; kolom lain ikut disalin. */
export function susunPribadi(key, ketik, w) {
  if (!/^\d{4}-K[1-4]$/.test(String(key))) return { tolak: 'Kuartal tidak dikenal' };
  const lama = ugAturDok(PD_ID) || {}; const peta = Object.assign({}, pdPribadiPeta()); const dulu = Number(peta[key]) || 0;
  if (ugKosong(ketik)) { if (!dulu) return { tolak: 'Tidak ada yang diubah' }; delete peta[key];
    return pdSimpanAtur(Object.assign({}, lama, { id: PD_ID, tanggal: w.tanggal, jam: w.jam, pribadi: peta }), { drafPribadi: null, kabar: 'Harta pribadi ' + ssKuartalNama(key) + ' dihapus', kabarAwas: false }); }
  const n = ugAngka(ketik); if (!(n > 0) || n > PD_TARGET_MAKS || Math.round(n) !== n) return { tolak: 'Harta pribadi ditulis dalam rupiah bulat, lebih dari 0 — kosong = dihapus' };
  if (n === dulu) return { tolak: 'Tidak ada yang diubah' }; peta[key] = n;
  return pdSimpanAtur(Object.assign({}, lama, { id: PD_ID, tanggal: w.tanggal, jam: w.jam, pribadi: peta }), { drafPribadi: null, kabar: 'Harta pribadi ' + ssKuartalNama(key) + ' tersimpan — ' + RP(n), kabarAwas: false });
}
/**
 * Harta pribadi owner (angka yang DIISI owner sendiri — sistem tidak mencatat harta pribadi) berdampingan dengan kekayaan bersih toko akhir kuartal (pdKekayaan:
 * bulan terakhir kuartal itu; kuartal berjalan = hari ini). Catatan Pondasi bisnis: yang dibesarkan dulu ekuitas toko, baru ekuitas pribadi → DISEBUT bila
 * pribadi naik selagi kekayaan toko turun (kuning). Belum diisi / belum bisa dihitung = disebut, bukan nol.
 */
export function pdPribadi(kini) { return ingatPerVersi(pdKunciIngat('pdPribadi', kini), () => pdPribadiHitung(kini)); }
function pdPribadiHitung(kini) {
  const iso = hariIniIso(kini); const kiniQ = ssKuartalKey(iso); const peta = pdPribadiPeta(); const KY = pdKekayaan(kini);
  const kuartal = []; for (let i = 0; i < PD_KUARTAL_PRIBADI; i++) { const key = ssKuartalGeser(kiniQ, -i); const q = Number(key.slice(6, 7)); const bulanAkhir = key.slice(0, 4) + '-' + String(q * 3).padStart(2, '0');
    const b = i === 0 ? KY.bulan.find((x) => x.berjalan) : KY.bulan.find((x) => x.key === bulanAkhir); const pribadi = Number(peta[key]) > 0 ? Math.round(Number(peta[key])) : null;
    kuartal.push({ key, nama: ssKuartalNama(key), berjalan: i === 0, toko: b && b.ada ? b.bersih : null, tokoKenapa: b && !b.ada ? b.kenapa : !b ? 'di luar catatan toko' : '', pribadi }); }
  const kini0 = kuartal[0]; const lalu = kuartal.slice(1).find((q) => q.pribadi !== null && q.toko !== null) || null; const lengkap = kini0.pribadi !== null && kini0.toko !== null;
  const dPribadi = lengkap && lalu ? kini0.pribadi - lalu.pribadi : null, dToko = lengkap && lalu ? kini0.toko - lalu.toko : null;
  const lampu = dPribadi === null ? 'tanpa' : dPribadi > 0 && dToko < 0 ? 'amber' : 'hijau';
  return { kuartal, kiniKey: kiniQ, lampu, dPribadi, dToko, banding: lalu ? lalu.nama : '', sumber: 'isian owner · Laporan › Neraca',
    kalimat: kini0.pribadi === null ? 'Harta pribadi ' + kini0.nama + ' belum diisi — sistem hanya tahu sisi toko. Isi sendiri perkiraannya (tabungan, kendaraan, rumah, dikurangi utang pribadi).'
      : kini0.toko === null ? 'Harta pribadi ' + kini0.nama + ' ' + RP(kini0.pribadi) + '; kekayaan toko belum bisa dihitung' + (kini0.tokoKenapa ? ' — ' + kini0.tokoKenapa : '') + '.'
        : 'Harta pribadi ' + RP(kini0.pribadi) + ' · kekayaan bersih toko ' + RP(kini0.toko) + ' (' + kini0.nama + ').'
          + (dPribadi === null ? ' Belum ada kuartal sebelumnya yang terisi untuk dibandingkan.' : ' Sejak ' + lalu.nama + ': pribadi ' + (dPribadi >= 0 ? 'naik ' : 'turun ') + RP(Math.abs(dPribadi)) + ', toko ' + (dToko >= 0 ? 'naik ' : 'turun ') + RP(Math.abs(dToko))
            + (lampu === 'amber' ? ' — harta pribadi tumbuh selagi kekayaan toko menyusut.' : '.')) };
}
