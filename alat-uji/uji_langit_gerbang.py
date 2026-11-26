#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
uji_langit_gerbang.py — LANGIT GERBANG (owner 26 Nov 2026): langit di balik pintu kaca gerbang ikut jam & cuaca sungguhan, "mewah", "terbaik tapi optimal".
baru/js/inti/langit-logika.js (tanpa DOM) dijalankan di jsc; langit.js, langit.css, gerbang.js, app.js, menu & index.html diperiksa statis.
  · SIANG TROPIS (owner 26 Nov: "matahari sama sekali gak muncul"): lintasan tidak pernah di balik papan nama / cincin / kotak Masuk (Mac, CPad), HP & tablet
    berdiri ≤ 100 menit; jam 12 di kanan atas; TERIK ±10–14 (padam saat mendung/hujan); cakram & pancaran di depan kaca buram; biru tropis pekat.
  · JAM: malam 03.00 (bintang, bulan, kunang, tanpa burung) · fajar · siang 12.00 (matahari tinggi, burung, tanpa bintang) · senja (berkas cahaya, matahari
    rendah) · warna BERGULIR tiap menit tanpa loncatan sepanjang 24 jam · terbit/terbenam dari cuaca dipakai · mode terang lebih muda dari gelap.
  · CUACA: kode WMO → cerah / berawan / mendung (langit kelabu) / kabut / gerimis / hujan / lebat / petir; kalimat "°  · teks"; cuaca > 3 jam = diabaikan.
  · AMBIL: tanpa lokasi = tidak pernah; belum ada / lokasi lain / > 30 menit / jam mundur = ambil; < 30 menit = tidak. Jawaban Open-Meteo dibaca & dijaga.
  · LOKASI: 3 desimal, tanpa tanda HTML, tanpa GPS; cari tempat Indonesia saja; bulan: fase purnama & bulan baru acuan.
  · STATIS (optimal): gerak tanpa henti hanya transform/opacity; tidak ada transisi letak; nama KELAS KEADAAN di gerbang tidak sama dengan nama kelas lapisan
    (26 Nov: 'lg-petir' dipakai keduanya → seluruh gerbang ikut bergaya sambaran petir); kilat lewat Web Animations di lapisnya (tanpa ganti kelas gerbang, tanpa
    memaksa tata letak); langit hanya hidup selama gerbang tampil; reduced-motion; fetch tanpa kuki & perujuk; CSP membuka dua alamat Open-Meteo saja;
    lokasi dari setelan disalin hanya bila dokumennya sudah terbaca; atur Perangkat menyimpan lokasi lewat lgLokasiSah.

    python3 alat-uji/uji_langit_gerbang.py            → N lulus · 0 gagal
    python3 alat-uji/uji_langit_gerbang.py --kontrol  → kerusakan wajib ketahuan (keluar 3 kalau ada yang diam)
"""
import os, re, sys, json, glob, subprocess, tempfile
SINI = os.path.dirname(os.path.abspath(__file__)); AKAR = os.path.abspath(os.path.join(SINI, '..'))
sys.path.insert(0, SINI)
import bundel_baru  # noqa: E402
JSC = '/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc'
LL, LJ, LC, GJ, AP, MN, SL, IX, GC = ('baru/js/inti/langit-logika.js', 'baru/js/inti/langit.js', 'baru/css/langit.css', 'baru/js/inti/gerbang.js', 'baru/js/app.js',
                                      'baru/js/layar/menu.js', 'baru/js/layar/sistem-logika.js', 'baru/index.html', 'baru/css/gerbang.css')

SKENARIO = r"""
var gagal = [], lulus = 0; var J = JSON.stringify;
function ok(nama, syarat, ket) { if (syarat) lulus++; else gagal.push(nama + (ket !== undefined ? ' → ' + String(typeof ket === 'string' ? ket : J(ket)).slice(0, 500) : '')); }
var jam = function (h, m, tgl) { var d = new Date(tgl || '2026-11-26T00:00:00'); d.setHours(h, m || 0, 0, 0); return d; };
var rgb = function (s) { var m = /rgba\((\d+),(\d+),(\d+),([\d.]+)\)/.exec(s); return m ? [Number(m[1]), Number(m[2]), Number(m[3]), Number(m[4])] : null; };
var segar = function (kode, awan, d) { return { lat: -6.2, lon: 106.8, pada: d.getTime() - 60000, kode: kode, awan: awan === undefined ? null : awan, hujanMm: 0, suhu: 30.6, terbit: null, terbenam: null, tanggal: '' }; };
// bulan purnama berikutnya sesudah 26 Nov 2026 (dicari, bukan ditebak)
var purnama = null, baru = null; for (var i = 0; i < 40 * 24; i++) { var t = new Date(2026, 10, 1, 0, 0).getTime() + i * 3600000; var f = lgFaseBulan(t); if (purnama === null && Math.abs(f - 0.5) < 0.01) purnama = t; if (baru === null && (f < 0.01 || f > 0.99)) baru = t; }

