#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_buku_ukuran.py — putaran 28: KARUNG 50 kg & 25 kg MEREK YANG SAMA = BUKU MASING-MASING (owner 28 Sep 2026).
  · Keputusan owner: buku merek lama ("Angsa") tetap buku karung 50 kg; karung 25 kg merek yang datang dua ukuran punya buku "Angsa 25 kg"
    (baris batch bertanda indukUkuran); berlaku SEMUA merek dua ukuran; stok lama dipisah dengan MENGHITUNG karung 25 kg utuh (modal rata-rata ikut).
  · Barang masuk: baris 25 kg merek yang punya karung 50 kg → dibukukan otomatis ke "Merek 25 kg"; merek yang cuma 25 kg tetap satu buku.
  · Jual / retur / katalog HP kasir: karung 25 kg dari bukunya sendiri, harga = katalog merek induk ukuran itu; induknya tidak menawarkan 25 kg lagi.
KOTAK PASIR (ANGKA CONTOH), jam dikunci 20 Sep 2026 10:00 WIB. Cadangan toko di _privat/: daftar merek dua ukuran; pemisahan Angsa dengan hitungan
contoh tidak menggeser nilai stok maupun laba bulan itu.

    python3 alat-uji/uji_buku_ukuran.py            → N lulus · 0 gagal
    python3 alat-uji/uji_buku_ukuran.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_wadah_bernama  # noqa: E402
import uji_wadah_stok_sendiri as UW  # noqa: E402

brs = uji_wadah_bernama.brs
KOTAK = {
  # b1: Angsa datang DUA ukuran (4 × 50 @13.000 + 6 × 25 @13.400) — satu buku lama; Perahu cuma 50 kg; Ketan Paris cuma 25 kg
  'batchMasuk': [{'id': 'b1', 'tanggal': '2026-09-10', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0,
                  'merkList': [brs(1, 'Angsa', 4, 13000), brs(2, 'Angsa', 6, 13400, 25), brs(3, 'Perahu', 2, 14000), brs(4, 'Ketan Paris', 3, 20000, 25)]}],
  'katalogHargaKemasan': [{'id': 'Angsa|50', 'merk': 'Angsa', 'ukuran': 50, 'hargaPerUnit': 760000}, {'id': 'Angsa|25', 'merk': 'Angsa', 'ukuran': 25, 'hargaPerUnit': 380000}],
  'katalogHargaKarung': [{'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 15200}, {'id': 'Perahu', 'merk': 'Perahu', 'hargaPerKg': 15600}, {'id': 'Ketan Paris', 'merk': 'Ketan Paris', 'hargaPerKg': 22000}],
}

# audit 39b no. 35: kedatangan Ketan Putih 25 kg (dipasok di tengah skenario, sesudah Ketan Putih 50 kg) — merek per liter yang datang dua ukuran
B8 = {'id': 'b8', 'tanggal': '2026-09-19', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'Ketan Putih', 2, 18500, 25)]}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-20', jam: '10:00', kini: '2026-09-20T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var s0 = function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return s; };
var karung = function () { return susunRak(s0()).karung.map(function (c) { return c.kunci + '|' + c.berat + '|' + c.harga; }).sort(); };
var buku = function (m) { return (hitungStokKarungPerMerk()[m] || { sisaKg: 0 }).sisaKg; };
var B2 = function (n) { return Math.round(n * 100) / 100; };
var nilai = function () { var st = hitungStokKarungPerMerk(); var v = 0; Object.keys(st).forEach(function (m) { v += st[m].sisaKg * st[m].hppTerakhirPerKg; }); return Math.round(v); };
var dok = function (R, k) { return (R.dokumen || []).filter(function (d) { return d.koleksi === k; }).map(function (d) { return d.data; }); };

