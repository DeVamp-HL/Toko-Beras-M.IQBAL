#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tablet_tampilan.py — paket tampilan tablet (owner 23 Nov 2026): push aplikasi tablet, lonceng kabar & pesan, dock lipat + layar penuh. Tanpa peramban.
(Kemasan per nama diuji uji_jual_baru.py bagian N + uji_rak_inkremental.py.)

  JSC (KOTAK PASIR — aplikasi tablet TIRUAN: window.Capacitor palsu, tanpa Google sungguhan)
  · notif-tablet.js: bukan aplikasi / APK tanpa plugin push / APK tanpa berkas Firebase → tombol menolak dengan kalimat yang menyebut jalan keluarnya;
    Nyalakan = izin diminta → daftar → token disimpan atas nama akun → keadaan lokal ber-uid; izin ditolak, Google menolak, token tak datang = gagal
    jujur & pendengar dilepas; Matikan = token dicabut + dikosongkan; Segarkan = tanpa minta izin, token sama = tidak menulis, token baru = menulis;
    notifikasi diketuk = layar tujuan.
  · perangkat.js: layar penuh = Perangkat.layarPenuh { nyala }, APK lama tanpa metode = saklar tidak tampil.
  · kabar-baru-logika.js (lonceng): owner = yang menunggu saja (pesan & kabar barang masuk bisa dibalas), akun tablet = miliknya (menunggu + putusan,
    alasan & balasan ikut), angka = belum dibuka, dibuka = nol, kabar baru sesudahnya = naik lagi, peta per akun tidak saling timpa.
  · functions/pesan.js: pesanPutus hanya saat menunggu → diputus, untuk uid peminta, balasan / alasan ikut, kirimanTablet = notifikasi Android saluran "kabar".
  PYTHON: apk/pasang.py — berkas Firebase diperiksa (paket wajib ada), plugin google-services dipastikan, izin notifikasi + ikon/saluran di manifest.
  STATIS: dock (pegangan lipat, tombol bulat, body.dock-lipat diingat, ruang dipakai keranjang/lembar, kolom keranjang tablet mulai dari atas), layar penuh
  (MainActivity diterapkan saat dibuka/kembali, geser dari tepi = muncul sebentar), lonceng di kepala 8 layar + lembarnya, fungsi kabarTablet, rules v17.

    python3 alat-uji/uji_tablet_tampilan.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tablet_tampilan.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, uji_titipan  # noqa: E402

JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
NT = 'baru/js/data/notif-tablet.js'; PR = 'baru/js/inti/perangkat.js'; KBL = 'baru/js/layar/kabar-baru-logika.js'; FMT = 'baru/js/inti/format.js'
TPL = 'baru/js/layar/titipan-logika.js'; PSN = 'functions/pesan.js'; FIX = 'functions/index.js'; PAS = 'apk/pasang.py'
IDX = 'baru/index.html'; KER = 'baru/css/kerangka.css'; APP = 'baru/js/app.js'; MA = 'apk/tambahan/MainActivity.java'; PP = 'apk/tambahan/PerangkatPlugin.java'
FB = 'baru/js/data/firebase.js'; MENU = 'baru/js/layar/menu.js'; LC = 'baru/js/layar/lonceng.js'; YML = '.github/workflows/apk.yml'; PKG = 'apk/package.json'
LAYAR = ['harga', 'jual', 'laporan', 'pelanggan', 'menu', 'stok', 'uang', 'ringkasan']
BERKAS = [NT, PR, KBL, FMT, TPL, PSN, FIX, PAS, IDX, KER, APP, MA, PP, FB, MENU, LC, YML, PKG] + ['baru/js/layar/%s.js' % n for n in LAYAR]


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS}
    for b, lama, baru in (ganti or []):
        assert t[b].count(lama) == 1, 'kontrol basi: %s · %r (%d×)' % (b, lama[:80], t[b].count(lama))
        t[b] = t[b].replace(lama, baru, 1)
    return t


CAP = r"""
var clearTimeout = function () {};   // jsc tanpa clearTimeout — waktu tunggu token disingkat alat uji (ntPasang tungguMs)
var __cap = { asli: true, headers: [{ name: 'PushNotifications', methods: [] }, { name: 'Perangkat', methods: [{ name: 'info' }, { name: 'layarPenuh' }] }],
  izin: 'prompt', izinMinta: 'granted', minta: 0, daftar: 0, token: 'tok-A-0123456789abcdef', galat: '', diam: false, dengar: {}, lepas: 0, unreg: 0, kanal: [], penuh: [] };
var __dengar = function (n, f) { (__cap.dengar[n] = __cap.dengar[n] || []).push(f); return Promise.resolve({ remove: function () { __cap.lepas++; var a = __cap.dengar[n]; var i = a.indexOf(f); if (i >= 0) a.splice(i, 1); } }); };
var __kabari = function (n, x) { (__cap.dengar[n] || []).slice().forEach(function (f) { f(x); }); };
window.Capacitor = { isNativePlatform: function () { return __cap.asli; }, get PluginHeaders() { return __cap.headers; }, Plugins: {
  PushNotifications: {
    checkPermissions: function () { return Promise.resolve({ receive: __cap.izin }); },
    requestPermissions: function () { __cap.minta++; __cap.izin = __cap.izinMinta; return Promise.resolve({ receive: __cap.izin }); },
    createChannel: function (o) { __cap.kanal.push(o); return Promise.resolve(); },
    addListener: __dengar,
    register: function () { __cap.daftar++; if (!__cap.diam) Promise.resolve().then(function () { if (__cap.galat) __kabari('registrationError', { error: __cap.galat }); else __kabari('registration', { value: __cap.token }); }); return Promise.resolve(); },
    unregister: function () { __cap.unreg++; return Promise.resolve(); } },
  Perangkat: { layarPenuh: function (o) { __cap.penuh.push(o); return Promise.resolve({ layarPenuh: !!o.nyala }); }, info: function () { return Promise.resolve({ pushSiap: true }); } } } };
var __tulis = []; var __uid = 'uid-tablet';
"""

