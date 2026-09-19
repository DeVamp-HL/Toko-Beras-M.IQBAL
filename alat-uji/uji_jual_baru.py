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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/jual-logika.js']

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
function cacheAda(koleksi, id) { return cacheMentah(({ retur: 'retur', karantina: 'karantina' })[koleksi] || koleksi).some(function (d) { return String(d.id) === String(id); }); }
function chip(jalur, kunci, berat) { var r = susunRak(s); return r[jalur].find(function (c) { return c.kunci === kunci && (!berat || c.berat === berat); }); }

// ---- rak dibaca dari mesin (bukan hitungan sendiri)
var rak = susunRak(s);
ok('rak karung: tiga chip berharga, per ukuran (50 dulu) lalu TERMURAH dulu: Angsa 50 (690.000) · Apex 50 (730.000) · Angsa 25', rak.karung.length === 3 && rak.karung.map(function (c) { return c.nama + c.berat; }).join() === 'Angsa50,IR64 Apex50,Angsa25', JSON.stringify(rak.karung.map(function (c) { return c.nama + c.berat; })));
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
terap(buangAntrean(s, s.antrean.length ? s.antrean[0].id : 0)); ok('buang struk → stoknya bebas lagi: 14 − 5 aktif = 9', s.antrean.length === 0 && chip('karung', 'Angsa', 50).sisa === 9);
terap(pembeliLain(s)); ok('pembeli lain = parkir', s.antrean.length === 1 && s.keranjang.length === 0);

// ---- pelanggan & hari ini
var d = daftarPelanggan(''); ok('daftar pelanggan: Bu Suti (terdaftar ✓, 2× belanja) & Deka (bon 890.000)', d.length === 2 && d.find(function (o) { return o.nama === 'Bu Suti'; }).terdaftar === true && d.find(function (o) { return o.nama === 'Deka'; }).sisaBon === 890000, JSON.stringify(d));
ok('cari "dek" menyempit', daftarPelanggan('dek').length === 1);
var hi = hariIni(s); ok('hari ini 19 Sep: 2 baris, 2 nota, omzet 834.000, Tunai 144.000 · Kredit 690.000', hi.baris === 2 && hi.nota === 2 && hi.omzet === 834000 && hi.perCara.Tunai === 144000 && hi.perCara.Kredit === 690000, JSON.stringify(hi));

// ================= PUTARAN 2: MENCATAT NOTA (bentuk dokumen = simpanKeranjangJual index.html) =================
var __id = 1000; var W = { tanggal: '2026-09-19', jam: '10:15', idUnik: function () { __id += 1; return __id; } };
function mulaiNota() { terap({ tukar: null, keranjang: [], pelanggan: '', cara: 'Tunai', uang: 0, potongan: 0, kreditDibuka: false, antrean: [], lembar: null, notaTerakhir: null, pesananId: null, namaRepack: '', penggantiTanya: null, ketik: '' }); }
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

