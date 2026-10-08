#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_stok_baru.py — uji logika layar STOK sistem baru (baru/js/layar/stok-logika.js) di jsc.
KOTAK PASIR (ANGKA CONTOH, bukan angka toko), jam dikunci 19 Sep 2026 10:00 WIB (laju 14 hari membaca Date.now).
Kalau ada backup-batch-*.json lokal: nilai stok layar = nilaiSack + nilaiBags mesin neraca untuk barang yang bersisa positif.

    python3 alat-uji/uji_stok_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_stok_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/nego-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/setengah-logika.js', 'baru/js/layar/stok-logika.js', 'baru/js/layar/varian-logika.js', 'baru/js/layar/stok-catat-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/stok-karantina-logika.js', 'baru/js/layar/stok-kantong-logika.js', 'baru/js/layar/stok-tempat-logika.js', 'baru/js/layar/stok-hpp-logika.js', 'baru/js/layar/kelas-merek-logika.js', 'baru/js/layar/struk-logika.js']   # putaran 30: + kelas-merek
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, merk, kg, jenis='karung', **k):
    d = {'id': id, 'tanggal': tgl, 'jam': k.pop('jam', '09:00'), 'caraBayar': 'Tunai', 'jenis': jenis, 'merkSumber': merk, 'totalKg': kg, 'hargaTotal': int(kg * 14000), 'hppTotalSaatJual': int(kg * 13000)}
    if jenis == 'karung': d.update({'beratKarungAcuan': 50, 'jumlahKarung': kg / 50})
    if jenis == 'literan': d.update({'jumlahLiter': round(kg / 0.82, 1)})
    d.update(k); return d


KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-08-20', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'subtotalHarga': 13000000, 'hargaPerKg': 13000},
      {'merk': 'IR64 Apex', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'subtotalHarga': 7000000, 'hargaPerKg': 14000},
      {'merk': 'Pandan Wangi', 'satuan': 'karung', 'beratKarung': 25, 'jumlahKarung': 8, 'totalKg': 200, 'subtotalHarga': 3200000, 'hargaPerKg': 16000}]},
    {'id': 'b2', 'tanggal': '2026-09-19', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [{'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 1350000, 'hargaPerKg': 13500}]}],
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-08-25', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 40, 'hppPerUnit': 66000, 'merkSumber': 'IR64 Apex', 'kgDipakai': 200}],
  'penjualan': [
    # Angsa: 14 hari terakhir terjual 700 kg → laju 50 kg/hari; sisa 1100 − 700 − 300 (lama) = 100 kg → habis 2 hari
    jual('a1', '2026-09-10', 'Angsa', 350), jual('a2', '2026-09-17', 'Angsa', 350), jual('a0', '2026-08-25', 'Angsa', 300),
    # IR64 Apex: laju 140/14 = 10 kg/hari; sisa 500 − 200 (adukan) − 140 = 160 kg → 16 hari (tidak perlu beli, tidak mandek)
    jual('x1', '2026-09-12', 'IR64 Apex', 140, jenis='literan'),
    # Pandan Wangi: tak ada gerak 14 hari → tidak terukur, modal diam
    jual('k1', '2026-09-15', None, 25, jenis='kemasan', namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=5),
    jual('h1', '2026-09-19', 'Angsa', 0, jenis='literan', jam='09:30') | {'jumlahLiter': 0, 'dibatalkan': True},
    jual('h2', '2026-09-19', 'IR64 Apex', 8.2, jenis='literan', jam='09:40'),
  ],
  'penyesuaianStok': [{'id': 'o1', 'tanggal': '2026-09-16', 'jam': '18:00', 'merk': 'Angsa', 'kgSistem': 110, 'kgFisik': 100, 'selisihKg': -10}, {'id': 'o2', 'tanggal': '2026-09-01', 'merk': 'IR64 Apex', 'kgSistem': 300, 'kgFisik': 300, 'selisihKg': 0}],
  'karantina': [{'id': 'q1', 'tanggal': '2026-09-18', 'asalRetur': True, 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 41.5, 'catatan': 'kualitas', 'statusTindakan': 'belum_diputuskan'},
                {'id': 'q2', 'tanggal': '2026-09-01', 'asalRetur': True, 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'catatan': 'x', 'statusTindakan': 'dibuang'}],
}
# ---- putaran 16 (ST4–ST6), ANGKA CONTOH — dipasok di blok ST4–ST6 saja supaya skenario lama tidak bergeser ----
KOTAK16 = {
  # kantong: 5 kg Kembang/BMW dibeli 2 batch (1.050 lalu 1.125 per lembar), 12 terpakai dalam 14 hari (laju 12/14 → sisa 488 = 569 hari);
  # 10 kg Putri Agri/Lele sisa 20, terpakai 60 dalam 14 hari (laju 4,29/hari → cukup 4,7 hari < 7 = AWAS); paper bag 10 L beli 900 lembar Rp355.500 (Rp395)
  'stokBahanKemasan': [{'id': 1001, 'tanggal': '2026-07-02', 'jenis': '5kg_kembangbmw', 'tipe': 'beli', 'jumlah': 300, 'hargaTotal': 315000},
                       {'id': 1002, 'tanggal': '2026-08-11', 'jenis': '5kg_kembangbmw', 'tipe': 'beli', 'jumlah': 200, 'hargaTotal': 225000},
                       {'id': 1003, 'tanggal': '2026-09-12', 'jenis': '5kg_kembangbmw', 'tipe': 'pakai', 'jumlah': 12, 'hargaTotal': 0},
                       {'id': 1004, 'tanggal': '2026-08-11', 'jenis': '10kg_putriagri_lele', 'tipe': 'beli', 'jumlah': 80, 'hargaTotal': 240000},
                       {'id': 1005, 'tanggal': '2026-09-10', 'jenis': '10kg_putriagri_lele', 'tipe': 'pakai', 'jumlah': 60, 'hargaTotal': 0}],
  'stokBahanLiteran': [{'id': 1101, 'tanggal': '2026-08-11', 'jenis': 'paperbag10l', 'tipe': 'beli', 'jumlah': 900, 'hargaTotal': 355500}],
  # harga jual per kg katalog karung: Angsa 13.400 (di atas modal 13.045 → untung), IR64 Apex 14.000 (= modal → margin Rp0 disengaja?), Pandan Wangi tidak ada
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 13400}, {'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerKg': 14000}],
  # peta tempat simpan sistem lama: Angsa di "rak depan" (tempat cuma teks); yang lain belum bertempat
  'pengaturan': [{'id': 'tempatSimpan', 'peta': {'K:Angsa': 'rak depan'}}],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var s = keadaanAwal();
var B = daftarBarang(); function brg(n) { return B.find(function (b) { return b.nama === n; }); }
ok('barang: Angsa sisa 90 kg (1100 − 1000 terjual − 10 susut cocokkan), laju 50 kg/hari (700 kg / 14 hari), habis 1,8 hari', brg('Angsa').sisa === 90 && brg('Angsa').laju === 50 && brg('Angsa').hariHabis === 1.8, JSON.stringify(brg('Angsa')));
ok('barang: nilai DI BUKU = modal rata-rata mesin (14.350.000 / 1.100 kg = 13.045,45) × sisa — sama dengan mesin; harga beli terbaru 13.500 dibawa sebagai pembanding', Math.abs(brg('Angsa').hpp - 14350000 / 1100) < 0.001 && brg('Angsa').hpp === hitungStokKarungPerMerk().Angsa.hppTerakhirPerKg && brg('Angsa').hargaTerbaru === 13500 && brg('Angsa').nilaiTerbaru === 90 * 13500, JSON.stringify([brg('Angsa').hpp, brg('Angsa').hargaTerbaru]));
ok('barang: baris yang dibatalkan tidak ikut laju; kemasan Kembang 5 kg sisa 35 unit', brg('Kembang 5 kg').sisa === 35 && brg('Kembang 5 kg').jenis === 'kemasan', JSON.stringify(brg('Kembang 5 kg')));
var G = susunGudang('beli', KINI);
ok('beli: Angsa habis 1,8 hari ≤ 7 → beli ceil((50×7 − 90)/50) = 6 karung 50 kg, ditandai AWAS (≤ 4 hari), urut dari yang paling cepat habis', G.jawab.baris[0].nama === 'Angsa' && G.jawab.baris[0].n === '6 karung' && G.jawab.baris[0].nKet === '50 kg' && G.jawab.baris[0].awas === true, JSON.stringify(G.jawab.baris));
ok('beli: IR64 Apex (±15 hari) TIDAK masuk daftar beli', !G.jawab.baris.some(function (x) { return x.nama === 'IR64 Apex'; }), JSON.stringify(G.jawab.baris.map(function (x) { return x.nama; })));
ok('beli: Pandan Wangi berisi tapi tak ada gerak 14 hari → DISEBUT tidak bisa dijawab (bukan dianggap aman)', /Pandan Wangi/.test(G.jawab.takTeks) && /lajunya belum bisa dihitung/.test(G.jawab.takTeks), G.jawab.takTeks);
ok('beli: kemasan yang menipis disuruh DIADUK, bukan dibeli', (function () { pasok('penjualan', cacheMentah('penjualan').concat([{ id: 'k9', tanggal: '2026-09-18', jam: '10:00', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 23, totalKg: 115, hargaTotal: 1, hppTotalSaatJual: 1 }])); var x = susunGudang('beli', KINI).jawab.baris.find(function (r) { return r.nama === 'Kembang 5 kg'; }); pasok('penjualan', cacheMentah('penjualan').filter(function (p) { return p.id !== 'k9'; })); return x && /^aduk \d+ unit$/.test(x.n); })());
G = susunGudang('modal', KINI);
var totalHarap = 90 * (14350000 / 1100) + brg('IR64 Apex').sisa * 14000 + 200 * 16000 + 35 * 66000; var totalBaruHarap = 90 * 13500 + brg('IR64 Apex').sisa * 14000 + 200 * 16000 + 35 * 66000;
ok('modal: total DI BUKU = Σ sisa × modal rata-rata; pembanding harga beli terbaru dihitung & DISEBUT di rumus; baris urut dari yang terbesar, persen ±100', Math.abs(G.jawab.total - totalHarap) < 0.01 && Math.abs(G.jawab.totalTerbaru - totalBaruHarap) < 0.01 && /HARGA BELI TERBARU/.test(G.jawab.rumus) && /Neraca sistem lama/.test(G.jawab.rumus) && G.jawab.baris[0].nama === 'Pandan Wangi' && Math.abs(G.jawab.baris.reduce(function (a, x) { return a + parseInt(x.nKet, 10); }, 0) - 100) <= 2, JSON.stringify([G.jawab.total, totalHarap, G.jawab.baris.map(function (x) { return x.nama + ':' + x.nKet; })]));
G = susunGudang('mandek', KINI);
ok('mandek: Pandan Wangi = tak ada gerak keluar 14 hari, "bukan nol, memang tidak terukur" (AWAS, paling atas); Kembang 5 kg cukup 98 hari (> 30); Angsa & Apex tidak mandek', G.jawab.baris.length === 2 && G.jawab.baris[0].nama === 'Pandan Wangi' && G.jawab.baris[0].awas && /tidak terukur/.test(G.jawab.baris[0].ket) && G.jawab.baris[1].nama === 'Kembang 5 kg' && /cukup untuk 98 hari/.test(G.jawab.baris[1].ket) && !G.jawab.baris[1].awas, JSON.stringify(G.jawab.baris));
G = susunGudang('cocok', KINI);
ok('cocok: Pandan Wangi & Kembang BELUM PERNAH dicocokkan (paling atas, awas); Apex 18 hari (awas); Angsa 3 hari (aman)', G.jawab.baris[0].n === 'belum pernah' && G.jawab.baris.find(function (x) { return x.nama === 'IR64 Apex'; }).n === '18 hari' && G.jawab.baris.find(function (x) { return x.nama === 'IR64 Apex'; }).awas && G.jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).n === '3 hari' && !G.jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).awas && G.kartu[3].a === '3 barang', JSON.stringify(G.jawab.baris.map(function (x) { return x.nama + ':' + x.n; })));
ok('kartu: pertanyaan tak dikenal jatuh ke "beli"; LIMA kartu dengan jawaban ringkasnya (kelima = "Berasnya ada di mana?", owner 21 Sep)', susunGudang('ngawur', KINI).aktif === 'beli' && G.kartu.length === 5 && G.kartu[0].a === '1 barang' && G.kartu[2].a === '2 barang' && G.kartu[4].id === 'lokasi' && /karung di tumpukan$/.test(G.kartu[4].a), JSON.stringify(G.kartu));
var LK0 = susunGudang('lokasi', KINI);
ok('lokasi: belum ada karung dibuka / wadah ditandai → semua beras di TUMPUKAN: Angsa 90 kg = 1 karung, IR64 Apex 3 karung, Pandan Wangi 200 kg = 8 karung @25 kg (nama yang cuma pernah masuk 25 kg dihitung per 25); kartu = jumlahnya; urut dari tumpukan terbesar', LK0.jawab.baris.length === 3 && LK0.jawab.baris[0].nama === 'Pandan Wangi' && LK0.jawab.baris[0].n === '8 karung' && LK0.jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).n === '1 karung' && LK0.jawab.baris.find(function (x) { return x.nama === 'IR64 Apex'; }).karung === 3 && LK0.kartu[4].a === '12 karung di tumpukan' && /perkiraan, ada yang belum ditandai/.test(LK0.jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).ket) && /karung terbuka \? \(belum ditandai\) · wadah \? \(belum ditandai\)/.test(LK0.jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).ket) && /semuanya di tumpukan/.test(LK0.jawab.baris[0].ket) === false && /Buka karung → tumpukan turun satu karung/.test(LK0.jawab.rumus), JSON.stringify(LK0.jawab.baris));
var K = susunKapur(KINI);
ok('papan kapur hari ini: barang masuk Angsa +100 kg (2 karung), terjual IR64 Apex −8,2 kg; baris dibatalkan & hari lain tidak ikut', K.baris.length === 2 && K.baris.some(function (x) { return /Barang masuk Angsa 2 karung/.test(x.isi) && x.n === '+100 kg' && x.jenis === 'masuk'; }) && K.baris.some(function (x) { return /Terjual IR64 Apex/.test(x.isi) && x.n === '−8,2 kg' && x.jenis === 'keluar'; }), JSON.stringify(K.baris));
var Q = susunKarantina(); ok('karantina: hanya yang BELUM diputuskan (41,5 kg Angsa); yang sudah dibuang tidak tampil', Q.baris.length === 1 && Q.totalKg === 41.5 && Q.baris[0].nama === 'Angsa', JSON.stringify(Q));
// ---- wadah & angka kebijakan yang diatur owner
var W0 = susunWadah(s); ok('wadah: bawaan delapan wadah BERPOSISI W1–W8, rata 50 kg · menggunung 60 kg · isi ulang ≤ 10 kg · takar 1,8 kg; isi wadah & karung di belakangnya semuanya belum ditandai (tidak ditebak)', W0.daftar.length === 8 && W0.daftar[0].no === 'W1' && W0.daftar[7].no === 'W8' && W0.atur.penuhKg === 50 && W0.atur.puncakKg === 60 && W0.atur.takarKg === 1.8 && W0.atur.isiUlangKg === 10 && W0.atur.dariOwner === false && W0.belumDitandai === 8 && W0.daftar.every(function (w) { return w.karung.diketahui === false; }) && W0.lain.length === 0, JSON.stringify(W0.atur));
var WW = { tanggal: '2026-09-19', jam: '09:00', idUnik: (function () { var n = 5000; return function () { n += 1; return n; }; })() };
ok('atur: rata 0 / isi ulang ≥ rata / daftar kosong DITOLAK', !!susunAturWadah({ penuhKg: '0', isiUlangKg: '5', daftar: ['A'] }, WW).tolak && !!susunAturWadah({ penuhKg: '40', isiUlangKg: '40', daftar: ['A'] }, WW).tolak && !!susunAturWadah({ penuhKg: '40', isiUlangKg: '5', daftar: [] }, WW).tolak);
// putaran 27: di kotak pasir ini "IR64 Apex" dipakai sebagai MEREK karung (barang masuk di bawah) — owner menandainya merek karung di Aturan wadah
var AT = susunAturWadah({ penuhKg: '60', puncakKg: '70', isiUlangKg: '15', takarKg: '1,8', merekKarung: ['Angsa', 'Perahu Layar', 'Pandan Wangi', 'IR64 Apex'], daftar: ['IR64 Apex', 'Angsa'] }, WW);
ok('atur: dokumen wadahLiteran bertipe atur {penuhKg 60, puncakKg 70, isiUlangKg 15, takarKg 1,8, daftar 2 berurut}', AT.dokumen[0].koleksi === 'wadahLiteran' && AT.dokumen[0].data.tipe === 'atur' && AT.dokumen[0].data.penuhKg === 60 && AT.dokumen[0].data.puncakKg === 70 && AT.dokumen[0].data.isiUlangKg === 15 && AT.dokumen[0].data.takarKg === 1.8 && AT.dokumen[0].data.daftar.join() === 'IR64 Apex,Angsa', JSON.stringify(AT.dokumen));
terapkanKeCache(AT.dokumen); var W1 = susunWadah(s);
ok('atur berlaku: tinggal dua wadah, posisi W1 = IR64 Apex (owner yang menyusun), rata 60 kg; Pandan Wangi bukan wadah lagi', W1.daftar.length === 2 && W1.daftar[0].no === 'W1' && W1.daftar[0].nama === 'IR64 Apex' && W1.atur.penuhKg === 60 && W1.atur.dariOwner === true && tinggiWadah('Pandan Wangi', s) === null);
terapkanKeCache(susunIsiUlangWadah('IR64 Apex', WW).dokumen);
var wa = susunWadah(s).daftar.find(function (w) { return w.nama === 'IR64 Apex'; });
ok('samakan 09:00 memakai angka owner (rata 60 kg); literan Apex 09:40 (8,2 kg) mengurangi → 51,8 kg; yang 12 Sep tidak', wa.diketahui && wa.sisaKg === 51.8 && wa.penuhKg === 60 && wa.perluIsi === false, JSON.stringify(wa));
terapkanKeCache(susunAturWadah({ penuhKg: '60', puncakKg: '70', isiUlangKg: '55', takarKg: '1,8', daftar: ['IR64 Apex', 'Angsa'] }, { tanggal: '2026-09-19', jam: '09:50', idUnik: WW.idUnik }).dokumen);
ok('ambang isi ulang dinaikkan owner ke 55 kg → wadah 51,8 kg kini MINTA isi ulang; papan kapur mencatat wadah disamakan', susunWadah(s).perluIsi === 1 && susunKapur(KINI).baris.some(function (x) { return x.jenis === 'wadah' && /Wadah IR64 Apex disamakan/.test(x.isi); }));
// ---- isi ulang takar demi takar: karung di belakang wadah turun; tumpukan gudang = buku − karung terbuka − isi wadah
var bukuApex = daftarBarang().find(function (b) { return b.nama === 'IR64 Apex' && b.jenis === 'karung'; }).sisa;
var lokSblm = susunGudang('lokasi', KINI); var modalSblm = susunGudang('modal', KINI).jawab.total;
terapkanKeCache(susunBukaKarung('IR64 Apex', { tanggal: '2026-09-19', jam: '09:55', idUnik: WW.idUnik }, 'IR64 Apex').dokumen);
ok('lokasi (inti permintaan owner 21 Sep): satu karung IR64 Apex dibuka di belakang wadahnya → di tab Gudang TUMPUKAN Apex turun 1 karung saat itu juga (kartu ikut turun 1), karung terbuka 50 kg; sisa/nilai di BUKU (empat pertanyaan lain) tidak berubah', (function () { var l = susunGudang('lokasi', KINI); var a0 = lokSblm.jawab.baris.find(function (x) { return x.nama === 'IR64 Apex'; }), a1 = l.jawab.baris.find(function (x) { return x.nama === 'IR64 Apex'; });
  return a0.karung - a1.karung === 1 && parseInt(lokSblm.kartu[4].a, 10) - parseInt(l.kartu[4].a, 10) === 1 && /karung terbuka 50 kg/.test(a1.ket) && daftarBarang().find(function (b) { return b.nama === 'IR64 Apex' && b.jenis === 'karung'; }).sisa === bukuApex && susunGudang('modal', KINI).jawab.total === modalSblm; })(), JSON.stringify(susunGudang('lokasi', KINI).jawab.baris));
var TK = susunTakarWadah('IR64 Apex', [{ merk: 'IR64 Apex', takar: 6 }, { merk: 'Angsa', takar: 3 }], { tanggal: '2026-09-19', jam: '10:00', idUnik: WW.idUnik }, s); terapkanKeCache(TK.dokumen);
var W2 = susunWadah(s); wa = W2.daftar.find(function (w) { return w.nama === 'IR64 Apex'; });
ok('9 takar campuran 6 : 3 (16,2 kg) → wadah 51,8 + 16,2 = 68 kg (di atas rata 60 → menggunung 0,8); karung Apex di belakang 50 − 10,8 = 39,2 kg; putaran 27 (owner 27 Sep, menggantikan pindah buku 22 Sep): BUKU Apex TIDAK berubah — 3 takar Angsa tercatat sebagai BAGIAN Angsa 5,4 kg di isi wadah Apex', wa.sisaKg === 68 && wa.gunung === 0.8 && wa.karung.sisaKg === 39.2 && Math.abs(daftarBarang().find(function (b) { return b.nama === 'IR64 Apex' && b.jenis === 'karung'; }).sisa - bukuApex) < 0.011 && Math.abs((wbKomposisi('IR64 Apex').bagian['Angsa'] || 0) - 5.4) < 0.011 && TK.dokumen.every(function (d) { return d.koleksi !== 'produksiKemasan'; }), JSON.stringify([wa.sisaKg, wa.gunung, wa.karung, wbKomposisi('IR64 Apex')]));
ok('tumpukan gudang Apex = buku − 39,2 (karung terbuka) − bagian Apex di wadah (68 − 5,4 bagian Angsa) — angkanya sama dengan model lama; layar tidak menambah pindah nama (0); lengkap karena keduanya sudah ditandai; tumpukan ANGSA = bukunya − 5,4 yang kini ada di wadah Apex', Math.abs(wa.tumpukan.kg - (bukuApex + 5.4 - 39.2 - 68)) < 0.011 && wa.tumpukan.pindahMasukKg === 0 && Math.abs(W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).tumpukan.kg - (brg('Angsa').sisa - 5.4)) < 0.011 && wa.karungNama === 'IR64 Apex' && wa.karungDicatat === true && wa.tumpukan.lengkap === true && wa.tumpukan.karung === Math.max(0, Math.floor((wa.tumpukan.kg + 0.0001) / 50)), JSON.stringify(wa.tumpukan));
ok('karung Angsa yang ikut dicampur belum pernah ditandai → TIDAK diketahui, dan tumpukan Angsa disebut "perkiraan belum lengkap"', W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).karung.diketahui === false && W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).tumpukan.lengkap === false);
var K2 = susunKapur(KINI);
ok('papan kapur: "diisi ulang 9 takar dari karung IR64 Apex 6 + Angsa 3" +16,2 kg (buku tetap milik merek karungnya — putaran 27, tanpa baris pindah nama) · "Karung IR64 Apex diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex" gudang −50 kg', K2.baris.some(function (x) { return x.jenis === 'wadah' && /Wadah IR64 Apex diisi ulang 9 takar dari karung IR64 Apex 6 \+ Angsa 3/.test(x.isi) && x.n === '+16,2 kg'; }) && K2.baris.some(function (x) { return /Karung IR64 Apex diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex/.test(x.isi) && x.n === 'gudang −50 kg'; }) && K2.baris.some(function (x) { return x.jenis === 'wadah' && /buku tetap milik merek karungnya/.test(x.isi); }) && !K2.baris.some(function (x) { return /Pindah nama di buku/.test(x.isi); }), JSON.stringify(K2.baris.filter(function (x) { return x.jenis === 'wadah'; })));
terapkanKeCache(susunAturWadah({ penuhKg: '60', puncakKg: '70', isiUlangKg: '55', takarKg: '1,8', daftar: ['IR64 Apex'], resep: { 'IR64 Apex': [{ merk: 'IR64 Apex', takar: 2 }, { merk: 'Kembang', takar: 1 }] } }, { tanggal: '2026-09-19', jam: '10:10', idUnik: WW.idUnik }).dokumen);
var W3 = susunWadah(s);
ok('Angsa dilepas dari daftar wadah + campuran bawaan Apex 2 : 1 dengan Kembang → "karung terbuka lain" memuat Angsa (pernah ditakar) & Kembang (ada di campuran)', W3.daftar.length === 1 && W3.daftar[0].resep.length === 2 && W3.lain.map(function (x) { return x.nama; }).join() === 'Angsa,Kembang', JSON.stringify(W3.lain.map(function (x) { return x.nama; })));
// ---- karung di belakang wadah BERNAMA (owner 21 Sep): karung Angsa dibuka di belakang wadah IR64 Apex
var lokA = susunGudang('lokasi', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).karung;
terapkanKeCache(susunBukaKarung('Angsa', { tanggal: '2026-09-19', jam: '10:20', idUnik: WW.idUnik }, 'IR64 Apex').dokumen);
var W4 = susunWadah(s); var w4 = W4.daftar[0];
ok('karung bernama: petak wadah IR64 Apex kini memegang KARUNG ANGSA (50 kg) dengan tumpukan ANGSA di gudang; karung Apex yang lama pindah ke "karung terbuka lain"; tumpukan Angsa di tab Gudang turun 1 karung', w4.nama === 'IR64 Apex' && w4.karungNama === 'Angsa' && w4.karungDicatat === true && w4.karung.sisaKg === 50 && w4.tumpukan.merk === 'Angsa' && W4.lain.some(function (x) { return x.nama === 'IR64 Apex' && x.karung.diketahui; }) && !W4.lain.some(function (x) { return x.nama === 'Angsa'; })
  && lokA - susunGudang('lokasi', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).karung === 1, JSON.stringify([w4.karungNama, w4.karung, W4.lain.map(function (x) { return x.nama; })]));
ok('karung bernama: papan kapur menyebut nama karung DAN wadahnya', susunKapur(KINI).baris.some(function (x) { return /Karung Angsa diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex/.test(x.isi); }));
// ---- PUTARAN 21 (owner 23 Sep): DERETAN karung terbuka di belakang deretan wadah; takar dari karung yang DIPILIH (bukan yang ditebak)
var DKR = deretanKarung();
ok('P21 deretan: urutan = karung yang dipegang W1 (IR64 Apex memegang karung Angsa ±50 kg) dulu, lalu karung Apex lama yang "dulu di belakang wadah IR64 Apex" (yatim, masih berisi)', DKR.length >= 2 && DKR[0].no === 'W1' && DKR[0].merk === 'Angsa' && DKR[0].lokasi === 'IR64 Apex' && DKR[0].sisaKg === 50 && DKR.some(function (k) { return k.merk === 'IR64 Apex' && k.lokasi === 'IR64 Apex' && /dulu di belakang/.test(k.letak); }), JSON.stringify(DKR.map(function (k) { return [k.no, k.merk, k.lokasi, k.sisaKg, k.letak]; })));
var apexLama = karungBelakang('IR64 Apex', 'IR64 Apex').sisaKg; var hYatim = hitungTakar('IR64 Apex', [{ merk: 'IR64 Apex', takar: 1, dari: 'IR64 Apex' }], s);
var TKD = susunTakarWadah('IR64 Apex', [{ merk: 'Angsa', takar: 1, dari: 'IR64 Apex' }], { tanggal: '2026-09-19', jam: '10:25', idUnik: WW.idUnik }, s); if (!TKD.tolak) terapkanKeCache(TKD.dokumen);
ok('P21 takar dari karung yang DIPILIH di deretan: dokumen takar menyimpan dari="IR64 Apex"; karung Angsa di belakang W1 turun 1,8 kg (50 → 48,2); memilih karung Apex LAMA (yatim, dulu di belakang wadah ini) menunjuk karung itu (' + apexLama + ' kg), bukan karung otomatis; wadah 68 → 69,8 kg', !TKD.tolak && TKD.dokumen.find(function (d) { return d.data.tipe === 'takar'; }).data.sumber.every(function (x) { return x.dari === 'IR64 Apex'; }) && karungBelakang('Angsa', 'IR64 Apex').sisaKg === 48.2 && hYatim.sumber[0].karung.lokasi === 'IR64 Apex' && hYatim.sumber[0].karung.yatim === true && Math.abs(hYatim.sumber[0].karung.sisaKg - apexLama) < 0.001 && susunWadah(s).daftar[0].sisaKg === 69.8, JSON.stringify([TKD.tolak, karungBelakang('Angsa', 'IR64 Apex').sisaKg, apexLama, hYatim.sumber[0].karung]));
// ---- PUTARAN 22: kembalikan karung terbuka ke tumpukan (owner: karung lepas / yatim bisa diatur, dihapus, dikembalikan)
var tgA0 = tumpukanGudang('IR64 Apex'); var kY = karungBelakang('IR64 Apex', 'IR64 Apex');
var KB1 = susunKembalikanKarung('IR64 Apex', 'IR64 Apex', WW, false);
ok('P22 kembalikan (karung Apex yatim, pernah ditakar): ketukan pertama DITANYA menyebut sisa & letak; ketukan kedua → karungIsi 0 bertanda dikembalikan + sisaSebelumKg; sesudahnya karung itu hilang dari deretan & "karung terbuka lain", tumpukan Apex NAIK persis sebesar sisanya; papan kapur menyebut "dikembalikan"', KB1.perluYakin === true && /dulu|di belakang wadah IR64 Apex/.test(KB1.tolak) && (function () { var R = susunKembalikanKarung('IR64 Apex', 'IR64 Apex', { tanggal: '2026-09-19', jam: '10:40', idUnik: WW.idUnik }, true); if (R.tolak) return false; var d = R.dokumen[0].data; terapkanKeCache(R.dokumen);
  var tg = tumpukanGudang('IR64 Apex'); return d.tipe === 'karungIsi' && d.isiKg === 0 && d.dikembalikan === true && Math.abs(d.sisaSebelumKg - kY.sisaKg) < 0.001 && d.wadah === 'IR64 Apex' && !deretanKarung().some(function (k) { return k.merk === 'IR64 Apex' && k.lokasi === 'IR64 Apex'; }) && !susunWadah(s).lain.some(function (x) { return x.nama === 'IR64 Apex' && x.lokasi === 'IR64 Apex'; }) && Math.abs(tg.kg - tgA0.kg - kY.sisaKg) < 0.011 && susunKapur(KINI).baris.some(function (x) { return /IR64 Apex dikembalikan ke tumpukan/.test(x.isi); }); })(), JSON.stringify([KB1.tolak, kY.sisaKg]));
