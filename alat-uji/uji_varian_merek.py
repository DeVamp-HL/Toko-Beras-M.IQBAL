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
var KOL = ['batchMasuk', 'penjualan', 'katalogHargaKarung', 'pengaturan', 'aturanToko', 'hargaTerbit', 'produksiKemasan'];   // owner 7 Okt: + pindah buku varian
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
// ==== owner 7 Okt: varian dari Harga SESUDAH barangnya dicatat masuk atas nama induk (kejadian nyata: stok tetap di induk, varian kosong = stok BERCABANG)
pulih();
var nilaiStok = function () { var s = hitungStokKarungPerMerk(); return Math.round(Object.keys(s).reduce(function (a, m) { return a + s[m].sisaKg * s[m].hppTerakhirPerKg; }, 0)); };
var nilaiBatch = function () { return ambilSemuaBatch().reduce(function (a, b) { return a + (b.merkList || []).reduce(function (x, m) { return x + (Number(m.subtotalHarga) || 0); }, 0); }, 0); };
var T71 = vrSusunBuatDariHarga('Polos', 'Imperial', '15.000', W);
ok('7 Okt: induk Polos masih berstok 100 kg → varian dari Harga DITOLAK sampai dipilih (ikut / kosong); kalimat menyebut stok & kedatangannya', T71.perluBawa === true && /^Polos masih punya stok 100 kg \(datang 10 Sep 2026 · PEMASOK CONTOH · 2 karung\)\. Pilih dulu: stok itu IKUT jadi Polos · Imperial, atau varian kosong/.test(T71.tolak || ''), T71.tolak);
terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 'o71', tanggal: '2026-09-18', jam: '08:00', merk: 'Polos', kgSistem: 100, kgFisik: 0, selisihKg: -100, alasan: 'contoh', nilaiRp: 0 } }]);
var T71b = vrSusunBuatDariHarga('Polos', 'Imperial', '15.000', W); var kal71b = vrKalimatBawa('Polos', 'Polos · Imperial', '');
terapkanKeCache([{ koleksi: 'penyesuaianStok', hapus: 'o71' }]);
ok('7 Okt: induk TANPA stok (Polos dicocokkan jadi 0) tidak ditanya — varian langsung dibuat, buku tidak disentuh', !T71b.tolak && kal71b === '' && !T71b.dokumen.some(function (d) { return d.koleksi === 'batchMasuk' || d.koleksi === 'produksiKemasan'; }), J([T71b.tolak, kal71b]));
// bawa + buku UTUH (hanya kedatangan, belum ada yang keluar) → kedatangan DIKOREKSI jadi nama varian
var polosSt = stok('Polos'); var lain71 = J(['LL', 'IR64 LL', 'Kumala'].map(stok)); var nilai71 = nilaiStok(), batch71 = nilaiBatch();
var S72 = vrStokInduk('Polos'); var T72 = vrSusunBuatDariHarga('Polos', 'Imperial', '15.000', W, false, 'bawa');
var kb72 = (T72.dokumen || []).find(function (d) { return d.koleksi === 'batchMasuk'; }); var kk72 = (T72.dokumen || []).find(function (d) { return d.koleksi === 'katalogHargaKarung'; });
ok('7 Okt bawa + buku utuh: kedatangan b1 DIKOREKSI — hanya baris Polos jadi "Polos · Imperial" (baris lain, nilai, pemasok, tanggal tetap), alasan & riwayat koreksi tercatat; katalog varian bermodal harga beli Polos; tanpa pindah buku',
  S72.utuh === true && !T72.tolak && kb72 && kb72.data.id === 'b1' && J(kb72.data.merkList.map(function (m) { return m.merk; })) === J(['LL', 'IR64 LL', 'Kumala', 'Polos · Imperial']) && kb72.data.merkList[3].subtotalHarga === 1300000 && kb72.data.pemasok === 'PEMASOK CONTOH' && kb72.data.tanggal === '2026-09-10'
  && /jadi varian Polos · Imperial/.test(kb72.data.alasanKoreksi || '') && (kb72.data.riwayat || []).length === 1 && kk72 && kk72.data.merk === 'Polos · Imperial' && kk72.data.modalSaatSetel === 13000 && !(T72.dokumen || []).some(function (d) { return d.koleksi === 'produksiKemasan'; }) && /ikut: kedatangan 10 Sep 2026/.test(T72.patch.kabar), J([S72, T72]));