PEMERIKSA = r"""
var H = []; function cek(nama, benar, ket) { H.push({ nama: nama, ok: !!benar, ket: ket === undefined ? '' : String(ket) }); }
var J = JSON.stringify;
ntPasang({ simpan: function (t) { __tulis.push(['simpan', t]); return Promise.resolve({ ok: true, id: __uid + '_p-1' }); }, hapus: function () { __tulis.push(['hapus']); return Promise.resolve({ ok: true }); },
  info: function () { return Promise.resolve(__info); }, uid: function () { return __uid; }, tungguMs: 40 });
var __info = { pushSiap: true };
async function utama() {
  // ---- dukung
  __cap.asli = false; cek('bukan aplikasi tablet → kartu tidak menawarkan push tablet', ntDukung({}).ok === false && ntAplikasi() === false); __cap.asli = true;
  var h0 = __cap.headers; __cap.headers = [{ name: 'Perangkat', methods: [] }]; var dPlugin = ntDukung({}); __cap.headers = h0;
  cek('APK lama tanpa plugin push → "pasang APK terbaru" (jalan keluar disebut)', !dPlugin.ok && /pasang APK terbaru/.test(dPlugin.sebab) && /docs\/notifikasi-tablet\.md/.test(dPlugin.sebab), dPlugin.sebab);
  var dFb = ntDukung({ pushSiap: false });
  cek('APK tanpa berkas Firebase → kalimat menyebut rahasia GOOGLE_SERVICES_JSON', !dFb.ok && /GOOGLE_SERVICES_JSON/.test(dFb.sebab), dFb.sebab);
  cek('APK baru dengan berkas Firebase → bisa', ntDukung({ pushSiap: true }).ok === true);
  // ---- nyalakan: APK tanpa Firebase ditolak SEBELUM meminta izin
  __info = { pushSiap: false }; var r0 = await ntNyalakan(); __info = { pushSiap: true };
  cek('Nyalakan di APK tanpa Firebase → ditolak tanpa minta izin & tanpa daftar', r0.gagal && __cap.minta === 0 && __cap.daftar === 0, J(r0));
  // ---- nyalakan sukses
  var r1 = await ntNyalakan(); var T1 = ntTersimpan(__uid);
  cek('Nyalakan: izin Android diminta sekali, daftar sekali, token disimpan atas nama akun', r1.ok && __cap.minta === 1 && __cap.daftar === 1 && __tulis.length === 1 && __tulis[0][1] === __cap.token, J([r1, __tulis]));
  cek('Nyalakan: saluran "kabar" dibuat (penting, bunyi)', __cap.kanal.length === 1 && __cap.kanal[0].id === 'kabar' && __cap.kanal[0].importance === 5, J(__cap.kanal));
  cek('Nyalakan: keadaan lokal ber-uid + ujung token (bukan token utuh)', T1 && T1.uid === __uid && T1.ujung === __cap.token.slice(-16) && JSON.stringify(T1).indexOf(__cap.token) < 0, J(T1));
  cek('keadaan lokal akun lain = tidak dianggap menyala', ntTersimpan('uid-lain') === null && ntTersimpan(__uid) !== null);
  cek('pendengar pendaftaran dilepas sesudah token datang (tidak menumpuk)', (__cap.dengar.registration || []).length === 0 && (__cap.dengar.registrationError || []).length === 0, J(Object.keys(__cap.dengar)));
  // ---- segarkan: token sama → tidak menulis; tanpa minta izin
  var nTulis = __tulis.length; var mi = __cap.minta; var s1 = await ntSegarkan();
  cek('Segarkan (token sama): tidak menulis, tidak minta izin', s1.ok && s1.sama && __tulis.length === nTulis && __cap.minta === mi, J(s1));
  __cap.token = 'tok-B-fedcba9876543210'; var s2 = await ntSegarkan();
  cek('Segarkan (Google mengganti token): token baru ditulis, keadaan lokal ikut', s2.ok && s2.baru && __tulis[__tulis.length - 1][1] === 'tok-B-fedcba9876543210' && ntTersimpan(__uid).ujung === 'tok-B-fedcba9876543210'.slice(-16), J([s2, __tulis]));
  __cap.izin = 'denied'; var nT = __tulis.length; var s3 = await ntSegarkan(); __cap.izin = 'granted';
  cek('Segarkan saat izin dicabut di Setelan: tidak minta izin, tidak menulis', s3.gagal && __cap.minta === mi && __tulis.length === nT, J(s3));
  // ---- matikan
  var m1 = await ntMatikan();
  cek('Matikan: token dicabut dari Google & dikosongkan di server, keadaan lokal hilang', m1.ok && __cap.unreg === 1 && __tulis[__tulis.length - 1][0] === 'hapus' && ntTersimpan(__uid) === null, J(m1));
  var s4 = await ntSegarkan(); cek('Segarkan sesudah dimatikan = lewat (tidak menyalakan diam-diam)', s4.lewat === true && __cap.daftar === 3, J([s4, __cap.daftar]));
  // ---- gagal jujur
  __cap.izin = 'prompt'; __cap.izinMinta = 'denied'; var g1 = await ntNyalakan(); __cap.izinMinta = 'granted';
  cek('izin ditolak → kalimat menyebut Setelan Android, tidak mendaftar', g1.gagal && /Setelan Android/.test(g1.pesan) && __cap.daftar === 3, J(g1));
  __cap.galat = 'SERVICE_NOT_AVAILABLE'; var nt2 = __tulis.length; var g2 = await ntNyalakan(); __cap.galat = '';
  cek('Google menolak pendaftaran → gagal dengan teks aslinya, token tidak disimpan', g2.gagal && /SERVICE_NOT_AVAILABLE/.test(g2.pesan) && __tulis.length === nt2, J(g2));
  __cap.diam = true; var g3 = await ntNyalakan(); __cap.diam = false;
  cek('token tidak datang → gagal "tidak datang dalam … detik", pendengar dilepas', g3.gagal && /tidak datang dalam/.test(g3.pesan) && (__cap.dengar.registration || []).length === 0, J(g3));
  // ---- diketuk
  var ke = []; ntPadaKetuk(function (l) { ke.push(l); }); await Promise.resolve(); __kabari('pushNotificationActionPerformed', { notification: { data: { layar: 'menu' } } });
  cek('notifikasi diketuk → layar tujuan dari data kiriman', ke.length === 1 && ke[0] === 'menu', J(ke));
  // ---- layar penuh
  cek('layar penuh: APK baru punya metodenya', layarPenuhAda() === true);
  var lp = {}; try { lp = await setelLayarPenuh(true); } catch (e) { lp = { galat: String(e && e.message || e) }; } cek('layar penuh: Perangkat.layarPenuh { nyala: true }', lp.layarPenuh === true && __cap.penuh.length === 1 && __cap.penuh[0].nyala === true, J([lp, __cap.penuh]));
  var hp = __cap.headers; __cap.headers = [{ name: 'Perangkat', methods: [{ name: 'info' }] }]; var ada2 = layarPenuhAda(); __cap.headers = hp;
  cek('layar penuh: APK lama tanpa metode → false (saklar tidak tampil)', ada2 === false);
  __cap.asli = false; cek('layar penuh: HP/Mac (bukan aplikasi) → false', layarPenuhAda() === false); __cap.asli = true;
  // ---- lonceng
  var D = [
    { id: 'p1', tindakan: 'pesan', status: 'menunggu', teks: 'Beras habis', dari: 'Penjaga A', mintaUid: 'uid-tablet', tanggal: '2026-11-23', jam: '09:00' },
    { id: 'k1', tindakan: 'uangKeluar', status: 'menunggu', jenis: 'toko', teks: 'Plastik', nominal: 20000, dari: 'Penjaga A', mintaUid: 'uid-tablet', tanggal: '2026-11-23', jam: '10:00' },
    { id: 'p0', tindakan: 'pesan', status: 'dibaca', teks: 'Lampu mati', balasan: 'Besok diganti', dari: 'Penjaga A', mintaUid: 'uid-tablet', tanggal: '2026-11-22', jam: '08:00', diputusTanggal: '2026-11-23', diputusJam: '11:00' },
    { id: 'k0', tindakan: 'uangKeluar', status: 'ditolak', alasanTolak: 'Belum perlu', jenis: 'toko', teks: 'Sapu', nominal: 15000, dari: 'Penjaga A', mintaUid: 'uid-tablet', tanggal: '2026-11-22', jam: '07:00', diputusTanggal: '2026-11-22', diputusJam: '12:00' },
    { id: 'x9', tindakan: 'pesan', status: 'dibaca', teks: 'dari akun lain', mintaUid: 'uid-lain', tanggal: '2026-11-23', jam: '12:00', diputusTanggal: '2026-11-23', diputusJam: '12:30' }];
  var OW = { jenis: 'owner', uid: 'uid-owner' }; var TB = { jenis: 'staf', uid: 'uid-tablet', peran: 'ben' };
  var L1 = kbLonceng(OW, D, {});
  cek('lonceng owner: hanya yang MENUNGGU, terbaru dulu, angka = belum dibuka', L1.owner && L1.daftar.map(function (x) { return x.id; }).join() === 'k1,p1' && L1.n === 2 && L1.menunggu === 2, J(L1.daftar.map(function (x) { return x.id; })));
  cek('lonceng owner: pesan bisa dibalas, titipan uang tidak (dibuka di Uang)', L1.daftar.find(function (x) { return x.id === 'p1'; }).bisaBalas === true && L1.daftar.find(function (x) { return x.id === 'k1'; }).bisaBalas === false && L1.daftar.find(function (x) { return x.id === 'k1'; }).layar === 'uang');
  var L2 = kbLonceng(OW, D, kbTandai(L1));
  cek('lonceng owner: sesudah dibuka angka nol, isi tetap', L2.n === 0 && L2.daftar.length === 2);
  var D2 = D.concat([{ id: 'p2', tindakan: 'pesan', status: 'menunggu', teks: 'Pembeli tanya', mintaUid: 'uid-tablet', tanggal: '2026-11-23', jam: '13:00' }]);
  cek('lonceng owner: pesan baru sesudah dibuka → angka 1, paling atas', kbLonceng(OW, D2, kbTandai(L1)).n === 1 && kbLonceng(OW, D2, kbTandai(L1)).daftar[0].id === 'p2');
  var T0 = kbLonceng(TB, D, {});
  cek('lonceng tablet: milik akun ini saja (menunggu + diputus), terbaru menurut jam kejadiannya (putusan / kiriman), akun lain tidak ikut', T0.daftar.map(function (x) { return x.id; }).join() === 'p0,k1,p1,k0' && T0.daftar.every(function (x) { return x.id !== 'x9'; }), J(T0.daftar.map(function (x) { return [x.id, x.urut]; })));
  cek('lonceng tablet: angka = putusan yang belum dibuka (bukan yang masih menunggu)', T0.n === 2, T0.n);
  var p0 = T0.daftar.find(function (x) { return x.id === 'p0'; }); var k0 = T0.daftar.find(function (x) { return x.id === 'k0'; });
  cek('lonceng tablet: balasan owner & alasan tolak ikut, judul menyebut putusannya', p0.balasan === 'Besok diganti' && /dibaca owner/.test(p0.judul) && k0.alasan === 'Belum perlu' && /DITOLAK/.test(k0.judul) && !p0.bisaBalas, J([p0, k0]));
  var T1b = kbLonceng(TB, D, kbTandai(T0)); var D3 = D.map(function (m) { return m.id === 'k1' ? Object.assign({}, m, { status: 'disetujui', diputusTanggal: '2026-11-23', diputusJam: '14:00' }) : m; });
  var T2 = kbLonceng(TB, D3, kbTandai(T0));
  cek('lonceng tablet: owner menyetujui titipan sesudah dibuka → angka 1 (status berubah = kabar baru)', T1b.n === 0 && T2.n === 1 && T2.daftar[0].id === 'k1' && /disetujui/.test(T2.daftar[0].judul), J([T1b.n, T2.n, T2.daftar[0]]));
  var teks = kbTulisLihat(null, 'uid-owner', { a: 'menunggu' }); teks = kbTulisLihat(teks, 'uid-tablet', { b: 'dibaca' });
  cek('peta "sudah dibuka" per akun: akun lain di perangkat yang sama tidak tertimpa', J(kbBacaLihat(teks, 'uid-owner')) === J({ a: 'menunggu' }) && J(kbBacaLihat(teks, 'uid-tablet')) === J({ b: 'dibaca' }) && kbBacaLihat(teks, 'uid-baru') === null && kbBacaLihat('rusak{', 'x') === null);
  var banyak = []; for (var i = 0; i < 40; i++) banyak.push({ id: 'm' + i, tindakan: 'pesan', status: 'menunggu', teks: 'p' + i, mintaUid: 'u', tanggal: '2026-11-23', jam: String(10 + (i % 10)) + ':' + String(10 + i) });
  var LB = kbLonceng(OW, banyak, {}); cek('lonceng: paling banyak 30 baris, sisanya disebut, angka dari SEMUA', LB.daftar.length === 30 && LB.lebih === 10 && LB.n === 40, J([LB.daftar.length, LB.lebih, LB.n]));
  // ---- isi push tablet (functions/pesan.js)
  var P = __modul.exports;
  var a = P.pesanPutus({ status: 'menunggu', tindakan: 'pesan', teks: 'Lampu mati', mintaUid: 'uid-tablet' }, { status: 'dibaca', tindakan: 'pesan', teks: 'Lampu mati', balasan: 'Besok diganti', mintaUid: 'uid-tablet' }, 'p0');
  cek('push tablet: pesan dibaca + balasan → untuk uid peminta, balasan di depan', a && a.uid === 'uid-tablet' && a.judul === 'Pesan dibaca owner' && /^Balasan owner: Besok diganti/.test(a.isi) && a.layar === 'menu' && a.tag === 'putus-p0', J(a));
  var b = P.pesanPutus({ status: 'menunggu', tindakan: 'uangKeluar', jenis: 'toko', teks: 'Sapu', nominal: 15000, mintaUid: 'u1' }, { status: 'ditolak', alasanTolak: 'Belum perlu', tindakan: 'uangKeluar', jenis: 'toko', teks: 'Sapu', nominal: 15000, mintaUid: 'u1' }, 'k0');
  cek('push tablet: titipan ditolak → judul DITOLAK, alasan + rupiah', b && /DITOLAK owner/.test(b.judul) && /Alasan: Belum perlu/.test(b.isi) && /Rp15\.000/.test(b.isi), J(b));
  var c = P.pesanPutus({ status: 'menunggu', tindakan: 'nego', teks: 'Beras 5 kg', nominal: 70000, negoUid: 'u2' }, { status: 'disetujui', tindakan: 'nego', teks: 'Beras 5 kg', nominal: 70000, negoUid: 'u2' }, 'n1');
  cek('push tablet: nego disetujui → uid dari negoUid', c && c.uid === 'u2' && /disetujui owner/.test(c.judul), J(c));
  cek('push tablet: TIDAK dikirim bila belum diputus, sudah diputus sebelumnya, atau tanpa peminta',
    P.pesanPutus({ status: 'menunggu' }, { status: 'menunggu', mintaUid: 'u' }, 'x') === null && P.pesanPutus({ status: 'dibaca' }, { status: 'dibaca', balasan: 'lagi', mintaUid: 'u' }, 'x') === null
    && P.pesanPutus({ status: 'menunggu' }, { status: 'dibaca' }, 'x') === null && P.pesanPutus(null, {}, 'x') === null);
  var k = P.kirimanTablet(a, ['t1', 't2']);
  cek('push tablet: kiriman = notifikasi Android saluran "kabar", prioritas tinggi, data layar teks', J(k.tokens) === J(['t1', 't2']) && k.notification.title === a.judul && k.android.priority === 'high' && k.android.notification.channelId === 'kabar' && k.data.layar === 'menu' && typeof k.data.tag === 'string', J(k));
  var pj = P.pesanPutus({ status: 'menunggu', tindakan: 'pesan', mintaUid: 'u' }, { status: 'dibaca', tindakan: 'pesan', teks: 'z'.repeat(300), balasan: 'y'.repeat(150), mintaUid: 'u' }, 'q');
  cek('push tablet: isi dipendekkan (layar kunci)', pj.isi.length <= P.BATAS_ISI, pj.isi.length);
  print(JSON.stringify(H));
}
utama().catch(function (e) { print(JSON.stringify([{ nama: 'jsc jatuh', ok: false, ket: String(e && e.stack || e) }])); });
"""


