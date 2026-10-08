// LOGIKA layar LAPORAN & DOKUMEN (putaran 19), tanpa DOM. Enam keluarga: Laba (tiga angka yang tidak boleh tertukar: margin kotor · laba bersih · diterima
// tunai, per bulan) · Harian (rekap satu hari + buku kas hari itu + kirim WA) · Bulanan (enam bulan, inti bulan, DK3 rekap omzet 12 bulan: kumulatif, tanda
// dilaporkan, tarif & batas = SETELAN OWNER, bukti bernomor) · Neraca (kekayaan toko per tanggal, dua sisi) · Dokumen (DK2 laporan berkop laba-rugi / neraca /
// arus kas 1·3·12 bulan, DRAF sebelum tutup buku, paket bank, banding periode; DK4 dokumen kecil: bukti setor modal, slip upah, kartu piutang, rekap bon
// pemasok, cetak ulang nota = SALINAN ke-N) · Setelan (DK1 kop & identitas usaha berversi, dokumen mana pakai kop mana, nomor dokumen).
// SEMUA angka dari mesin beku yang sama dengan sistem lama (hitungLabaBersihRentang lewat ugLabaBersih = + lebih/kurang kas, 39b no. 38; hitungArusKasInti, hitungNeraca, kasPada) — di sini cuma disusun, diberi kop,
// dinomori, lalu dicetak / PDF / WA. Yang BARU ditulis: aturanToko/{identitas, dokumen, rekapOmzet, laporan} + koleksi dokumenCetak (tiap cetakan bernomor).
// Kejujuran: bulan belum tutup buku = DRAF; neraca yang kasnya belum bisa dihitung / stoknya minus TIDAK dicetak; kas akhir arus kas = kas neraca (satu mesin);
// tarif/batas rekap omzet bukan nasihat pajak. Nama pembantu diprefiks `lp` (bundel uji jsc satu lingkup).
import { hitungLabaRentang, hitungArusKasInti, barisSusutStok, bayaranBiayaBulanan, hitungNeraca, kasPada, hitungPiutang, hitungUtangPemasok } from '../mesin/beku.js';
import { akhirBulanIso, bulanDari, namaBulanPanjang, caraBayarKunci, hppTercatat, namaSingkatTrx, kunciPelanggan, formatTanggal } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilPengeluaranHarian, ambilPiutangMutasi, ambilSemuaBatch, ambilTutupHari, ambilTitikKas, ambilDokumenCetak, cacheMentah, kunciSampai, kunciNota, jumlahNota, returUangPerHari, ambilHargaTerbit, eraBuku, tahunDiarsip, potretTahun, potretBulan, potretHari, catatanPertama, ingatGerakanKas, ingatKasPada, ingatNeraca } from '../data/toko.js';
import { RP, ANGKA, hariIniIso, tanggalPendek, lebihBayarDari, LEBIH_AMBANG, pecahLebih, ringkasLebih } from '../inti/format.js';
import { ugAturDok, ugAngka, ugKosong, ugTambahHari, modalTertanam, aturKeluar, priveBulan, priveRentang, pilahHarian, adalahMdr, ugLabaBersih, saldoKantong, ugLebihKurangKas } from './uang-logika.js';
import { bkEra } from './tutup-buku-logika.js';
import { notaDari, notaDariBaris, susunStruk, stAtur, namaBaris } from './struk-logika.js';
import { riwayatUpah } from './upah-logika.js';
import { semuaBon } from './bon-logika.js';
import { daftarPemasok, bukuBon } from './bon-pemasok-logika.js';
import { bukuOwner } from './owner-toko-logika.js';
import { pjOmzetSistem, pjGabungRekap, pjTahun, PJ_LABEL } from './pajak-logika.js';
// owner 7 Okt: daftar harga & harga yang naik untuk pelanggan dibaca dari katalog yang dipakai kasir
import { hgSemua } from './harga-logika.js';

export const KELUARGA_LAPORAN = [['laba', 'Laba'], ['biaya', 'Biaya'], ['harian', 'Harian'], ['mingguan', 'Mingguan'], ['bulanan', 'Bulanan'], ['pajak', 'Pajak'], ['tahunan', 'Tahunan'], ['neraca', 'Neraca'], ['dokumen', 'Dokumen'], ['setelan', 'Setelan']];   // Mingguan & Tahunan: owner 23 Sep · Biaya: kendali biaya, putaran 38 (kendali-biaya-logika.js)
export const JENIS_LAPORAN = [['labarugi', 'Laba-Rugi'], ['neraca', 'Neraca'], ['aruskas', 'Arus Kas']];
export const RENTANG_LAPORAN = [[1, '1 bulan'], [3, '3 bulan'], [12, '12 bulan']];
export const JENIS_KECIL = [['setor', 'Bukti setoran modal', 'dari catatan Owner & toko'], ['upah', 'Slip upah', 'dari buku upah'], ['piutang', 'Kartu piutang', 'per pelanggan'], ['bon', 'Rekap bon pemasok', 'per pemasok'], ['nota', 'Cetak ulang nota', 'SALINAN bercap'],
  ['harga', 'Daftar harga', 'untuk pelanggan · yang dipakai kasir'], ['naik', 'Harga yang naik', 'untuk pelanggan · dari riwayat terbit']].map((j) => ({ id: j[0], nama: j[1], ket: j[2] }));   // harga & naik: owner 7 Okt (visi 17 Sep)
export const DOKUMEN_KOP = [['nota', 'Nota pelanggan & cetak ulang', 'ringkas'], ['kartu', 'Kartu piutang', 'ringkas'], ['slip', 'Slip upah', 'ringkas'], ['harian', 'Rekap harian', 'ringkas'], ['laporan', 'Laba-rugi · neraca · arus kas', 'penuh'], ['omzet', 'Rekap omzet bulanan', 'penuh'], ['bon', 'Rekap bon pemasok', 'penuh'], ['setor', 'Bukti setoran modal', 'penuh'], ['harga', 'Daftar harga & harga yang naik', 'ringkas']].map((d) => ({ id: d[0], nama: d[1], awal: d[2] }));
export const KOLOM_IDENTITAS = [['nama', 'Nama usaha', 'wajib'], ['alamat', 'Alamat', 'wajib'], ['telepon', 'Telepon / WA', 'boleh kosong'], ['npwp', 'NPWP', '15 atau 16 angka, boleh kosong'], ['nib', 'NIB', '13 angka, boleh kosong'], ['slogan', 'Baris kaki', 'boleh kosong']].map((k) => ({ id: k[0], nama: k[1], ket: k[2] }));
export const IDENTITAS_BAWAAN = { nama: 'Toko Beras M.IQBAL', alamat: '', telepon: '', npwp: '', nib: '', slogan: '', gaya: 'kiri', npwpDiKop: false };
// NPWP (owner 24 Sep, putaran 24): kolomnya tetap ada, tapi BAWAAN TIDAK DICETAK di kop mana pun — hanya kalau owner menyalakan npwpDiKop (kop penuh saja).
// NPWP orang pribadi 16 angka = NIK → peringatan, kalimat owner:
export const PERINGATAN_NPWP_NIK = 'NPWP orang pribadi = NIK; mencetaknya membuka NIK ke semua pembeli.';
export function peringatanNpwp(npwp) { return lpDigit(npwp || '').length === 16 ? PERINGATAN_NPWP_NIK : ''; }
/** Setelan yang tinggal di layarnya masing-masing — Setelan hanya menunjuk, tidak menggandakan. */
export const ATUR_LAIN = [
  { nama: 'Uang keluar', ket: 'keperluan rutin, batas aman ambil pribadi, tagihan bulanan, alasan', tujuan: { ke: 'uang', keluarga: 'keluar' } }, { nama: 'Tutup hari', ket: 'sisihan laba, uang kembalian, selisih yang dimaafkan, potongan QRIS', tujuan: { ke: 'uang', keluarga: 'tutup' } },
  { nama: 'Orang & upah', ket: 'tarif harian, daftar karyawan, alasan kasbon', tujuan: { ke: 'uang', keluarga: 'upah' } }, { nama: 'Pindah uang', ket: 'uang kembalian di laci, alasan pindah', tujuan: { ke: 'uang', keluarga: 'pindah' } }, { nama: 'Tutup buku', ket: 'daftar saksi paraf', tujuan: { ke: 'uang', keluarga: 'buku' } },
  { nama: 'Bon pemasok', ket: 'tempo, biaya admin bank', tujuan: { ke: 'harga', keluarga: 'bon' } }, { nama: 'Katalog harga', ket: 'margin, harga pasar, label rak', tujuan: { ke: 'harga', keluarga: 'katalog' } }, { nama: 'Struk nota', ket: 'kertas 58/80, kalimat kaki, cetak & WA otomatis', tujuan: { ke: 'jual' } },
  { nama: 'Pelanggan', ket: 'hari tagih, batas macet, salam tagihan', tujuan: { ke: 'pelanggan', keluarga: 'bon' } }, { nama: 'Wadah literan', ket: 'penuh, minta isi ulang, beras per wadah', tujuan: { ke: 'stok', tab: 'wadah' } },
  { nama: 'Perangkat, peran, cadangan, lokasi, pengingat', ket: 'Menu → Toko ini', tujuan: { ke: 'sistem', sistem: 'perangkat' } }, { nama: 'Barang masuk', ket: 'tempo bawaan, toleransi timbangan', tujuan: { ke: 'stok', lembar: 'masuk' } },
];

const LP_BLN = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
const lpKey = (iso) => String(iso).slice(0, 7);
const lpGeserBulan = (key, n) => { const y = Number(key.slice(0, 4)), m = Number(key.slice(5, 7)) - 1 + n; const d = new Date(Date.UTC(y + Math.floor(m / 12), ((m % 12) + 12) % 12, 1)); return d.toISOString().slice(0, 7); };
export const lpNamaBulan = (key) => namaBulanPanjang(key + '-01');
export const lpBulanPendek = (key, tahun) => LP_BLN[Number(key.slice(5, 7)) - 1] + (tahun ? ' ' + key.slice(2, 4) : '');
const lpDigit = (x) => String(x || '').replace(/\D/g, '');
const lpBulat = (n) => Math.round(Number(n) || 0);
/** Tanggal catatan pertama toko (nota atau kedatangan sungguhan) — awal buku. Paket B: catatan tahun yang sudah ditutup buku sudah diarsip → dari potretnya. */
export function lpPertama() { return catatanPertama(); }   // satu sumber dengan Menu: toko.js catatanPertama (sanggahan Paket B)
/** 39b no. 40 (owner 30 Sep): bulan awal buku ('' = belum ada catatan). Bulan SEBELUMNYA tetap tampil dengan keterangan, tetapi tidak dijumlah sebagai laba/rugi. */
export function lpAwalBuku() { const p = lpPertama(); return p ? lpKey(p) : ''; }
/** Keterangan bulan sebelum awal buku: `label` ("Jul 26" / "Mei – Jul 26"), `laba` = Σ laba bersih mesin di bulan-bulan itu (biaya tanpa penjualan). */
export function lpKetSebelumBuku(label, laba) { return label + ' sebelum awal buku (catatan pertama ' + tanggalPendek(lpPertama()) + ') — tampil, tidak dijumlah: penjualannya tidak ada di sistem' + (laba ? ', jadi biaya ' + RP(-laba) + ' yang tercatat di sana bukan rugi toko.' : '.'); }
/** Bulan FINAL = tahunnya sudah ditutup buku (era = tahun saldo pembuka terakhir) ATAU bulannya sudah DIKUNCI (putaran 25: sampaiBulan). Selain itu DRAF. */
export function lpFinal(key) { const era = bkEra(); if (era !== null && Number(key.slice(0, 4)) <= era) return true; const s = kunciSampai(); return !!s && String(key).slice(0, 7) <= s; }
/** Tahun FINAL = era tutup bukunya sudah lewat ATAU kedua belas bulannya terkunci (owner 25 Sep). BUKAN lpFinal(tahun + '-01'): Januari terkunci ≠ setahun final. */
export function lpTahunFinal(tahun) { const era = bkEra(); if (era !== null && Number(tahun) <= era) return true; const s = kunciSampai(); return !!s && s >= tahun + '-12'; }
/** Daftar bulan dari catatan pertama sampai bulan berjalan, TERBARU dulu (paling banyak `maks`). */
export function daftarBulan(kini, maks) { const akhir = lpKey(hariIniIso(kini)); const p = lpPertama(); const awal = p ? lpKey(p) : akhir; const out = []; let k = akhir; while (k >= awal && out.length < (maks || 24)) { out.push({ key: k, nama: lpNamaBulan(k), pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || out.length === 0), final: lpFinal(k), berjalan: k === akhir }); k = lpGeserBulan(k, -1); } return out; }
/** 39b no. 38: nama baris lebih/kurang kas (selisih laci tutup hari) di laba — satu kalimat untuk Laba, laba-rugi berkop & Banding. */
export const lpNamaLebihKurang = (L) => 'Lebih/kurang kas · selisih laci tutup hari (' + L.nLebihKurang + ' malam)';
const lpMdrRentang = (dari, sampai) => ambilPengeluaranHarian().reduce((a, h) => a + ((h.kategori === 'toko' || h.kategori === 'tokoDompet') && adalahMdr(h) && h.tanggal >= dari && h.tanggal <= sampai ? (Number(h.nominal) || 0) : 0), 0);   // 39b no. 24: satu pengenal

// ==================== Paket B (siap 2027): TAHUN YANG SUDAH DITUTUP BUKU dibaca dari POTRET ====================
// Sesudah tutup buku, catatan tahun itu pindah ke arsip (tidak dimuat). Bulan & hari tahun itu dibaca dari potret di berita acaranya (toko.js potretBulan /
// potretHari; disusun potret-logika.js dari fungsi yang SAMA di modul ini) — tidak ada rumus baru. Rentang yang menyentuh tahun itu dijumlah PER BULAN
// (potret untuk bulan yang ditutup, mesin untuk sisanya); uji_potret_tahun.py menjaga Σ bulan = rentang mesin sebelum arsip. Tahun yang ditutup TANPA potret
// disebut (angkanya hanya di berkas arsip & cadangan), tidak digambar Rp0.
const lpTutup = (key) => tahunDiarsip(key);   // tahun yang catatannya DIARSIP tutup buku sistem ini (toko.js)
const lpBulanDari = (dari, sampai) => { const out = []; let k = lpKey(dari); const z = lpKey(sampai); while (k <= z && out.length < 600) { out.push(k); k = lpGeserBulan(k, 1); } return out; };
/** Bulan di [dari, sampai] yang tahunnya sudah ditutup buku. */
export const lpBulanDitutup = (dari, sampai) => lpBulanDari(dari, sampai).filter(lpTutup);
/** Bulan di [dari, sampai] yang tahunnya ditutup TANPA potret (angkanya hanya di berkas arsip) — laporan yang menyentuhnya ditolak, bukan dicetak Rp0. */
export const lpBulanTanpaPotret = (dari, sampai) => lpBulanDari(dari, sampai).filter((k) => lpTutup(k) && !potretBulan(k));
export const lpKalimatTanpaPotret = (kk) => (kk.length ? lpBulanPendek(kk[0], true) + (kk.length > 1 ? ' – ' + lpBulanPendek(kk[kk.length - 1], true) : '') + ' sudah tutup buku tanpa potret — angkanya hanya di berkas arsip & cadangan sebelum tutup buku' : '');
const lpTambahAngka = (L, X) => { Object.keys(X || {}).forEach((f) => { if (typeof X[f] === 'number') L[f] = (L[f] || 0) + X[f]; }); return L; };
/** Laba bersih (ugLabaBersih) untuk rentang BULAN PENUH. Tanpa bulan yang ditutup = ugLabaBersih apa adanya; menyentuh tahun yang ditutup = Σ per bulan
 *  (bulan ditutup: L potret; lainnya: ugLabaBersih bulan itu). Bentuk sama (dariIso/sampaiIso + angka). */