terapkan(T72);
ok('7 Okt sesudahnya: buku Polos · Imperial = 100 kg dengan modal & harga beli Polos yang lama; buku Polos HILANG (tidak bercabang); buku lain, nilai stok & nilai kedatangan BYTE-SAMA',
  stok('Polos · Imperial').sisaKg === 100 && stok('Polos · Imperial').hppTerakhirPerKg === polosSt.hppTerakhirPerKg && stok('Polos · Imperial').hargaTerakhirPerKg === polosSt.hargaTerakhirPerKg && !hitungStokKarungPerMerk()['Polos'] && J(['LL', 'IR64 LL', 'Kumala'].map(stok)) === lain71 && nilaiStok() === nilai71 && nilaiBatch() === batch71, J([stok('Polos · Imperial'), polosSt]));
ok('7 Okt: barang masuk berikutnya diketik "Polos" → ditawari Polos · Imperial (satu ketukan, audit 43)', J(hitungMasuk(draf([brs('Polos', 1, 13000)])).baris[0].saranVarian.map(function (v) { return v.nama; })) === J(['Polos · Imperial']));
pulih();
// bawa + buku sudah BERGERAK (LL terjual 50 kg) → buku varian lahir + pindah buku seluruh sisa, modal ikut; kedatangan lama tetap
var ll73 = stok('LL'); var nilai73 = nilaiStok(); var S73 = vrStokInduk('LL');
var T73 = vrSusunBuatDariHarga('LL', 'Gold', '15.500', W, false, 'bawa');
var lahir73 = (T73.dokumen || []).find(function (d) { return d.koleksi === 'batchMasuk' && d.data.lahirBuku; }); var pd73 = (T73.dokumen || []).find(function (d) { return d.koleksi === 'produksiKemasan'; });
ok('7 Okt bawa + buku sudah bergerak (LL terjual 50 kg): buku "LL · Gold" LAHIR (batch 0 kg) + PINDAH BUKU 450 kg LL → LL · Gold (jadi-karung-utuh, modal LL, bertanda jadiVarian); kedatangan b1 TIDAK dikoreksi; katalog bermodal harga beli LL',
  S73.utuh === false && /terjual/.test(S73.sebab) && !T73.tolak && lahir73 && lahir73.data.merkList[0].merk === 'LL · Gold' && pd73 && pd73.data.jadiKarungUtuh === true && pd73.data.merkTujuan === 'LL · Gold' && J(pd73.data.sumberList) === J([{ merk: 'LL', kg: 450 }]) && pd73.data.jadiVarian.induk === 'LL'
  && !(T73.dokumen || []).some(function (d) { return d.koleksi === 'batchMasuk' && d.data.id === 'b1'; }) && ((T73.dokumen || []).find(function (d) { return d.koleksi === 'katalogHargaKarung'; }) || { data: {} }).data.modalSaatSetel === 14000, J([S73, T73]));