def lingkup(teks):
    """Modul tanpa impor dalam lingkupnya sendiri (notif-tablet.js & perangkat.js sama-sama punya `const cap`); ekspornya dijadikan global."""
    nama = re.findall(r'^export\s+(?:async\s+)?(?:function|const|let)\s+(\w+)', teks, re.M)
    return 'var __m = (function () {\n' + bundel_baru.polos(teks) + '\nreturn { ' + ', '.join('%s: %s' % (n, n) for n in nama) + ' };\n})();\n' + ''.join('var %s = __m.%s;\n' % (n, n) for n in nama)


def jalankan_jsc(t):
    js = bundel_baru.PRELUDE + uji_titipan.TIRUAN + CAP
    js += bundel_baru.polos(t[FMT]) + '\n' + bundel_baru.polos(t[TPL]) + '\n' + bundel_baru.polos(t[KBL]) + '\n' + lingkup(t[NT]) + lingkup(t[PR])
    js += 'var __modul = { exports: {} }; (function (module) {\n' + t[PSN] + '\n})(__modul);\n' + PEMERIKSA
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(js); p = f.name
    try: r = subprocess.run([JSC, p], capture_output=True, text=True, timeout=120)
    finally: os.unlink(p)
    baris = [x for x in r.stdout.strip().splitlines() if x.startswith('[')]
    if not baris: return [{'nama': 'jsc tidak jalan', 'ok': False, 'ket': (r.stderr or r.stdout).strip()[:600]}]
    return json.loads(baris[-1])