export function lpLabaRentang(dari, sampai, B) {
  if (!lpBulanDitutup(dari, sampai).length) return ugLabaBersih(dari, sampai, B);
  const nol = {}; const K0 = ugLabaBersih('1900-01-01', '1900-01-01', B); Object.keys(K0).forEach((f) => { if (typeof K0[f] === 'number') nol[f] = 0; });   // semua kolom mesin ada, bernilai nol
  const L = lpBulanDari(dari, sampai).reduce((acc, k) => { const Pt = potretBulan(k); return lpTambahAngka(acc, Pt ? Pt.L : lpTutup(k) ? null : ugLabaBersih(k + '-01', akhirBulanIso(k), B)); }, nol);
  return Object.assign(L, { dariIso: dari, sampaiIso: sampai });
}
/** Potongan QRIS (MDR) rentang bulan penuh — bulan ditutup dari potret (labaBulan.mdr). */
const lpMdrLintas = (dari, sampai) => (!lpBulanDitutup(dari, sampai).length ? lpMdrRentang(dari, sampai) : lpBulanDari(dari, sampai).reduce((a, k) => { const Pt = potretBulan(k); return a + (Pt ? Number(Pt.lb && Pt.lb.mdr) || 0 : lpTutup(k) ? 0 : lpMdrRentang(k + '-01', akhirBulanIso(k))); }, 0));
/** Lebih/kurang kas tutup hari rentang bulan penuh — bulan ditutup dari L potret. */
const lpLebihKurangLintas = (dari, sampai) => (!lpBulanDitutup(dari, sampai).length ? ugLebihKurangKas(dari, sampai) : lpBulanDari(dari, sampai).reduce((a, k) => { const Pt = potretBulan(k); const x = Pt ? { n: Number(Pt.L.lebihKurangKas) || 0, malam: Number(Pt.L.nLebihKurang) || 0 } : lpTutup(k) ? { n: 0, malam: 0 } : ugLebihKurangKas(k + '-01', akhirBulanIso(k)); return { n: a.n + x.n, malam: a.malam + x.malam }; }, { n: 0, malam: 0 }));
/** Arus kas (hitungArusKasInti) rentang bulan penuh — menyentuh tahun yang ditutup: Σ per bulan (bulan ditutup: K potret), baris masuk/keluar dijumlah per label. */
export function lpArusRentang(dari, sampai, B) {
  if (!lpBulanDitutup(dari, sampai).length) return hitungArusKasInti((t) => !!t && t >= dari && t <= sampai, B);
  const out = { masuk: [], keluar: [], pos: {} }; const baris = (arah, X) => (X[arah] || []).forEach((r) => { let b = out[arah].find((x) => x.label === r.label); if (!b) { b = { label: r.label, nominal: 0, n: 0, satuan: r.satuan }; out[arah].push(b); } b.nominal += Number(r.nominal) || 0; b.n += Number(r.n) || 0; });
  lpBulanDari(dari, sampai).forEach((k) => { const Pt = potretBulan(k); const X = Pt ? Pt.K : lpTutup(k) ? null : hitungArusKasInti((t) => !!t && t >= k + '-01' && t <= akhirBulanIso(k), B); if (!X) return; baris('masuk', X); baris('keluar', X); lpTambahAngka(out.pos, X.pos); ['totalMasuk', 'totalKeluar', 'bersih', 'omzetPenuh', 'kreditBulanIni', 'jumlahKredit'].forEach((f) => { out[f] = (out[f] || 0) + (Number(X[f]) || 0); }); });
  ['totalMasuk', 'totalKeluar', 'bersih', 'omzetPenuh', 'kreditBulanIni', 'jumlahKredit'].forEach((f) => { out[f] = out[f] || 0; }); return out;
}
/** Omzet & nota per HARI untuk rentang [dari, sampai] (hitungLabaRentang + jumlahNota): hari di tahun yang ditutup dari potret hari, sisanya mesin.
 *  { omzetPenuh, margin, jumlahTanpaHpp, returUang, nota, diarsip: n hari dari potret, tanpaPotret: n hari tanpa potret }. Tanpa hari ditutup = mesin apa adanya. */
export function lpHariRentang(dari, sampai) {
  const cocok = (t) => !!t && t >= dari && t <= sampai; let tutup = []; if (lpBulanDitutup(dari, sampai).length) { let t = dari; while (t <= sampai) { if (lpTutup(t)) tutup.push(t); t = ugTambahHari(t, 1); } }
  const hidup = tutup.length ? (t) => cocok(t) && !lpTutup(t) : cocok; const R = hitungLabaRentang(hidup); const out = { omzetPenuh: R.omzetPenuh, margin: R.margin, jumlahTanpaHpp: R.jumlahTanpaHpp, returUang: R.returUang, nota: jumlahNota(hidup), diarsip: 0, tanpaPotret: 0 };
  tutup.forEach((t) => { const P = potretHari(t); if (!P) { out.tanpaPotret += 1; return; } out.diarsip += 1; out.omzetPenuh += P.omzet; out.margin += P.margin; out.jumlahTanpaHpp += P.tanpaHpp; out.returUang += P.retur; out.nota += P.nota; });
  return out;
}

// ==================== LABA · tiga angka per bulan ====================
/** 39b no. 39 (owner 30 Sep): margin bon DITAHAN dari "diterima tunai" sampai bonnya tertutup, dengan urutan potong yang SAMA dengan buku bon (mesin
 *  hitungPiutang / rincianBelumLunas): pembayaran & hapus buku memadamkan bon TERTUA dulu, uang lebih menunggu bon berikutnya, bon yang baru tertutup
 *  sebagian melepas marginnya SEBANDING (bagian tertutup ÷ nilai bon). Saldo awal & baris tanpa modal = margin 0 (memang tidak pernah ditahan) — kecuali saldo
 *  pembuka tutup buku yang membawa bon asalnya (`marginBon`, Paket B: lpPecahSaldoAwal). Bon & penutup
 *  di hari yang sama: bon dulu (sama dengan buku bon per akhir hari). → margin yang lepas di [dari, sampai], dipisah `dibayar` (jadi uang) dan `dihapus`
 *  (hapus buku: laba bersih bulan itu sudah memotong SELURUH nilai bon, termasuk marginnya — kalau tetap ditahan, margin itu terpotong dua kali).
 *  Audit 39b no. 37: `diretur` = bon yang ditutup barang yang kembali dari nota bon (mutasi retur) — laba sudah memotongnya lewat retur (penjualan turun,
 *  modal barang utuh kembali), jadi marginnya juga tidak ditahan lagi; urutan potongnya sama dengan mesin (tinjauan U37-U5: NOTA ASALNYA dulu, sisanya bon tertua). */
export function lpMarginBonLepas(dari, sampai) { return lpJalanBon(dari, sampai).out; }
/** Paket B (sanggahan): bon yang MASIH TERBUKA per pelanggan pada `batas` (urutan potong sama: tertua dulu) → { kunci: [{ sisa, nilai, margin, nota? }] }. Dibawa
 *  saldo pembuka tutup buku (tutup-buku-logika pembukaBuku → piutangMutasi saldoAwal.marginBon), supaya margin bon tahun lalu yang dibayar SESUDAH ritual tetap
 *  kembali ke "diterima tunai" bulan bayarnya — sama persis dengan sebelum ritual (dijaga uji_potret_tahun: Januari sebelum = sesudah). */
export function lpBonTerbuka(batas) { return lpJalanBon('', '', batas).terbuka; }
/** Saldo awal pembuka yang membawa `marginBon` dipecah lagi jadi bon-bon asalnya (sisa saat dibuka, nilai & margin asli, nota) — tanpa ini saldo awal = margin 0,
 *  jadi margin bon 2026 yang dibayar Januari 2027 tidak pernah dilepas. Σ sisa harus = nominal dokumennya; kalau tidak (diubah tangan), dibaca seperti saldo awal biasa. */
function lpPecahSaldoAwal(d, dok) {
  if (!d.mutasi.some((m) => m.jenis === 'saldoAwal' && dok[String(m.idMutasi)])) return d;
  const mutasi = []; d.mutasi.forEach((m) => { const x = m.jenis === 'saldoAwal' ? dok[String(m.idMutasi)] : null; const mb = x ? x.marginBon : null;
    if (!mb || Math.abs(mb.reduce((a, b) => a + (Number(b && b.sisa) || 0), 0) - (Number(m.nominal) || 0)) >= 1) { mutasi.push(m); return; }
    mb.forEach((b) => { const nota = b && b.nota !== undefined && b.nota !== null ? b.nota : null;
      mutasi.push({ jenis: nota !== null ? 'jual' : 'saldoAwal', tanggal: m.tanggal, jam: m.jam, idTrx: nota, nominal: Number(b.nilai) || 0, sisaAwal: Number(b.sisa) || 0, margin: Number(b.margin) || 0, sub: true }); }); });
  return Object.assign({}, d, { mutasi });
}
/** Satu jalan mesin margin bon untuk dua pembaca: margin yang lepas di [dari, sampai] (`out`) dan bon yang masih terbuka pada `batas` (`terbuka`). */
function lpJalanBon(dari, sampai, batas) {
  const baris = {}; ambilPenjualan().forEach((p) => { baris[p.id] = p; });
  const dok = {}; ambilPiutangMutasi().forEach((m) => { if (m && m.tipe === 'saldoAwal' && Array.isArray(m.marginBon) && m.marginBon.length) dok[String(m.id)] = m; });
  const mg = (u) => { if (u.sub) return u.margin; const p = u.jenis === 'jual' ? baris[u.idTrx] : null; return p && hppTercatat(p) ? (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0) : 0; };
  const out = { dibayar: 0, dihapus: 0, diretur: 0 }; const terbuka = {};
  hitungPiutang(batas || undefined).map((d) => lpPecahSaldoAwal(d, dok)).forEach((d) => {
    const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));
    const tutup = d.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')) || String(x.jam || '').localeCompare(String(y.jam || '')));
    const buka = []; const lebih = []; const ditutupHapus = []; let j = 0;
    const pakai = (b, x, jenis, t) => { b.sisa -= x; if (jenis === 'hapusBuku') ditutupHapus.push({ b, x }); if (b.u.nominal > 0 && t >= dari && t <= sampai) out[jenis === 'bayar' ? 'dibayar' : jenis === 'retur' ? 'diretur' : 'dihapus'] += mg(b.u) * x / b.u.nominal; };
    const lahir = (t) => { while (j < utang.length && String(utang[j].tanggal || '') <= t) { const b = { u: utang[j], i: j, sisa: Math.max(0, (utang[j].sub ? utang[j].sisaAwal : utang[j].nominal) || 0) }; j++;
      while (b.sisa > 0 && lebih.length) { const k = lebih[0]; const x = Math.min(k.n, b.sisa); pakai(b, x, k.jenis, String(b.u.tanggal || '')); k.n -= x; if (k.n <= 0) lebih.shift(); }
      if (b.sisa > 0) buka.push(b); } };
    // Paket F2 (owner 8 Okt 2026): hapus buku BERNILAI MINUS = hapus buku DIBALIK (dibayar sesudah dihapus, bon-logika susunBayarSesudahHapus). Yang terakhir
    // ditutup hapus buku dibuka lagi (terbaru dulu): hapus buku yang masih menunggu bon (lebih) dibatalkan dulu, lalu bon yang ditutupnya kembali terbuka dan
    // marginnya DITARIK dari `dihapus` pada tanggal pembalikan (laba bersih naik lewat hapus buku minus — kalau margin tetap dilepas, terhitung dua kali); uang
    // yang sedang menunggu bon (lebih: bayar / retur — invarian: lebih ada ⇒ tidak ada bon terbuka) langsung menutup bon yang terbuka lagi, tertua dulu.
    const balik = (r, t) => {
      for (let i = lebih.length - 1; i >= 0 && r > 0; i--) { if (lebih[i].jenis !== 'hapusBuku') continue; const x = Math.min(r, lebih[i].n); lebih[i].n -= x; r -= x; if (lebih[i].n <= 0) lebih.splice(i, 1); }
      while (r > 0 && ditutupHapus.length) { const z = ditutupHapus[ditutupHapus.length - 1]; const x = Math.min(r, z.x); z.x -= x; r -= x; if (z.x <= 0) ditutupHapus.pop();
        const b = z.b; const tadi = b.sisa; b.sisa += x; if (b.u.nominal > 0 && t >= dari && t <= sampai) out.dihapus -= mg(b.u) * x / b.u.nominal;
        if (tadi <= 0) { buka.push(b); buka.sort((p, q) => p.i - q.i); } }
      for (let k = 0; k < buka.length && lebih.length;) { const b = buka[k]; const L0 = lebih[0]; const x = Math.min(L0.n, b.sisa); pakai(b, x, L0.jenis, t); L0.n -= x; if (L0.n <= 0) lebih.shift(); if (b.sisa <= 0) buka.splice(k, 1); else k += 1; }
    };
    tutup.forEach((c) => { const t = String(c.tanggal || ''); lahir(t); let n = c.nominal || 0;
      if (c.jenis === 'hapusBuku' && n < 0) { balik(-n, t); return; }
      // tinjauan U37-U5: retur nota bon melepas margin NOTA ASALNYA dulu (sama dengan mesin hitungPiutang, MM1), sisanya bon tertua dulu
      if (c.jenis === 'retur' && c.notaAsalId != null) { const i = buka.findIndex((b) => b.u.jenis === 'jual' && String(b.u.idTrx) === String(c.notaAsalId)); if (i >= 0) { const b = buka[i]; const x = Math.min(n, b.sisa); pakai(b, x, 'retur', t); n -= x; if (b.sisa <= 0) buka.splice(i, 1); } }
      while (n > 0 && buka.length) { const b = buka[0]; const x = Math.min(n, b.sisa); pakai(b, x, c.jenis, t); n -= x; if (b.sisa <= 0) buka.shift(); }
      if (n > 0) lebih.push({ n, jenis: c.jenis }); });
    lahir('\uffff');
    if (buka.length) terbuka[d.kunci] = buka.map((b) => Object.assign({ sisa: b.sisa, nilai: b.u.nominal || 0, margin: mg(b.u) }, b.u.jenis === 'jual' && b.u.idTrx !== undefined && b.u.idTrx !== null ? { nota: b.u.idTrx } : {}));
  });
  return { out, terbuka };
}
/** Laba satu bulan lewat mesin yang sama dengan kaca Laba sistem lama: margin kotor · laba bersih · diterima tunai (= bersih − margin nota bon bulan itu +
 *  margin bon yang tertutup bulan itu, lpMarginBonLepas — 39b no. 39; bon yang ditutup retur barang ikut, no. 37: `marginDiretur` hanya ada bila bukan nol,
 *  supaya bulan tanpa retur nota bon berbentuk sama persis dengan sebelumnya). */
const lpPctLaba = (a, b) => (b > 0 ? (a < 0 ? '−' : '') + Math.abs(a / b * 100).toFixed(1).replace('.', ',') + '%' : '—');
/** Paket B · labaBulan bulan yang sudah ditutup buku: angka dari potret (bentuk sama); daftar per nota (rugi, tanpa modal, susut) ikut arsip — jumlahnya tetap
 *  disebut lewat `dalamArsip` (potret-logika: nRugi, nRugiNota, rugiRp, nTanpaHpp, nTanpaHppNota, nSusut). */
function lpLabaPotret(key, Pt) {
  const L = Object.assign({ dariIso: key + '-01', sampaiIso: akhirBulanIso(key) }, Pt.L);
  return Object.assign({}, Pt.lb, { key, nama: lpNamaBulan(key), berjalan: false, final: lpFinal(key), L, margin: L.margin, labaBersih: L.labaBersih, susut: [], rugi: [], tanpaHpp: [], aman: null, diarsip: true, pct: lpPctLaba });
}
export function labaBulan(key, kini, bayaran) {
  const Pt = potretBulan(key); if (Pt && Pt.lb) return lpLabaPotret(key, Pt);   // Paket B: tahun yang sudah ditutup buku
  const iso = hariIniIso(kini); const awal = key + '-01', akhir = akhirBulanIso(key); const B = bayaran || bayaranBiayaBulanan(); const L = ugLabaBersih(awal, akhir, B);
  let marginKredit = 0, omzetKredit = 0; const notaKredit = new Set(); ambilPenjualan().forEach((p) => { if (!p.tanggal || p.tanggal < awal || p.tanggal > akhir || caraBayarKunci(p) !== 'kredit') return; notaKredit.add(kunciNota(p)); omzetKredit += p.hargaTotal || 0; if (hppTercatat(p)) marginKredit += (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0); });
  const nKredit = notaKredit.size;   // tinjauan rantai laporan T2: NOTA bon, bukan baris
  const lepas = lpMarginBonLepas(awal, akhir); const marginDibayar = Math.round(lepas.dibayar); const marginDihapus = Math.round(lepas.dihapus); const marginDiretur = Math.round(lepas.diretur);
  const tunai = L.labaBersih - marginKredit + marginDibayar + marginDihapus + marginDiretur; const omzetKotor = L.omzetHitung + L.returUang; const penyebut = omzetKotor + L.omzetTanpaHpp; const cakupan = penyebut > 0 ? omzetKotor / penyebut : null;
  const mdr = lpMdrRentang(awal, akhir); const biayaLain = L.biayaToko - mdr;
  const terjun = [['Penjualan terhitung', omzetKotor]].concat(L.returJumlah ? [['Retur & refund (' + L.returJumlah + ')', -L.returUang]] : []).concat([['HPP barang', -(L.hpp + L.returHpp)]]).concat(L.returHpp > 0 ? [['HPP barang yang kembali ke stok', L.returHpp]] : [])
    .concat([['Margin kotor', L.margin, 'jumlah'], ['Biaya toko (harian + jatah bulanan)', -biayaLain]]).concat(mdr ? [['Potongan QRIS (MDR)', -mdr]] : []).concat(L.hapusBuku ? [['Hapus buku piutang', -L.hapusBuku]] : []).concat([['Susut & selisih stok', L.susutStok]]).concat(L.lebihKurangKas ? [[lpNamaLebihKurang(L), L.lebihKurangKas]] : []).concat([['Laba bersih', L.labaBersih, 'jumlah']]).map((r) => ({ nama: r[0], n: r[1], kelas: r[2] || '' }));
  const cocok = (t) => !!t && t >= awal && t <= akhir; const susut = barisSusutStok(cocok);
  const bulan = ambilPenjualan().filter((p) => cocok(p.tanggal)); const rugi = bulan.filter((p) => hppTercatat(p) && (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0) < 0).map((p) => ({ id: p.id, nota: kunciNota(p), nama: namaSingkatTrx(p), tanggal: p.tanggal, jam: p.jam || '', omzet: p.hargaTotal || 0, margin: (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0) })).sort((a, b) => a.margin - b.margin);
  const tanpaHpp = bulan.filter((p) => !hppTercatat(p)).map((p) => ({ id: p.id, nota: kunciNota(p), nama: namaSingkatTrx(p), tanggal: p.tanggal, jam: p.jam || '', omzet: p.hargaTotal || 0 })).sort((a, b) => String(b.tanggal + b.jam).localeCompare(String(a.tanggal + a.jam)));
  const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && !susut.length; const berjalan = key === lpKey(iso);
  let aman = null; if (berjalan) { const A = aturKeluar(iso); const P = priveBulan(iso); aman = { batas: A.aman, dariLaba: A.amanDariLaba, terpakai: P.total, sisa: A.aman - P.total }; }
  return Object.assign({ key, nama: lpNamaBulan(key), berjalan, final: lpFinal(key), L, margin: L.margin, labaBersih: L.labaBersih, tunai, marginKredit, marginDibayar, marginDihapus, omzetKredit, nKredit, cakupan, omzetKotor, penyebut, mdr, biayaLain, terjun, susut, susutTotal: L.susutStok, rugi, tanpaHpp, omzetTanpaHpp: L.omzetTanpaHpp, tanpaCatatan, aman,
    pct: lpPctLaba }, marginDiretur ? { marginDiretur } : {});
}

