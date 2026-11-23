#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kpi_laba.py — PAKET KPI LABA (keputusan owner 24 Nov 2026, 15 butir). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  1 per jenis (karung · kemasan · literan · repack + lain) menutup ke laba kotor Laporan, retur ikut jenis nota asalnya, ongkir ke "lain";
  2 laba usaha − hapus buku ± lebih/kurang kas = laba bersih mesin (identitas dijaga); 3 PPh final tidak terpotong dua kali; ketiga margin satu penyebut;
  4 harga saran = modal ÷ (1 − target), mark-up = m ÷ (1 − m), target bawaan = margin 3 bulan mesin, owner menimpa; 5 BPS disebut;
  6 GMROI = laba kotor merek ÷ rata-rata nilai stok buku (dihitung ulang mandiri di uji); 7 siklus uang = tiga sumbernya;
  8 target harian (owner / bawaan impas) + lampu laju jam; 9 kas minimum = saldoKantong empat tempat (tegas <); 10 nota terbesar = nota Riwayat (batal tidak);
  11 bon dalam kg; 12 HPP maks tegas `>`, catatStok disalin utuh; 13 hari bayar pemasok (saldo awal & tanpa tunjuk disebut, tidak dihitung);
  14 cek mingguan gudang (jadwal, lima hal, catatan wajib bila masalah, bentuk = rules v19 / penjaga kiriman); 15 lama pemenuhan pesanan;
  Dasbor (dbKpi) = angka yang sama apa adanya; layar memasang kartunya (statis).

    python3 alat-uji/uji_kpi_laba.py            → N lulus · 0 gagal
    python3 alat-uji/uji_kpi_laba.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru, uji_ringkasan_baru, uji_kunci_periode  # noqa: E402
JSC = uji_antar.JSC
KL = 'baru/js/layar/kpi-laba-logika.js'; LG = 'baru/js/layar/laporan-logika.js'; ST = 'baru/js/layar/stok-logika.js'; BP = 'baru/js/layar/bon-pemasok-logika.js'
PO = 'baru/js/layar/pesanan-logika.js'; RW = 'baru/js/layar/riwayat-logika.js'; CK = 'baru/js/layar/stok-catat-logika.js'; SL = 'baru/js/layar/sistem-logika.js'; AK = 'baru/js/data/akses.js'
DL = 'baru/js/layar/dasbor-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_ringkasan_baru.modul_dasbor() + ['baru/js/data/akses.js', 'baru/js/data/hemat-baca.js', RW, KL, SL])))
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'harga': 'baru/js/layar/harga.js', 'menu': 'baru/js/layar/menu.js', 'menuL': 'baru/js/layar/menu-logika.js',
          'stok': 'baru/js/layar/stok.js', 'pelanggan': 'baru/js/layar/pelanggan.js', 'app': 'baru/js/app.js', 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'kl': KL,
          'bundel': 'alat-uji/bundel_baru.py', 'koleksi': 'baru/js/data/koleksi.js', 'rules': 'firestore.rules', 'cssL': 'baru/css/laporan.css', 'cssR': 'baru/css/ringkasan.css', 'cssH': 'baru/css/harga.css',
          'baca': 'baru/BACA-DULU.md'}

