#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_rapor_bulan.py — PAKET P2 (sensus 27 Nov 2026: A109 A110 A111 A136 B4 B26 B110 B112 B124). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  A109 target bulanan + ANGKA KHUSUS per bulan (aturanToko/anggaranBulan): parse, tolak berkalimat, khusus menimpa bulan itu saja, simpan satu ketukan (2 dokumen
       hanya bila target / angka khusus berubah); lampu min / maks / jatah sampai hari ke-N; acuan terukur hanya mengisi formulir.
  A110 anggaran vs aktual SEMUA pos + sebab & tindakan per pos (aturanToko/anggaranCatatan): tulis / ubah / hapus, tolak pos asing & bulan depan.
  A111 pecahan selisih laba kotor: volume · harga jual · harga beli — Σ = laba kotor − anggaran laba kotor PERSIS; susut di bawahnya; target kurang = disebut.
  A136 B112 lembar KPI bulanan / scorecard: ini · bulan lalu · % ubah (bulan berjalan lewat perkiraan sebulan) · target; mode Kas = arus kas mesin.
  B4 penjualan kotor = bersih + potongan nota + tawar + retur; per hari (satu lintasan) Σ = bulan; pjPotonganHarian Σ = pjPotonganBulan.
  B26 arus kas bulan ini = intiBulan (Laporan › Bulanan) + rincian; kartu & saklar di Dasbor.
  B110 B124 lampu target owner menempel ke margin %, piutang, karcis belum dirinci, laba kotor hari ini (laju jam) — tanpa target = seperti dulu.
  Mesin uang TIDAK berubah: laba bersih, Σ biaya & titik impas sama persis dengan / tanpa target.

    python3 alat-uji/uji_rapor_bulan.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_rapor_bulan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus, uji_susut_harga  # noqa: E402
RB = 'baru/js/layar/rapor-bulan-logika.js'; KB = 'baru/js/layar/kendali-biaya-logika.js'; PJ = 'baru/js/layar/pajak-logika.js'; LPL = 'baru/js/layar/laporan-logika.js'
DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'
MODUL = uji_dasbor_sensus.MODUL
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'css': 'baru/css/ringkasan.css', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md',
          'rs': 'baru/js/layar/riwayat-setelan-logika.js', 'bundel': 'alat-uji/bundel_baru.py', 'peta': 'alat-uji/peta_akses.py', 'rb': RB, 'kb': KB, 'dl': DL, 'wg': WG}

KARUNG = uji_susut_harga.KARUNG
KOTAK = json.loads(json.dumps(uji_sisa_sensus.KOTAK))
# B4: satu nota November dengan potongan nota Rp5.000 + tawar di bawah harga daftar (harga daftar 13.000, jadi 12.500/kg) · satu nota Oktober berpotongan
p1 = KARUNG('pt1', '2026-11-12', 'Kembang', 10, 125000, 120000); p1.update({'potonganTransaksi': 5000, 'hargaAsliSatuan': 13000, 'negoSelisih': -500, 'pembulatan': 0})
p2 = KARUNG('pt2', '2026-10-08', 'Kembang', 10, 128000, 120000); p2.update({'potonganTransaksi': 2000, 'pembulatan': 0})
# kelebihan bayar (bayar > bon) — sisa minus BUKAN piutang (mesin & neraca menyaring sisa > 0) · satu nota hari ini (laba kotor hari ini > 0 untuk lampu laju jam)
lb = KARUNG('lb1', '2026-11-03', 'Kembang', 2, 26000, 24000); lb.update({'caraBayar': 'Kredit', 'namaPelanggan': 'Pelanggan Contoh L'})
KOTAK['penjualan'] = KOTAK['penjualan'] + [p1, p2, lb, KARUNG('h1', '2026-11-18', 'Angsa', 10, 130000, 120000)]
KOTAK['piutangMutasi'] = KOTAK['piutangMutasi'] + [{'id': 521, 'tipe': 'bayar', 'namaPelanggan': 'Pelanggan Contoh L', 'nominal': 40000, 'tanggal': '2026-11-05', 'jam': '10:00', 'caraBayar': 'Tunai', 'dicatatDi': 'sistem'}]
# retur uang (refund tunai) 13 Nov Rp20.000 — mengurangi omzet mesin & ikut "retur" di kotor → bersih
KOTAK['retur'] = [{'id': 'rt1', 'tanggal': '2026-11-13', 'jam': '12:00', 'jenisAsal': 'karung', 'merkSumber': 'Kembang', 'totalKg': 2, 'kondisi': 'utuh', 'alasan': 'contoh', 'nominalRefund': 20000, 'trxIdAsal': 'pt1', 'caraKembali': 'tunai'}]
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

