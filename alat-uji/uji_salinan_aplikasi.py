#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_salinan_aplikasi.py — putaran T1 langkah 4 (owner 16 Nov 2026): tablet kasir bisa DIBUKA tanpa internet.
Yang diuji: baru/sw-baru.js (salinan aplikasi), baru/js/inti/salinan.js (sisi halaman), alat-uji/cap_sw_baru.py (cap saat terbit), sambungan app.js & pages.yml.

JSC (KOTAK PASIR: situs, berkas, CDN, dan huruf CONTOH; cache, jaringan, crypto.subtle tiruan — SHA-256 tiruan dicocokkan dengan hashlib dulu):
  · pasang versi A: SEMUA berkas diunduh melewati cache peramban (cache: 'reload'), HTML diminta sebagai text/html; modul CDN & huruf latin ikut;
    huruf subset lain TIDAK; kabar memasang → terpasang
  · aplikasi tablet: HTML bersuntikan script jembatan Capacitor tetap lolos sidik, dan yang disimpan = HTML BERSUNTIKAN (cetak tetap jalan)
  · sesudah aktif: halaman, modul, gambar ../, modul CDN, huruf disajikan dari salinan — ADA internet (isi jaringan sudah beda) maupun TIDAK;
    data toko (Firestore), POST, halaman lain di situs, alamat tak dikenal = tidak disentuh
  · versi B dengan CDN masih menyajikan berkas lama = pasang DITOLAK (kabar gagal menyebut berkasnya), salinan A tetap; sesudah CDN benar = terpasang,
    berkas yang sidiknya sama DISALIN dari salinan A (tidak diunduh ulang) kecuali HTML (selalu diunduh: jembatan milik APK yang terpasang)
  · aktif B: salinan A dihapus, halaman diklaim; 'aktifkan' = skipWaiting; tanya versi dijawab {versi, lengkap}
  · salinan yang belum dicap (isi repo) menolak dipasang; VERSI 'lepas' = hapus semua simpanan + cabut diri, tidak menyajikan apa pun
  · salinan.js: siapa yang memasang (tablet / sudah memakai / ?salinan=pasang; lepas), kapan aman (gerbang + tanpa isian + tanpa mengetik),
    kalimat jujur ("bisa dibuka tanpa internet" HANYA bila salinan lengkap sedang dipakai), jam setempat
STATIS:
  · cap_sw_baru pada repo ini: tiap berkas ada & sidiknya benar; mencakup SEMUA modul modulepreload + stylesheet + gambar ../ index.html, modul CDN,
    stylesheet huruf; tanpa .md & tanpa sw-baru.js; tanda CAP hilang = galat
  · sw-baru.js di repo TIDAK dicap; pages.yml: job terbitkan mengecap SEBELUM membungkus; uji ini & uji peramban salinan di CI
  · app.js: hanya lewat pasangSalinan dengan slPerluPasang(asliAda / dikendalikan / ?salinan); aman = gerbang tertutup + isian + mengetik; kunci
    orang mencoba memasang; index.html: modul di modulepreload, tempat kalimat & tombol ada
  · salinan.js: register('sw-baru.js') saja; muat ulang hanya untuk versi yang diminta / sesudah salinan lama (pemasangan pertama tidak)

    python3 alat-uji/uji_salinan_aplikasi.py            → N lulus · 0 gagal
    python3 alat-uji/uji_salinan_aplikasi.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, hashlib, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, cap_sw_baru  # noqa: E402
from uji_tablet_pin import POLYFILL  # noqa: E402  (SHA-256 JS yang sudah dicocokkan dengan hashlib di uji tablet)
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
SW, SL, APP, IDX, CAP, YML = 'baru/sw-baru.js', 'baru/js/inti/salinan.js', 'baru/js/app.js', 'baru/index.html', 'alat-uji/cap_sw_baru.py', '.github/workflows/pages.yml'
BERKAS_BACA = [SW, SL, APP, IDX, CAP, YML]

# ---------- situs CONTOH ----------
ASAL = 'https://contoh.test'; DASAR = ASAL + '/T/baru/'
SUNTIK = '<script type="text/javascript">window.Capacitor = { isNativePlatform: function () { return true; } }; /* jembatan contoh */</script>'
HTML_A = '<!doctype html>\n<html lang="id">\n<head>\n<meta charset="utf-8">\n<title>Contoh · versi A</title>\n</head>\n<body>contoh</body>\n</html>\n'
JS_A, JS_B = 'export const VERSI_CONTOH = "A"; // é ·\n', 'export const VERSI_CONTOH = "B"; // é ·\n'
CSS = 'body { color: #123; }\n'; PNG = 'PNG-contoh'
CDN, CDN_BARU, CDN_LAMA = 'https://cdn.test/sdk-1.0.js', 'https://cdn.test/sdk-1.1.js', 'https://cdn.test/sdk-0.9.js'; HURUF = 'https://fonts.googleapis.com/css2?family=Contoh&display=swap'
HURUF_LATIN, HURUF_LAIN = 'https://fonts.gstatic.com/s/contoh/latin.woff2', 'https://fonts.gstatic.com/s/contoh/cyrillic.woff2'
CSS_HURUF = ('/* cyrillic */\n@font-face {\n  font-family: \'Contoh\';\n  src: url(' + HURUF_LAIN + ') format(\'woff2\');\n}\n'
             '/* latin */\n@font-face {\n  font-family: \'Contoh\';\n  src: url(' + HURUF_LATIN + ') format(\'woff2\');\n}\n')