KOTAK_KPI = {
  'batchMasuk': [{'id': 'b2', 'tanggal': '2026-11-02', 'jam': '08:00', 'pemasok': 'Roda Contoh', 'caraBayar': 'utang', 'biayaBongkar': 50000, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'subtotalHarga': 13300000, 'hargaPerKg': 13300}]}],
  'utangPemasokMutasi': [
      {'id': 'sa1', 'tipe': 'saldoAwal', 'pemasok': 'Roda Contoh', 'nominal': 1000000, 'bonTanggal': '2026-08-01', 'catatan': 'bon lama', 'tanggal': '2026-09-20'},
      {'id': 'p1', 'tipe': 'bayar', 'pemasok': 'Roda Contoh', 'nominal': 5000000, 'bonId': 'b2', 'tanggal': '2026-11-12', 'jam': '10:00'},
      {'id': 'p2', 'tipe': 'bayar', 'pemasok': 'Roda Contoh', 'nominal': 3000000, 'bonId': 'b2', 'tanggal': '2026-11-17', 'jam': '10:00'},
      {'id': 'p3', 'tipe': 'bayar', 'pemasok': 'Roda Contoh', 'nominal': 1000000, 'bonId': 'sa1', 'tanggal': '2026-11-13', 'jam': '10:00'},
      {'id': 'p4', 'tipe': 'bayar', 'pemasok': 'Roda Contoh', 'nominal': 500000, 'bonId': 'tidak-ada', 'tanggal': '2026-11-14', 'jam': '10:00'}],
  'penjualanNov': [
      {'id': 'n1', 'tanggal': '2026-11-03', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': 'Bu Suti', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 700000, 'hppTotalSaatJual': 660000, 'grupNota': 'gn1'},
      {'id': 'n2', 'tanggal': '2026-11-04', 'jam': '09:00', 'caraBayar': 'QRIS', 'namaPelanggan': 'Pak Contoh', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 2, 'totalKg': 10, 'hargaTotal': 144000, 'hppTotalSaatJual': 132000, 'grupNota': 'gn2'},
      {'id': 'n3', 'tanggal': '2026-11-05', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'literan', 'merkSumber': 'Angsa', 'jumlahLiter': 3, 'totalKg': 2.46, 'hargaTotal': 40500, 'hppTotalSaatJual': 33000, 'grupNota': 'gn3'},
      {'id': 'n4', 'tanggal': '2026-11-06', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'repacking', 'merkSumber': 'Angsa', 'namaProduk': 'Angsa', 'totalKg': 10, 'hargaTotal': 145000, 'hppTotalSaatJual': 130000, 'grupNota': 'gn4'},
      {'id': 'n5', 'tanggal': '2026-11-06', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'wadah', 'namaProduk': 'Kantong 5 kg', 'jumlahUnit': 1, 'hargaTotal': 2000, 'hppTotalSaatJual': 1125, 'grupNota': 'gn4'},
      {'id': 'n6', 'tanggal': '2026-11-07', 'jam': '09:00', 'caraBayar': 'Kredit', 'namaPelanggan': 'Bu Suti', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 715000, 'ongkirAntar': 15000, 'hppTotalSaatJual': 660000, 'grupNota': 'gn6'},
      {'id': 'n7', 'tanggal': '2026-11-08', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': 72000, 'grupNota': 'gn7'},
      {'id': 'n8', 'tanggal': '2026-11-18', 'jam': '08:30', 'caraBayar': 'Tunai', 'namaPelanggan': 'Mbak Contoh', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 690000, 'hppTotalSaatJual': 655000, 'grupNota': 'gn8'},
      {'id': 'n9', 'tanggal': '2026-11-18', 'jam': '09:15', 'caraBayar': 'QRIS', 'namaPelanggan': '', 'jenis': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 1, 'totalKg': 5, 'hargaTotal': 72000, 'hppTotalSaatJual': 66000, 'grupNota': 'gn9'},
      {'id': 'n10', 'tanggal': '2026-11-18', 'jam': '09:30', 'caraBayar': 'Tunai', 'namaPelanggan': 'Batal', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 900000, 'hppTotalSaatJual': 655000, 'grupNota': 'gn10', 'dibatalkan': True}],
  'retur': [
      {'id': 'r1', 'tanggal': '2026-11-10', 'jam': '10:00', 'notaAsalId': 'n2', 'jenisAsal': 'kemasan', 'namaProduk': 'Kembang', 'ukuranKemasan': 5, 'jumlahUnit': 1, 'totalKg': 5, 'kondisi': 'tidak_utuh', 'nominalRefund': 72000, 'satuanNota': 'unit'},
      {'id': 'r2', 'tanggal': '2026-11-12', 'jam': '10:00', 'notaAsalId': 'n3', 'jenisAsal': 'karung', 'merkSumber': 'Angsa', 'totalKg': 1, 'jumlahKarung': 0.02, 'kondisi': 'utuh', 'nominalRefund': 13500, 'hppKembali': 13000, 'satuanNota': 'liter'}],
  'pengeluaranHarian': [
      {'id': 'h1', 'tanggal': '2026-11-05', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'listrik token', 'nominal': 100000},
      {'id': 'h2', 'tanggal': '2026-11-06', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'karyawan', 'keterangan': 'kopi karyawan', 'nominal': 20000},
      {'id': 'h3', 'tanggal': '2026-11-07', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Potongan QRIS', 'nominal': 2000, 'mdr': True},
      {'id': 'h4', 'tanggal': '2026-11-09', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'bayar PPh final Oktober', 'nominal': 5000}],
  'piutangMutasiTambah': [
      {'id': 'hb1', 'tanggal': '2026-11-11', 'jam': '10:00', 'namaPelanggan': 'Deka', 'tipe': 'hapusBuku', 'nominal': 50000},
      {'id': 'by1', 'tanggal': '2026-11-12', 'jam': '10:00', 'namaPelanggan': 'Bu Suti', 'tipe': 'bayar', 'nominal': 715000, 'caraBayar': 'Tunai'}],
  'penyesuaianStok': [{'id': 'ps1', 'tanggal': '2026-11-10', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': 100, 'kgFisik': 98, 'selisihKg': -2, 'alasan': 'susut', 'nilaiRp': -26000, 'hppPerKgSaatOpname': 13000}],
  'pesanan': [
      {'id': 'o1', 'tanggal': '2026-11-10', 'jam': '09:00', 'namaPelanggan': 'Bu Suti', 'isi': 'beras', 'status': 'dibayar', 'trxIdJual': 'x1', 'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-11-10T02:00:00.000Z'}, {'status': 'diantar', 'pada': '2026-11-11T02:00:00.000Z'}, {'status': 'dibayar', 'pada': '2026-11-11T08:00:00.000Z'}]},
      {'id': 'o2', 'tanggal': '2026-11-14', 'jam': '07:00', 'namaPelanggan': 'Pak Contoh', 'isi': 'beras', 'status': 'dibayar', 'trxIdJual': 'x2', 'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-11-14T00:00:00.000Z'}, {'status': 'dibayar', 'pada': '2026-11-14T06:00:00.000Z'}]},
      {'id': 'o3', 'tanggal': '2026-11-14', 'jam': '07:00', 'namaPelanggan': 'Batal', 'isi': 'beras', 'status': 'batal', 'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-11-14T00:00:00.000Z'}, {'status': 'dibayar', 'pada': '2026-11-14T01:00:00.000Z'}, {'status': 'batal', 'pada': '2026-11-14T02:00:00.000Z'}]},
      {'id': 'o4', 'tanggal': '2026-11-15', 'jam': '07:00', 'namaPelanggan': 'Mbak Contoh', 'isi': 'beras', 'status': 'diantar', 'riwayatStatus': [{'status': 'dipesan', 'pada': '2026-11-15T00:00:00.000Z'}, {'status': 'diantar', 'pada': '2026-11-15T12:00:00.000Z'}, {'status': 'dibayar', 'pada': '2026-11-16T00:00:00.000Z'}, {'status': 'diantar', 'pada': '2026-11-16T01:00:00.000Z'}]}],
}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b) { return a !== null && b !== null && Math.abs(a - b) < 0.5; };
var KINI = new Date('2026-11-18T10:00:00+07:00'); var nId = 90000;
var W = { tanggal: '2026-11-18', jam: '10:00', kini: '2026-11-18T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
var K0 = JSON.parse(J(KOTAK));
K0.batchMasuk = K0.batchMasuk.concat(KPI.batchMasuk); K0.penjualan = K0.penjualan.concat(KPI.penjualanNov); K0.piutangMutasi = K0.piutangMutasi.concat(KPI.piutangMutasiTambah);
K0.utangPemasokMutasi = KPI.utangPemasokMutasi; K0.retur = KPI.retur; K0.pengeluaranHarian = KPI.pengeluaranHarian; K0.penyesuaianStok = KPI.penyesuaianStok; K0.pesanan = KPI.pesanan;
Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); });
var ATUR = [{ id: 'rekapOmzet', jenisWp: 'orangPribadi', tarifPerMil: 5, batasBebas: 0, batasOmzet: 4800000000 }, { id: 'catatStok', tempoHari: 21, modalFifoMulai: '', kadarAirMaks: 13 }];
pasok('aturanToko', JSON.parse(J(ATUR)));
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-11-01', laci: 20000000, brankas: 1000000, rekening: 2000000, amplop: 300000, diubahPada: '2026-11-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { pasok('aturanToko', JSON.parse(J(ATUR)).concat(extra || [])); };

// ---- 1 · per jenis November: angka tangan (lihat komentar uji) & menutup ke mesin
var JB = jenisBulan('2026-11', KINI); var j = function (id) { return JB.jenis.find(function (g) { return g.id === id; }); };
ok('1: per jenis menutup ke laba kotor, omzet ber-HPP, omzet tanpa modal & jumlah baris Laporan', JB.menutup === true && JB.identitas.length === 4, JB.kalimat);
ok('1: karung = 3 nota (700rb + 700rb tanpa ongkir + 690rb) − modal 1.975rb = 115rb; batal tidak ikut', j('karung').omzet === 2090000 && j('karung').margin === 115000 && j('karung').nBaris === 3, J(j('karung')));
ok('1: kemasan = 144rb + 72rb − retur rusak 72rb; modal 198rb; 1 baris tanpa modal 72rb → margin −54rb', j('kemasan').omzet === 144000 && j('kemasan').margin === -54000 && j('kemasan').omzetTanpaHpp === 72000, J(j('kemasan')));
ok('1: literan: retur UTUH dari nota literan ikut LITERAN (nota asal), modalnya batal 13rb → margin 7rb', j('literan').omzet === 27000 && j('literan').margin === 7000 && j('literan').nRetur === 1, J(j('literan')));
ok('1: repack 15rb; lain = wadah 875 + ongkir 15rb', j('repack').margin === 15000 && JB.lain.margin === 15875, J([j('repack'), JB.lain]));
ok('1: margin % per jenis = margin ÷ omzet jenis itu', Math.abs(j('karung').pct - 115000 / 2090000 * 100) < 1e-9 && Math.abs(j('literan').pct - 7000 / 27000 * 100) < 1e-9, J([j('karung').pct, j('literan').pct]));
ok('1: retur tanpa nota asal ikut satuannya (liter → literan, kg → repack, unit → kemasan)', lpJenisRetur({ satuanNota: 'liter' }, {}) === 'literan' && lpJenisRetur({ satuanNota: 'kg' }, {}) === 'repack' && lpJenisRetur({ satuanNota: 'unit' }, {}) === 'kemasan' && lpJenisRetur({ jenisAsal: 'karung' }, {}) === 'karung');

