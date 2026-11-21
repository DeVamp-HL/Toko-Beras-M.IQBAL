#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_tablet_pin.py — putaran T1 langkah 3: SATU AKUN TABLET + PIN PER ORANG (baru/js/layar/tablet-logika.js).

Keputusan owner 16 Nov 2026 yang dijaga di sini:
  · salah PIN 5 kali → nama itu terkunci 5 menit (orang lain tetap bisa masuk)
  · tidak disentuh 5 menit → kembali ke "Siapa yang jaga?"
  · modal boleh tersimpan di tablet asal tidak tampil di layar staf (tidak ada ubahan pendengar / rules di putaran ini)
  · owner di tablet jualan saja pakai PIN (orang di tablet berperan ben/karyawan — tidak pernah owner)

KOTAK PASIR (nama contoh, PIN contoh) di jsc. crypto.subtle peramban diganti PBKDF2-HMAC-SHA256 JS yang DICOCOKKAN dengan hashlib Python dulu.
JSC:
  · PBKDF2 pengganti = hashlib.pbkdf2_hmac; PIN 4–6 angka, bukan kembar / urutan
  · hitungan salah per orang: 4 salah belum terkunci, salah ke-5 terkunci 5 menit, lewat 5 menit bersih; PIN benar membersihkan
  · keadaan gerbang: owner / tanpa daftar = tanpa PIN; daftar ada (meski semua libur) = wajib PIN; daftar belum datang = memuat
  · akun efektif: nama & peran orang, uid akun tablet; peran tidak pernah melebihi akun tablet; menunggu orang = tidak bisa bekerja
  · owner: tambah / ganti PIN / libur / peran / hapus menulis SATU dokumen aturanToko/peran; kolom lain (kisi hak, jatah nego) utuh; PIN tidak pernah
    tersimpan apa adanya (hanya PBKDF2 = hashlib); nama kembar, PIN lemah, ulangan beda, peran owner ditolak
  · memutar hak SS2 / mengubah jatah nego TIDAK menghapus orang di tablet (dokumen peran ditimpa utuh tiap disimpan)
  · bentuk tidak sah ditolak (ssBersihkanOrangTablet)
  · catatan baru di tablet: oleh = orang yang jaga, olehUid = akun tablet, operatorId ikut; ubahan tidak menambah kolom pencipta
STATIS:
  · firebase.js: penulis pusat & pemegang denyut memakai orang yang jaga (akunPenulis); app.js menyetelnya, kunci diam memakai tbHarusKunci
  · index.html: panel "Siapa yang jaga?" ada, modulnya di modulepreload

    python3 alat-uji/uji_tablet_pin.py            → N lulus · 0 gagal
    python3 alat-uji/uji_tablet_pin.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, hashlib, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru, peta_akses  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
MODUL = peta_akses.MODUL_KIRIM + ['baru/js/layar/bon-pemasok-logika.js', 'baru/js/layar/sistem-logika.js', 'baru/js/layar/tablet-logika.js']
STATIS = ['baru/js/data/firebase.js', 'baru/js/app.js', 'baru/index.html', 'baru/js/layar/menu.js', 'baru/css/gerbang.css', 'baru/js/data/akses.js', 'baru/js/layar/sistem-logika.js', 'baru/css/identitas.css']
JAM = "var __KINI = new Date('2026-11-16T10:00:00+07:00').getTime(); Date.now = function () { return __KINI; };\n"

# garam dari acak tetap (16 bait 0x01..0x10) — sama dengan getRandomValues pengganti di bawah
GARAM_UJI = 'g' + bytes(range(1, 17)).hex()
def pbkdf2(pin, garam, n=100000): return hashlib.pbkdf2_hmac('sha256', pin.encode(), garam.encode(), n).hex()
HASH = {'2580': pbkdf2('2580', GARAM_UJI), '7319': pbkdf2('7319', GARAM_UJI), 'kecil': pbkdf2('4826', 'g' + '0' * 32, 10000)}

