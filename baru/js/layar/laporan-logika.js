// LOGIKA layar LAPORAN & DOKUMEN (putaran 19), tanpa DOM. Enam keluarga: Laba (tiga angka yang tidak boleh tertukar: margin kotor · laba bersih · diterima
// tunai, per bulan) · Harian (rekap satu hari + buku kas hari itu + kirim WA) · Bulanan (enam bulan, inti bulan, DK3 rekap omzet 12 bulan: kumulatif, tanda
// dilaporkan, tarif & batas = SETELAN OWNER, bukti bernomor) · Neraca (kekayaan toko per tanggal, dua sisi) · Dokumen (DK2 laporan berkop laba-rugi / neraca /
// arus kas 1·3·12 bulan, DRAF sebelum tutup buku, paket bank, banding periode; DK4 dokumen kecil: bukti setor modal, slip upah, kartu piutang, rekap bon
// pemasok, cetak ulang nota = SALINAN ke-N) · Setelan (DK1 kop & identitas usaha berversi, dokumen mana pakai kop mana, nomor dokumen).
// SEMUA angka dari mesin beku yang sama dengan sistem lama (hitungLabaBersihRentang, hitungArusKasInti, hitungNeraca, kasPada) — di sini cuma disusun, diberi kop,
// dinomori, lalu dicetak / PDF / WA. Yang BARU ditulis: aturanToko/{identitas, dokumen, rekapOmzet, laporan} + koleksi dokumenCetak (tiap cetakan bernomor).
// Kejujuran: bulan belum tutup buku = DRAF; neraca yang kasnya belum bisa dihitung / stoknya minus TIDAK dicetak; kas akhir arus kas = kas neraca (satu mesin);
// tarif/batas rekap omzet bukan nasihat pajak. Nama pembantu diprefiks `lp` (bundel uji jsc satu lingkup).
import { hitungLabaRentang, hitungLabaBersihRentang, hitungArusKasInti, barisSusutStok, bayaranBiayaBulanan, hitungNeraca, kasPada, hitungPiutang, hitungUtangPemasok } from '../mesin/beku.js';
import { akhirBulanIso, bulanDari, namaBulanPanjang, caraBayarKunci, hppTercatat, daftarGerakanKas, namaSingkatTrx, kunciPelanggan } from '../mesin/pembantu.js';
import { ambilPenjualan, ambilPenjualanSemua, ambilPengeluaranHarian, ambilSemuaBatch, ambilTutupHari, ambilTitikKas, ambilDokumenCetak, cacheMentah } from '../data/toko.js';
import { RP, ANGKA, hariIniIso, tanggalPendek } from '../inti/format.js';
import { ugAturDok, ugAngka, ugKosong, ugTambahHari, modalTertanam, aturKeluar, priveBulan } from './uang-logika.js';
import { bkEra } from './tutup-buku-logika.js';
import { notaDari, notaDariBaris, susunStruk, stAtur, namaBaris } from './struk-logika.js';
import { riwayatUpah } from './upah-logika.js';
import { semuaBon } from './bon-logika.js';
import { daftarPemasok, bukuBon } from './bon-pemasok-logika.js';
import { bukuOwner } from './owner-toko-logika.js';
import { pjOmzetSistem, pjGabungRekap, pjTahun, PJ_LABEL } from './pajak-logika.js';

export const KELUARGA_LAPORAN = [['laba', 'Laba'], ['harian', 'Harian'], ['mingguan', 'Mingguan'], ['bulanan', 'Bulanan'], ['pajak', 'Pajak'], ['tahunan', 'Tahunan'], ['neraca', 'Neraca'], ['dokumen', 'Dokumen'], ['setelan', 'Setelan']];   // Mingguan & Tahunan: owner 23 Sep
export const JENIS_LAPORAN = [['labarugi', 'Laba-Rugi'], ['neraca', 'Neraca'], ['aruskas', 'Arus Kas']];
export const RENTANG_LAPORAN = [[1, '1 bulan'], [3, '3 bulan'], [12, '12 bulan']];
export const JENIS_KECIL = [['setor', 'Bukti setoran modal', 'dari catatan Owner & toko'], ['upah', 'Slip upah', 'dari buku upah'], ['piutang', 'Kartu piutang', 'per pelanggan'], ['bon', 'Rekap bon pemasok', 'per pemasok'], ['nota', 'Cetak ulang nota', 'SALINAN bercap']].map((j) => ({ id: j[0], nama: j[1], ket: j[2] }));
export const DOKUMEN_KOP = [['nota', 'Nota pelanggan & cetak ulang', 'ringkas'], ['kartu', 'Kartu piutang', 'ringkas'], ['slip', 'Slip upah', 'ringkas'], ['harian', 'Rekap harian', 'ringkas'], ['laporan', 'Laba-rugi · neraca · arus kas', 'penuh'], ['omzet', 'Rekap omzet bulanan', 'penuh'], ['bon', 'Rekap bon pemasok', 'penuh'], ['setor', 'Bukti setoran modal', 'penuh']].map((d) => ({ id: d[0], nama: d[1], awal: d[2] }));
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
/** Tanggal catatan pertama toko (nota atau kedatangan sungguhan) — awal buku. */
export function lpPertama() { let p = ''; ambilPenjualanSemua().forEach((d) => { if (d.tanggal && (!p || d.tanggal < p)) p = d.tanggal; }); ambilSemuaBatch().forEach((b) => { if (!b.stokAwal && !b.tutupBuku && b.tanggal && (!p || b.tanggal < p)) p = b.tanggal; }); return p; }
/** Bulan FINAL = tahunnya sudah ditutup buku (era = tahun saldo pembuka terakhir). Sebelum tutup buku pertama: semua DRAF. */
export function lpFinal(key) { const era = bkEra(); return era !== null && Number(key.slice(0, 4)) <= era; }
/** Daftar bulan dari catatan pertama sampai bulan berjalan, TERBARU dulu (paling banyak `maks`). */
export function daftarBulan(kini, maks) { const akhir = lpKey(hariIniIso(kini)); const p = lpPertama(); const awal = p ? lpKey(p) : akhir; const out = []; let k = akhir; while (k >= awal && out.length < (maks || 24)) { out.push({ key: k, nama: lpNamaBulan(k), pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || out.length === 0), final: lpFinal(k), berjalan: k === akhir }); k = lpGeserBulan(k, -1); } return out; }
const lpMdrRentang = (dari, sampai) => ambilPengeluaranHarian().reduce((a, h) => a + (h.mdr && h.kategori === 'toko' && h.tanggal >= dari && h.tanggal <= sampai ? (Number(h.nominal) || 0) : 0), 0);