// ---- 2 · 3 · 5 · tiga margin + PPh + BPS
var M = klMarginBulan('2026-11', KINI); var KM = keManaLabaKotor('2026-11', KINI); var t = function (id) { return M.tangga.find(function (x) { return x.id === id; }); };
ok('2: laba usaha = laba kotor − biaya toko − biaya karyawan + susut (mesin keManaLabaKotor)', M.labaUsaha === KM.labaKotor - KM.biayaToko - KM.biayaKaryawan + KM.susut && KM.susut === -26000 && M.mdr === 2000, J([M.labaUsaha, KM.labaKotor, KM.biayaToko, KM.biayaKaryawan, KM.susut, M.mdr]));
ok('2: IDENTITAS laba usaha − hapus buku ± lebih/kurang kas = laba bersih mesin (persis)', M.tutupUsaha === true && Math.abs(M.labaUsaha - KM.hapusBuku + M.identitas.lebihKurang - KM.labaBersih) < 0.5 && KM.hapusBuku === 50000, J(M.identitas));
ok('2: margin kotor % = laba kotor ÷ omzet ber-HPP = rasio titik impas Laporan › Biaya', Math.abs(t('kotor').pct - titikImpas(kendaliBulan('2026-11', KINI), KINI).rasio * 100) < 1e-9 && M.omzet === KM.L.omzetHitung, J([t('kotor').pct, M.omzet]));
ok('2: tiga margin satu penyebut (omzet ber-HPP)', Math.abs(t('usaha').pct - M.labaUsaha / M.omzet * 100) < 1e-9 && Math.abs(t('bersih').pct - M.labaBersih / M.omzet * 100) < 1e-9 && M.labaBersih === KM.labaBersih, J(M.tangga));
var PP = pjPerkiraanBulan('2026-11', KINI);
ok('3: PPh perkiraan dari modul pajak; uang keluar bertulis PPh (5rb) sudah di biaya → dipotong SISANYA saja', PP.pph > 5000 && M.pph === PP.pph && M.pajakDiBiaya.rp === 5000 && M.potongPph === PP.pph - 5000 && M.sesudahPph === M.labaBersih - (PP.pph - 5000), J([PP, M.pajakDiBiaya, M.potongPph]));
ok('3: baris "sesudah perkiraan PPh final" ada & berlabel perkiraan', !!t('pph') && /perkiraan/.test(t('pph').ket), J(t('pph')));
ok('3: kata pajak hanya utuh (bukan "pajangan")', klPajakDiBiaya('2026-11').n === 1);
ok('5: pembanding BPS 9,84 % / 11,35 % dengan sumber; grosir toko = karung, ecer = kemasan+literan+repack', M.bps.grosir === 9.84 && M.bps.eceran === 11.35 && /BPS/.test(M.bps.sumber) && /2016/.test(M.bps.sumber)
  && Math.abs(M.bps.tokoGrosir - 115000 / 2090000 * 100) < 1e-9 && Math.abs(M.bps.tokoEcer - (-54000 + 7000 + 15000) / (144000 + 27000 + 145000) * 100) < 1e-9, J(M.bps));
ok('2·5: mark-up = margin ÷ (1 − margin) di tiap tangga', M.tangga.every(function (r) { return r.pct === null ? r.markup === null : Math.abs(r.markup - r.pct / (100 - r.pct) * 100) < 1e-9; }), J(M.tangga));
ok('1·2·3: kartu menutup (identitas usaha + per jenis)', M.menutup === true && M.jenisMenutup === true);

// ---- 4 · saran harga & target margin
ok('4: harga saran = modal ÷ (1 − target), dibulatkan KE ATAS', klHargaSaran(10000, 20, 100) === 12500 && klHargaSaran(13350, 3, 100) === 13800 && klHargaSaran(0, 3, 100) === null && klHargaSaran(1000, 100, 0) === null);
ok('4: mark-up = m ÷ (1 − m): 20 % → 25 %, 50 % → 100 %', Math.abs(klMarkup(20) - 25) < 1e-9 && Math.abs(klMarkup(50) - 100) < 1e-9 && klMarkup(null) === null && klMarkup(100) === null);
var TM = klTargetMargin(KINI); var R3 = lpJenisRentang('2026-09-01', '2026-11-18'); var r3 = function (id) { return R3.jenis.find(function (g) { return g.id === id; }); };
ok('4: target BAWAAN = margin terwujud 3 bulan (1 Sep – hari ini) dari mesin, per jenis', TM.dari === '2026-09-01' && Math.abs(TM.jenis.karung.pct - r3('karung').margin / r3('karung').omzet * 100) < 1e-9 && !TM.jenis.karung.dariOwner, J([TM.jenis.karung, r3('karung')]));
var Pst = susunAturKpi({ targetMargin: { karung: '4,5', literan: '' } }, W); terapkanKeCache(Pst.dokumen);
var TM2 = klTargetMargin(KINI);
ok('4: target owner menimpa (4,5 %); kosong = tetap bawaan', !Pst.tolak && TM2.jenis.karung.pct === 4.5 && TM2.jenis.karung.dariOwner && !TM2.jenis.literan.dariOwner, J([Pst.tolak, TM2.jenis.karung]));
ok('4: target di luar 0–90 % ditolak (tidak dibulatkan diam)', !!susunAturKpi({ targetMargin: { kemasan: '95' } }, W).tolak && !!susunAturKpi({ targetMargin: { kemasan: 'abc' } }, W).tolak);
var S = hgSemua(KINI); var bS = cariBaris(S, kunciHarga('Angsa', 'S')); var bK = cariBaris(S, kunciHarga('Angsa', 'K25')); var bL = cariBaris(S, kunciHarga('Angsa', 'L')); var bM = cariBaris(S, kunciHarga('Kembang', 'K5'));
var X = klSaranBaris(bK, TM2, S);
ok('4: karung utuh 25 kg: saran = modal ÷ (1 − 4,5 %) dibulatkan seperti usul kemasan; margin & mark-up harga sekarang', X.saran.length === 1 && X.saran[0].jenis === 'karung' && X.saran[0].harga === klHargaSaran(bK.modalUnit, 4.5, S.atur.bulatKemasan)
  && Math.abs(X.pctKini - (bK.n - bK.modalUnit) / bK.n * 100) < 1e-9 && Math.abs(X.markupKini - (bK.n - bK.modalUnit) / bK.modalUnit * 100) < 1e-6, J(X));
