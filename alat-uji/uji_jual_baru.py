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
MODUL = bundel_baru.MODUL_DATA + ['baru/js/inti/format.js', 'baru/js/layar/retur-logika.js', 'baru/js/layar/wadah-jual-logika.js', 'baru/js/layar/struk-logika.js', 'baru/js/layar/jual-logika.js', 'baru/js/layar/karcis-logika.js']

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
                       {'id': 'l2', 'tanggal': '2026-09-01', 'jenis': 'paperbag10l', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 39500},
                       # karung bekas tercatat "beli" 1.000 lembar Rp1.000 → modal Rp1/lembar (pola salah satuan yang ada di buku toko; ANGKA CONTOH)
                       {'id': 'l3', 'tanggal': '2026-09-01', 'jenis': 'karungbekas', 'tipe': 'beli', 'jumlah': 1000, 'hargaTotal': 1000}],
  # putaran 15 — kantong kosong (wadah): 5 kg Kembang/BMW dibeli 100 lembar Rp112.500 (Rp1.125/lembar), 10 terpakai; 5 kg Putri Agri cuma opname 20 (tanpa harga beli)
  'stokBahanKemasan': [{'id': 'k1', 'tanggal': '2026-09-01', 'jenis': '5kg_kembangbmw', 'tipe': 'beli', 'jumlah': 100, 'hargaTotal': 112500},
                       {'id': 'k2', 'tanggal': '2026-09-02', 'jenis': '5kg_kembangbmw', 'tipe': 'pakai', 'jumlah': 10, 'hargaTotal': 0},
                       {'id': 'k3', 'tanggal': '2026-09-02', 'jenis': '5kg_putriagri', 'tipe': 'opname', 'jumlah': 20, 'hargaTotal': 0}],
  # harga jual wadah per lembar (katalog baru, id = jenis): kantong 5 kg Kembang/BMW Rp2.000, karung bekas Rp1.500, 5 kg Putri Agri Rp2.500; paper bag 10 L TIDAK diberi harga
  'hargaWadah': [{'id': '5kg_kembangbmw', 'jenis': '5kg_kembangbmw', 'harga': 2000, 'tanggal': '2026-09-10'}, {'id': 'karungbekas', 'jenis': 'karungbekas', 'harga': 1500, 'tanggal': '2026-09-10'},
                 {'id': '5kg_putriagri', 'jenis': '5kg_putriagri', 'harga': 2500, 'tanggal': '2026-09-10'}],
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
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '0,3' }); p = masukkan(s); ok('0,3 karung ditolak (bukan kelipatan setengah)', s.keranjang.length === 2 && /setengah/.test(p.kabar), p.kabar);
ok('tuts koma BOLEH untuk karung (setengah karung, owner 22 Sep) dan literan, TIDAK untuk kemasan', tekanTuts(Object.assign({}, s, { ketik: '1' }), ',').ketik === '1,' && tekanTuts(Object.assign({}, s, { ketik: '1', pilih: rak.kemasan[0] }), ',').ketik === undefined && tekanTuts(Object.assign({}, s, { ketik: '1,', pilih: rak.literan[0] }), ',').ketik === undefined, JSON.stringify(tekanTuts(Object.assign({}, s, { ketik: '1' }), ',')));
terap({ lembar: null, pilih: null, ketik: '' });

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
ok('O: SAMAKAN wadah = SATU dokumen wadahLiteran {wadah, tipe isi, isiKg 50 (bawaan: rata), tanggal, jam} — tidak menyentuh penjualan/stok', IU.dokumen.length === 1 && IU.dokumen[0].koleksi === 'wadahLiteran' && IU.dokumen[0].data.wadah === 'Angsa' && IU.dokumen[0].data.tipe === 'isi' && IU.dokumen[0].data.isiKg === 50 && IU.dokumen[0].data.jam === '09:30', JSON.stringify(IU.dokumen));
ok('O: samakan di luar 0..60 kg DITOLAK; 60 kg (menggunung penuh) diterima', /di antara 0 dan 60/.test(susunIsiUlangWadah('Angsa', W, '61').tolak || '') && /di antara/.test(susunIsiUlangWadah('Angsa', W, '-1').tolak || '') && susunIsiUlangWadah('Angsa', W, '60').dokumen[0].data.isiKg === 60);
var kgSblm = chip('repack', 'Angsa').sisa; terapkanKeCache(IU.dokumen);
ok('O (koreksi owner 19 Sep): 50 kg = RATA sejajar bibir kotak — isi dalam 1, gunung 0; muat 10 kg lagi sampai batas menggunung 60; STOK merek tidak berubah', chip('literan', 'Angsa').wadah.sisaKg === 50 && chip('literan', 'Angsa').wadah.gunung === 0 && chip('literan', 'Angsa').wadah.dalam === 1 && chip('literan', 'Angsa').wadah.muatKg === 10 && chip('literan', 'Angsa').wadah.perluIsi === false && chip('repack', 'Angsa').sisa === kgSblm, JSON.stringify(chip('literan', 'Angsa').wadah));
terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '10' }); terap(masukkan(s));
ok('O: 10 L (8,2 kg) MASUK KERANJANG → permukaan langsung turun: sisa 41,8 kg, isi dalam 0,836, tanpa gunung', chip('literan', 'Angsa').wadah.sisaKg === 41.8 && Math.abs(chip('literan', 'Angsa').wadah.dalam - 0.836) < 0.001 && chip('literan', 'Angsa').wadah.gunung === 0, JSON.stringify(chip('literan', 'Angsa').wadah));
terap(parkir(s)); ok('O: struk diparkir tetap dihitung (berasnya sudah keluar dari wadah)', chip('literan', 'Angsa').wadah.sisaKg === 41.8); terap(buangAntrean(s, s.antrean[0].id)); ok('O: struk dibuang → isi kembali 50', chip('literan', 'Angsa').wadah.sisaKg === 50);
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w1', tanggal: '2026-09-19', jam: '09:45', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 30, totalKg: 24.6, hargaTotal: 405000, hppTotalSaatJual: 330000 } },
  { koleksi: 'penjualan', data: { id: 'w0', tanggal: '2026-09-19', jam: '09:00', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 20, totalKg: 16.4, hargaTotal: 270000, hppTotalSaatJual: 220000 } }]);
var wd = chip('literan', 'Angsa').wadah;
ok('O: hanya literan SESUDAH titik samakan 09:30 yang mengurangi (09:45 → 24,6 kg; yang 09:00 tidak): sisa 25,4 kg → isi dalam 0,508', wd.sisaKg === 25.4 && wd.gunung === 0 && Math.abs(wd.dalam - 0.508) < 0.001 && wd.perluIsi === false, JSON.stringify(wd));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w2', tanggal: '2026-09-19', jam: '11:00', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 20, totalKg: 16.4, hargaTotal: 270000, hppTotalSaatJual: 220000 } }]);
wd = chip('literan', 'Angsa').wadah; ok('O: tersisa 9 kg (≤ 10) → PERLU ISI ULANG — dan pratinjau takar yang BELUM dicatat tidak mematikan permintaan itu', wd.sisaKg === 9 && wd.perluIsi === true && tinggiWadah('Angsa', s, 9).perluIsi === true && tinggiWadah('Angsa', s, 9).sisaKg === 18, JSON.stringify(wd));

// ---- ISI ULANG TAKAR DEMI TAKAR dari karung terbuka di belakang wadah (praktik toko: owner 13–14 Sep, koreksi 19 Sep) ----
var WT = { tanggal: '2026-09-19', jam: '11:10', idUnik: W.idUnik };
ok('P: belum ada takar / wadah belum pernah disamakan / bukan wadah → DITOLAK dengan alasannya', /Belum ada takar/.test(susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 0 }], WT, s).tolak || '') && /belum pernah disamakan/.test(susunTakarWadah('IR64 Apex', [{ merk: 'IR64 Apex', takar: 2 }], WT, s).tolak || '') && /bukan wadah/.test(susunTakarWadah('Kembang', [{ merk: 'Kembang', takar: 1 }], WT, s).tolak || ''));
ok('P: karung terbuka di belakang wadah belum pernah ditandai → TIDAK diketahui (tidak ditebak 50 kg)', karungBelakang('Angsa').diketahui === false);
var T1 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 5 }], WT, s);
ok('P: 5 takar × 1,8 kg = 9 kg → SATU dokumen {tipe takar, wadah, takar 5, kgPerTakar 1,8, kg 9, sumber[Angsa 5 takar 9 kg]}; karung belum ditandai → tidak ada karung yang dibuka diam-diam', T1.dokumen.length === 1 && T1.dokumen[0].data.tipe === 'takar' && T1.dokumen[0].data.wadah === 'Angsa' && T1.dokumen[0].data.takar === 5 && T1.dokumen[0].data.kgPerTakar === 1.8 && T1.dokumen[0].data.kg === 9 && T1.dokumen[0].data.sumber.length === 1 && T1.dokumen[0].data.sumber[0].kg === 9 && /belum pernah ditandai/.test(T1.patch.kabar), JSON.stringify(T1.dokumen));
var bukuSblm = chip('repack', 'Angsa').sisa; terapkanKeCache(T1.dokumen); wd = chip('literan', 'Angsa').wadah;
ok('P: sesudah dicatat isi wadah 9 + 9 = 18 kg, tidak lagi minta isi ulang; BUKU stok Angsa TIDAK berubah (literan memotong buku saat terjual — bukan dua kali)', wd.sisaKg === 18 && wd.perluIsi === false && wd.dituangKg === 9 && chip('repack', 'Angsa').sisa === bukuSblm, JSON.stringify(wd));
ok('P: pratinjau takar (belum dicatat) menaikkan GAMBAR saja — keputusan "perlu isi" tetap dari isi nyata', tinggiWadah('Angsa', s, 36).sisaKg === 54 && tinggiWadah('Angsa', s, 36).gunung === 0.4 && tinggiWadah('Angsa', s, 36).sisaNyataKg === 18);
ok('P: isian yang membuat wadah > 60 kg DITOLAK (layar tidak memotong diam-diam): 18 + 24×1,8 = 61,2', /melebihi 60 kg/.test(susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 24 }], WT, s).tolak || ''), susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 24 }], WT, s).tolak);
ok('P: "sampai rata" = 17 takar (18 + 30,6 = 48,6 ≤ 50); "sampai menggunung" = 23 takar (18 + 41,4 = 59,4 ≤ 60) — dibulatkan ke BAWAH, tak pernah lewat', takarSampai('Angsa', null, 50, s)[0].takar === 17 && takarSampai('Angsa', null, 60, s)[0].takar === 23, JSON.stringify([takarSampai('Angsa', null, 50, s), takarSampai('Angsa', null, 60, s)]));
// karung di belakang: buka dari tumpukan, takar mengurangi, habis → karung baru otomatis
var tpSblmBuka = tumpukanGudang('Angsa');
var BK = susunBukaKarung('Angsa', { tanggal: '2026-09-19', jam: '11:12', idUnik: W.idUnik }, 'Angsa');
ok('P: buka karung = SATU dokumen {tipe karung, merk, kg 50, wadah = di belakang wadah mana}; kabarnya menyebut tumpukan gudang turun 50 kg', BK.dokumen.length === 1 && BK.dokumen[0].data.tipe === 'karung' && BK.dokumen[0].data.merk === 'Angsa' && BK.dokumen[0].data.kg === 50 && BK.dokumen[0].data.wadah === 'Angsa' && !BK.dokumen[0].data.lepas && Math.abs(BK.gudang.dariKg - BK.gudang.keKg - 50) < 0.011 && /tumpukan gudang/.test(BK.patch.kabar) && /di belakang wadah Angsa/.test(BK.patch.kabar), JSON.stringify(BK.dokumen));
terapkanKeCache(BK.dokumen);
ok('P (owner 21 Sep): begitu karung dibuka, TUMPUKAN GUDANG nama itu turun satu karung (−50 kg, −1 karung) saat itu juga — BUKU mesin lama tidak berubah', (function () { var t = tumpukanGudang('Angsa'); return Math.abs(tpSblmBuka.kg - t.kg - 50) < 0.011 && tpSblmBuka.karung - t.karung === 1 && t.bukuKg === tpSblmBuka.bukuKg && t.diBelakangKg === 50; })(), JSON.stringify([tpSblmBuka, tumpukanGudang('Angsa')]));
ok('P: karung di belakang Angsa 50 kg; takar SEBELUM karung ini dibuka (11:10) tidak ikut mengurangi', karungBelakang('Angsa').diketahui && karungBelakang('Angsa').sisaKg === 50 && karungBelakang('Angsa').bagian === 1, JSON.stringify(karungBelakang('Angsa')));
var T2 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 20 }], { tanggal: '2026-09-19', jam: '11:15', idUnik: W.idUnik }, s); terapkanKeCache(T2.dokumen);
ok('P (inti permintaan owner): 20 takar (36 kg) dicatat → wadah 54 kg MENGGUNUNG (gunung 0,4) dan KARUNG DI BELAKANGNYA turun 50 → 14 kg', chip('literan', 'Angsa').wadah.sisaKg === 54 && chip('literan', 'Angsa').wadah.gunung === 0.4 && chip('literan', 'Angsa').wadah.dalam === 1 && karungBelakang('Angsa').sisaKg === 14 && T2.dokumen.length === 1, JSON.stringify([chip('literan', 'Angsa').wadah, karungBelakang('Angsa')]));
var tp = tumpukanGudang('Angsa');
ok('P: tumpukan gudang (perkiraan) = buku − karung terbuka − isi wadah; ketiganya berjumlah SAMA dengan buku', tp.adaBuku && Math.abs(tp.kg + tp.diBelakangKg + tp.diWadahKg - tp.bukuKg) < 0.011 && tp.diBelakangKg === 14 && tp.diWadahKg === 54 && tp.lengkap === true, JSON.stringify(tp));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w5', tanggal: '2026-09-19', jam: '11:20', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 50, totalKg: 41, hargaTotal: 675000, hppTotalSaatJual: 550000 } }]);
var T3 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 10 }], { tanggal: '2026-09-19', jam: '11:30', idUnik: W.idUnik }, s);
ok('P: karung di belakang tinggal 14 kg, isian 18 kg → karung HABIS: dokumen "karung" (otomatis, diambil dari tumpukan) ditulis LEBIH DULU, lalu takar; kabarnya menyebut itu', T3.dokumen.length === 2 && T3.dokumen[0].data.tipe === 'karung' && T3.dokumen[0].data.otomatis === true && T3.dokumen[1].data.tipe === 'takar' && /1 karung Angsa diambil dari tumpukan/.test(T3.patch.kabar), JSON.stringify(T3.dokumen));
terapkanKeCache(T3.dokumen);
ok('P: sesudahnya karung di belakang 14 + 50 − 18 = 46 kg (karung ke-2), wadah 13 + 18 = 31 kg', karungBelakang('Angsa').sisaKg === 46 && karungBelakang('Angsa').dibuka === 2 && chip('literan', 'Angsa').wadah.sisaKg === 31, JSON.stringify([karungBelakang('Angsa'), chip('literan', 'Angsa').wadah]));
// campuran 2 : 1 (dua karung BERBEDA — jawaban owner 14 Sep)
var bk4 = hitungStokKarungPerMerk();
var T4 = susunTakarWadah('Angsa', [{ merk: 'Angsa', takar: 4 }, { merk: 'IR64 Apex', takar: 2 }], { tanggal: '2026-09-19', jam: '11:35', idUnik: W.idUnik }, s);
ok('P: campuran 4 : 2 → dokumen takar bersumber DUA nama (Angsa 7,2 kg + IR64 Apex 3,6 kg = 10,8 kg); sumber tercatat per nama', T4.dokumen.length === 2 && T4.dokumen[0].data.takar === 6 && T4.dokumen[0].data.kg === 10.8 && T4.dokumen[0].data.sumber.map(function (x) { return x.merk + ':' + x.kg; }).join() === 'Angsa:7.2,IR64 Apex:3.6' && T4.hitung.banding === '4 : 2', JSON.stringify(T4.dokumen));
ok('PINDAH BUKU (keputusan owner A, 22 Sep): takar IR64 Apex ke wadah Angsa juga menulis SATU dokumen produksiKemasan jadi-karung-utuh {sumberList Apex 3,6 kg, merkTujuan Angsa, kgDipakai 3,6, ukuranKemasan 3,6 × 1 unit, modal = modal Apex, dariTakar, takarId}; takarnya menunjuk produksiId; tanpa upah/kantong', (function () { var d = T4.dokumen[1]; var q = d.data; return d.koleksi === 'produksiKemasan' && q.jadiKarungUtuh === true && q.merkTujuan === 'Angsa' && q.sumberList.length === 1 && q.sumberList[0].merk === 'IR64 Apex' && q.sumberList[0].kg === 3.6 && q.kgDipakai === 3.6 && q.ukuranKemasan === 3.6 && q.jumlahUnit === 1 && Math.abs(q.hppSumberPerKgDipakai - bk4['IR64 Apex'].hppTerakhirPerKg) < 0.001 && Math.abs(q.hppPerUnit - 3.6 * bk4['IR64 Apex'].hppTerakhirPerKg) < 0.01 && q.dariTakar === true && q.takarId === T4.dokumen[0].data.id && T4.dokumen[0].data.produksiId === q.id && q.upahRepacking === 0 && q.biayaKemasan === 0 && q.sumberKemasanList.length === 0 && /BUKU: IR64 Apex −3,6 kg → Angsa \+3,6 kg/.test(T4.patch.kabar); })(), JSON.stringify(T4.dokumen[1]) + ' | ' + T4.patch.kabar);
terapkanKeCache(T4.dokumen);
ok('PINDAH BUKU: sesudah dicatat, buku IR64 Apex turun 3,6 kg dan buku Angsa naik 3,6 kg (mesin beku membacanya sendiri); yang senama (Angsa 7,2 kg) TIDAK memindahkan buku; kemasan jadi TIDAK bertambah', (function () { var b = hitungStokKarungPerMerk(); var m = hitungStokKemasan(); return Math.abs(bk4['IR64 Apex'].sisaKg - b['IR64 Apex'].sisaKg - 3.6) < 0.011 && Math.abs(b['Angsa'].sisaKg - bk4['Angsa'].sisaKg - 3.6) < 0.011 && !Object.keys(m).some(function (k) { return /Angsa/.test(k) && m[k].unitDibuat > 0 && String(m[k].ukuranKemasan) === '3.6'; }); })(), JSON.stringify([bk4['IR64 Apex'].sisaKg, hitungStokKarungPerMerk()['IR64 Apex'].sisaKg, bk4['Angsa'].sisaKg, hitungStokKarungPerMerk()['Angsa'].sisaKg]));
ok('P: takar campuran mengurangi karung MASING-MASING merek: Angsa 46 → 38,8; karung IR64 Apex belum ditandai → tetap tidak diketahui', karungBelakang('Angsa').sisaKg === 38.8 && karungBelakang('IR64 Apex').diketahui === false);
ok('P: "sampai rata" mengikuti perbandingan 2:1 yang sedang dipakai (FPB dari 4:2): isi 41,8 → muat 1 putaran (3 takar = 5,4 kg)', (function () { var r = takarSampai('Angsa', [{ merk: 'Angsa', takar: 4 }, { merk: 'IR64 Apex', takar: 2 }], 50, s); return r[0].takar === 2 && r[1].takar === 1; })(), JSON.stringify(takarSampai('Angsa', [{ merk: 'Angsa', takar: 4 }, { merk: 'IR64 Apex', takar: 2 }], 50, s)));
var SK = susunSamakanKarung('Angsa', '12,5', { tanggal: '2026-09-19', jam: '11:36', idUnik: W.idUnik }); terapkanKeCache(SK.dokumen);
ok('P: samakan karung terbuka 12,5 kg → titik hitung baru (karung & takar sebelumnya tidak dihitung lagi); > 50 kg ditolak', karungBelakang('Angsa').sisaKg === 12.5 && karungBelakang('Angsa').dibuka === 0 && /di antara 0 dan 50/.test(susunSamakanKarung('Angsa', '51', W).tolak || ''), JSON.stringify(karungBelakang('Angsa')));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w3', tanggal: '2026-09-19', jam: '11:38', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 60, totalKg: 49.2, hargaTotal: 810000, hppTotalSaatJual: 660000 } }]);
wd = chip('literan', 'Angsa').wadah; ok('O: terjual lebih dari isinya (lupa mencatat isi ulang) → sisa 0, selisihnya DILAPORKAN 7,4 kg, tetap perlu isi', wd.sisaKg === 0 && wd.lewat === 7.4 && wd.perluIsi === true, JSON.stringify(wd));
terapkanKeCache(susunIsiUlangWadah('Angsa', { tanggal: '2026-09-19', jam: '11:40', idUnik: W.idUnik }, 60).dokumen);
ok('O: disamakan lagi 11:40 = 60 kg → GUNUNG PENUH (gunung 1), takar & penjualan sebelum titik itu tidak dihitung lagi; wadah lain tidak ikut', chip('literan', 'Angsa').wadah.sisaKg === 60 && chip('literan', 'Angsa').wadah.gunung === 1 && chip('literan', 'Angsa').wadah.dituangKg === 0 && chip('literan', 'IR64 Apex').wadah.diketahui === false, JSON.stringify(chip('literan', 'Angsa').wadah));
terapkanKeCache(susunIsiUlangWadah('IR64 Apex', { tanggal: '2026-09-19', jam: '11:05', idUnik: W.idUnik }, 30).dokumen);
ok('O: wadah IR64 Apex disamakan 30 kg pukul 11:05 → takar-takar Angsa sesudahnya TIDAK menaikkan wadah ini', chip('literan', 'IR64 Apex').wadah.sisaKg === 30 && chip('literan', 'IR64 Apex').wadah.dituangKg === 0, JSON.stringify(chip('literan', 'IR64 Apex').wadah));
ok('O: literan merek lain / karung / kemasan tidak mengurangi wadah Angsa', (function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'w4', tanggal: '2026-09-19', jam: '12:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 1, totalKg: 50, hargaTotal: 690000, hppTotalSaatJual: 650000 } }]); var x = chip('literan', 'Angsa').wadah.sisaKg; terapkanKeCache([{ koleksi: 'penjualan', hapus: 'w4' }]); return x === 60; })());
// susunan posisi & aturan — diatur owner
ok('Q: geser posisi (W1 ↔ W2), ganti beras di satu posisi (yang sudah punya wadah ditolak), lepas — murni, daftar asal tidak berubah', (function () { var d = ['A', 'B', 'C']; return geserWadah(d, 0, 1).join() === 'B,A,C' && geserWadah(d, 0, -1).join() === 'A,B,C' && gantiBerasWadah(d, 1, 'X').join() === 'A,X,C' && gantiBerasWadah(d, 1, 'C').join() === 'A,B,C' && lepasWadah(d, 1).join() === 'A,C' && d.join() === 'A,B,C'; })());
ok('Q: calon beras untuk wadah = yang punya harga literan & belum punya wadah; calon campuran = merek yang menurut buku masih ada, di luar yang sudah dipakai', calonBerasWadah(['Angsa']).join() === 'IR64 Apex' && calonCampur(['Angsa']).indexOf('Angsa') < 0 && calonCampur(['Angsa']).indexOf('IR64 Apex') >= 0, JSON.stringify([calonBerasWadah(['Angsa']), calonCampur(['Angsa'])]));
ok('Q: aturan mustahil DITOLAK — batas menggunung < rata · takar 0 · satu beras dua wadah · campuran menyebut merek dua kali', /menggunung/.test(susunAturWadah({ penuhKg: '50', puncakKg: '40', isiUlangKg: '10', takarKg: '1,8', daftar: ['A'] }, W).tolak || '') && /takar/.test(susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '0', daftar: ['A'] }, W).tolak || '') && /dua kali/.test(susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '1,8', daftar: ['A', 'A'] }, W).tolak || '') && /dua kali/.test(susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '1,8', daftar: ['A'], resep: { A: [{ merk: 'B', takar: 1 }, { merk: 'B', takar: 2 }] } }, W).tolak || ''));
var AT6 = susunAturWadah({ penuhKg: '50', puncakKg: '58', isiUlangKg: '10', takarKg: '2', daftar: ['IR64 Apex', 'Angsa'], resep: { Angsa: [{ merk: 'Angsa', takar: 2 }, { merk: 'IR64 Apex', takar: 1 }], 'IR64 Apex': [{ merk: 'IR64 Apex', takar: 1 }] } }, { tanggal: '2026-09-19', jam: '12:10', idUnik: W.idUnik });
ok('Q: dokumen atur memuat SELURUH aturan {penuhKg, puncakKg 58, isiUlangKg, takarKg 2, daftar BERURUT, resep}; resep "1 takar merek sendiri" tidak disimpan (itu bawaan)', AT6.dokumen[0].data.tipe === 'atur' && AT6.dokumen[0].data.puncakKg === 58 && AT6.dokumen[0].data.takarKg === 2 && AT6.dokumen[0].data.daftar.join() === 'IR64 Apex,Angsa' && Object.keys(AT6.dokumen[0].data.resep).join() === 'Angsa', JSON.stringify(AT6.dokumen));
terapkanKeCache(AT6.dokumen);
ok('Q: aturan owner BERLAKU: batas menggunung 58 (samakan 60 kini ditolak), takar 2 kg, posisi W1 = IR64 Apex, campuran bawaan Angsa 2 : 1', aturWadah().puncakKg === 58 && aturWadah().takarKg === 2 && aturWadah().daftar[0] === 'IR64 Apex' && resepWadah('Angsa').map(function (x) { return x.merk + x.takar; }).join() === 'Angsa2,IR64 Apex1' && resepWadah('IR64 Apex').length === 1 && /di antara 0 dan 58/.test(susunIsiUlangWadah('Angsa', W, '60').tolak || ''), JSON.stringify(aturWadah()));
ok('Q: aturan LAMA tanpa batas menggunung (ditulis sebelum koreksi 19 Sep) → sebanding bawaan: rata 40 → menggunung 48', (function () { terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: 999999, tanggal: '2026-09-19', jam: '12:20', tipe: 'atur', penuhKg: 40, isiUlangKg: 8, daftar: ['Angsa', 'IR64 Apex'] } }]); var a = aturWadah(); terapkanKeCache([{ koleksi: 'wadahLiteran', hapus: 999999 }]); return a.puncakKg === 48 && a.takarKg === 1.8 && a.penuhKg === 40; })());
terapkanKeCache([{ koleksi: 'wadahLiteran', hapus: AT6.dokumen[0].data.id }]);
ok('Q: dokumen aturan uji dihapus → bawaan kembali (rata 50 · menggunung 60 · takar 1,8 · delapan wadah)', aturWadah().dariOwner === false && aturWadah().puncakKg === 60 && aturWadah().takarKg === 1.8 && aturWadah().daftar.length === 8);

