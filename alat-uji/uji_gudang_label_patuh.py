#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_gudang_label_patuh.py — PAKET STOK MINUS, LABEL & KEPATUHAN (keputusan owner 26 Nov 2026, sensus ulang 1c: B49 B50 B53 B54 · A49 A62 A78 · A16 A38 A45 +
"pasang notifikasi"). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  Gudang: buku minus = minusBuku (gerbang tutup buku) jenis stok, berrupiah, urut terdalam, 10 teratas · hilang & rusak per jenis beras menutup ke "Susut &
  selisih stok" Laporan · tugas gudang terbuka per jenis (opname & cek gudang = sumber pengingat sistem-logika) · Dasbor apa adanya.
  Label: umur simpan & kelas mutu (aturanToko/catatStok.label, dokumen lain di catatStok disalin utuh) · kemasan bertanggal FIFO (adukan tertua yang tersisa,
  lewat / dekat / aman, stok awal tanpa tanggal) · isi label lengkap & label tanggal masuk · ESC/POS & TSPL: tanpa `baris` = byte lama PERSIS (dibanding escpos.js
  HEAD), dengan `baris` = baris kecil tercetak.
  Kepatuhan: putaran butir (bulanan, 3 bulan, tahunan, sekali; SPT ikut bentuk usaha) · tanda "sudah dikerjakan" (kepatuhanCek = bentuk rules v22, akses.js
  cekPatuhSah) · pengingat & lonceng · push pagi functions/patuh.js = rumus yang SAMA dengan patuh-logika (ratusan tanggal) + kapan dikirim.

    python3 alat-uji/uji_gudang_label_patuh.py            → N lulus · 0 gagal
    python3 alat-uji/uji_gudang_label_patuh.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile, glob, hashlib
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru, uji_ringkasan_baru, uji_kunci_periode, uji_susut_harga  # noqa: E402
JSC = uji_antar.JSC
GD = 'baru/js/layar/gudang-logika.js'; LB = 'baru/js/layar/label-logika.js'; PT = 'baru/js/layar/patuh-logika.js'; EP = 'baru/js/inti/escpos.js'; SL = 'baru/js/layar/sistem-logika.js'
KB = 'baru/js/layar/kabar-baru-logika.js'; AK = 'baru/js/data/akses.js'; FP = 'functions/patuh.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_ringkasan_baru.modul_dasbor() + [AK, 'baru/js/data/hemat-baca.js', 'baru/js/layar/riwayat-logika.js', 'baru/js/layar/kpi-laba-logika.js', SL,
                                                                                    'baru/js/layar/tutup-buku-logika.js', 'baru/js/layar/potret-logika.js', 'baru/js/layar/upah-logika.js', KB, EP, GD, LB, PT])))
SUMBER = {'stok': 'baru/js/layar/stok.js', 'jual': 'baru/js/layar/jual.js', 'laporan': 'baru/js/layar/laporan.js', 'menu': 'baru/js/layar/menu.js', 'dasbor': 'baru/js/layar/dasbor.js',
          'app': 'baru/js/app.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'fi': 'functions/index.js', 'bundel': 'alat-uji/bundel_baru.py',
          'cssS': 'baru/css/stok.css', 'cssL': 'baru/css/laporan.css', 'cssM': 'baru/css/menu.css', 'cssJ': 'baru/css/jual.css', 'lonceng': 'baru/js/layar/lonceng.js', 'lp': 'baru/js/layar/label-panel.js',
          'pp': 'baru/js/layar/patuh-panel.js', 'gd': GD, 'lb': LB, 'pt': PT, 'dl': 'baru/js/layar/dasbor-logika.js', 'koleksi': 'baru/js/data/koleksi.js', 'rs': 'baru/js/layar/riwayat-setelan-logika.js'}

KS = uji_susut_harga.KOTAK_SH
JUAL = lambda i, tgl, merk, kg, harga, hpp: uji_susut_harga.KARUNG(i, tgl, merk, kg, harga, hpp)
KEMAS = lambda i, tgl, nama, uk, unit: {'id': i, 'tanggal': tgl, 'jam': '11:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'kemasan', 'namaProduk': nama, 'ukuranKemasan': uk, 'jumlahUnit': unit,
                                        'totalKg': uk * unit, 'hargaTotal': 70000 * unit, 'hppTotalSaatJual': 60000 * unit, 'grupNota': 'g' + i}
ADUK = lambda i, tgl, nama, uk, unit, **x: dict({'id': i, 'tanggal': tgl, 'jam': '09:00', 'namaProduk': nama, 'ukuranKemasan': uk, 'jumlahUnit': unit, 'hppPerUnit': 60000, 'merkSumber': 'Angsa',
                                                  'kgDipakai': 0, 'biayaKemasan': 0, 'upahRepacking': 0, 'kantongJenis': '', 'kantongJumlah': 0, 'hppSumberPerKgDipakai': 12000}, **x)
KOTAK = dict(KS)
# buku minus: Kembang −50,6 kg (−607.200) · Hantu 1–10 datang 1 kg, terjual 5×i kg · Kemas Hantu dibuat 1, terjual 3 (−2 × 60.000) · kantong5 −5 (tanpa harga beli)
KOTAK['batchMasuk'] = KS['batchMasuk'] + [{'id': 104, 'tanggal': '2026-11-02', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
    {'merk': 'Hantu %d' % i, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 1, 'totalKg': 1, 'subtotalHarga': 12000, 'hargaPerKg': 12000} for i in range(1, 11)]
    + [{'merk': 'Hantu Kecil', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 1, 'totalKg': 1, 'subtotalHarga': 12000, 'hargaPerKg': 12000}]}]
KOTAK['penjualan'] = KS['penjualan'] + [JUAL('m1', '2026-11-15', 'Kembang', 100, 1300000, 1200000)] + [JUAL('h%d' % i, '2026-11-15', 'Hantu %d' % i, 5 * i, 65000 * i, 60000 * i) for i in range(1, 11)] \
    + [JUAL('hk', '2026-11-15', 'Hantu Kecil', 1.5, 19500, 18000)] + [KEMAS('k1', '2026-11-16', 'Kemas Contoh', 5, 5), KEMAS('k2', '2026-11-16', 'Kemas Hantu', 10, 3)]
# adukan bertanggal (umur simpan bawaan 6 bulan): 10 Mei (lewat 10 Nov) · 1 Okt · 17 Nov; 5 terjual → yang tersisa tertua = 5 kantong 10 Mei. Stok awal = tanpa tanggal kemas.
KOTAK['produksiKemasan'] = [ADUK('pa', '2026-05-10', 'Kemas Contoh', 5, 10), ADUK('pb', '2026-10-01', 'Kemas Contoh', 5, 10), ADUK('pc', '2026-11-17', 'Kemas Contoh', 5, 10),
                            ADUK('pd', '2026-11-01', 'Kemas Dekat', 10, 4), ADUK('ps', '2026-08-08', 'Kemas Lama', 5, 3, stokAwal=True, beliJadi=True), ADUK('ph', '2026-11-02', 'Kemas Hantu', 10, 1)]
KOTAK['retur'] = [{'id': 'r1', 'tanggal': '2026-11-14', 'jam': '12:00', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'kondisi': 'tidak_utuh', 'alasan': 'kualitas kurang',
                   'nominalKembali': 130000, 'uangKembali': 130000, 'trxIdAsal': 'n1', 'caraKembali': 'tunai'}]
KOTAK['karantina'] = [{'id': 'r1', 'tanggal': '2026-11-14', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 10, 'asalRetur': True, 'statusTindakan': 'dibuang', 'tanggalKeputusan': '2026-11-15'}]
KOTAK['persetujuan'] = [{'id': 'pm1', 'tindakan': 'barangMasuk', 'status': 'menunggu', 'teks': 'Kabar contoh', 'batchId': '101', 'tanggal': '2026-11-18', 'jam': '08:00', 'dari': 'Tablet'}]
ATUR = uji_susut_harga.ATUR_DASAR + [{'id': 'struk', 'kop': {'nama': 'TOKO CONTOH', 'alamat': 'Jl. Contoh No. 1', 'telp': ''}}]

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T10:00:00+07:00'); var nId = 90000;
var W = { tanggal: '2026-11-18', jam: '10:00', kini: '2026-11-18T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'pesanan', 'karantina', 'persetujuan', 'cekGudang', 'kepatuhanCek'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-09-01T14:00:00.000Z' }, { id: 'jenisBeras', peta: { Kembang: 'IR42' } }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var iso = '2026-11-18';