var tgT0 = tumpukanGudang('Tawon' in hitungStokKarungPerMerk() ? 'Tawon' : 'Angsa');
terapkanKeCache(susunBukaKarung('Angsa', { tanggal: '2026-09-19', jam: '10:42', idUnik: WW.idUnik }, '').dokumen); var tgAn1 = tumpukanGudang('Angsa');
var KB2 = susunKembalikanKarung('Angsa', '', { tanggal: '2026-09-19', jam: '10:43', idUnik: WW.idUnik }, true);
ok('P22 kembalikan karung LEPAS yang baru dibuka & belum ditakar: catatan bukanya DIHAPUS (bukan ditulis 0) — tumpukan Angsa pulih persis 1 karung; belum ditandai → ditolak', !KB2.tolak && KB2.hapus.length === 1 && KB2.dokumen.length === 0 && (function () { terapkanKeCache(KB2.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); return Math.abs(tumpukanGudang('Angsa').kg - tgAn1.kg - 50) < 0.011; })() && /belum pernah ditandai/.test(susunKembalikanKarung('Kembang', '', WW, true).tolak), JSON.stringify(KB2));
ok('jumlahnya menutup untuk SEMUA nama: tumpukan + karung terbuka + isi wadah = buku − pindah keluar + pindah masuk', susunLokasi().every(function (t) { return Math.abs(t.kg + t.diBelakangKg + t.diWadahKg - (t.bukuKg - t.pindahKeluarKg + t.pindahMasukKg)) < 0.011; }), JSON.stringify(susunLokasi()));
terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 7001, tanggal: '2026-09-19', jam: '11:00', merk: 'Angsa', kgSistem: null, kgFisik: null, selisihKg: 41.5, alasan: 'Rework', dariRework: true } }]);
ok('tinjau 22 Sep: rework dari karantina (dariRework, kgFisik null) BUKAN hitungan gudang — Angsa tetap "3 hari sejak cocok", bukan 0', susunGudang('cocok', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).n === '3 hari', JSON.stringify(susunGudang('cocok', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; })));
terapkanKeCache([{ koleksi: 'penyesuaianStok', hapus: 7001 }]);
ok('Pandan Wangi cuma pernah masuk sebagai karung 25 kg → satu karungnya 25 kg (bukan 50)', beratKarungBuka('Pandan Wangi') === 25 && beratKarungBuka('Angsa') === 50 && susunBukaKarung('Pandan Wangi', WW, '').dokumen[0].data.kg === 25 && susunBukaKarung('Pandan Wangi', WW, '').dokumen[0].data.lepas === true);

// ==================== BARANG MASUK (ST1) — bentuk dokumen simpanKedatangan index.html ====================
var WM = { tanggal: '2026-09-19', jam: '15:00', idUnik: WW.idUnik };
ok('masuk: aturan bawaan = 60 karung · tempo 21 hari · selisih wajar 3 % · stok bertambah > 250.000 ditanya (angka sistem berjalan)', aturCatat().minKarung === 60 && aturCatat().tempoHari === 21 && aturCatat().batasSelisih === 3 && aturCatat().ambangSusutPositif === 250000 && aturCatat().dariOwner === false);
ok('masuk: calon pemasok dari kedatangan (terbaru dulu), calon nama beras dari buku', calonPemasok().join() === 'PEMASOK CONTOH' && calonMerkMasuk().indexOf('Angsa') === 0 && calonMerkMasuk().indexOf('Pandan Wangi') >= 0 && hargaSebelumnya('Angsa') === 13500, JSON.stringify([calonPemasok(), calonMerkMasuk()]));
var dm = drafMasukKosong(WM); dm.pemasok = 'PEMASOK CONTOH'; dm.caraBayar = 'utang'; dm.bongkar = '100.000';
dm.baris = [{ merk: 'Angsa', jumlahKarung: '40', beratKarung: 50, hargaPerKg: '13.200' }, { merk: 'IR64 Apex', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '14.100' }, barisMasukKosong()];
var hm = hitungMasuk(dm);
ok('masuk: 40×50 @13.200 + 20×50 @14.100 + bongkar 100.000 → 60 karung, 3.000 kg, beras 40.500.000; HPP Angsa 13.233,33 & Apex 14.133,33 (bongkar dibagi menurut kg — hitungHppMerkDalamBatch); baris kosong diabaikan; harga sebelumnya disebut', hm.karung === 60 && hm.kg === 3000 && hm.nilaiBeras === 40500000 && hm.total === 40600000 && Math.abs(hm.sah[0].hppPerKg - 13233.3333) < 0.01 && Math.abs(hm.sah[1].hppPerKg - 14133.3333) < 0.01 && hm.sah[0].alokasiBongkar === 66667 && hm.baris.length === 3 && !hm.bermasalah.length && hm.sah[0].hargaLalu === 13500, JSON.stringify(hm.sah));
ok('masuk: pemasok kosong DITOLAK; baris terisi tanpa harga DITOLAK dan menyebut barisnya; nama dua kali DITOLAK', /pemasok/.test(susunSimpanMasuk(Object.assign({}, dm, { pemasok: '' }), WM).tolak || '') && /Baris 2 \(IR64 Apex\): harga beli/.test(susunSimpanMasuk(Object.assign({}, dm, { baris: [dm.baris[0], { merk: 'IR64 Apex', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '' }] }), WM).tolak || '') && /dua kali/.test(susunSimpanMasuk(Object.assign({}, dm, { baris: [dm.baris[0], dm.baris[0]] }), WM).tolak || ''), JSON.stringify(susunSimpanMasuk(Object.assign({}, dm, { baris: [dm.baris[0], { merk: 'IR64 Apex', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '' }] }), WM)));
ok('tinjauan rantai laporan (no. 11): pemasok bernama sistem ("Lahir Buku", "Stok awal", "Tutup buku 2026") DITOLAK di Barang masuk — bonnya akan menggantung tanpa kartu pemasok; nama biasa tetap boleh',
  ['Lahir Buku', 'stok awal', 'TUTUP BUKU 2026'].every(function (n) { return /nama yang dipakai sistem/.test(susunSimpanMasuk(Object.assign({}, dm, { pemasok: n }), WM).tolak || ''); }) && !/nama yang dipakai sistem/.test(susunSimpanMasuk(dm, WM).tolak || ''));
var dmKecil = Object.assign({}, dm, { baris: [{ merk: 'Angsa', jumlahKarung: '5', beratKarung: 50, hargaPerKg: '13.200' }] });
ok('masuk: 5 karung (< 60) DITANYA dulu (perluYakin), ketukan kedua boleh', susunSimpanMasuk(dmKecil, WM).perluYakin === true && /Cuma 5 karung/.test(susunSimpanMasuk(dmKecil, WM).tolak) && !susunSimpanMasuk(dmKecil, WM, true).tolak);
var SM = susunSimpanMasuk(dm, WM); var dokM = SM.dokumen[0].data;
ok('masuk: SATU dokumen batchMasuk {tanggal, jam, pemasok, biayaBongkar, caraBayar utang, merkList[{id, merk, satuan karung, jumlahKarung, beratKarung, totalKg, hargaPerKg, subtotalHarga}]} — kolom persis sistem berjalan', SM.dokumen.length === 1 && SM.dokumen[0].koleksi === 'batchMasuk' && dokM.pemasok === 'PEMASOK CONTOH' && dokM.caraBayar === 'utang' && dokM.biayaBongkar === 100000 && dokM.tanggal === '2026-09-19' && dokM.merkList.length === 2 && Object.keys(dokM.merkList[0]).sort().join() === 'beratKarung,hargaPerKg,id,jumlahKarung,merk,satuan,subtotalHarga,totalKg' && dokM.merkList[0].subtotalHarga === 26400000 && dokM.merkList[0].totalKg === 2000 && dokM.merkList[0].id === '1' && /jadi bon pemasok · jatuh tempo 21 hari/.test(SM.patch.kabar), JSON.stringify(dokM));
var bkM = hitungStokKarungPerMerk(); terapkanKeCache(SM.dokumen); var bkM2 = hitungStokKarungPerMerk();
ok('masuk: sesudah dicatat, buku Angsa +2.000 kg; Apex +1.000 kg; BON pemasok 40.500.000 (beras saja, bongkar tunai) tercatat di utang pemasok', Math.abs(bkM2['Angsa'].sisaKg - bkM['Angsa'].sisaKg - 2000) < 0.011 && Math.abs(bkM2['IR64 Apex'].sisaKg - bkM['IR64 Apex'].sisaKg - 1000) < 0.011 && (hitungUtangPemasok().find(function (x) { return x.pemasok === 'PEMASOK CONTOH'; }) || { bon: [] }).bon.some(function (b) { return String(b.id) === String(dokM.id) && b.nilai === 40500000; }), JSON.stringify(hitungUtangPemasok().find(function (x) { return x.pemasok === 'PEMASOK CONTOH'; })));
var buku = daftarKedatangan(10);
ok('masuk: buku kedatangan terbaru dulu; kedatangan tadi paling atas (60 karung · 3.000 kg · utang); stok awal tidak ada di kotak pasir ini', buku[0].id === dokM.id && buku[0].karung === 60 && buku[0].kg === 3000 && buku[0].cara === 'utang' && buku[0].nilai === 40600000 && buku.length === 3, JSON.stringify(buku.map(function (b) { return b.pemasok + ':' + b.karung + ':' + b.cara; })));
var dk = drafDariKedatangan(dokM.id); dk.baris[0].hargaPerKg = '13.000'; dk.alasan = '';
ok('masuk: KOREKSI tanpa alasan DITOLAK; dengan alasan → dokumen dengan id yang SAMA (menimpa), alasanKoreksi & riwayat tercatat; harga baru berlaku di buku', /alasan/.test(susunSimpanMasuk(dk, { tanggal: '2026-09-19', jam: '15:10', idUnik: WW.idUnik }).tolak || '') && (function () { dk.alasan = 'salah ketik harga'; var K = susunSimpanMasuk(dk, { tanggal: '2026-09-19', jam: '15:10', idUnik: WW.idUnik }); if (K.tolak) return false; terapkanKeCache(K.dokumen);
  var d = K.dokumen[0].data; return d.id === dokM.id && d.alasanKoreksi === 'salah ketik harga' && d.riwayat.length === 1 && /dikoreksi/.test(d.riwayat[0].teks) && d.jam === '15:00' && ambilSemuaBatch().find(function (b) { return String(b.id) === String(dokM.id); }).merkList[0].hargaPerKg === 13000 && ambilSemuaBatch().filter(function (b) { return String(b.id) === String(dokM.id); }).length === 1; })());
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'fondasi1', tanggal: '2026-08-08', pemasok: 'stok awal', stokAwal: true, caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: '1', merk: 'Angsa', satuan: 'karung', jumlahKarung: 1, beratKarung: 50, totalKg: 50, hargaPerKg: 12000, subtotalHarga: 600000 }] } }]);
ok('masuk: batch FONDASI (stok awal) tidak bisa dikoreksi maupun dihapus; hapus tanpa alasan DITOLAK', /fondasi/i.test(susunSimpanMasuk(Object.assign(drafDariKedatangan('fondasi1'), { alasan: 'x' }), WM).tolak || '') && /fondasi/i.test(susunHapusKedatangan('fondasi1', 'x', WM).tolak || '') && /alasan/.test(susunHapusKedatangan(dokM.id, '', WM).tolak || ''));
terapkanKeCache([{ koleksi: 'batchMasuk', hapus: 'fondasi1' }]);
terapkanKeCache([{ koleksi: 'produksiKemasan', data: { id: 'bj1', tanggal: '2026-09-19', namaProduk: 'Angsa', ukuranKemasan: 5, jumlahUnit: 10, hppPerUnit: 70000, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true, dariBatch: dokM.id } }]);
var HK = susunHapusKedatangan(dokM.id, 'mobil dicatat dua kali', { tanggal: '2026-09-19', jam: '15:20', idUnik: WW.idUnik });
ok('masuk: HAPUS beralasan → batch + pasangan beli-jadi (dariBatch) dicabut bersama, jejak ke bukuHapus {koleksi, idDok, pemasok, ringkas, alasan, pasangan 1}', !HK.tolak && HK.hapus.length === 2 && HK.hapus[0].koleksi === 'batchMasuk' && HK.hapus[1].koleksi === 'produksiKemasan' && HK.hapus[1].id === 'bj1' && HK.dokumen[0].koleksi === 'bukuHapus' && HK.dokumen[0].data.idDok === String(dokM.id) && HK.dokumen[0].data.alasan === 'mobil dicatat dua kali' && HK.dokumen[0].data.pasangan === 1 && /pasangannya/.test(HK.patch.kabar), JSON.stringify(HK));
terapkanKeCache(HK.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; }).concat(HK.dokumen));
ok('masuk: sesudah dihapus, buku Angsa kembali seperti sebelum kedatangan; buku hapus memuatnya', Math.abs(hitungStokKarungPerMerk()['Angsa'].sisaKg - bkM['Angsa'].sisaKg) < 0.011 && bukuHapus(5).length === 1 && bukuHapus(5)[0].idDok === String(dokM.id), JSON.stringify(bukuHapus(5)));
var AC = susunAturCatat({ minKarung: '30', tempoHari: '14', batasSelisih: '5', ambangSusutPositif: '' }, WM);
ok('masuk: aturan owner disimpan ke aturanToko/catatStok (id tetap) dan BERLAKU: 40 karung kini tidak ditanya; angka mustahil ditolak', !AC.tolak && AC.dokumen[0].koleksi === 'aturanToko' && AC.dokumen[0].data.id === 'catatStok' && AC.dokumen[0].data.ambangSusutPositif === 250000 && (function () { terapkanKeCache(AC.dokumen); return aturCatat().minKarung === 30 && aturCatat().dariOwner === true && !susunSimpanMasuk(Object.assign({}, dm, { baris: [{ merk: 'Angsa', jumlahKarung: '40', beratKarung: 50, hargaPerKg: '13.200' }] }), WM).tolak && /0–100/.test(susunAturCatat({ batasSelisih: '150' }, WM).tolak || ''); })());
terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'catatStok' }]);

// ==================== audit 39b no. 2: KEDATANGAN BON YANG SUDAH DIBAYAR ====================
// pembayaran bon menempel lewat bonId + nama pemasok persis; mesin beku mengalirkan yang yatim ke bon tertua → dijaga di susunSimpanMasuk & susunHapusKedatangan.
// Yang MENGUNCI = uang yang ditujukan ke bon (pembayaran bertunjuk); aliran tanpa tujuan (FIFO lama, kelebihan bayar) tidak mengunci (tinjauan 30 Sep).
var W2 = { tanggal: '2026-09-19', jam: '16:00', idUnik: WW.idUnik }; var W2b = { tanggal: '2026-09-22', jam: '09:00', idUnik: WW.idUnik };
var masuk2 = function (pem, cara) { var d = drafMasukKosong(W2); d.pemasok = pem; d.caraBayar = cara; d.baris = [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '13.000' }]; var r = susunSimpanMasuk(d, W2, true); terapkanKeCache(r.dokumen || []); return r; };
var bayar2 = function (id, pem, n, bonId, tgl) { var d = { id: id, tipe: 'bayar', pemasok: pem, nominal: n, tanggal: tgl || '2026-09-21', jam: '10:00' }; if (bonId) { d.bonId = String(bonId); d.bonTanggal = '2026-09-19'; } terapkanKeCache([{ koleksi: 'utangPemasokMutasi', data: d }]); };
var S2 = masuk2('PEMASOK BON UJI', 'utang'); var id2 = S2.dokumen[0].data.id;
bayar2('bb2', 'PEMASOK BON UJI', 38000000, id2); bayar2('bb2x', 'PEMASOK LAIN', 1000000, id2);   // umpan: pemasok lain yang menunjuk bon ini TIDAK dipasang mesin ke bon ini
var BB2 = ckBayarBonId(id2);
ok('39b-2: ckBayarBon: bon 39.000.000 (60 × 50 × 13.000), dibayar 38.000.000 lewat pembayaran bertunjuk 21 Sep; pembayaran pemasok lain yang menunjuk bon ini tidak dihitung; mesin setuju', !S2.tolak && BB2.nilai === 39000000 && BB2.dibayar === 38000000 && BB2.dibayarMesin === 38000000 && BB2.bayar.length === 1 && BB2.bayarPertama === '2026-09-21', JSON.stringify(BB2));
var kor2 = function (ubah, id) { var x = drafDariKedatangan(id || id2); x.alasan = 'uji'; ubah(x); return susunSimpanMasuk(x, W2b, true); };
var T2 = { tunai: kor2(function (x) { x.caraBayar = 'tunai'; }).tolak || '', pem: kor2(function (x) { x.pemasok = 'PEMASOK LAIN'; }).tolak || '', tgl: kor2(function (x) { x.tanggal = '2026-09-22'; }).tolak || '', tglMaju: kor2(function (x) { x.tanggal = '2026-09-18'; }).tolak || '', nilai: kor2(function (x) { x.baris[0].jumlahKarung = '58'; }).tolak || '' };
ok('39b-2: koreksi bon yang sudah dibayar DITOLAK bila jadi tunai / pemasok lain / tanggal datang diubah (mundur MAUPUN maju) / nilai beras di bawah yang dibayar — kalimatnya menyebut 38.000.000 & tanggal bayar', /jadi tunai/.test(T2.tunai) && /dua kali/.test(T2.tunai) && /nama pemasoknya tidak bisa diganti/.test(T2.pem) && /tanggal datangnya \(19 Sep/.test(T2.tgl) && /tanggal datangnya \(19 Sep/.test(T2.tglMaju) && /lebih kecil; kelebihan Rp300\.000/.test(T2.nilai) && [T2.tunai, T2.pem, T2.tgl, T2.tglMaju, T2.nilai].every(function (t) { return /sudah dibayar Rp38\.000\.000 \(21 Sep/.test(t); }), JSON.stringify(T2));
ok('39b-2: koreksi yang aman TETAP boleh: harga turun tapi nilai ≥ dibayar (12.700 → 38.100.000), ejaan "pemasok bon uji" dibaca PEMASOK BON UJI (ejaan pembayarannya)', !kor2(function (x) { x.baris[0].hargaPerKg = '12.700'; }).tolak && (function () { var r = kor2(function (x) { x.pemasok = 'pemasok bon uji'; }); return !r.tolak && r.dokumen[0].data.pemasok === 'PEMASOK BON UJI'; })());
var H2 = susunHapusKedatangan(id2, 'uji', W2b);
ok('39b-2: HAPUS kedatangan yang sudah dibayar DITOLAK (menyebut 38.000.000)', /tidak bisa dihapus/.test(H2.tolak || '') && /Rp38\.000\.000/.test(H2.tolak || '') && !H2.hapus, JSON.stringify(H2));
var HP2 = susunKoreksiHpp('Angsa', '12.500', 'uji HPP', W2b, true); var NK2 = nilaiKoreksi('Angsa', '12.500');
ok('39b-2: koreksi HPP menolak LEBIH DULU (kartu, pratinjau, massal) dengan nama berasnya: kedatangan terakhir Angsa = bon yang sudah dibayar, 12.500 → 37.500.000 di bawah yang dibayar; harga naik tetap boleh', /^Angsa: kedatangan terakhirnya .*sudah dibayar Rp38\.000\.000/.test(HP2.tolak || '') && /^Angsa: kedatangan terakhirnya/.test(NK2.tolak || '') && !nilaiKoreksi('Angsa', '13.300').tolak && /Angsa: kedatangan terakhirnya/.test(susunKoreksiMassal({ Angsa: '12.500' }, 'uji', W2b).tolak || ''), JSON.stringify([HP2.tolak, NK2.tolak]).slice(0, 300));
var K2 = kor2(function (x) { x.baris[0].hargaPerKg = '12.700'; }); terapkanKeCache(K2.dokumen || []);
var bonPC = function (pem, id) { var px = hitungUtangPemasok().find(function (p) { return p.pemasok === pem; }); return { px: px, bon: px ? px.bon.find(function (b) { return b.id === String(id); }) : null }; };
ok('39b-2: sesudah koreksi aman diterapkan, pembayaran tetap di bonnya: dibayar 38.000.000, sisa bon 100.000, tanpa kelebihan bayar', !K2.tolak && (function () { var q = bonPC('PEMASOK BON UJI', id2); return q.bon && q.bon.sisa === 100000 && !(q.px.tekor > 0) && ckBayarBonId(id2).dibayar === 38000000; })(), JSON.stringify(bonPC('PEMASOK BON UJI', id2)));
// aliran TANPA tujuan (pembayaran lama tanpa bonId) → dibayarMesin naik, tetapi TIDAK menambah kunci
bayar2('bb2f', 'PEMASOK BON UJI', 50000, null);
ok('39b-2: pembayaran tanpa bonId yang mengalir ke bon ini (FIFO mesin): dibayarMesin 38.050.000, kunci tetap 38.000.000 (uang tanpa tujuan tidak mengunci)', ckBayarBonId(id2).dibayarMesin === 38050000 && ckBayarBonId(id2).dibayar === 38000000 && bonPC('PEMASOK BON UJI', id2).bon.sisa === 50000, JSON.stringify(ckBayarBonId(id2)));
// bon LUNAS PENUH (tidak lagi tampil di mesin) tetap terkunci
bayar2('bb2g', 'PEMASOK BON UJI', 50000, id2);
ok('39b-2: bon LUNAS PENUH (hilang dari hitungUtangPemasok): dibayar 38.050.000 bertunjuk, dibayarMesin = nilai 38.100.000; hapus & jadi tunai tetap DITOLAK', !bonPC('PEMASOK BON UJI', id2).bon && ckBayarBonId(id2).dibayar === 38050000 && ckBayarBonId(id2).dibayarMesin === 38100000 && /tidak bisa dihapus/.test(susunHapusKedatangan(id2, 'uji', W2b).tolak || '') && /jadi tunai/.test(kor2(function (x) { x.caraBayar = 'tunai'; }).tolak || ''), JSON.stringify(ckBayarBonId(id2)));
// KELEBIHAN BAYAR yang terserap kedatangan salah catat: tidak mengunci — kedatangan itu tetap bisa dihapus (kelebihan bayar kembali seperti semula)
var ST1 = masuk2('PEMASOK TEKOR', 'utang'); var idT1 = ST1.dokumen[0].data.id; bayar2('bt1', 'PEMASOK TEKOR', 39000000, idT1); bayar2('bt2', 'PEMASOK TEKOR', 5000000, null);
var tekorAwal = (bonPC('PEMASOK TEKOR', idT1).px || {}).tekor || 0;
var ST2 = masuk2('PEMASOK TEKOR', 'utang'); var idT2 = ST2.dokumen[0].data.id;
ok('39b-2: kedatangan salah catat yang MENYERAP kelebihan bayar 5.000.000 (dibayarMesin 5.000.000, tanpa pembayaran bertunjuk) tetap bisa DIHAPUS tetapi tanggalnya terkunci (urutan FIFO & neraca per tanggal); bon yang dibayar bertunjuk tetap terkunci', tekorAwal === 5000000 && ckBayarBonId(idT2).dibayarMesin === 5000000 && ckBayarBonId(idT2).dibayar === 0 && !susunHapusKedatangan(idT2, 'salah catat', W2b).tolak && /tidak bisa dihapus/.test(susunHapusKedatangan(idT1, 'uji', W2b).tolak || '') && /sudah terbayar Rp5\.000\.000 menurut buku bon/.test(kor2(function (x) { x.tanggal = '2026-09-25'; }, idT2).tolak || ''), JSON.stringify([tekorAwal, ckBayarBonId(idT2), kor2(function (x) { x.tanggal = '2026-09-25'; }, idT2).tolak]));
// koreksi HPP MASSAL dua nama di SATU kedatangan berbayar: lolos per nama, ditolak BERSAMA dengan nama berasnya (tinjauan 30 Sep)
var dM = drafMasukKosong(W2); dM.pemasok = 'PEMASOK MASSAL'; dM.caraBayar = 'utang'; dM.baris = [{ merk: 'Angsa', jumlahKarung: '30', beratKarung: 50, hargaPerKg: '13.000' }, { merk: 'IR64 Apex', jumlahKarung: '30', beratKarung: 50, hargaPerKg: '14.000' }];
var SM2 = susunSimpanMasuk(dM, W2, true); terapkanKeCache(SM2.dokumen || []); var idM = SM2.dokumen[0].data.id; bayar2('bm1', 'PEMASOK MASSAL', 40000000, idM);
var PM2 = pratinjauMassal({ 'Angsa': '12.800', 'IR64 Apex': '13.800' }); var KM2 = susunKoreksiMassal({ 'Angsa': '12.800', 'IR64 Apex': '13.800' }, 'uji massal', W2b);
ok('39b-2: koreksi HPP MASSAL dua nama di satu kedatangan berbayar (40.500.000, dibayar 40.000.000): masing-masing lolos sendiri (40.200.000), BERSAMA 39.900.000 → pratinjau & terapkan menolak dengan nama berasnya; nama beras tidak tercetak dua kali', !SM2.tolak && !nilaiKoreksi('Angsa', '12.800').tolak && !nilaiKoreksi('IR64 Apex', '13.800').tolak && !PM2.siap && PM2.bermasalah.length === 2 && /^Angsa \+ IR64 Apex: kedatangan terakhirnya sama/.test(PM2.bermasalah[0].tolak) && /Angsa \+ IR64 Apex: kedatangan terakhirnya sama .*Rp39\.900\.000/.test(KM2.tolak || '') && !/Angsa: Angsa:/.test(susunKoreksiMassal({ Angsa: '12.500' }, 'uji', W2b).tolak || '') && /^Angsa: kedatangan terakhirnya/.test(susunKoreksiMassal({ Angsa: '12.500' }, 'uji', W2b).tolak || ''), JSON.stringify([PM2.bermasalah.map(function (b) { return b.tolak; }), KM2.tolak]).slice(0, 500));
// kedatangan BERBARIS BAL yang sudah dibayar: baris bal ikut tertulis apa adanya (audit 39b no. 30) — bon tertulis = karung draf + bal lama
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'bal2', tanggal: '2026-09-19', jam: '08:30', pemasok: 'PEMASOK BAL', caraBayar: 'utang', biayaBongkar: 0, merkList: [{ id: '1', merk: 'Angsa', satuan: 'karung', jumlahKarung: 10, beratKarung: 50, totalKg: 500, hargaPerKg: 13000, subtotalHarga: 6500000 }, { id: '2', merk: 'Kemasan Contoh', bentuk: 'bal', jumlahBal: 2, totalKg: 0, hargaPerKg: 0, subtotalHarga: 1000000 }] } }]);
bayar2('bbal', 'PEMASOK BAL', 7000000, 'bal2');
var kb = kor2(function (x) { x.baris[0].hargaPerKg = '13.100'; }, 'bal2'); var kb2 = kor2(function (x) { x.baris[0].hargaPerKg = '11.000'; }, 'bal2');
ok('39b-2: kedatangan berbaris bal yang sudah dibayar 7.000.000: koreksi harga NAIK boleh (karung 6.550.000 + bal 1.000.000 = 7.550.000); TURUN ke 11.000 DITOLAK dengan bon yang memuat bal (5.500.000 + 1.000.000 = 6.500.000, kelebihan 500.000)', !kb.tolak && /nilai bon sesudah koreksi Rp6\.500\.000 lebih kecil; kelebihan Rp500\.000/.test(kb2.tolak || '') && ckBayarBonId('bal2').dibayar === 7000000 && ckBayarBonId('bal2').nilai === 7500000, JSON.stringify([kb.tolak, kb2.tolak, ckBayarBonId('bal2')]).slice(0, 400));
// ejaan pemasok: kedatangan BARU → ejaan yang sudah dipakai; pemasok baru apa adanya; koreksi ejaan kedatangan tunggal (tanpa dokumen lain) boleh
var d3 = drafMasukKosong(W2); d3.pemasok = '  pemasok   contoh '; d3.caraBayar = 'tunai'; d3.baris = [{ merk: 'Angsa', jumlahKarung: '60', beratKarung: 50, hargaPerKg: '13.000' }]; var S3 = susunSimpanMasuk(d3, W2, true);
var S4 = masuk2('Pemasok Tunggal', 'tunai');
var k4 = drafDariKedatangan(S4.dokumen[0].data.id); k4.pemasok = 'PEMASOK TUNGGAL'; k4.alasan = 'ejaan'; var S4k = susunSimpanMasuk(k4, W2b, true);
ok('39b-2: kedatangan BARU "  pemasok   contoh " ditulis sebagai PEMASOK CONTOH (satu ejaan di mesin) & kabarnya menyebut; pemasok baru apa adanya; koreksi ejaan kedatangan yang satu-satunya boleh (Pemasok Tunggal → PEMASOK TUNGGAL)', !S3.tolak && S3.dokumen[0].data.pemasok === 'PEMASOK CONTOH' && /ejaan yang sudah dipakai/.test(S3.patch.kabar) && ckEjaanPemasok('PEMASOK BARU SEKALI') === 'PEMASOK BARU SEKALI' && ckEjaanPemasok('PEMASOK CONTOH') === 'PEMASOK CONTOH' && !S4k.tolak && S4k.dokumen[0].data.pemasok === 'PEMASOK TUNGGAL', JSON.stringify([S3.dokumen && S3.dokumen[0].data.pemasok, S4k.tolak, S4k.dokumen && S4k.dokumen[0].data.pemasok]));
ok('39b-2: kedatangan TUNAI dan bon yang belum dibayar: dibayar 0 dan hapusnya tetap boleh', ckBayarBon(S4.dokumen[0].data).dibayar === 0 && !susunHapusKedatangan(S4.dokumen[0].data.id, 'uji', W2b).tolak);
terapkanKeCache(['bb2', 'bb2x', 'bb2f', 'bb2g', 'bt1', 'bt2', 'bm1', 'bbal'].map(function (x) { return { koleksi: 'utangPemasokMutasi', hapus: x }; }).concat([id2, idT1, idT2, idM, 'bal2', S4.dokumen[0].data.id].map(function (x) { return { koleksi: 'batchMasuk', hapus: x }; })));

