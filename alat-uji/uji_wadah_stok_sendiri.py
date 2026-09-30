#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_wadah_stok_sendiri.py — putaran 28: WADAH PUNYA STOK SENDIRI (owner 28 Sep 2026).
  · "Gua mau semua wadah kotak literan itu punya stok tersendiri" — sumbernya karung 50 kg di BELAKANG wadah; karung itu dari tumpukan gudang,
    kiriman pemasok, atau hasil adukan (tiga pintu).
  · Buku wadah berkunci 'Wadah <nama>', lahir lewat batch stokAwal 0 kg (mesin beku hanya memotong nama yang lahir lewat batch).
  · Pindahan awal (keputusan owner: pindah dari buku merek): isi tercatat → buku wadah, buku merek turun, modal ikut — nilai stok, laba, tumpukan tidak berubah.
  · Takar = pindah buku merek karung → buku wadah; literan terjual = buku wadah saja; cocokkan wadah = penyesuaian buku wadah; ganti nama membawa stok.
  · Katalog HP kasir (keputusan owner: wadah ikut katalog): baris buku wadah berharga liter wadahnya; nama wadah berstok sendiri tidak menjual literan atas
    nama mereknya.
  · Buku wadah tidak bocor ke daftar MEREK (rak karung, gudang, harga karung, barang masuk, adukan, tempat, belanja, HPP).
KOTAK PASIR (ANGKA CONTOH), jam dikunci 20 Sep 2026 10:00 WIB. Cadangan toko di _privat/: pindahan awal semua wadah tidak menggeser nilai stok, laba
September, maupun tumpukan tiap merek; tiap wadah berharga bisa dijual 1 L dari bukunya sendiri.

    python3 alat-uji/uji_wadah_stok_sendiri.py            → N lulus · 0 gagal
    python3 alat-uji/uji_wadah_stok_sendiri.py --kontrol  → logika yang dirusak wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
import uji_wadah_bernama  # noqa: E402
import uji_kunci_periode  # noqa: E402

_M = uji_kunci_periode.MODUL + uji_wadah_bernama.MODUL + ['baru/js/layar/jenis-beras-logika.js', 'baru/js/layar/belanja-logika.js']
MODUL = [m for i, m in enumerate(_M) if m not in _M[:i]]
JAM_TETAP = "var __KINI = new Date('2026-09-20T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"
brs = uji_wadah_bernama.brs

KOTAK = {
  # b0 = kedatangan LAMA atas nama kelas "IR64 Apex"; b1 = NG 10, Kumala 2, Angsa 4 karung (baru datang 15 Sep — pintu "baru datang")
  'batchMasuk': [{'id': 'b0', 'tanggal': '2026-08-20', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'IR64 Apex', 2, 14000)]},
                 {'id': 'b1', 'tanggal': '2026-09-15', 'jam': '08:00', 'pemasok': 'PEMASOK CONTOH', 'caraBayar': 'tunai', 'biayaBongkar': 0, 'merkList': [brs(1, 'NG', 10, 12000), brs(2, 'Kumala', 2, 11000), brs(3, 'Angsa', 4, 13000)]}],
  # adukan X KI 50 kg × 2 (modal Rp600.000 per unit) — pintu "hasil adukan"
  'produksiKemasan': [{'id': 'p1', 'tanggal': '2026-09-16', 'jam': '09:00', 'namaProduk': 'X KI', 'ukuranKemasan': 50, 'jumlahUnit': 2, 'hppPerUnit': 600000, 'merkSumber': 'NG', 'kgDipakai': 100,
                       'sumberList': [{'merk': 'NG', 'kg': 100}], 'batchProduksi': 'p1', 'barisKe': 1, 'jumlahBaris': 1, 'jadiKarungUtuh': False, 'merkTujuan': None}],
  # dua wadah: IR64 Apex berisi NG 30 + Kumala 20 (komposisi putaran 27), Angsa = dokumen LAMA tanpa komposisi (seluruh isinya milik buku "Angsa")
  'wadahLiteran': [{'id': 100, 'tanggal': '2026-09-01', 'jam': '07:00', 'tipe': 'atur', 'penuhKg': 50, 'puncakKg': 60, 'isiUlangKg': 10, 'takarKg': 1.8, 'daftar': ['IR64 Apex', 'Angsa']},
                   {'id': 101, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'IR64 Apex', 'isiKg': 50, 'komposisi': {'NG': 30, 'Kumala': 20}},
                   {'id': 102, 'tanggal': '2026-09-19', 'jam': '08:00', 'tipe': 'isi', 'wadah': 'Angsa', 'isiKg': 40},
                   {'id': 103, 'tanggal': '2026-09-19', 'jam': '07:30', 'tipe': 'karung', 'merk': 'Kumala', 'kg': 50, 'wadah': 'IR64 Apex'},
                   {'id': 104, 'tanggal': '2026-09-19', 'jam': '07:30', 'tipe': 'karung', 'merk': 'Angsa', 'kg': 50, 'wadah': 'Angsa'}],
  'katalogHargaLiteran': [{'id': 'IR64 Apex', 'merk': 'IR64 Apex', 'hargaPerLiter': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerLiter': 13000}],
  'katalogHargaKarung': [{'id': 'NG', 'merk': 'NG', 'hargaPerKg': 13000}, {'id': 'Kumala', 'merk': 'Kumala', 'hargaPerKg': 12000}, {'id': 'Angsa', 'merk': 'Angsa', 'hargaPerKg': 14000}],
}

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket ? ' → ' + String(ket).slice(0, 600) : '')); }
__dom['jualKarungBerat'] = { value: '50' };
Object.keys(KOTAK).forEach(function (n) { pasok(n, JSON.parse(J(KOTAK[n]))); });
var nId = 9000; var W = { tanggal: '2026-09-20', jam: '10:00', kini: '2026-09-20T03:00:00.000Z', idUnik: function () { nId += 1; return nId; } };
var s0 = function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return s; };
var chipL = function (k, s) { return susunRak(s || s0()).literan.find(function (c) { return c.kunci === k && c.wadahLiteran; }); };
var masuk = function (s, c, j) { var r = masukkan(Object.assign({}, s, { pilih: c }), j); return r.keranjang ? Object.assign({}, s, { keranjang: r.keranjang, urutBaris: r.urutBaris }) : Object.assign({ tolak: r.kabar }, s); };
var buku = function (m) { return (hitungStokKarungPerMerk()[m] || { sisaKg: 0 }).sisaKg; };
var hpp = function (m) { return (hitungStokKarungPerMerk()[m] || { hppTerakhirPerKg: 0 }).hppTerakhirPerKg; };
var B2 = function (n) { return Math.round(n * 100) / 100; };
var nilai = function () { var st = hitungStokKarungPerMerk(); var v = 0; Object.keys(st).forEach(function (m) { v += st[m].sisaKg * st[m].hppTerakhirPerKg; }); return Math.round(v); };
var tump = function (m) { return B2(tumpukanGudang(m).kg); };
var dok = function (R, k) { return (R.dokumen || []).filter(function (d) { return d.koleksi === k; }).map(function (d) { return d.data; }); };
var MEREK = ['NG', 'Kumala', 'Angsa', 'IR64 Apex'];