// ==================== LABA · tiga angka per bulan ====================
/** Laba satu bulan lewat mesin yang sama dengan kaca Laba sistem lama: margin kotor · laba bersih · diterima tunai (= bersih − margin nota kredit). */
export function labaBulan(key, kini, bayaran) {
  const iso = hariIniIso(kini); const awal = key + '-01', akhir = akhirBulanIso(key); const B = bayaran || bayaranBiayaBulanan(); const L = hitungLabaBersihRentang(awal, akhir, B);
  let marginKredit = 0, omzetKredit = 0, nKredit = 0; ambilPenjualan().forEach((p) => { if (!p.tanggal || p.tanggal < awal || p.tanggal > akhir || caraBayarKunci(p) !== 'kredit') return; nKredit += 1; omzetKredit += p.hargaTotal || 0; if (hppTercatat(p)) marginKredit += (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0); });
  const tunai = L.labaBersih - marginKredit; const omzetKotor = L.omzetHitung + L.returUang; const penyebut = omzetKotor + L.omzetTanpaHpp; const cakupan = penyebut > 0 ? omzetKotor / penyebut : null;
  const mdr = lpMdrRentang(awal, akhir); const biayaLain = L.biayaToko - mdr;
  const terjun = [['Omzet terhitung', omzetKotor]].concat(L.returJumlah ? [['Retur & refund (' + L.returJumlah + ')', -L.returUang]] : []).concat([['HPP barang', -(L.hpp + L.returHpp)]]).concat(L.returHpp > 0 ? [['HPP barang yang kembali ke stok', L.returHpp]] : [])
    .concat([['Margin kotor', L.margin, 'jumlah'], ['Biaya toko (harian + jatah bulanan)', -biayaLain]]).concat(mdr ? [['Potongan QRIS (MDR)', -mdr]] : []).concat(L.hapusBuku ? [['Hapus buku piutang', -L.hapusBuku]] : []).concat([['Susut & selisih stok', L.susutStok], ['Laba bersih', L.labaBersih, 'jumlah']]).map((r) => ({ nama: r[0], n: r[1], kelas: r[2] || '' }));
  const cocok = (t) => !!t && t >= awal && t <= akhir; const susut = barisSusutStok(cocok);
  const bulan = ambilPenjualan().filter((p) => cocok(p.tanggal)); const rugi = bulan.filter((p) => hppTercatat(p) && (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0) < 0).map((p) => ({ id: p.id, nama: namaSingkatTrx(p), tanggal: p.tanggal, jam: p.jam || '', omzet: p.hargaTotal || 0, margin: (p.hargaTotal || 0) - (p.hppTotalSaatJual || 0) })).sort((a, b) => a.margin - b.margin);
  const tanpaHpp = bulan.filter((p) => !hppTercatat(p)).map((p) => ({ id: p.id, nama: namaSingkatTrx(p), tanggal: p.tanggal, jam: p.jam || '', omzet: p.hargaTotal || 0 })).sort((a, b) => String(b.tanggal + b.jam).localeCompare(String(a.tanggal + a.jam)));
  const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && !susut.length; const berjalan = key === lpKey(iso);
  let aman = null; if (berjalan) { const A = aturKeluar(iso); const P = priveBulan(iso); aman = { batas: A.aman, dariLaba: A.amanDariLaba, terpakai: P.total, sisa: A.aman - P.total }; }
  return { key, nama: lpNamaBulan(key), berjalan, final: lpFinal(key), L, margin: L.margin, labaBersih: L.labaBersih, tunai, marginKredit, omzetKredit, nKredit, cakupan, omzetKotor, penyebut, mdr, biayaLain, terjun, susut, susutTotal: L.susutStok, rugi, tanpaHpp, omzetTanpaHpp: L.omzetTanpaHpp, tanpaCatatan, aman,
    pct: (a, b) => (b > 0 ? (a < 0 ? '−' : '') + Math.abs(a / b * 100).toFixed(1).replace('.', ',') + '%' : '—') };
}

// ==================== HARIAN · rekap satu hari ====================
/** Rekap satu hari — arus kas & laba dari mesin yang sama (dataRekapHarian sistem lama) + per jam + tutup hari + buku kas hari itu. */
export function rekapHari(iso, bayaran) {
  const B = bayaran || bayaranBiayaBulanan(); const K = hitungArusKasInti((t) => t === iso, B); const L = hitungLabaRentang((t) => t === iso);
  const jam = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== iso) return; const j = String(p.jam || '').slice(0, 2) || '??'; if (!jam[j]) jam[j] = { jam: j, n: 0, omzet: 0 }; jam[j].n += 1; jam[j].omzet += p.hargaTotal || 0; });
  const perJam = Object.keys(jam).sort().map((j) => jam[j]); const maksJam = Math.max(1, ...perJam.map((x) => x.omzet));
  const tutup = ambilTutupHari().find((t) => t.tanggal === iso) || null; const buku = daftarGerakanKas().filter((r) => r.t === iso).sort((a, b) => String(a.jam).localeCompare(String(b.jam)));
  return { iso, omzet: L.omzetPenuh, n: L.jumlahTrx, margin: L.margin, jumlahTanpaHpp: L.jumlahTanpaHpp, tunai: K.pos.tunai, qris: K.pos.qris, kredit: K.kreditBulanIni, nKredit: K.jumlahKredit, pelunasan: K.pos.pelunasan, refund: K.pos.refund, keluarHarian: K.pos.harian, prive: K.pos.prive, setoran: K.pos.setoran, belanja: K.pos.belanja, bayarBon: K.pos.bayarBon, biayaBulanan: K.pos.biayaBulanan,
    totalMasuk: K.totalMasuk, totalKeluar: K.totalKeluar, bersih: K.bersih, masuk: K.masuk.filter((x) => x.nominal > 0), keluar: K.keluar.filter((x) => x.nominal > 0), perJam, maksJam, tutup: tutup ? { jam: tutup.jam || '', selisih: Number(tutup.selisihLaci || tutup.selisih || 0), sistemBaru: !!tutup.sistemBaru } : null, buku, kosong: L.jumlahTrx === 0 && K.totalMasuk === 0 && K.totalKeluar === 0 };
}
/** Empat belas hari terakhir untuk pemilih tanggal: omzet & jumlah nota per hari (yang kosong tetap ada, ditandai). */
export function hariTerakhir(kini, n) { const iso = hariIniIso(kini); const per = {}; ambilPenjualan().forEach((p) => { if (!p.tanggal) return; if (!per[p.tanggal]) per[p.tanggal] = { n: 0, omzet: 0 }; per[p.tanggal].n += 1; per[p.tanggal].omzet += p.hargaTotal || 0; }); const out = []; for (let i = 0; i < (n || 14); i++) { const t = ugTambahHari(iso, -i); out.push({ iso: t, n: per[t] ? per[t].n : 0, omzet: per[t] ? per[t].omzet : 0, hariIni: i === 0 }); } return out; }
/** Teks rekap untuk WhatsApp — kalimat kirimRekapHarianWa sistem lama, ditambah yang dulu tidak disebut (pelunasan bon, prive, margin). */
export function teksRekapHari(R, kop) {
  const b = ['*Rekap ' + ((kop && kop.nama) || IDENTITAS_BAWAAN.nama) + ' — ' + tanggalPendek(R.iso) + '*', 'Omzet: ' + RP(R.omzet) + ' (' + R.n + ' nota)', 'Tunai: ' + RP(R.tunai), 'QRIS: ' + RP(R.qris)];
  if (R.kredit) b.push('Bon (belum jadi uang): ' + RP(R.kredit) + ' · ' + R.nKredit + ' nota'); if (R.pelunasan) b.push('Pembayaran bon pelanggan: ' + RP(R.pelunasan)); if (R.refund) b.push('Refund & tukar retur: ' + RP(R.refund));
  if (R.keluarHarian) b.push('Belanja & biaya toko: ' + RP(R.keluarHarian)); if (R.belanja) b.push('Belanja beras tunai + bongkar: ' + RP(R.belanja)); if (R.bayarBon) b.push('Bayar bon pemasok: ' + RP(R.bayarBon)); if (R.biayaBulanan) b.push('Tagihan bulanan: ' + RP(R.biayaBulanan));
  if (R.prive) b.push('Ambil pribadi owner: ' + RP(R.prive)); if (R.setoran) b.push('Setoran ke owner: ' + RP(R.setoran));
  b.push('Kas bersih hari ini: ' + RP(R.bersih)); b.push('Margin kotor: ' + RP(R.margin) + (R.jumlahTanpaHpp ? ' (' + R.jumlahTanpaHpp + ' baris tanpa modal tidak ikut)' : '')); if (R.tutup) b.push('Sudah tutup hari' + (R.tutup.jam ? ' ' + R.tutup.jam : '')); return b.join('\n');
}