terapkan(T73);
ok('7 Okt sesudahnya: LL 0 kg, LL · Gold 450 kg @ modal LL; nilai stok seluruh toko BYTE-SAMA (laba tidak bergeser)', stok('LL').sisaKg === 0 && stok('LL · Gold').sisaKg === 450 && Math.abs(stok('LL · Gold').hppTerakhirPerKg - ll73.hppTerakhirPerKg) < 1e-9 && nilaiStok() === nilai73, J([stok('LL'), stok('LL · Gold')]));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'j73', tanggal: '2026-09-19', jam: '11:00', jenis: 'karung', merkSumber: 'LL · Gold', totalKg: 50, jumlahKarung: 1, beratKarungAcuan: 50, hargaTotal: 775000, hppTotalSaatJual: 700000, caraBayar: 'Tunai' } }]);
ok('7 Okt: penjualan atas nama LL · Gold sesudahnya MEMOTONG bukunya (450 → 400) — buku varian lahir lewat batch', stok('LL · Gold').sisaKg === 400, J(stok('LL · Gold')));
pulih();
ok('7 Okt: modal varian yang ikut = modal induk → harga 13.000 di bawah modal LL 14.000 minta ketukan kedua; varian kosong (tanpa modal) langsung', vrSusunBuatDariHarga('LL', 'Gold', '13.000', W, false, 'bawa').perluYakin === true && !vrSusunBuatDariHarga('LL', 'Gold', '13.000', W, false, 'kosong').tolak);
// kosong = dipilih sadar: buku induk tidak disentuh
var ll74 = J(stok('LL')); var T74 = vrSusunBuatDariHarga('LL', 'Gold', '15.500', W, false, 'kosong'); terapkan(T74);
ok('7 Okt kosong (dipilih sadar): katalog varian saja, buku LL BYTE-SAMA, kabar menyebut stok LL tetap atas namanya', !T74.tolak && !(T74.dokumen || []).some(function (d) { return d.koleksi === 'batchMasuk' || d.koleksi === 'produksiKemasan'; }) && J(stok('LL')) === ll74 && !hitungStokKarungPerMerk()['LL · Gold'] && /tetap atas nama LL \(dipilih: varian kosong\)/.test((T74.patch || {}).kabar || ''), T74.patch && T74.patch.kabar);
// varian yang SUDAH ADA dengan buku kosong + induk berstok (bentuk stok bercabang yang terlanjur): hanya pindah stok, katalog tidak diubah
var T77 = vrSusunBuatDariHarga('LL', 'Gold', '15.500', W); var T77b = vrSusunBuatDariHarga('LL', 'Gold', '99.000', W, false, 'bawa');
ok('7 Okt: varian LL · Gold SUDAH ADA (buku kosong) & LL berstok → bukan "sudah ada" mentah: wajib "ikut"; ikut = pindah buku 450 kg saja, TANPA dokumen katalog / terbit (harga tidak diubah)',
  vrBisaIkutKeAda('LL', 'LL · Gold') === true && T77.perluBawa === true && T77.sudahAda === true && !T77b.tolak && !T77b.dokumen.some(function (d) { return d.koleksi === 'katalogHargaKarung' || d.koleksi === 'hargaTerbit'; })
  && T77b.dokumen.some(function (d) { return d.koleksi === 'produksiKemasan' && d.data.merkTujuan === 'LL · Gold' && d.data.kgDipakai === 450; }) && /sudah ada — tidak dibuat ulang, harganya tidak diubah/.test((T77b.patch || {}).kabar || ''), J([T77.tolak, T77b]));
var stG = denganCacheSementara(T77b.dokumen, function () { return [stok('LL').sisaKg, stok('LL · Gold').sisaKg, nilaiStok()]; });
ok('7 Okt: ... diterapkan: LL 0 kg, LL · Gold 450 kg, nilai stok sama', stG[0] === 0 && stG[1] === 450 && stG[2] === nilaiStok(), J(stG));
// barang masuk: "LL" berbuku padahal ada varian LL · Gold → pita "yang mana?" (tidak memblokir)
var H75 = hitungMasuk(draf([brs('LL', 2, 14000), brs('Kumala', 1, 14000), brs('LL', 1, 14000, { varian: 'sama' })]));
ok('7 Okt barang masuk: "LL" (berbuku) padahal ada varian LL · Gold → pita "yang mana?" (varianInduk), tidak memblokir; Kumala tanpa varian, baris yang sudah dijawab "sama", dan koreksi kedatangan tidak ditawari',
  J(H75.baris[0].varianInduk) === J([{ nama: 'LL · Gold', bukuKg: 0 }]) && !H75.baris[0].saranVarian.length && !H75.baris[1].varianInduk.length && !H75.baris[2].varianInduk.length && !hitungMasuk(draf([brs('LL', 2, 14000)], { id: 'b1' })).baris[0].varianInduk.length && !susunSimpanMasuk(draf([brs('LL', 2, 14000)]), W, true).tolak, J(H75.baris.map(function (b) { return [b.merk, b.varianInduk]; })));