MANIFEST_UJI = None


def periksa_python(t):
    import importlib.util  # noqa: F401
    import uji_perangkat_sunmi as U
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    ruang = {'__name__': 'pasang_uji', '__file__': os.path.join(AKAR, PAS)}
    try: exec(compile(t[PAS], PAS, 'exec'), ruang)
    except Exception as e: return [{'nama': 'pasang.py tidak bisa dimuat', 'ok': False, 'ket': repr(e)}]
    Tolak = ruang['Tolak']
    def ditolak(f, *a):
        try: f(*a)
        except Tolak: return True
        except Exception: return False
        return False
    m = ruang['ubah_manifest'](U.MANIFEST)
    ok('manifest: izin notifikasi (Android 13+) tepat sekali, di luar <application>', m.count('<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />') == 1 and m.index('POST_NOTIFICATIONS') < m.index('<application'))
    blok = m[m.index('<application'):m.index('</application>')]
    ok('manifest: ikon kecil notifikasi = @drawable/ic_kabar & saluran bawaan "kabar", di dalam <application>, tepat sekali',
       blok.count('default_notification_icon" android:resource="@drawable/ic_kabar"') == 1 and blok.count('default_notification_channel_id" android:value="kabar"') == 1)
    ok('manifest: dijalankan dua kali = sama (dengan bagian notifikasi)', ruang['ubah_manifest'](m) == m)
    gs = {'project_info': {'project_id': 'proyek-contoh', 'project_number': '1'}, 'client': [{'client_info': {'mobilesdk_app_id': '1:1:android:x', 'android_client_info': {'package_name': 'id.miqbal.tokoberas'}}}]}
    ok('google-services: berkas yang memuat paket aplikasi diterima', json.loads(ruang['periksa_gs'](json.dumps(gs)))['project_info']['project_id'] == 'proyek-contoh')
    gs2 = json.loads(json.dumps(gs)); gs2['client'][0]['client_info']['android_client_info']['package_name'] = 'com.lain'
    ok('google-services: berkas aplikasi lain DITOLAK (bangun gagal, bukan APK diam-diam tanpa push)', ditolak(ruang['periksa_gs'], json.dumps(gs2)))
    ok('google-services: bukan JSON DITOLAK', ditolak(ruang['periksa_gs'], 'bukan json'))
    app_g = U.GRADLE; akar_g = "buildscript {\n    dependencies {\n        classpath 'com.android.tools.build:gradle:8.7.2'\n    }\n}\n"
    a2, r2 = ruang['ubah_gradle_gs'](app_g, akar_g)
    ok('gradle: plugin google-services diterapkan & classpath-nya ditambah bila cetakan tidak membawanya', "apply plugin: 'com.google.gms.google-services'" in a2 and "classpath 'com.google.gms:google-services:" in r2 and r2.index('tools.build:gradle') < r2.index('google-services'))
    ok('gradle: cetakan yang sudah membawanya tidak diubah (dua kali = sama)', ruang['ubah_gradle_gs'](a2, r2) == (a2, r2))
    ok('gradle: build.gradle akar tanpa classpath Android DITOLAK', ditolak(ruang['ubah_gradle_gs'], app_g, 'buildscript {}'))
    ok('pasang.py memasang berkas Firebase dari rahasia GOOGLE_SERVICES_JSON & menyalin ikon notifikasi', "os.environ.get('GOOGLE_SERVICES_JSON'" in t[PAS] and "'ic_kabar.xml'" in t[PAS] and 'pasang_firebase();' in t[PAS])
    ok('apk.yml meneruskan rahasia GOOGLE_SERVICES_JSON ke langkah pasang & menulis ringkasan ada-tidaknya push', 'GOOGLE_SERVICES_JSON: ${{ secrets.GOOGLE_SERVICES_JSON }}' in t[YML] and 'Push tablet: TANPA berkas Firebase' in t[YML])
    ok('apk/package.json membawa plugin resmi @capacitor/push-notifications seri 7', json.loads(t[PKG])['dependencies'].get('@capacitor/push-notifications', '').startswith('^7'))
    return h


