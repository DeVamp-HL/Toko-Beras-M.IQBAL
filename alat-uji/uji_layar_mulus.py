#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_layar_mulus.py — owner 3 Okt 2026 "masih ada lag atau patah-patah" (layar SELAIN Jual; Jual sudah dipercepat #100/#102).
Diukur 7 Okt atas cadangan toko: satu angka yang sama dihitung ratusan kali per gambar (ambilPenjualan sampai 936×, buku stok mesin sampai 927×,
petaBukuWadah 3.366×). Obatnya INGATAN per versi cache (toko.js ingatPerVersi — pola rakUntukChip Jual) + hitung sekali per gambar (Tempat simpan) +
yang tidak tampil tidak dihitung (Dasbor ganti rentang = tren saja; denyut HP tidak membasikan dasbor; Menu dibuka tanpa data baru tidak digambar ulang).
TUJUH LAYAR ASLI (Ringkasan, Stok, Pelanggan, Menu, Harga, Uang, Laporan) dijalankan di jsc lewat pemuat modul ES (alat-uji/modul_es.py, lingkup modul utuh,
'use strict'), DOM longgar & jam palsu; tiap aksi = buka, buka lagi, data berubah, NOTA BARU (isi penjualan berubah), TITIK KAS PERANGKAT berubah (tanpa versi
cache naik), tiap tab & sub-tab, ketik di tiap kolom, ketuk tombol yang tidak menulis.
  · KESETARAAN: seluruh rangkaian dijalankan TANPA ingatan (setelIngatan mati — tiap panggilan dihitung ulang) dan DENGAN ingatan → semua yang digambar
    (tiap innerHTML / pasang, berurutan) byte-sama per aksi, dan urutan aksinya sama.
  · BEKU: hasil ingatan dibekukan dalam-dalam (Object.freeze) → modul ES strict MELEMPAR bila ada pemanggil yang mengubah hasil bersama (sort / push /
    assign di tempat); rangkaian tanpa galat dan gambarnya tetap sama.
  · FUNGSI (hasil sebelum vs sesudah): tiap fungsi yang diingat = hitung ulang penuh (mesin langsung / tanpaIngatan), byte-sama — awal, sesudah nota baru,
    di dalam & sesudah cache sementara, sesudah titik kas perangkat berubah, dan melewati pergantian hari & bulan.
  · ORAKEL DASBOR: tiap sesudah aksi Dasbor, isinya = Ringkasan yang baru dipasang (hitung segar) — ganti rentang & denyut HP tidak meninggalkan kartu basi.
  · KUNCI LUAR (sanggahan 7 Okt): yang digambar tetapi TIDAK menaikkan versi data — jam 12 siang (hari tutup aktif), hari, pita jam Menu, jam Pelanggan, menit
    Sistem › Perangkat, titik kas perangkat, tahun baru. Dasbor (detak menit, denyut HP, jejak, ganti rentang), Menu, Stok › Wadah literan & Gudang, Uang ›
    Tutup hari / Pindah uang / Tutup buku, Harga › Bon pemasok & Belanja, Laporan › Harian & Neraca, Pelanggan › Kenali yang dibuka lagi TANPA data baru =
    gambar segar saat itu juga; tiap kasus wajib TAJAM (gambar segar memang berubah). Indeks cincin dibangun ulang saat tahun berganti tanpa data baru.
  · ONGKOS (hitungan panggilan, pasti): Tempat simpan menyusun rantai stok sekali per gambar; ketukan Katalog harga tanpa data baru tidak menghitung buku stok;
    ganti rentang Dasbor tidak menghitung stok; denyut HP tidak menyusun dasbor; Menu dibuka lagi tanpa data baru tidak digambar; Laporan › Bulanan tidak
    menghitung omzet 12 bulan ulang; ketukan Uang tidak menyusun gerakan kas ulang.
  · KOTAK PASIR = gabungan kotak uji_rak_inkremental (wadah, katalog, adukan, penjualan) + kotak dasbor uji_ringkasan_baru (biaya, piutang, modal) + titik kas,
    tempat simpan, aturan pajak — ANGKA CONTOH, bukan angka toko. Jam dikunci 21 Sep 2026 10:00 WIB.
  · Cadangan toko (lokal saja, dilewati di CI): `--cadangan <berkas>` atau _privat/backup-batch-*.json → kesetaraan + fungsi + orakel atas data toko, dan ms
    per aksi tanpa vs dengan ingatan (satu sampel, jam dinding preciseTime).

    python3 alat-uji/uji_layar_mulus.py [--cadangan JALUR]   → N lulus · 0 gagal
    python3 alat-uji/uji_layar_mulus.py --kontrol            → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, sys, json, subprocess, tempfile, glob, re
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import modul_es  # noqa: E402

JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
LAYAR = ['baru/js/layar/%s.js' % n for n in ['ringkasan', 'stok', 'pelanggan', 'menu', 'harga', 'uang', 'laporan']]
JAM = '2026-09-21T03:00:00.000Z'   # 21 Sep 2026 10:00 WIB

# ---------------------------------------------------------------- lingkungan jsc: jam palsu, DOM longgar, localStorage dalam memori
LINGKUNGAN = r"""
var __KINI = 0;
var __DateAsli = Date;
class __DateTetap extends __DateAsli { constructor(...a) { if (a.length) super(...a); else super(__KINI); } static now() { return __KINI; } }
Date = __DateTetap;
var __benih = 12345; Math.random = function () { __benih = (Math.imul(__benih, 1103515245) + 12345) | 0; return ((__benih >>> 8) & 0xffffff) / 0x1000000; };
var __galat = [];
var console = { log: function () {}, warn: function () {}, info: function () {}, error: function () { var a = Array.prototype.slice.call(arguments).map(function (x) { return x && x.stack ? String(x.message || x) + ' @ ' + String(x.stack).split('\n')[0] : String(x); }); __galat.push(a.join(' ').slice(0, 300)); } };
var __ls = {};
var localStorage = { getItem: function (k) { return Object.prototype.hasOwnProperty.call(__ls, k) ? __ls[k] : null; }, setItem: function (k, v) { __ls[k] = String(v); },
  removeItem: function (k) { delete __ls[k]; }, key: function (i) { return Object.keys(__ls)[i] || null; }, get length() { return Object.keys(__ls).length; } };
var __jam = 0, __timer = [], __raf = [], __nomor = 1, __mikro = [], __interval = [];
function setTimeout(f, ms) { var id = __nomor++; __timer.push({ id: id, at: __jam + (ms || 0), f: f }); return id; }
function clearTimeout(id) { for (var i = 0; i < __timer.length; i++) if (__timer[i].id === id) { __timer.splice(i, 1); return; } }
function setInterval(f, ms) { __interval.push(f); return __nomor++; }
function clearInterval() {}
function requestAnimationFrame(f) { __raf.push(f); return __raf.length; }
function cancelAnimationFrame() {}
function queueMicrotask(f) { __mikro.push(f); }
var performance = { now: function () { return __jam; } };
function __kurasMikro() { var n = 0; while (__mikro.length && n < 10000) { var f = __mikro.shift(); n++; try { f(); } catch (e) { console.error('mikro', e); } } if (typeof drainMicrotasks === 'function') drainMicrotasks(); }
function __jalanTimer(batas) { __timer.sort(function (a, b) { return a.at - b.at; }); while (__timer.length && __timer[0].at <= batas) { var t = __timer.shift(); try { t.f(); } catch (e) { console.error('timer', e); } __kurasMikro(); } }
function __bingkai() { var r = __raf; __raf = []; __jam += 16; r.forEach(function (f) { try { f(__jam); } catch (e) { console.error('raf', e); } }); __kurasMikro(); __jalanTimer(__jam); }
function __Kelas() { this.s = {}; }
__Kelas.prototype = { add: function (k) { this.s[k] = 1; }, remove: function (k) { delete this.s[k]; }, toggle: function (k, ya) { if (ya === undefined ? !this.s[k] : ya) this.s[k] = 1; else delete this.s[k]; return !!this.s[k]; }, contains: function (k) { return !!this.s[k]; } };
// tiap innerHTML / pasang dicatat berurutan: sidik aksi = gabungan SEMUA yang digambar (bukan cuma yang terakhir)
var __gb = { n: 0, sidik: 0, bytes: 0 };
function __catatGambar(s) { __gb.n += 1; __gb.bytes += s.length; var h = __gb.sidik; for (var q = 0; q < s.length; q++) h = (Math.imul(h, 31) + s.charCodeAt(q)) | 0; __gb.sidik = (Math.imul(h, 131) + 7) | 0; }
function __El(tag) { this.tagName = String(tag || 'div').toUpperCase(); this.nodeName = this.tagName; this.nodeType = 1; this.dataset = {}; this.style = { setProperty: function () {}, removeProperty: function () {} }; this.classList = new __Kelas();
  this.__dengar = {}; this.__ids = {}; this.__html = ''; this.children = []; this.childNodes = []; this.hidden = false; this.value = ''; this.firstElementChild = null; this.textContent = ''; this.__attr = {}; this.id = ''; }
function __cariId(el, id) {
  if (el.__ids[id]) return el.__ids[id];
  if (el.__html && el.__html.indexOf('id="' + id + '"') >= 0) { var x = new __El(); x.id = id; el.__ids[id] = x; return x; }
  var k = Object.keys(el.__ids); for (var i = 0; i < k.length; i++) { var r = __cariId(el.__ids[k[i]], id); if (r) return r; }
  return null;
}
__El.prototype = {
  addEventListener: function (t, f) { (this.__dengar[t] = this.__dengar[t] || []).push(f); }, removeEventListener: function () {}, dispatchEvent: function () { return true; },
  querySelector: function (sel) { var m = /^#([\w-]+)$/.exec(sel); return m ? __cariId(this, m[1]) : null; }, querySelectorAll: function () { return []; },
  getBoundingClientRect: function () { return { left: 0, top: 0, right: 320, bottom: 200, width: 320, height: 200, x: 0, y: 0 }; },
  appendChild: function (c) { this.children.push(c); return c; }, append: function () {}, prepend: function () {}, insertBefore: function (c) { return c; }, removeChild: function (c) { return c; }, remove: function () {},
  setAttribute: function (k, v) { this.__attr[k] = String(v); }, getAttribute: function (k) { return k in this.__attr ? this.__attr[k] : null; }, removeAttribute: function (k) { delete this.__attr[k]; }, hasAttribute: function (k) { return k in this.__attr; },
  scrollIntoView: function () {}, scrollTo: function () {}, focus: function () {}, blur: function () {}, select: function () {}, click: function () {}, setSelectionRange: function () {},
  closest: function () { return null; }, matches: function () { return false; }, contains: function () { return true; },
  animate: function () { return { onfinish: null, cancel: function () {}, finish: function () {}, finished: Promise.resolve() }; },
  get offsetWidth() { return 320; }, get offsetHeight() { return 200; }, get offsetParent() { return null; }, get scrollHeight() { return 200; }, get clientHeight() { return 200; },
};
Object.defineProperty(__El.prototype, 'innerHTML', { get: function () { return this.__html; }, set: function (v) { this.__html = String(v); this.__ids = {}; this.firstElementChild = this.__html ? {} : null; __catatGambar(this.__html); } });
var document = { hidden: false, body: new __El('body'), documentElement: new __El('html'), activeElement: null, visibilityState: 'visible',
  getElementById: function () { return null; }, querySelector: function () { return null; }, querySelectorAll: function () { return []; },
  createElement: function (t) { return new __El(t); }, createElementNS: function (ns, t) { return new __El(t); }, createTextNode: function () { return new __El('#text'); },
  addEventListener: function () {}, removeEventListener: function () {} };
var window = this; var self = this;
var innerWidth = 1280, innerHeight = 800, devicePixelRatio = 2;
function matchMedia() { return { matches: false, addEventListener: function () {}, removeEventListener: function () {}, addListener: function () {} }; }
function getComputedStyle() { return { getPropertyValue: function () { return ''; } }; }
function addEventListener() {} function removeEventListener() {} function scrollTo() {}
var open = function () { return null; };
var navigator = { onLine: true, userAgent: 'jsc', storage: { estimate: function () { return Promise.resolve({ usage: 0, quota: 0 }); }, persisted: function () { return Promise.resolve(false); }, persist: function () { return Promise.resolve(false); } }, clipboard: { writeText: function () { return Promise.resolve(); } } };
function CustomEvent(t, o) { this.type = t; this.detail = o && o.detail; }
var location = { href: 'https://contoh.invalid/baru/', search: '', hash: '', pathname: '/baru/' };
var URL = { createObjectURL: function () { return 'blob:x'; }, revokeObjectURL: function () {} };
function Blob() {}
"""

