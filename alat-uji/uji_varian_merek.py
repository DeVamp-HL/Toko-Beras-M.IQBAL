#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_varian_merek.py — putaran 27 Bagian 2: VARIAN MEREK PER BELANJA (owner 27 Sep: barang berbeda dengan nama yang sama = nama sendiri).
  · Barang masuk: nama yang sudah punya buku & harga beli beda > batas owner (bawaan 5 %) dari modal berjalan → WAJIB dijawab "sama barangnya" (gabung,
    modal dirata-rata seperti biasa) atau "beda mutu" (nama "<induk> · <mutu>", atau "<induk> · <tanggal>"). Di bawah batas, koreksi, nama baru: tidak ditanya.
  · Kolam lama TIDAK berubah saat varian dibuat; varian mewarisi jenis beras induknya (kunci baru di peta pengaturan/jenisBeras yang sama).
  · Harga jual ditawarkan (usul = modal + target katalog) dan terbit sendiri (draf lain tidak ikut); varian bisa dibuat dari Harga sebelum barangnya datang.
KOTAK PASIR (ANGKA CONTOH), jam dikunci 19 Sep 2026 10:00 WIB. Cadangan toko di _privat/ (kalau ada): tiap nama di buku diberi kedatangan contoh —
harga ±3 % tidak ditanya, ±10 % ditanya; varian untuk semua nama → buku nama lama byte-sama.

    python3 alat-uji/uji_varian_merek.py            → N lulus · 0 gagal
    python3 alat-uji/uji_varian_merek.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kunci_periode  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/arsip-logika.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/nego-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/wadah-bernama-logika.js', 'baru/js/layar/stok-adukan-logika.js', 'baru/js/layar/setengah-logika.js',
                                  'baru/js/layar/stok-logika.js', 'baru/js/layar/varian-logika.js', 'baru/js/layar/stok-hpp-logika.js', 'baru/js/layar/kelas-merek-logika.js', 'baru/js/layar/stok-catat-logika.js', 'baru/js/layar/harga-logika.js', 'baru/js/layar/jenis-beras-logika.js', 'baru/js/layar/struk-logika.js']   # putaran 30: + stok-hpp & kelas-merek
JAM_TETAP = "var __KINI = new Date('2026-09-19T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"


def baris(merk, n, harga, berat=50):
    return {'id': str(n), 'merk': merk, 'satuan': 'karung', 'beratKarung': berat, 'jumlahKarung': n, 'totalKg': n * berat, 'hargaPerKg': harga, 'subtotalHarga': n * berat * harga}


KOTAK = {
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [baris('LL', 10, 14000), baris('IR64 LL', 4, 14800), baris('Kumala', 10, 14000), baris('Polos', 2, 13000)]}],
  'penjualan': [{'id': 'j1', 'tanggal': '2026-09-12', 'jam': '09:00', 'jenis': 'karung', 'merkSumber': 'LL', 'totalKg': 50, 'jumlahKarung': 1, 'beratKarungAcuan': 50, 'hargaTotal': 740000, 'hppTotalSaatJual': 700000, 'caraBayar': 'Tunai'}],
  'katalogHargaKarung': [{'id': 'LL', 'merk': 'LL', 'hargaPerKg': 14800}, {'id': 'Kumala', 'merk': 'Kumala', 'hargaPerKg': 14500}],
  'pengaturan': [{'id': 'jenisBeras', 'peta': {'LL': 'IR64', 'Kumala': 'IR64', 'Polos': ''}}],
  'aturanToko': [{'id': 'harga', 'targetPerKg': 500, 'bulatKarung': 100, 'bulatLiter': 500, 'bulatKemasan': 1000, 'langkahRp': 50, 'ambangDampak': 50000, 'bongkarKg': 0, 'mdrPersen': 30, 'mdrBatas': 500000},
                 {'id': 'hargaDraf', 'draf': {'Kumala|S': 14700}}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
var KOL = ['batchMasuk', 'penjualan', 'katalogHargaKarung', 'pengaturan', 'aturanToko', 'hargaTerbit'];
var pulih = function () { KOL.forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n] || []))); }); };
pulih();
var nId = 9000; var W = { tanggal: '2026-09-19', jam: '10:00', kini: '2026-09-19T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var draf = function (baris, ubah) { return Object.assign({ id: null, tanggal: '2026-09-19', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', bongkar: '', alasan: '', baris: baris }, ubah || {}); };
var brs = function (merk, n, harga, ubah) { return Object.assign({ merk: merk, jumlahKarung: String(n), beratKarung: 50, hargaPerKg: String(harga) }, ubah || {}); };
var stok = function (m) { return hitungStokKarungPerMerk()[m] || {}; };
var terapkan = function (r) { terapkanKeCache((r && r.dokumen) || []); return r; };