var R75 = susunSimpanMasuk(draf([brs('LL · Gold', 2, 15000)]), W, true); terapkan(R75);
ok('7 Okt sesudah "masuk LL · Gold": kedatangan tercatat di buku varian (100 kg), buku LL tidak bertambah', !R75.tolak && stok('LL · Gold').sisaKg === 100 && J(stok('LL')) === ll74, J([R75.tolak, stok('LL · Gold')]));
ok('7 Okt: varian yang sudah BERISI tidak menerima stok induk (tetap "sudah ada — ubah harganya")', vrBisaIkutKeAda('LL', 'LL · Gold') === false && /sudah ada — ubah harganya/.test(vrSusunBuatDariHarga('LL', 'Gold', '15.500', W, false, 'bawa').tolak || ''));
pulih();
// kedatangan induk di bulan TERKUNCI → tidak dikoreksi; stok ikut lewat pindah buku bertanggal hari ini
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'b8', tanggal: '2026-08-20', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ id: '1', merk: 'Lawas', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 12000, subtotalHarga: 1200000 }] } },
  { koleksi: 'aturanToko', data: { id: 'kunciPeriode', sampaiBulan: '2026-08', riwayat: [] } }]);
var S76 = vrStokInduk('Lawas'); var T76 = vrSusunBuatDariHarga('Lawas', 'Baru', '14.000', W, false, 'bawa');
ok('7 Okt: kedatangan induk di bulan TERKUNCI → tidak dikoreksi; stok ikut lewat pindah buku bertanggal hari ini', S76.utuh === false && /dikunci/.test(S76.sebab) && !T76.tolak && T76.dokumen.some(function (d) { return d.koleksi === 'produksiKemasan' && d.data.merkTujuan === 'Lawas · Baru' && d.data.tanggal === '2026-09-19'; }) && !T76.dokumen.some(function (d) { return d.koleksi === 'batchMasuk' && d.data.id === 'b8'; }), J([S76, T76.tolak]));
pulih();
// ---- 10 · varian dari layar Harga (sebelum barang datang) — owner 7 Okt: Kumala masih berstok, jadi pilihan "varian kosong" disebut tegas
var B10 = vrSusunBuatDariHarga('Kumala', 'Super', '15.000', W, false, 'kosong');
ok('varian dari Harga: "Kumala · Super" (dipilih: varian kosong) — katalog per kg terbit + jenis ikut Kumala (IR64); ditolak: induk tak dikenal, mutu kosong, nama yang sudah ada',
  !B10.tolak && B10.dokumen.some(function (d) { return d.koleksi === 'katalogHargaKarung' && d.data.merk === 'Kumala · Super' && d.data.hargaPerKg === 15000; }) && B10.dokumen.some(function (d) { return d.koleksi === 'pengaturan' && d.data.peta['Kumala · Super'] === 'IR64'; })
  && !!vrSusunBuatDariHarga('Tak Ada', 'X', '15.000', W).tolak && !!vrSusunBuatDariHarga('Kumala', '', '15.000', W).tolak && (terapkan(B10), /sudah ada/.test(vrSusunBuatDariHarga('Kumala', 'Super', '15.000', W, false, 'kosong').tolak || '')), J(B10));
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
  // owner 7 Okt: tiap merek berstok di data toko → varian dari Harga dengan stok IKUT, diterapkan di cache SEMENTARA (tidak ditulis): buku varian = sisa induk,
  // modal sama, buku induk kosong/hilang, nilai stok seluruh toko byte-sama; buku utuh → koreksi kedatangan, selain itu pindah buku. + keadaan FJN (kejadian nyata).
  var bawa7 = { utuh: 0, pindah: 0, salah: [], fjn: null, koreksi: 0 };
  (function () { var s0 = hitungStokKarungPerMerk(); var kls = wbNamaKelas(); var bm = Object.assign({}, petaUkuran(), petaBukuWadah());
    var nilai = function (s) { return Object.keys(s).reduce(function (a, m) { return a + s[m].sisaKg * s[m].hppTerakhirPerKg; }, 0); }; var n0 = nilai(s0);
    var WC7 = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
    Object.keys(s0).filter(function (m) { return s0[m].sisaKg > 0.004 && m.indexOf('·') < 0 && !kls[m] && !bm[m] && !arBeras(m); }).forEach(function (m) {
      var S = vrStokInduk(m); var T = vrSusunBuatDariHarga(m, 'Asap', '99.000', WC7, true, 'bawa'); var v = m + ' · Asap';
      if (T.tolak) { bawa7.salah.push(m + ': ' + T.tolak.slice(0, 80)); return; }
      denganCacheSementara(T.dokumen.filter(function (d) { return d.koleksi === 'batchMasuk' || d.koleksi === 'produksiKemasan'; }), function () { var s1 = hitungStokKarungPerMerk(); var sv = s1[v] || { sisaKg: NaN, hppTerakhirPerKg: NaN };
        if (!(Math.abs(sv.sisaKg - S.sisa) <= 0.01)) bawa7.salah.push(m + ': sisa varian ' + sv.sisaKg + ' vs ' + S.sisa);
        if (!(Math.abs(sv.hppTerakhirPerKg - s0[m].hppTerakhirPerKg) <= 0.01)) bawa7.salah.push(m + ': modal varian');
        if (S.utuh ? !!s1[m] : !(Math.abs(s1[m].sisaKg) <= 0.01)) bawa7.salah.push(m + ': induk masih berisi');
        if (!(Math.abs(nilai(s1) - n0) <= 1)) bawa7.salah.push(m + ': nilai stok bergeser'); });
      if (S.utuh) bawa7.utuh += 1; else bawa7.pindah += 1; });
    // jalur KOREKSI KEDATANGAN di data toko: salinan kedatangan nyata terbaru dengan SATU baris nama baru (belum bergerak) → stok ikut → kedatangan itu dikoreksi:
    // buku varian = buku induk tadi, induk hilang, nilai stok & total bon pemasok (mesin beku) tidak berubah
    var bt = ambilSemuaBatch().filter(function (b) { return !b.stokAwal && !b.tutupBuku && !b.lahirBuku && (b.merkList || []).some(function (m) { return m.bentuk !== 'bal'; }); }).sort(function (x, y) { return String(y.tanggal).localeCompare(String(x.tanggal)); })[0];
    if (bt) { var klon = JSON.parse(J(bt)); klon.id = 'asap7'; klon.merkList = [Object.assign({}, klon.merkList.filter(function (m) { return m.bentuk !== 'bal'; })[0], { id: '1', merk: 'Asap Induk' })];
      denganCacheSementara([{ koleksi: 'batchMasuk', data: klon }], function () { var sA = hitungStokKarungPerMerk(); var nA = nilai(sA); var uA = hitungUtangPemasok().reduce(function (a, x) { return a + x.totalUtang; }, 0);
        var S = vrStokInduk('Asap Induk'); var T = vrSusunBuatDariHarga('Asap Induk', 'Asap', '99.000', WC7, true, 'bawa');
        if (!S.utuh || T.tolak) { bawa7.salah.push('salinan kedatangan tidak utuh: ' + (S.sebab || T.tolak)); return; }
        denganCacheSementara(T.dokumen.filter(function (d) { return d.koleksi === 'batchMasuk' || d.koleksi === 'produksiKemasan'; }), function () { var sB = hitungStokKarungPerMerk(); var vB = sB['Asap Induk · Asap'];
          var uB = hitungUtangPemasok().reduce(function (a, x) { return a + x.totalUtang; }, 0);
          if (!vB || J(vB) !== J(sA['Asap Induk']) || sB['Asap Induk'] || Math.abs(nilai(sB) - nA) > 1 || uB !== uA || T.dokumen.some(function (d) { return d.koleksi === 'produksiKemasan'; })) bawa7.salah.push('koreksi kedatangan di data toko: ' + J([vB, sA['Asap Induk'], uA, uB]));
          else bawa7.koreksi = 1; }); }); }
    if (s0['FJN']) { var f = vrStokInduk('FJN'); var kat = ambilHargaKarung().filter(function (h) { return /^FJN · /.test(h.merk); }).map(function (h) { return h.merk; });
      var vi = hitungMasuk(draf([brs('FJN', 1, 1)], { tanggal: TGL_CAD })).baris[0].varianInduk.map(function (v) { return v.nama; });
      bawa7.fjn = { sisa: f.sisa, datang: f.datang.length, utuh: f.utuh, sebab: f.sebab, katalogVarian: kat, ditawari: vi };
      if (kat.some(function (k) { return vi.indexOf(k) < 0; })) bawa7.salah.push('FJN diketik di barang masuk tidak menawarkan variannya: ' + kat.join(', ')); }
  })();
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
  asap = { bawa7: bawa7, hurufKecil: hurufKecil.length, hurufSalah: hurufSalah, saranToko: saranToko, nama: nama.length, tanya3: tanya3, tanya10: tanya10, tolak: R.tolak || '', lamaSama: lamaSama, jenisIkut: jenisIkut, varian: Object.keys(st1).filter(function (m) { return / · Uji$/.test(m); }).length, kelas: namaKelas.length, kelasLolos: kelasLolos };
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
    'varian dari Harga menimpa nama yang sudah ada': ("if (vrAda(nama)) {", "if (false) {"),   # owner 7 Okt: penolakan "sudah ada" kini di dalam blok nama-sudah-ada
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
    # owner 7 Okt: varian dari Harga sesudah barangnya masuk atas nama induk — stok tidak boleh bercabang diam-diam
    '7 Okt: varian dari Harga tidak bertanya walau induk berstok': ("if (S.sisa > 0.004 && !pilih) return { tolak:", "if (false) return { tolak:"),
    '7 Okt: stok induk tidak ikut walau dipilih "ikut"': ("const ikut = S.sisa > 0.004 && pilih === 'bawa';", "const ikut = false;"),
    '7 Okt: koreksi kedatangan mengganti SEMUA baris (bukan nama induk saja)': ("(x && x.merk === ind && x.bentuk !== 'bal' ? Object.assign({}, x, { merk: nama }) : x)", "(x ? Object.assign({}, x, { merk: nama }) : x)"),
    '7 Okt: buku induk yang sudah terjual tetap dikoreksi (bukan pindah buku)': ("const dipakai = !!ind && (", "const dipakai = false && ("),
    '7 Okt: pindah buku tanpa buku lahir (penjualan varian tidak terpotong)': ("const lahir = wbDokLahir([{ merk: nama }], w); if (lahir) dokumen.push(lahir);", ""),
    '7 Okt: varian yang sudah ada & kosong tidak bisa menerima stok induk': ("if (!vrBisaIkutKeAda(ind, nama)) return { tolak: nama + ' sudah ada", "if (true) return { tolak: nama + ' sudah ada"),
    '7 Okt: varian yang sudah BERISI ikut menerima stok induk': ("return !(sv && Math.abs(Number(sv.sisaKg) || 0) > 0.004) && vrStokInduk(induk).sisa > 0.004;", "return vrStokInduk(induk).sisa > 0.004;"),
    '7 Okt: varian yang sudah ada ikut diterbitkan ulang harganya': ("return { dokumen: P0.dokumen, patch:", "return { dokumen: P0.dokumen.concat(vrSusunTerbitHarga(nama, hargaKetik, w, true).dokumen || []), patch:"),
    '7 Okt: modal varian yang ikut dibaca dari buku varian yang masih kosong': ("const r = vrSusunTerbitHarga(nama, hargaKetik, w, yakin, ikut ? ind : '');", "const r = vrSusunTerbitHarga(nama, hargaKetik, w, yakin, '');"),
    '7 Okt: kedatangan di bulan terkunci tetap dikoreksi': ("const t = tolakKunci('batchMasuk', b, ''); if (t && !terkunci) terkunci = t;", ""),
    '7 Okt: pita "punya varian — yang mana?" di Barang masuk tidak muncul': ("const varianInduk = !draf.id && !baru", "const varianInduk = false && !draf.id && !baru"),
    '7 Okt: pita "punya varian" muncul juga di koreksi kedatangan': ("const varianInduk = !draf.id && !baru", "const varianInduk = !baru"),
    '7 Okt: pita "punya varian" muncul walau baris sudah dijawab sama / beda mutu': ("&& !!merk && !pilih && merk.indexOf", "&& !!merk && merk.indexOf"),
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