// ==================== audit 39b no. 30: KOREKSI KEDATANGAN BERBARIS BAL ====================
// Baris BAL (beli jadi, sistem lama index.html bacaBarisMerk) tidak diubah dari Barang masuk / Stok › HPP — saat kedatangannya dikoreksi baris itu WAJIB
// ikut tertulis apa adanya: nilainya bagian bon (atau belanja tunai), dan porsi bongkarnya sudah masuk modal per bag pasangan beli-jadi (dariBatch).
var W30 = { tanggal: '2026-09-19', jam: '16:30', idUnik: WW.idUnik };
var BAL30 = { id: '2', merk: 'Kembang', satuan: 'bal', bentuk: 'bal', ukuranBag: 5, jumlahBal: 10, isiPerBal: 4, jumlahPcs: 40, totalKg: 200, hargaPerBal: 280000, hargaPerKg: 14000, subtotalHarga: 2800000 };
var batch30 = { id: 'bal30', tanggal: '2026-09-19', jam: '08:40', pemasok: 'PEMASOK BAL30', caraBayar: 'utang', biayaBongkar: 170000, merkList: [
  { id: '1', merk: 'Rojolele Bal Uji', satuan: 'karung', jumlahKarung: 20, beratKarung: 50, totalKg: 1000, hargaPerKg: 13000, subtotalHarga: 13000000 }, BAL30,
  { id: '3', merk: 'Rojolele Bal Dua', satuan: 'karung', jumlahKarung: 10, beratKarung: 50, totalKg: 500, hargaPerKg: 13000, subtotalHarga: 6500000 }] };
terapkanKeCache([{ koleksi: 'batchMasuk', data: batch30 }, { koleksi: 'produksiKemasan', data: { id: 'bj30', tanggal: '2026-09-19', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 40, hppPerUnit: 70500, merkSumber: 'BELI JADI', kgDipakai: 0, beliJadi: true, dariBatch: 'bal30' } }]);
var bon30 = function () { var px = hitungUtangPemasok().find(function (p) { return p.pemasok === 'PEMASOK BAL30'; }); var b = px ? px.bon.find(function (x) { return x.id === 'bal30'; }) : null; return b ? b.nilai : null; };
var urut30 = function (o) { return JSON.stringify(Object.keys(o).filter(function (k) { return k !== 'id'; }).sort().map(function (k) { return [k, o[k]]; })); };
var balSama = function (d) { var b = (d.merkList || []).filter(function (m) { return m.bentuk === 'bal'; }); return b.length === 1 && urut30(b[0]) === urut30(BAL30); };
var alok30 = function (merk) { var d = ambilSemuaBatch().find(function (b) { return b.id === 'bal30'; }); var r = hitungHppMerkDalamBatch(d.merkList, d.biayaBongkar).find(function (m) { return m.merk === merk && m.bentuk !== 'bal'; }); return r ? Math.round(r.alokasiBongkar) : null; };
var d30 = drafDariKedatangan('bal30'); d30.baris[0].hargaPerKg = '13.050'; d30.alasan = 'salah ketik harga'; var K30 = susunSimpanMasuk(d30, W30, true); var t30 = K30.dokumen ? K30.dokumen[0].data : { merkList: [] };
ok('39b-30: koreksi kedatangan berbaris bal: draf hanya baris karung (bal tidak diubah dari sini); dokumen yang ditulis MEMUAT baris bal apa adanya (hanya nomor barisnya, di belakang); kabar menyebut bal "tidak diubah"; pasangan beli-jadi tidak disentuh',
  d30.adaBal === true && d30.baris.length === 2 && !K30.tolak && t30.merkList.length === 3 && balSama(t30) && t30.merkList[2].bentuk === 'bal' && t30.merkList[2].id === '3' && /baris bal Rp2\.800\.000 \(tidak diubah\)/.test(K30.patch.kabar) && K30.dokumen.every(function (x) { return x.koleksi !== 'produksiKemasan'; }), JSON.stringify([K30.tolak, t30.merkList]).slice(0, 400));
var hm30 = hitungMasuk(d30);
ok('39b-30: pratinjau koreksi (kartu Jumlah & modal per baris) = yang akan ditulis: nilai bal 2.800.000 ikut, total 13.050.000 + 6.500.000 + 2.800.000 + bongkar 170.000 = 22.520.000; bongkar Rojolele Bal Uji 100.000 → modal 13.150/kg (bukan 113.333 / 13.163)',
  hm30.nilaiBal === 2800000 && hm30.total === 22520000 && hm30.sah[0].alokasiBongkar === 100000 && Math.abs(hm30.sah[0].hppPerKg - 13150) < 0.01, JSON.stringify([hm30.nilaiBal, hm30.total, hm30.sah[0].alokasiBongkar, hm30.sah[0].hppPerKg]));
var rw30 = riwayatModal('Rojolele Bal Uji').filter(function (r) { return r.jenis === 'kedatangan' && r.batchId === 'bal30'; })[0] || {}; var ms30 = hitungStokKarungPerMerk()['Rojolele Bal Uji'] || {};
ok('39b-30: riwayat modal Stok › HPP = mesin untuk kedatangan berbaris bal: HPP 13.100/kg (13.000 + bongkar 100), rata-rata totalMasuk = modal mesin; baris bal sendiri bukan kedatangan karung',
  Math.abs((rw30.hppPerKg || 0) - 13100) < 0.01 && Math.abs(totalMasuk('Rojolele Bal Uji').rata - (ms30.hppTerakhirPerKg || 0)) < 1e-6 && !riwayatModal('Kembang').some(function (r) { return r.batchId === 'bal30'; }), JSON.stringify([rw30.hppPerKg, totalMasuk('Rojolele Bal Uji').rata, ms30.hppTerakhirPerKg]));
terapkanKeCache(K30.dokumen || []);
ok('39b-30: sesudah koreksi: bon pemasok 13.050.000 + 6.500.000 + bal 2.800.000 = 22.350.000 (bukan 19.550.000); porsi bongkar Rojolele Bal Uji tetap 1.000/1.700 × 170.000 = 100.000 (porsi bal tidak pindah ke modal karung)',
  bon30() === 22350000 && alok30('Rojolele Bal Uji') === 100000, JSON.stringify([bon30(), alok30('Rojolele Bal Uji')]));
terapkanKeCache([{ koleksi: 'batchMasuk', data: batch30 }]);
var H30 = susunKoreksiHpp('Rojolele Bal Uji', '13.050', 'uji no. 30', W30, true); var h30 = H30.dokumen ? H30.dokumen.filter(function (x) { return x.koleksi === 'batchMasuk'; })[0].data : { merkList: [] };
ok('39b-30: koreksi HPP (Stok › HPP) atas kedatangan berbaris bal juga menulis baris bal apa adanya', !H30.tolak && h30.merkList.length === 3 && balSama(h30), JSON.stringify([H30.tolak, h30.merkList]).slice(0, 400));
bayar2('b30', 'PEMASOK BAL30', 21000000, 'bal30');
var k30 = function (ubah) { var x = drafDariKedatangan('bal30'); x.alasan = 'uji'; ubah(x); return susunSimpanMasuk(x, W30, true); };
var naik30 = k30(function (x) { x.baris[0].hargaPerKg = '13.050'; }); var turun30 = k30(function (x) { x.baris[0].hargaPerKg = '11.000'; x.baris[1].hargaPerKg = '12.000'; });
ok('39b-30: bon berbaris bal yang sudah dibayar 21.000.000: koreksi harga karung NAIK boleh (22.350.000 termasuk bal); TURUN ke 11.000.000 + 6.000.000 + bal 2.800.000 = 19.800.000 DITOLAK dengan angka yang memuat bal',
  !naik30.tolak && /nilai bon sesudah koreksi Rp19\.800\.000 lebih kecil; kelebihan Rp1\.200\.000/.test(turun30.tolak || ''), JSON.stringify([naik30.tolak, turun30.tolak]).slice(0, 400));
var PM30 = pratinjauMassal({ 'Rojolele Bal Uji': '13.050', 'Rojolele Bal Dua': '13.050' }); var PM30b = pratinjauMassal({ 'Rojolele Bal Uji': '12.000', 'Rojolele Bal Dua': '12.000' });
ok('39b-30: koreksi HPP atas bon berbaris bal yang dibayar 21.000.000 menghitung nilai bal: satu nama 13.050 boleh, 10.000 ditolak (19.300.000); massal dua nama 13.050 SIAP (22.375.000), 12.000 ditolak BERSAMA (20.800.000)',
  !nilaiKoreksi('Rojolele Bal Uji', '13.050').tolak && /nilai bonnya Rp19\.300\.000/.test(nilaiKoreksi('Rojolele Bal Uji', '10.000').tolak || '') && PM30.siap && !PM30b.siap && /BERSAMA membuat nilai bonnya Rp20\.800\.000/.test(PM30b.bermasalah.map(function (b) { return b.tolak; }).join(' | ')),
  JSON.stringify([nilaiKoreksi('Rojolele Bal Uji', '13.050').tolak, PM30.teks, PM30b.teks]).slice(0, 400));
terapkanKeCache([{ koleksi: 'utangPemasokMutasi', hapus: 'b30' }, { koleksi: 'batchMasuk', hapus: 'bal30' }, { koleksi: 'produksiKemasan', hapus: 'bj30' }]);

// ==================== COCOKKAN / HITUNG GUDANG (ST3) — bentuk dokumen simpanPenyesuaianStok / Kemasan / OpnameBahan ====================
var WC = { tanggal: '2026-09-19', jam: '16:00', idUnik: WW.idUnik };
var bc = barangCocok('tumpukan'); var bA = bc.find(function (b) { return b.nama === 'Angsa'; });
ok('cocok (putaran 27 · tab TUMPUKAN): tiap nama dari buku; tercatat = tumpukan gudang (buku − karung terbuka − bagian di wadah), buku & modal ikut; rincian menyebut rantainya', bc.length >= 3 && bA && Math.abs(bA.sistem - tumpukanGudang('Angsa').kg) < 0.011 && Math.abs(bA.buku - hitungStokKarungPerMerk()['Angsa'].sisaKg) < 0.011 && bA.modal > 0 && bA.satuan === 'kg' && /^buku .* = tumpukan /.test(bc.find(function (b) { return b.nama === 'IR64 Apex'; }).rincian || ''), JSON.stringify(bc.map(function (b) { return b.nama + ':' + b.sistem; })));
var C0 = susunCocok('tumpukan', {}, {}, {});
ok('cocok: belum ada yang dihitung → simpan ditolak dengan kalimatnya', /Belum ada yang dihitung/.test(C0.tolak) && C0.dihitung === 0 && C0.semua === bc.length);
var H = {}; H[bA.kunci] = String(bA.sistem - 8); var C1 = susunCocok('tumpukan', H, {}, {});
var b1 = C1.baris.find(function (b) { return b.nama === 'Angsa'; });
ok('cocok: Angsa dihitung 8 kg kurang (ketikan "76.6" dari papan tombol HP dibaca 76,6 — bukan 766); selisih > 3 % butuh alasan → simpan ditolak menyebut namanya', b1.ada && b1.selisih === -8 && b1.rp === Math.round(-8 * bA.modal) && b1.besar === true && b1.perluAlasan === true && C1.susutRp === b1.rp && /Angsa: selisihnya lebih dari 3 %/.test(C1.tolak), JSON.stringify([b1, C1.tolak]));
var AL = {}; AL[bA.kunci] = 'tumpah waktu bongkar'; var C2 = susunCocok('tumpukan', H, AL, {});
ok('cocok: dengan alasan, sisa penolakan = yang belum dihitung (ketuk sekali lagi = simpan sebagian)', C2.perluYakin === 'sebagian' && /belum dihitung/.test(C2.tolak) && !susunCocok('tumpukan', H, AL, { sebagian: true }).tolak);
var SC = susunSimpanCocok('tumpukan', H, AL, WC, { sebagian: true }); if (!SC.dokumen) { gagal.push('cocok: simpan DITOLAK: ' + SC.tolak + ' | ' + JSON.stringify(susunCocok('tumpukan', H, AL, { sebagian: true }))); SC.dokumen = [{ koleksi: '?', data: {} }]; } var dokC = SC.dokumen[0].data;
ok('cocok: SATU dokumen penyesuaianStok {tanggal, jam, merk, kgSistem = buku, kgFisik = buku − 8, selisihKg −8, alasan, nilaiRp (dikunci), hppPerKgSaatOpname} = kolom sistem berjalan + penanda putaran 27 {bagian tumpukan, bagianSistemKg = tumpukan tercatat, bagianFisikKg = dihitung}; kabar menyebut laba turun', SC.dokumen.length === 1 && SC.dokumen[0].koleksi === 'penyesuaianStok' && Object.keys(dokC).sort().join() === 'alasan,bagian,bagianFisikKg,bagianSistemKg,hppPerKgSaatOpname,id,jam,kgFisik,kgSistem,merk,nilaiRp,selisihKg,tanggal' && dokC.merk === 'Angsa' && dokC.selisihKg === -8 && Math.abs(dokC.kgFisik - (bA.buku - 8)) < 0.001 && dokC.kgSistem === bA.buku && dokC.bagian === 'tumpukan' && dokC.bagianSistemKg === bA.sistem && Math.abs(dokC.bagianFisikKg - (bA.sistem - 8)) < 0.001 && dokC.nilaiRp === b1.rp && dokC.hppPerKgSaatOpname === Math.round(bA.modal) && dokC.alasan === 'tumpah waktu bongkar' && /Laba bulan ini turun/.test(SC.patch.kabar), JSON.stringify(SC));
terapkanKeCache(SC.dokumen);
ok('cocok: sesudah dicatat, buku Angsa = hasil hitungan (mesin beku membaca selisihKg), modal per kg TIDAK berubah; kartu "belum dicocokkan" Angsa = 0 hari; riwayat memuatnya', Math.abs(hitungStokKarungPerMerk()['Angsa'].sisaKg - (bA.buku - 8)) < 0.011 && Math.abs(hitungStokKarungPerMerk()['Angsa'].hppTerakhirPerKg - bA.modal) < 0.001 && susunGudang('cocok', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).n === '0 hari' && riwayatCocok(3)[0].baris[0].nama === 'Angsa (tumpukan)' && riwayatCocok(3)[0].rp === b1.rp, JSON.stringify(riwayatCocok(3)));
var H2 = {}; H2[bA.kunci] = String(bA.sistem - 8 + 1); var AL2 = {}; AL2[bA.kunci] = 'hitung ulang'; var C3 = susunSimpanCocok('tumpukan', H2, AL2, { tanggal: '2026-09-19', jam: '16:05', idUnik: WW.idUnik }, { sebagian: true });
ok('cocok: hitungan KEDUA untuk Angsa 5 menit kemudian DITANYA (penjaga opname ganda 26 Agu), ketukan kedua boleh', C3.perluYakin === 'ganda' && /baru saja dicocokkan/.test(C3.tolak) && !susunSimpanCocok('tumpukan', H2, AL2, { tanggal: '2026-09-19', jam: '16:05', idUnik: WW.idUnik }, { sebagian: true, ganda: true }).tolak, JSON.stringify([C3.tolak, bA.sistem]));
var H3 = {}; H3[bA.kunci] = String(bA.sistem * 3); var C4 = susunCocok('tumpukan', H3, (function () { var o = {}; o[bA.kunci] = 'benar'; return o; })(), {});
ok('cocok: dihitung lebih dari dua kali tercatat = ANEH, ditanya dulu; stok bertambah lebih dari ambang rupiah ditanya juga (beras tidak tumbuh sendiri)', C4.perluYakin === 'aneh' && /Angka aneh/.test(C4.tolak) && susunCocok('tumpukan', H3, (function () { var o = {}; o[bA.kunci] = 'benar'; return o; })(), { aneh: true }).perluYakin === 'susutPositif');
var ck = barangCocok('kemasan'); var kK = ck.find(function (b) { return /Kembang 5 kg/.test(b.nama); }); var HK2 = {}; HK2[kK.kunci] = String(kK.sistem + 1);
var SK = susunSimpanCocok('kemasan', HK2, {}, WC, { sebagian: true }); if (!SK.dokumen) SK.dokumen = [{ koleksi: '?', data: {} }];
ok('cocok: kemasan jadi per unit → dokumen penyesuaianKemasan {namaProduk, ukuranKemasan (angka), unitSistem, unitFisik, selisihUnit +1, alasan bawaan, nilaiRp = modal per unit, hppPerUnitSaatOpname}; sesudahnya sisa unit = hitungan', kK.satuan === 'unit' && SK.dokumen.length === 1 && SK.dokumen[0].koleksi === 'penyesuaianKemasan' && SK.dokumen[0].data.namaProduk === 'Kembang' && SK.dokumen[0].data.ukuranKemasan === 5 && SK.dokumen[0].data.selisihUnit === 1 && SK.dokumen[0].data.nilaiRp === Math.round(kK.modal) && SK.dokumen[0].data.alasan === 'Cocokkan stok' && (function () { terapkanKeCache(SK.dokumen); return hitungStokKemasan()[kunciKemasan('Kembang', 5)].sisaUnit === kK.sistem + 1; })(), JSON.stringify(SK.dokumen));
terapkanKeCache([{ koleksi: 'stokBahanKemasan', data: { id: 'bk1', tanggal: '2026-09-01', jenis: '5kg_kembangbmw', tipe: 'beli', jumlah: 200, hargaTotal: 225000 } }]);
var ckt = barangCocok('kantong'); var kT = ckt.find(function (b) { return b.jenis === '5kg_kembangbmw'; }); var HT = {}; HT[kT.kunci] = '190';
var ALT = {}; ALT[kT.kunci] = 'robek'; var ST = susunSimpanCocok('kantong', HT, ALT, WC, { sebagian: true, susutPositif: true }); if (!ST.dokumen) ST.dokumen = [{ koleksi: '?', data: {} }];
ok('cocok: kantong per lembar → dokumen stokBahanKemasan {tipe opname, jenis, jumlah −10, hargaTotal 0, pcsSistem, pcsFisik, catatan, nilaiRp = −10 × 1.125, hargaPerPcsSaatOpname}; sesudahnya sisa = 190, harga per lembar tetap', kT && kT.sistem === 200 && kT.modal === 1125 && ST.dokumen.length === 1 && ST.dokumen[0].koleksi === 'stokBahanKemasan' && ST.dokumen[0].data.tipe === 'opname' && ST.dokumen[0].data.jumlah === -10 && ST.dokumen[0].data.hargaTotal === 0 && ST.dokumen[0].data.nilaiRp === -11250 && ST.dokumen[0].data.pcsFisik === 190 && (function () { terapkanKeCache(ST.dokumen); var k = hitungStokBahanKemasan()['5kg_kembangbmw']; return k.sisaPcs === 190 && k.hppPerPcs === 1125; })(), JSON.stringify([kT, ST.dokumen]));
ok('cocok: rework karantina (dariRework, kgFisik null) tidak masuk riwayat hitungan fisik dan tidak mengunci penjaga ganda', (function () { terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 7002, tanggal: '2026-09-19', jam: '16:01', merk: 'IR64 Apex', kgSistem: null, kgFisik: null, selisihKg: 41.5, alasan: 'Rework', dariRework: true } }]);
  var bX = barangCocok('tumpukan').find(function (b) { return b.nama === 'IR64 Apex'; }); var Hx = {}; Hx[bX.kunci] = String(bX.sistem - 1); var r = susunSimpanCocok('tumpukan', Hx, {}, { tanggal: '2026-09-19', jam: '16:03', idUnik: WW.idUnik }, { sebagian: true });
  var adaRework = riwayatCocok(20).some(function (g) { return g.baris.some(function (x) { return x.alasan === 'Rework'; }); }); terapkanKeCache([{ koleksi: 'penyesuaianStok', hapus: 7002 }]); return !r.tolak && !adaRework; })());

// ====================== ADUKAN (ST2) & KARANTINA — 23 Sep ======================
// bahan baru dipasok DI AKHIR supaya skenario di atas tidak bergeser: Perahu Layar 500 kg @12.000, kantong 5 kg @1.125 & 25 kg @2.500, katalog nama
pasok('batchMasuk', cacheMentah('batch').concat([{ id: 'b3', tanggal: '2026-08-22', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ merk: 'Perahu Layar', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, subtotalHarga: 6000000, hargaPerKg: 12000 }] }]));
pasok('stokBahanKemasan', [{ id: 'kb1', tipe: 'beli', jenis: '5kg_kembangbmw', jumlah: 100, hargaTotal: 112500, tanggal: '2026-08-20' }, { id: 'kb2', tipe: 'beli', jenis: '25kg_kembang', jumlah: 10, hargaTotal: 25000, tanggal: '2026-08-20' }]);
pasok('katalogHargaKemasan', [{ id: 'ascent_25kg', merk: 'Ascent', ukuran: 25, hargaPerUnit: 390000 }, { id: 'kembang_5kg', merk: 'Kembang', ukuran: 5, hargaPerUnit: 78000 }]);
var WA = { tanggal: '2026-09-19', jam: '11:00', kini: '2026-09-19T04:00:00.000Z', idUnik: (function () { var n = 7000; return function () { n += 1; return n; }; })() };
var adSalinProduksi = function () { return cacheMentah('produksi').slice(); };
var adTerapkan = function (r) { var per = {}; r.dokumen.forEach(function (d) { var kol = d.koleksi; if (!per[kol]) per[kol] = cacheMentah(({ produksiKemasan: 'produksi', stokBahanKemasan: 'bahanKemasan', penyesuaianStok: 'penyesuaian', karantina: 'karantina', retur: 'retur', bukuHapus: 'bukuHapus' })[kol]).slice();
  per[kol] = per[kol].filter(function (x) { return String(x.id) !== String(d.data.id); }).concat([d.data]); }); Object.keys(per).forEach(function (kol) { pasok(kol, per[kol]); }); };
ok('adukan: calon bahan = nama bersisa, terbanyak dulu (Perahu Layar 500 kg); kantong untuk 5 kg = dua jenis Kembang/BMW & Putri Agri dengan sisa & modal per lembar; 50 kg tanpa kantong; calon nama hasil = pernah diaduk (Kembang) lalu katalog (Ascent)',
  calonBahan()[0].merk === 'Perahu Layar' && calonBahan()[0].sisaKg === 500 && calonBahan()[0].hpp === 12000 && kantongUntuk(5).length === 2 && kantongUntuk(5)[0].jenis === '5kg_kembangbmw' && kantongUntuk(5)[0].sisaPcs === 100 && kantongUntuk(5)[0].hppPerPcs === 1125 && kantongUntuk(50).length === 0 && calonNamaHasil()[0] === 'Kembang' && calonNamaHasil().indexOf('Ascent') > 0,
  JSON.stringify([calonBahan().slice(0, 2), kantongUntuk(5), calonNamaHasil()]));
var dA = drafAdukanKosong(WA); dA.bahan = [{ merk: 'Perahu Layar', kg: '100' }]; dA.hasil = [{ nama: 'Ascent', ukuran: '25', unit: '2', kantongJenis: '25kg_kembang', kantongJumlah: '2' }, { nama: 'Ascent', ukuran: '5', unit: '10', kantongJenis: '5kg_kembangbmw', kantongJumlah: '10' }]; dA.upah = '20.000';
var HA = hitungAdukan(dA);
ok('adukan: biaya = bahan 100 kg × 12.000 + kantong (2 × 2.500 + 10 × 1.125) + upah 20.000 = 1.236.250; dibagi MENURUT KG (50 kg : 50 kg): 25 kg → 309.063/unit (dibulatkan), 5 kg → sisa/10 = 61.812,4 berpecahan; Σ (modal × unit) = total PERSIS',
  HA.nilaiBahan === 1200000 && HA.biayaKantong === 16250 && HA.upah === 20000 && HA.total === 1236250 && HA.kgMasuk === 100 && HA.kgJadi === 100 && HA.sahH[0].hppPerUnit === 309063 && Math.abs(HA.sahH[1].hppPerUnit - 61812.4) < 1e-9 && HA.sahH.reduce(function (a, h) { return a + h.hppPerUnit * h.unit; }, 0) === 1236250 && HA.susutKg === 0,
  JSON.stringify([HA.nilaiBahan, HA.biayaKantong, HA.total, HA.sahH.map(function (h) { return h.hppPerUnit; })]));