// ---- 1 · di bawah batas: tidak ditanya, gabung seperti biasa
var v1 = vrPerluTanya('LL', 14500);
ok('LL modal 14.000, beli 14.500 (3,6 % ≤ 5 %) → TIDAK ditanya; tersimpan atas nama LL', v1.perlu === false && v1.beda === 3.6 && v1.batas === 5 && (function () { var r = susunSimpanMasuk(draf([brs('LL', 4, 14500)]), W, true); return !r.tolak && r.dokumen[0].data.merkList[0].merk === 'LL' && r.dokumen.length === 1; })(), J(v1));
// ---- 2 · di atas batas: wajib dijawab
var v2 = vrPerluTanya('LL', 16000); var r2 = susunSimpanMasuk(draf([brs('LL', 4, 16000)]), W, true);
ok('LL beli 16.000 (14,3 % > 5 %) → simpan DITOLAK sampai dijawab, kalimat menyebut harga, beda %, modal LL, batas', v2.perlu === true && v2.naik === true && r2.perluVarian === 1 && /Baris 1 \(LL\): harga beli Rp16\.000\/kg beda 14,3 % dari modal LL Rp14\.000\/kg \(batas 5 %\)/.test(r2.tolak), J([v2, r2.tolak]));
ok('harga TURUN jauh juga ditanya (LL beli 12.000 = −14,3 %)', vrPerluTanya('LL', 12000).perlu === true && vrPerluTanya('LL', 12000).naik === false);
// ---- 3 · "sama barangnya" = gabung (modal dirata-rata seperti biasa)
var r3 = susunSimpanMasuk(draf([brs('LL', 4, 16000, { varian: 'sama' })]), W, true); terapkan(r3);
ok('SAMA barangnya → satu kolam LL: 450 + 200 = 650 kg, modal rata-rata (10×50×14.000 + 4×50×16.000) / 700 kg; tanpa dokumen jenis, tanpa tawaran harga', !r3.tolak && r3.dokumen.length === 1 && r3.dokumen[0].data.merkList[0].merk === 'LL' && stok('LL').sisaKg === 650 && Math.abs(stok('LL').hppTerakhirPerKg - (500 * 14000 + 200 * 16000) / 700) < 0.001 && !r3.patch.varianTawar, J(stok('LL')));
pulih();
// ---- 4 · "beda mutu" = varian; kolam lama tidak disentuh; jenis ikut induk
var llSebelum = J(stok('LL')); var petaSebelum = J(ambilPetaJenisBeras());
var r4 = susunSimpanMasuk(draf([brs('LL', 4, 16000, { varian: 'beda', namaMutu: ' Premium ' })]), W, true);
var dj = (r4.dokumen || []).find(function (d) { return d.koleksi === 'pengaturan'; });
ok('BEDA mutu → kedatangan atas nama "LL · Premium" (pemisah titik tengah); + satu dokumen pengaturan/jenisBeras berisi kunci baru = jenis induk (IR64), kunci lain utuh; tawaran harga membawa modal kedatangan ini',
  !r4.tolak && r4.dokumen[0].data.merkList[0].merk === 'LL · Premium' && !!dj && dj.data.id === 'jenisBeras' && dj.data.peta['LL · Premium'] === 'IR64' && dj.data.peta.LL === 'IR64' && dj.data.peta.Kumala === 'IR64' && Object.keys(dj.data.peta).length === 4
  && r4.patch.varianTawar.length === 1 && r4.patch.varianTawar[0].merk === 'LL · Premium' && r4.patch.varianTawar[0].induk === 'LL' && r4.patch.varianTawar[0].modalKg === 16000 && r4.patch.varianTawar[0].baru === true && /kolam lama tidak disentuh/.test(r4.patch.kabar), J(r4));
terapkan(r4);
ok('sesudah varian: buku LL BYTE-SAMA (sisa & modal tidak bergeser); LL · Premium kolam sendiri 200 kg @16.000; jenisnya IR64 (diisi, bukan tebakan)', J(stok('LL')) === llSebelum && stok('LL · Premium').sisaKg === 200 && stok('LL · Premium').hppTerakhirPerKg === 16000 && jenisUntukMerk('LL · Premium') === 'IR64' && jbDaftar().baris.find(function (b) { return b.merk === 'LL · Premium'; }).asal === 'owner', J([stok('LL'), llSebelum]));
ok('varian = nama karung biasa: katalog harga punya barisnya (belum ada harga), barang masuk berikutnya menawarkan namanya', HG_baris('LL · Premium|S') && HG_baris('LL · Premium|S').status === 'lubang' && calonMerkMasuk().indexOf('LL · Premium') >= 0);
// kedatangan kedua ke varian yang sama: beda kecil dari modal VARIAN → tidak ditanya
ok('kedatangan berikutnya "LL · Premium" @16.200 (1,3 % dari modal varian) → tidak ditanya', vrPerluTanya('LL · Premium', 16200).perlu === false);
pulih();
// ---- 5 · tanpa nama mutu → tanggal datang
var r5 = susunSimpanMasuk(draf([brs('LL', 4, 16000, { varian: 'beda', namaMutu: '' })]), W, true);
ok('beda mutu tanpa nama → "LL · 19 Sep" (tanggal datang)', !r5.tolak && r5.dokumen[0].data.merkList[0].merk === 'LL · 19 Sep', J(r5.tolak || r5.dokumen[0].data.merkList));
ok('nama mutu bertitik tengah ditolak; dua baris jadi nama sama ditolak', !!susunSimpanMasuk(draf([brs('LL', 4, 16000, { varian: 'beda', namaMutu: 'A · B' })]), W, true).tolak
  && /tertulis dua kali/.test(susunSimpanMasuk(draf([brs('LL', 4, 16000, { varian: 'beda', namaMutu: 'X' }), brs('LL', 2, 16500, { varian: 'beda', namaMutu: 'X' })]), W, true).tolak || ''));
