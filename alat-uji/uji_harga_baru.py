#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_harga_baru.py — uji logika layar HARGA & PEMASOK sistem baru (harga-logika.js H1 · bon-pemasok-logika.js H2 · belanja-logika.js H3) di jsc.
KOTAK PASIR (ANGKA CONTOH, bukan angka toko), jam dikunci 19 Sep 2026 10:00 WIB (laju 14 hari & laku 30 hari membaca Date.now).
Kalau ada backup-batch-*.json lokal (asap): tiap dokumen katalog = satu baris harga dengan angka yang sama; total bon = mesin beku; kolom dokumen dikenal cadangan.

    python3 alat-uji/uji_harga_baru.py            → N lulus · 0 gagal
    python3 alat-uji/uji_harga_baru.py --kontrol  → logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/belanja-logika.js']
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def jual(id, tgl, merk, kg, jenis='karung', **k):
    d = {'id': id, 'tanggal': tgl, 'jam': k.pop('jam', '09:00'), 'caraBayar': 'Tunai', 'jenis': jenis, 'merkSumber': merk, 'totalKg': kg, 'hargaTotal': int(kg * 14000), 'hppTotalSaatJual': int(kg * 13000)}
    if jenis == 'karung': d.update({'beratKarungAcuan': 50, 'jumlahKarung': kg / 50})
    d.update(k); return d


def batch(id, tgl, pemasok, cara, baris, bongkar=0):
    return {'id': id, 'tanggal': tgl, 'jam': '08:00', 'pemasok': pemasok, 'caraBayar': cara, 'biayaBongkar': bongkar,
            'merkList': [{'id': id + str(i), 'merk': m, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg // 50, 'totalKg': kg, 'hargaPerKg': h, 'subtotalHarga': kg * h} for i, (m, kg, h) in enumerate(baris)]}


# ---- ANGKA CONTOH. Angsa modal rata-rata (13.000.000 + 6.850.000 [13.600 + bongkar 100/kg] + 1.350.000) / 1.600 = 13.250, beli terbaru 13.500;
#      IR64 Apex (7.000.000 + 2.900.000) / 700 = 14.142,86, terbaru 14.500; Pandan Wangi 16.000. Target untung owner 600/kg.
KOTAK = {
  'batchMasuk': [batch('b1', '2026-08-20', 'RODA CONTOH', 'utang', [('Angsa', 1000, 13000), ('IR64 Apex', 500, 14000), ('Pandan Wangi', 200, 16000)]),
                 batch('b2', '2026-09-05', 'SEJATI CONTOH', 'tunai', [('Angsa', 500, 13600)], bongkar=50000),
                 batch('b3', '2026-09-12', 'RODA CONTOH', 'utang', [('Angsa', 100, 13500), ('IR64 Apex', 200, 14500)])],
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-08-25', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 40, 'hppPerUnit': 66000, 'merkSumber': 'Pandan Wangi', 'kgDipakai': 100}],
  'penjualan': [
    # Angsa: 700 kg karung dalam 14 hari → laju 50 kg/hari; sisa 1.600 − 700 − 24,6 = 875,4 kg → ±17 hari (tidak perlu dibeli); laku 30 hari: S 700 kg, L 30 liter
    jual('a1', '2026-09-10', 'Angsa', 350), jual('a2', '2026-09-17', 'Angsa', 350), jual('a3', '2026-08-25', 'Angsa', 24.6, jenis='literan', jumlahLiter=30),
    # IR64 Apex: 550 kg dalam 14 hari → laju 39,29/hari; sisa 700 − 550 = 150 → 3 hari → PERLU; saran ceil((550 − 150) / 50) = 8 karung
    jual('x1', '2026-09-08', 'IR64 Apex', 300), jual('x2', '2026-09-16', 'IR64 Apex', 250),
    # Pandan Wangi: tak ada penjualan → laju 0 (tidak ditebak); kemasan Kembang 5 kg terjual 5 unit → sisa 35, laku K5 = 5
    jual('k1', '2026-09-15', None, 25, jenis='kemasan', namaProduk='Kembang', ukuranKemasan=5, jumlahUnit=5),
    jual('h1', '2026-09-19', 'Angsa', 8.2, jenis='literan', jam='09:30', jumlahLiter=10) | {'dibatalkan': True},
  ],
  # katalog: Angsa per kg 13.800 disetel 1 Sep (harga beli saat itu 13.000 → kini 13.500 = NAIK; untung 550 < target 600 → DIMAKAN); Apex 14.100 disetel 14 Sep (< modal 14.142,86 → RUGI); Pandan Wangi tanpa harga per kg (LUBANG)
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 13800, 'diubahPada': '2026-09-01T03:00:00.000Z'}, {'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerKg': 14100, 'diubahPada': '2026-09-14T03:00:00.000Z'}],
  # literan: Angsa 12.500/liter (modal 13.250 × 0,82 = 10.865 → untung 1.994/kg AMAN); Pandan Wangi 13.000 (modal 16.000 × 0,82 = 13.120 → RUGI 146/kg); Apex tanpa harga literan
  'katalogHargaLiteran': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 12500, 'diubahPada': '2026-08-02T03:00:00.000Z'}, {'id': 'Pandan Wangi', 'merk': 'Pandan Wangi', 'hargaPerLiter': 13000, 'diubahPada': '2026-08-10T03:00:00.000Z'}],
  # kemasan: Kembang 5 kg 75.000 (modal adukan 66.000 → untung 1.800/kg); Angsa karung utuh 50 kg 700.000 (modal beras 662.500 → untung 750/kg)
  'katalogHargaKemasan': [{'id': 'kembang_5kg', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 75000, 'diubahPada': '2026-09-02T03:00:00.000Z'}, {'id': 'angsa50', 'merk': 'Angsa', 'ukuran': 50, 'hargaPerUnit': 700000, 'diubahPada': '2026-09-02T03:00:00.000Z'}],
  # bon: b1 RODA 23.200.000 dibayar 20.000.000 (SEBAGIAN → tetap di daftar, sisa 3.200.000); b3 RODA 4.250.000; bon lama SEJATI 5.000.000 tanpa tanggal
  'utangPemasokMutasi': [{'id': 501, 'tipe': 'bayar', 'pemasok': 'RODA CONTOH', 'nominal': 20000000, 'tanggal': '2026-09-10', 'jam': '16:00', 'bonId': 'b1', 'bonTanggal': '2026-08-20', 'catatan': ''},
                         {'id': 502, 'tipe': 'saldoAwal', 'pemasok': 'SEJATI CONTOH', 'nominal': 5000000, 'tanggal': '2026-08-25', 'jam': '23:02', 'bonTanggal': None, 'catatan': 'bon lama, dari ingatan'}],
  'pemasokCatatan': [{'id': 'roda contoh', 'nama': 'RODA CONTOH', 'kontak': '0812 3456 7890', 'catatan': 'antar tiap Jumat', 'tempo': 21}],
  'aturanToko': [{'id': 'harga', 'targetPerKg': 600}],
  'pengeluaranHarian': [], 'hargaPasar': [], 'hargaTerbit': [], 'pesananPemasok': [],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
var KINI = new Date(Date.now()); var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: (function () { var n = 9000; return function () { n += 1; return n; }; })() };
var stokK = hitungStokKarungPerMerk();
ok('kotak pasir: modal rata-rata Angsa 13.250 (bongkar ikut), beli terbaru 13.500; Apex 14.142,86; sisa Apex 150', Math.abs(stokK.Angsa.hppTerakhirPerKg - 13250) < 1e-6 && stokK.Angsa.hargaTerakhirPerKg === 13500 && Math.abs(stokK['IR64 Apex'].hppTerakhirPerKg - 9900000 / 700) < 1e-6 && stokK['IR64 Apex'].sisaKg === 150, J(stokK));

