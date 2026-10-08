#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pelanggan_baru.py — uji logika layar PELANGGAN sistem baru (baru/js/layar/pelanggan-logika.js + bon-logika.js) di jsc.
KOTAK PASIR (NAMA & ANGKA CONTOH, bukan pelanggan toko), jam dikunci 19 Sep 2026 10:00 WIB (Sabtu).
Kalau ada backup-batch-*.json lokal: jumlah kunjungan/belanja bernama & sisa bon layar = mesin beku; kolom dokumen yang ditulis dikenal cadangan.

    python3 alat-uji/uji_pelanggan_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pelanggan_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js']
def kunci_jam(iso):
    return ("var __RealDate = Date; var __KINI = new __RealDate('%s').getTime();\n"
            "Date = function (a, b, c, d, e, f, g) { if (!(this instanceof Date)) return new __RealDate(__KINI).toString(); if (arguments.length === 0) return new __RealDate(__KINI); if (arguments.length === 1) return new __RealDate(a); return new __RealDate(a, b, c === undefined ? 1 : c, d || 0, e || 0, f || 0, g || 0); };\n"
            "Date.prototype = __RealDate.prototype; Date.now = function () { return __KINI; }; Date.UTC = __RealDate.UTC; Date.parse = __RealDate.parse;\n") % iso
JAM_TETAP = kunci_jam('2026-09-19T10:00:00+07:00')


def jual(id, tgl, jam, nama, jenis, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'namaPelanggan': nama, 'caraBayar': k.pop('cara', 'Tunai'), 'jenis': jenis, 'hargaTotal': k.pop('n', 0), 'hppTotalSaatJual': 0}
    d.update(k); return d


def literan(id, tgl, jam, nama, merk, liter, n, **k): return jual(id, tgl, jam, nama, 'literan', merkSumber=merk, jumlahLiter=liter, totalKg=round(liter * 0.82, 2), n=n, **k)
def karung(id, tgl, jam, nama, merk, jml, n, **k): return jual(id, tgl, jam, nama, 'karung', merkSumber=merk, namaProduk=merk + ' (karung utuh)', jumlahKarung=jml, beratKarungAcuan=50, totalKg=50 * jml, n=n, **k)


KOTAK = {
  'penjualan': [
    # Bu Rahma: 5 kedatangan pagi tiap 2 hari, terakhir 9 Sep → bangku kosong (10 hari ≥ 2,0 × selang 2); satu nota Kredit → bon 37.500
    literan(101, '2026-09-01', '09:10', 'Bu Rahma', 'Angsa', 3, 37500), literan(102, '2026-09-03', '09:20', 'Bu Rahma', 'Angsa', 3, 37500), literan(103, '2026-09-05', '09:05', 'Bu Rahma', 'Angsa', 3, 37500),
    literan(104, '2026-09-07', '09:30', 'Bu Rahma', 'Angsa', 3, 37500), literan(105, '2026-09-09', '09:15', 'Bu Rahma', 'Angsa', 3, 37500, cara='Kredit'),
    # Mbak Yuni: 6 hari berturut siang, terakhir kemarin → selang 1, "waktunya datang"
    literan(111, '2026-09-13', '13:00', 'Mbak Yuni', 'IR64 Apex', 10, 130000), literan(112, '2026-09-14', '13:05', 'Mbak Yuni', 'IR64 Apex', 10, 130000), literan(113, '2026-09-15', '13:00', 'Mbak Yuni', 'IR64 Apex', 10, 130000),
    literan(114, '2026-09-16', '13:10', 'Mbak Yuni', 'IR64 Apex', 10, 130000), literan(115, '2026-09-17', '12:55', 'Mbak Yuni', 'IR64 Apex', 10, 130000), literan(116, '2026-09-18', '13:00', 'Mbak Yuni', 'IR64 Apex', 10, 130000),
    # Pak Darto: 2 nota Kredit sore + 1 pembayaran (13 Sep) = 3 kedatangan → selang median [7, 1] = 4; bon 1.380.000 − 300.000
    karung(121, '2026-09-05', '16:00', 'Pak Darto', 'Angsa', 1, 690000, cara='Kredit'), karung(122, '2026-09-12', '16:10', 'Pak Darto', 'Angsa', 1, 690000, cara='Kredit'),
    # Uda Feri: karung IR42 pagi, 2 nota Kredit; ditagih 10 Sep janji 15 Sep, tidak membayar sesudahnya → janjinya lewat
    karung(131, '2026-08-28', '08:00', 'Uda Feri', 'IR42 Select', 1, 780000, cara='Kredit'), karung(132, '2026-09-05', '08:05', 'Uda Feri', 'IR42 Select', 1, 780000, cara='Kredit'),
    # Mas Bimo: bon kecil, ditagih 8 Sep janji 12 Sep, MEMBAYAR 14 Sep → janjinya tidak lagi "lewat"
    literan(141, '2026-09-01', '17:00', 'Mas Bimo', 'Perahu Layar', 5, 70000, cara='Kredit'),
    # Bu Sri: bon 100.000 (1 Sep) + 500.000 (8 Sep), membayar 150.000 (10 Sep) → FIFO: bon pertama tertutup, sisa 450.000 melekat di bon kedua
    literan(191, '2026-09-01', '11:00', 'Bu Sri', 'Angsa', 8, 100000, cara='Kredit'), literan(192, '2026-09-08', '11:10', 'Bu Sri', 'Angsa', 40, 500000, cara='Kredit'),
    # Bang Togar: pengantar (benang ke Uda Feri)
    literan(151, '2026-09-11', '14:05', 'Bang Togar', 'Angsa', 3, 45000),
    # nama kembar & nama belum jadi
    literan(161, '2026-08-11', '09:21', 'Ibu Rahma Warung', 'Angsa', 8, 103500), literan(171, '2026-08-21', '16:25', 'b', 'Angsa', 2, 32500),
    # HARI INI tanpa nama: satu nota BESAR (2 baris, grupNota g1) dan satu kecil
    karung(181, '2026-09-19', '08:10', '', 'IR42 Select', 3, 2340000, grupNota='g1'), karung(182, '2026-09-19', '08:10', '', 'IR42 Select', 1, 780000, grupNota='g1'), literan(183, '2026-09-19', '09:25', '', 'Angsa', 3, 37500, grupNota='g2'),
  ],
  'piutangMutasi': [
    {'id': 201, 'tipe': 'bayar', 'namaPelanggan': 'Pak Darto', 'nominal': 300000, 'tanggal': '2026-09-13', 'jam': '16:20', 'caraBayar': 'Tunai', 'catatan': '', 'dicatatDi': 'sistem'},
    {'id': 202, 'tipe': 'bayar', 'namaPelanggan': 'Uda Feri', 'nominal': 110000, 'tanggal': '2026-09-05', 'jam': '08:10', 'caraBayar': 'Tunai', 'catatan': 'dibayar waktu ambil karung kedua', 'dicatatDi': 'sistem'},
    {'id': 203, 'tipe': 'bayar', 'namaPelanggan': 'Mas Bimo', 'nominal': 20000, 'tanggal': '2026-09-14', 'jam': '17:00', 'caraBayar': 'Tunai', 'catatan': '', 'dicatatDi': 'sistem'},
    {'id': 204, 'tipe': 'saldoAwal', 'namaPelanggan': 'Pak Hartawan', 'nominal': 250000, 'tanggal': '2022-07-15', 'catatan': 'Sisa dari catatan lama', 'dicatatDi': 'sistem'},
    {'id': 205, 'tipe': 'saldoAwal', 'namaPelanggan': 'Bu Lisna', 'nominal': 650000, 'tanggal': '2025-02-28', 'catatan': 'Sisa dari catatan lama', 'dicatatDi': 'sistem'},
    {'id': 206, 'tipe': 'bayar', 'namaPelanggan': 'Bu Lisna', 'nominal': 50000, 'tanggal': '2026-09-10', 'jam': '10:00', 'caraBayar': 'QRIS', 'catatan': '', 'dicatatDi': 'sistem'},
    {'id': 207, 'tipe': 'bayar', 'namaPelanggan': 'Bu Sri', 'nominal': 150000, 'tanggal': '2026-09-10', 'jam': '11:30', 'caraBayar': 'Tunai', 'catatan': '', 'dicatatDi': 'sistem'},
  ],
  'pelangganCatatan': [
    {'id': 'bu rahma', 'nama': 'Bu Rahma', 'catatan': '', 'ciri': 'ibu-ibu · kerudung · naik motor · literan', 'rute': ''},   # kartu gaya LAMA: ciri teks
    {'id': 'pak darto', 'nama': 'Pak Darto', 'catatan': 'beli tiap sore sepulang kerja', 'ciri': 'bapak-bapak · peci · naik motor · karung', 'rute': '', 'cip': ['bapak-bapak', 'peci', 'naik motor', 'karung'], 'kontak': '0813 0000 2290'},
    {'id': 'uda feri', 'nama': 'Uda Feri', 'catatan': '', 'ciri': 'bapak-bapak · kacamata · mobil bak · karung · warung / usaha', 'rute': '', 'cip': ['bapak-bapak', 'kacamata', 'mobil bak', 'karung', 'warung / usaha'], 'kontak': '0812 0000 0001'},
    {'id': 'mbak yuni', 'nama': 'Mbak Yuni', 'catatan': '', 'ciri': 'anak muda · kerudung · jalan kaki · literan · warung / usaha', 'rute': '', 'cip': ['anak muda', 'kerudung', 'jalan kaki', 'literan', 'warung / usaha']},
    {'id': 'ibu rahma warung', 'nama': 'Ibu Rahma Warung', 'catatan': 'warung nasi', 'ciri': '', 'rute': ''},
  ],
  'pelangganTitip': [{'id': 't1', 'dari': 'bang togar', 'untuk': 'uda feri', 'apa': 'membayarkan bon', 'kali': 3, 'tanggal': '2026-09-11'}],
  'tagihPelanggan': [{'id': 'tg1', 'kunci': 'uda feri', 'nama': 'Uda Feri', 'tanggal': '2026-09-10', 'jam': '10:00', 'janji': '2026-09-15', 'sisa': 1450000}, {'id': 'tg2', 'kunci': 'mas bimo', 'nama': 'Mas Bimo', 'tanggal': '2026-09-08', 'jam': '10:00', 'janji': '2026-09-12', 'sisa': 70000}],
  'thrPelanggan': [{'id': 'th1', 'tahun': 2025, 'kunci': 'uda feri', 'nama': 'Uda Feri', 'bentuk': 'Sarung', 'nilai': 75000, 'tanggal': '2025-03-20', 'jam': '10:00', 'serah': True}],
}

# PUTARAN 25 — nota SISTEM BARU (bentuk susunNotaDokumen jual-logika.js; keranjang index.html sama): trxId di TIAP baris, TANPA grupNota; id & trxId
# berbentuk idUnik() asli (Date.now() + Math.random()). Plus satu baris lama tanpa trxId/grupNota (satu baris = satu nota). Dipasang HANYA di kasus
# putaran 25 lalu dipulihkan, jadi kasus lain melihat kotak yang sama.
TRX_BARU = 1758249600000.4217
NOTA_TRX = [
    karung(1758249600000.6113, '2026-09-19', '09:40', '', 'IR42 Select', 1, 780000, trxId=TRX_BARU),
    literan(1758249600000.7731, '2026-09-19', '09:40', '', 'Angsa', 3, 37500, trxId=TRX_BARU),
    literan(1758249600000.9302, '2026-09-19', '09:40', '', 'Perahu Layar', 5, 70000, trxId=TRX_BARU),
    karung(9701, '2026-09-19', '09:50', '', 'Angsa', 1, 690000),
]

# PAKET BRIEF 9 OKT (butir 1) — RATA-RATA HARI BON TERTAGIH. Dipasang HANYA di kasus tertagih lalu dipulihkan (kotak dasar tetap sama untuk kasus lain).
# Jam dikunci 19 Sep 2026 → periode bawaan 90 hari = 22 Jun – 19 Sep (hari ini ikut). Hitungan tangan (rupiah dalam ribu; hari = tanggal bayar − tanggal bon):
#   Bu Wati   bon 200 (1 Agu) + 100 (11 Agu); bayar 150 (6 Agu) + 150 (21 Agu). FIFO: 150 → bon 1 Agu (5 hari); 150 → 50 sisa bon 1 Agu (20 hari) + 100 bon 11 Agu
#             (10 hari). Σ rp 300 · Σ rp×hari = 150×5 + 50×20 + 100×10 = 2.750 → 9,1666… → "9,2 hari". Dua bon lunas 21 Agu.
#   Pak Joko  bon 400 (1 Jul) + 50 (1 Agu); bayar 100 (11 Jul, 10 hari) + 300 (10 Agu, 40 hari) → bon 1 Jul lunas 10 Agu; bon 1 Agu TETAP terbuka (FIFO).
#             Σ rp 400 · 100×10 + 300×40 = 13.000 → 32,5 hari.
#   Mbak Rina bon 150 (15 Jul); bayar 50 (25 Jul, 10 hari); hapus buku 100 (1 Sep) → lunas 1 Sep. Tertagih 50×10 = 500 (10 hari); hapus buku 100 TERPISAH.
#   Pak Udin  bon 300 (5 Agu) + 120 (20 Agu); retur 120 nota asal 20 Agu (25 Agu) → bon 20 Agu ditutup RETUR; bayar 300 (4 Sep) → bon 5 Agu 30 hari.
#             Tertagih 300×30 = 9.000; retur 120 TERPISAH.
#   Bu Tini   saldo awal 200 (1 Mei, catatan lama) dibayar 200 (1 Agu) → SALDO AWAL: belum bisa dihitung (bukan 92 hari).
#   Pak Bowo  bayar 50 (1 Agu) SEBELUM bonnya lahir; bon 50 (3 Agu) → ditutup uang yang menunggu = 0 hari (nol, tidak −2).
#   Bu Ani    bon 80 (10 Mei); bayar 80 (1 Jun, 22 hari) → lunas 1 Jun = DI LUAR 90 hari (masuk kalau periode 120 hari: 23 Mei – 19 Sep).
#   Pak Eko   bon 100 (20 Jul); hapus buku 100 (20 Agu); 10 Sep: hapus buku DIBALIK −100 + bayar 100 (Paket F2) → tertagih 100×52 hari = 5.200.
#   Bu Sri    (kotak dasar) bon 100 (1 Sep) ditutup bayar 150 (10 Sep) → 100×9 = 900; bon 500 (8 Sep) belum lunas.
#   Bu Yati   nota 500 (2 Sep) uang kurang: 300 DIBAYAR DI MEJA saat beli (notaTrxId, catatan kosong) + 200 dibayar 12 Sep (10 hari) → saat beli 300 TERPISAH
#             (bukan bon yang ditagih), tertagih 200×10 = 2.000.
#   Pak Hadi  bon 100 (20 Agu); nota 250 (5 Sep) uang kurang 150 di meja (catatan "Dibayar langsung saat beli", gaya index.html, tanpa notaTrxId): FIFO → 100 menutup
#             bon 20 Agu = TERTAGIH 16 hari, 50 menutup nota 5 Sep di hari itu = saat beli; bayar 200 (14 Sep) → nota 5 Sep 9 hari. Tertagih 100×16 + 200×9 = 3.400 / 300.
#   TOKO 90 hari: tertagih 11 bon · Σ rp 300+400+50+300+50+100+100+200+300 = 1.800 · Σ rp×hari 2.750+13.000+500+9.000+0+5.200+900+2.000+3.400 = 36.750
#             → 20,416… → "20,4 hari"; saat beli 2 bon 350 · saldo awal 1 bon 200 · hapus buku 1 bon 100 · retur 1 bon 120 · lunas 13 bon 2.570 = 1.800+350+200+100+120.
#   120 hari: + Bu Ani 80×22 = 1.760 → 12 bon · 1.880 · 38.510 → 20,48… → "20,5 hari" · 14 bon lunas.
#   10 hari (10–19 Sep): Bu Sri 900 + Pak Eko 5.200 + Bu Yati 2.000 + Pak Hadi nota 5 Sep 1.800 = 9.900 / 600 → 16,5 hari (4 bon lunas; bon Hadi 20 Agu lunas 5 Sep = di luar).
#   5 hari (15–19 Sep): tidak ada bon yang lunas → kosong "—" (bukan 0).
def _bon(id, tgl, nama, n): return literan(id, tgl, '10:00', nama, 'Angsa', 1, n, cara='Kredit')
def _m(id, tipe, nama, n, tgl, **k):
    d = {'id': id, 'tipe': tipe, 'namaPelanggan': nama, 'nominal': n, 'tanggal': tgl, 'jam': k.pop('jam', '10:00'), 'dicatatDi': 'sistem'}
    if tipe == 'bayar': d.update({'caraBayar': 'Tunai', 'catatan': ''})
    d.update(k); return d