// ==================== 1 · ANGKA SATU BULAN = SUMBERNYA ====================
var X = rbBulan('2026-11', KINI), XO = rbBulan('2026-10', KINI); var K = kendaliBulan('2026-11', KINI); var P = pemicuBiaya(K); var M = klMarginBulan('2026-11', KINI);
var PT = pjPotonganBulan('2026-11'); var I = intiBulan('2026-11', KINI);
ok('1: omzet, laba kotor, biaya, laba bersih, kg = kendaliBulan (Laporan › Biaya, mesin laba)', X.omzet === K.omzet && X.labaKotor === K.margin && X.biaya === K.semuaBiaya && X.labaBersih === K.labaBersih && X.kg === K.kgTerjual && X.berjalan && X.hariJalan === 18 && X.nHari === 30, J([X.omzet, K.omzet]));
ok('1: HPP/kg = pemicu "HPP per kg terjual" · margin kotor % = Laporan › Laba (klMarginBulan)', dekat(X.hppKg, (P.baris.find(function (r) { return r.id === 'hppKg'; }) || {}).n, 0.06) && dekat(X.marginKotor, M.tangga.find(function (t) { return t.id === 'kotor'; }).pct, 1e-9), J([X.hppKg, X.marginKotor]));
ok('1: penjualan kotor = bersih + potongan nota + tawar + retur (Rp5.000 potongan · tawar Rp5.000 dari 130.000 × 500 ÷ 12.500 · retur Rp20.000)', PT.nota === 5000 && PT.tawar === 5200 && X.retur === 20000 && X.kotor === X.omzet + 20000 + 10200 && dekat(X.potPct, 10200 / X.kotor * 100, 1e-9), J([PT, X.retur, X.kotor, X.omzet]));
var Hp = hitungPiutang(iso).filter(function (x) { return x.sisa > 0; });
ok('1: ada kelebihan bayar (sisa minus) di mesin — tidak ikut piutang', hitungPiutang(iso).some(function (x) { return x.sisa < 0; }), J(hitungPiutang(iso).map(function (x) { return x.sisa; })));
var DSn = pnDsoPada(iso);
ok('1: piutang akhir bulan (berjalan: hari ini) = sisa bon mesin (sama dengan neraca) · lama piutang = pnDsoPada hari ini (P1, satu rumus dengan Dasbor)', X.piutang === Hp.reduce(function (a, x) { return a + x.sisa; }, 0) && X.piutang > 0 && X.bon === I.kredit && DSn.dso !== null && X.dso === DSn.dso && X.piutang === DSn.piutang, J([X.piutang, X.bon, X.dso, DSn]));
var MT = klModalTertahan(KINI, '2026-11-01', iso); var SRk = klStokRp(KINI, '2026-11-01', iso);
ok('1: perputaran (disetahunkan) & hari stok = klStokRp (P1, satu sumber dengan Dasbor) · nilai stok rata-rata = klModalTertahan', SRk.putaranTahun !== null && X.perputaran === SRk.putaranTahun && X.hariStok === SRk.hari && X.rataStok === MT.rata && X.stokStatus === SRk.status, J([X.perputaran, X.hariStok, SRk.status]));
var bHs = rbRapor('2026-11', KINI).baris.find(function (x) { return x.id === 'hariStok'; });
ok('1: hari stok berlampu dari target Stok › Umur (pas = hijau, tipis / diam = kuning) · masuk tabel anggaran vs aktual', bHs.lampu === (SRk.status === 'pas' ? 'hijau' : 'amber') && /target/.test(bHs.targetTeks) && rbAnggaranAktual('2026-11', KINI).baris.some(function (r) { return r.id === 'hariStok'; }), J(bHs));
ok('1: arus kas = intiBulan (Laporan › Bulanan) · susut % = susutRentang (Per merek)', X.masuk === I.masuk && X.keluar === I.keluar && X.kasBersih === I.bersih && X.susutPct === (susutRentang('2026-11-01', iso).susut || {}).pct, J([X.masuk, I.masuk]));

// ==================== 2 · B4 KOTOR vs BERSIH PER HARI ====================
var PH = pjPotonganHarian('2026-11'); var tot = Object.keys(PH.hari).reduce(function (a, t) { return a + PH.hari[t].jumlah; }, 0);
ok('2: potongan per hari: Σ hari = pjPotonganBulan (nota, tawar, jumlah, n) · 12 Nov Rp10.200', tot === PT.jumlah && PH.nota === PT.nota && PH.tawar === PT.tawar && PH.n === PT.n && PH.hari['2026-11-12'].jumlah === 10200, J([PH, PT]));
var HB = lpHariBulan('2026-11'); var sOm = Object.keys(HB).reduce(function (a, t) { return a + HB[t].omzet; }, 0); var sRt = Object.keys(HB).reduce(function (a, t) { return a + HB[t].retur; }, 0);
ok('2: omzet per hari (satu lintasan): Σ = omzet mesin bulan itu · retur 13 Nov · hari = rekap harian', sOm === K.omzet && sRt === 20000 && HB['2026-11-13'].retur === 20000 && HB['2026-11-12'].omzet === rekapHari('2026-11-12').omzet && HB['2026-11-12'].nota === rekapHari('2026-11-12').n, J([sOm, K.omzet, sRt]));
var KB_ = rbKotorBersih('2026-11', KINI);
ok('2: kartu kotor → bersih menutup: Σ hari bersih = omzet, Σ potongan = bulan, Σ retur = bulan; tangga kotor − potongan − tawar − retur = bersih', KB_.menutup === true && KB_.tangga[0].n + KB_.tangga[1].n + KB_.tangga[2].n + KB_.tangga[3].n === KB_.tangga[4].n && KB_.terbesar.iso === '2026-11-12' && KB_.hari[0].iso >= KB_.hari[KB_.hari.length - 1].iso, J(KB_.tangga));
ok('2: Oktober: potongan Rp2.000 · kotor = bersih + 2.000 (tanpa retur)', XO.potongan === 2000 && XO.kotor === XO.omzet + 2000 && rbKotorBersih('2026-10', KINI).menutup === true, J([XO.potongan, XO.kotor, XO.omzet]));

