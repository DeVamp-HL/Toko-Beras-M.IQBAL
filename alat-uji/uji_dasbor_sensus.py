#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_dasbor_sensus.py — PAKET DASBOR (keputusan owner 26 Nov 2026, sensus ulang 1c: B1 B9 B88 B89 B90 B91 B95 B109 B113 B127). KOTAK PASIR (nama & angka
CONTOH), jsc saja, TANPA peramban.
  B1/B113 omzet hari ini vs kemarin jam segini & hari yang sama minggu lalu jam segini (rumus Cincin rkJamSegini — satu sumber; nota sesudah jam sekarang tidak
  ikut) · B9 rata-rata nilai nota hari ini, bulan ini vs bulan lalu sampai tanggal yang sama · B95 saringan tanggal (tujuh pilihan, rentang, pembanding, laba
  bersih hanya bulan utuh/berjalan = Σ kendaliBulan) · B109 cap "data per HH.MM" (tersambung · tanpa internet · cadangan) · B91 headline (omzet + laba + mendesak)
  · B113 enam bulan (trenBiaya · pdPosisiBulan = pdKekayaan) · B127 stok minimum per barang (bawaan = Belanja ambangHari dengan aturan baca yang SAMA, hari =
  hariHabis Belanja, per barang hari ATAU minimum jumlah; Perlu perhatian = Dasbor; Belanja menggeser batas merek itu) · B88/B89 widget (katalog, bawaan,
  bersih/pindah/hapus/ukuran/tambah, simpan satu dokumen aturanToko/dasbor, TIAP widget menutup ke kartu sumbernya).

    python3 alat-uji/uji_dasbor_sensus.py            → N lulus · 0 gagal
    python3 alat-uji/uji_dasbor_sensus.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_jual_baru, uji_ringkasan_baru, uji_kunci_periode, uji_susut_harga  # noqa: E402
JSC = uji_antar.JSC
DL = 'baru/js/layar/dasbor-logika.js'; WG = 'baru/js/layar/dasbor-widget-logika.js'; SM = 'baru/js/layar/stok-minimum-logika.js'; RK = 'baru/js/layar/ringkasan-logika.js'
LPL = 'baru/js/layar/laporan-logika.js'; BL = 'baru/js/layar/belanja-logika.js'; PDL = 'baru/js/layar/pondasi-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_ringkasan_baru.modul_dasbor() + ['baru/js/layar/riwayat-logika.js', 'baru/js/layar/kpi-laba-logika.js', WG, SM])))
SUMBER = {'dasbor': 'baru/js/layar/dasbor.js', 'kisi': 'baru/js/layar/dasbor-kisi.js', 'ringkasan': 'baru/js/layar/ringkasan.js', 'stok': 'baru/js/layar/stok.js', 'app': 'baru/js/app.js',
          'fb': 'baru/js/data/firebase.js', 'css': 'baru/css/ringkasan.css', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'bundel': 'alat-uji/bundel_baru.py',
          'dl': DL, 'wg': WG, 'sm': SM, 'rk': RK, 'rs': 'baru/js/layar/riwayat-setelan-logika.js', 'smp': 'baru/js/layar/stok-minimum-panel.js', 'index': 'baru/index.html'}

KS = uji_susut_harga.KOTAK_SH
KARUNG = uji_susut_harga.KARUNG
def JAM(x, jam):
    x = dict(x); x['jam'] = jam; return x
KOTAK = dict(KS)
# hari ini Rabu 18 Nov (KINI 14.00): 09.00 Angsa 40 kg + 13.00 Kembang 10 kg = Rp650.000, 2 nota · kemarin 08.00 Rp260.000 + 16.00 Rp390.000 (sesudah jam segini)
# · Rabu lalu 11 Nov 09.00 Kembang Rp650.000 (KS n2). Bulan ini s.d. 18 Nov = 3.250.000 / 6 nota; Oktober s.d. 18 Okt = 3.900.000 / 1 nota (KS o1).
KOTAK['penjualan'] = KS['penjualan'] + [JAM(KARUNG('t1', '2026-11-18', 'Angsa', 40, 520000, 493320), '09:00'), JAM(KARUNG('t2', '2026-11-18', 'Kembang', 10, 130000, 120000), '13:00'),
                                       JAM(KARUNG('k1', '2026-11-17', 'Angsa', 20, 260000, 246660), '08:00'), JAM(KARUNG('k2', '2026-11-17', 'Angsa', 30, 390000, 369990), '16:00')]
# tagihan bulanan November (listrik): laba bersih SEBULAN memotong penuh, "sampai hari ini" memotong jatah sampai hari ini — keduanya beda (widget memakai yang mana)
KOTAK['biayaBulanan'] = [{'id': '2026-11', 'bulan': '2026-11', 'listrik': 300000, 'internet': 0, 'akses': 0, 'keamanan': 0, 'tanggalBayarPos': {'listrik': '2026-11-10'}}]
ATUR = uji_susut_harga.ATUR_DASAR

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return a !== null && b !== null && a !== undefined && b !== undefined && Math.abs(a - b) < (t || 0.005); };
var KINI = new Date('2026-11-18T14:00:00+07:00'); var nId = 90000;
var W = { tanggal: '2026-11-18', jam: '14:00', kini: '2026-11-18T07:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK0).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'pesanan', 'karantina', 'persetujuan', 'cekGudang', 'kepatuhanCek'].forEach(function (n) { pasok(n, []); });
Object.keys(GK).forEach(function (n) { pasok(n, JSON.parse(J(GK[n]))); });
pasok('pengaturan', [{ id: 'titikKas', tanggal: '2026-09-01', laci: 1000000, brankas: 250000, rekening: 0, amplop: 0, diubahPada: '2026-09-01T14:00:00.000Z' }, { id: 'jenisBeras', peta: { Kembang: 'IR42' } }]);
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra) { var e = extra || []; var id = {}; e.forEach(function (d) { id[d.id] = 1; }); pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return !id[d.id]; }).concat(e)); };
aturDengan([]);
var iso = '2026-11-18';