// ---- SEBELUM pindahan: model putaran 27 (buku merek asal), katalog kasir byte-sama penyusun index.html
ok('sebelum pindahan: kedua wadah belum berstok sendiri, katalog HP kasir byte-sama penyusun index.html (tanpa saring wadah)',
  !wbAktif('IR64 Apex') && !wbAktif('Angsa') && (function () { var x = kkIsi(); var ada = Array.isArray(x.bayarBonTerhitung); delete x.bayarBonTerhitung; delete x.bayarBonSejak; return ada && J(x) === J(arSaringKatalogKasir(susunIsiKatalogKasir())); })(), J([wbAktif('IR64 Apex'), wbAktif('Angsa')]));
var jualNG = { id: 7001, tanggal: '2026-09-20', jam: '09:00', jenis: 'karung', merkSumber: 'NG', jumlahKarung: 8, totalKg: 400, hargaTotal: 5200000, hppTotalSaatJual: 4800000, caraBayar: 'Tunai', namaProduk: 'NG (karung utuh)' };
var chipSebelumNGminus = denganCacheSementara([{ koleksi: 'penjualan', data: jualNG }], function () { var c = chipL('IR64 Apex'); return c ? c.sisa : null; });
ok('sebelum pindahan: buku NG yang habis MENAHAN literan wadah IR64 Apex (inilah yang dikeluhkan owner)', chipSebelumNGminus === 0, J(chipSebelumNGminus));

// ---- PINDAHAN AWAL
var v0 = nilai(), laba0 = hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih; var t0 = MEREK.map(tump); var b0 = MEREK.map(buku);
var P = wbSusunPindahAwal(W); var pb = dok(P, 'batchMasuk'), pp = dok(P, 'produksiKemasan'), pi = dok(P, 'wadahLiteran');
ok('pindahan awal: satu batch LAHIR (stokAwal, 0 kg, satu baris ber-stokWadah per wadah) + satu pindah buku per wadah + titik samakan isi',
  !P.tolak && pb.length === 1 && pb[0].stokAwal === true && pb[0].lahirBuku === true && pb[0].merkList.length === 2 && pb[0].merkList.every(function (r) { return r.totalKg === 0 && !!r.stokWadah && /^Wadah /.test(r.merk); })
  && pp.length === 2 && pi.length === 2 && pi.every(function (d) { return d.tipe === 'isi' && d.pindahAwal === true && /^Wadah /.test(d.stokWadah); }), J([P.tolak, pb, pp.length, pi]));
var pA = pp.find(function (d) { return d.merkTujuan === 'Wadah IR64 Apex'; });
ok('pindah buku IR64 Apex: sumber = komposisi (Kumala 20 + NG 30), tujuan buku wadah, 50 kg, modal rata-rata tertimbang Rp11.600/kg, jadi-karung-utuh dariTakar',
  !!pA && J(pA.sumberList) === J([{ merk: 'Kumala', kg: 20 }, { merk: 'NG', kg: 30 }]) && pA.kgDipakai === 50 && pA.ukuranKemasan === 50 && pA.jumlahUnit === 1 && Math.round(pA.hppSumberPerKgDipakai) === 11600 && pA.jadiKarungUtuh === true && pA.dariTakar === true, J(pA));
terapkanKeCache(P.dokumen);
ok('sesudah pindahan: buku wadah IR64 Apex 50 kg @Rp11.600, wadah Angsa 40 kg @Rp13.000; NG −30, Kumala −20, Angsa −40, IR64 Apex tetap',
  wbAktif('IR64 Apex') && wbAktif('Angsa') && buku('Wadah IR64 Apex') === 50 && Math.round(hpp('Wadah IR64 Apex')) === 11600 && buku('Wadah Angsa') === 40 && Math.round(hpp('Wadah Angsa')) === 13000
  && J(MEREK.map(buku).map(function (x, i) { return B2(x - b0[i]); })) === J([-30, -20, -40, 0]), J([MEREK.map(buku), buku('Wadah IR64 Apex'), hpp('Wadah IR64 Apex'), buku('Wadah Angsa')]));
ok('pindahan tidak mengubah nilai stok (Σ sisa × modal), laba September, maupun tumpukan gudang tiap merek',
  nilai() === v0 && hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih === laba0 && J(MEREK.map(tump)) === J(t0), J([v0, nilai(), laba0, t0, MEREK.map(tump)]));
ok('pindahan kedua ditolak (semua wadah sudah berstok sendiri)', !!wbSusunPindahAwal(W).tolak);
var cA = chipL('IR64 Apex'), cB = chipL('Angsa');
ok('chip literan wadah = buku wadahnya sendiri: IR64 Apex 60,9 L modal Rp11.600/kg, Angsa 48,7 L', !!cA && cA.sisa === 60.9 && Math.round(cA.hppPerKg) === 11600 && !!cB && cB.sisa === 48.7, J([cA && [cA.sisa, cA.hppPerKg], cB && cB.sisa]));
var chipNGminus = denganCacheSementara([{ koleksi: 'penjualan', data: jualNG }], function () { var c = chipL('IR64 Apex'); return c ? c.sisa : null; });
ok('sesudah pindahan: buku NG yang habis TIDAK menahan literan wadah lagi (tetap 60,9 L)', chipNGminus === 60.9, J(chipNGminus));
var sK = masuk(s0(), cA, 2); sinkronKeranjang(sK); var cK = chipL('IR64 Apex', sK); sinkronKeranjang(s0());
ok('2 L di keranjang memegang buku wadah: chip turun jadi 58,9 L (bebas = buku − keranjang)', !sK.tolak && !!cK && cK.sisa === 58.9, J([sK.tolak, cK && cK.sisa]));

// ---- JUAL dari wadah berstok sendiri
var N = simpanNota(Object.assign({}, sK, { cara: 'QRIS' }), W); var rj = dok(N, 'penjualan');
ok('nota 2 L IR64 Apex: SATU baris, merkSumber buku wadah, dariWadah nama wadah, 1,64 kg, modal beras 1,64 × Rp11.600, Rp24.000',
  !N.tolak && rj.length === 1 && rj[0].merkSumber === 'Wadah IR64 Apex' && rj[0].dariWadah === 'IR64 Apex' && rj[0].totalKg === 1.64 && rj[0].hppTotalSaatJual - (rj[0].biayaKemasanLiteran || 0) === Math.round(1.64 * 11600) && rj[0].hargaTotal === 24000, J([N.tolak, rj]));
var ngS = buku('NG'), kmS = buku('Kumala'); terapkanKeCache(N.dokumen);
ok('sesudah nota: cuma buku wadah yang turun 1,64 kg — NG & Kumala tidak disentuh', B2(buku('Wadah IR64 Apex')) === 48.36 && buku('NG') === ngS && buku('Kumala') === kmS, J([buku('Wadah IR64 Apex'), buku('NG'), buku('Kumala')]));
terapkanKeCache([{ koleksi: 'penjualan', data: { id: 7002, tanggal: '2026-09-20', jam: '10:00', jenis: 'literan', merkSumber: 'Wadah Angsa', namaProduk: 'Wadah Angsa', jumlahLiter: 2, totalKg: 1.64, hargaTotal: 26000, hppTotalSaatJual: 21320, caraBayar: 'Tunai' } }]);
var tA = tinggiWadah('Angsa', null);
ok('satu kebenaran: literan dari HP kasir (tanpa dariWadah, merkSumber buku wadah) ikut menurunkan tinggi wadah — isi wadah = buku wadah',
  tA.stokSendiri === true && B2(tA.sisaNyataKg) === 38.36 && B2(buku('Wadah Angsa')) === 38.36, J([tA.stokSendiri, tA.sisaNyataKg, buku('Wadah Angsa')]));