// ==================== H1 · KATALOG HARGA ====================
var A = aturHarga();
ok('atur: target 600/kg dari owner; pembulatan bawaan liter 500 · kemasan 1.000 · per kg 100; ongkos bongkar TERUKUR 100/kg (50.000 ÷ 500 kg) dan disebut terukur; QRIS 0,30 % di atas 500.000', A.targetPerKg === 600 && !A.targetDariRata && A.bulatLiter === 500 && A.bulatKemasan === 1000 && A.bulatKarung === 100 && A.bongkarKg === 100 && A.bongkarTerukur && A.mdrPersen === 30 && A.mdrBatas === 500000 && hgPct(30) === '0,30 %', J(A));
pasok('aturanToko', []);
ok('target bawaan = rata-rata untung katalog KARUNG yang berlaku (550 + (−42,86)) / 2 = 253,6 → 250, ditandai dari rata-rata; bongkar 0 bila tak ada upah bongkar', aturHarga().targetPerKg === 250 && aturHarga().targetDariRata === true && (function () { var b = ambilSemuaBatch(); pasok('batchMasuk', b.map(function (x) { return Object.assign({}, x, { biayaBongkar: 0 }); })); var r = aturHarga().bongkarKg; pasok('batchMasuk', b); return r === 0; })(), J(aturHarga()));
pasok('aturanToko', KOTAK.aturanToko);
var AT = susunAturHarga({ targetPerKg: '700', langkahRp: '0' }, W); ok('atur: langkah nol DITOLAK (tidak boleh nol)', !!AT.tolak && /nol/.test(AT.tolak), J(AT));
AT = susunAturHarga({ targetPerKg: '700', mdrPersen: '70' }, W); ok('atur: dokumen aturanToko/harga memuat semua angka (yang kosong = nilai kini), target 700, QRIS 0,70 %', AT.dokumen[0].data.id === 'harga' && AT.dokumen[0].data.targetPerKg === 700 && AT.dokumen[0].data.mdrPersen === 70 && AT.dokumen[0].data.bulatLiter === 500 && AT.dokumen[0].data.bongkarKg === 100, J(AT));
var S = hgSemua(KINI); var br = function (k) { return cariBaris(S, k); };
ok('baris: merek × satuan yang ada — Angsa L/K50/S, IR64 Apex L/S, Pandan Wangi L/S, Kembang K5 (8 baris), urut merek lalu liter → kemasan → per kg', S.baris.length === 8 && S.baris.map(function (b) { return b.k; }).join() === 'Angsa|L,Angsa|K50,Angsa|S,IR64 Apex|L,IR64 Apex|S,Kembang|K5,Pandan Wangi|L,Pandan Wangi|S', J(S.baris.map(function (b) { return b.k; })));
ok('Angsa per kg 13.800: modal 13.250 → untung 550 < target 600, dan harga beli NAIK 500 sejak disetel 1 Sep (13.000 → 13.500) → DIMAKAN; vs beli terbaru untung 300', br('Angsa|S').status === 'dimakan' && Math.abs(br('Angsa|S').margin - 550) < 1e-6 && br('Angsa|S').naik && br('Angsa|S').naikRp === 500 && /naik Rp500\/kg sejak harga ini disetel 2026-09-01/.test(br('Angsa|S').naikTeks) && Math.abs(br('Angsa|S').marginTerbaru - 300) < 1e-6, J(br('Angsa|S')));
ok('IR64 Apex per kg 14.100 < modal 14.142,86 → RUGI 42,86/kg (bukan dimakan: harga beli saat disetel 14 Sep = 14.500, tidak naik)', br('IR64 Apex|S').status === 'rugi' && Math.abs(br('IR64 Apex|S').margin + 300000 / 7000) < 1e-6 && !br('IR64 Apex|S').naik, J(br('IR64 Apex|S')));
ok('Pandan Wangi per kg: LUBANG (belum ada harga), usul = modal 16.000 + 600 dibulatkan ke 100 = 16.600; Apex literan lubang, usul (14.142,86 + 600) × 0,82 = 12.089 → 12.500', br('Pandan Wangi|S').status === 'lubang' && br('Pandan Wangi|S').usul === 16600 && br('IR64 Apex|L').status === 'lubang' && br('IR64 Apex|L').usul === 12500, J([br('Pandan Wangi|S'), br('IR64 Apex|L')]));
ok('literan Angsa 12.500/liter: per kg 15.243,9; modal 13.250 × 0,82; untung 1.993,9/kg → AMAN; Pandan Wangi literan 13.000 < 13.120 → RUGI 146,3/kg', br('Angsa|L').status === 'aman' && Math.abs(br('Angsa|L').perKg - 12500 / 0.82) < 1e-6 && Math.abs(br('Angsa|L').margin - (12500 - 13250 * 0.82) / 0.82) < 1e-6 && br('Pandan Wangi|L').status === 'rugi' && Math.abs(br('Pandan Wangi|L').margin - (13000 - 16000 * 0.82) / 0.82) < 1e-6, J([br('Angsa|L'), br('Pandan Wangi|L')]));
ok('kemasan Kembang 5 kg 75.000: modal dari ADUKAN 66.000 (beras + kantong + upah) → untung 1.800/kg AMAN; Angsa 50 kg 700.000: modal beras 13.250 × 50 = 662.500 → untung 750/kg', br('Kembang|K5').modalDari === 'adukan' && br('Kembang|K5').modalUnit === 66000 && Math.abs(br('Kembang|K5').margin - 1800) < 1e-6 && br('Angsa|K50').modalDari === 'beras' && Math.abs(br('Angsa|K50').margin - 750) < 1e-6 && br('Angsa|K50').st.nama === 'Karung 50 kg', J([br('Kembang|K5'), br('Angsa|K50')]));
ok('laku 30 hari dalam SATUAN barisnya: Angsa S 700 kg, Angsa L 30 liter (25 Agu ikut, yang dibatalkan tidak), Apex S 550, Kembang K5 5 unit', br('Angsa|S').laku === 700 && br('Angsa|L').laku === 30 && br('IR64 Apex|S').laku === 550 && br('Kembang|K5').laku === 5, J(S.baris.map(function (b) { return b.k + ':' + b.laku; })));
ok('ringkas: 2 belum ada harga · 1 modal naik · 0 di bawah target · 2 rugi; 5 perlu diputuskan; belum ada draf', J(S.ringkas.map(function (r) { return r.a; })) === '[2,1,0,2]' && S.perlu.length === 5 && S.nDraf === 0, J(S.ringkas));
ok('nilaiHarga: rugi hanya bila modal > harga (tegas); harga = modal → NOL bukan rugi; tanpa modal → tanpaModal', nilaiHarga(14000, 14000, 1, 600, false).status === 'nol' && nilaiHarga(13999, 14000, 1, 600, false).status === 'rugi' && nilaiHarga(14001, 14000, 1, 600, true).status === 'dimakan' && nilaiHarga(14001, 14000, 1, 600, false).status === 'bawah' && nilaiHarga(15000, 0, 1, 600, false).status === 'tanpaModal' && nilaiHarga(0, 14000, 1, 600, false).status === 'lubang');
// ---- ubah satu harga → DRAF; harga pasar = catatan
var U = hitungUbah(S, 'Angsa|S', '13.800', 'jual'); ok('ubah: sama dengan harga berlaku DITOLAK dengan kalimat; modal disebut (13.250/kg · beli terbaru 13.500)', /Sama dengan harga yang sedang berlaku/.test(U.tolak) && /13\.250\/kg · beli terbaru Rp13\.500\/kg/.test(U.modalTeks), J(U));
U = hitungUbah(S, 'Angsa|S', '13.900', 'jual'); ok('ubah 13.900: arti "untung 650/kg", label SIMPAN SEBAGAI DRAF, usul dijelaskan (modal + 600, dibulatkan ke 100)', !U.tolak && /untung Rp650\/kg/.test(U.arti) && /DRAF/.test(U.label) && /modal \+ Rp600\/kg, dibulatkan ke atas ke Rp100/.test(U.usulTeks), J(U));
U = hitungUbah(S, 'IR64 Apex|S', '14.000', 'jual'); ok('ubah di bawah modal: BOLEH, ditandai awas "RUGI 142,86/kg — dijual di bawah modal"', !U.tolak && U.awas && /RUGI Rp143\/kg/.test(U.arti), J(U));
var R = susunUbah('Angsa|S', '13.900', 'jual', W); ok('susunUbah: dokumen aturanToko/hargaDraf {draf: {Angsa|S: 13900}} — kasir masih memakai 13.800 sampai diterbitkan', R.dokumen.length === 1 && R.dokumen[0].data.id === 'hargaDraf' && R.dokumen[0].data.draf['Angsa|S'] === 13900 && /kasir masih memakai Rp13\.800/.test(R.patch.kabar), J(R));
terapkanKeCache(R.dokumen); S = hgSemua(KINI);
ok('sesudah draf: Angsa per kg n = 13.900 (draf), lamaN 13.800, status aman (650 ≥ 600), nDraf 1, tidak lagi di "perlu"; ringkas modal naik 0', br('Angsa|S').adaDraf && br('Angsa|S').n === 13900 && br('Angsa|S').lamaN === 13800 && br('Angsa|S').status === 'aman' && S.nDraf === 1 && !S.perlu.some(function (b) { return b.k === 'Angsa|S'; }) && S.ringkas[1].a === 0, J(br('Angsa|S')));
terapkanKeCache(susunUbah('Angsa|S', '13.800', 'jual', W).dokumen); S = hgSemua(KINI);
ok('draf yang diketik = harga berlaku → drafnya DIBUANG (bukan draf 13.800)', S.nDraf === 0 && !br('Angsa|S').adaDraf, J(S.draf));
R = susunUbah('Angsa|K50', '705.000', 'pasar', W); ok('harga pasar: dokumen hargaPasar {id = kunci, harga 705000}; arti "pasar Rp850/kg di atas modal lu"', R.dokumen[0].koleksi === 'hargaPasar' && R.dokumen[0].data.id === 'Angsa|K50' && R.dokumen[0].data.harga === 705000 && /kasir tidak terpengaruh/.test(R.patch.kabar), J(R));
terapkanKeCache(R.dokumen); S = hgSemua(KINI);
ok('pasar tercatat, TIDAK jadi draf; hitungUbah mode pasar dengan angka sama ditolak', br('Angsa|K50').pasar.harga === 705000 && !br('Angsa|K50').adaDraf && S.nDraf === 0 && /Sama dengan catatan pasar/.test(hitungUbah(S, 'Angsa|K50', '705000', 'pasar').tolak));
// ---- sengaja dibiarkan (V6): diingat, gugur sendiri bila modal/harga berubah
R = susunSengaja('Angsa|S', W); ok('sengaja: Angsa per kg (dimakan) dibiarkan → aturanToko/hargaSengaja {peta: {Angsa|S: {modal 13250, n 13800}}}', R.dokumen[0].data.id === 'hargaSengaja' && R.dokumen[0].data.peta['Angsa|S'].modal === 13250 && R.dokumen[0].data.peta['Angsa|S'].n === 13800 && /berhenti menagihnya/.test(R.patch.kabar), J(R));
terapkanKeCache(R.dokumen); S = hgSemua(KINI);
ok('sesudah sengaja: baris ditandai sengaja, keluar dari perlu (4) & ringkas modal naik 0; ketuk lagi = tagih lagi', br('Angsa|S').sengaja && S.perlu.length === 4 && S.ringkas[1].a === 0 && /ditagih lagi/.test(susunSengaja('Angsa|S', W).patch.kabar), J(br('Angsa|S')));
ok('sengaja GUGUR sendiri kalau harganya berubah (katalog 13.820: masih dimakan, tapi n beda dari yang diingat)', (function () { var k = ambilHargaKarung(); pasok('katalogHargaKarung', k.map(function (x) { return x.merk === 'Angsa' ? Object.assign({}, x, { hargaPerKg: 13820 }) : x; })); var r = cariBaris(hgSemua(KINI), 'Angsa|S').sengaja; pasok('katalogHargaKarung', k); return r === false; })());
ok('sengaja: harga yang tidak sedang ditagih ditolak; yang sedang draf ditolak', /tidak sedang ditagih/.test(susunSengaja('Angsa|L', W).tolak) && (function () { terapkanKeCache(susunUbah('IR64 Apex|S', '14.800', 'jual', W).dokumen); var r = susunSengaja('IR64 Apex|S', W).tolak; terapkanKeCache(susunBuangDraf('IR64 Apex|S', W).dokumen); return /draf/.test(r); })());
// ---- usul semua → draf (Apex S 14.800, Pandan S 16.600, Pandan L 14.000, Apex L 12.500); Angsa S sengaja tidak ikut
R = susunUsulSemua(W); terapkanKeCache(R.dokumen); S = hgSemua(KINI);
ok('usul semua: 4 draf (Apex S 14.800 · Pandan S 16.600 · Pandan L 14.000 · Apex L 12.500), Angsa S (sengaja) tidak ikut; semuanya masih DRAF', S.nDraf === 4 && br('IR64 Apex|S').n === 14800 && br('Pandan Wangi|S').n === 16600 && br('Pandan Wangi|L').n === 14000 && br('IR64 Apex|L').n === 12500 && !br('Angsa|S').adaDraf && br('IR64 Apex|S').status === 'aman' && br('IR64 Apex|S').lamaN === 14100, J(S.draf));
ok('pratinjau terbit: 4 baris lama → baru, tidak ada rugi; Pandan S lama 0 ("belum ada")', pratinjauTerbit(S).n === 4 && !pratinjauTerbit(S).adaRugi && pratinjauTerbit(S).daftar.find(function (d) { return d.k === 'Pandan Wangi|S'; }).lama === 0, J(pratinjauTerbit(S)));
// ---- kalimat: berangkat dari harga SEKARANG, dibulatkan searah
var KL = hitungKalimat(S, { arah: 'turun', merek: 'Angsa', satuan: 'L', rp: 50 });
ok('kalimat "Turunkan harga literan Angsa Rp50 per kg": 12.500 − 41 = 12.459 → dibulatkan KE BAWAH ke 500 = 12.000 (turun 500/liter = Rp610/kg sesudah dibulatkan — disebut)', /^Turunkan harga literan Angsa Rp50 per kg\.$/.test(KL.kalimat) && KL.hasil.length === 1 && KL.hasil[0].baru === 12000 && /= Rp610\/kg sesudah dibulatkan/.test(KL.hasil[0].ket), J(KL));
KL = hitungKalimat(S, { arah: 'naik', merek: 'semua', satuan: 'S', rp: 100 });
ok('kalimat naikkan semua per kg 100: Angsa 13.800 → 13.900, Apex (draf 14.800) → 14.900, Pandan (draf 16.600) → 16.700; lubang tidak ada lagi di per kg', KL.hasil.length === 3 && KL.hasil.map(function (x) { return x.baru; }).join() === '13900,14900,16700', J(KL));
KL = hitungKalimat(S, { arah: 'turun', merek: 'Kembang', satuan: 'semua', rp: 200 });
ok('kalimat turunkan Kembang 200/kg: 75.000 − 1.000 = 74.000 (kelipatan 1.000 pas); yang jadi rugi ditandai; rp 0 → kosong', KL.hasil[0].baru === 74000 && !KL.hasil[0].rugi && hitungKalimat(S, { arah: 'turun', merek: 'Kembang', satuan: 'semua', rp: 0 }).hasil.length === 0, J(KL));
R = susunKalimatDraf({ arah: 'naik', merek: 'Angsa', satuan: 'S', rp: 100 }, W); terapkanKeCache(R.dokumen); S = hgSemua(KINI);
ok('kalimat → draf: Angsa per kg draf 13.900 (5 draf), sengajanya gugur karena kini draf', S.nDraf === 5 && br('Angsa|S').n === 13900 && !br('Angsa|S').sengaja, J(S.draf));
terapkanKeCache(susunBuangDraf('Angsa|S', W).dokumen); S = hgSemua(KINI);
// ---- dampak: rupiah per bulan
var D = susunDampak(S);
ok('dampak: yang perlu & belum draf = Angsa S (sengaja → tidak dihitung) … tertinggal 0 karena Apex/Pandan sudah draf; draf Apex S +385.000/bulan ((14.800 − 14.100) × 550) + Pandan L (laku 0) 0 + baru 2', D.totalTinggal === 0 && D.totalDraf === 385000 && D.kelompok.some(function (g) { return g.judul === 'Sudah jadi draf' && g.isi.length === 4; }), J(D.kelompok.map(function (g) { return g.judul + ':' + g.isi.length; })));
terapkanKeCache(susunBuangDraf(null, W).dokumen); terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'hargaSengaja', peta: {} } }]); S = hgSemua(KINI); D = susunDampak(S);
ok('dampak tanpa draf/sengaja: tertinggal = Angsa S (13.900 − 13.800) × 700 = 70.000 + Apex S (14.800 − 14.100) × 550 = 385.000 = 455.000; Pandan L rugi tapi laku 0 → "tidak ada yang terjual"; Apex S di "paling terasa", Angsa S juga (≥ 50.000)', D.totalTinggal === 455000 && D.kelompok[0].judul === 'Paling terasa di kantong' && D.kelompok[0].isi.length === 2 && D.kelompok[0].isi[0].k === 'IR64 Apex|S' && D.kelompok.some(function (g) { return /tidak ada yang terjual/.test(g.judul) && g.isi[0].k === 'Pandan Wangi|L'; }) && /pembelinya TIDAK berkurang/.test(D.syarat), J(D.kelompok.map(function (g) { return g.judul + ':' + g.isi.map(function (x) { return x.k; }).join('/'); })));
R = susunPakaiUsul('IR64 Apex|S', W); ok('pakai usul satu baris → draf 14.800', R.dokumen[0].data.draf['IR64 Apex|S'] === 14800);
// ---- pasar
var PS = susunPasar(S); var ps = function (k) { return PS.baris.find(function (b) { return b.k === k; }); };
ok('pasar: Angsa 50 kg pasar 705.000 > harga 700.000 → "ruang" (Rp5.000 di bawah pasar); yang lain "kosong"; ringkas di atas pasar 0', ps('Angsa|K50').ps === 'ruang' && /Rp5\.000 di bawah pasar/.test(ps('Angsa|K50').teks) && ps('Angsa|S').ps === 'kosong' && PS.ringkas[0].a === 0 && PS.ringkas[3].a === 7, J(PS.ringkas));
terapkanKeCache(susunUbah('Angsa|K50', '690.000', 'pasar', W).dokumen); PS = susunPasar(hgSemua(KINI));
ok('pasar 690.000 < harga 700.000 → "DI ATAS pasar" (awas, menyala); pasar di bawah modal terdeteksi', ps('Angsa|K50').ps === 'atas' && ps('Angsa|K50').awas && PS.ringkas[0].a === 1 && (function () { terapkanKeCache(susunUbah('Angsa|K50', '600.000', 'pasar', W).dokumen); var r = susunPasar(hgSemua(KINI)).baris.find(function (b) { return b.k === 'Angsa|K50'; }); return r.ps === 'bawahModal' && /DI BAWAH modal lu Rp1\.250\/kg/.test(r.teks); })(), J(ps('Angsa|K50')));
terapkanKeCache([{ koleksi: 'hargaPasar', hapus: 'Angsa|K50' }]); ok('hapus catatan pasar: ditolak bila tidak ada', /Tidak ada catatan pasar/.test(susunHapusPasar('Angsa|K50', W).tolak));
// ---- belah
S = hgSemua(KINI); var BL = susunBelah(S, { merek: 'Angsa', satuan: 'S', bayar: 'tunai' });
ok('belah Angsa per kg 13.800 tunai: ke pemasok 13.250 + bongkar 100 (terukur) + QRIS 0 → tinggal 450 (3,3 %); menutup', BL.ada && BL.beras === 13250 && BL.bongkar === 100 && BL.mdr === 0 && BL.sisa === 450 && BL.beras + BL.wadah + BL.bongkar + BL.mdr + BL.sisa === BL.harga && BL.persen === '3,3 %', J(BL));
BL = susunBelah(S, { merek: 'Angsa', satuan: 'S', bayar: 'qris' }); ok('belah QRIS di bawah batas 500.000 (per kg 13.800): TIDAK dipotong, ket "bebas sampai Rp500.000"', BL.mdr === 0 && /bebas sampai Rp500\.000/.test(BL.rinci[3].ket) && BL.sisa === 450, J(BL.rinci));
BL = susunBelah(S, { merek: 'Angsa', satuan: 'K50', bayar: 'qris' });
ok('belah Angsa karung 50 kg 700.000 QRIS: > 500.000 → potongan 0,30 % = 2.100; beras 662.500; bongkar 5.000; tinggal 30.400 = Rp608/kg; skala karung 1', BL.mdr === 2100 && BL.beras === 662500 && BL.bongkar === 5000 && BL.sisa === 30400 && Math.abs(BL.perKg - 608) < 1e-6 && BL.skala === 1 && !BL.kaleng, J(BL));
BL = susunBelah(S, { merek: 'Kembang', satuan: 'K5', bayar: 'tunai' });
ok('belah Kembang 5 kg: modal adukan utuh (beras tak dikenal) = 66.000 satu komponen; bongkar 500; tinggal 8.500', BL.beras === 66000 && BL.wadah === 0 && /modal kemasan/.test(BL.rinci[0].nama) && BL.bongkar === 500 && BL.sisa === 8500, J(BL));
BL = susunBelah(S, { merek: 'IR64 Apex', satuan: 'S', bayar: 'tunai' }); ok('belah harga rugi: NOMBOK disebut (sisa negatif), awas', BL.sisa < 0 && BL.awas && /NOMBOK/.test(BL.sisaTeks), J(BL));
BL = susunBelah(S, { merek: 'Pandan Wangi', satuan: 'S', bayar: 'tunai' }); ok('belah baris lubang: tidak ada yang dibelah, usul disebut', !BL.ada && /belum punya harga/.test(BL.kosongTeks) && /Rp16\.600/.test(BL.kosongTeks), J(BL));
// ---- papan kapur & WA
var PP = susunPapan(S, 'owner'); var PB = susunPapan(S, 'pembeli');
ok('papan sisi owner: 4 merek; Pandan Wangi per kg = "isi" (lubang); Apex per kg awas; sisi pembeli: lubang = "—", tanpa kelas', PP.baris.length === 4 && PP.baris.find(function (m) { return m.merk === 'Pandan Wangi'; }).sel[1].harga === 'isi' && PP.baris.find(function (m) { return m.merk === 'IR64 Apex'; }).sel[1].kelas === 'awas' && PB.baris.find(function (m) { return m.merk === 'Pandan Wangi'; }).sel[1].harga === '—' && PB.baris.every(function (m) { return m.sel.every(function (c) { return c.kelas === ''; }); }), J(PP.baris));
terapkanKeCache(susunUbah('Pandan Wangi|S', '16.600', 'jual', W).dokumen); S = hgSemua(KINI); PP = susunPapan(S, 'owner'); PB = susunPapan(S, 'pembeli');
ok('draf tampil di sisi owner (16.600, kelas draf) tapi papan PEMBELI tetap "—"; teks WA cuma harga terbit & mengaku 1 draf belum ikut', PP.baris.find(function (m) { return m.merk === 'Pandan Wangi'; }).sel[1].harga === 16600 && PP.baris.find(function (m) { return m.merk === 'Pandan Wangi'; }).sel[1].kelas === 'draf' && PB.baris.find(function (m) { return m.merk === 'Pandan Wangi'; }).sel[1].harga === '—' && /1 draf lu belum ikut/.test(teksWaHarga(S, '19 Sep').arti) && teksWaHarga(S, '19 Sep').baris.some(function (t) { return /Pandan Wangi — liter 13\.000$/.test(t); }) && /wa\.me\/\?text=/.test(teksWaHarga(S, '19 Sep').tautan), J(teksWaHarga(S, '19 Sep')));
// ---- terbit: semua atau tidak sama sekali
terapkanKeCache(susunUbah('IR64 Apex|S', '14.000', 'jual', W).dokumen); S = hgSemua(KINI);
var T = susunTerbit(W, false); ok('terbit dengan draf RUGI (Apex 14.000 < modal): ketukan pertama DITOLAK menyebut namanya, minta ketuk lagi', !!T.tolak && /IR64 Apex · Karung per kg/.test(T.tolak) && T.perluYakin, J(T));
terapkanKeCache(susunUbah('IR64 Apex|S', '14.800', 'jual', W).dokumen); terapkanKeCache(susunUbah('Angsa|L', '13.000', 'jual', W).dokumen); S = hgSemua(KINI);
T = susunTerbit(W, false);
ok('terbit 3 draf: dokumen katalog per koleksi PERSIS bentuk sistem lama (karung {id, merk, hargaPerKg, diubahPada} + modalSaatSetel; literan hargaPerLiter) + hargaDraf kosong + hargaLabel 3 tugas + hargaTerbit; SATU daftar dokumen (satu writeBatch)', !T.tolak && T.dokumen.length === 6 && T.dokumen.filter(function (d) { return d.koleksi === 'katalogHargaKarung'; }).length === 2 && T.dokumen.find(function (d) { return d.koleksi === 'katalogHargaKarung' && d.data.merk === 'Pandan Wangi'; }).data.id === 'Pandan Wangi' && T.dokumen.find(function (d) { return d.koleksi === 'katalogHargaKarung' && d.data.merk === 'IR64 Apex'; }).data.hargaPerKg === 14800 && T.dokumen.find(function (d) { return d.koleksi === 'katalogHargaKarung' && d.data.merk === 'IR64 Apex'; }).data.modalSaatSetel === 14500
  && T.dokumen.find(function (d) { return d.koleksi === 'katalogHargaLiteran'; }).data.hargaPerLiter === 13000 && T.dokumen.find(function (d) { return d.data && d.data.id === 'hargaDraf'; }).data.draf && Object.keys(T.dokumen.find(function (d) { return d.data && d.data.id === 'hargaDraf'; }).data.draf).length === 0 && T.dokumen.find(function (d) { return d.data && d.data.id === 'hargaLabel'; }).data.daftar.length === 3 && T.dokumen.find(function (d) { return d.koleksi === 'hargaTerbit'; }).data.n === 3, J(T.dokumen));