// ==================== BULANAN · enam bulan, inti bulan, DK3 rekap omzet ====================
export function enamBulan(kini) { const akhir = lpKey(hariIniIso(kini)); const out = []; for (let i = 5; i >= 0; i--) { const k = lpGeserBulan(akhir, -i); const L = hitungLabaRentang((t) => !!t && bulanDari(t) === k); out.push({ key: k, pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || i === 5), omzet: L.omzetPenuh, n: L.jumlahTrx, berjalan: k === akhir }); } const maks = Math.max(1, ...out.map((x) => x.omzet)); return { daftar: out, maks }; }
export function intiBulan(key, kini, bayaran) {
  const iso = hariIniIso(kini); const B = bayaran || bayaranBiayaBulanan(); const awal = key + '-01', akhir = akhirBulanIso(key); const L = hitungLabaBersihRentang(awal, akhir, B); const K = hitungArusKasInti((t) => !!t && t >= awal && t <= akhir, B);
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
  for (let i = 11; i >= 0; i--) { const k = lpGeserBulan(akhir, -i); const S = pjOmzetSistem(k); const th = Number(k.slice(0, 4)); if (th === tahunIni) kum += S.omzet; const pb = A.tarifPerMil ? pjBulan(k) : null;
    daftar.push({ key: k, nama: lpNamaBulan(k), pendek: lpBulanPendek(k, k.slice(5, 7) === '01' || i === 11), omzet: S.omzet, n: S.n, final: lpFinal(k), berjalan: i === 0, absen: k < awalBuku, kum: th === tahunIni ? kum : null, lapor: A.lapor[k] || null, perkiraan: pb ? pb.pph : null, perkiraanLengkap: pb ? pb.lengkapSejauhIni : false }); }
  const totalTahun = kum; const pjIni = A.tarifPerMil ? (PJ[tahunIni] || pjTahun(tahunIni, kini)) : null; const adaTarif = A.tarifPerMil > 0, adaBatas = A.batasOmzet > 0; const lewatBatas = adaBatas && totalTahun > A.batasOmzet; const finalTerakhir = daftar.filter((b) => b.final).pop() || null;
  const belumLapor = daftar.filter((b) => b.final && Number(b.key.slice(0, 4)) === tahunIni && !b.lapor); const hariIni = Number(iso.slice(8, 10)); const maks = Math.max(1, ...daftar.map((b) => b.omzet));
  let tempo = null; if (finalTerakhir) { const bulanBerikut = lpGeserBulan(finalTerakhir.key, 1); const lewat = akhir > bulanBerikut || (akhir === bulanBerikut && hariIni > A.tanggalLapor); tempo = { bulan: finalTerakhir, teks: 'lapor ' + lpBulanPendek(finalTerakhir.key) + ' paling lambat ' + A.tanggalLapor + ' ' + lpBulanPendek(bulanBerikut), sudah: !!finalTerakhir.lapor, lewat: !finalTerakhir.lapor && lewat, sisaHari: akhir === bulanBerikut ? A.tanggalLapor - hariIni : null }; }
  return { daftar, maks, tahunIni, totalTahun, adaTarif, adaBatas, lewatBatas, sisaBatas: adaBatas ? A.batasOmzet - totalTahun : null, perkiraanTahun: pjIni ? pjIni.totalPph : null, A, finalTerakhir, belumLapor, tempo, adaFinal: !!finalTerakhir,
    totalTeks: 'Tahun ' + tahunIni + ' sampai ' + lpBulanPendek(akhir) + ' (omzet di sistem saja): ' + RP(totalTahun) + (adaBatas ? (lewatBatas ? ' — LEWAT batas yang diatur owner (' + RP(A.batasOmzet) + ')' : ' — ' + RP(A.batasOmzet - totalTahun) + ' lagi sampai batas yang diatur owner') : ' — batas belum diatur (Atur)') + '. Kumulatif lengkap dengan omzet di luar sistem: Laporan › Pajak',
    tarifTeks: pjIni ? (pjIni.totalPph === null ? 'Perkiraan PPh tidak dihitung (jenis wajib pajak: badan — tanyakan konsultan)' : 'Perkiraan PPh ' + tarifTeks(A.tarifPerMil) + (pjIni.P.batasBebas ? ' sesudah batas bebas ' + RP(pjIni.P.batasBebas) : ' (batas bebas belum diisi)') + ': tahun ini ' + RP(pjIni.totalPph) + (pjIni.kosong ? ' — ' + pjIni.kosong + ' bulan belum diisi, bisa kurang' : '') + ' — ' + PJ_LABEL) : 'Tarif belum diatur → kolom perkiraan tidak dicetak (Atur)' };
}
/** Tandai / batalkan tanda "sudah dilaporkan" satu bulan — hanya bulan FINAL; membatalkan butuh ketukan kedua. */
export function susunTandaLapor(key, w, yakin) {
  const A = aturRekap(); if (!lpFinal(key)) return { tolak: lpNamaBulan(key) + ' belum tutup buku — angkanya masih bisa berubah, jangan dilaporkan dulu' };
  const lapor = Object.assign({}, A.lapor); const sudah = !!lapor[key];
  if (sudah) { if (!yakin) return { tolak: 'Ketuk sekali lagi untuk membatalkan tanda ' + lpNamaBulan(key), perluYakin: true }; delete lapor[key]; }
  else lapor[key] = { tgl: w.tanggal, jam: w.jam };
  return { dokumen: [{ koleksi: 'aturanToko', data: pjGabungRekap({ lapor }, w) }], patch: { yakinBatal: false, kabar: sudah ? 'Tanda dilaporkan ' + lpNamaBulan(key) + ' dibatalkan' : lpNamaBulan(key) + ' ditandai sudah dilaporkan ' + tanggalPendek(w.tanggal), kabarAwas: false } };
}
/** Bukti omzet dari bulan yang dipilih: Σ baris = jumlah (penjaga identitas tergambar); hanya bulan final. */
export function buktiOmzet(pilih, kini) {
  const R = rekapOmzet(kini); const terpilih = R.daftar.filter((b) => pilih && pilih[b.key]); const total = terpilih.reduce((a, b) => a + b.omzet, 0);
  const tolak = !terpilih.length ? 'Pilih bulannya dulu' : terpilih.some((b) => !b.final) ? 'Ada bulan yang belum tutup buku (DRAF) — bukti untuk pajak/bank hanya dari bulan final' : '';
  return { baris: terpilih.map((b) => ({ nama: b.nama, tanda: b.final ? 'final' : 'DRAF', n: b.omzet })), total, n: terpilih.length, tolak, judul: terpilih.length ? terpilih.length + ' bulan · ' + RP(total) : 'Pilih bulannya', cocok: terpilih.reduce((a, b) => a + b.omzet, 0) === total };
}