// ==================== LABA KOTOR → KE MANA (putaran 29, owner 27 Sep 2026) ====================
/** Satu kartu per bulan: ke mana laba kotor pergi — biaya toko · biaya karyawan (upah + non-upah, dipisah) · hapus buku · susut & selisih stok (mesin menaruhnya
 *  di BAWAH laba kotor) · = laba bersih mesin · ambil pribadi owner · sisa. SEMUA angka dari hitungLabaBersihRentang + bayaranBiayaBulanan yang sama, cuma
 *  dipilah dengan kategori (pilahHarian: kolom `untuk`); tidak ada rumus laba baru. Bulan terkunci/tutup buku = final. Bulan tanpa satu catatan pun disebut begitu. */
const lpPctKeMana = (L) => (a) => (L.margin > 0 ? (a < 0 ? '−' : '') + Math.abs(a / L.margin * 100).toFixed(1).replace('.', ',') + '%' : '—');
export function keManaLabaKotor(key, kini, bayaran) {
  const Pt = potretBulan(key); if (Pt && Pt.km) { const L = Object.assign({ dariIso: key + '-01', sampaiIso: akhirBulanIso(key) }, Pt.L); return Object.assign({}, Pt.km, { key, nama: lpNamaBulan(key), berjalan: false, final: lpFinal(key), L, diarsip: true, pct: lpPctKeMana(L) }); }   // Paket B
  const iso = hariIniIso(kini); const awal = key + '-01', akhir = akhirBulanIso(key); const B = bayaran || bayaranBiayaBulanan(); const L = ugLabaBersih(awal, akhir, B);
  const P = pilahHarian(awal, akhir);   // Σ = L.harianToko
  const gajiRows = B.filter((x) => x.bulan === key && String(x.pos || '').indexOf('gaji:') === 0); const upah = gajiRows.reduce((a, x) => a + (x.nominalKotor === undefined ? x.nominal : x.nominalKotor), 0);
  const posLain = L.jatahBulanan - upah;   // jatah pos bulanan bukan gaji (listrik, akses, keamanan, internet) — dari jatah yang sama dengan mesin, jadi selalu menutup
  const biayaToko = P.tokoSemua + posLain; const nonUpah = P.karyawan; const biayaKaryawan = upah + nonUpah;
  const Pr = priveRentang(awal, akhir); const sisa = L.labaBersih - Pr.total;
  const menutup = Math.abs((L.margin - biayaToko - biayaKaryawan - L.hapusBuku + L.susutStok + L.lebihKurangKas) - L.labaBersih) < 0.5 && Math.abs(P.total - L.harianToko) < 0.5;
  const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && L.nSusut === 0 && !gajiRows.length && !L.jatahBulanan;
  const baris = [{ id: 'kotor', nama: 'Laba kotor', n: L.margin, kelas: 'jumlah', ket: 'omzet ber-HPP − HPP-nya' },
    { id: 'toko', nama: 'Biaya toko', n: -biayaToko, ket: [P.nToko + P.nBelum ? 'harian ' + RP(P.tokoSemua) + (P.mdr || P.bank ? ' (termasuk ' + [P.mdr ? 'potongan QRIS ' + RP(P.mdr) : '', P.bank ? 'biaya bank ' + RP(P.bank) : ''].filter(Boolean).join(' & ') + ')' : '') : '', posLain ? 'jatah tagihan bulanan ' + RP(posLain) : ''].filter(Boolean).join(' + ') || 'tidak ada', belumDipilah: P.nBelum, belumDipilahRp: P.belum },
    { id: 'upah', nama: 'Biaya karyawan · upah', n: -upah, ket: gajiRows.length ? gajiRows.length + ' baris gaji kotor, dibagi rata per hari (mesin lama)' : 'tidak ada baris gaji bulan ini' },
    { id: 'karyawan', nama: 'Biaya karyawan · di luar upah', n: -nonUpah, ket: P.nKaryawan ? P.nKaryawan + ' catatan "untuk karyawan" (kopi, rokok, makan warung)' : 'belum ada catatan "untuk karyawan"' }]
    .concat(L.hapusBuku ? [{ id: 'hapus', nama: 'Hapus buku piutang', n: -L.hapusBuku, ket: L.nHapus + ' catatan' }] : [])
    .concat([{ id: 'susut', nama: 'Susut & selisih stok', n: L.susutStok, ket: L.nSusut ? L.nSusut + ' baris · di bawah laba kotor, tidak menyentuh kas' : 'tidak ada' }])
    .concat(L.lebihKurangKas ? [{ id: 'lebihKurang', nama: 'Lebih/kurang kas', n: L.lebihKurangKas, ket: 'selisih laci tutup hari · ' + L.nLebihKurang + ' malam' }] : [])
    .concat([{ id: 'bersih', nama: 'Laba bersih', n: L.labaBersih, kelas: 'jumlah', ket: 'mesin yang sama dengan Laba' },
      { id: 'prive', nama: 'Ambil pribadi owner', n: -Pr.total, ket: [Pr.prive ? 'dari laci ' + RP(Pr.prive) : '', Pr.alih ? 'kasbon dialihkan ' + RP(Pr.alih) : '', Pr.tarik ? 'tarik modal ' + RP(Pr.tarik) : ''].filter(Boolean).join(' · ') || 'tidak ada' },
      { id: 'sisa', nama: 'Sisa di toko', n: sisa, kelas: 'jumlah', ket: 'laba bersih − ambil pribadi' }]);
  return { key, nama: lpNamaBulan(key), berjalan: key === lpKey(iso), final: lpFinal(key), tanpaCatatan, L, labaKotor: L.margin, biayaToko, upah, nonUpah, biayaKaryawan, hapusBuku: L.hapusBuku, susut: L.susutStok, labaBersih: L.labaBersih, prive: Pr.total, priveRinci: Pr, sisa, menutup, pilah: P, posLain, baris,
    belumDipilah: P.nBelum, belumDipilahRp: P.belum, pct: lpPctKeMana(L) };
}

// ==================== HARIAN · rekap satu hari ====================
/** Rekap satu hari — arus kas & laba dari mesin yang sama (dataRekapHarian sistem lama) + per jam + tutup hari + buku kas hari itu. */
export function rekapHari(iso, bayaran) {
  if (lpTutup(iso)) return lpHariArsip(iso);   // Paket B: hari di tahun yang sudah ditutup buku
  const B = bayaran || bayaranBiayaBulanan(); const K = hitungArusKasInti((t) => t === iso, B); const L = hitungLabaRentang((t) => t === iso);
  const jam = {}; const notaJam = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== iso) return; const j = String(p.jam || '').slice(0, 2) || '??'; if (!jam[j]) { jam[j] = { jam: j, n: 0, omzet: 0 }; notaJam[j] = new Set(); } notaJam[j].add(kunciNota(p)); jam[j].n = notaJam[j].size; jam[j].omzet += p.hargaTotal || 0; });   // n = nota, bukan baris (39b no. 20)
  const perJam = Object.keys(jam).sort().map((j) => jam[j]); const maksJam = Math.max(1, ...perJam.map((x) => x.omzet));
  // siap 2027 (A4): saldo pembuka modal owner tutup buku (31 Des 00.00) bukan gerakan uang — tidak digambar di buku kas hari itu
  const pembukaModal = {}; cacheMentah('modal').forEach((m) => { if (m && m.tutupBuku) pembukaModal[String(m.id)] = true; });
  const tutup = ambilTutupHari().find((t) => t.tanggal === iso) || null; const buku = ingatGerakanKas().filter((r) => r.t === iso && !pembukaModal[String(r.id)]).sort((a, b) => String(a.jam).localeCompare(String(b.jam)));
  return { iso, omzet: L.omzetPenuh, retur: Math.round(((returUangPerHari()[iso] || {}).uang) || 0), n: jumlahNota((t) => t === iso), margin: L.margin, jumlahTanpaHpp: L.jumlahTanpaHpp, tunai: K.pos.tunai, qris: K.pos.qris, kredit: K.kreditBulanIni, nKredit: jumlahNota((t) => t === iso, (p) => caraBayarKunci(p) === 'kredit'), pelunasan: K.pos.pelunasan, refund: K.pos.refund, keluarHarian: K.pos.harian, prive: K.pos.prive, setoran: K.pos.setoran, belanja: K.pos.belanja, bayarBon: K.pos.bayarBon, biayaBulanan: K.pos.biayaBulanan,
    totalMasuk: K.totalMasuk, totalKeluar: K.totalKeluar, bersih: K.bersih, masuk: K.masuk.filter((x) => x.nominal > 0), keluar: K.keluar.filter((x) => x.nominal > 0), perJam, maksJam, tutup: tutup ? { jam: tutup.jam || '', selisih: Number(tutup.selisihLaci || tutup.selisih || 0), sistemBaru: !!tutup.sistemBaru } : null, buku, kosong: L.jumlahTrx === 0 && K.totalMasuk === 0 && K.totalKeluar === 0 };
}
/** Paket B · rekap hari di tahun yang sudah ditutup buku: omzet, nota, margin dari potret hari; uang per cara bayar, per jam, arus kas & buku kas hari itu
 *  ikut arsip → null / kosong dan `diarsip` (layar menyebutnya, tidak menggambar Rp0). Tahun tanpa potret: `tanpaPotret`. */
function lpHariArsip(iso) {
  const P = potretHari(iso); const x = P || { omzet: null, margin: null, tanpaHpp: 0, retur: null, nota: 0 }; const kos = ['tunai', 'qris', 'kredit', 'pelunasan', 'refund', 'keluarHarian', 'prive', 'setoran', 'belanja', 'bayarBon', 'biayaBulanan', 'totalMasuk', 'totalKeluar', 'bersih'];
  const R = { iso, omzet: x.omzet, retur: x.retur, n: x.nota, margin: x.margin, jumlahTanpaHpp: x.tanpaHpp, nKredit: 0, masuk: [], keluar: [], perJam: [], maksJam: 1, tutup: null, buku: [], kosong: !!P && !x.nota && !x.omzet && !x.retur, diarsip: true, tanpaPotret: !P };
  kos.forEach((k) => { R[k] = null; }); return R;
}
/** Empat belas hari terakhir untuk pemilih tanggal: omzet & jumlah nota per hari (yang kosong tetap ada, ditandai). Paket B: hari di tahun yang sudah ditutup = potret hari. */
export function hariTerakhir(kini, n) { const iso = hariIniIso(kini); const per = {}; const notaHari = {}; const retur = returUangPerHari();   // 39b no. 19: omzet = penjualan − uang retur (sama dengan rekap harinya)
  ambilPenjualan().forEach((p) => { if (!p.tanggal) return; if (!per[p.tanggal]) { per[p.tanggal] = { n: 0, omzet: 0 }; notaHari[p.tanggal] = new Set(); } notaHari[p.tanggal].add(kunciNota(p)); per[p.tanggal].n = notaHari[p.tanggal].size; per[p.tanggal].omzet += p.hargaTotal || 0; }); const out = []; for (let i = 0; i < (n || 14); i++) { const t = ugTambahHari(iso, -i);
    if (lpTutup(t)) { const P = potretHari(t); out.push({ iso: t, n: P ? P.nota : 0, omzet: P ? P.omzet : 0, hariIni: i === 0, diarsip: true, tanpaPotret: !P }); continue; }
    out.push({ iso: t, n: per[t] ? per[t].n : 0, omzet: (per[t] ? per[t].omzet : 0) - ((retur[t] || {}).uang || 0), hariIni: i === 0 }); } return out; }
/** Audit 39b no. 37 tinjauan U37-U4: retur nota BON hari itu (bon dipotong, bukan uang laci) = uang retur rekap (uangKembaliRetur, termasuk potongBon) − refund
 *  kas (nominalRefund + selisih tukar). Kartu rekap & teks WA menyebutnya supaya omzet = tunai + QRIS + bon − refund − retur nota bon menutup. */
export const lpReturBonHari = (R) => Math.max(0, Math.round((R.retur || 0) - (R.refund || 0)));
/** Teks rekap untuk WhatsApp — kalimat kirimRekapHarianWa sistem lama, ditambah yang dulu tidak disebut (pelunasan bon, prive, margin). */
export function teksRekapHari(R, kop) {
  const b = ['*Rekap ' + ((kop && kop.nama) || IDENTITAS_BAWAAN.nama) + ' — ' + tanggalPendek(R.iso) + '*', 'Omzet: ' + RP(R.omzet) + ' (' + R.n + ' nota)', 'Tunai: ' + RP(R.tunai), 'QRIS: ' + RP(R.qris)];
  if (R.kredit) b.push('Bon (belum jadi uang): ' + RP(R.kredit) + ' · ' + R.nKredit + ' nota'); if (R.pelunasan) b.push('Pembayaran bon pelanggan: ' + RP(R.pelunasan)); if (R.refund) b.push('Refund & tukar retur: ' + RP(R.refund));
  const rb = lpReturBonHari(R); if (rb) b.push('Retur nota bon (bon dipotong): ' + RP(rb));
  if (R.keluarHarian) b.push('Belanja & biaya toko: ' + RP(R.keluarHarian)); if (R.belanja) b.push('Belanja beras tunai + bongkar: ' + RP(R.belanja)); if (R.bayarBon) b.push('Bayar bon pemasok: ' + RP(R.bayarBon)); if (R.biayaBulanan) b.push('Tagihan bulanan: ' + RP(R.biayaBulanan));
  if (R.prive) b.push('Ambil pribadi owner: ' + RP(R.prive)); if (R.setoran) b.push('Setoran ke owner: ' + RP(R.setoran));
  b.push('Kas bersih hari ini: ' + RP(R.bersih)); b.push('Margin kotor: ' + RP(R.margin) + (R.jumlahTanpaHpp ? ' (' + R.jumlahTanpaHpp + ' baris tanpa modal tidak ikut)' : '')); if (R.tutup) b.push('Sudah tutup hari' + (R.tutup.jam ? ' ' + R.tutup.jam : '')); return b.join('\n');
}