// ==================== 1 · B1 / B113 · banding jam segini ====================
var B = dbBanding(KINI); var R = rekapHari(iso);
ok('1: omzet & nota hari ini = Laporan › Harian (rekapHari): Rp650.000 · 2 nota', B.omzet === R.omzet && B.omzet === 650000 && B.nota === 2 && B.nota === R.n, J([B.omzet, B.nota, R.omzet, R.n]));
ok('1: indeks Cincin sehari penuh MENUTUP ke rekapHari (satu sumber omzet)', B.cincin && B.cincin.omzet === R.omzet && B.cincin.nota === R.n, J(B.cincin));
ok('1: kemarin JAM SEGINI = 08.00 saja (nota 16.00 belum terjadi jam segini): Rp260.000 · 1 nota · +150 %', B.kemarin.ada && B.kemarin.omzet === 260000 && B.kemarin.nota === 1 && dekat(B.kemarin.pct, 150) && B.kemarin.selisih === 390000, J(B.kemarin));
ok('1: kemarin sehari penuh tetap Rp650.000 (pembanding jam segini bukan omzet kemarin)', rekapHari('2026-11-17').omzet === 650000);
ok('1: hari yang sama minggu lalu jam segini = Rabu 11 Nov: Rp650.000 · 0 %', B.mingguLalu.ada && B.mingguLalu.iso === '2026-11-11' && B.mingguLalu.nama === 'Rabu lalu' && B.mingguLalu.omzet === 650000 && dekat(B.mingguLalu.pct, 0), J(B.mingguLalu));
var B5 = dbBanding(new Date('2026-11-18T08:30:00+07:00'));
ok('1: jam 08.30: kemarin jam segini Rp260.000, hari ini belum ada yang jam ≤ 08.30 tapi omzet hari ini = sehari (Laporan)', B5.kemarin.omzet === 260000 && B5.omzet === 650000, J([B5.kemarin, B5.omzet]));
var B0 = dbBanding(new Date('2026-08-08T10:00:00+07:00'));
ok('1: sebelum toko mencatat: pembanding disebut, bukan Rp0', !B0.kemarin.ada && B0.kemarin.ket === 'belum ada catatan' && !B0.mingguLalu.ada, J([B0.kemarin, B0.mingguLalu]));
ok('1: kunci ingatan banding bergeser tiap 5 menit (jam segini tidak beku pagi sampai sore)', dbKunciTambahan('banding', KINI) !== dbKunciTambahan('banding', new Date('2026-11-18T14:05:00+07:00')) && dbKunciTambahan('stokMin', KINI) === 'stokMin');

// ==================== 2 · B9 rata-rata nilai nota ====================
ok('2: rata-rata nota hari ini = omzet ÷ nota = Rp325.000', B.rata === 325000, B.rata);
var M = B.bulan;
ok('2: bulan ini (1–18 Nov): Rp3.250.000 · 6 nota · rata 541.666,67 = lpHariRentang', M.ini.omzet === 3250000 && M.ini.nota === 6 && dekat(M.ini.rata, 3250000 / 6) && M.ini.omzet === lpHariRentang('2026-11-01', iso).omzetPenuh, J(M.ini));
ok('2: bulan lalu SAMPAI TANGGAL YANG SAMA (1–18 Okt): Rp3.900.000 · 1 nota → omzet −16,7 %, rata −86,1 %', M.lalu.ada && M.sampaiLalu === '2026-10-18' && M.lalu.omzet === 3900000 && M.lalu.nota === 1 && dekat(M.pctOmzet, (3250000 / 3900000 - 1) * 100) && dekat(M.pctRata, (3250000 / 6 / 3900000 - 1) * 100), J([M.lalu, M.pctOmzet, M.pctRata]));
var M31 = dbBulanBanding(new Date('2026-10-31T12:00:00+07:00'));
ok('2: 31 Okt dibanding September sampai 30 Sep (bulan pendek: tanggal terakhir, bukan 31 Sep)', M31.sampaiLalu === '2026-09-30', M31.sampaiLalu);
var LRn = lpRataNota('2026-11-05', '2026-11-05');
ok('2: rentang tanpa nota: rata null (bukan Rp0 atau NaN)', LRn.nota === 0 && LRn.rata === null, J(LRn));

// ==================== 3 · B95 saringan tanggal ====================
var P = {}; DB_PERIODE.forEach(function (x) { P[x[0]] = dbPeriode({ id: x[0], dari: '2026-11-04', sampai: '2026-11-11' }, KINI); });
ok('3: tujuh pilihan: Hari ini · Kemarin · 7 hari · Bulan ini · Bulan lalu · Tahun ini · Pilih tanggal', DB_PERIODE.map(function (x) { return x[0]; }).join() === 'hari,kemarin,h7,bulan,bulanLalu,tahun,pilih');
ok('3: Hari ini = banding (omzet, nota, rata) & pembanding = kemarin jam segini', P.hari.omzet === B.omzet && P.hari.nota === B.nota && P.hari.banding.ada && P.hari.banding.omzet === 260000 && dekat(P.hari.pctOmzet, 150) && !P.hari.laba, J(P.hari.banding));
ok('3: Kemarin = 17 Nov penuh Rp650.000 · 2 nota; pembanding Senin 16 Nov (tanpa nota)', P.kemarin.dari === '2026-11-17' && P.kemarin.omzet === 650000 && P.kemarin.nota === 2 && P.kemarin.banding.ada && P.kemarin.banding.omzet === 0 && P.kemarin.pctOmzet === null, J(P.kemarin));
ok('3: 7 hari = 12–18 Nov (Rp1.300.000) vs 5–11 Nov (Rp650.000)', P.h7.dari === '2026-11-12' && P.h7.sampai === iso && P.h7.omzet === 1300000 && P.h7.banding.omzet === 650000 && dekat(P.h7.pctOmzet, 100), J([P.h7.dari, P.h7.omzet, P.h7.banding]));
var KB = kendaliBulan('2026-11', KINI), KO = kendaliBulan('2026-10', KINI), KS9 = kendaliBulan('2026-09', KINI);
ok('3: Bulan ini = bulan banding & laba bersih = kendaliBulan Nov (mesin Laporan › Laba)', P.bulan.omzet === M.ini.omzet && P.bulan.banding.omzet === M.lalu.omzet && P.bulan.laba && P.bulan.laba.labaBersih === KB.labaBersih && P.bulan.laba.semuaBiaya === KB.semuaBiaya, J([P.bulan.laba, KB.labaBersih]));
ok('3: Bulan lalu = Oktober penuh; laba bersih = kendaliBulan Okt; September TIDAK UTUH (catatan mulai 2 Sep) → disebut, bukan dibandingkan', P.bulanLalu.dari === '2026-10-01' && P.bulanLalu.sampai === '2026-10-31' && P.bulanLalu.omzet === 3900000 && !P.bulanLalu.banding.ada && /tidak utuh/.test(P.bulanLalu.banding.ket) && P.bulanLalu.pctOmzet === null && P.bulanLalu.laba.labaBersih === KO.labaBersih, J([P.bulanLalu.omzet, P.bulanLalu.banding, P.bulanLalu.laba]));
var PBL = dbPeriode({ id: 'bulanLalu' }, new Date('2026-12-05T10:00:00+07:00'));
ok('3: 5 Des: Bulan lalu = November penuh vs Oktober penuh (utuh → dibandingkan)', PBL.dari === '2026-11-01' && PBL.banding.ada && PBL.banding.omzet === 3900000 && PBL.omzet === 3250000, J([PBL.dari, PBL.banding, PBL.omzet]));
ok('3: Tahun ini = tahun buku 1 Jan – hari ini; laba bersih = Σ kendaliBulan bulan yang tercatat (Sep–Nov), tahun lalu belum tercatat → disebut', P.tahun.dari === '2026-01-01' && P.tahun.laba.bulan.map(function (x) { return x.key; }).join() === '2026-09,2026-10,2026-11' && dekat(P.tahun.laba.labaBersih, KS9.labaBersih + KO.labaBersih + KB.labaBersih, 0.5) && !P.tahun.banding.ada && /catatan toko baru mulai/.test(P.tahun.ket), J([P.tahun.laba, P.tahun.banding, P.tahun.ket]));
ok('3: Pilih tanggal 4–11 Nov = Rp1.950.000 · 2 nota; pembanding 8 hari sebelumnya; laba bersih tidak dihitung (disebut)', P.pilih.dari === '2026-11-04' && P.pilih.omzet === 1950000 && P.pilih.nota === 2 && P.pilih.banding.nama === '8 hari sebelumnya' && P.pilih.laba === null && !!P.pilih.labaKet, J([P.pilih.omzet, P.pilih.banding.nama, P.pilih.labaKet]));
var PT = [dbPeriode({ id: 'pilih', dari: '', sampai: '' }, KINI), dbPeriode({ id: 'pilih', dari: '2026-11-11', sampai: '2026-11-04' }, KINI), dbPeriode({ id: 'pilih', dari: '2026-11-11', sampai: '2026-11-30' }, KINI)];
ok('3: Pilih tanggal ditolak berkalimat: kosong · awal sesudah akhir · akhir sesudah hari ini', PT.every(function (x) { return !!x.tolak; }) && /tukar/.test(PT[1].tolak) && /belum terjadi/.test(PT[2].tolak), J(PT.map(function (x) { return x.tolak; })));
ok('3: tiap pilihan membawa tujuan ke Laporan', DB_PERIODE.every(function (x) { return P[x[0]].tujuan && P[x[0]].tujuan.ke === 'laporan'; }));