// ---- TAKAR = pindah buku karung → wadah
var kmT = buku('Kumala'), wT = buku('Wadah IR64 Apex'), krT = karungBelakang('Kumala', 'IR64 Apex').sisaKg, tmT = tump('Kumala');
var T = susunTakarWadah('IR64 Apex', [{ merk: 'Kumala', takar: 3 }], W, s0()); var tt = dok(T, 'wadahLiteran').filter(function (d) { return d.tipe === 'takar'; }); var tp = dok(T, 'produksiKemasan');
ok('takar 3 × Kumala ke wadah IR64 Apex: dokumen takar (stokWadah, produksiId) + satu pindah buku Kumala 5,4 kg → buku wadah (takarId, dariTakar)',
  !T.tolak && tt.length === 1 && tt[0].stokWadah === 'Wadah IR64 Apex' && tp.length === 1 && String(tt[0].produksiId) === String(tp[0].id) && String(tp[0].takarId) === String(tt[0].id)
  && J(tp[0].sumberList) === J([{ merk: 'Kumala', kg: 5.4 }]) && tp[0].merkTujuan === 'Wadah IR64 Apex' && tp[0].dariTakar === true && !dok(T, 'batchMasuk').length, J([T.tolak, tt, tp]));
terapkanKeCache(T.dokumen);
ok('sesudah takar: buku Kumala −5,4, buku wadah +5,4, karung Kumala di belakang −5,4, tumpukan Kumala tidak bergeser, tinggi wadah = buku',
  B2(buku('Kumala') - kmT) === -5.4 && B2(buku('Wadah IR64 Apex') - wT) === 5.4 && B2(karungBelakang('Kumala', 'IR64 Apex').sisaKg - krT) === -5.4 && tump('Kumala') === tmT
  && B2(tinggiWadah('IR64 Apex', null).sisaNyataKg) === B2(buku('Wadah IR64 Apex')), J([buku('Kumala') - kmT, buku('Wadah IR64 Apex') - wT, karungBelakang('Kumala', 'IR64 Apex').sisaKg - krT, tump('Kumala'), tmT]));
var T2 = susunTakarWadah('IR64 Apex', [{ merk: 'Tanpa Buku', takar: 1, dari: '' }], W, s0());
ok('takar dari karung yang tidak punya buku DITOLAK (beras tidak muncul dari udara di buku wadah)', !!T2.tolak && /tidak punya buku/.test(T2.tolak), J(T2.tolak || T2.dokumen));

// ---- COCOKKAN WADAH = susut wadah itu sendiri
var hW = hpp('Wadah IR64 Apex'); var sebelumC = B2(buku('Wadah IR64 Apex')); var H = {}; H['wadah|IR64 Apex'] = '50';
var CC = susunSimpanCocok('wadah', H, { 'wadah|IR64 Apex': 'tumpah waktu takar' }, W, { sebagian: true });
var cps = dok(CC, 'penyesuaianStok'), cis = dok(CC, 'wadahLiteran').filter(function (d) { return d.tipe === 'isi'; });
ok('cocokkan wadah IR64 Apex (hitung 50 kg) sesaat sesudah pindahan: tidak ditanya "baru saja dicocokkan"; penyesuaian atas BUKU WADAH, rupiah = selisih × modal wadah',
  !CC.tolak && cps.length === 1 && cps[0].merk === 'Wadah IR64 Apex' && cps[0].selisihKg === B2(50 - sebelumC) && cps[0].nilaiRp === Math.round(B2(50 - sebelumC) * hW) && cps[0].bagian === 'wadah', J([CC.tolak, cps, sebelumC]));
ok('titik samakan cocokkan wadah berstok sendiri: tanpa komposisi, bertanda stokWadah', cis.length === 1 && !cis[0].komposisi && cis[0].stokWadah === 'Wadah IR64 Apex' && cis[0].isiKg === 50, J(cis));
terapkanKeCache(CC.dokumen || []);
ok('sesudah cocokkan: buku wadah = hitungan (50 kg)', B2(buku('Wadah IR64 Apex')) === 50, J(buku('Wadah IR64 Apex')));
var SJ = susunIsiUlangWadah('IR64 Apex', W, 48);
ok('samakan isi dari panel Jual untuk wadah berstok sendiri DITOLAK → lewat Stok › Cocokkan (satu pintu yang minta alasan)', !!SJ.tolak && /Cocokkan/.test(SJ.tolak), J(SJ));

// ---- GANTI NAMA membawa stok
var GN = wbSusunGantiNama('IR64 Apex', 'Apex Baru', W); var gb = dok(GN, 'batchMasuk'), gp = dok(GN, 'produksiKemasan'), gi = dok(GN, 'wadahLiteran').filter(function (d) { return d.tipe === 'isi'; });
ok('ganti nama IR64 Apex → Apex Baru: buku Wadah Apex Baru lahir, stok 50 kg dipindah dari buku lama, titik samakan bertanda stokWadah nama baru',
  !GN.tolak && gb.length === 1 && gb[0].merkList[0].merk === 'Wadah Apex Baru' && gb[0].merkList[0].stokWadah === 'Apex Baru' && gp.length === 1 && J(gp[0].sumberList) === J([{ merk: 'Wadah IR64 Apex', kg: 50 }]) && gp[0].merkTujuan === 'Wadah Apex Baru'
  && gi.length === 1 && gi[0].stokWadah === 'Wadah Apex Baru' && !gi[0].komposisi, J([GN.tolak, gb, gp, gi]));
terapkanKeCache(GN.dokumen);
var cN = chipL('Apex Baru');
ok('sesudah ganti nama: buku lama 0, buku baru 50 kg, wadah baru berstok sendiri, chip Apex Baru 60,9 L Rp12.000', buku('Wadah IR64 Apex') === 0 && buku('Wadah Apex Baru') === 50 && wbAktif('Apex Baru') && !!cN && cN.sisa === 60.9 && cN.harga === 12000, J([buku('Wadah IR64 Apex'), buku('Wadah Apex Baru'), cN && [cN.sisa, cN.harga]]));
var AT = susunAturWadah({ penuhKg: '50', isiUlangKg: '10', daftar: ['Apex Baru'] }, W);
ok('atur susunan yang melepas wadah Angsa (masih berstok ±38 kg) DITOLAK — stoknya akan yatim', !!AT.tolak && /Angsa/.test(AT.tolak), J(AT));

// ---- KATALOG HP KASIR
var kk = kkIsi(); var kw = function (m) { return kk.merkKarung.find(function (x) { return x.merk === m; }); };
ok('katalog HP kasir: buku wadah berharga liter wadahnya & tanpa karung; merek Angsa (nama wadah berstok sendiri) tidak dijual literan; buku wadah lama (nol, sudah ganti nama) tidak ditawarkan',
  !!kw('Wadah Apex Baru') && kw('Wadah Apex Baru').hargaPerLiter === 12000 && kw('Wadah Apex Baru').karung50 === false && kw('Wadah Apex Baru').sisaKg === 50 && !!kw('Wadah Angsa') && kw('Wadah Angsa').hargaPerLiter === 13000
  && !!kw('Angsa') && kw('Angsa').hargaPerLiter === 0 && !kw('Wadah IR64 Apex'), J([kw('Wadah Apex Baru'), kw('Wadah Angsa'), kw('Angsa'), !!kw('Wadah IR64 Apex')]));