ok('4: per kg: repack saja kalau merek punya harga karung utuh sendiri; literan → literan; kemasan 5 kg → kemasan', klSaranBaris(bS, TM2, S).saran.map(function (x) { return x.jenis; }).join() === 'repack'
  && klSaranBaris(bL, TM2, S).saran[0].jenis === 'literan' && klSaranBaris(bM, TM2, S).saran[0].jenis === 'kemasan' && klJenisKatalog(bS, false).join() === 'repack,karung');
ok('4: harga katalog TIDAK berubah (saran saja)', cariBaris(hgSemua(KINI), kunciHarga('Angsa', 'K25')).n === bK.n && !hgSemua(KINI).nDraf);

// ---- 6 · GMROI — dihitung ulang MANDIRI dari buku per tanggal
var G = klGmroi('2026-11', KINI); var ga = G.daftar.find(function (x) { return x.merek === 'Angsa'; }); var MB = merekBulan('2026-11', KINI);
var rp = 0, nH = 0; for (var d = 1; d <= 18; d++) { var iso = '2026-11-' + (d < 10 ? '0' : '') + d; var B = ingatStokKarung(iso); nH++; Object.keys(B).forEach(function (k) { if (lpMerekBuku(k) === 'Angsa' && B[k].sisaKg > 0) rp += B[k].sisaKg * (B[k].hppTerakhirPerKg || 0); }); }
var rata = rp / nH; var lAngsa = MB.merek.find(function (x) { return x.merek === 'Angsa'; }).margin;
ok('6: GMROI Angsa = laba kotor merek (Per merek) ÷ rata-rata nilai stok 1–18 Nov (buku per tanggal)', ga && G.nHari === 18 && Math.abs(ga.nilaiRata - rata) < 0.5 && ga.laba === lAngsa && Math.abs(ga.gmroi - lAngsa / rata) < 1e-9, J([ga, rata, lAngsa]));
ok('6: total GMROI = Σ laba ÷ Σ nilai merek yang terhitung; teks layar', G.total !== null && Math.abs(G.total - G.labaDihitung / G.nilaiDihitung) < 1e-12 && klGmroiTeks(0.4234) === '0,42×' && klGmroiTeks(null) === '—', J(G));

// ---- 13 · hari bayar pemasok
var HB = bpHariBayar(KINI, 90);
ok('13: b2 datang 2 Nov, dibayar 12 Nov (5 jt, 10 hari) & 17 Nov (3 jt, 15 hari) → (5×10 + 3×15)/8 = 11,875 hari', Math.abs(HB.rataHari - 11.875) < 1e-9 && HB.total.n === 2 && HB.pemasok.length === 1 && HB.pemasok[0].nama === 'Roda Contoh', J(HB));
ok('13: bon lama sebelum sistem & bayar tanpa tunjuk DISEBUT, tidak dihitung', HB.saldoAwal.n === 1 && HB.saldoAwal.rp === 1000000 && HB.tanpaTunjuk.n === 1 && HB.tanpaTunjuk.rp === 500000 && HB.sebab.length === 2, J([HB.saldoAwal, HB.tanpaTunjuk]));
ok('13: teks hari', bpHariTeks(11.875) === '±11,9 hari' && bpHariTeks(0.2) === 'hari itu juga' && bpHariTeks(null) === '—');

// ---- 7 · siklus uang = tiga sumber
var SK = klSiklusUang(KINI); var U = umRingkas(KINI); var T = tertagihBon(KINI);
ok('7: siklus = hari stok (periode ÷ putaran) + hari bon tertagih − hari bayar pemasok, tiap bagian dari sumbernya', SK.keadaan === 'ada' && U.putaranMerek > 0 && T.rataHari !== null
  && Math.abs(SK.hari - (U.periode.n / U.putaranMerek + T.rataHari - HB.rataHari)) < 1e-9 && SK.bagian[2].tanda === -1, J([SK.hari, U.periode.n, U.putaranMerek, T.rataHari, HB.rataHari]));
ok('7: bon Bu Suti 7 Nov lunas 12 Nov = 5 hari tertagih', Math.abs(T.rataHari - 5) < 1e-9, J(T.rataHari));

// ---- 8 · target harian
var R = rekapHari('2026-11-18');
ok('8: omzet hari ini = 690rb + 72rb (nota batal tidak)', R.omzet === 762000, R.omzet);
var TH0 = klTargetHari(KINI); var Ti = titikImpas(kendaliBulan('2026-11', KINI), KINI);
ok('8: tanpa target owner = BAWAAN omzet impas per hari (titikImpas)', TH0.dariOwner === false && TH0.target === Ti.omzetImpasHari && Ti.omzetImpasHari > 0 && /impas/.test(TH0.targetTeks), J([TH0.target, Ti.omzetImpasHari]));
var lampu = function (n, jam) { aturDengan([{ id: 'kpiLaba', targetHarian: n }]); return klTargetHari(new Date('2026-11-18T' + jam + ':00+07:00')); };
var L1 = lampu(700000, '10:00'), L2 = lampu(2000000, '10:00'), L3 = lampu(3000000, '10:00'), L4 = lampu(2438400, '10:00');
ok('8: lampu: tercapai hijau · sesuai laju jam kuning · di bawah laju merah (10.00 = 5/16 hari toko)', L1.lampu === 'hijau' && L2.lampu === 'kuning' && L2.laju === 625000 && L3.lampu === 'merah' && L3.laju === 937500 && L1.dariOwner, J([L1.lampu, L2.lampu, L2.laju, L3.lampu]));
ok('8: tepat di laju = kuning (≥), di bawah 1 rupiah = merah', L4.laju === 762000 && L4.lampu === 'kuning' && lampu(2438404, '10:00').lampu === 'merah', J([L4.laju, L4.lampu]));
ok('8: sebelum buka = laju 0 (bukan merah); sesudah tutup = laju penuh', lampu(2000000, '04:00').lampu === 'kuning' && lampu(2000000, '22:00').lampu === 'merah' && klBagianHari(new Date('2026-11-18T13:00:00+07:00')) === 0.5);

// ---- 9 · kas minimum
var SKt = saldoKantong(); aturDengan([{ id: 'kpiLaba', kasMinimum: 0 }]);
ok('9: ambang kosong = mati', klKasMinimum().nyala === false);
aturDengan([{ id: 'kpiLaba', kasMinimum: SKt.total }]); var K1 = klKasMinimum(); aturDengan([{ id: 'kpiLaba', kasMinimum: SKt.total + 1 }]); var K2 = klKasMinimum();
ok('9: kas = saldoKantong EMPAT tempat (laci + brankas + rekening + amplop); tegas <', SKt.ada && K1.kas === SKt.total && SKt.total === SKt.laci + SKt.brankas + SKt.rekening + SKt.amplop && K1.bawah === false && K2.bawah === true && K2.kurang === 1 && K2.tempat.length === 4, J([SKt, K1.bawah, K2.bawah]));