// ==================== 3 · A109 TARGET & ANGKA KHUSUS ====================
var A0 = aturAnggaranBulan();
ok('3: bawaan = belum diatur (semua target 0, tanpa angka khusus); aturKendaliBulan = aturKendali', A0.nTarget === 0 && !A0.dariOwner && J(aturKendaliBulan('2026-11').anggaran) === J(aturKendali().anggaran) && J(aturKendaliBulan('2026-11').khusus) === '{}', J(A0));
var d0 = drafAturSemua('2026-11'); d0.target.kgTerjual = '600'; d0.target.marginKotor = '8,5'; d0.target.hppKg = '12.000'; d0.target.piutangAkhir = '100.000'; d0.target.karcisBelum = '3'; d0.target.labaKotor = '900.000';
var s1 = susunAturSemua(d0, W);
ok('3: simpan target = 2 dokumen (kendaliBiaya apa adanya + anggaranBulan) · koma & titik ribuan terbaca', !s1.tolak && s1.dokumen.length === 2 && s1.dokumen[0].data.id === 'kendaliBiaya' && s1.dokumen[1].data.id === 'anggaranBulan' && s1.dokumen[1].data.target.marginKotor === 8.5 && s1.dokumen[1].data.target.hppKg === 12000 && s1.dokumen[1].data.target.kgTerjual === 600 && /6 target bulanan/.test(s1.patch.kabar), J(s1));
var d1 = drafAturSemua('2026-11'); var s0 = susunAturSemua(d1, W);
ok('3: tanpa ubahan target = HANYA kendaliBiaya (anggaranBulan tidak ditulis ulang)', !s0.tolak && s0.dokumen.length === 1 && s0.dokumen[0].data.id === 'kendaliBiaya', J(s0));
var tl = function (k, v) { var d = drafAturSemua('2026-11'); d.target[k] = v; return susunAturSemua(d, W).tolak || ''; };
ok('3: ketikan rusak DITOLAK berkalimat: huruf · minus · margin > 100 % · karcis pecahan', /angka saja/.test(tl('omzet', 'sejuta')) && /angka saja/.test(tl('kgTerjual', '-5')) && /terlalu besar/.test(tl('marginKotor', '120')) && /bulat/.test(tl('karcisBelum', '2,5')), [tl('omzet', 'sejuta'), tl('marginKotor', '120'), tl('karcisBelum', '2,5')]);
aturDengan([s1.dokumen[1].data]);
var T1 = targetBulan('2026-11'), T0 = targetBulan('2026-10');
ok('3: target umum berlaku tiap bulan (Nov & Okt sama)', T1.kgTerjual.nilai === 600 && T0.kgTerjual.nilai === 600 && !T1.kgTerjual.khusus && T1.omzet.nilai === 0, J([T1, T0]));
var d2 = drafAturSemua('2026-11'); d2.khususNyala = true; d2.khususA.angkut = '50.000'; d2.khususA.susut = '0'; d2.khususT.kgTerjual = '900'; d2.khususT.hppKg = '';
var s2 = susunAturSemua(d2, W); aturDengan([s2.dokumen[1].data]);
ok('3: angka khusus Nov: kg 900 (kosong = ikut umum, 0 = mati bulan itu) · tersimpan perBulan', !s2.tolak && J(s2.dokumen[1].data.perBulan['2026-11']) === J({ anggaran: { angkut: 50000, susut: 0 }, target: { kgTerjual: 900 } }) && /angka khusus November 2026/.test(s2.patch.kabar), J(s2.dokumen[1].data));
var T1b = targetBulan('2026-11'), T0b = targetBulan('2026-10'); var AKn = aturKendaliBulan('2026-11'), AKo = aturKendaliBulan('2026-10');
ok('3: khusus menimpa NOVEMBER saja: target kg 900 (khusus) · HPP/kg tetap umum · Oktober tetap umum', T1b.kgTerjual.nilai === 900 && T1b.kgTerjual.khusus && T1b.hppKg.nilai === 12000 && !T1b.hppKg.khusus && T0b.kgTerjual.nilai === 600 && !T0b.kgTerjual.khusus, J([T1b, T0b]));
ok('3: anggaran biaya khusus Nov: angkut 50.000 & susut 0 (mati) di Nov; Okt = anggaran umum', AKn.anggaran.angkut === 50000 && AKn.anggaran.susut === 0 && AKn.khusus.angkut && AKo.anggaran.angkut === aturKendali().anggaran.angkut && !AKo.khusus.angkut, J([AKn.anggaran, AKo.anggaran]));
var Kn = kendaliBulan('2026-11', KINI); var rA = Kn.baris.find(function (r) { return r.id === 'angkut'; });
ok('3: Peta biaya Nov memakai angka khusus (lampu menyala, kalimat menyebut "angka khusus")', rA.anggaran === 50000 && rA.lampu !== 'tanpa' && rA.khusus && /angka khusus November 2026/.test(rA.lampuTeks), J([rA.anggaran, rA.lampuTeks]));
var d3 = drafAturSemua('2026-11'); ok('3: draf Atur membawa angka khusus yang tersimpan (formulir terisi)', d3.khususNyala && d3.khususT.kgTerjual === '900' && d3.khususA.angkut === '50000' && d3.khususA.susut === '0' && d3.khususT.hppKg === '', J(d3));
d3.khususNyala = false; var s3 = susunAturSemua(d3, W);
ok('3: angka khusus dimatikan = dihapus, bulan itu ikut angka umum lagi', !s3.tolak && !s3.dokumen[1].data.perBulan['2026-11'] && /dihapus/.test(s3.patch.kabar), J(s3.dokumen[1].data));
var d4 = drafAturSemua('2027-12'); d4.khususNyala = true; d4.khususT.omzet = '1000';
ok('3: angka khusus paling jauh 12 bulan ke depan', /12 bulan/.test(susunAturSemua(d4, W).tolak || ''), J(susunAturSemua(d4, W)));
var Kc = kendaliBulan('2026-11', KINI); aturDengan([]); var Kb = kendaliBulan('2026-11', KINI);
ok('3: mesin TIDAK berubah: laba bersih, Σ biaya, titik impas sama dengan / tanpa target (yang berubah cuma lampu)', Kc.labaBersih === Kb.labaBersih && Kc.semuaBiaya === Kb.semuaBiaya && titikImpas(Kc, KINI).omzetImpas === titikImpas(Kb, KINI).omzetImpas, J([Kc.labaBersih, Kb.labaBersih]));