// ==================== NERACA · dua sisi ====================
export function aturLaporan() { const a = ugAturDok('laporan') || {}; return { asetTetap: isFinite(Number(a.asetTetap)) && Number(a.asetTetap) >= 0 ? Math.round(Number(a.asetTetap)) : 0, asetKet: String(a.asetKet || ''), dariOwner: !!ugAturDok('laporan') }; }
export function susunAturLaporan(isi, w) { const n = ugKosong(isi.asetTetap) ? 0 : ugAngka(isi.asetTetap); if (n < 0) return { tolak: 'Aset tetap tidak boleh minus' }; return { dokumen: [{ koleksi: 'aturanToko', data: { id: 'laporan', tanggal: w.tanggal, jam: w.jam, asetTetap: Math.round(n), asetKet: String(isi.asetKet || '').trim().slice(0, 120) } }], patch: { aturN: null, kabar: 'Aset tetap ' + RP(n) + ' dicatat sebagai isian owner — ikut di neraca sampai modul aset tetap ada', kabarAwas: false } }; }
/**
 * Neraca per tanggal `sampai` (bawaan: sekarang) — hitungNeraca mesin lama (kas · stok · piutang · kasbon · utang pemasok · utang ke owner) + modal owner tertanam
 * (Owner & toko) + aset tetap (isian owner). Laba ditahan = sisa aset sesudah kewajiban & modal (DIHITUNG, disebut begitu); pembandingnya laba bersih kumulatif mesin
 * sejak catatan pertama − ambil pribadi; selisihnya DITULIS sebagai "belum terjelaskan buku" (titik kas, stok awal sebelum sistem), tidak disembunyikan.
 */
export function neracaPada(sampai, kini) {
  const iso = hariIniIso(kini); const s = sampai || null; const N = hitungNeraca(s); const modal = modalTertanam(s); const AT = aturLaporan(); const pertama = lpPertama();
  const kasAda = N.kas !== null; const aset = kasAda ? N.kas + N.stok + N.piutang + N.kasbon + AT.asetTetap : null; const kewajiban = N.utangPemasok + N.utangOwner; const labaDitahan = aset === null ? null : aset - kewajiban - modal;
  let labaKum = null, prive = 0; if (pertama) { labaKum = hitungLabaBersihRentang(pertama, s || iso).labaBersih; ambilPengeluaranHarian().forEach((h) => { if (h.kategori === 'owner' && h.tanggal && (!s || h.tanggal <= s)) prive += Number(h.nominal) || 0; }); }
  const menurutMesin = labaKum === null ? null : labaKum - prive; const selisihBuku = labaDitahan === null || menurutMesin === null ? null : labaDitahan - menurutMesin;
  const harta = [['Kas (laci · brankas · rekening · amplop)', N.kas, kasAda ? '' : 'titik kas belum disetel'], ['Stok beras — karung', N.nilaiSack], ['Stok kemasan jadi', N.nilaiBags], ['Kantong & bahan', N.nilaiBahan], ['Piutang pelanggan (' + N.nPiutang + ' nama)', N.piutang], ['Kasbon pegawai & owner (' + N.nKasbon + ' nama)', N.kasbon]].concat(AT.asetTetap ? [['Aset tetap (isian owner' + (AT.asetKet ? ': ' + AT.asetKet : '') + ')', AT.asetTetap]] : []).map((r) => ({ nama: r[0], n: r[1], ket: r[2] || '' }));
  const pasiva = [['Utang ke pemasok (' + N.nBonPemasok + ' bon)', N.utangPemasok], ['Utang toko ke owner', N.utangOwner], ['Modal owner tertanam', modal], ['Laba ditahan (dihitung: aset − kewajiban − modal)', labaDitahan]].map((r) => ({ nama: r[0], n: r[1], ket: '' }));
  const tolak = !kasAda ? 'Kas belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya' : N.adaStokMinus ? 'Buku menyebut stok MINUS (' + N.sackMinus.concat(N.bagsMinus).slice(0, 3).join(', ') + ') — cocokkan dulu di Stok, neraca tidak dicetak' : '';
  return { sampai: s || iso, N, modal, asetTetap: AT.asetTetap, aset, kewajiban, labaDitahan, labaKum, prive, menurutMesin, selisihBuku, harta, pasiva, total: N.total, tolak, seimbang: aset !== null && Math.round(aset) === Math.round(kewajiban + modal + (labaDitahan || 0)),
    catatan: aset === null ? 'Tanpa titik kas, sisi harta tidak utuh.' : 'Aset ' + RP(aset) + ' = kewajiban ' + RP(kewajiban) + ' + modal ' + RP(modal) + ' + laba ditahan ' + RP(labaDitahan) + '. ' + (menurutMesin === null ? '' : 'Laba bersih kumulatif mesin − ambil pribadi = ' + RP(menurutMesin) + (Math.abs(selisihBuku) > 0.5 ? '; beda ' + RP(selisihBuku) + ' belum terjelaskan buku (titik kas yang pernah disetel ulang, stok awal sebelum sistem).' : '; cocok dengan laba ditahan.')) };
}
/** Banding kekayaan sekarang vs saat titik kas disetel (kalimat tampilkanNeraca sistem lama). */
export function bandingKekayaan(kini) { const t = ambilTitikKas(); const kiniN = hitungNeraca(); if (!t || kiniN.total === null) return { ada: false, titik: t, teks: 'Stok dinilai dengan HPP (harga modal), bukan harga jual — sengaja konservatif.' }; const awal = hitungNeraca(t.tanggal); if (awal.total === null) return { ada: false, titik: t, teks: '' }; const d = kiniN.total - awal.total; return { ada: true, titik: t, awal: awal.total, kini: kiniN.total, selisih: d, teks: 'Saat titik kas ' + tanggalPendek(t.tanggal) + ' kekayaan ' + RP(awal.total) + ' — ' + (d === 0 ? 'belum bergeser.' : 'sejak itu ' + (d > 0 ? 'naik ' : 'turun ') + RP(Math.abs(d)) + '.') + ' Belanja stok tidak menggerakkan angka ini — uangnya cuma berubah wujud; yang menggerakkannya untung dan biaya.' }; }

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
export function riwayatCetakan(n) { return ambilDokumenCetak().slice().sort((a, b) => (Number(b.nomor) || 0) - (Number(a.nomor) || 0)).slice(0, n || 12).map((d) => ({ id: String(d.id), nomor: Number(d.nomor) || 0, teks: (d.cara === 'wa' ? 'WA' : d.cara === 'pdf' ? 'PDF' : 'CETAK') + ' · ' + d.judul + (d.periode ? ' ' + d.periode : '') + (d.draf ? ' (DRAF)' : '') + (d.salinanKe ? ' · salinan ke-' + d.salinanKe : '') + ' · kop v' + (d.kopVersi || 0), tanggal: d.tanggal || '', jam: d.jam || '' })); }

