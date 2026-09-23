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
var HB0 = susunHapusBon(KINI, 'pak hartawan', '250.000', 'pindah, tidak bisa dihubungi', W, false); var HB = susunHapusBon(KINI, 'pak hartawan', '250.000', 'pindah, tidak bisa dihubungi', W, true);
ok('hapus buku: alasan wajib; ketukan pertama DITANYA dengan kalimat "BUKAN uang masuk … KERUGIAN"; ketukan kedua → dokumen tipe hapusBuku persis simpanHapusBuku; sesudahnya mesin beku membaca sisa Hartawan 0; melebihi sisa ditolak', /wajib/.test(susunHapusBon(KINI, 'pak hartawan', '250.000', '', W, true).tolak) && HB0.perluYakin === true && /BUKAN uang masuk/.test(HB0.tolak) && /KERUGIAN/.test(HB0.tolak) && !HB.tolak && Object.keys(HB.dokumen[0].data).sort().join(',') === ['id', 'tipe', 'namaPelanggan', 'nominal', 'alasan', 'tanggal', 'jam', 'dicatatDi'].sort().join(',') && HB.dokumen[0].data.tipe === 'hapusBuku'
  && (function () { var s = simpan(); terapkan(HB); var r = hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }).sisa === 0 && hitungPiutang().find(function (x) { return x.kunci === 'pak hartawan'; }).dihapus === 250000; pulih(s); return r; })() && /melebihi sisa/.test(susunHapusBon(KINI, 'pak hartawan', '300.000', 'x', W, true).tolak), JSON.stringify([HB0, HB]));
// ---- PUTARAN 21 (owner 23 Sep): ciri serinci mungkin & sketsanya; nama paku benang utuh; benang di kartu; urusan ojek/kurir
var SK1 = sketsa({ cip: ['sawo matang', 'kumis', 'gemuk', 'botak', 'naik motor', '40-an', 'Sunda'] }); var SK2 = sketsa({ cip: ['kerudung', 'kulit putih', 'kurus', 'tinggi', 'kacamata'] }); var SK3 = sketsa({ cip: ['brewok', 'rambut panjang', 'kulit gelap', 'pendek'] });
ok('P21 ciri: kelompok bertambah (umur, perawakan, kulit, wajah & rambut, suku/logat) dan tiap cip bawaan punya kelompoknya; urusan titipan bawaan memuat ojek / kurir langganan', TANYA_CIRI.length === 9 && ATUR_PELANGGAN_BAWAAN.ciriDaftar.every(function (c) { return TANYA_CIRI.some(function (t) { return t[0] === c.grup; }); }) && ATUR_PELANGGAN_BAWAAN.ciriDaftar.length > 40 && ATUR_PELANGGAN_BAWAAN.titipDaftar.indexOf('ojek / kurir langganan') >= 0);
ok('P21 sketsa ikut ciri: sawo matang → kulit 3, kumis, gemuk, botak (tanpa rambut), motor; kerudung + kulit putih + kurus + tinggi + kacamata; brewok = kumis & janggut, rambut panjang, kulit gelap 4, pendek', SK1.kulit === 3 && SK1.kumis && !SK1.janggut && SK1.gemuk && SK1.botak && !SK1.rambut && SK1.naik === 'motor' && SK2.kerudung && SK2.kulit === 1 && SK2.kurus && SK2.tinggi && SK2.kacamata && !SK2.rambut && SK3.kumis && SK3.janggut && SK3.panjang && SK3.kulit === 4 && SK3.pendek && SK3.rambut, JSON.stringify([SK1, SK2, SK3]));
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
var LB = lembarBon(KINI, 'uda feri');
ok('lembar orang: rincian 2 bon terbuka (yang pertama "dari Rp780.000"), riwayat memuat pembayaran & tagihan (terbaru dulu), pilihan alasan hapus dari aturan', LB.rinci.length === 2 && /dari Rp780\.000/.test(LB.rinci[0].teks) && LB.rinci[0].n === 670000 && LB.riwayat.length === 2 && /ditagih · janji/.test(LB.riwayat[0].teks) && LB.riwayat[1].n === -110000 && LB.alasanPilihan.length === 4, JSON.stringify(LB.riwayat));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var O = semuaOrang(KINI); var WX = { tanggal: '2026-09-22', jam: '10:00', kini: '2026-09-22T03:00:00.000Z', idUnik: function () { return Math.random(); } }; var asing = [];
var berlaku = ambilPenjualan().filter(function (p) { return String(p.namaPelanggan || '').trim(); }); var pasangan = {}; berlaku.forEach(function (p) { pasangan[kunciPelanggan(p.namaPelanggan) + '|' + p.tanggal] = 1; });
ambilPiutangMutasi().forEach(function (m) { if (m.tipe === 'bayar' && m.namaPelanggan) pasangan[kunciPelanggan(m.namaPelanggan) + '|' + m.tanggal] = 1; });
var kunjunganLayar = O.reduce(function (a, b) { return a + b.kunjungan; }, 0); var kunjunganNyata = Object.keys(pasangan).length;
var belanjaLayar = O.reduce(function (a, b) { return a + b.total; }, 0); var belanjaNyata = berlaku.reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0);
var SB = semuaBon(KINI); var sisaLayar = SB.reduce(function (a, b) { return a + b.sisa; }, 0); var sisaMesin = hitungPiutang().reduce(function (a, b) { return a + b.sisa; }, 0);
var kenalB = {}; (CAD.piutangMutasi || []).forEach(function (m) { if (m.tipe === 'bayar') Object.keys(m).forEach(function (k) { kenalB[k] = 1; }); }); kenalB.dibawaOleh = 1;
var berutang = SB.filter(function (b) { return b.sisa > 0; })[0]; if (berutang) { var by = susunBayarBon(KINI, berutang.kunci, '1', 'Tunai', 'uji', '', WX); if (by.dokumen) Object.keys(by.dokumen[0].data).forEach(function (k) { if (!kenalB[k]) asing.push('bayar.' + k); }); else asing.push('bayar ditolak: ' + by.tolak);
  var hb = susunHapusBon(KINI, berutang.kunci, '1', 'uji', WX, true); if (hb.dokumen) Object.keys(hb.dokumen[0].data).forEach(function (k) { if (!kenalB[k] && k !== 'alasan') asing.push('hapusBuku.' + k); }); else asing.push('hapus ditolak: ' + hb.tolak); }
