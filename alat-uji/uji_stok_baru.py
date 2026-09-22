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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/stok-logika.js']
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
var AT = susunAturWadah({ penuhKg: '60', puncakKg: '70', isiUlangKg: '15', takarKg: '1,8', daftar: ['IR64 Apex', 'Angsa'] }, WW);
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
ok('9 takar campuran 6 : 3 (16,2 kg) → wadah 51,8 + 16,2 = 68 kg (di atas rata 60 → menggunung 0,8); karung Apex di belakang 50 − 10,8 = 39,2 kg; BUKU stok Apex TIDAK berubah', wa.sisaKg === 68 && wa.gunung === 0.8 && wa.karung.sisaKg === 39.2 && daftarBarang().find(function (b) { return b.nama === 'IR64 Apex' && b.jenis === 'karung'; }).sisa === bukuApex, JSON.stringify([wa.sisaKg, wa.gunung, wa.karung]));
ok('tumpukan gudang Apex = buku + 5,4 (3 takar Angsa yang PINDAH NAMA ke wadah Apex) − 39,2 (karung terbuka) − 68 (wadah); lengkap karena keduanya sudah ditandai; tumpukan ANGSA = bukunya − 5,4 (berasnya sudah di wadah Apex)', Math.abs(wa.tumpukan.kg - (bukuApex + 5.4 - 39.2 - 68)) < 0.011 && wa.tumpukan.pindahMasukKg === 5.4 && Math.abs(W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).tumpukan.kg - (brg('Angsa').sisa - 5.4)) < 0.011 && wa.karungNama === 'IR64 Apex' && wa.karungDicatat === true && wa.tumpukan.lengkap === true && wa.tumpukan.karung === Math.max(0, Math.floor((wa.tumpukan.kg + 0.0001) / 50)), JSON.stringify(wa.tumpukan));
ok('karung Angsa yang ikut dicampur belum pernah ditandai → TIDAK diketahui, dan tumpukan Angsa disebut "perkiraan belum lengkap"', W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).karung.diketahui === false && W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).tumpukan.lengkap === false);
var K2 = susunKapur(KINI);
ok('papan kapur: "diisi ulang 9 takar dari karung IR64 Apex 6 + Angsa 3" +16,2 kg · "Karung IR64 Apex diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex" gudang −50 kg', K2.baris.some(function (x) { return x.jenis === 'wadah' && /Wadah IR64 Apex diisi ulang 9 takar dari karung IR64 Apex 6 \+ Angsa 3/.test(x.isi) && x.n === '+16,2 kg'; }) && K2.baris.some(function (x) { return /Karung IR64 Apex diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex/.test(x.isi) && x.n === 'gudang −50 kg'; }), JSON.stringify(K2.baris.filter(function (x) { return x.jenis === 'wadah'; })));
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
ok('jumlahnya menutup untuk SEMUA nama: tumpukan + karung terbuka + isi wadah = buku − pindah keluar + pindah masuk', susunLokasi().every(function (t) { return Math.abs(t.kg + t.diBelakangKg + t.diWadahKg - (t.bukuKg - t.pindahKeluarKg + t.pindahMasukKg)) < 0.011; }), JSON.stringify(susunLokasi()));
terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 7001, tanggal: '2026-09-19', jam: '11:00', merk: 'Angsa', kgSistem: null, kgFisik: null, selisihKg: 41.5, alasan: 'Rework', dariRework: true } }]);
ok('tinjau 22 Sep: rework dari karantina (dariRework, kgFisik null) BUKAN hitungan gudang — Angsa tetap "3 hari sejak cocok", bukan 0', susunGudang('cocok', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).n === '3 hari', JSON.stringify(susunGudang('cocok', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; })));
terapkanKeCache([{ koleksi: 'penyesuaianStok', hapus: 7001 }]);
ok('Pandan Wangi cuma pernah masuk sebagai karung 25 kg → satu karungnya 25 kg (bukan 50)', beratKarungBuka('Pandan Wangi') === 25 && beratKarungBuka('Angsa') === 50 && susunBukaKarung('Pandan Wangi', WW, '').dokumen[0].data.kg === 25 && susunBukaKarung('Pandan Wangi', WW, '').dokumen[0].data.lepas === true);
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var G = susunGudang('modal', KINI); var N = hitungNeraca();
var stokK = hitungStokKarungPerMerk(), stokM = hitungStokKemasan(); var positif = 0;
Object.keys(stokK).forEach(function (m) { if ((stokK[m].sisaKg || 0) > 0) positif += stokK[m].sisaKg * (stokK[m].hppTerakhirPerKg || 0); });
Object.keys(stokM).forEach(function (k) { if ((stokM[k].sisaUnit || 0) > 0) positif += stokM[k].sisaUnit * (stokM[k].hppRataRataPerUnit || 0); });
print(JSON.stringify({ nilaiLayar: Math.round(G.jawab.total), nilaiPositif: Math.round(positif), neraca: N.nilaiSack + N.nilaiBags, minus: N.adaStokMinus, barang: G.banyakBarang, beli: susunGudang('beli', KINI).jawab.baris.length, mandek: susunGudang('mandek', KINI).jawab.baris.length, cocok: susunGudang('cocok', KINI).jawab.baris.length, kapur: susunKapur(KINI).banyak, wadah: susunWadah(keadaanAwal()).daftar.length }));
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
            'barang tanpa gerak 14 hari dianggap AMAN (tidak disebut)': js.replace("if (b.laju <= 0) { if (b.sisa > 0) tak.push(b.nama); return; }", "if (b.laju <= 0) { return; }"),
            'jumlah beli tidak dibulatkan ke karung penuh': js.replace("Math.ceil(kurang / b.beratKarung) + ' karung'", "Math.floor(kurang / b.beratKarung) + ' karung'"),
            'target isi 7 hari diabaikan (semua barang disuruh beli)': js.replace("if (b.hariHabis > HARI_TARGET) return;", ""),
            'nilai di buku diganti harga beli terbaru (beda dengan Neraca sistem lama)': js.replace("hpp, nilai: sisa * hpp, bisaDinilai: hpp > 0, hargaTerbaru: terbaru,", "hpp, nilai: sisa * (terbaru || hpp), bisaDinilai: hpp > 0, hargaTerbaru: terbaru,"),
            'pembanding harga beli terbaru tidak disebut': js.replace("' · bila dinilai HARGA BELI TERBARU: ' + RP(totalTerbaru)", "''"),
            'stok tak bergerak digambar sebagai NOL hari (bukan tidak terukur)': js.replace("if (b.laju <= 0) out.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: b.bisaDinilai", "if (false) out.push({ kunci: b.jenis + '|' + b.kunci, nama: b.nama, n: b.bisaDinilai"),
            'barang yang belum pernah dicocokkan dianggap baru dicocokkan': js.replace("awas: umur === null || umur >= HARI_COCOK_AWAS, umur: umur === null ? 1e6 : umur,", "awas: umur !== null && umur >= HARI_COCOK_AWAS, umur: umur === null ? 0 : umur,"),
            'papan kapur memuat baris yang dibatalkan / hari lain': js.replace("const jual = {}; ambilPenjualan().forEach((p) => { if (p.tanggal !== hari) return;", "const jual = {}; ambilPenjualanSemua().forEach((p) => {"),
            'karantina menampilkan yang sudah diputuskan': js.replace(".filter((k) => (k.statusTindakan || 'belum_diputuskan') === 'belum_diputuskan')", ""),
            'angka kebijakan owner diabaikan (tetap 50 kg)': js.replace("const penuhKg = a && Number(a.penuhKg) > 0 ? Number(a.penuhKg) : WADAH_PENUH_KG;", "const penuhKg = WADAH_PENUH_KG;"),
            'aturan wadah yang mustahil diterima (isi ulang ≥ penuh)': js.replace("if (!(ulang >= 0) || ulang >= penuh) return { tolak:", "if (false) return { tolak:"),
            'aturan LAMA yang dipakai (bukan yang terbaru)': js.replace("const wdTerbaru = (daftar) => daftar.reduce((a, x) => (!a || wdSesudah(x, a) ? x : a), null);", "const wdTerbaru = (daftar) => daftar.reduce((a, x) => (!a || wdSesudah(a, x) ? x : a), null);"),
            'posisi wadah tidak mengikuti susunan owner': js.replace("const daftar = atur.daftar.map((m, i) => { const kn = karungUntukWadah(m);", "const daftar = atur.daftar.slice().sort().map((m, i) => { const kn = karungUntukWadah(m);"),
            'karung di belakang wadah tidak ikut digambar di layar Stok': js.replace("karung: karungBelakang(kn.merk, m), tumpukan: tumpukanGudang(kn.merk, siap) }, tinggiWadah(m, s)); });", "karung: { diketahui: false }, tumpukan: tumpukanGudang(kn.merk, siap) }, tinggiWadah(m, s)); });"),
            'tumpukan gudang lupa mengurangi isi wadah': js.replace("const kg = wdB2(namaKg - diBelakang - diWadah); const berat", "const kg = wdB2(namaKg - diBelakang); const berat"),
            'perkiraan yang belum lengkap disebut lengkap': js.replace("lengkap: (!w || w.diketahui) && pemegang.every((x) => kolam.some((k) => k.lokasi === x)), minus: kg < -0.0001 };", "lengkap: true, minus: kg < -0.0001 };"),
            'buka karung tidak menurunkan tumpukan di tab Gudang': js.replace("const kg = wdB2(namaKg - diBelakang - diWadah); const berat", "const kg = wdB2(namaKg - diWadah); const berat"),
            'kartu "Berasnya ada di mana?" hilang': js.replace("    { id: 'lokasi', q: 'Berasnya ada di mana?',", "    false && { id: 'lokasi', q: 'Berasnya ada di mana?',").replace("  ];\n  const aktif = kartu.some", "  ].filter(Boolean);\n  const aktif = kartu.some"),
            'petak wadah memakai karung senama, bukan karung yang dicatat di belakangnya': js.replace("karungNama: kn.merk, karungDicatat: kn.dariCatatan, karung: karungBelakang(kn.merk, m), tumpukan: tumpukanGudang(kn.merk, siap)", "karungNama: m, karungDicatat: kn.dariCatatan, karung: karungBelakang(m, m), tumpukan: tumpukanGudang(m, siap)"),
            'karung lama yang wadahnya sudah berganti karung hilang dari layar': js.replace("siap.kolam.forEach((k) => { if (k.wadah) return;", "siap.kolam.forEach((k) => { if (k.wadah || k.yatim) return;"),
            'karung yatim (wadahnya berganti karung) masih dihitung milik wadah itu': js.replace("wadah: pegang ? L : '', yatim: !!L && !pegang };", "wadah: L, yatim: false };"),
            'takar karung nama lain tidak pindah nama': js.replace("const namaKg = wdB2(buku.sisaKg - keluarKg + masukKg);", "const namaKg = wdB2(buku.sisaKg);"),
            'karung 25 kg dibuka sebagai 50 kg': js.replace("return !merkPunyaKarungBerat(merk, 50) && merkPunyaKarungBerat(merk, 25) ? 25 : KARUNG_BELAKANG_KG;", "return KARUNG_BELAKANG_KG;"),
            'yang belum ditandai ditulis 0 kg (bukan "?")': js.replace("(t.karungDiketahui ? skKG(t.diBelakangKg) : t.karungDiWadah ? '? (belum ditandai)' : '—')", "skKG(t.diBelakangKg)"),
            'rework karantina dianggap hitungan gudang di kartu cocokkan': js.replace("ambilPenyesuaianStok().forEach((p) => { if (!hitunganFisik(p)) return; const k = 'karung|'", "ambilPenyesuaianStok().forEach((p) => { const k = 'karung|'"),
            'papan kapur tidak menyebut di belakang wadah mana karung dibuka': js.replace("(w.wadah ? 'di belakang wadah ' + w.wadah : w.lepas ? 'sebagai bahan campuran' : 'di belakang wadah')", "'di belakang wadah'"),
            'bahan campuran yang bukan wadah tidak tampil': js.replace("daftar.forEach((w) => w.resep.forEach((x) => sebut(x.merk)));", ""),
            'papan kapur tidak mencatat takar isi ulang': js.replace("if (w.tipe === 'takar') out.push(", "if (false) out.push("),
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
    sys.exit(2 if g else 0)
