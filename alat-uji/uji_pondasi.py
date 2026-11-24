#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_pondasi.py — PONDASI (owner 24 Nov 2026, dari catatan "Pondasi bisnis"): delapan lampu + disiplin dalam; PAKET KEDUA: kuartal (K1–K4), kekayaan dari waktu ke waktu,
rantai pasok (lama kirim, gerak harga beli), risiko & pola hari, organisasi per orang, modal = posisi toko saat sistem mulai mencatat. KOTAK PASIR (nama & angka CONTOH), jsc saja,
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
PGL = 'baru/js/layar/laba-pelanggan-logika.js'; PLL = 'baru/js/layar/pelanggan-logika.js'
SLG = 'baru/js/layar/sistem-logika.js'; KW = 'baru/js/layar/kuartal-logika.js'; BP = 'baru/js/layar/bon-pemasok-logika.js'; RW = 'baru/js/layar/riwayat-logika.js'
MODUL = bundel_baru.lengkapi(list(uji_kpi_laba.MODUL)) + [KW]
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'laporanL': 'baru/js/layar/laporan-logika.js', 'dasbor': 'baru/js/layar/dasbor.js', 'dasborL': DL, 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml',
          'pd': PD, 'kw': KW, 'sl': SLG, 'menu': 'baru/js/layar/menu.js', 'menuL': 'baru/js/layar/menu-logika.js', 'akses': 'baru/js/data/akses.js', 'rules': 'firestore.rules', 'rules19': 'firestore.rules.v19', 'dok20': 'docs/uji-rules-v20.md', 'cssM': 'baru/css/menu.css', 'bundel': 'alat-uji/bundel_baru.py', 'cssL': 'baru/css/laporan.css', 'cssR': 'baru/css/ringkasan.css', 'baca': 'baru/BACA-DULU.md'}

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
var DSR = N.modal + N.selisihBuku;
ok('4: modal yang dibandingkan = POSISI TOKO saat sistem mulai mencatat, dihitung dari buku (setoran 2 jt + beda "belum terjelaskan buku" Neraca = kekayaan bersih − laba kumulatif + ambil pribadi); tidak ada dokumen modal yang ditulis', N.modal === 2000000 && DSR > 0 && Math.abs(DSR - ((N.aset - N.kewajiban) - (N.labaKum - N.prive))) < 0.5 && rinci(HS, 'Setoran modal owner yang tercatat') === 'Rp2.000.000' && rinci(HS, 'Posisi toko saat sistem mulai mencatat (1 Sep 2026), dihitung') === RP(DSR) && HS.kalimat.indexOf('Dibanding modal yang tertanam di toko ' + RP(DSR)) > 0, J([HS, DSR]));
pasok('utangPemasokMutasi', K1.utangPemasokMutasi.concat([{ id: 'sa9', tipe: 'saldoAwal', pemasok: 'Roda Contoh', nominal: 100000000, bonTanggal: '2026-11-10', catatan: 'bon besar', tanggal: '2026-11-10' }]));
var HS2 = lam(pdPondasi(KINI), 'hasil'); ok('4: posisi toko saat sistem mulai mencatat MINUS (utang lebih besar dari harta) → DISEBUT, hasil atas modal tidak dihitung (bukan persen atas modal minus)', /tidak ada modal bersih untuk dibandingkan/.test(HS2.kalimat) && !/balik modal/.test(HS2.kalimat) && /^−Rp/.test(rinci(HS2, 'Posisi toko saat sistem mulai mencatat (1 Sep 2026), dihitung')) && isFinite(HS2.pct), J(HS2)); pasang();

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

// ==================== PAKET KEDUA: kuartal · kekayaan · rantai pasok · risiko · organisasi ====================
// ---- kuartal: kunci & rentang (tangan)
ok('kuartal: kunci, tiga bulannya, rentang & geser (tangan)', kwKey('2026-11-18') === '2026-K4' && kwKey('2026-03-31') === '2026-K1' && kwKey('2026-04-01') === '2026-K2' && J(kwBulan('2026-K4')) === J(['2026-10', '2026-11', '2026-12']) && J(kwRentang('2026-K1')) === J({ awal: '2026-01-01', akhir: '2026-03-31' }) && J(kwRentang('2028-K1')) === J({ awal: '2028-01-01', akhir: '2028-03-31' }) && kwGeser('2026-K1', -1) === '2025-K4' && kwGeser('2026-K4', 1) === '2027-K1' && kwGeser('2026-K3', -6) === '2025-K1' && kwNama('2026-K4') === 'K4 2026');
ok('kuartal: akhir bulan tanpa mesin (Feb biasa 28, Feb kabisat 29, Des 31)', pdAkhirBulan('2026-02') === '2026-02-28' && pdAkhirBulan('2028-02') === '2028-02-29' && pdAkhirBulan('2026-12') === '2026-12-31' && pdAkhirBulan('2026-11') === '2026-11-30');
ok('kuartal: daftar dari catatan pertama (1 Sep 2026 → K3) sampai kuartal berjalan, terbaru dulu', J(kwDaftar(KINI).map(function (k) { return k.key; })) === J(['2026-K4', '2026-K3']) && kwDaftar(KINI)[0].berjalan === true);
var RT = rekapTahun(2026, KINI); var bln = function (k) { return RT.bulan.find(function (b) { return b.key === k; }); };
var Q4 = kwRekap('2026-K4', KINI); var Q3 = kwRekap('2026-K3', KINI);
ok('kuartal K4: omzet = Okt (700 + 300 rb = 1 jt, tangan) + Nov Laporan › Tahunan; Des belum mulai tidak ikut', bln('2026-10').omzet === 1000000 && Q4.omzet === 1000000 + bln('2026-11').omzet && Q4.labaBersih === bln('2026-10').labaBersih + bln('2026-11').labaBersih && Q4.labaKotor === bln('2026-10').margin + bln('2026-11').margin && Q4.biaya === bln('2026-10').biaya + bln('2026-11').biaya && Q4.nBulan === 2 && Q4.nota === bln('2026-10').n + bln('2026-11').n, J([Q4.omzet, Q4.labaBersih, bln('2026-10'), bln('2026-11')]));
ok('kuartal K4: ambil pribadi 300 rb (tangan) → tinggal di toko = laba bersih − 300 rb', Q4.prive === 300000 && Q4.tinggal === Q4.labaBersih - 300000, J([Q4.prive, Q4.tinggal]));
ok('kuartal: K4 masih berjalan & K3 baru mulai di tengahnya → keduanya TIDAK UTUH, sebabnya disebut, banding ditandai BUKAN setara', Q4.utuh === false && Q4.berjalan === true && /TIDAK UTUH — masih berjalan/.test(Q4.status) && Q3.utuh === false && /catatan toko baru mulai 1 Sep 2026/.test(Q3.sebab) && Q4.banding.ada === true && Q4.banding.setara === false && /BUKAN banding setara/.test(Q4.banding.teks) && Q4.banding.omzet === Q3.omzet, J([Q4.status, Q3.sebab, Q4.banding]));
ok('kuartal K3: hanya September yang dihitung (Juli–Agustus sebelum catatan pertama); tidak ada K2 untuk dibandingkan → disebut', Q3.nBulan === 1 && Q3.omzet === bln('2026-09').omzet && Q3.banding.ada === false && /Belum ada K2 2026 untuk dibandingkan/.test(Q3.banding.teks), J([Q3.nBulan, Q3.omzet, Q3.banding]));
var T26 = kwTahun(2026, KINI);
ok('kuartal: Σ empat kuartal = angka tahun Laporan › Tahunan (omzet, laba kotor, biaya, laba bersih)', T26.menutup === true && T26.omzet === RT.omzet && T26.labaBersih === RT.labaBersih && T26.kuartal.length === 4 && T26.kuartal[0].nBulan === 0 && T26.kuartal[1].nBulan === 0, J([T26.menutup, T26.beda, T26.omzet, RT.omzet]));
ok('kuartal K4 (berjalan): kekayaan = Neraca hari ini; potret lampu memakai aturan warna Pondasi (utang ÷ harta, ambil pribadi merah, pemasok 75 %)', Q4.kekayaan.ada && Q4.kekayaan.bersih === N.aset - N.kewajiban && Q4.lampu.length === 5 && Q4.lampu[0].nilai === pdPctTeks(N.kewajiban / N.aset * 100) && Q4.lampu[2].lampu === 'merah' && Q4.lampu[4].nilai === '75 %' && Q4.lampu[4].lampu === 'tanpa', J(Q4.lampu));
ambang({ utangMaks: 5, pemasokMaks: 70 }); var Q4b = kwRekap('2026-K4', KINI); ok('kuartal: ambang owner Pondasi ikut mewarnai potret kuartal', Q4b.lampu[0].lampu === 'merah' && Q4b.lampu[4].lampu === 'merah', J(Q4b.lampu)); aturDengan([]);
ok('kuartal K3: tanpa hitungan tutup hari akhir September → kekayaan akhir kuartal BELUM bisa dihitung & disebut (tidak ditebak dari titik kas sekarang)', Q3.kekayaan.ada === false && /belum bisa dihitung/.test(Q3.kekayaan.kenapa) && Q3.lampu[0].lampu === 'tanpa' && Q3.lampu[0].nilai === 'belum bisa' && Q4.kekayaanNaik === null, J(Q3.kekayaan));
pasok('tutupHari', [{ id: 'tq3', tanggal: '2026-09-29', jam: '21:00', titik: { laci: 5000000, rekening: 2000000, amplop: 0, brankas: 1000000 } }]);
var Q3b = kwRekap('2026-K3', KINI); var Q4c = kwRekap('2026-K4', KINI); var NS = neracaPada('2026-09-30', KINI, lpKasAkhirBulan('2026-09'));
ok('kuartal K3: dengan hitungan tutup hari 29 Sep (8 jt, tangan) → kekayaan akhir kuartal terhitung = Neraca berkop 30 Sep; K4 menyebut naik/turunnya', Q3b.kekayaan.ada && NS.N.kas === 8000000 && Q3b.kekayaan.aset === NS.aset && Q3b.kekayaan.bersih === NS.aset - NS.kewajiban && Q4c.kekayaanNaik === (N.aset - N.kewajiban) - (NS.aset - NS.kewajiban), J([Q3b.kekayaan, NS.N.kas, Q4c.kekayaanNaik]));