// ==================== 4 · LAMPU TARGET ====================
var ctx = { berjalan: true, hariJalan: 18, nHari: 30 };
var Lm = function (akt) { return kbLampuTarget({ arah: 'min', jalan: true }, 1000, akt, ctx, 10).lampu; }; var Lx = function (akt) { return kbLampuTarget({ arah: 'maks', jalan: false }, 1000, akt, ctx, 10).lampu; };
ok('4: target min bulan berjalan = jatah sampai hari ke-18 (600): 600 hijau · 540 amber · 539 merah', Lm(600) === 'hijau' && Lm(540) === 'amber' && Lm(539) === 'merah' && kbLampuTarget({ arah: 'min', jalan: true }, 1000, 600, ctx, 10).dasar === 600, [Lm(600), Lm(540), Lm(539)]);
ok('4: batas maks: 1.000 hijau · 1.100 amber · 1.101 merah · tanpa target = tanpa · angka belum ada = belum', Lx(1000) === 'hijau' && Lx(1100) === 'amber' && Lx(1101) === 'merah' && kbLampuTarget({ arah: 'maks' }, 0, 5, ctx, 10).lampu === 'tanpa' && kbLampuTarget({ arah: 'maks' }, 9, null, ctx, 10).lampu === 'belum', [Lx(1000), Lx(1100), Lx(1101)]);

// ==================== 5 · A136 B112 RAPOR (SCORECARD) ====================
aturDengan([s1.dokumen[1].data]);
var R = rbRapor('2026-11', KINI, 'laba'); var b = function (id) { return R.baris.find(function (x) { return x.id === id; }); };
ok('5: bulan berjalan: angka menumpuk dibanding Okt lewat PERKIRAAN SEBULAN (omzet × 30 ÷ 18) — disebut perkiraan', b('omzet').perkiraan && dekat(b('omzet').pembanding, X.omzet / 18 * 30, 1e-6) && dekat(b('omzet').ubah, (X.omzet / 18 * 30 - XO.omzet) / Math.abs(XO.omzet) * 100, 1e-9) && /perkiraan sebulan/.test(R.kalimat), J(b('omzet')));
ok('5: rasio (margin %, HPP/kg) & posisi (piutang) dibanding langsung — bukan perkiraan', !b('marginKotor').perkiraan && dekat(b('marginKotor').ubah, (X.marginKotor - XO.marginKotor) / Math.abs(XO.marginKotor) * 100, 1e-9) && !b('piutangAkhir').perkiraan && b('piutangAkhir').pembanding === X.piutang, J([b('marginKotor'), b('piutangAkhir')]));
var Lk = kbLampuTarget(AB_TARGET.find(function (t) { return t.id === 'kgTerjual'; }), 600, X.kg, ctx, 10);
ok('5: lampu kg terjual = jatah sampai hari ke-18 dari target 600 kg (360 kg) · target teks menyebutnya', b('kgTerjual').lampu === Lk.lampu && b('kgTerjual').dasar === 360 && /sampai hari ke-18/.test(b('kgTerjual').targetTeks), J(b('kgTerjual')));
ok('5: laba bersih bulan berjalan dibanding target lewat laba bersih SAMPAI HARI INI (titik impas)', b('labaBersih').target === null && b('labaBersih').lampu === 'tanpa', J(b('labaBersih')));
ok('5: membaik/memburuk ikut arah baik (HPP/kg turun = membaik)', b('hppKg').baik === 'turun' && (b('hppKg').ubah === null || b('hppKg').membaik === (b('hppKg').ubah < 0)));
var KCn = daftarKarcis(KINI).nKarcis; var sk = R.sekarang.find(function (x) { return x.id === 'karcisBelum'; });
ok('5: posisi sekarang: karcis belum dirinci (batas 3 karcis) & siklus uang — hanya bulan berjalan', sk && sk.ini === KCn && sk.lampu === kbLampuTarget({ arah: 'maks' }, 3, KCn, null, 10).lampu && R.sekarang.some(function (x) { return x.id === 'siklus'; }) && rbRapor('2026-10', KINI).sekarang.length === 0, J(R.sekarang));
var RK = rbRapor('2026-11', KINI, 'kas'); var bk = function (id) { return RK.baris.find(function (x) { return x.id === id; }); };
ok('5: mode KAS: uang masuk / keluar / kas bersih / jual bon = intiBulan; laba bersih pembanding; posisi sekarang (karcis) tidak ikut lampunya', RK.mode === 'kas' && RK.sekarang.length === 0 && RK.merah + RK.amber + RK.hijau === 0 && bk('masuk').ini === I.masuk && bk('keluar').ini === I.keluar && bk('kasBersih').ini === I.bersih && bk('bon').ini === I.kredit && bk('labaBersihKas').ini === K.labaBersih, J(RK.baris.map(function (x) { return [x.id, x.ini]; })));
ok('5: % ubah: lalu 0 / tidak ada = —, laba minus membaik terbaca naik (penyebut |lalu|)', rbUbah(5, 0) === null && rbUbah(-50, -100) === 50 && rbUbahTeks(null) === '—', [rbUbah(-50, -100)]);

