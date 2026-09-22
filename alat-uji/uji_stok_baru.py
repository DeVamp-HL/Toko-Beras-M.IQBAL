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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/stok-logika.js', 'baru/js/layar/stok-catat-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/stok-karantina-logika.js']
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
ok('9 takar campuran 6 : 3 (16,2 kg) → wadah 51,8 + 16,2 = 68 kg (di atas rata 60 → menggunung 0,8); karung Apex di belakang 50 − 10,8 = 39,2 kg; BUKU Apex naik 5,4 kg (3 takar Angsa pindah nama di buku, keputusan owner A), buku Angsa turun 5,4', wa.sisaKg === 68 && wa.gunung === 0.8 && wa.karung.sisaKg === 39.2 && Math.abs(daftarBarang().find(function (b) { return b.nama === 'IR64 Apex' && b.jenis === 'karung'; }).sisa - (bukuApex + 5.4)) < 0.011, JSON.stringify([wa.sisaKg, wa.gunung, wa.karung]));
ok('tumpukan gudang Apex = buku (sudah memuat +5,4 pindahan) − 39,2 (karung terbuka) − 68 (wadah); layar tidak menambah pindah nama lagi (0); lengkap karena keduanya sudah ditandai; tumpukan ANGSA = bukunya, yang sudah turun 5,4 dari sebelum takar', Math.abs(wa.tumpukan.kg - (bukuApex + 5.4 - 39.2 - 68)) < 0.011 && wa.tumpukan.pindahMasukKg === 0 && Math.abs(W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).tumpukan.kg - (brg('Angsa').sisa - 5.4)) < 0.011 && wa.karungNama === 'IR64 Apex' && wa.karungDicatat === true && wa.tumpukan.lengkap === true && wa.tumpukan.karung === Math.max(0, Math.floor((wa.tumpukan.kg + 0.0001) / 50)), JSON.stringify(wa.tumpukan));
ok('karung Angsa yang ikut dicampur belum pernah ditandai → TIDAK diketahui, dan tumpukan Angsa disebut "perkiraan belum lengkap"', W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).karung.diketahui === false && W2.daftar.find(function (w) { return w.nama === 'Angsa'; }).tumpukan.lengkap === false);
var K2 = susunKapur(KINI);
ok('papan kapur: "diisi ulang 9 takar dari karung IR64 Apex 6 + Angsa 3" +16,2 kg · "Karung IR64 Apex diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex" gudang −50 kg', K2.baris.some(function (x) { return x.jenis === 'wadah' && /Wadah IR64 Apex diisi ulang 9 takar dari karung IR64 Apex 6 \+ Angsa 3/.test(x.isi) && x.n === '+16,2 kg'; }) && K2.baris.some(function (x) { return /Karung IR64 Apex diambil dari tumpukan gudang, dibuka di belakang wadah IR64 Apex/.test(x.isi) && x.n === 'gudang −50 kg'; }) && K2.baris.some(function (x) { return x.jenis === 'wadah' && /Pindah nama di buku \(takar wadah\): Angsa 5,4 kg → IR64 Apex/.test(x.isi) && x.n === '↔ 5,4 kg'; }), JSON.stringify(K2.baris.filter(function (x) { return x.jenis === 'wadah'; })));
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