// ==================== BULANAN · enam bulan, inti bulan, DK3 rekap omzet ====================
// Paket B: omzet & nota per bulan lewat pjOmzetSistem — fungsi yang SAMA (hitungLabaRentang bulan itu + jumlahNota), dan bulan di tahun yang ditutup membaca potret
export function enamBulan(kini) { const akhir = lpKey(hariIniIso(kini)); const out = []; for (let i = 5; i >= 0; i--) { const k = lpGeserBulan(akhir, -i); const S = pjOmzetSistem(k); const tp = lpTutup(k) && !potretBulan(k); out.push(Object.assign({ key: k, pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || i === 5), omzet: S.omzet, n: S.n, berjalan: k === akhir }, tp ? { tanpaPotret: true } : {})); } const maks = Math.max(1, ...out.map((x) => x.omzet)); return { daftar: out, maks }; }
export function intiBulan(key, kini, bayaran) {
  const Pt = potretBulan(key); if (Pt && Pt.inti) return Object.assign({}, Pt.inti, { key, nama: lpNamaBulan(key), berjalan: false, final: lpFinal(key), diarsip: true });   // Paket B
  const iso = hariIniIso(kini); const B = bayaran || bayaranBiayaBulanan(); const awal = key + '-01', akhir = akhirBulanIso(key); const L = ugLabaBersih(awal, akhir, B); const K = hitungArusKasInti((t) => !!t && t >= awal && t <= akhir, B);
  const berjalan = key === lpKey(iso); const hariJalan = berjalan ? Number(iso.slice(8, 10)) : Number(akhir.slice(8, 10)); const belum = B.filter((x) => !x.tanggal && x.bulan === key && x.nominal > 0);
  return { key, nama: lpNamaBulan(key), berjalan, final: lpFinal(key), hariJalan, omzet: L.omzetPenuh, rataHari: hariJalan ? Math.round(L.omzetPenuh / hariJalan) : 0, hpp: L.hpp, omzetTanpaHpp: L.omzetTanpaHpp, jumlahTanpaHpp: L.jumlahTanpaHpp, margin: L.margin, biayaToko: L.biayaToko, labaBersih: L.labaBersih, keluar: K.totalKeluar, masuk: K.totalMasuk, bersih: K.bersih, kredit: K.kreditBulanIni, belumBayar: belum.map((x) => ({ label: x.label, n: x.nominal })), belumBayarTotal: belum.reduce((a, x) => a + x.nominal, 0) };
}
export const ATUR_REKAP_BAWAAN = { tarifPerMil: 0, batasOmzet: 0, tanggalLapor: 15 };
export function aturRekap() { const a = ugAturDok('rekapOmzet') || {}; const ang = (v, b) => (isFinite(Number(v)) && Number(v) >= 0 ? Math.round(Number(v)) : b); return { tarifPerMil: ang(a.tarifPerMil, 0), batasOmzet: ang(a.batasOmzet, 0), tanggalLapor: isFinite(Number(a.tanggalLapor)) && Number(a.tanggalLapor) >= 1 && Number(a.tanggalLapor) <= 28 ? Math.round(Number(a.tanggalLapor)) : 15, lapor: a.lapor && typeof a.lapor === 'object' ? a.lapor : {}, dariOwner: !!ugAturDok('rekapOmzet') }; }
export const tarifTeks = (n) => (n / 10).toFixed(1).replace('.', ',') + '%';
export function susunAturRekap(isi, w) {
  const A = aturRekap(); const tarif = ugKosong(isi.tarifPerMil) ? 0 : ugAngka(isi.tarifPerMil); const batas = ugKosong(isi.batasOmzet) ? 0 : ugAngka(isi.batasOmzet); const tgl = ugKosong(isi.tanggalLapor) ? 15 : ugAngka(isi.tanggalLapor);
  if (!(tarif >= 0 && tarif <= 1000)) return { tolak: 'Tarif ditulis per seribu: 0–1000 (5 = 0,5 % dari omzet)' }; if (batas < 0) return { tolak: 'Batas omzet tidak boleh minus' }; if (!(tgl >= 1 && tgl <= 28)) return { tolak: 'Tanggal lapor 1–28' };
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap({ tarifPerMil: Math.round(tarif), batasOmzet: Math.round(batas), tanggalLapor: Math.round(tgl), lapor: A.lapor }, w) }], patch: { aturR: null, kabar: 'Setelan rekap omzet tersimpan — ' + (tarif ? 'tarif perkiraan ' + tarifTeks(tarif) : 'tanpa kolom perkiraan') + ' · ' + (batas ? 'batas ' + RP(batas) : 'batas belum diatur') + ' · lapor tiap tanggal ' + Math.round(tgl) + '. Ini setelan owner, bukan nasihat pajak.', kabarAwas: false } };
}
/** DK3: 12 bulan omzet (mesin laba, satu sumber), kumulatif tahun berjalan, tanda dilaporkan, tarif & batas setelan owner, tempo lapor. */
export function rekapOmzet(kini) {
  const iso = hariIniIso(kini); const akhir = lpKey(iso); const tahunIni = Number(akhir.slice(0, 4)); const A = aturRekap(); const daftar = []; let kum = 0; const p0 = lpPertama(); const awalBuku = p0 ? lpKey(p0) : akhir;
  // putaran 24: omzet = pjOmzetSistem (satu sumber dengan layar Pajak); perkiraan = hitungan pajak (dengan batas bebas) — dua layar, satu angka
  const PJ = {}; const pjBulan = (k) => { const th = Number(k.slice(0, 4)); if (!PJ[th]) PJ[th] = pjTahun(th, kini); return PJ[th].daftar.find((b) => b.key === k) || null; };
  // Paket B: bulan di tahun yang sudah ditutup buku = potret (lewat pjOmzetSistem); ditutup TANPA potret = `tanpaPotret` (angkanya hanya di arsip — bukan Rp0)
  for (let i = 11; i >= 0; i--) { const k = lpGeserBulan(akhir, -i); const S = pjOmzetSistem(k); const th = Number(k.slice(0, 4)); if (th === tahunIni) kum += S.omzet; const pb = A.tarifPerMil ? pjBulan(k) : null;
    daftar.push(Object.assign({ key: k, nama: lpNamaBulan(k), pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || i === 11), omzet: S.omzet, n: S.n, final: lpFinal(k), berjalan: i === 0, absen: k < awalBuku, kum: th === tahunIni ? kum : null, lapor: A.lapor[k] || null, perkiraan: pb ? pb.pph : null, perkiraanLengkap: pb ? pb.lengkapSejauhIni : false }, lpTutup(k) && !potretBulan(k) ? { tanpaPotret: true } : {})); }
  const totalTahun = kum; const pjIni = A.tarifPerMil ? (PJ[tahunIni] || pjTahun(tahunIni, kini)) : null; const adaTarif = A.tarifPerMil > 0, adaBatas = A.batasOmzet > 0; const lewatBatas = adaBatas && totalTahun > A.batasOmzet; const finalTerakhir = daftar.filter((b) => b.final).pop() || null;
  const belumLapor = daftar.filter((b) => b.final && Number(b.key.slice(0, 4)) === tahunIni && !b.lapor); const hariIni = Number(iso.slice(8, 10)); const maks = Math.max(1, ...daftar.map((b) => b.omzet));
  let tempo = null; if (finalTerakhir) { const bulanBerikut = lpGeserBulan(finalTerakhir.key, 1); const lewat = akhir > bulanBerikut || (akhir === bulanBerikut && hariIni > A.tanggalLapor); tempo = { bulan: finalTerakhir, teks: 'lapor ' + lpBulanPendek(finalTerakhir.key) + ' paling lambat ' + A.tanggalLapor + ' ' + lpBulanPendek(bulanBerikut), sudah: !!finalTerakhir.lapor, lewat: !finalTerakhir.lapor && lewat, sisaHari: akhir === bulanBerikut ? A.tanggalLapor - hariIni : null }; }
  return { daftar, maks, tahunIni, totalTahun, adaTarif, adaBatas, lewatBatas, sisaBatas: adaBatas ? A.batasOmzet - totalTahun : null, perkiraanTahun: pjIni ? pjIni.totalPph : null, A, finalTerakhir, belumLapor, tempo, adaFinal: !!finalTerakhir,
    totalTeks: 'Tahun ' + tahunIni + ' sampai ' + lpBulanPendek(akhir) + ' (omzet di sistem saja): ' + RP(totalTahun) + (adaBatas ? (lewatBatas ? ' — LEWAT batas yang diatur owner (' + RP(A.batasOmzet) + ')' : ' — ' + RP(A.batasOmzet - totalTahun) + ' lagi sampai batas yang diatur owner') : ' — batas belum diatur (Atur)') + '. Kumulatif lengkap dengan omzet di luar sistem: Laporan › Pajak',
    tarifTeks: pjIni ? (pjIni.totalPph === null ? 'Perkiraan PPh tidak dihitung (jenis wajib pajak: badan — tanyakan konsultan)' : 'Perkiraan PPh ' + tarifTeks(A.tarifPerMil) + (pjIni.P.batasBebas ? ' sesudah batas bebas ' + RP(pjIni.P.batasBebas) : ' (batas bebas belum diisi)') + ': tahun ini ' + RP(pjIni.totalPph) + (pjIni.kosong ? ' — ' + pjIni.kosong + ' bulan belum diisi, bisa kurang' : '') + ' — ' + PJ_LABEL) : 'Tarif belum diatur → kolom perkiraan tidak dicetak (Atur)' };
}
/** Tandai / batalkan tanda "sudah dilaporkan" satu bulan — hanya bulan FINAL; membatalkan butuh ketukan kedua. */
export function susunTandaLapor(key, w, yakin) {
  const A = aturRekap(); if (!lpFinal(key)) return { tolak: lpNamaBulan(key) + ' belum dikunci / belum tutup buku — angkanya masih bisa berubah, jangan dilaporkan dulu (Uang › Tutup buku › Kunci bulan)' };
  const lapor = Object.assign({}, A.lapor); const sudah = !!lapor[key];
  if (sudah) { if (!yakin) return { tolak: 'Ketuk sekali lagi untuk membatalkan tanda ' + lpNamaBulan(key), perluYakin: true }; delete lapor[key]; }
  else lapor[key] = { tgl: w.tanggal, jam: w.jam };
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap({ lapor }, w) }], patch: { yakinBatal: false, kabar: sudah ? 'Tanda dilaporkan ' + lpNamaBulan(key) + ' dibatalkan' : lpNamaBulan(key) + ' ditandai sudah dilaporkan ' + tanggalPendek(w.tanggal), kabarAwas: false } };
}
/** Bukti omzet dari bulan yang dipilih: Σ baris = jumlah (penjaga identitas tergambar); hanya bulan final. */
export function buktiOmzet(pilih, kini) {
  const R = rekapOmzet(kini); const terpilih = R.daftar.filter((b) => pilih && pilih[b.key]); const total = terpilih.reduce((a, b) => a + b.omzet, 0);
  // Paket B (H2): bulan final yang angkanya TIDAK ada di sistem (sebelum catatan pertama, atau tahun yang ditutup tanpa potret) ditolak — dulu tercetak Rp0 "final"
  const tanpaAngka = terpilih.filter((b) => b.absen || b.tanpaPotret);
  const tolak = !terpilih.length ? 'Pilih bulannya dulu' : terpilih.some((b) => !b.final) ? 'Ada bulan yang belum tutup buku (DRAF) — bukti untuk pajak/bank hanya dari bulan final'
    : tanpaAngka.length ? tanpaAngka.map((b) => b.nama).join(', ') + ' tidak punya angka omzet di sistem (' + (tanpaAngka.some((b) => b.tanpaPotret) ? 'tahunnya ditutup tanpa potret — angkanya hanya di berkas arsip' : 'sebelum catatan pertama') + ') — bukti tidak dicetak Rp0' : '';
  return { baris: terpilih.map((b) => ({ nama: b.nama, tanda: b.final ? 'final' : 'DRAF', n: b.omzet })), total, n: terpilih.length, tolak, judul: terpilih.length ? terpilih.length + ' bulan · ' + RP(total) : 'Pilih bulannya', cocok: terpilih.reduce((a, b) => a + b.omzet, 0) === total };
}

// ==================== NERACA · dua sisi ====================
export function aturLaporan() { const a = ugAturDok('laporan') || {}; return { asetTetap: isFinite(Number(a.asetTetap)) && Number(a.asetTetap) >= 0 ? Math.round(Number(a.asetTetap)) : 0, asetKet: String(a.asetKet || ''), dariOwner: !!ugAturDok('laporan') }; }
export function susunAturLaporan(isi, w) { const n = ugKosong(isi.asetTetap) ? 0 : ugAngka(isi.asetTetap); if (n < 0) return { tolak: 'Aset tetap tidak boleh minus' }; return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'laporan', tanggal: w.tanggal, jam: w.jam, asetTetap: Math.round(n), asetKet: String(isi.asetKet || '').trim().slice(0, 120) } }], patch: { aturN: null, kabar: 'Aset tetap ' + RP(n) + ' dicatat sebagai isian owner — ikut di neraca sampai modul aset tetap ada', kabarAwas: false } }; }
/**
 * Neraca per tanggal `sampai` (bawaan: sekarang) — hitungNeraca mesin lama (kas · stok · piutang · kasbon · utang pemasok · utang ke owner) + modal owner tertanam
 * (Owner & toko) + aset tetap (isian owner). Laba ditahan = sisa aset sesudah kewajiban & modal (DIHITUNG, disebut begitu); pembandingnya laba bersih kumulatif mesin
 * sejak catatan pertama − ambil pribadi; selisihnya DITULIS sebagai "belum terjelaskan buku" (titik kas, stok awal sebelum sistem), tidak disembunyikan.
 * kasBulan (39b no. 36, dari lpKasAkhirBulan) = kas akhir bulan FINAL dari hitungan fisik tutup hari; tanpa itu kas = kasPada mesin (bentuk & angka tetap).
 */
export function neracaPada(sampai, kini, kasBulan) {
  const iso = hariIniIso(kini); const s = sampai || null; if (s && lpTutup(s)) return lpNeracaArsip(s);   // Paket B: tanggal di tahun yang sudah ditutup buku
  const N0 = ingatNeraca(s); const KB = kasBulan || null;
  const N = KB ? Object.assign({}, N0, { kas: KB.kas, total: KB.kas === null ? null : Math.round(KB.kas + N0.stok + N0.piutang + N0.kasbon - N0.utangOwner - N0.utangPemasok) }) : N0; const modal = modalTertanam(s); const AT = aturLaporan(); const pertama = lpPertama();
  const kasAda = N.kas !== null; const aset = kasAda ? N.kas + N.stok + N.piutang + N.kasbon + AT.asetTetap : null; const kewajiban = N.utangPemasok + N.utangOwner; const labaDitahan = aset === null ? null : aset - kewajiban - modal;
  let labaKum = null, prive = 0; if (pertama) { const X = lpLabaKum(pertama, s, iso); labaKum = X.laba; prive = X.prive; }
  const menurutMesin = labaKum === null ? null : labaKum - prive; const selisihBuku = labaDitahan === null || menurutMesin === null ? null : labaDitahan - menurutMesin;
  const harta = [['Kas (laci · brankas · rekening · amplop)', N.kas, kasAda ? '' : KB ? KB.kenapa : 'titik kas belum disetel'], ['Stok beras — karung', N.nilaiSack], ['Stok kemasan jadi', N.nilaiBags], ['Kantong & bahan', N.nilaiBahan], ['Piutang pelanggan (' + N.nPiutang + ' nama)', N.piutang], ['Kasbon pegawai & owner (' + N.nKasbon + ' nama)', N.kasbon]].concat(AT.asetTetap ? [['Aset tetap (isian owner' + (AT.asetKet ? ': ' + AT.asetKet : '') + ')', AT.asetTetap]] : []).map((r) => ({ nama: r[0], n: r[1], ket: r[2] || '' }));
  const pasiva = [['Utang ke pemasok (' + N.nBonPemasok + ' bon)', N.utangPemasok], ['Utang toko ke owner', N.utangOwner], ['Modal owner tertanam', modal], ['Laba ditahan (dihitung: aset − kewajiban − modal)', labaDitahan]].map((r) => ({ nama: r[0], n: r[1], ket: '' }));
  const kataLebih = lebihNeraca(s, kasAda).kata;   // no. 4 (lihat lebihNeraca): ikut catatan → semua kertas; bentuk objek ini TETAP (ASAP GLOBAL membandingkannya byte-sama)
  const tolak = !kasAda ? 'Kas belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya' : N.adaStokMinus ? 'Buku menyebut stok MINUS (' + N.sackMinus.concat(N.bagsMinus).slice(0, 3).join(', ') + ') — cocokkan dulu di Stok, neraca tidak dicetak' : '';
  const catatanInti = aset === null ? (KB ? 'Tanpa hitungan tutup hari akhir bulan, sisi harta tidak utuh.' : 'Tanpa titik kas, sisi harta tidak utuh.') : (KB ? 'Kas ' + RP(N.kas) + ' = ' + KB.sumber + '. ' : '') + 'Aset ' + RP(aset) + ' = kewajiban ' + RP(kewajiban) + ' + modal ' + RP(modal) + ' + laba ditahan ' + RP(labaDitahan) + '. ' + (menurutMesin === null ? '' : 'Laba bersih kumulatif mesin − ambil pribadi = ' + RP(menurutMesin) + (Math.abs(selisihBuku) > 0.5 ? '; beda ' + RP(selisihBuku) + ' belum terjelaskan buku (titik kas yang pernah disetel ulang, stok awal sebelum sistem).' : '; cocok dengan laba ditahan.'));
  return { sampai: s || iso, N, modal, asetTetap: AT.asetTetap, aset, kewajiban, labaDitahan, labaKum, prive, menurutMesin, selisihBuku, harta, pasiva, total: N.total, tolak: KB && !kasAda ? KB.tolak : tolak, seimbang: aset !== null && Math.round(aset) === Math.round(kewajiban + modal + (labaDitahan || 0)),
    catatan: catatanInti + (kataLebih ? ' ' + kataLebih : '') };
}
/**
 * Keputusan owner 8 Okt 2026 (K9): modal awal saat sistem mulai mencatat (8 Agu 2026) DIBIARKAN tidak dicatat. SATU kalimat tetap — sama persis di Neraca
 * berkop (catatanNeracaBerkop) dan berita acara tutup buku (tutup-buku-logika.js teksAcara) — menyebut asal beda "belum terjelaskan buku"; angka pastinya
 * urusan konsultan. Objek neracaPada TIDAK diubah (layar Neraca & ASAP GLOBAL membandingkannya byte-sama dengan main).
 */
export const LP_KALIMAT_MODAL_AWAL = 'Modal awal toko saat sistem mulai mencatat 8 Agu 2026 tidak pernah dicatat: posisi toko sebelum tanggal itu — bersama titik kas yang pernah disetel ulang dan catatan yang tidak lengkap, bila ada — ikut terbaca sebagai beda "belum terjelaskan buku". Angka pastinya diserahkan ke konsultan.';
/** Catatan kertas Neraca berkop: catatan neraca + kalimat K9 bila catatannya menulis beda "belum terjelaskan buku" (cocok = tanpa kalimat itu). */
export function catatanNeracaBerkop(NP) {
  const beda = NP && NP.selisihBuku !== null && NP.selisihBuku !== undefined && Math.abs(Number(NP.selisihBuku)) > 0.5;
  return String((NP && NP.catatan) || '') + (beda ? ' ' + LP_KALIMAT_MODAL_AWAL : '');
}
/** Paket B (sintesis d): laba bersih kumulatif mesin & ambil pribadi dari catatan pertama s.d. `s` (null = semua; laba s.d. hari ini) — pembanding laba ditahan.
 *  Sesudah tutup buku, bagian s.d. 31 Des tahun yang ditutup = angka neraca 31 Des di potretnya (dihitung fungsi ini juga, saat kunci) + catatan hidup sesudahnya.
 *  Tanpa ini bagian itu hilang bersama arsip dan neraca Januari menulis seluruh laba ditahan tahun lalu sebagai "belum terjelaskan buku". */
function lpLabaKum(pertama, s, iso) {
  const era = eraBuku(); const PtN = era !== null && (s || iso) > era + '-12-31' ? ((potretBulan(era + '-12') || {}).neraca || null) : null;
  if (PtN && PtN.labaKum !== null && PtN.labaKum !== undefined) { const c1 = (era + 1) + '-01-01'; let prive = Number(PtN.prive) || 0; ambilPengeluaranHarian().forEach((h) => { if (h.kategori === 'owner' && h.tanggal && h.tanggal >= c1 && (!s || h.tanggal <= s)) prive += Number(h.nominal) || 0; }); return { laba: PtN.labaKum + ugLabaBersih(c1, s || iso).labaBersih, prive }; }
  let prive = 0; ambilPengeluaranHarian().forEach((h) => { if (h.kategori === 'owner' && h.tanggal && (!s || h.tanggal <= s)) prive += Number(h.nominal) || 0; }); return { laba: ugLabaBersih(pertama, s || iso).labaBersih, prive };
}
/** Paket B: neraca per tanggal di tahun yang sudah ditutup buku. Akhir bulan = neraca dari potret (dihitung saat kunci, kas akhir bulan dari hitungan tutup hari —
 *  sama dengan Dokumen → Neraca bulan final waktu itu); tanggal lain tidak bisa dihitung (catatannya diarsip, mesin tidak menghitung mundur) → ditolak dengan sebabnya. */