// ================= PUTARAN 3: paritas Jual lama =================
W.kini = '2026-09-19T03:15:00.000Z';
// H. REPACKING DADAKAN: kg bebas dari kolam karung, harga per kg katalog, nama jual bebas
mulaiNota(); rak = susunRak(s);
ok('H: rak repack = merek berharga per kg: Angsa 13.800/kg & Apex 14.600/kg, satuan kg, sisa Angsa ±700 kg', rak.repack.length === 2 && rak.repack[0].kunci === 'Angsa' && rak.repack[0].harga === 13800 && rak.repack[0].satuan === 'kg' && rak.repack[0].sisa === 700, JSON.stringify(rak.repack));
terap(ketukChip(s, chip('repack', 'Angsa'))); terap(tekanTuts(s, '1')); terap(tekanTuts(s, '2')); terap(tekanTuts(s, ',')); terap(tekanTuts(s, '5'));
ok('H: tuts koma boleh untuk repack (12,5)', s.ketik === '12,5', s.ketik);
terap({ namaRepack: 'Angsa eceran 12,5' }); terap(masukkan(s));
ok('H: baris repacking {jenis repacking, merkSumber Angsa, namaProduk dari ketikan, totalKg 12,5, hargaTotal 172.500, HPP 12,5 × hpp/kg}', s.keranjang.length === 1 && s.keranjang[0].trx.jenis === 'repacking' && s.keranjang[0].trx.merkSumber === 'Angsa' && s.keranjang[0].trx.namaProduk === 'Angsa eceran 12,5' && s.keranjang[0].trx.totalKg === 12.5 && s.keranjang[0].trx.hargaTotal === 172500 && s.keranjang[0].trx.hppTotalSaatJual === Math.round(chip('repack', 'Angsa').hppPerKg * 12.5) && s.namaRepack === '', JSON.stringify(s.keranjang[0].trx));
ok('H: kolam kg SAMA — chip karung Angsa 50 bebas 13 (687,5 kg), literan & repack ikut turun', chip('karung', 'Angsa', 50).sisa === 13.5 && chip('repack', 'Angsa').sisa === 687.5 && chip('literan', 'Angsa').sisa === Math.floor(687.5 / 0.82 * 10) / 10, chip('karung', 'Angsa', 50).sisa + '/' + chip('repack', 'Angsa').sisa);
terap(ketukChip(s, chip('repack', 'Angsa'))); terap({ ketik: '700' }); p = masukkan(s); ok('H: minta 700 kg padahal bebas 687,5 → ditolak', s.keranjang.length === 1 && /bebas dijual sekarang 687,5 kg/.test(p.kabar), p.kabar); terap({ lembar: null, pilih: null, ketik: '' });
terap(ubahJumlahBaris(s, s.keranjang[0].id, 1)); ok('H: +1 kg → 13,5 kg, nama jual dipertahankan', s.keranjang[0].trx.totalKg === 13.5 && s.keranjang[0].trx.namaProduk === 'Angsa eceran 12,5' && s.keranjang[0].trx.hargaTotal === 186300, JSON.stringify(s.keranjang[0].trx));
terap(uangPas(s)); pj = susunNotaDokumen(s, W).dokumen[0].data;
ok('H: dokumen repacking = bentuk index.html 19333: {jenis, merkSumber, namaProduk, totalKg, hppTotalSaatJual, hargaTotal, hargaAsliSatuan} tanpa jumlahKarung/jumlahLiter', pj.jenis === 'repacking' && pj.totalKg === 13.5 && pj.hargaAsliSatuan === 13800 && !('jumlahKarung' in pj) && !('jumlahLiter' in pj) && !('jumlah' in pj) && !('label' in pj), JSON.stringify(pj));
terap(ketukChip(s, chip('repack', 'IR64 Apex'))); terap({ ketik: '5' }); terap(masukkan(s)); ok('H: tanpa nama ketikan → nama jual = merek', s.keranjang[1].trx.namaProduk === 'IR64 Apex' && s.keranjang[1].trx.label === 'Repack IR64 Apex', s.keranjang[1].trx.label);
ok('H: ringkasan hari ini mengenal repacking', /^Repack /.test((function () { terapkanKeCache([{ koleksi: 'penjualan', data: Object.assign({}, pj, { id: 'sR', tanggal: '2026-09-19' }) }]); var r = hariIni(s).terakhir.find(function (x) { return /Repack/.test(x.teks); }); terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sR' }]); return r ? r.teks : ''; })()));
// I. BONUS kemasan +1: stok & HPP ikut, uang tidak
mulaiNota(); terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '10' }); terap(masukkan(s)); id = s.keranjang[0].id;
terap(toggleBonus(s, id)); var tb = s.keranjang[0].trx;
ok('I: bonus → jumlahUnit 11, totalKg 55, HPP 11 × 66.000, hargaTotal TETAP 10 × 72.000, bonusUnit 1', tb.jumlahUnit === 11 && tb.totalKg === 55 && tb.hppTotalSaatJual === 726000 && tb.hargaTotal === 720000 && tb.bonusUnit === 1 && tb.jumlah === 10, JSON.stringify(tb));
ok('I: stok Kembang bebas 37 − 11 = 26 (bonus memotong stok)', chip('kemasan', 'Kembang|5').sisa === 26, chip('kemasan', 'Kembang|5').sisa);
terap(ubahJumlahBaris(s, id, 1)); ok('I: +1 unit bayar → 11 bayar + 1 bonus = 12 unit, uang 11 × 72.000', s.keranjang[0].trx.jumlahUnit === 12 && s.keranjang[0].trx.hargaTotal === 792000 && s.keranjang[0].trx.bonusUnit === 1, JSON.stringify(s.keranjang[0].trx));
terap(ubahJumlahBaris(s, id, 25)); ok('I: 36 bayar + 1 bonus = 37 = pas stok → boleh', s.keranjang[0].trx.jumlahUnit === 37, JSON.stringify(s.keranjang[0].trx));
p = ubahJumlahBaris(s, id, 1); ok('I: 37 bayar + bonus = 38 > 37 → ditolak, kalimat menyebut termasuk bonus', /termasuk bonus/.test(p.kabar) && s.keranjang[0].trx.jumlahUnit === 37, p.kabar);
terap(toggleBonus(s, id)); ok('I: bonus dilepas → 36 unit, tanpa bonusUnit', s.keranjang[0].trx.jumlahUnit === 36 && !('bonusUnit' in s.keranjang[0].trx), JSON.stringify(s.keranjang[0].trx));
terap(ubahJumlahBaris(s, id, 1)); p = toggleBonus(s, id); ok('I: 37 bayar, minta bonus → stok tidak cukup, ditolak', /Bonus butuh 1 unit lagi/.test(p.kabar) && !s.keranjang[0].trx.bonusUnit, p.kabar);
terap(ubahJumlahBaris(s, id, -35)); terap(toggleBonus(s, id)); terap(terapkanNego(s, id, 70000)); ok('I: nego pada baris berbonus: uang 2 × 70.000, unit tetap 3', s.keranjang[0].trx.hargaTotal === 140000 && s.keranjang[0].trx.jumlahUnit === 3, JSON.stringify(s.keranjang[0].trx));
terap(uangPas(s)); pj = susunNotaDokumen(s, W).dokumen[0].data; ok('I: dokumen membawa bonusUnit 1, jumlahUnit 3, hargaTotal 140.000, negoSelisih −2.000', pj.bonusUnit === 1 && pj.jumlahUnit === 3 && pj.hargaTotal === 140000 && pj.negoSelisih === -2000, JSON.stringify(pj));
ok('I: 140.000 pas; stok cukup → periksaStokKeranjang diam', periksaStokKeranjang(s) === '' && !simpanNota(s, W).tolak);
terap(ubahJumlahBaris(s, id, 34)); terap(uangPas(s)); ok('I: 36 bayar + 1 bonus = 37 = pas stok', s.keranjang[0].trx.jumlahUnit === 37);
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sY', tanggal: '2026-09-19', jam: '10:20', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 72000, hppTotalSaatJual: 66000 } }]);
ok('I: 1 unit terjual di perangkat lain → 36 bayar + bonus = 37 > 36: mencatat DITAHAN, kalimat menyebut termasuk bonus', /termasuk bonus/.test(simpanNota(s, W).tolak || '') && /tinggal 36 kemasan/.test(simpanNota(s, W).tolak || ''), simpanNota(s, W).tolak);
terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sY' }]);
// J. PENGGANTI RETUR: omzet & kas Rp0, nilai barang jadi jejak, HPP tetap, tanpa pembulatan
mulaiNota(); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '1,3' }); terap(masukkan(s)); id = s.keranjang[0].id;
terap(togglePenggantiRetur(s, id)); var tp = s.keranjang[0].trx;
ok('J: hargaTotal 0, nilaiBarangPengganti 17.550, penggantiRetur true, HPP tetap', tp.hargaTotal === 0 && tp.nilaiBarangPengganti === 17550 && tp.penggantiRetur === true && tp.hppTotalSaatJual > 0, JSON.stringify(tp));
t = hitungTagihan(s); ok('J: tagihan 0 → tanpa pembulatan; nota tunai tanpa uang SAH (tidak ada yang ditagih)', t.total === 0 && t.bulat === 0 && alasanTolak(s) === '', alasanTolak(s));
terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '1' }); terap(masukkan(s)); terap(uangPas(s)); N = susunNotaDokumen(s, W); pj = N.dokumen.map(function (x) { return x.data; });
ok('J: pembulatan 0 (72.000 pas); baris pengganti tidak dapat potongan/pembulatan; baris kemasan normal', pj[0].hargaTotal === 0 && !('pembulatan' in pj[0]) && pj[1].hargaTotal === 72000 && N.totalBayar === 72000, JSON.stringify(pj));
terap(setelPotongan(s, 1000)); N = susunNotaDokumen(s, W); pj = N.dokumen.map(function (x) { return x.data; });
ok('J: potongan 1.000 semua ke baris bernilai (72.000 → 71.000), baris Rp0 tetap 0; bulat +0 (71.000 pas)', !('potonganTransaksi' in pj[0]) && pj[1].potonganTransaksi === 1000 && pj[1].hargaTotal === 71000 && /1 pengganti retur Rp0/.test(N.ringkas), JSON.stringify(pj) + N.ringkas);
terap(terapkanNego(s, id, 13000)); ok('J: nego pada baris pengganti: nilai jejak ikut 16.900, uang tetap 0', s.keranjang[0].trx.nilaiBarangPengganti === 16900 && s.keranjang[0].trx.hargaTotal === 0, JSON.stringify(s.keranjang[0].trx));
terap(togglePenggantiRetur(s, id)); ok('J: dilepas → dijual penuh 16.900 (harga nego), jejak hilang', s.keranjang[0].trx.hargaTotal === 16900 && !('nilaiBarangPengganti' in s.keranjang[0].trx) && !('penggantiRetur' in s.keranjang[0].trx), JSON.stringify(s.keranjang[0].trx));
terapkanKeCache([{ koleksi: 'retur', data: { id: 'rB', tanggal: '2026-09-19', tukarModel: 'kreditBarang', nominalRefund: 50000 } }]);
p = togglePenggantiRetur(s, id); ok('J: hari ini ada tukar BERNOTA → ketukan pertama cuma memperingatkan (penjaga model B)', /MENUNJUK NOTA/.test(p.kabar) && p.penggantiTanya === id && !s.keranjang[0].trx.penggantiRetur, p.kabar); terap(p);
terap(togglePenggantiRetur(s, id)); ok('J: ketukan kedua pada baris yang sama → jadi pengganti', s.keranjang[0].trx.penggantiRetur === true && s.penggantiTanya === null);
terapkanKeCache([{ koleksi: 'retur', hapus: 'rB' }]);
// K. PESANAN: dipesan → diantar → DIBAYAR hanya lewat nota; ikatan ikut parkir; batal nota memulihkan
mulaiNota(); terap({ psNama: 'Bu Ani', psIsi: '2 karung Angsa', psAlamat: 'Jl. Melati 3', psNilai: '1.380.000' });
var PS = susunPesananBaru(s, W); ok('K: pesanan baru = bentuk simpanPesanan: status dipesan, trxIdJual null, riwayatStatus [dipesan], nilaiPerkiraan 1.380.000', PS.dokumen && PS.dokumen[0].koleksi === 'pesanan' && PS.dokumen[0].data.status === 'dipesan' && PS.dokumen[0].data.trxIdJual === null && PS.dokumen[0].data.riwayatStatus.length === 1 && PS.dokumen[0].data.nilaiPerkiraan === 1380000 && PS.dokumen[0].data.alamat === 'Jl. Melati 3', JSON.stringify(PS));
ok('K: tanpa isi ditolak', !!susunPesananBaru(Object.assign({}, s, { psIsi: '' }), W).tolak);
terapkanKeCache(PS.dokumen); terap(PS.patch); var psId = PS.dokumen[0].data.id;
ok('K: daftar pesanan aktif memuat Bu Ani; saring "dek" kosong', daftarPesanan('').length === 1 && daftarPesanan('')[0].nama === 'Bu Ani' && daftarPesanan('dek').length === 0);
ok('K: pesanan BUKAN uang & BUKAN stok: omzet hari ini & stok Angsa tidak berubah', hariIni(s).omzet === 834000 && chip('karung', 'Angsa', 50).sisa === 14);
var PA = susunPesananAntar(psId, W); ok('K: antar → status diantar, riwayat 2', PA.dokumen[0].data.status === 'diantar' && PA.dokumen[0].data.riwayatStatus.length === 2, JSON.stringify(PA)); terapkanKeCache(PA.dokumen);
ok('K: antar dua kali ditolak (sudah DIANTAR)', /sudah DIANTAR/.test(susunPesananAntar(psId, W).tolak || ''), JSON.stringify(susunPesananAntar(psId, W)));
terap(ikatPesanan(s, psId)); ok('K: ikat → nama Bu Ani terisi, pesananId terpasang', s.pesananId === String(psId) && s.pelanggan === 'Bu Ani');
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '2' }); terap(masukkan(s));
terap(parkir(s)); ok('K: parkir membawa ikatan pesanan; keranjang baru tanpa ikatan', s.pesananId === null && s.antrean[0].beku.pesananId === String(psId));
terap(pakaiAntrean(s, s.antrean[0].id)); ok('K: buka lagi → ikatan kembali', s.pesananId === String(psId) && s.pelanggan === 'Bu Ani');
terap(uangPas(s)); R = simpanNota(s, W); ok('K: nota sah', !R.tolak, R.tolak); N = R.nota;
var dps = N.dokumen.filter(function (x) { return x.koleksi === 'pesanan'; });
ok('K: satu dokumen pesanan DIBAYAR dalam batch yang sama, trxIdJual = trxId nota, riwayat 3, ringkasan menyebutnya', dps.length === 1 && dps[0].data.status === 'dibayar' && dps[0].data.trxIdJual === N.trxId && dps[0].data.riwayatStatus.length === 3 && /pesanan Bu Ani DIBAYAR/.test(N.ringkas), JSON.stringify(dps) + N.ringkas);
terapkanKeCache(N.dokumen); terap(R.patch);
ok('K: sesudah dicatat: pesanan hilang dari daftar aktif, ikatan lepas, notaTerakhir ingat pesanannya', daftarPesanan('').length === 0 && s.pesananId === null && s.notaTerakhir.pesanan.id === String(psId) && s.notaTerakhir.pesanan.statusSebelum === 'diantar');
P = susunPembatalan(s.notaTerakhir, 'uji', W); var dpsB = P.dokumen.filter(function (x) { return x.koleksi === 'pesanan'; });
ok('K: batalkan nota → pesanan kembali DIANTAR, trxIdJual null, riwayat 4', dpsB.length === 1 && dpsB[0].data.status === 'diantar' && dpsB[0].data.trxIdJual === null && dpsB[0].data.riwayatStatus.length === 4, JSON.stringify(dpsB));
terapkanKeCache(P.dokumen); ok('K: pesanan aktif lagi', daftarPesanan('').length === 1 && daftarPesanan('')[0].status === 'diantar');
terap(ikatPesanan(s, psId)); terapkanKeCache(susunPesananBatal(psId, W).dokumen || []); ok('K: pesanan dibatalkan orang lain saat terikat → nota DITAHAN', /sudah tuntas/.test(alasanTolak(Object.assign({}, s, { keranjang: [{ id: 'x', trx: bangunBaris(chip('kemasan', 'Kembang|5'), 1, s) }], uang: 72000 }))), alasanTolak(s));
ok('K: pesanan batal tidak bisa diikat lagi', /sudah tuntas/.test(ikatPesanan(s, psId).kabar));
terap(lepasPesanan(s)); ok('K: lepas ikatan', s.pesananId === null);