ok('adukan: modal per unit = rumus mesin beku bagiBiayaAdukan (bukan hitungan sendiri)', JSON.stringify(HA.sahH.map(function (h) { return h.hppPerUnit; })) === JSON.stringify(bagiBiayaAdukan([{ ukuranKemasan: 25, jumlahUnit: 2 }, { ukuranKemasan: 5, jumlahUnit: 10 }], 1236250)));
var SA = susunSimpanAdukan(dA, WA, {}); var dokA = SA.dokumen.filter(function (d) { return d.koleksi === 'produksiKemasan'; }).map(function (d) { return d.data; }); var dokK = SA.dokumen.filter(function (d) { return d.koleksi === 'stokBahanKemasan'; }).map(function (d) { return d.data; });
var KUNCI_PRODUKSI = ['id', 'tanggal', 'jam', 'merkSumber', 'namaProduk', 'ukuranKemasan', 'jumlahUnit', 'biayaKemasan', 'upahRepacking', 'kantongJenis', 'kantongJumlah', 'hppSumberPerKgDipakai', 'hppPerUnit', 'sumberList', 'kgDipakai', 'sumberKemasanList', 'kgKemasanDipakai', 'batchProduksi', 'barisKe', 'jumlahBaris', 'jadiKarungUtuh', 'merkTujuan'].sort().join(',');
ok('adukan: SIMPAN → 2 dokumen produksi + 2 pemakaian kantong; kolom PERSIS simpanProduksi (+ jam); sumberList/kgDipakai/upah HANYA di dokumen pertama; batchProduksi = id pertama, barisKe 1–2, jumlahBaris 2; kantong id = id produksi + 1, tipe pakai, jumlah lembar',
  !SA.tolak && dokA.length === 2 && dokK.length === 2 && Object.keys(dokA[0]).sort().join(',') === KUNCI_PRODUKSI && Object.keys(dokA[1]).sort().join(',') === KUNCI_PRODUKSI && dokA[0].sumberList.length === 1 && dokA[0].sumberList[0].kg === 100 && dokA[0].kgDipakai === 100 && dokA[0].upahRepacking === 20000 && dokA[1].sumberList.length === 0 && dokA[1].kgDipakai === 0 && dokA[1].upahRepacking === 0
  && dokA[0].batchProduksi === dokA[0].id && dokA[1].batchProduksi === dokA[0].id && dokA[0].barisKe === 1 && dokA[1].barisKe === 2 && dokA[0].jumlahBaris === 2 && dokA[0].jadiKarungUtuh === false && dokA[0].merkTujuan === null && dokA[0].merkSumber === 'Perahu Layar' && dokA[0].biayaKemasan === 5000 && dokA[1].biayaKemasan === 11250
  && dokK[0].id === dokA[0].id + 1 && dokK[0].tipe === 'pakai' && dokK[0].jenis === '25kg_kembang' && dokK[0].jumlah === 2 && dokK[0].hargaTotal === 0 && /produksi id/.test(dokK[0].catatan) && dokK[1].id === dokA[1].id + 1 && dokK[1].jumlah === 10 && Math.abs(dokA[0].hppSumberPerKgDipakai - 12000) < 1e-9,
  JSON.stringify([SA.tolak, dokA, dokK]));
var adSebelum = adSalinProduksi(); adTerapkan(SA); var stokKA = hitungStokKarungPerMerk(), stokMA = hitungStokKemasan(), stokBA = hitungStokBahanKemasan();
ok('adukan: sesudah tersimpan, MESIN LAMA membaca: Perahu Layar 500 → 400 kg (dipotong SEKALI), Ascent 25 kg 2 unit @309.063, Ascent 5 kg 10 unit @61.812, kantong 25 kg 10 → 8 lembar, 5 kg 100 → 90; nilai kemasan jadi = total biaya persis',
  stokKA['Perahu Layar'].sisaKg === 400 && stokMA['Ascent|25'].sisaUnit === 2 && stokMA['Ascent|25'].hppRataRataPerUnit === 309063 && stokMA['Ascent|5'].sisaUnit === 10 && stokMA['Ascent|5'].hppRataRataPerUnit === 61812 && stokBA['25kg_kembang'].sisaPcs === 8 && stokBA['5kg_kembangbmw'].sisaPcs === 90
  && Math.abs(stokMA['Ascent|25'].nilaiProduksiTotal + stokMA['Ascent|5'].nilaiProduksiTotal - 1236250) < 1e-6, JSON.stringify([stokKA['Perahu Layar'], stokMA['Ascent|25'], stokMA['Ascent|5'], stokBA['25kg_kembang'].sisaPcs, stokBA['5kg_kembangbmw'].sisaPcs]));
ok('adukan: kabar menyebut bahan → hasil, biaya & modal per unit, dan bahwa KAS tidak bergerak', /100 kg Perahu Layar → 2 × Ascent 25 kg \+ 10 × Ascent 5 kg/.test(SA.patch.kabar) && /Rp1\.236\.250/.test(SA.patch.kabar) && /Kas tidak bergerak/.test(SA.patch.kabar), SA.patch.kabar);
// penjaga — urutan sama dengan simpanProduksi
var dKosong = drafAdukanKosong(WA); dKosong.hasil = [{ nama: 'Ascent', ukuran: '5', unit: '1', kantongJenis: '', kantongJumlah: '' }];
var dTanpaUnit = drafAdukanKosong(WA); dTanpaUnit.bahan = [{ merk: 'Perahu Layar', kg: '50' }]; dTanpaUnit.hasil = [{ nama: 'Ascent', ukuran: '5', unit: '', kantongJenis: '', kantongJumlah: '' }];
var dLingkar = drafAdukanKosong(WA); dLingkar.bahan = []; dLingkar.bahanKemasan = [{ kunci: 'Ascent|25', unit: '1' }]; dLingkar.hasil = [{ nama: 'Ascent', ukuran: '25', unit: '1', kantongJenis: '', kantongJumlah: '' }];
var dKurang = drafAdukanKosong(WA); dKurang.bahan = [{ merk: 'Perahu Layar', kg: '450' }]; dKurang.hasil = [{ nama: 'Ascent', ukuran: '25', unit: '18', kantongJenis: '', kantongJumlah: '' }];
var dKantongKosong = drafAdukanKosong(WA); dKantongKosong.bahan = [{ merk: 'Perahu Layar', kg: '50' }]; dKantongKosong.hasil = [{ nama: 'Ascent', ukuran: '5', unit: '10', kantongJenis: '5kg_kembangbmw', kantongJumlah: '' }];
var dKantongKurang = drafAdukanKosong(WA); dKantongKurang.bahan = [{ merk: 'Perahu Layar', kg: '400' }]; dKantongKurang.hasil = [{ nama: 'Ascent', ukuran: '5', unit: '80', kantongJenis: '5kg_kembangbmw', kantongJumlah: '95' }];
var dSusut = drafAdukanKosong(WA); dSusut.bahan = [{ merk: 'Perahu Layar', kg: '100' }]; dSusut.hasil = [{ nama: 'Ascent', ukuran: '5', unit: '16', kantongJenis: '', kantongJumlah: '' }];
var dBongkar = drafAdukanKosong(WA); dBongkar.bahan = []; dBongkar.bahanKemasan = [{ kunci: 'Ascent|25', unit: '1' }]; dBongkar.hasil = [{ nama: 'Ascent', ukuran: '5', unit: '5', kantongJenis: '5kg_kembangbmw', kantongJumlah: '5' }];
ok('adukan: tanpa bahan DITOLAK; baris hasil tanpa unit DITOLAK menyebut barisnya; bahan = hasil (Ascent 25 kg dibongkar jadi Ascent 25 kg) DITOLAK sebagai lingkaran',
  /minimal satu bahan/.test(susunSimpanAdukan(dKosong, WA, {}).tolak || '') && /Baris 1 \(Ascent\): jumlah unitnya belum diisi/.test(susunSimpanAdukan(dTanpaUnit, WA, {}).tolak || '') && /BAHAN sekaligus jadi HASIL/.test(susunSimpanAdukan(dLingkar, WA, {}).tolak || '') && !susunSimpanAdukan(dLingkar, WA, { bahan: true, kemasan: true }).dokumen,
  JSON.stringify([susunSimpanAdukan(dKosong, WA, {}).tolak, susunSimpanAdukan(dTanpaUnit, WA, {}).tolak, susunSimpanAdukan(dLingkar, WA, {}).tolak]));
ok('adukan: stok bahan kurang (450 dari 400 kg) DITANYA (perluYakin bahan) lalu boleh; kantong dipilih tanpa lembar DITANYA (kantongKosong) dengan kalimat "terhitung GRATIS"; kantong kurang (95 dari 90) DITANYA (kantong); susut > 15 % (100 → 80 kg) DITANYA (susut)',
  susunSimpanAdukan(dKurang, WA, {}).perluYakin === 'bahan' && /menurut buku cuma 400 kg/.test(susunSimpanAdukan(dKurang, WA, {}).tolak) && !susunSimpanAdukan(dKurang, WA, { bahan: true }).tolak
  && susunSimpanAdukan(dKantongKosong, WA, {}).perluYakin === 'kantongKosong' && /GRATIS/.test(susunSimpanAdukan(dKantongKosong, WA, {}).tolak) && !susunSimpanAdukan(dKantongKosong, WA, { kantongKosong: true }).tolak
  && susunSimpanAdukan(dKantongKurang, WA, {}).perluYakin === 'kantong' && !susunSimpanAdukan(dKantongKurang, WA, { kantong: true }).tolak
  && susunSimpanAdukan(dSusut, WA, {}).perluYakin === 'susut' && /selisih lebih dari 15 %/.test(susunSimpanAdukan(dSusut, WA, {}).tolak) && !susunSimpanAdukan(dSusut, WA, { susut: true }).tolak,
  JSON.stringify([susunSimpanAdukan(dKurang, WA, {}), susunSimpanAdukan(dKantongKosong, WA, {}).tolak, susunSimpanAdukan(dKantongKurang, WA, {}).tolak, susunSimpanAdukan(dSusut, WA, {}).tolak].map(function (x) { return x && x.tolak ? x.tolak : x; })));
ok('adukan: kantong yang disimpan "gratis" (ketukan kedua) memang TIDAK menulis pemakaian kantong dan biaya kantongnya 0 — jujur, bukan diam-diam', (function () { var r = susunSimpanAdukan(dKantongKosong, WA, { kantongKosong: true }); return r.dokumen.length === 1 && r.dokumen[0].data.biayaKemasan === 0 && r.dokumen[0].data.kantongJumlah === 0; })());
// buku adukan · rincian · hapus · koreksi
var DA = daftarAdukan(10); var batchA = dokA[0].id;
ok('buku adukan: adukan tadi paling atas (satu kartu, 2 baris), total 1.236.250, teks bahan → hasil; adukan lama satu baris (p1) ikut; kg masuk/jadi tersedia untuk timbangan',
  DA[0].batch === String(batchA) && DA[0].baris === 2 && DA[0].total === 1236250 && DA[0].bahanTeks === '100 kg Perahu Layar' && DA[0].hasilTeks === '2 × Ascent 25 kg + 10 × Ascent 5 kg' && DA[0].kgMasuk === 100 && DA[0].kgJadi === 100 && DA.some(function (x) { return x.batch === 'p1'; }), JSON.stringify(DA));
pasok('produksiKemasan', cacheMentah('produksi').concat([{ id: 'bj1', tanggal: '2026-09-18', beliJadi: true, dariBatch: 'b2', namaProduk: 'BMW', ukuranKemasan: 5, jumlahUnit: 10, hppPerUnit: 60000, kgDipakai: 0 }, { id: 'tk1', tanggal: '2026-09-18', dariTakar: true, jadiKarungUtuh: true, merkTujuan: 'Angsa', namaProduk: 'Angsa', ukuranKemasan: 3.6, jumlahUnit: 1, hppPerUnit: 0, kgDipakai: 3.6, sumberList: [{ merk: 'IR64 Apex', kg: 3.6 }] }]));
ok('buku adukan: beli-jadi dari kedatangan & pindah buku takar TIDAK tampil sebagai adukan (milik layar lain)', !daftarAdukan(50).some(function (x) { return x.batch === 'bj1' || x.batch === 'tk1'; }), JSON.stringify(daftarAdukan(50).map(function (x) { return x.batch; })));
pasok('produksiKemasan', cacheMentah('produksi').filter(function (p) { return p.id !== 'bj1' && p.id !== 'tk1'; }));
var RA = rincianAdukan(batchA);
ok('rincian: biaya bahan 1.200.000 · kantong 16.250 · upah 20.000 · total tercatat 1.236.250; timbangan 100 kg ⇄ 100 kg; kedua hasil belum terjual → boleh dihapus & dikoreksi',
  RA && Math.abs(RA.biaya.bahan - 1200000) < 1e-6 && RA.biaya.kantong === 16250 && RA.biaya.upah === 20000 && Math.abs(RA.biaya.total - 1236250) < 1e-6 && RA.kgMasuk === 100 && RA.kgJadi === 100 && RA.bisaHapus && RA.bisaKoreksi && RA.hasil[0].kantong === '25 kg — Kembang × 2', JSON.stringify(RA));
pasok('penjualan', cacheMentah('penjualan').concat([{ id: 'j9', tanggal: '2026-09-19', jam: '11:30', caraBayar: 'Tunai', jenis: 'kemasan', namaProduk: 'Ascent', ukuranKemasan: 25, jumlahUnit: 1, totalKg: 25, hargaTotal: 390000, hppTotalSaatJual: 309063 }]));
ok('hapus: satu Ascent 25 kg sudah TERJUAL → hapus DITOLAK dengan kalimat "1 dari 2 unit sudah terjual"; koreksi masih boleh', !rincianAdukan(batchA).bisaHapus && /Ascent 25 kg: 1 dari 2 unit sudah terjual/.test(susunHapusAdukan(batchA, 'x', WA).tolak) && rincianAdukan(batchA).bisaKoreksi, susunHapusAdukan(batchA, 'x', WA).tolak);
pasok('penjualan', cacheMentah('penjualan').filter(function (p) { return p.id !== 'j9'; }));
var HPA = susunHapusAdukan(batchA, 'salah ketik ukuran', WA);
ok('hapus: tanpa alasan DITOLAK; dengan alasan → mencabut 2 dokumen produksi + 2 pasangan kantong (id + 1), jejak ke bukuHapus koleksi produksiKemasan; kabar menyebut bahan kembali & hasil dicabut',
  /alasan/.test(susunHapusAdukan(batchA, '', WA).tolak || '') && HPA.hapus.length === 4 && HPA.hapus.filter(function (x) { return x.koleksi === 'stokBahanKemasan'; }).map(function (x) { return x.id; }).sort().join(',') === [dokA[0].id + 1, dokA[1].id + 1].sort().join(',') && HPA.dokumen[0].koleksi === 'bukuHapus' && HPA.dokumen[0].data.koleksi === 'produksiKemasan' && HPA.dokumen[0].data.idDok === String(batchA) && /kembali ke stok asal/.test(HPA.patch.kabar), JSON.stringify(HPA));
var KA = susunKoreksiAdukan(batchA, '1.300.000', 'lupa upah kemas', WA);
ok('koreksi: tanpa alasan DITOLAK; total sama DITOLAK; total 1.300.000 → 4 dokumen: 2 pengganti (koreksiDari, hppPerUnit baru, tanpa dikoreksiOleh) + 2 lama ditandai dikoreksiOleh = id pengganti; modal baru 325.000 & 65.000 (Σ persis 1.300.000)',
  /alasan/.test(susunKoreksiAdukan(batchA, '1.300.000', '', WA).tolak || '') && /sama dengan yang tercatat/.test(susunKoreksiAdukan(batchA, '1.236.250', 'x', WA).tolak || '') && !KA.tolak && KA.dokumen.length === 4
  && KA.dokumen[0].data.koreksiDari === dokA[0].id && KA.dokumen[0].data.hppPerUnit === 325000 && KA.dokumen[0].data.dikoreksiOleh === undefined && KA.dokumen[1].data.id === dokA[0].id && KA.dokumen[1].data.dikoreksiOleh === KA.dokumen[0].data.id && KA.dokumen[2].data.hppPerUnit === 65000 && KA.dokumen[0].data.hppPerUnit * 2 + KA.dokumen[2].data.hppPerUnit * 10 === 1300000 && KA.dokumen[0].data.alasanKoreksi === 'lupa upah kemas',
  JSON.stringify([susunKoreksiAdukan(batchA, '1.300.000', '', WA).tolak, KA]));
adTerapkan(KA); var stokMK = hitungStokKemasan();
ok('koreksi: sesudah diterapkan mesin membaca modal BARU (Ascent 25 kg 325.000, 5 kg 65.000), unit tidak berlipat (2 & 10), Perahu Layar tetap 400 kg (bahan tidak terpotong dua kali); rincian menandai dikoreksi & riwayat 2 baris beralasan',
  stokMK['Ascent|25'].hppRataRataPerUnit === 325000 && stokMK['Ascent|25'].sisaUnit === 2 && stokMK['Ascent|5'].hppRataRataPerUnit === 65000 && stokMK['Ascent|5'].sisaUnit === 10 && hitungStokKarungPerMerk()['Perahu Layar'].sisaKg === 400 && rincianAdukan(batchA).dikoreksi && rincianAdukan(batchA).riwayat.length === 2 && rincianAdukan(batchA).riwayat[0].alasan === 'lupa upah kemas' && Math.abs(rincianAdukan(batchA).biaya.total - 1300000) < 1e-6,
  JSON.stringify([stokMK['Ascent|25'], stokMK['Ascent|5'], rincianAdukan(batchA)]));
ok('koreksi: baris seadukan tidak lengkap (satu baris dihapus sendiri-sendiri) → DITOLAK dengan jalan keluar', (function () { var simpan = cacheMentah('produksi').slice(); pasok('produksiKemasan', simpan.filter(function (p) { return !(p.koreksiDari === dokA[1].id); })); var r = susunKoreksiAdukan(batchA, '1.400.000', 'x', WA); pasok('produksiKemasan', simpan); return /seharusnya punya 2 baris hasil, yang masih berlaku cuma 1/.test(r.tolak || ''); })());
var SB = susunSimpanAdukan(dBongkar, WA, {});
ok('bongkar kemasan jadi: 1 × Ascent 25 kg (modal 325.000) → 5 × Ascent 5 kg + 5 kantong: nilai bahan 325.000, sumberKemasanList di dokumen pertama dengan hppPerUnitSaatDipakai, kgKemasanDipakai 25, merkSumber "DARI KEMASAN JADI: …"; sesudah tersimpan Ascent 25 kg sisa 1 (unit dibongkar hilang)',
  !SB.tolak && SB.hitung.nilaiBahan === 325000 && SB.dokumen[0].data.sumberKemasanList.length === 1 && SB.dokumen[0].data.sumberKemasanList[0].hppPerUnitSaatDipakai === 325000 && SB.dokumen[0].data.sumberKemasanList[0].unit === 1 && SB.dokumen[0].data.kgKemasanDipakai === 25 && SB.dokumen[0].data.kgDipakai === 0 && SB.dokumen[0].data.merkSumber === 'DARI KEMASAN JADI: Ascent 25kg'
  && (function () { adTerapkan(SB); return hitungStokKemasan()['Ascent|25'].sisaUnit === 1 && hitungStokKemasan()['Ascent|5'].sisaUnit === 15; })(), JSON.stringify([SB.tolak, SB.dokumen[0].data, hitungStokKemasan()['Ascent|25']]));
// ---- KARANTINA ----
pasok('retur', [{ id: 'q1', tanggal: '2026-09-18', jam: '12:00', jenisAsal: 'karung', merkSumber: 'Angsa', totalKg: 41.5, jumlahDikembalikan: 41.5, kondisi: 'tidak_utuh', catatan: 'kualitas', notaAsalId: 'a2' }, { id: 'q2', tanggal: '2026-09-01', jam: '09:00', jenisAsal: 'karung', merkSumber: 'Angsa', totalKg: 10, kondisi: 'tidak_utuh', catatan: 'x' },
  { id: 'q3', tanggal: '2026-09-18', jam: '13:00', jenisAsal: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 2, totalKg: 10, kondisi: 'tidak_utuh', catatan: 'kantong sobek' }]);
pasok('penyesuaianStok', cacheMentah('penyesuaian').filter(function (x) { return !(x.merk === 'Angsa' && String(x.tanggal) >= '2026-09-19'); }));   // sisa cocokkan skenario ST3 di atas — bukan bagian cerita karantina
var KAR0 = cacheMentah('karantina').slice(); pasok('karantina', KAR0.concat([{ id: 'q3', tanggal: '2026-09-18', asalRetur: true, jenisAsal: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, totalKg: 10, catatan: 'kantong sobek', statusTindakan: 'belum_diputuskan' }]));
var KAR1 = cacheMentah('karantina').slice(); var RET1 = cacheMentah('retur').slice(); var PS1 = cacheMentah('penyesuaian').slice(); var PR1 = cacheMentah('produksi').slice();
var pulih = function () { pasok('karantina', KAR1); pasok('retur', RET1); pasok('penyesuaianStok', PS1); pasok('produksiKemasan', PR1); };
var angsaSisa0 = hitungStokKarungPerMerk().Angsa.sisaKg; var kembangSisa0 = hitungStokKemasan()['Kembang|5'].sisaUnit;
var DQ = daftarKarantina(WA); var q1 = DQ.antre.find(function (x) { return x.id === 'q1'; }); var q3 = DQ.antre.find(function (x) { return x.id === 'q3'; });
ok('karantina: antrean = yang belum diputuskan saja (q1 Angsa 41,5 kg, q3 Kembang 5 kg 2 unit), q2 (dibuang) di riwayat; keempat pilihan BOLEH untuk q1 dengan kalimat akibatnya; layak jual menyebut +41,5 kg & taksiran laba naik; buang menyebut kerugian SUDAH tercatat',
  DQ.antre.length === 2 && q1 && q3 && q3.jumlah === 2 && q3.satuan === 'unit' && DQ.riwayat.some(function (x) { return x.id === 'q2' && x.label === 'dibuang'; }) && q1.pilihan.every(function (p) { return p.bisa; }) && /\+41,5 kg/.test(q1.pilihan[0].akibat) && /laba & margin tanggal retur naik ±Rp/.test(q1.pilihan[0].akibat) && /SUDAH tercatat/.test(q1.pilihan[3].akibat), JSON.stringify(DQ));
var PB = susunPutusKarantina('q1', 'dibuang', '', WA);
ok('buang: ketukan pertama DITANYA (perluYakin dibuang) dengan kalimat jujur (tidak mengubah laba); ketukan kedua → SATU dokumen karantina statusTindakan dibuang + tanggalKeputusan, tanpa dokumen stok/laba',
  PB.perluYakin === 'dibuang' && /TIDAK mengubah laba/.test(PB.tolak) && (function () { var r = susunPutusKarantina('q1', 'dibuang', '', WA, 'dibuang'); return r.dokumen.length === 1 && r.dokumen[0].koleksi === 'karantina' && r.dokumen[0].data.statusTindakan === 'dibuang' && r.dokumen[0].data.tanggalKeputusan === '2026-09-19' && /laba & kas tidak berubah/.test(r.patch.kabar); })(), JSON.stringify(PB));
var RW = susunPutusKarantina('q1', 'dirework', '', WA);
ok('rework karung: dokumen penyesuaianStok dariRework {merk Angsa, kgSistem/kgFisik null, selisihKg 41,5, nilaiRp 0, hppPerKgSaatOpname 0, alasan "retur id q1)"} DULU lalu status; sesudah diterapkan Angsa +41,5 kg, modal per kg tetap, BUKAN hitungan fisik (tidak mengganggu cocokkan)',
  !RW.tolak && RW.dokumen.length === 2 && RW.dokumen[0].koleksi === 'penyesuaianStok' && RW.dokumen[0].data.dariRework === true && RW.dokumen[0].data.kgSistem === null && RW.dokumen[0].data.kgFisik === null && RW.dokumen[0].data.selisihKg === 41.5 && RW.dokumen[0].data.nilaiRp === 0 && RW.dokumen[0].data.hppPerKgSaatOpname === 0 && /retur id q1\)/.test(RW.dokumen[0].data.alasan) && RW.dokumen[1].data.statusTindakan === 'dirework'
  && (function () { var hpp0 = hitungStokKarungPerMerk().Angsa.hppTerakhirPerKg; adTerapkan(RW); var st = hitungStokKarungPerMerk().Angsa; var r = Math.abs(st.sisaKg - (angsaSisa0 + 41.5)) < 1e-6 && st.hppTerakhirPerKg === hpp0 && !hitunganFisik(RW.dokumen[0].data) && !daftarKarantina(WA).antre.some(function (x) { return x.id === 'q1'; }); pulih(); return r; })(), JSON.stringify(RW));
var RK = susunPutusKarantina('q3', 'dirework', '', WA);
ok('rework kemasan: dokumen produksiKemasan tanpa bahan {merkSumber null, kgDipakai 0, jumlahUnit 2 (10 kg / 5), hppPerUnit = rata-rata Kembang 5 kg sekarang 66.000, catatan "Hasil rework dari karantina (retur id q3)"} — kolom PERSIS putuskanKarantina; sesudah diterapkan Kembang 5 kg +2 unit, rata-rata tetap 66.000; tampil di buku adukan sebagai rework yang TIDAK bisa dihapus/dikoreksi di situ',
  !RK.tolak && RK.dokumen[0].koleksi === 'produksiKemasan' && Object.keys(RK.dokumen[0].data).sort().join(',') === ['id', 'tanggal', 'merkSumber', 'kgDipakai', 'namaProduk', 'ukuranKemasan', 'jumlahUnit', 'biayaKemasan', 'upahRepacking', 'hppSumberPerKgDipakai', 'hppPerUnit', 'catatan'].sort().join(',') && RK.dokumen[0].data.jumlahUnit === 2 && RK.dokumen[0].data.hppPerUnit === 66000 && RK.dokumen[0].data.merkSumber === null
  && (function () { adTerapkan(RK); var st = hitungStokKemasan()['Kembang|5']; var rid = String(RK.dokumen[0].data.id); var d = daftarAdukan(50).find(function (x) { return x.batch === rid; }); var rc = rincianAdukan(rid); var r = st.sisaUnit === kembangSisa0 + 2 && st.hppRataRataPerUnit === 66000 && d && d.jenis === 'rework' && rc && !rc.bisaHapus && !rc.bisaKoreksi && /Karantina/.test(rc.takBisaHapus); pulih(); return r; })(), JSON.stringify(RK));
var LJ0 = susunPutusKarantina('q1', 'layak_jual', '', WA); var LJ = susunPutusKarantina('q1', 'layak_jual', 'ternyata cuma sebagian yang kembali, berasnya bagus', WA);
ok('layak jual: alasan WAJIB; → 2 dokumen: retur kondisi utuh + koreksiKondisi {dari tidak_utuh, alasan, pada, oleh} dan kartu layak_jual ber-catatanKeputusan; TIDAK ada dokumen stok; sesudah diterapkan mesin lama membaca Angsa +41,5 kg lewat retur utuh',
  /alasan/.test(LJ0.tolak || '') && !LJ.tolak && LJ.dokumen.length === 2 && LJ.dokumen[0].koleksi === 'retur' && LJ.dokumen[0].data.kondisi === 'utuh' && LJ.dokumen[0].data.koreksiKondisi.dari === 'tidak_utuh' && LJ.dokumen[0].data.koreksiKondisi.alasan === 'ternyata cuma sebagian yang kembali, berasnya bagus' && LJ.dokumen[0].data.koreksiKondisi.pada === WA.kini && LJ.dokumen[1].data.statusTindakan === 'layak_jual' && LJ.dokumen[1].data.catatanKeputusan === LJ.dokumen[0].data.koreksiKondisi.alasan
  && (function () { adTerapkan(LJ); var r = Math.abs(hitungStokKarungPerMerk().Angsa.sisaKg - (angsaSisa0 + 41.5)) < 1e-6; return r; })(), JSON.stringify(LJ));
// keadaan: retur q1 sudah utuh & kartu layak_jual → kartu dibuka lagi (menyusul dari perangkat lain)
pasok('karantina', cacheMentah('karantina').map(function (k) { return k.id === 'q1' ? Object.assign({}, k, { statusTindakan: 'belum_diputuskan' }) : k; }));
var DQ2 = daftarKarantina(WA); var q1b = DQ2.antre.find(function (x) { return x.id === 'q1'; });
ok('retur sudah utuh: rework / buang / balik DITOLAK (barang sudah kembali lewat koreksi) dan pilihan yang TAMPIL memakai penjaga yang SAMA dengan yang menulis (kalimat identik); layak jual = menutup kartu saja (1 dokumen, "kartu menyusul", stok tidak bertambah)',
  q1b && q1b.returUtuh && !q1b.pilihan[3].bisa && q1b.pilihan[3].sebab === susunPutusKarantina('q1', 'dibuang', '', WA, 'dibuang').tolak && /LAYAK JUAL/.test(q1b.pilihan[1].sebab) && q1b.pilihan[0].bisa
  && (function () { var r = susunPutusKarantina('q1', 'layak_jual', '', WA); return r.dokumen.length === 1 && r.dokumen[0].data.catatanKeputusan === 'kartu menyusul sesudah koreksi' && /stok tidak bertambah lagi/.test(r.patch.kabar); })(), JSON.stringify(q1b));