// ---- TIGA PINTU karung di belakang wadah
var CB = calonBukaKarung(14);
ok('tiga pintu: tumpukan gudang, kedatangan 14 hari (b1: NG, Kumala, Angsa), kemasan jadi hasil adukan (X KI 50 kg × 2)',
  CB.tumpukan.length > 0 && J(CB.masuk.map(function (x) { return [x.batchId, x.merk]; })) === J([['b1', 'Angsa'], ['b1', 'Kumala'], ['b1', 'NG']]) && CB.adukan.some(function (x) { return x.namaProduk === 'X KI' && x.ukuran === 50 && x.unit === 2; }), J(CB));
var tmNG = tump('NG'); var BM = susunBukaKarung('NG', W, '', { jenis: 'masuk', batchId: 'b1' }); var bm = dok(BM, 'wadahLiteran');
ok('pintu "baru datang": catatan karung membawa asal & batch, bukunya tetap buku NG — tumpukan turun satu karung seperti pintu tumpukan',
  !BM.tolak && bm.length === 1 && bm[0].asal === 'masuk' && bm[0].batchId === 'b1' && bm[0].lepas === true && denganCacheSementara(BM.dokumen, function () { return B2(tump('NG') - tmNG); }) === -50, J([BM.tolak, bm]));
var BX = susunBukaKarung('NG', W, '', { jenis: 'masuk', batchId: 'b0' });
ok('pintu "baru datang" dari kedatangan yang tidak memuat merek itu DITOLAK', !!BX.tolak, J(BX));
var kmX = hitungStokKemasan()[kunciKemasan('X KI', 50)].sisaUnit; var tgAng = tump('Angsa');
var BK = susunBukaKarung('X KI', W, 'Angsa', { jenis: 'adukan', namaProduk: 'X KI', ukuran: 50 }); var bkb = dok(BK, 'batchMasuk'), bkp = dok(BK, 'produksiKemasan'), bkw = dok(BK, 'wadahLiteran');
ok('pintu "hasil adukan": 1 kemasan X KI 50 kg dibuka — buku SENDIRI "Adukan X KI 50 kg" lahir (bukan buku merek pemasok), stok kemasan −1 unit lewat sumberKemasanList, catatan karung asal adukan di belakang Angsa',
  !BK.tolak && bkb.length === 1 && bkb[0].merkList[0].merk === 'Adukan X KI 50 kg' && bkb[0].merkList[0].bukuAdukan === 'X KI|50' && !bkb[0].merkList[0].stokWadah && bkp.length === 1 && J(bkp[0].sumberKemasanList) === J([{ namaProduk: 'X KI', ukuranKemasan: 50, unit: 1 }])
  && bkp[0].merkTujuan === 'Adukan X KI 50 kg' && bkp[0].jadiKarungUtuh === true && bkp[0].bukaKemasan === true && bkw.length === 1 && bkw[0].merk === 'Adukan X KI 50 kg' && bkw[0].asal === 'adukan' && bkw[0].wadah === 'Angsa', J([BK.tolak, bkb, bkp, bkw]));
terapkanKeCache(BK.dokumen);
var AX = 'Adukan X KI 50 kg';
ok('sesudah buka kemasan: stok kemasan X KI 50 kg 2 → 1, buku "Adukan X KI 50 kg" 50 kg @Rp12.000, karungnya di belakang Angsa 50 kg, tumpukannya 0, buku merek Angsa tidak tercampur',
  hitungStokKemasan()[kunciKemasan('X KI', 50)].sisaUnit === kmX - 1 && buku(AX) === 50 && Math.round(hpp(AX)) === 12000 && karungBelakang(AX, 'Angsa').sisaKg === 50 && tump(AX) === 0 && !petaStokWadah()[AX] && petaBukuWadah()[AX].jenis === 'adukan' && tump('Angsa') === tgAng && buku('X KI') === 0,
  J([hitungStokKemasan()[kunciKemasan('X KI', 50)].sisaUnit, buku(AX), hpp(AX), karungBelakang(AX, 'Angsa').sisaKg, tump(AX)]));
var wAng = buku('Wadah Angsa'); var T3 = susunTakarWadah('Angsa', [{ merk: AX, takar: 2, dari: 'Angsa' }], W, s0()); terapkanKeCache(T3.dokumen || []);
ok('takar 2 × dari karung "Adukan X KI 50 kg" ke wadah Angsa: bukunya 46,4, buku wadah Angsa +3,6', !T3.tolak && B2(buku(AX)) === 46.4 && B2(buku('Wadah Angsa') - wAng) === 3.6, J([T3.tolak, buku(AX), buku('Wadah Angsa') - wAng]));
var H0 = { 'wadah|Angsa': '0' }; var C0 = susunSimpanCocok('wadah', H0, { 'wadah|Angsa': 'uji: wadah dikosongkan' }, Object.assign({}, W, { jam: '10:30' }), { sebagian: true }); terapkanKeCache(C0.dokumen || []);
var c0 = chipL('Angsa');
ok('wadah berstok sendiri yang KOSONG tidak menjual dari karung di belakangnya (Adukan X KI 46,4 kg): chip Angsa 0 L', !C0.tolak && B2(buku('Wadah Angsa')) === 0 && !!c0 && c0.sisa === 0, J([C0.tolak, buku('Wadah Angsa'), c0 && c0.sisa]));

// ---- BUKU WADAH TIDAK BOCOR ke daftar MEREK
var wd = function (m) { return /^Wadah /.test(String(m)); };
var bocor = { rakKarung: susunRak(s0()).karung.filter(function (c) { return wd(c.kunci); }).length, repack: susunRak(s0()).repack.filter(function (c) { return wd(c.kunci); }).length,
  literanLangsung: susunRak(s0()).literan.filter(function (c) { return !c.wadahLiteran && wd(c.kunci); }).length, calonKarung: calonKarung().filter(function (t) { return wd(t.merk); }).length,
  calonCampur: calonCampur([]).filter(wd).length, harga: hgSemua(new Date(Date.now())).baris.filter(function (b) { return wd(b.merk); }).length, masuk: calonMerkMasuk().filter(wd).length,
  cocokTumpukan: barangCocok('tumpukan').filter(function (b) { return wd(b.nama); }).length, kedatangan: daftarKedatangan(50).filter(function (b) { return /LAHIR/.test(b.pemasok); }).length,
  hpp: kartuHpp().kartu ? kartuHpp().kartu.filter(function (k) { return wd(k.merk); }).length : kartuHpp().filter(function (k) { return wd(k.merk); }).length,
  adukan: calonBahan().filter(function (b) { return wd(b.merk); }).length, tempat: barangTempat().filter(function (b) { return wd(b.nama); }).length,
  belanja: daftarBelanja(new Date(Date.now())).merk.filter(function (b) { return wd(b.merk); }).length, lokasi: susunLokasi().filter(function (t) { return wd(t.merk); }).length };
ok('buku wadah tidak bocor ke daftar merek (rak karung/repack/literan langsung, karung gudang, campuran, harga, barang masuk, cocokkan tumpukan, kedatangan, HPP, adukan, tempat, belanja, lokasi)',
  Object.keys(bocor).every(function (k) { return bocor[k] === 0; }), J(bocor));