# ---------------------------------------------------------------- pemandu: pasang tujuh layar, jalankan rangkaian aksi, catat gambar & panggilan
PEMANDU = r"""
__KINI = new __DateAsli(JAM).getTime();
var DOM = __E['baru/js/inti/dom.js'], GR = __E['baru/js/inti/gerak.js'], AD = __E['baru/js/layar/adegan.js'], D = __E['baru/js/data/toko.js'], F = __E['baru/js/inti/format.js'];
DOM.pasang = function (akar, isi) { var s = isi && isi.__mentah ? isi.html : String(isi || ''); akar.__html = s; akar.__ids = {}; akar.firstElementChild = s ? {} : null; __catatGambar(s); };
DOM.delegasi = function (akar, p) { akar.__aksi = p; };
GR.gulirkan = function () {}; GR.sekali = function () {}; GR.terbangkan = function () {};
Object.keys(AD).forEach(function (k) { if (typeof AD[k] === 'function') AD[k] = function () { return 0; }; });
// pembeku dalam: objek & array yang terjangkau dari hasil ingatan (dokumen cache ikut — tidak ada yang boleh mengubahnya di tempat)
var bekukan = function (o) { if (!o || typeof o !== 'object' || Object.isFrozen(o)) return o; Object.freeze(o); Object.getOwnPropertyNames(o).forEach(function (k) { var v = o[k]; if (v && typeof v === 'object') bekukan(v); }); return o; };
if (MODE === 'mati') D.setelIngatan({ mati: true }); else if (MODE === 'beku') D.setelIngatan({ beku: bekukan });
// penghitung panggilan (lewat ekspor modul: memanggil dari modul lain; panggilan di dalam modul yang sama tidak terhitung)
var HITUNG = { 'baru/js/mesin/beku.js': ['hitungStokKarungPerMerk', 'hitungStokKemasan', 'hitungLabaRentang', 'kasPada'], 'baru/js/mesin/pembantu.js': ['daftarGerakanKas'],
  'baru/js/layar/wadah-bernama-logika.js': ['wbBagianMerk'], 'baru/js/layar/stok-logika.js': ['daftarBarang'], 'baru/js/layar/dasbor-logika.js': ['susunDasbor'],
  'baru/js/layar/ringkasan-logika.js': ['bangunIndeks'] };
var __n = {};
Object.keys(HITUNG).forEach(function (m) { HITUNG[m].forEach(function (f) { var asli = __E[m][f]; __E[m][f] = function () { __n[f] = (__n[f] || 0) + 1; return asli.apply(this, arguments); }; }); });
__sambungSemua();
__E['baru/js/inti/kunci.js'].setelKunci(false);

var HASIL = { aksi: [], fungsi: [], orakel: [], info: {} };
var AKUN = { jenis: 'owner', peran: 'owner', nama: 'Owner', uid: 'u-owner', email: 'owner@contoh.invalid' };
var __versi = 0;
Object.keys(CAD).forEach(function (n) { if (Array.isArray(CAD[n])) D.pasok(n, CAD[n]); });
if (CAD.petaJenisBeras) localStorage.setItem('miqbal_jenis_beras_v1', JSON.stringify(CAD.petaJenisBeras));
if (TITIK) localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify(TITIK));
D.setelSumber('firestore', '');
D.dengarkan(function () { __versi += 1; });
var PJ = __E['baru/js/layar/pajak-logika.js'], JL = __E['baru/js/layar/jual-logika.js'], M = __E['baru/js/mesin/beku.js'], MP = __E['baru/js/mesin/pembantu.js'];
var opsi = { akun: function () { return AKUN; }, gantiMode: function () {}, mode: function () { return 'gelap'; }, sekarang: function () { return null; }, statusRingkas: function () { return 'OWNER'; },
  pindah: function () {}, keTujuan: function () {}, versiData: function () { return __versi; }, keranjangJual: function () { return { keranjang: [], antrean: [], aktifId: null, sekarang: null }; },
  bukaHarga: function () {}, bukaStok: function () {}, bukaPelanggan: function () {}, bukaUang: function () {}, bukaLaporan: function () {}, bukaJual: function () {},
  periksaSambungan: function () { return Promise.resolve(true); }, setelLokasi: function () {}, namaiPerangkat: function () {}, antreLokal: function () { return { belum: [], ditolak: [] }; },
  buangDitolak: function () {}, tulisUlangDitolak: function () {} };
// Menu: app.js menghitung pengingat pajak di dalam lokal() tiap kali dipanggil (owner) — sama di sini
var opsiMenu = Object.assign({}, opsi, { lokal: function () { var p = []; try { p = PJ.pjSumberPengingat(new Date()); } catch (e) { console.error('pajak', e); }
  return { antre: [], idPerangkat: 'p-mac', namaPerangkat: 'Mac', pemegang: null, lokasi: null, koleksiSiap: 56, koleksiTotal: 56, offline: false, pajak: p }; } });
var opsiUang = Object.assign({}, opsi, { lokal: function () { return { antre: [], menunggu: 0, idPerangkat: 'p-mac', namaPerangkat: 'Mac', pemegang: null, offline: false, antreLokal: { belum: [], ditolak: [] }, parkir: [] }; } });

// ---- satu aksi: jalankan, kuras mikro, satu bingkai (jadwal: nanti/segera); sisa animasi di luar catatan
function __tuntas() { __kurasMikro(); __bingkai(); __kurasMikro(); }
function __sisa() { for (var i = 0; i < 120 && (__raf.length || __timer.length); i++) { if (__raf.length) __bingkai(); else { __jam += 50; __jalanTimer(__jam); } } __timer = []; __raf = []; }
var LAYAR_KINI = '';
function ukur(label, f, persiapan) {
  var g0 = __galat.length;
  if (persiapan) { try { persiapan(); } catch (e) { console.error('persiapan ' + label, e); } __tuntas(); __sisa(); }
  __gb = { n: 0, sidik: 0, bytes: 0 }; __n = {};
  var t0 = preciseTime();
  try { var r = f(); if (r && typeof r.then === 'function') r.then(null, function (e) { console.error('janji ' + label, e); }); } catch (e) { console.error('aksi ' + label, e); }
  __tuntas(); var ms = (preciseTime() - t0) * 1000;
  var rec = { layar: LAYAR_KINI, aksi: label, sidik: __gb.sidik, gambar: __gb.n, bytes: __gb.bytes, ms: Math.round(ms * 10) / 10, panggil: Object.assign({}, __n), galat: __galat.slice(g0).slice(0, 3) };
  __sisa(); HASIL.aksi.push(rec); return rec;
}

// ---- isi yang BERUBAH: nota baru (penjualan), titik kas perangkat (localStorage, tanpa versi cache), hari berganti
var __nNota = 0, __nTitik = 0;
function notaBaru() {
  var semua = D.cacheMentah('penjualan'); var c = semua.filter(function (p) { return p.jenis === 'karung' && !p.dibatalkan && !p.dikoreksiOleh && p.merkSumber; })[0] || semua[0];
  __nNota += 1; var iso = F.hariIniIso(new Date());
  var n = Object.assign({}, c, { id: 8100000000000 + __nNota, tanggal: iso, jam: '09:' + String(10 + __nNota % 40), grupNota: 'gUji' + __nNota, trxId: 'tUji' + __nNota, namaPelanggan: '', hargaTotal: (Number(c.hargaTotal) || 100000) + __nNota * 1000 });
  delete n.dibatalkan; delete n.dikoreksiOleh;
  D.pasok('penjualan', semua.concat([n]));
}
function titikBaru() { __nTitik += 1; localStorage.setItem('miqbal_titik_kas_v1', JSON.stringify({ tanggal: F.hariIniIso(new Date(Date.now() - 86400000)), laci: 1000000 + __nTitik * 25000, rekening: 200000, amplop: 0, brankas: 50000, diubahPada: '9999-12-31T00:00:00.000Z' })); }

// ---- FUNGSI: tiap fungsi yang diingat = hitung ulang penuh (mesin langsung / tanpaIngatan) — hasil sebelum vs sesudah, byte-sama
var J = JSON.stringify;
function bandingFungsi(tahap) {
  if (MODE === 'mati') return;
  var bulan = F.hariIniIso(new Date()).slice(0, 7), lalu = F.hariIniIso(new Date(Date.now() - 32 * 86400000)).slice(0, 7), kemarin = F.hariIniIso(new Date(Date.now() - 86400000));
  var sampaiLama = F.hariIniIso(new Date(Date.now() - 6 * 86400000));
  var mentah = function (f) { return D.tanpaIngatan(f); };
  var daftar = [
    ['ambilPenjualan', function () { return D.ambilPenjualan(); }, function () { return mentah(function () { return D.ambilPenjualanSemua().filter(MP.penjualanMasihBerlaku); }); }],
    ['ambilProduksiBerlaku', function () { return D.ambilProduksiBerlaku(); }, function () { return mentah(D.ambilProduksiBerlaku); }],
    ['ambilSemuaBatch', function () { return D.ambilSemuaBatch(); }, function () { return mentah(D.ambilSemuaBatch); }],
    ['petaBukuWadah', function () { return D.petaBukuWadah(); }, function () { return mentah(D.petaBukuWadah); }],
    ['ingatStokKarung() = hitungStokKarungPerMerk()', function () { return D.ingatStokKarung(); }, function () { return mentah(function () { return M.hitungStokKarungPerMerk(); }); }],
    ['ingatStokKarung(' + sampaiLama + ')', function () { return D.ingatStokKarung(sampaiLama); }, function () { return mentah(function () { return M.hitungStokKarungPerMerk(sampaiLama); }); }],
    ['ingatStokKemasan() = hitungStokKemasan()', function () { return D.ingatStokKemasan(); }, function () { return mentah(function () { return M.hitungStokKemasan(); }); }],
    ['ingatGerakanKas() = daftarGerakanKas()', function () { return D.ingatGerakanKas(); }, function () { return mentah(MP.daftarGerakanKas); }],
    ['ingatKasPada() = kasPada()', function () { return D.ingatKasPada(); }, function () { return mentah(function () { return M.kasPada(); }); }],
    ['ingatKasPada(kemarin)', function () { return D.ingatKasPada(kemarin); }, function () { return mentah(function () { return M.kasPada(kemarin); }); }],
    ['ingatNeraca() = hitungNeraca()', function () { return D.ingatNeraca(); }, function () { return mentah(function () { return M.hitungNeraca(); }); }],
    ['ingatNeraca(' + sampaiLama + ')', function () { return D.ingatNeraca(sampaiLama); }, function () { return mentah(function () { return M.hitungNeraca(sampaiLama); }); }],
    ['pjOmzetSistem(' + bulan + ')', function () { return PJ.pjOmzetSistem(bulan); }, function () { return mentah(function () { return PJ.pjOmzetSistem(bulan); }); }],
    ['pjOmzetSistem(' + lalu + ')', function () { return PJ.pjOmzetSistem(lalu); }, function () { return mentah(function () { return PJ.pjOmzetSistem(lalu); }); }],
    ['pjPotonganBulan(' + bulan + ')', function () { return PJ.pjPotonganBulan(bulan); }, function () { return mentah(function () { return PJ.pjPotonganBulan(bulan); }); }],
    ['pjTahun(tahun ini)', function () { return PJ.pjTahun(null, new Date()); }, function () { return mentah(function () { return PJ.pjTahun(null, new Date()); }); }],
  ];
  JL.aturWadah().daftar.forEach(function (W) { daftar.push(['karungUntukWadah(' + W + ')', function () { return JL.karungUntukWadah(W); }, function () { return mentah(function () { return JL.karungUntukWadah(W); }); }]); });
  daftar.forEach(function (x) {
    var a1, a2, b, e = '';
    try { a1 = J(x[1]()); a2 = J(x[1]()); b = J(x[2]()); } catch (er) { e = String(er && er.message || er); }
    HASIL.fungsi.push({ tahap: tahap, nama: x[0], sama: !e && a1 === b && a2 === b, galat: e, ada: !!b && b !== '{}' && b !== '[]' && b !== 'null', contoh: e || (a1 === b ? '' : String(a1).slice(0, 160) + ' ≠ ' + String(b).slice(0, 160)) });
  });
}
function rangkaianFungsi() {
  var n0 = D.ambilPenjualan().length; var kas0 = D.ingatKasPada();
  bandingFungsi('awal');
  notaBaru(); bandingFungsi('sesudah nota baru'); HASIL.info.notaMenambah = D.ambilPenjualan().length === n0 + 1;
  var nota = Object.assign({}, D.cacheMentah('penjualan')[0], { id: 8200000000000, grupNota: 'gUjiS', trxId: 'tUjiS', hargaTotal: 123000 }); delete nota.dibatalkan; delete nota.dikoreksiOleh;
  D.denganCacheSementara([{ koleksi: 'penjualan', data: nota }], function () { bandingFungsi('di dalam cache sementara'); });
  bandingFungsi('sesudah cache sementara');
  titikBaru(); bandingFungsi('sesudah titik kas perangkat berubah'); HASIL.info.titikMengubahKas = J(D.ingatKasPada()) !== J(kas0);
  var jam0 = __KINI; __KINI = new __DateAsli('2026-09-30T23:30:00+07:00').getTime(); bandingFungsi('30 Sep 23.30'); __KINI = new __DateAsli('2026-10-01T00:30:00+07:00').getTime(); bandingFungsi('1 Okt 00.30 (bulan berganti)');
  __KINI = jam0;
}

// ---- ORAKEL DASBOR: Ringkasan yang baru dipasang menghitung segar — isinya harus sama dengan dasbor yang hidup terus
var RG = __E['baru/js/layar/ringkasan.js'];
function orakelDasbor(label) {
  if (!PERIKSA) return;
  var a = (AK.ringkasan.querySelector('#rkDasbor') || {}).__html || '';
  var A2 = new __El('main'); var gb = __gb; var R2 = RG.pasangLayarRingkasan(A2, opsi); R2.tampilkan(true); __tuntas(); __sisa();
  var b = (A2.querySelector('#rkDasbor') || {}).__html || ''; R2.tampilkan(false); __tuntas(); __sisa(); __gb = gb;
  HASIL.orakel.push({ aksi: label, sama: a === b, ada: a.length > 200, contoh: a === b ? '' : a.slice(0, 120) + ' ≠ ' + b.slice(0, 120) });
}

// ---- pembaca HTML tergambar: elemen data-aksi / data-ketik + dataset
var ENT = { '&amp;': '&', '&quot;': '"', '&#39;': "'", '&lt;': '<', '&gt;': '>' };
var lepas = function (s) { return String(s).replace(/&(amp|quot|#39|lt|gt);/g, function (m) { return ENT[m]; }); };
var kamel = function (s) { return s.replace(/-([a-z0-9])/g, function (m, c) { return c.toUpperCase(); }); };
function elemen(html, atr) {
  var out = [], re = new RegExp('<([a-zA-Z]+)\\b[^>]*\\b' + atr + '="([^"]+)"[^>]*>', 'g'), m;
  while ((m = re.exec(html))) { var tagTeks = m[0], ds = {}, a, ra = /\bdata-([a-z0-9-]+)="([^"]*)"/g; while ((a = ra.exec(tagTeks))) ds[kamel(a[1])] = lepas(a[2]); out.push({ tag: m[1].toLowerCase(), nama: lepas(m[2]), ds: ds }); }
  return out;
}
function elPalsu(ds, value) { var el = new __El(); el.dataset = Object.assign({}, ds); el.value = value || ''; return el; }
function ketuk(akar, nama, ds) { var f = akar.__aksi && akar.__aksi[nama]; if (!f) throw new Error('aksi tidak ada: ' + nama); var el = elPalsu(ds); return f(Object.assign({}, ds), el, { preventDefault: function () {}, stopPropagation: function () {}, target: el }); }
function ketik(akar, nama, ds, v) { var f = akar.__aksi && akar.__aksi[nama]; if (!f) throw new Error('ketik tidak ada: ' + nama); var el = elPalsu(ds, v); return f(v, el, { preventDefault: function () {}, target: el, key: '' }); }
// ketukan yang MENULIS / keluar layar tidak dijalankan
var TULIS = /simpan|Simpan|hapus|Hapus|kirim|Kirim|terbit|Terbit|tulis|Tulis|catat|Catat|bayar|Bayar|[Ll]unas|kunci|Kunci|buang|Buang|arsip|Arsip|pulih|Pulih|setujui|[Tt]olak|daftarkan|unduh|Wa$|Wa[A-Z]|^wa|[Cc]etak|gabungkan|[Ss]erah|^bk(?!Mode)|sisihkan|bongkar|tuangBalik|bukaKarung|samakanKarung|pisahUkuran|gabungUkuran|^dr(Kosong|Kembalikan|Hapus)|tandaiTulis|^mode$|[Bb]ertahap|periksaSambung|putarHak|ubahPeran|^op[A-Z]|saklarAkun|jadikanUtama|lokasiIni|stafKe|mintaKe|Putus$|kpLupakan|aktifkan|^pergi$|keTujuan|^ke[A-Z]|kpCocok|[Uu]rung|Batal$|^tdCek|tdTimbang|kirimTagih|bsBersihkan|iniDia|bukanKembar|tampiJawab|kuis|vrTerbit|vrBuat|PakaiUsul|UsulSemua|SaranSemua|blPenuhi|ukJadiKasbon|ukTetapPrive|upSlip|tdLangkah|[Aa]mbil|tundaG|selesaiG|saklarG|tdPecahan|^tujuan$|^lbKeping$|dkPaketSusun|stPutar|aTambah|aLepas|mTambahBaris|mLepasBaris|tpGeser|aturGeser|aturTambah|aturLepas|aturGanti|kalRp|Keluar$/;
var SUBNAV = /^(tab\w*|\w+Tab|tanya|sistem|susunan|bagian|laci|dkJenis|dkKecilJenis|jenisK|blBulan|kbBulan|hrHari|mgMinggu|thTahun|tahunGeser|pilihWadah|saring|rincianLain|hariP|hariC|pilihP|peran)$/;

function satuLayar(nama, L, akar, rencana) {
  LAYAR_KINI = nama;
  ukur('buka pertama', function () { L.tampilkan(true); });
  ukur('buka lagi, data sama', function () { L.tampilkan(true); }, function () { L.tampilkan(false); });
  ukur('buka lagi sesudah data berubah (tersembunyi)', function () { L.tampilkan(true); }, function () { L.tampilkan(false); D.pasok('penjualan', D.cacheMentah('penjualan').slice()); __tuntas(); });
  ukur('gambar ulang langsung', function () { L.gambar(); });
  ['penjualan', 'perangkatStatus', 'wadahLiteran', 'pengeluaranHarian'].forEach(function (k) { ukur('data berubah selagi tampil: pasok ' + k, function () { D.pasok(k, D.cacheMentah(KOL[k]).slice()); }); });
  ukur('nota baru tercatat (isi penjualan berubah)', function () { notaBaru(); });
  ukur('titik kas perangkat berubah (tanpa data baru)', function () { titikBaru(); L.gambar(); });
  if (rencana) rencana();
}
var KOL = { penjualan: 'penjualan', perangkatStatus: 'perangkat', wadahLiteran: 'wadah', pengeluaranHarian: 'harian' };
function jelajah(label, L, akar, batas) {
  batas = batas || {}; var K = L.keadaan; var snap = K.baca(); var html = akar.__html || '';
  var semua = elemen(html, 'data-aksi'); var lihat = {};
  var pulih = function () { K.setel(snap); };
  semua.filter(function (e) { return SUBNAV.test(e.nama); }).forEach(function (e) {
    var k = e.nama + J(e.ds); if (lihat[k]) return; lihat[k] = 1;
    ukur(label + ' › ' + e.nama + '=' + (e.ds.t || e.ds.nama || e.ds.ke || e.ds.k || e.ds.s || e.ds.a || J(e.ds).slice(0, 40)), function () { ketuk(akar, e.nama, e.ds); }, pulih);
  });
  pulih(); __tuntas(); __sisa();
  ketikSemua(label, L, akar);
  var perNama = {}; var n = 0;
  semua.forEach(function (e) {
    if (SUBNAV.test(e.nama) || TULIS.test(e.nama) || n >= (batas.ketuk || 24)) return;
    perNama[e.nama] = (perNama[e.nama] || 0) + 1; if (perNama[e.nama] > 2) return;
    var k = e.nama + J(e.ds); if (lihat[k]) return; lihat[k] = 1; n++;
    ukur(label + ' · ketuk ' + e.nama + (Object.keys(e.ds).length > 1 ? ' ' + J(e.ds).slice(0, 50) : ''), function () { ketuk(akar, e.nama, e.ds); }, pulih);
  });
  pulih(); __tuntas(); __sisa();
}
function ketikSemua(label, L, akar) {
  var K = L.keadaan; var snap = K.baca(); var lihat = {}; var n = 0;
  elemen(akar.__html || '', 'data-ketik').forEach(function (e) {
    var k = e.nama + J(e.ds); if (lihat[k] || n >= 6) return; lihat[k] = 1; n++;
    var teks = /cari|Cari|nama|Nama|alasan|Alasan|catatan|pengantar|toko|pemasok|ket$|Ket$|judul|bukti/i.test(e.nama + J(e.ds)) && e.tag !== 'select' ? ['a', 'an'] : ['1', '12'];
    ukur(label + ' · ketik ' + e.nama + (e.ds.kolom ? '[' + e.ds.kolom + ']' : ''), function () { ketik(akar, e.nama, e.ds, teks[1]); }, function () { K.setel(snap); __tuntas(); ketik(akar, e.nama, e.ds, teks[0]); });
    K.setel(snap); __tuntas(); __sisa();
  });
}

// ---- jalankan
rangkaianFungsi();
var LY = {}, AK = {};
var pasangX = { ringkasan: ['baru/js/layar/ringkasan.js', 'pasangLayarRingkasan', opsi], stok: ['baru/js/layar/stok.js', 'pasangLayarStok', opsi], pelanggan: ['baru/js/layar/pelanggan.js', 'pasangLayarPelanggan', opsi],
  menu: ['baru/js/layar/menu.js', 'pasangLayarMenu', opsiMenu], harga: ['baru/js/layar/harga.js', 'pasangLayarHarga', opsi], uang: ['baru/js/layar/uang.js', 'pasangLayarUang', opsiUang], laporan: ['baru/js/layar/laporan.js', 'pasangLayarLaporan', opsi] };
LAYAR_KINI = 'semua';
Object.keys(pasangX).forEach(function (n) { var x = pasangX[n]; AK[n] = new __El('main'); ukur('pasang layar ' + n, function () { LY[n] = __E[x[0]][x[1]](AK[n], x[2]); }); });
ukur('data berubah, semua layar tersembunyi', function () { D.pasok('penjualan', D.cacheMentah('penjualan').slice()); });

// RINGKASAN: Dasbor (owner, bawaan) lalu Cincin — tiap aksi dasbor diperiksa orakel
var R = LY.ringkasan, AR = AK.ringkasan;
var klik = function (id, ds) { var el = AR.querySelector('#' + id); (el && el.__dengar.click || []).forEach(function (f) { f({ target: { closest: function () { return { dataset: ds }; } } }); }); };
var ukurDb = function (label, f, p) { ukur(label, f, p); orakelDasbor(label); };
LAYAR_KINI = 'ringkasan-dasbor';
ukurDb('buka pertama', function () { R.tampilkan(true); });
['penjualan', 'perangkatStatus', 'wadahLiteran', 'pengeluaranHarian'].forEach(function (k) { ukurDb('data berubah selagi tampil: pasok ' + k, function () { D.pasok(k, D.cacheMentah(KOL[k]).slice()); }); });
['minggu', 'bulan', 'hari'].forEach(function (r) { ukurDb('dasbor › rentang ' + r, function () { klik('rkDasbor', { dbRentang: r }); }); });
ukurDb('nota baru tercatat (isi penjualan berubah)', function () { notaBaru(); });
ukurDb('dasbor › rentang minggu sesudah nota baru', function () { klik('rkDasbor', { dbRentang: 'minggu' }); });
ukurDb('denyut HP (perangkatStatus) sesudah ganti rentang', function () { D.pasok('perangkatStatus', D.cacheMentah('perangkat').concat([{ id: 'p-uji', pada: new Date().toISOString(), aplikasi: 'baru', antrean: 0 }])); });
ukurDb('nota baru lagi (rentang minggu)', function () { notaBaru(); });
ukurDb('dasbor › rentang hari', function () { klik('rkDasbor', { dbRentang: 'hari' }); });
ukurDb('detak tiap menit (hari sama)', function () { __KINI += 60000; __interval.forEach(function (f) { f(); }); });
ukur('ganti tampilan → Cincin', function () { klik('rkSaklar', { tampil: 'cincin' }); });
R.tampilkan(false); __tuntas(); __sisa();
satuLayar('ringkasan-cincin', R, AR, function () {
  ['langsung', 'menit', 'jam', 'hari', 'minggu', 'bulan', 'tahun', 'jam'].forEach(function (s) { ukur('cincin › skala ' + s, function () { klik('rkSkala', { k: s }); }); });
  ukur('detak tiap menit (cincin)', function () { __KINI += 60000; __interval.forEach(function (f) { f(); }); });
  ukurDb('ganti tampilan → Dasbor', function () { klik('rkSaklar', { tampil: 'dasbor' }); });
});
R.tampilkan(false); __tuntas(); __sisa();

function layarBiasa(nama, keluargaAksi, daftar, kunciDs) {
  var L = LY[nama], A = AK[nama];
  satuLayar(nama, L, A, function () {
    daftar.forEach(function (k, i) {
      var ds = {}; ds[kunciDs] = k; var lain = {}; lain[kunciDs] = daftar[i === 0 ? 1 : 0];
      ukur(nama + ' › ' + k + ' (pindah tab)', function () { ketuk(A, keluargaAksi, ds); }, function () { ketuk(A, keluargaAksi, lain); });
      ketuk(A, keluargaAksi, ds); __tuntas(); __sisa();
      ukur(nama + ' › ' + k + ' · nota baru', function () { notaBaru(); });
      jelajah(nama + ' › ' + k, L, A, { ketuk: 20 });
    });
  });
  L.tampilkan(false); __tuntas(); __sisa();
}
var LG = __E['baru/js/layar/laporan-logika.js'], UG = __E['baru/js/layar/uang-logika.js'], SL = __E['baru/js/layar/stok-logika.js'];
// STOK: tab + lembar kerja
var LS = LY.stok, AS = AK.stok;
satuLayar('stok', LS, AS, function () {
  SL.TAB_STOK.forEach(function (t) {
    ukur('stok › ' + t[0] + ' (pindah tab)', function () { ketuk(AS, 'tab', { t: t[0] }); }, function () { ketuk(AS, 'tab', { t: t[0] === 'gudang' ? 'kapur' : 'gudang' }); });
    ketuk(AS, 'tab', { t: t[0] }); __tuntas(); __sisa();
    ukur('stok › ' + t[0] + ' · nota baru', function () { notaBaru(); });
    jelajah('stok › ' + t[0], LS, AS, { ketuk: 20 });
  });
  ketuk(AS, 'tab', { t: 'gudang' }); __tuntas(); __sisa();
  ['bukaMasuk', 'bukaAdukan', 'bukaCocok', 'bukaKantong', 'bukaTempat', 'bukaHpp'].forEach(function (b) {
    ukur('stok › lembar ' + b, function () { ketuk(AS, b, {}); }, function () { LS.keadaan.setel({ lembar: null }); notaBaru(); });
    ketuk(AS, b, {}); __tuntas(); __sisa();
    jelajah('stok › ' + b, LS, AS, { ketuk: 14 });
    LS.keadaan.setel({ lembar: null }); __tuntas(); __sisa();
  });
});
LS.tampilkan(false); __tuntas(); __sisa();
layarBiasa('pelanggan', 'keluarga', ['kenali', 'bon', 'thr'], 'ke');
layarBiasa('harga', 'keluarga', ['katalog', 'bon', 'belanja'], 'nama');
layarBiasa('uang', 'keluarga', UG.KELUARGA_UANG.map(function (k) { return k[0]; }), 'nama');
layarBiasa('laporan', 'keluarga', LG.KELUARGA_LAPORAN.map(function (k) { return k[0]; }), 'nama');
// MENU: laci, Sistem, lalu simpanan perangkat berubah (keadaan lsKb wajib ikut)
var LM = LY.menu, AM = AK.menu;
satuLayar('menu', LM, AM, function () {
  jelajah('menu (laci)', LM, AM, { ketuk: 16 });
  ['perangkat', 'cadangan', 'pengingat'].forEach(function (s) {
    ukur('menu › Sistem ' + s, function () { LM.keadaan.setel({ sistem: s }); }, function () { LM.keadaan.setel({ sistem: null }); });
    LM.keadaan.setel({ sistem: s }); __tuntas(); __sisa();
    jelajah('menu › Sistem ' + s, LM, AM, { ketuk: 12 });
    LM.keadaan.setel({ sistem: null }); __tuntas(); __sisa();
  });
  ukur('simpanan perangkat bertambah lalu Menu dibuka lagi', function () { LM.tampilkan(true); }, function () { LM.tampilkan(false); localStorage.setItem('uji_mulus_isi', new Array(4001).join('x')); });
  var b = 0; for (var i = 0; i < localStorage.length; i++) { var k = localStorage.key(i); b += (k.length + String(localStorage.getItem(k) || '').length) * 2; }
  HASIL.info.menuLsKb = { keadaan: LM.keadaan.baca().lsKb, harap: Math.round(b / 1024) };
});
// ---- TANDINGAN KUNCI LUAR (sanggahan 7 Okt): yang DIGAMBAR layar tetapi TIDAK menaikkan versi data — jam 12 siang (hari tutup aktif), hari, pita jam Menu,
// jam Pelanggan, menit Sistem › Perangkat, titik kas perangkat, tahun (indeks cincin). Layar yang hidup terus (dibuka lagi tanpa data baru, detak menit, denyut
// HP, jejak tulisan, ganti rentang) harus SAMA dengan gambar segar pada saat yang sama. `berubah` = gambar segar memang beda dari gambar sebelum kejadian
// (kasusnya tajam — tidak lulus karena isinya kebetulan sama). ms = ongkos kejadian itu (jam dinding).
HASIL.tandingan = [];
if (MODE !== 'mati') (function () {
  var HARI0 = F.hariIniIso(new Date(JAM));
  var jamPada = function (iso, hm) { return new __DateAsli(iso + 'T' + hm + ':00+07:00').getTime(); };
  var hariKe = function (n) { return F.hariIniIso(new __DateAsli(jamPada(HARI0, '12:00') + n * 86400000)); };
  var potong = function (a, b) { var i = 0; while (i < a.length && a[i] === b[i]) i++; return a.slice(Math.max(0, i - 60), i + 90) + ' ≠ ' + b.slice(Math.max(0, i - 60), i + 90); };
  var catat = function (nama, hidup, segar, lama, ms) { HASIL.tandingan.push({ nama: nama, sama: hidup === segar, berubah: segar !== lama, ada: segar.length > 200, ms: Math.round(ms * 10) / 10, contoh: hidup === segar ? '' : potong(hidup, segar) }); };
  var waktuKejadian = function (f) { var t0 = preciseTime(); try { f(); } catch (e) { console.error('tandingan', e); } __tuntas(); var ms = (preciseTime() - t0) * 1000; __sisa(); return ms; };
  // DASBOR: dasbor yang hidup terus vs Ringkasan yang baru dipasang (orakel yang sama dengan orakelDasbor)
  var dbHtml = function (A) { return (A.querySelector('#rkDasbor') || {}).__html || ''; };
  var dbSegar = function () { var A2 = new __El('main'); var gb = __gb; var R2 = RG.pasangLayarRingkasan(A2, opsi); R2.tampilkan(true); __tuntas(); __sisa(); var x = dbHtml(A2); R2.tampilkan(false); __tuntas(); __sisa(); __gb = gb; return x; };
  var buka = function (jam) { R.tampilkan(false); __tuntas(); __sisa(); __KINI = jam; R.tampilkan(true); __tuntas(); __sisa(); };
  var denyut = function (id) { D.pasok('perangkatStatus', D.cacheMentah('perangkat').concat([{ id: id, pada: new Date().toISOString(), aplikasi: 'kasir', antrean: 0 }])); };
  var dasbor = function (nama, jam0, jam1, f) { buka(jam0); var lama = dbHtml(AR); if (jam1) __KINI = jam1; var ms = waktuKejadian(f); catat('Dasbor · ' + nama, dbHtml(AR), dbSegar(), lama, ms); };
  dasbor('dibuka 11.58, detak menit 12.02 tanpa data ("cek tutup" wadah pindah hari)', jamPada(HARI0, '11:58'), jamPada(HARI0, '12:02'), function () { __interval.forEach(function (f) { f(); }); });
  dasbor('dibuka 11.58, denyut HP 12.02', jamPada(hariKe(1), '11:58'), jamPada(hariKe(1), '12:02'), function () { denyut('p-tand1'); });
  dasbor('dibuka 11.58, jejak tulisan 12.02', jamPada(hariKe(2), '11:58'), jamPada(hariKe(2), '12:02'), function () { D.pasok('logAktivitas', D.cacheMentah('log').concat([{ id: 'l-tand', pada: new Date().toISOString(), ringkas: 'uji' }])); });
  dasbor('dibuka 11.58, ganti rentang minggu 12.02', jamPada(hariKe(3), '11:58'), jamPada(hariKe(3), '12:02'), function () { klik('rkDasbor', { dbRentang: 'minggu' }); });
  dasbor('titik kas perangkat berubah lalu ganti rentang bulan', jamPada(hariKe(3), '13:00'), null, function () { titikBaru(); klik('rkDasbor', { dbRentang: 'bulan' }); });
  dasbor('titik kas perangkat berubah lalu denyut HP', jamPada(hariKe(3), '13:10'), null, function () { titikBaru(); denyut('p-tand2'); });
  dasbor('titik kas perangkat berubah lalu detak menit', jamPada(hariKe(3), '13:20'), jamPada(hariKe(3), '13:21'), function () { titikBaru(); __interval.forEach(function (f) { f(); }); });
  klik('rkDasbor', { dbRentang: 'hari' }); R.tampilkan(false); __tuntas(); __sisa();
  // LAYAR LAIN: ditutup di jam0, dibuka lagi di jam1 TANPA data baru (ubah = hanya titik kas perangkat) → sama dengan gambar paksa segar saat itu juga
  var layar = function (nama, L, A, jam0, siapkan, jam1, ubah) {
    L.tampilkan(false); __tuntas(); __sisa(); __KINI = jam0;
    if (siapkan) { try { siapkan(); } catch (e) { console.error('siapkan ' + nama, e); } __tuntas(); __sisa(); }
    L.tampilkan(true); __tuntas(); __sisa(); L.gambar(); __tuntas(); __sisa(); var lama = A.__html;
    L.tampilkan(false); __tuntas(); __sisa(); __KINI = jam1;
    if (ubah) { ubah(); __tuntas(); __sisa(); }
    var ms = waktuKejadian(function () { L.tampilkan(true); }); var hidup = A.__html;
    L.gambar(); __tuntas(); __sisa(); catat(nama, hidup, A.__html, lama, ms);
  };
  var AU = AK.uang, LU = LY.uang, AH = AK.harga, LH = LY.harga, AL = AK.laporan, LL = LY.laporan, AP = AK.pelanggan, LP = LY.pelanggan;
  layar('Menu · dibuka 20.00, dibuka lagi esok 09.00', LM, AM, jamPada(hariKe(4), '20:00'), function () { LM.keadaan.setel({ sistem: null, susunan: 'laci' }); }, jamPada(hariKe(5), '09:00'));
  layar('Menu · pita jam berganti Sore → Malam (hari sama, sesudah 12.00)', LM, AM, jamPada(hariKe(5), '16:00'), null, jamPada(hariKe(5), '18:00'));
  layar('Menu (yang bertanya) · titik kas perangkat berubah', LM, AM, jamPada(hariKe(5), '18:30'), function () { LM.keadaan.setel({ susunan: 'tanya' }); }, jamPada(hariKe(5), '18:30'), titikBaru);
  layar('Menu › Sistem › Perangkat · dibuka lagi 10 menit kemudian (denyut N menit lalu)', LM, AM, jamPada(hariKe(5), '19:00'), function () { LM.keadaan.setel({ susunan: 'laci', sistem: 'perangkat' }); D.pasok('perangkatStatus', D.cacheMentah('perangkat').concat([{ id: 'p-mac', pada: new Date().toISOString(), aplikasi: 'baru', antrean: 0 }])); }, jamPada(hariKe(5), '19:10'));
  LM.keadaan.setel({ sistem: null, susunan: 'laci' }); LM.tampilkan(false); __tuntas(); __sisa();
  // wadah pertama diberi stok sendiri (pindahan awal, jalur tulis asli) + cek tutup toko 20.00 kemarin: sebelum 12.00 rinciannya ("Karung di belakang…" dibuka)
  // memajang cek itu, sesudahnya "belum dicek"
  var WB = __E['baru/js/layar/wadah-bernama-logika.js'], nU = 0; var W0 = JL.aturWadah().daftar[0];
  var wkt = function (iso, jam) { return { tanggal: iso, jam: jam, kini: new Date().toISOString(), idUnik: function () { nU += 1; return 9100000000000 + nU; } }; };
  layar('Stok › Wadah literan · dibuka lagi sesudah 12.00 (cek tutup)', LS, AS, jamPada(hariKe(6), '11:58'), function () {
    var P = WB.wbSusunPindahAwal(wkt(hariKe(5), '19:55'), W0); if (!P.tolak) D.terapkanKeCache(P.dokumen);
    var C = WB.wbSusunCek(W0, 'sesuai', wkt(hariKe(5), '20:00')); if (!C.tolak) D.terapkanKeCache(C.dokumen);
    D.pasok('wadahLiteran', D.cacheMentah('wadah').slice());   // pendengar data berbunyi seperti sesudah tulisan sungguhan (versi data layar naik)
    ketuk(AS, 'tab', { t: 'wadah' }); LS.keadaan.setel({ wadahAktif: W0, rincianLain: true }); }, jamPada(hariKe(6), '12:02'));
  layar('Stok › Gudang · dibuka lagi esok hari', LS, AS, jamPada(hariKe(6), '13:00'), function () { ketuk(AS, 'tab', { t: 'gudang' }); }, jamPada(hariKe(7), '13:00'));
  LS.tampilkan(false); __tuntas(); __sisa();
  layar('Uang › Tutup hari · dibuka lagi sesudah 12.00 (hari dagang yang ditutup)', LU, AU, jamPada(hariKe(7), '11:58'), function () { ketuk(AU, 'keluarga', { nama: 'tutup' }); }, jamPada(hariKe(7), '12:02'));
  layar('Uang › Pindah uang · titik kas perangkat berubah', LU, AU, jamPada(hariKe(7), '13:00'), function () { ketuk(AU, 'keluarga', { nama: 'pindah' }); }, jamPada(hariKe(7), '13:00'), titikBaru);
  LU.tampilkan(false); __tuntas(); __sisa();
  layar('Harga › Bon pemasok · titik kas perangkat berubah', LH, AH, jamPada(hariKe(7), '14:00'), function () { ketuk(AH, 'keluarga', { nama: 'bon' }); }, jamPada(hariKe(7), '14:00'), titikBaru);
  layar('Harga › Belanja · dibuka lagi esok hari', LH, AH, jamPada(hariKe(7), '14:00'), function () { ketuk(AH, 'keluarga', { nama: 'belanja' }); }, jamPada(hariKe(8), '14:00'));
  LH.tampilkan(false); __tuntas(); __sisa();
  layar('Laporan › Harian · dibuka lagi esok hari', LL, AL, jamPada(hariKe(8), '20:00'), function () { ketuk(AL, 'keluarga', { nama: 'harian' }); }, jamPada(hariKe(9), '13:00'));
  layar('Laporan › Neraca · titik kas perangkat berubah', LL, AL, jamPada(hariKe(9), '13:00'), function () { ketuk(AL, 'keluarga', { nama: 'neraca' }); }, jamPada(hariKe(9), '13:00'), titikBaru);
  LL.tampilkan(false); __tuntas(); __sisa();
  layar('Pelanggan › Kenali · jam berganti siang → sore (hari sama)', LP, AP, jamPada(hariKe(9), '13:00'), function () { ketuk(AP, 'keluarga', { ke: 'kenali' }); }, jamPada(hariKe(9), '16:00'));
  LP.tampilkan(false); __tuntas(); __sisa();
  // TAHUN BARU tanpa data baru: Uang › Tutup buku membaca tahun yang bisa ditutup; indeks cincin membaca potret tahun < tahun jam sekarang
  var th = Number(HARI0.slice(0, 4));
  layar('Uang › Tutup buku · dibuka lagi sesudah tahun baru', LU, AU, jamPada(th + '-12-31', '20:00'), function () { ketuk(AU, 'keluarga', { nama: 'buku' }); }, jamPada((th + 1) + '-01-02', '13:00'));
  LU.tampilkan(false); __tuntas(); __sisa();
  klik('rkSaklar', { tampil: 'cincin' }); buka(jamPada(th + '-12-31', '23:58')); var n = {};
  __n = {}; __KINI = jamPada(th + '-12-31', '23:59'); __interval.forEach(function (f) { f(); }); __tuntas(); __sisa(); n.samaTahun = __n.bangunIndeks || 0;
  __n = {}; __KINI = jamPada((th + 1) + '-01-01', '00:01'); __interval.forEach(function (f) { f(); }); __tuntas(); __sisa(); n.gantiTahun = __n.bangunIndeks || 0;
  HASIL.info.cincinTahun = n; R.tampilkan(false); __tuntas(); __sisa();
})();
HASIL.galat = __galat.slice(0, 40); HASIL.info.nGalat = __galat.length;
print('@@HASIL@@' + JSON.stringify(HASIL));
"""


