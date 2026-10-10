#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_menu_baru.py — uji logika layar MENU & SISTEM sistem baru (baru/js/layar/menu-logika.js + sistem-logika.js) di jsc.
KOTAK PASIR (NAMA & ANGKA CONTOH, bukan pelanggan/pemasok toko), jam dikunci 19 Sep 2026 10:00 WIB (Sabtu, pagi).
Kalau ada backup-batch-*.json lokal (asap): angka laci = mesin beku; berkas cadangan sistem baru memuat SEMUA koleksi cadangan lama.

    python3 alat-uji/uji_menu_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_menu_baru.py --kontrol  → logika yang dirusak wajib ketahuan (jalankan HANYA sesudah 0 gagal)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/pelanggan-logika.js', 'baru/js/layar/bon-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/uang-logika.js', 'baru/js/data/akses.js', 'baru/js/layar/nego-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/sistem-logika.js', 'baru/js/layar/menu-logika.js']
def kunci_jam(iso):
    return ("var __RealDate = Date; var __KINI = new __RealDate('%s').getTime();\n"
            "Date = function (a, b, c, d, e, f, g) { if (!(this instanceof Date)) return new __RealDate(__KINI).toString(); if (arguments.length === 0) return new __RealDate(__KINI); if (arguments.length === 1) return new __RealDate(a); return new __RealDate(a, b, c === undefined ? 1 : c, d || 0, e || 0, f || 0, g || 0); };\n"
            "Date.prototype = __RealDate.prototype; Date.now = function () { return __KINI; }; Date.UTC = __RealDate.UTC; Date.parse = __RealDate.parse;\n") % iso
JAM_TETAP = kunci_jam('2026-09-19T10:00:00+07:00')