// ==================== 1 · STOK MINUS (B49 · B50) ====================
var M = gdMinus(KINI); var MB = minusBuku(iso).daftar.filter(function (x) { return x.jenis === 'beras' || x.jenis === 'kemasan' || x.jenis === 'kantong'; });
ok('1: jumlah buku minus = minusBuku (gerbang tutup buku) jenis stok', M.n === MB.length && M.n === 14, J([M.n, MB.length, M.perJenis]));
ok('1: per jenis: beras 12 (Kembang + 10 Hantu + Hantu Kecil −0,5 kg: ambang −0,01 seperti minusBuku) · kemasan 1 · kantong 1', M.perJenis.beras === 12 && M.perJenis.kemasan === 1 && M.perJenis.kantong === 1, J(M.perJenis));
var kb = M.daftar[0];
ok('1: terdalam dulu: Kembang −50,6 kg × 12.000 = −607.200 di depan Hantu 10 (−49 kg = −588.000); rupiah = sisa × hppTerakhirPerKg', kb.nama === 'Kembang' && kb.dinilai && kb.rp === Math.round(kb.jumlah * kb.nilai) && kb.rp === -607200 && M.daftar[1].nama === 'Hantu 10' && M.daftar[1].rp === -588000, J(M.daftar.slice(0, 3)));
var dinilai = M.daftar.filter(function (x) { return x.dinilai; });
ok('1: urut rupiah terdalam; yang belum bisa dinilai (kantong tanpa harga beli) paling belakang', dinilai.every(function (x, i) { return !i || dinilai[i - 1].rp <= x.rp; }) && M.daftar[M.daftar.length - 1].jenis === 'kantong' && !M.daftar[M.daftar.length - 1].dinilai, J(M.daftar.map(function (x) { return [x.nama, x.rp]; })));
ok('1: 10 teratas + "lebih" = sisanya; Σ rupiah = jumlah baris', M.top.length === 10 && M.lebih === 4 && M.rp === M.daftar.reduce(function (a, x) { return a + x.rp; }, 0), J([M.top.length, M.lebih, M.rp]));
ok('1: kemasan & kantong minus ikut (dulu Dasbor hanya buku karung merek)', M.daftar.some(function (x) { return x.jenis === 'kemasan' && x.nama === 'Kemas Hantu 10 kg' && x.jumlah === -2 && x.rp === -120000; }) && M.daftar.some(function (x) { return x.jenis === 'kantong'; }), J(M.daftar.map(function (x) { return x.jenis + ':' + x.nama + ':' + x.rp; })));

// ==================== 2 · HILANG & RUSAK PER JENIS (B53) ====================
var BN = gdBuang('2026-11', KINI); var g = function (j) { return BN.jenis.find(function (x) { return x.jenis === j; }); };
ok('2: Σ rupiah hilang + lebih + kantong & bahan = "Susut & selisih stok" Laporan bulan itu (menutup)', BN.menutup === true && Math.abs(BN.rpSusut - BN.laporan) < 0.5, J([BN.rpSusut, BN.laporan, BN.kalimat]));
ok('2: per JENIS beras: Kembang → IR42 (setelan Jenis beras) · Angsa → IR64 (tebakan nama)', !!g('IR42') && !!g('IR64') && g('IR42').merek.indexOf('Kembang') >= 0, J(BN.jenis));
ok('2: retur rusak Angsa 10 kg masuk IR64 + taksiran modal > 0 + nasib karantina dibuang 10 kg', g('IR64').rusakKg === 10 && g('IR64').rusakRp > 0 && BN.nasib.dibuang === 10 && BN.total.nRusak === 1, J([g('IR64'), BN.nasib]));
['2026-09', '2026-10'].forEach(function (k) { var B = gdBuang(k, KINI); ok('2: ' + k + ' menutup ke Laporan', B.menutup === true, J([B.rpSusut, B.laporan])); });

// ==================== 3 · TUGAS GUDANG (B54) ====================
var T = gdTugas(KINI, W); var t = function (id) { return T.daftar.find(function (x) { return x.id === id; }); };
ok('3: dua belas jenis tugas tertulis (yang 0 tetap disebut; paket tanggal janji 27 Nov 2026: + lewat janji datang / antar; paket P3 27 Nov 2026: + nota "jual dulu, tandai")', T.daftar.length === 12 && T.daftar.some(function (x) { return x.id === 'janji'; }) && T.daftar.some(function (x) { return x.id === 'tembus'; }) && T.daftar.every(function (x) { return x.n !== null && x.tujuan; }), J(T.daftar.map(function (x) { return x.id + ':' + x.n; })));
ok('3: kabar barang masuk menunggu = 1 · buku minus = gdMinus', t('masuk').n === 1 && t('minus').n === M.n, J([t('masuk'), t('minus').n]));
ok('3: karantina = daftarKarantina apa adanya', t('karantina').n === daftarKarantina(W).antre.length, J(t('karantina')));
var SP = ssSumberPengingat(KINI, {}); var op = SP.find(function (p) { return p.jenis === 'opname'; }); var O = gdOpname(KINI);
ok('3: opname jatuh = sumber pengingat opname sistem-logika (satu sumber)', op && op.jatuh === O.jatuh && O.tiap === ssAtur('pengingat').opnameTiap, J([op, O]));
var CG = gdCekGudang(KINI); var SC = ssCekGudang(KINI);
ok('3: cek gudang = ssCekGudang (jatuh, sisa, teks)', CG.jatuh === SC.jatuh && CG.sisa === SC.sisa && CG.teks === SC.teks && t('cekGudang').n === (SC.sisa <= 0 ? 1 : 0), J([CG, SC.jatuh, SC.sisa]));
pasok('cekGudang', [{ id: 'cg-1', tanggal: '2026-11-17', jam: '08:00', cek: {}, catatan: '' }]); aturDengan([{ id: 'pengingat', gudangTiap: 3, opnameTiap: 2 }]);
var CG2 = gdCekGudang(KINI); var SC2 = ssCekGudang(KINI); var O2 = gdOpname(KINI); var op2 = ssSumberPengingat(KINI, {}).find(function (p) { return p.jenis === 'opname'; });
ok('3: setelan owner (tiap 3 / 2 hari) dibaca sama oleh gudang-logika & sistem-logika', CG2.jatuh === SC2.jatuh && CG2.jatuh === '2026-11-20' && O2.jatuh === op2.jatuh && O2.tiap === 2, J([CG2, SC2.jatuh, O2, op2.jatuh]));
pasok('cekGudang', []); aturDengan([]);
ok('3: pindah stok antar lokasi: satu lokasi → disebut tidak berlaku (bukan 0)', /tidak berlaku/.test(T.pindahLokasi), T.pindahLokasi);
ok('3: kemasan lewat ikut tugas (awas)', t('kemasan').n >= 1 && t('kemasan').awas === true, J(t('kemasan')));