def kotak():
    """Kotak pasir gabungan — ANGKA CONTOH, bukan angka toko."""
    import uji_rak_inkremental, uji_ringkasan_baru
    k = json.loads(json.dumps(uji_rak_inkremental.KOTAK))
    for nama, isi in uji_ringkasan_baru.kotak_dasbor().items():
        if not isinstance(isi, list): continue
        ada = set(str(x.get('id')) for x in k.get(nama, []))
        k[nama] = k.get(nama, []) + [dict(x, id=(str(x.get('id')) + '-d') if str(x.get('id')) in ada else x.get('id')) for x in isi]
    # tempat simpan (tumpukan 3D punya isi), aturan pajak (rekap setahun dihitung), denyut satu HP kasir
    k['pengaturan'] = k.get('pengaturan', []) + [{'id': 'tempatSimpan', 'peta': {'K:Angsa': 'Kiri belakang', 'K:NG': 'Kiri belakang', 'K:Kumala': 'Kanan belakang', 'K:Tawon': 'Kanan belakang'}}]
    k['aturanToko'] = k.get('aturanToko', []) + [{'id': 'rekapOmzet', 'tanggal': '2026-09-01', 'jam': '08:00', 'tarifPerMil': 5, 'batasBebas': 500000000, 'batasOmzet': 4800000000, 'tanggalLapor': 15, 'lapor': {}}]
    k['perangkatStatus'] = k.get('perangkatStatus', []) + [{'id': 'k-hp1', 'pada': '2026-09-21T02:30:00.000Z', 'aplikasi': 'kasir', 'antrean': 0, 'versi': 'kasir-v32'}]
    return k