// ---- JAM
var M = lgKeadaan(jam(3, 0, purnama ? new Date(purnama).toISOString() : undefined), null, 'gelap');
ok('malam 03.00 (purnama): malam penuh, bintang, bulan tampil, kunang ya, burung & capung tidak, matahari tidak', M.malam === 1 && M.bintang > 0.8 && M.bulan.op > 0.5 && M.kunang && !M.burung && !M.capung && M.surya.op === 0 && M.fase === 'malam', M);
var S = lgKeadaan(jam(12, 0), null, 'gelap');
ok('siang 12.00: matahari tinggi & terang, tanpa bintang & bulan, burung & capung ya, kunang tidak', S.siang === 1 && S.surya.op > 0.9 && S.surya.y < 25 && S.bintang === 0 && S.bulan.op === 0 && S.burung && S.capung && !S.kunang && S.fase === 'siang', S);
var SJ = lgKeadaan(jam(17, 55), null, 'gelap');
ok('senja 17.55 (terbenam rata-rata): fase senja, cahaya cakrawala pekat, berkas cahaya, matahari rendah', SJ.fase === 'senja' && rgb(SJ.warna.cahaya)[3] > 0.6 && SJ.surya.sinar > 0.5 && SJ.surya.y > 50, SJ);
var F = lgKeadaan(jam(5, 30), null, 'gelap');
ok('fajar 05.30: fase fajar, cahaya jingga, bintang memudar', F.fase === 'fajar' && rgb(F.warna.cahaya)[0] > 200 && F.bintang < 0.5, F);
// bergulir tiap menit tanpa loncatan
var lompat = 0, contoh = ''; var a0 = null;
for (var mnt = 0; mnt < 1440; mnt++) { var K = lgKeadaan(jam(Math.floor(mnt / 60), mnt % 60), null, 'gelap'); var a = ['l1', 'l2', 'l3', 'cahaya'].map(function (k) { return rgb(K.warna[k]); });
  if (a0) { for (var x = 0; x < 4; x++) for (var y = 0; y < 3; y++) { var d = Math.abs(a[x][y] - a0[x][y]); if (d > 6) { lompat++; if (!contoh) contoh = mnt + ' ' + x + ' ' + d; } } } a0 = a; }
ok('warna langit bergulir tiap menit tanpa loncatan sepanjang 24 jam (perubahan per menit ≤ 6 per kanal)', lompat === 0, contoh);
var T2 = segar(0, 0, jam(6, 10)); T2.terbit = 6 * 60 + 30; T2.terbenam = 18 * 60 + 40;
ok('terbit/terbenam dari cuaca dipakai: 06.10 dengan terbit 06.30 matahari belum naik (redup), tanpa cuaca (terbit 05.35) sudah terang', lgKeadaan(jam(6, 10), T2, 'gelap').surya.op < 0.3 && lgKeadaan(jam(6, 10), null, 'gelap').surya.op > 0.5, [lgKeadaan(jam(6, 10), T2, 'gelap').surya, lgKeadaan(jam(6, 10), null, 'gelap').surya]);
var jml = function (s) { var c = rgb(s); return c[0] + c[1] + c[2]; };
ok('mode terang lebih muda dari mode gelap (siang & malam)', jml(lgKeadaan(jam(12, 0), null, 'terang').warna.l1) > jml(S.warna.l1) && jml(lgKeadaan(jam(23, 0), null, 'terang').warna.l1) > jml(lgKeadaan(jam(23, 0), null, 'gelap').warna.l1));

// ---- CUACA
var C = function (k, a) { return lgCuaca(k, a); };
ok('kode cuaca: 95 petir lebat · 61 hujan · 51 gerimis · 45 kabut · 3 mendung · 0 cerah · tak dikenal = cerah tanpa kalimat',
  C(95).petir && C(95).hujan === 3 && C(61).hujan === 2 && !C(61).petir && C(51).hujan === 1 && C(45).kabut === 1 && C(3).jenis === 'mendung' && C(0).hujan === 0 && C(0).teks === 'Cerah' && C(1234).teks === '' && C(null).hujan === 0);
var sat = function (s) { var c = rgb(s); return Math.max(c[0], c[1], c[2]) - Math.min(c[0], c[1], c[2]); };
var D12 = jam(12, 0); var Cr = lgKeadaan(D12, segar(0, 2, D12), 'gelap'), Md = lgKeadaan(D12, segar(3, 99, D12), 'gelap'), Hj = lgKeadaan(D12, segar(63, 100, D12), 'gelap');
ok('mendung 99% = langit kelabu (jauh kurang biru dari cerah), matahari nyaris hilang; hujan: burung pergi, kalimat bersuhu', sat(Md.warna.l2) < sat(Cr.warna.l2) * 0.6 && Md.surya.op < 0.2 && Cr.surya.op > 0.9 && !Hj.burung && Hj.hujan === 2 && Hj.teks === '31° · Hujan' && Md.mendung > 0.6, [Md.warna.l2, Cr.warna.l2, Md.surya.op, Hj.teks]);
var basi = segar(95, 100, D12); basi.pada = D12.getTime() - 4 * 3600000;
var B4 = lgKeadaan(D12, basi, 'gelap');
ok('cuaca lebih tua dari 3 jam diabaikan: tanpa hujan, tanpa petir, tanpa kalimat', B4.hujan === 0 && !B4.petir && B4.teks === '', B4);

// ---- AMBIL
var LOK = { nama: 'Contoh', lat: -6.2, lon: 106.8 }; var k0 = Date.UTC(2026, 10, 26, 3, 0); var c0 = { lat: -6.2, lon: 106.8, pada: k0 };
ok('ambil cuaca: tanpa lokasi tidak pernah; belum ada → ambil; 10 mnt → tidak; 31 mnt → ambil; lokasi lain → ambil; jam mundur → ambil',
  !lgPerluAmbil(null, null, k0) && lgPerluAmbil(null, LOK, k0) && !lgPerluAmbil(c0, LOK, k0 + 600000) && lgPerluAmbil(c0, LOK, k0 + 31 * 60000) && lgPerluAmbil(c0, { lat: -7, lon: 110 }, k0 + 60000) && lgPerluAmbil(c0, LOK, k0 - 60000));
