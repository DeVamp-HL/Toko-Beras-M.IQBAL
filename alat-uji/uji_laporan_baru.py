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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/uang-logika.js', 'baru/js/layar/upah-logika.js', 'baru/js/layar/owner-toko-logika.js', 'baru/js/layar/tutup-hari-logika.js', 'baru/js/layar/tutup-buku-logika.js',
                                  'baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/setengah-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/pajak-logika.js', 'baru/js/layar/laporan-logika.js']
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
                    'rincianGaji': [{'nama': 'Alfa Contoh', 'hari': 26, 'gaji': 1560000}, {'nama': 'Gama', 'hari': 10, 'gaji': 600000}], 'tanggalBayarGaji': {'Alfa Contoh': '2026-08-31', 'Gama': '2026-08-31'}, 'gaji': 2160000, 'gajiHariOrang': 36},
                   {'id': '2026-09', 'bulan': '2026-09', 'listrik': 350000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {}, 'rincianGaji': [], 'gaji': 0, 'gajiHariOrang': 0}],
  'kasbonMutasi': [{'id': 701, 'tipe': 'ambil', 'namaPegawai': 'Alfa Contoh', 'nominal': 200000, 'tanggal': '2026-09-05', 'catatan': 'Keperluan keluarga'}],
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
ok('diterima tunai = laba bersih − margin nota bon 21.800 (1 nota bon, pokok 300.000) + margin bon yang dibayar bulan ini 7.267 (39b no. 39: bayar 100.000 dari bon 300.000)', LB.marginKredit === 21800 && LB.nKredit === 1 && LB.omzetKredit === 300000 && LB.marginDibayar === 7267 && LB.tunai === LB.labaBersih - 21800 + 7267);
ok('cakupan = omzet ber-HPP ÷ (ber-HPP + tanpa HPP 80.000) = 2.470.000/2.550.000; 1 nota tanpa modal disebut', LB.penyebut === 2550000 && dekat(LB.cakupan * 1000, 968.6) && LB.tanpaHpp.length === 1 && LB.tanpaHpp[0].id === 'j8' && LB.omzetTanpaHpp === 80000, J([LB.cakupan, LB.tanpaHpp]));
ok('potongan QRIS 1.800 dipisah dari biaya toko; biaya lain = biayaToko − 1.800; terjun menutup: Σ baris (tanpa baris jumlah) = laba bersih', LB.mdr === 1800 && LB.biayaLain === LB.L.biayaToko - 1800 && dekat(LB.terjun.filter(function (r) { return r.kelas !== 'jumlah'; }).reduce(function (a, r) { return a + r.n; }, 0), LB.labaBersih), J(LB.terjun));
ok('nota rugi: j7 dijual 120.000 modal 140.000 → −20.000; susut Sep 1 baris −26.000 = L.susutStok', LB.rugi.length === 1 && LB.rugi[0].id === 'j7' && LB.rugi[0].margin === -20000 && LB.susut.length === 1 && LB.susutTotal === -26000 && LB.L.susutStok === -26000);
ok('bulan berjalan: aman diambil = batas aman (laba bulan berjalan, owner belum menyetel) − prive 100.000', LB.berjalan && LB.aman && LB.aman.dariLaba && LB.aman.terpakai === 100000 && LB.aman.sisa === LB.aman.batas - 100000, J(LB.aman));
var LB7 = labaBulan('2026-07', KINI); ok('Juli tanpa satu catatan pun → tanpaCatatan (beda dari bulan yang untungnya nol); Agu: margin 50.000, bukan tanpaCatatan', LB7.tanpaCatatan && LB7.margin === 0 && !labaBulan('2026-08', KINI).tanpaCatatan && labaBulan('2026-08', KINI).margin === 50000);

// ---- 39b no. 38 (owner 30 Sep 2026): selisih laci tutup hari (lebih +, kurang −) = baris "Lebih/kurang kas" di LABA — satu aturan (ugLabaBersih), semua layar laba
// 17 Sep LEBIH 50.000 · 18 Sep tutup pertama KURANG 20.000 lalu tutup ulang PAS (riwayat) · 25 Agu sistem lama LEBIH 15.000 (kolom selisih saja) · 19 Sep tidak bisa dihitung (null)
var TH38 = [{ koleksi: 'tutupHari', data: { id: '2026-09-17', tanggal: '2026-09-17', jam: '21:00', sistemBaru: true, selisih: 50000, selisihLaci: 50000, alasanSelisih: 'Ada penjualan belum dicatat' } },
  { koleksi: 'tutupHari', data: { id: '2026-09-18', tanggal: '2026-09-18', jam: '21:30', sistemBaru: true, selisih: 0, selisihLaci: 0, riwayat: [{ id: '2026-09-18', tanggal: '2026-09-18', jam: '21:00', sistemBaru: true, selisih: -20000, selisihLaci: -20000, digantiPada: '2026-09-18T14:30:00.000Z' }] } },
  { koleksi: 'tutupHari', data: { id: '2026-08-25', tanggal: '2026-08-25', jam: '21:00', selisih: 15000, alasanSelisih: 'Keuntungan' } },
  { koleksi: 'tutupHari', data: { id: '2026-09-19', tanggal: '2026-09-19', jam: '21:00', selisih: null, alasanSelisih: 'patokan kas belum bisa dihitung' } }];
var lk38 = function (xs) { return (xs || []).filter(function (r) { return /^Lebih\/kurang kas/.test(r.nama || ''); }); };
var NP38 = neracaPada(null, KINI), T38 = rekapTahun('2026', KINI), A38 = aturKeluar('2026-09-19').labaBulan;
ok('39b-38 tanpa selisih laci: lebih/kurang kas 0 dan TIDAK digambar (Laba, laba-rugi berkop, Ke mana laba kotor, Banding, Tahunan) — laba = mesin persis seperti sebelum keputusan',
  LB.L.lebihKurangKas === 0 && LB.labaBersih === LM.labaBersih && !lk38(LB.terjun).length && !lk38(laporanBerkop('labarugi', '2026-09', 1, KINI).baris).length && !keManaLabaKotor('2026-09', KINI).baris.some(function (r) { return r.id === 'lebihKurang'; })
  && !lk38(bandingLabaRugi('2026-09', '2026-08', KINI).baris).length && T38.lebihKurangKas === 0, J([LB.L.lebihKurangKas, LB.labaBersih, LM.labaBersih, T38.lebihKurangKas]));
ok('39b-38 Laba Sep: lebih 50.000 (17 Sep) + kurang 20.000 (18 Sep, tutup pertama di riwayat; tutup ulang PAS) = baris "Lebih/kurang kas" +30.000 · 2 malam tepat di atas Laba bersih; laba bersih = mesin + 30.000; tangga menutup; diterima tunai ikut; selisih yang tidak bisa dihitung (19 Sep) = 0',
  denganCacheSementara(TH38, function () { var B = labaBulan('2026-09', KINI); var M = hitungLabaBersihRentang('2026-09-01', '2026-09-30'); var r = lk38(B.terjun); var i = B.terjun.indexOf(r[0]);
    return B.L.lebihKurangKas === 30000 && B.L.nLebihKurang === 2 && B.L.labaMesin === M.labaBersih && B.labaBersih === M.labaBersih + 30000 && r.length === 1 && r[0].n === 30000 && /2 malam/.test(r[0].nama) && B.terjun[i + 1].nama === 'Laba bersih' && B.terjun[i + 1].n === B.labaBersih
      && dekat(B.terjun.filter(function (x) { return x.kelas !== 'jumlah'; }).reduce(function (a, x) { return a + x.n; }, 0), B.labaBersih) && B.tunai === B.labaBersih - 21800 + 7267 && intiBulan('2026-09', KINI).labaBersih === B.labaBersih; }),
  J(denganCacheSementara(TH38, function () { var B = labaBulan('2026-09', KINI); return [B.L.lebihKurangKas, B.L.nLebihKurang, B.labaBersih, B.L.labaMesin, B.terjun.slice(-3)]; })));
ok('39b-38 sistem lama (kolom selisih tanpa selisihLaci) ikut dibaca: Agu lebih 15.000; laba-rugi berkop Sep & 3 bulan (Agu–Sep, Jul sebelum awal buku) punya baris lebih/kurang kas 30.000 / 45.000, Laba bersih = Laba, kalimatnya menyebut lebih/kurang kas',
  denganCacheSementara(TH38, function () { var A = labaBulan('2026-08', KINI); var R = laporanBerkop('labarugi', '2026-09', 1, KINI); var R3 = laporanBerkop('labarugi', '2026-09', 3, KINI); var lb = function (X) { return X.baris.filter(function (r) { return r.nama === 'Laba bersih'; })[0].n; };
    return A.L.lebihKurangKas === 15000 && A.labaBersih === A.L.labaMesin + 15000 && lk38(R.baris).length === 1 && lk38(R.baris)[0].n === 30000 && lb(R) === labaBulan('2026-09', KINI).labaBersih && /lebih\/kurang kas/.test(R.catatan)
      && lk38(R3.baris)[0].n === 45000 && lb(R3) === hitungLabaBersihRentang('2026-08-01', '2026-09-30').labaBersih + 45000; }),
  J(denganCacheSementara(TH38, function () { var R3 = laporanBerkop('labarugi', '2026-09', 3, KINI); return [labaBulan('2026-08', KINI).L.lebihKurangKas, R3.baris.slice(-3), R3.catatan]; })));
ok('39b-38 laba yang sama di Ke mana laba kotor (baris "Lebih/kurang kas", tetap menutup), neraca (laba kumulatif +45.000 → beda belum terjelaskan −45.000, harta tidak bergeser: kas sudah memuatnya lewat titik kas), Mingguan, Tahunan (Σ +45.000), Banding (baris 30.000 vs 15.000) & batas aman ambil pribadi (laba bulan berjalan +30.000)',
  denganCacheSementara(TH38, function () { var K = keManaLabaKotor('2026-09', KINI); var kb = K.baris.filter(function (r) { return r.id === 'lebihKurang'; }); var NP = neracaPada(null, KINI); var RM = rekapMinggu('2026-09-14', KINI); var T = rekapTahun('2026', KINI); var BD = bandingLabaRugi('2026-09', '2026-08', KINI); var bk = lk38(BD.baris);
    return K.menutup && kb.length === 1 && kb[0].n === 30000 && K.labaBersih === labaBulan('2026-09', KINI).labaBersih && NP.labaKum === NP38.labaKum + 45000 && NP.selisihBuku === NP38.selisihBuku - 45000 && NP.labaDitahan === NP38.labaDitahan
      && RM.lebihKurangKas === 30000 && RM.labaBersih === hitungLabaBersihRentang('2026-09-14', '2026-09-20').labaBersih + 30000 && T.lebihKurangKas === 45000 && T.labaBersih === T38.labaBersih + 45000
      && bk.length === 1 && bk[0].a === 30000 && bk[0].b === 15000 && BD.baris[BD.baris.length - 1].a === labaBulan('2026-09', KINI).labaBersih && aturKeluar('2026-09-19').labaBulan === A38 + 30000; }),
  J(denganCacheSementara(TH38, function () { var NP = neracaPada(null, KINI); return [keManaLabaKotor('2026-09', KINI).menutup, NP.labaKum - NP38.labaKum, NP.selisihBuku - NP38.selisihBuku, rekapMinggu('2026-09-14', KINI).lebihKurangKas, rekapTahun('2026', KINI).lebihKurangKas, aturKeluar('2026-09-19').labaBulan - A38]; })));

// ---- 39b no. 39 (owner 30 Sep 2026): margin bon ditahan dari "diterima tunai" sampai bonnya tertutup — urutan potong = buku bon (bon TERTUA dulu; bon yang
// tertutup sebagian melepas marginnya sebanding; uang lebih menunggu bon berikutnya). Uji Lintas: bon 10 Agu 600.000 (margin 60.000) & 20 Agu 400.000
// (margin 20.000), bayar 25 Agu 100.000 & 5 Sep 700.000, hapus buku 18 Sep 200.000. Uji Lebih: bayar 28 Agu 50.000 sebelum punya bon, bon 3 Sep 100.000 (margin 10.000).
var BON39 = [['k39a', '2026-08-10', 'Uji Lintas', 600000, 540000], ['k39b', '2026-08-20', 'Uji Lintas', 400000, 380000], ['k39c', '2026-09-03', 'Uji Lebih', 100000, 90000]].map(function (x) {
    return { koleksi: 'penjualan', data: { id: x[0], trxId: 'T' + x[0], tanggal: x[1], jam: '09:00', caraBayar: 'Kredit', namaPelanggan: x[2], jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: x[3], hppTotalSaatJual: x[4] } }; })
  .concat([[3901, 'bayar', 'Uji Lintas', 100000, '2026-08-25'], [3902, 'bayar', 'Uji Lintas', 700000, '2026-09-05'], [3903, 'hapusBuku', 'Uji Lintas', 200000, '2026-09-18'], [3904, 'bayar', 'Uji Lebih', 50000, '2026-08-28']].map(function (x) {
    return { koleksi: 'piutangMutasi', data: { id: x[0], tipe: x[1], namaPelanggan: x[2], nominal: x[3], tanggal: x[4], jam: '10:00', caraBayar: 'Tunai', alasan: 'uji' } }; }));
var A39 = labaBulan('2026-08', KINI), S39 = labaBulan('2026-09', KINI);
ok('39b-39 bon yang dibayar di bulan yang sama ikut: 19 Sep bayar 100.000 menutup sepertiga bon 300.000 (margin 21.800) → 7.267 kembali; diterima tunai = laba bersih − 21.800 + 7.267; Agu tanpa bon = laba bersih',
  S39.marginDibayar === 7267 && S39.marginDihapus === 0 && S39.tunai === S39.labaBersih - 21800 + 7267 && A39.marginKredit === 0 && A39.marginDibayar === 0 && A39.tunai === A39.labaBersih, J([S39.marginDibayar, S39.marginDihapus, S39.tunai, S39.labaBersih, A39.tunai, A39.labaBersih]));
ok('39b-39 lintas bulan: Agu bayar 100.000 → bon TERTUA (10 Agu) sebanding 10.000; Sep bayar 700.000 → sisa bon 10 Agu 50.000 + 200.000 bon 20 Agu 10.000, uang lebih 28 Agu menutup separuh bon 3 Sep 5.000 (dibayar 65.000); hapus buku 200.000 melepas 10.000 (laba bersih sudah memotong 200.000 penuh) — geser tunai Agu +10.000, Sep −125.000',
  denganCacheSementara(BON39, function () { var A = labaBulan('2026-08', KINI), S = labaBulan('2026-09', KINI);
    return A.marginKredit === 80000 && A.marginDibayar === 10000 && A.marginDihapus === 0 && A.tunai === A.labaBersih - 80000 + 10000 && A.tunai - A39.tunai === 10000
      && S.marginKredit === S39.marginKredit + 10000 && S.marginDibayar === S39.marginDibayar + 65000 && S.marginDihapus === 10000 && S.tunai === S.labaBersih - S.marginKredit + S.marginDibayar + 10000 && S.tunai - S39.tunai === -125000; }),
  J(denganCacheSementara(BON39, function () { var A = labaBulan('2026-08', KINI), S = labaBulan('2026-09', KINI); return [A.marginKredit, A.marginDibayar, A.tunai - A39.tunai, S.marginKredit, S.marginDibayar, S.marginDihapus, S.tunai - S39.tunai]; })));
ok('39b-39 tidak ada margin yang hilang atau terhitung dua kali: Σ (Agu + Sep) diterima tunai = Σ laba bersih − margin yang masih tertahan, dan yang tertahan = margin bagian bon yang masih terbuka di Pelanggan → Bon (rincianBelumLunas, sebanding)',
  denganCacheSementara(BON39, function () { var A = labaBulan('2026-08', KINI), S = labaBulan('2026-09', KINI); var tahan = (A.marginKredit - A.marginDibayar - A.marginDihapus) + (S.marginKredit - S.marginDibayar - S.marginDihapus);
    var mg = {}; ambilPenjualan().forEach(function (p) { mg[p.id] = p.hargaTotal - p.hppTotalSaatJual; }); var buka = 0; semuaBon(KINI).forEach(function (b) { b.buka.forEach(function (u) { if (u.idTrx && u.nominal > 0) buka += (mg[u.idTrx] || 0) * u.sisa / u.nominal; }); });
    return Math.abs(tahan - buka) < 1 && Math.abs(buka - (5000 + 21800 * 2 / 3)) < 0.01 && A.tunai + S.tunai === A.labaBersih + S.labaBersih - tahan; }),
  J(denganCacheSementara(BON39, function () { var A = labaBulan('2026-08', KINI), S = labaBulan('2026-09', KINI); return [A.tunai + S.tunai, A.labaBersih + S.labaBersih, A.marginKredit - A.marginDibayar - A.marginDihapus + S.marginKredit - S.marginDibayar - S.marginDihapus]; })));

// ---- 39b no. 37 (owner 2 Okt 2026 "37 buka"): retur nota BON memotong bon — mesin hitungPiutang membaca mutasi piutang tipe 'retur' (bon tertua dulu; bukan uang,
// bukan rugi); dokumen retur nota bon = nominalRefund 0 + potongBon (laba: pengurang penjualan lewat uangKembaliRetur; kas tidak membacanya). ANGKA CONTOH:
// Uji Retur bon 10 Sep 700.500 (pembulatan bon 500, modal 650.000) & 15 Sep 700.000 (modal 650.000), bayar 12 Sep 200.000 → sisa 1.200.500 (bon sebagian dibayar);
// Uji Sebagian bon 700.000 dibayar 500.000; Uji Lunas bon 280.000 dibayar lunas. Harga nota 14.000/kg, modal Angsa di buku 13.000/kg.
var KR37 = function (id, tgl, nama, kg, n, hpp, x) { return { koleksi: 'penjualan', data: Object.assign({ id: id, trxId: 'T' + id, tanggal: tgl, jam: '09:00', caraBayar: 'Kredit', namaPelanggan: nama, jenis: 'karung', merkSumber: 'Angsa', totalKg: kg, beratKarungAcuan: 50, jumlahKarung: kg / 50, hargaTotal: n, hppTotalSaatJual: hpp }, x || {}) }; };
var BY37 = function (id, tgl, nama, n) { return { koleksi: 'piutangMutasi', data: { id: id, tipe: 'bayar', namaPelanggan: nama, nominal: n, tanggal: tgl, jam: '10:00', caraBayar: 'Tunai', dicatatDi: 'sistem' } }; };
var BASE37 = [KR37('k37a', '2026-09-10', 'Uji Retur', 50, 700500, 650000, { pembulatan: 500 }), KR37('k37b', '2026-09-15', 'Uji Retur', 50, 700000, 650000), KR37('k37c', '2026-09-11', 'Uji Lunas', 20, 280000, 260000),
  KR37('k37d', '2026-09-11', 'Uji Sebagian', 50, 700000, 650000), BY37(3701, '2026-09-12', 'Uji Retur', 200000), BY37(3702, '2026-09-13', 'Uji Lunas', 280000), BY37(3703, '2026-09-13', 'Uji Sebagian', 500000)];