var HM = hitungMasuk({ tanggal: '2026-09-20', baris: [{ merk: 'Wadah Angsa', jumlahKarung: '1', beratKarung: '50', hargaPerKg: '13000' }] });
ok('barang masuk atas nama buku wadah DITOLAK dengan kalimat', HM.baris[0].masalah.indexOf('buku KHUSUS') >= 0, J(HM.baris[0]));
var db = daftarBarang().filter(function (b) { return wd(b.nama); });
ok('Stok › Gudang tetap MENILAI buku wadah (modal tidur) tapi tidak menaruhnya di daftar belanja', db.length >= 2 && db.every(function (b) { return b.wadahStok === true; }), J(db));
var kap = susunKapur(new Date(Date.now())).baris.map(function (x) { return x.isi; }).join(' | ');
ok('Papan Kapur: pindahan awal, takar ke stok wadah, buka kemasan hasil adukan tertulis; batch lahir TIDAK tampil sebagai barang masuk',
  /Pindahan awal stok wadah IR64 Apex/.test(kap) && /Takar ke stok wadah: Kumala/.test(kap) && /Kemasan X KI 50 kg hasil adukan dibuka/.test(kap) && !/Barang masuk Wadah/.test(kap) && !/Barang masuk Adukan/.test(kap), kap);
ok('daftar Adukan tidak memuat pindah buku / buka kemasan (cuma adukan X KI)', daftarAdukan(20).length === 1, J(daftarAdukan(20).map(function (a) { return a.hasilTeks; })));
var TB = pembukaBuku(2026, W); var tbb = dok(TB, 'batchMasuk')[0] || { merkList: [] }; var tbw = tbb.merkList.filter(function (r) { return wd(r.merk); });
ok('tutup buku: saldo pembuka membawa tanda stokWadah untuk tiap buku wadah (termasuk yang nol → baris lahir)',
  tbw.length === 3 && tbw.every(function (r) { return !!r.stokWadah; }) && tbw.some(function (r) { return r.merk === 'Wadah IR64 Apex' && r.totalKg === 0; }), J(tbw));

// ---- SISIHKAN · TUANG BALIK · BONGKAR (owner 28 Sep): isi yang dikeluarkan dari kotak = karung wadah, buku terpisah
var KB = 'Karung wadah Apex Baru'; var WB5 = 'Wadah Apex Baru'; var v5 = nilai(); var tK5 = MEREK.map(tump);
var SH = wbSusunSisih('Apex Baru', '', W); var shb = dok(SH, 'batchMasuk'), shp = dok(SH, 'produksiKemasan'), shw = dok(SH, 'wadahLiteran');
ok('sisihkan (kosong = aturan 10 kg): buku "Karung wadah Apex Baru" lahir, pindah buku 10 kg dari buku wadah, karung lepas asal wadah 10 kg',
  !SH.tolak && shb.length === 1 && shb[0].merkList[0].merk === KB && shb[0].merkList[0].karungWadah === 'Apex Baru' && shp.length === 1 && J(shp[0].sumberList) === J([{ merk: WB5, kg: 10 }]) && shp[0].merkTujuan === KB && shp[0].sisihWadah === 'Apex Baru'
  && shw.length === 1 && shw[0].merk === KB && shw[0].kg === 10 && shw[0].lepas === true && shw[0].asal === 'wadah', J([SH.tolak, shb, shp, shw]));
terapkanKeCache(SH.dokumen || []);
ok('sesudah sisihkan: wadah 40 kg (chip 48,7 L), karung wadah 10 kg (buku & kolam), nilai stok & tumpukan merek tetap',
  buku(WB5) === 40 && buku(KB) === 10 && wbKarungWadah('Apex Baru').sisaKg === 10 && chipL('Apex Baru').sisa === 48.7 && nilai() === v5 && J(MEREK.map(tump)) === J(tK5), J([buku(WB5), buku(KB), wbKarungWadah('Apex Baru'), chipL('Apex Baru').sisa, nilai(), v5]));
ok('sisihkan melebihi isi buku wadah DITOLAK', !!wbSusunSisih('Apex Baru', '45', W).tolak);
var TBL = wbSusunTuangBalik('Apex Baru', '', W); var tbt = dok(TBL, 'wadahLiteran'), tbp = dok(TBL, 'produksiKemasan');
ok('tuang balik semua: takar bertanda tuangBalik dari karung wadah + pindah buku 10 kg kembali ke buku wadah',
  !TBL.tolak && tbt.length === 1 && tbt[0].tipe === 'takar' && tbt[0].tuangBalik === true && tbt[0].kg === 10 && J(tbp[0].sumberList) === J([{ merk: KB, kg: 10 }]) && tbp[0].merkTujuan === WB5 && String(tbp[0].takarId) === String(tbt[0].id), J([TBL.tolak, tbt, tbp]));
terapkanKeCache(TBL.dokumen || []);
ok('sesudah tuang balik: wadah 50, karung wadah 0 (buku & kolam)', buku(WB5) === 50 && buku(KB) === 0 && wbKarungWadah('Apex Baru').sisaKg === 0, J([buku(WB5), buku(KB), wbKarungWadah('Apex Baru')]));
ok('tuang balik dari karung wadah kosong DITOLAK', !!wbSusunTuangBalik('Apex Baru', '', W).tolak);
terapkanKeCache(wbSusunSisih('Apex Baru', '5', W).dokumen || []); terapkanKeCache(susunTakarWadah('Apex Baru', [{ merk: 'Kumala', takar: 8 }], W, s0()).dokumen || []);
var TBX = wbSusunTuangBalik('Apex Baru', '', W);
ok('tuang balik yang membuat wadah melewati batas menggunung (59,4 + 5 > 60) DITOLAK dengan kalimat', !!TBX.tolak && /melebihi/.test(TBX.tolak), J([buku(WB5), TBX]));
var AT2 = susunAturWadah({ penuhKg: '50', isiUlangKg: '10', sisihKg: '12', daftar: ['Apex Baru', 'Angsa'] }, W); var at2 = dok(AT2, 'wadahLiteran')[0] || {};
ok('aturan wadah menyimpan "disisihkan saat tutup" (12 kg); 0 kg ditolak', !AT2.tolak && at2.sisihKg === 12 && !!susunAturWadah({ penuhKg: '50', isiUlangKg: '10', sisihKg: '0', daftar: ['Apex Baru', 'Angsa'] }, W).tolak, J([AT2.tolak, at2.sisihKg]));
terapkanKeCache(AT2.dokumen || []);
ok('sisihkan kosong memakai angka owner (12 kg)', dok(wbSusunSisih('Apex Baru', '', W), 'produksiKemasan')[0].kgDipakai === 12);
var bw5 = B2(buku(WB5)); var h5 = hpp(WB5); var laba5 = hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih;
var BG0 = wbSusunBongkar('Apex Baru', '57', '', W, false);
ok('bongkar dengan selisih di atas susut wajar tanpa alasan DITOLAK; dengan alasan → ditanya dua ketukan', !!BG0.tolak && /alasan/.test(BG0.tolak) && wbSusunBongkar('Apex Baru', '57', 'tumpah', W, false).perluYakin === 'bongkar', J(BG0));
var BG = wbSusunBongkar('Apex Baru', '57', 'tumpah waktu bongkar', W, true); var bgs = dok(BG, 'penyesuaianStok'), bgp = dok(BG, 'produksiKemasan'), bgi = dok(BG, 'wadahLiteran').filter(function (d) { return d.tipe === 'isi'; });
ok('bongkar: penyesuaian buku wadah (57 − ' + bw5 + ') bertanda bongkar, pindah 57 kg ke karung wadah, titik samakan isi 0',
  !BG.tolak && bgs.length === 1 && bgs[0].merk === WB5 && bgs[0].selisihKg === B2(57 - bw5) && bgs[0].bongkar === true && bgp.length === 1 && J(bgp[0].sumberList) === J([{ merk: WB5, kg: 57 }]) && bgp[0].merkTujuan === KB
  && bgi.length === 1 && bgi[0].isiKg === 0 && bgi[0].dariCocok === true, J([BG.tolak, bgs, bgp, bgi]));