// ---- R. RANTAI STOK BERTINGKAT (owner 21 Sep): karung di belakang wadah BERNAMA, diambil dari karung sumber di gudang ----
function WR(jam) { return { tanggal: '2026-09-19', jam: jam, idUnik: W.idUnik }; }
function menutup(t) { return Math.abs(t.kg + t.diBelakangKg + t.diWadahKg - (t.bukuKg - t.pindahKeluarKg + t.pindahMasukKg)) < 0.011; }
ok('R: karung bahan campuran (lepas) TIDAK mengaku di belakang wadah senama; catatan LAMA tanpa kolom wadah (sebelum 21 Sep) tetap dikenali di belakang wadah senama', (function () {
  terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: 777001, tanggal: '2026-09-19', jam: '12:30', tipe: 'karung', merk: 'Perahu Layar', kg: 50, lepas: true } }, { koleksi: 'wadahLiteran', data: { id: 777002, tanggal: '2026-09-19', jam: '12:31', tipe: 'karung', merk: 'IR42 Value', kg: 50 } }]);
  var a = karungUntukWadah('Perahu Layar'), b = karungUntukWadah('IR42 Value'); terapkanKeCache([{ koleksi: 'wadahLiteran', hapus: 777001 }, { koleksi: 'wadahLiteran', hapus: 777002 }]);
  return a.dariCatatan === false && a.merk === 'Perahu Layar' && b.dariCatatan === true && b.merk === 'IR42 Value'; })());
ok('R: nama yang tidak ada di buku gudang DITOLAK dibuka (karung di belakang wadah selalu dari karung sumber gudang)', /tidak ada di buku gudang/.test(susunBukaKarung('Beras Khayalan', WR('12:40'), 'Angsa').tolak || ''));
ok('R: calon karung = nama di buku yang tumpukannya masih ada, dengan banyak karungnya', (function () { var c = calonKarung(); return c.length === 2 && c.every(function (t) { return t.kg > 0 && t.karung === Math.floor((t.kg + 0.0001) / 50); }) && c.map(function (t) { return t.merk; }).join() === 'Angsa,IR64 Apex'; })(), JSON.stringify(calonKarung()));
var tX0 = tumpukanGudang('IR64 Apex'), tA0 = tumpukanGudang('Angsa'), pn0 = pindahNama();   // pn0: takar campuran bagian P (2 takar Apex → wadah Angsa = 3,6 kg) sudah pindah nama
var BR = susunBukaKarung('IR64 Apex', WR('13:00'), 'Angsa'); terapkanKeCache(BR.dokumen);
ok('R (inti): karung IR64 Apex dibuka DI BELAKANG WADAH ANGSA → nama karung wadah Angsa = IR64 Apex, campuran bawaannya ikut, dan TUMPUKAN IR64 Apex turun 50 kg; buku Apex & tumpukan Angsa tidak berubah', karungUntukWadah('Angsa').merk === 'IR64 Apex' && karungUntukWadah('Angsa').dariCatatan && wadahUntukKarung('IR64 Apex') === 'Angsa' && resepWadah('Angsa').length === 1 && resepWadah('Angsa')[0].merk === 'IR64 Apex'
  && Math.abs(tX0.kg - tumpukanGudang('IR64 Apex').kg - 50) < 0.011 && tumpukanGudang('IR64 Apex').bukuKg === tX0.bukuKg && tumpukanGudang('Angsa').kg === tA0.kg, JSON.stringify([karungUntukWadah('Angsa'), tumpukanGudang('IR64 Apex')]));
ok('R (temuan tinjau 22 Sep): karung IR64 Apex di belakang ANGSA tidak ikut tergambar/terpotong di wadah IR64 APEX yang belum punya karung — wadah Apex tetap "?" dan takar ke wadah Apex TIDAK menyentuh karung milik Angsa', (function () {
  var kApex = karungBelakang('IR64 Apex', 'IR64 Apex'), kAngsa = karungBelakang('IR64 Apex', 'Angsa');
  var h = hitungTakar('IR64 Apex', [{ merk: 'IR64 Apex', takar: 4 }], s);
  return kApex.diketahui === false && kAngsa.diketahui && kAngsa.sisaKg === 50 && h.sumber[0].dari === 'IR64 Apex' && h.sumber[0].karung.diketahui === false && h.sumber[0].bukaKarung === 0 && lokasiSumber('IR64 Apex', 'Angsa') === 'Angsa'; })(), JSON.stringify([karungBelakang('IR64 Apex', 'IR64 Apex'), hitungTakar('IR64 Apex', [{ merk: 'IR64 Apex', takar: 4 }], s).sumber]));
ok('R: nama yang sama dibuka di DUA tempat → dua kolam terpisah: karung Angsa di belakang wadah Apex 50 kg, kolam Angsa di belakang wadah Angsa tidak berubah; takar Angsa ke wadah Apex mengambil dari karung di belakang Apex', (function () {
  var sblm = karungBelakang('Angsa', 'Angsa').sisaKg; var B = susunBukaKarung('Angsa', WR('13:02'), 'IR64 Apex'); terapkanKeCache(B.dokumen);
  var h = hitungTakar('IR64 Apex', [{ merk: 'Angsa', takar: 2 }], s); var T = susunTakarWadah('IR64 Apex', [{ merk: 'Angsa', takar: 2 }], WR('13:03'), s);
  var ok1 = karungBelakang('Angsa', 'IR64 Apex').sisaKg === 50 && karungBelakang('Angsa', 'Angsa').sisaKg === sblm && h.sumber[0].dari === 'IR64 Apex' && T.dokumen.length === 2 && T.dokumen[0].data.sumber[0].dari === 'IR64 Apex';
  terapkanKeCache(T.dokumen);   // dicatat: hanya kolam di belakang wadah Apex yang turun (50 → 46,4); kolam di belakang wadah Angsa tidak
  var ok2 = karungBelakang('Angsa', 'IR64 Apex').sisaKg === 46.4 && karungBelakang('Angsa', 'Angsa').sisaKg === sblm && tinggiWadah('IR64 Apex', s).dituangKg === 3.6;
  terapkanKeCache([{ koleksi: 'wadahLiteran', hapus: B.dokumen[0].data.id }, { koleksi: 'wadahLiteran', hapus: T.dokumen[0].data.id }, { koleksi: 'produksiKemasan', hapus: T.dokumen[1].data.id }]); return ok1 && ok2 && karungUntukWadah('IR64 Apex').dariCatatan === false; })(), JSON.stringify([karungBelakang('Angsa', 'IR64 Apex'), karungBelakang('Angsa', 'Angsa')]));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'r1', tanggal: '2026-09-19', jam: '13:05', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 25, totalKg: 20.5, hargaTotal: 337500, hppTotalSaatJual: 270000 } }]);
