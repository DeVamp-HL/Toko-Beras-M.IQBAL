#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_sisa_sensus.py — PAKET SISA SENSUS (keputusan owner 27 Nov 2026: B94 B68 A74 B35 A47 A121). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  B94 satu saringan Dasbor untuk semua kartu (dbSaring: bulan kartu bulanan, tolak berkalimat; kelompok yang ikut dihitung untuk rentang itu, yang lain = posisi
  sekarang & sama persis; saringan Hari ini = Dasbor seperti dulu; nama widget ikut periode; headline tetap hari ini) · lpRekapRentang sehari = rekapHari.
  B68 pembelian per hari/minggu/bulan dari kedatangan (bon vs langsung; stok awal & lahir buku bukan belanja) — batang bulan = "+ Pembelian" HPP periode.
  A74 susut per penjaga: dibagi ke yang masuk kerja sejak hitungan sebelumnya barang itu (cocok persis = batas, rework bukan batas, ½ hari = setengah),
  tanpa hari kerja = kelompok sendiri, Σ = susut & selisih stok Laporan persis.
  B35 diperkirakan telat = 2 dari 3 bon terakhir lunas lewat jatuh tempo; hanya bon BELUM jatuh tempo; yang lewat & tanpa riwayat disebut.
  A47 PPh final pos anggaran: perkiraan = pjTahun, jatah sampai hari ke-N, sisihkan = perkiraan − setor; laba bersih, Σ biaya & titik impas TIDAK berubah.
  A121 modal tertahan: rata-rata nilai stok × bunga (bawaan 6 %, setelan owner, 0 = mati) × hari ÷ 365; karung = umNilaiRata (GMROI); rentang panjang disampel.

    python3 alat-uji/uji_sisa_sensus.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_sisa_sensus.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru, uji_ringkasan_baru, uji_kunci_periode, uji_susut_harga, uji_dasbor_sensus  # noqa: E402
JSC = uji_antar.JSC
DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'; SH = 'baru/js/layar/susut-harga-logika.js'; BL = 'baru/js/layar/bon-logika.js'
KL = 'baru/js/layar/kpi-laba-logika.js'; KB = 'baru/js/layar/kendali-biaya-logika.js'; LPL = 'baru/js/layar/laporan-logika.js'
MODUL = uji_dasbor_sensus.MODUL
SUMBER = {'dasbor': 'baru/js/layar/dasbor.js', 'kisi': 'baru/js/layar/dasbor-kisi.js', 'ringkasan': 'baru/js/layar/ringkasan.js', 'laporan': 'baru/js/layar/laporan.js',
          'pelanggan': 'baru/js/layar/pelanggan.js', 'menu': 'baru/js/layar/menu.js', 'css': 'baru/css/ringkasan.css', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md',
          'kl': KL, 'sh': SH, 'dl': DL, 'wg': WG}

KS = uji_susut_harga.KOTAK_SH
KARUNG = uji_susut_harga.KARUNG
def BON(i, tgl, nama, rp):
    x = KARUNG(i, tgl, 'Angsa', 10, rp, round(rp * 0.9)); x['caraBayar'] = 'Kredit'; x['namaPelanggan'] = nama; return x
def BAYAR(i, tgl, nama, rp):
    return {'id': i, 'tipe': 'bayar', 'namaPelanggan': nama, 'nominal': rp, 'tanggal': tgl, 'jam': '10:00', 'caraBayar': 'Tunai', 'dicatatDi': 'sistem'}
def HARI(dari, sampai, v):
    import datetime
    a = datetime.date.fromisoformat(dari); b = datetime.date.fromisoformat(sampai); out = {}
    while a <= b: out[a.isoformat()] = v; a += datetime.timedelta(days=1)
    return out
KOTAK = json.loads(json.dumps(KS))
# B68: kedatangan Nov dibayar NANTI (+ bongkar), stok awal (dicatat, bukan belanja), lahir buku (bukan kedatangan)
KOTAK['batchMasuk'] += [
    {'id': 104, 'tanggal': '2026-11-04', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'utang', 'biayaBongkar': 50000, 'merkList': [
      {'merk': 'Kembang', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 4, 'totalKg': 200, 'subtotalHarga': 2400000, 'hargaPerKg': 12000}]},
    {'id': 105, 'tanggal': '2026-11-01', 'jam': '07:00', 'pemasok': '', 'stokAwal': True, 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Contoh Awal', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 2, 'totalKg': 100, 'subtotalHarga': 1000000, 'hargaPerKg': 10000}]},
    {'id': 106, 'tanggal': '2026-11-06', 'jam': '07:00', 'pemasok': 'Pindah buku', 'lahirBuku': True, 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 1, 'totalKg': 50, 'subtotalHarga': 600000, 'hargaPerKg': 12000}]}]