sha = lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()


def manifest(js):
    return [['index.html', sha(HTML_A)], ['js/a.js', sha(js)], ['css/b.css', sha(CSS)], ['../icon.png', sha(PNG)]]


MOCK = r"""
var __log = [], __pesan = [], __H = {}, __JARINGAN = {};
function __utf8(s) { s = String(s); var o = []; for (var i = 0; i < s.length; i++) { var c = s.codePointAt(i); if (c > 0xffff) i++;
  if (c < 0x80) o.push(c); else if (c < 0x800) o.push(0xc0 | (c >> 6), 0x80 | (c & 63)); else if (c < 0x10000) o.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
  else o.push(0xf0 | (c >> 18), 0x80 | ((c >> 12) & 63), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63)); } return new Uint8Array(o); }
function __dariUtf8(b) { var s = '', i = 0; while (i < b.length) { var c = b[i++]; if (c >= 0xf0) { c = ((c & 7) << 18) | ((b[i++] & 63) << 12) | ((b[i++] & 63) << 6) | (b[i++] & 63); }
  else if (c >= 0xe0) { c = ((c & 15) << 12) | ((b[i++] & 63) << 6) | (b[i++] & 63); } else if (c >= 0xc0) { c = ((c & 31) << 6) | (b[i++] & 63); } s += String.fromCodePoint(c); } return s; }
function __u8(x) { if (x === undefined || x === null) return new Uint8Array(0); if (typeof x === 'string') return __utf8(x); if (x instanceof Uint8Array) return new Uint8Array(x);
  if (x instanceof ArrayBuffer) return new Uint8Array(x.slice(0)); return __utf8(String(x)); }
function TextEncoder() {} TextEncoder.prototype.encode = function (s) { return __utf8(s); };
function TextDecoder() {} TextDecoder.prototype.decode = function (b) { return __dariUtf8(__u8(b)); };
var __URLRE = /^([a-z]+:)\/\/([^\/?#]+)([^?#]*)(\?[^#]*)?/;
function URL(u, dasar) {
  u = String(u); var m = __URLRE.exec(u);
  if (!m) { if (dasar === undefined) throw new TypeError('URL tidak sah: ' + u); var b = dasar instanceof URL ? dasar : new URL(String(dasar));
    var q = '', j = u.indexOf('?'); if (j >= 0) { q = u.slice(j); u = u.slice(0, j); }
    var jalur = u.charAt(0) === '/' ? u : b.pathname.slice(0, b.pathname.lastIndexOf('/') + 1) + u; var out = [];
    jalur.split('/').forEach(function (s) { if (s === '..') { if (out.length > 1) out.pop(); } else if (s !== '.') out.push(s); });
    if (/(^|\/)\.\.?$/.test(u)) out.push(''); m = __URLRE.exec(b.protocol + '//' + b.host + out.join('/') + q); }
  this.protocol = m[1]; this.host = m[2]; this.pathname = m[3] || '/'; this.search = m[4] || ''; this.origin = this.protocol + '//' + this.host; this.href = this.origin + this.pathname + this.search;
}
URL.prototype.toString = function () { return this.href; };
function Response(isi, o) { o = o || {}; this._b = __u8(isi); this.status = o.status === undefined ? 200 : o.status; this.ok = this.status >= 200 && this.status < 300;
  this.type = o.type || 'default'; var h = {}; Object.keys(o.headers || {}).forEach(function (k) { h[k.toLowerCase()] = o.headers[k]; }); this._h = h;
  this.headers = { get: function (k) { k = k.toLowerCase(); return Object.prototype.hasOwnProperty.call(h, k) ? h[k] : null; } }; }
Response.prototype.clone = function () { return new Response(this._b, { status: this.status, type: this.type, headers: this._h }); };
Response.prototype.arrayBuffer = function () { return Promise.resolve(this._b.slice(0).buffer); };
Response.prototype.text = function () { return Promise.resolve(__dariUtf8(this._b)); };
function Request(u, o) { o = o || {}; if (u instanceof Request) { o = Object.assign({ method: u.method, mode: u.mode, headers: u.headers, cache: u.cache }, o); u = u.url; }
  this.url = new URL(u, self.location.href).href; this.method = o.method || 'GET'; this.mode = o.mode || 'cors'; this.cache = o.cache || 'default'; this.headers = o.headers || {}; }
var __ASAL = '__ASAL__';
function fetch(x, o) {
  var r = x instanceof Request ? new Request(x, o) : new Request(x, o);
  __log.push({ url: r.url, accept: r.headers.Accept || '', cache: r.cache, mode: r.mode });
  var j = __JARINGAN[r.url]; if (j === undefined) return Promise.reject(new TypeError('Failed to fetch'));
  var silang = r.url.indexOf(__ASAL + '/') !== 0;
  return Promise.resolve(new Response(j.isi, { status: j.status || 200, headers: j.headers || {}, type: silang ? (r.mode === 'no-cors' ? 'opaque' : 'cors') : 'basic' }));
}
var __CACHES = new Map();
function __kunci(r) { return typeof r === 'string' ? new URL(r, self.location.href).href : r.url; }
function Cache() { this.m = new Map(); }
Cache.prototype.match = function (r) { var x = this.m.get(__kunci(r)); return Promise.resolve(x ? x.clone() : undefined); };
Cache.prototype.put = function (r, res) { this.m.set(__kunci(r), res.clone()); return Promise.resolve(); };
Cache.prototype.keys = function () { return Promise.resolve(Array.from(this.m.keys()).map(function (u) { return { url: u }; })); };
Cache.prototype.delete = function (r) { return Promise.resolve(this.m.delete(__kunci(r))); };
var caches = { open: function (n) { if (!__CACHES.has(n)) __CACHES.set(n, new Cache()); return Promise.resolve(__CACHES.get(n)); },
  keys: function () { return Promise.resolve(Array.from(__CACHES.keys())); }, delete: function (n) { return Promise.resolve(__CACHES.delete(n)); },
  match: function (r) { var k = __kunci(r); var a = Array.from(__CACHES.values()); for (var i = 0; i < a.length; i++) { var x = a[i].m.get(k); if (x) return Promise.resolve(x.clone()); } return Promise.resolve(undefined); } };
var crypto = { subtle: { digest: function (alg, isi) { return Promise.resolve(new Uint8Array(__bait32(__sha(Array.from(__u8(isi))))).buffer); } } };
var __unreg = 0;
var self = { location: { href: '__ASAL__/T/baru/sw-baru.js', origin: '__ASAL__' }, addEventListener: function (n, f) { __H[n] = f; },
  skipWaiting: function () { __log.push('skipWaiting'); return Promise.resolve(); },
  clients: { matchAll: function () { return Promise.resolve([{ url: '__ASAL__/T/baru/', postMessage: function (m) { __pesan.push(m); }, navigate: function () {} }]); },
    claim: function () { __log.push('claim'); return Promise.resolve(); } },
  registration: { unregister: function () { __unreg++; return Promise.resolve(true); } } };
function __pasang(h) { var p = null; h.install({ waitUntil: function (x) { p = x; } }); return p; }
function __aktif(h) { var p = null; h.activate({ waitUntil: function (x) { p = x; } }); return p; }
function __ambil(h, url, o) { var r = new Request(url, o); var hasil = null; h.fetch({ request: r, respondWith: function (x) { hasil = Promise.resolve(x); } });
  return hasil ? hasil.then(function (res) { return res.text().then(function (t) { return { t: t, type: res.type, ct: res.headers.get('Content-Type') }; }); }) : Promise.resolve(null); }
function __isiCache(n) { var c = __CACHES.get(n); return c ? Array.from(c.m.keys()) : []; }
"""

