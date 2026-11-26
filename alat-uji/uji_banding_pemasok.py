#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_banding_pemasok.py — PAKET BANDING PEMASOK (keputusan owner 26 Nov 2026, sensus ulang 1c: A6 · A18 · A19 · A95 · A129 · A137). KOTAK PASIR (nama & angka
CONTOH), jsc saja, TANPA peramban.
  Hitungan (banding-pemasok-logika): kg diterima per baris (nota / timbang / sampel / ikut timbang, retur dikurangi), modal sampai toko = mesin
  hitungHppMerkDalamBatch ÷ kg diterima, pecahan harga + bongkar & ongkir + timbang MENUTUP ke modal, layak jual = (modal + potongan mutu) ÷ (kg × (1 − susut
  gudang pemasok 3 bulan)), harga tawaran = perkiraan (ongkir & bongkar rata-rata toko, susut rata-rata toko), urutan termurah dulu per kelas, jumlah pemasok
  (kedatangan + tawaran) vs minimal owner, PENJAGA Σ baris = sapuan Bon pemasok; laporan mingguan berjajar + tanggal; rapor bulanan (timbang = rekapTimbangMutu,
  retur / tolak / klaim = jejak kedatangan, susut, tawaran); harga acuan terbaru vs modal kelas HET; tren modal per bulan.
  Catatan (banding-catat-logika): satu penjaga isian untuk owner / tablet / setujui usul, dokumen aturanToko/banding-YYYY-MM, kembar ditolak, hapus, tandai,
  setelan (potongan mutu, sumber, hari), usul tablet = bentuk rules v21 (= akses.js usulBandingSah), setujui lewat papan Persetujuan (sistem-logika),
  pengingat Jumat & tanggal 1 (berhenti sesudah cukup / ditandai), tarik otomatis (functions/acuan.js menyisir JSON, bukan angka karangan).

    python3 alat-uji/uji_banding_pemasok.py            → N lulus · 0 gagal (+ asap cadangan toko bila ada di _privat/)
    python3 alat-uji/uji_banding_pemasok.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile, glob
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_antar, uji_ringkasan_baru, uji_kunci_periode, uji_faktur, uji_jual_baru  # noqa: E402
JSC = uji_antar.JSC
BD = 'baru/js/layar/banding-pemasok-logika.js'; BC = 'baru/js/layar/banding-catat-logika.js'; SH = 'baru/js/layar/susut-harga-logika.js'; SL = 'baru/js/layar/sistem-logika.js'
CK = 'baru/js/layar/stok-catat-logika.js'; AK = 'baru/js/data/akses.js'; FA = 'functions/acuan.js'
MODUL_A = bundel_baru.lengkapi(list(dict.fromkeys(uji_ringkasan_baru.modul_dasbor() + [SH, BD])))
MODUL_B = bundel_baru.lengkapi(list(uji_faktur.MODUL))
SUMBER = {'harga': 'baru/js/layar/harga.js', 'menu': 'baru/js/layar/menu.js', 'menuL': 'baru/js/layar/menu-logika.js', 'panel': 'baru/js/layar/banding-panel.js', 'bd': BD, 'bc': BC,
          'sl': SL, 'ak': AK, 'css': 'baru/css/harga.css', 'pages': '.github/workflows/pages.yml', 'baca': 'baru/BACA-DULU.md', 'rsd': 'baru/js/data/riwayat-setelan.js',
          'rsl': 'baru/js/layar/riwayat-setelan-logika.js', 'fi': 'functions/index.js', 'fp': 'functions/pesan.js', 'fa': FA, 'rules': 'firestore.rules', 'bundel': 'alat-uji/bundel_baru.py',
          'peta': 'alat-uji/peta_akses.py', 'ck': CK}

ATUR = [
    {'id': 'catatStok', 'tempoHari': 21, 'kadarAirMaks': 14, 'patahMaks': 25},
    {'id': 'kelasMerek', 'peta': {'Merek A1': 'Kelas Satu', 'Merek B1': 'Kelas Satu', 'Merek A2': 'Kelas Dua'}, 'asal': {'Merek A1': 'owner', 'Merek B1': 'owner', 'Merek A2': 'owner'}, 'kelasSendiri': []},
    {'id': 'het', 'medium': 12700, 'premium': 14900, 'zona': 'Zona contoh', 'sumber': 'contoh', 'peta': {'Kelas Satu': 'medium'}},
    {'id': 'bandingPemasok', 'minPemasok': 3, 'hariMinggu': 5, 'tanggalBulan': 1, 'potongMutu': {'kadarAir': 100}, 'sumber': ['Panel Harga Bapanas', 'PIHPS BI', 'BPS'], 'wilayah': ''},
    {'id': 'banding-2026-11', 'bulan': '2026-11', 'entri': [
        {'id': 'bdT1', 'jenis': 'tawaran', 'tanggal': '2026-11-20', 'pemasok': 'Pemasok Contoh C', 'kelas': 'Kelas Satu', 'merek': '', 'hargaPerKg': 11500, 'ongkirPerKg': 0, 'sampaiToko': False, 'ongkirDiketahui': False, 'catatan': '', 'oleh': 'Owner', 'dicatatPada': '2026-11-20T03:00:00.000Z'},
        {'id': 'bdA1', 'jenis': 'acuan', 'tanggal': '2026-11-20', 'sumber': 'Panel Harga Bapanas', 'tingkat': 'grosir', 'mutu': 'medium', 'wilayah': 'nasional', 'hargaPerKg': 12500, 'catatan': '', 'oleh': 'Owner', 'dicatatPada': '2026-11-20T03:01:00.000Z'}]},
]
BARIS = lambda merk, jml, harga, **k: dict({'merk': merk, 'satuan': 'karung', 'beratKarung': 50, 'jumlahKarung': jml, 'totalKg': jml * 50, 'hargaPerKg': harga, 'subtotalHarga': jml * 50 * harga}, **k)
KOTAK_BD = {
  'batchMasuk': [
    {'id': 90, 'tanggal': '2026-10-06', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'utang', 'biayaBongkar': 0, 'merkList': [BARIS('Merek A1', 20, 11800)]},
    # 2 Nov · A: Merek A1 ditimbang 990 (nota 1000, kadar air 15 % → AWAS), Merek A2 belum ditimbang; bongkar 50.000 + ongkos kirim 25.000
    {'id': 101, 'tanggal': '2026-11-02', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'utang', 'biayaBongkar': 75000, 'ongkosKirim': 25000,
     'merkList': [BARIS('Merek A1', 20, 12000, timbangKg=990, kadarAir=15), BARIS('Merek A2', 10, 13000)]},
    # 3 Nov · B: Merek B1 IKUT TIMBANG (kgTerima 1005 → buku 1005), uang dari nota 1000 kg
    {'id': 102, 'tanggal': '2026-11-03', 'jam': '08:00', 'pemasok': 'Pemasok Contoh B', 'caraBayar': 'utang', 'biayaBongkar': 50000,
     'merkList': [dict(BARIS('Merek B1', 20, 11800), totalKg=1005, kgTerima=1005, timbangKg=1005)]},
    # 4 Nov · A: baris BAL (beli jadi, tidak dibanding) + Merek A1 timbang SAMPEL 2 karung 99 kg (perkiraan 99 kg)
    {'id': 103, 'tanggal': '2026-11-04', 'jam': '08:00', 'pemasok': 'Pemasok Contoh A', 'caraBayar': 'Tunai', 'biayaBongkar': 3000,
     'merkList': [{'merk': 'Kemasan Contoh', 'bentuk': 'bal', 'satuan': 'bal', 'totalKg': 50, 'hargaPerKg': 14000, 'subtotalHarga': 700000}, BARIS('Merek A1', 2, 12100, sampelKarung=2, sampelKg=99)]},
    # 5 Nov · B: Merek B1 500 kg ditimbang pas, 50 kg dikembalikan (retur — baris lama: buku 450, uang 450 kg) + 100 kg ditolak saat datang + klaim diminta
    {'id': 104, 'tanggal': '2026-11-05', 'jam': '08:00', 'pemasok': 'Pemasok Contoh B', 'caraBayar': 'utang', 'biayaBongkar': 0,
     'merkList': [dict(BARIS('Merek B1', 10, 11900), totalKg=450, kgPotong=50, subtotalHarga=450 * 11900, timbangKg=500)],
     'potongan': [{'jenis': 'retur', 'tanggal': '2026-11-06', 'kg': 50, 'rp': 595000, 'alasan': 'basah', 'baris': [{'merk': 'Merek B1', 'kg': 50, 'rp': 595000}]}],
     'ditolak': [{'merk': 'Merek B1', 'jumlahKarung': 2, 'beratKarung': 50, 'kg': 100, 'nilai': 1190000, 'alasan': 'basah'}], 'klaim': {'cara': 'catat', 'status': 'diminta', 'nilai': 0}}],
  # 25 Nov · hitungan Merek A1: buku 100 → fisik 74 (−26 kg) → susut gudang Pemasok A = 26 ÷ 2.600 kg datang (Sep–Nov) = 1 %
  'penyesuaianStok': [{'id': 201, 'tanggal': '2026-11-25', 'jam': '10:00', 'merk': 'Merek A1', 'kgSistem': 100, 'kgFisik': 74, 'selisihKg': -26, 'alasan': 'susut', 'nilaiRp': -314600, 'hppPerKgSaatOpname': 12100, 'bagian': 'tumpukan', 'bagianSistemKg': 100, 'bagianFisikKg': 74}],
}