var tX1 = tumpukanGudang('IR64 Apex'), tA1 = tumpukanGudang('Angsa');
ok('R: literan Angsa TERJUAL 20,5 kg → wadah Angsa & buku Angsa turun sama besar, tumpukan Angsa TIDAK bergeser; jumlahnya menutup', Math.abs(tA0.bukuKg - tA1.bukuKg - 20.5) < 0.011 && Math.abs(tA0.diWadahKg - tA1.diWadahKg - 20.5) < 0.011 && tA1.kg === tA0.kg && menutup(tA1) && menutup(tX1), JSON.stringify([tA0, tA1]));
var bkR = hitungStokKarungPerMerk();
var TR = susunTakarWadah('Angsa', [{ merk: 'IR64 Apex', takar: 5 }], WR('13:10'), s); terapkanKeCache(TR.dokumen);
var tX2 = tumpukanGudang('IR64 Apex'), tA2 = tumpukanGudang('Angsa'), pn = pindahNama();
ok('R (inti): 5 takar (9 kg) dari karung IR64 Apex ke wadah Angsa → karung Apex 50 → 41, wadah Angsa +9; berasnya PINDAH NAMA DI BUKU (buku Apex −9, buku Angsa +9, dokumen produksi ikut) sehingga layar TIDAK menghitungnya lagi (keluar/masuk kosong), tumpukan Apex tidak naik & tumpukan Angsa tidak turun; semuanya menutup', karungBelakang('IR64 Apex').sisaKg === 41 && Math.abs(tA2.diWadahKg - tA1.diWadahKg - 9) < 0.011 && TR.dokumen.length === 2 && TR.dokumen[1].koleksi === 'produksiKemasan' && !pn.keluar['IR64 Apex'] && !pn.masuk['Angsa'] && Math.abs(bkR['IR64 Apex'].sisaKg - hitungStokKarungPerMerk()['IR64 Apex'].sisaKg - 9) < 0.011 && Math.abs(hitungStokKarungPerMerk()['Angsa'].sisaKg - bkR['Angsa'].sisaKg - 9) < 0.011 && tX2.kg === tX1.kg && tA2.kg === tA1.kg && menutup(tX2) && menutup(tA2) && /karung IR64 Apex 5/.test(TR.patch.kabar), JSON.stringify([tX2, tA2, pn, TR.patch.kabar]));
// catatan takar LAMA (sebelum pindah buku, tanpa produksiId) masih dihitung pindah nama DI LAYAR
terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: W.idUnik(), tanggal: '2026-09-19', jam: '13:20', tipe: 'takar', wadah: 'Angsa', takar: 7, kgPerTakar: 1.8, kg: 12.6, sumber: [{ merk: 'IR64 Apex', takar: 7, kg: 12.6, dari: 'Angsa' }] } }]);
// wadah Angsa diturunkan dulu lewat penjualan supaya isian berikutnya tidak melewati batas menggunung (catatan lama tadi masuk tanpa penjaga)
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'r1b', tanggal: '2026-09-19', jam: '13:22', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 25, totalKg: 20.5, hargaTotal: 337500, hppTotalSaatJual: 270000 } }]);
tX2 = tumpukanGudang('IR64 Apex'); var pnL = pindahNama();
ok('R: catatan takar LAMA (tanpa produksiId) tetap dihitung pindah nama di layar: keluar Apex 12,6 · masuk Angsa 12,6; menutup', pnL.keluar['IR64 Apex'] === 12.6 && pnL.masuk['Angsa'] === 12.6 && menutup(tX2) && menutup(tumpukanGudang('Angsa')), JSON.stringify([pnL, tX2]));
terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 1790000000000, tanggal: '2026-09-19', jam: '13:30', merk: 'IR64 Apex', kgSistem: tX2.bukuKg, kgFisik: tX2.bukuKg - 12.6, selisihKg: -12.6, alasan: 'Opname' } }]);
ok('R: hitungan gudang (cocokkan) IR64 Apex sesudah itu MENYERAP pindahan 12,6 kg ke buku → pindah-keluar Apex kembali 0 (tidak dipotong dua kali), tumpukan Apex tetap; pindah-masuk Angsa (belum dicocokkan) tetap 12,6', (function () { var p2 = pindahNama(), t = tumpukanGudang('IR64 Apex'); return !p2.keluar['IR64 Apex'] && p2.masuk['Angsa'] === 12.6 && t.kg === tX2.kg && Math.abs(t.bukuKg - (tX2.bukuKg - 12.6)) < 0.011 && menutup(t); })(), JSON.stringify([pindahNama(), tumpukanGudang('IR64 Apex')]));
terapkanKeCache(susunSamakanKarung('IR64 Apex', '2', WR('13:40'), 'Angsa').dokumen);
var tX3 = tumpukanGudang('IR64 Apex'); var TR2 = susunTakarWadah('Angsa', [{ merk: 'IR64 Apex', takar: 3 }], WR('13:45'), s);
ok('R: karung di belakang tinggal 2 kg, isian 5,4 kg → karung baru OTOMATIS: dokumen karung {merk IR64 Apex, wadah Angsa, otomatis} lebih dulu, lalu takar, lalu pindah buku; kabarnya menyebut tumpukan gudang turun 50 kg', TR2.dokumen.length === 3 && TR2.dokumen[0].data.tipe === 'karung' && TR2.dokumen[0].data.merk === 'IR64 Apex' && TR2.dokumen[0].data.wadah === 'Angsa' && TR2.dokumen[0].data.otomatis === true && TR2.dokumen[1].data.tipe === 'takar' && TR2.dokumen[2].koleksi === 'produksiKemasan' && TR2.gudang.length === 1 && Math.abs(TR2.gudang[0].dariKg - TR2.gudang[0].keKg - 50) < 0.011 && /tumpukan gudang/.test(TR2.patch.kabar), JSON.stringify([TR2.dokumen, TR2.patch.kabar]));
terapkanKeCache(TR2.dokumen);
ok('R: sesudahnya karung Apex 2 + 50 − 5,4 = 46,6 kg dan tumpukan Apex persis 50 kg lebih rendah; menutup', karungBelakang('IR64 Apex').sisaKg === 46.6 && Math.abs(tX3.kg - tumpukanGudang('IR64 Apex').kg - 50) < 0.011 && menutup(tumpukanGudang('IR64 Apex')) && menutup(tumpukanGudang('Angsa')));
var tA4 = tumpukanGudang('Angsa');
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'r2', tanggal: '2026-09-19', jam: '13:50', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 80, totalKg: 65.6, hargaTotal: 1080000, hppTotalSaatJual: 860000 } }]);
ok('R: LUPA mencatat isi ulang (terjual 65,6 kg, lebih dari isi wadah) → wadah digambar 0 + selisihnya dilaporkan, tapi hitungan tumpukan memakai angka MENTAH: tumpukan Angsa tidak bergeser diam-diam & tetap menutup', (function () { var w = tinggiWadah('Angsa', s), t = tumpukanGudang('Angsa'); return w.sisaKg === 0 && w.lewat > 0 && t.kg === tA4.kg && t.diWadahKg < 0 && menutup(t); })(), JSON.stringify([tinggiWadah('Angsa', s), tumpukanGudang('Angsa')]));
terapkanKeCache([{ koleksi: 'penjualan', hapus: 'r2' }]);
var BR3 = susunBukaKarung('IR64 Apex', WR('14:00'), 'Angsa');
ok('R: menurut buku tumpukan IR64 Apex tidak sampai satu karung → buka karung TETAP dicatat (bukunya yang mungkin salah) tapi kabarnya MEMPERINGATKAN, tidak diam', BR3.dokumen.length === 1 && BR3.patch.kabarAwas === true && /MENURUT BUKU tumpukannya tidak sampai satu karung/.test(BR3.patch.kabar) && BR3.gudang.keKg < 0, JSON.stringify(BR3.patch));
terapkanKeCache(BR3.dokumen);
ok('R: tumpukan yang sudah habis/kurang menurut buku → DISEBUT kurang (minus:true, 0 karung) dan namanya hilang dari calon karung', tumpukanGudang('IR64 Apex').minus === true && tumpukanGudang('IR64 Apex').karung === 0 && calonKarung().map(function (t) { return t.merk; }).join() === 'Angsa' && menutup(tumpukanGudang('IR64 Apex')), JSON.stringify([tumpukanGudang('IR64 Apex'), calonKarung().map(function (t) { return t.merk; })]));
terapkanKeCache([{ koleksi: 'wadahLiteran', hapus: BR3.dokumen[0].data.id }]);
// ---- temuan alur tinjau 22 Sep (dibantah agen, terbukti) — semuanya ditambal
terapkanKeCache(susunIsiUlangWadah('Angsa', WR('14:10'), 30).dokumen); var wdSblm = tinggiWadah('Angsa', s).sisaKg;
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 9000000000000, tanggal: '2026-09-19', jam: '14:10', caraBayar: 'Tunai', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 10, totalKg: 8.2, hargaTotal: 135000, hppTotalSaatJual: 110000 } }]);
ok('tinjau: nota literan di MENIT yang sama sesudah samakan (id lebih besar) ikut memotong wadah — pemutus seri id, sama seperti takar', Math.abs(wdSblm - tinggiWadah('Angsa', s).sisaKg - 8.2) < 0.011, JSON.stringify([wdSblm, tinggiWadah('Angsa', s)]));
terapkanKeCache([{ koleksi: 'penjualan', hapus: 9000000000000 }]);
// catatan takar LAMA Apex → Angsa SESUDAH cocokkan 13:30, supaya ada pindahan yang bisa dibuang keliru oleh dokumen rework
terapkanKeCache([{ koleksi: 'wadahLiteran', data: { id: W.idUnik(), tanggal: '2026-09-19', jam: '14:15', tipe: 'takar', wadah: 'Angsa', takar: 2, kgPerTakar: 1.8, kg: 3.6, sumber: [{ merk: 'IR64 Apex', takar: 2, kg: 3.6, dari: 'Angsa' }] } }]);
var pnSblm = pindahNama();
terapkanKeCache([{ koleksi: 'penyesuaianStok', data: { id: 1790000000001, tanggal: '2026-09-19', jam: '14:20', merk: 'IR64 Apex', kgSistem: null, kgFisik: null, selisihKg: 41.5, alasan: 'Rework', dariRework: true } }]);
ok('tinjau: rework dari karantina (penyesuaianStok dariRework, kgFisik null) BUKAN hitungan gudang — pindahan nama sebelumnya tidak dibuang', JSON.stringify(pindahNama()) === JSON.stringify(pnSblm) && pnSblm.keluar['IR64 Apex'] === 3.6 && (pnSblm.masuk['Angsa'] || 0) > 0, JSON.stringify([pnSblm, pindahNama()]));
terapkanKeCache([{ koleksi: 'penyesuaianStok', hapus: 1790000000001 }]);
ok('tinjau: campuran satu baris yang cuma menyalin KARUNG DI BELAKANG wadah tidak disimpan (ikut karung yang sedang terbuka), campuran sungguhan tetap disimpan', (function () { var kn = karungUntukWadah('Angsa').merk; if (kn === 'Angsa') return false;
  var A = susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '1,8', daftar: aturWadah().daftar, resep: { Angsa: [{ merk: kn, takar: 1 }] } }, WR('14:30'));
  var B = susunAturWadah({ penuhKg: '50', puncakKg: '60', isiUlangKg: '10', takarKg: '1,8', daftar: aturWadah().daftar, resep: { Angsa: [{ merk: kn, takar: 2 }, { merk: 'Angsa', takar: 1 }] } }, WR('14:31'));
  return !A.tolak && !A.dokumen[0].data.resep.Angsa && !B.tolak && B.dokumen[0].data.resep.Angsa.length === 2; })());
ok('tinjau: "samakan sisa karung" dengan kotak KOSONG / spasi ditolak (bukan 0 kg)', /Ketik dulu/.test(susunSamakanKarung('IR64 Apex', '', WR('14:40'), 'Angsa').tolak || '') && /Ketik dulu/.test(susunSamakanKarung('IR64 Apex', '   ', WR('14:40'), 'Angsa').tolak || '') && !susunSamakanKarung('IR64 Apex', '0', WR('14:40'), 'Angsa').tolak);