// ==================== 4 · B109 cap data ====================
var c1 = dbCapData({ jenis: 'firestore', masuk: true, hidup: true }, KINI), c2 = dbCapData({ jenis: 'firestore', masuk: true, hidup: false, putus: new Date('2026-11-18T13:20:00+07:00').getTime() }, KINI),
    c3 = dbCapData({ jenis: 'firestore', masuk: true, hidup: false, tersimpan: new Date('2026-11-17T20:05:00+07:00').getTime() }, KINI), c4 = dbCapData({ jenis: 'cadangan', keterangan: 'cadangan contoh' }, KINI),
    c5 = dbCapData({ jenis: 'firestore', masuk: true, hidup: false }, KINI), c6 = dbCapData({ jenis: 'firestore', masuk: true, memuat: true }, KINI), c7 = dbCapData({ jenis: '' }, KINI);
ok('4: tersambung = "data per 14.00" (jam sekarang), tidak awas', c1.teks === 'data per 14.00' && !c1.awas && c1.hidup, J(c1));
ok('4: tanpa internet = jam terakhir tersambung + "tanpa internet", awas', c2.teks === 'data per 13.20 · tanpa internet' && c2.awas, J(c2));
ok('4: dibuka tanpa internet = jam tersambung terakhir yang diingat perangkat, hari lain disebut harinya', c3.teks === 'data per Selasa 17 Nov 20.05 · tanpa internet' && c3.awas, J(c3));
ok('4: cadangan = saat cadangan diunduh; tanpa jam tersambung sama sekali = disebut, tidak ditebak; memuat; belum masuk', /^data cadangan · 18 Nov 14\.00$/.test(c4.teks) && c5.teks === 'data dari simpanan perangkat' && c5.awas && c6.teks === 'memuat data…' && c7.awas, J([c4, c5, c6, c7]));

// ==================== 5 · B127 stok minimum ====================
var sh = [null, { id: 'belanja', ambangHari: 9 }, { id: 'belanja', ambangHari: 99 }, { id: 'belanja', ambangHari: null }, { id: 'belanja', ambangHari: '' }, { id: 'belanja', ambangHari: '5' }, { id: 'belanja' }];
var samaBawaan = sh.map(function (d) { aturDengan(d ? [d] : []); return [smHariBawaan(), aturBelanja().ambangHari]; });
ok('5: bawaan stok minimum = Belanja ambangHari dengan aturan baca yang SAMA (kosong/null/rusak/teks/tanpa dokumen)', samaBawaan.every(function (x) { return x[0] === x[1]; }), J(samaBawaan));
aturDengan([]);
var pasang = [[0, 3], [-5, 3], [3, 0], [7, 1], [7.999, 1], [13.5, 2], [100, 7], [0.001, 3]];
ok('5: hari tersisa = hariHabis Belanja (tanpa laju null · 0/minus yang laku = 0 · dibulatkan ke bawah)', pasang.every(function (x) { return smHari(x[0], x[1]) === hariHabis(x[0], x[1]); }) && smHari(5, 0) === null && hariHabis(5, 0) === null, J(pasang.map(function (x) { return [smHari(x[0], x[1]), hariHabis(x[0], x[1])]; })));
var DB0 = daftarBarang(); var SM0 = dbStokMin(KINI);
ok('5: Dasbor = Perlu perhatian (penghitung sama): daftar & jumlah sama', (function () { var Pp = susunPerhatian().find(function (x) { return /stok minimum/.test(x.teks); }); return SM0.n === 0 ? !Pp : !!Pp && Pp.nilai === SM0.n + ' barang' && Pp.teks.indexOf(SM0.daftar[0].nama) >= 0; })(), J([SM0.n, SM0.daftar.map(function (x) { return x.nama; }), susunPerhatian()]));
var SX = smBawahDari([{ jenis: 'karung', kunci: 'Lambat', nama: 'Lambat', sisa: 100, laju: 50 }, { jenis: 'karung', kunci: 'Minus', nama: 'Minus', sisa: -2, laju: 0 }, { jenis: 'karung', kunci: 'W1', nama: 'W1', sisa: -1, laju: 3, wadahStok: true },
  { jenis: 'kemasan', kunci: 'K5', nama: 'Kemas 5 kg', sisa: 3, laju: 1 }, { jenis: 'karung', kunci: 'Diam', nama: 'Diam', sisa: 40, laju: 0 }, { jenis: 'karung', kunci: 'Nol', nama: 'Nol', sisa: 0, laju: 0 }], {}, 7);