// ================= PUTARAN 4: RETUR menunjuk nota — refund & tukar =================
mulaiNota(); terap({ tukar: null });
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 's5', trxId: 'T5', tanggal: '2026-09-18', jam: '09:30', caraBayar: 'Tunai', namaPelanggan: 'Pak Rudi', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 2, totalKg: 100, hargaTotal: 1380500, pembulatan: 500, hppTotalSaatJual: 1300000 } },
  { koleksi: 'penjualan', data: { id: 's6', trxId: 'T6', tanggal: '2026-09-18', jam: '09:40', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 3, bonusUnit: 1, totalKg: 15, hargaTotal: 144000, hppTotalSaatJual: 198000 } }]);
var dn = daftarNotaRetur(s); function nota(id) { return dn.find(function (x) { return x.id === id; }); }
ok('L: daftar nota = baris karung/kemasan berlaku (s1 s2 s3 s5 s6), literan & yang dibatalkan tidak ikut, terbaru dulu', dn.length === 5 && dn[0].id === 's2' && !nota('s4'), JSON.stringify(dn.map(function (x) { return x.id; })));
ok('L: nota KREDIT ditolak dengan sebabnya; nota ber-BONUS ditolak; nota tunai bisa', nota('s2').bisa === false && /KREDIT/.test(nota('s2').sebab) && nota('s6').bisa === false && /BONUS/.test(nota('s6').sebab) && nota('s5').bisa === true && nota('s5').sisa === 100 && nota('s5').satuan === 'kg', JSON.stringify([nota('s2'), nota('s6'), nota('s5')]));
terap({ rtCari: 'rudi' }); ok('L: cari "rudi" menyempit ke notanya', daftarNotaRetur(s).length === 1 && daftarNotaRetur(s)[0].id === 's5'); terap({ rtCari: '' });
terap({ rtNotaId: 's5', ketik: '41,5' }); var nd = notaDitunjuk(s);
ok('L: nilai dari NOTA: (1.380.500 − pembulatan 500) ÷ 100 kg = 13.800/kg × 41,5 kg = 572.700', nd.d.perSatuan === 13800 && nd.nilai === 572700, JSON.stringify([nd.d.perSatuan, nd.nilai]));
ok('L: tanpa alasan DITOLAK (KR3)', /alasan retur/.test(susunRetur(s, W).tolak || ''), JSON.stringify(susunRetur(s, W)));
terap({ rtAlasan: 'kualitas kurang' }); ok('L: tanpa jawaban layak-dijual-lagi DITOLAK', /BOLEH DIJUAL LAGI/.test(susunRetur(s, W).tolak || ''));
terap({ rtKondisi: 'utuh', ketik: '101' }); ok('L: 101 kg dari nota 100 kg DITOLAK, kalimat menyebut sisa', /melebihi sisa nota/.test(susunRetur(s, W).tolak || '') && /sisa 100 kg/.test(susunRetur(s, W).tolak || ''), susunRetur(s, W).tolak);
var kgSebelum = chip('repack', 'Angsa').sisa;
terap({ ketik: '41,5' }); var RT = susunRetur(s, W); var rd = RT.dokumen && RT.dokumen[0].data;
ok('L: refund layak-jual = SATU dokumen retur (tanpa karantina), bentuk simpanRetur: karung sebagian totalKg 41,5 & jumlahKarung 0,83', RT.dokumen.length === 1 && RT.dokumen[0].koleksi === 'retur' && rd.jenisAsal === 'karung' && rd.merkSumber === 'Angsa' && rd.totalKg === 41.5 && rd.jumlahKarung === 0.83 && rd.beratKarungAcuan === 50, JSON.stringify(RT.dokumen));
ok('L: jejak nota lengkap: notaAsalId/Tanggal/Kunci, hargaPerSatuanNota 13.800, satuanNota kg, jumlahDikembalikan 41,5, nilaiDikembalikan = nominalRefund = 572.700, kondisi utuh, penyelesaian refund, catatan', rd.notaAsalId === 's5' && rd.notaAsalTanggal === '2026-09-18' && rd.notaAsalKunci === 'T5' && rd.hargaPerSatuanNota === 13800 && rd.satuanNota === 'kg' && rd.jumlahDikembalikan === 41.5 && rd.nilaiDikembalikan === 572700 && rd.nominalRefund === 572700 && rd.kondisi === 'utuh' && rd.penyelesaian === 'refund' && rd.catatan === 'kualitas kurang' && rd.tanggal === '2026-09-19' && /pembulatan tunai/.test(rd.dasarHargaNota) && !('tukarModel' in rd), JSON.stringify(rd));
terapkanKeCache(RT.dokumen); terap(RT.patch);
ok('L: barang layak-jual KEMBALI ke stok: kolam Angsa +41,5 kg; isian retur bersih lagi', chip('repack', 'Angsa').sisa === kgSebelum + 41.5 && s.rtNotaId === null && s.rtAlasan === '', chip('repack', 'Angsa').sisa + ' vs ' + kgSebelum);
ok('L: sisa nota turun jadi 58,5 kg', daftarNotaRetur(s).find(function (x) { return x.id === 's5'; }).sisa === 58.5);
terap({ rtNotaId: 's5', ketik: '60', rtAlasan: 'kelebihan', rtKondisi: 'tidak_utuh' }); ok('L: retur kedua 60 kg > sisa 58,5 DITOLAK dan menyebut yang sudah diretur', /41,5 sudah diretur sebelumnya/.test(susunRetur(s, W).tolak || ''), susunRetur(s, W).tolak);
kgSebelum = chip('repack', 'Angsa').sisa; terap({ ketik: '8,5' }); RT = susunRetur(s, W);
ok('L: rusak/diragukan → retur + dokumen KARANTINA ber-id sama, statusTindakan belum_diputuskan', RT.dokumen.length === 2 && RT.dokumen[1].koleksi === 'karantina' && RT.dokumen[1].data.id === RT.dokumen[0].data.id && RT.dokumen[1].data.statusTindakan === 'belum_diputuskan' && RT.dokumen[1].data.asalRetur === true && RT.dokumen[1].data.totalKg === 8.5 && RT.dokumen[1].data.merkSumber === 'Angsa', JSON.stringify(RT.dokumen[1]));
terapkanKeCache(RT.dokumen); terap(RT.patch);
ok('L: barang karantina TIDAK kembali ke stok jual', chip('repack', 'Angsa').sisa === kgSebelum, chip('repack', 'Angsa').sisa + ' vs ' + kgSebelum);
terap({ rtNotaId: 's1', ketik: '1,5', rtAlasan: 'salah beli', rtKondisi: 'utuh' }); ok('L: kemasan 1,5 unit DITOLAK (unit utuh)', /UNIT utuh/.test(susunRetur(s, W).tolak || ''));
terap({ ketik: '1', rtTimpa: true, rtNominal: '80.000', rtAlasanTimpa: 'sepakat' }); ok('L: menimpa ke ATAS nilai nota (72.000) DITOLAK', /hanya boleh MENURUNKAN/.test(susunRetur(s, W).tolak || ''), susunRetur(s, W).tolak);
terap({ rtNominal: '70.000', rtAlasanTimpa: 'ok' }); ok('L: menimpa tanpa alasan cukup DITOLAK', /Alasan menimpa wajib/.test(susunRetur(s, W).tolak || ''));
terap({ rtAlasanTimpa: 'kantong sobek, disepakati 70 rb' }); RT = susunRetur(s, W); rd = RT.dokumen[0].data;
ok('L: timpa ke bawah: nominalRefund 70.000, nominalSistem 72.000, alasanTimpaNominal tercatat; kemasan {namaProduk, ukuranKemasan, jumlahUnit 1, totalKg 5}', rd.nominalRefund === 70000 && rd.nominalSistem === 72000 && /kantong sobek/.test(rd.alasanTimpaNominal) && rd.jenisAsal === 'kemasan' && rd.jumlahUnit === 1 && rd.totalKg === 5 && rd.ukuranKemasan === 5, JSON.stringify(rd));
terap({ rtNotaId: 'tidak-ada' }); ok('L: nota yang hilang DITOLAK', /tidak ditemukan lagi/.test(susunRetur(s, W).tolak || ''));
// M. TUKAR: retur diikat ke keranjang, lahir BERSAMA penjualan penggantinya
mulaiNota(); terap(Object.assign(returAwal(), { rtNotaId: 's5', ketik: '41,5', rtAlasan: 'salah beli', rtKondisi: 'tidak_utuh', rtPenyelesaian: 'tukar', tukar: null }));
RT = susunRetur(s, W); ok('M: tukar TIDAK menulis dokumen — menghasilkan ikatan {returDraf, kredit 572.700, ringkas}; draf kreditBarangGabung, selisih 0', !RT.dokumen && RT.ikat && RT.ikat.kredit === 572700 && RT.ikat.returDraf.tukarModel === 'kreditBarangGabung' && RT.ikat.returDraf.selisihHargaTukar === 0 && RT.ikat.returDraf.nominalRefund === 572700 && RT.ikat.returDraf.penyelesaian === 'tukar' && /Angsa 41,5 kg/.test(RT.ikat.ringkas), JSON.stringify(RT));
terap({ pesananId: 'x' }); terap(ikatTukar(s, RT.ikat)); terap(RT.patch);
ok('M: ikatan terpasang; ikatan pesanan dilepas (saling meniadakan); retur BELUM tercatat', s.tukar && s.tukar.kredit === 572700 && s.pesananId === null && !cacheAda('retur', RT.ikat.returDraf.id));
ok('M: mengikat tukar kedua ke keranjang yang sama DITOLAK', /MASIH terikat tukar/.test(ikatTukar(s, RT.ikat).kabar || ''));
terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '1' }); terap(masukkan(s)); t = hitungTagihan(s);
ok('M: pengganti 72.000 < retur 572.700 → DITOLAK (toko mengembalikan uang belum bisa di alur ini)', t.bersih < 0 && /lebih besar dari keranjang pengganti/.test(alasanTolak(s)), alasanTolak(s));
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '1' }); terap(masukkan(s)); t = hitungTagihan(s);
ok('M: tagihan = 762.000 − 572.700 = 189.300 → pembulatan atas SELISIH +200 → pembeli bayar 189.500', t.kredit === 572700 && t.bersih === 189300 && t.bulat === 200 && t.total === 189500, JSON.stringify(t));
terap(pilihCara(s, 'Kredit')); ok('M: tukar dicatat BON DITOLAK', /Tukar tidak bisa dicatat BON/.test(alasanTolak(s)), alasanTolak(s)); terap(pilihCara(s, 'Tunai'));
terap(tambahUang(s, 100000)); ok('M: tukar dibayar sebagian DITOLAK (bukan jadi bon)', /tidak bisa dibayar sebagian/.test(alasanTolak(s)), alasanTolak(s));
terap(tambahUang(s, 100000)); ok('M: 200.000 → kembalian 10.500 dari yang DIBAYAR (bukan dari nilai keranjang)', hitungTagihan(s).kembalian === 10500 && alasanTolak(s) === '', alasanTolak(s));
terap(parkir(s)); ok('M: parkir membawa ikatan tukar', s.tukar === null && ((s.antrean[0] || { beku: {} }).beku.tukar || {}).kredit === 572700); terap(pakaiAntrean(s, (s.antrean[0] || {}).id)); ok('M: dibuka lagi → ikatan kembali', s.tukar && s.tukar.kredit === 572700);
ok('M: keranjang terikat tukar tidak bisa diikat pesanan', /terikat TUKAR/.test(ikatPesanan(s, 'apa-saja-yang-ada').kabar || '') || /tuntas/.test(ikatPesanan(s, 'x').kabar || ''));
R = simpanNota(s, W); ok('M: nota tukar sah', !R.tolak, R.tolak); N = R.nota || { dokumen: [], ringkas: '', trxId: null };
pj = N.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).map(function (x) { return x.data; }); var rdT = N.dokumen.filter(function (x) { return x.koleksi === 'retur'; }).map(function (x) { return x.data; }); var kr = N.dokumen.filter(function (x) { return x.koleksi === 'karantina'; }); var r0 = rdT[0] || { hitunganTukarSistem: {} }; var k0 = kr[0] || { data: {} };
ok('M: SATU tulisan: 2 penjualan + 1 retur + 1 karantina (barang rusak)', pj.length === 2 && rdT.length === 1 && kr.length === 1 && k0.data.id === r0.id, JSON.stringify(N.dokumen.map(function (x) { return x.koleksi; })));
ok('M: tiap penjualan pengganti membawa tukarReturId = id retur; dicatat PENUH 72.000 + 690.200 (pembulatan 200 di baris terakhir); kembalian 10.500', pj.every(function (p) { return p.tukarReturId === String(r0.id) && p.caraBayar === 'Tunai' && p.kembalian === 10500 && p.uangDiterima === 200000; }) && pj.length === 2 && pj[0].hargaTotal === 72000 && pj[1].hargaTotal === 690200 && pj[1].pembulatan === 200, JSON.stringify(pj));
ok('M: retur lahir di jam nota, menunjuk trx penggantinya, hitunganTukarSistem {pengganti 762.000, kredit 572.700, bersih 189.300, pembulatan 200, dibayarPembeli 189.500, dikembalikanToko 0}', r0.jam === '10:15' && r0.penjualanPenggantiTrxId === String(N.trxId) && r0.hitunganTukarSistem.pengganti === 762000 && r0.hitunganTukarSistem.kredit === 572700 && r0.hitunganTukarSistem.bersih === 189300 && r0.hitunganTukarSistem.pembulatan === 200 && r0.hitunganTukarSistem.dibayarPembeli === 189500 && r0.hitunganTukarSistem.dikembalikanToko === 0 && r0.hitunganTukarSistem.caraBayar === 'Tunai' && r0.nominalRefund === 572700, JSON.stringify(r0));
ok('M: ringkasan menyebut TUKAR & yang dibayar pembeli', /TUKAR: barang kembali Rp572\.700 · pembeli bayar Rp189\.500/.test(N.ringkas), N.ringkas);
terapkanKeCache(N.dokumen); terap(R.patch || {});
ok('M: sesudah dicatat: ikatan lepas, retur ADA di data, notaTerakhir ingat returnya', s.tukar === null && cacheAda('retur', r0.id) && s.notaTerakhir && s.notaTerakhir.retur && s.notaTerakhir.retur.karantina === true);
P = susunPembatalan(s.notaTerakhir, 'uji', W) || { dokumen: [], hapus: [] };
ok('M: batalkan nota tukar → 2 baris dibatalkan + retur & karantinanya DICABUT (lahir bersama, pergi bersama)', P.dokumen.filter(function (x) { return x.koleksi === 'penjualan'; }).length === 2 && P.hapus.some(function (x) { return x.koleksi === 'retur' && x.id === r0.id; }) && P.hapus.some(function (x) { return x.koleksi === 'karantina' && x.id === r0.id; }), JSON.stringify(P.hapus));
terapkanKeCache(P.dokumen); terapkanKeCache(P.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; }));
// draf dibaca ULANG saat mencatat: nota yang sama diretur habis dari perangkat lain sesudah diikat
mulaiNota(); terap(Object.assign(returAwal(), { rtNotaId: 's5', ketik: '50', rtAlasan: 'salah beli', rtKondisi: 'utuh', rtPenyelesaian: 'tukar', tukar: null })); RT = susunRetur(s, W); terap(ikatTukar(s, RT.ikat)); terap(RT.patch);
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '1' }); terap(masukkan(s)); terap(uangPas(s)); ok('M: tukar 50 kg (sisa nota 50) sah', alasanTolak(s) === '', alasanTolak(s));
terapkanKeCache([{ koleksi: 'retur', data: { id: 'rLain', tanggal: '2026-09-19', jenisAsal: 'karung', merkSumber: 'Angsa', totalKg: 30, notaAsalId: 's5', jumlahDikembalikan: 30, kondisi: 'utuh', penyelesaian: 'refund', nominalRefund: 414000 } }]);
ok('M: perangkat lain meretur 30 kg dari nota yang sama → mencatat tukar 50 kg DITAHAN (sisa tinggal 20)', /melebihi sisa nota/.test(alasanTolak(s)), alasanTolak(s));
terapkanKeCache([{ koleksi: 'retur', hapus: 'rLain' }]); terap(batalTukar(s)); ok('M: batal tukar → ikatan lepas, keranjang tetap, retur tidak pernah tercatat', s.tukar === null && s.keranjang.length === 1);

