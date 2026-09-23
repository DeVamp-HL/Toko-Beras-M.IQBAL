#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_laporan_baru.py — uji logika layar LAPORAN & DOKUMEN sistem baru (laporan-logika: Laba · Harian · Bulanan/rekap omzet · Neraca · DK1 kop · DK2 laporan berkop · DK4 dokumen kecil · cetakan bernomor) di jsc.
KOTAK PASIR (ANGKA CONTOH, bukan angka toko), jam dikunci 19 Sep 2026 10:00 WIB.
Identitas yang dijaga: setiap angka layar = mesin beku yang sama (hitungLabaBersihRentang / hitungArusKasInti / hitungNeraca / kasPada); baris dokumen menutup ke jumlahnya;
bulan belum tutup buku = DRAF; nomor cetakan urut; salinan nota ke-N naik tiap cetak ulang.

    python3 alat-uji/uji_laporan_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_laporan_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/uang-logika.js', 'baru/js/layar/upah-logika.js', 'baru/js/layar/owner-toko-logika.js', 'baru/js/layar/tutup-hari-logika.js', 'baru/js/layar/tutup-buku-logika.js',
                                  'baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/laporan-logika.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, jam, cara, merk, kg, harga, hpp, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'caraBayar': cara, 'jenis': 'karung', 'merkSumber': merk, 'totalKg': kg, 'beratKarungAcuan': 50, 'jumlahKarung': kg / 50, 'hargaTotal': harga, 'hppTotalSaatJual': hpp, 'trxId': 't' + str(id)[1:]}
    d.update(k); return d


# ---- ANGKA CONTOH. Titik kas 15 Sep: laci 2.000.000 · brankas 10.000.000 · rekening 3.000.000 · amplop 1.000.000.
#      Sep: j1 16 Sep tunai 500.000 · j2 17 Sep QRIS 700.000 · j3 19 Sep QRIS 600.000 · j4 19 Sep tunai 250.000 · j5 19 Sep BON 300.000 (Bu Contoh) · j6 batal · j7 19 Sep tunai 120.000 RUGI (modal 140.000) · j8 18 Sep tunai 80.000 TANPA modal.
#      Omzet Sep terhitung 2.470.000 · HPP 2.323.700 · margin kotor 146.300 · margin nota bon 21.800. Potongan QRIS 19 Sep 1.800 (biaya toko bertanda mdr).
KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'RODA CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 0,
                  'merkList': [{'id': 'b10', 'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'hargaPerKg': 13000, 'subtotalHarga': 13000000},
                               {'id': 'b11', 'merk': 'IR64 Apex', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'hargaPerKg': 14000, 'subtotalHarga': 7000000}]}],
  'penjualan': [jual('a1', '2026-08-25', '09:00', 'Tunai', 'Angsa', 50, 700000, 650000),
                jual('j1', '2026-09-16', '09:00', 'Tunai', 'Angsa', 35.7, 500000, 464100), jual('j2', '2026-09-17', '10:00', 'QRIS', 'Angsa', 50, 700000, 650000),
                jual('j3', '2026-09-19', '09:12', 'QRIS', 'IR64 Apex', 40, 600000, 560000), jual('j4', '2026-09-19', '09:40', 'Tunai', 'Angsa', 17.8, 250000, 231400),
                jual('j5', '2026-09-19', '09:50', 'Kredit', 'Angsa', 21.4, 300000, 278200, namaPelanggan='Bu Contoh'),
                jual('j6', '2026-09-19', '09:55', 'Tunai', 'Angsa', 0, 0, 0) | {'dibatalkan': True},
                jual('j7', '2026-09-19', '10:05', 'Tunai', 'IR64 Apex', 10, 120000, 140000), jual('j8', '2026-09-18', '15:00', 'Tunai', 'Angsa', 5, 80000, 0)],
  'pengeluaranHarian': [{'id': 'h1', 'kategori': 'toko', 'tanggal': '2026-09-16', 'jam': '09:15', 'keterangan': 'Bensin antar', 'nominal': 20000},
                        {'id': 'h2', 'kategori': 'owner', 'tanggal': '2026-09-17', 'jam': '11:02', 'keterangan': 'Belanja dapur', 'nominal': 100000},
                        {'id': 'mdr-2026-09-19', 'kategori': 'toko', 'tanggal': '2026-09-19', 'jam': '09:13', 'keterangan': 'Potongan QRIS', 'nominal': 1800, 'mdr': True, 'dari': 'rekening'},
                        {'id': 'h4', 'kategori': 'tokoDompet', 'tanggal': '2026-09-11', 'jam': '14:00', 'keterangan': 'Beli lakban', 'nominal': 120000},
                        {'id': 'h5', 'kategori': 'toko', 'tanggal': '2026-08-25', 'jam': '08:00', 'keterangan': 'Bensin antar', 'nominal': 30000}],
  'biayaBulanan': [{'id': '2026-08', 'bulan': '2026-08', 'listrik': 350000, 'internet': 250000, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-08-10', 'internet': '2026-08-05', 'gaji': '2026-08-31'},
                    'rincianGaji': [{'nama': 'Ben Mohsein', 'hari': 26, 'gaji': 1560000}, {'nama': 'Gono', 'hari': 10, 'gaji': 600000}], 'tanggalBayarGaji': {'Ben Mohsein': '2026-08-31', 'Gono': '2026-08-31'}, 'gaji': 2160000, 'gajiHariOrang': 36},
                   {'id': '2026-09', 'bulan': '2026-09', 'listrik': 350000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {}, 'rincianGaji': [], 'gaji': 0, 'gajiHariOrang': 0}],
  'kasbonMutasi': [{'id': 701, 'tipe': 'ambil', 'namaPegawai': 'Ben Mohsein', 'nominal': 200000, 'tanggal': '2026-09-05', 'catatan': 'Keperluan keluarga'}],
  'piutangMutasi': [{'id': 801, 'tipe': 'bayar', 'namaPelanggan': 'Bu Contoh', 'nominal': 100000, 'tanggal': '2026-09-19', 'jam': '09:58', 'caraBayar': 'Tunai'}],
  'utangPemasokMutasi': [{'id': 901, 'tipe': 'bayar', 'pemasok': 'RODA CONTOH', 'nominal': 5000000, 'tanggal': '2026-09-10', 'jam': '10:00', 'bonTanggal': '2026-08-20', 'dari': 'rekening'}],
  'modalOwner': [{'id': 'm1', 'tanggal': '2026-08-08', 'jam': '08:00', 'tipe': 'setor', 'nominal': 25000000, 'catatan': 'Tabungan pribadi'}],
  'amplopLaba': [{'id': 'am-2026-09-16', 'tanggal': '2026-09-16', 'jam': '21:00', 'tipe': 'setor', 'nominal': 50000, 'catatan': 'Sisihan tutup hari'}],
  'penyesuaianStok': [{'id': 's1', 'tanggal': '2026-09-12', 'jam': '20:00', 'merk': 'Angsa', 'selisihKg': -2, 'nilaiRp': -26000, 'alasan': 'tercecer'}],
  'tutupHari': [{'id': 'th-16', 'tanggal': '2026-09-16', 'jam': '21:05', 'selisihLaci': 0}],
  'retur': [], 'karantina': [], 'stokBahanKemasan': [], 'stokBahanLiteran': [], 'katalogHargaLiteran': [], 'katalogHargaKemasan': [], 'katalogHargaKarung': [], 'produksiKemasan': [], 'pesanan': [], 'setoranKas': [], 'penyesuaianKemasan': [],
  'utangOwnerMutasi': [], 'tembusanStok': [], 'pelangganCatatan': [], 'pemasokCatatan': [], 'thrPelanggan': [], 'slipUpah': [], 'absenKaryawan': [], 'pindahUang': [], 'tutupBukuAcara': [], 'perangkatStatus': [], 'persetujuan': [], 'pengaturan': [],
  'aturanToko': [], 'dokumenCetak': [], 'tagihPelanggan': [], 'strukKeluar': [], 'wadahLiteran': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var tulis = function (r) { if (r.tolak) throw new Error('DITOLAK: ' + r.tolak); if (r.dokumen) terapkanKeCache(r.dokumen); return r; };