var W37 = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 37000; return function () { n += 1; return n; }; })() };
var RS37 = function (o) { return Object.assign(returAwal(), { rtAlasan: 'kualitas kurang', rtKondisi: 'utuh', sekarang: KINI }, o); };
var cariP37 = function (k) { return hitungPiutang().find(function (x) { return x.kunci === k; }) || {}; };
var potret37 = function () { var bon = cariP37('uji retur'); var sb = semuaBon(KINI).find(function (b) { return b.kunci === 'uji retur'; }) || {}; var kk = susunIsiKatalogKasir() || { piutang: [] };
  var st = hitungSaldoTutup('2026').piutang.find(function (x) { return x.nama === 'Uji Retur'; }) || {}; var rh = rekapHari('2026-09-19');
  return { sisa: bon.sisa, tertua: bon.tanggalTertua, buka: (sb.buka || []).map(function (u) { return [u.idTrx, u.sisa]; }), kr1: infoKreditPelanggan('Uji Retur').sisa, katalog: (kk.piutang.find(function (x) { return x.nama === 'Uji Retur'; }) || {}).sisa, tutup: st.sisa,
    piutangNeraca: hitungNeraca().piutang, kas: kasPada(null), nGerak: daftarGerakanKas().length, kasHari: rh.bersih, returHari: rh.retur, omzetHari: rh.omzet, stok: hitungStokKarungPerMerk().Angsa.sisaKg, L: labaBulan('2026-09', KINI) }; };
var A37 = denganCacheSementara(BASE37, function () { var P0 = potret37(); var R = susunRetur(RS37({ rtNotaId: 'k37b', ketik: '20' }), W37); var D = R.dokumen || [];
  return { P0: P0, R: R, D: D, P1: denganCacheSementara(D, potret37), kartu: denganCacheSementara(D, function () { return dokumenKecil('piutang', 'uji retur', '', KINI); }),
    lembar: denganCacheSementara(D, function () { return lembarBon(KINI, 'uji retur'); }), buku: denganCacheSementara(D, function () { return susunBon(KINI, 'uji retur').buku; }) }; });
var dt37 = function (D, i) { return (D[i] || { data: {} }).data; };
ok('39b-37 bon sebagian dibayar (sisa 1.200.500): retur 20 kg dari nota 15 Sep = dokumen retur nominalRefund 0 + potongBon 280.000 (20 kg, 0,4 karung, utuh) + mutasi piutang retur 280.000 atas nama Uji Retur — dua dokumen, tanpa karantina',
  A37.P0.sisa === 1200500 && A37.D.length === 2 && A37.D[0].koleksi === 'retur' && dt37(A37.D, 0).nominalRefund === 0 && dt37(A37.D, 0).potongBon === 280000 && dt37(A37.D, 0).totalKg === 20 && dt37(A37.D, 0).jumlahKarung === 0.4
  && A37.D[1].koleksi === 'piutangMutasi' && dt37(A37.D, 1).tipe === 'retur' && dt37(A37.D, 1).nominal === 280000 && dt37(A37.D, 1).namaPelanggan === 'Uji Retur', J([A37.P0.sisa, A37.R]));
// tinjauan MM1 (dibalik SENGAJA): retur memotong NOTA ASALNYA dulu, bukan bon tertua — dulu nota 10 Sep tinggal 220.500 dan nota 15 Sep (yang barangnya kembali) tetap 700.000
ok('39b-37 sisa bon turun PERSIS 280.000 (1.200.500 → 920.500) dan NOTA ASALNYA yang dipotong (tinjauan MM1): nota 15 Sep tinggal 420.000, nota 10 Sep tetap 500.500 (dibayar 200.000; Pelanggan → Bon = mesin)',
  A37.P1.sisa === 920500 && J(A37.P1.buka) === J([['k37a', 500500], ['k37b', 420000]]), J([A37.P1.sisa, A37.P1.buka]));
ok('39b-37 batas kredit KR1, katalog HP kasir, saldo tutup buku 2026 dan piutang neraca ikut turun sendiri (semuanya pembaca mesin): 920.500, neraca −280.000',
  A37.P1.kr1 === 920500 && A37.P1.katalog === 920500 && A37.P1.tutup === 920500 && A37.P1.piutangNeraca === A37.P0.piutangNeraca - 280000, J([A37.P1.kr1, A37.P1.katalog, A37.P1.tutup, A37.P1.piutangNeraca - A37.P0.piutangNeraca]));
ok('39b-37 retur tercatat dan uang laci/kas TIDAK bergerak: kas sekarang, jumlah baris buku kas, kas bersih 19 Sep sama persis (bukan refund, bukan pembayaran)',
  A37.D.length === 2 && A37.P0.kas !== null && A37.P1.kas === A37.P0.kas && A37.P1.nGerak === A37.P0.nGerak && A37.P1.kasHari === A37.P0.kasHari, J([A37.P0.kas, A37.P1.kas, A37.P0.nGerak, A37.P1.nGerak, A37.P0.kasHari, A37.P1.kasHari]));
ok('39b-37 laba: penjualan Sep turun 280.000 (baris Retur), modal 20 kg × 13.000 = 260.000 kembali (barang utuh) → laba bersih −20.000; omzet 19 Sep turun 280.000 (penjualan − retur, satu arti di semua layar)',
  A37.P1.L.L.returUang === A37.P0.L.L.returUang + 280000 && A37.P1.L.L.omzetHitung === A37.P0.L.L.omzetHitung - 280000 && A37.P1.L.L.returHpp === A37.P0.L.L.returHpp + 260000 && A37.P1.L.labaBersih === A37.P0.L.labaBersih - 20000
  && A37.P1.returHari === A37.P0.returHari + 280000 && A37.P1.omzetHari === A37.P0.omzetHari - 280000, J([A37.P1.L.L.returUang - A37.P0.L.L.returUang, A37.P1.L.L.returHpp - A37.P0.L.L.returHpp, A37.P1.L.labaBersih - A37.P0.L.labaBersih, A37.P1.omzetHari - A37.P0.omzetHari]));
ok('39b-37 stok: 20 kg utuh kembali ke buku Angsa', A37.P1.stok === A37.P0.stok + 20, J([A37.P0.stok, A37.P1.stok]));
// tinjauan U37-U5 (dibalik SENGAJA): margin yang dilepas retur = margin NOTA YANG DIRETUR (15 Sep), bukan bon tertua — dulu 50.500 × 280.000 ÷ 700.500 = 20.186 (nota 10 Sep)
ok('39b-37 diterima tunai: margin bon yang ditutup retur dilepas dari NOTA ASALNYA (nota 15 Sep, margin 50.000 × 280.000 ÷ 700.000 = 20.000 = margin barang yang kembali) dan rumusnya menutup; bulan tanpa retur nota bon tidak punya kolom marginDiretur (bentuk lama)',
  A37.P1.L.marginDiretur === 20000 && !('marginDiretur' in A37.P0.L) && A37.P1.L.marginKredit === A37.P0.L.marginKredit && A37.P1.L.tunai === A37.P1.L.labaBersih - A37.P1.L.marginKredit + A37.P1.L.marginDibayar + A37.P1.L.marginDihapus + 20000,
  J([A37.P1.L.marginDiretur, A37.P1.L.tunai, A37.P1.L.labaBersih, A37.P1.L.marginKredit, A37.P1.L.marginDibayar]));
ok('39b-37 Kartu Piutang: baris "barang kembali (retur)" −280.000, identitas "… − retur Rp280.000", saldo kartu = mesin (tidak ditolak karena beda sisa; kop kotak pasir memang belum lengkap)',
  !/≠ sisa menurut mesin/.test(A37.kartu.tolak || '') && /− retur Rp280\.000/.test(A37.kartu.identitas) && A37.kartu.baris.some(function (b) { return /barang kembali \(retur\)/.test(b.nama) && b.n === -280000; }), J([A37.kartu.identitas, A37.kartu.tolak]));
ok('39b-37 Pelanggan → Bon: riwayat "barang kembali (retur), bon dipotong" −280.000; Buku bon punya baris retur; rincian yang belum lunas berjumlah sisa mesin',
  !!A37.lembar && A37.lembar.riwayat.some(function (r) { return /barang kembali \(retur\), bon dipotong/.test(r.teks) && r.n === -280000; }) && !!A37.buku && A37.buku.halaman.some(function (r) { return r.jenis === 'retur' && r.n === -280000; })
  && A37.lembar.rinci.reduce(function (a, r) { return a + r.n; }, 0) === 920500, J([A37.lembar && A37.lembar.riwayat, A37.buku && A37.buku.halaman]));
var B37 = denganCacheSementara(BASE37, function () { var P0 = potret37(); var R = susunRetur(RS37({ rtNotaId: 'k37a', ketik: '50' }), W37); var D = R.dokumen || [];
  return { P0: P0, R: R, D: D, P1: denganCacheSementara(D, potret37), lebih: denganCacheSementara(D.concat([BY37(3704, '2026-09-19', 'Uji Retur', 600000)]), function () { var d = cariP37('uji retur'); var b = semuaBon(KINI).find(function (x) { return x.kunci === 'uji retur'; }) || {};
    return { sisa: d.sisa, PL: pecahLebih(d), status: b.status, cap: b.cap }; }) }; });
ok('39b-37 retur PENUH nota bon ber-pembulatan: 50 kg dari nota 10 Sep = 700.000 + pembulatan bon 500 = 700.500 (bon nota itu habis persis); sisa 1.200.500 → 500.000, nota 10 Sep tertutup, umur bon kini dari nota 15 Sep',
  dt37(B37.D, 0).potongBon === 700500 && dt37(B37.D, 1).nominal === 700500 && B37.P1.sisa === 500000 && J(B37.P1.buka) === J([['k37b', 500000]]) && B37.P0.tertua === '2026-09-10' && B37.P1.tertua === '2026-09-15', J([B37.R, B37.P1.sisa, B37.P1.buka, B37.P1.tertua]));
ok('39b-37 retur penuh: penjualan Sep turun 700.500, modal 650.000 kembali → laba bersih turun 50.500 = margin nota itu (seolah tidak pernah terjual); stok +50 kg; kas tetap; margin yang dilepas = bagian bon tertutup retur (500.500 dari nota 10 Sep + 200.000 dari nota 15 Sep)',
  B37.P1.L.L.returUang === B37.P0.L.L.returUang + 700500 && B37.P1.L.L.returHpp === B37.P0.L.L.returHpp + 650000 && B37.P1.L.labaBersih === B37.P0.L.labaBersih - 50500 && B37.P1.stok === B37.P0.stok + 50 && B37.P1.kas === B37.P0.kas
  && B37.P1.L.marginDiretur === Math.round(50500 * 500500 / 700500 + 50000 * 200000 / 700000), J([B37.P1.L.labaBersih - B37.P0.L.labaBersih, B37.P1.L.marginDiretur]));
ok('39b-37 kelebihan bayar SESUDAH retur = uang pelanggan, bukan "hapus buku terbayar" (pecahLebih tahu retur): bayar 600.000 atas sisa 500.000 → sisa −100.000, kelebihan bayar 100.000',
  B37.lebih.sisa === -100000 && B37.lebih.PL.uang === 100000 && B37.lebih.PL.hapus === 0 && B37.lebih.status === 'lebih' && B37.lebih.cap === 'kelebihan bayar', J(B37.lebih));
var C37 = denganCacheSementara(BASE37, function () { var rusak = susunRetur(RS37({ rtNotaId: 'k37b', ketik: '10', rtKondisi: 'tidak_utuh' }), W37);
  return { lebihSisa: susunRetur(RS37({ rtNotaId: 'k37d', ketik: '20' }), W37), pas: susunRetur(RS37({ rtNotaId: 'k37d', ketik: '14,28' }), W37), lunas: susunRetur(RS37({ rtNotaId: 'k37c', ketik: '10' }), W37),
    rusak: rusak, P0: potret37(), P1: denganCacheSementara(rusak.dokumen || [], potret37) }; });
ok('39b-37 retur melebihi sisa bon DITOLAK (Uji Sebagian: bon 700.000 dibayar 500.000): kalimat menyebut sisa Rp200.000 dan batas 14,28 kg; 14,28 kg (199.920) lolos — sama dengan bayar & hapus buku, sisa tidak didorong ke bawah nol',
  !C37.lebihSisa.dokumen && /melebihi sisa bon Uji Sebagian \(Rp200\.000\)/.test(C37.lebihSisa.tolak || '') && /paling banyak 14,28 kg/.test(C37.lebihSisa.tolak || '') && !!C37.pas.dokumen && dt37(C37.pas.dokumen, 0).potongBon === 199920, J([C37.lebihSisa.tolak, C37.pas.tolak]));
ok('39b-37 bon sudah LUNAS (Uji Lunas): retur DITOLAK, tidak dijadikan kelebihan bayar tanpa uang (no. 4: kelebihan bayar = uang pelanggan sungguhan); kalimat menunjuk retur ketik tangan bila uangnya dikembalikan dari laci',
  !C37.lunas.dokumen && /sudah lunas/.test(C37.lunas.tolak || '') && /Retur ketik tangan/.test(C37.lunas.tolak || ''), C37.lunas.tolak);
ok('39b-37 barang RUSAK dari nota bon: retur + mutasi + KARANTINA (3 dokumen); bon tetap turun 140.000, stok jual tidak bertambah, laba bersih turun penuh 140.000 (modalnya tidak kembali), kas tetap',
  (C37.rusak.dokumen || []).length === 3 && C37.rusak.dokumen[2].koleksi === 'karantina' && C37.P1.sisa === C37.P0.sisa - 140000 && C37.P1.stok === C37.P0.stok && C37.P1.L.labaBersih === C37.P0.L.labaBersih - 140000 && C37.P1.kas === C37.P0.kas,
  J([C37.rusak, C37.P1.sisa - C37.P0.sisa, C37.P1.stok - C37.P0.stok, C37.P1.L.labaBersih - C37.P0.L.labaBersih]));

// ---- 39b no. 37 tinjauan U37-U2: bon yang DIHAPUS BUKU tidak pernah dibayar — kalimat tolak retur tidak boleh menyebut "sudah dibayar" atau menyuruh uang keluar
// laci lewat retur ketik tangan. ANGKA CONTOH: Uji Hapus bon 700.000 dihapus penuh; Uji Hapus Sebagian dihapus 600.000; Uji Campur dibayar 300.000 + dihapus 400.000.
var HB37 = function (id, tgl, nama, n) { return { koleksi: 'piutangMutasi', data: { id: id, tipe: 'hapusBuku', namaPelanggan: nama, nominal: n, tanggal: tgl, jam: '10:00', alasan: 'macet', dicatatDi: 'sistem' } }; };
var U2 = denganCacheSementara([KR37('h37a', '2026-09-10', 'Uji Hapus', 50, 700000, 650000), HB37(3801, '2026-09-12', 'Uji Hapus', 700000),
  KR37('h37b', '2026-09-10', 'Uji Hapus Sebagian', 50, 700000, 650000), HB37(3802, '2026-09-12', 'Uji Hapus Sebagian', 600000),
  KR37('h37c', '2026-09-10', 'Uji Campur', 50, 700000, 650000), BY37(3803, '2026-09-11', 'Uji Campur', 300000), HB37(3804, '2026-09-12', 'Uji Campur', 400000)], function () {
  return { a: susunRetur(RS37({ rtNotaId: 'h37a', ketik: '10' }), W37), b: susunRetur(RS37({ rtNotaId: 'h37b', ketik: '20' }), W37), c: susunRetur(RS37({ rtNotaId: 'h37c', ketik: '10' }), W37) }; });
ok('39b-37 U37-U2: bon DIHAPUS BUKU penuh — retur ditolak dengan kalimat "sudah DIHAPUS BUKU (Rp700.000), bukan dibayar", tanpa "sudah dibayar" dan tanpa jalan uang laci (retur ketik tangan)',
  !U2.a.dokumen && /sudah DIHAPUS BUKU \(Rp700\.000\), bukan dibayar/.test(U2.a.tolak || '') && /tidak ada uang yang dikembalikan/.test(U2.a.tolak || '') && !/sudah dibayar|Retur ketik tangan/.test(U2.a.tolak || ''), U2.a.tolak);
ok('39b-37 U37-U2: bon dihapus buku sebagian (sisa 100.000) — retur 20 kg ditolak "sebagian bonnya sudah DIHAPUS BUKU (Rp600.000), bukan dibayar", batas 7,14 kg tetap disebut, tanpa jalan uang laci',
  !U2.b.dokumen && /sebagian bonnya sudah DIHAPUS BUKU \(Rp600\.000\), bukan dibayar/.test(U2.b.tolak || '') && /paling banyak 7,14 kg/.test(U2.b.tolak || '') && !/sudah dibayar|Retur ketik tangan/.test(U2.b.tolak || ''), U2.b.tolak);
ok('39b-37 U37-U2: bon ditutup bayar 300.000 + hapus buku 400.000 — kalimat menyebut keduanya; uang kembali dari laci paling banyak sebesar yang memang dibayar',
  !U2.c.dokumen && /sudah tertutup \(dibayar Rp300\.000, DIHAPUS BUKU Rp400\.000\)/.test(U2.c.tolak || '') && /paling banyak sebesar yang memang dibayar/.test(U2.c.tolak || ''), U2.c.tolak);