terapkanKeCache(T.dokumen); S = hgSemua(KINI);
ok('sesudah terbit: katalog berlaku Apex 14.800 (aman), Pandan per kg 16.600 (lubang hilang), Angsa literan 13.000; nDraf 0; ringkas lubang tinggal 1 (Apex literan); riwayat terbit 3 baris (Pandan "baru")', br('IR64 Apex|S').lamaN === 14800 && br('IR64 Apex|S').status === 'aman' && br('Pandan Wangi|S').lamaN === 16600 && br('Angsa|L').lamaN === 13000 && S.nDraf === 0 && S.ringkas[0].a === 1 && riwayatTerbit(10).length === 3 && riwayatTerbit(10).some(function (r) { return /Pandan Wangi/.test(r.nama) && r.arah === 'baru'; }), J([br('IR64 Apex|S'), S.ringkas, riwayatTerbit(10)]));
ok('modalSaatSetel baru terbaca: Apex disetel saat beli terbaru 14.500 → belum naik', !br('IR64 Apex|S').naik);
var LB = susunLabelTugas(S); ok('label rak: 3 label masih harga lama (Apex tulis 14.800 · label 14.100; Pandan label kosong → tulis 16.600; Angsa literan 12.500 → 13.000)', LB.ada && LB.tugas.length === 3 && LB.tugas.find(function (t) { return t.k === 'IR64 Apex|S'; }).lama === 14100 && LB.tugas.find(function (t) { return t.k === 'IR64 Apex|S'; }).tulis === 14800 && LB.tugas.find(function (t) { return t.k === 'Pandan Wangi|S'; }).lama === 0, J(LB));
terapkanKeCache(susunLabelSelesai('IR64 Apex|S', W).dokumen); ok('label satu selesai → tinggal 2; semua selesai → 0; selesai lagi ditolak', susunLabelTugas(hgSemua(KINI)).tugas.length === 2 && (function () { terapkanKeCache(susunLabelSelesai('semua', W).dokumen); return susunLabelTugas(hgSemua(KINI)).tugas.length === 0 && /Tidak ada label/.test(susunLabelSelesai('semua', W).tolak); })());
ok('terbit lagi harga yang sama ke angka lama: label yang diingat = angka yang masih TERTULIS (kalau kembali ke tulisan label → tugas hilang)', (function () { terapkanKeCache(susunUbah('Angsa|L', '13.500', 'jual', W).dokumen); var t1 = susunTerbit(W, false); terapkanKeCache(t1.dokumen); var a = susunLabelTugas(hgSemua(KINI)).tugas.find(function (t) { return t.k === 'Angsa|L'; }); terapkanKeCache(susunUbah('Angsa|L', '13.000', 'jual', W).dokumen); var t2 = susunTerbit(W, false); terapkanKeCache(t2.dokumen); var b = susunLabelTugas(hgSemua(KINI)).tugas.find(function (t) { return t.k === 'Angsa|L'; }); return a && a.lama === 13000 && a.tulis === 13500 && !b; })());
terapkanKeCache(susunUbah('Angsa|K50', '710.000', 'jual', W).dokumen); S = hgSemua(KINI);
ok('draf TIDAK membuat tugas label (label = yang sudah terbit saja)', S.nDraf === 1 && susunLabelTugas(S).tugas.length === 0, J(susunLabelTugas(S)));
T = susunTerbit(W, false); ok('terbit memakai id dokumen katalog yang SUDAH ADA (angsa50), bukan id rumus — katalog tidak jadi dua', T.dokumen[0].koleksi === 'katalogHargaKemasan' && T.dokumen[0].data.id === 'angsa50' && T.dokumen[0].data.hargaPerUnit === 710000 && T.dokumen[0].data.ukuran === 50 && T.dokumen[0].data.merk === 'Angsa', J(T.dokumen[0]));
terapkanKeCache(T.dokumen); ok('sesudahnya: tetap SATU dokumen kemasan Angsa (bukan dua), label 1 tugas (700.000 → 710.000)', ambilHargaKemasan().filter(function (h) { return h.merk === 'Angsa'; }).length === 1 && susunLabelTugas(hgSemua(KINI)).tugas.length === 1 && susunLabelTugas(hgSemua(KINI)).tugas[0].lama === 700000, J(ambilHargaKemasan()));
ok('terbit tanpa draf ditolak', /Tidak ada draf/.test(susunTerbit(W, false).tolak));