SKENARIO_A = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); }; var dekat = function (a, b, t) { return typeof a === 'number' && typeof b === 'number' && Math.abs(a - b) < (t || 0.01); };
var KINI = new Date('2026-11-26T15:00:00+07:00'); var nId = 70000;
var W = { tanggal: '2026-11-26', jam: '15:00', kini: '2026-11-26T08:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'pesanan', 'penjualan', 'utangPemasokMutasi', 'pemasokCatatan', 'persetujuan', 'pesananPemasok'].forEach(function (n) { pasok(n, []); });
Object.keys(BDK).forEach(function (n) { pasok(n, JSON.parse(J(BDK[n]))); });
setelSumber('cadangan', 'kotak pasir');
var aturDengan = function (extra, buang) { pasok('aturanToko', JSON.parse(J(ATUR)).filter(function (d) { return (buang || []).indexOf(d.id) < 0; }).concat(extra || [])); };
aturDengan([]);
var baris = function (B, batch, merk) { return B.baris.find(function (r) { return String(r.batchId) === String(batch) && r.merk === merk; }); };
var dokAt = function (r) { return (r.dokumen || []).filter(function (x) { return x.koleksi === 'aturanToko'; }).map(function (x) { return x.data; })[0] || null; };

// ==================== A6 · BARIS & MODAL SAMPAI TOKO ====================
var B = bdBaris('2026-11-01', '2026-11-30');
var a101 = baris(B, 101, 'Merek A1'), a101b = baris(B, 101, 'Merek A2'), b102 = baris(B, 102, 'Merek B1'), a103 = baris(B, 103, 'Merek A1'), b104 = baris(B, 104, 'Merek B1');
ok('kg diterima: baris lama ditimbang = hasil timbang (990), bukan nota 1000', a101 && a101.kgNyata === 990 && a101.asal === 'timbang' && a101.kgTagih === 1000, J(a101));
ok('kg diterima: baris belum ditimbang = kg nota DISEBUT "nota" (bukan dianggap pas)', a101b && a101b.kgNyata === 500 && a101b.asal === 'nota', J(a101b));
ok('kg diterima: baris ikut timbang = kg buku (1005), kg dibayar = nota 1000', b102 && b102.kgNyata === 1005 && b102.asal === 'timbang' && b102.kgTagih === 1000, J(b102));
ok('kg diterima: timbang SAMPEL = perkiraan 99 kg (ditandai sampel)', a103 && a103.kgNyata === 99 && a103.asal === 'sampel', J(a103));
ok('kg diterima: retur dikurangi dari hasil timbang (500 − 50 = 450), kg dibayar 450', b104 && b104.kgNyata === 450 && b104.kgTagih === 450, J(b104));
ok('baris BAL & baris tanpa kg tidak dibanding — dihitung di nilaiLewat (bal 700.000 + porsi bongkar 1.000)', B.dilewati === 1 && dekat(B.nilaiLewat, 701000), J([B.dilewati, B.nilaiLewat]));
ok('porsi bongkar & ongkos kirim = mesin hitungHppMerkDalamBatch (75.000 dibagi menurut kg: 50.000 / 25.000)', dekat(a101.bongkar, 50000) && dekat(a101b.bongkar, 25000) && dekat(a103.bongkar, 2000), J([a101.bongkar, a101b.bongkar, a103.bongkar]));
ok('modal sampai toko per baris = (nilai + bongkar) ÷ kg diterima', dekat(a101.modalKg, 12050000 / 990) && dekat(b102.modalKg, 11850000 / 1005), J([a101.modalKg, b102.modalKg]));
ok('tanda mutu AWAS terbaca dari tmBaris (kadar air 15 > 14) → potongan mutu 100/kg × 990 kg', J(a101.tanda) === J(['kadarAir']) && a101.potMutuKg === 100 && dekat(a101.potMutuRp, 99000), J([a101.tanda, a101.potMutuRp]));
ok('kelas = kelas yang dikonfirmasi owner (Merek A1 & B1 → Kelas Satu), HET medium terbawa', a101.kelas === 'Kelas Satu' && b102.kelas === 'Kelas Satu' && a101b.kelas === 'Kelas Dua' && a101.het === 'medium' && a101b.het === '', J([a101.kelas, a101.het]));

// ==================== SUSUT & RATA-RATA TOKO ====================
var S = bdSusut('2026-11-30'); var kA = kunciPelanggan('Pemasok Contoh A'), kB = kunciPelanggan('Pemasok Contoh B');
ok('susut gudang per pemasok = shSusutPemasok 3 bulan: A 26 kg ÷ 2.600 kg datang = 1 %, B belum terukur', S.per[kA] && dekat(S.per[kA].pct, 1, 1e-9) && (!S.per[kB] || S.per[kB].pct === null), J(S.per));
ok('susut rata-rata toko = Σ susut ÷ Σ kg datang (26 ÷ 4.055)', dekat(S.rataPct, 26 / 4055 * 100, 1e-9), S.rataPct);
var RB = bdRataBongkar('2026-09-01', '2026-11-30');
ok('rata-rata bongkar & ongkir toko per kg terpisah (ongkir 25.000 · bongkar 103.000 ÷ 4.055 kg)', dekat(RB.ongkirKg, 25000 / 4055, 1e-9) && dekat(RB.bongkarKg, 103000 / 4055, 1e-9) && RB.ganjil === 0, J(RB));

// ==================== A95 · BANDING BULAN ====================
var BL = bdBulan('2026-11', KINI); var K1 = BL.kelas.find(function (g) { return g.kelas === 'Kelas Satu'; });
var xA = K1 && K1.baris.find(function (x) { return x.pemasok === 'Pemasok Contoh A'; }); var xB = K1 && K1.baris.find(function (x) { return x.pemasok === 'Pemasok Contoh B'; });
var xC = K1 && K1.baris.find(function (x) { return x.pemasok === 'Pemasok Contoh C'; });
var modalA = (12050000 + 1212000) / 1089, layakA = (13262000 + 99000) / (1089 * 0.99);
ok('modal sampai toko A (Kelas Satu) tertimbang kg: 13.262.000 ÷ 1.089 kg', xA && xA.modalKg === Math.round(modalA), J(xA));
ok('layak jual A = (modal + potongan mutu 99.000) ÷ (1.089 kg × (1 − 1 %))', xA && xA.layakKg === Math.round(layakA), J([xA && xA.layakKg, Math.round(layakA)]));
ok('pecahan MENUTUP: nota + bongkar + timbang = modal; modal + mutu + susut = layak jual (rupiah bulat)', xA && xA.hargaKg + xA.bongkarKg + xA.timbangKg === xA.modalKg && xA.modalKg + xA.mutuKg + xA.susutKg === xA.layakKg
   && xB.hargaKg + xB.bongkarKg + xB.timbangKg === xB.modalKg && xB.modalKg + xB.mutuKg + xB.susutKg === xB.layakKg, J([xA, xB]));
ok('pecahan A: harga nota per kg dibayar = 13.210.000 ÷ 1.100', xA && xA.hargaKg === Math.round(13210000 / 1100) && xA.bongkarKg === Math.round(52000 / 1100), J(xA));
ok('B: susut belum terukur = 0 % (DISEBUT, susutPct null) → layak = modal', xB && xB.susutPct === null && xB.layakKg === xB.modalKg && xB.modalKg === Math.round(17205000 / 1455), J(xB));
var modalC = 11500 + RB.ongkirKg + RB.bongkarKg, layakC = modalC / (1 - S.rataPct / 100);
ok('harga TAWARAN C = perkiraan: harga + ongkir rata-rata toko (tidak disebut) + bongkar rata-rata, susut rata-rata toko', xC && xC.jenis === 'tawaran' && xC.perkiraan && xC.ongkirDitebak && xC.modalKg === Math.round(modalC) && xC.layakKg === Math.round(layakC), J([xC, modalC, layakC]));
ok('urutan per kelas termurah dulu (layak jual): C (tawaran) → B → A', K1 && J(K1.baris.map(function (x) { return x.pemasok.slice(-1); })) === J(['C', 'B', 'A']) && K1.baris[0].urut === 1 && K1.baris[2].lebihMahal === K1.baris[2].layakKg - K1.baris[0].layakKg, J(K1 && K1.baris.map(function (x) { return [x.pemasok, x.layakKg]; })));
ok('hemat per bulan hanya dari yang DIBELI (tawaran tidak dikali kg)', K1 && K1.baris.filter(function (x) { return x.jenis === 'tawaran'; }).every(function (x) { return x.hematPerBulan === 0; }) && xA.hematPerBulan === Math.round(xA.lebihMahal * xA.kgNyata), J(K1 && K1.baris));
ok('jumlah pemasok dibanding = kedatangan (A, B) + tawaran (C) = 3 → cukup (minimal 3)', BL.nPemasok === 3 && BL.cukup === true && BL.min === 3, J([BL.nPemasok, BL.pemasok]));
ok('PENJAGA menutup: Σ modal baris + bagian lewat = nilai kedatangan di Bon pemasok (37.693.000)', BL.menutup === true && dekat(BL.nilai, 37693000) && dekat(BL.sapuan, 37693000), J([BL.nilai, BL.sapuan]));
aturDengan([{ id: 'bandingPemasok', minPemasok: 4, hariMinggu: 5, tanggalBulan: 1, potongMutu: {} }], ['bandingPemasok']);
var BL4 = bdBulan('2026-11', KINI); var xA4 = BL4.kelas.find(function (g) { return g.kelas === 'Kelas Satu'; }).baris.find(function (x) { return x.pemasok === 'Pemasok Contoh A'; });
ok('minimal pemasok = setelan owner (4 → KURANG) · potongan mutu dicabut → mutu Rp0', BL4.cukup === false && BL4.min === 4 && xA4.mutuKg === 0 && /KURANG/.test(BL4.kalimat), J([BL4.cukup, xA4.mutuKg]));
aturDengan([]);
// penjaga BISA gagal: kedatangan berbongkar tapi barisnya 0 kg — mesin membagi bongkar menurut kg (0 ÷ 0 → porsi 0), sapuan Bon pemasok tetap menghitungnya
pasok('batchMasuk', JSON.parse(J(BDK.batchMasuk)).concat([{ id: 105, tanggal: '2026-11-06', jam: '08:00', pemasok: 'Pemasok Contoh B', caraBayar: 'utang', biayaBongkar: 5000, merkList: [{ merk: 'Merek B1', satuan: 'karung', beratKarung: 50, jumlahKarung: 0, totalKg: 0, hargaPerKg: 11800, subtotalHarga: 0 }] }]));
var BX = bdBulan('2026-11', KINI);
ok('PENJAGA berbunyi: bongkar 5.000 pada kedatangan 0 kg tidak masuk baris mana pun → TIDAK MENUTUP disebut di kalimat', BX.menutup === false && dekat(BX.sapuan - BX.nilai, 5000) && /PENJAGA TIDAK MENUTUP/.test(BX.kalimat), J([BX.nilai, BX.sapuan]));
pasok('batchMasuk', JSON.parse(J(BDK.batchMasuk)));
var BO = bdBulan('2026-10', KINI);
ok('Oktober: satu pemasok, penjaga menutup, kalimat menyebut KURANG', BO.nPemasok === 1 && BO.menutup && BO.cukup === false, J([BO.nPemasok, BO.menutup]));

// ==================== A129 + A18 · MINGGUAN ====================
var M = bdMinggu('2026-11-04', KINI); var M1 = M.kelas.find(function (g) { return g.kelas === 'Kelas Satu'; });
ok('minggu = Senin–Minggu (2–8 Nov), apa pun hari yang diminta', M.senin === '2026-11-02' && M.minggu === '2026-11-08', J([M.senin, M.minggu]));
ok('harga beli per kg BERJAJAR per pemasok + tanggal kedatangan (B 11.800/11.900 tertimbang kg, A 12.000/12.100)', M1 && M1.kolom.length === 2 && M1.kolom[0].pemasok === 'Pemasok Contoh B' && J(M1.kolom[0].tanggal) === J(['2026-11-03', '2026-11-05'])
   && M1.kolom[0].harga === Math.round((1000 * 11800 + 500 * 11900) / 1500) && M1.kolom[1].lebih === M1.kolom[1].harga - M1.kolom[0].harga, J(M1));
ok('minggu 2–8 Nov: 2 pemasok berharga (< 3)', M.nPemasok === 2 && M.cukup === false, M.nPemasok);
var M3 = bdMinggu('2026-11-16', KINI);
ok('minggu 16–22 Nov: harga tawaran C ikut (tanggal ditanya) + acuan minggu itu', M3.nPemasok === 1 && M3.nTawaran === 1 && M3.acuan.length === 1 && M3.kelas[0].kolom[0].jenis === 'tawaran' && J(M3.kelas[0].kolom[0].tanggal) === J(['2026-11-20']), J(M3));

// ==================== A137 · RAPOR ====================
var R = bdRapor('2026-11', KINI); var rA = R.pemasok.find(function (p) { return p.pemasok === 'Pemasok Contoh A'; }); var rB = R.pemasok.find(function (p) { return p.pemasok === 'Pemasok Contoh B'; });
var rC = R.pemasok.find(function (p) { return p.pemasok === 'Pemasok Contoh C'; });
ok('rapor B: retur 50 kg / 595.000 · ditolak 100 kg / 1.190.000 · klaim 1 masih diminta', rB && rB.retur.kg === 50 && rB.retur.rp === 595000 && rB.tolak.kg === 100 && rB.tolak.rp === 1190000 && rB.klaim.diminta === 1, J(rB && [rB.retur, rB.tolak, rB.klaim]));
ok('rapor timbang = rekapTimbangMutu apa adanya: A kurang 11 kg (990/1000 + sampel 99/100), B lebih 5 kg', rA && rA.timbang && rA.timbang.selisihKg === -11 && rB.timbang.selisihKg === 5 && rA.timbang.sebagian === 1, J([rA && rA.timbang, rB && rB.timbang]));
ok('rapor mutu: A satu tanda kadar air + potongan 99.000; susut A 1 %', rA && rA.tanda.length === 1 && rA.tanda[0].id === 'kadarAir' && dekat(rA.potMutuRp, 99000) && dekat(rA.susut.pct, 1, 1e-9), J(rA && [rA.tanda, rA.potMutuRp]));
ok('rapor: pemasok yang HANYA menawarkan (C) ikut, tanpa kelompok kedatangan', rC && !rC.kelompok && rC.tawaran.length === 1 && /hanya 1 harga tawaran/.test(rC.kalimat), J(rC));
ok('rapor kelompok A = angka banding bulan yang sama (modal semua kelas A)', rA && rA.kelompok.modalKg === Math.round((12050000 + 6525000 + 1212000) / (990 + 500 + 99)), J(rA && rA.kelompok));

// ==================== A19 · ACUAN ====================
var A = bdAcuan(KINI); var a0 = A.acuan[0];
ok('acuan terbaru per sumber × tingkat × mutu; pembanding = modal kelas yang dipetakan HET medium 30 hari', A.acuan.length === 1 && a0.hargaPerKg === 12500 && a0.modalKg === Math.round(30467000 / 2544) && a0.selisih === a0.modalKg - 12500 && /di bawah/.test(a0.kalimat), J(a0));
ok('tanpa pemetaan HET → kalimat menyebutnya (bukan angka 0)', (function () { aturDengan([{ id: 'het', medium: 12700, premium: 14900, peta: {} }], ['het']); var X = bdAcuan(KINI); aturDengan([]); return X.petaKosong && X.acuan[0].modalKg === null && /belum ada kedatangan medium/.test(X.acuan[0].kalimat); })());

// ==================== A6 · TREN ====================
var T = bdTren(KINI, 6); var tK = T.kelas.find(function (k) { return k.kelas === 'Kelas Satu'; }); var tO = tK.titik.find(function (t) { return t.key === '2026-10'; }), tN = tK.titik.find(function (t) { return t.key === '2026-11'; });
ok('tren: Okt 11.800 → Nov ' + Math.round(30467000 / 2544) + ' (▲), terendah Okt; bulan tanpa kedatangan = tidak ada (bukan 0)', tO.modalKg === 11800 && tN.modalKg === Math.round(30467000 / 2544) && tN.gerak === tN.modalKg - 11800 && tK.terendah.key === '2026-10'
   && tK.titik.filter(function (t) { return !t.ada; }).length === 4 && tN.termurah.nama === 'Pemasok Contoh B', J(tK));

// ==================== CATATAN (banding-catat-logika) ====================
var CT = susunCatatBanding('tawaran', { pemasok: 'Pemasok Contoh D', kelas: 'Kelas Satu', hargaPerKg: '11.950', ongkirPerKg: '0', tanggal: '2026-11-24' }, W, 'Owner');
var dC = dokAt(CT);
ok('catat tawaran: dokumen aturanToko/banding-2026-11 (bulan TANGGAL harga), entri lama ikut, ongkir 0 yang diketik = diketahui', dC && dC.id === 'banding-2026-11' && dC.entri.length === 3 && dC.entri[2].hargaPerKg === 11950 && dC.entri[2].ongkirDiketahui === true && dC.entri[2].oleh === 'Owner' && CT.dokumen.length === 1, J(CT));
ok('catat: harga pecahan / harga karung / huruf DITOLAK (bukan dibulatkan diam-diam)', !!susunCatatBanding('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: '12,5' }, W).tolak && !!susunCatatBanding('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: '645.000' }, W).tolak
   && !!susunCatatBanding('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: 'dua belas' }, W).tolak && bcRupiah('12,5') !== bcRupiah('12,5') && bcRupiah('14.500') === 14500);
ok('catat: tanggal di depan / > 62 hari lalu ditolak; tanpa kelas ditolak; nama sistem bukan pemasok', !!susunCatatBanding('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: '12000', tanggal: '2026-11-27' }, W).tolak
   && !!susunCatatBanding('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: '12000', tanggal: '2026-09-20' }, W).tolak && !!susunCatatBanding('tawaran', { pemasok: 'P X', hargaPerKg: '12000' }, W).tolak
   && !!susunCatatBanding('tawaran', { pemasok: 'LAHIR BUKU', kelas: 'K X', hargaPerKg: '12000' }, W).tolak);
ok('catat KEMBAR (tanggal, pemasok, kelas, harga sama) ditolak', /Sudah tercatat/.test(susunCatatBanding('tawaran', { pemasok: 'pemasok contoh c', kelas: 'kelas satu', hargaPerKg: '11500', tanggal: '2026-11-20' }, W).tolak || ''));
var CA = susunCatatBanding('acuan', { sumber: 'PIHPS BI', tingkat: 'grosir', mutu: 'premium', hargaPerKg: '14200' }, W); var eA = dokAt(CA).entri.slice(-1)[0];
ok('catat acuan: sumber, tingkat, mutu wajib; wilayah bawaan = setelan', eA.jenis === 'acuan' && eA.sumber === 'PIHPS BI' && eA.mutu === 'premium' && eA.tanggal === '2026-11-26' && !!susunCatatBanding('acuan', { sumber: 'BPS', tingkat: 'pasar', mutu: 'medium', hargaPerKg: '13000' }, W).tolak, J(eA));
var HP = susunHapusBanding('bdT1', W);
ok('hapus satu entri: dokumen bulan ditulis ulang tanpa entri itu', dokAt(HP).entri.length === 1 && dokAt(HP).entri[0].id === 'bdA1' && !!susunHapusBanding('tidak-ada', W).tolak, J(HP));
var AT = susunAturBanding({ minPemasok: '4', hariMinggu: 6, tanggalBulan: '2', potongMutu: { kadarAir: '150', kutu: '' }, sumber: ['Panel Harga Bapanas', 'Pasar induk'], wilayah: 'Wilayah contoh' }, W); var dAt = dokAt(AT);
ok('setelan: angka owner tersimpan, potongan mutu per tanda (kosong = 0), sumber bebas', dAt.minPemasok === 4 && dAt.hariMinggu === 6 && dAt.tanggalBulan === 2 && dAt.potongMutu.kadarAir === 150 && dAt.potongMutu.kutu === 0 && J(dAt.sumber) === J(['Panel Harga Bapanas', 'Pasar induk']), J(dAt));
ok('setelan ditolak: minimal 0 / tanggal 31 / potongan pecahan / sumber kembar / sumber kosong', !!susunAturBanding({ minPemasok: '0' }, W).tolak && !!susunAturBanding({ tanggalBulan: '31' }, W).tolak && !!susunAturBanding({ potongMutu: { menir: '12,5' } }, W).tolak
   && !!susunAturBanding({ sumber: ['BPS', 'bps'] }, W).tolak && !!susunAturBanding({ sumber: [] }, W).tolak);
var TD = susunTandaiBanding('2026-11', 'kelas satu pindah ke pemasok B', W);
ok('tandai sudah dibanding: tanda tersimpan di dokumen bulan, entri tetap', dokAt(TD).dibanding.catatan === 'kelas satu pindah ke pemasok B' && dokAt(TD).entri.length === 2 && !!susunTandaiBanding('2026-12', '', W).tolak, J(TD));

// ==================== PENGINGAT ====================
var P1 = bcSumberPengingat('2026-11-26'); var pw = P1.find(function (p) { return p.jenis === 'banding'; });
ok('pengingat mingguan: minggu ini (23–29 Nov) belum punya harga 3 pemasok → jatuh JUMAT 27 Nov', pw && pw.jatuh === '2026-11-27' && pw.id === 'banding|2026-11-23' && /baru 0/.test(pw.teks), J(P1));
aturDengan([{ id: 'banding-2026-11', bulan: '2026-11', entri: ['P1', 'P2', 'P3'].map(function (p, i) { return { id: 't' + i, jenis: 'tawaran', tanggal: '2026-11-24', pemasok: 'Pemasok ' + p, kelas: 'Kelas Satu', hargaPerKg: 12000 + i }; }) }], ['banding-2026-11']);
ok('pengingat mingguan berhenti sesudah 3 pemasok berharga (harga tawaran ikut dihitung)', !bcSumberPengingat('2026-11-26').some(function (p) { return p.jenis === 'banding'; }) && bcStatusMinggu('2026-11-26').cukup === true);
aturDengan([]);
var PB = bcSumberPengingat('2026-12-01'); var pb = PB.find(function (p) { return p.jenis === 'bandingBulan'; });
ok('pengingat bulanan: tanggal 1 Des → banding November (ada kedatangan, belum ditandai)', pb && pb.kunci === '2026-11' && pb.jatuh === '2026-12-01', J(PB));
ok('pengingat bulanan ditagih paling lama 7 hari (9 Des = tidak lagi)', !bcSumberPengingat('2026-12-09').some(function (p) { return p.jenis === 'bandingBulan'; }) && bcSumberPengingat('2026-12-08').some(function (p) { return p.jenis === 'bandingBulan'; }));
aturDengan([{ id: 'banding-2026-11', bulan: '2026-11', entri: [], dibanding: { tanggal: '2026-12-01', jam: '09:00', catatan: '' } }], ['banding-2026-11']);
ok('pengingat bulanan berhenti sesudah ditandai sudah dibanding', !bcSumberPengingat('2026-12-01').some(function (p) { return p.jenis === 'bandingBulan'; }));
aturDengan([{ id: 'bandingPemasok', minPemasok: 3, hariMinggu: 1, tanggalBulan: 5 }], ['bandingPemasok']);
ok('hari & tanggal pengingat = setelan owner (Senin · tanggal 5)', bcSumberPengingat('2026-11-26').find(function (p) { return p.jenis === 'banding'; }).jatuh === '2026-11-23' && bcSumberPengingat('2026-12-05').find(function (p) { return p.jenis === 'bandingBulan'; }).jatuh === '2026-12-05');
aturDengan([]);

// ==================== USUL TABLET (bentuk rules v21) ====================
var ben = { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben' };
var U = bcSusunUsul('tawaran', { pemasok: 'Pemasok Contoh E', kelas: 'Kelas Satu', hargaPerKg: '12.300', sampaiToko: true }, ben, W); var dU = U.dokumen && U.dokumen[0].data;
ok('usul tablet = SATU persetujuan: tindakan hargaBanding, menunggu, mintaUid penulis, jenis, harga bulat, kalimat ≤ 300, tanpa keputusan', U.dokumen.length === 1 && U.dokumen[0].koleksi === 'persetujuan' && dU.tindakan === 'hargaBanding' && dU.status === 'menunggu'
   && dU.mintaUid === 'uid-ben' && dU.jenis === 'tawaran' && dU.hargaPerKg === 12300 && typeof dU.teks === 'string' && dU.teks.length > 0 && dU.teks.length <= 300 && !('diputusPada' in dU) && dU.isi.pemasok === 'Pemasok Contoh E' && !('hargaPerKg' in dU.isi), J(dU));
ok('usul tablet: penjaga isian SAMA dengan owner (harga karung ditolak), tanpa akun ditolak', !!bcSusunUsul('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: '645000' }, ben, W).tolak && !!bcSusunUsul('tawaran', { pemasok: 'P X', kelas: 'K X', hargaPerKg: '12000' }, null, W).tolak);
pasok('persetujuan', [dU]);
ok('usul yang sama selagi menunggu tidak dikirim dua kali', /tidak dikirim dua kali/.test(bcSusunUsul('tawaran', { pemasok: 'Pemasok Contoh E', kelas: 'Kelas Satu', hargaPerKg: '12300', sampaiToko: true }, ben, W).tolak || '') && bcUsulMenunggu() === 1);
var PS = bcPasangUsul(dU, W); var ePS = PS.dokumen && PS.dokumen[0].data.entri.slice(-1)[0];
ok('setujui usul: catatan ditulis atas nama pengusul (oleh Ben, dariUsul) — isian dicek ulang', ePS && ePS.oleh === 'Ben Contoh' && ePS.dariUsul === dU.id && ePS.hargaPerKg === 12300 && ePS.sampaiToko === true && ePS.pemasok === 'Pemasok Contoh E', J(PS));
ok('setujui usul yang isiannya rusak (harga diubah jadi pecahan) ditolak', !!bcPasangUsul(Object.assign({}, dU, { hargaPerKg: 12300.5 }), W).tolak);
ok('kalimat papan dihitung ulang dari isian (bukan teks kiriman)', bcTeksUsul(Object.assign({}, dU, { teks: 'teks palsu' })).indexOf('Pemasok Contoh E') >= 0);
pasok('persetujuan', []);

// ==================== TARIK OTOMATIS (functions/acuan.js) ====================
var FA = FUNGSI_ACUAN();
var S1 = { data: [{ nama: 'Beras Medium SPHP Bulog', harga: 12500 }, { nama: 'Beras Premium', harga: 15500, tanggal: '25/11/2026' }, { nama: 'Beras Medium', harga: '13.100' }, { nama: 'Gula Pasir', harga: 18000 }] };
var H1 = FA.sisirHarga(S1, 'eceran', '2026-11-27');
ok('sisir: beras premium & medium dikenali (angka "13.100" terbaca), SPHP / Bulog / komoditas lain dilewati, tanggal dari jawaban atau tanggal tarik', H1.length === 2 && H1[0].mutu === 'premium' && H1[0].hargaPerKg === 15500 && H1[0].tanggal === '2026-11-25'
   && H1[1].hargaPerKg === 13100 && H1[1].tanggal === '2026-11-27' && H1.every(function (x) { return x.tebakTingkat && x.tingkat === 'eceran'; }), J(H1));
var H2 = FA.sisirHarga({ status: 'ok', data: { items: [{ commodity: 'Beras Medium', geomean_today: 13250.6, province_name: 'Wilayah Contoh' }] } }, 'produsen', '2026-11-27');
ok('sisir bentuk lain (bersarang, kunci inggris): wilayah terbawa, harga dibulatkan rupiah', H2.length === 1 && H2[0].hargaPerKg === 13251 && H2[0].wilayah === 'Wilayah Contoh', J(H2));
// bentuk jawaban Panel Harga yang TERLIHAT 26 Nov 2026 (angka contoh): today = hari ini, yesterday & yesterday_date = kemarin (tidak dipakai), 0 = belum ada data
var BAP = function (rows) { return { status: 'success', message: 'Berhasil mendapatkan data', data: rows, request_data: { level_harga_id: '3' } }; };
var bar = function (id, nama, today, kemarin) { return { id: id, name: nama, satuan: 'Rp./Kg', today: today, yesterday: kemarin, yesterday_date: '25-11-2026', gap: today - kemarin, gap_percentage: 0.1, gap_change: 'down', gap_color: 'green', background: 'https://contoh/ikon.png' }; };
var H3 = FA.sisirHarga(BAP([bar(1, 'Gula Pasir', 18000, 18100), bar(27, 'Beras Premium', 15800, 15900), bar(28, 'Beras Medium', 13400, 13500), bar(109, 'Beras SPHP', 12400, 12450), bar(165, 'Beras Medium Non SPHP', 14100, 14200)]), 'eceran', '2026-11-26', false);
ok('bentuk Panel Harga: harga HARI INI (today), bertanggal hari tarik — bukan yesterday_date; SPHP & Non SPHP dilewati; tingkat terbukti (bukan tebakan)', H3.length === 2 && H3[0].hargaPerKg === 15800 && H3[0].tanggal === '2026-11-26' && H3[1].hargaPerKg === 13400 && H3[1].mutu === 'medium'
   && H3.every(function (x) { return x.tebakTingkat === false && x.wilayah === 'nasional'; }), J(H3));
var H4 = FA.sisirHarga(BAP([bar(5, 'Beras Medium Penggilingan', 12900, 13000), bar(6, 'Beras Premium Penggilingan', 14600, 14700)]), 'produsen', '2026-11-26', false);
var H5 = FA.sisirHarga(BAP([bar(15, 'Beras Premium', 0, 0), bar(16, 'Beras Medium', 0, 0)]), 'grosir', '2026-11-26', true);
ok('level produsen (Penggilingan) terbaca; harga 0 = belum ada data → dilewati, bukan Rp0', H4.length === 2 && H4[0].mutu === 'medium' && H4[0].hargaPerKg === 12900 && H5.length === 0, J([H4, H5]));
ok('fungsi menarik tiga tingkat: eceran & produsen terbukti, grosir ditandai tebakan', J(FA.ACUAN_LEVEL.map(function (L) { return [L.id, L.tingkat, L.tebak]; })) === J([[3, 'eceran', false], [1, 'produsen', false], [2, 'grosir', true]]));
var D0 = FA.dokTarik([{ tingkat: 'eceran', json: { message: 'kosong' } }, { tingkat: 'produsen', galat: 'server menjawab 403' }], new Date('2026-11-26T23:00:00Z'));
ok('tarik tanpa harga dikenali = status gagal + pesan + potongan jawaban (bukan angka karangan); tanggal WIB', D0.status === 'gagal' && D0.harga.length === 0 && /403/.test(D0.pesan) && D0.contoh.indexOf('kosong') >= 0 && D0.tanggal === '2026-11-27', J(D0));
var D1 = FA.dokTarik([{ tingkat: 'eceran', json: S1 }], new Date('2026-11-27T00:00:00Z'));
aturDengan([D1]); var TR = bcTarik();
ok('hasil tarik dibaca layar sebagai USULAN (status ok, 2 harga, belum dipakai)', TR.ada && TR.status === 'ok' && TR.harga.length === 2 && !TR.harga[0].dipakai, J(TR));
var x0 = TR.harga[0]; var PK = susunCatatBanding('acuan', { tanggal: x0.tanggal, sumber: x0.sumber, tingkat: x0.tingkat, mutu: x0.mutu, wilayah: x0.wilayah, hargaPerKg: x0.hargaPerKg, otomatis: true }, W, 'Owner · tarik otomatis');
aturDengan([D1, dokAt(PK)], ['banding-2026-11']);
ok('Pakai satu harga tarik → tercatat sebagai acuan bertanda otomatis, lalu ditandai "sudah dicatat"', bcTarik().harga[0].dipakai === true && bcTarik().harga[1].dipakai === false && dokAt(PK).entri.slice(-1)[0].otomatis === true);
aturDengan([]);
ok('belum pernah tarik = kalimat jujur (fungsi belum dipasang), bukan daftar kosong diam', !bcTarik().ada && /belum pernah jalan/.test(bcTarik().kalimat));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

SKENARIO_B = r"""
var lulus = 0, gagal = [];
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 700) : '')); }
var J = function (x) { return JSON.stringify(x); };
var KINI = new Date('2026-11-26T15:00:00+07:00'); var nId = 80000;
var W = { tanggal: '2026-11-26', jam: '15:00', kini: '2026-11-26T08:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, []); });
['retur', 'produksiKemasan', 'penyesuaianKemasan', 'wadahLiteran', 'biayaBulanan', 'piutangMutasi', 'kasbonMutasi', 'stokBahanLiteran', 'pesanan', 'penjualan', 'utangPemasokMutasi', 'pemasokCatatan', 'persetujuan', 'pesananPemasok', 'stokBahanKemasan', 'penyesuaianStok', 'pengeluaranHarian', 'tutupHari'].forEach(function (n) { pasok(n, []); });
pasok('batchMasuk', JSON.parse(J(BDK.batchMasuk))); pasok('aturanToko', JSON.parse(J(ATUR)));
setelSumber('cadangan', 'kotak pasir');
// papan Persetujuan memutus usul banding lewat pintu yang SAMA dengan setelan lain (susunPutusPersetujuan)
var U = bcSusunUsul('acuan', { sumber: 'Panel Harga Bapanas', tingkat: 'grosir', mutu: 'medium', hargaPerKg: '13100' }, { uid: 'uid-ben', nama: 'Ben Contoh', peran: 'ben' }, W); var dU = U.dokumen[0].data;
ok('akses.js usulBandingSah = cermin rules v21 untuk usul yang disusun (dan menolak harga karung / atas nama lain)', usulBandingSah(dU, 'uid-ben') === true && usulBandingSah(Object.assign({}, dU, { hargaPerKg: 645000 }), 'uid-ben') === false && usulBandingSah(dU, 'uid-lain') === false
   && usulBandingSah(Object.assign({}, dU, { alasanTolak: 'x' }), 'uid-ben') === false, J(dU));
pasok('persetujuan', [dU]);
var P = ssPersetujuan(KINI); var bP = P.menunggu.find(function (m) { return m.id === String(dU.id); });
ok('papan Persetujuan: usul banding tampil satu per satu (tidak ikut setujui sekaligus), kalimat dihitung ulang', bP && bP.sekaligus === false && bP.n === 0 && /Usul harga acuan/.test(bP.namaTindakan) && bP.teks.indexOf('Panel Harga Bapanas') >= 0, J(bP));
var SJ = susunPutusPersetujuan(String(dU.id), true, '', W);
var dP = SJ.dokumen && SJ.dokumen.find(function (x) { return x.koleksi === 'persetujuan'; }); var dB = SJ.dokumen && SJ.dokumen.find(function (x) { return x.koleksi === 'aturanToko'; });
ok('Setujui = SATU kiriman: persetujuan disetujui + catatan banding bulan itu (atas nama pengusul)', SJ.dokumen && SJ.dokumen.length === 2 && dP.data.status === 'disetujui' && dB.data.id === 'banding-2026-11' && dB.data.entri.slice(-1)[0].dariUsul === String(dU.id) && dB.data.entri.slice(-1)[0].oleh === 'Ben Contoh', J(SJ));
ok('Tolak tanpa alasan ditolak; dengan alasan = persetujuan ditolak saja (tidak ada catatan)', !!susunPutusPersetujuan(String(dU.id), false, '', W).tolak && susunPutusPersetujuan(String(dU.id), false, 'harga salah ketik', W).dokumen.length === 1);
pasok('persetujuan', []);
// pengingat masuk ke sumber Pengingat Menu (jenis banding & bandingBulan terdaftar, bawaan nyala, penerima)
var G = ssSumberPengingat(KINI, {}); var g = G.find(function (p) { return p.jenis === 'banding'; });
ok('ssSumberPengingat memuat pengingat mingguan banding (jatuh Jumat 27 Nov)', g && g.jatuh === '2026-11-27', J(G.filter(function (p) { return /banding/.test(p.jenis); })));
ok('jenis pengingat banding & bandingBulan terdaftar + bawaan nyala & penerima', SS_JENIS_PENGINGAT.some(function (j) { return j.id === 'banding'; }) && SS_JENIS_PENGINGAT.some(function (j) { return j.id === 'bandingBulan'; })
   && ssAtur('pengingat').nyala.banding === true && J(ssAtur('pengingat').ke.banding) === J(['Owner', 'Ben']) && J(ssAtur('pengingat').ke.bandingBulan) === J(['Owner']));
var GB = ssSumberPengingat(new Date('2026-12-01T09:00:00+07:00'), {});
ok('ssSumberPengingat tanggal 1 Des memuat banding bulan November', GB.some(function (p) { return p.jenis === 'bandingBulan' && p.kunci === '2026-11'; }));
print(JSON.stringify({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) pasok(n, CAD[n]); });
var kini = new Date(Date.now()); var iso = hariIniIso(kini); var out = { akhir: iso, bulan: [], galat: [] };
var aman = function (nama, f) { try { return f(); } catch (e) { out.galat.push(nama + ': ' + e + ' ' + String(e.stack || '').slice(0, 200)); return null; } };
['2026-09', '2026-10', '2026-11'].forEach(function (k) { if (k > iso.slice(0, 7)) return; var B = aman('bulan ' + k, function () { return bdBulan(k, kini); });
  var R = aman('rapor ' + k, function () { return bdRapor(k, kini); });
  var tutup = !!B && B.kelas.every(function (g) { return g.baris.every(function (x) { return x.hargaKg + x.bongkarKg + x.timbangKg === x.modalKg && x.modalKg + x.mutuKg + x.susutKg === x.layakKg; }); });
  out.bulan.push({ key: k, menutup: B ? B.menutup : null, pecahMenutup: tutup, pemasok: B ? B.nPemasok : null, kelas: B ? B.kelas.length : null, baris: B ? B.nBaris : null, rapor: R ? R.pemasok.length : null }); });
var M = aman('minggu', function () { return bdMinggu(bcSenin(iso), kini); }); out.minggu = M ? [M.senin, M.nPemasok, M.kelas.length] : null;
var T = aman('tren', function () { return bdTren(kini, 6); }); out.tren = T ? T.kelas.length : null;
var A = aman('acuan', function () { return bdAcuan(kini); }); out.acuan = A ? A.acuan.length : null;
var P = aman('pengingat', function () { return bcSumberPengingat(iso); }); out.pengingat = P ? P.map(function (p) { return p.jenis + ' ' + p.jatuh; }) : null;
var C = aman('calon', function () { return bdCalon(kini); }); out.calon = C ? [C.kelas.length, C.pemasok.length] : null;
print(JSON.stringify(out));
"""

STATIS = [
    ('Harga & Pemasok: keluarga keempat Banding pemasok + lima tab + lembar catat / atur', 'harga', ["['banding', 'Banding pemasok']", "s.keluarga === 'banding' ? gambarBanding(s, L)", 'function gambarBdBulan(s)', 'function gambarBdMinggu(s)',
     'function gambarBdRapor(s)', 'function gambarBdAcuan(s)', 'function gambarBdTren()', "BC.susunCatatBanding(d.jenis, d, waktu(), 'Owner')", 'BC.susunAturBanding(', 'BC.susunTandaiBanding(bulan', "'bdCatat', 'aturBd'"]),
    ('tab Banding = BD_TAB (lima tab)', 'bd', ["export const BD_TAB = [['minggu', 'Minggu ini'], ['bulan', 'Banding bulan'], ['rapor', 'Rapor pemasok'], ['acuan', 'Harga acuan'], ['tren', 'Tren modal']];"]),
    ('tablet: kartu usul hanya Penjaga laci, kirim lewat bcSusunUsul', 'menu', ["${akunM.peran === 'ben' ? kartuUsulBanding(s, { akun: akunM }) : ''}", 'aksiUsulBanding({ set, st, tulis, akun: opsi.akun, waktu })', "['ub', (v) =>"]),
    ('panel tablet menulis usul saja', 'panel', ['BC.bcSusunUsul(d.jenis, d, ak(), waktu())']),
    ('Menu: baris Banding pemasok menuju keluarga banding', 'menuL', ["{ nama: 'Banding pemasok',", "tujuan: { ke: 'harga', keluarga: 'banding'"]),
    ('sistem-logika: pengingat banding & papan Persetujuan', 'sl', ["import { bcSumberPengingat, bcPasangUsul, bcTeksUsul, BC_TINDAKAN } from './banding-catat-logika.js';", 'bcSumberPengingat(iso).forEach((p) => out.push(p));',
     "setuju && m.tindakan === BC_TINDAKAN ? bcPasangUsul(m, w)", "if (m.tindakan === BC_TINDAKAN) Object.assign(b, { n: 0, sekaligus: false"]),
    ('akses.js: usul banding Penjaga laci saja (cermin rules v21)', 'ak', ["if (P !== 'ben' || !usulBandingSah(d, akun.uid))"]),
    ('rules v21: fungsi usul di create persetujuan', 'rules', ["|| stafUsulBanding(['ben']);", 'function stafUsulBanding(peranBoleh)', 'ATURAN FIRESTORE v21 FINAL']),
    ('riwayat setelan: catatan banding & hasil tarik bukan setelan', 'rsd', ["'aturanToko/banding-', 'aturanToko/acuanTarik'"]),
    ('riwayat setelan: judul Banding pemasok & acuanTarik dokumen sistem', 'rsl', ["bandingPemasok: 'Banding pemasok'", 'acuanTarik: true']),
    ('fungsi server: tarik acuan terjadwal Jumat 06.00 WIB menulis aturanToko/acuanTarik saja', 'fi', ["exports.tarikAcuan = onSchedule({ schedule: 'every friday 06:00', timeZone: 'Asia/Jakarta'", "collection('aturanToko').doc('acuanTarik').set(d)"]),
    ('notifikasi HP: judul usul banding', 'fp', ["hargaBanding: 'Usul harga tawaran / acuan' };   // + banding pemasok"]),
    ('stok-catat: tanda AWAS terstruktur (satu penilai ambang)', 'ck', ["const tanda = (id) => { if (hasil.tanda.indexOf(id) < 0) hasil.tanda.push(id); };", "hasil.awas.push(teks); tanda(id); }); }"]),
    ('bundel uji: banding-catat ikut otomatis di belakang sistem-logika', 'bundel', ["BC_PEMAKAI = ('sistem-logika.js', 'banding-pemasok-logika.js')"]),
    ('peta akses: usul banding diukur sebagai kiriman staf', 'peta', ["catat('usul banding', p, 'usul harga tawaran pemasok (satu persetujuan menunggu)', kirim(p, UT.dokumen));"]),
    ('CSS: gerak masuk bergiliran + batang tren + reduced-motion', 'css', ['@keyframes bd-masuk', '@keyframes bd-batang', '.layar-harga .bd-urut', 'prefers-reduced-motion: reduce) { .layar-harga .bd-kelas']),
    ('CI: langkah uji banding pemasok', 'pages', ['python3 alat-uji/uji_banding_pemasok.py && python3 alat-uji/uji_banding_pemasok.py --kontrol']),
    ('BACA-DULU: bagian Banding pemasok', 'baca', ['## Banding pemasok (owner 26 Nov 2026)']),
]

RUSAK = [
    ('kg diterima pakai nota walau ditimbang', 'A', BD, "else if (cek.timbangKg !== null && !cek.masalah) { kgNyata = bdB(cek.timbangKg - bdReturBaris(b, m.merk)); asal = cek.perkiraan ? 'sampel' : 'timbang'; }", "else if (false) { kgNyata = 0; }"),
    ('retur tidak dikurangi dari hasil timbang', 'A', BD, "kgNyata = bdB(cek.timbangKg - bdReturBaris(b, m.merk));", "kgNyata = bdB(cek.timbangKg);"),
    ('layak jual tanpa susut gudang', 'A', BD, "const layakKg = (s.uang + s.bongkar + s.pot) / (s.kgNyata * (1 - (pct || 0) / 100));", "const layakKg = (s.uang + s.bongkar + s.pot) / s.kgNyata;"),
    ('layak jual tanpa potongan mutu', 'A', BD, "const layakKg = (s.uang + s.bongkar + s.pot) / (s.kgNyata * (1 - (pct || 0) / 100));", "const layakKg = (s.uang + s.bongkar) / (s.kgNyata * (1 - (pct || 0) / 100));"),
    ('pecahan timbang dihitung sendiri (tidak menutup)', 'A', BD, "const bdTutup = (total, a, b) => { const T = Math.round(total), A = Math.round(a), B = Math.round(b); return [A, B, T - A - B, T]; };",
     "const bdTutup = (total, a, b) => { const T = Math.round(total), A = Math.round(a), B = Math.round(b); return [A, B, Math.round(total - a - b) + 1, T]; };"),
    ('urutan termahal dulu', 'A', BD, ".sort((a, b) => a.layakKg - b.layakKg || (a.jenis === 'beli' ? -1 : 1) || a.pemasok.localeCompare(b.pemasok));", ".sort((a, b) => b.layakKg - a.layakKg);"),
    ('tawaran tidak dihitung sebagai pemasok', 'A', BD, "const kp = kunciPelanggan(e.pemasok); semuaPem[kp] = semuaPem[kp] || e.pemasok;", "const kp = kunciPelanggan(e.pemasok);"),
    ('ongkir tawaran tidak disebut dianggap Rp0', 'A', BD, "const ongkir = e.sampaiToko ? 0 : tahu ? Number(e.ongkirPerKg) || 0 : R.ongkirKg;", "const ongkir = e.sampaiToko ? 0 : Number(e.ongkirPerKg) || 0;"),
    ('penjaga selalu menutup', 'A', BD, "const menutup = Math.abs(nilai - sapu) < 0.5;", "const menutup = true;"),
    ('nilai bal tidak dihitung penjaga (bentuk rusak yang harus ketahuan)', 'A', BD, "dilewati += 1; nilaiLewat += uang + bongkar; return; }\n      const ikut", "dilewati += 1; nilaiLewat += uang; return; }\n      const ikut"),
    ('minggu mulai Minggu, bukan Senin', 'A', BC, "export const bcSenin = (iso) => bcTambahHari(iso, -((bcHariMinggu(iso) + 6) % 7));", "export const bcSenin = (iso) => bcTambahHari(iso, -bcHariMinggu(iso));"),
    ('harga pecahan dibulatkan diam-diam', 'A', BC, "if (/^\\d+$/.test(t)) return Number(t); if (/^\\d{1,3}(\\.\\d{3})+$/.test(t)) return Number(t.replace(/\\./g, '')); return NaN;",
     "if (/^\\d+$/.test(t)) return Number(t); if (/^\\d{1,3}(\\.\\d{3})+$/.test(t)) return Number(t.replace(/\\./g, '')); return Math.round(Number(t.replace(',', '.')));"),
    ('harga karung (> 100.000) lolos', 'A', BC, "h >= BC_BATAS.hargaMin && h <= BC_BATAS.hargaMaks)) return { tolak: 'Harga per kg", "h >= BC_BATAS.hargaMin)) return { tolak: 'Harga per kg"),
    ('kembar tidak ditolak', 'A', BC, "const kembar = entri.find((e) => e && bcSama(e, data)); if (kembar) return", "const kembar = null; if (kembar) return"),
    ('pengingat mingguan jatuh Senin, bukan hari setelan', 'A', BC, "const jatuh = bcTambahHari(senin, (A.hariMinggu + 6) % 7);", "const jatuh = senin;"),
    ('pengingat mingguan tidak menghitung harga tawaran', 'A', BC, "bcEntri(dari, sampai).forEach((e) => { if (e.jenis === 'tawaran') { const k = kunciPelanggan(e.pemasok); if (!out[k]) out[k] = e.pemasok; } });", ""),
    ('pengingat bulanan tidak berhenti sesudah ditandai', 'A', BC, "if (!bcDibanding(blnLalu) && iso >=", "if (iso >="),
    ('pengingat bulanan abadi (tanpa batas 7 hari)', 'A', BC, " && bcHariKe(iso) - bcHariKe(jatuhB) <= BC_SUSUL &&", " &&"),
    ('usul tanpa mintaUid', 'A', BC, "mintaUid: String(akun.uid), dari:", "dari:"),
    ('setujui usul tanpa jejak pengusul', 'A', BC, "{ oleh: bcBersih(m.dari) || 'tablet', dariUsul: String(m.id) }", "{ oleh: 'Owner' }"),
    ('setujui usul tanpa cek ulang isian', 'A', BC, "const B = bcBacaIsi(m.jenis, Object.assign({}, m.isi || {}, { hargaPerKg: m.hargaPerKg, otomatis: false }), w.tanggal); if (B.tolak) return { tolak: 'Usul tidak bisa dipasang: ' + B.tolak };",
     "const B = { data: Object.assign({ jenis: m.jenis, hargaPerKg: m.hargaPerKg }, m.isi || {}) };"),
    ('potongan mutu dibaca dari teks AWAS, bukan tanda', 'A', BD, "const tanda = (cek.tanda || []).slice();", "const tanda = (cek.awas || []).map(() => 'kadarAir').slice(0, 0);"),
    ('tmBaris tanpa tanda kadar air', 'A', CK, "hasil.awas.push('kadar air ' + tmD(hasil.kadarAir) + ' % > maks ' + tmD(A.kadarAirMaks) + ' %'); tanda('kadarAir'); }", "hasil.awas.push('kadar air ' + tmD(hasil.kadarAir) + ' % > maks ' + tmD(A.kadarAirMaks) + ' %'); }"),
    ('sisir acuan ikut SPHP', 'A', FA, "if (m && !/sphp|bulog/i.test(nama)) {", "if (m) {"),
    ('tarik tanpa harga ditulis ok', 'A', FA, "status: harga.length ? 'ok' : 'gagal'", "status: 'ok'"),
    ('tarik memakai tanggal kemarin (yesterday_date) untuk harga hari ini', 'A', FA, "if (!tanggal && KUNCI_TANGGAL.test(k) && !KUNCI_KEMARIN.test(k) && (typeof v === 'string')) tanggal = isoDari(v);", "if (!tanggal && KUNCI_TANGGAL.test(k) && (typeof v === 'string')) tanggal = isoDari(v);"),
    ('tarik memakai harga kemarin', 'A', FA, "if ('today' in o) harga = angkaHarga(o.today);", "if ('yesterday' in o) harga = angkaHarga(o.yesterday);"),
    ('tingkat terbukti tetap ditandai tebakan', 'A', FA, "tebakTingkat: tebak !== false,", "tebakTingkat: true,"),
    ('papan Persetujuan memasang usul banding sekaligus', 'B', SL, "if (m.tindakan === BC_TINDAKAN) Object.assign(b, { n: 0, sekaligus: false,", "if (m.tindakan === BC_TINDAKAN) Object.assign(b, { n: 0, sekaligus: true,"),
    ('setujui usul banding tidak menulis catatan', 'B', SL, " : setuju && m.tindakan === BC_TINDAKAN ? bcPasangUsul(m, w) : null;", " : null;"),
    ('pengingat banding tidak masuk sumber Pengingat', 'B', SL, "  bcSumberPengingat(iso).forEach((p) => out.push(p));\n", ""),
    ('akses.js membolehkan harga karung', 'B', AK, "&& d.hargaPerKg >= 1000 && d.hargaPerKg <= 100000 &&", "&& d.hargaPerKg >= 1000 &&"),
]
RUSAK_STATIS = [
    ('tablet: kartu usul tampil untuk karyawan', 'menu', "${akunM.peran === 'ben' ? kartuUsulBanding(s, { akun: akunM }) : ''}", "${kartuUsulBanding(s, { akun: akunM })}"),
    ('keluarga Banding hilang dari Harga & Pemasok', 'harga', "['banding', 'Banding pemasok']", "['bandingX', 'Banding pemasok']"),
    ('langkah CI dicabut', 'pages', 'python3 alat-uji/uji_banding_pemasok.py && python3 alat-uji/uji_banding_pemasok.py --kontrol', 'python3 alat-uji/uji_banding_pemasok.py'),
    ('hasil tarik ikut riwayat setelan', 'rsd', "'aturanToko/banding-', 'aturanToko/acuanTarik'", "'aturanToko/banding-'"),
]


def fungsi_acuan(teks_fa):
    """functions/acuan.js (CommonJS) dibungkus supaya jalan di jsc: FUNGSI_ACUAN() → module.exports."""
    return 'function FUNGSI_ACUAN() { var module = { exports: {} }; var exports = module.exports; (function (module, exports) {\n' + teks_fa + '\n})(module, exports); return module.exports; }\n'


def bundel_js(teks, modul):
    js = bundel_baru.PRELUDE + ''.join('\n// ===== ' + p + ' =====\n' + bundel_baru.polos(teks[p]) for p in modul)
    if modul is MODUL_A: js = uji_kunci_periode.satu_lingkup(js)   # bundel Dasbor + laporan (nama kembar diselesaikan); bundel sistem = bundel uji_faktur apa adanya
    BL = uji_ringkasan_baru.BON_PEMASOK_LAMA
    if js.count(BL) == 1: js = js.replace(BL, BL.replace('susunBon(', 'bpSusunBon('))
    return js


def jalan_satu(teks, modul, skenario):
    js = bundel_js(teks, modul)
    jam = "var __KINI = new Date('2026-11-26T15:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(jam + js + '\n' + fungsi_acuan(teks[FA]) + 'var KOTAK = ' + json.dumps(uji_jual_baru.KOTAK) + ';\nvar BDK = ' + json.dumps(KOTAK_BD) + ';\nvar ATUR = ' + json.dumps(ATUR) + ';\n' + skenario); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
    if r.returncode != 0 or not out.startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(out); return h['lulus'], h['gagal']


def jalan(teks, bagian=('A', 'B')):
    l, g = 0, []
    if 'A' in bagian: a, b = jalan_satu(teks, MODUL_A, SKENARIO_A); l += a; g += ['[hitung] ' + x for x in b]
    if 'B' in bagian: a, b = jalan_satu(teks, MODUL_B, SKENARIO_B); l += a; g += ['[sistem] ' + x for x in b]
    return l, g


def statis(src):
    g = []
    for nama, berkas, daftar in STATIS:
        kurang = [x for x in daftar if x not in src[berkas]]
        if kurang: g.append(nama + ' → tidak ketemu: ' + kurang[0][:120])
    bd, bc = src['bd'], src['bc']
    if 'document.' in bd + bc or 'tulisDokumen' in bd + bc or 'window.' in bd + bc: g.append('logika banding menyentuh DOM / menulis langsung — modul ini cuma menyusun')
    if 'koleksi:' in bd: g.append('banding-pemasok-logika menulis dokumen — modul hitungan wajib baca saja')
    if sorted(set(__import__('re').findall(r"koleksi: '(\w+)'", bc))) != ['aturanToko', 'persetujuan']: g.append('banding-catat-logika menulis koleksi selain aturanToko & persetujuan')
    if __import__('re').search(r"^import .* from '\./(?!banding-catat-logika)", bc, __import__('re').M): g.append('banding-catat-logika bukan modul DAUN (mengimpor layar lain) — sistem-logika tidak boleh menarik mesin laporan')
    return len(STATIS) + 4 - len(g), g


def muat():
    semua = list(dict.fromkeys(MODUL_A + MODUL_B + [FA]))
    return dict((p, open(os.path.join(AKAR, p), encoding='utf-8').read()) for p in semua), dict((k, open(os.path.join(AKAR, v), encoding='utf-8').read()) for k, v in SUMBER.items())


if __name__ == '__main__':
    teks, src = muat()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, bagian, berkas, a, b in RUSAK:
            if teks[berkas].count(a) != 1: print('KONTROL BASI  ' + nama + ' (' + str(teks[berkas].count(a)) + '×)'); kode = 3; continue
            T = dict(teks); T[berkas] = T[berkas].replace(a, b)
            l, g = jalan(T, (bagian,))
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
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write("var __KINI = new Date('%sT20:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n" % tgl + bundel_js(teks, MODUL_A) + '\nvar CAD = ' + open(cad[-1], encoding='utf-8').read() + ';\n' + ASAP); pth = f.name
        r = subprocess.run([JSC, pth], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(pth)
        out = r.stdout.strip().split('\n')[-1] if r.stdout.strip() else ''
        if r.returncode != 0 or not out.startswith('{'): print('ASAP DATA TOKO: JSC JATUH ' + (r.stderr or r.stdout)[-600:]); g.append('asap')
        else:
            h = json.loads(out); beres = not h['galat'] and h['bulan'] and all(x['menutup'] and x['pecahMenutup'] for x in h['bulan']) and h['minggu'] is not None and h['tren'] is not None
            print('ASAP DATA TOKO (%s, hari terakhir %s): %s — %s' % (os.path.basename(cad[-1]), h['akhir'], 'MENUTUP' if beres else 'GAGAL', json.dumps(h, ensure_ascii=False)))
            if not beres: g.append('asap data toko: penjaga banding tidak menutup, pecahan tidak menutup, atau galat')
    sys.exit(1 if g or gs else 0)