// ==================== 6 · A110 ANGGARAN vs AKTUAL + SEBAB & TINDAKAN ====================
var c1 = susunCatatanPos('2026-11', 'kgTerjual', 'hujan seminggu', 'antar ke warung langganan', W);
ok('6: tulis sebab & tindakan satu pos satu bulan = 1 dokumen aturanToko/anggaranCatatan', !c1.tolak && c1.dokumen.length === 1 && c1.dokumen[0].data.id === 'anggaranCatatan' && c1.dokumen[0].data.bulan['2026-11'].kgTerjual.sebab === 'hujan seminggu' && c1.patch.catAb === null, J(c1));
ok('6: pos asing · bulan depan · terlalu panjang · tanpa isi DITOLAK', !!susunCatatanPos('2026-11', 'apaSaja', 'x', 'y', W).tolak && /belum berjalan/.test(susunCatatanPos('2026-12', 'kgTerjual', 'x', '', W).tolak) && !!susunCatatanPos('2026-11', 'upah', new Array(202).join('a'), '', W).tolak && !!susunCatatanPos('2026-11', 'upah', '', '', W).tolak);
aturDengan([s1.dokumen[1].data, c1.dokumen[0].data]);
ok('6: tidak ada yang diubah = ditolak; dua-duanya kosong = hapus pos itu', /Tidak ada yang diubah/.test(susunCatatanPos('2026-11', 'kgTerjual', 'hujan seminggu', 'antar ke warung langganan', W).tolak) && !susunCatatanPos('2026-11', 'kgTerjual', '', '', W).dokumen[0].data.bulan['2026-11'], J(susunCatatanPos('2026-11', 'kgTerjual', '', '', W)));
var AA = rbAnggaranAktual('2026-11', KINI); var aa = function (kel, id) { return AA.baris.find(function (r) { return r.kel === kel && r.id === id; }); };
ok('6: tabel memuat biaya per jenis (Peta biaya), PPh, dan pos target (kg, HPP/kg, piutang, margin, laba kotor, karcis, susut %)', aa('biaya', 'upah') && aa('biaya', 'susut') && aa('pajak', 'pph') && ['kgTerjual', 'hppKg', 'piutangAkhir', 'marginKotor', 'labaKotor', 'karcisBelum', 'susutPct', 'omzet', 'potonganPct', 'labaBersih'].every(function (id) { return aa('target', id); }), J(AA.baris.map(function (r) { return r.kel + ':' + r.id; })));
ok('6: sebab & tindakan menempel ke posnya; aktual baris biaya = Peta biaya', aa('target', 'kgTerjual').catatan && aa('target', 'kgTerjual').catatan.tindakan === 'antar ke warung langganan' && aa('biaya', 'upah').aktual === K.baris.find(function (r) { return r.id === 'upah'; }).pakai && R.baris.length > 0, J(aa('target', 'kgTerjual')));
ok('6: pos lewat / mendekati yang belum diberi sebab dihitung & disebut', AA.awas === AA.baris.filter(function (r) { return r.lampu === 'merah' || r.lampu === 'amber'; }).length && AA.tanpaSebab === AA.baris.filter(function (r) { return (r.lampu === 'merah' || r.lampu === 'amber') && !r.catatan; }).length, J([AA.awas, AA.tanpaSebab, AA.kalimat]));

// ==================== 7 · A111 PECAHAN SELISIH ====================
aturDengan([]);
var PS0 = rbPecahSelisih('2026-11', KINI);
ok('7: tanpa target kg / HPP/kg / margin = tidak dipecah, yang kurang DISEBUT', !PS0.ada && PS0.kurang.length === 3 && /kg terjual/.test(PS0.kalimat), J(PS0));
aturDengan([{ id: 'anggaranBulan', target: { kgTerjual: 600, hppKg: 12000, marginKotor: 8 }, perBulan: {} }, { id: 'kendaliBiaya', anggaran: { susut: 30000 }, ambang: 10, ambangPemicu: 10, kata: {} }]);
var PS = rbPecahSelisih('2026-11', KINI); var X2 = rbBulan('2026-11', KINI); var jB = 12000 / 0.92, mB = jB - 12000, kgB = 360, kgA = X2.kgHitung;
ok('7: anggaran laba kotor = 360 kg (600 × 18/30) × (12.000 ÷ 0,92 − 12.000)', PS.ada && dekat(PS.anggaran, kgB * mB, 1e-6) && dekat(PS.dasar.jB, jB, 1e-9), J(PS.dasar));
var vol = (kgA - kgB) * mB, hj = kgA * (X2.omzetHitung / kgA - jB), hb = kgA * (12000 - X2.hpp / kgA);
ok('7: volume = (kg − 360) × laba kotor anggaran/kg · harga jual = kg × (jual − jual anggaran) · harga beli = kg × (batas − HPP)', dekat(PS.bagian[0].n, vol, 1e-6) && dekat(PS.bagian[1].n, hj, 1e-6) && dekat(PS.bagian[2].n, hb, 1e-6), J(PS.bagian));
ok('7: Σ tiga bagian = laba kotor mesin − anggaran PERSIS (menutup)', PS.menutup && dekat(PS.bagian[0].n + PS.bagian[1].n + PS.bagian[2].n, X2.labaKotor - PS.anggaran, 1e-6) && PS.aktual === X2.labaKotor, J([PS.sisa]));
var rS = kendaliBulan('2026-11', KINI).baris.find(function (r) { return r.id === 'susut'; });
ok('7: kuantitas (susut) = anggaran susut Peta biaya − susut & selisih stok, di bawah laba kotor', PS.susut && PS.susut.anggaran === rS.dasar && PS.susut.aktual === rS.pakai && PS.susut.selisih === rS.dasar - rS.pakai, J(PS.susut));
aturDengan([]);

// ==================== 8 · ACUAN TERUKUR (formulir) ====================
var dA = drafAturSemua('2026-11'); dA.target.kgTerjual = '777'; var AC = rbDrafAcuanTarget('2026-11', KINI, dA);
var bulanAc = ['2026-10', '2026-09'].map(function (k) { return rbBulan(k, KINI); }).filter(function (x) { return !x.tanpaCatatan; }); var om = bulanAc.map(function (x) { return x.omzet; }).sort(function (a, b) { return a - b; });
var med = om.length % 2 ? om[(om.length - 1) / 2] : (om[om.length / 2 - 1] + om[om.length / 2]) / 2;
ok('8: acuan = median bulan selesai sebelumnya (dibulatkan ribuan) · ketikan owner TIDAK ditimpa · karcis tanpa acuan · tidak menyimpan apa pun', AC.n > 0 && AC.draf.target.omzet === String(Math.round(med / 1000) * 1000) && AC.draf.target.kgTerjual === '777' && !AC.draf.target.karcisBelum && !AC.dokumen, J([AC.draf.target, med, AC.bulan]));