// ================= PUTARAN 15: WADAH DIJUAL (keputusan owner 17 Sep) =================
terap(Object.assign(keadaanAwal(), { sekarang: new Date('2026-09-19T10:00:00') }));
var rw = susunRak(s).wadah;
ok('W: rak wadah = hanya jenis BERHARGA JUAL: 5 kg Kembang/BMW · 5 kg Putri Agri · karung bekas (paper bag 10 L punya stok 100 tapi tanpa harga → tidak tampil)', rw.map(function (c) { return c.kunci; }).join() === '5kg_kembangbmw,5kg_putriagri,karungbekas', JSON.stringify(rw.map(function (c) { return c.kunci; })));
var cw = chip('wadah', '5kg_kembangbmw');
ok('W: kantong 5 kg Kembang/BMW: bebas 90 lembar (100 beli − 10 pakai), harga 2.000, modal 1.125 (rata-rata beli), margin 875 — dari mesin hitungStokBahanKemasan', cw.sisa === 90 && cw.harga === 2000 && cw.modal === 1125 && cw.adaModal === true && !cw.modalAneh && /margin Rp875/.test(cw.teksModal), JSON.stringify(cw));
var cpa = chip('wadah', '5kg_putriagri');
ok('W: kantong Putri Agri hanya opname (tanpa harga beli) → sisa 20, modal BELUM ADA (bukan Rp0), kalimatnya jujur', cpa.sisa === 20 && cpa.modal === null && cpa.adaModal === false && /belum pernah tercatat dibeli/.test(cpa.teksModal), JSON.stringify(cpa));
var ckb = chip('wadah', 'karungbekas');
ok('W: karung bekas = hasil samping: tidak dibatasi buku (tanpaBatas), modal di buku Rp1 → modalAneh & teksnya bilang catatan beli salah satuan', ckb.tanpaBatas === true && ckb.hasilSamping === true && ckb.modal === 1 && ckb.modalAneh === true && /salah satuan/.test(ckb.teksModal) && maksUntuk(ckb) === null, JSON.stringify(ckb));
terap(ketukChip(s, cw)); terap({ ketik: '6' }); terap(masukkan(s));
ok('W: 6 lembar masuk: baris jenis "wadah", jenisWadah, namaProduk "Kantong Kembang/BMW 5 kg", jumlahUnit 6, totalKg 0, hargaTotal 12.000, HPP 6.750', s.keranjang.length === 1 && s.keranjang[0].trx.jenis === 'wadah' && s.keranjang[0].trx.jenisWadah === '5kg_kembangbmw' && s.keranjang[0].trx.namaProduk === 'Kantong Kembang/BMW 5 kg' && s.keranjang[0].trx.jumlahUnit === 6 && s.keranjang[0].trx.totalKg === 0 && s.keranjang[0].trx.hargaTotal === 12000 && s.keranjang[0].trx.hppTotalSaatJual === 6750, JSON.stringify(s.keranjang[0].trx));
ok('W: rak sesudahnya: kantong 5 kg bebas 84 (90 − 6 di keranjang)', chip('wadah', '5kg_kembangbmw').sisa === 84, chip('wadah', '5kg_kembangbmw').sisa);
terap(ketukChip(s, chip('wadah', '5kg_kembangbmw'))); terap({ ketik: '85' }); p = masukkan(s);
ok('W: 85 lembar lagi ditolak — langit-langit buku kantong 84', p.kabarAwas && /bebas dijual sekarang 84 lembar/.test(p.kabar), p.kabar);
terap({ ketik: '2,5' }); p = masukkan(s); ok('W: lembar pecahan ditolak', /per lembar/.test(p.kabar), p.kabar);
terap({ ketik: '' }); ok('W: tuts koma dimatikan untuk wadah', tekanTuts(s, ',').ketik === undefined);
// contoh owner 17 Sep: 6 L literan + kemasan 5 kg (di kotak pasir: 6 × 13.500 + 2.000)
terap({ pilih: null, lembar: null }); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '6' }); terap(masukkan(s)); terap(ketukChip(s, chip('wadah', '5kg_kembangbmw'))); terap({ ketik: '1' }); terap(masukkan(s));
ok('W: contoh owner — literan 6 L (81.000) + 1 kantong 5 kg (2.000) + 6 kantong tadi (12.000) = subtotal 95.000: wadah menambah omzet', hitungTagihan(s).subtotal === 95000 && s.keranjang.length === 3, JSON.stringify(hitungTagihan(s)));
// nota: dokumen pakai id+1 di koleksi bahannya, mesin membaca stok turun & laba naik
terap({ uang: 0 }); terap(uangPas(s)); var NW = susunNotaDokumen(s, W);
var dokW = NW.dokumen.filter(function (d) { return d.koleksi === 'penjualan' && d.data.jenis === 'wadah'; }); var pakaiW = NW.dokumen.filter(function (d) { return d.koleksi === 'stokBahanKemasan'; });
ok('W: nota → 2 baris wadah + 2 dokumen stokBahanKemasan tipe pakai (id nota + 1, jumlah 6 & 1, hargaTotal 0, catatan menyebut notanya)', dokW.length === 2 && pakaiW.length === 2 && pakaiW.every(function (d, i) { return d.data.tipe === 'pakai' && d.data.jenis === '5kg_kembangbmw' && d.data.id === dokW[i].data.id + 1 && d.data.hargaTotal === 0 && /nota id/.test(d.data.catatan); }) && pakaiW.map(function (d) { return d.data.jumlah; }).join() === '6,1', JSON.stringify(pakaiW));
ok('W: baris wadah di dokumen tidak membawa isian layar (label/satuan/jumlah/hargaSatuan)', dokW.every(function (d) { return d.data.label === undefined && d.data.satuan === undefined && d.data.jumlah === undefined && d.data.hargaSatuan === undefined && d.data.hargaAsliSatuan === 2000; }), JSON.stringify(dokW[0].data));
ok('W: ringkasan nota menyebut 7 lembar wadah dijual', /7 lembar wadah dijual/.test(NW.ringkas), NW.ringkas);
var labaSblm = hitungLabaRentang(function (t) { return t === '2026-09-19'; }); var stokSblm = hitungStokBahanKemasan()['5kg_kembangbmw'].sisaPcs; var kemSblm = JSON.stringify(Object.keys(hitungStokKemasan())); var krgSblm = JSON.stringify(Object.keys(hitungStokKarungPerMerk()));
terapkanKeCache(NW.dokumen);
var labaSdh = hitungLabaRentang(function (t) { return t === '2026-09-19'; });
ok('W: MESIN BEKU membaca: buku kantong 90 → 83; omzet hari itu +95.000 (termasuk 14.000 wadah); HPP wadah 7 × 1.125 = 7.875 ikut; margin naik 14.000 − 7.875 untuk wadahnya', hitungStokBahanKemasan()['5kg_kembangbmw'].sisaPcs === stokSblm - 7 && labaSdh.omzetHitung - labaSblm.omzetHitung === 95000 && labaSdh.hpp - labaSblm.hpp === 7875 + Math.round(chip('literan', 'Angsa').hppPerKg * 4.92) + 395, JSON.stringify([labaSblm, labaSdh]));
ok('W: mesin stok BERAS tidak menyentuh baris wadah — kunci merek/kemasan tidak bertambah', JSON.stringify(Object.keys(hitungStokKemasan())) === kemSblm && JSON.stringify(Object.keys(hitungStokKarungPerMerk())) === krgSblm);
ok('W: sesudah tercatat, chip wadah kembali 83 bebas (keranjang kosong lagi)', (function () { terap({ keranjang: [] }); return chip('wadah', '5kg_kembangbmw').sisa === 83; })(), chip('wadah', '5kg_kembangbmw').sisa);
var PB = susunPembatalan({ trxId: NW.trxId, idPenjualan: NW.idPenjualan, piutangId: null, pesanan: null, retur: null }, 'uji', { kini: '2026-09-19T10:20:00.000Z' });
ok('W: pembatalan mencabut dokumen pakai kantong (2 stokBahanKemasan + 1 stokBahanLiteran kantong literan)', PB.hapus.filter(function (x) { return x.koleksi === 'stokBahanKemasan'; }).length === 2 && PB.hapus.filter(function (x) { return x.koleksi === 'stokBahanLiteran'; }).length === 1, JSON.stringify(PB.hapus));
terapkanKeCache(PB.dokumen); terapkanKeCache(PB.hapus.map(function (x) { return { koleksi: x.koleksi, hapus: x.id }; }));
ok('W: sesudah dibatalkan buku kantong pulih ke 90', hitungStokBahanKemasan()['5kg_kembangbmw'].sisaPcs === 90 && chip('wadah', '5kg_kembangbmw').sisa === 90, hitungStokBahanKemasan()['5kg_kembangbmw'].sisaPcs);
// wadah tanpa modal → baris TANPA hppTotalSaatJual → mesin laba: "tanpa HPP", bukan margin 100 %
terap(ketukChip(s, chip('wadah', '5kg_putriagri'))); terap({ ketik: '4' }); terap(masukkan(s)); terap({ uang: 0 }); terap(uangPas(s));
var NP = susunNotaDokumen(s, W); var bP = NP.dokumen.filter(function (d) { return d.koleksi === 'penjualan'; })[0].data;
ok('W: baris wadah tanpa modal: hargaTotal 10.000, TANPA kolom hppTotalSaatJual (bukan 0)', bP.hargaTotal === 10000 && !('hppTotalSaatJual' in bP), JSON.stringify(bP));
var lbA = hitungLabaRentang(function (t) { return t === '2026-09-19'; }); terapkanKeCache(NP.dokumen); var lbB = hitungLabaRentang(function (t) { return t === '2026-09-19'; });
ok('W: mesin laba menaruhnya di TANPA HPP (+1 baris, omzetTanpaHpp +10.000), margin TIDAK bergerak — labanya belum bisa disebut', lbB.jumlahTanpaHpp - lbA.jumlahTanpaHpp === 1 && lbB.omzetTanpaHpp - lbA.omzetTanpaHpp === 10000 && lbB.margin === lbA.margin && lbB.omzetPenuh - lbA.omzetPenuh === 10000, JSON.stringify([lbA, lbB]));
NP.idPenjualan.forEach(function (id) { terapkanKeCache([{ koleksi: 'penjualan', hapus: id }, { koleksi: 'stokBahanKemasan', hapus: id + 1 }]); }); terap({ keranjang: [] });
// karung bekas: tidak dibatasi buku, bukunya tetap dipotong (stokBahanLiteran)
terap(ketukChip(s, chip('wadah', 'karungbekas'))); terap({ ketik: '10' }); terap(masukkan(s));
ok('W: "jual karung bekas gak? mau 10" → 10 × 1.500 = 15.000, HPP 10 × Rp1 (modal buku) — dan modal anehnya dilaporkan di chip', s.keranjang[0].trx.hargaTotal === 15000 && s.keranjang[0].trx.hppTotalSaatJual === 10 && chip('wadah', 'karungbekas').modalAneh, JSON.stringify(s.keranjang[0].trx));
terap({ uang: 0 }); terap(uangPas(s)); var NK = susunNotaDokumen(s, W);
ok('W: dokumen pakainya masuk stokBahanLiteran (koleksi karung bekas), 10 lembar', NK.dokumen.some(function (d) { return d.koleksi === 'stokBahanLiteran' && d.data.tipe === 'pakai' && d.data.jenis === 'karungbekas' && d.data.jumlah === 10; }), JSON.stringify(NK.dokumen.map(function (d) { return d.koleksi; })));
terap({ keranjang: [] });
// parkir memegang lembar wadah; sering mengenal wadah
terap(ketukChip(s, chip('wadah', '5kg_kembangbmw'))); terap({ ketik: '50' }); terap(masukkan(s)); terap(parkir(s));
ok('W: struk parkir memegang 50 lembar → chip bebas 40 & menyebut dipegang struk lain', chip('wadah', '5kg_kembangbmw').sisa === 40 && chip('wadah', '5kg_kembangbmw').dipegang === 50, JSON.stringify(chip('wadah', '5kg_kembangbmw')));
terap(ketukChip(s, chip('wadah', '5kg_kembangbmw'))); terap({ ketik: '41' }); p = masukkan(s); ok('W: 41 ditolak, kalimat menyebut struk lain memegang 50 lembar', /40 lembar/.test(p.kabar) && /memegang 50 lembar/.test(p.kabar), p.kabar);
terap(buangAntrean(s, s.antrean[0].id)); terap({ keranjang: [], pilih: null, lembar: null });
// ---- REPACK + wadah: dijual (baris sendiri) / ditanggung toko (HPP) / upah per nota
terap(ketukChip(s, chip('repack', 'Angsa'))); terap({ ketik: '10', rpWadah: '5kg_kembangbmw', rpLembar: '2', rpDijual: true, rpUpah: '' });
ok('W: saran lembar = kg ÷ muatan dibulatkan KE ATAS: 10 kg / 5 = 2; 11 kg → 3; 25 kg karung bekas → 1; 26 → 2', saranLembar(10, '5kg_kembangbmw') === 2 && saranLembar(11, '5kg_kembangbmw') === 3 && saranLembar(25, 'karungbekas') === 1 && saranLembar(26, 'karungbekas') === 2);
terap(masukkan(s));
ok('W: repack 10 kg DIJUAL wadahnya → DUA baris: repack 10 × 13.800 = 138.000 (tanpa kemasanRepack) + wadah 2 lembar 4.000', s.keranjang.length === 2 && s.keranjang[0].trx.jenis === 'repacking' && s.keranjang[0].trx.hargaTotal === 138000 && !s.keranjang[0].trx.kemasanRepack && s.keranjang[1].trx.jenis === 'wadah' && s.keranjang[1].trx.jumlahUnit === 2 && s.keranjang[1].trx.hargaTotal === 4000 && s.rpWadah === '' && s.rpLembar === '', JSON.stringify(s.keranjang));
terap({ keranjang: [] }); terap(ketukChip(s, chip('repack', 'Angsa'))); terap({ ketik: '10', rpWadah: '5kg_kembangbmw', rpLembar: '2', rpDijual: false, rpUpah: '5.000' });
var hppRepack = Math.round(chip('repack', 'Angsa').hppPerKg * 10); terap(masukkan(s));
ok('W: repack 10 kg DITANGGUNG toko + upah 5.000 → SATU baris: hargaTotal 138.000 + 5.000 = 143.000, upahRepack 5.000, HPP = beras + 2 × 1.125, kemasanRepack tercatat', s.keranjang.length === 1 && s.keranjang[0].trx.hargaTotal === 143000 && s.keranjang[0].trx.upahRepack === 5000 && s.keranjang[0].trx.kemasanRepack === '5kg_kembangbmw' && s.keranjang[0].trx.jumlahKemasanRepackDipakai === 2 && s.keranjang[0].trx.biayaKemasanRepack === 2250 && s.keranjang[0].trx.hppTotalSaatJual === hppRepack + 2250, JSON.stringify(s.keranjang[0].trx));
ok('W: wadah yang ditanggung ikut memegang buku kantong: chip wadah bebas 88', chip('wadah', '5kg_kembangbmw').sisa === 88, chip('wadah', '5kg_kembangbmw').sisa);
var idR = s.keranjang[0].id; terap(ubahJumlahBaris(s, idR, 5));
ok('W: +5 kg membangun ulang baris dengan wadah & upah DIPERTAHANKAN: 15 × 13.800 + 5.000 = 212.000, kemasanRepack tetap 2 lembar', s.keranjang[0].trx.hargaTotal === 212000 && s.keranjang[0].trx.upahRepack === 5000 && s.keranjang[0].trx.jumlahKemasanRepackDipakai === 2, JSON.stringify(s.keranjang[0].trx));
terap(terapkanNego(s, idR, 13000)); ok('W: nego per kg tetap menyimpan upah: 15 × 13.000 + 5.000 = 200.000', s.keranjang[0].trx.hargaTotal === 200000 && s.keranjang[0].trx.upahRepack === 5000, s.keranjang[0].trx.hargaTotal);
terap({ uang: 0 }); terap(uangPas(s)); var NR = susunNotaDokumen(s, W); var bR = NR.dokumen.filter(function (d) { return d.koleksi === 'penjualan'; })[0].data;
ok('W: dokumen repack membawa kemasanRepack/jumlahKemasanRepackDipakai/biayaKemasanRepack/upahRepack + satu dokumen pakai 2 lembar; ringkasannya menyebut ditanggung toko & upah', bR.kemasanRepack === '5kg_kembangbmw' && bR.jumlahKemasanRepackDipakai === 2 && bR.upahRepack === 5000 && NR.dokumen.some(function (d) { return d.koleksi === 'stokBahanKemasan' && d.data.jumlah === 2 && /ditanggung toko/.test(d.data.catatan); }) && /2 lembar wadah ditanggung toko/.test(NR.ringkas) && /upah repack Rp5\.000/.test(NR.ringkas), NR.ringkas);
terap({ keranjang: [] }); terap(ketukChip(s, chip('repack', 'Angsa'))); terap({ ketik: '10', rpWadah: 'paperbag10l', rpLembar: '1', rpDijual: true, rpUpah: '' }); p = masukkan(s);
ok('W: wadah TANPA harga jual tidak bisa "dijual" — ditolak dengan arahan setel harga / ditanggung toko', p.kabarAwas && /belum punya harga jual/.test(p.kabar) && s.keranjang.length === 0, p.kabar);
terap({ rpDijual: false }); terap(masukkan(s)); ok('W: … tapi boleh DITANGGUNG toko (paper bag 10 L, modal 395 masuk HPP)', s.keranjang.length === 1 && s.keranjang[0].trx.kemasanRepack === 'paperbag10l' && s.keranjang[0].trx.biayaKemasanRepack === 395, JSON.stringify(s.keranjang[0].trx));
terap({ keranjang: [] }); terap(ketukChip(s, chip('repack', 'Angsa'))); terap({ ketik: '10', rpWadah: '5kg_kembangbmw', rpLembar: '95', rpDijual: false, rpUpah: '' }); p = masukkan(s);
ok('W: 95 lembar ditanggung melebihi buku 90 → ditolak ("kantong yang belum ada dibeli dulu")', p.kabarAwas && /buku 90 lembar/.test(p.kabar), p.kabar);
terap({ keranjang: [], pilih: null, lembar: null, rpWadah: '', rpLembar: '', rpDijual: true, rpUpah: '' });
// ---- atur harga jual wadah
var AW = susunAturHargaWadah({ '5kg_kembangbmw': '2000', 'paperbag10l': '50' }, W);
ok('W: harga per lembar Rp50 DITOLAK (lantai Rp100 — salah satuan)', /salah satuan/.test(AW.tolak || ''), JSON.stringify(AW));
AW = susunAturHargaWadah({ '5kg_kembangbmw': '2000', 'paperbag10l': '600', 'karungbekas': '', 'jenisAsing': '1000' }, W);
ok('W: yang berubah saja yang ditulis: paper bag 10 L 600 (baru), karung bekas dicabut (0, hargaSebelum 1.500); 5 kg sama → tidak; jenis asing diabaikan', !AW.tolak && AW.dokumen.length === 2 && AW.dokumen.every(function (d) { return d.koleksi === 'hargaWadah' && d.data.id === d.data.jenis; }) && AW.dokumen.find(function (d) { return d.data.jenis === 'paperbag10l'; }).data.harga === 600 && AW.dokumen.find(function (d) { return d.data.jenis === 'karungbekas'; }).data.harga === 0 && AW.dokumen.find(function (d) { return d.data.jenis === 'karungbekas'; }).data.hargaSebelum === 1500, JSON.stringify(AW.dokumen));
terapkanKeCache(AW.dokumen);
ok('W: rak wadah mengikuti katalog: paper bag 10 L kini tampil, karung bekas hilang', susunRak(s).wadah.map(function (c) { return c.kunci; }).join() === '5kg_kembangbmw,5kg_putriagri,paperbag10l', JSON.stringify(susunRak(s).wadah.map(function (c) { return c.kunci; })));
ok('W: tanpa perubahan → ditolak "tidak ada yang berubah"', /Tidak ada harga yang berubah/.test(susunAturHargaWadah({ '5kg_kembangbmw': '2000' }, W).tolak || ''));
terapkanKeCache([{ koleksi: 'hargaWadah', data: { id: 'karungbekas', jenis: 'karungbekas', harga: 1500 } }, { koleksi: 'hargaWadah', data: { id: 'paperbag10l', jenis: 'paperbag10l', harga: 0 } }]);
ok('W: sering mengenal baris wadah (kunciBaris wadah|jenis) — baris wadah kemarin masuk hitungan', (function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sw1', tanggal: '2026-09-18', jam: '09:00', caraBayar: 'Tunai', jenis: 'wadah', jenisWadah: '5kg_kembangbmw', namaProduk: 'Kantong Kembang/BMW 5 kg', jumlahUnit: 3, totalKg: 0, hargaTotal: 6000, hppTotalSaatJual: 3375 } }]); var r = susunRak(s).sering.some(function (c) { return c.id === 'wadah|5kg_kembangbmw'; }); terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sw1' }]); return r; })());