var jawab = { current: { time: '2026-11-26T10:45', temperature_2m: 31.64, weather_code: 3, cloud_cover: 99, precipitation: 0, is_day: 1 }, daily: { time: ['2026-11-26'], sunrise: ['2026-11-26T05:26'], sunset: ['2026-11-26T17:53'] } };
var Bc = lgBacaCuaca(jawab, LOK, k0);
ok('jawaban Open-Meteo dibaca: kode, awan, suhu dibulatkan, terbit & terbenam dalam menit, tanggal', Bc && Bc.kode === 3 && Bc.awan === 99 && Bc.suhu === 31.6 && Bc.terbit === 326 && Bc.terbenam === 1073 && Bc.tanggal === '2026-11-26' && Bc.pada === k0, Bc);
ok('jawaban rusak → null; terbit sesudah terbenam → terbit/terbenam tidak dipakai; simpanan dibaca pulang-pergi',
  lgBacaCuaca({}, LOK, k0) === null && lgBacaCuaca(jawab, null, k0) === null && lgBacaCuaca({ current: { weather_code: 'x' } }, LOK, k0) === null
  && lgBacaCuaca({ current: { weather_code: 1 }, daily: { sunrise: ['T18:00'], sunset: ['T06:00'] } }, LOK, k0).terbit === null && J(lgCuacaTersimpan(J(Bc))) === J(Bc) && lgCuacaTersimpan('{') === null);

// ---- LOKASI & CARI
var Ls = lgLokasiSah({ nama: '<b>Menteng</b>', lat: -6.19876, lon: 106.83912 });
ok('lokasi: 3 desimal, tanda HTML dibuang, di luar batas → null', Ls.lat === -6.199 && Ls.lon === 106.839 && Ls.nama === 'bMenteng/b' && lgLokasiSah({ lat: 91, lon: 0 }) === null && lgLokasiSah({ lat: 'x', lon: 1 }) === null && lgLokasiSah(null) === null, Ls);
var U = lgUrlCuaca(Ls);
ok('alamat cuaca hanya membawa koordinat (+ isian yang diminta), Open-Meteo', U.indexOf('https://api.open-meteo.com/v1/forecast?latitude=-6.199&longitude=106.839&') === 0 && U.indexOf('nama') < 0 && U.indexOf('Menteng') < 0 && lgUrlCuaca(null) === '', U);
ok('cari tempat: < 3 huruf → kosong; Indonesia saja; nama di-encode; hasil → nama + wilayah, 6 paling banyak',
  lgUrlCari('ab') === '' && /countryCode=ID/.test(lgUrlCari('Kebayoran Lama')) && /name=Kebayoran%20Lama/.test(lgUrlCari('Kebayoran Lama'))
  && J(lgBacaCari({ results: [{ name: 'Menteng', latitude: -6.19, longitude: 106.83, admin1: 'Jakarta', admin2: 'Jakarta Pusat' }, { name: 'X', latitude: 'a', longitude: 1 }] })) === J([{ nama: 'Menteng', lat: -6.19, lon: 106.83, wilayah: 'Jakarta Pusat, Jakarta' }])
  && lgBacaCari(null).length === 0);