ok('5: buku minus selalu di bawah minimum & paling depan; buku wadah tidak dicek; tanpa laju tidak ditebak; kemasan ikut (bungkus)', SX.daftar.map(function (x) { return x.nama; }).join() === 'Minus,Lambat,Kemas 5 kg' && SX.dicek === 4 && SX.daftar[2].satuan === 'bungkus' && /MINUS/.test(SX.daftar[0].kata), J(SX));
var ang = DB0.find(function (b) { return b.jenis === 'karung' && b.kunci === 'Angsa'; }); var kem = DB0.find(function (b) { return b.jenis === 'karung' && b.kunci === 'Kembang'; });
var hA = smHari(ang.sisa, ang.laju), hK = smHari(kem.sisa, kem.laju);
ok('5: bawaan 7 hari: Angsa ' + hA + ' hari & Kembang ' + hK + ' hari menurut laju — ikut daftar hanya kalau ≤ 7', SM0.daftar.some(function (x) { return x.nama === 'Angsa'; }) === (hA !== null && hA <= 7) && SM0.daftar.some(function (x) { return x.nama === 'Kembang'; }) === (hK !== null && hK <= 7), J([hA, hK, ang, kem]));
aturDengan([{ id: 'stokMinimum', barang: { 'karung|Angsa': { min: Math.ceil(ang.sisa) + 1 }, 'karung|Kembang': { hari: hK }, 'karung|Rusak': { hari: 999 }, 'karung|X': { min: -1 } } }]);
var SM1 = dbStokMin(KINI); var PE = smPeta();
ok('5: per barang: Angsa minimum kg (sisa < minimum → di bawah) · Kembang hari = hari tersisanya (≤ → di bawah); isian rusak dibuang', SM1.daftar.some(function (x) { return x.nama === 'Angsa' && x.cek.kenapa === 'jumlah'; }) && SM1.daftar.some(function (x) { return x.nama === 'Kembang' && x.cek.kenapa === 'hari'; }) && !PE['karung|Rusak'] && !PE['karung|X'] && SM1.nSendiri === 2, J([SM1.daftar, PE]));
var DS1 = dbStok(KINI);
ok('5: kartu Stok per merek memakai batas yang sama (awas = di bawah stok minimum)', DS1.merek.filter(function (m) { return m.awas; }).map(function (m) { return m.nama; }).sort().join() === SM1.daftar.filter(function (x) { return x.jenis === 'karung'; }).map(function (x) { return x.nama; }).sort().join(), J(DS1.merek));
var Pp1 = susunPerhatian().find(function (x) { return /stok minimum/.test(x.teks); });
ok('5: Perlu perhatian ikut angka per barang', !!Pp1 && Pp1.nilai === SM1.n + ' barang', J(Pp1));
var sa = susunAturStokMinimum({ 'karung|Angsa': { cara: 'min', n: '1.250' }, 'karung|Kembang': { cara: 'hari', n: '5' }, 'kemasan|K': { cara: 'bawaan', n: '9' } }, W);
var sb = [susunAturStokMinimum({ 'karung|Angsa': { cara: 'hari', n: '61' } }, W), susunAturStokMinimum({ 'karung|Angsa': { cara: 'hari', n: '2,5' } }, W), susunAturStokMinimum({ 'karung|Angsa': { cara: 'min', n: '0' } }, W), susunAturStokMinimum({ 'lain|Q': { cara: 'hari', n: '3' } }, W)];
ok('5: simpan: satu dokumen aturanToko/stokMinimum; "ikut bawaan" tidak disimpan; 1.250 = seribu dua ratus lima puluh', !sa.tolak && sa.dokumen.length === 1 && sa.dokumen[0].koleksi === 'aturanToko' && sa.dokumen[0].data.id === 'stokMinimum' && sa.dokumen[0].data.barang['karung|Angsa'].min === 1250 && sa.dokumen[0].data.barang['karung|Kembang'].hari === 5 && !sa.dokumen[0].data.barang['kemasan|K'], J(sa));
ok('5: simpan ditolak berkalimat: hari > 60 · hari pecahan · minimum 0 · barang tak dikenal', sb.every(function (x) { return !!x.tolak; }), J(sb.map(function (x) { return x.tolak; })));
// Belanja: tanpa angka per barang = sama persis; Kembang diberi batas hari tinggi → disarankan
aturDengan([]); var BL0 = hitungBelanja({}, KINI); var k0 = BL0.baris.find(function (b) { return b.merk === 'Kembang'; });
ok('5: Belanja tanpa angka per barang: atur kelompok = atur umum (objek yang sama), judul lama', smAturKelompok(aturBelanja(), [{ merk: 'Kembang', laju: 1 }], {}) === aturBelanja() || J(smAturKelompok(aturBelanja(), [{ merk: 'Kembang', laju: 1 }], {})) === J(aturBelanja()), '');
aturDengan([{ id: 'stokMinimum', barang: { 'karung|Kembang': { hari: 60 } } }]); var BL1 = hitungBelanja({}, KINI); var k1 = BL1.baris.find(function (b) { return b.merk === 'Kembang'; });
ok('5: Belanja: Kembang batas 60 hari → masuk "Di bawah stok minimum" & disarankan (dulu: aman ≤ 7 hari)', !!k1 && k1.hari !== null && k1.hari <= 60 && k1.perlu === (k1.saranK > 0) && BL1.kelompok.some(function (g) { return /Di bawah stok minimum/.test(g.judul) && g.isi.some(function (b) { return b.merk === 'Kembang'; }); }), J([k0 && { hari: k0.hari, perlu: k0.perlu }, k1 && { hari: k1.hari, perlu: k1.perlu, saranK: k1.saranK }, BL1.kelompok.map(function (g) { return g.judul; })]));
aturDengan([]);

// ==================== 6 · B113 enam bulan ====================
var E = dbEnam(KINI); var TB = trenBiaya(KINI, 6); var PK = pdKekayaan(KINI);
ok('6: enam bulan laba bersih & biaya = Laporan › Biaya trenBiaya (sama per bulan)', E.bulan.length === 6 && E.bulan.every(function (b, i) { return b.labaBersih === TB.daftar[i].labaBersih && b.semuaBiaya === TB.daftar[i].semuaBiaya && b.key === TB.daftar[i].key; }) && E.bulan[5].key === '2026-11', J(E.bulan.map(function (b) { return [b.key, b.labaBersih]; })));
ok('6: laba bersih bulan berjalan di enam bulan = kartu Bulan ini (kendaliBulan)', !!E.bulan[5] && E.bulan[5].labaBersih === KB.labaBersih);
var NK = neracaPada(null, KINI).N; var PB = E.posisi[E.posisi.length - 1];
ok('6: posisi bulan berjalan = neraca sekarang (kas 4 tempat · piutang · nilai stok)', PB.berjalan && PB.ada && PB.kas === NK.kas && PB.piutang === NK.piutang && PB.stok === NK.stok && NK.kas !== 0, J([PB, NK.kas, NK.piutang, NK.stok]));
ok('6: posisi akhir bulan = Pondasi pdKekayaan (kas · piutang · stok per bulan, terlama dulu)', E.posisi.length === Math.min(6, PK.bulan.length) && E.posisi[E.posisi.length - 1].key === PK.bulan[0].key && E.posisi.every(function (p) { var q = PK.bulan.find(function (x) { return x.key === p.key; }); return q && (!q.ada || (p.kas === q.kas && p.piutang === q.piutang && p.stok === q.stok)); }), J([E.posisi, PK.bulan.slice(0, 3)]));