// ================= PUTARAN 15: STRUK (JS3-A kertas & WA, JS3-C aturan otomatis) =================
var A0 = stAtur();
ok('S: setelan bawaan: kop Toko Beras M.IQBAL, kertas 58, aturan otomatis MATI dua-duanya, kaki "Terima kasih 🙏"', A0.kop.nama === 'Toko Beras M.IQBAL' && A0.kertas === 58 && A0.oto.cetak === 'tidak' && A0.oto.wa === 'tidak' && /Terima kasih/.test(A0.kaki) && A0.sertakan.rincian === true, JSON.stringify(A0));
var n1 = notaDari({ grupNota: 'g1' }); var st1 = susunStruk(n1, A0, null);
ok('S: nota g1 (Bu Suti, 2 kemasan 144.000, tunai) — kop di atas (huruf besar, di tengah), tanggal + jam, nama, baris barang, TOTAL, Bayar: Tunai, kaki di akhir', st1.kertas[0].trim() === 'TOKO BERAS M.IQBAL' && /2026/.test(st1.kertas[2]) && /08:10/.test(st1.kertas[2]) && st1.kertas[3] === 'Bu Suti' && st1.kertas.some(function (t) { return /^Kembang 5 kg/.test(t); }) && st1.kertas.some(function (t) { return /^  2 kemasan × 72\.000\s+Rp144\.000$/.test(t); }) && st1.kertas.some(function (t) { return /^TOTAL\s+Rp144\.000$/.test(t); }) && st1.kertas.some(function (t) { return t === 'Bayar: Tunai'; }) && /Terima kasih/.test(st1.kertas[st1.kertas.length - 1]), st1.teks);
ok('S: 58 mm = 30 kolom, angka rata kanan; 80 mm = 42 kolom', st1.kertas.find(function (t) { return /^TOTAL/.test(t); }).length === 30 && susunStruk(n1, A0, { kertas: 80 }).kertas.find(function (t) { return /^TOTAL/.test(t); }).length === 42, JSON.stringify([st1.lebar, susunStruk(n1, A0, { kertas: 80 }).lebar]));
ok('S: wujud WhatsApp = isi yang sama tanpa spasi pengisi, TOTAL & kop ditebalkan *…*', /^\*TOKO BERAS M\.IQBAL\*\n/.test(st1.wa) && /\n\*TOTAL   Rp144\.000\*\n/.test(st1.wa) && !/ {6,}/.test(st1.wa) && /^https:\/\/wa\.me\/\?text=\*TOKO%20BERAS/.test(tautanWa(st1.wa)), st1.wa);
var n2 = notaDari({ id: 's2' }); var st2 = susunStruk(n2, A0, null);
ok('S: nota BON Deka: "BON — belum dibayar", a.n. Deka, sisa bon 890.000 dari mesin piutang (saldo awal + kredit ini)', st2.kertas.some(function (t) { return t === 'BON — belum dibayar'; }) && st2.kertas.some(function (t) { return t === 'a.n. Deka'; }) && st2.sisaBon === 890000 && st2.kertas.some(function (t) { return /^Sisa bon Deka\s+Rp890\.000$/.test(t); }), st2.teks);
ok('S: sisa bon bisa tidak disertakan; kalimat kaki bisa dilepas; tanpa rincian baris barang hilang tapi TOTAL tetap', !susunStruk(n2, A0, { sertakan: { bon: false } }).kertas.some(function (t) { return /^Sisa bon/.test(t); }) && !/Terima kasih/.test(susunStruk(n2, A0, { sertakan: { kaki: false } }).teks) && (function () { var x = susunStruk(n1, A0, { sertakan: { rincian: false } }).kertas; return !x.some(function (t) { return /Kembang/.test(t); }) && x.some(function (t) { return /^TOTAL/.test(t); }); })());
// nota yang disusun sistem baru: potongan + pembulatan + wadah + upah → baris kotor + potongan + pembulatan + upah = TOTAL (menutup)
terap({ keranjang: [], pelanggan: 'Bu Suti', cara: 'Tunai', uang: 0, potongan: 0, tukar: null, pesananId: null });
terap(ketukChip(s, chip('kemasan', 'Kembang|5'))); terap({ ketik: '1' }); terap(masukkan(s)); terap(ketukChip(s, chip('wadah', 'karungbekas'))); terap({ ketik: '3' }); terap(masukkan(s));
terap(ketukChip(s, chip('repack', 'Angsa'))); terap({ ketik: '2', rpUpah: '1000' }); terap(masukkan(s)); terap(setelPotongan(s, 1300)); terap(tambahUang(s, 100000)); terap(tambahUang(s, 5000));
var NS = susunNotaDokumen(s, W); terapkanKeCache(NS.dokumen); var nS = notaDari({ trxId: NS.trxId }); var stS = susunStruk(nS, A0, null);
ok('S: nota baru (kemasan 72.000 + karung bekas 3 × 1.500 + repack 2 kg 27.600 + upah 1.000 − potongan 1.300, dibulatkan tunai) — struk memuat Potongan −1.300, Pembulatan, upah repack, dan TOTAL = jumlah hargaTotal', stS.pot === 1300 && stS.bulat === NS.bulatNota && stS.upah === 1000 && stS.total === NS.totalBayar && stS.kertas.some(function (t) { return /^Potongan\s+−Rp1\.300$/.test(t); }) && stS.kertas.some(function (t) { return /^Pembulatan Rp500\s+\+Rp/.test(t); }) && stS.kertas.some(function (t) { return /^  upah repack\s+Rp1\.000$/.test(t); }) && stS.kertas.some(function (t) { return /^  3 lembar × 1\.500\s+Rp4\.500$/.test(t); }), stS.teks);
ok('S: HITUNGAN MENUTUP: jumlah baris kotor − potongan + pembulatan + upah = TOTAL', nS.baris.reduce(function (a, p) { return a + kotorBaris(p); }, 0) - stS.pot + stS.bulat + stS.upah === stS.total, JSON.stringify([nS.baris.map(kotorBaris), stS.pot, stS.bulat, stS.upah, stS.total]));
ok('S: uang diterima 105.000 & kembalian tertulis', stS.kertas.some(function (t) { return /^Uang diterima\s+Rp105\.000$/.test(t); }) && stS.kertas.some(function (t) { return new RegExp('^Kembali\\s+' + RP(105000 - NS.totalBayar).replace('.', '\\.') + '$').test(t); }), stS.teks);
ok('S: nota tanpa nama ditulis "Tanpa nama"; nota QRIS ditulis Bayar: QRIS tanpa MDR/rekening', (function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sq1', trxId: 'tq1', tanggal: '2026-09-19', jam: '12:00', caraBayar: 'QRIS', namaPelanggan: '', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 72000, hppTotalSaatJual: 66000 } }]); var x = susunStruk(notaDari({ trxId: 'tq1' }), A0, null); terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sq1' }]); return x.kertas[3] === 'Tanpa nama' && x.kertas.some(function (t) { return t === 'Bayar: QRIS'; }) && !/MDR|rekening/i.test(x.teks); })());
var PS = susunPembatalan({ trxId: NS.trxId, idPenjualan: NS.idPenjualan, piutangId: null, pesanan: null, retur: null }, 'uji', { kini: '2026-09-19T10:30:00.000Z' }); terapkanKeCache(PS.dokumen);
ok('S: nota yang dibatalkan: struknya berkata "(catatan ini sudah dibatalkan)" dan kepalanya tidak berlaku', (function () { var x = notaDari({ trxId: NS.trxId }); return x.berlaku === false && x.dibatalkan === true && susunStruk(x, A0, null).kertas.some(function (t) { return /sudah dibatalkan/.test(t); }); })());
NS.idPenjualan.forEach(function (id) { terapkanKeCache([{ koleksi: 'penjualan', hapus: id }]); }); PS.hapus.forEach(function (x) { terapkanKeCache([{ koleksi: x.koleksi, hapus: x.id }]); }); terap({ keranjang: [], pelanggan: '', uang: 0, potongan: 0 });
// aturan otomatis (JS3-C)
ok('S: bawaan: tidak ada yang otomatis', putusOto(A0, n1).teks === 'tidak' && putusOto(A0, n2).teks === 'tidak');
var A1 = JSON.parse(JSON.stringify(A0)); A1.oto = { cetak: 'tunai', wa: 'bon' };
ok('S: aturan cetak tunai / WA bon: nota tunai → cetak, nota bon → WA', putusOto(A1, n1).cetak === true && putusOto(A1, n1).wa === false && putusOto(A1, n2).wa === true && putusOto(A1, n2).cetak === false, JSON.stringify([putusOto(A1, n1), putusOto(A1, n2)]));
A1.oto = { cetak: 'semua', wa: 'semua' }; ok('S: semua + semua → cetak + WA', putusOto(A1, n2).teks === 'cetak + WA');
A1.perOrang = { 'deka': 'tidak' }; ok('S: pilihan pelanggan "tidak perlu" mengalahkan aturan (Deka)', putusOto(A1, n2).teks.indexOf('tidak') === 0 && !putusOto(A1, n2).wa && !putusOto(A1, n2).cetak, putusOto(A1, n2).teks);
A1.perOrang = { 'bu suti': 'wa' }; A1.oto = { cetak: 'tunai', wa: 'tidak' }; ok('S: "selalu WA" mengalahkan cetak-tunai untuk Bu Suti', putusOto(A1, n1).wa === true && putusOto(A1, n1).cetak === false);
// setelan tersimpan & dibaca lagi
var AS = susunAturStruk({ kop: { nama: 'Toko Beras Contoh', alamat: 'Jl. Contoh 1', telp: '0812-0000' }, kaki: '', kertas: 80, sertakan: { rincian: true, bon: false, kaki: true, pelayan: false }, oto: { cetak: 'tunai', wa: 'bon' }, perOrang: { 'Bu Suti': 'wa', 'X': 'ikut' } }, W);
ok('S: susunAturStruk → dokumen aturanToko/struk; perOrang dikunci lewat kunciPelanggan, "ikut" tidak disimpan', !AS.tolak && AS.dokumen[0].koleksi === 'aturanToko' && AS.dokumen[0].data.id === 'struk' && AS.dokumen[0].data.perOrang['bu suti'] === 'wa' && !('x' in AS.dokumen[0].data.perOrang) && AS.dokumen[0].data.kertas === 80, JSON.stringify(AS));
terapkanKeCache(AS.dokumen); var A2 = stAtur(); var st3 = susunStruk(n1, A2, null);
ok('S: setelan owner terpakai: kop baru + alamat + telp, 42 kolom, sisa bon mati, kaki kosong → tanpa baris kaki, Dilayani dimatikan', st3.kertas[0].trim() === 'TOKO BERAS CONTOH' && /Jl\. Contoh 1/.test(st3.kertas[1]) && /Telp 0812-0000/.test(st3.kertas[2]) && st3.lebar === 42 && st3.kertas[st3.kertas.length - 1] !== '' && !/Terima kasih/.test(st3.teks) && A2.sertakan.bon === false && A2.oto.cetak === 'tunai', st3.teks);
ok('S: ditolak: nama kop kosong / kertas 70 / pilihan aturan asing', /kosong/.test(susunAturStruk({ kop: { nama: ' ' }, kertas: 58, oto: { cetak: 'tidak', wa: 'tidak' } }, W).tolak) && /58 atau 80/.test(susunAturStruk({ kop: { nama: 'A' }, kertas: 70, oto: { cetak: 'tidak', wa: 'tidak' } }, W).tolak) && /tidak dikenal/.test(susunAturStruk({ kop: { nama: 'A' }, kertas: 58, oto: { cetak: 'kadang', wa: 'tidak' } }, W).tolak));
terapkanKeCache([{ koleksi: 'aturanToko', hapus: 'struk' }]);
var SK = susunStrukKeluar(n1, 'wa', W, 'uji'); terapkanKeCache([SK]);
ok('S: struk keluar dicatat (koleksi strukKeluar: trxId/grupNota, cara, nama, total) dan riwayat hari itu membacanya', SK.koleksi === 'strukKeluar' && SK.data.trxId === 'g1' && SK.data.cara === 'wa' && SK.data.total === 144000 && riwayatStruk('2026-09-19').length === 1 && riwayatStruk('2026-09-19')[0].cara === 'WhatsApp', JSON.stringify(riwayatStruk('2026-09-19')));
ok('S: Dilayani = kolom oleh baris nota bila disertakan', (function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'so1', trxId: 'to1', tanggal: '2026-09-19', jam: '12:30', caraBayar: 'Tunai', namaPelanggan: 'Bu Suti', oleh: 'Ben', jenis: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, hargaTotal: 72000, hppTotalSaatJual: 66000 } }]); var x = susunStruk(notaDari({ trxId: 'to1' }), A0, null); var y = susunStruk(notaDari({ trxId: 'to1' }), A0, { sertakan: { pelayan: false } }); terapkanKeCache([{ koleksi: 'penjualan', hapus: 'so1' }]); return x.kertas.some(function (t) { return t === 'Dilayani Ben'; }) && !y.kertas.some(function (t) { return /Dilayani/.test(t); }); })());
ok('S: nota lama sistem lama (tanpa trxId, tanpa grupNota) = satu baris satu nota; kembalian lama (kembalianUangDiterima/kembalianNominal) terbaca', (function () { terapkanKeCache([{ koleksi: 'penjualan', data: { id: 'sl1', tanggal: '2026-09-19', jam: '13:00', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'literan', merkSumber: 'Angsa', jumlahLiter: 2, totalKg: 1.64, hargaTotal: 27000, hppTotalSaatJual: 22000, kembalianUangDiterima: 50000, kembalianNominal: 23000 } }]); var n = notaDari({ id: 'sl1' }); var x = susunStruk(n, A0, null); terapkanKeCache([{ koleksi: 'penjualan', hapus: 'sl1' }]); return n.baris.length === 1 && x.kertas.some(function (t) { return /^Uang diterima\s+Rp50\.000$/.test(t); }) && x.kertas.some(function (t) { return /^Kembali\s+Rp23\.000$/.test(t); }) && x.kertas.some(function (t) { return /^  2 L × 13\.500\s+Rp27\.000$/.test(t); }); })());
terap(Object.assign(keadaanAwal(), { sekarang: new Date('2026-09-19T10:00:00') }));

// ================= PUTARAN 20: RINCI KARCIS (karcis-logika) · RETUR TANPA NOTA · TUKAR YATIM =================
terap(Object.assign(keadaanAwal(), { sekarang: new Date('2026-09-19T10:00:00') }));
terapkanKeCache([
  { koleksi: 'penjualan', data: { id: 'k1', tanggal: '2026-09-19', jam: '09:30', caraBayar: 'Tunai', jenis: 'kasir_darurat_nominal', hargaTotal: 690000, operator: 'Gono' } },
  { koleksi: 'penjualan', data: { id: 'k2', tanggal: '2026-09-19', jam: '09:45', caraBayar: 'Qris', jenis: 'kasir_darurat_nominal', hargaTotal: 40500 } },
  { koleksi: 'penjualan', data: { id: 'k3', tanggal: '2026-09-18', jam: '16:00', caraBayar: 'Tunai', jenis: 'kasir_darurat_nominal', hargaTotal: 200000 } },
  { koleksi: 'penjualan', data: { id: 'r1', tanggal: '2026-09-19', jam: '08:00', caraBayar: 'Tunai', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 0, totalKg: 0, hargaTotal: 690000, hppTotalSaatJual: 0, perluKoreksi: true } }]);