ok('pratinjau ?langitJam=19.30&langitCuaca=95 dibaca; kode tak dikenal diabaikan; tanpa isian = null', J(lgPaksa('?langitJam=19.30&langitCuaca=95')) === J({ menit: 1170, kode: 95 }) && lgPaksa('?langitCuaca=1234') === null && lgPaksa('') === null && lgPaksa('?langitJam=7:05').menit === 425);
ok('fase bulan: purnama 25 Jan 2024 ≈ 0,5; bulan baru 11 Jan 2024 ≈ 0 (selisih < 0,03)', Math.abs(lgFaseBulan(Date.UTC(2024, 0, 25, 17, 54)) - 0.5) < 0.03 && Math.min(lgFaseBulan(Date.UTC(2024, 0, 11, 11, 57)), 1 - lgFaseBulan(Date.UTC(2024, 0, 11, 11, 57))) < 0.03, [lgFaseBulan(Date.UTC(2024, 0, 25, 17, 54)), lgFaseBulan(Date.UTC(2024, 0, 11, 11, 57))]);
// ---- TAMPILAN G4 ASLI (owner 26 Nov: "jangan dihapus") & SUASANA
var Pg = lgKeadaan(jam(18, 35), null, 'gelap'), St = lgKeadaan(jam(16, 10), null, 'terang');
ok('petang cerah mode gelap (18.35) = G4 asli PERSIS: langit tembus, cahaya cakrawala rgba(214,146,64,0.46), tanpa matahari/bulan/bintang', Pg.asli === 1 && rgb(Pg.warna.l1)[3] === 0 && rgb(Pg.warna.l3)[3] === 0 && Pg.warna.cahaya === 'rgba(214,146,64,0.46)' && Pg.surya.op === 0 && Pg.bulan.op === 0 && Pg.bintang === 0, Pg);
ok('sore cerah mode terang (16.10) = G4 terang asli PERSIS: langit tembus, cahaya rgba(246,190,104,0.62), tanpa matahari', St.asli === 1 && rgb(St.warna.l1)[3] === 0 && St.warna.cahaya === 'rgba(246,190,104,0.62)' && St.surya.op === 0, St);
var PgH = lgKeadaan(jam(18, 35), segar(63, 100, jam(18, 35)), 'gelap');
ok('petang yang hujan: tampilan asli tertutup hujan & cahaya cakrawala meredup', PgH.hujan === 2 && rgb(PgH.warna.cahaya)[3] < 0.3, PgH.warna.cahaya);
ok('mode gelap petang & mode terang sore tidak dipakai di mode lawannya (gelap 16.10 bukan asli, terang 18.35 bukan asli)', lgKeadaan(jam(16, 10), null, 'gelap').asli === 0 && lgKeadaan(jam(18, 35), null, 'terang').asli === 0);
var sw = function (h, m, c) { return lgKeadaan(jam(h, m), c === undefined ? null : segar(c, undefined, jam(h, m)), 'gelap').satwa; };
var Pa = sw(7, 10), Si = sw(13, 0, 0), Sr = sw(16, 40), Mm = sw(22, 0, 0), Hu = sw(16, 40, 63), Gr = sw(22, 0, 51), Kb = sw(6, 30, 45), Fj = sw(5, 0);
ok('suasana pagi 07.10: burung, bangau, kupu-kupu; tanpa kelelawar & kunang', Pa.burung && Pa.bangau && Pa.kupu && !Pa.kelelawar && !Pa.kunang, Pa);
ok('suasana siang 13.00 cerah: elang, kupu-kupu, capung', Si.elang && Si.kupu && Si.capung && !Si.kelelawar, Si);
ok('suasana sore 16.40: kawanan burung pulang, capung, bangau; elang sudah turun', Sr.burung && Sr.capung && Sr.bangau && !Sr.elang, Sr);
ok('suasana malam 22.00 cerah: kunang, kelelawar, bintang jatuh; tanpa burung, kupu, elang', Mm.kunang && Mm.kelelawar && Mm.meteor && !Mm.burung && !Mm.kupu && !Mm.elang, Mm);
ok('hujan sore: SEPI — tidak ada yang terbang', !Hu.burung && !Hu.capung && !Hu.kupu && !Hu.bangau && !Hu.elang && !Hu.kelelawar, Hu);
ok('gerimis malam: kunang & kelelawar masih ada, bintang jatuh tidak', Gr.kunang && Gr.kelelawar && !Gr.meteor, Gr);
ok('kabut pagi: hanya bangau samar (tanpa burung & kupu-kupu)', Kb.bangau && !Kb.burung && !Kb.kupu, Kb);
ok('subuh 05.00: kelelawar pulang & kunang masih ada, burung belum', Fj.kelelawar && Fj.kunang && !Fj.burung, Fj);
// ---- PETIR (owner 26 Nov: "coba garap")
var acak = (function () { var x = 7; return function () { x = (Math.imul(x, 1103515245) + 12345) | 0; return ((x >>> 8) & 0xffffff) / 0x1000000; }; })();
var P1 = lgPetirAcak(acak), P2 = lgPetirAcak(acak);
var titik = function (d) { return d.slice(1).split(' L').map(function (p) { return p.split(' ').map(Number); }); };
var t1 = titik(P1.utama);
ok('sambaran: jalur utama dari puncak (y 0) sampai bawah (≥ 360 dari 400), x tetap di dalam 2–98, zig-zag (≥ 10 titik)', t1[0][1] === 0 && t1[t1.length - 1][1] >= 360 && t1.every(function (p) { return p[0] >= 2 && p[0] <= 98 && p[1] >= 0 && p[1] <= 400; }) && t1.length >= 10, P1.utama.slice(0, 200));
ok('sambaran: 1–3 cabang, tiap cabang di dalam kotak; tiap sambaran BEDA bentuk', P1.cabang.length >= 1 && P1.cabang.length <= 3 && P1.cabang.every(function (c) { return titik(c).every(function (p) { return p[0] >= 2 && p[0] <= 98 && p[1] <= 400; }); }) && P1.utama !== P2.utama, [P1.cabang.length, P2.cabang.length]);
var Bd = lgKeadaan(D12, segar(95, 100, D12), 'gelap'), Hj2 = lgKeadaan(D12, segar(63, 100, D12), 'gelap');
ok('langit badai lebih gelap dari langit hujan biasa (sambaran menyala di atasnya)', jml(Bd.warna.l1) < jml(Hj2.warna.l1) - 40 && jml(Bd.warna.l2) < jml(Hj2.warna.l2) - 40, [Bd.warna.l2, Hj2.warna.l2]);
var Mb = baru ? lgKeadaan(jam(23, 0, new Date(baru).toISOString()), null, 'gelap') : null;
ok('bulan baru: hampir tak terlihat (malam tetap berbintang)', Mb && Mb.bulan.op < 0.12 && Mb.bintang > 0.8, Mb && Mb.bulan);
// ---- SIANG TROPIS (owner 26 Nov 2026: "Gak sesuai, Indonesia kan negara tropis. Lalu matahari sama sekali gak muncul beserta pancarannya.")
// rintangan = papan nama + pil jam, cincin kunci, kotak Masuk, tombol mode (% layar, diukur di peramban); cakram matahari = 38% kotak clamp(64px, 8.6vw, 118px)
var LAYAR = { datar: [['Mac 1918×937', 1918, 937, [[40, 60, 4, 17.5], [28, 45, 40, 77], [53, 75, 38, 79], [97, 99, 1, 6]]], ['CPad 1280×800', 1280, 800, [[35, 65, 5, 22], [17, 43, 39, 81], [54, 87, 36, 84], [95, 99, 2, 7]]]],
  tegak: [['HP 390×844', 390, 844, [[15, 85, 3, 16], [29, 71, 18, 37], [4, 96, 39, 83], [85, 96, 2, 7]]], ['tablet berdiri 800×1280', 800, 1280, [[26, 68, 5, 15], [34, 66, 16, 36], [23, 78, 38, 66], [93, 98, 1, 5]]]] };
var tertutup = function (L, tegak) { var r = 0.38 * Math.min(118, Math.max(64, 0.086 * L[1])) / 2, rx = r / L[1] * 100, ry = r / L[2] * 100, out = [];
  for (var m = 335; m <= 1075; m += 5) { var K = lgKeadaan(jam(Math.floor(m / 60), m % 60), null, 'gelap').surya; var x = tegak ? K.tx : K.x, y = tegak ? K.ty : K.y; if (y > 72) continue;
    if (L[3].some(function (o) { return x > o[0] - rx * 0.3 && x < o[1] + rx * 0.3 && y > o[2] - ry * 0.3 && y < o[3] + ry * 0.3; })) out.push(Math.floor(m / 60) + '.' + ('0' + m % 60).slice(-2) + '@' + x + ',' + y); }
  return out; };