// ================= PUTARAN 6: tata letak per ukuran (termurah dulu) & WADAH LITERAN bergunung =================
mulaiNota(); terap(Object.assign(returAwal(), { tukar: null }));
pasok('katalogHargaKemasan', [{ id: 'hm1', merk: 'Kembang', ukuran: 5, hargaPerUnit: 72000 }, { id: 'hm2', merk: 'Angsa', ukuran: 25, hargaPerUnit: 340000 }, { id: 'hm3', merk: 'Melati', ukuran: 5, hargaPerUnit: 65000 }, { id: 'hm4', merk: 'Melati', ukuran: 10, hargaPerUnit: 128000 }]);
pasok('produksiKemasan', cacheMentah('produksi').concat([{ id: 'p2', tanggal: '2026-09-02', namaProduk: 'Melati', ukuranKemasan: 5, jumlahUnit: 20, hppPerUnit: 60000 }, { id: 'p3', tanggal: '2026-09-02', namaProduk: 'Melati', ukuranKemasan: 10, jumlahUnit: 10, hppPerUnit: 118000 }]));
pasok('katalogHargaLiteran', [{ id: 'hl1', merk: 'Angsa', hargaPerLiter: 13500 }, { id: 'hl2', merk: 'IR64 Apex', hargaPerLiter: 12500 }]);
rak = susunRak(s);
ok('N: kemasan dikelompokkan per ukuran seperti papan harga toko — "5 kg" lalu "10 kg"; dalam kelompok dari TERMURAH (Melati 65.000 sebelum Kembang 72.000)', rak.kelompok.kemasan.map(function (g) { return g.judul; }).join() === '5 kg,10 kg' && rak.kelompok.kemasan[0].daftar.map(function (c) { return c.nama; }).join() === 'Melati,Kembang' && rak.kelompok.kemasan[1].daftar[0].nama === 'Melati', JSON.stringify(rak.kelompok.kemasan.map(function (g) { return [g.judul, g.daftar.map(function (c) { return c.nama + ':' + c.harga; })]; })));
ok('N: karung dikelompokkan "Karung 50 kg" lalu "Karung 25 kg"', rak.kelompok.karung.map(function (g) { return g.judul; }).join() === 'Karung 50 kg,Karung 25 kg', JSON.stringify(rak.kelompok.karung.map(function (g) { return g.judul; })));
ok('N: literan dari termurah: IR64 Apex 12.500 sebelum Angsa 13.500; repack: Angsa 13.800 sebelum Apex 14.600', rak.literan.map(function (c) { return c.nama; }).join() === 'IR64 Apex,Angsa' && rak.repack.map(function (c) { return c.nama; }).join() === 'Angsa,IR64 Apex', JSON.stringify([rak.literan.map(function (c) { return c.nama; }), rak.repack.map(function (c) { return c.nama; })]));
ok('O: Angsa & IR64 Apex = WADAH kotak; belum pernah ditandai isi ulang → isi TIDAK diketahui (layar menolak menggambar isinya, bukan menebak penuh)', chip('literan', 'Angsa').wadah.wadah === true && chip('literan', 'Angsa').wadah.diketahui === false, JSON.stringify(chip('literan', 'Angsa').wadah));
ok('O: merek di luar daftar wadah (mis. Kembang) bukan wadah; menandainya ditolak', tinggiWadah('Kembang', s) === null && /bukan wadah/.test(susunIsiUlangWadah('Kembang', W).tolak || ''));
var IU = susunIsiUlangWadah('Angsa', { tanggal: '2026-09-19', jam: '09:30', idUnik: W.idUnik });
ok('O: tandai isi ulang = SATU dokumen wadahLiteran {wadah, tipe isi, isiKg 50, tanggal, jam} — tidak menyentuh penjualan/stok', IU.dokumen.length === 1 && IU.dokumen[0].koleksi === 'wadahLiteran' && IU.dokumen[0].data.wadah === 'Angsa' && IU.dokumen[0].data.tipe === 'isi' && IU.dokumen[0].data.isiKg === 50 && IU.dokumen[0].data.jam === '09:30', JSON.stringify(IU.dokumen));
var kgSblm = chip('repack', 'Angsa').sisa; terapkanKeCache(IU.dokumen);
ok('O: sesudah ditandai: penuh 50 kg, gunung 1, isi dalam 1, belum perlu isi ulang; STOK merek tidak berubah (alat ukur, bukan stok)', chip('literan', 'Angsa').wadah.sisaKg === 50 && chip('literan', 'Angsa').wadah.gunung === 1 && chip('literan', 'Angsa').wadah.dalam === 1 && chip('literan', 'Angsa').wadah.perluIsi === false && chip('repack', 'Angsa').sisa === kgSblm, JSON.stringify(chip('literan', 'Angsa').wadah));
terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '10' }); terap(masukkan(s));
ok('O: 10 L (8,2 kg) MASUK KERANJANG → gunung langsung turun: sisa 41,8 kg, gunung (0,836−0,6)/0,4 = 0,59', chip('literan', 'Angsa').wadah.sisaKg === 41.8 && Math.abs(chip('literan', 'Angsa').wadah.gunung - 0.59) < 0.001, JSON.stringify(chip('literan', 'Angsa').wadah));
terap(parkir(s)); ok('O: struk diparkir tetap dihitung (berasnya sudah keluar dari wadah)', chip('literan', 'Angsa').wadah.sisaKg === 41.8); terap(buangAntrean(s, s.antrean[0].id)); ok('O: struk dibuang → gunung kembali 50', chip('literan', 'Angsa').wadah.sisaKg === 50);
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w1', tanggal: '2026-09-19', jam: '09:45', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 30, totalKg: 24.6, hargaTotal: 405000, hppTotalSaatJual: 330000 } },
  { koleksi: 'penjualan', data: { id: 'w0', tanggal: '2026-09-19', jam: '09:00', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 20, totalKg: 16.4, hargaTotal: 270000, hppTotalSaatJual: 220000 } }]);