var KCd = daftarKarcis(s.sekarang);
ok('T: antrean karcis: 3 karcis + 1 perlu dirapikan, terbaru dulu (k2, k1, r1, k3), total karcis 930.500; k1 menyebut oleh Gono', KCd.nKarcis === 3 && KCd.nRapikan === 1 && KCd.daftar.map(function (k) { return k.id; }).join() === 'k2,k1,r1,k3' && KCd.total === 930500 && KCd.daftar[1].oleh === 'Gono' && KCd.daftar[2].jenisAsal === 'rapikan', JSON.stringify(KCd));
var TB = tebakanKarcis(690000); ok('T: tebakan 690.000: "Karung 50 kg Angsa × 1" tepat ada', TB.some(function (t) { return t.label === 'Karung 50 kg Angsa × 1' && t.tepat; }), JSON.stringify(TB.map(function (t) { return t.label; })));
TB = tebakanKarcis(40500); ok('T: 40.500 = Angsa 3 L tepat (urutan pertama)', TB[0].label === 'Angsa 3 L' && TB[0].tepat && TB[0].isi[0].jumlah === 3, JSON.stringify(TB));
TB = tebakanKarcis(40800); ok('T: 40.800 = Angsa 3 L · bulat +Rp300 (toleransi < 500), harga PAS 40.800 dibawa; 41.000 (selisih 500) TIDAK ditebak', TB.some(function (t) { return /Angsa 3 L · bulat \+Rp300/.test(t.label) && t.isi[0].hargaPas === 40800 && !t.tepat; }) && !tebakanKarcis(41000).some(function (t) { return /Angsa 3 L/.test(t.label); }), JSON.stringify(TB));
ok('T: tebakan kombinasi: 730.500 = Karung 50 IR64 Apex × 1 (730.000)… tidak; 703.500 = karung Angsa 690.000 + Angsa 1 L 13.500 ADA', tebakanKarcis(703500).some(function (t) { return /Karung 50 Angsa × 1 \+ Angsa 1 L|Angsa 1 L \+ Karung 50 Angsa × 1/.test(t.label) && t.isi.length === 2; }), JSON.stringify(tebakanKarcis(703500).map(function (t) { return t.label; })));
terap(ikatKarcis(s, 'k1', s.sekarang)); ok('T: karcis k1 terikat: cara Tunai, pelanggan kosong, hitung = belum ada barang', s.karcis && s.karcis.id === 'k1' && s.cara === 'Tunai' && hitungKarcis(s).teks === 'belum ada barang', JSON.stringify(s.karcis));
ok('T: mengikat karcis kedua DITOLAK; parkir DITOLAK; catat nota biasa DITOLAK menyebut SIMPAN RINCIAN', /sedang merinci karcis/.test(ikatKarcis(s, 'k2', s.sekarang).kabar) && /merinci karcis/.test(parkir(s).kabar) && /SIMPAN RINCIAN/.test(alasanTolak(s)));
ok('T: keranjang kosong → simpan rincian DITOLAK', /Tambahkan barangnya dulu/.test(susunRinciDokumen(s, W).tolak));
terap(pakaiTebakan(s, tebakanKarcis(690000).find(function (t) { return t.label === 'Karung 50 kg Angsa × 1'; })));
ok('T: tebakan mengisi keranjang: 1 baris karung Angsa 50 kg 690.000 → PAS', s.keranjang.length === 1 && s.keranjang[0].trx.hargaTotal === 690000 && hitungKarcis(s).pas, JSON.stringify(hitungKarcis(s)));
var RR = susunRinciDokumen(s, W); var brs = RR.dokumen.filter(function (d) { return d.koleksi === 'penjualan' && d.data.asalDarurat; }); var asli = RR.dokumen[RR.dokumen.length - 1].data;
ok('T: dokumen = simpanRinciTrx: baris karung {tanggal 19 Sep, jam 09:30 DARI KARCIS, caraBayar Tunai, grupNota, asalDarurat, rinciDari k1, koreksiDari k1, alasanKoreksi "Rincian dari kasir darurat #…k1", dirinciPada, operator Gono, hppTotalSaatJual > 0}; asli ditandai dikoreksiOleh = id baris pertama & alasan "Dirinci jadi 1 barang"; tanpa sisa', brs.length === 1 && brs[0].data.tanggal === '2026-09-19' && brs[0].data.jam === '09:30' && brs[0].data.caraBayar === 'Tunai' && brs[0].data.grupNota === RR.rinci.grupNota && brs[0].data.rinciDari === 'k1' && brs[0].data.koreksiDari === 'k1' && /Rincian dari kasir darurat #/.test(brs[0].data.alasanKoreksi) && brs[0].data.dirinciPada && brs[0].data.operator === 'Gono' && brs[0].data.hppTotalSaatJual > 0 && asli.id === 'k1' && asli.dikoreksiOleh === brs[0].data.id && /Dirinci jadi 1 barang/.test(asli.alasanKoreksi) && !/sisa/.test(asli.alasanKoreksi) && brs[0].data.jenis === 'karung', JSON.stringify(RR.dokumen));
var kgSebelumK = hitungStokKarungPerMerk()['Angsa'].sisaKg; terapkanKeCache(RR.dokumen); terap(RR.patch);
ok('T: sesudah simpan: k1 keluar dari antrean (2 karcis), keranjang kosong, notaTerakhir.rinci menunjuk grup, stok buku Angsa turun 50 kg (rak sudah menahannya sejak di keranjang)', daftarKarcis(s.sekarang).nKarcis === 2 && !s.keranjang.length && !s.karcis && s.notaTerakhir.rinci.asliId === 'k1' && Math.abs(hitungStokKarungPerMerk()['Angsa'].sisaKg - (kgSebelumK - 50)) < 0.01, JSON.stringify([kgSebelumK, hitungStokKarungPerMerk()['Angsa'].sisaKg]));
// sisa belum terurai → karcis baru
terap(ikatKarcis(s, 'k3', s.sekarang)); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '10' }); terap(masukkan(s));
var HK = hitungKarcis(s); ok('T: k3 200.000 − Angsa 10 L 135.000 = sisa 65.000 belum terurai — boleh disimpan (bukan ditolak)', HK.sisa === 65000 && !HK.lebih && /boleh disimpan/.test(HK.teks), JSON.stringify(HK));
RR = susunRinciDokumen(s, W); var sisaDoc = RR.dokumen.find(function (d) { return d.koleksi === 'penjualan' && d.data.jenis === 'kasir_darurat_nominal' && d.data.asalDarurat; }); asli = RR.dokumen[RR.dokumen.length - 1].data;
ok('T: sisa 65.000 jadi karcis baru {asalDarurat, rinciDari k3, grupNota sama, alasan "Sisa belum diurai"}; kantong literan id+1 ikut; asli menyebut "+ sisa Rp65.000"', !RR.tolak && sisaDoc && sisaDoc.data.hargaTotal === 65000 && sisaDoc.data.rinciDari === 'k3' && sisaDoc.data.grupNota === RR.rinci.grupNota && /Sisa belum diurai/.test(sisaDoc.data.alasanKoreksi) && RR.dokumen.some(function (d) { return d.koleksi === 'stokBahanLiteran' && d.data.tipe === 'pakai'; }) && /sisa Rp65\.000 belum diurai/.test(asli.alasanKoreksi), JSON.stringify(RR.dokumen));
terapkanKeCache(RR.dokumen); terap(RR.patch); KCd = daftarKarcis(s.sekarang);
ok('T: antrean: k2 + sisa k3 (65.000, teks "Sisa karcis") + r1; riwayat rinci hari ini 2 grup utuh', KCd.nKarcis === 2 && KCd.daftar.some(function (k) { return k.nominal === 65000 && /Sisa karcis/.test(k.teks) && k.sisaDari === 'k3'; }) && riwayatRinci('2026-09-19').length === 2 && riwayatRinci('2026-09-19').every(function (r) { return r.utuh; }), JSON.stringify(KCd.daftar));
// kelebihan · potongan · bon tanpa nama
terap(ikatKarcis(s, 'k2', s.sekarang)); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '4' }); terap(masukkan(s));
ok('T: barang 54.000 > karcis 40.500 → KELEBIHAN 13.500 DITOLAK menyebut nominal', /KELEBIHAN Rp13\.500 dari nominal Rp40\.500/.test(susunRinciDokumen(s, W).tolak), susunRinciDokumen(s, W).tolak);
terap({ keranjang: [] }); terap(ketukChip(s, chip('literan', 'Angsa'))); terap({ ketik: '3' }); terap(masukkan(s)); terap({ potongan: 500 }); ok('T: potongan nota saat merinci DITOLAK', /Potongan nota tidak dipakai/.test(susunRinciDokumen(s, W).tolak)); terap({ potongan: 0 });
terap(pilihCara(s, 'Kredit')); ok('T: bon tanpa nama DITOLAK', /nama pembeli/.test(susunRinciDokumen(s, W).tolak)); terap(pilihCara(s, 'QRIS'));
// hanya perbaiki cara bayar / nama
terap({ pelanggan: 'Bu Suti' }); var PB = susunPerbaikanKarcis(s, W);
ok('T: perbaikan: pengganti {caraBayar QRIS, namaPelanggan Bu Suti, koreksiDari k2, jenis tetap karcis, TANPA dikoreksiOleh} + asli k2 ditandai; barang keranjang tidak ditulis', !PB.tolak && PB.dokumen.length === 2 && PB.dokumen[0].data.namaPelanggan === 'Bu Suti' && PB.dokumen[0].data.caraBayar === 'QRIS' && PB.dokumen[0].data.koreksiDari === 'k2' && PB.dokumen[0].data.jenis === 'kasir_darurat_nominal' && !('dikoreksiOleh' in PB.dokumen[0].data) && PB.dokumen[1].data.id === 'k2' && PB.dokumen[1].data.dikoreksiOleh === PB.dokumen[0].data.id, JSON.stringify(PB));
terap({ pelanggan: '' }); ok('T: perbaikan tanpa perubahan DITOLAK', /Tidak ada yang berubah/.test(susunPerbaikanKarcis(s, W).tolak));
terapkanKeCache(PB.dokumen); terap(PB.patch); KCd = daftarKarcis(s.sekarang);
ok('T: sesudah perbaikan: tetap 2 karcis, pengganti k2 bernama Bu Suti menggantikan; karcis dilepas dari keranjang, barang keranjang tetap', KCd.nKarcis === 2 && KCd.daftar.some(function (k) { return k.nama === 'Bu Suti' && k.nominal === 40500; }) && !KCd.daftar.some(function (k) { return k.id === 'k2'; }) && !s.karcis && s.keranjang.length === 1, JSON.stringify(KCd.daftar));
terap({ keranjang: [] });
// rapikan (perluKoreksi): uang tetap, harus pas
terap(ikatKarcis(s, 'r1', s.sekarang)); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '0,5' }); terap(masukkan(s));
ok('T: rapikan bersisa (345.000 dari 690.000) DITOLAK — harus menutup persis', /menutup Rp690\.000 persis/.test(susunRinciDokumen(s, W).tolak), susunRinciDokumen(s, W).tolak);
terap({ keranjang: [] }); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '1' }); terap(masukkan(s)); RR = susunRinciDokumen(s, W); var br = RR.dokumen[0].data;
ok('T: rapikan PAS: baris karung {jumlahKarung 1, hpp > 0, koreksiDari r1, alasan "Dirapikan dari kasir", TANPA asalDarurat/rinciDari, tanpa perluKoreksi}; asli r1 ditandai "Dirapikan jadi 1 barang"', !RR.tolak && br.jumlahKarung === 1 && br.hppTotalSaatJual > 0 && br.koreksiDari === 'r1' && /Dirapikan dari kasir/.test(br.alasanKoreksi) && !br.asalDarurat && !br.rinciDari && !br.perluKoreksi && RR.dokumen[RR.dokumen.length - 1].data.id === 'r1' && /Dirapikan jadi 1 barang/.test(RR.dokumen[RR.dokumen.length - 1].data.alasanKoreksi), JSON.stringify(RR.dokumen));
terapkanKeCache(RR.dokumen); terap(RR.patch); ok('T: antrean rapikan kosong', daftarKarcis(s.sekarang).nRapikan === 0);
// tarik balik
var RU = susunUrungRinci(RR.rinci, W);
ok('T: tarik balik rapikan: 1 baris dibatalkan (alasan "Rincian diurungkan"), asli r1 pulih TANPA dikoreksiOleh & alasanKoreksi', !RU.tolak && RU.jumlah === 1 && RU.dokumen[0].data.dibatalkan === true && /Rincian diurungkan/.test(RU.dokumen[0].data.alasanKoreksi) && RU.dokumen[1].data.id === 'r1' && !('dikoreksiOleh' in RU.dokumen[1].data) && !('alasanKoreksi' in RU.dokumen[1].data) && RU.dokumen[1].data.perluKoreksi === true, JSON.stringify(RU));
terapkanKeCache(RU.dokumen); ok('T: r1 kembali ke antrean rapikan', daftarKarcis(s.sekarang).nRapikan === 1);
var grupK3 = riwayatRinci('2026-09-19').find(function (r) { return r.asliId === 'k3'; }); var barisK3 = ambilPenjualanSemua().find(function (x) { return x.grupNota === grupK3.grupNota && x.jenis === 'literan'; });
terapkanKeCache([{ koleksi: 'penjualan', data: Object.assign({}, barisK3, { dikoreksiOleh: 'zzz' }) }]);
ok('T: grup yang sebagian sudah dikoreksi TIDAK bisa ditarik balik (menyebut catatannya); riwayat menandai tidak utuh', /sudah dikoreksi\/dirinci lagi/.test(susunUrungRinci({ grupNota: grupK3.grupNota, asliId: 'k3' }, W).tolak) && riwayatRinci('2026-09-19').find(function (r) { return r.asliId === 'k3'; }).utuh === false, susunUrungRinci({ grupNota: grupK3.grupNota, asliId: 'k3' }, W).tolak);
terapkanKeCache([{ koleksi: 'penjualan', data: barisK3 }]);
// ---- RETUR TANPA NOTA (ketik tangan)
mulaiNota(); terap(Object.assign(returAwal(), { lembar: 'returTanpa' }));
var DB = daftarBarangRetur();
ok('T: barang retur tanpa nota: karung per merek & berat (Angsa 50 · Angsa 25 · IR64 Apex 50) dengan terjual & diretur; kemasan Kembang 5 kg', DB.karung.map(function (x) { return x.kunci; }).join() === 'Angsa|50,Angsa|25,IR64 Apex|50' && DB.kemasan.some(function (x) { return x.kunci === 'Kembang|5' && x.terjual >= 3; }) && DB.karung.find(function (x) { return x.kunci === 'Angsa|50'; }).terjual >= 2, JSON.stringify(DB));
ok('T: tanpa barang DITOLAK; tanpa jumlah DITOLAK; karung 0,3 DITOLAK; kemasan 1,5 DITOLAK', /Pilih barang/.test(susunReturTanpaNota(s, W).tolak) && (terap({ rtBarang: 'Angsa|50' }), /berapa karung/.test(susunReturTanpaNota(s, W).tolak)) && (terap({ ketik: '0,3' }), /utuh atau setengah/.test(susunReturTanpaNota(s, W).tolak)) && (terap({ rtJenis: 'kemasan', rtBarang: 'Kembang|5', ketik: '1,5' }), /UNIT utuh/.test(susunReturTanpaNota(s, W).tolak)));
terap({ rtJenis: 'karung', rtBarang: 'Angsa|50', ketik: '1' }); ok('T: tanpa alasan DITOLAK; tanpa kondisi DITOLAK', /alasan retur/.test(susunReturTanpaNota(s, W).tolak) && (terap({ rtAlasan: 'salah beli' }), /BOLEH DIJUAL LAGI/.test(susunReturTanpaNota(s, W).tolak)));
terap({ rtKondisi: 'utuh' }); ok('T: refund tanpa nominal DITOLAK — tanpa nota tidak ada yang menghitungkannya', /Isi nominal uang yang dikembalikan/.test(susunReturTanpaNota(s, W).tolak));
terap({ rtNominal: '650.000' }); var RTN = susunReturTanpaNota(s, W); var rtd = RTN.dokumen && RTN.dokumen[0].data;
ok('T: dokumen retur tanpa nota = cabang lama: {jenisAsal karung, merkSumber Angsa, jumlahKarung 1, beratKarungAcuan 50, totalKg 50, kondisi utuh, penyelesaian refund, catatan, nominalRefund 650.000, tanpaNota true, TANPA notaAsalId}; kabar menyebut uang keluar', !RTN.tolak && rtd.jenisAsal === 'karung' && rtd.merkSumber === 'Angsa' && rtd.jumlahKarung === 1 && rtd.beratKarungAcuan === 50 && rtd.totalKg === 50 && rtd.kondisi === 'utuh' && rtd.penyelesaian === 'refund' && rtd.nominalRefund === 650000 && rtd.tanpaNota === true && !('notaAsalId' in rtd) && RTN.dokumen.length === 1 && /uang keluar Rp650\.000/.test(RTN.patch.kabar), JSON.stringify(RTN));
terap({ ketik: '5' }); RTN = susunReturTanpaNota(s, W); ok('T: 5 karung melebihi yang pernah terjual − diretur → perluYakin (ketukan kedua), menyebut angkanya', RTN.perluYakin && /cuma pernah terjual/.test(RTN.tolak) && /mungkin salah ketik/.test(RTN.tolak), RTN.tolak);
terap({ rtYakin: true }); ok('T: dengan ketukan kedua → tercatat', !susunReturTanpaNota(s, W).tolak);
terap({ ketik: '1', rtYakin: false, rtPenyelesaian: 'tukar', rtSelisih: '' }); ok('T: tukar tanpa selisih DITOLAK (ketik 0 kalau tidak ada)', /Isi selisih tukarnya/.test(susunReturTanpaNota(s, W).tolak));
terap({ rtSelisih: '-20.000', rtKondisi: 'tidak_utuh' }); RTN = susunReturTanpaNota(s, W); rtd = RTN.dokumen[0].data;
ok('T: tukar tanpa nota: selisihHargaTukar −20.000 (pembeli menambah), tanpa nominalRefund, karantina ikut (id sama), kabar menyuruh pil "pengganti retur"', rtd.penyelesaian === 'tukar' && rtd.selisihHargaTukar === -20000 && !('nominalRefund' in rtd) && RTN.dokumen[1].koleksi === 'karantina' && RTN.dokumen[1].data.id === rtd.id && /pembeli menambah Rp20\.000/.test(RTN.patch.kabar) && /pengganti retur/.test(RTN.patch.kabar), JSON.stringify(RTN));
terap({ rtSelisih: '0' }); ok('T: selisih 0 sah', !susunReturTanpaNota(s, W).tolak && susunReturTanpaNota(s, W).dokumen[0].data.selisihHargaTukar === 0);
// ---- TUKAR YATIM: catat penggantinya (susulan) & pengganti sudah tercatat
terapkanKeCache([{ koleksi: 'retur', data: { id: 'ry1', tanggal: '2026-09-18', jam: '15:00', jenisAsal: 'karung', merkSumber: 'Angsa', jumlahKarung: 1, beratKarungAcuan: 50, totalKg: 50, kondisi: 'utuh', penyelesaian: 'tukar', nominalRefund: 690000, selisihHargaTukar: 0, tukarModel: 'kreditBarangGabung', notaAsalId: 's2', catatan: 'salah beli',
  hitunganTukarSistem: { pengganti: 730000, kredit: 690000, bersih: 40000, pembulatan: 0, caraBayar: 'Tunai', dibayarPembeli: 40000, dikembalikanToko: 0 } } }]);
var Y = returYatim(); ok('T: 1 tukar yatim ry1: target 730.000, tercatat 0, kurang 730.000, teks "tidak tercatat lagi"', Y.length === 1 && Y[0].id === 'ry1' && Y[0].target === 730000 && Y[0].tercatat === 0 && Y[0].kurang === 730000 && /tidak tercatat lagi/.test(Y[0].teks), JSON.stringify(Y));
mulaiNota(); var IS = ikatSusulan('ry1'); terap(ikatTukar(s, IS.ikat));
ok('T: ikatan susulan: kredit 0, susulanReturId ry1, model gabung; kabar menyebut catat HANYA yang belum Rp730.000 & dibayar Tunai', s.tukar && s.tukar.kredit === 0 && s.tukar.susulanReturId === 'ry1' && s.tukar.model === 'kreditBarangGabung' && /HANYA yang belum: Rp730\.000/.test(IS.kabar) && /dibayar Tunai/.test(IS.kabar), IS.kabar);
terap(ketukChip(s, chip('karung', 'IR64 Apex', 50))); terap({ ketik: '1' }); terap(masukkan(s)); t = hitungTagihan(s);
ok('T: susulan gabung: pembulatan atas selisih yang dulu diterima (730.000 − 690.000 = 40.000 → 0), kredit 0 → total 730.000', t.kredit === 0 && t.bulat === 0 && t.total === 730000, JSON.stringify(t));
terap(pilihCara(s, 'Kredit')); ok('T: susulan BON DITOLAK', /Susulan tukar tidak bisa BON/.test(alasanTolak(s)), alasanTolak(s)); terap(pilihCara(s, 'Tunai')); terap(uangPas(s)); ok('T: sah dicatat', alasanTolak(s) === '', alasanTolak(s));
var SN = simpanNota(s, W); var rowsS = SN.dokumen.filter(function (d) { return d.koleksi === 'penjualan'; });
ok('T: nota susulan: tiap baris membawa tukarReturId ry1; TIDAK ada dokumen retur baru; ringkas menyebut SUSULAN; notaTerakhir.retur null', rowsS.length === 1 && rowsS[0].data.tukarReturId === 'ry1' && !SN.dokumen.some(function (d) { return d.koleksi === 'retur'; }) && /SUSULAN tukar/.test(SN.ringkas) && SN.nota.retur === null, JSON.stringify(SN.dokumen));
terapkanKeCache(SN.dokumen); terap(SN.patch); ok('T: sesudah dicatat: ry1 tidak yatim lagi', returYatim().length === 0);
terapkanKeCache([{ koleksi: 'retur', data: { id: 'ry2', tanggal: '2026-09-19', jam: '09:00', jenisAsal: 'karung', merkSumber: 'Angsa', jumlahKarung: 1, beratKarungAcuan: 50, totalKg: 50, kondisi: 'utuh', penyelesaian: 'tukar', nominalRefund: 690000, selisihHargaTukar: 0, tukarModel: 'kreditBarangGabung', notaAsalId: 's2', catatan: 'x', hitunganTukarSistem: { pengganti: 72000, kredit: 690000, bersih: -618000, pembulatan: 0, caraBayar: 'Tunai' } } }]);
mulaiNota(); terap(ikatTukar(s, ikatSusulan('ry2').ikat)); terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap({ ketik: '1' }); terap(masukkan(s)); terap(uangPas(s));
ok('T: keranjang 690.000 MELEBIHI yang belum tercatat (72.000) → DITOLAK sampai "nilainya memang berubah"', /MELEBIHI yang belum tercatat/.test(alasanTolak(s)) && (terap(yakinLebihSusulan(s)), alasanTolak(s) === ''), alasanTolak(s));
ok('T: susulan untuk retur yang tidak yatim DITOLAK', /sudah punya pengganti tercatat/.test(ikatSusulan('ry1').tolak));
terapkanKeCache([{ koleksi: 'retur', data: { id: 'ry3', tanggal: '2026-09-18', jam: '09:00', jenisAsal: 'kemasan', namaProduk: 'Kembang', ukuranKemasan: 5, jumlahUnit: 1, totalKg: 5, kondisi: 'utuh', penyelesaian: 'tukar', nominalRefund: 72000, selisihHargaTukar: 0, tukarModel: 'kreditBarang', notaAsalId: 's3', catatan: 'x' } }]);
var CP = calonPengganti('ry3', s.sekarang);
ok('T: calon pengganti ry3 (18 Sep 09:00, model lama): penjualan sejak 18 Sep, bukan pengganti-retur, tidak tertaut retur lain, terdekat jamnya dulu (s5 09:30 sebelum s3 10:00); nota batal s4 tidak ikut', CP.length >= 2 && CP[0].id === 's5' && CP.some(function (c) { return c.id === 's3'; }) && !CP.some(function (c) { return c.id === 's4'; }), JSON.stringify(CP.map(function (c) { return c.id + ' ' + c.tanggal + ' ' + c.jam; })));
ok('T: menandai penjualan yang bukan calon DITOLAK', /tidak ada di daftar calon/.test(susunPenggantiTercatat('ry3', 'tidak-ada', W).tolak));
var PT = susunPenggantiTercatat('ry3', 's3', W); ok('T: pengganti sudah tercatat: dokumen retur ry3 ditulis ulang dengan penggantiDikonfirmasi {penjualanId s3, pada}; penjualan tidak disentuh', !PT.tolak && PT.dokumen.length === 1 && PT.dokumen[0].koleksi === 'retur' && PT.dokumen[0].data.penggantiDikonfirmasi.penjualanId === 's3' && PT.dokumen[0].data.penggantiDikonfirmasi.pada, JSON.stringify(PT));
terapkanKeCache(PT.dokumen); ok('T: sesudah ditandai: ry3 keluar dari daftar yatim (ry2 masih)', returYatim().length === 1 && returYatim()[0].id === 'ry2', JSON.stringify(returYatim()));

// ================= PUTARAN 21 (owner 23 Sep): belanja terakhir orang bernama · ulangi · saran benang (ojek) · takar dari karung yang dipilih di deretan =================
terap(Object.assign(keadaanAwal(), { sekarang: new Date('2026-09-19T10:00:00'), pelanggan: 'Bu Suti' }));
var PB = pembelianTerakhir(s, 3);
ok('U: belanja terakhir Bu Suti: nota-nota MILIKNYA saja, terbaru dulu, tiap nota = Σ barisnya, teks barisnya & berapa hari lalu; tanpa nama → kosong', PB.length >= 2 && PB.every(function (x) { return x.baris.every(function (p) { return kunciPelanggan(p.namaPelanggan) === 'bu suti'; }) && x.total === x.baris.reduce(function (a, p) { return a + (p.hargaTotal || 0); }, 0) && x.teks.length > 0 && x.hariLalu >= 0; })
  && (PB[0].tanggal + PB[0].jam) >= (PB[1].tanggal + PB[1].jam) && PB.some(function (x) { return x.grup === 'g3'; }) && pembelianTerakhir(Object.assign({}, s, { pelanggan: '' }), 3).length === 0, JSON.stringify(PB.map(function (x) { return [x.grup, x.tanggal, x.jam, x.total, x.teks]; })));