var kenalK = {}; (CAD.pelangganCatatan || []).forEach(function (c) { Object.keys(c).forEach(function (k) { kenalK[k] = 1; }); }); ['cip', 'arah', 'asli', 'kontak', 'biasa', 'diubahPada'].forEach(function (k) { kenalK[k] = 1; });
var kartuAda = O.find(function (b) { return b.kartu; }); if (kartuAda) { var sk = susunSimpanKartu(KINI, kartuAda.kunci, { nama: kartuAda.nama, cip: kartuAda.cip, catatan: kartuAda.catatan, arah: kartuAda.arah }, WX); if (sk.dokumen) Object.keys(sk.dokumen[0].data).forEach(function (k) { if (!kenalK[k]) asing.push('kartu.' + k); }); else asing.push('kartu ditolak: ' + sk.tolak); }
var pt = berutang ? pesanTagih(KINI, berutang.kunci) : null;
print(JSON.stringify({ orang: O.length, dikenali: O.filter(function (b) { return b.dikenali; }).length, kunjunganLayar: kunjunganLayar, kunjunganNyata: kunjunganNyata, belanjaLayar: belanjaLayar, belanjaNyata: belanjaNyata, sisaLayar: sisaLayar, sisaMesin: sisaMesin, berutang: SB.filter(function (b) { return b.sisa > 0; }).length,
  kembar: pasanganKembar(O).length, kosong: O.filter(function (b) { return b.kosong; }).length, diharap: O.filter(function (b) { return b.diharap; }).length, tampah: susunTampah(KINI, []).tanya ? susunTampah(KINI, []).tanya.c : null, wajah: susunWajah(KINI, '').daftar.length, asing: asing, waKop: pt ? pt.baris[0] : null, thr: susunThr(KINI, 2026).daftar.length }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            # ---- putaran 22
            'hapus nama tanpa ketukan kedua': js.replace("if (!yakin) return { tolak: 'Ketuk sekali lagi untuk menghapus nama \"'", "if (false) return { tolak: 'Ketuk sekali lagi untuk menghapus nama \"'"),
            'nama berbon boleh dihapus (bonnya jadi yatim)': js.replace("const tolak = piutang.length || O.utang > 0 ? '\"' + O.nama + '\" punya buku bon", "const tolak = false ? '\"' + O.nama + '\" punya buku bon"),
            # ---- putaran 21
            'nama paku benang dipotong di tanda hubung ("Al -")': js.replace("const n = String(nama || '').replace(/\\s*-\\s*/g, '-').trim(); if (n.length <= 16) return n;", "const n = String(nama || '').trim(); if (n.length <= 16) return n.split(/\\s+/).slice(0, 2).join(' ');"),
            'sketsa mengabaikan warna kulit': js.replace("kulit: kulit ? kulit[1] : 0, gemuk:", "kulit: 0, gemuk:"),
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
            'bon: rincian tidak FIFO (pembayaran tidak memadamkan bon tertua)': js.replace("for (const u of utang) { if (tertutup >= u.nominal) { tertutup -= u.nominal; continue; }", "for (const u of utang) { if (false) { tertutup -= u.nominal; continue; }"),
            'bon: macet tanpa syarat "tidak ada pembayaran selama itu"': js.replace("umur > atur.macetHari && (diamSejak === null || diamSejak > atur.macetHari);", "umur > atur.macetHari;"),
            'bon: janji dianggap lewat walau sudah membayar sesudah ditagih': js.replace("tagih.janji < iso && (!bayarAkhir || bayarAkhir.tanggal < tagih.tanggal);", "tagih.janji < iso;"),
            'bon: pembayaran melebihi sisa diterima': js.replace("if (n > b.sisa) return { tolak: 'Pembayaran ' + RP(n) + ' melebihi sisa bonnya", "if (false) return { tolak: 'Pembayaran ' + RP(n) + ' melebihi sisa bonnya"),
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
            print('ASAP DATA TOKO: kolom dokumen (bayar, hapus buku, kartu) vs cadangan: %s · kop WhatsApp: %s' % (', '.join(h['asing']) or 'semua dikenal', h['waKop']))
            if h['asing'] or h['waKop'] != '*TOKO BERAS M.IQBAL*': g.append('asap: dokumen punya kolom yang tidak dikenal cadangan / kop tagihan berubah')
    sys.exit(2 if g else 0)