// ==================== DK2 · LAPORAN BERKOP ====================
const lpBarisAK = (K, arah) => K[arah].filter((x) => x.nominal > 0).map((x) => ({ nama: x.label + (x.n ? ' (' + x.n + ' ' + x.satuan + ')' : ''), n: arah === 'masuk' ? x.nominal : -x.nominal, kelas: '' }));
/** Satu laporan berkop untuk rentang bulan berakhir di `keKey`. */
export function laporanBerkop(jenis, keKey, rentang, kini, bayaran) {
  const iso = hariIniIso(kini); const B = bayaran || bayaranBiayaBulanan(); const n = RENTANG_LAPORAN.some((r) => r[0] === rentang) ? rentang : 1; const bulan = []; for (let i = n - 1; i >= 0; i--) bulan.push(lpGeserBulan(keKey, -i));
  const dari = bulan[0] + '-01', sampai = akhirBulanIso(keKey); const final = bulan.every(lpFinal); const periode = bulan.length === 1 ? lpNamaBulan(keKey) : lpBulanPendek(bulan[0], true) + ' – ' + lpBulanPendek(keKey, true); const J = JENIS_LAPORAN.find((j) => j[0] === jenis) || JENIS_LAPORAN[0];
  const I = identitasUsaha(); let baris = [], catatan = '', tolak = '', judul = 'Laporan ' + J[1], sub = periode;
  if (J[0] === 'labarugi') {
    const L = hitungLabaBersihRentang(dari, sampai, B); const mdr = lpMdrRentang(dari, sampai);
    baris = [{ nama: 'Pendapatan', kelas: 'kel' }, { nama: 'Omzet terhitung (nota ber-HPP)', n: L.omzetHitung + L.returUang }].concat(L.returJumlah ? [{ nama: 'Retur & refund (' + L.returJumlah + ')', n: -L.returUang }] : []).concat([{ nama: 'Harga pokok barang terjual (HPP)', n: -(L.hpp + L.returHpp) }]).concat(L.returHpp > 0 ? [{ nama: 'HPP barang yang kembali ke stok', n: L.returHpp }] : [])
      .concat([{ nama: 'Laba kotor', n: L.margin, kelas: 'jumlah' }, { nama: 'Biaya', kelas: 'kel' }, { nama: 'Belanja & biaya toko harian', n: -(L.harianToko - mdr) }, { nama: 'Biaya bulanan — dibagi rata per hari (' + L.nHari + ' hari)', n: -L.jatahBulanan }]).concat(mdr ? [{ nama: 'Potongan QRIS (MDR)', n: -mdr }] : []).concat(L.hapusBuku ? [{ nama: 'Hapus buku piutang', n: -L.hapusBuku }] : []).concat([{ nama: 'Susut & selisih stok', n: L.susutStok }, { nama: 'Laba bersih', n: L.labaBersih, kelas: 'jumlah' }]);
    catatan = 'Laba bersih ' + RP(L.labaBersih) + ' = laba kotor − biaya (upah kotor, termasuk potongan QRIS ' + RP(mdr) + ') − hapus buku ± susut.' + (L.jumlahTanpaHpp ? ' ' + L.jumlahTanpaHpp + ' nota tanpa modal (' + RP(L.omzetTanpaHpp) + ') tidak ikut.' : '');
  } else if (J[0] === 'neraca') {
    const NP = neracaPada(sampai > iso ? iso : sampai, kini); sub = 'per ' + tanggalPendek(NP.sampai) + (bulan.length > 1 ? ' (akhir ' + periode + ')' : '');
    baris = [{ nama: 'Harta', kelas: 'kel' }].concat(NP.harta.map((r) => ({ nama: r.nama, n: r.n }))).concat([{ nama: 'Jumlah harta', n: NP.aset, kelas: 'jumlah' }, { nama: 'Kewajiban & modal', kelas: 'kel' }]).concat(NP.pasiva.map((r) => ({ nama: r.nama, n: r.n }))).concat([{ nama: 'Jumlah kewajiban & modal', n: NP.aset === null ? null : NP.kewajiban + NP.modal + NP.labaDitahan, kelas: 'jumlah' }]);
    catatan = NP.catatan; tolak = NP.tolak;
  } else {
    const K = hitungArusKasInti((t) => !!t && t >= dari && t <= sampai, B); const kasAwal = kasPada(ugTambahHari(dari, -1)); const kasAkhir = kasPada(sampai > iso ? null : sampai); const selisih = kasAwal === null || kasAkhir === null ? null : kasAkhir - (kasAwal + K.bersih);
    baris = [{ nama: 'Kas awal periode' + (kasAwal === null ? ' — sebelum titik kas, belum bisa dihitung' : ''), n: kasAwal }, { nama: 'Masuk', kelas: 'kel' }].concat(lpBarisAK(K, 'masuk')).concat([{ nama: 'Keluar', kelas: 'kel' }]).concat(lpBarisAK(K, 'keluar')).concat([{ nama: 'Kas bersih periode', n: K.bersih, kelas: 'jumlah' }]).concat(selisih !== null && Math.abs(selisih) > 0.5 ? [{ nama: 'Penyesuaian titik kas (disetel ulang dalam periode)', n: selisih }] : []).concat([{ nama: 'Kas akhir periode', n: kasAkhir, kelas: 'jumlah' }]);
    catatan = kasAkhir === null ? 'Kas akhir belum bisa dihitung — titik kas belum disetel.' : 'Kas akhir ' + RP(kasAkhir) + ' = kas di neraca (satu mesin).' + (selisih !== null && Math.abs(selisih) > 0.5 ? ' Penyesuaian ' + RP(selisih) + ' = titik kas yang disetel ulang di dalam periode, bukan uang yang bergerak.' : '');
    if (kasAkhir === null) tolak = 'Kas belum bisa dihitung — titik kas belum disetel';
  }
  if (!tolak && !I.lengkap) tolak = 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)';
  return { jenis: J[0], namaJenis: J[1], judul, sub: sub + ' · ' + (final ? 'FINAL (tutup buku)' : 'DRAF — belum tutup buku'), periode, bulan, dari, sampai, final, cap: final ? '' : 'DRAF', baris: baris.map((r) => ({ nama: r.nama, n: r.n === undefined ? null : r.n, kelas: r.kelas || '', teks: r.n === undefined ? '' : r.n === null ? '—' : RP(r.n) })), catatan, tolak, kop: kopUntuk(pakaiKop().pakai.laporan, I) };
}
/** Paket bank: beberapa laporan jadi satu, hanya dari bulan yang sudah tutup buku; kop butuh nama & alamat. */
export function paketBank(pilih, kini) {
  const R = rekapOmzet(kini); const F = R.finalTerakhir; const isi = [['labarugi', 'Laba-rugi 3 bulan terakhir (final)'], ['neraca', 'Neraca per akhir bulan final terakhir'], ['aruskas', 'Arus kas 3 bulan terakhir'], ['omzet', 'Rekap omzet 12 bulan']].map((p) => ({ id: p[0], nama: p[1] + (F && p[0] === 'neraca' ? ' — ' + F.nama : ''), dipilih: !!(pilih && pilih[p[0]]) }));
  const nPilih = isi.filter((x) => x.dipilih).length; const I = identitasUsaha();
  const tolak = !F ? 'Belum ada bulan yang tutup buku — bank butuh angka FINAL; sampai tutup buku pertama, cetak laporan biasa bercap DRAF' : !nPilih ? 'Pilih isi paketnya' : !I.lengkap ? 'Kop belum lengkap: nama & alamat wajib' : '';
  const daftar = !tolak ? isi.filter((x) => x.dipilih).map((x) => (x.id === 'omzet' ? { jenis: 'omzet', judul: 'Rekap Omzet Bulanan', periode: '12 bulan', R } : laporanBerkop(x.id, F.key, x.id === 'neraca' ? 1 : 3, kini))) : [];
  return { isi, nPilih, F, tolak, daftar, ket: F ? 'Semua dari bulan FINAL (sampai ' + F.nama + '). Bulan berjalan tidak ikut — bank butuh angka yang sudah tutup buku.' + (!I.npwp ? ' NPWP belum ada: paket tetap bisa disusun, barisnya kosong.' : '') : 'Belum pernah tutup buku — belum ada bulan final.' };
}
/** Banding laba-rugi dua bulan. */
export function bandingLabaRugi(a, b, kini, bayaran) {
  const B = bayaran || bayaranBiayaBulanan(); const satu = (k) => { const L = hitungLabaBersihRentang(k + '-01', akhirBulanIso(k), B); return { omzet: L.omzetHitung, hpp: L.hpp, kotor: L.margin, biaya: L.biayaToko + L.hapusBuku - L.susutStok, bersih: L.labaBersih }; }; const A1 = satu(a), A2 = satu(b);
  return { judul: lpNamaBulan(a) + ' vs ' + lpNamaBulan(b), baris: [['Omzet terhitung', 'omzet'], ['HPP', 'hpp'], ['Laba kotor', 'kotor'], ['Biaya, hapus buku & susut', 'biaya'], ['Laba bersih', 'bersih']].map((r) => { const d = A1[r[1]] - A2[r[1]]; const pct = A2[r[1]] ? Math.round(d / Math.abs(A2[r[1]]) * 100) : null; return { nama: r[0], a: A1[r[1]], b: A2[r[1]], d, pct, arah: d > 0 ? 'naik' : d < 0 ? 'turun' : '', teksD: (d >= 0 ? '+' : '−') + RP(Math.abs(d)).replace('Rp', '') + (pct === null ? '' : ' (' + (pct >= 0 ? '+' : '') + pct + '%)') }; }) };
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
  let judul = J.nama, sub = '', baris = [], identitas = '', tolak = '', cap = '', pilihan = [], ragam = 'ringkas', trxId = null, salinan = null, cocokN = null, teksTambahan = '';
  const brs = (nama, n, saldo, kelas) => ({ nama, n: n === '' || n === undefined ? null : n, saldo: saldo === undefined ? null : saldo, kelas: kelas || '', teks: n === '' || n === undefined ? '' : RP(n), teksSaldo: saldo === undefined || saldo === null ? '' : RP(saldo) });
  if (J.id === 'setor') { ragam = P.setor; const rows = bukuOwner(300).filter((r) => r.ubah === 'modal' && r.arah === 1 || r.judul === 'Pinjaman owner ke toko'); pilihan = rows.map((r) => ({ id: r.id, nama: tanggalPendek(r.tanggal) + ' · ' + r.judul, n: r.n })); const S1 = rows.find((r) => r.id === String(pilih)) || rows[0] || null;
    if (S1) { sub = tanggalPendek(S1.tanggal) + (S1.jam ? ' ' + S1.jam : '') + ' · ' + S1.judul; baris = [brs(S1.judul === 'Pinjaman owner ke toko' ? 'Pinjaman owner ke toko (bukan modal)' : 'Setoran modal dari owner', S1.n)].concat(S1.ket ? [brs('Keterangan: ' + S1.ket, '')] : []).concat([brs('Jumlah', S1.n, undefined, 'jumlah')]); identitas = 'Angka dari catatan Owner & toko — tidak diketik ulang'; } else { sub = 'belum ada setoran modal tercatat'; tolak = 'Belum ada catatan setoran modal (Uang → Owner & toko)'; } }
  if (J.id === 'upah') { ragam = P.slip; const rows = riwayatUpah('', 60); pilihan = rows.map((r) => ({ id: r.id, nama: r.nama + ' · ' + tanggalPendek(String(r.tanggal).slice(0, 10)) + (r.jenis === 'lamaBelum' ? ' · BELUM dibayar' : ''), n: r.n })); const U = rows.find((r) => r.id === String(pilih)) || rows[0] || null;
    if (U) { sub = U.nama + ' · ' + U.ket; if (U.teks) { baris = U.teks.split('\n').slice(3).filter((x) => x.trim()).map((x) => { const m = x.match(/^(.*?)\s{2,}(−?Rp[\d.]+)$/); return m ? brs(m[1].trim(), Number(m[2].replace(/[^\d−-]/g, '').replace('−', '-')), undefined, /^DITERIMA/.test(m[1]) ? 'jumlah' : '') : brs(x.trim(), ''); }); identitas = 'Dari slip yang tersimpan saat upah dibayar (Uang → Orang & upah) — tarif × hari, dikurangi kasbon'; }
      else { baris = [brs('Gaji bulan ' + String(U.id).split('|')[1] + ' (buku bulanan sistem lama)', U.n), brs('Diterima', U.n, undefined, 'jumlah')]; identitas = 'Baris gaji dari buku bulanan sistem lama — tarif & hari per hari tidak tercatat, jadi tidak dirinci'; if (U.jenis === 'lamaBelum') tolak = 'Gaji ini belum dibayar — slip baru ada sesudah dibayar'; } } else { sub = 'belum ada pembayaran upah'; tolak = 'Belum ada upah yang dibayar'; } }
  if (J.id === 'piutang') { ragam = P.kartu; const semua = hitungPiutang().filter((d) => d.mutasi && d.mutasi.length); const bon = semuaBon(kini); const sisaDari = {}; bon.forEach((b) => { sisaDari[b.kunci] = b.sisa; }); semua.sort((a, b) => (sisaDari[b.kunci] || 0) - (sisaDari[a.kunci] || 0) || a.nama.localeCompare(b.nama)); pilihan = semua.map((d) => ({ id: d.kunci, nama: d.nama, n: sisaDari[d.kunci] || 0, ket: 'sisa' })); const D = semua.find((d) => d.kunci === pilih) || semua[0] || null;
    if (D) { judul = 'Kartu Piutang'; sub = D.nama + ' · sampai ' + tanggalPendek(iso); let sd = 0, tambah = 0, bayar = 0, hapus = 0; const mut = D.mutasi.slice().sort((a, b) => String(a.tanggal + (a.jam || '')).localeCompare(String(b.tanggal + (b.jam || ''))));
      baris = mut.map((m) => { const n = Number(m.nominal) || 0; const masuk = m.jenis === 'jual' || m.jenis === 'saldoAwal'; if (masuk) tambah += n; else if (m.jenis === 'hapusBuku') hapus += n; else bayar += n; sd += masuk ? n : -n; return brs(tanggalPendek(m.tanggal) + ' · ' + (m.jenis === 'jual' ? 'bon' : m.jenis === 'saldoAwal' ? 'bon lama' : m.jenis === 'hapusBuku' ? 'dihapus dari buku' : 'bayar') + (m.ket && m.jenis !== 'bayar' ? ' · ' + String(m.ket).slice(0, 40) : ''), masuk ? n : -n, sd); });
      baris.push(brs('Sisa bon', sd, undefined, 'jumlah')); identitas = 'Sisa ' + RP(sd) + ' = bon ' + RP(tambah) + ' − bayar ' + RP(bayar) + (hapus ? ' − dihapus ' + RP(hapus) : ''); if (Math.abs(sd - (D.sisa || 0)) > 0.5) tolak = 'Saldo kartu ' + RP(sd) + ' ≠ sisa menurut mesin ' + RP(D.sisa) + ' — tidak dicetak sampai ketemu sebabnya'; } else { sub = 'belum ada pelanggan berbon'; tolak = 'Belum ada catatan bon pelanggan'; } }
  if (J.id === 'bon') { ragam = P.bon; const UP = {}; hitungUtangPemasok().forEach((u) => { UP[kunciPelanggan(u.pemasok)] = u; }); const pem = daftarPemasok().map((p) => Object.assign({}, p, { totalUtang: UP[p.kunci] ? UP[p.kunci].totalUtang || 0 : 0, tekor: UP[p.kunci] ? UP[p.kunci].tekor || 0 : 0 })).sort((a, b) => b.totalUtang - a.totalUtang || a.nama.localeCompare(b.nama)); pilihan = pem.map((p) => ({ id: p.kunci, nama: p.nama, n: p.totalUtang, ket: 'sisa' })); const M = pem.find((p) => p.kunci === pilih) || pem[0] || null;
    if (M) { judul = 'Rekap Bon Pemasok'; sub = M.nama + ' · sampai ' + tanggalPendek(iso); const BB = bukuBon(M.nama); let total = 0, bayar = 0; baris = BB.baris.map((e) => { if (e.n > 0) total += e.n; else bayar += -e.n; return brs((e.t ? tanggalPendek(e.t) + ' · ' : '') + e.teks + (e.ket ? ' · ' + String(e.ket).slice(0, 40) : ''), e.n, e.saldo); }); baris.push(brs('Sisa utang ke ' + M.nama, BB.saldo, undefined, 'jumlah')); identitas = 'Sisa ' + RP(BB.saldo) + ' = bon ' + RP(total) + ' − dibayar ' + RP(bayar); if (Math.abs(BB.saldo - M.totalUtang) > 0.5) identitas += ' · mesin utang pemasok menyebut ' + RP(M.totalUtang) + (M.tekor ? ' (kelebihan bayar ' + RP(M.tekor) + ')' : ''); } else { sub = 'belum ada pemasok'; tolak = 'Belum ada catatan pemasok'; } }
  if (J.id === 'nota') { ragam = P.nota; const DN = daftarNota(cari, kini, 40); cocokN = DN.cocok; pilihan = DN.daftar.map((x) => ({ id: x.kunci, nama: tanggalPendek(x.tanggal) + ' ' + x.jam + ' · ' + x.nama + ' · ' + x.isi + (x.batal ? ' · DIBATALKAN' : x.salinan ? ' · salinan ' + x.salinan + '×' : ''), n: x.total })); const X = DN.daftar.find((x) => x.kunci === pilih) || null;
    if (X) { const N = notaDari(X.kunci.indexOf('t:') === 0 ? { trxId: X.trxId } : X.kunci.indexOf('g:') === 0 ? { grupNota: X.trxId } : { id: X.id }); const S = N ? susunStruk(N, stAtur()) : null; trxId = X.trxId; salinan = salinanKe(trxId); judul = 'Nota'; sub = tanggalPendek(X.tanggal) + ' ' + X.jam + ' · ' + X.nama + ' · ' + X.cara;
      baris = S ? S.garis.filter((g) => !g.garis && g.kanan).map((g) => brs(g.kiri, g.kanan.replace(/[^\d−-]/g, '') ? Number(g.kanan.replace(/[^\d−-]/g, '').replace('−', '-')) : '', undefined, /^TOTAL/i.test(g.kiri) ? 'jumlah' : '')) : [brs(X.isi, X.total, undefined, 'jumlah')]; teksTambahan = S ? S.teks : '';
      cap = X.batal ? 'DIBATALKAN' : 'SALINAN ke-' + salinan; identitas = X.batal ? 'Nota ini dibatalkan — tidak dicetak ulang' : 'Cetak ulang ke-' + salinan + ' · nota asli ' + tanggalPendek(X.tanggal) + ' ' + X.jam + ' · angka dari nota yang tersimpan'; if (X.batal) tolak = 'Nota dibatalkan tidak dicetak ulang'; } else { sub = cocokN + ' nota cocok — ketuk salah satu'; tolak = 'Pilih notanya'; } }
  if (!tolak && !I.lengkap) tolak = 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)';
  return { jenis: J.id, namaJenis: J.nama, judul, sub, baris, identitas, cap, tolak, pilihan, ragam, kop: kopUntuk(ragam, I), trxId, salinanKe: salinan, cocokN, teksTambahan, adaSaldo: baris.some((b) => b.saldo !== null) };
}
/** Wujud teks satu dokumen (untuk WhatsApp / pratinjau): kop, judul, baris, catatan, nomor. */
export function teksDokumen(D, nomor, iso) {
  const k = D.kop; const L = [k.nama.toUpperCase()]; if (k.alamat) L.push(k.alamat); if (k.resmi) L.push(k.resmi); L.push('', (D.judul || '').toUpperCase() + (D.cap ? ' — ' + D.cap : ''), D.sub || '', '');
  (D.baris || []).forEach((b) => { if (b.kelas === 'kel') L.push(b.nama.toUpperCase()); else L.push((b.kelas === 'jumlah' ? '' : '  ') + b.nama + (b.teks ? '  ' + b.teks : '') + (b.teksSaldo ? '  (saldo ' + b.teksSaldo + ')' : '')); });
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
  const L = hitungLabaBersihRentang(awal, akhir, B); const K = hitungArusKasInti(cocok, B); const Lr = hitungLabaRentang(cocok);
  const hari = []; for (let i = 0; i < 7; i++) { const t = ugTambahHari(awal, i); const Lh = hitungLabaRentang((x) => x === t); hari.push({ iso: t, nama: LP_HARI[i], tgl: String(parseInt(t.slice(8, 10), 10)), omzet: Lh.omzetPenuh, n: Lh.jumlahTrx, margin: Lh.margin, depan: t > iso, hariIni: t === iso }); }
  const jalan = hari.filter((h) => !h.depan); const omzet = hari.reduce((a, h) => a + h.omzet, 0); const n = hari.reduce((a, h) => a + h.n, 0); const maks = Math.max(1, ...hari.map((h) => h.omzet));
  const lalu = hitungLabaRentang((t) => !!t && t >= ugTambahHari(awal, -7) && t <= ugTambahHari(awal, -1)); const pct = lpPersen(omzet, lalu.omzetPenuh);
  const isi = jalan.filter((h) => h.n > 0); const terbaik = isi.length ? isi.reduce((a, h) => (h.omzet > a.omzet ? h : a)) : null; const sepi = isi.length ? isi.reduce((a, h) => (h.omzet < a.omzet ? h : a)) : null;
  return { awal, akhir, label: tanggalPendek(awal) + ' – ' + tanggalPendek(akhir), berjalan: akhir >= iso, hariJalan: jalan.length, hari, omzet, n, maks, rataHari: jalan.length ? Math.round(omzet / jalan.length) : 0, cocokJumlah: omzet === Lr.omzetPenuh,
    hpp: L.hpp, margin: L.margin, biayaToko: L.biayaToko, labaBersih: L.labaBersih, susut: L.susutStok, omzetTanpaHpp: L.omzetTanpaHpp, jumlahTanpaHpp: L.jumlahTanpaHpp, masuk: K.totalMasuk, keluar: K.totalKeluar, bersih: K.bersih, kredit: K.kreditBulanIni,
    lalu: lalu.omzetPenuh, pct, bandingTeks: lpBandingTeks(pct, 'minggu sebelumnya') + (lalu.omzetPenuh ? ' (' + RP(lalu.omzetPenuh) + ')' : ''), terbaik, sepi, kosong: n === 0 && K.totalMasuk === 0 && K.totalKeluar === 0 };
}