var dekat = function (a, b) { return Math.abs(a - b) < 0.5; };

// ==================== BERSAMA ====================
ok('catatan pertama 8 Aug? tidak — batch 20 Agu & nota 25 Agu: pertama = 2026-08-20; daftar bulan Sep, Agu (2), terbaru dulu, semua belum tutup buku', lpPertama() === '2026-08-20' && daftarBulan(KINI).length === 2 && daftarBulan(KINI)[0].key === '2026-09' && daftarBulan(KINI).every(function (b) { return !b.final; }), J(daftarBulan(KINI)));
ok('tanpa tutup buku: tidak ada bulan final', !lpFinal('2026-08') && !lpFinal('2025-12'));

// ==================== LABA · tiga angka ====================
var LB = labaBulan('2026-09', KINI); var LM = hitungLabaBersihRentang('2026-09-01', '2026-09-30');
ok('Sep: omzet terhitung 2.470.000 · HPP 2.323.700 · margin kotor 146.300 = mesin; laba bersih = hitungLabaBersihRentang (satu mesin)', LB.L.omzetHitung === 2470000 && LB.L.hpp === 2323700 && LB.margin === 146300 && LB.labaBersih === LM.labaBersih, J([LB.margin, LB.labaBersih, LM.labaBersih]));
ok('diterima tunai = laba bersih − margin nota bon 21.800 (1 nota bon, pokok 300.000)', LB.marginKredit === 21800 && LB.nKredit === 1 && LB.omzetKredit === 300000 && LB.tunai === LB.labaBersih - 21800);
ok('cakupan = omzet ber-HPP ÷ (ber-HPP + tanpa HPP 80.000) = 2.470.000/2.550.000; 1 nota tanpa modal disebut', LB.penyebut === 2550000 && dekat(LB.cakupan * 1000, 968.6) && LB.tanpaHpp.length === 1 && LB.tanpaHpp[0].id === 'j8' && LB.omzetTanpaHpp === 80000, J([LB.cakupan, LB.tanpaHpp]));
ok('potongan QRIS 1.800 dipisah dari biaya toko; biaya lain = biayaToko − 1.800; terjun menutup: Σ baris (tanpa baris jumlah) = laba bersih', LB.mdr === 1800 && LB.biayaLain === LB.L.biayaToko - 1800 && dekat(LB.terjun.filter(function (r) { return r.kelas !== 'jumlah'; }).reduce(function (a, r) { return a + r.n; }, 0), LB.labaBersih), J(LB.terjun));
ok('nota rugi: j7 dijual 120.000 modal 140.000 → −20.000; susut Sep 1 baris −26.000 = L.susutStok', LB.rugi.length === 1 && LB.rugi[0].id === 'j7' && LB.rugi[0].margin === -20000 && LB.susut.length === 1 && LB.susutTotal === -26000 && LB.L.susutStok === -26000);
ok('bulan berjalan: aman diambil = batas aman (laba bulan berjalan, owner belum menyetel) − prive 100.000', LB.berjalan && LB.aman && LB.aman.dariLaba && LB.aman.terpakai === 100000 && LB.aman.sisa === LB.aman.batas - 100000, J(LB.aman));
var LB7 = labaBulan('2026-07', KINI); ok('Juli tanpa satu catatan pun → tanpaCatatan (beda dari bulan yang untungnya nol); Agu: margin 50.000, bukan tanpaCatatan', LB7.tanpaCatatan && LB7.margin === 0 && !labaBulan('2026-08', KINI).tanpaCatatan && labaBulan('2026-08', KINI).margin === 50000);