# A74: rework (bukan batas) & hitungan Angsa sesudahnya; kemasan cocok persis lalu berselisih di hari tanpa penjaga tercatat
KOTAK['penyesuaianStok'] += [
    {'id': 206, 'tanggal': '2026-11-15', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': None, 'kgFisik': None, 'selisihKg': -0.1, 'alasan': 'rework karantina', 'nilaiRp': -1200, 'dariRework': True},
    {'id': 207, 'tanggal': '2026-11-17', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': 480, 'kgFisik': 479.84, 'selisihKg': -0.16, 'alasan': 'susut', 'nilaiRp': -2000, 'hppPerKgSaatOpname': 12500}]
KOTAK['penyesuaianKemasan'] = [
    {'id': 401, 'tanggal': '2026-11-16', 'jam': '10:00', 'namaProduk': 'Kemas Contoh', 'ukuranKemasan': 5, 'unitSistem': 10, 'unitFisik': 10, 'selisihUnit': 0, 'nilaiRp': 0, 'alasan': 'Cocok persis'},
    {'id': 402, 'tanggal': '2026-11-17', 'jam': '10:00', 'namaProduk': 'Kemas Contoh', 'ukuranKemasan': 5, 'unitSistem': 10, 'unitFisik': 9, 'selisihUnit': -1, 'nilaiRp': -2500, 'alasan': 'hilang'}]
KOTAK['absenKaryawan'] = [
    {'id': 'pekerja contoh a|2026-09', 'nama': 'Pekerja Contoh A', 'bulan': '2026-09', 'hari': HARI('2026-09-01', '2026-09-30', 1)},
    {'id': 'pekerja contoh a|2026-11', 'nama': 'Pekerja Contoh A', 'bulan': '2026-11', 'hari': dict(HARI('2026-11-01', '2026-11-10', 0.5), **{'2026-11-11': 0})},
    {'id': 'pekerja contoh b|2026-10', 'nama': 'Pekerja Contoh B', 'bulan': '2026-10', 'hari': HARI('2026-10-01', '2026-10-31', 1)},
    {'id': 'pekerja contoh b|2026-11', 'nama': 'Pekerja Contoh B', 'bulan': '2026-11', 'hari': dict(HARI('2026-11-01', '2026-11-10', 1), **{'2026-11-15': 1})}]
# B35: T biasanya telat (2 dari 3 bon terakhir lunas lewat jatuh tempo), R sekali telat, N belum pernah melunasi bon. Tempo = "waktunya ditagih" bawaan 14 hari.
KOTAK['penjualan'] = KOTAK['penjualan'] + [
    BON('t1', '2026-09-05', 'Pelanggan Contoh T', 100000), BON('t2', '2026-09-26', 'Pelanggan Contoh T', 100000), BON('t3', '2026-10-20', 'Pelanggan Contoh T', 100000),
    BON('t4', '2026-11-01', 'Pelanggan Contoh T', 80000), BON('t5', '2026-11-10', 'Pelanggan Contoh T', 60000),
    BON('r1', '2026-09-10', 'Pelanggan Contoh R', 100000), BON('r2', '2026-10-01', 'Pelanggan Contoh R', 100000), BON('r3', '2026-10-25', 'Pelanggan Contoh R', 100000), BON('r4', '2026-11-12', 'Pelanggan Contoh R', 50000),
    BON('n1', '2026-11-15', 'Pelanggan Contoh N', 40000), dict(KARUNG('q1', '2026-11-17', 'Kembang', 10, 130000, 120000), caraBayar='QRIS')]
KOTAK['piutangMutasi'] = [BAYAR(501, '2026-09-25', 'Pelanggan Contoh T', 100000), BAYAR(502, '2026-10-15', 'Pelanggan Contoh T', 100000), BAYAR(503, '2026-11-01', 'Pelanggan Contoh T', 100000),
                          BAYAR(511, '2026-09-15', 'Pelanggan Contoh R', 100000), BAYAR(512, '2026-10-20', 'Pelanggan Contoh R', 100000), BAYAR(513, '2026-11-05', 'Pelanggan Contoh R', 100000)]
# A47: setoran PPh masa November (contoh)
KOTAK['pajakSetoran'] = [{'id': 601, 'masaPajak': '2026-11', 'tanggalSetor': '2026-11-16', 'jumlah': 1000, 'ntpn': ''}]
ATUR = uji_susut_harga.ATUR_DASAR

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T14:00:00+07:00'); var nId = 90000;
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'pesanan', 'karantina', 'persetujuan', 'cekGudang', 'kepatuhanCek', 'absenKaryawan', 'pajakSetoran', 'pajakOmzetLuar'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-01', laci: 1000000, brankas: 250000, rekening: 0, amplop: 0, diubahPada: '2026-09-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var iso = '2026-11-18';

// ==================== 1 · B68 PEMBELIAN ====================
var PN = shPembelian('2026-11-01', iso), PS = shPembelian('2026-09-01', '2026-09-30'), PO = shPembelian('2026-10-01', '2026-10-31');
ok('1: Nov = kedatangan dibayar NANTI Rp2.400.000 + bongkar Rp50.000 · 200 kg · 1 kedatangan; stok awal Rp1.000.000 = dicatat (bukan belanja); lahir buku tidak dihitung',
  PN.rp === 2450000 && PN.n === 1 && PN.bon.rp === 2450000 && PN.bon.n === 1 && PN.langsung.rp === 0 && PN.kg === 200 && PN.dicatat === 1000000 && PN.nDicatat === 1, J(PN));
ok('1: Sep Rp16.800.000 (2 kedatangan dibayar langsung) · Okt Rp6.500.000; pemasok terbesar dulu', PS.rp === 16800000 && PS.n === 2 && PS.langsung.n === 2 && PS.bon.rp === 0 && PO.rp === 6500000 && PO.pemasok[0].pemasok === 'Pemasok Contoh B', J([PS, PO]));
var TB = shTrenBeli('bulan', KINI);
ok('1: batang bulan = "+ Pembelian" HPP periode bulan itu (satu aturan nilai kedatangan)', TB.batang.length >= 3 && TB.batang.every(function (b) { var H = shHppPeriode(b.id, KINI); return b.absen || (b.rp === H.beli && b.n === H.nBeli); }), J(TB.batang.map(function (b) { var H = shHppPeriode(b.id, KINI); return [b.id, b.rp, H.beli, b.n, H.nBeli]; })));
ok('1: HPP periode Nov: stok awal masuk "stok yang dicatat", bukan pembelian', shHppPeriode('2026-11', KINI).dicatat === 1000000 && shHppPeriode('2026-11', KINI).beli === 2450000);
var TH = shTrenBeli('hari', KINI), TM = shTrenBeli('minggu', KINI);
var m2 = TM.batang.find(function (b) { return b.dari === '2026-11-02'; }); var TH0 = shTrenBeli('hari', new Date('2026-11-10T14:00:00+07:00')); var h4 = TH0.batang.find(function (b) { return b.id === '2026-11-04'; });
ok('1: per hari (14, hari ini terakhir & berjalan) & per minggu Senin–Minggu: 4 Nov Rp2.450.000 bon; minggu 2–8 Nov sama', TH.batang.length === 14 && TH.batang[0].id === '2026-11-05' && TH.batang[13].id === iso && TH.batang[13].berjalan && h4 && h4.rp === 2450000 && h4.bon === 2450000 && m2 && m2.rp === 2450000 && m2.sampai === '2026-11-08', J([h4, m2]));
ok('1: tujuan batang: bulan → Laporan › Bulanan bulan itu, hari/minggu → Stok › Barang masuk', TB.batang[TB.batang.length - 1].tujuan.keluarga === 'bulanan' && TH.batang[0].tujuan.ke === 'stok');

// ==================== 2 · A74 SUSUT PER PENJAGA ====================
var SP = shSusutPenjaga('2026-09-01', iso); var og = function (n) { return SP.orang.find(function (g) { return g.nama === n; }) || {}; };
var A = og('Pekerja Contoh A'), Bk = og('Pekerja Contoh B'), T0 = og('(tanpa catatan hari kerja)');
// A: 201 (2–20 Sep, A saja) −96.000 · 202 (21 Sep–20 Okt: A 10 hari, B 20) −12.500 · 203 Kembang (2 Sep–10 Nov: A 29 + 5×½ = 34, B 41) −3.264 · 205 −453,33 · 301 kantong −2.266,67
ok('2: Pekerja A = Rp−114.484 (½ hari = setengah bobot; hitungan sebelumnya barang yang sama = batas)', dekat(A.bersih, -114484, 0.01) && dekat(A.susutKg, 8 + 1 + 0.6 * 34 / 75 + 0.1 * 34 / 75, 0.006), J(A));
ok('2: Pekerja B = Rp−35.416 (rework 15 Nov BUKAN batas: hitungan 17 Nov ikut jaga 15 Nov)', dekat(Bk.bersih, -35416, 0.01) && Bk.hariJaga === 42, J(Bk));
ok('2: hari tanpa penjaga tercatat (kemasan 17 Nov sesudah cocok persis 16 Nov) = kelompok sendiri', dekat(T0.bersih, -2500, 0.01) && T0.tanpa === true && SP.orang[SP.orang.length - 1].tanpa, J(SP.orang));
ok('2: Σ per penjaga = susut & selisih stok Laporan (barisSusutStok) persis — kalimat menutup', SP.menutup && dekat(SP.total, susutRentang('2026-09-01', iso).mesin, 0.01) && dekat(SP.total, -152400, 0.01) && /menutup persis/.test(SP.kalimat), J([SP.total, susutRentang('2026-09-01', iso).mesin]));
ok('2: hari kerja di rentang laporan (bukan rentang jaga): A 30 + 5 = 35, B 31 + 10 + 1 = 42', A.hariJaga === 35, J(A.hariJaga));
var SP2 = shSusutPenjaga('2026-10-01', '2026-10-31');
ok('2: rentang Okt: hanya hitungan 20 Okt (A 1/3, B 2/3)', SP2.nBaris === 1 && dekat((SP2.orang.find(function (g) { return g.nama === 'Pekerja Contoh B'; }) || {}).bersih, -25000, 0.01), J(SP2.orang));

// ==================== 3 · B35 PERKIRAAN TELAT ====================
var KB0 = pnKebiasaanBayar(KINI); var kT = KB0[kunciPelanggan('Pelanggan Contoh T')], kR = KB0[kunciPelanggan('Pelanggan Contoh R')];
ok('3: T: 3 bon terakhir lunas, 2 lewat jatuh tempo (6 & 5 hari) → biasanya telat · rata-rata telat 5,5 hari', kT && kT.n === 3 && kT.nTelat === 2 && kT.biasaTelat && dekat(kT.rataTelat, 5.5) && kT.tiga[0].lunas === '2026-11-01' && !kT.tiga[0].telat, J(kT));
ok('3: R: cuma 1 dari 3 telat → BUKAN biasanya telat', kR && kR.n === 3 && kR.nTelat === 1 && !kR.biasaTelat, J(kR));
var PT = pnPerkiraanTelat(KINI);
ok('3: diperkirakan telat = bon T yang BELUM jatuh tempo saja (10 Nov Rp60.000, jatuh tempo 24 Nov); bon T 1 Nov yang sudah lewat disebut terpisah', PT.n === 1 && PT.daftar[0].nama === 'Pelanggan Contoh T' && PT.daftar[0].rp === 60000 && PT.daftar[0].jatuhTerdekat === '2026-11-24' && PT.daftar[0].hariLagi === 6 && PT.nLewatBiasa === 1 && PT.rpLewatBiasa === 80000, J(PT));
ok('3: N belum pernah melunasi bon = belum bisa diperkirakan (disebut, bukan dicap)', PT.nTanpaRiwayat === 1 && /belum bisa diperkirakan/.test(PT.kalimat) && !PT.daftar.some(function (o) { return /N$/.test(o.nama); }), J(PT.kalimat));
var DT = dbTagihan(KINI);
ok('3: Dasbor Piutang = pnPerkiraanTelat apa adanya', DT.piutang.telat && DT.piutang.telat.n === PT.n && DT.piutang.telat.rp === PT.rp && DT.piutang.telatTujuan.tab === 'tempo', J(DT.piutang.telat));

// ==================== 4 · A47 PPh FINAL POS ANGGARAN ====================
var K0 = kendaliBulan('2026-11', KINI); var T0i = titikImpas(K0, KINI); var P0 = klPph(K0, KINI);
ok('4: tarif belum diatur → belum bisa diperkirakan, disebut jalannya (Laporan › Pajak)', P0.keadaan === 'tanpa' && P0.n === null && /Pakai aturan/.test(P0.teks), J(P0));
aturDengan([{ id: 'rekapOmzet', jenisWp: 'orangPribadi', tarifPerMil: 5, batasBebas: 0, batasOmzet: 4800000000 }, { id: 'kendaliBiaya', anggaran: { pph: 30000 }, ambang: 10, ambangPemicu: 10, kata: {} }]);
var K1 = kendaliBulan('2026-11', KINI); var P1 = klPph(K1, KINI); var PJb = pjTahun(2026, KINI).daftar.find(function (x) { return x.key === '2026-11'; });
ok('4: perkiraan = pjTahun (Laporan › Pajak) bulan itu; sisihkan = perkiraan − setor Rp1.000', P1.keadaan === 'ada' && P1.n === Math.round(PJb.pph) && P1.n > 0 && P1.setor === 1000 && P1.sisihkan === Math.max(0, P1.n - 1000), J([P1, PJb.pph]));
ok('4: bulan berjalan: dibanding jatah sampai hari ke-18 dari 30 (Rp18.000) + perkiraan sebulan; lampu dengan ambang kendali biaya', P1.dasar === 18000 && P1.proyeksi === Math.round(P1.n / 18 * 30) && P1.lampu === (P1.n <= 18000 ? 'hijau' : (P1.n - 18000) / 18000 * 100 <= 10 ? 'amber' : 'merah'), J([P1.dasar, P1.lampu, P1.n]));
ok('4: pos SENDIRI: Σ biaya, laba bersih & titik impas tidak berubah; bukan baris biaya', K1.semuaBiaya === K0.semuaBiaya && K1.labaBersih === K0.labaBersih && titikImpas(K1, KINI).omzetImpas === T0i.omzetImpas && !K1.baris.some(function (r) { return r.id === 'pph'; }), J([K1.semuaBiaya, K0.semuaBiaya]));
ok('4: anggaran PPh tersimpan di aturanToko/kendaliBiaya.anggaran.pph (Atur: draf membawa, simpan menulis)', aturKendali().anggaran.pph === 30000 && drafAtur().anggaran.pph === '30000' && susunAturKendali({ anggaran: { pph: '45.000' }, ambang: '10', ambangPemicu: '10', kata: {} }, W).dokumen[0].data.anggaran.pph === 45000, J(aturKendali().anggaran));
ok('4: Dasbor Bulan ini membawa pos PPh (klPph apa adanya)', dbBulanIni(KINI).pph && dbBulanIni(KINI).pph.n === P1.n);
aturDengan([]);

// ==================== 5 · A121 MODAL TERTAHAN ====================
var MT = klModalTertahan(KINI, '2026-11-01', iso); var U = umNilaiRata('2026-11-01', iso); var uk = Object.keys(U.buku).reduce(function (a, k) { return a + U.buku[k].rp; }, 0);
ok('5: bawaan 6 % setahun (keputusan owner 27 Nov) · 18 hari · rata-rata karung = umNilaiRata (GMROI) · biaya = rata × 6 % × 18 ÷ 365', MT.bunga === 6 && !MT.dariOwner && MT.nHari === 18 && !MT.sampel && dekat(MT.rata, uk, 0.01) && dekat(MT.biaya, MT.rata * 0.06 * 18 / 365, 0.01) && dekat(MT.sebulan, MT.rata * 0.06 / 12, 0.01), J([MT, uk]));
var N1 = ingatNeraca(iso); var MT1 = klModalTertahan(KINI, iso, iso);
ok('5: sehari = nilai stok neraca hari itu (beras karung + kemasan, tanpa buku minus)', N1.adaStokMinus || dekat(MT1.rata, N1.nilaiSack + N1.nilaiBags, 1), J([MT1.rata, N1.nilaiSack, N1.nilaiBags]));
var MY = klModalTertahan(KINI, '2026-01-01', iso);
ok('5: Tahun ini dipotong ke catatan pertama toko & rentang > 62 hari disampel (disebut di rumus)', MY.dari === '2026-09-02' && MY.nHari === 78 && MY.sampel && MY.nTitik <= 63 && /titik hari/.test(MY.rumus), J([MY.dari, MY.nHari, MY.nTitik]));
aturDengan([{ id: 'kpiLaba', bungaModalPersen: 0 }]); var M0 = klModalTertahan(KINI, '2026-11-01', iso);
aturDengan([{ id: 'kpiLaba', bungaModalPersen: 12 }]); var M12 = klModalTertahan(KINI, '2026-11-01', iso);
ok('5: setelan owner: 0 = mati (biaya 0, disebut) · 12 % = dua kali biaya bawaan', M0.bunga === 0 && M0.biaya === 0 && /mati/.test(M0.kalimat) && M12.bunga === 12 && M12.dariOwner && dekat(M12.biaya, 2 * MT.biaya, 0.01), J([M0.kalimat, M12.biaya, MT.biaya]));
aturDengan([]);
var s1 = susunAturKpi({ bungaModal: '6,5' }, W), s2 = susunAturKpi({ bungaModal: 'enam' }, W), s3 = susunAturKpi({ bungaModal: '51' }, W), s4 = susunAturKpi({ bungaModal: '0' }, W);
aturDengan([{ id: 'kpiLaba', bungaModalPersen: 9, kasMinimum: 500000 }]); var s5 = susunAturKpi({ bungaModal: '' }, W);
ok('5: simpan bunga: 6,5 → 6,5 · teks & > 50 DITOLAK berkalimat · 0 = mati · kosong = kembali bawaan (kolom lain tidak tertimpa)', !s1.tolak && s1.dokumen[0].data.bungaModalPersen === 6.5 && !!s2.tolak && !!s3.tolak && s4.dokumen[0].data.bungaModalPersen === 0 && !('bungaModalPersen' in s5.dokumen[0].data) && s5.dokumen[0].data.kasMinimum === 500000, J([s1, s2.tolak, s3.tolak, s4.dokumen && s4.dokumen[0].data, s5.dokumen && s5.dokumen[0].data]));
aturDengan([]);
ok('5: Dasbor Margin & target membawa modal tertahan bulan ini (klModalTertahan apa adanya)', dekat(dbKpi(KINI).modal.rata, MT.rata, 0.01) && dbKpi(KINI).modal.dari === '2026-11-01');

// ==================== 6 · B94 SATU SARINGAN ====================
var S = {}; ['hari', 'kemarin', 'h7', 'bulan', 'bulanLalu', 'tahun'].forEach(function (id) { S[id] = dbSaring({ id: id }, KINI); });
var Sp1 = dbSaring({ id: 'pilih', dari: '2026-10-25', sampai: '2026-11-05' }, KINI), Sp2 = dbSaring({ id: 'pilih', dari: '2026-10-03', sampai: '2026-10-09' }, KINI), St = dbSaring({ id: 'pilih', dari: '2026-11-10', sampai: '2026-11-30' }, KINI);
ok('6: bulan kartu bulanan: Hari ini/Kemarin/7 hari/Bulan ini/Tahun ini = Nov · Bulan lalu = Okt · pilih 25 Okt–5 Nov = Nov (disebut lintas) · pilih 3–9 Okt = Okt',
  S.hari.bawaan && !S.kemarin.bawaan && ['hari', 'kemarin', 'h7', 'bulan', 'tahun'].every(function (k) { return S[k].bulan === '2026-11'; }) && S.bulanLalu.bulan === '2026-10' && Sp1.bulan === '2026-11' && Sp1.lintas && /bulan tanggal akhir/.test(Sp1.bulanKet) && Sp2.bulan === '2026-10' && !Sp2.lintas, J([S, Sp1, Sp2]));
ok('6: pilihan ditolak (tanggal belum terjadi) = Dasbor tetap Hari ini + kalimat tolaknya', St.bawaan && St.id === 'hari' && /belum terjadi/.test(St.tolak), J(St));
var D0 = susunDasbor(KINI, 'hari'); var DH = susunDasbor(KINI, 'hari', null, null, S.hari);
ok('6: saringan Hari ini = Dasbor seperti dulu (semua kelompok sama persis)', ['hari', 'bulan', 'stok', 'tagihan', 'mutu', 'b2b', 'kpi', 'pondasi', 'beli'].every(function (k) { return J(D0[k]) === J(DH[k]); }));
var D7 = susunDasbor(KINI, 'hari', null, null, S.h7); var P7 = dbPeriode({ id: 'h7' }, KINI);
ok('6: 7 hari: kartu Hari ini = omzet, laba kotor, nota rentang itu (= kartu Periode) + pembanding 7 hari sebelumnya; judul ikut', D7.hari.omzet === P7.omzet && D7.hari.margin === P7.margin && D7.hari.nota === P7.nota && D7.hari.judul === '7 hari' && D7.hari.saring.banding.banding.omzet === P7.banding.omzet && D7.hari.tujuan.ke === 'laporan', J([D7.hari.omzet, P7.omzet, D7.hari.judul]));
var tunai7 = 0, kredit7 = 0; for (var i = 0; i < 7; i++) { var R7 = rekapHari(ugTambahHari(iso, -i)); tunai7 += R7.tunai; kredit7 += R7.kredit; }
ok('6: 7 hari: uang per cara bayar = Σ rekap harian (arus kas mesin rentang itu)', D7.hari.tunai === tunai7 && D7.hari.kredit === kredit7, J([D7.hari.tunai, tunai7, D7.hari.kredit, kredit7]));
ok('6: kas per tempat, stok, piutang & utang, pondasi = posisi SEKARANG (sama persis dengan Hari ini)', J(D7.hari.kas) === J(D0.hari.kas) && J(D7.stok) === J(D0.stok) && J(D7.tagihan) === J(D0.tagihan) && J(D7.pondasi) === J(D0.pondasi));
ok('6: 7 hari: nota terbesar & HPP lewat = rentang itu; modal tertahan = rentang itu; target harian tetap hari ini', D7.kpi.nota.rentang === 'saring' && J(D7.kpi.nota.daftar) === J(rwTerbesar('2026-11-12', iso, 3).daftar) && D7.kpi.modal.dari === '2026-11-12' && D7.kpi.target.iso === iso && /sekarang/.test(D7.kpi.periode), J(D7.kpi.periode));
var DL_ = susunDasbor(KINI, 'hari', null, null, S.bulanLalu);
ok('6: Bulan lalu: Bulan ini · Pemicu · Margin · Mutu (merek & susut) · Pelanggan usaha = Oktober; judul kartu = nama bulannya', DL_.bulan.key === '2026-10' && DL_.bulan.judul === lpNamaBulan('2026-10') && DL_.kpi.margin.key === '2026-10' && DL_.mutu.merek.nama === lpNamaBulan('2026-10') && DL_.b2b.nama === lpNamaBulan('2026-10') && DL_.bulan.labaBersih === kendaliBulan('2026-10', KINI).labaBersih, J([DL_.bulan.key, DL_.mutu.merek.nama, DL_.b2b.nama]));
ok('6: Pembelian ikut saringan: Bulan lalu = Okt Rp6.500.000', DL_.beli.saring.rp === 6500000 && DL_.beli.periodeNama === lpNamaBulan('2026-10'), J(DL_.beli.saring));
var kunci = []; var ing = function (k, f) { kunci.push(k); return f(); }; susunDasbor(KINI, 'hari', null, ing, S.h7);
ok('6: ingatan: kelompok yang ikut berkunci saringan, yang tetap berkunci lama (hasil Hari ini terpakai lagi)', kunci.indexOf('hari|saring|' + S.h7.kunci) >= 0 && kunci.indexOf('stok') >= 0 && kunci.indexOf('tagihan') >= 0 && kunci.indexOf('stok|saring|' + S.h7.kunci) < 0, J(kunci));
var Dtb = dbTambahan(DL_, KINI); var HL = dbHeadline(Dtb, []);
ok('6: headline tetap ringkas HARI INI — saringan bulan lain tidak memasukkan laba bulan itu', !HL.bagian.some(function (b) { return b.id === 'laba'; }) && dbHeadline(dbTambahan(susunDasbor(KINI, 'hari'), KINI), []).bagian.some(function (b) { return b.id === 'laba'; }), J(HL.bagian));
var W7 = wgSusun(WG_KATALOG.map(function (k) { return { id: k.id }; }), Object.assign(dbTambahan(D7, KINI), {})); var w = function (id) { return W7.find(function (x) { return x.id === id; }); };
ok('6: angka yang ikut saringan ganti nama periodenya; yang "hari ini" (jam segini) tetap', w('labaKotorHari').nama === 'Laba kotor · 7 hari' && w('labaBersihBulan').nama === 'Laba bersih · ' + lpNamaBulan('2026-11') && w('pembelian').nama === 'Pembelian · 7 hari' && w('omzetHari').nama === 'Omzet hari ini' && w('uangToko').nama === 'Uang toko sekarang' && !W7.some(function (x) { return x.nilai === 'gagal dihitung'; }), J(W7.filter(function (x) { return x.nilai === 'gagal dihitung'; })));
var R1 = lpRekapRentang('2026-11-17', '2026-11-17'), RH = rekapHari('2026-11-17');
ok('6: rekap rentang sehari = rekap harian (omzet, nota, laba kotor, tunai, QRIS, bon, nota bon)', RH.qris > 0 && R1.omzet === RH.omzet && R1.n === RH.n && R1.margin === RH.margin && R1.tunai === RH.tunai && R1.qris === RH.qris && R1.kredit === RH.kredit && R1.nKredit === RH.nKredit, J([R1, { omzet: RH.omzet, n: RH.n, tunai: RH.tunai, kredit: RH.kredit }]));
ok('6: kartu Pembelian di KATALOG (bawaan Dasbor tetap kartu lama, keputusan owner 26 Nov)', WG_KATALOG.some(function (k) { return k.id === 'kBeli' && k.jenis === 'lama'; }) && !WG_BAWAAN.some(function (x) { return x.id === 'kBeli'; }));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Dasbor: satu saringan di atas kisi (pita & tanggal pindah dari kartu Periode), ganti = Dasbor dihitung ulang', 'kisi', ['function htmlSaring()', 'dbSaring(pil, k)', '(atur ? \'\' : htmlSaring())', 'opsi.gantiSaring', 'DB_SARING_TETAP', 'pil: () => Object.assign({}, pil)']),
    ('Dasbor: kartu tetap diberi cap, Pembelian, pos PPh, perkiraan telat, modal tertahan', 'dasbor', ['kBeli: () => kartuBeli(D.beli)', 'function kartuBeli(Bl)', 'data-db-beli', 'tetap()', 'barisPph(B.pph)', 'data-k="db-telat"', 'const MT = Q.modal;', 'saring: () => kisi.pil()', "kepala(H.judul || 'Hari ini'"]),
    ('Ringkasan menyusun Dasbor dengan saringan (juga pemanasan latar)', 'ringkasan', ['dbSaring(dasbor.saring(), k)', 'susunDasbor(k, r, null, ingatDb(k), S)', 'ingatDb(k), saringKini(k))', "dbSaringKunci = 'hari'"]),
    ('Laporan: pos PPh di Biaya + anggarannya · susut per penjaga di Susut & Organisasi', 'laporan', ['KL.klPph(K, kini())', 'data-kunci="anggaran:pph"', '${pph}${kaki}', '${peta}${pph}${impas}', 'SH.shSusutPenjaga(R3.awal, R3.akhir)', "kartuPenjaga(SH.shSusutPenjaga(a, t), '30 hari', 'pd-penjaga')"]),
    ('Pelanggan › Bon › Jatuh tempo: diperkirakan telat', 'pelanggan', ['B.pnPerkiraanTelat(d)', '${gambarTelat(d)}']),
    ('Menu › Target & ambang: bunga modal stok (setelan owner)', 'menu', ["isian('bungaModal'", 'KL.klModalTertahan(d, null, null)', 'KL.KL_BUNGA_BAWAAN']),
    ('CSS saringan, cap tetap, batang pembelian', 'css', ['.layar-ringkasan .db-saring {', '.layar-ringkasan .db-tetap {', '.layar-ringkasan .db-beli-bon {', '.layar-ringkasan .db-beli-langsung {']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_sisa_sensus.py && python3 alat-uji/uji_sisa_sensus.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['Paket sisa sensus', 'shSusutPenjaga', 'pnPerkiraanTelat', 'klPph', 'klModalTertahan', 'dbSaring', 'bungaModalPersen', 'anggaran.pph']),
]
RUSAK = [
    ('lahir buku dihitung pembelian', SH, "if (!b || b.lahirBuku) return { jenis: 'lewat'", "if (!b) return { jenis: 'lewat'"),
    ('kedatangan bon terbaca dibayar langsung', SH, "return { jenis: b.stokAwal || b.tutupBuku ? 'dicatat' : 'beli', rp, kg, bon: batchDiutang(b) };", "return { jenis: b.stokAwal || b.tutupBuku ? 'dicatat' : 'beli', rp, kg, bon: false };"),
    ('bongkar tidak ikut pembelian', SH, "const rp = (b.merkList || []).reduce((a, m) => a + (Number(m && m.subtotalHarga) || 0), 0) + (Number(b.biayaBongkar) || 0);\n  const kg", "const rp = (b.merkList || []).reduce((a, m) => a + (Number(m && m.subtotalHarga) || 0), 0);\n  const kg"),
    ('rework jadi batas rentang jaga', SH, "if (h.batas) sebelum[h.kunci] = h.tanggal;", "sebelum[h.kunci] = h.tanggal;"),
    ('setengah hari dihitung sehari', SH, "const h = peta[t] || (peta[t] = {}); h[nm] = (h[nm] || 0) + v;", "const h = peta[t] || (peta[t] = {}); h[nm] = (h[nm] || 0) + 1;"),
    ('hari hitungan sebelumnya ikut rentang jaga', SH, "const mulai = lalu ? (lalu < h.tanggal ? ugTambahHari(lalu, 1) : h.tanggal)", "const mulai = lalu ? (lalu < h.tanggal ? lalu : h.tanggal)"),
    ('hitungan cocok persis tidak jadi batas', SH, "if (h.batas) sebelum[h.kunci] = h.tanggal; const rp = h.x.nilaiRp;", "const rp = h.x.nilaiRp; if (h.batas && rp) sebelum[h.kunci] = h.tanggal;"),
    ('sekali telat sudah dicap', BL, "biasaTelat: nTelat >= PN_TELAT_MIN,", "biasaTelat: nTelat >= 1,"),
    ('jatuh tempo bon lama digeser seminggu', BL, "new Date((hariKe(b.tanggal) + T.hari) * 86400000).toISOString().slice(0, 10);\n      const telatHari", "new Date((hariKe(b.tanggal) + T.hari + 7) * 86400000).toISOString().slice(0, 10);\n      const telatHari"),
    ('bon yang sudah lewat ikut perkiraan', BL, "if (x.status === 'lewat') { nLewatBiasa += 1; rpLewatBiasa += x.sisa; return; }", "if (x.status === 'lewat') { nLewatBiasa += 1; rpLewatBiasa += x.sisa; }"),
    ('PPh dibanding anggaran sebulan penuh di bulan berjalan', KL, "dasar = K.berjalan ? Math.round(ang * K.hariJalan / K.nHari) : ang;", "dasar = ang;"),
    ('sisihkan tanpa mengurangi setoran', KL, "sisihkan: n === null ? null : Math.max(0, n - setor),", "sisihkan: n,"),
    ('anggaran PPh tidak terbaca', KB, "const a = ugAturDok('kendaliBiaya') || {}; const anggaran = {}; KB_ID_SIMPAN.forEach((id) => {", "const a = ugAturDok('kendaliBiaya') || {}; const anggaran = {}; ID_ANGGARAN.forEach((id) => {"),
    ('bunga modal bawaan 0', KL, "export const KL_BUNGA_BAWAAN = 6;", "export const KL_BUNGA_BAWAAN = 0;"),
    ('biaya modal dibagi 12, bukan hari ÷ 365', KL, "const biaya = bunga > 0 ? rata * bunga / 100 * nHari / 365 : 0;", "const biaya = bunga > 0 ? rata * bunga / 100 / 12 : 0;"),
    ('bunga 0 dianggap bawaan', KL, "const bOwn = bm !== undefined && bm !== null && bm !== '' && isFinite(bn) && bn >= 0 && bn <= KL_BUNGA_MAKS;", "const bOwn = bm !== undefined && bm !== null && bm !== '' && isFinite(bn) && bn > 0 && bn <= KL_BUNGA_MAKS;"),
    ('saringan tidak sampai ke kelompok', DL, "const S = ikut && SR && !SR.bawaan ? SR : null;", "const S = null;"),
    ('saringan ikut ke kartu posisi sekarang', DL, "const ikut = DB_IKUT_SARING.indexOf(kel) >= 0;", "const ikut = true;"),
    ('kartu bulanan memakai bulan tanggal awal', DL, "const bulan = R.id === 'bulanLalu' ? R.dari.slice(0, 7) : R.sampai.slice(0, 7);", "const bulan = R.dari.slice(0, 7);"),
    ('kartu Hari ini tidak disaring', DL, "const R = sar ? lpRekapRentang(SR.dari, SR.sampai) : rekapHari(iso);", "const R = rekapHari(iso);"),
    ('headline memakai laba bulan saringan', DL, "(!Bd || Bd.galat || !Bl.key || Bl.key === String(Bd.iso || '').slice(0, 7))", "true"),
    ('nama angka tidak ikut periode', WG, "labaKotorHari: (S) => 'Laba kotor · ' + S.nama,", "labaKotorHari: (S) => 'Laba kotor hari ini',"),
    ('rekap rentang: tunai bercampur QRIS', LPL, "tunai: K ? K.pos.tunai : null,", "tunai: K ? K.pos.tunai + K.pos.qris : null,"),
]
RUSAK_STATIS = [
    ('saringan tidak digambar di atas kisi', 'kisi', "(atur ? '' : htmlSaring())", "''"),
    ('Ringkasan tanpa saringan', 'ringkasan', 'dbSaring(dasbor.saring(), k)', 'null'),
    ('Biaya tanpa pos PPh', 'laporan', '${pph}${kaki}', '${kaki}'),
    ('Jatuh tempo tanpa perkiraan telat', 'pelanggan', '${gambarTelat(d)}', ''),
    ('Menu tanpa bunga modal', 'menu', "isian('bungaModal'", "isian('bungaX'"),
    ('komentar // menelan kunci objek', 'dasbor', "/* B94: Ringkasan menyusun ulang dengan saringan baru */ simpanWidget:", "// B94: Ringkasan menyusun ulang dengan saringan baru simpanWidget:"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_sisa_sensus.py && python3 alat-uji/uji_sisa_sensus.py --kontrol', 'true'),
]

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var TB = aman('beli', function () { return shTrenBeli('bulan', kini); });
out.beli = TB ? { bulan: TB.batang.length, sama: TB.batang.every(function (b) { var H = shHppPeriode(b.id, kini); return b.absen || (Math.round(b.rp) === Math.round(H.beli) && b.n === H.nBeli); }), nBon: TB.batang.reduce(function (a, b) { return a + b.nBon; }, 0), n: TB.n } : null;
var a3 = shRentang3(kini); var SP = aman('penjaga', function () { return shSusutPenjaga(a3.awal, a3.akhir); });
out.penjaga = SP ? { baris: SP.nBaris, menutup: SP.menutup, samaLaporan: Math.abs(SP.total - susutRentang(a3.awal, a3.akhir).mesin) < 0.5, orang: SP.orang.filter(function (g) { return !g.tanpa; }).length, tanpaBaris: (SP.orang.find(function (g) { return g.tanpa; }) || { nBaris: 0 }).nBaris } : null;
var PT = aman('telat', function () { return pnPerkiraanTelat(kini); }); out.telat = PT ? { n: PT.n, lewat: PT.nLewatBiasa, tanpa: PT.nTanpaRiwayat } : null;
var K = aman('kendali', function () { return kendaliBulan(iso.slice(0, 7), kini); }); var PP = K ? aman('pph', function () { return klPph(K, kini); }) : null; out.pph = PP ? { keadaan: PP.keadaan, teks: PP.n === null ? PP.teks : 'ada' } : null;
var MT = aman('modal', function () { return klModalTertahan(kini, iso.slice(0, 8) + '01', iso); });
var U = aman('um', function () { return umNilaiRata(iso.slice(0, 8) + '01', iso); }); var uk = U ? Object.keys(U.buku).reduce(function (a, k) { return a + U.buku[k].rp; }, 0) : null;
out.modal = MT ? { hari: MT.nHari, bunga: MT.bunga, bawaan: !MT.dariOwner, karungDiAtasGmroi: uk !== null && MT.rata >= uk - 0.5, nBuku: MT.buku.length } : null;
out.saring = {}; ['hari', 'kemarin', 'h7', 'bulan', 'bulanLalu', 'tahun'].forEach(function (id) { var S = dbSaring({ id: id }, kini); var D = aman('susun ' + id, function () { return dbTambahan(susunDasbor(kini, 'hari', null, null, S), kini); });
  var Wd = D ? aman('wg ' + id, function () { return wgSusun(WG_KATALOG.map(function (k) { return { id: k.id }; }), D); }) : null;
  out.saring[id] = D && Wd ? { galat: Object.keys(D).filter(function (k) { return D[k] && D[k].galat; }), wgGalat: Wd.filter(function (w) { return w.nilai === 'gagal dihitung'; }).map(function (w) { return w.id; }) } : 'gagal'; });
var D0 = aman('bawaan', function () { return susunDasbor(kini, 'hari'); }); var DH = aman('bawaan hari', function () { return susunDasbor(kini, 'hari', null, null, dbSaring({ id: 'hari' }, kini)); });
out.hariSama = D0 && DH ? ['hari', 'bulan', 'kpi', 'mutu', 'b2b', 'beli'].every(function (k) { return JSON.stringify(D0[k]) === JSON.stringify(DH[k]); }) : false;
var t = ugTambahHari(iso, -1); var RR = aman('rekap', function () { var a = lpRekapRentang(t, t), b = rekapHari(t); return a.omzet === b.omzet && a.tunai === b.tunai && a.qris === b.qris && a.kredit === b.kredit && a.n === b.n; }); out.rekapSama = RR;
print(JSON.stringify(out));
"""


def bundel_js(teks):
    return uji_dasbor_sensus.bundel_js(teks)


def jalan(teks):
    jam = "var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def komentar_ekor(baris):
    """Teks sesudah // pertama yang BUKAN di dalam string ('…', "…", `…`) dan bukan bagian URL / regex sederhana; '' bila tidak ada."""
    q = None; i = 0; n = len(baris)
    while i < n - 1:
        c = baris[i]
        if q:
            if c == '\\': i += 2; continue
            if c == q: q = None
        elif c in '\'"`': q = c
        elif c == '/' and baris[i + 1] == '/' and (i == 0 or baris[i - 1] != ':'):
            return baris[i + 2:] if baris[:i].strip() else ''
        i += 1
    return ''


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # setelan baru memakai dokumen yang SUDAH ada (aturanToko/kpiLaba & kendaliBiaya) — tidak ada pintu tulis baru di modul logika paket ini
    if src['kl'].count("koleksi: 'aturanToko'") != 1: g.append('kpi-laba-logika: pintu tulis bertambah (paket ini tanpa tulisan baru)')
    if src['sh'].count("koleksi: 'aturanToko'") != 1 or src['sh'].count('koleksi:') != 1: g.append('susut-harga-logika: pintu tulis bertambah (paket ini tanpa tulisan baru)')
    for k in ('kl', 'sh', 'dl', 'wg'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    # pola cacat lama (memori "komentar // menelan kode"): komentar // di tengah baris yang masih diikuti kode (kunci objek, pernyataan, panah) — mis. B94 sempat menelan
    # `simpanWidget:` di dasbor.js (simpan susunan Dasbor gagal di peramban; jsc tidak menjalankan dasbor.js, jadi uji lain diam)
    for k in ('dasbor', 'kisi', 'ringkasan', 'laporan', 'pelanggan', 'menu', 'kl', 'sh', 'dl', 'wg'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    i = src['baca'].find('Paket sisa sensus')
    # hanya bagian paket ini (sampai judul ## berikutnya) — bagian paket lain sesudahnya (mis. Tanggal janji, rules v24) bukan urusan penjaga ini
    j = src['baca'].find('\n## ', i + 1) if i >= 0 else -1; bag = src['baca'][i:j if j > i else i + 6000] if i >= 0 else ''
    if i >= 0 and ('rules v24' in bag or 'firestore.rules' in bag): g.append('BACA-DULU menyebut rules untuk paket ini (paket ini tanpa rules)')
    return len(STATIS) - len([x for x in g if ' → ' in x]), g


def muat():
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in MODUL), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read() if os.path.exists(os.path.join(AKAR, v)) else '') for k, v in SUMBER.items())


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
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
        r, out = uji_dasbor_sensus.jsc("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = (not h['galat'] and h['beli'] and h['beli']['sama'] and h['penjaga'] and h['penjaga']['menutup'] and h['penjaga']['samaLaporan'] and h['telat'] is not None and h['pph'] and h['modal']
                     and all(isinstance(v, dict) and not v['galat'] and not v['wgGalat'] for v in h['saring'].values()) and h['hariSama'] and h['rekapSama'])
            # angka rupiah toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: pembelian ≠ HPP periode, susut per penjaga tidak menutup, saringan galat, atau saringan Hari ini ≠ Dasbor lama')
    sys.exit(1 if g or gs else 0)