// ==================== TAHUNAN · dua belas bulan (owner 23 Sep) ====================
/** Tahun-tahun yang punya catatan, terbaru dulu. */
export function daftarTahun(kini) { const th = Number(hariIniIso(kini).slice(0, 4)); const p = lpPertama(); const awal = p ? Number(p.slice(0, 4)) : th; const out = []; for (let y = th; y >= awal; y--) out.push({ tahun: y, berjalan: y === th, final: lpFinal(y + '-01') }); return out; }
/** Rekap satu tahun: 12 bulan (omzet, nota, margin, biaya, laba bersih) dari mesin yang sama; jumlah tahun = Σ bulan; banding tahun sebelumnya; bulan terbaik & tersepi. */
export function rekapTahun(tahun, kini, bayaran) {
  const iso = hariIniIso(kini); const B = bayaran || bayaranBiayaBulanan(); const kiniKey = iso.slice(0, 7); const bulan = [];
  for (let m = 1; m <= 12; m++) { const key = tahun + '-' + String(m).padStart(2, '0'); const depan = key > kiniKey;
    if (depan) { bulan.push({ key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key), depan: true, berjalan: false, final: false, omzet: 0, n: 0, margin: 0, biaya: 0, labaBersih: 0, susut: 0 }); continue; }
    const L = hitungLabaBersihRentang(key + '-01', akhirBulanIso(key), B); const Lr = hitungLabaRentang((t) => !!t && bulanDari(t) === key);
    bulan.push({ key, nama: lpNamaBulan(key), pendek: lpBulanPendek(key), depan: false, berjalan: key === kiniKey, final: lpFinal(key), omzet: Lr.omzetPenuh, n: Lr.jumlahTrx, margin: L.margin, biaya: L.biayaToko, labaBersih: L.labaBersih, susut: L.susutStok, hpp: L.hpp }); }
  const ada = bulan.filter((b) => !b.depan); const jml = (k) => ada.reduce((a, b) => a + (b[k] || 0), 0); const omzet = jml('omzet'); const n = jml('n');
  const Lt = hitungLabaRentang((t) => !!t && String(t).slice(0, 4) === String(tahun)); const maks = Math.max(1, ...bulan.map((b) => b.omzet));
  const laluL = hitungLabaRentang((t) => !!t && String(t).slice(0, 4) === String(tahun - 1)); const pct = lpPersen(omzet, laluL.omzetPenuh);
  const isi = ada.filter((b) => b.n > 0); const terbaik = isi.length ? isi.reduce((a, b) => (b.omzet > a.omzet ? b : a)) : null; const sepi = isi.length ? isi.reduce((a, b) => (b.omzet < a.omzet ? b : a)) : null;
  const bulanJalan = ada.filter((b) => b.n > 0 || b.berjalan).length; const final = lpFinal(tahun + '-01');
  return { tahun, bulan, ada: ada.length, bulanJalan, omzet, n, cocokJumlah: omzet === Lt.omzetPenuh, hpp: jml('hpp'), margin: jml('margin'), biaya: jml('biaya'), labaBersih: jml('labaBersih'), susut: jml('susut'), maks,
    rataBulan: bulanJalan ? Math.round(omzet / bulanJalan) : 0, lalu: laluL.omzetPenuh, pct, bandingTeks: lpBandingTeks(pct, 'tahun ' + (tahun - 1)) + (laluL.omzetPenuh ? ' (' + RP(laluL.omzetPenuh) + ')' : ''), terbaik, sepi, final, berjalan: String(tahun) === iso.slice(0, 4),
    status: final ? 'FINAL — sudah tutup buku' : String(tahun) === iso.slice(0, 4) ? 'DRAF — tahun berjalan, sampai ' + tanggalPendek(iso) : 'DRAF — belum tutup buku', kosong: n === 0 };
}