pulih();
// sudah pernah di-rework (dokumen rework ada, status kartu belum sampai)
pasok('penyesuaianStok', cacheMentah('penyesuaian').concat([{ id: 'rw1', tanggal: '2026-09-18', merk: 'Angsa', kgSistem: null, kgFisik: null, selisihKg: 41.5, alasan: 'Rework dari karantina (retur id q1)', nilaiRp: 0, dariRework: true }]));
ok('sudah pernah di-rework (dokumennya ada walau kartu masih terbuka): layak jual DITOLAK & rework kedua DITOLAK — stok tidak dihitung dua kali', /SUDAH pernah di-rework/.test(susunPutusKarantina('q1', 'layak_jual', 'x', WA).tolak || '') && /Sudah pernah di-rework/.test(susunPutusKarantina('q1', 'dirework', '', WA).tolak || ''), JSON.stringify([susunPutusKarantina('q1', 'layak_jual', 'x', WA).tolak, susunPutusKarantina('q1', 'dirework', '', WA).tolak]));
pulih();
// cocokkan SESUDAH retur → ditanya
pasok('penyesuaianStok', cacheMentah('penyesuaian').concat([{ id: 'o9', tanggal: '2026-09-19', jam: '09:00', merk: 'Angsa', kgSistem: 100, kgFisik: 100, selisihKg: 0 }]));
ok('layak jual saat ada COCOKKAN sesudah retur: DITANYA (perluYakin layak_jual) menyebut tanggal cocokkannya; ketukan kedua boleh; antrean menyebut opname sesudahnya', susunPutusKarantina('q1', 'layak_jual', 'x', WA).perluYakin === 'layak_jual' && /2026-09-19 09:00/.test(susunPutusKarantina('q1', 'layak_jual', 'x', WA).tolak) && !susunPutusKarantina('q1', 'layak_jual', 'x', WA, 'layak_jual').tolak && daftarKarantina(WA).antre.find(function (x) { return x.id === 'q1'; }).opnameSesudah.length === 1, susunPutusKarantina('q1', 'layak_jual', 'x', WA).tolak);
pulih();
pasok('retur', cacheMentah('retur').map(function (r) { return r.id === 'q1' ? Object.assign({}, r, { tanggal: '2025-12-30' }) : r; }));
ok('layak jual untuk retur TAHUN LAIN (sudah/akan ditutup buku) DITOLAK; karung tanpa nama asal tidak bisa di-rework (disebut jalan keluarnya); kartu yang sudah diputuskan ditolak untuk semua tindakan',
  /tahun lain/.test(susunPutusKarantina('q1', 'layak_jual', 'x', WA).tolak || '') && (function () { pasok('karantina', cacheMentah('karantina').map(function (k) { return k.id === 'q1' ? Object.assign({}, k, { merkSumber: null }) : k; })); var r = /nama asalnya/.test(susunPutusKarantina('q1', 'dirework', '', WA).tolak || ''); pulih(); return r; })() && /sudah diputuskan/.test(susunPutusKarantina('q2', 'dibuang', '', WA, 'dibuang').tolak || ''), JSON.stringify([susunPutusKarantina('q1', 'layak_jual', 'x', WA).tolak, susunPutusKarantina('q2', 'dibuang', '', WA, 'dibuang').tolak]));
pulih();
// ================= PUTARAN 16: KANTONG (ST4) =================
// keadaan dipulihkan ke KOTAK awal — skenario sebelumnya mengganti cache kantong, batch, adukan
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); }); Object.keys(KOTAK16).forEach(function (n) { pasok(n, KOTAK16[n]); }); ['aturanToko', 'koreksiHpp', 'pindahTempat', 'bukuHapus', 'retur'].forEach(function (n) { pasok(n, []); });
var WK = { tanggal: '2026-09-19', jam: '10:30', kini: '2026-09-19T03:30:00.000Z', idUnik: function () { return 2000 + Math.floor(Math.random() * 1e6); } };
var RK = rakKantong(); function rk(j) { return RK.daftar.find(function (x) { return x.jenis === j; }); }
ok('ST4 rak: karung bekas TIDAK ada (hasil samping); 5 kg Kembang/BMW sisa 488 (300+200−12), harga terakhir 1.125 (batch 11 Agu, bukan rata-rata 1.080), cukup 569 hari', !rk('karungbekas') && rk('5kg_kembangbmw').sisa === 488 && rk('5kg_kembangbmw').hargaAkhir === 1125 && rk('5kg_kembangbmw').dariRata === false && Math.floor(rk('5kg_kembangbmw').hariCukup) === 569 && !rk('5kg_kembangbmw').awas, JSON.stringify(rk('5kg_kembangbmw')));
ok('ST4 rak: 10 kg Putri Agri/Lele sisa 20, laju 60/14 → cukup 4 hari < 7 → AWAS, rakKet menyebutnya & setelan owner', rk('10kg_putriagri_lele').awas === true && Math.floor(rk('10kg_putriagri_lele').hariCukup) === 4 && RK.awas.length === 1 && /Putri Agri\/Lele 10 kg cukup 4 hari/.test(RK.rakKet) && /di bawah 7 hari/.test(RK.rakKet), RK.rakKet);
ok('ST4 rak: jenis tanpa pemakaian 14 hari → "lajunya belum bisa dihitung" (bukan cukup 0 hari); tinggi tumpukan relatif ke terbanyak (paper bag 900 = 1)', /belum bisa dihitung/.test(rk('paperbag10l').teksHari) && rk('paperbag10l').hariCukup === null && rk('paperbag10l').tinggi === 1 && rk('10kg_putriagri_lele').tinggi < 0.1, JSON.stringify([rk('paperbag10l').teksHari, rk('10kg_putriagri_lele').tinggi]));
ok('ST4 rak: harga dokumen lama = total ÷ jumlah (paper bag 355.500/900 = 395); jenis yang belum pernah dibeli & tanpa buku → belum ada harga', rk('paperbag10l').hargaAkhir === 395 && rk('5kg_putriagri').hargaAkhir === 0 && /belum ada harga/.test(rk('5kg_putriagri').teksHarga), JSON.stringify(rk('5kg_putriagri')));
var HB = hitungBeli({ jenis: '5kg_kembangbmw', jumlah: '1000', harga: '1', toko: '' });
ok('ST4 beli Rp1/lembar: pita "per LEMBAR?" (kejadian sistem lama); simpan ketukan pertama cuma bertanya (perluYakin murah)', HB.murah && /per LEMBAR\?/.test(HB.murahTeks) && susunSimpanBeli({ jenis: '5kg_kembangbmw', jumlah: '1000', harga: '1' }, WK, {}).perluYakin === 'murah', JSON.stringify(HB));
HB = hitungBeli({ jenis: '5kg_kembangbmw', jumlah: '1.000', harga: '1.300' });
ok('ST4 beli 1.300: murah gugur, lonjakan 1.125 → 1.300 = 16 % > 15 % ditandai; total 1.300.000', !HB.murah && HB.lonjak && HB.lonjakPct === 16 && HB.total === 1300000 && /naik 16 %/.test(HB.lonjakTeks), JSON.stringify(HB));
var SB = susunSimpanBeli({ jenis: '5kg_kembangbmw', jumlah: '1.000', harga: '1.300', toko: 'Toko Kemasan Contoh' }, WK, {});
ok('ST4 lonjakan: ketukan pertama bertanya', SB.perluYakin === 'lonjak' && /[Kk]etuk sekali lagi/.test(SB.tolak), SB.tolak);
SB = susunSimpanBeli({ jenis: '5kg_kembangbmw', jumlah: '1.000', harga: '1.300', toko: 'Toko Kemasan Contoh' }, WK, { lonjak: true });
ok('ST4 tersimpan: dokumen stokBahanKemasan {tipe beli, jenis, jumlah 1000, hargaTotal 1.300.000, hargaPerPcs 1.300 (yang DIKETIK), tanggal, jam, toko} — bentuk simpanBeliBahanKemasan + kolom baru', SB.dokumen && SB.dokumen[0].koleksi === 'stokBahanKemasan' && SB.dokumen[0].data.tipe === 'beli' && SB.dokumen[0].data.jumlah === 1000 && SB.dokumen[0].data.hargaTotal === 1300000 && SB.dokumen[0].data.hargaPerPcs === 1300 && SB.dokumen[0].data.toko === 'Toko Kemasan Contoh' && /keluar dari laci/.test(SB.patch.kabar), JSON.stringify(SB));
terapkanKeCache(SB.dokumen);
ok('ST4 sesudah tersimpan: mesin membaca sisa 1.488; harga terakhir 1.300', hitungStokBahanKemasan()['5kg_kembangbmw'].sisaPcs === 1488 && rakKantong().daftar.find(function (x) { return x.jenis === '5kg_kembangbmw'; }).hargaAkhir === 1300, JSON.stringify(hitungStokBahanKemasan()['5kg_kembangbmw']));
var RH = riwayatHarga().find(function (r) { return r.jenis === '5kg_kembangbmw'; });
ok('ST4 riwayat harga 5 kg: 3 kali beli 1.050 → 1.125 → 1.300; lonjakan ▲ 16 % di beli ketiga saja (1.050→1.125 = 7 %)', RH.baris.length === 3 && RH.baris.map(function (b) { return b.harga; }).join() === '1050,1125,1300' && RH.baris[2].lonjak === '▲ 16 %' && RH.baris[1].lonjak === '' && /3 kali beli/.test(RH.ket), JSON.stringify(RH));
var idBaru = SB.dokumen[0].data.id; var BB = bukuBeli(10);
ok('ST4 buku beli: batch baru paling atas dengan toko & harga; dokumen lama ditandai lama (harga = total ÷ jumlah)', BB[0].id === idBaru && BB[0].toko === 'Toko Kemasan Contoh' && BB[0].harga === 1300 && !BB[0].lama && BB.find(function (b) { return b.id === 1001; }).lama === true && BB.find(function (b) { return b.id === 1001; }).harga === 1050, JSON.stringify(BB.slice(0, 2)));
var HP1 = susunHapusBeli(1004, 'coba', WK, true);
ok('ST4 hapus batch 10 kg (80 lembar) DITOLAK: sisa 20 − 80 < 0 → lembarnya sudah terpakai; arahannya Cocokkan', /sudah terpakai/.test(HP1.tolak) && /Cocokkan/.test(HP1.tolak), HP1.tolak);
ok('ST4 hapus tanpa alasan ditolak; ketukan pertama bertanya (menyebut uang kembali ke laci); pemakaian tidak bisa dihapus dari sini', /butuh alasan/.test(susunHapusBeli(idBaru, '', WK, false).tolak) && susunHapusBeli(idBaru, 'salah jenis', WK, false).perluYakin === true && /kembali ke laci/.test(susunHapusBeli(idBaru, 'salah jenis', WK, false).tolak) && /hanya catatan BELI/.test(susunHapusBeli(1003, 'x', WK, true).tolak));
var HP2 = susunHapusBeli(idBaru, 'salah jenis', WK, true);
ok('ST4 hapus sah: hapus dokumen beli + jejak bukuHapus (koleksi stokBahanKemasan, ringkas, alasan)', HP2.hapus.length === 1 && HP2.hapus[0].id === idBaru && HP2.dokumen[0].koleksi === 'bukuHapus' && HP2.dokumen[0].data.koleksi === 'stokBahanKemasan' && /1\.000 lembar Kantong Kembang\/BMW 5 kg/.test(HP2.dokumen[0].data.ringkas) && HP2.dokumen[0].data.alasan === 'salah jenis', JSON.stringify(HP2));
terapkanKeCache([{ koleksi: 'stokBahanKemasan', hapus: idBaru }]);
ok('ST4 sesudah dihapus: sisa kembali 488, harga terakhir kembali 1.125 (turunan dokumen, bukan disimpan)', hitungStokBahanKemasan()['5kg_kembangbmw'].sisaPcs === 488 && rakKantong().daftar.find(function (x) { return x.jenis === '5kg_kembangbmw'; }).hargaAkhir === 1125);
ok('ST4 atur: lonjakan 30 % → 16 % tidak ditanya; stok aman 3 hari → 10 kg (4,7 hari) tidak lagi awas; lantai 2.000 → 1.300 ditanya murah; nilai di luar batas ditolak', (function () { var A = susunAturKantong({ lonjakan: '30', hariAman: '3', lantaiHarga: '2000' }, WK); if (A.tolak) return false; terapkanKeCache(A.dokumen);
  var r = !hitungBeli({ jenis: '5kg_kembangbmw', jumlah: '10', harga: '1300' }).lonjak && rakKantong().daftar.find(function (x) { return x.jenis === '10kg_putriagri_lele'; }).awas === false && hitungBeli({ jenis: '5kg_kembangbmw', jumlah: '10', harga: '1300' }).murah === true && /0–100/.test(susunAturKantong({ lonjakan: '150' }, WK).tolak) && /0–365/.test(susunAturKantong({ hariAman: '700' }, WK).tolak);
  terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'kantong' }]); return r; })());

// ================= PUTARAN 16: TEMPAT SIMPAN (ST5) =================
var TP = susunTempat(); function tp(nm) { return TP.tempat.find(function (t) { return t.nama === nm; }); }
ok('ST5 awal: peta sistem lama dibaca (Angsa di "rak depan", tempat cuma teks → tanpa kotak) + 9 tempat BAWAAN dari foto toko (owner belum menyimpan daftar) yang semuanya berkotak & kosong; Pandan Wangi, IR64 Apex, Kembang 5 kg tanpa tempat', TP.tempat.length === 1 + TEMPAT_BAWAAN.length && TEMPAT_BAWAAN.every(function (b) { return tp(b.nama) && tp(b.nama).kotak && tp(b.nama).n === 0; }) && tp('rak depan').isi.length === 1 && tp('rak depan').isi[0].nama === 'Angsa' && !tp('rak depan').kotak && TP.tanpaTempat.n === 3 && /Pandan Wangi/.test(TP.tanpaTempat.teks) && TP.zona.length === TEMPAT_BAWAAN.length, JSON.stringify([TP.tempat, TP.tanpaTempat.teks]));
ok('ST5 nilai: rak depan memegang Angsa 90 kg × 13.045 dari nilai semua → persen < 50, tidak menumpuk', Math.abs(tp('rak depan').nilai - 90 * 14350000 / 1100) < 0.01 && tp('rak depan').pct === Math.round(tp('rak depan').nilai / TP.nilaiSemua * 100) && tp('rak depan').tumpuk === false && /tersebar/.test(TP.tumpukKet), TP.tumpukKet);
ok('ST5 pindah ke tempat yang belum ada di daftar DITOLAK; ke tempat yang sama ditolak halus', /belum ada di daftar/.test(susunPindah('K:Pandan Wangi', 'gudang belakang', WK).tolak) && /memang sudah di rak depan/.test(susunPindah('K:Angsa', 'rak depan', WK).tolak));
var AT = susunAturTempat({ daftar: [{ nama: 'rak depan', posisi: 'kiri-bawah' }, { nama: 'gudang belakang', posisi: 'atas' }, { nama: 'teras', posisi: '' }], batasTumpuk: '50' }, WK);
ok('ST5 atur: 3 tempat (2 berkotak) tersimpan di aturanToko/tempat', !AT.tolak && AT.dokumen[0].data.id === 'tempat' && AT.dokumen[0].data.daftar.length === 3, JSON.stringify(AT));
terapkanKeCache(AT.dokumen); TP = susunTempat();
ok('ST5 denah: 2 zona berkotak (gaya persen; kunci kotak LAMA "atas" → belakang, "kiri-bawah" → kiri depan) + 1 tanpa kotak (teras); sesudah owner menyimpan daftar, tempat bawaan tidak ditambahkan lagi', TP.zona.length === 2 && /left: 3%; top: 2%; width: 94%/.test(tp('gudang belakang').gaya) && /top: 55%/.test(tp('rak depan').gaya) && tpPosisi('atas') === 'belakang' && tpPosisi('ngawur') === '' && TP.tanpaKotak.length === 1 && TP.tanpaKotak[0].nama === 'teras' && TP.tempat.length === 3, JSON.stringify(TP.zona.map(function (z) { return z.nama + '|' + z.gaya; })));
ok('ST5 atur ditolak: nama kosong / kembar / kotak dipakai dua tempat / batas 0', /kosong/.test(susunAturTempat({ daftar: [{ nama: ' ' }] }, WK).tolak) && /dua kali/.test(susunAturTempat({ daftar: [{ nama: 'A' }, { nama: 'a' }] }, WK).tolak) && /dipakai dua tempat/.test(susunAturTempat({ daftar: [{ nama: 'A', posisi: 'atas' }, { nama: 'B', posisi: 'atas' }] }, WK).tolak) && /1–100/.test(susunAturTempat({ daftar: [{ nama: 'rak depan' }], batasTumpuk: '0' }, WK).tolak));
var PD = susunPindah('K:Pandan Wangi', 'gudang belakang', WK);
ok('ST5 pindah Pandan Wangi → gudang belakang: dokumen pengaturan/tempatSimpan {peta} (bentuk sistem lama, kunci K:nama) + catatan pindahTempat; kabar: stok & modal tidak berubah', PD.dokumen.length === 2 && PD.dokumen[0].koleksi === 'pengaturan' && PD.dokumen[0].data.id === 'tempatSimpan' && PD.dokumen[0].data.peta['K:Pandan Wangi'] === 'gudang belakang' && PD.dokumen[0].data.peta['K:Angsa'] === 'rak depan' && PD.dokumen[1].koleksi === 'pindahTempat' && PD.dokumen[1].data.dari === '' && PD.dokumen[1].data.ke === 'gudang belakang' && /stok & modal tidak berubah/.test(PD.patch.kabar), JSON.stringify(PD));
var stokSblmPindah = JSON.stringify(hitungStokKarungPerMerk()); terapkanKeCache(PD.dokumen); TP = susunTempat();
ok('ST5 sesudah pindah: gudang belakang berisi Pandan Wangi 200 kg = 3.200.000 = persen dari nilai semua (36 % < 50 → belum menumpuk); mesin stok tidak bergeser; riwayat pindahan 1', tp('gudang belakang').isi.length === 1 && Math.abs(tp('gudang belakang').nilai - 3200000) < 0.01 && tp('gudang belakang').pct === Math.round(3200000 / TP.nilaiSemua * 100) && tp('gudang belakang').tumpuk === false && JSON.stringify(hitungStokKarungPerMerk()) === stokSblmPindah && riwayatPindah('2026-09-19').length === 1, JSON.stringify([tp('gudang belakang').pct, TP.tumpukKet]));
ok('ST5 batas menumpuk owner 30 % → gudang belakang (36 %) MENUMPUK & disebut dengan setelannya', (function () { var A = susunAturTempat({ daftar: [{ nama: 'rak depan', posisi: 'kiri-bawah' }, { nama: 'gudang belakang', posisi: 'atas' }, { nama: 'teras' }], batasTumpuk: '30' }, WK); terapkanKeCache(A.dokumen); var T2 = susunTempat(); var g = T2.tempat.find(function (t) { return t.nama === 'gudang belakang'; }); return g.tumpuk === true && /gudang belakang \d+ % memegang nilai rak di atas 30 %/.test(T2.tumpukKet); })());
var PD2 = susunPindah('K:Angsa', '', WK); ok('ST5 dikosongkan = kuncinya DIBUANG dari peta (bukan string kosong)', !('K:Angsa' in PD2.dokumen[0].data.peta) && PD2.dokumen[1].data.ke === '' && PD2.dokumen[1].data.dari === 'rak depan', JSON.stringify(PD2.dokumen[0].data.peta));
ok('ST5 hapus tempat yang masih berisi DITOLAK (gudang belakang berisi Pandan Wangi); tempat kosong boleh dilepas', /masih berisi 1 barang/.test(susunAturTempat({ daftar: [{ nama: 'rak depan' }] }, WK).tolak) && !susunAturTempat({ daftar: [{ nama: 'rak depan' }, { nama: 'gudang belakang', posisi: 'atas' }] }, WK).tolak);
// ---- PUTARAN 22 (owner 23 Sep): tumpukan 3D, geser urutan, tempat berisi boleh dilepas dengan ketukan kedua, zona kasir
var T3 = susunTumpukan(); var zRD = T3.zona.find(function (z) { return z.nama === 'rak depan'; }); var zGB = T3.zona.find(function (z) { return z.nama === 'gudang belakang'; });
ok('P22 tumpukan 3D: tiap tempat berkotak jadi lantai isometrik dengan tumpukan per barang; rak depan memegang Angsa → tinggi = banyak karung menurut rantai stok (tumpukanGudang), gudang belakang memegang Pandan Wangi; koordinat lantai = kotak denah (dalam × 4/3); tpIso menaruh titik jauh di atas titik dekat', !!zRD && zRD.stacks.length === 1 && zRD.stacks[0].nama === 'Angsa' && zRD.stacks[0].karung === tumpukanGudang('Angsa').karung && zRD.stacks[0].lapis === Math.min(TP_LAPIS_MAKS, zRD.stacks[0].karung) && !!zGB && zGB.stacks[0].nama === 'Pandan Wangi'
  && Math.abs(zGB.y - 2 * 4 / 3) < 0.01 && Math.abs(zGB.d - 9 * 4 / 3) < 0.01 && tpIso(0, 0, 0).sy < tpIso(50, 50, 0).sy && tpIso(10, 0, 0).sx > 0 && tpIso(0, 10, 0).sx < 0 && tpIso(0, 0, 5).sy === -5 && T3.tanpaTempat.length === 2, JSON.stringify([zRD && zRD.stacks, zGB && [zGB.y, zGB.d], T3.tanpaTempat.map(function (x) { return x.nama; })]));
terapkanKeCache(susunPindah('K:IR64 Apex', 'rak depan', WK).dokumen); T3 = susunTumpukan(); zRD = T3.zona.find(function (z) { return z.nama === 'rak depan'; });
ok('P22 geser: Apex dipindah ke rak depan → dua tumpukan (Angsa, IR64 Apex urut nama); geser Apex ke depan → aturanToko/tempat.susunan menyimpan urutan & Apex jadi pertama; di ujung ditolak "Sudah di ujung"; daftar & batas tidak berubah', zRD.stacks.length === 2 && zRD.stacks[0].nama === 'Angsa' && (function () { var G = susunGeserTumpukan('K:IR64 Apex', -1, WK); if (G.tolak) return false; terapkanKeCache(G.dokumen); var z2 = susunTumpukan().zona.find(function (z) { return z.nama === 'rak depan'; }); var A = aturTempat();
  return z2.stacks[0].nama === 'IR64 Apex' && z2.stacks[0].urut === 0 && A.susunan['K:IR64 Apex'] === 0 && A.susunan['K:Angsa'] === 1 && A.daftar.length === 3 && /Sudah di ujung/.test(susunGeserTumpukan('K:IR64 Apex', -1, WK).tolak); })(), JSON.stringify(susunTumpukan().zona.find(function (z) { return z.nama === 'rak depan'; }).stacks.map(function (x) { return x.nama; })));
terapkanKeCache(susunPindah('K:IR64 Apex', '', WK).dokumen);
ok('P22 zona: "bangku-kiri" lama → kasir (meja owner, kiri pintu); "meja" lama → kanan depan; kotak kasir ada di POSISI_DENAH', tpPosisi('bangku-kiri') === 'kasir' && tpPosisi('meja') === 'kanan-depan' && POSISI_DENAH.some(function (p) { return p[0] === 'kasir' && /kasir/.test(p[1]); }) && !POSISI_DENAH.some(function (p) { return p[0] === 'meja'; }));
var LP1 = susunAturTempat({ daftar: [{ nama: 'rak depan', posisi: 'kiri-bawah' }, { nama: 'teras' }], batasTumpuk: '90' }, WK);
ok('P22 lepas tempat berisi: ketukan pertama DITANYA (perluYakin, menyebut isinya); ketukan kedua (yakin) → daftar tanpa tempat itu + peta tempatSimpan tanpa kunci barangnya + catatan pindahTempat bertanda tempatDihapus; Pandan Wangi jadi tanpa tempat, stok tidak berubah', /masih berisi 1 barang/.test(LP1.tolak) && LP1.perluYakin === true && (function () { var st0 = JSON.stringify(hitungStokKarungPerMerk()); var R = susunAturTempat({ daftar: [{ nama: 'rak depan', posisi: 'kiri-bawah' }, { nama: 'teras' }], batasTumpuk: '90', yakin: true }, WK); if (R.tolak) return false;
  var pd = R.dokumen.find(function (d) { return d.koleksi === 'pindahTempat'; }); var pt = R.dokumen.find(function (d) { return d.koleksi === 'pengaturan'; }); terapkanKeCache(R.dokumen); var T = susunTempat();
  var r = pd && pd.data.barang === 'Pandan Wangi' && pd.data.tempatDihapus === true && pt && !('K:Pandan Wangi' in pt.data.peta) && T.tempat.length === 2 && T.tanpaTempat.isi.some(function (b) { return b.nama === 'Pandan Wangi'; }) && JSON.stringify(hitungStokKarungPerMerk()) === st0;
  terapkanKeCache(susunAturTempat({ daftar: [{ nama: 'rak depan', posisi: 'kiri-bawah' }, { nama: 'gudang belakang', posisi: 'atas' }, { nama: 'teras' }], batasTumpuk: '90' }, WK).dokumen); terapkanKeCache(susunPindah('K:Pandan Wangi', 'gudang belakang', WK).dokumen); return r; })(), JSON.stringify(LP1));
ok('ST5 batas menumpuk owner 90 % → gudang belakang tidak lagi ditandai', (function () { var A = susunAturTempat({ daftar: [{ nama: 'rak depan' }, { nama: 'gudang belakang', posisi: 'atas' }, { nama: 'teras' }], batasTumpuk: '90' }, WK); terapkanKeCache(A.dokumen); return susunTempat().tempat.find(function (t) { return t.nama === 'gudang belakang'; }).tumpuk === false; })());
terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'tempat' }, { koleksi: 'pengaturan', data: { id: 'tempatSimpan', peta: { 'K:Angsa': 'rak depan' } } }]); cacheMentah('pindahTempat').slice().forEach(function (x) { terapkanKeCache([{ koleksi: 'pindahTempat', hapus: x.id }]); });

// ================= PUTARAN 16: HPP (ST6) =================
// kasus pembeda: b4 = kedatangan BERBONGKAR (Ketan Contoh 250 kg @18.000 + bongkar 25.000 → HPP 18.100/kg); b5 = merk yang cuma punya batch FONDASI (stok awal)
pasok('batchMasuk', KOTAK.batchMasuk.concat([{ id: 'b4', tanggal: '2026-09-05', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 25000, merkList: [{ merk: 'Ketan Contoh', satuan: 'karung', beratKarung: 25, jumlahKarung: 10, totalKg: 250, subtotalHarga: 4500000, hargaPerKg: 18000 }] },
  { id: 'b5', tanggal: '2026-08-08', stokAwal: true, biayaBongkar: 0, merkList: [{ merk: 'Beras Awal Contoh', satuan: 'karung', beratKarung: 50, jumlahKarung: 4, totalKg: 200, subtotalHarga: 2400000, hargaPerKg: 12000 }] }]));