// ---- kekayaan dari waktu ke waktu
var KY = pdKekayaan(KINI); var ky = function (k) { return KY.bulan.find(function (b) { return b.key === k; }); };
ok('kekayaan: tiap akhir bulan sejak catatan pertama, terbaru dulu; bulan berjalan = Neraca hari ini; September dari tutup hari 29 Sep; Oktober tanpa hitungan → DISEBUT', J(KY.bulan.map(function (b) { return b.key; })) === J(['2026-11', '2026-10', '2026-09']) && ky('2026-11').ada && ky('2026-11').bersih === N.aset - N.kewajiban && ky('2026-11').per === '2026-11-18' && ky('2026-09').ada && ky('2026-09').bersih === NS.aset - NS.kewajiban && ky('2026-09').per === '2026-09-30' && ky('2026-10').ada === false && /belum bisa dihitung/.test(ky('2026-10').kenapa), J(KY.bulan));
ok('kekayaan: naik/turun dibanding titik SEBELUMNYA yang bisa dihitung (Nov vs Sep, melompati Okt), ringkasannya menyebut arah & rupiahnya', ky('2026-11').naik === ky('2026-11').bersih - ky('2026-09').bersih && ky('2026-09').naik === null && KY.ubah === ky('2026-11').naik && (KY.ubah >= 0 ? /NAIK/ : /TURUN/).test(KY.kalimat) && KY.n === 2, J([KY.kalimat, KY.ubah]));
pasang();

// ---- risiko: skenario murni (tangan) & pola hari
var SK1 = pdSkenario(10000000, 2000000, 6000000, 10), SK3 = pdSkenario(10000000, 2000000, 6000000, 30), SK0 = pdSkenario(10000000, 2000000, 0, 30);
ok('risiko (tangan): laba kotor 10 jt, laba bersih 2 jt — turun 10 % → hilang 1 jt, masih untung 1 jt; turun 30 % → rugi 1 jt per 30 hari, uang 6 jt tahan 180 hari; uang nol → 0 hari', SK1.hilang === 1000000 && SK1.laba === 1000000 && SK1.tahanHari === null && SK3.laba === -1000000 && Math.abs(SK3.tahanHari - 180) < 1e-6 && SK0.tahanHari === 0, J([SK1, SK3, SK0]));
ok('risiko (tangan): omzet boleh turun paling banyak = laba bersih ÷ laba kotor (2 dari 10 jt = 20 %); sudah rugi / laba kotor nol → tidak ada batas', pdBatasTurun(10000000, 2000000) === 20 && pdBatasTurun(10000000, -1) === null && pdBatasTurun(0, 5) === null && pdBatasTurun(1000, 5000) === 100);
var RS = pdRisiko(KINI);
ok('risiko: angka dasarnya = mesin laba 30 hari & uang toko Neraca; toko kotak pasir sedang rugi → tidak ada batas turun, kalimatnya menyebut RUGI', RS.laba === L30.labaBersih && RS.labaKotor === L30.margin && RS.kas === S0.total && RS.batas === null && /sudah RUGI/.test(RS.kalimat) && RS.skenario.length === 4 && RS.skenario[1].laba === pdSkenario(L30.margin, L30.labaBersih, S0.total, 20).laba, J([RS.kalimat, RS.skenario[1]]));
var PL = pdPolaHari(KINI); var HT = hariTerakhir(KINI, 57).filter(function (d) { return !d.hariIni; }); var jmlHT = HT.reduce(function (a, d) { return a + d.omzet; }, 0);
var dpn = 0; for (var kk = 1; kk <= 30; kk++) dpn += PL.per[new Date(ugTambahHari('2026-11-18', kk) + 'T00:00:00').getDay()].rata;
ok('pola hari: 56 hari terakhir TANPA hari ini, dibagi per nama hari (tiap nama hari 8 kali); Σ per hari = Σ omzet 56 hari; prakiraan 30 hari = Σ rata-rata hari-harinya', PL.ada && PL.nHari === 56 && PL.per.every(function (x) { return x.n === 8; }) && Math.abs(PL.per.reduce(function (a, x) { return a + x.rp; }, 0) - jmlHT) < 0.5 && PL.depan === Math.round(dpn) && PL.ramai.rata >= PL.sepi.rata, J([PL, jmlHT]));
ok('pola hari (tangan): 18 Nov 2026 = Rabu; Selasa = nota 3 Nov 700 rb − uang retur 10 Nov 72 rb = 628 rb dalam 8 Selasa → rata-rata 78.500', new Date('2026-11-18T00:00:00').getDay() === 3 && PL.per[2].nama === 'Selasa' && PL.per[2].rp === 628000 && PL.per[2].rata === 78500, J(PL.per[2]));

// ---- rantai pasok
pasok('pesananPemasok', [{ id: 'ps1', tanggal: '2026-10-28', jam: '09:00', pemasok: 'Roda Contoh', status: '' }, { id: 'ps2', tanggal: '2026-11-10', jam: '09:00', pemasok: 'Roda Contoh', status: '' },
  { id: 'ps3', tanggal: '2026-09-25', jam: '09:00', pemasok: 'Sumber Contoh', status: 'batal' }, { id: 'ps4', tanggal: '2026-09-28', jam: '09:00', pemasok: 'Sumber Contoh', status: 'datang', datangTanggal: '2026-10-01' }]);
var LK = bpLamaKirim(KINI, 180); var lk = function (nm) { return LK.pemasok.find(function (x) { return x.nama === nm; }); };
ok('lama kirim (tangan): dipesan 28 Okt → datang 2 Nov = 5 hari; 28 Sep → 1 Okt = 3 hari; rata-rata 4 hari; pesanan 10 Nov masih MENUNGGU (disebut, tidak dihitung); yang batal tidak ikut', LK.n === 2 && lk('Roda Contoh').rataHari === 5 && lk('Sumber Contoh').rataHari === 3 && LK.rataHari === 4 && LK.menunggu === 1 && lk('Sumber Contoh').n === 1, J(LK));
pasok('batchMasuk', K1.batchMasuk.concat([{ id: 'b3', tanggal: '2026-11-15', jam: '08:00', pemasok: 'Roda Contoh', caraBayar: 'tunai', biayaBongkar: 0, merkList: [{ merk: 'Angsa', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, subtotalHarga: 1350000, hargaPerKg: 13500 }] }]));
var RN = pdRantai(KINI); var rn = function (nm) { return RN.pemasok.find(function (x) { return x.nama === nm; }); };
ok('rantai pasok: per pemasok porsi belanja, lama kirim & gerak harga beli (Angsa 13.300 → 13.500 = 1 merek naik, tangan); pesanan 10 Nov kini datang 15 Nov (5 hari) → tidak ada yang menunggu; urut belanja terbesar', RN.pemasok.length === 2 && RN.pemasok[0].nama === 'Roda Contoh' && rn('Roda Contoh').naik === 1 && rn('Roda Contoh').turun === 0 && rn('Roda Contoh').gerak[0].dari === 13300 && rn('Roda Contoh').gerak[0].ke === 13500 && rn('Roda Contoh').rp === 14700000 && Math.abs(rn('Roda Contoh').pct - 14700000 / 19150000 * 100) < 1e-9 && rn('Sumber Contoh').naik + rn('Sumber Contoh').turun === 0 && /belum ada merek dengan dua kedatangan/.test(rn('Sumber Contoh').kalimat) && rn('Sumber Contoh').kirim.rataHari === 3 && rn('Roda Contoh').kirim.n === 2 && rn('Roda Contoh').kirim.rataHari === 5 && RN.nPesananMenunggu === 0 && !/menunggu datang/.test(RN.kalimat), J(RN));
ok('porsi pemasok: rentang dipakai apa adanya (hanya Oktober → Sumber Contoh 100 %)', (function () { var X = pdPorsiPemasok('2026-10-01', '2026-10-31'); return X.daftar.length === 1 && X.daftar[0].nama === 'Sumber Contoh' && X.pct === 100 && X.total === 4450000; })());
pasang(); pasok('pesananPemasok', []);

