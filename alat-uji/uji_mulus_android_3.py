#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_mulus_android_3.py — MULUS ANDROID PAKET 3 (owner 23 Nov 2026: "app masih lag dan belum optimal performanya, terutama masalah responsif").
Kartu Kelancaran CPad 23 Nov: Ringkasan › Cincin 481× tersendat (±1×/menit selama layar terbuka), Jual 4 tab ±550×, Menu 185× + Laci 94× (kebanyakan
"tanpa ketukan (kabar data / latar)"), lembar karcis ±290×, Dasbor dingin 9× ±1,6 dtk. Yang dijaga di sini (jsc, layar & logika ASLI, kotak pasir
uji_layar_mulus — ANGKA CONTOH, bukan angka toko):
  · INGATAN TAHU DENYUT (toko.js): hitungan yang TIDAK membaca cache denyut perangkat / jejak tulisan tetap berlaku melewati kabar perangkatStatus &
    logAktivitas; yang membaca (cacheMentah / dokDiCache — juga lewat ingatan lain yang bersarang) dihitung ulang & hasilnya segar; kabar koleksi lain
    membuang semuanya; galat di tengah hitungan tidak meninggalkan tanda; versiIsi() tidak naik oleh denyut/jejak, versiCache() tetap naik.
  · RINGKASAN: detak menit hanya menyusun ulang cincin (perhatian, kas tidak dihitung ulang); kabar denyut selagi Cincin tampil tidak menghitung apa pun.
  · DASBOR: data berubah selagi Dasbor tidak tampil → kelompoknya dipanaskan di latar satu per satu; dibuka sesudahnya = tanpa hitung ulang, isinya =
    hitungan segar. Cincin / bukan owner → tidak ada pemanasan.
  · KARCIS & KARTU RINGKAS TABLET: tebakan karcis, rincian hari ini, rtHitung diingat — sama persis dengan hitung ulang penuh; panggilan kedua tanpa hitung.
  · MENU STAF (akun tablet): kartu "Kelancaran perangkat ini" ada (owner minta kartu dari CPad; dulu hanya di Sistem › Perangkat milik owner).
  · STATIS: html.ringan (Android) mematikan semua kaca buram; tidak ada animasi tanpa henti yang menggerakkan selain transform/opacity; jarum detik cincin =
    lapisan sendiri yang diputar (dikomposit), bukan garis di dalam SVG cincin.

    python3 alat-uji/uji_mulus_android_3.py            → N lulus · 0 gagal
    python3 alat-uji/uji_mulus_android_3.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, re, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import modul_es  # noqa: E402
import uji_layar_mulus as ULM  # noqa: E402

MODUL = ['baru/js/layar/ringkasan.js', 'baru/js/layar/menu.js', 'baru/js/layar/karcis-logika.js', 'baru/js/layar/ringkas-tablet-logika.js']
TK, RG, KC, RT = 'baru/js/data/toko.js', 'baru/js/layar/ringkasan.js', 'baru/js/layar/karcis-logika.js', 'baru/js/layar/ringkas-tablet-logika.js'

