#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_keranjang_tahan.py — owner 7 Okt 2026 ("Ya, simpan di perangkat"): keranjang & nota PARKIR Jual BERTAHAN saat halaman dimuat ulang.
Layar Jual ASLI (baru/js/layar/jual.js) dijalankan di jsc dengan tiruan peramban (pola uji_cache_chip_literan) + penyimpanan SESI tiruan + jendela tiruan
(pagehide / pageshow). KOTAK PASIR = uji_rak_inkremental.KOTAK (angka & nama CONTOH), jam dikunci 21 Sep 2026 10:00 WIB.
  · yang disimpan: keranjang, struk parkir, struk aktif, pelanggan, cara bayar, potongan, ikatan pesanan — per AKUN (uid) + TANGGAL + TAB; TIDAK: tukar, karcis
    yang dirinci, nota terakhir, uang diterima, buka kredit sekali;
  · muat ulang (halaman lama menerima pagehide, layar baru di atas penyimpanan yang sama) + akun yang sama hari itu → dipulihkan persis, kabar menyebutnya, cermin
    stok yang dipegang (sinkronKeranjang) ikut; akun lain / hari lain → TIDAK dipulihkan dan simpanannya dibuang; layar yang sudah berisi tidak ditimpa;
  · nota tercatat & keranjang kosong → simpanan dihapus (parkir tersisa tetap); ganti orang (lupakanOrang) → dihapus & berhenti menyimpan;
  · sebelum pemulihan dicoba layar TIDAK menulis simpanan keranjang (muat ulang tidak menghapusnya sebelum sempat dipulihkan);
  · penyimpanan melempar (mode privat Safari / penuh) → keranjang tetap jalan, tidak jatuh; simpanan terlalu besar tidak ditulis.
  Tinjauan 7 Okt (sanggahan):
  · NOTA GANDA: halaman dimuat ulang SELAGI nota menunggu server (dokumennya sudah di antrean perangkat) → keranjang itu TIDAK dipulihkan (penanda "sedang
    mencatat"), mencatat lagi ditolak "Keranjang kosong", total tetap SATU nota; ketukan lain selama menunggu tidak mengembalikannya; ditolak / gagal → simpanan
    biasa kembali (keranjang masih bisa dicatat); tercatat → simpanan tanpa keranjang & tanpa penanda;
  · TAB SALINAN ("Duplikat tab" menyalin penyimpanan sesi): id tab baru, keranjang tab asal tidak dipulihkan, kabar menyebutnya; tab asal yang dimuat ulang tetap
    memulihkan miliknya; kembali dari tembolok mundur → tanda "dipakai" lagi;
  · HARGA & MODAL: baris yang dipulihkan dibangun ulang dari katalog SEKARANG saat nota dicatat — cuma modal berubah → dipakai diam-diam (dokumen membawa modal
    baru); harga berubah → nota DITAHAN, keranjang diperbarui, uang diterima dikosongkan; nego yang tidak sah lagi → dilepas & disebut.

    python3 alat-uji/uji_keranjang_tahan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_keranjang_tahan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import uji_wadah_bernama, uji_cache_chip_literan, uji_rak_inkremental  # noqa: E402

SKENARIO = uji_rak_inkremental.BANTU + r"""
// penyimpanan SESI tiruan (peramban: per tab); __ssRusak = melempar seperti mode privat Safari
var __ss = {}; var __ssRusak = false;
var sessionStorage = { getItem: function (k) { if (__ssRusak) throw new Error('SecurityError'); return Object.prototype.hasOwnProperty.call(__ss, k) ? __ss[k] : null; },
  setItem: function (k, v) { if (__ssRusak) throw new Error('QuotaExceededError'); __ss[k] = String(v); }, removeItem: function (k) { if (__ssRusak) throw new Error('SecurityError'); delete __ss[k]; } };
var KUNCI = KUNCI_SIMPAN_KERANJANG, KUNCI_TAB = KUNCI_TAB_KERANJANG;
var simpanan = function () { return __ss[KUNCI] ? JSON.parse(__ss[KUNCI]) : null; };
var tandaTab = function () { return __ss[KUNCI_TAB] ? JSON.parse(__ss[KUNCI_TAB]) : null; };
// jendela tiruan: penangan pagehide / pageshow yang didaftarkan SATU halaman (layar Jual) — dicatat per halaman
var window = { __baru: [], addEventListener: function (n, f) { window.__baru.push({ n: n, f: f }); } };
var picu = function (X, n, e) { X.h.filter(function (x) { return x.n === n; }).forEach(function (x) { x.f(e || {}); }); };
var AKUN_A = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'uid-a' }, AKUN_B = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'uid-b' };
var akunKini = AKUN_A;
var opsiJ = function () { return { akun: function () { return akunKini; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null }; };
var KINI = new Date(Date.now());
// halaman baru = layar Jual baru di atas penyimpanan sesi yang ada; layar menggambar diri & pindah jalur dulu (seperti app.js) sebelum akun diketahui
var pasang = function () { window.__baru = []; var a = __akar(); var L2 = pasangLayarJual(a, opsiJ()); var h = window.__baru; L2.keadaan.setel({ jalur: 'karung', sekarang: KINI }); return { a: a, L: L2, h: h, s: function () { return L2.keadaan.baca(); } }; };
// MUAT ULANG tab yang sama = halaman lama menerima pagehide, lalu halaman baru dipasang
var muatUlang = function (X) { picu(X, 'pagehide', { persisted: false }); return pasang(); };
var rakDari = function (s) { sinkronKeranjang(s); return susunRak(s); };
var sisaChip = function (s) { var r = rakDari(s); return r.karung.concat(r.kemasan, r.literan, r.repack).map(function (c) { return c.jalur + ':' + c.kunci + ':' + (c.berat || '') + '=' + c.sisa; }).join('|'); };
var masuk = function (X, jalur, pilih, n) { var c = rakDari(X.s())[jalur].filter(pilih)[0]; var r = masukkan(Object.assign({}, X.s(), { pilih: c }), n); X.L.keadaan.setel({ keranjang: r.keranjang, urutBaris: r.urutBaris }); return r; };
var NG50 = function (c) { return c.kunci === 'NG' && c.berat === 50; }, KMB = function (c) { return c.kunci === 'Kembang|5'; };
var jualDok = function (r) { return (r.dokumen || []).filter(function (d) { return d.koleksi === 'penjualan'; }).map(function (d) { return d.data; }); };

// ---- 0 · tanda tab
var tb0 = bacaTandaTab(null, 'baru1'), tb1 = bacaTandaTab({ id: 't1', ditinggal: true }, 'baru2'), tb2 = bacaTandaTab({ id: 't1', ditinggal: false }, 'baru3');
var tb3 = bacaTandaTab({ id: 't1', ditinggal: false }, 'baru4', true);
ok('tanda tab: tanpa tanda = tab baru (id baru); "ditinggal" (pagehide) = tab yang SAMA dimuat ulang (id tetap); masih "dipakai" = SALINAN (id baru); web app layar penuh (tanpa tab) = tab yang sama',
  tb0.asal === 'baru' && tb0.id === 'baru1' && tb1.asal === 'muatUlang' && tb1.id === 't1' && tb2.asal === 'salinan' && tb2.id === 'baru3' && tb3.asal === 'muatUlang' && tb3.id === 't1', J([tb0, tb1, tb2, tb3]));

// ---- 1 · pertama dibuka: belum ada simpanan, pemulihan dicoba → mulai menyimpan
var X = pasang(); var TAB1 = tandaTab() && tandaTab().id;
ok('sebelum akun diketahui layar TIDAK menulis simpanan keranjang — cuma tanda tab "dipakai"', !(KUNCI in __ss) && Object.keys(__ss).length === 1 && tandaTab().ditinggal === false && !!TAB1, J(__ss));
X.L.pulihkanKeranjang(AKUN_A);
masuk(X, 'karung', function (c) { return c.kunci === 'NG'; }, 2);
masuk(X, 'kemasan', KMB, 1);
X.L.keadaan.setel(parkir(Object.assign({}, X.s(), { pelanggan: 'Pembeli Contoh A' })));
masuk(X, 'karung', function (c) { return c.kunci === 'Kumala'; }, 1);
X.L.keadaan.setel({ pelanggan: 'Pembeli Contoh B', cara: 'QRIS', potongan: 2000, uang: 50000, kreditDibuka: true, notaTerakhir: { trxId: 'x', idPenjualan: [], pada: Date.now(), ringkas: 'x' } });
var S1 = simpanan(); var sAsli = X.s(); var sisaAsli = sisaChip(sAsli);
ok('tersimpan per akun + tanggal hari ini + TAB: keranjang 1 baris, 1 struk parkir (2 baris), pelanggan, cara bayar QRIS, potongan, struk aktif',
  S1 && S1.v === 1 && S1.uid === 'uid-a' && S1.tanggal === hariIniIso(KINI) && S1.tab === TAB1 && S1.isi.keranjang.length === 1 && S1.isi.antrean.length === 1 && S1.isi.antrean[0].beku.items.length === 2
  && S1.isi.pelanggan === 'Pembeli Contoh B' && S1.isi.cara === 'QRIS' && S1.isi.potongan === 2000 && S1.isi.aktifId === sAsli.aktifId && !S1.isi.mencatat, J(S1));
ok('TIDAK disimpan: uang diterima, buka kredit sekali, nota terakhir (juga di struk parkir: uang 0, kredit tertutup, tanpa tukar)',
  !('uang' in S1.isi) && !('kreditDibuka' in S1.isi) && !('notaTerakhir' in S1.isi) && S1.isi.antrean[0].beku.uang === 0 && S1.isi.antrean[0].beku.kreditDibuka === false && S1.isi.antrean[0].beku.tukar === null, J(S1.isi.antrean[0].beku));

// ---- 2 · muat ulang, akun yang sama → dipulihkan persis + stok yang dipegang ikut
var Y = muatUlang(X);
ok('muat ulang: tab yang sama (id tetap), layar baru mulai kosong, simpanan BELUM terhapus oleh gambar & pindah jalur pertama', tandaTab().id === TAB1 && tandaTab().ditinggal === false && Y.s().keranjang.length === 0 && !!simpanan(), J([tandaTab(), simpanan()]));
Y.L.pulihkanKeranjang(AKUN_A); var sY = Y.s();
ok('akun sama hari yang sama → keranjang, struk parkir, struk aktif, pelanggan, cara, potongan DIPULIHKAN persis; uang 0, kredit tertutup, nota terakhir tidak ikut',
  J(sY.keranjang) === J(sAsli.keranjang) && J(sY.antrean.map(function (a) { return a.beku.items; })) === J(sAsli.antrean.map(function (a) { return a.beku.items; })) && sY.aktifId === sAsli.aktifId && sY.idBerikut === sAsli.idBerikut
  && sY.pelanggan === 'Pembeli Contoh B' && sY.cara === 'QRIS' && sY.potongan === 2000 && sY.uang === 0 && sY.kreditDibuka === false && !sY.notaTerakhir && /dipulihkan sesudah halaman dimuat ulang: 1 barang · 1 struk parkir/.test(sY.kabar), J([sY.keranjang.length, sY.antrean.length, sY.kabar]));
ok('kabar pemulihan TIDAK berbohong: harga & modal memang diperiksa lagi saat nota dicatat (baris pulihan ditandai: 1 di keranjang + 2 di struk parkir)',
  /stok, harga & modal diperiksa lagi dengan katalog sekarang/.test(sY.kabar) && sY.pulihPeriksa.length === 3 && sY.pulihPeriksa.indexOf(sY.keranjang[0].id) >= 0, J([sY.kabar, sY.pulihPeriksa]));
ok('cermin stok yang dipegang ikut pulih: sisa tiap chip rak = sebelum dimuat ulang (keranjang + struk parkir memegang barangnya)', sisaChip(sY) === sisaAsli && sisaAsli !== sisaChip(keadaanAwal()), sisaChip(sY) + ' ≠ ' + sisaAsli);
var hY = Y.a.__html || '';
ok('layar tergambar dengan keranjang & bilah struk parkir yang dipulihkan', hY.indexOf('Pembeli Contoh A') >= 0 && hY.indexOf('1 barang') >= 0, hY.slice(0, 200));
Y.L.pulihkanKeranjang(AKUN_A);
ok('pemulihan kedua untuk akun yang sama tidak mengulang apa pun', J(Y.s().keranjang) === J(sY.keranjang) && Y.s().antrean.length === 1);

// ---- 3 · akun lain / hari lain → tidak dipulihkan, simpanan dibuang
var Z = muatUlang(Y); Z.L.pulihkanKeranjang(AKUN_B);
ok('akun LAIN di tab yang sama → keranjang akun A TIDAK dipulihkan dan simpanannya dibuang', Z.s().keranjang.length === 0 && Z.s().antrean.length === 0 && simpanan() === null, J(simpanan()));
__ss[KUNCI] = JSON.stringify(Object.assign({}, S1, { tanggal: '2026-09-20' }));
var Z2 = muatUlang(Z); Z2.L.pulihkanKeranjang(AKUN_A);
ok('simpanan KEMARIN (tab sama) → tidak dipulihkan dan dibuang', tandaTab().id === TAB1 && Z2.s().keranjang.length === 0 && !/salinan/.test(Z2.s().kabar || '') && simpanan() === null, J([simpanan(), Z2.s().kabar]));
__ss[KUNCI] = JSON.stringify(S1);
var Z3 = muatUlang(Z2); masuk(Z3, 'karung', function (c) { return c.kunci === 'Angsa' && c.berat === 50; }, 1); Z3.L.pulihkanKeranjang(AKUN_A);
ok('layar yang SUDAH berisi tidak ditimpa simpanan (keranjang yang sedang jalan menang)', Z3.s().keranjang.length === 1 && Z3.s().keranjang[0].trx.merkSumber === 'Angsa' && Z3.s().antrean.length === 0 && simpanan().isi.keranjang[0].trx.merkSumber === 'Angsa', J(Z3.s().keranjang));

// ---- 4 · tukar & karcis tidak disimpan
var T = muatUlang(Z3); T.L.pulihkanKeranjang(AKUN_A); T.L.keadaan.setel({ keranjang: [], antrean: [] });
masuk(T, 'karung', function (c) { return c.kunci === 'NG'; }, 1); T.L.keadaan.setel(parkir(Object.assign({}, T.s(), { tukar: { ringkas: 'tukar contoh', kredit: 1000, returDraf: { id: 'r1' } } })));
masuk(T, 'kemasan', KMB, 1); T.L.keadaan.setel(parkir(T.s()));
masuk(T, 'karung', function (c) { return c.kunci === 'Kumala'; }, 1); T.L.keadaan.setel({ tukar: { ringkas: 'tukar aktif', kredit: 500, returDraf: { id: 'r2' } } });
var ST = simpanan();
ok('struk parkir yang terikat TUKAR tidak disimpan; keranjang aktif yang terikat tukar tidak disimpan (barisnya juga); struk parkir lain tetap', ST && ST.isi.antrean.length === 1 && ST.isi.antrean[0].beku.items[0].trx.jenis === 'kemasan' && ST.isi.keranjang.length === 0 && !('pelanggan' in ST.isi), J(ST));
T.L.keadaan.setel({ tukar: null, karcis: { id: 'k1', nominal: 10000 } });
ok('keranjang yang sedang MERINCI KARCIS tidak disimpan', simpanan().isi.keranjang.length === 0, J(simpanan().isi));
T.L.keadaan.setel({ karcis: null });
ok('ikatan lepas → keranjang aktif ikut tersimpan lagi', simpanan().isi.keranjang.length === 1);

// ---- 5 · nota tercatat / kosong / ganti orang
var N = simpanNota(Object.assign({}, T.s(), { uang: 1e9 }), W); T.L.keadaan.setel(N.patch);
ok('nota tercatat → keranjang aktif kosong; simpanan tinggal struk parkir yang boleh disimpan (yang bertukar tidak; notaTerakhir tidak ikut)', !N.tolak && simpanan() && simpanan().isi.keranjang.length === 0 && simpanan().isi.antrean.length === 1 && T.s().antrean.length === 2 && !('notaTerakhir' in simpanan().isi), J([N.tolak, simpanan()]));
while (T.s().antrean.length) T.L.keadaan.setel(buangAntrean(T.s(), T.s().antrean[0].id));
ok('keranjang & parkir kosong → simpanan DIHAPUS (tanda tab tetap)', simpanan() === null && Object.keys(__ss).length === 1 && !!tandaTab(), J(__ss));
masuk(T, 'karung', function (c) { return c.kunci === 'NG'; }, 1);
ok('mulai lagi → tersimpan lagi', !!simpanan());
T.L.lupakanOrang();
ok('ganti orang (lupakanOrang) → simpanan DIHAPUS', simpanan() === null);
T.L.keadaan.setel({ keranjang: rakDari(T.s()).karung.length ? masukkan(Object.assign({}, T.s(), { pilih: rakDari(T.s()).karung[0] }), 1).keranjang : [] });
ok('sesudah ganti orang layar BERHENTI menyimpan sampai akun berikutnya dipulihkan', simpanan() === null, J(simpanan()));

// ---- 6 · penyimpanan melempar & terlalu besar
var P = pasang(); __ssRusak = true; var jatuh = '';
try { P.L.pulihkanKeranjang(AKUN_A); masuk(P, 'karung', function (c) { return c.kunci === 'NG'; }, 1); } catch (e) { jatuh = String(e); }
__ssRusak = false;
ok('penyimpanan melempar (mode privat / penuh) → tidak jatuh, keranjang tetap jalan', !jatuh && P.s().keranjang.length === 1, jatuh);
var besar = { aktifId: 1, idBerikut: 2, urutBaris: 1, keranjang: [{ id: 'b1', trx: { jenis: 'karung', label: new Array(BATAS_SIMPAN_KERANJANG + 10).join('x') } }], antrean: [] };
ok('simpanan lebih dari batas tidak ditulis (null → dihapus)', susunSimpanKeranjang(besar, 'uid-a', '2026-09-21') === null && susunSimpanKeranjang(Object.assign({}, besar, { keranjang: [{ id: 'b1', trx: { jenis: 'karung', label: 'x' } }] }), 'uid-a', '2026-09-21') !== null);
ok('tanpa akun / tanpa tanggal → tidak ada simpanan; simpanan rusak / versi lain → tidak dipulihkan', susunSimpanKeranjang(sAsli, '', '2026-09-21') === null && pulihSimpanKeranjang({ v: 2, uid: 'uid-a', tanggal: '2026-09-21', isi: S1.isi }, 'uid-a', '2026-09-21', keadaanAwal()) === null
  && pulihSimpanKeranjang({ v: 1, uid: 'uid-a', tanggal: '2026-09-21', isi: { keranjang: [{ id: 'b1' }], antrean: 'x' } }, 'uid-a', '2026-09-21', keadaanAwal()) === null);
var pm = pulihSimpanKeranjang({ v: 1, uid: 'uid-a', tanggal: '2026-09-21', tab: 't9', isi: { keranjang: [{ id: 'b1', trx: { jenis: 'karung', label: 'x' } }], antrean: [], aktifId: 1, idBerikut: 2, urutBaris: 1, mencatat: { trxId: 'trx-tak-ada', ringkas: '1 barang' } } }, 'uid-a', '2026-09-21', keadaanAwal(), 't9');
ok('penanda "sedang mencatat" di simpanan → keranjangnya TIDAK dipulihkan walau barisnya ada di simpanan (lapis kedua), kabar awas menyuruh periksa Riwayat', pm && pm.keranjang.length === 0 && pm.kabarAwas && /TIDAK dipulihkan/.test(pm.kabar) && /Periksa Riwayat/.test(pm.kabar), J(pm));

// ---- 7 · NOTA GANDA (sanggahan berat): muat ulang SELAGI nota menunggu server
__ss = {}; var G = pasang(); var TABG = tandaTab().id; G.L.pulihkanKeranjang(AKUN_A);
masuk(G, 'kemasan', KMB, 1); G.L.keadaan.setel(parkir(Object.assign({}, G.s(), { pelanggan: 'Pembeli Contoh P' })));
masuk(G, 'karung', NG50, 1); G.L.keadaan.setel(uangPas(G.s()));
var nPj0 = ambilPenjualan().length; var idKeranjangG = G.s().keranjang[0].id;
setelPenulis({ tulis: function (d) { terapkanKeCache(d); return new Promise(function () {}); } });   // dokumen sudah di cache/antrean, server belum menjawab
G.a.__aksi.catatNotaInti(false);
var sM = simpanan(); var trxG = sM && sM.isi.mencatat && sM.isi.mencatat.trxId;
ok('nota sedang dicatat (dokumen sudah di antrean perangkat, server belum menjawab) → simpanan TIDAK lagi memegang keranjang itu, diganti penanda nota; struk parkir tetap',
  ambilPenjualan().length - nPj0 === 1 && sM && sM.isi.keranjang.length === 0 && !!trxG && ambilPenjualan().some(function (p) { return String(p.trxId) === String(trxG); }) && sM.isi.antrean.length === 1 && G.s().keranjang.length === 1, J(sM));
G.L.keadaan.setel({ kabar: 'ketukan lain selama menunggu' });
ok('ketukan lain selama menunggu TIDAK mengembalikan keranjang itu ke simpanan (penanda bertahan)', simpanan().isi.keranjang.length === 0 && simpanan().isi.mencatat && simpanan().isi.mencatat.trxId === trxG, J(simpanan()));
var G2 = muatUlang(G); G2.L.pulihkanKeranjang(AKUN_A); setelPenulis(null);
ok('muat ulang di jendela itu → keranjang yang notanya sudah dikirim TIDAK dipulihkan; struk parkir dipulihkan; kabar: nota SUDAH tercatat (ada di cache)',
  G2.s().keranjang.length === 0 && G2.s().antrean.length === 1 && /SUDAH tercatat/.test(G2.s().kabar) && /1 struk parkir dipulihkan/.test(G2.s().kabar), J([G2.s().keranjang.length, G2.s().antrean.length, G2.s().kabar]));
var rG = simpanNota(Object.assign({}, G2.s(), { uang: 1e9 }), W);
ok('mencatat lagi sesudah muat ulang → DITOLAK "Keranjang kosong" — tetap SATU nota (dulu: dipulihkan lalu tercatat dua kali)', rG.tolak === 'Keranjang kosong' && ambilPenjualan().length - nPj0 === 1, J([rG.tolak, ambilPenjualan().length - nPj0]));
ok('penanda dilepas sesudah dipulihkan: simpanan berikutnya tanpa penanda (tinggal struk parkir)', simpanan() && !simpanan().isi.mencatat && simpanan().isi.antrean.length === 1, J(simpanan()));
// nota belum terlihat di cache (mis. data belum termuat) → tetap TIDAK dipulihkan, kabar menyuruh memeriksa Riwayat
__ss = {}; var G3 = pasang(); G3.L.pulihkanKeranjang(AKUN_A); masuk(G3, 'karung', NG50, 1); G3.L.keadaan.setel(uangPas(G3.s()));
setelPenulis({ tulis: function () { return new Promise(function () {}); } }); G3.a.__aksi.catatNotaInti(false);
var G4 = muatUlang(G3); G4.L.pulihkanKeranjang(AKUN_A); setelPenulis(null);
ok('nota belum terlihat di data perangkat → keranjang tetap TIDAK dipulihkan; kabar AWAS: periksa Riwayat, kalau belum ada masukkan lagi', G4.s().keranjang.length === 0 && G4.s().kabarAwas && /Periksa Riwayat dulu/.test(G4.s().kabar), J(G4.s().kabar));

// ---- 8 · TAB SALINAN ("Duplikat tab" menyalin penyimpanan sesi; tab asal masih terbuka)
__ss = {}; var D1 = pasang(); D1.L.pulihkanKeranjang(AKUN_A); masuk(D1, 'karung', NG50, 1);
var tabAsal = tandaTab().id; var ssAsal = JSON.parse(J(__ss));
var D2 = pasang(); D2.L.pulihkanKeranjang(AKUN_A);
ok('tab SALINAN → id tab baru, keranjang tab asal TIDAK dipulihkan, kabar awas menyebut salinan; simpanan salinan tidak memegang keranjang tab asal',
  tandaTab().id !== tabAsal && D2.s().keranjang.length === 0 && /salinan/.test(D2.s().kabar) && D2.s().kabarAwas && simpanan() === null, J([tandaTab(), D2.s().kabar, simpanan()]));
masuk(D2, 'karung', function (c) { return c.kunci === 'Kumala'; }, 1);
ok('tab salinan menyimpan keranjangnya SENDIRI dengan id tabnya', simpanan() && simpanan().tab === tandaTab().id && simpanan().isi.keranjang[0].trx.merkSumber === 'Kumala');
__ss = ssAsal; var D3 = muatUlang(D1); D3.L.pulihkanKeranjang(AKUN_A);
ok('tab ASAL dimuat ulang → id tab tetap, keranjangnya sendiri dipulihkan', tandaTab().id === tabAsal && D3.s().keranjang.length === 1 && D3.s().keranjang[0].trx.merkSumber === 'NG', J([tandaTab(), D3.s().keranjang.length]));
// web app layar penuh dimatikan iOS di latar (TANPA pagehide) lalu dibuka lagi → tetap tab yang sama, keranjangnya pulih (tidak ada tab untuk digandakan)
window.matchMedia = function (q) { return { matches: q === '(display-mode: standalone)' }; };
var D4 = pasang(); D4.L.pulihkanKeranjang(AKUN_A); delete window.matchMedia;
ok('web app LAYAR PENUH dibuka lagi tanpa pagehide (iOS mematikannya di latar) → id tab tetap, keranjang dipulihkan', tandaTab().id === tabAsal && D4.s().keranjang.length === 1 && !/salinan/.test(D4.s().kabar), J([tandaTab(), D4.s().kabar]));
picu(D3, 'pagehide', { persisted: true }); var tPh = tandaTab().ditinggal; picu(D3, 'pageshow', { persisted: true });
ok('masuk tembolok mundur (pagehide) lalu kembali (pageshow persisted) → tanda kembali "dipakai" — salinan sesudahnya tetap terdeteksi', tPh === true && tandaTab().ditinggal === false && tandaTab().id === tabAsal);

// ---- 9 · baris pulihan dibangun ulang dari katalog SEKARANG (bukan cuma stok)
__ss = {}; var R1 = pasang(); R1.L.pulihkanKeranjang(AKUN_A); masuk(R1, 'karung', NG50, 1); masuk(R1, 'kemasan', KMB, 1);
var idNG = R1.s().keranjang[0].id, idKm = R1.s().keranjang[1].id; var hNG = R1.s().keranjang[0].trx.hargaAsli, mNG = R1.s().keranjang[0].trx.hppTotalSaatJual;
R1.L.keadaan.setel(terapkanNego(Object.assign({}, R1.s(), { negoAkun: AKUN_A, negoHak: 'sendiri' }), idNG, mNG + 20000));
var R2 = muatUlang(R1); R2.L.pulihkanKeranjang(AKUN_A); var simpanR = __ss[KUNCI];
var catat = function (X) { return simpanNota(Object.assign({}, X.s(), { uang: 1e9, negoAkun: AKUN_A, negoHak: 'sendiri' }), W); };
var r9a = catat(R2);
ok('pulihan TANPA perubahan katalog → tercatat apa adanya (harga nego tetap, modal sama)', !r9a.tolak && jualDok(r9a)[0].hargaTotal === mNG + 20000 && jualDok(r9a)[0].hppTotalSaatJual === mNG, J([r9a.tolak, jualDok(r9a)[0]]));
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'b-uji-2', tanggal: '2026-09-20', jam: '08:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0,
  merkList: [{ id: '1', merk: 'NG', satuan: 'karung', beratKarung: 50, jumlahKarung: 2, totalKg: 100, hargaPerKg: 12200, subtotalHarga: 1220000 }] } }]);
var mNG2 = Math.round((rakDari(R2.s()).karung.filter(NG50)[0].hppPerKg || 0) * 50);
var r9b = catat(R2);
ok('cuma MODAL berubah (pembelian baru) → tidak ditahan, dokumen membawa modal katalog sekarang (bukan modal saat disimpan)', mNG2 !== mNG && !r9b.tolak && jualDok(r9b)[0].hppTotalSaatJual === mNG2 && jualDok(r9b)[0].hargaTotal === mNG + 20000, J([mNG, mNG2, r9b.tolak, jualDok(r9b)[0]]));
terapkanKeCache([{ koleksi: 'katalogHargaKemasan', data: { id: 'hm1', merk: 'Kembang', ukuran: 5, hargaPerUnit: 74000 } }]);
var r9c = catat(R2);
ok('HARGA katalog berubah → nota DITAHAN: kalimat menyebut barang & harga lama → baru, keranjang diperbarui ke harga sekarang, uang diterima dikosongkan',
  /^Harga berubah sejak keranjang disimpan: Kembang/.test(r9c.tolak || '') && /72\.000 → Rp74\.000/.test(r9c.tolak || '') && r9c.perbarui && r9c.perbarui.uang === 0 && r9c.perbarui.keranjang[1].trx.hargaSatuan === 74000 && r9c.perbarui.keranjang[0].trx.hargaSatuan === mNG + 20000 && r9c.perbarui.pulihPeriksa.length === 0, J([r9c.tolak, r9c.perbarui && r9c.perbarui.uang]));
R2.a.__aksi.catatNotaInti(false); var sR2 = R2.s(); var bR2 = sR2.keranjang[1] || { trx: {} };
ok('layar: CATAT pada keranjang pulihan yang harganya berubah → keranjang di layar ikut diperbarui, uang 0, kabar awas (nota tidak ditulis)', bR2.trx.hargaSatuan === 74000 && sR2.uang === 0 && sR2.kabarAwas && /Harga berubah/.test(sR2.kabar) && sR2.pulihPeriksa.length === 0, J([sR2.kabar, sR2.uang]));
var r9d = catat(R2);
ok('sesudah diperbarui & uang diterima lagi → tercatat dengan harga sekarang', !r9d.tolak && jualDok(r9d)[1].hargaTotal === 74000, J([r9d.tolak, jualDok(r9d)[1]]));
// nego yang tidak sah lagi: modal naik melewati harga nego (owner tanpa alasan) → dilepas ke harga katalog & disebut
__ss = {}; __ss[KUNCI_TAB] = J({ id: 'tab-r', ditinggal: true }); var simpanLama = simpanR ? JSON.parse(simpanR) : { v: 1, isi: {} }; simpanLama.tab = 'tab-r'; __ss[KUNCI] = J(simpanLama);
var R3 = pasang(); R3.L.pulihkanKeranjang(AKUN_A);
terapkanKeCache([{ koleksi: 'batchMasuk', data: { id: 'b-uji-3', tanggal: '2026-09-20', jam: '09:00', pemasok: 'PEMASOK CONTOH', caraBayar: 'tunai', biayaBongkar: 0,
  merkList: [{ id: '1', merk: 'NG', satuan: 'karung', beratKarung: 50, jumlahKarung: 20, totalKg: 1000, hargaPerKg: 15000, subtotalHarga: 15000000 }] } }]);
var mNG3 = Math.round((rakDari(R3.s()).karung.filter(NG50)[0].hppPerKg || 0) * 50);
var r9e = catat(R3); var bNG = r9e.perbarui && r9e.perbarui.keranjang.filter(function (b) { return b.id === idNG; })[0];
ok('nego pulihan yang tidak sah lagi (modal naik melewati harga nego) → nota DITAHAN, nego DILEPAS ke harga katalog & disebut', mNG3 > mNG + 20000 && R3.s().keranjang.length === 2 && /nego dilepas/.test(r9e.tolak || '') && bNG && !bNG.trx.nego && bNG.trx.hargaSatuan === bNG.trx.hargaAsli, J([mNG3, r9e.tolak, bNG && bNG.trx]));

// ---- 10 · hasil kiriman diketahui (asinkron): ditolak / gagal / tercatat → penanda dilepas, simpanan biasa dari keadaan sesudahnya
var A1;
var langkah = [
  function () { __ss = {}; A1 = pasang(); A1.L.pulihkanKeranjang(AKUN_A); masuk(A1, 'karung', NG50, 1); A1.L.keadaan.setel(uangPas(A1.s()));
    setelPenulis({ tulis: function () { return Promise.resolve({ gagal: true, pesan: 'ditolak server (uji)' }); } });
    return A1.a.__aksi.catatNotaInti(false).then(function () { setelPenulis(null);
      ok('kiriman DITOLAK → penanda dilepas, simpanan memegang keranjang itu lagi (masih bisa dicatat), kabar DITOLAK', !!simpanan() && !simpanan().isi.mencatat && simpanan().isi.keranjang.length === 1 && A1.s().keranjang.length === 1 && /DITOLAK/.test(A1.s().kabar), J([simpanan(), A1.s().kabar])); }); },
  function () { setelPenulis({ tulis: function () { return Promise.reject(new Error('jaringan putus (uji)')); } });
    return A1.a.__aksi.catatNotaInti(false).then(function () { setelPenulis(null);
      ok('kiriman GAGAL (melempar) → penanda dilepas, keranjang tetap tersimpan', !!simpanan() && !simpanan().isi.mencatat && simpanan().isi.keranjang.length === 1 && /GAGAL mencatat/.test(A1.s().kabar), J([simpanan(), A1.s().kabar])); }); },
  function () { masuk(A1, 'kemasan', KMB, 1); A1.L.keadaan.setel(parkir(A1.s())); masuk(A1, 'karung', NG50, 1); A1.L.keadaan.setel(uangPas(A1.s()));
    setelPenulis({ tulis: function (d) { terapkanKeCache(d); return Promise.resolve({}); } });
    return A1.a.__aksi.catatNotaInti(false).then(function () { setelPenulis(null);
      ok('kiriman TERCATAT → keranjang kosong, simpanan tanpa keranjang & tanpa penanda (struk parkir tetap)', A1.s().keranjang.length === 0 && !!simpanan() && !simpanan().isi.mencatat && simpanan().isi.keranjang.length === 0 && simpanan().isi.antrean.length === 1, J(simpanan())); }); },
];
var selesai = function () { print(J({ lulus: lulus, gagal: gagal })); };
langkah.reduce(function (p, f) { return p.then(f); }, Promise.resolve()).then(selesai, function (e) { gagal.push('JATUH (asinkron): ' + e); selesai(); });
"""

RUSAK = [
    ('akun tidak diperiksa saat memulihkan', 'logika', "if (!v || v.v !== 1 || !uid || String(v.uid) !== String(uid) ||", "if (!v || v.v !== 1 || !uid ||"),
    ('tanggal tidak diperiksa saat memulihkan', 'logika', " || String(v.tanggal) !== String(tanggal) || !v.isi) return null;", " || !v.isi) return null;"),
    ('struk parkir bertukar ikut disimpan', 'logika', ".filter((a) => a && a.beku && !a.beku.tukar && Array.isArray(a.beku.items) && a.beku.items.length)\n    .map((a) => ({ id: a.id, beku: Object.assign({}, a.beku, { uang: 0, kreditDibuka: false, tukar: null }) }));\n  if (!keranjang.length && !antrean.length && !m) return null;",
     ".filter((a) => a && a.beku && Array.isArray(a.beku.items) && a.beku.items.length)\n    .map((a) => ({ id: a.id, beku: Object.assign({}, a.beku, { uang: 0, kreditDibuka: false, tukar: null }) }));\n  if (!keranjang.length && !antrean.length && !m) return null;"),
    ('keranjang karcis / tukar ikut disimpan', 'logika', "const aktifBoleh = !s.tukar && !s.karcis && !m;", "const aktifBoleh = !m;"),
    ('layar berisi ditimpa simpanan', 'logika', "  if ((s.keranjang || []).length || (s.antrean || []).length) return null;\n  if (String(v.tab", "  if (String(v.tab"),
    ('menulis sebelum pemulihan dicoba (muat ulang menghapus simpanan)', 'layar', "const simpanKeranjang = (s) => { if (_simpanUid) tulisSimpanan(", "const simpanKeranjang = (s) => { tulisSimpanan("),
    ('ganti orang tidak menghapus simpanan', 'layar', "function lupakanSimpanan() { _simpanUid = null; tulisSimpanan(null); }", "function lupakanSimpanan() { _simpanUid = null; }"),
    ('ganti orang tetap menyimpan', 'layar', "function lupakanSimpanan() { _simpanUid = null; tulisSimpanan(null); }", "function lupakanSimpanan() { tulisSimpanan(null); }"),
    ('penyimpanan melempar tidak ditangkap', 'layar', "const tulisSesi = (k, v) => { try { if (v) sessionStorage.setItem(k, JSON.stringify(v)); else sessionStorage.removeItem(k); } catch (e) { /* mode privat / penuh */ } };",
     "const tulisSesi = (k, v) => { if (v) sessionStorage.setItem(k, JSON.stringify(v)); else sessionStorage.removeItem(k); };"),
    ('uang diterima ikut tersimpan', 'logika', "if (keranjang.length) Object.assign(isi, { pelanggan: s.pelanggan || '', cara: s.cara || 'Tunai',", "if (keranjang.length) Object.assign(isi, { uang: s.uang, pelanggan: s.pelanggan || '', cara: s.cara || 'Tunai',"),
    # tinjauan 7 Okt — NOTA GANDA
    ('NOTA GANDA: penanda "sedang mencatat" tidak ditulis sebelum dikirim', 'layar', "      tahanSimpanan({ trxId: r.nota.trxId, ringkas: r.ringkas });\n", ""),
    ('NOTA GANDA: keranjang yang sedang dicatat tetap ikut disimpan', 'logika', "const aktifBoleh = !s.tukar && !s.karcis && !m;", "const aktifBoleh = !s.tukar && !s.karcis;"),
    ('NOTA GANDA: penanda diabaikan saat memulihkan', 'logika', "const keranjang = m ? [] : daftar(i.keranjang);", "const keranjang = daftar(i.keranjang);"),
    ('NOTA GANDA: ketukan lain selama menunggu menimpa penanda', 'layar', "{ tab: _tab.id, mencatat: _mencatatNota }", "{ tab: _tab.id }"),
    ('NOTA GANDA: penanda tidak dilepas sesudah hasilnya diketahui', 'layar', "      finally { lepasSimpanan(); }\n", ""),
    # tinjauan 7 Okt — TAB SALINAN
    ('TAB SALINAN: tanda "dipakai" dianggap tab yang sama', 'logika', "const asal = !t ? 'baru' : t.ditinggal === true || mandiri === true ? 'muatUlang' : 'salinan';", "const asal = !t ? 'baru' : 'muatUlang';"),
    ('TAB SALINAN: simpanan tidak memeriksa id tab', 'logika', "  if (String(v.tab || '') !== String(tab || '')) return {", "  if (false) return {"),
    ('TAB SALINAN: halaman ditutup / dimuat ulang tidak menandai "ditinggal"', 'layar', "    window.addEventListener('pagehide', () => tandaiTab(true));\n", ""),
    ('TAB SALINAN: web app layar penuh diperlakukan seperti tab (keranjang hilang saat iOS mematikannya)', 'logika', "t.ditinggal === true || mandiri === true ? 'muatUlang'", "t.ditinggal === true ? 'muatUlang'"),
    ('TAB SALINAN: layar tidak membaca mode layar penuh', 'layar', "!!window.matchMedia('(display-mode: standalone)').matches);", "false);"),
    ('TAB SALINAN: kembali dari tembolok mundur tidak menandai "dipakai" lagi', 'layar', "    window.addEventListener('pageshow', (e) => { if (e && e.persisted) tandaiTab(false); });\n", ""),
    # tinjauan 7 Okt — HARGA & MODAL baris pulihan
    ('PULIHAN: baris pulihan tidak dibangun ulang (cuma stok diperiksa)', 'logika', "const pp = periksaPulih(s0);", "const pp = null;"),
    ('PULIHAN: baris pulihan tidak ditandai saat dipulihkan', 'logika', ", uang: 0, kreditDibuka: false, lembar: null, pulihPeriksa,", ", uang: 0, kreditDibuka: false, lembar: null, pulihPeriksa: [],"),
    ('PULIHAN: harga berubah tapi uang diterima tidak dikosongkan', 'logika', "perbarui: { keranjang, uang: 0, pulihPeriksa: sisa }", "perbarui: { keranjang, pulihPeriksa: sisa }"),
    ('PULIHAN: harga berubah tidak menahan nota', 'logika', "  if (!ubah.length) return { keranjang };", "  return { keranjang };"),
    ('PULIHAN: kabar menjanjikan pemeriksaan harga (kembali ke kalimat lama)', 'logika', " — stok, harga & modal diperiksa lagi dengan katalog sekarang saat nota dicatat';", " — stok & harga diperiksa lagi saat nota dicatat';"),
    ('PULIHAN: layar tidak menerapkan keranjang yang diperbarui', 'layar', "if (r.tolak) return set(Object.assign({}, r.perbarui || {}, {", "if (r.tolak) return set(Object.assign({}, {}, {"),
]


def jalan(ganti_logika=None, ganti_layar=None):
    js, lay, _app = uji_cache_chip_literan.bundel(ganti_layar)
    for lama, baru in (ganti_logika or []):
        n = js.count(lama); assert n == 1, 'kontrol basi: ' + lama[:90] + ' (' + str(n) + '×)'
        js = js.replace(lama, baru)
    kotak = '\nvar KOTAK = ' + json.dumps(uji_rak_inkremental.KOTAK) + ';\n'
    h, e = uji_wadah_bernama.jalan(uji_rak_inkremental.JAM_TETAP + js + uji_cache_chip_literan.PROKSI + lay + kotak + SKENARIO)
    if h is None: return 0, ['JSC JATUH ' + e]
    return h['lulus'], h['gagal']


if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, bagian, a, b in RUSAK:
            try: l, g = jalan([(a, b)] if bagian == 'logika' else None, [(a, b)] if bagian == 'layar' else None)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' — ' + str(e)); kode = 3; continue
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    l, g = jalan()
    print('KERANJANG BERTAHAN (kotak pasir, layar asli): %d lulus · %d gagal' % (l, len(g)))
    for x in g: print('   ✗ ' + x[:700])
    sys.exit(2 if g else 0)