ok('sebelum: buku Angsa campur 50 & 25 kg (350 kg) — rak menawarkan Angsa 50 & 25 kg dari buku yang sama; calon pisah = Angsa saja (Perahu cuma 50, Ketan Paris cuma 25)',
  buku('Angsa') === 350 && J(karung()) === J(['Angsa|25|380000', 'Angsa|50|760000', 'Ketan Paris|25|550000', 'Perahu|50|780000']) && J(ckCalonPisahUkuran().map(function (x) { return x.merk; })) === J(['Angsa']), J([karung(), ckCalonPisahUkuran()]));

// ---- BARANG MASUK: baris 25 kg merek yang punya karung 50 kg → buku 'Merek 25 kg'
var draf = { id: null, tanggal: '2026-09-20', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', bongkar: '', alasan: '', baris: [
  { merk: 'Angsa', jumlahKarung: '2', beratKarung: 25, hargaPerKg: '13500' }, { merk: 'Angsa', jumlahKarung: '1', beratKarung: 50, hargaPerKg: '13000' },
  { merk: 'Ketan Paris', jumlahKarung: '2', beratKarung: 25, hargaPerKg: '20000' }, { merk: 'Perahu', jumlahKarung: '2', beratKarung: 25, hargaPerKg: '14200' }] };
var HM = hitungMasuk(draf);
ok('barang masuk: Angsa 25 → "Angsa 25 kg", Angsa 50 → "Angsa", Ketan Paris 25 (cuma 25 kg) → "Ketan Paris", Perahu 25 (punya 50 kg) → "Perahu 25 kg"',
  J(HM.baris.map(function (b) { return [b.merkSimpan, b.indukUkuran]; })) === J([['Angsa 25 kg', 'Angsa'], ['Angsa', ''], ['Ketan Paris', ''], ['Perahu 25 kg', 'Perahu']]) && !HM.bermasalah.length, J(HM.baris.map(function (b) { return [b.merkSimpan, b.indukUkuran, b.masalah]; })));
var SM = susunSimpanMasuk(draf, W, true); var bm = dok(SM, 'batchMasuk')[0] || { merkList: [] };
ok('kedatangan tersimpan: baris 25 kg yang dipisah bertanda indukUkuran, baris lain bentuk lama (tanpa kolom baru)',
  !SM.tolak && J(bm.merkList.map(function (r) { return [r.merk, r.beratKarung, r.indukUkuran || '']; })) === J([['Angsa 25 kg', 25, 'Angsa'], ['Angsa', 50, ''], ['Ketan Paris', 25, ''], ['Perahu 25 kg', 25, 'Perahu']])
  && bm.merkList.filter(function (r) { return !r.indukUkuran; }).every(function (r) { return !('indukUkuran' in r); }), J([SM.tolak, bm.merkList]));
terapkanKeCache(SM.dokumen || []);
ok('sesudah kedatangan: rak — Angsa cuma 50 kg; "Angsa 25 kg" dari bukunya sendiri Rp380.000 (katalog Angsa 25); "Perahu 25 kg" Rp390.000 (per kg Perahu × 25); induk tidak menawarkan 25 kg',
  J(karung()) === J(['Angsa 25 kg|25|380000', 'Angsa|50|760000', 'Ketan Paris|25|550000', 'Perahu 25 kg|25|390000', 'Perahu|50|780000']), J(karung()));
var c25 = susunRak(s0()).karung.find(function (c) { return c.kunci === 'Angsa 25 kg'; });
ok('chip karung 25 kg: nama tampil merek induk, sisa 2 karung (buku sendiri 50 kg), jenis beras ikut induk', !!c25 && c25.nama === 'Angsa' && c25.sisa === 2 && jbMerkChip(c25) === 'Angsa', J(c25));
var HM2 = hitungMasuk({ id: null, tanggal: '2026-09-20', pemasok: 'X', caraBayar: 'tunai', bongkar: '', baris: [{ merk: 'Angsa 25 kg', jumlahKarung: '1', beratKarung: 25, hargaPerKg: '13500' }] });
ok('nama buku ukuran yang DIKETIK di barang masuk ditolak dengan kalimat (tulis mereknya, bukunya dipilih otomatis)', /dipilih otomatis/.test(HM2.baris[0].masalah) && calonMerkMasuk().indexOf('Angsa 25 kg') < 0, J([HM2.baris[0].masalah, calonMerkMasuk()]));
var DK = drafDariKedatangan(bm.id); var HK = hitungMasuk(Object.assign({}, DK, { alasan: 'salah ketik' }));
ok('koreksi kedatangan yang sudah dipisah: nama tetap, tanda indukUkuran tetap, tidak dianggap salah', !HK.bermasalah.length && J(HK.baris.map(function (b) { return [b.merkSimpan, b.indukUkuran]; })) === J([['Angsa 25 kg', 'Angsa'], ['Angsa', ''], ['Ketan Paris', ''], ['Perahu 25 kg', 'Perahu']]),
  J(HK.baris.map(function (b) { return [b.merkSimpan, b.indukUkuran, b.masalah]; })));