// ---- organisasi: siapa mencatat apa
var nota = function (id, oleh, lain) { return Object.assign({ id: id, grupNota: 'g' + id, tanggal: '2026-11-12', jam: '10:00', caraBayar: 'Tunai', namaPelanggan: '', jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 1, totalKg: 50, hargaTotal: 700000, hppTotalSaatJual: 660000, oleh: oleh }, lain || {}); };
pasok('penjualan', K1.penjualan.concat([nota('po1', 'Orang A'), nota('po2', 'Orang A', { dibatalkan: true }), nota('po3', 'Orang B', { negoSelisih: -500, hargaAsliSatuan: 14000, hargaTotal: 675000, jumlahKarung: 1 }), nota('po4', 'Orang B', { tanggal: '2026-10-01' })]));
pasok('tutupHari', [{ id: 'to1', tanggal: '2026-11-12', jam: '21:00', oleh: 'Orang A', selisihLaci: -2000 }, { id: 'to2', tanggal: '2026-11-13', jam: '21:00', oleh: 'Orang A', selisihLaci: 0 }, { id: 'to3', tanggal: '2026-10-01', jam: '21:00', oleh: 'Orang A', selisihLaci: -9000 }]);
var PO = rwPerOrang('2026-10-20', '2026-11-18'); var po = function (nm) { return PO.orang.find(function (x) { return x.nama === nm; }); };
ok('nota per orang (tangan): Orang A 1 nota berlaku 700 rb + 1 dibatalkan; Orang B 1 nota 675 rb (nota 1 Okt di luar rentang); nota tanpa nama pencatat dikumpulkan sendiri', po('Orang A').nota === 1 && po('Orang A').omzet === 700000 && po('Orang A').batal === 1 && po('Orang B').nota === 1 && po('Orang B').omzet === 675000 && po('Orang B').batal === 0 && po('').nota > 0 && po('').batal === 1, J(PO));
var OG = pdOrganisasi(KINI); var og = function (nm) { return OG.orang.find(function (x) { return x.nama === nm; }); };
ok('organisasi (tangan): Orang A 2 tutup hari, 1 malam berselisih −2 rb (tutup 1 Okt di luar 30 hari); Orang B 1 nego potongan Rp500; nota tanpa nama pencatat DISEBUT', og('Orang A').tutup === 2 && og('Orang A').nSelisih === 1 && og('Orang A').selisih === -2000 && og('Orang A').batal === 1 && og('Orang B').nego === 1 && og('Orang B').potongan === 500 && og('Orang B').tutup === 0 && OG.tanpaNama === po('').nota && /tanpa nama pencatat/.test(OG.kalimat) && og('').tampil === 'tanpa nama pencatat' && OG.nBatal === 2, J(OG));
pasang();
ok('mulus paket kedua: kekayaan, rantai pasok, risiko & organisasi diingat per versi data (ketukan tidak menghitung ulang)', pdKekayaan(KINI) === pdKekayaan(KINI) && pdRantai(KINI) === pdRantai(KINI) && pdRisiko(KINI) === pdRisiko(KINI) && pdOrganisasi(KINI) === pdOrganisasi(KINI));

// ==================== paket ketiga: PELANGGAN (pilar marketing) ====================
// tangan: Bu Uji Besar 3 nota × 7 jt (5, 10, 15 Nov; modal 6,6 jt → laba kotor 3 × 400 rb) · Pak Uji Kecil 1 nota 300 rb (12 Nov) · Pak Uji Balik 2 nota × 400 rb
// (1 Sep & 11 Nov) · Bu Uji Lama 3 nota Agustus (10, 20, 30 → selang 10 hari, terakhir 80 hari lalu = bangku kosong; di luar Sep–Nov) · 1 nota tanpa nama 500 rb
var PL0 = pdPelanggan(KINI);
var nj = function (id, nama, tgl, harga, hpp) { return { id: id, grupNota: 'g' + id, tanggal: tgl, jam: '10:00', caraBayar: 'Tunai', namaPelanggan: nama, jenis: 'karung', merkSumber: 'Angsa', beratKarungAcuan: 50, jumlahKarung: 1, totalKg: 50, hargaTotal: harga, hppTotalSaatJual: hpp }; };
var NOTA_PL = [nj('pl1', 'Bu Uji Besar', '2026-11-05', 7000000, 6600000), nj('pl2', 'Bu Uji Besar', '2026-11-10', 7000000, 6600000), nj('pl3', 'Bu Uji Besar', '2026-11-15', 7000000, 6600000),
  nj('pl4', 'Pak Uji Kecil', '2026-11-12', 300000, 280000), nj('pl5', 'Pak Uji Balik', '2026-09-01', 400000, 380000), nj('pl6', 'Pak Uji Balik', '2026-11-11', 400000, 380000),
  nj('pl7', 'Bu Uji Lama', '2026-08-10', 200000, 190000), nj('pl8', 'Bu Uji Lama', '2026-08-20', 200000, 190000), nj('pl9', 'Bu Uji Lama', '2026-08-30', 200000, 190000), nj('pl10', '', '2026-11-14', 500000, 470000)];
var SETP = { id: 'hargaTingkat', tingkat: [{ id: 'warung', nama: 'Warung', potKg: 0 }], barang: {}, orang: { 'bu uji besar': 'warung' }, khusus: [] };
var aturPl = function (maks) { aturDengan([SETP].concat(maks === null ? [] : [{ id: 'pondasi', pembeliMaks: maks }])); };
pasok('penjualan', K1.penjualan.concat(NOTA_PL)); aturPl(null);
var PL1 = pdPelanggan(KINI); var pb = function (X, nm) { return X.pembeli.find(function (o) { return o.nama === nm; }); }; var sg = function (X, id) { return X.segmen.find(function (g) { return g.id === id; }); };
var BL = pelangganBulan('2026-11', 3, KINI);
ok('pelanggan: sumber menutup — Σ pembeli bernama + nota tanpa nama = omzet barang = Σ kelompok; angka per pelanggan menutup ke Laporan', BL.menutup && Math.abs(BL.pembeli.reduce(function (a, o) { return a + o.omzet; }, 0) + BL.tanpaNama.omzet - BL.omzetBarang) < 0.5 && Math.abs(BL.tingkat.reduce(function (a, g) { return a + g.omzet; }, 0) - BL.omzetBarang) < 0.5 && PL1.menutup, J([BL.omzetBarang, BL.tanpaNama, BL.kalimat]));
ok('pelanggan (tangan): omzet bernama Sep–Nov naik 21 jt + 300 rb + 800 rb = 22,1 jt (nota Agustus di luar tiga bulan); nota tanpa nama naik 1 nota 500 rb; orang bernama +3', PL1.dikenal.omzetNama - PL0.dikenal.omzetNama === 22100000 && PL1.dikenal.omzetTanpa - PL0.dikenal.omzetTanpa === 500000 && PL1.dikenal.nNotaTanpa - PL0.dikenal.nNotaTanpa === 1 && PL1.dikenal.nOrang - PL0.dikenal.nOrang === 3 && PL1.dikenal.omzet - PL0.dikenal.omzet === 22600000 && Math.abs(PL1.dikenal.pct - PL1.dikenal.omzetNama / PL1.dikenal.omzet * 100) < 1e-9, J([PL0.dikenal, PL1.dikenal]));
ok('pelanggan (tangan): pembeli terbesar Bu Uji Besar 21 jt, 3 nota, laba kotor 1,2 jt, porsi = 21 jt ÷ omzet barang; ia pelanggan usaha tingkat Warung; daftar paling banyak ' + PD_PEMBELI_TERATAS + ' orang, omzet terbesar dulu', PL1.terbesar && PL1.terbesar.nama === 'Bu Uji Besar' && PL1.terbesar.omzet === 21000000 && PL1.terbesar.nNota === 3 && PL1.terbesar.labaKotor === 1200000 && Math.abs(PL1.terbesar.pct - 21000000 / PL1.dikenal.omzet * 100) < 1e-9 && PL1.terbesar.usaha === true && PL1.terbesar.tingkatNama === 'Warung' && PL1.pembeli.length <= PD_PEMBELI_TERATAS && PL1.pembeli.every(function (o, i) { return !i || PL1.pembeli[i - 1].omzet >= o.omzet; }), J(PL1.pembeli));
ok('pelanggan (tangan): kelompok Warung = 1 orang, omzet 21 jt, laba kotor 1,2 jt, margin 1,2 ÷ 21 = 5,71 %; pembeli umum tetap ada; kalimat menyebut nota tanpa nama & pembeli terbesar', sg(PL1, 'warung') && sg(PL1, 'warung').nOrang === 1 && sg(PL1, 'warung').omzet === 21000000 && sg(PL1, 'warung').labaKotor === 1200000 && Math.abs(sg(PL1, 'warung').margin - 1200000 / 21000000 * 100) < 1e-9 && !!sg(PL1, 'eceran') && /nota tanpa nama/.test(PL1.kalimat) && /Pembeli terbesar Bu Uji Besar/.test(PL1.kalimat) && PL1.ada === true, J([PL1.segmen, PL1.kalimat]));
var pctB = PL1.terbesar.pct;
ok('pelanggan: warna pembeli terbesar hanya dari ambang owner — mati = tanpa warna', PL1.lampu === 'tanpa' && /belum diatur/.test(PL1.ambang), J([PL1.lampu, PL1.ambang]));
aturPl(Math.floor(pctB) - 1); ok('pelanggan: porsi lewat ambang owner → merah', pdPelanggan(KINI).lampu === 'merah' && /ambang owner/.test(pdPelanggan(KINI).ambang), J([pctB, pdPelanggan(KINI).lampu]));
aturPl(Math.min(100, Math.round(pctB * 1.05 * 100) / 100)); ok('pelanggan: porsi dalam ' + PD_DEKAT + ' % di bawah ambang → kuning', pdPelanggan(KINI).lampu === 'amber', J([pctB, pdAtur().pembeliMaks, pdPelanggan(KINI).lampu]));
if (pctB < 89) { aturPl(100); ok('pelanggan: porsi jauh di bawah ambang → aman', pdPelanggan(KINI).lampu === 'hijau', J([pctB, pdPelanggan(KINI).lampu])); } else ok('pelanggan: kotak pasir tidak cocok untuk uji aman (porsi ≥ 89 %)', false, String(pctB));
aturPl(null);
ok('datang lagi (tangan, 30 hari = 20 Okt–18 Nov): baru +2 (Bu Uji Besar, Pak Uji Kecil) · kembali +1 (Pak Uji Balik, pertama 1 Sep) · orang lama +2 (Pak Uji Balik, Bu Uji Lama) · bangku kosong +1', PL1.datang.baru - PL0.datang.baru === 2 && PL1.datang.kembali - PL0.datang.kembali === 1 && PL1.datang.lama - PL0.datang.lama === 2 && PL1.datang.nKosong - PL0.datang.nKosong === 1 && PL1.datang.nDatang - PL0.datang.nDatang === 3 && PL1.datang.dari === '2026-10-20', J([PL0.datang, PL1.datang]));
var OS = semuaOrang(KINI); var os = function (nm) { return OS.find(function (o) { return o.nama === nm; }); };
ok('datang lagi (tangan): Bu Uji Lama selang 10 hari, terakhir 30 Agu = 80 hari lalu → bangku kosong; kunjungan pertama tercatat (Pak Uji Balik 1 Sep, terakhir 11 Nov)', os('Bu Uji Lama').selang === 10 && os('Bu Uji Lama').sejak === 80 && os('Bu Uji Lama').kosong === true && os('Bu Uji Lama').pertama === '2026-08-10' && os('Pak Uji Balik').pertama === '2026-09-01' && os('Pak Uji Balik').terakhir === '2026-11-11' && os('Pak Uji Balik').kosong === false, J([os('Bu Uji Lama').selang, os('Bu Uji Lama').sejak, os('Pak Uji Balik').pertama]));
ok('pelanggan: diingat per versi data (ketukan tidak menghitung ulang)', pdPelanggan(KINI) === pdPelanggan(KINI));
pasok('penjualan', []); var PLk = pdPelanggan(KINI);
ok('pelanggan: tanpa jualan → disebut "belum ada jualan", tanpa warna, tanpa daftar — tidak jatuh & tidak dianggap 0 %', PLk.ada === false && PLk.lampu === 'tanpa' && PLk.pembeli.length === 0 && PLk.terbesar === null && PLk.dikenal.pct === null && /Belum ada jualan/.test(PLk.kalimat), J(PLk));
var Spm = susunAturPondasi({ pembeliMaks: '40' }, W); ok('setelan: ambang satu pembeli disimpan di aturanToko/pondasi; lewat 100 % ditolak', !Spm.tolak && Spm.dokumen[0].data.pembeliMaks === 40 && !!susunAturPondasi({ pembeliMaks: '101' }, W).tolak, J(Spm));
pasang();

