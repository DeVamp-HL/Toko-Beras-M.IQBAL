#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jual_baru.py — uji logika layar JUAL sistem baru (baru/js/layar/jual-logika.js) di jsc, tanpa peramban.
Data = KOTAK PASIR kecil (ANGKA CONTOH) supaya bisa jalan di CI; kalau ada backup-batch-*.json lokal,
ditambah uji asap atas data toko (rak terisi, tidak melempar).

    python3 alat-uji/uji_jual_baru.py            → 0 lulus · 2 gagal
    python3 alat-uji/uji_jual_baru.py --kontrol  → kontrol positif: logika yang dirusak wajib ketahuan
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/jual-logika.js']

# KOTAK PASIR — angka contoh, bukan angka toko
KOTAK = {
  'batchMasuk': [
    {'id': 'b1', 'tanggal': '2026-09-01', 'caraBayar': 'utang', 'biayaBongkar': 100000, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'totalKg': 500, 'subtotalHarga': 6500000, 'hargaPerKg': 13000},
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 25, 'totalKg': 250, 'subtotalHarga': 3300000, 'hargaPerKg': 13200},
      {'merk': 'IR64 Apex', 'satuan': 'karung', 'beratKarung': 50, 'totalKg': 300, 'subtotalHarga': 4200000, 'hargaPerKg': 14000}]},
  ],
  'katalogHargaKarung': [{'id': 'hk1', 'merk': 'Angsa', 'hargaPerKg': 13800}, {'id': 'hk2', 'merk': 'IR64 Apex', 'hargaPerKg': 14600}],
  'katalogHargaKemasan': [{'id': 'hm1', 'merk': 'Kembang', 'ukuran': 5, 'hargaPerUnit': 72000}, {'id': 'hm2', 'merk': 'Angsa', 'ukuran': 25, 'hargaPerUnit': 340000}],
  'katalogHargaLiteran': [{'id': 'hl1', 'merk': 'Angsa', 'hargaPerLiter': 13500}],
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-09-02', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 40, 'hppPerUnit': 66000, 'merkSumber': 'IR64 Apex', 'kgDipakai': 200}],
  'stokBahanLiteran': [{'id': 'l1', 'tanggal': '2026-09-01', 'jenis': 'paperbag5l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 30500},
                       {'id': 'l2', 'tanggal': '2026-09-01', 'jenis': 'paperbag10l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 39500}],
  'penjualan': [
    {'id': 's1', 'tanggal': '2026-09-19', 'jam': '08:10', 'caraBayar': 'Tunai', 'namaPelanggan': 'Bu Suti', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 2, 'totalKg': 10, 'hargaTotal': 144000, 'hppTotalSaatJual': 132000, 'grupNota': 'g1'},
    {'id': 's2', 'tanggal': '2026-09-19', 'jam': '09:00', 'caraBayar': 'Kredit', 'namaPelanggan': 'Deka', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 690000, 'hppTotalSaatJual': 660000, 'grupNota': 'g2'},
    {'id': 's3', 'tanggal': '2026-09-18', 'jam': '10:00', 'caraBayar': 'Tunai', 'namaPelanggan': 'Bu Suti', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': 72000, 'hppTotalSaatJual': 66000, 'grupNota': 'g3'},
    {'id': 's4', 'tanggal': '2026-09-19', 'jam': '11:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'literan', 'merkSumber': 'Angsa', 'jumlahLiter': 3, 'totalKg': 2.46, 'hargaTotal': 40500, 'hppTotalSaatJual': 32000, 'grupNota': 'g4', 'dibatalkan': True},
  ],
  'piutangMutasi': [{'id': 'm1', 'tanggal': '2026-08-20', 'namaPelanggan': 'Deka', 'tipe': 'saldoAwal', 'nominal': 200000}],
  'pelangganCatatan': [{'id': 'bu suti', 'nama': 'Bu Suti', 'catatan': 'warung depan pasar'}],
}

SKENARIO = r"""
var gagal = [], lulus = 0;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + ket : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, KOTAK[n]); });
setelSumber('cadangan', 'kotak pasir');
var s = keadaanAwal(); s.sekarang = new Date('2026-09-19T10:00:00');
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); return p; }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }

// ---- rak dibaca dari mesin (bukan hitungan sendiri)
var rak = susunRak(s);
ok('rak karung: Angsa 50 & 25, Apex 50 — tiga chip berharga', rak.karung.length === 3 && rak.karung.map(function (c) { return c.nama + c.berat; }).join() === 'Angsa50,Angsa25,IR64 Apex50', JSON.stringify(rak.karung.map(function (c) { return c.nama + c.berat; })));
ok('harga karung Angsa 25 dari katalog KEMASAN (menang atas per kg): 340.000; Angsa 50 = 13.800 × 50', chip('karung', 'Angsa', 25).harga === 340000 && chip('karung', 'Angsa', 50).harga === 690000, chip('karung', 'Angsa', 50).harga);
ok('sisa Angsa: (750 − 50 terjual) / 50 = 14 karung; per 25 = 28', chip('karung', 'Angsa', 50).sisa === 14 && chip('karung', 'Angsa', 25).sisa === 28, chip('karung', 'Angsa', 50).sisa + '/' + chip('karung', 'Angsa', 25).sisa);
ok('kemasan Kembang 5: 40 dibuat − 3 terjual = 37, harga 72.000', rak.kemasan.length === 1 && rak.kemasan[0].sisa === 37 && rak.kemasan[0].harga === 72000, JSON.stringify(rak.kemasan));
ok('literan Angsa 13.500/L, sisa ±853 L (700 kg / 0,82)', rak.literan.length === 1 && rak.literan[0].harga === 13500 && rak.literan[0].sisa === 853.6, JSON.stringify(rak.literan));
ok('sering tanpa nama = yang laku 28 hari (Kembang 5 kg 2×, Angsa 50 1×; yang dibatalkan tidak dihitung)', rak.sering.length === 2 && rak.sering[0].nama === 'Kembang' && rak.sering[0].kali === 2, JSON.stringify(rak.sering.map(function (c) { return c.nama + ':' + c.kali; })));
terap({ pelanggan: 'bu suti' }); ok('sering untuk Bu Suti (kunci nama tak peduli huruf besar): Kembang 5 kg 2×', susunRak(s).sering.length === 1 && susunRak(s).sering[0].kali === 2); terap({ pelanggan: '' });

// ---- keranjang: ketuk chip → jumlah → masuk
terap(ketukChip(s, chip('karung', 'Angsa', 50))); ok('ketuk chip membuka lembar jumlah', s.lembar === 'jumlah' && s.pilih.kunci === 'Angsa');
terap(tekanTuts(s, '2')); terap(masukkan(s));
ok('2 karung Angsa 50 masuk: hargaTotal 1.380.000, totalKg 100, hpp dari mesin', s.keranjang.length === 1 && s.keranjang[0].trx.hargaTotal === 1380000 && s.keranjang[0].trx.totalKg === 100 && s.keranjang[0].trx.hppTotalSaatJual > 0 && s.keranjang[0].trx.jenis === 'karung', JSON.stringify(s.keranjang[0]));
ok('sesudah masuk, chip Angsa 50 bebas tinggal 12 (langit-langit ikut keranjang aktif)', chip('karung', 'Angsa', 50).sisa === 12, chip('karung', 'Angsa', 50).sisa);
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '13' }); var p = masukkan(s);
ok('minta 13 padahal bebas 12 → DITOLAK, kalimat menyebut yang bebas', s.keranjang.length === 1 && /bebas dijual sekarang 12 karung/.test(p.kabar) && p.kabarAwas, p.kabar); terap(p);
terap({ ketik: '1,5' }); terap(masukkan(s)); ok('1,5 karung boleh (setengah sack) → baris kedua 75 kg', s.keranjang.length === 2 && s.keranjang[1].trx.totalKg === 75, JSON.stringify(s.keranjang.map(function (b) { return b.trx.totalKg; })));
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '0,3' }); p = masukkan(s); ok('0,3 karung ditolak (bukan kelipatan setengah)', s.keranjang.length === 2 && /setengah/.test(p.kabar), p.kabar); terap({ lembar: null, pilih: null, ketik: '' });

// ---- tagihan & pembulatan (Tunai + Bon dibulatkan, QRIS persis)
terap({ keranjang: [], potongan: 0 }); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '1,3' }); terap(masukkan(s));
var t = hitungTagihan(s);
ok('1,3 L × 13.500 = 17.550 → tunai ditagih 18.000 (bulat +450)', t.subtotal === 17550 && t.bulat === 450 && t.total === 18000, JSON.stringify(t));
ok('literan 1,3 L: totalKg = 1,3 × 0,82 = 1,066; di bawah 5 L tanpa kantong', s.keranjang[0].trx.totalKg === 1.066 && !s.keranjang[0].trx.kemasanLiteran, JSON.stringify(s.keranjang[0].trx));
terap(pilihCara(s, 'Kredit')); t = hitungTagihan(s); ok('BON ikut dibulatkan: 18.000', t.total === 18000 && t.bulat === 450);
terap(pilihCara(s, 'QRIS')); t = hitungTagihan(s); ok('QRIS persis 17.550', t.total === 17550 && t.bulat === 0);
terap(pilihCara(s, 'Tunai')); terap(setelPotongan(s, 2550)); t = hitungTagihan(s); ok('potongan 2.550 → bersih 15.000, pas bulat, total 15.000', t.potongan === 2550 && t.bersih === 15000 && t.bulat === 0 && t.total === 15000, JSON.stringify(t));
terap(setelPotongan(s, 99999999)); ok('potongan dijepit ke subtotal (tidak bisa minus)', hitungTagihan(s).potongan === 17550); terap(setelPotongan(s, 0));

// ---- literan ≥ 5 L membawa kantong (biaya masuk HPP, bukan harga)
terap({ keranjang: [] }); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '6' }); terap(masukkan(s));
ok('6 L: kantong 10 L × 1 masuk HPP (395), harga tetap 6 × 13.500', s.keranjang[0].trx.kemasanLiteran === 'paperbag10l' && s.keranjang[0].trx.biayaKemasanLiteran === 395 && s.keranjang[0].trx.hargaTotal === 81000 && s.keranjang[0].trx.hppTotalSaatJual - Math.round(chip('literan', 'Angsa').hppPerKg * s.keranjang[0].trx.totalKg) === 395, JSON.stringify(s.keranjang[0].trx));

// ---- uang, kembalian, kurang → sisa jadi bon
terap({ keranjang: [] }); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '3' }); terap(masukkan(s)); // 216.000
terap(tambahUang(s, 100000)); terap(tambahUang(s, 100000)); t = hitungTagihan(s);
ok('bayar 200.000 dari 216.000 → kurang 16.000, sisa jadi bon', t.kurang === 16000 && t.sisaJadiBon === true && t.kembalian === 0, JSON.stringify(t));
ok('tanpa nama: nota DITAHAN, alasannya sisa jadi bon', /sisanya jadi bon/.test(alasanTolak(s)), alasanTolak(s));
terap({ pelanggan: 'Deka' }); ok('ada nama: sah', alasanTolak(s) === '');
ok('nama ada → simpanNota sah (dokumen tersusun)', !simpanNota(s, { tanggal: '2026-09-19', jam: '10:00', idUnik: function () { return 1; } }).tolak);
terap(uangPas(s)); t = hitungTagihan(s); ok('PAS → kembalian 0, tidak kurang', t.uang === 216000 && t.kembalian === 0 && t.kurang === 0);
terap({ uang: 0 }); terap(tambahUang(s, 100000)); terap(tambahUang(s, 100000)); terap(tambahUang(s, 20000)); ok('220.000 → kembalian 4.000', hitungTagihan(s).kembalian === 4000);
terap({ uang: 0 }); ok('tunai tanpa uang diterima ditolak', /uang yang diterima/.test(alasanTolak(s)));
terap(pilihCara(s, 'Kredit')); terap({ pelanggan: '' }); ok('bon tanpa nama ditolak', /nama/.test(alasanTolak(s))); terap({ pelanggan: 'Deka' }); ok('bon Deka dikunci KR1 — belum terdaftar di buku Pelanggan', /belum terdaftar/.test(alasanTolak(s)), alasanTolak(s)); terap({ kreditDibuka: true }); ok('owner buka kredit sekali → sah', alasanTolak(s) === ''); terap({ kreditDibuka: false });
var info = infoPelanggan('Deka'); ok('info kredit Deka: sisa bon 890.000 (saldo awal 200.000 + kredit 690.000), rata 90 hari dari mesin', info.sisa === 890000 && info.rataBulanan === 230000, JSON.stringify(info));

// ---- nego
terap(pilihCara(s, 'Tunai')); var id = s.keranjang[0].id;
p = terapkanNego(s, id, 200); ok('nego di bawah lantai Rp500 ditolak', /paling rendah Rp500/.test(p.kabar) && s.keranjang[0].trx.hargaSatuan === 72000);
terap(terapkanNego(s, id, 70000)); ok('nego 70.000 → total 210.000, ditandai nego', s.keranjang[0].trx.hargaTotal === 210000 && s.keranjang[0].trx.nego === true && !s.kabarAwas);
terap(terapkanNego(s, id, 60000)); ok('nego di bawah modal (66.000) tidak ditolak tapi DIBERI TAHU', s.keranjang[0].trx.hargaTotal === 180000 && s.kabarAwas && /DI BAWAH MODAL/.test(s.kabar), s.kabar);
terap(ubahJumlahBaris(s, id, 1)); ok('+1 unit memakai harga nego: 4 × 60.000', s.keranjang[0].trx.jumlah === 4 && s.keranjang[0].trx.hargaTotal === 240000, JSON.stringify(s.keranjang[0].trx));
terap(ubahJumlahBaris(s, id, -4)); ok('−4 → baris hilang', s.keranjang.length === 0);

// ---- antrean: parkir MEMEGANG stok
terap({ keranjang: [], pelanggan: 'Bu Ani', uang: 0, cara: 'Tunai' }); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '5' }); terap(masukkan(s));
terap(parkir(s)); ok('parkir: keranjang kosong, antrean 1 bernama, id aktif baru', s.keranjang.length === 0 && s.antrean.length === 1 && s.antrean[0].beku.pelanggan === 'Bu Ani' && s.aktifId === 2 && s.pelanggan === '');
ok('chip Angsa 50 sekarang bebas 9 (14 − 5 yang dipegang Bu Ani) dan menyebut yang dipegang', chip('karung', 'Angsa', 50).sisa === 9 && chip('karung', 'Angsa', 50).dipegang === 250, chip('karung', 'Angsa', 50).sisa + '/' + chip('karung', 'Angsa', 50).dipegang);
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '10' }); p = masukkan(s);
ok('Pak Budi minta 10 → ditolak, kalimat menyebut BU ANI memegang 250 kg', /bebas dijual sekarang 9 karung/.test(p.kabar) && /Bu Ani masih memegang 250 kg/.test(p.kabar), p.kabar);
terap({ ketik: '3' }); terap(masukkan(s)); ok('3 karung boleh untuk pembeli kedua', s.keranjang.length === 1);
ok('literan Angsa juga berkurang karena kolam kg sama: (700 − 250 − 150) / 0,82', chip('literan', 'Angsa').sisa === Math.floor(300 / 0.82 * 10) / 10, chip('literan', 'Angsa').sisa);
terap(pakaiAntrean(s, 1)); ok('membuka struk Bu Ani MEMARKIR yang sedang jalan (bukan dibuang) dan memulihkan 5 karung', s.keranjang.length === 1 && s.keranjang[0].trx.jumlahKarung === 5 && s.pelanggan === 'Bu Ani' && s.antrean.length === 1 && s.antrean[0].beku.items[0].trx.jumlahKarung === 3, JSON.stringify(s.antrean));
terap(buangAntrean(s, s.antrean[0].id)); ok('buang struk → stoknya bebas lagi: 14 − 5 aktif = 9', s.antrean.length === 0 && chip('karung', 'Angsa', 50).sisa === 9);
terap(pembeliLain(s)); ok('pembeli lain = parkir', s.antrean.length === 1 && s.keranjang.length === 0);

// ---- pelanggan & hari ini
var d = daftarPelanggan(''); ok('daftar pelanggan: Bu Suti (terdaftar ✓, 2× belanja) & Deka (bon 890.000)', d.length === 2 && d.find(function (o) { return o.nama === 'Bu Suti'; }).terdaftar === true && d.find(function (o) { return o.nama === 'Deka'; }).sisaBon === 890000, JSON.stringify(d));
ok('cari "dek" menyempit', daftarPelanggan('dek').length === 1);
var hi = hariIni(s); ok('hari ini 19 Sep: 2 baris, 2 nota, omzet 834.000, Tunai 144.000 · Kredit 690.000', hi.baris === 2 && hi.nota === 2 && hi.omzet === 834000 && hi.perCara.Tunai === 144000 && hi.perCara.Kredit === 690000, JSON.stringify(hi));

// ================= PUTARAN 2: MENCATAT NOTA (bentuk dokumen = simpanKeranjangJual index.html) =================
var __id = 1000; var W = { tanggal: '2026-09-19', jam: '10:15', idUnik: function () { __id += 1; return __id; } };
function mulaiNota() { terap({ keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, kreditDibuka: false, antrean: [], lembar: null, notaTerakhir: null }); }
// A. tunai + potongan + pembulatan: literan 1,3 L (17.550) + Kembang 5 kg (72.000) = 89.550; potongan 1.000 → 88.550 → bulat +450 = 89.000; uang 100.000
mulaiNota(); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '1,3' }); terap(masukkan(s)); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '1' }); terap(masukkan(s));
terap(setelPotongan(s, 1000)); terap(tambahUang(s, 100000));
var N = susunNotaDokumen(s, W); var pj = N.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).map(function (x) { return x.data; });
ok('A: dua dokumen penjualan, tidak ada dokumen lain (1,3 L tanpa kantong)', N.dokumen.length === 2 && pj.length === 2, JSON.stringify(N.dokumen.map(function (x) { return x.koleksi; })));
ok('A: potongan proporsional — 196 ke literan, sisa 804 ke Kembang (jumlahnya PERSIS 1.000)', pj[0].potonganTransaksi === 196 && pj[1].potonganTransaksi === 804, JSON.stringify([pj[0].potonganTransaksi, pj[1].potonganTransaksi]));
ok('A: pembulatan 450 melekat ke baris TERAKHIR: 72.000 − 804 + 450 = 71.646; literan 17.354; total 89.000', pj[1].pembulatan === 450 && pj[1].hargaTotal === 71646 && pj[0].hargaTotal === 17354 && !pj[0].pembulatan && N.totalBayar === 89000, JSON.stringify(pj.map(function (p) { return p.hargaTotal; })));
ok('A: tiap baris membawa uangDiterima 100.000 & kembalian 11.000, caraBayar Tunai, trxId sama, id unik, tanggal/jam tetap', pj.every(function (p) { return p.uangDiterima === 100000 && p.kembalian === 11000 && p.caraBayar === 'Tunai' && p.trxId === N.trxId && p.tanggal === '2026-09-19' && p.jam === '10:15'; }) && pj[0].id !== pj[1].id, JSON.stringify(pj));
ok('A: bentuk baris = index.html: literan {jenis, merkSumber, jumlahLiter, rasioPakai, totalKg, namaProduk, hppTotalSaatJual, hargaTotal, hargaAsliSatuan}; tanpa sisa isian layar', ['jenis', 'merkSumber', 'jumlahLiter', 'rasioPakai', 'totalKg', 'namaProduk', 'hppTotalSaatJual', 'hargaTotal', 'hargaAsliSatuan', 'namaPelanggan'].every(function (k) { return k in pj[0]; }) && ['label', 'satuan', 'jumlah', 'hargaSatuan', 'hargaAsli', 'nego'].every(function (k) { return !(k in pj[0]); }), JSON.stringify(Object.keys(pj[0])));
ok('A: kemasan {namaProduk, ukuranKemasan, jumlahUnit, totalKg}; hargaAsliSatuan = harga daftar 72.000; tanpa negoSelisih', pj[1].jenis === 'kemasan' && pj[1].ukuranKemasan === 5 && pj[1].jumlahUnit === 1 && pj[1].totalKg === 5 && pj[1].hargaAsliSatuan === 72000 && !('negoSelisih' in pj[1]), JSON.stringify(pj[1]));
ok('A: ringkasannya menyebut potongan, pembulatan, kembalian', /potongan Rp1\.000/.test(N.ringkas) && /dibulatkan \+Rp450/.test(N.ringkas) && /kembalian Rp11\.000/.test(N.ringkas), N.ringkas);
// B. bayar sebagian: Kembang × 3 = 216.000, uang 200.000, Deka (belum terdaftar — bayar sebagian TIDAK kena KR1, seperti live)
mulaiNota(); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '3' }); terap(masukkan(s)); terap(tambahUang(s, 200000)); terap({ pelanggan: 'Deka' });
var R = simpanNota(s, W); ok('B: sah walau Deka belum terdaftar (bayar sebagian bukan bon murni)', !R.tolak, R.tolak);
N = R.nota; pj = N.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).map(function (x) { return x.data; }); var pt = N.dokumen.filter(function (x) { return x.koleksi === 'piutangMutasi'; }).map(function (x) { return x.data; });
ok('B: baris jadi KREDIT penuh 216.000 tanpa uangDiterima; satu pelunasan piutang 200.000 caraBayar Tunai, dicatatDi sistem', pj[0].caraBayar === 'Kredit' && pj[0].hargaTotal === 216000 && !('uangDiterima' in pj[0]) && pt.length === 1 && pt[0].tipe === 'bayar' && pt[0].nominal === 200000 && pt[0].caraBayar === 'Tunai' && pt[0].namaPelanggan === 'Deka' && pt[0].dicatatDi === 'sistem' && /sisa Rp16\.000 jadi piutang/.test(pt[0].catatan), JSON.stringify(N.dokumen));
ok('B: ringkasan menyebut dibayar & BON atas nama', /dibayar Rp200\.000 · BON Rp16\.000 atas nama Deka/.test(N.ringkas), N.ringkas);
var utangSebelum = hitungPiutang().find(function (x) { return x.kunci === 'deka'; }).sisa; var stokSebelum = chip('kemasan', 'Kembang|5').sisa;
terapkanKeCache(N.dokumen); terap(R.patch);
ok('B: sesudah dicatat — bon Deka naik 16.000; stok Kembang 5 tetap 34 (3 pindah dari keranjang ke terjual); keranjang kosong, notaTerakhir terisi', hitungPiutang().find(function (x) { return x.kunci === 'deka'; }).sisa === utangSebelum + 16000 && chip('kemasan', 'Kembang|5').sisa === stokSebelum && stokSebelum === 34 && s.keranjang.length === 0 && s.notaTerakhir && s.notaTerakhir.idPenjualan.length === 1, hitungPiutang().find(function (x) { return x.kunci === 'deka'; }).sisa + ' / ' + chip('kemasan', 'Kembang|5').sisa);
ok('B: Hari ini ikut naik: 3 baris, omzet 834.000 + 216.000', hariIni(s).baris === 3 && hariIni(s).omzet === 1050000, JSON.stringify(hariIni(s)));
// G. batalkan nota barusan: baris ditandai dibatalkan, pelunasan sebagiannya dilepas → angka pulih
var P = susunPembatalan(s.notaTerakhir, 'uji'); ok('G: pembatalan = 1 dokumen penjualan bertanda dibatalkan + hapus 1 pelunasan piutang', P.dokumen.length === 1 && P.dokumen[0].data.dibatalkan === true && P.dokumen[0].data.alasanKoreksi === 'uji' && P.hapus.length === 1 && P.hapus[0].koleksi === 'piutangMutasi', JSON.stringify(P));
terapkanKeCache(P.dokumen); terapkanKeCache(P.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; }));
ok('G: sesudah dibatalkan — bon Deka pulih, stok Kembang kembali 37, omzet hari ini kembali', hitungPiutang().find(function (x) { return x.kunci === 'deka'; }).sisa === utangSebelum && chip('kemasan', 'Kembang|5').sisa === stokSebelum + 3 && hariIni(s).omzet === 834000, hitungPiutang().find(function (x) { return x.kunci === 'deka'; }).sisa + ' / ' + chip('kemasan', 'Kembang|5').sisa);
// C. KR1 untuk bon murni
mulaiNota(); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '1' }); terap(masukkan(s)); terap(pilihCara(s, 'Kredit')); terap({ pelanggan: 'Deka' });
ok('C: Deka belum terdaftar → KR1 mengunci bon', /belum terdaftar/.test(alasanTolak(s)), alasanTolak(s));
terap({ kreditDibuka: true }); R = simpanNota(s, W); ok('C: owner membuka kredit sekali → sah, baris membawa kreditDibukaOwner', !R.tolak && R.nota.dokumen[0].data.kreditDibukaOwner === true, R.tolak);
terap({ kreditDibuka: false, pelanggan: 'Bu Suti' }); ok('C: Bu Suti terdaftar, batas 2× belanja bulanan (rata 72.000 → 144.000): 72.000 boleh', alasanTolak(s) === '', alasanTolak(s));
terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '2' }); terap(masukkan(s)); ok('C: 216.000 melewati batas 144.000 → dikunci', /Melewati batas kredit Rp144\.000/.test(alasanTolak(s)), alasanTolak(s));
// D. literan ≥ 5 L: dokumen pemakaian kantong ikut, id = id + 1
mulaiNota(); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '6' }); terap(masukkan(s)); terap(uangPas(s));
N = susunNotaDokumen(s, W); var bh = N.dokumen.filter(function (x) { return x.koleksi === 'stokBahanLiteran'; })[0]; pj = N.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; })[0].data;
ok('D: dokumen stokBahanLiteran {id: id+1, tipe pakai, jenis paperbag10l, jumlah 1, hargaTotal 0}', bh && bh.data.id === pj.id + 1 && bh.data.tipe === 'pakai' && bh.data.jenis === 'paperbag10l' && bh.data.jumlah === 1 && bh.data.hargaTotal === 0 && /penjualan literan id/.test(bh.data.catatan), JSON.stringify(bh));
ok('D: Tunai PAS → uangDiterima = total, kembalian 0; pembulatan 0 (81.000 pas)', pj.uangDiterima === 81000 && pj.kembalian === 0 && !pj.pembulatan, JSON.stringify(pj));
// E. nego: hargaAsliSatuan tetap harga daftar, negoSelisih negatif
mulaiNota(); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '2' }); terap(masukkan(s)); terap(terapkanNego(s, s.keranjang[0].id, 70000)); terap(uangPas(s));
pj = susunNotaDokumen(s, W).dokumen[0].data; ok('E: nego 70.000: hargaTotal 140.000, hargaAsliSatuan 72.000, negoSelisih −2.000', pj.hargaTotal === 140000 && pj.hargaAsliSatuan === 72000 && pj.negoSelisih === -2000, JSON.stringify(pj));
// F. stok dicek ulang saat mencatat: penjualan lain masuk sesudah keranjang diisi
mulaiNota(); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '14' }); terap(masukkan(s)); terap(uangPas(s)); ok('F: 14 karung sah sekarang', !simpanNota(s, W).tolak);
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sX', tanggal: '2026-09-19', jam: '10:20', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 2, totalKg: 100, hargaTotal: 1380000, hppTotalSaatJual: 1300000 } }]);
R = simpanNota(s, W); ok('F: 2 karung terjual di perangkat lain → mencatat 14 DITAHAN: bebas tinggal 12', /bebas dijual tinggal 12 karung/.test(R.tolak || ''), R.tolak);
terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sX' }]);

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var s = keadaanAwal(); sinkronKeranjang(s); var rak = susunRak(s); var hi = hariIni(s); var d = daftarPelanggan('');
// bentuk dokumen dari data toko: kunci yang dihasilkan wajib sudah dikenal baris penjualan nyata (kecuali 'pembulatan' yang lahir 5 Sep)
var dikenal = {}; (CAD.penjualan || []).forEach(function (p) { Object.keys(p).forEach(function (k) { dikenal[k] = true; }); }); dikenal.pembulatan = true;
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); }
var asing = [];
[['karung', rak.karung[0]], ['literan', rak.literan[0]], ['kemasan', rak.kemasan[0]]].forEach(function (x) {
  if (!x[1]) return; terap({ keranjang: [] }); terap(ketukChip(s, x[1])); terap({ ketik: x[0] === 'literan' ? '6' : '1' }); terap(masukkan(s)); terap({ uang: 0 }); terap(uangPas(s));
  susunNotaDokumen(s, { tanggal: '2026-09-11', jam: '10:00', idUnik: function () { return Math.random(); } }).dokumen.forEach(function (dk) { if (dk.koleksi !== 'penjualan') return; Object.keys(dk.data).forEach(function (k) { if (!dikenal[k]) asing.push(x[0] + ':' + k); }); });
});
print(JSON.stringify({ karung: rak.karung.length, kemasan: rak.kemasan.length, literan: rak.literan.length, sering: rak.sering.length, pelanggan: d.length, tanpaHarga: rak.karung.concat(rak.kemasan, rak.literan).filter(function (c) { return !(c.harga > 0); }).length, kunciAsing: asing }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def utama(js):
    h, e = jalan(js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    js = bundel_baru.bundel(MODUL)
    if '--kontrol' in sys.argv:
        rusak = {
            'QRIS ikut dibulatkan': js.replace("return (c === 'Tunai' || c === 'Kredit') && total > 0 ?", "return total > 0 ?"),
            'bon tidak dibulatkan (aturan lama)': js.replace("return (c === 'Tunai' || c === 'Kredit') && total > 0 ?", "return c === 'Tunai' && total > 0 ?"),
            'struk parkir tidak memegang stok': js.replace("s.antrean.map((a) => ({ beku: { items: a.beku.items.map((b) => ({ trx: b.trx })), nama: a.beku.pelanggan } }))", "[]"),
            'langit-langit stok diabaikan': js.replace("if (maks !== null && j > maks) {", "if (false) {"),
            'uang kurang dianggap lunas': js.replace("const kurang = s.cara === 'Tunai' && uang > 0 ? Math.max(0, total - uang) : 0;", "const kurang = 0;"),
            'sisa bon tanpa nama lolos': js.replace("if (t.sisaJadiBon && !nama) return", "if (false) return"),
            'nego di bawah modal tidak diberi tahu': js.replace("const awas = hppSatuan > 0 && hg < hppSatuan;", "const awas = false;"),
            'penjualan batal ikut dihitung di hari ini': js.replace("const baris = ambilPenjualan().filter((p) => p.tanggal === iso);", "const baris = ambilPenjualanSemua().filter((p) => p.tanggal === iso);"),
            'harga kemasan 25 kg diabaikan (per kg menang)': js.replace("const hg = hargaKarungUtuh(merk, berat);", "const hg = { perUnit: Math.round((cariHargaKarungPerKg(merk) || 0) * berat) };"),
            'kantong literan tidak masuk HPP': js.replace("hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg) + biayaK,", "hppTotalSaatJual: Math.round((chip.hppPerKg || 0) * totalKg),"),
            'membuka struk lain MEMBUANG keranjang yang sedang jalan': js.replace("const dasar = s.keranjang.length ? parkir(s) : { antrean: s.antrean };", "const dasar = { antrean: s.antrean };"),
            # ---- putaran 2 ----
            'potongan tidak proporsional (semua ke baris pertama)': js.replace("const bagian = i === items.length - 1 ? potDipakai - terpakai : Math.min(t.hargaTotal, Math.round(potDipakai * t.hargaTotal / (subtotal || 1)));", "const bagian = i === 0 ? potDipakai : 0;"),
            'pembulatan melekat ke baris PERTAMA': js.replace("for (let i = items.length - 1; i >= 0; i--) { if (items[i].hargaTotal > 0) { items[i].pembulatan = bulatNota; items[i].hargaTotal += bulatNota; break; } }", "for (let i = 0; i < items.length; i++) { if (items[i].hargaTotal > 0) { items[i].pembulatan = bulatNota; items[i].hargaTotal += bulatNota; break; } }"),
            'bayar sebagian dicatat Tunai (kekurangan hilang dari buku bon)': js.replace("if (cara !== 'Kredit' && uang > 0 && uang < tagihan) { bayarSebagian = uang; cara = 'Kredit'; }", "if (false) { }"),
            'pelunasan sebagian tidak dicatat': js.replace("if (bayarSebagian > 0) {\n    piutangId = w.idUnik();", "if (false) {\n    piutangId = w.idUnik();"),
            'kantong literan tidak dicatat terpakai': js.replace("if (d.kemasanLiteran && d.jumlahKemasanLiteranDipakai > 0) {\n      dokumen.push", "if (false) {\n      dokumen.push"),
            'KR1 dilewati untuk bon': js.replace("if (s.cara === 'Kredit') { const k = alasanKunciKredit(s, t.total); if (k) return k; }", ""),
            'stok tidak dicek ulang saat mencatat': js.replace("const tolak = alasanTolak(s) || periksaStokKeranjang(s);", "const tolak = alasanTolak(s);"),
            'pembatalan tidak melepas pelunasan sebagian': js.replace("if (notaTerakhir.piutangId) hapus.push({ koleksi: 'piutangMutasi', id: notaTerakhir.piutangId });", ""),
            'isian layar bocor ke dokumen (label/satuan)': js.replace("['label', 'satuan', 'jumlah', 'hargaSatuan', 'hargaAsli', 'nego'].forEach((k) => { delete d[k]; });", ""),
        }
        kode = 0
        for nama, isi in rusak.items():
            if isi == js: print('KONTROL BASI  ' + nama); kode = 3; continue
            l, g = utama(isi)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:110] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = utama(js)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g))); [print('   ✗ ' + x) for x in g]
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')))
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        h, e = jalan(js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else: print('ASAP DATA TOKO (%s): rak karung %d · kemasan %d · literan %d · sering %d · pelanggan %d · chip tanpa harga %d · kunci dokumen asing %s' % (os.path.basename(cad[-1]), h['karung'], h['kemasan'], h['literan'], h['sering'], h['pelanggan'], h['tanpaHarga'], h['kunciAsing'] or 'nihil'))
        if h and (h['karung'] == 0 or h['tanpaHarga'] > 0 or h['kunciAsing']): g.append('asap: rak kosong, chip tanpa harga, atau kunci dokumen yang tidak dikenal baris nyata')
    sys.exit(2 if g else 0)