function lpNeracaArsip(s) {
  const key = String(s).slice(0, 7); const Pt = potretBulan(key); const th = key.slice(0, 4);
  if (Pt && Pt.neraca && s === akhirBulanIso(key)) return Object.assign({}, Pt.neraca, { diarsip: true });
  const kenapa = Pt ? 'catatan ' + th + ' sudah diarsip (tutup buku ' + th + '); yang tersimpan neraca akhir tiap bulan' : 'catatan ' + th + ' sudah diarsip (tutup buku ' + th + ') tanpa potret — angkanya hanya di berkas arsip & cadangan sebelum tutup buku';
  const tolak = 'Neraca per ' + tanggalPendek(s) + ' tidak bisa disusun — ' + kenapa + (Pt ? '. Pilih ' + tanggalPendek(akhirBulanIso(key)) : '');
  const N = { kas: null, nilaiSack: null, nilaiBags: null, nilaiBahan: null, stok: null, piutang: null, nPiutang: 0, kasbon: null, nKasbon: 0, utangOwner: null, utangPemasok: null, nBonPemasok: 0, sackMinus: [], bagsMinus: [], adaStokMinus: false, kewajiban: null, total: null };
  const harta = ['Kas (laci · brankas · rekening · amplop)', 'Stok beras — karung', 'Stok kemasan jadi', 'Kantong & bahan', 'Piutang pelanggan', 'Kasbon pegawai & owner'].map((nama) => ({ nama, n: null, ket: '' }));
  const pasiva = ['Utang ke pemasok', 'Utang toko ke owner', 'Modal owner tertanam', 'Laba ditahan (dihitung: aset − kewajiban − modal)'].map((nama) => ({ nama, n: null, ket: '' }));
  return { sampai: s, N, modal: null, asetTetap: aturLaporan().asetTetap, aset: null, kewajiban: null, labaDitahan: null, labaKum: null, prive: 0, menurutMesin: null, selisihBuku: null, harta, pasiva, total: null, tolak, seimbang: false, catatan: tolak + '.', diarsip: true, tanpaPotret: !Pt };
}
/** 39b no. 4: kelebihan bayar pelanggan (sisa negatif) tidak masuk piutang mesin (sisa > 0) dan belum punya baris kewajiban → kekayaan neraca lebih
 * besar sebesarnya. Angka mesin TIDAK diubah; kalimatnya ikut catatan neraca (semua kertas) dan pita layar. BUKAN tolak: menahan cetak = keputusan owner. */
export function lebihNeraca(sampai, asetAda) {
  const lebihBayar = lebihBayarDari(hitungPiutang(sampai || null)); const U = lebihBayar.uang, H = lebihBayar.hapus;
  // B1: hanya bagian UANG (bayar melebihi semua bon) yang membuat kekayaan terlalu besar; hapus buku yang ternyata dibayar = rugi hapus buku yang salah.
  // B4: tanpa titik kas neraca tidak punya angka kekayaan — kalimatnya menyebut akibatnya nanti, bukan "di atas".
  const kataU = U.n ? 'Kelebihan bayar pelanggan ' + RP(U.jumlah) + ' (' + U.n + ' nama) belum dihitung sebagai kewajiban — ' + (asetAda === false ? 'begitu kas bisa dihitung, kekayaan akan terbaca lebih besar sebesar itu.' : 'kekayaan di atas lebih besar sebesar itu.') : '';
  const kataH = H.n ? RP(H.jumlah) + ' (' + H.n + ' nama) dibayar padahal sudah dihapus dari buku — kerugian hapus bukunya sebenarnya sudah dibayar; hapus bukunya perlu dibalik, bukan uang pelanggan.' : '';
  return { lebihBayar, kata: [kataU, kataH].filter(Boolean).join(' ') };
}
/**
 * 39b no. 36 (owner 30 Sep 2026): kas akhir bulan FINAL (neraca & arus kas berkop, paket bank) = hitungan fisik tutup hari TERAKHIR di bulan itu — kolom `titik`
 * dokumen tutupHari (isi tempat uang sesudah tutup malam itu; pola titikTahun tutup buku); catatan uang sesudahnya sampai akhir bulan ikut (saldoKantong). Bukan
 * kasPada: titik kas sekarang selalu lebih muda dari bulan final dan mesin tidak menghitung mundur. Bulan tanpa hitungan itu → kas null + kalimat tolak yang benar.
 */
export function lpKasAkhirBulan(key) {
  // Paket B: bulan di tahun yang sudah ditutup buku — tutup harinya ikut arsip; kas akhir bulan itu dihitung fungsi ini juga saat kunci dan disimpan di potret
  if (lpTutup(key)) { const Pt = potretBulan(key); if (Pt && Pt.kas) return Object.assign({}, Pt.kas); const kenapa = 'catatan ' + String(key).slice(0, 4) + ' sudah diarsip (tutup buku) tanpa potret'; return { kas: null, kenapa, sumber: '', tolak: 'Kas akhir ' + lpNamaBulan(key) + ' belum bisa dihitung — ' + kenapa }; }
  const awal = key + '-01', akhir = akhirBulanIso(key); const nama = lpNamaBulan(key); const th = ambilTutupHari().filter((d) => d && d.tanggal && d.tanggal >= awal && d.tanggal <= akhir);
  const d = th.filter((x) => x.titik).sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)))[0];
  if (!d) { const kenapa = th.length ? 'tutup hari ' + nama + ' belum menyimpan isi tempat uang sesudah tutup (tutup hari lama)' : 'tidak ada tutup hari di ' + nama; return { kas: null, kenapa, sumber: '', tolak: 'Kas akhir ' + nama + ' belum bisa dihitung — ' + kenapa + '. Bulan final memakai hitungan fisik tutup hari akhir bulan, bukan titik kas sekarang' }; }
  const t = { tanggal: d.tanggal, laci: Number(d.titik.laci) || 0, rekening: Number(d.titik.rekening) || 0, amplop: Number(d.titik.amplop) || 0, brankas: Number(d.titik.brankas) || 0 };
  return { kas: saldoKantong(akhir, t).total, kenapa: '', sumber: 'hitungan fisik tutup hari ' + tanggalPendek(t.tanggal) + (t.tanggal < akhir ? ' + catatan uang sesudahnya sampai ' + tanggalPendek(akhir) : ''), tolak: '' };
}
/**
 * Tinjauan 39b UU36-2: neraca LAYAR untuk tanggal yang dipilih (Laporan → Neraca, layar & kertasnya). Bulan FINAL: akhir bulan = kas dari hitungan fisik tutup
 * hari akhir bulan (sama dengan Dokumen → Neraca); tanggal lain yang kasnya tidak terhitung mesin (titik kas sekarang lebih muda) ditolak dengan sebab yang
 * benar, bukan "titik kas belum disetel". Hari ini / bulan draf = neracaPada apa adanya.
 */
export function neracaTanggal(sampai, kini, final) {
  if (!sampai || !final || lpTutup(sampai)) return neracaPada(sampai, kini);   // Paket B: tahun yang ditutup → neracaPada membaca potret / menolak dengan sebabnya
  const key = String(sampai).slice(0, 7); if (sampai === akhirBulanIso(key)) return neracaPada(sampai, kini, lpKasAkhirBulan(key));
  const NP = neracaPada(sampai, kini); if (NP.N.kas !== null) return NP;
  const nama = lpNamaBulan(key); const kenapa = 'bulan ' + nama + ' sudah final dan titik kas sekarang lebih muda';
  return neracaPada(sampai, kini, { kas: null, kenapa, sumber: '', tolak: 'Kas per ' + tanggalPendek(sampai) + ' belum bisa dihitung — ' + kenapa + '. Neraca akhir ' + nama + ' (hitungan fisik tutup hari akhir bulan) ada di Dokumen → Laporan berkop' });
}
/** Catatan neraca untuk LAYAR: tanpa kalimat kelebihan bayar (layar memajangnya sebagai pita tersendiri, tetap tampil walau neraca ditolak). */
export const catatanLayarNeraca = (NP, NL) => (NL && NL.kata && NP.catatan.endsWith(' ' + NL.kata) ? NP.catatan.slice(0, NP.catatan.length - NL.kata.length - 1) : NP.catatan);
/** Banding kekayaan sekarang vs saat titik kas disetel (kalimat tampilkanNeraca sistem lama). */
export function bandingKekayaan(kini) { const t = ambilTitikKas(); const kiniN = ingatNeraca(); if (!t || kiniN.total === null) return { ada: false, titik: t, teks: 'Stok dinilai dengan HPP (harga modal), bukan harga jual — sengaja konservatif.' }; const awal = ingatNeraca(t.tanggal); if (awal.total === null) return { ada: false, titik: t, teks: '' }; const d = kiniN.total - awal.total; return { ada: true, titik: t, awal: awal.total, kini: kiniN.total, selisih: d, teks: 'Saat titik kas ' + tanggalPendek(t.tanggal) + ' kekayaan ' + RP(awal.total) + ' — ' + (d === 0 ? 'belum bergeser.' : 'sejak itu ' + (d > 0 ? 'naik ' : 'turun ') + RP(Math.abs(d)) + '.') + ' Belanja stok tidak menggerakkan angka ini — uangnya cuma berubah wujud; yang menggerakkannya untung dan biaya.' }; }

// ==================== DK1 · KOP & IDENTITAS ====================
/** Identitas usaha: aturanToko/identitas menang; belum ada → nama & alamat & telepon dari setelan struk (Jual) kalau ada; versi 0 = kop bawaan (belum pernah disimpan). */
export function identitasUsaha() {
  const a = ugAturDok('identitas'); const st = stAtur().kop; const I = Object.assign({}, IDENTITAS_BAWAAN);
  if (a) { KOLOM_IDENTITAS.forEach((k) => { if (a[k.id] !== undefined && a[k.id] !== null) I[k.id] = String(a[k.id]); }); if (a.gaya === 'tengah' || a.gaya === 'kiri') I.gaya = a.gaya; I.npwpDiKop = a.npwpDiKop === true; }
  else { if (st.nama) I.nama = st.nama; if (st.alamat) I.alamat = st.alamat; if (st.telp) I.telepon = st.telp; }
  return Object.assign(I, { versi: a ? Number(a.versi) || 1 : 0, riwayat: a && Array.isArray(a.riwayat) ? a.riwayat : [], dariOwner: !!a, dariStruk: !a && !!(st.alamat || st.telp), lengkap: !!(I.nama.trim() && I.alamat.trim()) });
}
export function periksaIdentitas(d) { if (!String(d.nama || '').trim()) return 'Nama usaha wajib diisi'; if (!String(d.alamat || '').trim()) return 'Alamat wajib diisi — dokumen untuk bank/pajak butuh alamat'; if (d.npwp && [15, 16].indexOf(lpDigit(d.npwp).length) < 0) return 'NPWP harus 15 atau 16 angka (' + lpDigit(d.npwp).length + ' angka) — atau kosongkan kalau belum ada'; if (d.nib && lpDigit(d.nib).length !== 13) return 'NIB harus 13 angka (' + lpDigit(d.nib).length + ') — atau kosongkan'; if (d.telepon && lpDigit(d.telepon).length < 8) return 'Nomor telepon terlalu pendek'; return ''; }
/** Simpan identitas = versi kop baru, berjejak; kop ringkas (nama · alamat · telepon) ikut ke setelan struk supaya nota memakai kop yang sama. */
export function susunIdentitas(draf, w) {
  const I = identitasUsaha(); const d = {}; KOLOM_IDENTITAS.forEach((k) => { d[k.id] = String(draf[k.id] === undefined ? I[k.id] : draf[k.id] || '').trim().slice(0, 120); }); d.gaya = draf.gaya === undefined ? I.gaya : draf.gaya === 'tengah' ? 'tengah' : 'kiri';
  d.npwpDiKop = draf.npwpDiKop === undefined ? !!I.npwpDiKop : draf.npwpDiKop === true;
  const tolak = periksaIdentitas(d); if (tolak) return { tolak }; const ubah = KOLOM_IDENTITAS.filter((k) => d[k.id] !== (I[k.id] || '')).map((k) => k.nama); if (d.gaya !== I.gaya) ubah.push('gaya kop'); if (d.npwpDiKop !== !!I.npwpDiKop) ubah.push(d.npwpDiKop ? 'NPWP dicetak di kop penuh' : 'NPWP tidak dicetak'); if (!ubah.length) return { tolak: 'Tidak ada yang berubah' };
  const versi = I.versi + 1; const riwayat = [{ versi, tanggal: w.tanggal, jam: w.jam, ubah }].concat(I.riwayat).slice(0, 30); const S = stAtur();
  return { dokumen: [{ koleksi: 'aturanToko', data: Object.assign({ id: 'identitas', tanggal: w.tanggal, jam: w.jam, versi, riwayat }, d) }, { koleksi: 'aturanToko', data: { id: 'struk', tanggal: w.tanggal, jam: w.jam, kop: { nama: d.nama.slice(0, 40), alamat: d.alamat.slice(0, 80), telp: d.telepon.slice(0, 30) }, kaki: S.kaki, kertas: S.kertas, sertakan: S.sertakan, oto: S.oto, perOrang: S.perOrang } }],
    versi, patch: { drafI: null, isiI: null, kabar: 'Tersimpan sebagai kop v' + versi + ' (' + ubah.join(', ') + ') — dokumen yang sudah dicetak tetap menyebut versi lamanya; kop nota di Jual ikut' + (d.npwpDiKop && peringatanNpwp(d.npwp) ? '. ' + PERINGATAN_NPWP_NIK : ''), kabarAwas: !!(d.npwpDiKop && peringatanNpwp(d.npwp)) } };
}
/** Kop untuk satu ragam: penuh (NIB kalau ada; NPWP HANYA kalau owner menyalakan npwpDiKop) atau ringkas (tanpa keduanya). */
export function kopUntuk(ragam, I) { const i = I || identitasUsaha(); return { nama: i.nama || '(nama usaha)', alamat: (i.alamat || '') + (i.telepon ? (i.alamat ? ' · ' : '') + i.telepon : ''), resmi: ragam === 'penuh' ? [i.npwp && i.npwpDiKop === true ? 'NPWP ' + i.npwp : '', i.nib ? 'NIB ' + i.nib : ''].filter(Boolean).join(' · ') : '', slogan: i.slogan || '', gaya: i.gaya, versi: i.versi, lengkap: i.lengkap, ragam }; }
export function pakaiKop() { const a = ugAturDok('dokumen') || {}; const pakai = {}; DOKUMEN_KOP.forEach((d) => { pakai[d.id] = a.pakai && (a.pakai[d.id] === 'penuh' || a.pakai[d.id] === 'ringkas') ? a.pakai[d.id] : d.awal; }); return { pakai, nomorAwal: isFinite(Number(a.nomorAwal)) && Number(a.nomorAwal) >= 1 ? Math.round(Number(a.nomorAwal)) : 1, dariOwner: !!ugAturDok('dokumen') }; }
export function susunAturDokumen(isi, w) {
  const P = pakaiKop(); const pakai = Object.assign({}, P.pakai); if (isi.pakai) Object.keys(isi.pakai).forEach((k) => { if (pakai[k] !== undefined && (isi.pakai[k] === 'penuh' || isi.pakai[k] === 'ringkas')) pakai[k] = isi.pakai[k]; });
  const n = ugKosong(isi.nomorAwal) ? P.nomorAwal : ugAngka(isi.nomorAwal); if (!(n >= 1 && n <= 999999)) return { tolak: 'Nomor dokumen mulai 1–999.999' }; const terpakai = nomorTerakhir(); if (n <= terpakai) return { tolak: 'Nomor ' + ANGKA(n) + ' sudah terpakai — cetakan terakhir No. ' + ANGKA(terpakai) };
  return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'dokumen', tanggal: w.tanggal, jam: w.jam, pakai, nomorAwal: Math.round(n) } }], patch: { aturD: null, kabar: 'Setelan dokumen tersimpan — nomor berikutnya No. ' + ANGKA(Math.max(n, terpakai + 1)), kabarAwas: false } };
}

// ==================== CETAKAN BERNOMOR ====================
export function nomorTerakhir() { return ambilDokumenCetak().reduce((a, d) => Math.max(a, Number(d.nomor) || 0), 0); }
export function nomorBerikut() { return Math.max(nomorTerakhir() + 1, pakaiKop().nomorAwal); }
export function salinanKe(trxId) { return ambilDokumenCetak().filter((d) => d.jenis === 'nota' && String(d.trxId) === String(trxId)).length + 1; }
/** Satu cetakan = satu dokumen `dokumenCetak` bernomor urut; cara = 'cetak' | 'pdf' | 'wa'. info = { jenis, judul, periode, draf, trxId, salinanKe, ragam }. */
export function susunCetakan(info, cara, w) {
  if (['cetak', 'pdf', 'wa'].indexOf(cara) < 0) return { tolak: 'Cara keluar tidak dikenal' }; const nomor = nomorBerikut(); const I = identitasUsaha();
  return { nomor, dokumen: [{ koleksi: 'dokumenCetak', data: { id: 'dc-' + w.idUnik(), nomor, jenis: info.jenis, judul: info.judul, periode: info.periode || '', cara, kopVersi: I.versi, draf: !!info.draf, tanggal: w.tanggal, jam: w.jam, trxId: info.trxId || null, salinanKe: info.salinanKe || null } }],
    patch: { kabar: info.judul + (info.periode ? ' ' + info.periode : '') + (info.draf ? ' bercap DRAF' : '') + (cara === 'cetak' ? ' dikirim ke dialog cetak' : cara === 'pdf' ? ' dibuka di dialog cetak — pilih "Simpan sebagai PDF"' : ' dibuka di WhatsApp') + ' — No. ' + ANGKA(nomor), kabarAwas: false } };
}
/** Paket bank (owner 7 Okt, Safari): SEMUA nomor dihitung dulu — urut dari nomorBerikut(), satu per dokumen, bentuk catatan = susunCetakan(…, 'pdf') —
 *  supaya dialog cetak dibuka di ketukan yang sama dan catatannya satu kiriman. daftar = [{ jenis, judul, periode, draf }]. */