TITIK_KOTAK = {'tanggal': '2026-09-14', 'laci': 1500000, 'rekening': 300000, 'amplop': 0, 'brankas': 0, 'diubahPada': '9999-12-31T00:00:00.000Z'}


def jalan(mode, cad, jam, titik, ganti=None, periksa=True):
    js, peta, urut = modul_es.bundel(LAYAR, LINGKUNGAN, ganti)
    kode = (js + '\nvar CAD = ' + json.dumps(cad) + ';\nvar JAM = ' + json.dumps(jam) + ';\nvar MODE = ' + json.dumps(mode) + ';\nvar TITIK = ' + json.dumps(titik)
            + ';\nvar PERIKSA = ' + ('true' if periksa else 'false') + ';\n' + PEMANDU)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(kode); p = f.name
    try: r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta'), timeout=1200)
    finally: os.unlink(p)   # bundel bisa berisi data toko (mode cadangan) — tidak dibiarkan tergeletak
    out = r.stdout or ''; i = out.find('@@HASIL@@')
    if i < 0: return None, 'JSC JATUH (%s): %s' % (r.returncode, (r.stderr or out)[-900:])
    return json.loads(out[i + 9:].strip().split('\n')[0]), ''


def periksa(H, nama_kotak, data_toko=False):
    """H = { mati, hidup, beku } → (lulus, gagal[])."""
    l, g = 0, []
    def ok(nama, syarat, ket=''):
        nonlocal l
        if syarat: l += 1
        else: g.append(nama + (' → ' + str(ket)[:600] if ket else ''))
    A, B, C = H['mati'], H['hidup'], H.get('beku')
    aksi = lambda x: [(a['layar'], a['aksi']) for a in x['aksi']]
    for nm, X in [('hidup', B)] + ([('beku', C)] if C else []):
        ok('%s · galat: tidak ada galat di rangkaian %s (%d aksi)' % (nama_kotak, nm, len(X['aksi'])), not X['info'].get('nGalat'), X.get('galat', [])[:3])
        ok('%s · KESETARAAN %s: urutan aksi = rangkaian tanpa ingatan' % (nama_kotak, nm), aksi(X) == aksi(A), [x for x in zip(aksi(X), aksi(A)) if x[0] != x[1]][:2])
        beda = [(a['layar'], a['aksi']) for a, b in zip(A['aksi'], X['aksi']) if a['sidik'] != b['sidik']]
        ok('%s · KESETARAAN %s: semua yang digambar byte-sama dengan hitung ulang penuh di %d aksi' % (nama_kotak, nm, len(A['aksi'])), not beda, beda[:4])
        f = X['fungsi']; salah = [x for x in f if not x['sama']]
        ok('%s · FUNGSI %s: %d hasil fungsi berbuku-ingatan = hitung ulang penuh (awal, nota baru, cache sementara, titik kas, ganti hari & bulan)' % (nama_kotak, nm, len(f)), f and not salah,
           [(x['tahap'], x['nama'], x['contoh']) for x in salah[:3]])
    ok('%s · galat: tidak ada galat di rangkaian tanpa ingatan' % nama_kotak, not A['info'].get('nGalat'), A.get('galat', [])[:3])
    o = B['orakel']; salah = [x for x in o if not x['sama']]
    ok('%s · ORAKEL DASBOR: %d keadaan dasbor = Ringkasan yang baru dipasang (ganti rentang, denyut HP, nota baru tidak meninggalkan kartu basi)' % (nama_kotak, len(o)),
       len(o) >= 10 and all(x['ada'] for x in o) and not salah, [(x['aksi'], x['contoh']) for x in salah[:2]] or len(o))
    # kontrol positif rangkaian (cakupan sungguh dijalankan — bukan lulus karena sempit)
    ok('%s · cakupan: nota baru menambah penjualan berlaku; titik kas perangkat berubah mengubah kasPada; fungsi berisi' % nama_kotak,
       B['info'].get('notaMenambah') and B['info'].get('titikMengubahKas') and sum(1 for x in B['fungsi'] if x['ada']) >= len(B['fungsi']) * 0.6, B['info'])
    m = B['info'].get('menuLsKb') or {}
    ok('%s · Menu: simpanan perangkat bertambah → angka simpanan di keadaan Menu ikut (%s KB)' % (nama_kotak, m.get('harap')), m.get('keadaan') == m.get('harap') and m.get('harap'), m)
    # KUNCI LUAR (sanggahan 7 Okt): kejadian tanpa data baru — layar yang hidup terus = gambar segar saat itu juga
    for nm, X in [('hidup', B)] + ([('beku', C)] if C else []):
        T = X.get('tandingan') or []; salah = [x for x in T if not x['sama']]
        ok('%s · KUNCI LUAR %s: %d kejadian tanpa data baru (jam 12 siang, hari, pita jam, jam, menit, titik kas perangkat, tahun baru) — layar yang hidup terus = gambar segar' % (nama_kotak, nm, len(T)),
           len(T) >= 21 and not salah, [(x['nama'], x['contoh'][:220]) for x in salah[:2]] or len(T))
    ci = B['info'].get('cincinTahun') or {}
    ok('%s · Cincin: indeks dibangun ulang saat tahun berganti tanpa data baru (1×), tidak di detak menit biasa (0×)' % nama_kotak, ci.get('gantiTahun') == 1 and ci.get('samaTahun') == 0, ci)
    if data_toko: return l, g
    T = B.get('tandingan') or []
    ok('cakupan KUNCI LUAR: tiap kejadian benar-benar mengubah gambar segar (kasus tajam — tidak lulus karena isinya kebetulan sama)', T and all(x['berubah'] and x['ada'] for x in T),
       [x['nama'] for x in T if not (x['berubah'] and x['ada'])])
    # ONGKOS (hitungan panggilan, pasti) — rangkaian DENGAN ingatan
    cari = lambda layar, pola: [a for a in B['aksi'] if a['layar'] == layar and re.search(pola, a['aksi'])]
    P = lambda a, f: (a['panggil'] or {}).get(f, 0)
    t = cari('stok', r'^stok › lembar bukaTempat$')
    tp = cari('stok', r'^stok › bukaTempat')
    ok('ONGKOS · Stok › Tempat simpan: rantai stok disusun SEKALI per gambar (isi wadah per merek ≤ 2×, buku stok mesin ≤ 1×; dulu tiap tumpukan menghitung ulang)',
       t and tp and all(P(a, 'wbBagianMerk') <= 2 and P(a, 'hitungStokKarungPerMerk') <= 1 for a in t + tp), [(a['aksi'][:40], a['panggil']) for a in (t + tp)[:3]])
    k = cari('harga', r'^harga › katalog( › | · ketuk (?!keluarga))')
    ok('ONGKOS · Harga › Katalog: %d ketukan / sub-tab tanpa data baru tidak menghitung buku stok mesin (karung & kemasan 0×; dulu ±130× per ketukan di data toko)' % len(k), len(k) >= 3 and all(P(a, 'hitungStokKarungPerMerk') + P(a, 'hitungStokKemasan') == 0 for a in k),
       [(a['aksi'][:40], a['panggil']) for a in k if P(a, 'hitungStokKarungPerMerk') + P(a, 'hitungStokKemasan')][:2])
    r = cari('ringkasan-dasbor', r'^dasbor › rentang (minggu|bulan|hari)$')
    ok('ONGKOS · Dasbor ganti rentang: hanya tren dihitung (daftar stok gudang 0×, buku stok 0×)', len(r) >= 3 and all(P(a, 'daftarBarang') == 0 and P(a, 'hitungStokKarungPerMerk') == 0 for a in r), [a['panggil'] for a in r])
    d = cari('ringkasan-dasbor', r'perangkatStatus')
    ok('ONGKOS · Dasbor: denyut HP (perangkatStatus) tidak menyusun dasbor ulang (susunDasbor 0×)', len(d) >= 2 and all(P(a, 'susunDasbor') == 0 for a in d), [a['panggil'] for a in d])
    n = [a for a in cari('ringkasan-dasbor', r'^data berubah selagi tampil: pasok (penjualan|wadahLiteran)$') + cari('ringkasan-dasbor', r'^nota baru')]
    ok('ONGKOS · Dasbor: data yang dibaca dasbor (penjualan, wadah) TETAP menyusun dasbor ulang (susunDasbor 1×)', n and all(P(a, 'susunDasbor') == 1 for a in n), [a['panggil'] for a in n])
    mb = cari('menu', r'^buka lagi, data sama$')
    ok('ONGKOS · Menu dibuka lagi tanpa data baru: tidak digambar ulang (0 gambar; dulu 2)', mb and all(a['gambar'] == 0 for a in mb), [a['gambar'] for a in mb])
    bl = cari('laporan', r'^laporan › bulanan › ')
    ok('ONGKOS · Laporan › Bulanan: %d sub-tab / bulan tanpa data baru — omzet 12 bulan & rekap pajak setahun diingat (mesin laba ≤ 8× = bulan yang dipilih saja)' % len(bl), len(bl) >= 3 and all(P(a, 'hitungLabaRentang') <= 8 for a in bl), [a['panggil'] for a in bl][:3])
    u = cari('uang', r' · (ketuk|ketik) (?!keluarga|upHari|puRutin)')   # memilih tanggal lain (upHari, puRutin) = saldo tanggal itu dihitung sekali
    ok('ONGKOS · Uang: %d ketukan / ketikan tanpa data baru tidak menyusun gerakan kas & kasPada ulang (0×)' % len(u), len(u) >= 5 and all(P(a, 'daftarGerakanKas') == 0 and P(a, 'kasPada') == 0 for a in u),
       [(a['aksi'][:40], a['panggil']) for a in u if P(a, 'daftarGerakanKas') or P(a, 'kasPada')][:2])
    return l, g