LAYAR.datar.forEach(function (L) { var t = tertutup(L, false); ok('lintasan matahari layar datar (' + L[0] + '): TIDAK PERNAH di balik papan nama, cincin, kotak Masuk — terbit s.d. terbenam', t.length === 0, t.slice(0, 6)); });
LAYAR.tegak.forEach(function (L) { var t = tertutup(L, true); ok('lintasan matahari layar tegak (' + L[0] + '): tertutup ≤ 100 menit sehari & 11.40–12.20 terlihat', t.length * 5 <= 100 && !t.some(function (s) { return /^(11\.[45]|12\.[01])/.test(s); }), t.length * 5 + ' mnt ' + t.slice(0, 4).join(' ')); });
ok('jam 12.00 matahari tinggi di langit KANAN ATAS yang lapang (bukan tengah atas di balik papan nama) — datar & tegak', S.surya.x > 66 && S.surya.x < 92 && S.surya.y < 22 && S.surya.tx > 70 && S.surya.ty > 16 && S.surya.ty < 30, S.surya);
var naik = true, turun = true, maju = true, sebelum = null;
for (var m = 335; m <= 1075; m += 5) { var K = lgKeadaan(jam(Math.floor(m / 60), m % 60), null, 'gelap').surya; if (sebelum) { if (m <= 760 && K.y > sebelum.y + 0.3) naik = false; if (m >= 770 && K.y < sebelum.y - 0.3) turun = false; if (K.x < sebelum.x - 0.3 || K.tx < sebelum.tx - 0.3) maju = false; } sebelum = K; }
ok('matahari terus naik sampai ±12.40, lalu terus turun; selalu bergerak ke kanan (tanpa mundur)', naik && turun && maju, [naik, turun, maju]);
var tr = function (h, m, kode, mode) { var d = jam(h, m); return lgKeadaan(d, kode === null ? null : segar(kode, undefined, d), mode || 'gelap').surya.terik; };
ok('TERIK: 12.00 cerah penuh (≥ 0,95) di mode gelap & terang; 10.00 & 14.00 masih terik; 07.00 & 16.30 tidak', tr(12, 0, 0) >= 0.95 && tr(12, 0, 0, 'terang') >= 0.95 && tr(10, 0, 0) > 0.6 && tr(14, 0, 0) > 0.5 && tr(7, 0, 0) === 0 && tr(16, 30, 0) === 0, [tr(12, 0, 0), tr(10, 0, 0), tr(14, 0, 0), tr(7, 0, 0), tr(16, 30, 0)]);
ok('TERIK padam saat mendung, hujan, badai; redup saat berawan & kabut; tidak ada di malam hari & tampilan G4 asli', tr(12, 0, 3) === 0 && tr(12, 0, 63) === 0 && tr(12, 0, 95) === 0 && tr(12, 0, 2) > 0.2 && tr(12, 0, 2) < 0.6 && tr(12, 0, 45) < 0.35 && tr(22, 0, 0) === 0 && lgKeadaan(jam(18, 35), null, 'gelap').surya.terik === 0,
   [tr(12, 0, 3), tr(12, 0, 2), tr(12, 0, 45)]);