// ==================== HARIAN ====================
var RH = rekapHari('2026-09-19');
ok('19 Sep: 4 nota (batal tidak ikut) · omzet 1.270.000 · tunai 370.000 · QRIS 600.000 · bon 300.000 · pembayaran bon 100.000 · keluar 1.800 (MDR) · kas bersih 1.068.200', RH.n === 4 && RH.omzet === 1270000 && RH.tunai === 370000 && RH.qris === 600000 && RH.kredit === 300000 && RH.pelunasan === 100000 && RH.keluarHarian === 1800 && RH.bersih === 1068200, J(RH));
ok('kas bersih = Σ masuk − Σ keluar (baris arus kas yang sama); per jam: jam 09 tiga nota, jam 10 satu', dekat(RH.masuk.reduce(function (a, x) { return a + x.nominal; }, 0) - RH.keluar.reduce(function (a, x) { return a + x.nominal; }, 0), RH.bersih) && RH.perJam.length === 2 && RH.perJam[0].jam === '09' && RH.perJam[0].n === 3 && RH.perJam[1].n === 1, J(RH.perJam));
ok('buku kas 19 Sep = baris daftarGerakanKas hari itu (5: 3 nota uang + pelunasan + MDR); 16 Sep sudah tutup hari 21:05, 19 Sep belum', RH.buku.length === daftarGerakanKas().filter(function (r) { return r.t === '2026-09-19'; }).length && RH.buku.length === 5 && !RH.tutup && rekapHari('2026-09-16').tutup.jam === '21:05', J(RH.buku.map(function (r) { return r.label; })));
var TR = teksRekapHari(RH, { nama: 'Toko Contoh' }); ok('teks WA: judul toko, omzet (4 nota), tunai, QRIS, bon, pembayaran bon, kas bersih, margin', /Rekap Toko Contoh — 19 Sep/.test(TR) && /Omzet: Rp1\.270\.000 \(4 nota\)/.test(TR) && /Bon \(belum jadi uang\): Rp300\.000/.test(TR) && /Pembayaran bon pelanggan: Rp100\.000/.test(TR) && /Kas bersih hari ini: Rp1\.068\.200/.test(TR) && /Margin kotor/.test(TR), TR);
var HT = hariTerakhir(KINI, 14); ok('14 hari terakhir, hari ini dulu; 19 Sep 4 nota, 18 Sep 1, 15 Sep 0 (sepi tetap ada)', HT.length === 14 && HT[0].iso === '2026-09-19' && HT[0].hariIni && HT[0].n === 4 && HT[1].n === 1 && HT[4].n === 0);

// ==================== BULANAN · enam bulan · inti · rekap omzet ====================
var E6 = enamBulan(KINI); ok('enam bulan Apr–Sep urut, Sep berjalan omzet 2.550.000 (semua nota, termasuk tanpa modal), Agu 700.000', E6.daftar.length === 6 && E6.daftar[0].key === '2026-04' && E6.daftar[5].key === '2026-09' && E6.daftar[5].berjalan && E6.daftar[5].omzet === 2550000 && E6.daftar[4].omzet === 700000 && E6.maks === 2550000);
var IB = intiBulan('2026-09', KINI); ok('inti Sep: 19 hari jalan, rata 134.210/hari, laba bersih = mesin, tagihan Sep belum dibayar: listrik 350.000', IB.hariJalan === 19 && IB.rataHari === Math.round(2550000 / 19) && IB.labaBersih === LM.labaBersih && IB.belumBayar.length === 1 && IB.belumBayar[0].label === 'Listrik' && IB.belumBayarTotal === 350000, J(IB));
var RO = rekapOmzet(KINI);
ok('rekap 12 bulan Okt 25 – Sep 26; kumulatif tahun 2026 = 700.000 (Agu) → 3.250.000 (Sep); bulan 2025 kum null; tarif & batas belum diatur → perkiraan null', RO.daftar.length === 12 && RO.daftar[0].key === '2025-10' && RO.daftar[11].key === '2026-09' && RO.daftar[10].kum === 700000 && RO.daftar[11].kum === 3250000 && RO.daftar[0].kum === null && RO.totalTahun === 3250000 && !RO.adaTarif && RO.daftar[11].perkiraan === null && !RO.adaFinal && !RO.tempo, J(RO.daftar.map(function (b) { return [b.key, b.omzet, b.kum]; })));
ok('atur rekap: tarif 1001 ditolak; tanggal 30 ditolak; batas minus ditolak', /per seribu/.test(susunAturRekap({ tarifPerMil: '1001' }, W).tolak) && /1–28/.test(susunAturRekap({ tanggalLapor: '30' }, W).tolak) && /minus/.test(susunAturRekap({ batasOmzet: '-1' }, W).tolak));
tulis(susunAturRekap({ tarifPerMil: '5', batasOmzet: '1.000.000', tanggalLapor: '20' }, W)); RO = rekapOmzet(KINI);
ok('sesudah atur: perkiraan Sep = 2.550.000 × 5‰ = 12.750; LEWAT batas 1.000.000; teks menyebut "bukan nasihat pajak" & LEWAT', RO.adaTarif && RO.daftar[11].perkiraan === 12750 && RO.lewatBatas && /bukan nasihat pajak/.test(RO.tarifTeks) && /LEWAT batas/.test(RO.totalTeks), RO.totalTeks);
ok('paket bank sebelum tutup buku pertama DITOLAK (bank butuh angka final; laporan biasa bercap DRAF)', /Belum ada bulan yang tutup buku/.test(paketBank({ omzet: true }, KINI).tolak));
ok('tanda dilaporkan pada bulan belum tutup buku DITOLAK; bukti dari bulan draf DITOLAK; bukti tanpa pilihan ditolak', /belum tutup buku/.test(susunTandaLapor('2026-08', W).tolak) && /DRAF/.test(buktiOmzet({ '2026-08': true }, KINI).tolak) && /Pilih/.test(buktiOmzet({}, KINI).tolak));
// tutup buku 2025 (era) → bulan 2025 FINAL
pasok('batchMasuk', ambilSemuaBatch().concat([{ id: 'tb-2025', tanggal: '2025-12-31', pemasok: 'TUTUP BUKU 2025', tutupBuku: true, tahunDari: 2025, merkList: [], stokAwal: false }]));
ok('sesudah tutup buku 2025: Des 2025 final, Jan 2026 draf; rekap punya bulan final terakhir Des 2025; tempo lapor "20 Jan" LEWAT', lpFinal('2025-12') && !lpFinal('2026-01') && rekapOmzet(KINI).finalTerakhir.key === '2025-12' && rekapOmzet(KINI).tempo.lewat && /paling lambat 20 Jan/.test(rekapOmzet(KINI).tempo.teks), J(rekapOmzet(KINI).tempo));
var TL = susunTandaLapor('2025-12', W); ok('tandai Des 2025: dokumen rekapOmzet.lapor["2025-12"] bertanggal hari ini, tarif/batas tetap', !TL.tolak && TL.dokumen[0].data.lapor['2025-12'].tgl === '2026-09-19' && TL.dokumen[0].data.tarifPerMil === 5 && TL.dokumen[0].data.batasOmzet === 1000000); tulis(TL);
ok('batalkan tanda butuh ketukan kedua (perluYakin); dengan yakin → tanda hilang', susunTandaLapor('2025-12', W).perluYakin === true && !susunTandaLapor('2025-12', W, true).dokumen[0].data.lapor['2025-12']);
var BO = buktiOmzet({ '2025-11': true, '2025-12': true }, KINI); ok('bukti dari dua bulan final: tidak ditolak, Σ = jumlah (0 — kotak pasir tidak punya nota 2025), tanda "final"', !BO.tolak && BO.n === 2 && BO.total === 0 && BO.cocok && BO.baris.every(function (b) { return b.tanda === 'final'; }));