// ==================== 7 · B88/B89 widget ====================
var SD = dbTambahan(susunDasbor(KINI, 'hari'), KINI);
ok('7: susunDasbor + dbTambahan memuat banding · stokMin · enam tanpa galat', SD.banding && !SD.banding.galat && SD.stokMin && !SD.stokMin.galat && SD.enam && !SD.enam.galat, J([SD.banding && SD.banding.galat, SD.stokMin && SD.stokMin.galat, SD.enam && SD.enam.galat]));
var A0 = wgAtur();
ok('7: belum pernah diatur = BAWAAN = urutan kartu lama (owner: "Tampilan saat ini yang paling penting"), lebar 6/12 (Tren 12/12), tinggi otomatis',
  !A0.dariOwner && A0.daftar.map(function (w) { return w.id; }).join() === 'kHari,kKpi,kTren,kBulan,kWadah,kPemicu,kTagihan,kStok,kMutu,kPondasi,kB2b' && A0.daftar.every(function (w) { return w.h === null && w.w === (w.id === 'kTren' ? 12 : 6); }), J(A0));
ok('7: Perlu perhatian disembunyikan; tambahan (Ringkas hari ini, Periode, Enam bulan, Perlu perhatian, angka utama) ada di katalog, bukan di bawaan', ['kPerhatian', 'kHeadline', 'kPeriode', 'kEnam', 'omzetHari', 'uangToko'].every(function (id) { return wgBelumDipasang(A0.daftar).some(function (k) { return k.id === id; }); }));
aturDengan([{ id: 'dasbor', widget: [] }]);
ok('7: daftar KOSONG yang disimpan owner = kosong', wgAtur().daftar.length === 0 && wgAtur().dariOwner);
aturDengan([{ id: 'dasbor', widget: [{ id: 'uangToko', w: 4, h: 30 }, { id: 'hantu' }, { id: 'uangToko' }, { id: 'kHari', w: 99, h: 5 }, { id: 'kStok', w: 1.6, h: 'x' }, { id: 'susut', ukuran: 'besar' }, { id: 'kTren', ukuran: 'penuh', h: 9999 }] }]);
ok('7: susunan rusak dibersihkan: id tak dikenal & kembar dibuang; lebar dijepit 3–12 (angka 2–12) & dibulatkan; tinggi dijepit 10–250 baris (rusak = otomatis); ukuran lama kecil/lebar/besar/penuh dibaca',
  J(wgAtur().daftar) === J([{ id: 'uangToko', w: 4, h: 30 }, { id: 'kHari', w: 12, h: 10 }, { id: 'kStok', w: 3, h: null }, { id: 'susut', w: 6, h: null }, { id: 'kTren', w: 12, h: 250 }]), J(wgAtur().daftar));
aturDengan([]);
var d = A0.daftar; var d1 = wgPindah(d, 0, 3), d2 = wgHapus(d, 1), d3 = wgTambah(d, 'kHeadline'), d4 = wgTambah(d, 'kHari'), d5 = wgUkur(d, 0, 8, 40), d6 = wgUkur(d5, 0, undefined, 3), d7 = wgTinggiOtomatis(d5, 0), d8 = wgUkur(d, 0, 0, undefined), d9 = wgTambah(d, 'omzetHari');
ok('7: pindah · hapus · tambah (sekali saja, lebar bawaan) · tarik lebar & tinggi (dijepit) · tinggi otomatis', d1[3].id === 'kHari' && d1.length === 11 && d2.length === 10 && d2[1].id === 'kTren' && d3.length === 12 && d3[11].id === 'kHeadline' && d3[11].w === 12 && d4.length === 11
  && d5[0].w === 8 && d5[0].h === 40 && d6[0].w === 8 && d6[0].h === 10 && d7[0].h === null && d7[0].w === 8 && d8[0].w === 3 && d9[11].w === 6 && d[0].w === 6 && d[0].h === null, J([d5[0], d6[0], d7[0], d8[0], d9[11]]));
ok('7: katalog "+ Tambah" = yang belum dipasang, berjenis (kartu Dasbor · kartu tambahan · angka)', wgBelumDipasang(d).length === WG_KATALOG.length - 11 && !wgBelumDipasang(d).some(function (x) { return x.id === 'kHari'; }) && wgBelumDipasang(d2).some(function (x) { return x.id === 'kKpi' && x.jenis === 'lama'; }) && wgBelumDipasang(d).some(function (x) { return x.jenis === 'angka'; }));
var sv = susunAturDasbor(d3, W); var sv2 = susunAturDasbor([{ id: 'hantu', ukuran: 'kecil' }], W);
ok('7: simpan = SATU dokumen aturanToko/dasbor { widget }; susunan tak dikenal ditolak', !sv.tolak && sv.dokumen.length === 1 && sv.dokumen[0].koleksi === 'aturanToko' && sv.dokumen[0].data.id === 'dasbor' && sv.dokumen[0].data.widget.length === 12 && sv.dokumen[0].data.widget[0].w === 6 && sv.dokumen[0].data.widget[0].h === null && !!sv2.tolak, J([sv, sv2]));
var PERH = [{ teks: 'Bon belum lunas · 2 nama', nilai: 'Rp10.000', awas: false }, { teks: 'Di bawah stok minimum: Contoh', nilai: '1 barang', awas: true }];
var semua = wgSusun(WG_KATALOG.map(function (k) { return { id: k.id, ukuran: k.ukuran }; }), Object.assign({}, SD, { perhatian: PERH })); var by = {}; semua.forEach(function (w) { by[w.id] = w; });
ok('7: semua ' + WG_KATALOG.length + ' kartu & widget tersusun dari hasil dasbor tanpa galat (kartu lama digambar layar)', semua.length === WG_KATALOG.length && semua.every(function (w) { return w.khusus || w.jenis === 'lama' || (w.nilai && w.nilai !== 'gagal dihitung'); }), J(semua.filter(function (w) { return w.nilai === 'gagal dihitung'; })));
ok('7: widget-KARTU tambahan menutup ke kelompoknya: Enam bulan = laba bersih bulan berjalan (trenBiaya) · Perlu perhatian = daftar Ringkasan (yang merah didahulukan)',
  !!SD.enam.bulan[5] && by.kEnam.nilai === RP(SD.enam.bulan[5].labaBersih) && by.kEnam.tren.length === 6 && by.kPerhatian.nilai === '2 hal' && by.kPerhatian.baris[0][0] === 'Di bawah stok minimum: Contoh' && by.kHeadline.khusus && by.kPeriode.khusus, J([by.kEnam, by.kPerhatian]));