// ---- 6 · batas diatur owner
var AC = susunAturCatat({ batasVarian: '20' }, W); terapkan(AC);
ok('owner menyetel batas 20 % → LL @16.000 (14,3 %) tidak ditanya lagi; dokumen catatStok membawa batasVarian 20; 101 % ditolak', !AC.tolak && AC.dokumen[0].data.batasVarian === 20 && vrPerluTanya('LL', 16000).perlu === false && !susunSimpanMasuk(draf([brs('LL', 4, 16000)]), W, true).tolak && !!susunAturCatat({ batasVarian: '101' }, W).tolak, J(AC));
pulih();
// ---- 7 · koreksi & nama baru tidak ditanya
var dk = drafDariKedatangan('b1'); dk.baris[0].hargaPerKg = '17000'; dk.alasan = 'salah ketik';
ok('koreksi kedatangan (harga LL diubah jauh) TIDAK ditanya — cuma kedatangan baru', !susunSimpanMasuk(dk, W, true).tolak);
ok('nama BARU (belum punya buku) tidak ditanya', vrPerluTanya('Tawon', 20000).perlu === false && !susunSimpanMasuk(draf([brs('Tawon', 4, 20000)]), W, true).tolak);
// ---- 8 · jenis induk lewat tebakan / dikosongkan
var r8 = susunSimpanMasuk(draf([brs('IR64 LL', 2, 17000, { varian: 'beda', namaMutu: 'Super' }), brs('Polos', 2, 16000, { varian: 'beda', namaMutu: 'B' })]), W, true);
var p8 = ((r8.dokumen || []).find(function (d) { return d.koleksi === 'pengaturan'; }) || { data: { peta: {} } }).data.peta;
ok('induk ber-jenis TEBAKAN (IR64 LL → IR64) diwariskan sebagai isian; induk yang DIKOSONGKAN owner (Polos = "") → varian juga kosong', !r8.tolak && p8['IR64 LL · Super'] === 'IR64' && p8['Polos · B'] === '', J(p8));
pulih();
// ---- 9 · tawaran harga: usul = modal + target; terbit varian saja
var atH = aturHarga(); ok('usul harga varian = ke atas(16.000 + target 500, Rp100) = 16.500', vrUsulHarga(16000, atH) === 16500 && vrUsulHarga(0, atH) === 0, J(atH));
terapkan(susunSimpanMasuk(draf([brs('LL', 4, 16000, { varian: 'beda', namaMutu: 'Premium' })]), W, true));
var T9 = vrSusunTerbitHarga('LL · Premium', '16.500', W); var kd = (T9.dokumen || []).find(function (d) { return d.koleksi === 'katalogHargaKarung'; });
ok('TERBIT harga varian: katalogHargaKarung {id & merk = nama varian, hargaPerKg 16.500, modalSaatSetel = harga beli terakhir} + hargaTerbit 1 baris + tugas label; draf Kumala TIDAK ikut terbit (dokumen hargaDraf tidak ditulis)',
  !T9.tolak && kd && kd.data.id === 'LL · Premium' && kd.data.hargaPerKg === 16500 && kd.data.modalSaatSetel === 16000 && T9.dokumen.some(function (d) { return d.koleksi === 'hargaTerbit' && d.data.n === 1; })
  && T9.dokumen.some(function (d) { return d.data.id === 'hargaLabel' && d.data.daftar.some(function (x) { return x.k === 'LL · Premium|S'; }); }) && !T9.dokumen.some(function (d) { return d.data.id === 'hargaDraf'; }), J(T9));