def satu_kotak(ganti=None, ulang=('mati', 'hidup', 'beku'), dasar=None):
    """Rangkaian atas kotak pasir. Kontrol: kerusakan dipasang di rangkaian `ulang`, sisanya dari `dasar` (tanpa kerusakan). Kerusakan di jalur ingatan tidak
    menyentuh rangkaian tanpa ingatan, jadi dasarnya sah; kerusakan layar dipasang di rangkaian tanpa ingatan JUGA (kesetaraan membandingkan kode yang sama)."""
    cad = kotak(); H = dict(dasar or {})
    for m in ulang:
        h, e = jalan(m, cad, JAM, TITIK_KOTAK, ganti)
        if h is None: return None, e
        H[m] = h
    return H, ''


def cadangan_toko():
    if '--cadangan' in sys.argv: return sys.argv[sys.argv.index('--cadangan') + 1]
    if os.environ.get('CADANGAN_TOKO'): return os.environ['CADANGAN_TOKO']
    c = sorted(glob.glob(os.path.join(AKAR, '_privat', 'backup-batch-*.json')) + glob.glob(os.path.join(AKAR, '_privat', '*', 'backup-batch-*.json')), key=os.path.basename)
    return c[-1] if c else None


def cad_dan_jam(p):
    d = json.load(open(p, encoding='utf-8')); kol = re.findall(r"\{ nama: '(\w+)'", open(os.path.join(AKAR, 'baru/js/data/koleksi.js'), encoding='utf-8').read())
    return dict((n, d[n]) for n in kol if isinstance(d.get(n), list)), (d.get('diunduhPada') or JAM)