// ==================== 9 · DASBOR (B26 B110 B112 B124) ====================
var D0 = dbTambahan(susunDasbor(KINI, 'hari'), KINI);
ok('9: susunDasbor memuat kelompok rapor (ikut dipanaskan & ikut saringan)', D0.rapor && !D0.rapor.galat && D0.rapor.key === '2026-11' && DB_PANAS.indexOf('rapor') >= 0 && DB_IKUT_SARING.indexOf('rapor') >= 0 && susunDasbor(KINI, 'bulan', D0).rapor === D0.rapor, J(D0.rapor && D0.rapor.galat));
var DLl = susunDasbor(KINI, 'hari', null, null, dbSaring({ id: 'bulanLalu' }, KINI));
ok('9: saringan Bulan lalu → rapor Oktober vs September; lampu laba kotor hari ini tidak dihitung', DLl.rapor.key === '2026-10' && DLl.rapor.laba.namaLalu === lpNamaBulan('2026-09') && !(DLl.rapor.ambang && DLl.rapor.ambang.labaHari), J([DLl.rapor.key]));
var Wd = wgSusun(WG_KATALOG.map(function (k) { return { id: k.id }; }), D0); var w = function (id) { return Wd.find(function (x) { return x.id === id; }); };
ok('9: widget Penjualan kotor & Kas bersih bulan ini = rapor apa adanya', w('penjualanKotor').nilai === RP(X.kotor) && w('kasBulan').nilai === RP(I.bersih) && !Wd.some(function (x) { return x.nilai === 'gagal dihitung'; }), J([w('penjualanKotor'), w('kasBulan')]));
ok('9: tanpa target owner: margin, piutang, karcis, laba kotor hari ini TANPA lampu (seperti dulu)', !w('marginBulan').lampu && !w('piutangTotal').lampu && !w('karcis').lampu && !w('labaKotorHari').lampu, J([w('marginBulan').lampu, w('piutangTotal').lampu]));
ok('9: kartu Rapor bulan & Arus kas ada di KATALOG, TIDAK di bawaan (owner: "Lu tambah sendiri")', WG_KATALOG.some(function (k) { return k.id === 'kRapor' && k.jenis === 'lama'; }) && WG_KATALOG.some(function (k) { return k.id === 'kArusKas'; }) && !WG_BAWAAN.some(function (x) { return x.id === 'kRapor' || x.id === 'kArusKas'; }));
aturDengan([{ id: 'anggaranBulan', target: { marginKotor: 50, piutangAkhir: 1000, karcisBelum: 1, labaKotor: 30000000 }, perBulan: {} }]);
var D1 = dbTambahan(susunDasbor(KINI, 'hari'), KINI); var W1 = wgSusun(WG_KATALOG.map(function (k) { return { id: k.id }; }), D1); var w1 = function (id) { return W1.find(function (x) { return x.id === id; }); };
var AM = D1.rapor.ambang; var RH = rekapHari(iso); var harian = 30000000 / 30; var laju = harian * klBagianHari(KINI);
ok('9: margin target 50 % → merah · piutang batas Rp1.000 → merah (piutang sekarang lebih) · lampu menempel ke widget + baris "Target owner"', AM.margin.lampu === 'merah' && AM.piutang.lampu === 'merah' && w1('marginBulan').lampu === 'merah' && w1('piutangTotal').lampu === 'merah' && w1('piutangTotal').rinci.some(function (r) { return r[0] === 'Target owner'; }), J(AM));
var bg = klBagianHari(KINI); aturDengan([{ id: 'anggaranBulan', target: { labaKotor: Math.round(RH.margin / ((1 + bg) / 2) * 30) }, perBulan: {} }]);
var AMt = dbTambahan(susunDasbor(KINI, 'hari'), KINI).rapor.ambang.labaHari;
ok('9: laba kotor hari ini di antara laju jam & target harian = AMBER (sesuai laju jam, belum tercapai)', RH.margin > 0 && bg > 0.1 && bg < 0.9 && AMt && AMt.lampu === 'amber' && /laju jam/.test(AMt.teks), J([RH.margin, bg, AMt]));
aturDengan([{ id: 'anggaranBulan', target: { marginKotor: 50, piutangAkhir: 1000, karcisBelum: 1, labaKotor: 30000000 }, perBulan: {} }]);
ok('9: karcis batas 1 → lampu dari jumlah karcis sekarang · laba kotor hari ini vs target harian (sebulan ÷ 30) dengan laju jam toko', AM.karcis.lampu === kbLampuTarget({ arah: 'maks' }, 1, daftarKarcis(KINI).nKarcis, null, 10).lampu && AM.labaHari.lampu === (RH.margin >= harian ? 'hijau' : RH.margin >= laju ? 'amber' : 'merah') && dekat(AM.labaHari.target, harian, 1e-6), J([AM.karcis, AM.labaHari, RH.margin]));
aturDengan([]);
ok('9: Dasbor Bulan ini & Biaya tidak berubah oleh rapor (kelompok lain sama persis)', J(D0.bulan) === J(susunDasbor(KINI, 'hari').bulan));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Laporan › Bulanan: lembar KPI (saklar Laba | Kas) · kotor & bersih · arus kas', 'laporan', ['RB.rbRapor(key, kini(), s.raporM)', 'RB.rbKotorBersih(key, kini())', 'RB.rbArusKas(key, kini())', '${hero}${inti}${rapor}${kotorB}${arus}', 'data-aksi="rbMode"', 'data-aksi="rbHari"']),
    ('Laporan › Biaya: anggaran vs aktual + sebab & tindakan · pecahan selisih · Atur target & angka khusus', 'laporan', ['RB.rbAnggaranAktual(key, kini())', 'RB.rbPecahSelisih(key, kini())', '${kartuAA}${kartuPS}', 'data-aksi="abCatBuka"', 'data-ketik="abCatKetik"', 'KB.susunCatatanPos(a.bulan, a.pos, a.sebab, a.tindakan, waktu())', 'data-kunci="target:${t.id}"', 'data-kunci="khususA:${id}"', 'data-kunci="khususT:${t.id}"', 'data-aksi="abKhusus"', 'KB.susunAturSemua(st().aturB || {}, waktu())', 'KB.drafAturSemua(keyBiaya())', 'RB.rbDrafAcuanTarget(key, kini(), D.draf)']),
    ('Dasbor: kartu Rapor bulan (saklar) & Arus kas + lampu target owner di kartu lama', 'dasbor', ['kRapor: () => kartuRapor(D.rapor)', 'kArusKas: () => kartuArusKas(D.rapor)', 'function kartuRapor(Q)', 'function kartuArusKas(Q)', 'data-db-rapor', "lampuDb('margin')", "lampuDb('piutang')", "lampuDb('karcis')", "lampuDb('labaHari')", 'KUNCI_RAPOR']),
    ('CSS rapor & arus kas', 'css', ['.layar-ringkasan .db-rapor-baris {', '.layar-ringkasan .db-arus-masuk {', '.layar-ringkasan .db-rapor-ubah.db-naik']),
    ('Riwayat setelan menamai dua dokumen baru', 'rs', ["anggaranBulan: 'Target bulanan & angka khusus'", "anggaranCatatan: 'Sebab & tindakan anggaran'"]),
    ('bundel uji membawa modul rapor otomatis', 'bundel', ["RB_MODUL = 'baru/js/layar/rapor-bulan-logika.js'", "RB_PEMAKAI = ('dasbor-logika.js', 'laporan.js')"]),
    ('peta tulis mencatat dua penyusun baru', 'peta', ["'susunAturSemua':", "'susunCatatanPos':"]),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_rapor_bulan.py && python3 alat-uji/uji_rapor_bulan.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['Paket P2', 'rapor-bulan-logika.js', 'aturanToko/anggaranBulan', 'aturanToko/anggaranCatatan', 'rbPecahSelisih', 'pjPotonganHarian', 'lpHariBulan', 'kbLampuTarget']),
]
RUSAK = [
    ('jatah sampai hari ke-N hilang', KB, "const dasar = t.jalan && X && X.berjalan && X.nHari > 0 ? nilai * X.hariJalan / X.nHari : nilai;", "const dasar = nilai;"),
    ('lampu batas terbalik', KB, "(aktual <= dasar + 1e-9 ? 'hijau'", "(aktual >= dasar ? 'hijau'"),
    ('angka khusus tidak menimpa anggaran', KB, "Object.keys(P.anggaran).forEach((id) => { anggaran[id] = P.anggaran[id]; khusus[id] = true; });", "Object.keys(P.anggaran).forEach((id) => { khusus[id] = true; });"),
    ('Peta biaya memakai anggaran umum', KB, "const A = aturKendaliBulan(key); const K = kbInti(key, kini, B, A);", "const A = aturKendali(); const K = kbInti(key, kini, B, A);"),
    ('target khusus diabaikan', KB, "const k = !!(P && P.target[t.id] !== undefined);", "const k = false;"),
    ('simpan selalu menulis anggaranBulan', KB, "const dokumen = K.dokumen.concat(berubah ?", "const dokumen = K.dokumen.concat(true ?"),
    ('huruf diterima sebagai target', KB, "if (!/^[0-9][0-9.,]*$/.test(s)) return { tolak: label", "if (false) return { tolak: label"),
    ('angka khusus kosong disimpan 0', KB, "const v = isi.khususA ? isi.khususA[id] : ''; if (ugKosong(v)) continue;", "const v = isi.khususA ? isi.khususA[id] || '0' : '0'; if (ugKosong(v)) continue;"),
    ('catatan kosong tidak menghapus', KB, "if (s || t) satu[pos] = { sebab: s, tindakan: t, tanggal: w.tanggal, jam: w.jam }; else delete satu[pos];", "satu[pos] = { sebab: s, tindakan: t, tanggal: w.tanggal, jam: w.jam };"),
    ('potongan per hari lupa tawar', PJ, "h.n += 1; h.nota += pot; h.tawar += tw; h.jumlah += pot + tw;", "h.n += 1; h.nota += pot; h.jumlah += pot;"),
    ('omzet per hari lupa retur', LPL, "d.retur = retur[t].uang || 0; d.omzet -= d.retur;", "d.retur = retur[t].uang || 0;"),
    ('kotor tanpa retur', RB, "const kotor = retur === null ? null : K.omzet + retur + PT.jumlah;", "const kotor = retur === null ? null : K.omzet + PT.jumlah;"),
    ('perkiraan sebulan tidak dipakai', RB, "const pembanding = b.arus && X.berjalan ? rbSebulan(X, ini) : ini;", "const pembanding = ini;"),
    ('volume dikali harga jual', RB, "const volume = (kgA - kgB) * mB,", "const volume = (kgA - kgB) * jB,"),
    ('harga beli terbalik', RB, "hargaBeli = kgA * (hB - hA);", "hargaBeli = kgA * (hA - hB);"),
    ('kg anggaran tidak dijatah', RB, "const kgB = X.berjalan ? TB.kgTerjual.nilai * X.hariJalan / X.nHari : TB.kgTerjual.nilai;", "const kgB = TB.kgTerjual.nilai;"),
    ('piutang ikut kelebihan bayar', RB, "const d = hitungPiutang(sampai).filter((x) => x.sisa > 0);", "const d = hitungPiutang(sampai);"),
    ('lama piutang diukur di awal bulan', RB, "const DS = diarsip ? null : pnDsoPada(sampai);", "const DS = diarsip ? null : pnDsoPada(awal);"),
    ('perputaran tidak disetahunkan', RB, "SR.putaranTahun !== null && SR.putaranTahun !== undefined ? SR.putaranTahun : null", "SR.putaran !== null && SR.putaran !== undefined ? SR.putaran : null"),
    ('laba kotor hari ini tanpa laju jam', RB, "const laju = harian * Math.max(0, Math.min(1, bagianHari));", "const laju = harian;"),
    ('acuan menimpa ketikan owner', RB, "if (!f || String(tg[t.id] || '').trim()) return;", "if (!f) return;"),
    ('rapor tidak ikut saringan', DL, "const R = rbRapor(key, kini, 'laba');", "const R = rbRapor(iso.slice(0, 7), kini, 'laba');"),
    ('widget tanpa lampu target owner', WG, "    isi = wgTempelAmbang(w.id, isi, D);\n", ""),
]
RUSAK_STATIS = [
    ('Bulanan tanpa lembar KPI', 'laporan', '${hero}${inti}${rapor}${kotorB}${arus}', '${hero}${inti}${kotorB}${arus}'),
    ('Biaya tanpa sebab & tindakan', 'laporan', 'data-aksi="abCatBuka"', 'data-aksi="x"'),
    ('Dasbor tanpa lampu piutang', 'dasbor', "lampuDb('piutang')", "''"),
    ('komentar // menelan kode (pola 30 Sep & 27 Nov)', 'rb', "return klPctTeks(n); /* di bawah", "return klPctTeks(n); // di bawah"),
    ('modul rapor menulis dokumen', 'rb', "export const RB_KATA_LAMPU = {", "const z = { koleksi: 'aturanToko' };\nexport const RB_KATA_LAMPU = {"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_rapor_bulan.py && python3 alat-uji/uji_rapor_bulan.py --kontrol', 'true'),
]

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [], bulan: {} };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
daftarBulan(kini, 4).map(function (b) { return b.key; }).forEach(function (k) {
  var X = aman('bulan ' + k, function () { return rbBulan(k, kini); }); var K = aman('kendali ' + k, function () { return kendaliBulan(k, kini); });
  var PT = aman('pot ' + k, function () { return pjPotonganBulan(k); }); var PH = aman('potHari ' + k, function () { return pjPotonganHarian(k); });
  var HB = aman('hari ' + k, function () { return lpHariBulan(k); }); var KB_ = aman('kotor ' + k, function () { return rbKotorBersih(k, kini); });
  var R = aman('rapor ' + k, function () { return rbRapor(k, kini, 'laba'); }); var RK = aman('kas ' + k, function () { return rbRapor(k, kini, 'kas'); });
  var AA = aman('aa ' + k, function () { return rbAnggaranAktual(k, kini); }); var PS = aman('pecah ' + k, function () { return rbPecahSelisih(k, kini); }); var AK = aman('arus ' + k, function () { return rbArusKas(k, kini); });
  var sHB = HB ? Object.keys(HB).reduce(function (a, t) { return a + HB[t].omzet; }, 0) : null; var sPH = PH ? Object.keys(PH.hari).reduce(function (a, t) { return a + PH.hari[t].jumlah; }, 0) : null;
  out.bulan[k] = { sumber: !!(X && K && X.omzet === K.omzet && X.labaKotor === K.margin && X.labaBersih === K.labaBersih), kotorTutup: KB_ ? KB_.menutup : 'x', hariSama: X && X.diarsip ? 'arsip' : Math.abs(sHB - K.omzet) < 0.5,
    potSama: PH && PT ? (PH.diarsip ? 'arsip' : sPH === PT.jumlah) : 'x', baris: R ? R.baris.length : 0, kas: RK ? RK.baris.length : 0, aa: AA ? AA.baris.length : 0, pecah: PS ? (PS.ada ? 'ada' : 'kurang ' + PS.kurang.length) : 'x', arus: !!AK }; });