SKENARIO = r"""
var lulus = 0, gagal = [];
function ok(n, c, k) { if (c) lulus++; else gagal.push(n + (k === undefined ? '' : ' · ' + JSON.stringify(k).slice(0, 300))); }
function jaringanA(htmlIsi) { __JARINGAN = {}; var J = __JARINGAN;
  J[DASAR + 'index.html'] = { isi: htmlIsi, headers: { 'Content-Type': 'text/html' } }; J[DASAR + 'js/a.js'] = { isi: JS_A, headers: { 'Content-Type': 'application/javascript' } };
  J[DASAR + 'css/b.css'] = { isi: CSS, headers: { 'Content-Type': 'text/css' } }; J[ASAL + '/T/icon.png'] = { isi: PNG, headers: { 'Content-Type': 'image/png' } };
  J[CDN] = { isi: 'export const sdk = 1;' }; J[HURUF] = { isi: CSS_HURUF }; J[HURUF_LATIN] = { isi: 'latin' }; J[HURUF_LAIN] = { isi: 'cyrillic' }; }
(async function () {
  // --- fungsi murni ---
  var P = SW_MURNI;
  ok('slRelatif: berkas di folder salinan', P.slRelatif('/T/baru/', '/T/baru/js/a.js') === 'js/a.js' && P.slRelatif('/T/baru/', '/T/baru/') === '');
  ok('slRelatif: gambar satu tingkat di atas = ../', P.slRelatif('/T/baru/', '/T/icon.png') === '../icon.png' && P.slRelatif('/baru/', '/icon.png') === '../icon.png');
  ok('slRelatif: folder lain / dua tingkat / situs lain = bukan salinan', P.slRelatif('/T/baru/', '/T/lain/x.js') === null && P.slRelatif('/T/baru/', '/x.png') === null && P.slRelatif('/T/baru/', '/U/baru/x.js') === null);
  var dis = HTML_A.replace('<head>', '<head>\n' + SUNTIK);
  ok('slBuangSuntikan: HTML bersuntikan Capacitor kembali byte-sama', P.slBuangSuntikan(dis) === HTML_A, P.slBuangSuntikan(dis).slice(0, 120));
  ok('slBuangSuntikan: HTML tanpa suntikan tidak berubah', P.slBuangSuntikan(HTML_A) === HTML_A);
  ok('slHurufLatin: hanya subset latin', JSON.stringify(P.slHurufLatin(CSS_HURUF)) === JSON.stringify([HURUF_LATIN]), P.slHurufLatin(CSS_HURUF));
  // --- belum dicap ---
  __H = {}; SW_MENTAH(); var HM = __H; var tolak = '';
  try { await __pasang(HM); } catch (e) { tolak = String(e.message || e); }
  ok('salinan belum dicap (isi repo) menolak dipasang', /belum dicap/.test(tolak), tolak);
  // --- versi A, aplikasi tablet (HTML bersuntikan) ---
  jaringanA(dis); __log = []; __pesan = [];
  __H = {}; SW_A(); var HA = __H;
  var gA = ''; try { await __pasang(HA); } catch (e) { gA = String(e.message || e); }
  ok('versi A terpasang (HTML bersuntikan lolos sidik)', !gA, gA);
  var kA = __isiCache('baru-salinan-aaaa');
  ok('salinan A: 4 berkas + tanda lengkap', kA.length === 5 && kA.indexOf(ASAL + '/T/baru/__salinan-lengkap__') >= 0, kA);
  var unduh = __log.filter(function (x) { return x.url && x.url.indexOf(ASAL) === 0; });
  ok('semua berkas diunduh melewati cache peramban (cache: reload)', unduh.length === 4 && unduh.every(function (x) { return x.cache === 'reload'; }), unduh);
  ok('HTML diminta sebagai text/html (Capacitor menyuntik jembatan hanya untuk itu)', unduh.some(function (x) { return /index\.html$/.test(x.url) && /text\/html/.test(x.accept); }), unduh);
  ok('modul CDN disimpan (mode cors)', __isiCache('baru-luar-v1').indexOf(CDN) >= 0 && __log.some(function (x) { return x.url === CDN && x.mode === 'cors'; }));
  var hf = __isiCache('baru-huruf-v1');
  ok('huruf: stylesheet + subset latin disimpan, subset lain tidak', hf.indexOf(HURUF) >= 0 && hf.indexOf(HURUF_LATIN) >= 0 && hf.indexOf(HURUF_LAIN) < 0, hf);
  ok('kabar: memasang lalu terpasang', JSON.stringify(__pesan.map(function (m) { return m.jenis; })) === '["memasang","terpasang"]', __pesan);
  await __aktif(HA);
  ok('aktif A: halaman diklaim', __log.indexOf('claim') >= 0);
  // --- sajian sesudah aktif: internet ADA tapi isinya sudah beda (salinan tetap dipakai = satu versi utuh) ---
  __JARINGAN[DASAR + 'js/a.js'] = { isi: 'JARINGAN-BERUBAH' }; __JARINGAN[DASAR + 'index.html'] = { isi: 'JARINGAN-BERUBAH' };
  var nav = await __ambil(HA, DASAR, { mode: 'navigate' });
  ok('buka /baru/ = index.html dari salinan, BERSUNTIKAN (cetak jalan)', nav && nav.t === dis && /charset=utf-8/.test(nav.ct), nav);
  var navq = await __ambil(HA, DASAR + 'index.html?cadangan=x', { mode: 'navigate' });
  ok('index.html?… = index.html dari salinan', navq && navq.t === dis);
  var ma = await __ambil(HA, DASAR + 'js/a.js');
  ok('modul dari salinan walau jaringan berisi lain (tidak campur versi)', ma && ma.t === JS_A && /javascript/.test(ma.ct), ma);
  // --- tanpa internet ---
  __JARINGAN = {};
  var off = [await __ambil(HA, DASAR, { mode: 'navigate' }), await __ambil(HA, DASAR + 'js/a.js'), await __ambil(HA, DASAR + 'css/b.css'), await __ambil(HA, ASAL + '/T/icon.png'),
    await __ambil(HA, CDN), await __ambil(HA, HURUF, { mode: 'no-cors' }), await __ambil(HA, HURUF_LATIN)];
  ok('TANPA INTERNET: halaman, modul, css, gambar ../, modul CDN, huruf tersaji', off.every(function (x) { return x && x.t; }) && off[3].t === PNG && off[4].type === 'cors', off.map(function (x) { return x && x.t.slice(0, 20); }));
  var tak = [await __ambil(HA, 'https://firestore.googleapis.com/v1/projects/x'), await __ambil(HA, ASAL + '/T/kasir-darurat-nominal.html', { mode: 'navigate' }),
    await __ambil(HA, DASAR + 'js/a.js', { method: 'POST' }), await __ambil(HA, DASAR + 'js/tidak-ada.js')];
  ok('data toko, halaman lain di situs, POST, berkas di luar daftar = tidak disentuh', tak.every(function (x) { return x === null; }), tak);
  // --- versi B: CDN Pages masih menyajikan a.js lama ---
  jaringanA(dis); __JARINGAN[CDN_BARU] = { isi: 'export const sdk = 2;' }; __log = []; __pesan = [];
  (await caches.open('baru-luar-v1')).put(CDN_LAMA, new Response('export const lama = 1;', { type: 'cors' }));   // SDK versi sebelum A (contoh)
  __H = {}; SW_B(); var HB = __H;
  var gB = ''; try { await __pasang(HB); } catch (e) { gB = String(e.message || e); }
  ok('versi B dengan berkas basi DITOLAK (sidik beda)', /js\/a\.js/.test(gB) && /sidik/.test(gB), gB);
  ok('kabar gagal menyebut berkasnya', __pesan.some(function (m) { return m.jenis === 'gagal' && /js\/a\.js/.test(m.sebab); }), __pesan);
  ok('salinan B tidak ditandai lengkap', __isiCache('baru-salinan-bbbb').indexOf(ASAL + '/T/baru/__salinan-lengkap__') < 0);
  var masihA = await __ambil(HA, DASAR + 'js/a.js');
  ok('selama B gagal, A tetap utuh dipakai', masihA && masihA.t === JS_A);
  // --- CDN sudah benar → B terpasang, berkas sama disalin dari A ---
  __JARINGAN[DASAR + 'js/a.js'] = { isi: JS_B, headers: { 'Content-Type': 'application/javascript' } }; __pesan = [];   // __log TIDAK dikosongkan: dua percobaan B dinilai bersama
  var gB2 = ''; try { await __pasang(HB); } catch (e) { gB2 = String(e.message || e); }
  ok('versi B terpasang sesudah berkasnya benar', !gB2, gB2);
  var LUAR_LAMA_SAAT_PASANG = __isiCache('baru-luar-v1').indexOf(CDN_LAMA) >= 0 && __isiCache('baru-luar-v1').indexOf(CDN_BARU) >= 0;
  var u2 = __log.filter(function (x) { return x.url && x.url.indexOf(ASAL) === 0; }).map(function (x) { return x.url.replace(ASAL, ''); });
  ok('berkas bersidik sama (css, gambar) disalin dari salinan A, tidak diunduh ulang (dua percobaan B)', u2.indexOf('/T/baru/css/b.css') < 0 && u2.indexOf('/T/icon.png') < 0, u2);
  ok('HTML versi B diunduh, tidak disalin dari A (jembatan milik APK yang terpasang)', u2.indexOf('/T/baru/index.html') >= 0, u2);
  await __aktif(HB);
  ok('aktif B: salinan A dihapus', __CACHES.has('baru-salinan-bbbb') && !__CACHES.has('baru-salinan-aaaa'), Array.from(__CACHES.keys()));
  ok('aktif B: modul CDN yang tidak dipakai lagi dibuang saat AKTIF (bukan saat pasang)', LUAR_LAMA_SAAT_PASANG && __isiCache('baru-luar-v1').indexOf(CDN_LAMA) < 0 && __isiCache('baru-luar-v1').indexOf(CDN) >= 0, __isiCache('baru-luar-v1'));
  var mb = await __ambil(HB, DASAR + 'js/a.js');
  ok('sesudah B aktif: modul versi B', mb && mb.t === JS_B);
  __log = []; HB.message({ data: { jenis: 'aktifkan' } });
  ok("pesan 'aktifkan' = skipWaiting", __log.indexOf('skipWaiting') >= 0);
  var jawab = await new Promise(function (jadi) { HB.message({ data: { jenis: 'versi' }, ports: [{ postMessage: jadi }] }); });
  ok('tanya versi dijawab {versi, lengkap}', jawab && jawab.versi === 'bbbb' && jawab.lengkap === true && jawab.n === 4, jawab);
  // --- VERSI lepas ---
  __H = {}; SW_LEPAS(); var HL = __H; __log = [];
  await __pasang(HL); await __aktif(HL);
  ok("VERSI 'lepas': semua simpanan salinan dihapus & salinan mencabut diri", __CACHES.size === 0 && __unreg === 1 && __log.indexOf('skipWaiting') >= 0, Array.from(__CACHES.keys()));
  ok("VERSI 'lepas': tidak menyajikan apa pun", (await __ambil(HL, DASAR, { mode: 'navigate' })) === null);
  // --- salinan.js (sisi halaman) ---
  ok('perlu pasang: aplikasi tablet / sudah memakai salinan / ?salinan=pasang', slPerluPasang({ asli: true }) && slPerluPasang({ dikendalikan: true }) && slPerluPasang({ minta: 'pasang' }));
  ok('perlu pasang: HP/Mac biasa TIDAK; ?salinan=lepas tidak', !slPerluPasang({}) && !slPerluPasang({ asli: true, minta: 'lepas' }) && !slPerluPasang({ minta: 'apa' }));
  ok('aman: hanya gerbang tertutup, tanpa isian, tanpa mengetik', slAman({ gerbang: true, isian: 0, mengetik: false }) && !slAman({ gerbang: false, isian: 0 }) &&
     !slAman({ gerbang: true, isian: 1 }) && !slAman({ gerbang: true, isian: 0, mengetik: true }) && !slAman(null));
  var akt = { versi: 'bbbb', terbit: '2026-11-16T11:35:54Z', n: 103, lengkap: true };
  var k1 = slKalimat({ didukung: true, dipasang: true, dikendalikan: true, aktif: akt });
  ok('kalimat: salinan lengkap dipakai = bisa dibuka tanpa internet + versi jam setempat', k1 === 'Bisa dibuka tanpa internet · versi 16 Nov 18.35', k1);
  var bohong = [slKalimat({ didukung: true, dipasang: true, dikendalikan: false, aktif: akt }), slKalimat({ didukung: true, dipasang: true, dikendalikan: true, aktif: { versi: 'x', lengkap: false } }),
    slKalimat({ didukung: true, dipasang: true, dikendalikan: true, aktif: null, memasang: true })];
  ok('kalimat: TIDAK mengaku bisa tanpa internet sebelum salinan lengkap dipakai', bohong.every(function (t) { return t && !/^Bisa dibuka/.test(t); }), bohong);
  ok('kalimat: gagal menyebut sebabnya', /sidik beda/.test(slKalimat({ didukung: true, dipasang: true, gagal: 'js/a.js: isinya bukan versi ini (sidik beda)' })));
  ok('kalimat: versi baru menunggu disebut', /versi baru siap/.test(slKalimat({ didukung: true, dipasang: true, dikendalikan: true, aktif: akt, menunggu: true })));
  ok('kalimat: perangkat tanpa salinan (HP/Mac) = tanpa kalimat', slKalimat({ didukung: true, dipasang: false }) === '' && slKalimat({ didukung: false, dipasang: true }) === '');
  print(JSON.stringify({ lulus: lulus, gagal: gagal }));
})().catch(function (e) { print(JSON.stringify({ lulus: lulus, gagal: gagal.concat(['JATUH: ' + (e && e.stack || e)]) })); });
"""


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in BERKAS_BACA}
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert lama in t[b], 'kontrol basi: ' + b + ' · ' + lama[:80]
            t[b] = t[b].replace(lama, baru, 1)
    return t