terapkan(T9); ok('sesudah terbit: katalog varian 16.500/kg (untung 500/kg), draf Kumala 14.700 masih menunggu', HG_baris('LL · Premium|S').n === 16500 && HG_baris('LL · Premium|S').status !== 'lubang' && drafHarga()['Kumala|S'] === 14700);
var T9b = vrSusunTerbitHarga('LL · Premium', '15.000', W); ok('harga varian di bawah modal → ketukan kedua', T9b.perluYakin === true && !vrSusunTerbitHarga('LL · Premium', '15.000', W, true).tolak);
pulih();
// ---- 10 · varian dari layar Harga (sebelum barang datang)
var B10 = vrSusunBuatDariHarga('Kumala', 'Super', '15.000', W);
ok('varian dari Harga: "Kumala · Super" — katalog per kg terbit + jenis ikut Kumala (IR64); ditolak: induk tak dikenal, mutu kosong, nama yang sudah ada',
  !B10.tolak && B10.dokumen.some(function (d) { return d.koleksi === 'katalogHargaKarung' && d.data.merk === 'Kumala · Super' && d.data.hargaPerKg === 15000; }) && B10.dokumen.some(function (d) { return d.koleksi === 'pengaturan' && d.data.peta['Kumala · Super'] === 'IR64'; })
  && !!vrSusunBuatDariHarga('Tak Ada', 'X', '15.000', W).tolak && !!vrSusunBuatDariHarga('Kumala', '', '15.000', W).tolak && (terapkan(B10), !!vrSusunBuatDariHarga('Kumala', 'Super', '15.000', W).tolak), J(B10));
ok('sesudahnya: barang masuk menawarkan "Kumala · Super", katalog punya barisnya, jenis beras terisi', calonMerkMasuk().indexOf('Kumala · Super') >= 0 && HG_baris('Kumala · Super|S').n === 15000 && jenisUntukMerk('Kumala · Super') === 'IR64');

// ---- perbaikan 28 Sep: induk berstok TANPA harga jual → kartu varian memperingatkan (stok tetap di nama induk, tidak tampil di Jual); induk berharga / tanpa stok → diam
ok('peringatan varian: Polos (stok 100 kg, tanpa katalog) → kalimat menyebut stok, "BELUM ada harga jual", "setel harga Polos di katalog", varian stok 0; LL (berharga) & nama tanpa stok → kosong', /^Polos punya stok 100 kg tapi BELUM ada harga jual — stok itu tetap atas nama Polos dan tidak tampil di Jual\. Kalau barangnya SAMA, setel harga Polos di katalog \(bukan varian\)\. Varian = nama BARU yang stoknya 0/.test(vrPeringatanInduk('Polos')) && vrPeringatanInduk('LL') === '' && vrPeringatanInduk('Tak Ada') === '' && vrPeringatanInduk('') === '', vrPeringatanInduk('Polos'));
// ---- putaran 27 (cek 390 px): kartu "Varian merek baru" di Harga tidak menawarkan nama wadah / kelas sebagai induk
ok('induk varian baru dari layar Harga: nama wadah / kelas mutu (IR64 Apex, IR42 Value) & nama varian TIDAK ditawarkan; Angsa (wadah yang juga merek karung) & merek biasa tetap', J(vrCalonInduk(['Angsa', 'IR42 Value', 'IR64 Apex', 'Kumala', 'LL', 'LL · Premium'])) === J(['Angsa', 'Kumala', 'LL']), J(vrCalonInduk(['Angsa', 'IR42 Value', 'IR64 Apex', 'Kumala', 'LL', 'LL · Premium'])));

// ---- ASAP DATA TOKO
var asap = null;

// ---- audit 39b no. 43 (owner 30 Sep: petunjuk satu ketukan): "TH" diketik padahal barangnya sudah berbuku sebagai varian "TH · House"
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'b43', tanggal: '2026-09-18', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: '1', merk: 'TH · House', satuan: 'karung', beratKarung: 50, jumlahKarung: 3, totalKg: 150, hargaPerKg: 12000, subtotalHarga: 1800000 }] } },
  { koleksi: 'katalogHargaKarung', data: { id: 'TH · Gold', merk: 'TH · Gold', hargaPerKg: 14000 } },
  // buku per ukuran "TH · House 25 kg" (buku khusus, bukan nama barang masuk) — TIDAK boleh ditawarkan sebagai saran
  { koleksi: 'batchMasuk', data: { id: 'b43u', tanggal: '2026-09-18', jam: '08:05', pemasok: 'LAHIR BUKU', caraBayar: 'tunai', biayaBongkar: 0, stokAwal: true, lahirBuku: true, merkList: [{ id: '1', merk: 'TH · House 25 kg', satuan: 'lahir', beratKarung: 25, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, indukUkuran: 'TH · House' }] } }]);
