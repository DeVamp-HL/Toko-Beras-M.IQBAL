#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_kpi_kg.py — PAKET P1 · KPI per kg, per minggu & deret bulanan (owner 27 Nov 2026; sensus ulang 27 Nov: A3 A112 A113 A114 A115 A116 A130 B6 B7 B133).
KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  A3 · A112 · A130  untung / HPP / jual per kg TERWUJUD per merek = laba kotor ÷ kg nota bermodal (aturan Laporan › Biaya; se-toko bulan penuh = pemicuBiaya marginKg),
                    dibanding target untung per kg (setelan Harga; di bawah = TEGAS <); urut omzet Rp & untung/kg; Dasbor kartu Margin & target memuat baris tetap.
  B6 · B133         tren per merek per minggu (Senin–Minggu): minggu berjalan dibanding minggu lalu SAMPAI HARI YANG SAMA; merek yang hilang tetap tampil; deret 8 minggu.
  B7                terlaris menurut omzet Rp rentang bebas (nota bermodal + tanpa modal − retur); Σ = omzet & laba kotor mesin (penjaga).
  A113 · A114       deret bulanan: margin % = klMarginBulan apa adanya, per kg, perputaran stok RUPIAH disetahunkan (modal terjual ÷ nilai stok rata-rata = modal tertahan).
  A115              hari stok rupiah per minggu vs target owner aturanToko/stokUmur (bawaan 7–14 hari, keputusan owner 27 Nov 2026; bawah > atas ditolak).
  A116              lama piutang (DSO) = piutang berjalan (sisa > 0) ÷ penjualan bon per hari 30 hari; saldo awal bukan penjualan; tren akhir tiap minggu.
  Dasbor            kelompok `kg` ikut saringan (bawaan Hari ini = bulan ini & Dasbor lama sama persis), angka & kartu baru hanya di katalog (bawaan tidak berubah).

    python3 alat-uji/uji_kpi_kg.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada; angka rupiah toko tidak dicetak)
    python3 alat-uji/uji_kpi_kg.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_jual_baru, uji_dasbor_sensus, uji_sisa_sensus  # noqa: E402
LPL = 'baru/js/layar/laporan-logika.js'; KL = 'baru/js/layar/kpi-laba-logika.js'; BL = 'baru/js/layar/bon-logika.js'; SL = 'baru/js/layar/stok-logika.js'
DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'
MODUL = uji_dasbor_sensus.MODUL
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'stok': 'baru/js/layar/stok.js', 'css': 'baru/css/laporan.css', 'pages': '.github/workflows/pages.yml',
          'baca': 'baru/BACA-DULU.md', 'lpl': LPL, 'kl': KL, 'bl': BL, 'sl': SL, 'dl': DL, 'wg': WG}

def KARUNG(i, tgl, merk, kg, harga, hpp, cara='Tunai', nama=''):
    x = {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': cara, 'namaPelanggan': nama, 'jenis': 'karung', 'merkSumber': merk, 'beratKarungAcuan': 50,
         'jumlahKarung': kg / 50, 'totalKg': kg, 'hargaTotal': harga, 'grupNota': 'g' + i}
    if hpp is not None: x['hppTotalSaatJual'] = hpp
    return x