def periksa_statis(t):
    h = []; ok = lambda nama, benar, ket='': h.append({'nama': nama, 'ok': bool(benar), 'ket': str(ket)})
    I, K, A = t[IDX], t[KER], t[APP]
    # ---- dock
    ok('dock: pegangan lipat di dalam menu bawah (button, bukan petak tujuan)', re.search(r'<button type="button" class="nav-lipat" data-dock="lipat"[^>]*>', I) and I.index('class="nav-lipat"') < I.index('</nav>'))
    ok('dock: tombol bulat pembuka di luar menu bawah', 'id="dockBuka" class="dock-buka" data-dock="buka"' in I and I.index('id="dockBuka"') > I.index('</nav>'))
    ok('dock: dilipat = menu bawah turun mengecil & tak bisa diketuk; tombol bulat muncul', 'body.dock-lipat .nav { transform: translateY(calc(100% + 30px)) scale(0.3); opacity: 0; pointer-events: none; }' in K
       and 'body.dock-lipat .dock-buka { opacity: 1; transform: none; pointer-events: auto; }' in K)
    ok('dock: gerak berkurva toko (480 ms cubic-bezier(.2,.8,.2,1)) + hormat prefers-reduced-motion', '.nav { transition: transform 480ms cubic-bezier(.2,.8,.2,1)' in K and '@media (prefers-reduced-motion: reduce) { .nav, .dock-buka' in K)
    ok('dock: ruang yang dibebaskan dipakai keranjang (tablet) & laci keranjang (HP)', 'body.dock-lipat .jual-keranjang { max-height: calc(100vh - 28px); max-height: calc(100dvh - 28px); }' in K and 'body.dock-lipat .jual-keranjang { bottom: 16px; right: 78px; }' in K)
    ok('dock: tirai tidak ikut digeser (lembar bukan tirai saja)', 'body.dock-lipat .lembar:not(.tirai) { bottom: 80px; }' in K.replace('body.dock-lipat .kabar-nav, ', '') or 'body.dock-lipat .kabar-nav, body.dock-lipat .lembar:not(.tirai) { bottom: 80px; }' in K)
    ok('dock: Mac (menu samping) tanpa tombol bulat; layar terkunci tanpa tombol bulat', '@media (min-width: 1100px) { .dock-buka { display: none; } }' in K and 'body.terkunci .dock-buka { display: none !important; }' in K)
    ok('dock: diingat per perangkat (localStorage) & dipulihkan saat dibuka', "const KUNCI_DOCK = 'miqbal_dock_lipat_v1';" in A and "dockLipat(localStorage.getItem(KUNCI_DOCK) === '1', false)" in A and "dockLipat(b.dataset.dock === 'lipat', true)" in A)
    ok('dock: penanda emas diukur ulang sesudah dock naik', 'if (!lipat) setTimeout(() => nanti(geserPenanda), 520);' in A)
    ok('tablet: kolom keranjang mulai dari ATAS (bukan di bawah judul) di 720–1099 px', '"kepala keranjang" "pita keranjang" "kabar keranjang" "rak keranjang" "samping keranjang"' in K)
    # ---- layar penuh
    M, PG = t[MA], t[PP]
    ok('layar penuh: bilah status & navigasi disembunyikan, geser dari tepi = muncul sebentar', 'BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE' in M and 'k.hide(WindowInsetsCompat.Type.systemBars());' in M and 'k.show(WindowInsetsCompat.Type.systemBars());' in M)
    ok('layar penuh: diterapkan saat dibuka, kembali ke depan, dan fokus kembali (sesudah dialog / papan ketik)', M.count('terapkanLayarPenuh(this, layarPenuhTersimpan(this));') == 3 and 'public void onResume()' in M and 'public void onWindowFocusChanged(boolean hasFocus)' in M)
    ok('layar penuh: disimpan aplikasi (SharedPreferences), saklar lewat Perangkat.layarPenuh di benang UI', '@PluginMethod\n    public void layarPenuh(PluginCall call)' in PG and 'MainActivity.simpanLayarPenuh(getContext(), nyala);' in PG and 'a.runOnUiThread(' in PG)
    ok('push: Perangkat.info melapor pushSiap dari sumber daya google_app_id (APK dengan berkas Firebase)', 'getIdentifier("google_app_id", "string"' in PG and 'o.put("pushSiap", pushSiap());' in PG)
    ok('push: saluran "Kabar toko" penting dibuat aplikasi saat dibuka', 'new NotificationChannel(SALURAN, "Kabar toko", NotificationManager.IMPORTANCE_HIGH)' in M and 'static final String SALURAN = "kabar";' in M)
    ok('Menu: kartu notifikasi tablet & layar penuh di aplikasi tablet — owner (Perangkat & antrean) DAN akun tablet (Menu staf), bukan kalimat "peramban tidak mendukung"',
       'if (ntAplikasi()) return h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}`;' in t[MENU] and "${ntAplikasi() ? h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}` : ''}" in t[MENU] and "data-aksi=\"lpSetel\" data-n=\"1\"" in t[MENU])
    # ---- lonceng
    for n in LAYAR:
        s = t['baru/js/layar/%s.js' % n]
        ok('lonceng di kepala layar %s, tepat sebelum pil akun' % n, ('${loncengMentah()}<div class="pil pil-akun' in s) if n != 'ringkasan' else ('${pintuLonceng()}<div class="pil pil-akun" id="rkPil"' in s))
    ok('lonceng: lembarnya ada di halaman & tersembunyi saat terkunci', 'id="lembarLonceng" class="lembar-lonceng kartu"' in I and 'body.terkunci .lembar-lonceng { display: none !important; }' in K and '.lembar-lonceng[hidden] { display: none; }' in K)
    ok('lonceng: bergoyang saat kabar baru, angka meletup', '.lonceng.goyang svg { animation: loncengGoyang' in K and '.lonceng-n.letup { animation: loncengLetup' in K)
    L = t[LC]
    ok('lonceng: balas lewat pintu yang SAMA dengan Uang (tpSusunPutus dibaca), hanya akun owner', "tpSusunPutus(id, 'dibaca', { balasan: _balas[id] || '' }" in L and "if (!_akun || _akun.jenis !== 'owner' || _sibuk) return;" in L and "owner && x.bisaBalas ?" in L)
    ok('lonceng: dihitung ulang tiap data berubah (app.js periksaKabarBaru)', 'loncengSegarkan(' in A and 'pasangLonceng({ pindah: (t) => pindah(t)' in A)
    # ---- push sisi server & rules
    F = t[FIX]
    ok('fungsi kabarTablet: pemicu UBAH persetujuan, token notifPerangkat milik uid peminta, token kosong dilewati', "exports.kabarTablet = onDocumentUpdated('persetujuan/{id}'" in F and ".collection('notifPerangkat').where('uid', '==', p.uid)" in F and "typeof x.token === 'string' && x.token" in F)
    ok('firebase.js: token tablet atas nama akun yang masuk, id = uid_perangkat, mati = dikosongkan', "const id = uid + '_' + pid;" in t[FB] and "export const hapusTokenTablet = () => tulisTokenTablet('');" in t[FB])
    ok('app.js: token tablet diperbarui diam-diam sekali per akun; notifikasi diketuk = pindah layar', 'ntSegarkan().catch(() => {})' in A and "ntPadaKetuk((t) => { if (['uang', 'menu', 'jual'].indexOf(t) >= 0) pindah(t); });" in A)
    return h


