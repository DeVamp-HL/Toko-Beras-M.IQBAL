#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_susut_harga.py — PAKET SUSUT + HPP & HARGA MINIMUM (keputusan owner 26 Nov 2026). KOTAK PASIR (nama & angka CONTOH), jsc saja, TANPA peramban.
  Susut: target se-toko terukur (3 bulan selesai, DIGABUNG) / angka owner · kuning ≤ merah · dua tingkat per merek · susut mingguan = rumus bulanan
  (susutRentang ≡ merekBulan per merek) + penjaga yang menutup ke mesin · alami (timbang sampel) vs operasional · per pemasok (kedatangan yang masih di
  tumpukan, terbaru dulu) menutup ke rupiah · opname bulan ini (hitungan cocok persis kini dicatat, mesin tidak bergerak).
  HPP & harga: biaya toko per kg = 3 bulan SELESAI digabung · harga minimum = modal + biaya + target laba (tegas <, susut hanya angka bantu) · alarm HET
  (modal + biaya ≥ HET − jarak) · kalkulator sebelum beli (kg timbang jadi penyebut, tidak menulis) · HPP periode = nilai stok awal + beli − nilai stok akhir
  menutup ke HPP nota + susut bila harga beli tetap. Dasbor = angka yang sama apa adanya; layar memasang kartunya (statis).

    python3 alat-uji/uji_susut_harga.py            → N lulus · 0 gagal
    python3 alat-uji/uji_susut_harga.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru, uji_ringkasan_baru, uji_kunci_periode  # noqa: E402
JSC = uji_antar.JSC
SH = 'baru/js/layar/susut-harga-logika.js'; LG = 'baru/js/layar/laporan-logika.js'; CK = 'baru/js/layar/stok-catat-logika.js'; KB = 'baru/js/layar/kendali-biaya-logika.js'
DL = 'baru/js/layar/dasbor-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_ringkasan_baru.modul_dasbor() + [SH])))
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'dasbor': 'baru/js/layar/dasbor.js', 'harga': 'baru/js/layar/harga.js', 'stok': 'baru/js/layar/stok.js', 'index': 'baru/index.html',
          'pages': '.github/workflows/pages.yml', 'sh': SH, 'bundel': 'alat-uji/bundel_baru.py', 'cssL': 'baru/css/laporan.css', 'cssH': 'baru/css/harga.css', 'rs': 'baru/js/layar/riwayat-setelan-logika.js',
          'baca': 'baru/BACA-DULU.md', 'dl': DL}

KARUNG = lambda i, tgl, merk, kg, harga, hpp: {'id': i, 'tanggal': tgl, 'jam': '09:00', 'caraBayar': 'Tunai', 'namaPelanggan': '', 'jenis': 'karung', 'merkSumber': merk, 'beratKarungAcuan': 50,
                                               'jumlahKarung': kg / 50, 'totalKg': kg, 'hargaTotal': harga, 'hppTotalSaatJual': hpp, 'grupNota': 'g' + i}