# owner 7 Okt — statis harga.js & stok.js (layar DOM tidak ikut kotak pasir): pilihan "stok induk ikut / varian kosong" diteruskan ke logika, pita "punya varian" ada
def periksa7okt(th, ts):
    kurang = ['harga.js tidak memuat ' + x for x in ['data-aksi="vrBawa" data-v="bawa"', 'data-aksi="vrBawa" data-v="kosong"', 'st().vrYakin, b.bawa);', 'blUbahG: ({ p, g, arah })', 'data-aksi="blKetukG"'] if x not in th]
    kurang += ['stok.js tidak memuat ' + x for x in ['data-k="mvi-${i}"', 'b.varianInduk.map((v) => h`<div class="kaca-btn aktif emas" data-aksi="mPakaiVarian"'] if x not in ts]
    return kurang

RUSAK_STATIS_7 = {
    'pilihan ikut/kosong tidak diteruskan ke logika': ('harga', "st().vrYakin, b.bawa);", "st().vrYakin);"),
    'pita "punya varian" di Barang masuk hilang': ('stok', 'data-k="mvi-${i}"', 'data-k="mvi-x"'),
}

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
        th7 = open(os.path.join(AKAR, 'baru/js/layar/harga.js'), encoding='utf-8').read()
        if periksa7okt(th7, t43): print('KONTROL BASI  statis 7 Okt (berkas asli sudah gagal: ' + ' | '.join(periksa7okt(th7, t43)) + ')'); kode = 3
        for nama, (berkas, a, b) in RUSAK_STATIS_7.items():
            asal = th7 if berkas == 'harga' else t43
            if asal.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(asal.count(a)) + '×)'); kode = 3; continue
            k = periksa7okt(asal.replace(a, b), t43) if berkas == 'harga' else periksa7okt(th7, asal.replace(a, b))
            print(('BERBUNYI ' if k else 'DIAM!!   ') + nama + ' → ' + (k[0][:140] if k else '-'))
            if not k: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    # audit 39b no. 43 — statis: pita "pakai itu?" & aksinya ada di layar Barang masuk (stok.js), satuan kg di tombolnya sekali saja
    t43 = open(os.path.join(AKAR, 'baru/js/layar/stok.js'), encoding='utf-8').read()
    kurang43 = periksa43(t43)
    if kurang43: g.append('statis 39b no. 43 · ' + ' | '.join(kurang43))
    else: l += 1
    kurang7 = periksa7okt(open(os.path.join(AKAR, 'baru/js/layar/harga.js'), encoding='utf-8').read(), t43)
    if kurang7: g.append('statis 7 Okt · ' + ' | '.join(kurang7))
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
        b7 = asap.get('bawa7') or {}
        print('   7 Okt — varian dari Harga dengan stok induk IKUT (cache sementara): %d merek berstok · %d lewat koreksi kedatangan (buku utuh) · %d lewat pindah buku · salinan kedatangan nyata terbaru lewat koreksi: %s · buku varian = sisa & modal induk, nilai stok & total bon sama: %s%s'
              % (b7.get('utuh', 0) + b7.get('pindah', 0), b7.get('utuh', 0), b7.get('pindah', 0), 'lulus' if b7.get('koreksi') else 'TIDAK', 'ya' if not b7.get('salah') else 'TIDAK — ' + '; '.join(b7['salah'][:5]),
                 (' · FJN: sisa buku %s kg, %d kedatangan, %s; varian di katalog %s; diketik di Barang masuk → ditawari %s' % (b7['fjn']['sisa'], b7['fjn']['datang'], 'utuh' if b7['fjn']['utuh'] else 'tidak utuh (' + b7['fjn']['sebab'] + ')', ', '.join(b7['fjn']['katalogVarian']) or '-', ', '.join(b7['fjn']['ditawari']) or '-')) if b7.get('fjn') else ''))
        if b7.get('salah') or not (b7.get('utuh', 0) + b7.get('pindah', 0)) or not b7.get('koreksi'): g.append('asap data toko (7 Okt varian bawa): ' + json.dumps(b7, ensure_ascii=False)[:400])
    sys.exit(2 if g else 0)