// ---- 11 · bon dalam kg
var MP = klModalPerKg(); var BK = klBonKg(1300000, MP); var B0 = ingatStokKarung(); var kg = 0, rr = 0; Object.keys(B0).forEach(function (k) { if (B0[k].sisaKg > 0) { kg += B0[k].sisaKg; rr += B0[k].sisaKg * (B0[k].hppTerakhirPerKg || 0); } });
ok('11: modal per kg = Σ sisa × modal per kg buku ÷ Σ sisa (nilai neraca); bon ÷ modal per kg', Math.abs(MP.perKg - rr / kg) < 1e-9 && Math.abs(BK.kg - 1300000 / MP.perKg) < 1e-9 && /^bon Rp1\.300\.000 ≈ \d[\d.]* kg beras pada modal Rp[\d.]+\/kg$/.test(BK.teks), BK.teks);
ok('11: tanpa stok = tanpa kalimat (bukan 0 kg)', klBonKg(1000, { perKg: null }).teks === '' && klBonKg(1000, { perKg: null }).kg === null);

// ---- 12 · HPP maks
aturDengan([]); pasok('aturanToko', [{ id: 'catatStok', tempoHari: 21, modalFifoMulai: '2026-12-01', kadarAirMaks: 13, hppMaksPerKg: { Angsa: 13350 } }]);
ok('12: HPP b2 Angsa = 13.300 + bongkar 50/kg = 13.350 → batas 13.350 TIDAK ditandai (tegas >)', ckHppLewat('2026-11-01', '2026-11-30').daftar.length === 0 && ckBatasHpp('Angsa') === 13350);
pasok('aturanToko', [{ id: 'catatStok', tempoHari: 21, modalFifoMulai: '2026-12-01', kadarAirMaks: 13, hppMaksPerKg: { Angsa: 13349 } }]);
var HL = ckHppLewat('2026-11-01', '2026-11-30');
ok('12: batas 13.349 → kedatangan 2 Nov ditandai, lebih 1/kg', HL.daftar.length === 1 && HL.daftar[0].batchId === 'b2' && Math.abs(HL.daftar[0].lebihPerKg - 1) < 1e-9 && klHppLewatBulan('2026-11').daftar.length === 1, J(HL));
var HMk = hitungMasuk({ pemasok: 'Roda Contoh', tanggal: '2026-11-18', bongkar: '0', baris: [{ merk: 'Angsa', jumlahKarung: '1', beratKarung: '50', hargaPerKg: '13350' }, { merk: 'Angsa', jumlahKarung: '1', beratKarung: '50', hargaPerKg: '13349' }] });
ok('12: Barang masuk menandai baris yang lewat (tegas >), yang sama persis tidak', HMk.sah.length === 2 && HMk.sah[0].lewatHppMaks === true && HMk.sah[1].lewatHppMaks === false && HMk.lewatHppMaks.length === 1, J(HMk.sah.map(function (b) { return [b.hppPerKg, b.hppMaks, b.lewatHppMaks]; })));
var Sh = susunAturHppMaks({ Angsa: '14.000', 'IR64 Apex': '' }, W); var dk = Sh.dokumen && Sh.dokumen[0].data;
ok('12: simpan batas: catatStok DISALIN utuh (saklar FIFO, tempo, mutu tetap), kosong = hapus batas', dk && dk.modalFifoMulai === '2026-12-01' && dk.tempoHari === 21 && dk.kadarAirMaks === 13 && J(dk.hppMaksPerKg) === '{"Angsa":14000}', J(dk));
ok('12: batas rusak ditolak', !!susunAturHppMaks({ Angsa: '-5' }, W).tolak && !!susunAturHppMaks({ Angsa: '13.500,5' }, W).tolak);
ok('12: varian (Merek · mutu) tanpa batas sendiri memakai batas mereknya; batas sendiri menang', ckBatasHpp('Angsa · Premium', { Angsa: 13000 }) === 13000 && ckBatasHpp('Angsa · Premium', { Angsa: 13000, 'Angsa · Premium': 14000 }) === 14000 && ckBatasHpp('Lain', { Angsa: 13000 }) === 0);
pasok('aturanToko', JSON.parse(J(ATUR)));

// ---- 10 · nota terbesar
var NB = klNotaTerbesar('bulan', KINI, 3); var NH = klNotaTerbesar('hari', KINI, 10);
ok('10: bulan ini 3 teratas = 715rb (bon) · 700rb · 690rb; nota batal 900rb TIDAK ikut', J(NB.daftar.map(function (o) { return o.total; })) === '[715000,700000,690000]' && NB.daftar[0].caraTeks === 'Bon' && NB.nNota === 8, J(NB));
ok('10: hari ini = 2 nota (690rb, 72rb); tujuan membuka nota itu di Jual › Riwayat', NH.daftar.length === 2 && NH.daftar[0].total === 690000 && NH.daftar[0].tujuan.ke === 'jual' && NH.daftar[0].tujuan.jalur === 'riwayat' && NH.daftar[0].tujuan.rwBuka === 'gn8', J(NH));
ok('10: nota berbaris dua dijumlah satu nota (repack + wadah = 147rb)', klNotaTerbesar('bulan', KINI, 10).daftar.some(function (o) { return o.kunci === 'gn4' && o.total === 147000 && o.nBaris === 2; }));
ok('10: 7 hari = 12–18 Nov', klNotaTerbesar('minggu', KINI, 10).dari === '2026-11-12' && klNotaTerbesar('xx', KINI).rentang === 'hari');

// ---- 15 · lama pemenuhan pesanan
var LP = poLamaPenuhi(KINI, 90);
ok('15: dipesan → diantar: o1 1 hari + o4 0,5 hari (diantar PERTAMA) → 0,75 hari', LP.antar.n === 2 && Math.abs(LP.antar.rata - 0.75) < 1e-9, J(LP.antar));
ok('15: dipesan → jadi nota: o1 1,25 + o2 0,25 → 0,75; batal & nota yang dibatalkan tidak ikut', LP.nota.n === 2 && Math.abs(LP.nota.rata - 0.75) < 1e-9 && LP.nota.teks === '±18 jam', J(LP.nota));