var nSblm = s.keranjang.length; var UL = ulangiPembelian(s, susunRak(s), 'g3');
ok('U: ulangi nota g3 (Kembang 5 kg × 1): satu baris kemasan masuk keranjang dengan HARGA HARI INI (chip), kabarnya menyebutnya; nota yang tidak ada ditolak', !!UL.keranjang && UL.keranjang.length === nSblm + 1 && UL.keranjang[UL.keranjang.length - 1].trx.jenis === 'kemasan' && UL.keranjang[UL.keranjang.length - 1].trx.jumlahUnit === 1 && UL.keranjang[UL.keranjang.length - 1].trx.hargaSatuan === chip('kemasan', chip('kemasan', 'Kembang|5') ? 'Kembang|5' : susunRak(s).kemasan[0].kunci).harga && /harga hari ini/.test(UL.kabar) && /tidak ketemu/.test(ulangiPembelian(s, susunRak(s), 'g-tidak-ada').kabar), JSON.stringify([UL.kabar, UL.keranjang && UL.keranjang.slice(-1)[0].trx]));
pasok('pelangganTitip', [{ id: 'tt1', dari: 'bang ojek contoh', untuk: 'bu suti', apa: 'disuruh belanja', kali: 2, tanggal: '2026-09-18' }]);
var SB = saranBenang('Bang Ojek Contoh');
ok('U: saran benang: nama yang tercatat biasa datang UNTUK orang lain → tawaran mencatat atas nama yang punya urusan (nama dari nota: Bu Suti); yang punya urusan sendiri / nama kosong → tidak ada saran', !!SB && SB.untuk === 'Bu Suti' && SB.kali === 2 && /biasanya datang untuk Bu Suti \(disuruh belanja, 2×\)/.test(SB.teks) && saranBenang('Bu Suti') === null && saranBenang('') === null, JSON.stringify(SB));
pasok('pelangganTitip', []);
var DK = deretanKarung(); var TD = tambahTakarDari([{ merk: 'Angsa', takar: 0 }], 'IR64 Apex', 'Angsa');
ok('U: deretan karung terbuka terbaca (tiap karung: nama, lokasi, letak); tambah takar DARI karung tertentu: baris baru {merk, takar 1, dari}, ketuk lagi → 2; baris kosong senama diisi (bukan baris baru)', DK.every(function (k) { return k.merk && typeof k.lokasi === 'string' && k.letak; }) && TD.length === 2 && TD[1].merk === 'IR64 Apex' && TD[1].dari === 'Angsa' && TD[1].takar === 1 && tambahTakarDari(TD, 'IR64 Apex', 'Angsa')[1].takar === 2 && tambahTakarDari(TD, 'IR64 Apex', 'Angsa').length === 2
  && (function () { var t = tambahTakarDari([{ merk: 'Angsa', takar: 0 }], 'Angsa', 'Angsa'); return t.length === 1 && t[0].takar === 1 && t[0].dari === 'Angsa'; })(), JSON.stringify([DK.length, TD]));
var hOto = hitungTakar('Angsa', [{ merk: 'IR64 Apex', takar: 1 }], s); var hPilih = hitungTakar('Angsa', [{ merk: 'IR64 Apex', takar: 1, dari: '' }], s);
ok('U: takar tanpa "dari" memakai karung otomatis (lokasiSumber); dengan "dari" = karung yang DIPILIH owner (karung lepas ""), walau otomatisnya menunjuk karung lain', hOto.sumber[0].dari === lokasiSumber('IR64 Apex', 'Angsa') && hPilih.sumber[0].dari === '' && hPilih.sumber[0].karung.lokasi === '', JSON.stringify([hOto.sumber[0].dari, hPilih.sumber[0].dari]));

// ---- GANTI ORANG (putaran 23c, owner 24 Sep): keranjang TIDAK terbawa ke akun berikutnya (alur Keluar/masuk diuji di peramban: uji_layar_kunci.py)
terap(Object.assign(keadaanAwal(), { sekarang: new Date('2026-09-19T10:00:00') }));
var sisaAwal = chip('karung', 'Angsa', 50).sisa;
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap(tekanTuts(s, '2')); terap(masukkan(s)); terap({ pelanggan: 'Pembeli Contoh' }); terap(parkir(s));
terap(ketukChip(s, chip('karung', 'Angsa', 50))); terap(tekanTuts(s, '1')); terap(masukkan(s));
var BD = barisBelumDisimpan(s), sisaDipegang = chip('karung', 'Angsa', 50).sisa;
ok('23c: baris belum disimpan = keranjang aktif + yang diparkir (1 + 1); kalimat tanyanya persis kalimat owner', BD.aktif === 1 && BD.parkir === 1 && BD.total === 2 && kalimatKeranjangKeluar(2) === 'Keranjang berisi 2 baris belum disimpan — simpan atau kosongkan?', JSON.stringify(BD));
var sPs = Object.assign(keadaanAwal(), { psNama: 'Pesanan Contoh' }), sRt = Object.assign(keadaanAwal(), { rtNominal: '5000' }), sStr = Object.assign(keadaanAwal(), { aturStruk: { kop: 'x' } });
ok('23d: isian Jual selain keranjang terdeteksi (pesanan yang diketik, retur, setelan struk terbuka); keadaan awal = tanpa isian; sesudah orang berikutnya = tanpa isian', adaIsianLain(sPs) && adaIsianLain(sRt) && adaIsianLain(sStr) && !adaIsianLain(keadaanAwal()) && !adaIsianLain(keadaanOrangBerikutnya(sPs)));
var sLama = s; s = keadaanOrangBerikutnya(Object.assign({}, s, { isiW: 3 }));
ok('23c: orang berikutnya — keranjang, parkir, nama pembeli kosong; kunci di luar keadaanAwal ikut dibuang; "sekarang" tetap; stok yang dipegang keranjang (3 karung) dilepas', s.keranjang.length === 0 && s.antrean.length === 0 && s.pelanggan === '' && s.isiW === undefined && s.sekarang === sLama.sekarang && barisBelumDisimpan(s).total === 0 && sisaDipegang === sisaAwal - 3 && chip('karung', 'Angsa', 50).sisa === sisaAwal, JSON.stringify([sisaAwal, sisaDipegang, chip('karung', 'Angsa', 50).sisa, s.antrean.length]));