def jual(id, tgl, jam, nama, jenis, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': jam, 'namaPelanggan': nama, 'caraBayar': k.pop('cara', 'Tunai'), 'jenis': jenis, 'hargaTotal': k.pop('n', 0), 'hppTotalSaatJual': k.pop('hpp', 0), 'oleh': k.pop('oleh', 'Owner')}
    d.update(k); return d
def literan(id, tgl, jam, nama, merk, liter, n, **k): return jual(id, tgl, jam, nama, 'literan', merkSumber=merk, jumlahLiter=liter, totalKg=round(liter * 0.82, 2), n=n, **k)
def karung(id, tgl, jam, nama, merk, jml, n, **k): return jual(id, tgl, jam, nama, 'karung', merkSumber=merk, namaProduk=merk + ' (karung utuh)', jumlahKarung=jml, beratKarungAcuan=50, totalKg=50 * jml, n=n, **k)
def batch(id, tgl, pemasok, cara, merk, kg, harga): return {'id': id, 'tanggal': tgl, 'jam': '10:00', 'pemasok': pemasok, 'caraBayar': cara, 'biayaBongkar': 0, 'merkList': [{'id': id * 10, 'merk': merk, 'satuan': 'karung', 'jumlahKarung': kg // 50, 'beratKarung': 50, 'totalKg': kg, 'hargaPerKg': harga, 'subtotalHarga': kg * harga}]}


KOTAK = {
  'penjualan': [
    literan(301, '2026-08-03', '08:10', 'Bu Rahma', 'Angsa', 3, 37500, hpp=30000),                                       # catatan pertama 3 Agu → Agustus TIDAK utuh
    karung(302, '2026-09-10', '09:00', 'Pak Darto', 'Angsa', 1, 690000, cara='Kredit', hpp=600000), karung(303, '2026-09-12', '16:10', 'Pak Darto', 'Angsa', 1, 690000, cara='Kredit', hpp=600000),
    karung(304, '2026-09-15', '16:00', '', 'IR42 Select', 2, 1560000, hpp=1400000),
    literan(305, '2026-09-16', '12:30', 'Mbak Yuni', 'IR64 Apex', 10, 130000, cara='QRIS', hpp=110000),
    literan(306, '2026-09-17', '07:30', 'Bu Sri', 'Angsa', 8, 100000, hpp=85000, dirinciPada='2026-09-17T13:15:00+07:00'),   # karcis: jam meja 07, disalin 13
    karung(307, '2026-09-18', '16:20', 'Uda Feri', 'IR42 Select', 1, 780000, cara='Kredit', hpp=700000, oleh='Ben'),
    karung(308, '2026-09-18', '16:40', '', 'Angsa', 2, 1380000, hpp=1250000, lokasi='gudang'),                            # dicatat perangkat di lokasi gudang
    literan(309, '2026-09-19', '08:15', '', 'Angsa', 3, 37500, hpp=30000),
    literan(310, '2026-09-01', '11:00', 'Mas Bimo', 'Angsa', 5, 70000, cara='Kredit', hpp=60000),
  ],
  'batchMasuk': [batch(401, '2026-08-20', 'CV Padi Jaya', 'utang', 'Angsa', 3000, 12000), batch(402, '2026-09-05', 'CV Padi Jaya', 'utang', 'IR42 Select', 1500, 14000), batch(403, '2026-09-01', 'UD Beras Makmur', 'tunai', 'IR64 Apex', 1000, 11500)],
  'utangPemasokMutasi': [{'id': 501, 'tipe': 'bayar', 'pemasok': 'CV Padi Jaya', 'nominal': 10000000, 'tanggal': '2026-09-08', 'jam': '19:00', 'bonId': '401'}],
  'katalogHargaKarung': [{'merk': 'Angsa', 'hargaPerKg': 12500}, {'merk': 'IR42 Select', 'hargaPerKg': 13800}, {'merk': 'IR64 Apex', 'hargaPerKg': 12000}],
  'katalogHargaKemasan': [{'id': 1, 'merk': 'Angsa', 'ukuran': 5, 'harga': 70000, 'diubahPada': '2026-09-15T12:10:00+07:00'}],
  'katalogHargaLiteran': [{'merk': 'Angsa', 'hargaPerLiter': 12500, 'diubahPada': '2026-09-15T12:20:00+07:00'}],
  'piutangMutasi': [
    {'id': 601, 'tipe': 'saldoAwal', 'namaPelanggan': 'Pak Hartawan', 'nominal': 250000, 'tanggal': '2022-07-15', 'catatan': 'Sisa dari catatan lama', 'dicatatDi': 'sistem'},
    {'id': 602, 'tipe': 'bayar', 'namaPelanggan': 'Mas Bimo', 'nominal': 20000, 'tanggal': '2026-09-14', 'jam': '17:00', 'caraBayar': 'Tunai', 'catatan': '', 'dicatatDi': 'sistem'},
  ],
  'tagihPelanggan': [{'id': 'tg1', 'kunci': 'pak darto', 'nama': 'Pak Darto', 'tanggal': '2026-09-14', 'jam': '10:00', 'janji': '2026-09-17', 'sisa': 1380000}, {'id': 'tg2', 'kunci': 'mas bimo', 'nama': 'Mas Bimo', 'tanggal': '2026-09-08', 'jam': '10:00', 'janji': '2026-09-12', 'sisa': 70000}],
  'pelangganCatatan': [{'id': 'pak darto', 'nama': 'Pak Darto', 'catatan': '', 'ciri': 'bapak-bapak', 'rute': '', 'cip': ['bapak-bapak'], 'kontak': '0813 0000 2290'}],
  'penyesuaianStok': [{'id': 701, 'merk': 'Angsa', 'tanggal': '2026-08-30', 'jam': '19:00', 'kgSistem': 100, 'kgFisik': 98, 'selisihKg': -2, 'alasan': 'susut'}, {'id': 702, 'merk': 'Angsa', 'tanggal': '2026-09-02', 'jam': '19:30', 'kgSistem': 90, 'kgFisik': 90, 'selisihKg': 0, 'nilaiRp': 0, 'alasan': ''}],
  'produksiKemasan': [{'id': 801, 'batchProduksi': 'p1', 'tanggal': '2026-09-10', 'jam': '10:00', 'merkTujuan': 'Angsa', 'namaProduk': 'Angsa', 'ukuranKemasan': 5, 'jumlahUnit': 20, 'kgDipakai': 100, 'sumberList': [{'merk': 'Angsa', 'kg': 100}], 'hppSumberPerKgDipakai': 12000, 'hppTotalBahan': 1200000, 'biayaTotal': 1200000}],
  'stokBahanKemasan': [{'id': 901, 'tipe': 'beli', 'jenis': '5kg_kembangbmw', 'jumlah': 200, 'hargaTotal': 400000, 'tanggal': '2026-08-15'}, {'id': 902, 'tipe': 'pakai', 'jenis': '5kg_kembangbmw', 'jumlah': 140, 'hargaTotal': 0, 'tanggal': '2026-09-10'},
                       {'id': 903, 'tipe': 'beli', 'jenis': '10kg_kembangbmw', 'jumlah': 100, 'hargaTotal': 300000, 'tanggal': '2026-08-15'}],
  'kasbonMutasi': [{'id': 1001, 'tipe': 'ambil', 'namaPegawai': 'Ben', 'nominal': 500000, 'tanggal': '2026-09-01'}, {'id': 1002, 'tipe': 'ambil', 'namaPegawai': 'Gama', 'nominal': 300000, 'tanggal': '2026-08-20'}, {'id': 1003, 'tipe': 'bayar', 'namaPegawai': 'Gama', 'nominal': 300000, 'tanggal': '2026-09-05'}],
  'perangkatStatus': [{'id': 'p-a1', 'nama': 'HP owner', 'aplikasi': 'baru', 'pada': '2026-09-19T02:55:00.000Z', 'antrean': 0, 'pemegang': 'Owner', 'lokasi': 'toko'}, {'id': 'p-b2', 'nama': '', 'aplikasi': 'sistem', 'pada': '2026-09-18T12:00:00.000Z', 'antrean': 2}],
  'logAktivitas': [{'id': 1101, 'pada': '2026-09-19T01:30:00.000Z', 'aksi': 'tulis', 'koleksi': 'penjualan', 'idDok': '309', 'oleh': 'Owner', 'perangkat': 'HP owner', 'ringkas': 'Angsa · Rp37.500'},
                   {'id': 1102, 'pada': '2026-09-18T09:40:00.000Z', 'aksi': 'tulis', 'koleksi': 'penjualan', 'idDok': '307', 'oleh': 'Ben', 'perangkat': 'Mac toko', 'ringkas': 'Uda Feri'},
                   {'id': 1103, 'pada': '2026-09-19T02:50:00.000Z', 'aksi': 'tulis', 'koleksi': 'piutangMutasi', 'idDok': '999', 'oleh': 'Owner', 'perangkat': 'HP owner', 'ringkas': 'x'}],
  'cadanganCatatan': [{'id': 1201, 'tanggal': '2026-09-09', 'jam': '20:00', 'perangkat': 'HP owner', 'nama': 'backup-batch-miqbal-2026-09-09.json', 'ukuranKb': 3200, 'dokumen': 1500, 'koleksi': 30, 'jenis': 'manual', 'ok': True}],
  'pengingat': [{'id': 'cadangan|2026-09-16', 'jenis': 'cadangan', 'jatuh': '2026-09-16', 'status': 'selesai', 'catatan': 'sudah diunduh ke laptop'}, {'id': 'opname|2026-09-16', 'jenis': 'opname', 'jatuh': '2026-09-16', 'status': 'tunda', 'tundaHari': 2, 'tundaKali': 1}],
  'aturanToko': [{'id': 'lokasi', 'daftar': [{'id': 'toko', 'nama': 'Toko M.IQBAL', 'alamat': '', 'utama': True}, {'id': 'gudang', 'nama': 'Gudang belakang', 'alamat': 'belakang toko', 'utama': False}], 'pengantar': ['Ben', 'Gama']}, {'id': 'catatStok', 'tempoHari': 21, 'minKarung': 60, 'batasSelisih': 3, 'ambangSusutPositif': 250000}],
  'pindahStok': [{'id': 1301, 'pasangan': 1301, 'tipe': 'keluar', 'lokasi': 'toko', 'dari': 'toko', 'ke': 'gudang', 'merk': 'Angsa', 'kg': 200, 'pengantar': 'Ben', 'tanggal': '2026-09-11', 'jam': '09:00'}, {'id': 1302, 'pasangan': 1301, 'tipe': 'masuk', 'lokasi': 'gudang', 'dari': 'toko', 'ke': 'gudang', 'merk': 'Angsa', 'kg': 200, 'pengantar': 'Ben', 'tanggal': '2026-09-11', 'jam': '09:00'}],
  'persetujuan': [{'id': 'm1', 'dari': 'Ben', 'peran': 'ben', 'tindakan': 'nego', 'teks': 'Nego 1 karung Angsa', 'nominal': 630000, 'tanggal': '2026-09-19', 'jam': '09:12', 'status': 'menunggu', 'pada': '2026-09-19T02:12:00.000Z'},
                  {'id': 'm2', 'dari': 'Gama', 'peran': 'karyawan', 'tindakan': 'jualBon', 'teks': 'Bon Warung Sari', 'nominal': 260000, 'tanggal': '2026-09-19', 'jam': '09:05', 'status': 'menunggu', 'pada': '2026-09-19T02:05:00.000Z'},
                  {'id': 'm0', 'dari': 'Ben', 'peran': 'ben', 'tindakan': 'koreksi', 'teks': 'Koreksi nota lama', 'nominal': 0, 'tanggal': '2026-09-18', 'jam': '15:00', 'status': 'disetujui', 'diputusTanggal': '2026-09-18', 'pada': '2026-09-18T08:00:00.000Z'}],
  'pemasokCatatan': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var ANTRE = [{ koleksi: 'piutangMutasi', id: '999', ringkas: 'x', pada: '2026-09-19T02:50:00.000Z' }]; var LOKAL = { antre: ANTRE, idPerangkat: 'p-a1', lsKb: 4300, autoTanggal: null };
var J = function (x) { return JSON.stringify(x); };
// ---- PITA JAM (N9) & silang jam
var SL = mnSilangJam(); var sj = function (id) { return SL.find(function (k) { return k.id === id; }); };
ok('silang: nota meja = jam di nota TANPA karcis (306 dirinci tidak ikut): pagi 3 · tengah 2 · sore 4 dari 9; karcis 1 di tengah hari (jam disalin 13); harga 2 tulisan berjam di tengah hari (katalog karung tanpa cap waktu tidak dihitung); opname 2 di malam',
  J(sj('jual').sel) === '[0,3,2,4,0]' && sj('jual').n === 9 && J(sj('karcis').sel) === '[0,0,1,0,0]' && J(sj('harga').sel) === '[0,0,2,0,0]' && sj('harga').n === 2 && sj('harga').tot === 5 && J(sj('opname').sel) === '[0,0,0,0,2]', J(SL.map(function (k) { return k.id + ':' + J(k.sel); })));
var PT = susunPita(KINI);
ok('pita: jam 10 = Pagi; tujuh baris SELALU tujuh dan urutannya tetap (jual, karcis, tutup, belanja, bon, opname, harga) walau nol; jual 3 tulisan = 33,3% dari 9', PT.bagian.nama === 'Pagi' && PT.isi.length === 7 && J(PT.isi.map(function (b) { return b.id; })) === '["jual","karcis","tutup","belanja","bon","opname","harga"]' && PT.isi[0].angka === '3' && /33,3%/.test(PT.isi[0].sub) && PT.isi[2].angka === '0', J(PT.isi.map(function (b) { return b.id + '=' + b.angka; })));
ok('pita: ganti bagian ke Sore → jual 4 (PUNCAKNYA), buku bon 1 di urutan KELIMA (urutan tetap, bukan menurut jumlah); daftar bagian 5, yang sekarang Pagi', susunPita(KINI, 3).isi[0].angka === '4' && /PUNCAKNYA/.test(susunPita(KINI, 3).isi[0].sub) && susunPita(KINI, 3).isi[4].id === 'bon' && susunPita(KINI, 3).isi[4].angka === '1' && susunPita(KINI, 3).isi[1].id === 'karcis' && PT.daftarBagian.length === 5 && PT.daftarBagian[1].sekarang === true && PT.sekarang === 1, J(susunPita(KINI, 3).isi[0]));
ok('jam: mnJam membaca HH:MM, HH.MM, ISO (jam setempat) dan menolak sampah', mnJam('16:20') === 16 && mnJam('07.05') === 7 && mnJam('2026-09-17T13:15:00+07:00') === 13 && mnJam('') === null && mnJam('abc') === null && mnBagianDari(5) === 0 && mnBagianDari(23) === 4);
// ---- LACI (N1 + Sistem)
var LC = susunLaci(KINI, LOKAL); var br = function (id) { var r = null; LC.forEach(function (g) { g.isi.forEach(function (b) { if (b.id === id) r = b; }); }); return r; };
var UP = hitungUtangPemasok(); var totalUP = UP.reduce(function (a, x) { return a + x.totalUtang; }, 0);
ok('laci: tiga kelompok 3 · 4 · 5 baris (Buku besar, Alat toko, Toko ini + Lokasi & Pengingat)', LC.length === 3 && J(LC.map(function (g) { return g.isi.length; })) === '[3,4,5]', J(LC.map(function (g) { return g.id + ':' + g.isi.length; })));
ok('laci pemasok: angka = mesin beku (26 jt + 21 jt = 47 jt), 1 pemasok, 2 bon terbuka; bon 20 Agu lewat tempo 21 hari (tempo umum, kartu kosong) → AWAS, tujuan layar Harga & Pemasok → Bon', totalUP === 47000000 && br('pemasok').angka === 'Rp47.000.000' && /1 pemasok · 2 bon terbuka · 1 lewat tempo/.test(br('pemasok').sub) && br('pemasok').awas && br('pemasok').tujuan.ke === 'harga' && br('pemasok').tujuan.keluarga === 'bon', J(br('pemasok')) + ' ' + totalUP);
var PI = hitungPiutang().filter(function (x) { return x.sisa > 0; }); var totalPI = PI.reduce(function (a, x) { return a + x.sisa; }, 0);
ok('laci pelanggan: angka = mesin beku piutang; Pak Hartawan (2022, tanpa bayar) macet → AWAS; tujuan Pelanggan → Bon', br('pelanggan').angka === RP(totalPI) && /macet/.test(br('pelanggan').sub) && br('pelanggan').awas && br('pelanggan').tujuan.keluarga === 'bon', J(br('pelanggan')) + ' ' + totalPI);
ok('laci laporan: umur buku 48 hari sejak 3 Agu; sub menyebut laba bersih bulan ini; tujuan Laporan → Laba (putaran 19)', br('laporan').angka === '48 hari' && /catatan pertama 3 Agu 2026/.test(br('laporan').sub) && /laba bersih bulan ini/.test(br('laporan').sub) && br('laporan').tujuan.ke === 'laporan' && br('laporan').tujuan.keluarga === 'laba', J(br('laporan')));
ok('laci harga: 5 baris (karung 3 · kemasan 1 · literan 1); IR42 Select dijual 13.800 di bawah modal 14.000 → "1 merek karung di bawah modal", AWAS', br('harga').angka === '5 baris' && br('harga').cap === 'karung 3 · kemasan 1 · literan 1' && /1 merek karung di bawah modal/.test(br('harga').sub) && br('harga').awas, J(br('harga')));
ok('laci opname: 2 catatan, terakhir 2 Sep (17 hari) → AWAS (≥ 14 hari); 1 catatan lama tanpa kolom rupiah disebut; tujuan Stok → Cocokkan', br('opname').angka === '2 catatan' && /17 hari lalu/.test(br('opname').cap) && br('opname').awas && /1 catatan lama tanpa kolom rupiah/.test(br('opname').sub) && br('opname').tujuan.lembar === 'cocok', J(br('opname')));
ok('laci produksi: 1 adukan bulan ini; tutup buku: belum pernah (era kosong), tidak awas karena bukunya baru tahun ini', br('produksi').angka === '1 adukan' && br('tutupBuku').angka === 'belum pernah' && br('tutupBuku').awas === false && br('tutupBuku').tujuan.ke === 'uang' && br('tutupBuku').tujuan.keluarga === 'buku', J([br('produksi'), br('tutupBuku')]));
ok('laci perangkat: 2 perangkat (1 bernama · 1 belum), 1 berdenyut hari ini, 1 catatan perangkat ini belum sampai + 2 menunggu di perangkat lain → AWAS', br('perangkat').angka === '2 perangkat' && br('perangkat').cap === '1 bernama · 1 belum dinamai' && /1 berdenyut hari ini · 1 catatan perangkat ini belum sampai server · 2 menunggu di perangkat lain/.test(br('perangkat').sub) && br('perangkat').awas, J(br('perangkat')));
ok('laci peran: 2 permintaan menunggu owner → AWAS; cadangan terakhir 9 Sep (10 hari, lebih dari jadwal 7) → AWAS; lokasi 2, utama Toko; pengingat menyebut yang lewat', br('peran').angka === '2 menunggu' && br('peran').awas && br('cadangan').angka === '9 Sep 2026' && br('cadangan').awas && br('lokasi').angka === '2 lokasi' && br('lokasi').cap === 'utama: Toko M.IQBAL' && br('pengingat').awas && /lewat/.test(br('pengingat').cap), J([br('peran'), br('cadangan'), br('lokasi'), br('pengingat')]));
// ---- TANYA (N2)
var TQ = susunTanya(KINI); var tq = function (id) { return TQ.find(function (t) { return t.id === id; }); };
ok('tanya: sepuluh pertanyaan, semuanya punya angka & jawaban', TQ.length === 10 && TQ.every(function (t) { return t.angka && t.sub && t.tujuan && t.tujuan.teks; }), J(TQ.map(function (t) { return t.id + '=' + t.angka; })));
ok('tanya utang: angka = mesin, jawaban menyebut pemasok & bon lewat tempo; bon berikutnya = bon 20 Agu jatuh 10 Sep (sudah lewat 9 hari) — bukan bon yang jatuh 26 Sep', tq('utang').angka === 'Rp47.000.000' && /CV Padi Jaya Rp47.000.000/.test(tq('utang').sub) && /1 bon lewat tempo/.test(tq('utang').sub) && tq('jatuh').angka === '10 Sep 2026' && /sudah lewat 9 hari/.test(tq('jatuh').sub) && tq('jatuh').awas, J([tq('utang'), tq('jatuh')]));
// Paket F1 (owner 8 Okt 2026): bon lama BERGULIR (kartu pemasok "bon lama ikut kedatangan terakhir") — Menu & Pengingat memakai aturan yang sama dengan Bon pemasok
var LAMA_F1 = { koleksi: 'utangPemasokMutasi', data: { id: 9701, tipe: 'saldoAwal', pemasok: 'UD Beras Makmur', nominal: 5000000, tanggal: '2026-08-25', jam: '23:02', bonTanggal: '2026-07-01', catatan: 'bon lama bergulir (contoh)' } };
var KARTU_F1 = { koleksi: 'pemasokCatatan', data: { id: 'ud beras makmur', nama: 'UD Beras Makmur', kontak: '', catatan: '', orang: '', tempo: 0, bonLamaBergulir: true } };
var F1A = denganCacheSementara([LAMA_F1], function () { var T = susunTanya(KINI).find(function (t) { return t.id === 'utang'; }); var P = ssSumberPengingat(KINI, LOKAL).find(function (x) { return x.id === 'bon|9701'; }); return { utang: T.sub, p: P }; });
var F1B = denganCacheSementara([LAMA_F1, KARTU_F1], function () { var T = susunTanya(KINI).find(function (t) { return t.id === 'utang'; }); var P = ssSumberPengingat(KINI, LOKAL).find(function (x) { return x.id === 'bon|9701'; }); return { utang: T.sub, p: P }; });
ok('F1 Menu & Pengingat: bon lama 1 Jul (tempo umum 21) LEWAT → 2 bon lewat tempo, pengingat jatuh 22 Jul; kartu dicentang "ikut kedatangan terakhir" (UD Beras Makmur datang 1 Sep) → jatuh 22 Sep, tidak lewat, 1 bon lewat tempo, ket "bon lama bergulir"',
  /2 bon lewat tempo/.test(F1A.utang) && F1A.p && F1A.p.jatuh === '2026-07-22' && /1 bon lewat tempo/.test(F1B.utang) && F1B.p && F1B.p.jatuh === '2026-09-22' && /bon lama bergulir · ikut kedatangan 1 Sep/.test(F1B.p.ket), J([F1A, F1B]));
ok('tanya kas & kekayaan: titik kas belum disetel → "belum bisa dihitung" (tidak ditebak), dua-duanya', tq('kas').angka === 'belum bisa dihitung' && /Titik kas belum disetel/.test(tq('kas').sub) && tq('kaya').angka === 'belum bisa dihitung', J([tq('kas'), tq('kaya')]));
var LB = hitungLabaBersihRentang('2026-09-01', '2026-09-19');
ok('tanya laba: angka = laba bersih bulan ini dari mesin; jawaban menyebut margin kotor & biaya toko', tq('laba').angka === RP(LB.labaBersih) && /margin kotor/.test(tq('laba').sub) && /biaya toko/.test(tq('laba').sub), J(tq('laba')) + ' ' + LB.labaBersih);
// 39b no. 38 (owner 30 Sep): selisih laci tutup hari = baris lebih/kurang kas di laba — "Bulan ini toko untung berapa?" & laci Laporan memakai laba yang sama dengan Laporan
var TH38 = [{ koleksi: 'tutupHari', data: { id: '2026-09-15', tanggal: '2026-09-15', jam: '21:00', sistemBaru: true, selisih: 40000, selisihLaci: 40000, alasanSelisih: 'Ada penjualan belum dicatat' } }];
ok('39b-38 tanya laba & laci Laporan dengan LEBIH 40.000 (15 Sep): angka = laba mesin + 40.000; jawaban menyebut "± lebih/kurang kas Rp40.000"; tanpa selisih kalimatnya tidak menyebutnya',
  !/lebih\/kurang kas/.test(tq('laba').sub) && denganCacheSementara(TH38, function () { var t = susunTanya(KINI).find(function (x) { return x.id === 'laba'; }); var b = null; susunLaci(KINI, LOKAL).forEach(function (g) { g.isi.forEach(function (x) { if (x.id === 'laporan') b = x; }); });
    return t.angka === RP(LB.labaBersih + 40000) && /± lebih\/kurang kas Rp40\.000/.test(t.sub) && b.sub.indexOf('laba bersih bulan ini ' + RP(LB.labaBersih + 40000)) >= 0; }),
  J(denganCacheSementara(TH38, function () { return susunTanya(KINI).find(function (x) { return x.id === 'laba'; }); })));
ok('tanya piutang: angka = mesin; menyebut jumlah nama & macet; tanya lantai: merek paling tipis IR42 Select −Rp200/kg, 1 merek di bawah modal, AWAS', tq('piutang').angka === RP(totalPI) && /nama\./.test(tq('piutang').sub) && /macet/.test(tq('piutang').sub) && tq('lantai').angka === '−Rp200/kg' && /IR42 Select/.test(tq('lantai').sub) && /1 merek sudah berdiri di bawah modalnya/.test(tq('lantai').sub) && tq('lantai').awas, J([tq('piutang'), tq('lantai')]));
ok('tanya jam: margin 30 hari terbesar jam 16 (160.000 + 90.000 + 80.000 + 130.000 = 460.000 dari 4 baris), kedua jam 09 (90.000)', tq('jam').angka === '16:00' && /Rp460.000 dari 4 baris/.test(tq('jam').sub) && /Kedua: 09:00 \(Rp90.000\)/.test(tq('jam').sub), J(tq('jam')));
ok('tanya rak & saksi: merek dengan nilai rak terbesar disebut dengan persennya (desimal KOMA); QRIS 130.000 dari omzet semua nota 5.475.000 = 2,4% → AWAS (< 10%)', /\d,\d% nilai rak beras di Angsa/.test(tq('rak').sub) && tq('saksi').angka === '2,4%' && tq('saksi').awas && /Rp130.000 dari Rp5.475.000/.test(tq('saksi').sub), J([tq('rak'), tq('saksi')]));
// ---- 39b no. 4: kelebihan bayar pelanggan disebut di laci & jawaban (dulu disaring sisa > 0 dengan diam); angka bon tetap mesin
(function () {
  ok('39b-4 tanpa sisa negatif: laci & jawaban piutang tidak menyebut kelebihan bayar', !/kelebihan bayar/i.test(br('pelanggan').sub) && !/Kelebihan bayar/.test(tq('piutang').sub), J([br('pelanggan').sub, tq('piutang').sub]));
  var piu0 = cacheMentah('piutang').slice();
  pasok('piutangMutasi', piu0.concat([{ id: 691, tipe: 'saldoAwal', namaPelanggan: 'Bu Wati', nominal: 50000, tanggal: '2026-09-18', catatan: '', dicatatDi: 'sistem' }, { id: 692, tipe: 'bayar', namaPelanggan: 'Bu Wati', nominal: 80000, tanggal: '2026-09-19', jam: '09:00', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  var LC4 = susunLaci(KINI, LOKAL); var pl = null; LC4.forEach(function (g) { g.isi.forEach(function (b) { if (b.id === 'pelanggan') pl = b; }); }); var TQ4 = susunTanya(KINI); var tp = TQ4.find(function (t) { return t.id === 'piutang'; }), tk = TQ4.find(function (t) { return t.id === 'kaya'; });
  ok('39b-4 laci Pelanggan & piutang: sub menyebut " · kelebihan bayar Rp30.000", AWAS; angkanya TETAP piutang mesin (sisa > 0)', pl && / · kelebihan bayar Rp30\.000/.test(pl.sub) && pl.awas && pl.angka === RP(totalPI), J(pl));
  ok('39b-4 tanya piutang: "Kelebihan bayar pelanggan Rp30.000 (Bu Wati) — uang pelanggan dipegang toko.", AWAS; tanya kaya ikut AWAS', tp && / Kelebihan bayar pelanggan Rp30\.000 \(Bu Wati\) — uang pelanggan dipegang toko\.$/.test(tp.sub) && tp.awas && tp.angka === RP(totalPI) && tk && tk.awas, J([tp, tk]));
  var OR4 = susunMenurutOrang(KINI); var pb4 = (OR4.find(function (g) { return g.id === 'pembeli'; }) || { isi: [] }); var rw = pb4.isi.find(function (b) { return b.id === 'pl-bu wati'; });
  ok('39b-4 B3 menu Orang › Pembeli: baris "Bu Wati · kelebihan bayar Rp30.000 — uang pelanggan dipegang toko" AWAS menuju bukunya; ket menyebut "1 nama sisa bonnya di bawah nol"', rw && rw.sub === 'kelebihan bayar Rp30.000 — uang pelanggan dipegang toko' && rw.awas && rw.tujuan.keluarga === 'bon' && rw.tujuan.orang === 'bu wati' && / · 1 nama sisa bonnya di bawah nol$/.test(pb4.ket), J(pb4));
  var CR4 = susunCari(KINI, 'wati'); var cw = CR4.hasil.find(function (h) { return h.jenis === 'orang' && h.judul === 'Bu Wati'; });
  ok('39b-4 B3 cari "wati": sub "kelebihan bayar Rp30.000 · … kali datang"', cw && /^kelebihan bayar Rp30\.000 · \d+ kali datang$/.test(cw.sub), J(CR4.hasil));
  ok('39b-4 B4 tanya kaya: kalimat kelebihan bayar ADA juga saat kas belum terhitung ("begitu kas bisa dihitung …") atau saat terhitung ("kekayaan ini lebih besar …")', tk && (tk.angka === 'belum bisa dihitung' ? /Kelebihan bayar pelanggan Rp30\.000 belum dihitung sebagai kewajiban — begitu kas bisa dihitung, kekayaan akan terbaca lebih besar sebesar itu\.$/.test(tk.sub) : /Kelebihan bayar pelanggan Rp30\.000 belum dihitung sebagai kewajiban — kekayaan ini lebih besar sebesar itu\./.test(tk.sub)), J(tk));
  pasok('piutangMutasi', piu0.concat([{ id: 693, tipe: 'saldoAwal', namaPelanggan: 'Pak Yoga', nominal: 100000, tanggal: '2026-09-10', catatan: '', dicatatDi: 'sistem' }, { id: 694, tipe: 'hapusBuku', namaPelanggan: 'Pak Yoga', nominal: 100000, alasan: 'pindah', tanggal: '2026-09-18', dicatatDi: 'sistem' }, { id: 695, tipe: 'bayar', namaPelanggan: 'Pak Yoga', nominal: 100000, tanggal: '2026-09-19', jam: '09:10', caraBayar: 'Tunai', catatan: '', dicatatDi: 'kasir' }]));
  var tp5 = susunTanya(KINI).find(function (t) { return t.id === 'piutang'; }), tk5 = susunTanya(KINI).find(function (t) { return t.id === 'kaya'; });
  ok('39b-4 B1 hapus buku 100.000 lalu dibayar 100.000: jawaban piutang "Hapus buku yang ternyata dibayar Rp100.000 (Pak Yoga) — hapus bukunya perlu dibalik, bukan uang pelanggan." — BUKAN kelebihan bayar; kaya TIDAK menyebut kekayaan lebih besar', tp5 && / Hapus buku yang ternyata dibayar Rp100\.000 \(Pak Yoga\) — hapus bukunya perlu dibalik, bukan uang pelanggan\.$/.test(tp5.sub) && !/Kelebihan bayar/.test(tp5.sub) && !/Kelebihan bayar/.test(tk5.sub), J([tp5, tk5]));
  pasok('piutangMutasi', piu0);
})();
// ---- JAM (N5) · ORANG (N6) · TERTUTUP (N8)
var MJ = susunMenurutJam(KINI);
ok('menurut jam: lima laci, Pagi bertanda sekarang, isi diurut dari yang terbanyak (Pagi: jual 3 di atas)', MJ.length === 5 && MJ[1].sekarang && MJ[1].isi[0].id === 'jual-1' && MJ[1].isi[0].angka === '3' && MJ[1].isi.length === 7, J(MJ.map(function (g) { return g.nama + ':' + g.isi[0].id; })));
var MO = susunMenurutOrang(KINI); var mo = function (id) { return MO.find(function (g) { return g.id === id; }); };
ok('menurut orang: Ben (kasbon 500.000 belum kembali) berdiri di dua sisi buku; Gama lunas persis di Pegawai; pemasok CV Padi Jaya; pembeli terbesar Pak Darto → tujuan bonnya; penulis: Owner terbanyak, Ben 1 baris',
  mo('duaSisi') && mo('duaSisi').isi[0].judul === 'Ben' && mo('duaSisi').isi[0].angka === 'Rp500.000' && mo('pegawai').isi[0].judul === 'Gama' && mo('pemasok').isi[0].judul === 'CV Padi Jaya' && mo('pembeli').isi[0].judul === 'Pak Darto' && mo('pembeli').isi[0].tujuan.orang === 'pak darto' && mo('penulis').isi[0].judul === 'Owner' && mo('penulis').isi.some(function (b) { return b.judul === 'Ben' && b.angka === '1'; }), J(MO.map(function (g) { return g.id + ':' + g.isi.map(function (b) { return b.judul; }).join('/'); })));
var TT = susunTertutup(KINI)[0]; var tt = function (id) { return TT.isi.find(function (p) { return p.id === id; }); };
ok('tertutup: tutup buku T (era kosong) · bulan penuh T (catatan mulai 3 Agu, Agustus tidak utuh) · opname rupiah TERBUKA (1 dari 2 punya rupiah) · kartu pemasok T (nol) · hapus buku TERBUKA · telusur T; kepala "4 dari 6 pintu"',
  tt('tutupBuku').tertutup && tt('bulanPenuh').tertutup && !tt('opnameRupiah').tertutup && tt('kartuPemasok').tertutup && !tt('hapusBuku').tertutup && tt('telusur').tertutup && /^4 dari 6 pintu/.test(TT.ket), J(TT.isi.map(function (p) { return p.id + '=' + p.tertutup; })) + ' ' + TT.ket);
// ---- CARI
ok('cari: "angsa" → merek beras & kemasan; "bon" → layar; "darto" → orang (tujuan kartunya); satu huruf → tidak mencari', susunCari(KINI, 'angsa').hasil.some(function (r) { return r.jenis === 'merek' && r.judul === 'Angsa'; }) && susunCari(KINI, 'bon').hasil.some(function (r) { return r.jenis === 'layar'; }) && susunCari(KINI, 'darto').hasil.some(function (r) { return r.jenis === 'orang' && r.tujuan.orang === 'pak darto'; }) && susunCari(KINI, 'a').hasil.length === 0 && susunCari(KINI, 'zzzz').kosong, J(susunCari(KINI, 'angsa').hasil.map(function (r) { return r.jenis + ':' + r.judul; })));
// audit P2 (K5): laci itu bernama "Toko ini" (N1 dikunci, nama tidak diganti) — kata "sistem" (nama lamanya) tetap menemukannya di Menu
var CRs = susunCari(KINI, 'sistem'); var lacT = LC.filter(function (g) { return g.id === 'toko'; })[0];
ok('audit P2 · cari "sistem" → Perangkat & antrean, Peran & persetujuan, Cadangan & simpanan (laci Toko ini, tujuan layar Sistem); keterangan laci Toko ini menyebut sistem',
  ['Perangkat & antrean', 'Peran & persetujuan', 'Cadangan & simpanan'].every(function (n) { return CRs.hasil.some(function (r) { return r.jenis === 'layar' && r.judul === n && r.tujuan.ke === 'sistem'; }); })
  && !!lacT && lacT.nama === 'Toko ini' && /sistem/.test(lacT.ket), J([CRs.hasil.map(function (r) { return r.judul; }), lacT && lacT.ket]));
// ---- SS1 PERANGKAT & JEJAK
var PR = ssPerangkat(KINI, ANTRE, 'p-a1');
ok('perangkat: HP owner (denyut 5 menit lalu) HIDUP & perangkat ini; perangkat tanpa nama denyut kemarin tidak hidup, 2 antrean di sana; antrean perangkat ini 1, umur 10 menit (belum lama, batas 30)', PR.daftar[0].ini && PR.daftar[0].hidup && PR.daftar[0].menitLalu === 5 && PR.daftar[1].nama === '(belum dinamai)' && !PR.daftar[1].hidup && PR.lainAntre === 2 && PR.nAntre === 1 && PR.antre[0].lama === 10 && PR.antre[0].terlalu === false && PR.antre[0].nama === 'Buku bon', J(PR.daftar.map(function (d) { return d.nama + ':' + d.menitLalu + ':' + d.hidup; })) + ' ' + J(PR.antre));
ok('perangkat: antrean berumur 40 menit ditandai LAMA (batas 30 menit dari Atur)', ssPerangkat(KINI, [{ koleksi: 'penjualan', id: '1', pada: '2026-09-19T02:20:00.000Z' }], 'p-a1').antre[0].terlalu === true);
var JK = ssJejak(KINI, ANTRE, '');
ok('jejak: 3 tulisan, 2 hari ini; yang masih di antrean (piutangMutasi 999) BELUM sampai, nota 309 sampai; terbaru dulu; saring Ben → 1', JK.semua === 3 && JK.hariIni === 2 && JK.belumSampai === 1 && JK.tampil[0].id === '1103' && JK.tampil[0].sampai === false && JK.tampil[1].sampai === true && ssJejak(KINI, ANTRE, 'Ben').tampil.length === 1 && JK.perOrang[0].nama === 'Owner', J(JK.tampil.map(function (l) { return l.id + ':' + l.sampai + ':' + l.jam; })));
// ---- SS2 PERAN & PERSETUJUAN
var PN = ssPeran();
ok('peran: bawaan desain — Ben 8 sendiri · 3 minta owner · 3 tidak; karyawan 6 · 1 · 7 (nilai kisi tersimpan tetap); YANG DIGAMBAR = kebenaran server (23c): Ben 5 boleh · 2 tertutup server (hitung laci, kedatangan) · 3 · 3, karyawan 4 · 1 tertutup server (kedatangan) · 1 · 7; owner semua boleh',
  PN.peran[1].ket === '6 boleh sendiri · 2 tertutup server · 3 minta owner · 3 tidak boleh' && PN.peran[2].ket === '5 boleh sendiri · 1 tertutup server · 1 minta owner · 7 tidak boleh' && PN.hak('ben', 'hitungLaci') === 'sendiri' && PN.hak('karyawan', 'kedatangan') === 'sendiri' && PN.hak('owner', 'hapus') === 'sendiri' && PN.hak('karyawan', 'isiUlang') === 'sendiri', J(PN.peran));   // putaran 39: + isiUlang (rules v5) → Ben 8 sendiri, karyawan 6
var PH = susunPutarHak('ben', 'nego', W);
ok('putar hak: Ben nego "minta owner" → "tidak boleh" (putaran sendiri → owner → tidak), dokumen aturanToko/peran menyimpan jejaknya; hak owner DITOLAK', PH.dokumen && PH.dokumen[0].data.id === 'peran' && PH.dokumen[0].data.hak.ben.nego === 'tidak' && PH.dokumen[0].data.hak.karyawan.jualBon === 'owner' && PH.dokumen[0].data.jejak.length === 1 && /minta owner → tidak boleh/.test(PH.dokumen[0].data.jejak[0].teks) && !!susunPutarHak('owner', 'nego', W).tolak && /owner/i.test(susunAturSistem('peran', { hak: { owner: { nego: 'tidak' } } }, W).tolak || ''), J(PH));
pasok('aturanToko', KOTAK.aturanToko.concat([PH.dokumen[0].data])); var PH2 = susunPutarHak('ben', 'nego', W); ok('putar hak lagi: tidak boleh → boleh sendiri; jejak jadi 2', PH2.dokumen[0].data.hak.ben.nego === 'sendiri' && PH2.dokumen[0].data.jejak.length === 2, J(PH2)); pasok('aturanToko', KOTAK.aturanToko);
var PS = ssPersetujuan(KINI);
ok('persetujuan: 2 menunggu (terbaru dulu: m1 lalu m2), 1 riwayat; yang kecil (≤ 300.000) cuma m2; saran m2: karyawan bon = minta owner memang', PS.menunggu.length === 2 && PS.menunggu[0].id === 'm1' && PS.riwayat.length === 1 && PS.kecil === 1 && /memang minta owner/.test(PS.menunggu[1].saran), J(PS.menunggu.map(function (m) { return m.id + ':' + m.saran; })));
ok('putus: menolak tanpa alasan DITOLAK; menolak beralasan → status ditolak + alasan; menyetujui → disetujui; yang sudah diputus ditolak lagi', !!susunPutusPersetujuan('m1', false, '', W).tolak && susunPutusPersetujuan('m1', false, 'jatah habis', W).dokumen[0].data.status === 'ditolak' && susunPutusPersetujuan('m1', false, 'jatah habis', W).dokumen[0].data.alasanTolak === 'jatah habis' && susunPutusPersetujuan('m2', true, '', W).dokumen[0].data.status === 'disetujui' && !!susunPutusPersetujuan('m0', true, '', W).tolak);
// sanggahan rules 7 Okt: permintaan NEGO (m1) tidak pernah ikut setujui sekaligus — dilihat satu per satu, angkanya dihitung ulang owner (bukan nominal kiriman)
ok('setujui semua yang kecil: hanya m2 (260.000); m1 (nego) tetap menunggu — dilihat satu per satu', susunSetujuiKecil(W).dokumen.length === 1 && susunSetujuiKecil(W).dokumen[0].data.id === 'm2' && /1 permintaan nego dilihat satu per satu/.test(susunSetujuiKecil(W).patch.kabar), J(susunSetujuiKecil(W)));
// ---- SS3 CADANGAN
var BK = ssBerkasCadangan(KINI);
ok('berkas cadangan: versi 5 bentuk sistem lama + koleksi baru; penjualan 10, batchMasuk 3; jejak & denyut TIDAK ikut; era null; nama berkas bertanggal', BK.isi.versi === 5 && BK.isi.penjualan.length === 10 && BK.isi.batchMasuk.length === 3 && BK.isi.logAktivitas === undefined && BK.isi.perangkatStatus === undefined && BK.isi.eraTutupBuku === null && BK.nama === 'backup-batch-miqbal-2026-09-19.json' && BK.isi.pindahStok.length === 2, J(Object.keys(BK.isi)) + ' ' + BK.dokumen);
var CC = susunCatatCadangan(BK, 2048 * 1024, W, 'HP owner');
ok('catat cadangan: dokumen cadanganCatatan 2.048 KB, jumlah catatan = berkas, ok', CC.dokumen[0].koleksi === 'cadanganCatatan' && CC.dokumen[0].data.ukuranKb === 2048 && CC.dokumen[0].data.dokumen === BK.dokumen && CC.dokumen[0].data.ok === true && CC.dokumen[0].data.perangkat === 'HP owner', J(CC));
var CD = ssCadangan(KINI, LOKAL);
ok('cadangan: terakhir 9 Sep (10 hari, TELAT dari jadwal 7); kalender 14 hari, hari ini terakhir & aktif; kuota 4.300 dari 5.120 KB = 84% ≥ ambang 80 → AWAS; sisa ±13 hari', CD.terakhir.tanggal === '2026-09-09' && CD.umurHari === 10 && CD.telat && CD.kalender.length === 14 && CD.kalender[13].ini && CD.kalender[13].aktif && CD.kalender[3].keadaan === 'ok' && CD.kuota.pct === 84 && CD.kuota.awas && CD.kuota.sisaHari === 13, J(CD.kalender.map(function (k) { return k.tgl + k.keadaan; })) + ' ' + J(CD.kuota));
ok('cadangan: cap otomatis sistem lama hari ini ikut jadi cadangan (sumber sistem lama) → tidak telat; kuota tak terbaca → dikatakan', ssCadangan(KINI, { autoTanggal: '2026-09-19' }).umurHari === 0 && ssCadangan(KINI, { autoTanggal: '2026-09-19' }).terakhir.sumber === 'sistem lama' && !ssCadangan(KINI, { autoTanggal: '2026-09-19' }).telat && /tidak bisa dibaca/.test(ssCadangan(KINI, {}).kuota.teks));
// ---- SS4 LOKASI
var SLK = ssStokLokasi(); var stokK = hitungStokKarungPerMerk();
ok('stok per lokasi: Angsa buku = toko + gudang (200 kg pindah); semua merek menutup buku', Math.abs(SLK.Angsa.toko + SLK.Angsa.gudang - stokK.Angsa.sisaKg) < 0.01 && SLK.Angsa.gudang === 200 && Object.keys(SLK).every(function (m) { return Math.abs(Object.keys(SLK[m]).reduce(function (a, k) { return a + SLK[m][k]; }, 0) - stokK[m].sisaKg) < 0.01; }), J(SLK) + ' ' + stokK.Angsa.sisaKg);
var LP = ssLaporLokasi(KINI);
ok('laporan lokasi: nota 308 (lokasi gudang) masuk omzet gudang 1.380.000; nota tanpa lokasi di toko; perangkat HP owner di toko', LP.lapor[1].id === 'gudang' && LP.lapor[1].omzetBulan === 1380000 && LP.lapor[0].omzetBulan === 5475000 - 1380000 - 37500 - 0 && LP.lapor[0].perangkat.indexOf('HP owner') >= 0, J(LP.lapor.map(function (l) { return l.id + ':' + l.omzetBulan + ':' + l.kg; })));
ok('39b-19 omzet per lokasi = penjualan − uang retur lokasi itu: retur 50.000 di gudang (18 Sep) & 20.000 tanpa lokasi (= toko utama) mengurangi omzet bulan masing-masing',
  denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtLk1', tanggal: '2026-09-18', jam: '17:00', nominalRefund: 50000, kondisi: 'utuh', lokasi: 'gudang' } }, { koleksi: 'retur', data: { id: 'rtLk2', tanggal: '2026-09-18', jam: '17:05', nominalRefund: 20000, kondisi: 'utuh' } }],
    function () { var L2 = ssLaporLokasi(KINI); return L2.lapor[1].omzetBulan === LP.lapor[1].omzetBulan - 50000 && L2.lapor[0].omzetBulan === LP.lapor[0].omzetBulan - 20000; }),
  J(denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtLk1', tanggal: '2026-09-18', jam: '17:00', nominalRefund: 50000, kondisi: 'utuh', lokasi: 'gudang' } }], function () { return ssLaporLokasi(KINI).lapor.map(function (l) { return l.id + ':' + l.omzetBulan; }); })));
ok('39b-19 tinjauan v2: retur hari ini di toko senilai penjualannya → omzet hari Rp0 tapi nota hari ini tetap 1; notaBulan dihitung (dasar "belum ada" = ada-tidaknya nota, bukan nilai omzet)',
  denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtLk3', tanggal: '2026-09-19', jam: '09:30', nominalRefund: LP.lapor[0].omzetHari, kondisi: 'utuh' } }], function () { var L3 = ssLaporLokasi(KINI).lapor[0]; return LP.lapor[0].omzetHari > 0 && L3.omzetHari === 0 && L3.notaHari === LP.lapor[0].notaHari && L3.notaHari > 0 && L3.notaBulan > 0; }),
  J(denganCacheSementara([{ koleksi: 'retur', data: { id: 'rtLk3', tanggal: '2026-09-19', jam: '09:30', nominalRefund: LP.lapor[0].omzetHari, kondisi: 'utuh' } }], function () { var L3 = ssLaporLokasi(KINI).lapor[0]; return [L3.omzetHari, L3.notaHari, L3.notaBulan]; })));
ok('pindah stok: tanpa merek / kg / pengantar / melebihi stok DITOLAK menyebut sebabnya; sah → DUA dokumen (keluar di asal, masuk di tujuan) satu pasangan, buku tidak disentuh', /Pilih mereknya/.test(susunPindahStok('', 'toko', 'gudang', 10, 'Ben', W).tolak) && /Ketik berapa kg/.test(susunPindahStok('Angsa', 'toko', 'gudang', '', 'Ben', W).tolak) && /Siapa yang mengantar/.test(susunPindahStok('Angsa', 'toko', 'gudang', 10, 'Udin', W).tolak) && /Cuma ada/.test(susunPindahStok('Angsa', 'toko', 'gudang', 999999, 'Ben', W).tolak)
  && (function () { var r = susunPindahStok('Angsa', 'toko', 'gudang', 50, 'Ben', W); return r.dokumen && r.dokumen.length === 2 && r.dokumen[0].data.tipe === 'keluar' && r.dokumen[0].data.lokasi === 'toko' && r.dokumen[1].data.tipe === 'masuk' && r.dokumen[1].data.lokasi === 'gudang' && r.dokumen[1].data.pasangan === r.dokumen[0].data.id && r.dokumen.every(function (d) { return d.koleksi === 'pindahStok'; }); })(), J(susunPindahStok('Angsa', 'toko', 'gudang', 50, 'Ben', W)));
ok('jadikan utama: gudang → dokumen lokasi dengan tepat satu utama; utama sekarang ditolak', susunJadikanUtama('gudang', W).dokumen[0].data.daftar.filter(function (l) { return l.utama; }).length === 1 && susunJadikanUtama('gudang', W).dokumen[0].data.daftar[1].utama && !!susunJadikanUtama('toko', W).tolak);
ok('atur lokasi: dua utama DITOLAK; tanpa utama DITOLAK; menghapus gudang yang masih berisi 200 kg DITOLAK; nama kosong DITOLAK', /tepat satu/.test(susunAturSistem('lokasi', { daftar: [{ id: 'toko', nama: 'A', utama: true }, { id: 'gudang', nama: 'B', utama: true }] }, W).tolak) && /tepat satu/.test(susunAturSistem('lokasi', { daftar: [{ id: 'toko', nama: 'A', utama: false }] }, W).tolak) && /Masih ada 200 kg/.test(susunAturSistem('lokasi', { daftar: [{ id: 'toko', nama: 'Toko', utama: true }] }, W).tolak) && /belum bernama/.test(susunAturSistem('lokasi', { daftar: [{ id: 'toko', nama: '', utama: true }] }, W).tolak));
ok('atur perangkat: Owner tidak bisa dihapus dari pencatat; batas antrean 0 ditolak; sah → dokumen aturanToko/perangkat', /Owner tidak bisa dihapus/.test(susunAturSistem('perangkat', { pemegang: ['Ben'] }, W).tolak) && /batasAntre harus/.test(susunAturSistem('perangkat', { batasAntre: 0 }, W).tolak) && susunAturSistem('perangkat', { batasAntre: 45, pemegang: ['Owner', 'Ben', 'Hana'] }, W).dokumen[0].data.pemegang.length === 3);
// ---- SS5 PENGINGAT
var PG = ssPengingat(KINI, LOKAL); var pg = function (id) { return PG.sumber.find(function (p) { return p.id === id; }); };
ok('pengingat sumber: bon 401 jatuh 10 Sep (lewat 9) & bon 402 jatuh 26 Sep (7 hari lagi, di luar 3 hari sebelum → tidak aktif); janji Pak Darto lewat 2 hari; Mas Bimo (sudah bayar sesudah ditagih) TIDAK ada; kantong 5 kg cukup 6 hari (laju 10/hari) aktif; kantong 10 kg tanpa laju TIDAK ditebak',
  pg('bon|401') && pg('bon|401').sisa === -9 && pg('bon|402') && pg('bon|402').sisa === 7 && !PG.aktif.some(function (p) { return p.id === 'bon|402'; }) && pg('janji|pak darto|2026-09-17') && pg('janji|pak darto|2026-09-17').sisa === -2 && !PG.sumber.some(function (p) { return p.kunci === 'mas bimo'; }) && PG.sumber.some(function (p) { return p.jenis === 'kantong' && p.kunci === '5kg_kembangbmw' && p.sisa === 6; }) && !PG.sumber.some(function (p) { return p.kunci === '10kg_kembangbmw'; }), J(PG.sumber.map(function (p) { return p.id + ':' + p.sisa; })));
ok('pengingat keadaan: opname jatuh 16 Sep ditunda 2 hari → sisa −1 (masih lewat), tundaKali 1; cadangan 16 Sep SELESAI → tidak aktif; ringkas menyebut bon pemasok lewat Rp26.000.000', pg('opname|2026-09-16').sisa === -1 && pg('opname|2026-09-16').tundaKali === 1 && pg('cadangan|2026-09-16').selesai && !PG.aktif.some(function (p) { return p.jenis === 'cadangan'; }) && /bon pemasok lewat Rp26.000.000/.test(PG.ringkas) && PG.lewat.length === 3, J(PG.aktif.map(function (p) { return p.id + ':' + p.sisa; })) + ' ' + PG.ringkas);
ok('pengingat kalender: 14 hari (−3 … +10), hari ini di indeks 3 & bertanda; +6 punya 1 (kantong); hariDaftar hari ini kosong → judul "tidak ada"', PG.kalender.length === 14 && PG.kalender[3].ini && PG.kalender[9].n === 1 && /tidak ada/.test(PG.hariJudul), J(PG.kalender.map(function (k) { return k.h + '=' + k.n; })));
ok('selesai: yang lewat tanpa catatan DITOLAK; dengan catatan → dokumen pengingat status selesai; kabar bon menyebut pembayarannya dicatat di tempat lain', /butuh catatan/.test(susunSelesaiPengingat(pg('bon|401'), '', W).tolak) && susunSelesaiPengingat(pg('bon|401'), 'sudah dibayar 18 Sep', W).dokumen[0].data.status === 'selesai' && susunSelesaiPengingat(pg('bon|401'), 'sudah', W).dokumen[0].data.id === 'bon|401' && /bon pemasok/.test(susunSelesaiPengingat(pg('bon|401'), 'sudah', W).patch.kabar) && susunSelesaiPengingat(pg('bon|402'), '', W).dokumen !== undefined);
ok('tunda: bon 401 ditunda 2 hari (ke-1 dari 2); opname sudah ditunda 1 kali → ditunda lagi = terakhir; sesudah 2 kali DITOLAK', susunTundaPengingat(pg('bon|401'), W).dokumen[0].data.tundaHari === 2 && susunTundaPengingat(pg('bon|401'), W).dokumen[0].data.tundaKali === 1 && /tundaan terakhir/.test(susunTundaPengingat(pg('opname|2026-09-16'), W).patch.kabar) && !!susunTundaPengingat(Object.assign({}, pg('opname|2026-09-16'), { tundaKali: 2 }), W).tolak);
var WA = susunWaPengingat(KINI, pg('janji|pak darto|2026-09-17'), W, false);
ok('WA janji: url wa.me ke 62813… dengan kalimat tagihan yang sama; mencatat waTanggal; kedua kali sehari perlu YAKIN; bukan janji ditolak', /^https:\/\/wa\.me\/6281300002290\?text=/.test(WA.url) && /TOKO%20BERAS%20M\.IQBAL/.test(WA.url) && WA.dokumen[0].data.waTanggal === '2026-09-19' && susunWaPengingat(KINI, Object.assign({}, pg('janji|pak darto|2026-09-17'), { waHari: true }), W, false).perluYakin === true && !!susunWaPengingat(KINI, pg('bon|401'), W, false).tolak, J(WA));
ok('aturan pengingat: saklar bon → mati (dokumen nyala.bon=false), yang lewat tetap tercatat; penerima: melepas satu-satunya penerima DITOLAK, menambah Ben → 2', susunSaklarPengingat('bon', W).dokumen[0].data.nyala.bon === false && !!susunKePengingat('bon', 'Owner', W).tolak && J(susunKePengingat('bon', 'Ben', W).dokumen[0].data.ke.bon) === '["Owner","Ben"]' && susunKePengingat('bon', 'Ben', W).dokumen[0].data.ke.janji.length === 2);
pasok('aturanToko', KOTAK.aturanToko.concat([susunSaklarPengingat('bon', W).dokumen[0].data])); ok('pengingat jenis mati tidak lagi aktif (bon hilang dari aktif) tapi sumbernya tetap ada', !ssPengingat(KINI, LOKAL).aktif.some(function (p) { return p.jenis === 'bon'; }) && ssPengingat(KINI, LOKAL).sumber.some(function (p) { return p.jenis === 'bon'; })); pasok('aturanToko', KOTAK.aturanToko);
ok('atur pengingat: hariBon 99 ditolak; nyala tanpa penerima ditolak; sah menyimpan opnameTiap 7', /hariBon harus/.test(susunAturSistem('pengingat', { hariBon: 99 }, W).tolak) && /Minimal satu orang/.test(susunAturSistem('pengingat', { ke: { bon: [] } }, W).tolak) && susunAturSistem('pengingat', { opnameTiap: 7 }, W).dokumen[0].data.opnameTiap === 7);
// ---- putaran 24: pengingat PAJAK — sumbernya dari modul pajak (owner saja) lewat lokal.pajak; H-3 sebelum tanggal 15
var LP_PJ = Object.assign({}, LOKAL, { pajak: [{ id: 'pajak|2026-08', jenis: 'pajak', kunci: '2026-08', teks: 'Setor PPh final Agustus 2026', siapa: 'pajak', jatuh: '2026-09-21', n: 350000, ket: 'perkiraan' }] });
var PGP = ssPengingat(KINI, LP_PJ); var pp = PGP.sumber.find(function (p) { return p.id === 'pajak|2026-08'; });
ok('pengingat pajak: jenis baru "Setoran PPh final bulan lalu" (H-3, penerima Owner); jatuh 21 Sep = 2 hari lagi → aktif; tanpa lokal.pajak (bukan owner / sudah disetor) → tidak ada; jatuh 25 Sep (6 hari) → belum berbunyi',
  SS_JENIS_PENGINGAT.some(function (j) { return j.id === 'pajak' && j.kunci === 'hariPajak'; }) && ssAtur('pengingat').hariPajak === 3 && J(ssAtur('pengingat').ke.pajak) === '["Owner"]' && pp && pp.sisa === 2 && PGP.aktif.some(function (p) { return p.id === 'pajak|2026-08'; })
  && !ssPengingat(KINI, LOKAL).sumber.some(function (p) { return p.jenis === 'pajak'; }) && !ssPengingat(KINI, Object.assign({}, LOKAL, { pajak: [Object.assign({}, LP_PJ.pajak[0], { jatuh: '2026-09-25' })] })).aktif.some(function (p) { return p.jenis === 'pajak'; })
  && /hariPajak/.test(susunAturSistem('pengingat', { hariPajak: 30 }, W).tolak || ''), J(pp));
// ---- bentuk dokumen: semua yang ditulis punya id & koleksi yang dikenal koleksi.js
var semuaDok = [].concat(PH.dokumen, CC.dokumen, susunPindahStok('Angsa', 'toko', 'gudang', 50, 'Ben', W).dokumen, susunSelesaiPengingat(pg('bon|402'), '', W).dokumen, susunPutusPersetujuan('m2', true, '', W).dokumen, susunAturSistem('cadangan', { simpanHari: 60 }, W).dokumen);
ok('dokumen: semua punya id & koleksi yang ada di koleksi.js', semuaDok.every(function (d) { return d.data && d.data.id !== undefined && KOLEKSI.some(function (k) { return k.nama === d.koleksi; }); }), J(semuaDok.map(function (d) { return d.koleksi + ':' + d.data.id; })));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var LC = susunLaci(KINI, {}); var br = function (id) { var r = null; LC.forEach(function (g) { g.isi.forEach(function (b) { if (b.id === id) r = b; }); }); return r; };
var up = hitungUtangPemasok().reduce(function (a, x) { return a + x.totalUtang; }, 0); var pi = hitungPiutang().filter(function (x) { return x.sisa > 0; }).reduce(function (a, x) { return a + x.sisa; }, 0);
var PT = susunPita(KINI); var SL = mnSilangJam(); var jumlahPita = PT.isi.reduce(function (a, b) { return a + b.n; }, 0); var jumlahSilang = SL.reduce(function (a, k) { return a + k.sel[PT.terbuka]; }, 0);
var BK = ssBerkasCadangan(KINI); var hilang = Object.keys(CAD).filter(function (k) { return Array.isArray(CAD[k]) && !Array.isArray(BK.isi[k]); }); var beda = Object.keys(CAD).filter(function (k) { return Array.isArray(CAD[k]) && Array.isArray(BK.isi[k]) && BK.isi[k].length !== CAD[k].length; });
print(JSON.stringify({ laci: LC.map(function (g) { return g.isi.length; }), pemasokCocok: br('pemasok').angka === (up ? RP(up) : 'nihil'), pelangganCocok: br('pelanggan').angka === (pi ? RP(pi) : 'nihil'), tanya: susunTanya(KINI).length, tertutup: susunTertutup(KINI)[0].ket, pitaCocok: jumlahPita === jumlahSilang, pitaBagian: PT.bagian.nama,
  cariAngsa: susunCari(KINI, 'angsa').hasil.length, orang: susunMenurutOrang(KINI).length, hilang: hilang, beda: beda, koleksiBerkas: BK.koleksi, dokumenBerkas: BK.dokumen, pengingat: ssPengingat(KINI, {}).ringkas.replace(/Rp[\d.]+/g, 'Rp…') }));
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


def jalur_menu(ganti=None):
    """Audit P2 (K5): tiap jalur "Menu › …" di kode /baru/ (bukan komentar) menunjuk laci, baris & tab yang SUNGGUH ada — laci dari menu-logika.js, baris dari
    menu.js JUDUL_SISTEM, tab dari menu.js TAB_SISTEM (+ tombol "Atur"); "Sistem ›" (jalur lama yang tidak ada di layar) tidak boleh ada di kalimat layar.
    ganti = {berkas: teks} untuk kontrol. → daftar temuan."""
    import re
    baca = lambda f: (ganti or {}).get(f) if (ganti or {}).get(f) is not None else open(os.path.join(AKAR, f), encoding='utf-8').read()
    menu = baca('baru/js/layar/menu.js'); logika = baca('baru/js/layar/menu-logika.js'); out = []
    mj = re.search(r'const JUDUL_SISTEM = \{([^}]*)\}', menu); mt = re.search(r'const TAB_SISTEM = \{(.*?)\};', menu)
    if not mj or not mt: return ['menu.js: JUDUL_SISTEM / TAB_SISTEM tidak terbaca']
    judul = dict(re.findall(r"(\w+): '([^']+)'", mj.group(1)))
    tab = {k: [l for _, l in re.findall(r"\['(\w+)', '([^']+)'\]", v)] for k, v in re.findall(r"(\w+): \[((?:\['\w+', '[^']+'\](?:, )?)*)\]", mt.group(1))}
    laci = re.findall(r"\{ id: '\w+', nama: '([^']+)', ket:", logika)
    if 'Toko ini' not in laci or len(judul) < 5: return ['menu-logika.js / menu.js: laci "Toko ini" atau JUDUL_SISTEM tidak terbaca']
    n = 0
    for f in sorted(glob.glob(os.path.join(AKAR, 'baru', 'js', '**', '*.js'), recursive=True)):
        rel = os.path.relpath(f, AKAR); teks = baca(rel)
        for i, baris in enumerate(teks.split('\n'), 1):
            s = baris.strip()
            if s.startswith('//') or s.startswith('*') or s.startswith('/*'): continue
            kode = re.sub(r'\s//\s.*$', '', baris)
            if re.search(r'(^|[^›] )Sistem ›|Menu › Sistem', kode): out.append(rel + ':' + str(i) + ': jalur lama "Sistem ›" (laci itu bernama Toko ini)')
            for m in re.finditer(r'Menu › ([^\'"`()<.,;:\\]+)', kode):
                # nama laci / baris / tab harus PERSIS (satu-satunya kata sambung yang boleh menempel di ujung kalimat: "dulu")
                seg = [x.strip() for x in m.group(1).split(' › ')]; seg[-1] = re.sub(r' dulu$', '', seg[-1].split(' — ')[0].strip()); n += 1
                if seg[0] not in laci: out.append(rel + ':' + str(i) + ': laci "' + seg[0] + '" tidak ada di Menu'); continue
                if seg[0] != 'Toko ini' or len(seg) < 2: continue
                k = next((k for k, v in judul.items() if seg[1] == v), None)
                if k is None: out.append(rel + ':' + str(i) + ': baris "' + seg[1] + '" tidak ada di laci Toko ini'); continue
                if len(seg) > 2 and seg[2] not in tab.get(k, []) + ['Atur']: out.append(rel + ':' + str(i) + ': tab "' + seg[2] + '" tidak ada di ' + judul[k])
    if n < 10: out.append('jalur "Menu › …" yang terbaca cuma ' + str(n) + ' — pemeriksa tidak melihat kalimat layar (lulus kosong)')
    return out


def lokasi_belum_ada(teks=None):
    """39b-19 tinjauan v2: Menu › Lokasi — omzet Rp0 / minus karena retur tidak boleh ditulis "belum ada" kalau notanya ada (tiga keadaan kosong)."""
    t = teks if teks is not None else open(os.path.join(AKAR, 'baru/js/layar/menu.js'), encoding='utf-8').read(); g = []
    if "${l.notaHari || l.omzetHari ? RP(l.omzetHari) : 'belum ada'}" not in t: g.append('Lokasi: omzet hari ini Rp0 karena retur ditulis "belum ada" padahal ada nota')
    if "${l.notaBulan || l.omzetBulan ? RP(l.omzetBulan) : 'belum ada'}" not in t: g.append('Lokasi: omzet bulan ini Rp0 karena retur ditulis "belum ada" padahal ada nota')
    return g


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'audit P2: cari "sistem" tidak menemukan Perangkat & antrean': js.replace("sub: 'sistem · siapa memegang alat mana,", "sub: 'siapa memegang alat mana,"),
            '39b-19: omzet lokasi tidak mengurangi retur': js.replace("omzetHari: hariIni.reduce((a, p) => a + (p.hargaTotal || 0), 0) - uangR((t) => t === iso),", "omzetHari: hariIni.reduce((a, p) => a + (p.hargaTotal || 0), 0),").replace("omzetBulan: bulanIni.reduce((a, p) => a + (p.hargaTotal || 0), 0) - uangR((t) => t.slice(0, 7) === bulan),", "omzetBulan: bulanIni.reduce((a, p) => a + (p.hargaTotal || 0), 0),"),
            'no.4: laci Pelanggan diam soal kelebihan bayar': js.replace("(macet ? ' · ' + macet + ' macet' : '') + (LB.n ? ' · ' + ringkasLebih({ uang: LB.uang.jumlah, hapus: LB.hapus.jumlah }) : '')", "(macet ? ' · ' + macet + ' macet' : '')"),
            'no.4: jawaban piutang diam soal kelebihan bayar': js.replace("const kataLB = (LB.uang.n ?", "const kataLB = (false ?"),
            'no.4 B1: hapus buku terbayar tidak disebut di jawaban piutang': js.replace("+ (LB.hapus.n ? ' Hapus buku yang ternyata dibayar '", "+ (false ? ' Hapus buku yang ternyata dibayar '"),
            'no.4 B3: kelompok Pembeli diam soal sisa di bawah nol': js.replace("isi: LBo.orang.map((x) => baris('pl-' + x.kunci,", "isi: [].map((x) => baris('pl-' + x.kunci,"),
            'no.4 B3: cari nama tanpa kelebihan bayar': js.replace(": o.lebih > 0 ? ringkasLebih({ uang: o.lebihUang, hapus: o.lebihHapus }) + ' · ' : '') + o.kunjungan", ": '') + o.kunjungan"),
            'no.4 B4: kaya diam soal kelebihan bayar saat kas belum terhitung': js.replace("jadi kekayaannya pun belum.' + (LB.uang.n ?", "jadi kekayaannya pun belum.' + (false ?"),
            'pengingat pajak dari modul pajak diabaikan': js.replace("(lokal && Array.isArray(lokal.pajak) ? lokal.pajak : []).forEach(", "([]).forEach("),
            'pengingat pajak tanpa tenggang H-3 (bawaan 0)': js.replace("hariCadangan: 0, hariPajak: 3,", "hariCadangan: 0, hariPajak: 0,"),
            'F1 Menu: bon lama bergulir diramal dari tanggal bon asli': js.replace("const d = gulirBon(G, px.pemasok, b) || b.tanggal; bon.push(", "const d = b.tanggal; bon.push("),
            'F1 Pengingat: bon lama bergulir diramal dari tanggal bon asli': js.replace("const g = gulirBon(G, px.pemasok, b); const d = g || b.tanggal; if (!d", "const g = ''; const d = g || b.tanggal; if (!d"),
            'tempo bon pemasok tidak dipakai (jatuh = tanggal bon)': js.replace("jatuh: d && T.hari > 0 ? ssTambahHari(d, T.hari) : ''", "jatuh: d ? d : ''"),
            'baris pita berpindah tempat (diurut menurut jumlah)': js.replace("awas: false, tujuan: k.tujuan, n: k.sel[b] }));", "awas: false, tujuan: k.tujuan, n: k.sel[b] })).sort((p, q) => q.n - p.n);"),
            'nota karcis dihitung sebagai nota meja': js.replace("jual: (d) => (d.dirinciPada ? null : mnJam(d.jam))", "jual: (d) => mnJam(d.jam)"),
            'laci pemasok tidak menyala saat bon lewat tempo': js.replace("U.lewat.length > 0 || U.tekor > 0, { ke: 'harga', keluarga: 'bon'", "false, { ke: 'harga', keluarga: 'bon'"),
            'laci opname tidak menyala walau 14 hari tidak dicocokkan': js.replace("opUmur === null || opUmur >= 14, { ke: 'stok', lembar: 'cocok'", "false, { ke: 'stok', lembar: 'cocok'"),
            'kas ditebak walau titik kas belum disetel': js.replace("kas === null ? 'belum bisa dihitung' : RP(kas)", "RP(kas || 0)"),
            'kekayaan ditebak walau kas belum bisa dihitung': js.replace("N.total === null ? 'belum bisa dihitung' : RP(N.total)", "RP(N.total || 0)"),
            'merek di bawah modal tidak dihitung rugi': js.replace("rugi: tipis.filter((x) => x.untung < 0).length };", "rugi: 0 };"),
            'saksi menghitung semua cara bayar sebagai QRIS': js.replace("if (/qris/i.test(String(p.caraBayar || ''))) qris += p.hargaTotal || 0;", "qris += p.hargaTotal || 0;"),
            'pintu hapus buku dinyatakan tertutup': js.replace("pintu('hapusBuku', 'hapus', 'Hapus buku piutang mati', false,", "pintu('hapusBuku', 'hapus', 'Hapus buku piutang mati', true,"),
            'bulan penuh dihitung walau catatan mulai di tengah bulan': js.replace("if (awal >= pertama) bulanPenuh += 1;", "bulanPenuh += 1;"),
            'cari mengabaikan nama orang': js.replace("semuaOrang(kini).forEach((o) => { if (cocok(o.nama) || cocok(o.asli))", "[].forEach((o) => { if (cocok(o.nama) || cocok(o.asli))"),
            'perangkat dianggap hidup tanpa batas denyut': js.replace("hidup: menit !== null && menit <= A.batasDenyut,", "hidup: menit !== null,"),
            'antrean lama tidak ditandai': js.replace("terlalu: lama !== null && lama > A.batasAntre,", "terlalu: false,"),
            'jejak "sampai" walau masih di antrean': js.replace("sampai: !tunda.has((l.koleksi || '') + '|' + String(l.idDok || ''))", "sampai: true"),
            'hak owner bisa diubah (dua penjaga dilepas)': js.replace("if (peran === 'owner') return { tolak: 'Hak owner tidak diubah", "if (false) return { tolak: 'Hak owner tidak diubah").replace("if (p === 'owner' || !SS_HAK_BAWAAN[p]) { tolak = tolak || 'Hak owner tidak diubah — owner selalu boleh semuanya'; return; }", "if (!SS_HAK_BAWAAN[p]) { o.hak[p] = {}; }"),
            'menolak permintaan tanpa alasan diterima': js.replace("if (!setuju && ssKosong(alasan)) return { tolak:", "if (false) return { tolak:"),
            'setujui sekaligus melampaui batas': js.replace("const kecil = P.menunggu.filter((m) => m.sekaligus && m.n <= P.batas);", "const kecil = P.menunggu;"),
            'jejak & denyut ikut ke berkas cadangan': js.replace("if (SS_TAK_DICADANGKAN[k.nama]) return; isi[k.nama]", "isi[k.nama]"),
            'kuota tidak memperingatkan di atas ambang': js.replace("awas: pct !== null && pct >= A.ambangKuota, sisaHari", "awas: false, sisaHari"),
            '39b-19: nota hari ini dihitung dari omzet (retur penuh → nota 0)': js.replace("notaHari: new Set(hariIni.map((p) => p.grupNota || p.trxId || p.id)).size,", "notaHari: hariIni.reduce((a, p) => a + (p.hargaTotal || 0), 0) - uangR((t) => t === iso) > 0 ? 1 : 0,"),
            '39b-19: notaBulan hilang': js.replace(" notaBulan: new Set(bulanIni.map((p) => p.grupNota || p.trxId || p.id)).size,", ""),
            'pindah stok melebihi stok asal diterima': js.replace("if (n > ada + 0.005) return { tolak: 'Cuma ada '", "if (false) return { tolak: 'Cuma ada '"),
            'pindah stok cuma satu catatan (sisi masuk hilang)': js.replace(", { koleksi: 'pindahStok', data: Object.assign({ id: id + 1, tipe: 'masuk', lokasi: ke }, dasar) }", ""),
            'lokasi yang masih berisi stok bisa dihapus': js.replace("if (kg > 0.05) tolak = 'Masih ada '", "if (false) tolak = 'Masih ada '"),
            'dua lokasi utama diterima': js.replace("daftar.filter((l) => l.utama).length !== 1) tolak = 'Harus ada tepat satu", "daftar.filter((l) => l.utama).length < 1) tolak = 'Harus ada tepat satu"),
            'stok per lokasi tidak menutup buku (masuk & keluar sama tanda)': js.replace("(p.tipe === 'masuk' ? kg : -kg)", "kg"),
            'pengingat lewat selesai tanpa catatan': js.replace("if (p.sisa < 0 && ssKosong(catatan)) return { tolak:", "if (false) return { tolak:"),
            'tunda tanpa batas': js.replace("if (p.tundaKali >= A.maksTunda) return { tolak:", "if (false) return { tolak:"),
            'pengingat yang dimatikan tetap aktif': js.replace("const aktif = sumber.filter((p) => p.nyala && !p.selesai && p.sisa <= p.hariSebelum)", "const aktif = sumber.filter((p) => !p.selesai && p.sisa <= p.hariSebelum)"),
            'janji yang sudah dibayar sesudah ditagih tetap diingatkan': js.replace(" || (b.status !== 'menunggu' && b.status !== 'janjiLewat')) return;", ") return;"),
            'kantong tanpa laju ditebak': js.replace("const laju = (pakai[j] || 0) / 14; if (!(laju > 0)) return;", "const laju = (pakai[j] || 0) / 14 || 1;"),
            'WA kedua kali sehari tanpa ditanya': js.replace("if (p.waHari && !yakin) return { perluYakin: true,", "if (false) return { perluYakin: true,"),
            'Owner bisa dihapus dari daftar pencatat': js.replace("if (!tolak && !o.pemegang.some((x) => x.toLowerCase() === 'owner'))", "if (false)"),
            # ---- 39b no. 38 (owner 30 Sep): selisih laci = baris lebih/kurang kas di laba
            '39b-38: Menu memakai laba mesin (tanpa lebih/kurang kas)': js.replace("const laba = ugLabaBersih(mnAwalBulan(iso), iso);\n", "const laba = Object.assign(ugLabaBersih(mnAwalBulan(iso), iso), {}); laba.labaBersih = laba.labaMesin; laba.lebihKurangKas = 0;\n"),
            '39b-38: laci Laporan memakai laba mesin': js.replace("+ 1 : 0; const laba = ugLabaBersih(mnAwalBulan(iso), iso);", "+ 1 : 0; const laba = { labaBersih: ugLabaBersih(mnAwalBulan(iso), iso).labaMesin };"),
        }
        kode = 0
        # audit P2 (K5): pemeriksa jalur Menu berbunyi untuk jalur lama, baris yang diganti nama, dan tab yang tidak ada
        tb = open(os.path.join(AKAR, 'baru/js/layar/tutup-buku-logika.js'), encoding='utf-8').read(); mn = open(os.path.join(AKAR, 'baru/js/layar/menu.js'), encoding='utf-8').read()
        for nmK, gK in [('jalur lama "Menu › Sistem › Perangkat" kembali di kalimat tutup buku', {'baru/js/layar/tutup-buku-logika.js': tb.replace('(Menu › Toko ini › Perangkat & antrean › Antrean kirim)', '(Menu › Sistem › Perangkat)', 1)}),
                        ('baris "Perangkat & antrean" diganti nama di Menu tanpa kalimat layar ikut', {'baru/js/layar/menu.js': mn.replace("perangkat: 'Perangkat & antrean',", "perangkat: 'Perangkat',", 1)}),
                        ('tab "Antrean kirim" tidak ada lagi tapi kalimat layar menunjuknya', {'baru/js/layar/menu.js': mn.replace("['antrean', 'Antrean kirim']", "['antrean', 'Antrean']", 1)})]:
            basi = list(gK.values())[0] == open(os.path.join(AKAR, list(gK)[0]), encoding='utf-8').read()
            gJ = [] if basi else jalur_menu(gK)
            print(('KONTROL BASI  ' if basi else 'BERBUNYI ' if gJ else 'DIAM!!   ') + 'audit P2: ' + nmK + ' → ' + (gJ[0] if gJ else '-'))
            if basi or not gJ: kode = 3
        T = open(os.path.join(AKAR, 'baru/js/layar/menu.js'), encoding='utf-8').read(); Tr = T.replace("${l.notaHari || l.omzetHari ? RP(l.omzetHari) : 'belum ada'}", "${l.omzetHari ? RP(l.omzetHari) : 'belum ada'}", 1)
        gL = lokasi_belum_ada(Tr) if Tr != T else ['BASI']
        print(('BERBUNYI ' if gL and gL != ['BASI'] else 'DIAM!!   ') + '39b-19: Lokasi menulis "belum ada" untuk omzet Rp0 bernota → ' + (gL[0] if gL else '-'))
        if not gL or gL == ['BASI']: kode = 3
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    tL = lokasi_belum_ada(); g = g + ['39b-19: ' + x for x in tL]; l = l + (0 if tL else 1)
    tJ = jalur_menu(); g = g + ['audit P2 jalur Menu: ' + x for x in tJ]; l = l + (0 if tJ else 1)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8')); tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        h, e = jalan(kunci_jam(tgl + 'T20:00:00+07:00') + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s): laci %s · pemasok = mesin: %s · piutang = mesin: %s · tanya %d · %s · pita (%s) = silang: %s · cari "angsa" %d · orang %d kelompok · pengingat: %s'
                  % (os.path.basename(cad[-1]), h['laci'], h['pemasokCocok'], h['pelangganCocok'], h['tanya'], h['tertutup'], h['pitaBagian'], h['pitaCocok'], h['cariAngsa'], h['orang'], h['pengingat']))
            print('ASAP DATA TOKO: berkas cadangan sistem baru memuat %d koleksi · %d catatan · koleksi cadangan lama yang HILANG: %s · yang jumlahnya beda: %s' % (h['koleksiBerkas'], h['dokumenBerkas'], h['hilang'] or 'tidak ada', h['beda'] or 'tidak ada'))
            if not (h['pemasokCocok'] and h['pelangganCocok'] and h['pitaCocok'] and h['tanya'] == 10 and h['laci'] == [3, 4, 5]) or h['hilang'] or h['beda']: g.append('asap: angka layar tidak cocok dengan mesin / berkas cadangan tidak utuh')
    sys.exit(2 if g else 0)