export function susunPaketCetakan(daftar, w) {
  if (!daftar || !daftar.length) return { tolak: 'Paket kosong — pilih isinya' }; const awal = nomorBerikut(); const dokumen = [];
  for (let i = 0; i < daftar.length; i++) { const r = susunCetakan(daftar[i], 'pdf', w); if (r.tolak) return r; r.dokumen[0].data.nomor = awal + i; dokumen.push(r.dokumen[0]); }
  return { nomor: awal, nomorAkhir: awal + daftar.length - 1, dokumen };
}
export function riwayatCetakan(n) { return ambilDokumenCetak().slice().sort((a, b) => (Number(b.nomor) || 0) - (Number(a.nomor) || 0)).slice(0, n || 12).map((d) => ({ id: String(d.id), nomor: Number(d.nomor) || 0, teks: (d.cara === 'wa' ? 'WA' : d.cara === 'pdf' ? 'PDF' : 'CETAK') + ' · ' + d.judul + (d.periode ? ' ' + d.periode : '') + (d.draf ? ' (DRAF)' : '') + (d.salinanKe ? ' · salinan ke-' + d.salinanKe : '') + ' · kop v' + (d.kopVersi || 0), tanggal: d.tanggal || '', jam: d.jam || '' })); }

// ==================== DK2 · LAPORAN BERKOP ====================
const lpBarisAK = (K, arah) => K[arah].filter((x) => x.nominal > 0).map((x) => ({ nama: x.label + (x.n ? ' (' + x.n + ' ' + x.satuan + ')' : ''), n: arah === 'masuk' ? x.nominal : -x.nominal, kelas: '' }));
/** Satu laporan berkop untuk rentang bulan berakhir di `keKey`. */
export function laporanBerkop(jenis, keKey, rentang, kini, bayaran) {
  const iso = hariIniIso(kini); const B = bayaran || bayaranBiayaBulanan(); const n = RENTANG_LAPORAN.some((r) => r[0] === rentang) ? rentang : 1; const bulan = []; for (let i = n - 1; i >= 0; i--) bulan.push(lpGeserBulan(keKey, -i));
  const dari = bulan[0] + '-01', sampai = akhirBulanIso(keKey); const final = bulan.every(lpFinal); const periode = bulan.length === 1 ? lpNamaBulan(keKey) : lpBulanPendek(bulan[0], true) + ' – ' + lpBulanPendek(keKey, true); const J = JENIS_LAPORAN.find((j) => j[0] === jenis) || JENIS_LAPORAN[0];
  const I = identitasUsaha(); let baris = [], catatan = '', tolak = '', judul = 'Laporan ' + J[1], sub = periode;
  // Paket B: bulan di tahun yang sudah ditutup buku = potret (lpLabaRentang / lpArusRentang / neraca & kas akhir bulan dari potret); ditutup TANPA potret = ditolak
  const tanpaPotret = lpBulanTanpaPotret(J[0] === 'neraca' ? keKey + '-01' : dari, sampai);
  if (J[0] === 'labarugi') {
    // 39b no. 40: bulan sebelum awal buku tetap di periode & di kertas (satu baris keterangan tanpa angka); laba dijumlah sejak bulan awal buku
    const ab = lpAwalBuku(); const pra = bulan.filter((k) => k < ab); const dariL = pra.length ? ab + '-01' : dari;
    const L = lpLabaRentang(dariL, sampai, B); const mdr = lpMdrLintas(dariL, sampai);
    baris = [{ nama: 'Pendapatan', kelas: 'kel' }, { nama: 'Penjualan terhitung (nota ber-HPP)', n: L.omzetHitung + L.returUang }].concat(L.returJumlah ? [{ nama: 'Retur & refund (' + L.returJumlah + ')', n: -L.returUang }] : []).concat([{ nama: 'Harga pokok barang terjual (HPP)', n: -(L.hpp + L.returHpp) }]).concat(L.returHpp > 0 ? [{ nama: 'HPP barang yang kembali ke stok', n: L.returHpp }] : [])
      .concat([{ nama: 'Laba kotor', n: L.margin, kelas: 'jumlah' }, { nama: 'Biaya', kelas: 'kel' }, { nama: 'Belanja & biaya toko harian', n: -(L.harianToko - mdr) }, { nama: 'Biaya bulanan — dibagi rata per hari (' + L.nHari + ' hari)', n: -L.jatahBulanan }]).concat(mdr ? [{ nama: 'Potongan QRIS (MDR)', n: -mdr }] : []).concat(L.hapusBuku ? [{ nama: 'Hapus buku piutang', n: -L.hapusBuku }] : []).concat([{ nama: 'Susut & selisih stok', n: L.susutStok }]).concat(L.lebihKurangKas ? [{ nama: lpNamaLebihKurang(L), n: L.lebihKurangKas }] : []).concat([{ nama: 'Laba bersih', n: L.labaBersih, kelas: 'jumlah' }]);
    catatan = 'Laba bersih ' + RP(L.labaBersih) + ' = laba kotor − biaya (upah kotor, termasuk potongan QRIS ' + RP(mdr) + ') − hapus buku ± susut' + (L.lebihKurangKas ? ' ± lebih/kurang kas (selisih laci tutup hari)' : '') + '.' + (L.jumlahTanpaHpp ? ' ' + L.jumlahTanpaHpp + ' baris tanpa modal (' + RP(L.omzetTanpaHpp) + ') tidak ikut.' : '');
    if (pra.length) { const lbl = lpBulanPendek(pra[0], true) + (pra.length > 1 ? ' – ' + lpBulanPendek(pra[pra.length - 1], true) : ''); baris.unshift({ nama: lbl + ' · sebelum awal buku — tidak dijumlah', n: null }); catatan += ' ' + lpKetSebelumBuku(lbl, lpLabaRentang(dari, akhirBulanIso(pra[pra.length - 1]), B).labaBersih); }
  } else if (J[0] === 'neraca') {
    const NP = neracaPada(sampai > iso ? iso : sampai, kini, final ? lpKasAkhirBulan(keKey) : null); sub = 'per ' + tanggalPendek(NP.sampai) + (bulan.length > 1 ? ' (akhir ' + periode + ')' : '');
    baris = [{ nama: 'Harta', kelas: 'kel' }].concat(NP.harta.map((r) => ({ nama: r.nama, n: r.n }))).concat([{ nama: 'Jumlah harta', n: NP.aset, kelas: 'jumlah' }, { nama: 'Kewajiban & modal', kelas: 'kel' }]).concat(NP.pasiva.map((r) => ({ nama: r.nama, n: r.n }))).concat([{ nama: 'Jumlah kewajiban & modal', n: NP.aset === null ? null : NP.kewajiban + NP.modal + NP.labaDitahan, kelas: 'jumlah' }]);
    catatan = catatanNeracaBerkop(NP); tolak = NP.tolak;
  } else {
    // 39b no. 36: bulan FINAL — kas awal & akhir dari hitungan fisik tutup hari akhir bulan (lpKasAkhirBulan), sama dengan kas neraca bulan itu
    const KA = final ? lpKasAkhirBulan(keKey) : null, KW = final ? lpKasAkhirBulan(lpGeserBulan(bulan[0], -1)) : null;
    const K = lpArusRentang(dari, sampai, B); const sebelumIso = ugTambahHari(dari, -1); const kasAwal = KW ? KW.kas : lpKasPadaLintas(sebelumIso); const kasAkhir = KA ? KA.kas : ingatKasPada(sampai > iso ? null : sampai); const selisih = kasAwal === null || kasAkhir === null ? null : kasAkhir - (kasAwal + K.bersih);
    // tinjauan 39b UU36-1: bagian penyesuaian yang = selisih laci tutup hari di dalam periode bernama seperti di laba-rugi (Lebih/kurang kas, no. 38), bukan
    // "bukan uang yang bergerak"; sisanya (titik kas disetel ulang, mis. catat isi rekening) tetap penyesuaian titik kas. Angka kas tidak berubah.
    const LKK = lpLebihKurangLintas(dari, sampai); const lk = selisih === null ? 0 : LKK.n; const sesuai = selisih === null ? null : selisih - lk;
    baris = [{ nama: 'Kas awal periode' + (kasAwal === null ? (KW ? ' — ' + KW.kenapa + ', belum bisa dihitung' : lpTutup(sebelumIso) ? ' — catatan ' + sebelumIso.slice(0, 4) + ' sudah diarsip dan kasnya tidak tersimpan di potret, belum bisa dihitung' : ' — sebelum titik kas, belum bisa dihitung') : ''), n: kasAwal }, { nama: 'Masuk', kelas: 'kel' }].concat(lpBarisAK(K, 'masuk')).concat([{ nama: 'Keluar', kelas: 'kel' }]).concat(lpBarisAK(K, 'keluar')).concat([{ nama: 'Kas bersih periode', n: K.bersih, kelas: 'jumlah' }]).concat(lk ? [{ nama: lpNamaLebihKurang({ nLebihKurang: LKK.malam }), n: lk }] : []).concat(sesuai !== null && Math.abs(sesuai) > 0.5 ? [{ nama: 'Penyesuaian titik kas (disetel ulang dalam periode)', n: sesuai }] : []).concat([{ nama: 'Kas akhir periode', n: kasAkhir, kelas: 'jumlah' }]);
    catatan = kasAkhir === null ? (KA ? KA.tolak + '.' : 'Kas akhir belum bisa dihitung — titik kas belum disetel.') : 'Kas akhir ' + RP(kasAkhir) + ' = kas di neraca (' + (KA ? KA.sumber : 'satu mesin') + ').' + (lk ? ' Lebih/kurang kas ' + RP(lk) + ' = selisih hitungan uang tutup hari di dalam periode, dibukukan di laba-rugi sebagai Lebih/kurang kas.' : '') + (sesuai !== null && Math.abs(sesuai) > 0.5 ? ' Penyesuaian ' + RP(sesuai) + ' = titik kas yang disetel ulang di dalam periode, bukan uang yang bergerak.' : '');
    if (kasAkhir === null) tolak = KA ? KA.tolak : 'Kas belum bisa dihitung — titik kas belum disetel';
  }
  if (tanpaPotret.length) tolak = lpKalimatTanpaPotret(tanpaPotret);
  if (!tolak && !I.lengkap) tolak = 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)';
  return { jenis: J[0], namaJenis: J[1], judul, sub: sub + ' · ' + (final ? 'FINAL (tutup buku)' : 'DRAF — belum tutup buku'), periode, bulan, dari, sampai, final, cap: final ? '' : 'DRAF', baris: baris.map((r) => ({ nama: r.nama, n: r.n === undefined ? null : r.n, kelas: r.kelas || '', teks: r.n === undefined ? '' : r.n === null ? '—' : RP(r.n) })), catatan, tolak, kop: kopUntuk(pakaiKop().pakai.laporan, I) };
}
/** kasPada untuk kas awal arus kas yang BELUM final. Tanggal di tahun yang sudah diarsip (selalu akhir bulan di sini): titik kas sudah pindah ke 31 Des dan mesin
 *  tidak menghitung mundur → kas menurut titik kas saat tahun dikunci (potret kasTitik — angka yang sama dengan sebelum ritual), atau kas akhir bulan dari hitungan
 *  tutup hari (potret kas) bila titik kas saat itu pun belum bisa. Sanggahan Paket B: dulu kas awal Nov 2026 – Jan 2027 hilang sesudah ritual. */
function lpKasPadaLintas(iso) {
  if (!lpTutup(iso)) return ingatKasPada(iso); const Pt = potretBulan(iso); if (!Pt || iso !== akhirBulanIso(lpKey(iso))) return null;
  return typeof Pt.kasTitik === 'number' ? Pt.kasTitik : Pt.kas && typeof Pt.kas.kas === 'number' ? Pt.kas.kas : null;
}
/** Paket bank: beberapa laporan jadi satu, hanya dari bulan yang sudah tutup buku; kop butuh nama & alamat. */
export function paketBank(pilih, kini) {
  const R = rekapOmzet(kini); const F = R.finalTerakhir; const isi = [['labarugi', 'Laba-rugi 3 bulan terakhir (final)'], ['neraca', 'Neraca per akhir bulan final terakhir'], ['aruskas', 'Arus kas 3 bulan terakhir'], ['omzet', 'Rekap omzet 12 bulan']].map((p) => ({ id: p[0], nama: p[1] + (F && p[0] === 'neraca' ? ' — ' + F.nama : ''), dipilih: !!(pilih && pilih[p[0]]) }));
  const nPilih = isi.filter((x) => x.dipilih).length; const I = identitasUsaha();
  const tolak = !F ? 'Belum ada bulan yang tutup buku — bank butuh angka FINAL; sampai tutup buku pertama, cetak laporan biasa bercap DRAF' : !nPilih ? 'Pilih isi paketnya' : !I.lengkap ? 'Kop belum lengkap: nama & alamat wajib' : '';
  const daftar = !tolak ? isi.filter((x) => x.dipilih).map((x) => (x.id === 'omzet' ? { jenis: 'omzet', judul: 'Rekap Omzet Bulanan', periode: '12 bulan', R } : laporanBerkop(x.id, F.key, x.id === 'neraca' ? 1 : 3, kini))) : [];
  // 39b no. 36: dokumen yang menolak dirinya (kas akhir bulan final tanpa tutup hari, stok minus) menahan paket — dulu ikut dicetak dengan kas "—"
  const tolakDok = daftar.filter((d) => d.tolak).map((d) => d.judul + ': ' + d.tolak)[0] || '';
  return { isi, nPilih, F, tolak: tolak || tolakDok, daftar, ket: F ? 'Semua dari bulan FINAL (sampai ' + F.nama + '). Bulan berjalan tidak ikut — bank butuh angka yang sudah tutup buku.' + (!I.npwp ? ' NPWP belum ada: paket tetap bisa disusun, barisnya kosong.' : '') : 'Belum pernah tutup buku — belum ada bulan final.' };
}
/** Banding laba-rugi dua bulan. */
export function bandingLabaRugi(a, b, kini, bayaran) {
  const B = bayaran || bayaranBiayaBulanan(); const satu = (k) => { const L = lpLabaRentang(k + '-01', akhirBulanIso(k), B);   /* Paket B: bulan yang ditutup = potret */ return { omzet: L.omzetHitung, hpp: L.hpp, kotor: L.margin, biaya: L.biayaToko + L.hapusBuku - L.susutStok, kas: L.lebihKurangKas, bersih: L.labaBersih }; }; const A1 = satu(a), A2 = satu(b);
  return { judul: lpNamaBulan(a) + ' vs ' + lpNamaBulan(b), baris: [['Omzet terhitung', 'omzet'], ['HPP', 'hpp'], ['Laba kotor', 'kotor'], ['Biaya, hapus buku & susut', 'biaya']].concat(A1.kas || A2.kas ? [['Lebih/kurang kas', 'kas']] : []).concat([['Laba bersih', 'bersih']]).map((r) => { const d = A1[r[1]] - A2[r[1]]; const pct = A2[r[1]] ? Math.round(d / Math.abs(A2[r[1]]) * 100) : null; return { nama: r[0], a: A1[r[1]], b: A2[r[1]], d, pct, arah: d > 0 ? 'naik' : d < 0 ? 'turun' : '', teksD: (d >= 0 ? '+' : '−') + RP(Math.abs(d)).replace('Rp', '') + (pct === null ? '' : ' (' + (pct >= 0 ? '+' : '') + pct + '%)') }; }) };
}

// ==================== DK4 · DAFTAR HARGA & HARGA YANG NAIK (owner 7 Okt) ====================
// Visi owner 17 Sep: pelanggan yang minta daftar harga, dan "daftar harga apa saja yang NAIK". Sumber = katalog yang SEDANG dipakai kasir (sudah terbit;
// draf tidak ikut — pembeli tidak pernah melihat draf) + riwayat terbit `hargaTerbit` (tiap terbit menulis harga lama → baru). Nama yang diarsipkan
// tidak ikut (hgSemua menyaringnya). Tidak ada angka yang lahir di sini: harga = katalog, kenaikan = selisih katalog dengan harga sebelum periode.
export const LP_KELOMPOK_HARGA = [['semua', 'Semua harga'], ['kg', 'Karung per kg'], ['liter', 'Literan per liter'], ['kemasan', 'Kemasan & karung utuh']].map((x) => ({ id: x[0], nama: x[1] }));
export const LP_RENTANG_NAIK = [['h30', '30 hari terakhir', 30], ['h7', '7 hari terakhir', 7], ['h90', '90 hari terakhir', 90], ['tahun', 'sejak awal tahun', 0]].map((x) => ({ id: x[0], nama: x[1], hari: x[2] }));
const lpKelompokHarga = (st) => (st.id === 'S' ? 'kg' : st.id === 'L' ? 'liter' : 'kemasan');
/** Nama satuan untuk pembeli: per kg · per liter · kemasan 5 kg · karung 25 kg. */
export const lpSatuanPembeli = (st) => (st.id === 'S' ? 'per kg' : st.id === 'L' ? 'per liter' : (st.kg >= 25 ? 'karung ' : 'kemasan ') + String(st.kg).replace('.', ',') + ' kg');
/** Awal periode "harga yang naik" (iso): N hari terakhir termasuk hari ini, atau 1 Januari tahun ini. */
export function lpSejakNaik(id, kini) { const iso = hariIniIso(kini); const R = LP_RENTANG_NAIK.find((r) => r.id === id) || LP_RENTANG_NAIK[0]; return R.hari ? ugTambahHari(iso, -(R.hari - 1)) : iso.slice(0, 4) + '-01-01'; }
/** Harga yang berlaku untuk pembeli = baris katalog berharga terbit (> 0), urutan katalog (merek lalu satuan). kelompok ∈ LP_KELOMPOK_HARGA. */
export function daftarHargaBerlaku(kini, kelompok) {
  const S = hgSemua(kini); const semua = S.baris.filter((b) => b.lamaN > 0).map((b) => ({ k: b.k, merk: b.merk, satuan: lpSatuanPembeli(b.st), kelompok: lpKelompokHarga(b.st), n: b.lamaN, draf: b.adaDraf }));
  const hit = {}; LP_KELOMPOK_HARGA.forEach((g) => { hit[g.id] = g.id === 'semua' ? semua.length : semua.filter((x) => x.kelompok === g.id).length; });
  const g = LP_KELOMPOK_HARGA.some((x) => x.id === kelompok) ? kelompok : 'semua';
  return { daftar: g === 'semua' ? semua : semua.filter((x) => x.kelompok === g), kelompok: g, hit, nDraf: semua.filter((x) => x.draf).length };
}
/**
 * Harga yang NAIK sejak `sejak` (iso). Harga sebelum = `lama` di terbit PERTAMA barang itu di dalam periode (barang yang baru diberi harga di periode itu:
 * harga pertamanya); harga sekarang = katalog yang dipakai kasir. Dicantumkan hanya yang sekarang > sebelum (naik lalu turun lagi ke harga semula tidak
 * dicantumkan). Yang baru diberi harga lalu tidak berubah, yang turun, dan yang kembali ke harga semula DIHITUNG (disebut jumlahnya), tidak dicantumkan.
 * berlaku = hasil daftarHargaBerlaku (supaya katalog dihitung sekali).
 */
