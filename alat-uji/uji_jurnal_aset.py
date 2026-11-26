#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_jurnal_aset.py — modul ERP no. 70 ASET TETAP & PENYUSUTAN (owner 26 Nov 2026, sensus ulang 26 Nov bagian 2). KOTAK PASIR (nama & angka CONTOH, bukan angka
toko), jsc saja, TANPA peramban. Jam dikunci Minggu 20 Des 2026 10:00 WIB. Angka harapan penyusutan dihitung TERPISAH (Python, rumus garis lurus harian) dan
ditanam sebagai angka.
  AS0 daftar kosong: laba & neraca byte-sama (tanpa kolom baru); isian lama tetap dipakai Neraca sampai daftar punya satu barang.
  AS1 susut harian: hari beli, akhir umur, sesudah umur, nilai sisa; Σ hari = bulan persis; sebelum tanggal mulai (bawaan 1 Des 2026) TIDAK memotong laba.
  AS2 laba: ugLabaBersih = laba mesin ± lebih/kurang kas − penyusutan + uang keluar yang ditunjuk (≤ nominal catatan, di bulan catatannya).
  AS3 neraca: nilai buku per tanggal, isian lama diganti, kekayaan ikut, seimbang, catatan menyebut aset bawaan & penyusutan sebelum mulai.
  AS4 semua identitas laba yang disusun ulang dari bagiannya menutup: Ke mana laba kotor, Kendali biaya, KPI laba usaha, terjun Laba, laba-rugi berkop.
  AS5 tunjuk Uang keluar: hanya biaya toko (bukan ambil pribadi / potongan QRIS), harga ≤ nominal, satu catatan satu aset, tanggal ikut catatan.
  AS6 bulan terkunci: simpan / hapus / ganti tanggal mulai yang menggeser laba bulan terkunci DITOLAK; yang tidak menggeser boleh.
  AS7 isian: nama, jenis, harga bulat, tanggal ≤ hari ini, umur 1–600 (kosong = bawaan jenis), sisa 0..< harga; hapus dua ketukan; dokumen membawa kolom lain.
  ASAP: cadangan toko lokal (bila ada) — tanpa aset byte-sama; dengan aset contoh (menunjuk uang keluar toko terbesar bulan terakhir + barang bawaan) semua
        identitas laba menutup, neraca seimbang, berkop baris terakhir = laba bersih.

    python3 alat-uji/uji_jurnal_aset.py            → N lulus · 0 gagal
    python3 alat-uji/uji_jurnal_aset.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_kpi_laba, uji_kunci_periode, uji_ringkasan_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
AS = 'baru/js/layar/aset-tetap-logika.js'; UG = 'baru/js/layar/uang-logika.js'; LG = 'baru/js/layar/laporan-logika.js'; KB = 'baru/js/layar/kendali-biaya-logika.js'
KL = 'baru/js/layar/kpi-laba-logika.js'
MODUL = bundel_baru.lengkapi(list(dict.fromkeys(uji_kpi_laba.MODUL + [AS])))
SUMBER = {'laporan': 'baru/js/layar/laporan.js', 'panel': 'baru/js/layar/aset-panel.js', 'as': AS, 'index': 'baru/index.html', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md',
          'rules': 'firestore.rules', 'css': 'baru/css/laporan.css', 'peta': 'alat-uji/peta_akses.py', 'bundel': 'alat-uji/bundel_baru.py', 'lg': LG}
JAM = "var __KINI = new Date('2026-12-20T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