var D = aman('dasbor', function () { return dbTambahan(susunDasbor(kini, 'hari'), kini); }); var Wd = D ? aman('wg', function () { return wgSusun(WG_KATALOG.map(function (k) { return { id: k.id }; }), D); }) : null;
out.dasbor = D ? { rapor: !!(D.rapor && !D.rapor.galat), galatRapor: D.rapor && D.rapor.galat ? D.rapor.galat : '', wgGalat: Wd ? Wd.filter(function (w) { return w.nilai === 'gagal dihitung'; }).map(function (w) { return w.id; }) : 'x', lampuTarget: Wd ? Wd.filter(function (w) { return w.lampu && ['marginBulan', 'piutangTotal', 'karcis', 'labaKotorHari'].indexOf(w.id) >= 0; }).length : 'x' } : null;
out.tanpaSetelan = !cacheMentah('aturan').some(function (d) { return d && (d.id === 'anggaranBulan' || d.id === 'anggaranCatatan'); });
print(JSON.stringify(out));
"""


def bundel_js(teks):
    return uji_dasbor_sensus.bundel_js(teks)


def jalan(teks):
    jam = "var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = uji_dasbor_sensus.jsc(jam + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    # modul rapor = baca saja; dua dokumen baru hanya ditulis kendali-biaya-logika (aturanToko, owner) — tidak ada koleksi baru, tidak ada rules
    if 'koleksi:' in src['rb'] or 'document.' in src['rb'] or 'tulisDokumen' in src['rb']: g.append('rapor-bulan-logika: modul baca menulis / menyentuh DOM')
    kol = set(re.findall(r"koleksi: '([a-zA-Z]+)'", src['kb']))
    if kol != {'aturanToko'}: g.append('kendali-biaya-logika menulis koleksi selain aturanToko: ' + ', '.join(sorted(kol)))
    for k in ('dl', 'wg', 'kb'):
        if 'document.' in src[k]: g.append(k + ': modul logika menyentuh DOM')
    for k in ('laporan', 'dasbor', 'rb', 'kb', 'dl', 'wg'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if)\b|\)\s*=>|\bconst \w+ = ", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    i = src['baca'].find('Paket P2')
    if i >= 0 and re.search(r'rules v2[5-9]|firestore\.rules', src['baca'][i:i + 6000]): g.append('BACA-DULU menyebut rules baru untuk paket ini (paket ini tanpa rules)')
    return len(STATIS) - len([x for x in g if ' → tidak ketemu' in x]), g


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
            beres = (not h['galat'] and all(v['sumber'] and v['kotorTutup'] in (True, None) and v['hariSama'] in (True, 'arsip') and v['potSama'] in (True, 'arsip') and v['baris'] and v['kas'] and v['aa'] and v['arus'] for v in h['bulan'].values())
                     and h['dasbor'] and h['dasbor']['rapor'] and not h['dasbor']['wgGalat'])
            # angka rupiah toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: rapor tidak menutup ke sumbernya, per hari ≠ bulan, atau Dasbor galat')
    sys.exit(1 if g or gs else 0)