ok('langit siang TROPIS: biru pekat di puncak (saturasi ≥ 175), cakrawala lembap terang', sat(S.warna.l1) >= 175 && rgb(S.warna.l1)[2] > 190 && jml(S.warna.l3) > 620, [S.warna.l1, S.warna.l3]);
print(J({ lulus: lulus, gagal: gagal }));
"""


def baca(ganti=None):
    t = {b: open(os.path.join(AKAR, b), encoding='utf-8').read() for b in [LL, LJ, LC, GJ, AP, MN, SL, IX, GC]}
    for f in sorted(glob.glob(os.path.join(AKAR, 'baru/css/*.css'))): t.setdefault(os.path.relpath(f, AKAR), open(f, encoding='utf-8').read())
    for b, pasangan in (ganti or {}).items():
        for lama, baru in pasangan:
            assert t[b].count(lama) == 1, 'kontrol basi: ' + b + ' · ' + lama[:80] + ' (' + str(t[b].count(lama)) + '×)'
            t[b] = t[b].replace(lama, baru, 1)
    return t


def statis(t):
    out = []; ok = lambda n, c, k='': out.append(('statis · ' + n, bool(c), k))
    lj, lc, gj, ap, mn, sl, ix = t[LJ], t[LC], t[GJ], t[AP], t[MN], t[SL], t[IX]
    # gerak tanpa henti hanya transform/opacity
    buruk = []
    kf = {m.group(1): m.group(2) for m in re.finditer(r'@keyframes\s+([\w-]+)\s*\{((?:[^{}]*\{[^{}]*\})*)[^{}]*\}', lc)}
    for m in re.finditer(r'animation:\s*([^;}]*)', lc):
        if 'infinite' not in m.group(1): continue
        for nama in re.findall(r'[\w-]+', m.group(1)):
            if nama in kf:
                sifat = set(re.findall(r'([a-z-]+)\s*:', kf[nama])) - {'transform', 'opacity', 'offset'}
                if sifat: buruk.append(nama + ' ' + str(sorted(sifat)))
    ok('langit.css: gerak tanpa henti hanya transform / opacity', not buruk and len(kf) >= 5, buruk)
    ok('langit.css: tidak ada transisi letak / ukuran (left, top, width, height, background)', not re.search(r'transition:[^;]*(left|top|width|height|background)', lc), re.findall(r'transition:[^;]*', lc))
    # nama kelas keadaan (di gerbang) ≠ nama kelas lapisan
    blok = lj[lj.find('const kelas = ['):lj.find('.filter(Boolean)', lj.find('const kelas = ['))]
    keadaan = set(re.findall(r"'(lg-[a-z-]+)'", blok)) | {'lg-hujan-0', 'lg-hujan-1', 'lg-hujan-2', 'lg-hujan-3'}
    lapisan = set()
    for m in re.finditer(r"""className\s*=\s*['"]([^'"]+)['"]|class="([^"]+)"|svg\([^,]+,\s*'([^']*)'""", lj):
        for k in (m.group(1) or m.group(2) or m.group(3) or '').split(): lapisan.add(k)
    lapisan |= {'lg-' + j for j in re.findall(r"satwa\('(\w+)'", lj)} | {'lg-satwa', 'lg-kepak', 'lg-elang-putar', 'lg-meteor', 'lg-awan', 'lg-hujan'}
    tabrak = sorted((keadaan & lapisan) | {k for k in keadaan if re.search(r'(^|[\s,{}])\.' + re.escape(k) + r'\s*\{', lc)})
    ok('nama kelas KEADAAN gerbang tidak dipakai lapisan mana pun (26 Nov: "lg-petir" ganda → seluruh gerbang bergaya sambaran)', not tabrak and len(keadaan) >= 10, tabrak)
    ok('kilat lewat Web Animations di lapisnya — tanpa ganti kelas gerbang, tanpa memaksa tata letak', "lapis.animate(" in lj and "kilas.animate(" in lj and 'offsetWidth' not in lj and 'lg-kilat-nyala' not in lj + lc)
    ok('sambaran petir di DEPAN kaca (di belakang kaca buram garis 2 px hilang), di bawah kotak Masuk, disembunyikan saat pintu bergerak; bentuk baru tiap sambaran',
       "g.insertBefore(sambar, hidupAda)" in lj and re.search(r'\.lg-sambar \{ position: absolute; z-index: 3;', lc) is not None and '.gerbang-masuk.t-membuka .lg-sambar, .gerbang-masuk.t-menutup .lg-sambar { visibility: hidden; }' in lc
       and 'const b = L.lgPetirAcak();' in lj and "petir.animate(KF_SAMBAR" in lj)
    ok('langit hidup hanya selama gerbang tampil: nyala bersama jam gerbang, dihitung sekali per menit', 'langit.nyala(ya);' in gj and 'langit.detik();' in gj and 'if (m === menitAkhir) return;' in lj and "if (!nyalaKini) return;" in lj)
    ok('mode terang/gelap ditukar dari gerbang → langit ikut', "tm.addEventListener('click', () => { opsi.gantiMode(); langit.perbarui(); });" in gj and "pasangGerbang({ gantiMode: () => gantiMode(), mode: () => mode })" in ap)
    ok('reduced-motion: langit tanpa gerak, tanpa kilat', '@media (prefers-reduced-motion: reduce)' in lc and 'if (diam()) return;' in lj)
    ok('ambil cuaca: tanpa kuki & perujuk, batas 8 dtk, gagal = diam (langit ikut jam)', "credentials: 'omit', referrerPolicy: 'no-referrer'" in lj and 'setTimeout(() => henti && henti.abort(), 8000)' in lj and "catch (e) { /* tanpa internet" in lj)
    ok('tanpa GPS perangkat & tanpa data toko dikirim (langit*.js tidak memakai geolocation / toko.js / firebase)', all('geolocation' not in t[f] and 'toko.js' not in t[f] and 'firebase' not in t[f].lower() for f in [LL, LJ]))
    cs = re.search(r"connect-src ([^;]*);", ix).group(1).split()
    ok('CSP: Open-Meteo cuaca & cari tempat dibuka (dan tidak ada host Open-Meteo lain)', 'https://api.open-meteo.com' in cs and 'https://geocoding-api.open-meteo.com' in cs and len([h for h in cs if 'open-meteo' in h]) == 2, cs)
    ok('index.html: langit.css sesudah gerbang.css, modul dipramuat, kalimat cuaca di pil jam', ix.find('href="css/langit.css"') > ix.find('href="css/gerbang.css"') > 0 and 'href="js/inti/langit.js"' in ix and 'href="js/inti/langit-logika.js"' in ix
       and '<span id="gmJam" class="serif gm-jam"></span><span id="gmCuaca" class="gm-cuaca" hidden></span>' in ix)
    ok('app.js: lokasi dari setelan disalin hanya bila dokumen setelannya sudah terbaca (cache kosong ≠ owner mencabut)', "if (dokDiCache('aturanToko', 'perangkat')) langitSimpanLokasi(ssAtur('perangkat').cuaca);" in ap and 'setTimeout(simpanLokasiCuaca, 0);' in ap)
    ok('atur Perangkat: lokasi disimpan lewat lgLokasiSah (bawaan null), dipilih dari hasil cari Open-Meteo', "o.cuaca = lgLokasiSah(isi.cuaca !== undefined ? isi.cuaca : A.cuaca);" in sl and "cuaca: null }" in sl
       and "cuacaPilih: ({ i }) =>" in mn and "aturCuaca(s, a)" in mn and "lgUrlCari(st().cuacaCari)" in mn)
    ok('TERIK: cakram tajam, pancaran & kilau DI DEPAN kaca (lapis makhluk hidup, di bawah burung) — di balik kaca buram 26 px semuanya lebur; silau di belakang kaca',
       "hidup.insertBefore(suryaDepan(), hidup.firstChild);" in lj and "'<div class=\"lg-terik-depan\"><div class=\"lg-pancar\"></div><div class=\"lg-kilau\"></div></div><div class=\"lg-inti\"></div>'" in lj
       and "K.surya.terik > 0.02 ? 'lg-ada-terik' : ''" in lj and "setel('--lg-terik', String(K.surya.terik));" in lj
       and '.gerbang-masuk.lg-ada-terik .lg-terik, .gerbang-masuk.lg-ada-terik .lg-terik-depan { display: block; }' in lc and '.gerbang-masuk.lg-ada-surya .lg-surya-depan { display: block; }' in lc
       and re.search(r'\.lg-pancar \{[^}]*animation: lgPutar', lc) is not None and '.lg-pancar, .lg-kilau,' in lc[lc.find('prefers-reduced-motion'):])
    dua = '@media (min-width: 1100px), (min-width: 900px) and (orientation: landscape)'
    ok('letak matahari & bulan: lintasan datar untuk gerbang DUA KOLOM, tegak untuk gerbang bertumpuk — syarat sama persis dengan gerbang.css',
       dua + ' { .gm-isi' in t[GC] and (dua + ' {\n  .gerbang-masuk { --lg-sx: var(--lg-surya-x, 50%); --lg-sy: var(--lg-surya-y, 30%); --lg-bx: var(--lg-bulan-x, 50%); --lg-by: var(--lg-bulan-y, 30%); }') in lc
       and '.gerbang-masuk { --lg-sx: var(--lg-surya-tx, 50%);' in lc and 'left: var(--lg-sx, 50%); top: var(--lg-sy, 30%);' in lc and 'left: var(--lg-bx, 50%); top: var(--lg-by, 30%);' in lc
       and "setel('--lg-surya-tx', K.surya.tx + '%')" in lj and "setel('--lg-bulan-ty', K.bulan.ty + '%')" in lj)
    ok('gerbang G4 terkunci tidak berubah: pintu, papan, cincin, kotak Masuk tetap (langit hanya menyisip lapisan)', '<div class="gm-latar" aria-hidden="true"><div class="gm-bola emas"></div><div class="gm-bola platina"></div><div class="gm-cakrawala"></div></div>' in ix
       and '.gm-pintu {' in t[GC] and 'id="formMasuk"' in ix and not re.search(r'\.gm-(pintu|papan|logo|cincin|pelat|isi|c-|cakram)\b', t[LC]))
    return out