KOTAK_SH = {
  'batchMasuk': [
    {'id': 101, 'tanggal': '2026-09-02', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 20, 'totalKg': 1000, 'subtotalHarga': 12000000, 'hargaPerKg': 12000}]},
    {'id': 102, 'tanggal': '2026-09-03', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Kembang', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 8, 'totalKg': 400, 'subtotalHarga': 4800000, 'hargaPerKg': 12000}]},
    {'id': 103, 'tanggal': '2026-10-02', 'jam': '08:00', 'pemasok': 'Pemasok Contoh B', 'caraBayar': 'Tunai', 'biayaBongkar': 0, 'merkList': [
      {'merk': 'Angsa', 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': 10, 'totalKg': 500, 'subtotalHarga': 6500000, 'hargaPerKg': 13000}]}],
  # September: Angsa 600 kg & Kembang 300 kg dengan modal 12.000/kg (harga beli tetap → HPP periode menutup persis)
  'penjualan': [KARUNG('s1', '2026-09-10', 'Angsa', 600, 7800000, 7200000), KARUNG('s2', '2026-09-11', 'Kembang', 300, 3900000, 3600000),
                KARUNG('o1', '2026-10-12', 'Angsa', 300, 3900000, 3700000), KARUNG('n1', '2026-11-04', 'Angsa', 100, 1300000, 1233333),
                KARUNG('n2', '2026-11-11', 'Kembang', 50, 650000, 600000)],
  'penyesuaianStok': [
    # Sep: Angsa −8 kg dari buku 400 → susut 8 ÷ (600 + 8) = 1,3158 % (MERAH di atas 1 %)
    {'id': 201, 'tanggal': '2026-09-20', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': 400, 'kgFisik': 392, 'selisihKg': -8, 'alasan': 'susut', 'nilaiRp': -96000, 'hppPerKgSaatOpname': 12000, 'bagian': 'tumpukan', 'bagianSistemKg': 400, 'bagianFisikKg': 392},
    # Okt: Angsa −3 kg dari buku 600 (500 kedatangan B terbaru + 100 sisa A) → 3 ÷ 303 = 0,990 % (KUNING); per pemasok B 2,5 kg / A 0,5 kg
    {'id': 202, 'tanggal': '2026-10-20', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': 600, 'kgFisik': 597, 'selisihKg': -3, 'alasan': 'susut', 'nilaiRp': -37500, 'hppPerKgSaatOpname': 12500, 'bagian': 'tumpukan', 'bagianSistemKg': 600, 'bagianFisikKg': 597},
    # Nov: Kembang −0,6 kg dengan timbang sampel — 0,5 kg ALAMI, 0,1 kg operasional
    {'id': 203, 'tanggal': '2026-11-10', 'jam': '10:00', 'merk': 'Kembang', 'kgSistem': 100, 'kgFisik': 99.4, 'selisihKg': -0.6, 'alasan': 'sampel', 'nilaiRp': -7200, 'hppPerKgSaatOpname': 12000, 'bagian': 'tumpukan', 'bagianSistemKg': 100, 'bagianFisikKg': 99.4,
     'sampel': {'karung': 2, 'kg': 99, 'isiKarung': 50, 'rata': 49.5, 'alamiKg': -0.5}},
    # Nov: hitungan Angsa yang COCOK PERSIS (jejak opname, tidak menggeser apa pun)
    {'id': 204, 'tanggal': '2026-11-12', 'jam': '10:00', 'merk': 'Angsa', 'kgSistem': 489, 'kgFisik': 489, 'selisihKg': 0, 'alasan': 'Cocok persis', 'nilaiRp': 0, 'hppPerKgSaatOpname': 12333, 'bagian': 'tumpukan', 'bagianSistemKg': 489, 'bagianFisikKg': 489, 'cocokPersis': True},
    # Nov: buku tanpa kedatangan (pindahan) — masuk kelompok "tanpa kedatangan", tetap menutup ke rupiah
    {'id': 205, 'tanggal': '2026-11-13', 'jam': '10:00', 'merk': 'Wadah Contoh', 'kgSistem': 5, 'kgFisik': 4.9, 'selisihKg': -0.1, 'alasan': 'tumpah', 'nilaiRp': -1000, 'hppPerKgSaatOpname': 10000}],
  'pengeluaranHarian': [
    {'id': 'h1', 'tanggal': '2026-09-05', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'listrik token', 'nominal': 100000},
    {'id': 'h2', 'tanggal': '2026-10-05', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'listrik token', 'nominal': 50000},
    {'id': 'h3', 'tanggal': '2026-11-05', 'jam': '10:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'listrik token', 'nominal': 900000}],
  'stokBahanKemasan': [{'id': 301, 'tipe': 'opname', 'jenis': 'kantong5', 'jumlah': -5, 'hargaTotal': 0, 'tanggal': '2026-11-14', 'jam': '10:00', 'pcsSistem': 100, 'pcsFisik': 95, 'catatan': 'hilang', 'nilaiRp': -5000, 'hargaPerPcsSaatOpname': 1000}],
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 13000}, {'id': 'Kembang', 'merk': 'Kembang', 'hargaPerKg': 12125}],
}
ATUR_DASAR = [{'id': 'catatStok', 'tempoHari': 21, 'modalFifoMulai': ''}, {'id': 'het', 'medium': 12700, 'premium': 14900, 'zona': 'Zona contoh', 'sumber': 'contoh', 'peta': {'Angsa': 'medium', 'Kembang': 'bukan'}}]

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T10:00:00+07:00'); var nId = 90000;
var W = { tanggal: '2026-11-18', jam: '10:00', kini: '2026-11-18T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'pesanan'].forEach(function (n) { pasok(n, []); });
Object.keys(SHK).forEach(function (n) { pasok(n, JSON.parse(J(SHK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-01', laci: 1000000, brankas: 0, rekening: 0, amplop: 0, diubahPada: '2026-09-01T14:00:00.000Z' }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var ganti = e.some(function (d) { return d.id === 'het'; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !(ganti && d.id === 'het'); }).concat(e)); };
aturDengan([]);
var g = function (M, m) { return M.merek.find(function (x) { return x.merek === m; }); };

// ---- 1 · dua tingkat per merek + rumus bulanan (penyebut tetap "beras yang keluar")
var MS = merekBulan('2026-09', KINI), MO = merekBulan('2026-10', KINI), MN = merekBulan('2026-11', KINI);
ok('1: Sep Angsa susut 8 ÷ (600 + 8) = 1,3158 % → MERAH (bukan kuning)', dekat(g(MS, 'Angsa').susutPct, 8 / 608 * 100, 1e-9) && g(MS, 'Angsa').tinggi === true && g(MS, 'Angsa').selidik === false, J(g(MS, 'Angsa')));
ok('1: Okt Angsa 3 ÷ 303 = 0,990 % → KUNING (di atas 0,5 %, tidak di atas 1 %)', dekat(g(MO, 'Angsa').susutPct, 3 / 303 * 100, 1e-9) && g(MO, 'Angsa').selidik === true && g(MO, 'Angsa').tinggi === false, J(g(MO, 'Angsa')));
ok('1: ringkasan bulan memisah merah & kuning', MS.susut.tinggi.length === 1 && MS.susut.selidik.length === 0 && MO.susut.selidik.length === 1 && MO.susut.tinggi.length === 0 && MO.susut.kuning === 0.5 && MO.susut.ambang === 1, J([MS.susut.tinggi.length, MO.susut.selidik.length]));
ok('1: penjaga merekBulan tetap menutup ke Laporan (laba kotor & susut)', MS.menutup && MO.menutup && MN.menutup, J([MS.kalimat, MN.kalimat]));

// ---- 2 · alami vs operasional (A71)
var kb = g(MN, 'Kembang');
ok('2: Kembang Nov: alami −0,5 kg (sampel) · operasional −0,1 kg · rupiah sebanding (−6.000 / −1.200)', dekat(kb.alamiKg, -0.5) && dekat(kb.operasionalKg, -0.1) && dekat(kb.alamiRp, -6000) && dekat(kb.operasionalRp, -1200) && kb.nSampel === 1, J(kb));
ok('2: ringkasan bulan: alami + operasional = selisih beras (naik − hilang)', dekat(MN.susut.alamiKg + MN.susut.operasionalKg, MN.susut.naikKg - MN.susut.kg) && dekat(MN.susut.alamiRp + MN.susut.operasionalRp, MN.susut.naikRp + MN.susut.rp), J(MN.susut));
var sp = ccSampel({ karung: '2', karung25: '', kg: '', sampelKarung: '2', sampelKg: '99' }, 'Kembang');
ok('2: ccSampel: 2 karung, sampel 99 kg → kg 99, alami = 99 − 100 (buku) = −1 kg', sp.ada && dekat(sp.kg, 99) && dekat(sp.alamiKg, -1) && dekat(sp.kgKarung, 100) && dekat(sp.kgKarungBuku, 100), J(sp));

// ---- 3 · mingguan = rumus bulanan (A40 · A72 · A128)
['2026-09', '2026-10', '2026-11'].forEach(function (k) { var M = merekBulan(k, KINI); var R = susutRentang(k + '-01', akhirBulanIso(k));
  ok('3: susutRentang(bulan ' + k + ') ≡ merekBulan per merek (kg, Rp, %, merah/kuning) & se-toko', R.menutup && M.merek.every(function (x) { var y = R.merek.find(function (z) { return z.merek === x.merek; });
    return y && dekat(y.susutKg, x.susutKg) && dekat(y.susutRp, x.susutRp) && (x.susutPct === null ? y.susutPct === null : dekat(y.susutPct, x.susutPct, 1e-9)) && y.tinggi === x.tinggi && y.selidik === x.selidik; }) && (M.susut.pct === null ? R.susut.pct === null : dekat(R.susut.pct, M.susut.pct, 1e-9)), J([R.kalimat, R.susut.pct, M.susut.pct])); });
var RW = susutRentang('2026-11-09', '2026-11-15');
ok('3: minggu 9–15 Nov: Kembang 0,6 ÷ (50 + 0,6); penjaga = Σ baris mesin (beras + pindahan + kantong) −13.200', RW.menutup && dekat(g(RW, 'Kembang').susutPct, 0.6 / 50.6 * 100, 1e-9) && RW.mesin === -13200, J([RW.kalimat, RW.mesin]));
var X = shMinggu('2026-11-09', '2026-11-15', KINI);
ok('3: shMinggu membawa target & status', X.target && X.target.pct !== null && (X.status === 'diAtas' || X.status === 'diBawah'), J([X.status, X.target.pct]));

// ---- 4 · target terukur & angka owner (A8)
var T = shTarget(KINI);
ok('4: target TERUKUR = Sep + Okt digabung: (8 + 3) ÷ (600 + 300 + 11) — bukan rata-rata persen, bulan berjalan tidak ikut', dekat(T.pct, 11 / 911 * 100, 1e-9) && T.terukur.n === 2 && !T.dariOwner && T.terukur.bulan.every(function (b) { return b.key !== '2026-11'; }), J(T));
aturDengan([{ id: 'merekLaporan', ambangSusutPersen: 1, teratas: 10, ambangSelidikPersen: 0.5, targetSusutPersen: 0.8 }]);
var T2 = shTarget(KINI);
ok('4: angka owner dipakai (0,8 %), terukur tetap disebut', T2.pct === 0.8 && T2.dariOwner && dekat(T2.terukur.pct, 11 / 911 * 100, 1e-9), J(T2));
aturDengan([{ id: 'merekLaporan', ambangSusutPersen: 0.3, teratas: 10 }]);
var A0 = aturMerek();
ok('4: dokumen lama (tanpa kuning) dengan merah 0,3 % → kuning tidak pernah di atas merah (0,3), target terukur', A0.ambangSelidikPersen === 0.3 && A0.ambangSusutPersen === 0.3 && A0.targetSusutPersen === null, J(A0));
aturDengan([]);
var A1 = aturMerek();
ok('4: bawaan: kuning 0,5 · merah 1 · target terukur (null)', A1.ambangSelidikPersen === 0.5 && A1.ambangSusutPersen === 1 && A1.targetSusutPersen === null && !A1.dariOwner, J(A1));
var s1 = susunAturMerek({ ambangSusutPersen: '1', ambangSelidikPersen: '1,5', teratas: '10', targetSusutPersen: '' }, W);
ok('4: kuning di atas merah DITOLAK', !!s1.tolak && !s1.dokumen, J(s1));
var s2 = susunAturMerek({ ambangSusutPersen: '1', ambangSelidikPersen: '0,5', teratas: '10', targetSusutPersen: '' }, W);
ok('4: target kosong = null (ikut terukur), satu dokumen aturanToko/merekLaporan', !s2.tolak && s2.dokumen.length === 1 && s2.dokumen[0].koleksi === 'aturanToko' && s2.dokumen[0].data.id === 'merekLaporan' && s2.dokumen[0].data.targetSusutPersen === null && s2.dokumen[0].data.ambangSelidikPersen === 0.5, J(s2));
var s3 = susunAturMerek({ ambangSusutPersen: '1', ambangSelidikPersen: '', teratas: '10', targetSusutPersen: '-2' }, W);
ok('4: target minus ditolak', !!s3.tolak, J(s3));
var TR = shTren(KINI, 6);
ok('4: tren: Sep 1,3158 % di atas target, Okt di bawah, Nov berjalan; jumlah buku dihitung per bulan', TR.bulan.length === 3 && TR.bulan[0].key === '2026-09' && TR.bulan[0].status === 'diAtas' && TR.bulan[1].status === 'diBawah' && TR.bulan[2].nHitung === 3 && TR.bulan[0].nMerah === 1 && TR.bulan[1].nKuning === 1, J(TR.bulan));

// ---- 5 · opname bulan ini (A135) & jejak cocok persis
var O = shOpname(KINI);
ok('5: opname Nov: Angsa (cocok persis) & Kembang dihitung — keduanya terhitung "sudah"', O.nKarung === 2 && O.nKarungDihitung === 2 && O.sudah.some(function (x) { return x.nama === 'Angsa'; }), J([O.n, O.nDihitung, O.belum, O.kalimat]));
var L0 = hitungLabaBersihRentang('2026-11-01', '2026-11-30'); var stokSebelum = hitungStokKarungPerMerk().Angsa.sisaKg;
var C1 = barangCocok('tumpukan').find(function (b) { return b.nama === 'Angsa'; }); var hit = {}; hit['tumpukan|Angsa'] = String(C1.sistem);
var YK = { sebagian: true, aneh: true, besar: true, ganda: true, susutPositif: true }; var R1 = susunSimpanCocok('tumpukan', hit, {}, W, YK, {});
var d1 = R1.dokumen && R1.dokumen[0] ? R1.dokumen[0].data : null;
ok('5: hitungan yang cocok persis DITULIS (selisih 0, nilaiRp 0, cocokPersis) — dulu tidak meninggalkan jejak', !R1.tolak && R1.dokumen.length === 1 && d1.selisihKg === 0 && d1.nilaiRp === 0 && d1.cocokPersis === true && /cocok persis/.test(R1.patch.kabar), J(R1));
pasok('penyesuaianStok', JSON.parse(J(SHK.penyesuaianStok)).concat(d1 ? [d1] : []));
ok('5: jejak cocok persis tidak menggeser stok, laba, maupun susut mesin', hitungStokKarungPerMerk().Angsa.sisaKg === stokSebelum && hitungLabaBersihRentang('2026-11-01', '2026-11-30').labaBersih === L0.labaBersih && barisSusutStok(function (t) { return t >= '2026-11-01'; }).length === barisSusutStok(function (t) { return t >= '2026-11-01'; }).filter(function (x) { return x.nilaiRp !== 0; }).length, J([stokSebelum, L0.labaBersih]));
pasok('penyesuaianStok', JSON.parse(J(SHK.penyesuaianStok)));
var C2 = barangCocok('tumpukan').find(function (b) { return b.nama === 'Kembang'; }); var hit2 = {}; hit2['tumpukan|Kembang'] = String(C2.sistem - 1); var smp = {}; smp['tumpukan|Kembang'] = { karung: 2, kgSampel: 99, isiKarung: 50, rata: 49.5, alamiKg: -1 };
var R2 = susunSimpanCocok('tumpukan', hit2, { 'tumpukan|Kembang': 'sampel' }, W, YK, smp);
ok('5: hitungan bersampel menyimpan bagian alami (−1 kg) tanpa dijepit', !R2.tolak && R2.dokumen[0].data.sampel && R2.dokumen[0].data.sampel.alamiKg === -1 && R2.dokumen[0].data.selisihKg === -1 && !R2.dokumen[0].data.cocokPersis, J(R2));

// ---- 6 · susut per pemasok (A73)
var P = shSusutPemasok('2026-09-01', '2026-11-18'); var pm = function (n) { return P.pemasok.find(function (x) { return x.pemasok === n; }); };
ok('6: Okt −3 kg dari buku 600 → kedatangan TERBARU dulu: B 2,5 kg (−31.250), A 0,5 kg; A total 8 + 0,5 + 0,6 = 9,1 kg', dekat(pm('Pemasok Contoh B').susutKg, 2.5) && dekat(pm('Pemasok Contoh B').susutRp, -31250) && dekat(pm('Pemasok Contoh A').susutKg, 9.1) && dekat(pm('Pemasok Contoh A').susutRp, -109450), J(P.pemasok));
ok('6: buku tanpa kedatangan = kelompoknya sendiri; Σ pemasok = Σ baris susut beras (−141.700) persis', P.menutup && P.total === -141700 && dekat(pm(SH_TANPA_KEDATANGAN).susutRp, -1000), J([P.kalimat, P.total]));
ok('6: pembanding kg datang di rentang & persen = hilang ÷ datang', pm('Pemasok Contoh A').kgMasuk === 1400 && dekat(pm('Pemasok Contoh A').pct, 9.1 / 1400 * 100, 1e-9) && pm('Pemasok Contoh B').kgMasuk === 500, J(P.pemasok));

// ---- 7 · biaya toko per kg & harga minimum (A97)
var B = shBiayaKg(KINI);
ok('7: biaya toko per kg = Sep + Okt DIGABUNG: 150.000 ÷ 1.200 kg = 125 (bulan berjalan tidak ikut, Agu tanpa jualan dilewati)', dekat(B.perKg, 125, 1e-9) && B.n === 2 && B.bulan.every(function (b) { return b.key !== '2026-11'; }), J(B));
var S = hgSemua(KINI); var MK = shMinimumKatalog(S, KINI, 'tampil'); var mk = function (k) { return MK.per[k]; };
ok('7: Angsa: minimum = modal 12.333,33 + biaya 125 + laba 0 = 12.458,33 → harga 13.000 aman', dekat(mk('Angsa|S').minimum, 18500000 / 1500 + 125, 1e-6) && mk('Angsa|S').status === 'aman', J(mk('Angsa|S')));
ok('7: Kembang harga 12.125 = minimum persis → aman (tegas <)', dekat(mk('Kembang|S').minimum, 12125, 1e-6) && mk('Kembang|S').status === 'aman', J(mk('Kembang|S')));
ok('7: susut TIDAK masuk minimum, hanya angka bantu (layak jual = modal ÷ (1 − target))', dekat(mk('Angsa|S').rinci.layak, (18500000 / 1500) / (1 - (11 / 911)), 1e-6) && dekat(mk('Angsa|S').rinci.minimumSusut, mk('Angsa|S').rinci.layak + 125, 1e-6), J(mk('Angsa|S').rinci));
pasok('katalogHargaKarung', [{ id: 'Angsa', merk: 'Angsa', hargaPerKg: 13000 }, { id: 'Kembang', merk: 'Kembang', hargaPerKg: 12124 }]);
var MK2 = shMinimumKatalog(hgSemua(KINI), KINI, 'tampil');
ok('7: Kembang Rp1 di bawah minimum → ditandai (peringatan, tidak menahan)', MK2.per['Kembang|S'].status === 'bawah' && MK2.nBawah === 1, J(MK2.per['Kembang|S']));
pasok('katalogHargaKarung', JSON.parse(J(SHK.katalogHargaKarung)));
aturDengan([{ id: 'hargaMinimum', targetLabaPerKg: 100, jarakHet: 500 }]);
var MK3 = shMinimumKatalog(hgSemua(KINI), KINI, 'tampil');
ok('7: target laba owner 100/kg → Kembang 12.125 kini di bawah minimum 12.225', dekat(MK3.per['Kembang|S'].minimum, 12225, 1e-6) && MK3.per['Kembang|S'].status === 'bawah', J(MK3.per['Kembang|S']));
var sa = susunAturMinimum({ targetLabaPerKg: '-5', jarakHet: '500' }, W); var sb = susunAturMinimum({ targetLabaPerKg: '150', jarakHet: '' }, W);
ok('7: setelan: minus ditolak; kosong = bawaan; satu dokumen aturanToko/hargaMinimum', !!sa.tolak && !sb.tolak && sb.dokumen.length === 1 && sb.dokumen[0].koleksi === 'aturanToko' && sb.dokumen[0].data.id === 'hargaMinimum' && sb.dokumen[0].data.targetLabaPerKg === 150 && sb.dokumen[0].data.jarakHet === 500, J([sa, sb]));

// ---- 8 · alarm dekat HET (A98)
aturDengan([]);
var H = shDekatHet(hgSemua(KINI), KINI);
var ha = H.daftar.find(function (x) { return x.merk === 'Angsa'; });
ok('8: Angsa medium HET 12.700: modal + biaya 12.458,33 → sisa 241,67 ≤ 500 → DEKAT; Kembang "bukan" tidak dinilai', ha && ha.status === 'dekat' && dekat(ha.jarak, 12700 - (18500000 / 1500 + 125), 1e-6) && H.nNilai === 1 && H.alarm.length === 1, J(H));
aturDengan([{ id: 'hargaMinimum', targetLabaPerKg: 0, jarakHet: 200 }]);
var H2 = shDekatHet(hgSemua(KINI), KINI);
ok('8: jarak owner 200 → aman (241,67 > 200)', H2.alarm.length === 0 && H2.daftar[0].status === 'aman', J(H2.daftar));
aturDengan([{ id: 'hargaMinimum', targetLabaPerKg: 0, jarakHet: 300 }, { id: 'het', medium: 12700, premium: 14900, peta: { Angsa: 'medium', Kembang: 'bukan' } }]);
var H3 = shDekatHet(hgSemua(KINI), KINI);
ok('8: jarak 300: modal + BIAYA (bukan modal saja) yang dibanding → dekat', H3.alarm.length === 1 && H3.alarm[0].status === 'dekat', J(H3.daftar));
aturDengan([{ id: 'het', medium: 12400, premium: 14900, peta: { Angsa: 'medium', Kembang: 'bukan' } }]);
var H4 = shDekatHet(hgSemua(KINI), KINI);
ok('8: HET 12.400 < modal + biaya → LEWAT (dijual tepat HET pun rugi)', H4.nLewat === 1 && H4.alarm[0].status === 'lewat', J(H4.alarm));
aturDengan([]);

// ---- 9 · kalkulator sebelum beli (A65 · A66)
var K = shHitungBeli({ hargaKg: '12.000', jumlahKarung: '100', isiKarung: '50', timbangKarung: '49,5', bongkarKg: '100', ongkir: '500.000', susut: '1', kelas: 'medium', hargaJual: '13.000' }, KINI, 0);
ok('9: modal per kg dibagi kg TIMBANG: 61.000.000 ÷ 4.950 = 12.323,23 (kurang timbang menaikkan modal)', K.siap && dekat(K.modalKg, 61000000 / 4950, 1e-6) && K.modalKg > 61000000 / 5000 && dekat(K.kurangKg, 50), J(K));
ok('9: modal per karung = modal per kg × 49,5 kg = 610.000', dekat(K.perKarung, 610000, 1e-6), J(K.perKarung));
ok('9: impas = modal + biaya 125; HET medium 12.700 → untung/kg = 12.700 − impas', dekat(K.impas, 61000000 / 4950 + 125, 1e-6) && dekat(K.untungHet, 12700 - K.impas, 1e-6) && dekat(K.layak, (61000000 / 4950) / 0.99, 1e-6) && dekat(K.untungJual, 13000 - K.impas, 1e-6), J(K));
var K2 = shHitungBeli({ hargaKg: '12000', jumlahKarung: '100' }, KINI, 80);
ok('9: tanpa timbang = kg nota; bongkar kosong = bongkar terukur; tidak menulis dokumen', K2.siap && K2.kgBuku === 5000 && K2.bongkarKg === 80 && !('dokumen' in K2) && !('dokumen' in K), J(K2));
ok('9: angka tidak masuk akal ditolak (tidak dihitung)', !shHitungBeli({ hargaKg: '0', jumlahKarung: '10' }, KINI, 0).siap && !shHitungBeli({ hargaKg: '12000', jumlahKarung: '10', susut: '100' }, KINI, 0).siap);

// ---- 10 · HPP periode (A11)
var HP = shHppPeriode('2026-09', KINI);
ok('10: Sep: stok awal 0 (sebelum sistem) + beli 16,8 jt − stok akhir 5.904.000 = 10.896.000', HP.stokAwal === 0 && HP.beli === 16800000 && Math.round(HP.stokAkhir) === 5904000 && Math.round(HP.hppPeriode) === 10896000, J(HP));
ok('10: harga beli tetap → HPP periode = HPP nota 10,8 jt + susut 96.000 PERSIS (beda 0)', Math.round(HP.hppNota) === 10800000 && HP.susut === 96000 && Math.abs(HP.beda) < 0.5, J([HP.hppNota, HP.susut, HP.beda]));
var HO = shHppPeriode('2026-10', KINI);
ok('10: Okt (harga beli naik 13.000) → beda disebut, dengan kalimat asal-usulnya (bukan disembunyikan)', HO.stokAwal === HP.stokAkhir && /harga beli berubah/.test(HO.kalimat) && HO.beli === 6500000, J([HO.beda, HO.kalimat]));

// ---- 11 · Dasbor apa adanya
var Q = dbMutu(KINI);
ok('11: dbMutu.susut = merekBulan bulan ini + target + opname (tanpa galat)', Q.susut && !Q.susut.galat && dekat(Q.susut.pct, MN.susut.pct, 1e-9) && dekat(Q.susut.target, 11 / 911 * 100, 1e-9) && Q.susut.opname.n === O.n && Array.isArray(Q.susut.merah), J(Q.susut));
var MT = shMinimumKatalog(hgSemua(KINI), KINI, 'terbit');
ok('11: dbMutu.harga = harga TERBIT di bawah minimum & alarm HET apa adanya', Q.harga && !Q.harga.galat && Q.harga.nBawah === MT.nBawah && Q.harga.nDekat === shDekatHet(hgSemua(KINI), KINI).nDekat && dekat(Q.harga.biayaKg, 125, 1e-9), J(Q.harga));

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('Laporan › Laba: kartu Susut (target, tren, alami, opname, per pemasok)', 'laporan', ["import * as SH from './susut-harga-logika.js';", 'const susutK = kartuSusut(MB);', 'function kartuSusut(M)', 'SH.shTren(kini(), 6)', 'SH.shOpname(kini())', 'SH.shSusutPemasok(R3.awal, R3.akhir)', 'data-k="sh-alami"']),
    ('Laporan › Laba: kuning & Atur target / dua ambang', 'laporan', ['lp-cip kuning', 'data-k="mr-kuning"', 'data-kunci="targetSusutPersen"', 'data-kunci="ambangSelidikPersen"']),
    ('Laporan › Mingguan: susut per merek sementara', 'laporan', ['const susutM = kartuSusutMinggu(R);', 'function kartuSusutMinggu(R)', 'SH.shMinggu(R.awal, akhir, kini())']),
    ('Laporan › Bulanan: HPP periode', 'laporan', ['SH.shHppPeriode(key, kini())', 'function kartuHppPeriode(X)']),
    ('Harga › Katalog: harga minimum & HET + lembar ubah + sebelum terbit', 'harga', ["import * as SH from './susut-harga-logika.js';", '${gambarMinimum(s, S)}', 'function gambarMinimum(s, S)', 'data-k="ubah-min"', 'data-k="tb-min"', 'SH.susunAturMinimum(st().aturMin || {}, waktu())']),
    ('Harga › Belanja: kalkulator sebelum beli (tidak menulis)', 'harga', ['${gambarHitungBeli(s)}', 'function gambarHitungBeli(s)', 'SH.shHitungBeli(a, kini(), bk)', "'aturMin', 'hb',"]),
    ('Dasbor: baris susut vs target, opname, harga minimum, dekat HET', 'dasbor', ["out.push(baris('opname'", "out.push(baris('minimum'", "out.push(baris('dekatHet'", 'const SS = Q.susut;']),
    ('dasbor-logika memanggil susut-harga-logika', 'dl', ["import { shDasborSusut, shRingkasHarga } from './susut-harga-logika.js';", 'aman(() => shDasborSusut(M, kini))', 'aman(() => shRingkasHarga(kini))']),
    ('Stok › Cocokkan menyimpan bagian alami sampel', 'stok', ['rata: S.rata, alamiKg: S.alamiKg }']),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/susut-harga-logika.js">']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_susut_harga.py && python3 alat-uji/uji_susut_harga.py --kontrol']),
    ('bundel uji melengkapi modul untuk Dasbor', 'bundel', ["SH_MODUL = 'baru/js/layar/susut-harga-logika.js'", "SH_PEMAKAI = ('dasbor-logika.js',)"]),
    ('riwayat setelan menamai dokumen baru', 'rs', ["hargaMinimum: 'Harga minimum & HET'", "merekLaporan: 'Susut & per merek'"]),
    ('gerak: kartu susut & harga minimum bergerak + hormat reduced motion', 'cssL', ['lpShTumbuh', 'lpShMasuk', '.layar-laporan .lp-sh-target > div, .layar-laporan .lp-sh-tren i { animation: none; }']),
    ('gerak Harga', 'cssH', ['hgShMasuk', '.layar-harga .sh-minimum .het-baris, .layar-harga .sh-hitung .sh-hasil > div { animation: none; }']),
    ('BACA-DULU menyebut paket ini', 'baca', ['## Paket Susut + HPP & harga minimum', 'uji_susut_harga.py']),
    ('modul tanpa DOM & hanya menulis setelan', 'sh', []),
]

RUSAK = [
    ('kuning juga menyala di merek merah', LG, "selidik: susutPct !== null && kuning !== undefined && kuning !== null && susutPct > kuning && !(susutPct > ambang),", "selidik: susutPct !== null && kuning !== undefined && kuning !== null && susutPct > kuning,"),
    ('kuning boleh di atas merah (dokumen lama)', LG, "isFinite(k) && k > 0 && k <= merah ? k : Math.min(LP_MEREK_BAWAAN.ambangSelidikPersen, merah);", "isFinite(k) && k > 0 && k <= 100 ? k : LP_MEREK_BAWAAN.ambangSelidikPersen;"),
    ('Atur menerima kuning di atas merah', LG, "if (kb > pb) return { tolak:", "if (false) return { tolak:"),
    ('alami = seluruh selisih', LG, "g.nSampel += 1; g.alamiKg += ak;", "g.nSampel += 1; g.alamiKg += sk;"),
    ('penjaga mingguan tanpa kelompok di luar merek', LG, "const kelompok = merek.reduce((a, g) => a + g.susutRp + g.naikRp, 0) + luar.reduce((a, g) => a + g.susutRp + g.naikRp, 0);", "const kelompok = merek.reduce((a, g) => a + g.susutRp + g.naikRp, 0);"),
    ('target = rata-rata persen (bukan digabung)', SH, "const terukur = dipakai.length && jual + kg > 0 ? kg / (jual + kg) * 100 : null;", "const terukur = dipakai.length ? dipakai.reduce((a, x) => a + x.pct, 0) / dipakai.length : null;"),
    ('target mengabaikan angka owner', SH, "const pct = A.targetSusutPersen !== null ? A.targetSusutPersen : terukur;", "const pct = terukur;"),
    ('target ikut bulan berjalan', SH, "if (dipakai.length >= SH_BULAN || b.key >= kunci || akhirBulanIso(b.key) < MULAI_SUSUT_LABA", "if (dipakai.length >= SH_BULAN || b.key > kunci || akhirBulanIso(b.key) < MULAI_SUSUT_LABA"),
    ('per pemasok: kedatangan TERLAMA dulu', SH, "for (let j = L.length - 1; j >= 0 && sisa > 0.004; j--)", "for (let j = 0; j < L.length && sisa > 0.004; j++)"),
    ('per pemasok: buku tanpa kedatangan hilang dari jumlah', SH, "const bagi = tot > 0 ? ambil : [{ pemasok: SH_TANPA_KEDATANGAN, kg: 1 }];", "const bagi = tot > 0 ? ambil : [];"),
    ('biaya per kg ikut bulan berjalan', SH, "if (bulan.length >= SH_BULAN || b.key >= kunci) return; const X = kbBiayaKgBulan", "if (bulan.length >= SH_BULAN || b.key > kunci) return; const X = kbBiayaKgBulan"),
    ('biaya per kg = rata-rata per bulan (bukan digabung)', SH, "const perKg = kg > 0 ? biaya / kg : null;", "const perKg = bulan.length ? bulan.reduce((a, x) => a + x.perKg, 0) / bulan.length : null;"),
    ('biaya per kg memakai semua biaya (termasuk susut & hapus buku)', KB, "return { key, nama: X.nama, biayaToko: X.biayaToko, kgTerjual: X.kgTerjual,", "return { key, nama: X.nama, biayaToko: X.semuaBiaya, kgTerjual: X.kgTerjual,"),
    ('harga minimum: sama dengan minimum dianggap di bawah', SH, "const status = minimum === null ? 'tanpaBiaya' : !(n > 0) ? 'lubang' : n + 0.5 < minimum ? 'bawah' : 'aman';", "const status = minimum === null ? 'tanpaBiaya' : !(n > 0) ? 'lubang' : n <= minimum ? 'bawah' : 'aman';"),
    ('harga minimum memuat susut (bukan rumus owner)', SH, "minimum: ada ? modalKg + biayaKg + labaKg : null,", "minimum: ada ? layak + biayaKg + labaKg : null,"),
    ('harga minimum tanpa target laba owner', SH, "const R = shMinimumKg(b.modalUnit / kg, beras, T.pct, B.perKg, A.targetLabaPerKg);", "const R = shMinimumKg(b.modalUnit / kg, beras, T.pct, B.perKg, 0);"),
    ('HET: modal saja (biaya toko lupa)', SH, "const R = shMinimumKg(b.modalUnit, true, T.pct, B.perKg, 0); const biayaKg = R.minimum;", "const R = shMinimumKg(b.modalUnit, true, T.pct, B.perKg, 0); const biayaKg = R.modal;"),
    ('HET: lewat memakai > (sama dengan HET tidak lewat)', SH, "const status = biayaKg >= het - 1e-6 ? 'lewat'", "const status = biayaKg > het + 1e9 ? 'lewat'"),
    ('kalkulator: modal dibagi kg nota (timbang diabaikan)', SH, "const modalKg = modal / kgBuku;", "const modalKg = modal / kgNota;"),
    ('HPP periode tanpa susut di pembanding', SH, "const pembanding = L.hpp + susut;", "const pembanding = L.hpp;"),
    ('HPP periode tanpa stok akhir', SH, "const hppPeriode = stokAwal + beli + dicatat + bahan + upah - stokAkhir;", "const hppPeriode = stokAwal + beli + dicatat + bahan + upah;"),
    ('Cocokkan: yang cocok persis tidak ditulis lagi', CK, "const berubah = c.baris.filter((b) => b.ada && (b.selisih !== 0 || tab === 'wadah' || tab === 'tumpukan' || tab === 'kemasan'));", "const berubah = c.baris.filter((b) => b.ada && (b.selisih !== 0 || tab === 'wadah'));"),
    ('Cocokkan: bagian alami tidak disimpan', CK, "? { alamiKg: ckB2(Number(x.alamiKg)) } : {}) } : {}))", "? {} : {}) } : {}))"),
    ('ccSampel: alami tanpa rasio sampel', CK, "alamiKg: ckB2(kgKarung * rasio - kgAsli) };", "alamiKg: ckB2(kgKarung - kgAsli) };"),
    ('Dasbor tanpa susut paket ini', DL, "const SS = M.galat || M.diarsip ? null : aman(() => shDasborSusut(M, kini));", "const SS = null;"),
]
RUSAK_STATIS = [
    ('Laporan tanpa kartu Susut', 'laporan', 'const susutK = kartuSusut(MB);', "const susutK = '';"),
    ('Mingguan tanpa susut per merek', 'laporan', 'const susutM = kartuSusutMinggu(R);', "const susutM = '';"),
    ('Harga tanpa harga minimum', 'harga', '${gambarMinimum(s, S)}', ''),
    ('Belanja tanpa kalkulator', 'harga', '${gambarHitungBeli(s)}', ''),
    ('Dasbor tanpa baris opname', 'dasbor', "out.push(baris('opname'", "out.push(baris('opnamex'"),
    ('Stok tidak membawa alami', 'stok', 'rata: S.rata, alamiKg: S.alamiKg }', 'rata: S.rata }'),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_susut_harga.py && python3 alat-uji/uji_susut_harga.py --kontrol', 'true'),
]
BON_PEMASOK_LAMA = uji_ringkasan_baru.BON_PEMASOK_LAMA

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var out = { akhir: hariIniIso(kini), per: [], galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
daftarBulan(kini, 6).forEach(function (b) { if (akhirBulanIso(b.key) < '2026-09-01' || tahunDiarsip(b.key)) return;
  var M = aman('merekBulan ' + b.key, function () { return merekBulan(b.key, kini); }); var R = aman('susutRentang ' + b.key, function () { return susutRentang(b.key + '-01', akhirBulanIso(b.key)); });
  var H = aman('hppPeriode ' + b.key, function () { return shHppPeriode(b.key, kini); });
  var sama = !!(M && R) && M.merek.every(function (x) { var y = R.merek.find(function (z) { return z.merek === x.merek; }); return y && Math.abs(y.susutRp - x.susutRp) < 0.5 && Math.abs(y.susutKg - x.susutKg) < 0.005 && (x.susutPct === null ? y.susutPct === null : Math.abs(y.susutPct - x.susutPct) < 1e-9); });
  out.per.push({ key: b.key, merek: !!(M && M.menutup), minggu: !!(R && R.menutup), sama: sama, pct: M && M.susut ? M.susut.pct : null, alami: M && M.susut ? [M.susut.nSampel, M.susut.nSampelLama] : null, hppBeda: H ? Math.round(H.beda) : null, hppPeriode: H ? Math.round(H.hppPeriode) : null }); });
var R3 = shRentang3(kini); var P = aman('pemasok', function () { return shSusutPemasok(R3.awal, R3.akhir); });
out.pemasok = P ? { menutup: P.menutup, n: P.pemasok.length, baris: P.nBaris } : null;
var T = aman('target', function () { return shTarget(kini); }); out.target = T ? { pct: T.pct, n: T.terukur.n } : null;
var O = aman('opname', function () { return shOpname(kini); }); out.opname = O ? [O.nDihitung, O.n] : null;
var B = aman('biaya', function () { return shBiayaKg(kini); }); out.biayaKg = B ? B.perKg : null;
var S = aman('katalog', function () { return hgSemua(kini); }); var MK = S ? aman('minimum', function () { return shMinimumKatalog(S, kini, 'terbit'); }) : null; var HT = S ? aman('het', function () { return shDekatHet(S, kini); }) : null;
out.minimum = MK ? MK.nBawah : null; out.het = HT ? [HT.keadaan, HT.nDekat, HT.nLewat, HT.nBelum] : null;
var Q = aman('dbMutu', function () { return dbMutu(kini); }); out.dasbor = Q ? { susut: !!(Q.susut && !Q.susut.galat), harga: !!(Q.harga && !Q.harga.galat) } : null;
var D = daftarMinggu(kini, 4); out.minggu = D.map(function (m) { var X = aman('minggu ' + m.awal, function () { return shMinggu(m.awal, m.akhir, kini); }); return X ? (X.diarsip ? 'arsip' : X.menutup) : null; });
print(JSON.stringify(out));
"""


def bundel_js(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)
    if js.count(BON_PEMASOK_LAMA) == 1: js = js.replace(BON_PEMASOK_LAMA, BON_PEMASOK_LAMA.replace('susunBon(', 'bpSusunBon('))
    return js


def jalan(teks):
    js = bundel_js(teks)
    jam = "var __KINI = new Date('2026-11-18T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(jam + js + '\nvar KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar SHK = ' + json.dumps(KOTAK_SH) + ';\nvar ATUR = ' + json.dumps(ATUR_DASAR) + ';\n' + SKENARIO); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    sh = src['sh']
    if 'document.' in sh or 'tulisDokumen' in sh or 'window.' in sh: g.append('susut-harga-logika menyentuh DOM / menulis langsung — modul ini cuma menyusun')
    if sh.count("koleksi: 'aturanToko'") != 1 or 'koleksi:' in sh.replace("koleksi: 'aturanToko'", ''): g.append('susut-harga-logika menulis dokumen selain setelan aturanToko/hargaMinimum')
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
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            tgl = os.path.basename(cad[-1]).split('miqbal-')[-1][:10]
            f.write("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP); pth = f.name
        r = subprocess.run([JSC, pth], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(pth)
        out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out); beres = not h['galat'] and h['per'] and all(x['merek'] and x['minggu'] and x['sama'] for x in h['per']) and h['pemasok'] and h['pemasok']['menutup'] and h['dasbor'] and h['dasbor']['susut'] and h['dasbor']['harga'] and all(m in (True, 'arsip') for m in h['minggu'])
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: mingguan ≠ bulanan, penjaga tidak menutup, atau Dasbor galat')
    sys.exit(1 if g or gs else 0)