terapkanKeCache(BG.dokumen || []);
ok('sesudah bongkar: wadah 0 (chip 0 L), karung wadah 5 + 57 = 62 kg, laba turun persis selisih × modal wadah',
  buku(WB5) === 0 && chipL('Apex Baru').sisa === 0 && B2(buku(KB)) === 62 && B2(wbKarungWadah('Apex Baru').sisaKg) === 62 && hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih - laba5 === Math.round(B2(57 - bw5) * h5),
  J([buku(WB5), buku(KB), wbKarungWadah('Apex Baru'), hitungLabaBersihRentang('2026-09-01', '2026-09-30').labaBersih - laba5, Math.round(B2(57 - bw5) * h5)]));
ok('sesudah bongkar, atur susunan boleh melepas wadah yang sudah kosong', !susunAturWadah({ penuhKg: '50', isiUlangKg: '10', daftar: ['Angsa'] }, W).tolak);
var kw5 = kkIsi().merkKarung.filter(function (m) { return /^Karung wadah |^Adukan /.test(m.merk); });
var bocor5 = { rak: susunRak(s0()).karung.filter(function (c) { return /^Karung wadah /.test(c.kunci); }).length, harga: hgSemua(new Date(Date.now())).baris.filter(function (b) { return /^Karung wadah |^Adukan /.test(b.merk); }).length,
  masuk: calonMerkMasuk().filter(function (m) { return /^Karung wadah |^Adukan /.test(m); }).length, tumpukan: barangCocok('tumpukan').filter(function (b) { return /^Karung wadah |^Adukan /.test(b.nama); }).length };
var dr5 = deretanKarung().find(function (k) { return k.merk === KB; });
ok('karung wadah & kemasan adukan dibuka tidak dijual dari HP kasir, tidak di rak karung / harga / barang masuk / cocokkan tumpukan; tampil di deretan sebagai "karung sisihan wadah"; boleh jadi bahan adukan',
  !kw5.length && Object.keys(bocor5).every(function (k) { return bocor5[k] === 0; }) && !!dr5 && /karung sisihan wadah Apex Baru/.test(dr5.letak) && calonBahan().some(function (b) { return b.merk === KB; }) && calonBahan().some(function (b) { return b.merk === 'Adukan X KI 50 kg'; }),
  J([kw5, bocor5, dr5 && dr5.letak]));
var GN2 = wbSusunGantiNama('Apex Baru', 'Apex Dua', W); terapkanKeCache(GN2.dokumen || []);
ok('ganti nama membawa karung wadah: buku & kolam "Karung wadah Apex Dua" 62 kg, yang lama 0', !GN2.tolak && B2(buku('Karung wadah Apex Dua')) === 62 && buku(KB) === 0 && B2(wbKarungWadah('Apex Dua').sisaKg) === 62 && wbKarungWadah('Apex Baru').sisaKg === 0,
  J([GN2.tolak, buku('Karung wadah Apex Dua'), buku(KB), wbKarungWadah('Apex Dua'), wbKarungWadah('Apex Baru')]));
var kap5 = susunKapur(new Date(Date.now())).baris.map(function (x) { return x.isi; }).join(' | ');
ok('Papan Kapur: disisihkan, dituang balik, dibongkar tertulis sebagai pindah buku', /Disisihkan dari wadah Apex Baru ke karung wadahnya/.test(kap5) && /Karung sisihan dituang balik ke wadah Apex Baru/.test(kap5) && /Wadah Apex Baru dibongkar ke karung wadahnya/.test(kap5), kap5);

// ---- PUTARAN 39 (owner 29 Sep): karung di belakang wadah AKTIF = buku sendiri 'Karung belakang <W> · <merek>' — juga tidak bocor ke daftar MEREK
var kb39 = function (m) { return /^Karung belakang /.test(String(m)); };
var bocor39 = function () { var r = susunRak(s0()); var kini = new Date(Date.now()); var hk = kartuHpp();
  return { rakKarung: r.karung.filter(function (c) { return kb39(c.kunci); }).length, repack: r.repack.filter(function (c) { return kb39(c.kunci); }).length, literanLangsung: r.literan.filter(function (c) { return !c.wadahLiteran && kb39(c.kunci); }).length,
    calonKarung: calonKarung().filter(function (t) { return kb39(t.merk); }).length, calonCampur: calonCampur([]).filter(kb39).length, harga: hgSemua(kini).baris.filter(function (b) { return kb39(b.merk); }).length, masuk: calonMerkMasuk().filter(kb39).length,
    cocokTumpukan: barangCocok('tumpukan').filter(function (b) { return kb39(b.nama); }).length, kedatangan: daftarKedatangan(50).filter(function (b) { return /LAHIR/.test(b.pemasok); }).length, hpp: (hk.kartu || hk).filter(function (k) { return kb39(k.merk); }).length,
    tempat: barangTempat().filter(function (b) { return kb39(b.nama); }).length, belanja: daftarBelanja(kini).merk.filter(function (b) { return kb39(b.merk); }).length, lokasi: susunLokasi().filter(function (t) { return kb39(t.merk); }).length,
    katalogKasir: kkIsi().merkKarung.filter(function (m) { return kb39(m.merk); }).length, merekSaja: Object.keys(stokMerekSaja(hitungStokKarungPerMerk())).filter(kb39).length }; };
var BK39 = susunBukaKarung('NG', W, 'Angsa'); terapkanKeCache(BK39.dokumen || []); var kunci39 = kunciKarungBelakang('Angsa', 'NG');
ok('putaran 39: karung NG dibuka di belakang wadah Angsa yang AKTIF lahir sebagai buku "Karung belakang Angsa · NG" 50 kg (pindah buku NG → kunci, modal ikut), jenis belakang, merek asal NG',
  !BK39.tolak && !!hitungStokKarungPerMerk()[kunci39] && buku(kunci39) === 50 && petaBukuWadah()[kunci39].jenis === 'belakang' && merkAsalKunci(kunci39) === 'NG', J([BK39.tolak, buku(kunci39), petaBukuWadah()[kunci39]]));