var KH = kartuHpp(); function kh(m) { return KH.kartu.find(function (k) { return k.merk === m; }); }
ok('ST6 rumus replika = mesin: Σ nilai ÷ Σ kg tiap nama sama dengan hppTerakhirPerKg mesin, TERMASUK kedatangan berbongkar (Ketan Contoh 18.100 = 18.000 + 25.000/250) — penjaga yang berbunyi bila rumus mesin berubah', Object.keys(hitungStokKarungPerMerk()).every(function (m) { return Math.abs(totalMasuk(m).rata - hitungStokKarungPerMerk()[m].hppTerakhirPerKg) < 1e-6; }) && Math.abs(totalMasuk('Ketan Contoh').rata - 18100) < 1e-6 && Math.abs(hitungStokKarungPerMerk()['Ketan Contoh'].hppTerakhirPerKg - 18100) < 1e-6, JSON.stringify([totalMasuk('Ketan Contoh'), hitungStokKarungPerMerk()['Ketan Contoh']]));
ok('ST6 nama yang cuma punya batch FONDASI (stok awal): kartu bisaKoreksi false, nilaiKoreksi DITOLAK menyebut fondasi (tidak diubah dari sini)', kh('Beras Awal Contoh') && kh('Beras Awal Contoh').bisaKoreksi === false && /fondasi/.test(nilaiKoreksi('Beras Awal Contoh', '13000').tolak) && /stok awal \(fondasi\)/.test(kh('Beras Awal Contoh').sumber), JSON.stringify([kh('Beras Awal Contoh'), nilaiKoreksi('Beras Awal Contoh', '13000')]));
ok('ST6 koreksi kedatangan berbongkar: harga 18.000 → 18.500 → HPP kedatangan 18.600 (bongkar 100/kg tetap ikut), teksTarget menyebut bongkar', (function () { var v = nilaiKoreksi('Ketan Contoh', '18500'); return !v.tolak && Math.abs(v.hppBaru - 18600) < 1e-6 && /bongkar Rp100\/kg/.test(v.teksTarget) && Math.abs(v.modalBaru - 18600) < 1e-6; })(), JSON.stringify(nilaiKoreksi('Ketan Contoh', '18500')));
ok('ST6 kartu Angsa: modal rata-rata 13.045,45 (buku), harga beli terbaru 13.500 (aturan owner, pembanding), jual 13.400 → margin 355 untung; nilai rak 90 × modal; sumber = kedatangan terakhir', Math.abs(kh('Angsa').modal - 14350000 / 1100) < 0.001 && kh('Angsa').hargaTerbaru === 13500 && kh('Angsa').jual === 13400 && kh('Angsa').margin === 355 && kh('Angsa').kelasMargin === 'untung' && Math.abs(kh('Angsa').nilaiRak - 90 * 14350000 / 1100) < 0.01 && /kedatangan PEMASOK CONTOH · 2026-09-19/.test(kh('Angsa').sumber), JSON.stringify(kh('Angsa')));
ok('ST6 ambang rugi pakai > bukan >=: IR64 Apex jual 14.000 = modal 14.000 → "margin Rp0/kg (disengaja?)", bukan RUGI; Pandan Wangi tanpa harga jual → disebut, bukan margin 0', kh('IR64 Apex').margin === 0 && kh('IR64 Apex').teksMargin === 'margin Rp0/kg (disengaja?)' && kh('IR64 Apex').kelasMargin === 'nol' && kh('Pandan Wangi').margin === null && /belum ada di katalog/.test(kh('Pandan Wangi').teksMargin) && KH.ringkas.nol === 1 && KH.ringkas.rugi === 0 && /1 margin nol/.test(KH.ringkasTeks), KH.ringkasTeks);
var GW = garisWaktu().find(function (g) { return g.merk === 'Angsa'; });
ok('ST6 garis waktu Angsa: 2 kedatangan (13.000 lalu 13.500), lonjakan 3,8 % < 10 % tidak ditandai; bar terakhir 100 %', GW.baris.length === 2 && GW.baris[0].hpp === 13000 && GW.baris[1].hpp === 13500 && GW.baris[1].lonjak === '' && GW.baris[1].lebar === 100, JSON.stringify(GW));
ok('ST6 nilai koreksi: 1.280 di bawah lantai 5.000 DITOLAK dengan kalimat; 50.000 > 3× modal ditolak; nama tidak dikenal ditolak', /di bawah lantai Rp5\.000/.test(nilaiKoreksi('Angsa', '1280').tolak) && /lebih dari 3× modal/.test(nilaiKoreksi('Angsa', '50000').tolak) && /tidak ada di buku/.test(nilaiKoreksi('Ngawur', '13000').tolak));
var NK = nilaiKoreksi('Angsa', '14.000');
ok('ST6 nilai koreksi Angsa 13.500 → 14.000 pada kedatangan terakhir (b2, 100 kg): modal baru = (14.350.000 + 500 × 100) / 1.100 = 13.090,91; Δ nilai rak = 45,45 × 90 = 4.091; lonjak 0 % tidak ditanya; di atas jual 13.400 → peringatan RUGI 600/kg', !NK.tolak && NK.target.batchId === 'b2' && Math.abs(NK.modalBaru - 14400000 / 1100) < 0.001 && Math.abs(NK.delta - (14400000 / 1100 - 14350000 / 1100) * 90) < 0.01 && NK.lonjak === '' && /RUGI Rp600/.test(NK.rugi) && /naik Rp4\.091/.test(NK.teksDelta), JSON.stringify(NK));
ok('ST6 koreksi tanpa alasan ditolak; harga sama dengan tercatat ditolak', /butuh alasan/.test(susunKoreksiHpp('Angsa', '14000', '', WK).tolak) && /sama dengan yang tercatat/.test(susunKoreksiHpp('Angsa', '13500', 'x', WK).tolak));
var NL = nilaiKoreksi('Angsa', '30000'); var KL = susunKoreksiHpp('Angsa', '30000', 'harga pemasok naik', WK);
ok('ST6 lonjakan: kedatangan terakhir 100 dari 1.100 kg, 13.500 → 30.000 menaikkan modal rata-rata 13.045 → 14.545 = 11 % > 10 % → ditanya (perluYakin), tidak ditulis; 20.000 cuma 4,5 % → tidak ditanya', /naik 1[12] %/.test(NL.lonjak) && KL.perluYakin === true && !KL.dokumen && nilaiKoreksi('Angsa', '20000').lonjak === '', JSON.stringify([NL.lonjak, KL]));
var KK = susunKoreksiHpp('Angsa', '14.000', 'bongkar belum masuk', WK, true);
ok('ST6 koreksi sah: dokumen = batchMasuk b2 yang SAMA (id tetap) dengan hargaPerKg 14.000, subtotal 1.400.000, alasanKoreksi & riwayat "koreksi HPP: …" + jejak koreksiHpp {merk, batchId, hargaDari 13.500, hargaKe 14.000, deltaNilai 4.091, sisaKg 90}', KK.dokumen && KK.dokumen.length === 2 && KK.dokumen[0].koleksi === 'batchMasuk' && KK.dokumen[0].data.id === 'b2' && KK.dokumen[0].data.merkList[0].hargaPerKg === 14000 && KK.dokumen[0].data.merkList[0].subtotalHarga === 1400000 && /koreksi HPP: bongkar belum masuk/.test(KK.dokumen[0].data.alasanKoreksi) && KK.dokumen[1].koleksi === 'koreksiHpp' && KK.dokumen[1].data.hargaDari === 13500 && KK.dokumen[1].data.hargaKe === 14000 && KK.dokumen[1].data.deltaNilai === 4091 && KK.dokumen[1].data.sisaKg === 90, JSON.stringify(KK.dokumen));
terapkanKeCache(KK.dokumen);
ok('ST6 sesudah koreksi: MESIN BEKU membaca modal Angsa = pratinjau (13.090,91), harga beli terbaru 14.000, sisa tetap 90 kg; garis waktu menandai koreksi; log koreksi 1', Math.abs(hitungStokKarungPerMerk().Angsa.hppTerakhirPerKg - NK.modalBaru) < 1e-6 && hitungStokKarungPerMerk().Angsa.hargaTerakhirPerKg === 14000 && hitungStokKarungPerMerk().Angsa.sisaKg === 90 && garisWaktu().find(function (g) { return g.merk === 'Angsa'; }).baris[1].koreksi === true && logKoreksi(5).length === 1, JSON.stringify(hitungStokKarungPerMerk().Angsa));
ok('ST6 kartu sesudahnya: Angsa jual 13.400 − modal 13.090,91 → margin 309 masih untung (yang rugi cuma kedatangan terakhirnya, diperingatkan saat koreksi)', kartuHpp().kartu.find(function (k) { return k.merk === 'Angsa'; }).margin === 309, JSON.stringify(kartuHpp().kartu.find(function (k) { return k.merk === 'Angsa'; })));
var PM = pratinjauMassal({ 'IR64 Apex': '14.500', 'Pandan Wangi': '100' });
ok('ST6 massal: Pandan Wangi 100 ditolak → TIDAK ADA yang disimpan; teks menyebutnya', PM.n === 2 && PM.bermasalah.length === 1 && PM.bermasalah[0].merk === 'Pandan Wangi' && !PM.siap && /TIDAK ADA yang disimpan/.test(PM.teks) && /TIDAK ADA yang disimpan/.test(susunKoreksiMassal({ 'IR64 Apex': '14.500', 'Pandan Wangi': '100' }, 'x', WK).tolak), PM.teks);
var deltaHarap = nilaiKoreksi('IR64 Apex', '14500').delta + nilaiKoreksi('Pandan Wangi', '16500').delta;
var KM = susunKoreksiMassal({ 'IR64 Apex': '14.500', 'Pandan Wangi': '16.500' }, 'harga baru semua', WK);
ok('ST6 massal sah: keduanya di kedatangan b1 → SATU dokumen batchMasuk (kedua baris berubah, Angsa di batch itu tetap 13.000) + 2 jejak koreksiHpp; Δ total = jumlah Δ tiap nama', !KM.tolak && KM.dokumen.filter(function (d) { return d.koleksi === 'batchMasuk'; }).length === 1 && KM.dokumen[0].data.id === 'b1' && KM.dokumen[0].data.merkList.find(function (m) { return m.merk === 'IR64 Apex'; }).hargaPerKg === 14500 && KM.dokumen[0].data.merkList.find(function (m) { return m.merk === 'Pandan Wangi'; }).hargaPerKg === 16500 && KM.dokumen[0].data.merkList.find(function (m) { return m.merk === 'Angsa'; }).hargaPerKg === 13000 && KM.dokumen.filter(function (d) { return d.koleksi === 'koreksiHpp'; }).length === 2 && Math.abs(KM.delta - deltaHarap) < 0.01, JSON.stringify(KM.dokumen.map(function (d) { return d.koleksi; })));
var modalAngsaSblm = hitungStokKarungPerMerk().Angsa.hppTerakhirPerKg; terapkanKeCache(KM.dokumen);
ok('ST6 sesudah massal: mesin membaca IR64 Apex 14.500 (kini RUGI 500/kg → ringkasan 1 nama RUGI), Pandan Wangi 16.500; Angsa tidak bergeser; log 3', hitungStokKarungPerMerk()['IR64 Apex'].hppTerakhirPerKg === 14500 && hitungStokKarungPerMerk()['Pandan Wangi'].hppTerakhirPerKg === 16500 && hitungStokKarungPerMerk().Angsa.hppTerakhirPerKg === modalAngsaSblm && kartuHpp().ringkas.rugi === 1 && /1 nama RUGI/.test(kartuHpp().ringkasTeks) && logKoreksi(5).length === 3, kartuHpp().ringkasTeks);
ok('ST6 atur: batas lonjakan 60 % → 30.000 tidak ditanya; lantai 20.000 → 14.000 ditolak', (function () { var A = susunAturHpp({ batasLonjak: '60', lantaiHpp: '' }, WK); terapkanKeCache(A.dokumen); var r1 = nilaiKoreksi('Angsa', '30000').lonjak === ''; var B = susunAturHpp({ lantaiHpp: '20000' }, WK); terapkanKeCache(B.dokumen); var r2 = /di bawah lantai Rp20\.000/.test(nilaiKoreksi('Angsa', '14000').tolak); terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'hpp' }]); return r1 && r2; })());
pasok('batchMasuk', KOTAK.batchMasuk); cacheMentah('koreksiHpp').slice().forEach(function (x) { terapkanKeCache([{ koleksi: 'koreksiHpp', hapus: x.id }]); });

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var G = susunGudang('modal', KINI); var N = hitungNeraca();
var stokK = hitungStokKarungPerMerk(), stokM = hitungStokKemasan(); var positif = 0;
Object.keys(stokK).forEach(function (m) { if ((stokK[m].sisaKg || 0) > 0) positif += stokK[m].sisaKg * (stokK[m].hppTerakhirPerKg || 0); });
Object.keys(stokM).forEach(function (k) { if ((stokM[k].sisaUnit || 0) > 0) positif += stokM[k].sisaUnit * (stokM[k].hppRataRataPerUnit || 0); });
// bentuk dokumen catat vs baris nyata: kolom batchMasuk & penyesuaianStok yang dihasilkan wajib dikenal cadangan (kolom tambahan sistem baru disebut eksplisit)
// putaran 27: kedatangan contoh berharga beda > batas dari modal → dijawab "sama barangnya" (varian: 'sama'; bentuk dokumen tetap)
var kenalB = {}; (CAD.batchMasuk || []).forEach(function (b) { Object.keys(b).forEach(function (k) { kenalB[k] = 1; }); (b.merkList || []).forEach(function (m) { Object.keys(m).forEach(function (k) { kenalB['merkList.' + k] = 1; }); }); }); kenalB.jam = 1; kenalB.alasanKoreksi = 1; kenalB.riwayat = 1;
// paket brief 9 Okt (butir 6 & 7): kolom timbang & mutu saat terima (opsional, hanya ditulis bila diisi) — kolom tambahan sistem baru, disebut eksplisit
TM_KOLOM.forEach(function (k) { kenalB['merkList.' + k] = 1; });
var kenalP = {}; (CAD.penyesuaianStok || []).forEach(function (b) { Object.keys(b).forEach(function (k) { kenalP[k] = 1; }); }); ['bagian', 'bagianSistemKg', 'bagianFisikKg', 'wadah'].forEach(function (k) { kenalP[k] = 1; });   // kolom tambahan putaran 27 (izin owner 27 Sep), disebut eksplisit
var WX = { tanggal: '2026-09-22', jam: '10:00', idUnik: function () { return Math.random(); } }; var asingC = [];
var dX = drafMasukKosong(WX); dX.pemasok = calonPemasok()[0] || 'X'; dX.baris = [{ merk: calonMerkMasuk()[0], jumlahKarung: '70', beratKarung: 50, hargaPerKg: '13.000', varian: 'sama', timbangKg: '3.490', kadarAir: '14,5', kutu: 'tidak', bau: 'normal', butirPatah: '20' }]; var SX = susunSimpanMasuk(dX, WX, true);
if (SX.dokumen) { Object.keys(SX.dokumen[0].data).forEach(function (k) { if (!kenalB[k]) asingC.push('batchMasuk.' + k); }); Object.keys(SX.dokumen[0].data.merkList[0]).forEach(function (k) { if (!kenalB['merkList.' + k]) asingC.push('batchMasuk.merkList.' + k); }); } else asingC.push('masuk ditolak: ' + SX.tolak);
var bY = barangCocok('tumpukan').filter(function (b) { return b.sistem > 0; })[0]; if (bY) { var HY = {}; HY[bY.kunci] = String(bY.sistem - 1); var SY = susunSimpanCocok('tumpukan', HY, {}, WX, { sebagian: true }); if (SY.dokumen) Object.keys(SY.dokumen[0].data).forEach(function (k) { if (!kenalP[k]) asingC.push('penyesuaianStok.' + k); }); else asingC.push('cocok ditolak: ' + SY.tolak); }
// adukan & karantina: kolom dokumen produksi / pemakaian kantong / rework wajib dikenal cadangan (kolom tambahan sistem baru: jam)
var kenalPr = {}; (CAD.produksiKemasan || []).forEach(function (p) { Object.keys(p).forEach(function (k) { kenalPr[k] = 1; }); }); kenalPr.jam = 1; kenalPr.catatan = 1;
var kenalKt = {}; (CAD.stokBahanKemasan || []).forEach(function (b) { Object.keys(b).forEach(function (k) { kenalKt[k] = 1; }); });
// ST4: dokumen beli kantong sistem baru = bentuk lama + kolom baru yang disebut (hargaPerPcs, jam, toko)
var SK4 = susunSimpanBeli({ jenis: '5kg_kembangbmw', jumlah: '10', harga: '1.125', toko: 'X' }, WX, { murah: true, lonjak: true });
if (SK4.dokumen) Object.keys(SK4.dokumen[0].data).forEach(function (k) { if (!kenalKt[k] && ['hargaPerPcs', 'jam', 'toko'].indexOf(k) < 0) asingC.push('stokBahanKemasan.beli.' + k); }); else asingC.push('beli kantong ditolak: ' + SK4.tolak);
// ST6: rumus replika Σnilai/Σkg = mesin untuk SEMUA nama di data toko
var replikaBeda = Object.keys(hitungStokKarungPerMerk()).filter(function (m) { return Math.abs(totalMasuk(m).rata - hitungStokKarungPerMerk()[m].hppTerakhirPerKg) > 1e-6; });
if (replikaBeda.length) asingC.push('HPP replika ≠ mesin: ' + replikaBeda.join(', '));
var cb = calonBahan()[0]; var cn = calonNamaHasil()[0]; var ck5 = kantongUntuk(5)[0]; var banyakAdukan = daftarAdukan(1e9).length; var rincianOk = true;
if (cb && cn && ck5) { var dZ = drafAdukanKosong(WX); dZ.bahan = [{ merk: cb.merk, kg: '50' }]; dZ.hasil = [{ nama: cn, ukuran: '5', unit: '10', kantongJenis: ck5.jenis, kantongJumlah: '10' }]; dZ.upah = '10.000';
  var SZ = susunSimpanAdukan(dZ, WX, { bahan: true, kantong: true, susut: true, kantongKosong: true, kemasan: true, mundur: true });   // putaran 31.3: WX bertanggal sebelum cocokkan terakhir di cadangan → ketukan kedua
  if (SZ.dokumen) { Object.keys(SZ.dokumen[0].data).forEach(function (k) { if (!kenalPr[k]) asingC.push('produksiKemasan.' + k); }); var kt = SZ.dokumen.find(function (d) { return d.koleksi === 'stokBahanKemasan'; }); if (kt) Object.keys(kt.data).forEach(function (k) { if (!kenalKt[k]) asingC.push('stokBahanKemasan.' + k); });
    if (Math.abs(SZ.dokumen[0].data.hppPerUnit * 10 - SZ.hitung.total) > 1e-6) asingC.push('adukan: Σ modal × unit ≠ total biaya'); } else asingC.push('adukan ditolak: ' + SZ.tolak); }