var wd = chip('literan', 'Angsa').wadah;
ok('O: hanya literan SESUDAH tanda 09:30 yang mengurangi (09:45 → 24,6 kg; yang 09:00 tidak): sisa 25,4 kg = 50,8% → gunung HILANG (rata), isi dalam 0,847', wd.sisaKg === 25.4 && wd.gunung === 0 && Math.abs(wd.dalam - 0.8467) < 0.001 && wd.perluIsi === false, JSON.stringify(wd));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w2', tanggal: '2026-09-19', jam: '11:00', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 20, totalKg: 16.4, hargaTotal: 270000, hppTotalSaatJual: 220000 } }]);
wd = chip('literan', 'Angsa').wadah; ok('O: tersisa 9 kg (≤ 10) → PERLU ISI ULANG', wd.sisaKg === 9 && wd.perluIsi === true, JSON.stringify(wd));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w3', tanggal: '2026-09-19', jam: '11:30', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 20, totalKg: 16.4, hargaTotal: 270000, hppTotalSaatJual: 220000 } }]);
wd = chip('literan', 'Angsa').wadah; ok('O: terjual lebih dari isi tanda (lupa menandai) → sisa 0, selisihnya DILAPORKAN 7,4 kg, tetap perlu isi', wd.sisaKg === 0 && wd.lewat === 7.4 && wd.perluIsi === true, JSON.stringify(wd));
terapkanKeCache(susunIsiUlangWadah('Angsa', { tanggal: '2026-09-19', jam: '11:40', idUnik: W.idUnik }).dokumen);
ok('O: ditandai isi ulang lagi 11:40 → gunung MUNCUL KEMBALI (50 kg), wadah lain tidak ikut', chip('literan', 'Angsa').wadah.sisaKg === 50 && chip('literan', 'Angsa').wadah.gunung === 1 && chip('literan', 'IR64 Apex').wadah.diketahui === false);
ok('O: literan merek lain / karung / kemasan tidak mengurangi wadah Angsa', (function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w4', tanggal: '2026-09-19', jam: '12:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 1, totalKg: 50, hargaTotal: 690000, hppTotalSaatJual: 650000 } }]); var x = chip('literan', 'Angsa').wadah.sisaKg; terapkanKeCache([{ koleksi: 'penjualan', hapus: 'w4' }]); return x === 50; })());