// ---- PISAHKAN STOK LAMA (hitung karung 25 kg utuh)
ok('Angsa masih calon pisah (stok lama 6 karung 25 kg masih di buku Angsa); Perahu bukan (25 kg-nya sudah langsung ke bukunya)', J(ckCalonPisahUkuran().map(function (x) { return x.merk; })) === J(['Angsa']), J(ckCalonPisahUkuran()));
ok('pisah tanpa hitungan / bukan bilangan bulat / melebihi buku DITOLAK', !!ckSusunPisahUkuran('Angsa', '', W, true).tolak && !!ckSusunPisahUkuran('Angsa', '2,5', W, true).tolak && !!ckSusunPisahUkuran('Angsa', '20', W, true).tolak);
var P1 = ckSusunPisahUkuran('Angsa', '5', W, false);
ok('pisah minta ketukan kedua dengan kalimat', P1.perluYakin === 'pisah' && /5 karung 25 kg/.test(P1.tolak), J(P1));
var v0 = nilai(), laba0 = hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih, a0 = buku('Angsa'), a25 = buku('Angsa 25 kg');
var P = ckSusunPisahUkuran('Angsa', '5', W, true); var pp = dok(P, 'produksiKemasan');
ok('pisah 5 karung: satu pindah buku Angsa → "Angsa 25 kg" 125 kg bertanda pisahUkuran (buku 25 kg sudah lahir lewat kedatangan — tanpa batch lahir)',
  !P.tolak && pp.length === 1 && J(pp[0].sumberList) === J([{ merk: 'Angsa', kg: 125 }]) && pp[0].merkTujuan === 'Angsa 25 kg' && J(pp[0].pisahUkuran) === J({ induk: 'Angsa', berat: 25, karung: 5 }) && !dok(P, 'batchMasuk').length, J([P.tolak, pp]));
terapkanKeCache(P.dokumen || []);
ok('sesudah pisah: Angsa −125, Angsa 25 kg +125 (7 karung), nilai stok & laba tetap, Angsa bukan calon lagi',
  B2(buku('Angsa') - a0) === -125 && B2(buku('Angsa 25 kg') - a25) === 125 && (susunRak(s0()).karung.find(function (c) { return c.kunci === 'Angsa 25 kg'; }) || {}).sisa === 7 && Math.abs(nilai() - v0) <= 1
  && hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih === laba0 && !ckCalonPisahUkuran().length, J([buku('Angsa') - a0, buku('Angsa 25 kg') - a25, nilai(), v0]));

// ---- JUAL, RETUR, KATALOG, HARGA, BUKA KARUNG
var s = s0(); var c25j = susunRak(s0()).karung.find(function (c) { return c.kunci === 'Angsa 25 kg'; }); var rk = c25j ? masukkan(Object.assign({}, s, { pilih: c25j }), 1) : {}; s = Object.assign({}, s, { keranjang: rk.keranjang || [], urutBaris: rk.urutBaris });
var N = simpanNota(Object.assign({}, s, { cara: 'QRIS' }), W); var nj = dok(N, 'penjualan');
ok('jual 1 karung Angsa 25 kg: merkSumber "Angsa 25 kg", 25 kg, Rp380.000, modal = modal buku 25 kg × 25', !N.tolak && nj.length === 1 && nj[0].merkSumber === 'Angsa 25 kg' && nj[0].totalKg === 25 && nj[0].hargaTotal === 380000
  && nj[0].hppTotalSaatJual === Math.round(hitungStokKarungPerMerk()['Angsa 25 kg'].hppTerakhirPerKg * 25), J([N.tolak, nj]));