// ==================== PR B: target per kuartal · rapor kuartal · pengingat ====================
ok('target (tangan): lampu = tercapai hijau · belum tercapai tapi sesuai laju hari kuning · di bawah laju merah · kuartal SELESAI tidak ada kuning · tanpa target / tanpa angka = tanpa warna',
  kwLampuTarget(100, 100, 0.5) === 'hijau' && kwLampuTarget(60, 100, 0.5) === 'amber' && kwLampuTarget(50, 100, 0.5) === 'amber' && kwLampuTarget(40, 100, 0.5) === 'merah' && kwLampuTarget(90, 100, 1) === 'merah' && kwLampuTarget(90, 0, 0.5) === 'tanpa' && kwLampuTarget(null, 100, 0.5) === 'tanpa');
ok('kuartal: kunci, geser, awal & nama = SATU sumber (sistem-logika) dipakai Laporan & pengingat', ssKuartalKey('2026-11-18') === kwKey('2026-11-18') && ssKuartalGeser('2026-K4', 1) === '2027-K1' && ssKuartalAwal('2026-K4') === '2026-10-01' && ssKuartalAwal('2027-K1') === kwRentang('2027-K1').awal && ssKuartalNama('2027-K1') === 'K1 2027');
var TQ1 = susunTargetKuartal('2026-K4', { omzet: '3.000.000', labaBersih: '', utangMaks: '5000000' }, W);
ok('target: disimpan ke aturanToko/pondasi.targetKuartal[kuartal]; titik ribuan dibaca; kosong = tidak ditarget', !TQ1.tolak && TQ1.dokumen.length === 1 && TQ1.dokumen[0].koleksi === 'aturanToko' && TQ1.dokumen[0].data.id === 'pondasi' && J(TQ1.dokumen[0].data.targetKuartal) === J({ '2026-K4': { omzet: 3000000, utangMaks: 5000000 } }) && TQ1.patch.aturTq === null, J(TQ1));
ok('target: ketikan rusak DITOLAK (huruf, nol, pecahan, kuartal tidak dikenal)', !!susunTargetKuartal('2026-K4', { omzet: 'abc' }, W).tolak && !!susunTargetKuartal('2026-K4', { omzet: '0' }, W).tolak && !!susunTargetKuartal('2026-K4', { omzet: '1,5' }, W).tolak && !!susunTargetKuartal('2026-K5', { omzet: '1000' }, W).tolak && !!susunTargetKuartal('K4', { omzet: '1000' }, W).tolak);
aturDengan([{ id: 'pondasi', utangMaks: 150, targetKuartal: { '2026-K3': { omzet: 111 }, '2026-K4': { omzet: 3000000, utangMaks: 5000000 } } }]);
var TQ2 = susunTargetKuartal('2026-K4', { labaBersih: '250000' }, W);
ok('target: simpan satu target TIDAK menimpa target lain, kuartal lain, atau ambang lampu; pembaca & drafnya sama', J(TQ2.dokumen[0].data.targetKuartal) === J({ '2026-K3': { omzet: 111 }, '2026-K4': { omzet: 3000000, labaBersih: 250000, utangMaks: 5000000 } }) && TQ2.dokumen[0].data.utangMaks === 150 && ssTargetKuartal('2026-K4').omzet === 3000000 && ssTargetKuartal('2026-K4').ada === true && ssTargetKuartal('2027-K1').ada === false && pdDrafTarget('2026-K4').utangMaks === '5000000' && pdDrafTarget('2026-K4').labaBersih === '' && pdAtur().utangMaks === 150, J([TQ2, pdDrafTarget('2026-K4')]));
var TQ3 = susunTargetKuartal('2026-K3', { omzet: '' }, W);
ok('target: mengosongkan satu-satunya target kuartal menghapus kuartal itu dari daftar; tidak ada yang diubah → ditolak', !TQ3.tolak && J(Object.keys(TQ3.dokumen[0].data.targetKuartal)) === J(['2026-K4']) && susunTargetKuartal('2026-K4', { omzet: '3000000' }, W).tolak === 'Tidak ada yang diubah');
var QT = kwRekap('2026-K4', KINI); var tg = function (Q, id) { return Q.target.baris.find(function (b) { return b.id === id; }); };
ok('target K4 (tangan): hari ke-49 dari 92 (1 Okt – 18 Nov); utang 4,8 jt di bawah batas 5 jt = aman; omzet dinilai dengan laju hari', QT.target.ada && QT.target.hariLewat === 49 && QT.target.hariSemua === 92 && Math.abs(QT.target.bagian - 49 / 92) < 1e-12 && tg(QT, 'utangMaks').lampu === 'hijau' && tg(QT, 'utangMaks').capai === 4800000 && tg(QT, 'omzet').lampu === kwLampuTarget(QT.omzet, 3000000, 49 / 92) && tg(QT, 'omzet').laju === Math.round(3000000 * 49 / 92) && tg(QT, 'labaBersih').lampu === 'tanpa', J(QT.target));
aturDengan([{ id: 'pondasi', targetKuartal: { '2026-K4': { omzet: QT.omzet + 1, labaBersih: 1000000, utangMaks: 4000000 } } }]);
var QT2 = kwRekap('2026-K4', KINI);
ok('target K4: omzet kurang Rp1 dari target tapi di atas laju = kuning; toko rugi vs target laba 1 jt = merah di bawah laju; utang 4,8 jt lewat batas 4 jt = merah, lebihnya 800 rb (tangan)', tg(QT2, 'omzet').lampu === 'amber' && /sesuai laju/.test(tg(QT2, 'omzet').teks) && tg(QT2, 'labaBersih').lampu === 'merah' && /DI BAWAH laju/.test(tg(QT2, 'labaBersih').teks) && tg(QT2, 'utangMaks').lampu === 'merah' && /lebih Rp800\.000 dari Rp4\.000\.000/.test(tg(QT2, 'utangMaks').teks), J(QT2.target));
aturDengan([{ id: 'pondasi', targetKuartal: { '2026-K3': { omzet: Q3.omzet + 1 } } }]);
ok('target kuartal yang SUDAH selesai: kurang Rp1 = TIDAK tercapai (merah, tidak ada kuning)', tg(kwRekap('2026-K3', KINI), 'omzet').lampu === 'merah' && /TIDAK tercapai/.test(tg(kwRekap('2026-K3', KINI), 'omzet').teks) && kwRekap('2026-K3', KINI).target.bagian === 1);
aturDengan([]);
ok('tanpa target: disebut belum diisi, tidak ada lampu yang berwarna', QT && kwRekap('2026-K4', KINI).target.ada === false && /belum diisi/.test(kwRekap('2026-K4', KINI).target.kalimat) && kwRekap('2026-K4', KINI).target.baris.every(function (b) { return b.lampu === 'tanpa'; }));