SKENARIO = r"""
__KINI = new __DateAsli(JAM).getTime();
var DOM = __E['baru/js/inti/dom.js'], GR = __E['baru/js/inti/gerak.js'], D = __E['baru/js/data/toko.js'], F = __E['baru/js/inti/format.js'];
DOM.pasang = function (akar, isi) { var s = isi && isi.__mentah ? isi.html : String(isi || ''); akar.__html = s; akar.__ids = {}; akar.firstElementChild = s ? {} : null; };
DOM.delegasi = function (akar, p) { akar.__aksi = p; };
GR.gulirkan = function () {}; GR.sekali = function () {}; GR.terbangkan = function () {};
var HITUNG = { 'baru/js/layar/ringkasan-logika.js': ['susunPerhatian', 'susunKas', 'susunRingkasan', 'bangunIndeks'], 'baru/js/mesin/beku.js': ['hitungStokKarungPerMerk', 'kasPada'],
  'baru/js/layar/stok-logika.js': ['umRingkas', 'daftarBarang'], 'baru/js/layar/laporan-logika.js': ['rekapHari'], 'baru/js/data/toko.js': ['ingatStokKarung', 'ambilPenjualanSemua'] };
var __n = {};
Object.keys(HITUNG).forEach(function (m) { HITUNG[m].forEach(function (f) { var asli = __E[m][f]; __E[m][f] = function () { __n[f] = (__n[f] || 0) + 1; return asli.apply(this, arguments); }; }); });
__sambungSemua();
__E['baru/js/inti/kunci.js'].setelKunci(false);
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) D.pasok(n, CAD[n]); });
if (TITIK) localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(TITIK));
D.setelSumber('firestore', '');
var J = JSON.stringify, H = { cek: [] };
function ok(nama, syarat, ket) { H.cek.push({ nama: nama, ok: !!syarat, ket: syarat ? '' : String(ket === undefined ? '' : (typeof ket === 'string' ? ket : J(ket))).slice(0, 500) }); }
function nol() { __n = {}; }
function __tuntas() { __kurasMikro(); __bingkai(); __kurasMikro(); }
function __sisa() { for (var i = 0; i < 200 && (__raf.length || __timer.length); i++) { if (__raf.length) __bingkai(); else { __jam += 100; __jalanTimer(__jam); } } }
var KOL = { perangkatStatus: 'perangkat', logAktivitas: 'log', penjualan: 'penjualan' };
var __u = 0;
function denyutBaru() { __u += 1; D.pasok('perangkatStatus', D.cacheMentah('perangkat').concat([{ id: 'uji-' + __u, pada: new Date().toISOString(), aplikasi: 'baru', antrean: 0 }])); }
function jejakBaru() { __u += 1; D.pasok('logAktivitas', D.cacheMentah('log').concat([{ id: 'log-' + __u, pada: new Date().toISOString(), ringkas: 'uji' }])); }
function penjualanSama() { D.pasok('penjualan', D.cacheMentah('penjualan').slice()); }
function notaBaru() { var c = D.cacheMentah('penjualan').filter(function (p) { return p.jenis === 'karung' && !p.dibatalkan && p.merkSumber; })[0] || D.cacheMentah('penjualan')[0];
  __u += 1; var n = Object.assign({}, c, { id: 8700000000000 + __u, tanggal: F.hariIniIso(new Date()), jam: '09:3' + (__u % 10), grupNota: 'gM3' + __u, trxId: 'tM3' + __u, hargaTotal: 120000 + __u });
  delete n.dibatalkan; delete n.dikoreksiOleh; D.pasok('penjualan', D.cacheMentah('penjualan').concat([n])); }

// ================= 1. INGATAN TAHU DENYUT (toko.js) =================
(function () {
  var c = { f: 0, g: 0, h: 0, o: 0 };
  var f = function () { return D.ingatPerVersi('uji|f', function () { c.f++; return D.ambilPenjualan().length; }); };
  var g = function () { return D.ingatPerVersi('uji|g', function () { c.g++; return D.cacheMentah('perangkat').length; }); };
  var h = function () { return D.ingatPerVersi('uji|h', function () { c.h++; return !!D.dokDiCache('logAktivitas', 'log-' + __u); }); };
  var o = function () { return D.ingatPerVersi('uji|o', function () { c.o++; return g() + 1000; }); };
  var semua = function () { return [f(), g(), h(), o()]; };
  semua(); g(); o();
  ok('denyut: hitungan pertama sekali per kunci (f, g, h, o bersarang)', c.f === 1 && c.g === 1 && c.h === 1 && c.o === 1, c);
  var fl = D.isiIngatan();
  ok('denyut: ingatan menandai siapa yang membaca cache denyut/jejak (g lewat cacheMentah, h lewat dokDiCache, o lewat ingatan g yang bersarang; f tidak)',
    fl['uji|f'] && !fl['uji|f'].denyut && fl['uji|g'].denyut && fl['uji|h'].denyut && fl['uji|o'].denyut, fl);
  var vi = D.versiIsi(), vc = D.versiCache(), g0 = g();
  denyutBaru(); var r1 = semua();
  ok('denyut: kabar perangkatStatus — f TIDAK dihitung ulang; g, h, o dihitung ulang dan g/o segar (+1 perangkat)', c.f === 1 && c.g === 2 && c.h === 2 && c.o === 2 && r1[1] === g0 + 1 && r1[3] === g0 + 1001, [c, r1, g0]);
  ok('denyut: versiIsi() tetap, versiCache() naik', D.versiIsi() === vi && D.versiCache() > vc, [vi, D.versiIsi(), vc, D.versiCache()]);
  jejakBaru(); var r2 = semua();
  ok('jejak: kabar logAktivitas — f tetap; h melihat jejak baru (true); g, o dihitung ulang', c.f === 1 && c.h === 3 && r2[2] === true && c.g === 3 && c.o === 3, [c, r2]);
  penjualanSama(); semua();
  ok('kabar koleksi lain (penjualan) membuang SEMUA ingatan seperti dulu', c.f === 2 && c.g === 4 && c.h === 4 && c.o === 4 && D.versiIsi() > vi, c);
  var lempar = ''; try { D.ingatPerVersi('uji|lempar', function () { D.cacheMentah('perangkat'); throw new Error('sengaja'); }); } catch (e) { lempar = e.message; }
  D.cacheMentah('perangkat');   // dibaca di luar hitungan: tidak boleh menandai apa pun
  var c2 = 0; D.ingatPerVersi('uji|sesudah', function () { c2++; return 1; });
  denyutBaru(); D.ingatPerVersi('uji|sesudah', function () { c2++; return 1; });
  ok('galat di tengah hitungan tidak meninggalkan tanda: hitungan berikutnya yang tidak membaca denyut tetap berlaku melewati denyut', lempar === 'sengaja' && c2 === 1 && !D.isiIngatan()['uji|sesudah'].denyut, [lempar, c2, D.isiIngatan()['uji|sesudah']]);
  // hitungan LUAR membaca denyut, lalu hitungan DALAM melempar dan ditangkap luar → tanda bacaan luar tetap ada (try/finally), luar dihitung ulang sesudah denyut
  var nL = 0; var luarGalat = function () { return D.ingatPerVersi('uji|luarGalat', function () { nL++; var n = D.cacheMentah('perangkat').length;
    try { D.ingatPerVersi('uji|dalamGalat', function () { throw new Error('dalam'); }); } catch (e) { /* ditangkap */ } return n; }); };
  var lg0 = luarGalat(); denyutBaru(); var lg1 = luarGalat();
  ok('galat hitungan dalam yang ditangkap tidak menghapus tanda bacaan denyut hitungan luar (dihitung ulang & segar sesudah denyut)', nL === 2 && lg1 === lg0 + 1 && D.isiIngatan()['uji|luarGalat'].denyut, [nL, lg0, lg1, D.isiIngatan()['uji|luarGalat']]);
  var luar = 0, dalam = 0; D.setelIngatan({});
  D.ingatPerVersi('uji|luar', function () { luar++; D.ingatPerVersi('uji|dalam', function () { dalam++; return D.ambilPenjualan().length; }); return D.cacheMentah('log').length; });
  ok('bersarang: tanda bacaan luar tidak menular ke hitungan dalam yang tidak membaca denyut', D.isiIngatan()['uji|luar'].denyut && !D.isiIngatan()['uji|dalam'].denyut, D.isiIngatan());
  D.setelIngatan({});
})();

// ================= 2. RINGKASAN: detak menit & kabar denyut =================
var AKUN = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'u-owner' };
var opsi = { akun: function () { return AKUN; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, sekarang: function () { return null; }, statusRingkas: function () { return 'OWNER'; },
  pindah: function () {}, keTujuan: function () {}, versiData: function () { return 0; } };
localStorage.setItem('miqbal_baru_ringkasan_tampilan', 'cincin'); localStorage.setItem('miqbal_baru_skala', 'jam');
var AR = new __El('main'); var RL = __E['baru/js/layar/ringkasan.js'].pasangLayarRingkasan(AR, opsi);
RL.tampilkan(true); __tuntas(); __sisa();
ok('ringkasan: cincin tergambar (kotak pasir)', String((AR.querySelector('#rkUmpan') || {}).__html || AR.__html).length > 50 && AR.__html.indexOf('rkCincin') >= 0, AR.__html.slice(0, 200));
ok('ringkasan: jarum detik = lapisan <svg class="rk-detik"> di luar SVG cincin', /<\/svg><svg class="rk-detik" id="rkDetik"/.test(AR.__html) && AR.__html.indexOf('jarum-detik') < 0, AR.__html.slice(AR.__html.indexOf('cincin-wadah'), AR.__html.indexOf('cincin-wadah') + 700));
nol(); __KINI += 60000; __interval.forEach(function (f) { f(); }); __tuntas(); __sisa();
ok('ringkasan: detak menit menyusun cincin lagi (1×) — perhatian & kas TIDAK dihitung ulang', (__n.susunRingkasan || 0) === 1 && !__n.susunPerhatian && !__n.susunKas && !__n.kasPada, __n);
nol(); denyutBaru(); __tuntas(); __sisa();
ok('ringkasan: kabar denyut selagi Cincin tampil — tidak ada yang dihitung ulang (susunan, perhatian, kas, stok, indeks)', !__n.susunRingkasan && !__n.susunPerhatian && !__n.susunKas && !__n.hitungStokKarungPerMerk && !__n.bangunIndeks, __n);
nol(); jejakBaru(); __tuntas(); __sisa();
ok('ringkasan: kabar jejak selagi Cincin tampil — tidak ada yang dihitung ulang', !__n.susunRingkasan && !__n.susunPerhatian && !__n.susunKas && !__n.hitungStokKarungPerMerk, __n);
nol(); notaBaru(); __tuntas(); __sisa();
ok('ringkasan: nota baru tetap menghitung ulang (kontrol positif)', (__n.susunRingkasan || 0) >= 1 && (__n.susunPerhatian || 0) >= 1, __n);

// ================= 3. DASBOR: pemanasan di latar =================
RL.tampilkan(false); __tuntas(); __sisa();
var RD = __E['baru/js/layar/dasbor-logika.js'];
// pindah ke Dasbor (owner) lalu sembunyikan
localStorage.setItem('miqbal_baru_ringkasan_tampilan', 'dasbor');
var AR2 = new __El('main'); var RL2 = __E['baru/js/layar/ringkasan.js'].pasangLayarRingkasan(AR2, opsi);
RL2.tampilkan(true); __tuntas(); __sisa(); RL2.tampilkan(false); __tuntas(); __sisa();
// 25 Nov 2026: peramban tiruan kini punya requestIdleCallback sendiri (uji_layar_mulus) — rantai pemanasan dijadwalkan __sisa, DIJALANKAN __jalanLuang
nol(); notaBaru(); __kurasMikro(); var segera1 = J(__n); __jam += 5000; __sisa(); __jalanLuang();
var panas = J(__n);
ok('dasbor: data berubah selagi tersembunyi → kelompok dipanaskan di LATAR (sesudah jeda, bukan di kabar datanya)', JSON.parse(segera1).rekapHari === undefined && (__n.rekapHari || 0) >= 1 && (__n.umRingkas || 0) >= 1, [segera1, panas]);
nol(); RL2.tampilkan(true); __tuntas(); __sisa();
ok('dasbor: dibuka sesudah dipanaskan — kelompok TIDAK dihitung ulang (hari ini, mutu)', !__n.rekapHari && !__n.umRingkas, __n);
var isiDb = (AR2.querySelector('#rkDasbor') || {}).__html || '';
var segar = D.tanpaIngatan(function () { return J(RD.susunDasbor(new Date(), 'hari')); });
var hangat = J(RD.susunDasbor(new Date(), 'hari', null, function (k, f) { return D.ingatPerVersi('db|' + k + '|' + D.kunciLuarCache(new Date()), f); }));
ok('dasbor: isi yang dipanaskan = hitungan segar (byte-sama) dan dasbor tergambar', segar === hangat && isiDb.length > 200, [segar.slice(0, 200), hangat.slice(0, 200), isiDb.length]);
RL2.tampilkan(false); __tuntas(); __sisa();
localStorage.setItem('miqbal_baru_ringkasan_tampilan', 'cincin');
var AR3 = new __El('main'); var RL3 = __E['baru/js/layar/ringkasan.js'].pasangLayarRingkasan(AR3, opsi); RL3.tampilkan(true); __tuntas(); __sisa(); RL3.tampilkan(false); __tuntas(); __sisa();
RL2 = null;
// hanya RL3 (cincin) yang mendengar sekarang? RL & RL2 tetap terpasang → pakai akun bukan-owner untuk kasus "bukan owner"
AKUN = { jenis: 'aktif', peran: 'ben', nama: 'Tablet', uid: 'u-tab', operatorId: 'o1' };
nol(); notaBaru(); __jam += 5000; __sisa(); __jalanLuang();
ok('dasbor: akun bukan owner → tidak ada pemanasan dasbor', !__n.umRingkas, __n);
AKUN = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'u-owner' };

// ================= 4. KARCIS & KARTU RINGKAS TABLET =================
(function () {
  var K = __E['baru/js/layar/karcis-logika.js'], R = __E['baru/js/layar/ringkas-tablet-logika.js'];
  var hl = D.ambilHargaLiteran().filter(function (x) { return x.hargaPerLiter > 0; });
  var nom = [hl.length ? hl[0].hargaPerLiter * 3 : 30000, 50000, 123456];
  nom.forEach(function (n) {
    var a = J(K.tebakanKarcis(n)), b = J(D.tanpaIngatan(function () { return K.tebakanKarcis(n); }));
    nol(); var a2 = J(K.tebakanKarcis(n));
    ok('karcis: tebakan ' + n + ' = hitung ulang penuh, panggilan kedua tanpa membaca stok', a === b && a2 === b && !__n.ingatStokKarung, [a.slice(0, 160), b.slice(0, 160), __n]);
  });
  var iso = F.hariIniIso(new Date());
  var ra = J(K.riwayatRinci(iso)), rb = J(D.tanpaIngatan(function () { return K.riwayatRinci(iso); }));
  nol(); K.riwayatRinci(iso);
  ok('karcis: rincian hari ini = hitung ulang penuh; panggilan kedua tidak memindai penjualan', ra === rb && !__n.ambilPenjualanSemua, [ra.slice(0, 120), rb.slice(0, 120), __n]);
  var AK = { jenis: 'aktif', peran: 'ben', operatorId: 'o1', bacaUang: true }, U = { nyala: true, siap: 11, total: 11, ditolak: [] };
  var x1 = J(R.rtHitung(new Date(), AK, U)), x2 = J(D.tanpaIngatan(function () { return R.rtHitung(new Date(), AK, U); }));
  nol(); var x3 = J(R.rtHitung(new Date(), AK, U)); var n3 = Object.assign({}, __n);
  var y1 = J(R.rtHitung(new Date(), AK, { nyala: true, siap: 3, total: 11, ditolak: [] })), y2 = J(D.tanpaIngatan(function () { return R.rtHitung(new Date(), AK, { nyala: true, siap: 3, total: 11, ditolak: [] }); }));
  ok('ringkas tablet: rtHitung = hitung ulang penuh; panggilan kedua tanpa menyusun daftar barang; keadaan data uang lain = hasil lain yang juga benar', x1 === x2 && x3 === x2 && !n3.daftarBarang && y1 === y2 && y1 !== x1, [x1.slice(0, 120), x2.slice(0, 120), n3, y1 === y2]);
  notaBaru(); var z1 = J(R.rtHitung(new Date(), AK, U)), z2 = J(D.tanpaIngatan(function () { return R.rtHitung(new Date(), AK, U); }));
  ok('ringkas tablet: sesudah nota baru hasilnya ikut segar', z1 === z2 && z1 !== x1, [z1.slice(0, 100), x1.slice(0, 100)]);
})();

// ================= 5. MENU STAF: kartu Kelancaran =================
(function () {
  var AK = { jenis: 'aktif', peran: 'ben', nama: 'Tablet', uid: 'u-tab', operatorId: 'o1', email: 'tablet@contoh.invalid' };
  var o = Object.assign({}, opsi, { akun: function () { return AK; }, lokal: function () { return { antre: [], idPerangkat: 'p-tab', namaPerangkat: 'Tablet', pemegang: null, lokasi: null, koleksiSiap: 56, koleksiTotal: 56, offline: false, pajak: [] }; },
    antreLokal: function () { return { belum: [], ditolak: [] }; }, statusUang: function () { return null; } });
  var AM = new __El('main'); var ML = __E['baru/js/layar/menu.js'].pasangLayarMenu(AM, o); ML.tampilkan(true); __tuntas(); __sisa();
  ok('menu staf (akun tablet): kartu "Kelancaran perangkat ini" dengan lihat & salin rincian', AM.__html.indexOf('data-k="staf"') >= 0 && AM.__html.indexOf('data-k="lancar"') >= 0 && AM.__html.indexOf('Kelancaran perangkat ini') >= 0 && AM.__html.indexOf('data-aksi="lcBuka"') >= 0, AM.__html.slice(0, 300));
})();
print('@@HASIL@@' + J(H));
"""