def jalan(js):
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f: f.write(js); p = f.name
    r = subprocess.run([JSC, p], capture_output=True, text=True, env=dict(os.environ, TZ='Asia/Jakarta')); os.unlink(p)
    out = (r.stdout or '').strip().split('\n')
    if r.returncode != 0 or not out[-1].startswith('{'): return None, (r.stderr or r.stdout)[-900:]
    return json.loads(out[-1]), ''


def semua(ganti=None, bagian=('statis', 'jsc')):
    t = baca(ganti); out = []
    if 'statis' in bagian: out += statis(t)
    if 'jsc' in bagian:
        h, e = jalan(bundel_baru.polos(t[LL]) + '\n' + SKENARIO)
        if h is None: out.append(('jsc · JATUH: ' + e, False, ''))
        else: out += [('jsc · ' + x, False, '') for x in h['gagal']] + [('__jsc', not h['gagal'], h['lulus'])]
    return out


KONTROL = [
    ('warna tidak dicampur di antara titik palet (loncat)', {LL: [("const t = mb > ma ? jepit((m - ma) / (mb - ma), 0, 1) : 0;", "const t = 0;")]}, ('jsc',)),
    ('cuaca basi tidak diabaikan', {LL: [("export const lgCuacaSegar = (cuaca, kiniMs) => !!cuaca && Number(kiniMs) - cuaca.pada >= 0 && Number(kiniMs) - cuaca.pada < 3 * 3600000;", "export const lgCuacaSegar = (cuaca) => !!cuaca;")]}, ('jsc',)),
    ('cuaca diambil tanpa melihat umur', {LL: [("const umur = Number(kiniMs) - cuaca.pada; return !(umur >= 0 && umur < LG_UMUR_MS);", "return false;")]}, ('jsc',)),
    ('tampilan asli petang tidak lagi tembus (G4 terhapus)', {LL: [("const ASLI = { gelap: { l1: [17, 21, 22, 0], l2: [11, 13, 15, 0], l3: [9, 11, 13, 0],", "const ASLI = { gelap: { l1: [17, 21, 22, 1], l2: [11, 13, 15, 1], l3: [9, 11, 13, 1],")]}, ('jsc',)),
    ('cahaya cakrawala asli diubah', {LL: [("cahaya: [214, 146, 64, 0.46] }", "cahaya: [214, 146, 64, 0.3] }")]}, ('jsc',)),
    ('hujan tidak menyepikan satwa', {LL: [("const kering = !C.hujan && !C.petir;", "const kering = true;")]}, ('jsc',)),
    ('kelelawar siang hari', {LL: [("kelelawar: basahRingan && (R(B - 5, 1440) || R(0, T - 20)),", "kelelawar: basahRingan,")]}, ('jsc',)),
    ('sambaran tanpa cabang', {LL: [("const cabang = []; const n = 1 + Math.floor(r() * 3);", "const cabang = []; const n = 0;")]}, ('jsc',)),
    ('sambaran keluar kotak', {LL: [("x = jepit(x + (r() - 0.5) * lebar, 4, 96);", "x = x + (r() - 0.5) * lebar * 9;")]}, ('jsc',)),
    ('langit badai tidak digelapkan', {LL: [("else if (C.petir) c = campur(c, [42, 48, 62, c[3]], terang ? 0.3 : 0.42);", "else if (C.petir) c = c;")]}, ('jsc',)),
    ('petir hilang dari kode 95', {LL: [("95: ['badai', 0.95, 3, 'Hujan petir']", "95: ['lebat', 0.95, 3, 'Hujan petir']")]}, ('jsc',)),
    ('mendung tidak mengelabukan langit', {LL: [("const redup = jepit((C.awan - 0.35) * 1.35, 0, 0.88);", "const redup = 0;")]}, ('jsc',)),
    ('lokasi tidak dibulatkan (koordinat rumah ikut terkirim)', {LL: [("return { nama: String(o.nama || '').replace(/[<>\"'`]/g, '').trim().slice(0, 80), lat: bulat(lat, 3), lon: bulat(lon, 3) };", "return { nama: String(o.nama || ''), lat, lon };")]}, ('jsc',)),
    ('terbit/terbenam dari cuaca diabaikan', {LL: [("const T = segar && cuaca.terbit !== null ? cuaca.terbit : LG_TERBIT;", "const T = LG_TERBIT;")]}, ('jsc',)),
    ('cari tempat tidak dibatasi Indonesia', {LL: [("&format=json&countryCode=ID'", "&format=json'")]}, ('jsc',)),
    ('kelas keadaan bertabrakan dengan lapisan petir lagi', {LJ: [("K.petir ? 'lg-ada-petir' : ''", "K.petir ? 'lg-petir' : ''")]}, ('statis',)),
    ('animasi tanpa henti menggerakkan selain transform/opacity', {LC: [("@keyframes lgKelip { from { opacity: 1; } to { opacity: 0.32; } }", "@keyframes lgKelip { from { opacity: 1; filter: blur(0); } to { opacity: 0.32; filter: blur(1px); } }")]}, ('statis',)),
    ('matahari dipindah dengan transisi letak', {LC: [("transition: opacity 2.4s ease; }\n.gerbang-masuk.lg-ada-surya .lg-surya { display: block; }", "transition: opacity 2.4s ease, left 60s linear, top 60s linear; }\n.gerbang-masuk.lg-ada-surya .lg-surya { display: block; }")]}, ('statis',)),
    ('kilat kembali memaksa tata letak gerbang', {LJ: [("      aturKilat();\n    }, 4500", "      void g.offsetWidth; aturKilat();\n    }, 4500")]}, ('statis',)),
    ('langit tetap berjalan saat gerbang pergi', {GJ: [("langit.nyala(ya);", "langit.nyala(true);")]}, ('statis',)),
    ('lokasi disalin walau setelan belum terbaca (cache kosong mencabut lokasi)', {AP: [("if (dokDiCache('aturanToko', 'perangkat')) langitSimpanLokasi", "langitSimpanLokasi")]}, ('statis',)),
    ('fetch cuaca membawa kuki', {LJ: [("credentials: 'omit', referrerPolicy: 'no-referrer'", "credentials: 'include'")]}, ('statis',)),
    ('kelas keadaan satwa bertabrakan dengan kelas satwanya', {LJ: [("K.satwa.kelelawar ? 'lg-ada-kelelawar' : ''", "K.satwa.kelelawar ? 'lg-kelelawar' : ''")]}, ('statis',)),
    ('satwa mengepak lewat animasi selain transform', {LC: [("@keyframes lgKepakKupu { from { transform: scaleX(1); } to { transform: scaleX(0.16); } }", "@keyframes lgKepakKupu { from { width: 20px; } to { width: 4px; } }")]}, ('statis',)),
    ('sambaran kembali di belakang kaca', {LJ: [("if (hidupAda) g.insertBefore(sambar, hidupAda); else g.appendChild(sambar);", "latar.appendChild(sambar);")]}, ('statis',)),
    ('lokasi memakai GPS perangkat', {LJ: [("const lokasi = () => {", "const gps = () => navigator.geolocation.getCurrentPosition(() => {});\n  const lokasi = () => {")]}, ('statis',)),
    ('CSP membuka host Open-Meteo lain', {IX: [("https://geocoding-api.open-meteo.com;", "https://geocoding-api.open-meteo.com https://archive-api.open-meteo.com;")]}, ('statis',)),
    ('atur Perangkat menyimpan lokasi mentah', {SL: [("o.cuaca = lgLokasiSah(isi.cuaca !== undefined ? isi.cuaca : A.cuaca);", "o.cuaca = isi.cuaca;")]}, ('statis',)),
    ('matahari jam 12 kembali ke tengah atas (di balik papan nama)', {LL: [("[jamKe(12, 0), 75, 14]", "[jamKe(12, 0), 50, 15]")]}, ('jsc',)),
    ('lintasan tegak lewat di balik kotak Masuk HP', {LL: [("[jamKe(12, 30), 82, 23]", "[jamKe(12, 30), 82, 45]")]}, ('jsc',)),
    ('siang tanpa terik (pancaran mati)', {LL: [("const terik = sOp > 0 ?", "const terik = 0 && sOp > 0 ?")]}, ('jsc',)),
    ('terik tetap menyala saat mendung', {LL: [("* jepit(1 - (C.awan - 0.15) * 1.6, 0, 1) * (C.kabut ? 0.3 : 1)", "* (C.kabut ? 0.3 : 1)")]}, ('jsc',)),
    ('langit siang kembali pucat (bukan tropis)', {LL: [("siang:  { l1: [14, 96, 204, 1]", "siang:  { l1: [52, 118, 204, 1]")]}, ('jsc',)),
    ('cakram & pancaran kembali di belakang kaca buram', {LJ: [("hidup.insertBefore(suryaDepan(), hidup.firstChild);", "latar.appendChild(suryaDepan());")]}, ('statis',)),
    ('gerbang tegak memakai lintasan datar (syarat dua kolom beda dari gerbang.css)', {LC: [("@media (min-width: 1100px), (min-width: 900px) and (orientation: landscape) {\n  .gerbang-masuk { --lg-sx", "@media (min-width: 700px) {\n  .gerbang-masuk { --lg-sx")]}, ('statis',)),
]

if __name__ == '__main__':
    if '--kontrol' in sys.argv:
        kode = 0
        for nama, ganti, bagian in KONTROL:
            try: h = semua(ganti, bagian)
            except AssertionError as e: print('KONTROL BASI  ' + nama + ' · ' + str(e)[:160]); kode = 3; continue
            g = [x for x in h if not x[1]]
            print(('BERBUNYI ' if g else 'DIAM!!   ') + nama + ' → ' + (g[0][0][:150] if g else '-'))
            if not g: kode = 3
        sys.exit(kode)
    h = semua(); g = [x for x in h if not x[1]]
    n = sum(1 for x in h if x[1] and x[0] != '__jsc') + next((x[2] for x in h if x[0] == '__jsc'), 0)
    for x in g: print('   ✗ ' + x[0] + (' → ' + json.dumps(x[2], ensure_ascii=False)[:400] if x[2] not in ('', None) else ''))
    print('LANGIT GERBANG: %d lulus · %d gagal' % (n, len(g)))
    sys.exit(1 if g else 0)