// ==================== BARANG MASUK (ST1) — bentuk dokumen simpanKedatangan index.html ====================
var WM = { tanggal: '2026-09-19', jam: '15:00', idUnik: WW.idUnik };
ok('masuk: aturan bawaan = 60 karung · tempo 21 hari · selisih wajar 3 % · stok bertambah > 250.000 ditanya (angka sistem berjalan)', aturCatat().minKarung === 60 && aturCatat().tempoHari === 21 && aturCatat().batasSelisih === 3 && aturCatat().ambangSusutPositif === 250000 && aturCatat().dariOwner === false);
ok('masuk: calon pemasok dari kedatangan (terbaru dulu), calon nama beras dari buku', calonPemasok().join() === 'PEMASOK CONTOH' && calonMerkMasuk().indexOf('Angsa') === 0 && calonMerkMasuk().indexOf('Pandan Wangi') >= 0 && hargaSebelumnya('Angsa') === 13500, JSON.stringify([calonPemasok(), calonMerkMasuk()]));
var dm = drafMasukKosong(WM); dm.pemasok = 'PEMASOK CONTOH'; dm.caraBayar = 'utang'; dm.bongkar = '100.000';
dm.baris = [{ merk: 'Angsa', jumlahKarung: '40', beratKarung: 50, hargaPerKg: '13.200' }, { merk: 'IR64 Apex', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '14.100' }, barisMasukKosong()];
var hm = hitungMasuk(dm);
ok('masuk: 40×50 @13.200 + 20×50 @14.100 + bongkar 100.000 → 60 karung, 3.000 kg, beras 40.500.000; HPP Angsa 13.233,33 & Apex 14.133,33 (bongkar dibagi menurut kg — hitungHppMerkDalamBatch); baris kosong diabaikan; harga sebelumnya disebut', hm.karung === 60 && hm.kg === 3000 && hm.nilaiBeras === 40500000 && hm.total === 40600000 && Math.abs(hm.sah[0].hppPerKg - 13233.3333) < 0.01 && Math.abs(hm.sah[1].hppPerKg - 14133.3333) < 0.01 && hm.sah[0].alokasiBongkar === 66667 && hm.baris.length === 3 && !hm.bermasalah.length && hm.sah[0].hargaLalu === 13500, JSON.stringify(hm.sah));
ok('masuk: pemasok kosong DITOLAK; baris terisi tanpa harga DITOLAK dan menyebut barisnya; nama dua kali DITOLAK', /pemasok/.test(susunSimpanMasuk(Object.assign({}, dm, { pemasok: '' }), WM).tolak || '') && /Baris 2 \(IR64 Apex\): harga beli/.test(susunSimpanMasuk(Object.assign({}, dm, { baris: [dm.baris[0], { merk: 'IR64 Apex', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '' }] }), WM).tolak || '') && /dua kali/.test(susunSimpanMasuk(Object.assign({}, dm, { baris: [dm.baris[0], dm.baris[0]] }), WM).tolak || ''), JSON.stringify(susunSimpanMasuk(Object.assign({}, dm, { baris: [dm.baris[0], { merk: 'IR64 Apex', jumlahKarung: '20', beratKarung: 50, hargaPerKg: '' }] }), WM)));
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