// ==================== 4 · KEMASAN BERTANGGAL & UMUR SIMPAN (A62) ====================
ok('4: tambah bulan: 31 Agu + 6 = 28 Feb (bukan 3 Mar); 31 Agu 2027 + 6 = 29 Feb 2028', lbTambahBulan('2026-08-31', 6) === '2027-02-28' && lbTambahBulan('2027-08-31', 6) === '2028-02-29' && lbTambahBulan('2026-11-18', 12) === '2027-11-18');
var A0 = lbAtur(); ok('4: bawaan: umur simpan 6 bulan · tanda dekat 30 hari · cetak baik dipakai sebelum', A0.umurBulan === 6 && A0.ambangHari === 30 && A0.kedaluwarsa === true && !A0.dariOwner, J(A0));
var K = lbRingkasKemasan(KINI); var kc = K.daftar.find(function (x) { return x.namaProduk === 'Kemas Contoh'; });
ok('4: FIFO: 30 dibuat − 5 terjual = 25 tersisa → 10 (17 Nov) + 10 (1 Okt) + 5 (10 Mei) — yang terjual adukan TERLAMA', kc && kc.sisa === 25 && kc.lapisan.length === 3 && kc.tertua.tanggal === '2026-05-10' && kc.tertua.unit === 5, J(kc));
ok('4: 10 Mei + 6 bulan = 10 Nov < 18 Nov → LEWAT 8 hari, keluarkan dulu', kc.status === 'lewat' && kc.tertua.kedaluwarsa === '2026-11-10' && kc.tertua.sisaHari === -8 && K.lewat.length === 1, J(kc.tertua));
var kd = K.daftar.find(function (x) { return x.namaProduk === 'Kemas Dekat'; });
ok('4: 1 Nov + 6 bulan = 1 Mei → aman (> 30 hari)', kd && kd.status === 'aman', J(kd && kd.tertua));
ok('4: stok awal (beli jadi 8 Agu) = tanpa tanggal kemas, tidak diberi umur', K.tanpa.some(function (x) { return x.nama === 'Kemas Lama 5 kg' && x.sisa === 3; }) && !K.daftar.some(function (x) { return x.namaProduk === 'Kemas Lama'; }), J(K.tanpa));
var F = lbFifo([{ tanggal: 'a', unit: 3 }, { tanggal: 'b', unit: 4 }], 9);
ok('4: FIFO menutup: sisa melebihi semua adukan = tanpa tanggal', F.tersisa.length === 2 && F.tanpaUnit === 2 && F.tersisa.reduce(function (a, x) { return a + x.unit; }, 0) === 7, J(F));
aturDengan([{ id: 'catatStok', tempoHari: 21, modalFifoMulai: '', label: { umurBulan: 3, ambangHari: 30, kedaluwarsa: true, kelas: {} } }]);
var K3 = lbRingkasKemasan(KINI); var kd3 = K3.daftar.find(function (x) { return x.namaProduk === 'Kemas Dekat'; });
ok('4: umur simpan owner 3 bulan → 1 Nov + 3 = 1 Feb → 75 hari → aman; ambang 90 → dekat', kd3.status === 'aman', J(kd3.tertua));
aturDengan([{ id: 'catatStok', tempoHari: 21, modalFifoMulai: '', label: { umurBulan: 3, ambangHari: 90, kedaluwarsa: true, kelas: {} } }]);
ok('4: ...ambang 90 hari → DEKAT', lbRingkasKemasan(KINI).daftar.find(function (x) { return x.namaProduk === 'Kemas Dekat'; }).status === 'dekat');
var LS = lbSumberPengingat(KINI); ok('4: pengingat kemasan: satu per kemasan lewat / dekat, jatuh = baik dipakai sebelum, hari sebelum = tanda dekat', LS.length === 2 && LS.every(function (p) { return p.jenis === 'kemasan' && p.hariSebelum === 90; }), J(LS));
aturDengan([]);

// ==================== 5 · SETELAN LABEL (catatStok disalin utuh) ====================
var s1 = susunAturLabel({ umurBulan: '9', ambangHari: '', kelas: { 'Kemas Contoh|5': 'Medium' } }, W);
var d1 = s1.dokumen ? s1.dokumen[0].data : {};
ok('5: simpan label = SATU dokumen aturanToko/catatStok; kolom lain (tempo, modal FIFO) disalin utuh', !s1.tolak && s1.dokumen.length === 1 && d1.id === 'catatStok' && d1.tempoHari === 21 && d1.modalFifoMulai === '' && d1.label.umurBulan === 9 && d1.label.ambangHari === 30 && d1.label.kelas['Kemas Contoh|5'] === 'Medium', J(d1));
ok('5: mengubah umur simpan menyebut tanggal kemasan yang belum laku ikut bergeser', /bergeser/.test(s1.patch.kabar), s1.patch.kabar);
ok('5: umur pecahan / di luar 1–24 / kelas asing DITOLAK', !!susunAturLabel({ umurBulan: '6,5' }, W).tolak && !!susunAturLabel({ umurBulan: '25' }, W).tolak && !!susunAturLabel({ kelas: { x: 'Super' } }, W).tolak);
aturDengan([{ id: 'catatStok', tempoHari: 21, label: { umurBulan: 6, ambangHari: 30, kedaluwarsa: true, kelas: { 'Kemas Contoh|5': 'Medium' } } }]);
var s2 = susunAturLabel({ kelas: { 'Kemas Contoh|5': '' } }, W);
ok('5: kelas dikosongkan = dihapus dari peta', !s2.tolak && !('Kemas Contoh|5' in s2.dokumen[0].data.label.kelas), J(s2.dokumen[0].data.label));

// ==================== 6 · ISI LABEL (A49 · A78) ====================
var I = lbIsiKemasan({ kunci: 'Kemas Contoh|5', nama: 'Kemas Contoh 5 kg' }, 'MIQ:B:ABCDEFGH', { tanggal: '2026-11-17' }, lbAtur(), lbKop(), 'ABCDEFGH');
ok('6: label kemasan LENGKAP: kelas mutu · berat bersih · dikemas · baik dipakai sebelum (+6 bulan) · alamat toko, nama toko di ket, QR', J(I.baris) === J(['Kelas mutu: Medium', 'Berat bersih: 5 kg', 'Dikemas: 17 Nov 2026', 'Baik dipakai sebelum: 17 Mei 2027', 'Jl. Contoh No. 1']) && I.ket === 'TOKO CONTOH' && I.kode === 'MIQ:B:ABCDEFGH' && !I.kurang.length, J(I));
aturDengan([{ id: 'struk', kop: { nama: 'TOKO CONTOH', alamat: '' } }]);
var I2 = lbIsiKemasan({ kunci: 'Kemas Dekat|10', nama: 'Kemas Dekat 10 kg' }, 'k', { tanggal: '' }, lbAtur(), lbKop(), 'k');
ok('6: tanpa kelas / alamat / tanggal = barisnya tidak dicetak & DISEBUT (kurang)', I2.kurang.length === 3 && I2.baris.length === 1 && I2.baris[0] === 'Berat bersih: 10 kg', J(I2));
aturDengan([{ id: 'catatStok', tempoHari: 21, label: { umurBulan: 6, ambangHari: 30, kedaluwarsa: false, kelas: {} } }]);
ok('6: "baik dipakai sebelum" dimatikan owner = tidak dicetak, tanggal kemas tetap', !lbIsiKemasan({ kunci: 'x|5', nama: 'x' }, 'k', { tanggal: '2026-11-17' }, lbAtur(), lbKop(), 'k').baris.some(function (b) { return /Baik dipakai/.test(b); }));
aturDengan([]);
var BK = lbBarisKedatangan({ merkList: [{ merk: 'Angsa', jumlahKarung: 20, beratKarung: 50, totalKg: 990, kgTerima: 990 }, { merk: 'Kembang', jumlahKarung: 8, beratKarung: 50, totalKg: 400 }, { merk: 'Bal', bentuk: 'bal', jumlahKarung: 2 }] });
ok('6: baris kedatangan: berat asli per karung dari timbang (990 ÷ 20 = 49,5), belum ditimbang = nota; bal tidak berlabel tumpukan', BK.length === 2 && BK[0].kgKarung === 49.5 && BK[0].ikutTimbang && BK[1].kgKarung === 50 && !BK[1].ikutTimbang, J(BK));
var IT = lbIsiTumpukan('Angsa', '2026-09-02', BK[0], lbKop());
ok('6: label tanggal masuk: merek, masuk, berat asli, jumlah karung, FIFO — tanpa QR', J(IT.baris) === J(['Masuk: 2 Sep 2026', 'Berat asli ±49,5 kg/karung', '20 karung datang', 'Keluarkan yang lebih lama dulu']) && IT.kode === '' && IT.judul === 'Angsa', J(IT));
var KM = lbKedatanganMerek('Angsa', 4);
ok('6: cetak ulang dari Jual: kedatangan Angsa terbaru dulu (2 Okt, 2 Sep)', KM.length === 2 && KM[0].tanggal === '2026-10-02' && KM[1].tanggal === '2026-09-02', J(KM.map(function (x) { return x.tanggal; })));
var PK = lbPilihanKemas('Kemas Contoh|5', KINI);
ok('6: pilihan tanggal kemas = adukan yang masih tersisa, terbaru dulu (bawaan label = adukan terbaru)', PK.length === 3 && PK[0].tanggal === '2026-11-17' && PK[2].tanggal === '2026-05-10' && PK[2].status === 'lewat', J(PK));