RUSAK = [
    ('ingatan tidak dikosongkan saat versi cache naik (nota baru → angka basi)', 'ingatan', {'baru/js/data/toko.js': [("if (I.versi !== _versiCache) { I.isi = new Map(); I.versi = _versiCache; }", "if (I.versi === -1) { I.isi = new Map(); I.versi = _versiCache; }")]}),
    ('kunci kasPada tanpa titik kas (titik perangkat berubah → kas basi)', 'ingatan', {'baru/js/data/toko.js': [("ingatPerVersi('kasPada|' + (sampai || '') + '|' + JSON.stringify(ambilTitikKas())", "ingatPerVersi('kasPada|' + (sampai || '')")]}),
    ('kunci neraca tanpa titik kas', 'ingatan', {'baru/js/data/toko.js': [("ingatPerVersi('neraca|' + (sampai || '') + '|' + JSON.stringify(ambilTitikKas())", "ingatPerVersi('neraca|' + (sampai || '')")]}),
    ('kunci buku stok tanpa tanggal sampai', 'ingatan', {'baru/js/data/toko.js': [("ingatPerVersi('stokKarung|' + (sampai || '')", "ingatPerVersi('stokKarung|'")]}),
    ('kunci karung di belakang wadah tanpa nama wadah', 'ingatan', {'baru/js/layar/jual-logika.js': [("ingatPerVersi('karungUntukWadah|' + wadah,", "ingatPerVersi('karungUntukWadah',")]}),
    ('kunci omzet pajak tanpa bulan', 'ingatan', {'baru/js/layar/pajak-logika.js': [("ingatPerVersi('pjOmzetSistem|' + key,", "ingatPerVersi('pjOmzetSistem',")]}),
    ('rekap pajak setahun diingat tanpa HARI (bulan berganti → basi)', 'ingatan', {'baru/js/layar/pajak-logika.js': [("ingatPerVersi('pjTahun|' + th + '|' + iso,", "ingatPerVersi('pjTahun|' + th,")]}),
    ('pemanggil mengubah hasil ingatan di tempat (Stok › Gudang menulis ke buku stok bersama)', 'beku', {'baru/js/layar/stok-logika.js': [("const sisa = stokK[m].sisaKg || 0;", "const sisa = (stokK[m].sisaKg = stokK[m].sisaKg || 0);")]}),
    ('Tempat simpan kembali menyusun rantai stok per tumpukan (tanpa siap)', 'layar', {'baru/js/layar/stok-tempat-logika.js': [("const g = tumpukanGudang(b.nama, siap);", "const g = tumpukanGudang(b.nama);")]}),
    ('Dasbor ganti rentang memakai tren lama', 'layar', {'baru/js/layar/dasbor-logika.js': [("if (lama) return { hari: lama.hari, bulan: lama.bulan, stok: lama.stok, tagihan: lama.tagihan, mutu: lama.mutu, tren: aman('tren', () => dbTren(rentang, kini)) };", "if (lama) return lama;")]}),
    ('Dasbor ganti rentang menghitung seluruh dasbor lagi', 'layar', {'baru/js/layar/ringkasan.js': [("else if (dbRentang !== r) { dbHasil = susunDasbor(k, r, dbHasil); dbRentang = r; }", "else if (dbRentang !== r) { dbHasil = susunDasbor(k, r); dbRentang = r; }")]}),
    ('denyut HP kembali menyusun dasbor', 'layar', {'baru/js/layar/ringkasan.js': [("const BUKAN_DASBOR = new Set(['perangkatStatus', 'logAktivitas']);", "const BUKAN_DASBOR = new Set([]);")]}),
    ('penjualan dianggap tidak dibaca dasbor (nota baru tidak tergambar)', 'layar', {'baru/js/layar/ringkasan.js': [("const BUKAN_DASBOR = new Set(['perangkatStatus', 'logAktivitas']);", "const BUKAN_DASBOR = new Set(['perangkatStatus', 'logAktivitas', 'penjualan']);")]}),
    ('Menu menyetel keadaan simpanan walau sama (gambar ulang tiap dibuka)', 'layar', {'baru/js/layar/menu.js': [("if (Object.keys(u).length) set(u); };", "set(p); };")]}),
    ('Menu tidak pernah menyetel simpanan yang berubah', 'layar', {'baru/js/layar/menu.js': [("if (Object.keys(u).length) set(u); };", "};")]}),
    ('omzet pajak per bulan tidak diingat (Bulanan ±60 hitungan lagi)', 'ingatan', {'baru/js/layar/pajak-logika.js': [("return ingatPerVersi('pjOmzetSistem|' + key, () => pjOmzetSistemHitung(key));", "return pjOmzetSistemHitung(key);")]}),
    ('saldo kantong kembali memakai gerakan kas tanpa ingatan', 'ingatan', {'baru/js/data/toko.js': [("export function ingatGerakanKas() { return ingatPerVersi('gerakanKas', daftarGerakanKas); }", "export function ingatGerakanKas() { return daftarGerakanKas(); }")]}),
    # sanggahan 7 Okt — KUNCI LUAR: jalur 'kunci' = hanya rangkaian dengan ingatan diulang; elemen ke-4 = sebab yang WAJIB muncul di kegagalan
    ('dasbor memakai hasil lama selama HARI sama (sebelum sanggahan: tanpa jam 12 & titik kas)', 'kunci', {'baru/js/layar/ringkasan.js': [("const kunci = kunciLuarCache(k);", "const kunci = hariIniIso(k);"), ("dbKunci !== kunciLuarCache(k)", "dbKunci !== hariIniIso(k)")]}, 'KUNCI LUAR hidup'),
    ('kunci luar tanpa hari tutup aktif (jam 12 siang)', 'kunci', {'baru/js/data/toko.js': [("return hariIniIso(k) + '|' + tanggalTutupAktif(k) + '|' + JSON.stringify(ambilTitikKas());", "return hariIniIso(k) + '|' + JSON.stringify(ambilTitikKas());")]}, 'KUNCI LUAR hidup'),
    ('kunci luar tanpa titik kas perangkat', 'kunci', {'baru/js/data/toko.js': [("return hariIniIso(k) + '|' + tanggalTutupAktif(k) + '|' + JSON.stringify(ambilTitikKas());", "return hariIniIso(k) + '|' + tanggalTutupAktif(k);")]}, 'KUNCI LUAR hidup'),
    ('Menu dibuka lagi tanpa memeriksa kunci gambar (sebelum sanggahan)', 'kunci', {'baru/js/layar/menu.js': [("|| !akar.firstElementChild || _kunciGambar !== kunciGambar())) segera(gambar);", "|| !akar.firstElementChild)) segera(gambar);")]}, 'KUNCI LUAR hidup'),
    ('kunci Menu tanpa pita jam', 'kunci', {'baru/js/layar/menu.js': [("return kunciLuarCache(d) + '|' + M.mnBagianDari(d.getHours()) +", "return kunciLuarCache(d) +")]}, 'KUNCI LUAR hidup'),
    ('kunci Menu tanpa menit selagi Sistem › Perangkat terbuka', 'kunci', {'baru/js/layar/menu.js': [(" + (st().sistem === 'perangkat' ? '|' + Math.floor(d.getTime() / 60000) : '')", "")]}, 'KUNCI LUAR hidup'),
    ('Stok dibuka lagi tanpa kunci luar', 'kunci', {'baru/js/layar/stok.js': [("|| !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar);", "|| !akar.firstElementChild)) segera(gambar);")]}, 'KUNCI LUAR hidup'),
    ('Uang dibuka lagi tanpa kunci luar', 'kunci', {'baru/js/layar/uang.js': [("|| !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar);", "|| !akar.firstElementChild)) segera(gambar);")]}, 'KUNCI LUAR hidup'),
    ('Harga dibuka lagi tanpa kunci luar', 'kunci', {'baru/js/layar/harga.js': [("|| !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar);", "|| !akar.firstElementChild)) segera(gambar);")]}, 'KUNCI LUAR hidup'),
    ('Laporan dibuka lagi tanpa kunci luar', 'kunci', {'baru/js/layar/laporan.js': [("|| !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar);", "|| !akar.firstElementChild)) segera(gambar);")]}, 'KUNCI LUAR hidup'),
    ('Pelanggan dibuka lagi tanpa kunci luar', 'kunci', {'baru/js/layar/pelanggan.js': [("|| !akar.firstElementChild || _kunciLuar !== kunciLuar())) segera(gambar);", "|| !akar.firstElementChild)) segera(gambar);")]}, 'KUNCI LUAR hidup'),
    ('kunci Pelanggan tanpa jam', 'kunci', {'baru/js/layar/pelanggan.js': [("return kunciLuarCache(d) + '|' + d.getHours();", "return kunciLuarCache(d);")]}, 'KUNCI LUAR hidup'),
    ('indeks cincin tanpa tahun (tahun baru tanpa data baru)', 'kunci', {'baru/js/layar/ringkasan.js': [("if (!ix || ixTahun !== thIx)", "if (!ix)")]}, 'Cincin: indeks'),
]