def bungkus(sw_teks, nama):
    """Tiap versi salinan di lingkupnya sendiri (const VERSI dll. tidak bertabrakan); __H menangkap penangan acaranya."""
    return 'function ' + nama + '() {\n' + sw_teks + '\nreturn { slRelatif: slRelatif, slBuangSuntikan: slBuangSuntikan, slHurufLatin: slHurufLatin };\n}\n'


def jalan_jsc(t):
    nilai = lambda versi, js, luar=(CDN,): {'VERSI': versi, 'TERBIT': '2026-11-16T11:35:54Z', 'BERKAS': manifest(js), 'LUAR': list(luar), 'HURUF': HURUF}
    sw = t[SW]
    try:
        a = cap_sw_baru.cap(sw, nilai('aaaa', JS_A)); b = cap_sw_baru.cap(sw, nilai('bbbb', JS_B, (CDN, CDN_BARU))); lepas = cap_sw_baru.cap(sw, nilai('lepas', JS_A))
    except SystemExit as e:
        return 0, ['cap gagal: ' + str(e)]
    konst = ''.join('var %s = %s;\n' % (k, json.dumps(v)) for k, v in
                    {'ASAL': ASAL, 'DASAR': DASAR, 'SUNTIK': SUNTIK, 'HTML_A': HTML_A, 'JS_A': JS_A, 'JS_B': JS_B, 'CSS': CSS, 'PNG': PNG, 'CDN': CDN, 'CDN_BARU': CDN_BARU, 'CDN_LAMA': CDN_LAMA,
                     'HURUF': HURUF, 'HURUF_LATIN': HURUF_LATIN, 'HURUF_LAIN': HURUF_LAIN, 'CSS_HURUF': CSS_HURUF}.items())
    js = (POLYFILL + MOCK.replace('__ASAL__', ASAL) + konst + bungkus(sw, 'SW_MENTAH') + bungkus(a, 'SW_A') + bungkus(b, 'SW_B') + bungkus(lepas, 'SW_LEPAS')
          + 'var SW_MURNI = (function () { var self; ' + sw + '\nreturn { slRelatif: slRelatif, slBuangSuntikan: slBuangSuntikan, slHurufLatin: slHurufLatin }; })();\n'
          + bundel_baru.polos(t[SL]) + SKENARIO)
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