// ==================== NERACA ====================
var NP = neracaPada(null, KINI); var NM = hitungNeraca();
ok('neraca hari ini: kas, stok, piutang, kasbon = hitungNeraca; modal tertanam 25.000.000; aset = Σ harta; laba ditahan = aset − kewajiban − modal; seimbang; kekayaan = N.total', NP.N.kas === NM.kas && NP.modal === 25000000 && dekat(NP.aset, NP.harta.reduce(function (a, r) { return a + (r.n || 0); }, 0)) && dekat(NP.labaDitahan, NP.aset - NP.kewajiban - 25000000) && NP.seimbang && NP.total === NM.total && !NP.tolak, J([NP.aset, NP.kewajiban, NP.labaDitahan, NP.tolak]));
ok('pembanding: laba kumulatif mesin − prive 100.000 = menurutMesin; selisih buku DISEBUT di catatan (bukan disembunyikan)', NP.menurutMesin === NP.labaKum - 100000 && /Laba bersih kumulatif mesin/.test(NP.catatan) && (Math.abs(NP.selisihBuku) > 0.5 ? /belum terjelaskan buku/.test(NP.catatan) : /cocok/.test(NP.catatan)), NP.catatan);
ok('piutang 200.000 (bon 300.000 − bayar 100.000) · kasbon 200.000 · utang pemasok 15.000.000 (bon 20 jt − bayar 5 jt)', NP.N.piutang === 200000 && NP.N.kasbon === 200000 && NP.N.utangPemasok === 15000000, J(NP.N));
tulis(susunAturLaporan({ asetTetap: '5.000.000', asetKet: 'timbangan' }, W)); var NP2 = neracaPada(null, KINI);
ok('aset tetap 5.000.000 (isian owner): aset & laba ditahan naik 5.000.000, baris harta bertambah menyebut "isian owner"', NP2.aset === NP.aset + 5000000 && NP2.labaDitahan === NP.labaDitahan + 5000000 && NP2.harta.some(function (r) { return /isian owner: timbangan/.test(r.nama) && r.n === 5000000; }));
ok('neraca per 17 Sep: kas = kasPada("2026-09-17"); per 14 Sep (mundur dari titik) → kas null, DITOLAK dicetak', neracaPada('2026-09-17', KINI).N.kas === kasPada('2026-09-17') && neracaPada('2026-09-14', KINI).N.kas === null && /titik kas/.test(neracaPada('2026-09-14', KINI).tolak));
var BK = bandingKekayaan(KINI); ok('banding dengan saat titik kas 15 Sep: ada, selisih = kini − awal', BK.ada && BK.selisih === BK.kini - BK.awal && /Saat titik kas 15 Sep/.test(BK.teks));
localStorage.removeItem('miqbal_titik_kas_v1'); ok('tanpa titik kas: neraca total null, tolak menyebut titik kas, aset null', neracaPada(null, KINI).total === null && /titik kas/.test(neracaPada(null, KINI).tolak) && neracaPada(null, KINI).aset === null);
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-15', laci: 2000000, brankas: 10000000, rekening: 3000000, amplop: 1000000 }));