var b39 = bocor39();
ok('putaran 39: kunci karung belakang tidak bocor ke daftar merek (rak karung/repack/literan langsung, karung gudang, campuran, harga, barang masuk, cocokkan tumpukan, kedatangan, HPP, tempat, belanja, lokasi, katalog HP kasir, stokMerekSaja)', Object.keys(b39).every(function (k) { return b39[k] === 0; }), J(b39));
print(J({ lulus: lulus, gagal: gagal }));
"""

ASAP = r"""
var J = JSON.stringify; var B2 = function (n) { return Math.round(n * 100) / 100; };
Object.keys(CADANGAN).forEach(function (n) { pasok(n, CADANGAN[n]); });
var nId = 900000; var W = { tanggal: TGL_CAD, jam: '23:50', kini: TGL_CAD + 'T16:50:00.000Z', idUnik: function () { nId += 1; return nId; } };
var s0 = function () { var s = keadaanAwal(); s.sekarang = new Date(Date.now()); return s; };
var nilai = function () { var st = hitungStokKarungPerMerk(); var v = 0; Object.keys(st).forEach(function (m) { v += st[m].sisaKg * st[m].hppTerakhirPerKg; }); return Math.round(v); };
var tump = function () { var o = {}; susunLokasi().forEach(function (t) { o[t.merk] = B2(t.kg); }); return o; };
var bulan = TGL_CAD.slice(0, 7); var akhir = bulan + '-' + String(new Date(Number(bulan.slice(0, 4)), Number(bulan.slice(5, 7)), 0).getDate()).padStart(2, '0');
var v0 = nilai(), t0 = tump(), laba0 = hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih;
var P = wbSusunPindahAwal(W); if (!P.tolak) terapkanKeCache(P.dokumen);
var t1 = tump(); var geserT = Object.keys(t0).filter(function (m) { return Math.abs((t1[m] || 0) - t0[m]) > 0.011; });
var jual = []; aturWadah().daftar.forEach(function (Wn) { var c = susunRak(s0()).literan.find(function (x) { return x.kunci === Wn && x.wadahLiteran; }); if (!c) return;
  var harap = Math.max(0, Math.floor(B2(hitungStokKarungPerMerk()[wbKunci(Wn)].sisaKg) / c.rasio * 10) / 10);
  var r = masukkan(Object.assign({}, s0(), { pilih: c }), 1); var s = Object.assign({}, s0(), { keranjang: r.keranjang || [] }); var N = simpanNota(Object.assign({}, s, { cara: 'QRIS' }), W);
  var rows = (N.dokumen || []).filter(function (d) { return d.koleksi === 'penjualan'; }).map(function (d) { return d.data; });
  jual.push({ w: Wn, sisa: c.sisa, harap: harap, ok: !N.tolak && rows.length === 1 && rows[0].merkSumber === wbKunci(Wn) && c.sisa === harap }); });
var kk = kkIsi(); var kwOk = aturWadah().daftar.every(function (Wn) { var e = kk.merkKarung.find(function (x) { return x.merk === wbKunci(Wn); }); var h = ambilHargaLiteran().find(function (x) { return x.merk === Wn; }); return !h || (e && e.hargaPerLiter === h.hargaPerLiter && e.karung50 === false); });
// putaran 39: satu karung dibuka (simulasi, tidak ditulis) di belakang wadah aktif pertama yang mereknya cukup → buku 'Karung belakang …' tidak boleh bocor ke daftar merek
var bocorKB = (function () { var kb = function (m) { return /^Karung belakang /.test(String(m)); }; var W1 = aturWadah().daftar.find(function (Wn) { return wbAktif(Wn); }); var M = W1 ? wbMerkAsal(karungUntukWadah(W1).merk) : ''; var st = hitungStokKarungPerMerk();
  var R = W1 && st[M] && !wbBukuKhusus(M) && st[M].sisaKg >= beratKarungBuka(M) ? susunBukaKarung(M, W, W1) : { tolak: 'tidak ada wadah aktif dengan karung merek yang cukup di buku' };
  var hitung = function () { return susunRak(s0()).karung.filter(function (c) { return kb(c.kunci); }).length + calonKarung().filter(function (t) { return kb(t.merk); }).length + hgSemua(new Date(Date.now())).baris.filter(function (b) { return kb(b.merk); }).length + calonMerkMasuk().filter(kb).length + kkIsi().merkKarung.filter(function (m) { return kb(m.merk); }).length + Object.keys(stokMerekSaja(hitungStokKarungPerMerk())).filter(kb).length; };
  return { simulasi: R.tolak || (W1 + ' ← ' + M), bocor: R.tolak ? hitung() : denganCacheSementara(R.dokumen, hitung) }; })();
print(J({ tolak: P.tolak || '', lewati: P.lewati || [], jadi: (P.jadi || []).map(function (x) { return x.W + ' ' + x.kg; }), rp: P.rp || 0, nilai: [v0, nilai()], laba: [laba0, hitungLabaBersihRentang(bulan + '-01', akhir).labaBersih], geser: geserT, jual: jual, katalog: kwOk,
  bocor: susunRak(s0()).karung.filter(function (c) { return /^Wadah /.test(c.kunci); }).length + calonKarung().filter(function (t) { return /^Wadah /.test(t.merk); }).length + hgSemua(new Date(Date.now())).baris.filter(function (b) { return /^Wadah /.test(b.merk); }).length, bocorKB: bocorKB }));