// kunci dokumen yang dihasilkan — dibandingkan python dengan kunci yang DITULIS index.html (cadangan toko belum punya retur bernota)
var KUNCI = { retur: {}, karantina: {} };
[rd, r0].forEach(function (d) { Object.keys(d || {}).forEach(function (k) { KUNCI.retur[k] = 1; }); });
Object.keys(k0.data || {}).forEach(function (k) { KUNCI.karantina[k] = 1; });
print(JSON.stringify({ lulus: lulus, gagal: gagal, kunci: { retur: Object.keys(KUNCI.retur), karantina: Object.keys(KUNCI.karantina) } }));
"""

ASAP = r"""
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var s = keadaanAwal(); sinkronKeranjang(s); var rak = susunRak(s); var hi = hariIni(s); var d = daftarPelanggan('');
// bentuk dokumen dari data toko: kunci yang dihasilkan wajib sudah dikenal baris penjualan nyata (kecuali 'pembulatan' yang lahir 5 Sep)
var dikenal = {}; (CAD.penjualan || []).forEach(function (p) { Object.keys(p).forEach(function (k) { dikenal[k] = true; }); }); dikenal.pembulatan = true;
// bendera yang ADA di kode live tapi bisa belum pernah terpakai di cadangan: bonusUnit (17633), penggantiRetur & nilaiBarangPengganti (19384)
dikenal.bonusUnit = true; dikenal.penggantiRetur = true; dikenal.nilaiBarangPengganti = true;
function terap(p) { s = Object.assign({}, s, p); sinkronKeranjang(s); }
var asing = [];
[['karung', rak.karung[0]], ['literan', rak.literan[0]], ['kemasan', rak.kemasan[0]], ['repack', rak.repack[0]]].forEach(function (x) {
  if (!x[1]) return; terap({ keranjang: [] }); terap(ketukChip(s, x[1])); terap({ ketik: x[0] === 'literan' ? '6' : '1' }); terap(masukkan(s)); terap({ uang: 0 }); terap(uangPas(s));
  susunNotaDokumen(s, { tanggal: '2026-09-11', jam: '10:00', idUnik: function () { return Math.random(); } }).dokumen.forEach(function (dk) { if (dk.koleksi !== 'penjualan') return; Object.keys(dk.data).forEach(function (k) { if (!dikenal[k]) asing.push(x[0] + ':' + k); }); });
});
print(JSON.stringify({ karung: rak.karung.length, kemasan: rak.kemasan.length, literan: rak.literan.length, repack: rak.repack.length, pesanan: daftarPesanan('').length, sering: rak.sering.length, pelanggan: d.length, tanpaHarga: rak.karung.concat(rak.kemasan, rak.literan, rak.repack).filter(function (c) { return !(c.harga > 0); }).length, kunciAsing: asing }));
"""


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True); os.unlink(p)
    if r.returncode != 0 or not r.stdout.strip().startswith('{'): return None, (r.stderr or r.stdout)[:700]
    return json.loads(r.stdout.strip().split('\n')[-1]), ''


def kunci_ditulis_index(nama_fungsi):
    """Teks fungsi-fungsi index.html yang MENULIS dokumen itu — sumber kebenaran bentuk dokumen saat data nyatanya belum ada."""
    import re
    html = open(os.path.join(AKAR, 'index.html'), encoding='utf-8').read()
    teks = ''
    for nm in nama_fungsi:
        m = re.search(r'\n  (?:async )?function ' + nm + r'\(', html)
        if not m: continue
        akhir = re.search(r'\n  (?:async )?function \w+\(', html[m.end():])
        teks += html[m.start(): m.end() + (akhir.start() if akhir else 20000)]
    return teks


def utama(js):
    h, e = jalan(js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e]
    gagal = h['gagal']
    # bentuk dokumen retur & karantina: tiap kunci yang ditulis sistem baru harus kunci yang juga ditulis index.html
    sumber = {'retur': kunci_ditulis_index(['simpanRetur', 'simpanKeranjangJual', 'tkIkatRetur']), 'karantina': kunci_ditulis_index(['tulisReturDanKarantina'])}
    import re
    for kol, daftar in (h.get('kunci') or {}).items():
        asing = [k for k in daftar if not re.search(r'\b' + re.escape(k) + r'\s*[:=]|\b' + re.escape(k) + r'\b\s*[,}]|\.' + re.escape(k) + r'\s*=', sumber.get(kol, ''))]
        if asing: gagal.append('kunci dokumen %s yang TIDAK ditulis index.html: %s' % (kol, asing))
        if not daftar: gagal.append('kunci dokumen %s kosong — skenario tidak menghasilkannya' % kol)
    return h['lulus'], gagal


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
            # ---- putaran 3 ----
            'repacking tidak menimba kolam kg (stok karung tidak turun)': js.replace("(b.trx.jenis === 'karung' || b.trx.jenis === 'literan' || b.trx.jenis === 'repacking')", "(b.trx.jenis === 'karung' || b.trx.jenis === 'literan')"),
            'repacking tanpa langit-langit kg': js.replace("if (chip.jalur === 'repack') return bebasKg(chip.kunci);", "if (chip.jalur === 'repack') return null;"),
            'bonus ikut ditagih (uang = unit + bonus)': js.replace("const nilai = Math.round(t.hargaSatuan * t.jumlah);", "const nilai = Math.round(t.hargaSatuan * (t.jumlahUnit || t.jumlah));"),
            'bonus tidak memotong stok & HPP': js.replace("const bonus = e.bonusUnit ? 1 : 0; const unit = j + bonus;", "const bonus = e.bonusUnit ? 1 : 0; const unit = j;"),
            'pemeriksaan stok buta bonus': js.replace("const butuhStok = (t) => t.jenis === 'kemasan' ? t.jumlah + (t.bonusUnit || 0) : t.jumlah;", "const butuhStok = (t) => t.jumlah;"),
            'pengganti retur tetap memakan omzet': js.replace("if (penggantiRetur) { t.penggantiRetur = true; t.nilaiBarangPengganti = nilai; t.hargaTotal = 0; }", "if (penggantiRetur) { t.penggantiRetur = true; t.nilaiBarangPengganti = nilai; t.hargaTotal = nilai; }"),
            'penjaga model B dilewati (tukar bernota tidak diperingatkan)': js.replace("if (nyalakan && s.penggantiTanya !== id) {", "if (false) {"),
            'pesanan tidak ditutup saat nota dicatat': js.replace("if (ps && pesananBelumTuntas(ps)) { dokumen.push(pesananGanti(ps, 'dibayar', w, trxId));", "if (false) { dokumen.push(pesananGanti(ps, 'dibayar', w, trxId));"),
            'parkir melepas ikatan pesanan (pindah ke pembeli berikutnya)': js.replace("potongan: s.potongan, pesananId: s.pesananId || null, tukar:", "potongan: s.potongan, pesananId: null, tukar:"),
            'pembatalan nota tidak memulihkan pesanan': js.replace("if (ps && ps.status === 'dibayar' && String(ps.trxIdJual) === String(notaTerakhir.trxId)) dokumen.push", "if (false) dokumen.push"),
            'pesanan bisa langsung DIBAYAR tanpa nota (majukan dua kali)': js.replace("if (ps.status !== 'dipesan') return { tolak:", "if (false) return { tolak:"),
            'nota atas pesanan yang sudah batal tetap lolos': js.replace("if (s.pesananId) { const ps = ambilPesananDoc(s.pesananId); if (!ps || !pesananBelumTuntas(ps)) return", "if (false) { return"),
            # ---- putaran 4: retur & tukar ----
            'nilai retur ikut memuat pembulatan tunai nota': js.replace("const bersih = (p.hargaTotal || 0) - (p.pembulatan || 0);", "const bersih = (p.hargaTotal || 0);"),
            'retur melebihi sisa nota lolos': js.replace("if (jml > d.sisa) return { tolak: rtKalimatLebih(d, jml) };", ""),
            'retur yang sudah terjadi tidak mengurangi sisa nota': js.replace(".reduce((a, r) => a + (r.jumlahDikembalikan || 0), 0);\n    const sisa", ".reduce((a, r) => a + 0, 0);\n    const sisa"),
            'nota KREDIT boleh di-refund (uang keluar padahal belum dibayar)': js.replace("if (caraBayarKunci(t) === 'kredit') {", "if (false) {"),
            'alasan retur tidak wajib': js.replace("if (!catatan) return { tolak: 'Pilih / isi alasan retur dulu", "if (false) return { tolak: 'Pilih / isi alasan retur dulu"),
            'kondisi barang tidak wajib dijawab': js.replace("if (s.rtKondisi !== 'utuh' && s.rtKondisi !== 'tidak_utuh') return", "if (false) return"),
            'barang rusak tidak masuk karantina': js.replace("if (draf.kondisi === 'tidak_utuh') dokumen.push(dokumenKarantina(draf));", ""),
            'menimpa nominal boleh MENAIKKAN': js.replace("if (nominal > nilai) return { tolak:", "if (false) return { tolak:"),
            'kemasan boleh diretur pecahan unit': js.replace("if (d.satuan === 'unit' && Math.round(jml) !== jml) return", "if (false) return"),
            'tukar menulis retur SEKARANG (tanpa pengganti → kas kurang)': js.replace("if (draf.penyelesaian === 'tukar') {", "if (false) {"),
            'kredit tukar tidak dipotong dari tagihan': js.replace("const kredit = s.tukar ? Math.round(s.tukar.kredit || 0) : 0;", "const kredit = 0;"),
            'pembulatan tukar atas keranjang penuh, bukan selisih': js.replace("const bulatNota = pembulatanTagihan(totalSetelahPot - kreditTukar, cara);", "const bulatNota = pembulatanTagihan(totalSetelahPot, cara);"),
            'tukar boleh dicatat BON': js.replace("if (s.cara === 'Kredit') return 'Tukar tidak bisa dicatat BON", "if (false) return 'Tukar tidak bisa dicatat BON"),
            'tukar boleh dibayar sebagian': js.replace("if (t.uang > 0 && t.uang < t.total) return 'Tukar tidak bisa dibayar sebagian", "if (false) return 'Tukar tidak bisa dibayar sebagian"),
            'pengganti lebih murah dari retur lolos': js.replace("if (t.bersih < 0) return 'Nilai retur '", "if (false) return 'Nilai retur '"),
            'penjualan pengganti tanpa tukarReturId': js.replace("if (tk) d.tukarReturId = String(tk.returDraf.id);", ""),
            'retur tukar tidak ikut ditulis bersama notanya': js.replace("    dokumen.push({ koleksi: 'retur', data: rd });\n", ""),
            'kembalian tukar dihitung dari nilai keranjang': js.replace("d.kembalian = Math.max(0, uang - (totalBayar - kreditTukar));", "d.kembalian = Math.max(0, uang - totalBayar);"),
            'pembatalan nota tukar meninggalkan returnya': js.replace("if (notaTerakhir.retur) { hapus.push({ koleksi: 'retur', id: notaTerakhir.retur.id });", "if (false) { hapus.push({ koleksi: 'retur', id: notaTerakhir.retur.id });"),
            'parkir melepas ikatan tukar': js.replace("pesananId: s.pesananId || null, tukar: s.tukar || null };", "pesananId: s.pesananId || null, tukar: null };"),
            'draf tukar tidak dibaca ulang saat mencatat': js.replace("const cek = cekDrafTukar(s.tukar.returDraf); if (cek) return cek;", ""),
            # ---- putaran 6: tata letak & wadah ----
            'kemasan tidak diurutkan dari termurah': js.replace("rak.kemasan.sort((a, b) => a.ukuranKg - b.ukuranKg || termurah(a, b));", "rak.kemasan.sort((a, b) => a.ukuranKg - b.ukuranKg || b.harga - a.harga);"),
            'kemasan tidak dikelompokkan per ukuran': js.replace("kemasan: kelompokkan(rak.kemasan, (c) => c.ukuranKg,", "kemasan: kelompokkan(rak.kemasan, (c) => 0,"),
            'wadah yang belum pernah ditandai digambar PENUH (ditebak)': js.replace("if (!tanda) return { wadah: true, diketahui: false, penuhKg: WADAH_PENUH };", "if (!tanda) return { wadah: true, diketahui: true, sisaKg: 50, gunung: 1, dalam: 1, perluIsi: false };"),
            'literan SEBELUM tanda isi ulang ikut mengurangi': js.replace("p.merkSumber === merk && cap(p) > sejak ? (p.totalKg || 0) : 0), 0);", "p.merkSumber === merk ? (p.totalKg || 0) : 0), 0);"),
            'keranjang tidak menurunkan gunung': js.replace("const dipegang = literKeranjang(s && s.keranjang) +", "const dipegang = 0 * literKeranjang(s && s.keranjang) + 0 *"),
            'gunung tidak pernah hilang (tanpa ambang rata)': js.replace("gunung: Math.max(0, Math.min(1, (bagian - WADAH_RATA_BAGIAN) / (1 - WADAH_RATA_BAGIAN))),", "gunung: bagian,"),
            'tidak pernah minta isi ulang': js.replace("perluIsi: sisaKg <= WADAH_ULANG,", "perluIsi: false,"),
            'kelebihan jual sesudah tanda disembunyikan': js.replace("lewat: sisaKg < 0 ? -sisaKg : 0,", "lewat: 0,"),
            'tanda isi ulang satu wadah mengisi semua wadah': js.replace("ambilWadahLiteran().filter((w) => w.wadah === merk && w.tipe === 'isi')", "ambilWadahLiteran().filter((w) => w.tipe === 'isi')"),
            'karung/kemasan ikut mengurangi wadah': js.replace("a + (p.jenis === 'literan' && p.merkSumber === merk && cap(p) > sejak", "a + (p.merkSumber === merk && cap(p) > sejak"),
            'dokumen retur membawa kunci yang tidak dikenal index.html': js.replace("kondisi: s.rtKondisi, penyelesaian:", "kunciAsingUji: 1, kondisi: s.rtKondisi, penyelesaian:"),
            'dokumen karantina membawa kunci yang tidak dikenal index.html': js.replace("statusTindakan: 'belum_diputuskan' } };", "statusTindakan: 'belum_diputuskan', kunciAsingUji: 1 } };"),
            'dua tukar diikat ke satu keranjang': js.replace("if (s.tukar) return { kabar: 'Keranjang ini MASIH terikat tukar: '", "if (false) return { kabar: 'Keranjang ini MASIH terikat tukar: '"),
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
        else: print('ASAP DATA TOKO (%s): rak karung %d · kemasan %d · literan %d · repack %d · pesanan aktif %d · sering %d · pelanggan %d · chip tanpa harga %d · kunci dokumen asing %s' % (os.path.basename(cad[-1]), h['karung'], h['kemasan'], h['literan'], h['repack'], h['pesanan'], h['sering'], h['pelanggan'], h['tanpaHarga'], h['kunciAsing'] or 'nihil'))
        if h and (h['karung'] == 0 or h['tanpaHarga'] > 0 or h['kunciAsing']): g.append('asap: rak kosong, chip tanpa harga, atau kunci dokumen yang tidak dikenal baris nyata')
    sys.exit(2 if g else 0)