terap(Object.assign(keadaanAwal(), { sekarang: new Date('2026-09-19T10:00:00') }));

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
// kolom BARU milik sistem baru (putaran 15, tercatat di BACA-DULU): baris wadah & repack berwadah/berupah — sistem lama tidak menulisnya
['jenisWadah', 'kemasanRepack', 'jumlahKemasanRepackDipakai', 'biayaKemasanRepack', 'upahRepack'].forEach(function (k) { dikenal[k] = true; });
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
            # ---- PUTARAN 23c: ganti orang
            'orang berikutnya mewarisi keranjang yang diparkir': js.replace("const baru = Object.assign(keadaanAwal(), { sekarang: (s && s.sekarang) || null });", "const baru = Object.assign(keadaanAwal(), { sekarang: (s && s.sekarang) || null, antrean: (s && s.antrean) || [] });"),
            'orang berikutnya: stok yang dipegang keranjang lama tidak dilepas': js.replace("  sinkronKeranjang(baru);\n  return baru;", "  return baru;"),
            'isian pesanan Jual tidak terdeteksi': js.replace("const ISIAN_JUAL_LAIN = ['psNama', ", "const ISIAN_JUAL_LAIN = ["),
            'baris belum disimpan lupa keranjang yang diparkir': js.replace("return { aktif, parkir, total: aktif + parkir };", "return { aktif, parkir, total: aktif };"),
            # ---- PUTARAN 21: belanja terakhir · saran benang · takar dari karung yang dipilih
            'belanja terakhir mencampur nota orang lain': js.replace("if (kunciPelanggan(p.namaPelanggan) !== k) return; const g = String(p.grupNota || p.id);", "const g = String(p.grupNota || p.id);"),
            'belanja terakhir diurutkan terlama dulu (yang "terakhir" bukan yang terbaru)': js.replace("return Object.keys(per).map((g) => per[g]).sort((a, b) => (b.tanggal + b.jam).localeCompare(a.tanggal + a.jam)).slice(0, n || 3)", "return Object.keys(per).map((g) => per[g]).sort((a, b) => (a.tanggal + a.jam).localeCompare(b.tanggal + b.jam)).slice(0, n || 3)"),
            'saran benang ditawarkan juga untuk yang punya urusan sendiri': js.replace("if (!namaUntuk || kunciPelanggan(namaUntuk) === k) return null;", "if (!namaUntuk) return null;").replace("const titip = cacheMentah('titip').filter((t) => t.dari === k && t.untuk)", "const titip = cacheMentah('titip').filter((t) => (t.dari === k || t.untuk === k) && t.untuk)"),
            'takar mengabaikan karung yang dipilih owner di deretan': js.replace("const dari = x.dari !== undefined && x.dari !== null ? String(x.dari) : lokasiSumber(x.merk, merk);", "const dari = lokasiSumber(x.merk, merk);"),
            # ---- PUTARAN 20: rinci karcis · retur tanpa nota · tukar yatim
            'rinci: kelebihan barang atas uang yang masuk lolos': js.replace("const H = hitungKarcis(s); if (H.lebih) return { tolak: 'Jumlah barang '", "const H = hitungKarcis(s); if (false) return { tolak: 'Jumlah barang '"),
            'rinci: baris tanpa tanda asalDarurat/rinciDari (tarik balik & penjaga karcis buta)': js.replace("if (karcis) { d.asalDarurat = true; d.rinciDari = p.id; d.alasanKoreksi = 'Rincian dari kasir darurat ' + kcEkor(p.id); }", "if (false) { d.asalDarurat = true; d.rinciDari = p.id; }"),
            'rinci: sisa yang belum terurai hilang (uang masuk berkurang)': js.replace("if (karcis && H.sisa > 0) { const sisaDoc =", "if (false) { const sisaDoc ="),
            'rinci: karcis asli tidak ditandai (uang dua kali)': js.replace("  dokumen.push({ koleksi: 'penjualan', data: asli });\n  // putaran 25: karcis bulan lalu", "\n  // putaran 25: karcis bulan lalu"),
            'rinci: tanggal baris = hari ini, bukan tanggal karcis (omzet pindah hari)': js.replace("d.id = w.idUnik(); d.tanggal = p.tanggal; d.jam = p.jam || ''; d.caraBayar = cara;", "d.id = w.idUnik(); d.tanggal = w.tanggal; d.jam = w.jam; d.caraBayar = cara;"),
            'rapikan boleh bersisa (uang nota bergeser)': js.replace("if (k.jenisAsal === 'rapikan' && H.sisa !== 0) return { tolak:", "if (false) return { tolak:"),
            'tarik balik grup yang sudah tersentuh (uang dobel)': js.replace("if (tersentuh) return { tolak: 'Tidak bisa ditarik balik:", "if (false) return { tolak: 'Tidak bisa ditarik balik:"),
            'retur tanpa nota: melebihi yang pernah terjual lolos tanpa ketukan kedua': js.replace("if (jml > bebas && !s.rtYakin) return { tolak:", "if (false) return { tolak:"),
            'retur tanpa nota: refund tanpa nominal lolos (Rp0 diam-diam)': js.replace("if (!(n > 0)) return { tolak: 'Isi nominal uang yang dikembalikan", "if (false) return { tolak: 'Isi nominal uang yang dikembalikan"),
            'susulan menulis retur BARU lagi (barang terkredit dua kali)': js.replace("if (tk && !tk.susulanReturId) {\n    const rd = Object.assign({}, tk.returDraf,", "if (tk) {\n    const rd = Object.assign({}, tk.returDraf,"),
            'susulan boleh BON': js.replace("if (s.cara === 'Kredit') return 'Susulan tukar tidak bisa BON", "if (false) return 'Susulan tukar tidak bisa BON"),
            'keranjang susulan melebihi yang belum tercatat lolos diam-diam': js.replace("if (total > kurang + 499 && !yakinLebih) return 'Keranjang '", "if (false) return 'Keranjang '"),
            '"pengganti sudah tercatat" tidak meninggalkan tanda di retur': js.replace("penggantiDikonfirmasi: { penjualanId: String(penjualanId), pada:", "penggantiDikonfirmasiX: { penjualanId: String(penjualanId), pada:"),
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
            'bonus ikut ditagih (uang = unit + bonus)': js.replace("const nilai = Math.round(t.hargaSatuan * t.jumlah) + (t.upahRepack || 0);", "const nilai = Math.round(t.hargaSatuan * (t.jumlahUnit || t.jumlah)) + (t.upahRepack || 0);"),
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
            'pembulatan tukar atas keranjang penuh, bukan selisih': js.replace("const bulatNota = bulatKeranjang(Object.assign({}, s, { cara }), totalSetelahPot - kreditTukar);", "const bulatNota = bulatKeranjang(Object.assign({}, s, { cara }), totalSetelahPot);"),
            'tukar boleh dicatat BON': js.replace("if (s.cara === 'Kredit') return 'Tukar tidak bisa dicatat BON", "if (false) return 'Tukar tidak bisa dicatat BON"),
            'tukar boleh dibayar sebagian': js.replace("if (t.uang > 0 && t.uang < t.total) return 'Tukar tidak bisa dibayar sebagian", "if (false) return 'Tukar tidak bisa dibayar sebagian"),
            'pengganti lebih murah dari retur lolos': js.replace("if (t.bersih < 0) return 'Nilai retur '", "if (false) return 'Nilai retur '"),
            'penjualan pengganti tanpa tukarReturId': js.replace("if (tk) d.tukarReturId = String(tk.susulanReturId || tk.returDraf.id);", ""),
            'retur tukar tidak ikut ditulis bersama notanya': js.replace("    dokumen.push({ koleksi: 'retur', data: rd });\n", ""),
            'kembalian tukar dihitung dari nilai keranjang': js.replace("d.kembalian = Math.max(0, uang - (totalBayar - kreditTukar));", "d.kembalian = Math.max(0, uang - totalBayar);"),
            'pembatalan nota tukar meninggalkan returnya': js.replace("if (notaTerakhir.retur) { hapus.push({ koleksi: 'retur', id: notaTerakhir.retur.id });", "if (false) { hapus.push({ koleksi: 'retur', id: notaTerakhir.retur.id });"),
            'parkir melepas ikatan tukar': js.replace("pesananId: s.pesananId || null, tukar: s.tukar || null, pada:", "pesananId: s.pesananId || null, tukar: null, pada:"),
            'draf tukar tidak dibaca ulang saat mencatat': js.replace("const cek = cekDrafTukar(s.tukar.returDraf); if (cek) return cek;", ""),
            # ---- putaran 6: tata letak & wadah ----
            'kemasan tidak diurutkan dari termurah': js.replace("rak.kemasan.sort((a, b) => a.ukuranKg - b.ukuranKg || termurah(a, b));", "rak.kemasan.sort((a, b) => a.ukuranKg - b.ukuranKg || b.harga - a.harga);"),
            'kemasan tidak dikelompokkan per ukuran': js.replace("kemasan: kelompokkan(rak.kemasan, (c) => c.ukuranKg,", "kemasan: kelompokkan(rak.kemasan, (c) => 0,"),
            'wadah yang belum pernah ditandai digambar PENUH (ditebak)': js.replace("if (!tanda) return { wadah: true, diketahui: false, penuhKg: WADAH_PENUH, puncakKg: WADAH_PUNCAK, takarKg: atur.takarKg };", "if (!tanda) return { wadah: true, diketahui: true, sisaKg: 50, gunung: 1, dalam: 1, perluIsi: false };"),
            'literan SEBELUM tanda isi ulang ikut mengurangi': js.replace("p.merkSumber === merk && wdSesudah(p, tanda) ? (p.totalKg || 0) : 0), 0);", "p.merkSumber === merk ? (p.totalKg || 0) : 0), 0);"),
            'keranjang tidak menurunkan gunung': js.replace("const dipegang = literKeranjang(s && s.keranjang) +", "const dipegang = 0 * literKeranjang(s && s.keranjang) + 0 *"),
            '50 kg masih digambar menggunung (rata tidak sejajar bibir kotak)': js.replace("gunung: WADAH_PUNCAK > WADAH_PENUH ? Math.max(0, Math.min(1, (sisaKg - WADAH_PENUH) / (WADAH_PUNCAK - WADAH_PENUH))) : 0,", "gunung: Math.max(0, Math.min(1, sisaKg / WADAH_PENUH)),"),
            'tidak pernah minta isi ulang': js.replace("perluIsi: nyata <= WADAH_ULANG,", "perluIsi: false,"),
            'pratinjau takar yang belum dicatat mematikan permintaan isi ulang': js.replace("perluIsi: nyata <= WADAH_ULANG,", "perluIsi: sisaKg <= WADAH_ULANG,"),
            'kelebihan jual sesudah tanda disembunyikan': js.replace("lewat: sisaKg < 0 ? wdB2(-sisaKg) : 0,", "lewat: 0,"),
            'tanda isi ulang satu wadah mengisi semua wadah': js.replace("semua.filter((w) => w.wadah === merk && w.tipe === 'isi')", "semua.filter((w) => w.tipe === 'isi')"),
            'karung/kemasan ikut mengurangi wadah': js.replace("a + (p.jenis === 'literan' && p.merkSumber === merk && wdSesudah(p, tanda)", "a + (p.merkSumber === merk && wdSesudah(p, tanda)"),
            # ---- koreksi owner 19 Sep: takar demi takar dari karung di belakang wadah ----
            'takar yang dicatat tidak menaikkan isi wadah': js.replace("const nyata = wdB2(isi + dituang - terjual - dipegang);", "const nyata = wdB2(isi - terjual - dipegang);"),
            'takar wadah lain ikut menaikkan wadah ini': js.replace("a + (t.tipe === 'takar' && t.wadah === merk && wdSesudah(t, tanda) ? (Number(t.kg) || 0) : 0), 0);", "a + (t.tipe === 'takar' && wdSesudah(t, tanda) ? (Number(t.kg) || 0) : 0), 0);"),
            'takar SEBELUM titik samakan ikut dihitung': js.replace("a + (t.tipe === 'takar' && t.wadah === merk && wdSesudah(t, tanda) ? (Number(t.kg) || 0) : 0), 0);", "a + (t.tipe === 'takar' && t.wadah === merk ? (Number(t.kg) || 0) : 0), 0);"),
            'isian melebihi batas menggunung lolos (dipotong diam-diam)': js.replace("if (h.lewat) return { tolak: 'Isian ini membuat wadah jadi '", "if (false) return { tolak: 'Isian ini membuat wadah jadi '"),
            'takar tidak mengurangi karung di belakang wadah': js.replace("const sisa = wdB2(masuk - diambil); const akhir", "const sisa = wdB2(masuk); const akhir"),
            'takar campuran membebani SEMUA karung (bukan nama masing-masing)': js.replace("b + (x.merk === merk && wdLokasiSumber(x, daftar) === L ? (Number(x.kg) || 0) : 0), 0)", "b + (wdLokasiSumber(x, daftar) === L ? (Number(x.kg) || 0) : 0), 0)"),
            'takar sebelum karung dibuka ikut mengurangi karung itu': js.replace("(t.tipe === 'takar' && wdSesudah(t, mulai) ?", "(t.tipe === 'takar' && true ?"),
            'karung habis tidak diganti (karung di belakang jadi minus diam-diam)': js.replace("const buka = kurang > 0.0001 ? Math.ceil(", "const buka = false ? Math.ceil("),
            'karung yang belum pernah ditandai dibuka diam-diam': js.replace("const kurang = k.diketahui ? kg - k.sisaKg : 0;", "const kurang = kg - (k.sisaKg || 0);"),
            'samakan karung bukan titik hitung baru (karung lama ikut dijumlah)': js.replace("k.tipe === 'karung' && diSini(k) && (!dasar || wdSesudah(k, dasar)));", "k.tipe === 'karung' && diSini(k));"),
            'sampai rata dibulatkan ke ATAS (melewati target)': js.replace("const putaran = Math.max(0, Math.floor((targetKg - w.sisaNyataKg + 0.0001) /", "const putaran = Math.max(0, Math.ceil((targetKg - w.sisaNyataKg + 0.0001) /"),
            'sampai rata merusak perbandingan campuran': js.replace("const pola = dasar.map((x) => ({ merk: x.merk, takar: Math.round(Number(x.takar)) / g }));", "const pola = dasar.map((x) => ({ merk: x.merk, takar: 1 }));"),
            'aturan mustahil diterima (menggunung di bawah rata)': js.replace("if (!(puncak >= penuh)) return { tolak:", "if (false) return { tolak:"),
            'satu beras boleh punya dua wadah': js.replace("if (kembar) return { tolak:", "if (false) return { tolak:"),
            'angka takar dari owner diabaikan (tetap 1,8 kg)': js.replace("const takarKg = a && Number(a.takarKg) > 0 ? Number(a.takarKg) : WADAH_TAKAR_KG;", "const takarKg = WADAH_TAKAR_KG;"),
            'batas menggunung dari owner diabaikan': js.replace("const puncakKg = a && Number(a.puncakKg) >= penuhKg ? Number(a.puncakKg) :", "const puncakKg = false ? 0 :"),
            'urutan posisi wadah dari owner diabaikan': js.replace("const daftar = a && Array.isArray(a.daftar) && a.daftar.length ? a.daftar.map(String) : DAFTAR_WADAH.slice();\n  const resep", "const daftar = DAFTAR_WADAH.slice();\n  const resep"),
            'samakan wadah di atas batas menggunung diterima': js.replace("if (!(kg >= 0) || kg > atur.puncakKg) return { tolak: 'Isi wadah harus", "if (false) return { tolak: 'Isi wadah harus"),
            'tumpukan gudang lupa mengurangi karung terbuka (buka karung tidak menurunkan gudang)': js.replace("const kg = wdB2(namaKg - diBelakang - diWadah); const berat", "const kg = wdB2(namaKg - diWadah); const berat"),
            # ---- owner 21 Sep: rantai stok bertingkat, karung di belakang wadah bernama ----
            'nama karung di belakang wadah diabaikan (selalu nama wadahnya)': js.replace("return { wadah, merk: a ? String(a.merk) : wadah, dariCatatan: !!a };", "return { wadah, merk: wadah, dariCatatan: !!a };"),
            'karung bahan campuran (lepas) mengaku di belakang wadah senama': js.replace("(d.wadah ? String(d.wadah) : d.lepas ? '' : (daftar.indexOf(String(d.merk)) >= 0 ? String(d.merk) : ''))", "(d.wadah ? String(d.wadah) : (daftar.indexOf(String(d.merk)) >= 0 ? String(d.merk) : ''))"),
            'catatan karung lama (tanpa kolom wadah) tidak dikenali lagi': js.replace("(d.wadah ? String(d.wadah) : d.lepas ? '' : (daftar.indexOf(String(d.merk)) >= 0 ? String(d.merk) : ''))", "(d.wadah ? String(d.wadah) : '')"),
            'kolam karung per NAMA saja, bukan per tempat (satu karung dipakai dua wadah — temuan tinjau)': js.replace("const diSini = (k) => k.merk === merk && wdLokasiDoc(k, daftar) === L;", "const diSini = (k) => k.merk === merk;"),
            'takar dari tempat lain ikut memotong kolam ini': js.replace("b + (x.merk === merk && wdLokasiSumber(x, daftar) === L ? (Number(x.kg) || 0) : 0), 0)", "b + (x.merk === merk ? (Number(x.kg) || 0) : 0), 0)"),
            'takar tidak mencatat dari tempat mana karungnya diambil': js.replace("sumber: h.sumber.map((x) => ({ merk: x.merk, takar: x.takar, kg: x.kg, dari: x.dari })) }, produksi ?", "sumber: h.sumber.map((x) => ({ merk: x.merk, takar: x.takar, kg: x.kg })) }, produksi ?"),
            'nota literan di menit yang sama sesudah samakan tidak dipotong (pemutus seri cuma menit)': js.replace("p.merkSumber === merk && wdSesudah(p, tanda) ?", "p.merkSumber === merk && cap(p) > cap(tanda) ?"),
            'rework karantina dianggap hitungan gudang (pindahan nama dibuang, beras dihitung dua kali)': js.replace("if (o.merk && hitunganFisik(o) && (!cocokAkhir[o.merk]", "if (o.merk && (!cocokAkhir[o.merk]"),
            'campuran satu baris yang menyalin karung di belakang wadah ikut disimpan (terpaku ke nama lama)': js.replace("(r[0].merk === m || r[0].merk === bawaan) && r[0].takar === 1", "r[0].merk === m && r[0].takar === 1"),
            'samakan karung dengan kotak kosong menulis 0 kg': js.replace("if (String(isiKg === undefined || isiKg === null ? '' : isiKg).trim() === '') return { tolak:", "if (false) return { tolak:"),
            'tuts koma ditolak untuk karung (setengah karung tidak bisa diketik)': js.replace("(s.pilih && (s.pilih.jalur === 'kemasan' || s.pilih.jalur === 'wadah')))", "(s.pilih && s.pilih.jalur !== 'literan' && s.pilih.jalur !== 'repack'))"),
            'takar lintas nama TIDAK memindahkan buku (dokumen produksi tidak ditulis)': js.replace("  if (asing.length) {\n    const stok = hitungStokKarungPerMerk();", "  if (false) {\n    const stok = hitungStokKarungPerMerk();"),
            'pindah buku tanpa modal (nilai nol)': js.replace("hppSumberPerKgDipakai: kgP > 0 ? nilai / kgP : 0, hppPerUnit: nilai,", "hppSumberPerKgDipakai: 0, hppPerUnit: 0,"),
            'pindah buku ditulis sebagai kemasan jadi (bukan jadi karung utuh)': js.replace("jadiKarungUtuh: true, merkTujuan: merk, dariTakar: true,", "jadiKarungUtuh: false, merkTujuan: merk, dariTakar: true,"),
            'pindah nama dihitung DUA KALI (takar yang sudah pindah buku masih ditambah di layar)': js.replace("if (t.produksiId !== undefined && t.produksiId !== null && diBuku[String(t.produksiId)]) return;", "if (false) return;"),
            'takar senama selalu mengambil dari karung di belakang wadah lain (bukan wadahnya sendiri)': js.replace("if (karungUntukWadah(wadah).merk === merk) return wadah;", "if (false) return wadah;"),
            'buka karung tidak mencatat di belakang wadah mana': js.replace("tipe: 'karung', merk, kg }, di ? { wadah: di } : { lepas: true }) }],", "tipe: 'karung', merk, kg }, { lepas: true }) }],"),
            'karung otomatis tidak mencatat di belakang wadah mana': js.replace("kg: berat, otomatis: true }, x.dari ? { wadah: x.dari } : { lepas: true }) });", "kg: berat, otomatis: true }, { lepas: true }) });"),
            'nama yang tidak ada di buku gudang boleh dibuka': js.replace("if (!t.adaBuku) return { tolak: merk + ' tidak ada di buku gudang", "if (false) return { tolak: merk + ' tidak ada di buku gudang"),
            'takar karung nama lain tidak pindah nama (tumpukan karung asal naik lagi saat ditakar)': js.replace("const namaKg = wdB2(buku.sisaKg - keluarKg + masukKg);", "const namaKg = wdB2(buku.sisaKg);"),
            'pindah nama cuma dicatat keluar (wadah tujuan tidak menerima)': js.replace("const namaKg = wdB2(buku.sisaKg - keluarKg + masukKg);", "const namaKg = wdB2(buku.sisaKg - keluarKg);"),
            'pindahan SEBELUM hitungan gudang terakhir ikut dihitung (dipotong dua kali)': js.replace("if (!cocokAkhir[x.merk] || wdSesudah(t, cocokAkhir[x.merk])) keluar", "if (true) keluar"),
            'hitungan tumpukan memakai angka terjepit nol (lupa catat isi ulang menggeser tumpukan diam-diam)': js.replace("const diWadah = w && w.diketahui ? w.nyataMentahKg : 0;", "const diWadah = w && w.diketahui ? w.sisaNyataKg : 0;"),
            'campuran bawaan tidak mengikuti karung di belakang wadah': js.replace(": [{ merk: karungUntukWadah(merk).merk, takar: 1 }]; }", ": [{ merk, takar: 1 }]; }"),
            'calon karung memuat nama yang tumpukannya sudah habis': js.replace(".filter((t) => t.adaBuku && t.kg > 0);\n}", ".filter((t) => t.adaBuku);\n}"),
            'dokumen retur membawa kunci yang tidak dikenal index.html': js.replace("kondisi: s.rtKondisi, penyelesaian:", "kunciAsingUji: 1, kondisi: s.rtKondisi, penyelesaian:"),
            'dokumen karantina membawa kunci yang tidak dikenal index.html': js.replace("statusTindakan: 'belum_diputuskan' } };", "statusTindakan: 'belum_diputuskan', kunciAsingUji: 1 } };"),
            'dua tukar diikat ke satu keranjang': js.replace("if (s.tukar) return { kabar: 'Keranjang ini MASIH terikat tukar: '", "if (false) return { kabar: 'Keranjang ini MASIH terikat tukar: '"),
            # ---- putaran 15: wadah dijual ----
            'wadah tanpa harga jual ikut tampil di rak': js.replace("return daftarJenisWadah().filter((d) => harga[d.jenis]).map((d) => {", "return daftarJenisWadah().map((d) => { harga[d.jenis] = harga[d.jenis] || { harga: 0 };"),
            'wadah dijual tidak memotong buku kantong (tanpa dokumen pakai)': js.replace("if (d.jenis === 'wadah' && d.jenisWadah && d.jumlahUnit > 0) {", "if (false) {"),
            'langit-langit buku kantong diabaikan untuk wadah': js.replace("if (chip.jalur === 'wadah') return bebasWadah(chip.kunci, wadahDipegang(chip.kunci));", "if (chip.jalur === 'wadah') return null;"),
            'wadah tanpa modal ditulis HPP 0 (mesin laba menganggapnya margin penuh)': js.replace("if (chip.adaModal) t.hppTotalSaatJual = Math.round(chip.modal * j);", "t.hppTotalSaatJual = chip.adaModal ? Math.round(chip.modal * j) : 0;"),
            'modal kantong dipakai walau buku belinya kosong (Rp0 jadi modal)': js.replace("const ada = (st.totalBeli || 0) > 0 && (st.hppPerPcs || 0) > 0;", "const ada = true;"),
            'wadah ditanggung toko tidak masuk HPP baris repack': js.replace("t.kemasanRepack = e.kemasanRepack; t.jumlahKemasanRepackDipakai = b.lembar; t.biayaKemasanRepack = b.biaya; t.hppTotalSaatJual += b.biaya;", "t.kemasanRepack = e.kemasanRepack; t.jumlahKemasanRepackDipakai = b.lembar; t.biayaKemasanRepack = b.biaya;"),
            'upah repack tidak ikut ditagih': js.replace("const nilai = Math.round(t.hargaSatuan * t.jumlah) + (t.upahRepack || 0);", "const nilai = Math.round(t.hargaSatuan * t.jumlah);"),
            'wadah & upah hilang saat baris repack dibangun ulang (+1 kg)': js.replace("kemasanRepack: t.kemasanRepack, jumlahKemasanRepack: t.jumlahKemasanRepackDipakai, upahRepack: t.upahRepack });", "});"),
            'pembatalan tidak memulihkan buku kantong wadah': js.replace("baris.forEach((p) => { if (p.jenis === 'wadah' && p.jenisWadah) hapus.push({ koleksi: koleksiWadah(p.jenisWadah), id: p.id + 1 });", "baris.forEach((p) => { if (false) hapus.push({ koleksi: koleksiWadah(p.jenisWadah), id: p.id + 1 });"),
            'lantai Rp100/lembar dilewati (Rp50 diterima)': js.replace("if (n > 0 && n < WJ_LANTAI_LEMBAR) { salah.push(d.label + ': ' + RP(n) + ' per lembar'); return; }", ""),
            'saran lembar dibulatkan ke bawah': js.replace("return Math.max(1, Math.ceil(Math.round(k / d.ukuranKg * 1000) / 1000));", "return Math.max(1, Math.floor(Math.round(k / d.ukuranKg * 1000) / 1000));"),
            'struk parkir tidak memegang lembar wadah': js.replace("function wadahDipegangParkir(jenis) { return _antreanKini.reduce(", "function wadahDipegangParkir(jenis) { return [].reduce("),
            # ---- putaran 15: struk ----
            'TOTAL struk bukan jumlah hargaTotal': js.replace("cara: bakuCaraBayar(p.caraBayar), oleh: p.oleh || '', total: rows.reduce((a, x) => a + (x.hargaTotal || 0), 0),", "cara: bakuCaraBayar(p.caraBayar), oleh: p.oleh || '', total: rows.reduce((a, x) => a + kotorBaris(x), 0),"),
            'potongan tidak tertulis di struk': js.replace("if (pot > 0) baris('Potongan', '−' + RP(pot));", ""),
            'sisa bon selalu ikut walau dimatikan': js.replace("if (S.bon && nota.nama) { const r = hitungPiutang()", "if (nota.nama) { const r = hitungPiutang()"),
            'kolom 80 mm sama dengan 58 mm': js.replace("const ST_KOLOM = { 58: 30, 80: 42 };", "const ST_KOLOM = { 58: 30, 80: 30 };"),
            'pilihan pelanggan tidak mengalahkan aturan': js.replace("if (p === 'tidak') return { cetak: false, wa: false, teks: 'tidak (pilihan ' + nota.nama + ')' };", ""),
            'aturan WA bon menyala untuk nota tunai juga': js.replace("const wa = A.oto.wa === 'semua' || (A.oto.wa === 'bon' && nota.cara === 'Kredit');", "const wa = A.oto.wa === 'semua' || A.oto.wa === 'bon';"),
            'kop tidak dari setelan owner': js.replace("baris(A.kop.nama.toUpperCase(), '', { tebal: true, tengah: true });", "baris('TOKO BERAS M.IQBAL', '', { tebal: true, tengah: true });"),
            'kembalian tidak tertulis': js.replace("if (nota.uangDiterima > 0) { baris('Uang diterima', RP(nota.uangDiterima)); if (nota.kembalian > 0) baris('Kembali', RP(nota.kembalian)); }", ""),
            'nota dibatalkan disusun seolah masih berlaku': js.replace("if (!nota.berlaku) baris('(catatan ini sudah ' + (nota.dibatalkan ? 'dibatalkan' : 'dikoreksi') + ')', '');", ""),
            'setelan kertas 70 mm diterima': js.replace("const kertas = Number(a.kertas); if (!ST_KOLOM[kertas]) return { tolak: 'Lebar kertas hanya 58 atau 80 mm' };", "const kertas = Number(a.kertas);"),
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
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_arsip-mockup', 'backup-batch-*.json')), key=os.path.basename)   # cadangan toko boleh di akar, _privat/ atau _arsip-mockup/ (semua di-gitignore); yang terbaru menurut tanggal di namanya
    if cad:
        c = json.load(open(cad[-1], encoding='utf-8'))
        h, e = jalan(js + '\nvar CAD = ' + json.dumps(c) + ';\n' + ASAP)
        if h is None: print('ASAP DATA TOKO: JSC JATUH ' + e); g.append('asap')
        else: print('ASAP DATA TOKO (%s): rak karung %d · kemasan %d · literan %d · repack %d · pesanan aktif %d · sering %d · pelanggan %d · chip tanpa harga %d · kunci dokumen asing %s' % (os.path.basename(cad[-1]), h['karung'], h['kemasan'], h['literan'], h['repack'], h['pesanan'], h['sering'], h['pelanggan'], h['tanpaHarga'], h['kunciAsing'] or 'nihil'))
        if h and (h['karung'] == 0 or h['tanpaHarga'] > 0 or h['kunciAsing']): g.append('asap: rak kosong, chip tanpa harga, atau kunci dokumen yang tidak dikenal baris nyata')
    sys.exit(2 if g else 0)