// ---- 39b no. 37 tinjauan U37-U3: jalan "potong bon dulu, sisanya retur ketik tangan" untuk bon yang sebagian dibayar — kalimat menyebut batas ketik tangan apa
// adanya (karung utuh / setengah saja; tidak terikat ke nota, jadi jangan diretur lagi), dan pembulatan bon yang sudah tertutup bayar tidak membuat retur nota
// penuh ditolak. ANGKA CONTOH: Uji Sebagian (BASE37) bon 700.000 dibayar 500.000; Uji Dua bon 700.000 dibayar 350.000; Uji Bulat bon 700.500 (pembulatan 500) dibayar 200.
var U3 = denganCacheSementara(BASE37.concat([KR37('q37a', '2026-09-18', 'Uji Dua', 50, 700000, 650000), BY37(3911, '2026-09-18', 'Uji Dua', 350000),
  KR37('p37a', '2026-09-18', 'Uji Bulat', 50, 700500, 650000, { pembulatan: 500 }), BY37(3901, '2026-09-18', 'Uji Bulat', 200)]), function () {
  var bulat = susunRetur(RS37({ rtNotaId: 'p37a', ketik: '50' }), W37); var lembar = notaDitunjuk(RS37({ rtNotaId: 'p37a', ketik: '50' })); var dulu = susunRetur(RS37({ rtNotaId: 'p37a', ketik: '49,99' }), W37);
  return { pecahan: susunRetur(RS37({ rtNotaId: 'k37d', ketik: '50' }), W37), setengah: susunRetur(RS37({ rtNotaId: 'q37a', ketik: '50' }), W37), bulat: bulat,
    lembar: { nilai: lembar.nilai, sisa: lembar.bon.sisa }, sisaBulat: denganCacheSementara(bulat.dokumen || [], function () { return cariP37('uji bulat').sisa; }),
    ekor: denganCacheSementara(dulu.dokumen || [], function () { var e = susunRetur(RS37({ rtNotaId: 'p37a', ketik: '0,01' }), W37); return { sisa0: cariP37('uji bulat').sisa, e: e, sisa1: denganCacheSementara(e.dokumen || [], function () { return cariP37('uji bulat').sisa; }) }; }) }; });
ok('39b-37 U37-U3: bon sebagian dibayar, sisa barang 35,72 kg BUKAN kelipatan setengah karung — kalimat tidak menjanjikan retur ketik tangan, menyebut batasnya (karung utuh atau setengah, 25 kg)',
  !U3.pecahan.dokumen && /paling banyak 14,28 kg/.test(U3.pecahan.tolak || '') && /\(35,72 kg\) tidak bisa dicatat sebagai uang kembali di layar ini: retur ketik tangan hanya menerima karung utuh atau setengah \(25 kg\)/.test(U3.pecahan.tolak || '')
  && !/dikembalikan sebagai uang lewat/.test(U3.pecahan.tolak || ''), U3.pecahan.tolak);
ok('39b-37 U37-U3: sisa barang 25 kg = 0,5 karung — jalan ketik tangan disebut, dengan peringatan bahwa catatannya TIDAK mengurangi nota ini (jangan diretur lagi: barang yang sama kembali dua kali)',
  !U3.setengah.dokumen && /paling banyak 25 kg/.test(U3.setengah.tolak || '') && /\(25 kg = 0,5 karung\) dikembalikan sebagai uang lewat "Tidak ada notanya\? Retur ketik tangan"/.test(U3.setengah.tolak || '')
  && /TIDAK mengurangi nota ini, jadi sesudahnya jangan retur nota ini lagi untuk barang yang sama/.test(U3.setengah.tolak || ''), U3.setengah.tolak);
ok('39b-37 U37-U3: nota bon 50 kg ber-pembulatan 500 yang baru dibayar Rp200 — retur 50 kg DITERIMA, bon dipotong sebesar sisanya (700.300) dan jadi nol; lembar Retur menggambar angka potong yang sama (dulu ditolak dengan saran "paling banyak 50,02 kg")',
  !!U3.bulat.dokumen && U3.bulat.dokumen[0].data.potongBon === 700300 && U3.bulat.dokumen[1].data.nominal === 700300 && U3.sisaBulat === 0 && U3.lembar.nilai === 700300 && U3.lembar.sisa === 700300, J([U3.bulat.tolak, U3.sisaBulat, U3.lembar]));
ok('39b-37 U37-U3: sesudah 49,99 kg, sisa 0,01 kg (nilai 140 + pembulatan 500) atas bon Rp440 — DITERIMA, bon dipotong Rp440 dan jadi nol (dulu Rp440 tertinggal)',
  U3.ekor.sisa0 === 440 && !!U3.ekor.e.dokumen && U3.ekor.e.dokumen[0].data.potongBon === 440 && U3.ekor.sisa1 === 0, J([U3.ekor.sisa0, U3.ekor.e.tolak, U3.ekor.sisa1]));

// ---- 39b no. 37 tinjauan MM4: sisa bon lebih kecil dari satu satuan nota (1 unit kemasan / 0,01 kg) — kalimat tolak tidak menyarankan "paling banyak 0 unit"
// (mengetik 0 ditolak "Isi berapa unit"). ANGKA CONTOH: Uji Kecil kemasan Kembang 5 kg 1 unit 72.000 dibayar 68.200 (sisa 3.800); Uji Kecil Kg bon 700.000 dibayar 699.900.
var MM4 = denganCacheSementara([{ koleksi: 'penjualan', data: { id: 'm37a', trxId: 'Tm37a', tanggal: '2026-09-18', jam: '09:00', caraBayar: 'Kredit', namaPelanggan: 'Uji Kecil', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 72000, hppTotalSaatJual: 66000 } },
  BY37(3921, '2026-09-18', 'Uji Kecil', 68200), KR37('m37b', '2026-09-18', 'Uji Kecil Kg', 50, 700000, 650000), BY37(3922, '2026-09-18', 'Uji Kecil Kg', 699900)], function () {
  return { unit: susunRetur(RS37({ rtNotaId: 'm37a', ketik: '1' }), W37), kg: susunRetur(RS37({ rtNotaId: 'm37b', ketik: '1' }), W37) }; });
ok('39b-37 MM4: sisa bon Rp3.800 < harga 1 unit — kalimat menyebut retur nota ini tidak bisa memotong bon (bukan "paling banyak 0 unit"); bagian yang dibayar lewat retur ketik tangan per unit',
  !MM4.unit.dokumen && /Sisa bon itu lebih kecil dari harga 1 unit nota ini \(Rp72\.000\), jadi retur nota ini tidak bisa memotong bon/.test(MM4.unit.tolak || '') && !/paling banyak 0/.test(MM4.unit.tolak || '') && /\(1 unit\) dikembalikan sebagai uang lewat/.test(MM4.unit.tolak || ''), MM4.unit.tolak);
ok('39b-37 MM4: sisa bon Rp100 < harga 0,01 kg — sama untuk karung: tidak ada "paling banyak 0 kg"',
  !MM4.kg.dokumen && /lebih kecil dari harga 0,01 kg nota ini \(Rp140\)/.test(MM4.kg.tolak || '') && !/paling banyak 0 kg/.test(MM4.kg.tolak || ''), MM4.kg.tolak);

// ---- 39b no. 37 tinjauan MM3: nota bon milik pembeli yang bonnya sudah LUNAS — daftar Retur menandainya tak-bisa (dengan kalimat penolakannya) dan lembar tidak
// dibuka dengan janji "sisa bon Rp0, sesudah retur −Rp…"; dulu baru ditolak sesudah kg, alasan, kondisi diisi. Pembanding: nota bon yang bonnya masih ada tetap bisa.
var MM3 = denganCacheSementara(BASE37, function () { var dl = daftarNotaRetur({ sekarang: KINI, rtCari: 'uji' }); var cari = function (id) { return dl.find(function (x) { return x.id === id; }) || {}; };
  return { lunas: cari('k37c'), masih: cari('k37b'), lembar: notaDitunjuk(RS37({ rtNotaId: 'k37c', ketik: '10' })), kirim: susunRetur(RS37({ rtNotaId: 'k37c', ketik: '10' }), W37) }; });
ok('39b-37 MM3: daftar Retur — nota bon Uji Lunas (bon sudah lunas) tak-bisa dengan kalimat "sudah lunas … Retur ketik tangan"; nota bon Uji Retur (bon masih ada) tetap bisa, bertanda memotong bon',
  MM3.lunas.bisa === false && /Bon Uji Lunas sudah lunas — tidak ada bon yang bisa dipotong retur nota ini/.test(MM3.lunas.sebab || '') && /Retur ketik tangan/.test(MM3.lunas.sebab || '') && MM3.masih.bisa === true && MM3.masih.bon === true, J([MM3.lunas, MM3.masih]));
ok('39b-37 MM3: lembar Retur untuk nota itu tidak menggambar bon minus — notaDitunjuk tidak sah (kalimat yang sama), kiriman tetap ditolak tanpa dokumen',
  !!MM3.lembar && MM3.lembar.d.ok === false && /sudah lunas/.test(MM3.lembar.d.sebab || '') && !MM3.lembar.bon && !MM3.kirim.dokumen && /sudah lunas/.test(MM3.kirim.tolak || ''), J([MM3.lembar && MM3.lembar.d, MM3.kirim.tolak]));

// ---- 39b no. 37 tinjauan MM1: retur nota bon memadamkan NOTA ASALNYA dulu (notaAsalId mutasi retur = idTrx bon jual), baru sisanya ikut bon tertua dulu. Dulu
// memotong bon TERTUA: tagihan WA & umur bon menunjuk nota yang barangnya sudah kembali, bon lama yang barangnya masih dipegang hilang dari tagihan.
// ANGKA CONTOH: Uji Tua bon 31 Agu 300.000 dibayar 100.000 (1 Sep) + nota bon 18 Sep 280.000 (20 kg) — nota 18 Sep diretur penuh.
var MM1 = denganCacheSementara([KR37('t37a', '2026-08-31', 'Uji Tua', 20, 300000, 260000), BY37(3931, '2026-09-01', 'Uji Tua', 100000), KR37('t37b', '2026-09-18', 'Uji Tua', 20, 280000, 260000)], function () {
  var R = susunRetur(RS37({ rtNotaId: 't37b', ketik: '20' }), W37);
  return denganCacheSementara(R.dokumen || [], function () { var d = cariP37('uji tua'); var b = semuaBon(KINI).find(function (x) { return x.kunci === 'uji tua'; }) || {};
    return { tolak: R.tolak || '', sisa: d.sisa, tertua: d.tanggalTertua, umur: d.umurHari, umur31: Math.round((isoKeTanggal(tanggalLokalIso()) - isoKeTanggal('2026-08-31')) / 86400000), buka: (b.buka || []).map(function (u) { return [u.idTrx, u.sisa]; }), tagih: (pesanTagih(KINI, 'uji tua') || {}).teks || '',
      buku: ((susunBon(KINI, 'uji tua').buku || {}).halaman || []).filter(function (h) { return h.u === 0; }).map(function (h) { return [h.tgl, h.jenis]; }) }; }); });
ok('39b-37 MM1: retur penuh nota 18 Sep memotong NOTA ITU — sisa 200.000 tinggal di bon 31 Agu (rincian & Buku bon), umur bon dari 31 Agu, bukan dari nota yang barangnya sudah kembali',
  !MM1.tolak && MM1.sisa === 200000 && J(MM1.buka) === J([['t37a', 200000]]) && MM1.tertua === '2026-08-31' && MM1.umur === MM1.umur31 && J(MM1.buku) === J([[formatTanggal('2026-08-31'), 'bon'], [formatTanggal('2026-09-18'), 'coret']]), J(MM1));
var MM1b = denganCacheSementara([KR37('t37a', '2026-08-31', 'Uji Tua', 20, 300000, 260000), BY37(3931, '2026-09-01', 'Uji Tua', 100000), KR37('t37b', '2026-09-18', 'Uji Tua', 20, 280000, 260000),
  { koleksi: 'piutangMutasi', data: { id: 3932, tipe: 'retur', namaPelanggan: 'Uji Tua', nominal: 200000, tanggal: '2026-09-05', jam: '10:00', catatan: 'tanpa nota asal', dicatatDi: 'sistem' } }], function () {
  var d = cariP37('uji tua'); var b = semuaBon(KINI).find(function (x) { return x.kunci === 'uji tua'; }) || {}; return { sisa: d.sisa, tertua: d.tanggalTertua, buka: (b.buka || []).map(function (u) { return [u.idTrx, u.sisa]; }) }; });
ok('39b-37 MM1: mutasi retur 200.000 TANPA nota asal di buku ini tetap memadamkan bon tertua dulu (seperti bayar) — mesin & rincian: 31 Agu tertutup, umur bon dari 18 Sep (utuh 280.000)',
  MM1b.sisa === 280000 && MM1b.tertua === '2026-09-18' && J(MM1b.buka) === J([['t37b', 280000]]), J(MM1b));
ok('39b-37 MM1: tagihan WhatsApp menyebut bon 31 Agu (sisa 200.000), TIDAK menyebut nota 18 Sep yang barangnya sudah dikembalikan',
  MM1.tagih.indexOf(formatTanggal('2026-08-31')) >= 0 && MM1.tagih.indexOf(formatTanggal('2026-09-18')) < 0 && /Total sisa: Rp200\.000/.test(MM1.tagih), MM1.tagih);

// ---- 39b no. 37 tinjauan U37-U5: "diterima tunai" — margin yang dilepas retur nota bon diambil dari NOTA YANG DIRETUR (sama dengan mesin, MM1), bukan dari bon
// tertua; dulu pelanggan bersaldo awal (margin 0) membuat diterima tunai turun seukuran margin barang itu tanpa ada uang bergerak. ANGKA CONTOH: Uji Lama saldo
// awal 1.000.000 (1 Agu) + nota bon 18 Sep 700.000 (modal 650.000) diretur penuh; pembanding Uji Baru tanpa bon lama.
var U5 = function (awal, nama, id) { return denganCacheSementara(awal.concat([KR37(id, '2026-09-18', nama, 50, 700000, 650000)]), function () { var L0 = labaBulan('2026-09', KINI); var r = susunRetur(RS37({ rtNotaId: id, ketik: '50' }), W37);
  var L1 = denganCacheSementara(r.dokumen || [], function () { return labaBulan('2026-09', KINI); }); return { tolak: r.tolak || '', dLaba: L1.labaBersih - L0.labaBersih, diretur: L1.marginDiretur || 0, dTunai: L1.tunai - L0.tunai }; }); };
var U5a = U5([{ koleksi: 'piutangMutasi', data: { id: 3950, tipe: 'saldoAwal', namaPelanggan: 'Uji Lama', nominal: 1000000, tanggal: '2026-08-01', jam: '00:00', catatan: 'saldo awal' } }], 'Uji Lama', 'u5a'), U5b = U5([], 'Uji Baru', 'u5b');
ok('39b-37 U37-U5: retur penuh nota bon pelanggan bersaldo awal — laba bersih −50.000, margin yang dilepas retur 50.000 (nota itu), diterima tunai TIDAK bergerak (tidak ada uang); sama dengan pelanggan tanpa bon lama',
  !U5a.tolak && U5a.dLaba === -50000 && U5a.diretur === 50000 && U5a.dTunai === 0 && !U5b.tolak && U5b.dLaba === -50000 && U5b.diretur === 50000 && U5b.dTunai === 0, J([U5a, U5b]));

// ---- 39b no. 37 tinjauan U37-U6 (+ MM2): SISTEM LAMA (index.html, hanya-baca) — hitungPiutang sudah membaca retur, pembacanya ikut. rincianBelumLunas sistem lama
// (dipakai tagihan WhatsApp-nya) disalin APA ADANYA dari index.html oleh uji ini (rincianBelumLunasLAMA): Σ rincian = sisa mesin = rincian /baru/ (contoh A37 & MM1).
var U6 = function (dok, k) { return denganCacheSementara(dok, function () { var d = cariP37(k); var lama = rincianBelumLunasLAMA(d).map(function (r) { return r.sisa; }); var baru = rincianBelumLunas(d).map(function (r) { return r.sisa; });
  return { sisa: d.sisa, lama: lama, baru: baru, jumlahLama: lama.reduce(function (a, x) { return a + x; }, 0) }; }); };
var U6a = U6(BASE37.concat(A37.D), 'uji retur');
var U6b = denganCacheSementara([KR37('t37a', '2026-08-31', 'Uji Tua', 20, 300000, 260000), BY37(3931, '2026-09-01', 'Uji Tua', 100000), KR37('t37b', '2026-09-18', 'Uji Tua', 20, 280000, 260000)], function () {
  return U6(susunRetur(RS37({ rtNotaId: 't37b', ketik: '20' }), W37).dokumen || [], 'uji tua'); });
var U6c = U6([KR37('t37a', '2026-08-31', 'Uji Tua', 20, 300000, 260000), BY37(3931, '2026-09-01', 'Uji Tua', 100000), KR37('t37b', '2026-09-18', 'Uji Tua', 20, 280000, 260000),
  { koleksi: 'piutangMutasi', data: { id: 3932, tipe: 'retur', namaPelanggan: 'Uji Tua', nominal: 200000, tanggal: '2026-09-05', jam: '10:00', catatan: 'tanpa nota asal', dicatatDi: 'sistem' } }], 'uji tua');
ok('39b-37 U37-U6: sistem lama rincianBelumLunas (tagihan WA-nya) — Σ rincian = sisa mesin dan sama dengan rincian /baru/ sesudah retur nota bon (nota asal, juga retur tanpa nota asal; dulu lebih besar tepat sebesar retur)',
  U6a.jumlahLama === U6a.sisa && J(U6a.lama) === J(U6a.baru) && U6a.sisa === 920500 && U6b.jumlahLama === U6b.sisa && J(U6b.lama) === J(U6b.baru) && U6b.sisa === 200000
  && U6c.jumlahLama === U6c.sisa && J(U6c.lama) === J(U6c.baru) && U6c.sisa === 280000, J([U6a, U6b, U6c]));