// ==================== COCOKKAN / HITUNG GUDANG (ST3) — bentuk dokumen simpanPenyesuaianStok / Kemasan / OpnameBahan ====================
var WC = { tanggal: '2026-09-19', jam: '16:00', idUnik: WW.idUnik };
var bc = barangCocok('beras'); var bA = bc.find(function (b) { return b.nama === 'Angsa'; });
ok('cocok: daftar beras dari buku dengan sistem kg & modal; nama wadah menyebut rincian tumpukan + karung terbuka + wadah', bc.length >= 3 && bA && Math.abs(bA.sistem - hitungStokKarungPerMerk()['Angsa'].sisaKg) < 0.011 && bA.modal > 0 && bA.satuan === 'kg' && (bc.find(function (b) { return b.nama === 'IR64 Apex'; }).rincian || '').indexOf('menurut layar') === 0, JSON.stringify(bc.map(function (b) { return b.nama + ':' + b.sistem; })));
var C0 = susunCocok('beras', {}, {}, {});
ok('cocok: belum ada yang dihitung → simpan ditolak dengan kalimatnya', /Belum ada yang dihitung/.test(C0.tolak) && C0.dihitung === 0 && C0.semua === bc.length);
var H = {}; H[bA.kunci] = String(bA.sistem - 8); var C1 = susunCocok('beras', H, {}, {});
var b1 = C1.baris.find(function (b) { return b.nama === 'Angsa'; });
ok('cocok: Angsa dihitung 8 kg kurang (ketikan "76.6" dari papan tombol HP dibaca 76,6 — bukan 766); selisih > 3 % butuh alasan → simpan ditolak menyebut namanya', b1.ada && b1.selisih === -8 && b1.rp === Math.round(-8 * bA.modal) && b1.besar === true && b1.perluAlasan === true && C1.susutRp === b1.rp && /Angsa: selisihnya lebih dari 3 %/.test(C1.tolak), JSON.stringify([b1, C1.tolak]));
var AL = {}; AL[bA.kunci] = 'tumpah waktu bongkar'; var C2 = susunCocok('beras', H, AL, {});
ok('cocok: dengan alasan, sisa penolakan = yang belum dihitung (ketuk sekali lagi = simpan sebagian)', C2.perluYakin === 'sebagian' && /belum dihitung/.test(C2.tolak) && !susunCocok('beras', H, AL, { sebagian: true }).tolak);
var SC = susunSimpanCocok('beras', H, AL, WC, { sebagian: true }); if (!SC.dokumen) { gagal.push('cocok: simpan DITOLAK: ' + SC.tolak + ' | ' + JSON.stringify(susunCocok('beras', H, AL, { sebagian: true }))); SC.dokumen = [{ koleksi: '?', data: {} }]; } var dokC = SC.dokumen[0].data;
ok('cocok: SATU dokumen penyesuaianStok {tanggal, jam, merk, kgSistem, kgFisik, selisihKg −8, alasan, nilaiRp (dikunci), hppPerKgSaatOpname} — kolom persis sistem berjalan; kabar menyebut laba turun', SC.dokumen.length === 1 && SC.dokumen[0].koleksi === 'penyesuaianStok' && Object.keys(dokC).sort().join() === 'alasan,hppPerKgSaatOpname,id,jam,kgFisik,kgSistem,merk,nilaiRp,selisihKg,tanggal' && dokC.merk === 'Angsa' && dokC.selisihKg === -8 && dokC.kgFisik === bA.sistem - 8 && dokC.nilaiRp === b1.rp && dokC.hppPerKgSaatOpname === Math.round(bA.modal) && dokC.alasan === 'tumpah waktu bongkar' && /Laba bulan ini turun/.test(SC.patch.kabar), JSON.stringify(SC));
terapkanKeCache(SC.dokumen);
ok('cocok: sesudah dicatat, buku Angsa = hasil hitungan (mesin beku membaca selisihKg), modal per kg TIDAK berubah; kartu "belum dicocokkan" Angsa = 0 hari; riwayat memuatnya', Math.abs(hitungStokKarungPerMerk()['Angsa'].sisaKg - (bA.sistem - 8)) < 0.011 && Math.abs(hitungStokKarungPerMerk()['Angsa'].hppTerakhirPerKg - bA.modal) < 0.001 && susunGudang('cocok', KINI).jawab.baris.find(function (x) { return x.nama === 'Angsa'; }).n === '0 hari' && riwayatCocok(3)[0].baris[0].nama === 'Angsa' && riwayatCocok(3)[0].rp === b1.rp, JSON.stringify(riwayatCocok(3)));
var H2 = {}; H2[bA.kunci] = String(bA.sistem - 8 + 1); var C3 = susunSimpanCocok('beras', H2, {}, { tanggal: '2026-09-19', jam: '16:05', idUnik: WW.idUnik }, { sebagian: true });
ok('cocok: hitungan KEDUA untuk Angsa 5 menit kemudian DITANYA (penjaga opname ganda 26 Agu), ketukan kedua boleh', C3.perluYakin === 'ganda' && /baru saja dicocokkan/.test(C3.tolak) && !susunSimpanCocok('beras', H2, {}, { tanggal: '2026-09-19', jam: '16:05', idUnik: WW.idUnik }, { sebagian: true, ganda: true }).tolak);
var H3 = {}; H3[bA.kunci] = String(bA.sistem * 3); var C4 = susunCocok('beras', H3, (function () { var o = {}; o[bA.kunci] = 'benar'; return o; })(), {});
ok('cocok: dihitung lebih dari dua kali tercatat = ANEH, ditanya dulu; stok bertambah lebih dari ambang rupiah ditanya juga (beras tidak tumbuh sendiri)', C4.perluYakin === 'aneh' && /Angka aneh/.test(C4.tolak) && susunCocok('beras', H3, (function () { var o = {}; o[bA.kunci] = 'benar'; return o; })(), { aneh: true }).perluYakin === 'susutPositif');
var ck = barangCocok('kemasan'); var kK = ck.find(function (b) { return /Kembang 5 kg/.test(b.nama); }); var HK2 = {}; HK2[kK.kunci] = String(kK.sistem + 1);
var SK = susunSimpanCocok('kemasan', HK2, {}, WC, { sebagian: true }); if (!SK.dokumen) SK.dokumen = [{ koleksi: '?', data: {} }];
ok('cocok: kemasan jadi per unit → dokumen penyesuaianKemasan {namaProduk, ukuranKemasan (angka), unitSistem, unitFisik, selisihUnit +1, alasan bawaan, nilaiRp = modal per unit, hppPerUnitSaatOpname}; sesudahnya sisa unit = hitungan', kK.satuan === 'unit' && SK.dokumen.length === 1 && SK.dokumen[0].koleksi === 'penyesuaianKemasan' && SK.dokumen[0].data.namaProduk === 'Kembang' && SK.dokumen[0].data.ukuranKemasan === 5 && SK.dokumen[0].data.selisihUnit === 1 && SK.dokumen[0].data.nilaiRp === Math.round(kK.modal) && SK.dokumen[0].data.alasan === 'Cocokkan stok' && (function () { terapkanKeCache(SK.dokumen); return hitungStokKemasan()[kunciKemasan('Kembang', 5)].sisaUnit === kK.sistem + 1; })(), JSON.stringify(SK.dokumen));
terapkanKeCache([{ koleksi: 'stokBahanKemasan', data: { id: 'bk1', tanggal: '2026-09-01', jenis: '5kg_kembangbmw', tipe: 'beli', jumlah: 200, hargaTotal: 225000 } }]);
var ckt = barangCocok('kantong'); var kT = ckt.find(function (b) { return b.jenis === '5kg_kembangbmw'; }); var HT = {}; HT[kT.kunci] = '190';
var ALT = {}; ALT[kT.kunci] = 'robek'; var ST = susunSimpanCocok('kantong', HT, ALT, WC, { sebagian: true, susutPositif: true }); if (!ST.dokumen) ST.dokumen = [{ koleksi: '?', data: {} }];
ok('cocok: kantong per lembar → dokumen stokBahanKemasan {tipe opname, jenis, jumlah −10, hargaTotal 0, pcsSistem, pcsFisik, catatan, nilaiRp = −10 × 1.125, hargaPerPcsSaatOpname}; sesudahnya sisa = 190, harga per lembar tetap', kT && kT.sistem === 200 && kT.modal === 1125 && ST.dokumen.length === 1 && ST.dokumen[0].koleksi === 'stokBahanKemasan' && ST.dokumen[0].data.tipe === 'opname' && ST.dokumen[0].data.jumlah === -10 && ST.dokumen[0].data.hargaTotal === 0 && ST.dokumen[0].data.nilaiRp === -11250 && ST.dokumen[0].data.pcsFisik === 190 && (function () { terapkanKeCache(ST.dokumen); var k = hitungStokBahanKemasan()['5kg_kembangbmw']; return k.sisaPcs === 190 && k.hppPerPcs === 1125; })(), JSON.stringify([kT, ST.dokumen]));
ok('cocok: rework karantina (dariRework, kgFisik null) tidak masuk riwayat hitungan fisik dan tidak mengunci penjaga ganda', (function () { terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 7002, tanggal: '2026-09-19', jam: '16:01', merk: 'IR64 Apex', kgSistem: null, kgFisik: null, selisihKg: 41.5, alasan: 'Rework', dariRework: true } }]);
  var bX = barangCocok('beras').find(function (b) { return b.nama === 'IR64 Apex'; }); var Hx = {}; Hx[bX.kunci] = String(bX.sistem - 1); var r = susunSimpanCocok('beras', Hx, {}, { tanggal: '2026-09-19', jam: '16:03', idUnik: WW.idUnik }, { sebagian: true });
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
var kenalB = {}; (CAD.batchMasuk || []).forEach(function (b) { Object.keys(b).forEach(function (k) { kenalB[k] = 1; }); (b.merkList || []).forEach(function (m) { Object.keys(m).forEach(function (k) { kenalB['merkList.' + k] = 1; }); }); }); kenalB.jam = 1; kenalB.alasanKoreksi = 1; kenalB.riwayat = 1;
var kenalP = {}; (CAD.penyesuaianStok || []).forEach(function (b) { Object.keys(b).forEach(function (k) { kenalP[k] = 1; }); });
var WX = { tanggal: '2026-09-22', jam: '10:00', idUnik: function () { return Math.random(); } }; var asingC = [];
var dX = drafMasukKosong(WX); dX.pemasok = calonPemasok()[0] || 'X'; dX.baris = [{ merk: calonMerkMasuk()[0], jumlahKarung: '70', beratKarung: 50, hargaPerKg: '13.000' }]; var SX = susunSimpanMasuk(dX, WX, true);
if (SX.dokumen) { Object.keys(SX.dokumen[0].data).forEach(function (k) { if (!kenalB[k]) asingC.push('batchMasuk.' + k); }); Object.keys(SX.dokumen[0].data.merkList[0]).forEach(function (k) { if (!kenalB['merkList.' + k]) asingC.push('batchMasuk.merkList.' + k); }); } else asingC.push('masuk ditolak: ' + SX.tolak);
var bY = barangCocok('beras').filter(function (b) { return b.sistem > 0; })[0]; if (bY) { var HY = {}; HY[bY.kunci] = String(bY.sistem - 1); var SY = susunSimpanCocok('beras', HY, {}, WX, { sebagian: true }); if (SY.dokumen) Object.keys(SY.dokumen[0].data).forEach(function (k) { if (!kenalP[k]) asingC.push('penyesuaianStok.' + k); }); else asingC.push('cocok ditolak: ' + SY.tolak); }
// adukan & karantina: kolom dokumen produksi / pemakaian kantong / rework wajib dikenal cadangan (kolom tambahan sistem baru: jam)
var kenalPr = {}; (CAD.produksiKemasan || []).forEach(function (p) { Object.keys(p).forEach(function (k) { kenalPr[k] = 1; }); }); kenalPr.jam = 1; kenalPr.catatan = 1;
var kenalKt = {}; (CAD.stokBahanKemasan || []).forEach(function (b) { Object.keys(b).forEach(function (k) { kenalKt[k] = 1; }); });
var cb = calonBahan()[0]; var cn = calonNamaHasil()[0]; var ck5 = kantongUntuk(5)[0]; var banyakAdukan = daftarAdukan(1e9).length; var rincianOk = true;
if (cb && cn && ck5) { var dZ = drafAdukanKosong(WX); dZ.bahan = [{ merk: cb.merk, kg: '50' }]; dZ.hasil = [{ nama: cn, ukuran: '5', unit: '10', kantongJenis: ck5.jenis, kantongJumlah: '10' }]; dZ.upah = '10.000';
  var SZ = susunSimpanAdukan(dZ, WX, { bahan: true, kantong: true, susut: true, kantongKosong: true, kemasan: true });
  if (SZ.dokumen) { Object.keys(SZ.dokumen[0].data).forEach(function (k) { if (!kenalPr[k]) asingC.push('produksiKemasan.' + k); }); var kt = SZ.dokumen.find(function (d) { return d.koleksi === 'stokBahanKemasan'; }); if (kt) Object.keys(kt.data).forEach(function (k) { if (!kenalKt[k]) asingC.push('stokBahanKemasan.' + k); });
    if (Math.abs(SZ.dokumen[0].data.hppPerUnit * 10 - SZ.hitung.total) > 1e-6) asingC.push('adukan: Σ modal × unit ≠ total biaya'); } else asingC.push('adukan ditolak: ' + SZ.tolak); }