"""


def utama(js, pakai_cadangan):
    h, e = uji_wadah_bernama.jalan(JAM_TETAP + js + '\nvar KOTAK = ' + json.dumps(KOTAK) + ';\n' + SKENARIO)
    if h is None: return 0, ['JSC JATUH: ' + e], None
    asap = None
    p = uji_wadah_bernama.cadangan_toko() if pakai_cadangan else None
    if p:
        cad, tgl = uji_wadah_bernama.cad_js(p)
        a, e2 = uji_wadah_bernama.jalan(JAM_TETAP.replace('2026-09-20T10:00:00', tgl + 'T23:00:00') + js + '\nvar CADANGAN = ' + cad + ';\nvar TGL_CAD = ' + json.dumps(tgl) + ';\n' + ASAP)
        asap = a if a is not None else {'jatuh': e2[-400:]}
    return h['lulus'], h['gagal'], asap


def bundel():
    """Bundel satu lingkup: harga-logika & stok-hpp-logika sama-sama punya `const teksMargin` — di bagian stok-hpp diganti nama (khusus uji ini)."""
    js = bundel_baru.bundel(MODUL); tanda = '// ===== baru/js/layar/stok-hpp-logika.js ====='
    i = js.index(tanda); j = js.find('// ===== ', i + len(tanda)); j = len(js) if j < 0 else j
    return js[:i] + js[i:j].replace('teksMargin', 'teksMarginHpp') + js[j:]


RUSAK = {
    'wadah aktif tetap dibaca komposisi merek asal': ("  if (wbAktif(W)) {   // putaran 28: stok wadah sendiri", "  if (false) {   // putaran 28: stok wadah sendiri"),
    'buku wadah tidak dikenali (baris stokWadah diabaikan)': ("if (m && m.stokWadah && m.merk) out[String(m.merk)] = String(m.stokWadah);", "if (false) out[String(m.merk)] = String(m.stokWadah);"),
    'daftar merek memuat buku wadah': ("if (!w[m]) out[m] = stok[m];", "out[m] = stok[m];"),
    'pindahan tanpa batch lahir (penjualan wadah tidak terpotong)': ("const lahir = wbDokLahir(jadi.map(", "const lahir = null && wbDokLahir(jadi.map("),
    'pindah buku tanpa modal (nilai stok berubah)': ("hppSumberPerKgDipakai: kg > 0 ? nilai / kg : 0, hppPerUnit: nilai, sumberList: list,", "hppSumberPerKgDipakai: 0, hppPerUnit: 0, sumberList: list,"),
    'pindah buku tanpa tanda dariTakar (muncul di daftar adukan)': ("batchProduksi: id, barisKe: 1, jumlahBaris: 1, jadiKarungUtuh: true, merkTujuan: tujuan, dariTakar: true }", "batchProduksi: id, barisKe: 1, jumlahBaris: 1, jadiKarungUtuh: true, merkTujuan: tujuan }"),
    'takar wadah aktif tidak memindah buku': ("    dokumen.push(pindah);\n", "\n"),
    'takar dari karung tanpa buku lolos': ("if (tanpa.length) return { tolak: 'Karung '", "if (false) return { tolak: 'Karung '"),
    'tinggi wadah aktif dihitung dari catatan isi, bukan buku': ("const nyata = aktif ? wdB2(", "const nyata = false ? wdB2("),
    'wadah kosong menjual dari karung di belakangnya': ("function wbMerkCadangan(W) { if (wbAktif(W)) return wbKunci(W);", "function wbMerkCadangan(W) {"),
    'pindahan awal dianggap hitungan (penjaga "baru saja dicocokkan")': ("if (d.tipe === 'isi' && d.wadah && !d.pindahAwal) catat('wadah|' + d.wadah, d);", "if (d.tipe === 'isi' && d.wadah) catat('wadah|' + d.wadah, d);"),
    'panel Jual menyamakan wadah aktif tanpa alasan': ("  if (wbAktif(merk)) return { tolak: 'Wadah ' + merk + ' punya stok sendiri", "  if (false) return { tolak: 'Wadah ' + merk + ' punya stok sendiri"),
    'ganti nama tidak membawa stok wadah': ("    if (K.totalKg > 0.004) dokumen.push(wbDokPindah([{ merk: K.kunci", "    if (false) dokumen.push(wbDokPindah([{ merk: K.kunci"),
    'atur susunan melepas wadah berstok': ("if (yatim.length) return { tolak: 'Wadah '", "if (false) return { tolak: 'Wadah '"),
    'katalog kasir: buku wadah tanpa harga liter': ("hargaPerLiter: h ? Number(h.hargaPerLiter) || 0 : 0, rasio: wbRasio(W) });", "hargaPerLiter: 0, rasio: wbRasio(W) });"),
    'katalog kasir: merek bernama wadah tetap menjual literan': ("if (aktifNama[m.merk] && langsung.indexOf(m.merk) < 0 && x.hargaPerLiter) return", "if (false) return"),
    'barang masuk menerima nama buku wadah': ("wadahStok[merk] ? merk + ' itu buku KHUSUS", "false ? merk + ' itu buku KHUSUS"),
    'buka kemasan tidak menurunkan stok kemasan': ("sumberKemasanList: [{ namaProduk: N, ukuranKemasan: uk, unit: 1 }]", "sumberKemasanList: []"),
    'pintu "baru datang" tanpa pemeriksaan kedatangan': ("if (!b || b.stokAwal || b.tutupBuku || !(b.merkList || []).some((m) => m.merk === merk && m.satuan === 'karung')) return", "if (false) return"),
    'batch lahir tampil di buku kedatangan': ("const semua = ambilSemuaBatch().filter((b) => !b.lahirBuku).sort(", "const semua = ambilSemuaBatch().slice().sort("),
    'tutup buku kehilangan tanda stok wadah': ("merkList.forEach((r) => { if (pw[r.merk]) r.stokWadah = pw[r.merk]; else if (bw[r.merk] && bw[r.merk].jenis === 'belakang') { r.karungBelakang = bw[r.merk].wadah; r.merkAsal = bw[r.merk].merk; } else if (bw[r.merk]) r.karungWadah = bw[r.merk].wadah; });", "merkList.forEach((r) => { });"),
    'karung wadah tidak dikenali sebagai buku khusus': ("else if (m.karungWadah) out[String(m.merk)] = { jenis: 'karung', wadah: String(m.karungWadah) };", "else if (false) out[String(m.merk)] = { jenis: 'karung', wadah: String(m.karungWadah) };"),
    'kemasan adukan dibuka masuk buku merek pemasok': ("const B = kunciBukuAdukan(N, uk);", "const B = N;"),
    'sisihkan melebihi isi wadah lolos': ("if (kg > K.totalKg + 0.004) return { tolak: 'Wadah ' + W + ' menurut bukunya", "if (false) return { tolak: 'Wadah ' + W + ' menurut bukunya"),
    'tuang balik melewati batas menggunung': ("if (isiBaru > A.puncakKg + 0.0001) return { tolak: 'Dituang '", "if (false) return { tolak: 'Dituang '"),
    'bongkar tanpa penyesuaian selisih timbang': ("if (Math.abs(sel) >= 0.005) dokumen.push({ koleksi: 'penyesuaianStok'", "if (false) dokumen.push({ koleksi: 'penyesuaianStok'"),
    'bongkar tanpa alasan di atas susut wajar': ("if (Math.abs(sel) > wajar + 0.0001 && !al) return", "if (false) return"),
    'ganti nama meninggalkan karung wadah': ("if (KWL && KWL.lahir && (KWL.bukuKg > 0.004 || KWL.sisaKg > 0.004)) {", "if (false) {"),
    'karung wadah dijual dari HP kasir': ("const merkKarung = isi.merkKarung.filter((m) => !(bw[m.merk] && bw[m.merk].jenis !== 'wadah') &&", "const merkKarung = isi.merkKarung.filter((m) =>"),
    'angka "disisihkan saat tutup" owner diabaikan': ("const sisihKg = a && Number(a.sisihKg) > 0 ? Number(a.sisihKg) : WADAH_SISIH_KG;", "const sisihKg = WADAH_SISIH_KG;"),
}

if __name__ == '__main__':
    js = bundel()
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, (a, b) in RUSAK.items():
            if js.count(a) != 1: print('KONTROL BASI  ' + nama + ' (jangkar ' + str(js.count(a)) + '×)'); kode = 3; continue
            l, g, _ = utama(js.replace(a, b), False)
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:140] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g, asap = utama(js, True)
    print('STOK WADAH SENDIRI (kotak pasir): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = uji_wadah_bernama.cadangan_toko()
    if asap:
        if 'jatuh' in asap: g.append('asap data toko JATUH: ' + asap['jatuh']); print('   ✗ ' + g[-1])
        else:
            baik = [x for x in asap['jual'] if x['ok']]
            print('ASAP DATA TOKO (%s): pindahan awal %d wadah (%s) · modal ikut Rp%s · dilewati: %s · nilai stok %s → %s · laba bulan itu %s → %s · tumpukan bergeser: %s · 1 L dari buku wadah sendiri: %d/%d · katalog kasir berharga wadah: %s · buku wadah bocor ke daftar merek: %d'
                  % (os.path.basename(p), len(asap['jadi']), ', '.join(asap['jadi']), format(asap['rp'], ',').replace(',', '.'), '; '.join(asap['lewati']) or 'tidak ada', asap['nilai'][0], asap['nilai'][1], asap['laba'][0], asap['laba'][1],
                     ', '.join(asap['geser']) or 'tidak ada', len(baik), len(asap['jual']), asap['katalog'], asap['bocor']))
            if asap['tolak'] or asap['nilai'][0] != asap['nilai'][1] or asap['laba'][0] != asap['laba'][1] or asap['geser'] or len(baik) != len(asap['jual']) or not asap['jual'] or not asap['katalog'] or asap['bocor']:
                g.append('asap data toko: ' + json.dumps(asap, ensure_ascii=False)[:500])
            # putaran 39: buku karung belakang (simulasi buka satu karung di belakang wadah aktif) tidak bocor ke daftar merek / katalog kasir
            kb = asap.get('bocorKB') or {'simulasi': 'tidak dihitung', 'bocor': 0}
            print('   putaran 39 — kunci karung belakang bocor ke daftar merek (simulasi %s): %d' % (kb['simulasi'], kb['bocor']))
            if kb['bocor']: g.append('asap data toko (39): kunci karung belakang bocor ' + json.dumps(kb, ensure_ascii=False))
    sys.exit(2 if g else 0)