var R = daftarBarangRetur().karung.map(function (x) { return x.kunci; }).sort();
ok('retur tanpa nota: Angsa 50, Angsa 25 kg 25 — tidak ada lagi "Angsa 25" di buku induk', R.indexOf('Angsa|50') >= 0 && R.indexOf('Angsa 25 kg|25') >= 0 && R.indexOf('Angsa|25') < 0 && R.indexOf('Angsa 25 kg|50') < 0, J(R));
var kk = kkIsi(); var km = function (m) { return kk.merkKarung.find(function (x) { return x.merk === m; }); };
ok('katalog HP kasir: Angsa tanpa karung 25 kg; "Angsa 25 kg" karung 25 kg Rp380.000, tanpa 50 kg & tanpa literan; Ketan Paris tidak berubah',
  km('Angsa').karung25 === false && km('Angsa').hargaKarung25 === 0 && km('Angsa').karung50 === true && km('Angsa 25 kg').karung25 === true && km('Angsa 25 kg').hargaKarung25 === 380000 && km('Angsa 25 kg').karung50 === false
  && km('Angsa 25 kg').hargaPerLiter === 0 && km('Ketan Paris').karung25 === true, J([km('Angsa'), km('Angsa 25 kg'), km('Ketan Paris')]));
var HG = hgSemua(new Date(Date.now())).baris;
ok('katalog harga: buku ukuran tidak ditagih harga sendiri (harganya harga induk); baris Angsa 25 kg (kemasan katalog) tetap', !HG.some(function (b) { return /25 kg$/.test(b.merk); }) && HG.some(function (b) { return b.merk === 'Angsa' && b.st.id === 'K25'; }), J(HG.filter(function (b) { return /Angsa|Perahu/.test(b.merk); }).map(function (b) { return b.merk + ' ' + b.st.id; })));
ok('karung terbuka dari buku 25 kg = 25 kg (bukan 50)', beratKarungBuka('Angsa 25 kg') === 25 && beratKarungBuka('Angsa') === 50 && beratKarungBuka('Ketan Paris') === 25);
var kap = susunKapur(new Date(Date.now())).baris.map(function (x) { return x.isi; }).join(' | ');
ok('Papan Kapur menulis pemisahan buku', /Buku Angsa dipisah per ukuran: 5 karung 25 kg → Angsa 25 kg/.test(kap), kap);
var jb = jbKelompokStok(); var jAngsa = (jb.find(function (g) { return g.merk.indexOf('Angsa') >= 0; }) || {}).merk || [];
ok('jenis beras: buku "Angsa 25 kg" dikelompokkan bersama induknya, dan tidak diatur sendiri di setelan jenis', jAngsa.indexOf('Angsa 25 kg') >= 0 && !jbDaftar().baris.some(function (b) { return b.merk === 'Angsa 25 kg'; }), J([jb, jbDaftar().baris.map(function (b) { return b.merk; })]));

// ---- AUDIT 39b no. 35 (owner 30 Sep): merek per liter / kelas sendiri TIDAK memakai buku per ukuran; buku yang terlanjur lahir digabung balik ke induk
// Ketan Hitam datang 50 + 25 kg SEBELUM ditandai per liter → buku "Ketan Hitam 25 kg" lahir (keadaan toko 29 Sep); Ketan Putih datang dua ukuran, belum dipisah
var KD = susunSimpanMasuk({ id: null, tanggal: '2026-09-20', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', bongkar: '', alasan: '', baris: [
  { merk: 'Ketan Hitam', jumlahKarung: '1', beratKarung: 50, hargaPerKg: '20000' }, { merk: 'Ketan Hitam', jumlahKarung: '1', beratKarung: 25, hargaPerKg: '21000' },
  { merk: 'Ketan Putih', jumlahKarung: '1', beratKarung: 50, hargaPerKg: '18000' }] }, W, true); terapkanKeCache(KD.dokumen || []);