KOTAK = {
  'penjualan': [
    {'id': 1001, 'tanggal': '2026-11-20', 'jam': '09:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 50, 'hargaTotal': 1000000, 'hppTotalSaatJual': 900000, 'trxId': 't1'},
    {'id': 1002, 'tanggal': '2026-12-03', 'jam': '10:00', 'caraBayar': 'Tunai', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 100, 'hargaTotal': 2000000, 'hppTotalSaatJual': 1700000, 'trxId': 't2'},
    {'id': 1003, 'tanggal': '2026-12-10', 'jam': '11:00', 'caraBayar': 'QRIS', 'jenis': 'karung', 'merkSumber': 'Angsa', 'totalKg': 25, 'hargaTotal': 500000, 'hppTotalSaatJual': 420000, 'trxId': 'q1'},
  ],
  'pengeluaranHarian': [
    {'id': 3001, 'tanggal': '2026-11-10', 'jam': '12:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Timbangan duduk 150 kg', 'nominal': 1500000, 'dari': 'laci'},
    {'id': 3002, 'tanggal': '2026-12-05', 'jam': '12:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Plastik', 'nominal': 50000, 'dari': 'laci'},
    {'id': 3003, 'tanggal': '2026-12-06', 'jam': '12:00', 'kategori': 'owner', 'keterangan': 'Makan', 'nominal': 200000, 'dari': 'laci'},
    {'id': 'mdr-2026-12-10', 'tanggal': '2026-12-10', 'jam': '21:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Potongan QRIS (MDR)', 'nominal': 3500, 'dari': 'rekening', 'mdr': True},
    {'id': 3005, 'tanggal': '2026-12-07', 'jam': '12:00', 'kategori': 'tokoDompet', 'untuk': 'toko', 'keterangan': 'Rak besi', 'nominal': 900000},
    {'id': 3006, 'tanggal': '2026-11-12', 'jam': '12:00', 'kategori': 'toko', 'untuk': 'toko', 'keterangan': 'Etalase kaca', 'nominal': 700000, 'dari': 'laci'},
  ],
  'pengaturan': [{'id': 'titikKas', 'tanggal': '2026-11-01', 'laci': 3000000, 'brankas': 0, 'rekening': 0, 'amplop': 0, 'diubahPada': '2026-11-01T14:00:00.000Z'}],
  'aturanToko': [],
}
# angka harapan (Python, terpisah dari kode): garis lurus harian, round half up — A1 Timbangan 4.800.000 beli 15 Jan 2026 umur 48 bln (1.461 hari),
# A2 Timbangan duduk dari uang keluar 3001 1.500.000 beli 10 Nov 2026 umur 48 bln (1.461 hari)
HARAP = {'A1': {'2026-01-15': 3285, '2026-11-26': 1038193, '2026-11-30': 1051335, '2026-12-20': 1117043, '2026-12-31': 1153183, '2030-01-14': 4800000},
         'A2': {'2026-11-30': 21561, '2026-12-20': 42094, '2026-12-31': 53388},
         'A1des20': 65708, 'A1des': 101848, 'duaDes20': 86241, 'duaDes': 133675, 'rakDes': 10267, 'tigaDes': 143942, 'bukuA1': 3682957, 'bukuA2': 1457906}

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-12-20T10:00:00+07:00'); var nId = 900000;
var W = { tanggal: '2026-12-20', jam: '10:00', kini: '2026-12-20T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
var K0 = JSON.parse(J(KOTAK)); Object.keys(K0).forEach(function (n) { pasok(n, K0[n]); }); setelSumber('cadangan', 'kotak pasir');
var dokAs = function (r) { var d = r && r.dokumen ? r.dokumen.find(function (x) { return x.koleksi === 'aturanToko' && x.data.id === 'asetTetap'; }) : null; return d ? d.data : null; };
var pakai = function (r) { terapkanKeCache(r.dokumen); return r; };
var aturan = function (daftar) { pasok('aturanToko', daftar); };
var draf = function (o) { return Object.assign({ nama: 'Timbangan', jenis: 'kecil', harga: '4.800.000', tanggalBeli: '2026-01-15', umurBulan: '', sisa: '', dariKeluar: '', catatan: '' }, o || {}); };
var bulanL = function (k) { return ugLabaBersih(k + '-01', akhirBulanIso(k)); };

// ---------- AS0 daftar kosong ----------
var L0n = J(bulanL('2026-11')), L0d = J(bulanL('2026-12')), N0 = J(neracaPada(null, KINI));
ok('AS0 tanpa dokumen: laba tanpa kolom penyusutan / asetDariBiaya', !('penyusutan' in bulanL('2026-12')) && !('asetDariBiaya' in bulanL('2026-11')));
aturan([{ id: 'asetTetap', mulai: '2026-12-01', aset: [] }]);
ok('AS0 daftar kosong: laba & neraca byte-sama dengan tanpa dokumen', J(bulanL('2026-11')) === L0n && J(bulanL('2026-12')) === L0d && J(neracaPada(null, KINI)) === N0);
aturan([{ id: 'laporan', asetTetap: 5000000, asetKet: 'isian lama' }]); var NL = neracaPada(null, KINI);
ok('AS0 isian lama dipakai Neraca selama daftar kosong (baris "isian owner")', NL.asetTetap === 5000000 && NL.harta.some(function (r) { return /isian owner: isian lama/.test(r.nama) && r.n === 5000000; }), J(NL.harta));

// ---------- AS1 susut harian ----------
var A1 = { id: 'x', harga: 4800000, sisa: 0, tanggalBeli: '2026-01-15', umurBulan: 48 };
ok('AS1 susut terkumpul A1 persis rumus garis lurus harian (hari beli, 26 Nov, 30 Nov, 20 Des, 31 Des, hari terakhir umur)', astSusut(A1, '2026-01-14') === 0 && astSusut(A1, '2026-01-15') === HARAP.A1['2026-01-15'] && astSusut(A1, '2026-11-26') === HARAP.A1['2026-11-26']
  && astSusut(A1, '2026-11-30') === HARAP.A1['2026-11-30'] && astSusut(A1, '2026-12-20') === HARAP.A1['2026-12-20'] && astSusut(A1, '2026-12-31') === HARAP.A1['2026-12-31'] && astSusut(A1, '2030-01-14') === 4800000 && astSusut(A1, '2031-06-01') === 4800000,
  J([astSusut(A1, '2026-01-15'), astSusut(A1, '2026-11-30'), astSusut(A1, '2026-12-31'), astSusut(A1, '2030-01-14')]));
var A1s = Object.assign({}, A1, { sisa: 800000 });
ok('AS1 nilai sisa: berhenti di harga − sisa (4.000.000), bukan nol', astSusut(A1s, '2031-01-01') === 4000000 && astSusut(A1s, '2026-11-30') === Math.round(4000000 * 320 / 1461), J([astSusut(A1s, '2031-01-01'), astSusut(A1s, '2026-11-30')]));
ok('AS1 tambah bulan menjepit akhir bulan (31 Jan + 1 = 28 Feb · 29 Feb 2028 + 12 = 28 Feb 2029) & habis = hari terakhir umur', astTambahBulan('2027-01-31', 1) === '2027-02-28' && astTambahBulan('2028-02-29', 12) === '2029-02-28' && astHabis(A1) === '2030-01-14');
pakai(susunAset(draf({}), W, KINI));
var dA = cacheMentah('aturan').find(function (d) { return d.id === 'asetTetap'; });
ok('AS1 simpan A1: dokumen asetTetap menyimpan tanggal mulai bawaan 1 Des 2026, umur bawaan 48, sisa 0, tanpa tunjuk', dA && dA.mulai === '2026-12-01' && dA.aset.length === 1 && dA.aset[0].harga === 4800000 && dA.aset[0].umurBulan === 48 && dA.aset[0].sisa === 0 && !('dariKeluar' in dA.aset[0]), J(dA));
var EN = astEfekLaba('2026-11-01', '2026-11-30'), ED = astEfekLaba('2026-12-01', '2026-12-31'), ED20 = astEfekLaba('2026-12-01', '2026-12-20');
ok('AS1 November (sebelum mulai) penyusutan 0; bagian sebelum mulai November = 30 Nov − 31 Okt', EN.penyusutan === 0 && EN.sebelum === HARAP.A1['2026-11-30'] - astSusut(A1, '2026-10-31'), J(EN));
ok('AS1 Desember penuh 101.848 · 1–20 Des 65.708', ED.penyusutan === HARAP.A1des && ED20.penyusutan === HARAP.A1des20, J([ED, ED20]));
var sumHari = 0; for (var d = 1; d <= 31; d++) { var t = '2026-12-' + (d < 10 ? '0' : '') + d; sumHari += ugLabaBersih(t, t).penyusutan; }
ok('AS1 Σ penyusutan per hari Desember (ugLabaBersih harian) = Desember sebulan persis', sumHari === HARAP.A1des, sumHari);
ok('AS1 rentang menyeberang mulai: 15 Nov – 10 Des = penyusutan 1–10 Des saja', astEfekLaba('2026-11-15', '2026-12-10').penyusutan === astSusut(A1, '2026-12-10') - astSusut(A1, '2026-11-30'));

// ---------- AS2 laba ----------
var LD = bulanL('2026-12');
ok('AS2 laba Desember = laba mesin ± lebih/kurang kas − penyusutan; kolom penyusutan & asetDariBiaya ada', LD.penyusutan === HARAP.A1des && LD.asetDariBiaya === 0 && LD.labaBersih === LD.labaMesin + LD.lebihKurangKas - HARAP.A1des && ugEfekAset(LD) === -HARAP.A1des, J([LD.labaMesin, LD.lebihKurangKas, LD.labaBersih]));
ok('AS2 laba November tidak bergeser (penyusutan sebelum mulai)', bulanL('2026-11').labaBersih === JSON.parse(L0n).labaBersih && bulanL('2026-11').penyusutan === 0);

// ---------- AS5 tunjuk uang keluar ----------
ok('AS5 harga melebihi nominal catatan ditolak', /tidak boleh lebih besar dari catatan uang keluarnya \(Rp1\.500\.000\)/.test(susunAset(draf({ nama: 'Timbangan duduk', harga: '2.000.000', dariKeluar: '3001' }), W, KINI).tolak || ''));
ok('AS5 ambil pribadi & potongan QRIS tidak bisa ditunjuk', /hanya uang keluar untuk toko/.test(susunAset(draf({ dariKeluar: '3003' }), W, KINI).tolak || '') && /hanya uang keluar untuk toko/.test(susunAset(draf({ harga: '3.500', dariKeluar: 'mdr-2026-12-10' }), W, KINI).tolak || ''));
ok('AS5 catatan yang tidak ada ditolak', /sudah tidak ada/.test(susunAset(draf({ dariKeluar: '9999' }), W, KINI).tolak || ''));
var R2 = susunAset(draf({ nama: 'Timbangan duduk', harga: '1.500.000', tanggalBeli: '2025-01-01', dariKeluar: '3001' }), W, KINI); var d2 = dokAs(R2);
ok('AS5 tunjuk 3001: tanggal beli IKUT catatan (10 Nov), dariKeluar tersimpan, kabar menyebut laba Nov naik Rp1.500.000', d2 && d2.aset.length === 2 && d2.aset[1].tanggalBeli === '2026-11-10' && d2.aset[1].dariKeluar === '3001' && /laba Nov 2026 naik Rp1\.500\.000/.test(R2.patch.kabar), J([d2 && d2.aset[1], R2.patch && R2.patch.kabar]));
pakai(R2);
ok('AS5 catatan yang sama tidak bisa ditunjuk aset kedua', /sudah ditunjuk oleh aset "Timbangan duduk"/.test(susunAset(draf({ nama: 'Lain', harga: '100.000', dariKeluar: '3001' }), W, KINI).tolak || ''));
var LN = bulanL('2026-11'), LD2 = bulanL('2026-12');
ok('AS2 November: uang keluar 3001 keluar dari biaya — laba naik 1.500.000, penyusutan tetap 0', LN.asetDariBiaya === 1500000 && LN.nAsetDariBiaya === 1 && LN.penyusutan === 0 && LN.labaBersih === JSON.parse(L0n).labaBersih + 1500000, J([LN.asetDariBiaya, LN.labaBersih]));
ok('AS2 Desember: penyusutan dua barang 133.675 (1–20 Des 86.241)', LD2.penyusutan === HARAP.duaDes && astEfekLaba('2026-12-01', '2026-12-20').penyusutan === HARAP.duaDes20, J([LD2.penyusutan]));
pakai(susunAset(draf({ nama: 'Rak besi', harga: '600.000', dariKeluar: '3005' }), W, KINI));
ok('AS5 harga di bawah nominal (dompet owner 900.000 → aset 600.000): yang keluar dari biaya = 600.000 saja', bulanL('2026-12').asetDariBiaya === 600000, bulanL('2026-12').asetDariBiaya);
var C = astCalon('', null, 30); var c6 = C.find(function (x) { return x.id === '3006'; }), c1 = C.find(function (x) { return x.id === '3001'; });
ok('AS5 calon: biaya toko & dompet saja (tanpa pribadi/QRIS), terbesar dulu, yang sudah ditunjuk diberi nama asetnya', !C.some(function (x) { return x.id === '3003' || x.id === 'mdr-2026-12-10'; }) && c6 && !c6.dipakai && c1 && c1.dipakai === 'Timbangan duduk' && C[0].id === '3001' && C.every(function (x, i) { return i === 0 || C[i - 1].nominal >= x.nominal; }), J(C));

// ---------- AS3 neraca ----------
var NP = neracaPada(null, KINI); var ra = NP.harta.find(function (r) { return /^Aset tetap \(/.test(r.nama); });
var bukuRak = 600000 - astSusut({ harga: 600000, sisa: 0, tanggalBeli: '2026-12-07', umurBulan: 48 }, '2026-12-20');
ok('AS3 neraca 20 Des: satu baris aset tetap (3 barang) = nilai buku Σ; isian lama TIDAK dipakai lagi', ra && /3 barang · harga beli Rp6\.900\.000/.test(ra.nama) && ra.n === HARAP.bukuA1 + HARAP.bukuA2 + bukuRak && NP.asetTetap === ra.n && !NP.harta.some(function (r) { return /isian owner/.test(r.nama); }), J([ra, NP.asetTetap]));
ok('AS3 neraca seimbang; kekayaan (total) = mesin + nilai buku', NP.seimbang && NP.total === ingatNeraca().total + ra.n, J([NP.total, ingatNeraca().total, ra && ra.n]));
var NP26 = neracaPada('2026-11-26', KINI); var ra26 = NP26.harta.find(function (r) { return /^Aset tetap \(/.test(r.nama); });
ok('AS3 neraca 26 Nov (sebelum mulai): nilai buku sudah dikurangi penyusutan sejak beli (dua barang)', ra26 && /2 barang/.test(ra26.nama) && ra26.n === 4800000 - HARAP.A1['2026-11-26'] + 1500000 - astSusut({ harga: 1500000, sisa: 0, tanggalBeli: '2026-11-10', umurBulan: 48 }, '2026-11-26'), J(ra26));
ok('AS3 catatan neraca menyebut aset bawaan owner & penyusutan sebelum mulai (ikut beda belum terjelaskan)', /Aset tetap: Rp4\.800\.000 dibawa owner \/ dibeli sebelum sistem, penyusutan sebelum 1 Des 2026 Rp/.test(NP.catatan), NP.catatan);
var PS = astPada('2026-12-20'); ok('AS3 astPada: sebelum mulai = susut s.d. 30 Nov, dibawa = barang tanpa tunjuk', PS.sebelum === HARAP.A1['2026-11-30'] + HARAP.A2['2026-11-30'] && PS.dibawa === 4800000 && PS.dariBiaya === 2100000, J([PS.sebelum, PS.dibawa, PS.dariBiaya]));

// ---------- AS4 identitas ----------
['2026-11', '2026-12'].forEach(function (k) {
  var KM = keManaLabaKotor(k, KINI); ok('AS4 Ke mana laba kotor ' + k + ' menutup sampai rupiah', KM.menutup, J(KM.baris));
  var KK = kendaliBulan(k, KINI); ok('AS4 Kendali biaya ' + k + ' menutup', KK.menutup, J([KK.margin, KK.biayaToko, KK.labaBersih]));
  var M = klMarginBulan(k, KINI); ok('AS4 KPI laba ' + k + ': laba usaha → laba bersih menutup', M.tutupUsaha, J(M.identitas));
  var B = labaBulan(k, KINI); var i0 = B.terjun.findIndex(function (r) { return r.nama === 'Margin kotor'; }); var jml = B.terjun.slice(i0, B.terjun.length - 1).reduce(function (a, r) { return a + r.n; }, 0);
  ok('AS4 terjun Laba ' + k + ': margin kotor + baris di bawahnya = laba bersih', Math.abs(jml - B.labaBersih) < 0.5, J(B.terjun));
});
var KMn = keManaLabaKotor('2026-11', KINI), KMd = keManaLabaKotor('2026-12', KINI);
ok('AS4 baris Ke mana: Nov "Uang keluar dipindah jadi aset tetap" +1.500.000 · Des "Penyusutan aset tetap" −143.942 (tiga barang; rak 7 Des = 10.267)', KMn.baris.some(function (r) { return r.id === 'asetBiaya' && r.n === 1500000; }) && KMd.baris.some(function (r) { return r.id === 'penyusutan' && r.n === -HARAP.tigaDes; }), J(KMd.baris));
var DB = laporanBerkop('labarugi', '2026-12', 1, KINI); var bAkhir = DB.baris[DB.baris.length - 1];
ok('AS4 laba-rugi berkop Desember: baris penyusutan & uang keluar dipindah, baris terakhir = laba bersih, catatan menyebut penyusutan', DB.baris.some(function (r) { return r.nama === 'Penyusutan aset tetap' && r.n === -HARAP.tigaDes; }) && DB.baris.some(function (r) { return r.nama === 'Uang keluar dipindah jadi aset tetap' && r.n === 600000; }) && bAkhir.n === bulanL('2026-12').labaBersih && /penyusutan aset tetap/.test(DB.catatan), J(DB.baris.slice(-5)));
var TI = titikImpas(kendaliBulan('2026-12', KINI), KINI); ok('AS4 titik impas: biaya di bawah margin ikut penyusutan & tanpa uang keluar yang dipindah', TI.biaya === kendaliBulan('2026-12', KINI).semuaBiaya + HARAP.tigaDes - 600000, J([TI.biaya]));

// ---------- AS6 bulan terkunci ----------
var atDok = function () { return cacheMentah('aturan').filter(function (d) { return d.id === 'asetTetap'; }); };
aturan(atDok().concat([{ id: 'kunciPeriode', sampaiBulan: '2026-11', riwayat: [] }]));
ok('AS6 Nov terkunci: menunjuk uang keluar November DITOLAK menyebut bulannya', /Laba Nov 2026 akan berubah/.test(susunAset(draf({ nama: 'Etalase kaca', harga: '700.000', dariKeluar: '3006' }), W, KINI).tolak || ''));
ok('AS6 Nov terkunci: tanggal mulai dimundurkan ke 1 Nov DITOLAK; tetap 1 Des boleh', /Laba Nov 2026 akan berubah/.test(susunAturAset({ mulai: '2026-11-01' }, W).tolak || '') && !susunAturAset({ mulai: '2026-12-01' }, W).tolak);
var idA2 = astAtur().aset.find(function (a) { return a.dariKeluar === '3001'; }).id;
ok('AS6 Nov terkunci: hapus aset yang menunjuk uang keluar November DITOLAK', /Laba Nov 2026 akan berubah/.test(susunHapusAset(idA2, W, true).tolak || ''));
var idA1 = astAtur().aset.find(function (a) { return a.nama === 'Timbangan'; }).id;
ok('AS6 Nov terkunci: ubah harga barang bawaan (penyusutan Nov tetap 0) BOLEH', !susunAset(draf({ id: idA1, harga: '5.000.000' }), W, KINI).tolak);
ok('AS6 calon: uang keluar di bulan terkunci diberi tanda terkunci', astCalon('etalase', null, 10)[0].terkunci === true);
aturan(atDok());

// ---------- AS7 isian ----------
var tolak = function (o) { return susunAset(draf(o), W, KINI).tolak || ''; };
ok('AS7 isian ngawur ditolak dengan sebabnya (nama, jenis, harga pecahan, tanggal depan, umur, sisa)', /Ketik nama/.test(tolak({ nama: 'x' })) && /Pilih jenis/.test(tolak({ jenis: 'mobil' })) && /rupiah bulat/.test(tolak({ harga: '1500,5' }))
  && /tidak boleh sesudah hari ini/.test(tolak({ tanggalBeli: '2026-12-21' })) && /Umur harus/.test(tolak({ umurBulan: '0' })) && /Umur harus/.test(tolak({ umurBulan: '601' })) && /Nilai sisa/.test(tolak({ sisa: '4.800.000' })));
ok('AS7 umur kosong = bawaan jenis (kendaraan 96 bulan, bangunan 240)', dokAs(susunAset(draf({ nama: 'Motor antar', jenis: 'kendaraan' }), W, KINI)).aset.slice(-1)[0].umurBulan === 96 && dokAs(susunAset(draf({ nama: 'Renovasi', jenis: 'bangunan' }), W, KINI)).aset.slice(-1)[0].umurBulan === 240);
var Rs = susunAset(draf({ id: idA1, harga: '5.000.000', sisa: '500.000', umurBulan: '60' }), W, KINI); var ds = dokAs(Rs).aset.find(function (a) { return a.id === idA1; });
ok('AS7 ubah barang: id & tanggal dicatat tetap, kolom baru tersimpan', ds.harga === 5000000 && ds.sisa === 500000 && ds.umurBulan === 60 && ds.dicatat === '2026-12-20' && dokAs(Rs).aset.length === 3, J(ds));
aturan(atDok().map(function (d) { return Object.assign({}, d, { catatanLain: 'tetap' }); }));
var Ry = susunHapusAset(idA1, W, false); ok('AS7 hapus ketukan pertama = minta yakin (tidak menulis)', Ry.perluYakin && !Ry.dokumen);
var Rh = susunHapusAset(idA1, W, true); ok('AS7 hapus ketukan kedua menulis daftar tanpa barang itu; kolom lain dokumen DIBAWA', dokAs(Rh).aset.length === 2 && !dokAs(Rh).aset.some(function (a) { return a.id === idA1; }) && dokAs(Rh).catatanLain === 'tetap');
var Rm = susunAturAset({ mulai: '2027-01-01' }, W); ok('AS7 atur mulai menyimpan tanggal pilihan owner + daftar apa adanya', dokAs(Rm).mulai === '2027-01-01' && dokAs(Rm).aset.length === 3);
ok('AS7 tanggal mulai ngawur ditolak', /belum benar/.test(susunAturAset({ mulai: '01-12-2026' }, W).tolak || ''));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var galat = []; var CAD = __CAD__; var hasil = {};
try { Object.keys(CAD).forEach(function (k) { if (Array.isArray(CAD[k])) pasok(k, CAD[k]); }); setelSumber('cadangan', 'asap'); } catch (e) { galat.push('muat: ' + e.message); }
var akhir = (function () { var t = ''; (CAD.penjualan || []).forEach(function (p) { if ((p.tanggal || '') > t) t = p.tanggal; }); return t; })(); var KINI = new Date(akhir + 'T20:00:00+07:00');
var W = { tanggal: akhir, jam: '20:00', kini: KINI.toISOString(), idUnik: (function () { var n = 0; return function () { n += 1; return 'asap' + n; }; })() };
var key = akhir.slice(0, 7); var aw = key + '-01'; var J = function (x) { return JSON.stringify(x); };
try {
  var L0 = J(ugLabaBersih(aw, akhir)), N0 = J(neracaPada(null, KINI)); var at0 = cacheMentah('aturan').slice();
  pasok('aturanToko', at0.concat([{ id: 'asetTetap', mulai: '2026-12-01', aset: [] }])); hasil.kosongSama = J(ugLabaBersih(aw, akhir)) === L0 && J(neracaPada(null, KINI)) === N0;
  var calon = astCalon('', null, 400).filter(function (c) { return c.tanggal >= aw && !c.terkunci && !c.dipakai; }).sort(function (a, b) { return b.nominal - a.nominal; })[0] || null;
  hasil.calon = calon ? { tanggal: calon.tanggal, nominal: calon.nominal } : null;
  var r1 = susunAset({ nama: 'Contoh bawaan', jenis: 'besar', harga: '10.000.000', tanggalBeli: '2025-06-01', umurBulan: '', sisa: '', dariKeluar: '' }, W, KINI); if (r1.tolak) galat.push('aset bawaan: ' + r1.tolak); else terapkanKeCache(r1.dokumen);
  if (calon) { var r2 = susunAset({ nama: 'Contoh dari uang keluar', jenis: 'kecil', harga: String(calon.nominal), tanggalBeli: '', umurBulan: '', sisa: '', dariKeluar: calon.id }, W, KINI); if (r2.tolak) galat.push('aset tunjuk: ' + r2.tolak); else terapkanKeCache(r2.dokumen); }
  // penyusutan memotong laba DI BULAN cadangan (mulai = awal bulan cadangan) supaya semua jalur penyusutan teruji pada data toko
  var r3 = susunAturAset({ mulai: aw }, W); if (r3.tolak) galat.push('mulai: ' + r3.tolak); else terapkanKeCache(r3.dokumen);
  var L1 = ugLabaBersih(aw, akhir); var Lm = JSON.parse(L0);
  hasil.laba = { mesin: Lm.labaBersih, sesudah: L1.labaBersih, penyusutan: L1.penyusutan, dariBiaya: L1.asetDariBiaya, cocok: L1.labaBersih === Lm.labaBersih - L1.penyusutan + L1.asetDariBiaya && L1.asetDariBiaya === (calon ? calon.nominal : 0) };
  var KM = keManaLabaKotor(key, KINI), KK = kendaliBulan(key, KINI), M = klMarginBulan(key, KINI), B = labaBulan(key, KINI); var i0 = B.terjun.findIndex(function (r) { return r.nama === 'Margin kotor'; });
  var DB = laporanBerkop('labarugi', key, 1, KINI); var NP = neracaPada(null, KINI);
  hasil.menutup = { keMana: KM.menutup, kendali: KK.menutup, kpi: M.tutupUsaha, terjun: Math.abs(B.terjun.slice(i0, B.terjun.length - 1).reduce(function (a, r) { return a + r.n; }, 0) - B.labaBersih) < 0.5,
    berkop: DB.baris[DB.baris.length - 1].n === ugLabaBersih(aw, akhirBulanIso(key)).labaBersih, neraca: NP.seimbang, asetNeraca: NP.asetTetap === astPada(akhir).buku };
} catch (e) { galat.push(e.message + ' ' + (e.stack || '').split('\n').slice(0, 2).join(' / ')); }
print(JSON.stringify({ galat: galat, akhir: akhir, hasil: hasil }));
"""

# kerusakan yang WAJIB membuat uji gagal (kontrol positif)
RUSAK = [
    ('laba: penyusutan tidak dipotong', UG, "labaBersih: L.labaBersih + K.n - AS.penyusutan + AS.dariBiaya }", "labaBersih: L.labaBersih + K.n + AS.dariBiaya }"),
    ('laba: uang keluar yang ditunjuk tetap jadi biaya', UG, "labaBersih: L.labaBersih + K.n - AS.penyusutan + AS.dariBiaya }", "labaBersih: L.labaBersih + K.n - AS.penyusutan }"),
    ('laba: daftar kosong tetap menambah kolom', UG, "AS.ada ? { penyusutan:", "true ? { penyusutan:"),
    ('penyusutan sebelum tanggal mulai ikut memotong laba', AS, "const awal = dari > m ? dari : m;", "const awal = dari;"),
    ('susut harian meleset sehari', AS, "const k = astHari(t) - h0 + 1;", "const k = astHari(t) - h0;"),
    ('nilai sisa diabaikan', AS, "const dep = Math.max(0, a.harga - a.sisa); if (!dep) return 0;", "const dep = Math.max(0, a.harga); if (!dep) return 0;"),
    ('bulan terkunci tidak dijaga', AS, "    if (!astTerkunci(k)) continue;", "    if (true) continue;"),
    ('harga aset boleh melebihi catatan uang keluar', AS, "  if (harga > batasHarga) return", "  if (false) return"),
    ('ambil pribadi boleh ditunjuk', AS, "if (AST_KATEGORI_TUNJUK.indexOf(h.kategori) < 0 || h.mdr) return { tolak:", "if (h.mdr) return { tolak:"),
    ('uang keluar dipindah tanpa batas harga aset', AS, "n: sah ? Math.min(a.harga, Math.round(Number(h.nominal) || 0)) : 0", "n: sah ? Math.round(Number(h.nominal) || 0) : 0"),
    ('satu catatan ditunjuk dua aset', AS, "if (lain) return { tolak:", "if (false) return { tolak:"),
    ('tanggal beli tidak ikut catatan yang ditunjuk', AS, "    tanggal = h.tanggal; batasHarga =", "    batasHarga ="),
    ('hapus tanpa ketukan yakin', AS, "  if (!yakin) return { perluYakin: true,", "  if (false) return { perluYakin: true,"),
    ('tanggal mulai pilihan owner tidak disimpan', AS, "return { dokumen: astDokumen(A, A.aset, m, w)", "return { dokumen: astDokumen(A, A.aset, A.mulai, w)"),
    ('dokumen aset membuang kolom lain', AS, "Object.assign({}, A.dok || {}, { id: AST_ID,", "Object.assign({}, {}, { id: AST_ID,"),
    ('neraca tetap memakai isian lama', LG, "const AT = AS.ada ? { asetTetap: AS.buku, asetKet: '' } : AT0;", "const AT = AT0;"),
    ('kekayaan tanpa aset tetap', LG, "total: AS.ada && N.total !== null ? N.total + AS.buku : N.total,", "total: N.total,"),
    ('Ke mana laba kotor tidak menutup', LG, "+ L.lebihKurangKas + EA) - L.labaBersih) < 0.5", "+ L.lebihKurangKas) - L.labaBersih) < 0.5"),
    ('laba-rugi berkop tanpa baris penyusutan', LG, ".concat(L.penyusutan ? [{ nama: 'Penyusutan aset tetap', n: -L.penyusutan }] : []).concat([{ nama: 'Laba bersih', n: L.labaBersih, kelas: 'jumlah' }]);", ".concat([{ nama: 'Laba bersih', n: L.labaBersih, kelas: 'jumlah' }]);"),
    ('terjun Laba tanpa baris penyusutan', LG, ".concat(L.penyusutan ? [['Penyusutan aset tetap', -L.penyusutan]] : []).concat([['Laba bersih', L.labaBersih, 'jumlah']])", ".concat([['Laba bersih', L.labaBersih, 'jumlah']])"),
    ('kendali biaya tidak menutup', KB, "+ L.lebihKurangKas + ugEfekAset(L) - L.labaBersih) < 0.5", "+ L.lebihKurangKas - L.labaBersih) < 0.5"),
    ('titik impas tanpa penyusutan', KB, "const biaya = K.semuaBiaya - ugEfekAset(K.L);", "const biaya = K.semuaBiaya;"),
    ('KPI laba usaha tanpa penyusutan', KL, "+ K.susut - asetPen + asetDari;", "+ K.susut;"),
]
STATIS = [
    ('Laporan: keluarga Aset tetap terdaftar & digambar panelnya', 'laporan', ["import { gambarAset, aksiPanelAset } from './aset-panel.js';", "s.keluarga === 'aset' ? gambarAset(s, L, kini(), grid, LP.aturLaporan())", 'Object.assign(AKSI, aksiPanelAset({ set, st, tulis, waktu, kini, iso }));']),
    ('Laporan › Neraca: tombol membuka daftar aset (isian satu angka dicabut)', 'laporan', ['data-aksi="keluarga" data-nama="aset" data-k="aturN-buka"']),
    ('laporan-logika: keluarga aset di daftar', 'lg', ["['neraca', 'Neraca'], ['aset', 'Aset tetap'], ['pondasi', 'Pondasi']"]),
    ('panel: gerak (gulir, pita, baris bergiliran) & tiga jalur tulis', 'panel', ['data-gulir="${P.buku}"', 'class="lp-pita"', '--urut:', 'susunAset(', 'susunHapusAset(', 'susunAturAset(']),
    ('CSS: baris bergiliran & hormati gerak dikurangi', 'css', ['.layar-laporan .as-baris {', 'animation-delay: calc(var(--urut, 0) * 40ms)', '@media (prefers-reduced-motion: reduce) { .layar-laporan .as-baris']),
    ('modul dipramuat', 'index', ['<link rel="modulepreload" href="js/layar/aset-tetap-logika.js">', '<link rel="modulepreload" href="js/layar/aset-panel.js">']),
    ('bundel uji: modul daun ikut di depan uang-logika', 'bundel', ["AS_MODUL = 'baru/js/layar/aset-tetap-logika.js'", "ASP_MODUL = 'baru/js/layar/aset-panel.js'"]),
    ('peta akses: jalur tulis aset terdaftar', 'peta', ["'susunAset'", "'susunHapusAset'", "'susunAturAset'"]),
    ('pages.yml menjalankan uji ini', 'pages', ['python3 alat-uji/uji_jurnal_aset.py && python3 alat-uji/uji_jurnal_aset.py --kontrol']),
    ('BACA-DULU menyebut modul ini', 'baca', ['## Aset tetap & penyusutan', 'aset-tetap-logika.js', 'aturanToko/asetTetap']),
]
RUSAK_STATIS = [
    ('Laporan tanpa keluarga Aset tetap', 'laporan', "s.keluarga === 'aset' ? gambarAset(s, L, kini(), grid, LP.aturLaporan())", "false ? gambarAset(s, L, kini(), grid, LP.aturLaporan())"),
    ('pages.yml tanpa uji ini', 'pages', 'python3 alat-uji/uji_jurnal_aset.py', 'true'),
    ('modul daun mengimpor uang-logika (lingkar)', 'as', "import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';", "import { RP, hariIniIso, tanggalPendek } from '../inti/format.js';\nimport { ugAngka } from './uang-logika.js';"),
    ('rules disentuh', 'rules', 'match /aturanToko/{id} {', 'match /aturanToko/{id} { // asetTetap'),
]


def bundel(teks):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in MODUL)
    js = uji_kunci_periode.satu_lingkup(js)   # tabrakan nama lama bundel Dasbor (sama dengan uji_kpi_laba): stok-hpp teksMargin & susunBon bon pemasok
    B = uji_ringkasan_baru.BON_PEMASOK_LAMA
    return js.replace(B, B.replace('susunBon(', 'bpSusunBon(')) if js.count(B) == 1 else js


def jalan(teks, isi=None):
    js = JAM + bundel(teks) + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar HARAP = ' + json.dumps(HARAP) + ';\n' + (isi or SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return None, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    return json.loads(out), None


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    a = src['as']
    if 'document.' in a or 'tulisDokumen' in a: g.append('aset-tetap-logika menyentuh DOM / menulis langsung — modul ini cuma menyusun')
    imp = [l for l in a.split('\n') if l.startswith('import ')]
    if any("from '../data/toko.js'" not in l and "from '../inti/format.js'" not in l for l in imp): g.append('aset-tetap-logika bukan modul daun lagi: ' + ' | '.join(imp)[:160])
    if 'asetTetap' in src['rules'] or src['rules'].count('match /aturanToko/{id} {') != 1: g.append('rules disentuh — modul ini sengaja tanpa rules baru (aturanToko sudah owner saja)')
    return len(STATIS) - len(g), g


def muat():
    sumber = set(MODUL)
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in sumber), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b); h, e = jalan(T); g = e if h is None else h['gagal']
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        for nama, berkas, a, b in RUSAK_STATIS:
            if src[berkas].count(a) < 1: print('KONTROL BASI  ' + nama); kode = 3; continue
            S = dict(src); S[berkas] = S[berkas].replace(a, b); l, g = statis(S)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h, e = jalan(teks); ls, gs = statis(src)
    g = e if h is None else h['gagal']
    print('KOTAK PASIR: %d lulus · %d gagal' % (0 if h is None else h['lulus'], len(g)))
    for x in g: print('   ✗ ' + x)
    print('STATIS: %d lulus · %d gagal' % (ls, len(gs)))
    for x in gs: print('   ✗ ' + x)
    cad = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '..', '..', '..', '_privat', 'backup-batch-*.json')), key=os.path.basename)
    if cad and '--tanpa-asap' not in sys.argv:
        ha, ea = jalan(teks, ASAP.replace('__CAD__', open(cad[-1], encoding='utf-8').read()))
        if ha is None: print('ASAP DATA TOKO: JSC JATUH ' + ea[0][:600]); g = list(g) + ['asap']
        else:
            H = ha['hasil']; M = H.get('menutup') or {}; beres = not ha['galat'] and H.get('kosongSama') and (H.get('laba') or {}).get('cocok') and M and all(M.values())
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s · galat %s' % (os.path.basename(cad[-1]), ha['akhir'], 'LULUS' if beres else 'GAGAL', json.dumps(H, ensure_ascii=False), json.dumps(ha['galat'], ensure_ascii=False)))
            if not beres: g = list(g) + ['asap']
    sys.exit(1 if g or gs else 0)