daftarAdukan(1e9).slice(0, 40).forEach(function (a) { var r = rincianAdukan(a.batch); if (!r || Math.abs(r.biaya.total - a.total) > 1) rincianOk = false; });
if (!rincianOk) asingC.push('adukan: rincian tidak sama dengan buku');
print(JSON.stringify({ kunciAsingCatat: asingC, adukan: banyakAdukan, karantinaAntre: daftarKarantina(WX).antre.length, nilaiLayar: Math.round(G.jawab.total), nilaiPositif: Math.round(positif), neraca: N.nilaiSack + N.nilaiBags, minus: N.adaStokMinus, barang: G.banyakBarang, beli: susunGudang('beli', KINI).jawab.baris.length, mandek: susunGudang('mandek', KINI).jawab.baris.length, cocok: susunGudang('cocok', KINI).jawab.baris.length, kapur: susunKapur(KINI).banyak, wadah: susunWadah(keadaanAwal()).daftar.length }));
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
            'pindah buku dari takar ditulis di papan kapur sebagai adukan biasa': js.replace("    if (p.dariTakar) out.push({ k: 'p' + p.id,", "    if (false) out.push({ k: 'p' + p.id,"),
            'karung 25 kg dibuka sebagai 50 kg': js.replace("return !merkPunyaKarungBerat(merk, 50) && merkPunyaKarungBerat(merk, 25) ? 25 : KARUNG_BELAKANG_KG;", "return KARUNG_BELAKANG_KG;"),
            'yang belum ditandai ditulis 0 kg (bukan "?")': js.replace("(t.karungDiketahui ? skKG(t.diBelakangKg) : t.karungDiWadah ? '? (belum ditandai)' : '—')", "skKG(t.diBelakangKg)"),
            'rework karantina dianggap hitungan gudang di kartu cocokkan': js.replace("ambilPenyesuaianStok().forEach((p) => { if (!hitunganFisik(p)) return; const k = 'karung|'", "ambilPenyesuaianStok().forEach((p) => { const k = 'karung|'"),
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
            'selisih cocokkan tanpa rupiah (nilaiRp 0)': js.replace("const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = ada ? Math.round(selisih * b.modal) : 0;", "const selisih = ada ? ckB2(dihitung - b.sistem) : 0; const rp = 0;"),
            'selisih besar tidak minta alasan': js.replace("perluAlasan: besar && !String(A[b.kunci] || '').trim(),", "perluAlasan: false,"),
            'opname ganda dalam jendela menit tidak ditanya': js.replace("if (ganda.length && !(yakin || {}).ganda) return", "if (false) return"),
            'angka aneh (lebih dari dua kali tercatat) tidak ditanya': js.replace("else if (anehDaftar.length && !Y.aneh) {", "else if (false) {"),
            'stok bertambah tanpa pembelian di atas ambang tidak ditanya': js.replace("else if (lebihRp > atur.ambangSusutPositif && !Y.susutPositif) {", "else if (false) {"),
            'kolom dokumen cocokkan beda dari sistem berjalan (kgFisik hilang)': js.replace("merk: b.nama, kgSistem: b.sistem, kgFisik: b.dihitung, selisihKg: b.selisih,", "merk: b.nama, kgSistem: b.sistem, selisihKg: b.selisih,"),
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
            print('ASAP DATA TOKO: kolom dokumen catat (barang masuk, cocokkan, adukan, kantong) vs cadangan: %s · %d adukan di buku · %d menunggu di karantina' % (', '.join(h['kunciAsingCatat']) or 'semua dikenal', h['adukan'], h['karantinaAntre']))
            if h['kunciAsingCatat']: g.append('asap: dokumen catat punya kolom yang tidak dikenal cadangan')
    sys.exit(2 if g else 0)