// ==================== H2 · BON PEMASOK ====================
var B = susunBon(KINI); var bn = function (id) { return B.bon.find(function (b) { return b.id === id; }); };
ok('bon dari mesin beku: 3 bon terbuka · total 12.450.000 · 2 pemasok; b1 SEBAGIAN (dibayar 20.000.000 dari 23.200.000, sisa 3.200.000) TETAP di daftar', B.nBon === 3 && B.total === 12450000 && B.nPemasok === 2 && bn('b1').sisa === 3200000 && bn('b1').dibayar === 20000000 && bn('b1').cap === 'sebagian', J(B.bon));
ok('tempo RODA dari KARTU (21 hari): b1 20 Agu → jatuh 10 Sep → LEWAT 9 hari; b3 12 Sep → 3 Okt → 14 hari lagi (jauh, dekat = 7); SEJATI kartu kosong → tempo UMUM bawaan 21 (angka Atur Barang masuk), tapi bon lamanya tanpa tanggal → TIDAK diramal', bn('b1').status === 'lewat' && bn('b1').sisaHari === -9 && /LEWAT 9 hari/.test(bn('b1').tempoTeks) && bn('b3').status === 'jauh' && bn('b3').jatuh === '2026-10-03' && bn('502').status === 'tanpaTempo' && bn('502').tempo.sumber === 'umum' && bn('502').tempo.hari === 21 && /bawaan/.test(bn('502').tempo.teks) && tempoPemasok('RODA CONTOH').sumber === 'kartu', J(B.bon.map(function (b) { return b.id + ':' + b.status + ':' + b.jatuh; })));
ok('tempo umum owner (aturanToko/catatStok.tempoHari 30) mengalahkan bawaan untuk kartu kosong; kartu RODA 21 tetap menang', (function () { terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'catatStok', tempoHari: 30 } }]); var t = tempoPemasok('SEJATI CONTOH'); var r = tempoPemasok('RODA CONTOH'); terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'catatStok' }]); return t.sumber === 'umum' && t.hari === 30 && /Atur Barang masuk/.test(t.teks) && r.hari === 21 && r.sumber === 'kartu'; })());
ok('kartu tempo dikosongkan → jatuh ke tempo umum bawaan 21 (b3 tetap 3 Okt, sumber umum); bon TANPA TANGGAL tidak pernah diramal', (function () { terapkanKeCache(susunKartu('RODA CONTOH', { tempo: '0', kontak: '0812 3456 7890', catatan: 'antar tiap Jumat' }, W).dokumen); var b = susunBon(KINI).bon.find(function (x) { return x.id === 'b3'; }); terapkanKeCache(susunKartu('RODA CONTOH', { tempo: '21', kontak: '0812 3456 7890', catatan: 'antar tiap Jumat' }, W).dokumen); return b.status === 'jauh' && b.jatuh === '2026-10-03' && b.tempo.sumber === 'umum' && susunBon(KINI).bon.find(function (x) { return x.id === '502'; }).jatuh === ''; })());
ok('tusukan: per pemasok, bon tertua di atas & ditandai SARAN (RODA: b1 saran, b3); isi bon menyebut mereknya & kg', B.tusukan[0].pemasok === 'RODA CONTOH' && B.tusukan[0].bon[0].id === 'b1' && B.tusukan[0].bon[0].saran && !B.tusukan[0].bon[1].saran && /Angsa, IR64 Apex, Pandan Wangi · 1\.700 kg/.test(bn('b1').isi) && B.tusukan[0].total === 7450000, J(B.tusukan));
ok('kas belum disetel → adaKas false, garis tanpa penanda "uang habis", cukupTeks mengaku belum bisa dibandingkan; ringkas lewat 1 (menyala)', !B.adaKas && !B.garis.some(function (g) { return g.tanda && g.kelas === 'habis'; }) && /belum bisa dihitung/.test(B.cukupTeks) && B.ringkas[0].a === '1' && B.ringkas[0].nyala && B.ringkas[2].a === '1', J([B.ringkas, B.cukupTeks]));
localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: '2026-09-18', laci: 3000000, rekening: 2000000 }));
B = susunBon(KINI); var kasNyata = kasPada();
ok('kas dari titik kas 18 Sep + gerakan sesudahnya (= kasPada mesin); garis: "hari ini" sebelum b3, penanda "uang toko habis di sini" muncul karena 5 jt-an < 7.450.000', B.adaKas && B.kas === kasNyata && kasNyata < 7450000 && B.garis.some(function (g) { return g.tanda && g.kelas === 'kini'; }) && B.garis.some(function (g) { return g.tanda && g.kelas === 'habis'; }) && B.kurang && /TIDAK cukup/.test(B.cukupTeks) && B.garis[B.garis.length - 1].id === '502' && B.garis.some(function (g) { return g.tanda && /tempo belum disepakati/.test(g.teks); }), J(B.garis.map(function (g) { return g.tanda ? 'T:' + g.kelas : g.id; })) + ' kas ' + kasNyata);
var BK = bukuBon('RODA CONTOH');
ok('buku bon RODA: 20 Agu +23.200.000 → 10 Sep bayar −20.000.000 → 12 Sep +4.250.000; utang jadi 7.450.000 (saldo berjalan menutup)', BK.baris.length === 3 && BK.baris[0].n === 23200000 && BK.baris[1].n === -20000000 && BK.baris[1].saldo === 3200000 && BK.baris[2].saldo === 7450000 && BK.saldo === 7450000, J(BK));
ok('buku bon SEJATI: bon lama tanpa tanggal paling atas; kedatangan TUNAI tidak masuk buku bon', bukuBon('SEJATI CONTOH').baris.length === 1 && bukuBon('SEJATI CONTOH').baris[0].teks === 'Bon lama (sebelum sistem)' && bukuBon('SEJATI CONTOH').saldo === 5000000, J(bukuBon('SEJATI CONTOH')));
// ---- bayar: satu pembayaran satu bon
var H = hitungBayar({ pemasok: 'RODA CONTOH', bonId: 'b1', ketik: '3.300.000', dari: 'laci' }, KINI); ok('bayar melebihi sisa bon DITOLAK dengan kalimat "satu pembayaran satu bon"', /Melebihi sisa bon ini \(Rp3\.200\.000\)/.test(H.tolak), J(H.tolak));
H = hitungBayar({ pemasok: 'RODA CONTOH', bonId: 'b1', ketik: '3.200.000', dari: '' }, KINI); ok('tanpa "dari mana" ditolak', /Uangnya dari mana/.test(H.tolak));
H = hitungBayar({ pemasok: 'SEJATI CONTOH', bonId: '502', ketik: '5.000.000', dari: 'rekening', adminI: 0 }, KINI); ok('melebihi uang toko (total kas 5.000.000 diketahui; 5.000.000 + admin 2.500) DITOLAK menyebut kasnya & adminnya', kasNyata === 5000000 && /Uang toko cuma Rp5\.000\.000/.test(H.tolak) && /termasuk biaya admin/.test(H.tolak), J(H.tolak) + ' kas ' + kasNyata);
H = hitungBayar({ pemasok: 'RODA CONTOH', bonId: 'b1', ketik: '3.200.000', dari: 'rekening', adminI: 0 }, KINI);
ok('bayar lunas 3.200.000 dari rekening + BI-FAST 2.500: arti LUNAS, rekening berkurang 3.202.500 (termasuk admin), laba tidak berubah kecuali admin', !H.tolak && H.lunas && H.admin === 2500 && /LUNAS — keluar dari daftar/.test(H.arti.a) && /Rekening berkurang Rp3\.202\.500 \(termasuk admin Rp2\.500\)/.test(H.arti.b) && /laba TIDAK berubah/.test(H.arti.c) && /biaya admin Rp2\.500 masuk biaya toko/.test(H.arti.c) && H.label === 'BAYAR LUNAS Rp3.200.000', J(H.arti));
var BY = susunBayar({ pemasok: 'RODA CONTOH', bonId: 'b1', ketik: '3.200.000', dari: 'rekening', adminI: 0, catatan: 'lunas b1' }, W);
ok('dokumen bayar = bentuk simpanBayarBon {tipe bayar, pemasok, nominal, catatan, bonId, bonTanggal} + dari/biayaAdmin/adminNama; biaya admin = pengeluaranHarian kategori toko 2.500 yang menunjuk pembayarannya (dariBayarBon)', BY.dokumen.length === 2 && BY.dokumen[0].koleksi === 'utangPemasokMutasi' && BY.dokumen[0].data.tipe === 'bayar' && BY.dokumen[0].data.bonId === 'b1' && BY.dokumen[0].data.bonTanggal === '2026-08-20' && BY.dokumen[0].data.nominal === 3200000 && BY.dokumen[0].data.dari === 'rekening' && BY.dokumen[0].data.biayaAdmin === 2500 && BY.dokumen[0].data.adminNama === 'BI-FAST'
  && BY.dokumen[1].koleksi === 'pengeluaranHarian' && BY.dokumen[1].data.kategori === 'toko' && BY.dokumen[1].data.nominal === 2500 && BY.dokumen[1].data.dariBayarBon === BY.dokumen[0].data.id && /Biaya admin BI-FAST — bayar bon RODA CONTOH/.test(BY.dokumen[1].data.keterangan) && BY.patch.urung.id === BY.dokumen[0].data.id, J(BY.dokumen));