def jalankan(t):
    return jalankan_jsc(t) + periksa_python(t) + periksa_statis(t)


KONTROL = [
    ('izin notifikasi tidak diminta (Android 13+ diam)', [(NT, "if ((!iz || iz.receive !== 'granted') && mintaIzin !== false) iz = await P.requestPermissions();", "")]),
    ('APK tanpa Firebase tetap meminta izin & mendaftar', [(NT, "  if (info && info.pushSiap === false) return { ok: false, sebab: NT_TANPA_FIREBASE };\n", "")]),
    ('keadaan lokal tanpa uid (akun lain dianggap menyala)', [(NT, "return x && (!uid || x.uid === uid) ? x : null;", "return x;")]),
    ('pendengar pendaftaran tidak dilepas', [(NT, "pegang.forEach((x) => { try { if (x && typeof x.remove === 'function') x.remove(); } catch (e) { /* sudah lepas */ } }); ", "")]),
    ('segarkan selalu menulis', [(NT, "  if (lama.ujung === ujungToken(t.token)) return { ok: true, sama: true };\n", "")]),
    ('segarkan meminta izin', [(NT, "const t = await ntToken(false); if (!t.ok) return t;\n  if (lama.ujung", "const t = await ntToken(true); if (!t.ok) return t;\n  if (lama.ujung")]),
    ('matikan tidak mencabut dari Google', [(NT, "try { if (P && typeof P.unregister === 'function') await P.unregister(); } catch (e) { /* sudah tidak terdaftar */ }", "")]),
    ('lonceng owner ikut memuat yang sudah diputus', [(KBL, "      if (st !== 'menunggu') return;\n", "")]),
    ('lonceng tablet memuat akun lain', [(KBL, "    if (!uid || uidPeminta(m) !== uid) return;\n", "")]),
    ('lonceng tablet menghitung yang masih menunggu', [(KBL, "baru: putus && L[id] !== st });", "baru: L[id] !== st });")]),
    ('peta dibuka menimpa akun lain', [(KBL, "  x[String(uid || '')] = peta || {}; return JSON.stringify(x);", "  return JSON.stringify({ [String(uid || '')]: peta || {} });")]),
    ('push tablet untuk permintaan yang sudah diputus sebelumnya', [(PSN, "  if ((sebelum.status || 'menunggu') !== 'menunggu') return null;\n  const st = sesudah.status", "  const st = sesudah.status")]),
    ('push tablet tanpa balasan owner', [(PSN, "st === 'dibaca' && teks(sesudah.balasan) ? 'Balasan owner: ' + teks(sesudah.balasan) + ' — ' : ''", "''")]),
    ('push tablet tanpa saluran kabar', [(PSN, "notification: { channelId: SALURAN_TABLET, tag: p.tag,", "notification: { tag: p.tag,")]),
    ('layar penuh memanggil metode lain', [(PR, "panggilAsli('Perangkat', 'layarPenuh', { nyala: !!nyala })", "panggilAsli('Perangkat', 'penuh', { nyala: !!nyala })")]),
    ('manifest tanpa izin notifikasi', [(PAS, "    wajib += ['<uses-permission android:name=\"%s\" />' % IZIN_NOTIF, META_IKON, META_SALURAN]\n", ""), (PAS, "    if IZIN_NOTIF not in m:\n", "    if False:\n")]),
    ('google-services aplikasi lain diterima', [(PAS, "    if PAKET not in nama: raise Tolak(", "    if False: raise Tolak(")]),
    ('dock tidak diingat', [(APP, "try { dockLipat(localStorage.getItem(KUNCI_DOCK) === '1', false); } catch (e) { /* bawaan: dock terbuka */ }\n", "")]),
    ('layar penuh tidak diterapkan saat kembali ke depan', [(MA, "    public void onResume() {\n        super.onResume();\n        terapkanLayarPenuh(this, layarPenuhTersimpan(this));\n", "    public void onResume() {\n        super.onResume();\n")]),
    ('kartu notifikasi tablet tidak ada di Menu akun tablet', [(MENU, "      ${ntAplikasi() ? h`${gambarNotifTablet(s)}${gambarLayarPenuh(s)}` : ''}\n", "")]),
    ('lonceng hilang dari kepala Stok', [('baru/js/layar/stok.js', '${loncengMentah()}<div class="pil pil-akun', '<div class="pil pil-akun')]),
    ('karyawan tablet boleh membalas dari lonceng', [(LC, "if (!_akun || _akun.jenis !== 'owner' || _sibuk) return;", "if (!_akun || _sibuk) return;")]),
    ('kabarTablet mengirim ke semua token', [(FIX, ".collection('notifPerangkat').where('uid', '==', p.uid).get()", ".collection('notifPerangkat').get()")]),
]


def main():
    if '--kontrol' in sys.argv:
        kode = 0; dasar = {(x['nama']) for x in jalankan(baca()) if x['ok']}
        for nama, ganti in KONTROL:
            try: t = baca(ganti)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' — ' + str(e)); kode = 3; continue
            gagal = [x for x in jalankan(t) if not x['ok'] and (x['nama'] in dasar or x['nama'].startswith('jsc '))]   # jsc jatuh = ketahuan juga
            print(('BERBUNYI ' if gagal else 'DIAM!!   ') + nama + (' → ' + gagal[0]['nama'][:110] if gagal else ''))
            if not gagal: kode = 3
        print('KONTROL %s %d' % ('LULUS' if kode == 0 else 'GAGAL', len(KONTROL))); sys.exit(kode)
    H = jalankan(baca()); g = [x for x in H if not x['ok']]
    for x in H: print(('  ok  ' if x['ok'] else 'GAGAL ') + x['nama'] + ('' if x['ok'] else ' — ' + x['ket'][:300]))
    print('TAMPILAN TABLET (kotak pasir): %d lulus · %d gagal' % (len(H) - len(g), len(g)))
    sys.exit(1 if g else 0)


if __name__ == '__main__':
    main()