// ==================== 7 · ESC/POS & TSPL ====================
var isiLama = { judul: 'Kemas Contoh 5 kg', ket: 'TOKO CONTOH', kode: 'MIQ:B:ABCDEFGH', teksKode: 'ABCDEFGH' };
var isiBaru = Object.assign({}, isiLama, { baris: I.baris });
var e1 = epSusunLabel(isiBaru, { kertas: 80, potong: 'penuh', umpan: 2, jumlah: 1 });
ok('7: ESC/POS dengan baris: kelima baris tercetak di antara nama toko & QR', I.baris.every(function (b) { return e1.teks.some(function (t) { return t.indexOf(b.slice(0, 20)) >= 0; }); }) && e1.teks.indexOf('[QR MIQ:B:ABCDEFGH]') > e1.teks.indexOf('TOKO CONTOH'), J(e1.teks));
var t30 = epTsplLabel(isiBaru, { lebarMm: 50, tinggiMm: 30, celahMm: 2, jumlah: 1 }); var t60 = epTsplLabel(isiBaru, { lebarMm: 50, tinggiMm: 60, celahMm: 2, jumlah: 1 });
var nTeks = function (x) { return x.teks.filter(function (s) { return /^TEXT /.test(s); }).length; };
ok('7: TSPL: baris kecil di kanan QR, berhenti sebelum tepi bawah (30 mm memuat lebih sedikit dari 60 mm)', nTeks(t60) > nTeks(t30) && t60.teks.some(function (s) { return /Baik dipakai sebelum/.test(s) || /Baik dipakai/.test(s); }), J([nTeks(t30), nTeks(t60)]));
var tq = epTsplLabel({ judul: 'Angsa', ket: 'TOKO CONTOH', kode: '', teksKode: '', baris: IT.baris }, { lebarMm: 50, tinggiMm: 40, jumlah: 1 });
ok('7: TSPL tanpa QR: nama toko & baris dari tepi kiri, tanpa QRCODE, nama toko sekali', !tq.teks.some(function (s) { return /^QRCODE/.test(s); }) && tq.teks.filter(function (s) { return /TOKO CONTOH/.test(s); }).length === 1 && tq.teks.some(function (s) { return /Masuk: 2 Sep 2026/.test(s); }), J(tq.teks));
var OUT_EP = { s: Array.prototype.slice.call(epSusunLabel(isiLama, { kertas: 80, potong: 'penuh', umpan: 2, jumlah: 2 }).byte), t: epTsplLabel(isiLama, { lebarMm: 50, tinggiMm: 30, jumlah: 3, potong: true }).teks,
  s58: Array.prototype.slice.call(epSusunLabel(Object.assign({}, isiLama, { baris: [] }), { kertas: 58 }).byte) };