def periksa_statis(t, akar_cap=AKAR):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    sw, sl, app, idx, yml = t[SW], t[SL], t[APP], t[IDX], t[YML]
    # cap pada repo ini (memakai alat cap dari teks yang dibaca — kontrol bisa merusaknya)
    ruang = {'__file__': os.path.join(AKAR, CAP), '__name__': 'cap_uji'}; exec(compile(t[CAP], CAP, 'exec'), ruang)
    try: n = ruang['susun'](akar_cap, 'uji-cap', '2026-11-16T00:00:00Z'); galat = ''
    except SystemExit as e: n = None; galat = str(e)
    ok('cap_sw_baru menyusun daftar repo ini', n and not galat, galat)
    if n:
        jalur = dict(n['BERKAS']); baru = os.path.join(akar_cap, 'baru')
        salah = [r for r, s in n['BERKAS'] if not os.path.isfile(os.path.normpath(os.path.join(baru, r))) or cap_sw_baru.sidik(os.path.normpath(os.path.join(baru, r))) != s]
        ok('tiap berkas daftar ada & sidiknya benar', not salah, salah[:5])
        pre = re.findall(r'<link rel="modulepreload" href="(js/[^"]+)"', idx); css = re.findall(r'<link rel="stylesheet" href="(css/[^"]+)"', idx)
        gambar = re.findall(r'<link rel="(?:icon|apple-touch-icon)" href="(\.\./[^"]+)"', idx)
        kurang = [x for x in ['index.html', 'uji-cetak.html'] + pre + css + gambar if x not in jalur]
        ok('mencakup index.html, uji-cetak.html, SEMUA modul modulepreload, stylesheet & gambar ../ (' + str(len(pre)) + ' modul, ' + str(len(css)) + ' css)', not kurang and len(pre) > 50, kurang)
        semua_js = [os.path.relpath(p, baru) for p in __import__('glob').glob(os.path.join(baru, 'js', '**', '*.js'), recursive=True)]
        ok('mencakup SEMUA modul baru/js (impor dinamis pun aman)', all(x in jalur for x in semua_js), [x for x in semua_js if x not in jalur][:5])
        ok('tanpa .md & tanpa sw-baru.js', not any(r.endswith('.md') or r.endswith('sw-baru.js') for r in jalur))
        cdn = re.findall(r'<link rel="modulepreload" href="(https://www\.gstatic\.com/[^"]+)"', idx)
        ok('modul Firebase CDN = modulepreload gstatic (' + str(len(cdn)) + ')', sorted(n['LUAR']) == sorted(cdn) and len(cdn) == 3, n['LUAR'])
        ok('stylesheet huruf ikut', n['HURUF'].startswith('https://fonts.googleapis.com/css2?') and '&amp;' not in n['HURUF'], n['HURUF'][:60])
    try: ruang['cap']('const VERSI = 1;', {'VERSI': 'x'}); ok('tanda CAP hilang = galat', False)
    except SystemExit: ok('tanda CAP hilang = galat', True)
    ok('sw-baru.js di repo TIDAK dicap (yang dicap hanya yang tayang)', "const VERSI = 'belum-dicap';   // CAP:VERSI" in sw and 'const BERKAS = [];   // CAP:BERKAS' in sw)
    ter = yml.split('\n  terbitkan:', 1)[1] if '\n  terbitkan:' in yml else ''
    i_cap = ter.find('python3 alat-uji/cap_sw_baru.py --tulis'); i_bungkus = ter.find('actions/upload-pages-artifact')
    ok('pages.yml: job terbitkan mengecap salinan SEBELUM membungkus folder', 0 <= i_cap < i_bungkus, (i_cap, i_bungkus))
    ok('pages.yml: uji ini + kontrol di job uji; uji peramban salinan + kontrol di job uji-peramban',
       'python3 alat-uji/uji_salinan_aplikasi.py && python3 alat-uji/uji_salinan_aplikasi.py --kontrol' in yml
       and 'python3 -u alat-uji/uji_salinan_peramban.py && python3 -u alat-uji/uji_salinan_peramban.py --kontrol' in yml.split('\n  uji-peramban:', 1)[-1].split('\n  terbitkan:', 1)[0])
    ok('app.js: salinan hanya lewat pasangSalinan + slPerluPasang(asliAda / dikendalikan / ?salinan)',
       "perlu: SL.slPerluPasang({ asli: asliAda(), dikendalikan: !!(navigator.serviceWorker && navigator.serviceWorker.controller), minta: q.get('salinan') })," in app
       and app.count('serviceWorker.register') == 0)
    ok('app.js: aman = gerbang tertutup + isian + mengetik', 'aman: () => SL.slAman({ gerbang: !bisaBekerja(akunKini()), isian: isianBelum().length, mengetik: sedangMengetik() }),' in app)
    ok('app.js: kembali ke "Siapa yang jaga?" mencoba memasang versi baru', re.search(r"function kunciOrang\(\) \{[^}]*\n  gambarAkun\(akunAsli\(\)\);\n  setTimeout\(cobaSalinan, 0\);", app))
    ok('index.html: salinan.js di modulepreload; tempat kalimat & tombol ada',
       '<link rel="modulepreload" href="js/inti/salinan.js">' in idx and all('id="' + i + '"' in idx for i in ('salinanGerbang', 'salinanKet', 'tombolSalinan')))
    ok("salinan.js: hanya register('sw-baru.js')", re.findall(r"\.register\(([^)]*)\)", sl) == ["'sw-baru.js'"], re.findall(r"\.register\(([^)]*)\)", sl))
    ok('salinan.js: muat ulang hanya untuk versi yang diminta / sesudah salinan lama (pemasangan pertama tidak)', 'if ((diminta || awalDikendalikan) && !muat) {' in sl)
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('__jsc', not g, l)]
    return out