export function hargaNaik(sejak, kini, berlaku) {
  const B = berlaku || daftarHargaBerlaku(kini, 'semua');
  const T = ambilHargaTerbit().slice().sort((a, b) => String(a.tanggal || '').localeCompare(String(b.tanggal || '')) || String(a.jam || '').localeCompare(String(b.jam || '')) || (Number(a.id) || 0) - (Number(b.id) || 0));
  const pertama = T.length ? String(T[0].tanggal || '') : ''; const per = {};
  T.forEach((t) => { if (String(t.tanggal || '') < sejak) return; (t.daftar || []).forEach((x) => { const k = String(x.kunci || ''); if (k) (per[k] = per[k] || []).push({ tanggal: String(t.tanggal || ''), lama: Math.round(Number(x.lama) || 0), baru: Math.round(Number(x.baru) || 0) }); }); });
  const naik = []; let nBaru = 0, nTurun = 0, nTetap = 0;
  B.daftar.forEach((b) => {
    const E = per[b.k]; if (!E || !E.length) return; const baru0 = !(E[0].lama > 0); const awal = baru0 ? E[0].baru : E[0].lama; if (!(awal > 0)) { nBaru++; return; }
    if (b.n > awal) { const nk = E.filter((e) => e.lama > 0 && e.baru > e.lama); naik.push({ k: b.k, merk: b.merk, satuan: b.satuan, awal, n: b.n, selisih: b.n - awal, tanggal: (nk.length ? nk[nk.length - 1] : E[E.length - 1]).tanggal }); }
    else if (b.n < awal) nTurun++; else if (baru0) nBaru++; else nTetap++;
  });
  return { naik, nBaru, nTurun, nTetap, pertama, sejak, sebelumRiwayat: !!pertama && sejak < pertama };
}

// ==================== DK4 · DOKUMEN KECIL ====================
/** Nota 60 hari terakhir dikelompokkan per nota (trxId / grupNota / baris tunggal), bisa dicari nama atau isinya. */
export function daftarNota(cari, kini, n) {
  const iso = hariIniIso(kini); const mulai = ugTambahHari(iso, -60); const grup = {}; const urutan = [];
  ambilPenjualanSemua().forEach((p) => { if (!p.tanggal || p.tanggal < mulai || p.tanggal > iso) return; const k = p.trxId ? 't:' + p.trxId : p.grupNota ? 'g:' + p.grupNota : 'i:' + p.id; if (!grup[k]) { grup[k] = []; urutan.push(k); } grup[k].push(p); });
  const t = String(cari || '').trim().toLowerCase(); const out = [];
  urutan.forEach((k) => { const N = notaDariBaris(grup[k]); if (!N) return; const isi = N.baris.map(namaBaris).join(', '); if (t && (N.nama + ' ' + isi).toLowerCase().indexOf(t) < 0) return; out.push({ kunci: k, id: N.id, trxId: N.trxId || N.grupNota || N.id, tanggal: N.tanggal, jam: N.jam, nama: N.nama || 'tanpa nama', isi, total: N.total, cara: N.cara, batal: !N.berlaku || N.dibatalkan, salinan: salinanKe(N.trxId || N.grupNota || N.id) - 1 }); });
  out.sort((a, b) => String(b.tanggal + ' ' + b.jam).localeCompare(String(a.tanggal + ' ' + a.jam))); return { daftar: out.slice(0, n || 40), cocok: out.length };
}
/**
 * Satu dokumen kecil: jenis ∈ setor | upah | piutang | bon | nota; pilih = id pilihan; cari untuk nota. Angka SELALU dari catatan modul lain.
 * Hasil: { judul, sub, baris:[{nama, n, saldo, kelas}], identitas, cap, tolak, pilihan:[{id, nama, n}], ragam, trxId, salinanKe, teksTambahan }.
 */
export function dokumenKecil(jenis, pilih, cari, kini) {
  const iso = hariIniIso(kini); const J = JENIS_KECIL.find((j) => j.id === jenis) || JENIS_KECIL[0]; const P = pakaiKop().pakai; const I = identitasUsaha();
  let judul = J.nama, sub = '', baris = [], identitas = '', tolak = '', cap = '', pilihan = [], ragam = 'ringkas', trxId = null, salinan = null, cocokN = null, teksTambahan = '', saldoPolos = false;
  const brs = (nama, n, saldo, kelas) => ({ nama, n: n === '' || n === undefined ? null : n, saldo: saldo === undefined ? null : saldo, kelas: kelas || '', teks: n === '' || n === undefined ? '' : RP(n), teksSaldo: saldo === undefined || saldo === null ? '' : RP(saldo) });
  if (J.id === 'setor') { ragam = P.setor; const rows = bukuOwner(300).filter((r) => r.ubah === 'modal' && r.arah === 1 || r.judul === 'Pinjaman owner ke toko'); pilihan = rows.map((r) => ({ id: r.id, nama: tanggalPendek(r.tanggal) + ' · ' + r.judul, n: r.n })); const S1 = rows.find((r) => r.id === String(pilih)) || rows[0] || null;
    if (S1) { sub = tanggalPendek(S1.tanggal) + (S1.jam ? ' ' + S1.jam : '') + ' · ' + S1.judul; baris = [brs(S1.judul === 'Pinjaman owner ke toko' ? 'Pinjaman owner ke toko (bukan modal)' : 'Setoran modal dari owner', S1.n)].concat(S1.ket ? [brs('Keterangan: ' + S1.ket, '')] : []).concat([brs('Jumlah', S1.n, undefined, 'jumlah')]); identitas = 'Angka dari catatan Owner & toko — tidak diketik ulang'; } else { sub = 'belum ada setoran modal tercatat'; tolak = 'Belum ada catatan setoran modal (Uang → Owner & toko)'; } }
  if (J.id === 'upah') { ragam = P.slip; const rows = riwayatUpah('', 60); pilihan = rows.map((r) => ({ id: r.id, nama: r.nama + ' · ' + tanggalPendek(String(r.tanggal).slice(0, 10)) + (r.jenis === 'lamaBelum' ? ' · BELUM dibayar' : ''), n: r.n })); const U = rows.find((r) => r.id === String(pilih)) || rows[0] || null;
    if (U) { sub = U.nama + ' · ' + U.ket; if (U.teks) { baris = U.teks.split('\n').slice(3).filter((x) => x.trim()).map((x) => { const m = x.match(/^(.*?)\s{2,}(−?Rp[\d.]+)$/); return m ? brs(m[1].trim(), Number(m[2].replace(/[^\d−-]/g, '').replace('−', '-')), undefined, /^DITERIMA/.test(m[1]) ? 'jumlah' : '') : brs(x.trim(), ''); }); identitas = 'Dari slip yang tersimpan saat upah dibayar (Uang → Orang & upah) — tarif × hari, dikurangi kasbon'; }
      else { baris = [brs('Gaji bulan ' + String(U.id).split('|')[1] + ' (buku bulanan sistem lama)', U.n), brs('Diterima', U.n, undefined, 'jumlah')]; identitas = 'Baris gaji dari buku bulanan sistem lama — tarif & hari per hari tidak tercatat, jadi tidak dirinci'; if (U.jenis === 'lamaBelum') tolak = 'Gaji ini belum dibayar — slip baru ada sesudah dibayar'; } } else { sub = 'belum ada pembayaran upah'; tolak = 'Belum ada upah yang dibayar'; } }
  if (J.id === 'piutang') { ragam = P.kartu; const semua = hitungPiutang().filter((d) => d.mutasi && d.mutasi.length); const bon = semuaBon(kini); const sisaDari = {}; bon.forEach((b) => { sisaDari[b.kunci] = b.sisa; }); const kel = (x) => ((sisaDari[x.kunci] || 0) < LEBIH_AMBANG ? 0 : 1); semua.sort((a, b) => kel(a) - kel(b) || (sisaDari[b.kunci] || 0) - (sisaDari[a.kunci] || 0) || a.nama.localeCompare(b.nama)); /* B2: sisa di bawah nol DI ATAS — layar menggambar 40 pilihan */ pilihan = semua.map((d) => { const sd = sisaDari[d.kunci] || 0; const PL = pecahLebih(d); return { id: d.kunci, nama: d.nama, n: sd < LEBIH_AMBANG ? -sd : sd, ket: sd >= LEBIH_AMBANG ? 'sisa' : PL.hapus > 0.5 ? (PL.uang > 0.5 ? 'di bawah nol' : 'hapus buku terbayar') : 'kelebihan bayar' }; }); const D = semua.find((d) => d.kunci === pilih) || semua[0] || null;
    if (D) { judul = 'Kartu Piutang'; sub = D.nama + ' · sampai ' + tanggalPendek(iso); let sd = 0, tambah = 0, bayar = 0, hapus = 0, retur = 0; const mut = D.mutasi.slice().sort((a, b) => String(a.tanggal + (a.jam || '')).localeCompare(String(b.tanggal + (b.jam || ''))));
      baris = mut.map((m) => { const n = Number(m.nominal) || 0; const masuk = m.jenis === 'jual' || m.jenis === 'saldoAwal'; if (masuk) tambah += n; else if (m.jenis === 'hapusBuku') hapus += n; else if (m.jenis === 'retur') retur += n; else bayar += n; sd += masuk ? n : -n; return brs(tanggalPendek(m.tanggal) + ' · ' + (m.jenis === 'jual' ? 'bon' : m.jenis === 'saldoAwal' ? 'bon lama' : m.jenis === 'hapusBuku' ? (n < 0 ? 'hapus buku dibalik (dibayar sesudah dihapus)' : 'dihapus dari buku') : m.jenis === 'retur' ? 'barang kembali (retur)' : 'bayar') + (m.ket && m.jenis !== 'bayar' ? ' · ' + String(m.ket).slice(0, 40) : ''), masuk ? n : -n, sd); });
      baris.push(brs(sd < LEBIH_AMBANG ? (pecahLebih(D).hapus > 0.5 ? 'Di bawah nol — ' + ringkasLebih(pecahLebih(D)) : 'Kelebihan bayar (uang pelanggan dipegang toko)') : 'Sisa bon', sd, undefined, 'jumlah')); identitas = 'Sisa ' + RP(sd) + ' = bon ' + RP(tambah) + ' − bayar ' + RP(bayar) + (hapus ? ' − dihapus ' + RP(hapus) : '') + (retur ? ' − retur ' + RP(retur) : ''); if (Math.abs(sd - (D.sisa || 0)) > 0.5) tolak = 'Saldo kartu ' + RP(sd) + ' ≠ sisa menurut mesin ' + RP(D.sisa) + ' — tidak dicetak sampai ketemu sebabnya'; } else { sub = 'belum ada pelanggan berbon'; tolak = 'Belum ada catatan bon pelanggan'; } }
  if (J.id === 'bon') { ragam = P.bon; const UP = {}; hitungUtangPemasok().forEach((u) => { UP[kunciPelanggan(u.pemasok)] = u; }); const pem = daftarPemasok().map((p) => Object.assign({}, p, { totalUtang: UP[p.kunci] ? UP[p.kunci].totalUtang || 0 : 0, tekor: UP[p.kunci] ? UP[p.kunci].tekor || 0 : 0 })).sort((a, b) => b.totalUtang - a.totalUtang || a.nama.localeCompare(b.nama)); pilihan = pem.map((p) => ({ id: p.kunci, nama: p.nama, n: p.totalUtang, ket: 'sisa' })); const M = pem.find((p) => p.kunci === pilih) || pem[0] || null;
    if (M) { judul = 'Rekap Bon Pemasok'; sub = M.nama + ' · sampai ' + tanggalPendek(iso); const BB = bukuBon(M.nama); let total = 0, bayar = 0; baris = BB.baris.map((e) => { if (e.n > 0) total += e.n; else bayar += -e.n; return brs((e.t ? tanggalPendek(e.t) + ' · ' : '') + e.teks + (e.ket ? ' · ' + String(e.ket).slice(0, 40) : ''), e.n, e.saldo); }); baris.push(brs('Sisa utang ke ' + M.nama, BB.saldo, undefined, 'jumlah')); identitas = 'Sisa ' + RP(BB.saldo) + ' = bon ' + RP(total) + ' − dibayar ' + RP(bayar); if (Math.abs(BB.saldo - M.totalUtang) > 0.5) identitas += ' · mesin utang pemasok menyebut ' + RP(M.totalUtang) + (M.tekor ? ' (kelebihan bayar ' + RP(M.tekor) + ')' : ''); } else { sub = 'belum ada pemasok'; tolak = 'Belum ada catatan pemasok'; } }
  if (J.id === 'nota') { ragam = P.nota; const DN = daftarNota(cari, kini, 40); cocokN = DN.cocok; pilihan = DN.daftar.map((x) => ({ id: x.kunci, nama: tanggalPendek(x.tanggal) + ' ' + x.jam + ' · ' + x.nama + ' · ' + x.isi + (x.batal ? ' · DIBATALKAN' : x.salinan ? ' · salinan ' + x.salinan + '×' : ''), n: x.total })); const X = DN.daftar.find((x) => x.kunci === pilih) || null;
    if (X) { const N = notaDari(X.kunci.indexOf('t:') === 0 ? { trxId: X.trxId } : X.kunci.indexOf('g:') === 0 ? { grupNota: X.trxId } : { id: X.id }); const S = N ? susunStruk(N, stAtur(), { kini: iso }) : null; trxId = X.trxId; salinan = salinanKe(trxId); judul = 'Nota'; sub = tanggalPendek(X.tanggal) + ' ' + X.jam + ' · ' + X.nama + ' · ' + X.cara;
      baris = S ? S.garis.filter((g) => !g.garis && g.kanan).map((g) => brs(g.sisaBonPer ? g.kiri + ' · per ' + formatTanggal(g.sisaBonPer) : g.kiri, g.kanan.replace(/[^\d−-]/g, '') ? Number(g.kanan.replace(/[^\d−-]/g, '').replace('−', '-')) : '', undefined, /^TOTAL/i.test(g.kiri) ? 'jumlah' : '')) : [brs(X.isi, X.total, undefined, 'jumlah')]; teksTambahan = S ? S.teks : '';
      cap = X.batal ? 'DIBATALKAN' : 'SALINAN ke-' + salinan; identitas = X.batal ? 'Nota ini dibatalkan — tidak dicetak ulang' : 'Cetak ulang ke-' + salinan + ' · nota asli ' + tanggalPendek(X.tanggal) + ' ' + X.jam + ' · angka dari nota yang tersimpan'; if (X.batal) tolak = 'Nota dibatalkan tidak dicetak ulang'; } else { sub = cocokN + ' nota cocok — ketuk salah satu'; tolak = 'Pilih notanya'; } }
  // owner 7 Okt: daftar harga untuk pelanggan — dikelompokkan per merek; pilihan = kelompok satuan (jumlah harganya, bukan rupiah → teksN)
  if (J.id === 'harga') { ragam = P.harga; const H = daftarHargaBerlaku(kini, pilih || 'semua'); const G = LP_KELOMPOK_HARGA.find((g) => g.id === H.kelompok);
    pilihan = LP_KELOMPOK_HARGA.filter((g) => g.id === 'semua' || H.hit[g.id] > 0).map((g) => ({ id: g.id, nama: g.nama, n: null, teksN: H.hit[g.id] + ' harga' }));
    judul = 'Daftar Harga'; sub = 'berlaku ' + tanggalPendek(iso) + ' · ' + (H.kelompok === 'semua' ? '' : G.nama.toLowerCase() + ' · ') + H.daftar.length + ' harga';
    let m0 = null; H.daftar.forEach((x) => { if (x.merk !== m0) { m0 = x.merk; baris.push(brs(x.merk, '', undefined, 'kel')); } baris.push(brs(x.satuan, x.n)); });
    identitas = 'Harga yang sedang dipakai kasir (sudah terbit)' + (H.nDraf ? '; ' + H.nDraf + ' perubahan yang masih draf belum ikut' : '') + '.';
    if (!H.daftar.length) tolak = 'Belum ada harga yang terbit' + (H.kelompok === 'semua' ? '' : ' di kelompok ini') + ' — atur di Harga & Pemasok → Katalog lalu terbitkan'; }
  // owner 7 Okt: harga yang NAIK — kolom tengah "sebelum → sekarang", kolom kanan naiknya; pilihan = periode (jumlah yang naik)
  if (J.id === 'naik') { ragam = P.harga; const B = daftarHargaBerlaku(kini, 'semua'); const R0 = LP_RENTANG_NAIK.find((r) => r.id === pilih) || LP_RENTANG_NAIK[0];
    pilihan = LP_RENTANG_NAIK.map((r) => { const Y = hargaNaik(lpSejakNaik(r.id, kini), kini, B); return { id: r.id, nama: r.nama + ' · sejak ' + tanggalPendek(Y.sejak), n: null, teksN: Y.naik.length + ' naik' }; });
    const X = hargaNaik(lpSejakNaik(R0.id, kini), kini, B); judul = 'Harga yang Naik'; sub = 'sejak ' + tanggalPendek(X.sejak) + ' sampai ' + tanggalPendek(iso) + ' · ' + X.naik.length + ' harga naik';
    let m0 = null; X.naik.forEach((x) => { if (x.merk !== m0) { m0 = x.merk; baris.push(brs(x.merk, '', undefined, 'kel')); } baris.push({ nama: x.satuan + ' · naik ' + tanggalPendek(x.tanggal), n: x.n, saldo: x.selisih, kelas: '', teks: RP(x.awal) + ' → ' + RP(x.n), teksSaldo: '+' + RP(x.selisih) }); });
    if (!X.naik.length) baris.push(brs('Tidak ada harga yang naik sejak ' + tanggalPendek(X.sejak), ''));
    const lain = [X.nTurun ? X.nTurun + ' harga turun' : '', X.nTetap ? X.nTetap + ' kembali ke harga semula' : '', X.nBaru ? X.nBaru + ' baru diberi harga' : ''].filter(Boolean);
    identitas = 'Harga sebelum → harga sekarang (yang dipakai kasir, sudah terbit); kanan = naiknya. Draf belum ikut.' + (lain.length ? ' Di periode ini juga: ' + lain.join(', ') + ' — tidak dicantumkan.' : '') + (X.sebelumRiwayat ? ' Riwayat harga tercatat sejak ' + tanggalPendek(X.pertama) + ' — kenaikan sebelum tanggal itu tidak terbaca.' : '');
    saldoPolos = true; if (!X.pertama) tolak = 'Belum ada riwayat harga — harga yang naik baru terbaca sesudah harga diubah lewat Harga & Pemasok → Katalog lalu diterbitkan'; }
  if (!tolak && !I.lengkap) tolak = 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)';
  return { jenis: J.id, namaJenis: J.nama, judul, sub, baris, identitas, cap, tolak, pilihan, ragam, kop: kopUntuk(ragam, I), trxId, salinanKe: salinan, cocokN, teksTambahan, adaSaldo: baris.some((b) => b.saldo !== null), saldoPolos };
}
/** Wujud teks satu dokumen (untuk WhatsApp / pratinjau): kop, judul, baris, catatan, nomor. */
export function teksDokumen(D, nomor, iso) {
  const k = D.kop; const L = [k.nama.toUpperCase()]; if (k.alamat) L.push(k.alamat); if (k.resmi) L.push(k.resmi); L.push('', (D.judul || '').toUpperCase() + (D.cap ? ' — ' + D.cap : ''), D.sub || '', '');
  (D.baris || []).forEach((b) => { if (b.kelas === 'kel') L.push(b.nama.toUpperCase()); else L.push((b.kelas === 'jumlah' ? '' : '  ') + b.nama + (b.teks ? '  ' + b.teks : '') + (b.teksSaldo ? (D.saldoPolos ? '  (' + b.teksSaldo + ')' : '  (saldo ' + b.teksSaldo + ')') : '')); });
  if (D.identitas || D.catatan) L.push('', D.identitas || D.catatan); L.push('', (k.slogan ? k.slogan + ' · ' : '') + 'No. ' + ANGKA(nomor) + ' · kop v' + k.versi + ' · ' + tanggalPendek(iso)); return L.join('\n');
}
export const lpKunciOrang = kunciPelanggan;