// ==================== HARIAN ====================
var RH = rekapHari('2026-09-19');
var rekapHari0918 = rekapHari('2026-09-18');
ok('19 Sep: 4 nota (batal tidak ikut) · omzet 1.270.000 · tunai 370.000 · QRIS 600.000 · bon 300.000 · pembayaran bon 100.000 · keluar 1.800 (MDR) · kas bersih 1.068.200', RH.n === 4 && RH.omzet === 1270000 && RH.tunai === 370000 && RH.qris === 600000 && RH.kredit === 300000 && RH.pelunasan === 100000 && RH.keluarHarian === 1800 && RH.bersih === 1068200, J(RH));
ok('kas bersih = Σ masuk − Σ keluar (baris arus kas yang sama); per jam: jam 09 tiga nota, jam 10 satu', dekat(RH.masuk.reduce(function (a, x) { return a + x.nominal; }, 0) - RH.keluar.reduce(function (a, x) { return a + x.nominal; }, 0), RH.bersih) && RH.perJam.length === 2 && RH.perJam[0].jam === '09' && RH.perJam[0].n === 3 && RH.perJam[1].n === 1, J(RH.perJam));
ok('buku kas 19 Sep = baris daftarGerakanKas hari itu (5: 3 nota uang + pelunasan + MDR); 16 Sep sudah tutup hari 21:05, 19 Sep belum', RH.buku.length === daftarGerakanKas().filter(function (r) { return r.t === '2026-09-19'; }).length && RH.buku.length === 5 && !RH.tutup && rekapHari('2026-09-16').tutup.jam === '21:05', J(RH.buku.map(function (r) { return r.label; })));
var TR = teksRekapHari(RH, { nama: 'Toko Contoh' }); ok('teks WA: judul toko, omzet (4 nota), tunai, QRIS, bon, pembayaran bon, kas bersih, margin', /Rekap Toko Contoh — 19 Sep/.test(TR) && /Omzet: Rp1\.270\.000 \(4 nota\)/.test(TR) && /Bon \(belum jadi uang\): Rp300\.000/.test(TR) && /Pembayaran bon pelanggan: Rp100\.000/.test(TR) && /Kas bersih hari ini: Rp1\.068\.200/.test(TR) && /Margin kotor/.test(TR), TR);
// 39b no. 37 tinjauan U37-U4: rekap harian & teks WA MENUTUP bila ada retur nota BON (bon dipotong, bukan uang laci): omzet = tunai + QRIS + bon − refund − retur
// nota bon. Dulu baris "Refund & tukar retur" (refund kas = 0) tersaring dan selisihnya tidak disebut di mana pun. Pembanding: retur nota TUNAI tanpa baris baru.
var U4 = function (id) { return denganCacheSementara([], function () { var r = susunRetur(RS37({ rtNotaId: id, ketik: '5' }), W37); return denganCacheSementara(r.dokumen || [], function () { var R = rekapHari('2026-09-19');
  return { tolak: r.tolak || '', R: R, rb: lpReturBonHari(R), wa: teksRekapHari(R, { nama: 'Toko Contoh' }), tutup: R.omzet - (R.tunai + R.qris + R.kredit - R.refund - lpReturBonHari(R)) }; }); }); };
var U4b = U4('j5'), U4t = U4('j4');
ok('39b-37 U37-U4: retur 5 kg nota BON j5 — rekap menyebut "Retur nota bon (bon dipotong): Rp70.093" dan omzet = tunai + QRIS + bon − refund − retur nota bon (selisih 0); retur nota TUNAI j4 tanpa baris itu (refund-nya sudah menutup)',
  !U4b.tolak && U4b.rb === 70093 && U4b.R.refund === 0 && U4b.tutup === 0 && /Retur nota bon \(bon dipotong\): Rp70\.093/.test(U4b.wa) && !U4t.tolak && U4t.rb === 0 && U4t.tutup === 0 && !/Retur nota bon/.test(U4t.wa), J([U4b.rb, U4b.tutup, U4b.wa, U4t.rb, U4t.tutup]));
// 39b no. 37 tinjauan MM5: arus kas "Refund retur (N retur)" hanya menghitung retur yang mengeluarkan uang — retur nota BON (potong bon, nominalRefund 0) di hari
// yang sama dulu ikut terhitung (rupiahnya benar, jumlah kejadiannya salah). ANGKA CONTOH: retur 5 kg nota tunai j4 + retur 5 kg nota bon j5, 19 Sep.
var MM5 = denganCacheSementara([], function () { var a = susunRetur(RS37({ rtNotaId: 'j4', ketik: '5' }), W37); var b = susunRetur(RS37({ rtNotaId: 'j5', ketik: '5' }), W37);
  return denganCacheSementara((a.dokumen || []).concat(b.dokumen || []), function () { var K = hitungArusKasInti(function (t) { return t === '2026-09-19'; }, bayaranBiayaBulanan()); var R = rekapHari('2026-09-19');
    var baris = function (xs) { return xs.find(function (x) { return x.label === 'Refund retur'; }) || {}; };
    return { tolak: (a.tolak || '') + (b.tolak || ''), nRetur: ambilRetur().length, K: baris(K.keluar), R: baris(R.keluar) }; }); });
ok('39b-37 MM5: hari dengan 1 retur uang kembali + 1 retur nota bon — baris arus kas "Refund retur" = Rp70.225 dari 1 retur (bukan 2); kartu arus kas Harian sama',
  !MM5.tolak && MM5.nRetur === 2 && MM5.K.nominal === 70225 && MM5.K.n === 1 && MM5.R.n === 1, J(MM5));
var HT = hariTerakhir(KINI, 14); ok('14 hari terakhir, hari ini dulu; 19 Sep 4 nota, 18 Sep 1, 15 Sep 0 (sepi tetap ada)', HT.length === 14 && HT[0].iso === '2026-09-19' && HT[0].hariIni && HT[0].n === 4 && HT[1].n === 1 && HT[4].n === 0);
ok('39b-19 pemilih 14 hari: omzet tiap hari = omzet rekap harinya (penjualan − uang retur), bukan penjualan kotor', hariTerakhir(KINI, 14).every(function (x) { return x.omzet === rekapHari(x.iso).omzet; })
  && denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtL19', tanggal: '2026-09-18', jam: '09:00', nominalRefund: 12000, kondisi: 'utuh' } }], function () { var h = hariTerakhir(KINI, 14)[1]; return h.iso === '2026-09-18' && h.omzet === rekapHari('2026-09-18').omzet && h.omzet === HT[1].omzet - 12000; }),
  J(hariTerakhir(KINI, 3).map(function (x) { return [x.iso, x.omzet, rekapHari(x.iso).omzet]; })));