KONTROL = [
    ('sidik tidak dicocokkan (berkas basi diterima)', {SW: [("if ((await sidikDari(dicek)) !== sidik)", "if (false)")]}, ('jsc',)),
    ('suntikan Capacitor tidak dibuang (tablet tidak pernah terpasang)', {SW: [("return String(html).replace(", "return String(html); void (")]}, ('jsc',)),
    ('jaringan dulu, salinan belakangan (campur versi saat online)', {SW: [("const c = await caches.open(NAMA); const ada = await c.match(kunci);\n    return ada || fetch(r);",
                                                                       "try { const n = await fetch(r); if (n.ok) return n; } catch (x) { /* jatuh ke salinan */ }\n    const c = await caches.open(NAMA); const ada = await c.match(kunci);\n    return ada || fetch(r);")]}, ('jsc',)),
    ('HTML ikut disalin dari versi lama (jembatan APK basi)', {SW: [("if (!html) { const lama = await caches.match(kunci);", "if (true) { const lama = await caches.match(kunci);")]}, ('jsc',)),
    ('modul CDN lama dibuang saat pasang (versi lama tanpa internet patah)', {SW: [("      await c.put(u, r);\n    });\n  };", "      await c.put(u, r);\n    });\n    const ada = await c.keys(); await Promise.all(ada.filter((k) => !LUAR_ADA.has(k.url)).map((k) => c.delete(k)));\n  };")]}, ('jsc',)),
    ('salinan lama tidak dihapus saat aktif', {SW: [("await Promise.all(ks.filter((k) => k.indexOf(AWALAN) === 0 && k !== NAMA).map((k) => caches.delete(k)));", "")]}, ('jsc',)),
    ('unduhan memakai cache peramban', {SW: [("fetch(new Request(alamat, { cache: 'reload',", "fetch(new Request(alamat, { cache: 'default',")]}, ('jsc',)),
    ('gambar ../ tidak dikenali', {SW: [("if (induk && jalur.indexOf(induk) === 0", "if (false && jalur.indexOf(induk) === 0")]}, ('jsc',)),
    ('salinan mentah ikut dipasang', {SW: [("if (!BERKAS.length) throw new Error('salinan belum dicap (bukan terbitan)');", "")]}, ('jsc',)),
    ('aman tanpa melihat isian', {SL: [("return !!x.gerbang && !(x.isian > 0) && !x.mengetik;", "return !!x.gerbang && !x.mengetik;")]}, ('jsc',)),
    ('kalimat mengaku bisa tanpa internet sebelum lengkap', {SL: [("if (!s.dikendalikan || !s.aktif || !s.aktif.lengkap) {", "if (!s.aktif) {")]}, ('jsc',)),
    ('HP/Mac owner ikut memasang', {SL: [("return !!(x.asli || x.dikendalikan || x.minta === 'pasang');", "return true;")]}, ('jsc',)),
    ('cap melewatkan css', {CAP: [("os.path.join(baru, 'css', '**', '*.css'), ", "")]}, ('statis',)),
    ('job terbitkan tidak mengecap', {YML: [("python3 alat-uji/cap_sw_baru.py --tulis", "true")]}, ('statis',)),
    ('sw-baru.js tercap ikut di-commit', {SW: [("const VERSI = 'belum-dicap';   // CAP:VERSI", "const VERSI = 'abc123';   // CAP:VERSI")]}, ('statis',)),
    ('muat ulang juga di pemasangan pertama', {SL: [("if ((diminta || awalDikendalikan) && !muat) {", "if (!muat) {")]}, ('statis',)),
    ('kunci orang tidak mencoba memasang', {APP: [("  setTimeout(cobaSalinan, 0);   // T1-4", "  // T1-4")]}, ('statis',)),
]