// ==================== DK1 · KOP & IDENTITAS ====================
var ID = identitasUsaha(); ok('bawaan: nama Toko Beras M.IQBAL, alamat kosong → belum lengkap, versi 0 (kop bawaan)', ID.nama === 'Toko Beras M.IQBAL' && ID.alamat === '' && !ID.lengkap && ID.versi === 0 && !ID.dariOwner);
ok('periksa: NPWP 10 angka ditolak; NIB 12 angka ditolak; telepon pendek ditolak; NPWP 16 angka & NIB 13 angka lolos', /NPWP harus 15 atau 16/.test(periksaIdentitas({ nama: 'A', alamat: 'B', npwp: '1234567890' })) && /NIB harus 13/.test(periksaIdentitas({ nama: 'A', alamat: 'B', nib: '123456789012' })) && /telepon/.test(periksaIdentitas({ nama: 'A', alamat: 'B', telepon: '0812' })) && periksaIdentitas({ nama: 'A', alamat: 'B', npwp: '1234567890123456', nib: '1234567890123' }) === '');
ok('simpan tanpa alamat DITOLAK (bank/pajak butuh alamat)', /Alamat wajib/.test(susunIdentitas({ nama: 'Toko Beras M.IQBAL', alamat: '' }, W).tolak));
var RI = tulis(susunIdentitas({ alamat: 'Jl. Contoh Raya No. 12', telepon: '0812-0000-0000', npwp: '1234567890123456', gaya: 'tengah' }, W));
ok('simpan → kop v1: dokumen aturanToko/identitas (versi 1, riwayat menyebut Alamat, Telepon, NPWP, gaya kop) + aturanToko/struk kop ikut (nota Jual memakai kop yang sama)', RI.versi === 1 && RI.dokumen[0].data.id === 'identitas' && RI.dokumen[0].data.versi === 1 && RI.dokumen[0].data.riwayat[0].ubah.join() === 'Alamat,Telepon / WA,NPWP,gaya kop' && RI.dokumen[1].data.id === 'struk' && RI.dokumen[1].data.kop.alamat === 'Jl. Contoh Raya No. 12' && RI.dokumen[1].data.kop.telp === '0812-0000-0000', J(RI.dokumen));
ID = identitasUsaha(); ok('sesudah simpan: lengkap, versi 1, gaya tengah; simpan lagi tanpa perubahan DITOLAK', ID.lengkap && ID.versi === 1 && ID.gaya === 'tengah' && /Tidak ada yang berubah/.test(susunIdentitas({}, W).tolak));
ok('kop penuh menyebut NPWP; kop ringkas tidak; alamat + telepon digabung', /NPWP 1234567890123456/.test(kopUntuk('penuh').resmi) && kopUntuk('ringkas').resmi === '' && kopUntuk('ringkas').alamat === 'Jl. Contoh Raya No. 12 · 0812-0000-0000');
var PK = pakaiKop(); ok('ragam bawaan: nota/kartu/slip/harian ringkas, laporan/omzet/bon/setor penuh; nomor awal 1', PK.pakai.nota === 'ringkas' && PK.pakai.laporan === 'penuh' && PK.pakai.setor === 'penuh' && PK.nomorAwal === 1 && !PK.dariOwner);
tulis(susunAturDokumen({ pakai: { nota: 'penuh' }, nomorAwal: '100' }, W)); ok('putar nota → penuh; nomor awal 100 → nomor berikutnya 100', pakaiKop().pakai.nota === 'penuh' && pakaiKop().pakai.kartu === 'ringkas' && nomorBerikut() === 100);

// ==================== CETAKAN BERNOMOR ====================
var C1 = tulis(susunCetakan({ jenis: 'labarugi', judul: 'Laporan Laba-Rugi', periode: 'September 2026', draf: true }, 'cetak', W));
ok('cetakan pertama No. 100: dokumenCetak {nomor 100, jenis, judul, cara cetak, kopVersi 1, draf}; berikutnya 101; riwayat menyebutnya', C1.nomor === 100 && C1.dokumen[0].koleksi === 'dokumenCetak' && C1.dokumen[0].data.kopVersi === 1 && C1.dokumen[0].data.draf === true && nomorBerikut() === 101 && riwayatCetakan(3)[0].nomor === 100 && /DRAF/.test(riwayatCetakan(3)[0].teks), J(C1));
ok('cara keluar asing ditolak; nomor awal ≤ nomor terpakai ditolak', /tidak dikenal/.test(susunCetakan({ jenis: 'x', judul: 'x' }, 'fax', W).tolak) && /sudah terpakai/.test(susunAturDokumen({ nomorAwal: '50' }, W).tolak));