# PBKDF2-HMAC-SHA256 untuk jsc (peramban: crypto.subtle). Status HMAC dalam/luar dihitung sekali per kunci → 2 kompresi per putaran.
POLYFILL = r"""
var __K = new Int32Array([0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2]);
var __W = new Int32Array(64);
function __kompres(H, blok) {   // H: Int32Array(8) diubah di tempat; blok: Int32Array(16)
  var w = __W, t; for (t = 0; t < 16; t++) w[t] = blok[t];
  for (t = 16; t < 64; t++) { var a1 = w[t - 15], a2 = w[t - 2]; w[t] = (w[t - 16] + (((a1 >>> 7) | (a1 << 25)) ^ ((a1 >>> 18) | (a1 << 14)) ^ (a1 >>> 3)) + w[t - 7] + (((a2 >>> 17) | (a2 << 15)) ^ ((a2 >>> 19) | (a2 << 13)) ^ (a2 >>> 10))) | 0; }
  var a = H[0], b = H[1], c = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
  for (t = 0; t < 64; t++) { var t1 = (h + (((e >>> 6) | (e << 26)) ^ ((e >>> 11) | (e << 21)) ^ ((e >>> 25) | (e << 7))) + ((e & f) ^ (~e & g)) + __K[t] + w[t]) | 0;
    var t2 = ((((a >>> 2) | (a << 30)) ^ ((a >>> 13) | (a << 19)) ^ ((a >>> 22) | (a << 10))) + ((a & b) ^ (a & c) ^ (b & c))) | 0; h = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0; }
  H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + c) | 0; H[3] = (H[3] + d) | 0; H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
}
var __H0 = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
function __sha(bait) {   // bait: array angka → Int32Array(8)
  var b = Array.prototype.slice.call(bait); var l = b.length * 8; b.push(0x80); while (b.length % 64 !== 56) b.push(0);
  for (var s = 56; s >= 0; s -= 8) b.push(s >= 32 ? 0 : (l >>> s) & 0xff);
  var H = new Int32Array(__H0), blok = new Int32Array(16);
  for (var o = 0; o < b.length; o += 64) { for (var i = 0; i < 16; i++) blok[i] = (b[o + 4 * i] << 24) | (b[o + 4 * i + 1] << 16) | (b[o + 4 * i + 2] << 8) | b[o + 4 * i + 3]; __kompres(H, blok); }
  return H;
}
function __bait32(H) { var u = []; for (var i = 0; i < 8; i++) u.push((H[i] >>> 24) & 255, (H[i] >>> 16) & 255, (H[i] >>> 8) & 255, H[i] & 255); return u; }
function __pbkdf2(kunci, garam, n) {
  var k = Array.prototype.slice.call(kunci); if (k.length > 64) k = __bait32(__sha(k)); while (k.length < 64) k.push(0);
  var ip = new Int32Array(16), op = new Int32Array(16);
  for (var i = 0; i < 16; i++) { var x = (k[4 * i] << 24) | (k[4 * i + 1] << 16) | (k[4 * i + 2] << 8) | k[4 * i + 3]; ip[i] = x ^ 0x36363636; op[i] = x ^ 0x5c5c5c5c; }
  var HI = new Int32Array(__H0), HO = new Int32Array(__H0); __kompres(HI, ip); __kompres(HO, op);   // status sesudah blok kunci
  function hmacPanjang(pesan) { var H = new Int32Array(HI); var b = Array.prototype.slice.call(pesan); var l = (64 + b.length) * 8; b.push(0x80); while ((b.length + 64) % 64 !== 56) b.push(0);
    for (var s = 56; s >= 0; s -= 8) b.push(s >= 32 ? 0 : (l >>> s) & 0xff); var blok = new Int32Array(16);
    for (var o = 0; o < b.length; o += 64) { for (var j = 0; j < 16; j++) blok[j] = (b[o + 4 * j] << 24) | (b[o + 4 * j + 1] << 16) | (b[o + 4 * j + 2] << 8) | b[o + 4 * j + 3]; __kompres(H, blok); }
    return luar(H); }
  var bl = new Int32Array(16); bl[8] = 0x80000000 | 0; bl[15] = (64 + 32) * 8;   // blok 32 bait + padding (sesudah 64 bait kunci)
  function luar(H) { var B = new Int32Array(HO); for (var j = 0; j < 8; j++) bl[j] = H[j]; __kompres(B, bl); return B; }
  function hmac32(U) { var H = new Int32Array(HI); for (var j = 0; j < 8; j++) bl[j] = U[j]; __kompres(H, bl); return luar(H); }
  var U = hmacPanjang(Array.prototype.slice.call(garam).concat([0, 0, 0, 1])); var T = new Int32Array(U);
  for (var r = 1; r < n; r++) { U = hmac32(U); for (var j = 0; j < 8; j++) T[j] ^= U[j]; }
  return new Uint8Array(__bait32(T)).buffer;
}
var __subtle = { importKey: function (fmt, data, alg) { return Promise.resolve({ __bait: Array.prototype.slice.call(data), alg: alg }); },
  deriveBits: function (p, k, bit) { if (p.name !== 'PBKDF2' || p.hash !== 'SHA-256' || bit !== 256) return Promise.reject(new Error('parameter PBKDF2 tidak dikenal'));
    return Promise.resolve(__pbkdf2(k.__bait, Array.prototype.slice.call(p.salt), p.iterations)); } };
var crypto = { subtle: __subtle, getRandomValues: function (u) { for (var i = 0; i < u.length; i++) u[i] = i + 1; return u; } };
"""

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(ket).slice(0, 400) : '')); }
var W = { tanggal: '2026-11-16', jam: '10:00', kini: '2026-11-16T03:00:00.000Z', idUnik: function () { return 1; } };
var KINI = Date.now();
var OWN = keadaanAkun('owner@tokoberasmiqbal.web.app', 'uid-owner', null);
var TAB = keadaanAkun('tablet.contoh@tokoberasmiqbal.web.app', 'uid-tablet', { uid: 'uid-tablet', nama: 'Tablet Contoh', peran: 'ben', aktif: true });
var TAB_K = keadaanAkun('tablet2.contoh@tokoberasmiqbal.web.app', 'uid-tablet2', { uid: 'uid-tablet2', nama: 'Tablet Dua', peran: 'karyawan', aktif: true });
var MATI = keadaanAkun('mati.contoh@tokoberasmiqbal.web.app', 'uid-mati', { uid: 'uid-mati', nama: 'Mati', peran: 'ben', aktif: false });
var KISI = { ben: { jualTunai: 'sendiri', nego: 'owner' }, karyawan: { jualTunai: 'sendiri', jualBon: 'owner' } };
function dokPeran() { return (cacheMentah('aturan').find(function (d) { return String(d.id) === 'peran'; }) || {}); }
(async function () {
  try {
    // ---- 0 · PBKDF2 pengganti = hashlib
    ok('PBKDF2-SHA256 pengganti di jsc = hashlib Python (10.000 putaran)', (await tbTurunkan('4826', 'g' + '00000000000000000000000000000000', 10000)) === HASH.kecil, await tbTurunkan('4826', 'g' + '00000000000000000000000000000000', 10000));
    ok('keputusan owner 16 Nov: salah 5 kali, terkunci 5 menit, kunci diam 5 menit; PBKDF2 100.000 putaran; paling banyak 12 orang',
      TB_BATAS_SALAH === 5 && TB_LAMA_KUNCI_MS === 300000 && TB_LAMA_DIAM_MS === 300000 && TB_ITERASI === 100000 && TB_MAKS_ORANG === 12);
    ok('garam = "g" + 32 hex dari pembangkit acak', tbGaram() === GARAM_UJI, tbGaram());
    // ---- 1 · PIN sah
    var sah = function (p) { return tbPinSah(p) === ''; };
    ok('PIN 4–6 angka; bukan kembar semua; bukan urutan naik/turun', sah('2580') && sah('135790') && sah('7319') && !sah('123') && !sah('1234567') && !sah('12a4') && !sah('0000') && !sah('777777')
      && !sah('1234') && !sah('9876') && !sah('8901') && !sah('3210') && !sah(''), [tbPinSah('1234'), tbPinSah('0000'), tbPinSah('12a4')].join(' | '));
    // ---- 2 · hitungan salah per orang
    var P = {}; for (var i = 0; i < 4; i++) P = tbCatatSalah(P, 'oani1', KINI);
    var s4 = tbStatusSalah(P, 'oani1', KINI);
    ok('4 salah: belum terkunci, hitungan 4; orang lain tidak ikut', !s4.terkunci && s4.salah === 4 && tbStatusSalah(P, 'obudi1', KINI).salah === 0, J(s4));
    P = tbCatatSalah(P, 'oani1', KINI); var s5 = tbStatusSalah(P, 'oani1', KINI);
    ok('salah ke-5: terkunci 5 menit', s5.terkunci && s5.sisaMs === 300000, J(s5));
    ok('selagi terkunci, salah lagi tidak memperpanjang', J(tbCatatSalah(P, 'oani1', KINI + 60000)) === J(P));
    var lewat = tbStatusSalah(P, 'oani1', KINI + 300000);
    ok('lewat 5 menit: bersih lagi (hitungan dari nol)', !lewat.terkunci && lewat.salah === 0 && tbStatusSalah(tbCatatSalah(P, 'oani1', KINI + 300001), 'oani1', KINI + 300001).salah === 1, J(lewat));
    ok('kunci diam: 4:59 belum, 5:00 sudah', !tbHarusKunci(KINI, KINI + 299999) && tbHarusKunci(KINI, KINI + 300000));
    // ---- 3 · keadaan gerbang & akun efektif
    var D1 = [{ id: 'oani1', nama: 'Ani Contoh', peran: 'karyawan', aktif: true }];
    ok('gerbang: owner = tanpa PIN; akun tablet + daftar = wajib PIN; nonaktif = tanpa gerbang (tirai akun yang menutup)',
      tbKeadaan(OWN, D1, true) === 'bukan' && tbKeadaan(TAB, D1, false) === 'pilih' && tbKeadaan(MATI, D1, true) === 'bukan');
    ok('gerbang: daftar belum datang = memuat; daftar kosong sesudah termuat = akun staf biasa', tbKeadaan(TAB, [], false) === 'muat' && tbKeadaan(TAB, [], true) === 'bukan');
    ok('gerbang: semua orang libur tetap wajib PIN (owner meliburkan semua tidak membuka tablet)', tbKeadaan(TAB, [{ id: 'oani1', nama: 'Ani Contoh', peran: 'karyawan', aktif: false }], true) === 'pilih');
    var E = tbEfektif(TAB, D1[0]);
    ok('akun efektif: nama & peran orang, uid & email akun tablet, kode orang ikut; bisa bekerja', E.nama === 'Ani Contoh' && E.peran === 'karyawan' && E.uid === 'uid-tablet' && E.email === TAB.email
      && E.operatorId === 'oani1' && E.akunNama === 'Tablet Contoh' && bisaBekerja(E) && teksMasukSebagai(E) === 'Ani Contoh (Karyawan)', J(E));
    ok('peran orang tidak pernah melebihi akun tablet: orang Ben di akun tablet karyawan = karyawan', tbEfektif(TAB_K, { id: 'oben1', nama: 'Ben Contoh', peran: 'ben' }).peran === 'karyawan'
      && tbEfektif(TAB, { id: 'oben1', nama: 'Ben Contoh', peran: 'ben' }).peran === 'ben');
    var M = tbMenunggu(TAB, 'pilih');
    ok('menunggu orang: TIDAK bisa bekerja (tirai menutup), uid tetap', M.jenis === 'pilihOrang' && !bisaBekerja(M) && M.uid === 'uid-tablet' && tbMenunggu(TAB, 'muat').kalimat === 'Memuat daftar orang…', J(M));
    // ---- 4 · owner menambah orang (dokumen aturanToko/peran, kolom lain utuh)
    pasok('aturanToko', [{ id: 'peran', hak: KISI, batasSekaligus: 250000, jatahBen: 40, jejak: [{ tanggal: '2026-11-01', jam: '08:00', teks: 'contoh' }] }]);
    var T1 = await tbSusunTambah({ nama: 'Ani Contoh', peran: 'karyawan', pin: '2580', pin2: '2580' }, W, { id: 'oani1' });
    var d1 = T1.dokumen ? T1.dokumen[0] : {};
    ok('tambah: SATU dokumen aturanToko/peran', !T1.tolak && T1.dokumen.length === 1 && d1.koleksi === 'aturanToko' && d1.data.id === 'peran', J(T1).slice(0, 300));
    var o1 = (d1.data && d1.data.operator || {}).oani1 || {};
    ok('tambah: PIN tersimpan hanya sebagai PBKDF2 (= hashlib), garam acak, 100.000 putaran; PIN-nya sendiri TIDAK ada', o1.acak === HASH['2580'] && o1.garam === GARAM_UJI && o1.iterasi === 100000
      && !/2580/.test(J(d1)) && !/"pin"/.test(J(d1)), J(o1));
    ok('tambah: kisi hak, batas sekaligus, jatah nego, jejak TIDAK hilang', d1.data.hak.ben.nego === 'owner' && d1.data.batasSekaligus === 250000 && d1.data.jatahBen === 40 && d1.data.jejak.length === 1, J(d1.data).slice(0, 300));
    terapkanKeCache(T1.dokumen);
    ok('daftar dari dokumen: 1 orang, aktif, Karyawan', J(tbDaftar().map(function (o) { return [o.id, o.nama, o.peran, o.aktif]; })) === J([['oani1', 'Ani Contoh', 'karyawan', true]]), J(tbDaftar()));
    ok('tambah ditolak: nama kembar (huruf besar/kecil), PIN lemah, ulangan beda, peran owner',
      /sudah ada/.test((await tbSusunTambah({ nama: 'ani contoh', peran: 'ben', pin: '7319', pin2: '7319' }, W)).tolak || '')
      && /berurutan/.test((await tbSusunTambah({ nama: 'Budi Contoh', peran: 'ben', pin: '1234', pin2: '1234' }, W)).tolak || '')
      && /tidak sama/.test((await tbSusunTambah({ nama: 'Budi Contoh', peran: 'ben', pin: '7319', pin2: '7318' }, W)).tolak || '')
      && /Pilih perannya/.test((await tbSusunTambah({ nama: 'Budi Contoh', peran: 'owner', pin: '7319', pin2: '7319' }, W)).tolak || ''));
    // ---- 5 · memutar hak / jatah nego tidak menghapus orang di tablet
    var R = susunPutarHak('karyawan', 'jualTunai', W);
    ok('putar hak SS2: orang di tablet ikut utuh', !R.tolak && J(R.dokumen[0].data.operator) === J(dokPeran().operator), J(R).slice(0, 300));
    var R2 = susunAturSistem('peran', { jatahBen: 35 }, W);
    ok('ubah jatah nego: orang di tablet ikut utuh', !R2.tolak && R2.dokumen[0].data.operator.oani1.acak === HASH['2580'], J(R2).slice(0, 300));
    // ---- 6 · periksa PIN
    var A = tbDaftar()[0];
    var r1 = await tbPeriksa(A, '2580', { oani1: { n: 3, sampai: 0 } }, KINI);
    ok('PIN benar: masuk, hitungan salah orang itu bersih', r1.ok && !r1.peta.oani1, J(r1));
    var r2 = await tbPeriksa(A, '2581', {}, KINI);
    ok('PIN salah: ditolak, sisa 4 kali', !r2.ok && r2.peta.oani1.n === 1 && /sisa 4 kali/.test(r2.kalimat), J(r2));
    var Pk = {}; for (i = 0; i < 5; i++) Pk = (await tbPeriksa(A, '1111', Pk, KINI)).peta;
    var r3 = await tbPeriksa(A, '2580', Pk, KINI + 1000);
    ok('5 salah → terkunci: PIN benar pun ditolak selama 5 menit', !r3.ok && /terkunci/.test(r3.kalimat) && tbStatusSalah(Pk, 'oani1', KINI).terkunci, J(r3));
    ok('lewat 5 menit: PIN benar masuk lagi', (await tbPeriksa(A, '2580', Pk, KINI + 300000)).ok);
    // ---- 7 · ganti PIN · libur · peran · hapus
    var G = await tbSusunGantiPin('oani1', '7319', '7319', W); terapkanKeCache(G.dokumen); A = tbDaftar()[0];
    ok('ganti PIN: PIN lama tidak berlaku, PIN baru masuk; PIN tidak tersimpan', !G.tolak && !(await tbPeriksa(A, '2580', {}, KINI)).ok && (await tbPeriksa(A, '7319', {}, KINI)).ok && !/7319/.test(J(G.dokumen)), J(G).slice(0, 200));
    var L = tbSusunAktif('oani1', false, W); terapkanKeCache(L.dokumen); A = tbDaftar()[0];
    var rl = await tbPeriksa(A, '7319', {}, KINI);
    ok('libur: nama tetap di daftar, tidak bisa masuk, hitungan salah tidak bertambah', !L.tolak && A.aktif === false && !rl.ok && /libur/.test(rl.kalimat) && J(rl.peta) === '{}', J(rl));
    var Pr = tbSusunPeran('oani1', 'ben', W); terapkanKeCache(Pr.dokumen);
    ok('ubah peran: Ben; peran owner ditolak', !Pr.tolak && tbDaftar()[0].peran === 'ben' && /tidak dikenal/.test(tbSusunPeran('oani1', 'owner', W).tolak || ''));
    var Hp = tbSusunHapus('oani1', W);
    ok('hapus orang terakhir: daftar kosong, kalimat menyebut tablet kembali TANPA PIN', !Hp.tolak && J(Hp.dokumen[0].data.operator) === '{}' && /TANPA PIN/.test(Hp.patch.kabar), J(Hp).slice(0, 200));
    // ---- 8 · bentuk tidak sah ditolak
    var baik = { nama: 'Ani Contoh', peran: 'karyawan', aktif: true, garam: GARAM_UJI, acak: HASH['2580'], iterasi: 100000 };
    var ubah = function (k, v) { var o = JSON.parse(J(baik)); o[k] = v; return o; };
    ok('bentuk sah diterima apa adanya', !ssBersihkanOrangTablet({ oani1: baik }).tolak);
    ok('bentuk tidak sah ditolak: kode, nama pendek, peran owner, acak bukan hex-64, PIN terbuka tanpa acak, putaran < 10.000, nama kembar, > 12 orang',
      !!ssBersihkanOrangTablet({ 'ani': baik }).tolak && !!ssBersihkanOrangTablet({ oani1: ubah('nama', 'A') }).tolak && !!ssBersihkanOrangTablet({ oani1: ubah('peran', 'owner') }).tolak
      && !!ssBersihkanOrangTablet({ oani1: ubah('acak', '2580') }).tolak && !!ssBersihkanOrangTablet({ oani1: ubah('acak', '') }).tolak && !!ssBersihkanOrangTablet({ oani1: ubah('iterasi', 5000) }).tolak
      && !!ssBersihkanOrangTablet({ oani1: baik, oani2: ubah('nama', 'ANI CONTOH') }).tolak
      && !!ssBersihkanOrangTablet((function () { var o = {}; for (var j = 0; j < 13; j++) o['oorang' + j] = ubah('nama', 'Orang ' + j); return o; })()).tolak);
    ok('bentuk dibersihkan: kolom asing (mis. pin) tidak ikut tertulis', !('pin' in ssBersihkanOrangTablet({ oani1: Object.assign({ pin: '2580' }, baik) }).peta.oani1));
    // ---- 9 · atribusi catatan dari tablet
    var EK = tbEfektif(TAB, { id: 'oani1', nama: 'Ani Contoh', peran: 'karyawan' });
    var baru = beriAtribusiAkun({ id: 'n1', hargaTotal: 1000 }, EK, { perangkat: 'Tablet toko', kini: W.kini }, false);
    ok('catatan BARU: oleh = orang yang jaga, olehUid = akun tablet, operatorId ikut', baru.oleh === 'Ani Contoh' && baru.olehUid === 'uid-tablet' && baru.operatorId === 'oani1' && baru.diubahOleh === 'Ani Contoh', J(baru));
    var ubahan = beriAtribusiAkun({ id: 'p1', status: 'dibayar' }, EK, { perangkat: 'Tablet toko', kini: W.kini }, true);
    ok('UBAHAN (kolom dibatasi rules): tanpa kolom pencipta & tanpa operatorId; diubahOleh = orang yang jaga', !('oleh' in ubahan) && !('operatorId' in ubahan) && ubahan.diubahOleh === 'Ani Contoh' && ubahan.diubahOlehUid === 'uid-tablet', J(ubahan));
    ok('owner (tanpa orang jaga): tanpa operatorId', !('operatorId' in beriAtribusiAkun({ id: 'n2' }, OWN, { perangkat: 'Mac', kini: W.kini }, false)));
  } catch (e) { gagal.push('JATUH: ' + (e && (e.stack || e.message) || e)); }
  print(J({ lulus: lulus, gagal: gagal }));
})();
"""


def baca(ganti=None):
    t = dict((b, open(os.path.join(AKAR, b), encoding='utf-8').read()) for b in list(dict.fromkeys(MODUL + STATIS)))
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert lama in t[b], 'kontrol basi: ' + b + ' · ' + lama[:80]
            t[b] = t[b].replace(lama, baru, 1)
    return t


def jalan_jsc(t):
    js = '\n'.join([bundel_baru.PRELUDE, POLYFILL] + ['\n// ===== ' + m + ' =====\n' + bundel_baru.polos(t[m]) for m in MODUL])
    isi = JAM + js + '\nvar HASH = ' + json.dumps(HASH) + "; var GARAM_UJI = '" + GARAM_UJI + "';\n" + SKENARIO
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(isi); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    baris = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not baris[-1].startswith('{'): return 0, ['JSC JATUH: ' + (r.stderr or r.stdout)[-900:]]
    h = json.loads(baris[-1]); return h['lulus'], h['gagal']


def periksa_statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    fb = t['baru/js/data/firebase.js']; app = t['baru/js/app.js']; html = t['baru/index.html']; mn = t['baru/js/layar/menu.js']
    ok('firebase.js: penulis pusat menulis atas nama orang yang jaga (akunPenulis)', re.search(r'const akun = akunPenulis\(\); const owner = akun\.jenis === \'owner\'', fb))
    ok('firebase.js: pemegang di denyut = orang yang jaga', re.search(r'export function pemegangPerangkat\(\) \{ const a = akunPenulis\(\);', fb))
    ok('firebase.js: orang yang jaga hanya dipakai bila uid-nya = akun yang masuk', 'e && e.uid === a.uid && bisaBekerja(e) ? e : a' in fb)
    ok('app.js: menyetel orang yang jaga ke penulis pusat & kisi hak memakai akun efektif', 'fb.setelAkunEfektif(' in app and re.search(r'fb\.setelSumberHak\(\(\) => \{ const a = akunKini\(\);', app))
    ok('app.js: kunci diam memakai tbHarusKunci (setInterval + kembali dari latar)', app.count('TB.tbHarusKunci(_sentuh, Date.now())') >= 2)
    ok('app.js: hitungan salah PIN disimpan per perangkat (tahan muat ulang)', 'localStorage.setItem(TB.TB_KUNCI_SALAH' in app)
    ok('index.html: panel "Siapa yang jaga?" + modul tablet di modulepreload', 'id="panelOrang"' in html and '<link rel="modulepreload" href="js/layar/tablet-logika.js">' in html)
    ok('menu.js: PIN hanya diketik di tab Orang di tablet dan diteruskan ke tablet-logika (tidak ditulis sendiri)',
       mn.count('type="password"') == 1 and 'TB.tbSusunTambah(' in mn and 'TB.tbSusunGantiPin(' in mn and not re.search(r"pin:\s*st\(\)\.tb", mn))
    # owner 21 Nov 2026 (CPad): gerbang "Siapa yang jaga?" bisa digeser ke samping & ke bawah, logo tertutup, tombol Keluar di luar layar.
    # Ukurannya dibuktikan di panel peramban (1067 × 585 mendatar, 667 × 985 tegak); di sini yang dijaga aturannya tidak hilang.
    gb = t['baru/css/gerbang.css']
    ok('gerbang.css: wadah gerbang tidak bisa digeser mendatar', '.gm-isi { overflow-x: hidden; overscroll-behavior: contain; }' in gb)
    ok('gerbang.css: tablet mendatar — panel jaga dua lajur (nama · PIN) selebar lajurnya, isi yang kepanjangan tidak terpotong di atas',
       '.gm-isi { align-content: safe center; }' in gb and 'grid-template-areas: "kepala kepala" "daftar pin" "catatan pin" "salinan pin" "keluar pin";' in gb
       and '.gm-isi > .gm-pelat.tb-panel:not([hidden]) { justify-self: stretch; width: auto; max-width: 600px;' in gb
       and '.tb-panel > .tb-pin, .tb-panel > .tb-tanya { grid-area: pin; }' in gb and '.tb-panel > #tombolKeluarTablet { grid-area: keluar; align-self: end; }' in gb)
    ok('gerbang.css: panel jaga yang DISEMBUNYIKAN tetap tersembunyi (aturan tata letaknya hanya untuk panel yang tampil)',
       not re.search(r'\.gm-pelat\.tb-panel(?!:not\(\[hidden\]\))[^{]*\{[^}]*display:\s*grid', gb) and '.gerbang-masuk .gm-pelat[hidden] { display: none; }' in gb)
    ok('gerbang.css: daftar nama yang panjang digulir di DAFTARNYA (bukan gerbangnya), mendatar maupun tegak',
       'max-height: min(34vh, 250px); overflow-y: auto; }' in gb and 'max-height: min(14vh, 150px); overflow-y: auto; }' in gb)
    ok('gerbang.css: tablet tegak — cincin dikecilkan selama panel jaga tampil', '.gerbang-masuk:has(.tb-panel:not([hidden])) { --gm-cincin: min(180px, 15vh); }' in gb)
    # akun tablet hanya punya empat menu (Ringkasan tersembunyi): bilah bawah dulu dibagi LIMA lajur mati → lajur kelima kosong di kanan
    ok('bilah menu bawah: lajurnya mengikuti jumlah menu yang TAMPIL (empat menu akun tablet terbagi rata, tanpa ruang kosong di kanan)',
       'display: grid; grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); align-items: center; background: var(--nav);' in t['baru/css/identitas.css']
       and 'repeat(5, minmax(0, 1fr)); align-items: center; background: var(--nav)' not in t['baru/css/identitas.css'] and "el.hidden = !!a && !bolehLayar(a, el.dataset.tujuan);" in app)
    ak = t['baru/js/data/akses.js']; sl = t['baru/js/layar/sistem-logika.js']
    ok('nama peran di layar: "Penjaga laci" (owner 21 Nov 2026: bukan lagi "Ben (penjaga laci)"); kunci perannya tetap ben',
       "ben: 'Penjaga laci'" in ak and "['ben', 'Penjaga laci']" in sl and not [b for b in t if 'Ben (penjaga laci)' in t[b]])
    return out


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += periksa_statis(t)
    if 'jsc' in bagian:
        l, g = jalan_jsc(t); out += [('jsc · ' + x, False, '') for x in g] + [('__jsc', not g, l)]
    return out


TL = 'baru/js/layar/tablet-logika.js'
KONTROL = [
    ('salah PIN 6 kali (bukan 5)', {TL: [("export const TB_BATAS_SALAH = 5;", "export const TB_BATAS_SALAH = 6;")]}, ('jsc',)),
    ('kunci diam 10 menit (bukan 5)', {TL: [("export const TB_LAMA_DIAM_MS = 5 * 60 * 1000;", "export const TB_LAMA_DIAM_MS = 10 * 60 * 1000;")]}, ('jsc',)),
    ('salah ke-5 tidak mengunci', {TL: [("P[id] = n >= TB_BATAS_SALAH ?", "P[id] = false ?")]}, ('jsc',)),
    ('terkunci tetap diperiksa (PIN benar masuk)', {TL: [("  if (s.terkunci) return { ok: false, peta: peta || {}, kalimat: op.nama + ' terkunci", "  if (false) return { ok: false, peta: peta || {}, kalimat: op.nama + ' terkunci")]}, ('jsc',)),
    ('peran orang melebihi akun tablet', {TL: [("const peran = akun.peran === 'karyawan' ? 'karyawan' : op.peran;", "const peran = op.peran;")]}, ('jsc',)),
    ('semua libur = tablet terbuka tanpa PIN', {TL: [("if ((daftar || []).length) return 'pilih';", "if ((daftar || []).filter((o) => o.aktif).length) return 'pilih';")]}, ('jsc',)),
    ('PIN urutan diterima', {TL: [("if (naik || turun) return", "if (false) return")]}, ('jsc',)),
    # dua lapis: tablet-logika tidak pernah menaruh PIN, DAN pembersih sistem-logika membuang kolom asing — kontrolnya merusak keduanya
    ('PIN tersimpan apa adanya (dua lapis dirusak)', {TL: [("peta[id] = { nama: tbTeks(i.nama), peran: i.peran, aktif: true, garam,", "peta[id] = { pin: String(i.pin), nama: tbTeks(i.nama), peran: i.peran, aktif: true, garam,")],
      'baru/js/layar/sistem-logika.js': [("out[id] = { nama: n, peran: o.peran,", "out[id] = { pin: o.pin, nama: n, peran: o.peran,")]}, ('jsc',)),
    ('putaran PBKDF2 diabaikan', {TL: [("iterations: Number(iterasi) || TB_ITERASI", "iterations: 1000")]}, ('jsc',)),
    ('libur menambah hitungan salah / tetap diperiksa', {TL: [("  if (!op.aktif) return { ok: false, peta: peta || {}, kalimat: op.nama + ' sedang libur", "  if (false) return { ok: false, peta: peta || {}, kalimat: op.nama + ' sedang libur")]}, ('jsc',)),
    ('simpan setelan peran menghapus orang di tablet', {'baru/js/layar/sistem-logika.js': [("if (ot.tolak) tolak = tolak || ot.tolak; else o.operator = ot.peta;", "if (ot.tolak) tolak = tolak || ot.tolak;")]}, ('jsc',)),
    ('bentuk orang tidak diperiksa (PIN terbuka lolos)', {'baru/js/layar/sistem-logika.js': [("if (!/^g[0-9a-f]{32}$/.test(t(o.garam)) || !/^[0-9a-f]{64}$/.test(t(o.acak))) return", "if (false) return")]}, ('jsc',)),
    ('catatan baru tanpa kode orang', {'baru/js/data/akses.js': [("if (akun.operatorId) d.operatorId = akun.operatorId;", "")]}, ('jsc',)),
    ('penulis pusat memakai akun tablet apa adanya', {'baru/js/data/firebase.js': [("const akun = akunPenulis(); const owner = akun.jenis === 'owner';", "const akun = status.akun; const owner = akun.jenis === 'owner';")]}, ('statis',)),
    ('app.js tidak menyetel orang yang jaga', {'baru/js/app.js': [("fb.setelAkunEfektif(", "void (")]}, ('statis',)),
    ('gerbang: panel jaga tersembunyi ikut tampil (aturan tata letak menimpa hidden)', {'baru/css/gerbang.css': [(".gm-isi > .gm-pelat.tb-panel:not([hidden]) { justify-self: stretch;", ".gm-isi > .gm-pelat.tb-panel { justify-self: stretch;")]}, ('statis',)),
    ('gerbang: bisa digeser mendatar lagi', {'baru/css/gerbang.css': [(".gm-isi { overflow-x: hidden; overscroll-behavior: contain; }", ".gm-isi { overscroll-behavior: contain; }")]}, ('statis',)),
    ('gerbang: panel jaga kembali satu lajur di tablet mendatar', {'baru/css/gerbang.css': [('grid-template-areas: "kepala kepala" "daftar pin" "catatan pin" "salinan pin" "keluar pin";', 'grid-template-areas: none;')]}, ('statis',)),
    ('bilah menu bawah kembali lima lajur mati', {'baru/css/identitas.css': [("grid-auto-flow: column; grid-auto-columns: minmax(0, 1fr); align-items: center; background: var(--nav);", "grid-template-columns: repeat(5, minmax(0, 1fr)); align-items: center; background: var(--nav);")]}, ('statis',)),
    ('label peran kembali "Ben (penjaga laci)"', {'baru/js/data/akses.js': [("ben: 'Penjaga laci'", "ben: 'Ben (penjaga laci)'")]}, ('statis',)),
    ('kunci diam dicabut dari app.js', {'baru/js/app.js': [("setInterval(() => { if (_jaga && TB.tbHarusKunci(_sentuh, Date.now())) kunciOrang(); }, 15000);", "")]}, ('statis',)),
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