// ---- rapor kuartal berkop
var RP4 = kwRapor('2026-K4', KINI); var rb = function (D, nama) { var r = D.baris.find(function (x) { return x.nama === nama; }); return r ? r.teks : null; };
ok('rapor kuartal: bentuk dokumen berkop (judul, sub, baris, catatan, kop) dengan angka kwRekap apa adanya; kuartal belum utuh → bercap DRAF & sebabnya di sub', RP4.jenis === 'kuartal' && RP4.judul === 'Rapor Kuartal K4 2026' && RP4.cap === 'DRAF' && RP4.final === false && /DRAF — masih berjalan/.test(RP4.sub) && rb(RP4, 'Laba bersih') === RP(Q4.labaBersih) && rb(RP4, 'Tinggal di toko') === RP(Q4.tinggal) && rb(RP4, 'Ambil pribadi owner') === RP(-300000) && rb(RP4, 'Kekayaan bersih') === RP(N.aset - N.kewajiban) && rb(RP4, 'Bergantung pada satu pemasok') === '75 %' && /merah$/.test(rb(RP4, 'Ambil pribadi dibanding laba')) && RP4.baris.some(function (r) { return r.kelas === 'kel' && r.nama === 'Potret pondasi'; }) && !RP4.baris.some(function (r) { return r.nama === 'Target owner'; }) && !!RP4.kop, J(RP4));
ok('rapor kuartal: syarat kop sama dengan laporan berkop lain (kop belum lengkap → ditolak dengan kalimat yang sama); teks WA-nya memuat judul & nomor', RP4.tolak === laporanBerkop('labarugi', '2026-11', 1, KINI).tolak && /RAPOR KUARTAL K4 2026 — DRAF/.test(teksDokumen(RP4, 7, '2026-11-18')) && /No\. 7/.test(teksDokumen(RP4, 7, '2026-11-18')), J([RP4.tolak, teksDokumen(RP4, 7, '2026-11-18').slice(0, 200)]));
aturDengan([{ id: 'pondasi', targetKuartal: { '2026-K4': { utangMaks: 4000000 } } }]);
ok('rapor kuartal: target yang diisi ikut tercetak dengan warnanya', (function () { var D = kwRapor('2026-K4', KINI); return D.baris.some(function (r) { return r.nama === 'Target owner'; }) && /Rp4\.800\.000 · merah$/.test(rb(D, 'Utang hari ini — target Rp4.000.000')); })(), J(kwRapor('2026-K4', KINI).baris.slice(-9)));
aturDengan([]);

// ---- pengingat target kuartal
var pk = function (kini) { return ssSumberPengingat(kini).filter(function (p) { return p.jenis === 'kuartal'; }); };
ok('pengingat: jenis "kuartal" terdaftar (bawaan 7 hari sebelum, ke Owner); 18 Nov: sumbernya K1 2027 (jatuh 1 Jan 2027) saja — K4 yang sudah berjalan 49 hari TIDAK ditagih; belum aktif (44 hari lagi)', SS_JENIS_PENGINGAT.some(function (j) { return j.id === 'kuartal' && j.kunci === 'hariKuartal'; }) && ssAtur('pengingat').hariKuartal === 7 && J(ssAtur('pengingat').ke.kuartal) === J(['Owner']) && J(pk(KINI).map(function (p) { return [p.id, p.jatuh]; })) === J([['kuartal|2027-K1', '2027-01-01']]) && !ssPengingat(KINI).aktif.some(function (p) { return p.jenis === 'kuartal'; }), J(pk(KINI)));
var K26 = new Date('2026-12-26T10:00:00+07:00');
ok('pengingat: 26 Des (6 hari sebelum 1 Jan) → "Isi target K1 2027" aktif', ssPengingat(K26).aktif.some(function (p) { return p.id === 'kuartal|2027-K1' && p.teks === 'Isi target K1 2027' && p.sisa === 6; }), J(ssPengingat(K26).aktif.map(function (p) { return [p.id, p.sisa]; })));
aturDengan([{ id: 'pondasi', targetKuartal: { '2027-K1': { omzet: 5000000 } } }]);
ok('pengingat: target K1 2027 sudah diisi → tidak diingatkan lagi', pk(K26).length === 0, J(pk(K26))); aturDengan([]);
ok('pengingat: kuartal berjalan yang targetnya kosong ditagih hanya 14 hari pertamanya (5 Jan ya, 20 Jan tidak)', pk(new Date('2027-01-05T10:00:00+07:00')).some(function (p) { return p.id === 'kuartal|2027-K1' && /sudah berjalan/.test(p.teks); }) && !pk(new Date('2027-01-20T10:00:00+07:00')).some(function (p) { return p.id === 'kuartal|2027-K1'; }), J([pk(new Date('2027-01-05T10:00:00+07:00')), pk(new Date('2027-01-20T10:00:00+07:00'))]));
pasang();

// ==================== PR C: buku pegangan (rules v20) ====================
ok('pegangan: belum ada isi → disebut, bukan galat; tidak ada bab untuk siapa pun', ssPegangan().ada === false && ssPegangan().teks === 'belum ada isinya' && ssPeganganUntuk('ben').length === 0 && ssPeganganUntuk('owner').length === 0 && ssDrafBab('').untuk === 'semua');
var BB1 = susunBabPegangan({ id: '', judul: '  Buka toko pagi ', isi: 'Hitung uang kembalian.\r\nCek timbangan.  ', untuk: 'semua' }, W);
ok('pegangan: bab baru → SATU dokumen aturanToko/bukuPegangan berisi bab saja (id · bab · tanggal · jam); judul dirapikan, baris baru disatukan, id bab baru', !BB1.tolak && BB1.dokumen.length === 1 && BB1.dokumen[0].koleksi === 'aturanToko' && BB1.dokumen[0].data.id === 'bukuPegangan' && BB1.dokumen[0].data.bab.length === 1 && BB1.dokumen[0].data.bab[0].judul === 'Buka toko pagi' && BB1.dokumen[0].data.bab[0].isi === 'Hitung uang kembalian.\nCek timbangan.' && /^bab-/.test(BB1.dokumen[0].data.bab[0].id) && J(Object.keys(BB1.dokumen[0].data).sort()) === J(['bab', 'id', 'jam', 'tanggal']) && J(Object.keys(BB1.dokumen[0].data.bab[0]).sort()) === J(['id', 'isi', 'judul', 'untuk']) && BB1.patch.bpgDraf === null, J(BB1));
var bbTolak = function (d) { return !!susunBabPegangan(d, W).tolak; };
ok('pegangan: ketikan ditolak dengan kalimat — judul < 3 huruf, isi kosong, untuk tidak dipilih / tak dikenal, judul > 80 huruf, isi > 2.000 huruf', bbTolak({ judul: 'ab', isi: 'isi yang cukup', untuk: 'semua' }) && bbTolak({ judul: 'Judul', isi: '   ', untuk: 'semua' }) && bbTolak({ judul: 'Judul', isi: 'isi yang cukup', untuk: '' }) && bbTolak({ judul: 'Judul', isi: 'isi yang cukup', untuk: 'owner' }) && bbTolak({ judul: new Array(82).join('x'), isi: 'isi yang cukup', untuk: 'semua' }) && bbTolak({ judul: 'Judul', isi: new Array(2002).join('x'), untuk: 'semua' }) && !bbTolak({ judul: new Array(81).join('x'), isi: new Array(2001).join('x'), untuk: 'ben' }));
var BKU = { id: 'bukuPegangan', tanggal: '2026-11-24', jam: '10:00', kolomLama: 'x', bab: [{ id: 'b1', judul: 'Buka toko', isi: 'Hitung laci.', untuk: 'semua' }, { id: 'b2', judul: 'Tutup hari', isi: 'Hitung laci, amankan.', untuk: 'ben' }, { id: 'b3', judul: 'Angkat karung', isi: 'Dua orang.', untuk: 'karyawan' }, { id: 'b4', judul: '', isi: 'tanpa judul', untuk: 'semua' }, { id: 'b5', judul: 'Peran aneh', isi: 'untuk tak dikenal', untuk: 'bos' }] };
aturDengan([BKU]); var idb = function (L) { return L.map(function (b) { return b.id; }); };
ok('pegangan: tiap peran hanya melihat bab "Semua" + bab perannya; owner melihat semua; bab tanpa judul dibuang, untuk tak dikenal dibaca Semua', J(idb(ssPeganganUntuk('ben'))) === J(['b1', 'b2', 'b5']) && J(idb(ssPeganganUntuk('karyawan'))) === J(['b1', 'b3', 'b5']) && J(idb(ssPeganganUntuk('owner'))) === J(['b1', 'b2', 'b3', 'b5']) && ssPegangan().n === 4 && ssPegangan().teks === '4 bab · terakhir diubah 24 Nov 2026' && ssPegangan().bab[1].untukNama === 'Penjaga laci', J([idb(ssPeganganUntuk('ben')), ssPegangan().teks]));
var BB2 = susunBabPegangan({ id: 'b2', judul: 'Tutup hari', isi: 'Hitung laci, catat selisih, amankan.', untuk: 'ben' }, W);
ok('pegangan: mengubah satu bab → bab lain & urutannya utuh, id tetap; kolom lain di dokumen TIDAK ikut ditulis ulang', !BB2.tolak && J(idb(BB2.dokumen[0].data.bab)) === J(['b1', 'b2', 'b3', 'b5']) && BB2.dokumen[0].data.bab[1].isi === 'Hitung laci, catat selisih, amankan.' && BB2.dokumen[0].data.bab[0].isi === 'Hitung laci.' && BB2.dokumen[0].data.kolomLama === undefined && ssDrafBab('b2').judul === 'Tutup hari', J(BB2));
ok('pegangan: judul kembar (huruf besar-kecil diabaikan), tidak ada yang diubah, dan bab yang sudah tidak ada → ditolak', susunBabPegangan({ id: '', judul: 'buka TOKO', isi: 'isi lain yang cukup', untuk: 'semua' }, W).tolak === 'Sudah ada bab berjudul "buka TOKO"' && susunBabPegangan({ id: 'b1', judul: 'Buka toko', isi: 'Hitung laci.', untuk: 'semua' }, W).tolak === 'Tidak ada yang diubah' && !!susunBabPegangan({ id: 'b9', judul: 'Bab hantu', isi: 'isi yang cukup', untuk: 'semua' }, W).tolak && !susunBabPegangan({ id: 'b1', judul: 'Buka toko', isi: 'Hitung laci.', untuk: 'ben' }, W).tolak);
var BH = susunHapusBab('b2', W), BG1 = susunGeserBab('b3', -1, W), BG2 = susunGeserBab('b1', 1, W);
ok('pegangan: hapus hanya bab itu; geser naik / turun menukar DUA bab bersebelahan; di ujung ditolak dengan kalimat', J(idb(BH.dokumen[0].data.bab)) === J(['b1', 'b3', 'b5']) && J(idb(BG1.dokumen[0].data.bab)) === J(['b1', 'b3', 'b2', 'b5']) && J(idb(BG2.dokumen[0].data.bab)) === J(['b2', 'b1', 'b3', 'b5']) && /paling atas/.test(susunGeserBab('b1', -1, W).tolak) && /paling bawah/.test(susunGeserBab('b5', 1, W).tolak) && !!susunHapusBab('b9', W).tolak && !!susunGeserBab('b9', 1, W).tolak, J([idb(BH.dokumen[0].data.bab), idb(BG1.dokumen[0].data.bab)]));
var banyak = []; for (var bi = 0; bi < 40; bi++) banyak.push({ id: 'x' + bi, judul: 'Bab nomor ' + bi, isi: 'isi bab ' + bi, untuk: 'semua' });
aturDengan([{ id: 'bukuPegangan', bab: banyak }]);
ok('pegangan: paling banyak 40 bab — bab ke-41 ditolak, mengubah bab yang ada tetap bisa', /Paling banyak 40 bab/.test(susunBabPegangan({ id: '', judul: 'Bab ke-41', isi: 'isi yang cukup', untuk: 'semua' }, W).tolak) && !susunBabPegangan({ id: 'x3', judul: 'Bab nomor 3', isi: 'isi diubah', untuk: 'semua' }, W).tolak);
aturDengan([]); pasang();