// ==================== 8 · KALENDER KEPATUHAN (A16 · A38 · A45) ====================
var tidak = function () { return false; };
var b = function (o) { return Object.assign({ id: 'x', ulang: 'bulanan', tanggal: '01', hariSebelum: 0 }, o); };
var P1 = ptPutaran(b({}), '2026-11-25', tidak, '');
ok('8: bulanan sebelum kalender lahir (1 Nov < 26 Nov) tidak ditagih → 1 Des, putaran 2026-12', P1.jatuh === '2026-12-01' && P1.periode === '2026-12' && P1.sisa === 6, J(P1));
var P2 = ptPutaran(b({}), '2026-12-03', tidak, '');
ok('8: 3 Des belum ditandai → LEWAT 2 hari (putaran 1 Des)', P2.jatuh === '2026-12-01' && P2.sisa === -2, J(P2));
var P3 = ptPutaran(b({}), '2026-12-03', function (p) { return p === '2026-12'; }, '');
ok('8: sudah ditandai → putaran berikutnya 1 Jan 2027', P3.jatuh === '2027-01-01' && P3.periode === '2027-01', J(P3));
var P4 = ptPutaran(b({}), '2027-01-05', tidak, '');
ok('8: bulan lalu terlewat tidak menumpuk: 5 Jan → putaran 1 Jan (lewat 4 hari), bukan Des', P4.jatuh === '2027-01-01' && P4.sisa === -4, J(P4));
var spt = { id: 'spt', ulang: 'tahunan', tanggal: '', hariSebelum: 30 };
ok('8: SPT tanpa tanggal: orang pribadi 31 Mar 2027 · badan 30 Apr 2027 (SPT 2025 sebelum kalender tidak ditagih)', ptPutaran(spt, '2026-11-25', tidak, 'op').jatuh === '2027-03-31' && ptPutaran(spt, '2026-11-25', tidak, 'badan').jatuh === '2027-04-30' && ptPutaran(spt, '2026-11-25', tidak, 'op').periode === '2027');
ok('8: SPT 2027 ditandai Feb → berikutnya 31 Mar 2028', ptPutaran(spt, '2027-02-10', function (p) { return p === '2027'; }, '').jatuh === '2028-03-31');
ok('8: tiap 3 bulan: Jan/Apr/Jul/Okt → 1 Jan 2027 (K1)', ptPutaran(b({ ulang: 'triwulan' }), '2026-11-25', tidak, '').periode === '2027-K1' && ptPutaran(b({ ulang: 'triwulan' }), '2027-02-01', tidak, '').jatuh === '2027-01-01');
ok('8: tanggal 31 di bulan pendek & 29 Feb di tahun biasa dijepit ke akhir bulan', ptPutaran(b({ tanggal: '31' }), '2027-02-10', function (p) { return p === '2027-01'; }, '').jatuh === '2027-02-28' && ptPutaran(b({ tanggal: '31' }), '2027-02-10', tidak, '').jatuh === '2027-01-31' && ptPutaran(b({ ulang: 'tahunan', tanggal: '02-29' }), '2027-01-01', tidak, '').jatuh === '2027-02-28');
var PS = ptPutaran(b({ ulang: 'sekali', tanggal: '2027-02-10' }), '2026-11-25', tidak, ''); var PS2 = ptPutaran(b({ ulang: 'sekali', tanggal: '2027-02-10' }), '2026-11-25', function (p) { return p === '2027-02-10'; }, '');
ok('8: sekali: jatuh tanggal itu; sudah ditandai = selesai', PS.jatuh === '2027-02-10' && PS.sisa === 77 && PS2.selesai === true, J([PS, PS2]));
ok('8: tanggal kosong = tanpa tanggal (tidak mengingatkan)', ptPutaran(b({ ulang: 'sekali', tanggal: '' }), '2026-11-25', tidak, '').tanpaTanggal === true);
ok('8: bentuk tanggal dijaga (bulanan 01–31, tahunan BB-HH, sekali TTTT-BB-HH)', ptTanggalSah('bulanan', '15') && !ptTanggalSah('bulanan', '32') && ptTanggalSah('tahunan', '03-31') && !ptTanggalSah('tahunan', '02-30') && ptTanggalSah('sekali', '2027-02-28') && !ptTanggalSah('sekali', '2027-02-30'));
var KAL = ptKalender(new Date('2026-11-25T10:00:00+07:00'));
ok('8: kalender bawaan: 9 butir, SPT 31 Mar 2027, tiga cek aturan 1 Des, izin/tera/THR tanpa tanggal, label 1 Jan, tutup buku 31 Des', KAL.baris.length === 9 && KAL.baris.find(function (x) { return x.id === 'spt'; }).jatuh === '2027-03-31' && KAL.aturan.length === 3 && KAL.baris.filter(function (x) { return x.tanpaTanggal; }).length === 3 && KAL.baris.find(function (x) { return x.id === 'tutup'; }).jatuh === '2026-12-31', J(KAL.baris.map(function (x) { return x.id + ':' + (x.jatuh || '-'); })));
ok('8: hari pertama: cek aturan yang belum pernah jatuh TIDAK langsung kuning', KAL.aturanBasi.length === 0, J(KAL.aturanBasi));
var KAL2 = ptKalender(new Date('2026-12-03T10:00:00+07:00'));
ok('8: 3 Des tanpa tanda: tiga cek aturan LEWAT + kuning; urusan disebut', KAL2.aturanBasi.length === 3 && KAL2.perlu.filter(function (x) { return x.keadaan === 'lewat'; }).length === 3, J(KAL2.perlu.map(function (x) { return x.id + ':' + x.keadaan; })));
var W2 = { tanggal: '2026-12-03', jam: '09:00', kini: '2026-12-03T02:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var C0 = susunCentangPatuh('cek-het', '', '', W2, new Date('2026-12-03T10:00:00+07:00'));
ok('8: lewat tanpa catatan DITOLAK (tulis kapan / bukti)', !!C0.tolak, J(C0));
var C1 = susunCentangPatuh('cek-het', '', 'HET tetap', W2, new Date('2026-12-03T10:00:00+07:00')); var dC = C1.dokumen ? C1.dokumen[0].data : {};
ok('8: tanda = SATU kepatuhanCek { id, tanggal, jam, butir, periode, catatan } — kolom = PT_CEK_KOLOM', !C1.tolak && C1.dokumen.length === 1 && C1.dokumen[0].koleksi === 'kepatuhanCek' && dC.butir === 'cek-het' && dC.periode === '2026-12' && J(Object.keys(dC).sort()) === J(PT_CEK_KOLOM.slice().sort()), J(C1));
ok('8: bentuk tanda = rules v22 (akses.js cekPatuhSah); kolom asing / butir huruf besar ditolak', cekPatuhSah(dC) && !cekPatuhSah(Object.assign({}, dC, { nominal: 1 })) && !cekPatuhSah(Object.assign({}, dC, { butir: 'Cek HET' })) && !cekPatuhSah(Object.assign({}, dC, { catatan: new Array(162).join('x') })), J(dC));
pasok('kepatuhanCek', [Object.assign({}, dC, { oleh: 'Ben Contoh' })]);
var KAL3 = ptKalender(new Date('2026-12-03T10:00:00+07:00')); var het = KAL3.baris.find(function (x) { return x.id === 'cek-het'; });
ok('8: sesudah ditandai: berikutnya 1 Jan, terakhir oleh Penjaga laci, tidak kuning; tanda putaran yang sama ditolak', het.jatuh === '2027-01-01' && het.akhir.oleh === 'Ben Contoh' && !het.basi && !!susunCentangPatuh('cek-het', '2026-12', 'x', W2, new Date('2026-12-03T10:00:00+07:00')).tolak, J(het));
pasok('kepatuhanCek', []);
var AP = susunAturPatuh({ butir: ptAtur().butir.concat([{ nama: 'Perpanjang izin edar', ulang: 'sekali', tanggal: '2027-06-30', hariSebelum: '60', ket: 'contoh' }]), usaha: { bentuk: 'cv', catat: 'pembukuan', konfirmasi: { tanggal: '2026-11-20', ke: 'KPP Contoh', catatan: '' } } }, W);
var dA = AP.dokumen ? AP.dokumen[0].data : {};
ok('8: Atur kalender = SATU dokumen aturanToko/kepatuhan; butir baru diberi id & mulai; bentuk usaha tersimpan', !AP.tolak && dA.id === 'kepatuhan' && dA.butir.length === 10 && /^b[0-9a-z]+$/.test(dA.butir[9].id) && dA.butir[9].mulai === '2026-11-18' && dA.usaha.bentuk === 'cv', J(dA.butir[9]));
ok('8: Atur menolak nama kosong, tanggal salah bentuk, ingatkan > 120 hari', !!susunAturPatuh({ butir: [{ nama: '', ulang: 'sekali' }] }, W).tolak && !!susunAturPatuh({ butir: [{ nama: 'x', ulang: 'tahunan', tanggal: '2027-03-31' }] }, W).tolak && !!susunAturPatuh({ butir: [{ nama: 'x', ulang: 'sekali', hariSebelum: '121' }] }, W).tolak);
aturDengan([dA]);
var KAL4 = ptKalender(new Date('2026-11-25T10:00:00+07:00'));
ok('8: bentuk usaha CV (badan) → SPT 30 Apr; butir izin baru 30 Jun 2027 (sekali)', KAL4.baris.find(function (x) { return x.id === 'spt'; }).jatuh === '2027-04-30' && KAL4.baris[9].jatuh === '2027-06-30' && KAL4.usaha.wp === 'badan', J(KAL4.usaha));
ok('8: bentuk usaha vs profil pajak: badan ≠ orang pribadi DISEBUT; PKP = PPN belum dicatat DISEBUT', ptCocokPajak(KAL4.usaha, 'orangPribadi', 'pkp').length === 2 && ptCocokPajak(KAL4.usaha, 'badan', 'bukan').length === 0, J(ptCocokPajak(KAL4.usaha, 'orangPribadi', 'pkp')));
aturDengan([]);

// ==================== 9 · PENGINGAT & LONCENG ("pasang notifikasi") ====================
ok('9: tiga jenis pengingat baru terdaftar', ['patuh', 'kemasan', 'minus'].every(function (j) { return SS_JENIS_PENGINGAT.some(function (x) { return x.id === j; }); }));
var lp = { patuh: [{ id: 'patuh|spt|2027', jenis: 'patuh', kunci: 'spt', teks: 'Lapor SPT Tahunan', jatuh: '2026-12-08', hariSebelum: 30, n: 0, ket: '' }], gudang: gdSumberPengingat(KINI).concat(lbSumberPengingat(KINI)) };
var G = ssPengingat(KINI, lp); var ada = function (id) { return G.aktif.some(function (p) { return p.id === id; }); };
ok('9: kalender 20 hari lagi + hari sebelum PER BUTIR 30 → aktif (angka Atur pengingat 0 tidak menutupnya)', ada('patuh|spt|2027') && G.aktif.find(function (p) { return p.id === 'patuh|spt|2027'; }).hariSebelum === 30, J(G.aktif.map(function (p) { return p.id; })));
ok('9: buku minus & kemasan lewat jadi pengingat hari ini / lewat', G.aktif.some(function (p) { return p.jenis === 'minus' && p.sisa === 0; }) && G.aktif.some(function (p) { return p.jenis === 'kemasan' && p.sisa < 0; }), J(G.aktif.map(function (p) { return p.jenis + ':' + p.sisa; })));
ok('9: Atur pengingat: hari kalender > 60 ditolak', !!susunAturSistem('pengingat', Object.assign({}, ssAtur('pengingat'), { hariPatuh: 61 }), W).tolak);
var jatuh = G.aktif.filter(function (p) { return ['patuh', 'kemasan', 'minus'].indexOf(p.jenis) >= 0 && p.sisa <= 0; }).map(function (p) { return { id: p.id, jenis: p.jenis, teks: p.teks, ket: p.ket, sisaTeks: p.sisaTeks, jatuh: p.jatuhEfektif }; });
var akO = { jenis: 'owner', uid: 'uid-owner', nama: 'Owner' };
var L1 = kbLonceng(akO, [], {}, iso, jatuh);
ok('9: lonceng: pengingat jatuh = kabar baru (pg|…), dibuka = sudah dilihat', L1.n === jatuh.length && jatuh.length >= 2 && L1.daftar.every(function (x) { return x.tindakan === 'pengingat' && x.baru && /^pg\|/.test(x.id) && x.layar === 'pengingat'; }), J(L1.daftar));
var L2 = kbLonceng(akO, [], kbTandai(L1), iso, jatuh); ok('9: sesudah dibuka angka nol', L2.n === 0, J(L2.n));
ok('9: tanpa pengingat lonceng sama dengan dulu', kbLonceng(akO, [], {}, iso).n === 0);

// ==================== 10 · AKSES STAF (rules v22) ====================
var akB = keadaanAkun('ben.contoh@contoh.com', 'uid-ben', { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben', aktif: true }); var akK = keadaanAkun('kry@contoh.com', 'uid-kry', { uid: 'uid-kry', nama: 'Karyawan', peran: 'karyawan', aktif: true });
var HL = {}; Object.keys(SERVER_BUKA).forEach(function (t) { HL[t] = 'sendiri'; });
var DK = [{ koleksi: 'kepatuhanCek', data: Object.assign({}, dC, { olehUid: 'uid-ben' }), ada: false, lama: null }];
ok('10: Penjaga laci boleh mengirim tanda kalender; karyawan ditolak perangkat', !periksaKiriman(akB, DK, [], HL).tolak && !!periksaKiriman(akK, DK, [], HL).tolak, J([periksaKiriman(akB, DK, [], HL), periksaKiriman(akK, DK, [], HL)]));
var DKx = [{ koleksi: 'kepatuhanCek', data: Object.assign({}, dC, { nominal: 5 }), ada: false, lama: null }];
ok('10: bentuk di luar rules v22 tidak dikirim', !!periksaKiriman(akB, DKx, [], HL).tolak);
var PB = pendengarPeran(akB), PKy = pendengarPeran(akK); var dok = function (P) { return (P.find(function (x) { return x.nama === 'aturanToko'; }) || {}).dok || []; };
ok('10: pendengar Penjaga laci: + kepatuhanCek & aturanToko/kepatuhan; karyawan tidak', PB.some(function (x) { return x.nama === 'kepatuhanCek'; }) && dok(PB).indexOf('kepatuhan') >= 0 && !PKy.some(function (x) { return x.nama === 'kepatuhanCek'; }) && dok(PKy).indexOf('kepatuhan') < 0, J([dok(PB), dok(PKy)]));

// ==================== 11 · DASBOR APA ADANYA ====================
var DS = dbStok(KINI); var DQ = dbMutu(KINI);
ok('11: dbStok.gudang = gdDasbor (buku minus, tugas, kemasan, hilang) tanpa galat', DS.gudang && !DS.gudang.galat && DS.gudang.minus.n === M.n && DS.gudang.tugas.n === gdTugas(KINI).n && DS.gudang.kemasan.lewat === 1 && DS.gudang.buang.menutup === true, J(DS.gudang && DS.gudang.minus));
ok('11: dbMutu.patuh = ptDasbor tanpa galat', DQ.patuh && !DQ.patuh.galat && DQ.patuh.n === ptDasbor(KINI).n, J(DQ.patuh));

// ==================== 12 · PUSH PAGI SERVER = RUMUS YANG SAMA ====================
var BUTIR = PT_BAWAAN.concat([{ id: 'a1', ulang: 'sekali', tanggal: '2027-02-10' }, { id: 'a2', ulang: 'triwulan', tanggal: '31' }, { id: 'a3', ulang: 'tahunan', tanggal: '02-29' }, { id: 'a4', ulang: 'bulanan', tanggal: '15', mulai: '2026-10-01' }]);
var beda = [], nBanding = 0; var d0 = new Date('2026-11-01T00:00:00Z');
for (var i = 0; i < 560; i += 3) { var t2 = new Date(d0.getTime() + i * 86400000).toISOString().slice(0, 10);
  BUTIR.forEach(function (bb) { ['', 'op', 'badan'].forEach(function (wp) { [function () { return false; }, function (p) { return p === t2.slice(0, 7) || p === t2.slice(0, 4); }].forEach(function (sd) {
    nBanding += 1; var a = ptPutaran(bb, t2, sd, wp), c = FPX.putaran(bb, t2, sd, wp); if (J(a) !== J(c)) beda.push(t2 + ' ' + bb.id + ' ' + wp + ': ' + J(a) + ' ≠ ' + J(c)); }); }); }); }
ok('12: functions/patuh.js putaran = patuh-logika ptPutaran di ' + nBanding + ' perbandingan (tanggal × butir × bentuk usaha × tanda)', !beda.length && nBanding > 1000, beda.slice(0, 3).join(' | '));
ok('12: butir bawaan server = PT_BAWAAN (id, nama, ulang, tanggal, hari sebelum)', J(FPX.BUTIR_BAWAAN.map(function (x) { return [x.id, x.nama, x.ulang, x.tanggal, x.hariSebelum]; })) === J(PT_BAWAAN.map(function (x) { return [x.id, x.nama, x.ulang, x.tanggal, x.hariSebelum]; })) && FPX.PT_MULAI === PT_MULAI);
var BERES = [{ butir: 'tutup', periode: '2026' }, { butir: 'label', periode: '2027-K1' }].concat(['cek-het', 'cek-qris', 'cek-pajak'].map(function (x) { return { butir: x, periode: '2027-03' }; }));
var Q1 = FPX.pesanPatuh(null, BERES, '2027-03-01', 1), Q2 = FPX.pesanPatuh(null, BERES, '2027-03-02', 2);
ok('12: push: SPT tepat H-30 DIKIRIM; H-29 tidak (masih di jendela, tidak cerewet)', Q1.kirim && Q1.n === 1 && Q1.daftar[0].id === 'spt' && /Lapor SPT Tahunan 30 hari lagi/.test(Q1.isi) && !Q2.kirim && Q2.n === 1, J([Q1, Q2]));
var Q3 = FPX.pesanPatuh(null, [], '2026-12-07', 1), Q4 = FPX.pesanPatuh(null, [], '2026-12-08', 2);
ok('12: push: cek aturan lewat dikirim hari SENIN saja', Q3.kirim && Q3.daftar.length === 3 && Q3.daftar.every(function (x) { return x.sisa === -6; }) && !Q4.kirim, J([Q3.isi, Q4.kirim]));
var Q5 = FPX.pesanPatuh(null, [{ butir: 'cek-het', periode: '2026-12' }, { butir: 'cek-qris', periode: '2026-12' }, { butir: 'cek-pajak', periode: '2026-12' }], '2026-12-07', 1);
ok('12: push: yang sudah ditandai (kepatuhanCek) tidak dikirim', !Q5.kirim && Q5.n === 0, J(Q5));
var Q6 = FPX.pesanPatuh({ butir: [{ id: 'spt', nama: 'Lapor SPT', ulang: 'tahunan', tanggal: '', hariSebelum: 30, nyala: false }] }, [], '2027-03-01', 1);
ok('12: push: butir yang dimatikan owner tidak dikirim', !Q6.kirim && Q6.n === 0);
var HW = FPX.hariWib(new Date('2026-11-30T23:30:00Z')); ok('12: hari WIB: 30 Nov 23.30 UTC = 1 Des (Selasa) 06.30 WIB', HW.iso === '2026-12-01' && HW.hari === 2, J(HW));

print(JSON.stringify({ lulus: lulus, gagal: gagal, ep: OUT_EP }));
"""

EP_LAMA = r"""
var isiLama = { judul: 'Kemas Contoh 5 kg', ket: 'TOKO CONTOH', kode: 'MIQ:B:ABCDEFGH', teksKode: 'ABCDEFGH' };
print(JSON.stringify({ s: Array.prototype.slice.call(epSusunLabel(isiLama, { kertas: 80, potong: 'penuh', umpan: 2, jumlah: 2 }).byte), t: epTsplLabel(isiLama, { lebarMm: 50, tinggiMm: 30, jumlah: 3, potong: true }).teks,
  s58: Array.prototype.slice.call(epSusunLabel(isiLama, { kertas: 58 }).byte) }));
"""

STATIS = [
    ('Stok: tab Tugas gudang terdaftar & tergambar', 'stok', ["import * as GD from './gudang-logika.js';", "s.tab === 'tugas' ? gambarTugas(s)", 'function gambarTugas(s)', 'GD.gdTugas(kini(), waktu())', 'GD.gdMinus(kini())', 'LB.lbRingkasKemasan(kini())', 'data-aksi="gdKe"']),
    ('Stok: label sesudah Barang masuk & adukan', 'stok', ["${s.tbm ? kartuLabelMasuk(s.tbm.id, s) : ''}", "${buka ? kartuLabelAdukan(buka.batch, s) : ''}", 'aksiPanelLabel({ set, st, waktu, tulisDokumen })']),
    ('Jual › Label: label lengkap, tanggal masuk, Atur label', 'jual', ["import * as LB from './label-logika.js';", 'LB.lbIsiKemasan(sasaran, kode, { tanggal: tg }', 'LB.lbIsiTumpukan(String(t.kunci), KD.tanggal, KD.baris)', 'function gambarAturLabel(s)', 'LB.susunAturLabel(a, tkWaktu())', '${gambarAturLabel(s)}']),
    ('Laporan › Pajak: kalender kepatuhan', 'laporan', ["import { kartuKalender, aksiPanelPatuh } from './patuh-panel.js';", 'const kalender = kartuKalender(s, kini(), P.jenisWp, P.statusPkp);', 'aksiPanelPatuh({ set, st, tulis, waktu, kini })']),
    ('Menu › Pengingat: tanda kalender (owner & Penjaga laci)', 'menu', ["p && p.jenis === 'patuh' ? kartuCentang(", 'aksiPanelPatuh({ set, st, tulis, waktu, kini })']),
    ('Dasbor: baris gudang & kalender', 'dasbor', ['+ barisGudang(S.gudang) +', 'function barisGudang(G)', "baris('patuh', 'Kalender kepatuhan'"]),
    ('dasbor-logika memanggil gudang & patuh apa adanya', 'dl', ["import { gdDasbor } from './gudang-logika.js';", 'gudang: dbCoba(() => gdDasbor(kini))', 'patuh: aman(() => ptDasbor(kini))']),
    ('app.js: sumber pengingat & lonceng', 'app', ['patuh: sumberPatuh(), gudang: sumberGudang() })', 'function pengingatLonceng(a)', "loncengPengingat({ ambil: (a) => pengingatLonceng(a), buka: () => { pindah('menu'); menu.buka('pengingat'); } });", "const LC_JENIS = ['patuh', 'kemasan', 'minus'];"]),
    ('lonceng meneruskan pengingat', 'lonceng', ['kbLonceng(_lcAkun, null, L, lcWaktu().tanggal, lcPengingat())']),
    ('push pagi server terpasang', 'fi', ["const { pesanPatuh, hariWib } = require('./patuh');", "exports.kabarPatuh = onSchedule({ schedule: 'every day 07:00', timeZone: 'Asia/Jakarta'", "collection('aksesAkun').where('peran', '==', 'ben').where('aktif', '==', true)"]),
    ('koleksi kepatuhanCek terdaftar', 'koleksi', ["{ nama: 'kepatuhanCek',        urut: 'id',    cache: 'kepatuhanCek', kelas: 'tetap' },"]),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/gudang-logika.js">', '<link rel="modulepreload" href="js/layar/label-logika.js">', '<link rel="modulepreload" href="js/layar/patuh-logika.js">', '<link rel="modulepreload" href="js/layar/label-panel.js">', '<link rel="modulepreload" href="js/layar/patuh-panel.js">']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_gudang_label_patuh.py && python3 alat-uji/uji_gudang_label_patuh.py --kontrol']),
    ('bundel uji melengkapi modul untuk Dasbor', 'bundel', ["GD_PEMAKAI = ('dasbor-logika.js', 'gudang-logika.js')"]),
    ('riwayat setelan menamai dokumen baru', 'rs', ["kepatuhan: 'Kalender kepatuhan'"]),
    ('gerak: tugas, label, kalender bergerak + hormat reduced motion', 'cssS', ['lbpMasuk', '@media (prefers-reduced-motion: reduce) { .layar-stok .lbp-baris { animation: none; } }']),
    ('gerak Laporan & Menu & Jual', 'cssL', ['ptMasuk', 'ptPegas', '.layar-laporan .pt-baris, .layar-laporan .pt-centang, .layar-laporan .pt-atur { animation: none; }']),
    ('gerak Menu', 'cssM', ['ptCentangPegas', '.pt-centang { animation: none; }']),
    ('gerak Jual', 'cssJ', ['lbAturPegas', '.lb-atur { animation: none; }']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Paket Stok minus, label & kepatuhan', 'uji_gudang_label_patuh.py', 'rules v22']),
    ('modul logika tanpa DOM', 'gd', []),
]

RUSAK = [
    ('minus: ambang beras beda dari minusBuku', GD, "const s = K[m].sisaKg; if (!(s <= -0.01)) return;", "const s = K[m].sisaKg; if (!(s <= -1)) return;"),
    ('minus: kantong tidak ikut', GD, "    d.push({ jenis: 'kantong', kunci: j,", "    if (false) d.push({ jenis: 'kantong', kunci: j,"),
    ('minus: rupiah dari harga beli terbaru (bukan nilai neraca)', GD, "const v = Number(K[m].hppTerakhirPerKg) || 0;", "const v = Number(K[m].hargaTerakhirPerKg || K[m].hppTerakhirPerKg) * 2 || 0;"),
    ('minus: urut terbalik (yang paling dalam di belakang)', GD, "(a.dinilai ? a.rp - b.rp : a.jumlah - b.jumlah)", "(a.dinilai ? b.rp - a.rp : b.jumlah - a.jumlah)"),
    ('buang: kantong & bahan lupa (tidak menutup)', GD, "luar.forEach((x) => { bahan.hilangRp += Number(x.susutRp) || 0; bahan.naikRp += Number(x.naikRp) || 0; });", "luar.forEach((x) => { bahan.hilangRp += 0; });"),
    ('buang: rusak tanpa jenis (semua ke satu kelompok)', GD, "const G = g(gdJenis(nama)); let rp = 0;", "const G = g('Lain'); let rp = 0;"),
    ('tugas: opname tiap angka tetap 30', GD, "const jatuh = akhir ? gdTambahHari(akhir, Number(A.opnameTiap) || 14) : iso;", "const jatuh = akhir ? gdTambahHari(akhir, 30) : iso;"),
    ('tugas: cek gudang tidak membaca setelan owner', GD, "const tiap = gdAturPengingat().gudangTiap;", "const tiap = 7;"),
    ('kemasan: yang terjual = adukan TERBARU (bukan terlama)', LB, "for (let i = lapisan.length - 1; i >= 0 && s > 0; i--) { const L = lapisan[i];", "for (let i = 0; i < lapisan.length && s > 0; i++) { const L = lapisan[i];"),
    ('kemasan: stok awal diberi umur (tanggal entri dianggap tanggal kemas)', LB, "tanpaTanggal: !p.tanggal || !!p.stokAwal || !!p.beliJadi }))", "tanpaTanggal: !p.tanggal }))"),
    ('kemasan: tambah bulan meluber ke bulan berikut (31 Agu + 6 = 3 Mar)', LB, "return Y + '-' + String(M + 1).padStart(2, '0') + '-' + String(Math.min(d, akhir)).padStart(2, '0');", "return new Date(Date.UTC(Y, M, d)).toISOString().slice(0, 10);"),
    ('kemasan: dekat memakai < (sama dengan ambang dianggap aman)', LB, "status: sisaHari < 0 ? 'lewat' : sisaHari <= A.ambangHari ? 'dekat' : 'aman'", "status: sisaHari < 0 ? 'lewat' : sisaHari < A.ambangHari - 60 ? 'dekat' : 'aman'"),
    ('label: setelan menimpa catatStok (tempo & modal FIFO hilang)', LB, "data: Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, label })", "data: { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, label }"),
    ('label: kelas tidak dicetak', LB, "  if (kelas) baris.push('Kelas mutu: ' + kelas); else kurang.push('kelas mutu (Atur label)');", "  kurang.push('kelas mutu (Atur label)');"),
    ('label: alamat kosong tidak disebut', LB, "if (K.alamat) baris.push(K.alamat); else kurang.push('alamat toko (Laporan › Identitas usaha)');", "if (K.alamat) baris.push(K.alamat);"),
    ('label: berat asli dari nota (timbang diabaikan)', LB, "const kg = m.kgTerima !== undefined && m.kgTerima !== null && Number(m.kgTerima) > 0 ? Number(m.kgTerima) : Number(m.totalKg) || n * (Number(m.beratKarung) || 50);", "const kg = n * (Number(m.beratKarung) || 50);"),
    ('ESC/POS: baris tambahan tidak dicetak', EP, "    tambah.forEach((s) => { w.baris(s); if (!i) teks.push(s); });", ""),
    ('ESC/POS: label lama berubah (baris kosong selalu dicetak)', EP, "  const tambah = epBarisLabel(x.baris, lebar, EP_LABEL_BARIS);", "  const tambah = epBarisLabel(x.baris, lebar, EP_LABEL_BARIS).concat(['']);"),
    ('TSPL: baris menembus tepi bawah label', EP, "if (yb + 12 > tg * 8 - 8) return;", "if (yb > 99999) return;"),
    ('TSPL: tanpa QR nama toko tercetak dua kali', EP, "if (x.ket && xTeks + 8 * 8 <= W && !tanpaQrBaris)", "if (x.ket && xTeks + 8 * 8 <= W)"),
    ('kalender: putaran sebelum kalender lahir ditagih', PT, "if (lalu >= mulai && !sudah(ptPeriode(b.ulang, lalu)))", "if (!sudah(ptPeriode(b.ulang, lalu)))"),
    ('kalender: SPT badan tetap 31 Maret', PT, "export function ptTanggalBerlaku(b, wp) { return b.id === 'spt' && !b.tanggal ? (wp === 'badan' ? '04-30' : '03-31') : String(b.tanggal || ''); }", "export function ptTanggalBerlaku(b, wp) { return b.id === 'spt' && !b.tanggal ? '03-31' : String(b.tanggal || ''); }"),
    ('kalender: tanggal 31 tidak dijepit di bulan pendek', PT, "return y + '-' + String(m).padStart(2, '0') + '-' + String(Math.min(d, akhir)).padStart(2, '0'); };", "return y + '-' + String(m).padStart(2, '0') + '-' + String(d).padStart(2, '0'); };"),
    ('kalender: lewat boleh ditandai tanpa catatan', PT, "if (b.keadaan === 'lewat' && cat.length < 3) return { tolak:", "if (false) return { tolak:"),
    ('kalender: tanda dobel putaran yang sama diterima', PT, "if ((b.riwayat || []).some((x) => x.periode === p) || (ptCek()[b.id] || []).some((x) => x.periode === p)) return { tolak:", "if (false) return { tolak:"),
    ('kalender: hari pertama langsung kuning', PT, "(akhir ? ptHariKe(iso) - ptHariKe(akhir.tanggal) > 30 : keadaan === 'lewat')", "(akhir ? ptHariKe(iso) - ptHariKe(akhir.tanggal) > 30 : true)"),
    ('server: rumus putaran berbeda dari halaman', FP, "if (lalu >= mulai && !sudah(periode(b.ulang, lalu)))", "if (!sudah(periode(b.ulang, lalu)))"),
    ('server: lewat dikirim tiap hari (cerewet)', FP, "const lewatSenin = hariMinggu === 1 && masuk.some((x) => x.sisa < 0);", "const lewatSenin = masuk.some((x) => x.sisa < 0);"),
    ('server: butir mati tetap dikirim', FP, "|| seen[b.id] || b.nyala === false) return;", "|| seen[b.id]) return;"),
    ('pengingat: hari sebelum per butir diabaikan', SL, "hariSebelum: p.hariSebelum !== undefined && p.hariSebelum !== null && isFinite(Number(p.hariSebelum)) ? Number(p.hariSebelum) : Number(A[jk.kunci]) || 0,", "hariSebelum: Number(A[jk.kunci]) || 0,"),
    ('pengingat: kalender dari lokal tidak masuk', SL, "if (p && p.jenis === 'patuh' && /^\\d{4}-\\d{2}-\\d{2}$/.test(String(p.jatuh || ''))) out.push(p); });", "if (false) out.push(p); });"),
    ('lonceng: pengingat tidak masuk', KB, "  (Array.isArray(pengingat) ? pengingat : []).forEach((p) => { if (!p || !p.id) return;", "  ([]).forEach((p) => { if (!p || !p.id) return;"),
    ('akses: tanda kalender karyawan lolos perangkat', AK, "cekGudang: ['ben'],   /* rules v19 (paket KPI laba, owner 24 Nov 2026): cek gudang = ben */ kepatuhanCek: ['ben'],", "cekGudang: ['ben'],   /* rules v19 (paket KPI laba, owner 24 Nov 2026): cek gudang = ben */ kepatuhanCek: ['ben', 'karyawan'],"),
    ('akses: pendengar ben tanpa kalender', AK, "const out = BACA_STAF.concat(akun.peran === 'ben' ? BACA_BEN : []).concat(akun.peran === 'ben' ? BACA_BEN_JANJI : []).map((n) => ({ nama: n }));", "const out = BACA_STAF.concat(akun.peran === 'ben' ? BACA_BEN_JANJI : []).map((n) => ({ nama: n }));"),
]
RUSAK_STATIS = [
    ('Stok tanpa tab Tugas gudang', 'stok', "s.tab === 'tugas' ? gambarTugas(s)", "s.tab === 'tugasX' ? gambarTugas(s)"),
    ('Barang masuk tanpa label tumpukan', 'stok', "${s.tbm ? kartuLabelMasuk(s.tbm.id, s) : ''}", ''),
    ('Jual tanpa label lengkap', 'jual', 'LB.lbIsiKemasan(sasaran, kode, { tanggal: tg }', 'TK.tkIsiLabel(sasaran, kode, { tanggal: tg }'),
    ('Pajak tanpa kalender', 'laporan', 'const kalender = kartuKalender(s, kini(), P.jenisWp, P.statusPkp);', "const kalender = '';"),
    ('lonceng tanpa pengingat', 'app', "loncengPengingat({ ambil: (a) => pengingatLonceng(a),", "({ ambil: (a) => pengingatLonceng(a),"),
    ('server tanpa push pagi', 'fi', "exports.kabarPatuh = onSchedule({ schedule: 'every day 07:00', timeZone: 'Asia/Jakarta'", "exports.kabarPatuhX = onSchedule({ schedule: 'every day 07:00', timeZone: 'Asia/Jakarta'"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_gudang_label_patuh.py && python3 alat-uji/uji_gudang_label_patuh.py --kontrol', 'true'),
]
BON_PEMASOK_LAMA = uji_ringkasan_baru.BON_PEMASOK_LAMA

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var M = aman('minus', function () { return gdMinus(kini); }); var MB = aman('minusBuku', function () { return minusBuku(iso).daftar.filter(function (x) { return x.jenis === 'beras' || x.jenis === 'kemasan' || x.jenis === 'kantong'; }); });
out.minus = M && MB ? { n: M.n, sama: M.n === MB.length } : null;
out.buang = []; daftarBulan(kini, 6).forEach(function (b) { if (tahunDiarsip(b.key)) return; var B = aman('buang ' + b.key, function () { return gdBuang(b.key, kini); }); if (B) out.buang.push({ key: b.key, menutup: B.diarsip ? 'arsip' : B.menutup, jenis: (B.jenis || []).length }); });
var T = aman('tugas', function () { return gdTugas(kini, { tanggal: iso, jam: '20:00' }); }); out.tugas = T ? { n: T.n, galat: T.daftar.filter(function (x) { return x.galat; }).map(function (x) { return x.id; }) } : null;
var K = aman('kemasan', function () { return lbRingkasKemasan(kini); }); out.kemasan = K ? { bertanggal: K.nBertanggal, lewat: K.lewat.length, dekat: K.dekat.length, tanpa: K.tanpa.length } : null;
var P = aman('kalender', function () { return ptKalender(kini); }); out.kalender = P ? { butir: P.baris.length, perlu: P.perlu.length } : null;
var DS = aman('dbStok', function () { return dbStok(kini); }); var DQ = aman('dbMutu', function () { return dbMutu(kini); });
out.dasbor = { gudang: !!(DS && DS.gudang && !DS.gudang.galat), patuh: !!(DQ && DQ.patuh && !DQ.patuh.galat) };
print(JSON.stringify(out));
"""


def fp_js():
    return ("var FPX = (function () { var module = { exports: {} }; var exports = module.exports; var require = function () { return {}; };\n"
            + open(os.path.join(AKAR, FP), encoding='utf-8').read() + '\nreturn module.exports; })();\n')


def bundel_js(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)
    if js.count(BON_PEMASOK_LAMA) == 1: js = js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))
    return js


def jsc(skrip):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(skrip); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    return r, out


# Sidik BEKU keluaran label escpos.js SEBELUM paket ini (main d9dd788, dihitung 26 Nov 2026 dari EP_LAMA). Pembanding byte-sama label tanpa `baris`
# tidak bergantung pada git: checkout CI dangkal tidak punya origin/main. Kalau git terbaca, sidik ini dicocokkan dulu dengan escpos.js di main.
SIDIK_EP_LAMA = '33bd9415e0f79835a948f6b4252313c11e1c99adc01625c500c5baea3f406da0'


def sidik_ep(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def ep_lama():
    """Keluaran label dari escpos.js SEBELUM paket ini (git origin/main) — hanya untuk mencocokkan SIDIK_EP_LAMA; None kalau tidak terbaca."""
    for rev in ('origin/main', 'HEAD'):
        r = subprocess.run(['git', '-C', AKAR, 'show', rev + ':' + EP], capture_output=True, text=True)
        if r.returncode == 0 and 'tambah.forEach' not in r.stdout: break
    else: return None
    rr, out = jsc(bundel_baru.PRELUDE + bundel_baru.polos(r.stdout) + EP_LAMA)
    return json.loads(out) if rr.returncode == 0 and out.startswith('{') else None


def jalan(teks):
    js = bundel_js(teks)
    jam = "var __KINI = new Date('2026-11-18T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    fp = ("var FPX = (function () { var module = { exports: {} }; var exports = module.exports; var require = function () { return {}; };\n" + teks[FP] + '\nreturn module.exports; })();\n')
    r, out = jsc(jam + js + fp + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); g = list(h['gagal']); l = h['lulus']
    if sidik_ep(h['ep']) == SIDIK_EP_LAMA: l += 1
    else: g.append('7: label TANPA baris tidak byte-sama dengan escpos.js sebelum paket ini (cetakan lama berubah)')
    return l, g


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    for k in ('gd', 'lb', 'pt'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k] or 'window.' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    if src['gd'].count('koleksi:') != 0: g.append('gudang-logika menulis dokumen — modul ini BACA SAJA')
    if src['lb'].count("koleksi: 'aturanToko'") != 1 or 'koleksi:' in src['lb'].replace("koleksi: 'aturanToko'", ''): g.append('label-logika menulis selain setelan aturanToko/catatStok')
    if "import { ssCekGudang" in src['gd'] or "from './sistem-logika.js'" in src['gd']: g.append('gudang-logika memakai sistem-logika (Dasbor tidak memuatnya)')
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL + [FP]), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b)
            l, g = jalan(T)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    lama = ep_lama()
    l, g = jalan(teks); ls, gs = statis(src)
    if lama is None: print('escpos.js di main tidak terbaca dari git (checkout dangkal) — label tanpa baris dibanding sidik beku saja')
    elif sidik_ep(lama) != SIDIK_EP_LAMA: g.append('sidik beku label lama BASI: escpos.js di main sudah berubah — hitung ulang SIDIK_EP_LAMA dari EP_LAMA')
    else: print('Sidik beku label lama = escpos.js di main (git)')
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        r, out = jsc("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = not h['galat'] and h['minus'] and h['minus']['sama'] and all(x['menutup'] in (True, 'arsip') for x in h['buang']) and h['tugas'] and not h['tugas']['galat'] and h['dasbor']['gudang'] and h['dasbor']['patuh']
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: minus ≠ minusBuku, hilang & rusak tidak menutup, tugas galat, atau Dasbor galat')
    sys.exit(1 if g or gs else 0)