def main():
    if '--kontrol' in sys.argv:
        diam = []
        for nama, ganti, bagian in KONTROL:
            hasil = semua(ganti, bagian); bunyi = any(not c for _, c, _ in hasil)
            print(('  tertangkap: ' if bunyi else '  DIAM     : ') + nama)
            if not bunyi: diam.append(nama)
        print('KONTROL ' + ('LULUS' if not diam else 'GAGAL') + ' ' + str(len(KONTROL) - len(diam)) + '/' + str(len(KONTROL)))
        sys.exit(3 if diam else 0)
    hasil = semua(); gagal = [(n, k) for n, c, k in hasil if not c]
    n_jsc = next((k for n, c, k in hasil if n == '__jsc'), 0)
    for n, c, k in hasil:
        if n == '__jsc': continue
        print(('  ok  ' if c else 'GAGAL ') + n + ('' if c or not k else ' · ' + str(k)[:300]))
    total = sum(1 for n, _, _ in hasil if n != '__jsc') + (n_jsc or 0)
    print(('LULUS ' if not gagal else 'GAGAL ') + str(total - len(gagal)) + ' lulus · ' + str(len(gagal)) + ' gagal (jsc ' + str(n_jsc) + ')')
    sys.exit(1 if gagal else 0)


if __name__ == '__main__':
    main()