terapkanKeCache(BY.dokumen); B = susunBon(KINI);
ok('sesudah bayar: b1 keluar dari daftar (LUNAS), tinggal 2 bon, total 9.250.000; kas turun 3.202.500 (bayar + admin, keduanya gerakan kas)', B.nBon === 2 && !B.bon.some(function (b) { return b.id === 'b1'; }) && B.total === 9250000 && kasPada() === kasNyata - 3202500, J([B.total, kasPada(), kasNyata]));
var UR = susunUrungBayar(BY.dokumen[0].data.id); ok('urungkan: menghapus dokumen bayar DAN dokumen biaya adminnya', UR.hapus.length === 2 && UR.hapus[1].koleksi === 'pengeluaranHarian' && /biaya adminnya ikut dicabut/.test(UR.patch.kabar), J(UR));
terapkanKeCache(UR.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; })); ok('sesudah urung: b1 kembali, kas kembali', susunBon(KINI).nBon === 3 && kasPada() === kasNyata);
BY = susunBayar({ pemasok: 'RODA CONTOH', bonId: 'b3', ketik: '1.000.000', dari: 'laci', catatan: '' }, W); terapkanKeCache(BY.dokumen);
ok('bayar SEBAGIAN 1.000.000 dari laci: b3 tetap di daftar dengan sisa 3.250.000, cap "sebagian"; tanpa admin → satu dokumen saja', BY.dokumen.length === 1 && susunBon(KINI).bon.find(function (b) { return b.id === 'b3'; }).sisa === 3250000 && susunBon(KINI).bon.find(function (b) { return b.id === 'b3'; }).cap === 'sebagian' && /dibayar sebagian, sisa Rp3\.250\.000/.test(BY.patch.kabar), J(BY.patch));
// ---- bon lama
var LM = hitungBonLama({ pemasok: '', nama: 'roda contoh', ketik: '2.000.000' }); ok('bon lama: nama yang diketik sama dengan pemasok yang ada → dipakai nama yang ada (RODA CONTOH), bukan pemasok kembar', LM.pemasok === 'RODA CONTOH' && LM.kembar === 'RODA CONTOH' && !LM.tolak, J(LM));
LM = susunBonLama({ pemasok: '', nama: 'PEMASOK BARU', tgl: '2026-07-15', ketik: '2.000.000', catatan: 'nota kuning' }, W);
ok('bon lama pemasok baru: dokumen {tipe saldoAwal, pemasok, nominal, catatan, bonTanggal 2026-07-15}; arti: uang, stok, laba TIDAK berubah', LM.dokumen[0].data.tipe === 'saldoAwal' && LM.dokumen[0].data.pemasok === 'PEMASOK BARU' && LM.dokumen[0].data.nominal === 2000000 && LM.dokumen[0].data.bonTanggal === '2026-07-15' && LM.dokumen[0].data.tanggal === '2026-09-19' && /uang toko, stok, dan laba tidak berubah/.test(LM.patch.kabar), J(LM));
terapkanKeCache(LM.dokumen); ok('bon lama masuk daftar: 4 bon, 3 pemasok; PEMASOK BARU ada di daftarPemasok walau belum pernah kirim barang', susunBon(KINI).nBon === 4 && susunBon(KINI).nPemasok === 3 && !!cariPemasok('PEMASOK BARU') && cariPemasok('PEMASOK BARU').kedatangan === 0);
ok('bon lama tanpa nilai / tanpa nama ditolak', /Ketik nilai/.test(hitungBonLama({ pemasok: 'RODA CONTOH', ketik: '' }).tolak) && /nama pemasok/.test(hitungBonLama({ ketik: '5' }).tolak));
// ---- kartu pemasok
var KP = susunKartu('SEJATI CONTOH', { orang: 'Pak S', kontak: '0813-1111-2222', tempo: '14', catatan: 'transfer' }, W);
ok('kartu: dokumen pemasokCatatan {id kunci, nama, kontak, catatan} sistem lama + orang & tempo; tempo 14 → bon SEJATI kini diramal (sumber kartu)', KP.dokumen[0].koleksi === 'pemasokCatatan' && KP.dokumen[0].data.id === 'sejati contoh' && KP.dokumen[0].data.nama === 'SEJATI CONTOH' && KP.dokumen[0].data.tempo === 14 && KP.dokumen[0].data.orang === 'Pak S' && (function () { terapkanKeCache(KP.dokumen); return tempoPemasok('SEJATI CONTOH').sumber === 'kartu' && nomorWa(cariPemasok('SEJATI CONTOH').kontak) === '6281311112222'; })(), J(KP));
ok('kartu: tempo 200 ditolak; nama kosong ditolak', /0–120/.test(susunKartu('SEJATI CONTOH', { tempo: '200' }, W).tolak) && !!susunKartu('', {}, W).tolak);
ok('pemasok: kebiasaan bayar dari 3 kedatangan terakhir — RODA "biasanya BON" (2 dari 2), SEJATI "biasanya TUNAI"', cariPemasok('RODA CONTOH').caraBiasa === 'bon' && /biasanya BON \(2 dari 2/.test(cariPemasok('RODA CONTOH').caraTeks) && cariPemasok('SEJATI CONTOH').caraBiasa === 'tunai', J(daftarPemasok().map(function (p) { return p.nama + ':' + p.caraBiasa; })));
var AB = susunAturBon({ dekatHari: '10', admin: [{ nama: 'BI-FAST', n: '2.500' }, { nama: '', n: '0' }, { nama: 'RTGS', n: '30.000' }] }, W);
ok('atur bon: dekat 10 hari, daftar admin (baris kosong dibuang): BI-FAST 2.500 · RTGS 30.000', AB.dokumen[0].data.dekatHari === 10 && AB.dokumen[0].data.admin.length === 2 && AB.dokumen[0].data.admin[1].n === 30000 && /Biaya admin Rp1\.000 belum diberi nama/.test(susunAturBon({ admin: [{ nama: '', n: '1000' }] }, W).tolak), J(AB));
terapkanKeCache(AB.dokumen); ok('atur berlaku: b3 (14 hari lagi) kini "jauh"→ tetap; dekat = 10 → bon 7–10 hari jadi dekat (uji: tempo kartu RODA 28 → b3 jatuh 10 Okt = 21 hari → jauh; tempo 20 → 2 Okt = 13 hari → jauh; tempo 17 → 29 Sep = 10 hari → DEKAT)', (function () { terapkanKeCache(susunKartu('RODA CONTOH', { tempo: '17', kontak: '0812 3456 7890' }, W).dokumen); var s = susunBon(KINI).bon.find(function (b) { return b.id === 'b3'; }).status; terapkanKeCache(susunKartu('RODA CONTOH', { tempo: '21', kontak: '0812 3456 7890' }, W).dokumen); return s === 'dekat'; })());

// ==================== H3 · BELANJA ====================
var AL = aturBelanja();
ok('atur belanja bawaan: ambang 7 · target 14 · muatan TERUKUR = median kg 3 kedatangan (300, 500, 1.700) = 500, ditandai terukur', AL.ambangHari === 7 && AL.targetHari === 14 && AL.muatanKg === 500 && AL.muatanTerukur && !AL.dariOwner, J(AL));
var DB = daftarBelanja(KINI); var mk = function (m) { return DB.merk.find(function (x) { return x.merk === m; }); };
ok('daftar: Apex habis 3 hari ≤ 7 → PERLU, saran 8 karung 50 kg; Angsa 17 hari tidak perlu; Pandan Wangi tanpa laju → hari null, tidak ditebak', mk('IR64 Apex').hari === 3 && mk('IR64 Apex').perlu && mk('IR64 Apex').saranK === 8 && mk('Angsa').hari === 17 && !mk('Angsa').perlu && mk('Pandan Wangi').hari === null && !mk('Pandan Wangi').perlu && /tidak ditebak/.test(mk('Pandan Wangi').sisaTeks), J(DB.merk.map(function (x) { return x.merk + ':' + x.hari + ':' + x.saranK; })));
ok('sumber harga per pemasok: Angsa dari RODA 13.500 (12 Sep) & SEJATI 13.600 (5 Sep) → termurah RODA; Apex hanya RODA 14.500; tanggal harga selalu ada', mk('Angsa').sumber.length === 2 && mk('Angsa').termurah.pemasok === 'RODA CONTOH' && mk('Angsa').termurah.harga === 13500 && mk('Angsa').termurah.tanggal === '2026-09-12' && mk('IR64 Apex').sumber.length === 1, J(mk('Angsa').sumber));
ok('pemasok belanja: RODA (bon, tempo 21 kartu, kontak) & SEJATI (tunai); PEMASOK BARU (bon lama saja, nol kedatangan) tidak ikut', DB.pemasok.length === 2 && DB.pemasok.find(function (p) { return p.nama === 'RODA CONTOH'; }).cara === 'bon' && DB.pemasok.find(function (p) { return p.nama === 'SEJATI CONTOH'; }).cara === 'tunai', J(DB.pemasok));
var HB = hitungBelanja({}, KINI);
ok('daftar kosong: kelompok "Habis dalam 7 hari" = Apex; "Masih aman" = Angsa; "Belum bisa dihitung" = Pandan; ringkas habis ≤ 2 hari 0, perlu 1', HB.kelompok[0].judul === 'Habis dalam 7 hari' && HB.kelompok[0].isi[0].merk === 'IR64 Apex' && HB.kelompok[1].isi[0].merk === 'Angsa' && HB.kelompok[2].isi[0].merk === 'Pandan Wangi' && HB.ringkas[0].a === 0 && HB.ringkas[1].a === 1 && HB.perluSemua.length === 1 && !HB.pesanTeks, J(HB.kelompok.map(function (g) { return g.judul; })));
var PN = tulisPesan({}, 'IR64 Apex', 'RODA CONTOH', 8); HB = hitungBelanja(PN, KINI); var RR = HB.perP.find(function (r) { return r.pemasok === 'RODA CONTOH'; });
ok('pesan 8 karung Apex ke RODA: 400 kg · ±5.800.000 (8 × 50 × 14.500); truk 500 kg → masih muat 100 kg (2 karung); Apex sesudahnya cukup ±14 hari; uang: BON → jadi utang, jatuh tempo ±10 Okt (hari ini + 21)', RR.karung === 8 && RR.kg === 400 && RR.rp === 5800000 && RR.sisaMuat === 100 && HB.baris.find(function (b) { return b.merk === 'IR64 Apex'; }).hariSesudah === 14 && /Biasanya BON — jadi utang ±Rp5\.800\.000, jatuh tempo ±10 Okt 2026/.test(RR.uangTeks) && HB.pesanTeks === '8 karung · 400 kg · ±Rp5.800.000', J([RR.uangTeks, HB.pesanTeks]));
var TK = susunTruk(HB, 'RODA CONTOH'); ok('truk: satu potongan bak APEX 8 (≥ 20 % muatan) + sisa kosong 100; "masih muat 100 kg · 2 karung"; bisa dipenuhi', TK.bak.length === 2 && TK.bak[0].t === 'IR64 8' && TK.bak[1].kelas === 'kosongbak' && TK.bak[1].flex === 100 && TK.muatSisa === 'masih muat 100 kg · 2 karung' && TK.bisaPenuhi, J(TK));
var PF = penuhiTruk(HB, 'RODA CONTOH', PN); ok('penuhi truk: 2 karung ditambahkan ke yang paling cepat habis sesudah pesanan (Apex 14 hari < Angsa 17) → Apex 10 karung, truk penuh', PF.tambahan === 2 && PF.pesan['IR64 Apex'].k === 10 && !PF.pesan.Angsa && susunTruk(hitungBelanja(PF.pesan, KINI), 'RODA CONTOH').muatSisa === 'truknya penuh', J(PF));
var PS2 = tulisPesan(PN, 'Angsa', 'SEJATI CONTOH', 4); HB = hitungBelanja(PS2, KINI); var RS = HB.perP.find(function (r) { return r.pemasok === 'SEJATI CONTOH'; });
ok('Angsa 4 karung dari SEJATI (13.600): 200 kg · 2.720.000; TUNAI → perlu uang waktu datang, dibandingkan dengan uang toko (kas diketahui) → cukup/kurang disebut', RS.karung === 4 && RS.rp === 2720000 && /Biasanya TUNAI — perlu ±Rp2\.720\.000/.test(RS.uangTeks) && (/cukup\.$/.test(RS.uangTeks) || /KURANG/.test(RS.uangTeks)) && RS.uangAwas === (2720000 > kasPada()), RS.uangTeks + ' kas ' + kasPada());
var KT = HB.kertas; ok('kertas: dua pemasok, tiap lembar isi yang dipilih + yang disarankan; lainnya (belum perlu) = Pandan Wangi', KT.length === 2 && KT[0].isi.length >= 1 && HB.lainnya.some(function (b) { return b.merk === 'Pandan Wangi'; }) && !HB.lainnya.some(function (b) { return b.merk === 'IR64 Apex'; }), J(KT.map(function (k) { return k.pemasok + ':' + k.isi.map(function (b) { return b.merk; }).join('/'); })));
ok('tulisPesan 0 karung menghapus barisnya', !tulisPesan(PS2, 'Angsa', 'SEJATI CONTOH', 0).Angsa);
var SP = susunPesanan(PS2, 'RODA CONTOH', W, false);
ok('pesanan RODA: teks WA berkop *Pesanan Toko Beras M.IQBAL*, baris "• IR64 Apex — 8 karung × 50 kg", jumlah; tautan wa.me/628123456790 (nomor kartu 0812… → 62812…); perkiraan harga TIDAK ikut', SP.baris[0] === '*Pesanan Toko Beras M.IQBAL*' && SP.baris.some(function (t) { return t === '• IR64 Apex — 8 karung × 50 kg'; }) && SP.baris.some(function (t) { return t === 'Jumlah 8 karung · 400 kg'; }) && !SP.baris.some(function (t) { return /Perkiraan/.test(t); }) && /^https:\/\/wa\.me\/6281234567890\?text=/.test(SP.tautan), J(SP.baris) + ' ' + SP.tautan);
ok('dokumen pesananPemasok {pemasok, baris [{merk, karung, berat, kg, hargaPerKg}], karung 8, kg 400, rp, status menunggu, teks, keNomor}; pesan Angsa (SEJATI) tetap tersisa di daftar', SP.dokumen[0].koleksi === 'pesananPemasok' && SP.dokumen[0].data.status === 'menunggu' && SP.dokumen[0].data.baris[0].merk === 'IR64 Apex' && SP.dokumen[0].data.baris[0].hargaPerKg === 14500 && SP.dokumen[0].data.karung === 8 && SP.dokumen[0].data.keNomor === '6281234567890' && SP.pesanSisa.Angsa && !SP.pesanSisa['IR64 Apex'], J(SP.dokumen));
ok('perkiraan harga ikut kalau diminta', susunPesanan(PS2, 'RODA CONTOH', W, true).baris.some(function (t) { return t === 'Perkiraan Rp5.800.000'; }));
ok('pesanan ke pemasok yang tak pernah kirim / tanpa karung ditolak', /tidak dikenal/.test(susunPesanan(PS2, 'PEMASOK BARU', W, false).tolak) && /Belum ada karung/.test(susunPesanan({}, 'RODA CONTOH', W, false).tolak));
terapkanKeCache(SP.dokumen); DB = daftarBelanja(KINI); HB = hitungBelanja(SP.pesanSisa, KINI);
ok('sesudah dipesan: Apex TIDAK disarankan lagi (dipesan, menunggu datang), masuk kelompok "Sudah dipesan"; ringkas sudah dipesan 1; pesananMenunggu 1', !mk('IR64 Apex').perlu && !!mk('IR64 Apex').dipesan && HB.kelompok.some(function (g) { return g.judul === 'Sudah dipesan' && g.isi[0].merk === 'IR64 Apex'; }) && HB.ringkas[2].a === 1 && pesananMenunggu().length === 1 && /sudah dipesan 19 Sep 2026 — menunggu datang/.test(HB.baris.find(function (b) { return b.merk === 'IR64 Apex'; }).dipesanTeks), J(HB.kelompok.map(function (g) { return g.judul; })));
terapkanKeCache([{ koleksi: 'batchMasuk', data: batchBaru('b4', '2026-09-19', '11:00', 'RODA CONTOH') }]);
ok('kedatangan RODA SESUDAH pesanan (19 Sep 11:00 > 10:00) → pesanan otomatis DATANG (tanggal kedatangan tercatat); Apex bisa disarankan lagi kalau perlu', pesananSemua()[0].status === 'datang' && pesananSemua()[0].datangTanggal === '2026-09-19' && pesananMenunggu().length === 0, J(pesananSemua()));
terapkanKeCache([{ koleksi: 'batchMasuk', hapus: 'b4' }]); ok('tanpa kedatangan itu → kembali menunggu (status dibaca dari data, bukan disimpan)', pesananMenunggu().length === 1);
var UB = susunUbahPesanan(SP.dokumen[0].data.id, 'batal', W); terapkanKeCache(UB.dokumen);
ok('batalkan pesanan: status batal tersimpan, Apex disarankan lagi; keadaan asing ditolak', pesananMenunggu().length === 0 && daftarBelanja(KINI).merk.find(function (x) { return x.merk === 'IR64 Apex'; }).perlu && /Keadaan tidak dikenal/.test(susunUbahPesanan(SP.dokumen[0].data.id, 'x', W).tolak), J(UB));
ok('penuhi truk TIDAK menebak: pemasok yang mereknya tanpa laju (TIGA CONTOH · Beras Merah, nol penjualan) → 0 karung ditambahkan', (function () { var b = ambilSemuaBatch(); pasok('batchMasuk', b.concat([{ id: 'b0', tanggal: '2026-08-01', jam: '08:00', pemasok: 'TIGA CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: 'b00', merk: 'Beras Merah', satuan: 'karung', beratKarung: 50, jumlahKarung: 10, totalKg: 500, hargaPerKg: 18000, subtotalHarga: 9000000 }] }]));
  var H0 = hitungBelanja({}, KINI); var r = penuhiTruk(H0, 'TIGA CONTOH', {}); var muat = H0.atur.muatanKg; pasok('batchMasuk', b); return r.tambahan === 0 && Object.keys(r.pesan).length === 0 && muat === 500; })());
var ABL = susunAturBelanja({ ambangHari: '2', targetHari: '21', muatanKg: '3.000' }, W); terapkanKeCache(ABL.dokumen);
ok('atur belanja owner: ambang 2 · target 21 · muatan 3.000 (tidak lagi terukur); Apex 3 hari kini TIDAK perlu (> 2), sarannya tetap dihitung = ceil((39,29 × 21 − 150) / 50) = 14; muatan nol ditolak', aturBelanja().muatanKg === 3000 && !aturBelanja().muatanTerukur && aturBelanja().ambangHari === 2 && daftarBelanja(KINI).merk.find(function (x) { return x.merk === 'IR64 Apex'; }).perlu === false && daftarBelanja(KINI).merk.find(function (x) { return x.merk === 'IR64 Apex'; }).saranK === 14 && /tidak boleh nol/.test(susunAturBelanja({ muatanKg: '0' }, W).tolak), J(aturBelanja()));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""
BATCH_BARU = r"""
function batchBaru(id, tgl, jam, pemasok) { return { id: id, tanggal: tgl, jam: jam, pemasok: pemasok, caraBayar: 'utang', biayaBongkar: 0, merkList: [{ id: id + '0', merk: 'IR64 Apex', satuan: 'karung', beratKarung: 50, jumlahKarung: 8, totalKg: 400, hargaPerKg: 14500, subtotalHarga: 5800000 }] }; }
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var S = hgSemua(KINI); var salah = [];
// tiap dokumen katalog = satu baris dengan angka yang sama
var nDok = 0; [['katalogHargaKarung', 'S', 'hargaPerKg'], ['katalogHargaLiteran', 'L', 'hargaPerLiter'], ['katalogHargaKemasan', 'K', 'hargaPerUnit']].forEach(function (x) { (CAD[x[0]] || []).forEach(function (d) { nDok += 1; var sid = x[1] === 'K' ? 'K' + Number(d.ukuran) : x[1]; var b = cariBaris(S, kunciHarga(d.merk, sid)); if (!b) salah.push('katalog tanpa baris: ' + d.merk + ' ' + sid); else if (b.lamaN !== Math.round(Number(d[x[2]]) || 0)) salah.push('angka beda: ' + b.k); }); });
var B = susunBon(KINI); var up = hitungUtangPemasok(); var totalMesin = up.reduce(function (a, x) { return a + x.totalUtang; }, 0), nBonMesin = up.reduce(function (a, x) { return a + x.bon.length; }, 0);
if (B.total !== totalMesin || B.nBon !== nBonMesin) salah.push('bon ≠ mesin: ' + B.total + ' vs ' + totalMesin);
var D = daftarBelanja(KINI); var stokK = hitungStokKarungPerMerk(); var laju = hitungLajuPakai().kgMerk || {};
D.merk.forEach(function (m) { var h = hariHabis((stokK[m.merk] || {}).sisaKg || 0, laju[m.merk] || 0); if (h !== m.hari) salah.push('hari beda: ' + m.merk); });
// kolom dokumen vs cadangan (kolom baru sistem baru disebut eksplisit)
var kenal = function (nama) { var o = {}; (CAD[nama] || []).forEach(function (d) { Object.keys(d).forEach(function (k) { o[k] = 1; }); }); return o; };
var WX = { tanggal: '2026-09-22', jam: '10:00', kini: '2026-09-22T03:00:00.000Z', idUnik: function () { return Math.random(); } };
var kU = kenal('utangPemasokMutasi'); var px = B.bon[0]; var catatan = []; var pgAsli = cacheMentah('pengaturan').slice(); var tanpaTitik = false;
if (px) { var by = susunBayar({ pemasok: px.pemasok, bonId: px.id, ketik: '1', dari: 'laci' }, WX);
  // Kas toko di cadangan bisa memang kurang dari Rp1 (mesin beku kasPada, sama persis dengan sistem lama): penjaga kas MENOLAK dengan benar → itu catatan,
  // bukan kegagalan. Kolom dokumen tetap diuji: titik kas disingkirkan SEMENTARA (kasPada = null → penjaga tidak berlaku), lalu dikembalikan.
  if (!by.dokumen && B.adaKas && B.kas < 1 && /^Uang toko cuma /.test(by.tolak || '')) { catatan.push('kas toko di cadangan ' + B.kas + ' (kasPada, titik kas ' + ((pgAsli.find(function (d) { return String(d.id) === 'titikKas'; }) || {}).tanggal || '?') + ') → bayar ditolak penjaga kas, benar; kolom diuji tanpa titik kas');
    pasok('pengaturan', pgAsli.filter(function (d) { return String(d.id) !== 'titikKas'; })); tanpaTitik = true; by = susunBayar({ pemasok: px.pemasok, bonId: px.id, ketik: '1', dari: 'laci' }, WX); }
  if (by.dokumen) Object.keys(by.dokumen[0].data).forEach(function (k) { if (!kU[k] && ['dari', 'biayaAdmin', 'adminNama'].indexOf(k) < 0) salah.push('bayar.' + k); }); else salah.push('bayar ditolak: ' + by.tolak); }
var bl = susunBonLama({ pemasok: '', nama: 'X CONTOH', tgl: '2026-07-01', ketik: '1', catatan: 'x' }, WX); if (bl.dokumen) Object.keys(bl.dokumen[0].data).forEach(function (k) { if (!kU[k]) salah.push('saldoAwal.' + k); });
var kC = kenal('pemasokCatatan'); var kr = susunKartu(px ? px.pemasok : 'X', { kontak: '0', tempo: '7' }, WX); if (kr.dokumen) Object.keys(kr.dokumen[0].data).forEach(function (k) { if (!kC[k] && ['orang', 'tempo'].indexOf(k) < 0) salah.push('kartu.' + k); });
var kH = kenal('pengeluaranHarian'); if (px && (B.adaKas === false || tanpaTitik)) { var by2 = susunBayar({ pemasok: px.pemasok, bonId: px.id, ketik: '1', dari: 'rekening', adminI: 0 }, WX); if (by2.dokumen && by2.dokumen[1]) Object.keys(by2.dokumen[1].data).forEach(function (k) { if (!kH[k] && k !== 'dariBayarBon') salah.push('harian.' + k); }); }
if (tanpaTitik) pasok('pengaturan', pgAsli);
var b0 = S.baris.find(function (b) { return b.st.id === 'S' && b.modalUnit > 0 && b.lamaN > 0; }); if (b0) { terapkanKeCache(susunUbah(b0.k, String(b0.lamaN + 100), 'jual', WX).dokumen); var T = susunTerbit(WX, true); var kK = kenal('katalogHargaKarung'); if (T.dokumen) Object.keys(T.dokumen[0].data).forEach(function (k) { if (!kK[k] && k !== 'modalSaatSetel') salah.push('katalogKarung.' + k); }); else salah.push('terbit ditolak: ' + T.tolak); }
print(JSON.stringify({ salah: salah, catatan: catatan, baris: S.baris.length, nDok: nDok, perlu: S.perlu.length, ringkas: S.ringkas.map(function (r) { return r.l + ' ' + r.a; }).join(' · '), target: S.target, targetDariRata: S.atur.targetDariRata, bongkar: S.atur.bongkarKg, bon: B.nBon, total: B.total, lewat: B.lewat.length, merk: D.merk.length, perluBeli: D.merk.filter(function (m) { return m.perlu; }).length, muatan: D.atur.muatanKg, pemasok: D.pemasok.map(function (p) { return p.nama.split(' ')[0] + ':' + p.cara; }).join(' · ') }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:900]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(JAM_TETAP + js + BATCH_BARU + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            # ---- H1 katalog
            'rugi memakai >= (untung nol jadi RUGI)': js.replace("const status = margin < -0.5 ? 'rugi' : Math.abs(margin) <= 0.5 ? 'nol'", "const status = margin <= 0.5 ? 'rugi' : Math.abs(margin) <= 0.5 ? 'nol'"),
            '"modal naik sesudah harga disetel" tidak terbaca (dimakan = bawah)': js.replace("const setel = hgModalSetel(dok, m); const naik = setel > 0 && beliTerbaru(m) > setel + 0.5;", "const setel = 0; const naik = false;"),
            'target bawaan angka karangan (bukan rata-rata yang berlaku)': js.replace("return { targetPerKg: t === null ? targetTerukur() : t, targetDariRata: t === null,", "return { targetPerKg: t === null ? 600 : t, targetDariRata: t === null,"),
            'usul tidak dibulatkan ke atas': js.replace("const usul = modalUnit > 0 ? hgBulatAtas(modalUnit + target * st.kg, atur[st.bulat]) : 0;", "const usul = modalUnit > 0 ? Math.round(modalUnit + target * st.kg) : 0;"),
            'modal kemasan tidak diambil dari adukan (beras saja)': js.replace("if (x && x.hppRataRataPerUnit > 0) { modalUnit = x.hppRataRataPerUnit; modalDari = 'adukan'; } else if", "if (false) { modalUnit = x.hppRataRataPerUnit; modalDari = 'adukan'; } else if"),
            'laku menghitung baris yang dibatalkan': js.replace("  ambilPenjualan().forEach((p) => { if ((p.tanggal || '') < mulai) return;\n    if (p.jenis === 'literan'", "  ambilPenjualanSemua().forEach((p) => { if ((p.tanggal || '') < mulai) return;\n    if (p.jenis === 'literan'"),
            'ubah harga langsung ke katalog (bukan draf)': js.replace("  const d = Object.assign({}, S.draf); if (u.n === u.b.lamaN) delete d[k]; else d[k] = u.n;\n  return { dokumen: [hgDokDraf(d, w)],", "  return { dokumen: [{ koleksi: u.b.koleksi, data: hgDokKatalog(Object.assign({}, u.b, { n: u.n }), w) }],"),
            'harga pasar diam-diam jadi draf': js.replace("if (mode === 'pasar') return { dokumen: [{ koleksi: 'hargaPasar', data: { id: k, kunci: k, harga: u.n, tanggal: w.tanggal, jam: w.jam } }],", "if (mode === 'pasar') return { dokumen: [{ koleksi: 'hargaPasar', data: { id: k, kunci: k, harga: u.n, tanggal: w.tanggal, jam: w.jam } }, hgDokDraf(Object.assign({}, S.draf, { [k]: u.n }), w)],"),
            '"sengaja" tidak gugur saat harga/modal berubah': js.replace("const sengajaAktif = !!sj && draf[k] === undefined && Number(sj.modal) === Math.round(modalUnit) && Number(sj.n) === lamaN && HG_PERLU.indexOf(N.status) >= 0;", "const sengajaAktif = !!sj && draf[k] === undefined && HG_PERLU.indexOf(N.status) >= 0;"),
            'kalimat dibulatkan selalu ke atas (turunkan literan diam-diam batal)': js.replace("const baru = K.arah === 'naik' ? hgBulatAtas(mentah, S.atur[b.st.bulat]) : hgBulatBawah(mentah, S.atur[b.st.bulat]);", "const baru = hgBulatAtas(mentah, S.atur[b.st.bulat]);"),
            'kalimat menghitung ulang dari modal, bukan dari harga sekarang': js.replace("const mentah = b.n + (K.arah === 'naik' ? 1 : -1) * rp * b.st.kg;", "const mentah = b.modalUnit + (K.arah === 'naik' ? 1 : -1) * rp * b.st.kg;"),
            'dampak memakai laku baris lain (bukan satuannya)': js.replace("const dampak = (b) => (!b.adaDraf && !b.sengaja && ['rugi', 'dimakan', 'bawah'].indexOf(b.status) >= 0 && b.usul > 0 ? Math.round((b.usul - b.n) * b.laku) : 0);", "const dampak = (b) => (!b.adaDraf && !b.sengaja && ['rugi', 'dimakan', 'bawah'].indexOf(b.status) >= 0 && b.usul > 0 ? Math.round((b.usul - b.n) * b.st.kg) : 0);"),
            'papan pembeli memperlihatkan draf': js.replace("const tampil = owner ? b.n : b.lamaN; const kosong = !(tampil > 0);", "const tampil = b.n; const kosong = !(tampil > 0);"),
            'teks WA ikut membawa draf': js.replace("const ada = S.baris.filter((b) => b.merk === m && b.lamaN > 0); if (ada.length) baris.push('• ' + m + ' — ' + ada.map((b) => b.st.pendek + ' ' + RP(b.lamaN).replace('Rp', '')).join(' · '));", "const ada = S.baris.filter((b) => b.merk === m && b.n > 0); if (ada.length) baris.push('• ' + m + ' — ' + ada.map((b) => b.st.pendek + ' ' + RP(b.n).replace('Rp', '')).join(' · '));"),
            'belah tidak menutup (sisa dihitung dari kotor saja)': js.replace("const sisa = harga - modal - bongkar - mdr;", "const sisa = harga - modal - bongkar;"),
            'potongan QRIS dikenakan juga di bawah batas': js.replace("const kenaMdr = B.bayar === 'qris' && harga > S.atur.mdrBatas;", "const kenaMdr = B.bayar === 'qris';"),
            'terbit dengan harga rugi tanpa ketukan kedua': js.replace("if (rugi.length && !yakin) return { tolak:", "if (false) return { tolak:"),
            'terbit lupa mengosongkan draf': js.replace("dokumen.push(hgDokDraf({}, w)); dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaLabel'", "dokumen.push({ koleksi: 'aturanToko', data: { id: 'hargaLabel'"),
            'terbit menulis dokumen katalog dengan id BARU (katalog jadi dua)': js.replace("const id = b.dok ? b.dok.id : b.st.id === 'K' + b.st.kg", "const id = b.st.id === 'K' + b.st.kg"),
            'label rak: tugas dibuat untuk draf (belum terbit)': js.replace("  const tugas = daftarLabel().map((t) => {", "  const tugas = daftarLabel().concat(S.baris.filter((b) => b.adaDraf).map((b) => ({ k: b.k, lama: b.lamaN, tanggal: '' }))).map((t) => {"),
            'label rak: angka yang diingat = harga lama terakhir, bukan yang masih tertulis': js.replace("const tertulis = ada ? Number(ada.lama) || 0 : b.lamaN;", "const tertulis = b.lamaN;"),
            'atur harga: langkah nol diterima': js.replace("|| baca('langkahRp', (n) => n > 0 && n <= 10000, 'Langkah naik-turun per kg harus 1–10.000 (tidak boleh nol)')", "|| baca('langkahRp', (n) => n >= 0 && n <= 10000, 'Langkah naik-turun per kg harus 1–10.000 (tidak boleh nol)')"),
            'ongkos bongkar per kg angka mati (bukan terukur)': js.replace("bongkarKg: bk === null ? bongkarTerukur() : bk, bongkarTerukur: bk === null,", "bongkarKg: bk === null ? 40 : bk, bongkarTerukur: bk === null,"),
            # ---- H2 bon pemasok
            'bon yang dibayar sebagian dianggap lunas': js.replace("bon.push({ id: String(b.id), pemasok: px.pemasok, tanggal: b.tanggal || '', nilai: Math.round(b.nilai || 0), dibayar: Math.round(b.dibayar || 0), sisa: Math.round(b.sisa || 0),", "if (b.dibayar > 0) return; bon.push({ id: String(b.id), pemasok: px.pemasok, tanggal: b.tanggal || '', nilai: Math.round(b.nilai || 0), dibayar: Math.round(b.dibayar || 0), sisa: Math.round(b.sisa || 0),"),
            'bon tanpa tanggal ikut diramal (jatuh dari tanggal kosong)': js.replace("const jatuh = T.hari > 0 && b.tanggal ? bpTambahHari(b.tanggal, T.hari) : '';", "const jatuh = T.hari > 0 ? bpTambahHari(b.tanggal || iso, T.hari) : '';"),
            'tempo umum owner diabaikan (selalu bawaan 21)': js.replace("return { hari: isFinite(n) && n > 0 ? n : TEMPO_UMUM_BAWAAN, dariOwner: isFinite(n) && n > 0 };", "return { hari: TEMPO_UMUM_BAWAAN, dariOwner: false };"),
            'tempo kartu diabaikan (selalu tempo umum)': js.replace("const p = cariPemasok(nama); if (p && p.tempo > 0) return { hari: p.tempo, sumber: 'kartu', teks: 'tempo ' + p.tempo + ' hari (kartu pemasok)' };", ""),
            'bayar melebihi sisa bon diterima': js.replace("else if (n > bon.sisa) tolak = 'Melebihi sisa bon ini", "else if (false) tolak = 'Melebihi sisa bon ini"),
            'bayar melebihi uang toko diterima': js.replace("else if (B.adaKas && n + admin > B.kas) tolak = 'Uang toko cuma '", "else if (false) tolak = 'Uang toko cuma '"),
            'biaya admin tidak masuk biaya toko (laba tidak berkurang)': js.replace("if (H.admin > 0) dokumen.push({ koleksi: 'pengeluaranHarian'", "if (false) dokumen.push({ koleksi: 'pengeluaranHarian'"),
            'dokumen bayar tanpa bonId (pembayaran mengalir ke bon tertua)': js.replace("nominal: H.n, catatan, bonId: H.bon.id, bonTanggal: H.bon.tanggal || null, dari: H.D.dari };", "nominal: H.n, catatan, bonTanggal: H.bon.tanggal || null, dari: H.D.dari };"),
            'urungkan meninggalkan dokumen biaya admin': js.replace("ambilPengeluaranHarian().forEach((h) => { if (String(h.dariBayarBon || '') === String(id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });", ""),
            'bon lama ditulis bertanggal hari ini (umurnya bohong)': js.replace("tipe: 'saldoAwal', pemasok: H.pemasok.slice(0, 60), nominal: H.n, catatan: String(H.D.catatan || '').trim().slice(0, 120), bonTanggal: H.D.tgl || null };", "tipe: 'saldoAwal', pemasok: H.pemasok.slice(0, 60), nominal: H.n, catatan: String(H.D.catatan || '').trim().slice(0, 120), bonTanggal: w.tanggal };"),
            'bon lama nama kembar dibuat pemasok baru': js.replace("const kembar = namaBaru ? daftarPemasok().find((p) => p.kunci === kunciPelanggan(namaBaru)) : null;", "const kembar = null;"),
            'kartu pemasok memakai id nama mentah (bukan kunci)': js.replace("const data = { id: kunciPelanggan(nm), nama: p ? p.nama : nm,", "const data = { id: nm, nama: p ? p.nama : nm,"),
            'garis jatuh tempo tanpa penanda uang habis': js.replace("if (kas !== null && !habisSudah && jalan + b.sisa > kas) {", "if (false) {"),
            'kebiasaan bayar pemasok dari SATU kedatangan terakhir': js.replace("const tiga = s.cara.slice(0, 3);", "const tiga = s.cara.slice(0, 1);"),
            # ---- H3 belanja
            'saran belanja tidak dibulatkan ke karung penuh': js.replace("const saranK = Math.ceil(butuh / berat);", "const saranK = Math.floor(butuh / berat);"),
            'merek tanpa laju ditebak habis 0 hari': js.replace("const hariHabis = (sisa, laju) => (!(sisa > 0) || !(laju > 0) ? null : Math.floor(sisa / laju + 1e-9));", "const hariHabis = (sisa, laju) => (!(sisa > 0) ? null : !(laju > 0) ? 0 : Math.floor(sisa / laju + 1e-9));"),
            'ambang hari setelan diabaikan': js.replace("perlu: hari !== null && hari <= atur.ambangHari && saranK > 0 && !dipesan,", "perlu: hari !== null && hari <= 7 && saranK > 0 && !dipesan,"),
            'yang sudah dipesan tetap disarankan': js.replace("const dipesan = menunggu.find((p) => (p.baris || []).some((b) => b.merk === m)) || null;", "const dipesan = null;"),
            'muatan truk angka mati 3.000 (bukan terukur)': js.replace("muatanKg: muat === null ? muatanTerukur() : muat, muatanTerukur: muat === null,", "muatanKg: muat === null ? 3000 : muat, muatanTerukur: muat === null,"),
            'penuhi truk menambah ke merek tanpa laju': js.replace("const calon = R.milik.filter((b) => b.laju > 0 && !b.dipesan && (!o[b.merk] || o[b.merk].p === pemasok)).map((b) => ({ b, k: b.k }));", "const calon = R.milik.filter((b) => !b.dipesan && (!o[b.merk] || o[b.merk].p === pemasok)).map((b) => ({ b, k: b.k }));"),
            'pesanan datang tidak dibaca dari kedatangan': js.replace("const status = p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : sesudah.length ? 'datang' : 'menunggu';", "const status = p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : 'menunggu';"),
            'harga termurah tanpa tanggal': js.replace("const sumber = pem.filter((p) => p.hargaPerMerk[m]).map((p) => ({ pemasok: p.nama, harga: p.hargaPerMerk[m].terakhir.hargaPerKg, tanggal: p.hargaPerMerk[m].terakhir.tanggal })).sort((a, b) => a.harga - b.harga);", "const sumber = pem.filter((p) => p.hargaPerMerk[m]).map((p) => ({ pemasok: p.nama, harga: p.hargaPerMerk[m].terakhir.hargaPerKg, tanggal: '' })).sort((a, b) => a.harga - b.harga);"),
            'uang belanja tunai tidak dibandingkan dengan kas': js.replace("(kas === null ? 'Uang toko belum bisa dihitung (titik kas belum disetel).' : 'Uang toko sekarang ' + RP(kas) + (rp > kas ? ' — KURANG ' + RP(rp - kas) + '.' : ' — cukup.'))", "''"),
            'nomor WhatsApp pemasok tidak dipakai': js.replace("const nomor = nomorWa(R.kontak);", "const nomor = '';"),
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
        c = json.load(open(cad[-1], encoding='utf-8'))
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        h, e = jalan("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s): %d baris harga dari %d dokumen katalog · %d perlu diputuskan · %s · target %s%s · bongkar %s/kg · bon %d = %s (lewat tempo %d) · belanja %d merek, %d perlu, muatan %s kg · %s · yang tidak cocok: %s%s'
                  % (os.path.basename(cad[-1]), h['baris'], h['nDok'], h['perlu'], h['ringkas'], h['target'], ' (rata-rata)' if h['targetDariRata'] else '', h['bongkar'], h['bon'], h['total'], h['lewat'], h['merk'], h['perluBeli'], h['muatan'], h['pemasok'], ', '.join(h['salah']) or 'tidak ada', (' · catatan (angka cadangan toko): ' + '; '.join(h['catatan'])) if h.get('catatan') else ''))
            if h['salah']: g.append('asap: ' + ', '.join(h['salah']))
    sys.exit(2 if g else 0)
