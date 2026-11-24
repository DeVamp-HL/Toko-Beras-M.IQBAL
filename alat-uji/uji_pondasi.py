#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pondasi.py — PONDASI (owner 24 Nov 2026, dari catatan "Pondasi bisnis"): delapan lampu + disiplin dalam. KOTAK PASIR (nama & angka CONTOH), jsc saja,
TANPA peramban. Data dasarnya kotak pasir uji_kpi_laba + beberapa catatan tambahan di bawah (jualan Oktober, pemasok kedua, setor modal, ambil pribadi).
  aturan warna (fungsi murni): ambang atas / bawah TEGAS, kuning = dalam 10 % dari ambang, ambang 0 = tanpa warna; hasil, ambil pribadi, laju tumbuh, prakiraan;
  1 utang ÷ harta = kewajiban ÷ aset neraca; 2 bon yang SEGERA jatuh tempo vs uang toko (lewat tempo & uang kurang = merah; yang masih jauh tidak); 3 uang toko ÷ biaya toko per hari;
  4 laba bersih 30 hari ÷ harta & ÷ modal owner; 5 ambil pribadi 90 hari vs laba (tidak ada ambil ≠ merah walau rugi); 6 omzet naik ditopang utang = merah;
  7 porsi pemasok terbesar dari RUPIAH belanja; 8 prakiraan = uang + gerak toko sebelum bayar pemasok − bon jatuh tempo, modal owner dikeluarkan;
  belum bisa dihitung DISEBUT (tanpa warna), satu lampu galat tidak mematikan yang lain; setelan ambang (tolak ketikan rusak, simpan sebagian);
  Dasbor (dbPondasi) = angka yang sama apa adanya; disiplin dalam (tutup hari, cek gudang); layar memasang tab & kartunya (statis).

    python3 alat-uji/uji_pondasi.py            → N lulus · 0 gagal
    python3 alat-uji/uji_pondasi.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kpi_laba, uji_jual_baru, uji_kunci_periode  # noqa: E402
JSC = uji_kpi_laba.JSC
PD = 'baru/js/layar/pondasi-logika.js'; DL = 'baru/js/layar/dasbor-logika.js'; LG = 'baru/js/layar/laporan-logika.js'
MODUL = bundel_baru.lengkapi(list(uji_kpi_laba.MODUL))
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'laporanL': 'baru/js/layar/laporan-logika.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': DL, 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml',
          'pd': PD, 'bundel': 'alat-uji/bundel_baru.py', 'cssL': 'baru/css/laporan.css', 'cssR': 'baru/css/ringkasan.css', 'baca': 'baru/BACA-DULU.md'}