// tinjauan 30 Sep: arsip & buku khusus wadah yang berinduk TH juga TIDAK boleh ditawarkan — dulu hanya buku per ukuran yang benar-benar diuji
terapkanKeCache([{ koleksi: 'katalogHargaKarung', data: { id: 'TH · Lama', merk: 'TH · Lama', hargaPerKg: 13000 } },
  { koleksi: 'aturanToko', data: { id: 'produkArsip', daftar: [{ kunci: 'K:TH · Lama', nama: 'TH · Lama', pada: '2026-09-18' }] } },
  // varian yang bukunya LEBIH BESAR dari induknya (Polos · Besar 600 kg vs Polos) — urutan 'induk paling depan' harus tetap berlaku
  { koleksi: 'batchMasuk', data: { id: 'b43p', tanggal: '2026-09-18', jam: '08:07', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: '1', merk: 'Polos \u00b7 Besar', satuan: 'karung', beratKarung: 50, jumlahKarung: 12, totalKg: 600, hargaPerKg: 13000, subtotalHarga: 7800000 }] } },
  { koleksi: 'batchMasuk', data: { id: 'b43w', tanggal: '2026-09-18', jam: '08:06', pemasok: 'LAHIR BUKU', caraBayar: 'tunai', biayaBongkar: 0, stokAwal: true, lahirBuku: true, merkList: [{ id: '1', merk: 'TH · Karung W9', satuan: 'lahir', beratKarung: 50, jumlahKarung: 0, totalKg: 0, hargaPerKg: 0, subtotalHarga: 0, karungWadah: 'W9' }] } }]);
var H43 = hitungMasuk(draf([brs('TH', 2, 12000), brs('  th ', 1, 12000), brs('TH · House', 1, 12000), brs('Polos', 1, 13000)]));
ok('39b-43 "TH" (tanpa buku) → baris baru dengan saran varian: TH · House (buku 150 kg) dulu, lalu TH · Gold (katalog saja, 0 kg); buku per ukuran TH · House 25 kg tidak ditawarkan; huruf kecil & spasi tidak dibedakan',
  H43.baris[0].baru === true && J(H43.baris[0].saranVarian) === J([{ nama: 'TH · House', bukuKg: 150 }, { nama: 'TH · Gold', bukuKg: 0 }]) && J(H43.baris[1].saranVarian) === J(H43.baris[0].saranVarian), J(H43.baris.slice(0, 2).map(function (b) { return [b.merkKetik, b.baru, b.saranVarian]; })));
ok('39b-43 nama varian yang diketik lengkap, dan nama yang sudah berbuku sendiri (Polos), TIDAK diberi saran; koreksi kedatangan juga tidak', !H43.baris[2].baru && !H43.baris[2].saranVarian.length && !H43.baris[3].saranVarian.length
  && !hitungMasuk(draf([brs('TH', 1, 12000)], { id: 'b1' })).baris[0].saranVarian.length && ckSaranVarian('TH · House').length === 0 && ckSaranVarian('').length === 0, J([H43.baris[2].saranVarian, H43.baris[3].saranVarian]));
var H43c = hitungMasuk(draf([brs('kumala', 1, 14000), brs('th · house', 1, 12000), brs('ll', 1, 14000), brs('polos', 1, 13000), brs('ir64  ll', 1, 14000)])); var kgKumala = stok('Kumala').sisaKg;
ok('39b-43 tinjauan: nama yang SAMA kecuali huruf ("kumala", "th · house", "ll", "polos", "ir64  ll" berspasi ganda) → buku aslinya ditawarkan PALING DEPAN, juga saat variannya lebih berisi (bukan cuma variannya); arsip TH · Lama & buku wadah TH · Karung W9 tidak ditawarkan',
  H43c.baris[0].baru === true && H43c.baris[0].saranVarian.length >= 2 && J(H43c.baris[0].saranVarian[0]) === J({ nama: 'Kumala', bukuKg: kgKumala }) && H43c.baris[0].saranVarian.some(function (v) { return v.nama === 'Kumala \u00b7 Super'; })
  && J(H43c.baris[1].saranVarian) === J([{ nama: 'TH \u00b7 House', bukuKg: 150 }]) && H43c.baris[2].saranVarian.length && H43c.baris[2].saranVarian[0].nama === 'LL' && J(H43c.baris[3].saranVarian.map(function (v) { return v.nama; })) === J(['Polos', 'Polos \u00b7 Besar']) && stok('Polos \u00b7 Besar').sisaKg > stok('Polos').sisaKg && H43c.baris[4].saranVarian.length && H43c.baris[4].saranVarian[0].nama === 'IR64 LL'
  && !ckSaranVarian('TH').some(function (v) { return v.nama === 'TH \u00b7 Lama' || v.nama === 'TH \u00b7 Karung W9'; }), J(H43c.baris.map(function (b) { return [b.merkKetik, b.baru, b.saranVarian]; })));
