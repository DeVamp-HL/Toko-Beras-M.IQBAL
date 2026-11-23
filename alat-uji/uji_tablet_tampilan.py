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
TPL = 'baru/js/layar/titipan-logika.js'; PSN = 'functions/pesan.js'; FIX = 'functions/index.js'; PAS = 'apk/pasang.py'; IKM = 'apk/ikon_m.py'
IDX = 'baru/index.html'; KER = 'baru/css/kerangka.css'; APP = 'baru/js/app.js'; MA = 'apk/tambahan/MainActivity.java'; PP = 'apk/tambahan/PerangkatPlugin.java'
FB = 'baru/js/data/firebase.js'; SIS = 'baru/js/layar/sistem-logika.js'; MENU = 'baru/js/layar/menu.js'; LC = 'baru/js/layar/lonceng.js'; YML = '.github/workflows/apk.yml'; PKG = 'apk/package.json'
LAYAR = ['harga', 'jual', 'laporan', 'pelanggan', 'menu', 'stok', 'uang', 'ringkasan']
BERKAS = [NT, PR, KBL, FMT, TPL, PSN, FIX, PAS, IKM, IDX, KER, APP, MA, PP, FB, MENU, LC, YML, PKG, SIS] + ['baru/js/layar/%s.js' % n for n in LAYAR]


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
  var OW = { jenis: 'owner', uid: 'uid-owner' }; var TB = { jenis: 'staf', uid: 'uid-tablet', peran: 'ben' }; var HI = '2026-11-23';
  var kunci = function (L) { return L.map(function (x) { return x.kunci || x.id; }).join(); };
  var L1 = kbLonceng(OW, D, {}, HI);
  cek('lonceng owner: tab Kabar = permintaan MENUNGGU selain pesan (pesan pindah ke Obrolan)', L1.owner && kunci(L1.daftar) === 'k1' && L1.menunggu === 1 && L1.nKabar === 1 && L1.daftar[0].bisaBalas === false && L1.daftar[0].layar === 'uang', J(L1.daftar));
  cek('obrolan owner: semua pesan tablet + balasan lama jadi gelembung owner, terlama dulu', kunci(L1.obrolan) === 'p0,p1,p0-balas,x9' && L1.obrolan[2].dari === 'owner' && L1.obrolan[2].teks === 'Besok diganti' && L1.obrolan[0].dari === 'tablet' && L1.obrolan[0].nama === 'Penjaga A', J(L1.obrolan));
  cek('obrolan: label hari (Kemarin / Hari ini) di gelembung pertama tiap tanggal, nama di awal rentetan', L1.obrolan[0].pisah === 'Kemarin' && L1.obrolan[1].pisah === 'Hari ini' && L1.obrolan[2].pisah === '' && L1.obrolan[1].namaTampil === true && L1.obrolan[2].namaTampil === true, J(L1.obrolan.map(function (x) { return [x.kunci, x.pisah, x.namaTampil]; })));
  cek('obrolan: centang — pesan tablet menunggu ✓ (1), sudah dibaca owner ✓✓ (2)', L1.obrolan[0].centang === 2 && L1.obrolan[1].centang === 1 && L1.obrolan[3].centang === 2);
  cek('obrolan owner: belum dibaca = pesan tablet yang MENUNGGU (keadaan server); angka lonceng = kabar + obrolan', L1.nObrolan === 1 && J(L1.belumDibaca) === J(['p1']) && L1.n === 2, J([L1.nObrolan, L1.belumDibaca, L1.n]));
  var L2 = kbLonceng(OW, D, kbTandai(L1), HI);
  cek('owner: membuka lonceng saja TIDAK membersihkan obrolan (baru bersih sesudah pesan ditandai dibaca di server)', L2.nKabar === 0 && L2.nObrolan === 1 && L2.daftar.length === 1, J([L2.nKabar, L2.nObrolan]));
  var Db = D.map(function (m) { return m.id === 'p1' ? Object.assign({}, m, { status: 'dibaca', balasan: '', diputusTanggal: HI, diputusJam: '09:05' }) : m; });
  var L2b = kbLonceng(OW, Db, kbTandai(L1), HI);
  cek('owner: pesan ditandai dibaca (dari HP / Mac mana pun) → obrolan bersih, centang tablet jadi dua, TANPA gelembung balasan kosong', L2b.nObrolan === 0 && L2b.belumDibaca.length === 0 && L2b.obrolan[1].centang === 2 && kunci(L2b.obrolan) === 'p0,p1,p0-balas,x9', J(L2b.obrolan));
  var D2 = D.concat([{ id: 'p2', tindakan: 'pesan', status: 'menunggu', teks: 'Pembeli tanya', mintaUid: 'uid-tablet', tanggal: '2026-11-23', jam: '13:00' }]);
  var L3 = kbLonceng(OW, D2, kbTandai(L1), HI);
  cek('owner: pesan tablet baru → angka obrolan naik, gelembungnya di ujung utas', L3.nObrolan === 2 && L3.obrolan[L3.obrolan.length - 1].kunci === 'p2' && L3.obrolan[L3.obrolan.length - 1].baru === true, J([L3.nObrolan, kunci(L3.obrolan)]));
  var DK = [{ id: 'b1', tindakan: 'barangMasuk', status: 'menunggu', teks: 'Datang 10 karung', mintaUid: 'uid-tablet', tanggal: HI, jam: '07:00' }];
  cek('owner: kabar barang masuk tetap di tab Kabar & bisa ditandai diperiksa + balasan', kbLonceng(OW, DK, {}, HI).daftar[0].bisaBalas === true && kbLonceng(OW, DK, {}, HI).obrolan.length === 0);
  var T0 = kbLonceng(TB, D, {}, HI);
  var Tz = kbLonceng(TB, D.concat([{ id: 'z1', tindakan: 'uangKeluar', status: 'ditolak', alasanTolak: 'x', jenis: 'toko', teks: 'Lain', nominal: 1000, mintaUid: 'uid-lain', tanggal: HI, jam: '15:00', diputusTanggal: HI, diputusJam: '15:10' }]), {}, HI);
  cek('lonceng tablet: tab Kabar = permintaan milik akun ini selain pesan, terbaru menurut jam kejadiannya; akun lain tidak ikut', kunci(T0.daftar) === 'k1,k0' && kunci(Tz.daftar) === 'k1,k0', J([T0.daftar.map(function (x) { return [x.id, x.urut]; }), kunci(Tz.daftar)]));
  cek('obrolan tablet: pesan akun ini + balasan owner (pesan akun lain tidak ikut)', kunci(T0.obrolan) === 'p0,p1,p0-balas' && T0.obrolan.every(function (x) { return x.id !== 'x9'; }), kunci(T0.obrolan));
  cek('lonceng tablet: angka = putusan belum dibuka (Kabar) + balasan / pesan owner belum dibuka (Obrolan)', T0.nKabar === 1 && T0.nObrolan === 1 && T0.n === 2, J([T0.nKabar, T0.nObrolan]));
  var k0 = T0.daftar.find(function (x) { return x.id === 'k0'; });
  cek('lonceng tablet: alasan tolak ikut, judul menyebut putusannya', k0.alasan === 'Belum perlu' && /DITOLAK/.test(k0.judul), J(k0));
  var Tk = kbLonceng(TB, D, kbTandai(T0, 'kabar'), HI), To = kbLonceng(TB, D, kbTandai(T0, 'obrolan'), HI), Tb = kbLonceng(TB, D, kbTandai(T0), HI);
  cek('tablet: tab yang DILIHAT saja yang jadi sudah dibuka (Kabar ≠ Obrolan); keduanya = nol', Tk.nKabar === 0 && Tk.nObrolan === 1 && To.nKabar === 1 && To.nObrolan === 0 && Tb.n === 0, J([Tk.nKabar, Tk.nObrolan, To.nKabar, To.nObrolan, Tb.n]));
  var Tko = kbLonceng(TB, D, kbTandai(Tk, 'obrolan'), HI);
  cek('tablet: buka Kabar lalu Obrolan → catatan Kabar tidak hilang', Tko.n === 0, Tko.n);
  var T1b = kbLonceng(TB, D, kbTandai(T0), HI); var D3 = D.map(function (m) { return m.id === 'k1' ? Object.assign({}, m, { status: 'disetujui', diputusTanggal: '2026-11-23', diputusJam: '14:00' }) : m; });
  var T2 = kbLonceng(TB, D3, kbTandai(T0), HI);
  cek('lonceng tablet: owner menyetujui titipan sesudah dibuka → angka 1 (status berubah = kabar baru)', T1b.n === 0 && T2.n === 1 && T2.daftar[0].id === 'k1' && /disetujui/.test(T2.daftar[0].judul), J([T1b.n, T2.n, T2.daftar[0]]));
  var Tc = kbLonceng(TB, Db, kbTandai(T0), HI);
  cek('tablet: pesannya dibaca owner tanpa balasan → centang dua, BUKAN angka baru', Tc.n === 0 && Tc.obrolan.find(function (x) { return x.kunci === 'p1'; }).centang === 2, J([Tc.n, Tc.obrolan]));
  var teks = kbTulisLihat(null, 'uid-owner', { a: 'menunggu' }); teks = kbTulisLihat(teks, 'uid-tablet', { b: 'dibaca' });
  cek('peta "sudah dibuka" per akun: akun lain di perangkat yang sama tidak tertimpa', J(kbBacaLihat(teks, 'uid-owner')) === J({ a: 'menunggu' }) && J(kbBacaLihat(teks, 'uid-tablet')) === J({ b: 'dibaca' }) && kbBacaLihat(teks, 'uid-baru') === null && kbBacaLihat('rusak{', 'x') === null);
  var banyak = []; for (var i = 0; i < 40; i++) banyak.push({ id: 'm' + i, tindakan: 'uangKeluar', status: 'menunggu', jenis: 'toko', teks: 'p' + i, nominal: 1000, mintaUid: 'u', tanggal: '2026-11-23', jam: String(10 + (i % 10)) + ':' + String(10 + i) });
  var LB = kbLonceng(OW, banyak, {}, HI); cek('lonceng Kabar: paling banyak 30 baris, sisanya disebut, angka dari SEMUA', LB.daftar.length === 30 && LB.lebih === 10 && LB.n === 40, J([LB.daftar.length, LB.lebih, LB.n]));
  var bp = []; for (var j = 0; j < 90; j++) bp.push({ id: 'q' + j, tindakan: 'pesan', status: 'menunggu', teks: 'p' + j, mintaUid: 'u', tanggal: '2026-11-23', jam: '10:' + String(10 + (j % 50)), pada: '2026-11-23T03:00:' + String(10 + (j % 50)) + '.' + String(100 + j) + 'Z' });
  var LP = kbLonceng(OW, bp, {}, HI);
  cek('obrolan: paling banyak 80 gelembung terbaru, sisanya disebut, angka dari SEMUA', LP.obrolan.length === 80 && LP.lebihObrolan === 10 && LP.nObrolan === 90 && LP.belumDibaca.length === 90, J([LP.obrolan.length, LP.lebihObrolan, LP.nObrolan]));
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
  cek('push tablet: pesan dibaca TANPA balasan (owner membuka obrolan) → tidak ada notifikasi, cukup centang dua; kabar barang masuk tetap dikabarkan',
    P.pesanPutus({ status: 'menunggu', tindakan: 'pesan', teks: 'Lampu', mintaUid: 'u' }, { status: 'dibaca', tindakan: 'pesan', teks: 'Lampu', balasan: '', mintaUid: 'u' }, 'q') === null
    && !!P.pesanPutus({ status: 'menunggu', tindakan: 'barangMasuk', teks: 'Datang', mintaUid: 'u' }, { status: 'dibaca', tindakan: 'barangMasuk', teks: 'Datang', balasan: '', mintaUid: 'u' }, 'b'));
  var k = P.kirimanTablet(a, ['t1', 't2']);
  cek('push tablet: kiriman = notifikasi Android saluran "kabar", prioritas tinggi, data layar teks', J(k.tokens) === J(['t1', 't2']) && k.notification.title === a.judul && k.android.priority === 'high' && k.android.notification.channelId === 'kabar' && k.data.layar === 'menu' && typeof k.data.tag === 'string', J(k));
  var pj = P.pesanPutus({ status: 'menunggu', tindakan: 'pesan', mintaUid: 'u' }, { status: 'dibaca', tindakan: 'pesan', teks: 'z'.repeat(300), balasan: 'y'.repeat(150), mintaUid: 'u' }, 'q');
  cek('push tablet: isi dipendekkan (layar kunci)', pj.isi.length <= P.BATAS_ISI, pj.isi.length);
  // ---- pesan owner KE tablet (owner 23 Nov 2026)
  var W = { tanggal: '2026-11-23', jam: '15:00', kini: '2026-11-23T08:00:00.000Z', idUnik: function () { return 'po1'; } };
  var S1 = kbSusunPesanOwner('  Tolong   cek stok 5 kg  ', W, OW); var dPO = S1.dokumen && S1.dokumen[0].data;
  cek('pesan owner: satu dokumen persetujuan pesanOwner, status terkirim (bukan menunggu), teks dirapikan, untuk tablet', S1.dokumen && S1.dokumen.length === 1 && S1.dokumen[0].koleksi === 'persetujuan'
    && dPO.tindakan === 'pesanOwner' && dPO.status === 'terkirim' && dPO.teks === 'Tolong cek stok 5 kg' && dPO.untuk === 'tablet' && dPO.tanggal === '2026-11-23' && dPO.jam === '15:00', J(S1));
  cek('pesan owner: kosong / lebih dari 500 huruf / bukan akun owner DITOLAK', !!kbSusunPesanOwner('   ', W, OW).tolak && !!kbSusunPesanOwner('x'.repeat(501), W, OW).tolak && !!kbSusunPesanOwner('halo', W, TB).tolak && !kbSusunPesanOwner('x'.repeat(500), W, OW).tolak);
  cek('pesan owner: baris baru dipertahankan (obrolan), spasi & baris kosong berlebih dirapikan', kbSusunPesanOwner('baris  satu \n\n\n\n baris dua', W, OW).dokumen[0].data.teks === 'baris satu\n\nbaris dua');
  var DP = D.concat([dPO]);
  var LO = kbLonceng(OW, DP, kbTandai(L1), HI);
  cek('lonceng owner: pesan owner TIDAK dihitung & tidak di Kabar; tampil di Obrolan sebagai gelembung sendiri (✓)', LO.nKabar === 0 && LO.menunggu === 1 && LO.daftar.every(function (x) { return x.id !== 'po1'; })
    && LO.obrolan.some(function (x) { return x.id === 'po1' && x.dari === 'owner' && !x.baru && x.centang === 1; }), J([LO.nKabar, LO.menunggu, LO.obrolan]));
  var LT = kbLonceng(TB, DP, kbTandai(T0), HI); var ujung = LT.obrolan[LT.obrolan.length - 1];
  cek('obrolan tablet: pesan owner = baru (angka 1, ujung utas, dari owner)', LT.n === 1 && LT.nObrolan === 1 && ujung.id === 'po1' && ujung.dari === 'owner' && ujung.baru === true && ujung.teks === 'Tolong cek stok 5 kg', J([LT.n, ujung]));
  cek('obrolan tablet: sesudah Obrolan dibuka angka nol', kbLonceng(TB, DP, kbTandai(LT, 'obrolan'), HI).n === 0);
  var LK = kbLonceng({ jenis: 'staf', uid: 'uid-lain', peran: 'karyawan' }, DP, {}, HI);
  cek('akun tablet lain (karyawan) juga menerima pesan owner di obrolannya (tanpa pesan milik akun lain)', LK.obrolan.some(function (x) { return x.id === 'po1'; }) && LK.obrolan.every(function (x) { return x.id !== 'p1'; }), kunci(LK.obrolan));
  var sTB0 = kbSidik(TB, D), sTB1 = kbSidik(TB, DP); var evT = kbBanding(sTB0, sTB1);
  cek('kabar dalam aplikasi: tablet berbunyi "Pesan dari owner" saat pesan owner datang', evT.length === 1 && evT[0].judul === 'Pesan dari owner' && evT[0].isi === 'Tolong cek stok 5 kg', J(evT));
  var evR = kbBanding(kbSidik(TB, D), kbSidik(TB, Db)); var Dr = D.map(function (m) { return m.id === 'p1' ? Object.assign({}, m, { status: 'dibaca', balasan: 'Oke', diputusTanggal: HI, diputusJam: '09:05' }) : m; });
  var evR2 = kbBanding(kbSidik(TB, D), kbSidik(TB, Dr));
  cek('kabar dalam aplikasi: pesan tablet dibaca TANPA balasan → tablet tidak berbunyi (centang dua saja); dengan balasan tetap berbunyi', evR.length === 0 && evR2.length === 1 && /dibaca owner/.test(evR2[0].judul), J([evR, evR2]));
  var evO = kbBanding(kbSidik(OW, D), kbSidik(OW, DP));
  cek('kabar dalam aplikasi: owner yang menulis TIDAK berbunyi untuk pesannya sendiri', evO.length === 0, J(evO));
  var pp = P.pesanDariOwner(dPO, 'po1');
  cek('push dari owner: judul "Pesan dari owner", isi teks, tag owner-id, ke semua tablet (untukUid kosong)', pp && pp.judul === 'Pesan dari owner' && pp.isi === 'Tolong cek stok 5 kg' && pp.tag === 'owner-po1' && pp.untukUid === '' && pp.layar === 'menu', J(pp));
  cek('push dari owner: bukan pesan owner / kosong = tidak dikirim; HP owner tidak dikabari pesannya sendiri', P.pesanDariOwner({ tindakan: 'pesan', teks: 'x' }, 'a') === null && P.pesanDariOwner({ tindakan: 'pesanOwner', teks: '  ' }, 'a') === null
    && P.pesanNotif(Object.assign({}, dPO, { status: 'menunggu' }), 'po1') === null);
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