ok('7: kotak pasir membedakan: brankas berisi & laba sebulan ≠ sampai hari ini (widget yang salah ambil ketahuan)', SD.hari.kas.tempat.find(function (t) { return t.id === 'brankas'; }).n > 0 && SD.bulan.labaBersih !== SD.bulan.impas.labaSampai, J([SD.hari.kas.tempat, SD.bulan.labaBersih, SD.bulan.impas.labaSampai]));
ok('7: widget MENUTUP ke kartunya: omzet = Laporan Harian · laba kotor · uang toko 4 tempat · laba bersih s.d. hari ini · biaya · piutang lewat · bon pemasok · stok minimum',
  by.omzetHari.nilai === RP(SD.hari.omzet) && SD.banding.omzet === SD.hari.omzet && by.labaKotorHari.nilai === RP(SD.hari.margin) && by.uangToko.nilai === RP(SD.hari.kas.total)
  && by.labaBersihBulan.nilai === RP(SD.bulan.impas.labaSampai) && by.biayaBulan.nilai === RP(SD.bulan.semuaBiaya) && by.piutangLewat.nilai === RP(SD.tagihan.piutang.nota.lewat)
  && by.bonPemasok.nilai === RP(SD.tagihan.pemasok.rpLewat + SD.tagihan.pemasok.rpDekat) && by.stokMinimum.nilai === (SD.stokMin.n ? SD.stokMin.n + ' barang' : 'aman'), J([by.omzetHari.nilai, by.uangToko.nilai, by.labaBersihBulan.nilai, by.stokMinimum.nilai]));
ok('7: omzet & rata bulan ini = banding bulan; laba bersih 6 bulan = enam bulan; tiap widget punya tujuan', by.omzetBulan.nilai === RP(M.ini.omzet) && by.rataBulan.nilai === RP(Math.round(M.ini.rata)) && !!SD.enam.bulan[5] && by.labaEnam.nilai === RP(SD.enam.bulan[5].labaBersih) && semua.every(function (w) { return !!w.tujuan || w.khusus || w.jenis === 'lama' || w.id === 'kPerhatian'; }), J(semua.filter(function (w) { return !w.tujuan; }).map(function (w) { return w.id; })));
var rusak = wgSusun([{ id: 'omzetHari', ukuran: 'lebar' }, { id: 'uangToko', ukuran: 'kecil' }], { banding: { galat: 'contoh rusak' }, hari: SD.hari });
ok('7: kelompok galat = widget itu berkalimat, widget lain tetap', rusak[0].nilai === 'gagal dihitung' && rusak[0].awas && rusak[1].nilai === RP(SD.hari.kas.total), J(rusak));

// ==================== 8 · B91 headline ====================
var perh = [{ teks: 'Bon belum lunas · 2 nama', nilai: 'Rp10.000', awas: false }, { teks: 'Di bawah stok minimum: Wadah Contoh', nilai: '1 barang', awas: true }];
var Hd = dbHeadline(SD, perh); var Hd0 = dbHeadline(SD, []);
ok('8: headline = omzet vs kemarin jam segini · laba bersih bulan ini vs titik impas · hal mendesak (yang awas didahulukan)', /^Omzet hari ini Rp650\.000, naik 150% dari kemarin jam segini · laba bersih November sampai hari ini /.test(Hd.teks) && /2 hal perlu perhatian, paling mendesak: Di bawah stok minimum: Wadah Contoh \(1 barang\)\.$/.test(Hd.teks) && Hd.bagian.length === 3, Hd.teks);
ok('8: laba di bawah impas disebut angkanya (titikImpas.kurang); tanpa perhatian = "tidak ada yang perlu perhatian"', (SD.bulan.impas.menutup ? /biaya sudah tertutup/.test(Hd.teks) : Hd.teks.indexOf('biaya masih ' + RP(SD.bulan.impas.kurang) + ' lebih besar dari margin kotor (belum impas)') >= 0) && /tidak ada yang perlu perhatian\.$/.test(Hd0.teks), Hd.teks + ' | ' + Hd0.teks);
var Hk = dbHeadline({ banding: { omzet: 100000, kemarin: { ada: true, omzet: 200000, pct: -50 }, tujuan: {} } }, []);
var Hz = dbHeadline({ banding: { omzet: 0, kemarin: { ada: true, omzet: 0, pct: null }, tujuan: {} } }, []);
ok('8: turun disebut "turun"; kemarin jam segini kosong disebut, bukan "naik ∞ %"', /turun 50% dari kemarin jam segini/.test(Hk.teks) && Hk.bagian[0].awas && /kemarin jam segini juga belum ada jualan/.test(Hz.teks), Hk.teks + ' | ' + Hz.teks);

print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