KOTAK_PD = {
  'penjualan': [
      {'id': 'pd1', 'tanggal': '2026-10-05', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 1, 'totalKg': 50, 'hargaTotal': 700000, 'hppTotalSaatJual': 640000, 'grupNota': 'gpd1'},
      {'id': 'pd2', 'tanggal': '2026-10-12', 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'karung', 'merkSumber': 'Angsa', 'beratKarungAcuan': 50, 'jumlahKarung': 0.4, 'totalKg': 20, 'hargaTotal': 300000, 'hppTotalSaatJual': 256000, 'grupNota': 'gpd2'}],
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-10-01', 'jam': '08:00', 'pemasok': 'Sumber Contoh', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 7, 'totalKg': 350, 'subtotalHarga': 4450000, 'hargaPerKg': 12714}]}],
  'pengeluaranHarian': [
      {'id': 'hpd1', 'tanggal': '2026-11-10', 'jam': '11:00', 'kategori': 'owner', 'keterangan': 'ambil pribadi', 'nominal': 300000},
      {'id': 'hpd2', 'tanggal': '2026-11-11', 'jam': '11:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'perbaikan atap', 'nominal': 3000000}],
  'modalOwner': [{'id': 'mo1', 'tipe': 'setor', 'nominal': 2000000, 'tanggal': '2026-11-05', 'jam': '09:00', 'kantong': 'laci'}],
  'tutupHari': [{'id': 'th' + str(i), 'tanggal': '2026-11-0' + str(i), 'jam': '21:00', 'kasFisikLaci': 0, 'kasFisikRekening': 0, 'kasFisikAmplop': 0, 'kasFisikBrankas': 0, 'selisihLaci': 0, 'selisih': 0} for i in range(3, 8)],
}

SKENARIO_PD = r"""
var PDX = __PDX__;
var TITIK = { id: 'titikKas', tanggal: '2026-09-30', laci: 20000000, brankas: 1000000, rekening: 2000000, amplop: 300000, diubahPada: '2026-09-30T14:00:00.000Z' };
var K1 = JSON.parse(J(K0)); K1.penjualan = K1.penjualan.concat(PDX.penjualan); K1.batchMasuk = K1.batchMasuk.concat(PDX.batchMasuk); K1.pengeluaranHarian = K1.pengeluaranHarian.concat(PDX.pengeluaranHarian);
var pasang = function () { Object.keys(K1).forEach(function (n) { pasok(n, JSON.parse(J(K1[n]))); }); pasok('modalOwner', JSON.parse(J(PDX.modalOwner))); pasok('pengaturan', [JSON.parse(J(TITIK))]); pasok('tutupHari', []); pasok('cekGudang', []); aturDengan([]); };
pasang();
var lam = function (P, id) { return P.lampu.find(function (l) { return l.id === id; }); };
var ambang = function (o) { aturDengan([Object.assign({ id: 'pondasi' }, o)]); };
var rinci = function (l, nama) { var r = l.rinci.find(function (x) { return x[0] === nama; }); return r ? r[1] : null; };

// ---- aturan warna: fungsi murni, dihitung tangan
ok('warna ambang ATAS tegas: 11 dari 10 merah · tepat 10 kuning (bukan merah) · 9,5 kuning · 9 aman · ambang 0 tanpa warna', pdLampuAtas(11, 10) === 'merah' && pdLampuAtas(10, 10) === 'amber' && pdLampuAtas(9.5, 10) === 'amber' && pdLampuAtas(9, 10) === 'hijau' && pdLampuAtas(999, 0) === 'tanpa');
ok('warna ambang BAWAH tegas: 9 dari 10 merah · tepat 10 kuning · 10,5 kuning · 11 aman · ambang 0 tanpa warna', pdLampuBawah(9, 10) === 'merah' && pdLampuBawah(10, 10) === 'amber' && pdLampuBawah(10.5, 10) === 'amber' && pdLampuBawah(11, 10) === 'hijau' && pdLampuBawah(0, 0) === 'tanpa');
ok('warna hasil: rugi merah (walau ambang mati) · tanpa ambang tanpa warna · di bawah ambang kuning · sama dengan ambang aman', pdLampuHasil(-1, -0.1, 0) === 'merah' && pdLampuHasil(100, 1, 0) === 'tanpa' && pdLampuHasil(100, 1, 2) === 'amber' && pdLampuHasil(100, 2, 2) === 'hijau');
ok('warna ambil pribadi: tidak ada ambil = aman walau toko rugi · ambil lebih besar dari laba = merah · sama dengan laba = aman · bulan ini lewat batas = kuning',
  pdLampuAmbil(0, -500, false) === 'hijau' && pdLampuAmbil(300, -500, false) === 'merah' && pdLampuAmbil(300, 200, true) === 'merah' && pdLampuAmbil(300, 300, false) === 'hijau' && pdLampuAmbil(200, 300, true) === 'amber' && pdLampuAmbil(200, 300, false) === 'hijau');
ok('warna laju tumbuh: omzet turun / sama = tanpa warna · naik + utang cepat + kas turun = merah · salah satunya kuning · tidak keduanya aman',
  pdLampuTumbuh(-5, true, true) === 'tanpa' && pdLampuTumbuh(0, true, true) === 'tanpa' && pdLampuTumbuh(5, true, true) === 'merah' && pdLampuTumbuh(5, true, false) === 'amber' && pdLampuTumbuh(5, false, true) === 'amber' && pdLampuTumbuh(5, false, false) === 'hijau');
var KD = pdKasDepan(10000000, 8000000, 2000000, 9500000, 4800000);
ok('prakiraan (tangan): gerak = (10 − 8) − 2 setor modal + 9,5 bayar pemasok = 9,5 jt; uang 30 hari lagi = 10 + 9,5 − 4,8 = 14,7 jt', KD.gerak === 9500000 && KD.kasDepan === 14700000, J(KD));

// ---- delapan lampu atas data kotak pasir
var P = pdPondasi(KINI); var N = neracaPada(null, KINI); var S0 = saldoKantong(); var S1 = saldoKantong('2026-10-19');
ok('delapan lampu, urutan tetap, tidak ada yang galat', J(P.lampu.map(function (l) { return l.id; })) === J(['utang', 'bon', 'kasHari', 'hasil', 'ambil', 'tumbuh', 'pemasok', 'depan']) && P.lampu.every(function (l) { return l.keadaan !== 'galat'; }), J(P.lampu.map(function (l) { return [l.id, l.keadaan, l.kalimat]; })));
ok('uang toko kotak pasir terhitung di dua tanggal (titik kas 30 Sep)', S0.ada && S1.ada && N.N.kas === S0.total, J([S0.total, S1.total, N.N.kas]));

// 1 · utang dibanding harta
var U = lam(P, 'utang');
ok('1: utang ÷ harta = kewajiban ÷ aset Neraca; utang pemasok 13,3 jt − 8 jt − 0,5 jt = 4,8 jt (tangan)', N.kewajiban === 4800000 && Math.abs(U.pct - 4800000 / N.aset * 100) < 1e-9 && rinci(U, 'Jumlah utang') === 'Rp4.800.000' && rinci(U, 'Harta toko') === RP(N.aset), J([U, N.aset]));
ok('1: tanpa ambang = tanpa warna, angkanya tetap tampil', U.lampu === 'tanpa' && U.nilai === pdPctTeks(U.pct) && /ambang belum diatur/.test(U.ambang), J(U));
ambang({ utangMaks: Math.floor(U.pct * 10) / 10 - 0.5 }); ok('1: lewat ambang owner = merah', lam(pdPondasi(KINI), 'utang').lampu === 'merah');
ambang({ utangMaks: Math.round(U.pct * 1.05 * 100) / 100 }); ok('1: dalam 10 % di bawah ambang = kuning', lam(pdPondasi(KINI), 'utang').lampu === 'amber');
ambang({ utangMaks: Math.round(U.pct * 2 * 100) / 100 }); ok('1: jauh di bawah ambang = aman', lam(pdPondasi(KINI), 'utang').lampu === 'hijau');
aturDengan([]);

// 2 · bon pemasok 30 hari ke depan
var B = lam(P, 'bon');
ok('2: bon yang SEGERA jatuh tempo (≤ 7 hari, setelan Bon pemasok) = 4,8 jt · 1 bon (kedatangan 2 Nov + tempo 21 hari = 23 Nov, 5 hari lagi); uang toko cukup = aman', B.lampu === 'hijau' && B.nilai === 'cukup' && rinci(B, 'Jatuh tempo ≤ 7 hari (termasuk yang lewat)') === 'Rp4.800.000 · 1 bon' && rinci(B, 'Jatuh tempo ≤ 30 hari') === 'Rp4.800.000 · 1 bon' && rinci(B, 'Uang toko sekarang') === RP(S0.total) && rinci(B, 'Sudah lewat tempo') === 'tidak ada', J(B));
pasok('pengaturan', [Object.assign({}, TITIK, { laci: 23300000 - S0.total + 1000000, brankas: 0, rekening: 0, amplop: 0 })]);
var B2 = lam(pdPondasi(KINI), 'bon'); var kasKecil = saldoKantong().total;
ok('2: uang toko tidak cukup untuk bon yang segera jatuh tempo = merah, kurangnya = bon − uang (tangan)', B2.lampu === 'merah' && kasKecil === 1000000 && B2.nilai === 'kurang Rp3.800.000', J([B2, kasKecil]));
pasok('aturanToko', JSON.parse(J(ATUR)).map(function (d) { return d.id === 'catatStok' ? Object.assign({}, d, { tempoHari: 28 }) : d; }));
var B2b = lam(pdPondasi(KINI), 'bon');
ok('2: bon yang temponya masih JAUH (tempo 28 hari → 12 hari lagi) TIDAK membuat merah walau uang hari ini kurang — dibayar dari penjualan; tetap disebut di jendela 30 hari & menunjuk lampu Prakiraan', B2b.lampu === 'hijau' && B2b.nilai === 'belum ada yang dekat' && rinci(B2b, 'Jatuh tempo ≤ 7 hari (termasuk yang lewat)') === 'Rp0 · 0 bon' && rinci(B2b, 'Jatuh tempo ≤ 30 hari') === 'Rp4.800.000 · 1 bon' && /lihat lampu Prakiraan/.test(B2b.kalimat), J(B2b));
pasok('aturanToko', JSON.parse(J(ATUR)).concat([{ id: 'bonPemasok', dekatHari: 14 }]).map(function (d) { return d.id === 'catatStok' ? Object.assign({}, d, { tempoHari: 28 }) : d; }));
ok('2: "segera" mengikuti setelan owner di Bon pemasok: dekat 14 hari → bon 12 hari lagi ikut, uang kurang = merah', lam(pdPondasi(KINI), 'bon').lampu === 'merah' && rinci(lam(pdPondasi(KINI), 'bon'), 'Jatuh tempo ≤ 14 hari (termasuk yang lewat)') === 'Rp4.800.000 · 1 bon', J(lam(pdPondasi(KINI), 'bon')));
aturDengan([]);
pasok('pengaturan', [JSON.parse(J(TITIK))]);
pasok('utangPemasokMutasi', K1.utangPemasokMutasi.filter(function (m) { return m.id !== 'p3'; }));
var B3 = lam(pdPondasi(KINI), 'bon');
ok('2: bon lama Agustus yang belum lunas = LEWAT tempo → merah walau uangnya cukup; mesin memotongkan bayar tanpa tunjuk 0,5 jt ke bon tertua, jadi lewat 0,5 jt & jumlah 0,5 + 5,3 = 5,8 jt (tangan)', B3.lampu === 'merah' && B3.nilai === '1 lewat tempo' && rinci(B3, 'Jatuh tempo ≤ 7 hari (termasuk yang lewat)') === 'Rp5.800.000 · 2 bon' && rinci(B3, 'Jatuh tempo ≤ 30 hari') === 'Rp5.800.000 · 2 bon' && rinci(B3, 'Sudah lewat tempo') === 'Rp500.000 · 1 bon' && /cukup, sisa/.test(B3.kalimat), J(B3));
pasang();

// 3 · uang toko cukup berapa hari
var KH = lam(P, 'kasHari');
ok('3: biaya toko 30 hari = 100 + 20 + 2 + 5 rb + atap 3 jt = 3.127.000 (tangan; ambil pribadi TIDAK ikut) → hari = uang ÷ (biaya ÷ 30)', rinci(KH, 'Biaya toko 30 hari terakhir') === 'Rp3.127.000' && Math.abs(KH.hari - S0.total / (3127000 / 30)) < 1e-6 && KH.nilai === '±' + Math.floor(KH.hari) + ' hari' && KH.lampu === 'tanpa', J(KH));
ambang({ kasHariMin: Math.floor(KH.hari) + 5 }); ok('3: di bawah ambang hari owner = merah', lam(pdPondasi(KINI), 'kasHari').lampu === 'merah');
ambang({ kasHariMin: Math.floor(KH.hari / 1.05) }); ok('3: dalam 10 % di atas ambang = kuning', lam(pdPondasi(KINI), 'kasHari').lampu === 'amber', J([KH.hari, Math.floor(KH.hari / 1.05)]));
ambang({ kasHariMin: Math.floor(KH.hari / 2) }); ok('3: jauh di atas ambang = aman', lam(pdPondasi(KINI), 'kasHari').lampu === 'hijau');
aturDengan([]);

// 4 · hasil atas harta & modal
var HS = lam(P, 'hasil'); var L30 = ugLabaBersih('2026-10-20', '2026-11-18');
ok('4: laba bersih 30 hari = mesin laba (20 Okt – 18 Nov) ÷ aset Neraca; rugi = merah', Math.abs(HS.pct - L30.labaBersih / N.aset * 100) < 1e-9 && rinci(HS, 'Laba bersih 30 hari terakhir') === RP(L30.labaBersih) && L30.labaBersih < 0 && HS.lampu === 'merah' && /RUGI/.test(HS.kalimat), J([HS, L30.labaBersih]));
ok('4: modal owner = setoran yang tercatat (2 jt), disebut di kalimat', rinci(HS, 'Modal owner tertanam') === 'Rp2.000.000' && /Dibanding modal owner yang tercatat Rp2\.000\.000/.test(HS.kalimat), HS.kalimat);
pasok('modalOwner', []); ok('4: tanpa setoran modal → hasil atas modal DISEBUT belum bisa dihitung (bukan dibagi nol)', /hasil atas modal belum bisa dihitung/.test(lam(pdPondasi(KINI), 'hasil').kalimat) && isFinite(lam(pdPondasi(KINI), 'hasil').pct)); pasang();

// 5 · ambil pribadi dibanding laba
var AM = lam(P, 'ambil'); var L90 = ugLabaBersih('2026-08-21', '2026-11-18');
ok('5: ambil pribadi 90 hari = 300 rb (tangan), laba bersih 90 hari = mesin; toko rugi & tetap diambil = merah', rinci(AM, 'Ambil pribadi 90 hari') === 'Rp300.000' && rinci(AM, 'Laba bersih 90 hari') === RP(L90.labaBersih) && rinci(AM, 'Tinggal di toko') === RP(L90.labaBersih - 300000) && AM.lampu === 'merah' && /toko sedang rugi dan tetap diambil/.test(AM.kalimat), J(AM));
pasok('pengeluaranHarian', K1.pengeluaranHarian.filter(function (h) { return h.kategori !== 'owner'; }));
var AM2 = lam(pdPondasi(KINI), 'ambil');
ok('5: tidak ada ambil pribadi → aman & disebut begitu, walau toko rugi (rugi urusan lampu 4)', AM2.lampu === 'hijau' && AM2.nilai === 'tidak ada ambil' && /tidak mengambil apa pun/.test(AM2.kalimat), J(AM2));
pasang();

// 6 · laju tumbuh
var TB = lam(P, 'tumbuh'); var O30 = lpHariRentang('2026-10-20', '2026-11-18'); var O60 = lpHariRentang('2026-09-20', '2026-10-19'); var N1 = neracaPada('2026-10-19', KINI);
ok('6: 30 hari sebelumnya (20 Sep – 19 Okt) = dua nota Oktober 700 + 300 rb = 1 jt (tangan); tumbuh = (kini − lalu) ÷ lalu', O60.omzetPenuh === 1000000 && Math.abs(TB.pct - (O30.omzetPenuh - 1000000) / 1000000 * 100) < 1e-9 && rinci(TB, 'Omzet 30 hari sebelumnya') === 'Rp1.000.000' && rinci(TB, 'Omzet 30 hari terakhir') === RP(O30.omzetPenuh), J([TB, O30.omzetPenuh, O60.omzetPenuh]));
ok('6: omzet naik, utang pemasok 1 jt → 4,8 jt (naik lebih cepat) DAN uang toko turun → merah "ditopang utang"', TB.pct > 0 && N1.N.utangPemasok === 1000000 && S0.total < S1.total && TB.lampu === 'merah' && /ditopang utang/.test(TB.kalimat) && /^naik Rp3\.800\.000/.test(rinci(TB, 'Utang pemasok')) && rinci(TB, 'Uang toko') === 'turun ' + RP(S1.total - S0.total), J([TB, N1.N.utangPemasok, S0.total, S1.total]));
pasok('penjualan', K1.penjualan.filter(function (p) { return p.id !== 'pd1' && p.id !== 'pd2'; }));
var TB2 = lam(pdPondasi(KINI), 'tumbuh');
ok('6: tanpa omzet di 30 hari sebelumnya → BELUM bisa dihitung, tanpa warna (tidak dianggap tumbuh tak terhingga)', TB2.keadaan === 'belum' && TB2.lampu === 'tanpa', J(TB2));
pasang();
pasok('penjualan', K1.penjualan.concat([{ id: 'pd3', tanggal: '2026-10-15', jam: '09:00', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 10, totalKg: 500, hargaTotal: 7000000, hppTotalSaatJual: 6400000, grupNota: 'gpd3' }]));
var TB3 = lam(pdPondasi(KINI), 'tumbuh');
ok('6: omzet TURUN → tanpa warna, kalimatnya menyebut turun (bukan soal tumbuh terlalu cepat)', TB3.keadaan === 'ada' && TB3.pct < 0 && TB3.lampu === 'tanpa' && /Omzet turun/.test(TB3.kalimat), J(TB3));
pasang();

// 7 · bergantung pada satu pemasok
var PM = lam(P, 'pemasok');
ok('7: porsi RUPIAH belanja 90 hari: 13,35 jt dari 17,8 jt = 75 % (tangan), dua pemasok', Math.abs(PM.pct - 75) < 1e-9 && PM.nilai === '75 %' && rinci(PM, 'Roda Contoh') === 'Rp13.350.000 · 75 % · 1 kedatangan' && rinci(PM, 'Sumber Contoh') === 'Rp4.450.000 · 25 % · 1 kedatangan' && rinci(PM, 'Jumlah belanja') === 'Rp17.800.000' && PM.lampu === 'tanpa', J(PM));
ambang({ pemasokMaks: 70 }); ok('7: 75 % lewat ambang 70 % = merah', lam(pdPondasi(KINI), 'pemasok').lampu === 'merah');
ambang({ pemasokMaks: 80 }); ok('7: 75 % dalam 10 % di bawah ambang 80 % (di atas 72 %) = kuning', lam(pdPondasi(KINI), 'pemasok').lampu === 'amber');
ambang({ pemasokMaks: 75 }); ok('7: tepat di ambang 75 % = kuning, BUKAN merah (tegas >)', lam(pdPondasi(KINI), 'pemasok').lampu === 'amber');
ambang({ pemasokMaks: 90 }); ok('7: 75 % jauh di bawah ambang 90 % = aman', lam(pdPondasi(KINI), 'pemasok').lampu === 'hijau');
aturDengan([]);
pasok('batchMasuk', K1.batchMasuk.filter(function (b) { return b.id !== 'b1'; }));
var PM2 = lam(pdPondasi(KINI), 'pemasok'); ok('7: satu pemasok saja = 100 % dan disebut "SATU pemasok"', Math.abs(PM2.pct - 100) < 1e-9 && /SATU pemasok/.test(PM2.kalimat), J(PM2)); pasang();

// 8 · prakiraan 30 hari
var DP = lam(P, 'depan'); var KDx = pdKasDepan(S0.total, S1.total, 2000000, 9500000, 4800000);
ok('8: prakiraan = uang kini + gerak toko − bon jatuh tempo; setor modal 2 jt DIKELUARKAN, bayar pemasok 30 hari 5 + 3 + 1 + 0,5 = 9,5 jt DITAMBAH KEMBALI (tangan)', DP.perkiraan === true && DP.kasDepan === KDx.kasDepan && rinci(DP, '— setor / tarik modal owner (dikeluarkan)') === 'Rp2.000.000' && rinci(DP, '— sudah dibayar ke pemasok (ditambah kembali)') === 'Rp9.500.000' && rinci(DP, 'Bon jatuh tempo ≤ 30 hari') === 'Rp4.800.000 · 1 bon' && rinci(DP, '— uang toko berubah') === RP(S0.total - S1.total) && /^\[PERKIRAAN\]/.test(DP.kalimat), J([DP, KDx, S0.total, S1.total]));
ok('8: perkiraan uang di atas nol & kas minimum mati = aman', DP.kasDepan > 0 && DP.lampu === 'hijau', J(DP.kasDepan));
aturDengan([{ id: 'kpiLaba', kasMinimum: DP.kasDepan + 1 }]); ok('8: perkiraan di bawah kas minimum owner (Target & ambang) = kuning', lam(pdPondasi(KINI), 'depan').lampu === 'amber'); aturDengan([]);
pasok('pengaturan', [Object.assign({}, TITIK, { tanggal: '2026-11-01' })]);
var DP2 = lam(pdPondasi(KINI), 'depan'); ok('8: titik kas disetel sesudah 30 hari lalu & tidak ada hitungan tutup hari → BELUM bisa dihitung, sebabnya disebut (tidak ditebak)', DP2.keadaan === 'belum' && DP2.lampu === 'tanpa' && /30 hari lalu belum bisa dihitung \(tidak ada tutup hari yang menyimpan isi tempat uang/.test(DP2.kalimat), J(DP2));
// titik kas sudah maju (keadaan toko sehari-hari): uang 30 hari lalu = hitungan fisik tutup hari terakhir pada/sebelum 19 Okt + catatan uang sesudahnya
pasok('tutupHari', [{ id: 'tl0', tanggal: '2026-10-08', jam: '21:00', titik: { laci: 1, rekening: 1, amplop: 1, brankas: 1 } }, { id: 'tl1', tanggal: '2026-10-11', jam: '21:00', titik: { laci: 9000000, rekening: 500000, amplop: 250000, brankas: 250000 } }, { id: 'tl2', tanggal: '2026-10-25', jam: '21:00', titik: { laci: 7, rekening: 7, amplop: 7, brankas: 7 } }]);
var KT = lpKasPadaTanggal('2026-10-19'); var P3 = pdPondasi(KINI); var DP3 = lam(P3, 'depan'); var S0b = saldoKantong();
ok('8: uang 30 hari lalu dari tutup hari TERAKHIR pada/sebelum tanggalnya: 11 Okt 10 jt + nota 12 Okt 300 rb = 10,3 jt (tangan); tutup hari sesudahnya tidak dipakai', KT.kas === 10300000 && /tutup hari 11 Okt/.test(KT.sumber), J(KT));
ok('8: titik kas sudah maju → prakiraan TETAP terhitung dari hitungan tutup hari; laju tumbuh ikut memakainya', DP3.keadaan === 'ada' && DP3.kasDepan === pdKasDepan(S0b.total, 10300000, 2000000, 9500000, 4800000).kasDepan && /^Rp10\.300\.000 · hitungan fisik tutup hari 11 Okt/.test(rinci(DP3, 'Uang toko 30 hari lalu')) && rinci(lam(P3, 'tumbuh'), 'Uang toko') === (S0b.total < 10300000 ? 'turun ' : 'naik ') + RP(Math.abs(S0b.total - 10300000)), J([DP3, S0b.total]));
pasang();

// ---- belum bisa dihitung & galat satu lampu
pasok('pengaturan', []);
var PK = pdPondasi(KINI);
ok('tanpa titik kas: utang, bon, uang cukup, hasil, prakiraan = BELUM (tanpa warna, kalimatnya menyebut sebab); pemasok tetap terhitung', ['utang', 'bon', 'kasHari', 'hasil', 'depan'].every(function (id) { var l = lam(PK, id); return l.keadaan === 'belum' && l.lampu === 'tanpa' && l.nilai === 'belum bisa' && l.kalimat.length > 20; }) && lam(PK, 'pemasok').keadaan === 'ada' && PK.hitung.belum >= 5 && PK.hitung.merah + PK.hitung.amber + PK.hitung.hijau + PK.hitung.tanpa === 8, J(PK.lampu.map(function (l) { return [l.id, l.keadaan, l.lampu]; })));
pasang();
var bpHariBayarAsli = bpHariBayar; bpHariBayar = function () { throw new Error('sengaja'); };
pasang(); var PG = pdPondasi(KINI); bpHariBayar = bpHariBayarAsli; pasang();
ok('satu lampu galat (prakiraan) tampil sebagai kalimat di lampunya; tujuh lampu lain tetap terhitung', lam(PG, 'depan').keadaan === 'galat' && /Gagal dihitung: sengaja/.test(lam(PG, 'depan').kalimat) && PG.lampu.filter(function (l) { return l.keadaan === 'ada'; }).length === 7, J(PG.lampu.map(function (l) { return [l.id, l.keadaan]; })));
var PA = pdPondasi(KINI); ok('mulus: data, hari & titik kas sama → hasil yang SAMA dipakai ulang (tidak dihitung ulang tiap ketukan); data berubah → dihitung lagi', pdPondasi(KINI) === PA && pdDisiplin(KINI) === pdDisiplin(KINI) && (pasang(), pdPondasi(KINI) !== PA) && J(pdPondasi(KINI).lampu) === J(PA.lampu));
pasok('pengaturan', [Object.assign({}, TITIK, { laci: TITIK.laci + 1000 })]); ok('mulus: titik kas berubah → dihitung lagi (uang toko ikut naik Rp1.000)', rinci(lam(pdPondasi(KINI), 'kasHari'), 'Uang toko (laci · brankas · rekening · amplop)') === RP(S0.total + 1000)); pasang();
ok('ringkasan menghitung & menyebut lampu merah', P.hitung.merah === P.lampu.filter(function (l) { return l.lampu === 'merah'; }).length && P.hitung.merah >= 3 && /lampu merah: /.test(P.kalimat) && /laju tumbuh/.test(P.kalimat) && P.luar.length === 3, J([P.hitung, P.kalimat]));

// ---- setelan ambang owner
var S1a = susunAturPondasi({ utangMaks: '150', kasHariMin: '', hasilMin: '2,5', pemasokMaks: '60' }, W);
ok('setelan: disimpan ke aturanToko/pondasi; koma desimal dibaca; kosong = mati', !S1a.tolak && S1a.dokumen.length === 1 && S1a.dokumen[0].koleksi === 'aturanToko' && S1a.dokumen[0].data.id === 'pondasi' && S1a.dokumen[0].data.utangMaks === 150 && S1a.dokumen[0].data.hasilMin === 2.5 && S1a.dokumen[0].data.pemasokMaks === 60 && S1a.dokumen[0].data.kasHariMin === 0 && S1a.patch.aturPd === null, J(S1a));
ok('setelan: ketikan rusak DITOLAK dengan kalimat (huruf, nol, lewat batas) — tidak dibulatkan diam-diam', !!susunAturPondasi({ utangMaks: 'abc' }, W).tolak && !!susunAturPondasi({ pemasokMaks: '0' }, W).tolak && !!susunAturPondasi({ pemasokMaks: '101' }, W).tolak && !!susunAturPondasi({ kasHariMin: '-5' }, W).tolak);
aturDengan([S1a.dokumen[0].data]);
var S2a = susunAturPondasi({ utangMaks: '120' }, W);
ok('setelan: simpan SATU ambang tidak menghapus ambang lain; pdAtur & draf membacanya', S2a.dokumen[0].data.utangMaks === 120 && S2a.dokumen[0].data.pemasokMaks === 60 && S2a.dokumen[0].data.hasilMin === 2.5 && pdAtur().utangMaks === 150 && pdAtur().kasHariMin === 0 && pdAtur().dariOwner === true && pdDrafAtur().hasilMin === '2,5' && pdDrafAtur().kasHariMin === '', J([S2a, pdAtur(), pdDrafAtur()]));
ok('setelan: tidak ada yang diubah → ditolak', susunAturPondasi({ utangMaks: '150', hasilMin: '2,5' }, W).tolak === 'Tidak ada yang diubah');
aturDengan([{ id: 'pondasi', utangMaks: 5000, pemasokMaks: -3, hasilMin: 'x' }]); ok('setelan: angka tersimpan yang di luar batas dibaca sebagai mati', pdAtur().utangMaks === 0 && pdAtur().pemasokMaks === 0 && pdAtur().hasilMin === 0, J(pdAtur()));
aturDengan([]);

// ---- Dasbor = angka yang sama apa adanya
var DBP = dbPondasi(KINI); var SD = susunDasbor(KINI, 'bulan');
ok('Dasbor: dbPondasi = pdPondasi apa adanya, menuju Laporan › Pondasi', J(DBP.lampu) === J(pdPondasi(KINI).lampu) && J(DBP.hitung) === J(P.hitung) && DBP.tujuan.ke === 'laporan' && DBP.tujuan.keluarga === 'pondasi' && DBP.sumber === 'Laporan › Pondasi');
ok('Dasbor: susunDasbor memuat pondasi, dipertahankan saat ganti rentang, ikut dipanaskan; Laporan punya keluarga pondasi', SD.pondasi && !SD.pondasi.galat && SD.pondasi.lampu.length === 8 && susunDasbor(KINI, 'minggu', SD).pondasi === SD.pondasi && DB_PANAS.indexOf('pondasi') >= 0 && KELUARGA_LAPORAN.some(function (k) { return k[0] === 'pondasi'; }));

// ---- disiplin dalam
var D0 = pdDisiplin(KINI); var db = function (D, id) { return D.baris.find(function (b) { return b.id === id; }); };
ok('disiplin: 6 hari berjualan (3–8 Nov; hari ini tidak ikut), belum ada tutup hari → kuning 0 dari 6; cek gudang belum pernah → kuning', db(D0, 'tutup').lampu === 'amber' && db(D0, 'tutup').nilai === '0 dari 6 hari' && db(D0, 'gudang').lampu === 'amber' && db(D0, 'gudang').nilai === 'belum pernah', J(D0));
pasok('tutupHari', JSON.parse(J(PDX.tutupHari)));
var D1 = pdDisiplin(KINI);
ok('disiplin: lima malam ditutup (3–7 Nov) → 5 dari 6, yang tidak ditutup disebut tanggalnya (8 Nov)', db(D1, 'tutup').lampu === 'amber' && db(D1, 'tutup').nilai === '5 dari 6 hari' && /1 hari berjualan tidak ditutup malamnya: 8 Nov\./.test(db(D1, 'tutup').kalimat), J(D1));
pasok('tutupHari', JSON.parse(J(PDX.tutupHari)).concat([{ id: 'th8', tanggal: '2026-11-08', jam: '21:00', kasFisikLaci: 0, selisihLaci: 0, selisih: 0 }]));
ok('disiplin: semua malam ditutup → aman', db(pdDisiplin(KINI), 'tutup').lampu === 'hijau' && db(pdDisiplin(KINI), 'tutup').nilai === '6 dari 6 hari');
var CEK = { timbangan: true, palet: true, bocor: true, lembap: true, kutu: true };
pasok('cekGudang', [{ id: 'cg1', tanggal: '2026-11-15', jam: '09:00', cek: CEK, catatan: '' }]); ok('disiplin: cek gudang 3 hari lalu (tiap 7 hari) → terjaga', db(pdDisiplin(KINI), 'gudang').lampu === 'hijau' && db(pdDisiplin(KINI), 'gudang').nilai === 'terjaga', J(pdDisiplin(KINI)));
pasok('cekGudang', [{ id: 'cg0', tanggal: '2026-11-01', jam: '09:00', cek: Object.assign({}, CEK, { kutu: false }), catatan: 'kutu di pojok' }]);
var D2 = pdDisiplin(KINI); ok('disiplin: cek gudang terakhir 17 hari lalu → lewat 10 hari = merah; temuan cek terakhir disebut', db(D2, 'gudang').lampu === 'merah' && db(D2, 'gudang').nilai === 'lewat 10 hari' && /menemukan: kutu/.test(db(D2, 'gudang').kalimat), J(D2));
pasang();

print(J({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Laporan memasang tab Pondasi + lembar ambang', 'laporan', ["import * as PD from './pondasi-logika.js';", "s.keluarga === 'pondasi' ? gambarPondasi(s, L)", 'function gambarPondasi(s, L)', 'PD.pdPondasi(kini())', 'PD.pdDisiplin(kini())', 'data-aksi="pdBuka"',
                                                     'pdAturSimpan: () => tulis(PD.susunAturPondasi(st().aturPd || {}, waktu()))', "'aturPd']", 'bukaPd: {}, aturPd: null']),
    ('Laporan: keluarga Pondasi terdaftar', 'laporanL', ["['neraca', 'Neraca'], ['pondasi', 'Pondasi'], ['dokumen', 'Dokumen']"]),
    ('Dasbor memasang kartu Pondasi', 'dasbor', ['function kartuPondasi(Q)', 'kartuPondasi(D.pondasi)', "daftar('pondasi:' + l.id"]),
    ('Dasbor logika: kelompok pondasi, dipertahankan & dipanaskan', 'dasborL', ["import { pdPondasi } from './pondasi-logika.js';", "pondasi: ['pondasi toko', dbPondasi]", 'pondasi: lama.pondasi', "pondasi: k('pondasi')", "'b2b', 'pondasi'];"]),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/pondasi-logika.js">']),
    ('CI menjalankan uji ini + kontrolnya', 'pages', ['python3 alat-uji/uji_pondasi.py && python3 alat-uji/uji_pondasi.py --kontrol']),
    ('bundel uji melengkapi modul untuk Dasbor', 'bundel', ["PD_MODUL = 'baru/js/layar/pondasi-logika.js'", "PD_PEMAKAI = ('dasbor-logika.js',)"]),
    ('gerak: deret lampu muncul bergiliran + hormat reduced motion', 'cssL', ['lpPdMuncul', 'lpPdDenyut', '.layar-laporan .lp-pd-titik, .layar-laporan .lp-pd-titik.merah { animation: none; }']),
    ('Dasbor: baris lampu dua kolom', 'cssR', ['.layar-ringkasan .db-pd-baris']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Pondasi', 'uji_pondasi.py', 'js/layar/pondasi-logika.js']),
    ('modul hanya membaca', 'pd', []),
]
# yang TIDAK boleh ada di pondasi-logika: DOM, tulisan langsung, mesin uang, dan pembaca koleksi mentah (angka harus lewat fungsi sumber layar lain)
TERLARANG = ['document.', 'tulisDokumen', "from '../mesin/", 'ambilPenjualan', 'ambilPengeluaranHarian', 'ambilUtangPemasokMutasi', 'ambilSemuaBatch', 'ambilPiutangMutasi', 'hitungLaba', 'hitungArusKas', 'cacheMentah']

RUSAK = [
    ('ambang atas: sama dengan ambang dianggap merah (≥)', PD, "(!(batas > 0) ? 'tanpa' : nilai > batas ? 'merah' : nilai > batas * (1 - PD_DEKAT / 100) ? 'amber' : 'hijau');", "(!(batas > 0) ? 'tanpa' : nilai >= batas ? 'merah' : nilai > batas * (1 - PD_DEKAT / 100) ? 'amber' : 'hijau');"),
    ('ambang bawah: tidak pernah kuning', PD, "nilai < batas ? 'merah' : nilai < batas * (1 + PD_DEKAT / 100) ? 'amber' : 'hijau');", "nilai < batas ? 'merah' : 'hijau');"),
    ('ambang mati tetap diberi warna', PD, "export const pdLampuAtas = (nilai, batas) => (!(batas > 0) ? 'tanpa' : ", "export const pdLampuAtas = (nilai, batas) => (false ? 'tanpa' : "),
    ('hasil: rugi tidak merah', PD, "(laba < 0 ? 'merah' : batas > 0 ? (hasil < batas ? 'amber' : 'hijau') : 'tanpa');", "(batas > 0 ? (hasil < batas ? 'amber' : 'hijau') : 'tanpa');"),
    ('ambil pribadi: rugi tanpa ambil dianggap merah', PD, "(ambil > 0 && ambil > laba ? 'merah' : lewatBulan ? 'amber' : 'hijau');", "(ambil > laba ? 'merah' : lewatBulan ? 'amber' : 'hijau');"),
    ('laju tumbuh: omzet turun tetap diberi warna', PD, "(!(tumbuh > 0) ? 'tanpa' : utangCepat && kasTurun ? 'merah'", "(utangCepat && kasTurun ? 'merah'"),
    ('laju tumbuh: satu tanda saja sudah merah', PD, "utangCepat && kasTurun ? 'merah' : utangCepat || kasTurun ? 'amber' : 'hijau');", "utangCepat || kasTurun ? 'merah' : 'hijau');"),
    ('prakiraan: setor modal owner ikut dianggap gerak toko', PD, "const gerak = (kas0 - kas1) - dModal + bayar;", "const gerak = (kas0 - kas1) + bayar;"),
    ('prakiraan: bayar pemasok tidak ditambah kembali (bon terhitung dua kali)', PD, "const gerak = (kas0 - kas1) - dModal + bayar;", "const gerak = (kas0 - kas1) - dModal;"),
    ('prakiraan: bon jatuh tempo tidak dikurangkan', PD, "return { gerak, kasDepan: kas0 + gerak - jatuh }; }", "return { gerak, kasDepan: kas0 + gerak }; }"),
    ('utang: dibagi kekayaan bersih, bukan harta', PD, "const pct = N.kewajiban / N.aset * 100; const batas = X.A.utangMaks;", "const pct = N.kewajiban / (N.aset - N.kewajiban) * 100; const batas = X.A.utangMaks;"),
    ('bon: yang lewat tempo tidak membuat merah', PD, "const lampu = J.nLewat || kurang ? 'merah' : J.nTanpa ? 'amber' : 'hijau';", "const lampu = kurang ? 'merah' : J.nTanpa ? 'amber' : 'hijau';"),
    ('bon: uang kurang tidak membuat merah', PD, "const lampu = J.nLewat || kurang ? 'merah' : J.nTanpa ? 'amber' : 'hijau';", "const lampu = J.nLewat ? 'merah' : J.nTanpa ? 'amber' : 'hijau';"),
    ('bon: bon yang masih jauh ikut dibandingkan dengan uang hari ini (merah selamanya)', PD, "const dekat = B.atur.dekatHari; const nSegera = B.lewat.length + B.dekat.length; const rpSegera = pdJumlah(B.lewat.concat(B.dekat), (b) => b.sisa);", "const dekat = B.atur.dekatHari; const nSegera = J.n; const rpSegera = J.rp;"),
    ('bon: yang sudah lewat tempo tidak ikut dijumlah', PD, "const rpSegera = pdJumlah(B.lewat.concat(B.dekat), (b) => b.sisa);", "const rpSegera = pdJumlah(B.dekat, (b) => b.sisa);"),
    ('bon: jendela 30 hari membuang bon yang sudah lewat', PD, "const jatuh = B.bon.filter((b) => b.jatuh && b.sisaHari !== null && b.sisaHari <= PD_HARI);", "const jatuh = B.bon.filter((b) => b.jatuh && b.sisaHari !== null && b.sisaHari >= 0 && b.sisaHari <= PD_HARI);"),
    ('uang cukup: biaya sebulan tidak dibagi hari', PD, "const L = X.L30(); const biayaHari = (Number(L.biayaToko) || 0) / PD_HARI;", "const L = X.L30(); const biayaHari = (Number(L.biayaToko) || 0);"),
    ('hasil: dibagi modal, bukan harta', PD, "const hasil = laba / N.aset * 100; const modal = Number(N.modal) || 0;", "const modal = Number(N.modal) || 0; const hasil = laba / (modal || 1) * 100;"),
    ('ambil pribadi: jendela 90 hari diganti bulan ini saja', PD, "const awal = X.h(-(PD_HARI_PANJANG - 1)); const P90 = priveRentang(awal, X.iso);", "const awal = X.iso.slice(0, 8) + '15'; const P90 = priveRentang(awal, X.iso);"),
    ('laju tumbuh: pembanding 30 hari sebelumnya salah jendela', PD, "const lalu30 = Number(lpHariRentang(awalLalu, X.h(-PD_HARI)).omzetPenuh) || 0;", "const lalu30 = Number(lpHariRentang(awalLalu, X.iso).omzetPenuh) || 0;"),
    ('pemasok: porsi dari jumlah kedatangan, bukan rupiah', PD, "d.sort((x, y) => y.rp - x.rp || x.nama.localeCompare(y.nama)); const atas = d[0]; const pct = atas.rp / total * 100;", "d.sort((x, y) => y.rp - x.rp || x.nama.localeCompare(y.nama)); const atas = d[0]; const pct = atas.n / d.reduce((a, x) => a + x.n, 0) * 100;"),
    ('prakiraan: titik kas terlalu baru ditebak sebagai nol', PD, "  if (!pdBilangan(kas1)) return pdBelum(id, nama, 'Uang toko ' + PD_HARI + ' hari lalu belum bisa dihitung", "  if (false) return pdBelum(id, nama, 'Uang toko ' + PD_HARI + ' hari lalu belum bisa dihitung"),
    ('uang 30 hari lalu: memakai tutup hari TERTUA, bukan terakhir sebelum tanggalnya', LG, "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal && x.tanggal <= iso).sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)))[0];", "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal && x.tanggal <= iso).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)))[0];"),
    ('uang 30 hari lalu: tutup hari SESUDAH tanggalnya ikut dipakai', LG, "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal && x.tanggal <= iso).sort(", "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal).sort("),
    ('uang 30 hari lalu: catatan uang sesudah tutup hari tidak ikut', LG, "return { kas: saldoKantong(iso, t).total, kenapa: '', sumber: 'hitungan fisik tutup hari ' + tanggalPendek(t.tanggal) + (t.tanggal < iso", "return { kas: saldoKantong(t.tanggal, t).total, kenapa: '', sumber: 'hitungan fisik tutup hari ' + tanggalPendek(t.tanggal) + (t.tanggal < iso"),
    ('prakiraan: hitungan tutup hari diabaikan (selalu belum bisa)', PD, "const K = lpKasPadaTanggal(iso); return pdBilangan(K.kas) ? K : ", "const K = { kas: null, kenapa: '' }; return pdBilangan(K.kas) ? K : "),
    ('mulus: delapan lampu dihitung ulang tiap ketukan (tanpa ingatan)', PD, "  return ingatPerVersi('pdPondasi|' + hariIniIso(kini) + '|' + JSON.stringify(ambilTitikKas()), () => pdPondasiHitung(kini));", "  return pdPondasiHitung(kini);"),
    ('satu lampu galat mematikan semuanya', PD, "const lampu = PD_LAMPU.map(([id, nama, f]) => { try { return f(X); } catch (e) {", "const lampu = PD_LAMPU.map(([id, nama, f]) => { try { return f(X); } catch (e) { throw e;"),
    ('setelan: ketikan rusak dibulatkan diam-diam', PD, "if (!(n > 0) || n > x.maks) { tolak = ", "if (false) { tolak = "),
    ('setelan: simpan satu ambang menimpa yang lain', PD, "const lama = ugAturDok(PD_ID) || {}; const data = Object.assign({}, lama, { id: PD_ID, tanggal: w.tanggal, jam: w.jam });", "const lama = {}; const data = { id: PD_ID, tanggal: w.tanggal, jam: w.jam };"),
    ('disiplin: hari ini ikut dihitung belum ditutup', PD, "filter((d) => !d.hariIni && !d.diarsip && d.n > 0)", "filter((d) => !d.diarsip && d.n > 0)"),
    ('disiplin: cek gudang lewat tempo tidak merah', PD, "lampu: !G.terakhir ? 'amber' : G.sisa < 0 ? 'merah' : G.sisa === 0 ? 'amber' : 'hijau'", "lampu: !G.terakhir ? 'amber' : G.sisa === 0 ? 'amber' : 'hijau'"),
    ('Dasbor memakai hitungan lain dari Laporan', DL, "tujuan: { ke: 'laporan', keluarga: 'pondasi' } }, pdPondasi(kini)); }", "tujuan: { ke: 'laporan', keluarga: 'pondasi' } }, { lampu: [], hitung: {} }); }"),
    ('Dasbor: pondasi dihitung ulang tiap ganti rentang', DL, "pondasi: lama.pondasi, tren: k('tren') };", "pondasi: k('pondasi'), tren: k('tren') };"),
]
RUSAK_STATIS = [
    ('Laporan tanpa tab Pondasi', 'laporan', "s.keluarga === 'pondasi' ? gambarPondasi(s, L) : ", ''),
    ('Dasbor tanpa kartu Pondasi', 'dasbor', 'kartuPondasi(D.pondasi)', "''"),
    ('modul membaca koleksi mentah (rumus uang baru)', 'pd', "import { ambilTutupHari, ambilTitikKas, ingatPerVersi } from '../data/toko.js';", "import { ambilTutupHari, ambilTitikKas, ingatPerVersi, ambilPenjualan } from '../data/toko.js';"),
    ('modul menulis dokumen kedua', 'pd', "return { dokumen: [{ koleksi: 'aturanToko', data }],", "return { dokumen: [{ koleksi: 'aturanToko', data }, { koleksi: 'aturanToko', data }],"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_pondasi.py', 'true'),
]

ASAP = r"""
var out = { galat: null, lampu: [], disiplin: [] };
try {
  Object.keys(CAD.data || CAD).forEach(function (n) { var d = (CAD.data || CAD)[n]; if (Array.isArray(d)) pasok(n, d); });
  setelSumber('cadangan', 'asap');
  var akhir = ''; ambilPenjualan().forEach(function (p) { if ((p.tanggal || '') > akhir) akhir = p.tanggal; }); out.akhir = akhir;
  var K = new Date(akhir + 'T20:00:00+07:00'); var P = pdPondasi(K); var N = neracaPada(null, K);
  out.lampu = P.lampu.map(function (l) { return { id: l.id, lampu: l.lampu, keadaan: l.keadaan }; }); out.hitung = P.hitung;
  var u = P.lampu[0]; out.utangCocok = u.keadaan !== 'ada' || Math.abs(u.pct - N.kewajiban / N.aset * 100) < 1e-9;
  out.dasbor = JSON.stringify(dbPondasi(K).lampu) === JSON.stringify(P.lampu);
  out.disiplin = pdDisiplin(K).baris.map(function (b) { return { id: b.id, lampu: b.lampu }; });
} catch (e) { out.galat = String((e && e.stack) || e).slice(0, 600); }
print(JSON.stringify(out));
"""
BON_PEMASOK_LAMA = uji_kpi_laba.BON_PEMASOK_LAMA


def bundel(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)
    if js.count(BON_PEMASOK_LAMA) == 1: js = js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))
    return js


def jsc(isi):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(isi); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    return r, out


def jalan(teks):
    kepala = uji_kpi_laba.SKENARIO.split('// ---- 1 ·')[0]
    jam = "var __KINI = new Date('2026-11-18T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = jsc(jam + bundel(teks) + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar KPI = ' + json.dumps(uji_kpi_laba.KOTAK_KPI) + ';\n' + kepala + SKENARIO_PD.replace('__PDX__', json.dumps(KOTAK_PD)))
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    pd = src['pd']
    kena = [x for x in TERLARANG if x in pd]
    if kena: g.append('pondasi-logika menyentuh ' + kena[0] + ' — modul ini hanya membaca lewat fungsi sumber layar lain')
    if pd.count("koleksi: '") != 1 or pd.count("koleksi: 'aturanToko'") != 1: g.append('pondasi-logika menulis dokumen selain setelan aturanToko/pondasi')
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
        r, out = jsc(bundel(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out); beres = not h['galat'] and len(h['lampu']) == 8 and all(x['keadaan'] != 'galat' for x in h['lampu']) and h.get('utangCocok') and h.get('dasbor')
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h.get('akhir'), 'LULUS' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: ada lampu galat, utang ÷ harta tidak sama dengan Neraca, atau Dasbor berbeda dari Laporan')
    sys.exit(1 if g or gs else 0)