TERTAGIH = {
    'penjualan': [_bon(3001, '2026-08-01', 'Bu Wati', 200000), _bon(3002, '2026-08-11', 'Bu Wati', 100000), _bon(3011, '2026-07-01', 'Pak Joko', 400000), _bon(3012, '2026-08-01', 'Pak Joko', 50000),
                  _bon(3021, '2026-07-15', 'Mbak Rina', 150000), _bon(3031, '2026-08-05', 'Pak Udin', 300000), _bon(3032, '2026-08-20', 'Pak Udin', 120000), _bon(3041, '2026-08-03', 'Pak Bowo', 50000),
                  _bon(3051, '2026-05-10', 'Bu Ani', 80000), _bon(3061, '2026-07-20', 'Pak Eko', 100000), _bon(3071, '2026-09-02', 'Bu Yati', 500000),
                  _bon(3081, '2026-08-20', 'Pak Hadi', 100000), _bon(3082, '2026-09-05', 'Pak Hadi', 250000)],
    'piutangMutasi': [_m(4001, 'bayar', 'Bu Wati', 150000, '2026-08-06'), _m(4002, 'bayar', 'Bu Wati', 150000, '2026-08-21'),
                      _m(4011, 'bayar', 'Pak Joko', 100000, '2026-07-11'), _m(4012, 'bayar', 'Pak Joko', 300000, '2026-08-10'),
                      _m(4021, 'bayar', 'Mbak Rina', 50000, '2026-07-25'), _m(4022, 'hapusBuku', 'Mbak Rina', 100000, '2026-09-01', alasan='pindah, tidak bisa dihubungi'),
                      _m(4031, 'retur', 'Pak Udin', 120000, '2026-08-25', notaAsalId=3032, catatan='barang kembali'), _m(4032, 'bayar', 'Pak Udin', 300000, '2026-09-04'),
                      _m(4041, 'saldoAwal', 'Bu Tini', 200000, '2026-05-01', catatan='Sisa dari catatan lama'), _m(4042, 'bayar', 'Bu Tini', 200000, '2026-08-01'),
                      _m(4051, 'bayar', 'Pak Bowo', 50000, '2026-08-01'), _m(4061, 'bayar', 'Bu Ani', 80000, '2026-06-01'),
                      _m(4071, 'hapusBuku', 'Pak Eko', 100000, '2026-08-20', alasan='tidak bisa dihubungi'),
                      _m(4073, 'bayar', 'Pak Eko', 100000, '2026-09-10', catatan='dibayar sesudah dihapus buku'),
                      _m(4072, 'hapusBuku', 'Pak Eko', -100000, '2026-09-10', alasan='hapus buku dibalik — dibayar sesudah dihapus', balikHapus=True),
                      _m(4081, 'bayar', 'Bu Yati', 300000, '2026-09-02', notaTrxId='3071'), _m(4082, 'bayar', 'Bu Yati', 200000, '2026-09-12'),
                      _m(4091, 'bayar', 'Pak Hadi', 150000, '2026-09-05', catatan='Dibayar langsung saat beli — sisa Rp100.000 jadi piutang'), _m(4092, 'bayar', 'Pak Hadi', 200000, '2026-09-14')],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var PETA = { penjualan: 'penjualan', piutangMutasi: 'piutang', pelangganCatatan: 'pelangganCat', thrPelanggan: 'thr', tagihPelanggan: 'tagih', pelangganTitip: 'titip', aturanToko: 'aturan', pesanan: 'pesanan' };
var terapkan = function (r) { var per = {}; (r.dokumen || []).forEach(function (d) { var kol = d.koleksi; if (!per[kol]) per[kol] = cacheMentah(PETA[kol]).slice(); per[kol] = per[kol].filter(function (x) { return String(x.id) !== String(d.data.id); }).concat([d.data]); });
  (r.hapus || []).forEach(function (h) { var kol = h.koleksi; if (!per[kol]) per[kol] = cacheMentah(PETA[kol]).slice(); per[kol] = per[kol].filter(function (x) { return String(x.id) !== String(h.id); }); }); Object.keys(per).forEach(function (kol) { pasok(kol, per[kol]); }); };
var simpan = function () { var s = {}; Object.keys(PETA).forEach(function (k) { s[k] = cacheMentah(PETA[k]).slice(); }); return s; }; var pulih = function (s) { Object.keys(s).forEach(function (k) { pasok(k, s[k]); }); };
var O = semuaOrang(KINI); var org = function (k) { return O.find(function (b) { return b.kunci === k; }); };
ok('orang: 11 nama (nota bernama + buku bon termasuk saldo awal + kartu); Bu Rahma 5 kedatangan, selang 2 hari, jam 9 pagi, terakhir 9 Sep → 10 hari tidak datang = BANGKU KOSONG (≥ 2,0× selang); dikenali lewat kartu gaya lama (ciri teks → 4 cip)',
  O.length === 11 && org('bu rahma').kunjungan === 5 && org('bu rahma').selang === 2 && org('bu rahma').jam === 9 && org('bu rahma').waktu === 'pagi' && org('bu rahma').sejak === 10 && org('bu rahma').kosong === true && org('bu rahma').dikenali && org('bu rahma').cip.length === 4 && org('bu rahma').cip[1] === 'kerudung' && org('bu rahma').utang === 37500, JSON.stringify(org('bu rahma')));
ok('orang: Mbak Yuni 6 hari berturut → selang 1, terakhir kemarin → WAKTUNYA DATANG (diharap), bukan kosong; jam 13 siang; belanja 780.000; Uda Feri baru 2 kali datang → selang BELUM dihitung (null)', org('uda feri').kunjungan === 2 && org('uda feri').selang === null && !org('uda feri').adaSelang && org('mbak yuni').kunjungan === 6 && org('mbak yuni').selang === 1 && org('mbak yuni').diharap === true && !org('mbak yuni').kosong && org('mbak yuni').jam === 13 && org('mbak yuni').total === 780000, JSON.stringify(org('mbak yuni')));
ok('orang: pembayar bon juga DATANG — Pak Darto 2 nota + 1 pembayaran = 3 kedatangan → selang median [7, 1] = 4, telat 2 hari (diharap), bon 1.080.000 (1.380.000 − 300.000 dari mesin beku)', org('pak darto').kunjungan === 3 && org('pak darto').selang === 4 && org('pak darto').jatuh === -2 && org('pak darto').diharap && org('pak darto').utang === 1080000 && org('pak darto').umurBon === 14, JSON.stringify(org('pak darto')));
ok('orang: "b" = nama belum jadi; Bu Rahma ↔ Ibu Rahma Warung ditawarkan sebagai kembar (tidak digabung sendiri); hari langganan Rahma: Sabtu 1 dari 5', org('b').belumJadi && pasanganKembar(O).length === 1 && pasanganKembar(O)[0].k === 'bu rahma+ibu rahma warung' && org('bu rahma').hari[5] === 1 && org('bu rahma').hari.reduce(function (a, x) { return a + x; }, 0) === 5, JSON.stringify([pasanganKembar(O).map(function (p) { return p.k; }), org('bu rahma').hari]));
ok('orang: pola barang = yang biasa dibeli (Uda Feri karung IR42; Rahma literan Angsa); nama barang terbaca manusiawi', org('uda feri').pola[0] === 'karung|IR42 Select' && plBarangNama(org('uda feri').pola[0]) === 'IR42 Select karung' && org('bu rahma').pola[0] === 'literan|Angsa', JSON.stringify([org('uda feri').pola, org('bu rahma').pola]));
// ---- WAJAH
var WJ = susunWajah(KINI, '');
ok('wajah: yang paling mungkin di depan meja SEKARANG (jam 10, pagi) di atas — Uda Feri & Ibu Rahma Warung (jam paginya cocok), lalu Mbak Yuni (waktunya datang), Bu Rahma (pagi tapi bangku kosong), Pak Darto; sketsa dari cip: Rahma kerudung + motor + liter, Darto peci + motor + karung; yang tanpa cip = "?"',
  WJ.daftar[0].kunci === 'uda feri' && WJ.daftar[1].kunci === 'ibu rahma warung' && WJ.daftar[2].kunci === 'mbak yuni' && WJ.daftar[3].kunci === 'bu rahma' && WJ.daftar[4].kunci === 'pak darto' && WJ.daftar[3].sk.kerudung && WJ.daftar[3].sk.naik === 'motor' && WJ.daftar[3].sk.beli === 'liter' && WJ.daftar[4].sk.peci && !WJ.daftar[4].sk.kerudung && WJ.daftar[4].sk.beli === 'karung' && WJ.daftar.find(function (x) { return x.kunci === 'b'; }).sk.kosong && WJ.daftar[3].titik === 'bon' && /Jam 10\.00/.test(WJ.kiniTeks) && WJ.kembar.length === 1 && WJ.belumJadi.length === 1,
  JSON.stringify(WJ.daftar.map(function (x) { return x.kunci + ':' + x.titik; })));
ok('wajah: cari "rahma" (sapaan dibuang) → dua orang; cari nama asli ikut', susunWajah(KINI, 'Bu Rahma').daftar.length === 2 && susunWajah(KINI, 'zzz').daftar.length === 0, JSON.stringify(susunWajah(KINI, 'rahma').daftar.map(function (x) { return x.kunci; })));
// ---- TAMPAH
var T0 = susunTampah(KINI, []);
ok('tampah: 4 orang punya cip; pertanyaan pertama = ciri yang membelah paling rata dan PALING AWAL di daftar owner ("bapak-bapak" 2 dari 4, timpang 0 — bukan "ibu-ibu" 1 dari 4)', T0.tanya && T0.tanya.c === 'bapak-bapak' && T0.tanya.n === 2 && T0.orang.length === 4 && T0.label === 'Siapa dia' && /tersisa 4 dari 4/.test(T0.info) && T0.tanpaCiri === 7, JSON.stringify([T0.tanya, T0.info]));
var T1 = susunTampah(KINI, [{ c: 'bapak-bapak', j: 'ya' }]); var T2 = susunTampah(KINI, [{ c: 'bapak-bapak', j: 'ya' }, { c: T1.tanya.c, j: 'bukan' }]);
ok('tampah: ya → tersisa Darto & Feri, Rahma & Yuni TERLEMPAR (sebab "bukan bapak-bapak"); tanya berikutnya "peci"; bukan → tinggal Uda Feri (ketemu); "tidak kelihatan" tidak melempar siapa pun', T1.orang.length === 2 && T1.lempar.length === 2 && T1.lempar[0].sebab === 'bukan bapak-bapak' && T1.tanya.c === 'peci' && T2.ketemu && T2.ketemu.kunci === 'uda feri' && !T2.tanya && susunTampah(KINI, [{ c: 'bapak-bapak', j: 'entah' }]).orang.length === 4, JSON.stringify([T1.tanya, T1.lempar, T2.ketemu && T2.ketemu.kunci]));
ok('tampah: jawaban untuk ciri yang sudah dihapus owner diabaikan; letak di tampah = titik di lingkaran (tidak di luar 0–100)', susunTampah(KINI, [{ c: 'ciri-hilang', j: 'ya' }]).orang.length === 4 && T0.orang.every(function (o) { return o.kiri >= 0 && o.kiri <= 100 && o.atas >= 0 && o.atas <= 100; }));
// ---- BELANJA
var BL = susunBelanja(KINI, null, []);
ok('belanja: hari ini SATU nota besar tanpa nama (g1 · 2 baris · 3.120.000) — nota kecil (37.500) tidak ditagih namanya; chip barang = barang yang biasa dibeli orang-orang', BL.nota.length === 1 && BL.nota[0].kunci === 'g1' && BL.nota[0].n === 3120000 && BL.nota[0].baris === 2 && BL.kecil === 1 && BL.notaBesar === 500000 && BL.barang.some(function (b) { return b.kunci === 'karung|IR42 Select'; }), JSON.stringify(BL.nota));
var BL1 = susunBelanja(KINI, 'g1', []);
ok('belanja: pilih nota g1 (IR42 karung, jam 08.10 pagi) → tebakan Uda Feri saja (biasa beli IR42 karung · jamnya cocok pagi → "cocok semua"); Bu Rahma tidak (Angsa literan)', BL1.tebak.length === 1 && BL1.tebak[0].kunci === 'uda feri' && /IR42 Select karung/.test(BL1.tebak[0].alasan) && /jamnya cocok \(pagi\)/.test(BL1.tebak[0].alasan) && BL1.tebak[0].yakin === 'cocok semua' && BL1.waktu === 'pagi', JSON.stringify(BL1.tebak.map(function (t) { return t.kunci + ':' + t.yakin; })));
var ID = susunIniDia(KINI, 'g1', 'uda feri');
ok('ini dia: SEMUA baris nota g1 (2) ditulis ulang dengan namaPelanggan "Uda Feri" — kolom lain utuh; nota bernama ditolak; sesudahnya Feri sudah datang hari ini & nota besar habis', !ID.tolak && ID.dokumen.length === 2 && ID.dokumen.every(function (d) { return d.koleksi === 'penjualan' && d.data.namaPelanggan === 'Uda Feri'; }) && ID.dokumen.some(function (d) { return d.data.hargaTotal === 2340000 && d.data.jumlahKarung === 3; }) && /Rp3\.120\.000/.test(ID.patch.kabar)
  && (function () { var s = simpan(); terapkan(ID); var r = semuaOrang(KINI).find(function (b) { return b.kunci === 'uda feri'; }).hariIni && susunBelanja(KINI, null, []).nota.length === 0 && /sudah bernama/.test(susunIniDia(KINI, 'g1', 'uda feri').tolak || ''); pulih(s); return r; })(), JSON.stringify(ID));
// ---- PUTARAN 25: nota sistem baru (trxId di tiap baris, tanpa grupNota) = SATU nota di Belanja; "ini dia" menamai SEMUA barisnya. Baris lama tanpa kunci tetap satu baris satu nota.
var sTrx = simpan(); pasok('penjualan', cacheMentah('penjualan').concat(NOTA_TRX)); var kTrx = String(TRX_BARU);
var BLT = susunBelanja(KINI, null, []); var nT = BLT.nota.find(function (n) { return n.jam === '09:40'; }) || {}; var gT = BLT.nota.find(function (n) { return n.kunci === 'g1'; }) || {};
ok('belanja (putaran 25): nota sistem baru 3 baris (trxId, tanpa grupNota) = SATU nota besar (3 baris · 887.500, kunci = trxId); baris 37.500 & 70.000-nya TIDAK jadi nota kecil sendiri; nota lama g1 tetap 2 baris; baris lama tanpa kunci = nota sendiri (kunci = id)',
  JSON.stringify(BLT.nota.map(function (n) { return n.kunci; })) === JSON.stringify(['g1', kTrx, '9701']) && nT.kunci === kTrx && nT.baris === 3 && nT.n === 887500 && /IR42 Select karung/.test(nT.teks) && /Angsa literan/.test(nT.teks) && /Perahu Layar literan/.test(nT.teks)
  && gT.baris === 2 && gT.n === 3120000 && BLT.kecil === 1 && susunBelanja(KINI, kTrx, []).dipilih === kTrx && susunBelanja(KINI, kTrx, []).isi.length === 3, JSON.stringify([BLT.nota, BLT.kecil]));
var IDT = susunIniDia(KINI, nT.kunci, 'uda feri'); var idTrx = NOTA_TRX.slice(0, 3).map(function (p) { return String(p.id); }).sort();
ok('ini dia (putaran 25): nota trxId → SEMUA 3 barisnya ditulis ulang bernama "Uda Feri"; trxId tetap, TIDAK ada kolom baru (grupNota); rupiah utuh; sesudahnya nota itu hilang UTUH dari Belanja & ditolak "sudah bernama"; baris lama tanpa kunci menamai dirinya saja',
  !IDT.tolak && IDT.dokumen.length === 3 && JSON.stringify(IDT.dokumen.map(function (d) { return String(d.data.id); }).sort()) === JSON.stringify(idTrx)
  && IDT.dokumen.every(function (d) { var asli = NOTA_TRX.find(function (p) { return String(p.id) === String(d.data.id); }); return d.koleksi === 'penjualan' && d.data.namaPelanggan === 'Uda Feri' && d.data.trxId === TRX_BARU && !('grupNota' in d.data) && JSON.stringify(Object.keys(d.data).sort()) === JSON.stringify(Object.keys(asli).sort()) && d.data.hargaTotal === asli.hargaTotal; })
  && /Rp887\.500/.test(IDT.patch.kabar)
  && (function () { var s2 = simpan(); terapkan(IDT); var r = JSON.stringify(susunBelanja(KINI, null, []).nota.map(function (n) { return n.kunci; })) === JSON.stringify(['g1', '9701']) && /sudah bernama/.test(susunIniDia(KINI, kTrx, 'uda feri').tolak || ''); pulih(s2); return r; })()
  && (function () { var L = susunIniDia(KINI, '9701', 'pak darto'); return !L.tolak && L.dokumen.length === 1 && L.dokumen[0].data.id === 9701 && L.dokumen[0].data.namaPelanggan === 'Pak Darto'; })(), JSON.stringify(IDT));
pulih(sTrx);
// ---- JAM & MINGGU
var JM = susunJam(KINI);
ok('jam dinding: yang dikenali & punya jam duduk di jamnya — Rahma 9, Darto 16, Feri 8, Yuni 13, Ibu Rahma Warung 9 (dua orang di jam 9 = lapis berbeda); 12 angka 06–17 dengan 10 = sekarang; jarum 300°; "sekitar jam 9–11" = Rahma & Ibu Rahma Warung (jam 9) + Bu Sri (jam 11, belum dikenali — tetap disebut); sisanya tanpa jam / tak dikenali', JM.orang.length === 5 && JM.orang.find(function (o) { return o.kunci === 'bu rahma'; }).jam === 9 && JM.orang.filter(function (o) { return o.jam === 9; }).map(function (o) { return o.lapis; }).sort().join() === '1,2' && JM.angka.length === 12 && JM.angka.find(function (a) { return a.kini; }).t === 10 && JM.sudut === 300 && JM.sekitar.length === 3 && JM.sekitar[0].kunci === 'bu rahma' && JM.sekitar[1].kunci === 'bu sri' && JM.tanpaJam === 6, JSON.stringify([JM.orang.map(function (o) { return o.kunci + '@' + o.jam; }), JM.sudut, JM.sekitar.map(function (o) { return o.kunci; })]));
var MG = susunMinggu(KINI);
ok('minggu: hari ini Sabtu; hanya yang ≥ 3 kedatangan (Darto, Rahma, Yuni, Bu Sri); Darto 2 dari 3 di Sabtu → KUAT & paling atas (sel "besar"); Rahma 1 dari 5 → "kecil"; Yuni 0 → nol; 7 orang belum tiga kali datang', MG.hariNama === 'Sabtu' && MG.daftar.length === 4 && MG.daftar[0].kunci === 'pak darto' && MG.daftar[0].kuat && MG.daftar[0].sel[5].kelas === 'besar' && MG.daftar[1].kunci === 'bu rahma' && MG.daftar[1].sel[5].kelas === 'kecil' && MG.daftar.find(function (d) { return d.kunci === 'mbak yuni'; }).sel[5].kelas === 'nol' && MG.kuat.join() === 'Pak Darto' && MG.kurang === 7, JSON.stringify(MG.daftar.map(function (d) { return d.kunci + ':' + d.kali; })));
// ---- BENANG
var BN = susunBenang(KINI, null);
ok('benang: Togar → Feri (3×) tergambar: 2 paku (Togar kiri, Feri kanan), 1 benang; baris menyebut bon Feri; jenis urusan dari aturan', BN.pin.length === 2 && BN.pin[0].kunci === 'bang togar' && BN.pin[0].kiri < 50 && BN.pin[1].kiri > 50 && BN.tali.length === 1 && BN.tali[0].kali === '3×' && /Bang Togar datang untuk Uda Feri/.test(BN.baris[0].teks) && /bon Uda Feri Rp1\.450\.000/.test(BN.baris[0].ket) && BN.jenis.length === ATUR_PELANGGAN_BAWAAN.titipDaftar.length, JSON.stringify(BN));
var TT = susunTitip('bu rahma', 'mbak yuni', 'disuruh belanja', W);
ok('benang: catat baru → dokumen pelangganTitip kali 1; catat lagi pasangan+urusan yang sama → dokumen yang SAMA kali 2; orang sama / urusan tak dikenal ditolak; buang → hapus', !TT.tolak && TT.dokumen[0].koleksi === 'pelangganTitip' && TT.dokumen[0].data.kali === 1 && (function () { var s = simpan(); terapkan(TT); var lagi = susunTitipLagi(TT.dokumen[0].data.id, W); var r = lagi.dokumen[0].data.id === TT.dokumen[0].data.id && lagi.dokumen[0].data.kali === 2 && susunBuangTitip(TT.dokumen[0].data.id).hapus[0].id === TT.dokumen[0].data.id; pulih(s); return r; })()
  && /Orang yang sama/.test(susunTitip('bu rahma', 'bu rahma', 'disuruh belanja', W).tolak) && /urusannya/.test(susunTitip('bu rahma', 'mbak yuni', 'ngawur', W).tolak), JSON.stringify(TT));
// ---- HAFALAN
var HF = susunHafalan(KINI, { putaran: 1, no: 0, jawab: null, benar: 0, salah: [], hanya: null }); var HF2 = susunHafalan(KINI, { putaran: 1, no: 0, jawab: null, benar: 0, salah: [], hanya: null });
ok('hafalan: dek = 4 orang bercip, urutan tetap untuk putaran yang sama; kartu pertama punya 3 pilihan (satu benar), pengecoh = yang cirinya paling mirip; belum dijawab → tulisan "siapa ini?"; putaran lain mengacak ulang', HF.dek === 4 && HF.kartu && HF.pilihan.length === 3 && HF.pilihan.filter(function (p) { return p.benar; }).length === 1 && HF.kartu.tulisan === 'siapa ini?' && JSON.stringify(HF.pilihan) === JSON.stringify(HF2.pilihan) && HF.tanpaCiri === 7
  && JSON.stringify(susunHafalan(KINI, { putaran: 2, no: 0, jawab: null, benar: 0, salah: [], hanya: null }).kartu.kunci) !== undefined, JSON.stringify(HF.pilihan));
ok('hafalan: sesudah dijawab salah → hasil menyebut nama & cirinya; putaran "ulang yang salah" hanya memuat yang salah', (function () { var q = { putaran: 1, no: 0, jawab: HF.pilihan.find(function (p) { return !p.benar; }).kunci, benar: 0, salah: [HF.kartu.kunci], hanya: null }; var h = susunHafalan(KINI, q); return /^Bukan\. Ini /.test(h.hasil) && h.kartu.tulisan === HF.kartu.nama && susunHafalan(KINI, { putaran: 2, no: 0, jawab: null, benar: 0, salah: [], hanya: [HF.kartu.kunci] }).dek === 1; })());
// ---- KARTU, ORANG BARU, GABUNG
var KR = kartuOrang(KINI, 'bu rahma');
ok('kartu: ringkasan 5 kali datang · belanja · bon; dikenali → kalimat KR1 "kasir BOLEH"; pola beli terbaca; daftar cip & arah dari aturan', /5 kali datang/.test(KR.ringkas) && /bon Rp37\.500/.test(KR.ringkas) && /BOLEH/.test(KR.bonTeks) && KR.ciriDaftar.length === ATUR_PELANGGAN_BAWAAN.ciriDaftar.length && /Angsa literan/.test(KR.polaTeks), JSON.stringify(KR.ringkas));
var SK = susunSimpanKartu(KINI, 'bu rahma', { nama: 'Bu Rahma', cip: ['ibu-ibu', 'kerudung', 'kerudung'], catatan: '', arah: 'gang masjid', asli: 'Rahmawati', kontak: '0812 0000 4417', biasa: 'Angsa 3 liter' }, W);
var KUNCI_KARTU_LAMA = ['id', 'nama', 'catatan', 'ciri', 'rute'];
ok('kartu: SIMPAN → dokumen pelangganCatatan id = kunci, kolom lama utuh (ciri = cip digabung "ibu-ibu · kerudung", rute = arah) + kolom baru (cip tanpa kembar, arah, asli, kontak, biasa); dikenali', !SK.tolak && SK.dokumen[0].koleksi === 'pelangganCatatan' && SK.dokumen[0].data.id === 'bu rahma' && KUNCI_KARTU_LAMA.every(function (k) { return k in SK.dokumen[0].data; }) && SK.dokumen[0].data.ciri === 'ibu-ibu · kerudung' && SK.dokumen[0].data.rute === 'gang masjid' && SK.dokumen[0].data.cip.length === 2 && SK.dokumen[0].data.asli === 'Rahmawati' && SK.dikenali && !SK.patch.kabarAwas, JSON.stringify(SK));
ok('kartu: ganti nama yang mengubah kuncinya DITOLAK (= memindahkan nota & bon); nomor WA kurang panjang ditolak; kartu kosong tersimpan tapi DISEBUT tidak dikenali (kasir menolak bon)', /SATUKAN/.test(susunSimpanKartu(KINI, 'bu rahma', { nama: 'Ibu Rahma', cip: [] }, W).tolak || '') && /WhatsApp/.test(susunSimpanKartu(KINI, 'bu rahma', { nama: 'Bu Rahma', cip: [], kontak: '0812' }, W).tolak || '')
  && (function () { var r = susunSimpanKartu(KINI, 'mbak yuni', { nama: 'Mbak Yuni', cip: [], catatan: '', arah: '' }, W); return !r.tolak && !r.dikenali && r.patch.kabarAwas && /menolak bon/.test(r.patch.kabar) && r.dokumen[0].data.ciri === ''; })());
ok('orang baru: "Rahma Warung" mirip Bu Rahma & Ibu Rahma Warung (ditawarkan dulu); "Bu Rahma" ditolak sudah ada; "Bu Siti" → kartu kosong id "bu siti"', orangMirip(KINI, 'Rahma Warung').length === 2 && /sudah ada/.test(susunOrangBaru(KINI, 'Bu Rahma', W).tolak) && susunOrangBaru(KINI, 'Bu Siti', W).dokumen[0].data.id === 'bu siti' && susunOrangBaru(KINI, 'B', W).tolak, JSON.stringify(orangMirip(KINI, 'Rahma Warung')));
var RG = rincianGabung(KINI, 'bu rahma', 'ibu rahma warung'); var GB = susunGabung(KINI, 'bu rahma', 'ibu rahma warung', W);
ok('gabung: rincian = 1 nota + kartu lama + kartu gabungan = 3 dokumen, arti menyebut 6 kali datang & belanja gabungan; SATUKAN → nota ditulis ulang atas "Bu Rahma", kartu Ibu Rahma Warung DIHAPUS, catatannya ikut ("dulu juga tercatat sebagai"); sesudahnya nama lama hilang, Bu Rahma 6 kunjungan', RG.n === 3 && /6 kali datang/.test(RG.arti) && /Rp291\.000/.test(RG.arti) && !GB.tolak && GB.dokumen.length === 2 && GB.dokumen[0].koleksi === 'penjualan' && GB.dokumen[0].data.namaPelanggan === 'Bu Rahma' && GB.dokumen[0].data.hargaTotal === 103500 && GB.hapus.length === 1 && GB.hapus[0].id === 'ibu rahma warung' && /warung nasi/.test(GB.dokumen[1].data.catatan) && /dulu juga tercatat sebagai "Ibu Rahma Warung"/.test(GB.dokumen[1].data.catatan)
  && (function () { var s = simpan(); terapkan(GB); var O2 = semuaOrang(KINI); var r = !O2.some(function (b) { return b.kunci === 'ibu rahma warung'; }) && O2.find(function (b) { return b.kunci === 'bu rahma'; }).kunjungan === 6 && pasanganKembar(O2).length === 0; pulih(s); return r; })(), JSON.stringify([RG.n, RG.arti, GB]));
ok('gabung: lebih dari batas satu writeBatch DITOLAK (biarkan terpisah)', (function () { var s = simpan(); var banyak = []; for (var i = 0; i < 200; i++) banyak.push({ id: 5000 + i, tanggal: '2026-08-0' + (1 + (i % 9)), jam: '09:00', namaPelanggan: 'Ibu Rahma Warung', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', hargaTotal: 1000 }); pasok('penjualan', cacheMentah('penjualan').concat(banyak)); var r = susunGabung(KINI, 'bu rahma', 'ibu rahma warung', W); pulih(s); return /terlalu banyak/i.test(r.tolak || '') && !rincianGabung(KINI, 'bu rahma', 'ibu rahma warung').tolak; })());
ok('bukan kembar: dicatat di aturanToko/pelangganKembar → pasangan itu tidak ditawarkan lagi', (function () { var r = susunBukanKembar('bu rahma+ibu rahma warung', W); var s = simpan(); terapkan(r); var t = r.dokumen[0].data.id === 'pelangganKembar' && pasanganKembar(semuaOrang(KINI)).length === 0 && susunWajah(KINI, '').kembar.length === 0; pulih(s); return t; })());
// ---- ATUR
var AT = susunAturPelanggan({ kosongKali: '30', notaBesar: '1.000.000', tagihHari: '7' }, W);
ok('atur: bangku kosong 3,0× · nota besar 1.000.000 · tagih 7 hari tersimpan (id tetap "pelanggan") dan BERLAKU: kosong 6,0× → Bu Rahma tidak lagi kosong; tagih 7 hari → Rahma (10 hari) & Bu Sri (11) jadi "waktunya ditagih"; angka mustahil ditolak; menghapus cip yang masih dipakai ditolak',
  !AT.tolak && AT.dokumen[0].data.id === 'pelanggan' && AT.dokumen[0].data.kosongKali === 30 && AT.dokumen[0].data.notaBesar === 1000000 && AT.dokumen[0].data.ciriDaftar.length === ATUR_PELANGGAN_BAWAAN.ciriDaftar.length && /kosongKali|10/.test(susunAturPelanggan({ kosongKali: '5' }, W).tolak || 'x') && /kerudung/.test(susunAturPelanggan({ ciriDaftar: ATUR_PELANGGAN_BAWAAN.ciriDaftar.filter(function (c) { return c.nama !== 'kerudung'; }) }, W).tolak || '')
  && (function () { var s = simpan(); terapkan(susunAturPelanggan({ kosongKali: '60' }, W)); var r = !semuaOrang(KINI).find(function (b) { return b.kunci === 'bu rahma'; }).kosong && aturPelanggan().kosongKali === 60 && aturPelanggan().dariOwner; pulih(s); terapkan(AT); r = r && aturPelanggan().tagihHari === 7 && semuaBon(KINI).find(function (b) { return b.kunci === 'bu rahma'; }).status === 'perluTagih' && semuaBon(KINI).find(function (b) { return b.kunci === 'bu sri'; }).status === 'perluTagih'; pulih(s); return r; })(), JSON.stringify([AT.tolak, susunAturPelanggan({ kosongKali: '5' }, W).tolak]));
// ---- THR
var TH = susunThr(KINI, 2026);
ok('THR 2026: urut menurut belanja tahun itu (Feri 1.560.000 → Darto 1.380.000 → Yuni 780.000); belum ada yang dapat; Feri "tahun lalu: Sarung"; anggaran 500.000, sisa penuh; 0 diserahkan', TH.daftar[0].kunci === 'uda feri' && TH.daftar[0].belanja === 1560000 && TH.daftar[1].kunci === 'pak darto' && TH.daftar[2].kunci === 'mbak yuni' && TH.dapat.length === 0 && TH.daftar[0].laluTeks === 'tahun lalu: Sarung' && TH.anggaran === 500000 && TH.sisa === 500000 && TH.meterIsi === 0, JSON.stringify(TH.daftar.map(function (d) { return d.kunci + ':' + d.belanja; })));
var BT = susunBeriThr(KINI, 'pak darto', 2026, 'Sarung', '75.000', W);
ok('THR beri: dokumen thrPelanggan {tahun, kunci, nama, bentuk, nilai, tanggal, jam} (kolom catatThrPelanggan) + serah false; sudah ada → ditolak; bentuk kosong ditolak; sesudah diterapkan: 1 orang dapat, terpakai 75.000, meter rencana 15 %', !BT.tolak && ['id', 'tahun', 'kunci', 'nama', 'bentuk', 'nilai', 'tanggal', 'jam', 'serah'].every(function (k) { return k in BT.dokumen[0].data; }) && BT.dokumen[0].data.nilai === 75000 && BT.dokumen[0].data.serah === false && /wajib/.test(susunBeriThr(KINI, 'pak darto', 2026, '', '0', W).tolak)
  && (function () { var s = simpan(); terapkan(BT); var t = susunThr(KINI, 2026); var r = t.dapat.length === 1 && t.terpakai === 75000 && t.meterRencana === 15 && t.meterIsi === 0 && /sudah tercatat/.test(susunBeriThr(KINI, 'pak darto', 2026, 'Mukena', '0', W).tolak); var sr = susunSerahThr(BT.dokumen[0].data.id, W); terapkan(sr); r = r && susunThr(KINI, 2026).meterIsi === 15 && susunThr(KINI, 2026).diserahkan === 1 && susunHapusThr(BT.dokumen[0].data.id).hapus[0].id === BT.dokumen[0].data.id; pulih(s); return r; })(), JSON.stringify(BT));
var US = usulThr(KINI, 2026, 'Sarung');
ok('THR amplop: sisa 500.000 cukup 6 Sarung → 6 orang teratas yang belum kebagian & pernah belanja (dari 7); RENCANAKAN → 6 dokumen; lewat amplop cuma diberi tahu, tidak ditolak', US.muat === 6 && US.calon.length === 6 && US.calon[0].kunci === 'uda feri' && susunUsulThr(KINI, 2026, 'Sarung', W).dokumen.length === 6 && susunBeriThr(KINI, 'pak darto', 2026, 'Sepeda', '600.000', W).lewat === 100000, JSON.stringify(US));
// ---- BON (PL2)
var SB = semuaBon(KINI); var bon = function (k) { return SB.find(function (b) { return b.kunci === k; }); };
ok('bon: status dari aturan owner (tagih 14 hari, macet 180) — Darto umur 14 = "waktunya ditagih"; Feri janji 15 Sep lewat tanpa pembayaran = "janjinya lewat"; Hartawan bon 2022 tanpa pembayaran = "macet"; Bu Lisna bon 2025 tapi BARU membayar 10 Sep = bukan macet; Bimo janji lewat tapi membayar sesudahnya = bukan "janjinya lewat"; Rahma & Bu Sri "masih baru"',
  bon('bu sri').status === 'baru' && bon('pak darto').status === 'perluTagih' && bon('uda feri').status === 'janjiLewat' && bon('pak hartawan').status === 'macet' && bon('bu lisna').status === 'perluTagih' && bon('mas bimo').status === 'perluTagih' && bon('bu rahma').status === 'baru' && /lewat 4 hari/.test(bon('uda feri').ket) && /belum pernah ditagih/.test(bon('pak darto').ket), JSON.stringify(SB.map(function (b) { return b.kunci + ':' + b.status + ':' + b.umur; })));
ok('bon: rincian FIFO — Feri membayar 110.000 → bon 28 Agu sisa 670.000, bon 5 Sep utuh 780.000; Bu Sri membayar 150.000 → bon 100.000 TERTUTUP, tinggal bon 500.000 sisa 450.000 (umur dari 8 Sep = 11 hari); sisa & umur = mesin beku', bon('bu sri').buka.length === 1 && bon('bu sri').buka[0].sisa === 450000 && bon('bu sri').buka[0].nominal === 500000 && bon('bu sri').umur === 11 && bon('uda feri').buka.length === 2 && bon('uda feri').buka[0].sisa === 670000 && bon('uda feri').buka[1].sisa === 780000 && bon('uda feri').sisa === 1450000 && bon('uda feri').umur === 22 && SB.reduce(function (a, b) { return a + b.sisa; }, 0) === hitungPiutang().reduce(function (a, b) { return a + b.sisa; }, 0), JSON.stringify(bon('uda feri').buka));
var BB = susunBon(KINI, null, '');
ok('bon: total 3.917.500 dari 7 nama; buku bawaan = sisa terbesar (Feri) dengan halaman 2 bon + 1 pembayaran urut tanggal; papan: Tagih (Darto, Feri, Lisna, Bimo) · Tunggu (Rahma, Bu Sri) · Macet (Hartawan); ember: Rahma/Darto/Feri/Bimo/Sri 8–30 hari, Lisna & Hartawan > 3 bulan',
  BB.total === 3917500 && BB.berutang === 7 && BB.buku.kunci === 'uda feri' && BB.buku.halaman.length === 3 && BB.buku.halaman[2].jenis === 'bayar' && BB.buku.halaman[0].jenis === 'bon' && BB.papan.filter(function (p) { return p.lajur; }).length === 3 && BB.papan[0].n === 4 && BB.papan.find(function (p) { return p.lajur && /Tunggu/.test(p.judul); }).n === 2 && BB.papan.find(function (p) { return p.lajur && /Macet/.test(p.judul); }).n === 1
  && BB.ember[1].n === 5 && BB.ember[3].n === 2 && susunBon(KINI, null, 'e4').perUmur.length === 2 && susunBon(KINI, null, 'e4').perUmur[0].kunci === 'pak hartawan', JSON.stringify([BB.total, BB.buku, BB.papan.map(function (p) { return p.lajur ? 'L:' + p.judul + ':' + p.n : p.kunci; }), BB.ember]));
var PT = pesanTagih(KINI, 'uda feri');
ok('tagih: pesan = kalimat sistem lama (kop, rincian bon dengan sisa, total, tertunggak, salam owner); nomor dari kartu 0812… → 62812… di wa.me; Rahma tanpa nomor → WhatsApp menanyakan tujuan', PT.baris[0] === '*TOKO BERAS M.IQBAL*' && PT.baris[1] === 'Catatan belanja a.n. Uda Feri' && /Rp780\.000 \(sisa Rp670\.000\)/.test(PT.baris[4]) && PT.baris.indexOf('*Total sisa: Rp1.450.000*') >= 0 && PT.baris.indexOf('(tertunggak 22 hari)') >= 0 && PT.baris[PT.baris.length - 1] === ATUR_PELANGGAN_BAWAAN.salamTagih && PT.nomor === '6281200000001' && PT.url.indexOf('https://wa.me/6281200000001?text=') === 0
  && pesanTagih(KINI, 'bu rahma').nomor === '' && pesanTagih(KINI, 'bu rahma').url.indexOf('https://wa.me/?text=') === 0 && /menanyakan tujuannya/.test(pesanTagih(KINI, 'bu rahma').tujuan) && pesanTagih(KINI, 'bang togar') === null, JSON.stringify(PT.baris));
var TG = susunTagih(KINI, 'uda feri', 7, W);
ok('tagih: dicatat ke tagihPelanggan {kunci, nama, tanggal, jam, janji = +7 hari, sisa}; sesudahnya status Feri = "menunggu janji"; tanpa janji → janji null', !TG.tolak && TG.dokumen[0].koleksi === 'tagihPelanggan' && TG.dokumen[0].data.janji === '2026-09-26' && TG.dokumen[0].data.sisa === 1450000 && susunTagih(KINI, 'uda feri', 0, W).dokumen[0].data.janji === null && (function () { var s = simpan(); terapkan(TG); var r = semuaBon(KINI).find(function (b) { return b.kunci === 'uda feri'; }).status === 'menunggu'; pulih(s); return r; })() && /Tidak ada yang perlu ditagih/.test(susunTagih(KINI, 'bang togar', 7, W).tolak), JSON.stringify(TG));
var BY = susunBayarBon(KINI, 'pak darto', '1.080.000', 'Tunai', '', 'Bang Togar', W);
var KUNCI_BAYAR = ['id', 'tipe', 'namaPelanggan', 'nominal', 'tanggal', 'jam', 'caraBayar', 'catatan', 'dicatatDi'];
ok('bayar: dokumen piutangMutasi PERSIS simpanBayarPiutang (+ dibawaOleh karena pengantarnya orang lain); Darto LUNAS; sesudah diterapkan mesin beku membaca sisa 0 dan ia keluar dari daftar berutang; melebihi sisa & nol ditolak; pengantar = dirinya tidak dicatat', !BY.tolak && BY.dokumen[0].koleksi === 'piutangMutasi' && KUNCI_BAYAR.every(function (k) { return k in BY.dokumen[0].data; }) && Object.keys(BY.dokumen[0].data).sort().join(',') === KUNCI_BAYAR.concat(['dibawaOleh']).sort().join(',') && BY.dokumen[0].data.tipe === 'bayar' && BY.dokumen[0].data.caraBayar === 'Tunai' && BY.dokumen[0].data.dibawaOleh === 'Bang Togar' && /LUNAS/.test(BY.patch.kabar)
  && (function () { var s = simpan(); terapkan(BY); var r = hitungPiutang().find(function (x) { return x.kunci === 'pak darto'; }).sisa === 0 && !susunBon(KINI, null, '').papan.some(function (p) { return p.kunci === 'pak darto'; }); pulih(s); return r; })() && /melebihi sisa/.test(susunBayarBon(KINI, 'pak darto', '2.000.000', 'Tunai', '', '', W).tolak) && /Ketik jumlah/.test(susunBayarBon(KINI, 'pak darto', '', 'Tunai', '', '', W).tolak)
  && !('dibawaOleh' in susunBayarBon(KINI, 'pak darto', '100.000', 'QRIS', 'x', 'Pak Darto', W).dokumen[0].data) && !/LUNAS/.test(susunBayarBon(KINI, 'pak darto', '100.000', 'QRIS', 'x', '', W).patch.kabar), JSON.stringify(BY));
// audit 39b no. 3: bayar bon lewat QRIS — kalimatnya menyebut potongan QRIS (MDR) yang dicatat saat tutup hari; tunai tidak
var BYQ = susunBayarBon(KINI, 'pak darto', '100.000', 'QRIS', '', '', W), BYT = susunBayarBon(KINI, 'pak darto', '100.000', 'Tunai', '', '', W);
ok('39b-3 bayar bon QRIS: caraBayar QRIS, "rekening bertambah" + "potongan QRIS (MDR)-nya, kalau ada, dicatat saat tutup hari"; tunai: "laci bertambah" tanpa kalimat potongan', !BYQ.tolak && BYQ.dokumen[0].data.caraBayar === 'QRIS' && /rekening bertambah/.test(BYQ.patch.kabar) && /potongan QRIS \(MDR\)-nya, kalau ada, dicatat saat tutup hari/.test(BYQ.patch.kabar) && /laci bertambah/.test(BYT.patch.kabar) && !/potongan QRIS/.test(BYT.patch.kabar), [BYQ.patch && BYQ.patch.kabar, BYT.patch && BYT.patch.kabar]);
// tinjauan no. 3 T6: hari ini SUDAH ditutup → uang (dan potongan QRIS) pembayaran ini baru ikut kas kalau tutup hari diulang — kalimatnya berkata begitu
var tutupLama = JSON.parse(JSON.stringify(ambilTutupHari() || [])); pasok('tutupHari', tutupLama.concat([{ id: W.tanggal, tanggal: W.tanggal, jam: '21:00', omzet: 0 }]));
var BYQ2 = susunBayarBon(KINI, 'pak darto', '100.000', 'QRIS', '', '', W), BYT2 = susunBayarBon(KINI, 'pak darto', '100.000', 'Tunai', '', '', W); pasok('tutupHari', tutupLama);
ok('39b-3 T6 hari sudah ditutup jam 21:00: QRIS "hari ini SUDAH ditutup jam 21:00 — uang ini dan potongan QRIS (MDR)-nya baru ikut hitungan kas kalau tutup hari diulang"; Tunai "uang ini baru ikut …"; tanpa janji "dicatat saat tutup hari"', /hari ini SUDAH ditutup jam 21:00 — uang ini dan potongan QRIS \(MDR\)-nya baru ikut hitungan kas kalau tutup hari diulang/.test(BYQ2.patch.kabar) && !/dicatat saat tutup hari/.test(BYQ2.patch.kabar) && /hari ini SUDAH ditutup jam 21:00 — uang ini baru ikut hitungan kas/.test(BYT2.patch.kabar) && !/SUDAH ditutup/.test(BYQ.patch.kabar), [BYQ2.patch && BYQ2.patch.kabar, BYT2.patch && BYT2.patch.kabar]);
var HB0 = susunHapusBon(KINI, 'pak hartawan', '250.000', 'pindah, tidak bisa dihubungi', W, false); var HB = susunHapusBon(KINI, 'pak hartawan', '250.000', 'pindah, tidak bisa dihubungi', W, true);
ok('hapus buku: alasan wajib; ketukan pertama DITANYA dengan kalimat "BUKAN uang masuk … KERUGIAN"; ketukan kedua → dokumen tipe hapusBuku persis simpanHapusBuku; sesudahnya mesin beku membaca sisa Hartawan 0; melebihi sisa ditolak', /wajib/.test(susunHapusBon(KINI, 'pak hartawan', '250.000', '', W, true).tolak) && HB0.perluYakin === true && /BUKAN uang masuk/.test(HB0.tolak) && /KERUGIAN/.test(HB0.tolak) && !HB.tolak && Object.keys(HB.dokumen[0].data).sort().join(',') === ['id', 'tipe', 'namaPelanggan', 'nominal', 'alasan', 'tanggal', 'jam', 'dicatatDi'].sort().join(',') && HB.dokumen[0].data.tipe === 'hapusBuku'
  && (function () { var s = simpan(); terapkan(HB); var r = hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }).sisa === 0 && hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }).dihapus === 250000; pulih(s); return r; })() && /melebihi sisa/.test(susunHapusBon(KINI, 'pak hartawan', '300.000', 'x', W, true).tolak), JSON.stringify([HB0, HB]));
// ---- PUTARAN 21 (owner 23 Sep): ciri serinci mungkin & sketsanya; nama paku benang utuh; benang di kartu; urusan ojek/kurir
var SK1 = sketsa({ cip: ['sawo matang', 'kumis', 'gemuk', 'botak', 'naik motor', '40-an', 'Sunda'] }); var SK2 = sketsa({ cip: ['kerudung', 'kulit putih', 'kurus', 'tinggi', 'kacamata'] }); var SK3 = sketsa({ cip: ['brewok', 'rambut panjang', 'kulit gelap', 'pendek'] });
ok('P21 ciri (DIGANTI 23b): 7 kelompok (umur, perawakan, wajah & rambut, yang dipakai, naik, beli) — warna kulit & suku/logat TIDAK ada lagi; tiap cip bawaan punya kelompoknya & tidak satu pun terlarang; urusan titipan bawaan memuat ojek / kurir langganan', TANYA_CIRI.length === 7 && !TANYA_CIRI.some(function (t) { return GRUP_DICABUT.indexOf(t[0]) >= 0; }) && ATUR_PELANGGAN_BAWAAN.ciriDaftar.every(function (c) { return TANYA_CIRI.some(function (t) { return t[0] === c.grup; }) && !cipTerlarang(c.nama) && GRUP_DICABUT.indexOf(c.grup) < 0; }) && ATUR_PELANGGAN_BAWAAN.ciriDaftar.length > 40 && ATUR_PELANGGAN_BAWAAN.titipDaftar.indexOf('ojek / kurir langganan') >= 0);
ok('P21 sketsa ikut ciri (DIGANTI 23b: warna kulit tidak lagi dibaca — satu nada netral): kumis, gemuk, botak (tanpa rambut), motor; kerudung + kurus + tinggi + kacamata; brewok = kumis & janggut, rambut panjang, pendek; cip kulit/suku tidak meninggalkan jejak apa pun di bahan sketsa', !('kulit' in SK1) && !('kulit' in SK2) && !('kulit' in SK3) && SK1.kumis && !SK1.janggut && SK1.gemuk && SK1.botak && !SK1.rambut && SK1.naik === 'motor' && SK2.kerudung && SK2.kurus && SK2.tinggi && SK2.kacamata && !SK2.rambut && SK3.kumis && SK3.janggut && SK3.panjang && SK3.pendek && SK3.rambut
  && JSON.stringify(sketsa({ cip: ['kumis', 'sawo matang', 'Sunda', 'kulit gelap'] })) === JSON.stringify(sketsa({ cip: ['kumis'] })), JSON.stringify([SK1, SK2, SK3]));
ok('P21 nama paku benang: "Al - Yamin" utuh jadi "Al-Yamin" (bukan "Al -"); nama pendek utuh; nama panjang = dua kata pertama yang berhuruf', plNamaPendek('Al - Yamin') === 'Al-Yamin' && plNamaPendek('Bang Togar') === 'Bang Togar' && plNamaPendek('Ibu Rahma Warung Makan Sederhana') === 'Ibu Rahma' && plNamaPendek('H. - Ahmad Sudirman Jaya') === 'H.-Ahmad Sudirman');
var BO = benangOrang(KINI, 'uda feri'); var BT2 = benangOrang(KINI, 'bang togar');
ok('P21 benang di kartu: kartu Feri menyebut Togar yang datang (3×); kartu Togar menyebut ia datang untuk Feri; orang tanpa benang → tidak ada', BO.ada && BO.dari.length === 1 && BO.dari[0].nama === 'Bang Togar' && BO.dari[0].kali === 3 && BT2.untuk.length === 1 && BT2.untuk[0].nama === 'Uda Feri' && kartuOrang(KINI, 'uda feri').benang.ada && !benangOrang(KINI, 'pak darto').ada, JSON.stringify([BO, BT2]));
// ---- PUTARAN 22: hapus nama salah ketik (owner 23 Sep: "b", "40000")
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sTypo1', tanggal: '2026-09-18', jam: '09:00', caraBayar: 'Tunai', namaPelanggan: 'b', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 2, totalKg: 1.64, hargaTotal: 27000, hppTotalSaatJual: 21000 } }, { koleksi: 'penjualan', data: { id: 'sTypo2', tanggal: '2026-09-19', jam: '08:00', caraBayar: 'Tunai', namaPelanggan: 'B', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 1, totalKg: 0.82, hargaTotal: 13500, hppTotalSaatJual: 10500 } }]);
var RHN = rincianHapusNama(KINI, 'b'); var HN0 = susunHapusNama(KINI, 'b', W, false); var HN = susunHapusNama(KINI, 'b', W, true);
var nB = RHN.penjualan.length;
ok('P22 hapus nama "b": rincian ≥ 2 nota ("b" & "B" satu kunci); ketukan pertama DITANYA; ketukan kedua → semua notanya ditulis ulang TANPA nama dengan jejak namaDihapus, rupiah tetap; nama berbon (Darto) & nama dengan benang+kartu (Feri) DITOLAK dihapus', !RHN.tolak && nB >= 2 && HN0.perluYakin === true && !HN.tolak && HN.dokumen.length === nB && HN.dokumen.every(function (d) { return d.koleksi === 'penjualan' && d.data.namaPelanggan === '' && /^b$/i.test(d.data.namaDihapus) && d.data.hargaTotal > 0; }) && HN.hapus.length === 0
  && /buku bon/.test(rincianHapusNama(KINI, 'pak darto').tolak) && /buku bon|THR|tagihan/.test(rincianHapusNama(KINI, 'uda feri').tolak || 'x'), JSON.stringify([RHN.arti, HN0.tolak, rincianHapusNama(KINI, 'uda feri').tolak]));
(function () { var s0 = simpan(); terapkan(HN); ok('P22 sesudah dihapus: "b" hilang dari daftar orang; omzet nota tetap terhitung (tanpa nama)', !semuaOrang(KINI).some(function (o) { return o.kunci === 'b'; }) && ambilPenjualanSemua().filter(function (p) { return p.namaDihapus; }).length === nB); pulih(s0); })();
terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sTypo1' }, { koleksi: 'penjualan', hapus: 'sTypo2' }]);
// ---- PUTARAN 23b (owner 23 Sep malam): cip warna kulit & suku/logat DICABUT — pintu ditutup, layar tak pernah menanyakan/menampilkan, data lama dibersihkan
(function () {
  var s23 = simpan(); var cadAwal = cacheMentah('cadangan').slice(); var logAwal = cacheMentah('log').slice();
  var larang = function (t) { return String(t || '').split(/\s*[·,;]\s*/).some(function (x) { return cipTerlarang(x); }); };
  var tolakAtur = function (tambah) { var r = susunAturPelanggan({ ciriDaftar: ATUR_PELANGGAN_BAWAAN.ciriDaftar.concat([tambah]) }, W); return r.tolak === TOLAK_CIRI_DICABUT; };
  ok('P23b pintu Atur: kelompok kulit / asal DITOLAK dengan kalimat owner; cip berkata kulit, suku, logat, ras, etnis (huruf besar-kecil apa saja) & cip bawaan lama ("sawo matang") DITOLAK walau ditaruh di kelompok lain; "suka beras merah" (beras ≠ ras) & "berkacamata" LOLOS',
    tolakAtur({ nama: 'hitam', grup: 'kulit' }) && tolakAtur({ nama: 'orang pesisir', grup: 'asal' }) && tolakAtur({ nama: 'kulit sawo', grup: 'wajah' }) && tolakAtur({ nama: 'SUKU pedalaman', grup: 'lain' }) && tolakAtur({ nama: 'Logat Medan', grup: 'lain' }) && tolakAtur({ nama: 'ras campuran', grup: 'lain' }) && tolakAtur({ nama: 'Etnis', grup: 'lain' }) && tolakAtur({ nama: 'sawo matang', grup: 'wajah' })
    && !susunAturPelanggan({ ciriDaftar: ATUR_PELANGGAN_BAWAAN.ciriDaftar.concat([{ nama: 'suka beras merah', grup: 'beli' }, { nama: 'berkacamata', grup: 'tampak' }]) }, W).tolak, TOLAK_CIRI_DICABUT);
  // setelan owner tersimpan SEBELUM keputusan (salinan bawaan lama + cip owner sendiri di kelompok kulit) & kartu-kartu yang memakainya
  var ciriLama = ATUR_PELANGGAN_BAWAAN.ciriDaftar.concat([{ nama: 'sawo matang', grup: 'kulit' }, { nama: 'Sunda', grup: 'asal' }, { nama: 'hitam manis', grup: 'kulit' }, { nama: 'berkacamata', grup: 'tampak' }, { nama: 'suka beras merah', grup: 'beli' }]);
  var aturLama = { id: 'pelanggan', tanggal: '2026-09-22', jam: '10:00', kosongKali: 20, notaBesar: 500000, tagihHari: 14, macetHari: 180, anggaranThr: 500000, ciriDaftar: ciriLama, salamTagih: 'salam', diubahOleh: 'Owner', diubahPada: '2026-09-22T03:00:00.000Z' };
  var cA = ['ibu-ibu', 'sawo matang', 'berkacamata', 'Sunda', 'hitam manis', 'suka beras merah', 'kerudung'];
  var KA = { id: 'bu tuti', nama: 'Bu Tuti', catatan: 'langganan pagi', ciri: cA.join(' · '), rute: '', cip: cA, arah: '', asli: '', kontak: '0812 0000 7777', biasa: 'literan Angsa', diubahPada: '2026-09-20T01:00:00.000Z', diubahOleh: 'Owner', diubahPerangkat: 'Mac', oleh: 'Owner', perangkat: 'Mac' };
  var KB = { id: 'pak oni', nama: 'Pak Oni', catatan: '', ciri: 'bapak-bapak · kulit gelap · peci', rute: '' };   // kartu gaya lama: cuma teks ciri
  var KC = { id: 'mas ucok', nama: 'Mas Ucok', catatan: '', ciri: 'kulit putih', rute: '', cip: ['kulit putih'], arah: '', asli: '', kontak: '', biasa: '' };
  var KD = { id: 'teh imas', nama: 'Teh Imas', catatan: 'orang Madura, ramah', ciri: 'Jawa', rute: '', cip: ['Jawa'], arah: '', asli: '', kontak: '', biasa: '' };
  var KF = { id: 'bang udin', nama: 'Bang Udin', catatan: '', ciri: 'peci · Batak', rute: '', cip: ['peci', 'Batak'], arah: '', asli: '', kontak: '', biasa: '' };   // sesudahnya tinggal SATU cip
  var KE = { id: 'bu lilis', nama: 'Bu Lilis', catatan: 'jual jaket kulit', ciri: 'ibu-ibu', rute: '', cip: ['ibu-ibu'], arah: '', asli: '', kontak: '', biasa: '' };
  pasok('aturanToko', [aturLama]); pasok('pelangganCatatan', cacheMentah('pelangganCat').concat([KA, KB, KC, KD, KE, KF]));
  pasok('logAktivitas', [{ id: 1, pada: '2026-09-22T03:00:00.000Z', aksi: 'tulis', koleksi: 'pelangganCatatan', idDok: 'x', ringkas: 'Bu Tuti · sawo matang' }, { id: 2, pada: '2026-09-22T03:01:00.000Z', aksi: 'tulis', koleksi: 'penjualan', idDok: 'y', ringkas: 'Angsa · Rp10.000' }]);
  var AP = aturPelanggan();
  ok('P23b setelan tersimpan yang masih memuat cip dicabut TIDAK sampai ke layar: daftar cip Atur/kartu tanpa sawo matang, Sunda, hitam manis (cip owner di kelompok kulit); berkacamata & suka beras merah tetap ada',
    !AP.ciriDaftar.some(function (c) { return cipTerlarang(c.nama) || GRUP_DICABUT.indexOf(c.grup) >= 0; }) && AP.ciriDaftar.some(function (c) { return c.nama === 'berkacamata'; }) && AP.ciriDaftar.some(function (c) { return c.nama === 'suka beras merah'; }) && cipTerlarang('hitam manis') && !cipTerlarang('berkacamata'), JSON.stringify(AP.ciriDaftar.slice(-4)));
  var jawab = [], ditanya = []; for (var i = 0; i < 80; i++) { var T = susunTampah(KINI, jawab); if (!T.tanya) break; ditanya.push(T.tanya.c + '|' + T.tanya.grup + '|' + T.label); jawab.push({ c: T.tanya.c, j: 'entah' }); }
  var dekH = susunHafalan(KINI, null).dek; var hafal = []; for (var n = 0; n < dekH; n++) { var H = susunHafalan(KINI, { putaran: 1, no: n, jawab: null, benar: 0, salah: [], hanya: null }); hafal.push(H.kartu.ciriTeks); var H2 = susunHafalan(KINI, { putaran: 1, no: n, jawab: 'x', benar: 0, salah: [], hanya: null }); hafal.push(H2.hasil); }
  var wajah = susunWajah(KINI, '').daftar.map(function (b) { return b.sub; }); var kA = kartuOrang(KINI, 'bu tuti');
  ok('P23b Tampah, Hafalan & Wajah TIDAK PERNAH menanyakan/menampilkan kelompok yang dicabut: seluruh pertanyaan Tampah (dijawab "tidak kelihatan" sampai habis), seluruh dek Hafalan (ciri & jawaban), julukan Wajah, dan cip di kartu — nol cip terlarang; berkacamata tetap ditampilkan',
    ditanya.length >= 5 && !ditanya.some(function (q) { return larang(q.split('|')[0]) || GRUP_DICABUT.indexOf(q.split('|')[1]) >= 0 || /kulit|suku/i.test(q.split('|')[2]); }) && dekH >= 5 && !hafal.some(larang) && !wajah.some(larang)
    && !kA.cip.some(function (c) { return cipTerlarang(c); }) && kA.cip.indexOf('berkacamata') >= 0 && kA.cip.indexOf('suka beras merah') >= 0, JSON.stringify({ ditanya: ditanya, kA: kA.cip }));
  ok('P23b sketsa & kartu di layar: svg sketsa tanpa kelas nada kulit (k1–k4), CSS nada kulit dibuang, kalimat Wajah tidak menyebut warna kulit; kolom catatan kartu punya keterangan tetap "Jangan tulis suku, agama, warna kulit, atau kesehatan."',
    LAYAR_PL.js.indexOf('sk.kulit') < 0 && !/' k' \+/.test(LAYAR_PL.js) && !/\.sk\.k[1-4]/.test(LAYAR_PL.css) && LAYAR_PL.js.indexOf('ciri di kartu: warna kulit') < 0 && LAYAR_PL.js.indexOf('Jangan tulis suku, agama, warna kulit, atau kesehatan.') >= 0);
  var SKD = susunSimpanKartu(KINI, 'pak darto', { nama: 'Pak Darto', cip: ['bapak-bapak', 'sawo matang', 'peci', 'Batak'], catatan: 'beli tiap sore' }, W);
  ok('P23b kartu: cip "sawo matang" & "Batak" TIDAK lolos ke kartu yang disimpan — cip & ciri gabungannya bersih, cip lain utuh', !SKD.tolak && JSON.stringify(SKD.dokumen[0].data.cip) === JSON.stringify(['bapak-bapak', 'peci']) && SKD.dokumen[0].data.ciri === 'bapak-bapak · peci', JSON.stringify(SKD.dokumen && SKD.dokumen[0].data));
  var ATS = susunAturPelanggan({ kosongKali: '30' }, W);
  ok('P23b simpan Atur biasa: cip owner di kelompok lama yang MASIH menempel di kartu dibawa apa adanya (bukti terlarangnya tidak hilang sebelum dibersihkan) — tidak pernah tampil',
    !ATS.tolak && ATS.dokumen[0].data.ciriDaftar.some(function (c) { return c.nama === 'hitam manis' && c.grup === 'kulit'; }) && (function () { var s0 = simpan(); terapkan(ATS); var r = cipTerlarang('hitam manis') && kartuOrang(KINI, 'bu tuti').cip.indexOf('hitam manis') < 0 && !aturPelanggan().ciriDaftar.some(function (c) { return c.nama === 'hitam manis'; }); pulih(s0); return r; })());
  // ---- pratinjau: TIDAK menulis apa pun
  pasok('cadanganCatatan', []);
  var jepret = function () { return JSON.stringify([simpan(), cacheMentah('cadangan'), cacheMentah('log')]); }; var j0 = jepret(); var R = rincianBersihkanCiri(KINI); var j1 = jepret();
  var nm = function (xs) { return xs.map(function (k) { return k.nama; }).sort().join(','); };
  ok('P23b pratinjau menulis NOL dokumen & menghitung benar: 5 kartu (termasuk kartu gaya lama yang cuma punya teks ciri), 7 cip dibuang (berkacamata & suka beras merah TIDAK), setelan owner ikut (3 cip), 1 batch; teks bebas cuma dilaporkan (Teh Imas catatan "Madura", Bu Lilis "jaket kulit"); jejak log yang menyebut ciri itu = 1',
    j0 === j1 && !R.ubahKolom && R.kartu.length === 5 && R.cip === 7 && R.atur && R.aturBuang === 3 && R.batch === 1 && R.ada && R.bebas.length === 2 && nm(R.bebas) === 'Bu Lilis,Teh Imas' && R.bebas.every(function (x) { return x.kolom.join() === 'catatan'; }) && R.logKena === 1 && !R.cadangan, JSON.stringify({ n: R.kartu.length, cip: R.cip, atur: R.aturBuang, bebas: R.bebas, log: R.logKena }));
  ok('P23b hitungan "tanpa cip sama sekali": Mas Ucok (cuma kulit putih) & Teh Imas (cuma Jawa) = 2 orang (Bang Udin tinggal satu cip = BUKAN tanpa cip); yang juga jadi "belum dikenal" di KR1 sistem lama = Mas Ucok saja (Teh Imas masih punya catatan)', nm(R.tanpaCip) === 'Mas Ucok,Teh Imas' && nm(R.belumDikenal) === 'Mas Ucok', nm(R.tanpaCip) + ' / ' + nm(R.belumDikenal));
  // ---- syarat cadangan hari ini & dua ketukan
  var tanpa = susunBersihkanCiri(KINI, true); pasok('cadanganCatatan', [{ id: 1, tanggal: '2026-09-18', jam: '20:00', ok: true }]); var kemarin = susunBersihkanCiri(KINI, true);
  pasok('cadanganCatatan', [{ id: 2, tanggal: '2026-09-19', jam: '08:00', ok: false }]); var gagalC = susunBersihkanCiri(KINI, true);
  pasok('cadanganCatatan', [{ id: 3, tanggal: '2026-09-19', jam: '09:30', ok: true, nama: 'backup-batch-miqbal-2026-09-19.json' }]); var sekali = susunBersihkanCiri(KINI, false); var BS = susunBersihkanCiri(KINI, true);
  ok('P23b tombol MATI tanpa cadangan hari ini ("Unduh cadangan dulu dari Menu › Toko ini › Cadangan & simpanan."): tanpa catatan, cadangan kemarin, cadangan hari ini yang gagal — semua ditolak; dengan cadangan hari ini: ketukan pertama DITANYA, kedua baru menyusun tulisan',
    tanpa.tolak === 'Unduh cadangan dulu dari Menu › Toko ini › Cadangan & simpanan.' && !tanpa.ubahKolom && kemarin.tolak === tanpa.tolak && gagalC.tolak === tanpa.tolak && sekali.perluYakin === true && !sekali.ubahKolom && !BS.tolak && BS.ubahKolom.length === 1, JSON.stringify([tanpa.tolak, kemarin.tolak, gagalC.tolak, sekali.tolak]));
  var semuaUbah = BS.ubahKolom[0]; var akhir = semuaUbah[semuaUbah.length - 1];
  ok('P23b yang ditulis cuma kolom cip & ciri (kartu gaya lama: ciri saja) dan ciriDaftar setelan — setelan di URUTAN TERAKHIR; baris log satu, berisi JUMLAH saja tanpa isi cip yang dibuang',
    semuaUbah.length === 6 && semuaUbah.slice(0, 5).every(function (u) { return u.koleksi === 'pelangganCatatan' && Object.keys(u.kolom).every(function (k) { return k === 'cip' || k === 'ciri'; }); }) && semuaUbah.filter(function (u) { return Object.keys(u.kolom).join() === 'ciri'; }).length === 1 && akhir.koleksi === 'aturanToko' && Object.keys(akhir.kolom).join() === 'ciriDaftar'
    && /5 kartu · 7 cip dibuang · setelan cip ikut \(3\)/.test(BS.ringkas) && !/sawo|sunda|hitam|jawa|madura|kulit|batak/i.test(BS.ringkas), BS.ringkas);
  // ---- bersihkan (penulis simulasi = update kolom): kolom lain byte-sama
  var buang2 = function (d) { var x = JSON.parse(JSON.stringify(d)); delete x.cip; delete x.ciri; return JSON.stringify(x); }; var sblm = {}; cacheMentah('pelangganCat').forEach(function (c) { sblm[c.id] = c; }); var atSblm = cacheMentah('aturan')[0];
  var HS = perbaruiKolom(BS.ubahKolom, BS.ringkas); var ssd = {}; cacheMentah('pelangganCat').forEach(function (c) { ssd[c.id] = c; }); var atSsd = cacheMentah('aturan').find(function (d) { return d.id === 'pelanggan'; });
  var dibersihkan = ['bu tuti', 'pak oni', 'mas ucok', 'teh imas', 'bang udin'];
  ok('P23b BERSIHKAN membuang TEPAT cip terlarang: Bu Tuti tinggal ibu-ibu · berkacamata · suka beras merah · kerudung (urutan tetap), Pak Oni (gaya lama) ciri tanpa kulit gelap & tetap tanpa larik cip, Mas Ucok & Teh Imas kosong; ciri = gabungan cip sesudahnya; SEMUA kolom lain byte-sama; kartu yang tak kena (Darto, Lilis) utuh; setelan: 3 cip terlarang hilang, kolom lainnya byte-sama',
    JSON.stringify(ssd['bu tuti'].cip) === JSON.stringify(['ibu-ibu', 'berkacamata', 'suka beras merah', 'kerudung']) && ssd['bu tuti'].ciri === ssd['bu tuti'].cip.join(' · ') && ssd['pak oni'].ciri === 'bapak-bapak · peci' && !('cip' in ssd['pak oni'])
    && JSON.stringify(ssd['bang udin'].cip) === '["peci"]' && ssd['bang udin'].ciri === 'peci' && ssd['mas ucok'].cip.length === 0 && ssd['mas ucok'].ciri === '' && ssd['teh imas'].cip.length === 0 && ssd['teh imas'].ciri === '' && dibersihkan.every(function (id) { return buang2(ssd[id]) === buang2(sblm[id]); })
    && JSON.stringify(ssd['pak darto']) === JSON.stringify(sblm['pak darto']) && JSON.stringify(ssd['bu lilis']) === JSON.stringify(sblm['bu lilis'])
    && atSsd.ciriDaftar.length === atSblm.ciriDaftar.length - 3 && !atSsd.ciriDaftar.some(function (c) { return c.nama === 'sawo matang' || c.nama === 'Sunda' || c.nama === 'hitam manis'; }) && atSsd.ciriDaftar.some(function (c) { return c.nama === 'berkacamata'; })
    && (function () { var a = JSON.parse(JSON.stringify(atSsd)), b = JSON.parse(JSON.stringify(atSblm)); delete a.ciriDaftar; delete b.ciriDaftar; return JSON.stringify(a) === JSON.stringify(b); })(), JSON.stringify([ssd['bu tuti'], ssd['pak oni']]));
  var R2 = rincianBersihkanCiri(KINI);
  ok('P23b sesudah bersih: tidak ada lagi yang perlu dibersihkan (lembar hilang), teks bebas tetap dilaporkan & TIDAK diubah; Mas Ucok kini "belum dikenal" di KR1 sistem lama, Teh Imas tetap dikenal lewat catatan',
    !R2.ada && R2.kartu.length === 0 && R2.bebas.length === 2 && ssd['teh imas'].catatan === 'orang Madura, ramah' && ssd['bu lilis'].catatan === 'jual jaket kulit' && !catatanPelangganBerisi(ssd['mas ucok']) && catatanPelangganBerisi(ssd['teh imas']) && /tidak ada yang perlu/.test(susunBersihkanCiri(KINI, true).tolak) && typeof HS.then === 'function', JSON.stringify({ ada: R2.ada, n: R2.kartu.length, bebas: R2.bebas.length }));
  // ---- batas satu writeBatch: 201 kartu → 2 batch (200 + 1)
  var banyak = []; for (var b = 0; b < 201; b++) banyak.push({ id: 'uji' + b, nama: 'Uji ' + b, catatan: '', ciri: 'Sunda', rute: '', cip: ['Sunda'] }); pasok('pelangganCatatan', cacheMentah('pelangganCat').concat(banyak));
  var BB = susunBersihkanCiri(KINI, true);
  ok('P23b batas batch: 201 kartu → 2 batch (200 + 1), dilaporkan per batch', !BB.tolak && BB.ubahKolom.length === 2 && BB.ubahKolom[0].length === BATAS_BERSIHKAN && BB.ubahKolom[1].length === 1 && BB.rincian.batch === 2, BB.tolak);
  pulih(s23); pasok('cadanganCatatan', cadAwal); pasok('logAktivitas', logAwal);
})();
var LB = lembarBon(KINI, 'uda feri');
ok('lembar orang: rincian 2 bon terbuka (yang pertama "dari Rp780.000"), riwayat memuat pembayaran & tagihan (terbaru dulu), pilihan alasan hapus dari aturan', LB.rinci.length === 2 && /dari Rp780\.000/.test(LB.rinci[0].teks) && LB.rinci[0].n === 670000 && LB.riwayat.length === 2 && /ditagih · janji/.test(LB.riwayat[0].teks) && LB.riwayat[1].n === -110000 && LB.alasanPilihan.length === 4, JSON.stringify(LB.riwayat));
// ---- 39b no. 4: SISA NEGATIF BERBUNYI — dokumen bayar MELEBIHI sisa disuntik langsung (seperti dari kasir.html berkatalog basi), bukan lewat susunBayarBon
(function () {
  var s0 = simpan(); var B0 = susunBon(KINI, null, '');
  pasok('piutangMutasi', cacheMentah('piutang').concat([{ id: 9951, tipe: 'bayar', namaPelanggan: 'Pak Hartawan', nominal: 280000, tanggal: '2026-09-19', jam: '09:30', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  var mesin = hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }); var b = semuaBon(KINI).find(function (x) { return x.kunci === 'pak hartawan'; }); var B1 = susunBon(KINI, null, '');
  ok('39b-4 mesin beku TIDAK diubah: sisa Hartawan = 250.000 − 280.000 = −30.000 (negatif apa adanya)', mesin && mesin.sisa === -30000, mesin && mesin.sisa);
  ok('39b-4 buku bon: status "lebih", cap "kelebihan bayar", ket "kelebihan bayar Rp30.000 — uang pelanggan dipegang toko" — BUKAN "lunas"', b && b.status === 'lebih' && b.cap === 'kelebihan bayar' && b.ket === 'kelebihan bayar Rp30.000 — uang pelanggan dipegang toko', b && [b.status, b.cap, b.ket]);
  ok('39b-4 tab Bon: daftar kelebihan bayar memuat Hartawan 30.000 (jumlah 30.000); "sisa semuanya" TIDAK dikurangi (= total tanpa Hartawan), berutang turun satu, papan tanpa Hartawan', B1.lebih.length === 1 && B1.lebih[0].kunci === 'pak hartawan' && B1.lebih[0].lebih === 30000 && B1.jumlahLebih === 30000 && B1.total === B0.total - 250000 && B1.berutang === B0.berutang - 1 && !B1.papan.some(function (p) { return p.kunci === 'pak hartawan'; }) && B0.lebih.length === 0, JSON.stringify([B0.total, B1.total, B1.lebih, B0.berutang, B1.berutang]));
  var LB = lembarBon(KINI, 'pak hartawan');
  ok('39b-4 lembar bon Hartawan tetap bisa dibuka: status "lebih", tanpa rincian bon terbuka, riwayat memuat pembayaran 280.000', LB && LB.status === 'lebih' && LB.rinci.length === 0 && LB.riwayat.some(function (r) { return r.n === -280000; }), LB && JSON.stringify([LB.status, LB.rinci, LB.riwayat.length]));
  var BYL = susunBayarBon(KINI, 'pak hartawan', '10.000', 'Tunai', '', '', W), HBL = susunHapusBon(KINI, 'pak hartawan', '10.000', 'salah catat', W, true);
  ok('39b-4 bayar & hapus bon untuk nama yang kelebihan bayar ditolak DULUAN dengan kalimat benar (bukan "melebihi sisa bonnya (−Rp30.000)")', BYL.tolak === 'Pak Hartawan: kelebihan bayar Rp30.000 — uang pelanggan dipegang toko. Tidak ada bon untuk dibayar.' && HBL.tolak === 'Pak Hartawan: kelebihan bayar Rp30.000 — uang pelanggan dipegang toko. Tidak ada bon untuk dihapus dari buku.' && !BYL.dokumen && !HBL.dokumen, JSON.stringify([BYL.tolak, HBL.tolak]));
  var KO = kartuOrang(KINI, 'pak hartawan');
  ok('39b-4 kartu orang: utang 0, lebih 30.000, ringkasan menyebut "kelebihan bayar Rp30.000"', KO && KO.utang === 0 && KO.lebih === 30000 && / · kelebihan bayar Rp30\.000/.test(KO.ringkas), KO && JSON.stringify([KO.utang, KO.lebih, KO.ringkas]));
  var RG = rincianGabung(KINI, 'pak darto', 'pak hartawan');
  ok('39b-4 gabung nama: pratinjau memakai sisa BERTANDA — Darto 1.080.000 + Hartawan −30.000 = bon Rp1.050.000 (dulu 1.080.000: kelebihan dijepit 0)', RG && !RG.tolak && /, bon Rp1\.050\.000\./.test(RG.arti), RG && (RG.tolak || RG.arti));
  var LX = lebihBayarDari(hitungPiutang());
  ok('39b-4 satu aturan (format.js lebihBayarDari): 1 nama, jumlah 30.000 = daftar tab Bon', LX.n === 1 && LX.jumlah === 30000 && LX.orang[0].kunci === 'pak hartawan' && LX.orang[0].nama === (B1.lebih[0] || {}).nama, JSON.stringify(LX));
  pulih(s0);
  // B1: bon Hartawan 250.000 dihapus buku 250.000 lalu dibayar 250.000 (HP kasir katalog basi) → sisa −250.000 BUKAN uang pelanggan
  pasok('piutangMutasi', cacheMentah('piutang').concat([{ id: 9953, tipe: 'hapusBuku', namaPelanggan: 'Pak Hartawan', nominal: 250000, alasan: 'pindah', tanggal: '2026-09-18', jam: '10:00', dicatatDi: 'sistem' }, { id: 9954, tipe: 'bayar', namaPelanggan: 'Pak Hartawan', nominal: 250000, tanggal: '2026-09-19', jam: '09:40', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  var bh = semuaBon(KINI).find(function (x) { return x.kunci === 'pak hartawan'; }); var BH = susunBon(KINI, null, ''); var LH = lebihBayarDari(hitungPiutang());
  ok('39b-4 B1 hapus buku terbayar: cap "hapus buku terbayar", ket "Rp250.000 dibayar padahal sudah dihapus dari buku — hapus bukunya yang perlu dibalik, bukan uang pelanggan"; pecahan uang 0 · hapus 250.000; tab Bon: jumlah uang 0', bh && bh.status === 'lebih' && bh.cap === 'hapus buku terbayar' && bh.ket === 'Rp250.000 dibayar padahal sudah dihapus dari buku — hapus bukunya yang perlu dibalik, bukan uang pelanggan' && bh.lebihUang === 0 && bh.lebihHapus === 250000 && LH.uang.n === 0 && LH.hapus.n === 1 && LH.hapus.jumlah === 250000 && BH.jumlahLebihUang === 0 && BH.jumlahLebihHapus === 250000, bh && JSON.stringify([bh.cap, bh.ket, bh.lebihUang, bh.lebihHapus, LH.uang, LH.hapus]));
  pulih(s0);
  pasok('piutangMutasi', cacheMentah('piutang').concat([{ id: 9952, tipe: 'bayar', namaPelanggan: 'Pak Hartawan', nominal: 250000.3, tanggal: '2026-09-19', jam: '09:31', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  var b2 = semuaBon(KINI).find(function (x) { return x.kunci === 'pak hartawan'; });
  ok('39b-4 ambang: sisa −0,3 (pembulatan) = LUNAS, bukan kelebihan bayar; daftar kelebihan kosong', b2 && b2.status === 'lunas' && lebihBayarDari(hitungPiutang()).n === 0 && susunBon(KINI, null, '').lebih.length === 0, b2 && [b2.sisa, b2.status]);
  pulih(s0);
})();
// ---- PAKET F2 (owner 8 Okt 2026: "catatannya jangan dihapus — sewaktu-waktu ada yang mau bayar"): dibayar sesudah dihapus buku = hapus buku DIBALIK
// (catatan hapus buku bernilai minus) + pembayaran biasa, SATU kiriman; hapus buku lama tetap ada
(function () {
  var s0 = simpan(); var B0 = susunBon(KINI, null, '');
  terapkan(susunHapusBon(KINI, 'pak hartawan', '250.000', 'pindah', W, true));
  var BH = susunBon(KINI, null, ''); var dh = BH.dihapus.find(function (x) { return x.kunci === 'pak hartawan'; });
  ok('F2 daftar "dihapus dari buku": Hartawan 250.000 bertanggal hapus 19 Sep (bonnya nol, tidak di daftar berutang); jumlahDihapus 250.000; sebelum dihapus daftar kosong', dh && dh.dihapus === 250000 && dh.tanggal === W.tanggal && BH.jumlahDihapus === 250000 && !BH.papan.some(function (p) { return p.kunci === 'pak hartawan'; }) && B0.dihapus.length === 0 && B0.jumlahDihapus === 0, JSON.stringify([BH.dihapus, B0.dihapus]));
  var P0 = susunBayarSesudahHapus(KINI, 'pak hartawan', '250.000', 'Tunai', 'datang sendiri', W, false); var P1 = susunBayarSesudahHapus(KINI, 'pak hartawan', '250.000', 'Tunai', 'datang sendiri', W, true);
  var Plb = susunBayarSesudahHapus(KINI, 'pak hartawan', '250.001', 'Tunai', '', W, true); var Pdt = susunBayarSesudahHapus(KINI, 'pak darto', '100.000', 'Tunai', '', W, true); var Pnol = susunBayarSesudahHapus(KINI, 'pak hartawan', '', 'Tunai', '', W, true);
  ok('F2 ketukan pertama DITANYA ("TETAP ada", "laba bulan ini naik Rp250.000"); kedua → 2 dokumen piutangMutasi: hapusBuku −250.000 (balikHapus) + bayar 250.000 Tunai; melebihi yang dihapus, jumlah kosong, & nama tanpa hapus buku ditolak',
    P0.perluYakin === true && /TETAP ada/.test(P0.tolak) && /laba bulan ini naik Rp250\.000/.test(P0.tolak) && !P0.dokumen && !P1.tolak && P1.dokumen.length === 2 && P1.dokumen[0].data.tipe === 'hapusBuku' && P1.dokumen[0].data.nominal === -250000 && P1.dokumen[0].data.balikHapus === true && /datang sendiri/.test(P1.dokumen[0].data.alasan)
    && P1.dokumen[1].data.tipe === 'bayar' && P1.dokumen[1].data.nominal === 250000 && P1.dokumen[1].data.caraBayar === 'Tunai' && P1.dokumen.every(function (d) { return d.koleksi === 'piutangMutasi' && d.data.namaPelanggan === 'Pak Hartawan' && d.data.tanggal === W.tanggal; }) && P1.dokumen[0].data.id !== P1.dokumen[1].data.id
    && /paling banyak/.test(Plb.tolak) && /Belum ada bon Pak Darto yang dihapus/.test(Pdt.tolak) && /Ketik jumlah/.test(Pnol.tolak) && /laci bertambah/.test(P1.patch.kabar) && /catatan hapus buku lama tetap ada/.test(P1.patch.kabar), JSON.stringify([P0.tolak, P1.dokumen, Plb.tolak, Pdt.tolak]));
  terapkan(P1); var m = hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }); var bb = semuaBon(KINI).find(function (x) { return x.kunci === 'pak hartawan'; }); var LB = lembarBon(KINI, 'pak hartawan'); var B2 = susunBon(KINI, null, '');
  ok('F2 sesudahnya: mesin sisa 0, dihapus bersih 0, bayar 250.000; status LUNAS (bukan "lebih"); daftar dihapus kosong lagi; riwayat memuat DIHAPUS −250.000, "hapus buku dibalik" +250.000, dan pembayaran — kedua catatan hapus buku TETAP ada',
    m.sisa === 0 && m.dihapus === 0 && m.bayar === 250000 && bb.status === 'lunas' && B2.dihapus.length === 0 && B2.lebih.length === 0 && LB.riwayat.some(function (r) { return /^DIHAPUS dari buku/.test(r.teks) && r.n === -250000; }) && LB.riwayat.some(function (r) { return /^hapus buku dibalik/.test(r.teks) && r.n === 250000; }) && LB.riwayat.some(function (r) { return /^membayar/.test(r.teks) && r.n === -250000; })
    && cacheMentah('piutang').filter(function (x) { return x.namaPelanggan === 'Pak Hartawan' && x.tipe === 'hapusBuku'; }).length === 2, JSON.stringify([m.sisa, m.dihapus, m.bayar, bb.status, LB.riwayat]));
  pulih(s0);
  terapkan(susunHapusBon(KINI, 'pak hartawan', '250.000', 'pindah', W, true)); terapkan(susunBayarSesudahHapus(KINI, 'pak hartawan', '100.000', 'QRIS', '', W, true));
  var m2 = hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }); var B3 = susunBon(KINI, null, ''); var d3 = B3.dihapus.find(function (x) { return x.kunci === 'pak hartawan'; });
  ok('F2 sebagian (QRIS 100.000 dari 250.000 yang dihapus): sisa tetap 0, dihapus bersih 150.000, daftar dihapus 150.000, pembayaran QRIS 100.000; sisa 150.000 boleh dibalik lagi, 150.001 tidak',
    m2.sisa === 0 && m2.dihapus === 150000 && d3 && d3.dihapus === 150000 && cacheMentah('piutang').some(function (x) { return x.tipe === 'bayar' && x.namaPelanggan === 'Pak Hartawan' && x.caraBayar === 'QRIS' && x.nominal === 100000; })
    && !susunBayarSesudahHapus(KINI, 'pak hartawan', '150.000', 'Tunai', '', W, true).tolak && /paling banyak/.test(susunBayarSesudahHapus(KINI, 'pak hartawan', '150.001', 'Tunai', '', W, true).tolak), JSON.stringify([m2.sisa, m2.dihapus, B3.dihapus]));
  pulih(s0);
  // hapus buku TERBAYAR (pembayaran sudah tercatat, mis. dari HP kasir) → cukup dibalik, TANPA pembayaran kedua
  pasok('piutangMutasi', cacheMentah('piutang').concat([{ id: 9963, tipe: 'hapusBuku', namaPelanggan: 'Pak Hartawan', nominal: 250000, alasan: 'pindah', tanggal: '2026-09-18', jam: '10:00', dicatatDi: 'sistem' }, { id: 9964, tipe: 'bayar', namaPelanggan: 'Pak Hartawan', nominal: 250000, tanggal: '2026-09-19', jam: '09:40', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  var R0 = susunBayarSesudahHapus(KINI, 'pak hartawan', '250.000', 'Tunai', '', W, true); var Rl = susunBayarSesudahHapus(KINI, 'pak hartawan', '260.000', 'Tunai', '', W, true);
  ok('F2 hapus buku TERBAYAR (status lebih): SATU dokumen hapusBuku −250.000 (tanpa bayar kedua), kabar "uangnya sudah tercatat"; melebihi yang terbayar ditolak; sesudahnya LUNAS, daftar lebih & dihapus kosong',
    !R0.tolak && R0.dokumen.length === 1 && R0.dokumen[0].data.nominal === -250000 && /sudah tercatat/.test(R0.patch.kabar) && /paling banyak/.test(Rl.tolak)
    && (function () { terapkan(R0); var x = semuaBon(KINI).find(function (y) { return y.kunci === 'pak hartawan'; }); var S = susunBon(KINI, null, ''); return x.status === 'lunas' && S.lebih.length === 0 && S.dihapus.length === 0; })(), JSON.stringify([R0, Rl.tolak]));
  pulih(s0);
  // kelebihan bayar UANG (bukan hapus buku) tidak boleh lewat pintu ini
  pasok('piutangMutasi', cacheMentah('piutang').concat([{ id: 9965, tipe: 'bayar', namaPelanggan: 'Pak Hartawan', nominal: 280000, tanggal: '2026-09-19', jam: '09:30', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  ok('F2 kelebihan bayar uang (tanpa hapus buku) ditolak: "Belum ada bon … yang dihapus"', /Belum ada bon Pak Hartawan yang dihapus/.test(susunBayarSesudahHapus(KINI, 'pak hartawan', '30.000', 'Tunai', '', W, true).tolak || ''));
  pulih(s0);
})();
// ---- PAKET BRIEF 9 OKT (butir 1): kelompok umur diatur owner + RATA-RATA HARI BON TERTAGIH (DSO versi toko). Hitungan tangan: komentar TERTAGIH di atas.
(function () {
  var s0 = simpan(); var B0 = susunBon(KINI, null, '');
  ok('umur bawaan: label PERSIS garis umur yang dikunci (≤ 7 hari · 8–30 hari · 1–3 bulan · > 3 bulan), batas 7/30/90, isi [0, 5, 0, 2] orang; Σ jumlah kelompok = sisa semuanya',
    JSON.stringify(B0.ember.map(function (e) { return e.label; })) === JSON.stringify(['≤ 7 hari', '8–30 hari', '1–3 bulan', '> 3 bulan']) && JSON.stringify(aturPelanggan().umurBatas) === '[7,30,90]' && aturPelanggan().tertagihHari === 90
    && JSON.stringify(B0.ember.map(function (e) { return e.n; })) === '[0,5,0,2]' && B0.ember.reduce(function (a, e) { return a + e.jumlah; }, 0) === B0.total && B0.total === 3917500, JSON.stringify(B0.ember));
  var AU = susunAturPelanggan({ umurBatas: ['14', '60', '365'], tertagihHari: '120' }, W);
  ok('atur umur: batas 14/60/365 + periode 120 tersimpan di aturanToko/pelanggan (kolom umurBatas, tertagihHari); batas yang tidak naik / kurang dari tiga / pecahan & periode 0 ditolak',
    !AU.tolak && JSON.stringify(AU.dokumen[0].data.umurBatas) === '[14,60,365]' && AU.dokumen[0].data.tertagihHari === 120 && /naik/.test(susunAturPelanggan({ umurBatas: ['30', '14', '90'] }, W).tolak || '')
    && /tiga batas/.test(susunAturPelanggan({ umurBatas: ['7', '30'] }, W).tolak || '') && /naik/.test(susunAturPelanggan({ umurBatas: ['7', '30', '90,5'] }, W).tolak || '') && /1–3650/.test(susunAturPelanggan({ tertagihHari: '0' }, W).tolak || ''), JSON.stringify(AU));
  terapkan(AU); var B1 = susunBon(KINI, null, '');
  ok('atur umur BERLAKU: label ikut angka (≤ 14 hari · 15–60 hari · 61–365 hari · > 1 tahun), isi [3, 2, 0, 2] orang (Rahma 10, Sri 11, Darto 14 | Feri 22, Bimo 18 | — | Lisna, Hartawan); Σ = sisa semuanya; kotak e1 → 3 orang; simpan Atur biasa membawa batas yang sama',
    JSON.stringify(B1.ember.map(function (e) { return e.label; })) === JSON.stringify(['≤ 14 hari', '15–60 hari', '61–365 hari', '> 1 tahun']) && JSON.stringify(B1.ember.map(function (e) { return e.n; })) === '[3,2,0,2]'
    && B1.ember.reduce(function (a, e) { return a + e.jumlah; }, 0) === B1.total && susunBon(KINI, null, 'e1').perUmur.length === 3 && JSON.stringify(susunAturPelanggan({ kosongKali: '30' }, W).dokumen[0].data.umurBatas) === '[14,60,365]', JSON.stringify(B1.ember));
  pulih(s0);
  pasok('penjualan', cacheMentah('penjualan').concat([{ id: 3999, tanggal: '', jam: '', namaPelanggan: 'Pak Tanpa Tanggal', caraBayar: 'Kredit', jenis: 'literan', merkSumber: 'Angsa', hargaTotal: 25000, hppTotalSaatJual: 0 }]));
  var B2 = susunBon(KINI, null, ''); var e0 = B2.ember.find(function (e) { return e.id === 'e0'; });
  ok('umur: bon TANPA TANGGAL jadi kelompok sendiri "tanpa tanggal" (1 orang, 25.000) — tidak dibuang diam-diam; Σ kelompok = sisa semuanya; kotaknya bisa dipilih',
    !!e0 && e0.label === 'tanpa tanggal' && e0.n === 1 && e0.jumlah === 25000 && B2.ember.reduce(function (a, e) { return a + e.jumlah; }, 0) === B2.total && B2.total === B0.total + 25000 && susunBon(KINI, null, 'e0').perUmur.length === 1, JSON.stringify(B2.ember));
  pulih(s0);
  var dasar = tertagihBon(KINI);
  ok('tertagih kotak dasar: cuma bon Bu Sri 1 Sep yang lunas (bayar 10 Sep) → 9 hari dari 1 bon', dasar.keadaan === 'ada' && dasar.rataHari === 9 && dasar.tertagih.n === 1 && dasar.lunas.n === 1, JSON.stringify(dasar));
  pasok('penjualan', cacheMentah('penjualan').concat(TERTAGIH.penjualan)); pasok('piutangMutasi', cacheMentah('piutang').concat(TERTAGIH.piutangMutasi));
  var T = tertagihBon(KINI); var tg = function (k) { return tertagihBon(KINI, k); };
  ok('tertagih toko (90 hari, 22 Jun–19 Sep): 11 bon dibayar Rp1.800.000, Σ rupiah×hari 36.750.000 → 20,4 hari; dibayar di meja saat beli 2 bon Rp350.000, saldo awal 1 bon Rp200.000 (belum bisa dihitung), hapus buku 1 bon Rp100.000 & retur 1 bon Rp120.000 terpisah; 13 bon lunas Rp2.570.000 = jumlah bagian-bagiannya',
    T.keadaan === 'ada' && T.hari === 90 && T.awal === '2026-06-22' && T.akhir === '2026-09-19' && T.tertagih.n === 11 && T.tertagih.rp === 1800000 && T.tertagih.rh === 36750000 && Math.abs(T.rataHari - 36750000 / 1800000) < 1e-9 && T.rataTeks === '20,4 hari'
    && T.saatBeli.n === 2 && T.saatBeli.rp === 350000 && T.saldoAwal.n === 1 && T.saldoAwal.rp === 200000 && T.hapusBuku.n === 1 && T.hapusBuku.rp === 100000 && T.retur.n === 1 && T.retur.rp === 120000 && T.lain.n === 0 && T.tanpaTanggal.n === 0
    && T.lunas.n === 13 && T.lunas.rp === 2570000 && T.lunas.rp === T.tertagih.rp + T.saatBeli.rp + T.saldoAwal.rp + T.hapusBuku.rp + T.retur.rp && /1 bon saldo awal/.test(T.teks) && /hapus buku Rp100\.000/.test(T.teks) && /Rp350\.000 dibayar di meja saat beli/.test(T.teks), JSON.stringify(T));
  ok('tertagih: uang yang dibayar DI MEJA saat beli bukan bon yang ditagih — Bu Yati (dikenali lewat notaTrxId) 300 rb terpisah, sisanya 200 rb 10 hari; Pak Hadi (dikenali lewat catatan gaya lama) 150 rb di meja: 100 rb memadamkan bon LAMA 20 Agu (FIFO) = tertagih 16 hari, 50 rb nota hari itu = saat beli; 200 rb 9 hari → 11,3 hari',
    tg('bu yati').rataHari === 10 && tg('bu yati').saatBeli.rp === 300000 && tg('bu yati').tertagih.rp === 200000 && tg('pak hadi').saatBeli.rp === 50000 && tg('pak hadi').tertagih.rp === 300000 && tg('pak hadi').tertagih.rh === 3400000 && tg('pak hadi').rataTeks === '11,3 hari' && tg('pak hadi').lunas.n === 2,
    JSON.stringify([tg('bu yati'), tg('pak hadi')]));
  ok('tertagih per orang: Bu Wati 2 bon × 2 pembayaran FIFO = 2.750.000 / 300.000 = 9,2 hari; Pak Joko 10 & 40 hari = 32,5 hari (bon 1 Agu masih terbuka); Mbak Rina 10 hari + hapus buku 100 rb terpisah; Pak Udin 30 hari + retur nota asal 120 rb terpisah (2 bon lunas); Pak Eko 52 hari (hapus buku dibalik lalu dibayar — bukan hapus buku)',
    Math.abs(tg('bu wati').rataHari - 2750000 / 300000) < 1e-9 && tg('bu wati').rataTeks === '9,2 hari' && tg('bu wati').tertagih.n === 2 && tg('pak joko').rataTeks === '32,5 hari' && tg('pak joko').tertagih.n === 1 && tg('pak joko').lunas.n === 1
    && tg('mbak rina').rataHari === 10 && tg('mbak rina').hapusBuku.rp === 100000 && tg('pak udin').rataHari === 30 && tg('pak udin').retur.rp === 120000 && tg('pak udin').lunas.n === 2 && tg('pak eko').rataHari === 52 && tg('pak eko').hapusBuku.n === 0 && tg('pak eko').tertagih.rp === 100000,
    JSON.stringify(['bu wati', 'pak joko', 'mbak rina', 'pak udin', 'pak eko'].map(function (k) { var x = tg(k); return [k, x.rataHari, x.tertagih, x.hapusBuku, x.retur, x.lunas]; })));
  ok('tertagih TIGA KEADAAN: Bu Tini (saldo awal dibayar) = "belum bisa dihitung: 1 bon saldo awal", rataHari null — bukan 0; Pak Bowo bayar dulu baru bon lahir = 0 hari (nol, keadaan "ada", tidak minus); Pak Hartawan (belum pernah membayar) & Bu Ani (lunas 1 Jun, di luar 90 hari) = kosong "—"',
    tg('bu tini').keadaan === 'belum' && tg('bu tini').rataHari === null && tg('bu tini').rataTeks === 'belum bisa dihitung' && /Belum bisa dihitung: 1 bon saldo awal/.test(tg('bu tini').teks) && tg('pak bowo').keadaan === 'ada' && tg('pak bowo').rataHari === 0 && tg('pak bowo').rataTeks === '0 hari'
    && /hari bon lahir/.test(tg('pak bowo').teks) && tg('pak hartawan').keadaan === 'kosong' && tg('pak hartawan').rataTeks === '—' && tg('bu ani').keadaan === 'kosong', JSON.stringify([tg('bu tini'), tg('pak bowo').rataHari, tg('bu ani').keadaan]));
  var tidakCocok = []; hitungPiutang().forEach(function (d) { var J = jalanTutupBon(d); var buka = J.filter(function (b) { return b.sisa > 1e-6; }).map(function (b) { return [b.tanggal, b.sisa]; }); var R = rincianBelumLunas(d).map(function (r) { return [r.tanggal, r.sisa]; });
    var utuh = J.every(function (b) { return Math.abs(b.potong.reduce(function (a, x) { return a + x.n; }, 0) + b.sisa - b.nominal) < 1e-6; }); if (JSON.stringify(buka) !== JSON.stringify(R) || !utuh) tidakCocok.push(d.kunci); });
  ok('jalan tutup = mesin: untuk SETIAP orang di kotak pasir (17 buku bon), bon yang masih terbuka (tanggal + sisa) = rincianBelumLunas (mesin hitungPiutang), dan per bon Σ potongan + sisa = nilai bon', tidakCocok.length === 0 && hitungPiutang().length === 17, JSON.stringify([tidakCocok, hitungPiutang().length]));
  ok('lembar orang & tab Garis umur membawa angka yang sama (lembarBon.tertagih = per orang; susunBon.tertagih = toko)', lembarBon(KINI, 'bu wati').tertagih.rataTeks === '9,2 hari' && lembarBon(KINI, 'bu tini').tertagih.keadaan === 'belum' && susunBon(KINI, null, '').tertagih.rataTeks === '20,4 hari');
  var s1 = simpan();
  terapkan(susunAturPelanggan({ tertagihHari: '120' }, W)); var T120 = tertagihBon(KINI); var ani = tg('bu ani').rataHari;
  terapkan(susunAturPelanggan({ tertagihHari: '10' }, W)); var T10 = tertagihBon(KINI);
  terapkan(susunAturPelanggan({ tertagihHari: '5' }, W)); var T5 = tertagihBon(KINI); pulih(s1);
  ok('tertagih: periode = setelan owner — 120 hari (23 Mei–19 Sep) ikut Bu Ani 22 hari → 12 bon Rp1.880.000, 38.510.000 → 20,5 hari, 14 lunas; 10 hari (10–19 Sep) Bu Sri 9, Pak Eko 52, Bu Yati 10, Pak Hadi 9 → 9.900.000 / 600.000 = 16,5 hari; 5 hari → kosong "—" (bukan 0)',
    T120.awal === '2026-05-23' && T120.tertagih.n === 12 && T120.tertagih.rp === 1880000 && T120.tertagih.rh === 38510000 && T120.rataTeks === '20,5 hari' && T120.lunas.n === 14 && ani === 22
    && T10.awal === '2026-09-10' && T10.tertagih.n === 4 && T10.tertagih.rp === 600000 && T10.tertagih.rh === 9900000 && T10.rataTeks === '16,5 hari' && T10.lunas.n === 4 && T10.hapusBuku.n === 0 && T5.keadaan === 'kosong' && T5.rataHari === null && T5.rataTeks === '—' && T5.lunas.n === 0,
    JSON.stringify([T120.awal, T120.rataTeks, T120.tertagih, ani, T10.awal, T10.rataTeks, T10.tertagih, T5.keadaan]));
  pulih(s0);
})();
ok('layar: tab Garis umur menggambar kartu tertagih; lembar orang menulis rata-rata hari bayar; Atur punya 3 batas umur + periode (pratinjau label) dan membawanya dari setelan; batang tertagih hormati prefers-reduced-motion',
  LAYAR_PL.js.indexOf('${gambarTertagih(Bn.tertagih)}') >= 0 && LAYAR_PL.js.indexOf('data-k="tertagih-orang"') >= 0 && LAYAR_PL.js.indexOf('O.tertagih.rataTeks') >= 0 && LAYAR_PL.js.indexOf('data-kolom="umurBatas"') >= 0 && LAYAR_PL.js.indexOf('data-kolom="tertagihHari"') >= 0
  && LAYAR_PL.js.indexOf('umurBatas: a.umurBatas.map(String), tertagihHari: String(a.tertagihHari)') >= 0 && LAYAR_PL.js.indexOf('${gambarAturUmur(a)}') >= 0 && /prefers-reduced-motion[^}]*tg-rel i/.test(LAYAR_PL.css));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var O = semuaOrang(KINI); var WX = { tanggal: '2026-09-22', jam: '10:00', kini: '2026-09-22T03:00:00.000Z', idUnik: function () { return Math.random(); } }; var asing = [];
var berlaku = ambilPenjualan().filter(function (p) { return String(p.namaPelanggan || '').trim(); }); var pasangan = {}; berlaku.forEach(function (p) { pasangan[kunciPelanggan(p.namaPelanggan) + '|' + p.tanggal] = 1; });
ambilPiutangMutasi().forEach(function (m) { if (m.tipe === 'bayar' && m.namaPelanggan) pasangan[kunciPelanggan(m.namaPelanggan) + '|' + m.tanggal] = 1; });
var kunjunganLayar = O.reduce(function (a, b) { return a + b.kunjungan; }, 0); var kunjunganNyata = Object.keys(pasangan).length;
var belanjaLayar = O.reduce(function (a, b) { return a + b.total; }, 0); var belanjaNyata = berlaku.reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
// paket brief 9 Okt: rata-rata hari bon tertagih & kelompok umur di data toko — dihitung SEBELUM kasus asap lain menyuntik apa pun
var TGX = (function () { var T = tertagihBon(KINI); var SU = sebaranUmurBon(KINI); var KU = kelompokUmur(aturPelanggan().umurBatas); var tidak = 0, bonKel = {}, orangAda = 0, nBuku = 0;
  hitungPiutang().forEach(function (d) { nBuku += 1; var J = jalanTutupBon(d); var buka = J.filter(function (b) { return b.sisa > 1e-6; }).map(function (b) { return [b.tanggal, b.sisa]; }); var R = rincianBelumLunas(d).map(function (r) { return [r.tanggal, r.sisa]; });
    var utuh = J.every(function (b) { return Math.abs(b.potong.reduce(function (a, x) { return a + x.n; }, 0) + b.sisa - b.nominal) < 1e-6; }); if (JSON.stringify(buka) !== JSON.stringify(R) || !utuh) tidak += 1;
    J.forEach(function (b) { if (!(b.sisa > 1e-6)) return; var u = /^\d{4}-\d{2}-\d{2}$/.test(b.tanggal) ? hariKe(hariIniIso(KINI)) - hariKe(b.tanggal) : null; var e = u === null ? null : KU.find(function (x) { return u >= x.dari && u <= x.sampai; }); var l = e ? e.label : 'tanpa tanggal'; bonKel[l] = (bonKel[l] || 0) + 1; });
    if (tertagihBon(KINI, d.kunci).keadaan === 'ada') orangAda += 1; });
  var sisaPos = semuaBon(KINI).filter(function (b) { return b.sisa > 0; }).reduce(function (a, b) { return a + b.sisa; }, 0);
  return { keadaan: T.keadaan, rataTeks: T.rataTeks, rataHari: T.rataHari, awal: T.awal, akhir: T.akhir, hari: T.hari, tertagih: T.tertagih, saldoAwal: T.saldoAwal, hapusBuku: T.hapusBuku, retur: T.retur, lain: T.lain, tanpaTanggal: T.tanpaTanggal, lunas: T.lunas,
    saatBeli: T.saatBeli, tutup: Math.abs(T.lunas.rp - (T.tertagih.rp + T.saatBeli.rp + T.saldoAwal.rp + T.hapusBuku.rp + T.retur.rp + T.lain.rp + T.tanpaTanggal.rp)) < 0.5, tidakCocok: tidak, nBuku: nBuku, orangAda: orangAda,
    umur: SU.map(function (e) { return { label: e.label, n: e.n, jumlah: e.jumlah }; }), umurCocok: Math.abs(SU.reduce(function (a, e) { return a + e.jumlah; }, 0) - sisaPos) < 0.5, sisa: sisaPos, bonKel: bonKel }; })();
var SB = semuaBon(KINI); var sisaLayar = SB.reduce(function (a, b) { return a + b.sisa; }, 0); var sisaMesin = hitungPiutang().reduce(function (a, b) { return a + b.sisa; }, 0);
var kenalB = {}; (CAD.piutangMutasi || []).forEach(function (m) { if (m.tipe === 'bayar') Object.keys(m).forEach(function (k) { kenalB[k] = 1; }); }); kenalB.dibawaOleh = 1;
var berutang = SB.filter(function (b) { return b.sisa > 0; })[0]; if (berutang) { var by = susunBayarBon(KINI, berutang.kunci, '1', 'Tunai', 'uji', '', WX); if (by.dokumen) Object.keys(by.dokumen[0].data).forEach(function (k) { if (!kenalB[k]) asing.push('bayar.' + k); }); else asing.push('bayar ditolak: ' + by.tolak);
  var hb = susunHapusBon(KINI, berutang.kunci, '1', 'uji', WX, true); if (hb.dokumen) Object.keys(hb.dokumen[0].data).forEach(function (k) { if (!kenalB[k] && k !== 'alasan') asing.push('hapusBuku.' + k); }); else asing.push('hapus ditolak: ' + hb.tolak);
    // Paket F2 asap: hapus buku sisa satu nama nyata lalu dibayar kembali penuh (cache sementara) — kolom dokumen dikenal cadangan (+ balikHapus); mesin: sisa 0,
    // hapus buku bersih kembali seperti semula, pembayaran bertambah sebesar sisa itu
    var sF2 = berutang.sisa; var cadF2 = cacheMentah('piutang').slice(); var hbF2 = susunHapusBon(KINI, berutang.kunci, String(Math.round(sF2)), 'asap', WX, true);
    if (hbF2.dokumen) { pasok('piutangMutasi', cadF2.concat(hbF2.dokumen.map(function (d) { return d.data; }))); var pF2 = susunBayarSesudahHapus(KINI, berutang.kunci, String(Math.round(sF2)), 'Tunai', 'asap', WX, true);
      if (pF2.dokumen) { pF2.dokumen.forEach(function (d) { Object.keys(d.data).forEach(function (k) { if (!kenalB[k] && ['alasan', 'balikHapus'].indexOf(k) < 0) asing.push('F2.' + d.data.tipe + '.' + k); }); });
        pasok('piutangMutasi', cacheMentah('piutang').concat(pF2.dokumen.map(function (d) { return d.data; }))); var mF2 = hitungPiutang().find(function (x) { return x.kunci === berutang.kunci; });
        if (!mF2 || Math.abs(mF2.sisa) > 0.5 || Math.abs(mF2.dihapus - berutang.dihapus) > 0.5 || Math.abs(mF2.bayar - berutang.bayar - sF2) > 0.5) asing.push('F2 ' + berutang.nama + ': sisa ' + (mF2 && mF2.sisa) + ' (harus 0) · dihapus ' + (mF2 && mF2.dihapus) + ' · bayar ' + (mF2 && mF2.bayar)); } else asing.push('F2 ditolak: ' + pF2.tolak); }
    pasok('piutangMutasi', cadF2); }
var kenalK = {}; (CAD.pelangganCatatan || []).forEach(function (c) { Object.keys(c).forEach(function (k) { kenalK[k] = 1; }); }); ['cip', 'arah', 'asli', 'kontak', 'biasa', 'diubahPada'].forEach(function (k) { kenalK[k] = 1; });
var kartuAda = O.find(function (b) { return b.kartu; }); if (kartuAda) { var sk = susunSimpanKartu(KINI, kartuAda.kunci, { nama: kartuAda.nama, cip: kartuAda.cip, catatan: kartuAda.catatan, arah: kartuAda.arah }, WX); if (sk.dokumen) Object.keys(sk.dokumen[0].data).forEach(function (k) { if (!kenalK[k]) asing.push('kartu.' + k); }); else asing.push('kartu ditolak: ' + sk.tolak); }
var pt = berutang ? pesanTagih(KINI, berutang.kunci) : null;
// ---- 23b: pratinjau Bersihkan di data toko (TIDAK menulis) + suntikan: kartu nyata diberi cip dicabut, dibersihkan, kolom selain cip/ciri wajib byte-sama
var jepretT = function () { return JSON.stringify(cacheMentah('pelangganCat')) + JSON.stringify(cacheMentah('aturan')); }; var jt0 = jepretT(); var RB = rincianBersihkanCiri(KINI); var pratinjauDiam = jt0 === jepretT();
var asli = {}; cacheMentah('pelangganCat').forEach(function (c) { asli[c.id] = JSON.parse(JSON.stringify(c)); });
var calonCip = cacheMentah('pelangganCat').filter(function (c) { return Array.isArray(c.cip) && c.cip.length; }).slice(0, 3); var calonLama = cacheMentah('pelangganCat').filter(function (c) { return !Array.isArray(c.cip) && String(c.ciri || '').trim(); }).slice(0, 1);
terapkanKeCache(calonCip.map(function (c) { var cip = c.cip.concat(['sawo matang', 'Sunda']); return { koleksi: 'pelangganCatatan', data: Object.assign({}, c, { cip: cip, ciri: cip.join(' · ') }) }; }).concat(calonLama.map(function (c) { return { koleksi: 'pelangganCatatan', data: Object.assign({}, c, { ciri: c.ciri + ' · kulit gelap' }) }; })));
var disuntik = {}; cacheMentah('pelangganCat').forEach(function (c) { disuntik[c.id] = JSON.parse(JSON.stringify(c)); });
pasok('cadanganCatatan', [{ id: 'asap', tanggal: hariIniIso(KINI), jam: '20:00', ok: true }]); var BSx = susunBersihkanCiri(KINI, true); if (BSx.ubahKolom) perbaruiKolom(BSx.ubahKolom, BSx.ringkas);
// data toko bisa SUDAH memuat cip dicabut (cadangan 24 Sep: ya) — yang wajib ditulis = semua kartu yang memuatnya sesudah suntikan, bukan cuma yang disuntik
var tanpaCipCiri = function (d) { var x = JSON.parse(JSON.stringify(d)); delete x.cip; delete x.ciri; return JSON.stringify(x); }; var kena = calonCip.concat(calonLama).map(function (c) { return String(c.id); }); var identik = true, pulihCip = true;
var token = function (d) { return (Array.isArray(d.cip) ? d.cip.map(String) : []).concat(String(d.ciri || '').split(/\s*[·,;]\s*/)); }; var bersihDari = function (a) { return a.filter(function (x) { return !cipTerlarang(x); }); };
var harus = Object.keys(disuntik).filter(function (id) { return token(disuntik[id]).some(cipTerlarang); }).sort(); var ditulisId = (BSx.ubahKolom || []).reduce(function (a, p) { return a.concat(p); }, []).filter(function (u) { return u.koleksi === 'pelangganCatatan'; }).map(function (u) { return String(u.id); }).sort();
if (JSON.stringify(harus) !== JSON.stringify(ditulisId)) identik = false;
cacheMentah('pelangganCat').forEach(function (c) { var id = String(c.id); if (ditulisId.indexOf(id) >= 0) { if (tanpaCipCiri(c) !== tanpaCipCiri(disuntik[id])) identik = false;
    if (Array.isArray(c.cip) ? JSON.stringify(c.cip) !== JSON.stringify(bersihDari(disuntik[id].cip)) || c.ciri !== c.cip.join(' · ') : token(c).some(cipTerlarang)) pulihCip = false;
    if (kena.indexOf(id) >= 0 && Array.isArray(c.cip) && JSON.stringify(c.cip) !== JSON.stringify(bersihDari(asli[id].cip))) pulihCip = false; } else if (JSON.stringify(c) !== JSON.stringify(disuntik[id])) identik = false; });
var LB4 = lebihBayarDari(hitungPiutang()); var SB4 = susunBon(KINI, null, '');   // 39b no. 4: berapa nama kelebihan bayar di data toko & apakah tab Bon memuat semuanya
print(JSON.stringify({ tg: TGX, lebih: { n: LB4.n, bon: SB4.lebih.length, negMesin: hitungPiutang().filter(function (d) { return d.sisa < -0.5; }).length, cocok: LB4.n === SB4.lebih.length && LB4.jumlah === SB4.jumlahLebih }, orang: O.length, dikenali: O.filter(function (b) { return b.dikenali; }).length, kunjunganLayar: kunjunganLayar, kunjunganNyata: kunjunganNyata, belanjaLayar: belanjaLayar, belanjaNyata: belanjaNyata, sisaLayar: sisaLayar, sisaMesin: sisaMesin, berutang: SB.filter(function (b) { return b.sisa > 0; }).length,
  kembar: pasanganKembar(O).length, kosong: O.filter(function (b) { return b.kosong; }).length, diharap: O.filter(function (b) { return b.diharap; }).length, tampah: susunTampah(KINI, []).tanya ? susunTampah(KINI, []).tanya.c : null, wajah: susunWajah(KINI, '').daftar.length, asing: asing, waKop: pt ? pt.baris[0] : null, thr: susunThr(KINI, 2026).daftar.length,
  bs: { kartu: RB.kartu.length, cip: RB.cip, tanpaCip: RB.tanpaCip.length, belumDikenal: RB.belumDikenal.length, atur: RB.atur, bebas: RB.bebas.length, bebasKolom: RB.bebas.map(function (x) { return x.kolom.join('+'); }), pratinjauDiam: pratinjauDiam, suntik: kena.length, suntikLama: calonLama.length, harus: harus.length + (BSx.rincian && BSx.rincian.atur ? 1 : 0), ditulis: (BSx.ubahKolom || []).reduce(function (a, p) { return a + p.length; }, 0), identik: identik, pulih: pulihCip, tolak: BSx.tolak || '' } }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar NOTA_TRX = ' + json.dumps(NOTA_TRX) + ';\nvar TRX_BARU = ' + json.dumps(TRX_BARU) + ';\nvar TERTAGIH = ' + json.dumps(TERTAGIH) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


LAYAR_JS = open(os.path.join(AKAR, 'baru/js/layar/pelanggan.js'), encoding='utf-8').read()
LAYAR_CSS = open(os.path.join(AKAR, 'baru/css/pelanggan.css'), encoding='utf-8').read()
def dengan_layar(js, lj=LAYAR_JS, lc=LAYAR_CSS): return js + '\nvar LAYAR_PL = ' + json.dumps({'js': lj, 'css': lc}) + ';\n'


if __name__ == '__main__':
    inti = bundel_baru.bundel(MODUL); js = dengan_layar(inti)
    if '--kontrol' in sys.argv:
        rusak = {
            # ---- paket brief 9 Okt (butir 1): kelompok umur diatur owner + rata-rata hari bon tertagih
            'tertagih: FIFO dirusak — bon TERMUDA ditutup dulu': js.replace("bon.forEach((b) => { const nom = b.u.nominal - b.retur; if (pool >= nom)", "bon.slice().reverse().forEach((b) => { const nom = b.u.nominal - b.retur; if (pool >= nom)"),
            'tertagih: pembayaran TERAKHIR dipasangkan ke rupiah bon tertua': js.replace("ev.sort((a, b) => a.tanggal.localeCompare(b.tanggal) || a.jam.localeCompare(b.jam) || a.urut - b.urut);", "ev.sort((a, b) => b.tanggal.localeCompare(a.tanggal) || b.jam.localeCompare(a.jam) || b.urut - a.urut);"),
            'tertagih: hapus buku ikut dihitung tertagih': js.replace("const k = p.jenis !== 'bayar' ? p.jenis : b.saldoAwal", "const k = p.jenis !== 'bayar' && p.jenis !== 'hapusBuku' ? p.jenis : b.saldoAwal"),
            'tertagih: retur ikut dihitung tertagih': js.replace("const k = p.jenis !== 'bayar' ? p.jenis : b.saldoAwal", "const k = p.jenis !== 'bayar' && p.jenis !== 'retur' ? p.jenis : b.saldoAwal"),
            'tertagih: saldo awal ikut rata-rata': js.replace(": b.saldoAwal ? 'saldoAwal' : p.hari === null", ": false ? 'saldoAwal' : p.hari === null"),
            'tertagih: belum ada yang tertagih → 0 hari (bukan "belum bisa dihitung")': js.replace("const rataHari = T.tertagih.rp > 1e-6 ? T.tertagih.rh / T.tertagih.rp : null;", "const rataHari = T.tertagih.rp > 1e-6 ? T.tertagih.rh / T.tertagih.rp : 0;"),
            'tertagih: periode setelan diabaikan (tetap 90 hari)': js.replace("const N = aturPelanggan().tertagihHari;", "const N = 90;"),
            'tertagih: bon yang lunas SEBELUM periode ikut': js.replace("b.lunasTanggal < awal || b.lunasTanggal > akhir", "b.lunasTanggal > akhir"),
            'tertagih: tidak ditimbang rupiah (tiap potongan sama berat)': js.replace("if (k === 'tertagih') T.tertagih.rh += p.n * p.hari;", "if (k === 'tertagih') T.tertagih.rh += 100000 * p.hari;"),
            'tertagih: uang yang datang sebelum bon lahir dihitung minus': js.replace("const tg = !tglSahBon(t) ? '' : t > tb ? t : tb;", "const tg = !tglSahBon(t) ? '' : t;"),
            'tertagih: hapus buku dibalik tidak menetralkan hapus bukunya': js.replace("if (e.n >= 0) return; let r = -e.n; e.n = 0;", "if (e.n >= 0 || true) return; let r = -e.n; e.n = 0;"),
            'tertagih: retur memadamkan bon tertua, bukan nota asalnya': js.replace("const b = m.notaAsalId == null ? null : bon.find((x) => x.u.jenis === 'jual' && String(x.u.idTrx) === String(m.notaAsalId));", "const b = null;"),
            'tertagih: uang yang dibayar di meja saat beli ikut dihitung (0 hari)': js.replace("p.beli && p.hari === 0 ? 'saatBeli' : 'tertagih'", "false ? 'saatBeli' : 'tertagih'"),
            'tertagih: uang saat beli yang memadamkan bon LAMA ikut dibuang': js.replace("p.beli && p.hari === 0 ? 'saatBeli' : 'tertagih'", "p.beli ? 'saatBeli' : 'tertagih'"),
            'tertagih: saat beli cuma dikenali lewat catatan (notaTrxId diabaikan)': js.replace("m.tipe === 'bayar' && ((m.notaTrxId !== undefined && m.notaTrxId !== null && String(m.notaTrxId) !== '')", "m.tipe === 'bayar' && ((false)"),
            'umur: batas setelan diabaikan (tetap 7/30/90)': js.replace("kelompokUmur(aturPelanggan().umurBatas)", "kelompokUmur([7, 30, 90])"),
            'umur: label kelompok tidak ikut angka setelan': js.replace("label: '≤ ' + kataHariBon(a)", "label: '≤ 7 hari'"),
            'umur: bon tanpa tanggal dibuang diam-diam': js.replace("if (berutang.some((b) => b.umur === null)) kel.push(", "if (false) kel.push("),
            'atur: batas umur yang tidak naik diterima': js.replace("if (!umurBatasSah(umur)) return { tolak:", "if (false) return { tolak:"),
            'atur: periode tertagih tidak disimpan': js.replace("umurBatas: umur, tertagihHari: tg.nilai,", "umurBatas: umur,"),
            'layar: kartu tertagih tidak digambar di Garis umur': dengan_layar(inti, lj=LAYAR_JS.replace('${gambarTertagih(Bn.tertagih)}', '')),
            'layar: lembar orang tanpa rata-rata hari bayar': dengan_layar(inti, lj=LAYAR_JS.replace('data-k="tertagih-orang"', 'data-k="x"')),
            # ---- Paket F2: dibayar sesudah dihapus buku
            'F2 hapus buku dibalik ditulis positif (kerugian dobel)': js.replace("nominal: -n, alasan: 'hapus buku dibalik", "nominal: n, alasan: 'hapus buku dibalik"),
            'F2 hapus buku terbayar tetap menulis pembayaran kedua': js.replace("if (!(sudah > 0)) dokumen.push(", "if (true) dokumen.push("),
            'F2 daftar dihapus selalu kosong': js.replace("const dihapus = semua.filter((b) => b.dihapus > 0.5 && b.sisa <= 0 && b.status !== 'lebih')", "const dihapus = semua.filter((b) => false)"),
            'F2 batas = tak terbatas (bukan yang dihapus)': js.replace("const maks = sudah > 0 ? Math.min(sudah, dihapus) : dihapus;", "const maks = 1e12;"),
            'F2 tanpa ketukan kedua': js.replace("if (!yakin) return { tolak: (sudah > 0 ? 'Balik hapus buku '", "if (false) return { tolak: (sudah > 0 ? 'Balik hapus buku '"),
            'F2 riwayat menyebut pembalikan sebagai DIHAPUS': js.replace("bnBalik(m) ? m.ket.replace(/^Hapus buku · /, '').replace(/^Hapus buku/, 'hapus buku dibalik') : m.ket.replace(/^Hapus buku/, 'DIHAPUS dari buku')", "m.ket.replace(/^Hapus buku/, 'DIHAPUS dari buku')"),
            # ---- putaran 25: nota sistem baru (trxId, tanpa grupNota)
            'perbaikan dicabut: nota trxId dipecah per baris (Belanja & ini dia)': js.replace("const plKunciNota = (p) => String(p.grupNota || p.trxId || p.id);", "const plKunciNota = (p) => String(p.grupNota || p.id);"),
            'Belanja saja memecah nota trxId per baris': js.replace("return; const g = plKunciNota(p); if (!grup[g])", "return; const g = String(p.grupNota || p.id); if (!grup[g])"),
            '"ini dia" saja mencari lewat grupNota (nota trxId tidak ketemu)': js.replace("p.tanggal === iso && plKunciNota(p) === String(notaKunci));", "p.tanggal === iso && String(p.grupNota || p.id) === String(notaKunci));"),
            'baris lama tanpa trxId/grupNota tidak lagi jadi nota sendiri': js.replace("const plKunciNota = (p) => String(p.grupNota || p.trxId || p.id);", "const plKunciNota = (p) => String(p.grupNota || p.trxId || 'tanpa-kunci');"),
            # ---- putaran 23b: cip warna kulit & suku/logat dicabut
            'cip sawo matang lolos ke kartu': js.replace(".filter((x, i, a) => x && a.indexOf(x) === i).filter((x) => !cipTerlarang(x)); const lama = kartuTersimpan(kunci);", ".filter((x, i, a) => x && a.indexOf(x) === i); const lama = kartuTersimpan(kunci);"),
            'pembersihan ikut membuang cip berkacamata': js.replace("const sisa = (punyaCip ? dariCip : dariCiri).filter((x) => !cipTerlarang(x));", "const sisa = (punyaCip ? dariCip : dariCiri).filter((x) => !cipTerlarang(x) && x !== 'berkacamata');"),
            'kata terlarang dicocokkan sebagai potongan (beras kena "ras")': js.replace("export const KATA_DICABUT = /\\b(kulit|suku|logat|ras|etnis|etnik)(nya)?\\b/i;", "export const KATA_DICABUT = /(kulit|suku|logat|ras|etnis|etnik)/i;").replace("const KATA_DICABUT = /\\b(kulit|suku|logat|ras|etnis|etnik)(nya)?\\b/i;", "const KATA_DICABUT = /(kulit|suku|logat|ras|etnis|etnik)/i;"),
            'ciri tidak ditulis ulang': js.replace("const kolom = punyaCip ? { cip: sisa, ciri: sisa.join(' · ') } : { ciri: sisa.join(' · ') };", "const kolom = punyaCip ? { cip: sisa } : {};"),
            'pratinjau menulis dokumen': js.replace("const nama = String(c.nama || c.id); cip += buang.length;", "const nama = String(c.nama || c.id); cip += buang.length; terapkanKeCache([{ koleksi: 'pelangganCatatan', data: Object.assign({}, c, kolom) }]);"),
            'tombol hidup tanpa cadangan hari ini': js.replace("if (!r.cadangan) return { tolak: 'Unduh cadangan dulu", "if (false) return { tolak: 'Unduh cadangan dulu"),
            'cadangan kemarin dianggap cukup': js.replace("c.tanggal === iso && c.ok !== false", "c.tanggal <= iso && c.ok !== false"),
            'bersihkan tanpa ketukan kedua': js.replace("if (!yakin) return { tolak: 'Ketuk sekali lagi untuk membersihkan '", "if (false) return { tolak: 'Ketuk sekali lagi untuk membersihkan '"),
            'hitungan "tanpa cip" salah (sisa satu dianggap kosong)': js.replace("tanpaCip: sisa.length === 0,", "tanpaCip: sisa.length <= 1,"),
            '"belum dikenal" tidak melihat catatan & arah': js.replace("belumDikenal: !catatanPelangganBerisi(Object.assign({}, c, kolom))", "belumDikenal: sisa.length === 0"),
            'baris log memuat isi cip yang dibuang': js.replace("ringkas: 'bersihkan ciri yang dicabut: ' + r.kartu.length", "ringkas: 'bersihkan ciri yang dicabut (' + CIP_DICABUT.join(', ') + '): ' + r.kartu.length"),
            'setelan cip owner tidak ikut dibersihkan': js.replace("if (r.atur) ubah.push({ koleksi: 'aturanToko'", "if (false) ubah.push({ koleksi: 'aturanToko'"),
            'setelan ditulis lebih dulu (kalau terputus, bukti terlarang hilang)': js.replace("const ubah = r.kartu.map((k) => ({ koleksi: 'pelangganCatatan', id: k.id, kolom: k.kolom })); if (r.atur) ubah.push(", "const ubah = r.kartu.map((k) => ({ koleksi: 'pelangganCatatan', id: k.id, kolom: k.kolom })); if (r.atur) ubah.unshift("),
            'batas batch diabaikan (201 kartu sekali tulis)': js.replace("for (let i = 0; i < ubah.length; i += BATAS_BERSIHKAN) ubahKolom.push(ubah.slice(i, i + BATAS_BERSIHKAN));", "ubahKolom.push(ubah);"),
            'Atur menerima kelompok kulit / asal': js.replace("if (Array.isArray(isi.ciriDaftar) && isi.ciriDaftar.some((x) => x && !plKosong(x.nama) && ciriDicabut(x.nama, x.grup))) return { tolak: TOLAK_CIRI_DICABUT };", ""),
            'Atur menerima cip berkata suku selama kelompoknya lain': js.replace("const ciriDicabut = (nama, grup) => GRUP_DICABUT.indexOf(String(grup || '')) >= 0 || cipTerlarang(nama);", "const ciriDicabut = (nama, grup) => GRUP_DICABUT.indexOf(String(grup || '')) >= 0;"),
            'setelan tersimpan yang memuat cip dicabut sampai ke daftar cip layar': js.replace("ciriDaftar: daftar('ciriDaftar', (x) => (x && x.nama && !ciriDicabut(x.nama, x.grup) ?", "ciriDaftar: daftar('ciriDaftar', (x) => (x && x.nama ?"),
            'kartu lama menampilkan cip dicabut (Hafalan / Wajah)': js.replace("cip: cip.filter((x) => !cipTerlarang(x)), catatan: String(c.catatan || ''),", "cip, catatan: String(c.catatan || ''),"),
            'kedua saringan lepas: Tampah menanyakan sawo matang': js.replace("ciriDaftar: daftar('ciriDaftar', (x) => (x && x.nama && !ciriDicabut(x.nama, x.grup) ?", "ciriDaftar: daftar('ciriDaftar', (x) => (x && x.nama ?").replace("cip: cip.filter((x) => !cipTerlarang(x)), catatan: String(c.catatan || ''),", "cip, catatan: String(c.catatan || ''),"),
            'cip owner di kelompok lama hilang saat simpan Atur biasa': js.replace("ciriDaftar: ciri.concat(bawa), arahDaftar: arah,", "ciriDaftar: ciri, arahDaftar: arah,"),
            'cip bawaan lama dikenali cuma lewat kelompoknya (Sunda di kartu lolos)': js.replace("if (KATA_DICABUT.test(t) || CIP_DICABUT.some((c) => c.toLowerCase() === k)) return true;", "if (KATA_DICABUT.test(t)) return true;"),
            'svg sketsa memberi kelas nada kulit lagi': dengan_layar(inti, lj=LAYAR_JS.replace("'<svg class=\"sk w' + (sk.warna || 0) + ' ' + (kelas", "'<svg class=\"sk w' + (sk.warna || 0) + ' k' + (sk.kulit || 0) + ' ' + (kelas")),
            'CSS nada kulit kembali': dengan_layar(inti, lc=LAYAR_CSS + '\n.layar-pelanggan .sk.k3 .kepala { fill: #b97f52; }'),
            'keterangan tetap di bawah catatan hilang': dengan_layar(inti, lj=LAYAR_JS.replace('Jangan tulis suku, agama, warna kulit, atau kesehatan.', '')),
            # ---- putaran 22
            'hapus nama tanpa ketukan kedua': js.replace("if (!yakin) return { tolak: 'Ketuk sekali lagi untuk menghapus nama \"'", "if (false) return { tolak: 'Ketuk sekali lagi untuk menghapus nama \"'"),
            'nama berbon boleh dihapus (bonnya jadi yatim)': js.replace("const tolak = piutang.length || O.utang > 0 ? '\"' + O.nama + '\" punya buku bon", "const tolak = false ? '\"' + O.nama + '\" punya buku bon"),
            # ---- putaran 21
            'nama paku benang dipotong di tanda hubung ("Al -")': js.replace("const n = String(nama || '').replace(/\\s*-\\s*/g, '-').trim(); if (n.length <= 16) return n;", "const n = String(nama || '').trim(); if (n.length <= 16) return n.split(/\\s+/).slice(0, 2).join(' ');"),
            'sketsa membaca warna kulit lagi (DIGANTI 23b; dulu "sketsa mengabaikan warna kulit")': js.replace("return { kosong: !b.cip.length, kerudung:", "return { kosong: !b.cip.length, kulit: punya(b, 'sawo matang') ? 3 : 0, kerudung:"),
            'brewok tidak menggambar janggut': js.replace("janggut: punya(b, 'janggut') || punya(b, 'brewok')", "janggut: punya(b, 'janggut')"),
            'pembayar bon tidak dihitung datang': js.replace("if (o && m.tipe === 'bayar' && m.tanggal) o.hari[m.tanggal] = (o.hari[m.tanggal] || 0) + 1;", ""),
            'selang dihitung walau kurang dari 3 kedatangan': js.replace("const selang = kunjungan >= 3 ?", "const selang = kunjungan >= 2 ?"),
            'bangku kosong memakai batas tetap, bukan selang orang itu': js.replace("const kosong = adaSelang && sejak * 10 >= selang * atur.kosongKali;", "const kosong = sejak !== null && sejak >= 30;"),
            'kartu gaya lama (ciri teks) dibaca tanpa cip': js.replace("const cip = Array.isArray(c.cip) ? c.cip.map(String) : String(c.ciri || '').split(/\\s*[·,;]\\s*/).map((x) => x.trim()).filter(Boolean);", "const cip = Array.isArray(c.cip) ? c.cip.map(String) : [];"),
            'pasangan yang sudah dinyatakan bukan kembar tetap ditawarkan': js.replace("if (bukan.indexOf(k) < 0) out.push({ k, a, b });", "out.push({ k, a, b });"),
            'ganti nama yang mengubah kunci diterima diam-diam': js.replace("if (kunciPelanggan(nama) !== kunci) return { tolak: 'Mengganti nama", "if (false) return { tolak: 'Mengganti nama"),
            'ciri gabungan tidak ditulis ke kolom lama (KR1 sistem lama buta)': js.replace("catatan: String(isi.catatan || '').trim(), ciri: cip.join(' · '), rute:", "catatan: String(isi.catatan || '').trim(), ciri: '', rute:"),
            'tampah memakai pertanyaan pertama di daftar, bukan yang membelah paling rata': js.replace("if (!tanya || timpang < tanya.timpang) tanya = { c: c.nama, grup: c.grup, n, timpang };", "if (!tanya) tanya = { c: c.nama, grup: c.grup, n, timpang };"),
            '"ini dia" menempel nama ke nota yang sudah bernama': js.replace("if (baris.some((p) => String(p.namaPelanggan || '').trim())) return { tolak: 'Nota itu sudah bernama' };", ""),
            '"ini dia" menulis sebagian baris nota saja': js.replace("return { dokumen: baris.map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { namaPelanggan: o.nama }) })),", "return { dokumen: baris.slice(0, 1).map((p) => ({ koleksi: 'penjualan', data: Object.assign({}, p, { namaPelanggan: o.nama }) })),"),
            'gabung melewati batas satu writeBatch': js.replace("if (!r.bisa) return { tolak: r.n + ' dokumen atas nama", "if (false) return { tolak: r.n + ' dokumen atas nama"),
            'gabung tidak menghapus kartu nama lama (kartu yatim)': js.replace("if (kL) hapus.push({ koleksi: 'pelangganCatatan', id: kL.dok.id });", ""),
            'THR dua kali setahun untuk orang yang sama diterima': js.replace("if (ambilThrPelanggan().some((t) => t.kunci === kunci && Number(t.tahun) === Th)) return { tolak:", "if (false) return { tolak:"),
            'usul THR melampaui amplop': js.replace("const calon = t.belumDapat.filter((b) => b.belanja > 0).slice(0, muat);", "const calon = t.belumDapat.filter((b) => b.belanja > 0);"),
            'bon: rincian tidak FIFO (pembayaran tidak memadamkan bon tertua)': js.replace("for (const u of utang) { const nom = u.nominal - (u.diretur || 0); if (tertutup >= nom) { tertutup -= nom; continue; }", "for (const u of utang) { const nom = u.nominal - (u.diretur || 0); if (false) { tertutup -= nom; continue; }"),   # jangkar disesuaikan 39b no. 37 tinjauan MM1
            'bon: macet tanpa syarat "tidak ada pembayaran selama itu"': js.replace("umur > atur.macetHari && (diamSejak === null || diamSejak > atur.macetHari);", "umur > atur.macetHari;"),
            'bon: janji dianggap lewat walau sudah membayar sesudah ditagih': js.replace("tagih.janji < iso && (!bayarAkhir || bayarAkhir.tanggal < tagih.tanggal);", "tagih.janji < iso;"),
            # ---- 39b no. 4: sisa negatif berbunyi
            'no.4: kelebihan bayar dicap "lunas" lagi': js.replace("const status = sisa < LEBIH_AMBANG ? 'lebih' : sisa <= 0 ? 'lunas'", "const status = sisa <= 0 ? 'lunas'"),
            'no.4: tab Bon tanpa daftar kelebihan bayar': js.replace("const lebih = semua.filter((b) => b.status === 'lebih')", "const lebih = semua.filter((b) => false)"),
            'no.4: bayar bon untuk nama kelebihan bayar tidak ditolak duluan': js.replace("  if (b.status === 'lebih') return { tolak: b.nama + ': ' + kalimatLebih(pecahLebih(b)) + '. Tidak ada bon untuk dibayar.' };", ""),
            'no.4: hapus bon untuk nama kelebihan bayar tidak ditolak duluan': js.replace("  if (b.status === 'lebih') return { tolak: b.nama + ': ' + kalimatLebih(pecahLebih(b)) + '. Tidak ada bon untuk dihapus dari buku.' };", ""),
            'no.4: kartu orang tanpa kelebihan bayar': js.replace("const PL = pecahLebih(r); const lebih = PL.lebih;", "const PL = pecahLebih(null); const lebih = 0;"),
            'no.4 B1: hapus buku terbayar disebut uang pelanggan (pecahan dicabut)': js.replace("const uang = Math.min(lebih, Math.max(0, (Number(d.bayar) || 0) - ((Number(d.total) || 0) - (Number(d.retur) || 0)))); return { lebih, uang, hapus: lebih - uang };", "return { lebih, uang: lebih, hapus: 0 };"),
            'no.4: gabung nama menjumlah utang yang dijepit 0': js.replace("(P.utang - P.lebih + L.utang - L.lebih > 0 ? ', bon ' + RP(P.utang - P.lebih + L.utang - L.lebih)", "(P.utang + L.utang > 0 ? ', bon ' + RP(P.utang + L.utang)"),
            'no.4: ambang kelebihan bayar di nol (sisa pembulatan jadi kelebihan)': js.replace("const LEBIH_AMBANG = -0.5;", "const LEBIH_AMBANG = 0;"),
            'bon: pembayaran melebihi sisa diterima': js.replace("if (n > b.sisa) return { tolak: 'Pembayaran ' + RP(n) + ' melebihi sisa bonnya", "if (false) return { tolak: 'Pembayaran ' + RP(n) + ' melebihi sisa bonnya"),
            '39b-3: kalimat bayar bon QRIS tidak menyebut potongan tutup hari': js.replace("return cara === 'QRIS' ? 'potongan QRIS (MDR)-nya, kalau ada, dicatat saat tutup hari' : '';", "return '';"),
            '39b-3 T6: bayar bon sesudah hari ditutup tetap menjanjikan "dicatat saat tutup hari"': js.replace("if (t) return 'hari ini SUDAH ditutup'", "if (false) return 'hari ini SUDAH ditutup'"),
            'bon: LUNAS diucapkan padahal masih bersisa': js.replace("kabar: (sisaBaru <= 0 ? b.nama + ' LUNAS.", "kabar: (true ? b.nama + ' LUNAS."),
            'bon: hapus buku tanpa alasan diterima': js.replace("if (bnKosong(alasan)) return { tolak: 'Alasannya wajib", "if (false) return { tolak: 'Alasannya wajib"),
            'bon: hapus buku tanpa ketukan kedua': js.replace("if (!yakin) return { tolak: 'Hapus ' + RP(n) + ' dari buku", "if (false) return { tolak: 'Hapus ' + RP(n) + ' dari buku"),
            'bon: pesan tagihan tanpa rincian bon': js.replace("b.buka.forEach((r) => baris.push('- ' + formatTanggal(r.tanggal)", "[].forEach((r) => baris.push('- ' + formatTanggal(r.tanggal)"),
            'bon: nomor WhatsApp tidak diubah ke awalan 62': js.replace("const nomor = !digit ? '' : digit.indexOf('0') === 0 ? '62' + digit.slice(1) : digit.indexOf('62') === 0 ? digit : digit.indexOf('8') === 0 ? '62' + digit : digit;", "const nomor = digit;"),
            'bon: tagihan tidak mencatat janji bayar': js.replace("const janji = Number(janjiHari) > 0 ? tambahHari(w.tanggal, Number(janjiHari)) : null;", "const janji = null;"),
            'bon: pengantar yang sama dengan pemilik bon dicatat sebagai pengantar': js.replace("if (!bnKosong(pengantar) && kunciPelanggan(pengantar) !== kunci) data.dibawaOleh", "if (!bnKosong(pengantar)) data.dibawaOleh"),
            'aturan owner diabaikan (bangku kosong tetap 2,0×)': js.replace("return { kosongKali: angka('kosongKali', (n) => n >= 10 && n <= 100),", "return { kosongKali: 20,"),
            'status bon tidak memakai aturan owner (tagih tetap 14 hari)': js.replace("umur !== null && umur >= atur.tagihHari ? 'perluTagih' : 'baru'", "umur !== null && umur >= 14 ? 'perluTagih' : 'baru'").replace("tagihHari: angka('tagihHari', (n) => n >= 0 && n <= 365),", "tagihHari: 14,"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    # paket brief 9 Okt: penanda pembayaran saat beli di bon-logika = struk-logika ST_CATATAN_BAYAR_BELI (= catatan yang ditulis jual-logika & index.html)
    _st = open(os.path.join(AKAR, 'baru/js/layar/struk-logika.js'), encoding='utf-8').read(); _bn = open(os.path.join(AKAR, 'baru/js/layar/bon-logika.js'), encoding='utf-8').read()
    if "export const ST_CATATAN_BAYAR_BELI = 'Dibayar langsung saat beli';" not in _st or "const BN_BAYAR_SAAT_BELI = 'Dibayar langsung saat beli';" not in _bn: g.append('penanda bayar saat beli bon-logika ≠ struk-logika')
    else: l += 1
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8')); tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        h, e = jalan(kunci_jam(tgl + 'T20:00:00+07:00') + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s): %d orang (%d dikenali) · kunjungan layar = pasangan nama×hari nyata: %s (%d) · belanja bernama layar = baris nyata: %s · sisa bon layar = mesin beku: %s · %d berutang · %d pasang nama kembar ditawarkan · %d bangku kosong · %d waktunya datang · tampah bertanya "%s" · %d wajah · THR %d nama'
                  % (os.path.basename(cad[-1]), h['orang'], h['dikenali'], h['kunjunganLayar'] == h['kunjunganNyata'], h['kunjunganNyata'], h['belanjaLayar'] == h['belanjaNyata'], h['sisaLayar'] == h['sisaMesin'], h['berutang'], h['kembar'], h['kosong'], h['diharap'], h['tampah'], h['wajah'], h['thr']))
            if h['kunjunganLayar'] != h['kunjunganNyata'] or h['belanjaLayar'] != h['belanjaNyata'] or h['sisaLayar'] != h['sisaMesin'] or h['wajah'] != h['orang']: g.append('asap: angka layar tidak cocok dengan baris nyata / mesin')
            x = h['lebih']
            print('ASAP DATA TOKO 39b-4 · kelebihan bayar pelanggan: %d nama (sisa mesin < −0,5: %d) · tab Bon memuat %d · jumlah cocok: %s' % (x['n'], x['negMesin'], x['bon'], x['cocok']))
            if x['n'] != x['negMesin'] or not x['cocok']: g.append('asap 39b-4: daftar kelebihan bayar tidak sama dengan sisa negatif mesin / tab Bon')
            print('ASAP DATA TOKO: kolom dokumen (bayar, hapus buku, kartu) vs cadangan: %s · kop WhatsApp: %s' % (', '.join(h['asing']) or 'semua dikenal', h['waKop']))
            if h['asing'] or h['waKop'] != '*TOKO BERAS M.IQBAL*': g.append('asap: dokumen punya kolom yang tidak dikenal cadangan / kop tagihan berubah')
            b = h['bs']
            print('ASAP DATA TOKO 23b · pratinjau Bersihkan: %d kartu memuat cip dicabut · %d cip dibuang · %d jadi tanpa cip (%d belum dikenal di KR1) · setelan ikut: %s · teks bebas berkata terlarang: %d (%s) · pratinjau menulis nol: %s'
                  % (b['kartu'], b['cip'], b['tanpaCip'], b['belumDikenal'], b['atur'], b['bebas'], ', '.join(b['bebasKolom']) or '-', b['pratinjauDiam']))
            print('ASAP DATA TOKO 23b · suntikan %d kartu nyata (%d gaya lama tanpa larik cip) → %d ditulis dari %d yang wajib · kolom selain cip/ciri byte-sama & kartu lain utuh: %s · cip = semula tanpa cip dicabut & ciri = gabungan cip: %s%s'
                  % (b['suntik'], b['suntikLama'], b['ditulis'], b['harus'], b['identik'], b['pulih'], (' · DITOLAK: ' + b['tolak']) if b['tolak'] else ''))
            if not (b['pratinjauDiam'] and b['identik'] and b['pulih'] and b['ditulis'] == b['harus']): g.append('asap 23b: pembersihan di data toko tidak identik')
            t = h['tg']; R_ = lambda x: 'Rp' + '{:,.0f}'.format(x).replace(',', '.')
            print('ASAP DATA TOKO (angka toko, cadangan %s) · rata-rata hari bon tertagih %d hari terakhir (%s s.d. %s): %s [%s] · dibayar %d bon %s · dibayar di meja saat beli %d bon %s · saldo awal %d bon %s (belum bisa dihitung) · hapus buku %d bon %s · retur %d bon %s · lain %d · tanpa tanggal %d · lunas %d bon %s · bagian = total: %s · %d orang punya rata-rata sendiri'
                  % (tgl, t['hari'], t['awal'], t['akhir'], t['rataTeks'], t['keadaan'], t['tertagih']['n'], R_(t['tertagih']['rp']), t['saatBeli']['n'], R_(t['saatBeli']['rp']), t['saldoAwal']['n'], R_(t['saldoAwal']['rp']), t['hapusBuku']['n'], R_(t['hapusBuku']['rp']), t['retur']['n'], R_(t['retur']['rp']), t['lain']['n'], t['tanpaTanggal']['n'], t['lunas']['n'], R_(t['lunas']['rp']), t['tutup'], t['orangAda']))
            print('ASAP DATA TOKO · kelompok umur (orang menurut bon tertuanya · sisa): %s · Σ = sisa semuanya %s: %s · bon terbuka per kelompok (umur bon itu sendiri): %s · jalan tutup = mesin: %d dari %d buku bon tidak cocok'
                  % (' | '.join('%s: %d · %s' % (e['label'], e['n'], R_(e['jumlah'])) for e in t['umur']), R_(t['sisa']), t['umurCocok'], ', '.join('%s %d' % (k, v) for k, v in t['bonKel'].items()) or '-', t['tidakCocok'], t['nBuku']))
            if not t['tutup'] or t['tidakCocok'] or not t['umurCocok']: g.append('asap tertagih: bagian tidak menutup / jalan tutup tidak sama dengan mesin / kelompok umur tidak menutup')
    sys.exit(2 if g else 0)
