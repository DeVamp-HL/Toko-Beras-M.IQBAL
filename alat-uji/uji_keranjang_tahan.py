#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_keranjang_tahan.py — owner 7 Okt 2026 ("Ya, simpan di perangkat"): keranjang & nota PARKIR Jual BERTAHAN saat halaman dimuat ulang.
Layar Jual ASLI (baru/js/layar/jual.js) dijalankan di jsc dengan tiruan peramban (pola uji_cache_chip_literan) + penyimpanan SESI tiruan. KOTAK PASIR =
uji_rak_inkremental.KOTAK (angka & nama CONTOH), jam dikunci 21 Sep 2026 10:00 WIB.
  · yang disimpan: keranjang, struk parkir, struk aktif, pelanggan, cara bayar, potongan, ikatan pesanan — per AKUN (uid) + TANGGAL; TIDAK: tukar, karcis yang
    dirinci, nota terakhir, uang diterima, buka kredit sekali;
  · muat ulang (layar baru, penyimpanan sama) + akun yang sama hari itu → dipulihkan persis, kabar menyebutnya, cermin stok yang dipegang (sinkronKeranjang) ikut:
    sisa chip rak = layar sebelum dimuat ulang; akun lain / hari lain → TIDAK dipulihkan dan simpanannya dibuang; layar yang sudah berisi tidak ditimpa;
  · nota tercatat & keranjang kosong → simpanan dihapus (parkir tersisa tetap); ganti orang (lupakanOrang) → dihapus & berhenti menyimpan;
  · sebelum pemulihan dicoba layar TIDAK menulis (muat ulang tidak menghapus simpanan sebelum sempat dipulihkan);
  · penyimpanan melempar (mode privat Safari / penuh) → keranjang tetap jalan, tidak jatuh; simpanan terlalu besar tidak ditulis.

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
var KUNCI = KUNCI_SIMPAN_KERANJANG;
var simpanan = function () { return __ss[KUNCI] ? JSON.parse(__ss[KUNCI]) : null; };
var AKUN_A = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'uid-a' }, AKUN_B = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'uid-b' };
var akunKini = AKUN_A;
var opsiJ = function () { return { akun: function () { return akunKini; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, statusTeks: function () { return ''; }, statusAwas: function () { return false; },
  statusRingkas: function () { return ''; }, versiData: function () { return __versi; }, pemegang: function () { return null; }, bukaStok: null }; };
var KINI = new Date(Date.now());
// "muat ulang" = layar Jual baru di atas penyimpanan yang sama; layar menggambar diri & pindah jalur dulu (seperti app.js) sebelum akun diketahui
var pasang = function () { var a = __akar(); var L2 = pasangLayarJual(a, opsiJ()); L2.keadaan.setel({ jalur: 'karung', sekarang: KINI }); return { a: a, L: L2, s: function () { return L2.keadaan.baca(); } }; };
var rakDari = function (s) { sinkronKeranjang(s); return susunRak(s); };
var sisaChip = function (s) { var r = rakDari(s); return r.karung.concat(r.kemasan, r.literan, r.repack).map(function (c) { return c.jalur + ':' + c.kunci + ':' + (c.berat || '') + '=' + c.sisa; }).join('|'); };
var masuk = function (X, jalur, pilih, n) { var c = rakDari(X.s())[jalur].filter(pilih)[0]; var r = masukkan(Object.assign({}, X.s(), { pilih: c }), n); X.L.keadaan.setel({ keranjang: r.keranjang, urutBaris: r.urutBaris }); return r; };

// ---- 1 · pertama dibuka: belum ada simpanan, pemulihan dicoba → mulai menyimpan
var X = pasang();
ok('sebelum akun diketahui layar TIDAK menulis apa pun ke penyimpanan sesi', Object.keys(__ss).length === 0, J(__ss));
X.L.pulihkanKeranjang(AKUN_A);
masuk(X, 'karung', function (c) { return c.kunci === 'NG'; }, 2);
masuk(X, 'kemasan', function (c) { return c.kunci === 'Kembang|5'; }, 1);
X.L.keadaan.setel(parkir(Object.assign({}, X.s(), { pelanggan: 'Pembeli Contoh A' })));
masuk(X, 'karung', function (c) { return c.kunci === 'Kumala'; }, 1);
X.L.keadaan.setel({ pelanggan: 'Pembeli Contoh B', cara: 'QRIS', potongan: 2000, uang: 50000, kreditDibuka: true, notaTerakhir: { trxId: 'x', idPenjualan: [], pada: Date.now(), ringkas: 'x' } });
var S1 = simpanan(); var sAsli = X.s(); var sisaAsli = sisaChip(sAsli);
ok('tersimpan per akun + tanggal hari ini: keranjang 1 baris, 1 struk parkir (2 baris), pelanggan, cara bayar QRIS, potongan, struk aktif',
  S1 && S1.v === 1 && S1.uid === 'uid-a' && S1.tanggal === hariIniIso(KINI) && S1.isi.keranjang.length === 1 && S1.isi.antrean.length === 1 && S1.isi.antrean[0].beku.items.length === 2
  && S1.isi.pelanggan === 'Pembeli Contoh B' && S1.isi.cara === 'QRIS' && S1.isi.potongan === 2000 && S1.isi.aktifId === sAsli.aktifId, J(S1));
ok('TIDAK disimpan: uang diterima, buka kredit sekali, nota terakhir (juga di struk parkir: uang 0, kredit tertutup, tanpa tukar)',
  !('uang' in S1.isi) && !('kreditDibuka' in S1.isi) && !('notaTerakhir' in S1.isi) && S1.isi.antrean[0].beku.uang === 0 && S1.isi.antrean[0].beku.kreditDibuka === false && S1.isi.antrean[0].beku.tukar === null, J(S1.isi.antrean[0].beku));

// ---- 2 · muat ulang, akun yang sama → dipulihkan persis + stok yang dipegang ikut
var Y = pasang();
ok('muat ulang: layar baru mulai kosong, simpanan BELUM terhapus oleh gambar & pindah jalur pertama', Y.s().keranjang.length === 0 && !!simpanan(), J(simpanan()));
Y.L.pulihkanKeranjang(AKUN_A); var sY = Y.s();
ok('akun sama hari yang sama → keranjang, struk parkir, struk aktif, pelanggan, cara, potongan DIPULIHKAN persis; uang 0, kredit tertutup, nota terakhir tidak ikut',
  J(sY.keranjang) === J(sAsli.keranjang) && J(sY.antrean.map(function (a) { return a.beku.items; })) === J(sAsli.antrean.map(function (a) { return a.beku.items; })) && sY.aktifId === sAsli.aktifId && sY.idBerikut === sAsli.idBerikut
  && sY.pelanggan === 'Pembeli Contoh B' && sY.cara === 'QRIS' && sY.potongan === 2000 && sY.uang === 0 && sY.kreditDibuka === false && !sY.notaTerakhir && /dipulihkan sesudah halaman dimuat ulang: 1 barang · 1 struk parkir/.test(sY.kabar), J([sY.keranjang.length, sY.antrean.length, sY.kabar]));
ok('cermin stok yang dipegang ikut pulih: sisa tiap chip rak = sebelum dimuat ulang (keranjang + struk parkir memegang barangnya)', sisaChip(sY) === sisaAsli && sisaAsli !== sisaChip(keadaanAwal()), sisaChip(sY) + ' ≠ ' + sisaAsli);
var hY = Y.a.__html || '';
ok('layar tergambar dengan keranjang & bilah struk parkir yang dipulihkan', hY.indexOf('Pembeli Contoh A') >= 0 && hY.indexOf('1 barang') >= 0, hY.slice(0, 200));
Y.L.pulihkanKeranjang(AKUN_A);
ok('pemulihan kedua untuk akun yang sama tidak mengulang apa pun', J(Y.s().keranjang) === J(sY.keranjang) && Y.s().antrean.length === 1);

// ---- 3 · akun lain / hari lain → tidak dipulihkan, simpanan dibuang
var Z = pasang(); Z.L.pulihkanKeranjang(AKUN_B);
ok('akun LAIN di tab yang sama → keranjang akun A TIDAK dipulihkan dan simpanannya dibuang', Z.s().keranjang.length === 0 && Z.s().antrean.length === 0 && simpanan() === null, J(simpanan()));
__ss[KUNCI] = JSON.stringify(Object.assign({}, S1, { tanggal: '2026-09-20' }));
var Z2 = pasang(); Z2.L.pulihkanKeranjang(AKUN_A);
ok('simpanan KEMARIN → tidak dipulihkan dan dibuang', Z2.s().keranjang.length === 0 && simpanan() === null, J(simpanan()));
__ss[KUNCI] = JSON.stringify(S1);
var Z3 = pasang(); masuk(Z3, 'karung', function (c) { return c.kunci === 'Angsa' && c.berat === 50; }, 1); Z3.L.pulihkanKeranjang(AKUN_A);
ok('layar yang SUDAH berisi tidak ditimpa simpanan (keranjang yang sedang jalan menang)', Z3.s().keranjang.length === 1 && Z3.s().keranjang[0].trx.merkSumber === 'Angsa' && Z3.s().antrean.length === 0 && simpanan().isi.keranjang[0].trx.merkSumber === 'Angsa', J(Z3.s().keranjang));

// ---- 4 · tukar & karcis tidak disimpan
var T = pasang(); T.L.pulihkanKeranjang(AKUN_A); T.L.keadaan.setel({ keranjang: [], antrean: [] });
masuk(T, 'karung', function (c) { return c.kunci === 'NG'; }, 1); T.L.keadaan.setel(parkir(Object.assign({}, T.s(), { tukar: { ringkas: 'tukar contoh', kredit: 1000, returDraf: { id: 'r1' } } })));
masuk(T, 'kemasan', function (c) { return c.kunci === 'Kembang|5'; }, 1); T.L.keadaan.setel(parkir(T.s()));
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
ok('keranjang & parkir kosong → simpanan DIHAPUS', simpanan() === null && Object.keys(__ss).length === 0, J(__ss));
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
print(J({ lulus: lulus, gagal: gagal }));
"""

RUSAK = [
    ('akun tidak diperiksa saat memulihkan', 'logika', "if (!v || v.v !== 1 || !uid || String(v.uid) !== String(uid) ||", "if (!v || v.v !== 1 || !uid ||"),
    ('tanggal tidak diperiksa saat memulihkan', 'logika', " || String(v.tanggal) !== String(tanggal) || !v.isi) return null;", " || !v.isi) return null;"),
    ('struk parkir bertukar ikut disimpan', 'logika', ".filter((a) => a && a.beku && !a.beku.tukar && Array.isArray(a.beku.items) && a.beku.items.length)\n    .map((a) => ({ id: a.id, beku: Object.assign({}, a.beku, { uang: 0, kreditDibuka: false, tukar: null }) }));\n  if (!keranjang.length && !antrean.length) return null;\n  const isi",
     ".filter((a) => a && a.beku && Array.isArray(a.beku.items) && a.beku.items.length)\n    .map((a) => ({ id: a.id, beku: Object.assign({}, a.beku, { uang: 0, kreditDibuka: false, tukar: null }) }));\n  if (!keranjang.length && !antrean.length) return null;\n  const isi"),
    ('keranjang karcis / tukar ikut disimpan', 'logika', "const aktifBoleh = !s.tukar && !s.karcis;", "const aktifBoleh = true;"),
    ('layar berisi ditimpa simpanan', 'logika', "  if ((s.keranjang || []).length || (s.antrean || []).length) return null;\n  const i = v.isi;", "  const i = v.isi;"),
    ('menulis sebelum pemulihan dicoba (muat ulang menghapus simpanan)', 'layar', "const simpanKeranjang = (s) => { if (_simpanUid) tulisSimpanan(", "const simpanKeranjang = (s) => { tulisSimpanan("),
    ('ganti orang tidak menghapus simpanan', 'layar', "function lupakanSimpanan() { _simpanUid = null; tulisSimpanan(null); }", "function lupakanSimpanan() { _simpanUid = null; }"),
    ('ganti orang tetap menyimpan', 'layar', "function lupakanSimpanan() { _simpanUid = null; tulisSimpanan(null); }", "function lupakanSimpanan() { tulisSimpanan(null); }"),
    ('penyimpanan melempar tidak ditangkap', 'layar', "const tulisSimpanan = (v) => { try { if (v) sessionStorage.setItem(L.KUNCI_SIMPAN_KERANJANG, JSON.stringify(v)); else sessionStorage.removeItem(L.KUNCI_SIMPAN_KERANJANG); } catch (e) { /* mode privat / penuh */ } };",
     "const tulisSimpanan = (v) => { if (v) sessionStorage.setItem(L.KUNCI_SIMPAN_KERANJANG, JSON.stringify(v)); else sessionStorage.removeItem(L.KUNCI_SIMPAN_KERANJANG); };"),
    ('uang diterima ikut tersimpan', 'logika', "if (keranjang.length) Object.assign(isi, { pelanggan: s.pelanggan || '', cara: s.cara || 'Tunai',", "if (keranjang.length) Object.assign(isi, { uang: s.uang, pelanggan: s.pelanggan || '', cara: s.cara || 'Tunai',"),
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