terapkanKeCache([{ koleksi: 'batchMasuk', data: B8 }]);
ok('39b-35 sebelum ditandai: Ketan Hitam 25 kg lahir sebagai buku sendiri (25 kg), induk terpisah; Ketan Putih calon pisah', !KD.tolak && buku('Ketan Hitam 25 kg') === 25 && !!(indukTerpisah()['Ketan Hitam'] || {})[25] && ckCalonPisahUkuran().some(function (x) { return x.merk === 'Ketan Putih'; }), J([KD.tolak, buku('Ketan Hitam 25 kg'), indukTerpisah(), ckCalonPisahUkuran()]));
var LL = wbSusunLiteranLangsung('Ketan Hitam', true, W); terapkanKeCache(LL.dokumen || []); var LL2 = wbSusunLiteranLangsung('Ketan Putih', true, W); terapkanKeCache(LL2.dokumen || []);
ok('39b-35 ditandai per liter: ckTanpaBukuUkuran memuat Ketan Hitam & Ketan Putih, bukan Angsa', !LL.tolak && !LL2.tolak && ckTanpaBukuUkuran()['Ketan Hitam'] === true && ckTanpaBukuUkuran()['Ketan Putih'] === true && !ckTanpaBukuUkuran()['Angsa'], J(ckTanpaBukuUkuran()));
var HK35 = hitungMasuk({ id: null, tanggal: '2026-09-20', pemasok: 'X', caraBayar: 'tunai', bongkar: '', baris: [{ merk: 'Ketan Hitam', jumlahKarung: '1', beratKarung: 25, hargaPerKg: '21000' }, { merk: 'Ketan Putih', jumlahKarung: '1', beratKarung: 25, hargaPerKg: '18500' }, { merk: 'Angsa', jumlahKarung: '1', beratKarung: 25, hargaPerKg: '13500' }] });
ok('39b-35 barang masuk: karung 25 kg Ketan Hitam & Ketan Putih (per liter) masuk buku INDUK tanpa indukUkuran; Angsa 25 kg tetap ke "Angsa 25 kg"', J(HK35.baris.map(function (b) { return [b.merkSimpan, b.indukUkuran]; })) === J([['Ketan Hitam', ''], ['Ketan Putih', ''], ['Angsa 25 kg', 'Angsa']]) && !HK35.bermasalah.length, J(HK35.baris.map(function (b) { return [b.merkSimpan, b.indukUkuran, b.masalah]; })));
ok('39b-35 Ketan Putih (per liter) tidak lagi ditawarkan pisah buku', !ckCalonPisahUkuran().some(function (x) { return x.merk === 'Ketan Putih'; }), J(ckCalonPisahUkuran()));
var G0 = ckCalonGabungUkuran();
ok('39b-35 calon gabung: "Ketan Hitam 25 kg" 25 kg → induk Ketan Hitam; Angsa 25 kg (bukan per liter) tidak', J(G0.map(function (x) { return [x.kunci, x.induk, x.kg]; })) === J([['Ketan Hitam 25 kg', 'Ketan Hitam', 25]]), J(G0));
var GY = ckSusunGabungUkuran('Ketan Hitam 25 kg', W, false);
ok('39b-35 gabung minta ketukan kedua dengan angka buku induk sebelum → sesudah', GY.perluYakin === 'gabung' && /25 kg di buku Ketan Hitam 25 kg pindah ke buku Ketan Hitam \(50 kg → 75 kg\)/.test(GY.tolak) && !GY.dokumen, J(GY));
ok('39b-35 gabung buku yang bukan calon DITOLAK (Angsa 25 kg)', !!ckSusunGabungUkuran('Angsa 25 kg', W, true).tolak && !ckSusunGabungUkuran('Angsa 25 kg', W, true).dokumen);
var vG = nilai(), lG = hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih, hInduk = buku('Ketan Hitam');
var GB = ckSusunGabungUkuran('Ketan Hitam 25 kg', W, true); var gp = dok(GB, 'produksiKemasan');
ok('39b-35 gabung: SATU pindah buku 25 kg "Ketan Hitam 25 kg" → "Ketan Hitam" bertanda gabungUkuran {dari, induk, berat 25} — bukan cocokkan (tanpa penyesuaianStok)', !GB.tolak && GB.dokumen.length === 1 && gp.length === 1 && J(gp[0].sumberList) === J([{ merk: 'Ketan Hitam 25 kg', kg: 25 }]) && gp[0].merkTujuan === 'Ketan Hitam' && J(gp[0].gabungUkuran) === J({ dari: 'Ketan Hitam 25 kg', induk: 'Ketan Hitam', berat: 25 }) && !dok(GB, 'penyesuaianStok').length, J([GB.tolak, gp]));
terapkanKeCache(GB.dokumen || []);
ok('39b-35 sesudah gabung: induk 50 → 75 kg, buku 25 kg nol, nilai stok & laba tetap, induk TIDAK lagi terpisah, tidak ada calon gabung lagi', B2(buku('Ketan Hitam') - hInduk) === 25 && B2(buku('Ketan Hitam 25 kg')) === 0 && Math.abs(nilai() - vG) <= 1 && hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih === lG && !indukTerpisah()['Ketan Hitam'] && !ckCalonGabungUkuran().length && ukuranDigabung()['Ketan Hitam 25 kg'] === 'Ketan Hitam', J([buku('Ketan Hitam'), buku('Ketan Hitam 25 kg'), nilai(), vG, indukTerpisah()]));
var KD2 = susunSimpanMasuk({ id: null, tanggal: '2026-09-20', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', bongkar: '', alasan: '', baris: [{ merk: 'Ketan Hitam', jumlahKarung: '1', beratKarung: 25, hargaPerKg: '21000' }] }, W, true); terapkanKeCache(KD2.dokumen || []);
ok('39b-35 kedatangan berikutnya: karung 25 kg Ketan Hitam tercatat & bertambah di buku induk (75 → 100), buku 25 kg tetap nol; rak & retur induk menerima 25 kg lagi', !KD2.tolak && B2(buku('Ketan Hitam')) === B2(hInduk + 50) && B2(buku('Ketan Hitam 25 kg')) === 0 && daftarBarangRetur().karung.some(function (x) { return x.kunci === 'Ketan Hitam|25'; }), J([KD2.tolak, buku('Ketan Hitam'), buku('Ketan Hitam 25 kg'), daftarBarangRetur().karung.map(function (x) { return x.kunci; })]));
print(J({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var J = JSON.stringify; var B2 = function (n) { return Math.round(n * 100) / 100; };
Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
var nId = 900000; var W = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
var nilai = function () { var st = hitungStokKarungPerMerk(); var v = 0; Object.keys(st).forEach(function (m) { v += st[m].sisaKg * st[m].hppTerakhirPerKg; }); return Math.round(v); };
var bulan = TGL_CAD.slice(0, 7); var akhir = bulan + '-' + String(new Date(Number(bulan.slice(0, 4)), Number(bulan.slice(5, 7)), 0).getDate()).padStart(2, '0');
var gabung = ckCalonGabungUkuran(); var vg0 = nilai(), lg0 = hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih; var hasilG = [];
gabung.forEach(function (x) { var r = ckSusunGabungUkuran(x.kunci, W, true); if (!r.tolak) terapkanKeCache(r.dokumen); hasilG.push(x.kunci + ' ' + x.kg + ' → ' + x.induk + (r.tolak ? ' DITOLAK' : '')); });
var gabungSisa = ckCalonGabungUkuran().length; var terpisahSisa = gabung.filter(function (x) { return !!indukTerpisah()[x.induk]; }).map(function (x) { return x.induk; }); var vg1 = nilai(), lg1 = hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih;
var calon = ckCalonPisahUkuran(); var v0 = nilai(), laba0 = hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih; var hasil = [];
calon.forEach(function (x) { var n = Math.min(4, Math.floor(x.bukuKg / 25)); var r = ckSusunPisahUkuran(x.merk, String(n), W, true); if (!r.tolak) terapkanKeCache(r.dokumen); hasil.push(x.merk + ' ' + n + (r.tolak ? ' DITOLAK' : '')); });
var rak = (function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return susunRak(s).karung; })();
var ganda = calon.filter(function (x) { return rak.some(function (c) { return c.kunci === x.merk && c.berat === 25; }); }).map(function (x) { return x.merk; });
print(J({ calon: calon.map(function (x) { return x.merk + ' ' + x.bukuKg; }), hasil: hasil, nilai: [v0, nilai()], laba: [laba0, hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih], ganda: ganda, sisaCalon: ckCalonPisahUkuran().length, gabung: hasilG, gabungNilai: [vg0, vg1], gabungLaba: [lg0, lg1], gabungSisa: gabungSisa, terpisahSisa: terpisahSisa }));
"""


def utama(js, pakai_cadangan):
    h, e = uji_wadah_bernama.jalan(UW.JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\nvar B8 = ' + json.dumps(B8) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    asap = None
    p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p:
        cad, tgl = uji_wadah_bernama.cad_js(p)
        a, e2 = uji_wadah_bernama.jalan(UW.JAM_TETAP.replace('2026-09-20T10:00:00', tgl + 'T23:00:00') + js + '\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + ASAP)
        asap = a if a is not None else {'jatuh': e2[-400:]}
    return h['lulus'], h['gagal'], asap


RUSAK = {
    'barang masuk tidak memisah karung 25 kg': ("const keUkuran = berat === 25 && duaUkuran(merkVarian);", "const keUkuran = false;"),
    'nama buku ukuran boleh diketik di barang masuk': ("ukuran[merk] && !namaLama[merk] ? merk + ' itu buku karung '", "false ? merk + ' itu buku karung '"),
    'rak induk tetap menawarkan 25 kg sesudah dipisah': ("if (uk ? berat !== uk.berat : !!(terpisah[merk] && terpisah[merk][berat])) return;", "if (uk ? berat !== uk.berat : false) return;"),
    'harga karung 25 kg dicari atas nama bukunya (tidak ketemu)': ("const hg = hargaKarungUtuh(hgNama, berat);", "const hg = hargaKarungUtuh(merk, berat);"),
    'pisah tidak memindah kg': ("dokumen.push(wbDokPindah([{ merk: M, kg }], B, w, { pisahUkuran:", "dokumen.push(wbDokPindah([{ merk: M, kg: 0 }], B, w, { pisahUkuran:"),
    'pisah melebihi buku lolos': ("if (kg > c.bukuKg + 0.004) return { tolak: n + ' karung 25 kg = '", "if (false) return { tolak: n + ' karung 25 kg = '"),
    'pisah tanpa ketukan kedua': ("if (!yakin) return { tolak: 'Pisahkan buku: '", "if (false) return { tolak: 'Pisahkan buku: '"),
    'calon pisah tidak ingat yang sudah dipisah': ("if (p.pisahUkuran && p.pisahUkuran.induk) sudah[p.pisahUkuran.induk] = true;", ""),
    'katalog kasir: karung 25 kg tanpa harga': ("hargaKarung25: u.berat === 25 ? hg : 0,", "hargaKarung25: 0,"),
    'katalog kasir: induk tetap menjual 25 kg': ("if (tp[m.merk] && tp[m.merk][25]) x = Object.assign({}, x, { karung25: false, hargaKarung25: 0 });", ""),
    'retur induk tetap menerima 25 kg': ("if (uk[merk] ? b !== uk[merk].berat : !!(tp[merk] && tp[merk][b])) return;", "if (uk[merk] ? b !== uk[merk].berat : false) return;"),
    'karung terbuka buku 25 kg dihitung 50 kg': ("const u = petaUkuran()[asal]; if (u) return u.berat;", "const u = null;"),
    'katalog harga menagih harga buku ukuran': ("Object.keys(stokMerekSaja(stokK)).filter((m) => !ukuranBuku[m]).forEach((m) => {", "Object.keys(stokMerekSaja(stokK)).forEach((m) => {"),
    # audit 39b no. 35
    'merek per liter / kelas sendiri masih dibukukan ke buku per ukuran': ("&& !namaLama[m] && !tanpaUkuran[m] && (", "&& !namaLama[m] && ("),
    'merek per liter masih ditawarkan pisah buku': ("&& !sudah[m] && !tanpa[m] && merkPunyaKarungBerat(m, 50)", "&& !sudah[m] && merkPunyaKarungBerat(m, 50)"),
    'buku yang sudah digabung masih memisah induknya': ("Object.keys(u).forEach((n) => { if (g[n]) return; (out[u[n].induk]", "Object.keys(u).forEach((n) => { (out[u[n].induk]"),
    'gabung tanpa tanda gabungUkuran (induk tetap terpisah)': ("{ gabungUkuran: { dari: K, induk: c.induk, berat: c.berat }, keterangan:", "{ keterangan:"),
    'gabung tanpa ketukan kedua': ("if (!yakin) return { tolak: 'Gabungkan buku: '", "if (false) return { tolak: 'Gabungkan buku: '"),
    'kedatangan tidak menulis tanda indukUkuran': ("b.indukUkuran ? { indukUkuran: b.indukUkuran } : {}, b.merkPemasok ? { merkPemasok: b.merkPemasok } : {})) };", "{}, b.merkPemasok ? { merkPemasok: b.merkPemasok } : {})) };"),   # putaran 30: baris merkList membawa merkPemasok bila ada
}

if __name__ == '__main__':
    js = UW.bundel()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('BUKU PER UKURAN (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if asap:
        if 'jatuh' in asap: g.append('asap data toko JATUH: ' + asap['jatuh']); print('   ✗ ' + g[-1])
        else:
            print('ASAP DATA TOKO (%s): merek dua ukuran: %s · dipisah dengan hitungan contoh: %s · nilai stok %s → %s · laba bulan itu %s → %s · induk masih menawarkan 25 kg: %s · calon tersisa %d'
                  % (os.path.basename(p), ', '.join(asap['calon']) or '-', ', '.join(asap['hasil']) or '-', asap['nilai'][0], asap['nilai'][1], asap['laba'][0], asap['laba'][1], ', '.join(asap['ganda']) or 'tidak ada', asap['sisaCalon']))
            print('   39b no. 35 — gabung balik buku per ukuran merek per liter: %s · nilai stok %s → %s · laba %s → %s · calon tersisa %d · induk masih terpisah: %s'
                  % (', '.join(asap['gabung']) or '-', asap['gabungNilai'][0], asap['gabungNilai'][1], asap['gabungLaba'][0], asap['gabungLaba'][1], asap['gabungSisa'], ', '.join(asap['terpisahSisa']) or 'tidak ada'))
            if abs(asap['gabungNilai'][0] - asap['gabungNilai'][1]) > 5 or asap['gabungLaba'][0] != asap['gabungLaba'][1] or asap['gabungSisa'] or asap['terpisahSisa'] or any('DITOLAK' in x for x in asap['gabung']):
                g.append('asap data toko (39b no. 35): ' + json.dumps({k: asap[k] for k in ('gabung', 'gabungNilai', 'gabungLaba', 'gabungSisa', 'terpisahSisa')}, ensure_ascii=False)[:500])
            if abs(asap['nilai'][0] - asap['nilai'][1]) > 5 or asap['laba'][0] != asap['laba'][1] or asap['ganda'] or asap['sisaCalon'] or any('DITOLAK' in x for x in asap['hasil']):
                g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:500])
    sys.exit(2 if g else 0)