// ==================== DK2 · LAPORAN BERKOP ====================
var LR = laporanBerkop('labarugi', '2026-09', 1, KINI);
ok('laba-rugi Sep: DRAF (belum tutup buku), baris Laba kotor 146.300 & Laba bersih = mesin, potongan QRIS 1.800 dipisah, kop penuh v1, tidak ditolak', LR.cap === 'DRAF' && !LR.final && LR.baris.find(function (r) { return r.nama === 'Laba kotor'; }).n === 146300 && LR.baris.find(function (r) { return r.nama === 'Laba bersih'; }).n === LM.labaBersih && LR.baris.find(function (r) { return /Potongan QRIS/.test(r.nama); }).n === -1800 && LR.kop.versi === 1 && LR.kop.resmi !== '' && !LR.tolak, J(LR.baris));
ok('laba-rugi menutup: Σ baris berangka (tanpa dua baris jumlah) = laba bersih', dekat(LR.baris.filter(function (r) { return r.n !== null && r.kelas !== 'jumlah'; }).reduce(function (a, r) { return a + r.n; }, 0), LM.labaBersih));
var LR3 = laporanBerkop('labarugi', '2026-09', 3, KINI); ok('3 bulan Jul–Sep: periode "Jul 26 – Sep 26", laba kotor = Agu 50.000 + Sep 146.300', LR3.periode === 'Jul 26 – Sep 26' && LR3.bulan.length === 3 && LR3.baris.find(function (r) { return r.nama === 'Laba kotor'; }).n === 196300);
var LN = laporanBerkop('neraca', '2026-09', 1, KINI); ok('neraca berkop: per 19 Sep (bulan berjalan dipotong hari ini), Jumlah harta = Jumlah kewajiban & modal, catatan menyebut aset = kewajiban + modal + laba ditahan', /per 19 Sep/.test(LN.sub) && LN.baris.find(function (r) { return r.nama === 'Jumlah harta'; }).n === LN.baris.find(function (r) { return r.nama === 'Jumlah kewajiban & modal'; }).n && /Aset Rp/.test(LN.catatan) && !LN.tolak, J(LN.baris));
var LA = laporanBerkop('aruskas', '2026-09', 1, KINI); var kasAkhir = LA.baris[LA.baris.length - 1];
ok('arus kas Sep: kas awal 31 Agu SEBELUM titik kas → belum bisa dihitung (null, disebut); kas akhir = kasPada() (= kas neraca); kas bersih = Σ masuk − Σ keluar', LA.baris[0].n === null && /belum bisa dihitung/.test(LA.baris[0].nama) && kasAkhir.n === kasPada() && /kas di neraca/.test(LA.catatan) && dekat(LA.baris.find(function (r) { return r.nama === 'Kas bersih periode'; }).n, LA.baris.filter(function (r) { return r.n !== null && r.kelas !== 'jumlah' && r.nama !== LA.baris[0].nama && !/Penyesuaian/.test(r.nama); }).reduce(function (a, r) { return a + r.n; }, 0)), J(LA.baris));
var BD = bandingLabaRugi('2026-09', '2026-08', KINI); ok('banding Sep vs Agu: laba kotor 146.300 vs 50.000, selisih +96.300 (+193%), arah naik', BD.baris[2].a === 146300 && BD.baris[2].b === 50000 && BD.baris[2].d === 96300 && BD.baris[2].pct === 193 && BD.baris[2].arah === 'naik' && /\+96\.300/.test(BD.baris[2].teksD), J(BD.baris[2]));
var PB = paketBank({ labarugi: true, neraca: true, aruskas: true, omzet: true }, KINI);
ok('paket bank: bulan final terakhir Des 2025 → 4 dokumen semua final; laba-rugi 3 bulan Okt–Des 2025; neraca per akhir Des 2025', !PB.tolak && PB.daftar.length === 4 && PB.daftar[0].periode === 'Okt 25 – Des 25' && PB.daftar[0].final && PB.daftar[1].jenis === 'neraca' && /31 Des/.test(PB.daftar[1].sub) && PB.daftar[3].jenis === 'omzet', J(PB.daftar.map(function (d) { return [d.jenis, d.periode, d.final]; })));
ok('paket tanpa pilihan ditolak', /Pilih isi/.test(paketBank({}, KINI).tolak));

