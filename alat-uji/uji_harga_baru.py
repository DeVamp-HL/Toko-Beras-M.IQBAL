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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/belanja-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/nego-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/setengah-logika.js', 'baru/js/layar/kelas-merek-logika.js', 'baru/js/layar/varian-logika.js', 'baru/js/layar/het-logika.js']   # tinjauan E1 · paket brief 9 Okt butir 8: HET: belanja membaca kelas mutu (merek lalu, harga kelas)
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
  # putaran 27 (Bagian 5): harga liter melekat pada WADAH — kotak pasir ini punya tiga wadah (Apex, Angsa, Pandan Wangi), belum ada yang disamakan isinya
  'wadahLiteran': [{'id': 1, 'tanggal': '2026-08-01', 'jam': '08:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'daftar': ['IR64 Apex', 'Angsa', 'Pandan Wangi']}],
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
ok('bayar lunas 3.200.000 dari rekening + BI-FAST 2.500: arti LUNAS, rekening berkurang 3.202.500 (termasuk admin), laba tidak berubah kecuali admin', !H.tolak && H.lunas && H.admin === 2500 && /LUNAS — keluar dari daftar/.test(H.arti.a) && /Rekening berkurang Rp3\.202\.500 lewat transfer \(termasuk admin Rp2\.500\)/.test(H.arti.b) && /utang ke RODA CONTOH berkurang Rp3\.200\.000 \(bukan Rp3\.202\.500\)/.test(H.arti.c) && /laba TIDAK berubah/.test(H.arti.c) && /biaya admin Rp2\.500 masuk biaya toko/.test(H.arti.c) && H.label === 'BAYAR LUNAS Rp3.200.000 · TRANSFER' && H.cara === 'transfer', J(H.arti));
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
var LB11 = { koleksi: 'batchMasuk', data: { id: 9911, tanggal: '2026-09-19', jam: '07:00', pemasok: 'LAHIR BUKU', caraBayar: 'tunai', biayaBongkar: 0, stokAwal: true, lahirBuku: true, merkList: [{ id: '1', merk: 'Wadah Contoh', satuan: 'lahir', beratKarung: 0, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, stokWadah: 'Contoh' }] } };
ok('39b-11 batch "LAHIR BUKU" (buku wadah / karung belakang) BUKAN pemasok: tidak di daftarPemasok; bon lama & kartu atas nama itu DITOLAK dengan kalimat (utang ke pemasok yang tidak ada)',
  denganCacheSementara([LB11], function () { return !daftarPemasok().some(function (p) { return /LAHIR BUKU/i.test(p.nama); }) && /nama yang dipakai sistem/.test(hitungBonLama({ pemasok: '', nama: 'lahir buku', ketik: '1.000.000' }).tolak || '')
    && /nama yang dipakai sistem/.test(hitungBonLama({ pemasok: 'LAHIR BUKU', ketik: '5' }).tolak || '') && /nama yang dipakai sistem/.test(susunKartu('LAHIR BUKU', { tempo: '7' }, W).tolak || '') && !pemasokSungguhan('Lahir Buku') && pemasokSungguhan('RODA CONTOH'); }),
  J(denganCacheSementara([LB11], function () { return [daftarPemasok().map(function (p) { return p.nama; }), hitungBonLama({ pemasok: 'LAHIR BUKU', ketik: '5' }).tolak]; })));
var KP = susunKartu('SEJATI CONTOH', { orang: 'Pak S', kontak: '0813-1111-2222', tempo: '14', catatan: 'transfer' }, W);
ok('kartu: dokumen pemasokCatatan {id kunci, nama, kontak, catatan} sistem lama + orang & tempo; tempo 14 → bon SEJATI kini diramal (sumber kartu)', KP.dokumen[0].koleksi === 'pemasokCatatan' && KP.dokumen[0].data.id === 'sejati contoh' && KP.dokumen[0].data.nama === 'SEJATI CONTOH' && KP.dokumen[0].data.tempo === 14 && KP.dokumen[0].data.orang === 'Pak S' && (function () { terapkanKeCache(KP.dokumen); return tempoPemasok('SEJATI CONTOH').sumber === 'kartu' && nomorWa(cariPemasok('SEJATI CONTOH').kontak) === '6281311112222'; })(), J(KP));
ok('kartu: tempo 200 ditolak; nama kosong ditolak', /0–120/.test(susunKartu('SEJATI CONTOH', { tempo: '200' }, W).tolak) && !!susunKartu('', {}, W).tolak);
// ---- PAKET F1 (owner 8 Okt 2026): bon lama BERGULIR — tanggalnya ikut kedatangan terakhir pemasoknya (utang lama satu pemasok, dikonfirmasi pemasok)
var KGF1 = susunKartu('SEJATI CONTOH', { orang: 'Pak S', kontak: '0813-1111-2222', tempo: '14', catatan: 'transfer', bonLamaBergulir: true }, W);
ok('F1 kartu: kolom bonLamaBergulir true ditulis; tanpa centang = false; kabar menyebut "ikut tanggal kedatangan terakhir"', KGF1.dokumen[0].data.bonLamaBergulir === true && susunKartu('SEJATI CONTOH', { tempo: '14' }, W).dokumen[0].data.bonLamaBergulir === false && /ikut tanggal kedatangan terakhir/.test(KGF1.patch.kabar), J(KGF1));
var BF0 = susunBon(KINI); terapkanKeCache(KGF1.dokumen); var BF1 = susunBon(KINI); var g0 = BF0.bon.find(function (b) { return b.id === '502'; }), g1 = BF1.bon.find(function (b) { return b.id === '502'; });
ok('F1 bon lama SEJATI (tanpa tanggal) bergulir ke kedatangan terakhir 5 Sep: jatuh 19 Sep (tempo kartu 14) = HARI INI, umur 14 hari, cap "bon bergulir", ket menyebut kedatangan terakhir & bon asli; tanggal dokumen TETAP kosong; sebelum dicentang tidak diramal; pemasok kartu membawa centangnya',
  g0.status === 'tanpaTempo' && !g0.gulir && g1.gulir === '2026-09-05' && g1.jatuh === '2026-09-19' && g1.sisaHari === 0 && g1.status === 'dekat' && /HARI INI/.test(g1.tempoTeks) && g1.umur === 14 && g1.cap === 'bon bergulir' && /ikut kedatangan terakhir 5 Sep/.test(g1.ket) && /bon asli tanpa tanggal/.test(g1.ket) && g1.tanggal === '' && cariPemasok('SEJATI CONTOH').bonLamaBergulir === true && cariPemasok('RODA CONTOH').bonLamaBergulir === false, J([g0, g1]));
ok('F1 nilai, sisa, total & bon pemasok lain TIDAK berubah (cuma umur/jatuh tempo bon lama yang bergulir)', BF1.total === BF0.total && g1.sisa === g0.sisa && g1.nilai === g0.nilai && BF1.bon.filter(function (b) { return b.pemasok === 'RODA CONTOH'; }).every(function (b) { var a = BF0.bon.find(function (x) { return x.id === b.id; }); return a && a.jatuh === b.jatuh && a.status === b.status && !b.gulir; }), J([BF0.total, BF1.total]));
terapkanKeCache(susunKartu('SEJATI CONTOH', { orang: 'Pak S', kontak: '0813-1111-2222', tempo: '14', catatan: 'transfer' }, W).dokumen);
ok('F1 centang dicabut → bon lama tanpa tanggal kembali tidak diramal', susunBon(KINI).bon.find(function (b) { return b.id === '502'; }).status === 'tanpaTempo' && !cariPemasok('SEJATI CONTOH').bonLamaBergulir);
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
var TK = susunTruk(HB, 'RODA CONTOH'); ok('truk: satu potongan bak per HARGA (owner 7 Okt) "14.500 · 8" (≥ 20 % muatan) + sisa kosong 100; "masih muat 100 kg · 2 karung"; bisa dipenuhi', TK.bak.length === 2 && TK.bak[0].t === '14.500 · 8' && TK.bak[1].kelas === 'kosongbak' && TK.bak[1].flex === 100 && TK.muatSisa === 'masih muat 100 kg · 2 karung' && TK.bisaPenuhi, J(TK));
var PF = penuhiTruk(HB, 'RODA CONTOH', PN); ok('penuhi truk: 2 karung ditambahkan ke yang paling cepat habis sesudah pesanan (Apex 14 hari < Angsa 17) → Apex 10 karung, truk penuh', PF.tambahan === 2 && PF.pesan['IR64 Apex'].k === 10 && !PF.pesan.Angsa && susunTruk(hitungBelanja(PF.pesan, KINI), 'RODA CONTOH').muatSisa === 'truknya penuh', J(PF));
var PS2 = tulisPesan(PN, 'Angsa', 'SEJATI CONTOH', 4); HB = hitungBelanja(PS2, KINI); var RS = HB.perP.find(function (r) { return r.pemasok === 'SEJATI CONTOH'; });
ok('Angsa 4 karung dari SEJATI (13.600): 200 kg · 2.720.000; TUNAI → perlu uang waktu datang, dibandingkan dengan uang toko (kas diketahui) → cukup/kurang disebut', RS.karung === 4 && RS.rp === 2720000 && /Biasanya TUNAI — perlu ±Rp2\.720\.000/.test(RS.uangTeks) && (/cukup\.$/.test(RS.uangTeks) || /KURANG/.test(RS.uangTeks)) && RS.uangAwas === (2720000 > kasPada()), RS.uangTeks + ' kas ' + kasPada());
var KT = HB.kertas; ok('kertas: dua pemasok, tiap lembar isi yang dipilih + yang disarankan; lainnya (belum perlu) = Pandan Wangi', KT.length === 2 && KT[0].isi.length >= 1 && HB.lainnya.some(function (b) { return b.merk === 'Pandan Wangi'; }) && !HB.lainnya.some(function (b) { return b.merk === 'IR64 Apex'; }), J(KT.map(function (k) { return k.pemasok + ':' + k.isi.map(function (b) { return b.merk; }).join('/'); })));
ok('tulisPesan 0 karung menghapus barisnya', !tulisPesan(PS2, 'Angsa', 'SEJATI CONTOH', 0).Angsa);
var SP = susunPesanan(PS2, 'RODA CONTOH', W, false);
ok('pesanan RODA: teks WA berkop *Pesanan Toko Beras M.IQBAL*, baris per HARGA (owner 7 Okt) "• IR64 Rp14.500/kg — 8 karung × 50 kg" (tinjauan E1: IR64 Apex = nama wadah/kelas buatan toko, TIDAK disebut sebagai merek lalu), jumlah; tautan wa.me/628123456790 (nomor kartu 0812… → 62812…); perkiraan harga TIDAK ikut', SP.baris[0] === '*Pesanan Toko Beras M.IQBAL*' && SP.baris.some(function (t) { return t === '• IR64 Rp14.500/kg — 8 karung × 50 kg'; }) && !SP.baris.some(function (t) { return t === '• IR64 Apex — 8 karung × 50 kg'; }) && SP.baris.some(function (t) { return t === 'Jumlah 8 karung · 400 kg'; }) && !SP.baris.some(function (t) { return /Perkiraan/.test(t); }) && /^https:\/\/wa\.me\/6281234567890\?text=/.test(SP.tautan), J(SP.baris) + ' ' + SP.tautan);
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
// ==================== owner 7 Okt · BELANJA PER HARGA BELI TERAKHIR (bukan per nama merek karung yang berganti-ganti) ====================
(function () {
  var bAsli = cacheMentah('batch').slice(), prAsli = cacheMentah('produksi').slice(), pgAsli = cacheMentah('pengaturan').slice();
  // RODA CONTOH mengirim tiga merek SEHARGA dengan Apex terakhir (14.500): TH · House (IR64 → satu baris dengan Apex), SB · Royal (IR42 → baris sendiri),
  // Ketan Contoh karung 25 kg (baris sendiri); + buku per ukuran Angsa 25 kg yang sudah dipisah (pindah jadi-karung-utuh) — dipesan dalam karung 25 kg
  terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'b9', tanggal: '2026-09-15', jam: '08:00', pemasok: 'RODA CONTOH', caraBayar: 'utang', biayaBongkar: 0, merkList: [
      { id: 'b90', merk: 'TH · House', satuan: 'karung', beratKarung: 50, jumlahKarung: 4, totalKg: 200, hargaPerKg: 14500, subtotalHarga: 2900000 },
      { id: 'b91', merk: 'SB · Royal', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 14500, subtotalHarga: 1450000 },
      { id: 'b92', merk: 'Ketan Contoh', satuan: 'karung', beratKarung: 25, jumlahKarung: 2, totalKg: 50, hargaPerKg: 14500, subtotalHarga: 725000 },
      { id: 'b93', merk: 'Angsa 25 kg', satuan: 'karung', beratKarung: 25, jumlahKarung: 2, totalKg: 50, hargaPerKg: 13600, subtotalHarga: 680000, indukUkuran: 'Angsa' }] } },
    { koleksi: 'produksiKemasan', data: { id: 'p9', tanggal: '2026-09-15', jam: '09:00', merkSumber: 'Angsa', namaProduk: 'Angsa 25 kg', ukuranKemasan: 25, jumlahUnit: 1, biayaKemasan: 0, upahRepacking: 0, hppSumberPerKgDipakai: 13250, hppPerUnit: 331250, sumberList: [{ merk: 'Angsa', kg: 25 }], kgDipakai: 25, jadiKarungUtuh: true, merkTujuan: 'Angsa 25 kg', pisahUkuran: { induk: 'Angsa', berat: 25, karung: 1 } } },
    { koleksi: 'pengaturan', data: { id: 'jenisBeras', peta: { 'TH · House': 'IR64', 'IR64 Apex': 'IR64', 'SB · Royal': 'IR42', 'Angsa': 'IR64' } } }]);
  var Db = daftarBelanja(KINI); var a25 = Db.merk.find(function (x) { return x.merk === 'Angsa 25 kg'; });
  ok('7 Okt: buku per ukuran "Angsa 25 kg" (dipisah lewat pindah jadi-karung-utuh) dipesan dalam karung 25 kg, bukan 50', a25 && a25.berat === 25, J(a25));
  var o = tulisPesan({}, 'IR64 Apex', 'RODA CONTOH', 8); o = tulisPesan(o, 'TH · House', 'RODA CONTOH', 3); o = tulisPesan(o, 'SB · Royal', 'RODA CONTOH', 2); o = tulisPesan(o, 'Ketan Contoh', 'RODA CONTOH', 2); o = tulisPesan(o, 'Angsa 25 kg', 'RODA CONTOH', 2);
  var H = hitungBelanja(o, KINI); var R = H.perP.find(function (r) { return r.pemasok === 'RODA CONTOH'; });
  var jm = function (d, k) { return d.reduce(function (a, x) { return a + x[k]; }, 0); };
  var g64 = R.g.find(function (g) { return g.kunci === '50|14500|IR64'; });
  ok('7 Okt kelompok harga: Apex 8 + TH · House 3 (IR64, Rp14.500, 50 kg) = SATU baris 11 karung; SB · Royal (IR42 seharga) & Ketan 25 kg tetap baris sendiri; Angsa 25 kg berlabel jenis induknya; Σ karung/kg/rp kelompok = Σ per merek (17 karung · 750 kg)',
    R.d.length === 5 && R.g.length === 4 && jm(R.g, 'k') === R.karung && R.karung === 17 && jm(R.g, 'kg') === R.kg && R.kg === 750 && jm(R.g, 'rp') === R.rp && g64 && g64.k === 11 && J(g64.merk.map(function (b) { return b.merk; })) === J(['IR64 Apex', 'TH · House'])
    && J(g64.kode) === J(['TH']) && R.g.some(function (g) { return g.kunci === '50|14500|IR42' && g.k === 2; }) && R.g.some(function (g) { return g.kunci === '25|14500|Ketan Putih' && g.k === 2; }) && R.g.some(function (g) { return g.kunci === '25|13600|IR64' && g.label === 'IR64 Rp13.600/kg'; }), J(R.g.map(function (g) { return [g.kunci, g.k, g.label, g.kode]; })));
  var SPg = susunPesanan(o, 'RODA CONTOH', W, false);
  ok('7 Okt pesanan WA per harga: termurah dulu, satu baris per harga ("• IR64 Rp14.500/kg — 11 karung × 50 kg (merek lalu: TH)" — nama wadah IR64 Apex tidak disebut), jumlah SAMA dengan per merek; dokumen: baris per merek tetap (penanda dipesan) + barisHarga',
    J(SPg.baris.slice(2)) === J(['• IR64 Rp13.600/kg — 2 karung × 25 kg (merek lalu: Angsa)', '• IR42 Rp14.500/kg — 2 karung × 50 kg (merek lalu: SB)', '• IR64 Rp14.500/kg — 11 karung × 50 kg (merek lalu: TH)', '• Ketan Putih Rp14.500/kg — 2 karung × 25 kg (merek lalu: Ketan Contoh)', 'Jumlah 17 karung · 750 kg'])
    && SPg.dokumen[0].data.baris.length === 5 && Array.isArray(SPg.dokumen[0].data.barisHarga) && SPg.dokumen[0].data.barisHarga.length === 4 && jm(SPg.dokumen[0].data.barisHarga, 'karung') === 17 && J(SPg.dokumen[0].data.barisHarga[2]) === J({ hargaPerKg: 14500, berat: 50, jenis: 'IR64', karung: 11, kg: 550, merk: ['IR64 Apex', 'TH · House'] }), J(SPg.baris));
  var kosongH = blKelompokHarga([{ merk: 'Tanpa Harga', k: 2, kg: 100, rp: 0, berat: 50, sumber: null, pakai: null, hari: null }, { merk: 'Ada Harga', k: 1, kg: 50, rp: 700000, berat: 50, sumber: { pemasok: 'X', harga: 14000, tanggal: '2026-09-01' }, pakai: { pemasok: 'X', harga: 14000, tanggal: '2026-09-01', kode: '' }, hari: 4 }, { merk: 'Tanpa Harga B', k: 1, kg: 50, rp: 0, berat: 50, sumber: null, pakai: null, hari: null }]);
  ok('7 Okt merek TANPA harga beli → tiap merek baris sendiri (tidak digabung walau sama-sama tanpa harga) bertanda "harga belum tercatat", paling akhir', kosongH.length === 3 && !kosongH[1].adaHarga && !kosongH[2].adaHarga && kosongH[1].teks === '• Tanpa Harga — 2 karung × 50 kg · harga belum tercatat' && kosongH[2].teks === '• Tanpa Harga B — 1 karung × 50 kg · harga belum tercatat' && kosongH[0].label === 'beras Rp14.000/kg', J(kosongH.map(function (g) { return g.teks; })));
  var TKg = susunTruk(H, 'RODA CONTOH'); ok('7 Okt truk: potongan bak = baris harga (4, urutan sama dengan pesanan); muatan 3.000 → baris IR64 550 kg cukup berlabel jumlah karung', J(TKg.bak.filter(function (k) { return k.kelas !== 'kosongbak'; }).map(function (k) { return k.merk; })) === J(R.g.map(function (g) { return g.kunci; })) && TKg.bak.some(function (k) { return k.merk === '50|14500|IR64' && k.t === '11'; }), J(TKg.bak));
  // − / + / centang satu baris harga: karungnya dibagi ke merek di dalamnya (laju & sisa tetap per merek)
  var up = ubahKelompok(H, 'RODA CONTOH', '50|14500|IR64', 1, o), dn = ubahKelompok(H, 'RODA CONTOH', '50|14500|IR64', -1, o);
  ok('7 Okt + di baris harga → merek yang paling cepat habis sesudah pesanan (Apex, ada laju) jadi 9; − → dari merek yang paling lama cukup (TH · House tanpa laju) jadi 2', up['IR64 Apex'].k === 9 && up['TH · House'].k === 3 && dn['TH · House'].k === 2 && dn['IR64 Apex'].k === 8, J([up, dn]));
  var kt = ketukKelompok(H, 'RODA CONTOH', '50|14500|IR64', o); var kt0 = tulisPesan(kt, 'SB · Royal', 'RODA CONTOH', 0); var kt2 = ketukKelompok(hitungBelanja(kt0, KINI), 'RODA CONTOH', '50|14500|IR42', kt0);
  ok('7 Okt centang baris harga berisi → semua mereknya dikosongkan; baris kosong tanpa saran → satu karung', !kt['IR64 Apex'] && !kt['TH · House'] && kt['SB · Royal'].k === 2 && kt2['SB · Royal'].k === 1, J([kt, kt2]));
  pasok('batchMasuk', bAsli); pasok('produksiKemasan', prAsli); pasok('pengaturan', pgAsli);
})();
// ==================== tinjauan E1 (7 Okt) · PERLU & SARAN per BARIS HARGA dari stok & laju GABUNGAN; arsip; stok 0; merek lalu; umur harga; baris hampir kembar ====================
(function () {
  var bAsli = cacheMentah('batch').slice(), jAsli = cacheMentah('penjualan').slice(), pgAsli = cacheMentah('pengaturan').slice(), atAsli = cacheMentah('aturan').slice();
  var brs = function (merk, kg, h, ubah) { return Object.assign({ id: merk, merk: merk, satuan: 'karung', beratKarung: 50, jumlahKarung: kg / 50, totalKg: kg, hargaPerKg: h, subtotalHarga: kg * h }, ubah || {}); };
  var jl = function (id, merk, kg) { return { koleksi: 'penjualan', data: { id: id, tanggal: '2026-09-15', jam: '09:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: merk, totalKg: kg, hargaTotal: kg * 16000, hppTotalSaatJual: kg * 15000, beratKarungAcuan: 50, jumlahKarung: kg / 50 } }; };
  var peta = Object.assign({}, ((cacheMentah('pengaturan').find(function (d) { return d.id === 'jenisBeras'; }) || {}).peta) || {});
  ['Merek Kosong', 'Merek Penuh', 'Gabung Lain', 'Nol Laku', 'Arsip Contoh', 'Dua A', 'Dua B', 'Dua Diam', 'Lama Apex', 'Jauh Apex', 'Baru Apex', 'Tebak Apex', 'Asc Lama', 'Asc Satu', 'Asc Dua', 'Bahan campuran Uji'].forEach(function (m) { peta[m] = 'IR64'; }); peta['Ketan Kelas'] = 'Ketan Putih';
  terapkanKeCache([
    // GABUNG: Merek Kosong (50 kg, laku 28,6/hari → habis 1 hari) seharga Merek Penuh (986 kg, laku 1/hari) → bersama 1.036 kg ÷ 29,6 = 35 hari: TIDAK perlu
    { koleksi: 'batchMasuk', data: { id: 'g1', tanggal: '2026-09-10', jam: '08:00', pemasok: 'GABUNG CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [brs('Merek Kosong', 450, 15000), brs('Merek Penuh', 1000, 15000), brs('Gabung Lain', 300, 15500), brs('Nol Laku', 100, 16000), brs('Arsip Contoh', 100, 15000)] } },
    // DUA: Dua A (80 kg, 30/hari) + Dua B (50 kg, 17,9/hari) + Dua Diam (100 kg, tak laku) seharga → bersama 230 kg ÷ 47,9 = 4 hari: PERLU, saran ⌈(670 − 230) / 50⌉ = 9
    { koleksi: 'batchMasuk', data: { id: 'd1', tanggal: '2026-09-10', jam: '08:00', pemasok: 'DUA CONTOH', caraBayar: 'utang', biayaBongkar: 0, merkList: [brs('Dua A', 500, 15200), brs('Dua B', 300, 15200), brs('Dua Diam', 100, 15200)] } },
    // KEMBAR: kelas mutu dipetakan owner; kiriman terbaru kelas IR64 Apex 12 Sep @15.100 (Baru Apex); IR64 Ascent 12 Sep DUA harga (15.300 & 15.400) = tidak ditebak
    { koleksi: 'batchMasuk', data: { id: 'k1', tanggal: '2026-09-08', jam: '08:00', pemasok: 'KEMBAR CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [brs('Lama Apex', 200, 15000), brs('Jauh Apex', 200, 14000), brs('Tebak Apex', 100, 15050), brs('Asc Lama', 100, 15350),
      brs('Ketan Kelas', 100, 20000, { merkPemasok: 'KK' }), brs('Bahan campuran Uji', 100, 13000)] } },
    { koleksi: 'batchMasuk', data: { id: 'k2', tanggal: '2026-09-12', jam: '08:00', pemasok: 'KEMBAR CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [brs('Baru Apex', 200, 15100), brs('Asc Satu', 100, 15300), brs('Asc Dua', 100, 15400)] } },
    jl('e1', 'Merek Kosong', 400), jl('e2', 'Merek Penuh', 14), jl('e3', 'Gabung Lain', 200), jl('e4', 'Nol Laku', 100), jl('e5', 'Arsip Contoh', 100), jl('e6', 'Dua A', 420), jl('e7', 'Dua B', 250),
    { koleksi: 'pengaturan', data: { id: 'jenisBeras', peta: peta } },
    { koleksi: 'aturanToko', data: { id: 'produkArsip', daftar: [{ kunci: 'K:Arsip Contoh', nama: 'Arsip Contoh', pada: '2026-09-18' }] } },
    { koleksi: 'aturanToko', data: { id: 'kelasMerek', peta: { 'Lama Apex': 'IR64 Apex', 'Jauh Apex': 'IR64 Apex', 'Baru Apex': 'IR64 Apex', 'Tebak Apex': 'IR64 Apex', 'Asc Lama': 'IR64 Ascent', 'Asc Satu': 'IR64 Ascent', 'Asc Dua': 'IR64 Ascent' },
      asal: { 'Lama Apex': 'owner', 'Jauh Apex': 'owner', 'Baru Apex': 'owner', 'Tebak Apex': 'tebakan', 'Asc Lama': 'owner', 'Asc Satu': 'owner', 'Asc Dua': 'owner' }, kelasSendiri: ['Ketan Kelas'] } }]);
  terapkanKeCache(susunAturBelanja({ ambangHari: '7', targetHari: '14', muatanKg: '200' }, W).dokumen);
  var H = hitungBelanja({}, KINI); var b = function (m) { return H.baris.find(function (x) { return x.merk === m; }) || null; }; var R = function (p) { return H.perP.find(function (r) { return r.pemasok === p; }); };
  var gG = R('GABUNG CONTOH').gMilik.find(function (g) { return g.kunci === '50|15000|IR64'; });
  ok('E1 GABUNGAN: Merek Kosong habis 1 hari tapi seharga Merek Penuh (986 kg) → baris IR64 Rp15.000 bersama 1.036 kg ±35 hari: TIDAK perlu, saran 0 (dulu 7 karung); Merek Kosong masuk "ada yang seharga", kalimatnya menyebut gabungannya',
    b('Merek Kosong').hari === 1 && b('Merek Kosong').perlu === false && b('Merek Kosong').saranK === 0 && b('Merek Penuh').saranK === 0 && gG && gG.perlu === false && gG.saranK === 0 && /±35 hari lagi/.test(gG.hariTeks)
    && /masih cukup bersama/.test(b('Merek Kosong').tutup) && /seharga Merek Penuh \(GABUNG CONTOH Rp15\.000\/kg\): bersama 1\.036 kg/.test(b('Merek Kosong').gabungTeks)
    && H.kelompok.some(function (k) { return /ada yang seharga/.test(k.judul) && k.isi.some(function (x) { return x.merk === 'Merek Kosong'; }); }) && !H.kelompok.some(function (k) { return k.judul === 'Habis dalam 7 hari' && k.isi.some(function (x) { return x.merk === 'Merek Kosong'; }); })
    && !H.kertas.some(function (r) { return r.g.some(function (g) { return g.kunci === '50|15000|IR64' && r.pemasok === 'GABUNG CONTOH'; }); }), J([b('Merek Kosong'), gG && [gG.perlu, gG.saranK, gG.hariTeks]]));
  var gD = R('DUA CONTOH').gMilik.find(function (g) { return g.kunci === '50|15200|IR64'; });
  ok('E1 GABUNGAN perlu: Dua A + Dua B + Dua Diam seharga → bersama 230 kg ±4 hari, saran ⌈(47,9 × 14 − 230) / 50⌉ = 9 karung (bukan 7 + 4 per merek), dibagi ke yang paling cepat habis: Dua A 6 · Dua B 3 · Dua Diam (tak laku) 0',
    gD && gD.perlu === true && gD.saranK === 9 && b('Dua A').saranK === 6 && b('Dua B').saranK === 3 && b('Dua Diam').saranK === 0 && b('Dua A').perlu && b('Dua B').perlu && !b('Dua Diam').perlu, J(gD && gD.merk.map(function (x) { return [x.merk, x.saranK, x.perlu, x.hari]; })));
  var kD = H.kertas.find(function (r) { return r.pemasok === 'DUA CONTOH'; });
  ok('E1 DAFTAR: baris harga yang perlu tampil LENGKAP — Dua Diam (tidak perlu, 100 kg) ikut di lembar sebagai merek seharga, bukan di "Belum perlu — boleh ditambah"',
    kD && kD.g.length === 1 && kD.isi.some(function (x) { return x.merk === 'Dua Diam'; }) && !H.lainnya.some(function (x) { return x.merk === 'Dua Diam'; }), J(kD && kD.isi.map(function (x) { return x.merk; })));
  var kk = function (o, m) { return (o[m] || { k: 0 }).k; };   // karung satu merek di peta pesanan (0 bila tidak ada) — kontrol tidak boleh berbunyi karena jsc jatuh
  var PS = pakaiSaran(H, {}, 'DUA CONTOH'); var PSall = pakaiSaran(H, {}, ''); var KT = ketukKelompok(H, 'DUA CONTOH', '50|15200|IR64', {});
  ok('E1 "Pakai saran" (per pemasok / semua) & centang baris harga = saran GABUNGAN dibagi ke merek (Dua A 6 · Dua B 3 = 9 karung, satu baris harga); merek tanpa bagian tidak ditulis',
    PS.baris === 1 && PS.karung === 9 && kk(PS.pesan, 'Dua A') === 6 && kk(PS.pesan, 'Dua B') === 3 && !PS.pesan['Dua Diam'] && !PS.pesan['Merek Kosong'] && J(KT) === J(PS.pesan) && kk(PSall.pesan, 'Dua A') === 6 && !PSall.pesan['Merek Kosong'] && /^Pakai saran: \d+ baris harga · \d+ karung$/.test(H.saranSemuaTeks), J([PS, KT]));
  var WD = susunPesanan(PS.pesan, 'DUA CONTOH', W, false);
  ok('E1 pesanan WA: satu baris "• IR64 Rp15.200/kg — 9 karung × 50 kg (merek lalu: Dua A / Dua B / Dua Diam)" — merek lalu dari SEMUA merek seharga pemasok itu, bukan hanya yang dipesan',
    WD.baris.indexOf('• IR64 Rp15.200/kg — 9 karung × 50 kg (merek lalu: Dua A / Dua B / Dua Diam)') >= 0, J(WD.baris));
  ok('E1 stok 0 yang masih laku = "habis hari ini" (dulu "belum ada gerak — tidak ditebak"): Nol Laku perlu, saran 2 karung; tanpa laju tetap tidak ditebak',
    b('Nol Laku').hari === 0 && b('Nol Laku').perlu && b('Nol Laku').saranK === 2 && /habis hari ini/.test(b('Nol Laku').sisaTeks) && hariHabis(0, 0) === null && hariHabis(-5, 3) === 0, J(b('Nol Laku')));
  ok('E1 nama yang DIARSIPKAN tidak ikut belanja (tidak disarankan walau stoknya habis & masih laku)', !b('Arsip Contoh') && !H.D.merk.some(function (x) { return x.merk === 'Arsip Contoh'; }));
  var PF = penuhiTruk(H, 'GABUNG CONTOH', {});
  ok('E1 penuhi truk per BARIS HARGA: 4 karung (muatan 200 kg) ke baris yang stok gabungannya paling cepat habis (Nol Laku, Gabung Lain) — Merek Kosong (habis 1 hari, tapi barisnya ±35 hari) tidak menerima',
    PF.tambahan === 4 && !PF.pesan['Merek Kosong'] && !PF.pesan['Merek Penuh'] && kk(PF.pesan, 'Nol Laku') + kk(PF.pesan, 'Gabung Lain') === 4, J(PF));
  // KEMBAR: umur harga, merek lalu, baris hampir kembar
  var o = {}; ['Lama Apex', 'Baru Apex', 'Jauh Apex', 'Tebak Apex', 'Asc Lama', 'Asc Satu', 'Asc Dua', 'Ketan Kelas', 'Bahan campuran Uji'].forEach(function (m) { o = tulisPesan(o, m, 'KEMBAR CONTOH', 1); });
  var HK = hitungBelanja(o, KINI); var bk = function (m) { return HK.baris.find(function (x) { return x.merk === m; }); }; var WK = susunPesanan(o, 'KEMBAR CONTOH', W, false);
  ok('E1 baris hampir kembar: Lama Apex (15.000, 8 Sep) sekelas IR64 Apex dengan kiriman terbaru Baru Apex (15.100, 12 Sep), beda 0,7 % ≤ batas owner 5 % → ikut 15.100, SATU baris "• IR64 Rp15.100/kg — 2 karung × 50 kg (merek lalu: Baru Apex / Lama Apex)"; rp & dokumen pesanan memakai 15.100; harga lamanya tetap disebut',
    bk('Lama Apex').pakai.harga === 15100 && bk('Lama Apex').pakai.lalu.harga === 15000 && bk('Lama Apex').rp === 50 * 15100 && WK.baris.indexOf('• IR64 Rp15.100/kg — 2 karung × 50 kg (merek lalu: Baru Apex / Lama Apex)') >= 0
    && WK.dokumen[0].data.baris.find(function (x) { return x.merk === 'Lama Apex'; }).hargaPerKg === 15100 && /Lama Apex terakhir Rp15\.000 \(8 Sep\)/.test(HK.perP.find(function (r) { return r.pemasok === 'KEMBAR CONTOH'; }).g.find(function (g) { return g.harga === 15100; }).hargaTeks), J([bk('Lama Apex').pakai, WK.baris]));
  ok('E1 TIDAK dirapikan bila tidak aman: Jauh Apex (beda 7,9 % > batas owner), Tebak Apex (kelasnya tebakan), Asc Lama (kiriman terbaru kelasnya punya DUA harga) → harganya sendiri, ditandai umurnya',
    bk('Jauh Apex').pakai.harga === 14000 && !bk('Jauh Apex').pakai.lalu && bk('Tebak Apex').pakai.harga === 15050 && bk('Asc Lama').pakai.harga === 15350
    && WK.baris.indexOf('• IR64 Rp14.000/kg (harga 8 Sep) — 1 karung × 50 kg (merek lalu: Jauh Apex)') >= 0 && WK.baris.indexOf('• IR64 Rp15.050/kg (harga 8 Sep) — 1 karung × 50 kg (merek lalu: Tebak Apex)') >= 0 && WK.baris.indexOf('• IR64 Rp15.350/kg (harga 8 Sep) — 1 karung × 50 kg (merek lalu: Asc Lama)') >= 0, J(WK.baris));
  ok('E1 umur harga: harga dari kiriman TERAKHIR pemasok itu (12 Sep) tanpa umur; merek lalu = merek pemasok yang tercatat (kelas sendiri Ketan Kelas → "KK"); nama buatan toko (bahan campuran) tidak disebut',
    WK.baris.indexOf('• IR64 Rp15.300/kg — 1 karung × 50 kg (merek lalu: Asc Satu)') >= 0 && WK.baris.indexOf('• Ketan Putih Rp20.000/kg (harga 8 Sep) — 1 karung × 50 kg (merek lalu: KK)') >= 0 && WK.baris.indexOf('• IR64 Rp13.000/kg (harga 8 Sep) — 1 karung × 50 kg') >= 0, J(WK.baris));
  pasok('batchMasuk', bAsli); pasok('penjualan', jAsli); pasok('pengaturan', pgAsli); pasok('aturanToko', atAsli);
})();

// ==================== HET BERAS (paket brief 9 Okt, butir 8) — ANGKA CONTOH ====================
// Katalog kembali ke KOTAK: 8 baris; satuan pemetaan = 3 WADAH (IR64 Apex, Angsa, Pandan Wangi — kotak pasir memakai nama wadah ini) + Kembang (merek tanpa kelas).
// Per kg menurut katalog: Angsa L 12.500 ÷ 0,82 = 15.243,9 · Angsa K50 700.000 ÷ 50 = 14.000 · Angsa S 13.800 · Apex S 14.100 · Apex L belum ada harga
// · Kembang K5 75.000 ÷ 5 = 15.000 · Pandan L 13.000 ÷ 0,82 = 15.853,7 · Pandan S belum ada harga. HET bawaan Zona I: medium 13.500, premium 14.900.
(function () {
  Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
  var S = hgSemua(KINI); var A = hetAtur(); var HT = hetKatalog(S); var hb = function (H, k) { return H.per[k]; };
  var tutup = function (H) { return H.hit.atas + H.hit.dalam + H.hit.belum + H.hit.bukan + H.hit.kosong === H.total && H.total === S.baris.length; };
  ok('HET bawaan tanpa dokumen: Zona I · medium 13.500 · premium 14.900 · sumber Kepbadan 299/2025, disebut angka bawaan yang bisa diubah di Atur',
    A.zona === 'Zona I' && A.medium === 13500 && A.premium === 14900 && A.sumber === 'Kepbadan 299/2025' && !A.angkaOwner && /dokumen owner: Kepbadan 299\/2025, Zona I — bisa diubah di Atur/.test(A.sumberTeks), J(A));
  ok('HET BELUM DIPETAKAN: tidak ada peringatan sama sekali; 8 harga "belum dipetakan" (bukan aman); judul "belum dipetakan: 4 kelas/merek"; satuan = 3 wadah (urutan wadah) + Kembang (merek tanpa kelas)',
    HT.keadaan === 'belum' && HT.nAtas === 0 && HT.hit.belum === 8 && !HT.baris.some(function (x) { return x.status === 'atas' || x.status === 'dalam'; }) && /^belum dipetakan: 4 kelas\/merek/.test(HT.judul) && !/aman|tidak ada harga di atas/.test(HT.judul)
    && HT.units.map(function (u) { return u.unit + ':' + u.jenis; }).join() === 'IR64 Apex:wadah,Angsa:wadah,Pandan Wangi:wadah,Kembang:merek' && tutup(HT), J([HT.judul, HT.hit, HT.units]));
  var R = susunPetaHet('Angsa', 'premium', W);
  ok('peta: Angsa → premium = dokumen aturanToko/het {peta: {Angsa: premium}} TANPA angka (yang belum diatur owner tetap bawaan)', !R.tolak && R.dokumen.length === 1 && R.dokumen[0].koleksi === 'aturanToko' && R.dokumen[0].data.id === 'het' && J(R.dokumen[0].data.peta) === '{"Angsa":"premium"}' && !('medium' in R.dokumen[0].data) && !('premium' in R.dokumen[0].data), J(R));
  terapkanKeCache(R.dokumen); HT = hetKatalog(S);
  ok('Angsa premium: LITERAN 12.500/L ÷ 0,82 = 15.243,9/kg > 14.900 → "di atas HET Rp14.900/kg (+Rp344)"; karung 50 kg 700.000 ÷ 50 = 14.000 sama/di bawah; per kg 13.800 di bawah; hetAtur tetap bawaan',
    hb(HT, 'Angsa|L').status === 'atas' && Math.abs(hb(HT, 'Angsa|L').perKg - 12500 / 0.82) < 1e-9 && hb(HT, 'Angsa|L').teks === 'di atas HET Rp14.900/kg (+Rp344)' && hb(HT, 'Angsa|K50').status === 'dalam' && hb(HT, 'Angsa|K50').perKg === 14000 && /di bawah HET premium Rp14\.900\/kg \(−Rp900\)/.test(hb(HT, 'Angsa|K50').teks)
    && hb(HT, 'Angsa|S').status === 'dalam' && /Rp12\.500\/L = Rp15\.244\/kg/.test(hb(HT, 'Angsa|L').hargaTeks) && !hetAtur().angkaOwner, J([hb(HT, 'Angsa|L'), hb(HT, 'Angsa|K50')]));
  ok('sebagian dipetakan: "1 harga di atas HET · belum dipetakan: 3 kelas/merek" (tidak pernah "aman"); 1 atas + 2 sama/di bawah + 5 belum = 8 (menutup)',
    HT.keadaan === 'sebagian' && HT.nAtas === 1 && HT.judul === '1 harga di atas HET · belum dipetakan: 3 kelas/merek' && HT.hit.dalam === 2 && HT.hit.belum === 5 && tutup(HT) && /^Dari 8 harga: 1 di atas HET · 2 sama\/di bawah HET · 5 belum dipetakan\.$/.test(HT.rincian), J([HT.judul, HT.hit, HT.rincian]));
  terapkanKeCache(susunPetaHet('Kembang', 'medium', W).dokumen); terapkanKeCache(susunPetaHet('IR64 Apex', 'premium', W).dokumen); terapkanKeCache(susunPetaHet('Pandan Wangi', 'bukan', W).dokumen); HT = hetKatalog(S);
  ok('KEMASAN Kembang 5 kg 75.000 ÷ 5 = 15.000/kg > medium 13.500 → +Rp1.500; Apex per kg 14.100 di bawah premium, Apex literan BELUM ADA HARGA (bukan aman, bukan atas); Pandan "bukan beras HET" → tidak dibandingkan walau 15.854/kg',
    hb(HT, 'Kembang|K5').status === 'atas' && hb(HT, 'Kembang|K5').perKg === 15000 && hb(HT, 'Kembang|K5').teks === 'di atas HET Rp13.500/kg (+Rp1.500)' && hb(HT, 'IR64 Apex|S').status === 'dalam' && hb(HT, 'IR64 Apex|L').status === 'kosong'
    && hb(HT, 'Pandan Wangi|L').status === 'bukan' && hb(HT, 'Pandan Wangi|S').status === 'bukan', J([hb(HT, 'Kembang|K5'), hb(HT, 'IR64 Apex|L'), hb(HT, 'Pandan Wangi|L')]));
  ok('semua dipetakan: "2 harga di atas HET", urut selisih terbesar (Kembang lalu Angsa literan); 2 atas + 3 sama/di bawah + 2 bukan + 1 belum ada harga = 8; tidak ada sisa "belum dipetakan"',
    HT.keadaan === 'lengkap' && HT.judul === '2 harga di atas HET' && HT.atas.map(function (x) { return x.k; }).join() === 'Kembang|K5,Angsa|L' && HT.hit.dalam === 3 && HT.hit.bukan === 2 && HT.hit.kosong === 1 && HT.hit.belum === 0 && HT.unitBelum.length === 0 && tutup(HT), J([HT.judul, HT.hit]));
  // harga TEPAT = HET tidak awas; satu rupiah lebih = awas; pecahan di bawah Rp1 tetap disebut
  terapkanKeCache(susunUbah('Angsa|S', '14.900', 'jual', W).dokumen); S = hgSemua(KINI); HT = hetKatalog(S);
  ok('harga TEPAT HET (draf Angsa per kg 14.900): sama/di bawah, "tepat HET premium Rp14.900/kg" — tidak awas; literan 12.218/L ÷ 0,82 = 14.900 juga tepat', hb(HT, 'Angsa|S').status === 'dalam' && hb(HT, 'Angsa|S').teks === 'tepat HET premium Rp14.900/kg' && hetNilai(12218 / 0.82, 'premium', hetAtur()).status === 'dalam' && hetNilai(12219 / 0.82, 'premium', hetAtur()).status === 'atas', J(hb(HT, 'Angsa|S')));
  ok('satu rupiah di atas HET = awas (+Rp1); kemasan 5 kg 74.502 = 14.900,4/kg → di atas, selisih disebut "+Rp0,4" (tidak dibulatkan jadi Rp0)', hetNilai(14901, 'premium', hetAtur()).teks === 'di atas HET Rp14.900/kg (+Rp1)' && hetNilai(74502 / 5, 'premium', hetAtur()).status === 'atas' && hetNilai(74502 / 5, 'premium', hetAtur()).lebihTeks === 'Rp0,4', J(hetNilai(74502 / 5, 'premium', hetAtur())));
  // sebelum terbit: draf dinilai dengan harga BARUNYA; peringatan tidak memblokir; harga kasir (terbit) dinilai terpisah untuk dasbor
  terapkanKeCache(susunUbah('Angsa|S', '15.000', 'jual', W).dokumen); S = hgSemua(KINI); var HD = hetDraf(S);
  ok('sebelum terbit: draf Angsa per kg 15.000 → "di atas HET Rp14.900/kg (+Rp100)"; teks "1 harga draf di atas HET Zona I — boleh terbit; owner yang memutuskan"; terbit TIDAK ditahan (ketukan pertama langsung jadi)',
    HD.daftar.length === 1 && HD.nAtas === 1 && HD.per['Angsa|S'].teks === 'di atas HET Rp14.900/kg (+Rp100)' && /^1 harga draf di atas HET Zona I — boleh terbit; owner yang memutuskan\.$/.test(HD.teks) && !susunTerbit(W, false).tolak, J(HD));
  var HK = hetKatalog(S, 'terbit');
  ok('harga KASIR (terbit, untuk dasbor) tetap 13.800 → sama/di bawah; harga tampil (draf) 15.000 → di atas; hetHargaKasir(kini) = hetKatalog(hgSemua(kini), "terbit")', HK.per['Angsa|S'].status === 'dalam' && HK.per['Angsa|S'].n === 13800 && hetKatalog(S).per['Angsa|S'].status === 'atas' && J(hetHargaKasir(KINI).hit) === J(HK.hit) && HK.pakai === 'terbit' && /yang dipakai kasir/.test(HK.rincian), J([HK.per['Angsa|S'], HK.hit]));
  var b = cariBaris(S, 'Angsa|S');
  ok('lembar ubah: harga yang DIKETIK dinilai terhadap HET kelasnya (15.500 → +Rp600; 14.000 → di bawah); kelas/merek belum dipetakan → "belum"', hetSatuHarga(b, 15500).teks === 'di atas HET Rp14.900/kg (+Rp600)' && hetSatuHarga(b, 14000).status === 'dalam'
    && (function () { var d = cacheMentah('aturan').find(function (x) { return x.id === 'het'; }); var p = Object.assign({}, d.peta); delete p.Angsa; terapkanKeCache([{ koleksi: 'aturanToko', data: Object.assign({}, d, { peta: p }) }]); var r = hetSatuHarga(b, 15500).status; terapkanKeCache([{ koleksi: 'aturanToko', data: d }]); return r === 'belum'; })(), J(hetSatuHarga(b, 15500)));
  // UBAH SETELAN HET → hasil ikut berubah
  var AT = susunAturHet({ zona: 'Zona II', medium: '13.600', premium: '15.300', sumber: 'Keputusan contoh' }, W);
  ok('atur HET: dokumen aturanToko/het {zona Zona II, medium 13.600, premium 15.300, sumber} + peta yang ada IKUT utuh', !AT.tolak && AT.dokumen[0].data.id === 'het' && AT.dokumen[0].data.medium === 13600 && AT.dokumen[0].data.premium === 15300 && AT.dokumen[0].data.zona === 'Zona II' && AT.dokumen[0].data.sumber === 'Keputusan contoh' && J(AT.dokumen[0].data.peta) === J({ Angsa: 'premium', Kembang: 'medium', 'IR64 Apex': 'premium', 'Pandan Wangi': 'bukan' }), J(AT));
  terapkanKeCache(AT.dokumen); HT = hetKatalog(S); HD = hetDraf(S);
  ok('sesudah setelan berubah HASIL IKUT: Angsa literan 15.243,9 kini di BAWAH premium 15.300; draf Angsa 15.000 tidak lagi di atas; Kembang 15.000 vs medium 13.600 → +Rp1.400; layar menyebut "angka owner … Keputusan contoh · Zona II"',
    hb(HT, 'Angsa|L').status === 'dalam' && HD.nAtas === 0 && hb(HT, 'Kembang|K5').teks === 'di atas HET Rp13.600/kg (+Rp1.400)' && HT.nAtas === 1 && /angka owner .*sumber: Keputusan contoh · Zona II/.test(hetAtur().sumberTeks), J([hb(HT, 'Angsa|L'), hb(HT, 'Kembang|K5'), hetAtur().sumberTeks]));
  var RP2 = susunPetaHet('Kembang', 'premium', W);
  ok('peta sesudah angka owner: angka owner ikut tertulis apa adanya (13.600 / 15.300 / Zona II), bukan bawaan', RP2.dokumen[0].data.medium === 13600 && RP2.dokumen[0].data.premium === 15300 && RP2.dokumen[0].data.zona === 'Zona II' && RP2.dokumen[0].data.peta.Kembang === 'premium', J(RP2));
  ok('atur HET ditolak: premium < medium ("tertukar?"), medium 0, huruf; kolom kosong = nilai berlaku', /tertukar/.test(susunAturHet({ medium: '15.000', premium: '14.000' }, W).tolak || '') && /1–100\.000/.test(susunAturHet({ medium: '0' }, W).tolak || '') && /1–100\.000/.test(susunAturHet({ premium: 'abc' }, W).tolak || '')
    && susunAturHet({}, W).dokumen[0].data.medium === 13600, J(susunAturHet({ medium: '15.000', premium: '14.000' }, W)));
  ok('peta ditolak: nama di luar katalog, pilihan yang sama lagi, pilihan tak dikenal; lepas ("") = kembali belum dipetakan', /tidak ada di katalog/.test(susunPetaHet('Merek Asing', 'premium', W).tolak || '') && /sudah premium/.test(susunPetaHet('Angsa', 'premium', W).tolak || '') && /tidak dikenal/.test(susunPetaHet('Angsa', 'mahal', W).tolak || '')
    && (function () { var r = susunPetaHet('Angsa', '', W); return !r.tolak && !('Angsa' in r.dokumen[0].data.peta) && /kembali belum dipetakan/.test(r.patch.kabar); })(), J(susunPetaHet('Angsa', '', W)));
  // KELAS: merek berkelas (dikonfirmasi owner) dinilai dengan pemetaan kelasnya; kelas TEBAKAN tidak dipakai
  terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kelasMerek', peta: { Kembang: 'IR64 Apex' }, asal: { Kembang: 'tebakan' }, kelasSendiri: [] } }]); HT = hetKatalog(S);
  ok('kelas TEBAKAN (Kembang → IR64 Apex, belum dikonfirmasi) tidak dipakai: Kembang tetap satuan sendiri (merek), tebakannya disebut', hetUnit('Kembang').unit === 'Kembang' && hetUnit('Kembang').tebakan === 'IR64 Apex' && HT.units.some(function (u) { return u.unit === 'Kembang' && u.jenis === 'merek' && u.tebakan === 'IR64 Apex'; }), J(hetUnit('Kembang')));
  terapkanKeCache([{ koleksi: 'aturanToko', data: { id: 'kelasMerek', peta: { Kembang: 'IR64 Apex' }, asal: { Kembang: 'owner' }, kelasSendiri: [] } }]); HT = hetKatalog(S);
  ok('kelas DIKONFIRMASI owner (Kembang → IR64 Apex): Kembang 15.000/kg dinilai dengan IR64 Apex (premium 15.300) → di bawah; anggota kelas Apex memuat Kembang; pemetaan lama "Kembang" kini tidak dipakai katalog dan boleh dilepas',
    hetUnit('Kembang').unit === 'IR64 Apex' && hetUnit('Kembang').jenis === 'wadah' && hb(HT, 'Kembang|K5').unit === 'IR64 Apex' && hb(HT, 'Kembang|K5').kategori === 'premium' && hb(HT, 'Kembang|K5').status === 'dalam'
    && HT.units.find(function (u) { return u.unit === 'IR64 Apex'; }).anggota.indexOf('Kembang') >= 0 && J(HT.tidakDipakai) === '["Kembang"]' && !susunPetaHet('Kembang', '', W).tolak && !!susunPetaHet('Kembang', 'medium', W).tolak, J([hb(HT, 'Kembang|K5'), HT.tidakDipakai]));
})();
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""
BATCH_BARU = r"""
function batchBaru(id, tgl, jam, pemasok) { return { id: id, tanggal: tgl, jam: jam, pemasok: pemasok, caraBayar: 'utang', biayaBongkar: 0, merkList: [{ id: id + '0', merk: 'IR64 Apex', satuan: 'karung', beratKarung: 50, jumlahKarung: 8, totalKg: 400, hargaPerKg: 14500, subtotalHarga: 5800000 }] }; }
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var KINI = new Date(Date.now()); var S = hgSemua(KINI); var salah = [];
// putaran 27: harga liter yang bukan wadah & bukan literan langsung tidak punya baris katalog — tampil di tab Literan sebagai "tidak dipakai"
var LTX = hgLiteran(S); var nLtTidak = 0;
// putaran 27 (Bagian 3): nama yang DIARSIPKAN (aturanToko/produkArsip) hilang dari katalog tapi harganya tetap tersimpan — dihitung terpisah, bukan "tidak cocok"
var ARS = arPeta(); var nArsip = 0; var namaArsip = [];
// tiap dokumen katalog = satu baris dengan angka yang sama
var nDok = 0; [['katalogHargaKarung', 'S', 'hargaPerKg'], ['katalogHargaLiteran', 'L', 'hargaPerLiter'], ['katalogHargaKemasan', 'K', 'hargaPerUnit']].forEach(function (x) { (CAD[x[0]] || []).forEach(function (d) { nDok += 1; var sid = x[1] === 'K' ? 'K' + Number(d.ukuran) : x[1]; var b = cariBaris(S, kunciHarga(d.merk, sid)); if (!b && sid === 'L' && LTX.tidakDipakai.some(function (t) { return t.merk === d.merk; })) nLtTidak += 1; else if (!b && (ARS['K:' + d.merk] || ARS['M:' + d.merk + '|' + Number(d.ukuran)])) { nArsip += 1; if (namaArsip.indexOf(d.merk) < 0) namaArsip.push(d.merk); } else if (!b) salah.push('katalog tanpa baris: ' + d.merk + ' ' + sid); else if (b.lamaN !== Math.round(Number(d[x[2]]) || 0)) salah.push('angka beda: ' + b.k); }); });
var B = susunBon(KINI); var up = hitungUtangPemasok(); var totalMesin = up.reduce(function (a, x) { return a + x.totalUtang; }, 0), nBonMesin = up.reduce(function (a, x) { return a + x.bon.length; }, 0);
if (B.total !== totalMesin || B.nBon !== nBonMesin) salah.push('bon ≠ mesin: ' + B.total + ' vs ' + totalMesin);
var D = daftarBelanja(KINI); var stokK = hitungStokKarungPerMerk(); var laju = hitungLajuPakai().kgMerk || {};
D.merk.forEach(function (m) { var h = hariHabis((stokK[m.merk] || {}).sisaKg || 0, laju[m.merk] || 0); if (h !== m.hari) salah.push('hari beda: ' + m.merk); });
// owner 7 Okt: pesanan per HARGA — di data toko, dua daftar (saran semua; tiap merek bersumber ≥ 1 karung): tiap pemasok Σ karung/kg/rp kelompok = Σ per merek,
// tiap merek di tepat satu kelompok yang harganya = harga barisnya, baris "Jumlah" pesan WA sama dengan jumlah per merek, satu baris WA per kelompok
var J = JSON.stringify; var kel = { merek: 0, baris: 0, pemasok: 0 }; var WB = { tanggal: '2026-09-22', jam: '10:00', kini: KINI.toISOString(), idUnik: function () { return 1; } };
(function () { var H0 = hitungBelanja({}, KINI); var o1 = {}, o2 = {};
  H0.perluSemua.forEach(function (b) { o1 = tulisPesan(o1, b.merk, b.termurah.pemasok, b.saranK); });
  H0.baris.forEach(function (b) { if (b.termurah && !b.dipesan) o2 = tulisPesan(o2, b.merk, b.termurah.pemasok, Math.max(1, b.saranK)); });
  [o1, o2].forEach(function (pes, ke) { var H = hitungBelanja(pes, KINI); H.perP.forEach(function (r) { if (!r.karung) return;
    var gk = r.g.reduce(function (a, g) { return a + g.k; }, 0), gkg = r.g.reduce(function (a, g) { return a + g.kg; }, 0), grp = r.g.reduce(function (a, g) { return a + g.rp; }, 0);
    if (gk !== r.karung || Math.abs(gkg - r.kg) > 0.001 || Math.abs(grp - r.rp) > 0.5) salah.push('kelompok harga ≠ per merek: ' + r.pemasok);
    var nm = []; r.g.forEach(function (g) { g.merk.forEach(function (b) { nm.push(b.merk); if (g.adaHarga && (!b.pakai || b.pakai.harga !== g.harga || b.berat !== g.berat || (b.pakai.lalu ? !(b.pakai.tanggal > b.pakai.lalu.tanggal) : b.pakai.harga !== b.sumber.harga))) salah.push('harga/berat campur di kelompok: ' + b.merk); }); });
    if (J(nm.slice().sort()) !== J(r.d.map(function (b) { return b.merk; }).sort())) salah.push('merek hilang/ganda di kelompok: ' + r.pemasok);
    var P = susunPesanan(pes, r.pemasok, WB, false); if (P.tolak) { salah.push('pesanan ditolak: ' + P.tolak); return; }
    if (P.baris.filter(function (t) { return /^Jumlah /.test(t); })[0] !== 'Jumlah ' + r.karung + ' karung · ' + blKG(r.kg) || P.baris.length !== r.g.length + 3) salah.push('pesan WA: ' + r.pemasok);
    if (ke === 1) { kel.merek += r.d.length; kel.baris += r.g.length; kel.pemasok += 1; } }); }); })();
// tinjauan E1: perlu & saran per BARIS HARGA di data toko — tiap kelompok: Σ sisa merek = sisa gabungan, Σ bagian saran = saran gabungan (kecuali tak ada merek yang bisa
// menerima), perlu = hari gabungan ≤ ambang & saran > 0 & tidak ada yang dipesan; tidak ada nama arsip; merek yang stok sendirinya tipis tapi ditutup seharganya dihitung
var gab = { baris: 0, perlu: 0, tutup: [] }; var ARS2 = arPeta();
(function () { var at = D.atur; var kel = {}; D.merk.forEach(function (x) { if (ARS2['K:' + x.merk]) salah.push('nama arsip ikut belanja: ' + x.merk); if (!x.kel) { salah.push('tanpa kelompok: ' + x.merk); return; } var k = x.kel.pemasok + '|' + x.kel.kunci; (kel[k] = kel[k] || { info: x.kel, isi: [] }).isi.push(x); if (x.tutup) gab.tutup.push(x.merk); });
  Object.keys(kel).forEach(function (k) { var G = kel[k], I = G.info; gab.baris += 1; if (I.perlu) gab.perlu += 1;
    var sisa = Math.round(G.isi.reduce(function (a, x) { return a + x.sisa; }, 0) * 100) / 100, bagi = G.isi.reduce(function (a, x) { return a + x.saranK; }, 0), bisa = G.isi.some(function (x) { return x.laju > 0 && !x.dipesan; });
    if (Math.abs(sisa - I.sisa) > 0.01) salah.push('sisa gabungan ≠ Σ merek: ' + k);
    if (bisa && bagi !== I.saranK) salah.push('saran gabungan ≠ Σ bagian: ' + k);
    if (I.perlu !== (I.hari !== null && I.hari <= at.ambangHari && I.saranK > 0 && !I.dipesan)) salah.push('perlu gabungan salah: ' + k);
    G.isi.forEach(function (x) { if (x.perlu !== (I.perlu && x.saranK > 0)) salah.push('perlu merek ≠ bagiannya: ' + x.merk); }); }); })();
// kolom dokumen vs cadangan (kolom baru sistem baru disebut eksplisit)
var kenal = function (nama) { var o = {}; (CAD[nama] || []).forEach(function (d) { Object.keys(d).forEach(function (k) { o[k] = 1; }); }); return o; };
var WX = { tanggal: '2026-09-22', jam: '10:00', kini: '2026-09-22T03:00:00.000Z', idUnik: function () { return Math.random(); } };
var kU = kenal('utangPemasokMutasi'); var px = B.bon[0]; var catatan = []; var pgAsli = cacheMentah('pengaturan').slice(); var tanpaTitik = false;
if (nLtTidak) catatan.push(nLtTidak + ' harga liter tidak dipakai rak (bukan wadah, bukan literan langsung — tab Literan): ' + LTX.tidakDipakai.map(function (x) { return x.merk; }).join(', '));
if (nArsip) catatan.push(nArsip + ' harga milik nama yang diarsipkan (tanpa baris katalog, harganya tetap tersimpan): ' + namaArsip.join(', '));
if (px) { var by = susunBayar({ pemasok: px.pemasok, bonId: px.id, ketik: '1', dari: 'laci' }, WX);
  // Kas toko di cadangan bisa memang kurang dari Rp1 (mesin beku kasPada, sama persis dengan sistem lama): penjaga kas MENOLAK dengan benar → itu catatan,
  // bukan kegagalan. Kolom dokumen tetap diuji: titik kas disingkirkan SEMENTARA (kasPada = null → penjaga tidak berlaku), lalu dikembalikan.
  if (!by.dokumen && B.adaKas && B.kas < 1 && /^Uang toko cuma /.test(by.tolak || '')) { catatan.push('kas toko di cadangan ' + B.kas + ' (kasPada, titik kas ' + ((pgAsli.find(function (d) { return String(d.id) === 'titikKas'; }) || {}).tanggal || '?') + ') → bayar ditolak penjaga kas, benar; kolom diuji tanpa titik kas');
    pasok('pengaturan', pgAsli.filter(function (d) { return String(d.id) !== 'titikKas'; })); tanpaTitik = true; by = susunBayar({ pemasok: px.pemasok, bonId: px.id, ketik: '1', dari: 'laci' }, WX); }
  if (by.dokumen) Object.keys(by.dokumen[0].data).forEach(function (k) { if (!kU[k] && ['dari', 'biayaAdmin', 'adminNama'].indexOf(k) < 0) salah.push('bayar.' + k); }); else salah.push('bayar ditolak: ' + by.tolak); }
var bl = susunBonLama({ pemasok: '', nama: 'X CONTOH', tgl: '2026-07-01', ketik: '1', catatan: 'x' }, WX); if (bl.dokumen) Object.keys(bl.dokumen[0].data).forEach(function (k) { if (!kU[k]) salah.push('saldoAwal.' + k); });
// Paket F1 asap: bon lama tiap pemasok yang punya bon lama, SEANDAINYA kartunya dicentang "ikut kedatangan terakhir" (cache sementara, tidak ditulis)
B.tusukan.forEach(function (t) { var lama = t.bon.filter(function (b) { return b.jenis === 'saldoAwal'; }); if (!lama.length) return; var P = cariPemasok(t.pemasok); if (!P) return;
  var kartuF1 = { koleksi: 'pemasokCatatan', data: { id: P.kunci, nama: P.nama, kontak: P.kontak, catatan: P.catatan, orang: P.orang, tempo: P.tempo, bonLamaBergulir: true } };
  var HF1 = denganCacheSementara([kartuF1], function () { var B2 = susunBon(KINI); return { total: B2.total, bon: B2.bon.filter(function (b) { return b.pemasok === t.pemasok && b.jenis === 'saldoAwal'; }) }; });
  if (Math.abs(HF1.total - B.total) > 0.5) salah.push('F1 asap: total bon berubah ' + B.total + ' → ' + HF1.total);
  HF1.bon.forEach(function (b) { var a = lama.find(function (x) { return x.id === b.id; }) || {}; if (b.sisa !== a.sisa) salah.push('F1 asap: sisa bon lama ' + t.pemasok + ' berubah');
    catatan.push('F1 ' + t.pemasok + ' bon lama ' + (b.tanggal || 'tanpa tanggal') + ' → bergulir ' + (b.gulir || '-') + ' · jatuh ' + (b.jatuh || '-') + ' · ' + b.status + ' (sebelum: ' + a.status + (a.jatuh ? ' ' + a.jatuh : '') + ')'); }); });
  if (ambilPemasokCatatan().some(function (c) { return c.bonLamaBergulir === true; })) catatan.push('F1: ada kartu pemasok yang sudah dicentang bergulir');
var kC = kenal('pemasokCatatan'); var kr = susunKartu(px ? px.pemasok : 'X', { kontak: '0', tempo: '7' }, WX); if (kr.dokumen) Object.keys(kr.dokumen[0].data).forEach(function (k) { if (!kC[k] && ['orang', 'tempo', 'bonLamaBergulir'].indexOf(k) < 0) salah.push('kartu.' + k); });
var kH = kenal('pengeluaranHarian'); if (px && (B.adaKas === false || tanpaTitik)) { var by2 = susunBayar({ pemasok: px.pemasok, bonId: px.id, ketik: '1', dari: 'rekening', adminI: 0 }, WX); if (by2.dokumen && by2.dokumen[1]) Object.keys(by2.dokumen[1].data).forEach(function (k) { if (!kH[k] && ['dariBayarBon', 'untuk'].indexOf(k) < 0) salah.push('harian.' + k); }); }
if (tanpaTitik) pasok('pengaturan', pgAsli);
// paket brief 9 Okt (butir 8): HET — keadaan NYATA cadangan (ada dokumen aturanToko/het?) lalu pemetaan CONTOH di cache sementara (BUKAN keputusan owner):
// wadah IR64 … → premium, wadah IR42 … → medium, kelas tanpa wadah (ketan, beras merah) → bukan beras HET; sisanya dibiarkan belum dipetakan
var HT0 = hetKatalog(S); var hetAdaDok = cacheMentah('aturan').some(function (d) { return String(d.id) === 'het'; });
var hetTutup = function (H) { return H.hit.atas + H.hit.dalam + H.hit.belum + H.hit.bukan + H.hit.kosong === H.total && H.total === S.baris.length; };
if (!hetTutup(HT0)) salah.push('HET tidak menutup');
if (!hetAdaDok && (HT0.nAtas !== 0 || HT0.keadaan !== 'belum')) salah.push('HET menyala sebelum dipetakan');
var petaContoh = {}; HT0.units.forEach(function (u) { if (u.jenis === 'wadah' && /^IR64 /.test(u.unit)) petaContoh[u.unit] = 'premium'; else if (u.jenis === 'wadah' && /^IR42 /.test(u.unit)) petaContoh[u.unit] = 'medium'; else if (u.jenis === 'sendiri') petaContoh[u.unit] = 'bukan'; });
var hetC = denganCacheSementara([{ koleksi: 'aturanToko', data: { id: 'het', peta: petaContoh } }], function () { var T = hetKatalog(S), K = hetKatalog(S, 'terbit');
  if (!hetTutup(T) || !hetTutup(K)) salah.push('HET contoh tidak menutup');
  return { hit: T.hit, judul: T.judul, unitBelum: T.unitBelum.length, kasirAtas: K.nAtas, atas: T.atas.map(function (x) { return x.judul + ' ' + x.hargaTeks + ' (' + x.unit + ' ' + x.kategori + ') ' + x.teks; }) }; });
// CONTOH B (juga bukan keputusan owner): SEMUA kelas berwadah premium, kelas tanpa wadah bukan beras HET — untuk melihat seberapa peka hasilnya pada pilihan IR42
var petaB = {}; HT0.units.forEach(function (u) { if (u.jenis === 'wadah') petaB[u.unit] = 'premium'; else if (u.jenis === 'sendiri') petaB[u.unit] = 'bukan'; });
var hetB = denganCacheSementara([{ koleksi: 'aturanToko', data: { id: 'het', peta: petaB } }], function () { var T = hetKatalog(S); return { atas: T.nAtas, kasirAtas: hetKatalog(S, 'terbit').nAtas, unitBelum: T.unitBelum.length }; });
var hetAsap = { dok: hetAdaDok, keadaan: HT0.keadaan, nAtas0: HT0.nAtas, unit: HT0.units.length, unitBelum0: HT0.unitBelum.length, judul0: HT0.judul, petaContoh: petaContoh, contoh: hetC, contohB: hetB, belumNama: HT0.units.filter(function (u) { return !petaContoh[u.unit]; }).map(function (u) { return u.unit + ' (' + u.jenisTeks + ')'; }) };
var b0 = S.baris.find(function (b) { return b.st.id === 'S' && b.modalUnit > 0 && b.lamaN > 0; }); if (b0) { terapkanKeCache(susunUbah(b0.k, String(b0.lamaN + 100), 'jual', WX).dokumen); var T = susunTerbit(WX, true); var kK = kenal('katalogHargaKarung'); if (T.dokumen) Object.keys(T.dokumen[0].data).forEach(function (k) { if (!kK[k] && k !== 'modalSaatSetel') salah.push('katalogKarung.' + k); }); else salah.push('terbit ditolak: ' + T.tolak); }
print(JSON.stringify({ het: hetAsap, salah: salah, catatan: catatan, baris: S.baris.length, nDok: nDok, perlu: S.perlu.length, ringkas: S.ringkas.map(function (r) { return r.l + ' ' + r.a; }).join(' · '), target: S.target, targetDariRata: S.atur.targetDariRata, bongkar: S.atur.bongkarKg, bon: B.nBon, total: B.total, lewat: B.lewat.length, merk: D.merk.length, perluBeli: D.merk.filter(function (m) { return m.perlu; }).length, gab: gab, muatan: D.atur.muatanKg, pemasok: D.pemasok.map(function (p) { return p.nama.split(' ')[0] + ':' + p.cara; }).join(' · '), kelompok: kel }));
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


def baca(jalur): return open(os.path.join(AKAR, jalur), encoding='utf-8').read()


# paket brief 9 Okt (butir 8): layar Harga (statis) — HET tergambar di papan, kartu HET (ringkasan + Atur), lembar ubah & sebelum terbit; isian setelan dijaga
def periksa_layar(hg, idx):
    c = []
    if "import * as HET from './het-logika.js';" not in hg: c.append('harga.js tidak memuat het-logika.js')
    if '<link rel="modulepreload" href="js/layar/het-logika.js">' not in idx: c.append('modulepreload het-logika.js belum ada di baru/index.html')
    if 'const HT = HET.hetKatalog(S);' not in hg or '${gambarHet(s, HT)}' not in hg: c.append('katalog tidak menggambar kartu HET')
    if "HT.per[k].status === 'atas'" not in hg or 'het-atas' not in hg: c.append('papan tidak menandai harga di atas HET')
    if 'const HD = HET.hetDraf(S);' not in hg or "${HD.teks ? h`<div class=\"pita-info" not in hg or 'hetX(d.k).teks' not in hg: c.append('periksa sebelum terbit tidak memperingatkan HET')
    if 'HET.hetSatuHarga(b, ' not in hg: c.append('lembar ubah tidak menilai harga ketikan terhadap HET')
    if "pasangIsian(K, awal, ['ketik', 'aturH', 'aturHet'," not in hg: c.append('isian setelan HET (aturHet) tidak dijaga penjaga isian')
    if 'HET.susunPetaHet(unit, ' not in hg or 'HET.susunAturHet(' not in hg: c.append('Atur HET tidak menulis lewat susunAturHet / susunPetaHet')
    if '${HT.judul}' not in hg or '${HT.hit[id]}' not in hg: c.append('kartu HET tanpa judul keadaan / lima bagian yang menutup')
    return c


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            # ---- Paket F1: bon lama bergulir
            'F1 bon lama tidak pernah bergulir': js.replace("return b && b.jenis === 'saldoAwal' && g && g > String(b.tanggal || '') ? g : ''; };", "return ''; };"),
            'F1 centang kartu tidak tersimpan': js.replace("tempo, bonLamaBergulir: isi.bonLamaBergulir === true, diubahPada: w.kini };", "tempo, bonLamaBergulir: false, diubahPada: w.kini };"),
            'F1 jatuh tempo tetap dari tanggal bon asli': js.replace("const jatuh = T.hari > 0 && dasar ? bpTambahHari(dasar, T.hari) : '';", "const jatuh = T.hari > 0 && b.tanggal ? bpTambahHari(b.tanggal, T.hari) : '';"),
            # ---- H1 katalog
            '39b-11: LAHIR BUKU dianggap pemasok lagi': js.replace(" || n === 'LAHIR BUKU'; };", "; };"),
            'rugi memakai >= (untung nol jadi RUGI)': js.replace("const status = margin < -0.5 ? 'rugi' : Math.abs(margin) <= 0.5 ? 'nol'", "const status = margin <= 0.5 ? 'rugi' : Math.abs(margin) <= 0.5 ? 'nol'"),
            '"modal naik sesudah harga disetel" tidak terbaca (dimakan = bawah)': js.replace("const setel = hgModalSetel(dok, m); const naik = setel > 0 && bT > setel + 0.5;", "const setel = 0; const naik = false;"),
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
            'label rak: tugas dibuat untuk draf (belum terbit)': js.replace("  const tugas = daftarLabel().filter((t) => tampil(t.k)).map((t) => {", "  const tugas = daftarLabel().filter((t) => tampil(t.k)).concat(S.baris.filter((b) => b.adaDraf).map((b) => ({ k: b.k, lama: b.lamaN, tanggal: '' }))).map((t) => {"),   # putaran 27: daftar label disaring arsip dulu
            'label rak: angka yang diingat = harga lama terakhir, bukan yang masih tertulis': js.replace("const tertulis = ada ? Number(ada.lama) || 0 : b.lamaN;", "const tertulis = b.lamaN;"),
            'atur harga: langkah nol diterima': js.replace("|| baca('langkahRp', (n) => n > 0 && n <= 10000, 'Langkah naik-turun per kg harus 1–10.000 (tidak boleh nol)')", "|| baca('langkahRp', (n) => n >= 0 && n <= 10000, 'Langkah naik-turun per kg harus 1–10.000 (tidak boleh nol)')"),
            'ongkos bongkar per kg angka mati (bukan terukur)': js.replace("bongkarKg: bk === null ? bongkarTerukur() : bk, bongkarTerukur: bk === null,", "bongkarKg: bk === null ? 40 : bk, bongkarTerukur: bk === null,"),
            # ---- H2 bon pemasok
            'bon yang dibayar sebagian dianggap lunas': js.replace("bon.push({ id: String(b.id), pemasok: px.pemasok, tanggal: b.tanggal || '', gulir, nilai: Math.round(b.nilai || 0), dibayar: Math.round(b.dibayar || 0), sisa: Math.round(b.sisa || 0),", "if (b.dibayar > 0) return; bon.push({ id: String(b.id), pemasok: px.pemasok, tanggal: b.tanggal || '', gulir, nilai: Math.round(b.nilai || 0), dibayar: Math.round(b.dibayar || 0), sisa: Math.round(b.sisa || 0),"),
            'bon tanpa tanggal ikut diramal (jatuh dari tanggal kosong)': js.replace("const jatuh = T.hari > 0 && dasar ? bpTambahHari(dasar, T.hari) : '';", "const jatuh = T.hari > 0 ? bpTambahHari(dasar || iso, T.hari) : '';"),
            'tempo umum owner diabaikan (selalu bawaan 21)': js.replace("return { hari: isFinite(n) && n > 0 ? n : TEMPO_UMUM_BAWAAN, dariOwner: isFinite(n) && n > 0 };", "return { hari: TEMPO_UMUM_BAWAAN, dariOwner: false };"),
            'tempo kartu diabaikan (selalu tempo umum)': js.replace("const p = cariPemasok(nama); if (p && p.tempo > 0) return { hari: p.tempo, sumber: 'kartu', teks: 'tempo ' + p.tempo + ' hari (kartu pemasok)' };", ""),
            'bayar melebihi sisa bon diterima': js.replace("else if (n > bon.sisa) tolak = 'Melebihi sisa bon ini", "else if (false) tolak = 'Melebihi sisa bon ini"),
            'bayar melebihi uang toko diterima': js.replace("else if (B.adaKas && n + admin > B.kas) tolak = 'Uang toko cuma '", "else if (false) tolak = 'Uang toko cuma '"),
            'biaya admin tidak masuk biaya toko (laba tidak berkurang)': js.replace("if (H.admin > 0) dokumen.push({ koleksi: 'pengeluaranHarian'", "if (false) dokumen.push({ koleksi: 'pengeluaranHarian'"),
            'dokumen bayar tanpa bonId (pembayaran mengalir ke bon tertua)': js.replace("nominal: H.n, catatan, bonId: H.bon.id, bonTanggal: H.bon.tanggal || null, dari: H.D.dari };", "nominal: H.n, catatan, bonTanggal: H.bon.tanggal || null, dari: H.D.dari };"),
            'urungkan meninggalkan dokumen biaya admin': js.replace("ambilPengeluaranHarian().forEach((h) => { if (String(h.dariBayarBon || '') === String(id)) hapus.push({ koleksi: 'pengeluaranHarian', id: h.id }); });", ""),
            'bon lama ditulis bertanggal hari ini (umurnya bohong)': js.replace("bonTanggal: H.keHariIni ? w.tanggal : (H.D.tgl || null) };", "bonTanggal: w.tanggal };"),
            'bon lama nama kembar dibuat pemasok baru': js.replace("const kembar = namaBaru ? daftarPemasok().find((p) => p.kunci === kunciPelanggan(namaBaru)) : null;", "const kembar = null;"),
            'kartu pemasok memakai id nama mentah (bukan kunci)': js.replace("const data = { id: kunciPelanggan(nm), nama: p ? p.nama : nm,", "const data = { id: nm, nama: p ? p.nama : nm,"),
            'garis jatuh tempo tanpa penanda uang habis': js.replace("if (kas !== null && !habisSudah && jalan + b.sisa > kas) {", "if (false) {"),
            'kebiasaan bayar pemasok dari SATU kedatangan terakhir': js.replace("const tiga = s.batch.slice(0, 3);", "const tiga = s.batch.slice(0, 1);"),
            # ---- H3 belanja
            'saran belanja tidak dibulatkan ke karung penuh': js.replace("const saranK = Math.ceil(butuh / G.berat);", "const saranK = Math.floor(butuh / G.berat);"),
            'merek tanpa laju ditebak habis 0 hari': js.replace("const hariHabis = (sisa, laju) => (!(laju > 0) ? null : !(sisa > 0) ? 0 :", "const hariHabis = (sisa, laju) => (!(laju > 0) ? 0 : !(sisa > 0) ? 0 :"),
            'ambang hari setelan diabaikan': js.replace("const perlu = hari !== null && hari <= atur.ambangHari && saranK > 0 && !dipesan;", "const perlu = hari !== null && hari <= 7 && saranK > 0 && !dipesan;"),
            'yang sudah dipesan tetap disarankan': js.replace("const dipesan = menunggu.find((p) => (p.baris || []).some((b) => b.merk === m)) || null;", "const dipesan = null;"),
            'muatan truk angka mati 3.000 (bukan terukur)': js.replace("muatanKg: muat === null ? muatanTerukur() : muat, muatanTerukur: muat === null,", "muatanKg: muat === null ? 3000 : muat, muatanTerukur: muat === null,"),
            'penuhi truk menambah ke merek tanpa laju': js.replace("const calon = anggota.filter((c) => c.b.laju > 0);", "const calon = anggota;"),
            'pesanan datang tidak dibaca dari kedatangan': js.replace("const status = p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : D.datang ? 'datang' : 'menunggu';", "const status = p.status === 'batal' ? 'batal' : p.status === 'datang' ? 'datang' : 'menunggu';"),
            'harga termurah tanpa tanggal': js.replace("tanggal: p.hargaPerMerk[m].terakhir.tanggal, kode: p.hargaPerMerk[m].terakhir.merkPemasok || '' }))", "tanggal: '', kode: p.hargaPerMerk[m].terakhir.merkPemasok || '' }))"),
            'uang belanja tunai tidak dibandingkan dengan kas': js.replace("(kas === null ? 'Uang toko belum bisa dihitung (titik kas belum disetel).' : 'Uang toko sekarang ' + RP(kas) + (rp > kas ? ' — KURANG ' + RP(rp - kas) + '.' : ' — cukup.'))", "''"),
            'nomor WhatsApp pemasok tidak dipakai': js.replace("const nomor = nomorWa(R.kontak);", "const nomor = '';"),
            # ---- owner 7 Okt: belanja per harga beli terakhir
            '7 Okt: pesan WA kembali per nama merek': js.replace(".concat(R.g.map((g) => g.teks))", ".concat(R.d.map((b) => '• ' + b.merk + ' — ' + b.k + ' karung × ' + b.berat + ' kg'))"),
            '7 Okt: merek seharga tidak digabung': js.replace("const kunci = harga ? berat + '|' + harga + '|' + jenis : 'x|' + b.merk;", "const kunci = 'x|' + b.merk;"),
            '7 Okt: jenis beras beda tapi seharga ikut digabung': js.replace("const kunci = harga ? berat + '|' + harga + '|' + jenis : 'x|' + b.merk;", "const kunci = harga ? berat + '|' + harga : 'x|' + b.merk;"),
            '7 Okt: berat karung beda tapi seharga ikut digabung': js.replace("const kunci = harga ? berat + '|' + harga + '|' + jenis : 'x|' + b.merk;", "const kunci = harga ? harga + '|' + jenis : 'x|' + b.merk;"),
            '7 Okt: merek tanpa harga beli ikut digabung': js.replace("const kunci = harga ? berat + '|' + harga + '|' + jenis : 'x|' + b.merk;", "const kunci = berat + '|' + harga + '|' + jenis;"),
            '7 Okt: karung kelompok tidak dijumlah': js.replace("g.k += b.k || 0;", "g.k = b.k || 0;"),
            '7 Okt: tanpa harga tidak ditandai': js.replace("(g.adaHarga ? '' : ' · harga belum tercatat')", "''"),
            '7 Okt: + baris harga ke merek yang paling LAMA cukup': js.replace("const c = g.merk.slice().sort((x, y) => cukup(x, x.k) - cukup(y, y.k)", "const c = g.merk.slice().sort((x, y) => cukup(y, y.k) - cukup(x, x.k)"),
            '7 Okt: buku 25 kg dipesan dalam karung 50 kg': js.replace("const blBerat = (m, uk) => (uk[m] ? uk[m].berat : merkPunyaKarungBerat(m, 50)", "const blBerat = (m, uk) => (merkPunyaKarungBerat(m, 50)"),
            '7 Okt: jenis buku per ukuran tidak dari induknya': js.replace("String(jenisUntukMerk(blInduk(m, uk)) || '').trim()", "String(jenisUntukMerk(m) || '').trim()"),
            '7 Okt: dokumen pesanan tanpa barisHarga': js.replace("barisHarga: R.g.map(", "barisHargaX: R.g.map("),
            # ---- tinjauan E1: perlu & saran per BARIS HARGA (stok & laju gabungan), Daftar lengkap, arsip, stok 0, merek lalu, umur harga, baris hampir kembar
            'E1: perlu & saran per merek lagi (stok merek seharga tidak dihitung)': js.replace("const k = (x.pakai ? x.pakai.pemasok : '') + '|' + K.kunci;", "const k = x.merk;"),
            'E1: Daftar hanya memuat merek yang perlu (merek seharga tak terlihat)': js.replace("g.forEach((x) => x.merk.forEach((b) => isi.push(b)));", "g.forEach((x) => x.merk.forEach((b) => { if (b.perlu || b.k > 0) isi.push(b); }));"),
            'E1: merek seharga di Daftar juga muncul di "Belum perlu"': js.replace("&& !diKertas[b.merk]).sort(urutHari);", ").sort(urutHari);"),
            'E1: saran gabungan dibagi ke merek yang paling LAMA cukup': js.replace("const c = calon.slice().sort((a, b) => cukup(a) - cukup(b) || a.merk.localeCompare(b.merk))[0];", "const c = calon.slice().sort((a, b) => cukup(b) - cukup(a) || a.merk.localeCompare(b.merk))[0];"),
            'E1: penuhi truk per merek (stok seharga diabaikan)': js.replace("muat.sort((x, y) => cukupG(x.g) - cukupG(y.g) || ", "muat.sort((x, y) => "),
            'E1: stok 0 yang masih laku tidak ditebak (tidak disarankan)': js.replace("const hariHabis = (sisa, laju) => (!(laju > 0) ? null : !(sisa > 0) ? 0 :", "const hariHabis = (sisa, laju) => (!(laju > 0) ? null : !(sisa > 0) ? null :"),
            'E1: nama yang diarsipkan ikut belanja': js.replace("Array.from(merks).filter((m) => !arBeras(m, arsip)).map(", "Array.from(merks).map("),
            'E1: merek lalu menyebut nama buatan toko (wadah / kelas)': js.replace("const tokoNama = (n) => !n || !!kelasToko[n] || /campuran/i.test(n);", "const tokoNama = (n) => !n || /campuran/i.test(n);"),
            'E1: merek lalu menyebut bahan campuran': js.replace("const tokoNama = (n) => !n || !!kelasToko[n] || /campuran/i.test(n);", "const tokoNama = (n) => !n || !!kelasToko[n];"),
            'E1: merek pemasok yang tercatat (kelas sendiri) tidak dipakai': js.replace("const kp = b.pakai && b.pakai.kode ? String(b.pakai.kode).trim() : '';", "const kp = '';"),
            'E1: harga lama tanpa umur di pesan WA': js.replace("(basi ? ' (harga ' + blTglPendek(g.tanggal, terakhir) + ')' : '')", "''"),
            'E1: baris hampir kembar tidak dirapikan': js.replace("if (dekat && r.tanggal > s.tanggal && r.harga[0] !== s.harga) return", "if (false) return"),
            'E1: harga kelas dipakai walau bedanya melebihi batas owner': js.replace("Math.abs(r.harga[0] - s.harga) / s.harga * 100 <= vrBatas() + 1e-9", "true"),
            'E1: harga kelas dipakai walau kiriman terbarunya dua harga': js.replace("const dekat = r && r.harga.length === 1 && s.harga > 0", "const dekat = r && s.harga > 0"),
            'E1: harga kelas dari kelas tebakan': js.replace("o[m] = K.kelas && kmTerisi(K.asal) ? K.kelas : '';", "o[m] = K.kelas || '';"),
            'E1: tanggal & merek lalu hanya dari merek yang dipesan': js.replace("g.kenal = g.merk.concat(lain);", "g.kenal = g.merk;"),
            # ---- paket brief 9 Okt (butir 8): HET beras
            'HET: belum dipetakan dinilai premium (peringatan menyala sebelum owner memetakan)': js.replace("const kategori = A.peta[U.unit] || '';", "const kategori = A.peta[U.unit] || 'premium';"),
            'HET: belum dipetakan disebut lengkap/aman': js.replace("const keadaan = !total ? 'kosong' : unitBelum.length === daftarUnit.length ? 'belum' : unitBelum.length ? 'sebagian' : 'lengkap';", "const keadaan = !total ? 'kosong' : 'lengkap';"),
            'HET: harga TEPAT HET dianggap di atas': js.replace("if (lebih > 1e-6) return { status: 'atas'", "if (lebih >= -1e-6) return { status: 'atas'"),
            'HET: literan tidak dibagi kg per liter': js.replace("const hetPerKg = (n, st) => (n > 0 ? nilaiHarga(n, 0, st.kg, 0, false).perKg : 0);", "const hetPerKg = (n, st) => (n > 0 ? nilaiHarga(n, 0, st.id === 'L' ? 1 : st.kg, 0, false).perKg : 0);"),
            'HET: kemasan tidak dibagi ukurannya': js.replace("const hetPerKg = (n, st) => (n > 0 ? nilaiHarga(n, 0, st.kg, 0, false).perKg : 0);", "const hetPerKg = (n, st) => (n > 0 ? nilaiHarga(n, 0, st.id.charAt(0) === 'K' ? 1 : st.kg, 0, false).perKg : 0);"),
            'HET: setelan owner diabaikan (angka bawaan mati)': js.replace("medium: medium === null ? HET_BAWAAN.medium : medium, premium: premium === null ? HET_BAWAAN.premium : premium,", "medium: HET_BAWAAN.medium, premium: HET_BAWAAN.premium,"),
            'HET: premium dan medium tertukar': js.replace("const het = A[kategori]; if (!(perKg > 0))", "const het = A[kategori === 'premium' ? 'medium' : 'premium']; if (!(perKg > 0))"),
            'HET: bukan beras HET tetap dibandingkan': js.replace("if (kategori === 'bukan') return {", "if (false) return {"),
            'HET: kelas TEBAKAN dipakai': js.replace("if (K.kelas && kmTerisi(K.asal)) {", "if (K.kelas) {"),
            'HET: kelas merek diabaikan (merek selalu dinilai sendiri)': js.replace("if (K.kelas && kmTerisi(K.asal)) {", "if (false) {"),
            'HET: hitungan tidak menutup (belum ada harga dibuang)': js.replace("baris.forEach((x) => { hit[x.status] += 1; });", "baris.forEach((x) => { if (x.status !== 'kosong') hit[x.status] += 1; });"),
            'HET: sebelum terbit menilai harga LAMA (draf tidak diperiksa)': js.replace("const H = hetKatalog(S, 'tampil'); const daftar = H.baris.filter((x) => x.adaDraf);", "const H = hetKatalog(S, 'terbit'); const daftar = H.baris.filter((x) => x.adaDraf);"),
            'HET: harga kasir (dasbor) ikut membaca draf': js.replace("const n = terbit ? b.lamaN : b.n;", "const n = b.n;"),
            'HET: pemetaan menulis angka bawaan sebagai angka owner': js.replace("HET_KOLOM.forEach((x) => { if (d && d[x] !== undefined && d[x] !== null) data[x] = d[x]; });", "HET_KOLOM.forEach((x) => { data[x] = A[x]; });"),
            'HET: premium lebih rendah dari medium diterima': js.replace("if (P.n < M.n) return { tolak:", "if (false) return { tolak:"),
            'HET: simpan setelan menghapus pemetaan': js.replace("sumber, peta: Object.assign({}, kini.peta) };", "sumber, peta: {} };"),
            'HET: selisih di bawah Rp1 tampil "Rp0"': js.replace("const hetRp = (x) => (Math.round(x) >= 1 ? RP(x) : 'Rp' + DESIMAL(x));", "const hetRp = (x) => RP(x);"),
            'HET: lembar ubah menilai harga lama, bukan ketikan': js.replace("const perKg = hetPerKg(Math.round(Number(n) || 0), b.st);", "const perKg = hetPerKg(b.n, b.st);"),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:120] if g else '-'))
            if not g: kode = 3
        # layar (statis): HET wajib tergambar di papan, kartu HET, lembar ubah & sebelum terbit
        HG0, IX0 = baca('baru/js/layar/harga.js'), baca('baru/index.html')
        layar = {
            'layar: kartu HET tidak digambar': (HG0.replace('${gambarHet(s, HT)}', ''), IX0),
            'layar: papan tanpa tanda di atas HET': (HG0.replace("HT.per[k].status === 'atas'", "HT.per[k].status === 'xx'"), IX0),
            'layar: sebelum terbit tanpa peringatan HET': (HG0.replace('${HD.teks ? h`<div class="pita-info', '${false ? h`<div class="pita-info'), IX0),
            'layar: isian setelan HET tidak dijaga': (HG0.replace("pasangIsian(K, awal, ['ketik', 'aturH', 'aturHet',", "pasangIsian(K, awal, ['ketik', 'aturH',"), IX0),
            'layar: modulepreload het-logika.js hilang': (HG0, IX0.replace('<link rel="modulepreload" href="js/layar/het-logika.js">\n', '')),
        }
        for nama, (a, b) in layar.items():
            if a == HG0 and b == IX0: print('KONTROL BASI  ' + nama); kode = 3; continue
            c = periksa_layar(a, b)
            print(('BERBUNYI ' if c else 'DIAM!!   ') + nama + ' → ' + (c[0][:120] if c else '-'))
            if not c: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    g += ['layar: ' + x for x in periksa_layar(baca('baru/js/layar/harga.js'), baca('baru/index.html'))]
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        h, e = jalan("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else:
            print('ASAP DATA TOKO (%s): %d baris harga dari %d dokumen katalog · %d perlu diputuskan · %s · target %s%s · bongkar %s/kg · bon %d = %s (lewat tempo %d) · belanja %d merek, %d perlu (tinjauan E1: %d baris harga, %d perlu; %d merek stoknya tipis tapi ditutup merek seharga), muatan %s kg · %s · pesanan per harga (owner 7 Okt): %d merek → %d baris di %d pemasok, jumlah karung/kg/rp sama · yang tidak cocok: %s%s'
                  % (os.path.basename(cad[-1]), h['baris'], h['nDok'], h['perlu'], h['ringkas'], h['target'], ' (rata-rata)' if h['targetDariRata'] else '', h['bongkar'], h['bon'], h['total'], h['lewat'], h['merk'], h['perluBeli'], h['gab']['baris'], h['gab']['perlu'], len(h['gab']['tutup']), h['muatan'], h['pemasok'], h['kelompok']['merek'], h['kelompok']['baris'], h['kelompok']['pemasok'], ', '.join(h['salah']) or 'tidak ada', (' · catatan (angka cadangan toko): ' + '; '.join(h['catatan'])) if h.get('catatan') else ''))
            if not h['kelompok']['pemasok']: g.append('asap: pesanan per harga tidak teruji (tidak ada pemasok berkarung)')
            if h['salah']: g.append('asap: ' + ', '.join(h['salah']))
            t = h['het']; c = t['contoh']; hc = c['hit']
            print('ASAP HET (paket brief butir 8, angka toko %s): dokumen aturanToko/het %s · keadaan %s — %s · %d kelas/merek di katalog, %d harga di atas HET tanpa pemetaan'
                  % (tgl, 'ADA' if t['dok'] else 'belum ada', t['keadaan'], t['judul0'], t['unit'], t['nAtas0']))
            print('   PEMETAAN CONTOH (bukan keputusan owner: %s): %s · dari %d harga: %d di atas HET · %d sama/di bawah · %d belum dipetakan (%d kelas/merek) · %d bukan beras HET · %d belum ada harga · harga kasir (terbit) di atas HET: %d'
                  % (', '.join('%s → %s' % kv for kv in sorted(t['petaContoh'].items())) or '-', c['judul'], sum(hc.values()), hc['atas'], hc['dalam'], hc['belum'], c['unitBelum'], hc['bukan'], hc['kosong'], c['kasirAtas']))
            for x in c['atas']: print('     · ' + x)
            print('   kelas/merek yang dibiarkan belum dipetakan di contoh: ' + (', '.join(t['belumNama']) or '-'))
            print('   CONTOH B (semua kelas berwadah premium, kelas tanpa wadah bukan): %d harga di atas HET (kasir %d), belum dipetakan %d kelas/merek' % (t['contohB']['atas'], t['contohB']['kasirAtas'], t['contohB']['unitBelum']))
    sys.exit(2 if g else 0)