def MASUK(i, tgl, merk, kg, perKg):
    return {'id': i, 'tanggal': tgl, 'jam': '07:00', 'pemasok': 'Pemasok Contoh', 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
        {'merk': merk, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': kg / 50, 'totalKg': kg, 'subtotalHarga': kg * perKg, 'hargaPerKg': perKg}]}
D_ = 'Pelanggan Contoh D'
KOTAK = {
    'batchMasuk': [MASUK(101, '2026-09-01', 'Angsa', 1000, 12000), MASUK(102, '2026-09-01', 'Kembang', 1000, 10000)],
    'penjualan': [
        KARUNG('s1', '2026-09-10', 'Angsa', 300, 3900000, 3600000),                       # Sep: untung TEPAT Rp1.000/kg (= target → BUKAN di bawah)
        KARUNG('o1', '2026-10-10', 'Angsa', 200, 2500000, 2400000), KARUNG('o2', '2026-10-15', 'Kembang', 200, 2300000, 2000000),
        KARUNG('ob', '2026-10-20', 'Kembang', 30, 360000, 300000, 'Kredit', D_),
        KARUNG('lb', '2026-11-02', 'Kembang', 10, 120000, 100000, 'Kredit', 'Pelanggan Contoh L'),
        KARUNG('m1', '2026-11-05', 'Murah', 400, 400000, 380000),                          # kg terbanyak, omzet kecil, untung Rp50/kg — urutan kg ≠ omzet ≠ abjad
        KARUNG('a1', '2026-11-09', 'Angsa', 100, 1300000, 1200000), KARUNG('k1', '2026-11-10', 'Kembang', 50, 600000, 500000), KARUNG('p1', '2026-11-10', 'Pelita', 10, 130000, 120000),
        KARUNG('a2', '2026-11-13', 'Angsa', 50, 650000, 600000),                          # Jumat minggu lalu — DI LUAR banding "sampai hari yang sama" (Rabu)
        KARUNG('a3', '2026-11-16', 'Angsa', 150, 1920000, 1800000), KARUNG('k2', '2026-11-17', 'Kembang', 100, 1150000, 1000000),
        KARUNG('x1', '2026-11-17', 'Kembang', 20, 240000, None),                          # tanpa modal: ikut omzet terlaris, TIDAK ikut kg pembagi per kg
        KARUNG('n1', '2026-11-18', 'Angsa', 50, 640000, 600000, 'Kredit', D_)],
    'retur': [{'id': 'r1', 'tanggal': '2026-10-16', 'jam': '10:00', 'jenisAsal': 'karung', 'merkSumber': 'Kembang', 'namaProduk': 'Kembang', 'totalKg': 10, 'kondisi': 'rusak', 'nominalRefund': 115000}],
    'piutangMutasi': [
        {'id': 501, 'tipe': 'bayar', 'namaPelanggan': D_, 'nominal': 200000, 'tanggal': '2026-11-01', 'jam': '10:00', 'caraBayar': 'Tunai', 'dicatatDi': 'sistem'},
        {'id': 502, 'tipe': 'bayar', 'namaPelanggan': 'Pelanggan Contoh L', 'nominal': 150000, 'tanggal': '2026-11-03', 'jam': '10:00', 'caraBayar': 'Tunai', 'dicatatDi': 'sistem'},   # lebih bayar Rp30.000
        {'id': 503, 'tipe': 'saldoAwal', 'namaPelanggan': 'Pelanggan Contoh S', 'nominal': 50000, 'tanggal': '2026-11-05', 'jam': '10:00', 'dicatatDi': 'sistem'}],                    # bukan penjualan bon
}
ATUR = [{'id': 'catatStok', 'tempoHari': 21, 'modalFifoMulai': ''}, {'id': 'harga', 'targetPerKg': 1000}]

SKENARIO = r"""
(function () {   // satu lingkup fungsi: nama var uji tidak bertabrakan dengan const modul (KG, SH, …)
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T14:00:00+07:00'); var nId = 90000; var iso = '2026-11-18';
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'penyesuaianStok', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'stokBahanKemasan', 'pesanan', 'karantina', 'persetujuan', 'pengeluaranHarian', 'absenKaryawan', 'pajakSetoran', 'pajakOmzetLuar'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-09-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);

// ==================== 1 · PER KG PER MEREK (A3 · A130) & TARGET ====================
var MN = merekRentang('2026-11-01', iso); var ang = MN.merek['Angsa'], kem = MN.merek['Kembang'], pel = MN.merek['Pelita'];
ok('1: Angsa Nov = laba kotor Rp310.000 ÷ 350 kg bermodal = Rp885,71/kg; HPP Rp12.000/kg; jual Rp12.885,71/kg', dekat(ang.marginKg, 310000 / 350) && dekat(ang.hppKg, 12000) && dekat(ang.jualKg, 4510000 / 350) && ang.kgHitung === 350, J([ang.marginKg, ang.hppKg, ang.kgHitung]));
ok('1: Kembang: baris TANPA modal (20 kg) tidak ikut pembagi → Rp270.000 ÷ 160 kg = Rp1.687,5/kg; omzet penuh Rp2.110.000 (ikut nota tanpa modal)', dekat(kem.marginKg, 1687.5) && kem.kgHitung === 160 && kem.kg === 180 && kem.omzetSemua === 2110000, J([kem.marginKg, kem.kgHitung, kem.kg, kem.omzetSemua]));
var T0 = lpTargetKg();
ok('1: target untung per kg = setelan Harga Rp1.000/kg (owner)', T0.rp === 1000 && T0.dariOwner && /setelan owner/.test(T0.teks), J(T0));
ok('1: di bawah target TEGAS <: Angsa Rp885,71 bawah · Kembang capai · Pelita tepat Rp1.000 = capai (bukan di bawah)', lpStatusKg(ang, T0) === 'bawah' && lpStatusKg(kem, T0) === 'capai' && lpStatusKg(pel, T0) === 'capai' && dekat(pel.marginKg, 1000), J([pel.marginKg]));
var MS = merekRentang('2026-09-01', '2026-09-30').merek['Angsa'];
ok('1: Sep Angsa tepat Rp1.000/kg = capai', dekat(MS.marginKg, 1000) && lpStatusKg(MS, T0) === 'capai');
aturDengan([{ id: 'harga', targetPerKg: 0 }]); ok('1: target 0 = belum ada → keadaan null (bukan "di bawah")', lpStatusKg(ang, lpTargetKg()) === null && /belum ada/.test(lpTargetKg().teks)); aturDengan([]);
var MB = merekBulan('2026-11', KINI); var RK = lpRingkasKg(MB.merek.concat(MB.luar ? [MB.luar] : []), T0);
ok('1: Per merek Nov se-toko: Rp610.000 ÷ 920 kg = Rp663,04/kg · HPP Rp6.300.000 ÷ 920 · 2 merek di bawah (Murah Rp50 dulu, Angsa), 2 capai', dekat(RK.marginKg, 610000 / 920) && dekat(RK.hppKg, 6300000 / 920) && RK.nBawah === 2 && RK.bawah[0].merek === 'Murah' && RK.bawah[1].merek === 'Angsa' && RK.nCapai === 2, J(RK));
var KO = kendaliBulan('2026-10', KINI); var PO = pemicuBiaya(KO); var mkO = PO.baris.find(function (r) { return r.id === 'marginKg'; });
var MO = merekBulan('2026-10', KINI); var RO = lpRingkasKg(MO.merek.concat(MO.luar ? [MO.luar] : []), T0);
ok('1: Okt se-toko per merek = Laporan › Biaya (pemicu "Margin kotor per kg"): Rp345.000 ÷ 430 kg — retur Rp115.000 ikut memotong', dekat(RO.marginKg, 345000 / 430) && mkO && dekat(Math.round(RO.marginKg * 10) / 10, mkO.n, 0.01), J([RO.marginKg, mkO && mkO.n]));
var TU = merekTeratas(MB, 'omzet'), TK = merekTeratas(MB, 'marginKg'), TG = merekTeratas(MB, 'kg');
ok('1: urut omzet Rp: Angsa · Kembang · Murah · Pelita; urut untung/kg: Kembang · Pelita · Angsa · Murah; urut kg: Murah dulu', TU.urut === 'omzet' && J(TU.daftar.map(function (g) { return g.merek; })) === J(['Angsa', 'Kembang', 'Murah', 'Pelita'])
  && TK.urut === 'marginKg' && J(TK.daftar.map(function (g) { return g.merek; })) === J(['Kembang', 'Pelita', 'Angsa', 'Murah']) && TG.daftar[0].merek === 'Murah' && TU.menutup, J([TU.daftar.map(function (g) { return g.merek; }), TK.daftar.map(function (g) { return g.merek; })]));
ok('1: urut tak dikenal = kg', merekTeratas(MB, 'ngawur').urut === 'kg' && LP_URUT_MEREK.map(function (u) { return u.id; }).join() === 'kg,margin,omzet,marginKg');

// ==================== 2 · TERLARIS RENTANG BEBAS (B7) ====================
var TL = lpTerlaris('2026-11-01', iso, 2);
ok('2: terlaris 1–18 Nov menurut omzet (bukan kg): Angsa Rp4.510.000 · Kembang Rp2.110.000 · sisa 2 merek (Murah + Pelita Rp530.000); Σ = omzet mesin Rp7.150.000', TL.daftar.length === 2 && TL.daftar[0].merek === 'Angsa' && TL.daftar[0].omzet === 4510000 && TL.daftar[1].omzet === 2110000
  && TL.sisa && TL.sisa.n === 2 && TL.sisa.omzet === 530000 && TL.total === 7150000 && Math.abs(TL.luar) < 0.5 && TL.menutup && dekat(TL.daftar[0].porsi, 4510000 / 7150000 * 100), J(TL));
ok('2: penjaga: Σ per merek = omzet & laba kotor mesin (lpHariRentang) — kalimat menutup', /menutup persis/.test(TL.kalimat) && TL.toko && dekat(TL.toko.marginKg, 610000 / 920) && TL.toko.nBawah === 2, J([TL.kalimat, TL.toko]));
var TO = lpTerlaris('2026-10-01', '2026-10-31', 5);
ok('2: Okt: retur Rp115.000 memotong omzet Kembang (Rp2.660.000 − Rp115.000) — tetap menutup', TO.daftar[0].merek === 'Kembang' && TO.daftar[0].omzet === 2545000 && TO.menutup, J(TO.daftar));
ok('2: rentang tanpa jualan = daftar kosong, tetap menutup', lpTerlaris('2026-09-20', '2026-09-25', 5).daftar.length === 0 && lpTerlaris('2026-09-20', '2026-09-25', 5).menutup);

// ==================== 3 · TREN PER MEREK PER MINGGU (B6 · B133 · A130) ====================
var MG = lpMerekMinggu('2026-11-16', KINI, 8); var g = function (M, n) { return M.merek.find(function (x) { return x.merek === n; }) || null; };
var gA = g(MG, 'Angsa'), gK = g(MG, 'Kembang'), gP = g(MG, 'Pelita');
ok('3: minggu berjalan (16–18 Nov) dibanding minggu lalu SAMPAI HARI YANG SAMA (9–11 Nov) — jualan Jumat 13 Nov tidak ikut', MG.berjalan && MG.sampai === iso && MG.laluDari === '2026-11-09' && MG.laluSampai === '2026-11-11' && gA.omzetLalu === 1300000 && /hari yang sama/.test(MG.bandingTeks), J([MG.laluSampai, gA && gA.omzetLalu]));
ok('3: Angsa Rp2.560.000 (▲96,9 %), untung Rp800/kg (−Rp200 dari Rp1.000) → di bawah target; Kembang Rp1.390.000 (▲131,7 %) Rp1.500/kg', gA.omzet === 2560000 && dekat(gA.omzetPct, (2560000 - 1300000) / 1300000 * 100) && dekat(gA.ini.marginKg, 800) && dekat(gA.marginKgBeda, -200) && gA.status === 'bawah'
  && gK.omzet === 1390000 && dekat(gK.ini.marginKg, 1500) && gK.status === 'capai', J([gA, gK]));
ok('3: Pelita laku minggu lalu, minggu ini tidak → tetap tampil "hilang" (Rp0), dihitung turun; urut omzet minggu ini', gP && gP.hilang && gP.omzet === 0 && gP.omzetLalu === 130000 && MG.merek[0].merek === 'Angsa' && MG.merek[MG.merek.length - 1].merek === 'Pelita' && MG.turun === 1 && MG.naik === 2, J(MG.merek.map(function (x) { return [x.merek, x.omzet]; })));
ok('3: se-toko minggu ini Rp3.950.000 · untung Rp310.000 ÷ 300 kg vs minggu lalu Rp210.000 ÷ 160 kg · HPP/kg naik', MG.toko.omzet === 3950000 && dekat(MG.toko.marginKg, 310000 / 300) && dekat(MG.toko.marginKgLalu, 210000 / 160) && MG.toko.omzetLalu === 2030000 && dekat(MG.toko.hppKg, 3400000 / 300) && MG.toko.nBawah === 1 && MG.menutup, J(MG.toko));
ok('3: deret 8 minggu Senin: minggu ini terakhir (berjalan); Angsa minggu 9 Nov = Rp1.950.000 (minggu penuh); minggu sebelum catatan = sebelum', MG.deret.length === 8 && MG.deret[7].awal === '2026-11-16' && MG.deret[7].berjalan && gA.deret[6] === 1950000 && gA.deret[7] === 2560000 && MG.deret[0].awal === '2026-09-28' && !MG.deret[0].sebelum, J([MG.deret.map(function (d) { return d.awal; }), gA.deret]));
var MG9 = lpMerekMinggu('2026-11-09', KINI, 8);
ok('3: minggu yang sudah lewat (9–15 Nov) dibanding minggu penuh 2–8 Nov; merek tanpa jualan minggu lalu = baru, Murah (5 Nov) = tidak laku minggu itu', !MG9.berjalan && MG9.sampai === '2026-11-15' && MG9.laluSampai === '2026-11-08' && g(MG9, 'Angsa').baru && g(MG9, 'Angsa').omzetPct === null && g(MG9, 'Kembang').omzetPct !== null && g(MG9, 'Murah').hilang, J(MG9.merek));
ok('3: tanggal di tengah minggu dibaca Senin-nya', lpMerekMinggu('2026-11-18', KINI, 4).awal === '2026-11-16');

// ==================== 4 · STOK DALAM RUPIAH: HARI STOK & PERPUTARAN (A114 · A115) ====================
var SR = klStokRp(KINI, '2026-11-16', '2026-11-22');
ok('4: minggu ini dipotong sampai hari ini (3 hari); nilai stok rata-rata (Rp9,5 jt + Rp8,3 jt + Rp7,7 jt) ÷ 3 = Rp8.500.000 = modal tertahan yang SAMA', SR.dari === '2026-11-16' && SR.sampai === iso && SR.nHari === 3 && dekat(SR.rata, 8500000, 0.5) && dekat(SR.rata, klModalTertahan(KINI, '2026-11-16', iso).rata), J(SR));
ok('4: modal terjual Rp3.400.000 (nota tanpa modal tidak ikut) → hari stok Rp8,5 jt ÷ Rp1.133.333/hari = 7,5 hari → PAS (bawaan 7–14 hari)', SR.hpp === 3400000 && dekat(SR.hari, 7.5) && SR.status === 'pas' && SR.target.min === 7 && SR.target.maks === 14 && !SR.target.dariOwner && /bawaan/.test(SR.target.teks), J(SR));
ok('4: perputaran 3,4 jt ÷ 8,5 jt = 0,4× dalam 3 hari = 48,67× setahun (× 365 ÷ 3)', dekat(SR.putaran, 0.4) && dekat(SR.putaranTahun, 0.4 * 365 / 3) && /STOK|pas/.test(SR.kalimat), J([SR.putaran, SR.putaranTahun, SR.kalimat]));
aturDengan([{ id: 'stokUmur', targetHariMin: 3, targetHariMaks: 5 }]); var SR2 = klStokRp(KINI, '2026-11-16', iso);
aturDengan([{ id: 'stokUmur', targetHariMin: 8, targetHariMaks: 20 }]); var SR3 = klStokRp(KINI, '2026-11-16', iso);
ok('4: setelan owner dibaca: target 3–5 → "diam" (modal kebanyakan diam) · target 8–20 → "tipis"', SR2.status === 'diam' && SR2.target.dariOwner && SR3.status === 'tipis' && /TIPIS/.test(SR3.kalimat), J([SR2.status, SR3.status]));
aturDengan([]);
ok('4: rentang tanpa modal terjual = belum bisa dihitung (null), bukan 0', klStokRp(KINI, '2026-09-20', '2026-09-25').hari === null && /belum bisa/.test(klStokRp(KINI, '2026-09-20', '2026-09-25').kalimat));
var SB = klStokRpBulan(KINI, 4); var sbOkt = SB.find(function (b) { return b.key === '2026-10'; });
ok('4: deret bulanan 4 bulan: Agu = sebelum catatan; Okt nilai stok Rp480 jt ÷ 31 hari, modal terjual Rp4.700.000 → disetahunkan', SB.length === 4 && SB[0].key === '2026-08' && SB[0].sebelum && dekat(sbOkt.rata, 480000000 / 31, 0.5) && sbOkt.hpp === 4700000 && dekat(sbOkt.putaranTahun, 4700000 / (480000000 / 31) * 365 / 31) && sbOkt.status === 'diam' && SB[3].berjalan, J(SB.map(function (b) { return [b.key, b.rata, b.hpp, b.status]; })));
var SM = klStokRpMinggu(KINI, 8);
ok('4: deret mingguan 8 minggu Senin–Minggu; minggu ini = klStokRp minggu ini', SM.length === 8 && SM[7].awal === '2026-11-16' && SM[7].berjalan && dekat(SM[7].hari, 7.5) && SM[0].awal === '2026-09-28', J(SM.map(function (b) { return [b.awal, b.hari]; })));
ok('4: setelan target: bawaan 7–14; bawah > atas DITOLAK; pecahan / 0 ditolak; kosong = angka sekarang', umAtur().targetHariMin === 7 && umAtur().targetHariMaks === 14
  && /tidak boleh di atas/.test(susunAturUmur({ targetHariMin: '20', targetHariMaks: '10' }, W).tolak || '') && !!susunAturUmur({ targetHariMin: '7,5' }, W).tolak && !!susunAturUmur({ targetHariMaks: '0' }, W).tolak
  && susunAturUmur({}, W).dokumen[0].data.targetHariMin === 7 && susunAturUmur({ targetHariMin: '5', targetHariMaks: '21' }, W).dokumen[0].data.targetHariMaks === 21 && susunAturUmur({}, W).dokumen[0].data.id === 'stokUmur', J(susunAturUmur({ targetHariMin: '20', targetHariMaks: '10' }, W)));

// ==================== 5 · LAMA PIUTANG (DSO, A116) ====================
var DS = pnDso(KINI, 8); var X = DS.kini;
ok('5: piutang berjalan = Σ sisa > 0: D Rp800.000 + saldo awal S Rp50.000 (lebih bayar L −Rp30.000 TIDAK mengurangi) = Rp850.000 · 2 orang', X.piutang === 850000 && X.nOrang === 2, J(X));
ok('5: penjualan bon 30 hari (20 Okt – 18 Nov) = Rp360.000 + Rp120.000 + Rp640.000 (saldo awal bukan penjualan) → Rp37.333/hari → DSO 22,77 hari', X.jual === 1120000 && X.hari === 30 && X.mulai === '2026-10-20' && dekat(X.dso, 850000 / (1120000 / 30)), J(X));
ok('5: akhir minggu lalu (Minggu 15 Nov): Rp210.000 ÷ (Rp480.000 ÷ 30) = 13,13 hari → naik 9,64 hari', DS.lalu.t === '2026-11-15' && DS.lalu.piutang === 210000 && dekat(DS.lalu.dso, 210000 / 16000) && dekat(DS.beda, 850000 / (1120000 / 30) - 13.125) && /naik/.test(DS.kalimat), J(DS.lalu));
ok('5: deret 8 titik: 7 akhir minggu (Minggu 4 Okt … 15 Nov) + hari ini; titik tanpa penjualan bon = belum bisa (null), bukan 0; 25 Okt = Rp360.000 ÷ (Rp360.000 ÷ 30) = 30 hari', DS.deret.length === 8 && DS.deret[7].hariIni && DS.deret[0].t === '2026-10-04' && DS.deret[0].dso === null && dekat(DS.deret[3].dso, 30), J(DS.deret.map(function (d) { return [d.t, d.dso, d.hari]; })));
var DP = pnDsoPada('2026-09-20');
ok('5: jendela dipendekkan bila catatan toko baru mulai (1 Sep → 20 hari) dan disebut', DP.mulai === '2026-09-01' && DP.hari === 20 && /catatan toko mulai/.test(DP.pendek) && DP.dso === null, J(DP));
ok('5: rata-rata hari bon tertagih (bon lunas) tetap disebut berdampingan', DS.tertagih && typeof DS.tertagih.rataTeks === 'string' && /piutang berjalan/.test(DS.rumus), J(DS.tertagih));

// ==================== 6 · DERET BULANAN (A113 · A112 · A130) ====================
var DB = klDeretBulan(KINI, 3, 8); var b = function (k) { return DB.bulan.find(function (x) { return x.key === k; }); };
ok('6: margin % per bulan = klMarginBulan apa adanya (kotor · usaha · bersih), grosir = pembanding BPS kartu Margin', ['2026-09', '2026-10', '2026-11'].every(function (k) { var M = klMarginBulan(k, KINI); var t = function (id) { return M.tangga.find(function (x) { return x.id === id; }).pct; };
  return b(k).kotor === t('kotor') && b(k).usaha === t('usaha') && b(k).bersih === t('bersih') && b(k).grosir === M.bps.tokoGrosir; }), J(DB.bulan));
ok('6: untung per kg per bulan se-toko: Sep Rp1.000 · Okt Rp802,33 · Nov Rp663,04; HPP/kg Nov Rp6.847,83', dekat(b('2026-09').marginKg, 1000) && dekat(b('2026-10').marginKg, 345000 / 430) && dekat(b('2026-11').marginKg, 610000 / 920) && dekat(b('2026-11').hppKg, 6300000 / 920), J(DB.bulan));
ok('6: perputaran & hari stok bulan = klStokRp bulan itu', ['2026-10', '2026-11'].every(function (k) { var S = klStokRp(KINI, k + '-01', akhirBulanIso(k)); return b(k).putaranTahun === S.putaranTahun && b(k).hariStok === S.hari && b(k).statusStok === S.status; }));
ok('6: per merek per bulan, kg bermodal terbanyak dulu: Angsa (850) · Murah (400) · Kembang (390) · Pelita; Angsa Sep Rp1.000 · Okt Rp500 · Nov Rp885,71 (di bawah target)', J(DB.merek.map(function (m) { return m.merek; })) === J(['Angsa', 'Murah', 'Kembang', 'Pelita'])
  && dekat(DB.merek[0].bulan[0].marginKg, 1000) && dekat(DB.merek[0].bulan[1].marginKg, 500) && dekat(DB.merek[0].bulan[2].marginKg, 310000 / 350) && DB.merek[0].bulan[2].status === 'bawah' && DB.merek[1].bulan[0].marginKg === null, J(DB.merek));
var DB6 = klDeretBulan(KINI, 6, 8);
ok('6: bulan sebelum catatan pertama = sebelum (tidak dihitung)', DB6.bulan.length === 6 && DB6.bulan[0].key === '2026-06' && DB6.bulan[0].sebelum && !DB6.bulan[3].sebelum && DB6.targetStok.min === 7);
var KG = klKgBulan('2026-11', KINI);   // nama var ini aman: skenario berjalan di lingkup fungsi
ok('6: kartu Dasbor "untung per kg" Nov = per merek se-toko; bulan lalu Okt; 2 merek di bawah target (kg terbanyak dulu)', dekat(KG.marginKg, 610000 / 920) && KG.lalu.key === '2026-10' && dekat(KG.lalu.marginKg, 345000 / 430) && dekat(KG.beda, 610000 / 920 - 345000 / 430) && KG.nBawah === 2 && KG.bawah[0].merek === 'Murah' && KG.berjalan, J(KG));

// ==================== 7 · DASBOR (keputusan owner 27 Nov 2026) ====================
var D0 = dbTambahan(susunDasbor(KINI, 'hari'), KINI);
ok('7: kelompok kg bawaan = bulan ini sampai hari ini; stok rupiah memakai nilai stok yang SAMA dengan modal tertahan di kartu Margin & target', D0.kg && !D0.kg.galat && D0.kg.terlaris.dari === '2026-11-01' && D0.kg.terlaris.sampai === iso && D0.kg.stok.rata === D0.kpi.modal.rata && D0.kg.dso.kini.piutang === 850000, J(D0.kg && D0.kg.galat));
ok('7: kartu Margin & target membawa untung per kg bulan itu (baris tetap)', D0.kpi.kg && dekat(D0.kpi.kg.marginKg, 610000 / 920) && D0.kpi.kg.key === '2026-11');
var SH = dbSaring({ id: 'hari' }, KINI), S7 = dbSaring({ id: 'h7' }, KINI), SL = dbSaring({ id: 'bulanLalu' }, KINI);
var DH = dbTambahan(susunDasbor(KINI, 'hari', null, null, SH), KINI); var D7 = dbTambahan(susunDasbor(KINI, 'hari', null, null, S7), KINI); var DLl = dbTambahan(susunDasbor(KINI, 'hari', null, null, SL), KINI);
ok('7: saringan Hari ini = Dasbor tanpa saringan PERSIS (kelompok kg & kpi)', J(DH.kg) === J(D0.kg) && J(DH.kpi.kg) === J(D0.kpi.kg));
ok('7: saringan 7 hari: terlaris & hari stok = 12–18 Nov; Bulan lalu: untung per kg = Oktober', D7.kg.terlaris.dari === '2026-11-12' && D7.kg.stok.dari === '2026-11-12' && DLl.kg.terlaris.dari === '2026-10-01' && DLl.kg.terlaris.sampai === '2026-10-31' && DLl.kpi.kg.key === '2026-10', J([D7.kg.terlaris.dari, DLl.kpi.kg.key]));
var kunci = []; var ing = function (k, f) { kunci.push(k); return f(); }; dbTambahan(susunDasbor(KINI, 'hari', null, ing, S7), KINI, ing);
ok('7: kelompok kg diingat dengan kunci saringan (kg|saring|…) — pemanasan & gambar memakai kunci yang sama', kunci.indexOf('kg|saring|' + S7.kunci) >= 0 && DB_PANAS.indexOf('kg') >= 0 && DB_IKUT_SARING.indexOf('kg') >= 0, J(kunci));
var WS = wgSusun(['marginKg', 'hariStok', 'putaranStok', 'dso', 'kTerlaris', 'kTrenMerek'].map(function (id) { return { id: id }; }), D0); var w = function (id) { return WS.find(function (x) { return x.id === id; }); };
ok('7: widget baru terisi dari kelompok yang sama (tanpa galat)', WS.length === 6 && WS.every(function (x) { return x.nilai !== 'gagal dihitung'; }) && w('marginKg').nilai === 'Rp663/kg' && w('kTerlaris').nilai === 'Angsa' && /^1\. Angsa/.test(w('kTerlaris').baris[0][0])
  && w('dso').nilai === DESIMAL(Math.round(850000 / (1120000 / 30) * 10) / 10) + ' hari' && w('kTrenMerek').baris[0][0] === 'Angsa' && w('kTrenMerek').tren.length === 4, J(WS.map(function (x) { return [x.id, x.nilai, x.ket]; })));
var W7 = wgSusun([{ id: 'hariStok' }, { id: 'kTerlaris' }, { id: 'marginKg' }, { id: 'dso' }], D7);
ok('7: nama angka ikut periode saringan; lama piutang tetap "sekarang"', W7[0].nama === 'Hari stok · 7 hari' && W7[1].nama === 'Terlaris · 7 hari' && W7[2].nama === 'Untung per kg · November 2026' && W7[3].nama === 'Lama piutang (hari)', J(W7.map(function (x) { return x.nama; })));
ok('7: keputusan owner: kartu & angka baru hanya di katalog "+ Tambah kartu" — susunan bawaan Dasbor tidak berubah', ['marginKg', 'hariStok', 'putaranStok', 'dso', 'kTerlaris', 'kTrenMerek'].every(function (id) { return WG_KATALOG.some(function (k) { return k.id === id; }) && !WG_BAWAAN.some(function (x) { return x.id === id; }); })
  && WG_BAWAAN.map(function (x) { return x.id; }).join() === 'kHari,kKpi,kTren,kBulan,kWadah,kPemicu,kTagihan,kStok,kMutu,kPondasi,kB2b');

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})();
"""

STATIS = [
    ('Laporan › Laba: Per merek memuat untung/HPP per kg + target, deret bulanan dipasang (HP & tablet/Mac)', 'laporan', ["const deret = kartuDeretBulan(KL.klDeretBulan(kini(), 6, 8), key);", '${keMana}${merek}${deret}${susutK}', 'h`${panel}${deret}${keMana}${merek}`',
      'function kgMerek(M, TK)', '${jaga}${kgMerek(M, TK)}${susut}', "LP.lpStatusKg(g, TK) === 'bawah'", "g.marginKg !== null ? 'untung ' + RP(Math.round(g.marginKg))", 'function kartuDeretBulan(D, key)']),
    ('Laporan › Mingguan: per merek minggu itu + stok & piutang per minggu', 'laporan', ['const kgM = kartuMerekMinggu(LP.lpMerekMinggu(awal, kini(), 8), s);', 'KL.klStokRpMinggu(kini(), 8), pnDso(kini(), 8), awal)', '${inti}${kgM}${susutM}${uangM}${perHari}',
      'h`${pilih}${hero}${uangM}${kaki}`, h`${inti}${kgM}${susutM}`', 'function kartuMerekMinggu(M, s)', 'function kartuStokPiutangMinggu(SM, DS, awal)', "import { pnDso } from './bon-logika.js';"]),
    ('Laporan: pilihan urut Per merek memakai daftar LP_URUT_MEREK (omzet Rp & untung/kg)', 'laporan', ["mrUrut: ({ u }) => set({ urutM: LP.LP_URUT_MEREK.some((x) => x.id === u) ? u : 'kg' })", 'kgMingguSemua: () => set({ kgMingguSemua: !st().kgMingguSemua })']),
    ('Dasbor › Margin & target: baris tetap untung per kg', 'dasbor', ['const G = Q.kg;', "out.push(baris('kg', 'Untung per kg <span class=\"ket\">'"]),
    ('Stok › Umur & putaran › Atur: target hari stok toko', 'stok', ["isian('umTargetMin', 'targetHariMin'", "isian('umTargetMaks', 'targetHariMaks'", 'targetHariMin: String(a.targetHariMin), targetHariMaks: String(a.targetHariMaks)', 'target hari stok toko ${A.targetHariMin}–${A.targetHariMaks} hari']),
    ('CSS deret, batang mini, pita target', 'css', ['.layar-laporan .lp-deret {', '.layar-laporan .lp-kg-mini {', '.layar-laporan .lp-kg-pita {', '.layar-laporan .lp-batang.delapan {']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_kpi_kg.py && python3 alat-uji/uji_kpi_kg.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['Paket P1', 'lpMerekMinggu', 'lpTerlaris', 'klStokRp', 'klDeretBulan', 'pnDso', 'targetHariMin', 'kgHitung']),
]
RUSAK = [
    ('kg tanpa modal ikut pembagi per kg (rentang)', LPL, "  if (tercatat) { g.adaHitung = true; g.omzetHitung += harga; g.hppHitung += p.hppTotalSaatJual || 0; g.kgHitung += Number(p.totalKg) || 0; } else { g.nTanpaHpp += 1; g.omzetTanpaHpp += harga; }\n  if (!ongkos) return;",
     "  g.kgHitung += Number(p.totalKg) || 0; if (tercatat) { g.adaHitung = true; g.omzetHitung += harga; g.hppHitung += p.hppTotalSaatJual || 0; } else { g.nTanpaHpp += 1; g.omzetTanpaHpp += harga; }\n  if (!ongkos) return;"),
    ('kg tanpa modal ikut pembagi per kg (bulan)', LPL, "    if (tercatat) { g.adaHitung = true; g.omzetHitung += harga; g.hppHitung += p.hppTotalSaatJual || 0; g.kgHitung += Number(p.totalKg) || 0; } else { g.nTanpaHpp += 1; g.omzetTanpaHpp += harga; }\n    if (ong)",
     "    g.kgHitung += Number(p.totalKg) || 0; if (tercatat) { g.adaHitung = true; g.omzetHitung += harga; g.hppHitung += p.hppTotalSaatJual || 0; } else { g.nTanpaHpp += 1; g.omzetTanpaHpp += harga; }\n    if (ong)"),
    ('untung per kg dibagi kg semua nota', LPL, "marginKg: margin !== null && g.kgHitung > 0 ? margin / g.kgHitung : null,", "marginKg: margin !== null && g.kgHitung > 0 ? margin / g.kgNota : null,"),
    ('omzet terlaris tanpa nota tanpa modal', LPL, "omzetSemua: g.omzetHitung + g.omzetTanpaHpp - g.returUang });", "omzetSemua: g.omzetHitung - g.returUang });"),
    ('omzet terlaris tanpa retur', LPL, "omzetSemua: g.omzetHitung + g.omzetTanpaHpp - g.returUang });", "omzetSemua: g.omzetHitung + g.omzetTanpaHpp });"),
    ('urut omzet diabaikan', LPL, "by === 'omzet' ? b.omzetSemua - a.omzetSemua || b.kg - a.kg :", "by === 'omzet' ? b.kg - a.kg :"),
    ('urut untung/kg dibalik', LPL, "const lpUrutNull = (x, y) => (x === null ? (y === null ? 0 : 1) : y === null ? -1 : y - x);", "const lpUrutNull = (x, y) => (x === null ? (y === null ? 0 : 1) : y === null ? -1 : x - y);"),
    ('pilihan urut omzet hilang', LPL, "['omzet', 'omzet Rp'], ", ""),
    ('tepat target dihitung di bawah', LPL, ": g.marginKg < T.rp ? 'bawah' : 'capai');", ": g.marginKg <= T.rp ? 'bawah' : 'capai');"),
    ('target 0 dianggap ada', LPL, "|| !(T && T.rp > 0) ? null :", "|| !T ? null :"),
    ('minggu berjalan dibanding minggu lalu penuh', LPL, "const sL = ugTambahHari(sampai, -7);", "const sL = ugTambahHari(akhir, -7);"),
    ('merek yang hilang minggu ini dibuang', LPL, ".filter((g) => (g.ini && (g.ini.omzet || g.ini.kg)) || (g.lalu && (g.lalu.omzet || g.lalu.kg)))", ".filter((g) => g.ini)"),
    ('penjaga rentang tidak membandingkan mesin', LPL, "const menutup = Math.abs(om - H.omzetPenuh) < 0.5 && Math.abs(mg - H.margin) < 0.5;", "const menutup = Math.abs(om - H.omzetPenuh - 1) < 0.5 && Math.abs(mg - H.margin) < 0.5;"),
    ('hari stok dibagi modal terjual seluruh rentang', KL, "const hari = hppHari !== null && rata > 0.5 ? rata / hppHari : null;", "const hari = hppHari !== null && rata > 0.5 ? rata / hpp : null;"),
    ('perputaran disetahunkan × 12', KL, "const tahun = putaran !== null ? putaran * 365 / n : null;", "const tahun = putaran !== null ? putaran * 12 : null;"),
    ('tipis & diam tertukar', KL, "hari < T.min ? 'tipis' : hari > T.maks ? 'diam' : 'pas'", "hari < T.min ? 'diam' : hari > T.maks ? 'tipis' : 'pas'"),
    ('target hari stok owner tidak dibaca', KL, "const T = { min: A.targetHariMin, maks: A.targetHariMaks, dariOwner: A.dariOwner,", "const T = { min: 7, maks: 14, dariOwner: A.dariOwner,"),
    ('nilai stok bukan modal tertahan', KL, "const hpp = R.semua.hpp; const rata = MT.rata;", "const hpp = R.semua.hpp; const rata = MT.kini;"),
    ('deret merek tidak urut kg', KL, ".sort((a, b) => kg[b] - kg[a] || a.localeCompare(b)).slice(0, nMerek || 8)", ".sort((a, b) => a.localeCompare(b)).slice(0, nMerek || 8)"),
    ('bawaan target hari stok bukan 7–14', SL, "targetHariMin: 7, targetHariMaks: 14 };", "targetHariMin: 14, targetHariMaks: 30 };"),
    ('batas bawah di atas batas atas lolos', SL, "if (o.targetHariMin > o.targetHariMaks) return { tolak:", "if (false) return { tolak:"),
    ('DSO memakai 7 hari', BL, "export const PN_DSO_HARI = 30;", "export const PN_DSO_HARI = 7;"),
    ('lebih bayar mengurangi piutang berjalan', BL, "if (d.sisa > 0) { piutang += d.sisa; nOrang += 1; }", "piutang += d.sisa; if (d.sisa > 0) { nOrang += 1; }"),
    ('saldo awal dihitung penjualan bon', BL, "if (m.jenis === 'jual' && String(m.tanggal || '') >= mulai", "if ((m.jenis === 'jual' || m.jenis === 'saldoAwal') && String(m.tanggal || '') >= mulai"),
    ('DSO tanpa catatan pertama memotong jendela', BL, "if (p && p > mulai) { mulai = p; sebab = 'catatan toko mulai ' + formatTanggal(p); }", ""),
    ('Dasbor per kg tidak ikut saringan', DL, "const sar = !!(SR && !SR.bawaan); const dari = sar ? SR.dari", "const sar = false; const dari = sar ? SR.dari"),
    ('saringan tidak diteruskan ke kelompok tambahan', DL, "H[n] = dbKelompok(n, kini, null, ingat, H.saring || null);", "H[n] = dbKelompok(n, kini, null, ingat);"),
    ('untung per kg Dasbor tetap bulan ini walau disaring', DL, "kg: aman(() => klKgBulan(key, kini)) };", "kg: aman(() => klKgBulan(iso.slice(0, 7), kini)) };"),
    ('kartu baru masuk susunan bawaan', WG, "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b']", "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren', 'kBulan', 'kWadah', 'kPemicu', 'kTagihan', 'kStok', 'kMutu', 'kPondasi', 'kB2b', 'kTerlaris']"),
    ('nama angka hari stok tidak ikut periode', WG, "hariStok: (S) => 'Hari stok · ' + S.nama,", ""),
]
RUSAK_STATIS = [
    ('deret bulanan tidak dipasang di Laba', 'laporan', '${keMana}${merek}${deret}${susutK}', '${keMana}${merek}${susutK}'),
    ('Mingguan tanpa per merek', 'laporan', '${inti}${kgM}${susutM}${uangM}${perHari}', '${inti}${susutM}${perHari}'),
    ('Per merek tanpa untung per kg', 'laporan', '${jaga}${kgMerek(M, TK)}${susut}', '${jaga}${susut}'),
    ('Dasbor tanpa baris untung per kg', 'dasbor', 'const G = Q.kg;', 'const G = null;'),
    ('Stok tanpa isian target hari stok', 'stok', "isian('umTargetMin', 'targetHariMin'", "isian('umTargetMin', 'x'"),
    ('komentar // menelan kode', 'lpl', "export const lpStatusKg = (g, T) =>", "// target\nexport const lpStatusKg = (g, T) => // tegas < target; const x = 1;\n  "),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_kpi_kg.py && python3 alat-uji/uji_kpi_kg.py --kontrol', 'true'),
]

ASAP = r"""
(function () {
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var p = catatanPertama(); var bulan = []; for (var i = 0; i < 6; i++) { var d = new Date(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1 - i, 1)).toISOString().slice(0, 7); if (akhirBulanIso(d) >= p) bulan.push(d); }
// per bulan: Σ per merek = mesin (omzet & laba kotor) · untung per kg se-toko = Laporan › Biaya
out.bulan = bulan.map(function (k) { var a = k + '-01', b = akhirBulanIso(k) < iso ? akhirBulanIso(k) : iso; var T = aman('terlaris ' + k, function () { return lpTerlaris(a, b, 10); });
  var KG = aman('kg ' + k, function () { return klKgBulan(k, kini); }); var K = aman('kendali ' + k, function () { return pemicuBiaya(kendaliBulan(k, kini)); }); var mk = K ? K.baris.find(function (r) { return r.id === 'marginKg'; }) : null;
  return { key: k, menutup: T ? T.menutup : null, urut: T ? T.daftar.every(function (g, j) { return j === 0 || T.daftar[j - 1].omzet >= g.omzet; }) : null,
    kgSamaBiaya: KG && mk ? (KG.marginKg === null ? mk.n === null : Math.abs(Math.round(KG.marginKg * 10) / 10 - mk.n) < 0.05) : null, nBawah: KG ? KG.nBawah : null }; });
var D8 = aman('minggu', function () { return daftarMinggu(kini, 8); }) || [];
out.minggu = D8.map(function (m) { var M = aman('minggu ' + m.awal, function () { return lpMerekMinggu(m.awal, kini, 8); }); return M ? (M.diarsip ? 'arsip' : M.menutup) : null; });
var SB = aman('stok bulan', function () { return klStokRpBulan(kini, 6); }); out.stokBulan = SB ? SB.map(function (b) { return b.sebelum ? 'sebelum' : b.hari === null ? null : Math.round(b.hari * 10) / 10; }) : null;
var SM = aman('stok minggu', function () { return klStokRpMinggu(kini, 8); }); out.stokMinggu = SM ? SM.map(function (b) { return b.sebelum ? 'sebelum' : b.hari === null ? null : Math.round(b.hari * 10) / 10; }) : null;
var DS = aman('dso', function () { return pnDso(kini, 8); }); out.dso = DS ? DS.deret.map(function (x) { return x.dso === null ? null : Math.round(x.dso * 10) / 10; }) : null;
var DB = aman('deret', function () { return klDeretBulan(kini, 6, 8); }); out.deret = DB ? { bulan: DB.bulan.length, merek: DB.merek.length, kotorSama: DB.bulan.every(function (b) { if (b.sebelum || b.galat) return true; var M = klMarginBulan(b.key, kini); return b.kotor === M.tangga[0].pct; }) } : null;
out.saring = {}; ['hari', 'kemarin', 'h7', 'bulan', 'bulanLalu', 'tahun'].forEach(function (id) { var S = dbSaring({ id: id }, kini); var D = aman('susun ' + id, function () { return dbTambahan(susunDasbor(kini, 'hari', null, null, S), kini); });
  var Wd = D ? aman('wg ' + id, function () { return wgSusun(['marginKg', 'hariStok', 'putaranStok', 'dso', 'kTerlaris', 'kTrenMerek'].map(function (x) { return { id: x }; }), D); }) : null;
  out.saring[id] = D && Wd ? { galat: D.kg && D.kg.galat ? D.kg.galat : D.kpi && D.kpi.kg && D.kpi.kg.galat ? D.kpi.kg.galat : '', wgGalat: Wd.filter(function (w) { return w.nilai === 'gagal dihitung'; }).map(function (w) { return w.id; }) } : 'gagal'; });
print(JSON.stringify(out));
})();
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
    # paket ini TANPA pintu tulis baru: setelan target hari stok menumpang aturanToko/stokUmur (susunAturUmur yang sudah ada)
    for k, dari, sampai in (('lpl', '// ==================== P1 · PER KG', '// ==================== PER JENIS'), ('kl', '// ---------- P1 · KPI per kg', '// ---------- 8 ·'), ('bl', '// ==================== P1 · LAMA PIUTANG', None), ('dl', 'export function dbKg(', 'DB_KELOMPOK.kg =')):
        t = src[k]; i = t.find(dari); j = t.find(sampai, i) if sampai and i >= 0 else len(t)
        if i < 0 or j < 0: g.append(k + ': bagian P1 tidak ketemu'); continue
        if 'koleksi:' in t[i:j] or 'dokumen:' in t[i:j]: g.append(k + ': bagian P1 menulis dokumen (paket ini tanpa pintu tulis baru)')
    if src['sl'].count("id: 'stokUmur'") != 1: g.append('stok-logika: setelan target hari stok bukan dokumen aturanToko/stokUmur yang sama')
    for k in ('lpl', 'kl', 'bl', 'dl', 'wg'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    # pola cacat lama (memori "komentar // menelan kode"): komentar // di tengah baris yang masih diikuti kode
    for k in ('laporan', 'dasbor', 'stok', 'lpl', 'kl', 'bl', 'dl', 'wg', 'sl'):
        for n, baris in enumerate(src[k].split('\n')):
            ekor = uji_sisa_sensus.komentar_ekor(baris)
            if ekor and re.search(r"\b[a-zA-Z]\w*: (opsi\.|\(|async |\[|\{|'|`)|;\s*(const|let|return|if)\b|\)\s*=>", ekor): g.append(k + ':' + str(n + 1) + ': komentar // menelan kode → ' + ekor.strip()[:90])
    i = src['baca'].find('Paket P1')
    if i >= 0 and ('rules v' in src['baca'][i:i + 6000] or 'firestore.rules' in src['baca'][i:i + 6000]): g.append('BACA-DULU menyebut rules untuk paket ini (paket ini tanpa rules)')
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
            S = dict(src); S[berkas] = S[berkas].replace(a, b, 1); l, g = statis(S)
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
            beres = (not h['galat'] and all(b['menutup'] and b['urut'] and b['kgSamaBiaya'] for b in h['bulan']) and all(m is True or m == 'arsip' for m in h['minggu'])
                     and h['stokBulan'] is not None and h['stokMinggu'] is not None and h['dso'] is not None and h['deret'] and h['deret']['kotorSama']
                     and all(isinstance(v, dict) and not v['galat'] and not v['wgGalat'] for v in h['saring'].values()))
            # angka RUPIAH toko TIDAK dicetak (repo publik) — hanya keadaan, jumlah, dan hari
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: per merek tidak menutup ke mesin, untung per kg ≠ Laporan › Biaya, atau Dasbor galat')
    sys.exit(1 if g or gs else 0)