var N20 = function (id, merk) { return { koleksi: 'penjualan', data: { id: id, trxId: 'T20', tanggal: '2026-09-19', jam: '11:00', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'karung', merkSumber: merk, totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }; };
ok('39b-19 tinjauan v2: Laporan Harian menyebut uang retur hari itu (rekapHari.retur) → kalimat "penjualan − uang retur = omzet" menutup; tanpa retur = 0',
  rekapHari('2026-09-18').retur === 0 && denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtL19b', tanggal: '2026-09-18', jam: '09:00', nominalRefund: 12000, kondisi: 'utuh' } }], function () { var r = rekapHari('2026-09-18'); return r.retur === 12000 && r.omzet + r.retur === rekapHari0918.omzet; }),
  J(denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtL19b', tanggal: '2026-09-18', jam: '09:00', nominalRefund: 12000, kondisi: 'utuh' } }], function () { var r = rekapHari('2026-09-18'); return [r.retur, r.omzet, rekapHari0918.omzet]; })));
ok('39b-19 tinjauan v2: angka SEBELUM retur bernama "Penjualan terhitung" (Laba & laba-rugi berkop); "Omzet terhitung" cuma untuk angka sesudah retur (Banding) — satu kata, satu arti',
  denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtL19c', tanggal: '2026-09-18', jam: '09:00', nominalRefund: 12000, kondisi: 'utuh' } }], function () { var B = labaBulan('2026-09', KINI); var R = laporanBerkop('labarugi', '2026-09', 1, KINI); var BD = bandingLabaRugi('2026-09', '2026-08', KINI);
    var bR = (R.baris || []).filter(function (x) { return /terhitung/.test(x.nama || ''); }); return B.terjun[0].nama === 'Penjualan terhitung' && B.terjun[0].n === B.L.omzetHitung + B.L.returUang && bR.length === 1 && bR[0].nama === 'Penjualan terhitung (nota ber-HPP)' && BD.baris[0].nama === 'Omzet terhitung' && BD.baris[0].a === B.L.omzetHitung; }),
  J(denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtL19c', tanggal: '2026-09-18', jam: '09:00', nominalRefund: 12000, kondisi: 'utuh' } }], function () { var R = laporanBerkop('labarugi', '2026-09', 1, KINI); return [labaBulan('2026-09', KINI).terjun[0], (R.baris || []).map(function (x) { return x.nama; }).slice(0, 4), bandingLabaRugi('2026-09', '2026-08', KINI).baris[0]]; })));
var n20 = { h: rekapHari('2026-09-19').n, m: rekapMinggu('2026-09-14', KINI).n, b: enamBulan(KINI).daftar.slice(-1)[0].n, p: pjOmzetSistem('2026-09').n };
var N20g = function (id, grup) { return { koleksi: 'penjualan', data: { id: id, grupNota: grup, tanggal: '2026-09-19', jam: '12:00', caraBayar: 'Kredit', namaPelanggan: 'Uji Bon', jenis: 'karung', merkSumber: 'Angsa', totalKg: 50, beratKarungAcuan: 50, jumlahKarung: 1, hargaTotal: 700000, hppTotalSaatJual: 650000 } }; };
ok('tinjauan rantai laporan T2/T3: nota HP kasir (grupNota saja, tanpa trxId) dua baris BON = satu nota: Harian +1, "Bon … · N nota" WA +1 nota, kartu Laba "nota bon" +1, Tahun +1 (bukan +2)',
  (function () { var h0 = rekapHari('2026-09-19'), b0 = labaBulan('2026-09', KINI), t0 = rekapTahun ? rekapTahun('2026', KINI) : null; return denganCacheSementara([N20g('g20a', 'G20'), N20g('g20b', 'G20')], function () { var R = rekapHari('2026-09-19'); var B = labaBulan('2026-09', KINI); var T = rekapTahun ? rekapTahun('2026', KINI) : null;
    return R.n === h0.n + 1 && R.nKredit === h0.nKredit + 1 && new RegExp('· ' + R.nKredit + ' nota').test(teksRekapHari(R, { nama: 'Toko Contoh' })) && B.nKredit === b0.nKredit + 1 && (!T || T.n === t0.n + 1); }); })(),
  J(denganCacheSementara([N20g('g20a', 'G20'), N20g('g20b', 'G20')], function () { return [rekapHari('2026-09-19').n, rekapHari('2026-09-19').nKredit, labaBulan('2026-09', KINI).nKredit]; })));
ok('39b-20 satu nota DUA baris (trxId sama) dihitung SATU nota: Harian 4 → 5 (bukan 6), jam 11 satu nota, 14 hari, teks WA "(5 nota)", minggu, bulan & Pajak ikut +1 (dulu +2: baris disebut nota)',
  denganCacheSementara([N20('n20a', 'Angsa'), N20('n20b', 'Beo')], function () { var R = rekapHari('2026-09-19'); var j11 = R.perJam.filter(function (x) { return x.jam === '11'; })[0];
    return R.n === n20.h + 1 && !!j11 && j11.n === 1 && hariTerakhir(KINI, 14)[0].n === n20.h + 1 && /\(5 nota\)/.test(teksRekapHari(R, { nama: 'Toko Contoh' })) && rekapMinggu('2026-09-14', KINI).n === n20.m + 1
      && enamBulan(KINI).daftar.slice(-1)[0].n === n20.b + 1 && pjOmzetSistem('2026-09').n === n20.p + 1; }),
  J(denganCacheSementara([N20('n20a', 'Angsa'), N20('n20b', 'Beo')], function () { return [rekapHari('2026-09-19').n, rekapMinggu('2026-09-14', KINI).n, pjOmzetSistem('2026-09').n, n20]; })));

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
ok('NPWP (owner 24 Sep): kolom tersimpan, tapi BAWAAN tidak dicetak di kop mana pun (penuh maupun ringkas); alamat + telepon digabung', ID.npwp === '1234567890123456' && ID.npwpDiKop === false && kopUntuk('penuh').resmi.indexOf('NPWP') < 0 && kopUntuk('ringkas').resmi === '' && kopUntuk('ringkas').alamat === 'Jl. Contoh Raya No. 12 · 0812-0000-0000', J([kopUntuk('penuh').resmi]));
ok('NPWP 16 angka → peringatan kalimat owner persis; 15 angka / kosong → tanpa peringatan', peringatanNpwp('1234567890123456') === 'NPWP orang pribadi = NIK; mencetaknya membuka NIK ke semua pembeli.' && peringatanNpwp('12.345.678.9-012.345') === '' && peringatanNpwp('') === '');
var dokIdLama = JSON.parse(JSON.stringify(ugAturDok('identitas'))), dokStrukLama = JSON.parse(JSON.stringify(ugAturDok('struk')));   // dipulihkan sesudahnya — uji di bawah memakai kop v1
var RN = tulis(susunIdentitas({ npwpDiKop: true }, W));
ok('owner menyalakan "cetak di kop penuh" = versi kop baru; kop penuh menyebut NPWP, kop ringkas TETAP tidak; kabarnya membawa peringatan NIK (16 angka)', identitasUsaha().npwpDiKop === true && /NPWP 1234567890123456/.test(kopUntuk('penuh').resmi) && kopUntuk('ringkas').resmi === '' && /membuka NIK/.test(RN.patch.kabar) && RN.patch.kabarAwas === true && identitasUsaha().versi === 2, J([RN.patch.kabar]));
terapkanKeCache([{ koleksi: 'aturanToko', data: dokIdLama }, { koleksi: 'aturanToko', data: dokStrukLama }]); ID = identitasUsaha();
var PK = pakaiKop(); ok('ragam bawaan: nota/kartu/slip/harian ringkas, laporan/omzet/bon/setor penuh; nomor awal 1', PK.pakai.nota === 'ringkas' && PK.pakai.laporan === 'penuh' && PK.pakai.setor === 'penuh' && PK.nomorAwal === 1 && !PK.dariOwner);
tulis(susunAturDokumen({ pakai: { nota: 'penuh' }, nomorAwal: '100' }, W)); ok('putar nota → penuh; nomor awal 100 → nomor berikutnya 100', pakaiKop().pakai.nota === 'penuh' && pakaiKop().pakai.kartu === 'ringkas' && nomorBerikut() === 100);

// ==================== CETAKAN BERNOMOR ====================
var C1 = tulis(susunCetakan({ jenis: 'labarugi', judul: 'Laporan Laba-Rugi', periode: 'September 2026', draf: true }, 'cetak', W));
ok('cetakan pertama No. 100: dokumenCetak {nomor 100, jenis, judul, cara cetak, kopVersi 1, draf}; berikutnya 101; riwayat menyebutnya', C1.nomor === 100 && C1.dokumen[0].koleksi === 'dokumenCetak' && C1.dokumen[0].data.kopVersi === 1 && C1.dokumen[0].data.draf === true && nomorBerikut() === 101 && riwayatCetakan(3)[0].nomor === 100 && /DRAF/.test(riwayatCetakan(3)[0].teks), J(C1));
ok('cara keluar asing ditolak; nomor awal ≤ nomor terpakai ditolak', /tidak dikenal/.test(susunCetakan({ jenis: 'x', judul: 'x' }, 'fax', W).tolak) && /sudah terpakai/.test(susunAturDokumen({ nomorAwal: '50' }, W).tolak));

// ==================== DK2 · LAPORAN BERKOP ====================
var LR = laporanBerkop('labarugi', '2026-09', 1, KINI);
ok('laba-rugi Sep: DRAF (belum tutup buku), baris Laba kotor 146.300 & Laba bersih = mesin, potongan QRIS 1.800 dipisah, kop penuh v1 (tanpa NPWP — bawaan tidak dicetak), tidak ditolak', LR.cap === 'DRAF' && !LR.final && LR.baris.find(function (r) { return r.nama === 'Laba kotor'; }).n === 146300 && LR.baris.find(function (r) { return r.nama === 'Laba bersih'; }).n === LM.labaBersih && LR.baris.find(function (r) { return /Potongan QRIS/.test(r.nama); }).n === -1800 && LR.kop.versi === 1 && LR.kop.ragam === 'penuh' && LR.kop.resmi.indexOf('NPWP') < 0 && !LR.tolak, J(LR.baris));
var M24 = [{ koleksi: 'pengeluaranHarian', data: { id: 'h24', kategori: 'toko', tanggal: '2026-09-19', jam: '21:00', keterangan: 'Potongan QRIS GoPay', nominal: 700 } }];
ok('39b-24 catatan potongan QRIS yang DIKETIK tangan (tanpa tanda mdr): laba-rugi berkop memisahnya (1.800 + 700 = 2.500), pilah harian ikut, Laba bersih tetap = mesin — satu pengenal dengan Kendali Biaya',
  denganCacheSementara(M24, function () { var R = laporanBerkop('labarugi', '2026-09', 1, KINI); var q = R.baris.find(function (r) { return /Potongan QRIS/.test(r.nama); }); var P = pilahHarian('2026-09-01', '2026-09-30');
    return !!q && q.n === -2500 && P.mdr === 2500 && R.baris.find(function (r) { return r.nama === 'Laba bersih'; }).n === hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih && adalahMdr(M24[0].data) && !adalahMdr({ keterangan: 'isi saldo qris' })
      && !adalahMdr({ keterangan: 'Biaya admin Admin Mdr — bayar bon MDR Jaya', dariBayarBon: true }) && !adalahMdr({ keterangan: 'Biaya admin Mdr — pindah uang ke rekening', dariPindah: true }) && !adalahMdr({ keterangan: 'mdrx kantong' }) && adalahMdr({ keterangan: 'Potongan MDR Qris Gopay E-Wallet' }); }),
  J(denganCacheSementara(M24, function () { return [laporanBerkop('labarugi', '2026-09', 1, KINI).baris.filter(function (r) { return /Potongan|Laba bersih|Belanja/.test(r.nama); }), pilahHarian('2026-09-01', '2026-09-30').mdr]; })));
ok('laba-rugi menutup: Σ baris berangka (tanpa dua baris jumlah) = laba bersih', dekat(LR.baris.filter(function (r) { return r.n !== null && r.kelas !== 'jumlah'; }).reduce(function (a, r) { return a + r.n; }, 0), LM.labaBersih));
var LR3 = laporanBerkop('labarugi', '2026-09', 3, KINI); ok('3 bulan Jul–Sep: periode "Jul 26 – Sep 26", laba kotor = Agu 50.000 + Sep 146.300', LR3.periode === 'Jul 26 – Sep 26' && LR3.bulan.length === 3 && LR3.baris.find(function (r) { return r.nama === 'Laba kotor'; }).n === 196300);
// ---- 39b no. 40 (owner 30 Sep): Juli SEBELUM awal buku (catatan pertama 20 Agu) tetap tampil dengan keterangan, tidak dijumlah sebagai bulan rugi
var M40 = [{ koleksi: 'biayaBulanan', data: { id: '2026-07', bulan: '2026-07', listrik: 300000, internet: 0, akses: 0, keamanan: 0, tanggalBayarPos: { listrik: '2026-07-10' }, rincianGaji: [], gaji: 0, gajiHariOrang: 0 } },
  { koleksi: 'pengeluaranHarian', data: { id: 'h40', kategori: 'toko', tanggal: '2026-07-28', jam: '10:00', keterangan: 'Bensin antar', nominal: 20000 } }];
var C40 = denganCacheSementara(M40, function () { return { R: laporanBerkop('labarugi', '2026-09', 3, KINI), T: rekapTahun(2026, KINI), jul: hitungLabaBersihRentang('2026-07-01', '2026-07-31').labaBersih, agsep: hitungLabaBersihRentang('2026-08-01', '2026-09-30').labaBersih }; });
var lb40 = C40.R.baris.find(function (r) { return r.nama === 'Laba bersih'; });
ok('39b-40 laba-rugi berkop 3 bulan: periode tetap "Jul 26 – Sep 26" (Juli tampil), baris pertama "Jul 26 · sebelum awal buku — tidak dijumlah" tanpa angka; Laba bersih = mesin Agu–Sep (biaya Juli 320.000 bukan rugi); catatan menyebut biaya Juli; baris berangka menutup',
  C40.jul === -320000 && C40.R.periode === 'Jul 26 – Sep 26' && C40.R.baris[0].nama === 'Jul 26 · sebelum awal buku — tidak dijumlah' && C40.R.baris[0].n === null && lb40.n === C40.agsep && lb40.n !== C40.agsep + C40.jul
    && /Jul 26 sebelum awal buku \(catatan pertama 20 Agu 2026\) — tampil, tidak dijumlah: .*biaya Rp320\.000/.test(C40.R.catatan) && dekat(C40.R.baris.filter(function (r) { return r.n !== null && r.kelas !== 'jumlah'; }).reduce(function (a, r) { return a + r.n; }, 0), C40.agsep), J([C40.jul, C40.agsep, C40.R.baris[0], lb40, C40.R.catatan]));
ok('39b-40 Tahunan: Juli tetap di daftar (sebelumBuku, laba bersih −320.000 tetap terbaca) tetapi Σ laba bersih & biaya tahun = bulan sejak awal buku (Agu & Sep); Agustus bukan sebelum buku; keterangan "Jan – Jul sebelum awal buku … biaya Rp320.000"',
  C40.T.bulan[6].sebelumBuku === true && C40.T.bulan[6].labaBersih === -320000 && C40.T.bulan[7].sebelumBuku === false && C40.T.labaBersih === C40.agsep && C40.T.labaBersih === C40.T.bulan.filter(function (b) { return !b.sebelumBuku; }).reduce(function (a, b) { return a + b.labaBersih; }, 0)
    && C40.T.biaya === C40.T.bulan[7].biaya + C40.T.bulan[8].biaya && /^Jan – Jul sebelum awal buku .*biaya Rp320\.000/.test(C40.T.sebelumBuku) && rekapTahun(2026, KINI).sebelumBuku.indexOf('biaya') < 0, J([C40.T.labaBersih, C40.agsep, C40.T.sebelumBuku, C40.T.bulan[6]]));
var LN = laporanBerkop('neraca', '2026-09', 1, KINI); ok('neraca berkop: per 19 Sep (bulan berjalan dipotong hari ini), Jumlah harta = Jumlah kewajiban & modal, catatan menyebut aset = kewajiban + modal + laba ditahan', /per 19 Sep/.test(LN.sub) && LN.baris.find(function (r) { return r.nama === 'Jumlah harta'; }).n === LN.baris.find(function (r) { return r.nama === 'Jumlah kewajiban & modal'; }).n && /Aset Rp/.test(LN.catatan) && !LN.tolak, J(LN.baris));
var LA = laporanBerkop('aruskas', '2026-09', 1, KINI); var kasAkhir = LA.baris[LA.baris.length - 1];
ok('arus kas Sep: kas awal 31 Agu SEBELUM titik kas → belum bisa dihitung (null, disebut); kas akhir = kasPada() (= kas neraca); kas bersih = Σ masuk − Σ keluar', LA.baris[0].n === null && /belum bisa dihitung/.test(LA.baris[0].nama) && kasAkhir.n === kasPada() && /kas di neraca/.test(LA.catatan) && dekat(LA.baris.find(function (r) { return r.nama === 'Kas bersih periode'; }).n, LA.baris.filter(function (r) { return r.n !== null && r.kelas !== 'jumlah' && r.nama !== LA.baris[0].nama && !/Penyesuaian/.test(r.nama); }).reduce(function (a, r) { return a + r.n; }, 0)), J(LA.baris));
var BD = bandingLabaRugi('2026-09', '2026-08', KINI); ok('banding Sep vs Agu: laba kotor 146.300 vs 50.000, selisih +96.300 (+193%), arah naik', BD.baris[2].a === 146300 && BD.baris[2].b === 50000 && BD.baris[2].d === 96300 && BD.baris[2].pct === 193 && BD.baris[2].arah === 'naik' && /\+96\.300/.test(BD.baris[2].teksD), J(BD.baris[2]));
// ---- 39b no. 36 (owner 30 Sep): neraca & arus kas bulan FINAL memakai hitungan fisik tutup hari akhir bulan (kolom `titik` dokumen tutupHari), bukan kasPada
//      yang mundur dari titik kas sekarang (15 Sep 2026 — selalu lebih muda dari bulan final). ANGKA CONTOH: tutup hari 30 Sep 2025 Σ 7.000.000 · 30 Des Σ 7.300.000 · 31 Des Σ 7.500.000.
var PALL = { labarugi: true, neraca: true, aruskas: true, omzet: true }; var PB0 = paketBank(PALL, KINI); var LN0 = laporanBerkop('neraca', '2025-12', 1, KINI); var LA0 = laporanBerkop('aruskas', '2025-12', 3, KINI);
ok('39b-36 bulan final Des 2025 TANPA tutup hari: paket bank DITOLAK menyebut neraca & sebab yang benar; neraca & arus kas berkop ditolak dengan kalimat yang sama — bukan "titik kas belum disetel" (titik kas ada, cuma lebih muda)',
  PB0.tolak.indexOf('Laporan Neraca: Kas akhir Desember 2025 belum bisa dihitung — tidak ada tutup hari di Desember 2025') === 0 && LN0.final && LN0.tolak === LA0.tolak && /^Kas akhir Desember 2025 belum bisa dihitung — tidak ada tutup hari di Desember 2025\. Bulan final memakai hitungan fisik tutup hari akhir bulan/.test(LN0.tolak)
    && !/belum disetel/.test(PB0.tolak + LN0.tolak + LN0.catatan + LA0.tolak + LA0.catatan + LA0.baris[0].nama) && /tidak ada tutup hari di September 2025/.test(LA0.baris[0].nama) && LA0.baris[0].n === null, J([PB0.tolak, LN0.tolak, LN0.catatan, LA0.tolak, LA0.catatan, LA0.baris[0]]));
var tt36 = function (id, tgl, laci, amplop, brankas) { return { koleksi: 'tutupHari', data: { id: id, tanggal: tgl, jam: '21:00', selisihLaci: 0, titik: { laci: laci, rekening: 2000000, amplop: amplop, brankas: brankas } } }; };
var TH36 = [tt36('th-250930', '2025-09-30', 1500000, 500000, 3000000), tt36('th-251230', '2025-12-30', 1000000, 300000, 4000000), tt36('th-251231', '2025-12-31', 1200000, 300000, 4000000)];
var kas36 = function (D) { return D.baris.find(function (r) { return /^Kas \(laci/.test(r.nama); }).n; };
var C36 = denganCacheSementara(TH36, function () { return { P: paketBank(PALL, KINI), N: laporanBerkop('neraca', '2025-12', 1, KINI), A: laporanBerkop('aruskas', '2025-12', 3, KINI), kp: kasPada('2025-12-31'), ND: neracaPada('2025-12-31', KINI), NK: neracaPada('2025-12-31', KINI, lpKasAkhirBulan('2025-12')) }; });
var PB = C36.P; var akA36 = C36.A.baris[C36.A.baris.length - 1], pyA36 = C36.A.baris.find(function (r) { return /Penyesuaian/.test(r.nama); });
ok('paket bank (tutup hari akhir bulan ada): bulan final terakhir Des 2025 → 4 dokumen semua final, tidak ditolak; laba-rugi 3 bulan Okt–Des 2025; neraca per akhir Des 2025', !PB.tolak && PB.daftar.length === 4 && PB.daftar[0].periode === 'Okt 25 – Des 25' && PB.daftar[0].final && PB.daftar[1].jenis === 'neraca' && /31 Des/.test(PB.daftar[1].sub) && PB.daftar[3].jenis === 'omzet' && PB.daftar.every(function (d) { return !d.tolak; }), J(PB.daftar.map(function (d) { return [d.jenis, d.periode, d.final, d.tolak]; })));
ok('39b-36 neraca Des 2025 (final): kas = hitungan tutup hari TERAKHIR bulan itu (31 Des, 7.500.000 — bukan 30 Des 7.300.000), jumlah harta = kewajiban & modal, catatan menyebut sumbernya (aset = kas + aset tetap 5.000.000 isian owner di atas); kekayaan (total) dari kas yang sama, bentuk objek neraca tetap; mesin tidak diubah (kasPada 31 Des tetap null, neraca per tanggal bawaan tetap memakai mesin)',
  kas36(C36.N) === 7500000 && !C36.N.tolak && C36.N.baris.find(function (r) { return r.nama === 'Jumlah harta'; }).n === C36.N.baris.find(function (r) { return r.nama === 'Jumlah kewajiban & modal'; }).n && /^Kas Rp7\.500\.000 = hitungan fisik tutup hari 31 Des 2025\. Aset Rp12\.500\.000 = /.test(C36.N.catatan)
    && C36.kp === null && C36.ND.N.kas === null && /titik kas belum disetel/.test(C36.ND.tolak)
    && C36.NK.N.kas === 7500000 && C36.NK.total === Math.round(7500000 + C36.NK.N.stok + C36.NK.N.piutang + C36.NK.N.kasbon - C36.NK.N.utangOwner - C36.NK.N.utangPemasok) && Object.keys(C36.NK).join() === Object.keys(C36.ND).join(), J([kas36(C36.N), C36.N.catatan, C36.kp, C36.ND.tolak, C36.NK.total]));
ok('39b-36 arus kas Okt–Des 2025 (final): kas awal = tutup hari 30 Sep 7.000.000, kas akhir = kas neraca 7.500.000 (satu sumber), kas bersih 0 → penyesuaian 500.000 disebut, catatan menyebut hitungan fisik tutup hari 31 Des',
  C36.A.baris[0].n === 7000000 && C36.A.baris[0].nama === 'Kas awal periode' && akA36.n === 7500000 && akA36.n === kas36(C36.N) && !!pyA36 && pyA36.n === 500000 && !C36.A.tolak && /kas di neraca \(hitungan fisik tutup hari 31 Des 2025\)/.test(C36.A.catatan), J([C36.A.baris, C36.A.catatan]));
// tinjauan 39b UU36-1: penyesuaian yang = selisih laci tutup hari di dalam periode bernama "Lebih/kurang kas" (= laba-rugi, no. 38), bukan "bukan uang yang bergerak";
//      sisanya tetap penyesuaian titik kas. ANGKA CONTOH: tutup 30 Des LEBIH 300.000 + 31 Des LEBIH 200.000 (= seluruh penyesuaian 500.000); campuran: hanya 31 Des 200.000.
var s36 = function (x, n) { return { koleksi: x.koleksi, data: Object.assign({}, x.data, { selisihLaci: n }) }; };
var A36s = denganCacheSementara([TH36[0], s36(TH36[1], 300000), s36(TH36[2], 200000)], function () { return laporanBerkop('aruskas', '2025-12', 3, KINI); });
var A36m = denganCacheSementara([TH36[0], TH36[1], s36(TH36[2], 200000)], function () { return laporanBerkop('aruskas', '2025-12', 3, KINI); });
var cari36 = function (A, re) { return A.baris.filter(function (r) { return re.test(r.nama); }); };
ok('UU36-1 arus kas berkop Okt–Des 2025 (final): penyesuaian 500.000 yang seluruhnya selisih laci tutup hari (30 Des +300.000, 31 Des +200.000) = baris "Lebih/kurang kas · selisih laci tutup hari (2 malam)" (nama laba-rugi), tanpa baris "Penyesuaian titik kas"; catatan "dibukukan di laba-rugi sebagai Lebih/kurang kas", bukan "bukan uang yang bergerak"; kas akhir tetap 7.500.000; campuran (31 Des 200.000 saja): Lebih/kurang kas 200.000 + Penyesuaian titik kas 300.000, catatan menyebut keduanya',
  cari36(A36s, /^Lebih\/kurang kas/).length === 1 && cari36(A36s, /^Lebih\/kurang kas/)[0].nama === 'Lebih/kurang kas · selisih laci tutup hari (2 malam)' && cari36(A36s, /^Lebih\/kurang kas/)[0].n === 500000 && cari36(A36s, /Penyesuaian/).length === 0
    && /Lebih\/kurang kas Rp500\.000 = selisih hitungan uang tutup hari di dalam periode, dibukukan di laba-rugi sebagai Lebih\/kurang kas\./.test(A36s.catatan) && !/bukan uang yang bergerak/.test(A36s.catatan) && A36s.baris[A36s.baris.length - 1].n === 7500000 && !A36s.tolak
    && cari36(A36m, /^Lebih\/kurang kas/).length === 1 && cari36(A36m, /^Lebih\/kurang kas/)[0].n === 200000 && cari36(A36m, /Penyesuaian/).length === 1 && cari36(A36m, /Penyesuaian/)[0].n === 300000
    && /Lebih\/kurang kas Rp200\.000 = /.test(A36m.catatan) && /Penyesuaian Rp300\.000 = titik kas yang disetel ulang/.test(A36m.catatan) && A36m.baris[A36m.baris.length - 1].n === 7500000,
  J([A36s.baris, A36s.catatan, A36m.baris, A36m.catatan]));
// tinjauan 39b UU36-2: Laporan → Neraca dengan tanggal di bulan FINAL (layar & kertas yang dikeluarkan) — akhir bulan = hitungan tutup hari akhir bulan (sama dengan
//      Dokumen → Neraca); tanggal lain yang kasnya tidak terhitung mesin ditolak dengan sebab yang benar, bukan "titik kas belum disetel"; bulan draf tidak berubah.
var NT = typeof neracaTanggal === 'function' ? neracaTanggal : null;
var C36t = denganCacheSementara(TH36, function () { return { akhir: NT && NT('2025-12-31', KINI, true), tengah: NT && NT('2025-12-15', KINI, true), dok: laporanBerkop('neraca', '2025-12', 1, KINI) }; });
ok('UU36-2 layar Neraca 31 Des 2025 (bulan final): kas 7.500.000 dari hitungan tutup hari 31 Des, jumlah harta = Dokumen → Neraca, tidak ditolak; 15 Des 2025 (final, titik kas sekarang lebih muda): kas tidak dihitung, tolak "Kas per 15 Des 2025 belum bisa dihitung — bulan Desember 2025 sudah final … ada di Dokumen", tanpa "titik kas belum disetel" (tolak, keterangan baris kas, catatan); hari bulan draf = neracaPada apa adanya',
  !!NT && C36t.akhir.N.kas === 7500000 && !C36t.akhir.tolak && C36t.akhir.aset === C36t.dok.baris.find(function (r) { return r.nama === 'Jumlah harta'; }).n
    && C36t.tengah.N.kas === null && C36t.tengah.total === null && /^Kas per 15 Des 2025 belum bisa dihitung — bulan Desember 2025 sudah final dan titik kas sekarang lebih muda\. Neraca akhir Desember 2025 \(hitungan fisik tutup hari akhir bulan\) ada di Dokumen/.test(C36t.tengah.tolak)
    && !/belum disetel/.test(C36t.tengah.tolak + ' ' + C36t.tengah.harta[0].ket + ' ' + C36t.tengah.catatan) && J(NT('2026-09-19', KINI, false)) === J(neracaPada('2026-09-19', KINI)),
  J(NT ? [C36t.akhir.N.kas, C36t.akhir.tolak, C36t.tengah.tolak, C36t.tengah.harta[0], C36t.tengah.catatan] : 'neracaTanggal tidak ada'));
var G36 = [TH36[0], TH36[1], { koleksi: 'pengeluaranHarian', data: { id: 'h36', kategori: 'toko', tanggal: '2025-12-31', jam: '10:00', keterangan: 'Bensin antar', nominal: 50000 } }, { koleksi: 'tutupHari', data: { id: 'th-251215', tanggal: '2025-12-15', jam: '21:00', selisihLaci: 0 } }];
var N36g = denganCacheSementara(G36, function () { return laporanBerkop('neraca', '2025-12', 1, KINI); }); var N36l = denganCacheSementara([{ koleksi: 'tutupHari', data: { id: 'th-251215', tanggal: '2025-12-15', jam: '21:00', selisihLaci: 0 } }], function () { return laporanBerkop('neraca', '2025-12', 1, KINI); });
ok('39b-36 tutup hari terakhir 30 Des + uang keluar 31 Des 50.000: kas akhir = 7.300.000 − 50.000 (catatan sesudahnya ikut, disebut); bulan yang tutup harinya belum menyimpan isi tempat uang (tutup hari lama) ditolak dengan kalimatnya sendiri',
  kas36(N36g) === 7250000 && /hitungan fisik tutup hari 30 Des 2025 \+ catatan uang sesudahnya sampai 31 Des 2025/.test(N36g.catatan) && /^Kas akhir Desember 2025 belum bisa dihitung — tutup hari Desember 2025 belum menyimpan isi tempat uang sesudah tutup/.test(N36l.tolak), J([kas36(N36g), N36g.catatan, N36l.tolak]));
ok('paket tanpa pilihan ditolak', /Pilih isi/.test(paketBank({}, KINI).tolak));

// ==================== DK4 · DOKUMEN KECIL ====================
var DS = dokumenKecil('setor', null, '', KINI); ok('setor: 1 pilihan (25.000.000, 8 Agu), baris Jumlah 25.000.000, kop penuh, angka "dari catatan Owner & toko"', DS.pilihan.length === 1 && DS.baris[DS.baris.length - 1].n === 25000000 && DS.baris[DS.baris.length - 1].kelas === 'jumlah' && DS.ragam === 'penuh' && /Owner & toko/.test(DS.identitas) && !DS.tolak, J(DS));
var DU = dokumenKecil('upah', null, '', KINI); ok('slip upah: pilihan dari buku bulanan lama (Ben 1.560.000, Gama 600.000), baris menyebut "sistem lama", kop ringkas', DU.pilihan.length === 2 && DU.baris[DU.baris.length - 1].n === 1560000 && /sistem lama/.test(DU.identitas) && DU.ragam === 'ringkas' && !DU.tolak, J(DU));
var DP = dokumenKecil('piutang', null, '', KINI); ok('kartu piutang Bu Contoh: bon 300.000 (19 Sep) → bayar 100.000 → sisa 200.000; saldo berjalan tiap baris; identitas "Sisa Rp200.000 = bon Rp300.000 − bayar Rp100.000"; sisa = mesin', DP.pilihan[0].nama === 'Bu Contoh' && DP.baris.length === 3 && DP.baris[0].saldo === 300000 && DP.baris[1].saldo === 200000 && DP.baris[2].n === 200000 && /Sisa Rp200\.000 = bon Rp300\.000 − bayar Rp100\.000/.test(DP.identitas) && !DP.tolak && DP.adaSaldo, J(DP));
var DB = dokumenKecil('bon', null, '', KINI); ok('rekap bon RODA CONTOH: bon 20.000.000 − dibayar 5.000.000 = sisa 15.000.000 = mesin utang pemasok', DB.pilihan[0].nama === 'RODA CONTOH' && DB.pilihan[0].n === 15000000 && DB.baris[DB.baris.length - 1].n === 15000000 && /Sisa Rp15\.000\.000 = bon Rp20\.000\.000 − dibayar Rp5\.000\.000/.test(DB.identitas) && !/mesin utang pemasok menyebut/.test(DB.identitas), J(DB));
var DN = daftarNota('', KINI, 40); ok('nota 60 hari terakhir: 8 nota (Agu ikut, j6 batal ikut bertanda), terbaru dulu; cari "contoh" → 1 (Bu Contoh)', DN.daftar.length === 8 && DN.daftar[0].id === 'j7' && DN.daftar.some(function (x) { return x.id === 'j6' && x.batal; }) && daftarNota('contoh', KINI).cocok === 1, J(DN.daftar.map(function (x) { return x.id; })));
var DNK = dokumenKecil('nota', null, '', KINI); ok('nota belum dipilih → tolak "Pilih notanya"; sub menyebut 8 nota cocok', /Pilih notanya/.test(DNK.tolak) && DNK.cocokN === 8);
DNK = dokumenKecil('nota', 't:t4', '', KINI); ok('nota j4 (Tunai 250.000): cap SALINAN ke-1, baris dari penyusun struk (TOTAL 250.000), kop nota kini penuh (diputar), teks struk ada', DNK.cap === 'SALINAN ke-1' && DNK.salinanKe === 1 && DNK.baris.some(function (b) { return /TOTAL/i.test(b.nama) && b.n === 250000; }) && DNK.ragam === 'penuh' && /250\.000/.test(DNK.teksTambahan) && !DNK.tolak, J(DNK));
// audit 39b no. 8 (tinjauan 30 Sep): Pusat Dokumen hanya memakai baris struk yang berangka — tanggal saldo bon ikut di label barisnya
var DN5 = dokumenKecil('nota', 't:t5', '', KINI); var bSisa5 = DN5.baris.filter(function (b) { return /^Sisa bon Bu Contoh/.test(b.nama); });
ok('39b-8 nota BON j5 di Pusat Dokumen: baris "Sisa bon Bu Contoh · per <tanggal dokumen disusun>" (saldo dihitung saat disusun, bukan saat nota ditulis)', bSisa5.length === 1 && bSisa5[0].nama === 'Sisa bon Bu Contoh \u00b7 per ' + formatTanggal(hariIniIso(KINI)) && bSisa5[0].n !== null, JSON.stringify(DN5.baris));
tulis(susunCetakan({ jenis: 'nota', judul: 'Nota', periode: '19 Sep', trxId: DNK.trxId, salinanKe: DNK.salinanKe }, 'wa', W));
ok('sesudah dikirim: salinan berikutnya ke-2; nota lain tetap ke-1; nota batal j6 DITOLAK dicetak ulang, cap DIBATALKAN', dokumenKecil('nota', 't:t4', '', KINI).cap === 'SALINAN ke-2' && dokumenKecil('nota', 't:t3', '', KINI).cap === 'SALINAN ke-1' && /dibatalkan/.test(dokumenKecil('nota', 't:t6', '', KINI).tolak) && dokumenKecil('nota', 't:t6', '', KINI).cap === 'DIBATALKAN');
var TD = teksDokumen(DP, 101, '2026-09-19'); ok('teks dokumen: kop (nama huruf besar, alamat), judul, baris + saldo, identitas, No. 101 · kop v1', /^TOKO BERAS M\.IQBAL\nJl\. Contoh Raya/.test(TD) && /KARTU PIUTANG/.test(TD) && /\(saldo Rp300\.000\)/.test(TD) && /Sisa Rp200\.000 = bon/.test(TD) && /No\. 101 · kop v1 · 19 Sep/.test(TD), TD);
// ==================== PUTARAN 21 (owner 23 Sep): MINGGUAN (Senin–Minggu) & TAHUNAN ====================
ok('minggu toko = Senin–Minggu: Senin dari 19 Sep (Sabtu) = 14 Sep; dari Minggu 20 Sep tetap 14 Sep; dari Senin 21 Sep = 21 Sep', lpSenin('2026-09-19') === '2026-09-14' && lpSenin('2026-09-20') === '2026-09-14' && lpSenin('2026-09-21') === '2026-09-21');
var DM = daftarMinggu(KINI, 8); ok('daftar minggu: yang pertama = minggu berjalan 14–20 Sep (belum penuh); minggu sebelum catatan pertama (20 Agu) tidak ditawarkan', DM[0].awal === '2026-09-14' && DM[0].akhir === '2026-09-20' && DM[0].berjalan && !DM[0].penuh && DM.every(function (m) { return m.akhir >= '2026-08-20'; }) && DM[DM.length - 1].awal <= '2026-08-20', J(DM));
var RM = rekapMinggu('2026-09-14', KINI); var sigmaHari = ['14', '15', '16', '17', '18', '19', '20'].reduce(function (a, d) { return a + rekapHari('2026-09-' + d).omzet; }, 0);
ok('rekap minggu 14–20 Sep: 7 hari (Sen…Min), Σ omzet hari = omzet minggu = mesin (cocokJumlah); Sabtu 19 = 4 nota 1.270.000 & hari ini; Minggu 20 belum datang; 6 hari jalan; laba bersih = mesin rentang; kas bersih = arus kas', RM.hari.length === 7 && RM.hari[0].nama === 'Sen' && RM.hari[6].nama === 'Min' && RM.omzet === sigmaHari && RM.cocokJumlah && RM.hari[5].n === 4 && RM.hari[5].omzet === 1270000 && RM.hari[5].hariIni && RM.hari[6].depan && RM.hariJalan === 6
  && RM.labaBersih === hitungLabaBersihRentang('2026-09-14', '2026-09-20').labaBersih && RM.bersih === hitungArusKasInti(function (t) { return t >= '2026-09-14' && t <= '2026-09-20'; }).bersih && RM.terbaik.iso === '2026-09-19', J([RM.omzet, sigmaHari, RM.hari.map(function (h) { return [h.nama, h.n, h.omzet]; })]));
ok('banding minggu: minggu 7–13 Sep tanpa nota → "belum ada pembanding" (bukan naik 100 %); minggu 24–30 Agu punya nota → minggu 31 Agu–6 Sep dibanding dengannya', RM.pct === null && /belum ada pembanding/.test(RM.bandingTeks) && rekapMinggu('2026-08-31', KINI).lalu === rekapMinggu('2026-08-24', KINI).omzet, J([RM.bandingTeks, rekapMinggu('2026-08-31', KINI).bandingTeks]));
var DT = daftarTahun(KINI); var RT = rekapTahun(2026, KINI);
ok('tahunan: hanya 2026 (catatan pertama 20 Agu 2026), berjalan, belum final; 12 bulan: Okt–Des belum datang; Σ omzet bulan = omzet tahun = mesin; Sep berjalan & DRAF; Agu 700.000; Σ laba bersih bulan; status DRAF; bulan terbaik Sep', DT.length === 1 && DT[0].tahun === 2026 && DT[0].berjalan && !DT[0].final && RT.bulan.length === 12 && RT.bulan[9].depan && RT.bulan[11].depan && !RT.bulan[8].depan && RT.bulan[8].berjalan && !RT.bulan[8].final
  && RT.cocokJumlah && RT.omzet === RT.bulan.reduce(function (a, b) { return a + b.omzet; }, 0) && RT.bulan[7].omzet === 700000 && RT.labaBersih === RT.bulan.reduce(function (a, b) { return a + b.labaBersih; }, 0) && /^DRAF/.test(RT.status) && RT.terbaik.key === '2026-09' && RT.pct === null, J([RT.omzet, RT.status, RT.bulan.map(function (b) { return [b.key, b.omzet, b.depan]; })]));

// ---- 39b no. 4: kelebihan bayar pelanggan BERBUNYI di neraca (catatan & kertas), Kartu Piutang, dan tutup buku — angka mesin TIDAK diubah
(function () {
  var NPa = neracaPada(null, KINI); var NLa = lebihNeraca(null);
  ok('39b-4 tanpa sisa negatif: tanpa kalimat kelebihan bayar; catatan layar = catatan kertas; objek neracaPada TANPA kunci baru (bentuk tetap = main)', !NLa.kata && NLa.lebihBayar.n === 0 && catatanLayarNeraca(NPa, NLa) === NPa.catatan && !('lebihBayar' in NPa) && !('kataLebih' in NPa) && !('catatanInti' in NPa), J([NLa, Object.keys(NPa)]));
  var piu0 = cacheMentah('piutang').slice();
  pasok('piutangMutasi', piu0.concat([{ id: 891, tipe: 'bayar', namaPelanggan: 'Bu Contoh', nominal: 230000, tanggal: '2026-09-19', jam: '10:30', caraBayar: 'Tunai', dicatatDi: 'kasir' }]));
  var NPb = neracaPada(null, KINI); var NLb = lebihNeraca(null); var kata = 'Kelebihan bayar pelanggan Rp30.000 (1 nama) belum dihitung sebagai kewajiban — kekayaan di atas lebih besar sebesar itu.';
  ok('39b-4 neraca: piutang mesin jadi 0 (Bu Contoh sisa −30.000 disaring mesin); kalimat kelebihan bayar ikut CATATAN (kertas); catatan layar tanpa kalimat itu (layar memajangnya di pita); total = mesin', NPb.N.piutang === 0 && NLb.kata === kata && NPb.catatan === catatanLayarNeraca(NPb, NLb) + ' ' + kata && catatanLayarNeraca(NPb, NLb).indexOf('Kelebihan bayar') < 0 && NPb.total === hitungNeraca().total, J([NPb.N.piutang, NLb.kata, NPb.total]));
  ok('39b-4 HITUNGAN MENUTUP: kekayaan naik tepat sebesar kelebihan bayar yang disebut (kas +230.000, piutang −200.000 = +30.000)', NPa.total !== null && NPb.total - NPa.total === NLb.lebihBayar.jumlah && NLb.lebihBayar.jumlah === 30000, J([NPa.total, NPb.total, NLb.lebihBayar]));
  ok('39b-4 kertas neraca (laporanBerkop) membawa kalimat kelebihan bayar', laporanBerkop('neraca', '2026-09', 1, KINI).catatan.indexOf(kata) >= 0, laporanBerkop('neraca', '2026-09', 1, KINI).catatan);
  var DK = dokumenKecil('piutang', 'bu contoh', '', KINI); var akhir = DK.baris[DK.baris.length - 1];
  ok('39b-4 Kartu Piutang: baris akhir "Kelebihan bayar (uang pelanggan dipegang toko)" −30.000 (bukan "Sisa bon"); pilihan "kelebihan bayar Rp30.000" (positif, bukan −); identitas & sisa mesin tetap cocok (tidak ditolak)', akhir && akhir.nama === 'Kelebihan bayar (uang pelanggan dipegang toko)' && akhir.n === -30000 && DK.pilihan.some(function (x) { return x.id === 'bu contoh' && x.ket === 'kelebihan bayar' && x.n === 30000; }) && !DK.tolak, J([akhir, DK.pilihan, DK.tolak]));
  var TB = barisBuku('2026-09-19', '2026-09-19');
  ok('39b-4 tutup buku: peringatan "Kelebihan bayar pelanggan Rp30.000 (Bu Contoh Rp30.000) TIDAK ikut menyeberang …" (saldo pembuka mesin hanya membawa sisa > 0)', TB.lebih.n === 1 && /^Kelebihan bayar pelanggan Rp30\.000 \(Bu Contoh Rp30\.000\) TIDAK ikut menyeberang: saldo pembuka hanya membawa bon yang bersisa/.test(TB.kataLebih) && TB.harta.find(function (h) { return h.id === 'piutang'; }).n === 0, J([TB.kataLebih, TB.lebih]));
  var piu1 = cacheMentah('piutang').slice(); pasok('piutangMutasi', piu1.concat([{ id: 894, tipe: 'saldoAwal', namaPelanggan: 'Pak Besar', nominal: 900000, tanggal: '2026-09-01', dicatatDi: 'sistem' }]));
  var DK2 = dokumenKecil('piutang', null, '', KINI);
  ok('39b-4 B2 Kartu Piutang: nama kelebihan bayar DI ATAS pilihan (layar hanya menggambar 40) — walau ada nama bersisa 900.000', DK2.pilihan.length >= 2 && DK2.pilihan[0].id === 'bu contoh' && DK2.pilihan[1].id === 'pak besar', J(DK2.pilihan.slice(0, 3)));
  pasok('piutangMutasi', piu1);
  var TX = teksAcara(2026, { latihan: true, paraf: {} }, bandingBuku(TB, null), TB, 'Saksi', { tanggal: '2026-09-19', jam: '10:00' });
  ok('39b-4 B6 berita acara tutup buku (cetak/WA) memuat peringatan kelebihan bayar yang tidak menyeberang', TX.indexOf(TB.kataLebih) >= 0 && /Paraf: owner/.test(TX), TX.slice(-400));
  var titik = localStorage.getItem('miqbal_titik_kas_v1'); localStorage.removeItem('miqbal_titik_kas_v1');
  var NPc = neracaPada(null, KINI);
  ok('39b-4 B4 tanpa titik kas: kalimat "… belum dihitung sebagai kewajiban — begitu kas bisa dihitung, kekayaan akan terbaca lebih besar sebesar itu." (bukan "di atas")', NPc.aset === null && /Kelebihan bayar pelanggan Rp30\.000 \(1 nama\) belum dihitung sebagai kewajiban — begitu kas bisa dihitung, kekayaan akan terbaca lebih besar sebesar itu\.$/.test(NPc.catatan) && NPc.catatan.slice(-lebihNeraca(null, false).kata.length) === lebihNeraca(null, false).kata, NPc.catatan);
  localStorage.setItem('miqbal_titik_kas_v1', titik);
  pasok('piutangMutasi', piu0.concat([{ id: 892, tipe: 'hapusBuku', namaPelanggan: 'Bu Contoh', nominal: 200000, alasan: 'uji', tanggal: '2026-09-19', jam: '10:10', dicatatDi: 'sistem' }, { id: 893, tipe: 'bayar', namaPelanggan: 'Bu Contoh', nominal: 200000, tanggal: '2026-09-19', jam: '10:40', caraBayar: 'Tunai', dicatatDi: 'kasir' }]));
  var NLh = lebihNeraca(null, true);
  ok('39b-4 B1 neraca: hapus buku 200.000 lalu dibayar 200.000 → "Rp200.000 (1 nama) dibayar padahal sudah dihapus dari buku …" dan TIDAK menyebut kekayaan terlalu besar', NLh.kata === 'Rp200.000 (1 nama) dibayar padahal sudah dihapus dari buku — kerugian hapus bukunya sebenarnya sudah dibayar; hapus bukunya perlu dibalik, bukan uang pelanggan.' && !/kekayaan/.test(NLh.kata) && NLh.lebihBayar.uang.n === 0, NLh.kata);
  pasok('piutangMutasi', piu0);
})();
// kop belum lengkap → semua dokumen ditolak dicetak
pasok('aturanToko', cacheMentah('aturan').filter(function (d) { return d.id !== 'identitas' && d.id !== 'struk'; }));
ok('kop belum lengkap (identitas dicabut): laporan berkop, dokumen kecil, bukti omzet, paket bank semua DITOLAK menyebut Setelan/kop', /Kop belum lengkap/.test(laporanBerkop('labarugi', '2026-09', 1, KINI).tolak) && /Kop belum lengkap/.test(dokumenKecil('setor', null, '', KINI).tolak) && /Kop belum lengkap/.test(paketBank({ omzet: true }, KINI).tolak));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
if (CAD.titikKas) localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(CAD.titikKas));
var KINI = new Date(Date.now()); var salah = []; var bl = hariIniIso(KINI).slice(0, 7);
// 39b no. 38: laba bersih = mesin + selisih laci tutup hari bulan itu (dihitung ulang di sini dari dokumen tutupHari, termasuk riwayat tutup ulang)
var kas38 = 0; ambilTutupHari().forEach(function (t) { if (!t || String(t.tanggal || '').slice(0, 7) !== bl) return; [t].concat(t.riwayat || []).forEach(function (x) { kas38 += Number((x && (x.selisihLaci || x.selisih)) || 0); }); });
var LB = labaBulan(bl, KINI); var LM = hitungLabaBersihRentang(bl + '-01', akhirBulanIso(bl)); if (LB.labaBersih !== LM.labaBersih + kas38) salah.push('laba bulan ≠ mesin + lebih/kurang kas');
var LR = laporanBerkop('labarugi', bl, 1, KINI); var lb = LR.baris.find(function (r) { return r.nama === 'Laba bersih'; }); if (lb.n !== LM.labaBersih + kas38) salah.push('laba-rugi berkop ≠ mesin + lebih/kurang kas');
var NP = neracaPada(null, KINI); if (NP.aset !== null && !NP.seimbang) salah.push('neraca tidak seimbang');
var RO = rekapOmzet(KINI); var RH = rekapHari(hariIniIso(KINI)); var DN = daftarNota('', KINI, 40); var DP = dokumenKecil('piutang', null, '', KINI); var DB = dokumenKecil('bon', null, '', KINI);
print(JSON.stringify({ salah: salah, bulan: bl, margin: LB.margin, labaBersih: LB.labaBersih, lebihKurangKas: LB.L.lebihKurangKas, tunai: LB.tunai, cakupan: LB.cakupan, mdr: LB.mdr, rugi: LB.rugi.length, tanpaHpp: LB.tanpaHpp.length, susut: LB.susut.length, hariIni: { n: RH.n, omzet: RH.omzet, bersih: RH.bersih, buku: RH.buku.length },
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


def neraca_layar(t):
    """tinjauan 39b UU36-2 — layar Laporan → Neraca (gambar & kertas yang dikeluarkan) memakai LP.neracaTanggal untuk tanggal yang dipilih (kas bulan final dari
    hitungan tutup hari akhir bulan / kalimat tolak yang benar), bukan neracaPada tanpa kas bulan final; hero bulan final memakai kalimat tolak itu."""
    out = []
    if t.count('LP.neracaTanggal(') != 2 or 'LP.neracaPada(' in t: out.append('layar Neraca masih memakai neracaPada tanpa kas bulan final (gambar / keluarkan)')
    if "(sampai && D.final ? NP.tolak + '.' :" not in t: out.append('hero Neraca bulan final masih menyebut "titik kas belum disetel"')
    return out


def rekap_layar(t):
    """39b no. 37 tinjauan U37-U4 — kartu rekap Laporan › Harian (laporan.js barisRekap) menyebut retur nota bon hari itu lewat LP.lpReturBonHari, satu rumus
    dengan teks WA, supaya omzet = tunai + QRIS + bon − refund − retur nota bon menutup."""
    return [] if "{ nama: 'Retur nota bon (bon dipotong)', teks: RP(LP.lpReturBonHari(R)) }" in t else ['kartu rekap harian tidak menyebut retur nota bon (bon dipotong) — omzet tidak menutup']


def lama_rincian(src):
    """39b no. 37 tinjauan U37-U6: rincianBelumLunas index.html (sistem lama) APA ADANYA, dinamai rincianBelumLunasLAMA supaya bisa dijalankan di samping /baru/."""
    import beku2
    f = beku2.potong(src, 'rincianBelumLunas')
    return ('\n' + f.replace('function rincianBelumLunas(', 'function rincianBelumLunasLAMA(', 1) + '\n') if f else '\nfunction rincianBelumLunasLAMA() { throw new Error("rincianBelumLunas tidak ada di index.html"); }\n'


def lama_layar(t):
    """39b no. 37 tinjauan U37-U6 + MM2 — pembaca piutang lain di index.html (hanya-baca) mengenal mutasi tipe 'retur': riwayat lembar piutang menggambarnya
    mengurangi (bukan +), kolam bulan menaruhnya di keran keluar (bukan utang baru), panel "Belum tertagih" menguranginya supaya rumusnya menutup ke sisa."""
    out = []
    if "const kurang = m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur';" not in t: out.append('sistem lama: riwayat piutang menggambar retur sebagai tambah (+)')
    if "else if (m.jenis === 'retur') diretur += m.nominal || 0;" not in t or 'const selisih = baru - dibayar - dihapus - diretur;' not in t or 'const keluar = dibayar + dihapus + diretur;' not in t:
        out.append('sistem lama: kolam bulan ini menghitung retur sebagai utang baru')
    if "sRetur = j('retur')" not in t or "(sRetur > 0 ? ' − retur ' + rp(sRetur) : '')" not in t:
        out.append('sistem lama: panel Belum tertagih tidak mengurangi retur (rumus tidak menutup ke sisa)')
    return out


def tunai_layar(t):
    """39b no. 39 — layar Laba: panel "Syarat diterima tunai" menyebut SEMUA komponennya (laba bersih − margin nota bon bulan ini + margin bon yang dibayar
    bulan ini [+ margin bon yang dihapus bukunya]) supaya hitungan yang tergambar menutup. Kembalikan daftar masalah."""
    out = []
    if '+ margin bon yang dibayar bulan ini ${RP(B.marginDibayar)}' not in t: out.append('panel diterima tunai tidak menyebut margin bon yang dibayar bulan ini')
    if "${B.marginDihapus ? ' + margin bon yang dihapus bukunya ' + RP(B.marginDihapus) : ''}" not in t: out.append('panel diterima tunai diam soal margin bon yang dihapus bukunya')
    if "${B.marginDiretur ? ' + margin bon yang dipotong retur barang ' + RP(B.marginDiretur) : ''}" not in t: out.append('panel diterima tunai diam soal margin bon yang dipotong retur barang (39b no. 37)')
    return out


if __name__ == '__main__':
    idx = open(os.path.join(AKAR, 'index.html'), encoding='utf-8').read()
    js = bundel_baru.bundel(MODUL) + lama_rincian(idx)
    lap = open(os.path.join(AKAR, 'baru', 'js', 'layar', 'laporan.js'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, isi in [('39b-39 laporan.js: panel diterima tunai tanpa margin bon yang dibayar', lap.replace(' + margin bon yang dibayar bulan ini ${RP(B.marginDibayar)}', '', 1)),
                          ('39b-39 laporan.js: panel diterima tunai tanpa margin bon yang dihapus bukunya', lap.replace("${B.marginDihapus ? ' + margin bon yang dihapus bukunya ' + RP(B.marginDihapus) : ''}", '', 1)),
                          ('39b-37 laporan.js: panel diterima tunai tanpa margin bon yang dipotong retur barang', lap.replace("${B.marginDiretur ? ' + margin bon yang dipotong retur barang ' + RP(B.marginDiretur) : ''}", '', 1)),
                          ('39b-37 U37-U4 laporan.js: kartu rekap harian tanpa baris retur nota bon', lap.replace("{ nama: 'Retur nota bon (bon dipotong)', teks: RP(LP.lpReturBonHari(R)) }, ", '', 1)),
                          ('UU36-2 laporan.js: kertas Neraca yang dikeluarkan memakai neracaPada lagi', lap.replace('const NP = LP.neracaTanggal(st().sampaiN, kini(), D.final);', 'const NP = LP.neracaPada(st().sampaiN, kini());', 1)),
                          ('UU36-2 laporan.js: hero Neraca bulan final kembali "titik kas belum disetel"', lap.replace("(sampai && D.final ? NP.tolak + '.' :", "(false ? NP.tolak + '.' :", 1))]:
            g = (tunai_layar(isi) + neraca_layar(isi) + rekap_layar(isi)) if isi != lap else []
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        # 39b no. 37 tinjauan U37-U6: pembaca piutang sistem lama (index.html) — teksnya dirusak, pemeriksa kata wajib berbunyi
        for nama, isi in [('U37-U6 index.html: riwayat piutang kembali menggambar retur sebagai tambah', idx.replace("const kurang = m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur';", "const kurang = m.jenis === 'bayar' || m.jenis === 'hapusBuku';", 1)),
                          ('U37-U6 index.html: kolam bulan ini kembali menghitung retur sebagai utang baru', idx.replace("            else if (m.jenis === 'retur') diretur += m.nominal || 0;\n", "", 1)),
                          ('U37-U6 index.html: panel Belum tertagih tanpa retur', idx.replace("(sRetur > 0 ? ' − retur ' + rp(sRetur) : '')", "''", 1))]:
            g = lama_layar(isi) if isi != idx else []
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        rusak = {
            'tinjauan T2: nota bon dihitung per baris (kartu Laba)': js.replace("notaKredit.add(kunciNota(p));", "notaKredit.add(String(p.id));"),
            'tinjauan T2: nota bon dihitung per baris (rekap WA)': js.replace("nKredit: jumlahNota((t) => t === iso, (p) => caraBayarKunci(p) === 'kredit'),", "nKredit: K.jumlahKredit,"),
            'tinjauan T3: kunci nota mengabaikan grupNota (nota HP kasir)': js.replace("const kunciNota = (p) => String(p.grupNota || p.trxId || p.id);", "const kunciNota = (p) => String(p.trxId || p.id);"),
            'tinjauan: potongan QRIS menangkap kalimat biaya admin otomatis': js.replace("(!h.dariBayarBon && !h.dariPindah && !/^biaya admin/i.test(String(h.keterangan || '')) && /(^| )(mdr|potongan qris|potongan mdr)( |$)/", "(/(^| )(mdr|potongan qris|potongan mdr)/"),
            '39b-19: rekapHari.retur selalu 0 (kalimat retur hilang)': js.replace("retur: Math.round(((returUangPerHari()[iso] || {}).uang) || 0), n: jumlahNota", "retur: 0, n: jumlahNota"),
            '39b-19: angka sebelum retur kembali bernama "Omzet terhitung"': js.replace("[['Penjualan terhitung', omzetKotor]]", "[['Omzet terhitung', omzetKotor]]").replace("{ nama: 'Penjualan terhitung (nota ber-HPP)', n: L.omzetHitung + L.returUang }", "{ nama: 'Omzet terhitung (nota ber-HPP)', n: L.omzetHitung + L.returUang }"),
            '39b-19: pemilih 14 hari Laporan bruto': js.replace("omzet: (per[t] ? per[t].omzet : 0) - ((retur[t] || {}).uang || 0),", "omzet: per[t] ? per[t].omzet : 0,"),
            'no.4: neraca diam soal kelebihan bayar pelanggan': js.replace("const kataU = U.n ? 'Kelebihan bayar pelanggan '", "const kataU = false ? 'Kelebihan bayar pelanggan '"),
            'no.4 B1: hapus buku terbayar disebut menaikkan kekayaan / tidak disebut': js.replace("const kataH = H.n ?", "const kataH = false ?"),
            'no.4 B4: tanpa titik kas neraca tetap bilang "kekayaan di atas lebih besar"': js.replace("(asetAda === false ? 'begitu kas bisa dihitung, kekayaan akan terbaca lebih besar sebesar itu.' : 'kekayaan di atas lebih besar sebesar itu.')", "'kekayaan di atas lebih besar sebesar itu.'"),
            'no.4 B2: Kartu Piutang menaruh kelebihan bayar paling bawah lagi': js.replace("const kel = (x) => ((sisaDari[x.kunci] || 0) < LEBIH_AMBANG ? 0 : 1);", "const kel = (x) => 0;"),
            'no.4 B6: berita acara tutup buku tanpa peringatan kelebihan bayar': js.replace("  if (sebelum.kataLebih) L.push(sebelum.kataLebih, '');", ""),
            'no.4: catatan layar neraca mengulang kalimat yang sudah jadi pita': js.replace("NL && NL.kata && NP.catatan.endsWith(' ' + NL.kata) ?", "false ?"),
            'no.4: kalimat kelebihan bayar tidak ikut kertas neraca': js.replace("catatan: catatanInti + (kataLebih ? ' ' + kataLebih : '') };", "catatan: catatanInti };"),
            'no.4: Kartu Piutang menyebut saldo negatif "Sisa bon"': js.replace("baris.push(brs(sd < LEBIH_AMBANG ?", "baris.push(brs(false ?"),
            'no.4: tutup buku diam soal kelebihan bayar yang tidak menyeberang': js.replace("const kataLebih = !lebih.n ? '' :", "const kataLebih = true ? '' :"),
            # ---- laba
            'nota di Pusat Dokumen tanpa tanggal saldo bon (39b no. 8)': js.replace("g.sisaBonPer ? g.kiri + ' \u00b7 per ' + formatTanggal(g.sisaBonPer) : g.kiri", "g.kiri"),
            'diterima tunai = laba bersih (margin nota bon tidak dikurangkan)': js.replace("const tunai = L.labaBersih - marginKredit + marginDibayar + marginDihapus + marginDiretur;", "const tunai = L.labaBersih + marginDibayar + marginDihapus + marginDiretur;"),
            'potongan QRIS tidak dipisah dari biaya toko': js.replace("const mdr = lpMdrRentang(awal, akhir); const biayaLain = L.biayaToko - mdr;", "const mdr = 0; const biayaLain = L.biayaToko;"),
            'susut hilang dari tangga kotor → bersih (jumlahnya tidak menutup)': js.replace(".concat([['Susut & selisih stok', L.susutStok]]).concat(L.lebihKurangKas ?", ".concat(L.lebihKurangKas ?"),
            'bulan tanpa catatan digambar sama dengan bulan nol': js.replace("const tanpaCatatan = L.jumlahTrx === 0 && L.nHarian === 0 && !susut.length;", "const tanpaCatatan = false;"),
            # ---- harian
            'nota batal ikut jumlah nota hari itu': js.replace("const s = new Set(); ambilPenjualan().forEach((p) => { if (cocok(p.tanggal) && (!saring || saring(p))) s.add(kunciNota(p)); });", "const s = new Set(); ambilPenjualanSemua().forEach((p) => { if (cocok(p.tanggal) && (!saring || saring(p))) s.add(kunciNota(p)); });"),   # 39b no. 20: jumlah nota kini dari jumlahNota (toko.js)
            'teks WA lupa menyebut bon yang belum jadi uang': js.replace("if (R.kredit) b.push('Bon (belum jadi uang): '", "if (false) b.push('Bon (belum jadi uang): '"),
            # ---- bulanan / rekap omzet
            'semua bulan dianggap final tanpa tutup buku': js.replace("function lpFinal(key) { const era = bkEra(); if (era !== null && Number(key.slice(0, 4)) <= era) return true; const s = kunciSampai(); return !!s && String(key).slice(0, 7) <= s; }", "function lpFinal(key) { return true; }"),
            'kumulatif diisi juga untuk bulan tahun lalu (bukan —)': js.replace("kum: th === tahunIni ? kum : null", "kum: kum"),
            'tanda dilaporkan diizinkan pada bulan draf': js.replace("if (!lpFinal(key)) return { tolak: lpNamaBulan(key) + ' belum dikunci", "if (false) return { tolak: lpNamaBulan(key) + ' belum dikunci"),
            'membatalkan tanda tanpa ketukan kedua': js.replace("if (sudah) { if (!yakin) return { tolak: 'Ketuk sekali lagi", "if (sudah) { if (false) return { tolak: 'Ketuk sekali lagi"),
            'bukti omzet menerima bulan draf': js.replace("terpilih.some((b) => !b.final) ? 'Ada bulan yang belum tutup buku (DRAF)", "false ? 'Ada bulan yang belum tutup buku (DRAF)"),
            'tarif per seribu tanpa batas atas': js.replace("if (!(tarif >= 0 && tarif <= 1000)) return { tolak:", "if (false) return { tolak:"),
            'tagihan bulan yang belum dibayar tidak disebut': js.replace("const belum = B.filter((x) => !x.tanggal && x.bulan === key && x.nominal > 0);", "const belum = [];"),
            # ---- mingguan / tahunan (putaran 21)
            'minggu dimulai Minggu, bukan Senin': js.replace("ugTambahHari(iso, -((new Date(iso + 'T00:00:00Z').getUTCDay() + 6) % 7))", "ugTambahHari(iso, -(new Date(iso + 'T00:00:00Z').getUTCDay()))"),
            'banding minggu tanpa pembanding ditulis naik (bukan belum ada)': js.replace("const lpPersen = (a, b) => (b > 0 ? Math.round((a - b) / b * 1000) / 10 : null);", "const lpPersen = (a, b) => (b > 0 ? Math.round((a - b) / b * 1000) / 10 : 100);"),
            '39b-40: laba-rugi berkop menjumlah bulan sebelum awal buku': js.replace("const dariL = pra.length ? ab + '-01' : dari;", "const dariL = dari;"),
            '39b-40: kertas laba-rugi tanpa baris keterangan bulan sebelum awal buku': js.replace("baris.unshift({ nama: lbl + ' · sebelum awal buku — tidak dijumlah', n: null }); ", ""),
            '39b-40: Tahunan menjumlah bulan sebelum awal buku': js.replace("a + (b.sebelumBuku ? 0 : b[k] || 0)", "a + (b[k] || 0)"),
            '39b-40: Tahunan tanpa keterangan bulan sebelum awal buku': js.replace("kosong: n === 0, sebelumBuku };", "kosong: n === 0, sebelumBuku: '' };"),
            'tahunan: bulan berjalan dianggap final': js.replace("berjalan: key === kiniKey, final: lpFinal(key), omzet: Lr.omzetPenuh", "berjalan: key === kiniKey, final: true, omzet: Lr.omzetPenuh"),
            # ---- neraca
            'modal owner tidak dipisah dari laba ditahan': js.replace("const labaDitahan = aset === null ? null : aset - kewajiban - modal;", "const labaDitahan = aset === null ? null : aset - kewajiban;"),
            'neraca tanpa titik kas tetap dicetak': js.replace("const tolak = !kasAda ? 'Kas belum bisa dihitung — titik kas belum disetel; Tutup hari malam ini menyetelnya' :", "const tolak = false ? '' :"),
            'aset tetap isian owner tidak ikut aset': js.replace("const aset = kasAda ? N.kas + N.stok + N.piutang + N.kasbon + AT.asetTetap : null;", "const aset = kasAda ? N.kas + N.stok + N.piutang + N.kasbon : null;"),
            '39b-20: jumlah nota menghitung BARIS lagi': js.replace("if (cocok(p.tanggal) && (!saring || saring(p))) s.add(kunciNota(p)); }); return s.size; }", "if (cocok(p.tanggal) && (!saring || saring(p))) s.add(p.id); }); return s.size; }"),
            '39b-20: per jam menghitung baris': js.replace("notaJam[j].add(kunciNota(p)); jam[j].n = notaJam[j].size;", "notaJam[j].add(p.id); jam[j].n = notaJam[j].size;"),
            '39b-24: laporan berkop hanya membaca tanda mdr (bukan catatan yang diketik)': js.replace("(h.kategori === 'toko' || h.kategori === 'tokoDompet') && adalahMdr(h) && h.tanggal >= dari", "h.mdr && h.kategori === 'toko' && h.tanggal >= dari"),
            # ---- kop & cetakan
            'NPWP tercetak di kop penuh tanpa izin owner (bawaan lama)': js.replace("[i.npwp && i.npwpDiKop === true ? 'NPWP ' + i.npwp : '',", "[i.npwp ? 'NPWP ' + i.npwp : '',"),
            'NPWP 16 angka tanpa peringatan NIK': js.replace("return lpDigit(npwp || '').length === 16 ? PERINGATAN_NPWP_NIK : '';", "return '';"),
            'sakelar NPWP di kop tidak tersimpan': js.replace("d.npwpDiKop = draf.npwpDiKop === undefined ? !!I.npwpDiKop : draf.npwpDiKop === true;", "d.npwpDiKop = false;"),
            'NPWP tidak diperiksa panjangnya': js.replace("if (d.npwp && [15, 16].indexOf(lpDigit(d.npwp).length) < 0) return 'NPWP harus 15 atau 16 angka", "if (false) return 'NPWP harus 15 atau 16 angka"),
            'simpan identitas tidak menaikkan versi kop': js.replace("const versi = I.versi + 1; const riwayat =", "const versi = I.versi; const riwayat ="),
            'kop ringkas tidak ikut ke setelan struk (nota memakai kop lain)': js.replace("{ koleksi: 'aturanToko', data: { id: 'struk', tanggal: w.tanggal, jam: w.jam, kop: { nama: d.nama.slice(0, 40), alamat: d.alamat.slice(0, 80), telp: d.telepon.slice(0, 30) },", "{ koleksi: 'aturanToko', data: { id: 'struk', tanggal: w.tanggal, jam: w.jam, kop: S.kop,"),
            'nomor awal setelan owner diabaikan': js.replace("function nomorBerikut() { return Math.max(nomorTerakhir() + 1, pakaiKop().nomorAwal); }", "function nomorBerikut() { return nomorTerakhir() + 1; }"),
            'salinan nota selalu ke-1 (cetak ulang tidak berjejak)': js.replace("function salinanKe(trxId) { return ambilDokumenCetak().filter((d) => d.jenis === 'nota' && String(d.trxId) === String(trxId)).length + 1; }", "function salinanKe(trxId) { return 1; }"),
            'dokumen dicetak dengan kop belum lengkap': js.replace("if (!tolak && !I.lengkap) tolak = 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)';\n  return { jenis: J[0], namaJenis: J[1]", "\n  return { jenis: J[0], namaJenis: J[1]"),
            # ---- laporan berkop / dokumen kecil
            'kas akhir arus kas dihitung dari kas awal + bersih (bukan mesin kas)': js.replace("const kasAkhir = KA ? KA.kas : kasPada(sampai > iso ? null : sampai);", "const kasAkhir = (kasPada(ugTambahHari(dari, -1)) || 0) + K.bersih;"),
            # ---- 39b no. 36 (owner 30 Sep): kas akhir bulan final = hitungan fisik tutup hari akhir bulan
            '39b-36: neraca bulan final memakai kasPada (titik kas sekarang) lagi': js.replace("neracaPada(sampai > iso ? iso : sampai, kini, final ? lpKasAkhirBulan(keKey) : null)", "neracaPada(sampai > iso ? iso : sampai, kini, null)"),
            '39b-36: arus kas bulan final memakai kasPada lagi': js.replace("const KA = final ? lpKasAkhirBulan(keKey) : null, KW = final ? lpKasAkhirBulan(lpGeserBulan(bulan[0], -1)) : null;", "const KA = null, KW = null;"),
            'UU36-2: akhir bulan final di layar Neraca tanpa kas tutup hari akhir bulan': js.replace("if (sampai === akhirBulanIso(key)) return neracaPada(sampai, kini, lpKasAkhirBulan(key));", ""),
            'UU36-2: tanggal lain di bulan final ditolak "titik kas belum disetel"': js.replace("const NP = neracaPada(sampai, kini); if (NP.N.kas !== null) return NP;", "return neracaPada(sampai, kini);"),
            'UU36-1: selisih laci tutup hari di arus kas berkop kembali disebut "penyesuaian titik kas … bukan uang yang bergerak"': js.replace("const lk = selisih === null ? 0 : LKK.n;", "const lk = 0;"),
            'UU36-1: baris lebih/kurang kas arus kas bernama lain dari laba-rugi': js.replace("[{ nama: lpNamaLebihKurang({ nLebihKurang: LKK.malam }), n: lk }]", "[{ nama: 'Penyesuaian titik kas (disetel ulang dalam periode)', n: lk }]"),
            '39b-36: kas awal arus kas bulan final tetap kasPada': js.replace("KW = final ? lpKasAkhirBulan(lpGeserBulan(bulan[0], -1)) : null;", "KW = null;"),
            '39b-36: tutup hari PERTAMA di bulan itu, bukan terakhir': js.replace("const d = th.filter((x) => x.titik).sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)))[0];", "const d = th.filter((x) => x.titik).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)))[0];"),
            '39b-36: catatan uang sesudah tutup hari terakhir sampai akhir bulan diabaikan': js.replace("kas: saldoKantong(akhir, t).total,", "kas: saldoKantong(t.tanggal, t).total,"),
            '39b-36: paket bank tidak meneruskan tolak dokumennya': js.replace("tolak: tolak || tolakDok, daftar,", "tolak, daftar,"),
            '39b-36: kalimat tolak bulan final kembali "titik kas belum disetel"': js.replace("tolak: KB && !kasAda ? KB.tolak : tolak, seimbang:", "tolak, seimbang:"),
            '39b-36: tutup hari lama (tanpa isi tempat uang) disebut "tidak ada tutup hari"': js.replace("const kenapa = th.length ?", "const kenapa = false ?"),
            '39b-36: kekayaan (total) neraca bulan final tetap dari mesin': js.replace("const N = KB ? Object.assign({}, N0, { kas: KB.kas, total:", "const N = KB ? Object.assign({}, N0, { kas: KB.kas, totalX:"),
            'paket bank disusun tanpa bulan final': js.replace("const tolak = !F ? 'Belum ada bulan yang tutup buku — bank butuh angka FINAL; sampai tutup buku pertama, cetak laporan biasa bercap DRAF' :", "const tolak = false ? '' :"),
            'kartu piutang menganggap pembayaran sebagai tambahan bon': js.replace("const masuk = m.jenis === 'jual' || m.jenis === 'saldoAwal';", "const masuk = m.jenis !== 'hapusBuku';"),
            'nota yang dibatalkan boleh dicetak ulang': js.replace("if (X.batal) tolak = 'Nota dibatalkan tidak dicetak ulang';", ""),
            'nota batal tidak ditandai di daftar cetak ulang': js.replace("batal: !N.berlaku || N.dibatalkan, salinan:", "batal: false, salinan:"),
            # ---- 39b no. 38 (owner 30 Sep): selisih laci = baris lebih/kurang kas di laba
            '39b-38: Laba tanpa baris lebih/kurang kas (tangga tidak menutup)': js.replace(".concat(L.lebihKurangKas ? [[lpNamaLebihKurang(L), L.lebihKurangKas]] : []).concat([['Laba bersih', L.labaBersih, 'jumlah']])", ".concat([['Laba bersih', L.labaBersih, 'jumlah']])"),
            '39b-38: laba-rugi berkop tanpa baris lebih/kurang kas': js.replace(".concat(L.lebihKurangKas ? [{ nama: lpNamaLebihKurang(L), n: L.lebihKurangKas }] : [])", ""),
            '39b-38: Ke mana laba kotor diam soal lebih/kurang kas (tidak menutup)': js.replace("+ L.susutStok + L.lebihKurangKas) - L.labaBersih) < 0.5", "+ L.susutStok) - L.labaBersih) < 0.5"),
            '39b-38: selisih tutup hari sistem lama (tanpa selisihLaci) tidak dibaca': js.replace("const sel = (x) => Number((x && (x.selisihLaci || x.selisih)) || 0);", "const sel = (x) => Number((x && x.selisihLaci) || 0);"),
            '39b-38: neraca memakai laba mesin (laba berjalan tanpa lebih/kurang kas)': js.replace("labaKum = ugLabaBersih(pertama, s || iso).labaBersih;", "labaKum = ugLabaBersih(pertama, s || iso).labaMesin;"),
            '39b-38: Banding tanpa baris lebih/kurang kas': js.replace(".concat(A1.kas || A2.kas ? [['Lebih/kurang kas', 'kas']] : [])", ""),
            '39b-38: Tahunan tanpa jumlah lebih/kurang kas': js.replace("lebihKurangKas: jml('kas'), maks,", "lebihKurangKas: 0, maks,"),
            # ---- 39b no. 39 (owner 30 Sep): margin bon kembali ke diterima tunai saat bonnya dibayar
            '39b-39: margin bon lama tidak pernah kembali (rumus lama)': js.replace("const tunai = L.labaBersih - marginKredit + marginDibayar + marginDihapus + marginDiretur;", "const tunai = L.labaBersih - marginKredit;"),
            '39b-39: pembayaran menutup bon TERBARU dulu (beda dengan buku bon)': js.replace("const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));\n    const tutup", "const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(y.tanggal || '').localeCompare(String(x.tanggal || '')));\n    const tutup"),
            '39b-39: bon dibayar sebagian melepas SELURUH marginnya': js.replace("out[jenis === 'bayar' ? 'dibayar' : jenis === 'retur' ? 'diretur' : 'dihapus'] += mg(b.u) * x / b.u.nominal;", "out[jenis === 'bayar' ? 'dibayar' : jenis === 'retur' ? 'diretur' : 'dihapus'] += b.sisa <= 0 ? mg(b.u) : 0;"),
            '39b-39: uang lebih bayar hangus (tidak menunggu bon berikutnya)': js.replace("if (n > 0) lebih.push({ n, jenis: c.jenis }); });", "});"),
            '39b-39: hapus buku menahan marginnya selamanya (terpotong dua kali)': js.replace("const marginDihapus = Math.round(lepas.dihapus);", "const marginDihapus = 0;"),
            '39b-39: margin bon yang dibayar di bulan yang sama tidak kembali': js.replace("if (b.u.nominal > 0 && t >= dari && t <= sampai)", "if (b.u.nominal > 0 && t >= dari && t <= sampai && String(b.u.tanggal || '') < dari)"),
            # ---- 39b no. 37 (owner 2 Okt "37 buka"): retur nota BON memotong bon
            '39b-37: mesin piutang tidak menghitung mutasi retur (bon tidak turun)': js.replace("        s.retur += n;\n", ""),
            '39b-37: mesin piutang: retur tidak memadamkan bon tertua (umur bon salah)': js.replace("        sisaBayar += m.nominal - x;\n", ""),   # jangkar disesuaikan tinjauan MM1: bagian retur tanpa nota asal
            '39b-37: laba tidak membaca potongBon (penjualan tidak turun)': js.replace(" + Math.max(0, r.selisihHargaTukar || 0) + (r.potongBon || 0);", " + Math.max(0, r.selisihHargaTukar || 0);"),
            '39b-37: retur nota bon jadi uang keluar laci': js.replace("penyelesaian: 'potongBon', nominalRefund: 0, potongBon: nilai,", "penyelesaian: 'potongBon', nominalRefund: nilai, potongBon: nilai,"),
            '39b-37: retur nota bon tanpa mutasi piutang': js.replace("const dokumen = [{ koleksi: 'retur', data: draf }, { koleksi: 'piutangMutasi', data: mutasi }];", "const dokumen = [{ koleksi: 'retur', data: draf }];"),
            '39b-37: retur melebihi sisa bon lolos (jadi kelebihan bayar tanpa uang)': js.replace("if (nilai - B.sisa > 0.5) {", "if (false) {"),
            '39b-37: pembulatan bon tidak ikut dipotong (bon nota tersisa Rp500)': js.replace("(d.bon && Math.abs(jml - d.sisa) < 0.0005 ?", "(false ?"),
            '39b-37: diterima tunai menahan margin bon yang ditutup retur': js.replace("+ marginDihapus + marginDiretur;", "+ marginDihapus;"),
            '39b-37: margin bon yang ditutup retur dihitung sebagai hapus buku': js.replace("jenis === 'retur' ? 'diretur' : 'dihapus'] +=", "'dihapus'] +="),
            '39b-37: rincian bon (Pelanggan) mengabaikan retur': js.replace("let tertutup = d.bayar + d.dihapus + (d.retur || 0) - bnDiretur(utang); const hasil = [];", "let tertutup = d.bayar + d.dihapus; const hasil = [];"),   # jangkar disesuaikan tinjauan MM1
            '39b-37: riwayat Bon diam soal retur': js.replace("const riwayat = b.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur')", "const riwayat = b.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku')"),
            '39b-37: buku bon tanpa baris retur': js.replace("Pa.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku' || m.jenis === 'retur')", "Pa.mutasi.filter((m) => m.jenis === 'bayar' || m.jenis === 'hapusBuku')"),
            '39b-37: Kartu Piutang menyebut retur sebagai bayar': js.replace("else if (m.jenis === 'retur') retur += n; ", ""),
            '39b-37: kelebihan bayar sesudah retur disebut hapus buku terbayar': js.replace("((Number(d.total) || 0) - (Number(d.retur) || 0))", "(Number(d.total) || 0)"),
            '39b-37: bon lunas: retur ditolak tanpa menunjuk jalan uang kembali': js.replace("Barangnya sudah dibayar: kalau uangnya dikembalikan dari laci, catat lewat \"Tidak ada notanya? Retur ketik tangan\" (uang kembali).", "Barangnya sudah dibayar."),   # jangkar disesuaikan tinjauan U37-U2
            '39b-37 U37-U2: bon yang dihapus buku disebut sudah dibayar (kalimat lama, uang laci)': js.replace("  if (!(B.dihapus > 0.5)) return null;\n  const campur", "  return null;\n  const campur"),
            '39b-37 U37-U2: bon dibayar + dihapus buku disebut dihapus buku saja': js.replace("const campur = B.bayar > 0.5;", "const campur = false;"),
            '39b-37 U37-U3: pembulatan bon yang tertutup bayar membuat retur nota penuh ditolak': js.replace("return nilai - sisaBon > 0.5 && sisaBon > 0.5 && nilai - sisaBon <= bulat ? sisaBon : nilai;", "return nilai;"),
            '39b-37 U37-U3: retur ketik tangan dijanjikan untuk kg yang bukan kelipatan setengah karung': js.replace("if (Math.abs(x / setengah - Math.round(x / setengah)) < 0.001) return", "if (true) return"),
            '39b-37 U37-U3: jalan ketik tangan tanpa peringatan retur dua kali': js.replace("const awas = ' — catatan itu TIDAK mengurangi nota ini, jadi sesudahnya jangan retur nota ini lagi untuk barang yang sama.';", "const awas = '.';"),
            '39b-37 MM4: sisa bon di bawah satu satuan kembali menyarankan "paling banyak 0"': js.replace("    if (maks < satu) return { tolak:", "    if (false) return { tolak:"),
            '39b-37 MM3: daftar & lembar menawarkan nota bon yang bonnya sudah lunas': js.replace("const B = bonPembeli(d, piutang); return B.sisa > 0.5 ? d : { ok: false, sebab: kalimatBonHabis(B) };", "return d;"),
            '39b-37 U37-U4: teks WA rekap harian tanpa baris retur nota bon': js.replace("const rb = lpReturBonHari(R); if (rb) b.push('Retur nota bon (bon dipotong): ' + RP(rb));", ""),
            '39b-37 U37-U4: retur nota bon hari itu dihitung dari uang retur saja (refund ikut)': js.replace("const lpReturBonHari = (R) => Math.max(0, Math.round((R.retur || 0) - (R.refund || 0)));", "const lpReturBonHari = (R) => Math.max(0, Math.round(R.retur || 0));"),
            '39b-37 MM5: arus kas menghitung retur potong bon sebagai refund': js.replace("{ label: 'Refund retur', nominal: refund, n: returDipakai.filter(r => !(r.potongBon > 0)).length, satuan: 'retur' },", "{ label: 'Refund retur', nominal: refund, n: returDipakai.length, satuan: 'retur' },"),
            '39b-37 MM1: mesin piutang — retur kembali memotong bon tertua (bukan nota asalnya)': js.replace("const u = m.notaAsalId == null ? null : utang.find(x => x.jenis === 'jual' && String(x.idTrx) === String(m.notaAsalId));", "const u = null;"),
            '39b-37 MM1: rincian bon (Pelanggan) mengabaikan bagian nota yang diretur': js.replace("for (const u of utang) { const nom = u.nominal - (u.diretur || 0); if (tertutup >= nom)", "for (const u of utang) { const nom = u.nominal; if (tertutup >= nom)"),
            '39b-37 MM1: Buku bon menyalakan nota yang barangnya sudah kembali': js.replace("utang.forEach((u) => { const nom = u.nominal - (u.diretur || 0); const lunas = tertutup >= nom;", "utang.forEach((u) => { const nom = u.nominal; const lunas = tertutup >= nom;"),
            '39b-37 U37-U5: margin yang dilepas retur diambil dari bon tertua (bukan nota asalnya)': js.replace("if (c.jenis === 'retur' && c.notaAsalId != null) {", "if (false) {"),
            '39b-37 U37-U6: rincianBelumLunas sistem lama mengabaikan retur (tagihan WA lebih besar dari sisa)': js.replace("let tertutup = d.bayar + d.dihapus + (d.retur || 0) - utang.reduce((a, u) => a + (u.diretur || 0), 0);", "let tertutup = d.bayar + d.dihapus;"),
            '39b-37 U37-U6: rincianBelumLunas sistem lama menagih nota yang barangnya sudah kembali': js.replace("const nominal = u.nominal - (u.diretur || 0);\n      if (tertutup >= nominal)", "const nominal = u.nominal;\n      if (tertutup >= nominal)"),
            '39b-37: barang rusak dari nota bon tanpa karantina': js.replace("  if (draf.kondisi === 'tidak_utuh') dokumen.push(dokumenKarantina(draf));\n  return { dokumen, patch: Object.assign(returAwal(), { lembar: null, ketik: '',\n    kabar: 'Retur nota BON", "  return { dokumen, patch: Object.assign(returAwal(), { lembar: null, ketik: '',\n    kabar: 'Retur nota BON"),
            '39b-38: batas aman ambil pribadi dari laba mesin': js.replace("const laba = iso ? ugLabaBersih(ugAwalBulan(iso), iso).labaBersih : 0;", "const laba = iso ? ugLabaBersih(ugAwalBulan(iso), iso).labaMesin : 0;"),
        }
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    g = g + tunai_layar(lap) + neraca_layar(lap) + rekap_layar(lap) + lama_layar(idx)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, 'backup-batch-*.json')), key=os.path.basename)   # audit 39b no. 46 / tinjauan T6: cadangan toko ada di _privat/
    if cad and not g:
        h, e = jalan(JAM_TETAP.replace("'2026-09-19T10:00:00+07:00'", "'2026-09-22T10:00:00+07:00'") + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if h is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s): %s' % (os.path.basename(cad[-1]), json.dumps(h, ensure_ascii=False)))
        if h['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