print(J({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Laporan memasang tab Pondasi + lembar ambang', 'laporan', ["import * as PD from './pondasi-logika.js';", "s.keluarga === 'pondasi' ? gambarPondasi(s, L)", 'function gambarPondasi(s, L)', 'PD.pdPondasi(kini())', 'PD.pdDisiplin(kini())', 'data-aksi="pdBuka"',
                                                     'pdAturSimpan: () => tulis(PD.susunAturPondasi(st().aturPd || {}, waktu()))', "'aturPd'", 'bukaPd: {}, aturPd: null']),
    ('Laporan: keluarga Pondasi terdaftar', 'laporanL', ["['neraca', 'Neraca'], ['pondasi', 'Pondasi'], ['dokumen', 'Dokumen']"]),
    ('Dasbor memasang kartu Pondasi', 'dasbor', ['function kartuPondasi(Q)', 'kartuPondasi(D.pondasi)', "daftar('pondasi:' + l.id"]),
    ('Dasbor logika: kelompok pondasi, dipertahankan & dipanaskan', 'dasborL', ["import { pdPondasi } from './pondasi-logika.js';", "pondasi: ['pondasi toko', dbPondasi]", 'pondasi: lama.pondasi', "pondasi: k('pondasi')", "'b2b', 'pondasi'];"]),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/pondasi-logika.js">']),
    ('CI menjalankan uji ini + kontrolnya', 'pages', ['python3 alat-uji/uji_pondasi.py && python3 alat-uji/uji_pondasi.py --kontrol']),
    ('bundel uji melengkapi modul untuk Dasbor', 'bundel', ["PD_MODUL = 'baru/js/layar/pondasi-logika.js'", "PD_PEMAKAI = ('dasbor-logika.js',)"]),
    ('gerak: deret lampu muncul bergiliran + hormat reduced motion', 'cssL', ['lpPdMuncul', 'lpPdDenyut', '.layar-laporan .lp-pd-titik, .layar-laporan .lp-pd-titik.merah { animation: none; }']),
    ('Dasbor: baris lampu dua kolom', 'cssR', ['.layar-ringkasan .db-pd-baris']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Pondasi', 'uji_pondasi.py', 'js/layar/pondasi-logika.js']),
    ('Laporan memasang keluarga Kuartal', 'laporan', ["import * as KW from './kuartal-logika.js';", "s.keluarga === 'kuartal' ? gambarKuartal(s, L)", 'function gambarKuartal(s, L)', 'KW.kwRekap(key, kini())', 'KW.kwTahun(KW.kwTahunDari(key), kini())', 'data-aksi="kwPilih"', 'kwPilih: ({ q }) => set({ kuartalQ: q']),
    ('Laporan: keluarga Kuartal terdaftar sesudah Bulanan', 'laporanL', ["['bulanan', 'Bulanan'], ['kuartal', 'Kuartal'], ['pajak', 'Pajak']"]),
    ('Pondasi memasang kartu Pelanggan (paket ketiga), dibungkus sendiri, di HP & layar lebar', 'laporan', ['data-k="pd-pelanggan"', "aman('pelanggan', () => PD.pdPelanggan(kini()))", '${rantai}${pelanggan}${disiplin}', '${daftar}${risiko}${pelanggan}', 'data-k="pdg-dikenal"', 'data-k="pdg-datang"']),
    ('pondasi-logika membaca pelanggan lewat fungsi sumber + ambang satu pembeli', 'pd', ["import { pelangganBulan } from './laba-pelanggan-logika.js';", "import { semuaOrang } from './pelanggan-logika.js';", "{ id: 'pembeliMaks', nama: 'Omzet dari satu pembeli paling banyak'"]),
    ('kalimat modal awal tidak lagi bilang "hanya setoran modal yang tercatat"', 'pd', ['hasil atas modal di sini memakai posisi toko pada hari pertama sistem mencatat']),
    ('Pondasi memasang empat kartu paket kedua, tiap kartu dibungkus sendiri', 'laporan', ['data-k="pd-kekayaan"', 'data-k="pd-rantai"', 'data-k="pd-risiko"', 'data-k="pd-organisasi"', "aman('kekayaan', () => PD.pdKekayaan(kini()))", "aman('organisasi', () => PD.pdOrganisasi(kini()))"]),
    ('modul kuartal dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/kuartal-logika.js">']),
    ('BACA-DULU menyebut paket kedua', 'baca', ['## Pondasi paket kedua', 'js/layar/kuartal-logika.js', 'bpLamaKirim', 'rwPerOrang']),
    ('Kuartal memasang kartu target, lembarnya & rapor berkop', 'laporan', ['data-k="kw-target"', 'kwTargetSimpan: () =>', 'PD.susunTargetKuartal(a.key || kwKeyAktif(), a, waktu())', "kertas(DR, null, 'kertas-kuartal')", "tigaTombol('kwKeluar', DR.tolak)", "await keluarkan(D, { jenis: 'kuartal', judul: 'Rapor kuartal'", "'aturPd', 'aturTq']"]),
    ('pengingat: jenis kuartal + satu sumber kunci & target', 'sl', ["['kuartal', 'Target kuartal belum diisi', 'hariKuartal']", 'hariKuartal: 7', 'export function ssTargetKuartal(key)', 'export const ssKuartalKey', "id: 'kuartal|' + kwDepan"]),
    ('BACA-DULU menyebut PR B', 'baca', ['PR B', 'susunTargetKuartal', 'kwRapor', 'hariKuartal']),
    ('Menu owner memasang lembar Buku pegangan + pintunya di Toko ini', 'menu', ["pegangan: 'Buku pegangan'", "s.sistem === 'pegangan' ? gambarPegangan(s)", 'function gambarPegangan(s)', 'bpgSimpan: () => tulis(S.susunBabPegangan(st().bpgDraf || {}, waktu()))', "'aturKpi', 'bpgDraf',", 'target: [], pegangan: []']),
    ('Menu staf (tablet) memasang kartu baca Buku pegangan untuk perannya', 'menu', ['${kartuPegangan(s, akunM)}', 'function kartuPegangan(s, akunM)', 'S.ssPeganganUntuk(akunM.peran)']),
    ('Toko ini: baris Buku pegangan', 'menuL', ["baris('pegangan', 'dokumen', 'Buku pegangan',", "sistem: 'pegangan'"]),
    ('rules v20 & halaman sepakat: bukuPegangan di daftar baca staf, salinan v19 tanpa itu, dokumen uji ada', 'rules', ["'hargaTingkat', 'produkArsip', 'bukuPegangan'] && staf(['ben', 'karyawan'])", 'ATURAN FIRESTORE v20 FINAL']),
    ('akses.js: staf mendengar dokumen bukuPegangan', 'akses', ["'hargaTingkat', 'produkArsip', 'bukuPegangan'], pengaturan:"]),
    ('salinan firestore.rules.v19 = rules sebelum buku pegangan', 'rules19', ["'hargaTingkat', 'produkArsip'] && staf(['ben', 'karyawan'])", 'ATURAN FIRESTORE v19 FINAL']),
    ('dokumen uji server v20 untuk owner', 'dok20', ['## Wajib owner', '★D1', '★D11', 'Terbitkan v20 SEBELUM PR']),
    ('gerak buku pegangan + hormat reduced motion', 'cssM', ['mnBpgBuka', '.mn-bpg-isi { animation: none; }']),
    ('BACA-DULU menyebut PR C', 'baca', ['PR C', 'rules v20', 'ssPeganganUntuk', 'docs/uji-rules-v20.md']),
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
    ('pemasok: porsi dari jumlah kedatangan, bukan rupiah', PD, "return { awal, akhir, total, arsip, daftar: d, pct: total > 0 ? d[0].rp / total * 100 : null };", "return { awal, akhir, total, arsip, daftar: d, pct: total > 0 ? d[0].n / d.reduce((a, x) => a + x.n, 0) * 100 : null };"),
    ('prakiraan: titik kas terlalu baru ditebak sebagai nol', PD, "  if (!pdBilangan(kas1)) return pdBelum(id, nama, 'Uang toko ' + PD_HARI + ' hari lalu belum bisa dihitung", "  if (false) return pdBelum(id, nama, 'Uang toko ' + PD_HARI + ' hari lalu belum bisa dihitung"),
    ('uang 30 hari lalu: memakai tutup hari TERTUA, bukan terakhir sebelum tanggalnya', LG, "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal && x.tanggal <= iso).sort((a, b) => String(b.tanggal).localeCompare(String(a.tanggal)))[0];", "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal && x.tanggal <= iso).sort((a, b) => String(a.tanggal).localeCompare(String(b.tanggal)))[0];"),
    ('uang 30 hari lalu: tutup hari SESUDAH tanggalnya ikut dipakai', LG, "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal && x.tanggal <= iso).sort(", "const d = ambilTutupHari().filter((x) => x && x.titik && x.tanggal).sort("),
    ('uang 30 hari lalu: catatan uang sesudah tutup hari tidak ikut', LG, "return { kas: saldoKantong(iso, t).total, kenapa: '', sumber: 'hitungan fisik tutup hari ' + tanggalPendek(t.tanggal) + (t.tanggal < iso", "return { kas: saldoKantong(t.tanggal, t).total, kenapa: '', sumber: 'hitungan fisik tutup hari ' + tanggalPendek(t.tanggal) + (t.tanggal < iso"),
    ('prakiraan: hitungan tutup hari diabaikan (selalu belum bisa)', PD, "const K = lpKasPadaTanggal(iso); return pdBilangan(K.kas) ? K : ", "const K = { kas: null, kenapa: '' }; return pdBilangan(K.kas) ? K : "),
    ('mulus: delapan lampu dihitung ulang tiap ketukan (tanpa ingatan)', PD, "  return ingatPerVersi('pdPondasi|' + hariIniIso(kini) + '|' + JSON.stringify(ambilTitikKas()), () => pdPondasiHitung(kini));", "  return pdPondasiHitung(kini);"),
    ('modal: hanya setoran yang tercatat (posisi awal toko diabaikan)', PD, "const dasar = pdBilangan(N.selisihBuku) ? modal + N.selisihBuku : null;", "const dasar = pdBilangan(N.selisihBuku) ? modal : null;"),
    ('modal: posisi awal MINUS tetap dipakai membagi', PD, "    : dasar > 0 ? ' Dibanding modal yang tertanam di toko '", "    : dasar !== 0 ? ' Dibanding modal yang tertanam di toko '"),
    ('kuartal: tiga bulannya bergeser (K4 = Sep–Nov)', KW, "return [0, 1, 2].map((i) => t + '-' + kwDua((q - 1) * 3 + 1 + i)); };", "return [0, 1, 2].map((i) => t + '-' + kwDua((q - 1) * 3 + i)); };"),
    ('kuartal: bulan sebelum catatan pertama ikut dijumlah', KW, "const ada = bulan.filter((b) => !b.depan && !b.sebelumBuku);", "const ada = bulan.filter((b) => !b.depan);"),
    ('kuartal: kuartal tidak utuh dibandingkan seolah setara', KW, "const utuh = !berjalan && !depan && !mulaiTengah && ada.length === 3 && !tanpaPotret;", "const utuh = true;"),
    ('kuartal: tinggal di toko = laba + ambil pribadi', KW, "const tinggal = kwBilangan(Q.labaBersih) && kwBilangan(prive) ? Q.labaBersih - prive : null;", "const tinggal = kwBilangan(Q.labaBersih) && kwBilangan(prive) ? Q.labaBersih + prive : null;"),
    ('kuartal: kekayaan akhir kuartal tanpa hitungan tutup hari (kas ditebak)', KW, "N = berjalan ? neracaPada(null, kini) : neracaPada(r.akhir, kini, KB);", "N = neracaPada(null, kini);"),
    ('kuartal: geser kuartal salah di pergantian tahun', SLG, "return Math.floor(i / 4) + '-K' + ((i % 4 + 4) % 4 + 1); };", "return String(key).slice(0, 4) + '-K' + ((i % 4 + 4) % 4 + 1); };"),
    ('kuartal: potret tidak memakai ambang owner', KW, "tambah('utang', 'Utang dibanding harta', pdLampuAtas(pct, A.utangMaks), pdPctTeks(pct),", "tambah('utang', 'Utang dibanding harta', 'tanpa', pdPctTeks(pct),"),
    ('kekayaan: naik/turun dibanding bulan SESUDAHNYA (terbalik)', PD, "const lalu = bulan.slice(i + 1).find((x) => x.ada); b.naik = lalu ? b.bersih - lalu.bersih : null;", "const lalu = bulan.slice(0, i).reverse().find((x) => x.ada); b.naik = lalu ? b.bersih - lalu.bersih : null;"),
    ('kekayaan: bulan lampau memakai titik kas sekarang (tanpa hitungan tutup hari)', PD, "N = b.berjalan ? neracaPada(null, kini) : neracaPada(per, kini, KB);", "N = neracaPada(null, kini);"),
    ('risiko: biaya ikut turun sebanding (laba bersih × sisa omzet)', PD, "const hilang = labaKotor30 * turunPct / 100; const laba = labaBersih30 - hilang;", "const hilang = labaKotor30 * turunPct / 100; const laba = labaBersih30 * (1 - turunPct / 100);"),
    ('risiko: batas turun dibalik (laba kotor ÷ laba bersih)', PD, "? Math.min(100, labaBersih30 / labaKotor30 * 100) : null);", "? Math.min(100, labaKotor30 / labaBersih30 * 100) : null);"),
    ('pola hari: hari ini (belum selesai) ikut rata-rata', PD, "const H = hariTerakhir(kini, 57).filter((d) => !d.hariIni && !d.diarsip && (!p || d.iso >= p));", "const H = hariTerakhir(kini, 56).filter((d) => !d.diarsip && (!p || d.iso >= p));"),
    ('lama kirim: pesanan batal ikut dihitung', BP, "if (!t || t < awal || t > akhir || p.status === 'batal' || !pemasokSungguhan(p.pemasok)) return;", "if (!t || t < awal || t > akhir || !pemasokSungguhan(p.pemasok)) return;"),
    ('lama kirim: yang masih menunggu dihitung 0 hari', BP, "if (!D.datang || !D.tanggal) { menunggu += 1; return; }", "if (!D.datang || !D.tanggal) { D.tanggal = t; }"),
    ('rantai pasok: gerak harga dibalik (lama − baru)', PD, "const d = r[0].hargaPerKg - r[1].hargaPerKg; if (d > 0) naik += 1;", "const d = r[1].hargaPerKg - r[0].hargaPerKg; if (d > 0) naik += 1;"),
    ('nota per orang: nota batal dihitung nota berlaku', RW, "if (o.status === 'batal') { x.batal += 1; nBatal += 1; } else { x.nota += 1; x.omzet += o.total; nBerlaku += 1; }", "{ x.nota += 1; x.omzet += o.total; nBerlaku += 1; }"),
    ('pelanggan: pembeli eceran bernama tidak ikut daftar pembeli', PGL, ".concat(eceranNama.map((o) => pgRingkas(o, false)))", ""),
    ('pelanggan: nota tanpa nama dianggap dikenal', PD, "const omzetNama = B.pembeli.reduce((a, o) => a + o.omzet, 0);", "const omzetNama = omzet;"),
    ('pelanggan: warna pembeli terbesar tidak membaca ambang owner', PD, "const lampu = t0 ? pdLampuAtas(t0.pct, A.pembeliMaks) : 'tanpa';", "const lampu = 'tanpa';"),
    ('pelanggan: kunjungan pertama = kunjungan terakhir (yang kembali dihitung baru)', PLL, "pertama: tgl.length ? tgl[0] : '', terakhir,", "pertama: terakhir, terakhir,"),
    ('pelanggan: tiga bulan dibaca satu bulan', PD, "export const PD_BULAN_PELANGGAN = 3;", "export const PD_BULAN_PELANGGAN = 1;"),
    ('pelanggan: bangku kosong tidak dihitung', PD, "const kosong = S.filter((o) => o.kosong)", "const kosong = S.filter((o) => false)"),
    ('organisasi: tutup hari di luar 30 hari ikut', PD, "riwayatTutup(PD_HARI + 5).forEach((t) => { if (!t.tanggal || t.tanggal < awal || t.tanggal > iso) return;", "riwayatTutup(999).forEach((t) => { if (!t.tanggal) return;"),
    ('organisasi: nego naik ikut dihitung potongan', PD, "if (b.totalSelisih < 0) x.potongan += -b.totalSelisih;", "x.potongan += Math.abs(b.totalSelisih) + 1;"),
    ('target: belum tercapai selalu kuning (tanpa laju hari)', KW, "capai >= target ? 'hijau' : bagian < 1 && capai >= target * bagian ? 'amber' : 'merah');", "capai >= target ? 'hijau' : bagian < 1 ? 'amber' : 'merah');"),
    ('target: kuartal selesai masih boleh kuning', KW, "capai >= target ? 'hijau' : bagian < 1 && capai >= target * bagian ? 'amber' : 'merah');", "capai >= target ? 'hijau' : capai >= target * bagian * 0.5 ? 'amber' : 'merah');"),
    ('target: kuartal berjalan dianggap sudah selesai (bagian = 1)', KW, "const bagian = Q.depan ? 0 : Q.berjalan ? Math.min(1, hariLewat / hariSemua) : 1;", "const bagian = Q.depan ? 0 : 1;"),
    ('target: utang lewat batas tidak merah', KW, "utang === null ? 'tanpa' : utang > T.utangMaks ? 'merah' : 'hijau';", "utang === null ? 'tanpa' : 'hijau';"),
    ('target: simpan satu kuartal membuang kuartal lain & ambang lampu', PD, "const lama = ugAturDok(PD_ID) || {}; const semua = Object.assign({}, lama.targetKuartal && typeof lama.targetKuartal === 'object' ? lama.targetKuartal : {});", "const lama = {}; const semua = {};"),
    ('target: target lain di kuartal yang sama terhapus saat satu diubah', PD, "if (v === undefined) { if (dulu[x.id]) baru[x.id] = dulu[x.id]; return; }", "if (v === undefined) return;"),
    ('target: ketikan rusak diterima', PD, "if (!(n > 0) || n > PD_TARGET_MAKS || Math.round(n) !== n) { tolak = ", "if (false) { tolak = "),
    ('rapor: kuartal belum utuh tidak bercap DRAF', KW, "const final = !Q.depan && Q.utuh && kwBulan(key).every(lpFinal);", "const final = true;"),
    ('rapor: kop belum lengkap tetap dikeluarkan', KW, ": !I.lengkap ? 'Kop belum lengkap: nama & alamat wajib (Setelan → Kop & identitas)' : '';", ": '';"),
    ('pengingat: kuartal berjalan ditagih terus (tanpa batas 14 hari)', SLG, "if (!ssTargetKuartal(kwKini).ada && ssHariKe(iso) - ssHariKe(ssKuartalAwal(kwKini)) < SS_KUARTAL_SUSUL) out.push(", "if (!ssTargetKuartal(kwKini).ada) out.push("),
    ('pengingat: target yang sudah diisi tetap diingatkan', SLG, "if (!ssTargetKuartal(kwDepan).ada) out.push(", "if (true) out.push("),
    ('pengingat: awal kuartal salah bulan', SLG, "String((Number(String(key).slice(6, 7)) - 1) * 3 + 1).padStart(2, '0') + '-01';", "String(Number(String(key).slice(6, 7)) * 3).padStart(2, '0') + '-01';"),
    ('pegangan: karyawan ikut melihat bab untuk Penjaga laci', SLG, "return peran === 'owner' ? B : B.filter((b) => b.untuk === 'semua' || b.untuk === peran); }", "return B; }"),
    ('pegangan: judul kembar diterima', SLG, "if (bab.some((b, k) => k !== i && b.judul.toLowerCase() === judul.toLowerCase())) return", "if (false) return"),
    ('pegangan: isi tanpa batas panjang', SLG, "if (isi.length > M.isi) return { tolak: 'Isi bab paling panjang '", "if (false) return { tolak: 'Isi bab paling panjang '"),
    ('pegangan: batas 40 bab tidak dijaga', SLG, "if (i < 0 && bab.length >= M.bab) return", "if (false) return"),
    ('pegangan: hapus satu bab menghapus semuanya', SLG, "return ssSimpanPegangan(bab.filter((x) => x.id !== b.id), w,", "return ssSimpanPegangan([], w,"),
    ('pegangan: geser di ujung tidak ditolak', SLG, "if (j < 0 || j >= bab.length) return { tolak: 'Bab itu sudah di '", "if (false) return { tolak: 'Bab itu sudah di '"),
    ('pegangan: mengubah bab menambah bab baru (id tidak dipakai)', SLG, "const b = { id: i >= 0 ? id : 'bab-' + w.idUnik(), judul, isi, untuk }; if (i >= 0) bab[i] = b; else bab.push(b);", "const b = { id: 'bab-' + w.idUnik(), judul, isi, untuk }; bab.push(b);"),
    ('pegangan: dokumen membawa kolom di luar bentuknya', SLG, "data: { id: SS_PEGANGAN_ID, bab: bab.map(", "data: { id: SS_PEGANGAN_ID, kolomLama: 'x', bab: bab.map("),
    ('satu lampu galat mematikan semuanya', PD, "const lampu = PD_LAMPU.map(([id, nama, f]) => { try { return f(X); } catch (e) {", "const lampu = PD_LAMPU.map(([id, nama, f]) => { try { return f(X); } catch (e) { throw e;"),
    ('setelan: ketikan rusak dibulatkan diam-diam', PD, "if (!(n > 0) || n > x.maks) { tolak = ", "if (false) { tolak = "),
    ('setelan: simpan satu ambang menimpa yang lain', PD, "const lama = ugAturDok(PD_ID) || {}; const data = Object.assign({}, lama, { id: PD_ID, tanggal: w.tanggal, jam: w.jam });", "const lama = {}; const data = { id: PD_ID, tanggal: w.tanggal, jam: w.jam };"),
    ('disiplin: hari ini ikut dihitung belum ditutup', PD, "filter((d) => !d.hariIni && !d.diarsip && d.n > 0)", "filter((d) => !d.diarsip && d.n > 0)"),
    ('disiplin: cek gudang lewat tempo tidak merah', PD, "lampu: !G.terakhir ? 'amber' : G.sisa < 0 ? 'merah' : G.sisa === 0 ? 'amber' : 'hijau'", "lampu: !G.terakhir ? 'amber' : G.sisa === 0 ? 'amber' : 'hijau'"),
    ('Dasbor memakai hitungan lain dari Laporan', DL, "tujuan: { ke: 'laporan', keluarga: 'pondasi' } }, pdPondasi(kini)); }", "tujuan: { ke: 'laporan', keluarga: 'pondasi' } }, { lampu: [], hitung: {} }); }"),
    ('Dasbor: pondasi dihitung ulang tiap ganti rentang', DL, "pondasi: lama.pondasi, tren: k('tren') };", "pondasi: k('pondasi'), tren: k('tren') };"),
]
RUSAK_STATIS = [
    ('Laporan tanpa kartu Pelanggan di layar lebar', 'laporan', 'h`${daftar}${risiko}${pelanggan}`', 'h`${daftar}${risiko}`'),
    ('Laporan tanpa tab Pondasi', 'laporan', "s.keluarga === 'pondasi' ? gambarPondasi(s, L) : ", ''),
    ('Dasbor tanpa kartu Pondasi', 'dasbor', 'kartuPondasi(D.pondasi)', "''"),
    ('modul membaca koleksi mentah (rumus uang baru)', 'pd', "import { ambilTutupHari, ambilTitikKas, ingatPerVersi } from '../data/toko.js';", "import { ambilTutupHari, ambilTitikKas, ingatPerVersi, ambilPenjualan } from '../data/toko.js';"),
    ('modul menulis dokumen kedua', 'pd', "({ dokumen: [{ koleksi: 'aturanToko', data }], patch });", "({ dokumen: [{ koleksi: 'aturanToko', data }, { koleksi: 'aturanToko', data }], patch });"),
    ('tablet staf tanpa kartu Buku pegangan', 'menu', '${kartuPegangan(s, akunM)}', ''),
    ('Menu owner tanpa lembar Buku pegangan', 'menu', "s.sistem === 'pegangan' ? gambarPegangan(s) : ", ''),
    ('halaman tidak mendengar bukuPegangan di perangkat staf', 'akses', "'produkArsip', 'bukuPegangan'], pengaturan:", "'produkArsip'], pengaturan:"),
    ('rules tidak membuka bukuPegangan untuk staf', 'rules', "'produkArsip', 'bukuPegangan'] && staf(['ben', 'karyawan'])", "'produkArsip'] && staf(['ben', 'karyawan'])"),
    ('Kuartal tanpa rapor berkop', 'laporan', "tigaTombol('kwKeluar', DR.tolak)", "''"),
    ('Laporan tanpa keluarga Kuartal', 'laporan', "s.keluarga === 'kuartal' ? gambarKuartal(s, L) : ", ''),
    ('Pondasi tanpa kartu risiko', 'laporan', 'data-k="pd-risiko"', 'data-k="x"'),
    ('modul kuartal menulis dokumen', 'kw', "import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';", "import { RP, hariIniIso, tanggalPendek } from '../inti/format.js'; const x = { koleksi: 'aturanToko' };"),
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
  var T = kwTahun(Number(akhir.slice(0, 4)), K); out.kuartalMenutup = T.menutup; out.kuartal = kwDaftar(K).map(function (k) { var q = kwRekap(k.key, K); return { key: k.key, utuh: q.utuh, kekayaan: q.kekayaan.ada, lampu: q.lampu.map(function (l) { return l.lampu; }).join(',') }; });
  out.kekayaan = pdKekayaan(K).bulan.map(function (b) { return b.key + (b.ada ? ':ada' : ':belum'); }); out.rantai = pdRantai(K).pemasok.length; out.risiko = pdRisiko(K).skenario.length; out.orang = pdOrganisasi(K).orang.length;
  var PLA = pdPelanggan(K); out.pelanggan = { ada: PLA.ada, menutup: PLA.menutup, lampu: PLA.lampu, nOrang: PLA.dikenal ? PLA.dikenal.nOrang : null, pctDikenal: PLA.dikenal && PLA.dikenal.pct !== null ? Math.round(PLA.dikenal.pct * 10) / 10 : null, pctTerbesar: PLA.terbesar ? Math.round(PLA.terbesar.pct * 10) / 10 : null, segmen: PLA.segmen.length, baru: PLA.datang.baru, kembali: PLA.datang.kembali, lama: PLA.datang.lama, kosong: PLA.datang.nKosong };
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
    kenaK = [x for x in TERLARANG + ["koleksi: '", 'ambilTutupHari'] if x in src['kw']]
    if kenaK: g.append('kuartal-logika menyentuh ' + kenaK[0] + ' — modul ini hanya membaca lewat fungsi sumber layar lain & tidak menulis apa pun')
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
            h = json.loads(out); beres = not h['galat'] and len(h['lampu']) == 8 and all(x['keadaan'] != 'galat' for x in h['lampu']) and h.get('utangCocok') and h.get('dasbor') and h.get('kuartalMenutup') and h.get('risiko') == 4 and bool(h.get('pelanggan')) and h['pelanggan'].get('menutup')
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h.get('akhir'), 'LULUS' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: ada lampu galat, utang ÷ harta tidak sama dengan Neraca, Dasbor berbeda dari Laporan, Σ kuartal tidak menutup ke tahun, atau angka per pelanggan tidak menutup ke Laporan')
    sys.exit(1 if g or gs else 0)