def main():
    if '--kontrol' in sys.argv:
        dasar, e = satu_kotak()
        if dasar is None: print('JSC JATUH (dasar): ' + e); return 2
        diam = 0
        for x in RUSAK:
            nama, jalur, gnt = x[:3]; harap = x[3] if len(x) > 3 else None
            # jalur ingatan / kunci: hanya rangkaian dengan ingatan diulang · beku: hanya rangkaian beku · layar: tanpa & dengan ingatan diulang (beku tidak dipakai)
            ulang = {'ingatan': ('hidup',), 'kunci': ('hidup',), 'beku': ('beku',), 'layar': ('mati', 'hidup')}[jalur]
            pakai = dict((m, dasar[m]) for m in ('mati', 'hidup', 'beku') if m not in ulang and not (jalur == 'layar' and m == 'beku'))
            try: H, e = satu_kotak(gnt, ulang, pakai)
            except AssertionError as x: print('KONTROL BASI ' + nama + ' — ' + str(x)); diam += 1; continue
            if H is None: g = ['JSC JATUH: ' + e[:200]]
            else: _, g = periksa(H, 'kotak pasir')
            # harap (kontrol KUNCI LUAR): kegagalan WAJIB menyebut sebabnya — berbunyi karena hal lain = dihitung diam
            sebab = [y for y in g if not harap or harap in y]
            print(('BERBUNYI ' if sebab else 'SEBAB LAIN!' if g else 'DIAM!!   ') + nama + (' → ' + (sebab or g)[0][:170] if g else ''))
            if not sebab: diam += 1
        print('kontrol: %d/%d berbunyi' % (len(RUSAK) - diam, len(RUSAK))); return 3 if diam else 0
    H, e = satu_kotak()
    if H is None: print('LAYAR MULUS: JSC JATUH — ' + e); return 2
    l, g = periksa(H, 'kotak pasir')
    print('LAYAR MULUS (kotak pasir, %d aksi × 3 rangkaian): %d lulus · %d gagal' % (len(H['hidup']['aksi']), l, len(g)))
    for x in g: print('   ✗ ' + x)
    p = cadangan_toko()
    if p:
        cad, jam = cad_dan_jam(p); HT = {}
        for m in ('mati', 'hidup', 'beku'):
            h, e = jalan(m, cad, jam, None)
            if h is None: g.append('DATA TOKO: JSC JATUH ' + e[-300:]); break
            HT[m] = h
        if len(HT) == 3:
            lt, gt = periksa(HT, 'data toko', data_toko=True); g += gt
            ms = lambda X: sum(a['ms'] for a in X['aksi'])
            lambat = sorted(zip(HT['mati']['aksi'], HT['hidup']['aksi']), key=lambda x: -x[0]['ms'])[:8]
            print('DATA TOKO (%s): %d lulus · %d gagal · %d aksi · total %d ms tanpa ingatan → %d ms dengan ingatan · >16 ms: %d → %d' % (os.path.basename(p), lt, len(gt), len(HT['hidup']['aksi']),
                  ms(HT['mati']), ms(HT['hidup']), sum(a['ms'] > 16 for a in HT['mati']['aksi']), sum(a['ms'] > 16 for a in HT['hidup']['aksi'])))
            for a, b in lambat: print('   %6.1f → %5.1f ms  %s | %s' % (a['ms'], b['ms'], a['layar'], a['aksi'][:80]))
            for x in gt: print('   ✗ ' + x)
    else: print('DATA TOKO: dilewati — tidak ada _privat/backup-batch-*.json (worktree / CI); boleh --cadangan <berkas>')
    return 1 if g else 0


if __name__ == '__main__':
    sys.exit(main())