daftarAdukan(1e9).slice(0, 40).forEach(function (a) { var r = rincianAdukan(a.batch); if (!r || Math.abs(r.biaya.total - a.total) > 1) rincianOk = false; });
if (!rincianOk) asingC.push('adukan: rincian tidak sama dengan buku');
// audit 39b no. 2: tiap kedatangan bon di data toko — yang sudah dibayar terkunci (jadi tunai / pemasok lain / hapus DITOLAK), yang belum dibayar tetap
// bisa dihapus; Σ (nilai − dibayar) bon kedatangan = Σ sisa bon kedatangan di mesin (satu sumber); ejaan pemasok nyata tidak ada yang digeser
var bon2 = { bon: 0, dibayar: 0, rpDibayar: 0, kunci: 0, kunciPeriode: 0, lolos: [], bebasSalah: [], selisihMesin: 0, bedaMesin: [], ejaanGeser: [] };
var WB2 = { tanggal: '2026-09-29', jam: '20:00', idUnik: function () { return Math.random(); } };
var sisaMesin = 0; hitungUtangPemasok().forEach(function (px) { px.bon.forEach(function (b) { if (b.jenis === 'batch') sisaMesin += b.sisa; }); });
var sisaHitung = 0;
ambilSemuaBatch().filter(function (b) { return !b.stokAwal && b.caraBayar === 'utang'; }).forEach(function (b) {
  bon2.bon++; var bb = ckBayarBon(b); sisaHitung += bb.nilai - bb.dibayarMesin; if (bb.dibayar !== bb.dibayarMesin) bon2.bedaMesin.push(String(b.id) + ' ' + bb.dibayar + '/' + bb.dibayarMesin);
  if (tolakKunci('batchMasuk', b, '')) { bon2.kunciPeriode++; return; }   // bulan terkunci: penolakan kunci periode datang lebih dulu (tinjauan 30 Sep)
  if (bb.dibayar > 0) {
    bon2.dibayar++; bon2.rpDibayar += bb.dibayar;
    var dx = drafDariKedatangan(b.id); dx.alasan = 'asap'; dx.caraBayar = 'tunai'; var t1 = susunSimpanMasuk(dx, WB2, true).tolak || '';
    var dy = drafDariKedatangan(b.id); dy.alasan = 'asap'; dy.pemasok = 'PEMASOK LAIN ASAP'; var t2 = susunSimpanMasuk(dy, WB2, true).tolak || '';
    var t3 = susunHapusKedatangan(b.id, 'asap', WB2).tolak || '';
    if ([t1, t2, t3].every(function (t) { return /sudah dibayar/.test(t); })) bon2.kunci++; else bon2.lolos.push(String(b.id) + ': ' + [t1, t2, t3].map(function (t) { return t.slice(0, 60); }).join(' | '));
  } else if (/sudah dibayar/.test(susunHapusKedatangan(b.id, 'asap', WB2).tolak || '')) bon2.bebasSalah.push(String(b.id));
});
bon2.selisihMesin = Math.round(sisaHitung - sisaMesin);
ambilSemuaBatch().forEach(function (b) { if (b.stokAwal || b.lahirBuku || !b.pemasok) return; var e = ckEjaanPemasok(b.pemasok, b.id); if (e !== String(b.pemasok).trim()) bon2.ejaanGeser.push(b.pemasok + ' → ' + e); });
print(JSON.stringify({ bon2: bon2, kunciAsingCatat: asingC, adukan: banyakAdukan, karantinaAntre: daftarKarantina(WX).antre.length, nilaiLayar: Math.round(G.jawab.total), nilaiPositif: Math.round(positif), neraca: N.nilaiSack + N.nilaiBags, minus: N.adaStokMinus, barang: G.banyakBarang, beli: susunGudang('beli', KINI).jawab.baris.length, mandek: susunGudang('mandek', KINI).jawab.baris.length, cocok: susunGudang('cocok', KINI).jawab.baris.length, kapur: susunKapur(KINI).banyak, wadah: susunWadah(keadaanAwal()).daftar.length }));
"""

# ---- UMUR & PUTARAN (paket brief 9 Okt, butir 2) — KOTAK PASIR SENDIRI (ANGKA CONTOH), jam 19 Sep 2026 10:00 WIB; harapan dihitung tangan di komentar ----
KB_UM = 'Karung belakang W1 · Contoh Sumber'


def batch_um(id, tgl, merk, kg, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
         'merkList': [{'merk': merk, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg / 50, 'totalKg': kg, 'subtotalHarga': kg * 13000, 'hargaPerKg': 13000}]}
    d.update(k); return d


def pindah_um(id, tgl, sumber, tujuan, kg, **k):
    d = {'id': id, 'tanggal': tgl, 'jam': '09:00', 'namaProduk': tujuan, 'merkTujuan': tujuan, 'jadiKarungUtuh': True, 'dariTakar': True, 'ukuranKemasan': kg, 'jumlahUnit': 1, 'kgDipakai': kg,
         'sumberList': [{'merk': sumber, 'kg': kg}], 'merkSumber': sumber, 'hppSumberPerKgDipakai': 13000, 'hppPerUnit': 13000 * kg, 'upahRepacking': 0, 'biayaKemasan': 0, 'kgKemasanDipakai': 0}
    d.update(k); return d


KOTAK_UMUR = {
  'batchMasuk': [
    # fondasi (stok awal 1 Jul): TIDAK bertanggal masuk — Contoh Lama 100, Contoh Lebih 500, Contoh Awal 80
    {'id': 'u0', 'tanggal': '2026-07-01', 'jam': '07:00', 'pemasok': 'STOK AWAL', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'stokAwal': True, 'merkList': [
        {'merk': 'Contoh Lama', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 1300000, 'hargaPerKg': 13000},
        {'merk': 'Contoh Lebih', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'subtotalHarga': 6500000, 'hargaPerKg': 13000},
        {'merk': 'Contoh Awal', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 1.6, 'totalKg': 80, 'subtotalHarga': 1040000, 'hargaPerKg': 13000}]},
    batch_um('u1', '2026-08-10', 'Contoh Lama', 200), batch_um('u2', '2026-09-09', 'Contoh Lama', 300),
    batch_um('u3', '2026-09-01', 'Contoh Lebih', 100), batch_um('u4', '2026-09-15', 'Contoh Diam', 50), batch_um('u5', '2026-09-01', 'Contoh Habis', 100),
    batch_um('u6', '2026-09-01', 'Contoh Sumber', 500),
    # buku wadah W1 & karung di belakangnya lahir 1 Sep (0 kg)
    {'id': 'lw', 'tanggal': '2026-09-01', 'jam': '07:00', 'pemasok': 'LAHIR BUKU', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'stokAwal': True, 'lahirBuku': True, 'merkList': [
        {'merk': 'Wadah W1', 'stokWadah': 'W1', 'satuan': 'kg', 'totalKg': 0, 'subtotalHarga': 0, 'hargaPerKg': 0},
        {'merk': KB_UM, 'karungBelakang': 'W1', 'merkAsal': 'Contoh Sumber', 'satuan': 'karung', 'totalKg': 0, 'subtotalHarga': 0, 'hargaPerKg': 0}]}],
  'produksiKemasan': [
    pindah_um('pu1', '2026-09-08', 'Contoh Sumber', KB_UM, 50, bukaKarung='W1', merkAsal='Contoh Sumber'),
    pindah_um('pu2', '2026-09-10', KB_UM, 'Wadah W1', 20), pindah_um('pu3', '2026-09-15', KB_UM, 'Wadah W1', 30),
    pindah_um('pu4', '2026-09-16', 'Contoh Sumber', KB_UM, 50, bukaKarung='W1', merkAsal='Contoh Sumber')],
  'penjualan': [
    jual('ul1', '2026-08-15', 'Contoh Lama', 150), jual('ul2', '2026-09-12', 'Contoh Lama', 70), jual('ub1', '2026-09-10', 'Contoh Lebih', 50),
    jual('ua1', '2026-09-15', 'Contoh Awal', 70), jual('uh1', '2026-09-10', 'Contoh Habis', 100),
    jual('uw1', '2026-09-12', 'Wadah W1', 10, jenis='literan', dariWadah='W1'), jual('uw2', '2026-09-15', 'Wadah W1', 4, jenis='literan', dariWadah='W1', jam='18:00'),
    jual('uw3', '2026-09-18', 'Wadah W1', 6, jenis='literan', dariWadah='W1')],
  # cocokkan wadah 17 Sep +2 kg (kenaikan tanpa catatan tuang → bagian tanpa tanggal)
  'penyesuaianStok': [{'id': 'uo1', 'tanggal': '2026-09-17', 'jam': '19:00', 'merk': 'Wadah W1', 'kgSistem': 36, 'kgFisik': 38, 'selisihKg': 2}],
}
# tinjauan no. 14 (9 Okt): masuk & keluar di hari yang sama — dipasang di kasusnya saja lalu dipulihkan
SEKEJAP = {'batch': batch_um('u9', '2026-09-12', 'Contoh Sekejap', 50), 'jual': jual('us1', '2026-09-12', 'Contoh Sekejap', 50)}

SKENARIO_UMUR = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push('UMUR ' + nama + (ket ? ' → ' + ket : '')); }
function dekat(a, b) { return a !== null && b !== null && Math.abs(a - b) < 1e-6; }
Object.keys(KOTAK_UMUR).forEach(function (n) { pasok(n, KOTAK_UMUR[n]); });
var KINI = new Date(Date.now()); var KB = 'Karung belakang W1 · Contoh Sumber';
function r(nama) { return umBarang(KINI).find(function (x) { return x.kunci === nama; }); }
var L = r('Contoh Lama');
// Contoh Lama: masuk 100 (stok awal) + 200 (10 Agu) + 300 (9 Sep); terjual 150 (15 Agu) + 70 (12 Sep) → sisa 380 = SUMBER GUDANG.
// FIFO: 300 kg kedatangan 9 Sep utuh (umur 10) + 80 dari 200 kg kedatangan 10 Agu (umur 40) → umur stok 40; rata-rata (300×10 + 80×40) / 380 = 16,3158
ok('sisa = sumber yang sama dengan Gudang (daftarBarang 380 kg)', L.sisa === 380 && L.sisa === daftarBarang().find(function (b) { return b.kunci === 'Contoh Lama'; }).sisa, JSON.stringify(L && L.sisa));
ok('FIFO menyentuh lapisan lama: 9 Sep 300 kg utuh + 80 dari 200 kg kedatangan 10 Agu; umur stok 40 hari; rata-rata ditimbang 16,3158; tanpa tanggal 0', L.umur.lapisan.length === 2 && L.umur.lapisan[0].tanggal === '2026-09-09' && L.umur.lapisan[0].kg === 300 && L.umur.lapisan[0].utuh && L.umur.lapisan[1].tanggal === '2026-08-10' && L.umur.lapisan[1].kg === 80 && L.umur.lapisan[1].kgMasuk === 200 && !L.umur.lapisan[1].utuh && L.umurAcuan === 40 && dekat(L.umur.umurRata, 6200 / 380) && L.umur.tanpaTanggalKg === 0, JSON.stringify(L.umur));
ok('kalimat lapisan menyebut "tersisa dari kedatangan 10 Agu · 80 kg dari 200 kg"', /tersisa dari kedatangan 10 Agu · 80 kg dari 200 kg \+ 1 kedatangan lebih baru/.test(umKalimat('Contoh Lama', KINI)), umKalimat('Contoh Lama', KINI));
// laju 14 hari (≥ 5 Sep): 70 kg → 5 kg/hari → hari stok 380 / 5 = 76
ok('hari stok = sisa ÷ laju Gudang = 380 ÷ 5 = 76; lambat laku karena umur 40 > 30 DAN hari stok 76 > 30', dekat(L.hariStok, 76) && L.lambat && L.alasan.join() === 'umur,hari', JSON.stringify([L.hariStok, L.alasan]));
// perputaran 30 hari (21 Agu–19 Sep): keluar 70; sisa akhir hari 150 ×19 (21 Agu–8 Sep) + 450 ×3 (9–11 Sep) + 380 ×8 (12–19 Sep) = 7.240 → rata 241,333; putaran 0,29006; tinggal 7.240 / 70 = 103,43
ok('perputaran 30 hari: keluar 70 kg ÷ rata-rata sisa 241,33 = 0,290×; rata-rata tinggal di rak 103,43 hari', L.keluarKg === 70 && L.terjualKg === 70 && dekat(L.rataSisa, 7240 / 30) && dekat(L.putaran, 70 / (7240 / 30)) && dekat(L.tinggal, 7240 / 70), JSON.stringify([L.keluarKg, L.rataSisa, L.putaran, L.tinggal]));
var B = r('Contoh Lebih');
// Contoh Lebih: stok awal 500 + kedatangan 1 Sep 100 − terjual 50 = 550 → 100 bertanggal (umur 18) + 450 TANPA TANGGAL (bukan umur 0)
ok('sisa melebihi kedatangan tercatat: 100 kg bertanggal (1 Sep, umur 18) + 450 kg tanpa tanggal masuk; menutup ke 550; umur acuan 18 (bukan 0)', B.sisa === 550 && B.umur.bertanggalKg === 100 && B.umur.tanpaTanggalKg === 450 && B.umurAcuan === 18 && B.umur.lapisan.length === 1, JSON.stringify(B.umur));
ok('lambat laku Contoh Lebih karena hari stok 550 ÷ (50/14) = 154 > 30 (umur 18 tidak)', dekat(B.hariStok, 550 / (50 / 14)) && B.alasan.join() === 'hari', JSON.stringify([B.hariStok, B.alasan]));
var Aw = r('Contoh Awal');
ok('stok awal saja: 10 kg semuanya tanpa tanggal → umur BELUM BISA DIHITUNG (null, bukan 0); tidak dicap lambat (hari stok 10 ÷ 5 = 2)', Aw.sisa === 10 && Aw.umurAcuan === null && Aw.umur.tanpaTanggalKg === 10 && Aw.umur.bertanggalKg === 0 && !Aw.lambat && dekat(Aw.hariStok, 2), JSON.stringify(Aw));
var Dm = r('Contoh Diam');
ok('merek tanpa gerak: hari stok "belum ada laju" (null, bukan 0), putaran null, lambat karena diam; umur 4 hari', Dm.hariStok === null && Dm.putaran === null && Dm.tinggal === null && Dm.alasan.join() === 'diam' && Dm.umurAcuan === 4 && /belum ada laju/.test(umKalimat('Contoh Diam', KINI)), JSON.stringify(Dm));
var H = r('Contoh Habis');
ok('merek habis tapi bergerak: tidak berumur (sisa 0) tetapi putarannya dihitung: keluar 100 ÷ (100 × 9 hari / 30) = 3,333×', H && !H.ada && H.umur === null && dekat(H.putaran, 100 / 30) && dekat(H.tinggal, 9), JSON.stringify(H));
var S = r('Contoh Sumber'), K = r(KB), W = r('Wadah W1');
ok('merek sumber: 500 − 2 karung dibuka ke belakang wadah = 400 kg, FIFO dari kedatangan 1 Sep (400 dari 500 kg, umur 18); keluar 100 kg semuanya DIPINDAH (terjual 0)', S.sisa === 400 && S.umurAcuan === 18 && S.umur.lapisan[0].kg === 400 && S.umur.lapisan[0].kgMasuk === 500 && S.keluarKg === 100 && S.terjualKg === 0 && S.kelompok === 'merek', JSON.stringify([S.sisa, S.umur, S.keluarKg]));
ok('karung di belakang wadah: FIFO per karung yang dibuka — sisa 50 = karung dibuka 16 Sep (umur 3), karung 8 Sep sudah habis dituang', K.kelompok === 'belakang' && K.cara === 'fifo' && K.sisa === 50 && K.umur.lapisan.length === 1 && K.umur.lapisan[0].tanggal === '2026-09-16' && K.umurAcuan === 3, JSON.stringify(K.umur));
// wadah campuran (owner: average): tuang 20 (10 Sep) → 20; jual 10 (12 Sep) → 10; tuang 30 (15 Sep) → umur rata (10×9 + 30×4)/40 = 5,25; jual 4 → 36;
// cocokkan +2 (17 Sep) → 36 bertanggal + 2 tanpa tanggal; jual 6 (18 Sep) → keluar merata ×32/38 → bertanggal 30,32 + tanpa tanggal 1,68 = 32
ok('wadah campuran = RATA-RATA (bukan FIFO): umur rata-rata 5,25 hari sejak dituang; bertanggal 30,32 + tanpa tanggal 1,68 = 32 kg', W.kelompok === 'wadah' && W.cara === 'rata' && W.sisa === 32 && dekat(W.umurAcuan, 5.25) && W.umur.bertanggalKg === 30.32 && W.umur.tanpaTanggalKg === 1.68 && /wadah campuran, rata-rata/.test(umKalimat('Wadah W1', KINI)), JSON.stringify(W.umur));
// ringkas: Σ sisa positif 380 + 550 + 10 + 50 + 400 + 50 + 32 = 1.472 = bertanggal 1.010,32 + tanpa tanggal 461,68
var G = umRingkas(KINI);
ok('hitungan menutup: Σ sisa positif 1.472 kg = bertanggal 1.010,32 + tanpa tanggal 461,68 (tidak ada yang dibuang)', G.sisaKg === 1472 && G.bertanggalKg === 1010.32 && G.tanpaTanggalKg === 461.68 && Math.round((G.bertanggalKg + G.tanpaTanggalKg) * 100) === Math.round(G.sisaKg * 100), JSON.stringify([G.sisaKg, G.bertanggalKg, G.tanpaTanggalKg]));
ok('lambat laku: Contoh Lama, Contoh Lebih, Contoh Diam, Contoh Sumber (hari stok 400 ÷ (100/14) = 56); merek tertua: Lama 40 · Lebih 18 · Sumber 18 · Diam 4 (Awal tanpa tanggal tidak ikut)', G.lambat.map(function (x) { return x.kunci; }).sort().join() === 'Contoh Diam,Contoh Lama,Contoh Lebih,Contoh Sumber' && G.tertua.map(function (x) { return x.kunci + ':' + x.umurAcuan; }).join() === 'Contoh Lama:40,Contoh Lebih:18,Contoh Sumber:18,Contoh Diam:4', JSON.stringify([G.lambat.map(function (x) { return x.kunci; }), G.tertua.map(function (x) { return x.kunci + ':' + x.umurAcuan; })]));
var PP = umPapan(KINI, 'tanpa', 'Contoh Lebih'); var bl = PP.kelompok[0].baris.find(function (b) { return b.kunci === 'Contoh Lebih'; });
ok('papan "tanpa tanggal": kartu 461,68 kg; rincian Contoh Lebih menyebut asalnya (stok awal 500 kg) & "Belum bisa dihitung"', PP.kartu[3].a === '461,68 kg' && bl && bl.rinci && bl.rinci.some(function (x) { return /450 kg TANPA TANGGAL MASUK/.test(x.teks) && /stok awal 500 kg/.test(x.teks) && /Belum bisa dihitung/.test(x.teks); }), JSON.stringify(bl && bl.rinci));
var PL = umPapan(KINI, 'lambat', null); var PU = umPapan(KINI, 'umur', null);
ok('papan: kartu lambat "4 barang", umur tertua "40 hari"; tab umur dikelompokkan merek · belakang · wadah; kalimat penutup menyebut bertanggal + tanpa tanggal', PL.kartu[0].a === '4 barang' && PL.kartu[1].a === '40 hari' && PU.kelompok.map(function (g) { return g.id; }).join() === 'merek,belakang,wadah' && /= bertanggal 1010,32 kg \+ tanpa tanggal masuk 461,68 kg/.test(PU.tutup) && !PU.kelompok[0].baris.some(function (b) { return b.kunci === 'Contoh Habis'; }), JSON.stringify([PL.kartu, PU.tutup]));
// tinjauan no. 14 (9 Okt): Contoh Sekejap masuk 50 kg & terjual 50 kg di hari yang SAMA (12 Sep) → keluar 50 kg, sisa akhir hari 0 tiap hari (rata 0) → putaran null.
// Angka besar di tab putaran = "belum bisa dihitung" (+ "sisa rata-rata tidak positif"), BUKAN "belum ada laju"; Contoh Diam (tidak keluar) tetap "belum ada laju".
pasok('batchMasuk', KOTAK_UMUR.batchMasuk.concat([SEKEJAP.batch])); pasok('penjualan', KOTAK_UMUR.penjualan.concat([SEKEJAP.jual]));
var Sk = r('Contoh Sekejap'); var PTn = umPapan(KINI, 'putaran', null); var cariB = function (P, k) { var x = null; P.kelompok.forEach(function (g) { g.baris.forEach(function (b) { if (b.kunci === k) x = b; }); }); return x; };
var bSk = cariB(PTn, 'Contoh Sekejap'), bDm = cariB(PTn, 'Contoh Diam');
pasok('batchMasuk', [SEKEJAP.batch]); pasok('penjualan', [SEKEJAP.jual]); pasok('produksiKemasan', []); pasok('penyesuaianStok', []);
var GSk = umRingkas(KINI); var KSk = umPapan(KINI, 'putaran', null).kartu[2];
Object.keys(KOTAK_UMUR).forEach(function (n) { pasok(n, KOTAK_UMUR[n]); });
ok('tinjauan no. 14: buku yang KELUAR 50 kg tetapi sisa akhir harinya selalu 0 → putaran null ditulis "belum bisa dihitung · sisa rata-rata tidak positif" (bukan "belum ada laju"); buku tanpa gerak tetap "belum ada laju · tak ada gerak"; kartu ringkasan juga (hanya buku itu: keluar 50, putaran tumpukan merek "belum bisa dihitung")',
  !!Sk && Sk.keluarKg === 50 && Sk.rataSisa === 0 && Sk.putaran === null && !!bSk && bSk.n === 'belum bisa dihitung' && bSk.nKet === 'sisa rata-rata tidak positif' && !!bDm && bDm.n === 'belum ada laju' && bDm.nKet === 'tak ada gerak'
  && GSk.putaranMerek === null && GSk.keluarMerek === 50 && KSk.a === 'belum bisa dihitung', JSON.stringify([Sk && [Sk.keluarKg, Sk.rataSisa, Sk.putaran], bSk && [bSk.n, bSk.nKet], bDm && [bDm.n, bDm.nKet], KSk]));
// FIFO murni
var F = umFifo([{ tanggal: '2026-09-01', jam: '08:00', id: 1, kg: 50 }, { tanggal: '2026-09-01', jam: '15:00', id: 2, kg: 50 }, { tanggal: '2026-08-01', id: 3, kg: 100 }], 60, '2026-09-19');
ok('FIFO murni: tanggal sama → jam lebih sore = lebih baru (50 utuh) + 10 dari kedatangan pagi; sisa 0 / minus → tidak ada lapisan, tanpa tanggal 0', F.lapisan.length === 2 && F.lapisan[0].id === 2 && F.lapisan[1].kg === 10 && F.umurTertua === 18 && umFifo([{ tanggal: '2026-09-01', kg: 5 }], 0, '2026-09-19').lapisan.length === 0 && umFifo([{ tanggal: '2026-09-01', kg: 5 }], -3, '2026-09-19').tanpaTanggalKg === 0, JSON.stringify(F));
// SETELAN OWNER → hasil ikut
var WS = { tanggal: '2026-09-19', jam: '10:00' };
ok('atur: pecahan 30,5 / 0 / periode 200 DITOLAK dengan kalimat (tidak dibulatkan diam-diam); kosong = angka sekarang', /bilangan bulat 1–365/.test(susunAturUmur({ ambangUmurHari: '30,5' }, WS).tolak || '') && !!susunAturUmur({ ambangHariStok: '0' }, WS).tolak && /7–120/.test(susunAturUmur({ periodeHari: '200' }, WS).tolak || '') && susunAturUmur({}, WS).dokumen[0].data.ambangUmurHari === 30);
var AT = susunAturUmur({ ambangUmurHari: '45', ambangHariStok: '80', periodeHari: '10' }, WS); terapkanKeCache(AT.dokumen);
L = r('Contoh Lama');
// periode 10 hari (10–19 Sep): sisa 450 ×2 + 380 ×8 = 3.940 → rata 394; putaran 70/394; tinggal 3.940/70 = 56,29
ok('setelan owner ikut: ambang umur 45 & hari stok 80 → Contoh Lama (umur 40, hari stok 76) & Contoh Sumber (56) TIDAK lagi lambat, tinggal Lebih (154) & Diam; periode 10 hari → rata-rata sisa 394, tinggal 56,29 hari', AT.dokumen[0].koleksi === 'aturanToko' && AT.dokumen[0].data.id === 'stokUmur' && umAtur().dariOwner && !L.lambat && dekat(L.rataSisa, 394) && dekat(L.tinggal, 3940 / 70) && umRingkas(KINI).lambat.map(function (x) { return x.kunci; }).sort().join() === 'Contoh Diam,Contoh Lebih', JSON.stringify([L.alasan, L.rataSisa, umRingkas(KINI).lambat.map(function (x) { return x.kunci; })]));
terapkanKeCache(susunAturUmur({ periodeHari: '60' }, WS).dokumen);
ok('periode 60 hari dipendekkan ke catatan pertama toko (10 Agu) → 41 hari, disebut', umRingkas(KINI).periode.n === 41 && umRingkas(KINI).periode.dari === '2026-08-10' && /catatan toko baru mulai 10 Agu/.test(umRingkas(KINI).periode.catat), JSON.stringify(umRingkas(KINI).periode));
terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'stokUmur' }]);
ok('setelan dihapus → kembali angka bawaan 30 / 30 / 30', umAtur().ambangUmurHari === 30 && !umAtur().dariOwner && r('Contoh Lama').lambat);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP_UMUR = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var G = umRingkas(KINI); var R = umBarang(KINI); var salah = [];
var buku = ingatStokKarung();
R.forEach(function (r) {
  if (!buku[r.kunci] || buku[r.kunci].sisaKg !== r.sisa) salah.push('sisa ' + r.kunci + ' bukan sumber Gudang');
  if (r.ada && Math.round(r.umur.bertanggalKg * 100) + Math.round(r.umur.tanpaTanggalKg * 100) !== Math.round(r.sisa * 100)) salah.push('tidak menutup: ' + r.kunci);
  if (r.ada && r.umurAcuan === null && r.umur.bertanggalKg > 0) salah.push('umur hilang: ' + r.kunci);
  if (r.ada && r.kelompok === 'wadah' && r.cara !== 'rata') salah.push('wadah bukan rata-rata: ' + r.kunci);
});
if (Math.round((G.bertanggalKg + G.tanpaTanggalKg) * 100) !== Math.round(G.sisaKg * 100)) salah.push('ringkas tidak menutup');
// tinjauan no. 14: tab putaran — buku yang keluar > 0 tidak boleh berangka besar "belum ada laju"
var belumHitung = []; umPapan(KINI, 'putaran', null).kelompok.forEach(function (g) { g.baris.forEach(function (b) { var x = R.find(function (y) { return y.kunci === b.kunci; });
  if (x && x.putaran === null && x.keluarKg > 0) { belumHitung.push(b.nama + ' (keluar ' + x.keluarKg + ' kg: ' + b.n + ')'); if (b.n === 'belum ada laju') salah.push('putaran "belum ada laju" padahal keluar: ' + b.nama); } }); });
var a = function (x) { return x.nama + ' ' + (x.umurAcuan === null ? '?' : Math.round(x.umurAcuan * 10) / 10) + ' hari'; };
print(JSON.stringify({ salah: salah, tertua: G.tertua.map(function (x) { return a(x) + ' (' + (x.umur.lapisan.length ? 'tersisa dari kedatangan ' + x.umur.tanggalTertua + ' · ' + x.umur.lapisan[x.umur.lapisan.length - 1].kg + ' kg' : '') + ')'; }),
  lambat: G.lambat.map(function (x) { return x.nama + ' [' + x.alasan.join('+') + '] umur ' + (x.umurAcuan === null ? '?' : Math.round(x.umurAcuan * 10) / 10) + ' · hari stok ' + (x.hariStok === null ? 'belum ada laju' : Math.round(x.hariStok)) + ' · sisa ' + x.sisa + ' kg'; }),
  sisa: G.sisaKg, bertanggal: G.bertanggalKg, tanpa: G.tanpaTanggalKg, minus: G.minus.map(function (x) { return x.nama + ' ' + x.sisa; }), putaran: G.putaranMerek === null ? null : Math.round(G.putaranMerek * 100) / 100, periode: G.periode, n: R.length, belumHitung: belumHitung }));
"""


