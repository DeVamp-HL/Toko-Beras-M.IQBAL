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

// ==================== HARIAN ====================
var RH = rekapHari('2026-09-19');
var rekapHari0918 = rekapHari('2026-09-18');
ok('19 Sep: 4 nota (batal tidak ikut) · omzet 1.270.000 · tunai 370.000 · QRIS 600.000 · bon 300.000 · pembayaran bon 100.000 · keluar 1.800 (MDR) · kas bersih 1.068.200', RH.n === 4 && RH.omzet === 1270000 && RH.tunai === 370000 && RH.qris === 600000 && RH.kredit === 300000 && RH.pelunasan === 100000 && RH.keluarHarian === 1800 && RH.bersih === 1068200, J(RH));
ok('kas bersih = Σ masuk − Σ keluar (baris arus kas yang sama); per jam: jam 09 tiga nota, jam 10 satu', dekat(RH.masuk.reduce(function (a, x) { return a + x.nominal; }, 0) - RH.keluar.reduce(function (a, x) { return a + x.nominal; }, 0), RH.bersih) && RH.perJam.length === 2 && RH.perJam[0].jam === '09' && RH.perJam[0].n === 3 && RH.perJam[1].n === 1, J(RH.perJam));
ok('buku kas 19 Sep = baris daftarGerakanKas hari itu (5: 3 nota uang + pelunasan + MDR); 16 Sep sudah tutup hari 21:05, 19 Sep belum', RH.buku.length === daftarGerakanKas().filter(function (r) { return r.t === '2026-09-19'; }).length && RH.buku.length === 5 && !RH.tutup && rekapHari('2026-09-16').tutup.jam === '21:05', J(RH.buku.map(function (r) { return r.label; })));
var TR = teksRekapHari(RH, { nama: 'Toko Contoh' }); ok('teks WA: judul toko, omzet (4 nota), tunai, QRIS, bon, pembayaran bon, kas bersih, margin', /Rekap Toko Contoh — 19 Sep/.test(TR) && /Omzet: Rp1\.270\.000 \(4 nota\)/.test(TR) && /Bon \(belum jadi uang\): Rp300\.000/.test(TR) && /Pembayaran bon pelanggan: Rp100\.000/.test(TR) && /Kas bersih hari ini: Rp1\.068\.200/.test(TR) && /Margin kotor/.test(TR), TR);
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
var PB = paketBank({ labarugi: true, neraca: true, aruskas: true, omzet: true }, KINI);
ok('paket bank: bulan final terakhir Des 2025 → 4 dokumen semua final; laba-rugi 3 bulan Okt–Des 2025; neraca per akhir Des 2025', !PB.tolak && PB.daftar.length === 4 && PB.daftar[0].periode === 'Okt 25 – Des 25' && PB.daftar[0].final && PB.daftar[1].jenis === 'neraca' && /31 Des/.test(PB.daftar[1].sub) && PB.daftar[3].jenis === 'omzet', J(PB.daftar.map(function (d) { return [d.jenis, d.periode, d.final]; })));
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


def tunai_layar(t):
    """39b no. 39 — layar Laba: panel "Syarat diterima tunai" menyebut SEMUA komponennya (laba bersih − margin nota bon bulan ini + margin bon yang dibayar
    bulan ini [+ margin bon yang dihapus bukunya]) supaya hitungan yang tergambar menutup. Kembalikan daftar masalah."""
    out = []
    if '+ margin bon yang dibayar bulan ini ${RP(B.marginDibayar)}' not in t: out.append('panel diterima tunai tidak menyebut margin bon yang dibayar bulan ini')
    if "${B.marginDihapus ? ' + margin bon yang dihapus bukunya ' + RP(B.marginDihapus) : ''}" not in t: out.append('panel diterima tunai diam soal margin bon yang dihapus bukunya')
    return out


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    lap = open(os.path.join(AKAR, 'baru', 'js', 'layar', 'laporan.js'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, isi in [('39b-39 laporan.js: panel diterima tunai tanpa margin bon yang dibayar', lap.replace(' + margin bon yang dibayar bulan ini ${RP(B.marginDibayar)}', '', 1)),
                          ('39b-39 laporan.js: panel diterima tunai tanpa margin bon yang dihapus bukunya', lap.replace("${B.marginDihapus ? ' + margin bon yang dihapus bukunya ' + RP(B.marginDihapus) : ''}", '', 1))]:
            g = tunai_layar(isi) if isi != lap else []
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
            'diterima tunai = laba bersih (margin nota bon tidak dikurangkan)': js.replace("const tunai = L.labaBersih - marginKredit + marginDibayar + marginDihapus;", "const tunai = L.labaBersih + marginDibayar + marginDihapus;"),
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
            'kas akhir arus kas dihitung dari kas awal + bersih (bukan mesin kas)': js.replace("const kasAkhir = kasPada(sampai > iso ? null : sampai);", "const kasAkhir = (kasPada(ugTambahHari(dari, -1)) || 0) + K.bersih;"),
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
            '39b-39: margin bon lama tidak pernah kembali (rumus lama)': js.replace("const tunai = L.labaBersih - marginKredit + marginDibayar + marginDihapus;", "const tunai = L.labaBersih - marginKredit;"),
            '39b-39: pembayaran menutup bon TERBARU dulu (beda dengan buku bon)': js.replace("const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(x.tanggal || '').localeCompare(String(y.tanggal || '')));\n    const tutup", "const utang = d.mutasi.filter((m) => m.jenis === 'jual' || m.jenis === 'saldoAwal').slice().sort((x, y) => String(y.tanggal || '').localeCompare(String(x.tanggal || '')));\n    const tutup"),
            '39b-39: bon dibayar sebagian melepas SELURUH marginnya': js.replace("out[jenis === 'bayar' ? 'dibayar' : 'dihapus'] += mg(b.u) * x / b.u.nominal;", "out[jenis === 'bayar' ? 'dibayar' : 'dihapus'] += b.sisa <= 0 ? mg(b.u) : 0;"),
            '39b-39: uang lebih bayar hangus (tidak menunggu bon berikutnya)': js.replace("if (n > 0) lebih.push({ n, jenis: c.jenis }); });", "});"),
            '39b-39: hapus buku menahan marginnya selamanya (terpotong dua kali)': js.replace("const marginDihapus = Math.round(lepas.dihapus);", "const marginDihapus = 0;"),
            '39b-39: margin bon yang dibayar di bulan yang sama tidak kembali': js.replace("if (b.u.nominal > 0 && t >= dari && t <= sampai)", "if (b.u.nominal > 0 && t >= dari && t <= sampai && String(b.u.tanggal || '') < dari)"),
            '39b-38: batas aman ambil pribadi dari laba mesin': js.replace("const laba = iso ? ugLabaBersih(ugAwalBulan(iso), iso).labaBersih : 0;", "const laba = iso ? ugLabaBersih(ugAwalBulan(iso), iso).labaMesin : 0;"),
        }
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    g = g + tunai_layar(lap)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, 'backup-batch-*.json')), key=os.path.basename)   # audit 39b no. 46 / tinjauan T6: cadangan toko ada di _privat/
    if cad and not g:
        h, e = jalan(JAM_TETAP.replace("'2026-09-19T10:00:00+07:00'", "'2026-09-22T10:00:00+07:00'") + js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if h is None: print('ASAP JATUH: ' + e); sys.exit(2)
        print('ASAP DATA TOKO (%s): %s' % (os.path.basename(cad[-1]), json.dumps(h, ensure_ascii=False)))
        if h['salah']: sys.exit(2)
    sys.exit(1 if g else 0)