// ==================== MINGGUAN · Senin–Minggu (owner 23 Sep) ====================
const LP_HARI = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'];
/** Senin dari minggu yang memuat tanggal itu (minggu toko = Senin–Minggu). */
export const lpSenin = (iso) => ugTambahHari(iso, -((new Date(iso + 'T00:00:00Z').getUTCDay() + 6) % 7));
const lpPersen = (a, b) => (b > 0 ? Math.round((a - b) / b * 1000) / 10 : null);
const lpBandingTeks = (pct, apa) => (pct === null ? apa + ' belum ada pembanding' : pct === 0 ? 'sama dengan ' + apa : (pct > 0 ? 'naik ' : 'turun ') + String(Math.abs(pct)).replace('.', ',') + ' % dari ' + apa);
/** Delapan minggu terakhir untuk pemilih: {awal (Senin), akhir (Minggu), label, berjalan, penuh}. Minggu sebelum catatan pertama tidak ditawarkan. */
export function daftarMinggu(kini, n) {
  const iso = hariIniIso(kini); const senin = lpSenin(iso); const p = lpPertama(); const out = [];
  for (let i = 0; i < (n || 8); i++) { const a = ugTambahHari(senin, -7 * i); const b = ugTambahHari(a, 6); if (p && b < p) break; out.push({ awal: a, akhir: b, label: tanggalPendek(a).slice(0, 6) + ' – ' + tanggalPendek(b).slice(0, 6), pendek: tanggalPendek(a).slice(0, 6), berjalan: i === 0, penuh: b <= iso }); }
  return out;
}
/** Rekap satu minggu (Senin `awal`): tujuh hari dengan omzet & nota, inti (mesin laba & arus kas yang sama), banding minggu sebelumnya. Σ hari = omzet minggu (penjaga identitas tergambar). */
export function rekapMinggu(awal, kini, bayaran) {
  const iso = hariIniIso(kini); const akhir = ugTambahHari(awal, 6); const B = bayaran || bayaranBiayaBulanan(); const cocok = (t) => !!t && t >= awal && t <= akhir;
  // Paket B: minggu yang menyentuh tahun yang sudah ditutup buku (mis. 28 Des – 3 Jan) — omzet, nota & margin per hari dari potret hari; laba bersih & arus kas
  // minggu itu tidak bisa disusun (potretnya per bulan, catatan harinya diarsip) → null + `diarsip` / `tanpaPotret` (layar menyebutnya, tidak menggambar Rp0)
  if (lpBulanDitutup(awal, akhir).length) return lpMingguArsip(awal, akhir, iso);
  const L = ugLabaBersih(awal, akhir, B); const K = hitungArusKasInti(cocok, B); const Lr = hitungLabaRentang(cocok);
  const hari = []; for (let i = 0; i < 7; i++) { const t = ugTambahHari(awal, i); const Lh = hitungLabaRentang((x) => x === t); hari.push({ iso: t, nama: LP_HARI[i], tgl: String(parseInt(t.slice(8, 10), 10)), omzet: Lh.omzetPenuh, n: jumlahNota((x) => x === t), margin: Lh.margin, depan: t > iso, hariIni: t === iso }); }
  const jalan = hari.filter((h) => !h.depan); const omzet = hari.reduce((a, h) => a + h.omzet, 0); const n = hari.reduce((a, h) => a + h.n, 0); const maks = Math.max(1, ...hari.map((h) => h.omzet));
  const lalu = lpHariRentang(ugTambahHari(awal, -7), ugTambahHari(awal, -1)); const pct = lpPersen(omzet, lalu.omzetPenuh);   // Paket B: minggu lalu bisa di tahun yang ditutup
  const isi = jalan.filter((h) => h.n > 0); const terbaik = isi.length ? isi.reduce((a, h) => (h.omzet > a.omzet ? h : a)) : null; const sepi = isi.length ? isi.reduce((a, h) => (h.omzet < a.omzet ? h : a)) : null;
  return { awal, akhir, label: tanggalPendek(awal) + ' – ' + tanggalPendek(akhir), berjalan: akhir >= iso, hariJalan: jalan.length, hari, omzet, n, maks, rataHari: jalan.length ? Math.round(omzet / jalan.length) : 0, cocokJumlah: omzet === Lr.omzetPenuh,
    hpp: L.hpp, margin: L.margin, biayaToko: L.biayaToko, labaBersih: L.labaBersih, susut: L.susutStok, lebihKurangKas: L.lebihKurangKas, omzetTanpaHpp: L.omzetTanpaHpp, jumlahTanpaHpp: L.jumlahTanpaHpp, masuk: K.totalMasuk, keluar: K.totalKeluar, bersih: K.bersih, kredit: K.kreditBulanIni,
    lalu: lalu.omzetPenuh, pct, bandingTeks: lpBandingTeks(pct, 'minggu sebelumnya') + (lalu.omzetPenuh ? ' (' + RP(lalu.omzetPenuh) + ')' : ''), terbaik, sepi, kosong: n === 0 && K.totalMasuk === 0 && K.totalKeluar === 0 };
}
function lpMingguArsip(awal, akhir, iso) {
  const hari = []; for (let i = 0; i < 7; i++) { const t = ugTambahHari(awal, i); const X = lpHariRentang(t, t); hari.push(Object.assign({ iso: t, nama: LP_HARI[i], tgl: String(parseInt(t.slice(8, 10), 10)), omzet: X.omzetPenuh, n: X.nota, margin: X.margin, depan: t > iso, hariIni: t === iso }, lpTutup(t) ? { diarsip: true, tanpaPotret: X.tanpaPotret > 0 } : {})); }
  const W = lpHariRentang(awal, akhir); const jalan = hari.filter((h) => !h.depan); const omzet = hari.reduce((a, h) => a + h.omzet, 0); const n = hari.reduce((a, h) => a + h.n, 0); const maks = Math.max(1, ...hari.map((h) => h.omzet));
  const lalu = lpHariRentang(ugTambahHari(awal, -7), ugTambahHari(awal, -1)); const pct = lalu.tanpaPotret ? null : lpPersen(omzet, lalu.omzetPenuh);
  const isi = jalan.filter((h) => h.n > 0); const terbaik = isi.length ? isi.reduce((a, h) => (h.omzet > a.omzet ? h : a)) : null; const sepi = isi.length ? isi.reduce((a, h) => (h.omzet < a.omzet ? h : a)) : null;
  return { awal, akhir, label: tanggalPendek(awal) + ' – ' + tanggalPendek(akhir), berjalan: akhir >= iso, hariJalan: jalan.length, hari, omzet, n, maks, rataHari: jalan.length ? Math.round(omzet / jalan.length) : 0, cocokJumlah: omzet === W.omzetPenuh,
    hpp: null, margin: W.margin, biayaToko: null, labaBersih: null, susut: null, lebihKurangKas: 0, omzetTanpaHpp: null, jumlahTanpaHpp: W.jumlahTanpaHpp, masuk: null, keluar: null, bersih: null, kredit: 0,
    lalu: lalu.omzetPenuh, pct, bandingTeks: lpBandingTeks(pct, 'minggu sebelumnya') + (lalu.omzetPenuh && pct !== null ? ' (' + RP(lalu.omzetPenuh) + ')' : ''), terbaik, sepi, kosong: n === 0 && !W.tanpaPotret, diarsip: W.diarsip, tanpaPotret: W.tanpaPotret };
}

// ==================== TAHUNAN · dua belas bulan (owner 23 Sep) ====================
/** Tahun-tahun yang punya catatan, terbaru dulu. */
export function daftarTahun(kini) { const th = Number(hariIniIso(kini).slice(0, 4)); const p = lpPertama(); const awal = p ? Number(p.slice(0, 4)) : th; const out = []; for (let y = th; y >= awal; y--) out.push({ tahun: y, berjalan: y === th, final: lpTahunFinal(y) }); return out; }
/** Rekap satu tahun: 12 bulan (omzet, nota, margin, biaya, laba bersih) dari mesin yang sama; jumlah tahun = Σ bulan; banding tahun sebelumnya; bulan terbaik & tersepi. */
export function rekapTahun(tahun, kini, bayaran) {
  const iso = hariIniIso(kini); const B = bayaran || bayaranBiayaBulanan(); const kiniKey = iso.slice(0, 7); const bulan = []; const ab = lpAwalBuku();
  for (let m = 1; m <= 12; m++) { const key = tahun + '-' + String(m).padStart(2, '0'); const depan = key > kiniKey;
    if (depan) { bulan.push({ key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key), depan: true, berjalan: false, final: false, omzet: 0, n: 0, margin: 0, biaya: 0, labaBersih: 0, susut: 0 }); continue; }
    // Paket B: bulan di tahun yang sudah ditutup buku = potret (L = ugLabaBersih bulan itu, omzet & nota = pjOmzetSistem saat kunci); tanpa potret = '—', bukan Rp0
    const Pt = potretBulan(key); if (!Pt && lpTutup(key)) { bulan.push({ key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key), depan: false, berjalan: false, final: lpFinal(key), omzet: null, n: 0, margin: null, biaya: null, labaBersih: null, susut: null, kas: null, hpp: null, sebelumBuku: key < ab, tanpaPotret: true }); continue; }
    const L = Pt ? Pt.L : ugLabaBersih(key + '-01', akhirBulanIso(key), B); const Lr = Pt ? { omzetPenuh: Pt.omzet } : hitungLabaRentang((t) => !!t && bulanDari(t) === key);
    bulan.push(Object.assign({ key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key), depan: false, berjalan: key === kiniKey, final: lpFinal(key), omzet: Lr.omzetPenuh, n: Pt ? Pt.n : jumlahNota((t) => !!t && bulanDari(t) === key), margin: L.margin, biaya: L.biayaToko, labaBersih: L.labaBersih, susut: L.susutStok, kas: L.lebihKurangKas, hpp: L.hpp, sebelumBuku: key < ab }, Pt ? { diarsip: true } : {})); }
  // 39b no. 40: bulan sebelum awal buku tetap di daftar (dengan keterangan), tidak ikut Σ tahun
  const ada = bulan.filter((b) => !b.depan); const jml = (k) => ada.reduce((a, b) => a + (b.sebelumBuku ? 0 : b[k] || 0), 0); const omzet = jml('omzet'); const n = jml('n');
  const pra = ada.filter((b) => b.sebelumBuku); const sebelumBuku = pra.length ? lpKetSebelumBuku(lpBulanPendek(pra[0].key) + (pra.length > 1 ? ' – ' + lpBulanPendek(pra[pra.length - 1].key) : ''), pra.reduce((a, b) => a + b.labaBersih, 0)) : '';
  // Paket B: tahun yang ditutup — pemeriksa Σ bulan = Σ HARI potret (dua bagian potret yang disusun terpisah); tahun lalu yang ditutup = Σ bulan potretnya
  const Pth = potretTahun(tahun); const tanpaPotret = bulan.filter((b) => b.tanpaPotret).length;
  const Lt = Pth ? { omzetPenuh: Object.keys(Pth.hari || {}).reduce((a, d) => a + (Number(Pth.hari[d][0]) || 0), 0) } : tanpaPotret ? { omzetPenuh: null } : hitungLabaRentang((t) => !!t && String(t).slice(0, 4) === String(tahun)); const maks = Math.max(1, ...bulan.map((b) => b.omzet));
  const laluL = { omzetPenuh: lpOmzetTahun(tahun - 1) }; const pct = laluL.omzetPenuh === null ? null : lpPersen(omzet, laluL.omzetPenuh);
  const isi = ada.filter((b) => b.n > 0); const terbaik = isi.length ? isi.reduce((a, b) => (b.omzet > a.omzet ? b : a)) : null; const sepi = isi.length ? isi.reduce((a, b) => (b.omzet < a.omzet ? b : a)) : null;
  const bulanJalan = ada.filter((b) => b.n > 0 || b.berjalan).length; const final = lpTahunFinal(tahun);
  return { tahun, bulan, ada: ada.length, bulanJalan, omzet, n, cocokJumlah: omzet === Lt.omzetPenuh, hpp: jml('hpp'), margin: jml('margin'), biaya: jml('biaya'), labaBersih: jml('labaBersih'), susut: jml('susut'), lebihKurangKas: jml('kas'), maks,
    rataBulan: bulanJalan ? Math.round(omzet / bulanJalan) : 0, lalu: laluL.omzetPenuh, pct, bandingTeks: lpBandingTeks(pct, 'tahun ' + (tahun - 1)) + (laluL.omzetPenuh ? ' (' + RP(laluL.omzetPenuh) + ')' : ''), terbaik, sepi, final, berjalan: String(tahun) === iso.slice(0, 4),
    status: final ? 'FINAL — sudah tutup buku' + (Pth ? ' · dari potret saat dikunci' : tanpaPotret ? ' · TANPA potret: ' + tanpaPotret + ' bulan hanya ada di berkas arsip' : '') : String(tahun) === iso.slice(0, 4) ? 'DRAF — tahun berjalan, sampai ' + tanggalPendek(iso) : 'DRAF — belum tutup buku', kosong: n === 0 && !tanpaPotret, sebelumBuku,
    diarsip: !!Pth, tanpaPotret };
}
/** Paket B: omzet setahun (omzet mesin) — tahun yang ditutup = Σ bulan potretnya; ditutup tanpa potret = null (tidak ada pembanding, bukan Rp0). */
export function lpOmzetTahun(y) { const P = potretTahun(y); if (P) return Object.keys(P.bulan || {}).reduce((a, k) => a + (Number(P.bulan[k].omzet) || 0), 0); if (lpTutup(String(y))) return null; return hitungLabaRentang((t) => !!t && String(t).slice(0, 4) === String(y)).omzetPenuh; }