def utama_umur(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK_UMUR = ' + json.dumps(KOTAK_UMUR) + ';\nvar SEKEJAP = ' + json.dumps(SEKEJAP) + ';\n' + SKENARIO_UMUR)
    if h is None: return 0, ['UMUR JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


def rusak_umur(js):
    """--kontrol paket brief 9 Okt: urutan / cara / setelan dirusak → kotak pasir umur WAJIB berbunyi."""
    cara = "const cara = jb === 'wadah' || jb === 'karung' ? 'rata' : 'fifo';"
    return {
        'umur FIFO dibalik jadi TERLAMA-DULU (sisa diisi dari kedatangan lama)': js.replace(".sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)) || String(b.jam || '').localeCompare(String(a.jam || ''))", ".sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)) || String(a.jam || '').localeCompare(String(b.jam || ''))"),
        'umur karung jadi RATA-RATA (semua buku memakai cara wadah)': js.replace(cara, "const cara = 'rata';"),
        'umur stok = rata-rata ditimbang, bukan lapisan tertua': js.replace("umurTertua: tua ? tua.umur : null,", "umurTertua: bertanggal > 0 ? tersisa.reduce((a, x) => a + umSen(x.kg) * x.umur, 0) / bertanggal : null,"),
        'wadah campuran dipaksa FIFO': js.replace(cara, "const cara = 'fifo';"),
        'tanpa tanggal masuk dibuang diam-diam (tidak menutup)': js.replace("tanpaTanggalKg: total > 0 ? (total - bertanggal) / 100 : 0, umurTertua", "tanpaTanggalKg: 0, umurTertua"),
        'tanpa tanggal digambar umur 0': js.replace("const umurAcuan = !U ? null : cara === 'rata' ? U.umurRata : U.umurTertua;", "const umurAcuan = !U ? null : cara === 'rata' ? U.umurRata : (U.umurTertua === null ? 0 : U.umurTertua);"),
        'tanpa gerak digambar hari stok 0': js.replace("const hariStok = ada && b.laju > 0 ? b.sisa / b.laju : null;", "const hariStok = ada ? (b.laju > 0 ? b.sisa / b.laju : 0) : null;"),
        'setelan owner tidak dibaca (ambang selalu bawaan)': js.replace("const a = cacheMentah('aturan').find((d) => String(d.id) === 'stokUmur') || null; const o = {};", "const a = null; const o = {};"),
        'ambang pecahan dibulatkan diam-diam': js.replace("if (!isFinite(n) || Math.round(n) !== n || n < b[0] || n > b[1])", "if (!isFinite(n) || n < b[0] || n > b[1])"),
        'perputaran memakai sisa hari ini, bukan rata-rata periode': js.replace("const rataSisa = P.n > 0 ? hariP.reduce(", "const rataSisa = P.n > 0 ? b.sisa + 0 * hariP.reduce("),
        'periode tidak dipendekkan ke catatan pertama': js.replace("if (pertama && pertama > dari) {", "if (false) {"),
        'tinjauan no. 14: buku yang bergerak (sisa rata-rata ≤ 0) ditulis "belum ada laju" lagi': js.replace("r.putaran !== null ? umKali(r.putaran) + '×' : r.keluarKg > 0 ? 'belum bisa dihitung' : 'belum ada laju'", "r.putaran !== null ? umKali(r.putaran) + '×' : 'belum ada laju'"),
        'tinjauan no. 14: kartu putaran menulis "belum ada laju" walau tumpukan merek keluar': js.replace("G.keluarMerek > 0 ? 'belum bisa dihitung' : 'belum ada laju'", "'belum ada laju'"),
    }


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar KOTAK16 = ' + json.dumps(KOTAK16) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    # audit 39b no. 30 — pemeriksaan statis stok.js (layar DOM tidak ikut kotak pasir): kartu Jumlah koreksi & pita bon dibayar menyebut baris bal
    POT30 = [('kartu Jumlah koreksi menyebut baris bal (beras + bal + bongkar = total)', "${hm.nilaiBal ? ' + baris bal ' + RP(hm.nilaiBal) + ' (tidak diubah)' : ''}"),
             ('pita bon dibayar: yang dijaga beras + baris bal', "nilai beras${hm.nilaiBal ? ' + baris bal' : ''} tidak boleh di bawah")]
    statis30 = lambda t: [n for n, pot in POT30 if pot not in t]
    sk30 = open(os.path.join(AKAR, 'baru/js/layar/stok.js'), encoding='utf-8').read()
    if '--kontrol' in sys.argv:
        rusak = {
            'tinjauan (no. 11): nama sistem diterima sebagai pemasok di Barang masuk': js.replace("if (namaSistemPemasok(pemasok)) return { tolak:", "if (false) return { tolak:"),
            # ---- putaran 21
            'kembalikan karung tanpa ketukan kedua': js.replace("if (!yakin) return { tolak: 'Ketuk sekali lagi untuk mengembalikan karung '", "if (false) return { tolak: 'Ketuk sekali lagi untuk mengembalikan karung '"),
            'kembalikan karung yang belum ditakar ditulis 0 (catatan buka tidak dihapus, papan kapur tetap menyebutnya)': js.replace("const bersih = !berbuku && !dasar && buka.length && !adaTakar;", "const bersih = false;"),
            'deretan karung: karung lepas / yatim yang masih berisi tidak ikut': js.replace("semuaKarungTerbuka().forEach((k) => { if (ada[k.merk + '|' + k.lokasi] || k.sisaMentahKg <= 0.0001) return;", "semuaKarungTerbuka().forEach((k) => { if (true) return;"),
            'tempat berisi dilepas tanpa ketukan kedua (barang hilang tempatnya diam-diam)': js.replace("if (berisi.length && !isi.yakin) { const nm = berisi[0].tempat;", "if (false) { const nm = berisi[0].tempat;"),
            'geser tumpukan tidak menyimpan urutan (susunan kosong)': js.replace("const A = aturTempat(); const susunan = Object.assign({}, A.susunan); daftar.forEach((k, n) => { susunan[k] = n; });", "const A = aturTempat(); const susunan = Object.assign({}, A.susunan);"),
            'tinggi tumpukan 3D dari buku, bukan rantai stok (karung terbuka & wadah tidak dikurangi)': js.replace("const g = tumpukanGudang(b.nama, siap); if (g.adaBuku) return Math.max(0, g.karung);", "const g = tumpukanGudang(b.nama, siap); if (g.adaBuku) return Math.max(0, Math.floor(g.bukuKg / 50));"),
            'kunci kotak lama tidak dipetakan ke denah baru (setelan tersimpan hilang)': js.replace("return KOTAK_DENAH[k] ? k : (KOTAK_LAMA[k] || '');", "return KOTAK_DENAH[k] ? k : '';"),
            'barang tanpa gerak 14 hari dianggap AMAN (tidak disebut)': js.replace("if (b.laju <= 0) { if (b.sisa > 0) tak.push(b.nama); return; }", "if (b.laju <= 0) { return; }"),
            'jumlah beli tidak dibulatkan ke karung penuh': js.replace("Math.ceil(kurang / b.beratKarung) + ' karung'", "Math.floor(kurang / b.beratKarung) + ' karung'"),
            'target isi 7 hari diabaikan (semua barang disuruh beli)': js.replace("if (b.hariHabis > HARI_TARGET) return;", ""),
            'nilai di buku diganti harga beli terbaru (beda dengan Neraca sistem lama)': js.replace("hpp, nilai: sisa * hpp, bisaDinilai: hpp > 0, hargaTerbaru: terbaru,", "hpp, nilai: sisa * (terbaru || hpp), bisaDinilai: hpp > 0, hargaTerbaru: terbaru,"),
            'pembanding harga beli terbaru tidak disebut': js.replace("' · bila dinilai HARGA BELI TERBARU: ' + RP(totalTerbaru)", "''"),
            'stok tak bergerak digambar sebagai NOL hari (bukan tidak terukur)': js.replace("if (b.laju <= 0) out.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: b.bisaDinilai", "if (false) out.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: b.bisaDinilai"),
            'barang yang belum pernah dicocokkan dianggap baru dicocokkan': js.replace("awas: umur === null || umur >= HARI_COCOK_AWAS, umur: umur === null ? 1e6 : umur,", "awas: umur !== null && umur >= HARI_COCOK_AWAS, umur: umur === null ? 0 : umur,"),
            'papan kapur memuat baris yang dibatalkan / hari lain': js.replace("const jual = {}; const takaran = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== hari) return;", "const jual = {}; const takaran = {}; ambilPenjualanSemua().forEach((p) => {"),
            'karantina menampilkan yang sudah diputuskan': js.replace(".filter((k) => (k.statusTindakan || 'belum_diputuskan') === 'belum_diputuskan')", ""),
            'angka kebijakan owner diabaikan (tetap 50 kg)': js.replace("const penuhKg = a && Number(a.penuhKg) > 0 ? Number(a.penuhKg) : WADAH_PENUH_KG;", "const penuhKg = WADAH_PENUH_KG;"),
            'aturan wadah yang mustahil diterima (isi ulang ≥ penuh)': js.replace("if (!(ulang >= 0) || ulang >= penuh) return { tolak:", "if (false) return { tolak:"),
            'aturan LAMA yang dipakai (bukan yang terbaru)': js.replace("const wdTerbaru = (daftar) => daftar.reduce((a, x) => (!a || wdSesudah(x, a) ? x : a), null);", "const wdTerbaru = (daftar) => daftar.reduce((a, x) => (!a || wdSesudah(a, x) ? x : a), null);"),
            'posisi wadah tidak mengikuti susunan owner': js.replace("const daftar = atur.daftar.map((m, i) => { const kn = karungUntukWadah(m);", "const daftar = atur.daftar.slice().sort().map((m, i) => { const kn = karungUntukWadah(m);"),
            'karung di belakang wadah tidak ikut digambar di layar Stok': js.replace("karung: kr, tumpukan: tumpukanGudang(asal, siap) }, tinggiWadah(m, s)); });", "karung: { diketahui: false }, tumpukan: tumpukanGudang(asal, siap) }, tinggiWadah(m, s)); });"),
            'tumpukan gudang lupa mengurangi isi wadah': js.replace("const kg = wdB2(namaKg - diBelakang - diWadah); const berat", "const kg = wdB2(namaKg - diBelakang); const berat"),
            'perkiraan yang belum lengkap disebut lengkap': js.replace("lengkap: (!w || w.diketahui) && pemegang.every((x) => kolam.some((k) => k.lokasi === x)), minus: kg < -0.0001 };", "lengkap: true, minus: kg < -0.0001 };"),
            'buka karung tidak menurunkan tumpukan di tab Gudang': js.replace("const kg = wdB2(namaKg - diBelakang - diWadah); const berat", "const kg = wdB2(namaKg - diWadah); const berat"),
            'kartu "Berasnya ada di mana?" hilang': js.replace("    { id: 'lokasi', q: 'Berasnya ada di mana?',", "    false && { id: 'lokasi', q: 'Berasnya ada di mana?',").replace("  ];\n  const aktif = kartu.some", "  ].filter(Boolean);\n  const aktif = kartu.some"),
            'petak wadah memakai karung senama, bukan karung yang dicatat di belakangnya': js.replace("karungNama: kn.merk, karungAsal: asal, karungDicatat: kn.dariCatatan, karung: kr, tumpukan: tumpukanGudang(asal, siap)", "karungNama: m, karungAsal: m, karungDicatat: kn.dariCatatan, karung: karungBelakang(m, m), tumpukan: tumpukanGudang(m, siap)"),
            'karung lama yang wadahnya sudah berganti karung hilang dari layar': js.replace("siap.kolam.forEach((k) => { if (k.wadah) return;", "siap.kolam.forEach((k) => { if (k.wadah || k.yatim) return;"),
            'karung yatim (wadahnya berganti karung) masih dihitung milik wadah itu': js.replace("wadah: pegang ? L : '', yatim: !!L && !pegang };", "wadah: L, yatim: false };"),
            # putaran 27 (Bagian 5): takar tidak lagi menulis produksi pindah buku — kontrol pindah buku di papan kapur diganti 1:1
            'takar bukuAsal di papan kapur tidak menyebut buku tetap milik merek karungnya': js.replace("(w.bukuAsal ? ' (buku tetap milik merek karungnya)' : w.stokWadah", "(false ? '' : w.stokWadah"),
            'karung 25 kg dibuka sebagai 50 kg': js.replace("return !merkPunyaKarungBerat(asal, 50) && merkPunyaKarungBerat(asal, 25) ? 25 : KARUNG_BELAKANG_KG;", "return KARUNG_BELAKANG_KG;"),
            'yang belum ditandai ditulis 0 kg (bukan "?")': js.replace("(t.karungDiketahui ? skKG(t.diBelakangKg) : t.karungDiWadah ? '? (belum ditandai)' : '—')", "skKG(t.diBelakangKg)"),
            'rework karantina dianggap hitungan gudang di kartu cocokkan': js.replace("ambilPenyesuaianStok().forEach((p) => { if (!hitunganFisik(p) || (p.bagian === 'wadah' && (!bw[p.merk] || bw[p.merk].jenis === 'adukan'))) return;", "ambilPenyesuaianStok().forEach((p) => { if ((p.bagian === 'wadah' && (!bw[p.merk] || bw[p.merk].jenis === 'adukan'))) return;"),
            'papan kapur tidak menyebut di belakang wadah mana karung dibuka': js.replace("(w.wadah ? 'di belakang wadah ' + w.wadah : w.lepas ? 'sebagai bahan campuran' : 'di belakang wadah')", "'di belakang wadah'"),
            'bahan campuran yang bukan wadah tidak tampil': js.replace("daftar.forEach((w) => w.resep.forEach((x) => sebut(x.merk)));", ""),
            'papan kapur tidak mencatat takar isi ulang': js.replace("if (w.tipe === 'takar') out.push(", "if (false) out.push("),
            # ---- Barang masuk (ST1) & Cocokkan (ST3), 23 Sep ----
            'upah bongkar tidak masuk HPP per kg': js.replace("sah.forEach((b, i) => { b.alokasiBongkar = Math.round(hpp[i].alokasiBongkar); b.hppPerKg = hpp[i].hppPerKg; });", "sah.forEach((b, i) => { b.alokasiBongkar = 0; b.hppPerKg = b.hargaPerKg; });"),
            'baris terisi tanpa harga ikut tersimpan diam-diam': js.replace("if (h.bermasalah.length) return { tolak: 'Baris '", "if (false) return { tolak: 'Baris '"),
            'kedatangan sedikit tidak ditanya': js.replace("if (h.karung < atur.minKarung && !yakin) return", "if (false) return"),
            'koreksi menulis dokumen BARU (kedatangan jadi dua)': js.replace("const data = { id: lama ? lama.id : w.idUnik(),", "const data = { id: w.idUnik(),"),
            'batch fondasi boleh dihapus': js.replace("if (ccFondasi(b)) return { tolak: 'Batch fondasi ('", "if (false) return { tolak: 'Batch fondasi ('"),
            'hapus kedatangan tidak mencabut pasangan beli-jadi': js.replace(".concat(pasangan.map((p) => ({ koleksi: 'produksiKemasan', id: p.id })))", ""),
            'aturan owner diabaikan (minimal karung tetap 60)': js.replace("return { minKarung: ambil('minKarung', (n) => n >= 0),", "return { minKarung: 60,"),
            'selisih cocokkan tanpa rupiah (nilaiRp 0)': js.replace("const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = ada ? (b.tab === 'tumpukan' ? ckRpKarung(b.nama, selisih, b.modal) : Math.round(selisih * b.modal)) : 0;", "const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = 0;"),
            'selisih besar tidak minta alasan': js.replace("perluAlasan: besar && !String(A[b.kunci] || '').trim(),", "perluAlasan: false,"),
            'opname ganda dalam jendela menit tidak ditanya': js.replace("if (ganda.length && !(yakin || {}).ganda) return", "if (false) return"),
            'angka aneh (lebih dari dua kali tercatat) tidak ditanya': js.replace("else if (anehDaftar.length && !Y.aneh) {", "else if (false) {"),
            'stok bertambah tanpa pembelian di atas ambang tidak ditanya': js.replace("else if (lebihRp > atur.ambangSusutPositif && !Y.susutPositif) {", "else if (false) {"),
            'kolom dokumen cocokkan beda dari sistem berjalan (kgFisik hilang)': js.replace("merk: b.nama, kgSistem: b.buku, kgFisik: ckB2(b.buku + b.selisih), selisihKg: b.selisih,", "merk: b.nama, kgSistem: b.buku, selisihKg: b.selisih,"),
            'rework karantina masuk riwayat hitungan fisik': js.replace("ambilPenyesuaianStok().forEach((d) => { if (hitunganFisik(d)) semua.push(", "ambilPenyesuaianStok().forEach((d) => { if (true) semua.push("),
            # ---- Adukan (ST2) & Karantina, 23 Sep ----
            'sumberList ditulis di SEMUA baris hasil (stok bahan terpotong berlipat)': js.replace("sumberList: i === 0 ? h.sahB.map((b) => ({ merk: b.merk, kg: b.kg })) : [], kgDipakai: i === 0 ? h.kgDipakai : 0,", "sumberList: h.sahB.map((b) => ({ merk: b.merk, kg: b.kg })), kgDipakai: h.kgDipakai,"),
            'pembagian biaya dihitung sendiri (sisa pembulatan tidak jatuh ke baris terakhir)': js.replace("const bagi = bagiBiayaAdukan(sahH.map((h) => ({ ukuranKemasan: h.ukuran, jumlahUnit: h.unit })), total) || [];", "const bagi = sahH.map((h) => Math.round(total * h.ukuran / (kgJadi || 1)));"),
            'pemakaian kantong tidak ditulis (kantong terhitung gratis diam-diam)': js.replace("if (x.kantongJenis && x.kantongJumlah > 0) dokumen.push({ koleksi: 'stokBahanKemasan'", "if (false) dokumen.push({ koleksi: 'stokBahanKemasan'"),
            'biaya kantong tidak masuk modal adukan': js.replace("const biayaKantong = pakaiKantong ? Math.round(((stokB[kantongJenis] || {}).hppPerPcs || 0) * kantongJumlah) : 0;", "const biayaKantong = 0;"),
            'bahan = hasil (lingkaran) diterima': js.replace("if (h.lingkaran.length) { const x = h.lingkaran[0]; return { tolak:", "if (false) { const x = h.lingkaran[0]; return { tolak:"),
            'stok bahan kurang tidak ditanya': js.replace("if (h.kurangBahan.length && !Y.bahan) {", "if (false) {"),
            'kantong dipilih tanpa lembar tidak ditanya': js.replace("if (h.kantongTanpaCacah.length && !Y.kantongKosong) {", "if (false) {"),
            'susut adukan besar tidak ditanya': js.replace("&& !Y.susut) return { tolak: 'Bahan '", "&& false) return { tolak: 'Bahan '"),
            'koreksi mengubah SATU baris saja (Σ tidak lagi = biaya adukan)': js.replace("baris.forEach((x, i) => { const idBaru = w.idUnik(); const pengganti", "baris.slice(0, 1).forEach((x, i) => { const idBaru = w.idUnik(); const pengganti"),
            'dokumen lama tidak ditandai dikoreksiOleh (dihitung dua kali)': js.replace("dokumen.push({ koleksi: 'produksiKemasan', data: pengganti }); dokumen.push({ koleksi: 'produksiKemasan', data: Object.assign({}, x, { dikoreksiOleh: idBaru, alasanKoreksi: String(alasan).trim() }) }); });", "dokumen.push({ koleksi: 'produksiKemasan', data: pengganti }); });"),
            'koreksi dengan baris seadukan tidak lengkap diterima': js.replace("if (baris.length !== r.jumlahBaris) return { tolak: 'Koreksi ditolak: adukan ini seharusnya", "if (false) return { tolak: 'Koreksi ditolak: adukan ini seharusnya"),
            'hapus adukan yang hasilnya sudah terjual diperbolehkan (stok kemasan minus)': js.replace("if (!r.bisaHapus) return { tolak: 'Hapus ditolak: ' + r.takBisaHapus };", ""),
            'hapus adukan tidak mencabut pasangan kantong (id + 1)': js.replace("hapus.push({ koleksi: 'stokBahanKemasan', id: p.id + 1 });", ""),
            'beli-jadi dari kedatangan tampil sebagai adukan': js.replace("if (jenis === 'beliJadi' || jenis === 'pindahBuku') return null;", "if (false) return null;"),
            'bahan dari kemasan jadi tidak dicatat di sumberKemasanList (unit tidak hilang)': js.replace("sumberKemasanList: i === 0 ? h.sahBK.map((k) => ({ namaProduk: k.namaProduk, ukuranKemasan: k.ukuranKemasan, unit: k.unit, hppPerUnitSaatDipakai: Math.round(k.hpp) })) : [],", "sumberKemasanList: [],"),
            'karantina: rework/buang diterima walau returnya sudah dikoreksi layak jual (barang bergerak dua kali)': js.replace("if (r && r.kondisi === 'utuh') return 'Retur asal barang ini sudah dikoreksi LAYAK JUAL", "if (false) return 'Retur asal barang ini sudah dikoreksi LAYAK JUAL"),
            'karantina: layak jual tidak mengoreksi returnya (stok tidak bergerak)': js.replace("return { dokumen: [dokR, status], patch: { kabar: 'Dikoreksi layak jual: '", "return { dokumen: [status], patch: { kabar: 'Dikoreksi layak jual: '"),
            'karantina: rework karung menulis nilai rupiah (menyentuh laba)': js.replace("nilaiRp: 0, hppPerKgSaatOpname: 0, dariRework: true } });", "nilaiRp: 1, hppPerKgSaatOpname: 0, dariRework: true } });"),
            'karantina: rework yang sudah ada dokumennya boleh diulang': js.replace("if (kqSudahRework(k)) return 'Sudah pernah di-rework", "if (false) return 'Sudah pernah di-rework"),
            'karantina: cocokkan sesudah retur tidak ditanya': js.replace("if (opname.length && yakin !== 'layak_jual') return { tolak:", "if (false) return { tolak:"),
            'karantina: buang / balik tanpa ketukan kedua': js.replace("if (yakin !== tindakan) return { tolak: (tindakan === 'dibuang'", "if (false) return { tolak: (tindakan === 'dibuang'"),
            'karantina: pilihan yang tampil memakai penjaga lain dari yang menulis': js.replace("pilihan: TINDAKAN_KARANTINA.map(([t, label]) => { const sebab = kqPeriksa(k, t, w);", "pilihan: TINDAKAN_KARANTINA.map(([t, label]) => { const sebab = '';"),
            'karantina: rework kemasan memakai modal Rp0 (bukan rata-rata sekarang)': js.replace("const hpp = (hitungStokKemasan()[kKem] || {}).hppRataRataPerUnit || 0;", "const hpp = 0;"),
            'karantina: barang yang sudah di-rework masih tampil di antrean': js.replace(".filter((k) => (k.statusTindakan || 'belum_diputuskan') === 'belum_diputuskan').map((k) => { const r = kqRetur(k.id);", ".map((k) => { const r = kqRetur(k.id);"),
            # ---- ST4 Kantong, ST5 Tempat simpan, ST6 HPP (23 Sep) ----
            'kantong: harga di bawah lantai tidak ditanya': js.replace("if (h.murah && !Y.murah) return { tolak: h.murahTeks", "if (false) return { tolak: h.murahTeks"),
            'kantong: lonjakan harga tidak ditanya': js.replace("if (h.lonjak && !Y.lonjak) return { tolak: h.lonjakTeks", "if (false) return { tolak: h.lonjakTeks"),
            'kantong: harga per lembar diambil dari total ÷ jumlah (bukan yang diketik)': js.replace("const hargaDokBeli = (b) => (Number(b.hargaPerPcs) > 0 ? Math.round(Number(b.hargaPerPcs)) :", "const hargaDokBeli = (b) => (false ?"),
            'kantong: harga terakhir memakai rata-rata buku (bukan beli terbaru)': js.replace("const beli = ktBeliJenis(jenis); if (beli.length) return { harga: hargaDokBeli(beli[0]), sejak: beli[0].tanggal || '', dariRata: false, nBeli: beli.length };", "const beli = ktBeliJenis(jenis);"),
            'kantong: batch yang lembarnya sudah terpakai bisa dihapus (buku minus)': js.replace("if (sisaSesudah < 0) return { tolak:", "if (false) return { tolak:"),
            'kantong: karung bekas (hasil samping) ikut dibeli': js.replace("function jenisKantong() { return daftarJenisWadah().filter((d) => !d.hasilSamping); }", "function jenisKantong() { return daftarJenisWadah(); }"),
            'kantong: stok aman setelan diabaikan': js.replace("awas: hariCukup !== null && hariCukup < atur.hariAman,", "awas: hariCukup !== null && hariCukup < 7,"),
            'kantong: jenis tanpa pemakaian dianggap cukup 0 hari': js.replace("const hariCukup = l > 0 ? sisa / l : null;", "const hariCukup = l > 0 ? sisa / l : 0;"),
            'tempat: pindah ke tempat yang sama tetap dicatat': js.replace("if ((brg.tempat || '') === ke) return { tolak: brg.nama + ' memang sudah di '", "if (false) return { tolak: brg.nama + ' memang sudah di '"),
            'tempat: dikosongkan disimpan sebagai string kosong (bukan dibuang)': js.replace("if (ke) peta[kunci] = ke; else delete peta[kunci];", "peta[kunci] = ke;"),
            'tempat: tempat berisi dihapus TANPA memindahkan barangnya ke "tanpa tempat" (peta tetap menunjuk tempat yang sudah hilang)': js.replace("  if (berisi.length) { const peta = petaTempat(); berisi.forEach((b) => { delete peta[b.kunci];", "  if (false) { const peta = petaTempat(); berisi.forEach((b) => { delete peta[b.kunci];"),
            'tempat: menumpuk pakai angka mati': js.replace("tumpuk: pct > atur.batasTumpuk,", "tumpuk: pct > 50,"),
            'tempat: peta sistem lama tidak dibaca (tempat teks hilang)': js.replace("Object.keys(petaTempat()).forEach((k) => { const nm = String(petaTempat()[k] || '').trim(); if (nm && !daftar.some((t) => t.nama === nm)) daftar.push({ nama: nm, posisi: '' }); });", ""),
            'tempat: pindahan tanpa catatan': js.replace("{ koleksi: 'pindahTempat', data: { id: w.idUnik(), tanggal: w.tanggal, jam: w.jam, kunci, barang: brg.nama, dari: brg.tempat || '', ke } }],", "],"),
            'hpp: lantai dipotong diam-diam (jepitan)': js.replace("if (n < atur.lantaiHpp) return { tolak: RP(n) + '/kg di bawah lantai '", "if (false) return { tolak: RP(n) + '/kg di bawah lantai '"),
            'hpp: tiga kali lipat lolos': js.replace("if (K.modal > 0 && n > K.modal * atur.kaliMaks) return { tolak:", "if (false) return { tolak:"),
            'hpp: ambang rugi pakai >= (margin nol jadi RUGI)': js.replace("const teksMargin = (m) => (m === null ? 'harga jual per kg belum ada di katalog' : m < 0 ?", "const teksMargin = (m) => (m === null ? 'harga jual per kg belum ada di katalog' : m <= 0 ?"),
            'hpp: koreksi tanpa alasan lolos': js.replace("if (hpKosong(alasan)) return { tolak: 'Koreksi HPP butuh alasan", "if (false) return { tolak: 'Koreksi HPP butuh alasan"),
            'hpp: lonjakan tidak ditanya': js.replace("if (v.lonjak && !yakin) return { tolak: 'HPP: ' + v.lonjak", "if (false) return { tolak: 'HPP: ' + v.lonjak"),
            'hpp: Δ nilai rak salah (tanpa sisa kg)': js.replace("const delta = (modalBaru - K.modal) * Math.max(0, K.sisa);", "const delta = (modalBaru - K.modal);"),
            'hpp: replika rumus melewatkan bongkar (≠ mesin)': js.replace("function totalMasuk(merk) { let kg = 0, nilai = 0; riwayatModal(merk).forEach((r) => { kg += r.totalKg; nilai += r.hppPerKg * r.totalKg; });", "function totalMasuk(merk) { let kg = 0, nilai = 0; riwayatModal(merk).forEach((r) => { kg += r.totalKg; nilai += r.hargaPerKg * r.totalKg; });"),
            'hpp: massal menyimpan sebagian': js.replace("if (salah.length) return { tolak: salah.join(' · ') + ' — TIDAK ADA yang disimpan sampai semuanya beres', salah };", ""),
            'hpp: koreksi menulis batch BARU (kedatangan jadi dua)': js.replace("d.baris.forEach((b) => { if (perBatch[id][b.merk] !== undefined) b.hargaPerKg = String(perBatch[id][b.merk]); }); d.alasan = 'koreksi HPP: ' + w.alasan;", "d.id = null; d.baris.forEach((b) => { if (perBatch[id][b.merk] !== undefined) b.hargaPerKg = String(perBatch[id][b.merk]); }); d.alasan = 'koreksi HPP: ' + w.alasan;"),
            'hpp: kedatangan fondasi ikut dikoreksi': js.replace("const target = riw.filter((r) => r.jenis === 'kedatangan' && !r.fondasi).slice(-1)[0] || null;", "const target = riw.filter((r) => r.jenis === 'kedatangan').slice(-1)[0] || null;"),
            # ---- audit 39b no. 2: kedatangan bon yang sudah dibayar
            'bon dibayar boleh diubah jadi tunai': js.replace("    if (cara !== 'utang') return { tolak: ckKalimatBayar(bb) + ' — tidak bisa diubah jadi tunai. '", "    if (false) return { tolak: ckKalimatBayar(bb) + ' — tidak bisa diubah jadi tunai. '"),
            'bon dibayar boleh ganti pemasok': js.replace("    if (pemasok !== String(lama.pemasok || '').trim()) return { tolak: ckKalimatBayar(bb) + ' atas nama '", "    if (false) return { tolak: ckKalimatBayar(bb) + ' atas nama '"),
            'tanggal datang bon dibayar boleh diubah': js.replace("    if (String(draf.tanggal) !== String(lama.tanggal || '')) return", "    if (false) return"),
            'nilai bon boleh di bawah yang dibayar': js.replace("    if (h.nilaiBeras + h.nilaiBal + 0.5 < bb.dibayar) return", "    if (false) return"),
            'tanggal bon yang terbayar lewat aliran boleh diubah': js.replace("  if (bb && bb.dibayar <= 0 && bb.dibayarMesin > 0 && String(draf.tanggal) !== String(lama.tanggal || '')) return", "  if (false) return"),
            'koreksi massal dua nama sekedatangan dinilai sendiri-sendiri': js.replace("function hpKunciBonGabung(nilai) {\n  const per = {};", "function hpKunciBonGabung(nilai) { return {};\n  const per = {};"),
            'nama beras tercetak dua kali di penolakan massal': js.replace("salah.push(v.tolak.indexOf(m + ':') === 0 ? v.tolak : m + ': ' + v.tolak)", "salah.push(m + ': ' + v.tolak)"),
            'hapus kedatangan bon dibayar lolos': js.replace("  const bb = ckBayarBon(b); if (bb.dibayar > 0) return { tolak: ckKalimatBayar(bb) + ' — kedatangan ini tidak bisa dihapus:", "  const bb = ckBayarBon(b); if (false) return { tolak: ckKalimatBayar(bb) + ' — kedatangan ini tidak bisa dihapus:"),
            'kunci ikut aliran tanpa tujuan / kelebihan bayar (kedatangan salah catat tak bisa dihapus)': js.replace("const dibayar = Math.round(Math.min(nilai, tunjuk));", "const dibayar = Math.round(nilai - ((hitungUtangPemasok().find((p) => p.pemasok === pem) || { bon: [] }).bon.filter((x) => String(x.id) === id).reduce((a, x) => a + x.sisa, 0)));"),
            'pembayaran pemasok lain yang menunjuk bon ikut dihitung': js.replace("&& String(m.bonId || '') === id && String(m.pemasok || '').trim() === pem)", "&& String(m.bonId || '') === id)"),
            'koreksi HPP tidak menolak lebih dulu (pratinjau & massal buta kunci bon)': js.replace("    if (nilaiBon + 0.5 < bb.dibayar) return { tolak: merk + ': kedatangan terakhirnya", "    if (false) return { tolak: merk + ': kedatangan terakhirnya"),
            'ejaan pemasok tidak disamakan': js.replace("const pemasok = ckEjaanPemasok(pemasokKetik, lama ? lama.id : null);", "const pemasok = pemasokKetik;"),
            'ejaan lama kedatangan yang dikoreksi memaksa (koreksi ejaan tunggal tidak bisa)': js.replace("(kecualiId !== undefined && kecualiId !== null && String(b.id) === String(kecualiId))", "false"),
            # ---- audit 39b no. 30: koreksi kedatangan berbaris bal
            'koreksi kedatangan membuang baris bal (bon & porsi bongkar bergeser)': js.replace(".concat(ckBarisBal(lama).map((m, j) => Object.assign({}, m, { id: String(h.sah.length + j + 1) })))", ".concat([])"),
            'baris bal tertulis tapi nilainya tidak dihitung di pagar bon dibayar': js.replace("if (h.nilaiBeras + h.nilaiBal + 0.5 < bb.dibayar) return", "if (h.nilaiBeras + 0.5 < bb.dibayar) return"),
            'koreksi HPP satu nama: nilai bal tidak dihitung di pagar bon dibayar': js.replace("(m.bentuk === 'bal' ? (Number(m.subtotalHarga) || 0) : m.merk === merk ?", "(m.bentuk === 'bal' ? 0 : m.merk === merk ?"),
            'koreksi HPP massal: nilai bal tidak dihitung di pagar bon dibayar bersama': js.replace("(x.bentuk === 'bal' ? (Number(x.subtotalHarga) || 0) : ms.indexOf(x.merk) >= 0 ?", "(x.bentuk === 'bal' ? 0 : ms.indexOf(x.merk) >= 0 ?"),
            'kabar koreksi diam soal baris bal': js.replace("(h.nilaiBal ? ' + baris bal ' + RP(h.nilaiBal) + ' (tidak diubah)' : '')", "''"),
            'pratinjau koreksi: bongkar tidak dibagi ke baris bal (modal karung kelebihan)': js.replace(".concat(bal.map((m) => ({ merk: m.merk, totalKg: Number(m.totalKg) || 0, subtotalHarga: Number(m.subtotalHarga) || 0 }))), bongkar);", ", bongkar);"),
            'kartu Jumlah: total tanpa nilai bal': js.replace("total: nilaiBeras + nilaiBal + bongkar,", "total: nilaiBeras + bongkar,"),
            'riwayat modal: bongkar tidak dibagi ke baris bal (beda dengan mesin)': js.replace("hitungHppMerkDalamBatch(k.merkList || [], Number(k.biayaBongkar) || 0).forEach((m) => { if (m.bentuk === 'bal' ||", "hitungHppMerkDalamBatch((k.merkList || []).filter((m) => m.bentuk !== 'bal'), Number(k.biayaBongkar) || 0).forEach((m) => { if (m.bentuk === 'bal' ||"),
            'riwayat modal: baris bal ikut jadi kedatangan karung': js.replace("forEach((m) => { if (m.bentuk === 'bal' || m.merk !== merk || !(m.totalKg > 0)) return;", "forEach((m) => { if (m.merk !== merk || !(m.totalKg > 0)) return;"),
            'hpp: batas lonjakan setelan diabaikan': js.replace("lonjak: Math.abs(pct) > atur.batasLonjak ? (K.fifo ? 'nilai rak per kg ' : 'modal rata-rata ')", "lonjak: Math.abs(pct) > 10 ? (K.fifo ? 'nilai rak per kg ' : 'modal rata-rata ')"),
        }
        kode = 0
        for nama, pot in POT30:
            hs = statis30(sk30.replace(pot, '')) if pot in sk30 else []
            print(('BERBUNYI ' if hs else ('KONTROL BASI  ' if pot not in sk30 else 'DIAM!!   ')) + 'statis 39b no. 30: ' + nama + ' dihapus'); kode = kode if hs else 3
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        # paket brief 9 Okt: umur & putaran — kotak pasirnya sendiri
        for nama, isi in rusak_umur(js).items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama_umur(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    lu, gu = utama_umur(js); l += lu; g += gu   # paket brief 9 Okt: umur & putaran
    g += ['statis 39b no. 30: ' + n for n in statis30(sk30)]
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)   # cadangan toko boleh di akar, _privat/ atau _arsip-mockup/ (semua di-gitignore); yang terbaru menurut tanggal di namanya
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        h, e = jalan("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s): nilai stok layar = Σ barang bersisa positif: %s · mesin neraca (termasuk yang minus): selisih %s · %d barang · beli %d · mandek %d · cocok %d · kapur %d · wadah %d'
                  % (os.path.basename(cad[-1]), h['nilaiLayar'] == h['nilaiPositif'], 'nol' if h['neraca'] == h['nilaiLayar'] else ('ada stok minus' if h['minus'] else 'ADA — periksa'), h['barang'], h['beli'], h['mandek'], h['cocok'], h['kapur'], h['wadah']))
            if h['nilaiLayar'] != h['nilaiPositif'] or (h['neraca'] != h['nilaiLayar'] and not h['minus']): g.append('asap: nilai stok layar tidak cocok dengan mesin')
            print('ASAP DATA TOKO: kolom dokumen catat (barang masuk, cocokkan, adukan, kantong) vs cadangan: %s · %d adukan di buku · %d menunggu di karantina' % (', '.join(h['kunciAsingCatat']) or 'semua dikenal', h['adukan'], h['karantinaAntre']))
            if h['kunciAsingCatat']: g.append('asap: dokumen catat punya kolom yang tidak dikenal cadangan')
            b2 = h.get('bon2') or {}
            print('   39b no. 2 — kedatangan bon di data toko: %d bon · %d sudah dibayar bertunjuk (Rp%s) · terkunci %d · di bulan terkunci %d · lolos %s · bon belum dibayar yang salah dikunci %s · Σ sisa vs mesin selisih %s · bertunjuk ≠ mesin %s · ejaan pemasok yang digeser %s'
                  % (b2.get('bon', 0), b2.get('dibayar', 0), format(b2.get('rpDibayar', 0), ',').replace(',', '.'), b2.get('kunci', 0), b2.get('kunciPeriode', 0), b2.get('lolos') or 'nihil', b2.get('bebasSalah') or 'nihil', b2.get('selisihMesin'), b2.get('bedaMesin') or 'nihil', b2.get('ejaanGeser') or 'nihil'))
            if not b2.get('bon') or b2.get('kunci') + b2.get('kunciPeriode', 0) < b2.get('dibayar') or b2.get('lolos') or b2.get('bebasSalah') or b2.get('selisihMesin') or b2.get('ejaanGeser'): g.append('asap 39b no. 2: ' + json.dumps(b2, ensure_ascii=False)[:400])
        # paket brief 9 Okt: umur & putaran atas data toko — sisa = sumber Gudang, tiap buku menutup (bertanggal + tanpa tanggal = sisa), wadah = rata-rata
        hu, eu = jalan("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP_UMUR)
        if hu is None: print('ASAP UMUR: JSC JATUH ' + eu); g.append('asap umur')
        else:
            print('ASAP UMUR & PUTARAN (%s): %d buku · sisa positif %s kg = bertanggal %s + tanpa tanggal %s · minus %s · putaran tumpukan merek %s× / %d hari%s'
                  % (os.path.basename(cad[-1]), hu['n'], hu['sisa'], hu['bertanggal'], hu['tanpa'], hu['minus'] or 'tidak ada', hu['putaran'], hu['periode']['n'], (' (' + hu['periode']['catat'] + ')') if hu['periode']['catat'] else ''))
            print('   5 merek tertua umur stoknya: ' + ' · '.join(hu['tertua']))
            print('   lambat laku (%d): %s' % (len(hu['lambat']), ' · '.join(hu['lambat']) or 'tidak ada'))
            print('   putaran belum bisa dihitung (keluar > 0, sisa rata-rata tidak positif — tinjauan no. 14): %s' % (' · '.join(hu['belumHitung']) or 'tidak ada'))
            if hu['salah']: g.append('asap umur: ' + '; '.join(hu['salah'])[:400])
    sys.exit(2 if g else 0)