var R43 = susunSimpanMasuk(draf([brs('TH · House', 2, 12000)]), W, true); var b43 = (R43.dokumen || []).find(function (d) { return d.koleksi === 'batchMasuk'; });
ok('39b-43 sesudah "pakai TH · House" (baris diganti ke nama varian): kedatangan tercatat atas TH · House, buku varian naik 150 → 250 kg, tidak ada buku "TH" baru', !R43.tolak && b43 && b43.data.merkList[0].merk === 'TH · House' && (function () { terapkanKeCache(R43.dokumen || []); return stok('TH · House').sisaKg === 250 && !hitungStokKarungPerMerk()['TH']; })(), J([R43.tolak, b43 && b43.data.merkList]));
if (CADANGAN) {
  Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
  // audit 39b no. 43: diukur di data toko APA ADANYA (sebelum varian contoh "· Uji" dibuat di bawah)
  var saranToko = ['TH', 'SR', 'HSj', 'SB', 'II', 'MTJ'].map(function (n) { return [n, ckSaranVarian(n).map(function (v) { return v.nama; })]; });
  // putaran 27 (Bagian 5): nama wadah / kelas mutu (IR64 Apex dkk.) tidak boleh lagi datang lewat barang masuk — dipisah: merek → varian, kelas → wajib ditolak
  var kelas = wbNamaKelas(); var st0 = hitungStokKarungPerMerk(); var semuaNama = Object.keys(st0).filter(function (m) { return st0[m].hppTerakhirPerKg > 0; });
  // putaran 28: buku per ukuran ('Merek 25 kg') & buku khusus wadah bukan nama barang masuk — ditolak dengan benar, jadi tidak ikut asap varian
  var bukanMasuk = Object.assign({}, petaUkuran(), petaBukuWadah());
  var nama = semuaNama.filter(function (m) { return !kelas[m] && !bukanMasuk[m]; }); var namaKelas = semuaNama.filter(function (m) { return kelas[m]; });
  var tanya3 = nama.filter(function (m) { return vrPerluTanya(m, Math.round(st0[m].hppTerakhirPerKg * 1.03)).perlu; });
  var tanya10 = nama.filter(function (m) { return !vrPerluTanya(m, Math.round(st0[m].hppTerakhirPerKg * 1.10)).perlu; });
  var WC = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
  var sebelum = J(st0); var R = susunSimpanMasuk(draf(nama.map(function (m) { return brs(m, 1, Math.round(st0[m].hppTerakhirPerKg * 1.10), { varian: 'beda', namaMutu: 'Uji' }); }), { tanggal: TGL_CAD }), WC, true);
  terapkanKeCache(R.dokumen || []); var st1 = hitungStokKarungPerMerk(); var lamaSama = nama.every(function (m) { return J(st1[m]) === J(st0[m]); });
  var petaR = ((R.dokumen || []).find(function (d) { return d.koleksi === 'pengaturan'; }) || { data: { peta: {} } }).data.peta;
  var jenisIkut = nama.every(function (m) { return petaR[m + ' · Uji'] === jenisUntukMerk(m); });
  var kelasLolos = namaKelas.filter(function (m) { return !/nama WADAH/.test(susunSimpanMasuk(draf([brs(m, 1, Math.round(st0[m].hppTerakhirPerKg * 1.10), { varian: 'beda', namaMutu: 'Uji' })], { tanggal: TGL_CAD }), WC, true).tolak || ''); });
  // tinjauan 30 Sep: tiap nama berbuku (bukan varian, bukan buku khusus) yang diketik huruf kecil → buku aslinya paling depan di saran
  var hurufKecil = Object.keys(st0).filter(function (m) { return st0[m].sisaKg > 0.004 && m.indexOf('\u00b7') < 0 && !bukanMasuk[m] && !arBeras(m) && m.toLowerCase() !== m; });
  var hurufSalah = hurufKecil.filter(function (m) { var v = ckSaranVarian(m.toLowerCase()); return !v.length || v[0].nama !== m; });
  asap = { hurufKecil: hurufKecil.length, hurufSalah: hurufSalah, saranToko: saranToko, nama: nama.length, tanya3: tanya3, tanya10: tanya10, tolak: R.tolak || '', lamaSama: lamaSama, jenisIkut: jenisIkut, varian: Object.keys(st1).filter(function (m) { return / · Uji$/.test(m); }).length, kelas: namaKelas.length, kelasLolos: kelasLolos };
}
print(J({ lulus: lulus, gagal: gagal, asap: asap }));
"""
# pembantu katalog (hgSemua) untuk skenario
PEMBANTU = "function HG_baris(k) { return hgSemua(new Date(Date.now())).baris.find(function (b) { return b.k === k; }) || null; }\n"


def cadangan_toko():
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def utama(js, pakai_cadangan):
    cad = 'null'; tgl = ''
    p = cadangan_toko() if pakai_cadangan else None
    if p:
        d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
        cad = json.dumps(dict((n, d[n]) for n in kol if isinstance(d.get(n), list))); tgl = os.path.basename(p).split('miqbal-')[-1][:10]
    h, e = jalan(JAM_TETAP + js + '\n' + PEMBANTU + 'var KOTAK = ' + json.dumps(KOTAK) + ';\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    return h['lulus'], h['gagal'], h.get('asap')


RUSAK = {
    'varian ditanya walau di bawah batas': ("return { perlu: beda > batas + 1e-9,", "return { perlu: beda > 0,"),
    'batas owner (catatStok.batasVarian) diabaikan': ("return a && a.batasVarian !== undefined && a.batasVarian !== null && isFinite(n) && n >= 0 ? n : VR_BATAS_BAWAAN;", "return VR_BATAS_BAWAAN;"),
    'pertanyaan varian dilewati (langsung gabung)': ("  if (h.tanyaVarian.length) { const x = h.tanyaVarian[0];", "  if (false) { const x = h.tanyaVarian[0];"),
    'beda mutu tetap dicatat atas nama lama (kolam lama berubah)': ("const merkVarian = pilih === 'beda' ? vrNama(merk, b.namaMutu, draf.tanggal) : merk;", "const merkVarian = merk;"),
    'jenis beras varian tidak diwarisi': ("peta[x.varian] = jenisUntukMerk(x.induk); ubah = true;", "peta[x.varian] = ''; ubah = true;"),
    'nama varian tanpa pemisah titik tengah': ("if (m) return vrBersih(induk) + VR_PEMISAH + m;", "if (m) return vrBersih(induk) + ' ' + m;"),
    'terbit varian ikut membuang draf harga lain': ("const draf = Object.assign({}, (drafDok && drafDok.draf) || {}); const adaDraf = draf[nama + '|S'] !== undefined;", "const draf = {}; const adaDraf = true;"),
    'koreksi kedatangan ikut ditanya': ("const vr = !draf.id && terisi && !masalah ? vrPerluTanya(merk, harga) : { perlu: false };", "const vr = terisi && !masalah ? vrPerluTanya(merk, harga) : { perlu: false };"),
    'harga varian di bawah modal tanpa ketukan kedua': ("if (modal > 0 && n < modal - 0.5 && !yakin) return { tolak:", "if (false) return { tolak:"),
    'varian dari Harga menimpa nama yang sudah ada': ("if (vrAda(nama)) return { tolak: nama + ' sudah ada", "if (false) return { tolak: nama + ' sudah ada"),
    'induk varian baru menawarkan nama wadah / kelas': ("return (daftar || []).filter((m) => String(m).indexOf(VR_PEMISAH) < 0 && !kelas[m]);", "return (daftar || []).filter((m) => String(m).indexOf(VR_PEMISAH) < 0);"),
    'peringatan varian diam walau induk berstok tanpa harga': ("if ((perKg !== null && perKg > 0) || (utuh && utuh.perUnit > 0)) return '';", "return '';"),
    'peringatan varian berbunyi walau induk sudah berharga': ("if ((perKg !== null && perKg > 0) || (utuh && utuh.perUnit > 0)) return '';", "if (false) return '';"),
    # audit 39b no. 43
    'petunjuk varian tidak muncul (TH lahir jadi buku terpisah tanpa ditanya)': ("const saranVarian = baru ? ckSaranVarian(merkKetik) : [];", "const saranVarian = [];"),
    'saran varian peka huruf besar/kecil & spasi': ("const kunci = (x) => String(x).trim().replace(/\\s+/g, ' ').toLowerCase();", "const kunci = (x) => String(x);"),
    'saran varian menawarkan nama yang diarsipkan': ("&& !arsip[arKunciBeras(m)] && !bw[m] && !uk[m])", "&& !bw[m] && !uk[m])"),
    'saran varian menawarkan buku khusus wadah': ("&& !arsip[arKunciBeras(m)] && !bw[m] && !uk[m])", "&& !arsip[arKunciBeras(m)] && !uk[m])"),
    'saran varian menawarkan buku per ukuran': ("&& !arsip[arKunciBeras(m)] && !bw[m] && !uk[m])", "&& !arsip[arKunciBeras(m)] && !bw[m])"),
    'saran varian peka spasi ganda di tengah nama': ("const kunci = (x) => String(x).trim().replace(/\\s+/g, ' ').toLowerCase();", "const kunci = (x) => String(x).trim().toLowerCase();"),
    'nama sama beda huruf tidak ditawarkan (pita menunjuk varian saja)': ("const sama = (m) => m !== t && kunci(m) === k;", "const sama = (m) => false;"),
    'nama sama beda huruf tidak paling depan': ("sort((a, b) => b.s - a.s || b.bukuKg", "sort((a, b) => b.bukuKg"),
    'usul harga tanpa target untung': ("return modalKg > 0 ? vrBulatAtas(modalKg + (Number(a.targetPerKg) || 0), Number(a.bulatKarung) || 0) : 0;", "return modalKg > 0 ? vrBulatAtas(modalKg, Number(a.bulatKarung) || 0) : 0;"),
}


# audit 39b no. 43 — pemeriksaan statis stok.js (layar DOM tidak ikut kotak pasir). KG di gambarMasuk SUDAH membawa " kg":
# tombol "pakai <varian> · buku … kg" yang menambah " kg" lagi tercetak "buku 750 kg kg" (tertangkap screenshot 30 Sep).
def periksa43(t):
    kurang = ['stok.js tidak memuat ' + x for x in ['data-aksi="mPakaiVarian"', 'mPakaiVarian: ({ i, merk }) => ubahMasuk(', 'data-k="msv-${i}"', 'sudah dicatat sebagai <b>${b.saranVarian.map((v) => v.nama)'] if x not in t]
    i = t.find('function gambarMasuk('); j = t.find('\n  function ', i + 1) if i >= 0 else -1
    badan = t[i:j] if i >= 0 and j > i else ''
    if "const KG = (n) => DESIMAL(Math.round(n * 10) / 10) + ' kg';" not in badan: kurang.append('KG di gambarMasuk tidak lagi membawa satuan kg (periksa ulang tombol pakai varian)')
    elif "KG(v.bukuKg) + ' kg'" in badan or 'KG(v.bukuKg)}' + ' kg' in badan: kurang.append('tombol pakai varian mencetak satuan kg dua kali ("buku … kg kg")')
    if "' · buku ' + KG(v.bukuKg)" not in badan: kurang.append('tombol pakai varian tidak menyebut isi bukunya')
    return kurang

RUSAK_STATIS = {
    'satuan kg dobel di tombol pakai varian': ("' · buku ' + KG(v.bukuKg) : ''", "' · buku ' + KG(v.bukuKg) + ' kg' : ''"),
    'tombol pakai varian tanpa isi buku': ("' · buku ' + KG(v.bukuKg) : ''", "'' : ''"),
}

if __name__ == '__main__':
    js = uji_kunci_periode.satu_lingkup(bundel_baru.bundel(MODUL))   # putaran 30: teksMargin stok-hpp vs harga-logika
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        t43 = open(os.path.join(AKAR, 'baru/js/layar/stok.js'), encoding='utf-8').read()
        if periksa43(t43): print('KONTROL BASI  statis 39b no. 43 (stok.js asli sudah gagal: ' + ' | '.join(periksa43(t43)) + ')'); kode = 3
        for nama, (a, b) in RUSAK_STATIS.items():
            if t43.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(t43.count(a)) + '×)'); kode = 3; continue
            k = periksa43(t43.replace(a, b))
            print(('BERBUNYI ' if k else 'DIAM!!   ') + nama + ' → ' + (k[0][:140] if k else '-'))
            if not k: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    # audit 39b no. 43 — statis: pita "pakai itu?" & aksinya ada di layar Barang masuk (stok.js), satuan kg di tombolnya sekali saja
    t43 = open(os.path.join(AKAR, 'baru/js/layar/stok.js'), encoding='utf-8').read()
    kurang43 = periksa43(t43)
    if kurang43: g.append('statis 39b no. 43 · ' + ' | '.join(kurang43))
    else: l += 1
    print('VARIAN MEREK (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    if asap:
        print('ASAP DATA TOKO (%s): %d nama bermodal · beli ±3 %% ditanya: %s · beli +10 %% TIDAK ditanya: %s · %d varian dibuat · buku nama lama byte-sama: %s · jenis ikut induk: %s · %d nama kelas/wadah ditolak barang masuk (lolos: %s)'
              % (os.path.basename(cadangan_toko()), asap['nama'], ', '.join(asap['tanya3']) or 'tidak ada', ', '.join(asap['tanya10']) or 'tidak ada', asap['varian'], asap['lamaSama'], asap['jenisIkut'], asap['kelas'], ', '.join(asap['kelasLolos']) or 'tidak ada'))
        if asap['tanya3'] or asap['tanya10'] or asap['tolak'] or not asap['lamaSama'] or not asap['jenisIkut'] or asap['varian'] != asap['nama'] or asap['kelasLolos']: g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:300])
        # audit 39b no. 43: TH, SR, HSj, SB, II, MTJ (dikoreksi 28 Sep jadi nama varian) — diketik lagi di Barang masuk wajib ditawari variannya
        st43 = asap.get('saranToko') or []
        print('   39b no. 43 — saran satu ketukan untuk nama karung yang sudah jadi varian: ' + ' · '.join('%s → %s' % (n, ' / '.join(v) or 'TIDAK ADA') for n, v in st43))
        if not st43 or any(not v or not all(x.split(' \u00b7 ')[0].lower() == n.lower() for x in v) for n, v in st43): g.append('asap data toko (39b no. 43): ' + json.dumps(st43, ensure_ascii=False)[:300])
        print('   39b no. 43 tinjauan — nama berbuku diketik huruf kecil: %d diuji, buku aslinya paling depan di saran: %d%s' % (asap.get('hurufKecil', 0), asap.get('hurufKecil', 0) - len(asap.get('hurufSalah') or []), (' · SALAH: ' + ', '.join(asap['hurufSalah'])) if asap.get('hurufSalah') else ''))
        if not asap.get('hurufKecil') or asap.get('hurufSalah'): g.append('asap data toko (39b no. 43 huruf): ' + json.dumps(asap.get('hurufSalah'), ensure_ascii=False)[:300])
    sys.exit(2 if g else 0)