_IKON = {}   # hasil ikon_m.semua() per teks sumbernya (±3 detik sekali; kontrol yang tidak mengubah ikon_m.py memakai ulang)


def ikon_dari(teks):
    if teks not in _IKON:
        r = {'__name__': 'ikon_uji', '__file__': os.path.join(AKAR, IKM)}; exec(compile(teks, IKM, 'exec'), r); _IKON[teks] = (r['semua'](), r)
    return _IKON[teks]


def piksel_alfa(png, x, y):
    """Alfa satu piksel PNG RGBA 8-bit tanpa interlace yang ditulis ikon_m.png() (filter 0 tiap baris)."""
    import struct, zlib
    w = struct.unpack('>I', png[16:20])[0]; i = 8; idat = b''
    while i < len(png):
        n = struct.unpack('>I', png[i:i + 4])[0]; jenis = png[i + 4:i + 8]
        if jenis == b'IDAT': idat += png[i + 8:i + 8 + n]
        i += 12 + n
    d = zlib.decompress(idat); baris = 1 + w * 4
    return d[y * baris + 1 + x * 4 + 3]


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
    # ---- logo M (owner 23 Nov 2026: "ikon logo aplikasi gak rapi di tablet … ganti logo" → "logo M aja gak perlu IQ")
    hasil, ikm = ikon_dari(t[IKM])
    beda = [n for n, b in hasil.items() if not os.path.exists(os.path.join(AKAR, n)) or open(os.path.join(AKAR, n), 'rb').read() != b]
    ok('logo M: icon-sistem.svg + PNG 512/192/180/32 + latar depan APK = hasil apk/ikon_m.py (satu sumber geometri)', not beda, beda)
    dp = hasil['apk/ikon-depan-432.png']
    ok('logo M: latar depan ikon adaptif TRANSPARAN di luar simbol (bukan kotak), cincin emas di dalam lingkar aman 66/108', piksel_alfa(dp, 0, 0) == 0 and piksel_alfa(dp, 431, 431) == 0
       and piksel_alfa(dp, 216 + 125, 216) > 0 and 125 * 2 / 432 < 66 / 108, [piksel_alfa(dp, 0, 0), piksel_alfa(dp, 341, 216)])
    ok('logo M: tanpa tulisan "IQ" / "BERAS" di ikon', 'IQ' not in hasil['icon-sistem.svg'].decode('utf-8') and 'BERAS' not in hasil['icon-sistem.svg'].decode('utf-8') and '<text' not in hasil['icon-sistem.svg'].decode('utf-8'))
    ok('logo M: pasang.py — latar depan = apk/ikon-depan-432.png, latar belakang = LATAR_IKON hitam malam (sama dengan ikon_m.LATAR_APK), ikon bulat dipotong lingkaran',
       "if os.path.exists(p): depan.resize(Image.open(p).size, Image.LANCZOS).save(p)" in t[PAS] and ruang.get('LATAR_IKON') == ikm['LATAR_APK'] and "re.sub(r'#[0-9A-Fa-f]{6,8}', LATAR_IKON, baca(latar))" in t[PAS]
       and "if os.path.exists(p): bulat(n).save(p)" in t[PAS])
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
        ok('lonceng di kepala layar %s, tepat sebelum pil akun (disuntik app.js lewat opsi.lonceng)' % n, ('${opsi.lonceng ? mentah(opsi.lonceng()) : \'\'}<div class="pil pil-akun' in s) if n != 'ringkasan' else ('${opsi.lonceng ? opsi.lonceng() : \'\'}<div class="pil pil-akun" id="rkPil"' in s))
    ok('lonceng: app.js menyuntik ikon ke kedelapan layar', A.count('lonceng: pintuLonceng,') == 8)
    ok('lonceng: lembarnya ada di halaman & tersembunyi saat terkunci', 'id="lembarLonceng" class="lembar-lonceng kartu"' in I and 'body.terkunci .lembar-lonceng { display: none !important; }' in K and '.lembar-lonceng[hidden] { display: none; }' in K)
    ok('lonceng: bergoyang saat kabar baru, angka meletup', '.lonceng.goyang svg { animation: loncengGoyang' in K and '.lonceng-n.letup { animation: loncengLetup' in K)
    L = t[LC]
    ok('lonceng: balas lewat pintu yang SAMA dengan Uang (tpSusunPutus dibaca), hanya akun owner', "tpSusunPutus(id, 'dibaca', { balasan: _lcBalas[id] || '' }" in L and "async function lcTandaiBaca(id) {\n  if (!_lcAkun || _lcAkun.jenis !== 'owner' || _lcSibuk) return;" in L and "owner && x.bisaBalas ?" in L)
    ok('lonceng: dihitung ulang tiap data berubah (app.js periksaKabarBaru)', 'loncengSegarkan(' in A and 'pasangLonceng({ pindah: (t) => pindah(t)' in A)
    # ---- push sisi server & rules
    F = t[FIX]
    ok('fungsi kabarTablet: pemicu UBAH persetujuan, token notifPerangkat milik uid peminta, token kosong dilewati', "exports.kabarTablet = onDocumentUpdated('persetujuan/{id}'" in F and ".collection('notifPerangkat').where('uid', '==', p.uid)" in F and "typeof x.token === 'string' && x.token" in F)
    ok('obrolan: satu kotak ketik di lonceng — owner menulis lewat kbSusunPesanOwner, akun tablet lewat tpSusunPesan (pintu yang sama dengan Menu)', "const r = _lcAkun.jenis === 'owner' ? kbSusunPesanOwner(_lcTulis, w, _lcAkun) : tpSusunPesan(_lcTulis, _lcAkun, w);" in L and 'data-ll="kirim"' in L and 'data-ll-tulis="1"' in L)
    ok('obrolan: owner membuka tab Obrolan = pesan tablet yang menunggu ditandai dibaca TANPA balasan, satu kiriman, tiap id sekali per pembukaan', "if (_lcTab === 'obrolan' && _lcIsi.owner && !document.hidden) lcBacaSemua();" in L and "tpSusunPutus(id, 'dibaca', { balasan: '' }, w)" in L and "_lcIsi.belumDibaca.filter((id) => !_lcMenandai.has(id))" in L and 'const x = await tulisDokumen(dok);' in L)
    ok('obrolan: tab Obrolan | Kabar, gelembung kiri-kanan, centang, label hari, gelembung & penanda tab beranimasi', 'data-ll="tab" data-tab="${k}"' in L and "${x.centang === 2 ? '✓✓' : '✓'}" in L and '.lo-gel.saya {' in K and '.lo-gel.dia {' in K and 'animation: masukGel' in K and 'transform: translateX(calc(var(--x, 0) * 100%)); transition: transform' in K and '.lo-hari {' in K)
    ok('obrolan: Enter = kirim hanya dengan papan ketik fisik (layar sentuh: baris baru), kotak ketik ikut tinggi tulisannya', "fisik = matchMedia('(pointer: fine)').matches;" in L and 'if (fisik) { ev.preventDefault(); lcKirim(); }' in L and 'const lcTinggi = (k) =>' in L)
    ok('pesan owner: papan Persetujuan tidak memuat pesan owner', "cacheMentah('persetujuan').filter((m) => m && m.tindakan !== 'pesanOwner')" in t[SIS])
    ok('fungsi kabarDariOwner: pemicu BUAT persetujuan, token notifPerangkat (semua / satu akun), token kosong dilewati', "exports.kabarDariOwner = onDocumentCreated('persetujuan/{id}'" in F and "(p.untukUid ? kol.where('uid', '==', p.untukUid) : kol)" in F)
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
    ('segarkan selalu menulis', [(NT, "  if (lama.ujung === ntUjung(t.token)) return { ok: true, sama: true };\n", "")]),
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
    ('lonceng hilang dari kepala Stok', [('baru/js/layar/stok.js', "${opsi.lonceng ? mentah(opsi.lonceng()) : ''}<div class=\"pil pil-akun", '<div class="pil pil-akun')]),
    ('app.js lupa menyuntik lonceng ke Uang', [(APP, "pasangLayarUang(document.getElementById('layarUang'), { lonceng: pintuLonceng,", "pasangLayarUang(document.getElementById('layarUang'), {")]),
    ('karyawan tablet boleh membalas dari lonceng', [(LC, "async function lcTandaiBaca(id) {\n  if (!_lcAkun || _lcAkun.jenis !== 'owner' || _lcSibuk) return;", "async function lcTandaiBaca(id) {\n  if (!_lcAkun || _lcSibuk) return;")]),
    ('pesan owner berstatus menunggu (masuk daftar menunggu owner)', [(KBL, "tindakan: KB_PESAN_OWNER, status: KB_STATUS_TERKIRIM,", "tindakan: KB_PESAN_OWNER, status: 'menunggu',")]),
    ('obrolan tablet tidak memuat pesan owner', [(KBL, "      ob.push(gelembung({ id, dari: 'owner', nama: 'Owner', teks: m.teks,", "      if (owner) ob.push(gelembung({ id, dari: 'owner', nama: 'Owner', teks: m.teks,")]),
    ('obrolan tablet memuat pesan akun lain', [(KBL, "      if (!owner && (!uid || uidPeminta(m) !== uid)) return;\n", "")]),
    ('obrolan owner: belum dibaca dari peta perangkat (bukan keadaan server)', [(KBL, "centang: st === 'menunggu' ? 1 : 2, baru: owner && st === 'menunggu' }));", "centang: st === 'menunggu' ? 1 : 2, baru: owner && L[id] !== st }));")]),
    ('balasan lama hilang dari obrolan', [(KBL, "      if (bal && st !== 'menunggu') ob.push(", "      if (false) ob.push(")]),
    ('membuka satu tab menandai kedua tab', [(KBL, "  if (bagian !== 'obrolan') Object.assign(out, kab);", "  Object.assign(out, kab);")]),
    ('obrolan tanpa label hari', [(KBL, "x.pisah = !s || s.tanggal !== x.tanggal ? kbLabelHari(x.tanggal, hariIni) : '';", "x.pisah = '';")]),
    ('obrolan tanpa batas gelembung', [(KBL, "  const utas = ob.slice(Math.max(0, ob.length - KB_MAKS_OBROLAN));", "  const utas = ob;")]),
    ('push tablet saat owner sekadar membuka obrolan', [(PSN, "  if (t === 'pesan' && st === 'dibaca' && !teks(sesudah.balasan)) return null;\n", "")]),
    ('tablet berbunyi untuk centang dua', [(KBL, "\n    && !(baru.milik[id].tindakan === TP_PESAN && baru.milik[id].status === 'dibaca' && !baru.milik[id].balasan)", "")]),
    ('owner membuka obrolan tidak menandai dibaca', [(LC, "  if (_lcTab === 'obrolan' && _lcIsi.owner && !document.hidden) lcBacaSemua();\n", "")]),
    ('pesan owner meratakan baris baru', [(KBL, ".replace(/[ \\t\\f\\v]+/g, ' ')", ".replace(/\\s+/g, ' ')")]),
    ('kabar dalam aplikasi diam saat pesan owner datang', [(KBL, "  return pesan.concat(putus);", "  return putus;")]),
    ('tablet menulis pesan owner dari obrolan', [(LC, "_lcAkun.jenis === 'owner' ? kbSusunPesanOwner(_lcTulis, w, _lcAkun) : tpSusunPesan(_lcTulis, _lcAkun, w)", "kbSusunPesanOwner(_lcTulis, w, _lcAkun)")]),
    ('pesan owner tanpa batas panjang', [(KBL, "  if (isi.length > TP_BATAS.pesan) return { tolak:", "  if (false) return { tolak:")]),
    ('push dari owner tanpa isi', [(PSN, "  const isi = teks(d.teks); if (!isi) return null;\n  return { judul: 'Pesan dari owner'", "  const isi = teks(d.teks);\n  return { judul: 'Pesan dari owner'")]),
    ('HP owner dikabari pesannya sendiri', [(PSN, "  if (d.tindakan === 'pesanOwner') return null;", "")]),
    ('papan Persetujuan memuat pesan owner', [(SIS, ".filter((m) => m && m.tindakan !== 'pesanOwner')", "")]),
    ('latar depan ikon adaptif kembali ikon 512 berkotak', [(PAS, "if os.path.exists(p): depan.resize(Image.open(p).size, Image.LANCZOS).save(p)", "if os.path.exists(p): sumber.resize(Image.open(p).size, Image.LANCZOS).save(p)")]),
    ('latar belakang ikon adaptif kembali terang', [(PAS, "LATAR_IKON = '#101314'", "LATAR_IKON = '#E2E7EC'")]),
    ('geometri logo diubah tanpa membuat ulang PNG', [(IKM, "def susun(ukuran, cincin=True, skala_m=1.12,", "def susun(ukuran, cincin=True, skala_m=1.2,")]),
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