def jalankan(ganti=None):
    js, peta, urut = modul_es.bundel(MODUL, ULM.LINGKUNGAN, ganti)
    kode = js + '\nvar CAD = ' + json.dumps(ULM.kotak()) + ';\nvar JAM = ' + json.dumps(ULM.JAM) + ';\nvar TITIK = ' + json.dumps(ULM.TITIK_KOTAK) + ';\n' + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(kode); p = f.name
    try: r = subprocess.run([ULM.JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta'), timeout=600)
    finally: os.unlink(p)
    out = r.stdout or ''; i = out.find('@@HASIL@@')
    if i < 0: return None, 'JSC JATUH (%s): %s' % (r.returncode, (r.stderr or out)[-1200:])
    return json.loads(out[i + 9:].strip().split('\n')[0]), ''


# ---------------------------------------------------------------- statis (CSS & app)
def baca(f): return open(os.path.join(AKAR, f), encoding='utf-8').read()


def statis(ubah=None):
    t = {f: baca(f) for f in ['baru/css/kinerja.css', 'baru/js/app.js', 'baru/css/ringkasan.css']}
    for f in sorted(glob.glob(os.path.join(AKAR, 'baru/css/*.css'))): t.setdefault(os.path.relpath(f, AKAR), baca(os.path.relpath(f, AKAR)))
    for (f, lama, baru) in (ubah or []):
        assert lama in t[f], ('jangkar kontrol hilang', f, lama[:60]); t[f] = t[f].replace(lama, baru, 1)
    hasil = []
    def ok(nama, syarat, ket=''): hasil.append({'nama': nama, 'ok': bool(syarat), 'ket': '' if syarat else str(ket)[:400]})
    k = t['baru/css/kinerja.css']
    ok('ringan: SEMUA kaca buram mati (html.ringan * / ::before / ::after, !important)', 'html.ringan *, html.ringan *::before, html.ringan *::after { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }' in k)
    ok('ringan: permukaan yang tadinya buram memakai warna pekat (nav, pita kabar, pintu & pelat Masuk)', 'html.ringan body { --nav: rgba(' in k and 'html.ringan body.gelap { --nav: rgba(' in k and '--gm-kaca-pintu: rgba(' in k and 'html.ringan .kabar-baru' in k)
    ok('ringan: isi panjang di luar layar tidak dicat (content-visibility: auto + ukuran tebakan)', re.search(r'html\.ringan [^{]*\{ content-visibility: auto; contain-intrinsic-size: auto \d+px; \}', k) is not None)
    ok('app: kelas ringan dari user agent Android (?ringan=1/0 memaksa)', "classList.toggle('ringan', r === '1' || (r !== '0' && /Android/i.test(String(navigator.userAgent || ''))))" in t['baru/js/app.js'])
    # animasi tanpa henti hanya boleh menggerakkan transform / opacity
    buruk = []
    for f, s in t.items():
        if not f.endswith('.css'): continue
        kf = {m.group(1): m.group(2) for m in re.finditer(r'@keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)[^{}]*\}', s)}
        for m in re.finditer(r'animation:\s*([^;}]*)', s):
            nilai = m.group(1)
            if 'infinite' not in nilai: continue
            for nama in re.findall(r'[\w-]+', nilai):
                if nama in kf:
                    sifat = set(re.findall(r'([a-z-]+)\s*:', kf[nama])) - {'transform', 'opacity', 'offset', 'animation-timing-function'}
                    if sifat: buruk.append('%s:%s %s' % (f, nama, sorted(sifat)))
    ok('animasi tanpa henti hanya transform / opacity (dikomposit kartu grafis, bukan cat ulang tiap bingkai)', not buruk, buruk)
    r = t['baru/css/ringkasan.css']
    ok('jarum detik: lapisan sendiri yang diputar (will-change: transform, transisi transform) & hormat reduced-motion',
       re.search(r'\.layar-ringkasan \.rk-detik \{[^}]*will-change: transform;[^}]*transition: transform', r) is not None and '.layar-ringkasan .rk-detik, .layar-ringkasan .kartu.hero' in r)
    return hasil


RUSAK = [
    # (nama, ganti modul_es {berkas: [(lama, baru)]}, ubah statis [(berkas, lama, baru)])
    ('cacheMentah tidak menandai bacaan denyut', {TK: [("export function cacheMentah(nama) { tandaiBaca(nama); return", "export function cacheMentah(nama) { return")]}, None),
    ('dokDiCache tidak menandai bacaan denyut', {TK: [("if (k) tandaiBaca(k.cache); return k ?", "return k ?")]}, None),
    ('ingatan bersarang yang membaca denyut tidak menular ke luar', {TK: [("if (ada.denyut && _ingatDalam > 0) _ingatBacaDenyut = true; return ada.h;", "return ada.h;")]}, None),
    ('denyut kembali membuang semua ingatan (cara lama)', {TK: [("if (namaKoleksi && KOLEKSI_DENYUT[namaKoleksi]) _versiDenyut += 1; else _versiBerat += 1;", "_versiDenyut += 1; _versiBerat += 1;")]}, None),
    ('denyut tidak membasikan hitungan yang membacanya', {TK: [("if (ada && (!ada.denyut || ada.vd === _versiDenyut))", "if (ada)")]}, None),
    ('galat meninggalkan kedalaman hitungan', {TK: [("try { h = I.beku ? I.beku(f()) : f(); } finally { _ingatDalam -= 1; denyut = _ingatBacaDenyut; _ingatBacaDenyut = luar || denyut; }",
                                                   "h = I.beku ? I.beku(f()) : f(); _ingatDalam -= 1; denyut = _ingatBacaDenyut; _ingatBacaDenyut = luar || denyut;")]}, None),
    ('kunci menit kembali di semua hitungan Ringkasan', {RG: [("(menit ? Math.floor(k.getTime() / 60000) : '')", "Math.floor(k.getTime() / 60000)")]}, None),
    ('pemanasan dasbor mati', {RG: [("    const token = ++_panas; let i = 0;", "    return; const token = ++_panas; let i = 0;")]}, None),
    ('pemanasan dasbor untuk bukan owner', {RG: [("if (!pemilik() || tampilan !== 'dasbor' ||", "if (tampilan !== 'dasbor' ||")]}, None),
    ('dasbor tidak memakai kelompok yang dipanaskan', {RG: [("dbHasil = susunDasbor(k, r, null, ingatDb(k));", "dbHasil = susunDasbor(k, r);")]}, None),
    ('tebakan karcis tidak diingat', {KC: [("return ingatPerVersi('kcTebak|' + n, () => tebakanKarcisHitung(n)); }", "return tebakanKarcisHitung(n); }")]}, None),
    ('rincian hari ini tidak diingat', {KC: [("{ return ingatPerVersi('kcRinciHari|' + iso, () => riwayatRinciHitung(iso)); }", "{ return riwayatRinciHitung(iso); }")]}, None),
    ('rtHitung tidak diingat', {RT: [("return ingatPerVersi('rtHitung|' + iso + '|' + K.st + '|' + K.teks, () => rtHitungIsi(iso, K));", "return rtHitungIsi(iso, K);")]}, None),
    ('rtHitung tidak membedakan keadaan data uang', {RT: [("ingatPerVersi('rtHitung|' + iso + '|' + K.st + '|' + K.teks,", "ingatPerVersi('rtHitung|' + iso,")]}, None),
    ('kartu Kelancaran hilang dari Menu staf', {'baru/js/layar/menu.js': [("      ${ntAplikasi() ? h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}` : ''}\n      ${gambarLancar(s)}", "      ${ntAplikasi() ? h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}` : ''}")]}, None),
    ('jarum detik kembali di dalam SVG cincin', {RG: [('</svg><svg class="rk-detik" id="rkDetik" viewBox="-6 -6 212 212" aria-hidden="true"><line x1="100" y1="34" x2="100" y2="24"></line></svg></div></div>',
                                                     '<line class="jarum-detik" id="rkDetik" x1="100" y1="34" x2="100" y2="24"></line></svg></div></div>')]}, None),
    ('kaca buram ringan hanya sebagian', None, [('baru/css/kinerja.css', 'html.ringan *, html.ringan *::before, html.ringan *::after { backdrop-filter', 'html.ringan .nav { backdrop-filter')]),
    ('animasi box-shadow tanpa henti kembali', None, [('baru/css/menu.css', '@keyframes prDenyut { 0% { transform: scale(1); opacity: 1; }', '@keyframes prDenyut { 0% { box-shadow: 0 0 0 0 red; transform: scale(1); opacity: 1; }')]),
    ('ringan tidak dipasang dari user agent', None, [('baru/js/app.js', "/Android/i.test(", "/TidakAda/i.test(")]),
]


def main():
    kontrol = '--kontrol' in sys.argv
    if not kontrol:
        H, galat = jalankan()
        semua = (H['cek'] if H else []) + statis()
        for c in semua: print(('✓ ' if c['ok'] else '✗ ') + c['nama'] + ('' if c['ok'] else ' → ' + c['ket']))
        lulus = sum(1 for c in semua if c['ok']); gagal = len(semua) - lulus + (1 if galat else 0)
        if galat: print('✗ ' + galat)
        print('MULUS ANDROID 3: %d lulus · %d gagal' % (lulus, gagal))
        sys.exit(1 if gagal else 0)
    diam = []
    for nama, ganti, ubah in RUSAK:
        if ganti:
            for f, pasang in ganti.items():
                s = open(os.path.join(AKAR, f), encoding='utf-8').read()
                for lama, _ in pasang:
                    if lama not in s: print('✗ jangkar kontrol hilang: %s · %s' % (nama, lama[:70])); diam.append(nama)
            H, galat = jalankan(ganti)
            jatuh = sum(1 for c in (H['cek'] if H else []) if not c['ok']) + (1 if galat else 0)
        else:
            jatuh = sum(1 for c in statis(ubah) if not c['ok'])
        print(('✓ ketahuan' if jatuh else '✗ DIAM') + ' · ' + nama + ' (' + str(jatuh) + ' cek jatuh)')
        if not jatuh: diam.append(nama)
    print('KONTROL MULUS ANDROID 3: %d/%d ketahuan' % (len(RUSAK) - len(set(diam)), len(RUSAK)))
    sys.exit(3 if diam else 0)


if __name__ == '__main__':
    main()