// ---- 14 · cek mingguan gudang
var CG0 = ssCekGudang(KINI);
ok('14: belum pernah dicek → jatuh hari ini, perlu', CG0.terakhir === null && CG0.jatuh === '2026-11-18' && CG0.perlu === true, J(CG0));
ok('14: jenis pengingat baru "gudang" muncul di sumber pengingat', ssSumberPengingat(KINI).some(function (p) { return p.jenis === 'gudang' && p.jatuh === '2026-11-18'; }) && SS_JENIS_PENGINGAT.some(function (j) { return j.id === 'gudang'; }));
ok('14: kelima hal wajib dijawab', /5 belum dijawab/.test(susunCekGudang({}, '', W, KINI).tolak || '') && /1 belum dijawab/.test(susunCekGudang({ timbangan: true, palet: true, bocor: true, lembap: true }, '', W, KINI).tolak || ''));
var semua = { timbangan: true, palet: true, bocor: true, lembap: true, kutu: true };
ok('14: ada masalah → catatan wajib', /catatannya/.test(susunCekGudang(Object.assign({}, semua, { kutu: false }), '', W, KINI).tolak || ''));
var CK1 = susunCekGudang(Object.assign({}, semua, { bocor: false }), 'atap belakang bocor', W, KINI); var dc = CK1.dokumen && CK1.dokumen[0].data;
ok('14: dokumen cekGudang = bentuk rules v19 / penjaga kiriman (cekGudangSah)', dc && CK1.dokumen[0].koleksi === 'cekGudang' && cekGudangSah(dc) && Object.keys(dc).every(function (k) { return SS_CEK_KOLOM.indexOf(k) >= 0; }) && dc.cek.bocor === false && CK1.patch.kabarAwas === true, J(CK1));
ok('14: penjaga kiriman menolak kolom lain / hal lain / nilai teks', !cekGudangSah(Object.assign({}, dc, { nominal: 1 })) && !cekGudangSah(Object.assign({}, dc, { cek: Object.assign({}, dc.cek, { atap: true }) })) && !cekGudangSah(Object.assign({}, dc, { cek: Object.assign({}, dc.cek, { kutu: 'ya' }) })) && cekGudangSah(Object.assign({}, dc, { oleh: 'Ben', olehUid: 'u', diubahPada: 'x' })));
terapkanKeCache(CK1.dokumen); var CG1 = ssCekGudang(KINI);
ok('14: sesudah dicek → berikutnya 7 hari lagi; riwayat menyebut masalahnya', CG1.terakhir && CG1.jatuh === '2026-11-25' && CG1.sisa === 7 && !CG1.perlu && CG1.riwayat[0].masalah.join() === 'bocor', J(CG1));
ok('14: "selesai" biasa ditolak untuk jenis gudang (wajib isi lima hal)', !!susunSelesaiPengingat({ jenis: 'gudang', sisa: 0 }, '', W).tolak);
var A14 = periksaKiriman({ jenis: 'aktif', peran: 'ben', uid: 'u-b', nama: 'Ben', aktif: true }, [{ koleksi: 'cekGudang', data: dc, ada: false }], [], {}, KINI);
var A14k = periksaKiriman({ jenis: 'aktif', peran: 'karyawan', uid: 'u-k', nama: 'K', aktif: true }, [{ koleksi: 'cekGudang', data: dc, ada: false }], [], {}, KINI);
ok('14: Penjaga laci boleh mengirim cek (rules v19), karyawan tidak', !A14.tolak && !!A14k.tolak, J([A14, A14k]));
ok('14: atur jadwal: gudangTiap 1–30 hari', !susunAturSistem('pengingat', { gudangTiap: '14' }, W).tolak && !!susunAturSistem('pengingat', { gudangTiap: '45' }, W).tolak);

// ---- setelan Menu (8 · 9)
aturDengan([{ id: 'kpiLaba', targetMargin: { karung: 4.5 } }]);
var Sa = susunAturKpi({ targetHarian: '2.500.000', kasMinimum: '1.000.000' }, W);
ok('8·9: simpan target & kas TIDAK menimpa target margin yang sudah tersimpan', !Sa.tolak && Sa.dokumen[0].data.targetHarian === 2500000 && Sa.dokumen[0].data.kasMinimum === 1000000 && Sa.dokumen[0].data.targetMargin.karung === 4.5, J(Sa));
ok('8·9: ketikan rusak ditolak, kosong = bawaan / mati', !!susunAturKpi({ targetHarian: '-1' }, W).tolak && !!susunAturKpi({ kasMinimum: '12,5' }, W).tolak && susunAturKpi({ targetHarian: '' }, W).dokumen[0].data.targetHarian === 0 && !!susunAturKpi({}, W).tolak);
aturDengan([]);

// ---- Dasbor = angka yang sama
var DB = dbKpi(KINI);
ok('Dasbor: kelompok kpi = kpi-laba-logika apa adanya (margin, target, kas, siklus, nota, HPP, pesanan)', !DB.margin.galat && DB.margin.labaBersih === M.labaBersih && !DB.target.galat && DB.target.omzet === 762000 && !DB.siklus.galat && Math.abs(DB.siklus.hari - SK.hari) < 1e-9
  && DB.nota.daftar.length === 2 && !DB.pesanan.galat && DB.pesanan.nota.n === 2 && !DB.kas.galat, J([DB.margin.galat, DB.target.galat, DB.kas.galat, DB.siklus.galat, DB.nota.galat, DB.hpp.galat, DB.pesanan.galat]));
var SD = susunDasbor(KINI, 'hari');
ok('Dasbor: susunDasbor memuat kpi & dipertahankan saat ganti rentang; piutang membawa bon dalam kg', SD.kpi && !SD.kpi.galat && susunDasbor(KINI, 'bulan', SD).kpi === SD.kpi && SD.tagihan.piutang.kg && SD.tagihan.piutang.kg.perKg > 0 && DB_PANAS.indexOf('kpi') >= 0, J(SD.tagihan.piutang.kg));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

# ASAP DATA TOKO (lokal saja; dilewati di CI): cadangan toko terbaru → tiap bulan Agu–bulan terakhir: per jenis menutup, identitas laba usaha → laba bersih benar,
# GMROI & nota terbesar & siklus uang & lama pesanan terhitung tanpa galat, kelompok Dasbor kpi tanpa galat. Yang dicetak hanya benar/salah & jumlah (bukan rupiah).
ASAP = r"""
console.error = function () {};
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); }); setelSumber('cadangan', 'asap');
var hidup = (CAD.penjualan || []).filter(function (p) { return !p.dikoreksiOleh && !p.dibatalkan; }); var tgl = hidup.map(function (p) { return p.tanggal || ''; }).sort();
var akhir = tgl[tgl.length - 1]; var KINI = new Date(akhir + 'T20:00:00'); var bln = []; for (var k = '2026-08'; k <= akhir.slice(0, 7); ) { bln.push(k); var y = +k.slice(0, 4), m = +k.slice(5, 7) + 1; if (m > 12) { m = 1; y++; } k = y + '-' + (m < 10 ? '0' : '') + m; }
var per = bln.map(function (key) { var J = jenisBulan(key, KINI); var M = klMarginBulan(key, KINI); var G = klGmroi(key, KINI);
  return { key: key, jenis: J.diarsip ? 'arsip' : J.menutup, usaha: M.tutupUsaha, margin: M.menutup, gmroi: G.total !== null, nJenis: J.diarsip ? 0 : J.jenis.filter(function (g) { return g.margin !== null; }).length }; });
var D = dbKpi(KINI); var galat = ['margin', 'target', 'kas', 'siklus', 'nota', 'hpp', 'pesanan'].filter(function (x) { return D[x] && D[x].galat; });
var S = hgSemua(KINI); var T = klTargetMargin(KINI); var nSaran = S.baris.filter(function (b) { return klSaranBaris(b, T, S).saran.some(function (x) { return x.harga !== null; }); }).length;
print(JSON.stringify({ akhir: akhir, per: per, galat: galat, siklus: D.siklus.keadaan, nota: D.nota.daftar ? D.nota.daftar.length : -1, pesanan: D.pesanan.keadaan, hariBayar: bpHariBayar(KINI, 90).keadaan, nSaran: nSaran, nBaris: S.baris.length,
  target: D.target.lampu, kas: D.kas.nyala, cek: ssCekGudang(KINI).perlu }));
"""