STATIS = [
    ('kisi panel berpegangan (mode atur: tekan lama, seret = pindah, tarik kanan/bawah/sudut = ukuran, tinggi otomatis diukur, hapus, tambah, simpan)', 'kisi', ['wgSusun(', 'wgPindah(', 'wgHapus(', 'wgUkur(', 'wgTinggiOtomatis(', 'wgTambah(', 'simpanWidget(', 'TEKAN_LAMA', 'setPointerCapture', 'data-pn-tarik="w"', 'data-pn-tarik="h"', 'data-pn-tarik="wh"', 'ResizeObserver', 'opsi.kartuPenuh(']),
    ('headline & saringan tanggal sebagai widget khusus + cap data', 'kisi', ['dbHeadline(', 'dbPeriode(', 'DB_PERIODE', 'db-cap']),
    ('Ringkasan menulis susunan widget & memberi cap tiap menit', 'ringkasan', ['dbTambahan(', 'susunAturDasbor(', 'tulisDokumen(', 'dbCapData(']),
    ('headline: bagian Perlu perhatian menggulir ke panelnya, atau menyebut bahwa ia disembunyikan', 'kisi', ["akar.querySelector('.pn[data-pn=\"kPerhatian\"]')", "Perlu perhatian disembunyikan dari Dasbor"]),
    ('Dasbor = kartu lama UTUH sebagai panel (kartuPenuh) di kisi · cap per kartu · Enam bulan · stok minimum', 'dasbor', ['pasangKisi(', 'akar.innerHTML = kisi.html(D, perhatianKini, capKini)', 'kHari: () => kartuHari(D.hari)', 'kartuPenuh(', 'db-cap', 'kartuEnam(', 'smTujuan']),
    ('app.js memberi Ringkasan keadaan data (cap)', 'app', ['dataPer:']),
    ('firebase.js mencatat jam terakhir tersambung', 'fb', ['dataPer', 'miqbal_baru_terakhir_tersambung']),
    ('Stok: lembar stok minimum per barang', 'stok', ['stokMin', 'kartuStokMinimum(']),
    ('CSS kisi 12 kolom × baris 8 px merapat (dense), panel tinggi tarikan digulir di dalam, HP satu kolom tanpa ukuran tarikan, pegangan kanan/bawah/sudut; mode Dasbor: samping tersembunyi & selebar layar', 'css', ['grid-template-columns: repeat(12, minmax(0, 1fr)); grid-auto-rows: 8px; grid-auto-flow: row dense;', '.pn.pn-tetap > :first-child { height: 100%; box-sizing: border-box; overflow: auto;', 'grid-column: auto !important; grid-row-end: auto !important;', '.pn-kanan', '.pn-bawah', '.pn-sudut', 'cursor: nwse-resize', 'prefers-reduced-motion', 'main.layar-ringkasan.mode-dasbor > .rk-samping { display: none; }', 'main.layar-ringkasan.mode-dasbor > .rk-dasbor, main.layar-ringkasan.mode-dasbor > .rk-saklar { grid-column: 1 / -1; }']),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_dasbor_sensus.py && python3 alat-uji/uji_dasbor_sensus.py --kontrol']),
    ('BACA-DULU menyebut paket ini', 'baca', ['dasbor-widget-logika.js', 'stok-minimum-logika.js', 'aturanToko/dasbor', 'aturanToko/stokMinimum']),
    ('bundel jsc memuat stok minimum otomatis', 'bundel', ["SM_MODUL = 'baru/js/layar/stok-minimum-logika.js'"]),
    ('riwayat setelan menamai dua dokumen baru', 'rs', ["dasbor: 'Susunan Dasbor'", "stokMinimum: 'Stok minimum'"]),
]
RUSAK = [
    ('kemarin dibanding sehari penuh (bukan jam segini)', DL, "const X = rkJamSegini(ix, t, menit);", "const X = rkJamSegini(ix, t, null);"),
    ('minggu lalu = kemarin', DL, "const kmr = ugTambahHari(iso, -1), mg = ugTambahHari(iso, -7);", "const kmr = ugTambahHari(iso, -1), mg = ugTambahHari(iso, -1);"),
    ('jam segini tanpa batas menit (nota sesudah jam sekarang ikut)', RK, "const R = rkJumlahRentang(ix, iso, iso, menit == null ? undefined : menit);", "const R = rkJumlahRentang(ix, iso, iso);"),
    ('rata-rata nota dibagi nota + 1', LPL, "rata: R.nota > 0 ? R.omzetPenuh / R.nota : null,", "rata: R.nota > 0 ? R.omzetPenuh / (R.nota + 1) : null,"),
    ('bulan lalu sampai akhir bulan (bukan tanggal yang sama)', DL, "const sampaiL = kL + '-' + iso.slice(8, 10) > akhirL ? akhirL : kL + '-' + iso.slice(8, 10);", "const sampaiL = akhirL;"),
    ('Tahun ini tanpa bulan sebelum hari ini', DL, "for (let m = 1; m <= Number(key.slice(5, 7)); m++) bulan.push(t + '-' + dbP2(m));", "bulan.push(key);"),
    ('pilih tanggal menerima tanggal yang belum terjadi', DL, "if (sampai > iso) return { id, nama, tolak:", "if (false) return { id, nama, tolak:"),
    ('cap tersambung tetap jam lama', DL, "if (I.hidup) return { teks: 'data per ' + dbJamTeks(k),", "if (I.hidup) return { teks: 'data per ' + dbJamTeks(new Date(Number(I.putus) || 0)),"),
    ('cap tanpa internet tanpa kata awas', DL, "return { teks: 'data per ' + kapan + ' · tanpa internet', awas: true,", "return { teks: 'data per ' + kapan, awas: false,"),
    ('stok minimum bawaan konstanta 4 hari', SM, "return a && isFinite(v) && v >= 0 && v <= SM_HARI_MAKS ? v : SM_HARI_BAWAAN; }", "return 4; }"),
    ('hari tersisa tidak dibulatkan seperti Belanja', SM, "export const smHari = (sisa, laju) => (!(laju > 0) ? null : !(sisa > 0) ? 0 : Math.floor(sisa / laju + 1e-9));", "export const smHari = (sisa, laju) => (!(laju > 0) ? null : sisa / laju);"),
    ('minimum jumlah per barang diabaikan', SM, "if (x && x.min !== undefined) return { hari: null, min: x.min,", "if (false) return { hari: null, min: x.min,"),
    ('buku minus tidak dihitung di bawah minimum', SM, "const kenapa = minus ? 'minus' :", "const kenapa = false ? 'minus' :"),
    ('Perlu perhatian memakai penghitung sendiri (≤ 4 hari)', RK, "const SM = smBawahDari(baris);", "const SM = smBawahDari(baris, {}, 4);"),
    ('kartu Stok per merek kembali ke konstanta', DL, "return { nama: b.nama, kg: b.sisa, laju: b.laju, hari: b.hariHabis, minus: b.sisa < 0, awas: C.bawah,", "return { nama: b.nama, kg: b.sisa, laju: b.laju, hari: b.hariHabis, minus: b.sisa < 0, awas: b.sisa < 0,"),
    ('Belanja mengabaikan stok minimum per barang', BL, "const atur = smAturKelompok(aturUmum, G.isi, smP);", "const atur = aturUmum;"),
    ('posisi enam bulan tanpa kas', PDL, "kas: (N.N || {}).kas, piutang:", "kas: 0, piutang:"),
    ('enam bulan memakai 5 bulan', DL, "const B = trenBiaya(kini, 6);", "const B = trenBiaya(kini, 5);"),
    ('daftar kosong milik owner diganti bawaan', WG, "const milik = !!d && Array.isArray(d.widget);", "const milik = !!d && Array.isArray(d.widget) && d.widget.length > 0;"),
    ('widget kembar tidak dibuang', WG, "if (!K || lihat[K.id] || out.length >= WG_MAKS) return;", "if (!K || out.length >= WG_MAKS) return;"),
    ('widget uang toko memakai laci saja', WG, "return { nilai: RP(K.total), ket: K.tempat.filter(", "return { nilai: RP((K.tempat[0] || {}).n), ket: K.tempat.filter("),
    ('widget laba bersih memakai sebulan penuh (bukan sampai hari ini)', WG, "return { nilai: RP(I.labaSampai), ket: 'sampai hari ini · '", "return { nilai: RP(B.labaBersih), ket: 'sampai hari ini · '"),
    ('bawaan bukan urutan kartu lama', WG, "export const WG_BAWAAN = ['kHari', 'kKpi', 'kTren',", "export const WG_BAWAAN = ['kKpi', 'kHari', 'kTren',"),
    ('lebar tidak dijepit', WG, "return { id: K.id, w: Math.max(K.minW, Math.min(WG_KOLOM, lebar)), h: tinggi };", "return { id: K.id, w: lebar, h: tinggi };"),
    ('tinggi tidak dijepit', WG, "const tinggi = hh === null || !isFinite(hh) ? null : Math.max(WG_H_MIN, Math.min(WG_H_MAKS, hh));", "const tinggi = hh === null || !isFinite(hh) ? null : hh;"),
    ('tinggi otomatis tidak mengembalikan ke isi', WG, "export function wgTinggiOtomatis(daftar, i) { return daftar.map((x, n) => (n !== i ? x : { id: x.id, w: x.w, h: null })); }", "export function wgTinggiOtomatis(daftar, i) { return daftar.slice(); }"),
    ('Perlu perhatian: yang merah tidak didahulukan', WG, "baris: P.slice().sort((a, b) => (b.awas ? 1 : 0) - (a.awas ? 1 : 0)).slice(0, 4)", "baris: P.slice(0, 4)"),
    ('headline turun ditulis naik', DL, "(K.pct > 0 ? 'naik ' : 'turun ')", "('naik ')"),
    ('headline paling mendesak = yang pertama, bukan yang awas', DL, "const top = P.find((x) => x.awas) || P[0];", "const top = P[0];"),
]
RUSAK_STATIS = [
    ('widget tanpa tekan lama', 'kisi', 'TEKAN_LAMA', 'TAHAN_X'),
    ('Dasbor kembali ke kartu tetap (tanpa kisi)', 'dasbor', 'pasangKisi(', 'pasangKisiX('),
    ('HP memakai ukuran tarikan Mac', 'css', 'grid-column: auto !important; grid-row-end: auto !important;', ''),
    ('tanpa pegangan sudut', 'kisi', 'data-pn-tarik="wh"', 'data-pn-x="wh"'),
    ('Ringkasan tanpa dbTambahan', 'ringkasan', 'dbTambahan(', 'dbTambahanX('),
    ('firebase tanpa jam tersambung', 'fb', 'miqbal_baru_terakhir_tersambung', 'miqbal_baru_x'),
    ('Perlu perhatian tampil lagi di samping mode Dasbor', 'css', 'main.layar-ringkasan.mode-dasbor > .rk-samping { display: none; }', ''),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_dasbor_sensus.py && python3 alat-uji/uji_dasbor_sensus.py --kontrol', 'true'),
]
BON_PEMASOK_LAMA = uji_ringkasan_baru.BON_PEMASOK_LAMA

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, galat: [], ms: {} };
var aman = function (nama, f) { var t0 = Date.now(); try { var x = f(); out.ms[nama] = Date.now() - t0; return x; } catch (e) { out.galat.push(nama + ': ' + e); return null; } };
var B = aman('banding', function () { return dbBanding(kini); }); var R = aman('rekapHari', function () { return rekapHari(iso); });
out.banding = B && R ? { sama: B.omzet === R.omzet && (!B.cincin || B.cincin.omzet === R.omzet), kemarin: B.kemarin.ada, minggu: B.mingguLalu.ada, nota: B.nota, bulanLalu: B.bulan.lalu.ada } : null;
var SM = aman('stokMin', function () { return dbStokMin(kini); }); var PP = aman('perhatian', function () { return susunPerhatian(); });
out.stokMin = SM && PP ? { n: SM.n, dicek: SM.dicek, sama: SM.n === 0 ? !PP.some(function (x) { return /stok minimum/.test(x.teks); }) : PP.some(function (x) { return x.nilai === SM.n + ' barang'; }) } : null;
var E = aman('enam', function () { return dbEnam(kini); }); out.enam = E ? { bulan: E.bulan.length, posisi: E.posisi.filter(function (p) { return p.ada; }).length, galat: E.galatPosisi } : null;
out.periode = {}; DB_PERIODE.forEach(function (x) { if (x[0] === 'pilih') return; var P = aman('periode ' + x[0], function () { return dbPeriode({ id: x[0] }, kini); }); out.periode[x[0]] = P ? !P.tolak : false; });
var SD = aman('susun', function () { return dbTambahan(susunDasbor(kini, 'hari'), kini); });
var WS = SD ? aman('widget', function () { return wgSusun(WG_KATALOG.map(function (k) { return { id: k.id, ukuran: k.ukuran }; }), SD); }) : null;
out.widget = WS ? { n: WS.length, galat: WS.filter(function (w) { return w.nilai === 'gagal dihitung'; }).map(function (w) { return w.id + ': ' + w.ket; }) } : null;
var H = SD && PP ? aman('headline', function () { return dbHeadline(SD, PP); }) : null; out.headline = H ? H.bagian.length : 0;
print(JSON.stringify(out));
"""


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


def jalan(teks):
    jam = "var __KINI = new Date('2026-11-18T14:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    r, out = jsc(jam + bundel_js(teks) + '\nvar KOTAK0 = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar GK = ' + json.dumps(KOTAK) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + SKENARIO)
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], list(h['gagal'])


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    for k in ('wg', 'sm'):
        if 'document.' in src[k] or 'tulisDokumen' in src[k] or 'window.' in src[k]: g.append(k + ': modul logika menyentuh DOM / menulis langsung')
    for k, idd in (('wg', 'dasbor'), ('sm', 'stokMinimum')):
        if src[k].count("koleksi: 'aturanToko'") != 1 or 'koleksi:' in src[k].replace("koleksi: 'aturanToko'", ''): g.append(k + ': menulis selain setelan aturanToko/' + idd)
    imp = [l for l in src['sm'].split('\n') if l.startswith('import ')]
    if any("'../data/toko.js'" not in l and "'../inti/format.js'" not in l for l in imp): g.append('stok-minimum-logika bukan modul daun lagi (impor selain data/toko.js & format)')
    if 'firestore.rules' in src['baca'] and 'v23' in src['baca'][src['baca'].find('Paket Dasbor'):src['baca'].find('Paket Dasbor') + 2000]: g.append('BACA-DULU menyebut rules baru untuk paket Dasbor (paket ini tanpa rules)')
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
        r, out = jsc("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP)
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out)
            beres = not h['galat'] and h['banding'] and h['banding']['sama'] and h['stokMin'] and h['stokMin']['sama'] and h['enam'] and all(h['periode'].values()) and h['widget'] and not h['widget']['galat'] and h['headline'] == 3
            # angka rupiah toko TIDAK dicetak (repo publik) — hanya keadaan & jumlah
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: banding tidak menutup ke Laporan, stok minimum Dasbor ≠ Perlu perhatian, periode/widget galat')
    sys.exit(1 if g or gs else 0)