// ==================== DK4 · DOKUMEN KECIL ====================
var DS = dokumenKecil('setor', null, '', KINI); ok('setor: 1 pilihan (25.000.000, 8 Agu), baris Jumlah 25.000.000, kop penuh, angka "dari catatan Owner & toko"', DS.pilihan.length === 1 && DS.baris[DS.baris.length - 1].n === 25000000 && DS.baris[DS.baris.length - 1].kelas === 'jumlah' && DS.ragam === 'penuh' && /Owner & toko/.test(DS.identitas) && !DS.tolak, J(DS));
var DU = dokumenKecil('upah', null, '', KINI); ok('slip upah: pilihan dari buku bulanan lama (Ben 1.560.000, Gono 600.000), baris menyebut "sistem lama", kop ringkas', DU.pilihan.length === 2 && DU.baris[DU.baris.length - 1].n === 1560000 && /sistem lama/.test(DU.identitas) && DU.ragam === 'ringkas' && !DU.tolak, J(DU));
var DP = dokumenKecil('piutang', null, '', KINI); ok('kartu piutang Bu Contoh: bon 300.000 (19 Sep) → bayar 100.000 → sisa 200.000; saldo berjalan tiap baris; identitas "Sisa Rp200.000 = bon Rp300.000 − bayar Rp100.000"; sisa = mesin', DP.pilihan[0].nama === 'Bu Contoh' && DP.baris.length === 3 && DP.baris[0].saldo === 300000 && DP.baris[1].saldo === 200000 && DP.baris[2].n === 200000 && /Sisa Rp200\.000 = bon Rp300\.000 − bayar Rp100\.000/.test(DP.identitas) && !DP.tolak && DP.adaSaldo, J(DP));
var DB = dokumenKecil('bon', null, '', KINI); ok('rekap bon RODA CONTOH: bon 20.000.000 − dibayar 5.000.000 = sisa 15.000.000 = mesin utang pemasok', DB.pilihan[0].nama === 'RODA CONTOH' && DB.pilihan[0].n === 15000000 && DB.baris[DB.baris.length - 1].n === 15000000 && /Sisa Rp15\.000\.000 = bon Rp20\.000\.000 − dibayar Rp5\.000\.000/.test(DB.identitas) && !/mesin utang pemasok menyebut/.test(DB.identitas), J(DB));
var DN = daftarNota('', KINI, 40); ok('nota 60 hari terakhir: 8 nota (Agu ikut, j6 batal ikut bertanda), terbaru dulu; cari "contoh" → 1 (Bu Contoh)', DN.daftar.length === 8 && DN.daftar[0].id === 'j7' && DN.daftar.some(function (x) { return x.id === 'j6' && x.batal; }) && daftarNota('contoh', KINI).cocok === 1, J(DN.daftar.map(function (x) { return x.id; })));
var DNK = dokumenKecil('nota', null, '', KINI); ok('nota belum dipilih → tolak "Pilih notanya"; sub menyebut 8 nota cocok', /Pilih notanya/.test(DNK.tolak) && DNK.cocokN === 8);
DNK = dokumenKecil('nota', 't:t4', '', KINI); ok('nota j4 (Tunai 250.000): cap SALINAN ke-1, baris dari penyusun struk (TOTAL 250.000), kop nota kini penuh (diputar), teks struk ada', DNK.cap === 'SALINAN ke-1' && DNK.salinanKe === 1 && DNK.baris.some(function (b) { return /TOTAL/i.test(b.nama) && b.n === 250000; }) && DNK.ragam === 'penuh' && /250\.000/.test(DNK.teksTambahan) && !DNK.tolak, J(DNK));
tulis(susunCetakan({ jenis: 'nota', judul: 'Nota', periode: '19 Sep', trxId: DNK.trxId, salinanKe: DNK.salinanKe }, 'wa', W));
ok('sesudah dikirim: salinan berikutnya ke-2; nota lain tetap ke-1; nota batal j6 DITOLAK dicetak ulang, cap DIBATALKAN', dokumenKecil('nota', 't:t4', '', KINI).cap === 'SALINAN ke-2' && dokumenKecil('nota', 't:t3', '', KINI).cap === 'SALINAN ke-1' && /dibatalkan/.test(dokumenKecil('nota', 't:t6', '', KINI).tolak) && dokumenKecil('nota', 't:t6', '', KINI).cap === 'DIBATALKAN');
var TD = teksDokumen(DP, 101, '2026-09-19'); ok('teks dokumen: kop (nama huruf besar, alamat), judul, baris + saldo, identitas, No. 101 · kop v1', /^TOKO BERAS M\.IQBAL\nJl\. Contoh Raya/.test(TD) && /KARTU PIUTANG/.test(TD) && /\(saldo Rp300\.000\)/.test(TD) && /Sisa Rp200\.000 = bon/.test(TD) && /No\. 101 · kop v1 · 19 Sep/.test(TD), TD);
// kop belum lengkap → semua dokumen ditolak dicetak
pasok('aturanToko', cacheMentah('aturan').filter(function (d) { return d.id !== 'identitas' && d.id !== 'struk'; }));
ok('kop belum lengkap (identitas dicabut): laporan berkop, dokumen kecil, bukti omzet, paket bank semua DITOLAK menyebut Setelan/kop', /Kop belum lengkap/.test(laporanBerkop('labarugi', '2026-09', 1, KINI).tolak) && /Kop belum lengkap/.test(dokumenKecil('setor', null, '', KINI).tolak) && /Kop belum lengkap/.test(paketBank({ omzet: true }, KINI).tolak));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
if (CAD.titikKas) localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(CAD.titikKas));
var KINI = new Date(Date.now()); var salah = []; var bl = hariIniIso(KINI).slice(0, 7);
var LB = labaBulan(bl, KINI); var LM = hitungLabaBersihRentang(bl + '-01', akhirBulanIso(bl)); if (LB.labaBersih !== LM.labaBersih) salah.push('laba bulan ≠ mesin');
var LR = laporanBerkop('labarugi', bl, 1, KINI); var lb = LR.baris.find(function (r) { return r.nama === 'Laba bersih'; }); if (lb.n !== LM.labaBersih) salah.push('laba-rugi berkop ≠ mesin');
var NP = neracaPada(null, KINI); if (NP.aset !== null && !NP.seimbang) salah.push('neraca tidak seimbang');
var RO = rekapOmzet(KINI); var RH = rekapHari(hariIniIso(KINI)); var DN = daftarNota('', KINI, 40); var DP = dokumenKecil('piutang', null, '', KINI); var DB = dokumenKecil('bon', null, '', KINI);
print(JSON.stringify({ salah: salah, bulan: bl, margin: LB.margin, labaBersih: LB.labaBersih, tunai: LB.tunai, cakupan: LB.cakupan, mdr: LB.mdr, rugi: LB.rugi.length, tanpaHpp: LB.tanpaHpp.length, susut: LB.susut.length, hariIni: { n: RH.n, omzet: RH.omzet, bersih: RH.bersih, buku: RH.buku.length },
  omzet12: RO.daftar.map(function (b) { return b.omzet; }), totalTahun: RO.totalTahun, final: RO.adaFinal, neraca: NP.aset === null ? 'kas tidak ada di cadangan' : { aset: NP.aset, kewajiban: NP.kewajiban, modal: NP.modal, labaDitahan: NP.labaDitahan, selisihBuku: NP.selisihBuku, tolak: NP.tolak },
  nota60hari: DN.cocok, piutang: { n: DP.pilihan.length, tolak: DP.tolak, baris: DP.baris.length }, bon: { n: DB.pilihan.length, tolak: DB.tolak }, kop: identitasUsaha().lengkap }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:1500]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            # ---- laba
            'diterima tunai = laba bersih (margin nota bon tidak dikurangkan)': js.replace("const tunai = L.labaBersih - marginKredit;", "const tunai = L.labaBersih;"),
            'potongan QRIS tidak dipisah dari biaya toko': js.replace("const mdr = lpMdrRentang(awal, akhir); const biayaLain = L.biayaToko - mdr;", "const mdr = 0; const biayaLain = L.biayaToko;"),
            'susut hilang dari tangga kotor → bersih (jumlahnya tidak menutup)': js.replace("['Susut & selisih stok', L.susutStok], ['Laba bersih', L.labaBersih, 'jumlah']", "['Laba bersih', L.labaBersih, 'jumlah']"),
            'bulan tanpa catatan digambar sama dengan bulan nol': js.replace("const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && !susut.length;", "const tanpaCatatan = false;"),
            # ---- harian
            'nota batal ikut jumlah nota hari itu': js.replace("const perJam = Object.keys(jam).sort().map((j) => jam[j]);", "const perJam = Object.keys(jam).sort().map((j) => jam[j]); L.jumlahTrx += ambilPenjualanSemua().filter((p) => p.tanggal === iso && p.dibatalkan).length;"),
            'teks WA lupa menyebut bon yang belum jadi uang': js.replace("if (R.kredit) b.push('Bon (belum jadi uang): '", "if (false) b.push('Bon (belum jadi uang): '"),
            # ---- bulanan / rekap omzet
            'semua bulan dianggap final tanpa tutup buku': js.replace("function lpFinal(key) { const era = bkEra(); return era !== null && Number(key.slice(0, 4)) <= era; }", "function lpFinal(key) { return true; }"),
            'kumulatif diisi juga untuk bulan tahun lalu (bukan —)': js.replace("kum: th === tahunIni ? kum : null", "kum: kum"),
            'tanda dilaporkan diizinkan pada bulan draf': js.replace("if (!lpFinal(key)) return { tolak: lpNamaBulan(key) + ' belum tutup buku", "if (false) return { tolak: lpNamaBulan(key) + ' belum tutup buku"),
            'membatalkan tanda tanpa ketukan kedua': js.replace("if (sudah) { if (!yakin) return { tolak: 'Ketuk sekali lagi", "if (sudah) { if (false) return { tolak: 'Ketuk sekali lagi"),
            'bukti omzet menerima bulan draf': js.replace("terpilih.some((b) => !b.final) ? 'Ada bulan yang belum tutup buku (DRAF)", "false ? 'Ada bulan yang belum tutup buku (DRAF)"),
            'tarif per seribu tanpa batas atas': js.replace("if (!(tarif >= 0 && tarif <= 1000)) return { tolak:", "if (false) return { tolak:"),
            'tagihan bulan yang belum dibayar tidak disebut': js.replace("const belum = B.filter((x) => !x.tanggal && x.bulan === key && x.nominal > 0);", "const belum = [];"),
            # ---- neraca
            'modal owner tidak dipisah dari laba ditahan': js.replace("const labaDitahan = aset === null ? null : aset - kewajiban - modal;", "const labaDitahan = aset === null ? null : aset - kewajiban;"),
            'neraca tanpa titik kas tetap dicetak': js.replace("const tolak = !kasAda ? 'Kas belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya' :", "const tolak = false ? '' :"),
            'aset tetap isian owner tidak ikut aset': js.replace("const aset = kasAda ? N.kas + N.stok + N.piutang + N.kasbon + AT.asetTetap : null;", "const aset = kasAda ? N.kas + N.stok + N.piutang + N.kasbon : null;"),
            # ---- kop & cetakan
            'NPWP tidak diperiksa panjangnya': js.replace("if (d.npwp && [15, 16].indexOf(lpDigit(d.npwp).length) < 0) return 'NPWP harus 15 atau 16 angka", "if (false) return 'NPWP harus 15 atau 16 angka"),
            'simpan identitas tidak menaikkan versi kop': js.replace("const versi = I.versi + 1; const riwayat =", "const versi = I.versi; const riwayat ="),
            'kop ringkas tidak ikut ke setelan struk (nota memakai kop lain)': js.replace("{ koleksi: 'aturanToko', data: { id: 'struk', tanggal: w.tanggal, jam: w.jam, kop: { nama: d.nama.slice(0, 40), alamat: d.alamat.slice(0, 80), telp: d.telepon.slice(0, 30) },", "{ koleksi: 'aturanToko', data: { id: 'struk', tanggal: w.tanggal, jam: w.jam, kop: S.kop,"),
            'nomor awal setelan owner diabaikan': js.replace("function nomorBerikut() { return Math.max(nomorTerakhir() + 1, pakaiKop().nomorAwal); }", "function nomorBerikut() { return nomorTerakhir() + 1; }"),
            'salinan nota selalu ke-1 (cetak ulang tidak berjejak)': js.replace("function salinanKe(trxId) { return ambilDokumenCetak().filter((d) => d.jenis === 'nota' && String(d.trxId) === String(trxId)).length + 1; }", "function salinanKe(trxId) { return 1; }"),
            'dokumen dicetak dengan kop belum lengkap': js.replace("if (!tolak && !I.lengkap) tolak = 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)';\n  return { jenis: J[0], namaJenis: J[1]", "\n  return { jenis: J[0], namaJenis: J[1]"),
            # ---- laporan berkop / dokumen kecil
            'kas akhir arus kas dihitung dari kas awal + bersih (bukan mesin kas)': js.replace("const kasAkhir = kasPada(sampai > iso ? null : sampai);", "const kasAkhir = (kasPada(ugTambahHari(dari, -1)) || 0) + K.bersih;"),
            'paket bank disusun tanpa bulan final': js.replace("const tolak = !F ? 'Belum ada bulan yang tutup buku — bank butuh angka FINAL; sampai tutup buku pertama, cetak laporan biasa bercap DRAF' :", "const tolak = false ? '' :"),
            'kartu piutang menganggap pembayaran sebagai tambahan bon': js.replace("const masuk = m.jenis === 'jual' || m.jenis === 'saldoAwal';", "const masuk = m.jenis !== 'hapusBuku';"),
            'nota yang dibatalkan boleh dicetak ulang': js.replace("if (X.batal) tolak = 'Nota dibatalkan tidak dicetak ulang';", ""),
            'nota batal tidak ditandai di daftar cetak ulang': js.replace("batal: !N.berlaku || N.dibatalkan, salinan:", "batal: false, salinan:"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, 'backup-batch-*.json')))
    if cad and not g:
        h, e = jalan(JAM_TETAP.replace("'2026-09-19T10:00:00+07:00'", "'2026-09-22T10:00:00+07:00'") + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if h is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s): %s' % (os.path.basename(cad[-1]), json.dumps(h, ensure_ascii=False)))
        if h['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