STATIS = [
    ('Laporan memasang kartu margin, GMROI, nota terbesar', 'laporan', ["import * as KL from './kpi-laba-logika.js';", 'kartuMargin(KL.klMarginBulan(key, kini()), s)', 'kartuGmroi(KL.klGmroi(key, kini()), HL)', 'kartuNotaTerbesar(KL.klNotaTerbesar(s.notaR, kini(), 10))',
                                                              '${margin}${panel}', '${terbesar}${rekap}', 'data-aksi="notaBuka"', "notaBuka: ({ kunci }) => keTujuan({ ke: 'jual', jalur: 'riwayat', rwBuka: kunci })", 'HPP lewat batas ×']),
    ('Dasbor memasang kartu Margin & target + bon dalam kg', 'dasbor', ['kartuKpi(D.kpi)', 'function kartuKpi(Q)', 'data-k="db-kpi"', 'data-k="db-bon-kg"', 'db-lampu ']),
    ('dasbor-logika menyusun kelompok kpi', 'kl', ['export function klMarginBulan', 'export function klTargetHari']),
    ('Harga › Katalog: saran harga, target margin, BPS, hari bayar pemasok', 'harga', ["import * as KL from './kpi-laba-logika.js';", 'gambarSaran(b, S)', 'gambarTargetMargin(s)', 'KL.susunAturKpi({ targetMargin: a }, waktu())', 'gambarHariBayar()', 'BP.bpHariBayar(kini())']),
    ('Menu: lembar Target & ambang + cek gudang (owner & Ben)', 'menu', ["target: 'Target & ambang'", 'gambarTarget(s, d)', 'KL.susunAturKpi(a, waktu())', 'function kartuCekGudang(s, d)', "${akunM.peran === 'ben' ? kartuCekGudang(s, d) : ''}", "${p && p.jenis === 'gudang' ? kartuCekGudang(s, d) : ''}", 'S.susunCekGudang(a.cek, a.catatan, waktu(), kini())']),
    ('Menu laci punya pintu Target & ambang', 'menuL', ["baris('target', 'naik', 'Target & ambang'"]),
    ('Stok › Barang masuk: tanda HPP lewat + atur batas (owner)', 'stok', ['b.sah && b.lewatHppMaks', 'function gambarAturHpp(s)', 'C.susunAturHppMaks(isi, waktu())']),
    ('Pelanggan › Bon: bon dalam kg (owner saja)', 'pelanggan', ['klBonKg(Bn.total, klModalPerKg())', 'data-k="bon-kg"', 'if (bukanOwner(akunKini())) return']),
    ('app.js membuka nota di Riwayat', 'app', ["t.ke === 'jual' && t.jalur === 'riwayat'", 'rwBuka: t.rwBuka || null']),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/kpi-laba-logika.js">']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_kpi_laba.py']),
    ('bundel uji melengkapi modul untuk Dasbor', 'bundel', ["KL_MODUL = 'baru/js/layar/kpi-laba-logika.js'", "KL_PEMAKAI = ('dasbor-logika.js',)"]),
    ('koleksi cekGudang terdaftar & rules v19 punya bloknya', 'koleksi', ["{ nama: 'cekGudang',"]),
    ('rules v19', 'rules', ['match /cekGudang/{id}', "allow create: if owner() || stafCekGudang(['ben'], id);"]),
    ('gerak: pita/lampu bergerak + hormat reduced motion', 'cssR', ['dbLampuDenyut', '.layar-ringkasan .db-lampu { animation: none; transition: none; }']),
    ('gerak Laporan & Harga', 'cssL', ['lpKlBuka']), ('gerak Harga', 'cssH', ['hgSaranMasuk', 'hgPitaTumbuh']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Paket KPI laba', 'uji_kpi_laba.py', 'rules v19']),
    ('modul tanpa DOM & tanpa menulis kecuali setelan', 'kl', []),
]

RUSAK = [
    ('per jenis: retur ikut jenisAsal saja (nota asal & satuan diabaikan)', LG, "  const a = r && r.notaAsalId !== undefined && r.notaAsalId !== null ? peta[String(r.notaAsalId)] : null; if (a) return lpJenisBaris(a);\n", "  return r && r.jenisAsal === 'kemasan' ? 'kemasan' : 'karung';\n"),
    ('per jenis: ongkir ikut karung (tidak dipisah ke lain)', LG, "const ong = Math.round(Number(p.ongkirAntar) || 0); const harga = (p.hargaTotal || 0) - ong; const tercatat = hppTercatat(p);\n    g.nBaris += 1;", "const ong = 0; const harga = (p.hargaTotal || 0) - ong; const tercatat = hppTercatat(p);\n    g.nBaris += 1;"),
    ('per jenis: kelompok "lain" hilang dari penjaga (penjaga wajib berbunyi)', LG, "const lain = lpJadiJenis(per.lain); const semua = jenis.concat([lain]);", "const lain = lpJadiJenis(per.lain); const semua = jenis;"),
    ('laba usaha tanpa susut', KL, "const labaUsaha = K.labaKotor - K.biayaToko - K.biayaKaryawan + K.susut;", "const labaUsaha = K.labaKotor - K.biayaToko - K.biayaKaryawan;"),
    ('PPh terpotong dua kali', KL, "const potong = pph === null ? null : Math.max(0, pph - D.rp);", "const potong = pph === null ? null : pph;"),
    ('margin bersih dibagi omzet penuh (penyebut beda)', KL, "{ id: 'bersih', nama: 'Margin laba bersih', rp: labaBersih, pct: klPct(labaBersih, omzet)", "{ id: 'bersih', nama: 'Margin laba bersih', rp: labaBersih, pct: klPct(labaBersih, omzet + (Number(L.omzetTanpaHpp) || 0) + 1)"),
    ('mark-up = margin (rumus salah)', KL, "export const klMarkup = (m) => (m === null || m === undefined || !isFinite(m) || m >= 100 ? null : m / (100 - m) * 100);", "export const klMarkup = (m) => (m === null || m === undefined || !isFinite(m) || m >= 100 ? null : m);"),
    ('harga saran = modal × (1 + target)', KL, "const x = modal / (1 - targetPct / 100);", "const x = modal * (1 + targetPct / 100);"),
    ('target bawaan angka karangan', KL, "const bawaan = g && g.margin !== null && g.omzet > 0 ? g.margin / g.omzet * 100 : null;", "const bawaan = 22;"),
    ('GMROI dibagi kg, bukan rupiah', KL, "const gm = g.margin !== null && v.rp > 0.5 ? g.margin / v.rp : null;", "const gm = g.margin !== null && v.rp > 0.5 ? g.margin / v.kg : null;"),
    ('nilai stok rata-rata tanpa modal per kg', ST, "j.kg += kg; j.rp += kg * (Number(x.hppTerakhirPerKg) || 0);", "j.kg += kg; j.rp += kg;"),
    ('siklus uang: hari bayar pemasok DITAMBAH', KL, "{ id: 'bayar', nama: 'Hari bayar pemasok', hari: B.rataHari, tanda: -1,", "{ id: 'bayar', nama: 'Hari bayar pemasok', hari: B.rataHari, tanda: 1,"),
    ('target harian: lampu tanpa laju jam (pagi selalu merah)', KL, "const laju = Math.round(target * bagian);", "const laju = target;"),
    ('target harian: bawaan bukan omzet impas', KL, "const target = A.targetHarian > 0 ? A.targetHarian : bawaan;", "const target = A.targetHarian > 0 ? A.targetHarian : 1000000;"),
    ('kas minimum: laci saja', KL, "const bawah = S.total < A.kasMinimum;", "const bawah = S.laci < A.kasMinimum;"),
    ('kas minimum: ≤ (sama dengan ambang dianggap kurang)', KL, "const bawah = S.total < A.kasMinimum;", "const bawah = S.total <= A.kasMinimum;"),
    ('bon kg: memakai harga beli terakhir, bukan modal neraca', KL, "kg += s; rp += s * (Number(x.hppTerakhirPerKg) || 0);", "kg += s; rp += s * (Number(x.hargaTerakhirPerKg) || 0);"),
    ('HPP maks: ≥ (sama persis ditandai)', CK, "if (bt > 0 && m.hppPerKg > bt) {", "if (bt > 0 && m.hppPerKg >= bt) {"),
    ('HPP maks: Barang masuk ≥', CK, "b.lewatHppMaks = bt > 0 && b.hppPerKg > bt;", "b.lewatHppMaks = bt > 0 && b.hppPerKg >= bt;"),
    ('HPP maks: catatStok ditulis tanpa kolom lama (saklar FIFO hilang)', CK, "const data = Object.assign({}, lama, { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, hppMaksPerKg: peta });", "const data = { id: 'catatStok', tanggal: w.tanggal, jam: w.jam, hppMaksPerKg: peta };"),
    ('nota terbesar: nota batal ikut', RW, "const cocok = D.daftar.filter((o) => (o.status === 'berlaku' || o.status === 'sebagian') && (!dari || o.tanggal >= dari) && o.tanggal <= sampai);", "const cocok = D.daftar.filter((o) => (!dari || o.tanggal >= dari) && o.tanggal <= sampai);"),
    ('hari bayar pemasok: bon lama ikut dihitung', BP, "      if (b.jenis === 'saldoAwal') { saldoAwal.n += 1; saldoAwal.rp += n; return; }\n", ""),
    ('hari bayar pemasok: tidak ditimbang rupiah', BP, "P.rp += n; P.rh += n * h; P.n += 1; ikut = true;", "P.rp += 1; P.rh += h; P.n += 1; ikut = true;"),
    ('pesanan: diantar terakhir, bukan pertama', PO, "const t1 = poSaat(p, status, status === 'dibayar');", "const t1 = poSaat(p, status, true);"),
    ('pesanan: batal ikut dihitung', PO, "if (!p || p.status === 'batal' || (status === 'dibayar' && p.status !== 'dibayar')) return;", "if (!p) return;"),
    ('cek gudang: masalah tanpa catatan lolos', SL, "if (masalah.length && cat.length < 5) return", "if (false) return"),
    ('cek gudang: jadwal tidak maju sesudah dicek', SL, "const jatuh = terakhir ? ssTambahHari(terakhir.tanggal, tiap) : iso;", "const jatuh = iso;"),
    ('cek gudang: penjaga kiriman membolehkan kolom lain', AK, "if (Object.keys(d).some((k) => CEK_GUDANG_KOLOM.indexOf(k) < 0)) return false;", ""),
    ('cek gudang: karyawan boleh mengirim', AK, "orderRutin: ['ben'], cekGudang: ['ben'] };", "orderRutin: ['ben'], cekGudang: ['ben', 'karyawan'] };"),
    ('setelan: simpan target menimpa target margin', KL, "const lama = ugAturDok(KL_ID) || {}; const data = Object.assign({}, lama, { id: KL_ID, tanggal: w.tanggal, jam: w.jam });", "const lama = {}; const data = { id: KL_ID, tanggal: w.tanggal, jam: w.jam };"),
    ('Dasbor kpi memakai target bawaan tetap', DL, "target: aman(() => klTargetHari(kini))", "target: aman(() => ({ omzet: 0 }))"),
]
RUSAK_STATIS = [
    ('Laporan tanpa kartu margin', 'laporan', '${margin}${panel}', '${panel}'),
    ('Dasbor tanpa kartu kpi', 'dasbor', 'kartuKpi(D.kpi)', "''"),
    ('Harga tanpa saran', 'harga', 'gambarSaran(b, S)', "''"),
    ('tablet Ben tanpa kartu cek gudang', 'menu', "${akunM.peran === 'ben' ? kartuCekGudang(s, d) : ''}", ''),
    ('Pelanggan menampilkan modal ke staf', 'pelanggan', 'if (bukanOwner(akunKini())) return', 'if (false) return'),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_kpi_laba.py', 'true'),
]
BON_PEMASOK_LAMA = uji_ringkasan_baru.BON_PEMASOK_LAMA


def jalan(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)
    if js.count(BON_PEMASOK_LAMA) == 1: js = js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))
    jam = "var __KINI = new Date('2026-11-18T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(jam + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar KPI = ' + json.dumps(KOTAK_KPI) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    kl = src['kl']
    if 'document.' in kl or 'tulisDokumen' in kl: g.append('kpi-laba-logika menyentuh DOM / menulis langsung — modul ini cuma menyusun')
    if kl.count("koleksi: 'aturanToko'") != 1: g.append('kpi-laba-logika menulis dokumen selain setelan aturanToko/kpiLaba')
    return len(STATIS) - len(g), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


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
    l, g = jalan(teks); ls, gs = statis(src)
    print('KOTAK PASIR: %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    import glob
    cad = sorted(glob.glob(os.path.join(AKAR, 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL); js = uji_kunci_periode.satu_lingkup(js)
        if js.count(BON_PEMASOK_LAMA) == 1: js = js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(js + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP); pth = f.name
        r = subprocess.run([JSC, pth], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(pth)
        out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out); beres = not h['galat'] and all((x['jenis'] in (True, 'arsip')) and x['usaha'] for x in h['per'])
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: per jenis / identitas laba usaha tidak menutup, atau kelompok Dasbor galat')
    sys.exit(1 if g or gs else 0)
